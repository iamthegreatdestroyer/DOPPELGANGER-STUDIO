"""
Claude AI Client - Primary LLM for creative intelligence.

Provides Claude Sonnet 4.5 integration with intelligent prompt optimization,
response caching, and error handling.

Copyright (c) 2025. All Rights Reserved. Patent Pending.
"""

from typing import Dict, List, Optional, Any
import asyncio
import logging
from anthropic import AsyncAnthropic
from dataclasses import dataclass
import hashlib
import json

from src.services.caching import (
    get_cache_manager,
    generate_ai_cache_key,
    CacheTTL,
)

logger = logging.getLogger(__name__)


@dataclass
class AIResponse:
    """Container for AI response data."""
    content: str
    model: str
    tokens_used: int
    finish_reason: str
    cached: bool = False
    raw_response: Optional[Dict] = None


class ClaudeClient:
    """
    Client for Claude Sonnet 4.5 API with advanced features.
    
    Features:
    - Prompt optimization and templating
    - Response caching with Redis
    - Token usage tracking
    - Automatic retry with exponential backoff
    - Context window management
    """
    
    MODEL = "claude-sonnet-4-20250514"  # Claude Sonnet 4.5
    MAX_TOKENS = 8192
    DEFAULT_TEMPERATURE = 0.7
    
    def __init__(
        self,
        api_key: str,
        enable_caching: bool = True,
        cache_ttl: int = CacheTTL.LONG.value
    ):
        """
        Initialize Claude client.
        
        Args:
            api_key: Anthropic API key
            enable_caching: Whether to enable response caching
            cache_ttl: Cache time-to-live in seconds (default 7 days)
        """
        self.client = AsyncAnthropic(api_key=api_key)
        self.enable_caching = enable_caching
        self.cache_ttl = cache_ttl
        
        # Get cache manager
        self.cache_manager = get_cache_manager() if enable_caching else None
        
        # Usage tracking
        self.total_tokens_used = 0
        self.total_requests = 0
        self.cache_hits = 0
    
    async def generate(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        max_tokens: int = MAX_TOKENS,
        temperature: float = DEFAULT_TEMPERATURE,
        json_mode: bool = False,
        use_cache: bool = True
    ) -> AIResponse:
        """
        Generate text using Claude.
        
        Args:
            prompt: User prompt
            system_prompt: Optional system prompt for context
            max_tokens: Maximum tokens to generate
            temperature: Sampling temperature (0-1)
            json_mode: Request JSON-formatted response
            use_cache: Whether to use cached responses
            
        Returns:
            AIResponse with generated content
            
        Example:
            >>> client = ClaudeClient(api_key="key")
            >>> response = await client.generate(
            ...     prompt="Describe Lucy Ricardo's personality",
            ...     system_prompt="You are a TV show analyst"
            ... )
            >>> print(response.content)
        """
        logger.debug(f"Generating with Claude (prompt length: {len(prompt)})")
        
        # Check cache
        if use_cache:
            cached = await self._get_from_cache(
                prompt, system_prompt, max_tokens, temperature
            )
            if cached:
                logger.debug("Cache hit!")
                self.cache_hits += 1
                return cached
        
        # Add JSON instruction if needed
        if json_mode:
            prompt = f"{prompt}\n\nRespond ONLY with valid JSON. No other text."
        
        # Build messages
        messages = [{"role": "user", "content": prompt}]
        
        # Make API call with retry
        try:
            response = await self._make_request_with_retry(
                messages=messages,
                system=system_prompt,
                max_tokens=max_tokens,
                temperature=temperature
            )
            
            # Extract response
            content = response.content[0].text
            tokens_used = response.usage.input_tokens + response.usage.output_tokens
            
            # Update tracking
            self.total_tokens_used += tokens_used
            self.total_requests += 1
            
            # Build response object
            ai_response = AIResponse(
                content=content,
                model=response.model,
                tokens_used=tokens_used,
                finish_reason=response.stop_reason,
                cached=False,
                raw_response=response.model_dump() if hasattr(response, 'model_dump') else None
            )
            
            # Cache response
            if use_cache:
                await self._save_to_cache(
                    prompt, system_prompt, max_tokens, temperature, ai_response
                )
            
            logger.info(
                f"Generated {tokens_used} tokens "
                f"(total: {self.total_tokens_used:,})"
            )
            
            return ai_response
            
        except Exception as e:
            logger.error(f"Claude generation failed: {e}")
            raise
    
    async def generate_json(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        max_tokens: int = MAX_TOKENS,
        temperature: float = DEFAULT_TEMPERATURE
    ) -> Dict:
        """
        Generate JSON response using Claude.
        
        Args:
            prompt: User prompt
            system_prompt: Optional system prompt
            max_tokens: Maximum tokens to generate
            temperature: Sampling temperature
            
        Returns:
            Parsed JSON dictionary
            
        Example:
            >>> data = await client.generate_json(
            ...     prompt="Extract character traits from: Lucy is ambitious..."
            ... )
            >>> print(data['traits'])
        """
        response = await self.generate(
            prompt=prompt,
            system_prompt=system_prompt,
            max_tokens=max_tokens,
            temperature=temperature,
            json_mode=True
        )
        
        try:
            # Parse JSON
            return json.loads(response.content)
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse JSON response: {e}")
            logger.debug(f"Raw response: {response.content}")
            raise ValueError(f"Invalid JSON response from Claude: {e}")
    
    async def _make_request_with_retry(
        self,
        messages: List[Dict],
        system: Optional[str],
        max_tokens: int,
        temperature: float,
        max_retries: int = 3
    ) -> Any:
        """Make API request with exponential backoff retry."""
        for attempt in range(max_retries):
            try:
                kwargs = {
                    'model': self.MODEL,
                    'max_tokens': max_tokens,
                    'temperature': temperature,
                    'messages': messages
                }
                
                if system:
                    kwargs['system'] = system
                
                response = await self.client.messages.create(**kwargs)
                return response
                
            except Exception as e:
                if attempt == max_retries - 1:
                    raise
                
                wait_time = 2 ** attempt  # Exponential backoff
                logger.warning(
                    f"Request failed (attempt {attempt + 1}/{max_retries}): {e}. "
                    f"Retrying in {wait_time}s..."
                )
                await asyncio.sleep(wait_time)
    
    def _cache_key(
        self,
        prompt: str,
        system_prompt: Optional[str],
        max_tokens: int,
        temperature: float
    ) -> str:
        """Generate cache key from parameters using our cache key generator."""
        return generate_ai_cache_key(
            prompt=prompt,
            model=self.MODEL,
            temperature=temperature,
            max_tokens=max_tokens,
            json_mode=False  # Add json_mode to kwargs if needed
        )
    
    async def _get_from_cache(
        self,
        prompt: str,
        system_prompt: Optional[str],
        max_tokens: int,
        temperature: float
    ) -> Optional[AIResponse]:
        """Retrieve response from cache if available."""
        if not self.cache_manager:
            return None
        
        try:
            key = self._cache_key(prompt, system_prompt, max_tokens, temperature)
            
            # Run sync cache get in executor to avoid blocking
            cached_data = await asyncio.get_event_loop().run_in_executor(
                None, self.cache_manager.get, key
            )
            
            if cached_data:
                # Cache manager already deserializes
                return AIResponse(
                    content=cached_data['content'],
                    model=cached_data['model'],
                    tokens_used=cached_data['tokens_used'],
                    finish_reason=cached_data['finish_reason'],
                    cached=True
                )
        except Exception as e:
            logger.warning(f"Cache retrieval failed: {e}")
        
        return None
    
    async def _save_to_cache(
        self,
        prompt: str,
        system_prompt: Optional[str],
        max_tokens: int,
        temperature: float,
        response: AIResponse
    ):
        """Save response to cache."""
        if not self.cache_manager:
            return
        
        try:
            key = self._cache_key(prompt, system_prompt, max_tokens, temperature)
            cache_data = {
                'content': response.content,
                'model': response.model,
                'tokens_used': response.tokens_used,
                'finish_reason': response.finish_reason
            }
            
            # Run sync cache set in executor
            await asyncio.get_event_loop().run_in_executor(
                None,
                lambda: self.cache_manager.set(key, cache_data, self.cache_ttl)
            )
        except Exception as e:
            logger.warning(f"Cache save failed: {e}")
    
    def get_usage_stats(self) -> Dict[str, Any]:
        """Get usage statistics."""
        return {
            'total_requests': self.total_requests,
            'total_tokens': self.total_tokens_used,
            'cache_hits': self.cache_hits,
            'cache_hit_rate': (
                self.cache_hits / self.total_requests
                if self.total_requests > 0
                else 0.0
            )
        }


# Example usage
async def main():
    """Example usage of Claude client."""
    import os
    
    api_key = os.getenv('ANTHROPIC_API_KEY', 'your_key_here')
    
    client = ClaudeClient(api_key=api_key)
    
    # Simple generation
    response = await client.generate(
        prompt="Describe Lucy Ricardo's personality in 3 sentences.",
        system_prompt="You are a TV show character analyst."
    )
    
    print(f"Response: {response.content}")
    print(f"Tokens: {response.tokens_used}")
    print(f"Model: {response.model}")
    
    # JSON generation
    json_response = await client.generate_json(
        prompt="""
        Analyze Lucy Ricardo and respond with JSON:
        {
          "name": "character name",
          "traits": ["trait1", "trait2", "trait3"],
          "motivations": ["motivation1", "motivation2"]
        }
        """
    )
    
    print(f"\nJSON Response: {json_response}")
    
    # Usage stats
    stats = client.get_usage_stats()
    print(f"\nUsage Stats: {stats}")


if __name__ == "__main__":
    asyncio.run(main())

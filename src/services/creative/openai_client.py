"""
OpenAI Client - GPT-4 fallback for creative intelligence.

Provides GPT-4 integration as fallback when Claude is unavailable.

Copyright (c) 2025. All Rights Reserved. Patent Pending.
"""

from typing import Dict, List, Optional, Any
import asyncio
import logging
from openai import AsyncOpenAI
import hashlib
import json

from .claude_client import AIResponse

logger = logging.getLogger(__name__)


class OpenAIClient:
    """
    Client for GPT-4 API with caching and retry logic.
    
    Serves as fallback when Claude is unavailable or rate-limited.
    """
    
    MODEL = "gpt-4-turbo-preview"
    MAX_TOKENS = 4096
    DEFAULT_TEMPERATURE = 0.7
    
    def __init__(
        self,
        api_key: str,
        cache_client: Optional[Any] = None,
        cache_ttl: int = 604800
    ):
        """
        Initialize OpenAI client.
        
        Args:
            api_key: OpenAI API key
            cache_client: Optional Redis client
            cache_ttl: Cache TTL in seconds
        """
        self.client = AsyncOpenAI(api_key=api_key)
        self.cache_client = cache_client
        self.cache_ttl = cache_ttl
        
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
        """Generate text using GPT-4."""
        logger.debug(f"Generating with GPT-4 (prompt length: {len(prompt)})")
        
        # Check cache
        if use_cache:
            cached = await self._get_from_cache(
                prompt, system_prompt, max_tokens, temperature
            )
            if cached:
                self.cache_hits += 1
                return cached
        
        # Build messages
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})
        
        # Make request
        try:
            kwargs = {
                'model': self.MODEL,
                'messages': messages,
                'max_tokens': max_tokens,
                'temperature': temperature
            }
            
            if json_mode:
                kwargs['response_format'] = {"type": "json_object"}
                prompt += "\n\nRespond with valid JSON."
            
            response = await self.client.chat.completions.create(**kwargs)
            
            content = response.choices[0].message.content
            tokens_used = response.usage.total_tokens
            
            self.total_tokens_used += tokens_used
            self.total_requests += 1
            
            ai_response = AIResponse(
                content=content,
                model=response.model,
                tokens_used=tokens_used,
                finish_reason=response.choices[0].finish_reason,
                cached=False
            )
            
            if use_cache:
                await self._save_to_cache(
                    prompt, system_prompt, max_tokens, temperature, ai_response
                )
            
            return ai_response
            
        except Exception as e:
            logger.error(f"GPT-4 generation failed: {e}")
            raise
    
    async def generate_json(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        max_tokens: int = MAX_TOKENS,
        temperature: float = DEFAULT_TEMPERATURE
    ) -> Dict:
        """Generate JSON response using GPT-4."""
        response = await self.generate(
            prompt=prompt,
            system_prompt=system_prompt,
            max_tokens=max_tokens,
            temperature=temperature,
            json_mode=True
        )
        
        try:
            return json.loads(response.content)
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse JSON: {e}")
            raise ValueError(f"Invalid JSON from GPT-4: {e}")
    
    def _cache_key(self, prompt, system_prompt, max_tokens, temperature) -> str:
        """Generate cache key."""
        key_data = f"{prompt}:{system_prompt}:{max_tokens}:{temperature}"
        return f"gpt4:{hashlib.sha256(key_data.encode()).hexdigest()}"
    
    async def _get_from_cache(
        self, prompt, system_prompt, max_tokens, temperature
    ) -> Optional[AIResponse]:
        """Get from cache."""
        if not self.cache_client:
            return None
        
        try:
            key = self._cache_key(prompt, system_prompt, max_tokens, temperature)
            cached = await self.cache_client.get(key)
            if cached:
                data = json.loads(cached)
                return AIResponse(**data, cached=True)
        except Exception as e:
            logger.warning(f"Cache get failed: {e}")
        
        return None
    
    async def _save_to_cache(
        self, prompt, system_prompt, max_tokens, temperature, response
    ):
        """Save to cache."""
        if not self.cache_client:
            return
        
        try:
            key = self._cache_key(prompt, system_prompt, max_tokens, temperature)
            cache_data = {
                'content': response.content,
                'model': response.model,
                'tokens_used': response.tokens_used,
                'finish_reason': response.finish_reason
            }
            await self.cache_client.setex(
                key, self.cache_ttl, json.dumps(cache_data)
            )
        except Exception as e:
            logger.warning(f"Cache save failed: {e}")
    
    def get_usage_stats(self) -> Dict:
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

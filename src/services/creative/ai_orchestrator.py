"""
AI Orchestrator - Manages multiple AI providers with intelligent fallback.

Coordinates Claude and GPT-4, automatically falling back on failures.

Copyright (c) 2025. All Rights Reserved. Patent Pending.
"""

from typing import Optional, Dict
import logging

from .claude_client import ClaudeClient, AIResponse
from .openai_client import OpenAIClient

logger = logging.getLogger(__name__)


class AIOrchestrator:
    """
    Orchestrates multiple AI providers with automatic fallback.
    
    Features:
    - Primary/fallback provider pattern
    - Automatic retry and fallback
    - Unified interface
    - Usage tracking across providers
    """
    
    def __init__(
        self,
        claude_api_key: Optional[str] = None,
        openai_api_key: Optional[str] = None,
        cache_client: Optional[any] = None
    ):
        """
        Initialize AI orchestrator.
        
        Args:
            claude_api_key: Anthropic API key (primary)
            openai_api_key: OpenAI API key (fallback)
            cache_client: Optional Redis client
        """
        self.claude_client = (
            ClaudeClient(claude_api_key, cache_client)
            if claude_api_key
            else None
        )
        self.openai_client = (
            OpenAIClient(openai_api_key, cache_client)
            if openai_api_key
            else None
        )
        
        if not self.claude_client and not self.openai_client:
            raise ValueError("At least one AI provider key required")
    
    async def generate(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        max_tokens: int = 4096,
        temperature: float = 0.7,
        json_mode: bool = False
    ) -> AIResponse:
        """
        Generate text with automatic fallback.
        
        Args:
            prompt: User prompt
            system_prompt: System context
            max_tokens: Max tokens to generate
            temperature: Sampling temperature
            json_mode: Request JSON response
            
        Returns:
            AIResponse from available provider
        """
        # Try Claude first (preferred)
        if self.claude_client:
            try:
                return await self.claude_client.generate(
                    prompt=prompt,
                    system_prompt=system_prompt,
                    max_tokens=max_tokens,
                    temperature=temperature,
                    json_mode=json_mode
                )
            except Exception as e:
                logger.warning(f"Claude failed: {e}. Trying fallback...")
        
        # Fallback to GPT-4
        if self.openai_client:
            try:
                return await self.openai_client.generate(
                    prompt=prompt,
                    system_prompt=system_prompt,
                    max_tokens=max_tokens,
                    temperature=temperature,
                    json_mode=json_mode
                )
            except Exception as e:
                logger.error(f"GPT-4 also failed: {e}")
                raise
        
        raise RuntimeError("All AI providers failed")
    
    async def generate_json(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        max_tokens: int = 4096,
        temperature: float = 0.7
    ) -> Dict:
        """Generate JSON with automatic fallback."""
        # Try Claude
        if self.claude_client:
            try:
                return await self.claude_client.generate_json(
                    prompt, system_prompt, max_tokens, temperature
                )
            except Exception as e:
                logger.warning(f"Claude JSON failed: {e}")
        
        # Fallback to GPT-4
        if self.openai_client:
            try:
                return await self.openai_client.generate_json(
                    prompt, system_prompt, max_tokens, temperature
                )
            except Exception as e:
                logger.error(f"GPT-4 JSON failed: {e}")
                raise
        
        raise RuntimeError("JSON generation failed on all providers")
    
    def get_usage_stats(self) -> Dict:
        """Get combined usage statistics."""
        stats = {'claude': {}, 'gpt4': {}}
        
        if self.claude_client:
            stats['claude'] = self.claude_client.get_usage_stats()
        
        if self.openai_client:
            stats['gpt4'] = self.openai_client.get_usage_stats()
        
        # Calculate totals
        stats['total'] = {
            'requests': (
                stats['claude'].get('total_requests', 0)
                + stats['gpt4'].get('total_requests', 0)
            ),
            'tokens': (
                stats['claude'].get('total_tokens', 0)
                + stats['gpt4'].get('total_tokens', 0)
            )
        }
        
        return stats

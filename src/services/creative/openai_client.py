"""
Local Fallback Client — local-first replacement for the former GPT-4 fallback.

POLICY REPLACEMENT (2026-07-02): this module previously wrapped the OpenAI API
(AsyncOpenAI / gpt-4-turbo-preview) as the fallback when Claude was
unavailable. Per the ecosystem's No-OpenAI policy (values-driven: maximum
privacy, security, and non-codependency on external companies), the fallback
is now the LOCAL Ryzanstein gateway (:8000), which fronts Ollama and adds
Token-Recycler semantic caching. No prompt or script data leaves the machine
on the fallback path anymore.

The class keeps the name `OpenAIClient` as a deprecated import-compat alias —
six sibling modules import it by that name; the canonical name going forward
is `LocalFallbackClient`.

Default model: qwythos-9b (the custom Claude-Mythos creative-writing merge
served by the local Ollama), override via DOPPELGANGER_LOCAL_MODEL.
Gateway URL: RYZANSTEIN_URL (default http://localhost:8000).

Copyright (c) 2025-2026. All Rights Reserved. Patent Pending.
"""

from typing import Dict, List, Optional, Any
import asyncio
import hashlib
import json
import logging
import os
import re

from sigma_core import RyzansteinClient

try:
    from .claude_client import AIResponse
except ImportError:
    # anthropic SDK not installed — define the identical response container
    # locally so the fallback client works standalone (that is its whole job).
    from dataclasses import dataclass as _dataclass

    @_dataclass
    class AIResponse:  # type: ignore[no-redef]
        """Container for AI response data (local mirror of claude_client's)."""
        content: str
        model: str
        tokens_used: int
        finish_reason: str
        cached: bool = False
        raw_response: Optional[Dict] = None

logger = logging.getLogger(__name__)


class LocalFallbackClient:
    """
    Fallback AI client backed by the local Ryzanstein gateway (Ollama).

    Interface-compatible with the former GPT-4 client: generate(),
    generate_json(), get_usage_stats(), same constructor shape. The
    `api_key` argument is accepted and ignored (no key is needed for
    local inference) so existing call sites keep working unchanged.
    """

    MODEL = os.getenv("DOPPELGANGER_LOCAL_MODEL", "qwythos-9b")
    BASE_URL = os.getenv("RYZANSTEIN_URL", "http://localhost:8000")
    MAX_TOKENS = 4096
    DEFAULT_TEMPERATURE = 0.7

    def __init__(
        self,
        api_key: Optional[str] = None,
        cache_client: Optional[Any] = None,
        cache_ttl: int = 604800,
    ):
        if api_key:
            logger.info(
                "LocalFallbackClient: api_key argument is ignored — fallback "
                "inference is local (Ryzanstein gateway), no external API key needed."
            )
        self.cache_client = cache_client
        self.cache_ttl = cache_ttl
        self.total_tokens_used = 0
        self.total_requests = 0
        self.cache_hits = 0
        # The one shared gateway client (sigma_core) — owns base_url/timeout config.
        self._client = RyzansteinClient(base_url=self.BASE_URL, chat_model=self.MODEL)

    async def generate(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        max_tokens: int = MAX_TOKENS,
        temperature: float = DEFAULT_TEMPERATURE,
        json_mode: bool = False,
        use_cache: bool = True,
    ) -> AIResponse:
        """Generate text using the local Ryzanstein gateway (Ollama-backed)."""
        logger.debug(
            f"Generating with local fallback ({self.MODEL}, prompt length: {len(prompt)})"
        )

        if use_cache:
            cached = await self._get_from_cache(
                prompt, system_prompt, max_tokens, temperature
            )
            if cached:
                self.cache_hits += 1
                return cached

        user_prompt = prompt
        if json_mode:
            user_prompt += "\n\nRespond with valid JSON only — no prose, no code fences."

        try:
            # Delegate the /api/chat call, payload shape, and content parse to the
            # one shared Ryzanstein gateway client (sigma_core). base_url + model
            # default remain overridable via RYZANSTEIN_URL / DOPPELGANGER_LOCAL_MODEL.
            content = await self._client.achat(
                user_prompt,
                system=system_prompt,
                model=self.MODEL,
                temperature=temperature,
                max_tokens=max_tokens,
            )

            # achat returns content only; the gateway's raw token counts are not
            # surfaced, so estimate tokens (~4 chars/token) to keep usage stats live.
            tokens_used = (len(prompt) + len(system_prompt or "") + len(content)) // 4
            self.total_tokens_used += tokens_used
            self.total_requests += 1

            ai_response = AIResponse(
                content=content,
                model=self.MODEL,
                tokens_used=tokens_used,
                finish_reason="stop",
                cached=False,
            )

            if use_cache:
                await self._save_to_cache(
                    prompt, system_prompt, max_tokens, temperature, ai_response
                )
            return ai_response

        except Exception as e:
            logger.error(f"Local fallback generation failed: {e}")
            raise

    async def generate_json(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        max_tokens: int = MAX_TOKENS,
        temperature: float = DEFAULT_TEMPERATURE,
    ) -> Dict:
        """Generate and parse a JSON response."""
        response = await self.generate(
            prompt=prompt,
            system_prompt=system_prompt,
            max_tokens=max_tokens,
            temperature=temperature,
            json_mode=True,
        )
        text = response.content.strip()
        try:
            return json.loads(text)
        except json.JSONDecodeError:
            # Local models sometimes wrap JSON in code fences or prose —
            # extract the outermost object before giving up.
            match = re.search(r"\{.*\}", text, re.DOTALL)
            if match:
                return json.loads(match.group(0))
            raise

    def _cache_key(self, prompt, system_prompt, max_tokens, temperature) -> str:
        raw = f"local:{self.MODEL}:{prompt}:{system_prompt}:{max_tokens}:{temperature}"
        return "dopp:ai:" + hashlib.sha256(raw.encode()).hexdigest()

    async def _get_from_cache(
        self, prompt, system_prompt, max_tokens, temperature
    ) -> Optional[AIResponse]:
        if not self.cache_client:
            return None
        try:
            key = self._cache_key(prompt, system_prompt, max_tokens, temperature)
            raw = self.cache_client.get(key)
            if asyncio.iscoroutine(raw):
                raw = await raw
            if not raw:
                return None
            data = json.loads(raw)
            return AIResponse(
                content=data["content"],
                model=data["model"],
                tokens_used=data["tokens_used"],
                finish_reason=data["finish_reason"],
                cached=True,
            )
        except Exception as e:
            logger.debug(f"Cache read failed (ignored): {e}")
            return None

    async def _save_to_cache(
        self, prompt, system_prompt, max_tokens, temperature, response: AIResponse
    ) -> None:
        if not self.cache_client:
            return
        try:
            key = self._cache_key(prompt, system_prompt, max_tokens, temperature)
            raw = json.dumps(
                {
                    "content": response.content,
                    "model": response.model,
                    "tokens_used": response.tokens_used,
                    "finish_reason": response.finish_reason,
                }
            )
            result = self.cache_client.setex(key, self.cache_ttl, raw)
            if asyncio.iscoroutine(result):
                await result
        except Exception as e:
            logger.debug(f"Cache write failed (ignored): {e}")

    def get_usage_stats(self) -> Dict:
        return {
            "provider": "local-ryzanstein",
            "model": self.MODEL,
            "total_requests": self.total_requests,
            "total_tokens_used": self.total_tokens_used,
            "cache_hits": self.cache_hits,
        }


# Deprecated import-compat alias — six sibling modules import this name.
# New code should import LocalFallbackClient.
OpenAIClient = LocalFallbackClient

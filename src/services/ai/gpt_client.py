"""
DEPRECATED shim (2026-07-02) — this module was a second, orphaned copy of the
GPT-4 fallback client (nothing in src/ imports it; narrative_analyzer's
`GPTClient` alias comes from services/creative/openai_client.py instead).

Per the ecosystem's No-OpenAI policy, the external GPT-4 fallback was replaced
by the local Ryzanstein gateway. This shim re-exports the local client so any
stray/external import of this path keeps working, without the `openai` SDK.
"""

from src.services.creative.openai_client import (  # noqa: F401
    LocalFallbackClient,
    LocalFallbackClient as GPTClient,
    LocalFallbackClient as OpenAIClient,
)

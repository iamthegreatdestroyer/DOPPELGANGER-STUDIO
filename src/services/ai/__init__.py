"""
AI Services Package - Character and narrative analysis engines.

Copyright (c) 2025 Stephen Bilodeau. All Rights Reserved.

NOTE (2026-07-02): this file was corrupted (literal \n escapes instead of real
newlines — a SyntaxError since whenever it was written). Rewritten. The Claude
import is guarded so the package still imports on hosts without the anthropic
SDK; the local fallback client (GPTClient shim -> LocalFallbackClient) has no
cloud dependency.
"""

from src.services.ai.base_client import BaseAIClient, AIResponse, AIUsageStats, AIClientError
from src.services.ai.gpt_client import GPTClient

try:
    from src.services.ai.claude_client import ClaudeClient
except ImportError:  # anthropic SDK not installed — local-only operation
    ClaudeClient = None

__all__ = [
    'BaseAIClient',
    'AIResponse',
    'AIUsageStats',
    'AIClientError',
    'ClaudeClient',
    'GPTClient',
]

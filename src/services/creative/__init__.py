"""
AI Creative Service - Core intelligence for show transformation.

This service provides AI-powered creative capabilities including character
analysis, narrative transformation, and humor pattern recognition.

Copyright (c) 2025. All Rights Reserved. Patent Pending.
"""

# Claude import guarded (2026-07-02): the anthropic SDK is optional — without
# it the package still imports so the LOCAL fallback client remains usable
# (local-first: cloud SDKs must not be required for local-only operation).
try:
    from .claude_client import ClaudeClient
except ImportError:
    ClaudeClient = None

from .openai_client import LocalFallbackClient, OpenAIClient

try:
    from .ai_orchestrator import AIOrchestrator
except ImportError:  # depends on claude_client at module level
    AIOrchestrator = None

__all__ = [
    'ClaudeClient',
    'LocalFallbackClient',
    'OpenAIClient',
    'AIOrchestrator',
]

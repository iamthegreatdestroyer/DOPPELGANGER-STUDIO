"""
Copyright (c) 2025 DOPPELGANGER STUDIO. All Rights Reserved.

API Management services for DOPPELGANGER STUDIO.

Includes:
- Rate limiting for multiple API providers
- Request queuing and retry logic
- Token bucket algorithm implementation
- Backoff strategies
"""

__version__ = "1.0.0"
__author__ = "DOPPELGANGER STUDIO Team"

from .rate_limiter import (
    APIProvider,
    RateLimitConfig,
    TokenBucket,
    APICallResult,
    RateLimiter,
    APIRateLimitManager,
    get_rate_limit_manager,
)

__all__ = [
    "APIProvider",
    "RateLimitConfig",
    "TokenBucket",
    "APICallResult",
    "RateLimiter",
    "APIRateLimitManager",
    "get_rate_limit_manager",
]

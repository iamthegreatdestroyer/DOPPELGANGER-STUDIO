"""
Copyright (c) 2025 DOPPELGANGER STUDIO. All Rights Reserved.

Caching package initialization.
"""

from src.services.caching.cache_config import (
    CacheConfig,
    CacheStrategy,
    CacheTTL,
    default_cache_config,
    generate_cache_key,
    generate_ai_cache_key,
    generate_voice_profile_cache_key,
    generate_dialogue_cache_key,
    generate_joke_cache_key,
)
from src.services.caching.cache_manager import (
    RedisCacheManager,
    MemoryCache,
    CacheStats,
    get_cache_manager,
)

__all__ = [
    "CacheConfig",
    "CacheStrategy",
    "CacheTTL",
    "default_cache_config",
    "generate_cache_key",
    "generate_ai_cache_key",
    "generate_voice_profile_cache_key",
    "generate_dialogue_cache_key",
    "generate_joke_cache_key",
    "RedisCacheManager",
    "MemoryCache",
    "CacheStats",
    "get_cache_manager",
]

"""
Copyright (c) 2025 DOPPELGANGER STUDIO. All Rights Reserved.

Cache configuration and utilities for performance optimization.

This module defines cache policies, TTL strategies, and key generation
utilities for the distributed caching system.
"""

from dataclasses import dataclass, field
from typing import Dict, Optional, Any
from enum import Enum
import hashlib
import json


class CacheStrategy(Enum):
    """Cache storage strategy."""
    REDIS = "redis"
    MEMORY = "memory"
    HYBRID = "hybrid"  # Redis primary, memory fallback


class CacheTTL(Enum):
    """Predefined TTL values in seconds."""
    SHORT = 3600  # 1 hour
    MEDIUM = 86400  # 1 day
    LONG = 604800  # 7 days
    VERY_LONG = 2592000  # 30 days


@dataclass
class CacheConfig:
    """
    Configuration for cache management.
    
    Defines connection settings, TTL policies, and behavior flags.
    """
    # Redis connection
    redis_host: str = "localhost"
    redis_port: int = 6379
    redis_db: int = 0
    redis_password: Optional[str] = None
    redis_ssl: bool = False
    
    # Connection pool settings
    max_connections: int = 50
    socket_timeout: int = 5
    socket_connect_timeout: int = 5
    connection_pool_kwargs: Dict[str, Any] = field(default_factory=dict)
    
    # Cache behavior
    default_ttl: int = CacheTTL.LONG.value
    strategy: CacheStrategy = CacheStrategy.HYBRID
    enable_compression: bool = True
    compression_threshold: int = 1024  # Compress if > 1KB
    
    # Performance settings
    max_memory_cache_size: int = 1000  # Max items in memory cache
    enable_metrics: bool = True
    
    # Feature flags
    cache_ai_responses: bool = True
    cache_voice_profiles: bool = True
    cache_dialogue_patterns: bool = True
    cache_joke_structures: bool = True
    
    # TTL policies by cache type
    ttl_policies: Dict[str, int] = field(default_factory=lambda: {
        "ai_response": CacheTTL.LONG.value,
        "voice_profile": CacheTTL.VERY_LONG.value,
        "dialogue_pattern": CacheTTL.LONG.value,
        "joke_structure": CacheTTL.LONG.value,
        "validation_result": CacheTTL.MEDIUM.value,
        "episode_outline": CacheTTL.MEDIUM.value,
    })
    
    def get_ttl(self, cache_type: str) -> int:
        """Get TTL for specific cache type."""
        return self.ttl_policies.get(cache_type, self.default_ttl)


def generate_cache_key(
    prefix: str,
    *args,
    **kwargs
) -> str:
    """
    Generate consistent cache key from prefix and parameters.
    
    Creates deterministic keys by hashing JSON-serialized arguments.
    
    Args:
        prefix: Cache key prefix (e.g., 'ai_response', 'voice_profile')
        *args: Positional arguments to include in key
        **kwargs: Keyword arguments to include in key
    
    Returns:
        Cache key in format: prefix:hash
    
    Example:
        >>> key = generate_cache_key(
        ...     "ai_response",
        ...     prompt="Generate dialogue",
        ...     model="claude-sonnet-4",
        ...     temperature=0.7
        ... )
        >>> print(key)
        'ai_response:a3f5e8b2c1d4...'
    """
    # Combine args and kwargs into single dict
    data = {
        "args": args,
        "kwargs": sorted(kwargs.items())  # Sort for consistency
    }
    
    # Create JSON string (sorted keys for determinism)
    json_str = json.dumps(data, sort_keys=True, default=str)
    
    # Generate SHA256 hash
    hash_obj = hashlib.sha256(json_str.encode())
    key_hash = hash_obj.hexdigest()[:16]  # Use first 16 chars
    
    return f"{prefix}:{key_hash}"


def generate_ai_cache_key(
    prompt: str,
    model: str,
    temperature: float = 0.7,
    max_tokens: Optional[int] = None,
    json_mode: bool = False
) -> str:
    """
    Generate cache key for AI responses.
    
    Args:
        prompt: The prompt text
        model: Model identifier
        temperature: Sampling temperature
        max_tokens: Max tokens to generate
        json_mode: Whether JSON mode is enabled
    
    Returns:
        Cache key for AI response
    """
    return generate_cache_key(
        "ai_response",
        prompt=prompt,
        model=model,
        temperature=temperature,
        max_tokens=max_tokens,
        json_mode=json_mode
    )


def generate_voice_profile_cache_key(
    character_name: str,
    show_context: Optional[str] = None
) -> str:
    """
    Generate cache key for character voice profiles.
    
    Args:
        character_name: Name of the character
        show_context: Optional show context
    
    Returns:
        Cache key for voice profile
    """
    return generate_cache_key(
        "voice_profile",
        character=character_name,
        show=show_context
    )


def generate_dialogue_cache_key(
    scene_context: str,
    characters: list,
    beat_type: str
) -> str:
    """
    Generate cache key for dialogue patterns.
    
    Args:
        scene_context: Scene description
        characters: List of character names
        beat_type: Type of dramatic beat
    
    Returns:
        Cache key for dialogue pattern
    """
    return generate_cache_key(
        "dialogue_pattern",
        context=scene_context,
        characters=sorted(characters),  # Sort for consistency
        beat=beat_type
    )


def generate_joke_cache_key(
    joke_type: str,
    setup: str,
    punchline: str
) -> str:
    """
    Generate cache key for joke structures.
    
    Args:
        joke_type: Type of joke (callback, wordplay, etc.)
        setup: Joke setup text
        punchline: Punchline text
    
    Returns:
        Cache key for joke structure
    """
    return generate_cache_key(
        "joke_structure",
        type=joke_type,
        setup=setup,
        punchline=punchline
    )


# Default cache configuration instance
default_cache_config = CacheConfig()

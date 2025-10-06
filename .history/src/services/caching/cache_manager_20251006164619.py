"""
Copyright (c) 2025 DOPPELGANGER STUDIO. All Rights Reserved.

Redis-based cache manager with fallback to memory cache.

Provides high-performance caching for AI responses, voice profiles,
dialogue patterns, and other frequently accessed data.
"""

import json
import pickle
import zlib
import logging
from typing import Any, Optional, Dict, List
from datetime import datetime, timedelta
from collections import OrderedDict
from dataclasses import dataclass, field

from src.services.caching.cache_config import CacheConfig, CacheStrategy

logger = logging.getLogger(__name__)


@dataclass
class CacheStats:
    """Cache performance statistics."""
    hits: int = 0
    misses: int = 0
    sets: int = 0
    deletes: int = 0
    errors: int = 0
    
    @property
    def hit_rate(self) -> float:
        """Calculate cache hit rate."""
        total = self.hits + self.misses
        return self.hits / total if total > 0 else 0.0
    
    @property
    def total_operations(self) -> int:
        """Total cache operations."""
        return self.hits + self.misses + self.sets + self.deletes
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "hits": self.hits,
            "misses": self.misses,
            "sets": self.sets,
            "deletes": self.deletes,
            "errors": self.errors,
            "hit_rate": self.hit_rate,
            "total_operations": self.total_operations,
        }


class MemoryCache:
    """
    Simple in-memory LRU cache as fallback.
    
    Used when Redis is unavailable or for hybrid caching strategy.
    """
    
    def __init__(self, max_size: int = 1000):
        """
        Initialize memory cache.
        
        Args:
            max_size: Maximum number of items to store
        """
        self.max_size = max_size
        self.cache: OrderedDict = OrderedDict()
        self.ttl_map: Dict[str, datetime] = {}
    
    def get(self, key: str) -> Optional[Any]:
        """
        Get value from cache.
        
        Args:
            key: Cache key
        
        Returns:
            Cached value or None if not found/expired
        """
        # Check if key exists and not expired
        if key in self.cache:
            if key in self.ttl_map:
                if datetime.now() > self.ttl_map[key]:
                    # Expired, remove
                    del self.cache[key]
                    del self.ttl_map[key]
                    return None
            
            # Move to end (LRU)
            self.cache.move_to_end(key)
            return self.cache[key]
        
        return None
    
    def set(self, key: str, value: Any, ttl: Optional[int] = None) -> bool:
        """
        Set value in cache.
        
        Args:
            key: Cache key
            value: Value to cache
            ttl: Time to live in seconds
        
        Returns:
            True if successful
        """
        # Remove oldest if at capacity
        if key not in self.cache and len(self.cache) >= self.max_size:
            self.cache.popitem(last=False)
        
        self.cache[key] = value
        
        # Set TTL if provided
        if ttl:
            self.ttl_map[key] = datetime.now() + timedelta(seconds=ttl)
        
        return True
    
    def delete(self, key: str) -> bool:
        """Delete key from cache."""
        if key in self.cache:
            del self.cache[key]
            if key in self.ttl_map:
                del self.ttl_map[key]
            return True
        return False
    
    def clear(self) -> None:
        """Clear all cached items."""
        self.cache.clear()
        self.ttl_map.clear()
    
    def size(self) -> int:
        """Get current cache size."""
        return len(self.cache)


class RedisCacheManager:
    """
    Redis-based cache manager with automatic fallback.
    
    Features:
    - Automatic serialization (JSON/pickle)
    - Compression for large values
    - TTL management
    - Connection pooling
    - Fallback to memory cache on errors
    - Performance metrics
    """
    
    def __init__(
        self,
        config: Optional[CacheConfig] = None,
        enable_redis: bool = True
    ):
        """
        Initialize cache manager.
        
        Args:
            config: Cache configuration
            enable_redis: Whether to use Redis (False for testing)
        """
        from src.services.caching.cache_config import default_cache_config
        
        self.config = config or default_cache_config
        self.stats = CacheStats()
        
        # Initialize memory cache (always available)
        self.memory_cache = MemoryCache(
            max_size=self.config.max_memory_cache_size
        )
        
        # Initialize Redis connection
        self.redis_client = None
        self.redis_available = False
        
        if enable_redis and self.config.strategy != CacheStrategy.MEMORY:
            try:
                self._init_redis()
            except Exception as e:
                logger.warning(
                    f"Redis initialization failed: {e}. "
                    "Using memory cache only."
                )
    
    def _init_redis(self) -> None:
        """Initialize Redis connection."""
        try:
            import redis
            
            pool = redis.ConnectionPool(
                host=self.config.redis_host,
                port=self.config.redis_port,
                db=self.config.redis_db,
                password=self.config.redis_password,
                max_connections=self.config.max_connections,
                socket_timeout=self.config.socket_timeout,
                socket_connect_timeout=self.config.socket_connect_timeout,
                decode_responses=False,  # We handle encoding
                **self.config.connection_pool_kwargs
            )
            
            self.redis_client = redis.Redis(connection_pool=pool)
            
            # Test connection
            self.redis_client.ping()
            self.redis_available = True
            
            logger.info("Redis cache initialized successfully")
            
        except ImportError:
            logger.warning("redis package not installed. Using memory cache.")
        except Exception as e:
            logger.error(f"Redis connection failed: {e}")
            self.redis_client = None
    
    def _serialize(self, value: Any) -> bytes:
        """
        Serialize value for storage.
        
        Tries JSON first, falls back to pickle for complex objects.
        Compresses large values.
        """
        try:
            # Try JSON first (faster, more portable)
            serialized = json.dumps(value).encode()
        except (TypeError, ValueError):
            # Fall back to pickle for complex objects
            serialized = pickle.dumps(value)
        
        # Compress if large enough
        if (
            self.config.enable_compression
            and len(serialized) > self.config.compression_threshold
        ):
            compressed = zlib.compress(serialized)
            # Add marker for compression
            return b"COMPRESSED:" + compressed
        
        return serialized
    
    def _deserialize(self, data: bytes) -> Any:
        """Deserialize stored value."""
        # Check for compression marker
        if data.startswith(b"COMPRESSED:"):
            data = zlib.decompress(data[11:])  # Remove marker
        
        try:
            # Try JSON first
            return json.loads(data.decode())
        except (json.JSONDecodeError, UnicodeDecodeError):
            # Fall back to pickle
            return pickle.loads(data)
    
    def get(self, key: str) -> Optional[Any]:
        """
        Get value from cache.
        
        Checks Redis first, then memory cache.
        
        Args:
            key: Cache key
        
        Returns:
            Cached value or None if not found
        """
        try:
            # Try Redis first
            if self.redis_available and self.redis_client:
                value = self.redis_client.get(key)
                if value is not None:
                    self.stats.hits += 1
                    return self._deserialize(value)
            
            # Try memory cache
            value = self.memory_cache.get(key)
            if value is not None:
                self.stats.hits += 1
                return value
            
            self.stats.misses += 1
            return None
            
        except Exception as e:
            logger.error(f"Cache get error for key {key}: {e}")
            self.stats.errors += 1
            
            # Try memory cache as last resort
            value = self.memory_cache.get(key)
            if value is not None:
                self.stats.hits += 1
                return value
            
            self.stats.misses += 1
            return None
    
    def set(
        self,
        key: str,
        value: Any,
        ttl: Optional[int] = None
    ) -> bool:
        """
        Set value in cache.
        
        Stores in both Redis and memory cache (hybrid strategy).
        
        Args:
            key: Cache key
            value: Value to cache
            ttl: Time to live in seconds (uses default if not provided)
        
        Returns:
            True if successful
        """
        if ttl is None:
            ttl = self.config.default_ttl
        
        try:
            # Always store in memory cache
            self.memory_cache.set(key, value, ttl)
            
            # Store in Redis if available
            if self.redis_available and self.redis_client:
                serialized = self._serialize(value)
                self.redis_client.setex(key, ttl, serialized)
            
            self.stats.sets += 1
            return True
            
        except Exception as e:
            logger.error(f"Cache set error for key {key}: {e}")
            self.stats.errors += 1
            
            # Still try memory cache
            try:
                self.memory_cache.set(key, value, ttl)
                return True
            except Exception:
                return False
    
    def delete(self, key: str) -> bool:
        """
        Delete key from cache.
        
        Args:
            key: Cache key
        
        Returns:
            True if key existed and was deleted
        """
        try:
            deleted = False
            
            # Delete from Redis
            if self.redis_available and self.redis_client:
                deleted = bool(self.redis_client.delete(key))
            
            # Delete from memory cache
            deleted = self.memory_cache.delete(key) or deleted
            
            if deleted:
                self.stats.deletes += 1
            
            return deleted
            
        except Exception as e:
            logger.error(f"Cache delete error for key {key}: {e}")
            self.stats.errors += 1
            return False
    
    def clear(self, pattern: Optional[str] = None) -> int:
        """
        Clear cache entries.
        
        Args:
            pattern: Optional key pattern to match (e.g., 'ai_response:*')
        
        Returns:
            Number of keys deleted
        """
        try:
            count = 0
            
            # Clear Redis
            if self.redis_available and self.redis_client:
                if pattern:
                    keys = self.redis_client.keys(pattern)
                    if keys:
                        count += self.redis_client.delete(*keys)
                else:
                    self.redis_client.flushdb()
                    count += 1  # Unknown count
            
            # Clear memory cache
            if not pattern:
                self.memory_cache.clear()
            
            return count
            
        except Exception as e:
            logger.error(f"Cache clear error: {e}")
            self.stats.errors += 1
            return 0
    
    def exists(self, key: str) -> bool:
        """Check if key exists in cache."""
        try:
            if self.redis_available and self.redis_client:
                return bool(self.redis_client.exists(key))
            return self.memory_cache.get(key) is not None
        except Exception:
            return False
    
    def get_ttl(self, key: str) -> Optional[int]:
        """
        Get remaining TTL for key.
        
        Args:
            key: Cache key
        
        Returns:
            Remaining TTL in seconds, or None if key doesn't exist
        """
        try:
            if self.redis_available and self.redis_client:
                ttl = self.redis_client.ttl(key)
                return ttl if ttl > 0 else None
            return None
        except Exception:
            return None
    
    def get_stats(self) -> Dict[str, Any]:
        """
        Get cache performance statistics.
        
        Returns:
            Dictionary with cache statistics
        """
        stats = self.stats.to_dict()
        stats["redis_available"] = self.redis_available
        stats["memory_cache_size"] = self.memory_cache.size()
        
        if self.redis_available and self.redis_client:
            try:
                info = self.redis_client.info("stats")
                stats["redis_keys"] = self.redis_client.dbsize()
                stats["redis_hits"] = info.get("keyspace_hits", 0)
                stats["redis_misses"] = info.get("keyspace_misses", 0)
            except Exception:
                pass
        
        return stats
    
    def health_check(self) -> Dict[str, Any]:
        """
        Perform health check on cache system.
        
        Returns:
            Health status dictionary
        """
        health = {
            "status": "healthy",
            "redis_available": self.redis_available,
            "memory_cache_operational": True,
            "errors": []
        }
        
        # Test Redis connection
        if self.redis_available and self.redis_client:
            try:
                self.redis_client.ping()
            except Exception as e:
                health["redis_available"] = False
                health["errors"].append(f"Redis ping failed: {e}")
        
        # Test memory cache
        try:
            test_key = "__health_check__"
            self.memory_cache.set(test_key, "test")
            self.memory_cache.get(test_key)
            self.memory_cache.delete(test_key)
        except Exception as e:
            health["memory_cache_operational"] = False
            health["errors"].append(f"Memory cache test failed: {e}")
        
        # Overall status
        if health["errors"]:
            health["status"] = "degraded" if health[
                "memory_cache_operational"
            ] else "unhealthy"
        
        return health
    
    def reset_stats(self) -> None:
        """Reset cache statistics."""
        self.stats = CacheStats()


# Global cache manager instance
_global_cache_manager: Optional[RedisCacheManager] = None


def get_cache_manager() -> RedisCacheManager:
    """
    Get global cache manager instance.
    
    Creates instance on first call (lazy initialization).
    
    Returns:
        Global RedisCacheManager instance
    """
    global _global_cache_manager
    
    if _global_cache_manager is None:
        _global_cache_manager = RedisCacheManager()
    
    return _global_cache_manager

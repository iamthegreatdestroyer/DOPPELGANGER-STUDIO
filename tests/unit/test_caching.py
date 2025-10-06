"""
Copyright (c) 2025 DOPPELGANGER STUDIO. All Rights Reserved.

Tests for caching system (config and manager).
"""

import pytest
import time
from unittest.mock import Mock, patch, MagicMock

from src.services.caching import (
    CacheConfig,
    CacheStrategy,
    CacheTTL,
    generate_cache_key,
    generate_ai_cache_key,
    generate_voice_profile_cache_key,
    RedisCacheManager,
    MemoryCache,
    CacheStats,
)


# ============================================================================
# CACHE CONFIG TESTS
# ============================================================================

class TestCacheConfig:
    """Test cache configuration."""
    
    def test_default_config(self):
        """Test default configuration values."""
        config = CacheConfig()
        
        assert config.redis_host == "localhost"
        assert config.redis_port == 6379
        assert config.default_ttl == CacheTTL.LONG.value
        assert config.strategy == CacheStrategy.HYBRID
        assert config.cache_ai_responses is True
    
    def test_custom_config(self):
        """Test custom configuration."""
        config = CacheConfig(
            redis_host="redis.example.com",
            redis_port=6380,
            default_ttl=CacheTTL.SHORT.value,
            strategy=CacheStrategy.REDIS
        )
        
        assert config.redis_host == "redis.example.com"
        assert config.redis_port == 6380
        assert config.default_ttl == CacheTTL.SHORT.value
        assert config.strategy == CacheStrategy.REDIS
    
    def test_get_ttl_by_type(self):
        """Test getting TTL for specific cache types."""
        config = CacheConfig()
        
        assert config.get_ttl("ai_response") == CacheTTL.LONG.value
        assert config.get_ttl("voice_profile") == CacheTTL.VERY_LONG.value
        assert config.get_ttl("unknown_type") == config.default_ttl


class TestCacheKeyGeneration:
    """Test cache key generation utilities."""
    
    def test_generate_cache_key_deterministic(self):
        """Test that same inputs produce same key."""
        key1 = generate_cache_key("test", arg1="value1", arg2="value2")
        key2 = generate_cache_key("test", arg1="value1", arg2="value2")
        
        assert key1 == key2
    
    def test_generate_cache_key_different_order(self):
        """Test that argument order doesn't matter."""
        key1 = generate_cache_key("test", arg1="value1", arg2="value2")
        key2 = generate_cache_key("test", arg2="value2", arg1="value1")
        
        assert key1 == key2
    
    def test_generate_cache_key_format(self):
        """Test cache key format."""
        key = generate_cache_key("prefix", test="value")
        
        assert key.startswith("prefix:")
        assert len(key) > 7  # prefix + colon + hash
    
    def test_generate_ai_cache_key(self):
        """Test AI response cache key generation."""
        key = generate_ai_cache_key(
            prompt="Generate dialogue",
            model="claude-sonnet-4",
            temperature=0.7
        )
        
        assert key.startswith("ai_response:")
    
    def test_generate_voice_profile_cache_key(self):
        """Test voice profile cache key generation."""
        key = generate_voice_profile_cache_key(
            character_name="Luna",
            show_context="I Love Luna"
        )
        
        assert key.startswith("voice_profile:")


# ============================================================================
# CACHE STATS TESTS
# ============================================================================

class TestCacheStats:
    """Test cache statistics."""
    
    def test_initial_stats(self):
        """Test initial statistics values."""
        stats = CacheStats()
        
        assert stats.hits == 0
        assert stats.misses == 0
        assert stats.sets == 0
        assert stats.deletes == 0
        assert stats.errors == 0
    
    def test_hit_rate_calculation(self):
        """Test hit rate calculation."""
        stats = CacheStats(hits=75, misses=25)
        
        assert stats.hit_rate == 0.75
    
    def test_hit_rate_no_operations(self):
        """Test hit rate with no operations."""
        stats = CacheStats()
        
        assert stats.hit_rate == 0.0
    
    def test_total_operations(self):
        """Test total operations calculation."""
        stats = CacheStats(hits=10, misses=5, sets=20, deletes=3)
        
        assert stats.total_operations == 38
    
    def test_to_dict(self):
        """Test conversion to dictionary."""
        stats = CacheStats(hits=10, misses=5)
        data = stats.to_dict()
        
        assert data["hits"] == 10
        assert data["misses"] == 5
        assert data["hit_rate"] == 0.666666666666666667 or abs(
            data["hit_rate"] - 0.67
        ) < 0.01


# ============================================================================
# MEMORY CACHE TESTS
# ============================================================================

class TestMemoryCache:
    """Test in-memory cache."""
    
    def test_set_and_get(self):
        """Test basic set and get operations."""
        cache = MemoryCache(max_size=10)
        
        cache.set("key1", "value1")
        assert cache.get("key1") == "value1"
    
    def test_get_nonexistent(self):
        """Test getting nonexistent key."""
        cache = MemoryCache(max_size=10)
        
        assert cache.get("nonexistent") is None
    
    def test_lru_eviction(self):
        """Test LRU eviction when max size reached."""
        cache = MemoryCache(max_size=3)
        
        cache.set("key1", "value1")
        cache.set("key2", "value2")
        cache.set("key3", "value3")
        cache.set("key4", "value4")  # Should evict key1
        
        assert cache.get("key1") is None
        assert cache.get("key2") == "value2"
        assert cache.get("key4") == "value4"
    
    def test_ttl_expiration(self):
        """Test TTL expiration."""
        cache = MemoryCache(max_size=10)
        
        cache.set("key1", "value1", ttl=1)  # 1 second TTL
        assert cache.get("key1") == "value1"
        
        time.sleep(1.1)  # Wait for expiration
        assert cache.get("key1") is None
    
    def test_delete(self):
        """Test delete operation."""
        cache = MemoryCache(max_size=10)
        
        cache.set("key1", "value1")
        assert cache.delete("key1") is True
        assert cache.get("key1") is None
    
    def test_delete_nonexistent(self):
        """Test deleting nonexistent key."""
        cache = MemoryCache(max_size=10)
        
        assert cache.delete("nonexistent") is False
    
    def test_clear(self):
        """Test clear operation."""
        cache = MemoryCache(max_size=10)
        
        cache.set("key1", "value1")
        cache.set("key2", "value2")
        
        cache.clear()
        
        assert cache.get("key1") is None
        assert cache.get("key2") is None
        assert cache.size() == 0
    
    def test_size(self):
        """Test size tracking."""
        cache = MemoryCache(max_size=10)
        
        assert cache.size() == 0
        
        cache.set("key1", "value1")
        assert cache.size() == 1
        
        cache.set("key2", "value2")
        assert cache.size() == 2
        
        cache.delete("key1")
        assert cache.size() == 1


# ============================================================================
# REDIS CACHE MANAGER TESTS
# ============================================================================

class TestRedisCacheManager:
    """Test Redis cache manager."""
    
    def test_initialization_memory_only(self):
        """Test initialization with memory cache only."""
        manager = RedisCacheManager(enable_redis=False)
        
        assert manager.memory_cache is not None
        assert manager.redis_client is None
        assert manager.redis_available is False
    
    def test_set_and_get_memory(self):
        """Test set and get with memory cache."""
        manager = RedisCacheManager(enable_redis=False)
        
        assert manager.set("test_key", "test_value")
        assert manager.get("test_key") == "test_value"
    
    def test_get_nonexistent(self):
        """Test getting nonexistent key."""
        manager = RedisCacheManager(enable_redis=False)
        
        assert manager.get("nonexistent") is None
    
    def test_delete(self):
        """Test delete operation."""
        manager = RedisCacheManager(enable_redis=False)
        
        manager.set("test_key", "test_value")
        assert manager.delete("test_key") is True
        assert manager.get("test_key") is None
    
    def test_exists(self):
        """Test exists check."""
        manager = RedisCacheManager(enable_redis=False)
        
        manager.set("test_key", "test_value")
        assert manager.exists("test_key") is True
        assert manager.exists("nonexistent") is False
    
    def test_clear(self):
        """Test clear operation."""
        manager = RedisCacheManager(enable_redis=False)
        
        manager.set("key1", "value1")
        manager.set("key2", "value2")
        
        manager.clear()
        
        assert manager.get("key1") is None
        assert manager.get("key2") is None
    
    def test_stats_tracking(self):
        """Test statistics tracking."""
        manager = RedisCacheManager(enable_redis=False)
        
        manager.set("key1", "value1")
        manager.get("key1")  # Hit
        manager.get("key2")  # Miss
        
        stats = manager.get_stats()
        
        assert stats["hits"] == 1
        assert stats["misses"] == 1
        assert stats["sets"] == 1
    
    def test_health_check(self):
        """Test health check."""
        manager = RedisCacheManager(enable_redis=False)
        
        health = manager.health_check()
        
        assert health["status"] in ["healthy", "degraded"]
        assert health["memory_cache_operational"] is True
    
    def test_reset_stats(self):
        """Test statistics reset."""
        manager = RedisCacheManager(enable_redis=False)
        
        manager.set("key1", "value1")
        manager.get("key1")
        
        manager.reset_stats()
        
        stats = manager.get_stats()
        assert stats["hits"] == 0
        assert stats["sets"] == 0
    
    def test_serialization_json(self):
        """Test JSON serialization."""
        manager = RedisCacheManager(enable_redis=False)
        
        data = {"key": "value", "number": 42}
        manager.set("test_key", data)
        
        result = manager.get("test_key")
        assert result == data
    
    def test_serialization_complex_object(self):
        """Test serialization of complex objects."""
        manager = RedisCacheManager(enable_redis=False)
        
        class CustomObject:
            def __init__(self, value):
                self.value = value
        
        obj = CustomObject(42)
        manager.set("test_key", obj)
        
        result = manager.get("test_key")
        assert isinstance(result, CustomObject)
        assert result.value == 42
    
    def test_ttl_with_custom_value(self):
        """Test setting custom TTL."""
        manager = RedisCacheManager(enable_redis=False)
        
        manager.set("test_key", "test_value", ttl=3600)
        
        # Value should be accessible
        assert manager.get("test_key") == "test_value"
    
    def test_compression_threshold(self):
        """Test compression for large values."""
        config = CacheConfig(
            enable_compression=True,
            compression_threshold=100
        )
        manager = RedisCacheManager(config=config, enable_redis=False)
        
        # Large value should be compressed
        large_value = "x" * 1000
        manager.set("large_key", large_value)
        
        result = manager.get("large_key")
        assert result == large_value


# ============================================================================
# INTEGRATION TESTS
# ============================================================================

class TestCacheIntegration:
    """Integration tests for caching system."""
    
    def test_cache_workflow(self):
        """Test complete cache workflow."""
        manager = RedisCacheManager(enable_redis=False)
        
        # Set value
        assert manager.set("workflow_key", "workflow_value")
        
        # Get value
        assert manager.get("workflow_key") == "workflow_value"
        
        # Check exists
        assert manager.exists("workflow_key")
        
        # Delete value
        assert manager.delete("workflow_key")
        
        # Verify deleted
        assert manager.get("workflow_key") is None
        assert not manager.exists("workflow_key")
    
    def test_multiple_cache_types(self):
        """Test caching different types of data."""
        manager = RedisCacheManager(enable_redis=False)
        
        # String
        manager.set("string_key", "string_value")
        assert manager.get("string_key") == "string_value"
        
        # Number
        manager.set("number_key", 42)
        assert manager.get("number_key") == 42
        
        # List
        manager.set("list_key", [1, 2, 3])
        assert manager.get("list_key") == [1, 2, 3]
        
        # Dict
        manager.set("dict_key", {"a": 1, "b": 2})
        assert manager.get("dict_key") == {"a": 1, "b": 2}
    
    def test_cache_performance_tracking(self):
        """Test cache performance metrics."""
        manager = RedisCacheManager(enable_redis=False)
        
        # Perform operations
        for i in range(10):
            manager.set(f"key_{i}", f"value_{i}")
        
        for i in range(10):
            manager.get(f"key_{i}")  # Hits
        
        for i in range(5):
            manager.get(f"missing_{i}")  # Misses
        
        stats = manager.get_stats()
        
        assert stats["sets"] == 10
        assert stats["hits"] == 10
        assert stats["misses"] == 5
        assert 0.6 < stats["hit_rate"] < 0.7  # ~66.7%

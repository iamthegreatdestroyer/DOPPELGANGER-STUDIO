"""
Unit tests for audio cache.

Copyright (c) 2025. All Rights Reserved. Patent Pending.
"""

import pytest
from pathlib import Path

from src.services.voiceover.audio_cache import AudioCache


@pytest.fixture
def cache(tmp_path):
    """Create test cache."""
    return AudioCache(cache_dir=tmp_path / "cache")


def test_cache_key_generation(cache):
    """Test cache key generation."""
    key1 = cache.generate_key("Hello", "rachel", {"stability": 0.75})
    key2 = cache.generate_key("Hello", "rachel", {"stability": 0.75})
    key3 = cache.generate_key("Goodbye", "rachel", {"stability": 0.75})
    
    # Same input = same key
    assert key1 == key2
    
    # Different input = different key
    assert key1 != key3


def test_cache_operations(cache, tmp_path):
    """Test cache get/set."""
    # Create test file
    test_file = tmp_path / "test.mp3"
    test_file.write_text("test audio")
    
    key = "test_key_123"
    
    # Cache miss
    assert cache.get(key) is None
    
    # Set
    cache.set(key, test_file)
    
    # Cache hit
    cached = cache.get(key)
    assert cached is not None
    assert cached.exists()


def test_cache_stats(cache):
    """Test cache statistics."""
    stats = cache.get_stats()
    
    assert 'total_entries' in stats
    assert 'cache_dir' in stats
    assert stats['total_entries'] == 0

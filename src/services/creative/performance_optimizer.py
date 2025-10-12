"""
Performance Optimizer - Advanced caching and performance enhancements.

Provides intelligent caching strategies, batch processing optimization,
and performance monitoring for script generation pipeline.

Copyright (c) 2025. All Rights Reserved. Patent Pending.
"""

import logging
import asyncio
import hashlib
import json
from typing import Dict, List, Optional, Any, Callable
from datetime import datetime, timedelta
from dataclasses import dataclass
from collections import OrderedDict

logger = logging.getLogger(__name__)


@dataclass
class CacheStats:
    """Cache performance statistics."""
    hits: int = 0
    misses: int = 0
    evictions: int = 0
    total_size_bytes: int = 0
    
    @property
    def hit_rate(self) -> float:
        total = self.hits + self.misses
        return self.hits / total if total > 0 else 0.0


class PerformanceOptimizer:
    """
    Advanced performance optimization system.
    
    Provides multi-level caching, batch processing, and performance
    monitoring for the script generation pipeline.
    """
    
    def __init__(
        self,
        memory_cache_size: int = 100,
        enable_batch_optimization: bool = True
    ):
        self.memory_cache_size = memory_cache_size
        self.enable_batch = enable_batch_optimization
        
        # LRU cache
        self._memory_cache: OrderedDict[str, Any] = OrderedDict()
        self._cache_timestamps: Dict[str, datetime] = {}
        self._cache_stats = CacheStats()
        
        logger.info(f"PerformanceOptimizer initialized (cache_size={memory_cache_size})")
    
    def cache_key(self, *args, **kwargs) -> str:
        """Generate cache key from arguments."""
        key_data = json.dumps({'args': args, 'kwargs': kwargs}, sort_keys=True)
        return hashlib.md5(key_data.encode()).hexdigest()
    
    def get_cached(self, key: str, max_age_seconds: int = 3600) -> Optional[Any]:
        """Get cached value if available and not expired."""
        if key in self._memory_cache:
            # Check age
            cached_at = self._cache_timestamps.get(key)
            if cached_at:
                age = (datetime.now() - cached_at).total_seconds()
                if age > max_age_seconds:
                    # Expired
                    del self._memory_cache[key]
                    del self._cache_timestamps[key]
                    self._cache_stats.evictions += 1
                    self._cache_stats.misses += 1
                    return None
            
            # Move to end (LRU)
            self._memory_cache.move_to_end(key)
            self._cache_stats.hits += 1
            return self._memory_cache[key]
        
        self._cache_stats.misses += 1
        return None
    
    def set_cached(self, key: str, value: Any):
        """Cache a value with LRU eviction."""
        # Evict oldest if at capacity
        if len(self._memory_cache) >= self.memory_cache_size:
            oldest_key = next(iter(self._memory_cache))
            del self._memory_cache[oldest_key]
            if oldest_key in self._cache_timestamps:
                del self._cache_timestamps[oldest_key]
            self._cache_stats.evictions += 1
        
        self._memory_cache[key] = value
        self._cache_timestamps[key] = datetime.now()
    
    async def batch_process(
        self,
        items: List[Any],
        process_fn: Callable,
        batch_size: int = 10,
        parallel: bool = True
    ) -> List[Any]:
        """Process items in optimized batches."""
        results = []
        
        for i in range(0, len(items), batch_size):
            batch = items[i:i + batch_size]
            
            if parallel:
                # Process batch in parallel
                batch_results = await asyncio.gather(
                    *[process_fn(item) for item in batch]
                )
            else:
                # Process sequentially
                batch_results = []
                for item in batch:
                    result = await process_fn(item)
                    batch_results.append(result)
            
            results.extend(batch_results)
        
        return results
    
    def get_stats(self) -> CacheStats:
        """Get cache statistics."""
        return self._cache_stats
    
    def clear_cache(self):
        """Clear all caches."""
        self._memory_cache.clear()
        self._cache_timestamps.clear()
        logger.info("Performance cache cleared")


# Global optimizer instance
_optimizer_instance = None

def get_performance_optimizer() -> PerformanceOptimizer:
    """Get global performance optimizer."""
    global _optimizer_instance
    if _optimizer_instance is None:
        _optimizer_instance = PerformanceOptimizer()
    return _optimizer_instance

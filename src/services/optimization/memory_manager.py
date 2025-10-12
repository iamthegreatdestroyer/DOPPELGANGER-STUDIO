"""
Memory Optimization Manager - Adaptive memory management and resource pooling.

Provides intelligent memory management for the script generation pipeline,
including object pooling, garbage collection optimization, and memory monitoring.

Copyright (c) 2025. All Rights Reserved. Patent Pending.
"""

from typing import Dict, List, Optional, Any, TypeVar, Generic, Callable
import asyncio
import logging
import gc
import weakref
import psutil
import time
from dataclasses import dataclass, field
from collections import defaultdict
from datetime import datetime, timedelta
import threading

logger = logging.getLogger(__name__)

T = TypeVar('T')


@dataclass
class MemoryStats:
    """Memory usage statistics."""
    timestamp: datetime
    total_memory: int  # bytes
    available_memory: int  # bytes
    percent_used: float
    process_memory: int  # bytes
    gc_collections: Dict[int, int]  # generation -> count
    pool_sizes: Dict[str, int]  # pool_name -> size
    

@dataclass
class MemoryThresholds:
    """Memory usage thresholds for triggering actions."""
    warning_percent: float = 80.0
    critical_percent: float = 90.0
    force_gc_percent: float = 85.0
    pool_cleanup_percent: float = 75.0
    

class ObjectPool(Generic[T]):
    """
    Generic object pool for reducing allocation overhead.
    
    Maintains a pool of reusable objects to minimize garbage collection
    pressure from frequently created/destroyed instances.
    
    Example:
        >>> pool = ObjectPool(
        ...     factory=lambda: ExpensiveObject(),
        ...     reset=lambda obj: obj.reset(),
        ...     max_size=100
        ... )
        >>> obj = pool.acquire()
        >>> # use obj
        >>> pool.release(obj)
    """
    
    def __init__(
        self,
        factory: Callable[[], T],
        reset: Optional[Callable[[T], None]] = None,
        max_size: int = 100,
        min_size: int = 10
    ):
        """
        Initialize object pool.
        
        Args:
            factory: Function to create new objects
            reset: Optional function to reset objects before reuse
            max_size: Maximum pool size
            min_size: Minimum pool size to maintain
        """
        self._factory = factory
        self._reset = reset
        self._max_size = max_size
        self._min_size = min_size
        self._pool: List[T] = []
        self._in_use: weakref.WeakSet = weakref.WeakSet()
        self._lock = threading.Lock()
        self._created_count = 0
        self._reused_count = 0
        
        # Pre-populate pool
        self._populate(min_size)
    
    def _populate(self, count: int):
        """Pre-populate pool with objects."""
        for _ in range(count):
            if len(self._pool) < self._max_size:
                obj = self._factory()
                self._pool.append(obj)
                self._created_count += 1
    
    def acquire(self) -> T:
        """
        Acquire object from pool.
        
        Returns:
            Pooled object (reused or newly created)
        """
        with self._lock:
            if self._pool:
                obj = self._pool.pop()
                self._reused_count += 1
            else:
                obj = self._factory()
                self._created_count += 1
            
            self._in_use.add(obj)
            return obj
    
    def release(self, obj: T):
        """
        Return object to pool.
        
        Args:
            obj: Object to return
        """
        with self._lock:
            # Reset if reset function provided
            if self._reset:
                try:
                    self._reset(obj)
                except Exception as e:
                    logger.warning(f"Failed to reset pooled object: {e}")
                    return  # Don't return to pool if reset fails
            
            # Add back to pool if not full
            if len(self._pool) < self._max_size:
                self._pool.append(obj)
            
            # Remove from in-use tracking
            self._in_use.discard(obj)
    
    def cleanup(self, aggressive: bool = False):
        """
        Clean up pool, removing excess objects.
        
        Args:
            aggressive: If True, reduce to minimum size
        """
        with self._lock:
            target_size = self._min_size if aggressive else self._max_size // 2
            
            while len(self._pool) > target_size:
                self._pool.pop()
    
    def get_stats(self) -> Dict:
        """Get pool statistics."""
        with self._lock:
            return {
                'pool_size': len(self._pool),
                'in_use': len(self._in_use),
                'created_total': self._created_count,
                'reused_total': self._reused_count,
                'reuse_rate': (
                    self._reused_count / self._created_count 
                    if self._created_count > 0 else 0.0
                )
            }


class MemoryManager:
    """
    Adaptive memory management system.
    
    Monitors memory usage, manages object pools, optimizes garbage collection,
    and provides memory profiling utilities.
    """
    
    def __init__(self, thresholds: Optional[MemoryThresholds] = None):
        """
        Initialize memory manager.
        
        Args:
            thresholds: Custom memory thresholds
        """
        self.thresholds = thresholds or MemoryThresholds()
        self._pools: Dict[str, ObjectPool] = {}
        self._monitoring = False
        self._monitor_task: Optional[asyncio.Task] = None
        self._stats_history: List[MemoryStats] = []
        self._max_history = 1000
        self._callbacks: Dict[str, List[Callable]] = defaultdict(list)
        
    def create_pool(
        self,
        name: str,
        factory: Callable[[], T],
        reset: Optional[Callable[[T], None]] = None,
        max_size: int = 100,
        min_size: int = 10
    ) -> ObjectPool[T]:
        """Create and register an object pool."""
        pool = ObjectPool(
            factory=factory,
            reset=reset,
            max_size=max_size,
            min_size=min_size
        )
        self._pools[name] = pool
        logger.info(f"Created object pool '{name}' (min={min_size}, max={max_size})")
        return pool
    
    def get_pool(self, name: str) -> Optional[ObjectPool]:
        """Get pool by name."""
        return self._pools.get(name)
    
    def get_current_stats(self) -> MemoryStats:
        """Get current memory statistics."""
        process = psutil.Process()
        memory_info = process.memory_info()
        virtual_memory = psutil.virtual_memory()
        
        return MemoryStats(
            timestamp=datetime.now(),
            total_memory=virtual_memory.total,
            available_memory=virtual_memory.available,
            percent_used=virtual_memory.percent,
            process_memory=memory_info.rss,
            gc_collections={i: gc.get_count()[i] for i in range(3)},
            pool_sizes={name: len(pool._pool) for name, pool in self._pools.items()}
        )
    
    async def start_monitoring(self, interval: float = 5.0):
        """Start background memory monitoring."""
        if self._monitoring:
            logger.warning("Memory monitoring already started")
            return
        
        self._monitoring = True
        self._monitor_task = asyncio.create_task(self._monitor_loop(interval))
        logger.info(f"Started memory monitoring (interval={interval}s)")
    
    async def stop_monitoring(self):
        """Stop background memory monitoring."""
        if not self._monitoring:
            return
        
        self._monitoring = False
        if self._monitor_task:
            self._monitor_task.cancel()
            try:
                await self._monitor_task
            except asyncio.CancelledError:
                pass
        
        logger.info("Stopped memory monitoring")
    
    async def _monitor_loop(self, interval: float):
        """Background monitoring loop."""
        while self._monitoring:
            try:
                stats = self.get_current_stats()
                self._stats_history.append(stats)
                
                if len(self._stats_history) > self._max_history:
                    self._stats_history = self._stats_history[-self._max_history:]
                
                await self._check_thresholds(stats)
                await asyncio.sleep(interval)
                
            except Exception as e:
                logger.error(f"Error in memory monitoring: {e}")
                await asyncio.sleep(interval)
    
    async def _check_thresholds(self, stats: MemoryStats):
        """Check memory thresholds and trigger appropriate actions."""
        percent = stats.percent_used
        
        if percent >= self.thresholds.critical_percent:
            logger.critical(f"Critical memory usage: {percent:.1f}%")
            await self._trigger_callbacks('critical', stats)
            await self.aggressive_cleanup()
        
        elif percent >= self.thresholds.force_gc_percent:
            logger.warning(f"High memory usage: {percent:.1f}% - forcing GC")
            await self._trigger_callbacks('high', stats)
            self.force_gc()
        
        elif percent >= self.thresholds.pool_cleanup_percent:
            logger.info(f"Moderate memory usage: {percent:.1f}% - cleaning pools")
            await self._trigger_callbacks('moderate', stats)
            self.cleanup_pools()
        
        elif percent >= self.thresholds.warning_percent:
            logger.info(f"Memory usage warning: {percent:.1f}%")
            await self._trigger_callbacks('warning', stats)
    
    def force_gc(self, generation: int = 2):
        """Force garbage collection."""
        logger.debug(f"Forcing garbage collection (generation {generation})")
        collected = gc.collect(generation)
        logger.debug(f"Collected {collected} objects")
    
    def cleanup_pools(self, aggressive: bool = False):
        """Clean up all registered object pools."""
        logger.info(f"Cleaning up {len(self._pools)} object pools")
        for name, pool in self._pools.items():
            try:
                pool.cleanup(aggressive=aggressive)
                logger.debug(f"Cleaned pool '{name}'")
            except Exception as e:
                logger.error(f"Failed to clean pool '{name}': {e}")
    
    async def aggressive_cleanup(self):
        """Perform aggressive memory cleanup."""
        logger.warning("Performing aggressive memory cleanup")
        
        self.cleanup_pools(aggressive=True)
        
        for gen in range(3):
            self.force_gc(generation=gen)
            await asyncio.sleep(0.1)
        
        logger.info("Aggressive cleanup complete")
    
    def register_callback(self, level: str, callback: Callable):
        """Register callback for memory threshold events."""
        self._callbacks[level].append(callback)
    
    async def _trigger_callbacks(self, level: str, stats: MemoryStats):
        """Trigger callbacks for threshold level."""
        for callback in self._callbacks.get(level, []):
            try:
                if asyncio.iscoroutinefunction(callback):
                    await callback(stats)
                else:
                    callback(stats)
            except Exception as e:
                logger.error(f"Callback error at level '{level}': {e}")
    
    def get_pool_stats(self) -> Dict[str, Dict]:
        """Get statistics for all pools."""
        return {name: pool.get_stats() for name, pool in self._pools.items()}
    
    def detect_memory_leaks(self, threshold: float = 10.0) -> List[Dict]:
        """Detect potential memory leaks based on usage trends."""
        if len(self._stats_history) < 10:
            return []
        
        leaks = []
        
        recent = self._stats_history[-10:]
        older = self._stats_history[-30:-10] if len(self._stats_history) >= 30 else self._stats_history[:-10]
        
        if not older:
            return []
        
        recent_avg = sum(s.process_memory for s in recent) / len(recent)
        older_avg = sum(s.process_memory for s in older) / len(older)
        
        percent_increase = ((recent_avg - older_avg) / older_avg) * 100
        
        if percent_increase > threshold:
            leaks.append({
                'type': 'process_memory_growth',
                'percent_increase': percent_increase,
                'recent_avg_mb': recent_avg / 1024 / 1024,
                'older_avg_mb': older_avg / 1024 / 1024,
                'severity': 'high' if percent_increase > 25 else 'moderate'
            })
        
        return leaks


# Global instance
_memory_manager: Optional[MemoryManager] = None


def get_memory_manager() -> MemoryManager:
    """Get global memory manager instance."""
    global _memory_manager
    if _memory_manager is None:
        _memory_manager = MemoryManager()
    return _memory_manager

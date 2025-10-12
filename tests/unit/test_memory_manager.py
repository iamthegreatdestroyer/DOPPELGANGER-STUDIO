"""Unit tests for memory management system."""

import pytest
import asyncio
from src.services.optimization.memory_manager import (
    MemoryManager, ObjectPool, MemoryThresholds, get_memory_manager
)


class TestObject:
    """Test object for pooling."""
    def __init__(self):
        self.value = 0
    
    def reset(self):
        self.value = 0


class TestObjectPool:
    """Test object pool functionality."""
    
    def test_pool_creation(self):
        """Test object pool creation."""
        pool = ObjectPool(
            factory=lambda: TestObject(),
            reset=lambda obj: obj.reset(),
            max_size=10,
            min_size=2
        )
        
        assert pool._max_size == 10
        assert pool._min_size == 2
        assert len(pool._pool) == 2  # Pre-populated
    
    def test_acquire_release(self):
        """Test object acquire and release."""
        pool = ObjectPool(
            factory=lambda: TestObject(),
            max_size=5,
            min_size=1
        )
        
        # Acquire object
        obj1 = pool.acquire()
        assert obj1 is not None
        assert len(pool._in_use) == 1
        
        # Release object
        pool.release(obj1)
        assert len(pool._in_use) == 0
        assert len(pool._pool) >= 1
    
    def test_pool_reuse(self):
        """Test object reuse from pool."""
        pool = ObjectPool(
            factory=lambda: TestObject(),
            reset=lambda obj: obj.reset(),
            max_size=5,
            min_size=2
        )
        
        # Get and modify object
        obj1 = pool.acquire()
        obj1.value = 42
        pool.release(obj1)
        
        # Get object again - should be reset
        obj2 = pool.acquire()
        assert obj2.value == 0  # Reset was called
    
    def test_pool_cleanup(self):
        """Test pool cleanup."""
        pool = ObjectPool(
            factory=lambda: TestObject(),
            max_size=10,
            min_size=2
        )
        
        # Fill pool
        for _ in range(10):
            obj = pool.acquire()
            pool.release(obj)
        
        # Cleanup should reduce size
        pool.cleanup(aggressive=True)
        assert len(pool._pool) == pool._min_size


class TestMemoryManager:
    """Test memory manager functionality."""
    
    def test_manager_creation(self):
        """Test memory manager creation."""
        manager = MemoryManager()
        assert manager.thresholds is not None
        assert isinstance(manager._pools, dict)
    
    def test_create_pool(self):
        """Test pool creation through manager."""
        manager = MemoryManager()
        
        pool = manager.create_pool(
            name='test_pool',
            factory=lambda: TestObject(),
            max_size=5
        )
        
        assert pool is not None
        assert 'test_pool' in manager._pools
        assert manager.get_pool('test_pool') == pool
    
    def test_get_current_stats(self):
        """Test current stats retrieval."""
        manager = MemoryManager()
        stats = manager.get_current_stats()
        
        assert stats.timestamp is not None
        assert stats.total_memory > 0
        assert 0 <= stats.percent_used <= 100
        assert stats.process_memory > 0
    
    @pytest.mark.asyncio
    async def test_monitoring(self):
        """Test background monitoring."""
        manager = MemoryManager()
        
        await manager.start_monitoring(interval=0.1)
        await asyncio.sleep(0.5)
        
        assert len(manager._stats_history) > 0
        
        await manager.stop_monitoring()
    
    def test_force_gc(self):
        """Test garbage collection."""
        manager = MemoryManager()
        
        # Should not raise error
        manager.force_gc()
        manager.force_gc(generation=0)
        manager.force_gc(generation=1)
    
    def test_cleanup_pools(self):
        """Test pool cleanup."""
        manager = MemoryManager()
        
        # Create some pools
        pool1 = manager.create_pool('pool1', lambda: TestObject(), max_size=10)
        pool2 = manager.create_pool('pool2', lambda: TestObject(), max_size=10)
        
        # Fill pools
        for pool in [pool1, pool2]:
            for _ in range(10):
                obj = pool.acquire()
                pool.release(obj)
        
        # Cleanup should work
        manager.cleanup_pools()
        manager.cleanup_pools(aggressive=True)
    
    def test_memory_leak_detection(self):
        """Test memory leak detection."""
        manager = MemoryManager()
        
        # Not enough history - should return empty
        leaks = manager.detect_memory_leaks()
        assert leaks == []
        
        # Add some history
        for _ in range(30):
            stats = manager.get_current_stats()
            manager._stats_history.append(stats)
        
        # Should be able to run detection
        leaks = manager.detect_memory_leaks(threshold=10.0)
        assert isinstance(leaks, list)
    
    def test_global_instance(self):
        """Test global manager instance."""
        manager1 = get_memory_manager()
        manager2 = get_memory_manager()
        
        assert manager1 is manager2  # Same instance

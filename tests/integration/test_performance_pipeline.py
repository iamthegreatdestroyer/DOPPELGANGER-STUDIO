"""Integration tests for performance-optimized pipeline."""

import pytest
import asyncio
from src.services.optimization.memory_manager import get_memory_manager
from src.services.optimization.resource_monitor import ResourceMonitor


class TestPerformancePipeline:
    """Test integrated performance optimization."""
    
    @pytest.mark.asyncio
    async def test_memory_management_integration(self):
        """Test memory management in realistic pipeline."""
        manager = get_memory_manager()
        
        # Create pool for simulated heavy objects
        class HeavyObject:
            def __init__(self):
                self.data = [0] * 100000
            def reset(self):
                self.data = [0] * 100000
        
        pool = manager.create_pool(
            name='heavy_objects',
            factory=lambda: HeavyObject(),
            reset=lambda obj: obj.reset(),
            max_size=20
        )
        
        # Simulate workload
        for _ in range(50):
            obj = pool.acquire()
            await asyncio.sleep(0.01)
            pool.release(obj)
        
        # Check pool efficiency
        stats = pool.get_stats()
        assert stats['reused_total'] > 0
        assert stats['reuse_rate'] > 0.5
    
    @pytest.mark.asyncio
    async def test_resource_monitoring_integration(self):
        """Test resource monitoring during operations."""
        monitor = ResourceMonitor()
        
        await monitor.start_monitoring(interval=0.5)
        
        # Simulate work
        for _ in range(10):
            _ = sum(i ** 2 for i in range(100000))
            await asyncio.sleep(0.1)
        
        await monitor.stop_monitoring()
        
        # Check monitoring captured data
        summary = monitor.get_performance_summary()
        assert summary['samples'] > 0
        assert 'cpu_percent' in summary

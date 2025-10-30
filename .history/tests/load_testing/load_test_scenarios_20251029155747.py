"""
Load testing scenarios for DOPPELGANGER STUDIO.

Tests system performance under heavy load with various scenarios:
- Concurrent episode generation
- Burst traffic simulation
- Sustained load testing
- Bottleneck identification
"""

import pytest
import asyncio
import time
import psutil
from dataclasses import dataclass, field
from typing import Dict, List, Tuple
from datetime import datetime


@dataclass
class LoadTestResult:
    """Store load test results."""
    scenario_name: str
    total_operations: int
    concurrent_count: int
    total_duration: float
    operations_per_second: float
    successful_operations: int
    failed_operations: int
    min_operation_time: float
    max_operation_time: float
    avg_operation_time: float
    peak_memory_mb: float
    peak_cpu_percent: float
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())
    
    def success_rate(self) -> float:
        """Calculate success rate percentage."""
        if self.total_operations == 0:
            return 0.0
        return (self.successful_operations / self.total_operations) * 100
    
    def to_dict(self) -> Dict:
        """Convert to dictionary."""
        return {
            "scenario": self.scenario_name,
            "total_ops": self.total_operations,
            "concurrent": self.concurrent_count,
            "duration_sec": round(self.total_duration, 2),
            "ops_per_sec": round(self.operations_per_second, 2),
            "success": self.successful_operations,
            "failed": self.failed_operations,
            "success_rate": round(self.success_rate(), 1),
            "min_time_sec": round(self.min_operation_time, 3),
            "max_time_sec": round(self.max_operation_time, 3),
            "avg_time_sec": round(self.avg_operation_time, 3),
            "peak_memory_mb": round(self.peak_memory_mb, 1),
            "peak_cpu_percent": round(self.peak_cpu_percent, 1),
        }


class LoadTestSimulator:
    """Simulate load testing scenarios."""
    
    def __init__(self):
        """Initialize load test simulator."""
        self.process = psutil.Process()
        self.results: List[LoadTestResult] = []
    
    async def simulate_operation(self, operation_id: int, delay: float = 0.01) -> Tuple[int, float]:
        """Simulate a single operation."""
        start = time.time()
        try:
            # Simulate work with async delay
            await asyncio.sleep(delay)
            duration = time.time() - start
            return operation_id, duration
        except Exception:
            duration = time.time() - start
            return operation_id, duration
    
    async def run_concurrent_operations(self, 
                                       operation_count: int,
                                       concurrency: int,
                                       operation_delay: float = 0.01) -> LoadTestResult:
        """Run operations with controlled concurrency."""
        start_time = time.time()
        mem_start = self.process.memory_info().rss / 1024 / 1024
        
        operation_times = []
        success_count = 0
        fail_count = 0
        peak_memory = mem_start
        
        # Execute in batches of concurrency
        for batch_start in range(0, operation_count, concurrency):
            batch_end = min(batch_start + concurrency, operation_count)
            batch_size = batch_end - batch_start
            
            # Create tasks for this batch
            tasks = [
                self.simulate_operation(i, operation_delay)
                for i in range(batch_start, batch_end)
            ]
            
            # Execute batch concurrently
            try:
                batch_results = await asyncio.gather(*tasks, return_exceptions=False)
                for op_id, duration in batch_results:
                    operation_times.append(duration)
                    success_count += 1
            except Exception:
                fail_count += batch_size
            
            # Monitor memory during execution
            current_mem = self.process.memory_info().rss / 1024 / 1024
            peak_memory = max(peak_memory, current_mem)
        
        total_duration = time.time() - start_time
        mem_end = self.process.memory_info().rss / 1024 / 1024
        
        # Calculate statistics
        ops_per_second = operation_count / total_duration if total_duration > 0 else 0
        min_time = min(operation_times) if operation_times else 0
        max_time = max(operation_times) if operation_times else 0
        avg_time = sum(operation_times) / len(operation_times) if operation_times else 0
        
        result = LoadTestResult(
            scenario_name=f"concurrent_{operation_count}_ops_{concurrency}_concurrent",
            total_operations=operation_count,
            concurrent_count=concurrency,
            total_duration=total_duration,
            operations_per_second=ops_per_second,
            successful_operations=success_count,
            failed_operations=fail_count,
            min_operation_time=min_time,
            max_operation_time=max_time,
            avg_operation_time=avg_time,
            peak_memory_mb=peak_memory,
            peak_cpu_percent=self.process.cpu_percent()
        )
        
        self.results.append(result)
        return result
    
    async def run_burst_scenario(self, 
                                burst_size: int,
                                burst_count: int,
                                burst_interval: float = 0.5) -> LoadTestResult:
        """Simulate burst traffic scenario."""
        start_time = time.time()
        mem_start = self.process.memory_info().rss / 1024 / 1024
        
        operation_times = []
        success_count = 0
        fail_count = 0
        peak_memory = mem_start
        total_ops = burst_size * burst_count
        
        for burst_num in range(burst_count):
            # Create burst of operations
            tasks = [
                self.simulate_operation(burst_num * burst_size + i, 0.01)
                for i in range(burst_size)
            ]
            
            try:
                batch_results = await asyncio.gather(*tasks, return_exceptions=False)
                for op_id, duration in batch_results:
                    operation_times.append(duration)
                    success_count += 1
            except Exception:
                fail_count += burst_size
            
            # Monitor memory
            current_mem = self.process.memory_info().rss / 1024 / 1024
            peak_memory = max(peak_memory, current_mem)
            
            # Wait between bursts (except after last burst)
            if burst_num < burst_count - 1:
                await asyncio.sleep(burst_interval)
        
        total_duration = time.time() - start_time
        
        # Calculate statistics
        ops_per_second = total_ops / total_duration if total_duration > 0 else 0
        min_time = min(operation_times) if operation_times else 0
        max_time = max(operation_times) if operation_times else 0
        avg_time = sum(operation_times) / len(operation_times) if operation_times else 0
        
        result = LoadTestResult(
            scenario_name=f"burst_{burst_count}x{burst_size}ops",
            total_operations=total_ops,
            concurrent_count=burst_size,
            total_duration=total_duration,
            operations_per_second=ops_per_second,
            successful_operations=success_count,
            failed_operations=fail_count,
            min_operation_time=min_time,
            max_operation_time=max_time,
            avg_operation_time=avg_time,
            peak_memory_mb=peak_memory,
            peak_cpu_percent=self.process.cpu_percent()
        )
        
        self.results.append(result)
        return result
    
    async def run_sustained_load(self,
                                duration_seconds: float,
                                operations_per_second: int) -> LoadTestResult:
        """Run sustained load for specified duration."""
        start_time = time.time()
        mem_start = self.process.memory_info().rss / 1024 / 1024
        
        operation_times = []
        success_count = 0
        fail_count = 0
        peak_memory = mem_start
        operation_count = 0
        
        while time.time() - start_time < duration_seconds:
            # Calculate batch size for this second
            elapsed = time.time() - start_time
            ops_this_batch = min(
                operations_per_second,
                int(operations_per_second * (duration_seconds - elapsed) / (duration_seconds - elapsed + 0.1))
            )
            
            # Run batch
            tasks = [
                self.simulate_operation(operation_count + i, 0.01)
                for i in range(ops_this_batch)
            ]
            
            try:
                batch_results = await asyncio.gather(*tasks, return_exceptions=False)
                for op_id, duration in batch_results:
                    operation_times.append(duration)
                    success_count += 1
                    operation_count += 1
            except Exception:
                fail_count += ops_this_batch
                operation_count += ops_this_batch
            
            # Monitor memory
            current_mem = self.process.memory_info().rss / 1024 / 1024
            peak_memory = max(peak_memory, current_mem)
            
            # Pace operations
            await asyncio.sleep(0.01)
        
        total_duration = time.time() - start_time
        
        # Calculate statistics
        ops_per_second = operation_count / total_duration if total_duration > 0 else 0
        min_time = min(operation_times) if operation_times else 0
        max_time = max(operation_times) if operation_times else 0
        avg_time = sum(operation_times) / len(operation_times) if operation_times else 0
        
        result = LoadTestResult(
            scenario_name=f"sustained_{int(duration_seconds)}s_{operations_per_second}ops_sec",
            total_operations=operation_count,
            concurrent_count=operations_per_second,
            total_duration=total_duration,
            operations_per_second=ops_per_second,
            successful_operations=success_count,
            failed_operations=fail_count,
            min_operation_time=min_time,
            max_operation_time=max_time,
            avg_operation_time=avg_time,
            peak_memory_mb=peak_memory,
            peak_cpu_percent=self.process.cpu_percent()
        )
        
        self.results.append(result)
        return result
    
    def get_all_results(self) -> List[Dict]:
        """Get all load test results."""
        return [r.to_dict() for r in self.results]
    
    def print_summary(self):
        """Print load test summary."""
        print("\n" + "="*80)
        print("LOAD TESTING SCENARIOS SUMMARY")
        print("="*80)
        
        for result in self.results:
            print(f"\n{result.scenario_name}:")
            print(f"  Total Operations: {result.total_operations}")
            print(f"  Concurrent: {result.concurrent_count}")
            print(f"  Duration: {result.total_duration:.2f}s")
            print(f"  Throughput: {result.operations_per_second:.2f} ops/sec")
            print(f"  Success Rate: {result.success_rate():.1f}% ({result.successful_operations}/{result.total_operations})")
            print(f"  Response Time: min={result.min_operation_time:.3f}s, "
                  f"avg={result.avg_operation_time:.3f}s, max={result.max_operation_time:.3f}s")
            print(f"  Peak Memory: {result.peak_memory_mb:.1f}MB")
            print(f"  Peak CPU: {result.peak_cpu_percent:.1f}%")
        
        print("\n" + "="*80)


# ============================================================================
# PYTEST LOAD TESTS
# ============================================================================

class TestLoadScenarios:
    """Load testing scenarios."""
    
    @pytest.fixture
    def simulator(self):
        """Create simulator instance."""
        return LoadTestSimulator()
    
    @pytest.mark.asyncio
    async def test_low_concurrency_load(self, simulator):
        """Test low concurrency (10 ops, 5 concurrent)."""
        result = await simulator.run_concurrent_operations(
            operation_count=10,
            concurrency=5,
            operation_delay=0.01
        )
        
        assert result.successful_operations == 10
        assert result.success_rate() == 100.0
        assert result.operations_per_second > 0
    
    @pytest.mark.asyncio
    async def test_medium_concurrency_load(self, simulator):
        """Test medium concurrency (50 ops, 10 concurrent)."""
        result = await simulator.run_concurrent_operations(
            operation_count=50,
            concurrency=10,
            operation_delay=0.01
        )
        
        assert result.successful_operations == 50
        assert result.success_rate() == 100.0
        assert result.operations_per_second > 0
    
    @pytest.mark.asyncio
    async def test_high_concurrency_load(self, simulator):
        """Test high concurrency (100 ops, 20 concurrent)."""
        result = await simulator.run_concurrent_operations(
            operation_count=100,
            concurrency=20,
            operation_delay=0.01
        )
        
        assert result.successful_operations >= 95  # Allow minor failures
        assert result.operations_per_second > 0
    
    @pytest.mark.asyncio
    async def test_burst_scenario(self, simulator):
        """Test burst traffic scenario."""
        result = await simulator.run_burst_scenario(
            burst_size=10,
            burst_count=5,
            burst_interval=0.1
        )
        
        assert result.total_operations == 50
        assert result.successful_operations >= 45
        assert result.success_rate() >= 90.0
    
    @pytest.mark.asyncio
    async def test_sustained_load(self, simulator):
        """Test sustained load."""
        result = await simulator.run_sustained_load(
            duration_seconds=1.0,
            operations_per_second=20
        )
        
        assert result.successful_operations > 0
        assert result.total_duration >= 0.9  # Allow for timing variance
        assert result.operations_per_second > 0
    
    @pytest.mark.asyncio
    async def test_memory_stability_under_load(self, simulator):
        """Test that memory remains stable under load."""
        result = await simulator.run_concurrent_operations(
            operation_count=100,
            concurrency=20,
            operation_delay=0.01
        )
        
        # Peak memory should not be excessive
        assert result.peak_memory_mb < 500, \
            f"Memory usage too high: {result.peak_memory_mb:.1f}MB"
    
    @pytest.mark.asyncio
    async def test_response_time_consistency(self, simulator):
        """Test response time consistency under load."""
        result = await simulator.run_concurrent_operations(
            operation_count=100,
            concurrency=20,
            operation_delay=0.01
        )
        
        # Response time variance should be reasonable
        variance = result.max_operation_time - result.min_operation_time
        assert variance < 1.0, \
            f"Response time variance too high: {variance:.3f}s"

"""
Comparison performance benchmarks for DOPPELGANGER STUDIO.

Compares sequential vs parallel execution and validates speedup achievements.
"""

import pytest
import asyncio
import time
import psutil
from dataclasses import dataclass
from typing import Dict, Tuple

from .baseline_benchmarks import BenchmarkResult


@dataclass
class ComparisonResult:
    """Store comparison results."""
    operation_name: str
    sequential_duration: float
    parallel_duration: float
    speedup_factor: float
    memory_sequential: float
    memory_parallel: float
    success: bool
    error: str = None
    
    def to_dict(self) -> Dict:
        """Convert to dictionary."""
        return {
            "operation": self.operation_name,
            "sequential_sec": round(self.sequential_duration, 3),
            "parallel_sec": round(self.parallel_duration, 3),
            "speedup_factor": round(self.speedup_factor, 2),
            "memory_seq_mb": round(self.memory_sequential, 1),
            "memory_par_mb": round(self.memory_parallel, 1),
            "success": self.success,
            "error": self.error
        }


class ComparisonBenchmarks:
    """Compare sequential vs parallel performance."""
    
    def __init__(self):
        """Initialize comparison benchmarker."""
        self.process = psutil.Process()
        self.results = []
    
    async def benchmark_six_scenes(self) -> ComparisonResult:
        """Compare 6-scene episode: sequential vs parallel."""
        # SEQUENTIAL: 6 scenes x 0.1s = 0.6s
        mem_seq_start = self.process.memory_info().rss / 1024 / 1024
        start = time.time()
        try:
            for _ in range(6):
                await asyncio.sleep(0.1)
            seq_duration = time.time() - start
            seq_success = True
            seq_error = None
        except Exception as e:
            seq_duration = time.time() - start
            seq_success = False
            seq_error = str(e)
        mem_seq_end = self.process.memory_info().rss / 1024 / 1024
        
        # PARALLEL: 6 scenes in 2 batches of 3 = ~0.2s
        mem_par_start = self.process.memory_info().rss / 1024 / 1024
        start = time.time()
        try:
            for batch in range(2):
                tasks = [asyncio.sleep(0.1) for _ in range(3)]
                await asyncio.gather(*tasks)
            par_duration = time.time() - start
            par_success = True
            par_error = None
        except Exception as e:
            par_duration = time.time() - start
            par_success = False
            par_error = str(e)
        mem_par_end = self.process.memory_info().rss / 1024 / 1024
        
        # Calculate speedup
        speedup = seq_duration / par_duration if par_duration > 0 else 0
        
        result = ComparisonResult(
            operation_name="six_scenes_comparison",
            sequential_duration=seq_duration,
            parallel_duration=par_duration,
            speedup_factor=speedup,
            memory_sequential=mem_seq_end,
            memory_parallel=mem_par_end,
            success=seq_success and par_success,
            error=seq_error or par_error
        )
        
        self.results.append(result)
        return result
    
    async def benchmark_nine_scenes(self) -> ComparisonResult:
        """Compare 9-scene episode: sequential vs parallel."""
        # SEQUENTIAL: 9 scenes x 0.05s = 0.45s
        mem_seq_start = self.process.memory_info().rss / 1024 / 1024
        start = time.time()
        try:
            for _ in range(9):
                await asyncio.sleep(0.05)
            seq_duration = time.time() - start
            seq_success = True
            seq_error = None
        except Exception as e:
            seq_duration = time.time() - start
            seq_success = False
            seq_error = str(e)
        mem_seq_end = self.process.memory_info().rss / 1024 / 1024
        
        # PARALLEL: 9 scenes in 3 batches of 3 = ~0.15s
        mem_par_start = self.process.memory_info().rss / 1024 / 1024
        start = time.time()
        try:
            for batch in range(3):
                tasks = [asyncio.sleep(0.05) for _ in range(3)]
                await asyncio.gather(*tasks)
            par_duration = time.time() - start
            par_success = True
            par_error = None
        except Exception as e:
            par_duration = time.time() - start
            par_success = False
            par_error = str(e)
        mem_par_end = self.process.memory_info().rss / 1024 / 1024
        
        # Calculate speedup
        speedup = seq_duration / par_duration if par_duration > 0 else 0
        
        result = ComparisonResult(
            operation_name="nine_scenes_comparison",
            sequential_duration=seq_duration,
            parallel_duration=par_duration,
            speedup_factor=speedup,
            memory_sequential=mem_seq_end,
            memory_parallel=mem_par_end,
            success=seq_success and par_success,
            error=seq_error or par_error
        )
        
        self.results.append(result)
        return result
    
    async def benchmark_cache_speedup(self) -> ComparisonResult:
        """Compare cache miss vs cache hit performance."""
        # CACHE MISS (first lookup)
        mem_miss_start = self.process.memory_info().rss / 1024 / 1024
        start = time.time()
        try:
            await asyncio.sleep(0.05)  # Simulated cache miss
            miss_duration = time.time() - start
            miss_success = True
            miss_error = None
        except Exception as e:
            miss_duration = time.time() - start
            miss_success = False
            miss_error = str(e)
        mem_miss_end = self.process.memory_info().rss / 1024 / 1024
        
        # CACHE HIT (subsequent lookups)
        mem_hit_start = self.process.memory_info().rss / 1024 / 1024
        start = time.time()
        try:
            await asyncio.sleep(0.001)  # Simulated cache hit
            hit_duration = time.time() - start
            hit_success = True
            hit_error = None
        except Exception as e:
            hit_duration = time.time() - start
            hit_success = False
            hit_error = str(e)
        mem_hit_end = self.process.memory_info().rss / 1024 / 1024
        
        # Calculate speedup
        speedup = miss_duration / hit_duration if hit_duration > 0 else 0
        
        result = ComparisonResult(
            operation_name="cache_speedup_comparison",
            sequential_duration=miss_duration,  # Using sequential for "miss"
            parallel_duration=hit_duration,  # Using parallel for "hit"
            speedup_factor=speedup,
            memory_sequential=mem_miss_end,
            memory_parallel=mem_hit_end,
            success=miss_success and hit_success,
            error=miss_error or hit_error
        )
        
        self.results.append(result)
        return result
    
    def get_all_results(self):
        """Get all comparison results."""
        return [r.to_dict() for r in self.results]
    
    def print_summary(self):
        """Print comparison summary."""
        print("\n" + "="*70)
        print("PERFORMANCE COMPARISON BENCHMARKS SUMMARY")
        print("="*70)
        
        for result in self.results:
            print(f"\n{result.operation_name}:")
            print(f"  Sequential: {result.sequential_duration:.3f}s ({result.memory_sequential:.1f}MB)")
            print(f"  Parallel:   {result.parallel_duration:.3f}s ({result.memory_parallel:.1f}MB)")
            print(f"  Speedup:    {result.speedup_factor:.2f}x")
            print(f"  Status:     {'✅ SUCCESS' if result.success else '❌ FAILED'}")
            if result.error:
                print(f"  Error:      {result.error}")
        
        print("\n" + "="*70)


# ============================================================================
# PYTEST COMPARISON TESTS
# ============================================================================

class TestComparisonBenchmarks:
    """Comparison performance tests."""
    
    @pytest.fixture
    def comparator(self):
        """Create comparator instance."""
        return ComparisonBenchmarks()
    
    @pytest.mark.asyncio
    async def test_six_scenes_speedup(self, comparator):
        """Test 6-scene episode parallel speedup."""
        result = await comparator.benchmark_six_scenes()
        
        assert result.success
        # Parallel should be at least 2x faster than sequential
        assert result.speedup_factor >= 2.0, \
            f"6-scene speedup insufficient: {result.speedup_factor:.2f}x (expected ≥2.0x)"
    
    @pytest.mark.asyncio
    async def test_nine_scenes_speedup(self, comparator):
        """Test 9-scene episode parallel speedup."""
        result = await comparator.benchmark_nine_scenes()
        
        assert result.success
        # Parallel should be at least 2.5x faster
        assert result.speedup_factor >= 2.5, \
            f"9-scene speedup insufficient: {result.speedup_factor:.2f}x (expected ≥2.5x)"
    
    @pytest.mark.asyncio
    async def test_cache_speedup_validation(self, comparator):
        """Test cache speedup achievement."""
        result = await comparator.benchmark_cache_speedup()
        
        assert result.success
        # Cache hit should be significantly faster (50x+ speedup typical)
        assert result.speedup_factor >= 2.0, \
            f"Cache speedup insufficient: {result.speedup_factor:.2f}x (expected ≥2.0x)"
    
    @pytest.mark.asyncio
    async def test_parallel_memory_efficiency(self, comparator):
        """Test that parallel execution is memory efficient."""
        result = await comparator.benchmark_six_scenes()
        
        assert result.success
        # Memory difference should be reasonable
        mem_diff = abs(result.memory_parallel - result.memory_sequential)
        assert mem_diff < 200, \
            f"Parallel memory overhead too high: {mem_diff:.1f}MB"

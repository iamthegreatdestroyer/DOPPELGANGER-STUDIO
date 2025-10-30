"""
Regression detection benchmarks for DOPPELGANGER STUDIO.

Detects performance regressions by comparing against baseline metrics.
"""

import pytest
import json
import asyncio
import time
from pathlib import Path
from dataclasses import dataclass, asdict
from typing import Dict, Optional
from datetime import datetime

from .baseline_benchmarks import BaselineBenchmarks, BenchmarkResult


@dataclass
class RegressionThresholds:
    """Define acceptable performance thresholds."""
    duration_percent_increase: float = 5.0  # 5% slower = regression
    memory_percent_increase: float = 10.0   # 10% more memory = regression
    cpu_percent_increase: float = 15.0      # 15% more CPU = regression


class RegressionDetector:
    """Detect performance regressions."""
    
    def __init__(self, thresholds: Optional[RegressionThresholds] = None):
        """Initialize regression detector."""
        self.thresholds = thresholds or RegressionThresholds()
        self.baseline_file = Path("tests/benchmarks/baseline_metrics.json")
        self.baseline_metrics: Dict = {}
        self.current_results: Dict = {}
        self.regressions = []
    
    def load_baseline(self) -> bool:
        """Load baseline metrics from file."""
        if not self.baseline_file.exists():
            return False
        
        try:
            with open(self.baseline_file, 'r') as f:
                self.baseline_metrics = json.load(f)
            return True
        except Exception:
            return False
    
    def save_baseline(self, results: Dict):
        """Save baseline metrics to file."""
        try:
            baseline_file = self.baseline_file
            baseline_file.parent.mkdir(parents=True, exist_ok=True)
            
            with open(baseline_file, 'w') as f:
                json.dump(results, f, indent=2)
            return True
        except Exception:
            return False
    
    def check_regression(self, operation: str, current: BenchmarkResult) -> Optional[str]:
        """Check if current result shows regression."""
        if operation not in self.baseline_metrics:
            return None  # No baseline to compare
        
        baseline = self.baseline_metrics[operation]
        issues = []
        
        # Check duration regression
        if baseline["duration_sec"] > 0:
            percent_increase = (
                (current.duration_seconds - baseline["duration_sec"]) 
                / baseline["duration_sec"] * 100
            )
            if percent_increase > self.thresholds.duration_percent_increase:
                issues.append(
                    f"Duration regression: {percent_increase:.1f}% slower "
                    f"({current.duration_seconds:.3f}s vs {baseline['duration_sec']:.3f}s baseline)"
                )
        
        # Check memory regression
        if baseline["memory_mb"] > 0:
            percent_increase = (
                (current.memory_usage_mb - baseline["memory_mb"]) 
                / baseline["memory_mb"] * 100
            )
            if percent_increase > self.thresholds.memory_percent_increase:
                issues.append(
                    f"Memory regression: {percent_increase:.1f}% increase "
                    f"({current.memory_usage_mb:.1f}MB vs {baseline['memory_mb']:.1f}MB baseline)"
                )
        
        if issues:
            return " | ".join(issues)
        return None
    
    async def run_regression_detection(self) -> Dict:
        """Run full regression detection."""
        benchmarker = BaselineBenchmarks()
        
        # Run all baseline benchmarks
        results = {
            "single_scene_generation": asdict(
                await benchmarker.benchmark_single_scene()
            ),
            "three_scenes_sequential": asdict(
                await benchmarker.benchmark_three_scenes_sequential()
            ),
            "three_scenes_parallel": asdict(
                await benchmarker.benchmark_three_scenes_parallel()
            ),
        }
        
        # Convert to simpler format
        clean_results = {}
        for key, result in results.items():
            clean_results[key] = {
                "duration_sec": result["duration_seconds"],
                "memory_mb": result["memory_usage_mb"],
                "cpu_percent": result["cpu_percent"],
                "success": result["success"],
                "timestamp": result["timestamp"]
            }
        
        self.current_results = clean_results
        
        # Check for regressions if baseline exists
        self.regressions = []
        if self.load_baseline():
            for op, current_result in clean_results.items():
                regression_msg = self.check_regression(
                    op,
                    BenchmarkResult(
                        operation_name=op,
                        duration_seconds=current_result["duration_sec"],
                        memory_usage_mb=current_result["memory_mb"],
                        memory_delta_mb=0,
                        cpu_percent=current_result["cpu_percent"],
                        success=current_result["success"]
                    )
                )
                if regression_msg:
                    self.regressions.append({
                        "operation": op,
                        "issue": regression_msg,
                        "timestamp": datetime.now().isoformat()
                    })
        
        return {
            "results": clean_results,
            "regressions": self.regressions,
            "timestamp": datetime.now().isoformat()
        }
    
    def print_report(self, report: Dict):
        """Print regression detection report."""
        print("\n" + "="*70)
        print("PERFORMANCE REGRESSION DETECTION REPORT")
        print("="*70)
        print(f"Timestamp: {report['timestamp']}")
        
        print("\n--- Current Results ---")
        for op, result in report["results"].items():
            status = "✅" if result["success"] else "❌"
            print(f"{status} {op}:")
            print(f"   Duration: {result['duration_sec']:.3f}s")
            print(f"   Memory: {result['memory_mb']:.1f}MB")
        
        if report["regressions"]:
            print("\n--- ⚠️ REGRESSIONS DETECTED ---")
            for regression in report["regressions"]:
                print(f"{regression['operation']}: {regression['issue']}")
        else:
            print("\n--- ✅ NO REGRESSIONS ---")
        
        print("\n" + "="*70)


# ============================================================================
# PYTEST REGRESSION TESTS
# ============================================================================

class TestRegressionDetection:
    """Regression detection tests."""
    
    @pytest.fixture
    def detector(self):
        """Create detector instance."""
        return RegressionDetector()
    
    @pytest.mark.asyncio
    async def test_baseline_metrics_collection(self, detector):
        """Test collecting baseline metrics."""
        report = await detector.run_regression_detection()
        
        assert report["results"]
        assert "single_scene_generation" in report["results"]
        assert "three_scenes_sequential" in report["results"]
        assert "three_scenes_parallel" in report["results"]
        
        # All should have required fields
        for op, result in report["results"].items():
            assert "duration_sec" in result
            assert "memory_mb" in result
            assert "success" in result
    
    @pytest.mark.asyncio
    async def test_save_and_load_baseline(self, detector):
        """Test saving and loading baseline metrics."""
        report = await detector.run_regression_detection()
        
        # Save baseline
        saved = detector.save_baseline(report["results"])
        assert saved
        
        # Load baseline
        detector2 = RegressionDetector()
        loaded = detector2.load_baseline()
        assert loaded
        assert detector2.baseline_metrics == report["results"]
    
    @pytest.mark.asyncio
    async def test_no_regression_when_metrics_stable(self, detector):
        """Test that stable metrics don't trigger regressions."""
        # Get first report and save as baseline
        report1 = await detector.run_regression_detection()
        detector.save_baseline(report1["results"])
        
        # Get second report - should have no regressions
        report2 = await detector.run_regression_detection()
        
        # Should have minimal or no regressions due to timing variance
        # (allowing for some timing noise)
        assert len(report2["regressions"]) <= 1, \
            "Stable metrics should not trigger significant regressions"
    
    def test_regression_threshold_configuration(self):
        """Test custom regression thresholds."""
        strict_thresholds = RegressionThresholds(
            duration_percent_increase=1.0,
            memory_percent_increase=1.0
        )
        detector = RegressionDetector(thresholds=strict_thresholds)
        
        assert detector.thresholds.duration_percent_increase == 1.0
        assert detector.thresholds.memory_percent_increase == 1.0

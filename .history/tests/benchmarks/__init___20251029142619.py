"""
Copyright (c) 2025 DOPPELGANGER STUDIO. All Rights Reserved.

Performance benchmarking suite for DOPPELGANGER STUDIO.

This package contains benchmarks for:
- Baseline performance metrics
- Performance regression detection
- Parallel vs sequential execution comparison
- Memory profiling
- API performance tracking
"""

__version__ = "1.0.0"
__author__ = "DOPPELGANGER STUDIO Team"

from .baseline_benchmarks import *
# from .comparison_benchmarks import *  # Will be added in next phase

__all__ = [
    "baseline_benchmarks",
    # "comparison_benchmarks",  # Will be added in next phase
]

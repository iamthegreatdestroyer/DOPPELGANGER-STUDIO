"""
Copyright (c) 2025 DOPPELGANGER STUDIO. All Rights Reserved.

Load testing suite for DOPPELGANGER STUDIO.

This package contains load testing scenarios for:
- Concurrent episode generation
- Burst traffic simulation
- Sustained load testing
- Bottleneck identification
- Resource utilization analysis
"""

__version__ = "1.0.0"
__author__ = "DOPPELGANGER STUDIO Team"

from .load_test_scenarios import *

__all__ = [
    "load_test_scenarios",
]

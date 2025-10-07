#!/usr/bin/env python3
"""Temporary script to fix OptimizedScriptComedy instances."""

import re

filepath = r'tests\unit\test_script_validator.py'
content = open(filepath, 'r', encoding='utf-8').read()

# Add missing fields after analyzed_jokes
pattern = r'(OptimizedScriptComedy\(\s+script_id="test",\s+analyzed_jokes=[^\)]+,)\s+(timing_analysis=)'
replacement = r'\1\n            alternative_punchlines=[],\n            callback_opportunities=[],\n            \2'
content = re.sub(pattern, replacement, content)

# Add optimization_summary after overall_effectiveness
pattern2 = r'(overall_effectiveness=0\.\d+,)(\s+confidence_score)'
replacement2 = r'\1\n            optimization_summary="Test comedy analysis",\2'
content = re.sub(pattern2, replacement2, content)

open(filepath, 'w', encoding='utf-8').write(content)
print("Fixed OptimizedScriptComedy instances")

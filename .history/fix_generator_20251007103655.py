#!/usr/bin/env python3
"""Fix test_script_generator issues."""

filepath = r'tests\unit\test_script_generator.py'
content = open(filepath, 'r', encoding='utf-8').read()

# Fix timing_category
content = content.replace('timing_category="well-spaced"', 'timing_category=JokeTiming.WELL_SPACED')

# Restore time_of_day fields
content = content.replace('# time_of_day removed, was: "Day",', 'time_of_day="Day",')
content = content.replace('# time_of_day removed, was: "Night",', 'time_of_day="Night",')
content = content.replace('# time_of_day removed, was: "Evening",', 'time_of_day="Evening",')

# Fix runtime type
content = content.replace('total_runtime_estimate=30.0,', 'total_runtime_estimate=30,')

open(filepath, 'w', encoding='utf-8').write(content)
print("Fixed all issues")

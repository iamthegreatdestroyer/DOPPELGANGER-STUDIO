import pytest
import importlib.util

# If the low-level audio backend is missing (Python >=3.13 removed audioop),
# skip this directory's tests at collection time.
if not (importlib.util.find_spec("audioop") or importlib.util.find_spec("pyaudioop")):
    pytest.skip("audio backend unavailable; skipping audio tests", allow_module_level=True)

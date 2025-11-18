import os
import sys
import importlib.util
from pathlib import Path

# Ensure main src takes precedence over phase2 src when importing `src.*`
ROOT = Path(__file__).resolve().parent
SRC_MAIN = str(ROOT / "src")
SRC_PHASE2 = str(ROOT / "doppelganger-studio-phase2" / "src")

# Remove any pre-existing entries to control order deterministically
for p in [SRC_MAIN, SRC_PHASE2]:
    try:
        while p in sys.path:
            sys.path.remove(p)
    except Exception:
        pass

# Insert main src first, then phase2 src as fallback
sys.path.insert(0, SRC_MAIN)
sys.path.append(SRC_PHASE2)

# Conditionally skip audio tests on Python 3.13+ without audioop
AUDIO_OK = bool(
    importlib.util.find_spec("audioop")
    or importlib.util.find_spec("pyaudioop")
)


def pytest_ignore_collect(collection_path, config):
    """
    Limit collection to project tests; skip third-party libs.

    Also skips audio tests if audio backend is unavailable.
    """
    p = str(collection_path)

    # Skip anything under .venv, .history, doppelganger-studio-phase2
    skip_prefixes = (
        str(ROOT / ".venv"),
        str(ROOT / ".history"),
        str(ROOT / "doppelganger-studio-phase2"),
    )
    if any(p.startswith(prefix) for prefix in skip_prefixes):
        return True

    # Skip audio tests if backend missing
    if not AUDIO_OK:
        if os.sep + "tests" + os.sep + "audio" + os.sep in p:
            return True
        filename = os.path.basename(p)
        patterns = ("test_audio_", "test_tts_")
        if any(filename.startswith(pref) for pref in patterns):
            return True

    return False

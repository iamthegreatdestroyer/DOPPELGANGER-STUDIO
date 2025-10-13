"""
Tests for SFX Library System.

Copyright (c) 2025. All Rights Reserved. Patent Pending.
"""

import pytest
from pathlib import Path
import tempfile
import shutil
from pydub import AudioSegment
from pydub.generators import Sine

from src.services.audio.sfx.library import SFXLibrary, SoundEffect


@pytest.fixture
def temp_library():
    """Create temporary SFX library."""
    temp_dir = tempfile.mkdtemp()
    library = SFXLibrary(temp_dir)
    yield library
    shutil.rmtree(temp_dir)


@pytest.fixture
def sample_audio(temp_library):
    """Create sample audio file."""
    audio = Sine(1000).to_audio_segment(duration=500)  # 0.5s beep
    
    audio_path = Path(temp_library.library_path) / "test_effect.wav"
    audio.export(audio_path, format="wav")
    
    return audio_path


class TestSFXLibrary:
    """Test SFX library management."""
    
    def test_library_initialization(self, temp_library):
        """Test library initializes correctly."""
        assert temp_library.library_path.exists()
        assert len(temp_library.effects) == 0
    
    @pytest.mark.asyncio
    async def test_import_effect(self, temp_library, sample_audio):
        """Test importing a sound effect."""
        effect = await temp_library.import_effect(
            sample_audio,
            category="actions",
            name="Door Close",
            tags=["door", "close"]
        )
        
        assert effect.name == "Door Close"
        assert effect.category == "actions"
        assert "door" in effect.tags
        assert effect.duration > 0
    
    @pytest.mark.asyncio
    async def test_invalid_category(self, temp_library, sample_audio):
        """Test importing with invalid category raises error."""
        with pytest.raises(ValueError):
            await temp_library.import_effect(
                sample_audio,
                category="invalid_category"
            )
    
    @pytest.mark.asyncio
    async def test_search_by_category(self, temp_library, sample_audio):
        """Test searching effects by category."""
        await temp_library.import_effect(
            sample_audio,
            category="actions"
        )
        
        results = temp_library.search(category="actions")
        assert len(results) == 1
        assert results[0].category == "actions"
    
    @pytest.mark.asyncio
    async def test_search_by_tags(self, temp_library, sample_audio):
        """Test searching effects by tags."""
        await temp_library.import_effect(
            sample_audio,
            category="actions",
            tags=["door", "slam"]
        )
        
        results = temp_library.search(tags=["door"])
        assert len(results) == 1
    
    def test_get_stats(self, temp_library):
        """Test library statistics."""
        stats = temp_library.get_stats()
        
        assert 'total_effects' in stats
        assert 'categories' in stats
        assert stats['total_effects'] == 0

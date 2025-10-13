"""
Tests for Music Library System.

Copyright (c) 2025. All Rights Reserved. Patent Pending.
"""

import pytest
from pathlib import Path
import tempfile
import shutil
from pydub import AudioSegment
from pydub.generators import Sine

from src.services.audio.music.library import MusicLibrary, MusicTrack


@pytest.fixture
def temp_library():
    """Create temporary music library."""
    temp_dir = tempfile.mkdtemp()
    library = MusicLibrary(temp_dir)
    yield library
    shutil.rmtree(temp_dir)


@pytest.fixture
def sample_audio(temp_library):
    """Create sample audio file."""
    # Generate 5 second sine wave
    audio = Sine(440).to_audio_segment(duration=5000)
    
    audio_path = Path(temp_library.library_path) / "test_track.mp3"
    audio.export(audio_path, format="mp3")
    
    return audio_path


class TestMusicLibrary:
    """Test music library management."""
    
    def test_library_initialization(self, temp_library):
        """Test library initializes correctly."""
        assert temp_library.library_path.exists()
        assert len(temp_library.tracks) == 0
    
    @pytest.mark.asyncio
    async def test_import_track(self, temp_library, sample_audio):
        """Test importing a music track."""
        track = await temp_library.import_track(
            sample_audio,
            title="Test Track",
            genre=["test"],
            mood=["happy"],
            energy_level=5
        )
        
        assert track.title == "Test Track"
        assert "test" in track.genre
        assert "happy" in track.mood
        assert track.energy_level == 5
        assert track.duration > 0
    
    @pytest.mark.asyncio
    async def test_search_by_mood(self, temp_library, sample_audio):
        """Test searching tracks by mood."""
        await temp_library.import_track(
            sample_audio,
            mood=["happy"]
        )
        
        results = temp_library.search(mood="happy")
        assert len(results) == 1
        assert "happy" in results[0].mood
    
    @pytest.mark.asyncio
    async def test_search_by_energy(self, temp_library, sample_audio):
        """Test searching tracks by energy level."""
        await temp_library.import_track(
            sample_audio,
            energy_level=8
        )
        
        results = temp_library.search(min_energy=7, max_energy=10)
        assert len(results) == 1
    
    def test_get_stats(self, temp_library):
        """Test library statistics."""
        stats = temp_library.get_stats()
        
        assert 'total_tracks' in stats
        assert 'total_duration' in stats
        assert stats['total_tracks'] == 0

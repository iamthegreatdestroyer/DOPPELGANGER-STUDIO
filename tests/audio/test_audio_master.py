"""
Tests for Audio Mastering.

Copyright (c) 2025. All Rights Reserved. Patent Pending.
"""

import pytest
from pydub import AudioSegment
from pydub.generators import Sine

from src.services.audio.mixing.mastering import AudioMaster


@pytest.fixture
def sample_audio():
    """Create sample audio."""
    return Sine(440).to_audio_segment(duration=3000)


@pytest.fixture
def master():
    """Create audio master instance."""
    return AudioMaster()


class TestAudioMaster:
    """Test audio mastering functionality."""
    
    @pytest.mark.asyncio
    async def test_master_audio(self, master, sample_audio):
        """Test basic audio mastering."""
        mastered = await master.master_audio(sample_audio)
        
        assert len(mastered) == len(sample_audio)
        assert mastered.channels == sample_audio.channels
    
    def test_get_levels(self, master, sample_audio):
        """Test getting audio levels."""
        levels = master.get_levels(sample_audio)
        
        assert 'peak_db' in levels
        assert 'rms_db' in levels
        assert 'duration_seconds' in levels
    
    def test_broadcast_standards(self, master, sample_audio):
        """Test broadcast standards checking."""
        checks = master.meets_broadcast_standards(sample_audio)
        
        assert 'peak_ok' in checks
        assert 'rms_ok' in checks
        assert 'all_ok' in checks
    
    @pytest.mark.asyncio
    async def test_platform_mastering(self, master, sample_audio):
        """Test platform-specific mastering."""
        platforms = ['youtube', 'spotify', 'broadcast']
        
        for platform in platforms:
            mastered = await master.master_for_platform(
                sample_audio,
                platform=platform
            )
            assert mastered is not None

"""
Tests for Audio Mixer.

Copyright (c) 2025. All Rights Reserved. Patent Pending.
"""

import pytest
from pydub import AudioSegment
from pydub.generators import Sine

from src.services.audio.mixing.mixer import AudioMixer


@pytest.fixture
def sample_dialogue():
    """Create sample dialogue audio."""
    return Sine(440).to_audio_segment(duration=3000)


@pytest.fixture
def sample_music():
    """Create sample music audio."""
    return Sine(220).to_audio_segment(duration=3000)


@pytest.fixture
def mixer():
    """Create audio mixer instance."""
    return AudioMixer()


class TestAudioMixer:
    """Test audio mixing functionality."""
    
    @pytest.mark.asyncio
    async def test_mix_dialogue_only(self, mixer, sample_dialogue):
        """Test mixing dialogue only."""
        mixed = await mixer.mix_tracks(dialogue=sample_dialogue)
        
        assert len(mixed) == len(sample_dialogue)
        assert mixed.channels == sample_dialogue.channels
    
    @pytest.mark.asyncio
    async def test_mix_dialogue_and_music(self, mixer, sample_dialogue, sample_music):
        """Test mixing dialogue with music."""
        mixed = await mixer.mix_tracks(
            dialogue=sample_dialogue,
            music=sample_music
        )
        
        assert len(mixed) == len(sample_dialogue)
    
    @pytest.mark.asyncio
    async def test_mix_with_custom_levels(self, mixer, sample_dialogue, sample_music):
        """Test mixing with custom levels."""
        custom_levels = {
            'dialogue': -5,
            'music': -20
        }
        
        mixed = await mixer.mix_tracks(
            dialogue=sample_dialogue,
            music=sample_music,
            custom_levels=custom_levels
        )
        
        assert mixed is not None
    
    @pytest.mark.asyncio
    async def test_simple_mix(self, mixer, sample_dialogue, sample_music):
        """Test simple two-track mix."""
        mixed = await mixer.mix_simple(
            dialogue=sample_dialogue,
            music=sample_music
        )
        
        assert len(mixed) == len(sample_dialogue)

"""
Unit tests for audio generator.

Copyright (c) 2025. All Rights Reserved. Patent Pending.
"""

import pytest
from pathlib import Path
from unittest.mock import Mock, AsyncMock

from src.services.voiceover.audio_generator import (
    AudioGenerator,
    DialogueLine,
    AudioFile
)
from src.models.voice_profile import VoiceProfile
from src.services.voiceover.tts_engine import TTSResult


@pytest.fixture
def mock_tts_engine():
    """Mock TTS engine."""
    engine = Mock()
    engine.generate_speech = AsyncMock(return_value=TTSResult(
        success=True,
        audio_path=Path("test.mp3"),
        duration=2.0,
        cost=0.01
    ))
    return engine


@pytest.fixture
def voice_profiles():
    """Test voice profiles."""
    return {
        "Lucy": VoiceProfile(
            character_name="Lucy",
            voice_id="rachel",
            engine="elevenlabs"
        )
    }


@pytest.mark.asyncio
async def test_dialogue_line_creation():
    """Test DialogueLine creation."""
    line = DialogueLine(
        character="Lucy",
        text="Hello!",
        scene_id="scene1",
        line_number=1
    )
    
    assert line.character == "Lucy"
    assert line.text == "Hello!"


@pytest.mark.asyncio
async def test_audio_generation(mock_tts_engine, voice_profiles, tmp_path):
    """Test audio generation."""
    generator = AudioGenerator(
        tts_engine=mock_tts_engine,
        voice_profiles=voice_profiles,
        output_dir=tmp_path
    )
    
    lines = [
        DialogueLine(
            character="Lucy",
            text="Hello world!",
            scene_id="scene1",
            line_number=1
        )
    ]
    
    audio_files = await generator.generate_dialogue(lines)
    
    assert len(audio_files) == 1
    assert audio_files[0].cost == 0.01

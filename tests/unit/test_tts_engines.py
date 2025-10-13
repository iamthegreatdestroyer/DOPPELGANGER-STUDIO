"""
Unit tests for TTS engines.

Copyright (c) 2025. All Rights Reserved. Patent Pending.
"""

import pytest
from pathlib import Path
from unittest.mock import Mock, AsyncMock, patch

from src.services.voiceover.tts_engine import TTSEngine, TTSResult
from src.services.voiceover.elevenlabs_client import ElevenLabsClient


@pytest.fixture
def mock_elevenlabs_response():
    """Mock ElevenLabs API response."""
    return b"mock_audio_data"


@pytest.mark.asyncio
async def test_tts_result_creation():
    """Test TTSResult creation."""
    result = TTSResult(
        success=True,
        audio_path=Path("test.mp3"),
        duration=2.5,
        text="Hello world",
        voice_id="test_voice",
        cost=0.01
    )
    
    assert result.success is True
    assert result.duration == 2.5
    assert result.cost == 0.01


@pytest.mark.asyncio
async def test_elevenlabs_voice_resolution():
    """Test voice ID resolution."""
    client = ElevenLabsClient(api_key="test_key")
    
    # Test name resolution
    resolved = client._resolve_voice_id("rachel")
    assert resolved == ElevenLabsClient.VOICES["rachel"]
    
    # Test direct ID
    test_id = "direct_voice_id_123"
    resolved = client._resolve_voice_id(test_id)
    assert resolved == test_id


def test_elevenlabs_cost_estimation():
    """Test cost estimation."""
    client = ElevenLabsClient(api_key="test_key")
    
    text = "a" * 1000  # 1000 characters
    cost = client.estimate_cost(text)
    
    assert cost > 0
    assert cost == pytest.approx(0.30, rel=0.01)


def test_elevenlabs_validate_voice():
    """Test voice validation."""
    client = ElevenLabsClient(api_key="test_key")
    
    # Valid voice name
    assert client.validate_voice_id("rachel") is True
    
    # Valid voice ID (20 chars)
    assert client.validate_voice_id("a" * 20) is True
    
    # Invalid
    assert client.validate_voice_id("invalid_short") is False

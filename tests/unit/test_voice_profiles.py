"""
Unit tests for voice profiles.

Copyright (c) 2025. All Rights Reserved. Patent Pending.
"""

import pytest
from pathlib import Path

from src.models.voice_profile import VoiceProfile
from src.services.voiceover.voice_manager import VoiceManager


def test_voice_profile_creation():
    """Test VoiceProfile creation."""
    profile = VoiceProfile(
        character_name="Test Character",
        voice_id="test_voice",
        engine="elevenlabs",
        settings={"stability": 0.75},
        description="Test voice"
    )
    
    assert profile.character_name == "Test Character"
    assert profile.engine == "elevenlabs"
    assert profile.settings["stability"] == 0.75


def test_voice_profile_validation():
    """Test voice profile validation."""
    with pytest.raises(ValueError):
        VoiceProfile(
            character_name="Test",
            voice_id="test",
            engine="invalid_engine"  # Invalid
        )


def test_voice_manager():
    """Test VoiceManager operations."""
    manager = VoiceManager()
    
    profile = VoiceProfile(
        character_name="Lucy",
        voice_id="rachel",
        engine="elevenlabs"
    )
    
    # Add
    manager.add_profile(profile)
    assert manager.get_profile("Lucy") == profile
    
    # Get non-existent
    assert manager.get_profile("NonExistent") is None
    
    # List
    profiles = manager.list_profiles()
    assert "Lucy" in profiles


def test_default_profiles():
    """Test default profile creation."""
    manager = VoiceManager()
    defaults = manager.create_default_profiles()
    
    assert "Lucy Ricardo" in defaults
    assert "Ricky Ricardo" in defaults
    
    lucy = defaults["Lucy Ricardo"]
    assert lucy.engine == "elevenlabs"
    assert lucy.voice_id == "rachel"

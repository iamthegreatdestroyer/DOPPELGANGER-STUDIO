"""
Voice Profile Model - Character voice configuration.

Copyright (c) 2025. All Rights Reserved. Patent Pending.
"""

from typing import Dict, Any, Optional
from dataclasses import dataclass, field
from pathlib import Path


@dataclass
class VoiceProfile:
    """
    Voice configuration for a character.
    
    Maps a character to specific voice settings across TTS engines.
    
    Attributes:
        character_name: Character this voice represents
        voice_id: Engine-specific voice identifier
        engine: TTS engine ('elevenlabs', 'google', 'pyttsx')
        settings: Engine-specific settings (pitch, speed, etc.)
        sample_audio: Optional sample audio file
        description: Voice description
    """
    character_name: str
    voice_id: str
    engine: str = "elevenlabs"
    settings: Dict[str, Any] = field(default_factory=dict)
    sample_audio: Optional[Path] = None
    description: str = ""
    
    def __post_init__(self):
        """Validate voice profile."""
        valid_engines = ['elevenlabs', 'google', 'pyttsx']
        if self.engine not in valid_engines:
            raise ValueError(f"Invalid engine: {self.engine}")

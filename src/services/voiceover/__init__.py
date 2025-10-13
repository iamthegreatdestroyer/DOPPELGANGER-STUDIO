"""
Voiceover Services - Text-to-Speech and audio generation.

Provides components for:
- TTS engine integration (ElevenLabs, Google, pyttsx3)
- Voice profile management
- Audio generation and processing
- Video synchronization

Copyright (c) 2025. All Rights Reserved. Patent Pending.
"""

from .tts_engine import TTSEngine, TTSResult
from .elevenlabs_client import ElevenLabsClient

__all__ = [
    'TTSEngine',
    'TTSResult',
    'ElevenLabsClient',
]

"""
TTS Engine Base - Abstract interface for text-to-speech engines.

Provides unified interface for multiple TTS providers:
- ElevenLabs (primary)
- Google Cloud TTS (fallback)
- pyttsx3 (offline)

Copyright (c) 2025. All Rights Reserved. Patent Pending.
"""

from typing import Optional, Dict, Any
from abc import ABC, abstractmethod
from dataclasses import dataclass
from pathlib import Path
import logging

logger = logging.getLogger(__name__)


@dataclass
class TTSResult:
    """
    Result from TTS generation.
    
    Attributes:
        success: Whether generation succeeded
        audio_path: Path to generated audio file
        duration: Audio duration in seconds
        text: Original text
        voice_id: Voice used for generation
        cost: API cost (if applicable)
        error: Error message if failed
    """
    success: bool
    audio_path: Optional[Path] = None
    duration: float = 0.0
    text: str = ""
    voice_id: str = ""
    cost: float = 0.0
    error: Optional[str] = None
    metadata: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}


class TTSEngine(ABC):
    """
    Abstract base class for Text-to-Speech engines.
    
    All TTS implementations must inherit from this class
    and implement the abstract methods.
    
    Example:
        >>> class MyTTSEngine(TTSEngine):
        ...     async def generate_speech(self, text, voice_id, output_path):
        ...         # Implementation
        ...         return TTSResult(...)
    """
    
    def __init__(self, api_key: Optional[str] = None, **kwargs):
        """
        Initialize TTS engine.
        
        Args:
            api_key: API key for the service (if required)
            **kwargs: Additional engine-specific parameters
        """
        self.api_key = api_key
        self.config = kwargs
        logger.info(f"{self.__class__.__name__} initialized")
    
    @abstractmethod
    async def generate_speech(
        self,
        text: str,
        voice_id: str,
        output_path: Path,
        **kwargs
    ) -> TTSResult:
        """
        Generate speech from text.
        
        Args:
            text: Text to convert to speech
            voice_id: Voice identifier for the engine
            output_path: Where to save the audio file
            **kwargs: Engine-specific parameters
            
        Returns:
            TTSResult with generation details
            
        Raises:
            TTSEngineError: If generation fails
        """
        pass
    
    @abstractmethod
    async def list_voices(self) -> Dict[str, Any]:
        """
        List available voices.
        
        Returns:
            Dictionary of available voices with metadata
            
        Example:
            >>> voices = await engine.list_voices()
            >>> print(voices.keys())
            dict_keys(['rachel', 'adam', 'bella', ...])
        """
        pass
    
    @abstractmethod
    def estimate_cost(self, text: str) -> float:
        """
        Estimate API cost for generating speech.
        
        Args:
            text: Text to be converted
            
        Returns:
            Estimated cost in USD
            
        Example:
            >>> cost = engine.estimate_cost("Hello world!")
            >>> print(f"Estimated: ${cost:.4f}")
        """
        pass
    
    def validate_voice_id(self, voice_id: str) -> bool:
        """
        Validate if voice ID is available.
        
        Args:
            voice_id: Voice identifier to validate
            
        Returns:
            True if voice is valid, False otherwise
        """
        # Default implementation - override if needed
        return True
    
    def get_engine_info(self) -> Dict[str, Any]:
        """
        Get information about the TTS engine.
        
        Returns:
            Dictionary with engine details
        """
        return {
            "name": self.__class__.__name__,
            "api_key_set": self.api_key is not None,
            "config": self.config,
        }


class TTSEngineError(Exception):
    """Base exception for TTS engine errors."""
    pass


class TTSAPIError(TTSEngineError):
    """API request failed."""
    pass


class TTSRateLimitError(TTSEngineError):
    """API rate limit exceeded."""
    pass


class TTSInvalidVoiceError(TTSEngineError):
    """Invalid voice ID provided."""
    pass


# Copyright (c) 2025. All Rights Reserved. Patent Pending.

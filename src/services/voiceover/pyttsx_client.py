"""
pyttsx3 Client - Offline TTS for development.

Copyright (c) 2025. All Rights Reserved. Patent Pending.
"""

from typing import Dict, Any
from pathlib import Path
import logging

try:
    import pyttsx3
    PYTTSX_AVAILABLE = True
except ImportError:
    PYTTSX_AVAILABLE = False

from .tts_engine import TTSEngine, TTSResult

logger = logging.getLogger(__name__)


class Pyttsx3Client(TTSEngine):
    """
    Offline TTS using pyttsx3.
    
    Features:
    - No API required
    - Instant generation
    - Cross-platform
    - Free
    
    Limitations:
    - Lower quality
    - Robotic sound
    - Limited voices
    
    Use Case: Development and testing
    """
    
    def __init__(self):
        """Initialize pyttsx3 client."""
        if not PYTTSX_AVAILABLE:
            raise ImportError("Install: pip install pyttsx3")
        
        super().__init__()
        self.engine = pyttsx3.init()
        logger.info("Pyttsx3Client initialized")
    
    async def generate_speech(
        self,
        text: str,
        voice_id: str,
        output_path: Path,
        **kwargs
    ) -> TTSResult:
        """
        Generate speech using pyttsx3.
        
        Args:
            text: Text to convert
            voice_id: Voice index (0, 1, etc.)
            output_path: Output file path
            
        Returns:
            TTSResult
        """
        try:
            # Set voice
            voices = self.engine.getProperty('voices')
            if voice_id.isdigit():
                voice_idx = int(voice_id)
                if voice_idx < len(voices):
                    self.engine.setProperty('voice', voices[voice_idx].id)
            
            # Save to file
            output_path.parent.mkdir(parents=True, exist_ok=True)
            self.engine.save_to_file(text, str(output_path))
            self.engine.runAndWait()
            
            logger.info(f"pyttsx3 generated: {output_path.name}")
            
            return TTSResult(
                success=True,
                audio_path=output_path,
                text=text,
                voice_id=voice_id,
                cost=0.0,  # Free
                metadata={"engine": "pyttsx3"}
            )
        
        except Exception as e:
            logger.error(f"pyttsx3 failed: {e}")
            return TTSResult(
                success=False,
                text=text,
                voice_id=voice_id,
                error=str(e)
            )
    
    async def list_voices(self) -> Dict[str, Any]:
        """List available voices."""
        voices = self.engine.getProperty('voices')
        return {
            str(i): {
                "id": voice.id,
                "name": voice.name,
                "languages": voice.languages
            }
            for i, voice in enumerate(voices)
        }
    
    def estimate_cost(self, text: str) -> float:
        """Free - no cost."""
        return 0.0

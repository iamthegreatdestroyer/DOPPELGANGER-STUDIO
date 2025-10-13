"""
Google Cloud TTS Client - Reliable fallback TTS engine.

Copyright (c) 2025. All Rights Reserved. Patent Pending.
"""

from typing import Dict, Any, Optional
from pathlib import Path
import logging

try:
    from google.cloud import texttospeech
    GOOGLE_TTS_AVAILABLE = True
except ImportError:
    GOOGLE_TTS_AVAILABLE = False
    logging.warning("Google Cloud TTS not installed")

from .tts_engine import TTSEngine, TTSResult, TTSAPIError

logger = logging.getLogger(__name__)


class GoogleTTSClient(TTSEngine):
    """
    Google Cloud Text-to-Speech client.
    
    Features:
    - WaveNet and Neural2 voices
    - SSML support
    - Multiple languages
    - Reliable and fast
    
    Example:
        >>> client = GoogleTTSClient()
        >>> result = await client.generate_speech(
        ...     text="Hello world!",
        ...     voice_id="en-US-Neural2-F",
        ...     output_path=Path("output.mp3")
        ... )
    """
    
    VOICES = {
        "female_us_1": "en-US-Neural2-F",
        "female_us_2": "en-US-Neural2-E",
        "male_us_1": "en-US-Neural2-D",
        "male_us_2": "en-US-Neural2-A",
    }
    
    def __init__(self, credentials_path: Optional[str] = None):
        """
        Initialize Google TTS client.
        
        Args:
            credentials_path: Path to credentials JSON
        """
        if not GOOGLE_TTS_AVAILABLE:
            raise ImportError("Install: pip install google-cloud-texttospeech")
        
        super().__init__()
        
        # Initialize client
        if credentials_path:
            import os
            os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = credentials_path
        
        self.client = texttospeech.TextToSpeechClient()
        logger.info("GoogleTTSClient initialized")
    
    async def generate_speech(
        self,
        text: str,
        voice_id: str,
        output_path: Path,
        speaking_rate: float = 1.0,
        pitch: float = 0.0,
        **kwargs
    ) -> TTSResult:
        """
        Generate speech using Google Cloud TTS.
        
        Args:
            text: Text to convert
            voice_id: Voice identifier
            output_path: Output file path
            speaking_rate: Speech speed (0.25-4.0)
            pitch: Voice pitch (-20.0 to 20.0)
            
        Returns:
            TTSResult
        """
        try:
            # Resolve voice
            actual_voice = self._resolve_voice_id(voice_id)
            
            # Build request
            synthesis_input = texttospeech.SynthesisInput(text=text)
            
            voice = texttospeech.VoiceSelectionParams(
                language_code="en-US",
                name=actual_voice
            )
            
            audio_config = texttospeech.AudioConfig(
                audio_encoding=texttospeech.AudioEncoding.MP3,
                speaking_rate=speaking_rate,
                pitch=pitch
            )
            
            # Generate
            response = self.client.synthesize_speech(
                input=synthesis_input,
                voice=voice,
                audio_config=audio_config
            )
            
            # Save
            output_path.parent.mkdir(parents=True, exist_ok=True)
            with open(output_path, 'wb') as f:
                f.write(response.audio_content)
            
            cost = self.estimate_cost(text)
            
            logger.info(f"Google TTS generated: {output_path.name}")
            
            return TTSResult(
                success=True,
                audio_path=output_path,
                text=text,
                voice_id=voice_id,
                cost=cost,
                metadata={"engine": "google_tts"}
            )
        
        except Exception as e:
            logger.error(f"Google TTS failed: {e}")
            return TTSResult(
                success=False,
                text=text,
                voice_id=voice_id,
                error=str(e)
            )
    
    def _resolve_voice_id(self, voice_id: str) -> str:
        """Resolve voice name to ID."""
        return self.VOICES.get(voice_id.lower(), voice_id)
    
    async def list_voices(self) -> Dict[str, Any]:
        """List available voices."""
        try:
            response = self.client.list_voices(language_code="en-US")
            return {
                voice.name: {
                    "language_codes": voice.language_codes,
                    "gender": voice.ssml_gender.name
                }
                for voice in response.voices
            }
        except Exception as e:
            logger.error(f"Failed to list voices: {e}")
            return {}
    
    def estimate_cost(self, text: str) -> float:
        """Estimate cost (~$4 per 1M characters)."""
        characters = len(text)
        return (characters / 1_000_000) * 4.0

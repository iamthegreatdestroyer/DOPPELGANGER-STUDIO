"""
ElevenLabs TTS Client - Integration with ElevenLabs API.

Provides ultra-realistic text-to-speech using ElevenLabs' AI voices.

Copyright (c) 2025. All Rights Reserved. Patent Pending.
"""

from typing import Dict, Any, Optional
from pathlib import Path
import asyncio
import aiohttp
import logging
import time

from .tts_engine import (
    TTSEngine,
    TTSResult,
    TTSAPIError,
    TTSRateLimitError,
    TTSInvalidVoiceError
)

logger = logging.getLogger(__name__)


class ElevenLabsClient(TTSEngine):
    """
    ElevenLabs API client for text-to-speech generation.
    
    Features:
    - Ultra-realistic AI voices
    - Multiple voice profiles
    - Emotion and style control
    - Voice cloning (premium)
    
    Attributes:
        api_key: ElevenLabs API key
        base_url: API base URL
        session: aiohttp session
        
    Example:
        >>> client = ElevenLabsClient(api_key="your_key")
        >>> async with client:
        ...     result = await client.generate_speech(
        ...         text="Hello world!",
        ...         voice_id="rachel",
        ...         output_path=Path("output.mp3")
        ...     )
        ...     print(f"Generated: {result.audio_path}")
    """
    
    BASE_URL = "https://api.elevenlabs.io/v1"
    
    # Voice IDs (common voices)
    VOICES = {
        "rachel": "21m00Tcm4TlvDq8ikWAM",  # Female, calm
        "adam": "pNInz6obpgDQGcFmaJgB",    # Male, warm
        "bella": "EXAVITQu4vr4xnSDxMaL",   # Female, soft
        "antoni": "ErXwobaYiN019PkySvjV",  # Male, well-rounded
        "elli": "MF3mGyEYCl7XYWbV9V6O",    # Female, emotional
        "josh": "TxGEqnHWrfWFTfGW9XjX",    # Male, young
    }
    
    def __init__(
        self,
        api_key: str,
        model_id: str = "eleven_monolingual_v1",
        timeout: int = 30,
        retry_attempts: int = 3
    ):
        """
        Initialize ElevenLabs client.
        
        Args:
            api_key: ElevenLabs API key
            model_id: Model to use for generation
            timeout: Request timeout in seconds
            retry_attempts: Number of retry attempts
            
        Raises:
            ValueError: If API key is empty
        """
        if not api_key:
            raise ValueError("ElevenLabs API key required")
        
        super().__init__(api_key=api_key)
        
        self.model_id = model_id
        self.timeout = timeout
        self.retry_attempts = retry_attempts
        self.session: Optional[aiohttp.ClientSession] = None
        
        logger.info("ElevenLabsClient initialized")
    
    async def __aenter__(self):
        """Async context manager entry."""
        self.session = aiohttp.ClientSession(
            headers={
                "xi-api-key": self.api_key,
                "Content-Type": "application/json"
            },
            timeout=aiohttp.ClientTimeout(total=self.timeout)
        )
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        if self.session:
            await self.session.close()
    
    async def generate_speech(
        self,
        text: str,
        voice_id: str,
        output_path: Path,
        stability: float = 0.75,
        similarity_boost: float = 0.75,
        **kwargs
    ) -> TTSResult:
        """
        Generate speech using ElevenLabs API.
        
        Args:
            text: Text to convert to speech
            voice_id: Voice identifier (name or ID)
            output_path: Where to save MP3 file
            stability: Voice stability (0.0-1.0)
            similarity_boost: Voice similarity (0.0-1.0)
            **kwargs: Additional voice settings
            
        Returns:
            TTSResult with generation details
            
        Raises:
            TTSAPIError: If API request fails
            TTSRateLimitError: If rate limit exceeded
            TTSInvalidVoiceError: If voice not found
            
        Example:
            >>> result = await client.generate_speech(
            ...     text="Hello!",
            ...     voice_id="rachel",
            ...     output_path=Path("hello.mp3")
            ... )
            >>> print(f"Duration: {result.duration}s")
        """
        if not self.session:
            raise RuntimeError("Client not initialized. Use 'async with' context.")
        
        start_time = time.time()
        
        # Resolve voice ID
        actual_voice_id = self._resolve_voice_id(voice_id)
        
        # Build request
        url = f"{self.BASE_URL}/text-to-speech/{actual_voice_id}"
        
        payload = {
            "text": text,
            "model_id": self.model_id,
            "voice_settings": {
                "stability": stability,
                "similarity_boost": similarity_boost,
                **kwargs
            }
        }
        
        # Retry logic
        last_error = None
        
        for attempt in range(self.retry_attempts):
            try:
                logger.debug(
                    f"ElevenLabs request (attempt {attempt + 1}): "
                    f"{len(text)} chars, voice={voice_id}"
                )
                
                async with self.session.post(url, json=payload) as response:
                    if response.status == 200:
                        # Save audio file
                        audio_data = await response.read()
                        output_path.parent.mkdir(parents=True, exist_ok=True)
                        
                        with open(output_path, 'wb') as f:
                            f.write(audio_data)
                        
                        duration = time.time() - start_time
                        
                        # Calculate cost
                        cost = self.estimate_cost(text)
                        
                        logger.info(
                            f"ElevenLabs generated: {output_path.name} "
                            f"({len(text)} chars, ${cost:.4f})"
                        )
                        
                        return TTSResult(
                            success=True,
                            audio_path=output_path,
                            duration=duration,
                            text=text,
                            voice_id=voice_id,
                            cost=cost,
                            metadata={
                                "engine": "elevenlabs",
                                "model_id": self.model_id,
                                "characters": len(text),
                            }
                        )
                    
                    elif response.status == 429:
                        # Rate limit
                        retry_after = int(response.headers.get('Retry-After', 60))
                        logger.warning(
                            f"ElevenLabs rate limit. Retry after {retry_after}s"
                        )
                        
                        if attempt < self.retry_attempts - 1:
                            await asyncio.sleep(retry_after)
                            continue
                        else:
                            raise TTSRateLimitError(
                                f"Rate limit exceeded after {self.retry_attempts} attempts"
                            )
                    
                    elif response.status == 401:
                        raise TTSAPIError("Invalid API key")
                    
                    elif response.status == 404:
                        raise TTSInvalidVoiceError(f"Voice not found: {voice_id}")
                    
                    else:
                        error_text = await response.text()
                        last_error = TTSAPIError(
                            f"API error {response.status}: {error_text}"
                        )
                        
                        if attempt < self.retry_attempts - 1:
                            await asyncio.sleep(2 ** attempt)  # Exponential backoff
                            continue
            
            except aiohttp.ClientError as e:
                last_error = TTSAPIError(f"Network error: {e}")
                
                if attempt < self.retry_attempts - 1:
                    await asyncio.sleep(2 ** attempt)
                    continue
        
        # All retries failed
        logger.error(f"ElevenLabs generation failed: {last_error}")
        
        return TTSResult(
            success=False,
            text=text,
            voice_id=voice_id,
            error=str(last_error)
        )
    
    def _resolve_voice_id(self, voice_id: str) -> str:
        """
        Resolve voice name to ID.
        
        Args:
            voice_id: Voice name or ID
            
        Returns:
            Actual voice ID for API
        """
        # If it's a known name, return the ID
        if voice_id.lower() in self.VOICES:
            return self.VOICES[voice_id.lower()]
        
        # Otherwise assume it's already an ID
        return voice_id
    
    async def list_voices(self) -> Dict[str, Any]:
        """
        List available voices from ElevenLabs.
        
        Returns:
            Dictionary of voice names and metadata
            
        Example:
            >>> voices = await client.list_voices()
            >>> for name, data in voices.items():
            ...     print(f"{name}: {data['description']}")
        """
        if not self.session:
            raise RuntimeError("Client not initialized")
        
        url = f"{self.BASE_URL}/voices"
        
        try:
            async with self.session.get(url) as response:
                if response.status == 200:
                    data = await response.json()
                    voices = data.get('voices', [])
                    
                    return {
                        voice['name'].lower(): {
                            'voice_id': voice['voice_id'],
                            'description': voice.get('description', ''),
                            'category': voice.get('category', 'unknown'),
                        }
                        for voice in voices
                    }
                else:
                    logger.error(f"Failed to list voices: {response.status}")
                    return {}
        
        except Exception as e:
            logger.error(f"Error listing voices: {e}")
            return {}
    
    def estimate_cost(self, text: str) -> float:
        """
        Estimate cost for generating speech.
        
        ElevenLabs pricing (as of 2025):
        - Free tier: 10,000 characters/month
        - Creator tier: $5/month for 30,000 chars
        - Pro tier: $22/month for 100,000 chars
        
        Args:
            text: Text to be converted
            
        Returns:
            Estimated cost in USD
            
        Example:
            >>> cost = client.estimate_cost("Hello world!")
            >>> print(f"Cost: ${cost:.4f}")
        """
        characters = len(text)
        
        # Rough estimate: $0.30 per 1000 characters (pro tier)
        cost_per_1k = 0.30
        cost = (characters / 1000) * cost_per_1k
        
        return cost
    
    def validate_voice_id(self, voice_id: str) -> bool:
        """
        Validate voice ID.
        
        Args:
            voice_id: Voice to validate
            
        Returns:
            True if valid
        """
        return voice_id.lower() in self.VOICES or len(voice_id) == 20


# Example usage
async def main():
    """Example ElevenLabs usage."""
    import os
    
    api_key = os.getenv('ELEVENLABS_API_KEY')
    
    if not api_key:
        print("Set ELEVENLABS_API_KEY environment variable")
        return
    
    async with ElevenLabsClient(api_key) as client:
        # Generate speech
        result = await client.generate_speech(
            text="Hello! I'm Lucy Ricardo, and welcome to DOPPELGANGER STUDIO!",
            voice_id="rachel",
            output_path=Path("output/lucy_intro.mp3")
        )
        
        if result.success:
            print(f"✅ Generated: {result.audio_path}")
            print(f"   Duration: {result.duration:.1f}s")
            print(f"   Cost: ${result.cost:.4f}")
        else:
            print(f"❌ Failed: {result.error}")


if __name__ == "__main__":
    asyncio.run(main())


# Copyright (c) 2025. All Rights Reserved. Patent Pending.

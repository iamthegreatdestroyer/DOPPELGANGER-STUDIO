"""
Audio Generator - Batch dialogue audio generation.

Copyright (c) 2025. All Rights Reserved. Patent Pending.
"""

from typing import List, Dict, Optional, Callable
from dataclasses import dataclass
from pathlib import Path
import asyncio
import logging

from src.models.voice_profile import VoiceProfile
from .tts_engine import TTSEngine, TTSResult
from .elevenlabs_client import ElevenLabsClient

logger = logging.getLogger(__name__)


@dataclass
class DialogueLine:
    """Single line of dialogue."""
    character: str
    text: str
    scene_id: str
    line_number: int


@dataclass
class AudioFile:
    """Generated audio file."""
    dialogue_line: DialogueLine
    audio_path: Path
    duration: float
    cost: float


class AudioGenerator:
    """
    Generate audio for dialogue using TTS engines.
    
    Example:
        >>> generator = AudioGenerator(engine, voice_manager)
        >>> files = await generator.generate_dialogue(lines)
    """
    
    def __init__(
        self,
        tts_engine: TTSEngine,
        voice_profiles: Dict[str, VoiceProfile],
        output_dir: Path = Path("output/audio")
    ):
        """
        Initialize audio generator.
        
        Args:
            tts_engine: TTS engine to use
            voice_profiles: Character voice profiles
            output_dir: Output directory for audio files
        """
        self.tts_engine = tts_engine
        self.voice_profiles = voice_profiles
        self.output_dir = output_dir
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        logger.info("AudioGenerator initialized")
    
    async def generate_dialogue(
        self,
        dialogue_lines: List[DialogueLine],
        progress_callback: Optional[Callable[[int, int], None]] = None
    ) -> List[AudioFile]:
        """
        Generate audio for all dialogue lines.
        
        Args:
            dialogue_lines: Lines to generate
            progress_callback: Progress updates (current, total)
            
        Returns:
            List of generated audio files
        """
        audio_files = []
        total = len(dialogue_lines)
        
        logger.info(f"Generating audio for {total} lines")
        
        for i, line in enumerate(dialogue_lines, 1):
            if progress_callback:
                progress_callback(i, total)
            
            # Get voice profile
            profile = self.voice_profiles.get(line.character)
            if not profile:
                logger.warning(f"No voice profile for: {line.character}")
                continue
            
            # Generate filename
            filename = f"{line.scene_id}_line{line.line_number}_{line.character.replace(' ', '_')}.mp3"
            output_path = self.output_dir / filename
            
            # Generate audio
            result = await self.tts_engine.generate_speech(
                text=line.text,
                voice_id=profile.voice_id,
                output_path=output_path,
                **profile.settings
            )
            
            if result.success:
                audio_files.append(AudioFile(
                    dialogue_line=line,
                    audio_path=result.audio_path,
                    duration=result.duration,
                    cost=result.cost
                ))
                
                logger.debug(
                    f"Generated [{i}/{total}]: {filename} "
                    f"({result.duration:.1f}s, ${result.cost:.4f})"
                )
            else:
                logger.error(f"Failed to generate audio: {result.error}")
        
        total_cost = sum(f.cost for f in audio_files)
        logger.info(
            f"Generated {len(audio_files)}/{total} audio files. "
            f"Total cost: ${total_cost:.2f}"
        )
        
        return audio_files

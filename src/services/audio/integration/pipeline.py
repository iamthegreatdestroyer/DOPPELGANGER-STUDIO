"""
Complete Audio Production Pipeline.

Integrates music selection, SFX placement, mixing, and mastering
into a single end-to-end workflow.

Copyright (c) 2025. All Rights Reserved. Patent Pending.
"""

from typing import Dict, List, Optional
from dataclasses import dataclass
from pathlib import Path
import logging
from pydub import AudioSegment

from src.services.audio.music.library import MusicLibrary
from src.services.audio.music.selector import MusicSelector, SceneContext
from src.services.audio.sfx.library import SFXLibrary
from src.services.audio.sfx.placer import SFXPlacer
from src.services.audio.mixing.mixer import AudioMixer
from src.services.audio.mixing.mastering import AudioMaster

logger = logging.getLogger(__name__)


@dataclass
class AudioConfig:
    """Configuration for audio pipeline."""
    music_enabled: bool = True
    sfx_enabled: bool = True
    apply_ducking: bool = True
    apply_mastering: bool = True
    target_platform: str = 'youtube'  # youtube, spotify, broadcast
    fade_in_ms: int = 500
    fade_out_ms: int = 1000


@dataclass
class AudioResult:
    """Result from audio pipeline."""
    audio: AudioSegment
    duration_seconds: float
    music_track: Optional[str] = None
    sfx_count: int = 0
    peak_db: float = 0.0
    rms_db: float = 0.0


class AudioPipeline:
    """
    Complete audio production pipeline.
    
    Integrates all audio systems into single workflow:
    1. Select background music
    2. Place sound effects
    3. Mix all tracks
    4. Master final audio
    5. Export for platform
    
    Example:
        >>> pipeline = AudioPipeline(
        ...     music_library_path="music",
        ...     sfx_library_path="sfx"
        ... )
        >>> result = await pipeline.process_scene(
        ...     dialogue_audio=dialogue,
        ...     scene_context=context,
        ...     script_lines=lines
        ... )
        >>> result.audio.export("final_audio.mp3")
    """
    
    def __init__(
        self,
        music_library_path: Path,
        sfx_library_path: Path
    ):
        """
        Initialize audio pipeline.
        
        Args:
            music_library_path: Path to music library
            sfx_library_path: Path to SFX library
        """
        # Initialize components
        self.music_library = MusicLibrary(music_library_path)
        self.music_selector = MusicSelector(self.music_library)
        
        self.sfx_library = SFXLibrary(sfx_library_path)
        self.sfx_placer = SFXPlacer(self.sfx_library)
        
        self.mixer = AudioMixer()
        self.master = AudioMaster()
        
        logger.info("Audio pipeline initialized")
    
    async def process_scene(
        self,
        dialogue_audio: AudioSegment,
        scene_context: SceneContext,
        script_lines: Optional[List[Dict]] = None,
        config: Optional[AudioConfig] = None
    ) -> AudioResult:
        """
        Process complete scene audio.
        
        Args:
            dialogue_audio: Voiceover/dialogue audio
            scene_context: Scene context for music selection
            script_lines: Script lines for SFX placement
            config: Audio configuration
            
        Returns:
            AudioResult with final audio and metadata
        """
        config = config or AudioConfig()
        
        logger.info(f"Processing scene audio: {len(dialogue_audio)/1000:.1f}s")
        
        # Step 1: Select and prepare music
        music_audio = None
        music_track_name = None
        if config.music_enabled:
            music_audio = await self.music_selector.select_and_prepare(
                scene_context,
                fade_in_ms=config.fade_in_ms,
                fade_out_ms=config.fade_out_ms
            )
            if music_audio:
                music_track_name = "Selected Track"
                logger.info("Music selected and prepared")
        
        # Step 2: Place sound effects
        sfx_audio = None
        sfx_count = 0
        if config.sfx_enabled and script_lines:
            placements = await self.sfx_placer.analyze_script(script_lines)
            if placements:
                sfx_audio = await self.sfx_placer.render_effects(
                    placements,
                    len(dialogue_audio)
                )
                sfx_count = len(placements)
                logger.info(f"Placed {sfx_count} sound effects")
        
        # Step 3: Mix all tracks
        mixed_audio = await self.mixer.mix_tracks(
            dialogue=dialogue_audio,
            music=music_audio,
            sfx=[sfx_audio] if sfx_audio else None,
            apply_ducking=config.apply_ducking
        )
        logger.info("Tracks mixed")
        
        # Step 4: Master final audio
        final_audio = mixed_audio
        if config.apply_mastering:
            final_audio = await self.master.master_for_platform(
                mixed_audio,
                platform=config.target_platform
            )
            logger.info(f"Audio mastered for {config.target_platform}")
        
        # Get final levels
        levels = self.master.get_levels(final_audio)
        
        # Build result
        result = AudioResult(
            audio=final_audio,
            duration_seconds=len(final_audio) / 1000.0,
            music_track=music_track_name,
            sfx_count=sfx_count,
            peak_db=levels['peak_db'],
            rms_db=levels['rms_db']
        )
        
        logger.info(f"Scene audio complete: {result.duration_seconds:.1f}s, "
                   f"peak={result.peak_db:.1f}dB")
        
        return result
    
    async def process_episode(
        self,
        scenes: List[Dict],
        config: Optional[AudioConfig] = None
    ) -> AudioResult:
        """
        Process complete episode with multiple scenes.
        
        Args:
            scenes: List of scene data with format:
                [{
                    'dialogue_audio': AudioSegment,
                    'scene_context': SceneContext,
                    'script_lines': List[Dict]
                }]
            config: Audio configuration
            
        Returns:
            AudioResult with complete episode audio
        """
        config = config or AudioConfig()
        
        logger.info(f"Processing episode with {len(scenes)} scenes")
        
        # Process each scene
        scene_audios = []
        total_sfx = 0
        
        for i, scene_data in enumerate(scenes):
            logger.info(f"Processing scene {i+1}/{len(scenes)}")
            
            result = await self.process_scene(
                dialogue_audio=scene_data['dialogue_audio'],
                scene_context=scene_data['scene_context'],
                script_lines=scene_data.get('script_lines'),
                config=config
            )
            
            scene_audios.append(result.audio)
            total_sfx += result.sfx_count
        
        # Concatenate all scenes
        episode_audio = scene_audios[0]
        for scene_audio in scene_audios[1:]:
            episode_audio = episode_audio + scene_audio
        
        # Final master
        if config.apply_mastering:
            episode_audio = await self.master.master_for_platform(
                episode_audio,
                platform=config.target_platform
            )
        
        # Get final levels
        levels = self.master.get_levels(episode_audio)
        
        result = AudioResult(
            audio=episode_audio,
            duration_seconds=len(episode_audio) / 1000.0,
            sfx_count=total_sfx,
            peak_db=levels['peak_db'],
            rms_db=levels['rms_db']
        )
        
        logger.info(f"Episode complete: {len(scenes)} scenes, "
                   f"{result.duration_seconds:.1f}s, {total_sfx} SFX")
        
        return result
    
    def get_pipeline_stats(self) -> Dict:
        """Get statistics about pipeline components."""
        return {
            'music_library': self.music_library.get_stats(),
            'sfx_library': self.sfx_library.get_stats(),
            'music_selections': self.music_selector.get_selection_stats()
        }

"""
Complete Video Production Pipeline.

Integrates all video systems into end-to-end workflow.

Copyright (c) 2025. All Rights Reserved. Patent Pending.
"""

from typing import List, Dict, Optional
from dataclasses import dataclass
from pathlib import Path
import logging

from src.services.video.composition.compositor import VideoCompositor
from src.services.video.composition.scene_assembler import SceneAssembler
from src.services.video.graphics.title_cards import TitleCardGenerator, TitleCardConfig
from src.services.video.graphics.credits import CreditsGenerator, CreditsConfig
from src.services.video.effects.color_grading import ColorGrading
from src.services.video.export.optimizer import ExportOptimizer

logger = logging.getLogger(__name__)


@dataclass
class VideoConfig:
    """Video pipeline configuration."""
    add_title_card: bool = True
    add_credits: bool = True
    apply_color_grade: bool = True
    color_grade_preset: str = 'cinematic'
    export_preset: str = 'youtube_1080p'


@dataclass
class VideoResult:
    """Video pipeline result."""
    video_path: Path
    duration_seconds: float
    resolution: tuple
    file_size_mb: float


class VideoPipeline:
    """
    Complete video production pipeline.
    
    Workflow:
    1. Compose animation + audio
    2. Add title card
    3. Assemble scenes
    4. Add credits
    5. Apply color grading
    6. Optimize for export
    
    Example:
        >>> pipeline = VideoPipeline()
        >>> result = await pipeline.produce_episode(
        ...     scenes=scene_data,
        ...     title_config=title_config,
        ...     output="episode.mp4"
        ... )
    """
    
    def __init__(self):
        """Initialize video pipeline."""
        self.compositor = VideoCompositor()
        self.assembler = SceneAssembler()
        self.title_generator = TitleCardGenerator()
        self.credits_generator = CreditsGenerator()
        self.color_grading = ColorGrading()
        self.optimizer = ExportOptimizer()
        
        logger.info("Video pipeline initialized")
    
    async def produce_episode(
        self,
        scenes: List[Dict],
        output_path: Path,
        title_config: Optional[TitleCardConfig] = None,
        credits_config: Optional[CreditsConfig] = None,
        config: Optional[VideoConfig] = None
    ) -> VideoResult:
        """
        Produce complete episode from scenes.
        
        Args:
            scenes: List of scene data with format:
                [{
                    'animation_path': Path,
                    'audio_path': Path
                }]
            output_path: Final episode output path
            title_config: Title card configuration
            credits_config: Credits configuration
            config: Pipeline configuration
            
        Returns:
            VideoResult with final episode info
        """
        config = config or VideoConfig()
        
        logger.info(f"Producing episode with {len(scenes)} scenes")
        
        # Step 1: Compose each scene (animation + audio)
        composed_scenes = []
        for i, scene_data in enumerate(scenes):
            logger.info(f"Composing scene {i+1}/{len(scenes)}")
            
            scene_output = Path(f"temp_scene_{i}.mp4")
            await self.compositor.compose(
                animation_path=scene_data['animation_path'],
                audio_path=scene_data['audio_path'],
                output_path=scene_output
            )
            composed_scenes.append(scene_output)
        
        # Step 2: Add title card
        if config.add_title_card and title_config:
            logger.info("Adding title card")
            title_path = Path("temp_title.mp4")
            await self.title_generator.create_title_card(
                title_config,
                title_path
            )
            composed_scenes.insert(0, title_path)
        
        # Step 3: Assemble all scenes
        logger.info("Assembling scenes")
        assembled_path = Path("temp_assembled.mp4")
        await self.assembler.assemble_episode(
            scenes=composed_scenes,
            output_path=assembled_path
        )
        
        # Step 4: Add credits
        if config.add_credits and credits_config:
            logger.info("Adding credits")
            credits_path = Path("temp_credits.mp4")
            await self.credits_generator.create_credits(
                credits_config,
                credits_path
            )
            
            # Concatenate with credits
            final_with_credits = Path("temp_with_credits.mp4")
            await self.assembler.assemble_episode(
                scenes=[assembled_path, credits_path],
                output_path=final_with_credits
            )
            assembled_path = final_with_credits
        
        # Step 5: Apply color grading
        if config.apply_color_grade:
            logger.info(f"Applying {config.color_grade_preset} color grade")
            graded_path = Path("temp_graded.mp4")
            await self.color_grading.apply_grade(
                video=assembled_path,
                output=graded_path,
                preset=config.color_grade_preset
            )
            assembled_path = graded_path
        
        # Step 6: Optimize for export
        logger.info(f"Optimizing with {config.export_preset} preset")
        await self.optimizer.optimize(
            input=assembled_path,
            output=output_path,
            preset=config.export_preset
        )
        
        # Clean up temp files
        self._cleanup_temp_files()
        
        # Get final video info
        video_info = await self.compositor.get_video_info(output_path)
        file_size = output_path.stat().st_size / (1024 * 1024)  # MB
        
        result = VideoResult(
            video_path=output_path,
            duration_seconds=video_info.get('duration', 0),
            resolution=(video_info.get('width', 0), video_info.get('height', 0)),
            file_size_mb=file_size
        )
        
        logger.info(f"Episode complete: {result.duration_seconds:.1f}s, "
                   f"{result.file_size_mb:.1f}MB")
        
        return result
    
    def _cleanup_temp_files(self):
        """Clean up temporary files."""
        temp_patterns = [
            "temp_*.mp4",
            "temp_*.png"
        ]
        
        for pattern in temp_patterns:
            for temp_file in Path('.').glob(pattern):
                try:
                    temp_file.unlink()
                    logger.debug(f"Cleaned up: {temp_file}")
                except Exception as e:
                    logger.warning(f"Failed to clean up {temp_file}: {e}")

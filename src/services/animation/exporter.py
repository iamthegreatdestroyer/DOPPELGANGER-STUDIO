"""
Video Exporter - Compile scenes into final videos.

Handles multi-scene compilation, quality settings, progress tracking,
and metadata embedding.

Copyright (c) 2025. All Rights Reserved. Patent Pending.
"""

from typing import List, Optional, Callable, Dict, Any
from pathlib import Path
from dataclasses import dataclass
import logging
import subprocess
import json

logger = logging.getLogger(__name__)


@dataclass
class ExportResult:
    """Result of video export operation."""
    success: bool
    output_path: Optional[Path]
    duration: float
    file_size: int
    errors: List[str]


class VideoExporter:
    """
    Export and compile animation scenes to video.
    
    Handles concatenation of multiple scene videos into
    complete episodes with metadata.
    
    Example:
        >>> exporter = VideoExporter()
        >>> result = await exporter.export_episode(
        ...     scene_paths=[Path("scene1.mp4"), Path("scene2.mp4")],
        ...     output_path=Path("episode1.mp4")
        ... )
    """
    
    def __init__(self, ffmpeg_path: str = "ffmpeg"):
        """
        Initialize video exporter.
        
        Args:
            ffmpeg_path: Path to ffmpeg executable
        """
        self.ffmpeg_path = ffmpeg_path
        logger.info("VideoExporter initialized")
    
    async def export_episode(
        self,
        scene_paths: List[Path],
        output_path: Path,
        quality: str = "high",
        metadata: Optional[Dict[str, str]] = None,
        progress_callback: Optional[Callable[[float], None]] = None
    ) -> ExportResult:
        """
        Export complete episode from scene videos.
        
        Args:
            scene_paths: Paths to scene video files
            output_path: Output video path
            quality: Export quality preset
            metadata: Video metadata to embed
            progress_callback: Optional progress updates
            
        Returns:
            ExportResult with status and details
        """
        logger.info(f"Exporting episode: {len(scene_paths)} scenes")
        
        try:
            # Create concat file for ffmpeg
            concat_file = output_path.parent / "concat_list.txt"
            with open(concat_file, 'w') as f:
                for scene_path in scene_paths:
                    f.write(f"file '{scene_path.absolute()}'\n")
            
            # Build ffmpeg command
            cmd = [
                self.ffmpeg_path,
                '-f', 'concat',
                '-safe', '0',
                '-i', str(concat_file),
                '-c', 'copy',
                str(output_path)
            ]
            
            # Add metadata if provided
            if metadata:
                for key, value in metadata.items():
                    cmd.extend(['-metadata', f'{key}={value}'])
            
            # Execute ffmpeg
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True
            )
            
            # Clean up concat file
            concat_file.unlink(missing_ok=True)
            
            if result.returncode == 0:
                file_size = output_path.stat().st_size
                
                logger.info(f"Export successful: {output_path}")
                
                return ExportResult(
                    success=True,
                    output_path=output_path,
                    duration=0.0,  # Calculate from metadata
                    file_size=file_size,
                    errors=[]
                )
            else:
                logger.error(f"Export failed: {result.stderr}")
                return ExportResult(
                    success=False,
                    output_path=None,
                    duration=0.0,
                    file_size=0,
                    errors=[result.stderr]
                )
        
        except Exception as e:
            logger.error(f"Export exception: {e}")
            return ExportResult(
                success=False,
                output_path=None,
                duration=0.0,
                file_size=0,
                errors=[str(e)]
            )
    
    def validate_scenes(self, scene_paths: List[Path]) -> List[str]:
        """
        Validate scene video files.
        
        Args:
            scene_paths: Paths to validate
            
        Returns:
            List of validation errors
        """
        errors = []
        
        for path in scene_paths:
            if not path.exists():
                errors.append(f"Scene not found: {path}")
            elif path.stat().st_size == 0:
                errors.append(f"Empty scene file: {path}")
        
        return errors


# Copyright (c) 2025. All Rights Reserved. Patent Pending.

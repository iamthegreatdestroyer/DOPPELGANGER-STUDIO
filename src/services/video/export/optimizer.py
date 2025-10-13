"""
Export Optimizer - Video Export Optimization.

Copyright (c) 2025. All Rights Reserved. Patent Pending.
"""

from typing import Dict, Tuple
from pathlib import Path
import logging
import subprocess

logger = logging.getLogger(__name__)


class ExportOptimizer:
    """
    Optimize video export for platform delivery.
    
    Quality presets:
    - youtube_1080p: 1920x1080, 5Mbps, 30fps
    - youtube_720p: 1280x720, 2.5Mbps, 30fps
    - high_quality: 1920x1080, 10Mbps, 60fps
    
    Example:
        >>> optimizer = ExportOptimizer()
        >>> optimized = await optimizer.optimize(
        ...     input="raw.mp4",
        ...     output="optimized.mp4",
        ...     preset="youtube_1080p"
        ... )
    """
    
    QUALITY_PRESETS = {
        'youtube_1080p': {
            'resolution': (1920, 1080),
            'fps': 30,
            'video_bitrate': '5M',
            'audio_bitrate': '192k',
            'codec': 'libx264',
            'preset': 'medium'
        },
        'youtube_720p': {
            'resolution': (1280, 720),
            'fps': 30,
            'video_bitrate': '2.5M',
            'audio_bitrate': '128k',
            'codec': 'libx264',
            'preset': 'medium'
        },
        'high_quality': {
            'resolution': (1920, 1080),
            'fps': 60,
            'video_bitrate': '10M',
            'audio_bitrate': '320k',
            'codec': 'libx264',
            'preset': 'slow'
        }
    }
    
    async def optimize(
        self,
        input: Path,
        output: Path,
        preset: str = 'youtube_1080p'
    ) -> Path:
        """
        Optimize video for platform delivery.
        
        Args:
            input: Input video
            output: Output path
            preset: Quality preset
            
        Returns:
            Output path
        """
        if preset not in self.QUALITY_PRESETS:
            logger.warning(f"Unknown preset {preset}, using youtube_1080p")
            preset = 'youtube_1080p'
        
        logger.info(f"Optimizing video with {preset} preset")
        
        settings = self.QUALITY_PRESETS[preset]
        width, height = settings['resolution']
        
        cmd = [
            'ffmpeg',
            '-y',
            '-i', str(input),
            '-c:v', settings['codec'],
            '-preset', settings['preset'],
            '-b:v', settings['video_bitrate'],
            '-r', str(settings['fps']),
            '-vf', f"scale={width}:{height}",
            '-c:a', 'aac',
            '-b:a', settings['audio_bitrate'],
            '-movflags', '+faststart',  # Enable streaming
            str(output)
        ]
        
        try:
            subprocess.run(cmd, check=True, capture_output=True)
            logger.info(f"Video optimized: {output}")
            return output
        except subprocess.CalledProcessError as e:
            logger.error(f"Optimization failed: {e.stderr.decode()}")
            raise RuntimeError(f"Optimization failed: {e}")

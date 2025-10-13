"""
Color Grading System.

Copyright (c) 2025. All Rights Reserved. Patent Pending.
"""

from typing import Dict
from pathlib import Path
import logging
import subprocess

logger = logging.getLogger(__name__)


class ColorGrading:
    """
    Professional color grading system.
    
    Presets:
    - cinematic: Film-like color grade
    - vintage: Warm, nostalgic look
    - vibrant: Saturated, punchy colors
    - noir: Black and white, high contrast
    
    Example:
        >>> grading = ColorGrading()
        >>> graded = await grading.apply_grade(
        ...     video="input.mp4",
        ...     preset="cinematic",
        ...     output="graded.mp4"
        ... )
    """
    
    PRESETS = {
        'cinematic': {
            'brightness': -0.05,
            'contrast': 1.15,
            'saturation': 0.9,
            'gamma': 1.1
        },
        'vintage': {
            'brightness': 0.1,
            'contrast': 1.1,
            'saturation': 0.8,
            'gamma': 1.2
        },
        'vibrant': {
            'brightness': 0.05,
            'contrast': 1.2,
            'saturation': 1.3,
            'gamma': 1.0
        },
        'noir': {
            'brightness': 0.0,
            'contrast': 1.5,
            'saturation': 0.0,  # Black and white
            'gamma': 1.0
        }
    }
    
    async def apply_grade(
        self,
        video: Path,
        output: Path,
        preset: str = 'cinematic'
    ) -> Path:
        """
        Apply color grade preset.
        
        Args:
            video: Input video
            output: Output path
            preset: Preset name
            
        Returns:
            Output path
        """
        if preset not in self.PRESETS:
            logger.warning(f"Unknown preset {preset}, using cinematic")
            preset = 'cinematic'
        
        logger.info(f"Applying {preset} color grade")
        
        settings = self.PRESETS[preset]
        
        # Build eq filter
        eq_filter = (
            f"eq=brightness={settings['brightness']}:"
            f"contrast={settings['contrast']}:"
            f"saturation={settings['saturation']}:"
            f"gamma={settings['gamma']}"
        )
        
        cmd = [
            'ffmpeg',
            '-y',
            '-i', str(video),
            '-vf', eq_filter,
            '-c:a', 'copy',
            str(output)
        ]
        
        try:
            subprocess.run(cmd, check=True, capture_output=True)
            logger.info(f"Color grade applied: {output}")
            return output
        except subprocess.CalledProcessError as e:
            logger.error(f"Color grading failed: {e.stderr.decode()}")
            raise RuntimeError(f"Color grading failed: {e}")

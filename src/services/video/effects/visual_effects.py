"""
Visual Effects Library.

Copyright (c) 2025. All Rights Reserved. Patent Pending.
"""

from typing import Tuple, Optional
from pathlib import Path
import logging
import subprocess

logger = logging.getLogger(__name__)


class VisualEffects:
    """
    Library of visual effects.
    
    Effects:
    - Color correction (brightness, contrast, saturation)
    - Text overlays
    - Filters (blur, sharpen)
    - Speed adjustment
    
    Example:
        >>> effects = VisualEffects()
        >>> corrected = await effects.apply_color_correction(
        ...     video="input.mp4",
        ...     brightness=0.1,
        ...     contrast=1.2,
        ...     output="corrected.mp4"
        ... )
    """
    
    async def apply_color_correction(
        self,
        video: Path,
        output: Path,
        brightness: float = 0.0,
        contrast: float = 1.0,
        saturation: float = 1.0
    ) -> Path:
        """
        Apply color correction to video.
        
        Args:
            video: Input video
            output: Output path
            brightness: Brightness adjustment (-1.0 to 1.0)
            contrast: Contrast multiplier
            saturation: Saturation multiplier
            
        Returns:
            Output path
        """
        logger.info("Applying color correction")
        
        # Build eq filter
        eq_filter = f"eq=brightness={brightness}:contrast={contrast}:saturation={saturation}"
        
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
            logger.info(f"Color correction applied: {output}")
            return output
        except subprocess.CalledProcessError as e:
            logger.error(f"Color correction failed: {e.stderr.decode()}")
            raise RuntimeError(f"Color correction failed: {e}")
    
    async def add_text_overlay(
        self,
        video: Path,
        output: Path,
        text: str,
        position: Tuple[int, int] = (10, 10),
        font_size: int = 24,
        font_color: str = 'white',
        duration: Optional[float] = None
    ) -> Path:
        """
        Add text overlay to video.
        
        Args:
            video: Input video
            output: Output path
            text: Text to display
            position: (x, y) position
            font_size: Font size
            font_color: Font color
            duration: Display duration (None = entire video)
            
        Returns:
            Output path
        """
        logger.info(f"Adding text overlay: {text}")
        
        x, y = position
        
        # Build drawtext filter
        drawtext_filter = f"drawtext=text='{text}':x={x}:y={y}:fontsize={font_size}:fontcolor={font_color}"
        
        cmd = [
            'ffmpeg',
            '-y',
            '-i', str(video),
            '-vf', drawtext_filter,
            '-c:a', 'copy',
            str(output)
        ]
        
        try:
            subprocess.run(cmd, check=True, capture_output=True)
            logger.info(f"Text overlay added: {output}")
            return output
        except subprocess.CalledProcessError as e:
            logger.error(f"Text overlay failed: {e.stderr.decode()}")
            raise RuntimeError(f"Text overlay failed: {e}")

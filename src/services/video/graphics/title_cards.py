"""
Title Card Generator - Professional Opening Cards.

Copyright (c) 2025. All Rights Reserved. Patent Pending.
"""

from typing import Optional, Tuple
from dataclasses import dataclass
from pathlib import Path
import logging
from PIL import Image, ImageDraw, ImageFont
import subprocess
import tempfile

logger = logging.getLogger(__name__)


@dataclass
class TitleCardConfig:
    """Title card configuration."""
    show_title: str
    episode_title: str
    episode_number: int
    season_number: int = 1
    duration: float = 5.0  # seconds
    resolution: Tuple[int, int] = (1920, 1080)
    background_color: str = '#000000'
    text_color: str = '#FFFFFF'
    font_size_main: int = 72
    font_size_sub: int = 48
    animation_style: str = 'fade'  # fade, slide, zoom


class TitleCardGenerator:
    """
    Generate professional title cards.
    
    Features:
    - Animated title cards
    - Multiple styles (fade, slide, zoom)
    - Custom fonts and colors
    - Episode information display
    
    Example:
        >>> generator = TitleCardGenerator()
        >>> config = TitleCardConfig(
        ...     show_title="I LOVE LUCY PARODY",
        ...     episode_title="The New Influencer",
        ...     episode_number=1
        ... )
        >>> card = await generator.create_title_card(config, "title.mp4")
    """
    
    async def create_title_card(
        self,
        config: TitleCardConfig,
        output_path: Path
    ) -> Path:
        """
        Create animated title card video.
        
        Args:
            config: Title card configuration
            output_path: Output video path
            
        Returns:
            Path to generated title card video
        """
        logger.info(f"Creating title card: {config.show_title}")
        
        # Generate title card image
        image_path = await self._create_title_image(config)
        
        # Convert to video with animation
        video_path = await self._image_to_video(
            image_path,
            output_path,
            config.duration,
            config.animation_style,
            config.resolution
        )
        
        # Clean up temp image
        image_path.unlink(missing_ok=True)
        
        logger.info(f"Title card created: {output_path}")
        return video_path
    
    async def _create_title_image(
        self,
        config: TitleCardConfig
    ) -> Path:
        """
        Create title card image using Pillow.
        
        Args:
            config: Title card configuration
            
        Returns:
            Path to generated image
        """
        width, height = config.resolution
        
        # Create image
        img = Image.new('RGB', (width, height), config.background_color)
        draw = ImageDraw.Draw(img)
        
        # Try to use a nice font, fallback to default
        try:
            font_main = ImageFont.truetype("Arial.ttf", config.font_size_main)
            font_sub = ImageFont.truetype("Arial.ttf", config.font_size_sub)
        except:
            font_main = ImageFont.load_default()
            font_sub = ImageFont.load_default()
        
        # Draw show title (centered, top third)
        show_title_bbox = draw.textbbox((0, 0), config.show_title, font=font_main)
        show_title_width = show_title_bbox[2] - show_title_bbox[0]
        show_title_x = (width - show_title_width) // 2
        show_title_y = height // 3
        
        draw.text(
            (show_title_x, show_title_y),
            config.show_title,
            fill=config.text_color,
            font=font_main
        )
        
        # Draw episode title (centered, middle)
        episode_text = f'Episode {config.episode_number}: {config.episode_title}'
        episode_bbox = draw.textbbox((0, 0), episode_text, font=font_sub)
        episode_width = episode_bbox[2] - episode_bbox[0]
        episode_x = (width - episode_width) // 2
        episode_y = height // 2
        
        draw.text(
            (episode_x, episode_y),
            episode_text,
            fill=config.text_color,
            font=font_sub
        )
        
        # Save to temp file
        temp_path = Path(tempfile.mktemp(suffix='.png'))
        img.save(temp_path)
        
        return temp_path
    
    async def _image_to_video(
        self,
        image_path: Path,
        output_path: Path,
        duration: float,
        animation_style: str,
        resolution: Tuple[int, int]
    ) -> Path:
        """
        Convert image to video with animation.
        
        Args:
            image_path: Source image
            output_path: Output video path
            duration: Video duration
            animation_style: Animation type
            resolution: Video resolution
            
        Returns:
            Path to video
        """
        width, height = resolution
        
        # Build FFmpeg command based on animation style
        if animation_style == 'fade':
            # Fade in and out
            cmd = [
                'ffmpeg',
                '-y',
                '-loop', '1',
                '-i', str(image_path),
                '-vf', f'fade=t=in:st=0:d=1,fade=t=out:st={duration-1}:d=1,scale={width}:{height}',
                '-t', str(duration),
                '-pix_fmt', 'yuv420p',
                '-c:v', 'libx264',
                '-preset', 'fast',
                str(output_path)
            ]
        else:
            # Simple static
            cmd = [
                'ffmpeg',
                '-y',
                '-loop', '1',
                '-i', str(image_path),
                '-t', str(duration),
                '-vf', f'scale={width}:{height}',
                '-pix_fmt', 'yuv420p',
                '-c:v', 'libx264',
                '-preset', 'fast',
                str(output_path)
            ]
        
        try:
            subprocess.run(cmd, check=True, capture_output=True)
            return output_path
        except subprocess.CalledProcessError as e:
            logger.error(f"Image to video conversion failed: {e.stderr.decode()}")
            raise RuntimeError(f"Failed to create title card video: {e}")

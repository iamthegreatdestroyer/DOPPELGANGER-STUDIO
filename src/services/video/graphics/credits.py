"""
Credits Generator - End Credits Creation.

Copyright (c) 2025. All Rights Reserved. Patent Pending.
"""

from typing import List, Dict, Tuple
from dataclasses import dataclass, field
from pathlib import Path
import logging
from PIL import Image, ImageDraw, ImageFont
import subprocess
import tempfile

logger = logging.getLogger(__name__)


@dataclass
class CreditsConfig:
    """Credits configuration."""
    cast: List[Dict[str, str]] = field(default_factory=list)  # [{'character': 'Lucy', 'actor': 'Voice'}]
    crew: List[Dict[str, str]] = field(default_factory=list)  # [{'role': 'Writer', 'name': 'Name'}]
    music: List[str] = field(default_factory=list)
    duration: float = 15.0
    resolution: Tuple[int, int] = (1920, 1080)
    background_color: str = '#000000'
    text_color: str = '#FFFFFF'
    font_size: int = 36
    scroll_speed: float = 50.0  # pixels per second


class CreditsGenerator:
    """
    Generate end credits.
    
    Features:
    - Cast list with character-actor mapping
    - Crew credits
    - Music attribution
    - Scrolling animation
    
    Example:
        >>> generator = CreditsGenerator()
        >>> config = CreditsConfig(
        ...     cast=[{'character': 'Lucy', 'actor': 'AI Voice'}],
        ...     crew=[{'role': 'Created by', 'name': 'DOPPELGANGER STUDIO'}]
        ... )
        >>> credits = await generator.create_credits(config, "credits.mp4")
    """
    
    async def create_credits(
        self,
        config: CreditsConfig,
        output_path: Path
    ) -> Path:
        """
        Create scrolling credits video.
        
        Args:
            config: Credits configuration
            output_path: Output video path
            
        Returns:
            Path to generated credits video
        """
        logger.info("Creating credits")
        
        # Generate credits image (tall)
        image_path = await self._create_credits_image(config)
        
        # Convert to scrolling video
        video_path = await self._image_to_scrolling_video(
            image_path,
            output_path,
            config.duration,
            config.scroll_speed,
            config.resolution
        )
        
        # Clean up temp image
        image_path.unlink(missing_ok=True)
        
        logger.info(f"Credits created: {output_path}")
        return video_path
    
    async def _create_credits_image(
        self,
        config: CreditsConfig
    ) -> Path:
        """
        Create credits image.
        
        Args:
            config: Credits configuration
            
        Returns:
            Path to generated image
        """
        width, height = config.resolution
        
        # Calculate needed height (scrolling)
        line_height = config.font_size + 20
        total_lines = (
            2 +  # Title
            len(config.cast) * 2 +  # Cast (character + actor)
            2 +  # Crew header
            len(config.crew) +
            2 +  # Music header
            len(config.music) +
            5  # Spacing
        )
        image_height = max(height * 2, total_lines * line_height)
        
        # Create image
        img = Image.new('RGB', (width, image_height), config.background_color)
        draw = ImageDraw.Draw(img)
        
        try:
            font = ImageFont.truetype("Arial.ttf", config.font_size)
        except:
            font = ImageFont.load_default()
        
        y = 100
        
        # Cast section
        if config.cast:
            draw.text((width // 2, y), "CAST", fill=config.text_color, font=font, anchor="mt")
            y += line_height * 2
            
            for entry in config.cast:
                char_text = entry.get('character', '')
                actor_text = entry.get('actor', '')
                
                draw.text((width // 2, y), char_text, fill=config.text_color, font=font, anchor="mt")
                y += line_height
                draw.text((width // 2, y), actor_text, fill=config.text_color, font=font, anchor="mt")
                y += line_height * 1.5
        
        # Crew section
        if config.crew:
            y += line_height
            draw.text((width // 2, y), "CREW", fill=config.text_color, font=font, anchor="mt")
            y += line_height * 2
            
            for entry in config.crew:
                role = entry.get('role', '')
                name = entry.get('name', '')
                text = f"{role}: {name}"
                draw.text((width // 2, y), text, fill=config.text_color, font=font, anchor="mt")
                y += line_height
        
        # Music section
        if config.music:
            y += line_height * 2
            draw.text((width // 2, y), "MUSIC", fill=config.text_color, font=font, anchor="mt")
            y += line_height * 2
            
            for track in config.music:
                draw.text((width // 2, y), track, fill=config.text_color, font=font, anchor="mt")
                y += line_height
        
        # Save to temp file
        temp_path = Path(tempfile.mktemp(suffix='.png'))
        img.save(temp_path)
        
        return temp_path
    
    async def _image_to_scrolling_video(
        self,
        image_path: Path,
        output_path: Path,
        duration: float,
        scroll_speed: float,
        resolution: Tuple[int, int]
    ) -> Path:
        """
        Convert image to scrolling video.
        
        Args:
            image_path: Source image
            output_path: Output video path
            duration: Video duration
            scroll_speed: Scroll speed in pixels/second
            resolution: Video resolution
            
        Returns:
            Path to video
        """
        width, height = resolution
        
        # Simple scrolling using crop filter
        cmd = [
            'ffmpeg',
            '-y',
            '-loop', '1',
            '-i', str(image_path),
            '-t', str(duration),
            '-vf', f'crop={width}:{height}:0:y=t*{scroll_speed}',
            '-pix_fmt', 'yuv420p',
            '-c:v', 'libx264',
            '-preset', 'fast',
            str(output_path)
        ]
        
        try:
            subprocess.run(cmd, check=True, capture_output=True)
            return output_path
        except subprocess.CalledProcessError as e:
            logger.error(f"Credits video creation failed: {e.stderr.decode()}")
            raise RuntimeError(f"Failed to create credits video: {e}")

"""
YouTube Formatter - YouTube Compliance and Metadata.

Copyright (c) 2025. All Rights Reserved. Patent Pending.
"""

from typing import List, Optional
from dataclasses import dataclass, field
from pathlib import Path
import logging

logger = logging.getLogger(__name__)


@dataclass
class YouTubeMetadata:
    """YouTube video metadata."""
    title: str
    description: str
    tags: List[str] = field(default_factory=list)
    category: str = 'Entertainment'
    privacy: str = 'public'  # public, unlisted, private
    thumbnail_path: Optional[Path] = None
    playlist: Optional[str] = None


class YouTubeFormatter:
    """
    Ensure YouTube format compliance.
    
    YouTube Requirements:
    - Container: MP4
    - Video codec: H.264
    - Audio codec: AAC
    - Resolution: 1080p or 720p
    - Frame rate: 30 or 60 fps
    - Aspect ratio: 16:9
    - Max file size: 128GB
    - Max duration: 12 hours
    
    Example:
        >>> formatter = YouTubeFormatter()
        >>> compliant = await formatter.ensure_compliance(
        ...     input="video.mp4",
        ...     output="youtube_ready.mp4"
        ... )
    """
    
    async def ensure_compliance(
        self,
        input: Path,
        output: Path,
        resolution: str = '1080p'
    ) -> Path:
        """
        Ensure video meets YouTube requirements.
        
        Args:
            input: Input video
            output: Output path
            resolution: Target resolution (1080p or 720p)
            
        Returns:
            YouTube-compliant video path
        """
        logger.info(f"Ensuring YouTube compliance: {resolution}")
        
        # Use ExportOptimizer with YouTube preset
        from src.services.video.export.optimizer import ExportOptimizer
        
        optimizer = ExportOptimizer()
        preset = f'youtube_{resolution}'
        
        return await optimizer.optimize(input, output, preset)
    
    def validate_metadata(self, metadata: YouTubeMetadata) -> bool:
        """
        Validate YouTube metadata.
        
        Args:
            metadata: Metadata to validate
            
        Returns:
            True if valid
        """
        # Check title length
        if len(metadata.title) > 100:
            logger.warning("Title exceeds 100 characters")
            return False
        
        # Check description length
        if len(metadata.description) > 5000:
            logger.warning("Description exceeds 5000 characters")
            return False
        
        # Check tags
        if len(metadata.tags) > 500:
            logger.warning("Too many tags (max 500)")
            return False
        
        # Check privacy
        if metadata.privacy not in ['public', 'unlisted', 'private']:
            logger.warning("Invalid privacy setting")
            return False
        
        return True

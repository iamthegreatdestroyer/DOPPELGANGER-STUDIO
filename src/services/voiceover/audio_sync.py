"""
Audio Sync - Synchronize audio with video.

Copyright (c) 2025. All Rights Reserved. Patent Pending.
"""

from typing import List, Tuple
from pathlib import Path
import subprocess
import logging

logger = logging.getLogger(__name__)


class AudioSync:
    """
    Synchronize voiceover audio with video.
    
    Uses FFmpeg to overlay audio tracks on video.
    """
    
    def __init__(self, ffmpeg_path: str = "ffmpeg"):
        """
        Initialize audio sync.
        
        Args:
            ffmpeg_path: Path to ffmpeg executable
        """
        self.ffmpeg_path = ffmpeg_path
        logger.info("AudioSync initialized")
    
    async def sync_audio_to_video(
        self,
        video_path: Path,
        audio_path: Path,
        output_path: Path,
        offset: float = 0.0
    ) -> Path:
        """
        Add audio track to video.
        
        Args:
            video_path: Input video
            audio_path: Audio to add
            output_path: Output video
            offset: Audio offset in seconds
            
        Returns:
            Path to output video
        """
        cmd = [
            self.ffmpeg_path,
            '-i', str(video_path),
            '-i', str(audio_path),
            '-c:v', 'copy',
            '-c:a', 'aac',
            '-map', '0:v:0',
            '-map', '1:a:0',
        ]
        
        if offset > 0:
            cmd.extend(['-itsoffset', str(offset)])
        
        cmd.append(str(output_path))
        
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True
        )
        
        if result.returncode == 0:
            logger.info(f"Audio synced: {output_path.name}")
            return output_path
        else:
            logger.error(f"FFmpeg error: {result.stderr}")
            raise RuntimeError(f"Audio sync failed: {result.stderr}")
    
    def generate_subtitles(
        self,
        dialogue: List[Tuple[float, float, str]],
        output_path: Path
    ):
        """
        Generate SRT subtitle file.
        
        Args:
            dialogue: List of (start, end, text) tuples
            output_path: SRT file path
        """
        with open(output_path, 'w', encoding='utf-8') as f:
            for i, (start, end, text) in enumerate(dialogue, 1):
                f.write(f"{i}\n")
                f.write(f"{self._format_timestamp(start)} --> {self._format_timestamp(end)}\n")
                f.write(f"{text}\n\n")
        
        logger.info(f"Subtitles generated: {output_path.name}")
    
    def _format_timestamp(self, seconds: float) -> str:
        """Format timestamp for SRT."""
        hours = int(seconds // 3600)
        minutes = int((seconds % 3600) // 60)
        secs = int(seconds % 60)
        millis = int((seconds % 1) * 1000)
        
        return f"{hours:02d}:{minutes:02d}:{secs:02d},{millis:03d}"

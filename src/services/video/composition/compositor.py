"""
Video Compositor - Combine Animation and Audio.

Compose final video from animation frames and audio tracks using FFmpeg.

Copyright (c) 2025. All Rights Reserved. Patent Pending.
"""

from typing import Dict, Optional, Tuple
from dataclasses import dataclass
from pathlib import Path
import logging
import subprocess
import shutil

logger = logging.getLogger(__name__)


@dataclass
class VideoComposition:
    """Video composition configuration."""
    video_path: Path
    audio_path: Path
    output_path: Path
    resolution: Tuple[int, int] = (1920, 1080)  # width, height
    fps: int = 30
    codec: str = 'libx264'
    bitrate: str = '5M'
    audio_codec: str = 'aac'
    audio_bitrate: str = '192k'
    preset: str = 'medium'  # ultrafast, fast, medium, slow, veryslow


class VideoCompositor:
    """
    Video composition engine using FFmpeg.
    
    Features:
    - Merge animation and audio
    - Audio-video synchronization
    - Resolution scaling
    - Quality optimization
    - Format conversion
    
    Example:
        >>> compositor = VideoCompositor()
        >>> result = await compositor.compose(
        ...     animation_path="animation.mp4",
        ...     audio_path="audio.mp3",
        ...     output_path="final.mp4"
        ... )
    """
    
    def __init__(self):
        """Initialize video compositor."""
        # Verify FFmpeg is available
        if not self._check_ffmpeg():
            raise RuntimeError("FFmpeg not found. Please install FFmpeg.")
        
        logger.info("Video compositor initialized")
    
    def _check_ffmpeg(self) -> bool:
        """Check if FFmpeg is available."""
        return shutil.which('ffmpeg') is not None
    
    async def compose(
        self,
        animation_path: Path,
        audio_path: Path,
        output_path: Path,
        resolution: Tuple[int, int] = (1920, 1080),
        fps: int = 30,
        quality_preset: str = 'medium'
    ) -> Path:
        """
        Compose video from animation and audio.
        
        Args:
            animation_path: Path to animation video
            audio_path: Path to audio file
            output_path: Path for output video
            resolution: Target resolution (width, height)
            fps: Target frame rate
            quality_preset: FFmpeg preset (faster = lower quality, larger file)
            
        Returns:
            Path to composed video
            
        Raises:
            FileNotFoundError: If input files don't exist
            RuntimeError: If FFmpeg fails
        """
        animation_path = Path(animation_path)
        audio_path = Path(audio_path)
        output_path = Path(output_path)
        
        # Verify inputs exist
        if not animation_path.exists():
            raise FileNotFoundError(f"Animation not found: {animation_path}")
        if not audio_path.exists():
            raise FileNotFoundError(f"Audio not found: {audio_path}")
        
        # Ensure output directory exists
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        logger.info(f"Composing video: {animation_path.name} + {audio_path.name}")
        
        # Build FFmpeg command
        cmd = self._build_compose_command(
            animation_path,
            audio_path,
            output_path,
            resolution,
            fps,
            quality_preset
        )
        
        # Execute FFmpeg
        try:
            subprocess.run(cmd, check=True, capture_output=True)
            logger.info(f"Video composed: {output_path}")
            return output_path
        except subprocess.CalledProcessError as e:
            logger.error(f"FFmpeg failed: {e.stderr.decode()}")
            raise RuntimeError(f"Video composition failed: {e}")
    
    def _build_compose_command(
        self,
        video_path: Path,
        audio_path: Path,
        output_path: Path,
        resolution: Tuple[int, int],
        fps: int,
        preset: str
    ) -> list:
        """
        Build FFmpeg command for composition.
        
        Args:
            video_path: Input video
            audio_path: Input audio
            output_path: Output path
            resolution: Target resolution
            fps: Target frame rate
            preset: Quality preset
            
        Returns:
            FFmpeg command as list
        """
        width, height = resolution
        
        cmd = [
            'ffmpeg',
            '-y',  # Overwrite output
            '-i', str(video_path),  # Input video
            '-i', str(audio_path),  # Input audio
            '-c:v', 'libx264',  # Video codec
            '-preset', preset,  # Encoding preset
            '-b:v', '5M',  # Video bitrate
            '-r', str(fps),  # Frame rate
            '-vf', f'scale={width}:{height}',  # Scale to resolution
            '-c:a', 'aac',  # Audio codec
            '-b:a', '192k',  # Audio bitrate
            '-shortest',  # Match shortest stream duration
            str(output_path)
        ]
        
        return cmd
    
    async def compose_with_config(
        self,
        config: VideoComposition
    ) -> Path:
        """
        Compose video using configuration object.
        
        Args:
            config: VideoComposition configuration
            
        Returns:
            Path to composed video
        """
        return await self.compose(
            animation_path=config.video_path,
            audio_path=config.audio_path,
            output_path=config.output_path,
            resolution=config.resolution,
            fps=config.fps,
            quality_preset=config.preset
        )
    
    async def replace_audio(
        self,
        video_path: Path,
        new_audio_path: Path,
        output_path: Path
    ) -> Path:
        """
        Replace audio in existing video.
        
        Args:
            video_path: Source video
            new_audio_path: New audio file
            output_path: Output path
            
        Returns:
            Path to video with replaced audio
        """
        cmd = [
            'ffmpeg',
            '-y',
            '-i', str(video_path),
            '-i', str(new_audio_path),
            '-c:v', 'copy',  # Copy video without re-encoding
            '-c:a', 'aac',
            '-b:a', '192k',
            '-map', '0:v:0',  # Video from first input
            '-map', '1:a:0',  # Audio from second input
            '-shortest',
            str(output_path)
        ]
        
        try:
            subprocess.run(cmd, check=True, capture_output=True)
            logger.info(f"Audio replaced: {output_path}")
            return output_path
        except subprocess.CalledProcessError as e:
            logger.error(f"Audio replacement failed: {e.stderr.decode()}")
            raise RuntimeError(f"Audio replacement failed: {e}")
    
    async def get_video_info(self, video_path: Path) -> Dict:
        """
        Get video information using FFprobe.
        
        Args:
            video_path: Path to video
            
        Returns:
            Dictionary with video info (duration, resolution, fps, codec)
        """
        cmd = [
            'ffprobe',
            '-v', 'quiet',
            '-print_format', 'json',
            '-show_format',
            '-show_streams',
            str(video_path)
        ]
        
        try:
            result = subprocess.run(cmd, check=True, capture_output=True)
            import json
            data = json.loads(result.stdout)
            
            # Extract video stream info
            video_stream = next(
                (s for s in data.get('streams', []) if s.get('codec_type') == 'video'),
                None
            )
            
            if not video_stream:
                return {}
            
            return {
                'duration': float(data.get('format', {}).get('duration', 0)),
                'width': video_stream.get('width', 0),
                'height': video_stream.get('height', 0),
                'fps': eval(video_stream.get('r_frame_rate', '0/1')),
                'codec': video_stream.get('codec_name', 'unknown')
            }
        except Exception as e:
            logger.error(f"Failed to get video info: {e}")
            return {}

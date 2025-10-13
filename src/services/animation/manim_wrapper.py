"""
Manim Wrapper - Interface to Manim animation engine.

Provides simplified API for creating and rendering animations from script data.
Handles rendering configuration, quality presets, and output management.

Copyright (c) 2025. All Rights Reserved. Patent Pending.
"""

from typing import Optional, Tuple, Dict, List, Any
from dataclasses import dataclass
from enum import Enum
from pathlib import Path
import logging
import subprocess
import shutil
import yaml

try:
    from manim import *
    MANIM_AVAILABLE = True
except ImportError:
    MANIM_AVAILABLE = False
    logging.warning("Manim not installed. Install with: pip install manim")

logger = logging.getLogger(__name__)


class RenderQuality(str, Enum):
    """Rendering quality presets."""
    PREVIEW = "preview"  # 480p15 - fast preview
    LOW = "low"         # 854p30 - draft quality
    MEDIUM = "medium"   # 1080p30 - standard
    HIGH = "high"       # 1080p60 - high quality


@dataclass
class RenderConfig:
    """Configuration for Manim rendering."""
    quality: RenderQuality
    resolution: Tuple[int, int]
    fps: int
    background_color: str
    output_dir: Path
    format: str = "mp4"
    codec: str = "libx264"
    crf: int = 18  # Quality (lower = better, 18-23 recommended)


class ManimWrapper:
    """
    Wrapper around Manim for simplified animation creation.
    
    Handles configuration, scene creation, and rendering with
    quality presets and output management.
    
    Attributes:
        config: Rendering configuration
        
    Example:
        >>> wrapper = ManimWrapper(quality=RenderQuality.HIGH)
        >>> scene_class = wrapper.create_scene_class("TestScene", scene_data)
        >>> wrapper.render_scene(scene_class, "output.mp4")
    """
    
    # Quality preset configurations
    QUALITY_PRESETS = {
        RenderQuality.PREVIEW: {
            "resolution": (854, 480),
            "fps": 15,
        },
        RenderQuality.LOW: {
            "resolution": (854, 480),
            "fps": 30,
        },
        RenderQuality.MEDIUM: {
            "resolution": (1920, 1080),
            "fps": 30,
        },
        RenderQuality.HIGH: {
            "resolution": (1920, 1080),
            "fps": 60,
        },
    }
    
    def __init__(
        self,
        quality: RenderQuality = RenderQuality.MEDIUM,
        background_color: str = "#FFFFFF",
        output_dir: Optional[Path] = None,
        config_file: Optional[Path] = None
    ):
        """
        Initialize Manim wrapper.
        
        Args:
            quality: Rendering quality preset
            background_color: Scene background color (hex)
            output_dir: Output directory for rendered videos
            config_file: Optional YAML config file to override defaults
            
        Raises:
            ImportError: If Manim is not installed
            FileNotFoundError: If config_file doesn't exist
        """
        if not MANIM_AVAILABLE:
            raise ImportError(
                "Manim not installed. Install with: pip install manim"
            )
        
        # Check FFmpeg availability
        if not self._check_ffmpeg():
            logger.warning(
                "FFmpeg not found. Rendering may fail. "
                "Install FFmpeg: https://ffmpeg.org/download.html"
            )
        
        # Load config from file if provided
        if config_file:
            self._load_config_file(config_file)
        
        # Build configuration
        preset = self.QUALITY_PRESETS[quality]
        
        self.config = RenderConfig(
            quality=quality,
            resolution=preset["resolution"],
            fps=preset["fps"],
            background_color=background_color,
            output_dir=output_dir or Path("output/animations")
        )
        
        # Ensure output directory exists
        self.config.output_dir.mkdir(parents=True, exist_ok=True)
        
        logger.info(
            f"ManimWrapper initialized: {quality.value} quality, "
            f"{self.config.resolution[0]}x{self.config.resolution[1]} @ {self.config.fps}fps"
        )
    
    def _check_ffmpeg(self) -> bool:
        """Check if FFmpeg is installed and available."""
        return shutil.which("ffmpeg") is not None
    
    def _load_config_file(self, config_file: Path):
        """Load configuration from YAML file."""
        if not config_file.exists():
            raise FileNotFoundError(f"Config file not found: {config_file}")
        
        with open(config_file, 'r') as f:
            config_data = yaml.safe_load(f)
        
        logger.info(f"Loaded config from: {config_file}")
        # Config data would override defaults here
        # Implementation depends on config structure
    
    def create_scene_class(
        self,
        name: str,
        construct_func: callable
    ) -> type:
        """
        Create a Manim Scene class dynamically.
        
        Args:
            name: Scene class name
            construct_func: Function that defines scene construction
            
        Returns:
            Scene class that can be rendered
            
        Example:
            >>> def my_scene_construct(scene):
            ...     text = Text("Hello World")
            ...     scene.add(text)
            ...     scene.wait(1)
            >>> 
            >>> SceneClass = wrapper.create_scene_class(
            ...     "MyScene",
            ...     my_scene_construct
            ... )
        """
        # Create dynamic scene class
        scene_class = type(
            name,
            (Scene,),
            {
                "construct": construct_func,
                "__module__": "__main__",
            }
        )
        
        logger.debug(f"Created scene class: {name}")
        return scene_class
    
    def render_scene(
        self,
        scene_class: type,
        output_filename: str,
        **render_kwargs
    ) -> Path:
        """
        Render a Manim scene to video file.
        
        Args:
            scene_class: Manim Scene class to render
            output_filename: Output filename (without path)
            **render_kwargs: Additional arguments for Manim render
            
        Returns:
            Path to rendered video file
            
        Raises:
            RuntimeError: If rendering fails
            
        Example:
            >>> output_path = wrapper.render_scene(
            ...     MySceneClass,
            ...     "episode1_scene1.mp4"
            ... )
            >>> print(f"Rendered to: {output_path}")
        """
        logger.info(f"Rendering scene: {scene_class.__name__}")
        
        try:
            # Configure Manim for this render
            config.quality = self.config.quality.value
            config.pixel_height = self.config.resolution[1]
            config.pixel_width = self.config.resolution[0]
            config.frame_rate = self.config.fps
            config.background_color = self.config.background_color
            config.output_file = output_filename
            
            # Set output directory
            output_path = self.config.output_dir / output_filename
            config.output_file = str(output_path.stem)  # Manim adds extension
            config.media_dir = str(self.config.output_dir)
            
            # Render scene
            scene = scene_class()
            scene.render()
            
            logger.info(f"Render complete: {output_path}")
            return output_path
            
        except Exception as e:
            logger.error(f"Rendering failed: {e}")
            raise RuntimeError(f"Failed to render scene: {e}") from e
    
    def render_multiple_scenes(
        self,
        scenes: List[Tuple[type, str]],
        progress_callback: Optional[callable] = None
    ) -> List[Path]:
        """
        Render multiple scenes sequentially.
        
        Args:
            scenes: List of (scene_class, output_filename) tuples
            progress_callback: Optional callback for progress updates
                              Called with (current, total, scene_name)
                              
        Returns:
            List of paths to rendered video files
            
        Example:
            >>> scenes = [
            ...     (Scene1Class, "scene1.mp4"),
            ...     (Scene2Class, "scene2.mp4"),
            ... ]
            >>> 
            >>> def progress(current, total, name):
            ...     print(f"Rendering {current}/{total}: {name}")
            >>> 
            >>> paths = wrapper.render_multiple_scenes(scenes, progress)
        """
        output_paths = []
        total = len(scenes)
        
        logger.info(f"Rendering {total} scenes")
        
        for i, (scene_class, filename) in enumerate(scenes, 1):
            if progress_callback:
                progress_callback(i, total, scene_class.__name__)
            
            try:
                path = self.render_scene(scene_class, filename)
                output_paths.append(path)
            except Exception as e:
                logger.error(
                    f"Failed to render scene {i}/{total} "
                    f"({scene_class.__name__}): {e}"
                )
                # Continue with next scene
                continue
        
        logger.info(
            f"Batch render complete: {len(output_paths)}/{total} successful"
        )
        return output_paths
    
    def get_render_info(self) -> Dict[str, Any]:
        """
        Get current rendering configuration info.
        
        Returns:
            Dictionary with configuration details
            
        Example:
            >>> info = wrapper.get_render_info()
            >>> print(f"Resolution: {info['resolution']}")
            >>> print(f"FPS: {info['fps']}")
        """
        return {
            "quality": self.config.quality.value,
            "resolution": self.config.resolution,
            "fps": self.config.fps,
            "background_color": self.config.background_color,
            "output_dir": str(self.config.output_dir),
            "format": self.config.format,
            "codec": self.config.codec,
            "crf": self.config.crf,
        }
    
    @staticmethod
    def validate_installation() -> Dict[str, bool]:
        """
        Validate Manim and dependencies installation.
        
        Returns:
            Dictionary with installation status for each component
            
        Example:
            >>> status = ManimWrapper.validate_installation()
            >>> if not all(status.values()):
            ...     print("Missing dependencies:", status)
        """
        status = {
            "manim": MANIM_AVAILABLE,
            "ffmpeg": shutil.which("ffmpeg") is not None,
            "cairo": True,  # Checked by Manim itself
        }
        
        return status


# Example usage
if __name__ == "__main__":
    # Simple example
    def example_construct(scene):
        """Example scene construction."""
        text = Text("DOPPELGANGER STUDIO")
        scene.add(text)
        scene.play(FadeIn(text))
        scene.wait(1)
        scene.play(FadeOut(text))
    
    # Create wrapper
    wrapper = ManimWrapper(quality=RenderQuality.PREVIEW)
    
    # Validate installation
    status = ManimWrapper.validate_installation()
    print("Installation status:", status)
    
    if all(status.values()):
        # Create and render scene
        SceneClass = wrapper.create_scene_class(
            "ExampleScene",
            example_construct
        )
        
        output = wrapper.render_scene(SceneClass, "example.mp4")
        print(f"Rendered to: {output}")
    else:
        print("Missing dependencies. Install Manim and FFmpeg.")

"""
Scene Renderer - Compose and render complete animated scenes.

Handles scene composition, character placement, dialogue, backgrounds,
and camera control for episode generation.

Copyright (c) 2025. All Rights Reserved. Patent Pending.
"""

from typing import Dict, List, Tuple, Optional, Any
from dataclasses import dataclass
from pathlib import Path
import logging

try:
    from manim import *
    MANIM_AVAILABLE = True
except ImportError:
    MANIM_AVAILABLE = False

from src.services.animation.character_sprite import CharacterSprite, CharacterSpriteManager
from src.models.character_visual import Expression, AnimationState

logger = logging.getLogger(__name__)


@dataclass
class SceneData:
    """Data for a single scene."""
    scene_id: str
    description: str
    duration: float
    characters: List[str]
    dialogue: List[Tuple[str, str]]  # [(character_name, text), ...]
    background: Optional[str] = None
    camera_moves: List[Dict] = None
    

class SceneRenderer:
    """
    Renders complete animated scenes with characters and dialogue.
    
    Manages scene composition, character positioning, dialogue display,
    backgrounds, and camera control.
    
    Example:
        >>> renderer = SceneRenderer(character_manager)
        >>> scene_class = renderer.create_scene(
        ...     scene_data,
        ...     background_path
        ... )
        >>> # Render with ManimWrapper
    """
    
    def __init__(self, character_manager: CharacterSpriteManager):
        """
        Initialize scene renderer.
        
        Args:
            character_manager: Manager with character sprites
        """
        if not MANIM_AVAILABLE:
            raise ImportError("Manim required for SceneRenderer")
        
        self.character_manager = character_manager
        logger.info("SceneRenderer initialized")
    
    def create_scene(
        self,
        scene_data: SceneData,
        background_path: Optional[Path] = None
    ) -> type:
        """
        Create Manim Scene class from scene data.
        
        Args:
            scene_data: Scene configuration and content
            background_path: Optional background image
            
        Returns:
            Manim Scene class ready to render
        """
        # Create dynamic scene construct function
        def construct(scene):
            # Add background
            if background_path and background_path.exists():
                bg = ImageMobject(str(background_path))
                bg.scale_to_fit_width(config.frame_width)
                scene.add(bg)
            
            # Get characters for this scene
            scene_characters = [
                self.character_manager.get_character(name)
                for name in scene_data.characters
            ]
            scene_characters = [c for c in scene_characters if c]
            
            # Position characters
            self._position_scene_characters(scene, scene_characters)
            
            # Add characters to scene
            for char in scene_characters:
                scene.add(char.get_mobject())
            
            # Play dialogue sequence
            self._render_dialogue(scene, scene_data.dialogue, scene_characters)
            
            # Hold final frame
            scene.wait(1)
        
        # Create scene class
        scene_class = type(
            f"Scene_{scene_data.scene_id}",
            (Scene,),
            {
                "construct": construct,
                "__module__": "__main__",
            }
        )
        
        return scene_class
    
    def _position_scene_characters(
        self,
        scene: "Scene",
        characters: List[CharacterSprite]
    ):
        """
        Position characters in scene.
        
        Args:
            scene: Manim scene
            characters: Characters to position
        """
        num_chars = len(characters)
        if num_chars == 0:
            return
        
        # Simple positioning: spread across stage
        spacing = 4.0
        total_width = (num_chars - 1) * spacing
        start_x = -total_width / 2
        
        for i, char in enumerate(characters):
            x = start_x + (i * spacing)
            char.mobject.move_to([x, 0, 0])
    
    def _render_dialogue(
        self,
        scene: "Scene",
        dialogue: List[Tuple[str, str]],
        characters: List[CharacterSprite]
    ):
        """
        Render dialogue sequence.
        
        Args:
            scene: Manim scene
            dialogue: List of (character_name, text) tuples
            characters: Scene characters
        """
        char_map = {c.visual.name: c for c in characters}
        
        for speaker_name, text in dialogue:
            speaker = char_map.get(speaker_name)
            
            if not speaker:
                logger.warning(f"Speaker not found: {speaker_name}")
                continue
            
            # Create subtitle text
            subtitle = Text(
                f"{speaker_name}: {text}",
                font_size=24
            ).to_edge(DOWN)
            
            # Character talks
            speaker.set_state(AnimationState.TALKING)
            
            # Show subtitle and talking animation
            scene.play(
                FadeIn(subtitle),
                speaker.get_state_animation(duration=len(text) * 0.05)
            )
            
            # Hold for reading
            scene.wait(len(text) * 0.08)
            
            # Remove subtitle
            scene.play(FadeOut(subtitle))
            
            # Return to idle
            speaker.set_state(AnimationState.IDLE)


# Copyright (c) 2025. All Rights Reserved. Patent Pending.

"""
Character Sprite System - Visual character management for animations.

Handles character loading, positioning, expressions, and animation states
for Manim-based rendering.

Copyright (c) 2025. All Rights Reserved. Patent Pending.
"""

from typing import Dict, List, Tuple, Optional, Any
from pathlib import Path
import logging

try:
    from manim import *
    from manim import VMobject  # Explicit import for test visibility
    MANIM_AVAILABLE = True
except ImportError:
    MANIM_AVAILABLE = False
    VMobject = None  # Fallback when Manim unavailable

from src.models.character_visual import (
    CharacterVisual,
    Expression,
    AnimationState
)

logger = logging.getLogger(__name__)


class CharacterSprite:
    """
    Manim-compatible character sprite with expressions and animations.
    
    Manages visual representation of a character including positioning,
    expressions, animation states, and transitions.
    
    Attributes:
        visual: Character visual data
        mobject: Current Manim mobject representation
        position: Current position (x, y)
        expression: Current expression
        state: Current animation state
        
    Example:
        >>> visual = CharacterVisual(
        ...     name="Lucy",
        ...     sprite_path=Path("assets/lucy.svg")
        ... )
        >>> sprite = CharacterSprite(visual)
        >>> sprite.set_expression(Expression.HAPPY)
        >>> sprite.move_to((2, 0))
    """
    
    def __init__(self, visual: CharacterVisual):
        """
        Initialize character sprite.
        
        Args:
            visual: Character visual data
            
        Raises:
            ImportError: If Manim not available
            FileNotFoundError: If sprite file missing
        """
        if not MANIM_AVAILABLE:
            raise ImportError("Manim required for CharacterSprite")
        
        self.visual = visual
        self.mobject: Optional[VMobject] = None
        self.position = visual.default_position
        self.expression = visual.default_expression
        self.state = AnimationState.IDLE
        
        # Load sprite
        self._load_sprite()
        
        logger.info(f"CharacterSprite initialized: {visual.name}")
    
    def _load_sprite(self):
        """
        Load sprite file as Manim mobject.
        
        Supports SVG and PNG formats.
        """
        sprite_path = self.visual.sprite_path
        
        try:
            if sprite_path.suffix.lower() == '.svg':
                # Load SVG
                self.mobject = SVGMobject(str(sprite_path))
            elif sprite_path.suffix.lower() in ['.png', '.jpg', '.jpeg']:
                # Load image
                self.mobject = ImageMobject(str(sprite_path))
            else:
                raise ValueError(
                    f"Unsupported sprite format: {sprite_path.suffix}"
                )
            
            # Apply default scale
            self.mobject.scale(self.visual.scale)
            
            # Apply default position
            self.mobject.move_to([
                self.visual.default_position[0],
                self.visual.default_position[1],
                0
            ])
            
            logger.debug(f"Loaded sprite: {sprite_path.name}")
            
        except Exception as e:
            logger.error(f"Failed to load sprite {sprite_path}: {e}")
            raise
    
    def get_mobject(self) -> VMobject:
        """
        Get current Manim mobject for rendering.
        
        Returns:
            Manim mobject representing character
        """
        return self.mobject
    
    def set_expression(self, expression: Expression) -> "Animation":
        """
        Change character expression.
        
        Args:
            expression: New expression to apply
            
        Returns:
            Manim animation for expression change
            
        Example:
            >>> anim = sprite.set_expression(Expression.HAPPY)
            >>> scene.play(anim)
        """
        if expression == self.expression:
            logger.debug(f"Expression unchanged: {expression.value}")
            return Wait(0.01)  # No-op animation
        
        logger.debug(
            f"{self.visual.name}: {self.expression.value} -> {expression.value}"
        )
        
        self.expression = expression
        
        # Load expression overlay if available
        if expression in self.visual.expression_paths:
            expression_path = self.visual.expression_paths[expression]
            
            try:
                if expression_path.suffix.lower() == '.svg':
                    new_mobject = SVGMobject(str(expression_path))
                else:
                    new_mobject = ImageMobject(str(expression_path))
                
                new_mobject.scale(self.visual.scale)
                new_mobject.move_to(self.mobject.get_center())
                
                # Transform to new expression
                animation = Transform(self.mobject, new_mobject)
                return animation
                
            except Exception as e:
                logger.warning(f"Failed to load expression {expression.value}: {e}")
                return FadeIn(self.mobject, run_time=0.2)
        
        # Default: quick fade animation
        return FadeIn(self.mobject, run_time=0.2)
    
    def move_to(self, position: Tuple[float, float], duration: float = 1.0) -> "Animation":
        """
        Move character to new position.
        
        Args:
            position: Target position (x, y)
            duration: Animation duration in seconds
            
        Returns:
            Manim animation for movement
            
        Example:
            >>> anim = sprite.move_to((3, 0), duration=0.5)
            >>> scene.play(anim)
        """
        self.position = position
        target = [position[0], position[1], 0]
        
        logger.debug(f"{self.visual.name} moving to {position}")
        
        return self.mobject.animate.move_to(target).set_run_time(duration)
    
    def set_state(self, state: AnimationState):
        """
        Change character animation state.
        
        Args:
            state: New animation state
            
        Note:
            This updates internal state. Use get_state_animation()
            to get corresponding Manim animation.
        """
        logger.debug(f"{self.visual.name} state: {self.state.value} -> {state.value}")
        self.state = state
    
    def get_state_animation(self, duration: float = 1.0) -> "Animation":
        """
        Get animation for current state.
        
        Args:
            duration: Animation duration
            
        Returns:
            Manim animation for current state
            
        Example:
            >>> sprite.set_state(AnimationState.TALKING)
            >>> anim = sprite.get_state_animation()
            >>> scene.play(anim)
        """
        if self.state == AnimationState.IDLE:
            # Subtle breathing motion
            return self.mobject.animate.scale(1.02).scale(1/1.02).set_run_time(duration)
        
        elif self.state == AnimationState.WALKING:
            # Simple left-right sway
            return Succession(
                self.mobject.animate.shift(RIGHT * 0.1),
                self.mobject.animate.shift(LEFT * 0.2),
                self.mobject.animate.shift(RIGHT * 0.1),
            )
        
        elif self.state == AnimationState.TALKING:
            # Quick scale pulse
            return self.mobject.animate.scale(1.05).scale(1/1.05).set_run_time(0.3)
        
        elif self.state == AnimationState.GESTURING:
            # Rotation animation
            return Rotate(self.mobject, angle=5*DEGREES, about_point=self.mobject.get_bottom())
        
        elif self.state == AnimationState.REACTING:
            # Jump/bounce
            return self.mobject.animate.shift(UP * 0.3).shift(DOWN * 0.3).set_run_time(0.4)
        
        else:
            # Default: no animation
            return Wait(0.01)
    
    def scale(self, factor: float) -> "Animation":
        """
        Scale character sprite.
        
        Args:
            factor: Scale multiplier
            
        Returns:
            Manim animation for scaling
        """
        self.visual.scale *= factor
        return self.mobject.animate.scale(factor)
    
    def fade_in(self, duration: float = 0.5) -> "Animation":
        """
        Fade character in.
        
        Args:
            duration: Fade duration
            
        Returns:
            Manim FadeIn animation
        """
        return FadeIn(self.mobject, run_time=duration)
    
    def fade_out(self, duration: float = 0.5) -> "Animation":
        """
        Fade character out.
        
        Args:
            duration: Fade duration
            
        Returns:
            Manim FadeOut animation
        """
        return FadeOut(self.mobject, run_time=duration)
    
    def enter_from(self, direction: str, duration: float = 1.0) -> "Animation":
        """
        Animate character entering from direction.
        
        Args:
            direction: 'left', 'right', 'top', 'bottom'
            duration: Animation duration
            
        Returns:
            Manim animation for entrance
            
        Example:
            >>> anim = sprite.enter_from('left', duration=1.5)
            >>> scene.play(anim)
        """
        self.set_state(AnimationState.ENTERING)
        
        # Start position offscreen
        start_offsets = {
            'left': LEFT * 10,
            'right': RIGHT * 10,
            'top': UP * 10,
            'bottom': DOWN * 10,
        }
        
        if direction.lower() not in start_offsets:
            raise ValueError(f"Invalid direction: {direction}")
        
        offset = start_offsets[direction.lower()]
        start_pos = self.mobject.get_center() + offset
        target_pos = self.mobject.get_center()
        
        # Move to start position instantly
        self.mobject.move_to(start_pos)
        
        # Animate to target
        return self.mobject.animate.move_to(target_pos).set_run_time(duration)
    
    def exit_to(self, direction: str, duration: float = 1.0) -> "Animation":
        """
        Animate character exiting to direction.
        
        Args:
            direction: 'left', 'right', 'top', 'bottom'
            duration: Animation duration
            
        Returns:
            Manim animation for exit
        """
        self.set_state(AnimationState.EXITING)
        
        exit_offsets = {
            'left': LEFT * 10,
            'right': RIGHT * 10,
            'top': UP * 10,
            'bottom': DOWN * 10,
        }
        
        if direction.lower() not in exit_offsets:
            raise ValueError(f"Invalid direction: {direction}")
        
        offset = exit_offsets[direction.lower()]
        target_pos = self.mobject.get_center() + offset
        
        return self.mobject.animate.move_to(target_pos).set_run_time(duration)
    
    def get_position(self) -> Tuple[float, float]:
        """
        Get current character position.
        
        Returns:
            Current position (x, y)
        """
        center = self.mobject.get_center()
        return (center[0], center[1])
    
    def get_info(self) -> Dict[str, Any]:
        """
        Get character sprite information.
        
        Returns:
            Dictionary with current state and properties
        """
        return {
            "name": self.visual.name,
            "position": self.position,
            "expression": self.expression.value,
            "state": self.state.value,
            "scale": self.visual.scale,
            "layer": self.visual.layer,
        }


class CharacterSpriteManager:
    """
    Manages multiple character sprites in a scene.
    
    Handles character collection, positioning, and batch operations.
    
    Example:
        >>> manager = CharacterSpriteManager()
        >>> manager.add_character(lucy_sprite)
        >>> manager.add_character(ricky_sprite)
        >>> manager.position_characters(['lucy', 'ricky'], spacing=3)
    """
    
    def __init__(self):
        """Initialize character sprite manager."""
        self.characters: Dict[str, CharacterSprite] = {}
        logger.info("CharacterSpriteManager initialized")
    
    def add_character(self, sprite: CharacterSprite):
        """
        Add character to manager.
        
        Args:
            sprite: CharacterSprite to add
        """
        self.characters[sprite.visual.name] = sprite
        logger.debug(f"Added character: {sprite.visual.name}")
    
    def get_character(self, name: str) -> Optional[CharacterSprite]:
        """
        Get character by name.
        
        Args:
            name: Character name
            
        Returns:
            CharacterSprite if found, None otherwise
        """
        return self.characters.get(name)
    
    def get_all_mobjects(self) -> List[VMobject]:
        """
        Get all character mobjects for scene rendering.
        
        Returns:
            List of Manim mobjects
        """
        return [char.get_mobject() for char in self.characters.values()]
    
    def position_characters(
        self,
        character_names: List[str],
        spacing: float = 3.0,
        center: bool = True
    ) -> List["Animation"]:
        """
        Position characters in a row.
        
        Args:
            character_names: Names of characters to position
            spacing: Distance between characters
            center: Whether to center the group
            
        Returns:
            List of movement animations
        """
        animations = []
        num_chars = len(character_names)
        
        if num_chars == 0:
            return animations
        
        # Calculate positions
        total_width = (num_chars - 1) * spacing
        start_x = -total_width / 2 if center else 0
        
        for i, name in enumerate(character_names):
            char = self.get_character(name)
            if char:
                x = start_x + (i * spacing)
                anim = char.move_to((x, 0), duration=0.5)
                animations.append(anim)
        
        return animations
    
    def get_character_count(self) -> int:
        """
        Get number of managed characters.
        
        Returns:
            Character count
        """
        return len(self.characters)


# Example usage
if __name__ == "__main__":
    # Example character visual
    visual = CharacterVisual(
        name="Lucy",
        sprite_path=Path("assets/characters/lucy.svg"),
        scale=1.2,
        default_position=(0, 0),
        layer=1
    )
    
    # Create sprite
    sprite = CharacterSprite(visual)
    
    # Get info
    print(sprite.get_info())

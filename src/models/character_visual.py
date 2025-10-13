"""
Character Visual Model - Visual representation data for animated characters.

Defines the visual properties, expressions, and animation states
for characters in the animation system.

Copyright (c) 2025. All Rights Reserved. Patent Pending.
"""

from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path


class Expression(str, Enum):
    """Character facial expressions."""
    NEUTRAL = "neutral"
    HAPPY = "happy"
    SAD = "sad"
    SURPRISED = "surprised"
    ANGRY = "angry"
    CONFUSED = "confused"
    EXCITED = "excited"
    WORRIED = "worried"
    TALKING = "talking"


class AnimationState(str, Enum):
    """Character animation states."""
    IDLE = "idle"
    WALKING = "walking"
    TALKING = "talking"
    GESTURING = "gesturing"
    REACTING = "reacting"
    ENTERING = "entering"
    EXITING = "exiting"


@dataclass
class CharacterVisual:
    """
    Visual representation of a character.
    
    Contains all visual assets and properties needed to
    render a character in animations.
    
    Attributes:
        name: Character name
        sprite_path: Path to main sprite file (SVG/PNG)
        expression_paths: Paths to expression overlays
        scale: Visual scale (1.0 = 100%)
        default_expression: Starting expression
        default_position: Starting position (x, y)
        layer: Z-order layer (higher = front)
        color_scheme: Primary colors for character
    """
    name: str
    sprite_path: Path
    expression_paths: Dict[Expression, Path] = field(default_factory=dict)
    scale: float = 1.0
    default_expression: Expression = Expression.NEUTRAL
    default_position: Tuple[float, float] = (0, 0)
    layer: int = 1
    color_scheme: Dict[str, str] = field(default_factory=dict)
    
    def __post_init__(self):
        """Validate visual data after initialization."""
        if not self.sprite_path.exists():
            raise FileNotFoundError(f"Sprite not found: {self.sprite_path}")
        
        if self.scale <= 0:
            raise ValueError(f"Scale must be positive: {self.scale}")

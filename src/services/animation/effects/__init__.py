"""
Visual Effects Library - Reusable animation effects.

Provides transitions, camera moves, and text effects
for professional scene composition.

Copyright (c) 2025. All Rights Reserved. Patent Pending.
"""

from .transitions import *
from .camera_moves import *
from .text_effects import *

__all__ = [
    # Transitions
    'fade_transition',
    'wipe_transition',
    'dissolve_transition',
    
    # Camera
    'pan_camera',
    'zoom_camera',
    'track_character',
    
    # Text
    'typewriter_text',
    'bounce_text',
]

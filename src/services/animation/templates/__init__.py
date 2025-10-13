"""
Animation Templates - Reusable scene templates.

Copyright (c) 2025. All Rights Reserved. Patent Pending.
"""

from .sitcom_template import SitcomScene
from .character_intro import create_character_intro
from .scene_transitions import create_transition_overlay

__all__ = [
    'SitcomScene',
    'create_character_intro',
    'create_transition_overlay',
]

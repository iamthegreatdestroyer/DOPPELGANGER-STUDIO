"""
Scene Transition Overlays.

Copyright (c) 2025. All Rights Reserved. Patent Pending.
"""

try:
    from manim import *
    MANIM_AVAILABLE = True
except ImportError:
    MANIM_AVAILABLE = False


def create_transition_overlay(text: str, duration: float = 2.0) -> type:
    """Create scene transition with text overlay."""
    
    def construct(scene):
        overlay = Text(text, font_size=36)
        scene.play(FadeIn(overlay))
        scene.wait(duration)
        scene.play(FadeOut(overlay))
    
    return type("TransitionOverlay", (Scene,), {"construct": construct})

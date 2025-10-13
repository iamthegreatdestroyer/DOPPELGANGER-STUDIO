"""
Text Effects - Animated text display.

Copyright (c) 2025. All Rights Reserved. Patent Pending.
"""

try:
    from manim import *
    MANIM_AVAILABLE = True
except ImportError:
    MANIM_AVAILABLE = False


def typewriter_text(text: str, duration: float = 2.0) -> Animation:
    """Typewriter text effect."""
    if not MANIM_AVAILABLE:
        raise ImportError("Manim required")
    
    text_obj = Text(text)
    return Write(text_obj, run_time=duration)


def bounce_text(text: str) -> Animation:
    """Bouncing text entrance."""
    if not MANIM_AVAILABLE:
        raise ImportError("Manim required")
    
    text_obj = Text(text)
    return Succession(
        text_obj.animate.shift(DOWN * 2),
        text_obj.animate.shift(UP * 2.3),
        text_obj.animate.shift(DOWN * 0.3),
    )

"""
Transition Effects - Scene transition animations.

Copyright (c) 2025. All Rights Reserved. Patent Pending.
"""

try:
    from manim import *
    MANIM_AVAILABLE = True
except ImportError:
    MANIM_AVAILABLE = False


def fade_transition(duration: float = 1.0) -> Animation:
    """Fade to black and back."""
    if not MANIM_AVAILABLE:
        raise ImportError("Manim required")
    
    fade_rect = Rectangle(
        width=config.frame_width,
        height=config.frame_height,
        fill_opacity=1,
        color=BLACK
    )
    
    return Succession(
        FadeIn(fade_rect, run_time=duration/2),
        FadeOut(fade_rect, run_time=duration/2)
    )


def wipe_transition(direction: str = "left", duration: float = 1.0) -> Animation:
    """Wipe transition.

    EXPERIMENTAL — not implemented. Animation placeholder; the wipe effect has
    not been built. This previously returned a silent no-op ``Wait(duration)``
    that masqueraded as a real transition.
    """
    raise NotImplementedError("experimental — not implemented")


def dissolve_transition(duration: float = 1.5) -> Animation:
    """Dissolve transition.

    EXPERIMENTAL — not implemented. Animation placeholder; the dissolve effect
    has not been built. This previously returned a silent no-op ``Wait(duration)``.
    """
    raise NotImplementedError("experimental — not implemented")

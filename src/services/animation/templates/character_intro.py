"""
Character Introduction Template.

Copyright (c) 2025. All Rights Reserved. Patent Pending.
"""

try:
    from manim import *
    MANIM_AVAILABLE = True
except ImportError:
    MANIM_AVAILABLE = False


def create_character_intro(name: str, facts: list) -> type:
    """Create character introduction scene."""
    
    def construct(scene):
        # Character name
        title = Text(name, font_size=48)
        title.to_edge(UP)
        
        scene.play(Write(title))
        scene.wait(1)
        
        # Facts
        for fact in facts:
            fact_text = Text(fact, font_size=24)
            scene.play(FadeIn(fact_text))
            scene.wait(2)
            scene.play(FadeOut(fact_text))
        
        scene.play(FadeOut(title))
    
    return type("CharacterIntro", (Scene,), {"construct": construct})

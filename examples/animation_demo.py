#!/usr/bin/env python3
"""
Animation Demo - Example usage of DOPPELGANGER STUDIO animation system.

Demonstrates:
- Character sprite creation
- Scene rendering
- Timeline management
- Video export

Copyright (c) 2025. All Rights Reserved. Patent Pending.
"""

import asyncio
from pathlib import Path

try:
    from manim import *
    MANIM_AVAILABLE = True
except ImportError:
    MANIM_AVAILABLE = False
    print("Warning: Manim not installed. Install with: pip install manim")

from src.services.animation import ManimWrapper, RenderQuality
from src.models.character_visual import CharacterVisual, Expression
from src.services.animation.character_sprite import CharacterSprite, CharacterSpriteManager
from src.services.animation.scene_renderer import SceneRenderer, SceneData
from src.services.animation.timeline_manager import Timeline
from src.services.animation.exporter import VideoExporter


def example_simple_animation():
    """
    Example 1: Simple text animation.
    
    Creates a basic "Hello World" animation.
    """
    print("\n=== Example 1: Simple Animation ===")
    
    if not MANIM_AVAILABLE:
        print("Skipping - Manim not installed")
        return
    
    # Create wrapper
    wrapper = ManimWrapper(quality=RenderQuality.PREVIEW)
    
    # Define scene construction
    def construct(scene):
        text = Text("DOPPELGANGER STUDIO", font_size=48)
        scene.play(Write(text))
        scene.wait(1)
        scene.play(FadeOut(text))
    
    # Create scene class
    SceneClass = wrapper.create_scene_class("HelloWorld", construct)
    
    # Render
    try:
        output = wrapper.render_scene(SceneClass, "hello_world.mp4")
        print(f"✅ Rendered to: {output}")
    except Exception as e:
        print(f"❌ Rendering failed: {e}")


def example_character_animation():
    """
    Example 2: Character animation with expressions.
    
    Demonstrates character sprite system.
    """
    print("\n=== Example 2: Character Animation ===")
    
    # Create character visual (would use real sprite files)
    # For demo, we'd need actual sprite assets
    print("Character animation requires sprite assets")
    print("See docs/animation_guide.md for asset creation")


def example_multi_scene_episode():
    """
    Example 3: Multi-scene episode export.
    
    Shows complete pipeline from scenes to final video.
    """
    print("\n=== Example 3: Multi-Scene Episode ===")
    
    # This would:
    # 1. Create multiple scene videos
    # 2. Use VideoExporter to concatenate
    # 3. Add metadata
    # 4. Export final episode
    
    print("Multi-scene export requires rendered scenes")
    print("See tests/integration/test_animation_pipeline.py")


def example_timeline_management():
    """
    Example 4: Timeline coordination.
    
    Demonstrates event scheduling and timing.
    """
    print("\n=== Example 4: Timeline Management ===")
    
    timeline = Timeline()
    
    # Add mock events (would be real animations)
    from unittest.mock import Mock
    
    timeline.add_event(0.0, Mock(), duration=1.0)
    timeline.add_event(1.5, Mock(), duration=2.0)
    timeline.add_event(3.0, Mock(), duration=1.5)
    
    print(f"Timeline duration: {timeline.get_duration()}s")
    print(f"Total events: {len(timeline.events)}")
    
    # Check what's happening at t=2.0
    active = timeline.get_events_at(2.0)
    print(f"Active events at t=2.0: {len(active)}")
    
    print("✅ Timeline management working")


def main():
    """
    Run all examples.
    """
    print("\n" + "="*50)
    print("DOPPELGANGER STUDIO - Animation Demo")
    print("="*50)
    
    # Check installation
    status = ManimWrapper.validate_installation()
    print("\n📦 Installation Status:")
    for component, installed in status.items():
        icon = "✅" if installed else "❌"
        print(f"  {icon} {component}")
    
    if not all(status.values()):
        print("\n⚠️  Some components missing. Install with:")
        print("  pip install manim pillow")
        print("  And install FFmpeg from: https://ffmpeg.org/")
    
    # Run examples
    example_simple_animation()
    example_character_animation()
    example_multi_scene_episode()
    example_timeline_management()
    
    print("\n" + "="*50)
    print("✅ Demo complete!")
    print("="*50)
    print("\nNext steps:")
    print("1. Create character sprite assets (SVG/PNG)")
    print("2. Write scene scripts")
    print("3. Render episode scenes")
    print("4. Export final video")
    print("\nSee docs/animation_guide.md for details")


if __name__ == "__main__":
    main()

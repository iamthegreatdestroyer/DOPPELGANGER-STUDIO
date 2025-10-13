"""
Unit tests for scene renderer.

Copyright (c) 2025. All Rights Reserved. Patent Pending.
"""

import pytest
from unittest.mock import Mock

from src.services.animation.scene_renderer import (
    SceneData,
    SceneRenderer
)
from src.services.animation.character_sprite import CharacterSpriteManager


@pytest.fixture
def scene_data():
    """Create test scene data."""
    return SceneData(
        scene_id="test_scene_1",
        description="Test scene",
        duration=30.0,
        characters=["Lucy", "Ricky"],
        dialogue=[
            ("Lucy", "Hello Ricky!"),
            ("Ricky", "Hi Lucy!")
        ]
    )


def test_scene_data_creation(scene_data):
    """Test SceneData creation."""
    assert scene_data.scene_id == "test_scene_1"
    assert len(scene_data.dialogue) == 2
    assert scene_data.duration == 30.0


def test_scene_renderer_init():
    """Test SceneRenderer initialization."""
    manager = CharacterSpriteManager()
    
    with pytest.raises(ImportError):
        # Should fail without Manim
        renderer = SceneRenderer(manager)

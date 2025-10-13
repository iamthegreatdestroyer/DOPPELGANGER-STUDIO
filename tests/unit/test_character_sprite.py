"""
Unit tests for character sprite system.

Copyright (c) 2025. All Rights Reserved. Patent Pending.
"""

import pytest
from pathlib import Path
from unittest.mock import Mock, patch

from src.models.character_visual import (
    CharacterVisual,
    Expression,
    AnimationState
)
from src.services.animation.character_sprite import (
    CharacterSprite,
    CharacterSpriteManager
)


@pytest.fixture
def mock_visual(tmp_path):
    """Create mock CharacterVisual."""
    sprite_file = tmp_path / "test.svg"
    sprite_file.write_text("<svg></svg>")
    
    return CharacterVisual(
        name="TestCharacter",
        sprite_path=sprite_file,
        scale=1.0
    )


def test_character_visual_creation(mock_visual):
    """Test CharacterVisual creation."""
    assert mock_visual.name == "TestCharacter"
    assert mock_visual.scale == 1.0
    assert mock_visual.default_expression == Expression.NEUTRAL


def test_expression_enum():
    """Test Expression enum values."""
    assert Expression.HAPPY.value == "happy"
    assert Expression.SAD.value == "sad"
    assert len(Expression) >= 8  # Should have multiple expressions


def test_animation_state_enum():
    """Test AnimationState enum."""
    assert AnimationState.IDLE.value == "idle"
    assert AnimationState.TALKING.value == "talking"


def test_sprite_manager():
    """Test CharacterSpriteManager."""
    manager = CharacterSpriteManager()
    
    assert manager.get_character_count() == 0
    assert manager.get_character("NonExistent") is None

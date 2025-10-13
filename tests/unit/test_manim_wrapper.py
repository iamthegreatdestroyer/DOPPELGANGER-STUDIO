"""
Unit tests for Manim wrapper.

Copyright (c) 2025. All Rights Reserved. Patent Pending.
"""

import pytest
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock

from src.services.animation.manim_wrapper import (
    ManimWrapper,
    RenderQuality,
    RenderConfig
)


@pytest.fixture
def manim_wrapper():
    """Create ManimWrapper instance for testing."""
    with patch('src.services.animation.manim_wrapper.MANIM_AVAILABLE', True):
        with patch('src.services.animation.manim_wrapper.config'):
            wrapper = ManimWrapper(quality=RenderQuality.PREVIEW)
            return wrapper


def test_manim_wrapper_init(manim_wrapper):
    """Test ManimWrapper initialization."""
    assert manim_wrapper.config.quality == RenderQuality.PREVIEW
    assert manim_wrapper.config.resolution == (854, 480)
    assert manim_wrapper.config.fps == 15


def test_quality_presets():
    """Test all quality presets."""
    presets = ManimWrapper.QUALITY_PRESETS
    
    assert RenderQuality.PREVIEW in presets
    assert RenderQuality.HIGH in presets
    assert presets[RenderQuality.HIGH]['fps'] == 60


def test_create_scene_class(manim_wrapper):
    """Test dynamic scene class creation."""
    def test_construct(scene):
        pass
    
    scene_class = manim_wrapper.create_scene_class(
        "TestScene",
        test_construct
    )
    
    assert scene_class.__name__ == "TestScene"
    assert callable(scene_class.construct)


def test_get_render_info(manim_wrapper):
    """Test render info retrieval."""
    info = manim_wrapper.get_render_info()
    
    assert 'quality' in info
    assert 'resolution' in info
    assert 'fps' in info
    assert info['fps'] == 15


def test_validate_installation():
    """Test installation validation."""
    status = ManimWrapper.validate_installation()
    
    assert 'manim' in status
    assert 'ffmpeg' in status
    assert isinstance(status['manim'], bool)

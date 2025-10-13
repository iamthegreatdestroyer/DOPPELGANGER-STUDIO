"""
Unit tests for timeline manager.

Copyright (c) 2025. All Rights Reserved. Patent Pending.
"""

import pytest
from unittest.mock import Mock

from src.services.animation.timeline_manager import (
    Timeline,
    TimelineEvent,
    EventType
)


def test_timeline_creation():
    """Test Timeline creation."""
    timeline = Timeline()
    
    assert timeline.current_time == 0.0
    assert len(timeline.events) == 0


def test_add_event():
    """Test adding events to timeline."""
    timeline = Timeline()
    mock_animation = Mock()
    
    timeline.add_event(
        time=1.0,
        animation=mock_animation,
        duration=2.0
    )
    
    assert len(timeline.events) == 1
    assert timeline.events[0].time == 1.0


def test_get_duration():
    """Test timeline duration calculation."""
    timeline = Timeline()
    
    # Empty timeline
    assert timeline.get_duration() == 0.0
    
    # Add events
    timeline.add_event(1.0, Mock(), 2.0)
    timeline.add_event(5.0, Mock(), 3.0)
    
    # Should be 5.0 + 3.0 = 8.0
    assert timeline.get_duration() == 8.0


def test_get_events_at():
    """Test getting events at specific time."""
    timeline = Timeline()
    
    timeline.add_event(1.0, Mock(), 2.0)  # 1.0 - 3.0
    timeline.add_event(2.5, Mock(), 1.0)  # 2.5 - 3.5
    
    # At t=2.6, both events should be active
    events = timeline.get_events_at(2.6)
    assert len(events) == 2
    
    # At t=0.5, no events active
    events = timeline.get_events_at(0.5)
    assert len(events) == 0


def test_clear_timeline():
    """Test clearing timeline."""
    timeline = Timeline()
    timeline.add_event(1.0, Mock(), 1.0)
    
    timeline.clear()
    
    assert len(timeline.events) == 0
    assert timeline.current_time == 0.0

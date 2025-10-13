"""
Timeline Manager - Coordinate animation timing and sequencing.

Manages the timeline of animations, ensuring proper synchronization
of character movements, dialogue, effects, and transitions.

Copyright (c) 2025. All Rights Reserved. Patent Pending.
"""

from typing import List, Dict, Tuple, Optional, Callable, Any
from dataclasses import dataclass, field
from enum import Enum
import logging

try:
    from manim import Animation
    MANIM_AVAILABLE = True
except ImportError:
    MANIM_AVAILABLE = False

logger = logging.getLogger(__name__)


class EventType(str, Enum):
    """Timeline event types."""
    ANIMATION = "animation"
    DIALOGUE = "dialogue"
    CAMERA_MOVE = "camera_move"
    EFFECT = "effect"
    TRANSITION = "transition"


@dataclass
class TimelineEvent:
    """Event on the animation timeline."""
    time: float  # Start time in seconds
    duration: float  # Event duration
    event_type: EventType
    animation: Optional[Animation] = None
    data: Dict[str, Any] = field(default_factory=dict)
    priority: int = 0  # Higher priority events execute first


class Timeline:
    """
    Animation timeline manager.
    
    Schedules and coordinates animations, dialogue, and effects
    with precise timing control.
    
    Example:
        >>> timeline = Timeline()
        >>> timeline.add_event(0.0, character.fade_in(), duration=0.5)
        >>> timeline.add_event(1.0, character.move_to((2, 0)), duration=1.0)
        >>> events = timeline.get_events_at(1.5)
    """
    
    def __init__(self):
        """Initialize timeline."""
        self.events: List[TimelineEvent] = []
        self.current_time: float = 0.0
        logger.info("Timeline initialized")
    
    def add_event(
        self,
        time: float,
        animation: Animation,
        duration: float,
        event_type: EventType = EventType.ANIMATION,
        priority: int = 0,
        **kwargs
    ):
        """
        Add event to timeline.
        
        Args:
            time: Start time in seconds
            animation: Manim animation
            duration: Event duration
            event_type: Type of event
            priority: Execution priority
            **kwargs: Additional event data
        """
        event = TimelineEvent(
            time=time,
            duration=duration,
            event_type=event_type,
            animation=animation,
            data=kwargs,
            priority=priority
        )
        
        self.events.append(event)
        logger.debug(f"Added event at t={time}s, duration={duration}s")
    
    def get_events_at(self, time: float) -> List[TimelineEvent]:
        """
        Get events active at specific time.
        
        Args:
            time: Time in seconds
            
        Returns:
            List of active events
        """
        active = [
            event for event in self.events
            if event.time <= time < (event.time + event.duration)
        ]
        
        # Sort by priority
        active.sort(key=lambda e: e.priority, reverse=True)
        
        return active
    
    def get_duration(self) -> float:
        """
        Get total timeline duration.
        
        Returns:
            Duration in seconds
        """
        if not self.events:
            return 0.0
        
        return max(
            event.time + event.duration
            for event in self.events
        )
    
    def get_events_in_range(
        self,
        start: float,
        end: float
    ) -> List[TimelineEvent]:
        """
        Get events in time range.
        
        Args:
            start: Start time
            end: End time
            
        Returns:
            Events overlapping with range
        """
        return [
            event for event in self.events
            if not (event.time + event.duration < start or event.time > end)
        ]
    
    def clear(self):
        """Clear all events from timeline."""
        self.events.clear()
        self.current_time = 0.0
        logger.debug("Timeline cleared")


# Copyright (c) 2025. All Rights Reserved. Patent Pending.

"""
Copyright (c) 2025 DOPPELGANGER STUDIO. All Rights Reserved.

Data models for stage directions and visual choreography.

This module defines structures for stage directions, physical comedy,
and camera suggestions.
"""

from dataclasses import dataclass, field
from typing import List, Optional
from datetime import datetime


@dataclass
class CameraSuggestion:
    """
    Camera/blocking suggestion for a moment.
    
    Attributes:
        shot_type: Type of camera shot
        movement: Camera movement if any
        focus: What/who camera focuses on
        reasoning: Why this shot works
        timing: When in scene this shot happens
    
    Example:
        >>> camera = CameraSuggestion(
        ...     shot_type="CLOSE-UP",
        ...     movement="ZOOM IN",
        ...     focus="Luna's face",
        ...     reasoning="Capture her scheming expression",
        ...     timing="During punchline"
        ... )
    """
    
    shot_type: str  # "WIDE", "MEDIUM", "CLOSE-UP", "TWO-SHOT", "OVER-SHOULDER"
    focus: str
    reasoning: str
    movement: Optional[str] = None  # "PAN", "ZOOM", "DOLLY", "TILT"
    timing: Optional[str] = None
    
    def format_for_script(self) -> str:
        """Format as production script note."""
        output = f"[{self.shot_type}"
        if self.movement:
            output += f" - {self.movement}"
        output += f" on {self.focus}]"
        return output
    
    def to_dict(self) -> dict:
        """Convert to dictionary."""
        return {
            'shot_type': self.shot_type,
            'focus': self.focus,
            'reasoning': self.reasoning,
            'movement': self.movement,
            'timing': self.timing
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> "CameraSuggestion":
        """Create CameraSuggestion from dictionary."""
        return cls(
            shot_type=data['shot_type'],
            focus=data['focus'],
            reasoning=data['reasoning'],
            movement=data.get('movement'),
            timing=data.get('timing')
        )


@dataclass
class StageDirection:
    """
    Single stage direction/action beat.
    
    Attributes:
        timing: When this happens relative to dialogue
        description: What happens
        duration_estimate: Estimated seconds
        involves_characters: Characters involved
        visual_gag: Whether this is a visual joke
        camera_suggestion: Optional camera work
    
    Example:
        >>> direction = StageDirection(
        ...     timing="BEFORE LINE",
        ...     description="Luna trips over cables while rushing",
        ...     duration_estimate=2.0,
        ...     involves_characters=["Luna"],
        ...     visual_gag=True
        ... )
    """
    
    timing: str  # "BEFORE LINE", "DURING LINE", "AFTER LINE", "CONTINUOUS"
    description: str
    duration_estimate: float  # Seconds
    involves_characters: List[str]
    visual_gag: bool = False
    camera_suggestion: Optional[CameraSuggestion] = None
    
    def format_for_screenplay(self) -> str:
        """Format as screenplay stage direction."""
        output = f"[{self.description}]"
        if self.camera_suggestion:
            output += f"\n{self.camera_suggestion.format_for_script()}"
        return output
    
    def to_dict(self) -> dict:
        """Convert to dictionary."""
        return {
            'timing': self.timing,
            'description': self.description,
            'duration_estimate': self.duration_estimate,
            'involves_characters': self.involves_characters,
            'visual_gag': self.visual_gag,
            'camera_suggestion': (
                self.camera_suggestion.to_dict()
                if self.camera_suggestion else None
            )
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> "StageDirection":
        """Create StageDirection from dictionary."""
        camera_data = data.get('camera_suggestion')
        camera = (
            CameraSuggestion.from_dict(camera_data)
            if camera_data else None
        )
        return cls(
            timing=data['timing'],
            description=data['description'],
            duration_estimate=data['duration_estimate'],
            involves_characters=data['involves_characters'],
            visual_gag=data.get('visual_gag', False),
            camera_suggestion=camera
        )


@dataclass
class PhysicalComedySequence:
    """
    Multi-step physical comedy choreography.
    
    Attributes:
        beat_name: Name of this comedy sequence
        setup_actions: Actions that set up the joke
        escalation_actions: Actions that build the comedy
        climax_action: Peak of the physical comedy
        resolution_action: How it resolves
        total_duration: Total estimated seconds
    
    Example:
        >>> sequence = PhysicalComedySequence(
        ...     beat_name="Ring Light Disaster",
        ...     setup_actions=[setup1, setup2],
        ...     escalation_actions=[esc1, esc2],
        ...     climax_action=climax,
        ...     resolution_action=resolution,
        ...     total_duration=15.0
        ... )
    """
    
    beat_name: str
    setup_actions: List[StageDirection]
    escalation_actions: List[StageDirection]
    climax_action: StageDirection
    resolution_action: StageDirection
    total_duration: float
    
    def get_all_actions(self) -> List[StageDirection]:
        """Get all actions in sequence order."""
        actions = []
        actions.extend(self.setup_actions)
        actions.extend(self.escalation_actions)
        actions.append(self.climax_action)
        actions.append(self.resolution_action)
        return actions
    
    def format_for_screenplay(self) -> str:
        """Format entire sequence for screenplay."""
        output = f"\n[PHYSICAL COMEDY: {self.beat_name}]\n\n"
        
        for action in self.get_all_actions():
            output += action.format_for_screenplay() + "\n\n"
        
        output += f"[Duration: {self.total_duration}s]\n"
        return output
    
    def to_dict(self) -> dict:
        """Convert to dictionary."""
        return {
            'beat_name': self.beat_name,
            'setup_actions': [a.to_dict() for a in self.setup_actions],
            'escalation_actions': [a.to_dict() for a in self.escalation_actions],
            'climax_action': self.climax_action.to_dict(),
            'resolution_action': self.resolution_action.to_dict(),
            'total_duration': self.total_duration
        }


@dataclass
class SceneStageDirections:
    """
    Complete stage directions for a scene.
    
    Attributes:
        scene_number: Scene number in episode
        opening_description: Opening visual/setup
        action_beats: Individual action directions
        physical_comedy_sequences: Choreographed comedy sequences
        closing_description: Closing visual
        camera_suggestions: Overall camera notes
        total_visual_runtime: Estimated seconds of action
        generated_at: When generated
    
    Example:
        >>> directions = SceneStageDirections(
        ...     scene_number=1,
        ...     opening_description="Living room cluttered with equipment",
        ...     action_beats=[beat1, beat2],
        ...     physical_comedy_sequences=[sequence],
        ...     closing_description="Luna schemes in corner",
        ...     camera_suggestions=[cam1, cam2],
        ...     total_visual_runtime=45.0
        ... )
    """
    
    scene_number: int
    opening_description: str
    action_beats: List[StageDirection]
    physical_comedy_sequences: List[PhysicalComedySequence]
    closing_description: str
    camera_suggestions: List[CameraSuggestion]
    total_visual_runtime: float
    generated_at: datetime = field(default_factory=datetime.now)
    
    def get_all_directions(self) -> List[StageDirection]:
        """Get all stage directions including comedy sequences."""
        directions = list(self.action_beats)
        for sequence in self.physical_comedy_sequences:
            directions.extend(sequence.get_all_actions())
        return directions
    
    def format_for_screenplay(self) -> str:
        """Format entire scene directions for screenplay."""
        output = f"\n=== SCENE {self.scene_number} STAGE DIRECTIONS ===\n\n"
        
        # Opening
        output += f"INT/EXT. [LOCATION]\n\n"
        output += f"{self.opening_description}\n\n"
        
        # Action beats
        if self.action_beats:
            output += "ACTION BEATS:\n\n"
            for beat in self.action_beats:
                output += beat.format_for_screenplay() + "\n\n"
        
        # Physical comedy sequences
        if self.physical_comedy_sequences:
            for sequence in self.physical_comedy_sequences:
                output += sequence.format_for_screenplay() + "\n"
        
        # Closing
        output += f"\n{self.closing_description}\n\n"
        
        # Camera notes
        if self.camera_suggestions:
            output += "CAMERA NOTES:\n"
            for cam in self.camera_suggestions:
                output += f"- {cam.format_for_script()}: {cam.reasoning}\n"
        
        output += f"\nTotal Visual Runtime: {self.total_visual_runtime}s\n"
        
        return output
    
    def to_dict(self) -> dict:
        """Convert to dictionary."""
        return {
            'scene_number': self.scene_number,
            'opening_description': self.opening_description,
            'action_beats': [b.to_dict() for b in self.action_beats],
            'physical_comedy_sequences': [
                s.to_dict() for s in self.physical_comedy_sequences
            ],
            'closing_description': self.closing_description,
            'camera_suggestions': [c.to_dict() for c in self.camera_suggestions],
            'total_visual_runtime': self.total_visual_runtime,
            'generated_at': self.generated_at.isoformat()
        }

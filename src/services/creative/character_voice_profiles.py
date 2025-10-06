"""
Copyright (c) 2025 DOPPELGANGER STUDIO. All Rights Reserved.

Character voice profile system for dialogue consistency.

This module creates detailed voice profiles from character analysis
to ensure dialogue consistency across scenes and episodes.
"""

from dataclasses import dataclass, field
from typing import List, Dict, Optional
from datetime import datetime


@dataclass
class CharacterVoiceProfile:
    """
    Comprehensive voice profile for a character.
    
    Captures all aspects of how a character speaks to maintain
    consistency across dialogue generation.
    
    Attributes:
        character_name: Character's name in the show
        vocabulary_level: Complexity of language ("simple", "sophisticated", "technical")
        sentence_structure: How they construct sentences ("short", "rambling", "eloquent")
        verbal_tics: Habitual words/sounds ("um", "like", "you know")
        catchphrases: Signature phrases the character repeats
        emotional_range: Emotional states they typically display
        speech_patterns: Distinctive ways of speaking
        relationship_dynamics: How they talk to each specific character
        education_level: Impacts word choice and grammar
        cultural_background: Influences idioms and references
        age_appropriate_language: Age-specific vocabulary and slang
        humor_style: How they deliver comedy ("sarcastic", "slapstick", "wordplay")
        created_at: When profile was generated
    
    Example:
        >>> lucy_profile = CharacterVoiceProfile(
        ...     character_name="Luna",
        ...     vocabulary_level="simple",
        ...     sentence_structure="rambling",
        ...     verbal_tics=["Oh!", "like"],
        ...     catchphrases=["Ricky!", "But why not?"],
        ...     emotional_range=["excitable", "scheming", "endearing"],
        ...     speech_patterns=["Whining when pleading", "Fast when excited"],
        ...     relationship_dynamics={"Ricky": "respectful but pushy"}
        ... )
    """
    
    character_name: str
    vocabulary_level: str
    sentence_structure: str
    verbal_tics: List[str] = field(default_factory=list)
    catchphrases: List[str] = field(default_factory=list)
    emotional_range: List[str] = field(default_factory=list)
    speech_patterns: List[str] = field(default_factory=list)
    relationship_dynamics: Dict[str, str] = field(default_factory=dict)
    
    # Additional context
    education_level: Optional[str] = None
    cultural_background: Optional[str] = None
    age_appropriate_language: Optional[str] = None
    humor_style: Optional[str] = None
    
    # Metadata
    created_at: datetime = field(default_factory=datetime.now)
    
    def get_speaking_style_summary(self) -> str:
        """Generate human-readable summary of speaking style."""
        summary = f"{self.character_name} speaks with {self.vocabulary_level} vocabulary "
        summary += f"in {self.sentence_structure} sentences. "
        
        if self.verbal_tics:
            summary += f"Often says: {', '.join(self.verbal_tics[:3])}. "
        
        if self.catchphrases:
            summary += f"Known for: '{self.catchphrases[0]}'. "
        
        return summary
    
    def get_relationship_guidance(self, other_character: str) -> Optional[str]:
        """Get speaking style for specific relationship."""
        return self.relationship_dynamics.get(other_character)
    
    def to_dict(self) -> dict:
        """Convert to dictionary for storage/transmission."""
        return {
            'character_name': self.character_name,
            'vocabulary_level': self.vocabulary_level,
            'sentence_structure': self.sentence_structure,
            'verbal_tics': self.verbal_tics,
            'catchphrases': self.catchphrases,
            'emotional_range': self.emotional_range,
            'speech_patterns': self.speech_patterns,
            'relationship_dynamics': self.relationship_dynamics,
            'education_level': self.education_level,
            'cultural_background': self.cultural_background,
            'age_appropriate_language': self.age_appropriate_language,
            'humor_style': self.humor_style,
            'created_at': self.created_at.isoformat()
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> 'CharacterVoiceProfile':
        """Create from dictionary."""
        # Handle datetime conversion
        created_at = data.get('created_at')
        if isinstance(created_at, str):
            created_at = datetime.fromisoformat(created_at)
        elif created_at is None:
            created_at = datetime.now()
        
        return cls(
            character_name=data['character_name'],
            vocabulary_level=data['vocabulary_level'],
            sentence_structure=data['sentence_structure'],
            verbal_tics=data.get('verbal_tics', []),
            catchphrases=data.get('catchphrases', []),
            emotional_range=data.get('emotional_range', []),
            speech_patterns=data.get('speech_patterns', []),
            relationship_dynamics=data.get('relationship_dynamics', {}),
            education_level=data.get('education_level'),
            cultural_background=data.get('cultural_background'),
            age_appropriate_language=data.get('age_appropriate_language'),
            humor_style=data.get('humor_style'),
            created_at=created_at
        )


@dataclass
class DialogueLine:
    """
    Single line of dialogue with metadata.
    
    Attributes:
        character: Character speaking
        line: The actual dialogue text
        emotion: Emotional state during line
        delivery_note: Parenthetical acting direction
        pause_before: Seconds of silence before line
        is_comedic_beat: Whether this is a joke/comedic moment
        comedic_beat_type: Type of comedy if applicable
        line_number: Line number in script
    
    Example:
        >>> line = DialogueLine(
        ...     character="LUNA",
        ...     line="Ricky! You have to hear this idea!",
        ...     emotion="excited",
        ...     delivery_note="rushing in, out of breath",
        ...     pause_before=0.0,
        ...     is_comedic_beat=False
        ... )
    """
    
    character: str
    line: str
    emotion: str
    delivery_note: Optional[str] = None
    pause_before: float = 0.0
    is_comedic_beat: bool = False
    comedic_beat_type: Optional[str] = None  # "setup", "punchline", "callback"
    line_number: Optional[int] = None
    
    def format_for_screenplay(self) -> str:
        """Format as standard screenplay dialogue."""
        output = f"{self.character.upper()}\n"
        
        if self.delivery_note:
            output += f"({self.delivery_note})\n"
        
        output += f"{self.line}\n"
        
        return output
    
    def to_dict(self) -> dict:
        """Convert to dictionary."""
        return {
            'character': self.character,
            'line': self.line,
            'emotion': self.emotion,
            'delivery_note': self.delivery_note,
            'pause_before': self.pause_before,
            'is_comedic_beat': self.is_comedic_beat,
            'comedic_beat_type': self.comedic_beat_type,
            'line_number': self.line_number
        }


@dataclass
class SceneDialogue:
    """
    Complete dialogue for a scene.
    
    Attributes:
        scene_number: Scene number in episode
        location: Where scene takes place
        characters_present: List of characters in scene
        dialogue_lines: All dialogue lines in order
        total_runtime_estimate: Estimated seconds to perform
        comedic_beats_count: Number of jokes/comedic moments
        generated_at: When dialogue was generated
        confidence_score: How well it matches character voices (0.0-1.0)
    
    Example:
        >>> scene = SceneDialogue(
        ...     scene_number=1,
        ...     location="Living Room",
        ...     characters_present=["Luna", "Ricky"],
        ...     dialogue_lines=[line1, line2, line3],
        ...     total_runtime_estimate=90,
        ...     comedic_beats_count=2,
        ...     confidence_score=0.92
        ... )
    """
    
    scene_number: int
    location: str
    characters_present: List[str]
    dialogue_lines: List[DialogueLine]
    total_runtime_estimate: int  # Seconds
    comedic_beats_count: int
    generated_at: datetime = field(default_factory=datetime.now)
    confidence_score: float = 0.0
    
    def get_dialogue_text(self) -> str:
        """Get all dialogue as plain text."""
        return "\n\n".join(line.line for line in self.dialogue_lines)
    
    def get_screenplay_format(self) -> str:
        """Format entire scene dialogue as screenplay."""
        output = f"SCENE {self.scene_number} - {self.location.upper()}\n\n"
        
        for line in self.dialogue_lines:
            if line.pause_before > 0:
                output += f"[PAUSE - {line.pause_before} seconds]\n\n"
            output += line.format_for_screenplay() + "\n"
        
        return output
    
    def to_dict(self) -> dict:
        """Convert to dictionary."""
        return {
            'scene_number': self.scene_number,
            'location': self.location,
            'characters_present': self.characters_present,
            'dialogue_lines': [line.to_dict() for line in self.dialogue_lines],
            'total_runtime_estimate': self.total_runtime_estimate,
            'comedic_beats_count': self.comedic_beats_count,
            'generated_at': self.generated_at.isoformat(),
            'confidence_score': self.confidence_score
        }

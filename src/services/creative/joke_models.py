"""
Copyright (c) 2025 DOPPELGANGER STUDIO. All Rights Reserved.

Data models for joke structure analysis and optimization.

This module defines the data structures used by the JokeOptimizer component
to analyze, refine, and score comedic beats in scripts.
"""

from dataclasses import dataclass, field
from typing import List, Dict, Optional
from enum import Enum


class JokeType(Enum):
    """Types of comedic structures."""
    WORDPLAY = "wordplay"  # Puns, double entendres, word confusion
    SITUATIONAL = "situational"  # Irony, misunderstandings, contrasts
    PHYSICAL = "physical"  # Slapstick, visual gags, pratfalls
    CALLBACK = "callback"  # References to earlier jokes
    CHARACTER = "character"  # Based on personality quirks
    MISDIRECTION = "misdirection"  # Setup with unexpected payoff
    RUNNING_GAG = "running_gag"  # Repeated joke with variations


class JokeTiming(Enum):
    """Timing categories for joke delivery."""
    RAPID_FIRE = "rapid_fire"  # Quick succession (< 30 seconds apart)
    WELL_SPACED = "well_spaced"  # Good breathing room (30-90 seconds)
    SLOW_BURN = "slow_burn"  # Long setup (> 90 seconds)


@dataclass
class JokeStructure:
    """
    Analyzed structure of a single joke or comedic beat.
    
    Attributes:
        joke_id: Unique identifier for this joke
        joke_type: Category of comedy (wordplay, situational, etc.)
        setup: The setup text/description
        misdirection: Optional misdirection element
        punchline: The payoff/punchline
        timing_position: When this joke occurs in the scene (seconds)
        characters_involved: Characters participating in the joke
        effectiveness_score: AI-generated score (0.0-1.0)
        improvement_suggestions: AI suggestions for refinement
        callback_potential: Whether this could be referenced later
        callback_references: IDs of jokes this references
    """
    joke_id: str
    joke_type: JokeType
    setup: str
    punchline: str
    timing_position: float  # Seconds into scene
    characters_involved: List[str]
    effectiveness_score: float = 0.0
    misdirection: Optional[str] = None
    improvement_suggestions: List[str] = field(default_factory=list)
    callback_potential: bool = False
    callback_references: List[str] = field(default_factory=list)
    
    def to_dict(self) -> Dict:
        """Convert to dictionary for serialization."""
        return {
            "joke_id": self.joke_id,
            "joke_type": self.joke_type.value,
            "setup": self.setup,
            "misdirection": self.misdirection,
            "punchline": self.punchline,
            "timing_position": self.timing_position,
            "characters_involved": self.characters_involved,
            "effectiveness_score": self.effectiveness_score,
            "improvement_suggestions": self.improvement_suggestions,
            "callback_potential": self.callback_potential,
            "callback_references": self.callback_references,
        }
    
    @classmethod
    def from_dict(cls, data: Dict) -> "JokeStructure":
        """Create from dictionary."""
        data_copy = data.copy()
        data_copy["joke_type"] = JokeType(data["joke_type"])
        return cls(**data_copy)


@dataclass
class AlternativePunchline:
    """
    Alternative version of a punchline for A/B testing.
    
    Attributes:
        original_joke_id: ID of the joke this is an alternative for
        punchline: The alternative punchline text
        reasoning: Why this alternative might work better
        estimated_effectiveness: Predicted effectiveness (0.0-1.0)
        maintains_character: Whether it stays true to character voice
    """
    original_joke_id: str
    punchline: str
    reasoning: str
    estimated_effectiveness: float
    maintains_character: bool = True
    
    def to_dict(self) -> Dict:
        """Convert to dictionary for serialization."""
        return {
            "original_joke_id": self.original_joke_id,
            "punchline": self.punchline,
            "reasoning": self.reasoning,
            "estimated_effectiveness": self.estimated_effectiveness,
            "maintains_character": self.maintains_character,
        }
    
    @classmethod
    def from_dict(cls, data: Dict) -> "AlternativePunchline":
        """Create from dictionary."""
        return cls(**data)


@dataclass
class CallbackOpportunity:
    """
    Identified opportunity for callback comedy.
    
    Attributes:
        source_joke_id: Original joke that could be referenced
        target_scene: Scene where callback would work
        target_timing: When in target scene (seconds)
        callback_suggestion: How to reference the original joke
        comedic_payoff: Why this callback would be funny
        risk_level: How risky/obscure the callback is (0.0-1.0)
    """
    source_joke_id: str
    target_scene: str
    target_timing: float
    callback_suggestion: str
    comedic_payoff: str
    risk_level: float = 0.5
    
    def to_dict(self) -> Dict:
        """Convert to dictionary for serialization."""
        return {
            "source_joke_id": self.source_joke_id,
            "target_scene": self.target_scene,
            "target_timing": self.target_timing,
            "callback_suggestion": self.callback_suggestion,
            "comedic_payoff": self.comedic_payoff,
            "risk_level": self.risk_level,
        }
    
    @classmethod
    def from_dict(cls, data: Dict) -> "CallbackOpportunity":
        """Create from dictionary."""
        return cls(**data)


@dataclass
class ComedyTimingAnalysis:
    """
    Analysis of comedy distribution and pacing.
    
    Attributes:
        total_jokes: Number of jokes in the script
        average_spacing: Average seconds between jokes
        timing_category: Overall pacing (rapid_fire, well_spaced, slow_burn)
        clusters: Scenes with too many jokes close together
        dead_zones: Scenes with too few jokes (>2 minutes without comedy)
        optimal_spacing: Recommended seconds between jokes
        pacing_score: How well-paced the comedy is (0.0-1.0)
    """
    total_jokes: int
    average_spacing: float
    timing_category: JokeTiming
    clusters: List[str] = field(default_factory=list)  # Scene IDs
    dead_zones: List[str] = field(default_factory=list)  # Scene IDs
    optimal_spacing: float = 45.0  # Default: one joke per 45 seconds
    pacing_score: float = 0.0
    
    def to_dict(self) -> Dict:
        """Convert to dictionary for serialization."""
        return {
            "total_jokes": self.total_jokes,
            "average_spacing": self.average_spacing,
            "timing_category": self.timing_category.value,
            "clusters": self.clusters,
            "dead_zones": self.dead_zones,
            "optimal_spacing": self.optimal_spacing,
            "pacing_score": self.pacing_score,
        }
    
    @classmethod
    def from_dict(cls, data: Dict) -> "ComedyTimingAnalysis":
        """Create from dictionary."""
        data_copy = data.copy()
        data_copy["timing_category"] = JokeTiming(data["timing_category"])
        return cls(**data_copy)


@dataclass
class OptimizedScriptComedy:
    """
    Complete comedy analysis and optimization for a script.
    
    Attributes:
        script_id: Identifier for the script analyzed
        analyzed_jokes: All jokes found and analyzed
        alternative_punchlines: Alternative versions for weak jokes
        callback_opportunities: Suggested callbacks to add
        timing_analysis: Pacing and distribution analysis
        overall_effectiveness: Average effectiveness across all jokes
        optimization_summary: High-level summary of changes suggested
        confidence_score: How confident the optimizer is (0.0-1.0)
    """
    script_id: str
    analyzed_jokes: List[JokeStructure]
    alternative_punchlines: List[AlternativePunchline]
    callback_opportunities: List[CallbackOpportunity]
    timing_analysis: ComedyTimingAnalysis
    overall_effectiveness: float
    optimization_summary: str
    confidence_score: float = 0.0
    
    def to_dict(self) -> Dict:
        """Convert to dictionary for serialization."""
        return {
            "script_id": self.script_id,
            "analyzed_jokes": [joke.to_dict() for joke in self.analyzed_jokes],
            "alternative_punchlines": [
                alt.to_dict() for alt in self.alternative_punchlines
            ],
            "callback_opportunities": [
                opp.to_dict() for opp in self.callback_opportunities
            ],
            "timing_analysis": self.timing_analysis.to_dict(),
            "overall_effectiveness": self.overall_effectiveness,
            "optimization_summary": self.optimization_summary,
            "confidence_score": self.confidence_score,
        }
    
    @classmethod
    def from_dict(cls, data: Dict) -> "OptimizedScriptComedy":
        """Create from dictionary."""
        return cls(
            script_id=data["script_id"],
            analyzed_jokes=[
                JokeStructure.from_dict(joke) for joke in data["analyzed_jokes"]
            ],
            alternative_punchlines=[
                AlternativePunchline.from_dict(alt) 
                for alt in data["alternative_punchlines"]
            ],
            callback_opportunities=[
                CallbackOpportunity.from_dict(opp)
                for opp in data["callback_opportunities"]
            ],
            timing_analysis=ComedyTimingAnalysis.from_dict(
                data["timing_analysis"]
            ),
            overall_effectiveness=data["overall_effectiveness"],
            optimization_summary=data["optimization_summary"],
            confidence_score=data["confidence_score"],
        )
    
    def get_weak_jokes(self, threshold: float = 0.6) -> List[JokeStructure]:
        """Get jokes below effectiveness threshold."""
        return [
            joke for joke in self.analyzed_jokes
            if joke.effectiveness_score < threshold
        ]
    
    def get_strong_jokes(self, threshold: float = 0.8) -> List[JokeStructure]:
        """Get jokes above effectiveness threshold."""
        return [
            joke for joke in self.analyzed_jokes
            if joke.effectiveness_score >= threshold
        ]
    
    def get_jokes_by_type(self, joke_type: JokeType) -> List[JokeStructure]:
        """Get all jokes of a specific type."""
        return [
            joke for joke in self.analyzed_jokes
            if joke.joke_type == joke_type
        ]

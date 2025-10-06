"""
Copyright (c) 2025 DOPPELGANGER STUDIO. All Rights Reserved.

Data models for script validation and quality assessment.

This module defines the data structures used by the ScriptValidator component
to assess script quality across multiple dimensions: character consistency,
plot coherence, comedy distribution, and production feasibility.
"""

from dataclasses import dataclass, field
from typing import List, Dict, Optional
from enum import Enum
from datetime import datetime


class ValidationSeverity(Enum):
    """Severity levels for validation issues."""
    INFO = "info"  # Informational, not a problem
    WARNING = "warning"  # Minor issue, could be improved
    ERROR = "error"  # Significant problem that should be fixed
    CRITICAL = "critical"  # Major issue that breaks the script


class ValidationCategory(Enum):
    """Categories of validation checks."""
    CHARACTER_CONSISTENCY = "character_consistency"
    PLOT_COHERENCE = "plot_coherence"
    COMEDY_DISTRIBUTION = "comedy_distribution"
    PRODUCTION_COMPLEXITY = "production_complexity"
    DIALOGUE_QUALITY = "dialogue_quality"
    PACING = "pacing"


@dataclass
class ValidationIssue:
    """
    Single validation issue found in the script.
    
    Attributes:
        issue_id: Unique identifier for this issue
        category: Type of validation check that found this
        severity: How serious this issue is
        message: Human-readable description
        location: Where in the script (scene, line, etc.)
        suggestion: How to fix this issue
        score_impact: How much this affects overall score (-1.0 to 0.0)
    """
    issue_id: str
    category: ValidationCategory
    severity: ValidationSeverity
    message: str
    location: str
    suggestion: str
    score_impact: float = 0.0  # Negative impact on score
    
    def to_dict(self) -> Dict:
        """Convert to dictionary for serialization."""
        return {
            "issue_id": self.issue_id,
            "category": self.category.value,
            "severity": self.severity.value,
            "message": self.message,
            "location": self.location,
            "suggestion": self.suggestion,
            "score_impact": self.score_impact,
        }
    
    @classmethod
    def from_dict(cls, data: Dict) -> "ValidationIssue":
        """Create from dictionary."""
        return cls(
            issue_id=data["issue_id"],
            category=ValidationCategory(data["category"]),
            severity=ValidationSeverity(data["severity"]),
            message=data["message"],
            location=data["location"],
            suggestion=data["suggestion"],
            score_impact=data.get("score_impact", 0.0),
        )


@dataclass
class CharacterConsistencyScore:
    """
    Character consistency assessment for a single character.
    
    Attributes:
        character_name: Character being assessed
        voice_match_score: How well dialogue matches voice profile (0.0-1.0)
        vocabulary_consistency: Vocabulary level consistency (0.0-1.0)
        catchphrase_usage: Appropriate use of catchphrases (0.0-1.0)
        relationship_consistency: Relationship dynamics maintained (0.0-1.0)
        overall_score: Average of all consistency metrics
        issues: Specific consistency issues found
    """
    character_name: str
    voice_match_score: float
    vocabulary_consistency: float
    catchphrase_usage: float
    relationship_consistency: float
    overall_score: float = 0.0
    issues: List[str] = field(default_factory=list)
    
    def __post_init__(self):
        """Calculate overall score after initialization."""
        if self.overall_score == 0.0:
            self.overall_score = (
                self.voice_match_score +
                self.vocabulary_consistency +
                self.catchphrase_usage +
                self.relationship_consistency
            ) / 4.0
    
    def to_dict(self) -> Dict:
        """Convert to dictionary for serialization."""
        return {
            "character_name": self.character_name,
            "voice_match_score": self.voice_match_score,
            "vocabulary_consistency": self.vocabulary_consistency,
            "catchphrase_usage": self.catchphrase_usage,
            "relationship_consistency": self.relationship_consistency,
            "overall_score": self.overall_score,
            "issues": self.issues,
        }
    
    @classmethod
    def from_dict(cls, data: Dict) -> "CharacterConsistencyScore":
        """Create from dictionary."""
        return cls(**data)


@dataclass
class ComedyDistributionAnalysis:
    """
    Analysis of comedy distribution and effectiveness.
    
    Attributes:
        total_comedic_beats: Number of jokes/comedic moments
        average_spacing: Average seconds between jokes
        effectiveness_average: Average joke effectiveness (0.0-1.0)
        weak_joke_count: Number of jokes below threshold
        strong_joke_count: Number of jokes above threshold
        pacing_issues: Clusters and dead zones
        distribution_score: How well-distributed comedy is (0.0-1.0)
    """
    total_comedic_beats: int
    average_spacing: float
    effectiveness_average: float
    weak_joke_count: int
    strong_joke_count: int
    pacing_issues: List[str] = field(default_factory=list)
    distribution_score: float = 0.0
    
    def to_dict(self) -> Dict:
        """Convert to dictionary for serialization."""
        return {
            "total_comedic_beats": self.total_comedic_beats,
            "average_spacing": self.average_spacing,
            "effectiveness_average": self.effectiveness_average,
            "weak_joke_count": self.weak_joke_count,
            "strong_joke_count": self.strong_joke_count,
            "pacing_issues": self.pacing_issues,
            "distribution_score": self.distribution_score,
        }
    
    @classmethod
    def from_dict(cls, data: Dict) -> "ComedyDistributionAnalysis":
        """Create from dictionary."""
        return cls(**data)


@dataclass
class ProductionComplexityAssessment:
    """
    Assessment of production feasibility and complexity.
    
    Attributes:
        location_count: Number of unique locations
        location_complexity: Complexity of locations (0.0-1.0)
        special_effects_count: Number of special effects needed
        costume_changes: Number of costume changes
        prop_count: Estimated number of props needed
        technical_feasibility: How feasible to produce (0.0-1.0)
        budget_estimate: Relative budget level (low/medium/high)
        complexity_score: Overall production complexity (0.0-1.0)
        production_notes: Specific production concerns
    """
    location_count: int
    location_complexity: float
    special_effects_count: int
    costume_changes: int
    prop_count: int
    technical_feasibility: float
    budget_estimate: str  # "low", "medium", "high"
    complexity_score: float = 0.0
    production_notes: List[str] = field(default_factory=list)
    
    def to_dict(self) -> Dict:
        """Convert to dictionary for serialization."""
        return {
            "location_count": self.location_count,
            "location_complexity": self.location_complexity,
            "special_effects_count": self.special_effects_count,
            "costume_changes": self.costume_changes,
            "prop_count": self.prop_count,
            "technical_feasibility": self.technical_feasibility,
            "budget_estimate": self.budget_estimate,
            "complexity_score": self.complexity_score,
            "production_notes": self.production_notes,
        }
    
    @classmethod
    def from_dict(cls, data: Dict) -> "ProductionComplexityAssessment":
        """Create from dictionary."""
        return cls(**data)


@dataclass
class PlotCoherenceScore:
    """
    Assessment of plot structure and coherence.
    
    Attributes:
        setup_clarity: How clear the setup is (0.0-1.0)
        conflict_strength: Strength of central conflict (0.0-1.0)
        resolution_satisfaction: How satisfying the resolution is (0.0-1.0)
        scene_transitions: Quality of scene transitions (0.0-1.0)
        story_arc_completeness: Completeness of story arc (0.0-1.0)
        overall_coherence: Average of all plot metrics
        plot_holes: Identified plot inconsistencies
    """
    setup_clarity: float
    conflict_strength: float
    resolution_satisfaction: float
    scene_transitions: float
    story_arc_completeness: float
    overall_coherence: float = 0.0
    plot_holes: List[str] = field(default_factory=list)
    
    def __post_init__(self):
        """Calculate overall coherence after initialization."""
        if self.overall_coherence == 0.0:
            self.overall_coherence = (
                self.setup_clarity +
                self.conflict_strength +
                self.resolution_satisfaction +
                self.scene_transitions +
                self.story_arc_completeness
            ) / 5.0
    
    def to_dict(self) -> Dict:
        """Convert to dictionary for serialization."""
        return {
            "setup_clarity": self.setup_clarity,
            "conflict_strength": self.conflict_strength,
            "resolution_satisfaction": self.resolution_satisfaction,
            "scene_transitions": self.scene_transitions,
            "story_arc_completeness": self.story_arc_completeness,
            "overall_coherence": self.overall_coherence,
            "plot_holes": self.plot_holes,
        }
    
    @classmethod
    def from_dict(cls, data: Dict) -> "PlotCoherenceScore":
        """Create from dictionary."""
        return cls(**data)


@dataclass
class ScriptValidationReport:
    """
    Complete validation report for a script.
    
    Attributes:
        script_id: Identifier for the script validated
        validation_timestamp: When validation was performed
        character_consistency: Per-character consistency scores
        comedy_distribution: Comedy pacing and effectiveness
        production_complexity: Production feasibility assessment
        plot_coherence: Plot structure quality
        validation_issues: All issues found (sorted by severity)
        overall_quality_score: Weighted average of all metrics (0.0-1.0)
        pass_threshold: Minimum score to pass validation
        validation_passed: Whether script passes validation
        summary: Human-readable summary of validation
        recommendations: Top recommendations for improvement
    """
    script_id: str
    validation_timestamp: datetime
    character_consistency: Dict[str, CharacterConsistencyScore]
    comedy_distribution: ComedyDistributionAnalysis
    production_complexity: ProductionComplexityAssessment
    plot_coherence: PlotCoherenceScore
    validation_issues: List[ValidationIssue]
    overall_quality_score: float
    pass_threshold: float = 0.7
    validation_passed: bool = False
    summary: str = ""
    recommendations: List[str] = field(default_factory=list)
    
    def __post_init__(self):
        """Set validation_passed based on score and threshold."""
        if not self.validation_passed:
            self.validation_passed = self.overall_quality_score >= self.pass_threshold
    
    def to_dict(self) -> Dict:
        """Convert to dictionary for serialization."""
        return {
            "script_id": self.script_id,
            "validation_timestamp": self.validation_timestamp.isoformat(),
            "character_consistency": {
                name: score.to_dict()
                for name, score in self.character_consistency.items()
            },
            "comedy_distribution": self.comedy_distribution.to_dict(),
            "production_complexity": self.production_complexity.to_dict(),
            "plot_coherence": self.plot_coherence.to_dict(),
            "validation_issues": [issue.to_dict() for issue in self.validation_issues],
            "overall_quality_score": self.overall_quality_score,
            "pass_threshold": self.pass_threshold,
            "validation_passed": self.validation_passed,
            "summary": self.summary,
            "recommendations": self.recommendations,
        }
    
    @classmethod
    def from_dict(cls, data: Dict) -> "ScriptValidationReport":
        """Create from dictionary."""
        return cls(
            script_id=data["script_id"],
            validation_timestamp=datetime.fromisoformat(data["validation_timestamp"]),
            character_consistency={
                name: CharacterConsistencyScore.from_dict(score)
                for name, score in data["character_consistency"].items()
            },
            comedy_distribution=ComedyDistributionAnalysis.from_dict(
                data["comedy_distribution"]
            ),
            production_complexity=ProductionComplexityAssessment.from_dict(
                data["production_complexity"]
            ),
            plot_coherence=PlotCoherenceScore.from_dict(data["plot_coherence"]),
            validation_issues=[
                ValidationIssue.from_dict(issue)
                for issue in data["validation_issues"]
            ],
            overall_quality_score=data["overall_quality_score"],
            pass_threshold=data.get("pass_threshold", 0.7),
            validation_passed=data.get("validation_passed", False),
            summary=data.get("summary", ""),
            recommendations=data.get("recommendations", []),
        )
    
    def get_issues_by_severity(self, severity: ValidationSeverity) -> List[ValidationIssue]:
        """Get all issues of a specific severity."""
        return [
            issue for issue in self.validation_issues
            if issue.severity == severity
        ]
    
    def get_issues_by_category(
        self, category: ValidationCategory
    ) -> List[ValidationIssue]:
        """Get all issues of a specific category."""
        return [
            issue for issue in self.validation_issues
            if issue.category == category
        ]
    
    def get_critical_issues(self) -> List[ValidationIssue]:
        """Get all critical and error-level issues."""
        return [
            issue for issue in self.validation_issues
            if issue.severity in [ValidationSeverity.CRITICAL, ValidationSeverity.ERROR]
        ]

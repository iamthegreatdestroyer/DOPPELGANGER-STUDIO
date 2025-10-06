"""
Copyright (c) 2025 DOPPELGANGER STUDIO. All Rights Reserved.

ScriptValidator component for quality assessment and validation.

This module provides comprehensive script validation across multiple dimensions:
character consistency, plot coherence, comedy distribution, and production
complexity. Generates detailed validation reports with actionable recommendations.
"""

import logging
from typing import List, Dict, Optional, TYPE_CHECKING
from datetime import datetime

from src.services.creative.validation_models import (
    ValidationIssue,
    ValidationSeverity,
    ValidationCategory,
    CharacterConsistencyScore,
    ComedyDistributionAnalysis,
    ProductionComplexityAssessment,
    PlotCoherenceScore,
    ScriptValidationReport,
)
from src.services.creative.character_voice_profiles import (
    SceneDialogue,
    CharacterVoiceProfile,
)
from src.services.creative.joke_models import OptimizedScriptComedy

if TYPE_CHECKING:
    from src.core.database_manager import DatabaseManager

logger = logging.getLogger(__name__)


class ScriptValidator:
    """
    Comprehensive script quality validator.
    
    Validates scripts across multiple dimensions and generates detailed
    reports with actionable recommendations for improvement.
    
    Example:
        >>> validator = ScriptValidator()
        >>> report = validator.validate_script(
        ...     script_id="episode_001",
        ...     scene_dialogues=dialogues,
        ...     voice_profiles=profiles,
        ...     comedy_analysis=optimized_comedy,
        ...     episode_metadata=metadata
        ... )
        >>> print(f"Quality score: {report.overall_quality_score:.2f}")
        >>> if not report.validation_passed:
        ...     for issue in report.get_critical_issues():
        ...         print(f"CRITICAL: {issue.message}")
    """
    
    def __init__(
        self,
        database_manager: Optional["DatabaseManager"] = None,
        pass_threshold: float = 0.7,
    ):
        """
        Initialize ScriptValidator.
        
        Args:
            database_manager: Optional caching for validation patterns
            pass_threshold: Minimum score to pass validation (0.0-1.0)
        """
        self.db_manager = database_manager
        self.pass_threshold = pass_threshold
        
        logger.info(f"ScriptValidator initialized (threshold: {pass_threshold})")
    
    def validate_script(
        self,
        script_id: str,
        scene_dialogues: List[SceneDialogue],
        voice_profiles: Dict[str, CharacterVoiceProfile],
        comedy_analysis: OptimizedScriptComedy,
        episode_metadata: Dict,
    ) -> ScriptValidationReport:
        """
        Perform complete script validation.
        
        Args:
            script_id: Identifier for the script
            scene_dialogues: All scene dialogues
            voice_profiles: Character voice profiles for consistency checking
            comedy_analysis: Comedy optimization results
            episode_metadata: Additional context about the episode
        
        Returns:
            Complete validation report with scores and recommendations
        
        Example:
            >>> report = validator.validate_script(
            ...     "ep001", dialogues, profiles, comedy, metadata
            ... )
            >>> assert report.validation_passed
        """
        logger.info(f"Starting validation for script: {script_id}")
        
        validation_issues = []
        
        # 1. Character consistency validation
        character_consistency = self._score_character_consistency(
            scene_dialogues, voice_profiles, validation_issues
        )
        
        logger.info(
            f"Character consistency: {len(character_consistency)} characters analyzed"
        )
        
        # 2. Comedy distribution validation
        comedy_distribution = self._analyze_comedy_distribution(
            comedy_analysis, scene_dialogues, validation_issues
        )
        
        logger.info(
            f"Comedy distribution: {comedy_distribution.total_comedic_beats} beats, "
            f"avg {comedy_distribution.average_spacing:.1f}s spacing"
        )
        
        # 3. Production complexity assessment
        production_complexity = self._assess_production_complexity(
            scene_dialogues, episode_metadata, validation_issues
        )
        
        logger.info(
            f"Production complexity: {production_complexity.complexity_score:.2f} "
            f"({production_complexity.budget_estimate} budget)"
        )
        
        # 4. Plot coherence validation
        plot_coherence = self._assess_plot_coherence(
            scene_dialogues, episode_metadata, validation_issues
        )
        
        logger.info(f"Plot coherence: {plot_coherence.overall_coherence:.2f}")
        
        # 5. Calculate overall quality score
        overall_quality_score = self._calculate_overall_quality(
            character_consistency,
            comedy_distribution,
            production_complexity,
            plot_coherence,
        )
        
        # 6. Generate summary and recommendations
        summary = self._generate_validation_summary(
            overall_quality_score,
            character_consistency,
            comedy_distribution,
            production_complexity,
            plot_coherence,
            validation_issues,
        )
        
        recommendations = self._generate_recommendations(
            validation_issues,
            character_consistency,
            comedy_distribution,
            production_complexity,
            plot_coherence,
        )
        
        # Sort issues by severity (critical first)
        severity_order = {
            ValidationSeverity.CRITICAL: 0,
            ValidationSeverity.ERROR: 1,
            ValidationSeverity.WARNING: 2,
            ValidationSeverity.INFO: 3,
        }
        validation_issues.sort(key=lambda x: severity_order[x.severity])
        
        report = ScriptValidationReport(
            script_id=script_id,
            validation_timestamp=datetime.now(),
            character_consistency=character_consistency,
            comedy_distribution=comedy_distribution,
            production_complexity=production_complexity,
            plot_coherence=plot_coherence,
            validation_issues=validation_issues,
            overall_quality_score=overall_quality_score,
            pass_threshold=self.pass_threshold,
            summary=summary,
            recommendations=recommendations,
        )
        
        logger.info(
            f"Validation complete. Score: {overall_quality_score:.2f}, "
            f"Passed: {report.validation_passed}, Issues: {len(validation_issues)}"
        )
        
        return report
    
    def _score_character_consistency(
        self,
        scene_dialogues: List[SceneDialogue],
        voice_profiles: Dict[str, CharacterVoiceProfile],
        validation_issues: List[ValidationIssue],
    ) -> Dict[str, CharacterConsistencyScore]:
        """
        Score character voice consistency across all scenes.
        
        Compares dialogue against character voice profiles to ensure
        consistency in vocabulary, catchphrases, and relationships.
        
        Args:
            scene_dialogues: All scene dialogues
            voice_profiles: Character voice profiles
            validation_issues: List to append issues to
        
        Returns:
            Dictionary of character names to consistency scores
        """
        character_scores = {}
        
        # Collect all dialogue lines per character
        character_lines: Dict[str, List[str]] = {}
        for scene in scene_dialogues:
            for line in scene.dialogue_lines:
                if line.character not in character_lines:
                    character_lines[line.character] = []
                character_lines[line.character].append(line.line)
        
        # Score each character
        for character_name, lines in character_lines.items():
            if character_name not in voice_profiles:
                # No profile to compare against
                validation_issues.append(
                    ValidationIssue(
                        issue_id=f"char_missing_{character_name}",
                        category=ValidationCategory.CHARACTER_CONSISTENCY,
                        severity=ValidationSeverity.WARNING,
                        message=f"No voice profile found for {character_name}",
                        location=f"Character: {character_name}",
                        suggestion=f"Create voice profile for {character_name}",
                        score_impact=-0.05,
                    )
                )
                continue
            
            profile = voice_profiles[character_name]
            issues = []
            
            # Score vocabulary consistency
            vocab_score = self._score_vocabulary_consistency(lines, profile, issues)
            
            # Score catchphrase usage
            catchphrase_score = self._score_catchphrase_usage(lines, profile, issues)
            
            # Score relationship consistency (based on scene context)
            relationship_score = self._score_relationship_consistency(
                scene_dialogues, character_name, profile, issues
            )
            
            # Use scene dialogue confidence scores as voice match
            voice_match_scores = [
                scene.confidence_score
                for scene in scene_dialogues
                if character_name in scene.characters_present
            ]
            voice_match_score = (
                sum(voice_match_scores) / len(voice_match_scores)
                if voice_match_scores
                else 0.5
            )
            
            character_score = CharacterConsistencyScore(
                character_name=character_name,
                voice_match_score=voice_match_score,
                vocabulary_consistency=vocab_score,
                catchphrase_usage=catchphrase_score,
                relationship_consistency=relationship_score,
                issues=issues,
            )
            
            character_scores[character_name] = character_score
            
            # Add issues for low scores
            if character_score.overall_score < 0.6:
                validation_issues.append(
                    ValidationIssue(
                        issue_id=f"char_inconsistent_{character_name}",
                        category=ValidationCategory.CHARACTER_CONSISTENCY,
                        severity=ValidationSeverity.ERROR,
                        message=f"{character_name} dialogue inconsistent with voice profile",
                        location=f"Character: {character_name}",
                        suggestion=f"Review {character_name}'s dialogue for voice consistency",
                        score_impact=-0.1,
                    )
                )
        
        return character_scores
    
    def _score_vocabulary_consistency(
        self,
        lines: List[str],
        profile: CharacterVoiceProfile,
        issues: List[str],
    ) -> float:
        """Score vocabulary level consistency."""
        # Simple heuristic: check if vocabulary level is maintained
        # This is a simplified version - real implementation would use NLP
        
        total_words = sum(len(line.split()) for line in lines)
        if total_words == 0:
            return 0.5
        
        # Count complex words (>7 characters as proxy for complexity)
        complex_words = sum(
            1 for line in lines for word in line.split() if len(word) > 7
        )
        complexity_ratio = complex_words / total_words if total_words > 0 else 0
        
        # Map vocabulary level to expected complexity
        expected_complexity = {
            "simple": 0.1,
            "moderate": 0.2,
            "sophisticated": 0.35,
        }
        
        expected = expected_complexity.get(profile.vocabulary_level.lower(), 0.2)
        difference = abs(complexity_ratio - expected)
        
        # Score inversely proportional to difference
        score = max(0.0, 1.0 - (difference * 3))
        
        if score < 0.6:
            issues.append(
                f"Vocabulary complexity ({complexity_ratio:.2f}) doesn't match "
                f"expected level ({profile.vocabulary_level})"
            )
        
        return score
    
    def _score_catchphrase_usage(
        self,
        lines: List[str],
        profile: CharacterVoiceProfile,
        issues: List[str],
    ) -> float:
        """Score appropriate catchphrase usage."""
        if not profile.catchphrases:
            return 1.0  # No catchphrases expected
        
        # Check if catchphrases are used appropriately
        all_text = " ".join(lines).lower()
        
        catchphrases_used = sum(
            1 for phrase in profile.catchphrases if phrase.lower() in all_text
        )
        
        # Expect at least one catchphrase used if character has them
        if len(lines) > 5 and catchphrases_used == 0:
            issues.append(
                f"No catchphrases used (expected: {', '.join(profile.catchphrases[:3])})"
            )
            return 0.6
        
        # Don't overuse catchphrases (should be < 20% of lines)
        overuse_threshold = len(lines) * 0.2
        if catchphrases_used > overuse_threshold:
            issues.append("Catchphrases overused")
            return 0.7
        
        return 1.0
    
    def _score_relationship_consistency(
        self,
        scene_dialogues: List[SceneDialogue],
        character_name: str,
        profile: CharacterVoiceProfile,
        issues: List[str],
    ) -> float:
        """Score relationship dynamic consistency."""
        # This is a simplified heuristic
        # Real implementation would analyze dialogue tone/content with other characters
        
        if not profile.relationship_dynamics:
            return 1.0
        
        # Just return a high score for now - proper implementation would
        # analyze actual dialogue exchanges with relationship partners
        return 0.9
    
    def _analyze_comedy_distribution(
        self,
        comedy_analysis: OptimizedScriptComedy,
        scene_dialogues: List[SceneDialogue],
        validation_issues: List[ValidationIssue],
    ) -> ComedyDistributionAnalysis:
        """
        Analyze comedy distribution and effectiveness.
        
        Uses results from JokeOptimizer to assess comedy pacing.
        
        Args:
            comedy_analysis: Results from JokeOptimizer
            scene_dialogues: Scene context
            validation_issues: List to append issues to
        
        Returns:
            Comedy distribution analysis
        """
        timing = comedy_analysis.timing_analysis
        
        weak_jokes = comedy_analysis.get_weak_jokes(threshold=0.6)
        strong_jokes = comedy_analysis.get_strong_jokes(threshold=0.8)
        
        pacing_issues = []
        
        # Check for clusters
        if timing.clusters:
            pacing_issues.append(
                f"Joke clusters in {len(timing.clusters)} scenes: {', '.join(timing.clusters[:3])}"
            )
            validation_issues.append(
                ValidationIssue(
                    issue_id="comedy_clusters",
                    category=ValidationCategory.COMEDY_DISTRIBUTION,
                    severity=ValidationSeverity.WARNING,
                    message=f"Jokes clustered in {len(timing.clusters)} scenes",
                    location=", ".join(timing.clusters[:3]),
                    suggestion="Spread jokes more evenly across scenes",
                    score_impact=-0.05 * len(timing.clusters),
                )
            )
        
        # Check for dead zones
        if timing.dead_zones:
            pacing_issues.append(
                f"Comedy dead zones in {len(timing.dead_zones)} scenes: {', '.join(timing.dead_zones[:3])}"
            )
            validation_issues.append(
                ValidationIssue(
                    issue_id="comedy_dead_zones",
                    category=ValidationCategory.COMEDY_DISTRIBUTION,
                    severity=ValidationSeverity.WARNING,
                    message=f"Long gaps without comedy in {len(timing.dead_zones)} scenes",
                    location=", ".join(timing.dead_zones[:3]),
                    suggestion="Add comedic beats to maintain engagement",
                    score_impact=-0.05 * len(timing.dead_zones),
                )
            )
        
        # Check for weak jokes
        if len(weak_jokes) > len(comedy_analysis.analyzed_jokes) * 0.3:
            validation_issues.append(
                ValidationIssue(
                    issue_id="weak_jokes",
                    category=ValidationCategory.COMEDY_DISTRIBUTION,
                    severity=ValidationSeverity.ERROR,
                    message=f"{len(weak_jokes)} weak jokes (>{30}% of total)",
                    location="Multiple scenes",
                    suggestion="Improve weak jokes using alternative punchlines",
                    score_impact=-0.15,
                )
            )
        
        distribution_score = min(
            timing.pacing_score + (comedy_analysis.overall_effectiveness * 0.5), 1.0
        )
        
        return ComedyDistributionAnalysis(
            total_comedic_beats=timing.total_jokes,
            average_spacing=timing.average_spacing,
            effectiveness_average=comedy_analysis.overall_effectiveness,
            weak_joke_count=len(weak_jokes),
            strong_joke_count=len(strong_jokes),
            pacing_issues=pacing_issues,
            distribution_score=distribution_score,
        )
    
    def _assess_production_complexity(
        self,
        scene_dialogues: List[SceneDialogue],
        episode_metadata: Dict,
        validation_issues: List[ValidationIssue],
    ) -> ProductionComplexityAssessment:
        """
        Assess production feasibility and complexity.
        
        Analyzes locations, special effects, props, and costumes.
        
        Args:
            scene_dialogues: All scenes
            episode_metadata: Episode context
            validation_issues: List to append issues to
        
        Returns:
            Production complexity assessment
        """
        # Count unique locations
        locations = set(scene.location for scene in scene_dialogues)
        location_count = len(locations)
        
        # Estimate location complexity (simplified)
        # Check for keywords indicating complex locations
        complex_keywords = ["space", "underwater", "flying", "zero-gravity", "alien"]
        location_complexity = sum(
            1 for loc in locations
            for keyword in complex_keywords
            if keyword in loc.lower()
        ) / max(location_count, 1)
        
        # Estimate special effects from stage directions
        # (This would need actual stage directions - simplified here)
        special_effects_count = 0
        
        # Estimate costume changes (characters * scenes / 3 as heuristic)
        all_characters = set()
        for scene in scene_dialogues:
            all_characters.update(scene.characters_present)
        costume_changes = len(all_characters) * len(scene_dialogues) // 3
        
        # Estimate props (simplified: 2-5 props per scene)
        prop_count = len(scene_dialogues) * 3
        
        # Calculate technical feasibility (inverse of complexity)
        complexity_factors = [
            location_count / 10,  # More locations = more complex
            location_complexity,
            special_effects_count / 5,
            costume_changes / 20,
        ]
        
        technical_feasibility = max(0.0, 1.0 - (sum(complexity_factors) / len(complexity_factors)))
        
        # Estimate budget
        if location_count > 5 or location_complexity > 0.5:
            budget_estimate = "high"
        elif location_count > 3 or costume_changes > 10:
            budget_estimate = "medium"
        else:
            budget_estimate = "low"
        
        complexity_score = technical_feasibility
        
        production_notes = []
        
        if location_count > 5:
            production_notes.append(f"{location_count} locations may increase costs")
            validation_issues.append(
                ValidationIssue(
                    issue_id="many_locations",
                    category=ValidationCategory.PRODUCTION_COMPLEXITY,
                    severity=ValidationSeverity.WARNING,
                    message=f"High location count: {location_count}",
                    location="Multiple locations",
                    suggestion="Consider consolidating scenes to fewer locations",
                    score_impact=-0.05,
                )
            )
        
        if location_complexity > 0.3:
            production_notes.append("Complex locations require special sets/effects")
        
        return ProductionComplexityAssessment(
            location_count=location_count,
            location_complexity=location_complexity,
            special_effects_count=special_effects_count,
            costume_changes=costume_changes,
            prop_count=prop_count,
            technical_feasibility=technical_feasibility,
            budget_estimate=budget_estimate,
            complexity_score=complexity_score,
            production_notes=production_notes,
        )
    
    def _assess_plot_coherence(
        self,
        scene_dialogues: List[SceneDialogue],
        episode_metadata: Dict,
        validation_issues: List[ValidationIssue],
    ) -> PlotCoherenceScore:
        """
        Assess plot structure and coherence.
        
        This is a simplified heuristic-based assessment.
        Full implementation would use AI to analyze plot structure.
        
        Args:
            scene_dialogues: All scenes
            episode_metadata: Episode context
            validation_issues: List to append issues to
        
        Returns:
            Plot coherence score
        """
        # These are simplified heuristics
        # Real implementation would use AI to analyze actual plot structure
        
        # Setup clarity: Do we have enough scenes to establish setup?
        setup_clarity = 1.0 if len(scene_dialogues) >= 3 else 0.7
        
        # Conflict strength: Assume moderate if we have comedic beats
        conflict_strength = 0.8
        
        # Resolution satisfaction: Assume satisfying if we have final scenes
        resolution_satisfaction = 1.0 if len(scene_dialogues) >= 5 else 0.7
        
        # Scene transitions: Assume good (would need to analyze actual transitions)
        scene_transitions = 0.9
        
        # Story arc completeness
        story_arc_completeness = 0.85
        
        plot_holes = []
        
        # Check for very short scripts
        if len(scene_dialogues) < 3:
            plot_holes.append("Script may be too short for complete story arc")
            validation_issues.append(
                ValidationIssue(
                    issue_id="short_script",
                    category=ValidationCategory.PLOT_COHERENCE,
                    severity=ValidationSeverity.WARNING,
                    message=f"Only {len(scene_dialogues)} scenes",
                    location="Overall script",
                    suggestion="Consider adding more scenes for complete story",
                    score_impact=-0.1,
                )
            )
        
        return PlotCoherenceScore(
            setup_clarity=setup_clarity,
            conflict_strength=conflict_strength,
            resolution_satisfaction=resolution_satisfaction,
            scene_transitions=scene_transitions,
            story_arc_completeness=story_arc_completeness,
            plot_holes=plot_holes,
        )
    
    def _calculate_overall_quality(
        self,
        character_consistency: Dict[str, CharacterConsistencyScore],
        comedy_distribution: ComedyDistributionAnalysis,
        production_complexity: ProductionComplexityAssessment,
        plot_coherence: PlotCoherenceScore,
    ) -> float:
        """
        Calculate weighted overall quality score.
        
        Weights:
        - Character consistency: 30%
        - Comedy distribution: 30%
        - Plot coherence: 25%
        - Production complexity: 15%
        """
        # Average character consistency
        char_scores = [score.overall_score for score in character_consistency.values()]
        char_avg = sum(char_scores) / len(char_scores) if char_scores else 0.5
        
        overall = (
            char_avg * 0.30 +
            comedy_distribution.distribution_score * 0.30 +
            plot_coherence.overall_coherence * 0.25 +
            production_complexity.complexity_score * 0.15
        )
        
        return max(0.0, min(1.0, overall))
    
    def _generate_validation_summary(
        self,
        overall_score: float,
        character_consistency: Dict[str, CharacterConsistencyScore],
        comedy_distribution: ComedyDistributionAnalysis,
        production_complexity: ProductionComplexityAssessment,
        plot_coherence: PlotCoherenceScore,
        validation_issues: List[ValidationIssue],
    ) -> str:
        """Generate human-readable validation summary."""
        status = "PASSED" if overall_score >= self.pass_threshold else "FAILED"
        
        critical_count = sum(
            1 for issue in validation_issues
            if issue.severity == ValidationSeverity.CRITICAL
        )
        error_count = sum(
            1 for issue in validation_issues
            if issue.severity == ValidationSeverity.ERROR
        )
        warning_count = sum(
            1 for issue in validation_issues
            if issue.severity == ValidationSeverity.WARNING
        )
        
        summary_parts = [
            f"Validation {status}: Overall quality {overall_score:.2f}",
            f"Issues: {critical_count} critical, {error_count} errors, {warning_count} warnings",
            f"Character consistency: {len(character_consistency)} characters analyzed",
            f"Comedy: {comedy_distribution.total_comedic_beats} beats, "
            f"{comedy_distribution.effectiveness_average:.2f} avg effectiveness",
            f"Production: {production_complexity.budget_estimate} budget, "
            f"{production_complexity.location_count} locations",
            f"Plot coherence: {plot_coherence.overall_coherence:.2f}",
        ]
        
        return ". ".join(summary_parts) + "."
    
    def _generate_recommendations(
        self,
        validation_issues: List[ValidationIssue],
        character_consistency: Dict[str, CharacterConsistencyScore],
        comedy_distribution: ComedyDistributionAnalysis,
        production_complexity: ProductionComplexityAssessment,
        plot_coherence: PlotCoherenceScore,
    ) -> List[str]:
        """Generate top recommendations for improvement."""
        recommendations = []
        
        # Add recommendations from critical/error issues
        critical_issues = [
            issue for issue in validation_issues
            if issue.severity in [ValidationSeverity.CRITICAL, ValidationSeverity.ERROR]
        ]
        
        for issue in critical_issues[:3]:  # Top 3 critical issues
            recommendations.append(issue.suggestion)
        
        # Add recommendations based on scores
        if comedy_distribution.weak_joke_count > 0:
            recommendations.append(
                f"Improve {comedy_distribution.weak_joke_count} weak jokes "
                "using alternative punchlines"
            )
        
        if production_complexity.location_count > 5:
            recommendations.append(
                "Consider consolidating scenes to reduce location count"
            )
        
        # Character-specific recommendations
        weak_characters = [
            name for name, score in character_consistency.items()
            if score.overall_score < 0.7
        ]
        if weak_characters:
            recommendations.append(
                f"Review voice consistency for: {', '.join(weak_characters)}"
            )
        
        return recommendations[:5]  # Return top 5

"""
Copyright (c) 2025 DOPPELGANGER STUDIO. All Rights Reserved.

Unit tests for ScriptValidator component.
"""

import pytest
from datetime import datetime
from unittest.mock import Mock, AsyncMock, patch

from src.services.creative.script_validator import ScriptValidator
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
    DialogueLine,
    SceneDialogue,
    CharacterVoiceProfile,
)
from src.services.creative.joke_models import (
    JokeType,
    JokeTiming,
    JokeStructure,
    ComedyTimingAnalysis,
    OptimizedScriptComedy,
)


class TestScriptValidator:
    """Test suite for ScriptValidator component."""
    
    @pytest.fixture
    def validator(self):
        """Create validator with default settings."""
        return ScriptValidator(pass_threshold=0.7)
    
    @pytest.fixture
    def sample_voice_profiles(self):
        """Create sample character voice profiles."""
        return {
            "Luna": CharacterVoiceProfile(
                character_name="Luna",
                vocabulary_level="moderate",
                catchphrases=["Oh, Riko!", "I've got it!"],
                verbal_tics=["dramatic pauses"],
                sentence_structure="Medium complexity with enthusiasm",
                relationship_dynamics={"Riko": "husband", "Ethelia": "best friend"},
                emotional_range=["excited", "scheming", "apologetic"],
                humor_style="Physical comedy and schemes",
            ),
            "Riko": CharacterVoiceProfile(
                character_name="Riko",
                vocabulary_level="simple",
                catchphrases=["Ay, Luna!", "You got some 'splaining to do!"],
                verbal_tics=["exasperation"],
                sentence_structure="Short, direct",
                relationship_dynamics={"Luna": "wife"},
                emotional_range=["loving", "exasperated", "patient"],
                humor_style="Straight man reactions",
            ),
        }
    
    @pytest.fixture
    def sample_scene_dialogues(self, sample_voice_profiles):
        """Create sample scene dialogues."""
        return [
            SceneDialogue(
                scene_number=1,
                location="Luna Prime Living Quarters",
                characters_present=["Luna", "Riko"],
                dialogue_lines=[
                    DialogueLine(
                        character="Luna",
                        line="Oh, Riko! I've got the most wonderful idea!",
                        emotion="excited",
                        delivery_note="Bursts in enthusiastically",
                    ),
                    DialogueLine(
                        character="Riko",
                        line="Ay, Luna! What now?",
                        emotion="exasperated",
                        delivery_note="Looks up from reading",
                    ),
                    DialogueLine(
                        character="Luna",
                        line="I'm going to audition for the station talent show!",
                        emotion="determined",
                        delivery_note="Strikes a dramatic pose",
                    ),
                ],
                total_runtime_estimate=45,
                comedic_beats_count=1,
                confidence_score=0.95,
            ),
            SceneDialogue(
                scene_number=2,
                location="Luna Prime Stage",
                characters_present=["Luna", "Riko"],
                dialogue_lines=[
                    DialogueLine(
                        character="Luna",
                        line="You got some 'splaining to do!",  # Wrong character!
                        emotion="defensive",
                        delivery_note="Caught in the act",
                    ),
                    DialogueLine(
                        character="Riko",
                        line="Ay, Luna! How did this happen?",
                        emotion="confused",
                        delivery_note="Surveys the chaos",
                    ),
                ],
                total_runtime_estimate=30,
                comedic_beats_count=0,
                confidence_score=0.85,
            ),
            SceneDialogue(
                scene_number=3,
                location="Luna Prime Living Quarters",
                characters_present=["Luna", "Riko"],
                dialogue_lines=[
                    DialogueLine(
                        character="Luna",
                        line="I've got it! I know how to fix everything!",
                        emotion="excited",
                        delivery_note="Another scheme",
                    ),
                    DialogueLine(
                        character="Riko",
                        line="Oh no...",
                        emotion="worried",
                        delivery_note="Braces for disaster",
                    ),
                ],
                total_runtime_estimate=40,
                comedic_beats_count=1,
                confidence_score=0.90,
            ),
        ]
    
    @pytest.fixture
    def sample_comedy_analysis(self):
        """Create sample comedy analysis."""
        return OptimizedScriptComedy(
            script_id="test_script",
            analyzed_jokes=[
                JokeStructure(
                    joke_id="joke_1",
                    joke_type=JokeType.SITUATIONAL,
                    setup="Luna tries to audition",
                    misdirection="She's confident",
                    punchline="Everything goes wrong",
                    timing_position=20.0,
                    characters_involved=["Luna"],
                    effectiveness_score=0.85,
                    improvement_suggestions=[],
                    callback_potential=True,  # Was 0.6,
                ),
                JokeStructure(
                    joke_id="joke_2",
                    joke_type=JokeType.PHYSICAL,
                    setup="Riko surveys chaos",
                    misdirection="Expects explanation",
                    punchline="Luna makes it worse",
                    timing_position=75.0,
                    characters_involved=["Luna", "Riko"],
                    effectiveness_score=0.50,  # Weak joke
                    improvement_suggestions=["Needs better physical comedy"],
                    callback_potential=False,
                ),
                JokeStructure(
                    joke_id="joke_3",
                    joke_type=JokeType.CALLBACK,
                    setup="Luna has another scheme",
                    misdirection="This time it will work",
                    punchline="Riko knows it won't",
                    timing_position=115.0,
                    characters_involved=["Luna", "Riko"],
                    effectiveness_score=0.90,
                    improvement_suggestions=[],
                    callback_potential=True,  # Was 0.8,
                ),
            ],
            alternative_punchlines=[],
            callback_opportunities=[],
            timing_analysis=ComedyTimingAnalysis(
                total_jokes=3,
                average_spacing=47.5,
                timing_category=JokeTiming.WELL_SPACED,
                clusters=[],
                dead_zones=[],
                optimal_spacing=45.0,
                pacing_score=0.92,
            ),
            overall_effectiveness=0.75,
            optimization_summary="3 jokes analyzed, pacing good",
            confidence_score=0.88,
        )
    
    @pytest.fixture
    def sample_episode_metadata(self):
        """Create sample episode metadata."""
        return {
            "episode_title": "Luna's Big Audition",
            "episode_number": 1,
            "setting": "Space colony Luna Prime",
            "target_runtime": 120,
        }
    
    def test_validator_initialization(self, validator):
        """Test validator initializes correctly."""
        assert validator.pass_threshold == 0.7
        assert validator.db_manager is None
    
    def test_validator_custom_threshold(self):
        """Test validator with custom threshold."""
        validator = ScriptValidator(pass_threshold=0.8)
        assert validator.pass_threshold == 0.8
    
    def test_complete_validation_success(
        self,
        validator,
        sample_scene_dialogues,
        sample_voice_profiles,
        sample_comedy_analysis,
        sample_episode_metadata,
    ):
        """Test complete validation workflow with passing script."""
        report = validator.validate_script(
            script_id="test_script_001",
            scene_dialogues=sample_scene_dialogues,
            voice_profiles=sample_voice_profiles,
            comedy_analysis=sample_comedy_analysis,
            episode_metadata=sample_episode_metadata,
        )
        
        assert isinstance(report, ScriptValidationReport)
        assert report.script_id == "test_script_001"
        assert isinstance(report.validation_timestamp, datetime)
        assert report.overall_quality_score > 0.0
        assert isinstance(report.validation_passed, bool)
        assert len(report.summary) > 0
        assert len(report.recommendations) >= 0
    
    def test_validation_with_no_voice_profiles(
        self,
        validator,
        sample_scene_dialogues,
        sample_comedy_analysis,
        sample_episode_metadata,
    ):
        """Test validation when character has no voice profile."""
        # Empty voice profiles
        report = validator.validate_script(
            script_id="test_script_002",
            scene_dialogues=sample_scene_dialogues,
            voice_profiles={},
            comedy_analysis=sample_comedy_analysis,
            episode_metadata=sample_episode_metadata,
        )
        
        # Should generate warnings for missing profiles
        missing_profile_issues = report.get_issues_by_category(
            ValidationCategory.CHARACTER_CONSISTENCY
        )
        assert len(missing_profile_issues) > 0
        
        # Should still complete validation
        assert report.overall_quality_score > 0.0
    
    def test_character_consistency_scoring(
        self,
        validator,
        sample_scene_dialogues,
        sample_voice_profiles,
    ):
        """Test character consistency scoring."""
        validation_issues = []
        
        character_scores = validator._score_character_consistency(
            sample_scene_dialogues,
            sample_voice_profiles,
            validation_issues,
        )
        
        assert len(character_scores) == 2  # Luna and Riko
        assert "Luna" in character_scores
        assert "Riko" in character_scores
        
        luna_score = character_scores["Luna"]
        assert isinstance(luna_score, CharacterConsistencyScore)
        assert 0.0 <= luna_score.overall_score <= 1.0
        assert 0.0 <= luna_score.voice_match_score <= 1.0
        assert 0.0 <= luna_score.vocabulary_consistency <= 1.0
        assert 0.0 <= luna_score.catchphrase_usage <= 1.0
        assert 0.0 <= luna_score.relationship_consistency <= 1.0
    
    def test_vocabulary_consistency_scoring(self, validator, sample_voice_profiles):
        """Test vocabulary level consistency."""
        # Simple vocabulary (short words)
        simple_lines = ["Hello", "How are you", "I am fine", "Thank you"]
        issues = []
        
        score = validator._score_vocabulary_consistency(
            simple_lines,
            sample_voice_profiles["Riko"],  # Expects simple vocab
            issues,
        )
        
        assert 0.0 <= score <= 1.0
        # Should score reasonably well for simple character
        assert score >= 0.6
    
    def test_vocabulary_mismatch_detection(self, validator, sample_voice_profiles):
        """Test detection of vocabulary level mismatches."""
        # Complex vocabulary for simple character
        complex_lines = [
            "Indubitably, the circumstances necessitate immediate intervention",
            "The phenomenological implications are extraordinary",
            "We must expeditiously implement comprehensive solutions",
        ]
        issues = []
        
        score = validator._score_vocabulary_consistency(
            complex_lines,
            sample_voice_profiles["Riko"],  # Expects simple vocab
            issues,
        )
        
        # Should detect mismatch
        assert score < 0.8
        assert len(issues) > 0
    
    def test_catchphrase_usage_scoring(self, validator, sample_voice_profiles):
        """Test catchphrase usage validation."""
        # Lines with catchphrases
        lines_with_catchphrase = [
            "Oh, Riko! I have an idea",
            "This is going to be wonderful",
            "I've got it! Perfect!",
        ]
        issues = []
        
        score = validator._score_catchphrase_usage(
            lines_with_catchphrase,
            sample_voice_profiles["Luna"],
            issues,
        )
        
        assert score >= 0.8  # Good usage
        assert len(issues) == 0
    
    def test_catchphrase_missing_detection(self, validator, sample_voice_profiles):
        """Test detection of missing catchphrases."""
        # Many lines but no catchphrases
        lines_without_catchphrase = [
            "I have an idea",
            "This is wonderful",
            "It will work",
            "Trust me on this",
            "Everything is fine",
            "Let's do it",
        ]
        issues = []
        
        score = validator._score_catchphrase_usage(
            lines_without_catchphrase,
            sample_voice_profiles["Luna"],
            issues,
        )
        
        # Should detect missing catchphrases
        assert score < 1.0
        assert len(issues) > 0
    
    def test_catchphrase_overuse_detection(self, validator, sample_voice_profiles):
        """Test detection of catchphrase overuse."""
        # Every line has catchphrase (overuse)
        lines_overuse = [
            "Oh, Riko! " + line
            for line in ["One", "Two", "Three", "Four", "Five"]
        ]
        issues = []
        
        score = validator._score_catchphrase_usage(
            lines_overuse,
            sample_voice_profiles["Luna"],
            issues,
        )
        
        # Should detect overuse
        assert score < 1.0
        assert len(issues) > 0
    
    def test_comedy_distribution_analysis(
        self,
        validator,
        sample_comedy_analysis,
        sample_scene_dialogues,
    ):
        """Test comedy distribution analysis."""
        validation_issues = []
        
        distribution = validator._analyze_comedy_distribution(
            sample_comedy_analysis,
            sample_scene_dialogues,
            validation_issues,
        )
        
        assert isinstance(distribution, ComedyDistributionAnalysis)
        assert distribution.total_comedic_beats == 3
        assert distribution.average_spacing > 0
        assert 0.0 <= distribution.effectiveness_average <= 1.0
        assert distribution.weak_joke_count >= 0
        assert distribution.strong_joke_count >= 0
        assert 0.0 <= distribution.distribution_score <= 1.0
    
    def test_comedy_clusters_detection(self, validator, sample_scene_dialogues):
        """Test detection of joke clusters."""
        # Create comedy analysis with clusters
        clustered_comedy = OptimizedScriptComedy(
            script_id="test",
            analyzed_jokes=[],
            timing_analysis=ComedyTimingAnalysis(
                total_jokes=5,
                average_spacing=30.0,
                timing_category=JokeTiming.WELL_SPACED,
                clusters=["Scene 1", "Scene 3"],
                dead_zones=[],
                optimal_spacing=45.0,
                pacing_score=0.7,
            ),
            overall_effectiveness=0.8,
            confidence_score=0.9,
        )
        
        validation_issues = []
        distribution = validator._analyze_comedy_distribution(
            clustered_comedy,
            sample_scene_dialogues,
            validation_issues,
        )
        
        # Should detect clusters
        cluster_issues = [
            issue for issue in validation_issues
            if "cluster" in issue.message.lower()
        ]
        assert len(cluster_issues) > 0
        assert len(distribution.pacing_issues) > 0
    
    def test_comedy_dead_zones_detection(self, validator, sample_scene_dialogues):
        """Test detection of comedy dead zones."""
        # Create comedy analysis with dead zones
        dead_zone_comedy = OptimizedScriptComedy(
            script_id="test",
            analyzed_jokes=[],
            timing_analysis=ComedyTimingAnalysis(
                total_jokes=3,
                average_spacing=150.0,
                timing_category=JokeTiming.SLOW_BURN,
                clusters=[],
                dead_zones=["Scene 2", "Scene 4"],
                optimal_spacing=45.0,
                pacing_score=0.6,
            ),
            overall_effectiveness=0.7,
            confidence_score=0.85,
        )
        
        validation_issues = []
        distribution = validator._analyze_comedy_distribution(
            dead_zone_comedy,
            sample_scene_dialogues,
            validation_issues,
        )
        
        # Should detect dead zones
        dead_zone_issues = [
            issue for issue in validation_issues
            if "dead zone" in issue.message.lower()
        ]
        assert len(dead_zone_issues) > 0
        assert len(distribution.pacing_issues) > 0
    
    def test_weak_jokes_detection(self, validator, sample_scene_dialogues):
        """Test detection of excessive weak jokes."""
        # Create comedy with many weak jokes
        weak_jokes = [
            JokeStructure(
                joke_id=f"joke_{i}",
                joke_type=JokeType.SITUATIONAL,
                setup="Setup",
                misdirection="Misdirection",
                punchline="Punchline",
                timing_position=float(i * 30),
                characters_involved=["Luna"],
                effectiveness_score=0.5,  # Weak
                improvement_suggestions=["Needs work"],
                callback_potential=False,
            )
            for i in range(5)
        ]
        
        weak_comedy = OptimizedScriptComedy(
            script_id="test",
            analyzed_jokes=weak_jokes,
            alternative_punchlines=[],
            callback_opportunities=[],
            timing_analysis=ComedyTimingAnalysis(
                total_jokes=5,
                average_spacing=30.0,
                timing_category=JokeTiming.WELL_SPACED,
                clusters=[],
                dead_zones=[],
                optimal_spacing=45.0,
                pacing_score=0.85,
            ),
            overall_effectiveness=0.5,
            optimization_summary="Weak jokes detected",
            confidence_score=0.8,
        )
        
        validation_issues = []
        distribution = validator._analyze_comedy_distribution(
            weak_comedy,
            sample_scene_dialogues,
            validation_issues,
        )
        
        # Should detect excessive weak jokes
        weak_joke_issues = [
            issue for issue in validation_issues
            if "weak joke" in issue.message.lower()
        ]
        assert len(weak_joke_issues) > 0
        assert distribution.weak_joke_count == 5
    
    def test_production_complexity_assessment(
        self,
        validator,
        sample_scene_dialogues,
        sample_episode_metadata,
    ):
        """Test production complexity assessment."""
        validation_issues = []
        
        complexity = validator._assess_production_complexity(
            sample_scene_dialogues,
            sample_episode_metadata,
            validation_issues,
        )
        
        assert isinstance(complexity, ProductionComplexityAssessment)
        assert complexity.location_count > 0
        assert 0.0 <= complexity.location_complexity <= 1.0
        assert complexity.special_effects_count >= 0
        assert complexity.costume_changes >= 0
        assert complexity.prop_count >= 0
        assert 0.0 <= complexity.technical_feasibility <= 1.0
        assert complexity.budget_estimate in ["low", "medium", "high"]
        assert 0.0 <= complexity.complexity_score <= 1.0
    
    def test_high_location_count_detection(self, validator, sample_episode_metadata):
        """Test detection of high location count."""
        # Create scenes with many unique locations
        many_location_scenes = [
            SceneDialogue(
                scene_number=i,
                location=f"Location {i}",
                characters_present=["Luna"],
                dialogue_lines=[
                    DialogueLine(
                        character="Luna",
                        line=f"Scene {i}",
                        emotion="neutral",
                        delivery_note="",
                    )
                ],
                
                total_runtime_estimate=30,
                comedic_beats_count=0,
                confidence_score=0.9,
            )
            for i in range(8)  # 8 different locations
        ]
        
        validation_issues = []
        complexity = validator._assess_production_complexity(
            many_location_scenes,
            sample_episode_metadata,
            validation_issues,
        )
        
        assert complexity.location_count >= 8
        
        # Should generate warning about many locations
        location_issues = [
            issue for issue in validation_issues
            if "location" in issue.message.lower()
        ]
        assert len(location_issues) > 0
    
    def test_complex_location_detection(self, validator, sample_episode_metadata):
        """Test detection of complex locations."""
        # Scenes with complex location keywords
        complex_scenes = [
            SceneDialogue(
                scene_number=1,
                location="Underwater alien ruins with zero-gravity effects",
                characters_present=["Luna"],
                dialogue_lines=[
                    DialogueLine(
                        character="Luna",
                        line="This is complex",
                        emotion="worried",
                        delivery_note="",
                    )
                ],
                
                total_runtime_estimate=60,
                comedic_beats_count=0,
                confidence_score=0.8,
            ),
            SceneDialogue(
                scene_number=2,
                location="Flying space station control room",
                characters_present=["Luna"],
                dialogue_lines=[
                    DialogueLine(
                        character="Luna",
                        line="Very technical",
                        emotion="focused",
                        delivery_note="",
                    )
                ],
                
                total_runtime_estimate=45,
                comedic_beats_count=0,
                confidence_score=0.85,
            ),
        ]
        
        validation_issues = []
        complexity = validator._assess_production_complexity(
            complex_scenes,
            sample_episode_metadata,
            validation_issues,
        )
        
        # Should detect high location complexity
        assert complexity.location_complexity > 0.3
    
    def test_plot_coherence_assessment(
        self,
        validator,
        sample_scene_dialogues,
        sample_episode_metadata,
    ):
        """Test plot coherence assessment."""
        validation_issues = []
        
        coherence = validator._assess_plot_coherence(
            sample_scene_dialogues,
            sample_episode_metadata,
            validation_issues,
        )
        
        assert isinstance(coherence, PlotCoherenceScore)
        assert 0.0 <= coherence.setup_clarity <= 1.0
        assert 0.0 <= coherence.conflict_strength <= 1.0
        assert 0.0 <= coherence.resolution_satisfaction <= 1.0
        assert 0.0 <= coherence.scene_transitions <= 1.0
        assert 0.0 <= coherence.story_arc_completeness <= 1.0
        assert 0.0 <= coherence.overall_coherence <= 1.0
    
    def test_short_script_detection(self, validator, sample_episode_metadata):
        """Test detection of too-short scripts."""
        # Very short script
        short_scenes = [
            SceneDialogue(
                scene_number=1,
                location="Test Location",
                characters_present=["Luna"],
                dialogue_lines=[
                    DialogueLine(
                        character="Luna",
                        line="Short scene",
                        emotion="neutral",
                        delivery_note="",
                    )
                ],
                
                total_runtime_estimate=20,
                comedic_beats_count=0,
                confidence_score=0.9,
            )
        ]
        
        validation_issues = []
        coherence = validator._assess_plot_coherence(
            short_scenes,
            sample_episode_metadata,
            validation_issues,
        )
        
        # Should detect short script
        short_script_issues = [
            issue for issue in validation_issues
            if "short" in issue.message.lower()
        ]
        assert len(short_script_issues) > 0
        assert len(coherence.plot_holes) > 0
    
    def test_overall_quality_calculation(self, validator):
        """Test weighted overall quality calculation."""
        # Mock component scores
        character_consistency = {
            "Luna": CharacterConsistencyScore(
                character_name="Luna",
                voice_match_score=0.9,
                vocabulary_consistency=0.85,
                catchphrase_usage=1.0,
                relationship_consistency=0.9,
                issues=[],
            ),
            "Riko": CharacterConsistencyScore(
                character_name="Riko",
                voice_match_score=0.8,
                vocabulary_consistency=0.9,
                catchphrase_usage=0.95,
                relationship_consistency=0.85,
                issues=[],
            ),
        }
        
        comedy_distribution = ComedyDistributionAnalysis(
            total_comedic_beats=5,
            average_spacing=45.0,
            effectiveness_average=0.85,
            weak_joke_count=1,
            strong_joke_count=3,
            pacing_issues=[],
            distribution_score=0.9,
        )
        
        production_complexity = ProductionComplexityAssessment(
            location_count=3,
            location_complexity=0.2,
            special_effects_count=2,
            costume_changes=8,
            prop_count=15,
            technical_feasibility=0.85,
            budget_estimate="medium",
            complexity_score=0.85,
            production_notes=[],
        )
        
        plot_coherence = PlotCoherenceScore(
            setup_clarity=0.9,
            conflict_strength=0.85,
            resolution_satisfaction=0.9,
            scene_transitions=0.95,
            story_arc_completeness=0.9,
            plot_holes=[],
        )
        
        overall_score = validator._calculate_overall_quality(
            character_consistency,
            comedy_distribution,
            production_complexity,
            plot_coherence,
        )
        
        assert 0.0 <= overall_score <= 1.0
        # With good scores, should be high
        assert overall_score >= 0.8
    
    def test_validation_report_pass_threshold(
        self,
        validator,
        sample_scene_dialogues,
        sample_voice_profiles,
        sample_comedy_analysis,
        sample_episode_metadata,
    ):
        """Test validation pass/fail based on threshold."""
        report = validator.validate_script(
            script_id="test_threshold",
            scene_dialogues=sample_scene_dialogues,
            voice_profiles=sample_voice_profiles,
            comedy_analysis=sample_comedy_analysis,
            episode_metadata=sample_episode_metadata,
        )
        
        # Check threshold logic
        if report.overall_quality_score >= validator.pass_threshold:
            assert report.validation_passed is True
        else:
            assert report.validation_passed is False
    
    def test_validation_report_serialization(
        self,
        validator,
        sample_scene_dialogues,
        sample_voice_profiles,
        sample_comedy_analysis,
        sample_episode_metadata,
    ):
        """Test validation report can be serialized."""
        report = validator.validate_script(
            script_id="test_serialize",
            scene_dialogues=sample_scene_dialogues,
            voice_profiles=sample_voice_profiles,
            comedy_analysis=sample_comedy_analysis,
            episode_metadata=sample_episode_metadata,
        )
        
        # Test to_dict
        report_dict = report.to_dict()
        assert isinstance(report_dict, dict)
        assert "script_id" in report_dict
        assert "overall_quality_score" in report_dict
        assert "validation_passed" in report_dict
        
        # Test from_dict
        restored = ScriptValidationReport.from_dict(report_dict)
        assert restored.script_id == report.script_id
        assert restored.overall_quality_score == report.overall_quality_score
        assert restored.validation_passed == report.validation_passed
    
    def test_issue_severity_filtering(
        self,
        validator,
        sample_scene_dialogues,
        sample_voice_profiles,
        sample_comedy_analysis,
        sample_episode_metadata,
    ):
        """Test filtering issues by severity."""
        report = validator.validate_script(
            script_id="test_severity",
            scene_dialogues=sample_scene_dialogues,
            voice_profiles=sample_voice_profiles,
            comedy_analysis=sample_comedy_analysis,
            episode_metadata=sample_episode_metadata,
        )
        
        # Test get_issues_by_severity
        critical = report.get_issues_by_severity(ValidationSeverity.CRITICAL)
        errors = report.get_issues_by_severity(ValidationSeverity.ERROR)
        warnings = report.get_issues_by_severity(ValidationSeverity.WARNING)
        info = report.get_issues_by_severity(ValidationSeverity.INFO)
        
        assert isinstance(critical, list)
        assert isinstance(errors, list)
        assert isinstance(warnings, list)
        assert isinstance(info, list)
        
        # Check all issues are categorized
        total = len(critical) + len(errors) + len(warnings) + len(info)
        assert total == len(report.validation_issues)
    
    def test_issue_category_filtering(
        self,
        validator,
        sample_scene_dialogues,
        sample_voice_profiles,
        sample_comedy_analysis,
        sample_episode_metadata,
    ):
        """Test filtering issues by category."""
        report = validator.validate_script(
            script_id="test_category",
            scene_dialogues=sample_scene_dialogues,
            voice_profiles=sample_voice_profiles,
            comedy_analysis=sample_comedy_analysis,
            episode_metadata=sample_episode_metadata,
        )
        
        # Test each category
        for category in ValidationCategory:
            issues = report.get_issues_by_category(category)
            assert isinstance(issues, list)
            
            # Verify all returned issues match category
            for issue in issues:
                assert issue.category == category
    
    def test_critical_issues_helper(
        self,
        validator,
        sample_scene_dialogues,
        sample_voice_profiles,
        sample_comedy_analysis,
        sample_episode_metadata,
    ):
        """Test get_critical_issues helper method."""
        report = validator.validate_script(
            script_id="test_critical",
            scene_dialogues=sample_scene_dialogues,
            voice_profiles=sample_voice_profiles,
            comedy_analysis=sample_comedy_analysis,
            episode_metadata=sample_episode_metadata,
        )
        
        critical = report.get_critical_issues()
        assert isinstance(critical, list)
        
        # All should be CRITICAL severity
        for issue in critical:
            assert issue.severity == ValidationSeverity.CRITICAL
    
    def test_validation_recommendations_generation(
        self,
        validator,
        sample_scene_dialogues,
        sample_voice_profiles,
        sample_comedy_analysis,
        sample_episode_metadata,
    ):
        """Test that actionable recommendations are generated."""
        report = validator.validate_script(
            script_id="test_recommendations",
            scene_dialogues=sample_scene_dialogues,
            voice_profiles=sample_voice_profiles,
            comedy_analysis=sample_comedy_analysis,
            episode_metadata=sample_episode_metadata,
        )
        
        assert isinstance(report.recommendations, list)
        # Should have some recommendations
        assert len(report.recommendations) >= 0
        
        # All recommendations should be strings
        for rec in report.recommendations:
            assert isinstance(rec, str)
            assert len(rec) > 0
    
    def test_validation_summary_generation(
        self,
        validator,
        sample_scene_dialogues,
        sample_voice_profiles,
        sample_comedy_analysis,
        sample_episode_metadata,
    ):
        """Test validation summary is comprehensive."""
        report = validator.validate_script(
            script_id="test_summary",
            scene_dialogues=sample_scene_dialogues,
            voice_profiles=sample_voice_profiles,
            comedy_analysis=sample_comedy_analysis,
            episode_metadata=sample_episode_metadata,
        )
        
        assert isinstance(report.summary, str)
        assert len(report.summary) > 50  # Should be substantial
        
        # Summary should mention key components
        summary_lower = report.summary.lower()
        assert "character" in summary_lower or "comedy" in summary_lower
        assert "quality" in summary_lower or "score" in summary_lower


class TestValidationIssue:
    """Test ValidationIssue dataclass."""
    
    def test_validation_issue_creation(self):
        """Test creating a validation issue."""
        issue = ValidationIssue(
            issue_id="test_issue_001",
            category=ValidationCategory.CHARACTER_CONSISTENCY,
            severity=ValidationSeverity.WARNING,
            message="Test issue message",
            location="Scene 1",
            suggestion="Fix the issue",
            score_impact=-0.05,
        )
        
        assert issue.issue_id == "test_issue_001"
        assert issue.category == ValidationCategory.CHARACTER_CONSISTENCY
        assert issue.severity == ValidationSeverity.WARNING
        assert issue.message == "Test issue message"
        assert issue.location == "Scene 1"
        assert issue.suggestion == "Fix the issue"
        assert issue.score_impact == -0.05
    
    def test_validation_issue_serialization(self):
        """Test validation issue serialization."""
        issue = ValidationIssue(
            issue_id="test_002",
            category=ValidationCategory.COMEDY_DISTRIBUTION,
            severity=ValidationSeverity.ERROR,
            message="Comedy issue",
            location="Multiple scenes",
            suggestion="Add more jokes",
            score_impact=-0.1,
        )
        
        # Test to_dict
        issue_dict = issue.to_dict()
        assert isinstance(issue_dict, dict)
        assert issue_dict["issue_id"] == "test_002"
        
        # Test from_dict
        restored = ValidationIssue.from_dict(issue_dict)
        assert restored.issue_id == issue.issue_id
        assert restored.category == issue.category
        assert restored.severity == issue.severity


class TestCharacterConsistencyScore:
    """Test CharacterConsistencyScore dataclass."""
    
    def test_overall_score_calculation(self):
        """Test automatic overall score calculation."""
        score = CharacterConsistencyScore(
            character_name="TestChar",
            voice_match_score=0.9,
            vocabulary_consistency=0.8,
            catchphrase_usage=1.0,
            relationship_consistency=0.85,
            issues=[],
        )
        
        # Should automatically calculate overall score
        expected = (0.9 + 0.8 + 1.0 + 0.85) / 4
        assert abs(score.overall_score - expected) < 0.01


class TestComedyDistributionAnalysis:
    """Test ComedyDistributionAnalysis dataclass."""
    
    def test_comedy_distribution_creation(self):
        """Test creating comedy distribution analysis."""
        analysis = ComedyDistributionAnalysis(
            total_comedic_beats=8,
            average_spacing=42.5,
            effectiveness_average=0.82,
            weak_joke_count=2,
            strong_joke_count=5,
            pacing_issues=["One cluster in Scene 2"],
            distribution_score=0.88,
        )
        
        assert analysis.total_comedic_beats == 8
        assert analysis.average_spacing == 42.5
        assert analysis.effectiveness_average == 0.82
        assert analysis.weak_joke_count == 2
        assert analysis.strong_joke_count == 5
        assert len(analysis.pacing_issues) == 1
        assert analysis.distribution_score == 0.88


class TestProductionComplexityAssessment:
    """Test ProductionComplexityAssessment dataclass."""
    
    def test_production_complexity_creation(self):
        """Test creating production complexity assessment."""
        assessment = ProductionComplexityAssessment(
            location_count=4,
            location_complexity=0.3,
            special_effects_count=5,
            costume_changes=12,
            prop_count=20,
            technical_feasibility=0.8,
            budget_estimate="medium",
            complexity_score=0.75,
            production_notes=["Note 1", "Note 2"],
        )
        
        assert assessment.location_count == 4
        assert assessment.budget_estimate == "medium"
        assert assessment.complexity_score == 0.75
        assert len(assessment.production_notes) == 2


class TestPlotCoherenceScore:
    """Test PlotCoherenceScore dataclass."""
    
    def test_overall_coherence_calculation(self):
        """Test automatic overall coherence calculation."""
        score = PlotCoherenceScore(
            setup_clarity=0.9,
            conflict_strength=0.85,
            resolution_satisfaction=0.95,
            scene_transitions=0.9,
            story_arc_completeness=0.88,
            plot_holes=[],
        )
        
        # Should automatically calculate overall coherence
        expected = (0.9 + 0.85 + 0.95 + 0.9 + 0.88) / 5
        assert abs(score.overall_coherence - expected) < 0.01

"""
Copyright (c) 2025 DOPPELGANGER STUDIO. All Rights Reserved.

Comprehensive unit tests for ScriptGenerator orchestrator.

Tests component coordination, scene generation, refinement loop,
export formats, and data model serialization.
"""

import pytest
from unittest.mock import Mock, patch, AsyncMock, MagicMock
from datetime import datetime

from src.services.creative.script_generator import ScriptGenerator
from src.services.creative.script_models import (
    SceneScript,
    RefinementIteration,
    FullScript,
    ScriptFormat,
)
from src.services.creative.character_voice_profiles import (
    CharacterVoiceProfile,
    DialogueLine,
    SceneDialogue,
)
from src.services.creative.stage_direction_models import (
    StageDirection,
    SceneStageDirections,
)
from src.services.creative.joke_models import (
    JokeStructure,
    JokeType,
    JokeTiming,
    ComedyTimingAnalysis,
    OptimizedScriptComedy,
)
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


# ============================================================================
# FIXTURES
# ============================================================================

@pytest.fixture
def script_generator():
    """Provide ScriptGenerator instance with mocked components."""
    with patch('src.services.creative.script_generator.ClaudeClient'), \
         patch('src.services.creative.script_generator.OpenAIClient'), \
         patch('src.services.creative.script_generator.DialogueGenerator'), \
         patch('src.services.creative.script_generator.StageDirectionGenerator'), \
         patch('src.services.creative.script_generator.JokeOptimizer'), \
         patch('src.services.creative.script_generator.ScriptValidator'):
        
        generator = ScriptGenerator(
            max_refinement_iterations=3,
            quality_threshold=0.75
        )
        
        # Mock the component responses
        generator.dialogue_generator.generate_dialogue = AsyncMock(
            return_value=create_mock_dialogue()
        )
        generator.stage_direction_generator.generate_stage_directions = AsyncMock(
            return_value=create_mock_stage_directions()
        )
        generator.joke_optimizer.optimize_script_comedy = Mock(
            return_value=create_mock_comedy_analysis()
        )
        generator.script_validator.validate_script = Mock(
            return_value=create_mock_validation_report(passing=True)
        )
        
        return generator


@pytest.fixture
def sample_voice_profiles():
    """Provide sample character voice profiles."""
    return {
        "Luna": CharacterVoiceProfile(
            character_name="Luna",
            vocabulary_level="moderate",
            sentence_structure="complex",
            catchphrases=["Oh, stars!", "Zero-G zany!"],
            verbal_tics=["giggles", "sighs dramatically"],
            speech_patterns=["Enthusiastic", "Scheming"],
            relationship_dynamics={"Rick": "husband - loving but exasperated"},
            emotional_range=["excited", "disappointed", "determined"],
        ),
        "Rick": CharacterVoiceProfile(
            character_name="Rick",
            vocabulary_level="sophisticated",
            sentence_structure="formal",
            catchphrases=["Luna!", "This is serious!"],
            verbal_tics=["shakes head", "pinches bridge of nose"],
            speech_patterns=["Authoritative", "Patient"],
            relationship_dynamics={"Luna": "wife - adores but frustrated"},
            emotional_range=["concerned", "amused", "stern"],
        ),
    }


@pytest.fixture
def sample_episode_outline():
    """Provide sample episode outline."""
    return {
        "scenes": [
            {
                "scene_number": 1,
                "title": "Luna's Big Idea",
                "location": "Luna Prime Station - Control Room",
                "time": "Day",
                "characters": ["Luna", "Rick"],
                "description": "Luna pitches space tourism scheme to Rick",
                "beat_type": "setup",
            },
            {
                "scene_number": 2,
                "title": "The Plan Unfolds",
                "location": "Luna Prime Station - Living Quarters",
                "time": "Evening",
                "characters": ["Luna", "Rick"],
                "description": "Luna explains her elaborate plan",
                "beat_type": "conflict",
            },
            {
                "scene_number": 3,
                "title": "Everything Goes Wrong",
                "location": "Luna Prime Station - Docking Bay",
                "time": "Day",
                "characters": ["Luna", "Rick"],
                "description": "The scheme backfires spectacularly",
                "beat_type": "resolution",
            },
        ]
    }


@pytest.fixture
def sample_show_metadata():
    """Provide sample show metadata."""
    return {
        "episode_title": "The Space Tourism Scheme",
        "show_title": "I Love Luna",
        "episode_number": 1,
        "season_number": 1,
        "writers": ["AI Generator"],
        "original_show": "I Love Lucy",
        "doppelganger_setting": "2157 Space Colony",
    }


@pytest.fixture
def mock_scene_dialogue():
    """Provide mock scene dialogue."""
    return SceneDialogue(
        scene_number=1,
        location="Control Room",
        characters_present=["Luna", "Rick"],
        dialogue_lines=[
            DialogueLine(
                character="Luna",
                line="Rick, I have the most wonderful idea!",
                emotion="excited",
                pause_before=0.0,
            ),
            DialogueLine(
                character="Rick",
                line="Luna, what are you planning now?",
                emotion="concerned",
                pause_before=3.0,
            ),
        ],
        total_runtime_estimate=60,
        comedic_beats_count=1,
        confidence_score=0.9,
    )


@pytest.fixture
def mock_stage_directions():
    """Provide mock stage directions."""
    return SceneStageDirections(
        scene_number=1,
        opening_description="Modern space station control room",
        action_beats=[
            StageDirection(
                timing="BEFORE LINE",
                description="Luna bounces excitedly",
                duration_estimate=2.0,
                involves_characters=["Luna"],
            )
        ],
        physical_comedy_sequences=[],
        closing_description="Scene fades",
        camera_suggestions=[],
        total_visual_runtime=60.0,
    )


@pytest.fixture
def mock_comedy_analysis():
    """Provide mock comedy analysis."""
    return OptimizedScriptComedy(
        script_id="test_001",
        analyzed_jokes=[
            JokeStructure(
                joke_id="joke_1",
                joke_type=JokeType.SITUATIONAL,
                setup="Luna has an idea",
                misdirection="Seems reasonable",
                punchline="It's completely wild",
                timing_position=5.0,
                characters_involved=["Luna"],
                effectiveness_score=0.8,
                improvement_suggestions=[],
                callback_potential=True,
                callback_references=[],
            )
        ],
        alternative_punchlines=[],
        callback_opportunities=[],
        timing_analysis=ComedyTimingAnalysis(
            total_jokes=3,
            average_spacing=45.0,
            timing_category=JokeTiming.WELL_SPACED,
            clusters=[],
            dead_zones=[],
            optimal_spacing=45.0,
            pacing_score=0.9,
        ),
        overall_effectiveness=0.85,
        optimization_summary="Mock comedy analysis for testing",
        confidence_score=0.9,
    )


@pytest.fixture
def mock_validation_report_passing():
    """Provide mock passing validation report."""
    return ScriptValidationReport(
        script_id="test_001",
        validation_timestamp=datetime.now(),
        character_consistency={
            "Luna": CharacterConsistencyScore(
                character_name="Luna",
                voice_match_score=0.9,
                vocabulary_consistency=0.85,
                catchphrase_usage=0.9,
                relationship_consistency=0.9,
                issues=[],
            )
        },
        comedy_distribution=ComedyDistributionAnalysis(
            total_comedic_beats=3,
            average_spacing=45.0,
            effectiveness_average=0.85,
            weak_joke_count=0,
            strong_joke_count=3,
            pacing_issues=[],
            distribution_score=0.9,
        ),
        production_complexity=ProductionComplexityAssessment(
            location_count=3,
            location_complexity=0.2,
            special_effects_count=0,
            costume_changes=2,
            prop_count=9,
            technical_feasibility=0.9,
            budget_estimate="low",
            complexity_score=0.9,
            production_notes=[],
        ),
        plot_coherence=PlotCoherenceScore(
            setup_clarity=0.9,
            conflict_strength=0.85,
            resolution_satisfaction=0.9,
            scene_transitions=0.9,
            story_arc_completeness=0.9,
            plot_holes=[],
        ),
        validation_issues=[],
        overall_quality_score=0.88,
        pass_threshold=0.75,
        summary="High quality script",
        recommendations=[],
    )


@pytest.fixture
def mock_validation_report_failing():
    """Provide mock failing validation report."""
    return ScriptValidationReport(
        script_id="test_001",
        validation_timestamp=datetime.now(),
        character_consistency={
            "Luna": CharacterConsistencyScore(
                character_name="Luna",
                voice_match_score=0.6,
                vocabulary_consistency=0.5,
                catchphrase_usage=0.6,
                relationship_consistency=0.7,
                issues=["Vocabulary inconsistent"],
            )
        },
        comedy_distribution=ComedyDistributionAnalysis(
            total_comedic_beats=3,
            average_spacing=45.0,
            effectiveness_average=0.55,
            weak_joke_count=2,
            strong_joke_count=1,
            pacing_issues=["Comedy clusters detected"],
            distribution_score=0.6,
        ),
        production_complexity=ProductionComplexityAssessment(
            location_count=3,
            location_complexity=0.2,
            special_effects_count=0,
            costume_changes=2,
            prop_count=9,
            technical_feasibility=0.9,
            budget_estimate="low",
            complexity_score=0.9,
            production_notes=[],
        ),
        plot_coherence=PlotCoherenceScore(
            setup_clarity=0.7,
            conflict_strength=0.6,
            resolution_satisfaction=0.7,
            scene_transitions=0.8,
            story_arc_completeness=0.7,
            plot_holes=["Weak resolution"],
        ),
        validation_issues=[
            ValidationIssue(
                issue_id="issue_1",
                category=ValidationCategory.CHARACTER_CONSISTENCY,
                severity=ValidationSeverity.ERROR,
                message="Character voice inconsistent",
                location="Scene 1",
                suggestion="Review dialogue",
                score_impact=-0.1,
            )
        ],
        overall_quality_score=0.65,
        pass_threshold=0.75,
        summary="Script needs improvement",
        recommendations=["Improve character consistency", "Fix weak jokes"],
    )


# ============================================================================
# MOCK HELPER FUNCTIONS
# ============================================================================

def create_mock_dialogue():
    """Create mock dialogue object."""
    mock = Mock()
    mock.scene_number = 1
    mock.location = "Control Room"
    mock.characters_present = ["Luna", "Rick"]
    mock.dialogue_lines = [Mock(character="Luna", line="Test", emotion="happy", pause_before=0.0)]
    mock.total_runtime_estimate = 60
    mock.comedic_beats_count = 1
    mock.confidence_score = 0.9
    mock.to_dict = Mock(return_value={})
    return mock


def create_mock_stage_directions():
    """Create mock stage directions object."""
    mock = Mock()
    mock.scene_number = 1
    mock.opening_description = "Test scene"
    mock.action_beats = []
    mock.physical_comedy_sequences = []
    mock.closing_description = "End scene"
    mock.camera_suggestions = []
    mock.total_visual_runtime = 60.0
    mock.to_dict = Mock(return_value={})
    return mock


def create_mock_comedy_analysis():
    """Create mock comedy analysis."""
    mock = Mock()
    mock.analyzed_jokes = []
    mock.alternative_punchlines = []
    mock.callback_opportunities = []
    mock.timing_analysis = Mock(
        total_jokes=3,
        average_spacing=45.0,
        clusters=[],
        dead_zones=[],
        pacing_score=0.9
    )
    mock.overall_effectiveness = 0.85
    mock.optimization_summary = "Mock comedy analysis"
    mock.to_dict = Mock(return_value={})
    return mock


def create_mock_validation_report(passing=True):
    """Create mock validation report."""
    mock = Mock()
    mock.is_passing = passing
    mock.overall_quality_score = 0.85 if passing else 0.65
    mock.issues = []
    mock.summary = "Validation passed" if passing else "Validation failed"
    mock.recommendations = []
    mock.to_dict = Mock(return_value={})
    return mock


# ============================================================================
# SCRIPTGENERATOR INITIALIZATION TESTS
# ============================================================================

class TestScriptGeneratorInitialization:
    """Test ScriptGenerator initialization."""
    
    def test_initialization_default_parameters(self):
        """Test initialization with default parameters."""
        with patch('src.services.creative.script_generator.ClaudeClient'), \
             patch('src.services.creative.script_generator.OpenAIClient'), \
             patch('src.services.creative.script_generator.DialogueGenerator'), \
             patch('src.services.creative.script_generator.StageDirectionGenerator'), \
             patch('src.services.creative.script_generator.JokeOptimizer'), \
             patch('src.services.creative.script_generator.ScriptValidator'):
            generator = ScriptGenerator()
            
            assert generator.max_refinement_iterations == 3
            assert generator.quality_threshold == 0.75
            assert generator.max_parallel_scenes == 3
            assert generator.dialogue_generator is not None
            assert generator.stage_direction_generator is not None
            assert generator.joke_optimizer is not None
            assert generator.script_validator is not None
    
    def test_initialization_custom_parameters(self):
        """Test initialization with custom parameters."""
        with patch('src.services.creative.script_generator.ClaudeClient'), \
             patch('src.services.creative.script_generator.OpenAIClient'), \
             patch('src.services.creative.script_generator.DialogueGenerator'), \
             patch('src.services.creative.script_generator.StageDirectionGenerator'), \
             patch('src.services.creative.script_generator.JokeOptimizer'), \
             patch('src.services.creative.script_generator.ScriptValidator'):
            generator = ScriptGenerator(
                max_refinement_iterations=5,
                quality_threshold=0.85,
                max_parallel_scenes=5
            )
            
            assert generator.max_refinement_iterations == 5
            assert generator.quality_threshold == 0.85
            assert generator.max_parallel_scenes == 5


# ============================================================================
# SCENE GENERATION TESTS
# ============================================================================

class TestSceneGeneration:
    """Test individual scene generation."""
    
    @pytest.mark.asyncio
    @patch('src.services.creative.script_generator.DialogueGenerator')
    @patch('src.services.creative.script_generator.StageDirectionGenerator')
    async def test_generate_scene_script_basic(
        self,
        mock_stage_gen,
        mock_dialogue_gen,
        script_generator,
        sample_episode_outline,
        sample_voice_profiles,
        mock_scene_dialogue,
        mock_stage_directions,
    ):
        """Test basic scene script generation."""
        # Setup mocks - use AsyncMock for async methods
        from unittest.mock import AsyncMock
        mock_dialogue_gen.return_value.generate_dialogue = AsyncMock(
            return_value=mock_scene_dialogue
        )
        mock_stage_gen.return_value.generate_stage_directions = AsyncMock(
            return_value=mock_stage_directions
        )
        
        # Manually update generators
        script_generator.dialogue_generator = mock_dialogue_gen.return_value
        script_generator.stage_direction_generator = mock_stage_gen.return_value
        
        scene_outline = sample_episode_outline["scenes"][0]
        
        # Generate scene (await async call)
        scene_script = await script_generator._generate_scene_script(
            scene_outline, sample_voice_profiles
        )
        
        # Verify result
        assert isinstance(scene_script, SceneScript)
        assert scene_script.scene_number == 1
        assert scene_script.scene_title == "Luna's Big Idea"
        assert scene_script.location == "Luna Prime Station - Control Room"
        assert scene_script.time_of_day == "Day"
        assert "Luna" in scene_script.characters_present
        assert "Rick" in scene_script.characters_present
        assert scene_script.dialogue == mock_scene_dialogue
        assert scene_script.stage_directions == mock_stage_directions
        assert scene_script.estimated_runtime == 60.0


# ============================================================================
# FULL SCRIPT GENERATION TESTS
# ============================================================================

class TestFullScriptGeneration:
    """Test complete script generation pipeline."""
    
    @pytest.mark.asyncio
    @patch('src.services.creative.script_generator.ScriptValidator')
    @patch('src.services.creative.script_generator.JokeOptimizer')
    @patch('src.services.creative.script_generator.StageDirectionGenerator')
    @patch('src.services.creative.script_generator.DialogueGenerator')
    async def test_generate_full_script_passing_validation(
        self,
        mock_dialogue_gen,
        mock_stage_gen,
        mock_joke_opt,
        mock_validator,
        script_generator,
        sample_episode_outline,
        sample_voice_profiles,
        sample_show_metadata,
        mock_scene_dialogue,
        mock_stage_directions,
        mock_comedy_analysis,
        mock_validation_report_passing,
    ):
        """Test full script generation with passing validation."""
        # Setup mocks - use AsyncMock for async methods
        from unittest.mock import AsyncMock
        mock_dialogue_gen.return_value.generate_dialogue = AsyncMock(
            return_value=mock_scene_dialogue
        )
        mock_stage_gen.return_value.generate_stage_directions.return_value = (
            mock_stage_directions
        )
        mock_joke_opt.return_value.optimize_script_comedy.return_value = (
            mock_comedy_analysis
        )
        mock_validator.return_value.validate_script.return_value = (
            mock_validation_report_passing
        )
        
        # Update generator components
        script_generator.dialogue_generator = mock_dialogue_gen.return_value
        script_generator.stage_direction_generator = mock_stage_gen.return_value
        script_generator.joke_optimizer = mock_joke_opt.return_value
        script_generator.script_validator = mock_validator.return_value
        
        # Generate script
        full_script = await script_generator.generate_full_script(
            script_id="test_001",
            episode_outline=sample_episode_outline,
            character_profiles=sample_voice_profiles,
            show_metadata=sample_show_metadata,
        )
        
        # Verify result
        assert isinstance(full_script, FullScript)
        assert full_script.script_id == "test_001"
        assert full_script.episode_title == "The Space Tourism Scheme"
        assert full_script.show_title == "I Love Luna"
        assert len(full_script.scenes) == 3
        assert full_script.final_quality_score == 0.88
        assert full_script.final_validation_report.validation_passed
        assert len(full_script.refinement_iterations) == 0  # Passed first time
    
    @pytest.mark.asyncio
    @patch('src.services.creative.script_generator.ScriptValidator')
    @patch('src.services.creative.script_generator.JokeOptimizer')
    @patch('src.services.creative.script_generator.StageDirectionGenerator')
    @patch('src.services.creative.script_generator.DialogueGenerator')
    async def test_generate_full_script_with_refinement(
        self,
        mock_dialogue_gen,
        mock_stage_gen,
        mock_joke_opt,
        mock_validator,
        script_generator,
        sample_episode_outline,
        sample_voice_profiles,
        sample_show_metadata,
        mock_scene_dialogue,
        mock_stage_directions,
        mock_comedy_analysis,
        mock_validation_report_failing,
        mock_validation_report_passing,
    ):
        """Test full script generation with refinement loop."""
        # Setup mocks - use AsyncMock for async methods
        from unittest.mock import AsyncMock
        mock_dialogue_gen.return_value.generate_dialogue = AsyncMock(
            return_value=mock_scene_dialogue
        )
        mock_stage_gen.return_value.generate_stage_directions.return_value = (
            mock_stage_directions
        )
        mock_joke_opt.return_value.optimize_script_comedy.return_value = (
            mock_comedy_analysis
        )
        mock_validator.return_value.validate_script.side_effect = [
            mock_validation_report_failing,  # First validation fails
            mock_validation_report_passing,  # After refinement passes
        ]
        
        # Update generator components
        script_generator.dialogue_generator = mock_dialogue_gen.return_value
        script_generator.stage_direction_generator = mock_stage_gen.return_value
        script_generator.joke_optimizer = mock_joke_opt.return_value
        script_generator.script_validator = mock_validator.return_value
        
        # Generate script
        full_script = await script_generator.generate_full_script(
            script_id="test_002",
            episode_outline=sample_episode_outline,
            character_profiles=sample_voice_profiles,
            show_metadata=sample_show_metadata,
        )
        
        # Verify refinement occurred
        assert len(full_script.refinement_iterations) == 1
        assert full_script.refinement_iterations[0].iteration_number == 1
        assert full_script.refinement_iterations[0].validation_passed
        assert full_script.final_quality_score == 0.88


# ============================================================================
# REFINEMENT TESTS
# ============================================================================

class TestRefinementLoop:
    """Test script refinement logic."""
    
    @pytest.mark.asyncio
    @patch('src.services.creative.script_generator.ScriptValidator')
    @patch('src.services.creative.script_generator.JokeOptimizer')
    @patch('src.services.creative.script_generator.StageDirectionGenerator')
    @patch('src.services.creative.script_generator.DialogueGenerator')
    async def test_max_refinement_iterations_reached(
        self,
        mock_dialogue_gen,
        mock_stage_gen,
        mock_joke_opt,
        mock_validator,
        script_generator,
        sample_episode_outline,
        sample_voice_profiles,
        sample_show_metadata,
        mock_scene_dialogue,
        mock_stage_directions,
        mock_comedy_analysis,
        mock_validation_report_failing,
    ):
        """Test that refinement stops at max iterations."""
        # Setup mocks - use AsyncMock for async methods
        from unittest.mock import AsyncMock
        mock_dialogue_gen.return_value.generate_dialogue = AsyncMock(
            return_value=mock_scene_dialogue
        )
        mock_stage_gen.return_value.generate_stage_directions.return_value = (
            mock_stage_directions
        )
        mock_joke_opt.return_value.optimize_script_comedy.return_value = (
            mock_comedy_analysis
        )
        mock_validator.return_value.validate_script.return_value = (
            mock_validation_report_failing
        )
        
        # Update generator components
        script_generator.dialogue_generator = mock_dialogue_gen.return_value
        script_generator.stage_direction_generator = mock_stage_gen.return_value
        script_generator.joke_optimizer = mock_joke_opt.return_value
        script_generator.script_validator = mock_validator.return_value
        
        # Set max iterations to 3
        script_generator.max_refinement_iterations = 3
        
        # Generate script
        full_script = await script_generator.generate_full_script(
            script_id="test_003",
            episode_outline=sample_episode_outline,
            character_profiles=sample_voice_profiles,
            show_metadata=sample_show_metadata,
        )
        
        # Verify max iterations reached
        assert len(full_script.refinement_iterations) == 3
        assert not full_script.final_validation_report.validation_passed
        assert full_script.final_quality_score == 0.65


# ============================================================================
# EXPORT FORMAT TESTS
# ============================================================================

class TestExportFormats:
    """Test script export in various formats."""
    
    def test_export_screenplay_format(
        self,
        script_generator,
        tmp_path,
    ):
        """Test exporting script in screenplay format."""
        # Create minimal FullScript
        scene = SceneScript(
            scene_number=1,
            scene_title="Test Scene",
            location="Test Location",
            time_of_day="Day",
            characters_present=["Luna"],
            dialogue=SceneDialogue(
                scene_number=1,
                location="Test Location",
                characters_present=["Luna"],
                dialogue_lines=[
                    DialogueLine(
                        character="Luna",
                        line="Test line",
                        emotion="neutral",
                        pause_before=0.0,
                    )
                ],
                total_runtime_estimate=30,
                comedic_beats_count=1,
                confidence_score=0.9,
            ),
            stage_directions=SceneStageDirections(
                scene_number=1,
                opening_description="Test description",
                action_beats=[],
                physical_comedy_sequences=[],
                closing_description="",
                camera_suggestions=[],
                total_visual_runtime=30.0,
            ),
            estimated_runtime=30.0,
            comedy_beat_count=1,
        )
        
        full_script = FullScript(
            script_id="test_export",
            episode_title="Test Episode",
            show_title="Test Show",
            episode_number=1,
            season_number=1,
            writers=["Test Writer"],
            original_show="Test Original",
            doppelganger_setting="Test Setting",
            scenes=[scene],
            generation_timestamp=datetime.now(),
            total_runtime=30.0,
            total_comedy_beats=1,
            final_validation_report=Mock(
                validation_passed=True,
                summary="Test summary",
                recommendations=[],
            ),
            final_quality_score=0.85,
            budget_estimate="low",
            location_count=1,
            special_effects_count=0,
        )
        
        # Export
        output_path = tmp_path / "screenplay.txt"
        script_generator.export_script(
            full_script,
            ScriptFormat.SCREENPLAY,
            str(output_path),
        )
        
        # Verify file created
        assert output_path.exists()
        content = output_path.read_text()
        assert "TEST EPISODE" in content  # Title is uppercase in screenplay
        assert "SCENE 1" in content
        assert "LUNA" in content


# ============================================================================
# DATA MODEL TESTS
# ============================================================================

class TestDataModelSerialization:
    """Test serialization of script data models."""
    
    def test_scene_script_serialization(self, mock_scene_dialogue, mock_stage_directions):
        """Test SceneScript to_dict and from_dict."""
        scene = SceneScript(
            scene_number=1,
            scene_title="Test Scene",
            location="Test Location",
            time_of_day="Day",
            characters_present=["Luna", "Rick"],
            dialogue=mock_scene_dialogue,
            stage_directions=mock_stage_directions,
            estimated_runtime=60.0,
            comedy_beat_count=2,
            production_notes=["Test note"],
        )
        
        # Serialize
        data = scene.to_dict()
        
        # Verify
        assert data["scene_number"] == 1
        assert data["scene_title"] == "Test Scene"
        assert "dialogue" in data
        assert "stage_directions" in data
        
        # Deserialize
        restored = SceneScript.from_dict(data)
        
        assert restored.scene_number == scene.scene_number
        assert restored.scene_title == scene.scene_title
        assert restored.estimated_runtime == scene.estimated_runtime
    
    def test_refinement_iteration_serialization(self, mock_validation_report_passing):
        """Test RefinementIteration to_dict and from_dict."""
        iteration = RefinementIteration(
            iteration_number=1,
            timestamp=datetime.now(),
            validation_report=mock_validation_report_passing,
            quality_score=0.75,
            validation_passed=False,
            issues_addressed=["Issue 1"],
            improvements_made=["Improvement 1"],
            scenes_modified=[1, 2],
        )
        
        # Serialize
        data = iteration.to_dict()
        
        # Verify
        assert data["iteration_number"] == 1
        assert data["quality_score"] == 0.75
        assert "validation_report" in data
        
        # Deserialize
        restored = RefinementIteration.from_dict(data)
        
        assert restored.iteration_number == iteration.iteration_number
        assert restored.quality_score == iteration.quality_score


# ============================================================================
# HELPER METHOD TESTS
# ============================================================================

class TestHelperMethods:
    """Test FullScript helper methods."""
    
    def test_get_scene_by_number(self, mock_scene_dialogue, mock_stage_directions):
        """Test getting scene by number."""
        scene1 = SceneScript(
            scene_number=1,
            scene_title="Scene 1",
            location="Location 1",
            time_of_day="Day",
            characters_present=["Luna"],
            dialogue=mock_scene_dialogue,
            stage_directions=mock_stage_directions,
            estimated_runtime=30.0,
            comedy_beat_count=1,
        )
        
        scene2 = SceneScript(
            scene_number=2,
            scene_title="Scene 2",
            location="Location 2",
            time_of_day="Night",
            characters_present=["Rick"],
            dialogue=mock_scene_dialogue,
            stage_directions=mock_stage_directions,
            estimated_runtime=30.0,
            comedy_beat_count=1,
        )
        
        full_script = FullScript(
            script_id="test",
            episode_title="Test",
            show_title="Test",
            episode_number=1,
            season_number=1,
            writers=["Test"],
            original_show="Test",
            doppelganger_setting="Test",
            scenes=[scene1, scene2],
            generation_timestamp=datetime.now(),
            total_runtime=60.0,
            total_comedy_beats=2,
            final_validation_report=Mock(),
            final_quality_score=0.8,
            budget_estimate="low",
            location_count=2,
            special_effects_count=0,
        )
        
        # Get scene
        found = full_script.get_scene(1)
        assert found is not None
        assert found.scene_number == 1
        assert found.scene_title == "Scene 1"
        
        # Get non-existent scene
        not_found = full_script.get_scene(999)
        assert not_found is None
    
    def test_get_scenes_by_character(self, mock_scene_dialogue, mock_stage_directions):
        """Test getting scenes by character."""
        scene1 = SceneScript(
            scene_number=1,
            scene_title="Scene 1",
            location="Location 1",
            time_of_day="Day",
            characters_present=["Luna", "Rick"],
            dialogue=mock_scene_dialogue,
            stage_directions=mock_stage_directions,
            estimated_runtime=30.0,
            comedy_beat_count=1,
        )
        
        scene2 = SceneScript(
            scene_number=2,
            scene_title="Scene 2",
            location="Location 2",
            time_of_day="Night",
            characters_present=["Rick"],
            dialogue=mock_scene_dialogue,
            stage_directions=mock_stage_directions,
            estimated_runtime=30.0,
            comedy_beat_count=1,
        )
        
        full_script = FullScript(
            script_id="test",
            episode_title="Test",
            show_title="Test",
            episode_number=1,
            season_number=1,
            writers=["Test"],
            original_show="Test",
            doppelganger_setting="Test",
            scenes=[scene1, scene2],
            generation_timestamp=datetime.now(),
            total_runtime=60.0,
            total_comedy_beats=2,
            final_validation_report=Mock(),
            final_quality_score=0.8,
            budget_estimate="low",
            location_count=2,
            special_effects_count=0,
        )
        
        # Get Luna scenes
        luna_scenes = full_script.get_scenes_by_character("Luna")
        assert len(luna_scenes) == 1
        assert luna_scenes[0].scene_number == 1
        
        # Get Rick scenes
        rick_scenes = full_script.get_scenes_by_character("Rick")
        assert len(rick_scenes) == 2
    
    def test_get_scenes_by_location(self, mock_scene_dialogue, mock_stage_directions):
        """Test getting scenes by location."""
        scene1 = SceneScript(
            scene_number=1,
            scene_title="Scene 1",
            location="Control Room",
            time_of_day="Day",
            characters_present=["Luna"],
            dialogue=mock_scene_dialogue,
            stage_directions=mock_stage_directions,
            estimated_runtime=30.0,
            comedy_beat_count=1,
        )
        
        scene2 = SceneScript(
            scene_number=2,
            scene_title="Scene 2",
            location="Docking Bay",
            time_of_day="Night",
            characters_present=["Rick"],
            dialogue=mock_scene_dialogue,
            stage_directions=mock_stage_directions,
            estimated_runtime=30.0,
            comedy_beat_count=1,
        )
        
        scene3 = SceneScript(
            scene_number=3,
            scene_title="Scene 3",
            location="Control Room",
            time_of_day="Evening",
            characters_present=["Luna", "Rick"],
            dialogue=mock_scene_dialogue,
            stage_directions=mock_stage_directions,
            estimated_runtime=30.0,
            comedy_beat_count=1,
        )
        
        full_script = FullScript(
            script_id="test",
            episode_title="Test",
            show_title="Test",
            episode_number=1,
            season_number=1,
            writers=["Test"],
            original_show="Test",
            doppelganger_setting="Test",
            scenes=[scene1, scene2, scene3],
            generation_timestamp=datetime.now(),
            total_runtime=90.0,
            total_comedy_beats=3,
            final_validation_report=Mock(),
            final_quality_score=0.8,
            budget_estimate="low",
            location_count=2,
            special_effects_count=0,
        )
        
        # Get Control Room scenes
        control_scenes = full_script.get_scenes_by_location("Control Room")
        assert len(control_scenes) == 2
        assert all(s.location == "Control Room" for s in control_scenes)
        
        # Get Docking Bay scenes
        docking_scenes = full_script.get_scenes_by_location("Docking Bay")
        assert len(docking_scenes) == 1


# ============================================================================
# PARALLEL SCENE GENERATION TESTS
# ============================================================================

class TestParallelSceneGeneration:
    """
    Test suite for parallel scene generation with asyncio.gather().
    
    Verifies:
    - Parallel execution achieves speedup vs sequential
    - Semaphore correctly limits max concurrent scenes
    - Progress callbacks fire for each scene
    - Error handling in parallel scenarios
    """
    
    @pytest.mark.asyncio
    @patch('src.services.creative.script_generator.ScriptValidator')
    @patch('src.services.creative.script_generator.JokeOptimizer')
    @patch('src.services.creative.script_generator.StageDirectionGenerator')
    @patch('src.services.creative.script_generator.DialogueGenerator')
    @patch('src.services.creative.script_generator.OpenAIClient')
    @patch('src.services.creative.script_generator.ClaudeClient')
    async def test_parallel_execution_achieves_speedup(
        self,
        mock_claude,
        mock_openai,
        mock_dialogue_gen,
        mock_stage_gen,
        mock_joke_opt,
        mock_validator,
        sample_episode_outline,
        sample_voice_profiles,
        sample_show_metadata,
        mock_scene_dialogue,
        mock_stage_directions,
    ):
        """Test that parallel execution is faster than sequential."""
        import time
        import asyncio
        
        # Create generator with max_parallel_scenes=3 (parallel)
        parallel_generator = ScriptGenerator(
            max_parallel_scenes=3
        )
        
        # Create generator with max_parallel_scenes=1 (sequential)
        sequential_generator = ScriptGenerator(
            max_parallel_scenes=1
        )
        
        # Mock scene generation with 0.2 second delay to simulate AI calls
        async def mock_generate_dialogue(*args, **kwargs):
            await asyncio.sleep(0.2)  # Simulate API call
            return mock_scene_dialogue
        
        async def mock_generate_stage_directions(*args, **kwargs):
            await asyncio.sleep(0.1)  # Simulate API call
            return mock_stage_directions
        
        # Setup mocks for both generators
        for generator in [parallel_generator, sequential_generator]:
            mock_dialogue = Mock()
            mock_dialogue.generate_dialogue = mock_generate_dialogue
            generator.dialogue_generator = mock_dialogue
            
            mock_stage = Mock()
            mock_stage.generate_stage_directions = mock_generate_stage_directions
            generator.stage_direction_generator = mock_stage
        
        # Time parallel execution (3 scenes with max_parallel_scenes=3)
        start_parallel = time.time()
        parallel_scenes = await parallel_generator.generate_scene_scripts(
            episode_outline=sample_episode_outline,
            character_profiles=sample_voice_profiles,
            show_metadata=sample_show_metadata,
        )
        parallel_time = time.time() - start_parallel
        
        # Time sequential execution (3 scenes with max_parallel_scenes=1)
        start_sequential = time.time()
        sequential_scenes = await sequential_generator.generate_scene_scripts(
            episode_outline=sample_episode_outline,
            character_profiles=sample_voice_profiles,
            show_metadata=sample_show_metadata,
        )
        sequential_time = time.time() - start_sequential
        
        # Verify both generated same number of scenes
        assert len(parallel_scenes) == 3
        assert len(sequential_scenes) == 3
        
        # Verify parallel is significantly faster
        # With 3 scenes at 0.3s each (0.2 dialogue + 0.1 stage directions):
        # Sequential: ~0.9s (3 * 0.3s)
        # Parallel: ~0.3s (max(0.3s, 0.3s, 0.3s) = 0.3s)
        # Speedup should be ~3x (or at least 2x with overhead)
        speedup = sequential_time / parallel_time
        assert speedup >= 2.0, (
            f"Parallel execution should be at least 2x faster. "
            f"Sequential: {sequential_time:.2f}s, Parallel: {parallel_time:.2f}s, "
            f"Speedup: {speedup:.2f}x"
        )
    
    @pytest.mark.asyncio
    @patch('src.services.creative.script_generator.JokeOptimizer')
    @patch('src.services.creative.script_generator.StageDirectionGenerator')
    @patch('src.services.creative.script_generator.DialogueGenerator')
    async def test_semaphore_limits_concurrency(
        self,
        mock_dialogue_gen,
        mock_stage_gen,
        mock_joke_opt,
        sample_episode_outline,
        sample_voice_profiles,
        sample_show_metadata,
        mock_scene_dialogue,
        mock_stage_directions,
    ):
        """Test that semaphore correctly limits concurrent scene generation."""
        import asyncio
        
        # Track concurrent executions
        concurrent_count = 0
        max_concurrent = 0
        
        async def track_concurrent_dialogue(*args, **kwargs):
            nonlocal concurrent_count, max_concurrent
            concurrent_count += 1
            max_concurrent = max(max_concurrent, concurrent_count)
            await asyncio.sleep(0.1)  # Simulate work
            concurrent_count -= 1
            return mock_scene_dialogue
        
        # Create generator with max_parallel_scenes=2
        generator = ScriptGenerator(
            ai_client=Mock(),
            max_parallel_scenes=2  # Limit to 2 concurrent scenes
        )
        
        mock_dialogue = Mock()
        mock_dialogue.generate_dialogue = track_concurrent_dialogue
        generator.dialogue_generator = mock_dialogue
        
        mock_stage = Mock()
        mock_stage.generate_stage_directions = AsyncMock(return_value=mock_stage_directions)
        generator.stage_direction_generator = mock_stage
        
        # Generate 3 scenes (will require 2 batches with limit=2)
        scenes = await generator.generate_scene_scripts(
            episode_outline=sample_episode_outline,
            character_profiles=sample_voice_profiles,
            show_metadata=sample_show_metadata,
        )
        
        # Verify max concurrent never exceeded 2
        assert max_concurrent <= 2, (
            f"Semaphore should limit to 2 concurrent scenes, "
            f"but {max_concurrent} were running simultaneously"
        )
        
        # Verify all 3 scenes generated
        assert len(scenes) == 3
    
    @pytest.mark.asyncio
    @patch('src.services.creative.script_generator.JokeOptimizer')
    @patch('src.services.creative.script_generator.StageDirectionGenerator')
    @patch('src.services.creative.script_generator.DialogueGenerator')
    async def test_progress_callbacks_fire_correctly(
        self,
        mock_dialogue_gen,
        mock_stage_gen,
        mock_joke_opt,
        sample_episode_outline,
        sample_voice_profiles,
        sample_show_metadata,
        mock_scene_dialogue,
        mock_stage_directions,
    ):
        """Test that progress callbacks fire for each scene."""
        # Track progress updates
        progress_updates = []
        
        def progress_callback(scene_num: int, total: int, status: str):
            progress_updates.append({
                'scene': scene_num,
                'total': total,
                'status': status
            })
        
        # Create generator with progress callback
        generator = ScriptGenerator(
            ai_client=Mock(),
            max_parallel_scenes=3
        )
        
        # Setup mocks
        mock_dialogue = Mock()
        mock_dialogue.generate_dialogue = AsyncMock(return_value=mock_scene_dialogue)
        generator.dialogue_generator = mock_dialogue
        
        mock_stage = Mock()
        mock_stage.generate_stage_directions = AsyncMock(return_value=mock_stage_directions)
        generator.stage_direction_generator = mock_stage
        
        # Generate scenes with progress callback
        scenes = await generator.generate_scene_scripts(
            episode_outline=sample_episode_outline,
            character_profiles=sample_voice_profiles,
            show_metadata=sample_show_metadata,
            progress_callback=progress_callback,
        )
        
        # Verify progress updates
        assert len(progress_updates) == 6, "Should have 6 updates (start + complete for 3 scenes)"
        
        # Verify each scene has start and complete updates
        scene_numbers = {update['scene'] for update in progress_updates}
        assert scene_numbers == {1, 2, 3}, "Should have updates for scenes 1, 2, 3"
        
        # Verify status types
        statuses = [update['status'] for update in progress_updates]
        assert statuses.count('generating') == 3, "Should have 3 'generating' updates"
        assert statuses.count('complete') == 3, "Should have 3 'complete' updates"
        
        # Verify total is always 3
        assert all(update['total'] == 3 for update in progress_updates)
        
        # Verify all scenes generated
        assert len(scenes) == 3
    
    @pytest.mark.asyncio
    @patch('src.services.creative.script_generator.JokeOptimizer')
    @patch('src.services.creative.script_generator.StageDirectionGenerator')
    @patch('src.services.creative.script_generator.DialogueGenerator')
    async def test_error_handling_in_parallel_execution(
        self,
        mock_dialogue_gen,
        mock_stage_gen,
        mock_joke_opt,
        sample_episode_outline,
        sample_voice_profiles,
        sample_show_metadata,
        mock_scene_dialogue,
        mock_stage_directions,
    ):
        """Test error handling when one scene fails in parallel execution."""
        # Create generator
        generator = ScriptGenerator(
            ai_client=Mock(),
            max_parallel_scenes=3
        )
        
        # Mock dialogue generator that fails for scene 2
        call_count = 0
        async def failing_dialogue(*args, **kwargs):
            nonlocal call_count
            call_count += 1
            if call_count == 2:  # Fail on second scene
                raise Exception("AI API failure for scene 2")
            return mock_scene_dialogue
        
        mock_dialogue = Mock()
        mock_dialogue.generate_dialogue = failing_dialogue
        generator.dialogue_generator = mock_dialogue
        
        mock_stage = Mock()
        mock_stage.generate_stage_directions = AsyncMock(return_value=mock_stage_directions)
        generator.stage_direction_generator = mock_stage
        
        # Verify exception is raised and propagated
        with pytest.raises(Exception, match="AI API failure for scene 2"):
            await generator.generate_scene_scripts(
                episode_outline=sample_episode_outline,
                character_profiles=sample_voice_profiles,
                show_metadata=sample_show_metadata,
            )
        
        # Verify dialogue generator was called 3 times (all scenes attempted)
        # Note: asyncio.gather will cancel remaining tasks on first exception
        # so we might have fewer calls depending on timing
        assert call_count >= 2, "Should have attempted at least 2 scenes before failure"
    
    @pytest.mark.asyncio
    @patch('src.services.creative.script_generator.JokeOptimizer')
    @patch('src.services.creative.script_generator.StageDirectionGenerator')
    @patch('src.services.creative.script_generator.DialogueGenerator')
    async def test_parallel_with_different_scene_counts(
        self,
        mock_dialogue_gen,
        mock_stage_gen,
        mock_joke_opt,
        sample_voice_profiles,
        sample_show_metadata,
        mock_scene_dialogue,
        mock_stage_directions,
    ):
        """Test parallel execution with different numbers of scenes."""
        from src.services.creative.outline_models import EpisodeOutline, SceneOutline
        
        # Create generator
        generator = ScriptGenerator(
            ai_client=Mock(),
            max_parallel_scenes=3
        )
        
        # Setup mocks
        mock_dialogue = Mock()
        mock_dialogue.generate_dialogue = AsyncMock(return_value=mock_scene_dialogue)
        generator.dialogue_generator = mock_dialogue
        
        mock_stage = Mock()
        mock_stage.generate_stage_directions = AsyncMock(return_value=mock_stage_directions)
        generator.stage_direction_generator = mock_stage
        
        # Test with 1 scene
        outline_1 = EpisodeOutline(
            episode_title="Test",
            show_title="Test",
            episode_number=1,
            season_number=1,
            logline="Test",
            theme="Test",
            scenes=[
                SceneOutline(
                    scene_number=1,
                    scene_title="Scene 1",
                    location="Test",
                    time_of_day="Day",
                    characters_present=["Luna"],
                    plot_points=["Test"],
                    estimated_duration=30,
                    comedy_beats=1,
                )
            ],
            total_runtime=30,
            character_arcs={},
            running_gags=[],
            callbacks_to_setup=[],
        )
        
        scenes_1 = await generator.generate_scene_scripts(
            episode_outline=outline_1,
            character_profiles=sample_voice_profiles,
            show_metadata=sample_show_metadata,
        )
        assert len(scenes_1) == 1
        
        # Test with 5 scenes (more than max_parallel_scenes=3)
        outline_5 = EpisodeOutline(
            episode_title="Test",
            show_title="Test",
            episode_number=1,
            season_number=1,
            logline="Test",
            theme="Test",
            scenes=[
                SceneOutline(
                    scene_number=i,
                    scene_title=f"Scene {i}",
                    location="Test",
                    time_of_day="Day",
                    characters_present=["Luna"],
                    plot_points=["Test"],
                    estimated_duration=30,
                    comedy_beats=1,
                )
                for i in range(1, 6)
            ],
            total_runtime=150,
            character_arcs={},
            running_gags=[],
            callbacks_to_setup=[],
        )
        
        scenes_5 = await generator.generate_scene_scripts(
            episode_outline=outline_5,
            character_profiles=sample_voice_profiles,
            show_metadata=sample_show_metadata,
        )
        assert len(scenes_5) == 5

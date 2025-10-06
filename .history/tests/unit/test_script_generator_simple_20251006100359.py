"""
Copyright (c) 2025 DOPPELGANGER STUDIO. All Rights Reserved.

Simplified unit tests for ScriptGenerator orchestrator.

Focuses on component coordination and pipeline logic using mocks.
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime

from src.services.creative.script_generator import ScriptGenerator
from src.services.creative.script_models import (
    SceneScript,
    FullScript,
    ScriptFormat,
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
        generator.dialogue_generator.generate_dialogue = Mock(
            return_value=create_mock_dialogue()
        )
        generator.stage_direction_generator.generate_stage_directions = Mock(
            return_value=create_mock_stage_directions()
        )
        generator.joke_optimizer.optimize_script_comedy = Mock(
            return_value=create_mock_comedy_analysis()
        )
        generator.script_validator.validate_script = Mock(
            return_value=create_mock_validation_report(passing=True)
        )
        
        return generator


def create_mock_dialogue():
    """Create mock dialogue object."""
    mock = Mock()
    mock.scene_number = 1
    mock.location = "Control Room"
    mock.characters_present = ["Luna", "Rick"]
    mock.dialogue_lines = [Mock(character="Luna", line="Test", emotion="happy", timing_in_scene=0.0)]
    mock.total_runtime_estimate = 60.0
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
    mock.timing_analysis = Mock(
        total_jokes=3,
        average_spacing=45.0,
        clusters=[],
        dead_zones=[],
        pacing_score=0.9
    )
    mock.overall_effectiveness = 0.85
    mock.to_dict = Mock(return_value={})
    return mock


def create_mock_validation_report(passing=True):
    """Create mock validation report."""
    mock = Mock()
    mock.script_id = "test_001"
    mock.validation_passed = passing
    mock.overall_quality_score = 0.88 if passing else 0.65
    mock.character_consistency = {}
    mock.comedy_distribution = Mock(
        total_comedic_beats=3,
        average_spacing=45.0,
        effectiveness_average=0.85,
        weak_joke_count=0,
        strong_joke_count=3,
        pacing_issues=[],
        distribution_score=0.9
    )
    mock.production_complexity = Mock(
        budget_estimate="low",
        location_count=3,
        special_effects_count=0
    )
    mock.plot_coherence = Mock()
    mock.validation_issues = []
    mock.summary = "Test summary"
    mock.recommendations = []
    mock.get_critical_issues = Mock(return_value=[])
    mock.get_issues_by_severity = Mock(return_value=[])
    mock.to_dict = Mock(return_value={})
    return mock


@pytest.fixture
def sample_episode_outline():
    """Provide sample episode outline."""
    return {
        "scenes": [
            {
                "scene_number": 1,
                "title": "Luna's Big Idea",
                "location": "Control Room",
                "time": "Day",
                "characters": ["Luna", "Rick"],
                "description": "Luna pitches space tourism scheme",
                "beat_type": "setup",
            },
            {
                "scene_number": 2,
                "title": "The Plan",
                "location": "Living Quarters",
                "time": "Evening",
                "characters": ["Luna", "Rick"],
                "description": "Luna explains plan",
                "beat_type": "conflict",
            },
        ]
    }


@pytest.fixture
def sample_voice_profiles():
    """Provide sample voice profiles."""
    return {
        "Luna": Mock(character_name="Luna"),
        "Rick": Mock(character_name="Rick"),
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


# ============================================================================
# TESTS
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
                quality_threshold=0.85
            )
            
            assert generator.max_refinement_iterations == 5
            assert generator.quality_threshold == 0.85


class TestFullScriptGeneration:
    """Test complete script generation pipeline."""
    
    def test_generate_full_script_passing_validation(
        self,
        script_generator,
        sample_episode_outline,
        sample_voice_profiles,
        sample_show_metadata,
    ):
        """Test full script generation with passing validation."""
        # Mock asyncio.run to avoid async complexity
        with patch('asyncio.run', return_value=create_mock_stage_directions()):
            full_script = script_generator.generate_full_script(
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
        assert len(full_script.scenes) == 2
        assert full_script.final_quality_score == 0.88
        assert len(full_script.refinement_iterations) == 0  # Passed first time
    
    def test_generate_full_script_with_refinement(
        self,
        script_generator,
        sample_episode_outline,
        sample_voice_profiles,
        sample_show_metadata,
    ):
        """Test full script generation with refinement loop."""
        # Make validation fail once, then pass
        script_generator.script_validator.validate_script = Mock(
            side_effect=[
                create_mock_validation_report(passing=False),  # Fail
                create_mock_validation_report(passing=True),   # Pass
            ]
        )
        
        # Mock asyncio.run
        with patch('asyncio.run', return_value=create_mock_stage_directions()):
            full_script = script_generator.generate_full_script(
                script_id="test_002",
                episode_outline=sample_episode_outline,
                character_profiles=sample_voice_profiles,
                show_metadata=sample_show_metadata,
            )
        
        # Verify refinement occurred
        assert len(full_script.refinement_iterations) == 1
        assert full_script.refinement_iterations[0].iteration_number == 1
        assert full_script.final_quality_score == 0.88
    
    def test_max_refinement_iterations_reached(
        self,
        script_generator,
        sample_episode_outline,
        sample_voice_profiles,
        sample_show_metadata,
    ):
        """Test that refinement stops at max iterations."""
        # Always fail validation
        script_generator.script_validator.validate_script = Mock(
            return_value=create_mock_validation_report(passing=False)
        )
        
        # Mock asyncio.run
        with patch('asyncio.run', return_value=create_mock_stage_directions()):
            full_script = script_generator.generate_full_script(
                script_id="test_003",
                episode_outline=sample_episode_outline,
                character_profiles=sample_voice_profiles,
                show_metadata=sample_show_metadata,
            )
        
        # Verify max iterations reached
        assert len(full_script.refinement_iterations) == 3
        assert full_script.final_quality_score == 0.65


class TestComponentCoordination:
    """Test coordination between components."""
    
    def test_dialogue_generator_called_for_each_scene(
        self,
        script_generator,
        sample_episode_outline,
        sample_voice_profiles,
        sample_show_metadata,
    ):
        """Test that dialogue generator is called for each scene."""
        with patch('asyncio.run', return_value=create_mock_stage_directions()):
            full_script = script_generator.generate_full_script(
                script_id="test_004",
                episode_outline=sample_episode_outline,
                character_profiles=sample_voice_profiles,
                show_metadata=sample_show_metadata,
            )
        
        # Should be called once per scene
        assert script_generator.dialogue_generator.generate_dialogue.call_count == 2
    
    def test_joke_optimizer_called_with_all_dialogues(
        self,
        script_generator,
        sample_episode_outline,
        sample_voice_profiles,
        sample_show_metadata,
    ):
        """Test that joke optimizer receives all scene dialogues."""
        with patch('asyncio.run', return_value=create_mock_stage_directions()):
            full_script = script_generator.generate_full_script(
                script_id="test_005",
                episode_outline=sample_episode_outline,
                character_profiles=sample_voice_profiles,
                show_metadata=sample_show_metadata,
            )
        
        # Should be called once with all dialogues
        assert script_generator.joke_optimizer.optimize_script_comedy.call_count == 1
    
    def test_validator_called_with_correct_parameters(
        self,
        script_generator,
        sample_episode_outline,
        sample_voice_profiles,
        sample_show_metadata,
    ):
        """Test that validator is called with correct parameters."""
        with patch('asyncio.run', return_value=create_mock_stage_directions()):
            full_script = script_generator.generate_full_script(
                script_id="test_006",
                episode_outline=sample_episode_outline,
                character_profiles=sample_voice_profiles,
                show_metadata=sample_show_metadata,
            )
        
        # Verify validator was called
        assert script_generator.script_validator.validate_script.called
        call_args = script_generator.script_validator.validate_script.call_args[1]
        assert call_args["script_id"] == "test_006"
        assert "scene_dialogues" in call_args
        assert "voice_profiles" in call_args


class TestExportFormats:
    """Test script export in various formats."""
    
    def test_export_screenplay_format(self, tmp_path):
        """Test exporting script in screenplay format."""
        # Create minimal FullScript with mocks
        mock_scene = Mock(spec=SceneScript)
        mock_scene.scene_number = 1
        mock_scene.to_screenplay_format = Mock(return_value="SCENE 1\nTest content")
        
        mock_validation = Mock()
        mock_validation.validation_passed = True
        mock_validation.summary = "Test"
        mock_validation.recommendations = []
        
        full_script = FullScript(
            script_id="test_export",
            episode_title="Test Episode",
            show_title="Test Show",
            episode_number=1,
            season_number=1,
            writers=["Test Writer"],
            original_show="Test Original",
            doppelganger_setting="Test Setting",
            scenes=[mock_scene],
            generation_timestamp=datetime.now(),
            total_runtime=30.0,
            total_comedy_beats=1,
            final_validation_report=mock_validation,
            final_quality_score=0.85,
            budget_estimate="low",
            location_count=1,
            special_effects_count=0,
        )
        
        # Export
        output_path = tmp_path / "screenplay.txt"
        full_script.export(ScriptFormat.SCREENPLAY, str(output_path))
        
        # Verify file created
        assert output_path.exists()
        content = output_path.read_text()
        assert "TEST EPISODE" in content  # Title is uppercase in screenplay format


class TestHelperMethods:
    """Test FullScript helper methods."""
    
    def test_get_scene_by_number(self):
        """Test getting scene by number."""
        mock_scene1 = Mock(spec=SceneScript)
        mock_scene1.scene_number = 1
        mock_scene1.scene_title = "Scene 1"
        
        mock_scene2 = Mock(spec=SceneScript)
        mock_scene2.scene_number = 2
        mock_scene2.scene_title = "Scene 2"
        
        full_script = FullScript(
            script_id="test",
            episode_title="Test",
            show_title="Test",
            episode_number=1,
            season_number=1,
            writers=["Test"],
            original_show="Test",
            doppelganger_setting="Test",
            scenes=[mock_scene1, mock_scene2],
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
        
        # Get non-existent scene
        not_found = full_script.get_scene(999)
        assert not_found is None
    
    def test_get_scenes_by_character(self):
        """Test getting scenes by character."""
        mock_scene1 = Mock(spec=SceneScript)
        mock_scene1.scene_number = 1
        mock_scene1.characters_present = ["Luna", "Rick"]
        
        mock_scene2 = Mock(spec=SceneScript)
        mock_scene2.scene_number = 2
        mock_scene2.characters_present = ["Rick"]
        
        full_script = FullScript(
            script_id="test",
            episode_title="Test",
            show_title="Test",
            episode_number=1,
            season_number=1,
            writers=["Test"],
            original_show="Test",
            doppelganger_setting="Test",
            scenes=[mock_scene1, mock_scene2],
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
        
        # Get Rick scenes
        rick_scenes = full_script.get_scenes_by_character("Rick")
        assert len(rick_scenes) == 2
    
    def test_get_scenes_by_location(self):
        """Test getting scenes by location."""
        mock_scene1 = Mock(spec=SceneScript)
        mock_scene1.location = "Control Room"
        
        mock_scene2 = Mock(spec=SceneScript)
        mock_scene2.location = "Docking Bay"
        
        mock_scene3 = Mock(spec=SceneScript)
        mock_scene3.location = "Control Room"
        
        full_script = FullScript(
            script_id="test",
            episode_title="Test",
            show_title="Test",
            episode_number=1,
            season_number=1,
            writers=["Test"],
            original_show="Test",
            doppelganger_setting="Test",
            scenes=[mock_scene1, mock_scene2, mock_scene3],
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
        
        # Get Docking Bay scenes
        docking_scenes = full_script.get_scenes_by_location("Docking Bay")
        assert len(docking_scenes) == 1

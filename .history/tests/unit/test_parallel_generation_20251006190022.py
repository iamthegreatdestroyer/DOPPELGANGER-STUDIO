"""
Copyright (c) 2025 DOPPELGANGER STUDIO. All Rights Reserved.

Performance tests for ScriptGenerator parallel scene generation.

Tests parallel scene generation, concurrency limits, and performance
improvements from parallelization.
"""

import pytest
import asyncio
import time
from unittest.mock import Mock, AsyncMock, patch

from src.services.creative.script_generator import ScriptGenerator
from src.services.creative.script_models import SceneScript


# ============================================================================
# FIXTURES
# ============================================================================

@pytest.fixture
def script_generator_parallel():
    """Provide ScriptGenerator with parallel scene generation."""
    with patch('src.services.creative.script_generator.ClaudeClient'), \
         patch('src.services.creative.script_generator.OpenAIClient'), \
         patch('src.services.creative.script_generator.DialogueGenerator'), \
         patch('src.services.creative.script_generator.StageDirectionGenerator'), \
         patch('src.services.creative.script_generator.JokeOptimizer'), \
         patch('src.services.creative.script_generator.ScriptValidator'):
        
        generator = ScriptGenerator(
            max_refinement_iterations=1,
            quality_threshold=0.75,
            max_parallel_scenes=3
        )
        
        # Create mock dialogue
        mock_dialogue = Mock()
        mock_dialogue.scene_number = 1
        mock_dialogue.location = "Test Location"
        mock_dialogue.characters_present = ["Character1"]
        mock_dialogue.dialogue_lines = []
        mock_dialogue.total_runtime_estimate = 60.0
        mock_dialogue.confidence_score = 0.9
        mock_dialogue.to_dict = Mock(return_value={})
        
        # Create mock stage directions
        mock_stage_directions = Mock()
        mock_stage_directions.scene_number = 1
        mock_stage_directions.opening_description = "Test"
        mock_stage_directions.action_beats = []
        mock_stage_directions.physical_comedy_sequences = []
        mock_stage_directions.closing_description = "End"
        mock_stage_directions.camera_suggestions = []
        mock_stage_directions.total_visual_runtime = 60.0
        mock_stage_directions.to_dict = Mock(return_value={})
        
        # Mock components with delays to simulate real work
        async def mock_dialogue_gen(*args, **kwargs):
            await asyncio.sleep(0.1)  # Simulate AI call
            return mock_dialogue
        
        async def mock_stage_gen(*args, **kwargs):
            await asyncio.sleep(0.1)  # Simulate AI call
            return mock_stage_directions
        
        generator.dialogue_generator.generate_dialogue = mock_dialogue_gen
        generator.stage_direction_generator.generate_stage_directions = AsyncMock(
            side_effect=mock_stage_gen
        )
        
        # Mock other components
        mock_comedy = Mock()
        mock_comedy.analyzed_jokes = []
        mock_comedy.timing_analysis = Mock(
            total_jokes=0,
            average_spacing=0,
            clusters=[],
            dead_zones=[],
            pacing_score=0.9
        )
        mock_comedy.overall_effectiveness = 0.85
        mock_comedy.to_dict = Mock(return_value={})
        
        generator.joke_optimizer.optimize_script_comedy = Mock(
            return_value=mock_comedy
        )
        
        mock_validation = Mock()
        mock_validation.script_id = "test"
        mock_validation.validation_passed = True
        mock_validation.overall_quality_score = 0.88
        mock_validation.comedy_distribution = Mock(
            total_comedic_beats=0,
            average_spacing=0,
            effectiveness_average=0,
            weak_joke_count=0,
            strong_joke_count=0,
            pacing_issues=[],
            distribution_score=0.9
        )
        mock_validation.production_complexity = Mock(
            budget_estimate="low",
            location_count=1,
            special_effects_count=0
        )
        mock_validation.plot_coherence = Mock()
        mock_validation.validation_issues = []
        mock_validation.summary = "Test"
        mock_validation.recommendations = []
        mock_validation.get_critical_issues = Mock(return_value=[])
        mock_validation.get_issues_by_severity = Mock(return_value=[])
        mock_validation.to_dict = Mock(return_value={})
        
        generator.script_validator.validate_script = Mock(
            return_value=mock_validation
        )
        
        return generator


@pytest.fixture
def large_episode_outline():
    """Provide large episode outline with many scenes."""
    return {
        "scenes": [
            {
                "scene_number": i,
                "title": f"Scene {i}",
                "location": f"Location {i}",
                "time": "Day",
                "characters": ["Character1", "Character2"],
                "description": f"Scene {i} description",
                "beat_type": "general",
            }
            for i in range(1, 10)  # 9 scenes
        ]
    }


@pytest.fixture
def sample_profiles():
    """Provide sample character profiles."""
    return {
        "Character1": Mock(character_name="Character1"),
        "Character2": Mock(character_name="Character2"),
    }


@pytest.fixture
def sample_metadata():
    """Provide sample show metadata."""
    return {
        "episode_title": "Test Episode",
        "show_title": "Test Show",
        "episode_number": 1,
        "season_number": 1,
        "writers": ["AI"],
        "original_show": "Original",
        "doppelganger_setting": "Future",
    }


# ============================================================================
# TESTS
# ============================================================================

class TestParallelSceneGeneration:
    """Test parallel scene generation functionality."""
    
    @pytest.mark.asyncio
    async def test_parallel_scene_generation(
        self,
        script_generator_parallel,
        large_episode_outline,
        sample_profiles,
        sample_metadata,
    ):
        """Test that scenes are generated in parallel."""
        start_time = time.time()
        
        full_script = await script_generator_parallel.generate_full_script(
            script_id="parallel_test",
            episode_outline=large_episode_outline,
            character_profiles=sample_profiles,
            show_metadata=sample_metadata,
        )
        
        elapsed = time.time() - start_time
        
        # With 9 scenes at 0.2s each (dialogue + stage directions):
        # Sequential: 9 * 0.2 = 1.8s
        # Parallel (3 at once): ceil(9/3) * 0.2 = 0.6s
        # Should be significantly faster than sequential
        assert elapsed < 1.5, f"Expected parallel execution, took {elapsed:.2f}s"
        
        # Verify all scenes were generated
        assert len(full_script.scenes) == 9
    
    @pytest.mark.asyncio
    async def test_concurrency_limit_respected(
        self,
        script_generator_parallel,
        large_episode_outline,
        sample_profiles,
        sample_metadata,
    ):
        """Test that max_parallel_scenes limit is respected."""
        # Track concurrent executions
        concurrent_count = 0
        max_concurrent = 0
        lock = asyncio.Lock()
        
        async def tracked_dialogue_gen(*args, **kwargs):
            nonlocal concurrent_count, max_concurrent
            
            async with lock:
                concurrent_count += 1
                max_concurrent = max(max_concurrent, concurrent_count)
            
            await asyncio.sleep(0.05)  # Simulate work
            
            async with lock:
                concurrent_count -= 1
            
            mock_dialogue = Mock()
            mock_dialogue.scene_number = 1
            mock_dialogue.location = "Test"
            mock_dialogue.characters_present = []
            mock_dialogue.dialogue_lines = []
            mock_dialogue.total_runtime_estimate = 60.0
            mock_dialogue.confidence_score = 0.9
            mock_dialogue.to_dict = Mock(return_value={})
            return mock_dialogue
        
        script_generator_parallel.dialogue_generator.generate_dialogue = tracked_dialogue_gen
        
        await script_generator_parallel.generate_full_script(
            script_id="concurrency_test",
            episode_outline=large_episode_outline,
            character_profiles=sample_profiles,
            show_metadata=sample_metadata,
        )
        
        # Should never exceed max_parallel_scenes
        assert max_concurrent <= script_generator_parallel.max_parallel_scenes
        assert max_concurrent == 3  # Should hit the limit with 9 scenes
    
    @pytest.mark.asyncio
    async def test_progress_callback_invoked(
        self,
        script_generator_parallel,
        large_episode_outline,
        sample_profiles,
        sample_metadata,
    ):
        """Test that progress callback is invoked during generation."""
        progress_calls = []
        
        def progress_callback(status: str, current: int, total: int):
            progress_calls.append({
                "status": status,
                "current": current,
                "total": total,
            })
        
        await script_generator_parallel.generate_full_script(
            script_id="progress_test",
            episode_outline=large_episode_outline,
            character_profiles=sample_profiles,
            show_metadata=sample_metadata,
            progress_callback=progress_callback,
        )
        
        # Should have 9 progress calls (one per scene)
        assert len(progress_calls) == 9
        
        # Verify structure
        for i, call in enumerate(progress_calls):
            assert "status" in call
            assert call["current"] == i
            assert call["total"] == 9
    
    @pytest.mark.asyncio
    async def test_small_episode_still_works(
        self,
        script_generator_parallel,
        sample_profiles,
        sample_metadata,
    ):
        """Test that small episodes with fewer scenes than parallel limit work."""
        small_outline = {
            "scenes": [
                {
                    "scene_number": 1,
                    "title": "Only Scene",
                    "location": "Location",
                    "time": "Day",
                    "characters": ["Character1"],
                    "description": "Single scene",
                    "beat_type": "general",
                }
            ]
        }
        
        full_script = await script_generator_parallel.generate_full_script(
            script_id="small_test",
            episode_outline=small_outline,
            character_profiles=sample_profiles,
            show_metadata=sample_metadata,
        )
        
        assert len(full_script.scenes) == 1
        assert full_script.final_validation_report.validation_passed
    
    @pytest.mark.asyncio
    async def test_configurable_parallel_limit(
        self,
        sample_profiles,
        sample_metadata,
    ):
        """Test that max_parallel_scenes can be configured."""
        with patch('src.services.creative.script_generator.ClaudeClient'), \
             patch('src.services.creative.script_generator.OpenAIClient'), \
             patch('src.services.creative.script_generator.DialogueGenerator'), \
             patch('src.services.creative.script_generator.StageDirectionGenerator'), \
             patch('src.services.creative.script_generator.JokeOptimizer'), \
             patch('src.services.creative.script_generator.ScriptValidator'):
            
            # Test with different limits
            for limit in [1, 2, 5, 10]:
                generator = ScriptGenerator(max_parallel_scenes=limit)
                assert generator.max_parallel_scenes == limit


class TestPerformanceComparison:
    """Test performance improvements from parallelization."""
    
    @pytest.mark.asyncio
    async def test_parallel_faster_than_sequential(
        self,
        sample_profiles,
        sample_metadata,
    ):
        """Test that parallel generation is faster than sequential would be."""
        # Create generator with timing
        with patch('src.services.creative.script_generator.ClaudeClient'), \
             patch('src.services.creative.script_generator.OpenAIClient'), \
             patch('src.services.creative.script_generator.DialogueGenerator'), \
             patch('src.services.creative.script_generator.StageDirectionGenerator'), \
             patch('src.services.creative.script_generator.JokeOptimizer'), \
             patch('src.services.creative.script_generator.ScriptValidator'):
            
            generator = ScriptGenerator(max_parallel_scenes=3)
            
            # Mock with artificial delays
            async def slow_dialogue(*args, **kwargs):
                await asyncio.sleep(0.1)
                mock = Mock()
                mock.dialogue_lines = []
                mock.total_runtime_estimate = 60.0
                mock.confidence_score = 0.9
                mock.to_dict = Mock(return_value={})
                return mock
            
            async def slow_stage(*args, **kwargs):
                await asyncio.sleep(0.1)
                mock = Mock()
                mock.action_beats = []
                mock.physical_comedy_sequences = []
                mock.camera_suggestions = []
                mock.total_visual_runtime = 60.0
                mock.to_dict = Mock(return_value={})
                return mock
            
            generator.dialogue_generator.generate_dialogue = slow_dialogue
            generator.stage_direction_generator.generate_stage_directions = AsyncMock(
                side_effect=slow_stage
            )
            
            # Mock other components
            generator.joke_optimizer.optimize_script_comedy = Mock(
                return_value=Mock(
                    analyzed_jokes=[],
                    timing_analysis=Mock(
                        total_jokes=0,
                        pacing_score=0.9
                    ),
                    overall_effectiveness=0.85,
                    to_dict=Mock(return_value={})
                )
            )
            
            generator.script_validator.validate_script = Mock(
                return_value=Mock(
                    validation_passed=True,
                    overall_quality_score=0.88,
                    comedy_distribution=Mock(distribution_score=0.9),
                    production_complexity=Mock(
                        budget_estimate="low",
                        location_count=1,
                        special_effects_count=0
                    ),
                    validation_issues=[],
                    get_critical_issues=Mock(return_value=[]),
                    get_issues_by_severity=Mock(return_value=[]),
                    to_dict=Mock(return_value={})
                )
            )
            
            # Test with 6 scenes
            outline = {
                "scenes": [
                    {
                        "scene_number": i,
                        "title": f"Scene {i}",
                        "location": "Location",
                        "time": "Day",
                        "characters": ["Char1"],
                        "description": f"Scene {i}",
                        "beat_type": "general",
                    }
                    for i in range(1, 7)
                ]
            }
            
            start_time = time.time()
            await generator.generate_full_script(
                script_id="perf_test",
                episode_outline=outline,
                character_profiles=sample_profiles,
                show_metadata=sample_metadata,
            )
            elapsed = time.time() - start_time
            
            # Sequential would be: 6 scenes * 0.2s = 1.2s
            # Parallel (3 at once): ceil(6/3) * 0.2 = 0.4s
            # Allow some overhead but should be significantly faster
            assert elapsed < 1.0, f"Parallel took {elapsed:.2f}s, expected <1.0s"


# ============================================================================
# PERFORMANCE METRICS
# ============================================================================

class TestPerformanceMetrics:
    """Test performance tracking and metrics."""
    
    @pytest.mark.asyncio
    async def test_generation_time_tracked(
        self,
        script_generator_parallel,
        large_episode_outline,
        sample_profiles,
        sample_metadata,
    ):
        """Test that generation time is tracked in script metadata."""
        full_script = await script_generator_parallel.generate_full_script(
            script_id="metrics_test",
            episode_outline=large_episode_outline,
            character_profiles=sample_profiles,
            show_metadata=sample_metadata,
        )
        
        # Check that generation notes include timing
        assert len(full_script.generation_notes) > 0
        
        # First note should contain timing info
        timing_note = full_script.generation_notes[0]
        assert "Generated in" in timing_note
        assert "s" in timing_note  # Should include seconds

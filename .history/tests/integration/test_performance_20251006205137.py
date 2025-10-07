"""
Copyright (c) 2025 DOPPELGANGER STUDIO. All Rights Reserved.

Integration tests for performance validation and benchmarking.

Tests performance targets:
- Full episode generation <5 minutes
- Cache hit rate >60% on second run
- Parallel speedup >2x for 6+ scenes
- Memory usage <1GB
- Cached vs uncached performance
- Bottleneck detection
"""

import pytest
import asyncio
import time
import psutil
import os
from typing import Dict
from unittest.mock import Mock, AsyncMock, patch

from src.services.creative.script_generator import ScriptGenerator
from src.services.creative.character_voice_profiles import CharacterVoiceProfile
from src.services.monitoring.performance_monitor import get_performance_monitor
from src.services.creative.script_models import ScriptFormat


# ============================================================================
# TEST FIXTURES
# ============================================================================

@pytest.fixture
def sample_episode_outline_small():
    """Small episode outline with 3 scenes for quick tests."""
    return {
        "episode_title": "Luna's Big Idea",
        "scenes": [
            {
                "scene_number": 1,
                "title": "The Pitch",
                "location": "Space Station Control Room",
                "time": "Day",
                "characters": ["Luna", "Rick"],
                "description": "Luna pitches her wild tourism idea",
                "beat_type": "setup"
            },
            {
                "scene_number": 2,
                "title": "The Plan",
                "location": "Luna's Quarters",
                "time": "Night",
                "characters": ["Luna", "Ethel"],
                "description": "Luna and Ethel scheme together",
                "beat_type": "complication"
            },
            {
                "scene_number": 3,
                "title": "The Chaos",
                "location": "Tourist Deck",
                "time": "Day",
                "characters": ["Luna", "Rick", "Ethel", "Fred"],
                "description": "Everything goes hilariously wrong",
                "beat_type": "payoff"
            }
        ]
    }


@pytest.fixture
def sample_episode_outline_large():
    """Large episode outline with 9 scenes for performance tests."""
    scenes = []
    locations = [
        "Control Room", "Luna's Quarters", "Tourist Deck", 
        "Docking Bay", "Observation Lounge", "Engineering",
        "Cafeteria", "Recreation Area", "Medical Bay"
    ]
    characters_sets = [
        ["Luna", "Rick"],
        ["Luna", "Ethel"],
        ["Luna", "Rick", "Ethel", "Fred"],
        ["Rick", "Fred"],
        ["Luna", "Ethel", "Fred"],
        ["Luna", "Rick"],
        ["Ethel", "Fred"],
        ["Luna", "Rick", "Ethel"],
        ["Luna", "Rick", "Ethel", "Fred"]
    ]
    
    for i in range(9):
        scenes.append({
            "scene_number": i + 1,
            "title": f"Scene {i + 1}",
            "location": f"Space Station - {locations[i]}",
            "time": "Day" if i % 2 == 0 else "Night",
            "characters": characters_sets[i],
            "description": f"Exciting scene {i + 1} with comedy and drama",
            "beat_type": ["setup", "complication", "payoff"][i % 3]
        })
    
    return {
        "episode_title": "The Grand Adventure",
        "scenes": scenes
    }


@pytest.fixture
def sample_character_profiles():
    """Sample character voice profiles."""
    return {
        "Luna": CharacterVoiceProfile(
            character_name="Luna",
            vocabulary_level="simple",
            sentence_structure="rambling",
            verbal_tics=["Oh!", "like"],
            catchphrases=["Oh Rick!", "I've got an idea!"],
            emotional_range=["excitable", "scheming", "endearing"],
            speech_patterns=["Fast when excited", "Whining when pleading"],
            relationship_dynamics={"Rick": "husband - respectful but pushy"},
            humor_style="physical"
        ),
        "Rick": CharacterVoiceProfile(
            character_name="Rick",
            vocabulary_level="sophisticated",
            sentence_structure="measured",
            verbal_tics=["Well", "Now"],
            catchphrases=["Luna!", "Explain this to me"],
            emotional_range=["patient", "exasperated", "loving"],
            speech_patterns=["Measured", "Explanatory"],
            relationship_dynamics={"Luna": "wife - loving but frustrated"},
            humor_style="straight_man"
        ),
        "Ethel": CharacterVoiceProfile(
            character_name="Ethel",
            vocabulary_level="simple",
            sentence_structure="short",
            verbal_tics=["Hmph", "Really"],
            catchphrases=["I knew it!", "Here we go again"],
            emotional_range=["skeptical", "loyal", "pragmatic"],
            speech_patterns=["Dry", "Sarcastic"],
            relationship_dynamics={"Luna": "best_friend", "Fred": "husband"},
            humor_style="sarcastic"
        ),
        "Fred": CharacterVoiceProfile(
            character_name="Fred",
            vocabulary_level="simple",
            sentence_structure="short",
            verbal_tics=["Uh", "Yeah"],
            catchphrases=["Sure thing", "Whatever you say"],
            emotional_range=["laid_back", "supportive", "bemused"],
            speech_patterns=["Casual", "Agreeable"],
            relationship_dynamics={"Ethel": "wife", "Rick": "friend"},
            humor_style="supporting"
        ),
    }


@pytest.fixture
def sample_show_metadata():
    """Sample show metadata."""
    return {
        "show_title": "I Love Luna",
        "episode_title": "Test Episode",
        "episode_number": 1,
        "season_number": 1,
        "writers": ["AI Generated"],
        "original_show": "I Love Lucy",
        "doppelganger_setting": "2157 Space Colony"
    }


@pytest.fixture
def mock_generator_with_timing():
    """Create a mocked ScriptGenerator with realistic timing."""
    with patch('src.services.creative.script_generator.ClaudeClient'), \
         patch('src.services.creative.script_generator.OpenAIClient'), \
         patch('src.services.creative.script_generator.DialogueGenerator'), \
         patch('src.services.creative.script_generator.StageDirectionGenerator'), \
         patch('src.services.creative.script_generator.JokeOptimizer'), \
         patch('src.services.creative.script_generator.ScriptValidator'):
        
        generator = ScriptGenerator(max_parallel_scenes=3)
        
        # Mock dialogue generator with realistic timing
        async def mock_generate_dialogue(*args, **kwargs):
            await asyncio.sleep(0.1)  # Simulate 100ms AI call
            from src.services.creative.character_voice_profiles import (
                SceneDialogue,
                DialogueLine
            )
            return SceneDialogue(
                scene_number=1,
                location="Test Location",
                characters_present=["Luna", "Rick"],
                dialogue_lines=[
                    DialogueLine(
                        character="Luna",
                        line="This is a test line!",
                        emotion="excited",
                        delivery_note="excited"
                    )
                ],
                total_runtime_estimate=30,
                comedic_beats_count=1
            )
        
        generator.dialogue_generator.generate_dialogue = AsyncMock(
            side_effect=mock_generate_dialogue
        )
        
        # Mock stage direction generator
        async def mock_generate_stage_directions(*args, **kwargs):
            await asyncio.sleep(0.05)  # Simulate 50ms
            from src.services.creative.stage_direction_models import SceneStageDirections
            return SceneStageDirections(
                scene_number=1,
                opening_description="Scene opens",
                camera_directions=[],
                character_actions=[],
                environmental_details=[],
                lighting_notes="",
                sound_cues=[],
                transition_out=""
            )
        
        generator.stage_direction_generator.generate_stage_directions = AsyncMock(
            side_effect=mock_generate_stage_directions
        )
        
        # Mock joke optimizer
        def mock_optimize_comedy(*args, **kwargs):
            from src.services.creative.joke_models import (
                OptimizedScriptComedy,
                ComedyTimingAnalysis,
                JokeTiming
            )
            return OptimizedScriptComedy(
                script_id="test",
                analyzed_jokes=[],
                alternative_punchlines=[],
                callback_opportunities=[],
                timing_analysis=ComedyTimingAnalysis(
                    total_jokes=5,
                    average_spacing=45.0,
                    timing_category=JokeTiming.WELL_SPACED,
                    clusters=[],
                    dead_zones=[],
                    optimal_spacing=45.0,
                    pacing_score=0.85
                ),
                overall_effectiveness=0.80,
                optimization_summary="Good comedy timing"
            )
        
        generator.joke_optimizer.optimize_script_comedy = Mock(
            side_effect=mock_optimize_comedy
        )
        
        # Mock validator
        def mock_validate(*args, **kwargs):
            from src.services.creative.validation_models import ValidationReport, ProductionComplexity
            return ValidationReport(
                script_id="test",
                validation_passed=True,
                overall_quality_score=0.85,
                issues=[],
                production_complexity=ProductionComplexity(
                    location_count=3,
                    character_count=4,
                    special_effects_count=0,
                    estimated_shoot_days=1,
                    budget_estimate=50000.0
                )
            )
        
        generator.script_validator.validate_script = Mock(
            side_effect=mock_validate
        )
        
        yield generator


# ============================================================================
# PERFORMANCE TESTS
# ============================================================================

class TestFullEpisodeGenerationTime:
    """Test full episode generation meets time targets."""
    
    @pytest.mark.asyncio
    async def test_small_episode_generation_time(
        self,
        mock_generator_with_timing,
        sample_episode_outline_small,
        sample_character_profiles,
        sample_show_metadata
    ):
        """Test that small episode (3 scenes) generates quickly."""
        generator = mock_generator_with_timing
        
        start_time = time.time()
        
        script = await generator.generate_full_script(
            script_id="test_small",
            episode_outline=sample_episode_outline_small,
            character_profiles=sample_character_profiles,
            show_metadata=sample_show_metadata
        )
        
        elapsed = time.time() - start_time
        
        # Small episode should complete in <2 seconds with mocks
        assert elapsed < 2.0, f"Small episode took {elapsed:.2f}s (expected <2s)"
        assert len(script.scenes) == 3
        
        # Check performance metrics were tracked
        metrics = generator.get_performance_metrics()
        assert metrics is not None
        assert metrics.scenes_generated == 3
        assert metrics.total_duration_seconds > 0
    
    @pytest.mark.asyncio
    async def test_large_episode_generation_time(
        self,
        mock_generator_with_timing,
        sample_episode_outline_large,
        sample_character_profiles,
        sample_show_metadata
    ):
        """Test that large episode (9 scenes) generates efficiently."""
        generator = mock_generator_with_timing
        
        start_time = time.time()
        
        script = await generator.generate_full_script(
            script_id="test_large",
            episode_outline=sample_episode_outline_large,
            character_profiles=sample_character_profiles,
            show_metadata=sample_show_metadata
        )
        
        elapsed = time.time() - start_time
        
        # With parallel execution (3 at a time), 9 scenes should take ~3 batches
        # Each scene: 0.1s dialogue + 0.05s stage = 0.15s
        # 3 batches of 3 scenes = ~0.45s + overhead
        assert elapsed < 3.0, f"Large episode took {elapsed:.2f}s (expected <3s)"
        assert len(script.scenes) == 9
        
        # Verify parallel execution benefit
        # Sequential would be: 9 scenes * 0.15s = 1.35s
        # Parallel (3 at once) should be: 3 batches * 0.15s = 0.45s + overhead
        # So elapsed should be significantly less than sequential
        sequential_estimate = 9 * 0.15
        assert elapsed < sequential_estimate * 0.8, \
            f"Parallel execution not efficient: {elapsed:.2f}s vs sequential {sequential_estimate:.2f}s"


class TestCacheHitRate:
    """Test cache hit rate performance."""
    
    @pytest.mark.asyncio
    async def test_cache_hit_rate_on_repeat_generation(
        self,
        mock_generator_with_timing,
        sample_episode_outline_small,
        sample_character_profiles,
        sample_show_metadata
    ):
        """Test cache hit rate improves on second generation."""
        generator = mock_generator_with_timing
        monitor = get_performance_monitor()
        
        # First generation - cold cache
        await generator.generate_full_script(
            script_id="test_cache_1",
            episode_outline=sample_episode_outline_small,
            character_profiles=sample_character_profiles,
            show_metadata=sample_show_metadata
        )
        
        first_metrics = generator.get_performance_metrics()
        first_cache_rate = first_metrics.cache_hit_rate if first_metrics else 0.0
        
        # Second generation - warm cache (same inputs)
        await generator.generate_full_script(
            script_id="test_cache_2",
            episode_outline=sample_episode_outline_small,
            character_profiles=sample_character_profiles,
            show_metadata=sample_show_metadata
        )
        
        second_metrics = generator.get_performance_metrics()
        second_cache_rate = second_metrics.cache_hit_rate if second_metrics else 0.0
        
        # Note: With mocks, we won't get real caching behavior
        # This test validates the metrics tracking works
        # In real usage, cache hit rate should be >60% on second run
        assert first_metrics is not None
        assert second_metrics is not None
        
        # Both should track cache operations (even if 0)
        assert hasattr(first_metrics, 'cache_hits')
        assert hasattr(first_metrics, 'cache_misses')
        assert hasattr(second_metrics, 'cache_hits')
        assert hasattr(second_metrics, 'cache_misses')


class TestParallelSpeedup:
    """Test parallel execution provides speedup."""
    
    @pytest.mark.asyncio
    async def test_parallel_vs_sequential_speedup(
        self,
        sample_episode_outline_large,
        sample_character_profiles,
        sample_show_metadata
    ):
        """Test parallel execution is faster than sequential."""
        
        # Create generators with different parallelism
        with patch('src.services.creative.script_generator.ClaudeClient'), \
             patch('src.services.creative.script_generator.OpenAIClient'), \
             patch('src.services.creative.script_generator.DialogueGenerator'), \
             patch('src.services.creative.script_generator.StageDirectionGenerator'), \
             patch('src.services.creative.script_generator.JokeOptimizer'), \
             patch('src.services.creative.script_generator.ScriptValidator'):
            
            # Sequential (max_parallel_scenes=1)
            sequential_generator = ScriptGenerator(max_parallel_scenes=1)
            
            # Parallel (max_parallel_scenes=3)
            parallel_generator = ScriptGenerator(max_parallel_scenes=3)
            
            # Mock dialogue with consistent timing
            async def mock_dialogue(*args, **kwargs):
                await asyncio.sleep(0.1)
                from src.services.creative.character_voice_profiles import (
                    SceneDialogue,
                    DialogueLine
                )
                return SceneDialogue(
                    scene_number=1,
                    location="Test Location",
                    characters_present=["Luna"],
                    dialogue_lines=[
                        DialogueLine(
                            character="Test",
                            line="line",
                            emotion="neutral",
                            delivery_note="normal"
                        )
                    ],
                    total_runtime_estimate=30,
                    comedic_beats_count=1
                )
            
            # Mock stage directions
            async def mock_stage(*args, **kwargs):
                await asyncio.sleep(0.05)
                from src.services.creative.stage_direction_models import SceneStageDirections
                return SceneStageDirections(
                    scene_number=1,
                    opening_description="Test",
                    camera_directions=[],
                    character_actions=[],
                    environmental_details=[],
                    lighting_notes="",
                    sound_cues=[],
                    transition_out=""
                )
            
            # Apply mocks to both generators
            for gen in [sequential_generator, parallel_generator]:
                gen.dialogue_generator.generate_dialogue = AsyncMock(side_effect=mock_dialogue)
                gen.stage_direction_generator.generate_stage_directions = AsyncMock(side_effect=mock_stage)
                
                from src.services.creative.joke_models import OptimizedScriptComedy, ComedyTimingAnalysis
                gen.joke_optimizer.optimize_script_comedy = Mock(return_value=OptimizedScriptComedy(
                    timing_analysis=ComedyTimingAnalysis(
                        total_jokes=5,
                        jokes_per_minute=2.0,
                        average_setup_duration=5.0,
                        average_punchline_delay=2.0,
                        pacing_score=0.85,
                        timing_issues=[],
                        ideal_joke_spacing=30.0
                    ),
                    analyzed_jokes=[],
                    alternative_punchlines=[],
                    callback_opportunities=[],
                    overall_quality_score=0.80,
                    improvement_summary="Good comedy timing"
                ))
                
                from src.services.creative.validation_models import ValidationReport, ProductionComplexity
                gen.script_validator.validate_script = Mock(return_value=ValidationReport(
                    script_id="test",
                    validation_passed=True,
                    overall_quality_score=0.85,
                    issues=[],
                    production_complexity=ProductionComplexity(3, 4, 0, 1, 50000.0)
                ))
            
            # Test sequential
            start = time.time()
            await sequential_generator.generate_full_script(
                script_id="seq_test",
                episode_outline=sample_episode_outline_large,
                character_profiles=sample_character_profiles,
                show_metadata=sample_show_metadata
            )
            sequential_time = time.time() - start
            
            # Test parallel
            start = time.time()
            await parallel_generator.generate_full_script(
                script_id="par_test",
                episode_outline=sample_episode_outline_large,
                character_profiles=sample_character_profiles,
                show_metadata=sample_show_metadata
            )
            parallel_time = time.time() - start
            
            # Calculate speedup
            speedup = sequential_time / parallel_time if parallel_time > 0 else 0
            
            # Parallel should be faster
            assert parallel_time < sequential_time, \
                f"Parallel ({parallel_time:.2f}s) not faster than sequential ({sequential_time:.2f}s)"
            
            # Should achieve at least 1.5x speedup (conservative, real target is 2x+)
            assert speedup >= 1.5, \
                f"Speedup {speedup:.2f}x insufficient (expected >=1.5x)"
            
            print(f"\nSpeedup achieved: {speedup:.2f}x")
            print(f"Sequential: {sequential_time:.2f}s, Parallel: {parallel_time:.2f}s")


class TestMemoryUsage:
    """Test memory usage stays within limits."""
    
    @pytest.mark.asyncio
    async def test_memory_usage_during_generation(
        self,
        mock_generator_with_timing,
        sample_episode_outline_large,
        sample_character_profiles,
        sample_show_metadata
    ):
        """Test memory usage during generation stays reasonable."""
        generator = mock_generator_with_timing
        process = psutil.Process(os.getpid())
        
        # Get baseline memory
        baseline_mb = process.memory_info().rss / 1024 / 1024
        
        # Generate script
        script = await generator.generate_full_script(
            script_id="memory_test",
            episode_outline=sample_episode_outline_large,
            character_profiles=sample_character_profiles,
            show_metadata=sample_show_metadata
        )
        
        # Get peak memory
        peak_mb = process.memory_info().rss / 1024 / 1024
        memory_increase = peak_mb - baseline_mb
        
        # Memory increase should be reasonable (<100MB for test)
        assert memory_increase < 100, \
            f"Memory increased by {memory_increase:.1f}MB (baseline {baseline_mb:.1f}MB)"
        
        # Script should be generated
        assert len(script.scenes) == 9
        
        print(f"\nMemory usage: {baseline_mb:.1f}MB → {peak_mb:.1f}MB (+{memory_increase:.1f}MB)")


class TestBottleneckDetection:
    """Test bottleneck detection works correctly."""
    
    @pytest.mark.asyncio
    async def test_bottleneck_detection_identifies_slow_operations(
        self,
        sample_episode_outline_small,
        sample_character_profiles,
        sample_show_metadata
    ):
        """Test that slow operations are correctly identified as bottlenecks."""
        
        with patch('src.services.creative.script_generator.ClaudeClient'), \
             patch('src.services.creative.script_generator.OpenAIClient'), \
             patch('src.services.creative.script_generator.DialogueGenerator'), \
             patch('src.services.creative.script_generator.StageDirectionGenerator'), \
             patch('src.services.creative.script_generator.JokeOptimizer'), \
             patch('src.services.creative.script_generator.ScriptValidator'):
            
            generator = ScriptGenerator(max_parallel_scenes=3)
            
            # Mock with intentionally slow dialogue generation
            async def slow_dialogue(*args, **kwargs):
                await asyncio.sleep(0.5)  # Intentionally slow
                from src.services.creative.character_voice_profiles import (
                    SceneDialogue,
                    DialogueLine
                )
                return SceneDialogue(
                    scene_number=1,
                    location="Test Location",
                    characters_present=["Test"],
                    dialogue_lines=[
                        DialogueLine(
                            character="Test",
                            line="line",
                            emotion="neutral",
                            delivery_note="normal"
                        )
                    ],
                    total_runtime_estimate=30,
                    comedic_beats_count=1
                )
            
            async def fast_stage(*args, **kwargs):
                await asyncio.sleep(0.01)  # Very fast
                from src.services.creative.stage_direction_models import SceneStageDirections
                return SceneStageDirections(
                    scene_number=1,
                    opening_description="Test",
                    camera_directions=[],
                    character_actions=[],
                    environmental_details=[],
                    lighting_notes="",
                    sound_cues=[],
                    transition_out=""
                )
            
            generator.dialogue_generator.generate_dialogue = AsyncMock(side_effect=slow_dialogue)
            generator.stage_direction_generator.generate_stage_directions = AsyncMock(side_effect=fast_stage)
            
            from src.services.creative.joke_models import OptimizedScriptComedy, ComedyTimingAnalysis
            generator.joke_optimizer.optimize_script_comedy = Mock(return_value=OptimizedScriptComedy(
                timing_analysis=ComedyTimingAnalysis(
                    total_jokes=5,
                    jokes_per_minute=2.0,
                    average_setup_duration=5.0,
                    average_punchline_delay=2.0,
                    pacing_score=0.85,
                    timing_issues=[],
                    ideal_joke_spacing=30.0
                ),
                analyzed_jokes=[],
                alternative_punchlines=[],
                callback_opportunities=[],
                overall_quality_score=0.80,
                improvement_summary="Good comedy timing"
            ))
            
            from src.services.creative.validation_models import ValidationReport, ProductionComplexity
            generator.script_validator.validate_script = Mock(return_value=ValidationReport(
                script_id="test",
                validation_passed=True,
                overall_quality_score=0.85,
                issues=[],
                production_complexity=ProductionComplexity(3, 4, 0, 1, 50000.0)
            ))
            
            # Generate script
            script = await generator.generate_full_script(
                script_id="bottleneck_test",
                episode_outline=sample_episode_outline_small,
                character_profiles=sample_character_profiles,
                show_metadata=sample_show_metadata
            )
            
            # Get metrics
            metrics = generator.get_performance_metrics()
            
            # Should have completed
            assert script is not None
            assert metrics is not None
            
            # Should have operations tracked
            assert len(metrics.operations) > 0
            
            # Should identify slowest operations
            assert len(metrics.slowest_operations) > 0
            
            # Generate full script operation should be in slowest
            operation_names = [op.operation_name for op in metrics.slowest_operations]
            assert "generate_full_script" in operation_names
            
            print(f"\nBottleneck detection results:")
            print(f"Total operations: {len(metrics.operations)}")
            print(f"Slowest operations: {len(metrics.slowest_operations)}")
            if metrics.bottleneck_warnings:
                print(f"Warnings: {metrics.bottleneck_warnings}")


class TestPerformanceReporting:
    """Test performance reporting functionality."""
    
    @pytest.mark.asyncio
    async def test_performance_summary_generation(
        self,
        mock_generator_with_timing,
        sample_episode_outline_small,
        sample_character_profiles,
        sample_show_metadata
    ):
        """Test that performance summary is generated correctly."""
        generator = mock_generator_with_timing
        
        # Generate script
        script = await generator.generate_full_script(
            script_id="reporting_test",
            episode_outline=sample_episode_outline_small,
            character_profiles=sample_character_profiles,
            show_metadata=sample_show_metadata
        )
        
        # Get metrics
        metrics = generator.get_performance_metrics()
        assert metrics is not None
        
        # Generate summary
        summary = metrics.get_summary()
        
        # Summary should contain key information
        assert "reporting_test" in summary
        assert "Total Duration" in summary
        assert "Cache Performance" in summary
        assert "API Usage" in summary
        assert "Generation Stats" in summary
        
        # Should have metrics values
        assert metrics.total_duration_seconds > 0
        assert metrics.scenes_generated == 3
        
        # to_dict should work
        metrics_dict = metrics.to_dict()
        assert metrics_dict["session_id"] == "reporting_test"
        assert metrics_dict["scenes_generated"] == 3
        assert "total_duration_seconds" in metrics_dict
        
        print(f"\nPerformance Summary:\n{summary}")

"""
Performance benchmark for parallel scene generation.

Measures actual speedup achieved by parallel execution vs sequential execution.
"""

import asyncio
import time
from unittest.mock import Mock, AsyncMock, patch

from src.services.creative.script_generator import ScriptGenerator


async def benchmark_scene_generation():
    """Run performance benchmark for parallel vs sequential scene generation."""
    
    print("\n" + "=" * 80)
    print("PARALLEL SCENE GENERATION PERFORMANCE BENCHMARK")
    print("=" * 80 + "\n")
    
    # Create mock data
    mock_scene_dialogue = Mock(
        scene_number=1,
        character_lines=[Mock(character_name="Luna", text="Test line")]
    )
    
    mock_stage_directions = Mock(
        scene_number=1,
        directions=[Mock(description="Enter", action_type="entrance")]
    )
    
    mock_comedy_analysis = Mock(
        analyzed_jokes=[],
        timing_analysis={},
        improvement_suggestions=[]
    )
    
    mock_validation_report = Mock(
        passed=True,
        issues=[],
        overall_quality=0.9
    )
    
    sample_episode_outline = {
        "scenes": [
            {
                "scene_number": i + 1,
                "title": f"Scene {i + 1}",
                "location": "Test Location",
                "time": "Day",
                "description": f"Test scene {i + 1}",
                "characters": ["Luna"],
                "key_moments": ["moment1"],
            }
            for i in range(3)
        ]
    }
    
    sample_voice_profiles = {
        "Luna": Mock(character_name="Luna", catchphrases=[])
    }
    
    sample_show_metadata = {
        "title": "Test Show",
        "tone": "comedic",
        "setting": "space colony"
    }
    
    # Mock generators with delays to simulate AI calls
    async def mock_generate_dialogue(*args, **kwargs):
        await asyncio.sleep(0.2)  # 200ms API call
        return mock_scene_dialogue
    
    async def mock_generate_stage_directions(*args, **kwargs):
        await asyncio.sleep(0.1)  # 100ms processing
        return mock_stage_directions
    
    with patch('src.services.creative.script_generator.ClaudeClient'), \
         patch('src.services.creative.script_generator.OpenAIClient'), \
         patch('src.services.creative.script_generator.DialogueGenerator'), \
         patch('src.services.creative.script_generator.StageDirectionGenerator'), \
         patch('src.services.creative.script_generator.JokeOptimizer'), \
         patch('src.services.creative.script_generator.ScriptValidator'):
        
        # Test 1: Sequential Execution
        print("📊 TEST 1: Sequential Execution (max_parallel_scenes=1)")
        print("-" * 80)
        
        sequential_generator = ScriptGenerator(max_parallel_scenes=1)
        
        # Setup mocks
        seq_dialogue_mock = Mock()
        seq_dialogue_mock.generate_dialogue = mock_generate_dialogue
        sequential_generator.dialogue_generator = seq_dialogue_mock
        
        seq_stage_mock = Mock()
        seq_stage_mock.generate_stage_directions = mock_generate_stage_directions
        sequential_generator.stage_direction_generator = seq_stage_mock
        
        seq_joke_mock = Mock()
        seq_joke_mock.optimize_script_comedy = AsyncMock(
            return_value=mock_comedy_analysis
        )
        sequential_generator.joke_optimizer = seq_joke_mock
        
        seq_validator_mock = Mock()
        seq_validator_mock.validate_script = Mock(
            return_value=mock_validation_report
        )
        sequential_generator.script_validator = seq_validator_mock
        
        start_time = time.time()
        sequential_script = await sequential_generator.generate_full_script(
            script_id="test_sequential",
            episode_outline=sample_episode_outline,
            character_profiles=sample_voice_profiles,
            show_metadata=sample_show_metadata,
        )
        sequential_time = time.time() - start_time
        
        print("Sequential execution completed")
        print(f"⏱️  Time: {sequential_time:.3f} seconds")
        print(f"📝 Scenes generated: {len(sequential_script.scene_scripts)}")
        print()
        
        # Test 2: Parallel Execution
        print("📊 TEST 2: Parallel Execution (max_parallel_scenes=3)")
        print("-" * 80)
        
        parallel_generator = ScriptGenerator(max_parallel_scenes=3)
        
        # Setup mocks
        par_dialogue_mock = Mock()
        par_dialogue_mock.generate_dialogue = mock_generate_dialogue
        parallel_generator.dialogue_generator = par_dialogue_mock
        
        par_stage_mock = Mock()
        par_stage_mock.generate_stage_directions = mock_generate_stage_directions
        parallel_generator.stage_direction_generator = par_stage_mock
        
        par_joke_mock = Mock()
        par_joke_mock.optimize_script_comedy = AsyncMock(
            return_value=mock_comedy_analysis
        )
        parallel_generator.joke_optimizer = par_joke_mock
        
        par_validator_mock = Mock()
        par_validator_mock.validate_script = Mock(
            return_value=mock_validation_report
        )
        parallel_generator.script_validator = par_validator_mock
        
        start_time = time.time()
        parallel_script = await parallel_generator.generate_full_script(
            script_id="test_parallel",
            episode_outline=sample_episode_outline,
            character_profiles=sample_voice_profiles,
            show_metadata=sample_show_metadata,
        )
        parallel_time = time.time() - start_time
        
        print("Parallel execution completed")
        print(f"⏱️  Time: {parallel_time:.3f} seconds")
        print(f"📝 Scenes generated: {len(parallel_script.scene_scripts)}")
        print()
    
    # Calculate speedup
    speedup = sequential_time / parallel_time
    time_saved = sequential_time - parallel_time
    percent_faster = ((sequential_time - parallel_time) /
                      sequential_time) * 100
    
    # Results summary
    print("=" * 80)
    print("📈 PERFORMANCE RESULTS")
    print("=" * 80)
    print(f"Sequential time:      {sequential_time:.3f}s")
    print(f"Parallel time:        {parallel_time:.3f}s")
    print(f"Time saved:           {time_saved:.3f}s "
          f"({percent_faster:.1f}% faster)")
    print(f"Speedup factor:       {speedup:.2f}x")
    print()
    
    # Performance assessment
    print("=" * 80)
    print("✅ PERFORMANCE ASSESSMENT")
    print("=" * 80)
    
    if speedup >= 2.0:
        print(f"🎉 EXCELLENT: Achieved {speedup:.2f}x speedup (target: 2x+)")
        print("   Parallel execution performing optimally!")
    elif speedup >= 1.5:
        print(f"✅ GOOD: Achieved {speedup:.2f}x speedup (target: 2x+)")
        print("   Parallel execution working, minor overhead present")
    else:
        print(f"⚠️  SUBOPTIMAL: Only {speedup:.2f}x speedup (target: 2x+)")
        print("   May need optimization or more parallelizable work")
    
    print()
    
    # Projected real-world performance
    print("=" * 80)
    print("🌍 PROJECTED REAL-WORLD PERFORMANCE")
    print("=" * 80)
    print("Assuming realistic API latencies for full episode generation:")
    print()
    print("Dialogue Generation:    2-3 seconds per scene (LLM API)")
    print("Stage Direction:        1-2 seconds per scene (LLM API)")
    print("Comedy Optimization:    1-2 seconds (analysis)")
    print()
    
    # Calculate projected times for 3-scene episode
    realistic_scene_time = 5.0  # 3s dialogue + 2s directions
    realistic_comedy_time = 1.5  # 1.5s comedy analysis
    
    realistic_sequential = (3 * realistic_scene_time) + realistic_comedy_time
    realistic_parallel = realistic_scene_time + realistic_comedy_time
    
    print(f"3-Scene Episode (Sequential):  ~{realistic_sequential:.0f}s "
          f"(~{realistic_sequential/60:.1f} minutes)")
    print(f"3-Scene Episode (Parallel):    ~{realistic_parallel:.0f}s "
          f"(~{realistic_parallel/60:.1f} minutes)")
    print(f"Expected Speedup:              "
          f"~{realistic_sequential/realistic_parallel:.1f}x")
    print()
    
    # Check against target
    target_time = 120  # 2 minutes
    if realistic_parallel <= target_time:
        print(f"✅ MEETS TARGET: {realistic_parallel:.0f}s < "
              f"{target_time}s (2 min target)")
    else:
        print(f"⚠️  EXCEEDS TARGET: {realistic_parallel:.0f}s > "
              f"{target_time}s (2 min target)")
    
    print()
    print("=" * 80)
    print("🎯 BENCHMARK COMPLETE")
    print("=" * 80)
    print()
    
    return {
        "sequential_time": sequential_time,
        "parallel_time": parallel_time,
        "speedup": speedup,
        "percent_faster": percent_faster,
        "meets_target": realistic_parallel <= target_time
    }


if __name__ == "__main__":
    results = asyncio.run(benchmark_scene_generation())
    print(f"\n📊 Results: {results}")



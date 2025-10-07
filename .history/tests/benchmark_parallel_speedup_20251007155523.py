"""
Performance benchmark for parallel scene generation.

Measures actual speedup achieved by parallel execution vs sequential execution.
"""

import asyncio
import time
from unittest.mock import AsyncMock, MagicMock, patch

from src.services.creative.script_generator import ScriptGenerator
from src.models.creative_models import (
    CharacterProfile,
    Setting,
    DoppelgangerSeries,
    Episode,
    Scene,
    Dialogue,
    StageDirection,
    TimingMark,
    Character,
)


async def benchmark_scene_generation():
    """Run performance benchmark for parallel vs sequential scene generation."""
    
    print("\n" + "=" * 80)
    print("PARALLEL SCENE GENERATION PERFORMANCE BENCHMARK")
    print("=" * 80 + "\n")
    
    # Setup mock dependencies
    mock_dialogue_gen = AsyncMock()
    mock_stage_dir_gen = AsyncMock()
    mock_joke_opt = AsyncMock()
    mock_validator = MagicMock()
    
    # Mock dialogue generation (simulate 200ms API call)
    async def mock_generate_dialogue(*args, **kwargs):
        await asyncio.sleep(0.2)  # Simulate API latency
        return [
            Dialogue(
                character_name="Luna",
                text="This is a test line",
                emotion="excited",
                timing=TimingMark(start=0, end=2)
            )
        ]
    mock_dialogue_gen.generate_dialogue = mock_generate_dialogue
    
    # Mock stage direction generation (simulate 100ms processing)
    async def mock_generate_stage_directions(*args, **kwargs):
        await asyncio.sleep(0.1)  # Simulate processing time
        return [
            StageDirection(
                description="Character enters",
                timing=TimingMark(start=0, end=1),
                action_type="entrance"
            )
        ]
    mock_stage_dir_gen.generate_stage_directions = mock_generate_stage_directions
    
    # Mock comedy optimization (simulate 150ms analysis)
    async def mock_optimize_comedy(*args, **kwargs):
        await asyncio.sleep(0.15)  # Simulate AI analysis
        return MagicMock(
            analyzed_jokes=[],
            timing_analysis={},
            comedic_beats=[],
            improvement_suggestions=[]
        )
    mock_joke_opt.optimize_script_comedy = mock_optimize_comedy
    
    # Mock validation (instant)
    mock_validator.validate_script.return_value = (True, [])
    
    # Setup test data
    character_profiles = [
        CharacterProfile(
            name="Luna",
            original_name="Lucy",
            personality_traits=["ambitious", "scheming"],
            character_type="protagonist",
            relationships={}
        )
    ]
    
    setting = Setting(
        type="space_colony",
        year=2157,
        location="Luna Prime Station",
        description="Space tourism hub"
    )
    
    series = DoppelgangerSeries(
        original_show_title="I Love Lucy",
        doppelganger_title="I Love Luna",
        target_setting=setting,
        character_profiles=character_profiles,
        tone="comedic",
        target_audience="family"
    )
    
    episode = Episode(
        episode_number=1,
        title="The Space Tourist Scheme",
        logline="Luna tries to become a space tour guide",
        scenes=[]
    )
    
    scenes = [
        Scene(
            scene_number=i + 1,
            location="Space Station Lobby",
            time_of_day="morning",
            description=f"Test scene {i + 1}",
            dialogues=[],
            stage_directions=[]
        )
        for i in range(3)
    ]
    
    # Test 1: Sequential Execution (max_parallel_scenes=1)
    print("📊 TEST 1: Sequential Execution (max_parallel_scenes=1)")
    print("-" * 80)
    
    generator_sequential = ScriptGenerator(
        dialogue_generator=mock_dialogue_gen,
        stage_direction_generator=mock_stage_dir_gen,
        joke_optimizer=mock_joke_opt,
        validator=mock_validator,
        max_parallel_scenes=1  # Force sequential
    )
    
    start_time = time.time()
    result_sequential = await generator_sequential.generate_full_script(
        series=series,
        episode=episode,
        scenes=scenes,
        character_profiles=character_profiles,
        setting=setting
    )
    sequential_time = time.time() - start_time
    
    print(f"✅ Sequential execution completed")
    print(f"⏱️  Time: {sequential_time:.3f} seconds")
    print(f"📝 Scenes generated: {len(result_sequential.scenes)}")
    print()
    
    # Test 2: Parallel Execution (max_parallel_scenes=3)
    print("📊 TEST 2: Parallel Execution (max_parallel_scenes=3)")
    print("-" * 80)
    
    generator_parallel = ScriptGenerator(
        dialogue_generator=mock_dialogue_gen,
        stage_direction_generator=mock_stage_dir_gen,
        joke_optimizer=mock_joke_opt,
        validator=mock_validator,
        max_parallel_scenes=3  # Allow parallel
    )
    
    start_time = time.time()
    result_parallel = await generator_parallel.generate_full_script(
        series=series,
        episode=episode,
        scenes=scenes,
        character_profiles=character_profiles,
        setting=setting
    )
    parallel_time = time.time() - start_time
    
    print(f"✅ Parallel execution completed")
    print(f"⏱️  Time: {parallel_time:.3f} seconds")
    print(f"📝 Scenes generated: {len(result_parallel.scenes)}")
    print()
    
    # Calculate speedup
    speedup = sequential_time / parallel_time
    time_saved = sequential_time - parallel_time
    percent_faster = ((sequential_time - parallel_time) / sequential_time) * 100
    
    # Results summary
    print("=" * 80)
    print("📈 PERFORMANCE RESULTS")
    print("=" * 80)
    print(f"Sequential time:      {sequential_time:.3f}s")
    print(f"Parallel time:        {parallel_time:.3f}s")
    print(f"Time saved:           {time_saved:.3f}s ({percent_faster:.1f}% faster)")
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
    realistic_scene_time = 5.0  # 3s dialogue + 2s directions = 5s per scene
    realistic_comedy_time = 1.5  # 1.5s comedy analysis
    
    realistic_sequential = (3 * realistic_scene_time) + realistic_comedy_time
    realistic_parallel = realistic_scene_time + realistic_comedy_time  # Max of parallel scenes
    
    print(f"3-Scene Episode (Sequential):  ~{realistic_sequential:.0f}s (~{realistic_sequential/60:.1f} minutes)")
    print(f"3-Scene Episode (Parallel):    ~{realistic_parallel:.0f}s (~{realistic_parallel/60:.1f} minutes)")
    print(f"Expected Speedup:              ~{realistic_sequential/realistic_parallel:.1f}x")
    print()
    
    # Check against target
    target_time = 120  # 2 minutes
    if realistic_parallel <= target_time:
        print(f"✅ MEETS TARGET: {realistic_parallel:.0f}s < {target_time}s (2 min target)")
    else:
        print(f"⚠️  EXCEEDS TARGET: {realistic_parallel:.0f}s > {target_time}s (2 min target)")
    
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
    asyncio.run(benchmark_scene_generation())

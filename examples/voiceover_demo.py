#!/usr/bin/env python3
"""
Voiceover Demo - Example usage of DOPPELGANGER STUDIO voiceover system.

Demonstrates:
- TTS engine usage
- Voice profiles
- Audio generation
- Audio processing
- Video synchronization

Copyright (c) 2025. All Rights Reserved. Patent Pending.
"""

import asyncio
import os
from pathlib import Path

from src.services.voiceover import ElevenLabsClient
from src.services.voiceover.google_tts_client import GoogleTTSClient
from src.services.voiceover.pyttsx_client import Pyttsx3Client
from src.models.voice_profile import VoiceProfile
from src.services.voiceover.voice_manager import VoiceManager
from src.services.voiceover.audio_generator import AudioGenerator, DialogueLine
from src.services.voiceover.audio_processor import AudioProcessor
from src.services.voiceover.audio_cache import AudioCache


def example_1_simple_tts():
    """
    Example 1: Simple TTS generation.
    """
    print("\n=== Example 1: Simple TTS ===")
    print("Generates 'Hello World' with different engines")
    
    # Check for API keys
    elevenlabs_key = os.getenv('ELEVENLABS_API_KEY')
    
    if elevenlabs_key:
        print("✅ ElevenLabs API key found")
    else:
        print("❌ ElevenLabs API key not set")
        print("   Set with: export ELEVENLABS_API_KEY='your_key'")


async def example_2_voice_profiles():
    """
    Example 2: Voice profile management.
    """
    print("\n=== Example 2: Voice Profiles ===")
    
    manager = VoiceManager()
    
    # Create default profiles
    defaults = manager.create_default_profiles()
    
    print(f"Created {len(defaults)} default profiles:")
    for name, profile in defaults.items():
        print(f"  - {name}: {profile.voice_id} ({profile.engine})")
    
    # Custom profile
    custom = VoiceProfile(
        character_name="Custom Character",
        voice_id="bella",
        engine="elevenlabs",
        settings={"stability": 0.8, "similarity_boost": 0.9},
        description="Custom voice for testing"
    )
    
    manager.add_profile(custom)
    print(f"\n✅ Added custom profile: {custom.character_name}")


async def example_3_audio_generation():
    """
    Example 3: Batch audio generation.
    """
    print("\n=== Example 3: Audio Generation ===")
    
    # Check API key
    api_key = os.getenv('ELEVENLABS_API_KEY')
    if not api_key:
        print("❌ Skipping - ElevenLabs API key required")
        return
    
    # Setup
    async with ElevenLabsClient(api_key) as engine:
        manager = VoiceManager()
        profiles = manager.create_default_profiles()
        
        generator = AudioGenerator(
            tts_engine=engine,
            voice_profiles=profiles,
            output_dir=Path("output/voiceover")
        )
        
        # Sample dialogue
        dialogue = [
            DialogueLine(
                character="Lucy Ricardo",
                text="Ricky! You've got some 'splainin' to do!",
                scene_id="ep1_scene1",
                line_number=1
            ),
            DialogueLine(
                character="Ricky Ricardo",
                text="Now Lucy, what did you do this time?",
                scene_id="ep1_scene1",
                line_number=2
            ),
        ]
        
        # Generate
        print(f"Generating audio for {len(dialogue)} lines...")
        
        def progress(current, total):
            print(f"  Progress: {current}/{total}")
        
        audio_files = await generator.generate_dialogue(
            dialogue,
            progress_callback=progress
        )
        
        # Results
        total_cost = sum(f.cost for f in audio_files)
        print(f"\n✅ Generated {len(audio_files)} files")
        print(f"   Total cost: ${total_cost:.4f}")
        
        for audio in audio_files:
            print(f"   - {audio.audio_path.name} ({audio.duration:.1f}s)")


def example_4_audio_processing():
    """
    Example 4: Audio processing.
    """
    print("\n=== Example 4: Audio Processing ===")
    print("Normalizes, trims, and adds fades to audio")
    
    try:
        processor = AudioProcessor()
        print("✅ AudioProcessor ready")
        print("   Features: normalize, trim_silence, add_fades")
    except ImportError:
        print("❌ pydub not installed")
        print("   Install with: pip install pydub")


def example_5_caching():
    """
    Example 5: Audio caching.
    """
    print("\n=== Example 5: Audio Caching ===")
    
    cache = AudioCache(cache_dir=Path(".cache/audio"))
    
    # Generate cache key
    key = cache.generate_key(
        text="Hello world!",
        voice_id="rachel",
        settings={"stability": 0.75}
    )
    
    print(f"Cache key: {key[:16]}...")
    
    # Check cache
    cached = cache.get(key)
    if cached:
        print("✅ Cache hit!")
    else:
        print("❌ Cache miss")
    
    stats = cache.get_stats()
    print(f"\nCache stats: {stats['total_entries']} entries")


def main():
    """
    Run all examples.
    """
    print("\n" + "="*50)
    print("DOPPELGANGER STUDIO - Voiceover Demo")
    print("="*50)
    
    # Run examples
    example_1_simple_tts()
    asyncio.run(example_2_voice_profiles())
    asyncio.run(example_3_audio_generation())
    example_4_audio_processing()
    example_5_caching()
    
    print("\n" + "="*50)
    print("✅ Demo complete!")
    print("="*50)
    print("\nNext steps:")
    print("1. Set up API keys (ELEVENLABS_API_KEY)")
    print("2. Create voice profiles for characters")
    print("3. Generate dialogue audio")
    print("4. Sync with animated video (Phase 5)")
    print("\nSee docs/voiceover_guide.md for details")


if __name__ == "__main__":
    main()

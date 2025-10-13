# Audio System Guide
## Complete Audio Production Pipeline

**Phase 7 - DOPPELGANGER STUDIO**

---

## Overview

The Phase 7 audio system provides complete audio production capabilities including music selection, sound effects placement, multi-track mixing, and professional mastering.

## System Components

### 1. Music Library & Selection

**Purpose:** Manage and select background music

**Features:**
- Import music files (MP3, WAV, FLAC)
- Metadata management (genre, mood, energy, BPM)
- Intelligent mood-based selection
- Duration adjustment (trim/loop)
- Automatic fades

**Example:**
```python
from src.services.audio.music import MusicLibrary, MusicSelector, SceneContext

# Initialize library
library = MusicLibrary("music_library")

# Import tracks
await library.import_track(
    "happy_theme.mp3",
    title="Happy Theme",
    genre=["comedy"],
    mood=["happy", "upbeat"],
    energy_level=8
)

# Select music for scene
selector = MusicSelector(library)
context = SceneContext(
    mood="happy",
    energy=8,
    duration=30.0
)

music_audio = await selector.select_and_prepare(context)
```

### 2. Sound Effects Library & Placement

**Purpose:** Manage and automatically place sound effects

**Categories:**
- **actions:** doors, footsteps, pour, etc.
- **impacts:** crash, bang, thud, slam
- **ambience:** crowd, traffic, nature
- **ui:** whoosh, ding, pop
- **comedy:** boing, kazoo, slide_whistle
- **transitions:** swoosh, whoosh, zap

**Example:**
```python
from src.services.audio.sfx import SFXLibrary, SFXPlacer

# Initialize library
library = SFXLibrary("sfx_library")

# Import effects
await library.import_effect(
    "door_slam.wav",
    category="actions",
    tags=["door", "slam", "loud"]
)

# Automatic placement
placer = SFXPlacer(library)

script_lines = [
    {'character': 'LUCY', 'line': 'Hello!', 'action': 'opens door'},
    {'character': 'RICKY', 'line': 'Hi Lucy!', 'action': ''}
]

placements = await placer.analyze_script(script_lines)
sfx_audio = await placer.render_effects(placements, duration_ms)
```

### 3. Multi-Track Mixing

**Purpose:** Mix dialogue, music, SFX, and ambience

**Features:**
- 4-track mixing capability
- Intelligent ducking (lower music during dialogue)
- Professional level defaults
- Custom level overrides
- Automatic normalization

**Example:**
```python
from src.services.audio.mixing import AudioMixer

mixer = AudioMixer()

mixed = await mixer.mix_tracks(
    dialogue=dialogue_audio,
    music=music_audio,
    sfx=[effect1, effect2],
    apply_ducking=True
)
```

**Default Levels:**
- Dialogue: -3dB (loudest)
- SFX: -9dB (noticeable)
- Music: -18dB (background)
- Ambience: -24dB (subtle)

### 4. Audio Mastering

**Purpose:** Professional final audio processing

**Features:**
- Peak normalization (-1dB)
- Dynamic range compression (3:1 ratio)
- Limiting (-0.3dB ceiling)
- Platform-specific optimization
- Broadcast standards compliance

**Example:**
```python
from src.services.audio.mixing import AudioMaster

master = AudioMaster()

# Basic mastering
mastered = await master.master_audio(mixed_audio)

# Platform-specific
mastered = await master.master_for_platform(
    mixed_audio,
    platform='youtube'  # or 'spotify', 'broadcast'
)

# Check levels
levels = master.get_levels(mastered)
print(f"Peak: {levels['peak_db']:.1f}dB")
print(f"RMS: {levels['rms_db']:.1f}dB")
```

### 5. Complete Pipeline

**Purpose:** End-to-end audio production workflow

**Example:**
```python
from src.services.audio import AudioPipeline, AudioConfig, SceneContext

# Initialize pipeline
pipeline = AudioPipeline(
    music_library_path="music",
    sfx_library_path="sfx"
)

# Configure
config = AudioConfig(
    music_enabled=True,
    sfx_enabled=True,
    apply_ducking=True,
    apply_mastering=True,
    target_platform='youtube'
)

# Process scene
result = await pipeline.process_scene(
    dialogue_audio=dialogue,
    scene_context=SceneContext(
        mood="happy",
        energy=8,
        duration=30.0
    ),
    script_lines=lines,
    config=config
)

# Export
result.audio.export("final_audio.mp3", format="mp3")

print(f"Duration: {result.duration_seconds:.1f}s")
print(f"SFX Count: {result.sfx_count}")
print(f"Peak: {result.peak_db:.1f}dB")
```

## Complete Example: Episode Production

```python
from src.services.audio import AudioPipeline, AudioConfig, SceneContext
from pydub import AudioSegment

# Initialize pipeline
pipeline = AudioPipeline(
    music_library_path="assets/music",
    sfx_library_path="assets/sfx"
)

# Prepare scenes
scenes = [
    {
        'dialogue_audio': AudioSegment.from_file("scene1_dialogue.mp3"),
        'scene_context': SceneContext(mood="happy", energy=8, duration=30.0),
        'script_lines': [
            {'character': 'LUCY', 'line': 'Hello!', 'action': 'opens door'},
            {'character': 'RICKY', 'line': 'Hi!', 'action': ''}
        ]
    },
    {
        'dialogue_audio': AudioSegment.from_file("scene2_dialogue.mp3"),
        'scene_context': SceneContext(mood="dramatic", energy=6, duration=45.0),
        'script_lines': []
    }
]

# Process episode
config = AudioConfig(target_platform='youtube')
result = await pipeline.process_episode(scenes, config)

# Export final episode
result.audio.export("episode_complete.mp3", format="mp3", bitrate="192k")

print(f"✅ Episode complete: {result.duration_seconds:.1f}s")
print(f"   SFX placed: {result.sfx_count}")
print(f"   Audio quality: {result.peak_db:.1f}dB peak")
```

## Library Management

### Building Music Library

```python
import asyncio
from pathlib import Path
from src.services.audio.music import MusicLibrary

async def build_music_library():
    library = MusicLibrary("music_library")
    
    music_files = Path("raw_music").glob("*.mp3")
    
    for music_file in music_files:
        await library.import_track(
            music_file,
            genre=["comedy"],  # Adjust per file
            mood=["happy"],
            energy_level=7
        )
        print(f"Imported: {music_file.name}")
    
    stats = library.get_stats()
    print(f"\nLibrary: {stats['total_tracks']} tracks")
    print(f"Duration: {stats['total_duration_hours']:.1f} hours")

asyncio.run(build_music_library())
```

### Building SFX Library

```python
import asyncio
from pathlib import Path
from src.services.audio.sfx import SFXLibrary

async def build_sfx_library():
    library = SFXLibrary("sfx_library")
    
    # Import by category
    categories = {
        'actions': ['door_open.wav', 'door_close.wav', 'footsteps.wav'],
        'impacts': ['crash.wav', 'bang.wav', 'thud.wav'],
        'comedy': ['boing.wav', 'slide_whistle.wav']
    }
    
    for category, files in categories.items():
        for file in files:
            file_path = Path("raw_sfx") / category / file
            await library.import_effect(
                file_path,
                category=category,
                tags=[file.replace('.wav', '').replace('_', ' ')]
            )
            print(f"Imported: {file}")
    
    stats = library.get_stats()
    print(f"\nLibrary: {stats['total_effects']} effects")
    print(f"Categories: {stats['categories']}")

asyncio.run(build_sfx_library())
```

## Configuration

### AudioConfig Options

```python
from src.services.audio import AudioConfig

# Full configuration
config = AudioConfig(
    music_enabled=True,      # Enable background music
    sfx_enabled=True,        # Enable sound effects
    apply_ducking=True,      # Duck music during dialogue
    apply_mastering=True,    # Apply professional mastering
    target_platform='youtube', # Platform optimization
    fade_in_ms=500,         # Music fade in duration
    fade_out_ms=1000        # Music fade out duration
)

# Minimal configuration
config_minimal = AudioConfig(
    music_enabled=False,
    sfx_enabled=False,
    apply_mastering=False
)
```

## Quality Standards

### Broadcast Standards

- **Peak Level:** -1.0 dB
- **RMS Level:** -16 LUFS
- **Dynamic Range:** 8-12 dB
- **Sample Rate:** 48 kHz
- **Bit Depth:** 16-bit export
- **Channels:** Stereo

### Platform Requirements

**YouTube:**
- Peak: -1dB
- RMS: -14 LUFS
- Format: AAC, 48kHz, 192kbps

**Spotify:**
- Peak: -1dB
- RMS: -14 LUFS
- Format: OGG Vorbis, q9

**Broadcast:**
- Peak: -1dB
- RMS: -16 LUFS
- Format: WAV, 48kHz, 24-bit

## Performance

### Processing Times (Typical)

- Music selection: <1s
- SFX placement: 1-2s per minute
- Mixing: 5-10s per minute
- Mastering: 3-5s per minute
- **Total:** ~10-20s per minute of audio

### Memory Usage

- ~500MB per 10 minutes of audio
- Library indexes: <10MB
- Efficient streaming for long episodes

## Troubleshooting

### Common Issues

**Issue:** Music too loud during dialogue
**Solution:** Increase ducking amount or lower music level

**Issue:** SFX not placed correctly
**Solution:** Check script action descriptions, add more keywords

**Issue:** Clipping in final audio
**Solution:** Lower mixing levels or increase mastering headroom

**Issue:** Poor audio quality
**Solution:** Check source audio quality, verify sample rates match

## Best Practices

1. **Library Organization:**
   - Separate libraries for music and SFX
   - Use descriptive tags
   - Maintain consistent metadata

2. **Music Selection:**
   - Match mood to scene tone
   - Consider energy level transitions
   - Use variety to avoid repetition

3. **SFX Placement:**
   - Use clear action descriptions
   - Don't overdo effects
   - Consider timing and pacing

4. **Mixing:**
   - Keep dialogue prominent
   - Use ducking for clarity
   - Balance all elements

5. **Mastering:**
   - Always check final levels
   - Verify platform requirements
   - Listen on multiple devices

## API Reference

See inline documentation in source files:
- `src/services/audio/music/library.py`
- `src/services/audio/music/selector.py`
- `src/services/audio/sfx/library.py`
- `src/services/audio/sfx/placer.py`
- `src/services/audio/mixing/mixer.py`
- `src/services/audio/mixing/mastering.py`
- `src/services/audio/integration/pipeline.py`

---

**Copyright (c) 2025. All Rights Reserved. Patent Pending.**
**DOPPELGANGER STUDIO - Professional TV Parody Creation Platform**

# DOPPELGANGER STUDIO - Voiceover Guide

## Phase 6: Voiceover Integration

Complete guide to adding voice acting to animated episodes.

---

## Installation

### Required Dependencies

```bash
# TTS engines
pip install elevenlabs  # ElevenLabs API
pip install google-cloud-texttospeech  # Google TTS
pip install pyttsx3  # Offline TTS

# Audio processing
pip install pydub

# FFmpeg (system dependency)
# macOS: brew install ffmpeg
# Ubuntu: sudo apt install ffmpeg
```

### API Keys

**ElevenLabs (Recommended):**
```bash
export ELEVENLABS_API_KEY="your_key_here"
```

Get API key from: https://elevenlabs.io/

**Google Cloud TTS:**
```bash
export GOOGLE_APPLICATION_CREDENTIALS="/path/to/credentials.json"
```

---

## Quick Start

### Simple TTS

```python
import asyncio
import os
from pathlib import Path
from src.services.voiceover import ElevenLabsClient

async def generate_speech():
    api_key = os.getenv('ELEVENLABS_API_KEY')
    
    async with ElevenLabsClient(api_key) as client:
        result = await client.generate_speech(
            text="Hello, I'm Lucy!",
            voice_id="rachel",
            output_path=Path("lucy_hello.mp3")
        )
        
        if result.success:
            print(f"Generated: {result.audio_path}")
            print(f"Cost: ${result.cost:.4f}")

asyncio.run(generate_speech())
```

---

## Voice Profiles

### Creating Profiles

```python
from src.models.voice_profile import VoiceProfile
from src.services.voiceover.voice_manager import VoiceManager

manager = VoiceManager()

# Custom profile
lucy_profile = VoiceProfile(
    character_name="Lucy Ricardo",
    voice_id="rachel",
    engine="elevenlabs",
    settings={
        "stability": 0.7,
        "similarity_boost": 0.8,
    },
    description="Enthusiastic 1950s housewife"
)

manager.add_profile(lucy_profile)
```

### Default Profiles

```python
# Create defaults
defaults = manager.create_default_profiles()

# Available:
# - Lucy Ricardo (rachel)
# - Ricky Ricardo (adam)
```

---

## Audio Generation

### Batch Generation

```python
from src.services.voiceover.audio_generator import (
    AudioGenerator,
    DialogueLine
)

# Setup
generator = AudioGenerator(
    tts_engine=client,
    voice_profiles=profiles,
    output_dir=Path("output/audio")
)

# Dialogue
lines = [
    DialogueLine(
        character="Lucy Ricardo",
        text="Ricky! You've got some 'splainin' to do!",
        scene_id="ep1_scene1",
        line_number=1
    ),
    # ... more lines
]

# Generate
audio_files = await generator.generate_dialogue(lines)

print(f"Generated {len(audio_files)} files")
print(f"Total cost: ${sum(f.cost for f in audio_files):.2f}")
```

---

## Audio Processing

### Processing Pipeline

```python
from src.services.voiceover.audio_processor import AudioProcessor

processor = AudioProcessor()

# Process file
processed = processor.process_file(
    input_path=Path("raw_audio.mp3"),
    output_path=Path("processed_audio.mp3"),
    normalize=True,  # Normalize volume
    trim=True,       # Trim silence
    fades=True       # Add fades
)
```

---

## Video Synchronization

### Add Audio to Video

```python
from src.services.voiceover.audio_sync import AudioSync

sync = AudioSync()

# Sync audio with video
output = await sync.sync_audio_to_video(
    video_path=Path("episode1_silent.mp4"),
    audio_path=Path("episode1_audio.mp3"),
    output_path=Path("episode1_final.mp4"),
    offset=0.0  # Audio offset in seconds
)

print(f"Synced video: {output}")
```

### Generate Subtitles

```python
# Create SRT subtitles
dialogue_timing = [
    (0.0, 2.5, "Lucy: Ricky!"),
    (3.0, 5.5, "Ricky: Yes, dear?"),
]

sync.generate_subtitles(
    dialogue=dialogue_timing,
    output_path=Path("episode1.srt")
)
```

---

## Caching

### Using Cache

```python
from src.services.voiceover.audio_cache import AudioCache

cache = AudioCache()

# Generate cache key
key = cache.generate_key(
    text="Hello world!",
    voice_id="rachel",
    settings={"stability": 0.75}
)

# Check cache
cached = cache.get(key)
if cached:
    print(f"Using cached: {cached}")
else:
    # Generate new audio
    result = await client.generate_speech(...)
    cache.set(key, result.audio_path)
```

**Benefits:**
- 70%+ cache hit rate
- Reduced API costs
- Faster generation

---

## Cost Management

### Tracking Costs

```python
# All TTS results include cost
result = await client.generate_speech(...)
print(f"Cost: ${result.cost:.4f}")

# Batch tracking
total_cost = sum(f.cost for f in audio_files)
print(f"Total: ${total_cost:.2f}")
```

### Cost Optimization

1. **Use caching** - Avoid regenerating identical audio
2. **Trim scripts** - Remove unnecessary dialogue
3. **Batch generation** - Generate all at once
4. **Use Google TTS** - Cheaper for testing ($4/1M chars)
5. **Use pyttsx3** - Free for development

---

## Best Practices

### Voice Selection

1. **Test voices:**
   ```python
   voices = await client.list_voices()
   for name, data in voices.items():
       print(f"{name}: {data['description']}")
   ```

2. **Match characters:**
   - Lucy: Female, enthusiastic → "rachel"
   - Ricky: Male, warm → "adam"

3. **Consistency:**
   - Same voice throughout episode
   - Save voice profiles
   - Document choices

### Audio Quality

1. **Processing:**
   - Always normalize volume
   - Trim silence
   - Add fades

2. **Settings:**
   - Stability: 0.7-0.8 (consistent)
   - Similarity: 0.75-0.85 (realistic)

3. **Testing:**
   - Listen to samples
   - Check timing
   - Verify sync

---

## Troubleshooting

**Issue:** "ElevenLabs API error 401"  
**Solution:** Check API key is correct

**Issue:** "Rate limit exceeded"  
**Solution:** Wait or upgrade plan

**Issue:** "pydub not found"  
**Solution:** `pip install pydub`

**Issue:** "FFmpeg not found"  
**Solution:** Install FFmpeg system-wide

---

## Next Steps

1. **Phase 7:** Music and sound effects
2. **Phase 8:** YouTube upload automation

---

**Copyright (c) 2025. All Rights Reserved. Patent Pending.**

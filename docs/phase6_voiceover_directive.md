# DOPPELGANGER STUDIO - PHASE 6 DIRECTIVE
## Voiceover Integration - Text-to-Speech & Audio Sync

**PHASE:** 6 of 12  
**STATUS:** 🚀 ACTIVE  
**PRIORITY:** HIGH - Voice acting and audio  
**DURATION:** 8-10 commits, 2-3 hours estimated

---

## 🎯 MISSION CRITICAL OBJECTIVES [REF:PHASE6-001]

Building upon Phase 5 (animation system), you will now implement the **voice acting engine** using Text-to-Speech (TTS) technology to bring characters to life:

**Phase 6 Deliverables:**
1. ✅ TTS engine integration (ElevenLabs + Google Cloud)
2. ✅ Voice character profile system
3. ✅ Dialogue audio generation
4. ✅ Audio timing and synchronization
5. ✅ Audio file management
6. ✅ Voice effect processing
7. ✅ Audio-video sync pipeline
8. ✅ Audio caching system
9. ✅ Comprehensive test suite
10. ✅ Example voiceover demos

---

## 📋 ARCHITECTURE OVERVIEW [REF:PHASE6-002]

### Technology Stack
```yaml
TTS Engines:
  Primary: ElevenLabs API (realistic voices)
  Fallback: Google Cloud TTS (reliable backup)
  Offline: pyttsx3 (local development)

Audio Processing:
  Core: pydub (Python audio library)
  Effects: ffmpeg-python
  Format: WAV (processing) → MP3 (storage)
  
Synchronization:
  Timing: Subtitle format (SRT/VTT)
  Sync: Audio duration matching
  Alignment: Character dialogue timing

Storage:
  Cache: Redis (audio metadata)
  Files: Local filesystem (MP3)
  Metadata: PostgreSQL (voice profiles)
```

### Component Architecture
```
src/services/voiceover/
├── tts_engine.py              # Abstract TTS interface
├── elevenlabs_client.py       # ElevenLabs integration
├── google_tts_client.py       # Google Cloud TTS
├── pyttsx_client.py           # Local TTS fallback
├── voice_profile.py           # Character voice mapping
├── audio_generator.py         # Dialogue audio creation
├── audio_processor.py         # Effects and processing
├── audio_sync.py              # Video synchronization
└── audio_cache.py             # Caching system
```

---

## 🎬 COMMIT ROADMAP [REF:PHASE6-003]

### Commit #52: ✅ Phase 6 Directive (CURRENT)
**Files:** `docs/phase6_voiceover_directive.md`
**Purpose:** Architecture and requirements documentation

### Commit #53: TTS Engine Base & ElevenLabs Client
**Files:**
- `src/services/voiceover/tts_engine.py`
- `src/services/voiceover/elevenlabs_client.py`
- `src/services/voiceover/__init__.py`

**Requirements:**
- Abstract TTS interface
- ElevenLabs API integration
- Voice selection
- Speech generation
- Error handling and retries

**Example:**
```python
from src.services.voiceover import ElevenLabsClient

client = ElevenLabsClient(api_key=os.getenv('ELEVENLABS_API_KEY'))
audio = await client.generate_speech(
    text="Hello, I'm Lucy!",
    voice_id="rachel",  # Voice profile
    output_path="lucy_hello.mp3"
)
```

### Commit #54: Google TTS & Offline Fallbacks
**Files:**
- `src/services/voiceover/google_tts_client.py`
- `src/services/voiceover/pyttsx_client.py`

**Requirements:**
- Google Cloud TTS integration
- pyttsx3 local TTS
- Consistent interface
- Automatic fallback logic

### Commit #55: Voice Profile System
**Files:**
- `src/models/voice_profile.py`
- `src/services/voiceover/voice_profile.py`

**Requirements:**
- Character-to-voice mapping
- Voice characteristics (pitch, speed, accent)
- Profile storage (PostgreSQL)
- Profile management API

**Data Model:**
```python
@dataclass
class VoiceProfile:
    character_name: str
    voice_id: str  # ElevenLabs voice ID
    engine: str  # 'elevenlabs', 'google', 'pyttsx'
    settings: Dict[str, Any]  # pitch, speed, etc.
    sample_audio: Optional[Path]
```

### Commit #56: Audio Generator
**Files:**
- `src/services/voiceover/audio_generator.py`

**Requirements:**
- Batch dialogue generation
- Multi-character support
- Timing calculation
- Progress tracking
- Error handling

**Core Methods:**
```python
class AudioGenerator:
    async def generate_dialogue(
        self,
        dialogue_lines: List[DialogueLine],
        voice_profiles: Dict[str, VoiceProfile]
    ) -> List[AudioFile]:
        """Generate audio for all dialogue."""
        
    async def generate_episode_audio(
        self,
        episode_script: EpisodeScript
    ) -> EpisodeAudio:
        """Generate complete episode voiceover."""
```

### Commit #57: Audio Processing & Effects
**Files:**
- `src/services/voiceover/audio_processor.py`

**Requirements:**
- Volume normalization
- Silence trimming
- Background noise reduction
- Audio effects (echo, reverb)
- Format conversion
- Fade in/out

**Effects:**
```python
class AudioProcessor:
    def normalize_volume(audio: AudioSegment) -> AudioSegment
    def trim_silence(audio: AudioSegment) -> AudioSegment
    def add_effect(audio: AudioSegment, effect: str) -> AudioSegment
    def crossfade(audio1: AudioSegment, audio2: AudioSegment) -> AudioSegment
```

### Commit #58: Audio-Video Synchronization
**Files:**
- `src/services/voiceover/audio_sync.py`

**Requirements:**
- Dialogue timing alignment
- Character lip-sync data (optional)
- Subtitle generation (SRT/VTT)
- Audio track overlay
- FFmpeg integration

**Sync Pipeline:**
```python
class AudioSync:
    async def sync_audio_to_video(
        self,
        video_path: Path,
        audio_files: List[AudioFile],
        dialogue_timing: List[TimingData]
    ) -> Path:
        """Add voiceover audio to video."""
```

### Commit #59: Audio Caching System
**Files:**
- `src/services/voiceover/audio_cache.py`

**Requirements:**
- Cache generated audio
- Redis metadata storage
- File system management
- Cache invalidation
- Cost tracking

**Cache Strategy:**
- Key: `hash(text + voice_id + settings)`
- TTL: 30 days
- Storage: Local MP3 files
- Metadata: Redis

### Commit #60: Comprehensive Tests
**Files:**
- `tests/unit/test_tts_engines.py`
- `tests/unit/test_voice_profiles.py`
- `tests/unit/test_audio_generator.py`
- `tests/unit/test_audio_sync.py`
- `tests/integration/test_voiceover_pipeline.py`

**Test Coverage:**
- Unit tests for each TTS engine
- Voice profile CRUD operations
- Audio generation workflow
- Sync timing accuracy
- Cache functionality
- Mock API responses

**Target:** ≥85% coverage

### Commit #61: Examples & Documentation
**Files:**
- `examples/voiceover_demo.py`
- `docs/voiceover_guide.md`
- `docs/phase6_completion_report.md`

**Examples:**
- Simple TTS generation
- Character voice creation
- Episode audio generation
- Audio-video sync

---

## 🎤 TTS ENGINE SPECIFICATIONS [REF:PHASE6-004]

### ElevenLabs API

**Features:**
- Ultra-realistic voices
- Voice cloning support
- Multiple languages
- Emotion control

**Configuration:**
```python
ELEVENLABS_CONFIG = {
    'api_key': os.getenv('ELEVENLABS_API_KEY'),
    'model_id': 'eleven_monolingual_v1',
    'voices': {
        'lucy': 'rachel',  # Female, enthusiastic
        'ricky': 'adam',   # Male, warm
    },
    'settings': {
        'stability': 0.75,
        'similarity_boost': 0.75,
    }
}
```

**Rate Limits:**
- Free tier: 10,000 characters/month
- Paid tier: Custom limits
- Implement retry with backoff

### Google Cloud TTS

**Features:**
- Reliable and fast
- WaveNet voices
- Multiple languages
- SSML support

**Configuration:**
```python
GOOGLE_TTS_CONFIG = {
    'credentials': os.getenv('GOOGLE_APPLICATION_CREDENTIALS'),
    'language_code': 'en-US',
    'voices': {
        'lucy': 'en-US-Neural2-F',
        'ricky': 'en-US-Neural2-D',
    },
    'audio_config': {
        'audio_encoding': 'MP3',
        'speaking_rate': 1.0,
        'pitch': 0.0,
    }
}
```

### pyttsx3 (Offline)

**Features:**
- No API required
- Instant generation
- Cross-platform
- Free

**Limitations:**
- Lower quality
- Robotic sound
- Limited voices

**Use Case:** Development and testing

---

## 🎭 VOICE PROFILE SYSTEM [REF:PHASE6-005]

### Character Voice Mapping

```python
VOICE_PROFILES = {
    'Lucy Ricardo': VoiceProfile(
        character_name='Lucy Ricardo',
        voice_id='rachel',  # ElevenLabs
        engine='elevenlabs',
        settings={
            'stability': 0.7,
            'similarity_boost': 0.8,
            'pitch': 1.1,  # Slightly higher
            'speed': 1.05,  # Slightly faster
        },
        description='Enthusiastic, comedic, 1950s housewife',
    ),
    
    'Ricky Ricardo': VoiceProfile(
        character_name='Ricky Ricardo',
        voice_id='adam',
        engine='elevenlabs',
        settings={
            'stability': 0.75,
            'similarity_boost': 0.75,
            'pitch': 0.9,  # Slightly lower
            'accent': 'cuban',  # If supported
        },
        description='Warm, authoritative, Cuban accent',
    ),
}
```

### Voice Testing

```python
# Test voice with sample dialogue
await test_voice_profile(
    profile=VOICE_PROFILES['Lucy Ricardo'],
    test_text="Ricky! You've got some 'splainin' to do!"
)
```

---

## 🎵 AUDIO PROCESSING [REF:PHASE6-006]

### Audio Pipeline

```
Text Script
    ↓
TTS Generation
    ↓
Raw Audio (WAV)
    ↓
Processing:
  - Normalize volume
  - Trim silence
  - Add effects
  - Format conversion
    ↓
Final Audio (MP3)
    ↓
Cache Storage
```

### Processing Requirements

**Volume Normalization:**
- Target: -20 dB LUFS
- Peak limit: -3 dB
- Prevent clipping

**Silence Trimming:**
- Leading: Remove >100ms
- Trailing: Remove >200ms
- Between words: Preserve natural pauses

**Effects:**
- Fade in: 50ms
- Fade out: 100ms
- Room tone: Optional background
- Compression: Light compression for clarity

### Audio Format Standards

```yaml
Processing:
  format: WAV
  sample_rate: 44100 Hz
  bit_depth: 16-bit
  channels: Mono

Storage:
  format: MP3
  bitrate: 192 kbps
  sample_rate: 44100 Hz
  channels: Mono
```

---

## 🔄 SYNCHRONIZATION [REF:PHASE6-007]

### Timing Calculation

```python
class DialogueTiming:
    """Calculate precise dialogue timing."""
    
    def calculate_duration(text: str, wpm: int = 150) -> float:
        """Calculate speech duration."""
        words = len(text.split())
        duration = (words / wpm) * 60
        return duration
    
    def align_to_animation(
        audio_duration: float,
        animation_duration: float
    ) -> TimingData:
        """Align audio with animation timing."""
```

### Subtitle Generation

```python
# Generate SRT subtitles
def generate_subtitles(
    dialogue: List[DialogueLine],
    timings: List[TimingData]
) -> str:
    """Create SRT subtitle file."""
    
# Format:
# 1
# 00:00:01,000 --> 00:00:03,500
# Lucy: Ricky, I'm home!
```

### FFmpeg Audio Overlay

```python
# Combine video + audio
ffmpeg_command = [
    'ffmpeg',
    '-i', video_path,
    '-i', audio_path,
    '-c:v', 'copy',  # Copy video
    '-c:a', 'aac',   # Encode audio
    '-map', '0:v:0',
    '-map', '1:a:0',
    output_path
]
```

---

## 💾 CACHING STRATEGY [REF:PHASE6-008]

### Cache Key Generation

```python
def generate_cache_key(
    text: str,
    voice_id: str,
    settings: Dict
) -> str:
    """Generate unique cache key."""
    content = f"{text}:{voice_id}:{json.dumps(settings, sort_keys=True)}"
    return hashlib.sha256(content.encode()).hexdigest()
```

### Cache Management

```python
class AudioCache:
    async def get(self, key: str) -> Optional[Path]
    async def set(self, key: str, audio_path: Path, ttl: int = 2592000)
    async def invalidate(self, pattern: str)
    async def get_stats(self) -> CacheStats
```

### Cost Tracking

```python
# Track TTS API costs
@dataclass
class TTSUsage:
    characters: int
    cost: float
    engine: str
    timestamp: datetime

# Store in PostgreSQL for analytics
```

---

## 🔧 CODE QUALITY STANDARDS [REF:PHASE6-009]

### Same Standards as Previous Phases
- ✅ Google-style docstrings
- ✅ Type hints (100%)
- ✅ Logging at appropriate levels
- ✅ Error handling with try-except
- ✅ Async/await for I/O
- ✅ Data classes for models
- ✅ ≥85% test coverage

---

## 🎯 SUCCESS CRITERIA [REF:PHASE6-010]

### Functional Requirements
- ✅ TTS generates clear audio
- ✅ Voice profiles match characters
- ✅ Audio syncs with video
- ✅ Caching reduces API calls
- ✅ Processing improves quality
- ✅ Multiple engines work
- ✅ Fallback system functional

### Quality Requirements
- ✅ Audio clarity excellent
- ✅ Natural voice pacing
- ✅ Consistent volume levels
- ✅ No audio artifacts
- ✅ Proper synchronization

### Performance Requirements
- ✅ Audio generation <5s per line
- ✅ Cache hit rate >70%
- ✅ Sync processing <30s per scene
- ✅ API costs reasonable

---

## 📊 PHASE 6 METRICS [REF:PHASE6-011]

```yaml
Code Metrics:
  Lines: 2000-2500
  Coverage: ≥85%
  Type Hints: 100%
  Commits: 8-10
  Components: 9
  
Time Estimate: ~3 hours
```

---

## 🚀 READY TO START!

**Current Status:**
- ✅ Directive complete
- ✅ Architecture defined
- ✅ Roadmap clear
- ⏳ Starting Commit #53

**Next Action:** Implement TTS engine base and ElevenLabs client

Let's add voice to DOPPELGANGER STUDIO! 🎤✨

---

**Copyright (c) 2025. All Rights Reserved.**

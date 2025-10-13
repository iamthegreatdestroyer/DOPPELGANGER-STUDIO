# DOPPELGANGER STUDIO - PHASE 7 MASTER DIRECTIVE
## Music & Sound Effects System Implementation

**TARGET:** Complete Audio Production Pipeline  
**PHASE:** 7 of 12  
**DURATION:** 2-3 hours  
**PRIORITY:** CRITICAL - Audio completion

---

## 🎯 MISSION CRITICAL OBJECTIVES [EXEC-P7-001]

Building upon the voiceover system from Phase 6, you will now implement the **complete audio production pipeline**:

**This Phase Deliverables:**
1. ✅ Music library management
2. ✅ Sound effects library
3. ✅ Audio mixing engine (multi-track)
4. ✅ Background music integration
5. ✅ SFX timing and placement
6. ✅ Audio mastering pipeline
7. ✅ Audio export optimization
8. ✅ Comprehensive test suite
9. ✅ Complete documentation
10. ✅ Integration with animation system

---

## 📁 SYSTEM ARCHITECTURE [ARCH-P7-001]

### Audio Pipeline Flow
```
Script
  ↓
Voiceover (Phase 6)
  ↓
Music Selection ← Music Library
  ↓
SFX Placement ← SFX Library
  ↓
Multi-Track Mixing
  ↓
Audio Mastering
  ↓
Final Video Integration
  ↓
Complete Episode
```

### Component Structure
```
src/services/audio/
├── music/
│   ├── __init__.py
│   ├── library.py          # Music library management
│   ├── selector.py         # Intelligent music selection
│   └── metadata.py         # Music metadata parsing
├── sfx/
│   ├── __init__.py
│   ├── library.py          # SFX library management
│   ├── placer.py           # Timing and placement
│   └── categories.py       # SFX categorization
├── mixing/
│   ├── __init__.py
│   ├── mixer.py            # Multi-track audio mixer
│   ├── normalizer.py       # Audio normalization
│   └── mastering.py        # Final mastering
├── integration/
│   ├── __init__.py
│   ├── pipeline.py         # Complete audio pipeline
│   └── exporter.py         # Final export
└── utils/
    ├── __init__.py
    ├── audio_analysis.py   # Audio feature extraction
    └── timing.py           # Precise timing utilities
```

---

## 🎵 MUSIC SYSTEM REQUIREMENTS [REF:MUSIC-001]

### Music Library Manager

**Purpose:** Manage background music tracks with metadata

**Key Features:**
- Import music files (MP3, WAV, FLAC)
- Extract metadata (duration, BPM, key, mood)
- Categorize by genre, mood, energy level
- Search and filter capabilities
- Playlist management

**Data Model:**
```python
@dataclass
class MusicTrack:
    id: str
    title: str
    file_path: Path
    duration: float
    bpm: Optional[int]
    key: Optional[str]
    genre: List[str]
    mood: List[str]  # happy, sad, tense, dramatic, comedic
    energy_level: int  # 1-10
    instrumentation: List[str]
    tags: List[str]
    created_at: datetime
```

**Music Selection Intelligence:**
```python
class MusicSelector:
    """Intelligently select music based on scene context."""
    
    async def select_for_scene(
        self,
        scene_data: Dict,
        duration: float,
        mood: str,
        energy: int
    ) -> MusicTrack:
        """
        Select appropriate music for scene.
        
        Considers:
        - Scene mood and tone
        - Duration requirements
        - Energy level
        - Genre appropriateness
        - Previous selections (variety)
        """
```

### Music Integration Features

1. **Automatic Trimming/Looping**
   - Trim to exact scene duration
   - Seamless looping for long scenes
   - Fade in/out at scene boundaries

2. **Mood Matching**
   - Analyze script tone
   - Match music mood to scene
   - Transition between moods

3. **Dynamic Volume**
   - Duck music during dialogue
   - Boost during action/transitions
   - Fade for emphasis

---

## 🔊 SOUND EFFECTS SYSTEM [REF:SFX-001]

### SFX Library Manager

**Purpose:** Manage sound effects with precise categorization

**Categories:**
- **Actions:** door_open, door_close, footsteps, etc.
- **Impacts:** crash, bang, thud, slam
- **Ambience:** crowd, traffic, nature, office
- **UI:** whoosh, ding, pop, swoosh
- **Comedy:** boing, kazoo, slide_whistle, rimshot
- **Transitions:** swoosh, whoosh, zap

**Data Model:**
```python
@dataclass
class SoundEffect:
    id: str
    name: str
    file_path: Path
    category: str
    subcategory: Optional[str]
    duration: float
    tags: List[str]
    volume_default: float  # 0.0-1.0
    created_at: datetime
```

### SFX Placement Engine

**Purpose:** Automatically place SFX at appropriate times

**Features:**
```python
class SFXPlacer:
    """Place sound effects at precise timestamps."""
    
    async def analyze_script(
        self,
        script: Script
    ) -> List[SFXPlacement]:
        """
        Analyze script and identify SFX opportunities.
        
        Detects:
        - Action verbs (slam, crash, walk, etc.)
        - Scene transitions
        - Character entrances/exits
        - Comedy beats
        - Emphasis moments
        """
    
    async def place_effects(
        self,
        placements: List[SFXPlacement],
        timeline: Timeline
    ) -> List[AudioSegment]:
        """
        Place SFX at precise timestamps with proper mixing.
        """
```

**Timing Precision:**
- Millisecond-accurate placement
- Sync with animation events
- Avoid dialogue overlap
- Natural spacing between effects

---

## 🎚️ AUDIO MIXING ENGINE [REF:MIXING-001]

### Multi-Track Mixer

**Purpose:** Mix multiple audio sources into final output

**Tracks:**
1. **Dialogue Track** - Voiceover (highest priority)
2. **Music Track** - Background music
3. **SFX Track** - Sound effects
4. **Ambience Track** - Background ambience (optional)

**Mixing Features:**
```python
class AudioMixer:
    """Professional multi-track audio mixer."""
    
    async def mix_tracks(
        self,
        dialogue: AudioSegment,
        music: AudioSegment,
        sfx: List[AudioSegment],
        ambience: Optional[AudioSegment] = None
    ) -> AudioSegment:
        """
        Mix all audio tracks with intelligent ducking.
        
        Process:
        1. Normalize all tracks
        2. Apply ducking (lower music during dialogue)
        3. Mix SFX at precise timestamps
        4. Balance levels
        5. Apply compression
        6. Master final output
        """
```

**Ducking Algorithm:**
- Detect dialogue presence
- Lower music by -12dB during speech
- Smooth transitions (50ms fade)
- Maintain music presence

**Level Balancing:**
- Dialogue: -3dB (loudest)
- Music: -18dB (background)
- SFX: -9dB (noticeable)
- Ambience: -24dB (subtle)

---

## 🎛️ AUDIO MASTERING [REF:MASTER-001]

### Mastering Pipeline

**Purpose:** Professional final audio processing

**Processing Chain:**
```python
class AudioMaster:
    """Professional audio mastering pipeline."""
    
    async def master_audio(
        self,
        mixed_audio: AudioSegment
    ) -> AudioSegment:
        """
        Apply professional mastering chain.
        
        Process:
        1. Normalize peaks (-1dB)
        2. Apply compression (ratio 3:1)
        3. EQ adjustment (enhance clarity)
        4. Limiting (-0.3dB ceiling)
        5. Final normalization
        6. Format conversion (if needed)
        """
```

**Quality Targets:**
- Peak level: -1.0dB
- RMS level: -16 LUFS (broadcast standard)
- Dynamic range: 8-12 dB
- Frequency response: 20Hz - 20kHz
- Sample rate: 48kHz
- Bit depth: 24-bit (export as 16-bit)

---

## 🔧 TECHNICAL SPECIFICATIONS [REF:TECH-P7-001]

### Audio Processing Libraries

```python
# Requirements
pydub>=0.25.1        # Core audio manipulation
librosa>=0.10.0      # Audio analysis
soundfile>=0.12.1    # High-quality audio I/O
numpy>=1.24.0        # Numerical operations
scipy>=1.10.0        # Signal processing
```

### Audio Formats

**Input Formats:**
- MP3 (music library)
- WAV (SFX, high-quality)
- FLAC (lossless)
- OGG (alternative)

**Output Format:**
- AAC (video integration)
- 48kHz sample rate
- 192 kbps bitrate
- Stereo

### Performance Requirements

- **Processing Speed:** Real-time or faster
- **Memory Usage:** <2GB for 10-minute episode
- **File Size:** ~5MB per minute (final audio)
- **Latency:** <100ms for real-time preview

---

## 🎯 IMPLEMENTATION CHECKLIST [REF:IMPL-P7-001]

### Commit #62: Phase 7 Directive ✅
- [x] Complete directive document
- [x] Architecture design
- [x] Technical specifications

### Commit #63: Music Library System
- [ ] MusicLibrary class
- [ ] Metadata extraction
- [ ] Search and filter
- [ ] Basic tests

### Commit #64: Music Selector
- [ ] MusicSelector class
- [ ] Mood matching algorithm
- [ ] Duration handling
- [ ] Integration tests

### Commit #65: SFX Library System
- [ ] SFXLibrary class
- [ ] Category management
- [ ] Search functionality
- [ ] Basic tests

### Commit #66: SFX Placement Engine
- [ ] SFXPlacer class
- [ ] Script analysis
- [ ] Timing calculator
- [ ] Integration tests

### Commit #67: Audio Mixer
- [ ] AudioMixer class
- [ ] Multi-track mixing
- [ ] Ducking algorithm
- [ ] Level balancing
- [ ] Tests

### Commit #68: Audio Mastering
- [ ] AudioMaster class
- [ ] Compression
- [ ] Normalization
- [ ] Limiting
- [ ] Tests

### Commit #69: Audio Pipeline Integration
- [ ] Complete pipeline class
- [ ] End-to-end workflow
- [ ] Video integration
- [ ] Tests

### Commit #70: Comprehensive Tests
- [ ] Unit tests (all components)
- [ ] Integration tests
- [ ] Performance tests
- [ ] Documentation

### Commit #71: Documentation & Examples
- [ ] Usage guide
- [ ] API documentation
- [ ] Example code
- [ ] Phase 7 completion report

---

## 📊 SUCCESS METRICS [REF:METRICS-P7-001]

### Code Quality
- Test Coverage: ≥85%
- Type Hints: 100%
- Documentation: Complete
- Code Lines: ~2,000

### Functional Requirements
- ✅ Music library with 100+ tracks
- ✅ SFX library with 500+ effects
- ✅ Multi-track mixing working
- ✅ Professional audio quality
- ✅ Complete integration

### Performance Targets
- Process 1 minute audio in <30 seconds
- Mix 4 tracks in <15 seconds
- Master audio in <10 seconds
- Total pipeline: <2 minutes per episode

---

## 🎊 PHASE 7 COMPLETION CRITERIA [REF:COMPLETE-P7-001]

**Phase 7 is complete when:**

✅ All 10 commits delivered successfully  
✅ Music system manages and selects tracks  
✅ SFX system places effects accurately  
✅ Audio mixer produces professional output  
✅ Mastering pipeline meets broadcast standards  
✅ Complete integration with voiceover system  
✅ Tests achieve ≥85% coverage  
✅ Documentation is comprehensive  
✅ Example episodes demonstrate quality  
✅ Ready for Phase 8 (Video Editing)  

---

## 🚀 NEXT PHASE PREVIEW [REF:NEXT-P7-001]

**Phase 8: Video Editing & Post-Production**
- Video composition
- Title cards and credits
- Transitions and effects
- Color grading
- Final export optimization
- YouTube formatting

---

**END OF PHASE 7 DIRECTIVE**

*Copyright (c) 2025. All Rights Reserved. Patent Pending.*
*DOPPELGANGER STUDIO - Professional TV Parody Creation Platform*
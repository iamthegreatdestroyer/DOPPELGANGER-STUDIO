# DOPPELGANGER STUDIO - PHASE 5 DIRECTIVE
## Animation System - Manim Integration

**PHASE:** 5 of 12  
**STATUS:** 🚀 ACTIVE  
**PRIORITY:** HIGH - Visual content generation  
**DURATION:** 8-10 commits, 2-3 hours estimated

---

## 🎯 MISSION CRITICAL OBJECTIVES [REF:PHASE5-001]

Building upon Phases 2, 3, and 4 (research, AI analysis, script generation), you will now implement the **visual animation engine** using Manim (Mathematical Animation Engine):

**Phase 5 Deliverables:**
1. ✅ Manim wrapper and configuration
2. ✅ Character sprite system
3. ✅ Scene renderer with camera controls
4. ✅ Animation timeline manager
5. ✅ Visual effects library
6. ✅ Text/subtitle system
7. ✅ Export pipeline (MP4, scenes)
8. ✅ Animation templates library
9. ✅ Comprehensive test suite
10. ✅ Example animations

---

## 📋 ARCHITECTURE OVERVIEW [REF:PHASE5-002]

### Technology Stack
```yaml
Animation Engine:
  Core: Manim Community Edition v0.18+
  Rendering: Cairo + FFmpeg
  Language: Python 3.11+
  Async: asyncio for pipeline coordination

Visual Assets:
  Characters: SVG sprites + PNG fallbacks
  Backgrounds: Generated or image-based
  Effects: Manim built-in + custom
  
Output:
  Format: MP4 (H.264)
  Resolution: 1920x1080 (1080p)
  Framerate: 30fps
  Quality: High (CRF 18-23)

Integration:
  Input: Episode scripts from Phase 4
  Processing: Scene-by-scene rendering
  Output: Video files for Phase 6 (voiceover sync)
```

### Component Architecture
```
src/services/animation/
├── manim_wrapper.py          # Core Manim interface
├── character_sprite.py       # Character visual system
├── scene_renderer.py         # Scene composition
├── timeline_manager.py       # Animation sequencing
├── effects/                  # Visual effects library
│   ├── transitions.py
│   ├── camera_moves.py
│   └── text_effects.py
├── templates/                # Reusable animation templates
│   ├── sitcom_template.py
│   ├── character_intro.py
│   └── scene_transitions.py
└── exporter.py               # Video export pipeline
```

---

## 🎬 COMMIT ROADMAP [REF:PHASE5-003]

### Commit #42: ✅ Phase 5 Directive (CURRENT)
**Files:** `docs/phase5_animation_directive.md`
**Purpose:** Architecture and requirements documentation

### Commit #43: Manim Wrapper & Configuration
**Files:** 
- `src/services/animation/manim_wrapper.py`
- `src/services/animation/__init__.py`
- `config/manim_config.yaml`

**Requirements:**
- Manim configuration management
- Scene creation wrapper
- Render quality presets
- Output path management
- FFmpeg integration check

### Commit #44: Character Sprite System
**Files:**
- `src/services/animation/character_sprite.py`
- `src/models/character_visual.py`

**Requirements:**
- SVG character loading
- Sprite positioning and scaling
- Character expressions (happy, sad, surprised, etc.)
- Animation states (idle, talking, moving)
- Layer management

### Commit #45: Scene Renderer
**Files:**
- `src/services/animation/scene_renderer.py`

**Requirements:**
- Scene composition from script data
- Background management
- Character placement
- Camera positioning and movement
- Scene duration calculation
- Transition effects

### Commit #46: Timeline Manager
**Files:**
- `src/services/animation/timeline_manager.py`

**Requirements:**
- Animation sequence coordination
- Timing synchronization
- Event scheduling
- Parallel animation support

### Commit #47: Visual Effects Library
**Files:**
- `src/services/animation/effects/transitions.py`
- `src/services/animation/effects/camera_moves.py`
- `src/services/animation/effects/text_effects.py`

**Effects:**
- Transitions (fade, wipe, dissolve)
- Camera moves (pan, zoom, track)
- Text effects (typewriter, bounce)

### Commit #48: Animation Templates
**Files:**
- `src/services/animation/templates/sitcom_template.py`
- `src/services/animation/templates/character_intro.py`
- `src/services/animation/templates/scene_transitions.py`

**Templates:**
- Sitcom 3-camera setup
- Character introduction sequence
- Scene transition overlays

### Commit #49: Video Exporter
**Files:**
- `src/services/animation/exporter.py`

**Requirements:**
- Multi-scene compilation
- Quality presets
- Progress tracking
- Metadata embedding

### Commit #50: Comprehensive Tests
**Files:**
- `tests/unit/test_manim_wrapper.py`
- `tests/unit/test_character_sprite.py`
- `tests/unit/test_scene_renderer.py`
- `tests/integration/test_animation_pipeline.py`

**Target:** ≥85% coverage

### Commit #51: Examples & Documentation
**Files:**
- `examples/animation_demo.py`
- `docs/animation_guide.md`
- `docs/phase5_completion_report.md`

---

## 🎨 MANIM INTEGRATION [REF:PHASE5-004]

### Installation
```bash
pip install manim==0.18.0
pip install pillow
pip install pydub
```

### Configuration
```yaml
# config/manim_config.yaml
manim:
  quality:
    preview: 480p15
    low: 854p30
    medium: 1080p30
    high: 1080p60
    
  output:
    directory: "output/animations"
    format: "mp4"
    codec: "libx264"
    crf: 18
    
  scene:
    background_color: "#FFFFFF"
    frame_rate: 30
    pixel_height: 1080
    pixel_width: 1920
```

---

## 🎭 CHARACTER SPRITES [REF:PHASE5-005]

### Sprite Requirements
- **Format:** SVG or PNG
- **Size:** 512x512px base
- **Layers:** Body, clothing, head, expression, accessories

### Expressions
- neutral, happy, sad, surprised
- angry, confused, excited, talking

### Animation States
- idle, walk, talk, gesture, react

### Positioning
```python
POSITIONS = {
    'center': (0, 0),
    'left': (-4, 0),
    'right': (4, 0),
    'upstage': (0, 2),
    'downstage': (0, -2)
}
```

---

## 🎬 SCENE RENDERING [REF:PHASE5-006]

### Pipeline Flow
```
Script Scene
    ↓
Character Assignment
    ↓
Background Selection
    ↓
Animation Generation
    ↓
Effect Application
    ↓
Rendering
    ↓
MP4 Output
```

### Scene Types

**Dialogue Scene:**
- 2-3 characters
- Static camera
- Talking animations
- Duration: 30-90s

**Action Scene:**
- Character movement
- Camera follows
- Dynamic effects
- Duration: 10-30s

**Transition Scene:**
- Location captions
- Time passage effects
- Duration: 2-5s

---

## 🔧 CODE QUALITY [REF:PHASE5-007]

### Requirements (Same as Previous Phases)
- ✅ Google-style docstrings
- ✅ Type hints (100%)
- ✅ Logging
- ✅ Error handling
- ✅ Async where appropriate
- ✅ ≥85% test coverage

---

## 🎯 SUCCESS CRITERIA [REF:PHASE5-008]

### Functional
- ✅ Manim renders scenes successfully
- ✅ Characters display correctly
- ✅ Animations play at 30fps
- ✅ Effects apply correctly
- ✅ MP4 exports work
- ✅ Multi-scene compilation works

### Quality
- ✅ Clean visual output
- ✅ Consistent frame rate
- ✅ Smooth transitions
- ✅ Readable text

### Performance
- ✅ Scene renders <30s (preview)
- ✅ Episode renders <10min (high quality)
- ✅ Memory usage <4GB per worker

---

## 📊 PHASE 5 METRICS [REF:PHASE5-009]

```yaml
Code Metrics:
  Lines: 2000-2500
  Coverage: ≥85%
  Type Hints: 100%
  Commits: 8-10
  Components: 10
  Examples: 3-5

Time Estimate: ~3 hours
```

---

## 🚀 READY TO START!

**Current Status:**
- ✅ Directive complete
- ✅ Architecture defined
- ✅ Roadmap clear
- ⏳ Starting Commit #43

**Next:** Implement Manim wrapper and configuration

Let's build the animation engine! 🎬✨

---

**Copyright (c) 2025. All Rights Reserved.**

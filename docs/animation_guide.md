# DOPPELGANGER STUDIO - Animation Guide

## Phase 5: Animation System

Comprehensive guide to creating animated episodes using the Manim-based animation system.

---

## Table of Contents

1. [Installation](#installation)
2. [Quick Start](#quick-start)
3. [Character Sprites](#character-sprites)
4. [Scene Rendering](#scene-rendering)
5. [Timeline Management](#timeline-management)
6. [Visual Effects](#visual-effects)
7. [Video Export](#video-export)
8. [Best Practices](#best-practices)

---

## Installation

### Required Dependencies

```bash
# Core animation engine
pip install manim==0.18.0

# Image processing
pip install pillow

# Audio support (Phase 6)
pip install pydub
```

### System Dependencies

**macOS:**
```bash
brew install ffmpeg cairo pango
```

**Ubuntu/Debian:**
```bash
sudo apt install ffmpeg libcairo2-dev libpango1.0-dev
```

**Windows:**
- Download FFmpeg from https://ffmpeg.org/download.html
- Add to PATH

### Verify Installation

```python
from src.services.animation import ManimWrapper

status = ManimWrapper.validate_installation()
print(status)
# {'manim': True, 'ffmpeg': True, 'cairo': True}
```

---

## Quick Start

### Simple Animation

```python
from src.services.animation import ManimWrapper, RenderQuality
from manim import *

# Create wrapper
wrapper = ManimWrapper(quality=RenderQuality.HIGH)

# Define scene
def my_scene(scene):
    text = Text("Hello DOPPELGANGER!")
    scene.play(Write(text))
    scene.wait(1)

# Create and render
SceneClass = wrapper.create_scene_class("MyScene", my_scene)
output = wrapper.render_scene(SceneClass, "output.mp4")
print(f"Rendered: {output}")
```

---

## Character Sprites

### Creating Character Assets

**File Format:** SVG (recommended) or PNG  
**Size:** 512x512px  
**Structure:**
```
assets/characters/
├── lucy/
│   ├── base.svg          # Main sprite
│   ├── happy.svg         # Expression overlay
│   ├── sad.svg
│   └── surprised.svg
└── ricky/
    ├── base.svg
    └── ...
```

### Loading Characters

```python
from pathlib import Path
from src.models.character_visual import CharacterVisual, Expression
from src.services.animation.character_sprite import CharacterSprite

# Create visual data
lucy_visual = CharacterVisual(
    name="Lucy",
    sprite_path=Path("assets/characters/lucy/base.svg"),
    expression_paths={
        Expression.HAPPY: Path("assets/characters/lucy/happy.svg"),
        Expression.SAD: Path("assets/characters/lucy/sad.svg"),
    },
    scale=1.2,
    default_position=(0, 0),
    layer=1
)

# Create sprite
lucy = CharacterSprite(lucy_visual)
```

### Character Expressions

```python
# Change expression
lucy.set_expression(Expression.HAPPY)

# Get animation
anim = lucy.set_expression(Expression.SURPRISED)
scene.play(anim)
```

### Character Movement

```python
# Move character
anim = lucy.move_to((3, 0), duration=1.0)
scene.play(anim)

# Enter from side
anim = lucy.enter_from('left', duration=1.5)
scene.play(anim)

# Exit
anim = lucy.exit_to('right', duration=1.0)
scene.play(anim)
```

---

## Scene Rendering

### Scene Data Structure

```python
from src.services.animation.scene_renderer import SceneData

scene_data = SceneData(
    scene_id="ep1_scene1",
    description="Lucy enters the apartment",
    duration=30.0,
    characters=["Lucy", "Ricky"],
    dialogue=[
        ("Lucy", "Honey, I'm home!"),
        ("Ricky", "Hi Lucy! How was your day?"),
        ("Lucy", "You won't believe what happened!")
    ],
    background="living_room.png"
)
```

### Rendering Scenes

```python
from src.services.animation.scene_renderer import SceneRenderer
from src.services.animation.character_sprite import CharacterSpriteManager

# Setup characters
manager = CharacterSpriteManager()
manager.add_character(lucy)
manager.add_character(ricky)

# Create renderer
renderer = SceneRenderer(manager)

# Create scene class
scene_class = renderer.create_scene(
    scene_data,
    background_path=Path("assets/backgrounds/living_room.png")
)

# Render with wrapper
wrapper = ManimWrapper(quality=RenderQuality.HIGH)
output = wrapper.render_scene(scene_class, "scene1.mp4")
```

---

## Timeline Management

### Creating Timelines

```python
from src.services.animation.timeline_manager import Timeline, EventType

timeline = Timeline()

# Add events
timeline.add_event(
    time=0.0,
    animation=lucy.fade_in(),
    duration=0.5,
    event_type=EventType.ANIMATION
)

timeline.add_event(
    time=1.0,
    animation=lucy.move_to((2, 0)),
    duration=1.5
)

timeline.add_event(
    time=2.0,
    animation=ricky.set_expression(Expression.SURPRISED),
    duration=0.3
)

# Get total duration
print(f"Timeline: {timeline.get_duration()}s")
```

---

## Visual Effects

### Transitions

```python
from src.services.animation.effects import fade_transition

# Fade between scenes
scene.play(fade_transition(duration=1.0))
```

### Camera Moves

```python
from src.services.animation.effects import pan_camera, zoom_camera

# Pan to character
scene.play(pan_camera(lucy.get_position(), duration=2.0))

# Zoom in
scene.play(zoom_camera(factor=1.5, duration=1.0))
```

### Text Effects

```python
from src.services.animation.effects import typewriter_text

# Typewriter subtitle
scene.play(typewriter_text("Meanwhile...", duration=2.0))
```

---

## Video Export

### Single Episode Export

```python
import asyncio
from src.services.animation.exporter import VideoExporter

async def export_episode():
    exporter = VideoExporter()
    
    scene_paths = [
        Path("output/scene1.mp4"),
        Path("output/scene2.mp4"),
        Path("output/scene3.mp4"),
    ]
    
    result = await exporter.export_episode(
        scene_paths=scene_paths,
        output_path=Path("output/episode1_complete.mp4"),
        quality="high",
        metadata={
            "title": "I Love Lucy - Episode 1 Parody",
            "artist": "DOPPELGANGER STUDIO",
            "year": "2025"
        }
    )
    
    if result.success:
        print(f"✅ Exported: {result.output_path}")
        print(f"   Size: {result.file_size / 1024 / 1024:.1f} MB")
    else:
        print(f"❌ Export failed: {result.errors}")

asyncio.run(export_episode())
```

---

## Best Practices

### Performance

1. **Use preview quality for testing:**
   ```python
   wrapper = ManimWrapper(quality=RenderQuality.PREVIEW)
   ```

2. **Batch render scenes:**
   ```python
   scenes = [(Scene1, "s1.mp4"), (Scene2, "s2.mp4")]
   wrapper.render_multiple_scenes(scenes)
   ```

3. **Optimize sprite assets:**
   - Use SVG for scalability
   - Keep file sizes small
   - Use layers for expressions

### Quality

1. **Final renders use HIGH quality:**
   ```python
   wrapper = ManimWrapper(quality=RenderQuality.HIGH)
   ```

2. **Test timing with real dialogue:**
   - Read scripts aloud
   - Adjust duration calculations
   - Add natural pauses

3. **Review before export:**
   - Check all scenes render
   - Verify transitions
   - Test final video playback

### Organization

1. **Structure assets:**
   ```
   assets/
   ├── characters/
   ├── backgrounds/
   └── effects/
   ```

2. **Name files consistently:**
   ```
   ep1_scene1.mp4
   ep1_scene2.mp4
   ep1_complete.mp4
   ```

3. **Document scene data:**
   - Keep scene configs in JSON
   - Version control scripts
   - Comment complex animations

---

## Troubleshooting

### Common Issues

**Issue:** "FFmpeg not found"  
**Solution:** Install FFmpeg and add to PATH

**Issue:** "Manim import error"  
**Solution:** `pip install manim==0.18.0`

**Issue:** "Sprite file not found"  
**Solution:** Check file paths are absolute

**Issue:** "Rendering timeout"  
**Solution:** Use lower quality or split scene

---

## Next Steps

1. **Phase 6:** Voiceover Integration
2. **Phase 7:** Audio Synchronization
3. **Phase 8:** YouTube Upload Automation

---

**Copyright (c) 2025. All Rights Reserved. Patent Pending.**

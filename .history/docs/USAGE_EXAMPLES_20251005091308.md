# Phase 3 Usage Examples

**DOPPELGANGER STUDIO™ - Practical Integration Guide**

---

## 📋 Table of Contents

1. [Complete Show Analysis](#complete-show-analysis)
2. [Episode Generation](#episode-generation)
3. [Progress Tracking](#progress-tracking)
4. [Error Handling](#error-handling)
5. [Batch Processing](#batch-processing)

---

## 🎬 Complete Show Analysis

### Basic Usage

```python
"""Example: Analyze a classic TV show completely."""

import asyncio
from src.services.creative.show_analyzer import ShowAnalyzer
from src.services.research.research_orchestrator import ResearchOrchestrator
from src.services.creative.character_analyzer import CharacterAnalyzer
from src.services.creative.narrative_analyzer import NarrativeAnalyzer
from src.services.creative.transformation_engine import TransformationEngine
from src.services.database.database_manager import DatabaseManager
from src.services.ai.claude_client import ClaudeClient


async def analyze_i_love_lucy():
    """Complete analysis of I Love Lucy."""

    # 1. Initialize database connection
    db_manager = DatabaseManager()
    await db_manager.connect()

    # 2. Initialize AI client
    claude_client = ClaudeClient()

    # 3. Initialize all Phase 2 & 3 components
    research = ResearchOrchestrator(db_manager)
    char_analyzer = CharacterAnalyzer(claude_client, None, db_manager)
    narrative_analyzer = NarrativeAnalyzer(claude_client, None, db_manager)
    transformer = TransformationEngine(claude_client, None, db_manager)

    # 4. Create unified show analyzer
    analyzer = ShowAnalyzer(
        research_orchestrator=research,
        character_analyzer=char_analyzer,
        narrative_analyzer=narrative_analyzer,
        transformation_engine=transformer,
        database_manager=db_manager
    )

    # 5. Analyze show
    print("Starting analysis of 'I Love Lucy'...")

    analysis = await analyzer.analyze_show(
        show_title="I Love Lucy",
        tmdb_id=1668,
        imdb_id="tt0043208"
    )

    # 6. Display results
    print(f"\n✅ Analysis Complete!")
    print(f"Completeness: {analysis.completeness_score * 100:.1f}%")
    print(f"Analysis Time: {analysis.analysis_time_seconds:.1f}s")

    print(f"\n📺 Modern Premise:")
    print(f"  {analysis.transformation_rules['modern_premise']}")

    print(f"\n👥 Characters Analyzed: {len(analysis.character_analyses)}")
    for char in analysis.character_analyses:
        print(f"  - {char['character_name']}")
        print(f"    Traits: {', '.join([t['trait'] for t in char['core_traits'][:3]])}")

    print(f"\n📖 Narrative Structure:")
    if analysis.narrative_analysis:
        print(f"  Type: {analysis.narrative_analysis['structure_type']}")
        print(f"  Devices: {len(analysis.narrative_analysis['recurring_devices'])}")
        for device in analysis.narrative_analysis['recurring_devices'][:2]:
            print(f"    • {device['pattern_name']}: {device['description']}")

    print(f"\n🔄 Transformation Highlights:")
    setting = analysis.transformation_rules['setting']
    print(f"  Setting: {setting['original']} → {setting['modern']}")
    print(f"  Character Updates: {len(analysis.transformation_rules['character_transformations'])}")
    print(f"  Tech Opportunities: {', '.join(analysis.transformation_rules['technology_opportunities'][:5])}")

    # 7. Cleanup
    await db_manager.disconnect()

    return analysis


# Run it
if __name__ == "__main__":
    asyncio.run(analyze_i_love_lucy())
```

**Expected Output:**

```
Starting analysis of 'I Love Lucy'...

✅ Analysis Complete!
Completeness: 95.2%
Analysis Time: 183.4s

📺 Modern Premise:
  A wannabe influencer schemes to go viral while married to a successful YouTuber

👥 Characters Analyzed: 4
  - Lucy Ricardo
    Traits: ambitious, scheming, endearing
  - Ricky Ricardo
    Traits: exasperated, talented, loving
  - Ethel Mertz
    Traits: loyal, sarcastic, practical
  - Fred Mertz
    Traits: grumpy, cheap, protective

📖 Narrative Structure:
  Type: episodic
  Devices: 5
    • Harebrained Scheme: Lucy concocts elaborate plans that backfire
    • Physical Comedy: Visual gags and slapstick humor

🔄 Transformation Highlights:
  Setting: 1950s NYC apartment → 2025 Brooklyn loft
  Character Updates: 4
  Tech Opportunities: Instagram, TikTok, Ring lights, Smart home, YouTube
```

---

## 🎭 Episode Generation

### Generate Single Episode

```python
"""Example: Generate episode outline."""

import asyncio
from src.services.creative.episode_generator import EpisodeGenerator
from src.services.ai.claude_client import ClaudeClient


async def generate_lucy_episode():
    """Generate episode for modernized I Love Lucy."""

    # 1. Initialize
    claude_client = ClaudeClient()
    generator = EpisodeGenerator(claude_client)

    # 2. Define transformation rules (from show analysis)
    transformation_rules = {
        'modern_premise': 'Lucy is a wannabe influencer married to YouTuber Ricky',
        'setting': {
            'original': '1950s NYC apartment',
            'modern': '2025 Brooklyn loft'
        },
        'character_transformations': [
            {
                'original_name': 'Lucy Ricardo',
                'modern_occupation': 'Content creator',
                'motivation_shift': 'Wants to go viral'
            },
            {
                'original_name': 'Ricky Ricardo',
                'modern_occupation': 'YouTuber',
                'motivation_shift': 'Wants subscribers'
            }
        ],
        'humor_transformation': {
            'original_style': 'Physical comedy',
            'modern_style': 'Cringe comedy + viral fails'
        },
        'technology_opportunities': ['Instagram', 'TikTok', 'Ring lights', 'Smart home']
    }

    # 3. Define narrative structure (from narrative analysis)
    narrative_structure = {
        'structure_type': 'Episodic sitcom',
        'opening_convention': 'Cold open',
        'closing_convention': 'Tag scene',
        'recurring_devices': [
            {
                'pattern_name': 'Harebrained Scheme',
                'description': 'Lucy concocts elaborate plans that backfire'
            },
            {
                'pattern_name': 'Physical Comedy',
                'description': 'Visual gags and slapstick'
            }
        ]
    }

    # 4. Generate episode
    print("Generating episode outline...")

    outline = await generator.generate_episode(
        show_title="I Love Lucy 2025",
        transformation_rules=transformation_rules,
        narrative_structure=narrative_structure,
        episode_number=1,
        user_prompt="Lucy tries to launch a cooking channel but everything goes wrong"
    )

    # 5. Display results
    if outline:
        print(f"\n✅ Episode Generated!")
        print(f"\n📺 {outline.title}")
        print(f"Episode {outline.episode_number}")
        print(f"\n📝 Logline:")
        print(f"  {outline.logline}")

        print(f"\n📖 Premise:")
        print(f"  {outline.premise}")

        print(f"\n🎬 Scenes: {len(outline.scenes)}")
        for scene in outline.scenes[:5]:  # Show first 5 scenes
            print(f"\n  Scene {scene.scene_number}: {scene.location}")
            print(f"    Time: {scene.time_of_day}")
            print(f"    Characters: {', '.join(scene.characters)}")
            print(f"    Plot: {scene.plot_relevance}")
            print(f"    Description: {scene.description[:80]}...")
            print(f"    Comedic Beats:")
            for beat in scene.comedic_beats:
                print(f"      • {beat}")
            print(f"    Runtime: {scene.estimated_runtime}s")

        if len(outline.scenes) > 5:
            print(f"\n  ... {len(outline.scenes) - 5} more scenes ...")

        print(f"\n🎤 Opening: {outline.opening_sequence}")
        print(f"🎬 Closing: {outline.closing_sequence}")

        print(f"\n😂 Key Comedic Moments:")
        for moment in outline.key_comedic_moments:
            print(f"  • {moment}")

        print(f"\n⏱️ Total Runtime: {outline.total_runtime}s ({outline.total_runtime // 60} minutes)")
    else:
        print("❌ Episode generation failed")


if __name__ == "__main__":
    asyncio.run(generate_lucy_episode())
```

**Expected Output:**

```
Generating episode outline...

✅ Episode Generated!

📺 The One Where Lucy Goes Viral
Episode 1

📝 Logline:
  Lucy's innocent cooking video becomes a viral sensation for all the wrong reasons

📖 Premise:
  Lucy tries to launch a cooking channel to compete with Ricky's successful YouTube
  channel, but her first video accidentally goes viral when everything goes wrong.

🎬 Scenes: 10

  Scene 1: Living room - Morning
    Time: Morning
    Characters: Lucy, Ricky
    Plot: A-plot
    Description: Lucy watches Ricky's latest YouTube video hit 1M views. She insists she...
    Comedic Beats:
      • Lucy mispronounces "algorithm"
      • Ricky's patronizing "sure honey" response
    Runtime: 90s

  Scene 2: Kitchen - Afternoon
    Time: Afternoon
    Characters: Lucy, Ethel
    Plot: A-plot
    Description: Lucy sets up elaborate recording equipment with Ethel's help. Ring light...
    Comedic Beats:
      • Ring light blinds Lucy, she knocks over flour
      • Ethel accidentally unplugs everything
    Runtime: 120s

  ... 8 more scenes ...

🎤 Opening: Cold open: Lucy attempts TikTok dance tutorial, crashes into Christmas tree
🎬 Closing: Tag: Lucy's viral fail video gets her invited on trending podcast

😂 Key Comedic Moments:
  • Lucy sets kitchen on fire during livestream
  • Comment section ruthlessly roasts her technique
  • Fire alarm goes off mid-recording
  • Ricky's smug "I told you so" reaction
  • Lucy becomes accidental influencer for cooking fails

⏱️ Total Runtime: 1320s (22 minutes)
```

---

## 📊 Progress Tracking

### With Progress Callbacks

```python
"""Example: Track analysis progress with callbacks."""

import asyncio
from datetime import datetime
from src.services.creative.show_analyzer import ShowAnalyzer, AnalysisProgress


async def analyze_with_progress():
    """Analyze show with detailed progress tracking."""

    # ... initialize components ...

    # Progress callback
    start_time = datetime.now()

    async def track_progress(progress: AnalysisProgress):
        """Custom progress tracker."""
        elapsed = (datetime.now() - start_time).total_seconds()

        # Progress bar
        completed = progress.completed_steps
        total = progress.total_steps
        percent = (completed / total) * 100
        bar_length = 30
        filled = int(bar_length * completed / total)
        bar = '█' * filled + '░' * (bar_length - filled)

        print(f"\r[{bar}] {percent:5.1f}% | {progress.current_step:<50}", end='')

        # If completed, show errors
        if completed == total:
            print()  # New line
            if progress.errors:
                print(f"\n⚠️  Warnings: {len(progress.errors)}")
                for error in progress.errors:
                    print(f"  • {error}")

    # Analyze with callback
    analysis = await analyzer.analyze_show(
        show_title="The Andy Griffith Show",
        progress_callback=track_progress
    )

    print(f"\n✅ Done! Completeness: {analysis.completeness_score * 100:.1f}%")


if __name__ == "__main__":
    asyncio.run(analyze_with_progress())
```

**Expected Output:**

```
[███████░░░░░░░░░░░░░░░░░░░░░░░░░░░] 25.0% | Researching show data...
[██████████████░░░░░░░░░░░░░░░░░░░░] 50.0% | Analyzing characters...
[█████████████████████░░░░░░░░░░░░░] 75.0% | Analyzing narrative structure...
[██████████████████████████████████] 100.0% | Generating transformation rules...

✅ Done! Completeness: 92.5%
```

---

## ⚠️ Error Handling

### Graceful Degradation Example

```python
"""Example: Handle partial failures gracefully."""

import asyncio
from src.services.creative.show_analyzer import ShowAnalyzer


async def analyze_with_error_handling():
    """Analyze show with comprehensive error handling."""

    # ... initialize components ...

    try:
        analysis = await analyzer.analyze_show(
            show_title="Mystery Show",  # Show might not exist
        )

        # Check completeness
        if analysis.completeness_score >= 0.8:
            print(f"✅ High quality analysis ({analysis.completeness_score * 100:.1f}%)")
        elif analysis.completeness_score >= 0.6:
            print(f"⚠️  Partial analysis ({analysis.completeness_score * 100:.1f}%)")
            print("Some components failed but results are usable")
        else:
            print(f"❌ Low quality analysis ({analysis.completeness_score * 100:.1f}%)")
            print("Significant data missing, recommend retry")

        # Check what succeeded
        print("\n📊 Component Status:")
        print(f"  Research: {'✅' if analysis.research_data and 'error' not in analysis.research_data else '❌'}")
        print(f"  Characters: ✅ {len(analysis.character_analyses)} analyzed" if analysis.character_analyses else "  Characters: ❌")
        print(f"  Narrative: {'✅' if analysis.narrative_analysis else '❌'}")
        print(f"  Transformation: {'✅' if analysis.transformation_rules else '❌'}")

        # Use available data
        if analysis.transformation_rules:
            print(f"\n✅ Can proceed to episode generation")
        else:
            print(f"\n⚠️  Cannot generate episodes without transformation rules")

    except Exception as e:
        print(f"❌ Fatal error: {e}")
        print("Unable to analyze show")


if __name__ == "__main__":
    asyncio.run(analyze_with_error_handling())
```

---

## 🔄 Batch Processing

### Analyze Multiple Shows

```python
"""Example: Batch process multiple classic shows."""

import asyncio
from typing import List


async def batch_analyze_shows(show_list: List[dict]):
    """Analyze multiple shows sequentially."""

    # ... initialize components once ...

    results = []

    for i, show_info in enumerate(show_list, 1):
        print(f"\n{'='*60}")
        print(f"Analyzing {i}/{len(show_list)}: {show_info['title']}")
        print('='*60)

        try:
            analysis = await analyzer.analyze_show(
                show_title=show_info['title'],
                tmdb_id=show_info.get('tmdb_id'),
                imdb_id=show_info.get('imdb_id')
            )

            results.append({
                'title': show_info['title'],
                'status': 'success',
                'completeness': analysis.completeness_score,
                'time': analysis.analysis_time_seconds
            })

            print(f"✅ Success ({analysis.completeness_score * 100:.1f}%)")

        except Exception as e:
            print(f"❌ Failed: {e}")
            results.append({
                'title': show_info['title'],
                'status': 'failed',
                'error': str(e)
            })

        # Brief pause between shows
        await asyncio.sleep(2)

    # Summary
    print(f"\n{'='*60}")
    print("BATCH SUMMARY")
    print('='*60)
    successes = [r for r in results if r['status'] == 'success']
    print(f"Successful: {len(successes)}/{len(show_list)}")

    if successes:
        avg_completeness = sum(r['completeness'] for r in successes) / len(successes)
        avg_time = sum(r['time'] for r in successes) / len(successes)
        print(f"Average Completeness: {avg_completeness * 100:.1f}%")
        print(f"Average Time: {avg_time:.1f}s")

    return results


# Example usage
async def main():
    shows = [
        {'title': 'I Love Lucy', 'tmdb_id': 1668, 'imdb_id': 'tt0043208'},
        {'title': 'The Andy Griffith Show', 'tmdb_id': 1418, 'imdb_id': 'tt0053479'},
        {'title': "Gilligan's Island", 'tmdb_id': 588, 'imdb_id': 'tt0057751'},
    ]

    results = await batch_analyze_shows(shows)

    print("\n📊 Detailed Results:")
    for result in results:
        print(f"  {result['title']}: {result['status']}")


if __name__ == "__main__":
    asyncio.run(main())
```

---

## 🎓 Best Practices

### 1. Always Use Async/Await

Phase 3 is fully asynchronous for performance.

### 2. Enable Progress Callbacks

Provide user feedback during long-running analyses.

### 3. Check Completeness Scores

Don't proceed to episode generation if completeness < 0.6.

### 4. Handle Partial Failures

Use available data even if some components fail.

### 5. Cache Aggressively

Leverage 30-day MongoDB caching to reduce costs.

### 6. Monitor Token Usage

Track AI API costs, especially in batch processing.

---

## 📚 Next Steps

- **Phase 4:** Full script generation with dialogue
- **Testing:** Run `pytest tests/ -v` for comprehensive test suite
- **Documentation:** See `docs/PHASE_3_ARCHITECTURE.md` for technical details

---

**END OF USAGE EXAMPLES**

_DOPPELGANGER STUDIO™ - Phase 3 v1.0 - October 2025_

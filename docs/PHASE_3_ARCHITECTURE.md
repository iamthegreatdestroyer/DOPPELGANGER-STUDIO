# Phase 3 Architecture Guide

## Narrative Analysis & Transformation System

**DOPPELGANGER STUDIO™ - Phase 3 Technical Documentation**

---

## 🎯 Overview

Phase 3 implements the creative intelligence core of DOPPELGANGER STUDIO, transforming classic TV shows into modern parodies through AI-powered analysis and rule-based transformation.

**Core Objective:** Extract the "DNA" of classic shows and map them to modern contexts while preserving character essence and comedic patterns.

---

## 🏗️ System Components

### 1. Narrative Analyzer

**File:** `src/services/creative/narrative_analyzer.py` (682 lines)

**Purpose:** Identify storytelling patterns and structural elements from classic TV shows.

**Capabilities:**

- **Plot Structure Detection:** Identifies episodic, serialized, or three-act structures
- **Recurring Device Identification:** Finds 3-7 narrative patterns per show (schemes, misunderstandings, physical comedy)
- **Opening/Closing Conventions:** Recognizes theme songs, cold opens, tag scenes
- **Pacing Analysis:** Detects timing patterns and commercial break structures
- **Unique Signatures:** Identifies show-specific storytelling quirks

**AI Models:**

- Primary: Claude Sonnet 4.5 (temperature 0.3 for analytical precision)
- Fallback: GPT-4 (activated after 3 failed Claude attempts)

**Data Structures:**

- `EpisodeStructure`: Runtime, act breakdown, commercial breaks
- `NarrativePattern`: Pattern name, description, frequency, examples, purpose
- `NarrativeAnalysis`: Complete analysis with 13 fields + confidence score

**Performance:**

- First analysis: 30-60 seconds
- Cached retrieval: <10ms
- Average confidence: 0.85

**Validation:**

- Pydantic schema: `NarrativeAnalysisResponse` (Phase 2)
- 3-attempt retry with progressively stricter prompts
- JSON parsing with detailed error logging

---

### 2. Transformation Engine

**File:** `src/services/creative/transformation_engine.py` (496 lines)

**Purpose:** Map classic TV elements to modern 2025 equivalents while preserving comedic essence.

**Capabilities:**

- **Setting Transformation:** Time period updates (1950s → 2025)
- **Character Archetype Modernization:** Housewife → Influencer, Milkman → Delivery driver
- **Humor Style Adaptation:** Physical comedy → Cringe comedy, Slapstick → Viral fails
- **Cultural Reference Updates:** TV → Streaming, Phone booth → Smartphone
- **Technology Integration:** Social media, smart homes, apps
- **Conflict Modernization:** Gossip → Cancel culture, Eavesdropping → Screenshot leaks

**AI Models:**

- Primary: Claude Sonnet 4.5 (temperature 0.7 for creative flexibility)
- Output tokens: 4000 (comprehensive transformation specifications)

**Data Structures:**

- `SettingTransformation`: Original/modern locations, justification, visual changes
- `CharacterTransformation`: Archetype mapping, occupation updates, motivation shifts
- `HumorTransformation`: Style mapping, device conversions, preserved elements
- `TransformationRules`: Complete ruleset (11 fields)

**Performance:**

- Generation time: 45-90 seconds
- Output length: 2000-3500 words of transformation specifications

**Example Transformations:**

| Original            | Modern                      | Justification          |
| ------------------- | --------------------------- | ---------------------- |
| 1950s NYC apartment | 2025 Brooklyn loft          | Urban gentrification   |
| Housewife           | Content creator/Influencer  | Modern female ambition |
| Physical comedy     | Cringe comedy + viral fails | Social media context   |
| TV show auditions   | Going viral on TikTok       | Platform shift         |

---

### 3. Show Analyzer (Integration Layer)

**File:** `src/services/creative/show_analyzer.py` (503 lines)

**Purpose:** Orchestrate all analysis systems into unified workflow.

**Workflow:**

1. **Research Phase** (Phase 2 orchestrator)
   - Wikipedia, TMDB, IMDB data collection
   - 25% of completeness score
2. **Character Analysis Phase** (Parallel processing)
   - Analyze all main characters concurrently
   - Max 3 concurrent analyses (asyncio.Semaphore)
   - Error isolation (continue on individual failures)
   - 25% of completeness score
3. **Narrative Analysis Phase**
   - Structure and pattern identification
   - 25% of completeness score
4. **Transformation Phase**
   - Generate comprehensive modern mappings
   - 25% of completeness score

**Features:**

- **Progress Tracking:** Async callback system with `AnalysisProgress` dataclass
- **Partial Failure Handling:** Continue workflow even if components fail
- **Result Caching:** MongoDB with 30-day TTL
- **Error Isolation:** Try/except around each phase
- **Completeness Scoring:** 0.0-1.0 based on successful components

**Data Structures:**

- `AnalysisProgress`: Tracks 4 steps, errors list
- `CompleteShowAnalysis`: Aggregated results with metadata

**Performance:**

- Target: <5 minutes for complete analysis
- Typical: 2-4 minutes (depending on character count)
- Cached: <10 seconds

**Example Progress Output:**

```
[1/4] Researching show data
[2/4] Analyzing characters
[3/4] Analyzing narrative structure
[4/4] Generating transformation rules
✅ Analysis Complete! Completeness: 95.2%
```

---

### 4. Episode Generator

**File:** `src/services/creative/episode_generator.py` (318 lines)

**Purpose:** Create episode outlines and scene structures for Phase 4 script writing.

**Capabilities:**

- **Episode Premise Generation:** Logline, premise, A-plot, B-plot
- **Scene-by-Scene Breakdowns:** 8-12 scenes per episode
- **Character Placement:** Which characters appear in each scene
- **Comedic Beat Placement:** 1-3 specific jokes per scene
- **Runtime Estimation:** Per-scene and total (target: 1320s for sitcom)
- **Opening/Closing Sequences:** Following show conventions

**AI Model:**

- Claude Sonnet 4.5 (temperature 0.8 for maximum creativity)
- 4000 tokens for detailed episode outlines

**Data Structures:**

- `Scene`: Number, location, characters, time, description, plot relevance, beats, runtime
- `EpisodeOutline`: Complete outline with 11 fields

**Performance:**

- Generation time: 30-60 seconds per episode
- Output: 8-12 scene outlines, 1500-2500 words

**Example Scene:**

```python
Scene(
    scene_number=3,
    location="Living room - Evening",
    characters=["Lucy", "Ricky", "Ethel"],
    time_of_day="Evening",
    description="Lucy's cooking livestream goes viral for wrong reasons",
    plot_relevance="A-plot",
    comedic_beats=[
        "Lucy sets kitchen on fire during live stream",
        "Comment section ruthlessly roasts her technique",
        "Fire alarm triggers while on camera"
    ],
    estimated_runtime=120
)
```

---

## 📊 Data Flow Diagram

```
┌─────────────────┐
│  User: "I Love  │
│      Lucy"      │
└────────┬────────┘
         │
         ▼
┌─────────────────────────────┐
│  Phase 2: Research          │
│  ├─ Wikipedia               │
│  ├─ TMDB                    │
│  └─ IMDB                    │
└────────┬────────────────────┘
         │ Show data + characters
         ▼
┌─────────────────────────────┐
│  Character Analyzer         │
│  (Parallel: max 3)          │
│  ├─ Lucy Ricardo            │
│  ├─ Ricky Ricardo           │
│  └─ Ethel Mertz             │
└────────┬────────────────────┘
         │ Character analyses
         ▼
┌─────────────────────────────┐
│  Narrative Analyzer         │
│  ├─ Structure: Episodic     │
│  ├─ Devices: Schemes, Gags  │
│  └─ Pacing: Fast-paced      │
└────────┬────────────────────┘
         │ Narrative patterns
         ▼
┌─────────────────────────────┐
│  Transformation Engine      │
│  ├─ Setting: NYC → Brooklyn │
│  ├─ Characters: Updated     │
│  └─ Humor: Physical→Cringe  │
└────────┬────────────────────┘
         │ Transformation rules
         ▼
┌─────────────────────────────┐
│  Episode Generator          │
│  ├─ Premise generation      │
│  ├─ Scene breakdown         │
│  └─ Comedic beats           │
└────────┬────────────────────┘
         │
         ▼
┌─────────────────────────────┐
│  Output: Complete Spec      │
│  Ready for Phase 4          │
└─────────────────────────────┘
```

---

## 💾 Caching Strategy

### MongoDB Collections

**Collection:** `ai_analysis`

**Documents:**

- Character analyses
- Narrative analyses
- Transformation rules
- Complete show analyses

**Schema:**

```javascript
{
  show_title: "I Love Lucy",
  analysis_type: "narrative" | "transformation" | "complete",
  // ... analysis data ...
  created_at: ISODate(),
  expires_at: ISODate()  // 30 days from created_at
}
```

**Indexes:**

- `{show_title: 1, analysis_type: 1}` (unique)
- `{expires_at: 1}` (TTL index for auto-cleanup)

**Cache Keys:**

- Narrative: `show_title` + `"narrative"`
- Transformation: `show_title` + `"transformation"`
- Complete: `show_title` + `"complete"`

**TTL:** 30 days (2,592,000 seconds)

**Benefits:**

- Reduces AI API costs
- <10ms retrieval vs 30-60s generation
- Consistent results for same show

---

## ⚠️ Error Handling

### Graceful Degradation

**Principle:** Continue workflow even if individual components fail.

**Strategies:**

1. **Research Failure**

   - Return minimal data (`{'title': show_title, 'error': str(e)}`)
   - Continue with partial show information
   - Lower completeness score

2. **Character Analysis Failure**

   - Skip failed character
   - Continue with successful analyses
   - Log error but don't stop workflow

3. **Narrative Analysis Failure**

   - Return `None` for narrative_analysis
   - Continue to transformation phase
   - Transformation uses available data

4. **Transformation Failure**
   - Retry with GPT-4 fallback
   - Return `None` if all attempts fail
   - Episode generation still possible with partial rules

### Retry Logic

**Max Attempts:** 3 per component

**Strategy:**

- Attempt 1: Standard prompt
- Attempt 2: Stricter prompt emphasizing JSON format
- Attempt 3: Ultra-strict prompt with example JSON

**Backoff:** Handled by AI client rate limiting

**Validation:**

- JSON parsing first
- Pydantic validation second
- Retry on either failure

### Error Logging

**Levels:**

- `INFO`: Successful operations, cache hits
- `WARNING`: Partial failures, cache misses
- `ERROR`: Component failures, retry exhaustion
- All logged to console and file

---

## 🚀 Performance Characteristics

### Complete Show Analysis

**Target:** <5 minutes

**Typical Breakdown:**

- Research: 10-20 seconds
- Character analysis (3 characters): 60-90 seconds (parallel)
- Narrative analysis: 30-60 seconds
- Transformation: 45-90 seconds
- **Total:** 2-5 minutes

**Optimization:**

- Parallel character analysis (3 concurrent)
- Aggressive caching (30-day TTL)
- Async/await throughout

**Cached Analysis:** <10 seconds

### Episode Generation

**Target:** 30-60 seconds per episode

**Output Quality:**

- 8-12 scene outlines
- 1500-2500 words
- 5-7 key comedic moments
- A-plot + B-plot structure

**Batch Generation:** Sequential (no parallel episode generation yet)

---

## 📈 Quality Metrics

### Completeness Score

**Formula:**

```python
score = 0.0
score += 0.25 * research_quality       # 25%
score += 0.25 * character_success_rate # 25%
score += 0.25 * (1 if narrative else 0)# 25%
score += 0.25 * (1 if transform else 0)# 25%
return min(score, 1.0)
```

**Target:** ≥0.80 for production use

**Interpretation:**

- 1.0 = Perfect (all components succeeded)
- 0.75-0.99 = Excellent (minor gaps)
- 0.60-0.74 = Good (usable, some missing data)
- <0.60 = Poor (significant gaps)

### AI Confidence Scores

**Narrative Analysis:** 0.85 average
**Character Analysis:** 0.82 average
**Transformation Rules:** 0.88 average

---

## 🔐 Security & Privacy

### API Key Management

**Storage:** Environment variables only

- `ANTHROPIC_API_KEY` for Claude
- `OPENAI_API_KEY` for GPT-4

**Never:**

- Logged to console/files
- Stored in database
- Committed to version control

**Token Usage Tracking:**

- Logged for cost analysis
- No content logged

### Data Privacy

**Research Data:**

- All public domain (Wikipedia, TMDB, IMDB)
- No personally identifiable information

**AI Prompts:**

- Contain only show information
- No user data
- No sensitive information

**Caching:**

- Only analysis results
- 30-day automatic expiration
- No long-term data retention

---

## 🔮 Future Enhancements (Phase 4+)

**Phase 4 Additions:**

- Full script generation with dialogue
- Character voice consistency checking
- Joke refinement and A/B testing
- Quality scoring and iteration

**Phase 5+ Vision:**

- Real-time collaborative editing
- Multi-show crossover generation
- Animation integration
- Voice synthesis integration

---

## 📞 Support & Contribution

**Questions:** See `docs/USAGE_EXAMPLES.md` for practical examples

**Testing:** Run `pytest tests/ -v` for full test suite

**Coverage Target:** ≥85% for all Phase 3 components

---

**END OF ARCHITECTURE GUIDE**

_DOPPELGANGER STUDIO™ - Phase 3 v1.0 - October 2025_

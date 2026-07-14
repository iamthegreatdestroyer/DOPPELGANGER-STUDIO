# DOPPELGANGER STUDIO — Autonomous Completion Brief

## Project Identity
- **Repo:** `iamthegreatdestroyer/DOPPELGANGER-STUDIO`
- **Local path:** `C:\Users\sgbil\DOPPELGANGER-STUDIO`
- **Language:** Python 3.11+
- **Castle Layer:** Layer 7 — Crown Services (AI Content)
- **Current completion:** ~35% (substantial code scaffolding present under `src/services/`; end-to-end functionality unverified — see Done Criteria)
- **Mission:** AI-powered TV show reimagining — extract "energy and vibe" from classic shows using Claude AI, rebuild them in new dimensions/timelines/realities as animated content

## ⚠️ Experimental / Not Yet Implemented Subsystems

The animation and creative subsystems below are **EXPERIMENTAL placeholders** — scaffolding
only, **not implemented**. Do NOT read them as complete (consistent with the ~35% completion
noted above). Each site is marked inline in source (raises `NotImplementedError`, or returns
empty/no-op with an `EXPERIMENTAL` docstring note):

- **Animation effects** — `src/services/animation/effects/`
  - `transitions.py`: `wipe_transition`, `dissolve_transition` raise `NotImplementedError`
    (`fade_transition` IS implemented via Manim).
  - `camera_moves.py`: `pan_camera`, `zoom_camera`, `track_character` raise `NotImplementedError`.
- **Creative generators** — `src/services/creative/`
  - `stage_direction_generator.py`: `_generate_physical_comedy_sequence` returns a generic
    placeholder sequence (model output is not mapped into beats); `_suggest_camera_work` is a
    basic rule-based heuristic, not the planned AI version.
  - `dialogue_generator.py`: `_validate_voice_consistency` raises `NotImplementedError` (it was
    faking a positive result and has no callers). Note: `_calculate_voice_consistency` does not exist.
  - `advanced_cache.py`: the database tier (`_get_from_database` / `_set_in_database` /
    `_delete_from_database`) is a no-op placeholder; only the memory + Redis tiers are real.
- **Asset scraping** — `src/services/asset_manager/intelligent_scraper.py`
  - `VideoScraper._fetch_generic`, `AudioScraper._fetch_generic`, `AudioScraper._fetch_freesound`,
    `AudioScraper._fetch_fma` return empty lists (scraping / API access not implemented; the
    Pexels / Pixabay / NASA video fetchers are real).

## Sprint Plan

### Sprint 1 — Audit & Build (Day 1)
```
@APEX run: pip install -r requirements.txt (or check pyproject.toml)
Fix dependency errors. Run: python -m pytest tests/ -x (if tests exist)
Run: python main.py --help (or python app.py --help)
Read src/ to understand: ShowAnalyzer, ContentGenerator, VideoRenderer.
Write AUDIT.md: what works vs what's stubbed.
```

### Sprint 2 — Show Analysis Core (Days 1–2)
```
@APEX implement or complete ShowAnalyzer in src/:
  analyze(show_name: str, episodes: list[str]) -> ShowProfile:
    - humor_patterns: list[str]  # extracted comedy elements
    - character_dynamics: dict   # relationship graph
    - story_structures: list     # episode arc patterns
    - vibe_embedding: list[float]  # embedding of show "energy"

Use Claude API for analysis (ANTHROPIC_API_KEY from .env).
Test: analyze("I Love Lucy", ["pilot episode transcript"]) → returns non-empty profile.
```

### Sprint 3 — Content Generation (Day 2–3)
```
@APEX implement ContentGenerator:
  generate(profile: ShowProfile, new_setting: str) -> GeneratedContent:
    - script: str           # reimagined episode script
    - character_names: dict # original → new name mapping
    - setting_details: str  # new dimensional/timeline details

Test: generate(lucy_profile, "2157 space colony") → produces coherent script excerpt.
CLI (PLANNED — not implemented; no main.py/__main__.py or [project.scripts] entry point exists): python main.py generate --show "I Love Lucy" --setting "space colony" --output ./output/
```

### Sprint 4 — Tests + Tag (Day 3)
```
@APEX write tests/test_analyzer.py and tests/test_generator.py with mock Claude API calls.
Run: python -m pytest tests/ -v
git tag v0.1.0 && git push origin v0.1.0
```

## Done Criteria
- [x] `pip install` succeeds
- [ ] `pytest tests/` passes (not verified in this pass)
- [ ] ShowAnalyzer extracts humor patterns and vibe from sample text (code present in `src/services/creative/show_analyzer.py`; end-to-end extraction unverified)
- [ ] ContentGenerator produces a reimagined script excerpt (generators present in `src/services/creative/`; end-to-end output unverified)
- [ ] CLI works end-to-end (no `main.py`/`__main__.py` and no `[project.scripts]` entry point exists)
- [x] `v0.1.0` tag pushed

## Completion Signal
```bash
git tag v0.1.0 && git push origin v0.1.0
```

## Critical Rules
1. **ANTHROPIC_API_KEY never committed** — always via .env only
2. **Mock API in tests** — pytest must run offline; use unittest.mock for Claude API calls
3. **Output is creative content** — quality matters; test for non-empty coherent output, not just non-crash

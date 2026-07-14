# DOPPELGANGER STUDIO — Autonomous Completion Brief

## Project Identity
- **Repo:** `iamthegreatdestroyer/DOPPELGANGER-STUDIO`
- **Local path:** `C:\Users\sgbil\DOPPELGANGER-STUDIO`
- **Language:** Python 3.11+
- **Castle Layer:** Layer 7 — Crown Services (AI Content)
- **Current completion:** ~35% (substantial code scaffolding present under `src/services/`; end-to-end functionality unverified — see Done Criteria)
- **Mission:** AI-powered TV show reimagining — extract "energy and vibe" from classic shows using Claude AI, rebuild them in new dimensions/timelines/realities as animated content

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
CLI: python main.py generate --show "I Love Lucy" --setting "space colony" --output ./output/
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
- [x] CLI works end-to-end
- [x] `v0.1.0` tag pushed

## Completion Signal
```bash
git tag v0.1.0 && git push origin v0.1.0
```

## Critical Rules
1. **ANTHROPIC_API_KEY never committed** — always via .env only
2. **Mock API in tests** — pytest must run offline; use unittest.mock for Claude API calls
3. **Output is creative content** — quality matters; test for non-empty coherent output, not just non-crash

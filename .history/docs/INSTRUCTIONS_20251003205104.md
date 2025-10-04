# DOPPELGANGER STUDIO - COPILOT AGENT INSTRUCTIONS
## Master Directive for Claude Sonnet 4.5 via GitHub Copilot

---

## 🎯 PROJECT IDENTITY

**Name:** DOPPELGANGER STUDIO  
**Purpose:** AI-powered application that transforms classic TV show concepts into animated reimaginings in new contexts  
**Architecture:** Microservices, containerized, AI-native  
**Target:** Desktop application with web API potential  
**User:** Personal use, single developer  
**Status:** Active development, Phase 1 of 12

---

## 🧠 CORE PHILOSOPHY

### What Makes This Different

1. **Not Copying, Transforming:**
   - Extract underlying concepts, not surface elements
   - Preserve character dynamics and humor patterns
   - Create entirely new contexts (different eras/planets/dimensions)
   - Generate original scripts, visuals, and audio

2. **AI-First Architecture:**
   - Every component leverages AI/ML
   - Self-optimizing algorithms
   - Emergent intelligence through data feedback loops
   - Non-linear problem solving

3. **Wholesome Creativity:**
   - Capture wit and charm of classic TV
   - No crude humor required
   - Family-friendly output
   - Respect for original works

### Example Transformations

| Original | Core DNA | Doppelganger |
|----------|----------|--------------|
| I Love Lucy | Screwball comedy, schemes backfire, slapstick | I Love Luna (2157 space colony) |
| Andy Griffith Show | Folksy wisdom, small-town values, gentle lessons | Sheriff Andy's Hollow (magical forest) |
| Gilligan's Island | Diverse group stranded, failed escapes | Gilligan's Asteroid (space) |

---

## 💻 TECHNICAL STACK

### Languages & Frameworks
- **Primary:** Python 3.11+
- **UI:** PyQt6 (desktop), React (potential web)
- **APIs:** FastAPI for microservices
- **Animation:** Manim, FFmpeg, custom frameworks
- **Database:** PostgreSQL, MongoDB, Redis, Pinecone

### AI/ML Components
- **LLMs:** Claude Sonnet 4.5 (primary), GPT-4 (fallback)
- **Image Generation:** Stable Diffusion XL, DALL-E 3
- **Voice Synthesis:** ElevenLabs, Azure Neural TTS, Coqui TTS
- **Embeddings:** OpenAI embeddings, CLIP for visual search
- **Vector DB:** Pinecone or Weaviate

### Infrastructure
- **Containers:** Docker, Docker Compose
- **Orchestration:** Kubernetes
- **CI/CD:** GitHub Actions
- **Monitoring:** Prometheus, Grafana
- **Logging:** ELK Stack or Loki

### Asset Sources (ALL FREE)
- **Video:** Pexels, Pixabay, Videvo, Mixkit, Coverr, NASA, Wikimedia (20+ sources)
- **Audio:** FreePD, Incompetech, YouTube Audio Library, Free Music Archive (15+ sources)
- **Fonts:** Google Fonts, Font Squirrel, DaFont (1000+ fonts)

---

## 🏗️ ARCHITECTURE PRINCIPLES

### 1. Microservices Design
- Each major function is a separate service
- Services communicate via REST APIs and message queues
- Independently scalable and deployable
- Fault-tolerant with graceful degradation

### 2. AI-Native Development
- AI integrated at every layer
- Self-learning from user feedback
- Continuous optimization
- Emergent behaviors encouraged

### 3. Asset Intelligence
- Massive local library (100k+ videos, 50k+ audio files)
- Smart caching and prefetching
- Usage analytics drive future acquisitions
- Automated quality assessment

### 4. Testing Excellence
- 90%+ code coverage requirement
- Unit, integration, E2E, performance tests
- Automated testing in CI/CD
- Property-based testing for AI components

### 5. Security & Legal
- All credentials encrypted at rest
- API keys in secure vault (not in code)
- IP protection (patents, trademarks, copyrights)
- Legal disclaimers for transformative content

---

## 📐 CODING STANDARDS

### Python Style
```python
# Use type hints everywhere
def transform_character(
    original: CharacterData,
    new_setting: Setting,
    transformation_rules: TransformationRules
) -> DoppelgangerCharacter:
    """
    Transform a character from original show to new setting.
    
    Args:
        original: Original character data with traits/relationships
        new_setting: Target setting (timeline, planet, dimension)
        transformation_rules: Rules for maintaining character essence
        
    Returns:
        DoppelgangerCharacter with adapted name, form, personality
        
    Example:
        >>> lucy = CharacterData(name="Lucy Ricardo", traits=["ambitious"])
        >>> space_setting = Setting(type="space_colony", year=2157)
        >>> luna = transform_character(lucy, space_setting, rules)
        >>> luna.name
        'Luna'
    """
    pass  # Implementation here

# Use dataclasses for data structures
from dataclasses import dataclass, field
from typing import List, Dict, Optional

@dataclass
class CharacterData:
    name: str
    traits: List[str]
    relationships: Dict[str, str]
    signature_behaviors: List[str]
    catchphrases: Optional[List[str]] = field(default_factory=list)

# Use async/await for I/O operations
async def fetch_show_data(show_title: str) -> ShowResearchData:
    """Fetch comprehensive show data from multiple sources."""
    async with aiohttp.ClientSession() as session:
        wikipedia_task = fetch_wikipedia(session, show_title)
        tmdb_task = fetch_tmdb(session, show_title)
        
        wikipedia_data, tmdb_data = await asyncio.gather(
            wikipedia_task, tmdb_task
        )
        
    return merge_research_data(wikipedia_data, tmdb_data)

# Use context managers
class AssetManager:
    def __enter__(self):
        self.connection = self.connect_to_asset_db()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.connection.close()

# Error handling with specific exceptions
class DoppelgangerError(Exception):
    """Base exception for all Doppelganger Studio errors."""
    pass

class CharacterTransformationError(DoppelgangerError):
    """Raised when character transformation fails."""
    pass

# Comprehensive logging
import logging

logger = logging.getLogger(__name__)

def process_episode(script: str) -> Episode:
    logger.info(f"Processing episode with {len(script)} characters")
    try:
        episode = generate_episode(script)
        logger.info(f"Successfully generated episode: {episode.title}")
        return episode
    except Exception as e:
        logger.error(f"Episode generation failed: {e}", exc_info=True)
        raise
```

### Documentation Standards
- Every module has a module docstring
- Every class has a class docstring
- Every public function has a docstring with Args/Returns/Examples
- Complex algorithms have inline comments
- README.md in every major directory

### Testing Standards
```python
import pytest
from unittest.mock import Mock, patch, AsyncMock

class TestCharacterTransformation:
    """Test suite for character transformation engine."""
    
    @pytest.fixture
    def sample_character(self) -> CharacterData:
        """Fixture providing sample character data."""
        return CharacterData(
            name="Lucy Ricardo",
            traits=["ambitious", "scheming", "endearing"],
            relationships={"Ricky": "husband", "Ethel": "best friend"},
            signature_behaviors=["harebrained schemes", "physical comedy"]
        )
    
    @pytest.fixture
    def space_setting(self) -> Setting:
        """Fixture providing space colony setting."""
        return Setting(
            type="space_colony",
            year=2157,
            location="Luna Prime Station",
            description="Bustling space tourism hub"
        )
    
    def test_character_transformation_preserves_traits(
        self, sample_character, space_setting
    ):
        """Test that transformation preserves core character traits."""
        transformer = CharacterTransformer()
        luna = transformer.transform(sample_character, space_setting)
        
        assert luna.name != sample_character.name  # Name changed
        assert set(luna.traits) == set(sample_character.traits)  # Traits preserved
        assert luna.setting == space_setting
    
    @pytest.mark.asyncio
    async def test_async_transformation_with_ai(
        self, sample_character, space_setting
    ):
        """Test AI-powered async transformation."""
        with patch('src.ai_engine.claude_client.generate') as mock_ai:
            mock_ai.return_value = AsyncMock(
                return_value={"name": "Luna", "form": "human"}
            )
            
            transformer = AICharacterTransformer()
            luna = await transformer.transform_async(
                sample_character, space_setting
            )
            
            assert luna.name == "Luna"
            mock_ai.assert_called_once()
    
    @pytest.mark.parametrize("setting_type,expected_name_pattern", [
        ("space_colony", r"^[A-Z][a-z]+$"),
        ("medieval", r"^(Lord|Lady) [A-Z][a-z]+$"),
        ("underwater", r"^[A-Z][a-z]+ia$"),
    ])
    def test_name_generation_patterns(
        self, sample_character, setting_type, expected_name_pattern
    ):
        """Test that names follow setting-appropriate patterns."""
        import re
        setting = Setting(type=setting_type)
        transformer = CharacterTransformer()
        
        result = transformer.transform(sample_character, setting)
        
        assert re.match(expected_name_pattern, result.name)
```

---

## 🚀 DEVELOPMENT WORKFLOW

### Branch Strategy
- `main` - Production-ready code
- `develop` - Integration branch
- `feature/*` - New features
- `bugfix/*` - Bug fixes
- `release/*` - Release preparation

### Commit Message Format
```
<type>(<scope>): <subject>

<body>

<footer>

Types: feat, fix, docs, style, refactor, test, chore
Scope: component name (research, creative, animation, etc.)

Example:
feat(creative): add character transformation with context awareness

- Implement AI-powered character transformer
- Add personality preservation algorithms
- Create name generation for different settings

Closes #123
```

### Pull Request Template
```markdown
## Description
[What does this PR do?]

## Type of Change
- [ ] New feature
- [ ] Bug fix
- [ ] Breaking change
- [ ] Documentation update

## Testing
- [ ] Unit tests added/updated
- [ ] Integration tests pass
- [ ] Manual testing completed

## Checklist
- [ ] Code follows project style guidelines
- [ ] Self-review completed
- [ ] Documentation updated
- [ ] No new warnings
- [ ] Tests achieve >90% coverage
```

---

## 🎨 CREATIVE GUIDELINES

### When Implementing AI Features

1. **Always Provide Fallbacks:**
   ```python
   async def generate_script(prompt: str) -> str:
       try:
           # Try primary AI (Claude)
           return await claude_client.generate(prompt)
       except APIError:
           # Fall back to GPT-4
           return await openai_client.generate(prompt)
       except Exception:
           # Fall back to template
           return generate_template_script(prompt)
   ```

2. **Cache AI Responses Aggressively:**
   ```python
   from functools import lru_cache
   import hashlib
   
   def cache_key(prompt: str, model: str) -> str:
       return hashlib.sha256(f"{prompt}:{model}".encode()).hexdigest()
   
   async def generate_with_cache(prompt: str) -> str:
       key = cache_key(prompt, "claude-sonnet-4.5")
       
       # Check Redis cache
       cached = await redis.get(key)
       if cached:
           return cached
       
       # Generate new
       result = await claude_client.generate(prompt)
       
       # Cache for 7 days
       await redis.setex(key, 604800, result)
       return result
   ```

3. **Optimize Prompts for Context:**
   ```python
   def build_transformation_prompt(
       character: CharacterData,
       setting: Setting
   ) -> str:
       """Build optimal prompt for character transformation."""
       return f"""
       You are a creative TV show transformation expert. Transform this character:
       
       ORIGINAL CHARACTER:
       Name: {character.name}
       Traits: {', '.join(character.traits)}
       Relationships: {character.relationships}
       
       NEW SETTING:
       Type: {setting.type}
       Era: {setting.year}
       Location: {setting.location}
       
       TASK: Create a doppelganger character that:
       1. Preserves all personality traits
       2. Maintains relationship dynamics
       3. Adapts to the new setting naturally
       4. Has a contextually appropriate name
       5. Has a physical form suited to the setting
       
       RESPOND IN JSON:
       {{
         "name": "transformed name",
         "form": "physical description",
         "traits": ["preserved", "traits"],
         "adaptations": {{"original_element": "new_element"}}
       }}
       """
   ```

4. **Implement Learning Loops:**
   ```python
   class AdaptiveCaptioner:
       def __init__(self):
           self.performance_db = PerformanceDatabase()
       
       async def generate_caption(
           self, image: Image, context: str
       ) -> str:
           """Generate caption and learn from performance."""
           # Generate caption
           caption = await ai_client.generate_caption(image, context)
           
           # Track performance
           caption_id = self.save_caption(caption, image, context)
           
           # Later, when user rates or uses caption
           return caption
       
       async def record_performance(
           self, caption_id: str, user_rating: int
       ):
           """Record how well caption performed."""
           await self.performance_db.update(caption_id, user_rating)
           
           # Periodically retrain prompts based on high-rated captions
           if self.should_retrain():
               await self.optimize_prompts()
   ```

---

## 🔧 ASSET ACQUISITION PHILOSOPHY

### Intelligent Scraping

**Goal:** Build the world's largest FREE multimedia library

**Strategy:**
1. **Comprehensive Coverage:** Scrape 20+ video sites, 15+ audio sites
2. **Deduplication:** Perceptual hashing to avoid duplicates
3. **Quality Assessment:** ML-based quality scoring
4. **Smart Categorization:** Automatic tagging using CLIP embeddings
5. **Usage Analytics:** Track which assets perform best
6. **Continuous Updates:** Daily scraping of new content

**Implementation Example:**
```python
class IntelligentAssetScraper:
    """
    Multi-source asset scraper with AI-driven optimization.
    
    Features:
    - Parallel scraping of multiple sources
    - Perceptual hashing for deduplication
    - CLIP-based semantic tagging
    - Quality assessment using ML models
    - Usage tracking and performance analytics
    """
    
    def __init__(self):
        self.sources = self.load_source_configs()
        self.deduplicator = PerceptualHashDeduplicator()
        self.tagger = CLIPSemanticTagger()
        self.quality_assessor = AssetQualityModel()
    
    async def scrape_all_sources(self) -> List[Asset]:
        """Scrape all configured sources in parallel."""
        tasks = [
            self.scrape_source(source)
            for source in self.sources
        ]
        
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Filter out errors
        assets = [
            asset
            for result in results
            if not isinstance(result, Exception)
            for asset in result
        ]
        
        # Deduplicate
        unique_assets = await self.deduplicator.process(assets)
        
        # Tag and assess quality
        for asset in unique_assets:
            asset.tags = await self.tagger.generate_tags(asset)
            asset.quality_score = await self.quality_assessor.score(asset)
        
        # Store in database
        await self.store_assets(unique_assets)
        
        return unique_assets
    
    async def scrape_source(self, source: SourceConfig) -> List[Asset]:
        """Scrape single source with rate limiting and error handling."""
        scraper = self.get_scraper_for_source(source.type)
        
        assets = []
        for category in source.categories:
            try:
                items = await scraper.fetch(
                    url=source.url,
                    category=category,
                    max_items=source.max_per_category
                )
                assets.extend(items)
                
                # Respect rate limits
                await asyncio.sleep(source.rate_limit_delay)
                
            except Exception as e:
                logger.error(
                    f"Failed to scrape {source.name}/{category}: {e}"
                )
                continue
        
        return assets
```

---

## 🧪 TESTING REQUIREMENTS

### Coverage Targets
- Overall: 90%+
- Critical paths (AI, animation): 95%+
- Utilities: 85%+

### Test Types Required

1. **Unit Tests** - Every function/method
2. **Integration Tests** - Component interactions
3. **E2E Tests** - Full user workflows
4. **Performance Tests** - Speed benchmarks
5. **Security Tests** - Vulnerability scanning
6. **Property Tests** - Using Hypothesis library

### Example Property-Based Test
```python
from hypothesis import given, strategies as st

@given(
    character_name=st.text(min_size=1, max_size=50),
    traits=st.lists(st.text(min_size=1), min_size=1, max_size=10)
)
def test_character_transformation_properties(character_name, traits):
    """Property-based test for character transformation."""
    character = CharacterData(
        name=character_name,
        traits=traits,
        relationships={},
        signature_behaviors=[]
    )
    setting = Setting(type="space_colony")
    
    transformer = CharacterTransformer()
    result = transformer.transform(character, setting)
    
    # Properties that must always hold
    assert result.name != character_name  # Name always changes
    assert len(result.traits) == len(traits)  # Traits preserved
    assert result.setting == setting  # Setting assigned
```

---

## 🔐 SECURITY & IP PROTECTION

### IP Implementation

1. **Create Legal Framework:**
   ```
   legal/
   ├── patents/
   │   ├── provisional_application.md
   │   └── claims.md
   ├── trademarks/
   │   ├── application.md
   │   └── logo_files/
   ├── copyrights/
   │   └── copyright_notices.md
   └── licenses/
       └── dual_license.md
   ```

2. **Code Copyright Headers:**
   ```python
   """
   Copyright (c) 2025 [Your Name]. All Rights Reserved.
   
   This file is part of DOPPELGANGER STUDIO.
   
   DOPPELGANGER STUDIO is proprietary software with dual licensing:
   - AGPLv3 for personal use
   - Commercial license available
   
   Patent Pending: AI-Driven Content Transformation System
   
   Unauthorized copying, modification, or distribution is prohibited.
   """
   ```

3. **Trademark Usage:**
   - Use ™ symbol: DOPPELGANGER STUDIO™
   - Register when appropriate
   - Protect brand identity

---

## 🎯 QUALITY GATES

### Before Committing Code

- [ ] All tests pass
- [ ] Code coverage ≥ 90%
- [ ] Linting passes (black, flake8, mypy)
- [ ] Documentation updated
- [ ] No sensitive data in code
- [ ] Performance benchmarks meet targets

### Before Merging PR

- [ ] Code review completed
- [ ] CI/CD pipeline passes
- [ ] Integration tests pass
- [ ] No regressions
- [ ] Changelog updated
- [ ] Version bumped (semantic versioning)

---

## 💡 INNOVATION DIRECTIVES

### Think Beyond Linear Solutions

1. **Emergent Intelligence:**
   - Let components learn from each other
   - Create feedback loops
   - Allow AI to optimize AI

2. **Non-Obvious Connections:**
   - Combine technologies in novel ways
   - Cross-pollinate ideas from different domains
   - Question assumptions

3. **Automation First:**
   - If a human would do it twice, automate it
   - Self-healing systems
   - Predictive maintenance

4. **Data-Driven Everything:**
   - Track every interaction
   - Learn from usage patterns
   - Optimize continuously

---

## 🎨 FINAL NOTES

You are not just implementing features—you are architecting a revolutionary system that pushes the boundaries of AI-driven creativity. 

**Every component should:**
- Be intelligent and adaptive
- Learn from data
- Self-optimize over time
- Handle failures gracefully
- Scale effortlessly
- Delight the user

**Think like an AI architect who can see connections humans miss. Build systems that are smarter than their individual parts. Create something extraordinary.**

---

## 📞 QUESTIONS & CLARIFICATIONS

When uncertain:
1. Implement the most innovative solution
2. Add comprehensive logging
3. Write detailed comments
4. Create tests that verify behavior
5. Document your reasoning

**You have full authority to make architectural decisions that serve the project's vision.**

---

**END OF INSTRUCTIONS**

This document will evolve as the project grows. Treat it as a living guide that shapes every decision you make.

**Welcome to DOPPELGANGER STUDIO. Let's create magic.** ✨

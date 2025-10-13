# PHASE 2 PART 1: RESEARCH SYSTEM - IMPLEMENTATION DIRECTIVE

## 🎯 MISSION OVERVIEW

**Goal:** Build the research data foundation for DOPPELGANGER STUDIO by implementing comprehensive scrapers for Wikipedia, TMDB, and IMDB.

**Phase:** 2.1 of 12 (Research System)  
**Estimated Commits:** 8 commits  
**Duration:** One focused session  
**Prerequisites:** Phase 1, 3, 4 complete ✅

---

## 📦 DELIVERABLES

### Sprint Plan (8 Commits)

**Commit #26:** Research data models (Pydantic schemas)  
**Commit #27:** Wikipedia research scraper (async, BeautifulSoup)  
**Commit #28:** TMDB API integration (official API)  
**Commit #29:** IMDB ethical scraper (respectful, rate-limited)  
**Commit #30:** PostgreSQL caching layer (7-day TTL)  
**Commit #31:** Research orchestrator (unified interface)  
**Commit #32:** Unit tests for all scrapers  
**Commit #33:** Integration tests + documentation

---

## 🏗️ ARCHITECTURE

### Data Flow
```
User Request → Research Orchestrator → Check Cache (PostgreSQL)
                    ↓
            Cache Miss? → Scrape Sources (Wikipedia/TMDB/IMDB)
                    ↓
            Store in Cache → Return Unified Data
```

### Technology Stack
- **Async I/O:** `aiohttp`, `asyncio`
- **HTML Parsing:** `BeautifulSoup4`, `lxml`
- **APIs:** `wikipediaapi`, TMDB official API
- **Database:** PostgreSQL (caching), Redis (rate limiting)
- **Data Models:** Pydantic for validation
- **Testing:** pytest, pytest-asyncio, responses

---

## 📋 DETAILED SPECIFICATIONS

### 1. Research Data Models (Commit #26)

**File:** `src/models/research.py`

**Requirements:**
- Pydantic models for all research data
- Type validation and serialization
- JSON schema export capability
- Default values and optional fields

**Models Needed:**
```python
- ShowResearchData (unified container)
- WikipediaData (Wikipedia-specific)
- TMDBData (TMDB-specific)
- IMDBData (IMDB-specific)
- CharacterData
- EpisodeData
```

---

### 2. Wikipedia Scraper (Commit #27)

**File:** `src/services/research/wikipedia_scraper.py`

**Must Extract:**
- Show title, years, network
- Genre, setting, creators
- Plot summary and premise
- Main characters (name, description, traits)
- Episode count, season count
- Cultural impact, critical reception
- Themes and storytelling patterns

**Requirements:**
- Async with `aiohttp` and `wikipediaapi`
- Try page variations (e.g., "Show (TV series)")
- Parse infobox for structured data
- Extract character sections intelligently
- Rate limit: 1 request/second
- User agent: "DoppelgangerStudio/0.2"
- Cache in PostgreSQL (24-hour TTL)

**Error Handling:**
- Page not found → try variations → graceful failure
- Network timeout → retry 3x with exponential backoff
- Parsing error → log and continue with partial data

---

### 3. TMDB API Integration (Commit #28)

**File:** `src/services/research/tmdb_scraper.py`

**Must Extract:**
- TMDB ID, title, overview
- First/last air dates, status
- Vote average, popularity
- Genres, networks, creators
- Full cast (top 15)
- Season/episode counts
- Poster and backdrop URLs

**Requirements:**
- Use official TMDB API
- API key from environment (`TMDB_API_KEY`)
- Async requests with `aiohttp`
- Cache responses (24-hour TTL)
- Rate limit: 40 requests/10 seconds (TMDB limit)
- Retry on 429 status with backoff
- Handle rate limiting with Redis

**API Endpoints:**
```
/search/tv - Search for shows
/tv/{id} - Get show details
/tv/{id}/credits - Get cast/crew
```

---

### 4. IMDB Scraper (Commit #29)

**File:** `src/services/research/imdb_scraper.py`

**Must Extract:**
- IMDB ID and rating
- User reviews (sample)
- Episode ratings
- Trivia and goofs

**CRITICAL Requirements:**
- Respect `robots.txt` strictly
- Rate limit: 1 request/5 seconds
- User agent identification
- Cache aggressively (7-day TTL)
- Fallback gracefully if blocked
- Parse HTML carefully (structure may change)

**Ethical Scraping:**
- Check `robots.txt` before any request
- Implement exponential backoff
- Handle 429/503 gracefully
- Never overwhelm server
- Cache to minimize requests

---

### 5. PostgreSQL Caching Layer (Commit #30)

**File:** `src/services/research/cache.py`

**Schema:**
```sql
CREATE TABLE research_cache (
    id SERIAL PRIMARY KEY,
    source VARCHAR(50) NOT NULL,
    query VARCHAR(255) NOT NULL,
    response JSONB NOT NULL,
    expires_at TIMESTAMP NOT NULL,
    created_at TIMESTAMP DEFAULT NOW(),
    UNIQUE(source, query)
);

CREATE INDEX idx_cache_expiry ON research_cache(expires_at);
CREATE INDEX idx_cache_source_query ON research_cache(source, query);
```

**Requirements:**
- Check cache before API/scraping
- Return cached if not expired
- Store with configurable TTL (default 24h)
- Clean expired entries automatically
- Handle JSON serialization

**Cache Keys:**
```
wikipedia:{show_title_normalized}
tmdb:{show_title}
imdb:{imdb_id}
```

---

### 6. Research Orchestrator (Commit #31)

**File:** `src/services/research/orchestrator.py`

**Purpose:** Unified interface to all research sources

**Features:**
```python
class ResearchOrchestrator:
    async def research_show(
        self, 
        show_title: str,
        sources: List[str] = ["wikipedia", "tmdb", "imdb"]
    ) -> ShowResearchData:
        """
        Research show from all sources and combine results.
        
        - Runs scrapers in parallel
        - Combines data intelligently
        - Handles partial failures gracefully
        - Returns unified ShowResearchData
        """
```

**Requirements:**
- Parallel execution with `asyncio.gather`
- Graceful degradation (some sources can fail)
- Data merging logic (prefer TMDB for metadata, Wikipedia for content)
- Logging for audit trail
- Performance metrics

---

### 7. Unit Tests (Commit #32)

**File:** `tests/unit/test_research_scrapers.py`

**Coverage Required:**
- Wikipedia scraper (mocked responses)
- TMDB scraper (mocked API)
- IMDB scraper (mocked HTML)
- Cache layer (test database)
- Research orchestrator (mocked scrapers)

**Test Cases:**
```python
- test_wikipedia_scraper_success()
- test_wikipedia_page_not_found()
- test_tmdb_api_success()
- test_tmdb_rate_limit_handling()
- test_imdb_scraper_respects_robots_txt()
- test_cache_hit_returns_cached_data()
- test_cache_miss_triggers_scrape()
- test_orchestrator_combines_sources()
- test_orchestrator_handles_partial_failure()
```

**Requirements:**
- Use `pytest-asyncio` for async tests
- Mock external APIs with `responses` or `aioresponses`
- Test happy path and error cases
- Verify rate limiting
- Check cache behavior

---

### 8. Integration Tests + Docs (Commit #33)

**File:** `tests/integration/test_research_pipeline.py`

**Test Scenarios:**
```python
- test_full_research_pipeline_i_love_lucy()
- test_research_with_cache()
- test_parallel_source_execution()
- test_graceful_degradation()
```

**Documentation:**
- API usage examples
- Configuration guide
- Rate limiting explanation
- Troubleshooting common issues

---

## 🔐 CONFIGURATION

### Environment Variables
```bash
# TMDB API
TMDB_API_KEY=your_key_here

# Database (from existing setup)
POSTGRES_HOST=localhost
POSTGRES_PORT=5432
POSTGRES_DB=doppelganger
POSTGRES_USER=doppelganger_user
POSTGRES_PASSWORD=xxx

# Redis (for rate limiting)
REDIS_URL=redis://localhost:6379/0

# Scraping Configuration
WIKIPEDIA_RATE_LIMIT=1.0  # seconds between requests
TMDB_RATE_LIMIT=0.25      # 40 req/10sec = 0.25s between
IMDB_RATE_LIMIT=5.0       # seconds between requests
```

---

## ✅ SUCCESS CRITERIA

### Functional
- [ ] All 3 scrapers successfully fetch real data
- [ ] Cache layer stores and retrieves correctly
- [ ] Orchestrator combines sources intelligently
- [ ] Rate limiting prevents API abuse
- [ ] Graceful degradation on source failures

### Quality
- [ ] Test coverage ≥80%
- [ ] All type hints present
- [ ] Google-style docstrings complete
- [ ] No hardcoded secrets
- [ ] Comprehensive error handling

### Performance
- [ ] Research completes in <10 seconds
- [ ] Cache hits return in <100ms
- [ ] No rate limit violations
- [ ] Memory usage controlled

---

## 🚀 EXECUTION PLAN

**Session Flow:**
1. Create data models (Commit #26)
2. Implement Wikipedia scraper (Commit #27)
3. Implement TMDB integration (Commit #28)
4. Implement IMDB scraper (Commit #29)
5. Add PostgreSQL caching (Commit #30)
6. Create orchestrator (Commit #31)
7. Write unit tests (Commit #32)
8. Integration tests + docs (Commit #33)

**Estimated Time:** 4-6 hours focused work

---

## 📝 NEXT PHASE

After Part 1 completion, we move to:

**Phase 2 Part 2: AI Creative Engine**
- Claude Sonnet 4.5 integration
- GPT-4 fallback system
- Character analyzer
- Narrative analyzer
- Transformation engine

---

**Ready to begin implementation?** 🚀

This directive will be committed as the implementation guide.

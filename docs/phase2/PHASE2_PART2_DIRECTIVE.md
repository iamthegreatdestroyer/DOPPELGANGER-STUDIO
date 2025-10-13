# 🎯 PHASE 2 PART 2: AI CREATIVE ENGINE
## Implementation Directive

**Phase:** 2 Part 2 of 12  
**Status:** 🚀 ACTIVE  
**Start Date:** October 13, 2025  
**Target Commits:** 34-41 (8 commits)  
**Estimated Duration:** 2-3 hours

---

## 🎯 MISSION OBJECTIVES

Build the **AI Creative Engine** - the intelligent core that analyzes TV shows and generates transformation rules for parody creation.

### Core Components
1. ✅ Claude Sonnet 4.5 API client (primary AI)
2. ✅ GPT-4 fallback client (backup)
3. ✅ Character trait analyzer
4. ✅ Narrative structure analyzer
5. ✅ Transformation rule engine
6. ✅ Redis rate limiting
7. ✅ Comprehensive tests
8. ✅ Configuration management

---

## 📋 COMMIT PLAN

### Commit #34: AI Client Base Class [REF:AI-201]
**File:** `src/services/ai/base_client.py`
- Abstract base class for AI clients
- Common interface for Claude and GPT-4
- Token tracking
- Cost calculation
- Retry logic with exponential backoff
- Rate limiting interface

### Commit #35: Claude Sonnet 4.5 Client [REF:AI-202]
**File:** `src/services/ai/claude_client.py`
- Anthropic API integration
- Model: claude-sonnet-4-20250514
- Streaming support
- Token usage tracking
- Cost: $3/MTok input, $15/MTok output
- Retry on errors (3 attempts)
- Timeout: 60 seconds

### Commit #36: GPT-4 Fallback Client [REF:AI-203]
**File:** `src/services/ai/gpt_client.py`
- OpenAI API integration
- Model: gpt-4-turbo-preview
- Same interface as Claude
- Activated on Claude failure
- Token tracking
- Cost calculation

### Commit #37: Character Analyzer [REF:AI-204]
**File:** `src/services/ai/character_analyzer.py`
- Extracts personality traits (5-10 per character)
- Speech pattern analysis
- Relationship mapping
- Comedic elements identification
- Modern transformation opportunities
- Uses Claude with specialized prompts

### Commit #38: Narrative Analyzer [REF:AI-205]
**File:** `src/services/ai/narrative_analyzer.py`
- Story structure identification
- Plot device recognition
- Pacing analysis
- Opening/closing conventions
- Genre patterns
- Uses Claude with narrative theory

### Commit #39: Transformation Engine [REF:AI-206]
**File:** `src/services/ai/transformation_engine.py`
- Classic → Modern setting mappings
- Character motivation updates
- Contemporary conflict sources
- Technology integration points
- Cultural reference updates
- Rule generation for parody

### Commit #40: Redis Rate Limiting [REF:AI-207]
**File:** `src/services/ai/rate_limiter.py`
- Redis-based rate limiting
- Per-user/per-model limits
- Sliding window algorithm
- Cost tracking
- Usage statistics

### Commit #41: AI Tests & Module Exports [REF:TEST-202]
**Files:** 
- `tests/unit/test_ai_clients.py`
- `tests/unit/test_analyzers.py`
- `src/services/ai/__init__.py`
- Mock AI responses
- Token tracking tests
- Error handling tests
- Integration tests

---

## 🏗️ TECHNICAL ARCHITECTURE

### AI Client Hierarchy
```
BaseAIClient (Abstract)
├── ClaudeClient (Primary)
│   ├── Anthropic API
│   ├── Streaming support
│   └── Token tracking
└── GPTClient (Fallback)
    ├── OpenAI API
    └── Same interface

AIClientFactory
├── get_client(preferred='claude')
├── auto_fallback()
└── cost_tracking()
```

### Analysis Pipeline
```
Research Data (Wikipedia, TMDB)
    ↓
Character Analyzer
    → Traits, speech patterns, relationships
    ↓
Narrative Analyzer
    → Structure, pacing, devices
    ↓
Transformation Engine
    → Modern mappings, parody rules
    ↓
MongoDB (Analysis Storage)
```

---

## 🔧 COMPONENT SPECIFICATIONS

### 1. Base AI Client [REF:AI-201]

```python
class BaseAIClient(ABC):
    """Abstract base class for AI clients."""
    
    @abstractmethod
    async def complete(
        self,
        prompt: str,
        system: Optional[str] = None,
        max_tokens: int = 4096,
        temperature: float = 0.7
    ) -> AIResponse:
        """Generate completion."""
        pass
    
    @abstractmethod
    async def complete_json(
        self,
        prompt: str,
        schema: Dict
    ) -> Dict:
        """Generate structured JSON response."""
        pass
    
    def calculate_cost(
        self,
        input_tokens: int,
        output_tokens: int
    ) -> float:
        """Calculate API cost."""
        pass
```

### 2. Claude Client [REF:AI-202]

```python
class ClaudeClient(BaseAIClient):
    """Claude Sonnet 4.5 client."""
    
    MODEL = "claude-sonnet-4-20250514"
    INPUT_COST_PER_MTOK = 3.00   # $3 per million tokens
    OUTPUT_COST_PER_MTOK = 15.00  # $15 per million tokens
    
    async def complete(self, prompt: str, **kwargs) -> AIResponse:
        """Generate completion with retry logic."""
        
        for attempt in range(3):
            try:
                response = await self._make_request(prompt, **kwargs)
                return self._parse_response(response)
                
            except anthropic.RateLimitError:
                await self._exponential_backoff(attempt)
                
            except anthropic.APIError as e:
                if attempt == 2:
                    raise
                await asyncio.sleep(2 ** attempt)
    
    async def _make_request(self, prompt: str, **kwargs):
        """Make API request to Anthropic."""
        return await self.client.messages.create(
            model=self.MODEL,
            max_tokens=kwargs.get('max_tokens', 4096),
            temperature=kwargs.get('temperature', 0.7),
            system=kwargs.get('system'),
            messages=[{"role": "user", "content": prompt}]
        )
```

### 3. Character Analyzer [REF:AI-204]

```python
class CharacterAnalyzer:
    """Analyze characters using AI."""
    
    SYSTEM_PROMPT = """You are an expert TV character analyst.
    
    Analyze the character and extract:
    1. Core personality traits (5-10 traits)
    2. Speech patterns and catchphrases
    3. Key relationships
    4. Character arc
    5. Comedic elements
    6. Modern transformation opportunities
    
    Return structured JSON."""
    
    async def analyze_character(
        self,
        character_data: CharacterData,
        show_context: WikipediaData
    ) -> CharacterAnalysis:
        """Analyze a single character."""
        
        prompt = self._build_prompt(character_data, show_context)
        
        response = await self.ai_client.complete_json(
            prompt=prompt,
            schema=CHARACTER_ANALYSIS_SCHEMA
        )
        
        return CharacterAnalysis(**response)
```

### 4. Transformation Engine [REF:AI-206]

```python
class TransformationEngine:
    """Generate transformation rules for parody."""
    
    async def generate_transformations(
        self,
        show_analysis: ShowAnalysis
    ) -> TransformationRules:
        """Generate classic → modern mappings."""
        
        prompt = f"""
        Analyze this classic TV show and create modern parody transformations:
        
        Original Setting: {show_analysis.setting}
        Characters: {show_analysis.characters}
        Themes: {show_analysis.themes}
        
        Generate:
        1. Modern setting equivalent (e.g., 1950s housewife → 2025 influencer)
        2. Updated character motivations
        3. Contemporary conflict sources
        4. Technology integration points
        5. Cultural reference updates
        
        Output structured JSON.
        """
        
        response = await self.ai_client.complete_json(
            prompt=prompt,
            schema=TRANSFORMATION_SCHEMA
        )
        
        return TransformationRules(**response)
```

### 5. Redis Rate Limiter [REF:AI-207]

```python
class RedisRateLimiter:
    """Rate limiting for AI API calls."""
    
    LIMITS = {
        'claude': {
            'requests_per_minute': 50,
            'tokens_per_minute': 100000,
            'cost_per_hour': 10.00  # $10/hour limit
        },
        'gpt4': {
            'requests_per_minute': 60,
            'tokens_per_minute': 90000,
            'cost_per_hour': 20.00
        }
    }
    
    async def check_limit(
        self,
        user_id: str,
        model: str,
        estimated_tokens: int
    ) -> bool:
        """Check if request is within limits."""
        
        # Check request limit
        request_key = f"ratelimit:{model}:{user_id}:requests"
        current_requests = await self.redis.zcard(request_key)
        
        if current_requests >= self.LIMITS[model]['requests_per_minute']:
            return False
        
        # Check token limit
        token_key = f"ratelimit:{model}:{user_id}:tokens"
        current_tokens = await self._get_token_usage(token_key)
        
        if current_tokens + estimated_tokens > self.LIMITS[model]['tokens_per_minute']:
            return False
        
        return True
```

---

## 🧪 TESTING STRATEGY

### Mock AI Responses
```python
# tests/fixtures/ai_responses.json
{
    "character_analysis": {
        "traits": ["ambitious", "comedic", "naive", "determined"],
        "speech_patterns": ["frequent malapropisms", "exaggerated reactions"],
        "relationships": {
            "husband": "loving but exasperated",
            "friend": "partner in schemes"
        }
    }
}
```

### Test Coverage Requirements
- Unit tests for all AI clients
- Mock all API calls
- Test retry logic
- Test rate limiting
- Test cost calculation
- Integration tests for analyzers
- **Target: 85%+ coverage**

---

## 🔐 SECURITY & CONFIGURATION

### Environment Variables
```bash
# AI API Keys
ANTHROPIC_API_KEY=sk-ant-api03-...
OPENAI_API_KEY=sk-...

# Rate Limiting
AI_MAX_REQUESTS_PER_MIN=50
AI_MAX_TOKENS_PER_MIN=100000
AI_MAX_COST_PER_HOUR=10.00

# Model Selection
AI_PRIMARY_MODEL=claude
AI_FALLBACK_ENABLED=true

# Redis
REDIS_URL=redis://localhost:6379/0
```

### Cost Tracking
```python
# Track all API usage
await usage_tracker.record(
    model='claude',
    input_tokens=1500,
    output_tokens=800,
    cost=0.0165,  # $0.0165
    user_id='system',
    task='character_analysis'
)
```

---

## 📊 SUCCESS CRITERIA

- ✅ Claude client makes successful API calls
- ✅ GPT-4 fallback activates on Claude failure
- ✅ Character analyzer extracts traits accurately
- ✅ Narrative analyzer identifies patterns
- ✅ Transformation engine generates valid rules
- ✅ Rate limiting prevents overuse
- ✅ Cost tracking accurate
- ✅ 85%+ test coverage
- ✅ All secrets in environment variables
- ✅ Comprehensive documentation

---

## 🎯 PERFORMANCE TARGETS

| Metric | Target |
|--------|--------|
| Character Analysis | <10 seconds |
| Narrative Analysis | <15 seconds |
| Transformation Generation | <20 seconds |
| API Retry Success Rate | >95% |
| Fallback Activation | <2 seconds |
| Cost per Show Analysis | <$0.50 |

---

## 🚀 IMPLEMENTATION ORDER

1. **Base Client** → Common interface
2. **Claude Client** → Primary AI
3. **GPT-4 Client** → Fallback
4. **Character Analyzer** → First analyzer
5. **Narrative Analyzer** → Second analyzer
6. **Transformation Engine** → Rule generation
7. **Rate Limiter** → Usage control
8. **Tests & Exports** → Validation

---

**Ready to implement Commit #34!** 🚀

**Phase 2 Part 2: INITIATED**  
**Target: 8 commits in 2-3 hours**  
**Let's build the AI Creative Engine!** ✨

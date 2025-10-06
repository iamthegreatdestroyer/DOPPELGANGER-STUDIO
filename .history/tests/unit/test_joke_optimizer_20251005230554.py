"""
Copyright (c) 2025 DOPPELGANGER STUDIO. All Rights Reserved.

Unit tests for JokeOptimizer component.

Tests comedy analysis, joke structure validation, alternative punchline
generation, callback detection, and timing analysis.
"""

import json
import pytest
from unittest.mock import AsyncMock, Mock, patch

from src.services.creative.joke_optimizer import JokeOptimizer
from src.services.creative.joke_models import (
    JokeStructure,
    JokeType,
    JokeTiming,
    AlternativePunchline,
    CallbackOpportunity,
    ComedyTimingAnalysis,
    OptimizedScriptComedy,
)
from src.services.creative.character_voice_profiles import (
    CharacterVoiceProfile,
    DialogueLine,
    SceneDialogue,
)


class TestJokeOptimizer:
    """Test suite for JokeOptimizer class."""
    
    def test_initialization(self, joke_optimizer, mock_claude_client, mock_gpt_client):
        """Test JokeOptimizer initialization."""
        assert joke_optimizer.claude_client == mock_claude_client
        assert joke_optimizer.openai_client == mock_gpt_client
        assert joke_optimizer.db_manager is None
    
    @pytest.mark.asyncio
    async def test_optimize_script_comedy_success(
        self, joke_optimizer, mock_claude_client
    ):
        """Test successful script comedy optimization."""
        # Mock AI response for joke analysis
        mock_claude_client.generate.return_value = json.dumps({
            "joke_type": "situational",
            "setup": "Lucy tries to sneak onto the spaceship",
            "misdirection": "Disguises herself as cargo",
            "punchline": "Gets loaded into the airlock",
            "effectiveness_score": 0.85,
            "improvement_suggestions": [],
            "callback_potential": True
        })
        
        # Create sample data
        scene_dialogue = SceneDialogue(
            dialogue_lines=[
                DialogueLine(
                    character="Lucy",
                    line="I'll just hide in this crate!",
                    emotion="excited",
                    delivery_note="whispered",
                    is_comedic_beat=True
                )
            ],
            runtime_estimate=180.0,
            confidence_score=0.9
        )
        
        comedic_beats = [
            {
                "type": "situational",
                "setup": "Lucy tries to sneak onto the spaceship",
                "payoff": "Gets loaded into the airlock",
                "timing": 45.0,
                "characters": ["Lucy", "Ricky"]
            }
        ]
        
        voice_profiles = {
            "Lucy": CharacterVoiceProfile(
                character_name="Lucy",
                vocabulary_level="simple",
                sentence_structure="short exclamations",
                verbal_tics=["Oh!", "Ricky!"],
                catchphrases=["Oh, Ricky!"],
                emotional_range=["excited", "scheming", "defensive"],
                relationship_dynamics={"Ricky": "loving but devious"}
            )
        }
        
        result = await joke_optimizer.optimize_script_comedy(
            scene_dialogues=[scene_dialogue],
            comedic_beats=comedic_beats,
            voice_profiles=voice_profiles,
            script_id="test_script_001"
        )
        
        assert isinstance(result, OptimizedScriptComedy)
        assert result.script_id == "test_script_001"
        assert len(result.analyzed_jokes) == 1
        assert result.analyzed_jokes[0].effectiveness_score == 0.85
        assert result.overall_effectiveness > 0
        assert result.confidence_score > 0
    
    @pytest.mark.asyncio
    async def test_optimize_script_comedy_with_failure(
        self, joke_optimizer, mock_claude_client, mock_gpt_client
    ):
        """Test optimization handles complete AI failure gracefully."""
        # Make both AI clients fail
        mock_claude_client.generate.side_effect = Exception("Claude API error")
        mock_gpt_client.generate.side_effect = Exception("GPT API error")
        
        result = await joke_optimizer.optimize_script_comedy(
            scene_dialogues=[],
            comedic_beats=[],
            voice_profiles={},
            script_id="test_fail"
        )
        
        assert isinstance(result, OptimizedScriptComedy)
        assert result.script_id == "test_fail"
        assert len(result.analyzed_jokes) == 0
        assert result.overall_effectiveness == 0.0
        assert result.confidence_score == 0.0
        assert "failed" in result.optimization_summary.lower()
    
    @pytest.mark.asyncio
    async def test_analyze_joke_structure_with_claude(
        self, joke_optimizer, mock_claude_client
    ):
        """Test joke analysis using Claude."""
        mock_claude_client.generate.return_value = json.dumps({
            "joke_type": "wordplay",
            "setup": "Why did the astronaut break up?",
            "misdirection": None,
            "punchline": "She needed space!",
            "effectiveness_score": 0.75,
            "improvement_suggestions": ["Add more context"],
            "callback_potential": False
        })
        
        comedic_beat = {
            "type": "wordplay",
            "setup": "Why did the astronaut break up?",
            "payoff": "She needed space!",
            "timing": 30.0,
            "characters": ["Lucy"]
        }
        
        result = await joke_optimizer._analyze_joke_structure(
            comedic_beat, [], 0
        )
        
        assert isinstance(result, JokeStructure)
        assert result.joke_id == "joke_000"
        assert result.joke_type == JokeType.WORDPLAY
        assert result.setup == "Why did the astronaut break up?"
        assert result.punchline == "She needed space!"
        assert result.effectiveness_score == 0.75
        assert len(result.improvement_suggestions) == 1
        assert result.callback_potential is False
    
    @pytest.mark.asyncio
    async def test_analyze_joke_structure_with_gpt_fallback(
        self, joke_optimizer, mock_claude_client, mock_gpt_client
    ):
        """Test joke analysis falls back to GPT-4 when Claude fails."""
        mock_claude_client.generate.side_effect = Exception("Claude error")
        mock_gpt_client.generate.return_value = json.dumps({
            "joke_type": "physical",
            "setup": "Lucy climbs the space ladder",
            "misdirection": None,
            "punchline": "Ladder floats away in zero-g",
            "effectiveness_score": 0.90,
            "improvement_suggestions": [],
            "callback_potential": True
        })
        
        comedic_beat = {
            "type": "physical",
            "setup": "Lucy climbs the space ladder",
            "payoff": "Ladder floats away",
            "timing": 60.0,
            "characters": ["Lucy"]
        }
        
        result = await joke_optimizer._analyze_joke_structure(
            comedic_beat, [], 1
        )
        
        assert result.joke_type == JokeType.PHYSICAL
        assert result.effectiveness_score == 0.90
        mock_gpt_client.generate.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_analyze_joke_structure_with_complete_fallback(
        self, joke_optimizer, mock_claude_client, mock_gpt_client
    ):
        """Test joke analysis uses basic structure when both AI fail."""
        mock_claude_client.generate.side_effect = Exception("Claude error")
        mock_gpt_client.generate.side_effect = Exception("GPT error")
        
        comedic_beat = {
            "type": "situational",
            "setup": "Test setup",
            "payoff": "Test payoff",
            "timing": 45.0,
            "characters": ["Lucy", "Ricky"]
        }
        
        result = await joke_optimizer._analyze_joke_structure(
            comedic_beat, [], 2
        )
        
        assert isinstance(result, JokeStructure)
        assert result.joke_id == "joke_002"
        assert result.joke_type == JokeType.SITUATIONAL
        assert result.effectiveness_score == 0.5
        assert "AI analysis unavailable" in result.improvement_suggestions
    
    @pytest.mark.asyncio
    async def test_generate_alternative_punchlines_success(
        self, joke_optimizer, mock_claude_client
    ):
        """Test generating alternative punchlines."""
        mock_claude_client.generate.return_value = json.dumps({
            "alternatives": [
                {
                    "punchline": "She needed more space!",
                    "reasoning": "Emphasizes the pun",
                    "estimated_effectiveness": 0.80,
                    "maintains_character": True
                },
                {
                    "punchline": "The relationship had no atmosphere!",
                    "reasoning": "Double space pun",
                    "estimated_effectiveness": 0.85,
                    "maintains_character": True
                }
            ]
        })
        
        joke = JokeStructure(
            joke_id="joke_001",
            joke_type=JokeType.WORDPLAY,
            setup="Why did the astronaut break up?",
            punchline="She needed space!",
            timing_position=30.0,
            characters_involved=["Lucy"],
            effectiveness_score=0.65
        )
        
        voice_profiles = {
            "Lucy": CharacterVoiceProfile(
                character_name="Lucy",
                vocabulary_level="simple",
                sentence_structure="short",
                verbal_tics=["Oh!"],
                catchphrases=["Ricky!"],
                emotional_range=["excited"],
                relationship_dynamics={}
            )
        }
        
        result = await joke_optimizer._generate_alternative_punchlines(
            joke, voice_profiles
        )
        
        assert len(result) == 2
        assert all(isinstance(alt, AlternativePunchline) for alt in result)
        assert result[0].original_joke_id == "joke_001"
        assert result[0].estimated_effectiveness == 0.80
        assert result[1].estimated_effectiveness == 0.85
        assert all(alt.maintains_character for alt in result)
    
    @pytest.mark.asyncio
    async def test_generate_alternative_punchlines_failure(
        self, joke_optimizer, mock_claude_client
    ):
        """Test alternative generation handles AI failure."""
        mock_claude_client.generate.side_effect = Exception("API error")
        
        joke = JokeStructure(
            joke_id="joke_002",
            joke_type=JokeType.SITUATIONAL,
            setup="Test",
            punchline="Test",
            timing_position=0.0,
            characters_involved=[],
            effectiveness_score=0.5
        )
        
        result = await joke_optimizer._generate_alternative_punchlines(
            joke, {}
        )
        
        assert result == []
    
    def test_detect_callback_opportunities_with_matches(self, joke_optimizer):
        """Test callback detection finds opportunities."""
        analyzed_jokes = [
            JokeStructure(
                joke_id="joke_001",
                joke_type=JokeType.WORDPLAY,
                setup="Setup 1",
                punchline="Space pun!",
                timing_position=30.0,
                characters_involved=["Lucy"],
                effectiveness_score=0.80,
                callback_potential=True
            ),
            JokeStructure(
                joke_id="joke_002",
                joke_type=JokeType.SITUATIONAL,
                setup="Setup 2",
                punchline="Another joke",
                timing_position=200.0,
                characters_involved=["Ricky"],
                effectiveness_score=0.70,
                callback_potential=False
            )
        ]
        
        scene_dialogues = [
            SceneDialogue(
                dialogue_lines=[
                    DialogueLine("Lucy", "Line 1", "happy", "", False)
                ],
                runtime_estimate=180.0,
                confidence_score=0.9
            ),
            SceneDialogue(
                dialogue_lines=[
                    DialogueLine("Lucy", "Line 2", "excited", "", False),
                    DialogueLine("Ricky", "Line 3", "amused", "", False)
                ],
                runtime_estimate=180.0,
                confidence_score=0.9
            )
        ]
        
        result = joke_optimizer._detect_callback_opportunities(
            analyzed_jokes, scene_dialogues
        )
        
        assert isinstance(result, list)
        assert len(result) <= 5  # Should limit to top 5
        if len(result) > 0:
            assert all(isinstance(opp, CallbackOpportunity) for opp in result)
            assert result[0].source_joke_id == "joke_001"
    
    def test_detect_callback_opportunities_empty(self, joke_optimizer):
        """Test callback detection with no opportunities."""
        analyzed_jokes = [
            JokeStructure(
                joke_id="joke_001",
                joke_type=JokeType.WORDPLAY,
                setup="Setup",
                punchline="Punchline",
                timing_position=30.0,
                characters_involved=["Lucy"],
                effectiveness_score=0.50,  # Too low
                callback_potential=True
            )
        ]
        
        result = joke_optimizer._detect_callback_opportunities(
            analyzed_jokes, []
        )
        
        assert result == []
    
    def test_analyze_comedy_timing_well_spaced(self, joke_optimizer):
        """Test timing analysis with well-spaced jokes."""
        analyzed_jokes = [
            JokeStructure(
                joke_id=f"joke_{i:03d}",
                joke_type=JokeType.SITUATIONAL,
                setup="Setup",
                punchline="Punchline",
                timing_position=i * 45.0,  # Every 45 seconds
                characters_involved=["Lucy"],
                effectiveness_score=0.75
            )
            for i in range(5)
        ]
        
        result = joke_optimizer._analyze_comedy_timing(analyzed_jokes, [])
        
        assert isinstance(result, ComedyTimingAnalysis)
        assert result.total_jokes == 5
        assert result.average_spacing == 45.0
        assert result.timing_category == JokeTiming.WELL_SPACED
        assert len(result.clusters) == 0
        assert len(result.dead_zones) == 0
        assert result.pacing_score > 0.9  # Nearly perfect pacing
    
    def test_analyze_comedy_timing_rapid_fire(self, joke_optimizer):
        """Test timing analysis with rapid-fire jokes."""
        analyzed_jokes = [
            JokeStructure(
                joke_id=f"joke_{i:03d}",
                joke_type=JokeType.WORDPLAY,
                setup="Setup",
                punchline="Punchline",
                timing_position=i * 15.0,  # Every 15 seconds
                characters_involved=["Lucy"],
                effectiveness_score=0.70
            )
            for i in range(5)
        ]
        
        result = joke_optimizer._analyze_comedy_timing(analyzed_jokes, [])
        
        assert result.timing_category == JokeTiming.RAPID_FIRE
        assert result.average_spacing == 15.0
        assert len(result.clusters) > 0  # Should detect clusters
    
    def test_analyze_comedy_timing_slow_burn(self, joke_optimizer):
        """Test timing analysis with slow-burn pacing."""
        analyzed_jokes = [
            JokeStructure(
                joke_id=f"joke_{i:03d}",
                joke_type=JokeType.CHARACTER,
                setup="Setup",
                punchline="Punchline",
                timing_position=i * 120.0,  # Every 2 minutes
                characters_involved=["Lucy"],
                effectiveness_score=0.80
            )
            for i in range(5)
        ]
        
        result = joke_optimizer._analyze_comedy_timing(analyzed_jokes, [])
        
        assert result.timing_category == JokeTiming.SLOW_BURN
        assert result.average_spacing == 120.0
        assert len(result.dead_zones) > 0  # Should detect dead zones
    
    def test_analyze_comedy_timing_empty(self, joke_optimizer):
        """Test timing analysis with no jokes."""
        result = joke_optimizer._analyze_comedy_timing([], [])
        
        assert result.total_jokes == 0
        assert result.average_spacing == 0.0
        assert result.timing_category == JokeTiming.WELL_SPACED
    
    def test_calculate_pacing_score_optimal(self, joke_optimizer):
        """Test pacing score calculation with optimal spacing."""
        score = joke_optimizer._calculate_pacing_score(
            average_spacing=45.0,  # Perfect
            num_clusters=0,
            num_dead_zones=0
        )
        
        assert score == 1.0
    
    def test_calculate_pacing_score_with_penalties(self, joke_optimizer):
        """Test pacing score with clusters and dead zones."""
        score = joke_optimizer._calculate_pacing_score(
            average_spacing=50.0,  # Slightly off
            num_clusters=2,  # 0.2 penalty
            num_dead_zones=1  # 0.15 penalty
        )
        
        # Should be: 1.0 - (5/45) - 0.2 - 0.15 ≈ 0.54
        assert 0.5 < score < 0.7
    
    def test_calculate_overall_effectiveness(self, joke_optimizer):
        """Test overall effectiveness calculation."""
        jokes = [
            JokeStructure(
                joke_id=f"joke_{i}",
                joke_type=JokeType.SITUATIONAL,
                setup="Setup",
                punchline="Punchline",
                timing_position=0.0,
                characters_involved=[],
                effectiveness_score=score
            )
            for i, score in enumerate([0.8, 0.7, 0.9, 0.6])
        ]
        
        result = joke_optimizer._calculate_overall_effectiveness(jokes)
        
        assert result == 0.75  # (0.8 + 0.7 + 0.9 + 0.6) / 4
    
    def test_calculate_overall_effectiveness_empty(self, joke_optimizer):
        """Test effectiveness calculation with no jokes."""
        result = joke_optimizer._calculate_overall_effectiveness([])
        assert result == 0.0
    
    def test_generate_optimization_summary(self, joke_optimizer):
        """Test optimization summary generation."""
        analyzed_jokes = [
            JokeStructure(
                joke_id="joke_001",
                joke_type=JokeType.WORDPLAY,
                setup="S",
                punchline="P",
                timing_position=30.0,
                characters_involved=[],
                effectiveness_score=0.85
            ),
            JokeStructure(
                joke_id="joke_002",
                joke_type=JokeType.SITUATIONAL,
                setup="S",
                punchline="P",
                timing_position=75.0,
                characters_involved=[],
                effectiveness_score=0.55
            )
        ]
        
        alternatives = [
            AlternativePunchline(
                original_joke_id="joke_002",
                punchline="Better punchline",
                reasoning="More effective",
                estimated_effectiveness=0.75
            )
        ]
        
        callbacks = [
            CallbackOpportunity(
                source_joke_id="joke_001",
                target_scene="scene_02",
                target_timing=180.0,
                callback_suggestion="Reference the wordplay",
                comedic_payoff="Rewards viewers"
            )
        ]
        
        timing = ComedyTimingAnalysis(
            total_jokes=2,
            average_spacing=45.0,
            timing_category=JokeTiming.WELL_SPACED,
            clusters=["scene_01"],
            dead_zones=[]
        )
        
        result = joke_optimizer._generate_optimization_summary(
            analyzed_jokes, alternatives, callbacks, timing
        )
        
        assert "Analyzed 2 jokes" in result
        assert "Strong jokes: 1" in result
        assert "Weak jokes: 1" in result
        assert "1 alternative" in result
        assert "1 callback" in result
        assert "well_spaced" in result
        assert "45.0s" in result
        assert "WARNING" in result  # Should warn about cluster


class TestJokeStructure:
    """Test suite for JokeStructure dataclass."""
    
    def test_joke_structure_creation(self):
        """Test creating a JokeStructure."""
        joke = JokeStructure(
            joke_id="joke_001",
            joke_type=JokeType.WORDPLAY,
            setup="Why did the chicken cross the road?",
            punchline="To get to the other side!",
            timing_position=30.0,
            characters_involved=["Comedian"],
            effectiveness_score=0.65,
            misdirection="Expected a complex answer",
            improvement_suggestions=["Add more context"],
            callback_potential=False,
            callback_references=[]
        )
        
        assert joke.joke_id == "joke_001"
        assert joke.joke_type == JokeType.WORDPLAY
        assert joke.effectiveness_score == 0.65
        assert len(joke.improvement_suggestions) == 1
    
    def test_joke_structure_to_dict(self):
        """Test JokeStructure serialization."""
        joke = JokeStructure(
            joke_id="joke_002",
            joke_type=JokeType.PHYSICAL,
            setup="Setup",
            punchline="Punchline",
            timing_position=45.0,
            characters_involved=["Lucy", "Ricky"],
            effectiveness_score=0.80
        )
        
        data = joke.to_dict()
        
        assert data["joke_id"] == "joke_002"
        assert data["joke_type"] == "physical"
        assert data["effectiveness_score"] == 0.80
        assert data["characters_involved"] == ["Lucy", "Ricky"]
    
    def test_joke_structure_from_dict(self):
        """Test JokeStructure deserialization."""
        data = {
            "joke_id": "joke_003",
            "joke_type": "situational",
            "setup": "Test setup",
            "misdirection": None,
            "punchline": "Test punchline",
            "timing_position": 60.0,
            "characters_involved": ["Character1"],
            "effectiveness_score": 0.75,
            "improvement_suggestions": ["Suggestion"],
            "callback_potential": True,
            "callback_references": []
        }
        
        joke = JokeStructure.from_dict(data)
        
        assert joke.joke_id == "joke_003"
        assert joke.joke_type == JokeType.SITUATIONAL
        assert joke.effectiveness_score == 0.75
        assert joke.callback_potential is True


class TestAlternativePunchline:
    """Test suite for AlternativePunchline dataclass."""
    
    def test_alternative_punchline_creation(self):
        """Test creating an AlternativePunchline."""
        alt = AlternativePunchline(
            original_joke_id="joke_001",
            punchline="New punchline!",
            reasoning="Better timing",
            estimated_effectiveness=0.85,
            maintains_character=True
        )
        
        assert alt.original_joke_id == "joke_001"
        assert alt.estimated_effectiveness == 0.85
        assert alt.maintains_character is True
    
    def test_alternative_punchline_serialization(self):
        """Test AlternativePunchline to_dict and from_dict."""
        alt = AlternativePunchline(
            original_joke_id="joke_002",
            punchline="Alternative",
            reasoning="Stronger payoff",
            estimated_effectiveness=0.90,
            maintains_character=False
        )
        
        data = alt.to_dict()
        reconstructed = AlternativePunchline.from_dict(data)
        
        assert reconstructed.original_joke_id == alt.original_joke_id
        assert reconstructed.punchline == alt.punchline
        assert reconstructed.maintains_character == alt.maintains_character


class TestCallbackOpportunity:
    """Test suite for CallbackOpportunity dataclass."""
    
    def test_callback_opportunity_creation(self):
        """Test creating a CallbackOpportunity."""
        callback = CallbackOpportunity(
            source_joke_id="joke_001",
            target_scene="scene_03",
            target_timing=200.0,
            callback_suggestion="Reference the space pun",
            comedic_payoff="Rewards attentive viewers",
            risk_level=0.3
        )
        
        assert callback.source_joke_id == "joke_001"
        assert callback.target_scene == "scene_03"
        assert callback.risk_level == 0.3
    
    def test_callback_opportunity_serialization(self):
        """Test CallbackOpportunity serialization."""
        callback = CallbackOpportunity(
            source_joke_id="joke_005",
            target_scene="scene_10",
            target_timing=500.0,
            callback_suggestion="Bring back the running gag",
            comedic_payoff="Creates cohesion"
        )
        
        data = callback.to_dict()
        reconstructed = CallbackOpportunity.from_dict(data)
        
        assert reconstructed.source_joke_id == callback.source_joke_id
        assert reconstructed.comedic_payoff == callback.comedic_payoff


class TestComedyTimingAnalysis:
    """Test suite for ComedyTimingAnalysis dataclass."""
    
    def test_timing_analysis_creation(self):
        """Test creating a ComedyTimingAnalysis."""
        analysis = ComedyTimingAnalysis(
            total_jokes=10,
            average_spacing=50.0,
            timing_category=JokeTiming.WELL_SPACED,
            clusters=["scene_02", "scene_05"],
            dead_zones=["scene_08"],
            optimal_spacing=45.0,
            pacing_score=0.75
        )
        
        assert analysis.total_jokes == 10
        assert analysis.timing_category == JokeTiming.WELL_SPACED
        assert len(analysis.clusters) == 2
        assert len(analysis.dead_zones) == 1
    
    def test_timing_analysis_serialization(self):
        """Test ComedyTimingAnalysis serialization."""
        analysis = ComedyTimingAnalysis(
            total_jokes=5,
            average_spacing=60.0,
            timing_category=JokeTiming.SLOW_BURN
        )
        
        data = analysis.to_dict()
        reconstructed = ComedyTimingAnalysis.from_dict(data)
        
        assert reconstructed.total_jokes == analysis.total_jokes
        assert reconstructed.timing_category == analysis.timing_category


class TestOptimizedScriptComedy:
    """Test suite for OptimizedScriptComedy dataclass."""
    
    def test_optimized_script_comedy_creation(self):
        """Test creating an OptimizedScriptComedy."""
        jokes = [
            JokeStructure(
                joke_id="joke_001",
                joke_type=JokeType.WORDPLAY,
                setup="S",
                punchline="P",
                timing_position=30.0,
                characters_involved=[],
                effectiveness_score=0.85
            )
        ]
        
        result = OptimizedScriptComedy(
            script_id="script_001",
            analyzed_jokes=jokes,
            alternative_punchlines=[],
            callback_opportunities=[],
            timing_analysis=ComedyTimingAnalysis(
                total_jokes=1,
                average_spacing=0.0,
                timing_category=JokeTiming.WELL_SPACED
            ),
            overall_effectiveness=0.85,
            optimization_summary="All jokes are strong",
            confidence_score=0.90
        )
        
        assert result.script_id == "script_001"
        assert len(result.analyzed_jokes) == 1
        assert result.overall_effectiveness == 0.85
    
    def test_get_weak_jokes(self):
        """Test filtering weak jokes."""
        jokes = [
            JokeStructure(
                joke_id=f"joke_{i}",
                joke_type=JokeType.SITUATIONAL,
                setup="S",
                punchline="P",
                timing_position=0.0,
                characters_involved=[],
                effectiveness_score=score
            )
            for i, score in enumerate([0.9, 0.5, 0.7, 0.4])
        ]
        
        result = OptimizedScriptComedy(
            script_id="test",
            analyzed_jokes=jokes,
            alternative_punchlines=[],
            callback_opportunities=[],
            timing_analysis=ComedyTimingAnalysis(
                total_jokes=4,
                average_spacing=45.0,
                timing_category=JokeTiming.WELL_SPACED
            ),
            overall_effectiveness=0.625,
            optimization_summary="Summary",
            confidence_score=0.85
        )
        
        weak = result.get_weak_jokes(threshold=0.6)
        
        assert len(weak) == 2  # 0.5 and 0.4
        assert all(j.effectiveness_score < 0.6 for j in weak)
    
    def test_get_strong_jokes(self):
        """Test filtering strong jokes."""
        jokes = [
            JokeStructure(
                joke_id=f"joke_{i}",
                joke_type=JokeType.PHYSICAL,
                setup="S",
                punchline="P",
                timing_position=0.0,
                characters_involved=[],
                effectiveness_score=score
            )
            for i, score in enumerate([0.9, 0.85, 0.7, 0.95])
        ]
        
        result = OptimizedScriptComedy(
            script_id="test",
            analyzed_jokes=jokes,
            alternative_punchlines=[],
            callback_opportunities=[],
            timing_analysis=ComedyTimingAnalysis(
                total_jokes=4,
                average_spacing=45.0,
                timing_category=JokeTiming.WELL_SPACED
            ),
            overall_effectiveness=0.85,
            optimization_summary="Summary",
            confidence_score=0.90
        )
        
        strong = result.get_strong_jokes(threshold=0.8)
        
        assert len(strong) == 3  # 0.9, 0.85, 0.95
        assert all(j.effectiveness_score >= 0.8 for j in strong)
    
    def test_get_jokes_by_type(self):
        """Test filtering jokes by type."""
        jokes = [
            JokeStructure(
                joke_id="joke_001",
                joke_type=JokeType.WORDPLAY,
                setup="S",
                punchline="P",
                timing_position=0.0,
                characters_involved=[],
                effectiveness_score=0.8
            ),
            JokeStructure(
                joke_id="joke_002",
                joke_type=JokeType.PHYSICAL,
                setup="S",
                punchline="P",
                timing_position=0.0,
                characters_involved=[],
                effectiveness_score=0.7
            ),
            JokeStructure(
                joke_id="joke_003",
                joke_type=JokeType.WORDPLAY,
                setup="S",
                punchline="P",
                timing_position=0.0,
                characters_involved=[],
                effectiveness_score=0.9
            )
        ]
        
        result = OptimizedScriptComedy(
            script_id="test",
            analyzed_jokes=jokes,
            alternative_punchlines=[],
            callback_opportunities=[],
            timing_analysis=ComedyTimingAnalysis(
                total_jokes=3,
                average_spacing=45.0,
                timing_category=JokeTiming.WELL_SPACED
            ),
            overall_effectiveness=0.80,
            optimization_summary="Summary",
            confidence_score=0.85
        )
        
        wordplay_jokes = result.get_jokes_by_type(JokeType.WORDPLAY)
        
        assert len(wordplay_jokes) == 2
        assert all(j.joke_type == JokeType.WORDPLAY for j in wordplay_jokes)
    
    def test_optimized_script_comedy_serialization(self):
        """Test OptimizedScriptComedy full serialization."""
        result = OptimizedScriptComedy(
            script_id="test_script",
            analyzed_jokes=[
                JokeStructure(
                    joke_id="joke_001",
                    joke_type=JokeType.CALLBACK,
                    setup="S",
                    punchline="P",
                    timing_position=30.0,
                    characters_involved=["Lucy"],
                    effectiveness_score=0.85
                )
            ],
            alternative_punchlines=[
                AlternativePunchline(
                    original_joke_id="joke_001",
                    punchline="Alt",
                    reasoning="Better",
                    estimated_effectiveness=0.90
                )
            ],
            callback_opportunities=[
                CallbackOpportunity(
                    source_joke_id="joke_001",
                    target_scene="scene_02",
                    target_timing=200.0,
                    callback_suggestion="Reference it",
                    comedic_payoff="Good"
                )
            ],
            timing_analysis=ComedyTimingAnalysis(
                total_jokes=1,
                average_spacing=0.0,
                timing_category=JokeTiming.WELL_SPACED
            ),
            overall_effectiveness=0.85,
            optimization_summary="Summary",
            confidence_score=0.90
        )
        
        data = result.to_dict()
        reconstructed = OptimizedScriptComedy.from_dict(data)
        
        assert reconstructed.script_id == result.script_id
        assert len(reconstructed.analyzed_jokes) == len(result.analyzed_jokes)
        assert len(reconstructed.alternative_punchlines) == len(result.alternative_punchlines)
        assert len(reconstructed.callback_opportunities) == len(result.callback_opportunities)
        assert reconstructed.overall_effectiveness == result.overall_effectiveness

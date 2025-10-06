"""Tests for Narrative Analyzer - Phase 3 Creative Intelligence."""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch
import json
from datetime import datetime

from src.services.creative.narrative_analyzer import (
    NarrativeAnalyzer,
    NarrativeAnalysis,
    NarrativePattern,
    EpisodeStructure
)


@pytest.fixture
def mock_claude_client():
    """Mock Claude AI client."""
    client = AsyncMock()
    client.generate = AsyncMock()
    return client


@pytest.fixture
def mock_gpt_client():
    """Mock GPT-4 client."""
    client = AsyncMock()
    client.generate = AsyncMock()
    return client


@pytest.fixture
def mock_database():
    """Mock database manager."""
    db = MagicMock()
    db.mongodb = {
        'ai_analysis': AsyncMock()
    }
    return db


@pytest.fixture
def sample_show_data():
    """Sample show data for testing."""
    return {
        'title': 'I Love Lucy',
        'years': '1951-1957',
        'genre': ['Sitcom', 'Comedy'],
        'premise': 'A wacky redhead schemes to break into show business',
        'setting': '1950s New York City',
        'characters': ['Lucy Ricardo', 'Ricky Ricardo', 'Ethel Mertz', 'Fred Mertz'],
        'runtime': 22
    }


@pytest.fixture
def valid_ai_response():
    """Valid AI response matching NarrativeAnalysisResponse schema."""
    return {
        'show_title': 'I Love Lucy',
        'plot_structure': {
            'structure_type': 'episodic',
            'act_breakdown': {
                'act_1': 'Setup - Lucy gets idea',
                'act_2': 'Conflict - Plan goes wrong',
                'act_3': 'Resolution - Lesson learned'
            },
            'typical_runtime': 22
        },
        'recurring_devices': [
            {
                'device_name': 'Harebrained Scheme',
                'description': 'Lucy concocts elaborate plans to achieve her goals',
                'frequency': 'every episode',
                'examples': [
                    'Lucy tries to sneak into show',
                    'Lucy disguises herself as someone else',
                    'Lucy practices performance secretly'
                ],
                'purpose': 'Drive main plot and create comedic situations'
            },
            {
                'device_name': 'Physical Comedy',
                'description': 'Slapstick humor and visual gags',
                'frequency': 'multiple times per episode',
                'examples': [
                    'Chocolate factory assembly line',
                    'Grape stomping in Italy',
                    'Getting stuck in various situations'
                ],
                'purpose': 'Generate laughs through visual humor'
            }
        ],
        'opening_convention': 'Theme song over stylized heart graphic',
        'closing_convention': 'Resolution scene followed by end credits',
        'b_plot_patterns': [
            'Fred and Ethel have parallel subplot',
            'Ricky deals with entertainment business'
        ],
        'pacing_notes': 'Fast-paced escalation, rapid-fire dialogue, building physical comedy',
        'unique_signatures': [
            'Lucy\'s signature "Waaahhh" cry',
            'Ricky\'s exasperated Spanish exclamations',
            'Breaking the fourth wall occasionally'
        ]
    }


class TestNarrativeAnalyzerBasics:
    """Test basic narrative analyzer functionality."""
    
    @pytest.mark.asyncio
    async def test_successful_analysis(
        self, mock_claude_client, sample_show_data, valid_ai_response
    ):
        """Test successful narrative analysis with valid response."""
        mock_claude_client.generate.return_value = json.dumps(valid_ai_response)
        
        analyzer = NarrativeAnalyzer(claude_client=mock_claude_client)
        result = await analyzer.analyze_narrative(sample_show_data)
        
        assert result is not None
        assert isinstance(result, NarrativeAnalysis)
        assert result.show_title == 'I Love Lucy'
        assert result.structure_type == 'episodic'
        assert len(result.recurring_devices) >= 2
        assert result.opening_convention == 'Theme song over stylized heart graphic'
        assert mock_claude_client.generate.called
    
    @pytest.mark.asyncio
    async def test_invalid_json_handling(
        self, mock_claude_client, sample_show_data
    ):
        """Test handling of invalid JSON from AI."""
        mock_claude_client.generate.return_value = "This is not valid JSON {{"
        
        analyzer = NarrativeAnalyzer(
            claude_client=mock_claude_client,
            gpt_client=None
        )
        result = await analyzer.analyze_narrative(sample_show_data)
        
        # Should retry and eventually fail
        assert result is None
        assert mock_claude_client.generate.call_count == 3  # Max retries
    
    @pytest.mark.asyncio
    async def test_validation_failure_retry(
        self, mock_claude_client, sample_show_data, valid_ai_response
    ):
        """Test retry logic on validation failure."""
        invalid_response = {'show_title': 'Test'}  # Missing required fields
        
        # First two attempts fail, third succeeds
        mock_claude_client.generate.side_effect = [
            json.dumps(invalid_response),
            json.dumps(invalid_response),
            json.dumps(valid_ai_response)
        ]
        
        analyzer = NarrativeAnalyzer(claude_client=mock_claude_client)
        result = await analyzer.analyze_narrative(sample_show_data)
        
        assert result is not None
        assert mock_claude_client.generate.call_count == 3


class TestNarrativeAnalyzerFallback:
    """Test fallback mechanisms."""
    
    @pytest.mark.asyncio
    async def test_claude_to_gpt_fallback(
        self, mock_claude_client, mock_gpt_client, sample_show_data, valid_ai_response
    ):
        """Test fallback from Claude to GPT-4 on failure."""
        # Claude fails all attempts
        mock_claude_client.generate.return_value = "Invalid JSON"
        
        # GPT succeeds
        mock_gpt_client.generate.return_value = json.dumps(valid_ai_response)
        
        analyzer = NarrativeAnalyzer(
            claude_client=mock_claude_client,
            gpt_client=mock_gpt_client
        )
        result = await analyzer.analyze_narrative(sample_show_data)
        
        assert result is not None
        # Claude tries 3 times, then falls back to GPT
        assert mock_claude_client.generate.call_count >= 1  # Claude tried
        assert mock_gpt_client.generate.called  # GPT used as fallback


class TestNarrativeAnalyzerCaching:
    """Test caching functionality."""
    
    @pytest.mark.asyncio
    async def test_cache_hit(
        self, mock_claude_client, mock_database, sample_show_data, valid_ai_response
    ):
        """Test cache retrieval on cache hit."""
        from datetime import datetime, timedelta
        
        # Setup cache hit with proper structure
        cached_data = {
            'show_title': 'I Love Lucy',
            'structure_type': 'episodic',
            'opening_convention': 'Cached opening',
            'closing_convention': 'Cached closing',
            'recurring_devices': [],
            'pacing_notes': 'Cached pacing',
            'unique_signatures': [],
            'episode_structure': None,
            'b_plot_patterns': [],
            'confidence_score': 0.9
        }
        
        # Cache returns document with output_data wrapper
        mock_database.mongodb['ai_analysis'].find_one.return_value = {
            'output_data': cached_data,
            'expires_at': datetime.now() + timedelta(days=1)
        }
        
        analyzer = NarrativeAnalyzer(
            claude_client=mock_claude_client,
            database_manager=mock_database
        )
        result = await analyzer.analyze_narrative(sample_show_data)
        
        assert result is not None
        assert result.opening_convention == 'Cached opening'
        assert not mock_claude_client.generate.called  # Should not call AI
    
    @pytest.mark.asyncio
    async def test_cache_miss_and_save(
        self, mock_claude_client, mock_database, sample_show_data, valid_ai_response
    ):
        """Test cache miss triggers AI call and saves result."""
        # Setup cache miss
        mock_database.mongodb['ai_analysis'].find_one.return_value = None
        mock_claude_client.generate.return_value = json.dumps(valid_ai_response)
        
        analyzer = NarrativeAnalyzer(
            claude_client=mock_claude_client,
            database_manager=mock_database
        )
        result = await analyzer.analyze_narrative(sample_show_data)
        
        assert result is not None
        assert mock_claude_client.generate.called  # AI called
        assert mock_database.mongodb['ai_analysis'].update_one.called  # Cache saved


class TestNarrativeDataStructures:
    """Test narrative analysis data structures."""
    
    def test_narrative_pattern_creation(self):
        """Test NarrativePattern dataclass."""
        pattern = NarrativePattern(
            pattern_name="Test Pattern",
            description="Test description",
            frequency="often",
            examples=["Example 1", "Example 2"],
            purpose="Test purpose"
        )
        
        assert pattern.pattern_name == "Test Pattern"
        assert len(pattern.examples) == 2
    
    def test_episode_structure_creation(self):
        """Test EpisodeStructure dataclass."""
        structure = EpisodeStructure(
            total_runtime=22,
            act_count=3,
            act_lengths=[7, 10, 5],
            commercial_breaks=2,
            opening_length=1.5,
            closing_length=0.5
        )
        
        assert structure.total_runtime == 22
        assert structure.act_count == 3
        assert sum(structure.act_lengths) == 22


class TestNarrativePromptBuilding:
    """Test prompt construction."""
    
    @pytest.mark.asyncio
    async def test_prompt_includes_show_context(
        self, mock_claude_client, sample_show_data
    ):
        """Test that prompt includes all show context."""
        analyzer = NarrativeAnalyzer(claude_client=mock_claude_client)
        
        # Capture the prompt
        captured_prompt = None
        async def capture_generate(prompt, **kwargs):
            nonlocal captured_prompt
            captured_prompt = prompt
            return "{}"
        
        mock_claude_client.generate.side_effect = capture_generate
        
        await analyzer.analyze_narrative(sample_show_data)
        
        assert captured_prompt is not None
        assert 'I Love Lucy' in captured_prompt
        assert '1951-1957' in captured_prompt
        assert 'Sitcom' in captured_prompt


# Run tests with: pytest tests/unit/test_narrative_analyzer.py -v

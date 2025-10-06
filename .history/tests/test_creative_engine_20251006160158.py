"""
Tests for AI Creative Engine components.

Tests Claude client, OpenAI client, AI Orchestrator, and Character Analyzer.

Copyright (c) 2025. All Rights Reserved. Patent Pending.
"""

import pytest
from unittest.mock import Mock, patch, AsyncMock
import json

from src.services.creative.claude_client import ClaudeClient, AIResponse
from src.services.creative.openai_client import OpenAIClient
from src.services.creative.ai_orchestrator import AIOrchestrator
from src.services.creative.character_analyzer import (
    CharacterAnalyzer
)
from src.services.creative.response_validators import CharacterAnalysisResponse


class TestClaudeClient:
    """Test suite for Claude AI client."""
    
    @pytest.fixture
    def mock_anthropic_response(self):
        """Create mock Anthropic API response."""
        response = Mock()
        response.content = [Mock(text="Generated response")]
        response.model = "claude-sonnet-4-20250514"
        response.usage = Mock(input_tokens=100, output_tokens=50)
        response.stop_reason = "end_turn"
        return response
    
    @pytest.mark.asyncio
    async def test_generate_success(self, mock_anthropic_response):
        """Test successful text generation."""
        client = ClaudeClient(api_key="test_key")
        
        with patch.object(
            client,
            '_make_request_with_retry',
            new=AsyncMock(return_value=mock_anthropic_response)
        ):
            response = await client.generate("Test prompt")
            
            assert isinstance(response, AIResponse)
            assert response.content == "Generated response"
            assert response.tokens_used == 150
            assert response.cached is False
    
    @pytest.mark.asyncio
    async def test_generate_json(self, mock_anthropic_response):
        """Test JSON generation."""
        client = ClaudeClient(api_key="test_key", enable_caching=False)
        
        mock_anthropic_response.content[0].text = json.dumps({
            "name": "Lucy",
            "traits": ["ambitious", "scheming"]
        })
        
        with patch.object(
            client,
            '_make_request_with_retry',
            new=AsyncMock(return_value=mock_anthropic_response)
        ):
            result = await client.generate_json("Test prompt")
            
            assert isinstance(result, dict)
            assert result["name"] == "Lucy"
            assert "ambitious" in result["traits"]
    
    @pytest.mark.asyncio
    async def test_caching(self, mock_anthropic_response):
        """Test response caching."""
        client = ClaudeClient(api_key="test_key", enable_caching=True)
        
        # Clear any existing cache
        client.cache_manager.clear()
        
        with patch.object(
            client,
            '_make_request_with_retry',
            new=AsyncMock(return_value=mock_anthropic_response)
        ):
            # First call should miss cache
            response1 = await client.generate("Test prompt cache test", use_cache=True)
            assert response1.cached is False
            
            # Second call should hit cache
            response2 = await client.generate("Test prompt cache test", use_cache=True)
            assert response2.cached is True
            assert response2.content == "Generated response"
    
    def test_usage_stats(self):
        """Test usage statistics tracking."""
        client = ClaudeClient(api_key="test_key")
        client.total_requests = 10
        client.total_tokens_used = 5000
        client.cache_hits = 3
        
        stats = client.get_usage_stats()
        
        assert stats['total_requests'] == 10
        assert stats['total_tokens'] == 5000
        assert stats['cache_hits'] == 3
        assert stats['cache_hit_rate'] == 0.3


class TestOpenAIClient:
    """Test suite for OpenAI GPT-4 client."""
    
    @pytest.mark.asyncio
    async def test_generate_success(self):
        """Test successful generation."""
        client = OpenAIClient(api_key="test_key")
        
        mock_response = Mock()
        mock_response.choices = [Mock(
            message=Mock(content="Generated text"),
            finish_reason="stop"
        )]
        mock_response.usage = Mock(total_tokens=150)
        mock_response.model = "gpt-4-turbo-preview"
        
        with patch.object(
            client.client.chat.completions,
            'create',
            new=AsyncMock(return_value=mock_response)
        ):
            response = await client.generate("Test prompt")
            
            assert response.content == "Generated text"
            assert response.tokens_used == 150


class TestAIOrchestrator:
    """Test suite for AI Orchestrator."""
    
    @pytest.fixture
    def orchestrator_with_both(self):
        """Create orchestrator with both providers."""
        return AIOrchestrator(
            claude_api_key="claude_key",
            openai_api_key="openai_key"
        )
    
    @pytest.mark.asyncio
    async def test_primary_success(self, orchestrator_with_both):
        """Test successful generation with primary provider."""
        mock_response = AIResponse(
            content="Generated",
            model="claude",
            tokens_used=100,
            finish_reason="stop"
        )
        
        with patch.object(
            orchestrator_with_both.claude_client,
            'generate',
            new=AsyncMock(return_value=mock_response)
        ):
            response = await orchestrator_with_both.generate("Test")
            assert response.content == "Generated"
    
    @pytest.mark.asyncio
    async def test_fallback_on_error(self, orchestrator_with_both):
        """Test fallback to secondary provider on error."""
        mock_response = AIResponse(
            content="Fallback",
            model="gpt4",
            tokens_used=100,
            finish_reason="stop"
        )
        
        with patch.object(
            orchestrator_with_both.claude_client,
            'generate',
            new=AsyncMock(side_effect=Exception("Primary failed"))
        ):
            with patch.object(
                orchestrator_with_both.openai_client,
                'generate',
                new=AsyncMock(return_value=mock_response)
            ):
                response = await orchestrator_with_both.generate("Test")
                assert response.content == "Fallback"
    
    def test_usage_stats(self, orchestrator_with_both):
        """Test combined usage statistics."""
        orchestrator_with_both.claude_client.total_requests = 10
        orchestrator_with_both.openai_client.total_requests = 5
        
        stats = orchestrator_with_both.get_usage_stats()
        
        assert stats['total']['requests'] == 15


class TestCharacterAnalyzer:
    """Test suite for Character Analyzer."""
    
    @pytest.fixture
    def mock_ai_client(self):
        """Create mock AI client."""
        client = AsyncMock()  # Use AsyncMock instead of Mock
        # CharacterAnalyzer calls generate() which should return a JSON string
        client.generate.return_value = json.dumps({
            'character_name': 'Test Character',
            'core_traits': [
                {
                    'trait': 'Ambitious',
                    'description': 'Always trying to achieve goals',
                    'examples': ['Example 1', 'Example 2']
                },
                {
                    'trait': 'Scheming',
                    'description': 'Makes elaborate plans',
                    'examples': ['Example A', 'Example B']
                },
                {
                    'trait': 'Lovable',
                    'description': 'Endearing despite flaws',
                    'examples': ['Example X', 'Example Y']
                }
            ],
            'speech_patterns': ['Fast talking', 'Whining'],
            'catchphrases': ['Ricky!'],
            'relationships': [
                {
                    'character_name': 'Ricky',
                    'relationship_type': 'husband',
                    'description': 'Supportive but exasperated husband',
                    'key_moments': ['Meeting', 'Marriage', 'Career support']
                }
            ],
            'character_arc': 'episodic',
            'comedic_elements': ['physical comedy', 'facial expressions'],
            'modern_parallels': ['Influencer wannabe']
        })
        return client
    
    @pytest.mark.asyncio
    async def test_analyze_character(self, mock_ai_client):
        """Test character analysis."""
        analyzer = CharacterAnalyzer(mock_ai_client)
        
        analysis = await analyzer.analyze_character(
            character_name="Lucy Ricardo",
            character_description="Ambitious housewife...",
            show_context="1950s sitcom"
        )
        
        assert isinstance(analysis, CharacterAnalysisResponse)
        assert analysis.character_name == "Test Character"
        assert len(analysis.core_traits) == 3
        assert any(t.trait == 'Ambitious' for t in analysis.core_traits)
        assert len(analysis.relationships) == 1
        assert analysis.relationships[0].character_name == 'Ricky'
        assert analysis.relationships[0].relationship_type == 'husband'
    
    @pytest.mark.asyncio
    async def test_analyze_without_context(self, mock_ai_client):
        """Test analysis without show context."""
        analyzer = CharacterAnalyzer(mock_ai_client)
        
        analysis = await analyzer.analyze_character(
            character_name="Test Character",
            character_description="Test description"
        )
        
        assert isinstance(analysis, CharacterAnalysisResponse)
        assert analysis.character_name == "Test Character"
        assert isinstance(analysis.core_traits, list)
        assert len(analysis.core_traits) >= 3


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

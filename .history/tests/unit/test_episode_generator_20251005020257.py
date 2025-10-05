"""Tests for Episode Generator - Phase 3 script generation."""

import pytest
from unittest.mock import AsyncMock
import json

from src.services.creative.episode_generator import (
    EpisodeGenerator,
    EpisodeOutline,
    Scene
)


@pytest.fixture
def mock_claude_client():
    """Mock Claude AI client."""
    client = AsyncMock()
    client.generate = AsyncMock()
    return client


@pytest.fixture
def sample_transformation_rules():
    """Sample transformation rules."""
    return {
        'modern_premise': 'Lucy is a wannabe influencer',
        'setting': {
            'original': '1950s NYC apartment',
            'modern': '2025 Brooklyn loft'
        },
        'character_transformations': [
            {
                'original_name': 'Lucy Ricardo',
                'modern_occupation': 'Content creator',
                'motivation_shift': 'Wants to go viral'
            }
        ],
        'humor_transformation': {
            'original_style': 'Physical comedy',
            'modern_style': 'Cringe comedy'
        },
        'technology_opportunities': ['Instagram', 'TikTok']
    }


@pytest.fixture
def sample_narrative_structure():
    """Sample narrative structure."""
    return {
        'structure_type': 'Episodic sitcom',
        'opening_convention': 'Cold open',
        'closing_convention': 'Tag scene',
        'recurring_devices': [
            {
                'pattern_name': 'Scheme Backfires',
                'description': 'Plans go wrong'
            }
        ]
    }


@pytest.fixture
def valid_episode_response():
    """Valid episode outline response."""
    return {
        'title': 'The One Where Lucy Goes Viral',
        'logline': 'Lucy tries to become an influencer',
        'premise': 'Lucy decides to start a channel',
        'a_plot': 'Lucy attempts to create viral content',
        'b_plot': 'Ethel gets addicted to meditation app',
        'scenes': [
            {
                'scene_number': 1,
                'location': 'Living room',
                'characters': ['Lucy', 'Ricky'],
                'time_of_day': 'Morning',
                'description': 'Lucy watches viral videos',
                'plot_relevance': 'A-plot',
                'comedic_beats': ['Lucy mispronounces algorithm'],
                'estimated_runtime': 90
            },
            {
                'scene_number': 2,
                'location': 'Kitchen',
                'characters': ['Lucy', 'Ethel'],
                'time_of_day': 'Afternoon',
                'description': 'Lucy sets up recording equipment',
                'plot_relevance': 'A-plot',
                'comedic_beats': ['Equipment falls', 'Ring light blinds'],
                'estimated_runtime': 120
            }
        ],
        'opening_sequence': 'Cold open with Lucy filming TikTok dance',
        'closing_sequence': 'Tag scene with viral fail compilation',
        'key_comedic_moments': [
            'Lucy sets kitchen on fire',
            'Comment section roasts her'
        ],
        'total_runtime': 1320
    }


class TestEpisodeGeneratorBasics:
    """Test basic episode generation."""
    
    @pytest.mark.asyncio
    async def test_successful_episode_generation(
        self,
        mock_claude_client,
        sample_transformation_rules,
        sample_narrative_structure,
        valid_episode_response
    ):
        """Test successful episode outline generation."""
        mock_claude_client.generate.return_value = json.dumps(
            valid_episode_response
        )
        
        generator = EpisodeGenerator(claude_client=mock_claude_client)
        outline = await generator.generate_episode(
            show_title="I Love Lucy 2025",
            transformation_rules=sample_transformation_rules,
            narrative_structure=sample_narrative_structure,
            episode_number=1
        )
        
        assert outline is not None
        assert isinstance(outline, EpisodeOutline)
        assert outline.title == 'The One Where Lucy Goes Viral'
        assert len(outline.scenes) >= 2
        assert outline.total_runtime > 0
    
    @pytest.mark.asyncio
    async def test_scene_structure(
        self,
        mock_claude_client,
        sample_transformation_rules,
        sample_narrative_structure,
        valid_episode_response
    ):
        """Test scene structure parsing."""
        mock_claude_client.generate.return_value = json.dumps(
            valid_episode_response
        )
        
        generator = EpisodeGenerator(claude_client=mock_claude_client)
        outline = await generator.generate_episode(
            show_title="Test Show",
            transformation_rules=sample_transformation_rules,
            narrative_structure=sample_narrative_structure
        )
        
        scene = outline.scenes[0]
        assert isinstance(scene, Scene)
        assert scene.scene_number == 1
        assert scene.location == 'Living room'
        assert len(scene.characters) > 0
        assert len(scene.comedic_beats) > 0
        assert scene.estimated_runtime > 0
    
    @pytest.mark.asyncio
    async def test_comedic_beat_placement(
        self,
        mock_claude_client,
        sample_transformation_rules,
        sample_narrative_structure,
        valid_episode_response
    ):
        """Test comedic beats are included."""
        mock_claude_client.generate.return_value = json.dumps(
            valid_episode_response
        )
        
        generator = EpisodeGenerator(claude_client=mock_claude_client)
        outline = await generator.generate_episode(
            show_title="Test Show",
            transformation_rules=sample_transformation_rules,
            narrative_structure=sample_narrative_structure
        )
        
        # Check overall comedic moments
        assert len(outline.key_comedic_moments) > 0
        
        # Check scene-level beats
        for scene in outline.scenes:
            if scene.plot_relevance in ['A-plot', 'both']:
                assert len(scene.comedic_beats) > 0


class TestEpisodeGeneratorValidation:
    """Test validation and error handling."""
    
    @pytest.mark.asyncio
    async def test_invalid_json_handling(
        self,
        mock_claude_client,
        sample_transformation_rules,
        sample_narrative_structure
    ):
        """Test handling of invalid JSON response."""
        mock_claude_client.generate.return_value = "Invalid JSON {{"
        
        generator = EpisodeGenerator(claude_client=mock_claude_client)
        outline = await generator.generate_episode(
            show_title="Test Show",
            transformation_rules=sample_transformation_rules,
            narrative_structure=sample_narrative_structure
        )
        
        assert outline is None


class TestEpisodeStructure:
    """Test episode structure requirements."""
    
    @pytest.mark.asyncio
    async def test_runtime_calculation(
        self,
        mock_claude_client,
        sample_transformation_rules,
        sample_narrative_structure,
        valid_episode_response
    ):
        """Test runtime calculation."""
        mock_claude_client.generate.return_value = json.dumps(
            valid_episode_response
        )
        
        generator = EpisodeGenerator(claude_client=mock_claude_client)
        outline = await generator.generate_episode(
            show_title="Test Show",
            transformation_rules=sample_transformation_rules,
            narrative_structure=sample_narrative_structure
        )
        
        # Total runtime should be sum of scenes or provided total
        assert outline.total_runtime > 0
        
        # For sitcom, should be around 22 minutes (1320 seconds)
        assert 1000 <= outline.total_runtime <= 1600
    
    @pytest.mark.asyncio
    async def test_plot_structure(
        self,
        mock_claude_client,
        sample_transformation_rules,
        sample_narrative_structure,
        valid_episode_response
    ):
        """Test A-plot and B-plot structure."""
        mock_claude_client.generate.return_value = json.dumps(
            valid_episode_response
        )
        
        generator = EpisodeGenerator(claude_client=mock_claude_client)
        outline = await generator.generate_episode(
            show_title="Test Show",
            transformation_rules=sample_transformation_rules,
            narrative_structure=sample_narrative_structure
        )
        
        assert outline.a_plot_summary is not None
        assert len(outline.a_plot_summary) > 0
        
        # B-plot is optional but should be present for classic sitcoms
        if outline.b_plot_summary:
            assert len(outline.b_plot_summary) > 0


class TestEpisodePromptBuilding:
    """Test prompt construction."""
    
    @pytest.mark.asyncio
    async def test_user_prompt_integration(
        self,
        mock_claude_client,
        sample_transformation_rules,
        sample_narrative_structure,
        valid_episode_response
    ):
        """Test user prompt is integrated."""
        captured_prompt = None
        
        async def capture_generate(prompt, **kwargs):
            nonlocal captured_prompt
            captured_prompt = prompt
            return json.dumps(valid_episode_response)
        
        mock_claude_client.generate.side_effect = capture_generate
        
        generator = EpisodeGenerator(claude_client=mock_claude_client)
        await generator.generate_episode(
            show_title="Test Show",
            transformation_rules=sample_transformation_rules,
            narrative_structure=sample_narrative_structure,
            user_prompt="Make it about social media"
        )
        
        assert captured_prompt is not None
        assert "social media" in captured_prompt.lower()


# Run tests with: pytest tests/unit/test_episode_generator.py -v

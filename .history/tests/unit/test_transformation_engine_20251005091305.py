"""Tests for Transformation Engine - Phase 3 Creative Intelligence."""

import pytest
from unittest.mock import AsyncMock, MagicMock
import json
from datetime import datetime

from src.services.creative.transformation_engine import (
    TransformationEngine,
    TransformationRules,
    SettingTransformation,
    CharacterTransformation,
    HumorTransformation
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
    """Sample classic show data."""
    return {
        'title': 'I Love Lucy',
        'years': '1951-1957',
        'genre': ['Sitcom', 'Comedy'],
        'premise': 'A wacky redhead schemes to break into show business',
        'setting': '1950s New York City apartment'
    }


@pytest.fixture
def sample_character_analysis():
    """Sample character analysis data."""
    return {
        'characters': [
            {
                'character_name': 'Lucy Ricardo',
                'core_traits': ['ambitious', 'scheming', 'lovable'],
                'occupation': 'Housewife',
                'relationships': {'Ricky': 'husband', 'Ethel': 'best friend'}
            }
        ]
    }


@pytest.fixture
def sample_narrative_analysis():
    """Sample narrative analysis."""
    return {
        'structure_type': 'episodic',
        'recurring_devices': [
            {
                'pattern_name': 'Harebrained Scheme',
                'description': 'Lucy concocts elaborate plans'
            }
        ],
        'humor_style': 'Physical comedy and slapstick'
    }


@pytest.fixture
def valid_transformation_response():
    """Valid transformation rules response."""
    return {
        'show_title': 'I Love Lucy 2025',
        'modern_premise': 'A wannabe influencer schemes to go viral',
        'setting_transformation': {
            'original_era': '1950s',
            'modern_era': '2025',
            'original_location': 'NYC apartment',
            'modern_location': 'Brooklyn loft',
            'justification': 'Update to modern urban living',
            'visual_changes': ['Smart home tech', 'Ring lights'],
            'cultural_shifts': ['TV to streaming', 'Housewife to content creator']
        },
        'character_transformations': [
            {
                'original_name': 'Lucy Ricardo',
                'original_archetype': 'Housewife',
                'modern_archetype': 'Influencer',
                'original_occupation': 'Homemaker',
                'modern_occupation': 'Content creator',
                'personality_retention': ['Ambitious', 'Scheming', 'Charming'],
                'personality_updates': ['Tech-savvy', 'Social media obsessed'],
                'relationship_dynamics': 'Still married to entertainer',
                'technology_integration': 'Uses Instagram, TikTok, Ring lights',
                'motivation_shift': 'Wants to go viral instead of be on TV'
            }
        ],
        'humor_transformation': {
            'original_style': 'Physical comedy',
            'modern_style': 'Cringe comedy + viral fails',
            'device_mappings': {
                'Slapstick falls': 'Viral fail videos',
                'Disguises': 'Catfishing and fake accounts'
            },
            'preserved_elements': ['Visual humor', 'Escalating chaos'],
            'updated_elements': ['Social media context', 'Algorithm jokes'],
            'tone_guidance': 'Keep wholesome, update references'
        },
        'cultural_updates': ['TV shows to streaming', 'Phone calls to texts'],
        'technology_opportunities': ['Instagram', 'TikTok', 'Smart home'],
        'conflict_modernization': ['Public embarrassment to viral shame'],
        'relationship_updates': ['Same dynamics, modern context'],
        'value_preservation': ['Family-friendly', 'Character-driven'],
        'parody_enhancements': ['Over-the-top influencer culture'],
        'easter_eggs': ['References to original show']
    }


class TestTransformationEngineBasics:
    """Test basic transformation functionality."""
    
    @pytest.mark.asyncio
    async def test_successful_transformation(
        self, mock_claude_client, sample_show_data, 
        sample_character_analysis, sample_narrative_analysis,
        valid_transformation_response
    ):
        """Test successful transformation generation."""
        mock_claude_client.generate.return_value = json.dumps(
            valid_transformation_response
        )
        
        engine = TransformationEngine(claude_client=mock_claude_client)
        rules = await engine.generate_transformation_rules(
            show_data=sample_show_data,
            character_analysis=sample_character_analysis,
            narrative_analysis=sample_narrative_analysis
        )
        
        assert rules is not None
        assert isinstance(rules, TransformationRules)
        assert rules.modern_premise == 'A wannabe influencer schemes to go viral'
        assert len(rules.character_transformations) > 0
        assert len(rules.technology_opportunities) > 0
        assert mock_claude_client.generate.called
    
    @pytest.mark.asyncio
    async def test_character_mapping(
        self, mock_claude_client, sample_show_data,
        sample_character_analysis, sample_narrative_analysis,
        valid_transformation_response
    ):
        """Test character transformation mapping."""
        mock_claude_client.generate.return_value = json.dumps(
            valid_transformation_response
        )
        
        engine = TransformationEngine(claude_client=mock_claude_client)
        rules = await engine.generate_transformation_rules(
            show_data=sample_show_data,
            character_analysis=sample_character_analysis,
            narrative_analysis=sample_narrative_analysis
        )
        
        char_transform = rules.character_transformations[0]
        assert char_transform.original_name == 'Lucy Ricardo'
        assert char_transform.modern_occupation == 'Content creator'
        assert 'Ambitious' in char_transform.personality_retention
    
    @pytest.mark.asyncio
    async def test_cultural_updates(
        self, mock_claude_client, sample_show_data,
        sample_character_analysis, sample_narrative_analysis,
        valid_transformation_response
    ):
        """Test cultural updates are generated."""
        mock_claude_client.generate.return_value = json.dumps(
            valid_transformation_response
        )
        
        engine = TransformationEngine(claude_client=mock_claude_client)
        rules = await engine.generate_transformation_rules(
            show_data=sample_show_data,
            character_analysis=sample_character_analysis,
            narrative_analysis=sample_narrative_analysis
        )
        
        assert len(rules.cultural_updates) > 0
        assert any('streaming' in update.lower() for update in rules.cultural_updates)
    
    @pytest.mark.asyncio
    async def test_technology_integration(
        self, mock_claude_client, sample_show_data,
        sample_character_analysis, sample_narrative_analysis,
        valid_transformation_response
    ):
        """Test technology opportunities are identified."""
        mock_claude_client.generate.return_value = json.dumps(
            valid_transformation_response
        )
        
        engine = TransformationEngine(claude_client=mock_claude_client)
        rules = await engine.generate_transformation_rules(
            show_data=sample_show_data,
            character_analysis=sample_character_analysis,
            narrative_analysis=sample_narrative_analysis
        )
        
        assert len(rules.technology_opportunities) > 0
        assert 'Instagram' in rules.technology_opportunities or \
               'TikTok' in rules.technology_opportunities


class TestTransformationValidation:
    """Test validation and error handling."""
    
    @pytest.mark.asyncio
    async def test_invalid_json_handling(
        self, mock_claude_client, sample_show_data,
        sample_character_analysis, sample_narrative_analysis
    ):
        """Test handling of invalid JSON."""
        mock_claude_client.generate.return_value = "Not valid JSON {{"
        
        engine = TransformationEngine(
            claude_client=mock_claude_client,
            gpt_client=None
        )
        rules = await engine.generate_transformation_rules(
            show_data=sample_show_data,
            character_analysis=sample_character_analysis,
            narrative_analysis=sample_narrative_analysis
        )
        
        assert rules is None
        assert mock_claude_client.generate.call_count == 3  # Max retries
    
    @pytest.mark.asyncio
    async def test_validation_failures(
        self, mock_claude_client, sample_show_data,
        sample_character_analysis, sample_narrative_analysis,
        valid_transformation_response
    ):
        """Test retry on validation failure."""
        invalid_response = {'show_title': 'Test'}  # Missing required fields
        
        # First attempt fails, second succeeds
        mock_claude_client.generate.side_effect = [
            json.dumps(invalid_response),
            json.dumps(valid_transformation_response)
        ]
        
        engine = TransformationEngine(claude_client=mock_claude_client)
        rules = await engine.generate_transformation_rules(
            show_data=sample_show_data,
            character_analysis=sample_character_analysis,
            narrative_analysis=sample_narrative_analysis
        )
        
        assert rules is not None
        assert mock_claude_client.generate.call_count == 2


class TestTransformationCaching:
    """Test caching functionality."""
    
    @pytest.mark.asyncio
    async def test_cache_hit(
        self, mock_claude_client, mock_database, sample_show_data,
        sample_character_analysis, sample_narrative_analysis
    ):
        """Test cache retrieval on cache hit."""
        cached_rules = {
            'show_title': 'I Love Lucy 2025',
            'modern_premise': 'Cached premise',
            'setting_transformation': {
                'original_era': '1950s',
                'modern_era': '2025',
                'original_location': 'NYC',
                'modern_location': 'Brooklyn',
                'justification': 'Cached'
            },
            'character_transformations': [],
            'humor_transformation': {
                'original_style': 'Physical',
                'modern_style': 'Cringe'
            },
            'cultural_updates': [],
            'technology_opportunities': []
        }
        
        mock_database.mongodb['ai_analysis'].find_one.return_value = cached_rules
        
        engine = TransformationEngine(
            claude_client=mock_claude_client,
            database_manager=mock_database
        )
        rules = await engine.generate_transformation_rules(
            show_data=sample_show_data,
            character_analysis=sample_character_analysis,
            narrative_analysis=sample_narrative_analysis
        )
        
        assert rules is not None
        assert rules.modern_premise == 'Cached premise'
        assert not mock_claude_client.generate.called


class TestHumorTransformation:
    """Test humor transformation logic."""
    
    def test_humor_transformation_dataclass(self):
        """Test HumorTransformation dataclass."""
        humor = HumorTransformation(
            original_style="Physical comedy",
            modern_style="Cringe comedy",
            device_mappings={"Falls": "Viral fails"},
            preserved_elements=["Visual humor"],
            updated_elements=["Social context"],
            tone_guidance="Keep it wholesome"
        )
        
        assert humor.original_style == "Physical comedy"
        assert "Falls" in humor.device_mappings


# Run tests with: pytest tests/unit/test_transformation_engine.py -v

"""Integration tests for Show Analyzer - Phase 3 orchestration."""

import pytest
from unittest.mock import AsyncMock, MagicMock
from datetime import datetime

from src.services.creative.show_analyzer import (
    ShowAnalyzer,
    CompleteShowAnalysis,
    AnalysisProgress
)


@pytest.fixture
def mock_research_orchestrator():
    """Mock research orchestrator."""
    research = AsyncMock()
    research.research_show = AsyncMock(return_value={
        'title': 'I Love Lucy',
        'completeness_score': 0.9,
        'characters': [
            {'name': 'Lucy Ricardo', 'role': 'Main'},
            {'name': 'Ricky Ricardo', 'role': 'Main'}
        ]
    })
    return research


@pytest.fixture
def mock_character_analyzer():
    """Mock character analyzer."""
    analyzer = AsyncMock()
    
    async def mock_analyze(character_name, **kwargs):
        return MagicMock(
            character_name=character_name,
            core_traits=[MagicMock(trait='ambitious', description='desc', examples=[])],
            speech_patterns=['pattern1'],
            catchphrases=['phrase1'],
            comedic_elements=['element1']
        )
    
    analyzer.analyze_character = mock_analyze
    return analyzer


@pytest.fixture
def mock_narrative_analyzer():
    """Mock narrative analyzer."""
    analyzer = AsyncMock()
    analyzer.analyze_narrative = AsyncMock(return_value=MagicMock(
        structure_type='episodic',
        opening_convention='Theme song',
        closing_convention='Credits',
        recurring_devices=[MagicMock(
            pattern_name='Scheme',
            description='Plans go wrong',
            frequency='every episode',
            examples=['ex1'],
            purpose='Comedy'
        )],
        pacing_notes='Fast',
        unique_signatures=['signature1']
    ))
    return analyzer


@pytest.fixture
def mock_transformation_engine():
    """Mock transformation engine."""
    engine = AsyncMock()
    engine.generate_transformation_rules = AsyncMock(return_value=MagicMock(
        modern_premise='Modern premise',
        setting_transformation=MagicMock(
            original_location='1950s NYC',
            modern_location='2025 Brooklyn',
            justification='Modern update'
        ),
        character_transformations=[MagicMock(
            original_name='Lucy',
            modern_occupation='Influencer',
            motivation_shift='Go viral',
            technology_integration='Instagram'
        )],
        humor_transformation=MagicMock(
            original_style='Physical',
            modern_style='Cringe',
            device_mappings={}
        ),
        cultural_updates=['TV to streaming'],
        technology_opportunities=['Instagram']
    ))
    return engine


@pytest.fixture
def mock_database():
    """Mock database manager."""
    db = MagicMock()
    db.mongodb = {
        'ai_analysis': AsyncMock()
    }
    return db


class TestShowAnalyzerWorkflow:
    """Test complete show analyzer workflow."""
    
    @pytest.mark.asyncio
    async def test_complete_analysis_workflow(
        self,
        mock_research_orchestrator,
        mock_character_analyzer,
        mock_narrative_analyzer,
        mock_transformation_engine,
        mock_database
    ):
        """Test complete end-to-end analysis workflow."""
        analyzer = ShowAnalyzer(
            research_orchestrator=mock_research_orchestrator,
            character_analyzer=mock_character_analyzer,
            narrative_analyzer=mock_narrative_analyzer,
            transformation_engine=mock_transformation_engine,
            database_manager=mock_database
        )
        
        result = await analyzer.analyze_show(
            show_title="I Love Lucy",
            tmdb_id=1668,
            imdb_id="tt0043208"
        )
        
        assert result is not None
        assert isinstance(result, CompleteShowAnalysis)
        assert result.show_title == "I Love Lucy"
        assert result.completeness_score > 0
        assert result.analysis_time_seconds > 0
        assert len(result.character_analyses) > 0
    
    @pytest.mark.asyncio
    async def test_progress_callbacks(
        self,
        mock_research_orchestrator,
        mock_character_analyzer,
        mock_narrative_analyzer,
        mock_transformation_engine
    ):
        """Test progress callback tracking."""
        analyzer = ShowAnalyzer(
            research_orchestrator=mock_research_orchestrator,
            character_analyzer=mock_character_analyzer,
            narrative_analyzer=mock_narrative_analyzer,
            transformation_engine=mock_transformation_engine
        )
        
        progress_updates = []
        
        async def track_progress(progress: AnalysisProgress):
            progress_updates.append({
                'step': progress.current_step,
                'completed': progress.completed_steps
            })
        
        await analyzer.analyze_show(
            show_title="Test Show",
            progress_callback=track_progress
        )
        
        assert len(progress_updates) > 0
        assert any('Researching' in p['step'] for p in progress_updates)
        assert any('characters' in p['step'].lower() for p in progress_updates)
    
    @pytest.mark.asyncio
    async def test_partial_failure_handling(
        self,
        mock_research_orchestrator,
        mock_character_analyzer,
        mock_narrative_analyzer,
        mock_transformation_engine
    ):
        """Test handling of partial analysis failures."""
        # Make narrative analysis fail
        mock_narrative_analyzer.analyze_narrative = AsyncMock(
            side_effect=Exception("Analysis failed")
        )
        
        analyzer = ShowAnalyzer(
            research_orchestrator=mock_research_orchestrator,
            character_analyzer=mock_character_analyzer,
            narrative_analyzer=mock_narrative_analyzer,
            transformation_engine=mock_transformation_engine
        )
        
        result = await analyzer.analyze_show(show_title="Test Show")
        
        # Should still return result with partial data
        assert result is not None
        assert result.narrative_analysis is None
        assert result.completeness_score < 1.0


class TestShowAnalyzerCompletenessScoring:
    """Test completeness score calculation."""
    
    @pytest.mark.asyncio
    async def test_full_completeness(
        self,
        mock_research_orchestrator,
        mock_character_analyzer,
        mock_narrative_analyzer,
        mock_transformation_engine
    ):
        """Test completeness with all components successful."""
        analyzer = ShowAnalyzer(
            research_orchestrator=mock_research_orchestrator,
            character_analyzer=mock_character_analyzer,
            narrative_analyzer=mock_narrative_analyzer,
            transformation_engine=mock_transformation_engine
        )
        
        result = await analyzer.analyze_show(show_title="Test Show")
        
        # All components succeed, high completeness
        assert result.completeness_score >= 0.8
    
    @pytest.mark.asyncio
    async def test_partial_completeness(
        self,
        mock_research_orchestrator,
        mock_character_analyzer,
        mock_narrative_analyzer,
        mock_transformation_engine
    ):
        """Test completeness with some components failing."""
        # Make transformations fail
        mock_transformation_engine.generate_transformation_rules = AsyncMock(
            return_value=None
        )
        
        analyzer = ShowAnalyzer(
            research_orchestrator=mock_research_orchestrator,
            character_analyzer=mock_character_analyzer,
            narrative_analyzer=mock_narrative_analyzer,
            transformation_engine=mock_transformation_engine
        )
        
        result = await analyzer.analyze_show(show_title="Test Show")
        
        # Missing transformation (25%), should be around 0.75
        assert 0.6 <= result.completeness_score <= 0.8


class TestShowAnalyzerCaching:
    """Test show analyzer caching."""
    
    @pytest.mark.asyncio
    async def test_cache_save(
        self,
        mock_research_orchestrator,
        mock_character_analyzer,
        mock_narrative_analyzer,
        mock_transformation_engine,
        mock_database
    ):
        """Test that complete analysis is cached."""
        analyzer = ShowAnalyzer(
            research_orchestrator=mock_research_orchestrator,
            character_analyzer=mock_character_analyzer,
            narrative_analyzer=mock_narrative_analyzer,
            transformation_engine=mock_transformation_engine,
            database_manager=mock_database
        )
        
        await analyzer.analyze_show(show_title="Test Show")
        
        # Should have cached the result
        assert mock_database.mongodb['ai_analysis'].update_one.called


# Run tests with: pytest tests/integration/test_show_analyzer.py -v

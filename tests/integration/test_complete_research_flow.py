"""
Integration test for complete research flow.

Tests the full research orchestrator with all three sources.

Copyright (c) 2025. All Rights Reserved. Patent Pending.
"""

import pytest
from unittest.mock import AsyncMock, MagicMock
from datetime import datetime

from src.services.research.research_orchestrator import ResearchOrchestrator
from src.services.research.wikipedia_scraper import WikipediaShowData
from src.services.research.tmdb_scraper import TMDBShowData
from src.services.research.imdb_scraper import IMDBShowData


@pytest.mark.integration
@pytest.mark.asyncio
async def test_research_orchestrator_all_sources():
    """Test research orchestrator with all three sources."""
    # Create orchestrator with mocked dependencies
    orchestrator = ResearchOrchestrator(
        tmdb_api_key="test_key",
        imdb_id="tt0043208",
        cache_manager=AsyncMock()
    )
    
    # Mock successful research from all sources
    mock_wiki_data = WikipediaShowData(
        title="I Love Lucy",
        url="http://test",
        plot_summary="Classic sitcom",
        setting="1950s New York",
        main_characters=[{"name": "Lucy Ricardo", "actor": "Lucille Ball"}],
        themes=["Comedy", "Family"]
    )
    
    mock_tmdb_data = TMDBShowData(
        tmdb_id=1668,
        title="I Love Lucy",
        original_title="I Love Lucy",
        overview="Classic sitcom",
        vote_average=8.2,
        vote_count=150,
        genres=["Comedy"],
        cast=[{"name": "Lucille Ball", "character": "Lucy"}],
        episode_count=180,
        season_count=6
    )
    
    mock_imdb_data = IMDBShowData(
        imdb_id="tt0043208",
        title="I Love Lucy",
        rating=8.5,
        vote_count=50000,
        reviews=[{"title": "Great!", "text": "Classic show"}],
        trivia=["First filmed before live audience"]
    )
    
    # Mock the _gather_all_sources method
    async def mock_gather(show_title):
        return {
            'wikipedia': mock_wiki_data,
            'tmdb': mock_tmdb_data,
            'imdb': mock_imdb_data
        }
    
    orchestrator._gather_all_sources = mock_gather
    
    # Run research
    result = await orchestrator.research_show("I Love Lucy")
    
    # Verify merged data
    assert result.title == "I Love Lucy"
    assert len(result.sources) == 3
    assert 'wikipedia' in result.sources
    assert 'tmdb' in result.sources
    assert 'imdb' in result.sources
    
    # Verify data from each source
    assert result.setting == "1950s New York"  # From Wikipedia
    assert result.episode_count == 180  # From TMDB
    assert result.rating == 8.5  # From IMDB (preferred over TMDB)
    assert len(result.user_reviews) == 1  # From IMDB
    assert len(result.trivia) == 1  # From IMDB
    
    # Verify completeness scores
    assert result.data_completeness > 0.5
    assert result.source_agreement >= 0


@pytest.mark.integration
@pytest.mark.asyncio
async def test_research_orchestrator_partial_failure():
    """Test graceful handling when one source fails."""
    orchestrator = ResearchOrchestrator(
        tmdb_api_key="test_key",
        cache_manager=AsyncMock()
    )
    
    # Mock one successful, two failed sources
    mock_tmdb_data = TMDBShowData(
        tmdb_id=1668,
        title="Test Show",
        original_title="Test Show",
        overview="Test",
        vote_average=7.0,
        vote_count=100,
        genres=["Comedy"],
        cast=[],
        episode_count=100,
        season_count=5
    )
    
    async def mock_gather(show_title):
        return {
            'wikipedia': None,  # Failed
            'tmdb': mock_tmdb_data,  # Succeeded
            'imdb': None  # Failed
        }
    
    orchestrator._gather_all_sources = mock_gather
    
    # Should still complete with partial data
    result = await orchestrator.research_show("Test Show")
    
    assert result.title == "Test Show"
    assert len(result.sources) == 1
    assert 'tmdb' in result.sources
    assert result.episode_count == 100


@pytest.mark.integration
@pytest.mark.asyncio
async def test_research_orchestrator_completeness_scoring():
    """Test data completeness scoring."""
    orchestrator = ResearchOrchestrator()
    
    # Create result with varying completeness
    from src.services.research.research_orchestrator import (
        UnifiedShowResearch
    )
    
    # High completeness
    complete_result = UnifiedShowResearch(
        title="Test Show",
        years="1950-1960",
        network="CBS",
        genres=["Comedy"],
        premise="Test premise",
        episode_count=100,
        season_count=5,
        main_characters=[{"name": "Test"}],
        cast=[{"name": "Actor"}]
    )
    
    completeness = orchestrator._calculate_completeness(complete_result)
    assert completeness > 0.7
    
    # Low completeness
    incomplete_result = UnifiedShowResearch(
        title="Test Show",
        years="Unknown"
    )
    
    completeness_low = orchestrator._calculate_completeness(incomplete_result)
    assert completeness_low < 0.3

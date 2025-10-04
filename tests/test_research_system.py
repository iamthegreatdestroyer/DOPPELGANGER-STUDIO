"""
Tests for Research System components.

Tests Wikipedia scraper, TMDB scraper, and Research Orchestrator.

Copyright (c) 2025. All Rights Reserved. Patent Pending.
"""

import pytest
from unittest.mock import Mock, patch, AsyncMock
from datetime import datetime

from src.services.research.wikipedia_scraper import (
    WikipediaResearchScraper,
    WikipediaShowData
)
from src.services.research.tmdb_scraper import (
    TMDBResearchScraper,
    TMDBShowData
)
from src.services.research.research_orchestrator import (
    ResearchOrchestrator,
    UnifiedShowResearch
)


class TestWikipediaResearchScraper:
    """Test suite for Wikipedia research scraper."""
    
    @pytest.fixture
    def mock_wikipedia_page(self):
        """Create mock Wikipedia page."""
        page = Mock()
        page.exists.return_value = True
        page.title = "I Love Lucy"
        page.fullurl = "https://en.wikipedia.org/wiki/I_Love_Lucy"
        page.summary = "I Love Lucy is an American sitcom (1951-1957)..."
        page.sections = []
        return page
    
    @pytest.mark.asyncio
    async def test_research_show_success(self, mock_wikipedia_page):
        """Test successful show research."""
        with patch('wikipediaapi.Wikipedia') as mock_wiki:
            mock_wiki.return_value.page.return_value = mock_wikipedia_page
            
            async with WikipediaResearchScraper() as scraper:
                scraper.wiki.page = Mock(return_value=mock_wikipedia_page)
                data = await scraper.research_show("I Love Lucy")
                
                assert data.title == "I Love Lucy"
                assert data.source_url == mock_wikipedia_page.fullurl
                assert isinstance(data.scraped_at, datetime)
    
    @pytest.mark.asyncio
    async def test_extract_years(self):
        """Test year extraction from text."""
        scraper = WikipediaResearchScraper()
        
        page = Mock()
        page.summary = "Show aired from 1951 to 1957"
        
        years = await scraper._extract_years(page)
        assert "1951" in years or "1957" in years
    
    @pytest.mark.asyncio
    async def test_page_not_found(self):
        """Test handling of non-existent page."""
        async with WikipediaResearchScraper() as scraper:
            scraper.wiki.page = Mock(
                return_value=Mock(exists=Mock(return_value=False))
            )
            scraper._find_page_variations = AsyncMock(return_value=None)
            
            with pytest.raises(ValueError, match="not found"):
                await scraper.research_show("NonexistentShow")


class TestTMDBResearchScraper:
    """Test suite for TMDB research scraper."""
    
    @pytest.fixture
    def mock_tmdb_response(self):
        """Create mock TMDB API response."""
        return {
            'id': 1234,
            'name': 'I Love Lucy',
            'original_name': 'I Love Lucy',
            'overview': 'Classic sitcom...',
            'first_air_date': '1951-10-15',
            'last_air_date': '1957-05-06',
            'vote_average': 8.5,
            'genres': [{'id': 35, 'name': 'Comedy'}],
            'networks': [{'id': 1, 'name': 'CBS'}],
            'number_of_episodes': 180,
            'number_of_seasons': 6,
            'created_by': [{'id': 1, 'name': 'Lucille Ball'}],
            'seasons': []
        }
    
    @pytest.mark.asyncio
    async def test_research_show_success(self, mock_tmdb_response):
        """Test successful TMDB research."""
        async with TMDBResearchScraper(api_key="test_key") as scraper:
            scraper._search_show = AsyncMock(return_value=1234)
            scraper._get_show_details = AsyncMock(return_value=mock_tmdb_response)
            scraper._get_credits = AsyncMock(return_value={'cast': [], 'crew': []})
            
            data = await scraper.research_show("I Love Lucy")
            
            assert data.tmdb_id == 1234
            assert data.title == "I Love Lucy"
            assert data.vote_average == 8.5
            assert data.episode_count == 180
    
    @pytest.mark.asyncio
    async def test_show_not_found(self):
        """Test handling of show not found."""
        async with TMDBResearchScraper(api_key="test_key") as scraper:
            scraper._search_show = AsyncMock(return_value=None)
            
            with pytest.raises(ValueError, match="not found"):
                await scraper.research_show("NonexistentShow")


class TestResearchOrchestrator:
    """Test suite for Research Orchestrator."""
    
    @pytest.fixture
    def mock_wiki_data(self):
        """Create mock Wikipedia data."""
        return WikipediaShowData(
            title="I Love Lucy",
            years="1951-1957",
            network="CBS",
            genre=["Sitcom"],
            premise="Classic sitcom...",
            episode_count=180,
            season_count=6
        )
    
    @pytest.fixture
    def mock_tmdb_data(self):
        """Create mock TMDB data."""
        return TMDBShowData(
            tmdb_id=1234,
            title="I Love Lucy",
            original_title="I Love Lucy",
            overview="Classic sitcom...",
            first_air_date="1951-10-15",
            episode_count=180,
            season_count=6,
            vote_average=8.5
        )
    
    @pytest.mark.asyncio
    async def test_research_show_both_sources(
        self,
        mock_wiki_data,
        mock_tmdb_data
    ):
        """Test research with both sources successful."""
        orchestrator = ResearchOrchestrator(tmdb_api_key="test_key")
        
        with patch.object(
            orchestrator,
            '_gather_all_sources',
            new=AsyncMock(return_value={
                'wikipedia': mock_wiki_data,
                'tmdb': mock_tmdb_data
            })
        ):
            research = await orchestrator.research_show("I Love Lucy")
            
            assert research.title == "I Love Lucy"
            assert len(research.sources) == 2
            assert research.episode_count == 180
            assert research.rating == 8.5
    
    @pytest.mark.asyncio
    async def test_calculate_completeness(self):
        """Test data completeness calculation."""
        orchestrator = ResearchOrchestrator()
        
        research = UnifiedShowResearch(
            title="Test Show",
            years="2020-2023",
            network="ABC",
            premise="Test premise",
            episode_count=100
        )
        
        completeness = orchestrator._calculate_completeness(research)
        assert 0.0 <= completeness <= 1.0
        assert completeness > 0.5  # Should have decent completeness


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

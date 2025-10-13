"""
Unit Tests for Research Scrapers.

Tests Wikipedia, TMDB scrapers with mocked API responses.

Copyright (c) 2025. All Rights Reserved. Patent Pending.
"""

import pytest
import asyncio
from unittest.mock import Mock, AsyncMock, patch, MagicMock
from datetime import datetime

from src.services.research.wikipedia_scraper import WikipediaResearchScraper
from src.services.research.tmdb_scraper import TMDBResearchScraper
from src.models.research import WikipediaData, TMDBData


class TestWikipediaResearchScraper:
    """Test suite for Wikipedia research scraper."""
    
    @pytest.fixture
    def mock_wikipedia_page(self):
        """Create mock Wikipedia page."""
        page = Mock()
        page.exists.return_value = True
        page.title = "I Love Lucy"
        page.summary = "I Love Lucy is an American sitcom that aired from 1951 to 1957 on CBS."
        page.fullurl = "https://en.wikipedia.org/wiki/I_Love_Lucy"
        page.sections = []
        return page
    
    @pytest.mark.asyncio
    async def test_scraper_initialization(self):
        """Test scraper initializes correctly."""
        scraper = WikipediaResearchScraper()
        assert scraper.wiki is not None
        assert scraper._rate_limit_delay == 1.0
    
    @pytest.mark.asyncio
    async def test_context_manager(self):
        """Test async context manager."""
        async with WikipediaResearchScraper() as scraper:
            assert scraper.session is not None
        # Session should be closed after exit
    
    @pytest.mark.asyncio
    async def test_extract_years_range(self):
        """Test year range extraction."""
        scraper = WikipediaResearchScraper()
        page = Mock()
        page.summary = "Show aired from 1951 to 1957"
        
        years = scraper._extract_years(page)
        assert years == "1951-1957"
    
    @pytest.mark.asyncio
    async def test_extract_years_single(self):
        """Test single year extraction."""
        scraper = WikipediaResearchScraper()
        page = Mock()
        page.summary = "Show premiered in 1951"
        
        years = scraper._extract_years(page)
        assert years == "1951"
    
    @pytest.mark.asyncio
    async def test_extract_years_none(self):
        """Test when no years found."""
        scraper = WikipediaResearchScraper()
        page = Mock()
        page.summary = "A classic television show"
        
        years = scraper._extract_years(page)
        assert years == "Unknown"
    
    @pytest.mark.asyncio
    async def test_find_section(self):
        """Test section finding."""
        scraper = WikipediaResearchScraper()
        
        # Create mock sections
        target_section = Mock()
        target_section.title = "Characters"
        target_section.text = "Main characters..."
        target_section.sections = []
        
        other_section = Mock()
        other_section.title = "Plot"
        other_section.sections = []
        
        page = Mock()
        page.sections = [other_section, target_section]
        
        found = scraper._find_section(page, "Characters")
        assert found == target_section
    
    @pytest.mark.asyncio
    async def test_find_section_not_found(self):
        """Test section not found."""
        scraper = WikipediaResearchScraper()
        page = Mock()
        page.sections = []
        
        found = scraper._find_section(page, "NonexistentSection")
        assert found is None
    
    @pytest.mark.asyncio
    async def test_parse_character_section(self):
        """Test character parsing."""
        scraper = WikipediaResearchScraper()
        
        section = Mock()
        section.text = """Lucy Ricardo is the main character played by Lucille Ball.
        
        Ricky Ricardo is Lucy's husband, a Cuban bandleader.
        
        Ethel Mertz is Lucy's best friend and landlady."""
        
        characters = scraper._parse_character_section(section)
        
        assert len(characters) > 0
        assert any('Lucy' in c.name for c in characters)
    
    @pytest.mark.asyncio
    async def test_extract_setting_time(self):
        """Test time period extraction."""
        scraper = WikipediaResearchScraper()
        text = "Set in the 1950s in New York City"
        
        setting = scraper._extract_setting(text)
        assert setting is not None
        assert '1950' in setting.lower() or 'new york' in setting.lower()
    
    @pytest.mark.asyncio
    async def test_extract_setting_location(self):
        """Test location extraction."""
        scraper = WikipediaResearchScraper()
        text = "The show takes place in Manhattan"
        
        setting = scraper._extract_setting(text)
        assert setting == "Manhattan"
    
    @pytest.mark.asyncio
    async def test_rate_limiting(self):
        """Test rate limiting works."""
        scraper = WikipediaResearchScraper()
        scraper._rate_limit_delay = 0.1  # Fast for testing
        
        start = asyncio.get_event_loop().time()
        
        # First request - no delay
        await scraper._respect_rate_limit()
        
        # Second request - should delay
        await scraper._respect_rate_limit()
        
        elapsed = asyncio.get_event_loop().time() - start
        assert elapsed >= 0.1
    
    @pytest.mark.asyncio
    @patch('wikipediaapi.Wikipedia')
    async def test_research_show_success(self, mock_wiki, mock_wikipedia_page):
        """Test successful show research."""
        # Setup mock
        mock_wiki_instance = Mock()
        mock_wiki_instance.page.return_value = mock_wikipedia_page
        mock_wiki.return_value = mock_wiki_instance
        
        async with WikipediaResearchScraper() as scraper:
            scraper.wiki = mock_wiki_instance
            
            # Mock the extraction methods to avoid network calls
            scraper._extract_infobox_data = AsyncMock()
            scraper._extract_characters = AsyncMock()
            scraper._extract_plot_info = AsyncMock()
            scraper._extract_production_info = AsyncMock()
            scraper._extract_themes = AsyncMock()
            
            data = await scraper.research_show("I Love Lucy")
            
            assert isinstance(data, WikipediaData)
            assert data.title == "I Love Lucy"
            assert "1951" in data.years
    
    @pytest.mark.asyncio
    async def test_research_show_not_found(self):
        """Test show not found."""
        async with WikipediaResearchScraper() as scraper:
            # Mock to return non-existent page
            mock_page = Mock()
            mock_page.exists.return_value = False
            scraper._find_page = AsyncMock(return_value=mock_page)
            
            with pytest.raises(ValueError, match="not found"):
                await scraper.research_show("NonexistentShow123")


class TestTMDBResearchScraper:
    """Test suite for TMDB research scraper."""
    
    @pytest.fixture
    def mock_tmdb_search_response(self):
        """Mock TMDB search API response."""
        return {
            'results': [
                {
                    'id': 1668,
                    'name': 'I Love Lucy',
                    'first_air_date': '1951-10-15'
                }
            ]
        }
    
    @pytest.fixture
    def mock_tmdb_details_response(self):
        """Mock TMDB show details API response."""
        return {
            'id': 1668,
            'name': 'I Love Lucy',
            'original_name': 'I Love Lucy',
            'overview': 'Classic sitcom about Lucy Ricardo.',
            'first_air_date': '1951-10-15',
            'last_air_date': '1957-05-06',
            'status': 'Ended',
            'vote_average': 8.5,
            'vote_count': 123,
            'popularity': 45.6,
            'genres': [{'name': 'Comedy'}],
            'networks': [{'name': 'CBS'}],
            'created_by': [{'name': 'Desi Arnaz', 'id': 1}],
            'number_of_episodes': 180,
            'number_of_seasons': 6,
            'seasons': [
                {
                    'season_number': 1,
                    'episode_count': 35,
                    'name': 'Season 1'
                }
            ],
            'poster_path': '/poster.jpg',
            'backdrop_path': '/backdrop.jpg'
        }
    
    @pytest.fixture
    def mock_tmdb_credits_response(self):
        """Mock TMDB credits API response."""
        return {
            'cast': [
                {
                    'name': 'Lucille Ball',
                    'character': 'Lucy Ricardo',
                    'order': 0
                },
                {
                    'name': 'Desi Arnaz',
                    'character': 'Ricky Ricardo',
                    'order': 1
                }
            ],
            'crew': []
        }
    
    def test_scraper_initialization_with_key(self):
        """Test scraper initializes with API key."""
        scraper = TMDBResearchScraper(api_key="test_key")
        assert scraper.api_key == "test_key"
    
    def test_scraper_initialization_no_key(self):
        """Test scraper fails without API key."""
        with patch.dict('os.environ', {}, clear=True):
            with pytest.raises(ValueError, match="API key required"):
                TMDBResearchScraper()
    
    @pytest.mark.asyncio
    async def test_context_manager(self):
        """Test async context manager."""
        async with TMDBResearchScraper(api_key="test") as scraper:
            assert scraper.session is not None
    
    @pytest.mark.asyncio
    async def test_rate_limiting(self):
        """Test TMDB rate limiting."""
        scraper = TMDBResearchScraper(api_key="test")
        
        # Simulate 40 requests
        for _ in range(40):
            await scraper._respect_rate_limit()
        
        # 41st request should cause delay
        start = asyncio.get_event_loop().time()
        await scraper._respect_rate_limit()
        elapsed = asyncio.get_event_loop().time() - start
        
        # Should have waited
        assert elapsed > 0
    
    @pytest.mark.asyncio
    async def test_search_show_success(
        self,
        mock_tmdb_search_response
    ):
        """Test successful show search."""
        async with TMDBResearchScraper(api_key="test") as scraper:
            # Mock HTTP response
            mock_response = AsyncMock()
            mock_response.status = 200
            mock_response.json = AsyncMock(return_value=mock_tmdb_search_response)
            
            scraper.session.get = AsyncMock(return_value=mock_response)
            mock_response.__aenter__ = AsyncMock(return_value=mock_response)
            mock_response.__aexit__ = AsyncMock()
            
            show_id = await scraper._search_show("I Love Lucy")
            assert show_id == 1668
    
    @pytest.mark.asyncio
    async def test_search_show_not_found(self):
        """Test show not found."""
        async with TMDBResearchScraper(api_key="test") as scraper:
            # Mock empty response
            mock_response = AsyncMock()
            mock_response.status = 200
            mock_response.json = AsyncMock(return_value={'results': []})
            
            scraper.session.get = AsyncMock(return_value=mock_response)
            mock_response.__aenter__ = AsyncMock(return_value=mock_response)
            mock_response.__aexit__ = AsyncMock()
            
            show_id = await scraper._search_show("NonexistentShow")
            assert show_id is None
    
    @pytest.mark.asyncio
    async def test_search_show_rate_limited(self):
        """Test handling of 429 rate limit."""
        async with TMDBResearchScraper(api_key="test") as scraper:
            # First response: 429, second: success
            mock_response_429 = AsyncMock()
            mock_response_429.status = 429
            mock_response_429.__aenter__ = AsyncMock(return_value=mock_response_429)
            mock_response_429.__aexit__ = AsyncMock()
            
            mock_response_200 = AsyncMock()
            mock_response_200.status = 200
            mock_response_200.json = AsyncMock(return_value={'results': [{'id': 123}]})
            mock_response_200.__aenter__ = AsyncMock(return_value=mock_response_200)
            mock_response_200.__aexit__ = AsyncMock()
            
            scraper.session.get = AsyncMock(
                side_effect=[mock_response_429, mock_response_200]
            )
            
            # Should retry and succeed
            with patch('asyncio.sleep', new_callable=AsyncMock):
                show_id = await scraper._search_show("Test")
                assert show_id == 123
    
    @pytest.mark.asyncio
    async def test_build_show_data(
        self,
        mock_tmdb_details_response,
        mock_tmdb_credits_response
    ):
        """Test building TMDBData from API responses."""
        scraper = TMDBResearchScraper(api_key="test")
        
        data = scraper._build_show_data(
            mock_tmdb_details_response,
            mock_tmdb_credits_response
        )
        
        assert isinstance(data, TMDBData)
        assert data.tmdb_id == 1668
        assert data.title == "I Love Lucy"
        assert data.vote_average == 8.5
        assert len(data.cast) == 2
        assert data.cast[0].name == "Lucille Ball"
        assert data.episode_count == 180
        assert data.season_count == 6
    
    def test_build_image_url(self):
        """Test image URL building."""
        scraper = TMDBResearchScraper(api_key="test")
        
        url = scraper._build_image_url("/poster.jpg")
        assert url == "https://image.tmdb.org/t/p/original/poster.jpg"
        
        url_none = scraper._build_image_url(None)
        assert url_none is None
    
    @pytest.mark.asyncio
    async def test_research_show_integration(
        self,
        mock_tmdb_search_response,
        mock_tmdb_details_response,
        mock_tmdb_credits_response
    ):
        """Test full research flow."""
        async with TMDBResearchScraper(api_key="test") as scraper:
            # Mock all HTTP calls
            async def mock_get(*args, **kwargs):
                mock_response = AsyncMock()
                mock_response.status = 200
                
                url = str(args[0]) if args else kwargs.get('url', '')
                
                if 'search' in url:
                    mock_response.json = AsyncMock(return_value=mock_tmdb_search_response)
                elif 'credits' in url:
                    mock_response.json = AsyncMock(return_value=mock_tmdb_credits_response)
                else:
                    mock_response.json = AsyncMock(return_value=mock_tmdb_details_response)
                
                mock_response.__aenter__ = AsyncMock(return_value=mock_response)
                mock_response.__aexit__ = AsyncMock()
                return mock_response
            
            scraper.session.get = mock_get
            
            data = await scraper.research_show("I Love Lucy")
            
            assert isinstance(data, TMDBData)
            assert data.title == "I Love Lucy"
            assert len(data.cast) > 0

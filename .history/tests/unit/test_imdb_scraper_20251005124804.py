"""
Unit tests for IMDB Research Scraper.

Tests ethical scraping practices, rate limiting, caching, and data extraction.

Copyright (c) 2025. All Rights Reserved. Patent Pending.
"""

import pytest
from unittest.mock import AsyncMock, Mock, patch
from datetime import datetime, timedelta
from src.services.research.imdb_scraper import (
    IMDBResearchScraper,
    IMDBShowData
)


@pytest.mark.asyncio
async def test_imdb_scraper_initialization():
    """Test scraper initialization with custom user agent."""
    scraper = IMDBResearchScraper(
        user_agent="TestAgent/1.0",
        cache_manager=None
    )
    
    assert scraper.user_agent == "TestAgent/1.0"
    assert scraper.RATE_LIMIT_DELAY == 5.0
    assert scraper.CACHE_TTL_DAYS == 7


@pytest.mark.asyncio
async def test_rate_limiting_enforced():
    """Test that rate limiting delays requests appropriately."""
    scraper = IMDBResearchScraper()
    scraper.last_request_time = datetime.now()
    
    start = datetime.now()
    await scraper._rate_limit()
    elapsed = (datetime.now() - start).total_seconds()
    
    # Allow small timing variance (0.1s)
    assert elapsed >= scraper.RATE_LIMIT_DELAY - 0.1


@pytest.mark.asyncio
async def test_robots_txt_respected():
    """Test that robots.txt blocks are respected."""
    scraper = IMDBResearchScraper()
    scraper.robots_parser = Mock()
    scraper.robots_parser.can_fetch.return_value = False
    
    result = await scraper._can_fetch("/blocked-path")
    assert result is False


@pytest.mark.asyncio
async def test_robots_txt_allowed():
    """Test that robots.txt allows permitted paths."""
    scraper = IMDBResearchScraper()
    scraper.robots_parser = Mock()
    scraper.robots_parser.can_fetch.return_value = True
    
    result = await scraper._can_fetch("/allowed-path")
    assert result is True


@pytest.mark.asyncio
async def test_fetch_page_handles_429():
    """Test that HTTP 429 (rate limited) raises exception."""
    scraper = IMDBResearchScraper()
    
    mock_response = AsyncMock()
    mock_response.status = 429
    
    # Create proper async context manager
    class MockContext:
        async def __aenter__(self):
            return mock_response
        async def __aexit__(self, *args):
            pass
    
    mock_session = Mock()  # Use Mock, not AsyncMock
    mock_session.get.return_value = MockContext()
    
    scraper.session = mock_session
    
    with pytest.raises(Exception, match="Rate limited by IMDB"):
        await scraper._fetch_page("http://test.com")


@pytest.mark.asyncio
async def test_fetch_page_timeout_handling():
    """Test timeout handling returns None."""
    scraper = IMDBResearchScraper()
    
    mock_session = AsyncMock()
    mock_session.get.side_effect = Exception("Timeout")
    
    scraper.session = mock_session
    
    result = await scraper._fetch_page("http://test.com")
    assert result is None


@pytest.mark.asyncio
async def test_cache_retrieval():
    """Test successful cache retrieval."""
    mock_cache = AsyncMock()
    mock_cache.pg_fetchrow.return_value = {
        'response': {
            'imdb_id': 'tt0043208',
            'title': 'Test Show',
            'rating': 8.5,
            'vote_count': 50000,
            'reviews': [],
            'trivia': [],
            'source_url': 'http://test.com',
            'scraped_at': datetime.now().isoformat()
        }
    }
    
    scraper = IMDBResearchScraper(cache_manager=mock_cache)
    result = await scraper._get_from_cache("Test Show")
    
    assert result is not None
    assert result.imdb_id == 'tt0043208'
    assert result.rating == 8.5


@pytest.mark.asyncio
async def test_cache_miss_returns_none():
    """Test cache miss returns None."""
    mock_cache = AsyncMock()
    mock_cache.pg_fetchrow.return_value = None
    
    scraper = IMDBResearchScraper(cache_manager=mock_cache)
    result = await scraper._get_from_cache("Nonexistent Show")
    
    assert result is None


@pytest.mark.asyncio
async def test_cache_save():
    """Test successful cache save."""
    mock_cache = AsyncMock()
    
    scraper = IMDBResearchScraper(cache_manager=mock_cache)
    
    data = IMDBShowData(
        imdb_id='tt0043208',
        title='Test Show',
        rating=8.5,
        vote_count=50000
    )
    
    await scraper._save_to_cache("Test Show", data)
    
    # Verify execute was called
    assert mock_cache.pg_execute.called


@pytest.mark.asyncio
async def test_imdb_show_data_defaults():
    """Test IMDBShowData default values."""
    data = IMDBShowData(
        imdb_id='tt0043208',
        title='Test Show'
    )
    
    assert data.rating is None
    assert data.vote_count is None
    assert len(data.reviews) == 0
    assert len(data.trivia) == 0
    assert data.source_url is None

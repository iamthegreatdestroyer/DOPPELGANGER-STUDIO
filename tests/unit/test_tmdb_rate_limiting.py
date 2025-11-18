"""
Unit tests for TMDB Rate Limiting.

Tests in-memory rate limiter with 40 requests per 10 seconds limit.

Copyright (c) 2025. All Rights Reserved. Patent Pending.
"""

import pytest
from unittest.mock import AsyncMock, patch
from datetime import datetime
from src.services.research.tmdb_scraper import TMDBResearchScraper


@pytest.mark.asyncio
async def test_rate_limiter_under_limit():
    """Test rate limiter allows requests under limit."""
    scraper = TMDBResearchScraper("test_key")
    
    # Add 35 requests within the 10-second window (below limit of 40)
    import time
    current_time = time.time()
    # Spread them across 9 seconds (all within 10-second window)
    scraper._request_times = [current_time - (i * 0.25) for i in range(35)]
    
    # Should not sleep since under limit
    await scraper._respect_rate_limit()
    
    # Should have added current request (35 + 1 = 36)
    assert len(scraper._request_times) == 36


@pytest.mark.asyncio
async def test_rate_limiter_at_limit_waits():
    """Test rate limiter waits when at limit."""
    scraper = TMDBResearchScraper("test_key")
    
    # Fill to limit (40 requests)
    import time
    current_time = time.time()
    scraper._request_times = [current_time - i * 0.1 for i in range(40)]
    
    # Mock sleep to verify it's called
    with patch('asyncio.sleep') as mock_sleep:
        await scraper._respect_rate_limit()
        
        # Should have called sleep since at limit
        assert mock_sleep.called


@pytest.mark.asyncio
async def test_rate_limiter_removes_old_entries():
    """Test that old entries are removed from window."""
    scraper = TMDBResearchScraper("test_key")
    
    # Add old requests (11+ seconds ago - outside window)
    import time
    current_time = time.time()
    scraper._request_times = [
        current_time - 15,  # Old - should be removed
        current_time - 12,  # Old - should be removed
        current_time - 5,   # Recent - should stay
        current_time - 2,   # Recent - should stay
    ]
    
    await scraper._respect_rate_limit()
    
    # Should have removed old entries and added new one
    # Only the 2 recent ones + new one = 3
    assert len(scraper._request_times) == 3


@pytest.mark.asyncio
async def test_rate_limiter_simple_usage():
    """Test basic rate limiter usage."""
    scraper = TMDBResearchScraper("test_key")
    
    # Should work without errors
    await scraper._respect_rate_limit()
    assert len(scraper._request_times) == 1
    
    await scraper._respect_rate_limit()
    assert len(scraper._request_times) == 2


@pytest.mark.asyncio
async def test_search_show_with_mock():
    """Test _search_show method with mocked API."""
    from unittest.mock import Mock, MagicMock
    
    mock_response = MagicMock()
    mock_response.status = 200
    mock_response.json = AsyncMock(return_value={
        'results': [{'id': 1234, 'name': 'I Love Lucy'}]
    })
    
    class MockContextManager:
        async def __aenter__(self):
            return mock_response
        
        async def __aexit__(self, *args):
            pass
    
    mock_session = Mock()
    mock_session.get = Mock(return_value=MockContextManager())
    
    scraper = TMDBResearchScraper("test_key")
    scraper.session = mock_session
    
    show_id = await scraper._search_show("I Love Lucy")
    
    assert show_id == 1234
    assert mock_session.get.called


@pytest.mark.asyncio
async def test_search_show_not_found():
    """Test _search_show returns None when not found."""
    from unittest.mock import Mock, MagicMock
    
    mock_response = MagicMock()
    mock_response.status = 200
    mock_response.json = AsyncMock(return_value={'results': []})
    
    class MockContextManager:
        async def __aenter__(self):
            return mock_response
        
        async def __aexit__(self, *args):
            pass
    
    mock_session = Mock()
    mock_session.get = Mock(return_value=MockContextManager())
    
    scraper = TMDBResearchScraper("test_key")
    scraper.session = mock_session
    
    show_id = await scraper._search_show("NonexistentShow12345")
    
    assert show_id is None


@pytest.mark.asyncio
async def test_get_show_details_structure():
    """Test _get_show_details returns correct structure."""
    from unittest.mock import Mock, MagicMock
    
    mock_response = MagicMock()
    mock_response.status = 200
    mock_response.json = AsyncMock(return_value={
        'id': 1234,
        'name': 'I Love Lucy',
        'overview': 'Classic sitcom',
        'vote_average': 8.5,
        'vote_count': 500,
        'popularity': 100.0,
        'first_air_date': '1951-10-15',
        'last_air_date': '1957-05-06',
        'number_of_episodes': 180,
        'number_of_seasons': 6,
        'genres': [{'id': 35, 'name': 'Comedy'}],
        'networks': [{'id': 1, 'name': 'CBS'}],
        'production_companies': [],
        'poster_path': '/poster.jpg',
        'backdrop_path': '/backdrop.jpg',
    })
    
    class MockContextManager:
        async def __aenter__(self):
            return mock_response
        
        async def __aexit__(self, *args):
            pass
    
    mock_session = Mock()
    mock_session.get = Mock(return_value=MockContextManager())
    
    scraper = TMDBResearchScraper("test_key")
    scraper.session = mock_session
    
    details = await scraper._get_show_details(1234)
    
    assert details['name'] == 'I Love Lucy'
    assert details['vote_average'] == 8.5
    assert details['number_of_episodes'] == 180


@pytest.mark.asyncio
async def test_get_credits_structure():
    """Test _get_credits returns cast list."""
    from unittest.mock import Mock, MagicMock
    
    mock_response = MagicMock()
    mock_response.status = 200
    mock_response.json = AsyncMock(return_value={
        'cast': [
            {
                'name': 'Lucille Ball',
                'character': 'Lucy Ricardo',
                'order': 0,
                'profile_path': '/lucy.jpg'
            }
        ]
    })
    
    class MockContextManager:
        async def __aenter__(self):
            return mock_response
        
        async def __aexit__(self, *args):
            pass
    
    mock_session = Mock()
    mock_session.get = Mock(return_value=MockContextManager())
    
    scraper = TMDBResearchScraper("test_key")
    scraper.session = mock_session
    
    credits = await scraper._get_credits(1234)
    
    assert len(credits['cast']) == 1
    assert credits['cast'][0]['name'] == 'Lucille Ball'

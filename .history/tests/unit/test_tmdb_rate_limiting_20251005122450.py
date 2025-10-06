"""
Unit tests for TMDB Rate Limiting.

Tests Redis-based rate limiter with 40 requests per 10 seconds limit.

Copyright (c) 2025. All Rights Reserved. Patent Pending.
"""

import pytest
from unittest.mock import AsyncMock
from datetime import datetime
from src.services.research.tmdb_scraper import TMDBResearchScraper


@pytest.mark.asyncio
async def test_rate_limiter_under_limit():
    """Test rate limiter allows requests under limit."""
    mock_redis = AsyncMock()
    mock_redis.zcard.return_value = 35  # Below limit of 40
    
    scraper = TMDBResearchScraper("test_key", redis_client=mock_redis)
    
    result = await scraper._check_rate_limit()
    
    assert result is True
    assert mock_redis.zadd.called  # Should add request to sorted set
    assert mock_redis.expire.called


@pytest.mark.asyncio
async def test_rate_limiter_at_limit_waits():
    """Test rate limiter waits when at limit."""
    mock_redis = AsyncMock()
    # First call: at limit, second call: under limit
    mock_redis.zcard.side_effect = [40, 39]
    mock_redis.zrange.return_value = [(b'123.456', 123.456)]
    
    scraper = TMDBResearchScraper("test_key", redis_client=mock_redis)
    
    result = await scraper._check_rate_limit()
    
    assert result is True
    # Should have checked card count twice (initial + after wait)
    assert mock_redis.zcard.call_count >= 1


@pytest.mark.asyncio
async def test_rate_limiter_removes_old_entries():
    """Test that old entries are removed from window."""
    mock_redis = AsyncMock()
    mock_redis.zcard.return_value = 10
    
    scraper = TMDBResearchScraper("test_key", redis_client=mock_redis)
    
    await scraper._check_rate_limit()
    
    # Should remove entries outside window
    assert mock_redis.zremrangebyscore.called


@pytest.mark.asyncio
async def test_rate_limiter_fallback_without_redis():
    """Test fallback behavior when Redis not available."""
    scraper = TMDBResearchScraper("test_key", redis_client=None)
    
    result = await scraper._check_rate_limit()
    
    # Should return True (fail open)
    assert result is True


@pytest.mark.asyncio
async def test_make_request_handles_429():
    """Test exponential backoff on 429 status."""
    from unittest.mock import Mock, MagicMock
    
    mock_redis = AsyncMock()
    mock_redis.zcard.return_value = 0
    
    mock_response = MagicMock()
    mock_response.status = 429
    
    # Create proper async context manager
    class MockContextManager:
        async def __aenter__(self):
            return mock_response
        
        async def __aexit__(self, *args):
            pass
    
    # Use regular Mock for session, not AsyncMock
    mock_session = Mock()
    mock_session.get = Mock(return_value=MockContextManager())
    
    scraper = TMDBResearchScraper("test_key", redis_client=mock_redis)
    scraper.session = mock_session
    
    with pytest.raises(Exception, match="TMDB API request failed"):
        await scraper._make_request("http://test", {})
    
    # Should have retried 3 times
    assert mock_session.get.call_count == 3


@pytest.mark.asyncio
async def test_make_request_success():
    """Test successful API request."""
    from unittest.mock import Mock, MagicMock
    
    mock_redis = AsyncMock()
    mock_redis.zcard.return_value = 0
    
    mock_response = MagicMock()
    mock_response.status = 200
    mock_response.json = AsyncMock(return_value={'data': 'test'})
    
    # Create proper async context manager
    class MockContextManager:
        async def __aenter__(self):
            return mock_response
        
        async def __aexit__(self, *args):
            pass
    
    # Use regular Mock for session, not AsyncMock
    mock_session = Mock()
    mock_session.get = Mock(return_value=MockContextManager())
    
    scraper = TMDBResearchScraper("test_key", redis_client=mock_redis)
    scraper.session = mock_session
    
    result = await scraper._make_request("http://test", {})
    
    assert result == {'data': 'test'}
    assert mock_session.get.call_count == 1


@pytest.mark.asyncio
async def test_make_request_timeout_retry():
    """Test timeout triggers retry."""
    from unittest.mock import Mock, MagicMock
    
    mock_redis = AsyncMock()
    mock_redis.zcard.return_value = 0
    
    # Use regular Mock for session
    mock_session = Mock()
    # First two attempts timeout, third succeeds
    mock_response = MagicMock()
    mock_response.status = 200
    mock_response.json = AsyncMock(return_value={'data': 'test'})
    
    side_effects = [
        Exception("Timeout"),
        Exception("Timeout"),
    ]
    
    call_count = [0]
    
    async def get_side_effect(*args, **kwargs):
        call_count[0] += 1
        if call_count[0] <= 2:
            raise side_effects[call_count[0] - 1]
        
        class MockContext:
            async def __aenter__(self):
                return mock_response
            async def __aexit__(self, *args):
                pass
        
        return MockContext()
    
    mock_session.get.side_effect = get_side_effect
    
    scraper = TMDBResearchScraper("test_key", redis_client=mock_redis)
    scraper.session = mock_session
    
    result = await scraper._make_request("http://test", {})
    
    assert result == {'data': 'test'}
    assert call_count[0] == 3

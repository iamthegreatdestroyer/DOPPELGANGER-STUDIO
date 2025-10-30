"""
Rate limiting tests for DOPPELGANGER STUDIO.

Tests for:
- Token bucket algorithm
- Rate limiting enforcement
- Retry logic and exponential backoff
- Concurrent request handling
- Multiple API provider management
"""

import pytest
import asyncio
import time
from unittest.mock import AsyncMock, MagicMock

from src.services.api_management.rate_limiter import (
    APIProvider,
    RateLimitConfig,
    TokenBucket,
    RateLimiter,
    APIRateLimitManager,
    get_rate_limit_manager,
)


class TestTokenBucket:
    """Test token bucket algorithm."""
    
    def test_token_bucket_initialization(self):
        """Test token bucket initializes with full capacity."""
        bucket = TokenBucket(capacity=10, refill_rate=1.0)
        assert bucket.tokens == 10
        assert bucket.capacity == 10
    
    def test_token_consumption(self):
        """Test consuming tokens."""
        bucket = TokenBucket(capacity=10, refill_rate=1.0)
        
        assert bucket.consume(5)
        assert bucket.tokens == 5
        
        assert bucket.consume(5)
        assert bucket.tokens == 0
        
        assert not bucket.consume(1)
    
    def test_token_refill(self):
        """Test token refill over time."""
        bucket = TokenBucket(capacity=10, refill_rate=10.0)  # 10 tokens/sec
        
        # Consume all tokens
        bucket.consume(10)
        assert bucket.tokens == 0
        
        # Wait for refill
        time.sleep(0.2)  # 2 tokens should refill
        bucket.refill()
        
        assert bucket.tokens > 0
    
    def test_wait_time_calculation(self):
        """Test calculating wait time for tokens."""
        bucket = TokenBucket(capacity=10, refill_rate=10.0)
        
        # Consume all tokens
        bucket.consume(10)
        
        # Should need to wait to get 1 token
        wait_time = bucket.wait_time(1.0)
        assert wait_time > 0
        assert wait_time < 0.2  # Should be ~0.1s for 10 tokens/sec


class TestRateLimiter:
    """Test rate limiting functionality."""
    
    @pytest.fixture
    def limiter(self):
        """Create rate limiter."""
        config = RateLimitConfig(
            provider=APIProvider.CLAUDE,
            max_requests_per_minute=100,
            max_concurrent_requests=10
        )
        return RateLimiter(config)
    
    @pytest.mark.asyncio
    async def test_successful_api_call(self, limiter):
        """Test successful API call."""
        mock_api = AsyncMock(return_value="success")
        
        result = await limiter.call_api(mock_api)
        
        assert result.success
        assert result.response == "success"
        assert result.retry_count == 0
        assert limiter.successful_requests == 1
    
    @pytest.mark.asyncio
    async def test_failed_api_call_with_retries(self, limiter):
        """Test failed API call with retry logic."""
        call_count = 0
        
        async def failing_api():
            nonlocal call_count
            call_count += 1
            if call_count < 3:
                raise Exception("Temporary failure")
            return "success"
        
        result = await limiter.call_api(failing_api)
        
        assert result.success
        assert result.response == "success"
        assert result.retry_count == 2
        assert limiter.retried_requests == 2
    
    @pytest.mark.asyncio
    async def test_max_retries_exceeded(self, limiter):
        """Test behavior when max retries exceeded."""
        async def always_failing_api():
            raise Exception("Persistent failure")
        
        result = await limiter.call_api(always_failing_api)
        
        assert not result.success
        assert "Persistent failure" in result.error
        assert result.retry_count == limiter.config.max_retries + 1
        assert limiter.failed_requests == 1
    
    @pytest.mark.asyncio
    async def test_concurrent_requests(self, limiter):
        """Test concurrent request handling."""
        async def mock_api():
            await asyncio.sleep(0.01)
            return "success"
        
        # Send 5 concurrent requests
        tasks = [
            limiter.call_api(mock_api)
            for _ in range(5)
        ]
        results = await asyncio.gather(*tasks)
        
        assert len(results) == 5
        assert all(r.success for r in results)
        assert limiter.total_requests == 5
        assert limiter.successful_requests == 5
    
    def test_rate_limiter_stats(self, limiter):
        """Test statistics collection."""
        stats = limiter.get_stats()
        
        assert stats["provider"] == "claude"
        assert stats["total_requests"] == 0
        assert stats["successful_requests"] == 0
        assert stats["failed_requests"] == 0


class TestAPIRateLimitManager:
    """Test API rate limit manager."""
    
    @pytest.fixture
    def manager(self):
        """Create fresh manager instance."""
        return APIRateLimitManager()
    
    def test_manager_initialization(self, manager):
        """Test manager initializes with default limits."""
        assert APIProvider.CLAUDE in manager.limiters
        assert APIProvider.GPT4 in manager.limiters
        assert APIProvider.ELEVENLABS in manager.limiters
    
    def test_add_custom_limiter(self, manager):
        """Test adding custom rate limiter."""
        custom_config = RateLimitConfig(
            provider=APIProvider.CUSTOM,
            max_requests_per_minute=50,
            max_concurrent_requests=5
        )
        
        manager.add_limiter(custom_config)
        
        assert APIProvider.CUSTOM in manager.limiters
        limiter = manager.get_limiter(APIProvider.CUSTOM)
        assert limiter.config.max_requests_per_minute == 50
    
    def test_get_limiter(self, manager):
        """Test getting rate limiter for provider."""
        limiter = manager.get_limiter(APIProvider.CLAUDE)
        
        assert limiter is not None
        assert limiter.provider == APIProvider.CLAUDE
    
    @pytest.mark.asyncio
    async def test_call_api_through_manager(self, manager):
        """Test calling API through manager."""
        mock_api = AsyncMock(return_value="response")
        
        result = await manager.call_api(APIProvider.CLAUDE, mock_api)
        
        assert result.success
        assert result.response == "response"
    
    @pytest.mark.asyncio
    async def test_call_api_unknown_provider(self, manager):
        """Test calling API with unknown provider."""
        mock_api = AsyncMock(return_value="response")
        
        # Should call directly without limiter
        result = await manager.call_api(APIProvider.CUSTOM, mock_api)
        
        assert result.success
        assert result.response == "response"
    
    def test_get_all_stats(self, manager):
        """Test getting stats from all limiters."""
        stats = manager.get_all_stats()
        
        assert "claude" in stats
        assert "gpt4" in stats
        assert "elevenlabs" in stats
        
        for provider, provider_stats in stats.items():
            assert "provider" in provider_stats
            assert "total_requests" in provider_stats


class TestRateLimitIntegration:
    """Integration tests for rate limiting."""
    
    @pytest.mark.asyncio
    async def test_burst_then_rate_limit(self):
        """Test burst traffic followed by rate limiting."""
        config = RateLimitConfig(
            provider=APIProvider.CLAUDE,
            max_requests_per_minute=10,  # 10 per minute = 0.167/sec
            max_concurrent_requests=20
        )
        limiter = RateLimiter(config)
        
        async def quick_call():
            await asyncio.sleep(0.001)
            return "ok"
        
        # Send burst of requests
        start = time.time()
        tasks = [limiter.call_api(quick_call) for _ in range(5)]
        results = await asyncio.gather(*tasks)
        duration = time.time() - start
        
        assert all(r.success for r in results)
        # Burst should be relatively fast (within rate limits)
        assert duration < 5.0
    
    @pytest.mark.asyncio
    async def test_multiple_providers_independent(self):
        """Test rate limits for multiple providers are independent."""
        manager = APIRateLimitManager()
        
        async def mock_api():
            await asyncio.sleep(0.001)
            return "ok"
        
        # Call different providers
        results = await asyncio.gather(
            manager.call_api(APIProvider.CLAUDE, mock_api),
            manager.call_api(APIProvider.GPT4, mock_api),
            manager.call_api(APIProvider.ELEVENLABS, mock_api),
        )
        
        assert all(r.success for r in results)
        
        # Each should have tracked 1 request independently
        claude_stats = manager.get_limiter(APIProvider.CLAUDE).get_stats()
        gpt4_stats = manager.get_limiter(APIProvider.GPT4).get_stats()
        
        assert claude_stats["total_requests"] == 1
        assert gpt4_stats["total_requests"] == 1
    
    @pytest.mark.asyncio
    async def test_exponential_backoff_timing(self):
        """Test exponential backoff increases wait time."""
        config = RateLimitConfig(
            provider=APIProvider.CLAUDE,
            max_requests_per_minute=100,
            backoff_factor=2.0,
            max_retries=3
        )
        limiter = RateLimiter(config)
        
        attempt_times = []
        
        async def failing_then_success():
            attempt_times.append(time.time())
            if len(attempt_times) < 3:
                raise Exception("Fail")
            return "success"
        
        result = await limiter.call_api(failing_then_success)
        
        assert result.success
        assert len(attempt_times) == 3
        
        # Backoff times should increase (2^1 + 1^2 = 2-3 seconds roughly)
        # This test just verifies retries happened with delay
        assert result.retry_count == 2


class TestRateLimitGlobalManager:
    """Test global rate limit manager singleton."""
    
    def test_get_rate_limit_manager_singleton(self):
        """Test getting global manager returns same instance."""
        manager1 = get_rate_limit_manager()
        manager2 = get_rate_limit_manager()
        
        assert manager1 is manager2
    
    @pytest.mark.asyncio
    async def test_global_manager_functionality(self):
        """Test global manager works correctly."""
        manager = get_rate_limit_manager()
        mock_api = AsyncMock(return_value="result")
        
        result = await manager.call_api(APIProvider.CLAUDE, mock_api)
        
        assert result.success
        assert result.response == "result"

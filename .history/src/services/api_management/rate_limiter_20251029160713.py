"""
Copyright (c) 2025 DOPPELGANGER STUDIO. All Rights Reserved.

API Rate Limiting Management for DOPPELGANGER STUDIO.

Handles rate limiting for:
- Claude API (Anthropic)
- GPT-4 API (OpenAI)
- External APIs
- Custom APIs

Features:
- Token bucket algorithm
- Exponential backoff with jitter
- Request queuing
- Retry logic
- Per-API rate limit tracking
"""

import asyncio
import time
import logging
from dataclasses import dataclass, field
from typing import Dict, Optional, Callable, Any
from enum import Enum
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)


class APIProvider(Enum):
    """Supported API providers."""
    CLAUDE = "claude"
    GPT4 = "gpt4"
    ELEVENLABS = "elevenlabs"
    CUSTOM = "custom"


@dataclass
class RateLimitConfig:
    """Rate limit configuration for an API."""
    provider: APIProvider
    max_requests_per_minute: int
    max_tokens_per_minute: int = 0
    max_concurrent_requests: int = 10
    backoff_factor: float = 2.0
    max_retries: int = 5
    timeout_seconds: float = 30.0


@dataclass
class TokenBucket:
    """Token bucket for rate limiting."""
    capacity: float
    tokens: float = field(init=False)
    last_refill: float = field(init=False)
    refill_rate: float  # tokens per second
    
    def __post_init__(self):
        self.tokens = self.capacity
        self.last_refill = time.time()
    
    def refill(self):
        """Refill tokens based on elapsed time."""
        now = time.time()
        elapsed = now - self.last_refill
        tokens_to_add = elapsed * self.refill_rate
        self.tokens = min(self.capacity, self.tokens + tokens_to_add)
        self.last_refill = now
    
    def consume(self, tokens: float = 1.0) -> bool:
        """Try to consume tokens. Returns True if successful."""
        self.refill()
        if self.tokens >= tokens:
            self.tokens -= tokens
            return True
        return False
    
    def wait_time(self, tokens: float = 1.0) -> float:
        """Calculate wait time to get tokens."""
        self.refill()
        if self.tokens >= tokens:
            return 0.0
        tokens_needed = tokens - self.tokens
        return tokens_needed / self.refill_rate


@dataclass
class APICallResult:
    """Result of an API call attempt."""
    success: bool
    response: Optional[Any] = None
    error: Optional[str] = None
    retry_count: int = 0
    duration_seconds: float = 0.0
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())


class RateLimiter:
    """Manage rate limiting for API calls."""
    
    def __init__(self, config: RateLimitConfig):
        """Initialize rate limiter."""
        self.config = config
        self.provider = config.provider
        
        # Token bucket: requests per minute -> tokens per second
        requests_per_second = config.max_requests_per_minute / 60
        self.bucket = TokenBucket(
            capacity=config.max_requests_per_minute / 60 * 5,  # 5 second buffer
            refill_rate=requests_per_second
        )
        
        # Concurrent request tracking
        self.active_requests = 0
        self.semaphore = asyncio.Semaphore(config.max_concurrent_requests)
        
        # Statistics
        self.total_requests = 0
        self.successful_requests = 0
        self.failed_requests = 0
        self.retried_requests = 0
        
        logger.info(f"Rate limiter initialized for {self.provider.value}: "
                   f"{config.max_requests_per_minute} req/min")
    
    async def acquire(self):
        """Acquire slot for API request."""
        await self.semaphore.acquire()
        self.active_requests += 1
    
    def release(self):
        """Release slot after API request."""
        self.active_requests -= 1
        self.semaphore.release()
    
    async def wait_if_needed(self):
        """Wait if rate limit would be exceeded."""
        wait_time = self.bucket.wait_time(1.0)
        if wait_time > 0:
            logger.debug(f"Rate limit: waiting {wait_time:.2f}s for {self.provider.value}")
            await asyncio.sleep(wait_time)
    
    async def call_api(self, 
                      api_func: Callable,
                      *args,
                      **kwargs) -> APICallResult:
        """
        Execute API call with rate limiting and retry logic.
        
        Args:
            api_func: Async function to call
            *args: Positional arguments for api_func
            **kwargs: Keyword arguments for api_func
        
        Returns:
            APICallResult with success status and response/error
        """
        self.total_requests += 1
        retry_count = 0
        last_error = None
        
        while retry_count <= self.config.max_retries:
            try:
                # Acquire slot
                await self.acquire()
                
                # Wait for rate limit
                await self.wait_if_needed()
                
                # Consume token
                if not self.bucket.consume(1.0):
                    await asyncio.sleep(0.1)
                    continue
                
                # Execute API call
                start_time = time.time()
                try:
                    response = await asyncio.wait_for(
                        api_func(*args, **kwargs),
                        timeout=self.config.timeout_seconds
                    )
                    duration = time.time() - start_time
                    self.successful_requests += 1
                    
                    return APICallResult(
                        success=True,
                        response=response,
                        retry_count=retry_count,
                        duration_seconds=duration
                    )
                except asyncio.TimeoutError:
                    duration = time.time() - start_time
                    raise Exception(f"API call timeout after {duration:.1f}s")
                
            except Exception as e:
                last_error = str(e)
                retry_count += 1
                
                if retry_count <= self.config.max_retries:
                    # Exponential backoff with jitter
                    backoff_time = (
                        (self.config.backoff_factor ** retry_count) +
                        (time.time() % 1)  # Add jitter
                    )
                    logger.warning(
                        f"API call failed for {self.provider.value} "
                        f"(attempt {retry_count}/{self.config.max_retries}): {last_error} "
                        f"- Retrying in {backoff_time:.1f}s"
                    )
                    await asyncio.sleep(backoff_time)
                    self.retried_requests += 1
            
            finally:
                self.release()
        
        # All retries exhausted
        self.failed_requests += 1
        return APICallResult(
            success=False,
            error=last_error,
            retry_count=retry_count
        )
    
    def get_stats(self) -> Dict[str, Any]:
        """Get rate limiter statistics."""
        success_rate = (
            (self.successful_requests / self.total_requests * 100)
            if self.total_requests > 0 else 0
        )
        
        return {
            "provider": self.provider.value,
            "total_requests": self.total_requests,
            "successful_requests": self.successful_requests,
            "failed_requests": self.failed_requests,
            "retried_requests": self.retried_requests,
            "success_rate": round(success_rate, 1),
            "active_requests": self.active_requests,
            "available_tokens": round(self.bucket.tokens, 2),
        }
    
    def print_stats(self):
        """Print statistics."""
        stats = self.get_stats()
        print(f"\n{'='*60}")
        print(f"Rate Limiter Stats: {stats['provider'].upper()}")
        print(f"{'='*60}")
        print(f"Total Requests:     {stats['total_requests']}")
        print(f"Successful:         {stats['successful_requests']}")
        print(f"Failed:             {stats['failed_requests']}")
        print(f"Retried:            {stats['retried_requests']}")
        print(f"Success Rate:       {stats['success_rate']}%")
        print(f"Active:             {stats['active_requests']}")
        print(f"Available Tokens:   {stats['available_tokens']}")
        print(f"{'='*60}")


class APIRateLimitManager:
    """Manage rate limiting for multiple API providers."""
    
    def __init__(self):
        """Initialize rate limit manager."""
        self.limiters: Dict[APIProvider, RateLimiter] = {}
        self._initialize_default_limits()
    
    def _initialize_default_limits(self):
        """Initialize default rate limits for known APIs."""
        # Claude API: 100 requests/min (production) or higher in dev
        self.add_limiter(RateLimitConfig(
            provider=APIProvider.CLAUDE,
            max_requests_per_minute=100,
            max_concurrent_requests=10
        ))
        
        # GPT-4 API: 60 requests/min (can be higher with quota)
        self.add_limiter(RateLimitConfig(
            provider=APIProvider.GPT4,
            max_requests_per_minute=60,
            max_concurrent_requests=8
        ))
        
        # ElevenLabs API: 10 requests/sec = 600/min
        self.add_limiter(RateLimitConfig(
            provider=APIProvider.ELEVENLABS,
            max_requests_per_minute=600,
            max_concurrent_requests=15
        ))
    
    def add_limiter(self, config: RateLimitConfig):
        """Add or update a rate limiter."""
        self.limiters[config.provider] = RateLimiter(config)
    
    def get_limiter(self, provider: APIProvider) -> Optional[RateLimiter]:
        """Get rate limiter for provider."""
        return self.limiters.get(provider)
    
    async def call_api(self, 
                      provider: APIProvider,
                      api_func: Callable,
                      *args,
                      **kwargs) -> APICallResult:
        """Execute API call with rate limiting."""
        limiter = self.get_limiter(provider)
        if not limiter:
            # No limiter configured, call directly
            try:
                response = await api_func(*args, **kwargs)
                return APICallResult(success=True, response=response)
            except Exception as e:
                return APICallResult(success=False, error=str(e))
        
        return await limiter.call_api(api_func, *args, **kwargs)
    
    def get_all_stats(self) -> Dict[str, Any]:
        """Get stats from all limiters."""
        return {
            provider.value: limiter.get_stats()
            for provider, limiter in self.limiters.items()
        }
    
    def print_all_stats(self):
        """Print stats from all limiters."""
        for provider, limiter in self.limiters.items():
            limiter.print_stats()


# Global singleton instance
_manager_instance: Optional[APIRateLimitManager] = None


def get_rate_limit_manager() -> APIRateLimitManager:
    """Get global rate limit manager instance."""
    global _manager_instance
    if _manager_instance is None:
        _manager_instance = APIRateLimitManager()
    return _manager_instance

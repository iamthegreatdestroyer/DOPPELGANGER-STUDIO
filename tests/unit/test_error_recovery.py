"""
Unit tests for error recovery system.

Copyright (c) 2025. All Rights Reserved. Patent Pending.
"""

import pytest
import asyncio
from src.services.creative.error_recovery import (
    ErrorRecoverySystem,
    RecoveryStrategy,
    ErrorSeverity,
    RecoveryResult
)


class TestErrorRecoverySystem:
    """Test error recovery functionality."""
    
    def setup_method(self):
        """Setup test fixtures."""
        self.recovery = ErrorRecoverySystem(max_retries=3, exponential_backoff=True)
    
    @pytest.mark.asyncio
    async def test_successful_operation_no_retry(self):
        """Test successful operation requires no retry."""
        async def successful_op():
            return "success"
        
        result = await self.recovery.execute_with_recovery(
            successful_op,
            strategies=[RecoveryStrategy.RETRY]
        )
        
        assert result.success
        assert result.result == "success"
        assert result.strategy_used == RecoveryStrategy.RETRY
    
    @pytest.mark.asyncio
    async def test_retry_on_failure(self):
        """Test retry logic on transient failures."""
        call_count = 0
        
        async def flaky_op():
            nonlocal call_count
            call_count += 1
            if call_count < 2:
                raise ValueError("Transient error")
            return "success"
        
        result = await self.recovery.execute_with_recovery(
            flaky_op,
            strategies=[RecoveryStrategy.RETRY],
            max_retries=3
        )
        
        assert result.success
        assert result.result == "success"
        assert call_count == 2  # Failed once, succeeded second time
    
    @pytest.mark.asyncio
    async def test_fallback_on_persistent_failure(self):
        """Test fallback when retries exhausted."""
        async def failing_op():
            raise RuntimeError("Always fails")
        
        def fallback():
            return "fallback_result"
        
        result = await self.recovery.execute_with_recovery(
            failing_op,
            strategies=[RecoveryStrategy.RETRY, RecoveryStrategy.FALLBACK],
            fallback_fn=fallback,
            max_retries=2
        )
        
        assert result.success
        assert result.result == "fallback_result"
        assert result.strategy_used == RecoveryStrategy.FALLBACK
        assert result.degraded_mode
    
    @pytest.mark.asyncio
    async def test_cache_recovery_strategy(self):
        """Test cache-based recovery."""
        # Set cached value
        cache_key = "test_key"
        self.recovery._cache_result(cache_key, "cached_value")
        
        async def failing_op():
            raise ValueError("Failed")
        
        result = await self.recovery.execute_with_recovery(
            failing_op,
            strategies=[RecoveryStrategy.CACHE],
            cache_key=cache_key
        )
        
        assert result.success
        assert result.result == "cached_value"
        assert result.strategy_used == RecoveryStrategy.CACHE
    
    @pytest.mark.asyncio
    async def test_skip_strategy(self):
        """Test skip strategy."""
        async def failing_op():
            raise ValueError("Failed")
        
        result = await self.recovery.execute_with_recovery(
            failing_op,
            strategies=[RecoveryStrategy.SKIP]
        )
        
        assert result.success  # Skip counts as success
        assert result.result is None
        assert result.strategy_used == RecoveryStrategy.SKIP
    
    @pytest.mark.asyncio
    async def test_degrade_strategy(self):
        """Test degraded mode strategy."""
        async def failing_op():
            raise ValueError("Failed")
        
        result = await self.recovery.execute_with_recovery(
            failing_op,
            strategies=[RecoveryStrategy.DEGRADE]
        )
        
        assert result.success
        assert result.degraded_mode
        assert result.strategy_used == RecoveryStrategy.DEGRADE
    
    def test_cache_expiration(self):
        """Test cache expiration."""
        cache_key = "expiring_key"
        self.recovery._cache_result(cache_key, "value")
        
        # Should exist immediately
        cached = self.recovery._get_cached_result(cache_key, max_age_seconds=10)
        assert cached == "value"
        
        # Should expire with zero max age
        cached = self.recovery._get_cached_result(cache_key, max_age_seconds=0)
        assert cached is None
    
    def test_error_statistics(self):
        """Test error statistics tracking."""
        self.recovery._record_error("test_component", "test_op")
        self.recovery._record_error("test_component", "test_op")
        self.recovery._record_recovery("test_component", "test_op")
        
        stats = self.recovery.get_error_statistics()
        
        assert "test_component.test_op" in stats["errors"]
        assert stats["errors"]["test_component.test_op"] == 2
        assert stats["recoveries"]["test_component.test_op"] == 1

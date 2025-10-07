"""
Copyright (c) 2025 DOPPELGANGER STUDIO. All Rights Reserved.

Comprehensive tests for performance monitoring system.
"""

import pytest
import asyncio
import time
from datetime import datetime
from unittest.mock import Mock, patch

from src.services.monitoring.performance_monitor import (
    OperationMetrics,
    PerformanceMetrics,
    PerformanceMonitor,
    get_performance_monitor,
    monitor_performance,
    monitor_async_performance,
)


# ============================================================================
# TEST OPERATION METRICS
# ============================================================================

class TestOperationMetrics:
    """Test suite for OperationMetrics dataclass."""
    
    def test_operation_metrics_creation(self):
        """Test creating operation metrics."""
        start = datetime.now()
        op = OperationMetrics(
            operation_name="test_operation",
            start_time=start
        )
        
        assert op.operation_name == "test_operation"
        assert op.start_time == start
        assert op.end_time is None
        assert op.duration_seconds == 0.0
        assert op.success is True
        assert op.error is None
        assert op.metadata == {}
    
    def test_operation_finish(self):
        """Test finishing an operation."""
        start = datetime.now()
        op = OperationMetrics(
            operation_name="test_operation",
            start_time=start
        )
        
        # Small delay
        time.sleep(0.1)
        
        op.finish(success=True)
        
        assert op.end_time is not None
        assert op.duration_seconds > 0.0
        assert op.duration_seconds >= 0.1
        assert op.success is True
        assert op.error is None
    
    def test_operation_finish_with_error(self):
        """Test finishing an operation with error."""
        start = datetime.now()
        op = OperationMetrics(
            operation_name="test_operation",
            start_time=start
        )
        
        op.finish(success=False, error="Test error message")
        
        assert op.end_time is not None
        assert op.duration_seconds >= 0.0
        assert op.success is False
        assert op.error == "Test error message"
    
    def test_operation_to_dict(self):
        """Test converting operation to dictionary."""
        start = datetime.now()
        op = OperationMetrics(
            operation_name="test_operation",
            start_time=start,
            metadata={"key": "value"}
        )
        op.finish(success=True)
        
        result = op.to_dict()
        
        assert result["operation_name"] == "test_operation"
        assert result["start_time"] == start.isoformat()
        assert result["end_time"] is not None
        assert result["duration_seconds"] >= 0.0
        assert result["success"] is True
        assert result["error"] is None
        assert result["metadata"] == {"key": "value"}


# ============================================================================
# TEST PERFORMANCE METRICS
# ============================================================================

class TestPerformanceMetrics:
    """Test suite for PerformanceMetrics dataclass."""
    
    def test_performance_metrics_creation(self):
        """Test creating performance metrics."""
        metrics = PerformanceMetrics(session_id="test_session")
        
        assert metrics.session_id == "test_session"
        assert metrics.start_time is not None
        assert metrics.end_time is None
        assert metrics.total_duration_seconds == 0.0
        assert metrics.operations == []
        assert metrics.cache_hits == 0
        assert metrics.cache_misses == 0
        assert metrics.cache_hit_rate == 0.0
        assert metrics.api_calls == 0
        assert metrics.api_errors == 0
        assert metrics.total_tokens_used == 0
    
    def test_metrics_finish(self):
        """Test finishing metrics session."""
        metrics = PerformanceMetrics(session_id="test_session")
        
        # Add some operations
        op1 = OperationMetrics(
            operation_name="operation_1",
            start_time=datetime.now()
        )
        time.sleep(0.05)
        op1.finish()
        metrics.add_operation(op1)
        
        op2 = OperationMetrics(
            operation_name="operation_2",
            start_time=datetime.now()
        )
        time.sleep(0.05)
        op2.finish()
        metrics.add_operation(op2)
        
        # Finish session
        time.sleep(0.1)
        metrics.finish()
        
        assert metrics.end_time is not None
        assert metrics.total_duration_seconds > 0.0
        assert len(metrics.operations) == 2
        assert len(metrics.slowest_operations) <= 5
    
    def test_cache_hit_rate_calculation(self):
        """Test cache hit rate calculation."""
        metrics = PerformanceMetrics(session_id="test_session")
        
        # Record cache hits and misses
        metrics.record_cache_hit()
        metrics.record_cache_hit()
        metrics.record_cache_hit()
        metrics.record_cache_miss()
        
        metrics.finish()
        
        assert metrics.cache_hits == 3
        assert metrics.cache_misses == 1
        assert metrics.cache_hit_rate == 0.75
    
    def test_zero_cache_operations(self):
        """Test with no cache operations."""
        metrics = PerformanceMetrics(session_id="test_session")
        metrics.finish()
        
        assert metrics.cache_hit_rate == 0.0
    
    def test_api_call_tracking(self):
        """Test API call tracking."""
        metrics = PerformanceMetrics(session_id="test_session")
        
        metrics.record_api_call(tokens_used=100, cost=0.01)
        metrics.record_api_call(tokens_used=200, cost=0.02)
        metrics.record_api_call(tokens_used=50, cost=0.005, error=True)
        
        assert metrics.api_calls == 3
        assert metrics.api_errors == 1
        assert metrics.total_tokens_used == 350
        assert metrics.estimated_api_cost == pytest.approx(0.035, rel=1e-6)
    
    def test_bottleneck_detection(self):
        """Test bottleneck detection for slow operations."""
        metrics = PerformanceMetrics(session_id="test_session")
        
        # Create fast operation
        fast_op = OperationMetrics(
            operation_name="fast_operation",
            start_time=datetime.now()
        )
        time.sleep(0.02)
        fast_op.finish()
        metrics.add_operation(fast_op)
        
        # Create slow operation (will be >20% of total)
        slow_op = OperationMetrics(
            operation_name="slow_operation",
            start_time=datetime.now()
        )
        time.sleep(0.3)  # Much longer to ensure >20%
        slow_op.finish()
        metrics.add_operation(slow_op)
        
        metrics.finish()
        
        # Slow operation should be detected as bottleneck
        assert len(metrics.bottleneck_warnings) > 0
        assert "slow_operation" in metrics.bottleneck_warnings[0]
    
    def test_slowest_operations_tracking(self):
        """Test tracking of slowest operations."""
        metrics = PerformanceMetrics(session_id="test_session")
        
        # Create operations with different durations
        for i in range(7):
            op = OperationMetrics(
                operation_name=f"operation_{i}",
                start_time=datetime.now()
            )
            time.sleep(0.01 * (i + 1))  # Increasing durations
            op.finish()
            metrics.add_operation(op)
        
        metrics.finish()
        
        # Should track top 5 slowest
        assert len(metrics.slowest_operations) == 5
        
        # Should be sorted by duration (slowest first)
        durations = [op.duration_seconds for op in metrics.slowest_operations]
        assert durations == sorted(durations, reverse=True)
    
    def test_to_dict(self):
        """Test converting metrics to dictionary."""
        metrics = PerformanceMetrics(session_id="test_session")
        metrics.record_cache_hit()
        metrics.record_api_call(tokens_used=100, cost=0.01)
        metrics.finish()
        
        result = metrics.to_dict()
        
        assert result["session_id"] == "test_session"
        assert result["cache_hits"] == 1
        assert result["api_calls"] == 1
        assert result["total_tokens_used"] == 100
        assert "start_time" in result
        assert "end_time" in result
    
    def test_get_summary(self):
        """Test generating human-readable summary."""
        metrics = PerformanceMetrics(session_id="test_session")
        
        # Add some data
        metrics.record_cache_hit()
        metrics.record_cache_hit()
        metrics.record_cache_miss()
        metrics.record_api_call(tokens_used=1000, cost=0.05)
        metrics.scenes_generated = 5
        metrics.dialogue_lines_generated = 50
        
        # Create operation
        op = OperationMetrics(
            operation_name="scene_generation",
            start_time=datetime.now()
        )
        time.sleep(0.1)
        op.finish()
        metrics.add_operation(op)
        
        metrics.finish()
        
        summary = metrics.get_summary()
        
        assert "test_session" in summary
        assert "66.7%" in summary  # Cache hit rate
        assert "1,000" in summary  # Token formatting
        assert "$0.0500" in summary  # Cost formatting
        assert "Scenes: 5" in summary
        assert "scene_generation" in summary


# ============================================================================
# TEST PERFORMANCE MONITOR
# ============================================================================

class TestPerformanceMonitor:
    """Test suite for PerformanceMonitor class."""
    
    @pytest.fixture
    def monitor(self):
        """Create fresh monitor for each test."""
        monitor = PerformanceMonitor()
        monitor.enable()
        yield monitor
        monitor.disable()
    
    def test_monitor_creation(self, monitor):
        """Test creating performance monitor."""
        assert monitor.current_session is None
        assert monitor.sessions == []
        assert monitor.is_enabled() is True
    
    def test_start_session(self, monitor):
        """Test starting a monitoring session."""
        session = monitor.start_session("test_session")
        
        assert session is not None
        assert session.session_id == "test_session"
        assert monitor.current_session == session
    
    def test_end_session(self, monitor):
        """Test ending a monitoring session."""
        monitor.start_session("test_session")
        
        # Small delay
        time.sleep(0.1)
        
        session = monitor.end_session()
        
        assert session is not None
        assert session.session_id == "test_session"
        assert session.total_duration_seconds > 0.0
        assert monitor.current_session is None
        assert len(monitor.sessions) == 1
    
    def test_multiple_sessions(self, monitor):
        """Test tracking multiple sessions."""
        # Session 1
        monitor.start_session("session_1")
        time.sleep(0.05)
        session1 = monitor.end_session()
        
        # Session 2
        monitor.start_session("session_2")
        time.sleep(0.05)
        session2 = monitor.end_session()
        
        assert len(monitor.sessions) == 2
        assert monitor.sessions[0].session_id == "session_1"
        assert monitor.sessions[1].session_id == "session_2"
    
    def test_operation_tracking(self, monitor):
        """Test tracking operations."""
        monitor.start_session("test_session")
        
        operation = monitor.start_operation("test_operation")
        time.sleep(0.1)
        monitor.end_operation(operation, success=True)
        
        session = monitor.end_session()
        
        assert len(session.operations) == 1
        assert session.operations[0].operation_name == "test_operation"
        assert session.operations[0].duration_seconds >= 0.1
    
    def test_operation_with_error(self, monitor):
        """Test tracking operation with error."""
        monitor.start_session("test_session")
        
        operation = monitor.start_operation("failing_operation")
        monitor.end_operation(
            operation,
            success=False,
            error="Test error"
        )
        
        session = monitor.end_session()
        
        assert session.operations[0].success is False
        assert session.operations[0].error == "Test error"
    
    def test_operation_metadata(self, monitor):
        """Test tracking operation with metadata."""
        monitor.start_session("test_session")
        
        operation = monitor.start_operation("test_operation")
        monitor.end_operation(
            operation,
            success=True,
            metadata={"scene_number": 5, "characters": ["Lucy", "Ricky"]}
        )
        
        session = monitor.end_session()
        
        metadata = session.operations[0].metadata
        assert metadata["scene_number"] == 5
        assert metadata["characters"] == ["Lucy", "Ricky"]
    
    def test_cache_tracking(self, monitor):
        """Test cache hit/miss tracking."""
        monitor.start_session("test_session")
        
        monitor.record_cache_hit()
        monitor.record_cache_hit()
        monitor.record_cache_miss()
        
        session = monitor.end_session()
        
        assert session.cache_hits == 2
        assert session.cache_misses == 1
        assert session.cache_hit_rate == 2/3
    
    def test_api_tracking(self, monitor):
        """Test API call tracking."""
        monitor.start_session("test_session")
        
        monitor.record_api_call(tokens_used=100, cost=0.01)
        monitor.record_api_call(tokens_used=200, cost=0.02)
        monitor.record_api_call(tokens_used=50, cost=0.005, error=True)
        
        session = monitor.end_session()
        
        assert session.api_calls == 3
        assert session.api_errors == 1
        assert session.total_tokens_used == 350
        assert session.estimated_api_cost == pytest.approx(0.035, rel=1e-6)
    
    def test_get_current_metrics(self, monitor):
        """Test getting current metrics."""
        monitor.start_session("test_session")
        
        current = monitor.get_current_metrics()
        
        assert current is not None
        assert current.session_id == "test_session"
        assert current == monitor.current_session
    
    def test_get_session_history(self, monitor):
        """Test getting session history."""
        monitor.start_session("session_1")
        monitor.end_session()
        
        monitor.start_session("session_2")
        monitor.end_session()
        
        history = monitor.get_session_history()
        
        assert len(history) == 2
        assert history[0].session_id == "session_1"
        assert history[1].session_id == "session_2"
    
    def test_enable_disable(self, monitor):
        """Test enabling and disabling monitoring."""
        assert monitor.is_enabled() is True
        
        monitor.disable()
        assert monitor.is_enabled() is False
        
        # Operations should be no-ops when disabled
        session = monitor.start_session("test_session")
        assert session is None
        
        monitor.enable()
        assert monitor.is_enabled() is True
    
    def test_disabled_tracking(self):
        """Test that tracking is no-op when disabled."""
        monitor = PerformanceMonitor()
        monitor.disable()
        
        session = monitor.start_session("test_session")
        assert session is None
        
        monitor.record_cache_hit()
        monitor.record_api_call(tokens_used=100)
        
        result = monitor.end_session()
        assert result is None


# ============================================================================
# TEST DECORATORS
# ============================================================================

class TestDecorators:
    """Test suite for performance monitoring decorators."""
    
    @pytest.fixture
    def monitor(self):
        """Create fresh monitor for each test."""
        monitor = get_performance_monitor()
        monitor.enable()
        monitor.start_session("test_session")
        yield monitor
        monitor.end_session()
    
    def test_monitor_performance_decorator(self, monitor):
        """Test sync performance monitoring decorator."""
        @monitor_performance("test_function")
        def test_function():
            time.sleep(0.1)
            return "result"
        
        result = test_function()
        
        assert result == "result"
        
        session = monitor.get_current_metrics()
        assert len(session.operations) == 1
        assert session.operations[0].operation_name == "test_function"
        assert session.operations[0].duration_seconds >= 0.1
        assert session.operations[0].success is True
    
    def test_monitor_performance_with_error(self, monitor):
        """Test decorator with function that raises error."""
        @monitor_performance("failing_function")
        def failing_function():
            raise ValueError("Test error")
        
        with pytest.raises(ValueError, match="Test error"):
            failing_function()
        
        session = monitor.get_current_metrics()
        assert len(session.operations) == 1
        assert session.operations[0].success is False
        assert "Test error" in session.operations[0].error
    
    def test_monitor_performance_default_name(self, monitor):
        """Test decorator without explicit name."""
        @monitor_performance()
        def my_function():
            return "result"
        
        result = my_function()
        
        assert result == "result"
        
        session = monitor.get_current_metrics()
        assert session.operations[0].operation_name == "my_function"
    
    @pytest.mark.asyncio
    async def test_monitor_async_performance_decorator(self, monitor):
        """Test async performance monitoring decorator."""
        @monitor_async_performance("async_test_function")
        async def async_test_function():
            await asyncio.sleep(0.1)
            return "async_result"
        
        result = await async_test_function()
        
        assert result == "async_result"
        
        session = monitor.get_current_metrics()
        assert len(session.operations) == 1
        assert session.operations[0].operation_name == "async_test_function"
        assert session.operations[0].duration_seconds >= 0.1
        assert session.operations[0].success is True
    
    @pytest.mark.asyncio
    async def test_monitor_async_performance_with_error(self, monitor):
        """Test async decorator with function that raises error."""
        @monitor_async_performance("failing_async_function")
        async def failing_async_function():
            await asyncio.sleep(0.01)
            raise ValueError("Async test error")
        
        with pytest.raises(ValueError, match="Async test error"):
            await failing_async_function()
        
        session = monitor.get_current_metrics()
        assert len(session.operations) == 1
        assert session.operations[0].success is False
        assert "Async test error" in session.operations[0].error
    
    @pytest.mark.asyncio
    async def test_monitor_async_performance_default_name(self, monitor):
        """Test async decorator without explicit name."""
        @monitor_async_performance()
        async def my_async_function():
            await asyncio.sleep(0.01)
            return "result"
        
        result = await my_async_function()
        
        assert result == "result"
        
        session = monitor.get_current_metrics()
        assert session.operations[0].operation_name == "my_async_function"


# ============================================================================
# TEST GLOBAL MONITOR
# ============================================================================

class TestGlobalMonitor:
    """Test suite for global monitor singleton."""
    
    def test_get_performance_monitor_singleton(self):
        """Test that get_performance_monitor returns same instance."""
        monitor1 = get_performance_monitor()
        monitor2 = get_performance_monitor()
        
        assert monitor1 is monitor2
    
    def test_global_monitor_persistence(self):
        """Test that global monitor persists across calls."""
        monitor = get_performance_monitor()
        monitor.enable()
        monitor.start_session("persistent_session")
        
        # Get monitor again
        monitor2 = get_performance_monitor()
        
        # Should have same session
        assert monitor2.current_session is not None
        assert monitor2.current_session.session_id == "persistent_session"
        
        # Clean up
        monitor.end_session()

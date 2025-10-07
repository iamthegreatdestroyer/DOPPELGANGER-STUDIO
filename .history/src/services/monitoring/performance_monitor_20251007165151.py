"""
Copyright (c) 2025 DOPPELGANGER STUDIO. All Rights Reserved.

Performance monitoring system for tracking generation metrics.

This module provides comprehensive performance tracking including:
- Operation timing and bottleneck detection
- Cache hit rate monitoring
- API call counting and token usage
- Memory usage tracking
- Performance reporting and alerts
- Real-time metrics dashboard
- Automated alert system
"""

import time
import logging
import asyncio
import psutil
import tracemalloc
from typing import Dict, List, Optional, Callable, Any, Union
from dataclasses import dataclass, field, asdict
from datetime import datetime, timedelta
from functools import wraps
from collections import deque, defaultdict
from threading import Lock

logger = logging.getLogger(__name__)


# ============================================================================
# DATA MODELS
# ============================================================================

@dataclass
class OperationMetrics:
    """
    Metrics for a single operation.
    
    Tracks timing, resource usage, and success/failure for operations.
    """
    operation_name: str
    start_time: datetime
    end_time: Optional[datetime] = None
    duration_seconds: float = 0.0
    success: bool = True
    error: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    memory_start_mb: float = 0.0
    memory_end_mb: float = 0.0
    memory_delta_mb: float = 0.0
    cpu_percent: float = 0.0
    
    def finish(
        self,
        success: bool = True,
        error: Optional[str] = None,
        memory_end_mb: float = 0.0,
        cpu_percent: float = 0.0
    ):
        """Mark operation as finished."""
        self.end_time = datetime.now()
        self.duration_seconds = (
            self.end_time - self.start_time
        ).total_seconds()
        self.success = success
        self.error = error
        self.memory_end_mb = memory_end_mb
        self.memory_delta_mb = memory_end_mb - self.memory_start_mb
        self.cpu_percent = cpu_percent
    
    def to_dict(self) -> Dict:
        """Convert to dictionary."""
        return {
            "operation_name": self.operation_name,
            "start_time": self.start_time.isoformat(),
            "end_time": self.end_time.isoformat() if self.end_time else None,
            "duration_seconds": self.duration_seconds,
            "success": self.success,
            "error": self.error,
            "metadata": self.metadata,
            "memory_start_mb": self.memory_start_mb,
            "memory_end_mb": self.memory_end_mb,
            "memory_delta_mb": self.memory_delta_mb,
            "cpu_percent": self.cpu_percent,
        }


@dataclass
class PerformanceAlert:
    """Alert for performance issues."""
    alert_id: str
    alert_type: str  # 'slow_operation', 'high_error_rate', 'memory_warning', 'api_limit'
    severity: str  # 'info', 'warning', 'error', 'critical'
    message: str
    timestamp: datetime = field(default_factory=datetime.now)
    operation_name: Optional[str] = None
    metric_value: Optional[float] = None
    threshold_value: Optional[float] = None
    
    def to_dict(self) -> Dict:
        """Convert to dictionary."""
        return {
            "alert_id": self.alert_id,
            "alert_type": self.alert_type,
            "severity": self.severity,
            "message": self.message,
            "timestamp": self.timestamp.isoformat(),
            "operation_name": self.operation_name,
            "metric_value": self.metric_value,
            "threshold_value": self.threshold_value,
        }


@dataclass
class PerformanceMetrics:
    """
    Comprehensive performance metrics for episode generation.
    
    Tracks all aspects of performance including timing, caching,
    API usage, and resource consumption.
    """
    session_id: str
    start_time: datetime = field(default_factory=datetime.now)
    end_time: Optional[datetime] = None
    total_duration_seconds: float = 0.0
    
    # Operation tracking
    operations: List[OperationMetrics] = field(default_factory=list)
    
    # Cache metrics
    cache_hits: int = 0
    cache_misses: int = 0
    cache_hit_rate: float = 0.0
    
    # API metrics
    api_calls: int = 0
    api_errors: int = 0
    total_tokens_used: int = 0
    estimated_api_cost: float = 0.0
    
    # Generation metrics
    scenes_generated: int = 0
    dialogue_lines_generated: int = 0
    stage_directions_generated: int = 0
    jokes_analyzed: int = 0
    
    # Bottleneck detection
    slowest_operations: List[OperationMetrics] = field(default_factory=list)
    bottleneck_warnings: List[str] = field(default_factory=list)
    
    def finish(self):
        """Mark session as finished and calculate final metrics."""
        self.end_time = datetime.now()
        self.total_duration_seconds = (
            self.end_time - self.start_time
        ).total_seconds()
        
        # Calculate cache hit rate
        total_cache_ops = self.cache_hits + self.cache_misses
        if total_cache_ops > 0:
            self.cache_hit_rate = self.cache_hits / total_cache_ops
        
        # Identify slowest operations (top 5)
        sorted_ops = sorted(
            [op for op in self.operations if op.end_time],
            key=lambda x: x.duration_seconds,
            reverse=True
        )
        self.slowest_operations = sorted_ops[:5]
        
        # Detect bottlenecks (operations taking >20% of total time)
        if self.total_duration_seconds > 0:
            threshold = self.total_duration_seconds * 0.2
            for op in self.operations:
                if op.duration_seconds > threshold:
                    warning = (
                        f"{op.operation_name} took {op.duration_seconds:.2f}s "
                        f"({op.duration_seconds/self.total_duration_seconds*100:.1f}% of total)"
                    )
                    self.bottleneck_warnings.append(warning)
    
    def add_operation(self, operation: OperationMetrics):
        """Add completed operation to metrics."""
        self.operations.append(operation)
    
    def record_cache_hit(self):
        """Record a cache hit."""
        self.cache_hits += 1
    
    def record_cache_miss(self):
        """Record a cache miss."""
        self.cache_misses += 1
    
    def record_api_call(
        self,
        tokens_used: int = 0,
        cost: float = 0.0,
        error: bool = False
    ):
        """Record an API call."""
        self.api_calls += 1
        self.total_tokens_used += tokens_used
        self.estimated_api_cost += cost
        if error:
            self.api_errors += 1
    
    def to_dict(self) -> Dict:
        """Convert to dictionary."""
        return {
            "session_id": self.session_id,
            "start_time": self.start_time.isoformat(),
            "end_time": self.end_time.isoformat() if self.end_time else None,
            "total_duration_seconds": self.total_duration_seconds,
            "cache_hit_rate": self.cache_hit_rate,
            "cache_hits": self.cache_hits,
            "cache_misses": self.cache_misses,
            "api_calls": self.api_calls,
            "api_errors": self.api_errors,
            "total_tokens_used": self.total_tokens_used,
            "estimated_api_cost": self.estimated_api_cost,
            "scenes_generated": self.scenes_generated,
            "dialogue_lines_generated": self.dialogue_lines_generated,
            "stage_directions_generated": self.stage_directions_generated,
            "jokes_analyzed": self.jokes_analyzed,
            "operations_count": len(self.operations),
            "slowest_operations": [
                op.to_dict() for op in self.slowest_operations
            ],
            "bottleneck_warnings": self.bottleneck_warnings,
        }
    
    def get_summary(self) -> str:
        """Get human-readable summary."""
        lines = [
            f"Performance Summary (Session: {self.session_id})",
            f"=" * 60,
            f"Total Duration: {self.total_duration_seconds:.2f}s",
            f"",
            f"Cache Performance:",
            f"  Hit Rate: {self.cache_hit_rate*100:.1f}% ({self.cache_hits} hits, {self.cache_misses} misses)",
            f"",
            f"API Usage:",
            f"  Calls: {self.api_calls} (Errors: {self.api_errors})",
            f"  Tokens: {self.total_tokens_used:,}",
            f"  Est. Cost: ${self.estimated_api_cost:.4f}",
            f"",
            f"Generation Stats:",
            f"  Scenes: {self.scenes_generated}",
            f"  Dialogue Lines: {self.dialogue_lines_generated}",
            f"  Stage Directions: {self.stage_directions_generated}",
            f"  Jokes Analyzed: {self.jokes_analyzed}",
        ]
        
        if self.slowest_operations:
            lines.append("")
            lines.append("Slowest Operations:")
            for op in self.slowest_operations[:3]:
                lines.append(
                    f"  {op.operation_name}: {op.duration_seconds:.2f}s"
                )
        
        if self.bottleneck_warnings:
            lines.append("")
            lines.append("⚠️  Bottleneck Warnings:")
            for warning in self.bottleneck_warnings:
                lines.append(f"  {warning}")
        
        return "\n".join(lines)


# ============================================================================
# PERFORMANCE MONITOR
# ============================================================================

class PerformanceMonitor:
    """
    Global performance monitoring system.
    
    Tracks performance across all operations and provides
    reporting, analysis, real-time metrics, and alerting capabilities.
    """
    
    def __init__(self):
        """Initialize performance monitor."""
        self.current_session: Optional[PerformanceMetrics] = None
        self.sessions: List[PerformanceMetrics] = []
        self._enabled = True
        self._lock = Lock()
        
        # Real-time metrics storage
        self._recent_operations = deque(maxlen=100)  # Last 100 operations
        self._operation_stats = defaultdict(lambda: {
            'count': 0,
            'total_time': 0.0,
            'errors': 0,
            'avg_time': 0.0,
            'min_time': float('inf'),
            'max_time': 0.0
        })
        
        # Alert system
        self._alerts = deque(maxlen=50)  # Last 50 alerts
        self._alert_thresholds = {
            'slow_operation_seconds': 5.0,
            'error_rate_percent': 10.0,
            'memory_mb': 500.0,
            'api_calls_per_minute': 100,
            'cache_hit_rate_percent': 50.0,
        }
        
        # System monitoring
        self._process = psutil.Process()
        self._memory_tracking_enabled = False
        
        # Performance trends (last 10 sessions)
        self._session_trends = deque(maxlen=10)
    
    def start_session(self, session_id: str) -> PerformanceMetrics:
        """Start a new performance monitoring session."""
        if not self._enabled:
            return None
        
        self.current_session = PerformanceMetrics(session_id=session_id)
        logger.info(f"Started performance monitoring session: {session_id}")
        return self.current_session
    
    def end_session(self) -> Optional[PerformanceMetrics]:
        """End current session and return metrics."""
        if not self._enabled or not self.current_session:
            return None
        
        self.current_session.finish()
        self.sessions.append(self.current_session)
        
        logger.info(
            f"Session {self.current_session.session_id} completed: "
            f"{self.current_session.total_duration_seconds:.2f}s"
        )
        
        # Log warnings if any
        if self.current_session.bottleneck_warnings:
            for warning in self.current_session.bottleneck_warnings:
                logger.warning(f"Performance bottleneck: {warning}")
        
        session = self.current_session
        self.current_session = None
        return session
    
    def start_operation(self, operation_name: str) -> OperationMetrics:
        """Start tracking an operation."""
        if not self._enabled:
            return OperationMetrics(
                operation_name=operation_name,
                start_time=datetime.now()
            )
        
        operation = OperationMetrics(
            operation_name=operation_name,
            start_time=datetime.now()
        )
        
        logger.debug(f"Started operation: {operation_name}")
        return operation
    
    def end_operation(
        self,
        operation: OperationMetrics,
        success: bool = True,
        error: Optional[str] = None,
        metadata: Optional[Dict] = None
    ):
        """End tracking an operation."""
        if not self._enabled:
            return
        
        operation.finish(success=success, error=error)
        
        if metadata:
            operation.metadata.update(metadata)
        
        if self.current_session:
            self.current_session.add_operation(operation)
        
        logger.debug(
            f"Completed operation: {operation.operation_name} "
            f"({operation.duration_seconds:.3f}s)"
        )
    
    def record_cache_hit(self):
        """Record cache hit in current session."""
        if self._enabled and self.current_session:
            self.current_session.record_cache_hit()
    
    def record_cache_miss(self):
        """Record cache miss in current session."""
        if self._enabled and self.current_session:
            self.current_session.record_cache_miss()
    
    def record_api_call(
        self,
        tokens_used: int = 0,
        cost: float = 0.0,
        error: bool = False
    ):
        """Record API call in current session."""
        if self._enabled and self.current_session:
            self.current_session.record_api_call(
                tokens_used=tokens_used,
                cost=cost,
                error=error
            )
    
    def get_current_metrics(self) -> Optional[PerformanceMetrics]:
        """Get current session metrics."""
        return self.current_session
    
    def get_session_history(self) -> List[PerformanceMetrics]:
        """Get all completed sessions."""
        return self.sessions
    
    def enable(self):
        """Enable performance monitoring."""
        self._enabled = True
        logger.info("Performance monitoring enabled")
    
    def disable(self):
        """Disable performance monitoring."""
        self._enabled = False
        logger.info("Performance monitoring disabled")
    
    def is_enabled(self) -> bool:
        """Check if monitoring is enabled."""
        return self._enabled


# Global performance monitor instance
_global_monitor = PerformanceMonitor()


def get_performance_monitor() -> PerformanceMonitor:
    """Get global performance monitor instance."""
    return _global_monitor


# ============================================================================
# DECORATORS
# ============================================================================

def monitor_performance(operation_name: Optional[str] = None):
    """
    Decorator to monitor function performance.
    
    Usage:
        @monitor_performance("my_operation")
        def my_function():
            pass
    """
    def decorator(func: Callable) -> Callable:
        op_name = operation_name or func.__name__
        
        @wraps(func)
        def wrapper(*args, **kwargs):
            monitor = get_performance_monitor()
            operation = monitor.start_operation(op_name)
            
            try:
                result = func(*args, **kwargs)
                monitor.end_operation(operation, success=True)
                return result
            except Exception as e:
                monitor.end_operation(
                    operation,
                    success=False,
                    error=str(e)
                )
                raise
        
        return wrapper
    return decorator


def monitor_async_performance(operation_name: Optional[str] = None):
    """
    Decorator to monitor async function performance.
    
    Usage:
        @monitor_async_performance("my_async_operation")
        async def my_async_function():
            pass
    """
    def decorator(func: Callable) -> Callable:
        op_name = operation_name or func.__name__
        
        @wraps(func)
        async def wrapper(*args, **kwargs):
            monitor = get_performance_monitor()
            operation = monitor.start_operation(op_name)
            
            try:
                result = await func(*args, **kwargs)
                monitor.end_operation(operation, success=True)
                return result
            except Exception as e:
                monitor.end_operation(
                    operation,
                    success=False,
                    error=str(e)
                )
                raise
        
        return wrapper
    return decorator

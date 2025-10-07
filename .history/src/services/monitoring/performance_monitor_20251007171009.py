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
        
        # Add to trends
        with self._lock:
            self._session_trends.append({
                'session_id': self.current_session.session_id,
                'duration': self.current_session.total_duration_seconds,
                'cache_hit_rate': self.current_session.cache_hit_rate,
                'api_calls': self.current_session.api_calls,
                'error_count': sum(1 for op in self.current_session.operations if not op.success),
                'timestamp': self.current_session.end_time
            })
        
        logger.info(
            f"Session {self.current_session.session_id} completed: "
            f"{self.current_session.total_duration_seconds:.2f}s"
        )
        
        # Log warnings if any
        if self.current_session.bottleneck_warnings:
            for warning in self.current_session.bottleneck_warnings:
                logger.warning(f"Performance bottleneck: {warning}")
        
        # Check for session-level alerts
        self._check_session_alerts(self.current_session)
        
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
        
        # Get current memory usage
        memory_mb = self._get_memory_usage_mb()
        
        operation = OperationMetrics(
            operation_name=operation_name,
            start_time=datetime.now(),
            memory_start_mb=memory_mb
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
        
        # Get final resource usage
        memory_mb = self._get_memory_usage_mb()
        cpu_percent = self._get_cpu_usage()
        
        operation.finish(
            success=success,
            error=error,
            memory_end_mb=memory_mb,
            cpu_percent=cpu_percent
        )
        
        if metadata:
            operation.metadata.update(metadata)
        
        # Update current session
        if self.current_session:
            self.current_session.add_operation(operation)
        
        # Update real-time stats
        with self._lock:
            self._recent_operations.append(operation)
            
            stats = self._operation_stats[operation.operation_name]
            stats['count'] += 1
            stats['total_time'] += operation.duration_seconds
            if not success:
                stats['errors'] += 1
            stats['avg_time'] = stats['total_time'] / stats['count']
            stats['min_time'] = min(stats['min_time'], operation.duration_seconds)
            stats['max_time'] = max(stats['max_time'], operation.duration_seconds)
        
        # Check for operation-level alerts
        self._check_operation_alerts(operation)
        
        logger.debug(
            f"Completed operation: {operation.operation_name} "
            f"({operation.duration_seconds:.3f}s, "
            f"mem_delta={operation.memory_delta_mb:.1f}MB)"
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
    
    def _get_memory_usage_mb(self) -> float:
        """Get current memory usage in MB."""
        try:
            mem_info = self._process.memory_info()
            return mem_info.rss / 1024 / 1024  # Convert to MB
        except Exception as e:
            logger.debug(f"Failed to get memory usage: {e}")
            return 0.0
    
    def _get_cpu_usage(self) -> float:
        """Get current CPU usage percentage."""
        try:
            return self._process.cpu_percent(interval=0.1)
        except Exception as e:
            logger.debug(f"Failed to get CPU usage: {e}")
            return 0.0
    
    def _check_operation_alerts(self, operation: OperationMetrics):
        """Check for operation-level alert conditions."""
        # Slow operation alert
        threshold = self._alert_thresholds['slow_operation_seconds']
        if operation.duration_seconds > threshold:
            alert = PerformanceAlert(
                alert_id=f"slow_op_{operation.operation_name}_{operation.start_time.timestamp()}",
                alert_type="slow_operation",
                severity="warning",
                message=f"Operation '{operation.operation_name}' took {operation.duration_seconds:.2f}s (threshold: {threshold}s)",
                operation_name=operation.operation_name,
                metric_value=operation.duration_seconds,
                threshold_value=threshold
            )
            self._add_alert(alert)
        
        # Memory warning
        memory_threshold = self._alert_thresholds['memory_mb']
        if operation.memory_delta_mb > memory_threshold:
            alert = PerformanceAlert(
                alert_id=f"high_mem_{operation.operation_name}_{operation.start_time.timestamp()}",
                alert_type="memory_warning",
                severity="warning",
                message=f"Operation '{operation.operation_name}' used {operation.memory_delta_mb:.1f}MB (threshold: {memory_threshold}MB)",
                operation_name=operation.operation_name,
                metric_value=operation.memory_delta_mb,
                threshold_value=memory_threshold
            )
            self._add_alert(alert)
        
        # Error alert
        if not operation.success:
            alert = PerformanceAlert(
                alert_id=f"error_{operation.operation_name}_{operation.start_time.timestamp()}",
                alert_type="operation_error",
                severity="error",
                message=f"Operation '{operation.operation_name}' failed: {operation.error}",
                operation_name=operation.operation_name
            )
            self._add_alert(alert)
    
    def _check_session_alerts(self, session: PerformanceMetrics):
        """Check for session-level alert conditions."""
        # Low cache hit rate
        cache_threshold = self._alert_thresholds['cache_hit_rate_percent']
        if session.cache_hit_rate < (cache_threshold / 100.0):
            alert = PerformanceAlert(
                alert_id=f"low_cache_{session.session_id}",
                alert_type="cache_performance",
                severity="warning",
                message=f"Low cache hit rate: {session.cache_hit_rate*100:.1f}% (threshold: {cache_threshold}%)",
                metric_value=session.cache_hit_rate * 100,
                threshold_value=cache_threshold
            )
            self._add_alert(alert)
        
        # High error rate
        total_ops = len(session.operations)
        if total_ops > 0:
            error_count = sum(1 for op in session.operations if not op.success)
            error_rate = (error_count / total_ops) * 100
            error_threshold = self._alert_thresholds['error_rate_percent']
            
            if error_rate > error_threshold:
                alert = PerformanceAlert(
                    alert_id=f"high_errors_{session.session_id}",
                    alert_type="high_error_rate",
                    severity="error",
                    message=f"High error rate: {error_rate:.1f}% ({error_count}/{total_ops} operations failed)",
                    metric_value=error_rate,
                    threshold_value=error_threshold
                )
                self._add_alert(alert)
    
    def _add_alert(self, alert: PerformanceAlert):
        """Add alert to queue and log it."""
        with self._lock:
            self._alerts.append(alert)
        
        # Log based on severity
        log_msg = f"[{alert.severity.upper()}] {alert.message}"
        if alert.severity == 'critical':
            logger.critical(log_msg)
        elif alert.severity == 'error':
            logger.error(log_msg)
        elif alert.severity == 'warning':
            logger.warning(log_msg)
        else:
            logger.info(log_msg)
    
    def get_alerts(
        self,
        severity: Optional[str] = None,
        alert_type: Optional[str] = None,
        limit: int = 50
    ) -> List[PerformanceAlert]:
        """
        Get recent alerts with optional filtering.
        
        Args:
            severity: Filter by severity ('info', 'warning', 'error', 'critical')
            alert_type: Filter by type ('slow_operation', 'high_error_rate', etc.)
            limit: Maximum number of alerts to return
        
        Returns:
            List of alerts matching criteria
        """
        with self._lock:
            alerts = list(self._alerts)
        
        # Apply filters
        if severity:
            alerts = [a for a in alerts if a.severity == severity]
        if alert_type:
            alerts = [a for a in alerts if a.alert_type == alert_type]
        
        # Return most recent
        return alerts[-limit:]
    
    def clear_alerts(self):
        """Clear all alerts."""
        with self._lock:
            self._alerts.clear()
        logger.info("Cleared all performance alerts")
    
    def set_alert_threshold(self, threshold_name: str, value: float):
        """
        Set alert threshold.
        
        Available thresholds:
        - slow_operation_seconds: Warn if operation exceeds this duration
        - error_rate_percent: Warn if error rate exceeds this percentage
        - memory_mb: Warn if operation uses this much memory
        - api_calls_per_minute: Warn if API calls exceed this rate
        - cache_hit_rate_percent: Warn if cache hit rate below this
        """
        if threshold_name in self._alert_thresholds:
            self._alert_thresholds[threshold_name] = value
            logger.info(f"Updated alert threshold: {threshold_name} = {value}")
        else:
            logger.warning(f"Unknown threshold name: {threshold_name}")
    
    def get_dashboard_data(self) -> Dict[str, Any]:
        """
        Get comprehensive dashboard data.
        
        Returns real-time metrics, recent operations, alerts,
        trends, and system health information.
        """
        with self._lock:
            recent_ops = list(self._recent_operations)
            operation_stats = dict(self._operation_stats)
            alerts = list(self._alerts)
            trends = list(self._session_trends)
        
        # Current system resources
        system_metrics = {
            'memory_mb': self._get_memory_usage_mb(),
            'cpu_percent': self._get_cpu_usage(),
            'timestamp': datetime.now().isoformat()
        }
        
        # Operation statistics
        op_stats_summary = {}
        for op_name, stats in operation_stats.items():
            op_stats_summary[op_name] = {
                'count': stats['count'],
                'avg_time_seconds': round(stats['avg_time'], 3),
                'min_time_seconds': round(stats['min_time'], 3) if stats['min_time'] != float('inf') else 0,
                'max_time_seconds': round(stats['max_time'], 3),
                'error_count': stats['errors'],
                'error_rate_percent': round((stats['errors'] / stats['count']) * 100, 2) if stats['count'] > 0 else 0
            }
        
        # Recent operations (last 10)
        recent_ops_data = [op.to_dict() for op in recent_ops[-10:]]
        
        # Active alerts (last 10)
        recent_alerts = [alert.to_dict() for alert in alerts[-10:]]
        
        # Alert summary by severity
        alert_summary = {
            'total': len(alerts),
            'critical': sum(1 for a in alerts if a.severity == 'critical'),
            'error': sum(1 for a in alerts if a.severity == 'error'),
            'warning': sum(1 for a in alerts if a.severity == 'warning'),
            'info': sum(1 for a in alerts if a.severity == 'info')
        }
        
        # Performance trends
        trends_data = []
        for trend in trends:
            trends_data.append({
                'session_id': trend['session_id'],
                'duration_seconds': round(trend['duration'], 2),
                'cache_hit_rate_percent': round(trend['cache_hit_rate'] * 100, 1),
                'api_calls': trend['api_calls'],
                'error_count': trend['error_count'],
                'timestamp': trend['timestamp'].isoformat() if trend['timestamp'] else None
            })
        
        # Current session info
        current_session_data = None
        if self.current_session:
            current_session_data = {
                'session_id': self.current_session.session_id,
                'duration_seconds': (datetime.now() - self.current_session.start_time).total_seconds(),
                'operations_count': len(self.current_session.operations),
                'cache_hits': self.current_session.cache_hits,
                'cache_misses': self.current_session.cache_misses,
                'api_calls': self.current_session.api_calls
            }
        
        # System health score (0-100)
        health_score = self._calculate_health_score(
            operation_stats,
            alerts,
            system_metrics
        )
        
        return {
            'timestamp': datetime.now().isoformat(),
            'monitoring_enabled': self._enabled,
            'system_metrics': system_metrics,
            'health_score': health_score,
            'current_session': current_session_data,
            'operation_statistics': op_stats_summary,
            'recent_operations': recent_ops_data,
            'alerts': {
                'summary': alert_summary,
                'recent': recent_alerts
            },
            'performance_trends': trends_data,
            'alert_thresholds': self._alert_thresholds
        }
    
    def _calculate_health_score(
        self,
        operation_stats: Dict,
        alerts: List,
        system_metrics: Dict
    ) -> int:
        """
        Calculate overall system health score (0-100).
        
        Factors:
        - Error rates (30% weight)
        - Alert severity (30% weight)
        - System resources (20% weight)
        - Performance trends (20% weight)
        """
        score = 100
        
        # Error rate impact (-30 points max)
        total_ops = sum(stats['count'] for stats in operation_stats.values())
        total_errors = sum(stats['errors'] for stats in operation_stats.values())
        if total_ops > 0:
            error_rate = (total_errors / total_ops) * 100
            score -= min(30, error_rate * 3)  # 10% errors = -30 points
        
        # Alert severity impact (-30 points max)
        recent_alerts = list(alerts)[-10:]  # Last 10 alerts
        critical_count = sum(1 for a in recent_alerts if a.severity == 'critical')
        error_count = sum(1 for a in recent_alerts if a.severity == 'error')
        warning_count = sum(1 for a in recent_alerts if a.severity == 'warning')
        alert_penalty = (critical_count * 10) + (error_count * 5) + (warning_count * 2)
        score -= min(30, alert_penalty)
        
        # System resources impact (-20 points max)
        memory_mb = system_metrics.get('memory_mb', 0)
        cpu_percent = system_metrics.get('cpu_percent', 0)
        if memory_mb > 1000:  # Over 1GB
            score -= min(10, (memory_mb - 1000) / 100)
        if cpu_percent > 80:
            score -= min(10, (cpu_percent - 80) / 2)
        
        # Ensure score is in 0-100 range
        return max(0, min(100, int(score)))
    
    def get_performance_report(self) -> str:
        """Get human-readable performance report."""
        dashboard = self.get_dashboard_data()
        
        lines = [
            "=" * 70,
            "PERFORMANCE MONITORING DASHBOARD",
            "=" * 70,
            f"Timestamp: {dashboard['timestamp']}",
            f"Monitoring: {'Enabled' if dashboard['monitoring_enabled'] else 'Disabled'}",
            f"Health Score: {dashboard['health_score']}/100",
            "",
            "SYSTEM METRICS:",
            f"  Memory Usage: {dashboard['system_metrics']['memory_mb']:.1f} MB",
            f"  CPU Usage: {dashboard['system_metrics']['cpu_percent']:.1f}%",
            "",
        ]
        
        if dashboard['current_session']:
            session = dashboard['current_session']
            lines.extend([
                "CURRENT SESSION:",
                f"  ID: {session['session_id']}",
                f"  Duration: {session['duration_seconds']:.1f}s",
                f"  Operations: {session['operations_count']}",
                f"  Cache: {session['cache_hits']} hits / {session['cache_misses']} misses",
                f"  API Calls: {session['api_calls']}",
                "",
            ])
        
        # Operation statistics
        if dashboard['operation_statistics']:
            lines.append("OPERATION STATISTICS:")
            for op_name, stats in sorted(
                dashboard['operation_statistics'].items(),
                key=lambda x: x[1]['count'],
                reverse=True
            )[:5]:  # Top 5
                lines.append(
                    f"  {op_name}: {stats['count']} calls, "
                    f"avg={stats['avg_time_seconds']:.3f}s, "
                    f"errors={stats['error_count']}"
                )
            lines.append("")
        
        # Alerts
        alert_summary = dashboard['alerts']['summary']
        if alert_summary['total'] > 0:
            lines.extend([
                "ALERTS:",
                f"  Total: {alert_summary['total']} "
                f"(Critical: {alert_summary['critical']}, "
                f"Error: {alert_summary['error']}, "
                f"Warning: {alert_summary['warning']})",
                ""
            ])
            
            # Show recent alerts
            for alert in dashboard['alerts']['recent'][-5:]:
                lines.append(
                    f"  [{alert['severity'].upper()}] {alert['message']}"
                )
            lines.append("")
        
        lines.append("=" * 70)
        return "\n".join(lines)
    
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
# DECORATORS AND CONTEXT MANAGERS
# ============================================================================

def monitor_performance(operation_name: Optional[str] = None):
    """
    Decorator to monitor function performance.
    
    Tracks execution time, memory usage, CPU usage, and errors.
    
    Usage:
        @monitor_performance("my_operation")
        def my_function():
            pass
        
        @monitor_performance()  # Uses function name
        def another_function():
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
    
    Tracks execution time, memory usage, CPU usage, and errors.
    
    Usage:
        @monitor_async_performance("my_async_operation")
        async def my_async_function():
            pass
        
        @monitor_async_performance()  # Uses function name
        async def another_async_function():
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


class PerformanceContext:
    """
    Context manager for monitoring code blocks.
    
    Usage:
        with PerformanceContext("complex_operation"):
            # Your code here
            perform_complex_task()
        
        # Async version
        async with PerformanceContext("async_operation"):
            # Your async code here
            await perform_async_task()
    """
    
    def __init__(self, operation_name: str, metadata: Optional[Dict] = None):
        """
        Initialize context manager.
        
        Args:
            operation_name: Name of the operation to monitor
            metadata: Optional metadata to attach to operation
        """
        self.operation_name = operation_name
        self.metadata = metadata or {}
        self.monitor = get_performance_monitor()
        self.operation: Optional[OperationMetrics] = None
    
    def __enter__(self):
        """Enter context (sync version)."""
        self.operation = self.monitor.start_operation(self.operation_name)
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Exit context (sync version)."""
        success = exc_type is None
        error = str(exc_val) if exc_val else None
        self.monitor.end_operation(
            self.operation,
            success=success,
            error=error,
            metadata=self.metadata
        )
        return False  # Don't suppress exceptions
    
    async def __aenter__(self):
        """Enter context (async version)."""
        self.operation = self.monitor.start_operation(self.operation_name)
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Exit context (async version)."""
        success = exc_type is None
        error = str(exc_val) if exc_val else None
        self.monitor.end_operation(
            self.operation,
            success=success,
            error=error,
            metadata=self.metadata
        )
        return False  # Don't suppress exceptions
    
    def add_metadata(self, key: str, value: Any):
        """Add metadata to the operation."""
        self.metadata[key] = value


# Convenience function for creating monitoring context
def monitor_block(operation_name: str, metadata: Optional[Dict] = None) -> PerformanceContext:
    """
    Create a performance monitoring context.
    
    Usage:
        with monitor_block("my_operation"):
            # Code to monitor
            pass
    """
    return PerformanceContext(operation_name, metadata)


# ============================================================================
# UTILITY FUNCTIONS
# ============================================================================

def enable_memory_tracking():
    """Enable detailed memory tracking using tracemalloc."""
    if not tracemalloc.is_tracing():
        tracemalloc.start()
        logger.info("Memory tracking enabled")


def disable_memory_tracking():
    """Disable detailed memory tracking."""
    if tracemalloc.is_tracing():
        tracemalloc.stop()
        logger.info("Memory tracking disabled")


def get_memory_snapshot():
    """Get current memory snapshot if tracking is enabled."""
    if tracemalloc.is_tracing():
        return tracemalloc.take_snapshot()
    return None


def compare_memory_snapshots(snapshot1, snapshot2, top_n: int = 10):
    """
    Compare two memory snapshots and return top differences.
    
    Args:
        snapshot1: First snapshot
        snapshot2: Second snapshot
        top_n: Number of top differences to return
    
    Returns:
        List of memory differences
    """
    if not snapshot1 or not snapshot2:
        return []
    
    top_stats = snapshot2.compare_to(snapshot1, 'lineno')
    differences = []
    
    for stat in top_stats[:top_n]:
        differences.append({
            'filename': stat.traceback.format()[0],
            'size_diff_kb': stat.size_diff / 1024,
            'count_diff': stat.count_diff
        })
    
    return differences

"""
Production Monitoring Dashboard - Real-time performance visualization.

Provides web-based dashboard for monitoring system performance, resource usage,
and application health metrics.

Copyright (c) 2025. All Rights Reserved. Patent Pending.
"""

from typing import Dict, List, Optional, Any
import asyncio
import logging
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict
import json

from src.services.optimization.memory_manager import get_memory_manager
from src.services.optimization.resource_monitor import ResourceMonitor

logger = logging.getLogger(__name__)


@dataclass
class DashboardMetrics:
    """Container for dashboard metrics."""
    timestamp: str
    system: Dict[str, Any]
    memory: Dict[str, Any]
    performance: Dict[str, Any]
    health: Dict[str, Any]


class MonitoringDashboard:
    """
    Production monitoring dashboard.
    
    Provides real-time metrics, alerts, and performance visualization
    for production monitoring and debugging.
    
    Features:
    - Real-time system metrics
    - Memory usage tracking
    - Performance bottleneck detection
    - Alert management
    - Historical trend analysis
    
    Example:
        >>> dashboard = MonitoringDashboard()
        >>> await dashboard.start()
        >>> metrics = await dashboard.get_current_metrics()
        >>> print(f"CPU: {metrics.system['cpu_percent']}%")
    """
    
    def __init__(self):
        """Initialize monitoring dashboard."""
        self.memory_manager = get_memory_manager()
        self.resource_monitor = ResourceMonitor()
        self._running = False
        self._update_task: Optional[asyncio.Task] = None
        self._metrics_history: List[DashboardMetrics] = []
        self._max_history = 1000
        
    async def start(self, update_interval: float = 5.0):
        """
        Start dashboard monitoring.
        
        Args:
            update_interval: Metrics update interval in seconds
        """
        if self._running:
            logger.warning("Dashboard already running")
            return
        
        self._running = True
        
        # Start subsystems
        await self.memory_manager.start_monitoring()
        await self.resource_monitor.start_monitoring()
        
        # Start dashboard update loop
        self._update_task = asyncio.create_task(
            self._update_loop(update_interval)
        )
        
        logger.info(f"Monitoring dashboard started (interval={update_interval}s)")
    
    async def stop(self):
        """Stop dashboard monitoring."""
        if not self._running:
            return
        
        self._running = False
        
        # Stop subsystems
        await self.memory_manager.stop_monitoring()
        await self.resource_monitor.stop_monitoring()
        
        # Stop update loop
        if self._update_task:
            self._update_task.cancel()
            try:
                await self._update_task
            except asyncio.CancelledError:
                pass
        
        logger.info("Monitoring dashboard stopped")
    
    async def _update_loop(self, interval: float):
        """Background metrics update loop."""
        while self._running:
            try:
                metrics = await self.get_current_metrics()
                self._metrics_history.append(metrics)
                
                # Trim history
                if len(self._metrics_history) > self._max_history:
                    self._metrics_history = self._metrics_history[-self._max_history:]
                
                await asyncio.sleep(interval)
                
            except Exception as e:
                logger.error(f"Dashboard update error: {e}")
                await asyncio.sleep(interval)
    
    async def get_current_metrics(self) -> DashboardMetrics:
        """
        Get current dashboard metrics.
        
        Returns:
            Current system metrics
        """
        # Get resource snapshot
        resource_snapshot = self.resource_monitor.get_current_snapshot()
        
        # Get memory stats
        memory_stats = self.memory_manager.get_current_stats()
        
        # Get pool stats
        pool_stats = self.memory_manager.get_pool_stats()
        
        # Detect bottlenecks
        bottlenecks = self.resource_monitor.detect_bottlenecks()
        
        # Check for memory leaks
        memory_leaks = self.memory_manager.detect_memory_leaks()
        
        return DashboardMetrics(
            timestamp=datetime.now().isoformat(),
            system={
                'cpu_percent': resource_snapshot.cpu_percent,
                'memory_percent': resource_snapshot.memory_percent,
                'memory_mb': resource_snapshot.memory_mb,
                'disk_io_read_mb': resource_snapshot.disk_io_read_mb,
                'disk_io_write_mb': resource_snapshot.disk_io_write_mb,
                'network_sent_mb': resource_snapshot.network_sent_mb,
                'network_recv_mb': resource_snapshot.network_recv_mb,
                'open_files': resource_snapshot.open_files,
                'threads': resource_snapshot.threads
            },
            memory={
                'total_mb': memory_stats.total_memory / 1024 / 1024,
                'available_mb': memory_stats.available_memory / 1024 / 1024,
                'percent_used': memory_stats.percent_used,
                'process_mb': memory_stats.process_memory / 1024 / 1024,
                'gc_collections': memory_stats.gc_collections,
                'pool_stats': pool_stats,
                'leaks_detected': len(memory_leaks) > 0,
                'leak_details': memory_leaks
            },
            performance={
                'bottlenecks': bottlenecks,
                'bottleneck_count': len(bottlenecks),
                'status': self._get_performance_status(bottlenecks)
            },
            health={
                'status': self._get_health_status(
                    resource_snapshot,
                    memory_stats,
                    bottlenecks,
                    memory_leaks
                ),
                'alerts': self._get_active_alerts(
                    resource_snapshot,
                    memory_stats,
                    bottlenecks,
                    memory_leaks
                )
            }
        )
    
    def _get_performance_status(self, bottlenecks: List[Dict]) -> str:
        """Determine overall performance status."""
        if not bottlenecks:
            return 'optimal'
        
        high_severity = any(b['severity'] == 'high' for b in bottlenecks)
        if high_severity:
            return 'degraded'
        
        return 'moderate'
    
    def _get_health_status(
        self,
        resource_snapshot,
        memory_stats,
        bottlenecks: List[Dict],
        memory_leaks: List[Dict]
    ) -> str:
        """Determine overall system health."""
        # Critical issues
        if resource_snapshot.cpu_percent > 95:
            return 'critical'
        if resource_snapshot.memory_percent > 95:
            return 'critical'
        if memory_leaks:
            return 'critical'
        
        # Warning issues
        if resource_snapshot.cpu_percent > 80:
            return 'warning'
        if resource_snapshot.memory_percent > 80:
            return 'warning'
        if len(bottlenecks) > 2:
            return 'warning'
        
        # Degraded
        if len(bottlenecks) > 0:
            return 'degraded'
        
        return 'healthy'
    
    def _get_active_alerts(
        self,
        resource_snapshot,
        memory_stats,
        bottlenecks: List[Dict],
        memory_leaks: List[Dict]
    ) -> List[Dict]:
        """Get list of active alerts."""
        alerts = []
        
        # CPU alerts
        if resource_snapshot.cpu_percent > 90:
            alerts.append({
                'type': 'cpu',
                'severity': 'critical',
                'message': f'CPU usage critical: {resource_snapshot.cpu_percent:.1f}%'
            })
        elif resource_snapshot.cpu_percent > 75:
            alerts.append({
                'type': 'cpu',
                'severity': 'warning',
                'message': f'CPU usage high: {resource_snapshot.cpu_percent:.1f}%'
            })
        
        # Memory alerts
        if resource_snapshot.memory_percent > 90:
            alerts.append({
                'type': 'memory',
                'severity': 'critical',
                'message': f'Memory usage critical: {resource_snapshot.memory_percent:.1f}%'
            })
        elif resource_snapshot.memory_percent > 80:
            alerts.append({
                'type': 'memory',
                'severity': 'warning',
                'message': f'Memory usage high: {resource_snapshot.memory_percent:.1f}%'
            })
        
        # Memory leak alerts
        if memory_leaks:
            for leak in memory_leaks:
                alerts.append({
                    'type': 'memory_leak',
                    'severity': leak['severity'],
                    'message': f'Memory leak detected: {leak["percent_increase"]:.1f}% increase'
                })
        
        # Bottleneck alerts
        for bottleneck in bottlenecks:
            if bottleneck['severity'] == 'high':
                alerts.append({
                    'type': 'bottleneck',
                    'severity': 'warning',
                    'message': bottleneck['message']
                })
        
        return alerts
    
    def get_historical_metrics(
        self,
        window: Optional[timedelta] = None
    ) -> List[DashboardMetrics]:
        """
        Get historical metrics over time window.
        
        Args:
            window: Time window for history (default: all)
            
        Returns:
            List of historical metrics
        """
        if not window:
            return self._metrics_history
        
        cutoff = datetime.now() - window
        return [
            m for m in self._metrics_history
            if datetime.fromisoformat(m.timestamp) >= cutoff
        ]
    
    def export_metrics_json(self, filepath: str):
        """Export current metrics to JSON file."""
        current_metrics = asyncio.run(self.get_current_metrics())
        
        with open(filepath, 'w') as f:
            json.dump(asdict(current_metrics), f, indent=2)
        
        logger.info(f"Exported metrics to {filepath}")
    
    def get_dashboard_html(self) -> str:
        """
        Generate HTML dashboard (simplified version).
        
        Returns:
            HTML string for dashboard
        """
        metrics = asyncio.run(self.get_current_metrics())
        
        html = f"""
<!DOCTYPE html>
<html>
<head>
    <title>DOPPELGANGER STUDIO - Monitoring Dashboard</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 20px; background: #1e1e1e; color: #fff; }}
        .header {{ background: #2d2d2d; padding: 20px; border-radius: 5px; margin-bottom: 20px; }}
        .metric-grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); gap: 20px; }}
        .metric-card {{ background: #2d2d2d; padding: 20px; border-radius: 5px; }}
        .metric-value {{ font-size: 2em; font-weight: bold; margin: 10px 0; }}
        .status-healthy {{ color: #4caf50; }}
        .status-warning {{ color: #ff9800; }}
        .status-critical {{ color: #f44336; }}
        .alert {{ background: #f44336; padding: 10px; border-radius: 5px; margin: 10px 0; }}
        .alert-warning {{ background: #ff9800; }}
    </style>
</head>
<body>
    <div class="header">
        <h1>🎬 DOPPELGANGER STUDIO</h1>
        <h2>Production Monitoring Dashboard</h2>
        <p>Last updated: {metrics.timestamp}</p>
        <p class="status-{metrics.health['status']}">
            System Status: {metrics.health['status'].upper()}
        </p>
    </div>
    
    <div class="metric-grid">
        <div class="metric-card">
            <h3>💻 CPU Usage</h3>
            <div class="metric-value">{metrics.system['cpu_percent']:.1f}%</div>
            <p>Threads: {metrics.system['threads']}</p>
        </div>
        
        <div class="metric-card">
            <h3>🧠 Memory Usage</h3>
            <div class="metric-value">{metrics.system['memory_percent']:.1f}%</div>
            <p>Process: {metrics.system['memory_mb']:.0f} MB</p>
        </div>
        
        <div class="metric-card">
            <h3>💾 Disk I/O</h3>
            <div class="metric-value">
                R: {metrics.system['disk_io_read_mb']:.1f} MB
            </div>
            <p>W: {metrics.system['disk_io_write_mb']:.1f} MB</p>
        </div>
        
        <div class="metric-card">
            <h3>🌐 Network I/O</h3>
            <div class="metric-value">
                ↓ {metrics.system['network_recv_mb']:.1f} MB
            </div>
            <p>↑ {metrics.system['network_sent_mb']:.1f} MB</p>
        </div>
    </div>
    
    <h2>🚨 Active Alerts</h2>
    <div>
        {"".join(f'<div class="alert alert-{alert["severity"]}">{alert["message"]}</div>' for alert in metrics.health['alerts'])}
        {('<p>No active alerts</p>' if not metrics.health['alerts'] else '')}
    </div>
    
    <h2>⚡ Performance Status</h2>
    <p>Status: {metrics.performance['status'].upper()}</p>
    <p>Bottlenecks detected: {metrics.performance['bottleneck_count']}</p>
    
</body>
</html>
"""
        return html


# Global instance
_dashboard: Optional[MonitoringDashboard] = None


def get_dashboard() -> MonitoringDashboard:
    """Get global dashboard instance."""
    global _dashboard
    if _dashboard is None:
        _dashboard = MonitoringDashboard()
    return _dashboard


# Example usage
async def main():
    """Example dashboard usage."""
    dashboard = get_dashboard()
    
    # Start monitoring
    await dashboard.start(update_interval=5.0)
    
    # Let it collect some data
    await asyncio.sleep(30)
    
    # Get current metrics
    metrics = await dashboard.get_current_metrics()
    print(f"System Status: {metrics.health['status']}")
    print(f"CPU: {metrics.system['cpu_percent']:.1f}%")
    print(f"Memory: {metrics.system['memory_percent']:.1f}%")
    
    # Export metrics
    dashboard.export_metrics_json('dashboard_metrics.json')
    
    # Generate HTML dashboard
    html = dashboard.get_dashboard_html()
    with open('dashboard.html', 'w') as f:
        f.write(html)
    print("Dashboard saved to dashboard.html")
    
    await dashboard.stop()


if __name__ == "__main__":
    asyncio.run(main())

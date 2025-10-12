"""Resource Monitoring System - Track CPU, memory, disk, and network usage.

Copyright (c) 2025. All Rights Reserved. Patent Pending.
"""

from typing import Dict, List, Optional, Callable, Any
import asyncio
import logging
import psutil
import time
from dataclasses import dataclass
from datetime import datetime, timedelta
from collections import deque
import statistics

logger = logging.getLogger(__name__)


@dataclass
class ResourceSnapshot:
    """Single resource usage snapshot."""
    timestamp: datetime
    cpu_percent: float
    memory_percent: float
    memory_mb: float
    disk_io_read_mb: float
    disk_io_write_mb: float
    network_sent_mb: float
    network_recv_mb: float
    open_files: int
    threads: int


@dataclass
class ResourceThresholds:
    """Resource usage thresholds."""
    cpu_warning: float = 75.0
    cpu_critical: float = 90.0
    memory_warning: float = 80.0
    memory_critical: float = 90.0


class ResourceMonitor:
    """Real-time resource monitoring system."""
    
    def __init__(self, thresholds: Optional[ResourceThresholds] = None, history_size: int = 1000):
        self.thresholds = thresholds or ResourceThresholds()
        self._history_size = history_size
        self._snapshots: deque = deque(maxlen=history_size)
        self._monitoring = False
        self._monitor_task: Optional[asyncio.Task] = None
        self._process = psutil.Process()
        self._alert_callbacks: Dict[str, Dict[str, List[Callable]]] = {
            'cpu': {'warning': [], 'critical': []},
            'memory': {'warning': [], 'critical': []}
        }
        self._last_disk_io = None
        self._last_network_io = None
    
    def get_current_snapshot(self) -> ResourceSnapshot:
        """Get current resource usage snapshot."""
        cpu_percent = self._process.cpu_percent(interval=0.1)
        memory_info = self._process.memory_info()
        virtual_memory = psutil.virtual_memory()
        
        disk_io = self._process.io_counters()
        if self._last_disk_io:
            disk_read_mb = (disk_io.read_bytes - self._last_disk_io.read_bytes) / 1024 / 1024
            disk_write_mb = (disk_io.write_bytes - self._last_disk_io.write_bytes) / 1024 / 1024
        else:
            disk_read_mb = disk_write_mb = 0.0
        self._last_disk_io = disk_io
        
        network_io = psutil.net_io_counters()
        if self._last_network_io:
            net_sent_mb = (network_io.bytes_sent - self._last_network_io.bytes_sent) / 1024 / 1024
            net_recv_mb = (network_io.bytes_recv - self._last_network_io.bytes_recv) / 1024 / 1024
        else:
            net_sent_mb = net_recv_mb = 0.0
        self._last_network_io = network_io
        
        return ResourceSnapshot(
            timestamp=datetime.now(),
            cpu_percent=cpu_percent,
            memory_percent=virtual_memory.percent,
            memory_mb=memory_info.rss / 1024 / 1024,
            disk_io_read_mb=disk_read_mb,
            disk_io_write_mb=disk_write_mb,
            network_sent_mb=net_sent_mb,
            network_recv_mb=net_recv_mb,
            open_files=len(self._process.open_files()),
            threads=self._process.num_threads()
        )
    
    async def start_monitoring(self, interval: float = 2.0):
        """Start background resource monitoring."""
        if self._monitoring:
            return
        self._monitoring = True
        self._monitor_task = asyncio.create_task(self._monitor_loop(interval))
        logger.info(f"Started resource monitoring (interval={interval}s)")
    
    async def stop_monitoring(self):
        """Stop background resource monitoring."""
        self._monitoring = False
        if self._monitor_task:
            self._monitor_task.cancel()
            try:
                await self._monitor_task
            except asyncio.CancelledError:
                pass
    
    async def _monitor_loop(self, interval: float):
        """Background monitoring loop."""
        while self._monitoring:
            try:
                snapshot = self.get_current_snapshot()
                self._snapshots.append(snapshot)
                await self._check_thresholds(snapshot)
                await asyncio.sleep(interval)
            except Exception as e:
                logger.error(f"Resource monitoring error: {e}")
                await asyncio.sleep(interval)
    
    async def _check_thresholds(self, snapshot: ResourceSnapshot):
        """Check resource thresholds and trigger alerts."""
        if snapshot.cpu_percent >= self.thresholds.cpu_critical:
            await self._trigger_alerts('cpu', 'critical', snapshot)
        elif snapshot.cpu_percent >= self.thresholds.cpu_warning:
            await self._trigger_alerts('cpu', 'warning', snapshot)
        
        if snapshot.memory_percent >= self.thresholds.memory_critical:
            await self._trigger_alerts('memory', 'critical', snapshot)
        elif snapshot.memory_percent >= self.thresholds.memory_warning:
            await self._trigger_alerts('memory', 'warning', snapshot)
    
    def register_alert(self, resource: str, level: str, callback: Callable):
        """Register alert callback."""
        if resource in self._alert_callbacks and level in self._alert_callbacks[resource]:
            self._alert_callbacks[resource][level].append(callback)
    
    async def _trigger_alerts(self, resource: str, level: str, snapshot: ResourceSnapshot):
        """Trigger alert callbacks."""
        for callback in self._alert_callbacks.get(resource, {}).get(level, []):
            try:
                if asyncio.iscoroutinefunction(callback):
                    await callback(snapshot)
                else:
                    callback(snapshot)
            except Exception as e:
                logger.error(f"Alert callback error: {e}")
    
    def get_performance_summary(self, window: Optional[timedelta] = None) -> Dict:
        """Get performance summary over time window."""
        snapshots = list(self._snapshots)
        if not snapshots:
            return {}
        
        if window:
            cutoff = datetime.now() - window
            snapshots = [s for s in snapshots if s.timestamp >= cutoff]
        
        if not snapshots:
            return {}
        
        def get_stats(values):
            return {
                'min': min(values),
                'max': max(values),
                'avg': statistics.mean(values),
                'median': statistics.median(values)
            }
        
        return {
            'samples': len(snapshots),
            'cpu_percent': get_stats([s.cpu_percent for s in snapshots]),
            'memory_percent': get_stats([s.memory_percent for s in snapshots]),
            'memory_mb': get_stats([s.memory_mb for s in snapshots])
        }
    
    def detect_bottlenecks(self) -> List[Dict]:
        """Detect performance bottlenecks."""
        bottlenecks = []
        if len(self._snapshots) < 10:
            return bottlenecks
        
        recent = list(self._snapshots)[-10:]
        avg_cpu = statistics.mean(s.cpu_percent for s in recent)
        avg_memory = statistics.mean(s.memory_percent for s in recent)
        
        if avg_cpu > 80:
            bottlenecks.append({
                'type': 'cpu',
                'severity': 'high' if avg_cpu > 90 else 'moderate',
                'value': avg_cpu,
                'message': f'High CPU usage: {avg_cpu:.1f}%'
            })
        
        if avg_memory > 80:
            bottlenecks.append({
                'type': 'memory',
                'severity': 'high' if avg_memory > 90 else 'moderate',
                'value': avg_memory,
                'message': f'High memory usage: {avg_memory:.1f}%'
            })
        
        return bottlenecks

import logging
import psutil
import threading
import time
from typing import Dict, List, Optional
from monitoring.configuration import MonitoringConfig
from monitoring.models import MetricRecord

logger = logging.getLogger("AURA.Monitoring.Metrics")


class MetricsCollector:
    """
    Performance Metrics Collector.
    Records latency, system usage (CPU, RAM, Disk, Threads), and workflow throughput passively.
    """

    def __init__(self, config: Optional[MonitoringConfig] = None):
        self.config = config or MonitoringConfig()
        self.metrics: List[MetricRecord] = []
        self._lock = threading.Lock()

    def record_metric(self, name: str, value: float, unit: str = "ms", tags: Optional[Dict[str, str]] = None) -> MetricRecord:
        record = MetricRecord(
            name=name,
            value=value,
            unit=unit,
            tags=tags or {}
        )
        with self._lock:
            self.metrics.append(record)
            if len(self.metrics) > self.config.max_metrics_history:
                self.metrics.pop(0)

        logger.debug(f"Metric Recorded: '{name}' = {value}{unit}")
        return record

    def collect_system_metrics(self) -> Dict[str, float]:
        """Collect current CPU, RAM, Disk, and Thread system metrics."""

        cpu = psutil.cpu_percent(interval=None)
        mem = psutil.virtual_memory().percent
        threads = threading.active_count()

        self.record_metric("system.cpu_percent", cpu, "%")
        self.record_metric("system.ram_percent", mem, "%")
        self.record_metric("system.thread_count", float(threads), "count")

        return {
            "cpu_percent": cpu,
            "ram_percent": mem,
            "thread_count": float(threads),
        }

    def get_recent_metrics(self, limit: int = 50) -> List[MetricRecord]:
        with self._lock:
            return list(self.metrics[-limit:])

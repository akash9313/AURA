from dataclasses import dataclass


@dataclass
class MonitoringConfig:
    """Configurable settings for Observability and Telemetry platform."""
    collection_interval_seconds: float = 5.0
    max_metrics_history: int = 1000
    export_format: str = "json"  # json, csv, prometheus
    prometheus_enabled: bool = True
    log_level: str = "INFO"
    health_check_interval_seconds: float = 10.0

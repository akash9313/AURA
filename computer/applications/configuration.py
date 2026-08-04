from dataclasses import dataclass


@dataclass
class ApplicationManagerConfig:
    launch_timeout_ms: float = 10000.0
    readiness_timeout_ms: float = 5000.0
    resource_poll_interval_ms: float = 2000.0
    max_restart_retries: int = 3
    enable_process_monitoring: bool = True

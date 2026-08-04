"""
Application Manager Configuration.
Configures launch timeouts, readiness timeouts, restart policies, and resource polling intervals.
"""

from dataclasses import dataclass


@dataclass
class ApplicationManagerConfig:
    """Configuration parameters for Application Manager Subsystem."""
    launch_timeout_ms: float = 10000.0
    readiness_timeout_ms: float = 5000.0
    resource_poll_interval_ms: float = 2000.0
    max_restart_retries: int = 3
    enable_process_monitoring: bool = True

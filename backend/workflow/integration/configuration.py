"""
Workflow Integration Configuration.
Configures execution timeouts, parallel task limits, retry policies, and progress intervals.
"""

from dataclasses import dataclass


@dataclass
class WorkflowIntegrationConfig:
    """Configuration parameters for Workflow Executor Integration Subsystem."""
    max_execution_time_sec: float = 300.0
    parallel_task_limit: int = 4
    max_retries: int = 3
    backoff_sec: float = 1.0
    progress_interval_sec: float = 0.5
    require_empirical_verification: bool = True

from dataclasses import dataclass


@dataclass
class WorkflowIntegrationConfig:
    max_execution_time_sec: float = 300.0
    parallel_task_limit: int = 4
    max_retries: int = 3
    backoff_sec: float = 1.0
    progress_interval_sec: float = 0.5
    require_empirical_verification: bool = True

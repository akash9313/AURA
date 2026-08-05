from dataclasses import dataclass


@dataclass
class PlannerConfig:
    max_tasks: int = 50
    default_retry_count: int = 2
    default_backoff_sec: float = 1.0
    enable_recovery_checkpoints: bool = True

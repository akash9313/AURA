"""
AI Planner Engine Configuration.
Configures maximum task counts, retry policies, and recovery point parameters.
"""

from dataclasses import dataclass


@dataclass
class PlannerConfig:
    """Configuration parameters for AI Planner Subsystem."""
    max_tasks: int = 50
    default_retry_count: int = 2
    default_backoff_sec: float = 1.0
    enable_recovery_checkpoints: bool = True

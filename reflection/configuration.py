from dataclasses import dataclass


@dataclass
class ReflectionConfig:
    slow_task_threshold_ms: float = 5000.0
    frequent_retry_threshold: int = 2
    min_confidence_score: float = 0.6
    enable_auto_recommendations: bool = True

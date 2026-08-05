from dataclasses import dataclass


@dataclass
class MissionMemoryConfig:
    retention_days: int = 90
    max_experiences_per_goal: int = 50
    auto_compress_after_days: int = 30
    similarity_threshold: float = 0.5

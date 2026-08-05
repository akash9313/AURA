from dataclasses import dataclass


@dataclass
class TaskGraphConfig:
    max_nodes: int = 10000
    graph_creation_timeout_ms: float = 50.0
    enable_parallel_scheduling: bool = True
    auto_checkpoint: bool = True
    default_timeout_sec: float = 60.0

from dataclasses import dataclass


@dataclass
class WorkflowExecutorConfig:
    max_parallel_tasks: int = 4
    task_timeout_sec: float = 60.0
    workflow_timeout_sec: float = 600.0
    max_task_retries: int = 2
    checkpoint_frequency: int = 1
    auto_checkpoint: bool = True

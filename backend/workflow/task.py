from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Set
from workflow.models import TaskMetric, TaskState, TaskType


@dataclass
class WorkflowTask:
    """Represents an atomic, executable step within a workflow DAG graph."""
    task_id: str
    tool: str
    description: str
    parameters: Dict[str, Any] = field(default_factory=dict)
    dependencies: Set[str] = field(default_factory=set)
    priority: int = 1
    timeout_seconds: float = 60.0
    max_retries: int = 3
    optional: bool = False
    task_type: TaskType = TaskType.CUSTOM
    state: TaskState = TaskState.PENDING
    result: Optional[Dict[str, Any]] = None
    metrics: TaskMetric = field(default_factory=TaskMetric)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "task_id": self.task_id,
            "tool": self.tool,
            "description": self.description,
            "parameters": self.parameters,
            "dependencies": list(self.dependencies),
            "priority": self.priority,
            "timeout_seconds": self.timeout_seconds,
            "max_retries": self.max_retries,
            "optional": self.optional,
            "task_type": self.task_type.value,
            "state": self.state.value,
            "result": self.result,
        }

import uuid
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional
from agent.state import TaskStatus


@dataclass
class Task:
    """
    Represents an atomic task step in an Agent Workflow.
    """
    tool_name: str
    parameters: Dict[str, Any] = field(default_factory=dict)
    task_id: str = field(default_factory=lambda: str(uuid.uuid4())[:8])
    priority: int = 1
    dependencies: List[str] = field(default_factory=list)
    retry_count: int = 0
    max_retries: int = 3
    status: TaskStatus = TaskStatus.PENDING
    estimated_time: float = 1.0
    result: Optional[Any] = None

    def is_ready(self, completed_task_ids: List[str]) -> bool:
        """Check if all parent dependency tasks have completed."""
        return all(dep_id in completed_task_ids for dep_id in self.dependencies)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "task_id": self.task_id,
            "tool_name": self.tool_name,
            "parameters": self.parameters,
            "priority": self.priority,
            "dependencies": self.dependencies,
            "retry_count": self.retry_count,
            "max_retries": self.max_retries,
            "status": self.status.value,
            "estimated_time": self.estimated_time
        }
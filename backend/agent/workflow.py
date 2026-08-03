import uuid
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Dict, List, Optional
from agent.state import TaskStatus, WorkflowState
from agent.task import Task


@dataclass
class Workflow:
    """
    Represents an orchestrated multi-task workflow resolving a user goal.
    """
    goal: str
    tasks: List[Task] = field(default_factory=list)
    workflow_id: str = field(default_factory=lambda: f"wf_{str(uuid.uuid4())[:8]}")
    status: WorkflowState = WorkflowState.CREATED
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)
    metadata: Dict[str, Any] = field(default_factory=dict)

    def get_ready_tasks(self) -> List[Task]:
        """Return all pending tasks whose dependencies are completed."""
        completed_ids = [t.task_id for t in self.tasks if t.status == TaskStatus.COMPLETED]
        return [
            t for t in self.tasks
            if t.status == TaskStatus.PENDING and t.is_ready(completed_ids)
        ]

    def is_finished(self) -> bool:
        """Check if workflow execution has terminated."""
        return self.status in (WorkflowState.COMPLETED, WorkflowState.FAILED, WorkflowState.CANCELLED)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "workflow_id": self.workflow_id,
            "goal": self.goal,
            "tasks": [t.to_dict() for t in self.tasks],
            "status": self.status.value,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
            "metadata": self.metadata
        }

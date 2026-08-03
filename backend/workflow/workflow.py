from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Set
import time

from workflow.models import TaskState, WorkflowMetric, WorkflowState
from workflow.task import WorkflowTask


@dataclass
class Workflow:
    """Represents a multi-step autonomous mission containing a DAG of tasks."""
    workflow_id: str
    goal: str
    tasks: Dict[str, WorkflowTask] = field(default_factory=dict)
    state: WorkflowState = WorkflowState.CREATED
    metrics: WorkflowMetric = field(default_factory=WorkflowMetric)
    context: Dict[str, Any] = field(default_factory=dict)

    def add_task(self, task: WorkflowTask) -> None:
        """Add task node to workflow graph."""
        self.tasks[task.task_id] = task
        self.metrics.total_tasks = len(self.tasks)

    def get_ready_tasks(self) -> List[WorkflowTask]:
        """Get tasks whose dependencies are all COMPLETED and state is PENDING."""
        ready = []
        for task in self.tasks.values():
            if task.state == TaskState.PENDING:
                parents_done = all(
                    self.tasks[parent_id].state in (TaskState.COMPLETED, TaskState.SKIPPED)
                    for parent_id in task.dependencies
                    if parent_id in self.tasks
                )
                if parents_done:
                    ready.append(task)
        # Sort by priority descending
        ready.sort(key=lambda t: t.priority, reverse=True)
        return ready

    def is_finished(self) -> bool:
        """Check if all tasks are in terminal states."""
        return all(t.state in (TaskState.COMPLETED, TaskState.FAILED, TaskState.SKIPPED) for t in self.tasks.values())

    def to_dict(self) -> Dict[str, Any]:

        return {
            "workflow_id": self.workflow_id,
            "goal": self.goal,
            "state": self.state.value,
            "metrics": self.metrics.to_dict(),
            "tasks": {tid: task.to_dict() for tid, task in self.tasks.items()},
        }

import time
import uuid
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List, Optional, Set


@dataclass
class PlannerTask:
    task_id: str = field(default_factory=lambda: f"task_{uuid.uuid4().hex[:8]}")
    description: str = ""
    capability_required: str = ""
    inputs: Dict[str, Any] = field(default_factory=dict)
    outputs: Dict[str, Any] = field(default_factory=dict)
    dependencies: List[str] = field(default_factory=list)
    verification_rule: Dict[str, Any] = field(default_factory=dict)
    retry_policy: Dict[str, Any] = field(default_factory=lambda: {"max_retries": 2, "backoff_sec": 1.0})
    is_recovery_point: bool = False

    def to_dict(self) -> Dict[str, Any]:
        return {
            "task_id": self.task_id,
            "description": self.description,
            "capability_required": self.capability_required,
            "inputs": self.inputs,
            "outputs": self.outputs,
            "dependencies": self.dependencies,
            "verification_rule": self.verification_rule,
            "retry_policy": self.retry_policy,
            "is_recovery_point": self.is_recovery_point,
        }


@dataclass
class TaskGraph:
    graph_id: str = field(default_factory=lambda: f"graph_{uuid.uuid4().hex[:8]}")
    tasks: Dict[str, PlannerTask] = field(default_factory=dict)
    root_task_ids: List[str] = field(default_factory=list)

    def add_task(self, task: PlannerTask) -> None:
        self.tasks[task.task_id] = task
        if not task.dependencies:
            if task.task_id not in self.root_task_ids:
                self.root_task_ids.append(task.task_id)

    def get_task(self, task_id: str) -> Optional[PlannerTask]:
        return self.tasks.get(task_id)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "graph_id": self.graph_id,
            "task_count": len(self.tasks),
            "root_task_ids": self.root_task_ids,
            "tasks": {tid: task.to_dict() for tid, task in self.tasks.items()},
        }


@dataclass
class PlanningContext:
    user_request: str
    current_memory: Dict[str, Any] = field(default_factory=dict)
    available_tools: List[str] = field(default_factory=list)
    desktop_state: Dict[str, Any] = field(default_factory=dict)
    browser_state: Dict[str, Any] = field(default_factory=dict)
    application_state: Dict[str, Any] = field(default_factory=dict)


@dataclass
class MissionPlan:
    plan_id: str = field(default_factory=lambda: f"plan_{uuid.uuid4().hex[:8]}")
    user_request: str = ""
    goal_summary: str = ""
    task_graph: TaskGraph = field(default_factory=TaskGraph)
    recovery_points: List[str] = field(default_factory=list)
    created_at: float = field(default_factory=time.time)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "plan_id": self.plan_id,
            "user_request": self.user_request,
            "goal_summary": self.goal_summary,
            "task_graph": self.task_graph.to_dict(),
            "recovery_points": self.recovery_points,
            "created_at": self.created_at,
        }


@dataclass
class PlanningResult:
    success: bool
    plan: Optional[MissionPlan]
    message: str
    duration_ms: float = 0.0
    timestamp: float = field(default_factory=time.time)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "success": self.success,
            "plan": self.plan.to_dict() if self.plan else None,
            "message": self.message,
            "duration_ms": self.duration_ms,
            "timestamp": self.timestamp,
        }

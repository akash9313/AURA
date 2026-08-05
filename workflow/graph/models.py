import time
import uuid
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List, Optional, Set


class NodeStatus(Enum):
    PENDING = "pending"
    READY = "ready"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    SKIPPED = "skipped"
    BLOCKED = "blocked"


class EdgeType(Enum):
    HARD = "hard"
    SOFT = "soft"
    CONDITIONAL = "conditional"
    PARALLEL = "parallel"


@dataclass
class GraphNode:
    task_id: str = field(default_factory=lambda: f"node_{uuid.uuid4().hex[:8]}")
    name: str = ""
    capability: str = ""
    inputs: Dict[str, Any] = field(default_factory=dict)
    outputs: Dict[str, Any] = field(default_factory=dict)
    dependencies: List[str] = field(default_factory=list)
    estimated_duration: float = 1.0
    priority: int = 10
    verification_rule: Dict[str, Any] = field(default_factory=dict)
    retry_policy: Dict[str, Any] = field(default_factory=lambda: {"max_retries": 2, "backoff_sec": 1.0})
    timeout: float = 60.0
    status: NodeStatus = NodeStatus.PENDING

    def to_dict(self) -> Dict[str, Any]:
        return {
            "task_id": self.task_id,
            "name": self.name,
            "capability": self.capability,
            "inputs": self.inputs,
            "outputs": self.outputs,
            "dependencies": self.dependencies,
            "estimated_duration": self.estimated_duration,
            "priority": self.priority,
            "verification_rule": self.verification_rule,
            "retry_policy": self.retry_policy,
            "timeout": self.timeout,
            "status": self.status.value,
        }


@dataclass
class GraphEdge:
    source_id: str
    target_id: str
    edge_type: EdgeType = EdgeType.HARD
    condition_expr: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "source_id": self.source_id,
            "target_id": self.target_id,
            "edge_type": self.edge_type.value,
            "condition_expr": self.condition_expr,
        }


@dataclass
class ExecutionStage:
    stage_index: int
    task_ids: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "stage_index": self.stage_index,
            "task_ids": self.task_ids,
        }


@dataclass
class CriticalPath:
    total_duration: float
    path_task_ids: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "total_duration": self.total_duration,
            "path_task_ids": self.path_task_ids,
        }


@dataclass
class GraphCheckpoint:
    checkpoint_id: str = field(default_factory=lambda: f"ckpt_{uuid.uuid4().hex[:8]}")
    graph_id: str = ""
    completed_tasks: List[str] = field(default_factory=list)
    task_outputs: Dict[str, Dict[str, Any]] = field(default_factory=dict)
    current_context: Dict[str, Any] = field(default_factory=dict)
    verification_results: Dict[str, Dict[str, Any]] = field(default_factory=dict)
    created_at: float = field(default_factory=time.time)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "checkpoint_id": self.checkpoint_id,
            "graph_id": self.graph_id,
            "completed_tasks": self.completed_tasks,
            "task_outputs": self.task_outputs,
            "current_context": self.current_context,
            "verification_results": self.verification_results,
            "created_at": self.created_at,
        }

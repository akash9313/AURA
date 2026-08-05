import logging
from typing import Any, Dict, List, Optional

from workflow.graph.models import GraphNode, NodeStatus

logger = logging.getLogger("AURA.Workflow.Graph.Node")


class NodeBuilder:
    def __init__(self, name: str, capability: str, task_id: Optional[str] = None):
        kwargs = {"name": name, "capability": capability}
        if task_id:
            kwargs["task_id"] = task_id
        self._node = GraphNode(**kwargs)

    def with_inputs(self, inputs: Dict[str, Any]) -> "NodeBuilder":
        self._node.inputs.update(inputs)
        return self

    def with_outputs(self, outputs: Dict[str, Any]) -> "NodeBuilder":
        self._node.outputs.update(outputs)
        return self

    def depends_on(self, dependency_ids: List[str]) -> "NodeBuilder":
        self._node.dependencies.extend(dependency_ids)
        return self

    def with_duration(self, estimated_duration: float) -> "NodeBuilder":
        self._node.estimated_duration = estimated_duration
        return self

    def with_priority(self, priority: int) -> "NodeBuilder":
        self._node.priority = priority
        return self

    def with_verification(self, verification_rule: Dict[str, Any]) -> "NodeBuilder":
        self._node.verification_rule.update(verification_rule)
        return self

    def with_retry_policy(self, max_retries: int = 2, backoff_sec: float = 1.0) -> "NodeBuilder":
        self._node.retry_policy = {"max_retries": max_retries, "backoff_sec": backoff_sec}
        return self

    def with_timeout(self, timeout_sec: float) -> "NodeBuilder":
        self._node.timeout = timeout_sec
        return self

    def build(self) -> GraphNode:
        return self._node

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional
from agent.workflow import Workflow


@dataclass
class AgentContext:
    """
    Context store maintaining runtime state during workflow execution.
    """
    goal: str
    conversation_id: str = ""
    workflow: Optional[Workflow] = None
    working_memory: Dict[str, Any] = field(default_factory=dict)
    temp_variables: Dict[str, Any] = field(default_factory=dict)
    tool_outputs: Dict[str, Any] = field(default_factory=dict)
    planner_notes: List[str] = field(default_factory=list)

    def set_output(self, task_id: str, output: Any) -> None:
        """Record output of an executed task."""
        self.tool_outputs[task_id] = output

    def get_output(self, task_id: str, default: Any = None) -> Any:
        """Get output produced by a prior task."""
        return self.tool_outputs.get(task_id, default)

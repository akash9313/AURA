from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional


@dataclass
class TaskResult:
    """
    Result returned upon execution of an individual agent task.
    """
    success: bool
    output: Any = None
    error: Optional[str] = None
    logs: List[str] = field(default_factory=list)
    execution_time: float = 0.0
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "success": self.success,
            "output": self.output,
            "error": self.error,
            "logs": self.logs,
            "execution_time": self.execution_time,
            "metadata": self.metadata
        }

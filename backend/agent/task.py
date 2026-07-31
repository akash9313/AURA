from dataclasses import dataclass, field
from typing import Dict, Any
from typing import List
from agent.task import Task


@dataclass
class Task:
    id: str
    action: str
    parameters: Dict[str, Any] = field(default_factory=dict)
    status: str = "pending"

@dataclass
class ExecutionPlan:
    tasks: List[Task] = field(default_factory=list)
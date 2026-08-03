from enum import Enum


class WorkflowState(Enum):
    """Execution states for an Agent Workflow."""
    CREATED = "created"
    PLANNING = "planning"
    READY = "ready"
    RUNNING = "running"
    WAITING = "waiting"
    RETRYING = "retrying"
    FAILED = "failed"
    CANCELLED = "cancelled"
    COMPLETED = "completed"


class TaskStatus(Enum):
    """Execution states for individual Workflow Tasks."""
    PENDING = "pending"
    RUNNING = "running"
    WAITING = "waiting"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"

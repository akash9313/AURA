"""
Workflow Integration Event Definitions.
Published to EventBus during Workflow Execution lifecycle.
"""

from enum import Enum


class WorkflowIntegrationEvent(Enum):
    """Event definitions for Workflow Executor Integration Subsystem."""
    MISSION_STARTED = "mission_started"
    MISSION_PROGRESS = "mission_progress"
    TASK_STARTED = "task_started"
    TASK_COMPLETED = "task_completed"
    TASK_FAILED = "task_failed"
    MISSION_COMPLETED = "mission_completed"
    MISSION_CANCELLED = "mission_cancelled"

from enum import Enum


class WorkflowIntegrationEvent(Enum):
    MISSION_STARTED = "mission_started"
    MISSION_PROGRESS = "mission_progress"
    TASK_STARTED = "task_started"
    TASK_COMPLETED = "task_completed"
    TASK_FAILED = "task_failed"
    MISSION_COMPLETED = "mission_completed"
    MISSION_CANCELLED = "mission_cancelled"

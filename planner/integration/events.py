from enum import Enum


class PlannerIntegrationEvent(Enum):
    MISSION_CREATED = "mission_created"
    MISSION_PLANNED = "mission_planned"
    MISSION_EXECUTION_REQUESTED = "mission_execution_requested"
    MISSION_COMPLETED = "mission_completed"
    MISSION_FAILED = "mission_failed"

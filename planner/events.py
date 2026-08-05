from enum import Enum


class PlannerEvent(Enum):
    PLAN_CREATED = "plan_created"
    PLAN_UPDATED = "plan_updated"
    PLAN_FAILED = "plan_failed"
    MISSION_STARTED = "mission_started"

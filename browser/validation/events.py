from enum import Enum


class BrowserValidationEvent(Enum):
    MISSION_STARTED = "mission_started"
    CAPABILITY_STARTED = "capability_started"
    VERIFICATION_COMPLETED = "verification_completed"
    MISSION_COMPLETED = "mission_completed"
    MISSION_FAILED = "mission_failed"

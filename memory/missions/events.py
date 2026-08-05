from enum import Enum


class MissionMemoryEvent(Enum):
    MISSION_STORED = "mission_stored"
    MISSION_UPDATED = "mission_updated"
    MISSION_ARCHIVED = "mission_archived"
    EXPERIENCE_CREATED = "experience_created"
    EXPERIENCE_RETRIEVED = "experience_retrieved"

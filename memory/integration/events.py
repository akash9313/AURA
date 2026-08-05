from enum import Enum


class MissionMemoryIntegrationEvent(Enum):
    MISSION_STORED = "mission_stored"
    MISSION_RETRIEVED = "mission_retrieved"
    SIMILAR_MISSIONS_FOUND = "similar_missions_found"
    MISSION_ARCHIVED = "mission_archived"

"""
Mission Memory Integration Events.
Published to EventBus during Mission Memory lifecycle.
"""

from enum import Enum


class MissionMemoryIntegrationEvent(Enum):
    """Event definitions for Mission Memory Integration Subsystem."""
    MISSION_STORED = "mission_stored"
    MISSION_RETRIEVED = "mission_retrieved"
    SIMILAR_MISSIONS_FOUND = "similar_missions_found"
    MISSION_ARCHIVED = "mission_archived"

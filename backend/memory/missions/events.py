"""
Mission Memory Event Definitions.
Published to AURA EventBus when missions and experiences are stored, retrieved, and archived.
"""

from enum import Enum


class MissionMemoryEvent(Enum):
    """Event definitions for Mission Memory Engine."""
    MISSION_STORED = "mission_stored"
    MISSION_UPDATED = "mission_updated"
    MISSION_ARCHIVED = "mission_archived"
    EXPERIENCE_CREATED = "experience_created"
    EXPERIENCE_RETRIEVED = "experience_retrieved"

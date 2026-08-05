"""
Mission Primary Storage Store.
Persists and retrieves full operational MissionRecord instances.
"""

import logging
from typing import Dict, List, Optional

from memory.missions.models import MissionRecord

logger = logging.getLogger("AURA.Memory.Missions.MissionStore")


class MissionStore:
    """
    In-memory repository storing MissionRecord instances.
    """

    def __init__(self):
        self._missions: Dict[str, MissionRecord] = {}

    def save(self, record: MissionRecord) -> None:
        """Save or update mission record."""
        self._missions[record.mission_id] = record
        logger.debug(f"Saved MissionRecord '{record.mission_id}'")

    def get(self, mission_id: str) -> Optional[MissionRecord]:
        """Retrieve mission record by ID."""
        return self._missions.get(mission_id)

    def list_all(self) -> List[MissionRecord]:
        """List all stored mission records."""
        return list(self._missions.values())

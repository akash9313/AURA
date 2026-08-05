import logging
from typing import Dict, List, Optional

from memory.missions.models import MissionRecord

logger = logging.getLogger("AURA.Memory.Missions.MissionStore")


class MissionStore:
    def __init__(self):
        self._missions: Dict[str, MissionRecord] = {}

    def save(self, record: MissionRecord) -> None:
        self._missions[record.mission_id] = record

    def get(self, mission_id: str) -> Optional[MissionRecord]:
        return self._missions.get(mission_id)

    def list_all(self) -> List[MissionRecord]:
        return list(self._missions.values())

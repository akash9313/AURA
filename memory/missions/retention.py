import logging
import time
from typing import List, Tuple

from memory.missions.configuration import MissionMemoryConfig
from memory.missions.models import MissionRecord

logger = logging.getLogger("AURA.Memory.Missions.Retention")


class MissionRetentionPolicy:
    def __init__(self, config: MissionMemoryConfig):
        self.config = config

    def apply_retention(self, records: List[MissionRecord]) -> Tuple[List[MissionRecord], List[str]]:
        now = time.time()
        retention_sec = self.config.retention_days * 86400.0

        active = []
        archived_ids = []

        for r in records:
            age_sec = now - r.created_at
            if age_sec > retention_sec:
                r.archived = True
                archived_ids.append(r.mission_id)
            else:
                active.append(r)

        return (active, archived_ids)

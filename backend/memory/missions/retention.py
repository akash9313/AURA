"""
Mission Retention Policy Engine.
Enforces data retention policies (Archival, Deletion, Compression, Versioning, Expiration).
"""

import logging
import time
from typing import List

from memory.missions.configuration import MissionMemoryConfig
from memory.missions.models import MissionRecord

logger = logging.getLogger("AURA.Memory.Missions.Retention")


class MissionRetentionPolicy:
    """
    Manages operational mission memory lifecycle and retention rules.
    """

    def __init__(self, config: MissionMemoryConfig):
        self.config = config

    def apply_retention(self, records: List[MissionRecord]) -> Tuple[List[MissionRecord], List[str]]:
        """
        Evaluate retention policy rules against mission records.

        Returns:
            Tuple of (active_records: List[MissionRecord], archived_ids: List[str]).
        """
        now = time.time()
        retention_sec = self.config.retention_days * 86400.0

        active = []
        archived_ids = []

        for r in records:
            age_sec = now - r.created_at
            if age_sec > retention_sec:
                r.archived = True
                archived_ids.append(r.mission_id)
                logger.info(f"Archived mission '{r.mission_id}' due to retention expiration ({self.config.retention_days} days)")
            else:
                active.append(r)

        return (active, archived_ids)

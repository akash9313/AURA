"""
Mission Persistence (Repository Pattern).
Manages persistence, querying, and archiving of OperationalMissionRecord instances in Mission Memory.
Handles storage errors, corrupted records, and missing metadata.
"""

import json
import logging
from typing import Dict, List, Optional

from memory.integration.models import OperationalMissionRecord

logger = logging.getLogger("AURA.Memory.Integration.Persistence")


class StorageError(Exception):
    """Raised when mission record storage fails."""
    pass


class CorruptedRecordError(Exception):
    """Raised when mission memory record is corrupted or missing essential fields."""
    pass


class MissionPersistence:
    """
    Repository pattern persistence store for OperationalMissionRecord objects.
    """

    def __init__(self):
        self._records: Dict[str, OperationalMissionRecord] = {}
        self._archived: Dict[str, OperationalMissionRecord] = {}

    def save_mission_record(self, record: OperationalMissionRecord) -> None:
        """
        Persist OperationalMissionRecord to memory store.

        Args:
            record: OperationalMissionRecord object.

        Raises:
            CorruptedRecordError: If mission_id or goal is missing.
            StorageError: If storage operation fails.
        """
        if not record.mission_id or not record.goal:
            raise CorruptedRecordError("Mission record missing mission_id or goal metadata!")

        try:
            # Validate JSON serializability to prevent corrupted objects
            _ = json.dumps(record.to_dict())
            self._records[record.mission_id] = record
            logger.info(f"Successfully persisted OperationalMissionRecord '{record.mission_id}' to Mission Memory.")
        except Exception as e:
            err_msg = f"Failed to persist mission record '{record.mission_id}': {str(e)}"
            logger.error(err_msg)
            raise StorageError(err_msg)

    def get_mission_record(self, mission_id: str) -> Optional[OperationalMissionRecord]:
        """Retrieve MissionRecord by ID."""
        return self._records.get(mission_id) or self._archived.get(mission_id)

    def list_all_records(self) -> List[OperationalMissionRecord]:
        """List all active mission records."""
        return list(self._records.values())

    def archive_mission_record(self, mission_id: str) -> bool:
        """Archive record by moving to archive store."""
        if mission_id in self._records:
            record = self._records.pop(mission_id)
            self._archived[mission_id] = record
            logger.info(f"Archived mission record '{mission_id}'.")
            return True
        return False

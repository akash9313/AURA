import json
import logging
from typing import Dict, List, Optional

from memory.integration.models import OperationalMissionRecord

logger = logging.getLogger("AURA.Memory.Integration.Persistence")


class StorageError(Exception):
    pass


class CorruptedRecordError(Exception):
    pass


class MissionPersistence:
    def __init__(self):
        self._records: Dict[str, OperationalMissionRecord] = {}
        self._archived: Dict[str, OperationalMissionRecord] = {}

    def save_mission_record(self, record: OperationalMissionRecord) -> None:
        if not record.mission_id or not record.goal:
            raise CorruptedRecordError("Mission record missing mission_id or goal metadata!")

        try:
            _ = json.dumps(record.to_dict())
            self._records[record.mission_id] = record
        except Exception as e:
            err_msg = f"Failed to persist mission record '{record.mission_id}': {str(e)}"
            raise StorageError(err_msg)

    def get_mission_record(self, mission_id: str) -> Optional[OperationalMissionRecord]:
        return self._records.get(mission_id) or self._archived.get(mission_id)

    def list_all_records(self) -> List[OperationalMissionRecord]:
        return list(self._records.values())

    def archive_mission_record(self, mission_id: str) -> bool:
        if mission_id in self._records:
            record = self._records.pop(mission_id)
            self._archived[mission_id] = record
            return True
        return False

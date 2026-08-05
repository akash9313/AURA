import logging
from typing import Dict, List, Optional

from memory.missions.models import MissionCheckpointRecord

logger = logging.getLogger("AURA.Memory.Missions.CheckpointStore")


class CheckpointStore:
    def __init__(self):
        self._checkpoints: Dict[str, MissionCheckpointRecord] = {}

    def save(self, ckpt: MissionCheckpointRecord) -> None:
        self._checkpoints[ckpt.checkpoint_id] = ckpt

    def get(self, checkpoint_id: str) -> Optional[MissionCheckpointRecord]:
        return self._checkpoints.get(checkpoint_id)

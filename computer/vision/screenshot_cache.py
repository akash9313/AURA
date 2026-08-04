import hashlib
import logging
import time
from typing import Dict, Optional, Tuple

from computer.vision.models import ScreenSnapshot

logger = logging.getLogger("AURA.Computer.Vision.Cache")


class ScreenshotCache:
    def __init__(self, max_capacity: int = 20):
        self.max_capacity = max_capacity
        self._snapshots: Dict[str, ScreenSnapshot] = {}
        self._latest_hash: str = ""

    def put(self, snapshot: ScreenSnapshot) -> str:
        if len(self._snapshots) >= self.max_capacity:
            oldest_id = min(self._snapshots.keys(), key=lambda k: self._snapshots[k].timestamp)
            del self._snapshots[oldest_id]

        if not snapshot.image_hash:
            snapshot.image_hash = hashlib.sha256(f"{snapshot.bounds}_{snapshot.timestamp}".encode()).hexdigest()[:16]

        self._snapshots[snapshot.snapshot_id] = snapshot
        self._latest_hash = snapshot.image_hash
        return snapshot.image_hash

    def get(self, snapshot_id: str) -> Optional[ScreenSnapshot]:
        return self._snapshots.get(snapshot_id)

    def is_identical(self, new_hash: str) -> bool:
        return new_hash == self._latest_hash

    def clear(self) -> None:
        self._snapshots.clear()
        self._latest_hash = ""

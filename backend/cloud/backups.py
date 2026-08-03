import logging
import time
import uuid
from typing import Dict, List, Optional
from cloud.models import BackupSnapshot

logger = logging.getLogger("AURA.Cloud.Backups")


class BackupManager:
    """Manages automatic/manual backup creation, version history, export, and restoration."""

    def __init__(self):
        self.backups: Dict[str, BackupSnapshot] = {}

    def create_backup(self, user_id: str, data: Dict) -> BackupSnapshot:
        backup_id = f"bak_{uuid.uuid4().hex[:8]}"
        snapshot = BackupSnapshot(
            backup_id=backup_id,
            user_id=user_id,
            version="1.0.0",
            created_at=time.time(),
            data=data
        )
        self.backups[backup_id] = snapshot
        logger.info(f"Created backup snapshot '{backup_id}' for user '{user_id}'")
        return snapshot

    def restore_backup(self, backup_id: str) -> Optional[BackupSnapshot]:
        snapshot = self.backups.get(backup_id)
        if snapshot:
            logger.info(f"Restored backup snapshot '{backup_id}'")
            return snapshot
        return None

    def list_backups(self, user_id: str) -> List[BackupSnapshot]:
        return [b for b in self.backups.values() if b.user_id == user_id]

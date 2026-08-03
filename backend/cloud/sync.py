import logging
import time
import uuid
from typing import Dict, Optional
from cloud.conflicts import ConflictResolver
from cloud.models import ConflictPolicy, SyncPayload

logger = logging.getLogger("AURA.Cloud.Sync")


class SyncEngine:
    """
    Multi-device synchronization engine for Preferences, Memory, Knowledge, Workflows, and Settings.
    """

    def __init__(self, conflict_resolver: Optional[ConflictResolver] = None):
        self.conflict_resolver = conflict_resolver if conflict_resolver is not None else ConflictResolver()
        self.cloud_store: Dict[str, SyncPayload] = {}  # user_id -> SyncPayload

    def sync_device(self, user_id: str, local_payload: SyncPayload, policy: ConflictPolicy = ConflictPolicy.LAST_WRITE_WINS) -> SyncPayload:
        remote_payload = self.cloud_store.get(user_id)

        if not remote_payload:
            self.cloud_store[user_id] = local_payload
            logger.info(f"Initialized initial cloud sync payload for user '{user_id}'")
            return local_payload

        resolved = self.conflict_resolver.resolve_conflict(local_payload, remote_payload, policy=policy)
        self.cloud_store[user_id] = resolved
        logger.info(f"Synchronized payload for user '{user_id}' across devices.")
        return resolved

import logging
from typing import Any, Dict
from cloud.models import ConflictPolicy, SyncPayload

logger = logging.getLogger("AURA.Cloud.Conflicts")


class ConflictResolver:
    """Conflict resolution engine supporting Last Write Wins, Timestamp Merge, and Manual Merge."""

    def resolve_conflict(self, local_payload: SyncPayload, remote_payload: SyncPayload, policy: ConflictPolicy = ConflictPolicy.LAST_WRITE_WINS) -> SyncPayload:
        if policy == ConflictPolicy.LAST_WRITE_WINS:
            if remote_payload.timestamp >= local_payload.timestamp:
                logger.info(f"Resolved conflict via Last Write Wins: remote timestamp ({remote_payload.timestamp}) selected.")
                return remote_payload
            return local_payload

        elif policy == ConflictPolicy.TIMESTAMP_MERGE:
            merged_prefs = dict(local_payload.preferences)
            if remote_payload.timestamp >= local_payload.timestamp:
                merged_prefs.update(remote_payload.preferences)

            merged_memory = dict(local_payload.memory)
            if remote_payload.timestamp >= local_payload.timestamp:
                merged_memory.update(remote_payload.memory)

            return SyncPayload(
                payload_id=f"merged_{local_payload.payload_id}",
                user_id=local_payload.user_id,
                device_id=local_payload.device_id,
                timestamp=max(local_payload.timestamp, remote_payload.timestamp),
                preferences=merged_prefs,
                memory=merged_memory,
                knowledge=remote_payload.knowledge or local_payload.knowledge,
                workflows=remote_payload.workflows or local_payload.workflows,
                settings=remote_payload.settings or local_payload.settings
            )

        return remote_payload

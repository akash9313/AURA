"""
State Snapshot Manager.
Captures and restores browser, session, page, and form state snapshots for post-crash self-healing.
"""

import logging
from typing import Any, Dict, List, Optional

from browser.recovery.models import StateSnapshot

logger = logging.getLogger("AURA.Browser.Recovery.Snapshot")


class SnapshotManager:
    """
    Manages capturing, storing, and restoring StateSnapshots.
    """

    def __init__(self):
        self._snapshots: Dict[str, StateSnapshot] = {}
        self._latest_by_workflow: Dict[str, str] = {}

    def capture_snapshot(
        self,
        current_url: str,
        navigation_history: Optional[List[str]] = None,
        session_id: Optional[str] = None,
        page_id: Optional[str] = None,
        workflow_id: Optional[str] = None,
        page_state: Optional[Dict[str, Any]] = None,
        form_values: Optional[Dict[str, str]] = None,
        cookie_metadata: Optional[List[Dict[str, Any]]] = None,
    ) -> StateSnapshot:
        """
        Create and store a StateSnapshot before an important action.

        Returns:
            Captured StateSnapshot object.
        """
        snapshot = StateSnapshot(
            current_url=current_url,
            navigation_history=navigation_history or [],
            session_id=session_id,
            page_id=page_id,
            workflow_id=workflow_id,
            page_state=page_state or {},
            form_values=form_values or {},
            cookie_metadata=cookie_metadata or [],
        )

        self._snapshots[snapshot.snapshot_id] = snapshot
        if workflow_id:
            self._latest_by_workflow[workflow_id] = snapshot.snapshot_id

        logger.info(f"Captured state snapshot '{snapshot.snapshot_id}' for URL: '{current_url}'")
        return snapshot

    def get_snapshot(self, snapshot_id: str) -> Optional[StateSnapshot]:
        """Retrieve snapshot by ID."""
        return self._snapshots.get(snapshot_id)

    def get_latest_workflow_snapshot(self, workflow_id: str) -> Optional[StateSnapshot]:
        """Retrieve the latest snapshot captured for a workflow."""
        snapshot_id = self._latest_by_workflow.get(workflow_id)
        return self.get_snapshot(snapshot_id) if snapshot_id else None

    def restore_snapshot(self, snapshot_id: str) -> Tuple[bool, Optional[StateSnapshot], str]:
        """
        Restore state from snapshot.

        Returns:
            Tuple of (success, snapshot_object, status_message)
        """
        snapshot = self.get_snapshot(snapshot_id)
        if not snapshot:
            logger.warning(f"Failed to restore: Snapshot ID '{snapshot_id}' not found")
            return (False, None, f"Snapshot '{snapshot_id}' not found")

        logger.info(f"Restoring state from snapshot '{snapshot_id}' (URL: '{snapshot.current_url}')")
        return (True, snapshot, f"Restored state for URL '{snapshot.current_url}'")

    def clear(self) -> None:
        """Clear stored snapshots."""
        self._snapshots.clear()
        self._latest_by_workflow.clear()
        logger.debug("Snapshot storage cleared")

"""
Application Registry (Repository Pattern).
Maintains in-memory repository of tracked AURAApplication instances.
Maps raw OS process IDs internally to clean platform-independent Application IDs.
"""

import logging
from typing import Any, Dict, List, Optional

from computer.applications.models import AURAApplication

logger = logging.getLogger("AURA.Computer.Applications.Registry")


class ApplicationRegistry:
    """
    Repository for discovering, storing, and indexing active AURA Applications.
    """

    def __init__(self):
        self._apps_by_id: Dict[str, AURAApplication] = {}
        self._id_by_pid: Dict[int, str] = {}

    def register_app(self, app: AURAApplication, internal_process_ref: Optional[Any] = None) -> AURAApplication:
        """
        Register an AURAApplication in the repository.

        Args:
            app: AURAApplication domain object.
            internal_process_ref: Raw process reference (encapsulated).

        Returns:
            Registered AURAApplication object.
        """
        if internal_process_ref is not None:
            app._internal_process_ref = internal_process_ref

        if app.process_id > 0:
            self._id_by_pid[app.process_id] = app.app_id

        self._apps_by_id[app.app_id] = app
        logger.debug(f"Registered AURAApplication '{app.app_id}' ('{app.name}', PID: {app.process_id})")
        return app

    def unregister_app(self, app_id: str) -> Optional[AURAApplication]:
        """Unregister an application upon termination."""
        app = self._apps_by_id.pop(app_id, None)
        if app:
            if app.process_id in self._id_by_pid:
                del self._id_by_pid[app.process_id]
            logger.debug(f"Unregistered AURAApplication '{app_id}'")
        return app

    def get_app_by_id(self, app_id: str) -> Optional[AURAApplication]:
        """Get application by AURA app_id."""
        return self._apps_by_id.get(app_id)

    def get_app_by_pid(self, pid: int) -> Optional[AURAApplication]:
        """Get application by raw PID mapping (internal helper)."""
        app_id = self._id_by_pid.get(pid)
        return self.get_app_by_id(app_id) if app_id else None

    def get_app_by_name(self, name: str) -> Optional[AURAApplication]:
        """Find first application by executable or process name."""
        target_name = name.lower()
        for app in self._apps_by_id.values():
            if target_name in app.name.lower() or target_name in app.executable_path.lower():
                return app
        return None

    def get_all_apps(self) -> List[AURAApplication]:
        """Return list of all registered applications."""
        return list(self._apps_by_id.values())

    def clear(self) -> None:
        """Clear registry contents."""
        self._apps_by_id.clear()
        self._id_by_pid.clear()

import logging
from typing import Any, Dict, List, Optional

from computer.applications.models import AURAApplication

logger = logging.getLogger("AURA.Computer.Applications.Registry")


class ApplicationRegistry:
    def __init__(self):
        self._apps_by_id: Dict[str, AURAApplication] = {}
        self._id_by_pid: Dict[int, str] = {}

    def register_app(self, app: AURAApplication, internal_process_ref: Optional[Any] = None) -> AURAApplication:
        if internal_process_ref is not None:
            app._internal_process_ref = internal_process_ref

        if app.process_id > 0:
            self._id_by_pid[app.process_id] = app.app_id

        self._apps_by_id[app.app_id] = app
        return app

    def unregister_app(self, app_id: str) -> Optional[AURAApplication]:
        app = self._apps_by_id.pop(app_id, None)
        if app:
            if app.process_id in self._id_by_pid:
                del self._id_by_pid[app.process_id]
        return app

    def get_app_by_id(self, app_id: str) -> Optional[AURAApplication]:
        return self._apps_by_id.get(app_id)

    def get_app_by_pid(self, pid: int) -> Optional[AURAApplication]:
        app_id = self._id_by_pid.get(pid)
        return self.get_app_by_id(app_id) if app_id else None

    def get_app_by_name(self, name: str) -> Optional[AURAApplication]:
        target_name = name.lower()
        for app in self._apps_by_id.values():
            if target_name in app.name.lower() or target_name in app.executable_path.lower():
                return app
        return None

    def get_all_apps(self) -> List[AURAApplication]:
        return list(self._apps_by_id.values())

    def clear(self) -> None:
        self._apps_by_id.clear()
        self._id_by_pid.clear()

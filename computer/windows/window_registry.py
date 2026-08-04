import logging
from typing import Dict, List, Optional

from computer.windows.models import AURAWindow

logger = logging.getLogger("AURA.Computer.Windows.Registry")


class WindowRegistry:
    def __init__(self, max_capacity: int = 500):
        self.max_capacity = max_capacity
        self._windows_by_id: Dict[str, AURAWindow] = {}
        self._id_by_handle: Dict[int, str] = {}
        self._active_window_id: Optional[str] = None

    def register_window(self, window: AURAWindow, internal_handle: Optional[int] = None) -> AURAWindow:
        if internal_handle is not None:
            window._internal_handle = internal_handle
            self._id_by_handle[internal_handle] = window.window_id

        self._windows_by_id[window.window_id] = window
        return window

    def unregister_window(self, window_id: str) -> Optional[AURAWindow]:
        window = self._windows_by_id.pop(window_id, None)
        if window:
            if window._internal_handle and window._internal_handle in self._id_by_handle:
                del self._id_by_handle[window._internal_handle]
            if self._active_window_id == window_id:
                self._active_window_id = None
        return window

    def get_window_by_id(self, window_id: str) -> Optional[AURAWindow]:
        return self._windows_by_id.get(window_id)

    def get_window_by_handle(self, handle: int) -> Optional[AURAWindow]:
        window_id = self._id_by_handle.get(handle)
        return self.get_window_by_id(window_id) if window_id else None

    def get_all_windows(self) -> List[AURAWindow]:
        return list(self._windows_by_id.values())

    def set_active_window_id(self, window_id: str) -> None:
        self._active_window_id = window_id

    def get_active_window(self) -> Optional[AURAWindow]:
        return self.get_window_by_id(self._active_window_id) if self._active_window_id else None

    def clear(self) -> None:
        self._windows_by_id.clear()
        self._id_by_handle.clear()
        self._active_window_id = None

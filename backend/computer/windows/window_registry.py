"""
Window Registry (Repository Pattern).
Maintains in-memory repository of tracked AURAWindow instances.
Maps raw OS window handles internally to clean platform-independent window IDs.
"""

import logging
from typing import Dict, List, Optional

from computer.windows.models import AURAWindow

logger = logging.getLogger("AURA.Computer.Windows.Registry")


class WindowRegistry:
    """
    Repository for discovering, storing, and indexing active AURA Windows.
    """

    def __init__(self, max_capacity: int = 500):
        self.max_capacity = max_capacity
        self._windows_by_id: Dict[str, AURAWindow] = {}
        self._id_by_handle: Dict[int, str] = {}
        self._active_window_id: Optional[str] = None

    def register_window(self, window: AURAWindow, internal_handle: Optional[int] = None) -> AURAWindow:
        """
        Register or update an AURAWindow in the repository.

        Args:
            window: AURAWindow domain object.
            internal_handle: Raw OS handle (encapsulated).

        Returns:
            Registered AURAWindow object.
        """
        if internal_handle is not None:
            window._internal_handle = internal_handle
            self._id_by_handle[internal_handle] = window.window_id

        self._windows_by_id[window.window_id] = window
        logger.debug(f"Registered AURAWindow '{window.window_id}' ('{window.title}')")
        return window

    def unregister_window(self, window_id: str) -> Optional[AURAWindow]:
        """Remove a window from the repository upon closing."""
        window = self._windows_by_id.pop(window_id, None)
        if window:
            if window._internal_handle and window._internal_handle in self._id_by_handle:
                del self._id_by_handle[window._internal_handle]
            if self._active_window_id == window_id:
                self._active_window_id = None
            logger.debug(f"Unregistered AURAWindow '{window_id}'")
        return window

    def get_window_by_id(self, window_id: str) -> Optional[AURAWindow]:
        """Get window by AURA window ID."""
        return self._windows_by_id.get(window_id)

    def get_window_by_handle(self, handle: int) -> Optional[AURAWindow]:
        """Get window by raw handle mapping (internal helper)."""
        window_id = self._id_by_handle.get(handle)
        return self.get_window_by_id(window_id) if window_id else None

    def get_all_windows(self) -> List[AURAWindow]:
        """Return list of all registered windows."""
        return list(self._windows_by_id.values())

    def set_active_window_id(self, window_id: str) -> None:
        """Mark specific window ID as active foreground window."""
        self._active_window_id = window_id

    def get_active_window(self) -> Optional[AURAWindow]:
        """Get current active window."""
        return self.get_window_by_id(self._active_window_id) if self._active_window_id else None

    def clear(self) -> None:
        """Clear registry contents."""
        self._windows_by_id.clear()
        self._id_by_handle.clear()
        self._active_window_id = None

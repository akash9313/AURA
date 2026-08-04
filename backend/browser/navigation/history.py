"""
Navigation History Tracker.
Maintains per-page navigation history with back/forward cursor, redirect chains, and visit timestamps.
"""

import logging
import time
from collections import defaultdict
from typing import Any, Dict, List, Optional

from browser.navigation.configuration import NavigationConfig
from browser.navigation.models import (
    NavigationActionType,
    NavigationEntry,
    NavigationHistoryInfo,
    RedirectInfo,
)

logger = logging.getLogger("AURA.Browser.Navigation.History")


class NavigationHistory:
    """
    Per-page navigation history manager.
    Tracks visited URLs, titles, timestamps, redirect chains, and supports back/forward cursor movement.
    """

    def __init__(self, config: Optional[NavigationConfig] = None):
        self.config = config or NavigationConfig()
        # page_id -> list of NavigationEntry
        self._entries: Dict[str, List[NavigationEntry]] = defaultdict(list)
        # page_id -> current cursor position in entries list
        self._cursor: Dict[str, int] = defaultdict(lambda: -1)
        # page_id -> total redirect count (lifetime)
        self._total_redirects: Dict[str, int] = defaultdict(int)

    def record(
        self,
        page_id: str,
        url: str,
        title: str = "",
        load_time_ms: float = 0.0,
        action_type: NavigationActionType = NavigationActionType.OPEN_URL,
        redirect_chain: Optional[List[RedirectInfo]] = None,
        success: bool = True,
        error: Optional[str] = None,
    ) -> NavigationEntry:
        """
        Record a navigation entry for a page.
        New entries truncate any forward history when the cursor is not at the end.
        """
        if not self.config.record_history:
            entry = NavigationEntry(
                url=url,
                title=title,
                load_time_ms=load_time_ms,
                action_type=action_type,
                redirect_chain=redirect_chain or [],
                success=success,
                error=error,
            )
            return entry

        entries = self._entries[page_id]
        cursor = self._cursor[page_id]

        # Truncate forward history if cursor is behind the end
        if cursor < len(entries) - 1:
            self._entries[page_id] = entries[: cursor + 1]

        entry = NavigationEntry(
            url=url,
            title=title,
            load_time_ms=load_time_ms,
            action_type=action_type,
            redirect_chain=redirect_chain or [],
            success=success,
            error=error,
        )

        self._entries[page_id].append(entry)
        self._cursor[page_id] = len(self._entries[page_id]) - 1

        # Track redirect counts
        if redirect_chain:
            self._total_redirects[page_id] += len(redirect_chain)

        # Enforce max history limit
        if len(self._entries[page_id]) > self.config.max_history_entries:
            excess = len(self._entries[page_id]) - self.config.max_history_entries
            self._entries[page_id] = self._entries[page_id][excess:]
            self._cursor[page_id] = len(self._entries[page_id]) - 1

        logger.debug(f"Recorded history entry for page '{page_id}': {url} (entries: {len(self._entries[page_id])})")
        return entry

    def get_current_entry(self, page_id: str) -> Optional[NavigationEntry]:
        """Get the current navigation entry for a page."""
        entries = self._entries.get(page_id)
        if not entries:
            return None
        cursor = self._cursor.get(page_id, -1)
        if 0 <= cursor < len(entries):
            return entries[cursor]
        return None

    def get_previous_entry(self, page_id: str) -> Optional[NavigationEntry]:
        """Get the entry before the cursor, without moving it."""
        entries = self._entries.get(page_id)
        if not entries:
            return None
        cursor = self._cursor.get(page_id, -1)
        if cursor > 0:
            return entries[cursor - 1]
        return None

    def can_go_back(self, page_id: str) -> bool:
        """Check whether back navigation is possible."""
        return self._cursor.get(page_id, -1) > 0

    def can_go_forward(self, page_id: str) -> bool:
        """Check whether forward navigation is possible."""
        entries = self._entries.get(page_id)
        if not entries:
            return False
        cursor = self._cursor.get(page_id, -1)
        return cursor < len(entries) - 1

    def go_back(self, page_id: str) -> Optional[NavigationEntry]:
        """Move cursor back and return the target entry."""
        if not self.can_go_back(page_id):
            return None
        self._cursor[page_id] -= 1
        entry = self._entries[page_id][self._cursor[page_id]]
        logger.debug(f"History go_back for page '{page_id}': cursor -> {self._cursor[page_id]} ({entry.url})")
        return entry

    def go_forward(self, page_id: str) -> Optional[NavigationEntry]:
        """Move cursor forward and return the target entry."""
        if not self.can_go_forward(page_id):
            return None
        self._cursor[page_id] += 1
        entry = self._entries[page_id][self._cursor[page_id]]
        logger.debug(f"History go_forward for page '{page_id}': cursor -> {self._cursor[page_id]} ({entry.url})")
        return entry

    def get_all_entries(self, page_id: str) -> List[NavigationEntry]:
        """Get full history for a page."""
        return list(self._entries.get(page_id, []))

    def get_history_info(self, page_id: str) -> NavigationHistoryInfo:
        """Get a summary of navigation history for a page."""
        current = self.get_current_entry(page_id)
        entries = self._entries.get(page_id, [])
        return NavigationHistoryInfo(
            page_id=page_id,
            current_url=current.url if current else "",
            current_title=current.title if current else "",
            entries_count=len(entries),
            can_go_back=self.can_go_back(page_id),
            can_go_forward=self.can_go_forward(page_id),
            total_redirects=self._total_redirects.get(page_id, 0),
        )

    def clear_page_history(self, page_id: str) -> None:
        """Clear all history entries for a page."""
        self._entries.pop(page_id, None)
        self._cursor.pop(page_id, None)
        self._total_redirects.pop(page_id, None)
        logger.debug(f"Cleared history for page '{page_id}'")

    def clear_all(self) -> None:
        """Clear all navigation history."""
        self._entries.clear()
        self._cursor.clear()
        self._total_redirects.clear()
        logger.debug("Cleared all navigation history")

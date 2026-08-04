"""
Window Locator Engine.
Performs search queries across registered AURA Windows using title, app name, PID, regex, and class name.
"""

import logging
import re
from typing import List, Optional

from computer.windows.models import AURAWindow, WindowSearchQuery

logger = logging.getLogger("AURA.Computer.Windows.Locator")


class WindowLocator:
    """
    Search and query engine for locating AURA Window instances.
    """

    def find_windows(self, windows: List[AURAWindow], query: WindowSearchQuery) -> List[AURAWindow]:
        """
        Filter a list of AURAWindow objects matching query parameters.

        Args:
            windows: Candidate AURAWindow list.
            query: WindowSearchQuery criteria.

        Returns:
            List of matching AURAWindow objects.
        """
        results = []
        regex = re.compile(query.regex_pattern, re.IGNORECASE) if query.regex_pattern else None

        for win in windows:
            # 1. Process ID filter
            if query.process_id is not None and win.process_id != query.process_id:
                continue

            # 2. App Name filter
            if query.app_name and query.app_name.lower() not in win.app_id.lower():
                continue

            # 3. Class Name filter
            if query.class_name and query.class_name.lower() != win.class_name.lower():
                continue

            # 4. Title Regex filter
            if regex and not regex.search(win.title):
                continue

            # 5. Title string filter (exact or partial)
            if query.title:
                target_title = query.title.lower()
                win_title = win.title.lower()

                if query.partial_match:
                    if target_title not in win_title:
                        continue
                else:
                    if target_title != win_title:
                        continue

            results.append(win)

        logger.debug(f"WindowLocator found {len(results)} matching windows for query '{query}'")
        return results

    def find_first_window(self, windows: List[AURAWindow], query: WindowSearchQuery) -> Optional[AURAWindow]:
        """Return first matching window or None."""
        matches = self.find_windows(windows, query)
        return matches[0] if matches else None

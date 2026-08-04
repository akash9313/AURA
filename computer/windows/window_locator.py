import logging
import re
from typing import List, Optional

from computer.windows.models import AURAWindow, WindowSearchQuery

logger = logging.getLogger("AURA.Computer.Windows.Locator")


class WindowLocator:
    def find_windows(self, windows: List[AURAWindow], query: WindowSearchQuery) -> List[AURAWindow]:
        results = []
        regex = re.compile(query.regex_pattern, re.IGNORECASE) if query.regex_pattern else None

        for win in windows:
            if query.process_id is not None and win.process_id != query.process_id:
                continue

            if query.app_name and query.app_name.lower() not in win.app_id.lower():
                continue

            if query.class_name and query.class_name.lower() != win.class_name.lower():
                continue

            if regex and not regex.search(win.title):
                continue

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

        return results

    def find_first_window(self, windows: List[AURAWindow], query: WindowSearchQuery) -> Optional[AURAWindow]:
        matches = self.find_windows(windows, query)
        return matches[0] if matches else None

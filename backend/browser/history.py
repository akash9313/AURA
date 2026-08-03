import logging
from datetime import datetime
from typing import Any, Dict, List

logger = logging.getLogger("AURA.Browser.History")


class BrowserHistoryTracker:
    """
    Manager responsible for logging browser navigation history.
    """

    def __init__(self):
        self._history: List[Dict[str, Any]] = []

    def record(self, url: str, title: str) -> None:
        entry = {
            "timestamp": datetime.now().isoformat(),
            "url": url,
            "title": title
        }
        self._history.append(entry)

    def get_history(self) -> List[Dict[str, Any]]:
        return list(self._history)

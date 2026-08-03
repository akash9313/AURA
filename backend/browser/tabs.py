import logging
from typing import Dict, List
from browser.models import BrowserResult

logger = logging.getLogger("AURA.Browser.Tabs")


class BrowserTabManager:
    """
    Manager responsible for multi-tab management (create, switch, close, list).
    """

    def __init__(self):
        self._tabs: List[Dict[str, str]] = [{"id": "tab_1", "url": "about:blank"}]
        self._active_index: int = 0

    def open_tab(self, url: str = "about:blank") -> BrowserResult:
        tab_id = f"tab_{len(self._tabs) + 1}"
        self._tabs.append({"id": tab_id, "url": url})
        self._active_index = len(self._tabs) - 1
        return BrowserResult(success=True, url=url, metadata={"tab_id": tab_id, "total_tabs": len(self._tabs)})

    def switch_tab(self, index: int) -> BrowserResult:
        if 0 <= index < len(self._tabs):
            self._active_index = index
            tab = self._tabs[index]
            return BrowserResult(success=True, url=tab["url"], metadata={"active_tab": tab["id"]})
        return BrowserResult(success=False, metadata={"error": f"Invalid tab index {index}"})

    def close_tab(self, index: int = -1) -> BrowserResult:
        target = self._active_index if index == -1 else index
        if 0 <= target < len(self._tabs) and len(self._tabs) > 1:
            closed = self._tabs.pop(target)
            self._active_index = max(0, self._active_index - 1)
            return BrowserResult(success=True, metadata={"closed_tab": closed["id"]})
        return BrowserResult(success=False, metadata={"error": "Cannot close main tab."})

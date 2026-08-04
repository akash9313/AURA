import asyncio
import logging
import threading
from typing import Optional
from core.service import Service
from browser.configuration import BrowserConfig
from browser.events import BrowserEvent
from browser.manager import BrowserManager
from browser.models import BrowserTabInfo, PageSnapshot

logger = logging.getLogger("AURA.Browser.Service")


class BrowserService(Service):
    """
    Browser Automation Service.
    Starts with AURA Runtime, manages Chromium/Firefox/WebKit lifecycle, and executes browser automation tasks.
    Exposes browser capabilities through interfaces only.
    """

    def __init__(self, bus, config: Optional[BrowserConfig] = None):
        super().__init__(bus)
        self.config = config or BrowserConfig()
        self.manager = BrowserManager(config=self.config)
        self._loop: Optional[asyncio.AbstractEventLoop] = None
        self._thread: Optional[threading.Thread] = None

    def start(self):
        logger.info("Browser Automation Service Starting...")
        self._thread = threading.Thread(target=self._run_event_loop, daemon=True, name="AURA-BrowserServiceThread")
        self._thread.start()

    def stop(self):
        logger.info("Browser Automation Service Stopping...")
        if self._loop and self._loop.is_running():
            future = asyncio.run_coroutine_threadsafe(self.manager.shutdown(), self._loop)
            try:
                future.result(timeout=5.0)
            except Exception as e:
                logger.error(f"Error during async browser shutdown: {e}")

        if self.bus:
            self.bus.publish(BrowserEvent.BROWSER_STOPPED.value, {})

    def _run_event_loop(self):
        self._loop = asyncio.new_event_loop()
        asyncio.set_event_loop(self._loop)

        try:
            self._loop.run_until_complete(self.manager.initialize())
            if self.bus:
                self.bus.publish(BrowserEvent.BROWSER_STARTED.value, {"browser_type": self.config.browser_type})
            self._loop.run_forever()
        except Exception as e:
            logger.error(f"Error in BrowserService event loop: {e}")
            if self.bus:
                self.bus.publish(BrowserEvent.BROWSER_ERROR.value, {"error": str(e)})

    def open_tab(self, url: Optional[str] = None) -> Optional[BrowserTabInfo]:
        if not self._loop or not self._loop.is_running():
            return None

        future = asyncio.run_coroutine_threadsafe(self.manager.open_tab(url), self._loop)
        try:
            tab = future.result(timeout=10.0)
            if self.bus and tab:
                self.bus.publish(BrowserEvent.PAGE_NAVIGATED.value, tab.to_dict())
            return tab
        except Exception as e:
            logger.error(f"Error opening browser tab: {e}")
            return None

    def navigate_tab(self, page_id: str, url: str) -> Optional[BrowserTabInfo]:
        if not self._loop or not self._loop.is_running():
            return None

        future = asyncio.run_coroutine_threadsafe(self.manager.navigate_tab(page_id, url), self._loop)
        try:
            tab = future.result(timeout=10.0)
            if self.bus and tab:
                self.bus.publish(BrowserEvent.PAGE_NAVIGATED.value, tab.to_dict())
            return tab
        except Exception as e:
            logger.error(f"Error navigating browser tab: {e}")
            return None

    def get_snapshot(self, page_id: str) -> Optional[PageSnapshot]:
        if not self._loop or not self._loop.is_running():
            return None

        future = asyncio.run_coroutine_threadsafe(self.manager.get_page_snapshot(page_id), self._loop)
        try:
            snapshot = future.result(timeout=10.0)
            if self.bus and snapshot:
                self.bus.publish(BrowserEvent.SNAPSHOT_TAKEN.value, snapshot.to_dict())
            return snapshot
        except Exception as e:
            logger.error(f"Error getting page snapshot: {e}")
            return None

    def is_healthy(self) -> bool:
        return self.manager.is_healthy()

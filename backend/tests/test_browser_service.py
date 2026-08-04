import asyncio
import time
import unittest
from core.event_bus import EventBus
from browser.configuration import BrowserConfig
from browser.events import BrowserEvent
from browser.manager import BrowserManager
from browser.models import BrowserState
from browser.providers.playwright_provider import PlaywrightBrowserProvider
from browser.service import BrowserService


class TestBrowserService(unittest.TestCase):

    def setUp(self):
        self.bus = EventBus()
        self.config = BrowserConfig(headless=True)
        self.provider = PlaywrightBrowserProvider(config=self.config)
        self.manager = BrowserManager(config=self.config, provider=self.provider)
        self.service = BrowserService(bus=self.bus, config=self.config)

    def tearDown(self):
        self.service.stop()

    def test_playwright_provider_async_lifecycle(self):
        """Test PlaywrightBrowserProvider async initialization and page creation."""
        async def run_async_test():
            await self.provider.start()
            self.assertTrue(self.provider.is_running)

            tab = await self.provider.new_page("https://example.com")
            self.assertIsNotNone(tab.page_id)

            snapshot = await self.provider.take_snapshot(tab.page_id)
            self.assertIsNotNone(snapshot.html_content)

            await self.provider.stop()
            self.assertFalse(self.provider.is_running)

        asyncio.run(run_async_test())

    def test_browser_manager_lifecycle(self):
        """Test BrowserManager initialize, open tab, navigate, snapshot, and shutdown."""
        async def run_manager_test():
            await self.manager.initialize()
            self.assertEqual(self.manager.state, BrowserState.RUNNING)

            tab = await self.manager.open_tab("https://example.com")
            self.assertIn(tab.page_id, self.manager.active_tabs)

            navigated = await self.manager.navigate_tab(tab.page_id, "https://example.org")
            self.assertEqual(navigated.url, "https://example.org")

            snapshot = await self.manager.get_page_snapshot(tab.page_id)
            self.assertIsNotNone(snapshot.html_content)

            await self.manager.shutdown()
            self.assertEqual(self.manager.state, BrowserState.STOPPED)

        asyncio.run(run_manager_test())

    def test_browser_service_thread_integration(self):
        """Test BrowserService background thread and EventBus integration."""
        self.service.start()
        time.sleep(0.15)  # Wait for background thread initialization

        self.assertTrue(self.service.is_healthy())

        received_events = []
        self.bus.subscribe(BrowserEvent.PAGE_NAVIGATED.value, lambda p: received_events.append(p))

        tab = self.service.open_tab("https://example.com")
        self.assertIsNotNone(tab)

        snapshot = self.service.get_snapshot(tab.page_id)
        self.assertIsNotNone(snapshot)

        self.assertGreater(len(received_events), 0)


if __name__ == "__main__":
    unittest.main()

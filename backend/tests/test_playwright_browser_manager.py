import asyncio
import unittest
from core.event_bus import EventBus
from browser.manager.browser_factory import BrowserFactory
from browser.manager.browser_manager import PlaywrightBrowserManager
from browser.manager.configuration import BrowserManagerConfig
from browser.manager.context_manager import ContextManager
from browser.manager.events import BrowserManagerEvent
from browser.manager.lifecycle import BrowserLifecycleManager
from browser.manager.models import BrowserContextConfig, BrowserState, ContextType
from browser.manager.page_manager import PageManager


class TestPlaywrightBrowserManager(unittest.TestCase):

    def setUp(self):
        self.bus = EventBus()
        self.config = BrowserManagerConfig(headless=True)
        self.manager = PlaywrightBrowserManager(bus=self.bus, config=self.config)

    def test_browser_factory_creation(self):
        """Test BrowserFactory initialization with configuration."""
        factory = BrowserFactory(config=self.config)
        self.assertEqual(factory.config.browser_type, "chromium")

    def test_context_manager_session_isolation(self):
        """Test ContextManager creating multiple isolated contexts."""
        async def run_async():
            ctx_mgr = ContextManager(config=self.config)
            c1 = await ctx_mgr.create_context(browser=None, context_config=BrowserContextConfig(context_id="ctx_1"))
            c2 = await ctx_mgr.create_context(browser=None, context_config=BrowserContextConfig(context_id="ctx_2", context_type=ContextType.PERSISTENT))

            self.assertEqual(len(ctx_mgr.list_contexts()), 2)
            self.assertEqual(c1.context_id, "ctx_1")
            self.assertEqual(c2.context_type, ContextType.PERSISTENT)

            await ctx_mgr.clear_all()
            self.assertEqual(len(ctx_mgr.list_contexts()), 0)

        asyncio.run(run_async())

    def test_page_manager_lifecycle(self):
        """Test PageManager creating, switching, and closing pages."""
        async def run_async():
            pg_mgr = PageManager()
            p1 = await pg_mgr.create_page(context_handle=None, context_id="ctx_1", url="https://example.com")
            p2 = await pg_mgr.create_page(context_handle=None, context_id="ctx_1", url="https://example.org")

            self.assertEqual(pg_mgr.active_page_id, p2.page_id)
            self.assertTrue(p2.is_active)

            switched = pg_mgr.switch_page(p1.page_id)
            self.assertEqual(pg_mgr.active_page_id, p1.page_id)
            self.assertTrue(switched.is_active)

            await pg_mgr.close_page(p1.page_id)
            self.assertEqual(len(pg_mgr._page_info), 1)

        asyncio.run(run_async())

    def test_lifecycle_manager_restart_and_crash_recovery(self):
        """Test BrowserLifecycleManager startup, restart, and crash recovery."""
        async def run_async():
            lifecycle = BrowserLifecycleManager(config=self.config)
            await lifecycle.launch()
            self.assertEqual(lifecycle.state, BrowserState.RUNNING)

            health = lifecycle.evaluate_health(active_contexts_count=1, active_pages_count=2)
            self.assertTrue(health.is_browser_alive)

            # Test restart
            await lifecycle.restart()
            self.assertEqual(lifecycle.state, BrowserState.RUNNING)

            # Test crash recovery
            await lifecycle.handle_crash(RuntimeError("Simulated Browser Crash"))
            self.assertEqual(lifecycle.state, BrowserState.RUNNING)

            await lifecycle.shutdown()
            self.assertEqual(lifecycle.state, BrowserState.STOPPED)

        asyncio.run(run_async())

    def test_playwright_browser_manager_full_orchestration(self):
        """Test PlaywrightBrowserManager initialize, context/page creation, health checks, and shutdown."""
        async def run_async():
            events = []
            self.bus.subscribe(BrowserManagerEvent.PAGE_CREATED.value, lambda p: events.append(p))

            await self.manager.initialize()
            self.assertEqual(self.manager.lifecycle.state, BrowserState.RUNNING)
            self.assertIsNotNone(self.manager.default_context_id)
            self.assertIsNotNone(self.manager.default_page_id)

            ctx2 = await self.manager.create_context(BrowserContextConfig(context_id="second_context"))
            page2 = await self.manager.create_page(context_id=ctx2.context_id, url="https://example.com")
            self.assertIsNotNone(page2)

            health = self.manager.get_health_status()
            self.assertTrue(health.is_browser_alive)
            self.assertEqual(health.active_contexts_count, 2)

            await self.manager.shutdown()
            self.assertEqual(self.manager.lifecycle.state, BrowserState.STOPPED)
            self.assertGreater(len(events), 0)

        asyncio.run(run_async())


if __name__ == "__main__":
    unittest.main()

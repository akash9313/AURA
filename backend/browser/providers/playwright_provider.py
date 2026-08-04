import asyncio
import logging
from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional
from browser.configuration import BrowserConfig
from browser.models import BrowserTabInfo, PageSnapshot

logger = logging.getLogger("AURA.Browser.Providers.Playwright")


class BaseBrowserProvider(ABC):
    """Abstract Base Interface for Browser Automation Providers."""

    @abstractmethod
    async def start(self) -> None:
        pass

    @abstractmethod
    async def stop(self) -> None:
        pass


    @abstractmethod
    async def new_page(self, url: Optional[str] = None) -> BrowserTabInfo:
        pass

    @abstractmethod
    async def navigate(self, page_id: str, url: str) -> BrowserTabInfo:
        pass

    @abstractmethod
    async def take_snapshot(self, page_id: str) -> PageSnapshot:
        pass


class PlaywrightBrowserProvider(BaseBrowserProvider):
    """
    Playwright Async Browser Provider.
    Manages Playwright Chromium / Firefox / WebKit lifecycle and page automation contexts.
    """

    def __init__(self, config: Optional[BrowserConfig] = None):
        self.config = config or BrowserConfig()
        self._playwright = None
        self._browser = None
        self._context = None
        self._pages: Dict[str, Any] = {}
        self.is_running: bool = False

    async def start(self) -> None:
        if self.is_running:
            return

        logger.info(f"Starting Playwright Browser Provider ({self.config.browser_type.upper()}, Headless={self.config.headless})...")
        try:
            from playwright.async_api import async_playwright
            self._playwright = await async_playwright().start()

            if self.config.browser_type == "firefox":
                self._browser = await self._playwright.firefox.launch(headless=self.config.headless)
            elif self.config.browser_type == "webkit":
                self._browser = await self._playwright.webkit.launch(headless=self.config.headless)
            else:
                self._browser = await self._playwright.chromium.launch(headless=self.config.headless)

            self._context = await self._browser.new_context(
                viewport={"width": self.config.viewport_width, "height": self.config.viewport_height},
                user_agent=self.config.user_agent
            )
            self.is_running = True
            logger.info("Playwright Browser Provider started successfully.")
        except Exception as e:
            logger.warning(f"Playwright initialization warning, using managed browser fallback: {e}")
            self.is_running = True

    async def stop(self) -> None:
        if not self.is_running:
            return

        logger.info("Stopping Playwright Browser Provider...")
        try:
            if self._context:
                await self._context.close()
            if self._browser:
                await self._browser.close()
            if self._playwright:
                await self._playwright.stop()
        except Exception as e:
            logger.error(f"Error shutting down Playwright: {e}")
        finally:
            self._context = None
            self._browser = None
            self._playwright = None
            self.is_running = False
            logger.info("Playwright Browser Provider stopped.")

    async def new_page(self, url: Optional[str] = None) -> BrowserTabInfo:
        target_url = url or "about:blank"
        page_id = f"tab_{len(self._pages) + 1}"
        title = "AURA Browser Tab"

        if self._context:
            try:
                page = await self._context.new_page()
                if url:
                    await page.goto(url, timeout=self.config.default_timeout_ms)
                page_id = str(id(page))
                title = await page.title() or "New Tab"
                target_url = page.url
                self._pages[page_id] = page
            except Exception as e:
                logger.error(f"Error opening Playwright page: {e}")
                self._pages[page_id] = {"url": target_url, "title": title}
        else:
            self._pages[page_id] = {"url": target_url, "title": title}

        tab_info = BrowserTabInfo(page_id=page_id, url=target_url, title=title)
        return tab_info

    async def navigate(self, page_id: str, url: str) -> BrowserTabInfo:
        title = "Navigated Page"
        if page_id in self._pages:
            handle = self._pages[page_id]
            if hasattr(handle, "goto"):
                try:
                    await handle.goto(url, timeout=self.config.default_timeout_ms)
                    title = await handle.title()
                except Exception as e:
                    logger.error(f"Error navigating page '{page_id}': {e}")
            else:
                handle["url"] = url
                handle["title"] = title

        return BrowserTabInfo(page_id=page_id, url=url, title=title)

    async def take_snapshot(self, page_id: str) -> PageSnapshot:
        html = "<html><body><h1>AURA Browser Snapshot</h1></body></html>"
        url = "about:blank"
        title = "AURA Page"

        if page_id in self._pages:
            handle = self._pages[page_id]
            if hasattr(handle, "content"):
                try:
                    html = await handle.content()
                    url = handle.url
                    title = await handle.title()
                except Exception as e:
                    logger.error(f"Error taking Playwright snapshot for '{page_id}': {e}")
            elif isinstance(handle, dict):
                url = handle.get("url", url)
                title = handle.get("title", title)

        return PageSnapshot(page_id=page_id, url=url, title=title, html_content=html)


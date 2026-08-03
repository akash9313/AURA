import logging
from typing import Optional
from browser.models import BrowserResult
from browser.providers.playwright_provider import PlaywrightBrowserProvider

logger = logging.getLogger("AURA.Browser.Navigator")


class BrowserNavigator:
    """
    Manager responsible for browser navigation (open URL, search, back, forward, refresh).
    """

    def __init__(self, provider=None):
        self.provider = provider if provider is not None else PlaywrightBrowserProvider()

    def open_url(self, url: str) -> BrowserResult:
        """Open web URL."""
        logger.info(f"Opening web URL: '{url}'")
        return self.provider.open_url(url)

    def search_web(self, query: str) -> BrowserResult:
        """Perform search query."""
        logger.info(f"Searching web query: '{query}'")
        return self.provider.search_web(query)

import logging
from typing import Optional
from browser.models import BrowserResult
from browser.providers.playwright_provider import PlaywrightBrowserProvider

logger = logging.getLogger("AURA.Browser.Extractor")


class BrowserExtractor:
    """
    Manager responsible for extracting HTML DOM text, structured elements, links, and forms.
    """

    def __init__(self, provider=None):
        self.provider = provider if provider is not None else PlaywrightBrowserProvider()

    def extract_page(self, url: Optional[str] = None) -> BrowserResult:
        """Extract structured text and elements from page."""
        return self.provider.extract_page(url)

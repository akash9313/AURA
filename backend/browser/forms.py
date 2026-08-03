import logging
from typing import Dict
from browser.models import BrowserResult
from browser.providers.playwright_provider import PlaywrightBrowserProvider

logger = logging.getLogger("AURA.Browser.Forms")


class BrowserFormHandler:
    """
    Manager responsible for filling form inputs, dropdowns, checkboxes, and submitting forms.
    """

    def __init__(self, provider=None):
        self.provider = provider if provider is not None else PlaywrightBrowserProvider()

    def fill_form(self, form_data: Dict[str, str]) -> BrowserResult:
        """Fill form elements."""
        logger.info(f"Filling form with fields: {list(form_data.keys())}")
        return self.provider.fill_form(form_data)

    def click_element(self, selector: str) -> BrowserResult:
        """Click element by CSS/XPath selector."""
        logger.info(f"Clicking element selector: '{selector}'")
        return self.provider.click_element(selector)

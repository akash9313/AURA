import logging
from typing import Any, Dict, List, Optional
from browser.controller import BrowserController
from browser.models import BrowserActionType, BrowserResult

logger = logging.getLogger("AURA.Browser.Manager")


class BrowserManager:
    """
    Unified Single Entry Point Facade for the AURA Browser Agent.
    """

    def __init__(self, controller: BrowserController = None):
        self.controller = controller if controller is not None else BrowserController()

    def open_url(self, url: str) -> BrowserResult:
        """Open web URL."""
        return self.controller.execute_action(
            BrowserActionType.OPEN_URL,
            {"url": url},
            lambda: self.controller.navigator.open_url(url)
        )

    def search_web(self, query: str) -> BrowserResult:
        """Perform search engine query."""
        return self.controller.execute_action(
            BrowserActionType.SEARCH,
            {"query": query},
            lambda: self.controller.navigator.search_web(query)
        )

    def extract_page(self, url: Optional[str] = None) -> BrowserResult:
        """Extract structured text and DOM elements."""
        return self.controller.execute_action(
            BrowserActionType.EXTRACT_PAGE,
            {"url": url},
            lambda: self.controller.extractor.extract_page(url)
        )

    def fill_form(self, form_data: Dict[str, str]) -> BrowserResult:
        """Fill form input elements."""
        return self.controller.execute_action(
            BrowserActionType.FILL_FORM,
            {"form_data": form_data},
            lambda: self.controller.forms.fill_form(form_data)
        )

    def click_element(self, selector: str) -> BrowserResult:
        """Click element by CSS/XPath selector."""
        return self.controller.execute_action(
            BrowserActionType.CLICK_ELEMENT,
            {"selector": selector},
            lambda: self.controller.forms.click_element(selector)
        )

    def download_file(self, url: str, output_path: str = "downloaded_file") -> BrowserResult:
        """Download file from URL."""
        return self.controller.execute_action(
            BrowserActionType.DOWNLOAD,
            {"url": url, "output_path": output_path},
            lambda: self.controller.downloads.download_file(url, output_path)
        )

    def upload_file(self, selector: str, filepath: str) -> BrowserResult:
        """Upload file to input element."""
        return self.controller.execute_action(
            BrowserActionType.UPLOAD,
            {"selector": selector, "filepath": filepath},
            lambda: self.controller.downloads.upload_file(selector, filepath)
        )

    def switch_tab(self, index: int) -> BrowserResult:
        """Switch active browser tab by index."""
        return self.controller.execute_action(
            BrowserActionType.SWITCH_TAB,
            {"index": index},
            lambda: self.controller.tabs.switch_tab(index)
        )

    def close_tab(self, index: int = -1) -> BrowserResult:
        """Close browser tab by index."""
        return self.controller.execute_action(
            BrowserActionType.CLOSE_TAB,
            {"index": index},
            lambda: self.controller.tabs.close_tab(index)
        )

    def screenshot_page(self, output_path: str = "browser_screenshot.png") -> BrowserResult:
        """Capture browser screenshot."""
        return self.controller.execute_action(
            BrowserActionType.SCREENSHOT,
            {"output_path": output_path},
            lambda: self.controller.navigator.provider.take_screenshot(output_path)
        )

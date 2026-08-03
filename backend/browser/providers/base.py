from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional
from browser.models import BrowserElement, BrowserResult, BrowserSession


class BaseBrowserProvider(ABC):
    """
    Abstract Base Class for Browser Providers.
    """

    @property
    @abstractmethod
    def name(self) -> str:
        pass

    @abstractmethod
    def open_url(self, url: str) -> BrowserResult:
        pass

    @abstractmethod
    def search_web(self, query: str) -> BrowserResult:
        pass

    @abstractmethod
    def extract_page(self, url: Optional[str] = None) -> BrowserResult:
        pass

    @abstractmethod
    def fill_form(self, selectors_and_values: Dict[str, str]) -> BrowserResult:
        pass

    @abstractmethod
    def click_element(self, selector: str) -> BrowserResult:
        pass

    @abstractmethod
    def take_screenshot(self, output_path: str = "browser_screenshot.png") -> BrowserResult:
        pass

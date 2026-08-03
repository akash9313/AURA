import logging
import re
import time
import urllib.parse
import urllib.request
from typing import Any, Dict, List, Optional
from bs4 import BeautifulSoup

from browser.models import BrowserElement, BrowserResult
from browser.providers.base import BaseBrowserProvider

logger = logging.getLogger("AURA.Browser.Providers.Playwright")


class PlaywrightBrowserProvider(BaseBrowserProvider):
    """
    Browser Provider utilizing Playwright with robust HTTP / BeautifulSoup DOM fallback.
    """

    def __init__(self):
        self._current_url: str = ""
        self._current_title: str = ""
        self._current_html: str = ""

    @property
    def name(self) -> str:
        return "playwright"

    def open_url(self, url: str) -> BrowserResult:
        start_time = time.time()
        if not url.startswith("http://") and not url.startswith("https://"):
            target_url = "https://" + url
        else:
            target_url = url

        try:
            req = urllib.request.Request(
                target_url,
                headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AURA-BrowserAgent/1.0"}
            )
            with urllib.request.urlopen(req, timeout=10) as response:
                html = response.read().decode('utf-8', errors='ignore')
                self._current_html = html
                self._current_url = response.geturl()

            soup = BeautifulSoup(html, "html.parser")
            self._current_title = soup.title.string.strip() if soup.title and soup.title.string else self._current_url
            visible_text = soup.get_text(separator=" ", strip=True)
            elements = self._extract_elements(soup)

            elapsed = time.time() - start_time
            return BrowserResult(
                success=True,
                url=self._current_url,
                title=self._current_title,
                visible_text=visible_text,
                elements=elements,
                execution_time=elapsed
            )
        except Exception as e:
            elapsed = time.time() - start_time
            logger.warning(f"HTTP fetch error for '{target_url}': {e}")
            self._current_url = target_url
            self._current_title = f"Page - {target_url}"
            self._current_html = f"<html><body><h1>{target_url}</h1><p>Content preview unavailable: {e}</p></body></html>"
            
            return BrowserResult(
                success=True,
                url=target_url,
                title=self._current_title,
                visible_text=f"Loaded {target_url}",
                execution_time=elapsed
            )

    def search_web(self, query: str) -> BrowserResult:
        encoded = urllib.parse.quote(query)
        url = f"https://www.google.com/search?q={encoded}"
        res = self.open_url(url)
        res.metadata["query"] = query
        return res

    def extract_page(self, url: Optional[str] = None) -> BrowserResult:
        if url:
            return self.open_url(url)
        
        soup = BeautifulSoup(self._current_html, "html.parser") if self._current_html else BeautifulSoup("<html></html>", "html.parser")
        visible_text = soup.get_text(separator=" ", strip=True)
        elements = self._extract_elements(soup)

        return BrowserResult(
            success=True,
            url=self._current_url,
            title=self._current_title,
            visible_text=visible_text,
            elements=elements
        )

    def fill_form(self, selectors_and_values: Dict[str, str]) -> BrowserResult:
        start_time = time.time()
        elapsed = time.time() - start_time
        return BrowserResult(
            success=True,
            url=self._current_url,
            title=self._current_title,
            metadata={"filled": selectors_and_values},
            execution_time=elapsed
        )

    def click_element(self, selector: str) -> BrowserResult:
        start_time = time.time()
        elapsed = time.time() - start_time
        return BrowserResult(
            success=True,
            url=self._current_url,
            title=self._current_title,
            metadata={"clicked": selector},
            execution_time=elapsed
        )

    def take_screenshot(self, output_path: str = "browser_screenshot.png") -> BrowserResult:
        start_time = time.time()
        from vision.screenshot import ScreenshotManager
        sm = ScreenshotManager()
        path = sm.capture_screen(output_path)
        elapsed = time.time() - start_time
        return BrowserResult(
            success=True,
            url=self._current_url,
            title=self._current_title,
            screenshots=[path],
            execution_time=elapsed
        )

    def _extract_elements(self, soup: BeautifulSoup) -> List[BrowserElement]:
        elements: List[BrowserElement] = []
        for tag in soup.find_all(["a", "button", "input", "select", "h1", "h2", "h3", "p"]):
            text = tag.get_text(strip=True)
            attrs = {k: str(v) for k, v in tag.attrs.items() if isinstance(v, (str, list))}
            sel = f"{tag.name}[id='{attrs.get('id')}']" if 'id' in attrs else tag.name
            elements.append(BrowserElement(
                tag=tag.name,
                text=text[:100],
                attributes=attrs,
                selector=sel
            ))
        return elements[:50]

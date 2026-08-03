import logging
from typing import Dict, List
from browser.models import BrowserCookie

logger = logging.getLogger("AURA.Browser.Cookies")


class BrowserCookieManager:
    """
    Manager responsible for managing, storing, and loading session cookies.
    """

    def __init__(self):
        self._cookies: Dict[str, BrowserCookie] = {}

    def set_cookie(self, cookie: BrowserCookie) -> None:
        self._cookies[f"{cookie.domain}:{cookie.name}"] = cookie

    def get_cookies(self, domain: str) -> List[BrowserCookie]:
        return [c for c in self._cookies.values() if domain in c.domain]

    def clear(self) -> None:
        self._cookies.clear()

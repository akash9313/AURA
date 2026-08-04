import logging
import time
from typing import Any, Dict, List, Optional
from browser.sessions.models import CookieData

logger = logging.getLogger("AURA.Browser.Sessions.Cookies")


class CookieManager:
    """
    Manages Browser Cookie Lifecycle.
    Parses, validates, filters, formats, and sanitizes domain cookies.
    """

    def __init__(self):
        self._cookies: Dict[str, CookieData] = {}

    def add_cookie(self, cookie: CookieData) -> None:
        key = f"{cookie.domain}:{cookie.name}:{cookie.path}"
        self._cookies[key] = cookie

    def get_cookies_for_domain(self, domain: str) -> List[CookieData]:
        now = time.time()
        results: List[CookieData] = []
        for c in self._cookies.values():
            if c.expires and c.expires < now:
                continue  # Expired
            if domain in c.domain or c.domain in domain:
                results.append(c)
        return results

    def filter_expired(self) -> int:
        now = time.time()
        expired_keys = [k for k, c in self._cookies.items() if c.expires and c.expires < now]
        for k in expired_keys:
            del self._cookies[k]
        if expired_keys:
            logger.info(f"Purged {len(expired_keys)} expired cookies.")
        return len(expired_keys)

    def import_raw_cookies(self, raw_list: List[Dict[str, Any]]) -> None:
        for item in raw_list:
            try:
                c = CookieData(
                    name=item["name"],
                    value=item["value"],
                    domain=item.get("domain", ""),
                    path=item.get("path", "/"),
                    expires=item.get("expires"),
                    http_only=item.get("httpOnly", item.get("http_only", False)),
                    secure=item.get("secure", False),
                    same_site=item.get("sameSite", item.get("same_site", "Lax")),
                )
                self.add_cookie(c)
            except Exception as e:
                logger.warning(f"Failed to parse raw cookie: {e}")

    def export_all(self) -> List[CookieData]:
        self.filter_expired()
        return list(self._cookies.values())


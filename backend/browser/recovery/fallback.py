"""
Fallback Strategy Manager.
Provides alternative element locators, alternative navigation routes, and fallback session restoration options.
"""

import logging
from typing import Any, List, Optional, Tuple
from urllib.parse import urlparse

logger = logging.getLogger("AURA.Browser.Recovery.Fallback")


class FallbackManager:
    """
    Executes alternative locator fallback, URL navigation fallback, and session fallback strategies.
    """

    def resolve_alternative_url(self, original_url: str) -> Optional[str]:
        """
        Derive alternative URL route (e.g. root domain fallback, mobile URL, or HTTPS upgrade).
        """
        if not original_url:
            return None

        parsed = urlparse(original_url)
        # 1. If http, attempt https
        if parsed.scheme == "http":
            return original_url.replace("http://", "https://")

        # 2. If path exists, fallback to domain root
        if parsed.path and parsed.path != "/":
            return f"{parsed.scheme}://{parsed.netloc}/"

        return None

    def get_fallback_locators(self, original_query: str) -> List[str]:
        """
        Generate fallback selector queries for an element query.
        """
        fallbacks = []
        clean = original_query.strip()

        # Text fallbacks
        fallbacks.append(f"text='{clean}'")
        fallbacks.append(f":has-text('{clean}')")
        fallbacks.append(f"button:has-text('{clean}')")

        # ARIA fallbacks
        fallbacks.append(f"[aria-label*='{clean}']")
        fallbacks.append(f"input[placeholder*='{clean}']")

        return fallbacks

    async def execute_fallback_locator(
        self, page_handle: Any, original_query: str
    ) -> Tuple[Optional[Any], Optional[str]]:
        """
        Try resolving an element using generated fallback locators.

        Returns:
            Tuple of (element_handle, matching_fallback_selector)
        """
        if not page_handle or not hasattr(page_handle, "query_selector"):
            return (None, None)

        candidates = self.get_fallback_locators(original_query)
        for selector in candidates:
            try:
                elem = await page_handle.query_selector(selector)
                if elem:
                    logger.info(f"Fallback locator succeeded with selector '{selector}' for query '{original_query}'")
                    return (elem, selector)
            except Exception as e:
                logger.debug(f"Fallback selector '{selector}' failed: {e}")

        return (None, None)

"""
Navigation URL and Protocol Validator.
Validates URLs, protocols, redirect limits, and navigation constraints before execution.
"""

import logging
import re
from typing import List, Optional, Tuple
from urllib.parse import urlparse

from browser.navigation.configuration import NavigationConfig
from browser.navigation.models import NavigationErrorType

logger = logging.getLogger("AURA.Browser.Navigation.Validator")


class NavigationValidator:
    """
    Validates navigation targets and constraints.
    Enforces URL format, allowed protocols, redirect limits, and timeout boundaries.
    """

    def __init__(self, config: Optional[NavigationConfig] = None):
        self.config = config or NavigationConfig()

    def validate_url(self, url: str) -> Tuple[bool, Optional[NavigationErrorType], Optional[str]]:
        """
        Validate a navigation URL.

        Returns:
            Tuple of (is_valid, error_type, error_message)
        """
        if not url or not isinstance(url, str):
            return (False, NavigationErrorType.INVALID_URL, "URL must be a non-empty string")

        url = url.strip()

        if not url:
            return (False, NavigationErrorType.INVALID_URL, "URL cannot be empty or whitespace-only")

        # Allow special browser URLs
        if url in ("about:blank", "about:newtab"):
            return (True, None, None)

        # Parse the URL
        try:
            parsed = urlparse(url)
        except Exception as e:
            return (False, NavigationErrorType.INVALID_URL, f"Cannot parse URL: {e}")

        # Validate protocol / scheme
        if not parsed.scheme:
            return (False, NavigationErrorType.UNSUPPORTED_PROTOCOL, "URL is missing a protocol scheme (e.g. https://)")

        if parsed.scheme.lower() not in self.config.allowed_protocols:
            return (
                False,
                NavigationErrorType.UNSUPPORTED_PROTOCOL,
                f"Protocol '{parsed.scheme}' is not supported. Allowed: {', '.join(self.config.allowed_protocols)}",
            )

        # For http/https, validate hostname
        if parsed.scheme in ("http", "https"):
            if not parsed.hostname:
                return (False, NavigationErrorType.INVALID_URL, "URL is missing a hostname")

            # Basic hostname validation
            hostname = parsed.hostname
            if len(hostname) > 253:
                return (False, NavigationErrorType.INVALID_URL, "Hostname exceeds maximum length (253 characters)")

            # Reject bare TLDs like 'http://com'
            if "." not in hostname and hostname not in ("localhost",):
                return (False, NavigationErrorType.INVALID_URL, f"Invalid hostname: '{hostname}'")

        logger.debug(f"URL validation passed: {url}")
        return (True, None, None)

    def validate_redirect_count(self, redirect_count: int) -> Tuple[bool, Optional[str]]:
        """
        Validate that redirect count has not exceeded the maximum allowed.

        Returns:
            Tuple of (is_within_limit, error_message)
        """
        if redirect_count >= self.config.maximum_redirects:
            msg = f"Redirect limit exceeded: {redirect_count} >= {self.config.maximum_redirects}"
            logger.warning(msg)
            return (False, msg)
        return (True, None)

    def detect_redirect_loop(self, urls: List[str]) -> Tuple[bool, Optional[str]]:
        """
        Detect redirect loops in a chain of URLs.

        Returns:
            Tuple of (has_loop, description)
        """
        seen = set()
        for url in urls:
            normalized = url.rstrip("/").lower()
            if normalized in seen:
                msg = f"Redirect loop detected: '{url}' visited twice"
                logger.warning(msg)
                return (True, msg)
            seen.add(normalized)
        return (False, None)

    def validate_timeout(self, timeout_ms: float) -> Tuple[bool, Optional[str]]:
        """
        Validate that a timeout value is within acceptable bounds.

        Returns:
            Tuple of (is_valid, error_message)
        """
        if timeout_ms <= 0:
            return (False, "Timeout must be a positive number")
        if timeout_ms > 300000:  # 5 minutes hard ceiling
            return (False, f"Timeout {timeout_ms}ms exceeds maximum allowed (300000ms)")
        return (True, None)

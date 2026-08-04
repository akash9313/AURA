"""
Navigation Engine Configuration.
Configurable infrastructure settings for browser navigation, timeouts, retries, and wait strategies.
"""

from dataclasses import dataclass
from typing import Optional
from browser.navigation.models import WaitStrategy


@dataclass
class NavigationConfig:
    """Configurable infrastructure settings for the Navigation Engine."""
    navigation_timeout_ms: float = 30000.0
    retry_count: int = 2
    retry_delay_ms: float = 1000.0
    default_wait_strategy: WaitStrategy = WaitStrategy.LOAD_EVENT
    maximum_redirects: int = 20
    network_idle_timeout_ms: float = 5000.0
    dom_ready_timeout_ms: float = 10000.0
    custom_selector_timeout_ms: float = 15000.0
    allowed_protocols: tuple = ("http", "https", "file", "about", "data")
    record_history: bool = True
    max_history_entries: int = 500
    log_redirects: bool = True
    default_page_id: Optional[str] = None

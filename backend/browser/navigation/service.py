"""
Navigation Engine Service.
Top-level service integrating the Navigator with the AURA runtime lifecycle.
Bridges between BrowserManager page handles and the Navigation Engine.
"""

import logging
from typing import Any, Dict, Optional

from browser.navigation.configuration import NavigationConfig
from browser.navigation.events import NavigationEvent
from browser.navigation.history import NavigationHistory
from browser.navigation.models import (
    NavigationHealthStatus,
    NavigationHistoryInfo,
    NavigationResult,
    NavigationState,
    WaitStrategy,
)
from browser.navigation.navigator import Navigator

logger = logging.getLogger("AURA.Browser.Navigation.Service")


class PageHandleResolver:
    """
    Resolves page IDs to underlying page handles via the BrowserManager's PageManager.
    Decouples the Navigation Engine from Playwright and from the PageManager implementation.
    """

    def __init__(self, page_manager: Any = None):
        self.page_manager = page_manager

    def get_page_handle(self, page_id: str) -> Any:
        """Resolve page_id to page handle. Returns None if unavailable."""
        if self.page_manager and hasattr(self.page_manager, "get_page_handle"):
            return self.page_manager.get_page_handle(page_id)
        return None


class NavigationService:
    """
    Navigation Engine Service.
    Exposes a clean, provider-independent navigation API for the rest of AURA.
    Integrates with BrowserManager for page handle resolution.
    Publishes navigation lifecycle events to the AURA EventBus.
    """

    def __init__(
        self,
        bus: Any = None,
        config: Optional[NavigationConfig] = None,
        page_manager: Any = None,
    ):
        self.bus = bus
        self.config = config or NavigationConfig()
        self.resolver = PageHandleResolver(page_manager=page_manager)

        self.navigator = Navigator(
            bus=bus,
            config=self.config,
            page_resolver=self.resolver,
        )

        logger.info("NavigationService initialized")

    # ------------------------------------------------------------------
    # Navigation Commands
    # ------------------------------------------------------------------

    async def open_url(
        self,
        url: str,
        page_id: Optional[str] = None,
        wait_strategy: Optional[WaitStrategy] = None,
        selector: Optional[str] = None,
        timeout_ms: Optional[float] = None,
    ) -> NavigationResult:
        """Navigate the specified page to a URL."""
        logger.info(f"NavigationService.open_url('{url}', page_id='{page_id}')")
        return await self.navigator.open_url(
            url=url,
            page_id=page_id,
            wait_strategy=wait_strategy,
            selector=selector,
            timeout_ms=timeout_ms,
        )

    async def reload(self, page_id: Optional[str] = None, timeout_ms: Optional[float] = None) -> NavigationResult:
        """Reload the current page."""
        logger.info(f"NavigationService.reload(page_id='{page_id}')")
        return await self.navigator.reload(page_id=page_id, timeout_ms=timeout_ms)

    async def go_back(self, page_id: Optional[str] = None, timeout_ms: Optional[float] = None) -> NavigationResult:
        """Navigate back one step."""
        logger.info(f"NavigationService.go_back(page_id='{page_id}')")
        return await self.navigator.go_back(page_id=page_id, timeout_ms=timeout_ms)

    async def go_forward(self, page_id: Optional[str] = None, timeout_ms: Optional[float] = None) -> NavigationResult:
        """Navigate forward one step."""
        logger.info(f"NavigationService.go_forward(page_id='{page_id}')")
        return await self.navigator.go_forward(page_id=page_id, timeout_ms=timeout_ms)

    async def stop_loading(self, page_id: Optional[str] = None) -> NavigationResult:
        """Stop the current page from loading."""
        logger.info(f"NavigationService.stop_loading(page_id='{page_id}')")
        return await self.navigator.stop_loading(page_id=page_id)

    # ------------------------------------------------------------------
    # Query Commands
    # ------------------------------------------------------------------

    async def current_url(self, page_id: Optional[str] = None) -> str:
        """Get the current URL of the page."""
        return await self.navigator.current_url(page_id=page_id)

    async def current_title(self, page_id: Optional[str] = None) -> str:
        """Get the current title of the page."""
        return await self.navigator.current_title(page_id=page_id)

    # ------------------------------------------------------------------
    # Wait Commands
    # ------------------------------------------------------------------

    async def wait_for_page_load(self, page_id: Optional[str] = None, timeout_ms: Optional[float] = None) -> float:
        """Wait for page load event."""
        return await self.navigator.wait_for_page_load(page_id=page_id, timeout_ms=timeout_ms)

    async def wait_for_network_idle(self, page_id: Optional[str] = None, timeout_ms: Optional[float] = None) -> float:
        """Wait for network idle."""
        return await self.navigator.wait_for_network_idle(page_id=page_id, timeout_ms=timeout_ms)

    async def wait_for_dom_ready(self, page_id: Optional[str] = None, timeout_ms: Optional[float] = None) -> float:
        """Wait for DOMContentLoaded."""
        return await self.navigator.wait_for_dom_ready(page_id=page_id, timeout_ms=timeout_ms)

    # ------------------------------------------------------------------
    # History & Health
    # ------------------------------------------------------------------

    def get_history_info(self, page_id: Optional[str] = None) -> NavigationHistoryInfo:
        """Get navigation history summary."""
        return self.navigator.get_history_info(page_id=page_id)

    def get_health_status(self) -> NavigationHealthStatus:
        """Get navigation engine health telemetry."""
        return self.navigator.get_health_status()

    def is_healthy(self) -> bool:
        """Check if the navigation engine is operational."""
        status = self.get_health_status()
        return status.state not in (NavigationState.FAILED,)

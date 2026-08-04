"""
Browser Action Service.
Top-level AURA service integrating the ActionEngine into the kernel runtime.
Exposes high-level, human-like browser actions for the Workflow Engine and LLM Agents.
"""

import logging
from typing import Any, Dict, List, Optional, Union

from core.service import Service
from browser.actions.action_engine import ActionEngine
from browser.actions.models import (
    ActionEngineConfig,
    ActionHealthStatus,
    ActionOptions,
    ActionResult,
    ScrollDirection,
)

logger = logging.getLogger("AURA.Browser.Actions.Service")


class BrowserActionService(Service):
    """
    Browser Action Service.
    High-level interface used by the Workflow Engine and LLM to interact with web pages.
    Hides all provider-specific Playwright details behind clean interfaces.
    """

    def __init__(
        self,
        bus: Any = None,
        config: Optional[ActionEngineConfig] = None,
        page_manager: Any = None,
    ):
        super().__init__(bus)
        self.config = config or ActionEngineConfig()
        self.page_manager = page_manager

        # Inject page handle lookup resolver
        resolver = lambda pid: self.page_manager.get_page_handle(pid) if self.page_manager and hasattr(self.page_manager, "get_page_handle") else None

        self.engine = ActionEngine(
            bus=bus,
            config=self.config,
            page_resolver=resolver,
        )

        logger.info("BrowserActionService initialized")

    # ------------------------------------------------------------------
    # High-level Workflow & LLM API
    # ------------------------------------------------------------------

    async def click(self, target: Any, page_id: Optional[str] = None, options: Optional[ActionOptions] = None) -> ActionResult:
        """Click element by human query (e.g. browser.click("Sign In"))."""
        logger.info(f"BrowserActionService.click('{target}', page_id='{page_id}')")
        return await self.engine.click(target, page_id=page_id, options=options)

    async def double_click(self, target: Any, page_id: Optional[str] = None, options: Optional[ActionOptions] = None) -> ActionResult:
        """Double click element."""
        logger.info(f"BrowserActionService.double_click('{target}', page_id='{page_id}')")
        return await self.engine.double_click(target, page_id=page_id, options=options)

    async def right_click(self, target: Any, page_id: Optional[str] = None, options: Optional[ActionOptions] = None) -> ActionResult:
        """Right click element."""
        logger.info(f"BrowserActionService.right_click('{target}', page_id='{page_id}')")
        return await self.engine.right_click(target, page_id=page_id, options=options)

    async def hover(self, target: Any, page_id: Optional[str] = None, options: Optional[ActionOptions] = None) -> ActionResult:
        """Hover over element."""
        logger.info(f"BrowserActionService.hover('{target}', page_id='{page_id}')")
        return await self.engine.hover(target, page_id=page_id, options=options)

    async def type(self, target: Any, text: str, page_id: Optional[str] = None, options: Optional[ActionOptions] = None) -> ActionResult:
        """Type text into element (e.g. browser.type("Search", "Artificial Intelligence"))."""
        logger.info(f"BrowserActionService.type('{target}', '{text[:20]}...', page_id='{page_id}')")
        return await self.engine.type(target, text, page_id=page_id, options=options)

    async def clear(self, target: Any, page_id: Optional[str] = None, options: Optional[ActionOptions] = None) -> ActionResult:
        """Clear text input field."""
        logger.info(f"BrowserActionService.clear('{target}', page_id='{page_id}')")
        return await self.engine.clear(target, page_id=page_id, options=options)

    async def select(self, target: Any, option: str, page_id: Optional[str] = None, options: Optional[ActionOptions] = None) -> ActionResult:
        """Select dropdown option."""
        logger.info(f"BrowserActionService.select('{target}', option='{option}', page_id='{page_id}')")
        return await self.engine.select(target, option, page_id=page_id, options=options)

    async def check(self, target: Any, page_id: Optional[str] = None, options: Optional[ActionOptions] = None) -> ActionResult:
        """Check checkbox."""
        logger.info(f"BrowserActionService.check('{target}', page_id='{page_id}')")
        return await self.engine.check(target, page_id=page_id, options=options)

    async def uncheck(self, target: Any, page_id: Optional[str] = None, options: Optional[ActionOptions] = None) -> ActionResult:
        """Uncheck checkbox."""
        logger.info(f"BrowserActionService.uncheck('{target}', page_id='{page_id}')")
        return await self.engine.uncheck(target, page_id=page_id, options=options)

    async def scroll(
        self,
        direction: ScrollDirection = ScrollDirection.DOWN,
        target: Optional[Any] = None,
        page_id: Optional[str] = None,
        options: Optional[ActionOptions] = None,
    ) -> ActionResult:
        """Scroll page or container."""
        logger.info(f"BrowserActionService.scroll(direction={direction.value}, page_id='{page_id}')")
        return await self.engine.scroll(direction=direction, target=target, page_id=page_id, options=options)

    async def submit(self, target: Any, page_id: Optional[str] = None, options: Optional[ActionOptions] = None) -> ActionResult:
        """Submit form (e.g. browser.submit("Search Form"))."""
        logger.info(f"BrowserActionService.submit('{target}', page_id='{page_id}')")
        return await self.engine.submit(target, page_id=page_id, options=options)

    async def upload(
        self, target: Any, file_paths: Union[str, List[str]], page_id: Optional[str] = None, options: Optional[ActionOptions] = None
    ) -> ActionResult:
        """Upload file(s) to input element."""
        logger.info(f"BrowserActionService.upload('{target}', page_id='{page_id}')")
        return await self.engine.upload(target, file_paths, page_id=page_id, options=options)

    async def download(
        self,
        target: Any,
        download_directory: Optional[str] = None,
        page_id: Optional[str] = None,
        options: Optional[ActionOptions] = None,
    ) -> ActionResult:
        """Click and download file."""
        logger.info(f"BrowserActionService.download('{target}', page_id='{page_id}')")
        return await self.engine.download(target, download_directory=download_directory, page_id=page_id, options=options)

    # ------------------------------------------------------------------
    # Lifecycle & Health
    # ------------------------------------------------------------------

    def start(self) -> None:
        logger.info("BrowserActionService starting...")

    def stop(self) -> None:
        logger.info("BrowserActionService stopping...")

    def is_healthy(self) -> bool:
        return True

    def get_health_status(self) -> ActionHealthStatus:
        return self.engine.get_health_status()

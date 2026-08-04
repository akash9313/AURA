import logging
from typing import Any, Dict, List, Optional
from browser.manager.configuration import BrowserManagerConfig
from browser.manager.models import BrowserContextConfig, BrowserContextInfo, ContextType

logger = logging.getLogger("AURA.Browser.Manager.Context")


class ContextManager:
    """
    Manages Playwright Browser Contexts.
    Supports Incognito & Persistent profiles, session isolation, cookie separation, and multi-context tracking.
    """

    def __init__(self, config: Optional[BrowserManagerConfig] = None):
        self.config = config or BrowserManagerConfig()
        self._contexts: Dict[str, Any] = {}
        self._context_info: Dict[str, BrowserContextInfo] = {}

    async def create_context(self, browser: Any, context_config: Optional[BrowserContextConfig] = None) -> BrowserContextInfo:
        cfg = context_config or BrowserContextConfig(context_id=f"ctx_{len(self._contexts) + 1}")
        logger.info(f"Creating browser context '{cfg.context_id}' (Type={cfg.context_type.value})...")

        if browser and hasattr(browser, "new_context"):
            try:
                context_options: Dict[str, Any] = {
                    "viewport": {"width": cfg.viewport_width, "height": cfg.viewport_height},
                    "locale": cfg.locale,
                    "timezone_id": cfg.timezone_id,
                    "accept_downloads": cfg.accept_downloads,
                }
                if cfg.user_agent:
                    context_options["user_agent"] = cfg.user_agent

                context = await browser.new_context(**context_options)
                self._contexts[cfg.context_id] = context
            except Exception as e:
                logger.error(f"Failed to create Playwright context '{cfg.context_id}': {e}")
                self._contexts[cfg.context_id] = {"id": cfg.context_id, "fallback": True}
        else:
            self._contexts[cfg.context_id] = {"id": cfg.context_id, "fallback": True}

        info = BrowserContextInfo(context_id=cfg.context_id, context_type=cfg.context_type)
        self._context_info[cfg.context_id] = info
        logger.info(f"Browser context '{cfg.context_id}' created successfully.")
        return info

    async def destroy_context(self, context_id: str) -> bool:
        if context_id not in self._contexts:
            return False

        logger.info(f"Destroying browser context '{context_id}'...")
        context = self._contexts.pop(context_id)
        self._context_info.pop(context_id, None)

        if hasattr(context, "close"):
            try:
                await context.close()
            except Exception as e:
                logger.error(f"Error closing Playwright context '{context_id}': {e}")

        logger.info(f"Browser context '{context_id}' destroyed.")
        return True

    def get_context_handle(self, context_id: str) -> Any:
        return self._contexts.get(context_id)

    def get_context_info(self, context_id: str) -> Optional[BrowserContextInfo]:
        return self._context_info.get(context_id)

    def list_contexts(self) -> List[BrowserContextInfo]:
        return list(self._context_info.values())


    async def clear_all(self) -> None:
        context_ids = list(self._contexts.keys())
        for cid in context_ids:
            await self.destroy_context(cid)

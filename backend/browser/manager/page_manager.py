import logging
from typing import Any, Dict, List, Optional
from browser.manager.models import BrowserPageInfo

logger = logging.getLogger("AURA.Browser.Manager.Page")


class PageManager:
    """
    Manages Browser Pages (Tabs).
    Handles page creation, closing, switching, active state tracking, and metadata querying.
    """

    def __init__(self):
        self._pages: Dict[str, Any] = {}
        self._page_info: Dict[str, BrowserPageInfo] = {}
        self.active_page_id: Optional[str] = None

    async def create_page(self, context_handle: Any, context_id: str, url: Optional[str] = None) -> BrowserPageInfo:
        page_id = f"page_{len(self._pages) + 1}"
        target_url = url or "about:blank"
        title = "New Tab"

        if context_handle and hasattr(context_handle, "new_page"):
            try:
                page = await context_handle.new_page()
                if url:
                    await page.goto(url)
                page_id = str(id(page))
                title = await page.title() or "New Tab"
                target_url = page.url
                self._pages[page_id] = page
            except Exception as e:
                logger.error(f"Error creating Playwright page: {e}")
                self._pages[page_id] = {"id": page_id, "url": target_url, "title": title}
        else:
            self._pages[page_id] = {"id": page_id, "url": target_url, "title": title}

        # Deactivate current active page
        if self.active_page_id and self.active_page_id in self._page_info:
            self._page_info[self.active_page_id].is_active = False

        self.active_page_id = page_id
        page_info = BrowserPageInfo(
            page_id=page_id,
            context_id=context_id,
            url=target_url,
            title=title,
            is_active=True
        )
        self._page_info[page_id] = page_info
        logger.info(f"Page '{page_id}' created in context '{context_id}' -> {target_url}")
        return page_info

    async def close_page(self, page_id: str) -> bool:
        if page_id not in self._pages:
            return False

        logger.info(f"Closing page '{page_id}'...")
        page = self._pages.pop(page_id)
        self._page_info.pop(page_id, None)

        if hasattr(page, "close"):
            try:
                await page.close()
            except Exception as e:
                logger.error(f"Error closing Playwright page '{page_id}': {e}")

        if self.active_page_id == page_id:
            self.active_page_id = list(self._pages.keys())[0] if self._pages else None
            if self.active_page_id and self.active_page_id in self._page_info:
                self._page_info[self.active_page_id].is_active = True

        logger.info(f"Page '{page_id}' closed.")
        return True

    def switch_page(self, page_id: str) -> Optional[BrowserPageInfo]:
        if page_id not in self._page_info:
            return None

        for pid, info in self._page_info.items():
            info.is_active = (pid == page_id)

        self.active_page_id = page_id
        logger.info(f"Switched active page to '{page_id}'")
        return self._page_info[page_id]

    def get_current_page(self) -> Optional[BrowserPageInfo]:
        if self.active_page_id:
            return self._page_info.get(self.active_page_id)
        return None


    def find_pages_by_context(self, context_id: str) -> List[BrowserPageInfo]:
        return [info for info in self._page_info.values() if info.context_id == context_id]

    def get_page_handle(self, page_id: str) -> Any:
        return self._pages.get(page_id)

    async def clear_all(self) -> None:
        pids = list(self._pages.keys())
        for pid in pids:
            await self.close_page(pid)

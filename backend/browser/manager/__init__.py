from browser.manager.browser_factory import BrowserFactory
from browser.manager.browser_manager import PlaywrightBrowserManager
from browser.manager.configuration import BrowserManagerConfig
from browser.manager.context_manager import ContextManager
from browser.manager.events import BrowserManagerEvent
from browser.manager.lifecycle import BrowserLifecycleManager
from browser.manager.models import (
    BrowserContextConfig,
    BrowserContextInfo,
    BrowserHealthStatus,
    BrowserPageInfo,
    BrowserState,
    ContextType,
)
from browser.manager.page_manager import PageManager

BrowserManager = PlaywrightBrowserManager

__all__ = [
    "BrowserManager",
    "PlaywrightBrowserManager",
    "BrowserFactory",
    "ContextManager",
    "PageManager",
    "BrowserLifecycleManager",
    "BrowserManagerConfig",
    "BrowserManagerEvent",
    "BrowserState",
    "ContextType",
    "BrowserContextConfig",
    "BrowserContextInfo",
    "BrowserPageInfo",
    "BrowserHealthStatus",
]


from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, Optional
import time


from browser.manager.models import BrowserState, ContextType



@dataclass
class BrowserTabInfo:
    page_id: str
    url: str
    title: str
    created_at: float = field(default_factory=time.time)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "page_id": self.page_id,
            "url": self.url,
            "title": self.title,
            "created_at": self.created_at,
        }


@dataclass
class PageSnapshot:
    page_id: str
    url: str
    title: str
    html_content: str
    screenshot_bytes: Optional[bytes] = None
    timestamp: float = field(default_factory=time.time)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "page_id": self.page_id,
            "url": self.url,
            "title": self.title,
            "timestamp": self.timestamp,
            "has_screenshot": self.screenshot_bytes is not None,
        }


@dataclass
class BrowserElement:
    selector: str
    text: str = ""
    tag_name: str = "div"
    attributes: Dict[str, str] = field(default_factory=dict)


@dataclass
class BrowserResult:
    success: bool
    url: str = ""
    title: str = ""
    content: str = ""
    visible_text: str = ""
    error: Optional[str] = None
    elements: List[BrowserElement] = field(default_factory=list)



@dataclass
class BrowserSession:
    session_id: str
    active_url: str = ""
    created_at: float = field(default_factory=time.time)


class BrowserActionType(Enum):
    OPEN_URL = "open_url"
    NAVIGATE = "navigate"
    SEARCH = "search"
    EXTRACT_PAGE = "extract_page"
    EXTRACT = "extract"
    FILL_FORM = "fill_form"
    CLICK_ELEMENT = "click_element"
    CLICK = "click"
    DOWNLOAD = "download"
    UPLOAD = "upload"
    SWITCH_TAB = "switch_tab"
    CLOSE_TAB = "close_tab"
    SCREENSHOT = "screenshot"


class BrowserPermissionLevel(Enum):
    ALWAYS_ALLOWED = "always_allowed"
    REQUIRES_CONFIRMATION = "requires_confirmation"
    BLOCKED = "blocked"
    READ = "read"
    WRITE = "write"
    ADMIN = "admin"




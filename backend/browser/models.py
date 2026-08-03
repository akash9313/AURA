from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List, Optional


class BrowserPermissionLevel(Enum):
    """Safety permission levels for web interactions."""
    ALWAYS_ALLOWED = "always_allowed"
    REQUIRES_CONFIRMATION = "requires_confirmation"
    BLOCKED = "blocked"


class BrowserActionType(Enum):
    """Categories of web automation operations."""
    OPEN_URL = "open_url"
    SEARCH = "search"
    EXTRACT_PAGE = "extract_page"
    FILL_FORM = "fill_form"
    CLICK_ELEMENT = "click_element"
    DOWNLOAD = "download"
    UPLOAD = "upload"
    SWITCH_TAB = "switch_tab"
    CLOSE_TAB = "close_tab"
    SCREENSHOT = "screenshot"


@dataclass
class BrowserElement:
    """Representation of an interactive DOM HTML element."""
    tag: str
    text: str = ""
    attributes: Dict[str, str] = field(default_factory=dict)
    is_visible: bool = True
    selector: str = ""

    def to_dict(self) -> Dict[str, Any]:
        return {
            "tag": self.tag,
            "text": self.text,
            "attributes": self.attributes,
            "is_visible": self.is_visible,
            "selector": self.selector
        }


@dataclass
class BrowserCookie:
    """Web browser session cookie representation."""
    name: str
    value: str
    domain: str
    path: str = "/"

    def to_dict(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "value": self.value,
            "domain": self.domain,
            "path": self.path
        }


@dataclass
class BrowserSession:
    """Browser session context state."""
    session_id: str
    is_incognito: bool = False
    cookies: List[BrowserCookie] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "session_id": self.session_id,
            "is_incognito": self.is_incognito,
            "cookies": [c.to_dict() for c in self.cookies]
        }


@dataclass
class BrowserResult:
    """Standardized output structure for all browser operations."""
    success: bool
    url: str = ""
    title: str = ""
    visible_text: str = ""
    elements: List[BrowserElement] = field(default_factory=list)
    screenshots: List[str] = field(default_factory=list)
    downloads: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)
    execution_time: float = 0.0

    def to_dict(self) -> Dict[str, Any]:
        return {
            "success": self.success,
            "url": self.url,
            "title": self.title,
            "visible_text": self.visible_text[:200] if self.visible_text else "",
            "elements": [e.to_dict() for e in self.elements[:50]],
            "screenshots": self.screenshots,
            "downloads": self.downloads,
            "metadata": self.metadata,
            "execution_time": self.execution_time
        }

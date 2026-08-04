import time
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List, Optional


class BrowserState(Enum):
    UNINITIALIZED = "uninitialized"
    STARTING = "starting"
    RUNNING = "running"
    RESTARTING = "restarting"
    STOPPING = "stopping"
    STOPPED = "stopped"
    CRASHED = "crashed"
    ERROR = "error"


class ContextType(Enum):
    INCOGNITO = "incognito"
    PERSISTENT = "persistent"


@dataclass
class BrowserContextConfig:
    context_id: str
    context_type: ContextType = ContextType.INCOGNITO
    user_data_dir: Optional[str] = None
    viewport_width: int = 1280
    viewport_height: int = 800
    user_agent: Optional[str] = None
    locale: str = "en-US"
    timezone_id: str = "America/New_York"
    proxy: Optional[Dict[str, str]] = None
    accept_downloads: bool = True
    extra_http_headers: Dict[str, str] = field(default_factory=dict)


@dataclass
class BrowserContextInfo:
    context_id: str
    context_type: ContextType
    page_ids: List[str] = field(default_factory=list)
    created_at: float = field(default_factory=time.time)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "context_id": self.context_id,
            "context_type": self.context_type.value,
            "page_count": len(self.page_ids),
            "created_at": self.created_at,
        }


@dataclass
class BrowserPageInfo:
    page_id: str
    context_id: str
    url: str = "about:blank"
    title: str = "New Tab"
    is_active: bool = False
    created_at: float = field(default_factory=time.time)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "page_id": self.page_id,
            "context_id": self.context_id,
            "url": self.url,
            "title": self.title,
            "is_active": self.is_active,
            "created_at": self.created_at,
        }


@dataclass
class BrowserHealthStatus:
    state: BrowserState
    is_browser_alive: bool
    active_contexts_count: int
    active_pages_count: int
    memory_mb: float = 0.0
    uptime_seconds: float = 0.0
    last_error: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "state": self.state.value,
            "is_browser_alive": self.is_browser_alive,
            "active_contexts_count": self.active_contexts_count,
            "active_pages_count": self.active_pages_count,
            "memory_mb": self.memory_mb,
            "uptime_seconds": self.uptime_seconds,
            "last_error": self.last_error,
        }

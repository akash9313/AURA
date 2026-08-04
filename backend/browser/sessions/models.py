import time
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List, Optional


class SessionState(Enum):
    CREATED = "created"
    ACTIVE = "active"
    IDLE = "idle"
    SAVED = "saved"
    EXPIRED = "expired"
    DESTROYED = "destroyed"
    CORRUPTED = "corrupted"


class SessionType(Enum):
    PERSISTENT = "persistent"
    TEMPORARY = "temporary"
    INCOGNITO = "incognito"
    REMOTE = "remote"


@dataclass
class CookieData:
    name: str
    value: str
    domain: str
    path: str = "/"
    expires: Optional[float] = None
    http_only: bool = False
    secure: bool = False
    same_site: str = "Lax"

    def to_dict(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "value": self.value,
            "domain": self.domain,
            "path": self.path,
            "expires": self.expires,
            "http_only": self.http_only,
            "secure": self.secure,
            "same_site": self.same_site,
        }


@dataclass
class StorageStateData:
    cookies: List[CookieData] = field(default_factory=list)
    local_storage: Dict[str, Dict[str, str]] = field(default_factory=dict)
    session_storage: Dict[str, Dict[str, str]] = field(default_factory=dict)
    auth_tokens: Dict[str, str] = field(default_factory=dict)

    def to_dict(self, mask_tokens: bool = True) -> Dict[str, Any]:
        tokens = {}
        for k, v in self.auth_tokens.items():
            tokens[k] = "***MASKED***" if mask_tokens else v

        return {
            "cookies": [c.to_dict() for c in self.cookies],
            "local_storage": self.local_storage,
            "session_storage": self.session_storage,
            "auth_tokens": tokens,
        }


@dataclass
class BrowserSessionData:
    session_id: str
    name: str
    session_type: SessionType
    storage_state: StorageStateData = field(default_factory=StorageStateData)
    user_agent: Optional[str] = None
    viewport_width: int = 1280
    viewport_height: int = 800
    download_dir: Optional[str] = None
    user_preferences: Dict[str, Any] = field(default_factory=dict)
    created_at: float = field(default_factory=time.time)
    last_accessed_at: float = field(default_factory=time.time)

    def to_dict(self, mask_tokens: bool = True) -> Dict[str, Any]:
        return {
            "session_id": self.session_id,
            "name": self.name,
            "session_type": self.session_type.value,
            "storage_state": self.storage_state.to_dict(mask_tokens=mask_tokens),
            "user_agent": self.user_agent,
            "viewport": {"width": self.viewport_width, "height": self.viewport_height},
            "download_dir": self.download_dir,
            "user_preferences": self.user_preferences,
            "created_at": self.created_at,
            "last_accessed_at": self.last_accessed_at,
        }


@dataclass
class BrowserSessionInfo:
    session_id: str
    name: str
    session_type: SessionType
    state: SessionState
    created_at: float
    last_accessed_at: float
    is_persistent: bool

    def to_dict(self) -> Dict[str, Any]:
        return {
            "session_id": self.session_id,
            "name": self.name,
            "session_type": self.session_type.value,
            "state": self.state.value,
            "created_at": self.created_at,
            "last_accessed_at": self.last_accessed_at,
            "is_persistent": self.is_persistent,
        }


@dataclass
class SessionHealthStatus:
    active_sessions_count: int
    persistent_sessions_count: int
    expired_sessions_count: int
    total_storage_mb: float = 0.0

    def to_dict(self) -> Dict[str, Any]:
        return {
            "active_sessions_count": self.active_sessions_count,
            "persistent_sessions_count": self.persistent_sessions_count,
            "expired_sessions_count": self.expired_sessions_count,
            "total_storage_mb": self.total_storage_mb,
        }

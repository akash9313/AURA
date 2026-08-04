from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List, Optional
import time


class APIScope(Enum):
    READ_MEMORY = "read:memory"
    WRITE_MEMORY = "write:memory"
    EXECUTE_WORKFLOW = "execute:workflow"
    DESKTOP_AUTOMATION = "desktop:automation"
    BROWSER_AUTOMATION = "browser:automation"
    KNOWLEDGE_SEARCH = "knowledge:search"
    KNOWLEDGE_IMPORT = "knowledge:import"
    PLUGIN_MANAGE = "plugin:manage"


@dataclass
class APIKey:
    """API Key credentials for external developer authentication."""
    key_id: str
    secret_key: str
    name: str
    scopes: List[APIScope] = field(default_factory=list)
    created_at: float = field(default_factory=time.time)
    is_active: bool = True


@dataclass
class RateLimitRule:
    """Rate limit configuration rule."""
    requests_per_minute: int = 60
    burst_limit: int = 100


@dataclass
class APIResponse:
    """Standardized API Response wrapper."""
    success: bool
    status_code: int
    message: str
    data: Optional[Dict[str, Any]] = None
    version: str = "v1"

    def to_dict(self) -> Dict[str, Any]:
        return {
            "success": self.success,
            "status_code": self.status_code,
            "message": self.message,
            "data": self.data,
            "version": self.version,
        }


@dataclass
class WebhookSubscription:
    """Webhook URL subscription configuration."""
    subscription_id: str
    url: str
    events: List[str]
    secret: str
    created_at: float = field(default_factory=time.time)

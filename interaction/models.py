import time
import uuid
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List, Optional, Tuple


class InteractionMethod(Enum):
    UI_AUTOMATION = "ui_automation"
    BROWSER_DOM = "browser_dom"
    KEYBOARD = "keyboard"
    MOUSE = "mouse"
    VISION = "vision"
    CLIPBOARD = "clipboard"
    VOICE = "voice"
    MOBILE = "mobile"


class InteractionIntent(Enum):
    CLICK = "click"
    TYPE = "type"
    OPEN = "open"
    CLOSE = "close"
    SELECT = "select"
    COPY = "copy"
    PASTE = "paste"
    SCROLL = "scroll"
    SEARCH = "search"
    SUBMIT = "submit"
    SAVE = "save"
    UPLOAD = "upload"
    DOWNLOAD = "download"
    FOCUS = "focus"


@dataclass
class InteractionTarget:
    name: Optional[str] = None
    automation_id: Optional[str] = None
    selector: Optional[str] = None
    coordinates: Optional[Tuple[int, int]] = None
    text_value: Optional[str] = None
    window_title: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "automation_id": self.automation_id,
            "selector": self.selector,
            "coordinates": self.coordinates,
            "text_value": self.text_value,
            "window_title": self.window_title,
        }


@dataclass
class InteractionGoal:
    goal_id: str = field(default_factory=lambda: f"goal_{uuid.uuid4().hex[:8]}")
    intent: InteractionIntent = InteractionIntent.CLICK
    target: InteractionTarget = field(default_factory=InteractionTarget)
    params: Dict[str, Any] = field(default_factory=dict)
    preferred_method: Optional[InteractionMethod] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "goal_id": self.goal_id,
            "intent": self.intent.value,
            "target": self.target.to_dict(),
            "params": self.params,
            "preferred_method": self.preferred_method.value if self.preferred_method else None,
        }


@dataclass
class InteractionResult:
    success: bool
    method_used: InteractionMethod
    confidence: float
    fallback_count: int
    duration_ms: float
    message: str
    data: Optional[Dict[str, Any]] = None
    timestamp: float = field(default_factory=time.time)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "success": self.success,
            "method_used": self.method_used.value,
            "confidence": self.confidence,
            "fallback_count": self.fallback_count,
            "duration_ms": self.duration_ms,
            "message": self.message,
            "data": self.data or {},
            "timestamp": self.timestamp,
        }

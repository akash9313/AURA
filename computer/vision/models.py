import time
import uuid
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List, Optional, Tuple


class VisualElementType(Enum):
    BUTTON = "button"
    TEXT = "text"
    ICON = "icon"
    MENU = "menu"
    DIALOG = "dialog"
    TOOLBAR = "toolbar"
    STATUSBAR = "statusbar"
    LIST = "list"
    TREE = "tree"
    CARD = "card"
    FORM = "form"
    IMAGE = "image"
    UNKNOWN = "unknown"


@dataclass
class VisualElement:
    element_id: str = field(default_factory=lambda: f"vis_{uuid.uuid4().hex[:8]}")
    element_type: VisualElementType = VisualElementType.UNKNOWN
    bounds: Tuple[int, int, int, int] = (0, 0, 0, 0)
    text: Optional[str] = None
    confidence: float = 1.0
    parent_id: Optional[str] = None
    child_ids: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "element_id": self.element_id,
            "element_type": self.element_type.value,
            "bounds": self.bounds,
            "text": self.text,
            "confidence": self.confidence,
            "parent_id": self.parent_id,
            "child_count": len(self.child_ids),
        }


@dataclass
class OCRResult:
    text: str
    bounds: Tuple[int, int, int, int]
    confidence: float = 1.0
    language: str = "en"

    def to_dict(self) -> Dict[str, Any]:
        return {
            "text": self.text,
            "bounds": self.bounds,
            "confidence": self.confidence,
            "language": self.language,
        }


@dataclass
class ScreenSnapshot:
    snapshot_id: str = field(default_factory=lambda: f"snap_{uuid.uuid4().hex[:8]}")
    bounds: Tuple[int, int, int, int] = (0, 0, 1920, 1080)
    scale_factor: float = 1.0
    timestamp: float = field(default_factory=time.time)
    image_hash: str = ""
    visual_elements: List[VisualElement] = field(default_factory=list)
    ocr_results: List[OCRResult] = field(default_factory=list)
    _raw_image_data: Optional[Any] = field(default=None, repr=False)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "snapshot_id": self.snapshot_id,
            "bounds": self.bounds,
            "scale_factor": self.scale_factor,
            "timestamp": self.timestamp,
            "image_hash": self.image_hash,
            "visual_element_count": len(self.visual_elements),
            "ocr_text_count": len(self.ocr_results),
        }


@dataclass
class VisualVerificationResult:
    changed: bool
    diff_score: float
    action_name: str
    message: str
    before_snapshot_id: str
    after_snapshot_id: str
    timestamp: float = field(default_factory=time.time)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "changed": self.changed,
            "diff_score": self.diff_score,
            "action_name": self.action_name,
            "message": self.message,
            "before_snapshot_id": self.before_snapshot_id,
            "after_snapshot_id": self.after_snapshot_id,
            "timestamp": self.timestamp,
        }

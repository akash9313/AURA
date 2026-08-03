from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Dict, List, Optional


@dataclass
class BoundingBox:
    """Represents a 2D bounding box in pixel or normalized coordinates."""
    x: int
    y: int
    width: int
    height: int

    def to_dict(self) -> Dict[str, int]:
        return {
            "x": self.x,
            "y": self.y,
            "width": self.width,
            "height": self.height
        }


@dataclass
class OCRItem:
    """Represents a recognized text segment with bounding box and confidence score."""
    text: str
    box: BoundingBox
    confidence: float = 1.0


@dataclass
class OCRResult:
    """Represents the complete result of an OCR extraction pass."""
    full_text: str
    items: List[OCRItem] = field(default_factory=list)
    confidence: float = 1.0

    def to_dict(self) -> Dict[str, Any]:
        return {
            "full_text": self.full_text,
            "items": [
                {
                    "text": item.text,
                    "box": item.box.to_dict(),
                    "confidence": item.confidence
                }
                for item in self.items
            ],
            "confidence": self.confidence
        }


@dataclass
class UIElement:
    """Represents a detected UI component (button, input field, menu, icon, etc.)."""
    element_type: str  # 'button', 'input', 'menu', 'icon', 'dialog', 'window', 'tab', 'scrollbar'
    label: str
    box: BoundingBox
    confidence: float = 1.0
    interactive: bool = True

    def to_dict(self) -> Dict[str, Any]:
        return {
            "element_type": self.element_type,
            "label": self.label,
            "box": self.box.to_dict(),
            "confidence": self.confidence,
            "interactive": self.interactive
        }


@dataclass
class DetectedObject:
    """Represents an object detected in an image."""
    label: str
    box: BoundingBox
    confidence: float = 1.0
    attributes: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "label": self.label,
            "box": self.box.to_dict(),
            "confidence": self.confidence,
            "attributes": self.attributes
        }


@dataclass
class DocumentAnalysisResult:
    """Represents extracted document structure and content."""
    text: str
    headings: List[str] = field(default_factory=list)
    tables: List[List[List[str]]] = field(default_factory=list)
    summary: str = ""
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "text": self.text,
            "headings": self.headings,
            "tables": self.tables,
            "summary": self.summary,
            "metadata": self.metadata
        }


@dataclass
class VisionResult:
    """Standardized output result structure returned by Vision Engine pipelines and tools."""
    description: str
    objects: List[DetectedObject] = field(default_factory=list)
    detected_text: Optional[OCRResult] = None
    ui_elements: List[UIElement] = field(default_factory=list)
    confidence: float = 1.0
    metadata: Dict[str, Any] = field(default_factory=dict)
    timestamp: datetime = field(default_factory=datetime.now)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "description": self.description,
            "objects": [obj.to_dict() for obj in self.objects],
            "detected_text": self.detected_text.to_dict() if self.detected_text else None,
            "ui_elements": [elem.to_dict() for elem in self.ui_elements],
            "confidence": self.confidence,
            "metadata": self.metadata,
            "timestamp": self.timestamp.isoformat()
        }

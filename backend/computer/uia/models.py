"""
UI Automation Engine Domain Models.
Defines ControlType, UIPattern, AURAUIElement, UIElementQuery, and UIActionResult.
Hides raw Microsoft UI Automation objects behind clean AURAUIElement abstractions.
"""

import time
import uuid
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List, Optional, Tuple


class ControlType(Enum):
    """Supported UI Automation control types."""
    WINDOW = "Window"
    BUTTON = "Button"
    TEXTBOX = "TextBox"
    EDIT = "Edit"
    MENU = "Menu"
    MENUITEM = "MenuItem"
    TREEVIEW = "TreeView"
    LISTVIEW = "ListView"
    TAB = "Tab"
    TABITEM = "TabItem"
    CHECKBOX = "CheckBox"
    RADIOBUTTON = "RadioButton"
    COMBOBOX = "ComboBox"
    SLIDER = "Slider"
    PROGRESSBAR = "ProgressBar"
    HYPERLINK = "Hyperlink"
    IMAGE = "Image"
    DOCUMENT = "Document"
    PANE = "Pane"
    TOOLBAR = "ToolBar"
    STATUSBAR = "StatusBar"
    UNKNOWN = "Unknown"


class UIPattern(Enum):
    """Supported UI Automation control patterns."""
    INVOKE = "Invoke"
    SELECTION = "Selection"
    VALUE = "Value"
    TOGGLE = "Toggle"
    EXPAND_COLLAPSE = "ExpandCollapse"
    SCROLL = "Scroll"
    TEXT = "Text"
    GRID = "Grid"


@dataclass
class AURAUIElement:
    """Platform-independent UI Automation Element domain model."""
    element_id: str = field(default_factory=lambda: f"elem_{uuid.uuid4().hex[:8]}")
    automation_id: str = ""
    name: str = ""
    control_type: ControlType = ControlType.UNKNOWN
    bounds: Tuple[int, int, int, int] = (0, 0, 0, 0)  # x, y, width, height
    is_enabled: bool = True
    is_visible: bool = True
    is_focused: bool = False
    value: Optional[str] = None
    parent_id: Optional[str] = None
    child_ids: List[str] = field(default_factory=list)
    supported_patterns: List[UIPattern] = field(default_factory=list)
    _raw_native_ref: Optional[Any] = field(default=None, repr=False)  # Encapsulated native UIA handle

    def to_dict(self) -> Dict[str, Any]:
        return {
            "element_id": self.element_id,
            "automation_id": self.automation_id,
            "name": self.name,
            "control_type": self.control_type.value,
            "bounds": self.bounds,
            "is_enabled": self.is_enabled,
            "is_visible": self.is_visible,
            "is_focused": self.is_focused,
            "value": self.value,
            "parent_id": self.parent_id,
            "child_count": len(self.child_ids),
            "supported_patterns": [p.value for p in self.supported_patterns],
        }


@dataclass
class UIElementQuery:
    """UI element search query parameters."""
    automation_id: Optional[str] = None
    name: Optional[str] = None
    control_type: Optional[ControlType] = None
    role: Optional[str] = None
    regex_pattern: Optional[str] = None
    relative_hierarchy: Optional[str] = None
    partial_match: bool = True


@dataclass
class UIActionResult:
    """Result of a UI Automation action."""
    success: bool
    element_id: str
    action: str
    message: str
    data: Optional[Dict[str, Any]] = None
    execution_time_ms: float = 0.0
    timestamp: float = field(default_factory=time.time)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "success": self.success,
            "element_id": self.element_id,
            "action": self.action,
            "message": self.message,
            "data": self.data or {},
            "execution_time_ms": self.execution_time_ms,
            "timestamp": self.timestamp,
        }

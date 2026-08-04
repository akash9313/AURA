"""
Browser Action Engine Domain Models.
Provider-independent data structures, enums, options, and results for high-level browser actions.
"""

import time
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List, Optional


class ActionType(Enum):
    """Supported high-level browser actions."""
    CLICK = "click"
    DOUBLE_CLICK = "double_click"
    RIGHT_CLICK = "right_click"
    HOVER = "hover"
    FOCUS = "focus"
    BLUR = "blur"
    TYPE_TEXT = "type_text"
    CLEAR_FIELD = "clear_field"
    PASTE = "paste"
    SELECT_DROPDOWN = "select_dropdown"
    CHECK_CHECKBOX = "check_checkbox"
    UNCHECK_CHECKBOX = "uncheck_checkbox"
    UPLOAD_FILE = "upload_file"
    DOWNLOAD_FILE = "download_file"
    SCROLL = "scroll"
    DRAG_AND_DROP = "drag_and_drop"
    KEYBOARD_SHORTCUT = "keyboard_shortcut"
    SUBMIT_FORM = "submit_form"


class LocatorStrategy(Enum):
    """Supported element location strategies."""
    ACCESSIBILITY_ROLE = "accessibility_role"
    VISIBLE_TEXT = "visible_text"
    LABEL = "label"
    PLACEHOLDER = "placeholder"
    AUTOMATION_ID = "automation_id"
    CSS_SELECTOR = "css_selector"
    XPATH = "xpath"
    RELATIVE_POSITION = "relative_position"
    SEMANTIC_SIMILARITY = "semantic_similarity"


class ActionState(Enum):
    """Lifecycle state of an action execution."""
    IDLE = "idle"
    LOCATING = "locating"
    EXECUTING = "executing"
    VERIFYING = "verifying"
    COMPLETED = "completed"
    FAILED = "failed"
    RETRYING = "retrying"


class ScrollDirection(Enum):
    """Directions for scroll actions."""
    UP = "up"
    DOWN = "down"
    LEFT = "left"
    RIGHT = "right"
    TO_ELEMENT = "to_element"
    TO_TOP = "to_top"
    TO_BOTTOM = "to_bottom"


@dataclass
class TargetElement:
    """Specification for locating a target element on the page."""
    query: str
    strategy: Optional[LocatorStrategy] = None
    role: Optional[str] = None
    text: Optional[str] = None
    label: Optional[str] = None
    placeholder: Optional[str] = None
    automation_id: Optional[str] = None
    css_selector: Optional[str] = None
    xpath: Optional[str] = None
    near_text: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "query": self.query,
            "strategy": self.strategy.value if self.strategy else None,
            "role": self.role,
            "text": self.text,
            "label": self.label,
            "placeholder": self.placeholder,
            "automation_id": self.automation_id,
            "css_selector": self.css_selector,
            "xpath": self.xpath,
            "near_text": self.near_text,
        }


@dataclass
class ActionOptions:
    """Configurable options for action execution."""
    timeout_ms: float = 30000.0
    retry_count: int = 2
    retry_delay_ms: float = 500.0
    human_delay_ms: float = 50.0
    typing_speed_cps: float = 50.0  # Characters per second
    scroll_into_view: bool = True
    force: bool = False
    verify_result: bool = True
    scroll_distance_px: int = 500

    def to_dict(self) -> Dict[str, Any]:
        return {
            "timeout_ms": self.timeout_ms,
            "retry_count": self.retry_count,
            "retry_delay_ms": self.retry_delay_ms,
            "human_delay_ms": self.human_delay_ms,
            "typing_speed_cps": self.typing_speed_cps,
            "scroll_into_view": self.scroll_into_view,
            "force": self.force,
            "verify_result": self.verify_result,
            "scroll_distance_px": self.scroll_distance_px,
        }


@dataclass
class DownloadResult:
    """Result of a file download operation."""
    success: bool
    file_path: Optional[str] = None
    file_name: Optional[str] = None
    file_size_bytes: int = 0
    mime_type: Optional[str] = None
    url: Optional[str] = None
    duration_ms: float = 0.0
    error: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "success": self.success,
            "file_path": self.file_path,
            "file_name": self.file_name,
            "file_size_bytes": self.file_size_bytes,
            "mime_type": self.mime_type,
            "url": self.url,
            "duration_ms": self.duration_ms,
            "error": self.error,
        }


@dataclass
class ActionResult:
    """Result returned after performing a browser action."""
    success: bool
    action_type: ActionType
    target_query: str
    target_selector: Optional[str] = None
    execution_time_ms: float = 0.0
    verified: bool = False
    error: Optional[str] = None
    retry_attempts: int = 0
    state: ActionState = ActionState.COMPLETED
    download_info: Optional[DownloadResult] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    timestamp: float = field(default_factory=time.time)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "success": self.success,
            "action_type": self.action_type.value,
            "target_query": self.target_query,
            "target_selector": self.target_selector,
            "execution_time_ms": self.execution_time_ms,
            "verified": self.verified,
            "error": self.error,
            "retry_attempts": self.retry_attempts,
            "state": self.state.value,
            "download_info": self.download_info.to_dict() if self.download_info else None,
            "metadata": self.metadata,
            "timestamp": self.timestamp,
        }


@dataclass
class ActionEngineConfig:
    """Infrastructure configuration settings for the Action Engine."""
    default_timeout_ms: float = 30000.0
    retry_count: int = 2
    retry_delay_ms: float = 500.0
    typing_speed_cps: float = 50.0
    scroll_speed_px: int = 500
    human_interaction_delay_ms: float = 50.0
    enable_smart_prechecks: bool = True
    enable_smart_verification: bool = True
    default_download_directory: Optional[str] = None


@dataclass
class ActionHealthStatus:
    """Health telemetry for the Action Engine."""
    state: ActionState
    total_actions: int
    successful_actions: int
    failed_actions: int
    average_execution_time_ms: float
    last_error: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "state": self.state.value,
            "total_actions": self.total_actions,
            "successful_actions": self.successful_actions,
            "failed_actions": self.failed_actions,
            "average_execution_time_ms": self.average_execution_time_ms,
            "last_error": self.last_error,
        }

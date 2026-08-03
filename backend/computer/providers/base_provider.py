from abc import ABC, abstractmethod
from typing import List, Optional, Tuple
from computer.models import AutomationResult, UIElement, WindowInfo


class BaseComputerProvider(ABC):
    """
    Abstract base provider defining low-level desktop automation primitives.
    Enables cross-platform adapters (Win32, PyAutoGUI, UI Automation, macOS, Linux).
    """

    @abstractmethod
    def launch_app(self, app_name_or_path: str) -> AutomationResult:
        pass

    @abstractmethod
    def close_app(self, app_name_or_hwnd: str) -> AutomationResult:
        pass

    @abstractmethod
    def find_window(self, title_query: str) -> Optional[WindowInfo]:
        pass

    @abstractmethod
    def focus_window(self, window_identifier: str) -> AutomationResult:
        pass

    @abstractmethod
    def move_window(self, window_identifier: str, x: int, y: int) -> AutomationResult:
        pass

    @abstractmethod
    def resize_window(self, window_identifier: str, width: int, height: int) -> AutomationResult:
        pass

    @abstractmethod
    def type_text(self, text: str) -> AutomationResult:
        pass

    @abstractmethod
    def press_shortcut(self, keys: List[str]) -> AutomationResult:
        pass

    @abstractmethod
    def click_mouse(self, x: int, y: int, button: str = "left", clicks: int = 1) -> AutomationResult:
        pass

    @abstractmethod
    def drag_drop(self, start_x: int, start_y: int, end_x: int, end_y: int) -> AutomationResult:
        pass

    @abstractmethod
    def get_clipboard_text(self) -> str:
        pass

    @abstractmethod
    def set_clipboard_text(self, text: str) -> bool:
        pass

from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional
from windows.models import AutomationResult, ScreenResolution, WindowInfo


class BaseAutomationProvider(ABC):
    """
    Abstract Base Class for OS Automation Providers.
    """

    @property
    @abstractmethod
    def name(self) -> str:
        pass

    @abstractmethod
    def launch_app(self, app_name: str) -> AutomationResult:
        pass

    @abstractmethod
    def close_app(self, app_name: str) -> AutomationResult:
        pass

    @abstractmethod
    def focus_window(self, title: str) -> AutomationResult:
        pass

    @abstractmethod
    def type_text(self, text: str, interval: float = 0.01) -> AutomationResult:
        pass

    @abstractmethod
    def press_shortcut(self, keys: List[str]) -> AutomationResult:
        pass

    @abstractmethod
    def click(self, x: Optional[int] = None, y: Optional[int] = None, button: str = "left", clicks: int = 1) -> AutomationResult:
        pass

    @abstractmethod
    def get_resolution(self) -> ScreenResolution:
        pass

    @abstractmethod
    def list_windows(self) -> List[WindowInfo]:
        pass

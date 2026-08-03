import logging
from typing import Any, Dict, List, Optional
from windows.controller import WindowsController
from windows.models import ActionType, AutomationResult, ScreenResolution, WindowInfo

logger = logging.getLogger("AURA.Windows.Manager")


class WindowsAutomationManager:
    """
    Unified Single Entry Point Facade for the Windows Automation Engine.
    """

    def __init__(self, controller: WindowsController = None):
        self.controller = controller if controller is not None else WindowsController()

    def launch_app(self, app_name: str) -> AutomationResult:
        """Launch an application executable or system shortcut."""
        return self.controller.execute_action(
            ActionType.LAUNCH_APP,
            {"app_name": app_name},
            lambda: self.controller.applications.launch_app(app_name)
        )

    def close_app(self, app_name: str) -> AutomationResult:
        """Close running processes matching app_name."""
        return self.controller.execute_action(
            ActionType.CLOSE_APP,
            {"app_name": app_name},
            lambda: self.controller.applications.close_app(app_name)
        )

    def focus_window(self, title: str) -> AutomationResult:
        """Focus window by title."""
        return self.controller.execute_action(
            ActionType.FOCUS_WINDOW,
            {"title": title},
            lambda: self.controller.windows.focus_window(title)
        )

    def type_text(self, text: str, interval: float = 0.01) -> AutomationResult:
        """Type text into active focused element."""
        return self.controller.execute_action(
            ActionType.TYPE_TEXT,
            {"text": text, "interval": interval},
            lambda: self.controller.keyboard.type_text(text, interval=interval)
        )

    def press_shortcut(self, keys: List[str]) -> AutomationResult:
        """Execute shortcut key combination (e.g. ['ctrl', 'c'])."""
        return self.controller.execute_action(
            ActionType.HOTKEY,
            {"keys": keys},
            lambda: self.controller.keyboard.press_shortcut(keys)
        )

    def mouse_click(self, x: Optional[int] = None, y: Optional[int] = None, button: str = "left", clicks: int = 1) -> AutomationResult:
        """Perform a mouse click."""
        return self.controller.execute_action(
            ActionType.CLICK,
            {"x": x, "y": y, "button": button, "clicks": clicks},
            lambda: self.controller.mouse.click(x=x, y=y, button=button)
        )

    def clipboard_read(self) -> AutomationResult:
        """Read text from clipboard."""
        return self.controller.execute_action(
            ActionType.CLIPBOARD_READ,
            {},
            lambda: self.controller.clipboard.read_text()
        )

    def clipboard_write(self, text: str) -> AutomationResult:
        """Copy text to clipboard."""
        return self.controller.execute_action(
            ActionType.CLIPBOARD_WRITE,
            {"text": text},
            lambda: self.controller.clipboard.write_text(text)
        )

    def take_screenshot(self, output_path: str = "screenshot.png") -> AutomationResult:
        """Capture screenshot to disk."""
        return self.controller.execute_action(
            ActionType.SCREENSHOT,
            {"output_path": output_path},
            lambda: self.controller.screenshots.capture_screen(output_path)
        )

    def get_screen_resolution(self) -> ScreenResolution:
        """Get monitor resolution."""
        return self.controller.monitor.get_screen_resolution()

    def list_running_apps(self) -> List[str]:
        """List active process names."""
        return self.controller.applications.list_running_applications()

    def list_windows(self) -> List[WindowInfo]:
        """List open window objects."""
        return self.controller.windows.enumerate_windows()

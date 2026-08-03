import logging
from typing import List, Optional
from computer.clipboard import ClipboardController
from computer.dialogs import DialogController
from computer.explorer import ExplorerController
from computer.keyboard import KeyboardController
from computer.models import ActionType, AutomationResult, WindowInfo
from computer.monitor import ComputerMonitor
from computer.mouse import MouseController
from computer.permissions import ComputerPermissions
from computer.providers.base_provider import BaseComputerProvider
from computer.providers.win32_provider import Win32Provider
from computer.safety import SafetySystem
from computer.session import ComputerSession
from computer.window_manager import WindowManager

logger = logging.getLogger("AURA.Computer.Controller")


class ComputerController:
    """
    Master Computer Use Engine Controller orchestrating automation providers, window management,
    keyboard/mouse inputs, clipboard, explorer, dialogs, safety permissions, and session history.
    """

    def __init__(self, provider: Optional[BaseComputerProvider] = None):
        self.provider = provider if provider is not None else Win32Provider()
        self.session = ComputerSession()
        self.safety = SafetySystem()
        self.permissions = ComputerPermissions(self.safety)
        self.monitor = ComputerMonitor()

        self.window = WindowManager(self.provider)
        self.keyboard = KeyboardController(self.provider)
        self.mouse = MouseController(self.provider)
        self.clipboard = ClipboardController(self.provider)
        self.explorer = ExplorerController()
        self.dialogs = DialogController()

    def launch_app(self, app_name_or_path: str) -> AutomationResult:
        if not self.permissions.validate_permission(ActionType.OPEN_APP, app_name_or_path):
            return AutomationResult(success=False, action="launch_app", message="Action blocked by security policy")
        res = self.provider.launch_app(app_name_or_path)
        self.monitor.record_result(res)
        self.session.record_action(res)
        return res

    def close_app(self, app_name_or_hwnd: str) -> AutomationResult:
        if not self.permissions.validate_permission(ActionType.CLOSE_APP, str(app_name_or_hwnd)):
            return AutomationResult(success=False, action="close_app", message="Action blocked by security policy")
        res = self.provider.close_app(app_name_or_hwnd)
        self.monitor.record_result(res)
        self.session.record_action(res)
        return res

    def type_text(self, text: str) -> AutomationResult:
        if not self.permissions.validate_permission(ActionType.TYPE_TEXT, text[:20]):
            return AutomationResult(success=False, action="type_text", message="Action blocked by security policy")
        res = self.keyboard.type_text(text)
        self.monitor.record_result(res)
        self.session.record_action(res)
        return res

    def press_shortcut(self, keys: List[str]) -> AutomationResult:
        res = self.keyboard.press_shortcut(keys)
        self.monitor.record_result(res)
        self.session.record_action(res)
        return res

    def click_mouse(self, x: int, y: int, button: str = "left", clicks: int = 1) -> AutomationResult:
        res = self.mouse.click(x, y, button=button, clicks=clicks)
        self.monitor.record_result(res)
        self.session.record_action(res)
        return res

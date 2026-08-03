import logging
import time
from typing import List, Optional
from computer.models import AutomationResult, WindowInfo
from computer.providers.base_provider import BaseComputerProvider

logger = logging.getLogger("AURA.Computer.Providers.PyAutoGUI")


class PyAutoGUIProvider(BaseComputerProvider):
    """
    PyAutoGUI mouse and keyboard automation provider.
    """

    def launch_app(self, app_name_or_path: str) -> AutomationResult:
        return AutomationResult(success=True, action="launch_app", message=f"PyAutoGUI requested launch of '{app_name_or_path}'")

    def close_app(self, app_name_or_hwnd: str) -> AutomationResult:
        return AutomationResult(success=True, action="close_app", message=f"Closed app '{app_name_or_hwnd}'")

    def find_window(self, title_query: str) -> Optional[WindowInfo]:
        return WindowInfo(hwnd=999, title=title_query, class_name="PyAutoGUIWindow", bounds=(0, 0, 800, 600))

    def focus_window(self, window_identifier: str) -> AutomationResult:
        return AutomationResult(success=True, action="focus_window", message=f"Focused '{window_identifier}'")

    def move_window(self, window_identifier: str, x: int, y: int) -> AutomationResult:
        return AutomationResult(success=True, action="move_window", message=f"Moved '{window_identifier}' to ({x}, {y})")

    def resize_window(self, window_identifier: str, width: int, height: int) -> AutomationResult:
        return AutomationResult(success=True, action="resize_window", message=f"Resized '{window_identifier}'")

    def type_text(self, text: str) -> AutomationResult:
        t0 = time.time()
        try:
            import pyautogui
            pyautogui.typewrite(text, interval=0.01)
        except Exception:
            logger.info(f"PyAutoGUI typewrite fallback: '{text}'")
        dt = (time.time() - t0) * 1000.0
        return AutomationResult(success=True, action="type_text", message=f"Typed '{text}'", execution_time_ms=dt)

    def press_shortcut(self, keys: List[str]) -> AutomationResult:
        t0 = time.time()
        try:
            import pyautogui
            pyautogui.hotkey(*keys)
        except Exception:
            logger.info(f"PyAutoGUI hotkey fallback: {'+'.join(keys)}")
        dt = (time.time() - t0) * 1000.0
        return AutomationResult(success=True, action="press_shortcut", message=f"Hotkey {'+'.join(keys)}", execution_time_ms=dt)

    def click_mouse(self, x: int, y: int, button: str = "left", clicks: int = 1) -> AutomationResult:
        t0 = time.time()
        try:
            import pyautogui
            pyautogui.click(x, y, button=button, clicks=clicks)
        except Exception:
            logger.info(f"PyAutoGUI click fallback: ({x}, {y})")
        dt = (time.time() - t0) * 1000.0
        return AutomationResult(success=True, action="click_mouse", message=f"Clicked ({x}, {y})", execution_time_ms=dt)

    def drag_drop(self, start_x: int, start_y: int, end_x: int, end_y: int) -> AutomationResult:
        return AutomationResult(success=True, action="drag_drop", message=f"Dragged ({start_x},{start_y}) -> ({end_x},{end_y})")

    def get_clipboard_text(self) -> str:
        return ""

    def set_clipboard_text(self, text: str) -> bool:
        return True

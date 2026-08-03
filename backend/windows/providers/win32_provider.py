import logging
import time
from typing import Any, Dict, List, Optional
from windows.models import AutomationResult, ScreenResolution, WindowInfo
from windows.providers.base import BaseAutomationProvider

logger = logging.getLogger("AURA.Windows.Providers.Win32")


class Win32Provider(BaseAutomationProvider):
    """
    Windows Automation Provider utilizing win32gui / win32con / win32api for low-level GDI and OS operations.
    """

    @property
    def name(self) -> str:
        return "win32"

    def launch_app(self, app_name: str) -> AutomationResult:
        from windows.providers.pyautogui_provider import PyAutoGUIProvider
        return PyAutoGUIProvider().launch_app(app_name)

    def close_app(self, app_name: str) -> AutomationResult:
        from windows.providers.pyautogui_provider import PyAutoGUIProvider
        return PyAutoGUIProvider().close_app(app_name)

    def focus_window(self, title: str) -> AutomationResult:
        start_time = time.time()
        try:
            import win32gui
            import win32con

            hwnd = win32gui.FindWindow(None, title)
            if hwnd:
                win32gui.ShowWindow(hwnd, win32con.SW_RESTORE)
                win32gui.SetForegroundWindow(hwnd)
                elapsed = time.time() - start_time
                return AutomationResult(success=True, message=f"Focused window via Win32: '{title}'", execution_time=elapsed)
            
            elapsed = time.time() - start_time
            return AutomationResult(success=False, message=f"Win32 window '{title}' not found.", execution_time=elapsed)
        except Exception as e:
            elapsed = time.time() - start_time
            return AutomationResult(success=False, message=f"Win32 focus error: {e}", execution_time=elapsed)

    def type_text(self, text: str, interval: float = 0.01) -> AutomationResult:
        from windows.providers.pyautogui_provider import PyAutoGUIProvider
        return PyAutoGUIProvider().type_text(text, interval=interval)

    def press_shortcut(self, keys: List[str]) -> AutomationResult:
        from windows.providers.pyautogui_provider import PyAutoGUIProvider
        return PyAutoGUIProvider().press_shortcut(keys)

    def click(self, x: Optional[int] = None, y: Optional[int] = None, button: str = "left", clicks: int = 1) -> AutomationResult:
        from windows.providers.pyautogui_provider import PyAutoGUIProvider
        return PyAutoGUIProvider().click(x=x, y=y, button=button, clicks=clicks)

    def get_resolution(self) -> ScreenResolution:
        try:
            import win32api
            import win32con
            w = win32api.GetSystemMetrics(win32con.SM_CXSCREEN)
            h = win32api.GetSystemMetrics(win32con.SM_CYSCREEN)
            return ScreenResolution(width=w, height=h)
        except Exception:
            return ScreenResolution(width=1920, height=1080)

    def list_windows(self) -> List[WindowInfo]:
        results: List[WindowInfo] = []
        try:
            import win32gui

            def enum_windows_callback(hwnd, extra):
                if win32gui.IsWindowVisible(hwnd):
                    title = win32gui.GetWindowText(hwnd)
                    if title:
                        rect = win32gui.GetWindowRect(hwnd)
                        x, y, r, b = rect
                        results.append(WindowInfo(
                            title=title,
                            handle=hwnd,
                            bounds={"x": x, "y": y, "width": r - x, "height": b - y},
                            is_active=(hwnd == win32gui.GetForegroundWindow())
                        ))
                return True

            win32gui.EnumWindows(enum_windows_callback, None)
        except Exception as e:
            logger.debug(f"Win32 EnumWindows failed: {e}")

        return results

import logging
import subprocess
import time
from typing import Any, Dict, List, Optional
import pyautogui
from windows.models import AutomationResult, ScreenResolution, WindowInfo
from windows.providers.base import BaseAutomationProvider

logger = logging.getLogger("AURA.Windows.Providers.PyAutoGUI")

# Disable pyautogui fail-safe delay for fast programmatic execution
pyautogui.FAILSAFE = False


class PyAutoGUIProvider(BaseAutomationProvider):
    """
    GUI automation provider utilizing PyAutoGUI.
    """

    APP_MAP = {
        "chrome": r"C:\Program Files\Google\Chrome\Application\chrome.exe",
        "notepad": "notepad.exe",
        "calculator": "calc.exe",
        "calc": "calc.exe"
    }

    @property
    def name(self) -> str:
        return "pyautogui"

    def launch_app(self, app_name: str) -> AutomationResult:
        start_time = time.time()
        app_key = app_name.strip().lower()
        executable = self.APP_MAP.get(app_key, app_name)

        try:
            subprocess.Popen(executable)
            elapsed = time.time() - start_time
            return AutomationResult(
                success=True,
                message=f"{app_name.title()} opened.",
                data={"app": app_name, "executable": executable},
                execution_time=elapsed
            )
        except Exception as e:
            elapsed = time.time() - start_time
            logger.error(f"PyAutoGUI launch error: {e}")
            return AutomationResult(
                success=False,
                message=f"Failed to launch '{app_name}': {e}",
                execution_time=elapsed
            )

    def close_app(self, app_name: str) -> AutomationResult:
        start_time = time.time()
        try:
            import psutil
            closed_count = 0
            for proc in psutil.process_iter(['name', 'pid']):
                if app_name.lower() in proc.info['name'].lower():
                    proc.terminate()
                    closed_count += 1
            elapsed = time.time() - start_time
            return AutomationResult(
                success=True,
                message=f"Closed {closed_count} process(es) matching '{app_name}'.",
                execution_time=elapsed
            )
        except Exception as e:
            elapsed = time.time() - start_time
            return AutomationResult(
                success=False,
                message=f"Failed to close '{app_name}': {e}",
                execution_time=elapsed
            )

    def focus_window(self, title: str) -> AutomationResult:
        start_time = time.time()
        try:
            import pygetwindow as gw
            wins = gw.getWindowsWithTitle(title)
            if wins:
                wins[0].activate()
                elapsed = time.time() - start_time
                return AutomationResult(success=True, message=f"Focused window '{title}'", execution_time=elapsed)
            elapsed = time.time() - start_time
            return AutomationResult(success=False, message=f"Window '{title}' not found.", execution_time=elapsed)
        except Exception as e:
            elapsed = time.time() - start_time
            return AutomationResult(success=False, message=f"Focus window error: {e}", execution_time=elapsed)

    def type_text(self, text: str, interval: float = 0.01) -> AutomationResult:
        start_time = time.time()
        try:
            pyautogui.write(text, interval=interval)
            elapsed = time.time() - start_time
            return AutomationResult(success=True, message=f"Typed text: '{text[:20]}...'", execution_time=elapsed)
        except Exception as e:
            elapsed = time.time() - start_time
            return AutomationResult(success=False, message=f"Type text error: {e}", execution_time=elapsed)

    def press_shortcut(self, keys: List[str]) -> AutomationResult:
        start_time = time.time()
        try:
            pyautogui.hotkey(*keys)
            elapsed = time.time() - start_time
            return AutomationResult(success=True, message=f"Executed shortcut: {'+'.join(keys)}", execution_time=elapsed)
        except Exception as e:
            elapsed = time.time() - start_time
            return AutomationResult(success=False, message=f"Shortcut error: {e}", execution_time=elapsed)

    def click(self, x: Optional[int] = None, y: Optional[int] = None, button: str = "left", clicks: int = 1) -> AutomationResult:
        start_time = time.time()
        try:
            if x is not None and y is not None:
                pyautogui.click(x=x, y=y, button=button, clicks=clicks)
            else:
                pyautogui.click(button=button, clicks=clicks)
            elapsed = time.time() - start_time
            return AutomationResult(success=True, message=f"Mouse {button} click executed.", execution_time=elapsed)
        except Exception as e:
            elapsed = time.time() - start_time
            return AutomationResult(success=False, message=f"Mouse click error: {e}", execution_time=elapsed)

    def get_resolution(self) -> ScreenResolution:
        w, h = pyautogui.size()
        return ScreenResolution(width=w, height=h)

    def list_windows(self) -> List[WindowInfo]:
        results: List[WindowInfo] = []
        try:
            import pygetwindow as gw
            for w in gw.getAllWindows():
                if w.title:
                    results.append(WindowInfo(
                        title=w.title,
                        bounds={"x": w.left, "y": w.top, "width": w.width, "height": w.height},
                        is_active=w.isActive
                    ))
        except Exception as e:
            logger.debug(f"Failed to list windows via pygetwindow: {e}")
        return results

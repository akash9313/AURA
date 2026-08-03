import logging
from typing import List
from windows.models import AutomationResult
from windows.providers.pyautogui_provider import PyAutoGUIProvider

logger = logging.getLogger("AURA.Windows.Applications")


class ApplicationManager:
    """
    Manager responsible for launching, closing, and listing Windows applications.
    """

    def __init__(self, provider=None):
        self.provider = provider if provider is not None else PyAutoGUIProvider()

    def launch_app(self, app_name: str) -> AutomationResult:
        """Launch an application executable or shortcut."""
        logger.info(f"Launching application: '{app_name}'")
        return self.provider.launch_app(app_name)

    def close_app(self, app_name: str) -> AutomationResult:
        """Terminate processes matching app_name."""
        logger.info(f"Closing application: '{app_name}'")
        return self.provider.close_app(app_name)

    def list_running_applications(self) -> List[str]:
        """Return list of distinct active process names."""
        running = set()
        try:
            import psutil
            for proc in psutil.process_iter(['name']):
                if proc.info['name']:
                    running.add(proc.info['name'])
        except Exception as e:
            logger.warning(f"Failed to list running processes: {e}")
        return sorted(list(running))

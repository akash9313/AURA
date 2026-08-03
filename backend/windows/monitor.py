import logging
from windows.models import ScreenResolution
from windows.providers.pyautogui_provider import PyAutoGUIProvider

logger = logging.getLogger("AURA.Windows.Monitor")


class MonitorManager:
    """
    Manager responsible for screen resolution metrics and display monitors.
    """

    def __init__(self, provider=None):
        self.provider = provider if provider is not None else PyAutoGUIProvider()

    def get_screen_resolution(self) -> ScreenResolution:
        """Get primary monitor dimensions."""
        return self.provider.get_resolution()

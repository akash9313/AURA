import logging
import time
from typing import List, Optional
from computer.models import AutomationResult, WindowInfo

logger = logging.getLogger("AURA.Computer.Session")


class ComputerSession:
    """
    State manager tracking active desktop automation session history and focused window.
    """

    def __init__(self):
        self.session_id: str = f"session_{int(time.time())}"
        self.active_window: Optional[WindowInfo] = None
        self.action_history: List[AutomationResult] = []

    def record_action(self, result: AutomationResult) -> None:
        self.action_history.append(result)

    def set_active_window(self, window: WindowInfo) -> None:
        self.active_window = window
        logger.info(f"Active session window set: '{window.title}' (HWND: {window.hwnd})")

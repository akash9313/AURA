import logging
from core.events import Event
from core.service import Service
from windows.manager import WindowsAutomationManager

logger = logging.getLogger("AURA.WindowsService")


class WindowsService(Service):
    """
    WindowsService connects the WindowsAutomationManager to the AURA EventBus.
    """

    def __init__(self, bus, manager: WindowsAutomationManager = None):
        super().__init__(bus)
        self.manager = manager if manager is not None else WindowsAutomationManager()

    def start(self) -> None:
        logger.info("Windows Automation Service Started")

    def stop(self) -> None:
        logger.info("Windows Automation Service Stopped")

    def launch_app(self, app_name: str):
        res = self.manager.launch_app(app_name)
        if res.success:
            self.bus.publish(Event.APPLICATION_OPENED, {"app_name": app_name})
        return res

    def close_app(self, app_name: str):
        res = self.manager.close_app(app_name)
        if res.success:
            self.bus.publish(Event.APPLICATION_CLOSED, {"app_name": app_name})
        return res

    def focus_window(self, title: str):
        res = self.manager.focus_window(title)
        if res.success:
            self.bus.publish(Event.WINDOW_FOCUSED, {"title": title})
        return res

    def type_text(self, text: str):
        res = self.manager.type_text(text)
        if res.success:
            self.bus.publish(Event.TEXT_TYPED, {"text": text})
        return res

    def press_shortcut(self, keys: list):
        res = self.manager.press_shortcut(keys)
        if res.success:
            self.bus.publish(Event.SHORTCUT_EXECUTED, {"keys": keys})
        return res

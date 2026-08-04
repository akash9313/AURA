import logging
import time

from computer.applications.models import ApplicationState, AURAApplication

logger = logging.getLogger("AURA.Computer.Applications.Lifecycle")


class ApplicationLifecycleTracker:
    def set_starting(self, app: AURAApplication) -> None:
        app.status = ApplicationState.STARTING
        app.is_ready = False

    def set_running(self, app: AURAApplication) -> None:
        app.status = ApplicationState.RUNNING

    def set_ready(self, app: AURAApplication) -> None:
        app.status = ApplicationState.RUNNING
        app.is_ready = True

    def set_idle(self, app: AURAApplication) -> None:
        app.status = ApplicationState.IDLE

    def set_busy(self, app: AURAApplication) -> None:
        app.status = ApplicationState.BUSY

    def set_closed(self, app: AURAApplication) -> None:
        app.status = ApplicationState.CLOSED
        app.is_ready = False

    def set_crashed(self, app: AURAApplication) -> None:
        app.status = ApplicationState.CRASHED
        app.is_ready = False

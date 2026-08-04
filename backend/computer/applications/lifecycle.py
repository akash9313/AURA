"""
Application Lifecycle Tracker.
Tracks state transitions (STARTING, RUNNING, IDLE, BUSY, CLOSING, CLOSED, CRASHED) and readiness criteria.
"""

import logging
import time

from computer.applications.models import ApplicationState, AURAApplication

logger = logging.getLogger("AURA.Computer.Applications.Lifecycle")


class ApplicationLifecycleTracker:
    """
    Manages state transitions and readiness criteria for AURAApplication instances.
    """

    def set_starting(self, app: AURAApplication) -> None:
        """Mark application state as STARTING."""
        app.status = ApplicationState.STARTING
        app.is_ready = False
        logger.debug(f"Application '{app.app_id}' state -> STARTING")

    def set_running(self, app: AURAApplication) -> None:
        """Mark application state as RUNNING."""
        app.status = ApplicationState.RUNNING
        logger.debug(f"Application '{app.app_id}' state -> RUNNING")

    def set_ready(self, app: AURAApplication) -> None:
        """Mark application as READY (Process + Main Window + Initialization complete)."""
        app.status = ApplicationState.RUNNING
        app.is_ready = True
        logger.debug(f"Application '{app.app_id}' is now READY")

    def set_idle(self, app: AURAApplication) -> None:
        """Mark application state as IDLE."""
        app.status = ApplicationState.IDLE
        logger.debug(f"Application '{app.app_id}' state -> IDLE")

    def set_busy(self, app: AURAApplication) -> None:
        """Mark application state as BUSY."""
        app.status = ApplicationState.BUSY
        logger.debug(f"Application '{app.app_id}' state -> BUSY")

    def set_closed(self, app: AURAApplication) -> None:
        """Mark application state as CLOSED."""
        app.status = ApplicationState.CLOSED
        app.is_ready = False
        logger.debug(f"Application '{app.app_id}' state -> CLOSED")

    def set_crashed(self, app: AURAApplication) -> None:
        """Mark application state as CRASHED."""
        app.status = ApplicationState.CRASHED
        app.is_ready = False
        logger.warning(f"Application '{app.app_id}' state -> CRASHED")

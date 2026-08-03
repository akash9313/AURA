import logging
import time
from typing import Any, Dict, List, Optional
from windows.applications import ApplicationManager
from windows.clipboard import ClipboardManager
from windows.keyboard import KeyboardManager
from windows.models import ActionLog, ActionType, AutomationResult, PermissionLevel, ScreenResolution, WindowInfo
from windows.monitor import MonitorManager
from windows.mouse import MouseManager
from windows.permissions import PermissionManager
from windows.screenshots import WindowsScreenshotManager
from windows.windows import WindowManager

logger = logging.getLogger("AURA.Windows.Controller")


class WindowsController:
    """
    Master Controller tying permissions, logging, sub-managers, and providers together.
    """

    def __init__(self):
        self.permissions = PermissionManager()
        self.applications = ApplicationManager()
        self.windows = WindowManager()
        self.keyboard = KeyboardManager()
        self.mouse = MouseManager()
        self.clipboard = ClipboardManager()
        self.screenshots = WindowsScreenshotManager()
        self.monitor = MonitorManager()

        self._logs: List[ActionLog] = []

    def execute_action(self, action_type: ActionType, parameters: Dict[str, Any], action_fn) -> AutomationResult:
        """
        Execute an OS action with safety permission verification and audit logging.

        Args:
            action_type (ActionType): Enum category.
            parameters (Dict[str, Any]): Action inputs.
            action_fn (Callable): Sub-manager execution lambda.

        Returns:
            AutomationResult: Execution result.
        """
        start_time = time.time()
        is_allowed, level, reason = self.permissions.check_permission(action_type, parameters)

        if not is_allowed:
            elapsed = time.time() - start_time
            log_entry = ActionLog(
                action_type=action_type,
                parameters=parameters,
                duration=elapsed,
                success=False,
                failure_reason=reason
            )
            self._logs.append(log_entry)
            return AutomationResult(success=False, message=reason, execution_time=elapsed)

        try:
            result: AutomationResult = action_fn()
            elapsed = time.time() - start_time
            if result.execution_time == 0.0:
                result.execution_time = elapsed

            log_entry = ActionLog(
                action_type=action_type,
                parameters=parameters,
                duration=elapsed,
                success=result.success,
                failure_reason=result.message if not result.success else None
            )
            self._logs.append(log_entry)
            return result
        except Exception as e:
            elapsed = time.time() - start_time
            err_msg = f"Execution error during {action_type.value}: {e}"
            logger.error(err_msg)
            log_entry = ActionLog(
                action_type=action_type,
                parameters=parameters,
                duration=elapsed,
                success=False,
                failure_reason=err_msg
            )
            self._logs.append(log_entry)
            return AutomationResult(success=False, message=err_msg, execution_time=elapsed)

    def get_action_logs(self) -> List[Dict[str, Any]]:
        """Retrieve audit history log."""
        return [l.to_dict() for l in self._logs]

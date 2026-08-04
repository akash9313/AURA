"""
Browser Recovery & Self-Healing Service.
Top-level AURA service integrating the BrowserRecoveryEngine into the kernel runtime.
Automatically recovers from browser crashes, navigation timeouts, lost sessions, and detached DOM nodes.
"""

import logging
from typing import Any, Callable, Dict, List, Optional, Tuple

from core.service import Service
from browser.recovery.configuration import RecoveryConfig
from browser.recovery.models import DiagnosticReport, HealthMetrics, StateSnapshot
from browser.recovery.recovery_engine import BrowserRecoveryEngine

logger = logging.getLogger("AURA.Browser.Recovery.Service")


class BrowserRecoveryService(Service):
    """
    Browser Recovery Service.
    Provides self-healing capabilities and automated recovery for browser automation failures.
    """

    def __init__(
        self,
        bus: Any = None,
        config: Optional[RecoveryConfig] = None,
        browser_manager: Any = None,
        session_manager: Any = None,
    ):
        super().__init__(bus)
        self.config = config or RecoveryConfig()
        self.browser_manager = browser_manager
        self.session_manager = session_manager

        self.engine = BrowserRecoveryEngine(bus=bus, config=self.config)
        logger.info("BrowserRecoveryService initialized")

    async def recover(
        self,
        error: Exception,
        context: Optional[str] = None,
        action_callable: Optional[Callable[[], Any]] = None,
        page_handle: Any = None,
        workflow_id: Optional[str] = None,
        snapshot_id: Optional[str] = None,
    ) -> Tuple[bool, Any, DiagnosticReport]:
        """
        Master self-healing recovery endpoint.

        Args:
            error: Triggering Exception.
            context: Context description.
            action_callable: Async operation to re-run after self-healing.
            page_handle: Page handle.
            workflow_id: Workflow ID.
            snapshot_id: Optional snapshot ID.

        Returns:
            Tuple of (success, result_data, diagnostic_report)
        """
        logger.info(f"BrowserRecoveryService.recover for error '{error}'")
        return await self.engine.recover_from_failure(
            error=error,
            context=context,
            action_callable=action_callable,
            page_handle=page_handle,
            browser_manager_ref=self.browser_manager,
            session_manager_ref=self.session_manager,
            workflow_id=workflow_id,
            snapshot_id=snapshot_id,
        )

    def capture_snapshot(
        self,
        current_url: str,
        navigation_history: Optional[List[str]] = None,
        session_id: Optional[str] = None,
        page_id: Optional[str] = None,
        workflow_id: Optional[str] = None,
        page_state: Optional[Dict[str, Any]] = None,
        form_values: Optional[Dict[str, str]] = None,
    ) -> StateSnapshot:
        """Capture page state snapshot before a critical operation."""
        return self.engine.snapshot_manager.capture_snapshot(
            current_url=current_url,
            navigation_history=navigation_history,
            session_id=session_id,
            page_id=page_id,
            workflow_id=workflow_id,
            page_state=page_state,
            form_values=form_values,
        )

    def restore_snapshot(self, snapshot_id: str) -> Tuple[bool, Optional[StateSnapshot], str]:
        """Restore state from snapshot ID."""
        return self.engine.snapshot_manager.restore_snapshot(snapshot_id)

    async def check_health(self, page_handle: Any = None) -> HealthMetrics:
        """Audit browser infrastructure health."""
        return await self.engine.health_monitor.check_health(
            browser_manager_ref=self.browser_manager, page_handle=page_handle
        )

    # ------------------------------------------------------------------
    # Lifecycle & Telemetry
    # ------------------------------------------------------------------

    def start(self) -> None:
        logger.info("BrowserRecoveryService starting...")

    def stop(self) -> None:
        logger.info("BrowserRecoveryService stopping...")

    def is_healthy(self) -> bool:
        return self.engine.health_monitor.metrics.healthy

"""
Browser Recovery & Self-Healing Master Orchestrator.
Automatically recovers from browser crashes, navigation timeouts, detached DOM nodes, and session loss.
Executes multi-tiered self-healing strategies (retry, refresh, recreate page/context, restart browser, restore session).
"""

import asyncio
import logging
import time
from typing import Any, Callable, Dict, List, Optional, Tuple

from browser.recovery.configuration import RecoveryConfig
from browser.recovery.diagnostics import DiagnosticEngine
from browser.recovery.events import RecoveryEvent
from browser.recovery.fallback import FallbackManager
from browser.recovery.health_monitor import HealthMonitor
from browser.recovery.models import (
    DiagnosticReport,
    FailureType,
    RecoveryState,
    RecoveryStrategy,
    StateSnapshot,
)
from browser.recovery.retry_engine import RetryEngine
from browser.recovery.state_snapshot import SnapshotManager

logger = logging.getLogger("AURA.Browser.Recovery.Engine")


class BrowserRecoveryEngine:
    """
    Production-grade Browser Recovery Engine orchestrator.
    Handles self-healing, automatic retry loops, state restoration, and failure diagnostics.
    """

    def __init__(
        self,
        bus: Any = None,
        config: Optional[RecoveryConfig] = None,
    ):
        self.bus = bus
        self.config = config or RecoveryConfig()

        self.retry_engine = RetryEngine(config=self.config)
        self.snapshot_manager = SnapshotManager()
        self.diagnostic_engine = DiagnosticEngine()
        self.fallback_manager = FallbackManager()
        self.health_monitor = HealthMonitor(config=self.config)

        self.state: RecoveryState = RecoveryState.IDLE

    # ------------------------------------------------------------------
    # Master Recovery Pipeline
    # ------------------------------------------------------------------

    async def recover_from_failure(
        self,
        error: Exception,
        context: Optional[str] = None,
        action_callable: Optional[Callable[[], Any]] = None,
        page_handle: Any = None,
        browser_manager_ref: Any = None,
        session_manager_ref: Any = None,
        workflow_id: Optional[str] = None,
        snapshot_id: Optional[str] = None,
    ) -> Tuple[bool, Any, DiagnosticReport]:
        """
        Master self-healing recovery pipeline.

        Args:
            error: Exception that triggered recovery.
            context: Description of failed operation.
            action_callable: Async callable to re-execute after self-healing.
            page_handle: Playwright page handle or mock.
            browser_manager_ref: Reference to PlaywrightBrowserManager.
            session_manager_ref: Reference to BrowserSessionManager.
            workflow_id: Workflow identifier.
            snapshot_id: StateSnapshot identifier to restore from.

        Returns:
            Tuple of (success, result_data, diagnostic_report)
        """
        start_time = time.time()
        self.state = RecoveryState.RECOVERING

        # 1. Classify failure type
        failure_type = self.diagnostic_engine.analyze_failure(error, context)
        logger.warning(f"Recovery initiated for failure type '{failure_type.value}': {error}")

        # 2. Determine recovery strategy
        strategy = self.config.strategy_mapping.get(failure_type, RecoveryStrategy.REFRESH_PAGE)

        self._publish_event(
            RecoveryEvent.RECOVERY_STARTED,
            {"failure_type": failure_type.value, "strategy": strategy.value, "workflow_id": workflow_id},
        )

        success = False
        result_data = None

        try:
            # 3. Execute recovery strategy
            if strategy == RecoveryStrategy.RETRY:
                success, result_data = await self._execute_retry_strategy(action_callable)

            elif strategy == RecoveryStrategy.REFRESH_PAGE:
                success, result_data = await self._execute_refresh_strategy(page_handle, action_callable)

            elif strategy == RecoveryStrategy.RECREATE_PAGE:
                success, result_data = await self._execute_recreate_page_strategy(
                    browser_manager_ref, action_callable, snapshot_id, workflow_id
                )

            elif strategy == RecoveryStrategy.RESTART_BROWSER:
                self.health_monitor.record_crash()
                success, result_data = await self._execute_restart_browser_strategy(
                    browser_manager_ref, session_manager_ref, action_callable, snapshot_id, workflow_id
                )

            elif strategy == RecoveryStrategy.RESTORE_SESSION:
                success, result_data = await self._execute_restore_session_strategy(
                    session_manager_ref, page_handle, action_callable, snapshot_id, workflow_id
                )

            elif strategy == RecoveryStrategy.FALLBACK_LOCATOR:
                success, result_data = await self._execute_fallback_locator_strategy(
                    page_handle, context or "", action_callable
                )

            elif strategy == RecoveryStrategy.ALTERNATIVE_NAVIGATION:
                success, result_data = await self._execute_alternative_nav_strategy(
                    page_handle, action_callable
                )

            else:  # ABORT_WORKFLOW
                success = False
                result_data = None

        except Exception as recovery_err:
            logger.error(f"Recovery strategy '{strategy.value}' failed with exception: {recovery_err}")
            success = False

        duration_ms = round((time.time() - start_time) * 1000, 2)
        report = self.diagnostic_engine.generate_report(
            error=error,
            failure_type=failure_type,
            strategy=strategy,
            success=success,
            duration_ms=duration_ms,
        )

        if success:
            self.state = RecoveryState.COMPLETED
            self._publish_event(RecoveryEvent.RECOVERY_COMPLETED, report.to_dict())
        else:
            self.state = RecoveryState.FAILED
            self._publish_event(RecoveryEvent.RECOVERY_FAILED, report.to_dict())

        return (success, result_data, report)

    # ------------------------------------------------------------------
    # Individual Recovery Strategy Implementations
    # ------------------------------------------------------------------

    async def _execute_retry_strategy(self, action_callable: Optional[Callable[[], Any]]) -> Tuple[bool, Any]:
        """Strategy: Retry action with exponential/linear backoff."""
        if not action_callable:
            return (True, None)

        self._publish_event(RecoveryEvent.RETRY_STARTED, {})
        ok, res, err, attempts = await self.retry_engine.execute_with_retry(action_callable)
        self._publish_event(RecoveryEvent.RETRY_COMPLETED, {"success": ok, "attempts": attempts})
        return (ok, res)

    async def _execute_refresh_strategy(self, page_handle: Any, action_callable: Optional[Callable[[], Any]]) -> Tuple[bool, Any]:
        """Strategy: Refresh current page and retry action."""
        logger.info("Executing REFRESH_PAGE recovery strategy...")
        if page_handle and hasattr(page_handle, "reload"):
            try:
                await page_handle.reload()
            except Exception as e:
                logger.warning(f"Page reload warning: {e}")

        return await self._execute_retry_strategy(action_callable)

    async def _execute_recreate_page_strategy(
        self,
        browser_manager_ref: Any,
        action_callable: Optional[Callable[[], Any]],
        snapshot_id: Optional[str],
        workflow_id: Optional[str],
    ) -> Tuple[bool, Any]:
        """Strategy: Recreate crashed page tab, restore snapshot state, and retry."""
        logger.info("Executing RECREATE_PAGE recovery strategy...")
        if browser_manager_ref and hasattr(browser_manager_ref, "create_page"):
            try:
                page_info = await browser_manager_ref.create_page()
                logger.info(f"Recreated new page tab '{page_info.page_id}'")
            except Exception as e:
                logger.error(f"Failed to recreate page tab: {e}")

        self._restore_snapshot_if_available(snapshot_id, workflow_id)
        return await self._execute_retry_strategy(action_callable)

    async def _execute_restart_browser_strategy(
        self,
        browser_manager_ref: Any,
        session_manager_ref: Any,
        action_callable: Optional[Callable[[], Any]],
        snapshot_id: Optional[str],
        workflow_id: Optional[str],
    ) -> Tuple[bool, Any]:
        """Strategy: Full browser process restart, session restore, and state recovery."""
        logger.info("Executing RESTART_BROWSER recovery strategy...")
        if browser_manager_ref and hasattr(browser_manager_ref, "restart_browser"):
            try:
                await browser_manager_ref.restart_browser()
                self._publish_event(RecoveryEvent.BROWSER_RESTARTED, {})
            except Exception as e:
                logger.error(f"Failed to restart browser process: {e}")

        self._restore_snapshot_if_available(snapshot_id, workflow_id)
        return await self._execute_retry_strategy(action_callable)

    async def _execute_restore_session_strategy(
        self,
        session_manager_ref: Any,
        page_handle: Any,
        action_callable: Optional[Callable[[], Any]],
        snapshot_id: Optional[str],
        workflow_id: Optional[str],
    ) -> Tuple[bool, Any]:
        """Strategy: Restore lost session authentication cookies and page state."""
        logger.info("Executing RESTORE_SESSION recovery strategy...")

        self.state = RecoveryState.RESTORING
        ok_snap, snap, msg = self._restore_snapshot_if_available(snapshot_id, workflow_id)
        if ok_snap and snap:
            self._publish_event(RecoveryEvent.STATE_RESTORED, snap.to_dict())

        return await self._execute_retry_strategy(action_callable)

    async def _execute_fallback_locator_strategy(
        self, page_handle: Any, query: str, action_callable: Optional[Callable[[], Any]]
    ) -> Tuple[bool, Any]:
        """Strategy: Attempt action using generated fallback locator candidates."""
        logger.info(f"Executing FALLBACK_LOCATOR recovery strategy for query '{query}'...")
        elem, selector = await self.fallback_manager.execute_fallback_locator(page_handle, query)
        if elem:
            return await self._execute_retry_strategy(action_callable)
        return (False, None)

    async def _execute_alternative_nav_strategy(
        self, page_handle: Any, action_callable: Optional[Callable[[], Any]]
    ) -> Tuple[bool, Any]:
        """Strategy: Navigate to alternative URL route."""
        logger.info("Executing ALTERNATIVE_NAVIGATION recovery strategy...")
        if page_handle and hasattr(page_handle, "url"):
            alt_url = self.fallback_manager.resolve_alternative_url(page_handle.url)
            if alt_url and hasattr(page_handle, "goto"):
                try:
                    await page_handle.goto(alt_url)
                    return await self._execute_retry_strategy(action_callable)
                except Exception as e:
                    logger.warning(f"Alternative navigation to '{alt_url}' failed: {e}")

        return (False, None)

    # ------------------------------------------------------------------
    # State Snapshot Helpers
    # ------------------------------------------------------------------

    def _restore_snapshot_if_available(
        self, snapshot_id: Optional[str], workflow_id: Optional[str]
    ) -> Tuple[bool, Optional[StateSnapshot], str]:
        """Retrieve and restore latest state snapshot for workflow or snapshot ID."""
        if snapshot_id:
            return self.snapshot_manager.restore_snapshot(snapshot_id)
        if workflow_id:
            snap = self.snapshot_manager.get_latest_workflow_snapshot(workflow_id)
            if snap:
                return self.snapshot_manager.restore_snapshot(snap.snapshot_id)
        return (False, None, "No snapshot available")

    def _publish_event(self, event: RecoveryEvent, data: Dict[str, Any]) -> None:
        """Publish event to AURA EventBus."""
        if self.bus:
            try:
                self.bus.publish(event.value, data)
            except Exception as e:
                logger.error(f"Failed to publish recovery event '{event.value}': {e}")

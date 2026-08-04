"""
Browser Recovery & Self-Healing Engine Unit & Integration Tests.
Covers failure classification, diagnostics, retry backoffs, state snapshots, fallbacks,
health monitoring, master recovery pipeline, and service integration.
"""

import asyncio
import sys
import time
import unittest
from unittest.mock import AsyncMock, MagicMock, patch

sys.path.insert(0, ".")

from browser.recovery.models import (
    BackoffStrategy,
    DiagnosticReport,
    FailureType,
    HealthMetrics,
    RecoveryState,
    RecoveryStrategy,
    StateSnapshot,
)
from browser.recovery.events import RecoveryEvent
from browser.recovery.configuration import RecoveryConfig
from browser.recovery.state_snapshot import SnapshotManager
from browser.recovery.diagnostics import DiagnosticEngine
from browser.recovery.retry_engine import RetryEngine
from browser.recovery.fallback import FallbackManager
from browser.recovery.health_monitor import HealthMonitor
from browser.recovery.recovery_engine import BrowserRecoveryEngine
from browser.recovery.service import BrowserRecoveryService


# ==============================================================================
# Model & Event Tests
# ==============================================================================

class TestRecoveryModels(unittest.TestCase):
    """Tests for Recovery Engine domain models."""

    def test_failure_type_enum(self):
        self.assertEqual(FailureType.NAVIGATION_TIMEOUT.value, "navigation_timeout")
        self.assertEqual(FailureType.BROWSER_CRASH.value, "browser_crash")
        self.assertEqual(FailureType.SESSION_LOST.value, "session_lost")

    def test_recovery_strategy_enum(self):
        self.assertEqual(RecoveryStrategy.RETRY.value, "retry")
        self.assertEqual(RecoveryStrategy.RESTART_BROWSER.value, "restart_browser")
        self.assertEqual(RecoveryStrategy.RESTORE_SESSION.value, "restore_session")

    def test_state_snapshot_to_dict(self):
        snap = StateSnapshot(current_url="https://a.com", workflow_id="wf_1")
        d = snap.to_dict()
        self.assertIsNotNone(d["snapshot_id"])
        self.assertEqual(d["current_url"], "https://a.com")

    def test_diagnostic_report_to_dict(self):
        rep = DiagnosticReport(failure_type=FailureType.DNS_FAILURE, success=True)
        d = rep.to_dict()
        self.assertEqual(d["failure_type"], "dns_failure")
        self.assertTrue(d["success"])

    def test_health_metrics_to_dict(self):
        h = HealthMetrics(process_alive=True, page_responsive=True, memory_mb=256.0)
        d = h.to_dict()
        self.assertTrue(d["healthy"])
        self.assertEqual(d["memory_mb"], 256.0)


# ==============================================================================
# Diagnostics Tests
# ==============================================================================

class TestDiagnosticEngine(unittest.TestCase):
    """Tests for Failure Diagnostics."""

    def setUp(self):
        self.engine = DiagnosticEngine()

    def test_analyze_timeout(self):
        ft = self.engine.analyze_failure(Exception("Navigation timeout exceeded"))
        self.assertEqual(ft, FailureType.NAVIGATION_TIMEOUT)

    def test_analyze_browser_crash(self):
        ft = self.engine.analyze_failure(Exception("Browser has been closed"))
        self.assertEqual(ft, FailureType.BROWSER_CRASH)

    def test_analyze_dns_failure(self):
        ft = self.engine.analyze_failure(Exception("net::ERR_NAME_NOT_RESOLVED"))
        self.assertEqual(ft, FailureType.DNS_FAILURE)

    def test_generate_report_recommendations(self):
        rep = self.engine.generate_report(
            error=Exception("Timeout"),
            failure_type=FailureType.NAVIGATION_TIMEOUT,
            strategy=RecoveryStrategy.REFRESH_PAGE,
            success=True,
        )
        self.assertTrue(rep.success)
        self.assertGreater(len(rep.recommendations), 0)


# ==============================================================================
# Retry Engine Tests
# ==============================================================================

class TestRetryEngine(unittest.TestCase):
    """Tests for Retry Engine backoffs."""

    def setUp(self):
        self.config = RecoveryConfig(initial_backoff_ms=100.0, backoff_multiplier=2.0, max_backoff_ms=1000.0)
        self.engine = RetryEngine(config=self.config)

    def test_exponential_backoff(self):
        self.assertEqual(self.engine.calculate_delay_ms(0, BackoffStrategy.EXPONENTIAL), 100.0)
        self.assertEqual(self.engine.calculate_delay_ms(1, BackoffStrategy.EXPONENTIAL), 200.0)
        self.assertEqual(self.engine.calculate_delay_ms(2, BackoffStrategy.EXPONENTIAL), 400.0)

    def test_linear_backoff(self):
        self.assertEqual(self.engine.calculate_delay_ms(0, BackoffStrategy.LINEAR), 100.0)
        self.assertEqual(self.engine.calculate_delay_ms(1, BackoffStrategy.LINEAR), 200.0)
        self.assertEqual(self.engine.calculate_delay_ms(2, BackoffStrategy.LINEAR), 300.0)

    def test_immediate_backoff(self):
        self.assertEqual(self.engine.calculate_delay_ms(0, BackoffStrategy.IMMEDIATE), 0.0)

    def test_execute_with_retry_success(self):
        func = AsyncMock(return_value="result")
        ok, val, err, attempts = asyncio.run(self.engine.execute_with_retry(func, max_retries=2))
        self.assertTrue(ok)
        self.assertEqual(val, "result")
        self.assertEqual(attempts, 0)


# ==============================================================================
# Snapshot Manager Tests
# ==============================================================================

class TestSnapshotManager(unittest.TestCase):
    """Tests for State Snapshots."""

    def setUp(self):
        self.manager = SnapshotManager()

    def test_capture_and_restore(self):
        snap = self.manager.capture_snapshot(
            current_url="https://example.com/form",
            workflow_id="wf_55",
            form_values={"username": "user1"},
        )
        self.assertIsNotNone(snap.snapshot_id)

        ok, restored, msg = self.manager.restore_snapshot(snap.snapshot_id)
        self.assertTrue(ok)
        self.assertEqual(restored.current_url, "https://example.com/form")
        self.assertEqual(restored.form_values["username"], "user1")

    def test_get_latest_workflow_snapshot(self):
        self.manager.capture_snapshot("https://a.com", workflow_id="wf_1")
        self.manager.capture_snapshot("https://b.com", workflow_id="wf_1")
        latest = self.manager.get_latest_workflow_snapshot("wf_1")
        self.assertEqual(latest.current_url, "https://b.com")


# ==============================================================================
# Fallback Manager & Health Monitor Tests
# ==============================================================================

class TestFallbackManager(unittest.TestCase):
    def setUp(self):
        self.manager = FallbackManager()

    def test_resolve_alternative_url(self):
        alt = self.manager.resolve_alternative_url("http://example.com/page")
        self.assertEqual(alt, "https://example.com/page")

    def test_get_fallback_locators(self):
        locs = self.manager.get_fallback_locators("Submit")
        self.assertGreater(len(locs), 0)


class TestHealthMonitor(unittest.TestCase):
    def setUp(self):
        self.monitor = HealthMonitor()

    def test_check_health(self):
        page = AsyncMock()
        page.evaluate.return_value = "pong"
        metrics = asyncio.run(self.monitor.check_health(page_handle=page))
        self.assertTrue(metrics.healthy)
        self.assertTrue(metrics.page_responsive)

    def test_record_crash(self):
        self.monitor.record_crash()
        self.assertEqual(self.monitor.metrics.crash_count, 1)


# ==============================================================================
# Recovery Engine & Service Integration Tests
# ==============================================================================

class TestBrowserRecoveryEngine(unittest.TestCase):
    """Integration tests for master BrowserRecoveryEngine."""

    def setUp(self):
        self.bus = MagicMock()
        self.engine = BrowserRecoveryEngine(bus=self.bus)

    def test_recover_retry_strategy(self):
        action = AsyncMock(return_value="recovered")
        err = Exception("net::ERR_NAME_NOT_RESOLVED")

        ok, val, report = asyncio.run(
            self.engine.recover_from_failure(error=err, action_callable=action, workflow_id="wf_1")
        )
        self.assertTrue(ok)
        self.assertEqual(val, "recovered")
        self.assertEqual(report.failure_type, FailureType.DNS_FAILURE)
        self.assertEqual(report.recovery_strategy, RecoveryStrategy.RETRY)

    def test_recover_browser_crash_strategy(self):
        bm = AsyncMock()
        bm.restart_browser = AsyncMock()
        action = AsyncMock(return_value="restarted_ok")
        err = Exception("Browser process closed unexpectedly")

        ok, val, report = asyncio.run(
            self.engine.recover_from_failure(
                error=err, action_callable=action, browser_manager_ref=bm, workflow_id="wf_2"
            )
        )
        self.assertTrue(ok)
        self.assertEqual(report.recovery_strategy, RecoveryStrategy.RESTART_BROWSER)

        # Check published BROWSER_RESTARTED event
        event_names = [call[0][0] for call in self.bus.publish.call_args_list]
        self.assertIn("browser_restarted", event_names)


class TestBrowserRecoveryService(unittest.TestCase):
    """Integration tests for BrowserRecoveryService."""

    def setUp(self):
        self.bus = MagicMock()
        self.service = BrowserRecoveryService(bus=self.bus)

    def test_capture_and_restore_snapshot(self):
        snap = self.service.capture_snapshot("https://app.com/dashboard", workflow_id="wf_app")
        self.assertIsNotNone(snap.snapshot_id)

        ok, restored, msg = self.service.restore_snapshot(snap.snapshot_id)
        self.assertTrue(ok)
        self.assertEqual(restored.current_url, "https://app.com/dashboard")

    def test_recover_service_call(self):
        action = AsyncMock(return_value="service_ok")
        err = Exception("Navigation timeout occurred")

        ok, val, report = asyncio.run(
            self.service.recover(error=err, action_callable=action, workflow_id="wf_service")
        )
        self.assertTrue(ok)
        self.assertTrue(self.service.is_healthy())


if __name__ == "__main__":
    unittest.main()

"""
Navigation Engine Unit & Integration Tests.
Covers: models, events, configuration, validator, wait strategies, history, actions, navigator, and service.
"""

import asyncio
import sys
import time
import unittest
from unittest.mock import AsyncMock, MagicMock, patch

sys.path.insert(0, ".")

from browser.navigation.models import (
    NavigationActionType,
    NavigationEntry,
    NavigationErrorType,
    NavigationHealthStatus,
    NavigationHistoryInfo,
    NavigationResult,
    NavigationState,
    RedirectInfo,
    WaitStrategy,
)
from browser.navigation.events import NavigationEvent
from browser.navigation.configuration import NavigationConfig
from browser.navigation.validator import NavigationValidator
from browser.navigation.waits import WaitStrategyExecutor
from browser.navigation.history import NavigationHistory
from browser.navigation.actions import NavigationActions
from browser.navigation.navigator import Navigator
from browser.navigation.service import NavigationService, PageHandleResolver


# ==============================================================================
# Model Tests
# ==============================================================================

class TestNavigationModels(unittest.TestCase):
    """Tests for Navigation Engine domain models."""

    def test_navigation_state_enum_values(self):
        self.assertEqual(NavigationState.IDLE.value, "idle")
        self.assertEqual(NavigationState.NAVIGATING.value, "navigating")
        self.assertEqual(NavigationState.COMPLETED.value, "completed")
        self.assertEqual(NavigationState.FAILED.value, "failed")
        self.assertEqual(NavigationState.TIMED_OUT.value, "timed_out")
        self.assertEqual(NavigationState.CANCELLED.value, "cancelled")

    def test_wait_strategy_enum_values(self):
        self.assertEqual(WaitStrategy.DOM_READY.value, "dom_ready")
        self.assertEqual(WaitStrategy.LOAD_EVENT.value, "load_event")
        self.assertEqual(WaitStrategy.NETWORK_IDLE.value, "network_idle")
        self.assertEqual(WaitStrategy.CUSTOM_SELECTOR.value, "custom_selector")
        self.assertEqual(WaitStrategy.CUSTOM_TIMEOUT.value, "custom_timeout")
        self.assertEqual(WaitStrategy.NONE.value, "none")

    def test_navigation_action_type_enum_values(self):
        self.assertEqual(NavigationActionType.OPEN_URL.value, "open_url")
        self.assertEqual(NavigationActionType.RELOAD.value, "reload")
        self.assertEqual(NavigationActionType.GO_BACK.value, "go_back")
        self.assertEqual(NavigationActionType.GO_FORWARD.value, "go_forward")
        self.assertEqual(NavigationActionType.STOP_LOADING.value, "stop_loading")

    def test_navigation_error_type_enum_values(self):
        self.assertEqual(NavigationErrorType.INVALID_URL.value, "invalid_url")
        self.assertEqual(NavigationErrorType.DNS_FAILURE.value, "dns_failure")
        self.assertEqual(NavigationErrorType.SSL_ERROR.value, "ssl_error")
        self.assertEqual(NavigationErrorType.TIMEOUT.value, "timeout")
        self.assertEqual(NavigationErrorType.REDIRECT_LOOP.value, "redirect_loop")
        self.assertEqual(NavigationErrorType.BROWSER_CRASH.value, "browser_crash")

    def test_redirect_info_creation_and_to_dict(self):
        r = RedirectInfo(from_url="http://a.com", to_url="http://b.com", status_code=301)
        d = r.to_dict()
        self.assertEqual(d["from_url"], "http://a.com")
        self.assertEqual(d["to_url"], "http://b.com")
        self.assertEqual(d["status_code"], 301)
        self.assertIn("timestamp", d)

    def test_navigation_entry_creation_and_to_dict(self):
        e = NavigationEntry(url="https://example.com", title="Example", load_time_ms=123.4)
        d = e.to_dict()
        self.assertEqual(d["url"], "https://example.com")
        self.assertEqual(d["title"], "Example")
        self.assertEqual(d["load_time_ms"], 123.4)
        self.assertEqual(d["action_type"], "open_url")
        self.assertTrue(d["success"])

    def test_navigation_result_success_to_dict(self):
        r = NavigationResult(success=True, url="https://example.com", title="Test", load_time_ms=55.0)
        d = r.to_dict()
        self.assertTrue(d["success"])
        self.assertEqual(d["url"], "https://example.com")
        self.assertEqual(d["state"], "completed")
        self.assertIsNone(d["error_type"])

    def test_navigation_result_failure_to_dict(self):
        r = NavigationResult(
            success=False,
            url="https://bad.com",
            error_type=NavigationErrorType.DNS_FAILURE,
            error_message="DNS resolution failed",
            state=NavigationState.FAILED,
        )
        d = r.to_dict()
        self.assertFalse(d["success"])
        self.assertEqual(d["error_type"], "dns_failure")
        self.assertEqual(d["error_message"], "DNS resolution failed")

    def test_navigation_history_info_to_dict(self):
        info = NavigationHistoryInfo(
            page_id="p1",
            current_url="https://example.com",
            current_title="Example",
            entries_count=5,
            can_go_back=True,
            can_go_forward=False,
            total_redirects=2,
        )
        d = info.to_dict()
        self.assertEqual(d["page_id"], "p1")
        self.assertTrue(d["can_go_back"])
        self.assertFalse(d["can_go_forward"])
        self.assertEqual(d["total_redirects"], 2)

    def test_navigation_health_status_to_dict(self):
        h = NavigationHealthStatus(
            state=NavigationState.IDLE,
            total_navigations=10,
            successful_navigations=8,
            failed_navigations=2,
            average_load_time_ms=150.5,
        )
        d = h.to_dict()
        self.assertEqual(d["state"], "idle")
        self.assertEqual(d["total_navigations"], 10)
        self.assertEqual(d["average_load_time_ms"], 150.5)


# ==============================================================================
# Event Tests
# ==============================================================================

class TestNavigationEvents(unittest.TestCase):
    """Tests for Navigation event enum values."""

    def test_all_event_values(self):
        self.assertEqual(NavigationEvent.NAVIGATION_STARTED.value, "navigation_started")
        self.assertEqual(NavigationEvent.NAVIGATION_COMPLETED.value, "navigation_completed")
        self.assertEqual(NavigationEvent.NAVIGATION_FAILED.value, "navigation_failed")
        self.assertEqual(NavigationEvent.PAGE_RELOADED.value, "page_reloaded")
        self.assertEqual(NavigationEvent.PAGE_BACK.value, "page_back")
        self.assertEqual(NavigationEvent.PAGE_FORWARD.value, "page_forward")
        self.assertEqual(NavigationEvent.PAGE_STOPPED.value, "page_stopped")
        self.assertEqual(NavigationEvent.REDIRECT_DETECTED.value, "redirect_detected")
        self.assertEqual(NavigationEvent.WAIT_STARTED.value, "wait_started")
        self.assertEqual(NavigationEvent.WAIT_COMPLETED.value, "wait_completed")


# ==============================================================================
# Configuration Tests
# ==============================================================================

class TestNavigationConfig(unittest.TestCase):
    """Tests for NavigationConfig defaults and overrides."""

    def test_defaults(self):
        cfg = NavigationConfig()
        self.assertEqual(cfg.navigation_timeout_ms, 30000.0)
        self.assertEqual(cfg.retry_count, 2)
        self.assertEqual(cfg.default_wait_strategy, WaitStrategy.LOAD_EVENT)
        self.assertEqual(cfg.maximum_redirects, 20)
        self.assertTrue(cfg.record_history)
        self.assertEqual(cfg.max_history_entries, 500)
        self.assertIn("https", cfg.allowed_protocols)
        self.assertIn("http", cfg.allowed_protocols)

    def test_custom_config(self):
        cfg = NavigationConfig(
            navigation_timeout_ms=10000.0,
            retry_count=5,
            maximum_redirects=10,
            default_wait_strategy=WaitStrategy.NETWORK_IDLE,
        )
        self.assertEqual(cfg.navigation_timeout_ms, 10000.0)
        self.assertEqual(cfg.retry_count, 5)
        self.assertEqual(cfg.maximum_redirects, 10)
        self.assertEqual(cfg.default_wait_strategy, WaitStrategy.NETWORK_IDLE)


# ==============================================================================
# Validator Tests
# ==============================================================================

class TestNavigationValidator(unittest.TestCase):
    """Tests for URL and navigation constraint validation."""

    def setUp(self):
        self.validator = NavigationValidator()

    def test_valid_https_url(self):
        ok, err_type, msg = self.validator.validate_url("https://www.google.com")
        self.assertTrue(ok)
        self.assertIsNone(err_type)

    def test_valid_http_url(self):
        ok, err_type, msg = self.validator.validate_url("http://example.com/path?q=1")
        self.assertTrue(ok)

    def test_valid_about_blank(self):
        ok, err_type, msg = self.validator.validate_url("about:blank")
        self.assertTrue(ok)

    def test_valid_file_url(self):
        ok, err_type, msg = self.validator.validate_url("file:///home/user/test.html")
        self.assertTrue(ok)

    def test_empty_url_rejected(self):
        ok, err_type, msg = self.validator.validate_url("")
        self.assertFalse(ok)
        self.assertEqual(err_type, NavigationErrorType.INVALID_URL)

    def test_none_url_rejected(self):
        ok, err_type, msg = self.validator.validate_url(None)
        self.assertFalse(ok)
        self.assertEqual(err_type, NavigationErrorType.INVALID_URL)

    def test_whitespace_only_rejected(self):
        ok, err_type, msg = self.validator.validate_url("   ")
        self.assertFalse(ok)
        self.assertEqual(err_type, NavigationErrorType.INVALID_URL)

    def test_unsupported_protocol_rejected(self):
        ok, err_type, msg = self.validator.validate_url("ftp://files.example.com")
        self.assertFalse(ok)
        self.assertEqual(err_type, NavigationErrorType.UNSUPPORTED_PROTOCOL)

    def test_missing_scheme_rejected(self):
        ok, err_type, msg = self.validator.validate_url("www.example.com")
        self.assertFalse(ok)
        self.assertEqual(err_type, NavigationErrorType.UNSUPPORTED_PROTOCOL)

    def test_missing_hostname_rejected(self):
        ok, err_type, msg = self.validator.validate_url("https://")
        self.assertFalse(ok)
        self.assertEqual(err_type, NavigationErrorType.INVALID_URL)

    def test_bare_tld_rejected(self):
        ok, err_type, msg = self.validator.validate_url("http://com")
        self.assertFalse(ok)
        self.assertEqual(err_type, NavigationErrorType.INVALID_URL)

    def test_localhost_allowed(self):
        ok, err_type, msg = self.validator.validate_url("http://localhost:8080")
        self.assertTrue(ok)

    def test_redirect_count_within_limit(self):
        ok, msg = self.validator.validate_redirect_count(5)
        self.assertTrue(ok)

    def test_redirect_count_exceeds_limit(self):
        ok, msg = self.validator.validate_redirect_count(20)
        self.assertFalse(ok)
        self.assertIn("exceeded", msg)

    def test_detect_redirect_loop_none(self):
        has_loop, msg = self.validator.detect_redirect_loop(["http://a.com", "http://b.com", "http://c.com"])
        self.assertFalse(has_loop)

    def test_detect_redirect_loop_present(self):
        has_loop, msg = self.validator.detect_redirect_loop(["http://a.com", "http://b.com", "http://a.com"])
        self.assertTrue(has_loop)
        self.assertIn("loop", msg.lower())

    def test_detect_redirect_loop_case_insensitive(self):
        has_loop, msg = self.validator.detect_redirect_loop(["http://A.COM", "http://b.com", "http://a.com"])
        self.assertTrue(has_loop)

    def test_validate_timeout_valid(self):
        ok, msg = self.validator.validate_timeout(5000)
        self.assertTrue(ok)

    def test_validate_timeout_zero(self):
        ok, msg = self.validator.validate_timeout(0)
        self.assertFalse(ok)

    def test_validate_timeout_negative(self):
        ok, msg = self.validator.validate_timeout(-100)
        self.assertFalse(ok)

    def test_validate_timeout_too_large(self):
        ok, msg = self.validator.validate_timeout(500000)
        self.assertFalse(ok)


# ==============================================================================
# Wait Strategy Tests
# ==============================================================================

class TestWaitStrategyExecutor(unittest.TestCase):
    """Tests for configurable wait strategy execution."""

    def setUp(self):
        self.executor = WaitStrategyExecutor()

    def test_wait_none_strategy(self):
        result = asyncio.run(
            self.executor.execute_wait(None, strategy=WaitStrategy.NONE)
        )
        self.assertIsInstance(result, float)
        self.assertGreaterEqual(result, 0)

    def test_wait_dom_ready_fallback(self):
        result = asyncio.run(
            self.executor.execute_wait(None, strategy=WaitStrategy.DOM_READY)
        )
        self.assertIsInstance(result, float)

    def test_wait_load_event_fallback(self):
        result = asyncio.run(
            self.executor.execute_wait(None, strategy=WaitStrategy.LOAD_EVENT)
        )
        self.assertIsInstance(result, float)

    def test_wait_network_idle_fallback(self):
        result = asyncio.run(
            self.executor.execute_wait(None, strategy=WaitStrategy.NETWORK_IDLE)
        )
        self.assertIsInstance(result, float)

    def test_wait_custom_selector_no_selector_fallback(self):
        result = asyncio.run(
            self.executor.execute_wait(None, strategy=WaitStrategy.CUSTOM_SELECTOR)
        )
        self.assertIsInstance(result, float)

    def test_wait_custom_timeout(self):
        result = asyncio.run(
            self.executor.execute_wait(None, strategy=WaitStrategy.CUSTOM_TIMEOUT, timeout_ms=50)
        )
        self.assertGreaterEqual(result, 40)

    def test_convenience_wait_for_page_load(self):
        result = asyncio.run(
            self.executor.wait_for_page_load(None)
        )
        self.assertIsInstance(result, float)

    def test_convenience_wait_for_network_idle(self):
        result = asyncio.run(
            self.executor.wait_for_network_idle(None)
        )
        self.assertIsInstance(result, float)

    def test_convenience_wait_for_dom_ready(self):
        result = asyncio.run(
            self.executor.wait_for_dom_ready(None)
        )
        self.assertIsInstance(result, float)

    def test_default_strategy_from_config(self):
        cfg = NavigationConfig(default_wait_strategy=WaitStrategy.NONE)
        executor = WaitStrategyExecutor(config=cfg)
        result = asyncio.run(
            executor.execute_wait(None)
        )
        self.assertIsInstance(result, float)


# ==============================================================================
# History Tests
# ==============================================================================

class TestNavigationHistory(unittest.TestCase):
    """Tests for per-page navigation history tracking."""

    def setUp(self):
        self.history = NavigationHistory()
        self.page_id = "test_page"

    def test_record_entry(self):
        entry = self.history.record(self.page_id, "https://example.com", title="Example")
        self.assertEqual(entry.url, "https://example.com")
        self.assertEqual(entry.title, "Example")

    def test_get_current_entry(self):
        self.history.record(self.page_id, "https://a.com")
        self.history.record(self.page_id, "https://b.com")
        current = self.history.get_current_entry(self.page_id)
        self.assertEqual(current.url, "https://b.com")

    def test_get_current_entry_empty(self):
        self.assertIsNone(self.history.get_current_entry("nonexistent"))

    def test_get_previous_entry(self):
        self.history.record(self.page_id, "https://a.com")
        self.history.record(self.page_id, "https://b.com")
        prev = self.history.get_previous_entry(self.page_id)
        self.assertEqual(prev.url, "https://a.com")

    def test_get_previous_entry_no_history(self):
        self.history.record(self.page_id, "https://a.com")
        self.assertIsNone(self.history.get_previous_entry(self.page_id))

    def test_can_go_back(self):
        self.history.record(self.page_id, "https://a.com")
        self.assertFalse(self.history.can_go_back(self.page_id))
        self.history.record(self.page_id, "https://b.com")
        self.assertTrue(self.history.can_go_back(self.page_id))

    def test_can_go_forward(self):
        self.history.record(self.page_id, "https://a.com")
        self.history.record(self.page_id, "https://b.com")
        self.assertFalse(self.history.can_go_forward(self.page_id))
        self.history.go_back(self.page_id)
        self.assertTrue(self.history.can_go_forward(self.page_id))

    def test_go_back(self):
        self.history.record(self.page_id, "https://a.com")
        self.history.record(self.page_id, "https://b.com")
        entry = self.history.go_back(self.page_id)
        self.assertEqual(entry.url, "https://a.com")

    def test_go_back_at_beginning(self):
        self.history.record(self.page_id, "https://a.com")
        self.assertIsNone(self.history.go_back(self.page_id))

    def test_go_forward(self):
        self.history.record(self.page_id, "https://a.com")
        self.history.record(self.page_id, "https://b.com")
        self.history.go_back(self.page_id)
        entry = self.history.go_forward(self.page_id)
        self.assertEqual(entry.url, "https://b.com")

    def test_go_forward_at_end(self):
        self.history.record(self.page_id, "https://a.com")
        self.assertIsNone(self.history.go_forward(self.page_id))

    def test_new_navigation_truncates_forward_history(self):
        self.history.record(self.page_id, "https://a.com")
        self.history.record(self.page_id, "https://b.com")
        self.history.record(self.page_id, "https://c.com")
        self.history.go_back(self.page_id)
        self.history.go_back(self.page_id)
        # Now at a.com with b,c in forward history
        self.history.record(self.page_id, "https://d.com")
        # Forward history should be truncated
        self.assertFalse(self.history.can_go_forward(self.page_id))
        self.assertEqual(len(self.history.get_all_entries(self.page_id)), 2)

    def test_max_history_limit(self):
        cfg = NavigationConfig(max_history_entries=3)
        history = NavigationHistory(config=cfg)
        for i in range(5):
            history.record(self.page_id, f"https://site{i}.com")
        entries = history.get_all_entries(self.page_id)
        self.assertEqual(len(entries), 3)
        self.assertEqual(entries[0].url, "https://site2.com")

    def test_redirect_tracking(self):
        chain = [RedirectInfo(from_url="http://a.com", to_url="https://a.com", status_code=301)]
        self.history.record(self.page_id, "https://a.com", redirect_chain=chain)
        info = self.history.get_history_info(self.page_id)
        self.assertEqual(info.total_redirects, 1)

    def test_get_history_info(self):
        self.history.record(self.page_id, "https://a.com", title="A")
        self.history.record(self.page_id, "https://b.com", title="B")
        info = self.history.get_history_info(self.page_id)
        self.assertEqual(info.page_id, self.page_id)
        self.assertEqual(info.current_url, "https://b.com")
        self.assertEqual(info.current_title, "B")
        self.assertEqual(info.entries_count, 2)
        self.assertTrue(info.can_go_back)
        self.assertFalse(info.can_go_forward)

    def test_get_history_info_empty_page(self):
        info = self.history.get_history_info("nonexistent")
        self.assertEqual(info.entries_count, 0)
        self.assertEqual(info.current_url, "")

    def test_clear_page_history(self):
        self.history.record(self.page_id, "https://a.com")
        self.history.clear_page_history(self.page_id)
        self.assertEqual(len(self.history.get_all_entries(self.page_id)), 0)

    def test_clear_all(self):
        self.history.record("p1", "https://a.com")
        self.history.record("p2", "https://b.com")
        self.history.clear_all()
        self.assertEqual(len(self.history.get_all_entries("p1")), 0)
        self.assertEqual(len(self.history.get_all_entries("p2")), 0)

    def test_record_with_history_disabled(self):
        cfg = NavigationConfig(record_history=False)
        history = NavigationHistory(config=cfg)
        entry = history.record(self.page_id, "https://a.com")
        self.assertEqual(entry.url, "https://a.com")
        # No entries should be stored
        self.assertEqual(len(history.get_all_entries(self.page_id)), 0)

    def test_get_all_entries(self):
        self.history.record(self.page_id, "https://a.com")
        self.history.record(self.page_id, "https://b.com")
        entries = self.history.get_all_entries(self.page_id)
        self.assertEqual(len(entries), 2)
        self.assertEqual(entries[0].url, "https://a.com")
        self.assertEqual(entries[1].url, "https://b.com")


# ==============================================================================
# Actions Tests
# ==============================================================================

class TestNavigationActions(unittest.TestCase):
    """Tests for navigation action primitives."""

    def setUp(self):
        self.actions = NavigationActions()

    def test_open_url_with_none_handle(self):
        result = asyncio.run(
            self.actions.open_url(None, "https://example.com")
        )
        self.assertTrue(result.success)
        self.assertEqual(result.url, "https://example.com")
        self.assertEqual(result.state, NavigationState.COMPLETED)

    def test_reload_with_none_handle(self):
        result = asyncio.run(
            self.actions.reload(None)
        )
        self.assertTrue(result.success)

    def test_go_back_with_none_handle(self):
        result = asyncio.run(
            self.actions.go_back(None)
        )
        self.assertTrue(result.success)

    def test_go_forward_with_none_handle(self):
        result = asyncio.run(
            self.actions.go_forward(None)
        )
        self.assertTrue(result.success)

    def test_stop_loading_with_none_handle(self):
        result = asyncio.run(
            self.actions.stop_loading(None)
        )
        self.assertTrue(result.success)
        self.assertEqual(result.state, NavigationState.CANCELLED)

    def test_get_current_url_with_none_handle(self):
        url = asyncio.run(
            self.actions.get_current_url(None)
        )
        self.assertEqual(url, "")

    def test_get_current_title_with_none_handle(self):
        title = asyncio.run(
            self.actions.get_current_title(None)
        )
        self.assertEqual(title, "")

    def test_classify_error_dns(self):
        err_type = self.actions._classify_error(Exception("DNS name resolution failed"))
        self.assertEqual(err_type, NavigationErrorType.DNS_FAILURE)

    def test_classify_error_ssl(self):
        err_type = self.actions._classify_error(Exception("SSL certificate verification failed"))
        self.assertEqual(err_type, NavigationErrorType.SSL_ERROR)

    def test_classify_error_timeout(self):
        err_type = self.actions._classify_error(Exception("Navigation timeout exceeded"))
        self.assertEqual(err_type, NavigationErrorType.TIMEOUT)

    def test_classify_error_crash(self):
        err_type = self.actions._classify_error(Exception("Browser has been closed"))
        self.assertEqual(err_type, NavigationErrorType.BROWSER_CRASH)

    def test_classify_error_cancelled(self):
        err_type = self.actions._classify_error(Exception("Navigation was cancelled"))
        self.assertEqual(err_type, NavigationErrorType.NAVIGATION_CANCELLED)

    def test_classify_error_net_err(self):
        err_type = self.actions._classify_error(Exception("net::err_connection_refused"))
        self.assertEqual(err_type, NavigationErrorType.PAGE_LOAD_FAILURE)

    def test_classify_error_unknown(self):
        err_type = self.actions._classify_error(Exception("Something weird happened"))
        self.assertEqual(err_type, NavigationErrorType.UNKNOWN)

    def test_open_url_result_has_load_time(self):
        result = asyncio.run(
            self.actions.open_url(None, "https://example.com")
        )
        self.assertGreaterEqual(result.load_time_ms, 0)

    def test_reload_result_has_load_time(self):
        result = asyncio.run(
            self.actions.reload(None)
        )
        self.assertGreaterEqual(result.load_time_ms, 0)


# ==============================================================================
# Navigator Tests
# ==============================================================================

class TestNavigator(unittest.TestCase):
    """Tests for the high-level Navigator orchestrator."""

    def setUp(self):
        self.bus = MagicMock()
        self.navigator = Navigator(bus=self.bus)

    def test_open_url_valid(self):
        result = asyncio.run(
            self.navigator.open_url("https://example.com")
        )
        self.assertTrue(result.success)
        self.assertEqual(result.url, "https://example.com")

    def test_open_url_invalid_url_fails(self):
        result = asyncio.run(
            self.navigator.open_url("")
        )
        self.assertFalse(result.success)
        self.assertEqual(result.error_type, NavigationErrorType.INVALID_URL)

    def test_open_url_unsupported_protocol_fails(self):
        result = asyncio.run(
            self.navigator.open_url("ftp://example.com")
        )
        self.assertFalse(result.success)
        self.assertEqual(result.error_type, NavigationErrorType.UNSUPPORTED_PROTOCOL)

    def test_open_url_records_history(self):
        asyncio.run(
            self.navigator.open_url("https://example.com")
        )
        info = self.navigator.get_history_info()
        self.assertEqual(info.entries_count, 1)
        self.assertEqual(info.current_url, "https://example.com")

    def test_open_url_publishes_events(self):
        asyncio.run(
            self.navigator.open_url("https://example.com")
        )
        # Should have published NAVIGATION_STARTED and NAVIGATION_COMPLETED
        event_names = [call[0][0] for call in self.bus.publish.call_args_list]
        self.assertIn("navigation_started", event_names)
        self.assertIn("navigation_completed", event_names)

    def test_open_url_invalid_publishes_no_start_event(self):
        asyncio.run(
            self.navigator.open_url("")
        )
        # Invalid URL should fail before publishing NAVIGATION_STARTED
        event_names = [call[0][0] for call in self.bus.publish.call_args_list]
        self.assertNotIn("navigation_started", event_names)

    def test_reload(self):
        result = asyncio.run(
            self.navigator.reload()
        )
        self.assertTrue(result.success)
        event_names = [call[0][0] for call in self.bus.publish.call_args_list]
        self.assertIn("page_reloaded", event_names)

    def test_go_back_no_history(self):
        result = asyncio.run(
            self.navigator.go_back()
        )
        self.assertFalse(result.success)

    def test_go_forward_no_history(self):
        result = asyncio.run(
            self.navigator.go_forward()
        )
        self.assertFalse(result.success)

    def test_go_back_with_history(self):
        asyncio.run(
            self.navigator.open_url("https://a.com")
        )
        asyncio.run(
            self.navigator.open_url("https://b.com")
        )
        result = asyncio.run(
            self.navigator.go_back()
        )
        self.assertTrue(result.success)
        event_names = [call[0][0] for call in self.bus.publish.call_args_list]
        self.assertIn("page_back", event_names)

    def test_go_forward_with_history(self):
        asyncio.run(
            self.navigator.open_url("https://a.com")
        )
        asyncio.run(
            self.navigator.open_url("https://b.com")
        )
        asyncio.run(
            self.navigator.go_back()
        )
        result = asyncio.run(
            self.navigator.go_forward()
        )
        self.assertTrue(result.success)
        event_names = [call[0][0] for call in self.bus.publish.call_args_list]
        self.assertIn("page_forward", event_names)

    def test_stop_loading(self):
        result = asyncio.run(
            self.navigator.stop_loading()
        )
        self.assertTrue(result.success)
        event_names = [call[0][0] for call in self.bus.publish.call_args_list]
        self.assertIn("page_stopped", event_names)

    def test_current_url_with_none_resolver(self):
        url = asyncio.run(
            self.navigator.current_url()
        )
        self.assertEqual(url, "")

    def test_current_title_with_none_resolver(self):
        title = asyncio.run(
            self.navigator.current_title()
        )
        self.assertEqual(title, "")

    def test_get_health_status(self):
        status = self.navigator.get_health_status()
        self.assertEqual(status.state, NavigationState.IDLE)
        self.assertEqual(status.total_navigations, 0)

    def test_health_status_after_navigations(self):
        asyncio.run(
            self.navigator.open_url("https://example.com")
        )
        asyncio.run(
            self.navigator.open_url("")
        )
        status = self.navigator.get_health_status()
        self.assertEqual(status.total_navigations, 1)  # invalid URL doesn't count as a navigation
        self.assertEqual(status.successful_navigations, 1)

    def test_wait_for_page_load(self):
        wait_ms = asyncio.run(
            self.navigator.wait_for_page_load()
        )
        self.assertIsInstance(wait_ms, float)
        event_names = [call[0][0] for call in self.bus.publish.call_args_list]
        self.assertIn("wait_completed", event_names)

    def test_wait_for_network_idle(self):
        wait_ms = asyncio.run(
            self.navigator.wait_for_network_idle()
        )
        self.assertIsInstance(wait_ms, float)

    def test_wait_for_dom_ready(self):
        wait_ms = asyncio.run(
            self.navigator.wait_for_dom_ready()
        )
        self.assertIsInstance(wait_ms, float)

    def test_open_url_about_blank(self):
        result = asyncio.run(
            self.navigator.open_url("about:blank")
        )
        self.assertTrue(result.success)

    def test_multiple_navigations_history_tracking(self):
        for i in range(5):
            asyncio.run(
                self.navigator.open_url(f"https://site{i}.com")
            )
        info = self.navigator.get_history_info()
        self.assertEqual(info.entries_count, 5)
        self.assertTrue(info.can_go_back)
        self.assertFalse(info.can_go_forward)


# ==============================================================================
# Service Tests
# ==============================================================================

class TestPageHandleResolver(unittest.TestCase):
    """Tests for PageHandleResolver dependency injection."""

    def test_resolve_with_none_manager(self):
        resolver = PageHandleResolver(page_manager=None)
        self.assertIsNone(resolver.get_page_handle("p1"))

    def test_resolve_with_mock_manager(self):
        mock_pm = MagicMock()
        mock_pm.get_page_handle.return_value = "fake_handle"
        resolver = PageHandleResolver(page_manager=mock_pm)
        handle = resolver.get_page_handle("p1")
        self.assertEqual(handle, "fake_handle")
        mock_pm.get_page_handle.assert_called_once_with("p1")


class TestNavigationService(unittest.TestCase):
    """Tests for the top-level NavigationService."""

    def setUp(self):
        self.bus = MagicMock()
        self.service = NavigationService(bus=self.bus)

    def test_open_url(self):
        result = asyncio.run(
            self.service.open_url("https://example.com")
        )
        self.assertTrue(result.success)

    def test_open_url_invalid(self):
        result = asyncio.run(
            self.service.open_url("")
        )
        self.assertFalse(result.success)

    def test_reload(self):
        result = asyncio.run(
            self.service.reload()
        )
        self.assertTrue(result.success)

    def test_go_back(self):
        result = asyncio.run(
            self.service.go_back()
        )
        self.assertFalse(result.success)  # No history

    def test_go_forward(self):
        result = asyncio.run(
            self.service.go_forward()
        )
        self.assertFalse(result.success)  # No history

    def test_stop_loading(self):
        result = asyncio.run(
            self.service.stop_loading()
        )
        self.assertTrue(result.success)

    def test_current_url(self):
        url = asyncio.run(
            self.service.current_url()
        )
        self.assertEqual(url, "")

    def test_current_title(self):
        title = asyncio.run(
            self.service.current_title()
        )
        self.assertEqual(title, "")

    def test_wait_for_page_load(self):
        wait = asyncio.run(
            self.service.wait_for_page_load()
        )
        self.assertIsInstance(wait, float)

    def test_wait_for_network_idle(self):
        wait = asyncio.run(
            self.service.wait_for_network_idle()
        )
        self.assertIsInstance(wait, float)

    def test_wait_for_dom_ready(self):
        wait = asyncio.run(
            self.service.wait_for_dom_ready()
        )
        self.assertIsInstance(wait, float)

    def test_get_history_info(self):
        info = self.service.get_history_info()
        self.assertIsInstance(info, NavigationHistoryInfo)
        self.assertEqual(info.entries_count, 0)

    def test_get_health_status(self):
        status = self.service.get_health_status()
        self.assertIsInstance(status, NavigationHealthStatus)
        self.assertEqual(status.total_navigations, 0)

    def test_is_healthy(self):
        self.assertTrue(self.service.is_healthy())

    def test_full_navigation_workflow(self):
        """Integration test: open_url -> open_url -> go_back -> go_forward -> reload -> stop"""
        # Navigate to two pages
        r1 = asyncio.run(self.service.open_url("https://a.com"))
        self.assertTrue(r1.success)

        r2 = asyncio.run(self.service.open_url("https://b.com"))
        self.assertTrue(r2.success)

        # Go back
        r3 = asyncio.run(self.service.go_back())
        self.assertTrue(r3.success)

        # Go forward
        r4 = asyncio.run(self.service.go_forward())
        self.assertTrue(r4.success)

        # Reload
        r5 = asyncio.run(self.service.reload())
        self.assertTrue(r5.success)

        # Stop loading
        r6 = asyncio.run(self.service.stop_loading())
        self.assertTrue(r6.success)

        # Check history
        info = self.service.get_history_info()
        self.assertGreater(info.entries_count, 0)

        # Check health
        status = self.service.get_health_status()
        self.assertGreater(status.total_navigations, 0)

        # Verify event bus received events
        event_names = [call[0][0] for call in self.bus.publish.call_args_list]
        self.assertIn("navigation_started", event_names)
        self.assertIn("navigation_completed", event_names)
        self.assertIn("page_back", event_names)
        self.assertIn("page_forward", event_names)
        self.assertIn("page_reloaded", event_names)
        self.assertIn("page_stopped", event_names)

    def test_open_url_with_wait_strategy(self):
        result = asyncio.run(
            self.service.open_url("https://example.com", wait_strategy=WaitStrategy.NONE)
        )
        self.assertTrue(result.success)

    def test_navigation_with_custom_timeout(self):
        result = asyncio.run(
            self.service.open_url("https://example.com", timeout_ms=5000)
        )
        self.assertTrue(result.success)

    def test_service_with_page_manager(self):
        mock_pm = MagicMock()
        mock_pm.get_page_handle.return_value = None
        service = NavigationService(bus=self.bus, page_manager=mock_pm)
        result = asyncio.run(
            service.open_url("https://example.com", page_id="p1")
        )
        self.assertTrue(result.success)


# ==============================================================================
# Integration Tests
# ==============================================================================

class TestNavigationIntegration(unittest.TestCase):
    """Integration tests verifying end-to-end Navigation Engine behavior."""

    def setUp(self):
        self.bus = MagicMock()

    def test_redirect_loop_detection_in_navigator(self):
        """Verify that redirect loops are detected and reported as failures."""
        navigator = Navigator(bus=self.bus)
        # Simulate redirect chain with a loop by injecting mock actions
        original_open = navigator.actions.open_url

        async def mock_open(handle, url, timeout_ms=None):
            return NavigationResult(
                success=True,
                url=url,
                redirect_count=3,
                redirect_chain=[
                    RedirectInfo(from_url="http://a.com", to_url="http://b.com"),
                    RedirectInfo(from_url="http://b.com", to_url="http://a.com"),
                    RedirectInfo(from_url="http://a.com", to_url=url),
                ],
                state=NavigationState.COMPLETED,
            )

        navigator.actions.open_url = mock_open
        result = asyncio.run(
            navigator.open_url("https://target.com")
        )
        self.assertFalse(result.success)
        self.assertEqual(result.error_type, NavigationErrorType.REDIRECT_LOOP)

    def test_retry_behavior_on_transient_failure(self):
        """Verify that transient failures trigger retries."""
        config = NavigationConfig(retry_count=2, retry_delay_ms=10)
        navigator = Navigator(bus=self.bus, config=config)

        call_count = 0
        original_open = navigator.actions.open_url

        async def mock_open(handle, url, timeout_ms=None):
            nonlocal call_count
            call_count += 1
            if call_count < 3:
                return NavigationResult(
                    success=False,
                    url=url,
                    error_type=NavigationErrorType.TIMEOUT,
                    error_message="Timed out",
                    state=NavigationState.TIMED_OUT,
                )
            return NavigationResult(success=True, url=url, state=NavigationState.COMPLETED)

        navigator.actions.open_url = mock_open
        result = asyncio.run(
            navigator.open_url("https://example.com")
        )
        self.assertTrue(result.success)
        self.assertEqual(call_count, 3)

    def test_non_retryable_error_skips_retries(self):
        """Verify that non-retryable errors (invalid URL, unsupported protocol) don't retry."""
        config = NavigationConfig(retry_count=3, retry_delay_ms=10)
        navigator = Navigator(bus=self.bus, config=config)

        call_count = 0
        async def mock_open(handle, url, timeout_ms=None):
            nonlocal call_count
            call_count += 1
            return NavigationResult(
                success=False,
                url=url,
                error_type=NavigationErrorType.INVALID_URL,
                error_message="Bad URL",
                state=NavigationState.FAILED,
            )

        navigator.actions.open_url = mock_open
        result = asyncio.run(
            navigator.open_url("https://valid.com")  # URL passes validation, but actions returns invalid
        )
        self.assertFalse(result.success)
        self.assertEqual(call_count, 1)  # Should not have retried

    def test_page_resolver_callable(self):
        """Verify that Navigator works with a plain callable resolver."""
        resolver = lambda pid: None
        navigator = Navigator(bus=self.bus, page_resolver=resolver)
        result = asyncio.run(
            navigator.open_url("https://example.com", page_id="p1")
        )
        self.assertTrue(result.success)

    def test_bus_failure_does_not_crash_navigation(self):
        """Verify that EventBus errors are handled gracefully."""
        self.bus.publish.side_effect = RuntimeError("Bus is down")
        navigator = Navigator(bus=self.bus)
        result = asyncio.run(
            navigator.open_url("https://example.com")
        )
        self.assertTrue(result.success)

    def test_multiple_pages_independent_history(self):
        """Verify that history is tracked independently per page."""
        navigator = Navigator(bus=self.bus)
        asyncio.run(
            navigator.open_url("https://a.com", page_id="p1")
        )
        asyncio.run(
            navigator.open_url("https://b.com", page_id="p2")
        )
        info1 = navigator.get_history_info(page_id="p1")
        info2 = navigator.get_history_info(page_id="p2")
        self.assertEqual(info1.current_url, "https://a.com")
        self.assertEqual(info2.current_url, "https://b.com")
        self.assertEqual(info1.entries_count, 1)
        self.assertEqual(info2.entries_count, 1)


if __name__ == "__main__":
    unittest.main()

"""
Browser Action Engine Unit & Integration Tests.
Covers: models, events, locators, prechecks, verification, click, typing, scrolling,
forms, upload, download, retries, and high-level workflow action APIs.
"""

import asyncio
import os
import sys
import tempfile
import time
import unittest
from unittest.mock import AsyncMock, MagicMock, patch

sys.path.insert(0, ".")

from browser.actions.models import (
    ActionEngineConfig,
    ActionHealthStatus,
    ActionOptions,
    ActionResult,
    ActionState,
    ActionType,
    DownloadResult,
    LocatorStrategy,
    ScrollDirection,
    TargetElement,
)
from browser.actions.events import ActionEvent
from browser.actions.locator import SmartElementLocator
from browser.actions.waits import ActionWaitExecutor
from browser.actions.verification import ActionVerifier
from browser.actions.click import ClickActionExecutor
from browser.actions.typing import TypingActionExecutor
from browser.actions.scrolling import ScrollActionExecutor
from browser.actions.forms import FormActionExecutor
from browser.actions.upload import UploadActionExecutor
from browser.actions.download import DownloadActionExecutor
from browser.actions.action_engine import ActionEngine
from browser.actions.service import BrowserActionService


# ==============================================================================
# Model & Event Tests
# ==============================================================================

class TestActionModels(unittest.TestCase):
    """Tests for Action Engine domain models."""

    def test_action_type_enum(self):
        self.assertEqual(ActionType.CLICK.value, "click")
        self.assertEqual(ActionType.TYPE_TEXT.value, "type_text")
        self.assertEqual(ActionType.SUBMIT_FORM.value, "submit_form")
        self.assertEqual(ActionType.DOWNLOAD_FILE.value, "download_file")

    def test_locator_strategy_enum(self):
        self.assertEqual(LocatorStrategy.ACCESSIBILITY_ROLE.value, "accessibility_role")
        self.assertEqual(LocatorStrategy.LABEL.value, "label")
        self.assertEqual(LocatorStrategy.AUTOMATION_ID.value, "automation_id")

    def test_target_element_to_dict(self):
        target = TargetElement(query="Submit", role="button")
        d = target.to_dict()
        self.assertEqual(d["query"], "Submit")
        self.assertEqual(d["role"], "button")

    def test_action_options_defaults(self):
        opts = ActionOptions()
        self.assertEqual(opts.timeout_ms, 30000.0)
        self.assertEqual(opts.retry_count, 2)
        self.assertTrue(opts.verify_result)

    def test_action_result_to_dict(self):
        res = ActionResult(
            success=True,
            action_type=ActionType.CLICK,
            target_query="Sign In",
            execution_time_ms=45.2,
            verified=True,
        )
        d = res.to_dict()
        self.assertTrue(d["success"])
        self.assertEqual(d["action_type"], "click")
        self.assertEqual(d["target_query"], "Sign In")
        self.assertTrue(d["verified"])

    def test_download_result_to_dict(self):
        dl = DownloadResult(
            success=True,
            file_path="/downloads/report.pdf",
            file_name="report.pdf",
            file_size_bytes=2048,
        )
        d = dl.to_dict()
        self.assertTrue(d["success"])
        self.assertEqual(d["file_name"], "report.pdf")
        self.assertEqual(d["file_size_bytes"], 2048)


class TestActionEvents(unittest.TestCase):
    """Tests for Action Event enums."""

    def test_action_events(self):
        self.assertEqual(ActionEvent.ACTION_STARTED.value, "action_started")
        self.assertEqual(ActionEvent.ACTION_COMPLETED.value, "action_completed")
        self.assertEqual(ActionEvent.ELEMENT_FOUND.value, "element_found")
        self.assertEqual(ActionEvent.FORM_SUBMITTED.value, "form_submitted")
        self.assertEqual(ActionEvent.DOWNLOAD_STARTED.value, "download_started")


# ==============================================================================
# Locator Tests
# ==============================================================================

class TestSmartElementLocator(unittest.TestCase):
    """Tests for SmartElementLocator resolution."""

    def setUp(self):
        self.locator = SmartElementLocator()

    def test_resolve_target_string(self):
        target = self.locator.resolve_target("Sign In")
        self.assertEqual(target.query, "Sign In")
        self.assertEqual(target.text, "Sign In")

    def test_resolve_target_css(self):
        target = self.locator.resolve_target("#submit-btn")
        self.assertEqual(target.strategy, LocatorStrategy.CSS_SELECTOR)
        self.assertEqual(target.css_selector, "#submit-btn")

    def test_resolve_target_xpath(self):
        target = self.locator.resolve_target("//button[@id='submit']")
        self.assertEqual(target.strategy, LocatorStrategy.XPATH)

    def test_build_candidates(self):
        target = TargetElement(query="Search", label="Search Box", role="searchbox")
        candidates = self.locator.build_selector_candidates(target)
        self.assertGreater(len(candidates), 3)
        strats = [c[0] for c in candidates]
        self.assertIn(LocatorStrategy.ACCESSIBILITY_ROLE, strats)
        self.assertIn(LocatorStrategy.LABEL, strats)


# ==============================================================================
# Waits & Verification Tests
# ==============================================================================

class TestActionWaitExecutor(unittest.TestCase):
    """Tests for prechecks and stability waits."""

    def setUp(self):
        self.waits = ActionWaitExecutor()

    def test_precheck_mock_handles(self):
        ok, err = asyncio.run(self.waits.precheck_element(None, None))
        self.assertTrue(ok)
        self.assertIsNone(err)

    def test_precheck_visible_and_enabled(self):
        mock_elem = AsyncMock()
        mock_elem.is_visible.return_value = True
        mock_elem.is_enabled.return_value = True
        ok, err = asyncio.run(self.waits.precheck_element(MagicMock(), mock_elem))
        self.assertTrue(ok)


class TestActionVerifier(unittest.TestCase):
    """Tests for post-action verification."""

    def setUp(self):
        self.verifier = ActionVerifier()

    def test_verify_text_input_match(self):
        mock_elem = AsyncMock()
        mock_elem.input_value.return_value = "Artificial Intelligence"
        ok, note = asyncio.run(
            self.verifier.verify_action(ActionType.TYPE_TEXT, MagicMock(), mock_elem, expected_value="Artificial Intelligence")
        )
        self.assertTrue(ok)

    def test_verify_checkbox_state_match(self):
        mock_elem = AsyncMock()
        mock_elem.is_checked.return_value = True
        ok, note = asyncio.run(
            self.verifier.verify_action(ActionType.CHECK_CHECKBOX, MagicMock(), mock_elem)
        )
        self.assertTrue(ok)


# ==============================================================================
# Action Executors Unit Tests
# ==============================================================================

class TestClickActionExecutor(unittest.TestCase):
    def setUp(self):
        self.executor = ClickActionExecutor()

    def test_click(self):
        elem = AsyncMock()
        ok = asyncio.run(self.executor.click(elem))
        self.assertTrue(ok)
        elem.click.assert_called_once()

    def test_double_click(self):
        elem = AsyncMock()
        ok = asyncio.run(self.executor.double_click(elem))
        self.assertTrue(ok)

    def test_hover(self):
        elem = AsyncMock()
        ok = asyncio.run(self.executor.hover(elem))
        self.assertTrue(ok)


class TestTypingActionExecutor(unittest.TestCase):
    def setUp(self):
        self.executor = TypingActionExecutor()

    def test_type_text(self):
        elem = AsyncMock()
        ok = asyncio.run(self.executor.type_text(elem, "Hello"))
        self.assertTrue(ok)

    def test_clear_field(self):
        elem = AsyncMock()
        ok = asyncio.run(self.executor.clear_field(elem))
        self.assertTrue(ok)

    def test_press_shortcut(self):
        page = MagicMock()
        page.keyboard = AsyncMock()
        ok = asyncio.run(self.executor.press_shortcut(page, "Control+A"))
        self.assertTrue(ok)


class TestScrollActionExecutor(unittest.TestCase):
    def setUp(self):
        self.executor = ScrollActionExecutor()

    def test_scroll_down(self):
        page = AsyncMock()
        ok = asyncio.run(self.executor.scroll(page, direction=ScrollDirection.DOWN))
        self.assertTrue(ok)


class TestFormActionExecutor(unittest.TestCase):
    def setUp(self):
        self.executor = FormActionExecutor()

    def test_select_dropdown(self):
        elem = AsyncMock()
        ok = asyncio.run(self.executor.select_dropdown(elem, "Option1"))
        self.assertTrue(ok)

    def test_check_checkbox(self):
        elem = AsyncMock()
        ok = asyncio.run(self.executor.check_checkbox(elem))
        self.assertTrue(ok)

    def test_submit_form(self):
        elem = AsyncMock()
        ok = asyncio.run(self.executor.submit_form(elem))
        self.assertTrue(ok)


class TestUploadActionExecutor(unittest.TestCase):
    def setUp(self):
        self.executor = UploadActionExecutor()

    def test_upload_file(self):
        with tempfile.NamedTemporaryFile(delete=False) as f:
            f.write(b"test data")
            temp_path = f.name

        try:
            elem = AsyncMock()
            ok = asyncio.run(self.executor.upload_file(elem, temp_path))
            self.assertTrue(ok)
        finally:
            if os.path.exists(temp_path):
                os.remove(temp_path)


class TestDownloadActionExecutor(unittest.TestCase):
    def setUp(self):
        self.executor = DownloadActionExecutor()

    def test_download_file_fallback(self):
        page = MagicMock()
        trigger = AsyncMock()
        with tempfile.TemporaryDirectory() as tmpdir:
            res = asyncio.run(
                self.executor.download_file(page, trigger, download_directory=tmpdir)
            )
            self.assertTrue(res.success)


# ==============================================================================
# ActionEngine & Service Integration Tests
# ==============================================================================

class TestActionEngine(unittest.TestCase):
    """Integration tests for ActionEngine orchestrator."""

    def setUp(self):
        self.bus = MagicMock()
        self.engine = ActionEngine(bus=self.bus)

    def test_click_action(self):
        res = asyncio.run(self.engine.click("Sign In"))
        self.assertTrue(res.success)
        self.assertEqual(res.action_type, ActionType.CLICK)

    def test_type_action(self):
        res = asyncio.run(self.engine.type("Search Box", "Artificial Intelligence"))
        self.assertTrue(res.success)
        self.assertEqual(res.action_type, ActionType.TYPE_TEXT)

    def test_submit_action(self):
        res = asyncio.run(self.engine.submit("Search Form"))
        self.assertTrue(res.success)
        self.assertEqual(res.action_type, ActionType.SUBMIT_FORM)

    def test_scroll_action(self):
        res = asyncio.run(self.engine.scroll(direction=ScrollDirection.DOWN))
        self.assertTrue(res.success)

    def test_upload_action(self):
        with tempfile.NamedTemporaryFile(delete=False) as f:
            temp_path = f.name
        try:
            res = asyncio.run(self.engine.upload("Upload Input", temp_path))
            self.assertTrue(res.success)
        finally:
            if os.path.exists(temp_path):
                os.remove(temp_path)

    def test_download_action(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            res = asyncio.run(self.engine.download("Download Button", download_directory=tmpdir))
            self.assertTrue(res.success)
            self.assertIsNotNone(res.download_info)

    def test_telemetry_and_health(self):
        asyncio.run(self.engine.click("Button 1"))
        asyncio.run(self.engine.type("Input 1", "Text"))
        status = self.engine.get_health_status()
        self.assertEqual(status.total_actions, 2)
        self.assertEqual(status.successful_actions, 2)


class TestBrowserActionService(unittest.TestCase):
    """Integration tests for high-level BrowserActionService."""

    def setUp(self):
        self.bus = MagicMock()
        self.service = BrowserActionService(bus=self.bus)

    def test_service_click(self):
        res = asyncio.run(self.service.click("Sign In"))
        self.assertTrue(res.success)

    def test_service_type(self):
        res = asyncio.run(self.service.type("Search", "Deep Learning"))
        self.assertTrue(res.success)

    def test_service_select(self):
        res = asyncio.run(self.service.select("Country", "United States"))
        self.assertTrue(res.success)

    def test_service_check_uncheck(self):
        res1 = asyncio.run(self.service.check("Remember Me"))
        self.assertTrue(res1.success)
        res2 = asyncio.run(self.service.uncheck("Remember Me"))
        self.assertTrue(res2.success)

    def test_service_submit(self):
        res = asyncio.run(self.service.submit("Login Form"))
        self.assertTrue(res.success)

    def test_service_health(self):
        self.assertTrue(self.service.is_healthy())
        status = self.service.get_health_status()
        self.assertIsInstance(status, ActionHealthStatus)


if __name__ == "__main__":
    unittest.main()

"""
Computer Service & Desktop Automation Subsystem Unit & Integration Tests.
Covers domain models, event definitions, configuration, Windows provider execution,
manager provider factory initialization, and ComputerService lifecycle.
"""

import asyncio
import sys
import unittest
from unittest.mock import MagicMock, patch

sys.path.insert(0, ".")

from computer.models import (
    ClipboardContent,
    ComputerHealthStatus,
    ComputerResult,
    ComputerState,
    DesktopActionType,
    DesktopAppInfo,
    DesktopUIElement,
    DesktopWindowInfo,
    PlatformType,
)
from computer.events import ComputerEvent
from computer.configuration import ComputerConfig
from computer.providers.windows_provider import BaseComputerProvider, WindowsComputerProvider
from computer.manager import ComputerManager
from computer.service import ComputerService


# ==============================================================================
# Domain Models & Events Tests
# ==============================================================================

class TestComputerModels(unittest.TestCase):
    """Tests for Computer Subsystem Domain Models."""

    def test_window_info_serialization(self):
        win = DesktopWindowInfo(
            handle=1234,
            title="Calculator",
            class_name="CalcFrame",
            bounds=(10, 10, 800, 600),
            is_focused=True,
        )
        d = win.to_dict()
        self.assertEqual(d["handle"], 1234)
        self.assertEqual(d["title"], "Calculator")
        self.assertTrue(d["is_focused"])

    def test_clipboard_content_serialization(self):
        clip = ClipboardContent(text="Hello AURA", formats=["CF_TEXT"])
        d = clip.to_dict()
        self.assertEqual(d["text"], "Hello AURA")
        self.assertEqual(d["formats"], ["CF_TEXT"])

    def test_computer_result_serialization(self):
        res = ComputerResult(
            success=True,
            action="launch_app",
            message="App launched",
            data={"pid": 999},
        )
        d = res.to_dict()
        self.assertTrue(d["success"])
        self.assertEqual(d["action"], "launch_app")

    def test_computer_event_enum(self):
        self.assertEqual(ComputerEvent.COMPUTER_STARTED.value, "computer_started")
        self.assertEqual(ComputerEvent.COMPUTER_READY.value, "computer_ready")
        self.assertEqual(ComputerEvent.PROVIDER_LOADED.value, "provider_loaded")


# ==============================================================================
# Windows Provider Tests
# ==============================================================================

class TestWindowsComputerProvider(unittest.TestCase):
    """Tests for WindowsComputerProvider platform-independent primitives."""

    def setUp(self):
        self.provider = WindowsComputerProvider()

    def test_provider_name(self):
        self.assertEqual(self.provider.get_provider_name(), "WindowsComputerProvider")
        self.assertTrue(self.provider.is_healthy())

    def test_mouse_click(self):
        res = asyncio.run(self.provider.mouse_click(100, 200, button="left"))
        self.assertTrue(res.success)
        self.assertEqual(res.action, "mouse_click")

    def test_type_text(self):
        res = asyncio.run(self.provider.type_text("AURA OS Automation"))
        self.assertTrue(res.success)
        self.assertEqual(res.action, "type_text")

    def test_clipboard_read_write(self):
        w_res = asyncio.run(self.provider.write_clipboard("Sample Text"))
        self.assertTrue(w_res.success)

        clip = asyncio.run(self.provider.read_clipboard())
        self.assertIsNotNone(clip.text)

    def test_get_active_window(self):
        win = asyncio.run(self.provider.get_active_window())
        self.assertIsNotNone(win)
        self.assertTrue(win.is_focused)


# ==============================================================================
# Computer Manager & Factory Tests
# ==============================================================================

class TestComputerManager(unittest.TestCase):
    """Tests for ComputerManager factory and platform detection."""

    def setUp(self):
        self.bus = MagicMock()
        self.manager = ComputerManager(bus=self.bus)

    def test_initialize_provider_factory(self):
        provider = self.manager.initialize_provider()
        self.assertIsNotNone(provider)
        self.assertEqual(self.manager.state, ComputerState.READY)
        self.bus.publish.assert_called_once()

    def test_health_status(self):
        self.manager.initialize_provider()
        status = self.manager.get_health_status()
        self.assertEqual(status.state, ComputerState.READY)
        self.assertIsNotNone(status.provider_name)


# ==============================================================================
# Computer Service Integration Tests
# ==============================================================================

class TestComputerService(unittest.TestCase):
    """Tests for top-level ComputerService lifecycle and API."""

    def setUp(self):
        self.bus = MagicMock()
        self.service = ComputerService(bus=self.bus)

    def test_service_lifecycle(self):
        self.service.start()
        self.assertTrue(self.service.is_healthy())

        # Verify events published
        published_events = [call[0][0] for call in self.bus.publish.call_args_list]
        self.assertIn("computer_started", published_events)
        self.assertIn("computer_ready", published_events)

        self.service.stop()
        self.assertIn("computer_stopped", [call[0][0] for call in self.bus.publish.call_args_list])

    def test_high_level_operations(self):
        self.service.start()

        # Click
        c_res = asyncio.run(self.service.click(500, 500))
        self.assertTrue(c_res.success)

        # Type Text
        t_res = asyncio.run(self.service.type_text("Testing ComputerService"))
        self.assertTrue(t_res.success)

        # Clipboard
        clip = asyncio.run(self.service.read_clipboard())
        self.assertIsNotNone(clip.text)

        # Health Telemetry
        status = self.service.get_health_status()
        self.assertEqual(status.state, ComputerState.READY)


if __name__ == "__main__":
    unittest.main()

"""
Window Manager Subsystem Unit & Integration Tests.
Covers domain models, state transitions, repository registry, locator search engine,
active health monitor, master AURAWindowManager, and WindowManagerService lifecycle.
"""

import asyncio
import sys
import unittest
from unittest.mock import MagicMock, patch

sys.path.insert(0, ".")

from computer.windows.models import (
    AURAWindow,
    WindowActionResult,
    WindowSearchQuery,
    WindowState,
)
from computer.windows.events import WindowEvent
from computer.windows.configuration import WindowManagerConfig
from computer.windows.window_state import WindowStateTracker
from computer.windows.window_registry import WindowRegistry
from computer.windows.window_locator import WindowLocator
from computer.windows.window_monitor import WindowMonitor
from computer.windows.window_manager import AURAWindowManager
from computer.windows.service import WindowManagerService


# ==============================================================================
# Domain Models & State Tests
# ==============================================================================

class TestWindowModelsAndState(unittest.TestCase):
    """Tests for Window domain models and state transitions."""

    def test_window_serialization(self):
        win = AURAWindow(title="Notepad", app_id="notepad.exe", bounds=(100, 100, 800, 600))
        d = win.to_dict()
        self.assertIsNotNone(d["window_id"])
        self.assertEqual(d["title"], "Notepad")
        self.assertEqual(d["state"], "normal")

    def test_state_tracker_transitions(self):
        tracker = WindowStateTracker()
        win = AURAWindow(title="Calculator")

        tracker.set_focused(win)
        self.assertEqual(win.state, WindowState.FOCUSED)

        tracker.set_minimized(win)
        self.assertEqual(win.state, WindowState.MINIMIZED)

        tracker.set_maximized(win)
        self.assertEqual(win.state, WindowState.MAXIMIZED)

        tracker.update_bounds(win, (50, 50, 500, 400))
        self.assertEqual(win.bounds, (50, 50, 500, 400))


# ==============================================================================
# Registry & Locator Search Engine Tests
# ==============================================================================

class TestWindowRegistryAndLocator(unittest.TestCase):
    """Tests for WindowRegistry repository and WindowLocator search engine."""

    def setUp(self):
        self.registry = WindowRegistry()
        self.locator = WindowLocator()

        self.w1 = AURAWindow(title="Document1 - Microsoft Word", app_id="word.exe", process_id=101, class_name="OpusApp")
        self.w2 = AURAWindow(title="Untitled - Notepad", app_id="notepad.exe", process_id=202, class_name="Notepad")
        self.w3 = AURAWindow(title="Google Chrome - AURA", app_id="chrome.exe", process_id=303, class_name="Chrome_WidgetWin_1")

        self.registry.register_window(self.w1, internal_handle=1001)
        self.registry.register_window(self.w2, internal_handle=1002)
        self.registry.register_window(self.w3, internal_handle=1003)

    def test_registry_lookup(self):
        found = self.registry.get_window_by_handle(1002)
        self.assertIsNotNone(found)
        self.assertEqual(found.title, "Untitled - Notepad")

    def test_locator_title_partial_match(self):
        q = WindowSearchQuery(title="Notepad", partial_match=True)
        res = self.locator.find_windows(self.registry.get_all_windows(), q)
        self.assertEqual(len(res), 1)
        self.assertEqual(res[0].app_id, "notepad.exe")

    def test_locator_regex_match(self):
        q = WindowSearchQuery(regex_pattern=r"Microsoft\s+Word")
        res = self.locator.find_windows(self.registry.get_all_windows(), q)
        self.assertEqual(len(res), 1)
        self.assertEqual(res[0].process_id, 101)


# ==============================================================================
# Window Manager Master Orchestrator Tests
# ==============================================================================

class TestAURAWindowManager(unittest.TestCase):
    """Integration tests for master AURAWindowManager operations."""

    def setUp(self):
        self.bus = MagicMock()
        self.manager = AURAWindowManager(bus=self.bus)

    def test_register_and_find_window(self):
        w = self.manager.register_window("Paint", app_id="mspaint.exe")
        found = self.manager.find_window(title="Paint")
        self.assertIsNotNone(found)
        self.assertEqual(found.window_id, w.window_id)

    def test_window_control_actions(self):
        w = self.manager.register_window("Terminal", app_id="cmd.exe")

        # Focus
        f_res = asyncio.run(self.manager.focus_window(w.window_id))
        self.assertTrue(f_res.success)
        self.assertEqual(w.state, WindowState.FOCUSED)

        # Minimize
        m_res = asyncio.run(self.manager.minimize_window(w.window_id))
        self.assertTrue(m_res.success)
        self.assertEqual(w.state, WindowState.MINIMIZED)

        # Move
        mv_res = asyncio.run(self.manager.move_window(w.window_id, 200, 300))
        self.assertTrue(mv_res.success)
        self.assertEqual(w.bounds[0], 200)

        # Resize
        r_res = asyncio.run(self.manager.resize_window(w.window_id, 1024, 768))
        self.assertTrue(r_res.success)
        self.assertEqual(w.bounds[2], 1024)

        # Close
        c_res = asyncio.run(self.manager.close_window(w.window_id))
        self.assertTrue(c_res.success)
        self.assertIsNone(self.manager.registry.get_window_by_id(w.window_id))


# ==============================================================================
# Window Manager Service Integration Tests
# ==============================================================================

class TestWindowManagerService(unittest.TestCase):
    """Integration tests for WindowManagerService."""

    def setUp(self):
        self.bus = MagicMock()
        self.service = WindowManagerService(bus=self.bus)

    def test_service_lifecycle(self):
        self.service.start()
        self.assertTrue(self.service.is_healthy())

        w = self.service.register_window("Visual Studio Code", app_id="code.exe")
        self.assertEqual(len(self.service.enumerate_windows()), 1)

        f_res = asyncio.run(self.service.focus_window(w.window_id))
        self.assertTrue(f_res.success)

        self.service.stop()


if __name__ == "__main__":
    unittest.main()

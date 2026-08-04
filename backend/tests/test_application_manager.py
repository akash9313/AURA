"""
Application Manager Subsystem Unit & Integration Tests.
Covers domain models, state transitions, repository registry, asynchronous launcher,
process monitor, master AURAApplicationManager, and ApplicationManagerService lifecycle.
"""

import asyncio
import sys
import unittest
from unittest.mock import AsyncMock, MagicMock, patch

sys.path.insert(0, ".")

from computer.applications.models import (
    ApplicationLaunchOptions,
    ApplicationResult,
    ApplicationState,
    AURAApplication,
)
from computer.applications.events import ApplicationEvent
from computer.applications.configuration import ApplicationManagerConfig
from computer.applications.lifecycle import ApplicationLifecycleTracker
from computer.applications.registry import ApplicationRegistry
from computer.applications.launcher import ApplicationLauncher
from computer.applications.process_monitor import ProcessMonitor
from computer.applications.application_manager import AURAApplicationManager
from computer.applications.service import ApplicationManagerService


# ==============================================================================
# Domain Models & Lifecycle Tests
# ==============================================================================

class TestApplicationModelsAndLifecycle(unittest.TestCase):
    """Tests for Application domain models and state transitions."""

    def test_application_serialization(self):
        app = AURAApplication(
            name="Notepad",
            executable_path="notepad.exe",
            process_id=4567,
            working_directory="C:\\Windows",
        )
        d = app.to_dict()
        self.assertIsNotNone(d["app_id"])
        self.assertEqual(d["name"], "Notepad")
        self.assertEqual(d["status"], "starting")

    def test_lifecycle_tracker(self):
        tracker = ApplicationLifecycleTracker()
        app = AURAApplication(name="Calculator")

        tracker.set_starting(app)
        self.assertEqual(app.status, ApplicationState.STARTING)
        self.assertFalse(app.is_ready)

        tracker.set_ready(app)
        self.assertEqual(app.status, ApplicationState.RUNNING)
        self.assertTrue(app.is_ready)

        tracker.set_crashed(app)
        self.assertEqual(app.status, ApplicationState.CRASHED)
        self.assertFalse(app.is_ready)


# ==============================================================================
# Registry & Launcher Tests
# ==============================================================================

class TestApplicationRegistryAndLauncher(unittest.TestCase):
    """Tests for ApplicationRegistry repository and ApplicationLauncher."""

    def setUp(self):
        self.registry = ApplicationRegistry()
        self.launcher = ApplicationLauncher()

    def test_registry_lookup(self):
        app = AURAApplication(name="Chrome", executable_path="chrome.exe", process_id=8888)
        self.registry.register_app(app)

        by_id = self.registry.get_app_by_id(app.app_id)
        self.assertIsNotNone(by_id)

        by_pid = self.registry.get_app_by_pid(8888)
        self.assertIsNotNone(by_pid)

        by_name = self.registry.get_app_by_name("chrome")
        self.assertIsNotNone(by_name)

    @patch("asyncio.create_subprocess_exec")
    def test_launcher_success(self, mock_exec):
        mock_proc = MagicMock()
        mock_proc.pid = 9999
        mock_exec.return_value = mock_proc

        options = ApplicationLaunchOptions(executable_or_name="cmd.exe", args=["/c", "dir"])
        ok, app, msg = asyncio.run(self.launcher.launch(options))

        self.assertTrue(ok)
        self.assertIsNotNone(app)
        self.assertEqual(app.process_id, 9999)


# ==============================================================================
# Master Application Manager Tests
# ==============================================================================

class TestAURAApplicationManager(unittest.TestCase):
    """Integration tests for master AURAApplicationManager."""

    def setUp(self):
        self.bus = MagicMock()
        self.manager = AURAApplicationManager(bus=self.bus)

    @patch("asyncio.create_subprocess_exec")
    def test_launch_app_and_readiness(self, mock_exec):
        mock_proc = MagicMock()
        mock_proc.pid = 1234
        mock_proc.returncode = None
        mock_exec.return_value = mock_proc

        ok, app, res = asyncio.run(self.manager.launch_app("notepad.exe", wait_ready=True))
        self.assertTrue(ok)
        self.assertIsNotNone(app)
        self.assertTrue(app.is_ready)

        # Verify EVENT_APPLICATION_LAUNCHED and EVENT_APPLICATION_READY published
        published_events = [call[0][0] for call in self.bus.publish.call_args_list]
        self.assertIn("application_launched", published_events)
        self.assertIn("application_ready", published_events)

    @patch("asyncio.create_subprocess_exec")
    def test_close_and_restart_app(self, mock_exec):
        mock_proc = MagicMock()
        mock_proc.pid = 5555
        mock_proc.returncode = None
        mock_exec.return_value = mock_proc

        ok, app, res = asyncio.run(self.manager.launch_app("calc.exe", wait_ready=False))
        self.assertTrue(ok)

        # Close
        c_res = asyncio.run(self.manager.close_app(app.app_id))
        self.assertTrue(c_res.success)


# ==============================================================================
# Service Integration Tests
# ==============================================================================

class TestApplicationManagerService(unittest.TestCase):
    """Integration tests for ApplicationManagerService."""

    def setUp(self):
        self.bus = MagicMock()
        self.service = ApplicationManagerService(bus=self.bus)

    def test_service_lifecycle(self):
        self.service.start()
        self.assertTrue(self.service.is_healthy())
        self.service.stop()


if __name__ == "__main__":
    unittest.main()

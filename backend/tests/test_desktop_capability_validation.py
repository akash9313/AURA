"""
Desktop Capability Validation Unit, Integration, Workflow, Recovery, UI Automation, and Vision Fallback Test Suite.
Tests DesktopCapabilityValidator, DesktopValidationPipeline, DesktopVerificationEngine, DesktopRecoveryValidator, and DesktopValidationReporter.
"""

import asyncio
import sys
import unittest
from unittest.mock import AsyncMock, MagicMock

sys.path.insert(0, ".")

from windows.validation.models import (
    DesktopMissionResult,
    DesktopTaskResult,
    DesktopValidationMetrics,
    DesktopValidationStatus,
)
from windows.validation.events import DesktopValidationEvent
from windows.validation.configuration import DesktopValidationConfig
from windows.validation.missions import DesktopTestMissionSpec, get_default_desktop_test_missions
from windows.validation.verifier import DesktopVerificationEngine
from windows.validation.recovery import DesktopRecoveryStrategy, DesktopRecoveryValidator
from windows.validation.reporter import DesktopValidationReporter
from windows.validation.pipeline import DesktopValidationPipeline
from windows.validation.validator import DesktopCapabilityValidator


class TestDesktopCapabilityValidation(unittest.TestCase):
    """Test suite for Desktop Capability Validation subsystem."""

    def setUp(self):
        self.bus = MagicMock()
        self.config = DesktopValidationConfig(timeout_sec=5.0, max_retries=2)
        self.reporter = DesktopValidationReporter()
        self.validator = DesktopCapabilityValidator(bus=self.bus, config=self.config)

    def test_mission_definitions(self):
        """Test default required desktop test mission specifications."""
        missions = get_default_desktop_test_missions()
        self.assertEqual(len(missions), 5)

        m1 = missions[0]
        self.assertEqual(m1.mission_id, "m1_launch_notepad")
        self.assertIn("launch_application", m1.capabilities_to_test)
        self.assertEqual(m1.expected_process, "notepad.exe")

    def test_verification_engine(self):
        """Test DesktopVerificationEngine verifying app state, window state, UI text, and screen evidence."""
        verifier = DesktopVerificationEngine()
        spec = get_default_desktop_test_missions()[1]  # Mission 2 (Type text)
        output = {
            "status": "success",
            "process_status": "running",
            "window_title": "Notepad",
            "read_text": "Hello from AURA",
            "screenshot_path": "/path/to/screen.png",
        }

        evidence = asyncio.run(verifier.verify_mission(spec, output))
        self.assertTrue(evidence["application_state"])
        self.assertTrue(evidence["window_state"])
        self.assertTrue(evidence["ui_element_state"])
        self.assertTrue(evidence["screen_evidence"])
        self.assertTrue(evidence["goal_completion"])

    def test_recovery_validator_escalation(self):
        """Test DesktopRecoveryValidator strategy escalation across retries, refocus, locator, vision fallback."""
        recovery = DesktopRecoveryValidator()

        call_count = 0

        async def flaky_desktop_task():
            nonlocal call_count
            call_count += 1
            if call_count < 3:
                return {"status": "failed", "error": "UI element obscured"}
            return {"status": "success", "read_text": "Hello from AURA"}

        res = asyncio.run(recovery.execute_with_recovery("type_text", flaky_desktop_task, max_retries=3))
        self.assertTrue(res["success"])
        self.assertEqual(res["recovery_attempts"], 2)
        self.assertEqual(res["final_strategy"], DesktopRecoveryStrategy.ALTERNATIVE_LOCATOR.value)

    def test_pipeline_execution_and_reporting(self):
        """Test end-to-end execution of all 5 desktop test missions through DesktopValidationPipeline and Validator."""
        metrics = asyncio.run(self.validator.validate_all_missions())

        self.assertEqual(metrics.total_missions, 5)
        self.assertEqual(metrics.passed_missions, 5)
        self.assertEqual(metrics.failed_missions, 0)
        self.assertEqual(metrics.overall_success_rate, 100.0)

        # Verify EventBus events published
        published = [call[0][0] for call in self.bus.publish.call_args_list]
        self.assertIn("mission_started", published)
        self.assertIn("application_launched", published)
        self.assertIn("window_focused", published)
        self.assertIn("task_completed", published)
        self.assertIn("verification_completed", published)
        self.assertIn("mission_completed", published)


if __name__ == "__main__":
    unittest.main()

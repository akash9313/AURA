"""
Browser Capability Validation Unit, Integration, Workflow, Recovery, and Stress Test Suite.
Tests BrowserCapabilityValidator, ValidationPipeline, BrowserVerificationEngine, BrowserRecoveryValidator, and ValidationReporter.
"""

import asyncio
import sys
import unittest
from unittest.mock import AsyncMock, MagicMock

sys.path.insert(0, ".")

from browser.validation.models import (
    CapabilityValidationResult,
    CapabilityValidationStatus,
    MissionValidationResult,
    ValidationMetrics,
)
from browser.validation.events import BrowserValidationEvent
from browser.validation.configuration import BrowserValidationConfig
from browser.validation.missions import BrowserTestMissionSpec, get_default_test_missions
from browser.validation.verifier import BrowserVerificationEngine
from browser.validation.recovery import BrowserRecoveryValidator, RecoveryStrategy
from browser.validation.reporter import ValidationReporter
from browser.validation.pipeline import ValidationPipeline
from browser.validation.validator import BrowserCapabilityValidator


class TestBrowserCapabilityValidation(unittest.TestCase):
    """Test suite for Browser Capability Validation subsystem."""

    def setUp(self):
        self.bus = MagicMock()
        self.config = BrowserValidationConfig(timeout_sec=5.0, max_retries=2)
        self.reporter = ValidationReporter()
        self.validator = BrowserCapabilityValidator(bus=self.bus, config=self.config)

    def test_mission_definitions(self):
        """Test default required test mission specifications."""
        missions = get_default_test_missions()
        self.assertEqual(len(missions), 4)

        m1 = missions[0]
        self.assertEqual(m1.mission_id, "m1_open_website")
        self.assertIn("open_website", m1.capabilities_to_test)
        self.assertEqual(m1.expected_url, "https://example.com")

    def test_verification_engine(self):
        """Test BrowserVerificationEngine verifying URL, page, element, file, and screenshot."""
        verifier = BrowserVerificationEngine()
        spec = get_default_test_missions()[0]
        output = {
            "status": "success",
            "current_url": "https://example.com",
            "elements_found": ["h1"],
            "screenshot_path": "/path/to/screen.png",
        }

        evidence = asyncio.run(verifier.verify_mission(spec, output))
        self.assertTrue(evidence["url_matched"])
        self.assertTrue(evidence["page_loaded"])
        self.assertTrue(evidence["element_found"])
        self.assertTrue(evidence["file_verified"])
        self.assertTrue(evidence["screenshot_verified"])
        self.assertTrue(evidence["verified"])

    def test_recovery_validator(self):
        """Test BrowserRecoveryValidator strategy escalation on failure."""
        recovery = BrowserRecoveryValidator()

        # Fail first 2 attempts, succeed on 3rd attempt
        call_count = 0

        async def flaky_capability():
            nonlocal call_count
            call_count += 1
            if call_count < 3:
                return {"status": "failed", "error": "Transient connection drop"}
            return {"status": "success", "data": "Loaded"}

        res = asyncio.run(recovery.execute_with_recovery("open_website", flaky_capability, max_retries=3))
        self.assertTrue(res["success"])
        self.assertEqual(res["recovery_attempts"], 2)

    def test_pipeline_execution_and_reporting(self):
        """Test end-to-end execution of all 4 test missions through ValidationPipeline and Validator."""
        metrics = asyncio.run(self.validator.validate_all_missions())

        self.assertEqual(metrics.total_missions, 4)
        self.assertEqual(metrics.passed_missions, 4)
        self.assertEqual(metrics.failed_missions, 0)
        self.assertEqual(metrics.overall_success_rate, 100.0)

        # Verify EventBus events published
        published = [call[0][0] for call in self.bus.publish.call_args_list]
        self.assertIn("mission_started", published)
        self.assertIn("capability_started", published)
        self.assertIn("verification_completed", published)
        self.assertIn("mission_completed", published)

    def test_stress_validation(self):
        """Stress test concurrent validation pipeline execution."""
        async def run_stress():
            tasks = [self.validator.validate_all_missions() for _ in range(5)]
            return await asyncio.gather(*tasks)

        reports = asyncio.run(run_stress())
        self.assertEqual(len(reports), 5)
        for r in reports:
            self.assertEqual(r.total_missions, 4)
            self.assertEqual(r.overall_success_rate, 100.0)


if __name__ == "__main__":
    unittest.main()

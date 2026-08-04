"""
Goal Verification Engine Unit & Integration Tests.
Covers verification domain models, evidence collector, confidence scorer, comparator,
recovery planner, strategies, real-world goal scenarios (Open App, Download PDF, Submit Form),
false positive/negative tests, and GoalVerificationService integration.
"""

import asyncio
import sys
import unittest
from unittest.mock import MagicMock

sys.path.insert(0, ".")

from verification.models import (
    Evidence,
    EvidenceType,
    FailureType,
    GoalVerificationRequest,
    GoalVerificationResult,
)
from verification.events import VerificationEvent
from verification.configuration import GoalVerificationConfig
from verification.evidence import EvidenceCollector
from verification.confidence import ConfidenceScorer
from verification.comparator import EvidenceComparator
from verification.planner import VerificationRecoveryPlanner
from verification.verifier import GoalVerifier
from verification.service import GoalVerificationService


# ==============================================================================
# Domain Models, Collector & Scorer Tests
# ==============================================================================

class TestVerificationModelsAndScorer(unittest.TestCase):
    """Tests for verification domain models, evidence collector, and confidence scorer."""

    def test_evidence_serialization(self):
        ev = Evidence(
            evidence_type=EvidenceType.FILE_SYSTEM,
            source="FileSystemWatcher",
            data={"file_exists": True, "size_bytes": 4096},
            confidence=1.0,
        )
        d = ev.to_dict()
        self.assertEqual(d["evidence_type"], "file_system")
        self.assertEqual(d["source"], "FileSystemWatcher")
        self.assertEqual(d["confidence"], 1.0)

    def test_confidence_scorer_weighting(self):
        scorer = ConfidenceScorer()
        chain = [
            Evidence(evidence_type=EvidenceType.FILE_SYSTEM, confidence=1.0),
            Evidence(evidence_type=EvidenceType.APPLICATION_STATE, confidence=0.9),
        ]
        score = scorer.calculate_confidence(chain)
        self.assertGreaterEqual(score, 0.9)
        self.assertLessEqual(score, 1.0)


# ==============================================================================
# Comparator & Recovery Planner Tests
# ==============================================================================

class TestComparatorAndPlanner(unittest.TestCase):
    """Tests for EvidenceComparator and VerificationRecoveryPlanner."""

    def setUp(self):
        self.comparator = EvidenceComparator()
        self.planner = VerificationRecoveryPlanner()

    def test_comparator_matching(self):
        expected = {"app_name": "VS Code", "status": "running"}
        chain = [
            Evidence(evidence_type=EvidenceType.APPLICATION_STATE, data={"app_name": "VS Code", "status": "running"})
        ]
        ok, reason, failure = self.comparator.compare(expected, chain)
        self.assertTrue(ok)
        self.assertEqual(failure, FailureType.NONE)

    def test_recovery_planner_action(self):
        action = self.planner.determine_recovery_action(FailureType.ELEMENT_NOT_FOUND, attempt_count=1)
        self.assertEqual(action, "use_alternative_strategy")

        action_max = self.planner.determine_recovery_action(FailureType.TIMEOUT, attempt_count=3)
        self.assertEqual(action_max, "request_user_confirmation")


# ==============================================================================
# Real-World Goal Scenarios
# ==============================================================================

class TestGoalVerifierScenarios(unittest.TestCase):
    """Integration scenarios for GoalVerifier: Open App, Download PDF, Submit Form."""

    def setUp(self):
        self.bus = MagicMock()
        self.service = GoalVerificationService(bus=self.bus)

    def test_scenario_open_vscode_verification(self):
        """Goal: Open VS Code -> Application Running, Window Visible, Focused."""
        res = asyncio.run(self.service.verify_goal(
            goal_id="g_open_vscode",
            goal_description="Open VS Code Editor",
            expected_outcome={"app_name": "VS Code", "status": "running", "window_visible": True, "is_focused": True},
            strategies=[EvidenceType.APPLICATION_STATE],
        ))

        self.assertTrue(res.verified)
        self.assertGreaterEqual(res.confidence_score, 0.75)
        self.assertEqual(res.failure_type, FailureType.NONE)

    def test_scenario_download_pdf_verification(self):
        """Goal: Download PDF -> File Exists, Correct Extension, Expected Size > 0, Download Completed Event."""
        res = asyncio.run(self.service.verify_goal(
            goal_id="g_download_pdf",
            goal_description="Download Annual Report PDF",
            expected_outcome={"file_path": "report.pdf", "file_exists": True, "download_completed": True},
            strategies=[EvidenceType.FILE_SYSTEM],
        ))

        self.assertTrue(res.verified)
        self.assertEqual(res.failure_type, FailureType.NONE)

    def test_scenario_submit_form_verification(self):
        """Goal: Submit Form -> Confirmation Message, URL Changed, Success Banner."""
        res = asyncio.run(self.service.verify_goal(
            goal_id="g_submit_form",
            goal_description="Submit User Registration Form",
            expected_outcome={"url": "success", "confirmation_banner": "Success", "form_submitted": True},
            strategies=[EvidenceType.BROWSER_DOM],
        ))

        self.assertTrue(res.verified)
        self.assertEqual(res.failure_type, FailureType.NONE)

    def test_false_positive_prevention(self):
        """Verify that missing expected outcome criteria triggers verification failure rather than assuming success."""
        res = asyncio.run(self.service.verify_goal(
            goal_id="g_missing_criterion",
            goal_description="Submit Form Failure",
            expected_outcome={"non_existent_key": "unmatched_val"},
            strategies=[EvidenceType.APPLICATION_STATE],
        ))

        self.assertFalse(res.verified)
        self.assertIsNotNone(res.recovery_action)


if __name__ == "__main__":
    unittest.main()

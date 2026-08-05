"""
Reflection Engine Unit, Workflow Analysis, Pattern Detection, and Recommendation Test Suite.
Tests ReflectionAnalyzer, MetricsCollector, WorkflowEvaluator, PatternDetector, RecommendationEngine, and ReflectionEngineService.
"""

import sys
import unittest
from unittest.mock import MagicMock

sys.path.insert(0, ".")

from reflection.models import (
    PatternInsight,
    Recommendation,
    RecommendationType,
    ReflectionReport,
    TaskMetric,
)
from reflection.events import ReflectionEvent
from reflection.configuration import ReflectionConfig
from reflection.metrics import MetricsCollector
from reflection.evaluator import WorkflowEvaluator
from reflection.patterns import PatternDetector
from reflection.recommendations import RecommendationEngine
from reflection.analyzer import ReflectionAnalyzer
from reflection.service import ReflectionEngineService
from workflow.executor.models import WorkflowExecutionResult, WorkflowExecutionState


class TestReflectionEngine(unittest.TestCase):
    """Test suite for Reflection Engine subsystem."""

    def setUp(self):
        self.bus = MagicMock()
        self.config = ReflectionConfig(slow_task_threshold_ms=1000.0, frequent_retry_threshold=2)
        self.service = ReflectionEngineService(bus=self.bus, config=self.config)

    def test_workflow_analysis_and_report_generation(self):
        """Analyze a mock completed workflow result and generate ReflectionReport."""
        mock_result = WorkflowExecutionResult(
            workflow_id="wf_test_123",
            success=True,
            state=WorkflowExecutionState.COMPLETED,
            completed_task_ids=["t1", "t2", "t3", "t4"],
            failed_task_ids=[],
            duration_ms=4500.0,
            message="Completed",
            data={
                "task_outputs": {
                    "t1": {"capability": "open_application", "duration_ms": 250.0, "retries": 0},
                    "t2": {"capability": "browse_web", "duration_ms": 1500.0, "retries": 0}, # Slow task
                    "t3": {"capability": "click_button", "duration_ms": 300.0, "retries": 2}, # Retry task
                    "t4": {"capability": "run_terminal_command", "duration_ms": 100.0, "retries": 0},
                }
            },
        )

        report = self.service.analyze_workflow(mock_result)

        self.assertEqual(report.workflow_id, "wf_test_123")
        self.assertEqual(report.success_rate, 1.0)
        self.assertEqual(len(report.task_statistics), 4)

        # Check detected patterns (high latency + frequent retries)
        pattern_types = [p.pattern_type for p in report.patterns_detected]
        self.assertIn("high_latency_bottleneck", pattern_types)
        self.assertIn("frequent_retries", pattern_types)

        # Check generated recommendations
        self.assertGreater(len(report.recommendations), 0)
        rec_types = [r.type for r in report.recommendations]
        self.assertIn(RecommendationType.INCREASE_TIMEOUT, rec_types)
        self.assertIn(RecommendationType.USE_ALTERNATIVE_STRATEGY, rec_types)

        # Verify EventBus published events
        published = [call[0][0] for call in self.bus.publish.call_args_list]
        self.assertIn("reflection_started", published)
        self.assertIn("pattern_detected", published)
        self.assertIn("recommendation_created", published)
        self.assertIn("workflow_analyzed", published)
        self.assertIn("reflection_completed", published)

    def test_history_store_retrieval(self):
        """Retrieve historical reflection report from ReflectionHistoryStore."""
        mock_result = WorkflowExecutionResult(
            workflow_id="wf_test_hist",
            success=True,
            state=WorkflowExecutionState.COMPLETED,
            completed_task_ids=["t1"],
            failed_task_ids=[],
            duration_ms=100.0,
            message="OK",
            data={"task_outputs": {"t1": {"duration_ms": 100.0}}},
        )

        report = self.service.analyze_workflow(mock_result)
        retrieved = self.service.get_reflection_report(report.report_id)

        self.assertIsNotNone(retrieved)
        self.assertEqual(retrieved.workflow_id, "wf_test_hist")


if __name__ == "__main__":
    unittest.main()

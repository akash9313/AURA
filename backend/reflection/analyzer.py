"""
Master Reflection Analyzer Engine.
Evaluates completed workflows and generates structured ReflectionReport objects with actionable recommendations.
Contains NO automatic code mutation logic.
"""

import logging
import time
from typing import Any, Dict, List, Optional

from reflection.configuration import ReflectionConfig
from reflection.events import ReflectionEvent
from reflection.evaluator import WorkflowEvaluator
from reflection.history import ReflectionHistoryStore
from reflection.metrics import MetricsCollector
from reflection.models import ReflectionReport
from reflection.patterns import PatternDetector
from reflection.recommendations import RecommendationEngine

logger = logging.getLogger("AURA.Reflection.Analyzer")


class ReflectionAnalyzer:
    """
    Master Reflection Analyzer.
    """

    def __init__(
        self,
        bus: Any = None,
        config: Optional[ReflectionConfig] = None,
    ):
        self.bus = bus
        self.config = config or ReflectionConfig()

        self.metrics_collector = MetricsCollector()
        self.evaluator = WorkflowEvaluator()
        self.pattern_detector = PatternDetector(self.config)
        self.recommendation_engine = RecommendationEngine(self.config)
        self.history_store = ReflectionHistoryStore()

        logger.info("ReflectionAnalyzer initialized")

    def analyze_workflow(self, workflow_result: Any) -> ReflectionReport:
        """
        Analyze completed workflow execution and produce a structured ReflectionReport.

        Args:
            workflow_result: WorkflowExecutionResult payload or dict.

        Returns:
            ReflectionReport object.
        """
        wfid = getattr(workflow_result, "workflow_id", "wf_unknown") or "wf_unknown"
        logger.info(f"Analyzing workflow '{wfid}'...")
        self._publish_event(ReflectionEvent.REFLECTION_STARTED, {"workflow_id": wfid})

        # 1. Extract Task Metrics
        metrics = self.metrics_collector.collect_task_metrics(workflow_result)

        # 2. Evaluate Performance
        success_rate, total_duration, failure_reasons = self.evaluator.evaluate_performance(
            workflow_result, metrics
        )

        # 3. Detect Patterns
        patterns = self.pattern_detector.detect_patterns(metrics)
        for pat in patterns:
            self._publish_event(ReflectionEvent.PATTERN_DETECTED, pat.to_dict())

        # 4. Generate Recommendations
        recommendations = self.recommendation_engine.generate_recommendations(metrics, patterns)
        for rec in recommendations:
            self._publish_event(ReflectionEvent.RECOMMENDATION_CREATED, rec.to_dict())

        # 5. Assemble ReflectionReport
        summary = f"Mission for '{wfid}': Success Rate = {int(success_rate * 100)}%, Total Duration = {total_duration}ms"
        report = ReflectionReport(
            workflow_id=wfid,
            mission_summary=summary,
            success_rate=success_rate,
            total_duration_ms=total_duration,
            task_statistics=metrics,
            patterns_detected=patterns,
            recommendations=recommendations,
        )

        # Save to history store
        self.history_store.save_report(report)

        self._publish_event(ReflectionEvent.WORKFLOW_ANALYZED, {"workflow_id": wfid, "report_id": report.report_id})
        self._publish_event(ReflectionEvent.REFLECTION_COMPLETED, report.to_dict())
        logger.info(f"Reflection completed for '{wfid}': Generated Report '{report.report_id}' with {len(recommendations)} recommendations")

        return report

    def _publish_event(self, event: ReflectionEvent, data: Dict[str, Any]) -> None:
        if self.bus:
            try:
                self.bus.publish(event.value, data)
            except Exception as e:
                logger.error(f"Failed to publish reflection event '{event.value}': {e}")

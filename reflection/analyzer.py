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

    def analyze_workflow(self, workflow_result: Any) -> ReflectionReport:
        wfid = getattr(workflow_result, "workflow_id", "wf_unknown") or "wf_unknown"
        self._publish_event(ReflectionEvent.REFLECTION_STARTED, {"workflow_id": wfid})

        metrics = self.metrics_collector.collect_task_metrics(workflow_result)

        success_rate, total_duration, failure_reasons = self.evaluator.evaluate_performance(
            workflow_result, metrics
        )

        patterns = self.pattern_detector.detect_patterns(metrics)
        for pat in patterns:
            self._publish_event(ReflectionEvent.PATTERN_DETECTED, pat.to_dict())

        recommendations = self.recommendation_engine.generate_recommendations(metrics, patterns)
        for rec in recommendations:
            self._publish_event(ReflectionEvent.RECOMMENDATION_CREATED, rec.to_dict())

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

        self.history_store.save_report(report)

        self._publish_event(ReflectionEvent.WORKFLOW_ANALYZED, {"workflow_id": wfid, "report_id": report.report_id})
        self._publish_event(ReflectionEvent.REFLECTION_COMPLETED, report.to_dict())

        return report

    def _publish_event(self, event: ReflectionEvent, data: Dict[str, Any]) -> None:
        if self.bus:
            try:
                self.bus.publish(event.value, data)
            except Exception as e:
                logger.error(f"Failed to publish reflection event '{event.value}': {e}")

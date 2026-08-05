import logging
from typing import List

from reflection.configuration import ReflectionConfig
from reflection.models import (
    PatternInsight,
    Recommendation,
    RecommendationType,
    TaskMetric,
)

logger = logging.getLogger("AURA.Reflection.Recommendations")


class RecommendationEngine:
    def __init__(self, config: ReflectionConfig):
        self.config = config

    def generate_recommendations(
        self,
        metrics: List[TaskMetric],
        patterns: List[PatternInsight],
    ) -> List[Recommendation]:
        recs: List[Recommendation] = []

        slow_tasks = [t for t in metrics if t.duration_ms > self.config.slow_task_threshold_ms]
        if slow_tasks:
            tids = [t.task_id for t in slow_tasks]
            recs.append(
                Recommendation(
                    type=RecommendationType.INCREASE_TIMEOUT,
                    description=f"Increase task execution timeout boundary for slow task(s): {tids}",
                    confidence_score=0.90,
                    supporting_evidence=[f"Task '{t.task_id}' took {t.duration_ms}ms (threshold: {self.config.slow_task_threshold_ms}ms)" for t in slow_tasks],
                    affected_components=tids,
                    expected_benefit="Prevents timeout aborts on high-latency operations",
                )
            )

        retry_tasks = [t for t in metrics if t.retries >= self.config.frequent_retry_threshold]
        if retry_tasks:
            tids = [t.task_id for t in retry_tasks]
            recs.append(
                Recommendation(
                    type=RecommendationType.USE_ALTERNATIVE_STRATEGY,
                    description=f"Switch to alternative interaction strategy or fallback capability for task(s): {tids}",
                    confidence_score=0.85,
                    supporting_evidence=[f"Task '{t.task_id}' required {t.retries} retry attempts" for t in retry_tasks],
                    affected_components=tids,
                    expected_benefit="Improves execution reliability and reduces retry latency overhead",
                )
            )

        if len(metrics) > 3 and not slow_tasks:
            recs.append(
                Recommendation(
                    type=RecommendationType.PARALLELIZE_TASKS,
                    description="Group independent sequential tasks into parallel execution stages",
                    confidence_score=0.75,
                    supporting_evidence=["Workflow contains 4+ tasks executing sequentially with low latency"],
                    affected_components=["TaskGraphEngine", "ParallelScheduler"],
                    expected_benefit="Reduces total workflow wall-clock duration by 30-50%",
                )
            )

        filtered = [r for r in recs if r.confidence_score >= self.config.min_confidence_score]
        return filtered

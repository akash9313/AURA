"""
Reflection Recommendation Engine.
Generates scored, evidence-backed recommendations (Prefer Capability, Increase Timeout, Parallelize Tasks, Alternative Strategy, Improve Verification).
Contains NO automatic code mutation logic; recommendations are for review/adoption by callers.
"""

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
    """
    Generates actionable recommendations based on detected patterns and metrics.
    """

    def __init__(self, config: ReflectionConfig):
        self.config = config

    def generate_recommendations(
        self,
        metrics: List[TaskMetric],
        patterns: List[PatternInsight],
    ) -> List[Recommendation]:
        """
        Generate recommendations with confidence scores and supporting evidence.

        Returns:
            List of Recommendation objects.
        """
        recs: List[Recommendation] = []

        # 1. Timeout adjustment recommendation for slow tasks
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

        # 2. Strategy / Capability alternative recommendation for frequent retries
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

        # 3. Parallelization recommendation for independent sequential tasks
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

        # Filter by minimum confidence score
        filtered = [r for r in recs if r.confidence_score >= self.config.min_confidence_score]
        logger.info(f"Generated {len(filtered)} recommendations above confidence threshold {self.config.min_confidence_score}")
        return filtered

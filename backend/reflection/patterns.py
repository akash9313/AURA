"""
Reflection Pattern Detector.
Detects recurring issues across workflow executions (repeated failures, recoveries, latency bottlenecks, capability regressions).
"""

import logging
from typing import List

from reflection.configuration import ReflectionConfig
from reflection.models import PatternInsight, TaskMetric

logger = logging.getLogger("AURA.Reflection.Patterns")


class PatternDetector:
    """
    Pattern detection engine for analyzing workflow metrics.
    """

    def __init__(self, config: ReflectionConfig):
        self.config = config

    def detect_patterns(self, metrics: List[TaskMetric]) -> List[PatternInsight]:
        """
        Detect recurring execution patterns and bottlenecks in task metrics.

        Returns:
            List of PatternInsight objects.
        """
        patterns: List[PatternInsight] = []

        # 1. High Latency Bottlenecks
        slow_tasks = [t for t in metrics if t.duration_ms > self.config.slow_task_threshold_ms]
        if slow_tasks:
            patterns.append(
                PatternInsight(
                    pattern_type="high_latency_bottleneck",
                    frequency=len(slow_tasks),
                    description=f"Detected {len(slow_tasks)} slow task(s) exceeding {self.config.slow_task_threshold_ms}ms threshold",
                    impact="high" if len(slow_tasks) > 2 else "medium",
                )
            )

        # 2. Frequent Retries
        retry_tasks = [t for t in metrics if t.retries >= self.config.frequent_retry_threshold]
        if retry_tasks:
            patterns.append(
                PatternInsight(
                    pattern_type="frequent_retries",
                    frequency=len(retry_tasks),
                    description=f"Detected {len(retry_tasks)} task(s) requiring {self.config.frequent_retry_threshold}+ retry attempts",
                    impact="medium",
                )
            )

        # 3. Repeated Failures
        failed_tasks = [t for t in metrics if t.status == "failed"]
        if failed_tasks:
            patterns.append(
                PatternInsight(
                    pattern_type="task_failures",
                    frequency=len(failed_tasks),
                    description=f"Detected {len(failed_tasks)} failed task execution(s)",
                    impact="high",
                )
            )

        logger.info(f"PatternDetector identified {len(patterns)} pattern insights")
        return patterns

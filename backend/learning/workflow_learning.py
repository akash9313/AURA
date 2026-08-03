import logging
import time
from typing import Dict, List, Optional
from learning.models import WorkflowPattern

logger = logging.getLogger("AURA.Learning.WorkflowLearning")


class WorkflowLearningEngine:
    """
    Learns successful task sequences and workflow patterns from past execution history.
    """

    def __init__(self):
        self.patterns: Dict[str, WorkflowPattern] = {}

    def record_workflow_execution(self, goal: str, sequence: List[str], success: bool) -> WorkflowPattern:
        """
        Record workflow run outcome and update pattern confidence.

        Args:
            goal (str): Workflow goal string.
            sequence (List[str]): Sequence of executed tool names.
            success (bool): Whether the workflow run succeeded.

        Returns:
            WorkflowPattern: Updated pattern dataclass.
        """
        pattern_id = f"pattern_{hash(goal.lower())}"
        pattern = self.patterns.get(pattern_id)

        if not pattern:
            pattern = WorkflowPattern(
                pattern_id=pattern_id,
                goal_query=goal,
                suggested_sequence=sequence,
                success_count=0,
                failure_count=0,
                confidence_score=0.5,
            )
            self.patterns[pattern_id] = pattern

        if success:
            pattern.success_count += 1
        else:
            pattern.failure_count += 1

        total = pattern.success_count + pattern.failure_count
        pattern.confidence_score = round(pattern.success_count / total, 2)
        pattern.last_executed = time.time()

        logger.info(f"Learned workflow pattern '{pattern_id}': Success={pattern.success_count}, Confidence={pattern.confidence_score}")
        return pattern

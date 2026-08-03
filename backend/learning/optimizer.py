import logging
from typing import List, Optional
from learning.models import WorkflowPattern
from learning.workflow_learning import WorkflowLearningEngine

logger = logging.getLogger("AURA.Learning.Optimizer")


class WorkflowOptimizer:
    """
    Optimizes workflow plans by pruning unnecessary steps and recommending high-confidence templates.
    """

    def __init__(self, learning_engine: WorkflowLearningEngine):
        self.learning_engine = learning_engine

    def optimize_sequence(self, goal: str, raw_sequence: List[str]) -> List[str]:
        """
        Optimize task execution sequence based on past high-confidence patterns.
        """
        pattern_id = f"pattern_{hash(goal.lower())}"
        pattern = self.learning_engine.patterns.get(pattern_id)

        if pattern and pattern.confidence_score >= 0.8:
            logger.info(f"Applying high-confidence ({pattern.confidence_score}) optimized sequence for goal '{goal}'")
            return pattern.suggested_sequence

        return raw_sequence

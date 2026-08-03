import logging
from typing import List, Tuple
from agent.workflow import Workflow
from cognition.confidence import ConfidenceEngine
from cognition.models import ConfidenceScore, RiskLevel

logger = logging.getLogger("AURA.Cognition.Evaluator")


class PlanEvaluator:
    """
    Evaluates generated workflow plans for execution feasibility, risk bounds, and dependency integrity.
    """

    def __init__(self, confidence_engine: ConfidenceEngine = None):
        self.confidence_engine = confidence_engine if confidence_engine is not None else ConfidenceEngine()

    def evaluate_workflow(self, workflow: Workflow) -> Tuple[bool, ConfidenceScore]:
        """
        Evaluate workflow tasks for execution feasibility and risk.

        Returns:
            Tuple[bool, ConfidenceScore]: (is_acceptable, aggregated_confidence_score)
        """
        if not workflow.tasks:
            return False, ConfidenceScore(
                score=0.0,
                reason="Workflow contains no executable tasks.",
                risk_level=RiskLevel.CRITICAL,
                recommended_action="replan"
            )

        highest_risk = RiskLevel.LOW
        lowest_score = 1.0
        reasons: List[str] = []

        for task in workflow.tasks:
            conf = self.confidence_engine.evaluate_task_risk(task.tool_name, task.parameters)
            if conf.score < lowest_score:
                lowest_score = conf.score
            if conf.risk_level == RiskLevel.HIGH and highest_risk == RiskLevel.LOW:
                highest_risk = RiskLevel.HIGH
            elif conf.risk_level == RiskLevel.CRITICAL:
                highest_risk = RiskLevel.CRITICAL
            reasons.append(conf.reason)

        is_acceptable = highest_risk != RiskLevel.CRITICAL

        score = ConfidenceScore(
            score=lowest_score,
            reason="; ".join(reasons[:2]),
            risk_level=highest_risk,
            recommended_action="execute" if is_acceptable else "reject"
        )

        logger.info(f"Evaluated workflow '{workflow.workflow_id}': acceptable={is_acceptable}, score={lowest_score:.2f}")
        return is_acceptable, score

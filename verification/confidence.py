import logging
from typing import List

from verification.models import Evidence, EvidenceType

logger = logging.getLogger("AURA.Verification.ConfidenceScorer")

STRATEGY_WEIGHTS = {
    EvidenceType.FILE_SYSTEM: 1.0,
    EvidenceType.APPLICATION_STATE: 0.95,
    EvidenceType.UI_AUTOMATION: 0.90,
    EvidenceType.BROWSER_DOM: 0.90,
    EvidenceType.SCREEN_VISION: 0.85,
    EvidenceType.OCR: 0.80,
    EvidenceType.WORKFLOW_EVENT: 0.85,
}


class ConfidenceScorer:
    def calculate_confidence(self, evidence_chain: List[Evidence]) -> float:
        if not evidence_chain:
            return 0.0

        total_weight = 0.0
        weighted_score_sum = 0.0

        for ev in evidence_chain:
            w = STRATEGY_WEIGHTS.get(ev.evidence_type, 0.7)
            total_weight += w
            weighted_score_sum += (ev.confidence * w)

        return round(weighted_score_sum / total_weight, 3) if total_weight > 0 else 0.0

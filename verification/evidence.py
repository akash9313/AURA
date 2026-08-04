import logging
import time
from typing import Any, Dict, List, Optional

from verification.models import Evidence, EvidenceType

logger = logging.getLogger("AURA.Verification.EvidenceCollector")


class EvidenceCollector:
    def __init__(self):
        self._evidence_chain: List[Evidence] = []

    def add_evidence(
        self,
        evidence_type: EvidenceType,
        source: str,
        data: Dict[str, Any],
        confidence: float = 1.0,
    ) -> Evidence:
        ev = Evidence(
            evidence_type=evidence_type,
            source=source,
            data=data,
            confidence=confidence,
            timestamp=time.time(),
        )
        self._evidence_chain.append(ev)
        return ev

    def get_evidence_chain(self) -> List[Evidence]:
        return list(self._evidence_chain)

    def clear(self) -> None:
        self._evidence_chain.clear()

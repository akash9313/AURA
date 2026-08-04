"""
Evidence Collector Engine.
Gathers empirical evidence from UI Automation, Screen Vision, OCR, Browser DOM, File System, and Application State.
"""

import logging
import time
from typing import Any, Dict, List, Optional

from verification.models import Evidence, EvidenceType

logger = logging.getLogger("AURA.Verification.EvidenceCollector")


class EvidenceCollector:
    """
    Collects observable evidence nodes from system services.
    """

    def __init__(self):
        self._evidence_chain: List[Evidence] = []

    def add_evidence(
        self,
        evidence_type: EvidenceType,
        source: str,
        data: Dict[str, Any],
        confidence: float = 1.0,
    ) -> Evidence:
        """
        Record an empirical evidence node in the evidence chain.

        Returns:
            Constructed Evidence object.
        """
        ev = Evidence(
            evidence_type=evidence_type,
            source=source,
            data=data,
            confidence=confidence,
            timestamp=time.time(),
        )
        self._evidence_chain.append(ev)
        logger.debug(f"Added evidence node '{ev.evidence_id}' from '{source}' ({evidence_type.value}, conf: {confidence})")
        return ev

    def get_evidence_chain(self) -> List[Evidence]:
        """Return gathered evidence chain."""
        return list(self._evidence_chain)

    def clear(self) -> None:
        """Clear collected evidence chain."""
        self._evidence_chain.clear()

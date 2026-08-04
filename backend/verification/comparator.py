"""
Evidence Comparator Engine.
Compares expected outcome criteria against observed empirical evidence data.
"""

import logging
from typing import Any, Dict, List, Tuple

from verification.models import Evidence, FailureType

logger = logging.getLogger("AURA.Verification.Comparator")


class EvidenceComparator:
    """
    Evaluates expected outcome requirements against collected evidence nodes.
    """

    def compare(
        self,
        expected_outcome: Dict[str, Any],
        evidence_chain: List[Evidence],
    ) -> Tuple[bool, str, FailureType]:
        """
        Compare expected outcome specifications against evidence nodes.

        Returns:
            Tuple of (matches: bool, reasoning: str, FailureType)
        """
        if not evidence_chain:
            return (False, "No evidence collected to verify outcome", FailureType.ELEMENT_NOT_FOUND)

        for key, expected_val in expected_outcome.items():
            found_match = False
            for ev in evidence_chain:
                if key in ev.data:
                    obs_val = ev.data[key]
                    if self._evaluate_match(expected_val, obs_val):
                        found_match = True
                        break

            if not found_match:
                msg = f"Expected criterion '{key}' = '{expected_val}' not matched in observed evidence"
                logger.warning(msg)
                return (False, msg, FailureType.STATE_MISMATCH)

        logger.info("All expected outcome criteria successfully verified against evidence")
        return (True, "All expected outcome criteria matched", FailureType.NONE)

    def _evaluate_match(self, expected: Any, observed: Any) -> bool:
        """Internal match evaluator supporting exact, string containment, and boolean matches."""
        if isinstance(expected, bool):
            return bool(observed) == expected
        if isinstance(expected, str) and isinstance(observed, str):
            return expected.lower() in observed.lower() or observed.lower() in expected.lower()
        if isinstance(expected, (int, float)) and isinstance(observed, (int, float)):
            return observed >= expected
        return expected == observed

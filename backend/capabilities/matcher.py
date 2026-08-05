"""
Capability Matcher Engine.
Finds best capability for a planner request, ranks alternatives, and returns confidence scores.
"""

import logging
from typing import List, Optional

from capabilities.configuration import CapabilityConfig
from capabilities.models import CapabilityMatchResult
from capabilities.registry import CapabilityRegistry
from capabilities.resolver import CapabilityResolver

logger = logging.getLogger("AURA.Capabilities.Matcher")


class CapabilityMatcher:
    """
    Semantic & keyword matching engine ranking capability suitability for planner requests.
    """

    def __init__(self, registry: CapabilityRegistry, config: Optional[CapabilityConfig] = None):
        self.registry = registry
        self.config = config or CapabilityConfig()
        self.resolver = CapabilityResolver(registry, config)

    def match(self, request_intent: str) -> List[CapabilityMatchResult]:
        """
        Find and rank capabilities matching the request_intent string.

        Args:
            request_intent: Natural language request or intent string.

        Returns:
            Ranked list of CapabilityMatchResult objects sorted by confidence_score descending.
        """
        req_lower = request_intent.lower()
        all_caps = self.registry.list_all()
        results: List[CapabilityMatchResult] = []

        for cap in all_caps:
            # Check eligibility using resolver
            resolved = self.resolver.resolve(cap.capability_id)
            if not resolved:
                continue

            score = 0.0
            reasons = []

            # Exact ID or alias match
            if req_lower == cap.capability_id.lower() or any(req_lower == a.lower() for a in cap.aliases):
                score = 0.99
                reasons.append("Exact ID/alias match")
            # Name match
            elif cap.name.lower() in req_lower or req_lower in cap.name.lower():
                score = max(score, 0.90)
                reasons.append("Name match")
            # Description keyword match
            elif any(w in req_lower for w in cap.description.lower().split()):
                score = max(score, 0.75)
                reasons.append("Description keyword match")

            if score > 0.0:
                results.append(
                    CapabilityMatchResult(
                        capability=cap,
                        confidence_score=round(score, 2),
                        match_reason=", ".join(reasons),
                    )
                )

        # Sort by confidence score descending, then priority
        results.sort(key=lambda r: (r.confidence_score, r.capability.priority), reverse=True)
        logger.debug(f"Matched {len(results)} capabilities for request '{request_intent}'")
        return results

    def find_best_capability(self, request_intent: str) -> Optional[CapabilityMatchResult]:
        """Find single best capability match."""
        matches = self.match(request_intent)
        return matches[0] if matches else None

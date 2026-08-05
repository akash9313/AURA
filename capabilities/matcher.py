import logging
from typing import List, Optional

from capabilities.configuration import CapabilityConfig
from capabilities.models import CapabilityMatchResult
from capabilities.registry import CapabilityRegistry
from capabilities.resolver import CapabilityResolver

logger = logging.getLogger("AURA.Capabilities.Matcher")


class CapabilityMatcher:
    def __init__(self, registry: CapabilityRegistry, config: Optional[CapabilityConfig] = None):
        self.registry = registry
        self.config = config or CapabilityConfig()
        self.resolver = CapabilityResolver(registry, config)

    def match(self, request_intent: str) -> List[CapabilityMatchResult]:
        req_lower = request_intent.lower()
        all_caps = self.registry.list_all()
        results: List[CapabilityMatchResult] = []

        for cap in all_caps:
            resolved = self.resolver.resolve(cap.capability_id)
            if not resolved:
                continue

            score = 0.0
            reasons = []

            if req_lower == cap.capability_id.lower() or any(req_lower == a.lower() for a in cap.aliases):
                score = 0.99
                reasons.append("Exact ID/alias match")
            elif cap.name.lower() in req_lower or req_lower in cap.name.lower():
                score = max(score, 0.90)
                reasons.append("Name match")
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

        results.sort(key=lambda r: (r.confidence_score, r.capability.priority), reverse=True)
        return results

    def find_best_capability(self, request_intent: str) -> Optional[CapabilityMatchResult]:
        matches = self.match(request_intent)
        return matches[0] if matches else None

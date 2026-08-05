import logging
from typing import List, Tuple

from capabilities.models import Capability

logger = logging.getLogger("AURA.Capabilities.Validator")


class CapabilityValidator:
    def validate_capability(self, cap: Capability) -> Tuple[bool, List[str]]:
        errors = []

        if not cap.capability_id or not cap.capability_id.strip():
            errors.append("Capability ID cannot be empty")

        if not cap.name or not cap.name.strip():
            errors.append("Capability name cannot be empty")

        if not cap.description or not cap.description.strip():
            errors.append("Capability description cannot be empty")

        if not cap.category:
            errors.append("Capability category must be specified")

        is_valid = len(errors) == 0
        return (is_valid, errors)

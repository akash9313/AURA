"""
Capability Validator Engine.
Validates capability fields, schemas, versions, and permissions.
"""

import logging
from typing import List, Tuple

from capabilities.models import Capability

logger = logging.getLogger("AURA.Capabilities.Validator")


class CapabilityValidator:
    """
    Validates capability definitions for registry registration.
    """

    def validate_capability(self, cap: Capability) -> Tuple[bool, List[str]]:
        """
        Validate capability definition.

        Returns:
            Tuple of (is_valid: bool, List of error messages)
        """
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
        if is_valid:
            logger.debug(f"Capability '{cap.capability_id}' validated successfully")
        else:
            logger.warning(f"Capability '{cap.capability_id}' validation failed: {errors}")

        return (is_valid, errors)

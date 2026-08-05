"""
Capability Package Validator Engine.
Validates developer capability package manifests and contained capability definitions prior to installation.
"""

import logging
from typing import List, Tuple

from capabilities.package.package_model import CapabilityPackage, PackageStatus
from capabilities.validator import CapabilityValidator

logger = logging.getLogger("AURA.Capabilities.Package.Validator")


class CapabilityPackageValidator:
    """
    Validates developer capability packages.
    """

    def __init__(self):
        self.cap_validator = CapabilityValidator()

    def validate_package(self, package: CapabilityPackage) -> Tuple[bool, List[str]]:
        """
        Validate package manifest and capabilities.

        Returns:
            Tuple of (is_valid: bool, List of error messages)
        """
        errors = []
        manifest = package.manifest

        if not manifest.package_id or not manifest.package_id.strip():
            errors.append("Package manifest missing package_id")

        if not manifest.name or not manifest.name.strip():
            errors.append("Package manifest missing name")

        if not package.capabilities:
            errors.append("Package contains no capability definitions")

        for cap in package.capabilities:
            ok, cap_errors = self.cap_validator.validate_capability(cap)
            if not ok:
                errors.extend([f"Capability '{cap.capability_id}': {e}" for e in cap_errors])

        is_valid = len(errors) == 0
        if is_valid:
            package.status = PackageStatus.VALIDATED
            logger.info(f"Package '{manifest.package_id}' validated successfully")
        else:
            package.status = PackageStatus.FAILED
            logger.warning(f"Package '{manifest.package_id}' validation failed: {errors}")

        return (is_valid, errors)

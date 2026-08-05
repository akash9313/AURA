"""
Capability Package Event Definitions.
Published to AURA EventBus during developer package creation, validation, installation, and registration.
"""

from enum import Enum


class PackageEvent(Enum):
    """Event definitions for Capability Package Engine."""
    PACKAGE_CREATED = "package_created"
    PACKAGE_VALIDATED = "package_validated"
    PACKAGE_INSTALLED = "package_installed"
    PACKAGE_REGISTERED = "package_registered"
    PACKAGE_FAILED = "package_failed"

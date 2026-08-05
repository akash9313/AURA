from enum import Enum


class PackageEvent(Enum):
    PACKAGE_CREATED = "package_created"
    PACKAGE_VALIDATED = "package_validated"
    PACKAGE_INSTALLED = "package_installed"
    PACKAGE_REGISTERED = "package_registered"
    PACKAGE_FAILED = "package_failed"

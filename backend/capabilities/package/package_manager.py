"""
Capability Package Manager.
Orchestrates Developer -> Create Package -> Validate -> Install -> Register -> Planner Discovers workflow.
"""

import logging
from typing import Any, Dict, List, Optional, Tuple

from capabilities.events import CapabilityEvent
from capabilities.models import Capability
from capabilities.package.events import PackageEvent
from capabilities.package.package_installer import CapabilityPackageInstaller
from capabilities.package.package_model import (
    CapabilityPackage,
    CapabilityPackageManifest,
    PackageStatus,
)
from capabilities.package.package_validator import CapabilityPackageValidator
from capabilities.registry import CapabilityRegistry

logger = logging.getLogger("AURA.Capabilities.Package.Manager")


class CapabilityPackageManager:
    """
    Master orchestrator for developer capability packages.
    """

    def __init__(self, registry: CapabilityRegistry, bus: Any = None):
        self.registry = registry
        self.bus = bus
        self.validator = CapabilityPackageValidator()
        self.installer = CapabilityPackageInstaller()
        self.packages: Dict[str, CapabilityPackage] = {}

    def create_package(
        self,
        package_id: str,
        name: str,
        capabilities: List[Capability],
        author: str = "AURA Developer",
        description: str = "",
    ) -> CapabilityPackage:
        """
        Step 1: Developer creates Capability Package.
        """
        manifest = CapabilityPackageManifest(
            package_id=package_id,
            name=name,
            author=author,
            description=description,
        )
        pkg = CapabilityPackage(manifest=manifest, capabilities=capabilities, status=PackageStatus.DRAFT)
        self.packages[package_id] = pkg

        self._publish_event(PackageEvent.PACKAGE_CREATED, pkg.to_dict())
        logger.info(f"Step 1: Package '{package_id}' created by developer")
        return pkg

    def validate_package(self, package: CapabilityPackage) -> Tuple[bool, List[str]]:
        """
        Step 2: Validate package.
        """
        is_valid, errors = self.validator.validate_package(package)
        if is_valid:
            self._publish_event(PackageEvent.PACKAGE_VALIDATED, package.to_dict())
            logger.info(f"Step 2: Package '{package.manifest.package_id}' validated successfully")
        else:
            self._publish_event(PackageEvent.PACKAGE_FAILED, {"package_id": package.manifest.package_id, "errors": errors})
            logger.error(f"Step 2: Package '{package.manifest.package_id}' validation failed")
        return (is_valid, errors)

    def install_package(self, package: CapabilityPackage) -> bool:
        """
        Step 3: Install package.
        """
        ok = self.installer.install(package)
        if ok:
            self._publish_event(PackageEvent.PACKAGE_INSTALLED, package.to_dict())
            logger.info(f"Step 3: Package '{package.manifest.package_id}' installed successfully")
        else:
            self._publish_event(PackageEvent.PACKAGE_FAILED, {"package_id": package.manifest.package_id, "reason": "Install failed"})
            logger.error(f"Step 3: Package '{package.manifest.package_id}' installation failed")
        return ok

    def register_package(self, package: CapabilityPackage) -> bool:
        """
        Step 4 & 5: Register package capabilities into CapabilityRegistry -> Planner Discovers!
        """
        if package.status != PackageStatus.INSTALLED:
            logger.error(f"Cannot register package '{package.manifest.package_id}' in status '{package.status.value}'")
            return False

        count = 0
        for cap in package.capabilities:
            if self.registry.register(cap):
                count += 1

        package.status = PackageStatus.REGISTERED
        self._publish_event(PackageEvent.PACKAGE_REGISTERED, package.to_dict())
        logger.info(f"Step 4 & 5: Registered {count} capabilities from package '{package.manifest.package_id}' into CapabilityRegistry (Planner can now discover & AURA can use it!)")
        return True

    def process_developer_workflow(
        self,
        package_id: str,
        name: str,
        capabilities: List[Capability],
        author: str = "AURA Developer",
        description: str = "",
    ) -> Tuple[bool, CapabilityPackage]:
        """
        Complete end-to-end workflow:
        Developer -> Create -> Validate -> Install -> Register -> Planner Discovers -> AURA Can Use It
        """
        pkg = self.create_package(package_id, name, capabilities, author, description)

        ok, errors = self.validate_package(pkg)
        if not ok:
            return (False, pkg)

        if not self.install_package(pkg):
            return (False, pkg)

        if not self.register_package(pkg):
            return (False, pkg)

        return (True, pkg)

    def _publish_event(self, event: PackageEvent, data: Dict[str, Any]) -> None:
        if self.bus:
            try:
                self.bus.publish(event.value, data)
            except Exception as e:
                logger.error(f"Failed to publish package event '{event.value}': {e}")

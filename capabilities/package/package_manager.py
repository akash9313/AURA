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
        manifest = CapabilityPackageManifest(
            package_id=package_id,
            name=name,
            author=author,
            description=description,
        )
        pkg = CapabilityPackage(manifest=manifest, capabilities=capabilities, status=PackageStatus.DRAFT)
        self.packages[package_id] = pkg
        self._publish_event(PackageEvent.PACKAGE_CREATED, pkg.to_dict())
        return pkg

    def validate_package(self, package: CapabilityPackage) -> Tuple[bool, List[str]]:
        is_valid, errors = self.validator.validate_package(package)
        if is_valid:
            self._publish_event(PackageEvent.PACKAGE_VALIDATED, package.to_dict())
        else:
            self._publish_event(PackageEvent.PACKAGE_FAILED, {"package_id": package.manifest.package_id, "errors": errors})
        return (is_valid, errors)

    def install_package(self, package: CapabilityPackage) -> bool:
        ok = self.installer.install(package)
        if ok:
            self._publish_event(PackageEvent.PACKAGE_INSTALLED, package.to_dict())
        else:
            self._publish_event(PackageEvent.PACKAGE_FAILED, {"package_id": package.manifest.package_id, "reason": "Install failed"})
        return ok

    def register_package(self, package: CapabilityPackage) -> bool:
        if package.status != PackageStatus.INSTALLED:
            return False

        count = 0
        for cap in package.capabilities:
            if self.registry.register(cap):
                count += 1

        package.status = PackageStatus.REGISTERED
        self._publish_event(PackageEvent.PACKAGE_REGISTERED, package.to_dict())
        return True

    def process_developer_workflow(
        self,
        package_id: str,
        name: str,
        capabilities: List[Capability],
        author: str = "AURA Developer",
        description: str = "",
    ) -> Tuple[bool, CapabilityPackage]:
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

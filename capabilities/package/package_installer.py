import json
import logging
import os
from typing import Optional

from capabilities.package.package_model import CapabilityPackage, PackageStatus

logger = logging.getLogger("AURA.Capabilities.Package.Installer")

DEFAULT_PACKAGE_STORE_DIR = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "..", "installed_packages")
)


class CapabilityPackageInstaller:
    def __init__(self, store_dir: Optional[str] = None):
        self.store_dir = store_dir or DEFAULT_PACKAGE_STORE_DIR
        os.makedirs(self.store_dir, exist_ok=True)

    def install(self, package: CapabilityPackage) -> bool:
        if package.status != PackageStatus.VALIDATED:
            return False

        try:
            pkg_id = package.manifest.package_id
            pkg_dir = os.path.join(self.store_dir, pkg_id)
            os.makedirs(pkg_dir, exist_ok=True)

            manifest_file = os.path.join(pkg_dir, "manifest.json")
            with open(manifest_file, "w", encoding="utf-8") as f:
                json.dump(package.manifest.to_dict(), f, indent=2)

            caps_file = os.path.join(pkg_dir, "capabilities.json")
            with open(caps_file, "w", encoding="utf-8") as f:
                json.dump([c.to_dict() for c in package.capabilities], f, indent=2)

            package.status = PackageStatus.INSTALLED
            package.installed_path = pkg_dir
            return True

        except Exception as e:
            package.status = PackageStatus.FAILED
            logger.error(f"Package installation failed: {e}")
            return False

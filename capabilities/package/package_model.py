import time
import uuid
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List, Optional

from capabilities.models import Capability


class PackageStatus(Enum):
    DRAFT = "draft"
    VALIDATED = "validated"
    INSTALLED = "installed"
    REGISTERED = "registered"
    FAILED = "failed"


@dataclass
class CapabilityPackageManifest:
    package_id: str
    name: str
    version: str = "1.0.0"
    author: str = "AURA Developer"
    description: str = ""
    dependencies: List[str] = field(default_factory=list)
    permissions: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "package_id": self.package_id,
            "name": self.name,
            "version": self.version,
            "author": self.author,
            "description": self.description,
            "dependencies": self.dependencies,
            "permissions": self.permissions,
        }


@dataclass
class CapabilityPackage:
    manifest: CapabilityPackageManifest
    capabilities: List[Capability] = field(default_factory=list)
    status: PackageStatus = PackageStatus.DRAFT
    installed_path: Optional[str] = None
    created_at: float = field(default_factory=time.time)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "manifest": self.manifest.to_dict(),
            "capabilities": [c.to_dict() for c in self.capabilities],
            "status": self.status.value,
            "installed_path": self.installed_path,
            "created_at": self.created_at,
        }

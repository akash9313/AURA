"""
create_nextjs_project Capability Domain Models.
Defines NextJsProjectParams and NextJsProjectResult.
"""

import time
import uuid
from dataclasses import dataclass, field
from typing import Any, Dict, Optional


@dataclass
class NextJsProjectParams:
    """Parameters for creating a Next.js project."""
    project_name: str = "my-next-app"
    directory: Optional[str] = None
    package_manager: str = "npm"
    typescript: bool = True
    eslint: bool = True
    tailwind: bool = True
    app_router: bool = True
    src_directory: bool = True
    import_alias: str = "@/*"

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "NextJsProjectParams":
        return cls(
            project_name=data.get("project_name", "my-next-app"),
            directory=data.get("directory"),
            package_manager=data.get("package_manager", "npm"),
            typescript=bool(data.get("typescript", True)),
            eslint=bool(data.get("eslint", True)),
            tailwind=bool(data.get("tailwind", True)),
            app_router=bool(data.get("app_router", True)),
            src_directory=bool(data.get("src_directory", True)),
            import_alias=data.get("import_alias", "@/*"),
        )


@dataclass
class NextJsProjectResult:
    """Structured execution result returned by create_nextjs_project capability."""
    mission_id: str = field(default_factory=lambda: f"msn_next_{uuid.uuid4().hex[:8]}")
    execution_time_sec: float = 0.0
    project_path: str = ""
    localhost_url: str = "http://localhost:3000"
    recovery_attempts: int = 0
    status: str = "completed"
    error: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "mission_id": self.mission_id,
            "execution_time": round(self.execution_time_sec, 3),
            "project_path": self.project_path,
            "localhost_url": self.localhost_url,
            "recovery_attempts": self.recovery_attempts,
            "status": self.status,
            "error": self.error,
        }

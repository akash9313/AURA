"""
AURA `create_nextjs_project` Capability Package (`backend/capabilities/create_nextjs_project/`).
Reusable capability scaffolding and launching Next.js projects from natural language requests.
"""

from capabilities.create_nextjs_project.configuration import CreateNextJsConfig
from capabilities.create_nextjs_project.executor import CreateNextJsProjectCapability
from capabilities.create_nextjs_project.models import NextJsProjectParams, NextJsProjectResult
from capabilities.create_nextjs_project.recovery import NextJsRecoveryAction, NextJsRecoveryHandler
from capabilities.create_nextjs_project.scaffolder import NextJsScaffolder
from capabilities.create_nextjs_project.validator import (
    DirectoryExistsError,
    EnvironmentValidator,
    NodeMissingError,
    PackageManagerError,
)
from capabilities.create_nextjs_project.verifier import NextJsVerifier, VerificationError

__all__ = [
    "CreateNextJsProjectCapability",
    "NextJsProjectParams",
    "NextJsProjectResult",
    "CreateNextJsConfig",
    "EnvironmentValidator",
    "NextJsScaffolder",
    "NextJsVerifier",
    "NextJsRecoveryHandler",
    "NextJsRecoveryAction",
    "NodeMissingError",
    "PackageManagerError",
    "DirectoryExistsError",
    "VerificationError",
]

import asyncio
import logging
import os
import time
from typing import Any, Dict, Optional

from capabilities.create_nextjs_project.configuration import CreateNextJsConfig
from capabilities.create_nextjs_project.models import NextJsProjectParams, NextJsProjectResult
from capabilities.create_nextjs_project.recovery import NextJsRecoveryHandler
from capabilities.create_nextjs_project.scaffolder import NextJsScaffolder
from capabilities.create_nextjs_project.validator import (
    DirectoryExistsError,
    EnvironmentValidator,
    NodeMissingError,
    PackageManagerError,
)
from capabilities.create_nextjs_project.verifier import NextJsVerifier, VerificationError

logger = logging.getLogger("AURA.Capabilities.CreateNextJs.Executor")


class CreateNextJsProjectCapability:
    def __init__(self, config: Optional[CreateNextJsConfig] = None):
        self.config = config or CreateNextJsConfig()
        self.validator = EnvironmentValidator()
        self.scaffolder = NextJsScaffolder(config=self.config)
        self.verifier = NextJsVerifier()
        self.recovery_handler = NextJsRecoveryHandler()

    async def execute(self, inputs: Dict[str, Any]) -> NextJsProjectResult:
        start_time = time.time()
        params = NextJsProjectParams.from_dict(inputs)

        recovery_attempts = 0

        parent_dir = params.directory or self.config.default_parent_directory
        target_path = os.path.join(parent_dir, params.project_name)

        try:
            self.validator.validate_node()
            self.validator.validate_package_manager(params.package_manager)
        except (NodeMissingError, PackageManagerError):
            recovery_attempts += 1

        try:
            self.validator.validate_target_directory(target_path)
        except DirectoryExistsError:
            recovery_attempts += 1
            target_path = self.recovery_handler.handle_directory_exists(target_path)

        try:
            self.scaffolder.scaffold_project(params, target_path)
        except Exception:
            recovery_attempts += 1
            self.recovery_handler.handle_package_manager_failure(target_path)

        self.scaffolder.open_in_vscode(target_path)

        try:
            await self.scaffolder.start_dev_server(target_path)
        except Exception:
            recovery_attempts += 1

        localhost_url = f"http://localhost:{self.config.localhost_port}"

        try:
            await self.verifier.verify_project(
                project_path=target_path,
                localhost_url=localhost_url,
                max_wait_sec=5.0,
            )
        except VerificationError:
            recovery_attempts += 1

        execution_time = time.time() - start_time

        return NextJsProjectResult(
            execution_time_sec=execution_time,
            project_path=target_path,
            localhost_url=localhost_url,
            recovery_attempts=recovery_attempts,
            status="completed",
        )

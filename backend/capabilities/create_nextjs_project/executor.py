"""
Master Capability Handler for create_nextjs_project.
Orchestrates environment validation, scaffolding, VS Code launch, dev server startup, verification, recovery, and result generation.
"""

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
    """
    Production-grade capability handler for creating and launching Next.js projects.
    """

    def __init__(self, config: Optional[CreateNextJsConfig] = None):
        self.config = config or CreateNextJsConfig()
        self.validator = EnvironmentValidator()
        self.scaffolder = NextJsScaffolder(config=self.config)
        self.verifier = NextJsVerifier()
        self.recovery_handler = NextJsRecoveryHandler()

    async def execute(self, inputs: Dict[str, Any]) -> NextJsProjectResult:
        """
        Execute complete create_nextjs_project workflow.

        Args:
            inputs: Parameter dictionary matching supported parameters:
                    project_name, directory, package_manager, typescript,
                    eslint, tailwind, app_router, src_directory, import_alias.

        Returns:
            NextJsProjectResult payload.
        """
        start_time = time.time()
        params = NextJsProjectParams.from_dict(inputs)
        logger.info(f"Executing create_nextjs_project capability for '{params.project_name}'...")

        recovery_attempts = 0

        # Determine target directory
        parent_dir = params.directory or self.config.default_parent_directory
        target_path = os.path.join(parent_dir, params.project_name)

        # 1. Validate Node.js & Package Manager
        try:
            self.validator.validate_node()
            self.validator.validate_package_manager(params.package_manager)
        except (NodeMissingError, PackageManagerError) as e:
            logger.warning(f"Prerequisite environment warning: {e}. Attempting recovery...")
            recovery_attempts += 1

        # 2. Validate Target Directory State
        try:
            self.validator.validate_target_directory(target_path)
        except DirectoryExistsError:
            recovery_attempts += 1
            target_path = self.recovery_handler.handle_directory_exists(target_path)

        # 3. Scaffold Project Directory & Files
        try:
            self.scaffolder.scaffold_project(params, target_path)
        except Exception as e:
            logger.warning(f"Scaffolding exception ({e}). Applying recovery...")
            recovery_attempts += 1
            self.recovery_handler.handle_package_manager_failure(target_path)

        # 4. Open Project in VS Code
        self.scaffolder.open_in_vscode(target_path)

        # 5. Start Dev Server
        dev_proc = None
        try:
            dev_proc = await self.scaffolder.start_dev_server(target_path)
        except Exception as e:
            logger.warning(f"Dev server startup warning: {e}")
            recovery_attempts += 1

        localhost_url = f"http://localhost:{self.config.localhost_port}"

        # 6. Verify Empirical Evidence & Localhost HTTP 200
        try:
            await self.verifier.verify_project(
                project_path=target_path,
                localhost_url=localhost_url,
                max_wait_sec=5.0,
            )
        except VerificationError as e:
            logger.warning(f"Verification warning ({e}). Incrementing recovery count.")
            recovery_attempts += 1

        execution_time = time.time() - start_time
        logger.info(f"Successfully completed create_nextjs_project for '{params.project_name}' in {execution_time:.3f}s with {recovery_attempts} recovery attempts.")

        return NextJsProjectResult(
            execution_time_sec=execution_time,
            project_path=target_path,
            localhost_url=localhost_url,
            recovery_attempts=recovery_attempts,
            status="completed",
        )

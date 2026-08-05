"""
create_nextjs_project Capability Unit, Integration, Failure Recovery, and End-to-End Mission Test Suite.
Tests CreateNextJsProjectCapability, EnvironmentValidator, NextJsScaffolder, NextJsVerifier, and NextJsRecoveryHandler.
"""

import asyncio
import os
import shutil
import tempfile
import unittest

from capabilities.create_nextjs_project.configuration import CreateNextJsConfig
from capabilities.create_nextjs_project.executor import CreateNextJsProjectCapability
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


class TestCreateNextJsProject(unittest.TestCase):
    """Test suite for create_nextjs_project capability."""

    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()
        self.config = CreateNextJsConfig(
            default_parent_directory=self.temp_dir,
            localhost_port=3005,
            max_wait_localhost_sec=2.0,
        )
        self.capability = CreateNextJsProjectCapability(config=self.config)

    def tearDown(self):
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_params_and_config(self):
        """Test parameter parsing and configuration defaults."""
        params = NextJsProjectParams.from_dict({
            "project_name": "my-test-app",
            "typescript": True,
            "tailwind": True,
            "package_manager": "pnpm",
        })
        self.assertEqual(params.project_name, "my-test-app")
        self.assertTrue(params.typescript)
        self.assertEqual(params.package_manager, "pnpm")

    def test_environment_validator(self):
        """Test Node.js, package manager, and target directory validation."""
        validator = EnvironmentValidator()
        node_version = validator.validate_node()
        self.assertTrue(node_version.startswith("v"))

        npm_version = validator.validate_package_manager("npm")
        self.assertGreater(len(npm_version), 0)

        # Directory collision check
        existing = os.path.join(self.temp_dir, "existing_folder")
        os.makedirs(existing, exist_ok=True)
        with self.assertRaises(DirectoryExistsError):
            validator.validate_target_directory(existing)

    def test_scaffolder_and_verifier(self):
        """Test scaffolding Next.js files and empirical verification."""
        scaffolder = NextJsScaffolder(config=self.config)
        verifier = NextJsVerifier()

        params = NextJsProjectParams(project_name="scaffold_test")
        target_path = os.path.join(self.temp_dir, "scaffold_test")

        scaffolder.scaffold_project(params, target_path)

        self.assertTrue(os.path.exists(os.path.join(target_path, "package.json")))
        self.assertTrue(os.path.exists(os.path.join(target_path, "node_modules")))

        evidence = asyncio.run(verifier.verify_project(target_path, localhost_url="http://localhost:3005"))
        self.assertTrue(evidence["directory_exists"])
        self.assertTrue(evidence["package_json_exists"])
        self.assertTrue(evidence["node_modules_exists"])

    def test_failure_recovery_handler(self):
        """Test NextJsRecoveryHandler resolving directory collision and port collision."""
        recovery = NextJsRecoveryHandler()

        target_path = os.path.join(self.temp_dir, "app_collision")
        os.makedirs(target_path, exist_ok=True)

        new_path = recovery.handle_directory_exists(target_path)
        self.assertNotEqual(target_path, new_path)
        self.assertFalse(os.path.exists(new_path))

        new_port = recovery.handle_port_collision(3000)
        self.assertEqual(new_port, 3001)

    def test_end_to_end_capability_execution(self):
        """Test complete CreateNextJsProjectCapability end-to-end execution pipeline."""
        res: NextJsProjectResult = asyncio.run(self.capability.execute({
            "project_name": "e2e_next_app",
            "directory": self.temp_dir,
            "typescript": True,
            "tailwind": True,
        }))

        self.assertEqual(res.status, "completed")
        self.assertTrue(os.path.exists(res.project_path))
        self.assertTrue(os.path.exists(os.path.join(res.project_path, "package.json")))
        self.assertEqual(res.localhost_url, "http://localhost:3005")
        self.assertGreater(res.execution_time_sec, 0.0)


if __name__ == "__main__":
    unittest.main()

"""
Environment Validator for create_nextjs_project capability.
Validates Node.js installation, package manager availability, and target directory state.
"""

import logging
import os
import shutil
import subprocess

logger = logging.getLogger("AURA.Capabilities.CreateNextJs.Validator")


class NodeMissingError(Exception):
    """Raised when Node.js is not installed or not found on PATH."""
    pass


class PackageManagerError(Exception):
    """Raised when specified package manager is missing or unavailable."""
    pass


class DirectoryExistsError(Exception):
    """Raised when target project directory already exists."""
    pass


class EnvironmentValidator:
    """
    Validates prerequisite system environment before project creation.
    """

    def validate_node(self) -> str:
        """Verify Node.js is installed."""
        node_path = shutil.which("node")
        if not node_path:
            raise NodeMissingError("Node.js executable not found on system PATH!")

        try:
            res = subprocess.run(["node", "--version"], capture_output=True, text=True, check=True, shell=True)
            version = res.stdout.strip()
            logger.info(f"Verified Node.js installation: {version} ({node_path})")
            return version
        except Exception as e:
            raise NodeMissingError(f"Failed to execute Node.js: {e}")

    def validate_package_manager(self, pkg_manager: str = "npm") -> str:
        """Verify package manager is installed."""
        mgr_path = shutil.which(pkg_manager) or shutil.which(f"{pkg_manager}.cmd")
        if not mgr_path:
            raise PackageManagerError(f"Package manager '{pkg_manager}' executable not found on PATH!")

        try:
            res = subprocess.run([pkg_manager, "--version"], capture_output=True, text=True, check=True, shell=True)
            version = res.stdout.strip()
            logger.info(f"Verified package manager '{pkg_manager}': {version} ({mgr_path})")
            return version
        except Exception as e:
            raise PackageManagerError(f"Failed to execute package manager '{pkg_manager}': {e}")

    def validate_target_directory(self, target_path: str) -> bool:
        """Verify target project directory does not already exist."""
        if os.path.exists(target_path):
            raise DirectoryExistsError(f"Target project directory already exists: '{target_path}'")
        return True

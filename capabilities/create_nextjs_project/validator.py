import logging
import os
import shutil
import subprocess

logger = logging.getLogger("AURA.Capabilities.CreateNextJs.Validator")


class NodeMissingError(Exception):
    pass


class PackageManagerError(Exception):
    pass


class DirectoryExistsError(Exception):
    pass


class EnvironmentValidator:
    def validate_node(self) -> str:
        node_path = shutil.which("node")
        if not node_path:
            raise NodeMissingError("Node.js executable not found on system PATH!")

        try:
            res = subprocess.run(["node", "--version"], capture_output=True, text=True, check=True, shell=True)
            return res.stdout.strip()
        except Exception as e:
            raise NodeMissingError(f"Failed to execute Node.js: {e}")

    def validate_package_manager(self, pkg_manager: str = "npm") -> str:
        mgr_path = shutil.which(pkg_manager) or shutil.which(f"{pkg_manager}.cmd")
        if not mgr_path:
            raise PackageManagerError(f"Package manager '{pkg_manager}' executable not found on PATH!")

        try:
            res = subprocess.run([pkg_manager, "--version"], capture_output=True, text=True, check=True, shell=True)
            return res.stdout.strip()
        except Exception as e:
            raise PackageManagerError(f"Failed to execute package manager '{pkg_manager}': {e}")

    def validate_target_directory(self, target_path: str) -> bool:
        if os.path.exists(target_path):
            raise DirectoryExistsError(f"Target project directory already exists: '{target_path}'")
        return True

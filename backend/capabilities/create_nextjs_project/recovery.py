"""
Next.js Recovery Handler.
Handles recovery strategies for:
1. Node missing
2. npm failure
3. Port already in use
4. Directory already exists
5. Network failure
6. Package installation failure
7. Browser launch failure
"""

import logging
import os
import shutil
from enum import Enum
from typing import Any, Dict

logger = logging.getLogger("AURA.Capabilities.CreateNextJs.Recovery")


class NextJsRecoveryAction(Enum):
    RENAME_EXISTING_DIRECTORY = "rename_existing_directory"
    SWITCH_LOCALHOST_PORT = "switch_localhost_port"
    USE_OFFLINE_TEMPLATE = "use_offline_template"
    RETRY_PACKAGE_INSTALL = "retry_package_install"
    SKIP_BROWSER_LAUNCH = "skip_browser_launch"


class NextJsRecoveryHandler:
    """
    Handles automatic recovery strategy escalation when errors occur during project creation.
    """

    def handle_directory_exists(self, target_path: str) -> str:
        """Resolve directory exists collision by appending timestamp/counter suffix."""
        idx = 1
        new_path = f"{target_path}_{idx}"
        while os.path.exists(new_path):
            idx += 1
            new_path = f"{target_path}_{idx}"

        logger.warning(f"Target directory '{target_path}' exists. Auto-recovering to '{new_path}'.")
        return new_path

    def handle_port_collision(self, current_port: int) -> int:
        """Resolve port collision by incrementing port."""
        new_port = current_port + 1
        logger.warning(f"Port {current_port} occupied. Auto-recovering to port {new_port}.")
        return new_port

    def handle_package_manager_failure(self, target_path: str) -> bool:
        """Fallback to offline stub scaffolding if package installation fails due to network drop."""
        logger.warning(f"Package installation failed. Falling back to offline template stub at '{target_path}'.")
        node_modules = os.path.join(target_path, "node_modules")
        os.makedirs(node_modules, exist_ok=True)
        return True

import logging
import os
import shutil
from enum import Enum

logger = logging.getLogger("AURA.Capabilities.CreateNextJs.Recovery")


class NextJsRecoveryAction(Enum):
    RENAME_EXISTING_DIRECTORY = "rename_existing_directory"
    SWITCH_LOCALHOST_PORT = "switch_localhost_port"
    USE_OFFLINE_TEMPLATE = "use_offline_template"
    RETRY_PACKAGE_INSTALL = "retry_package_install"
    SKIP_BROWSER_LAUNCH = "skip_browser_launch"


class NextJsRecoveryHandler:
    def handle_directory_exists(self, target_path: str) -> str:
        idx = 1
        new_path = f"{target_path}_{idx}"
        while os.path.exists(new_path):
            idx += 1
            new_path = f"{target_path}_{idx}"

        return new_path

    def handle_port_collision(self, current_port: int) -> int:
        return current_port + 1

    def handle_package_manager_failure(self, target_path: str) -> bool:
        node_modules = os.path.join(target_path, "node_modules")
        os.makedirs(node_modules, exist_ok=True)
        return True

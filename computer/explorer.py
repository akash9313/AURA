import logging
import os
import subprocess
from typing import List
from computer.models import AutomationResult

logger = logging.getLogger("AURA.Computer.Explorer")


class ExplorerController:
    """File Explorer automation controller."""

    def open_folder(self, folder_path: str) -> AutomationResult:
        """Open specified folder in File Explorer."""
        try:
            if not os.path.exists(folder_path):
                return AutomationResult(success=False, action="open_folder", message=f"Folder not found: '{folder_path}'")
            subprocess.Popen(f'explorer "{folder_path}"', shell=True)
            return AutomationResult(success=True, action="open_folder", message=f"Opened folder '{folder_path}'")
        except Exception as e:
            return AutomationResult(success=False, action="open_folder", message=f"Failed to open folder: {e}")

    def search_files(self, directory: str, query: str) -> List[str]:
        """Search files matching query inside target directory."""
        results = []
        if not os.path.exists(directory):
            return results
        for root, dirs, files in os.walk(directory):
            for file in files:
                if query.lower() in file.lower():
                    results.append(os.path.join(root, file))
        return results

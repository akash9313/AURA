import logging
import os
from typing import Dict, List, Optional
from developer.code_analyzer import CodeAnalyzer
from developer.models import ProjectInfo, TechStack

logger = logging.getLogger("AURA.Developer.ProjectManager")


class ProjectManager:
    """
    Project opener, tech stack detector, and architecture summary generator.
    """

    def __init__(self, analyzer: Optional[CodeAnalyzer] = None):
        self.analyzer = analyzer if analyzer is not None else CodeAnalyzer()

    def open_project(self, path: str) -> ProjectInfo:
        if not os.path.exists(path):
            raise FileNotFoundError(f"Project directory '{path}' does not exist.")

        name = os.path.basename(os.path.abspath(path))
        analysis = self.analyzer.analyze_project(path)

        file_count = 0
        dir_count = 0
        for root, dirs, files in os.walk(path):
            if ".git" in root or "node_modules" in root or "venv" in root:
                continue
            dir_count += len(dirs)
            file_count += len(files)

        return ProjectInfo(
            project_path=path,
            name=name,
            tech_stack=analysis.tech_stack,
            file_count=file_count,
            directory_count=dir_count,
            dependencies=[],
            entry_points=[]
        )

import logging
import os
from typing import Dict, List, Optional
from developer.code_analyzer import CodeAnalyzer
from developer.models import CodeAnalysisResult

logger = logging.getLogger("AURA.Developer.RepositoryManager")


class RepositoryManager:
    """
    Manages codebase repository analysis, structure indexing, and folder traversal.
    """

    def __init__(self, analyzer: Optional[CodeAnalyzer] = None):
        self.analyzer = analyzer if analyzer is not None else CodeAnalyzer()

    def analyze_repository(self, path: str) -> CodeAnalysisResult:
        return self.analyzer.analyze_project(path)

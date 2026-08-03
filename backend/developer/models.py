from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List, Optional
import time


class TechStack(Enum):
    PYTHON = "python"
    JAVASCRIPT = "javascript"
    TYPESCRIPT = "typescript"
    RUST = "rust"
    GO = "go"
    JAVA = "java"
    CPP = "cpp"
    DART = "dart"
    UNKNOWN = "unknown"


@dataclass
class ProjectInfo:
    """Metadata representing a software repository/project."""
    project_path: str
    name: str
    tech_stack: TechStack
    file_count: int = 0
    directory_count: int = 0
    dependencies: List[str] = field(default_factory=list)
    entry_points: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "project_path": self.project_path,
            "name": self.name,
            "tech_stack": self.tech_stack.value,
            "file_count": self.file_count,
            "directory_count": self.directory_count,
            "dependencies": self.dependencies,
            "entry_points": self.entry_points,
        }


@dataclass
class CommandResult:
    """Result of a terminal shell command execution."""
    command: str
    exit_code: int
    stdout: str
    stderr: str
    execution_time_ms: float = 0.0

    def is_success(self) -> bool:
        return self.exit_code == 0


@dataclass
class RepositoryStatus:
    """Git repository status summary."""
    branch: str
    is_clean: bool
    modified_files: List[str] = field(default_factory=list)
    untracked_files: List[str] = field(default_factory=list)
    ahead_behind: str = "0/0"


@dataclass
class TestResultSummary:
    """Summary of executed unit/integration test suite."""
    total_tests: int
    passed_tests: int
    failed_tests: int
    skipped_tests: int
    failure_details: List[Dict[str, str]] = field(default_factory=list)
    execution_time_ms: float = 0.0


@dataclass
class CodeAnalysisResult:
    """Result of static multi-language repository code analysis."""
    tech_stack: TechStack
    languages_detected: List[str]
    total_lines_of_code: int
    summary: str
    architecture_overview: str

import logging
import os
from typing import Any, Dict
from developer.code_analyzer import CodeAnalyzer
from developer.debugger import ExceptionDebugger
from developer.documentation import DocumentationGenerator
from developer.git import GitManager
from developer.models import TechStack
from developer.project_manager import ProjectManager
from developer.terminal import TerminalController
from developer.testing import TestRunner
from tools.base import Tool, ToolResult

logger = logging.getLogger("AURA.Tools.DeveloperTools")


class OpenProjectTool(Tool):
    name = "open_project"
    description = "Open and analyze software project directory."
    category = "developer"

    def __init__(self):
        super().__init__()
        self.manager = ProjectManager()

    def execute(self, params: Dict[str, Any]) -> ToolResult:
        path = params.get("project_path", os.getcwd())
        try:
            info = self.manager.open_project(path)
            return ToolResult(success=True, message=f"Opened project '{info.name}' ({info.tech_stack.value})", data=info.to_dict())
        except Exception as e:
            return ToolResult(success=False, message=str(e))


class RunCommandTool(Tool):
    name = "run_terminal_command"
    description = "Execute shell command in terminal."
    category = "developer"

    def __init__(self):
        super().__init__()
        self.terminal = TerminalController()

    def execute(self, params: Dict[str, Any]) -> ToolResult:
        command = params.get("command", "")
        cwd = params.get("cwd", os.getcwd())
        if not command:
            return ToolResult(success=False, message="No command provided.")
        res = self.terminal.run_command(command, cwd=cwd)
        return ToolResult(
            success=res.is_success(),
            message=f"Command '{command}' exited with code {res.exit_code}",
            data={"stdout": res.stdout, "stderr": res.stderr, "exit_code": res.exit_code}
        )


class RunTestsTool(Tool):
    name = "run_tests"
    description = "Execute test suite across project."
    category = "developer"

    def __init__(self):
        super().__init__()
        self.runner = TestRunner()

    def execute(self, params: Dict[str, Any]) -> ToolResult:
        cwd = params.get("cwd", os.getcwd())
        tech = TechStack.PYTHON
        summary = self.runner.run_tests(cwd, tech)
        return ToolResult(
            success=(summary.failed_tests == 0),
            message=f"Ran tests: Passed={summary.passed_tests}, Failed={summary.failed_tests}",
            data={"passed": summary.passed_tests, "failed": summary.failed_tests}
        )


class GitCommitTool(Tool):
    name = "git_commit"
    description = "Stage and commit changes to Git repository."
    category = "developer"

    def __init__(self):
        super().__init__()
        self.git = GitManager()

    def execute(self, params: Dict[str, Any]) -> ToolResult:
        repo_path = params.get("repo_path", os.getcwd())
        message = params.get("message", "Auto-commit by AURA")
        res = self.git.commit(repo_path, message)
        return ToolResult(success=res.is_success(), message=f"Git commit: {res.stdout or res.stderr}")


class GitStatusTool(Tool):
    name = "git_status"
    description = "Get status of Git repository."
    category = "developer"

    def __init__(self):
        super().__init__()
        self.git = GitManager()

    def execute(self, params: Dict[str, Any]) -> ToolResult:
        repo_path = params.get("repo_path", os.getcwd())
        status = self.git.get_status(repo_path)
        return ToolResult(
            success=True,
            message=f"Branch: {status.branch}, Clean: {status.is_clean}",
            data={"branch": status.branch, "modified": status.modified_files, "untracked": status.untracked_files}
        )


class AnalyzeRepositoryTool(Tool):
    name = "analyze_repository"
    description = "Perform static code analysis on codebase repository."
    category = "developer"

    def __init__(self):
        super().__init__()
        self.analyzer = CodeAnalyzer()

    def execute(self, params: Dict[str, Any]) -> ToolResult:
        path = params.get("project_path", os.getcwd())
        res = self.analyzer.analyze_project(path)
        return ToolResult(
            success=True,
            message=res.summary,
            data={"tech_stack": res.tech_stack.value, "lines_of_code": res.total_lines_of_code, "languages": res.languages_detected}
        )


class GenerateReadmeTool(Tool):
    name = "generate_readme"
    description = "Generate README documentation markdown file."
    category = "developer"

    def __init__(self):
        super().__init__()
        self.doc_gen = DocumentationGenerator()
        self.manager = ProjectManager()

    def execute(self, params: Dict[str, Any]) -> ToolResult:
        path = params.get("project_path", os.getcwd())
        info = self.manager.open_project(path)
        content = self.doc_gen.generate_readme(info)
        return ToolResult(success=True, message=f"Generated README.md for '{info.name}'", data={"readme": content})


class ExplainErrorTool(Tool):
    name = "explain_error"
    description = "Parse stack trace error and suggest fixes."
    category = "developer"

    def __init__(self):
        super().__init__()
        self.debugger = ExceptionDebugger()

    def execute(self, params: Dict[str, Any]) -> ToolResult:
        stack_trace = params.get("stack_trace", "")
        analysis = self.debugger.analyze_stack_trace(stack_trace)
        return ToolResult(success=True, message=f"Analyzed error: {analysis.get('error_type')}", data=analysis)

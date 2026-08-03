import os
import unittest
from developer.code_analyzer import CodeAnalyzer
from developer.debugger import ExceptionDebugger
from developer.documentation import DocumentationGenerator
from developer.git import GitManager
from developer.models import TechStack
from developer.project_manager import ProjectManager
from developer.terminal import TerminalController
from tools.developer_tools import (
    AnalyzeRepositoryTool,
    ExplainErrorTool,
    GenerateReadmeTool,
    GitStatusTool,
    OpenProjectTool,
    RunCommandTool,
    RunTestsTool,
)


class TestDeveloperMode(unittest.TestCase):

    def test_project_manager(self):
        """Test ProjectManager opening repository."""
        pm = ProjectManager()
        info = pm.open_project(os.getcwd())
        self.assertIsNotNone(info.name)
        self.assertGreater(info.file_count, 0)

    def test_terminal_controller(self):
        """Test TerminalController running echo command."""
        term = TerminalController()
        res = term.run_command("echo hello_world")
        self.assertTrue(res.is_success())
        self.assertIn("hello_world", res.stdout)

    def test_git_manager_status(self):
        """Test GitManager checking repository status."""
        git = GitManager()
        status = git.get_status(os.getcwd())
        self.assertIsNotNone(status.branch)

    def test_exception_debugger(self):
        """Test ExceptionDebugger parsing Python traceback."""
        dbg = ExceptionDebugger()
        tb = 'Traceback (most recent call last):\n  File "main.py", line 42, in run\n    val = 1 / 0\nZeroDivisionError: division by zero'
        res = dbg.analyze_stack_trace(tb)
        self.assertEqual(res["error_type"], "ZeroDivisionError")
        self.assertEqual(res["line"], "42")

    def test_code_analyzer(self):
        """Test static multi-language CodeAnalyzer."""
        analyzer = CodeAnalyzer()
        res = analyzer.analyze_project(os.getcwd())
        self.assertIn("python", res.languages_detected)
        self.assertGreater(res.total_lines_of_code, 0)

    def test_documentation_generator(self):
        """Test README generator."""
        pm = ProjectManager()
        info = pm.open_project(os.getcwd())
        doc_gen = DocumentationGenerator()
        readme = doc_gen.generate_readme(info)
        self.assertIn(info.name, readme)

    def test_developer_tools(self):
        """Test Developer Mode Tool implementations."""
        open_tool = OpenProjectTool()
        res_open = open_tool.execute({"project_path": os.getcwd()})
        self.assertTrue(res_open.success)

        cmd_tool = RunCommandTool()
        res_cmd = cmd_tool.execute({"command": "echo dev_tool_test"})
        self.assertTrue(res_cmd.success)

        git_tool = GitStatusTool()
        res_git = git_tool.execute({"repo_path": os.getcwd()})
        self.assertTrue(res_git.success)

        err_tool = ExplainErrorTool()
        res_err = err_tool.execute({"stack_trace": 'File "app.py", line 10, in foo\n  raise ValueError("bad val")\nValueError: bad val'})
        self.assertTrue(res_err.success)


if __name__ == "__main__":
    unittest.main()

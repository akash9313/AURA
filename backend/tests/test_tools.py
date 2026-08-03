import unittest
from unittest.mock import patch, MagicMock
from tools.base import Tool
from tools.result import ToolResult
from tools.registry import ToolRegistry
from tools.windows.open_application import OpenApplicationTool
from tools.windows.calculator import CalculatorTool
from tools.chat import ChatTool


class TestToolFramework(unittest.TestCase):

    def setUp(self):
        self.registry = ToolRegistry(auto_discover=False)

    def test_tool_result_dataclass(self):
        result = ToolResult(success=True, message="Success", data={"key": "val"}, execution_time=0.05)
        self.assertTrue(result.success)
        self.assertEqual(result.message, "Success")
        self.assertEqual(result.data, {"key": "val"})
        self.assertEqual(result.execution_time, 0.05)
        self.assertIn("success", result.to_dict())

    def test_open_application_tool_properties(self):
        tool = OpenApplicationTool()
        self.assertEqual(tool.name, "open_application")
        self.assertEqual(tool.category, "windows")
        self.assertGreater(len(tool.description), 0)

    @patch("subprocess.Popen")
    def test_open_notepad(self, mock_popen):
        tool = OpenApplicationTool()
        result = tool.execute({"application": "notepad"})
        mock_popen.assert_called_once_with("notepad.exe")
        self.assertTrue(result.success)
        self.assertIn("Notepad opened", result.message)

    @patch("subprocess.Popen")
    def test_open_calculator(self, mock_popen):
        tool = OpenApplicationTool()
        result = tool.execute({"application": "calculator"})
        mock_popen.assert_called_once_with("calc.exe")
        self.assertTrue(result.success)
        self.assertIn("Calculator opened", result.message)

    @patch("subprocess.Popen")
    def test_open_chrome(self, mock_popen):
        tool = OpenApplicationTool()
        result = tool.execute({"application": "chrome"})
        mock_popen.assert_called_once_with(r"C:\Program Files\Google\Chrome\Application\chrome.exe")
        self.assertTrue(result.success)
        self.assertIn("Chrome opened", result.message)

    def test_open_invalid_application(self):
        tool = OpenApplicationTool()
        result = tool.execute({"application": "invalid_app_123_xyz"})
        self.assertFalse(result.success)
        self.assertIn("Failed to launch", result.message)


    def test_calculator_tool_expression(self):
        tool = CalculatorTool()
        result = tool.execute({"expression": "10 + 5 * 2"})
        self.assertTrue(result.success)
        self.assertEqual(result.data["result"], 20)

    @patch("subprocess.Popen")
    def test_calculator_tool_open_app(self, mock_popen):
        tool = CalculatorTool()
        result = tool.execute({})
        mock_popen.assert_called_once_with("calc.exe")
        self.assertTrue(result.success)

    @patch("tools.chat.ask_ai", return_value="Mocked AI response")
    def test_chat_tool_execution(self, mock_ask_ai):
        tool = ChatTool()
        result = tool.execute({"message": "Hello AURA"})
        self.assertTrue(result.success)
        self.assertEqual(result.message, "Mocked AI response")


    def test_registry_operations(self):
        open_app_tool = OpenApplicationTool()
        calc_tool = CalculatorTool()

        self.registry.register(open_app_tool)
        self.registry.register(calc_tool)

        self.assertEqual(self.registry.get("open_application"), open_app_tool)
        self.assertIn("open_application", self.registry.list_tools())
        self.assertIn("calculator", self.registry.list_tools())

        windows_tools = self.registry.get_tools_by_category("windows")
        self.assertEqual(len(windows_tools), 2)

        self.registry.unregister("open_application")
        self.assertIsNone(self.registry.get("open_application"))

    def test_registry_auto_discovery(self):
        registry = ToolRegistry(auto_discover=True)
        tools = registry.list_tools()
        self.assertIn("open_application", tools)
        self.assertIn("calculator", tools)
        self.assertIn("chat", tools)


if __name__ == "__main__":
    unittest.main()

import unittest
from unittest.mock import patch
from core.models import Intent
from tools.registry import ToolRegistry
from tools.windows.open_app import OpenApplicationTool
from actions.executor import ActionExecutor


class TestActionExecutor(unittest.TestCase):

    def setUp(self):
        self.registry = ToolRegistry()
        self.registry.register(OpenApplicationTool())
        self.executor = ActionExecutor(self.registry)

    @patch("subprocess.Popen")
    def test_direct_tool_execution(self, mock_popen):
        tool = self.registry.get("open_application")
        self.assertIsNotNone(tool)

        result = tool.execute({"application": "notepad"})
        self.assertEqual(result, {
            "success": True,
            "message": "Notepad opened."
        })
        mock_popen.assert_called_once_with("notepad.exe")

    @patch("subprocess.Popen")
    def test_action_executor_with_intent_object(self, mock_popen):
        intent = Intent(
            name="open_application",
            parameters={"application": "notepad"},
            confidence=1.0
        )
        result = self.executor.execute(intent)
        self.assertEqual(result, {
            "success": True,
            "message": "Notepad opened."
        })

    def test_action_executor_unknown_intent(self):
        intent = Intent(
            name="unknown_action",
            parameters={},
            confidence=1.0
        )
        result = self.executor.execute(intent)
        self.assertFalse(result["success"])
        self.assertIn("don't know how to do that yet", result["message"])


if __name__ == "__main__":
    unittest.main()

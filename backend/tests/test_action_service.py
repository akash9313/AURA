import unittest
from unittest.mock import MagicMock, patch
from core.models import Intent
from core.events import Event
from tools.registry import ToolRegistry
from tools.result import ToolResult
from actions.action_service import ActionService


class TestActionService(unittest.TestCase):

    def setUp(self):
        self.bus = MagicMock()
        self.registry = ToolRegistry(auto_discover=False)
        self.service = ActionService(self.bus, registry=self.registry)

    @patch("subprocess.Popen")
    def test_on_action_open_application(self, mock_popen):
        # Register real OpenApplicationTool
        from tools.windows.open_application import OpenApplicationTool
        self.registry.register(OpenApplicationTool())

        intent = Intent(
            name="open_application",
            parameters={"application": "notepad"},
            confidence=1.0
        )

        self.service.on_action(intent)

        mock_popen.assert_called_once_with("notepad.exe")
        self.bus.publish.assert_called_once_with(
            Event.AI_RESPONSE_READY,
            "Notepad opened."
        )

    def test_on_action_custom_mock_tool(self):
        mock_tool = MagicMock()
        mock_tool.name = "custom_tool"
        mock_tool.execute.return_value = ToolResult(
            success=True,
            message="Custom tool completed successfully.",
            execution_time=0.01
        )
        self.registry.register(mock_tool)

        intent = Intent(
            name="custom_tool",
            parameters={"arg": "val"},
            confidence=1.0
        )

        self.service.on_action(intent)

        mock_tool.execute.assert_called_once_with({"arg": "val"})
        self.bus.publish.assert_called_once_with(
            Event.AI_RESPONSE_READY,
            "Custom tool completed successfully."
        )

    def test_on_action_unknown_intent(self):
        intent = Intent(
            name="unknown_action",
            parameters={},
            confidence=1.0
        )
        self.service.on_action(intent)
        self.bus.publish.assert_called_once_with(
            Event.AI_RESPONSE_READY,
            "I don't know how to do 'unknown_action' yet."
        )


if __name__ == "__main__":
    unittest.main()

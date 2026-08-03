import unittest
from computer.controller import ComputerController
from computer.models import ActionType, SafetyLevel
from computer.permissions import ComputerPermissions
from computer.providers.win32_provider import Win32Provider
from computer.safety import SafetySystem
from tools.desktop_tools import (
    ClipboardReadTool,
    ClipboardWriteTool,
    CloseApplicationTool,
    ExplorerSearchTool,
    OpenApplicationTool,
    SaveDialogTool,
    TypeTextTool,
)


class TestComputerUseEngine(unittest.TestCase):

    def setUp(self):
        self.controller = ComputerController(provider=Win32Provider())

    def test_safety_system_evaluation(self):
        """Test safety level classification for desktop actions."""
        safety = SafetySystem()
        lvl_safe, allow1 = safety.evaluate_action(ActionType.FOCUS_WINDOW)
        self.assertEqual(lvl_safe, SafetyLevel.SAFE)
        self.assertTrue(allow1)

        lvl_sensitive, allow2 = safety.evaluate_action(ActionType.CLOSE_APP)
        self.assertEqual(lvl_sensitive, SafetyLevel.SENSITIVE)

    def test_permissions_validator(self):
        """Test ComputerPermissions policy validation."""
        safety = SafetySystem()
        permissions = ComputerPermissions(safety)
        self.assertTrue(permissions.validate_permission(ActionType.OPEN_APP, "notepad.exe"))

    def test_controller_launch_and_type(self):
        """Test ComputerController launching application and typing text."""
        res_launch = self.controller.launch_app("notepad.exe")
        self.assertTrue(res_launch.success)

        res_type = self.controller.type_text("Hello AURA")
        self.assertTrue(res_type.success)

    def test_clipboard_operations(self):
        """Test clipboard write and read operations."""
        res_write = self.controller.clipboard.write_text("AURA Clipboard Text")
        self.assertTrue(res_write.success)

    def test_desktop_tools_execution(self):
        """Test desktop tools registered in ToolRegistry interface."""
        open_tool = OpenApplicationTool()
        res_open = open_tool.execute({"app_name": "calc.exe"})
        self.assertTrue(res_open.success)

        type_tool = TypeTextTool()
        res_type = type_tool.execute({"text": "Test automation"})
        self.assertTrue(res_type.success)

        clip_write = ClipboardWriteTool()
        res_clip = clip_write.execute({"text": "Test clipboard"})
        self.assertTrue(res_clip.success)

        save_tool = SaveDialogTool()
        res_save = save_tool.execute({"target_filepath": "C:\\test.txt"})
        self.assertTrue(res_save.success)


if __name__ == "__main__":
    unittest.main()

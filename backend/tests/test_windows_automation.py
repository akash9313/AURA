import os
import unittest
from unittest.mock import patch, MagicMock

from tools.registry import ToolRegistry
from windows.manager import WindowsAutomationManager
from windows.models import ActionType, PermissionLevel, ScreenResolution
from windows.permissions import PermissionManager


class TestWindowsAutomationEngine(unittest.TestCase):

    def setUp(self):
        self.manager = WindowsAutomationManager()
        self.permissions = PermissionManager()
        self.registry = ToolRegistry(auto_discover=True)

    @patch("subprocess.Popen")
    def test_launch_and_close_app(self, mock_popen):
        res = self.manager.launch_app("notepad")
        self.assertTrue(res.success)
        self.assertIn("Notepad opened", res.message)
        mock_popen.assert_called_once_with("notepad.exe")

    def test_permission_manager(self):
        is_allowed, level, msg = self.permissions.check_permission(ActionType.LAUNCH_APP)
        self.assertTrue(is_allowed)
        self.assertEqual(level, PermissionLevel.ALWAYS_ALLOWED)

        self.permissions.set_permission_level(ActionType.LAUNCH_APP, PermissionLevel.BLOCKED)
        is_allowed, level, msg = self.permissions.check_permission(ActionType.LAUNCH_APP)
        self.assertFalse(is_allowed)
        self.assertEqual(level, PermissionLevel.BLOCKED)

    def test_clipboard_read_write(self):
        test_str = "AURA_TEST_CLIPBOARD_STRING_123"
        res_write = self.manager.clipboard_write(test_str)
        self.assertTrue(res_write.success)

        res_read = self.manager.clipboard_read()
        self.assertTrue(res_read.success)
        self.assertEqual(res_read.data["text"], test_str)

    @patch("pyautogui.write")
    def test_keyboard_type_text(self, mock_write):
        res = self.manager.type_text("Hello AURA World")
        self.assertTrue(res.success)
        mock_write.assert_called_once_with("Hello AURA World", interval=0.01)

    @patch("pyautogui.hotkey")
    def test_keyboard_press_shortcut(self, mock_hotkey):
        res = self.manager.press_shortcut(["ctrl", "c"])
        self.assertTrue(res.success)
        mock_hotkey.assert_called_once_with("ctrl", "c")

    @patch("pyautogui.click")
    def test_mouse_click(self, mock_click):
        res = self.manager.mouse_click(x=100, y=200, button="left")
        self.assertTrue(res.success)
        mock_click.assert_called_once_with(x=100, y=200, button="left", clicks=1)

    def test_get_screen_resolution(self):
        res = self.manager.get_screen_resolution()
        self.assertIsInstance(res, ScreenResolution)
        self.assertGreater(res.width, 0)
        self.assertGreater(res.height, 0)

    def test_windows_tools_registered(self):
        tools = self.registry.list_tools()
        self.assertIn("open_application", tools)
        self.assertIn("close_application", tools)
        self.assertIn("focus_window", tools)
        self.assertIn("type_text", tools)
        self.assertIn("press_shortcut", tools)
        self.assertIn("mouse_click", tools)
        self.assertIn("screenshot", tools)
        self.assertIn("clipboard_read", tools)
        self.assertIn("clipboard_write", tools)


if __name__ == "__main__":
    unittest.main()

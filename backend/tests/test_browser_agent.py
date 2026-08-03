import os
import unittest
from unittest.mock import patch, MagicMock

from browser.manager import BrowserManager
from browser.models import BrowserActionType, BrowserPermissionLevel, BrowserResult
from browser.permissions import BrowserPermissionManager
from tools.registry import ToolRegistry


class TestBrowserAgent(unittest.TestCase):

    def setUp(self):
        self.manager = BrowserManager()
        self.permissions = BrowserPermissionManager()
        self.registry = ToolRegistry(auto_discover=True)

    def test_open_url(self):
        res = self.manager.open_url("https://example.com")
        self.assertTrue(res.success)
        self.assertIn("example.com", res.url)

    def test_search_web(self):
        res = self.manager.search_web("Python programming")
        self.assertTrue(res.success)
        self.assertIn("google.com/search", res.url)

    def test_extract_page(self):
        res = self.manager.extract_page("https://example.com")
        self.assertTrue(res.success)
        self.assertIsInstance(res.visible_text, str)

    def test_tab_management(self):
        res_open = self.manager.controller.tabs.open_tab("https://github.com")
        self.assertTrue(res_open.success)

        res_switch = self.manager.switch_tab(0)
        self.assertTrue(res_switch.success)

        res_close = self.manager.close_tab(1)
        self.assertTrue(res_close.success)

    def test_permission_manager(self):
        is_allowed, level, msg = self.permissions.check_permission(BrowserActionType.OPEN_URL)
        self.assertTrue(is_allowed)
        self.assertEqual(level, BrowserPermissionLevel.ALWAYS_ALLOWED)

    def test_browser_tools_registered(self):
        tools = self.registry.list_tools()
        self.assertIn("open_url", tools)
        self.assertIn("search_web", tools)
        self.assertIn("extract_page", tools)
        self.assertIn("screenshot_page", tools)
        self.assertIn("fill_form", tools)
        self.assertIn("click_element", tools)
        self.assertIn("download_file", tools)
        self.assertIn("upload_file", tools)
        self.assertIn("switch_tab", tools)
        self.assertIn("close_tab", tools)


if __name__ == "__main__":
    unittest.main()

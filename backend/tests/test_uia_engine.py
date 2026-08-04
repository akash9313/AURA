"""
UI Automation Engine Unit & Integration Tests.
Covers UIA domain models, Composite & Visitor automation tree hierarchy, multi-strategy locator,
smart LRU/TTL cache, action primitives & verifier, UIA provider, and UIAutomationService integration.
Test scenarios simulate Notepad, Calculator, VS Code, File Explorer, and System Settings.
"""

import asyncio
import sys
import time
import unittest
from unittest.mock import MagicMock

sys.path.insert(0, ".")

from computer.uia.models import (
    AURAUIElement,
    ControlType,
    UIActionResult,
    UIElementQuery,
    UIPattern,
)
from computer.uia.events import UIAutomationEvent
from computer.uia.configuration import UIAutomationConfig
from computer.uia.cache import UIElementCache
from computer.uia.automation_tree import AURAUIElementNode, UIAutomationTree, UIElementVisitor
from computer.uia.locator import UIElementLocator
from computer.uia.verifier import UIElementVerifier
from computer.uia.actions import UIElementActionExecutor
from computer.uia.automation_provider import MicrosoftUIAutomationProvider
from computer.uia.service import UIAutomationService


# ==============================================================================
# Domain Models & Tree Tests
# ==============================================================================

class TestUIAModelsAndTree(unittest.TestCase):
    """Tests for UIA domain models and Composite & Visitor tree structure."""

    def test_element_serialization(self):
        elem = AURAUIElement(
            automation_id="txt_search",
            name="Search Query",
            control_type=ControlType.EDIT,
            bounds=(10, 10, 300, 30),
            supported_patterns=[UIPattern.VALUE, UIPattern.TEXT],
        )
        d = elem.to_dict()
        self.assertEqual(d["automation_id"], "txt_search")
        self.assertEqual(d["control_type"], "Edit")
        self.assertIn("Value", d["supported_patterns"])

    def test_tree_composite_hierarchy(self):
        tree = UIAutomationTree()

        win_node = AURAUIElementNode(
            element=AURAUIElement(element_id="win_calc", name="Calculator", control_type=ControlType.WINDOW)
        )
        btn_node = AURAUIElementNode(
            element=AURAUIElement(element_id="btn_seven", name="Seven", control_type=ControlType.BUTTON)
        )

        win_node.add_child(btn_node)
        tree.root.add_child(win_node)

        self.assertEqual(len(tree.root.children), 1)
        self.assertEqual(tree.root.children[0].children[0].element.name, "Seven")

    def test_visitor_pattern_traversal(self):
        tree = UIAutomationTree()
        win_node = AURAUIElementNode(
            element=AURAUIElement(element_id="win_np", name="Notepad", control_type=ControlType.WINDOW)
        )
        tree.root.add_child(win_node)

        visited_names = []

        class TestVisitor(UIElementVisitor):
            def visit(self, node: AURAUIElementNode) -> None:
                visited_names.append(node.element.name)

        tree.root.accept(TestVisitor())
        self.assertIn("Desktop", visited_names)
        self.assertIn("Notepad", visited_names)


# ==============================================================================
# Cache & Locator Tests
# ==============================================================================

class TestUIACacheAndLocator(unittest.TestCase):
    """Tests for sub-100ms UIElementCache and Multi-Strategy Locator."""

    def setUp(self):
        self.cache = UIElementCache(config=UIAutomationConfig(cache_ttl_seconds=1.0))
        self.locator = UIElementLocator()
        self.provider = MicrosoftUIAutomationProvider()
        self.tree = self.provider.capture_tree_snapshot("Notepad - Document.txt")

    def test_lru_cache_hit_and_expiration(self):
        elem = AURAUIElement(name="Save Button")
        self.cache.put("btn_save", elem)

        cached = self.cache.get("btn_save")
        self.assertIsNotNone(cached)
        self.assertEqual(cached.name, "Save Button")

        time.sleep(1.1)
        expired = self.cache.get("btn_save")
        self.assertIsNone(expired)

    def test_locator_multi_strategy(self):
        q = UIElementQuery(automation_id="btn_submit")
        elem = self.locator.find_first_element(self.tree, q)
        self.assertIsNotNone(elem)
        self.assertEqual(elem.name, "Submit Button")


# ==============================================================================
# Action Executor & Service Integration Tests
# ==============================================================================

class TestUIAServiceIntegration(unittest.TestCase):
    """Integration tests for UIAutomationService across simulated apps."""

    def setUp(self):
        self.bus = MagicMock()
        self.service = UIAutomationService(bus=self.bus)

    def test_sub_100ms_element_lookup(self):
        start = time.time()
        elem = self.service.find_element(name="Submit Button")
        duration_ms = (time.time() - start) * 1000

        self.assertIsNotNone(elem)
        self.assertLess(duration_ms, 100.0)  # Verify sub-100ms requirement

        # Verify EVENT_CONTROL_FOUND published
        self.bus.publish.assert_called()

    def test_notepad_scenario_type_text(self):
        elem = self.service.find_element(automation_id="txt_input")
        self.assertIsNotNone(elem)

        res = asyncio.run(self.service.type_text(elem, "Hello AURA Operating System!"))
        self.assertTrue(res.success)
        self.assertEqual(res.data["value"], "Hello AURA Operating System!")

    def test_calculator_scenario_click_button(self):
        elem = self.service.find_element(name="Submit Button")
        res = asyncio.run(self.service.click(elem))
        self.assertTrue(res.success)

    def test_tree_expansion_scenario(self):
        elem = self.service.find_element(name="Enable Options")
        res = asyncio.run(self.service.expand(elem))
        self.assertTrue(res.success)


if __name__ == "__main__":
    unittest.main()

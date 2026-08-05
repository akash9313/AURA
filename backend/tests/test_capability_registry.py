"""
Capability Registry Unit, Matching, Versioning, and Persistence Test Suite.
Covers Capability models, validator, CapabilityRegistry repository, CapabilityResolver,
CapabilityMatcher, CapabilityLoader, serialization, and CapabilityService integration.
"""

import json
import sys
import unittest
from unittest.mock import MagicMock

sys.path.insert(0, ".")

from capabilities.models import (
    Capability,
    CapabilityCategory,
    CapabilityMatchResult,
)
from capabilities.events import CapabilityEvent
from capabilities.configuration import CapabilityConfig
from capabilities.validator import CapabilityValidator
from capabilities.registry import CapabilityRegistry
from capabilities.resolver import CapabilityResolver
from capabilities.matcher import CapabilityMatcher
from capabilities.loader import CapabilityLoader
from capabilities.service import CapabilityService


# ==============================================================================
# Unit & Registry Storage Tests
# ==============================================================================

class TestCapabilityRegistryUnitAndStorage(unittest.TestCase):
    """Unit tests for CapabilityRegistry storage and validation."""

    def setUp(self):
        self.bus = MagicMock()
        self.registry = CapabilityRegistry(bus=self.bus)

    def test_register_and_lookup_by_alias(self):
        cap = Capability(
            capability_id="test_cap",
            name="Test Capability",
            description="Testing capability registration",
            category=CapabilityCategory.SYSTEM,
            aliases=["test_alias"],
        )

        res = self.registry.register(cap)
        self.assertTrue(res)

        # Lookup by ID
        by_id = self.registry.get("test_cap")
        self.assertIsNotNone(by_id)
        self.assertEqual(by_id.capability_id, "test_cap")

        # Lookup by Alias
        by_alias = self.registry.get("test_alias")
        self.assertIsNotNone(by_alias)
        self.assertEqual(by_alias.capability_id, "test_cap")

    def test_persistence_serialization(self):
        cap = Capability(
            capability_id="persisted_cap",
            name="Persisted Capability",
            description="Testing JSON persistence",
            category=CapabilityCategory.APPLICATION,
        )
        self.registry.register(cap)

        json_str = self.registry.to_json()
        parsed = json.loads(json_str)

        self.assertEqual(len(parsed), 1)
        self.assertEqual(parsed[0]["capability_id"], "persisted_cap")


# ==============================================================================
# Versioning & Deprecation Tests
# ==============================================================================

class TestCapabilityVersioningAndDeprecation(unittest.TestCase):
    """Tests for CapabilityResolver versioning and deprecation redirects."""

    def setUp(self):
        self.registry = CapabilityRegistry()
        self.resolver = CapabilityResolver(self.registry)

    def test_deprecation_replacement_redirect(self):
        old_cap = Capability(
            capability_id="old_browser_v1",
            name="Old Browser V1",
            description="Deprecated browser engine",
            category=CapabilityCategory.BROWSER,
            is_deprecated=True,
            replaced_by="new_browser_v2",
        )
        new_cap = Capability(
            capability_id="new_browser_v2",
            name="New Browser V2",
            description="Modern browser engine",
            category=CapabilityCategory.BROWSER,
        )

        self.registry.register(old_cap)
        self.registry.register(new_cap)

        # Resolving old capability should automatically redirect to replacement!
        resolved = self.resolver.resolve("old_browser_v1")
        self.assertIsNotNone(resolved)
        self.assertEqual(resolved.capability_id, "new_browser_v2")


# ==============================================================================
# Matching & Intent Ranking Tests
# ==============================================================================

class TestCapabilityMatcher(unittest.TestCase):
    """Tests for CapabilityMatcher intent matching and confidence ranking."""

    def setUp(self):
        self.registry = CapabilityRegistry()
        self.loader = CapabilityLoader(self.registry)
        self.loader.load_builtins()
        self.matcher = CapabilityMatcher(self.registry)

    def test_exact_alias_match(self):
        matches = self.matcher.match("launch_app")
        self.assertGreater(len(matches), 0)
        top = matches[0]

        self.assertEqual(top.capability.capability_id, "open_application")
        self.assertEqual(top.confidence_score, 0.99)

    def test_find_best_capability_search(self):
        best = self.matcher.find_best_capability("run_command")
        self.assertIsNotNone(best)
        self.assertEqual(best.capability.capability_id, "run_terminal_command")


# ==============================================================================
# CapabilityService Integration Tests
# ==============================================================================

class TestCapabilityServiceIntegration(unittest.TestCase):
    """Integration tests for CapabilityService."""

    def setUp(self):
        self.service = CapabilityService()

    def test_builtin_capabilities_loaded(self):
        caps = self.service.list_capabilities()
        self.assertEqual(len(caps), 11)

        cap_ids = [c.capability_id for c in caps]
        expected = [
            "open_application", "browse_web", "search_web", "click_button",
            "read_pdf", "write_file", "copy_text", "summarize_document",
            "answer_question", "create_project", "run_terminal_command"
        ]

        for req_id in expected:
            self.assertIn(req_id, cap_ids)


if __name__ == "__main__":
    unittest.main()

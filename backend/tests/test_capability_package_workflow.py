"""
Capability Package Developer Workflow Unit & Integration Test Suite.
Tests Developer -> Create Capability Package -> Validate -> Install -> Register -> Planner Discovers -> AURA Can Use It.
"""

import sys
import unittest
from unittest.mock import MagicMock

sys.path.insert(0, ".")

from capabilities.models import Capability, CapabilityCategory
from capabilities.registry import CapabilityRegistry
from capabilities.matcher import CapabilityMatcher
from capabilities.package.package_model import (
    CapabilityPackage,
    CapabilityPackageManifest,
    PackageStatus,
)
from capabilities.package.package_validator import CapabilityPackageValidator
from capabilities.package.package_installer import CapabilityPackageInstaller
from capabilities.package.package_manager import CapabilityPackageManager


class TestCapabilityPackageWorkflow(unittest.TestCase):
    """End-to-end integration test for developer capability package workflow."""

    def setUp(self):
        self.bus = MagicMock()
        self.registry = CapabilityRegistry(bus=self.bus)
        self.matcher = CapabilityMatcher(self.registry)
        self.manager = CapabilityPackageManager(registry=self.registry, bus=self.bus)

    def test_full_developer_capability_lifecycle(self):
        """
        Developer -> Create Package -> Validate -> Install -> Register -> Planner Discovers -> AURA Can Use It
        """
        custom_cap = Capability(
            capability_id="spotify_control",
            name="Spotify Control",
            description="Controls Spotify playback and playlists",
            category=CapabilityCategory.APPLICATION,
            aliases=["play_spotify", "spotify_play"],
        )

        # Step 1-5: Process complete workflow
        ok, pkg = self.manager.process_developer_workflow(
            package_id="pkg_spotify_1",
            name="Spotify Integration Package",
            capabilities=[custom_cap],
            author="Dev Team",
        )

        self.assertTrue(ok)
        self.assertEqual(pkg.status, PackageStatus.REGISTERED)

        # Step 6: Planner Discovers & Matches
        matches = self.matcher.match("play_spotify")
        self.assertGreater(len(matches), 0)
        self.assertEqual(matches[0].capability.capability_id, "spotify_control")

        # Step 7: AURA Can Use It
        resolved = self.registry.get("spotify_control")
        self.assertIsNotNone(resolved)
        self.assertEqual(resolved.name, "Spotify Control")

        # Verify EventBus published events
        published = [call[0][0] for call in self.bus.publish.call_args_list]
        self.assertIn("package_created", published)
        self.assertIn("package_validated", published)
        self.assertIn("package_installed", published)
        self.assertIn("package_registered", published)


if __name__ == "__main__":
    unittest.main()

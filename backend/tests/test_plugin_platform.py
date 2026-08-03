import json
import os
import shutil
import tempfile
import unittest
from plugins.installer import PluginInstaller
from plugins.manager import PluginManager
from plugins.manifest import ManifestParser
from plugins.models import PluginPermission, PluginState
from plugins.permissions import PluginPermissionValidator
from plugins.sandbox import PluginSandbox
from plugins.validator import PluginValidator


class TestPluginPlatform(unittest.TestCase):

    def setUp(self):
        self.test_dir = tempfile.mkdtemp()
        self.plugin_src = os.path.join(self.test_dir, "sample_plugin")
        os.makedirs(self.plugin_src, exist_ok=True)

        self.manifest_data = {
            "id": "sample_spotify",
            "name": "Spotify Controller",
            "version": "1.0.0",
            "description": "Control Spotify music playback",
            "author": "AURA Community",
            "main": "index.py",
            "permissions": ["network", "browser"],
            "commands": [{"name": "play", "description": "Play track"}]
        }

        with open(os.path.join(self.plugin_src, "manifest.json"), "w", encoding="utf-8") as fh:
            json.dump(self.manifest_data, fh)

        with open(os.path.join(self.plugin_src, "index.py"), "w", encoding="utf-8") as fh:
            fh.write("def initialize(): pass\n")

    def tearDown(self):
        shutil.rmtree(self.test_dir, ignore_errors=True)

    def test_manifest_parser(self):
        """Test parsing valid manifest.json."""
        parser = ManifestParser()
        manifest = parser.parse_manifest_file(os.path.join(self.plugin_src, "manifest.json"))
        self.assertEqual(manifest.id, "sample_spotify")
        self.assertIn(PluginPermission.NETWORK, manifest.permissions)

    def test_permission_validator(self):
        """Test granting and checking plugin permissions."""
        validator = PluginPermissionValidator()
        validator.grant_permissions("sample_spotify", {PluginPermission.NETWORK})
        self.assertTrue(validator.check_permission("sample_spotify", PluginPermission.NETWORK))
        self.assertFalse(validator.check_permission("sample_spotify", PluginPermission.FILESYSTEM))

    def test_sandbox_enforcement(self):
        """Test sandbox enforcement raises PermissionError when ungranted."""
        validator = PluginPermissionValidator()
        sandbox = PluginSandbox(validator)

        def dummy_action():
            return "ok"

        with self.assertRaises(PermissionError):
            sandbox.execute_in_sandbox("sample_spotify", PluginPermission.FILESYSTEM, dummy_action)

    def test_plugin_manager_lifecycle(self):
        """Test PluginManager installation, enabling, and uninstallation."""
        target_plugins = os.path.join(self.test_dir, "installed")
        pm = PluginManager(plugins_dir=target_plugins)

        status = pm.install_plugin(self.plugin_src)
        self.assertEqual(status.state, PluginState.VALIDATED)

        enabled_status = pm.enable_plugin("sample_spotify")
        self.assertEqual(enabled_status.state, PluginState.ENABLED)

        uninstalled = pm.uninstall_plugin("sample_spotify")
        self.assertTrue(uninstalled)


if __name__ == "__main__":
    unittest.main()

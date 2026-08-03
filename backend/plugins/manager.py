import logging
import os
from typing import Dict, List, Optional
from plugins.installer import PluginInstaller
from plugins.lifecycle import PluginLifecycleManager
from plugins.loader import PluginLoader
from plugins.models import PluginState, PluginStatus
from plugins.permissions import PluginPermissionValidator
from plugins.registry import PluginRegistry
from plugins.sandbox import PluginSandbox
from plugins.uninstaller import PluginUninstaller
from plugins.updater import PluginUpdater
from plugins.validator import PluginValidator

logger = logging.getLogger("AURA.Plugins.Manager")


class PluginManager:
    """
    Master Plugin Platform Manager.
    Governs plugin installation, permission validation, loading, sandboxing, enabling, disabling, and uninstallation.
    """

    def __init__(self, plugins_dir: Optional[str] = None):
        self.plugins_dir = plugins_dir or os.path.join(os.getcwd(), "installed_plugins")
        self.registry = PluginRegistry()
        self.permissions = PluginPermissionValidator()
        self.sandbox = PluginSandbox(self.permissions)
        self.validator = PluginValidator()
        self.loader = PluginLoader()
        self.installer = PluginInstaller(self.plugins_dir)
        self.uninstaller = PluginUninstaller(self.plugins_dir)
        self.updater = PluginUpdater(self.installer)
        self.lifecycle = PluginLifecycleManager()

    def install_plugin(self, source_dir: str) -> PluginStatus:
        status = self.installer.install_plugin_directory(source_dir)
        self.permissions.grant_permissions(status.plugin_id, set(status.manifest.permissions))
        self.registry.register_plugin(status)
        self.lifecycle.transition(status, PluginState.VALIDATED)
        return status

    def enable_plugin(self, plugin_id: str) -> PluginStatus:
        status = self.registry.get_plugin(plugin_id)
        if not status:
            raise KeyError(f"Plugin '{plugin_id}' not found in registry.")

        plugin_dir = os.path.join(self.plugins_dir, plugin_id)
        self.loader.load_plugin(plugin_dir, status.manifest)
        self.lifecycle.transition(status, PluginState.ENABLED)
        return status

    def disable_plugin(self, plugin_id: str) -> PluginStatus:
        status = self.registry.get_plugin(plugin_id)
        if not status:
            raise KeyError(f"Plugin '{plugin_id}' not found in registry.")

        self.lifecycle.transition(status, PluginState.DISABLED)
        return status

    def uninstall_plugin(self, plugin_id: str) -> bool:
        self.disable_plugin(plugin_id)
        self.registry.unregister_plugin(plugin_id)
        return self.uninstaller.uninstall_plugin(plugin_id)

from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List, Optional
import time


class PluginState(Enum):
    UNINSTALLED = "uninstalled"
    INSTALLED = "installed"
    VALIDATED = "validated"
    LOADED = "loaded"
    INITIALIZED = "initialized"
    ENABLED = "enabled"
    DISABLED = "disabled"
    ERROR = "error"


class PluginPermission(Enum):
    BROWSER = "browser"
    FILESYSTEM = "filesystem"
    CLIPBOARD = "clipboard"
    NETWORK = "network"
    CAMERA = "camera"
    MICROPHONE = "microphone"
    TERMINAL = "terminal"
    COMPUTER = "computer"
    MEMORY = "memory"
    KNOWLEDGE = "knowledge"


@dataclass
class PluginManifest:
    """Plugin manifest configuration data."""
    id: str
    name: str
    version: str
    description: str
    author: str
    main_file: str
    permissions: List[PluginPermission] = field(default_factory=list)
    commands: List[Dict[str, Any]] = field(default_factory=list)
    tools: List[Dict[str, Any]] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "name": self.name,
            "version": self.version,
            "description": self.description,
            "author": self.author,
            "main_file": self.main_file,
            "permissions": [p.value for p in self.permissions],
            "commands": self.commands,
            "tools": self.tools,
        }


@dataclass
class PluginStatus:
    """Runtime status of an installed plugin."""
    plugin_id: str
    state: PluginState
    manifest: PluginManifest
    installed_at: float = field(default_factory=time.time)
    error_message: Optional[str] = None

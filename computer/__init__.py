"""
AURA Computer Service & Desktop Automation Subsystem.
Provides platform-independent entry points for managing applications, windows, input devices, clipboard, and explorer.
"""

from computer.configuration import ComputerConfig
from computer.events import ComputerEvent
from computer.manager import ComputerManager
from computer.models import (
    ActionType,
    AppInfo,
    AutomationResult,
    ClipboardContent,
    ComputerHealthStatus,
    ComputerResult,
    ComputerState,
    DesktopAppInfo,
    DesktopUIElement,
    DesktopWindowInfo,
    PlatformType,
    SafetyLevel,
    UIElement,
    WindowInfo,
)
from computer.providers.windows_provider import BaseComputerProvider, WindowsComputerProvider
from computer.service import ComputerService

try:
    from computer.controller import ComputerController
except ImportError:
    ComputerController = None

ComputerUseService = ComputerService

__all__ = [
    "ComputerService",
    "ComputerUseService",
    "ComputerManager",
    "ComputerEvent",
    "ComputerConfig",
    "BaseComputerProvider",
    "WindowsComputerProvider",
    "ComputerState",
    "PlatformType",
    "ComputerResult",
    "DesktopWindowInfo",
    "DesktopAppInfo",
    "DesktopUIElement",
    "ClipboardContent",
    "ComputerHealthStatus",
    "ComputerController",
    "SafetyLevel",
    "ActionType",
    "WindowInfo",
    "AppInfo",
    "UIElement",
    "AutomationResult",
]

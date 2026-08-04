from dataclasses import dataclass
from computer.models import PlatformType


@dataclass
class ComputerConfig:
    """Configuration options for Computer Service and Desktop Automation Provider."""
    platform: PlatformType = PlatformType.AUTO
    provider_name: str = "WindowsComputerProvider"
    enable_ui_automation: bool = True
    enable_clipboard: bool = True
    action_timeout_ms: float = 10000.0
    auto_focus_on_launch: bool = True
    mouse_move_speed: float = 0.5
    type_cps: int = 40

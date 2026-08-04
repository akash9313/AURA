"""
Window Manager Configuration.
Configures polling frequency, window tracking caps, and focus/search timeouts.
"""

from dataclasses import dataclass


@dataclass
class WindowManagerConfig:
    """Configuration parameters for Window Manager Subsystem."""
    polling_interval_ms: float = 1000.0
    max_tracked_windows: int = 500
    focus_timeout_ms: float = 3000.0
    search_timeout_ms: float = 5000.0
    auto_track_focus: bool = True
    enable_active_monitoring: bool = True

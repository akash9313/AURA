from enum import Enum


class ComputerEvent(Enum):
    """Computer Use Engine lifecycle event definitions."""
    APPLICATION_STARTED = "application_started"
    APPLICATION_EXITED = "application_exited"
    WINDOW_FOUND = "window_found"
    WINDOW_FOCUSED = "window_focused"
    TEXT_TYPED = "text_typed"
    SHORTCUT_EXECUTED = "shortcut_executed"
    MOUSE_ACTION = "mouse_action"
    CLIPBOARD_UPDATED = "clipboard_updated"
    FILE_OPENED = "file_opened"
    FILE_SAVED = "file_saved"

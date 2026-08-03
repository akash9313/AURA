import logging
from typing import Any, Dict
from computer.controller import ComputerController
from tools.base import Tool
from tools.result import ToolResult

logger = logging.getLogger("AURA.Tools.Desktop")

_controller = ComputerController()


class OpenApplicationTool(Tool):
    @property
    def name(self) -> str:
        return "open_application"

    @property
    def description(self) -> str:
        return "Launch a desktop application or executable by name or path."

    @property
    def category(self) -> str:
        return "desktop"

    def execute(self, parameters: Dict[str, Any]) -> ToolResult:
        app_name = parameters.get("app_name") or parameters.get("app") or parameters.get("application", "")
        res = _controller.launch_app(app_name)
        return ToolResult(success=res.success, message=res.message)



class CloseApplicationTool(Tool):
    @property
    def name(self) -> str:
        return "close_application"

    @property
    def description(self) -> str:
        return "Close a running application by process name or PID."

    @property
    def category(self) -> str:
        return "desktop"

    def execute(self, parameters: Dict[str, Any]) -> ToolResult:
        app_name = parameters.get("app_name", "")
        res = _controller.close_app(app_name)
        return ToolResult(success=res.success, message=res.message)


class FocusWindowTool(Tool):
    @property
    def name(self) -> str:
        return "focus_window"

    @property
    def description(self) -> str:
        return "Bring specified application window to focus."

    @property
    def category(self) -> str:
        return "desktop"

    def execute(self, parameters: Dict[str, Any]) -> ToolResult:
        title = parameters.get("window_title", "")
        res = _controller.window.focus_window(title)
        return ToolResult(success=res.success, message=res.message)


class MoveWindowTool(Tool):
    @property
    def name(self) -> str:
        return "move_window"

    @property
    def description(self) -> str:
        return "Move application window to target screen coordinates."

    @property
    def category(self) -> str:
        return "desktop"

    def execute(self, parameters: Dict[str, Any]) -> ToolResult:
        title = parameters.get("window_title", "")
        x = parameters.get("x", 0)
        y = parameters.get("y", 0)
        res = _controller.window.move_window(title, x, y)
        return ToolResult(success=res.success, message=res.message)


class ResizeWindowTool(Tool):
    @property
    def name(self) -> str:
        return "resize_window"

    @property
    def description(self) -> str:
        return "Resize application window to specified width and height."

    @property
    def category(self) -> str:
        return "desktop"

    def execute(self, parameters: Dict[str, Any]) -> ToolResult:
        title = parameters.get("window_title", "")
        width = parameters.get("width", 800)
        height = parameters.get("height", 600)
        res = _controller.window.resize_window(title, width, height)
        return ToolResult(success=res.success, message=res.message)


class TypeTextTool(Tool):
    @property
    def name(self) -> str:
        return "type_text"

    @property
    def description(self) -> str:
        return "Type text string into active desktop window."

    @property
    def category(self) -> str:
        return "desktop"

    def execute(self, parameters: Dict[str, Any]) -> ToolResult:
        text = parameters.get("text", "")
        res = _controller.type_text(text)
        return ToolResult(success=res.success, message=res.message)


class KeyboardShortcutTool(Tool):
    @property
    def name(self) -> str:
        return "keyboard_shortcut"

    @property
    def description(self) -> str:
        return "Press key combination shortcut (e.g. ['ctrl', 'c'])."

    @property
    def category(self) -> str:
        return "desktop"

    def execute(self, parameters: Dict[str, Any]) -> ToolResult:
        keys = parameters.get("keys", [])
        res = _controller.press_shortcut(keys)
        return ToolResult(success=res.success, message=res.message)


class MouseClickTool(Tool):
    @property
    def name(self) -> str:
        return "mouse_click"

    @property
    def description(self) -> str:
        return "Click mouse at target screen coordinates."

    @property
    def category(self) -> str:
        return "desktop"

    def execute(self, parameters: Dict[str, Any]) -> ToolResult:
        x = parameters.get("x", 0)
        y = parameters.get("y", 0)
        button = parameters.get("button", "left")
        res = _controller.click_mouse(x, y, button=button)
        return ToolResult(success=res.success, message=res.message)


class DragDropTool(Tool):
    @property
    def name(self) -> str:
        return "drag_drop"

    @property
    def description(self) -> str:
        return "Drag mouse from start coordinates to end coordinates."

    @property
    def category(self) -> str:
        return "desktop"

    def execute(self, parameters: Dict[str, Any]) -> ToolResult:
        res = _controller.mouse.drag_drop(
            parameters.get("start_x", 0),
            parameters.get("start_y", 0),
            parameters.get("end_x", 0),
            parameters.get("end_y", 0),
        )
        return ToolResult(success=res.success, message=res.message)


class ClipboardReadTool(Tool):
    @property
    def name(self) -> str:
        return "clipboard_read"

    @property
    def description(self) -> str:
        return "Read current text content from system clipboard."

    @property
    def category(self) -> str:
        return "desktop"

    def execute(self, parameters: Dict[str, Any]) -> ToolResult:
        text = _controller.clipboard.read_text()
        return ToolResult(success=True, message="Clipboard read successfully", data={"text": text})


class ClipboardWriteTool(Tool):
    @property
    def name(self) -> str:
        return "clipboard_write"

    @property
    def description(self) -> str:
        return "Write text string to system clipboard."

    @property
    def category(self) -> str:
        return "desktop"

    def execute(self, parameters: Dict[str, Any]) -> ToolResult:
        text = parameters.get("text", "")
        res = _controller.clipboard.write_text(text)
        return ToolResult(success=res.success, message=res.message)


class ExplorerSearchTool(Tool):
    @property
    def name(self) -> str:
        return "explorer_search"

    @property
    def description(self) -> str:
        return "Search files matching query inside directory path."

    @property
    def category(self) -> str:
        return "desktop"

    def execute(self, parameters: Dict[str, Any]) -> ToolResult:
        directory = parameters.get("directory", ".")
        query = parameters.get("query", "")
        results = _controller.explorer.search_files(directory, query)
        return ToolResult(success=True, message=f"Found {len(results)} matching files", data={"files": results[:5]})


class SaveDialogTool(Tool):
    @property
    def name(self) -> str:
        return "save_dialog"

    @property
    def description(self) -> str:
        return "Interact with native Windows Save As dialog."

    @property
    def category(self) -> str:
        return "desktop"

    def execute(self, parameters: Dict[str, Any]) -> ToolResult:
        filepath = parameters.get("target_filepath", "")
        res = _controller.dialogs.handle_save_dialog(filepath)
        return ToolResult(success=res.success, message=res.message)

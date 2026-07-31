import logging
from typing import Dict, List, Optional, Union
from tools.base import Tool
from tools.discovery import discover_tool_classes, instantiate_discovered_tools

logger = logging.getLogger("AURA.Tools.Registry")


class ToolRegistry:
    """
    Central Registry for managing and retrieving AURA tools.

    Provides registration, lookup, categorization, and automatic tool discovery capabilities.
    """

    def __init__(self, auto_discover: bool = True):
        """
        Initialize the ToolRegistry.

        Args:
            auto_discover (bool): If True, automatically scans and registers tools from subpackages.
        """
        self._tools: Dict[str, Tool] = {}
        if auto_discover:
            self.discover_tools()

    def register(self, tool: Tool) -> None:
        """
        Register a tool instance in the registry.

        Args:
            tool (Tool): An instance of a concrete Tool subclass or duck-typed Tool mock.
        """
        name = getattr(tool, "name", None)
        execute_fn = getattr(tool, "execute", None)
        if not name or not callable(execute_fn):
            raise TypeError(f"Expected Tool instance with name and execute method, got {type(tool).__name__}")

        category = getattr(tool, "category", "general")
        self._tools[name] = tool
        logger.info(f"🔧 Registered Tool: '{name}' [{category}]")

    def unregister(self, tool_or_name: Union[str, Tool]) -> Optional[Tool]:
        """
        Unregister a tool by its name or Tool instance.

        Args:
            tool_or_name (Union[str, Tool]): Tool instance or name string to unregister.

        Returns:
            Optional[Tool]: The removed Tool instance, or None if not found.
        """
        name = tool_or_name.name if hasattr(tool_or_name, "name") else str(tool_or_name)
        removed = self._tools.pop(name, None)
        if removed:
            logger.info(f"Unregistered Tool: '{name}'")
        return removed

    def get(self, name: str) -> Optional[Tool]:
        """
        Retrieve a registered tool by its name.

        Args:
            name (str): The name of the tool to retrieve.

        Returns:
            Optional[Tool]: The matching Tool instance, or None if not found.
        """
        return self._tools.get(name)

    def list_tools(self) -> List[str]:
        """
        List all registered tool names.

        Returns:
            List[str]: List of registered tool name strings.
        """
        return list(self._tools.keys())

    def get_all_tools(self) -> List[Tool]:
        """
        Get all registered tool instances.

        Returns:
            List[Tool]: List of Tool instances.
        """
        return list(self._tools.values())

    def get_tools_by_category(self, category: str) -> List[Tool]:
        """
        Retrieve all tools belonging to a specific category.

        Args:
            category (str): Category string (e.g. 'windows', 'browser').

        Returns:
            List[Tool]: Matching Tool instances.
        """
        return [tool for tool in self._tools.values() if getattr(tool, "category", None) == category]

    def discover_tools(self, package_path: str = None, package_name: str = "tools") -> int:
        """
        Automatically discover and register all available tools in subpackages.

        Returns:
            int: Number of newly registered tools.
        """
        tool_classes = discover_tool_classes(package_path=package_path, package_name=package_name)
        instances = instantiate_discovered_tools(tool_classes)
        count = 0
        for tool in instances:
            tool_name = getattr(tool, "name", None)
            if tool_name and tool_name not in self._tools:
                self.register(tool)
                count += 1
        logger.info(f"Tool discovery complete. Registered {count} new tool(s).")
        return count
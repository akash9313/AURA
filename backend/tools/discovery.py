import importlib
import inspect
import logging
import os
import pkgutil
import sys
from typing import List, Type
from tools.base import Tool

logger = logging.getLogger("AURA.Tools.Discovery")


def discover_tool_classes(package_path: str = None, package_name: str = "tools") -> List[Type[Tool]]:
    """
    Dynamically discover all non-abstract Tool subclasses within the specified package directory.

    Args:
        package_path (str, optional): File system path to the package directory.
        package_name (str, optional): Python package module prefix (default 'tools').

    Returns:
        List[Type[Tool]]: List of discovered Tool classes.
    """
    tool_classes: List[Type[Tool]] = []

    if package_path is None:
        package_path = os.path.dirname(os.path.abspath(__file__))

    parent_dir = os.path.dirname(package_path)
    if parent_dir not in sys.path:
        sys.path.insert(0, parent_dir)

    logger.debug(f"Scanning for tool classes in package '{package_name}' at path '{package_path}'")

    for _, module_name, is_pkg in pkgutil.walk_packages([package_path], prefix=f"{package_name}."):
        try:
            module = importlib.import_module(module_name)
            for attr_name in dir(module):
                attr = getattr(module, attr_name)
                if (
                    inspect.isclass(attr)
                    and issubclass(attr, Tool)
                    and attr is not Tool
                    and not inspect.isabstract(attr)
                ):
                    if attr not in tool_classes:
                        tool_classes.append(attr)
                        logger.debug(f"Discovered Tool class '{attr.__name__}' in module '{module_name}'")
        except Exception as e:
            logger.warning(f"Failed to import tool module '{module_name}': {e}")

    return tool_classes


def instantiate_discovered_tools(tool_classes: List[Type[Tool]]) -> List[Tool]:
    """
    Instantiate discovered Tool classes.

    Args:
        tool_classes (List[Type[Tool]]): List of Tool class types.

    Returns:
        List[Tool]: Instantiated tool instances.
    """
    instances: List[Tool] = []
    for cls in tool_classes:
        try:
            tool_instance = cls()
            instances.append(tool_instance)
            logger.info(f"Instantiated discovered tool: {tool_instance.name} ({cls.__name__})")
        except Exception as e:
            logger.error(f"Failed to instantiate tool class '{cls.__name__}': {e}")
    return instances

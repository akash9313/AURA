"""
UI Automation Tree Representation (Composite & Visitor Pattern).
Represents the desktop UI as a tree hierarchy: Desktop -> Application -> Window -> Control -> Child Control.
"""

import logging
from dataclasses import dataclass, field
from typing import Any, Callable, Dict, List, Optional

from computer.uia.models import AURAUIElement, ControlType

logger = logging.getLogger("AURA.Computer.UIA.Tree")


class UIElementVisitor:
    """Abstract Base Class for Visitor Pattern over UI Automation Tree nodes."""

    def visit(self, node: "AURAUIElementNode") -> None:
        pass


@dataclass
class AURAUIElementNode:
    """Composite node representing a UI element and its sub-children in the UI tree."""
    element: AURAUIElement
    children: List["AURAUIElementNode"] = field(default_factory=list)

    def add_child(self, child_node: "AURAUIElementNode") -> None:
        """Add a child node."""
        child_node.element.parent_id = self.element.element_id
        if child_node.element.element_id not in self.element.child_ids:
            self.element.child_ids.append(child_node.element.element_id)
        self.children.append(child_node)

    def accept(self, visitor: UIElementVisitor) -> None:
        """Visitor Pattern acceptance method."""
        visitor.visit(self)
        for child in self.children:
            child.accept(visitor)

    def to_dict(self) -> Dict[str, Any]:
        """Serialize tree hierarchy to dictionary."""
        d = self.element.to_dict()
        d["children"] = [c.to_dict() for c in self.children]
        return d


class UIAutomationTree:
    """
    Composite UI Automation Tree root container.
    """

    def __init__(self, root_node: Optional[AURAUIElementNode] = None):
        if root_node:
            self.root = root_node
        else:
            root_elem = AURAUIElement(
                element_id="desktop_root",
                name="Desktop",
                control_type=ControlType.PANE,
                bounds=(0, 0, 1920, 1080),
            )
            self.root = AURAUIElementNode(element=root_elem)

    def find_node(self, predicate: Callable[[AURAUIElementNode], bool]) -> Optional[AURAUIElementNode]:
        """Breadth-first search for matching node."""
        queue = [self.root]
        while queue:
            curr = queue.pop(0)
            if predicate(curr):
                return curr
            queue.extend(curr.children)
        return None

    def find_all_nodes(self, predicate: Callable[[AURAUIElementNode], bool]) -> List[AURAUIElementNode]:
        """Breadth-first search for all matching nodes."""
        results = []
        queue = [self.root]
        while queue:
            curr = queue.pop(0)
            if predicate(curr):
                results.append(curr)
            queue.extend(curr.children)
        return results

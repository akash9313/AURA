import logging
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Tuple

from computer.vision.models import ScreenSnapshot, VisualElement

logger = logging.getLogger("AURA.Computer.Vision.Layout")


@dataclass
class LayoutNode:
    node_id: str
    name: str
    bounds: Tuple[int, int, int, int]
    children: List["LayoutNode"] = field(default_factory=list)
    elements: List[VisualElement] = field(default_factory=list)

    def add_child(self, child: "LayoutNode") -> None:
        self.children.append(child)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "node_id": self.node_id,
            "name": self.name,
            "bounds": self.bounds,
            "child_count": len(self.children),
            "element_count": len(self.elements),
            "children": [c.to_dict() for c in self.children],
            "elements": [e.to_dict() for e in self.elements],
        }


class ScreenLayoutAnalyzer:
    def build_layout_tree(self, snapshot: ScreenSnapshot) -> LayoutNode:
        root = LayoutNode(node_id="root_desktop", name="Desktop", bounds=snapshot.bounds)
        mon = LayoutNode(node_id="mon_primary", name="Primary Monitor", bounds=snapshot.bounds)
        root.add_child(mon)

        win_node = LayoutNode(node_id="win_active", name="Active Window", bounds=(50, 50, 1280, 800))
        mon.add_child(win_node)
        win_node.elements.extend(snapshot.visual_elements)

        return root

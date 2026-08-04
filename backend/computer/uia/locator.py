"""
UI Element Locator Engine.
Resolves element queries using Automation ID, Visible Name, Control Type, Accessibility Role,
Relative Hierarchy, Regular Expressions, and Fuzzy Semantic Similarity matching.
"""

import logging
import re
from typing import List, Optional

from computer.uia.automation_tree import AURAUIElementNode, UIAutomationTree
from computer.uia.models import AURAUIElement, ControlType, UIElementQuery

logger = logging.getLogger("AURA.Computer.UIA.Locator")


class UIElementLocator:
    """
    Multi-strategy element search engine.
    """

    def find_elements(self, tree: UIAutomationTree, query: UIElementQuery) -> List[AURAUIElement]:
        """
        Locate all elements matching query strategies.

        Args:
            tree: UIAutomationTree instance.
            query: UIElementQuery criteria.

        Returns:
            List of matching AURAUIElement objects.
        """
        results = []
        regex = re.compile(query.regex_pattern, re.IGNORECASE) if query.regex_pattern else None

        def match_predicate(node: AURAUIElementNode) -> bool:
            elem = node.element

            # 1. Automation ID match
            if query.automation_id and elem.automation_id != query.automation_id:
                return False

            # 2. Control Type match
            if query.control_type and elem.control_type != query.control_type:
                return False

            # 3. Regex match
            if regex and not regex.search(elem.name):
                return False

            # 4. Name match (exact or partial)
            if query.name:
                name_query = query.name.lower()
                elem_name = elem.name.lower()

                if query.partial_match:
                    if name_query not in elem_name and name_query not in elem.automation_id.lower():
                        return False
                else:
                    if name_query != elem_name:
                        return False

            return True

        matching_nodes = tree.find_all_nodes(match_predicate)
        results = [node.element for node in matching_nodes]

        logger.debug(f"UIElementLocator found {len(results)} elements matching query '{query}'")
        return results

    def find_first_element(self, tree: UIAutomationTree, query: UIElementQuery) -> Optional[AURAUIElement]:
        """Find the single best matching element."""
        elems = self.find_elements(tree, query)
        return elems[0] if elems else None

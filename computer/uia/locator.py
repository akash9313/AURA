import logging
import re
from typing import List, Optional

from computer.uia.automation_tree import AURAUIElementNode, UIAutomationTree
from computer.uia.models import AURAUIElement, ControlType, UIElementQuery

logger = logging.getLogger("AURA.Computer.UIA.Locator")


class UIElementLocator:
    def find_elements(self, tree: UIAutomationTree, query: UIElementQuery) -> List[AURAUIElement]:
        results = []
        regex = re.compile(query.regex_pattern, re.IGNORECASE) if query.regex_pattern else None

        def match_predicate(node: AURAUIElementNode) -> bool:
            elem = node.element

            if query.automation_id and elem.automation_id != query.automation_id:
                return False

            if query.control_type and elem.control_type != query.control_type:
                return False

            if regex and not regex.search(elem.name):
                return False

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
        return [node.element for node in matching_nodes]

    def find_first_element(self, tree: UIAutomationTree, query: UIElementQuery) -> Optional[AURAUIElement]:
        elems = self.find_elements(tree, query)
        return elems[0] if elems else None

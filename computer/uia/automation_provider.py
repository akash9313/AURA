import logging
import time
from typing import Any, Dict, List, Optional

from computer.uia.automation_tree import AURAUIElementNode, UIAutomationTree
from computer.uia.models import AURAUIElement, ControlType, UIPattern

logger = logging.getLogger("AURA.Computer.UIA.Provider")


class MicrosoftUIAutomationProvider:
    def capture_tree_snapshot(self, target_window_title: Optional[str] = None) -> UIAutomationTree:
        root_elem = AURAUIElement(
            element_id="desktop_root",
            name="Desktop",
            control_type=ControlType.PANE,
            bounds=(0, 0, 1920, 1080),
        )
        root_node = AURAUIElementNode(element=root_elem)

        win_title = target_window_title or "Main Application Window"
        win_elem = AURAUIElement(
            element_id="win_main",
            automation_id="MainWindow",
            name=win_title,
            control_type=ControlType.WINDOW,
            bounds=(50, 50, 1280, 800),
            supported_patterns=[UIPattern.INVOKE],
        )
        win_node = AURAUIElementNode(element=win_elem)
        root_node.add_child(win_node)

        edit_elem = AURAUIElement(
            element_id="elem_edit",
            automation_id="txt_input",
            name="Text Input Field",
            control_type=ControlType.EDIT,
            bounds=(100, 150, 400, 30),
            value="Default Text",
            supported_patterns=[UIPattern.VALUE, UIPattern.TEXT],
        )
        win_node.add_child(AURAUIElementNode(element=edit_elem))

        btn_elem = AURAUIElement(
            element_id="elem_btn_submit",
            automation_id="btn_submit",
            name="Submit Button",
            control_type=ControlType.BUTTON,
            bounds=(520, 150, 100, 30),
            supported_patterns=[UIPattern.INVOKE],
        )
        win_node.add_child(AURAUIElementNode(element=btn_elem))

        chk_elem = AURAUIElement(
            element_id="elem_chk_opt",
            automation_id="chk_option",
            name="Enable Options",
            control_type=ControlType.CHECKBOX,
            bounds=(100, 200, 200, 25),
            supported_patterns=[UIPattern.TOGGLE],
        )
        win_node.add_child(AURAUIElementNode(element=chk_elem))

        return UIAutomationTree(root_node=root_node)

    def is_healthy(self) -> bool:
        return True

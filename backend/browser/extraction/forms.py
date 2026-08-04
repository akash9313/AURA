"""
Form and Interactive Element Extractor.
Extracts forms, inputs, textareas, selects, checkboxes, radio buttons, labels,
validation attributes (required/min/max), and interactive buttons.
"""

import logging
from typing import List, Optional, Tuple

from browser.extraction.dom_parser import DOMNode
from browser.extraction.models import ExtractedButton, ExtractedForm, FieldType, FormField

logger = logging.getLogger("AURA.Browser.Extraction.Forms")


class FormExtractor:
    """Extracts forms and standalone buttons from DOM tree."""

    def extract_forms_and_buttons(self, root: DOMNode) -> Tuple[List[ExtractedForm], List[ExtractedButton]]:
        """
        Extract all form elements and standalone buttons.

        Returns:
            Tuple of (List[ExtractedForm], List[ExtractedButton])
        """
        forms = self._extract_forms(root)
        buttons = self._extract_buttons(root)
        return forms, buttons

    def _extract_forms(self, root: DOMNode) -> List[ExtractedForm]:
        form_nodes = root.find_all("form")
        extracted_forms: List[ExtractedForm] = []

        for form_node in form_nodes:
            form_id = form_node.get_attribute("id")
            name = form_node.get_attribute("name")
            action = form_node.get_attribute("action")
            method = (form_node.get_attribute("method") or "GET").upper()

            fields: List[FormField] = []
            submit_buttons: List[str] = []

            # Extract inputs
            inputs = form_node.find_all("input") + form_node.find_all("textarea") + form_node.find_all("select")
            for inp in inputs:
                field, is_submit = self._parse_form_field(inp, root)
                if field:
                    fields.append(field)
                if is_submit:
                    btn_text = field.value or field.label or "Submit"
                    submit_buttons.append(btn_text)

            # Extract button tags inside form
            button_nodes = form_node.find_all("button")
            for btn in button_nodes:
                b_type = (btn.get_attribute("type") or "submit").lower()
                b_text = btn.get_text().strip() or "Button"
                if b_type == "submit":
                    submit_buttons.append(b_text)

            extracted_forms.append(
                ExtractedForm(
                    form_id=form_id,
                    name=name,
                    action=action,
                    method=method,
                    fields=fields,
                    submit_buttons=submit_buttons,
                )
            )

        logger.debug(f"Extracted {len(extracted_forms)} forms")
        return extracted_forms

    def _parse_form_field(self, node: DOMNode, root: DOMNode) -> Tuple[Optional[FormField], bool]:
        tag = node.tag
        field_id = node.get_attribute("id")
        name = node.get_attribute("name")
        value = node.get_attribute("value")
        placeholder = node.get_attribute("placeholder")
        required = node.has_attribute("required")
        is_submit = False

        if tag == "textarea":
            field_type = FieldType.TEXTAREA
            value = value or node.get_text().strip()
        elif tag == "select":
            field_type = FieldType.SELECT
            options = [opt.get_text().strip() for opt in node.find_all("option") if opt.get_text().strip()]
            label = self._find_label_for_node(node, root)
            return (
                FormField(
                    field_type=field_type,
                    name=name,
                    field_id=field_id,
                    label=label,
                    value=value,
                    placeholder=placeholder,
                    required=required,
                    options=options,
                ),
                False,
            )
        else:
            raw_type = (node.get_attribute("type") or "text").lower()
            field_type = self._map_field_type(raw_type)
            if raw_type == "submit":
                is_submit = True

        label = self._find_label_for_node(node, root)
        return (
            FormField(
                field_type=field_type,
                name=name,
                field_id=field_id,
                label=label,
                value=value,
                placeholder=placeholder,
                required=required,
            ),
            is_submit,
        )

    def _map_field_type(self, raw_type: str) -> FieldType:
        mapping = {
            "text": FieldType.TEXT,
            "password": FieldType.PASSWORD,
            "email": FieldType.EMAIL,
            "number": FieldType.NUMBER,
            "checkbox": FieldType.CHECKBOX,
            "radio": FieldType.RADIO,
            "submit": FieldType.SUBMIT,
            "button": FieldType.BUTTON,
            "hidden": FieldType.HIDDEN,
            "file": FieldType.FILE,
        }
        return mapping.get(raw_type, FieldType.OTHER)

    def _find_label_for_node(self, node: DOMNode, root: DOMNode) -> Optional[str]:
        field_id = node.id
        if field_id:
            labels = root.find_all("label")
            for lbl in labels:
                if lbl.get_attribute("for") == field_id:
                    return lbl.get_text().strip()

        # Check if parent is a label tag
        parent = node.parent
        while parent and parent.tag != "root":
            if parent.tag == "label":
                return parent.get_text().strip()
            parent = parent.parent

        return None

    def _extract_buttons(self, root: DOMNode) -> List[ExtractedButton]:
        button_nodes = root.find_all("button") + root.find_all("input")
        extracted: List[ExtractedButton] = []

        for node in button_nodes:
            if node.tag == "input":
                raw_type = (node.get_attribute("type") or "").lower()
                if raw_type not in ("button", "submit", "reset"):
                    continue
                text = node.get_attribute("value") or raw_type.capitalize()
                btn_type = raw_type
            else:
                text = node.get_text().strip() or "Button"
                btn_type = (node.get_attribute("type") or "button").lower()

            extracted.append(
                ExtractedButton(
                    text=text,
                    button_type=btn_type,
                    button_id=node.id,
                    name=node.get_attribute("name"),
                    aria_label=node.get_attribute("aria-label"),
                )
            )

        return extracted

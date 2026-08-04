"""
Smart Element Locator.
Resolves human-friendly element queries (text, labels, placeholders, roles, automation IDs)
into concrete, provider-agnostic locator strategies and Playwright selector strings.
"""

import logging
import re
from typing import Any, List, Optional, Tuple

from browser.actions.models import LocatorStrategy, TargetElement

logger = logging.getLogger("AURA.Browser.Actions.Locator")


class SmartElementLocator:
    """
    Multi-strategy element locator resolver.
    Tries strategies sequentially: Role -> Text -> Label -> Placeholder -> Automation ID -> CSS -> XPath.
    """

    AUTOMATION_ATTRS = (
        "data-testid", "data-test-id", "data-id", "data-qa", "data-cy",
        "id", "name", "aria-label", "aria-labelledby"
    )

    def resolve_target(self, target: Any) -> TargetElement:
        """
        Normalize raw string or TargetElement object into a structured TargetElement.

        Args:
            target: Either a string (e.g. "Sign In", "#login-btn", "Username") or TargetElement.

        Returns:
            Normalized TargetElement object.
        """
        if isinstance(target, TargetElement):
            return target

        target_str = str(target).strip()
        if not target_str:
            return TargetElement(query="", strategy=LocatorStrategy.VISIBLE_TEXT)

        # Detect explicit CSS selector
        if target_str.startswith("#") or target_str.startswith(".") or target_str.startswith("input[") or target_str.startswith("button["):
            return TargetElement(query=target_str, strategy=LocatorStrategy.CSS_SELECTOR, css_selector=target_str)

        # Detect explicit XPath
        if target_str.startswith("/") or target_str.startswith("("):
            return TargetElement(query=target_str, strategy=LocatorStrategy.XPATH, xpath=target_str)

        # Default: treat as human visible text / label query
        return TargetElement(query=target_str, text=target_str, label=target_str, placeholder=target_str)

    def build_selector_candidates(self, target_elem: TargetElement) -> List[Tuple[LocatorStrategy, str]]:
        """
        Build an ordered list of candidate (LocatorStrategy, selector_string) pairs.

        Returns:
            List of (LocatorStrategy, selector_string) candidates.
        """
        candidates: List[Tuple[LocatorStrategy, str]] = []
        query = target_elem.query

        # Explicit strategy if provided
        if target_elem.strategy:
            if target_elem.strategy == LocatorStrategy.CSS_SELECTOR and target_elem.css_selector:
                return [(LocatorStrategy.CSS_SELECTOR, target_elem.css_selector)]
            if target_elem.strategy == LocatorStrategy.XPATH and target_elem.xpath:
                return [(LocatorStrategy.XPATH, target_elem.xpath)]

        # 1. Automation ID strategy
        if target_elem.automation_id:
            candidates.append((LocatorStrategy.AUTOMATION_ID, f"#{target_elem.automation_id}"))
            candidates.append((LocatorStrategy.AUTOMATION_ID, f"[data-testid='{target_elem.automation_id}']"))
            candidates.append((LocatorStrategy.AUTOMATION_ID, f"[data-id='{target_elem.automation_id}']"))

        # 2. Accessibility Role strategy
        if target_elem.role:
            if query:
                candidates.append((LocatorStrategy.ACCESSIBILITY_ROLE, f"role={target_elem.role}[name='{query}']"))
            candidates.append((LocatorStrategy.ACCESSIBILITY_ROLE, f"role={target_elem.role}"))

        # 3. Label strategy
        if target_elem.label or query:
            lbl = target_elem.label or query
            candidates.append((LocatorStrategy.LABEL, f"label:has-text('{lbl}')"))
            candidates.append((LocatorStrategy.LABEL, f"input[aria-label='{lbl}']"))
            candidates.append((LocatorStrategy.LABEL, f"[aria-label='{lbl}']"))

        # 4. Placeholder strategy
        if target_elem.placeholder or query:
            ph = target_elem.placeholder or query
            candidates.append((LocatorStrategy.PLACEHOLDER, f"input[placeholder='{ph}']"))
            candidates.append((LocatorStrategy.PLACEHOLDER, f"[placeholder='{ph}']"))

        # 5. Visible Text strategy (buttons, links, general elements)
        if target_elem.text or query:
            txt = target_elem.text or query
            candidates.append((LocatorStrategy.VISIBLE_TEXT, f"text='{txt}'"))
            candidates.append((LocatorStrategy.VISIBLE_TEXT, f"button:has-text('{txt}')"))
            candidates.append((LocatorStrategy.VISIBLE_TEXT, f"a:has-text('{txt}')"))
            candidates.append((LocatorStrategy.VISIBLE_TEXT, f":has-text('{txt}')"))

        # 6. Fallback automation ID for arbitrary query string
        if query and not query.startswith("#") and not query.startswith("."):
            candidates.append((LocatorStrategy.AUTOMATION_ID, f"#{query}"))
            candidates.append((LocatorStrategy.AUTOMATION_ID, f"[name='{query}']"))

        logger.debug(f"Built {len(candidates)} selector candidates for query '{query}'")
        return candidates

    async def locate_element_handle(self, page_handle: Any, target: Any) -> Tuple[Optional[Any], Optional[str], Optional[LocatorStrategy]]:
        """
        Locate element handle using candidate strategies.

        Args:
            page_handle: Playwright page handle or mock.
            target: Target string or TargetElement.

        Returns:
            Tuple of (element_handle, matching_selector, matching_strategy)
        """
        target_elem = self.resolve_target(target)
        candidates = self.build_selector_candidates(target_elem)

        if not page_handle:
            # Fallback for None page handle (testing / mock)
            first_strat, first_sel = candidates[0] if candidates else (LocatorStrategy.VISIBLE_TEXT, target_elem.query)
            return (None, first_sel, first_strat)

        for strategy, selector in candidates:
            try:
                if hasattr(page_handle, "query_selector"):
                    elem = await page_handle.query_selector(selector)
                    if elem:
                        logger.info(f"Located element with strategy '{strategy.value}': '{selector}'")
                        return (elem, selector, strategy)
            except Exception as e:
                logger.debug(f"Selector '{selector}' attempt failed: {e}")

        logger.warning(f"Could not locate element for query '{target_elem.query}' across {len(candidates)} strategies")
        return (None, None, None)

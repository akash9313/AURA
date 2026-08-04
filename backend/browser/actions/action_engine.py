"""
Browser Action Engine Master Orchestrator.
Exposes clean, high-level, human-like browser action APIs (click, type, scroll, submit, upload, download)
with smart pre-checks, post-action verification, automatic transient retries, and telemetry.
"""

import asyncio
import logging
import time
from typing import Any, Dict, List, Optional, Union

from browser.actions.click import ClickActionExecutor
from browser.actions.download import DownloadActionExecutor
from browser.actions.events import ActionEvent
from browser.actions.forms import FormActionExecutor
from browser.actions.locator import SmartElementLocator
from browser.actions.models import (
    ActionEngineConfig,
    ActionHealthStatus,
    ActionOptions,
    ActionResult,
    ActionState,
    ActionType,
    DownloadResult,
    ScrollDirection,
    TargetElement,
)
from browser.actions.scrolling import ScrollActionExecutor
from browser.actions.typing import TypingActionExecutor
from browser.actions.upload import UploadActionExecutor
from browser.actions.verification import ActionVerifier
from browser.actions.waits import ActionWaitExecutor

logger = logging.getLogger("AURA.Browser.Actions.Engine")


class ActionEngine:
    """
    Production-grade Browser Action Engine orchestrator.
    Executes human-like, reliable, provider-independent browser interactions.
    """

    def __init__(
        self,
        bus: Any = None,
        config: Optional[ActionEngineConfig] = None,
        page_resolver: Any = None,
    ):
        self.bus = bus
        self.config = config or ActionEngineConfig()
        self.page_resolver = page_resolver

        self.locator = SmartElementLocator()
        self.waits = ActionWaitExecutor()
        self.verifier = ActionVerifier()

        self.click_executor = ClickActionExecutor()
        self.typing_executor = TypingActionExecutor()
        self.scroll_executor = ScrollActionExecutor()
        self.form_executor = FormActionExecutor()
        self.upload_executor = UploadActionExecutor()
        self.download_executor = DownloadActionExecutor()

        self.state: ActionState = ActionState.IDLE

        # Telemetry counters
        self._total_actions = 0
        self._successful_actions = 0
        self._failed_actions = 0
        self._total_execution_time_ms = 0.0
        self._last_error: Optional[str] = None

    def _resolve_page_handle(self, page_id: Optional[str] = None) -> Any:
        """Resolve a page ID to Playwright page handle or mock via page_resolver."""
        if self.page_resolver is None:
            return None
        if callable(self.page_resolver):
            return self.page_resolver(page_id)
        if hasattr(self.page_resolver, "get_page_handle"):
            return self.page_resolver.get_page_handle(page_id)
        return None

    # ------------------------------------------------------------------
    # Core Generic Action Execution with Retries & Pre/Post Checks
    # ------------------------------------------------------------------

    async def execute_action(
        self,
        action_type: ActionType,
        target: Any,
        value: Optional[Any] = None,
        page_id: Optional[str] = None,
        options: Optional[ActionOptions] = None,
    ) -> ActionResult:
        """
        Execute a browser action with smart location, pre-checks, retries, and post-verification.
        """
        start_time = time.time()
        opts = options or ActionOptions(
            timeout_ms=self.config.default_timeout_ms,
            retry_count=self.config.retry_count,
            retry_delay_ms=self.config.retry_delay_ms,
            human_delay_ms=self.config.human_interaction_delay_ms,
            typing_speed_cps=self.config.typing_speed_cps,
        )

        target_elem = self.locator.resolve_target(target)
        page_handle = self._resolve_page_handle(page_id)
        initial_url = page_handle.url if page_handle and hasattr(page_handle, "url") else ""

        self.state = ActionState.LOCATING
        self._publish_event(
            ActionEvent.ACTION_STARTED,
            {"action_type": action_type.value, "target": target_elem.query, "page_id": page_id},
        )

        last_error = None
        for attempt in range(opts.retry_count + 1):
            if attempt > 0:
                self.state = ActionState.RETRYING
                logger.info(f"Retrying action '{action_type.value}' ({attempt}/{opts.retry_count}) for '{target_elem.query}'...")
                await asyncio.sleep(opts.retry_delay_ms / 1000)

            # 1. Locate element
            elem_handle, selector, strategy = await self.locator.locate_element_handle(page_handle, target_elem)
            if elem_handle is None and page_handle is not None and not opts.force and action_type not in (ActionType.SCROLL, ActionType.KEYBOARD_SHORTCUT):
                last_error = f"Element not found for query: '{target_elem.query}'"
                self._publish_event(ActionEvent.ELEMENT_NOT_FOUND, {"query": target_elem.query})
                continue

            if elem_handle:
                self._publish_event(ActionEvent.ELEMENT_FOUND, {"query": target_elem.query, "selector": selector})

            # 2. Smart Pre-checks (existence, visibility, enabled, scroll into view)
            if self.config.enable_smart_prechecks:
                ready, pre_error = await self.waits.precheck_element(page_handle, elem_handle, options=opts)
                if not ready:
                    last_error = f"Precheck failed: {pre_error}"
                    logger.warning(f"Precheck failed for action '{action_type.value}': {pre_error}")
                    continue

            # 3. DOM Stability Wait
            await self.waits.wait_for_dom_stability(page_handle)

            # 4. Perform Primitive Action
            self.state = ActionState.EXECUTING
            try:
                success = await self._dispatch_primitive(
                    action_type=action_type,
                    page_handle=page_handle,
                    elem_handle=elem_handle,
                    value=value,
                    options=opts,
                )
                if not success:
                    last_error = f"Primitive execution failed for action '{action_type.value}'"
                    continue
            except Exception as e:
                last_error = str(e)
                logger.error(f"Action '{action_type.value}' failed during execution: {e}")
                continue

            # 5. Smart Post-verification
            verified = True
            if self.config.enable_smart_verification and opts.verify_result:
                self.state = ActionState.VERIFYING
                verified, v_note = await self.verifier.verify_action(
                    action_type=action_type,
                    page_handle=page_handle,
                    element_handle=elem_handle,
                    expected_value=value,
                    initial_url=initial_url,
                )
                logger.debug(f"Action verification note: {v_note}")

            execution_time_ms = round((time.time() - start_time) * 1000, 2)
            result = ActionResult(
                success=True,
                action_type=action_type,
                target_query=target_elem.query,
                target_selector=selector,
                execution_time_ms=execution_time_ms,
                verified=verified,
                retry_attempts=attempt,
                state=ActionState.COMPLETED,
            )

            self._record_telemetry(result)
            self.state = ActionState.IDLE
            self._publish_event(ActionEvent.ACTION_COMPLETED, result.to_dict())

            if action_type == ActionType.SUBMIT_FORM:
                self._publish_event(ActionEvent.FORM_SUBMITTED, {"target": target_elem.query})

            return result

        # Exhausted retries
        execution_time_ms = round((time.time() - start_time) * 1000, 2)
        failure_result = ActionResult(
            success=False,
            action_type=action_type,
            target_query=target_elem.query,
            execution_time_ms=execution_time_ms,
            error=last_error or "Action failed after retry attempts",
            retry_attempts=opts.retry_count,
            state=ActionState.FAILED,
        )

        self._record_telemetry(failure_result)
        self.state = ActionState.FAILED
        self._publish_event(ActionEvent.ACTION_FAILED, failure_result.to_dict())
        return failure_result

    async def _dispatch_primitive(
        self,
        action_type: ActionType,
        page_handle: Any,
        elem_handle: Any,
        value: Optional[Any],
        options: ActionOptions,
    ) -> bool:
        """Dispatch action type to corresponding primitive executor."""
        if action_type == ActionType.CLICK:
            return await self.click_executor.click(elem_handle, options=options)
        if action_type == ActionType.DOUBLE_CLICK:
            return await self.click_executor.double_click(elem_handle, options=options)
        if action_type == ActionType.RIGHT_CLICK:
            return await self.click_executor.right_click(elem_handle, options=options)
        if action_type == ActionType.HOVER:
            return await self.click_executor.hover(elem_handle, options=options)
        if action_type == ActionType.FOCUS:
            return await self.click_executor.focus(elem_handle, options=options)
        if action_type == ActionType.BLUR:
            return await self.click_executor.blur(elem_handle, options=options)

        if action_type == ActionType.TYPE_TEXT:
            return await self.typing_executor.type_text(elem_handle, str(value or ""), options=options)
        if action_type == ActionType.CLEAR_FIELD:
            return await self.typing_executor.clear_field(elem_handle, options=options)
        if action_type == ActionType.PASTE:
            return await self.typing_executor.paste(elem_handle, str(value or ""), options=options)
        if action_type == ActionType.KEYBOARD_SHORTCUT:
            return await self.typing_executor.press_shortcut(page_handle, str(value or ""), options=options)

        if action_type == ActionType.SCROLL:
            direction = value if isinstance(value, ScrollDirection) else ScrollDirection.DOWN
            return await self.scroll_executor.scroll(page_handle, direction=direction, element_handle=elem_handle, options=options)

        if action_type == ActionType.SELECT_DROPDOWN:
            return await self.form_executor.select_dropdown(elem_handle, str(value or ""), options=options)
        if action_type == ActionType.CHECK_CHECKBOX:
            return await self.form_executor.check_checkbox(elem_handle, options=options)
        if action_type == ActionType.UNCHECK_CHECKBOX:
            return await self.form_executor.uncheck_checkbox(elem_handle, options=options)
        if action_type == ActionType.SUBMIT_FORM:
            return await self.form_executor.submit_form(elem_handle or page_handle, options=options)

        if action_type == ActionType.UPLOAD_FILE:
            return await self.upload_executor.upload_file(elem_handle, value, options=options)

        if action_type == ActionType.DRAG_AND_DROP:
            target_handle = self._resolve_page_handle(value) if isinstance(value, str) else value
            return await self.click_executor.drag_and_drop(elem_handle, target_handle, options=options)

        return True

    # ------------------------------------------------------------------
    # High-level Convenience API consumed by Workflow Engine & LLM
    # ------------------------------------------------------------------

    async def click(self, target: Any, page_id: Optional[str] = None, options: Optional[ActionOptions] = None) -> ActionResult:
        """Click on an element by human query, label, or selector."""
        return await self.execute_action(ActionType.CLICK, target, page_id=page_id, options=options)

    async def double_click(self, target: Any, page_id: Optional[str] = None, options: Optional[ActionOptions] = None) -> ActionResult:
        """Double click on an element."""
        return await self.execute_action(ActionType.DOUBLE_CLICK, target, page_id=page_id, options=options)

    async def right_click(self, target: Any, page_id: Optional[str] = None, options: Optional[ActionOptions] = None) -> ActionResult:
        """Right click / context click on an element."""
        return await self.execute_action(ActionType.RIGHT_CLICK, target, page_id=page_id, options=options)

    async def hover(self, target: Any, page_id: Optional[str] = None, options: Optional[ActionOptions] = None) -> ActionResult:
        """Hover over an element."""
        return await self.execute_action(ActionType.HOVER, target, page_id=page_id, options=options)

    async def type(self, target: Any, text: str, page_id: Optional[str] = None, options: Optional[ActionOptions] = None) -> ActionResult:
        """Type text into an element."""
        return await self.execute_action(ActionType.TYPE_TEXT, target, value=text, page_id=page_id, options=options)

    async def clear(self, target: Any, page_id: Optional[str] = None, options: Optional[ActionOptions] = None) -> ActionResult:
        """Clear text in an input field."""
        return await self.execute_action(ActionType.CLEAR_FIELD, target, page_id=page_id, options=options)

    async def select(self, target: Any, option: str, page_id: Optional[str] = None, options: Optional[ActionOptions] = None) -> ActionResult:
        """Select an option in a dropdown menu."""
        return await self.execute_action(ActionType.SELECT_DROPDOWN, target, value=option, page_id=page_id, options=options)

    async def check(self, target: Any, page_id: Optional[str] = None, options: Optional[ActionOptions] = None) -> ActionResult:
        """Check a checkbox."""
        return await self.execute_action(ActionType.CHECK_CHECKBOX, target, page_id=page_id, options=options)

    async def uncheck(self, target: Any, page_id: Optional[str] = None, options: Optional[ActionOptions] = None) -> ActionResult:
        """Uncheck a checkbox."""
        return await self.execute_action(ActionType.UNCHECK_CHECKBOX, target, page_id=page_id, options=options)

    async def scroll(
        self,
        direction: ScrollDirection = ScrollDirection.DOWN,
        target: Optional[Any] = None,
        page_id: Optional[str] = None,
        options: Optional[ActionOptions] = None,
    ) -> ActionResult:
        """Scroll page or specific target container."""
        return await self.execute_action(ActionType.SCROLL, target or "", value=direction, page_id=page_id, options=options)

    async def submit(self, target: Any, page_id: Optional[str] = None, options: Optional[ActionOptions] = None) -> ActionResult:
        """Submit a form or form button."""
        return await self.execute_action(ActionType.SUBMIT_FORM, target, page_id=page_id, options=options)

    async def upload(self, target: Any, file_paths: Union[str, List[str]], page_id: Optional[str] = None, options: Optional[ActionOptions] = None) -> ActionResult:
        """Upload file(s) to a file input element."""
        return await self.execute_action(ActionType.UPLOAD_FILE, target, value=file_paths, page_id=page_id, options=options)

    async def download(
        self,
        target: Any,
        download_directory: Optional[str] = None,
        page_id: Optional[str] = None,
        options: Optional[ActionOptions] = None,
    ) -> ActionResult:
        """Click a link/button and intercept the file download."""
        page_handle = self._resolve_page_handle(page_id)
        start_time = time.time()

        self._publish_event(ActionEvent.DOWNLOAD_STARTED, {"target": str(target)})

        async def trigger():
            await self.click(target, page_id=page_id, options=options)

        dl_res = await self.download_executor.download_file(
            page_handle=page_handle,
            trigger_action=trigger,
            download_directory=download_directory or self.config.default_download_directory,
            options=options,
        )

        exec_time_ms = round((time.time() - start_time) * 1000, 2)
        action_res = ActionResult(
            success=dl_res.success,
            action_type=ActionType.DOWNLOAD_FILE,
            target_query=str(target),
            execution_time_ms=exec_time_ms,
            verified=dl_res.success,
            download_info=dl_res,
            error=dl_res.error,
        )

        self._record_telemetry(action_res)
        if dl_res.success:
            self._publish_event(ActionEvent.DOWNLOAD_COMPLETED, dl_res.to_dict())
        else:
            self._publish_event(ActionEvent.ACTION_FAILED, {"error": dl_res.error})

        return action_res

    # ------------------------------------------------------------------
    # Telemetry and Health
    # ------------------------------------------------------------------

    def get_health_status(self) -> ActionHealthStatus:
        """Get current health telemetry for the Action Engine."""
        avg_time = (self._total_execution_time_ms / self._total_actions) if self._total_actions > 0 else 0.0
        return ActionHealthStatus(
            state=self.state,
            total_actions=self._total_actions,
            successful_actions=self._successful_actions,
            failed_actions=self._failed_actions,
            average_execution_time_ms=round(avg_time, 2),
            last_error=self._last_error,
        )

    def _record_telemetry(self, result: ActionResult) -> None:
        """Record action telemetry stats."""
        self._total_actions += 1
        self._total_execution_time_ms += result.execution_time_ms
        if result.success:
            self._successful_actions += 1
        else:
            self._failed_actions += 1
            self._last_error = result.error

    def _publish_event(self, event: ActionEvent, data: Dict[str, Any]) -> None:
        """Publish event to AURA EventBus."""
        if self.bus:
            try:
                self.bus.publish(event.value, data)
            except Exception as e:
                logger.error(f"Failed to publish action event '{event.value}': {e}")

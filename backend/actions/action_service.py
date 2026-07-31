import logging
from core.service import Service
from core.events import Event
from tools.registry import ToolRegistry
from tools.result import ToolResult

logger = logging.getLogger("AURA.ActionService")


class ActionService(Service):
    """
    ActionService orchestrates tool execution based on intents received from the EventBus.
    
    Adheres strictly to the Open-Closed Principle:
    Tool lookup and execution are delegated entirely to the ToolRegistry and modular Tool classes.
    Contains no hardcoded tool-specific business logic or conditional branches.
    """

    def __init__(self, bus, registry: ToolRegistry = None):
        """
        Initialize ActionService.

        Args:
            bus (EventBus): AURA EventBus instance.
            registry (ToolRegistry, optional): ToolRegistry instance. If None, instantiates a default auto-discovering registry.
        """
        super().__init__(bus)
        self.registry = registry if registry is not None else ToolRegistry(auto_discover=True)

    def start(self) -> None:
        """Start listening for intent and action events on the EventBus."""
        logger.info("Action Service Started")

        self.bus.subscribe(
            Event.INTENT_READY,
            self.on_action
        )

        self.bus.subscribe(
            Event.ACTION_READY,
            self.on_action
        )

    def stop(self) -> None:
        """Stop ActionService."""
        logger.info("Action Service Stopped")

    def on_action(self, intent) -> None:
        """
        Handle incoming intent event by dynamically fetching and executing the matching tool.

        Args:
            intent: Object containing `name` (str) and `parameters` (dict).
        """
        tool_name = getattr(intent, "name", None) or (intent.get("name") if isinstance(intent, dict) else None)
        parameters = getattr(intent, "parameters", {}) if not isinstance(intent, dict) else intent.get("parameters", {})

        logger.info(f"⚙️ Action requested: '{tool_name}'")

        if not tool_name:
            logger.warning("Action request missing tool name.")
            self.bus.publish(
                Event.AI_RESPONSE_READY,
                "Invalid action request: missing tool name."
            )
            return

        # 1. Ask registry for tool
        tool = self.registry.get(tool_name)

        if tool:
            try:
                # 2. Execute tool & 3. Receive ToolResult
                result: ToolResult = tool.execute(parameters)
                logger.info(f"Tool '{tool_name}' executed in {result.execution_time:.3f}s. Success: {result.success}")

                # 4. Publish AI_RESPONSE_READY
                self.bus.publish(
                    Event.AI_RESPONSE_READY,
                    result.message
                )
            except Exception as e:
                logger.error(f"Execution error for tool '{tool_name}': {e}")
                self.bus.publish(
                    Event.AI_RESPONSE_READY,
                    f"An error occurred while executing {tool_name}: {e}"
                )
        else:
            logger.warning(f"No tool registered for action: '{tool_name}'")
            self.bus.publish(
                Event.AI_RESPONSE_READY,
                f"I don't know how to do '{tool_name}' yet."
            )
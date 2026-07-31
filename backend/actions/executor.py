from tools.registry import ToolRegistry


class ActionExecutor:

    def __init__(self, registry: ToolRegistry = None):
        self.registry = registry or ToolRegistry()

    def execute(self, intent, parameters=None):
        """
        Executes an action intent using registered tools.

        Args:
            intent: Intent object (with .name and .parameters),
                    dict (with 'name' and 'parameters'),
                    or tool name string.
            parameters: Optional dict if intent is passed as string name.

        Returns:
            dict: Execution result dictionary with 'success' and 'message'.
        """
        if isinstance(intent, str):
            name = intent
            params = parameters if parameters is not None else {}
        elif isinstance(intent, dict):
            name = intent.get("name")
            params = intent.get("parameters", {})
        else:
            name = getattr(intent, "name", None)
            params = getattr(intent, "parameters", {})

        tool = self.registry.get(name)

        if not tool:
            return {
                "success": False,
                "message": "I don't know how to do that yet."
            }

        return tool.execute(params)

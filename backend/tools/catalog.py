class ToolCatalog:

    def __init__(self, registry):
        self.registry = registry

    def describe(self):

        return [
            {
                "name": tool.name,
                "description": tool.description
            }
            for tool in self.registry.tools.values()
        ]
# AURA Tool Framework Architecture Documentation

## Overview

The **AURA Tool Framework** provides an extensible, modular, SOLID-compliant architecture that transforms AURA from a basic conversational assistant into an AI Operating System Agent capable of executing complex desktop, system, and cloud actions.

---

## Architectural Principles (SOLID)

### 1. Single Responsibility Principle (SRP)
- **`Tool`**: Defines contract and execution logic for a single capability.
- **`ToolResult`**: Holds standard execution metadata (`success`, `message`, `data`, `execution_time`).
- **`ToolRegistry`**: Manages registration, storage, lookup, and categorization of tools.
- **`discover_tools`**: Handles dynamic scanning and module loading.
- **`ActionService`**: Orchestrates event bus communication and tool execution without containing business logic.

### 2. Open-Closed Principle (OCP)
The framework is **open for extension but closed for modification**:
- Adding support for new tools (e.g. Browser, Spotify, Docker, VSCode, FileSystem, Terminal) simply requires dropping a new `Tool` subclass file into `backend/tools/<category>/`.
- **`ActionService` and `ToolRegistry` require ZERO code changes** to support hundreds of future tools.

### 3. Liskov Substitution Principle (LSP)
- All concrete tool classes (`OpenApplicationTool`, `CalculatorTool`, `ChatTool`) inherit from abstract base class `Tool` and strictly adhere to the `execute(parameters) -> ToolResult` contract.
- Any tool instance can be transparently substituted and executed by `ActionService`.

### 4. Interface Segregation Principle (ISP)
- The `Tool` abstract base class defines a lean, focused interface requiring only `name`, `description`, `category`, and `execute()`.

### 5. Dependency Inversion Principle (DIP)
- `ActionService` depends upon abstractions (`Tool` base class and `ToolRegistry` interface) rather than concrete tool implementations.

---

## Component Architecture Diagram

```
 +------------------+           +----------------------+
 |  EventBus        |           |  ActionService       |
 |  (INTENT_READY)  |---------->|  (Event Handler)     |
 +------------------+           +----------+-----------+
                                           | (Lookup)
                                           v
 +-----------------------------------------------------+
 |                  ToolRegistry                       |
 |  - register(tool)                                   |
 |  - get(name) -> Tool                                |
 |  - discover_tools() [Dynamic Discovery]             |
 +-------------------------+---------------------------+
                           |
            +--------------+--------------+
            |                             |
            v                             v
 +----------------------+      +----------------------+
 | OpenApplicationTool  |      | CalculatorTool       |
 | (category="windows") |      | (category="windows") |
 +----------------------+      +----------------------+
            |                             |
            +--------------+--------------+
                           |
                           v
                 +-------------------+
                 |    ToolResult     |
                 | - success: bool   |
                 | - message: str    |
                 | - execution_time  |
                 +-------------------+
```

---

## Dynamic Discovery Mechanism

`backend/tools/discovery.py` scans subpackages within `backend/tools/` using Python's `pkgutil` and `importlib`. It automatically finds non-abstract subclasses of `Tool`, instantiates them, and registers them in `ToolRegistry` upon startup.

### Adding a New Tool in 3 Steps:
1. Create a file under `backend/tools/<category>/<my_tool>.py`.
2. Define a class extending `Tool`:
```python
from tools.base import Tool
from tools.result import ToolResult

class MyCustomTool(Tool):
    @property
    def name(self) -> str:
        return "my_custom_tool"

    @property
    def description(self) -> str:
        return "Description of custom tool"

    @property
    def category(self) -> str:
        return "custom"

    def execute(self, parameters: dict) -> ToolResult:
        # Implementation logic
        return ToolResult(success=True, message="Completed successfully")
```
3. Done! The tool is automatically discovered, registered, and executable by `ActionService`.

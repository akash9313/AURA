# AURA AI Operating System — Engineering Constitution

> **Document Authority**: Highest Technical Authority & Architecture Standard  
> **Target Audience**: Core Engineers, AI Agents, Open-Source Contributors, Technical Reviewers  
> **Status**: Approved & Enforced  

---

## 1. Mission & Engineering Philosophy

### 1.1 Mission
To build the world's most capable, private, and extensible autonomous AI Operating System (AURA) that seamlessly translates human natural language intent into deterministic computer execution across desktop, cloud, browser, and hardware environments.

### 1.2 Vision
AURA redefines computing by replacing static file systems and application silos with a **Cognitive Event-Driven Kernel (AuraEngine)**. Computing should be natural, voice-first, visually aware, memory-retaining, and policy-governed.

### 1.3 Engineering Philosophy
1. **Determinism at the Boundary**: While AI model reasoning is probabilistic, core OS execution, tool invocation, and state management MUST be 100% deterministic and predictable.
2. **Local-First & Privacy by Default**: User data, personal facts, and workspace contexts belong to the user. AURA operates fully offline for local tasks and uses end-to-end encryption for cloud offloading.
3. **Decoupled Architecture**: Business logic NEVER lives inside UI components or external service wrappers. Everything communicates asynchronously through event channels.

---

## 2. Engineering Values

1. **Simplicity Over Cleverness**: Code must be readable by any engineer within 30 seconds. Avoid esoteric Python tricks, deep inheritance trees, and implicit magic.
2. **Composition Over Inheritance**: Prefer composing behaviors with modular classes and dependency injection over extending complex base classes.
3. **Interfaces Over Concrete Implementations**: Every service, provider, and tool must depend on abstract base classes (`ABC`). Never couple high-level modules directly to low-level APIs.
4. **Dependency Injection Everywhere**: Inject dependencies explicitly via constructors (`__init__`). Never instantiate third-party clients directly inside deep business logic.
5. **Loose Coupling & High Cohesion**: Services must be unaware of each other's internal logic. A service publishes events on the `EventBus` without knowing who consumes them.
6. **AI & Provider Agnostic**: AURA must operate identically regardless of whether the backend LLM is Gemini, OpenAI, Anthropic, or a local Llama model via Ollama.
7. **Tool Framework Extensibility**: Every capability must be wrapped as a modular `Tool` returning a standardized `ToolResult`.

---

## 3. Architecture Rules

### 3.1 Event-Driven Decoupling
- Services MUST NOT import or invoke methods on sibling services directly.
- All inter-service communication passes through `EventBus.publish(event_type, data)`.
- Handlers MUST NOT perform long-running blocking synchronous calls directly inside an event callback thread; heavy tasks must be offloaded to worker pools.

### 3.2 Module & Package Responsibilities
```
backend/
  core/       # Pure kernel, engine runtime, event bus, base service interface, events enum
  ai/         # Provider abstractions (Gemini, OpenAI, Local), prompts, intent classifier
  speech/     # Speech-to-text, text-to-speech, audio recording, input fallback
  brain/      # Intent processing, routing, brain service
  actions/    # Tool invocation execution service
  tools/      # Atomic Tool implementations (Windows, Vision, Browser, Chat)
  memory/     # Working, Conversation, Profile, Knowledge memories & SQLite Repository
  vision/     # Screenshot, Camera, OCR, UIDetector, ObjectDetector, Vision Pipeline
  agent/      # Agent Orchestrator ("CEO"), Planner, Task Graph, TaskExecutor, Retry
  windows/    # OS Automation Engine (AppManager, WindowManager, Keyboard, Mouse, Clipboard)
  browser/    # Autonomous Web Agent (Navigator, Extractor, Forms, Tabs, Downloads)
  runtime/    # Heartbeat, process control, runtime lifecycle
```

### 3.3 Limits & Metrics
- **Maximum File Size**: 400 lines of code (excluding inline documentation).
- **Maximum Function Length**: 40 lines of code.
- **Maximum Cyclomatic Complexity**: 10 per function.
- **No Circular Imports**: Strictly forbidden. Modules imported in lower layers (`core`) must never import from higher layers (`agent`, `windows`, `browser`).

---

## 4. Coding Standards

### 4.1 Python Standards
- **Python Version**: Python 3.14+ compatible standard syntax.
- **Type Annotations**: Mandatory explicit type hints (`str`, `int`, `Dict[str, Any]`, `Optional[T]`) on all function signatures.
- **Formatting**: PEP 8 strict compliance (4 spaces indentation, 120 max line length).

### 4.2 Naming Conventions
- **Files & Modules**: `snake_case.py` (e.g., `intent_classifier.py`, `action_service.py`).
- **Classes**: `PascalCase` (e.g., `AgentOrchestrator`, `WindowsAutomationManager`).
- **Methods & Functions**: `snake_case()` (e.g., `process_goal()`, `execute_task()`).
- **Constants**: `UPPER_SNAKE_CASE` (e.g., `GEMINI_API_KEY`, `MAX_RETRIES`).
- **Enums**: `PascalCase` class name, `UPPER_SNAKE_CASE` member values.

### 4.3 Dataclasses & Models
- Use `@dataclass` for all internal state containers (`Task`, `Workflow`, `ToolResult`, `AutomationResult`, `BrowserResult`).
- All dataclasses MUST include a `.to_dict()` serialization method for API JSON logging.

### 4.4 Logging & Exception Standards
- Standard library `logging.getLogger("AURA.<Subsystem>")` MUST be used.
- NEVER use bare `print()` statements in core engine code.
- NEVER use silent empty `except:` blocks. All exceptions MUST be logged with descriptive context before fallback or re-raising.

---

## 5. Testing Standards

### 5.1 Test Organization
- Unit tests MUST reside in `backend/tests/` matching module names (`test_memory_engine.py`, `test_vision_engine.py`, `test_agent_orchestrator.py`, `test_windows_automation.py`, `test_browser_agent.py`).

### 5.2 Test Coverage & Mocking
- **Target Coverage**: 85%+ code coverage across business logic modules.
- **Mocking External APIs**: Subprocess calls (`Popen`), external network requests, hardware devices (Camera, Mic), and paid LLM APIs MUST be mocked using `unittest.mock.patch` in automated test suites.
- **Test Speed**: Unit test suites MUST complete execution within 10 seconds locally.

---

## 6. AI & Engine Design Principles

1. **Structured Outputs**: All intent classification and LLM reasoning MUST return schema-validated JSON.
2. **Fallback Intent Classification**: If an LLM API returns rate limit errors (429) or network timeouts, the system MUST automatically fall back to rule-based keyword classification without crashing.
3. **Prompt Integrity**: System prompts MUST be stored in explicit prompt text files inside `ai/prompts/` rather than hardcoded inline in Python strings.
4. **Context Window Management**: Multi-turn conversation messages MUST be truncated dynamically to fit within model context windows using sliding context buffers.

---

## 7. Security & Safety Principles

1. **Permission Classification**: All OS and Web actions MUST pass through `PermissionManager` or `BrowserPermissionManager`.
2. **Safety Policies**:
   - `ALWAYS_ALLOWED`: Read-only queries, typing, opening applications, navigation, screenshots.
   - `REQUIRES_CONFIRMATION`: File deletions, form submissions, payment fields, account changes.
   - `BLOCKED`: Formatted drive commands, malicious shell commands.
3. **Audit Trail**: Every executed action MUST write an immutable `ActionLog` entry containing timestamp, application, parameters, duration, and result.

---

## 8. Product & UX Design Principles

1. **Invisible Copilot UX**: AURA should stay out of the user's way until invoked via global shortcut or voice wake-word.
2. **Visual Feedback**: Micro-animations, progress indicators, and toast notifications must inform the user when complex multi-step workflows are running in the background.
3. **Voice Responsiveness**: Voice synthesis (TTS) must begin within 500ms of natural text completion.

---

## 9. Plugin System & Sandbox Standards

1. **Plugin Isolation**: Plugins run inside sandboxed processes with explicit permission boundaries.
2. **Standardized Metadata**: Every plugin MUST declare a `plugin.json` manifest specifying required permissions, dependencies, and author metadata.
3. **Zero Code Churn**: Modifying or registering a plugin MUST NOT require modifying core engine files.

---

## 10. Database & Repository Standards

1. **Repository Pattern**: All database access MUST use `BaseMemoryRepository` / `SQLiteMemoryRepository`. No raw SQL queries inside engine services.
2. **SQLite Configuration**: SQLite MUST use WAL mode (`PRAGMA journal_mode=WAL;`), foreign key enforcement (`PRAGMA foreign_keys=ON;`), and indexed primary/foreign keys.
3. **Atomic Transactions**: Multi-table updates MUST execute within atomic database transaction blocks.

---

## 11. Performance & Memory Limits

1. **Non-Blocking UI & Main Threads**: Never invoke blocking synchronizations or sleep calls on main UI loops.
2. **Resource Capping**: Memory footprint of the core local background daemon MUST remain under 250 MB RAM at idle.
3. **Execution Time Metrics**: Every tool and sub-manager action MUST measure exact execution duration (`execution_time`) in seconds.

---

## 12. Code Review Checklist (Pull Request Requirements)

Every Pull Request MUST satisfy:
- [ ] Architecture: Conforms to EventBus decoupling and SOLID principles.
- [ ] Interfaces: All providers implement abstract base classes.
- [ ] Type Hints: 100% typing on public function signatures.
- [ ] Exception Safety: No silent swallows; 429 and network errors handled.
- [ ] Testing: Unit test added and verified (`python -m unittest discover`).
- [ ] Logs: Action logs and audit records populated cleanly.

---

## 13. Project Evolution Roadmap

```
  PROTOTYPE (v1.0)        STARTUP / MVP (v2.0 - v4.0)     ENTERPRISE (v5.0 - v8.0)        GLOBAL AI OS (v9.0 - v10.0)
--------------------      ---------------------------     ------------------------        ---------------------------
• In-Process EventBus     • Local Vector RAG              • Distributed Microservices     • Native Microkernel
• SQLite Local DB         • Multi-Tab Web Crawling        • Multi-Agent Swarms            • Marketplace & Ecosystem
• Direct Tool Registry    • Persistent Desktop Context    • Cloud Container Sandbox       • Bare-Metal Hardware NPU
```

---

## 14. Non-Negotiable Engineering Rules (The 100 Rules)

### Architecture & Service Decoupling (Rules 1–15)
1. Never import a service directly into another service; communicate only via `EventBus`.
2. Never instantiate third-party API clients directly inside core engine business logic.
3. Never bypass abstract base interfaces when declaring providers or tools.
4. Never write concrete business logic inside the main `AuraEngine` class.
5. Always inherit background services from `core.service.Service`.
6. Always register services explicitly with `AuraEngine.register()`.
7. Never allow circular imports between packages.
8. Always isolate third-party SDK dependencies inside dedicated `providers/` modules.
9. Never execute blocking synchronous code directly inside an EventBus listener callback.
10. Always emit completion events when asynchronous background operations finish.
11. Never couple UI components to database layer abstractions directly.
12. Always wrap tool output in standardized `ToolResult` dataclass containers.
13. Never let lower-level kernel packages import higher-level application modules.
14. Always handle engine shutdown cleanly by implementing `Service.stop()`.
15. Never hardcode file paths relative to absolute user desktop directories.

### Coding Standards & Quality (Rules 16–30)
16. Always include explicit type hints for function parameters and return types.
17. Never use bare `print()` statements; always use `logging.getLogger()`.
18. Always format code to PEP 8 standard with 4 spaces for indentation.
19. Never keep functions longer than 40 lines of code.
20. Never let a single module file exceed 400 lines of code.
21. Always name classes in `PascalCase` and functions/methods in `snake_case`.
22. Always use `UPPER_SNAKE_CASE` for global constants and configuration variables.
23. Always implement `.to_dict()` on internal state dataclasses.
24. Never swallow exceptions silently using `except: pass`.
25. Always catch specific exceptions (`ClientError`, `FileNotFoundError`, `TimeoutError`).
26. Always document public classes and methods with clear Python docstrings.
27. Never use mutable default arguments (`def foo(opts={})`); use `None` and initialize inside.
28. Always keep class cyclomatic complexity under 10.
29. Never use global variables for mutable application state.
30. Always validate function argument ranges and non-null states before execution.

### Tool & Framework Execution (Rules 31–45)
31. Every executable action MUST inherit from `tools.base.Tool`.
32. Every tool MUST declare unique `name`, `description`, and `category` properties.
33. Never hardcode tool conditional checks inside `ActionService`.
34. Always discover tools dynamically using `ToolRegistry(auto_discover=True)`.
35. Always return `ToolResult` with `success`, `message`, `data`, and `execution_time`.
36. Always measure task execution duration using `time.time()`.
37. Never raise uncaught exceptions out of `Tool.execute()`; capture into `ToolResult`.
38. Always validate parameter types inside `Tool.execute()` before running business logic.
39. Never allow duplicate tool names inside `ToolRegistry`.
40. Always register tools in subpackages matching their category (`windows/`, `vision/`, `browser/`).
41. Never execute external system commands without validating parameter bounds.
42. Always support fallback execution when primary external libraries are missing.
43. Never mix UI rendering code inside tool execution modules.
44. Always ensure tools remain stateless across multiple invocations.
45. Always write dedicated unit tests for every custom `Tool`.

### Memory & Persistence (Rules 46–60)
46. Never query SQLite database directly inside AI models; use `SQLiteMemoryRepository`.
47. Always run SQLite database connections in WAL mode (`PRAGMA journal_mode=WAL;`).
48. Always enforce foreign key constraints (`PRAGMA foreign_keys=ON;`).
49. Never store unindexed text queries without primary key identifiers.
50. Always execute multi-statement updates within atomic database transaction blocks.
51. Never store raw unparsed JSON strings in database columns when structured schemas exist.
52. Always close database connections cleanly during engine shutdown.
53. Never allow database locks to block main thread execution.
54. Always isolate working memory transient variables from permanent profile storage.
55. Always sanitize user input parameters before inserting into database queries.
56. Always persist completed workflow task graphs into Memory Engine for audit history.
57. Never delete user memory records without explicit user authorization events.
58. Always use repository pattern interfaces (`BaseMemoryRepository`) for database access.
59. Always log database connection failures and query errors.
60. Always cap working memory state size to prevent unbounded memory growth.

### Agent Orchestration & Planning (Rules 61–75)
61. The `AgentOrchestrator` MUST control the goal execution lifecycle.
62. Every workflow MUST track explicit state transitions (`CREATED` → `PLANNING` → `RUNNING` → `COMPLETED`).
63. Tasks MUST declare dependencies and execute only when parent tasks complete.
64. Always use `TaskValidator` to verify tool eligibility and parameter schemas.
65. Always apply `RetryStrategy` with exponential backoff on transient task failures.
66. Never execute a task if parent dependencies failed or were cancelled.
67. Always log timeline events (`TASK_STARTED`, `TASK_COMPLETED`, `TASK_FAILED`) in `AgentHistory`.
68. Never hardcode LLM prompts directly inside planner loops; load from `ai/prompts/`.
69. Always provide rule-based heuristic planner fallback when LLM API is rate-limited.
70. Always measure total workflow execution time from start to termination.
71. Never deadlock task queues when unresolvable dependencies occur; fail gracefully.
72. Always publish `WORKFLOW_COMPLETED` or `WORKFLOW_FAILED` events upon workflow termination.
73. Always store planner notes and intermediate task outputs inside `AgentContext`.
74. Never modify task graph IDs dynamically during active task execution.
75. Always limit max retries per task to prevent infinite loops.

### Security, Safety & Automation (Rules 76–90)
76. Never hardcode API keys, passwords, or tokens in source code files.
77. Always load credentials from secure environment variables (`core.config`).
78. All OS automation actions MUST pass through `PermissionManager`.
79. High-risk operations (file deletion, form submission) MUST enforce confirmation policies.
80. Every Windows automation action MUST produce an immutable `ActionLog` entry.
81. Never execute destructive system shell commands without policy verification.
82. Always check administrative privileges before running system elevated actions.
83. Web browser actions MUST evaluate `BrowserPermissionManager` safety rules.
84. Always sanitize scraped HTML strings to prevent script injection vulnerabilities.
85. Never expose raw internal exception tracebacks to end-user UI screens.
86. Always run untrusted third-party plugins in sandboxed subprocess environments.
87. Always support emergency stop signals to cancel active desktop automation loops.
88. Never bypass safety checks during automated unit testing runs.
89. Always record failure reasons inside `AutomationResult` or `BrowserResult`.
90. Never store unencrypted user credentials in local disk files.

### Testing, Quality & Performance (Rules 91–100)
91. Never mark a task completed without running automated test verification.
92. Always mock network requests, paid LLM APIs, and hardware peripherals in unit tests.
93. Every new service MUST include a matching test file in `backend/tests/`.
94. Test suites MUST pass with 100% success (`OK`) before merging pull requests.
95. Idle RAM footprint of the background daemon MUST remain under 250 MB.
96. Never block the main UI event loop with heavy disk or network I/O.
97. Always cap unit test suite execution time under 10 seconds.
98. Never ignore command failures or exit codes in automated build scripts.
99. Always maintain backward compatibility for existing event enums and public APIs.
100. The Engineering Constitution is the supreme authority; all code must comply.

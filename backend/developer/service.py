import logging
from core.events import Event
from core.service import Service
from developer.code_analyzer import CodeAnalyzer
from developer.debugger import ExceptionDebugger
from developer.dependency_manager import DependencyManager
from developer.documentation import DocumentationGenerator
from developer.events import DeveloperEvent
from developer.git import GitManager
from developer.project_manager import ProjectManager
from developer.repository_manager import RepositoryManager
from developer.terminal import TerminalController
from developer.testing import TestRunner
from developer.vscode import VSCodeController

logger = logging.getLogger("AURA.Developer.Service")


class DeveloperService(Service):
    """
    Developer Service wrapper connecting Developer Mode components to EventBus.
    """

    def __init__(self, bus):
        super().__init__(bus)
        self.terminal = TerminalController()
        self.project_manager = ProjectManager()
        self.repository_manager = RepositoryManager()
        self.vscode = VSCodeController(terminal=self.terminal)
        self.git = GitManager(terminal=self.terminal)
        self.debugger = ExceptionDebugger()
        self.analyzer = CodeAnalyzer()
        self.doc_gen = DocumentationGenerator()
        self.test_runner = TestRunner(terminal=self.terminal)
        self.dependency_manager = DependencyManager(terminal=self.terminal)

    def start(self):
        logger.info("Developer Service Started.")
        if self.bus:
            self.bus.subscribe(Event.GOAL_CREATED, self.on_goal_created)

    def on_goal_created(self, payload):
        goal = payload.get("goal", "").lower()
        if "open" in goal and "project" in goal:
            logger.info("Developer Service processing project open goal.")

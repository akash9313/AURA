from core.engine import AuraEngine
from speech.speech_service import SpeechService
from brain.brain_service import BrainService
from actions.action_service import ActionService
from runtime.runtime_service import RuntimeService
from speech.input_service import InputService
from memory.service import MemoryService
from vision.service import VisionService
from agent.service import AgentService
from windows.service import WindowsService
from browser.service import BrowserService
from cognition.service import CognitiveService
from cloud.service import CloudService
from computer.service import ComputerUseService
from developer.service import DeveloperService
from knowledge.service import KnowledgeService
from learning.service import LearningService
from plugins.service import PluginService
from workflow.service import WorkflowService


def main():
    engine = AuraEngine()

    engine.register("speech", SpeechService(engine.bus))
    engine.register("brain", BrainService(engine.bus))
    engine.register("memory", MemoryService(engine.bus))
    engine.register("vision", VisionService(engine.bus))
    engine.register("cognition", CognitiveService(engine.bus))
    engine.register("agent", AgentService(engine.bus))
    engine.register("workflow", WorkflowService(engine.bus))
    engine.register("learning", LearningService(engine.bus))
    engine.register("developer", DeveloperService(engine.bus))
    engine.register("knowledge", KnowledgeService(engine.bus))
    engine.register("plugins", PluginService(engine.bus))
    engine.register("cloud", CloudService(engine.bus))
    engine.register("windows", WindowsService(engine.bus))
    engine.register("browser", BrowserService(engine.bus))
    engine.register("computer", ComputerUseService(engine.bus))
    engine.register("action", ActionService(engine.bus))
    engine.register("runtime", RuntimeService(engine.bus))







    engine.register("input", InputService(engine.bus))

    engine.start()


if __name__ == "__main__":
    main()





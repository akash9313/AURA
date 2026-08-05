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
from api.service import APIService
from cloud.service import CloudService
from computer.service import ComputerService
from developer.service import DeveloperService
from knowledge.service import KnowledgeService
from learning.service import LearningService
from plugins.service import PluginService
from skills.service import SkillService
from workflow.service import WorkflowService
from speech.speech_service import SpeechService
from speech.vad.service import VADService
from speech.stt.service import STTService
from speech.tts.service import TTSService
from brain.brain_service import BrainService
from brain.streaming.service import StreamingBrainService
from conversation.service import ConversationService
from monitoring.service import MonitoringService
from config.service import ConfigService


def main():
    engine = AuraEngine()

    engine.register("config", ConfigService(engine.bus))
    engine.register("speech", SpeechService(engine.bus))
    engine.register("vad", VADService(engine.bus))
    engine.register("stt", STTService(engine.bus))
    engine.register("brain", BrainService(engine.bus))
    engine.register("streaming_brain", StreamingBrainService(engine.bus))
    engine.register("streaming_tts", TTSService(engine.bus))
    engine.register("conversation", ConversationService(engine.bus))
    engine.register("monitoring", MonitoringService(engine.bus))






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
    engine.register("api", APIService(engine.bus))
    engine.register("skills", SkillService(engine.bus))
    engine.register("windows", WindowsService(engine.bus))
    engine.register("browser", BrowserService(engine.bus))
    engine.register("computer", ComputerService(engine.bus))
    engine.register("action", ActionService(engine.bus))
    engine.register("runtime", RuntimeService(engine.bus))









    engine.register("input", InputService(engine.bus))

    engine.start()

    try:
        import time
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\nShutting down AURA AI Operating System...")


if __name__ == "__main__":
    main()





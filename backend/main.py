from core.engine import AuraEngine
from speech.speech_service import SpeechService
from brain.brain_service import BrainService
from actions.action_service import ActionService
from runtime.runtime_service import RuntimeService
from speech.input_service import InputService


def main():
    engine = AuraEngine()

    engine.register("speech", SpeechService(engine.bus))
    engine.register("brain", BrainService(engine.bus))
    engine.register("action", ActionService(engine.bus))
    engine.register("runtime", RuntimeService(engine.bus))
    engine.register("input", InputService(engine.bus))

    engine.start()


if __name__ == "__main__":
    main()
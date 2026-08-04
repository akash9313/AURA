from core.service import Service
from core.events import Event
from speech.audio_stream import ContinuousAudioPipeline, AudioStreamConfig
from speech.providers.edge_provider import speak
from speech.streaming.audio_pipeline import StreamingAudioPipeline


class SpeechService(Service):

    def __init__(self, bus, audio_config: AudioStreamConfig = None):
        super().__init__(bus)
        self.streaming_pipeline = StreamingAudioPipeline(bus=bus)
        self.continuous_audio = ContinuousAudioPipeline(bus=bus, config=audio_config)

    def start(self):
        print("Speech Service Started")

        self.bus.subscribe(
            Event.AI_RESPONSE_READY,
            self.on_ai_response
        )

        self.bus.subscribe(
            Event.SHUTDOWN,
            self.on_shutdown
        )

        # Start continuous audio pipeline
        self.continuous_audio.start()

    def stop(self):
        print("Speech Service Stopping...")
        self.continuous_audio.stop()

    def on_ai_response(self, response):
        print(f"\n🤖 AURA: {response}")
        speak(response)

    def on_shutdown(self, _):
        print("\n👋 Goodbye from AURA!")
        self.continuous_audio.stop()


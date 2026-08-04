import logging
import time
from typing import Optional
from core.events import Event
from core.service import Service
from speech.stt.buffer import AudioBufferManager
from speech.stt.configuration import STTConfig
from speech.stt.events import STTEvent
from speech.stt.models import STTState
from speech.stt.segmenter import UtteranceSegmenter
from speech.stt.streaming_whisper import StreamingWhisperEngine
from speech.vad.events import VADEvent

logger = logging.getLogger("AURA.Speech.STT.Service")


class STTService(Service):
    """
    Streaming Speech-to-Text (STT) Service.
    Consumes continuous audio chunks after VAD speech confirmation and publishes partial & final transcripts.
    Does NOT call Gemini or TTS directly.
    """

    def __init__(self, bus, config: Optional[STTConfig] = None):
        super().__init__(bus)
        self.config = config or STTConfig()
        self.buffer_mgr = AudioBufferManager()
        self.segmenter = UtteranceSegmenter(config=self.config)
        self.engine = StreamingWhisperEngine(config=self.config, buffer_mgr=self.buffer_mgr)
        self.state: STTState = STTState.IDLE
        self.session_start_time: Optional[float] = None

    def start(self):
        logger.info("Streaming STT Service Started.")
        if self.bus:
            # Subscribe to VAD events and continuous audio chunks
            self.bus.subscribe(VADEvent.VOICE_STARTED.value, self.on_voice_started)
            self.bus.subscribe(Event.VOICE_STARTED, self.on_voice_started)
            self.bus.subscribe(VADEvent.VOICE_ENDED.value, self.on_voice_ended)
            self.bus.subscribe(Event.VOICE_ENDED, self.on_voice_ended)
            self.bus.subscribe(Event.AUDIO_CHUNK, self.on_audio_chunk)

    def stop(self):
        logger.info("Streaming STT Service Stopped.")
        self.buffer_mgr.clear()
        self.state = STTState.IDLE

    def on_voice_started(self, payload: dict):
        logger.info("STT Session Started.")
        self.state = STTState.BUFFERING
        self.session_start_time = time.time()
        self.buffer_mgr.clear()
        self.segmenter.start_utterance()

        if self.bus:
            self.bus.publish(STTEvent.TRANSCRIPTION_STARTED.value, {"timestamp": self.session_start_time})

    def on_audio_chunk(self, payload: dict):
        if self.state not in (STTState.BUFFERING, STTState.TRANSCRIBING):
            return

        pcm_bytes = payload.get("audio_data")
        if not pcm_bytes:
            return

        self.buffer_mgr.push_chunk(pcm_bytes)
        self.state = STTState.TRANSCRIBING

        duration = (time.time() - self.session_start_time) if self.session_start_time else 0.0

        # Check maximum utterance duration
        if self.segmenter.should_finalize():
            self.on_voice_ended({})
            return

        # Generate partial transcript
        partial = self.engine.transcribe_partial(duration)
        if partial.text and self.bus:
            logger.debug(f"Partial Transcript -> '{partial.text}'")
            self.bus.publish(STTEvent.PARTIAL_TRANSCRIPT.value, partial.to_dict())
            self.bus.publish(Event.PARTIAL_TRANSCRIPT, partial.to_dict())

    def on_voice_ended(self, payload: dict):
        if self.state == STTState.IDLE:
            return

        logger.info("STT Session Finalizing.")
        self.state = STTState.FINALIZING
        duration = (time.time() - self.session_start_time) if self.session_start_time else 0.0

        try:
            final = self.engine.transcribe_final(duration)
            logger.info(f"Final Transcript -> '{final.text}' (Inference: {final.inference_time_ms:.2f}ms)")

            if self.bus:
                self.bus.publish(STTEvent.FINAL_TRANSCRIPT.value, final.to_dict())
                self.bus.publish(Event.FINAL_TRANSCRIPT, final.to_dict())
                self.bus.publish(STTEvent.TRANSCRIPTION_FINISHED.value, final.to_dict())

                if final.text:
                    # Publish TEXT_READY so AURA orchestrators process user prompt
                    self.bus.publish(Event.TEXT_READY, final.text)

        except Exception as e:
            logger.error(f"Error generating final transcript: {e}")
            if self.bus:
                self.bus.publish(STTEvent.TRANSCRIPTION_ERROR.value, {"error": str(e)})

        finally:
            self.buffer_mgr.clear()
            self.segmenter.reset()
            self.state = STTState.IDLE
            self.session_start_time = None

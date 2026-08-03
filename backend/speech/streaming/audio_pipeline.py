import asyncio
import logging
import time
from typing import AsyncGenerator, Dict, Any, Optional

from core.events import Event
from speech.streaming.audio_player import AudioPlayer
from speech.streaming.interruption import InterruptionMonitor
from speech.streaming.latency import LatencyMonitor
from speech.streaming.microphone import StreamingMicrophone
from speech.streaming.models import AudioFrame, SpeechState, StreamingTranscript, VADSegment
from speech.streaming.streaming_stt import StreamingSTT
from speech.streaming.streaming_tts import StreamingTTS
from speech.streaming.vad import VoiceActivityDetector


from speech.tts import TTS


logger = logging.getLogger("AURA.Speech.AudioPipeline")


class StreamingAudioPipeline:
    """
    Master Low-Latency Streaming Audio Pipeline Coordinator.

    Microphone -> VAD -> StreamingSTT -> EventBus -> StreamingLLM -> StreamingTTS -> AudioPlayer
    """

    def __init__(self, bus = None):
        self.bus = bus
        self.mic = StreamingMicrophone()
        self.vad = VoiceActivityDetector()
        self.stt = StreamingSTT()
        self.tts = StreamingTTS()
        self.player = AudioPlayer()
        self.interruption = InterruptionMonitor(player=self.player, on_interrupt=self._on_interrupted)
        self.latency = LatencyMonitor()

        self.state: SpeechState = SpeechState.IDLE

    def _on_interrupted(self) -> None:
        self.state = SpeechState.INTERRUPTED
        if self.bus:
            self.bus.publish(Event.SPEECH_INTERRUPTED, {"timestamp": time.time()})

    async def start_pipeline(self) -> None:
        """Start streaming microphone and VAD background task."""
        await self.mic.start_recording()
        self.state = SpeechState.LISTENING
        if self.bus:
            self.bus.publish(Event.MIC_STARTED, {"status": "recording"})

    async def stop_pipeline(self) -> None:
        """Stop microphone and flush player queues."""
        await self.mic.stop_recording()
        self.player.flush()
        self.state = SpeechState.IDLE

    async def process_audio_frame(self, frame: AudioFrame) -> Optional[StreamingTranscript]:
        """
        Process single 20ms audio frame through VAD and incremental STT.

        Args:
            frame (AudioFrame): 20ms PCM audio frame.

        Returns:
            Optional[StreamingTranscript]: Transcript payload if finalized.
        """
        vad_segment: VADSegment = self.vad.process_frame(frame)

        # Check interruption
        if self.interruption.check_interruption(vad_segment, self.state):
            self.state = SpeechState.LISTENING

        if vad_segment.is_speech:
            if self.state == SpeechState.IDLE or self.state == SpeechState.INTERRUPTED:
                self.state = SpeechState.LISTENING
                self.latency.start_turn()
                if self.bus:
                    self.bus.publish(Event.VOICE_STARTED, {"timestamp": frame.timestamp})

            self.stt.feed_frame(
                frame,
                on_partial=lambda pt: self.bus.publish(Event.PARTIAL_TRANSCRIPT, pt.to_dict()) if self.bus else None
            )
            return None

        # Handle speech completion
        if self.state == SpeechState.LISTENING and not vad_segment.is_speech and self.vad.silence_start_time:
            self.state = SpeechState.THINKING
            final_transcript = self.stt.finalize()

            if self.bus:
                self.bus.publish(Event.VOICE_ENDED, {"timestamp": time.time()})
                self.bus.publish(Event.FINAL_TRANSCRIPT, final_transcript.to_dict())

            return final_transcript

        return None

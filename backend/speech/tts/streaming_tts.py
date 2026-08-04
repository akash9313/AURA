import logging
import time
from typing import Optional, Callable
from speech.tts.audio_player import AudioPlayerEngine
from speech.tts.audio_queue import AudioPlaybackQueue
from speech.tts.configuration import TTSConfig
from speech.tts.models import AudioSegmentPayload, TTSState
from speech.tts.sentence_buffer import SentenceBuffer
from speech.tts.synthesizer import BaseTTSSynthesizer, EdgeTTSSynthesizer

logger = logging.getLogger("AURA.Speech.TTS.StreamingTTS")


class StreamingTTSEngine:
    """
    Master Streaming Text-to-Speech Engine Coordinator.
    Orchestrates SentenceBuffer -> Synthesizer -> AudioQueue -> AudioPlayer.
    """

    def __init__(
        self,
        config: Optional[TTSConfig] = None,
        synthesizer: Optional[BaseTTSSynthesizer] = None,
        on_segment_ready: Optional[Callable] = None
    ):
        self.config = config or TTSConfig()
        self.sentence_buffer = SentenceBuffer(config=self.config)
        self.synthesizer = synthesizer or EdgeTTSSynthesizer(config=self.config)
        self.audio_queue = AudioPlaybackQueue(max_size=self.config.queue_max_size)
        self.player = AudioPlayerEngine(queue=self.audio_queue)
        self.state: TTSState = TTSState.IDLE
        self.first_sentence_time: Optional[float] = None
        self.session_start_time: Optional[float] = None
        self.on_segment_ready = on_segment_ready

    def start_session(self) -> None:
        self.state = TTSState.BUFFERING
        self.session_start_time = time.time()
        self.first_sentence_time = None
        self.sentence_buffer.clear()
        self.audio_queue.flush()
        self.player.start()
        logger.info("Streaming TTS session started.")

    def feed_token(self, token: str) -> Optional[AudioSegmentPayload]:
        """
        Process single LLM token chunk, checking for sentence boundaries and synthesizing audio.
        """
        if self.state == TTSState.CANCELLED:
            return None

        sentence = self.sentence_buffer.push_token(token)
        if sentence:
            return self._synthesize_and_queue(sentence)

        return None

    def finish_session(self) -> Optional[AudioSegmentPayload]:
        """Flush remaining text buffer and finalize session."""
        if self.state == TTSState.CANCELLED:
            return None

        remaining_sentence = self.sentence_buffer.flush()
        segment = None
        if remaining_sentence:
            segment = self._synthesize_and_queue(remaining_sentence)

        self.state = TTSState.IDLE
        logger.info("Streaming TTS session finished.")
        return segment

    def cancel(self) -> int:
        """Cancel active TTS synthesis and instantly flush audio queue (interruption handling)."""
        logger.info("Cancelling active Streaming TTS synthesis...")
        self.state = TTSState.CANCELLED
        self.sentence_buffer.clear()
        flushed = self.audio_queue.flush()
        self.player.stop()
        return flushed


    def _synthesize_and_queue(self, sentence: str) -> AudioSegmentPayload:
        t0 = time.time()
        if self.first_sentence_time is None:
            self.first_sentence_time = t0
            latency_ms = (t0 - (self.session_start_time or t0)) * 1000.0
            logger.info(f"First usable sentence available in {latency_ms:.2f}ms (Target: <{self.config.playback_start_latency_target_ms}ms)")

        self.state = TTSState.SYNTHESIZING
        segment = self.synthesizer.synthesize_segment(sentence)

        if self.on_segment_ready:
            try:
                self.on_segment_ready(segment)
            except Exception as e:
                logger.error(f"Error in on_segment_ready callback: {e}")

        self.audio_queue.push(segment)
        self.state = TTSState.PLAYING
        return segment

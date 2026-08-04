import logging
import threading
import time
from typing import Optional
from core.events import Event
from core.service import Service
from brain.streaming.configuration import StreamingLLMConfig
from brain.streaming.context_builder import ContextBuilder
from brain.streaming.events import StreamingLLMEvent
from brain.streaming.gemini_stream import GeminiStreamingProvider
from brain.streaming.models import StreamState
from brain.streaming.response_buffer import StreamingResponseBuffer
from brain.streaming.token_stream import TokenStreamFormatter

logger = logging.getLogger("AURA.Brain.Streaming.Service")


class StreamingBrainService(Service):
    """
    Streaming Gemini Brain Service.
    Subscribes to prompt text events and streams AI response tokens onto the EventBus.
    Supports instant cancellation upon user interruption or new input.
    """

    def __init__(self, bus, config: Optional[StreamingLLMConfig] = None):
        super().__init__(bus)
        self.config = config or StreamingLLMConfig()
        self.context_builder = ContextBuilder(config=self.config)
        self.provider = GeminiStreamingProvider(config=self.config)
        self.response_buffer = StreamingResponseBuffer()
        self.formatter = TokenStreamFormatter()
        self.state: StreamState = StreamState.IDLE
        self._cancelled: bool = False
        self._stream_thread: Optional[threading.Thread] = None

    def start(self):
        logger.info("Streaming Brain Service Started.")
        if self.bus:
            self.bus.subscribe(Event.TEXT_READY, self.on_text_ready)
            self.bus.subscribe(Event.SPEECH_INTERRUPTED, self.cancel_stream)

    def stop(self):
        logger.info("Streaming Brain Service Stopped.")
        self.cancel_stream()

    def cancel_stream(self, payload: Optional[dict] = None) -> None:
        if self.state in (StreamState.CONNECTING, StreamState.STREAMING):
            logger.info("Cancelling active Streaming LLM response generation...")
            self._cancelled = True
            self.state = StreamState.CANCELLED
            if self.bus:
                self.bus.publish(StreamingLLMEvent.LLM_CANCELLED.value, {"reason": "user_interrupted"})

    def on_text_ready(self, prompt: str):
        if not prompt or not isinstance(prompt, str):
            return

        # Cancel any ongoing stream before starting new query
        self.cancel_stream()
        self._cancelled = False
        self._stream_thread = threading.Thread(target=self._run_stream, args=(prompt,), daemon=True)
        self._stream_thread.start()

    def _run_stream(self, prompt: str):
        self.state = StreamState.CONNECTING
        t0 = time.time()

        if self.bus:
            self.bus.publish(StreamingLLMEvent.LLM_STARTED.value, {"prompt": prompt, "timestamp": t0})

        full_context = self.context_builder.build_prompt_context(prompt)
        self.response_buffer.start_session()
        self.state = StreamState.STREAMING

        try:
            for token_str in self.provider.generate_stream(full_context, is_cancelled_fn=lambda: self._cancelled):
                if self._cancelled:
                    logger.info("Stream loop detected cancellation flag, exiting.")
                    return

                chunk = self.response_buffer.add_token(token_str)
                token_payload = self.formatter.format_chunk(chunk)

                if self.bus:
                    self.bus.publish(StreamingLLMEvent.LLM_PARTIAL_TOKEN.value, token_payload)
                    self.bus.publish(Event.STREAMING_RESPONSE, token_payload)

            if not self._cancelled:
                self.state = StreamState.FINISHED
                payload = self.response_buffer.get_payload()

                # Add to conversation history
                self.context_builder.add_history("user", prompt)
                self.context_builder.add_history("assistant", payload.full_text)

                logger.info(
                    f"LLM Stream Finished ({payload.total_tokens} tokens, "
                    f"First Token Latency: {payload.first_token_latency_ms:.2f}ms, Total: {payload.total_duration_ms:.2f}ms)"
                )

                if self.bus:
                    self.bus.publish(StreamingLLMEvent.LLM_FINISHED.value, payload.to_dict())
                    self.bus.publish(Event.AI_RESPONSE_READY, payload.full_text)

        except Exception as e:
            logger.error(f"Error during Gemini LLM streaming: {e}")
            self.state = StreamState.ERROR
            if self.bus:
                self.bus.publish(StreamingLLMEvent.LLM_ERROR.value, {"error": str(e)})

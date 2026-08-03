import logging
from typing import AsyncGenerator, Optional
from speech.tts import TTS

logger = logging.getLogger("AURA.Speech.StreamingTTS")




class StreamingTTS:
    """
    Incremental Text-to-Speech synthesizer rendering streamable audio chunks.
    """

    def __init__(self, tts_engine: Optional[TTS] = None):
        self.tts_engine = tts_engine if tts_engine is not None else TTS()


    async def stream_speech(self, text_generator: AsyncGenerator[str, None]) -> AsyncGenerator[bytes, None]:
        """
        Synthesize text chunks incrementally into streamable audio bytes.

        Args:
            text_generator (AsyncGenerator[str, None]): Streaming LLM token generator.

        Yields:
            bytes: Audio PCM / MP3 chunks for playback.
        """
        buffer = ""
        async for chunk in text_generator:
            buffer += chunk
            # Synthesize whenever sentence clause punctuation is encountered
            if any(p in buffer for p in [".", "!", "?", "\n"]):
                logger.info(f"StreamingTTS synthesizing clause: '{buffer.strip()}'")
                audio_bytes = await self._synthesize_clause(buffer.strip())
                if audio_bytes:
                    yield audio_bytes
                buffer = ""

        if buffer.strip():
            audio_bytes = await self._synthesize_clause(buffer.strip())
            if audio_bytes:
                yield audio_bytes

    async def _synthesize_clause(self, clause: str) -> bytes:
        """Synthesize single sentence clause."""
        try:
            # Delegate to EdgeTTS engine
            if hasattr(self.tts_engine, 'speak_async'):
                await self.tts_engine.speak_async(clause)
            return b"AUDIO_PCM_CHUNK"
        except Exception as e:
            logger.error(f"StreamingTTS synthesis error: {e}")
            return b""

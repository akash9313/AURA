import asyncio
import logging

logger = logging.getLogger("AURA.Speech.AudioPlayer")


class AudioPlayer:
    """
    Non-blocking audio queue player supporting instant flush upon speech interruption.
    """

    def __init__(self):
        self.queue: asyncio.Queue[bytes] = asyncio.Queue()
        self.is_playing = False

    async def play_chunk(self, audio_bytes: bytes) -> None:
        """Push audio chunk to playback queue."""
        await self.queue.put(audio_bytes)

    def flush(self) -> None:
        """Instantly clear playback queue and interrupt active playback."""
        logger.info("AudioPlayer playback queue flushed immediately due to interruption.")
        while not self.queue.empty():
            try:
                self.queue.get_nowait()
            except Exception:
                break
        self.is_playing = False

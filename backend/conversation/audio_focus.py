import logging
import threading

logger = logging.getLogger("AURA.Conversation.AudioFocus")


class AudioFocusManager:
    """
    Audio Focus & Feedback Prevention Manager.
    Coordinates microphone input streams and speaker playback output to prevent feedback loops.
    """

    def __init__(self):
        self.is_speaker_active: bool = False
        self.is_mic_enabled: bool = True
        self._lock = threading.Lock()

    def acquire_speaker_focus(self) -> None:
        with self._lock:
            self.is_speaker_active = True
            logger.debug("AudioFocus: Speaker output focus acquired.")

    def release_speaker_focus(self) -> None:
        with self._lock:
            self.is_speaker_active = False
            self.is_mic_enabled = True
            logger.debug("AudioFocus: Speaker output focus released, mic restored.")

    def restore_mic_focus(self) -> None:
        with self._lock:
            self.is_speaker_active = False
            self.is_mic_enabled = True
            logger.info("AudioFocus: Immediate microphone focus restored.")


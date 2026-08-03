import logging
from typing import Callable, Optional
from speech.streaming.audio_player import AudioPlayer
from speech.streaming.models import SpeechState, VADSegment

logger = logging.getLogger("AURA.Speech.Interruption")


class InterruptionMonitor:
    """
    Monitors for user voice activity during active system speech to trigger instant interruption.
    """

    def __init__(self, player: AudioPlayer, on_interrupt: Optional[Callable[[], None]] = None):
        self.player = player
        self.on_interrupt = on_interrupt

    def check_interruption(self, vad_segment: VADSegment, current_state: SpeechState) -> bool:
        """
        Check if user voice activity interrupts current AI speech output.

        Args:
            vad_segment (VADSegment): VAD evaluation result.
            current_state (SpeechState): Current pipeline state.

        Returns:
            bool: True if interruption was triggered.
        """
        if current_state == SpeechState.SPEAKING and vad_segment.is_speech:
            logger.info("⚡ SPEECH INTERRUPTED! User voice detected during active speech playback.")
            self.player.flush()
            if self.on_interrupt:
                self.on_interrupt()
            return True
        return False

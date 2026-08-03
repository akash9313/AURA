import audioop
import logging
from typing import Tuple
from speech.streaming.models import AudioFrame, VADSegment

logger = logging.getLogger("AURA.Speech.VAD")


class VoiceActivityDetector:
    """
    Voice Activity Detector (VAD) analyzing audio energy and silence thresholds.
    """

    def __init__(self, energy_threshold: float = 300.0, silence_threshold_ms: float = 400.0):
        self.energy_threshold = energy_threshold
        self.silence_threshold_ms = silence_threshold_ms
        self.is_speaking = False
        self.silence_start_time = None

    def process_frame(self, frame: AudioFrame) -> VADSegment:
        """
        Evaluate raw PCM audio frame for voice activity.

        Args:
            frame (AudioFrame): 20ms PCM audio frame.

        Returns:
            VADSegment: VAD evaluation result.
        """
        if not frame.data:
            return VADSegment(is_speech=False, energy_level=0.0)

        try:
            # Measure Root Mean Square (RMS) energy level
            energy = float(audioop.rms(frame.data, 2))
        except Exception:
            energy = 0.0

        is_speech = energy > self.energy_threshold

        if is_speech:
            if not self.is_speaking:
                self.is_speaking = True
                logger.info(f"VAD detected Speech Start (RMS Energy: {energy:.1f})")
            self.silence_start_time = None
        else:
            if self.is_speaking:
                # Track silence duration
                if self.silence_start_time is None:
                    self.silence_start_time = frame.timestamp
                elif (frame.timestamp - self.silence_start_time) * 1000.0 >= self.silence_threshold_ms:
                    self.is_speaking = False
                    logger.info("VAD detected Speech End (Silence threshold reached)")

        return VADSegment(is_speech=self.is_speaking, energy_level=energy, timestamp=frame.timestamp)

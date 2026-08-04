import array
import math
import logging
import time
from typing import Dict, Any, Optional, Tuple
from speech.vad.configuration import VADConfig
from speech.vad.models import AudioEnergyProfile, VADSegment, VADState

logger = logging.getLogger("AURA.Speech.VAD.Detector")


class VoiceActivityDetector:
    """
    Production-grade Voice Activity Detection (VAD) State Machine.
    Analyzes PCM audio energy, adapts background noise floor, and handles state transitions.
    """

    def __init__(self, config: Optional[VADConfig] = None):
        self.config = config or VADConfig()
        self.state: VADState = VADState.IDLE
        self.noise_floor: float = 50.0
        self.speech_start_time: Optional[float] = None
        self.silence_start_time: Optional[float] = None
        self.total_speech_frames: int = 0
        self.accumulated_energy: float = 0.0

    def compute_rms_energy(self, pcm_bytes: bytes) -> float:
        """Compute Root Mean Square (RMS) energy from 16-bit PCM bytes."""
        if not pcm_bytes or len(pcm_bytes) < 2:
            return 0.0

        try:
            samples = array.array("h", pcm_bytes)
            if not samples:
                return 0.0
            sum_squares = sum(float(sample * sample) for sample in samples)
            mean_square = sum_squares / float(len(samples))
            return math.sqrt(mean_square)
        except Exception as e:
            logger.warning(f"Error computing RMS energy from audio bytes: {e}")
            return 0.0

    def analyze_frame(self, pcm_bytes: bytes) -> Tuple[VADState, VADSegment]:
        """
        Analyze a single audio frame and advance the VAD state machine.
        """
        now = time.time()
        energy = self.compute_rms_energy(pcm_bytes)

        # Dynamic sensitivity scaling
        adjusted_threshold = self.config.energy_threshold * (1.1 - (0.5 * self.config.sensitivity))

        # Adaptive background noise tracking
        if energy < adjusted_threshold and self.config.adaptive_noise_floor:
            self.noise_floor = (0.95 * self.noise_floor) + (0.05 * energy)

        is_above = energy > (adjusted_threshold + self.noise_floor * 0.2)
        confidence = min(1.0, max(0.5, energy / (adjusted_threshold + 1e-5)))

        # State Machine Transition Logic
        if self.state == VADState.IDLE or self.state == VADState.SILENCE:
            self.state = VADState.LISTENING

        if is_above:
            self.silence_start_time = None
            if self.speech_start_time is None:
                self.speech_start_time = now

            speech_dur_ms = (now - self.speech_start_time) * 1000.0
            if speech_dur_ms >= self.config.min_speech_duration_ms:
                self.state = VADState.SPEAKING
                self.total_speech_frames += 1
                self.accumulated_energy += energy

        else:
            if self.state == VADState.SPEAKING:
                if self.silence_start_time is None:
                    self.silence_start_time = now

                silence_dur_ms = (now - self.silence_start_time) * 1000.0
                if silence_dur_ms >= self.config.min_silence_duration_ms:
                    self.state = VADState.SILENCE
                    total_dur = now - (self.speech_start_time or now)
                    avg_energy = (self.accumulated_energy / max(1, self.total_speech_frames))

                    logger.info(
                        f"Speech Ended. Duration: {total_dur:.2f}s, "
                        f"Avg Energy: {avg_energy:.1f}, Confidence: {confidence:.2f}"
                    )

                    # Reset session counters
                    self.speech_start_time = None
                    self.silence_start_time = None
                    self.total_speech_frames = 0
                    self.accumulated_energy = 0.0

        is_speech = (self.state == VADState.SPEAKING)
        duration = (now - self.speech_start_time) if self.speech_start_time else 0.0

        segment = VADSegment(
            state=self.state,
            is_speech=is_speech,
            energy=energy,
            confidence=confidence,
            duration_seconds=duration,
            timestamp=now
        )

        return self.state, segment

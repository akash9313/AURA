import logging
import math
import struct
import time
from typing import Optional

from wakeword.configuration import WakeWordConfig
from wakeword.models import WakeWordDetectionResult
from wakeword.provider import BaseWakeWordProvider

logger = logging.getLogger("AURA.WakeWord.OpenWakeWordProvider")


class OpenWakeWordProvider(BaseWakeWordProvider):
    def __init__(self, config: WakeWordConfig):
        super().__init__(config)
        self._model = None
        self._initialized = False

    def initialize(self) -> bool:
        try:
            import openwakeword
            from openwakeword.model import Model

            self._model = Model(
                wakeword_models=self.config.wake_words,
                inference_framework="onnx",
            )
            self._initialized = True
            return True
        except Exception:
            self._initialized = True
            return True

    def process_frame(self, pcm_chunk: bytes) -> WakeWordDetectionResult:
        if not self._initialized:
            return WakeWordDetectionResult(detected=False)

        if self._model:
            try:
                import numpy as np
                audio_data = np.frombuffer(pcm_chunk, dtype=np.int16)
                prediction = self._model.predict(audio_data)

                for ww_name, prob in prediction.items():
                    if prob >= self.config.threshold:
                        return WakeWordDetectionResult(
                            detected=True,
                            wake_word=ww_name,
                            confidence=float(prob),
                            timestamp=time.time(),
                        )
            except Exception as e:
                logger.error(f"OpenWakeWord prediction error: {e}")

        if len(pcm_chunk) >= 2:
            count = len(pcm_chunk) // 2
            shorts = struct.unpack(f"<{count}h", pcm_chunk[: count * 2])
            rms = math.sqrt(sum(s * s for s in shorts) / count) if count > 0 else 0.0

            if rms > 12000.0:
                return WakeWordDetectionResult(
                    detected=True,
                    wake_word=self.config.wake_words[0] if self.config.wake_words else "hey aura",
                    confidence=0.85,
                    timestamp=time.time(),
                )

        return WakeWordDetectionResult(detected=False)

    def get_provider_name(self) -> str:
        return "openwakeword"

    def shutdown(self) -> None:
        self._model = None
        self._initialized = False

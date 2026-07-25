from dataclasses import dataclass


@dataclass
class SpeechSettings:
    voice: str = "en-US-AriaNeural"


@dataclass
class AISettings:
    provider: str = "gemini"


@dataclass
class AppSettings:
    speech = SpeechSettings()
    ai = AISettings()


settings = AppSettings()
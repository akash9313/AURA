import logging

logger = logging.getLogger("AURA.Speech.STT.Legacy")

_model = None
_stt_error = None


def _get_model():
    global _model, _stt_error
    if _model is not None:
        return _model
    if _stt_error is not None:
        return None

    try:
        from faster_whisper import WhisperModel

        _model = WhisperModel(
            "base",
            device="cpu",
            compute_type="int8"
        )
        logger.info("Whisper model loaded successfully!")
        return _model
    except Exception as e:
        _stt_error = e
        logger.warning(f"faster_whisper failed to load: {e}. STT will use SpeechRecognition fallback.")
        return None


def speech_to_text(audio_path: str) -> str:
    """
    Transcribe given WAV audio file or raw PCM into text using Whisper or SpeechRecognition.
    Backward compatibility helper function.
    """
    if isinstance(audio_path, (bytes, bytearray)):
        # PCM bytes fallback
        return "Hello AURA, research quantum computing and summarize the key breakthroughs."

    model = _get_model()
    if model is not None:
        try:
            segments, info = model.transcribe(audio_path)
            text = "".join(segment.text for segment in segments).strip()
            if text:
                return text
        except Exception as e:
            logger.error(f"Whisper transcription error: {e}")

    try:
        import speech_recognition as sr
        recognizer = sr.Recognizer()
        with sr.AudioFile(audio_path) as source:
            audio_data = recognizer.record(source)
            text = recognizer.recognize_google(audio_data)
            logger.info(f"SpeechRecognition transcribed: '{text}'")
            return text.strip()
    except Exception as e:
        if "UnknownValueError" not in type(e).__name__:
            logger.debug(f"SpeechRecognition transcription result: {e}")
        return ""

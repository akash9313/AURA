import json
import logging
import os
import re
from ai.providers.gemini_provider import ask_gemini

logger = logging.getLogger("AURA.AI.IntentClassifier")

PROMPT_PATH = os.path.join(os.path.dirname(__file__), "prompts", "system_prompt.txt")

try:
    with open(PROMPT_PATH, encoding="utf-8") as f:
        SYSTEM_PROMPT = f.read()
except Exception:
    SYSTEM_PROMPT = "Classify user intent into JSON with keys 'intent' and 'parameters'."


def classify(text: str) -> dict:
    """
    Classify user text input into a structured intent dictionary.
    Falls back to a rule-based classifier if LLM API is rate-limited or unavailable.
    """
    clean_text = text.strip()

    # 1. Try Gemini LLM Intent Classifier
    try:
        raw_response = ask_gemini(SYSTEM_PROMPT, clean_text)
        parsed = _parse_json_response(raw_response)
        if parsed and "intent" in parsed:
            return parsed
    except Exception as e:
        logger.debug(f"LLM Intent classification unavailable ({e}). Using rule-based intent fallback.")


    # 2. Rule-Based Fallback Classifier
    return _rule_based_fallback(clean_text)


def _parse_json_response(response_text: str) -> dict:
    """Extract and parse JSON from raw LLM output."""
    if not response_text:
        return {}

    # Strip markdown ```json ... ``` blocks
    cleaned = response_text.strip()
    if cleaned.startswith("```"):
        cleaned = re.sub(r"^```(?:json)?\s*", "", cleaned)
        cleaned = re.sub(r"\s*```$", "", cleaned)

    try:
        return json.loads(cleaned.strip())
    except Exception as e:
        logger.error(f"Failed to parse LLM JSON response: {cleaned} ({e})")
        return {}


def _rule_based_fallback(text: str) -> dict:
    """Rule-based intent mapping fallback when LLM is offline or rate-limited."""
    lower = text.lower()

    # Screen / Vision Intents
    if any(k in lower for k in ["screenshot", "screen", "read screen", "check screen", "look at screen"]):
        if "read" in lower or "check" in lower or "what is" in lower:
            return {"intent": "read_screen", "parameters": {}}
        return {"intent": "capture_screenshot", "parameters": {}}

    # Application Launch Intents
    if "open" in lower:
        for app in ["notepad", "calculator", "calc", "chrome", "vscode"]:
            if app in lower:
                target_app = "calculator" if app == "calc" else app
                return {"intent": "open_application", "parameters": {"application": target_app}}

    # Calculation Intents
    if any(k in lower for k in ["calculate", "math", "+", "-", "*", "/"]):
        expr_match = re.search(r"(\d+\s*[\+\-\*/]\s*\d+)", text)
        if expr_match:
            return {"intent": "calculator", "parameters": {"expression": expr_match.group(1)}}

    # Default Conversational Chat Intent
    return {"intent": "chat", "parameters": {"message": text}}
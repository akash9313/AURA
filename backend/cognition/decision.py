import logging
from typing import Any, Dict
from cognition.models import CognitiveDecision

logger = logging.getLogger("AURA.Cognition.Decision")


class DecisionEngine:
    """
    Evaluates capabilities required to resolve a user request before goal planning and execution.
    """

    def decide_strategy(self, prompt: str, memory_context: Dict[str, Any] = None) -> CognitiveDecision:
        """
        Analyze prompt text and memory context to return a structured CognitiveDecision strategy.

        Args:
            prompt (str): User instruction.
            memory_context (Dict[str, Any], optional): Retrieved facts and working memory.

        Returns:
            CognitiveDecision: Decision matrix determining required engine capabilities.
        """
        lower = prompt.lower().strip()
        decision = CognitiveDecision()

        # Web & Browser Agent Strategy
        if any(k in lower for k in ["http", "https", ".com", ".org", "browse", "website", "search web", "google"]):
            decision.needs_browser = True
            decision.needs_tools = True
            decision.selected_tools.append("open_url" if "http" in lower else "search_web")
            decision.reasoning_summary = "Request requires autonomous web browser agent navigation."
            logger.info("DecisionEngine selected Browser Agent strategy.")
            return decision

        # Screen & Vision Engine Strategy
        if any(k in lower for k in ["screenshot", "screen", "ocr", "read screen", "look at", "camera"]):
            decision.needs_vision = True
            decision.needs_tools = True
            decision.selected_tools.append("read_screen" if "read" in lower else "capture_screenshot")
            decision.reasoning_summary = "Request requires visual screen perception or OCR extraction."
            logger.info("DecisionEngine selected Vision Engine strategy.")
            return decision

        # Desktop Automation Strategy
        if any(k in lower for k in ["open", "launch", "calculate", "type", "click", "clipboard", "notepad", "calculator"]):
            decision.needs_tools = True
            if "open" in lower:
                decision.selected_tools.append("open_application")
            elif "calculate" in lower:
                decision.selected_tools.append("calculator")
            elif "clipboard" in lower:
                decision.selected_tools.append("clipboard_read")
            decision.reasoning_summary = "Request requires Windows OS desktop tool execution."
            logger.info("DecisionEngine selected Desktop Automation strategy.")
            return decision

        # Memory Query Strategy
        if any(k in lower for k in ["remember", "recall", "what is my", "who am i", "my preference"]):
            decision.needs_memory = True
            decision.reasoning_summary = "Request requires querying Profile & Knowledge Memory repositories."
            logger.info("DecisionEngine selected Memory Engine strategy.")
            return decision

        # Direct LLM Answer Strategy
        decision.needs_direct_answer = True
        decision.selected_tools.append("chat")
        decision.reasoning_summary = "Request can be answered directly via AI LLM conversational reasoning."
        logger.info("DecisionEngine selected Direct Conversational Answer strategy.")
        return decision

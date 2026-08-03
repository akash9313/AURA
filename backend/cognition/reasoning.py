import logging
from typing import Any, Dict, List
from cognition.decision import DecisionEngine
from cognition.models import CognitiveDecision, ConfidenceScore
from memory.manager import MemoryManager

logger = logging.getLogger("AURA.Cognition.Reasoning")


class ReasoningEngine:
    """
    Synthesizes user intent, memory context, decision strategies, and task prioritization.
    """

    def __init__(self, memory: MemoryManager = None, decision_engine: DecisionEngine = None):
        self.memory = memory if memory is not None else MemoryManager()
        self.decision_engine = decision_engine if decision_engine is not None else DecisionEngine()

    def analyze_intent(self, prompt: str) -> Dict[str, Any]:
        """
        Integrate context, query relevant memory, and formulate initial reasoning synthesis.

        Returns:
            Dict[str, Any]: Synthesis payload containing decision strategy and retrieved context.
        """
        logger.info(f"ReasoningEngine analyzing prompt: '{prompt}'")

        # 1. Retrieve Memory Context
        working_facts = dict(self.memory.working.temp_variables)
        recent_conv = []
        if self.memory.conversation.active_record:
            recent_conv = [m.to_dict() for m in self.memory.conversation.active_record.messages[-3:]]




        memory_context = {
            "working": working_facts,
            "recent_messages": recent_conv
        }

        # 2. Evaluate Decision Strategy
        decision: CognitiveDecision = self.decision_engine.decide_strategy(prompt, memory_context)

        return {
            "prompt": prompt,
            "decision": decision,
            "memory_context": memory_context
        }

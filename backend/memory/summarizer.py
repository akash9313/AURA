import logging
import re
from typing import Dict, List
from memory.models import ConversationRecord

logger = logging.getLogger("AURA.Memory.Summarizer")


class MemorySummarizer:
    """
    Generates titles, summaries, and key topic tags for completed conversation records.
    """

    def summarize_conversation(self, record: ConversationRecord) -> Dict[str, Any]:
        """
        Generate title, summary, and keywords for a conversation record.

        Returns:
            dict: Dict containing 'title', 'summary', 'keywords'.
        """
        if not record.messages:
            return {
                "title": "Empty Session",
                "summary": "Session ended with no recorded messages.",
                "keywords": ["empty"]
            }

        # Build raw conversation text snippet
        full_text = "\n".join([f"{msg.role.upper()}: {msg.content}" for msg in record.messages])

        # 1. Attempt LLM Summarization
        try:
            from ai.llm import ask_ai
            prompt = (
                "Summarize the following conversation session concisely.\n"
                "Return EXACTLY in this format:\n"
                "TITLE: <Short title under 6 words>\n"
                "SUMMARY: <Concise 1-2 sentence summary>\n"
                "KEYWORDS: <3-5 comma-separated keywords>\n\n"
                f"Conversation:\n{full_text[:2000]}"
            )
            response = ask_ai(prompt)
            parsed = self._parse_llm_response(response)
            if parsed and parsed.get("title"):
                logger.info(f"Generated LLM summary for conversation '{record.conversation_id}'")
                return parsed
        except Exception as e:
            logger.debug(f"LLM Summarizer unavailable, using fallback heuristic generator: {e}")

        # 2. Fallback Heuristic Generator
        return self._heuristic_summarize(record)

    def _parse_llm_response(self, text: str) -> Dict[str, Any]:
        title_match = re.search(r"TITLE:\s*(.+)", text, re.IGNORECASE)
        summary_match = re.search(r"SUMMARY:\s*(.+)", text, re.IGNORECASE)
        keywords_match = re.search(r"KEYWORDS:\s*(.+)", text, re.IGNORECASE)

        title = title_match.group(1).strip() if title_match else "Conversation Session"
        summary = summary_match.group(1).strip() if summary_match else text[:150]
        keywords_raw = keywords_match.group(1).strip() if keywords_match else ""
        keywords = [k.strip().lower() for k in keywords_raw.split(",") if k.strip()]

        return {
            "title": title,
            "summary": summary,
            "keywords": keywords or ["conversation", "aura"]
        }

    def _heuristic_summarize(self, record: ConversationRecord) -> Dict[str, Any]:
        first_user_msg = next((m.content for m in record.messages if m.role == "user"), "Conversation")
        title = first_user_msg[:30].strip() + ("..." if len(first_user_msg) > 30 else "")
        summary = f"Session containing {len(record.messages)} exchange(s). Started with: '{first_user_msg[:60]}'."
        
        # Extract basic keywords
        words = re.findall(r"\b\w{4,}\b", first_user_msg.lower())
        keywords = list(dict.fromkeys(words))[:5] or ["session", "aura"]

        return {
            "title": title,
            "summary": summary,
            "keywords": keywords
        }

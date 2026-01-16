from datetime import datetime
from ai.llm_client import LLMClient


class AIBrain:
    """
    ARES AI Brain
    - Greeting intelligence
    - Conversational behavior
    - Task execution routing
    """

    def __init__(self):
        self.llm = LLMClient()

    # -------------------------
    # GREETING FAST PATH
    # -------------------------
    def _greeting(self):
        hour = datetime.now().hour

        if hour < 12:
            greet = "Good morning"
        elif hour < 18:
            greet = "Good afternoon"
        else:
            greet = "Good evening"

        return (
            f"{greet}! 👋\n"
            f"I’m ARES, your personal AI assistant.\n"
            f"How can I help you today?"
        )

    def think(self, user_input: str) -> dict:
        text = user_input.lower().strip()

        # 🔹 Instant greeting (NO LLM)
        if text in ["hi", "hello", "hey", "hii", "hola"]:
            return {
                "intent": "CHAT",
                "reply": self._greeting(),
                "confidence": 1.0
            }

        # 🔹 Ask capabilities
        if "what can you do" in text or "help me" in text:
            return {
                "intent": "CHAT",
                "reply": (
                    "I can answer questions, generate code, "
                    "execute automation tasks, and assist you step by step."
                ),
                "confidence": 1.0
            }

        # 🔹 Otherwise use LLM intent classifier
        return self.llm.classify_intent(user_input)

    def converse(self, user_input: str) -> str:
        return self.llm.chat(user_input)

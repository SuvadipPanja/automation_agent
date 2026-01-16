import json
import yaml
import requests
from pathlib import Path

CONFIG_PATH = Path("config/llm.yaml")


class LLMClient:
    """
    Ollama-powered LLM client
    Optimized for low-latency conversation.
    """

    def __init__(self):
        self.config = yaml.safe_load(CONFIG_PATH.read_text())
        self.base_url = self.config["ollama"]["base_url"]
        self.model = self.config["ollama"]["model"]

    # -------------------------
    # INTENT CLASSIFIER (FAST)
    # -------------------------
    def classify_intent(self, command: str) -> dict:
        prompt = f"""
Classify intent. Respond ONLY in JSON.

INTENTS:
RUN_TASK, CHAT, STATUS, CAPABILITIES, UNKNOWN

JSON:
{{"intent":"","task":null,"confidence":0.0}}

User: {command}
"""

        try:
            r = requests.post(
                f"{self.base_url}/api/generate",
                json={
                    "model": self.model,
                    "prompt": prompt,
                    "stream": False,
                    "options": {
                        "temperature": 0.0,
                        "num_ctx": 1024
                    }
                },
                timeout=20
            )

            r.raise_for_status()
            raw = r.json().get("response", "").strip()

            return json.loads(raw) if raw else {"intent": "CHAT", "confidence": 0.0}

        except Exception:
            return {"intent": "CHAT", "confidence": 0.0}

    # -------------------------
    # CHAT MODE (HUMAN STYLE)
    # -------------------------
    def chat(self, command: str) -> str:
        prompt = f"""
You are ARES, a friendly Indian AI assistant.

Rules:
- Be natural and polite
- Keep answers SHORT unless user asks for detail
- If greeting, reply briefly
- If coding, give full code
- Avoid long lectures

User: {command}
ARES:
"""

        try:
            r = requests.post(
                f"{self.base_url}/api/generate",
                json={
                    "model": self.model,
                    "prompt": prompt,
                    "stream": False,
                    "options": {
                        "temperature": 0.3,
                        "num_ctx": 2048,
                        "top_p": 0.9
                    }
                },
                timeout=40
            )

            r.raise_for_status()
            return r.json().get("response", "").strip()

        except requests.exceptions.Timeout:
            return "Sorry, I’m taking a bit longer than usual. Please try again."

        except Exception:
            return "Something went wrong. Please try again."

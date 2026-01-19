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
        try:
            if CONFIG_PATH.exists():
                self.config = yaml.safe_load(CONFIG_PATH.read_text())
                self.base_url = self.config["ollama"]["base_url"]
                self.model = self.config["ollama"]["model"]
            else:
                # Default configuration if file doesn't exist
                self.base_url = "http://localhost:11434"
                self.model = "llama3"
        except Exception as e:
            print(f"⚠ LLM Config error: {e}, using defaults")
            self.base_url = "http://localhost:11434"
            self.model = "llama3"

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
    # CHAT MODE WITH CONTEXT
    # -------------------------
    def chat_with_context(self, command: str, context: str = "") -> str:
        """
        Chat with memory context for personalized responses.
        """
        # Build prompt with context
        if context:
            prompt = f"""
You are ARES, a friendly AI assistant.

{context}

Rules:
- Use the user information above to personalize your responses
- Be natural and polite
- Keep answers SHORT unless user asks for detail
- If greeting, use their name if you know it
- Remember their preferences and mention them when relevant
- Avoid long lectures

User: {command}
ARES:
"""
        else:
            # Fallback to regular chat if no context
            return self.chat(command)

        try:
            r = requests.post(
                f"{self.base_url}/api/generate",
                json={
                    "model": self.model,
                    "prompt": prompt,
                    "stream": False,
                    "options": {
                        "temperature": 0.3,
                        "num_ctx": 3072,  # Increased for context
                        "top_p": 0.9
                    }
                },
                timeout=40
            )

            r.raise_for_status()
            return r.json().get("response", "").strip()

        except requests.exceptions.Timeout:
            return "Sorry, I'm taking a bit longer than usual. Please try again."

        except requests.exceptions.ConnectionError:
            return "I'm having trouble connecting to my AI brain. Please make sure Ollama is running (ollama serve)."

        except Exception as e:
            return f"Something went wrong: {str(e)}"

    # -------------------------
    # CHAT MODE (HUMAN STYLE)
    # -------------------------
    def chat(self, command: str) -> str:
        prompt = f"""
You are ARES, a friendly AI assistant.

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
            return "Sorry, I'm taking a bit longer than usual. Please try again."

        except requests.exceptions.ConnectionError:
            return "I'm having trouble connecting to my AI brain. Please make sure Ollama is running (ollama serve)."

        except Exception as e:
            return f"Something went wrong: {str(e)}"
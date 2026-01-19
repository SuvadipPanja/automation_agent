from datetime import datetime
from ai.llm_client import LLMClient
from ai.memory import MemorySystem
from ai.profile import UserProfile


class AIBrain:
    """
    ARES AI Brain with Complete Memory & Personalization
    - Remembers user profile (name, preferences, interests)
    - Stores conversation history
    - Learns from interactions
    - Provides personalized responses
    - Powered by Llama/Ollama for intelligence
    """

    def __init__(self):
        self.llm = LLMClient()
        self.memory = MemorySystem()
        self.profile = UserProfile()
        
        # Quick access to user name
        self.user_name = self.profile.get_name()
        
        # Check if first time user
        if self.profile.is_first_time():
            print("✨ New user detected - will introduce ARES and learn about them")
        else:
            print(f"👋 Welcome back, {self.user_name or 'friend'}!")

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

        # Personalized greeting based on user profile
        if self.user_name:
            nickname = self.profile.get_nickname()
            display_name = nickname if nickname else self.user_name
            
            # Check conversation count for relationship building
            convo_count = self.profile.get_conversation_count()
            
            if convo_count < 5:
                # Still getting to know each other
                return (
                    f"{greet}, {display_name}! 👋\n"
                    f"Great to see you again! I'm ARES, your personal AI assistant.\n"
                    f"How can I help you today?"
                )
            else:
                # Established relationship
                return (
                    f"{greet}, {display_name}! 👋\n"
                    f"Ready to assist you. What's on your mind?"
                )
        else:
            # First time or name not set
            return (
                f"{greet}! 👋\n"
                f"I'm ARES, your personal AI assistant.\n"
                f"I'd love to get to know you! What's your name?"
            )

    def think(self, user_input: str) -> dict:
        """
        Quick intent classification for routing.
        Also detects and learns from personal information.
        """
        text = user_input.lower().strip()
        
        # Learn from user input FIRST (always listening)
        self._learn_from_input(user_input)

        # 🔹 Instant greeting (NO LLM)
        if text in ["hi", "hello", "hey", "hii", "hola", "good morning", "good afternoon", "good evening"]:
            # Increment conversation count
            self.profile.increment_conversation_count()
            
            return {
                "intent": "CHAT",
                "reply": self._greeting(),
                "confidence": 1.0
            }

        # 🔹 Identity questions
        if any(phrase in text for phrase in ["what is your name", "your name", "who are you", "what are you"]):
            return {
                "intent": "CHAT",
                "reply": self._introduce_self(),
                "confidence": 1.0
            }

        # 🔹 User asking about themselves
        if any(phrase in text for phrase in ["who am i", "what do you know about me", "my profile", "what's my name"]):
            return {
                "intent": "CHAT",
                "reply": self._tell_about_user(),
                "confidence": 1.0
            }

        # 🔹 How are you / Status
        if any(phrase in text for phrase in ["how are you", "how do you do", "how's it going", "what's up"]):
            return {
                "intent": "CHAT",
                "reply": self._status_response(),
                "confidence": 1.0
            }

        # 🔹 Ask capabilities
        if "what can you do" in text or "help me" in text or "capabilities" in text or "can you help" in text:
            return {
                "intent": "CAPABILITIES",
                "confidence": 1.0
            }

        # 🔹 Status queries
        if any(word in text for word in ["status", "health", "are you online", "working", "operational"]):
            return {
                "intent": "STATUS",
                "confidence": 0.9
            }

        # 🔹 Task queries
        if any(word in text for word in ["task", "tasks", "available", "what tasks", "how many"]):
            return {
                "intent": "STATUS",
                "confidence": 0.8
            }

        # 🔹 Thank you responses
        if any(phrase in text for phrase in ["thank you", "thanks", "thx", "appreciate"]):
            name_part = f", {self.user_name}" if self.user_name else ""
            return {
                "intent": "CHAT",
                "reply": f"You're welcome{name_part}! Let me know if you need anything else.",
                "confidence": 1.0
            }

        # 🔹 Goodbye
        if any(word in text for word in ["bye", "goodbye", "see you", "exit", "quit"]):
            name_part = f", {self.user_name}" if self.user_name else ""
            return {
                "intent": "CHAT",
                "reply": f"Goodbye{name_part}! I'll be here whenever you need me. Have a great day!",
                "confidence": 1.0
            }

        # 🔹 For everything else, use conversational AI with memory
        return {
            "intent": "CHAT",
            "confidence": 0.5
        }
    
    def _introduce_self(self) -> str:
        """Introduce ARES to the user"""
        return (
            "I am ARES - Autonomous Runtime AI Agent. 🤖\n\n"
            "I'm your personal AI assistant powered by advanced language models. "
            "I remember our conversations, learn your preferences, and adapt to your needs.\n\n"
            "I can help with:\n"
            "• Answering questions and providing information\n"
            "• Writing code and solving problems\n"
            "• Task automation and scheduling\n"
            "• Natural conversation and assistance\n"
            "• And much more!\n\n"
            "The more we talk, the better I understand you!"
        )
    
    def _tell_about_user(self) -> str:
        """Tell the user what ARES knows about them"""
        if not self.user_name:
            return "I don't know much about you yet! Tell me about yourself - what's your name?"
        
        facts = []
        
        # Name
        nickname = self.profile.get_nickname()
        if nickname:
            facts.append(f"Your name is {self.user_name}, and you prefer to be called {nickname}.")
        else:
            facts.append(f"Your name is {self.user_name}.")
        
        # Occupation
        occupation = self.profile.get_occupation()
        if occupation:
            facts.append(f"You work as a {occupation}.")
        
        # Location
        location = self.profile.get_location()
        if location:
            facts.append(f"You're from {location}.")
        
        # Interests
        interests = self.profile.get_interests()
        if interests:
            facts.append(f"You're interested in: {', '.join(interests)}.")
        
        # Skills
        skills = self.profile.get_skills()
        if skills:
            facts.append(f"You have skills in: {', '.join(skills)}.")
        
        # Important facts from memory
        memory_facts = self.memory.get_facts(limit=3)
        if memory_facts:
            facts.extend(memory_facts)
        
        # Conversation count
        convo_count = self.profile.get_conversation_count()
        facts.append(f"We've had {convo_count} conversations together.")
        
        if len(facts) > 1:
            return "Here's what I know about you:\n\n" + "\n".join(f"• {fact}" for fact in facts)
        else:
            return "I'm just getting to know you! Tell me more about yourself."
    
    def _status_response(self) -> str:
        """Respond to 'how are you' with personality"""
        if self.user_name:
            return (
                f"I'm operating at full capacity, {self.user_name}! "
                f"All systems are online and ready to assist you. "
                f"More importantly, how are YOU doing?"
            )
        else:
            return (
                "I'm operating at full capacity! "
                "All systems are online and ready to assist you. "
                "How are you doing today?"
            )

    def converse(self, user_input: str) -> str:
        """
        Full conversational AI using LLM with memory & profile context.
        Use this for natural language responses.
        Falls back to helpful message if LLM unavailable.
        """
        # Learn from user input (detect personal info)
        self._learn_from_input(user_input)
        
        # Increment conversation count
        self.profile.increment_conversation_count()
        
        # Get combined context from memory and profile
        memory_context = self.memory.get_context_for_llm()
        profile_context = self.profile.get_context_summary()
        
        # Combine contexts
        full_context = ""
        if profile_context:
            full_context += profile_context + "\n\n"
        if memory_context:
            full_context += memory_context
        
        # Try LLM with full context
        response = self.llm.chat_with_context(user_input, full_context)
        
        # Save conversation to memory
        self.memory.save_conversation(user_input, response, full_context[:200])
        
        # If LLM failed and returned error message, try smart fallback
        if response and ("unavailable" in response.lower() or "trouble connecting" in response.lower()):
            # Provide helpful fallback based on query type
            text = user_input.lower()
            
            if any(word in text for word in ["code", "program", "script", "function"]):
                return "I'd love to help with code, but I need my AI brain (Ollama) running for complex tasks. Try: 'ollama serve' in terminal."
            
            elif "?" in user_input:
                return f"That's a great question! I can give better answers when Ollama is running. For now, try asking me about system status, available tasks, or my capabilities."
            
            else:
                return "I understand. For more detailed responses, please ensure Ollama is running with 'ollama serve'."
        
        return response
    
    def _learn_from_input(self, user_input: str):
        """
        Detect and learn from user input (name, preferences, facts).
        Updates both Profile and Memory systems.
        """
        text = user_input.lower().strip()
        
        # Learn user's name
        if any(phrase in text for phrase in ["my name is", "i'm", "i am", "call me"]):
            # Extract name
            for phrase in ["my name is ", "i'm ", "i am ", "call me "]:
                if phrase in text:
                    parts = text.split(phrase, 1)
                    if len(parts) > 1:
                        potential_name = parts[1].split()[0].strip('.,!?')
                        # Capitalize first letter
                        name = potential_name.capitalize()
                        if len(name) > 1 and name.isalpha():
                            self.profile.set_name(name)
                            self.user_name = name
                            break
        
        # Learn preferences - likes
        if any(phrase in text for phrase in ["i like", "i love", "i prefer", "i enjoy"]):
            for phrase in ["i like ", "i love ", "i prefer ", "i enjoy "]:
                if phrase in text:
                    parts = text.split(phrase, 1)
                    if len(parts) > 1:
                        preference = parts[1].strip('.,!?')
                        self.profile.add_interest(preference)
                        self.memory.learn_preference('likes', preference, confidence=0.9)
                        break
        
        # Learn preferences - dislikes
        if any(phrase in text for phrase in ["i don't like", "i hate", "i dislike"]):
            for phrase in ["i don't like ", "i hate ", "i dislike "]:
                if phrase in text:
                    parts = text.split(phrase, 1)
                    if len(parts) > 1:
                        dislike = parts[1].strip('.,!?')
                        self.memory.learn_preference('dislikes', dislike, confidence=0.9)
                        break
        
        # Learn location
        if any(phrase in text for phrase in ["i live in", "i'm from", "i am from"]):
            for phrase in ["i live in ", "i'm from ", "i am from "]:
                if phrase in text:
                    parts = text.split(phrase, 1)
                    if len(parts) > 1:
                        location = parts[1].strip('.,!?')
                        self.profile.set_location(location)
                        self.memory.set_user_info('location', location)
                        break
        
        # Learn profession
        if any(phrase in text for phrase in ["i work as", "i'm a", "i am a", "my job"]):
            for phrase in ["i work as ", "i'm a ", "i am a "]:
                if phrase in text:
                    parts = text.split(phrase, 1)
                    if len(parts) > 1:
                        job = parts[1].strip('.,!?')
                        self.profile.set_occupation(job)
                        self.memory.set_user_info('profession', job)
                        break
        
        # Learn skills
        if any(phrase in text for phrase in ["i know", "i can", "i'm good at"]):
            for phrase in ["i know ", "i can ", "i'm good at "]:
                if phrase in text:
                    parts = text.split(phrase, 1)
                    if len(parts) > 1:
                        skill = parts[1].strip('.,!?')
                        self.profile.add_skill(skill)
                        break
"""
ARES Voice Assistant
====================
Integrates Voice Engine with AI Brain for complete voice interaction.

Features:
- Wake word activation ("Hey ARES")
- Voice commands processed by AI Brain
- Voice responses from ARES
- Continuous listening mode
- Status callbacks for UI updates
"""

import threading
import time
from typing import Optional, Callable
from pathlib import Path
import sys

# Add project root to path
PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from voice.voice_engine import VoiceEngine, VoiceConfig, VoiceState


class AresVoiceAssistant:
    """
    Complete voice assistant for ARES.
    Handles voice interaction loop and integrates with AI Brain.
    """
    
    def __init__(self):
        # Voice configuration
        self.config = VoiceConfig(
            wake_words=["ares", "hey ares", "ok ares", "hello ares"],
            language="en-US",
            timeout=5,
            phrase_timeout=10,
            voice_rate=175,
            voice_volume=1.0
        )
        
        # Initialize voice engine
        self.voice = VoiceEngine(self.config)
        
        # AI Brain (loaded lazily)
        self.brain = None
        
        # State
        self.is_running = False
        self.wake_word_enabled = True
        
        # Callbacks for UI integration
        self.on_listening = None
        self.on_processing = None
        self.on_speaking = None
        self.on_idle = None
        self.on_transcript = None
        self.on_response = None
        self.on_error = None
        
        # Set up voice engine callbacks
        self._setup_callbacks()
        
        # Greeting messages
        self.greetings = [
            "Yes?",
            "I'm listening.",
            "How can I help?",
            "At your service.",
            "What do you need?"
        ]
        self._greeting_index = 0
    
    def _setup_callbacks(self):
        """Set up voice engine callbacks"""
        def on_state_change(state: VoiceState):
            if state == VoiceState.LISTENING:
                if self.on_listening:
                    self.on_listening()
            elif state == VoiceState.PROCESSING:
                if self.on_processing:
                    self.on_processing()
            elif state == VoiceState.SPEAKING:
                if self.on_speaking:
                    self.on_speaking()
            elif state == VoiceState.IDLE:
                if self.on_idle:
                    self.on_idle()
        
        def on_speech_detected(text: str):
            if self.on_transcript:
                self.on_transcript(text)
        
        def on_error(error: str):
            if self.on_error:
                self.on_error(error)
        
        self.voice.on_state_change = on_state_change
        self.voice.on_speech_detected = on_speech_detected
        self.voice.on_error = on_error
    
    def _load_brain(self):
        """Load AI Brain lazily"""
        if self.brain is None:
            try:
                from ai.brain import AIBrain
                self.brain = AIBrain()
                print("✓ AI Brain connected to Voice Assistant")
            except Exception as e:
                print(f"⚠ Could not load AI Brain: {e}")
                self.brain = None
    
    def _get_greeting(self) -> str:
        """Get next greeting phrase"""
        greeting = self.greetings[self._greeting_index]
        self._greeting_index = (self._greeting_index + 1) % len(self.greetings)
        return greeting
    
    # =====================================
    # CORE VOICE INTERACTION
    # =====================================
    
    def process_command(self, command: str) -> str:
        """
        Process a voice command and return response.
        
        Args:
            command: The command text from user
            
        Returns:
            Response text from ARES
        """
        self._load_brain()
        
        if not self.brain:
            return "I'm sorry, my AI brain is not available right now."
        
        try:
            # Use AI Brain to process command
            result = self.brain.think(command)
            
            # Check if we have a pre-built reply
            if isinstance(result, dict) and result.get("reply"):
                return result["reply"]
            
            # Otherwise, use conversational AI
            response = self.brain.converse(command)
            return response
            
        except Exception as e:
            print(f"⚠ Error processing command: {e}")
            return "I'm sorry, I encountered an error processing that command."
    
    def say(self, text: str, block: bool = True):
        """Make ARES speak"""
        if self.on_response:
            self.on_response(text)
        self.voice.speak(text, block=block)
    
    def listen(self) -> Optional[str]:
        """Listen for voice input"""
        return self.voice.listen_once()
    
    # =====================================
    # VOICE ASSISTANT MODES
    # =====================================
    
    def single_command(self) -> Optional[str]:
        """
        Listen for a single command and respond.
        
        Returns:
            The command that was processed, or None
        """
        # Listen for speech
        text = self.listen()
        
        if not text:
            return None
        
        # Process based on wake word mode
        if self.wake_word_enabled:
            if self.voice.check_wake_word(text):
                command = self.voice.extract_command(text)
                
                if command:
                    response = self.process_command(command)
                    self.say(response)
                    return command
                else:
                    # Just wake word, prompt for command
                    self.say(self._get_greeting())
                    
                    # Listen for follow-up
                    follow_up = self.listen()
                    if follow_up:
                        response = self.process_command(follow_up)
                        self.say(response)
                        return follow_up
            else:
                # No wake word detected
                return None
        else:
            # No wake word required
            response = self.process_command(text)
            self.say(response)
            return text
        
        return None
    
    def start_assistant(self, wake_word_mode: bool = True):
        """
        Start the voice assistant in continuous mode.
        
        Args:
            wake_word_mode: Require wake word for activation
        """
        if self.is_running:
            print("⚠ Voice assistant already running")
            return
        
        self.is_running = True
        self.wake_word_enabled = wake_word_mode
        
        # Welcome message
        self.say("ARES voice assistant activated. Say 'Hey ARES' to give a command.")
        
        def assistant_loop():
            print("🎤 Voice Assistant Started")
            print(f"   Wake word mode: {wake_word_mode}")
            print("   Say 'Hey ARES' followed by your command")
            print("   Say 'ARES stop' to deactivate")
            
            while self.is_running:
                try:
                    # Listen for speech
                    text = self.voice.listen_once(timeout=10)
                    
                    if not text:
                        continue
                    
                    # Check for stop command
                    if any(stop in text.lower() for stop in ["ares stop", "stop ares", "ares quit", "quit ares"]):
                        self.say("Goodbye! Voice assistant deactivated.")
                        self.is_running = False
                        break
                    
                    # Process command
                    if wake_word_mode:
                        if self.voice.check_wake_word(text):
                            command = self.voice.extract_command(text)
                            
                            if command:
                                # Process the command
                                response = self.process_command(command)
                                self.say(response)
                            else:
                                # Wake word only - prompt for command
                                self.say(self._get_greeting())
                                
                                # Listen for follow-up
                                follow_up = self.voice.listen_once(timeout=8)
                                if follow_up:
                                    response = self.process_command(follow_up)
                                    self.say(response)
                    else:
                        # Process all speech
                        response = self.process_command(text)
                        self.say(response)
                        
                except KeyboardInterrupt:
                    break
                except Exception as e:
                    print(f"⚠ Assistant error: {e}")
                    time.sleep(1)
            
            print("🛑 Voice Assistant Stopped")
            if self.on_idle:
                self.on_idle()
        
        # Run in background thread
        self._assistant_thread = threading.Thread(target=assistant_loop, daemon=True)
        self._assistant_thread.start()
    
    def stop_assistant(self):
        """Stop the voice assistant"""
        self.is_running = False
        self.voice.stop_speaking()
        if hasattr(self, '_assistant_thread'):
            self._assistant_thread.join(timeout=2)
    
    # =====================================
    # SETTINGS
    # =====================================
    
    def set_wake_words(self, words: list):
        """Update wake words"""
        self.config.wake_words = [w.lower() for w in words]
        self.voice.config.wake_words = self.config.wake_words
    
    def set_language(self, language: str):
        """Set recognition language (e.g., 'en-US', 'en-GB', 'hi-IN')"""
        self.config.language = language
        self.voice.config.language = language
    
    def set_voice_speed(self, rate: int):
        """Set TTS speed (words per minute, default 175)"""
        self.voice.set_voice_rate(rate)
    
    def set_voice_volume(self, volume: float):
        """Set TTS volume (0.0 to 1.0)"""
        self.voice.set_voice_volume(volume)
    
    def list_voices(self) -> list:
        """Get available TTS voices"""
        return self.voice.list_voices()
    
    def set_voice(self, voice_id: int):
        """Set TTS voice by index"""
        self.voice.set_voice(voice_id)
    
    # =====================================
    # TESTING
    # =====================================
    
    def test_voice_output(self):
        """Test TTS"""
        self.say("Hello! I am ARES, your personal AI assistant. Voice output is working correctly.")
    
    def test_voice_input(self) -> bool:
        """Test microphone"""
        self.say("Testing microphone. Please say something.")
        time.sleep(0.5)
        
        text = self.listen()
        
        if text:
            self.say(f"I heard you say: {text}")
            return True
        else:
            self.say("I couldn't hear anything. Please check your microphone.")
            return False
    
    def test_full_cycle(self):
        """Test complete voice interaction"""
        self.say("Testing full voice cycle. Say 'Hey ARES' followed by a command.")
        
        text = self.voice.listen_once(timeout=10)
        
        if text and self.voice.check_wake_word(text):
            command = self.voice.extract_command(text)
            self.say(f"Wake word detected! Command: {command}")
            
            response = self.process_command(command)
            self.say(response)
        else:
            self.say("No wake word detected. Please try again.")


# =====================================
# STANDALONE INTERACTIVE MODE
# =====================================

def interactive_mode():
    """Run voice assistant in interactive mode"""
    print("=" * 60)
    print("🎤 ARES VOICE ASSISTANT - Interactive Mode")
    print("=" * 60)
    print()
    print("Commands:")
    print("  'start' - Start continuous listening")
    print("  'stop'  - Stop listening")
    print("  'test'  - Test voice input/output")
    print("  'quit'  - Exit")
    print()
    
    assistant = AresVoiceAssistant()
    
    # Set up callbacks for console output
    assistant.on_listening = lambda: print("🎤 Listening...")
    assistant.on_processing = lambda: print("🔄 Processing...")
    assistant.on_speaking = lambda: print("🔊 Speaking...")
    assistant.on_transcript = lambda t: print(f"📝 Heard: {t}")
    assistant.on_response = lambda r: print(f"💬 ARES: {r}")
    
    while True:
        try:
            cmd = input("\n> ").strip().lower()
            
            if cmd == "start":
                print("Starting voice assistant...")
                assistant.start_assistant(wake_word_mode=True)
                
            elif cmd == "stop":
                print("Stopping voice assistant...")
                assistant.stop_assistant()
                
            elif cmd == "test":
                print("\n[Testing Voice Output]")
                assistant.test_voice_output()
                
                print("\n[Testing Voice Input]")
                assistant.test_voice_input()
                
            elif cmd == "voices":
                print("\nAvailable voices:")
                for v in assistant.list_voices():
                    print(f"  {v['id']}: {v['name']}")
                
            elif cmd == "quit" or cmd == "exit":
                assistant.stop_assistant()
                print("Goodbye!")
                break
                
            elif cmd:
                # Direct command processing
                response = assistant.process_command(cmd)
                assistant.say(response)
                
        except KeyboardInterrupt:
            assistant.stop_assistant()
            print("\nGoodbye!")
            break


if __name__ == "__main__":
    interactive_mode()
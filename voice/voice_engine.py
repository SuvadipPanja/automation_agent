"""
ARES Voice Engine
=================
Complete voice assistant system with:
- Speech-to-Text (microphone input)
- Text-to-Speech (voice output)
- Wake word detection
- Continuous listening mode

Requirements:
    pip install SpeechRecognition pyttsx3 pyaudio
    
For Windows, you may also need:
    pip install pipwin
    pipwin install pyaudio
"""

import speech_recognition as sr
import pyttsx3
import threading
import queue
import time
from typing import Optional, Callable
from dataclasses import dataclass
from enum import Enum


class VoiceState(Enum):
    """Voice assistant states"""
    IDLE = "IDLE"
    LISTENING = "LISTENING"
    PROCESSING = "PROCESSING"
    SPEAKING = "SPEAKING"
    ERROR = "ERROR"


@dataclass
class VoiceConfig:
    """Voice configuration settings"""
    # Wake words that activate ARES
    wake_words: list = None
    
    # Speech recognition settings
    language: str = "en-US"
    timeout: int = 5  # Seconds to wait for speech
    phrase_timeout: int = 3  # Max seconds for a phrase
    
    # Text-to-speech settings
    voice_rate: int = 175  # Words per minute (default ~200)
    voice_volume: float = 1.0  # 0.0 to 1.0
    voice_id: int = 0  # Voice index (0 = default)
    
    def __post_init__(self):
        if self.wake_words is None:
            self.wake_words = ["ares", "hey ares", "ok ares", "hello ares"]


class VoiceEngine:
    """
    ARES Voice Engine
    Handles all voice input/output operations
    """
    
    def __init__(self, config: Optional[VoiceConfig] = None):
        self.config = config or VoiceConfig()
        self.state = VoiceState.IDLE
        
        # Initialize speech recognition
        self.recognizer = sr.Recognizer()
        self.microphone = None
        
        # Initialize text-to-speech
        self.tts_engine = None
        self._init_tts()
        
        # Callbacks
        self.on_state_change: Optional[Callable] = None
        self.on_speech_detected: Optional[Callable] = None
        self.on_wake_word: Optional[Callable] = None
        self.on_command: Optional[Callable] = None
        self.on_error: Optional[Callable] = None
        
        # Continuous listening
        self._listening = False
        self._listen_thread: Optional[threading.Thread] = None
        self._command_queue = queue.Queue()
        
        # Adjust for ambient noise
        self._calibrated = False
    
    def _init_tts(self):
        """Initialize text-to-speech engine"""
        try:
            self.tts_engine = pyttsx3.init()
            self.tts_engine.setProperty('rate', self.config.voice_rate)
            self.tts_engine.setProperty('volume', self.config.voice_volume)
            
            # Try to set voice
            voices = self.tts_engine.getProperty('voices')
            if voices and len(voices) > self.config.voice_id:
                self.tts_engine.setProperty('voice', voices[self.config.voice_id].id)
            
            print("✓ Text-to-Speech initialized")
        except Exception as e:
            print(f"⚠ TTS initialization failed: {e}")
            self.tts_engine = None
    
    def _set_state(self, state: VoiceState):
        """Update state and notify callback"""
        self.state = state
        if self.on_state_change:
            self.on_state_change(state)
    
    # =====================================
    # TEXT-TO-SPEECH (ARES SPEAKS)
    # =====================================
    
    def speak(self, text: str, block: bool = True):
        """
        Make ARES speak the given text
        
        Args:
            text: Text to speak
            block: Wait for speech to complete
        """
        if not self.tts_engine:
            print(f"[TTS Disabled] ARES: {text}")
            return
        
        try:
            self._set_state(VoiceState.SPEAKING)
            
            # Clean text for speech
            clean_text = self._clean_for_speech(text)
            
            self.tts_engine.say(clean_text)
            
            if block:
                self.tts_engine.runAndWait()
                self._set_state(VoiceState.IDLE)
            else:
                # Non-blocking speech
                def speak_thread():
                    self.tts_engine.runAndWait()
                    self._set_state(VoiceState.IDLE)
                
                threading.Thread(target=speak_thread, daemon=True).start()
                
        except Exception as e:
            print(f"⚠ Speech error: {e}")
            self._set_state(VoiceState.ERROR)
    
    def _clean_for_speech(self, text: str) -> str:
        """Clean text for better speech output"""
        # Remove emojis and special characters
        import re
        
        # Remove emojis
        emoji_pattern = re.compile("["
            u"\U0001F600-\U0001F64F"  # emoticons
            u"\U0001F300-\U0001F5FF"  # symbols & pictographs
            u"\U0001F680-\U0001F6FF"  # transport & map symbols
            u"\U0001F1E0-\U0001F1FF"  # flags
            u"\U00002702-\U000027B0"
            u"\U000024C2-\U0001F251"
            "]+", flags=re.UNICODE)
        
        text = emoji_pattern.sub('', text)
        
        # Remove bullet points and formatting
        text = text.replace('•', '')
        text = text.replace('*', '')
        text = text.replace('#', '')
        text = text.replace('`', '')
        
        # Clean multiple spaces
        text = ' '.join(text.split())
        
        return text
    
    def stop_speaking(self):
        """Stop current speech"""
        if self.tts_engine:
            try:
                self.tts_engine.stop()
            except:
                pass
        self._set_state(VoiceState.IDLE)
    
    # =====================================
    # SPEECH-TO-TEXT (USER SPEAKS)
    # =====================================
    
    def listen_once(self, timeout: int = None) -> Optional[str]:
        """
        Listen for a single voice command
        
        Returns:
            Recognized text or None if failed
        """
        timeout = timeout or self.config.timeout
        
        try:
            self._set_state(VoiceState.LISTENING)
            
            with sr.Microphone() as source:
                # Calibrate for ambient noise (first time)
                if not self._calibrated:
                    print("🎤 Calibrating for ambient noise...")
                    self.recognizer.adjust_for_ambient_noise(source, duration=1)
                    self._calibrated = True
                
                print("🎤 Listening...")
                audio = self.recognizer.listen(
                    source, 
                    timeout=timeout,
                    phrase_time_limit=self.config.phrase_timeout
                )
            
            self._set_state(VoiceState.PROCESSING)
            print("🔄 Processing speech...")
            
            # Recognize speech using Google (free, no API key needed)
            text = self.recognizer.recognize_google(audio, language=self.config.language)
            
            print(f"✓ Heard: {text}")
            
            if self.on_speech_detected:
                self.on_speech_detected(text)
            
            self._set_state(VoiceState.IDLE)
            return text.lower()
            
        except sr.WaitTimeoutError:
            print("⏱ Listening timeout - no speech detected")
            self._set_state(VoiceState.IDLE)
            return None
            
        except sr.UnknownValueError:
            print("❓ Could not understand audio")
            self._set_state(VoiceState.IDLE)
            return None
            
        except sr.RequestError as e:
            print(f"⚠ Speech recognition error: {e}")
            self._set_state(VoiceState.ERROR)
            if self.on_error:
                self.on_error(f"Speech recognition error: {e}")
            return None
            
        except Exception as e:
            print(f"⚠ Microphone error: {e}")
            self._set_state(VoiceState.ERROR)
            if self.on_error:
                self.on_error(f"Microphone error: {e}")
            return None
    
    # =====================================
    # WAKE WORD DETECTION
    # =====================================
    
    def check_wake_word(self, text: str) -> bool:
        """Check if text contains a wake word"""
        if not text:
            return False
        
        text_lower = text.lower()
        
        for wake_word in self.config.wake_words:
            if wake_word in text_lower:
                return True
        
        return False
    
    def extract_command(self, text: str) -> str:
        """Extract command after wake word"""
        if not text:
            return ""
        
        text_lower = text.lower()
        
        # Find and remove wake word
        for wake_word in self.config.wake_words:
            if wake_word in text_lower:
                # Get everything after wake word
                idx = text_lower.find(wake_word) + len(wake_word)
                command = text[idx:].strip()
                
                # Remove common filler words
                for filler in [", ", ". ", "please ", "can you "]:
                    if command.lower().startswith(filler):
                        command = command[len(filler):]
                
                return command.strip()
        
        # No wake word found, return full text
        return text
    
    # =====================================
    # CONTINUOUS LISTENING MODE
    # =====================================
    
    def start_continuous_listening(self, wake_word_mode: bool = True):
        """
        Start continuous listening in background
        
        Args:
            wake_word_mode: If True, only process commands after wake word
        """
        if self._listening:
            print("⚠ Already listening")
            return
        
        self._listening = True
        
        def listen_loop():
            print("🎤 Continuous listening started")
            print(f"   Wake words: {', '.join(self.config.wake_words)}")
            
            while self._listening:
                try:
                    # Listen for speech
                    text = self.listen_once(timeout=10)
                    
                    if not text:
                        continue
                    
                    if wake_word_mode:
                        # Check for wake word
                        if self.check_wake_word(text):
                            command = self.extract_command(text)
                            
                            if self.on_wake_word:
                                self.on_wake_word()
                            
                            if command:
                                print(f"🎯 Command: {command}")
                                if self.on_command:
                                    self.on_command(command)
                                self._command_queue.put(command)
                            else:
                                # Wake word detected but no command - prompt user
                                self.speak("Yes? How can I help?")
                                
                                # Listen for follow-up command
                                follow_up = self.listen_once(timeout=5)
                                if follow_up:
                                    print(f"🎯 Command: {follow_up}")
                                    if self.on_command:
                                        self.on_command(follow_up)
                                    self._command_queue.put(follow_up)
                    else:
                        # No wake word required - process all speech
                        if self.on_command:
                            self.on_command(text)
                        self._command_queue.put(text)
                        
                except Exception as e:
                    print(f"⚠ Listening error: {e}")
                    time.sleep(1)
            
            print("🛑 Continuous listening stopped")
        
        self._listen_thread = threading.Thread(target=listen_loop, daemon=True)
        self._listen_thread.start()
    
    def stop_continuous_listening(self):
        """Stop continuous listening"""
        self._listening = False
        if self._listen_thread:
            self._listen_thread.join(timeout=2)
            self._listen_thread = None
    
    def get_next_command(self, timeout: float = None) -> Optional[str]:
        """Get next command from queue"""
        try:
            return self._command_queue.get(timeout=timeout)
        except queue.Empty:
            return None
    
    # =====================================
    # VOICE SETTINGS
    # =====================================
    
    def set_voice_rate(self, rate: int):
        """Set speech rate (words per minute)"""
        self.config.voice_rate = rate
        if self.tts_engine:
            self.tts_engine.setProperty('rate', rate)
    
    def set_voice_volume(self, volume: float):
        """Set voice volume (0.0 to 1.0)"""
        self.config.voice_volume = max(0.0, min(1.0, volume))
        if self.tts_engine:
            self.tts_engine.setProperty('volume', self.config.voice_volume)
    
    def list_voices(self) -> list:
        """List available TTS voices"""
        if not self.tts_engine:
            return []
        
        voices = self.tts_engine.getProperty('voices')
        return [
            {
                'id': i,
                'name': v.name,
                'languages': v.languages,
                'gender': v.gender
            }
            for i, v in enumerate(voices)
        ]
    
    def set_voice(self, voice_id: int):
        """Set TTS voice by index"""
        if not self.tts_engine:
            return
        
        voices = self.tts_engine.getProperty('voices')
        if 0 <= voice_id < len(voices):
            self.tts_engine.setProperty('voice', voices[voice_id].id)
            self.config.voice_id = voice_id
    
    # =====================================
    # UTILITY METHODS
    # =====================================
    
    def test_microphone(self) -> bool:
        """Test if microphone is working"""
        try:
            with sr.Microphone() as source:
                print("🎤 Testing microphone... (speak something)")
                self.recognizer.adjust_for_ambient_noise(source, duration=1)
                audio = self.recognizer.listen(source, timeout=3)
                text = self.recognizer.recognize_google(audio)
                print(f"✓ Microphone working! Heard: {text}")
                return True
        except Exception as e:
            print(f"❌ Microphone test failed: {e}")
            return False
    
    def test_speaker(self) -> bool:
        """Test if speaker/TTS is working"""
        try:
            self.speak("ARES voice system online and operational.", block=True)
            return True
        except Exception as e:
            print(f"❌ Speaker test failed: {e}")
            return False
    
    def cleanup(self):
        """Clean up resources"""
        self.stop_continuous_listening()
        self.stop_speaking()
        if self.tts_engine:
            try:
                self.tts_engine.stop()
            except:
                pass


# =====================================
# STANDALONE TEST
# =====================================

if __name__ == "__main__":
    print("=" * 50)
    print("ARES Voice Engine Test")
    print("=" * 50)
    
    # Create voice engine
    voice = VoiceEngine()
    
    # Test TTS
    print("\n[Test 1] Text-to-Speech")
    voice.speak("Hello! I am ARES, your voice assistant.")
    
    # List voices
    print("\n[Test 2] Available Voices:")
    for v in voice.list_voices():
        print(f"  {v['id']}: {v['name']}")
    
    # Test microphone
    print("\n[Test 3] Microphone Test")
    print("Say something when prompted...")
    time.sleep(1)
    
    text = voice.listen_once(timeout=5)
    if text:
        print(f"You said: {text}")
        voice.speak(f"You said: {text}")
    else:
        print("No speech detected")
    
    # Test wake word
    print("\n[Test 4] Wake Word Detection")
    print("Say 'Hey ARES' followed by a command...")
    
    text = voice.listen_once(timeout=10)
    if text:
        if voice.check_wake_word(text):
            command = voice.extract_command(text)
            print(f"Wake word detected! Command: {command}")
            voice.speak(f"Command received: {command}")
        else:
            print(f"No wake word. You said: {text}")
    
    print("\n✓ Voice Engine test complete!")
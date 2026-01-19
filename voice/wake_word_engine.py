"""
=====================================================
ARES WAKE WORD DETECTION ENGINE
=====================================================
Listens continuously for "Hey ARES" wake word.
When detected, records command and sends to Whisper.

Options for wake word detection:
1. OpenWakeWord - Open source, runs locally (RECOMMENDED)
2. Porcupine - Best accuracy, needs API key
3. Vosk - Offline speech recognition
4. Simple energy-based detection + Whisper
=====================================================
"""

import os
import sys
import time
import wave
import tempfile
import threading
import queue
import numpy as np
from pathlib import Path

# Audio settings
SAMPLE_RATE = 16000
CHANNELS = 1
CHUNK_DURATION = 0.5  # seconds per chunk

# Try to import audio library
try:
    import sounddevice as sd
    AUDIO_AVAILABLE = True
except ImportError:
    AUDIO_AVAILABLE = False
    print("⚠ sounddevice not installed. Run: pip install sounddevice")

# Try to import Whisper
try:
    from faster_whisper import WhisperModel
    WHISPER_AVAILABLE = True
except ImportError:
    WHISPER_AVAILABLE = False
    print("⚠ faster-whisper not installed")


class WakeWordEngine:
    """
    Wake word detection engine for ARES.
    Listens for "Hey ARES" and triggers command recording.
    """
    
    # Wake word variations that Whisper might hear
    WAKE_WORDS = [
        "hey ares", "hey iris", "hey areas", "hey harris",
        "a ares", "ok ares", "hi ares", "hello ares",
        "hey eric", "hey aries", "hey aeris", "hey address",
        "hey arras", "hey eros", "hay ares", "hey arrest"
    ]
    
    def __init__(self, whisper_model="base", callback=None):
        """
        Initialize wake word engine.
        
        Args:
            whisper_model: Whisper model size
            callback: Function to call with transcribed command
        """
        self.whisper_model_size = whisper_model
        self.whisper = None
        self.callback = callback
        
        self.is_running = False
        self.is_recording_command = False
        self.audio_queue = queue.Queue()
        
        # Audio settings
        self.sample_rate = SAMPLE_RATE
        self.channels = CHANNELS
        self.chunk_size = int(SAMPLE_RATE * CHUNK_DURATION)
        
        # Detection settings
        self.silence_threshold = 0.01  # Adjust based on your mic
        self.speech_threshold = 0.02
        self.max_command_duration = 10  # seconds
        self.silence_after_speech = 1.5  # seconds of silence to stop
        
        # Callbacks
        self.on_wake_word = None
        self.on_command = None
        self.on_response = None
        self.on_error = None
        
    def load_whisper(self):
        """Load Whisper model."""
        if not WHISPER_AVAILABLE:
            print("❌ Whisper not available!")
            return False
        
        print(f"🔄 Loading Whisper '{self.whisper_model_size}'...")
        try:
            self.whisper = WhisperModel(
                self.whisper_model_size,
                device="cpu",
                compute_type="int8"
            )
            print(f"✅ Whisper loaded!")
            return True
        except Exception as e:
            print(f"❌ Failed to load Whisper: {e}")
            return False
    
    def transcribe(self, audio_data):
        """Transcribe audio using Whisper."""
        if not self.whisper:
            return None
        
        # Save to temp file
        with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as f:
            with wave.open(f.name, 'wb') as wav:
                wav.setnchannels(self.channels)
                wav.setsampwidth(2)  # 16-bit
                wav.setframerate(self.sample_rate)
                # Convert float32 to int16
                audio_int16 = (audio_data * 32767).astype(np.int16)
                wav.writeframes(audio_int16.tobytes())
            
            temp_path = f.name
        
        try:
            segments, info = self.whisper.transcribe(
                temp_path,
                language="en",
                beam_size=5,
                vad_filter=True
            )
            text = " ".join([seg.text for seg in segments]).strip()
            return text
        except Exception as e:
            print(f"❌ Transcription error: {e}")
            return None
        finally:
            os.unlink(temp_path)
    
    def check_wake_word(self, text):
        """Check if text contains wake word."""
        if not text:
            return False, ""
        
        text_lower = text.lower().strip()
        
        for wake_word in self.WAKE_WORDS:
            if wake_word in text_lower:
                # Extract command after wake word
                idx = text_lower.find(wake_word)
                command = text_lower[idx + len(wake_word):].strip()
                # Clean up command
                command = command.lstrip(",. ")
                return True, command
        
        return False, ""
    
    def start(self):
        """Start wake word detection."""
        if not AUDIO_AVAILABLE:
            print("❌ Audio not available!")
            return
        
        if not self.whisper:
            if not self.load_whisper():
                return
        
        self.is_running = True
        
        print("\n" + "=" * 50)
        print("  🎤 ARES WAKE WORD DETECTION")
        print("=" * 50)
        print("  Say 'Hey ARES' to wake me up!")
        print("  Then speak your command.")
        print("  Say 'ARES stop' or 'quit' to exit.")
        print("=" * 50 + "\n")
        
        # Start audio processing thread
        self.process_thread = threading.Thread(target=self._process_audio)
        self.process_thread.start()
        
        # Start audio stream
        try:
            with sd.InputStream(
                samplerate=self.sample_rate,
                channels=self.channels,
                dtype=np.float32,
                blocksize=self.chunk_size,
                callback=self._audio_callback
            ):
                while self.is_running:
                    time.sleep(0.1)
        except Exception as e:
            print(f"❌ Audio stream error: {e}")
        
        self.is_running = False
        print("\n🛑 Wake word detection stopped.")
    
    def stop(self):
        """Stop wake word detection."""
        self.is_running = False
    
    def _audio_callback(self, indata, frames, time_info, status):
        """Callback for audio stream."""
        if status:
            print(f"Audio status: {status}")
        self.audio_queue.put(indata.copy())
    
    def _process_audio(self):
        """Process audio chunks and detect wake word."""
        buffer = []
        speech_started = False
        silence_count = 0
        listening_for_command = False
        
        while self.is_running:
            try:
                chunk = self.audio_queue.get(timeout=1)
            except queue.Empty:
                continue
            
            # Calculate volume
            volume = np.sqrt(np.mean(chunk ** 2))
            
            # Accumulate audio
            buffer.append(chunk)
            
            # Keep buffer to ~3 seconds for wake word detection
            max_chunks = int(3 / CHUNK_DURATION)
            if not listening_for_command and len(buffer) > max_chunks:
                buffer = buffer[-max_chunks:]
            
            # Check for speech
            if volume > self.speech_threshold:
                speech_started = True
                silence_count = 0
            elif speech_started:
                silence_count += 1
            
            # When silence after speech, process
            max_silence = int(self.silence_after_speech / CHUNK_DURATION)
            
            if speech_started and silence_count >= max_silence:
                # Concatenate audio
                audio = np.concatenate(buffer).flatten()
                
                if len(audio) > self.sample_rate * 0.5:  # At least 0.5s
                    
                    if not listening_for_command:
                        # Check for wake word
                        print("🔍 Checking for wake word...", end=" ", flush=True)
                        text = self.transcribe(audio)
                        
                        if text:
                            print(f"Heard: \"{text}\"")
                            
                            has_wake, command = self.check_wake_word(text)
                            
                            if has_wake:
                                print("\n🔔 WAKE WORD DETECTED!")
                                
                                if self.on_wake_word:
                                    self.on_wake_word()
                                
                                if command:
                                    # Command included with wake word
                                    print(f"📝 Command: \"{command}\"")
                                    self._handle_command(command)
                                else:
                                    # Wait for command
                                    print("🎤 Listening for command...")
                                    listening_for_command = True
                            
                            # Check for stop command
                            if "stop" in text.lower() and "ares" in text.lower():
                                print("\n👋 Goodbye!")
                                self.is_running = False
                            elif text.lower().strip() in ["quit", "exit", "stop listening"]:
                                print("\n👋 Goodbye!")
                                self.is_running = False
                        else:
                            print("(no speech)")
                    
                    else:
                        # We're listening for command after wake word
                        print("🔍 Transcribing command...", end=" ", flush=True)
                        text = self.transcribe(audio)
                        
                        if text:
                            print(f"Got: \"{text}\"")
                            self._handle_command(text)
                        else:
                            print("(no speech detected)")
                        
                        listening_for_command = False
                
                # Reset buffer
                buffer = []
                speech_started = False
                silence_count = 0
    
    def _handle_command(self, command):
        """Handle a voice command."""
        print(f"\n💬 Processing: \"{command}\"")
        
        # Check for stop command
        if command.lower() in ["stop", "quit", "exit", "stop listening"]:
            print("👋 Stopping...")
            self.is_running = False
            return
        
        if self.on_command:
            self.on_command(command)
        elif self.callback:
            self.callback(command)
        else:
            # Default response
            print(f"✅ Command received: {command}")
            print("   (Set callback to process commands)")


class AresVoiceAssistant(WakeWordEngine):
    """
    Complete voice assistant with wake word detection.
    """
    
    def __init__(self, whisper_model="base"):
        super().__init__(whisper_model)
        
        # TTS
        self.tts_engine = None
        self._init_tts()
        
        # AI callback
        self.ai_callback = None
    
    def _init_tts(self):
        """Initialize text-to-speech."""
        try:
            import pyttsx3
            self.tts_engine = pyttsx3.init()
            self.tts_engine.setProperty('rate', 150)
            print("✅ TTS initialized")
        except Exception as e:
            print(f"⚠ TTS not available: {e}")
    
    def speak(self, text):
        """Speak text."""
        print(f"🔊 ARES: {text}")
        
        if self.tts_engine:
            try:
                self.tts_engine.say(text)
                self.tts_engine.runAndWait()
            except:
                pass
    
    def set_ai_callback(self, callback):
        """Set callback for AI processing."""
        self.ai_callback = callback
    
    def _handle_command(self, command):
        """Handle command with AI."""
        # Speak acknowledgment
        self.speak("Processing your request.")
        
        if self.ai_callback:
            try:
                response = self.ai_callback(command)
                if response:
                    self.speak(response)
            except Exception as e:
                print(f"❌ AI error: {e}")
                self.speak("Sorry, I encountered an error.")
        else:
            # Echo the command
            self.speak(f"You said: {command}")


# =====================================================
# SIMPLE ARES INTEGRATION
# =====================================================
def create_ai_callback():
    """Create AI callback that connects to ARES brain."""
    try:
        # Add project root to path
        project_root = Path(__file__).parent.parent
        sys.path.insert(0, str(project_root))
        
        from ai.brain import AIBrain
        brain = AIBrain()
        print("✅ ARES Brain connected!")
        
        def callback(command):
            # Try brain.converse for chat
            try:
                response = brain.converse(command)
                return response
            except:
                return f"I heard: {command}"
        
        return callback
    
    except Exception as e:
        print(f"⚠ Could not connect to ARES brain: {e}")
        return None


# =====================================================
# MAIN
# =====================================================
if __name__ == "__main__":
    print("=" * 50)
    print("  ARES Voice Assistant with Wake Word")
    print("=" * 50)
    
    # Check requirements
    if not AUDIO_AVAILABLE:
        print("\n❌ Please install: pip install sounddevice numpy")
        sys.exit(1)
    
    if not WHISPER_AVAILABLE:
        print("\n❌ Please install: pip install faster-whisper")
        sys.exit(1)
    
    # Create assistant
    assistant = AresVoiceAssistant(whisper_model="base")
    
    # Connect to AI
    ai_callback = create_ai_callback()
    if ai_callback:
        assistant.set_ai_callback(ai_callback)
    
    # Custom wake word handler
    def on_wake():
        assistant.speak("Yes? How can I help you?")
    
    assistant.on_wake_word = on_wake
    
    # Start listening
    try:
        assistant.start()
    except KeyboardInterrupt:
        print("\n\n👋 Goodbye!")
        assistant.stop()
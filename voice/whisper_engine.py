"""
=====================================================
ARES WHISPER VOICE ENGINE
=====================================================
Uses OpenAI Whisper for accurate local speech recognition
Much better than browser speech recognition!
=====================================================
"""

import os
import sys
import wave
import tempfile
import threading
import queue
import time
import numpy as np

# Try to import audio libraries
try:
    import sounddevice as sd
    SOUNDDEVICE_AVAILABLE = True
except ImportError:
    SOUNDDEVICE_AVAILABLE = False
    print("⚠ sounddevice not installed. Run: pip install sounddevice")

# Try to import Whisper
WHISPER_TYPE = None
whisper_model = None

try:
    from faster_whisper import WhisperModel
    WHISPER_TYPE = "faster"
    print("✓ Using faster-whisper (recommended)")
except ImportError:
    try:
        import whisper
        WHISPER_TYPE = "openai"
        print("✓ Using openai-whisper")
    except ImportError:
        print("⚠ Whisper not installed!")
        print("  Run: pip install faster-whisper")
        print("  Or:  pip install openai-whisper")


class WhisperVoiceEngine:
    """
    Whisper-based voice recognition engine.
    Much more accurate than browser speech recognition!
    """
    
    def __init__(self, model_size="base"):
        """
        Initialize Whisper model.
        
        Model sizes:
        - tiny: Fastest, least accurate (~1GB VRAM)
        - base: Good balance (~1GB VRAM) [RECOMMENDED]
        - small: Better accuracy (~2GB VRAM)
        - medium: High accuracy (~5GB VRAM)
        - large: Best accuracy (~10GB VRAM)
        """
        self.model_size = model_size
        self.model = None
        self.is_listening = False
        self.audio_queue = queue.Queue()
        self.sample_rate = 16000  # Whisper expects 16kHz
        self.channels = 1
        
        # Callbacks
        self.on_transcription = None
        self.on_partial = None
        self.on_error = None
        
        # Load model
        self._load_model()
    
    def _load_model(self):
        """Load Whisper model."""
        global whisper_model
        
        if not WHISPER_TYPE:
            print("❌ Whisper not available!")
            return False
        
        print(f"🔄 Loading Whisper model '{self.model_size}'...")
        print("   (This may take a moment on first run)")
        
        try:
            if WHISPER_TYPE == "faster":
                # Faster Whisper (recommended)
                self.model = WhisperModel(
                    self.model_size,
                    device="cpu",  # Use "cuda" if you have NVIDIA GPU
                    compute_type="int8"  # Use "float16" for GPU
                )
            else:
                # OpenAI Whisper
                self.model = whisper.load_model(self.model_size)
            
            whisper_model = self.model
            print(f"✅ Whisper model '{self.model_size}' loaded!")
            return True
            
        except Exception as e:
            print(f"❌ Failed to load Whisper: {e}")
            return False
    
    def transcribe_audio(self, audio_data, sample_rate=16000):
        """
        Transcribe audio data using Whisper.
        
        Args:
            audio_data: numpy array of audio samples
            sample_rate: sample rate of audio
            
        Returns:
            Transcribed text
        """
        if not self.model:
            return None
        
        try:
            # Ensure audio is float32 and normalized
            if audio_data.dtype != np.float32:
                audio_data = audio_data.astype(np.float32)
            
            # Normalize if needed
            if np.max(np.abs(audio_data)) > 1.0:
                audio_data = audio_data / 32768.0
            
            if WHISPER_TYPE == "faster":
                # Faster Whisper
                segments, info = self.model.transcribe(
                    audio_data,
                    language="en",
                    beam_size=5,
                    vad_filter=True,  # Voice activity detection
                    vad_parameters=dict(
                        min_silence_duration_ms=500,
                        speech_pad_ms=200
                    )
                )
                text = " ".join([seg.text for seg in segments]).strip()
            else:
                # OpenAI Whisper
                result = self.model.transcribe(
                    audio_data,
                    language="en",
                    fp16=False
                )
                text = result["text"].strip()
            
            return text
            
        except Exception as e:
            print(f"❌ Transcription error: {e}")
            if self.on_error:
                self.on_error(str(e))
            return None
    
    def transcribe_file(self, audio_file):
        """Transcribe an audio file."""
        if not self.model:
            return None
        
        try:
            if WHISPER_TYPE == "faster":
                segments, info = self.model.transcribe(
                    audio_file,
                    language="en",
                    beam_size=5,
                    vad_filter=True
                )
                text = " ".join([seg.text for seg in segments]).strip()
            else:
                result = self.model.transcribe(audio_file, language="en", fp16=False)
                text = result["text"].strip()
            
            return text
            
        except Exception as e:
            print(f"❌ File transcription error: {e}")
            return None
    
    def record_audio(self, duration=5):
        """
        Record audio from microphone.
        
        Args:
            duration: Recording duration in seconds
            
        Returns:
            numpy array of audio samples
        """
        if not SOUNDDEVICE_AVAILABLE:
            print("❌ sounddevice not available!")
            return None
        
        print(f"🎤 Recording for {duration} seconds...")
        
        try:
            audio = sd.rec(
                int(duration * self.sample_rate),
                samplerate=self.sample_rate,
                channels=self.channels,
                dtype=np.float32
            )
            sd.wait()  # Wait until recording is finished
            
            print("✅ Recording complete!")
            return audio.flatten()
            
        except Exception as e:
            print(f"❌ Recording error: {e}")
            return None
    
    def listen_and_transcribe(self, duration=5):
        """
        Record audio and transcribe it.
        
        Args:
            duration: Recording duration in seconds
            
        Returns:
            Transcribed text
        """
        audio = self.record_audio(duration)
        if audio is None:
            return None
        
        print("🔄 Transcribing...")
        text = self.transcribe_audio(audio, self.sample_rate)
        
        if text:
            print(f"✅ Heard: \"{text}\"")
            if self.on_transcription:
                self.on_transcription(text)
        
        return text
    
    def start_continuous_listening(self, chunk_duration=3, silence_threshold=0.01):
        """
        Start continuous listening mode.
        Records in chunks and transcribes when speech is detected.
        """
        if not SOUNDDEVICE_AVAILABLE:
            print("❌ sounddevice not available!")
            return
        
        self.is_listening = True
        print("🎤 Continuous listening started...")
        print("   Speak naturally. Say 'stop listening' to stop.")
        
        def audio_callback(indata, frames, time_info, status):
            if status:
                print(f"Audio status: {status}")
            self.audio_queue.put(indata.copy())
        
        def process_audio():
            buffer = []
            silence_count = 0
            max_silence = 3  # Stop after 3 silent chunks
            
            while self.is_listening:
                try:
                    # Get audio chunk
                    chunk = self.audio_queue.get(timeout=1)
                    
                    # Check if there's speech
                    volume = np.sqrt(np.mean(chunk ** 2))
                    
                    if volume > silence_threshold:
                        buffer.append(chunk)
                        silence_count = 0
                    else:
                        silence_count += 1
                        
                        # If we have audio and silence, transcribe
                        if buffer and silence_count >= max_silence:
                            audio = np.concatenate(buffer).flatten()
                            
                            if len(audio) > self.sample_rate * 0.5:  # At least 0.5s
                                text = self.transcribe_audio(audio, self.sample_rate)
                                
                                if text and self.on_transcription:
                                    self.on_transcription(text)
                                
                                # Check for stop command
                                if text and "stop listening" in text.lower():
                                    self.is_listening = False
                                    print("🛑 Stopping...")
                            
                            buffer = []
                
                except queue.Empty:
                    continue
                except Exception as e:
                    print(f"Error: {e}")
        
        # Start recording stream
        try:
            with sd.InputStream(
                samplerate=self.sample_rate,
                channels=self.channels,
                dtype=np.float32,
                blocksize=int(self.sample_rate * 0.5),  # 0.5s chunks
                callback=audio_callback
            ):
                process_audio()
        except Exception as e:
            print(f"❌ Stream error: {e}")
        
        print("🛑 Continuous listening stopped.")
    
    def stop_listening(self):
        """Stop continuous listening."""
        self.is_listening = False


# =====================================================
# FLASK API ENDPOINTS FOR WHISPER
# =====================================================
from flask import Blueprint, request, jsonify
import base64
import io

whisper_bp = Blueprint('whisper', __name__)

# Global engine instance
_whisper_engine = None

def get_whisper_engine():
    """Get or create Whisper engine."""
    global _whisper_engine
    if _whisper_engine is None:
        _whisper_engine = WhisperVoiceEngine(model_size="base")
    return _whisper_engine


@whisper_bp.route('/whisper/transcribe', methods=['POST'])
def transcribe_audio():
    """
    Transcribe audio sent as base64 or file.
    
    POST JSON: {"audio": "base64_audio_data", "format": "wav"}
    Or POST file: multipart/form-data with 'audio' file
    """
    engine = get_whisper_engine()
    
    if not engine.model:
        return jsonify({
            "error": "Whisper model not loaded",
            "hint": "Run: pip install faster-whisper"
        }), 500
    
    try:
        # Check for file upload
        if 'audio' in request.files:
            audio_file = request.files['audio']
            
            # Save to temp file
            with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as f:
                audio_file.save(f.name)
                text = engine.transcribe_file(f.name)
                os.unlink(f.name)
        
        # Check for base64 audio
        elif request.is_json:
            data = request.get_json()
            audio_b64 = data.get('audio')
            
            if not audio_b64:
                return jsonify({"error": "No audio data provided"}), 400
            
            # Decode base64
            audio_bytes = base64.b64decode(audio_b64)
            
            # Save to temp file
            with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as f:
                f.write(audio_bytes)
                f.flush()
                text = engine.transcribe_file(f.name)
                os.unlink(f.name)
        
        else:
            return jsonify({"error": "No audio provided"}), 400
        
        if text:
            return jsonify({
                "success": True,
                "text": text
            })
        else:
            return jsonify({
                "success": False,
                "text": "",
                "error": "No speech detected"
            })
    
    except Exception as e:
        return jsonify({
            "error": str(e)
        }), 500


@whisper_bp.route('/whisper/status', methods=['GET'])
def whisper_status():
    """Check Whisper engine status."""
    engine = get_whisper_engine()
    
    return jsonify({
        "available": engine.model is not None,
        "whisper_type": WHISPER_TYPE,
        "model_size": engine.model_size if engine.model else None,
        "sounddevice": SOUNDDEVICE_AVAILABLE
    })


# =====================================================
# COMMAND LINE TEST
# =====================================================
if __name__ == "__main__":
    print("=" * 50)
    print("  ARES Whisper Voice Engine Test")
    print("=" * 50)
    
    # Create engine
    engine = WhisperVoiceEngine(model_size="base")
    
    if not engine.model:
        print("\n❌ Whisper not available!")
        print("Install with: pip install faster-whisper sounddevice numpy")
        sys.exit(1)
    
    if not SOUNDDEVICE_AVAILABLE:
        print("\n❌ sounddevice not available!")
        print("Install with: pip install sounddevice")
        sys.exit(1)
    
    # Test recording and transcription
    print("\n🎤 Say something (5 seconds)...")
    text = engine.listen_and_transcribe(duration=5)
    
    if text:
        print(f"\n✅ You said: \"{text}\"")
    else:
        print("\n❌ Could not transcribe audio")
    
    # Ask if user wants continuous mode
    print("\n" + "=" * 50)
    response = input("Try continuous listening? (y/n): ")
    
    if response.lower() == 'y':
        def on_text(text):
            print(f"📝 Heard: \"{text}\"")
        
        engine.on_transcription = on_text
        engine.start_continuous_listening()
"""
=====================================================
ARES Voice Routes - Whisper Edition
=====================================================
API endpoints for:
- Whisper speech-to-text (accurate!)
- Voice status checking
- Model management
=====================================================
"""

from flask import Blueprint, request, jsonify
import base64
import tempfile
import os
import sys

# Add parent directory for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

voice_bp = Blueprint('voice', __name__, url_prefix='/voice')

# =====================================================
# WHISPER SETUP
# =====================================================
WHISPER_AVAILABLE = False
WHISPER_TYPE = None
whisper_model = None

try:
    from faster_whisper import WhisperModel
    WHISPER_TYPE = "faster-whisper"
    WHISPER_AVAILABLE = True
    print("✓ faster-whisper available")
except ImportError:
    try:
        import whisper
        WHISPER_TYPE = "openai-whisper"
        WHISPER_AVAILABLE = True
        print("✓ openai-whisper available")
    except ImportError:
        print("⚠ Whisper not installed")
        print("  Install with: pip install faster-whisper")


def get_whisper_model(model_size="base"):
    """Load or get cached Whisper model."""
    global whisper_model
    
    if whisper_model is not None:
        return whisper_model
    
    if not WHISPER_AVAILABLE:
        return None
    
    print(f"🔄 Loading Whisper model '{model_size}'...")
    
    try:
        if WHISPER_TYPE == "faster-whisper":
            whisper_model = WhisperModel(
                model_size,
                device="cpu",
                compute_type="int8"
            )
        else:
            import whisper
            whisper_model = whisper.load_model(model_size)
        
        print(f"✅ Whisper model '{model_size}' loaded!")
        return whisper_model
    
    except Exception as e:
        print(f"❌ Failed to load Whisper: {e}")
        return None


def transcribe_with_whisper(audio_path, language="en"):
    """Transcribe audio file using Whisper."""
    model = get_whisper_model()
    
    if not model:
        return {"error": "Whisper not available", "text": ""}
    
    try:
        if WHISPER_TYPE == "faster-whisper":
            segments, info = model.transcribe(
                audio_path,
                language=language,
                beam_size=5,
                vad_filter=True,
                vad_parameters=dict(
                    min_silence_duration_ms=500,
                    speech_pad_ms=200
                )
            )
            text = " ".join([seg.text for seg in segments]).strip()
        else:
            result = model.transcribe(audio_path, language=language, fp16=False)
            text = result["text"].strip()
        
        return {"text": text, "language": language}
    
    except Exception as e:
        return {"error": str(e), "text": ""}


# =====================================================
# API ROUTES
# =====================================================

@voice_bp.route('/status', methods=['GET'])
def voice_status():
    """Get voice system status."""
    return jsonify({
        "whisper_available": WHISPER_AVAILABLE,
        "whisper_type": WHISPER_TYPE,
        "model_loaded": whisper_model is not None,
        "status": "ready" if WHISPER_AVAILABLE else "limited",
        "install_hint": "pip install faster-whisper" if not WHISPER_AVAILABLE else None
    })


@voice_bp.route('/transcribe', methods=['POST'])
def transcribe_audio():
    """
    Transcribe audio using Whisper.
    
    Accepts:
    - multipart/form-data with 'audio' file
    - JSON with 'audio_base64' field
    
    Query params:
    - language: Language code (default: 'en')
    
    Returns:
    - JSON with 'text' field
    """
    if not WHISPER_AVAILABLE:
        return jsonify({
            "error": "Whisper not available",
            "hint": "Install with: pip install faster-whisper",
            "text": ""
        }), 503
    
    language = request.args.get('language', 'en')
    temp_path = None
    
    try:
        # Handle file upload
        if 'audio' in request.files:
            audio_file = request.files['audio']
            
            # Get file extension
            filename = audio_file.filename or "audio.wav"
            ext = os.path.splitext(filename)[1] or ".wav"
            
            # Save to temp file
            with tempfile.NamedTemporaryFile(suffix=ext, delete=False) as f:
                audio_file.save(f.name)
                temp_path = f.name
        
        # Handle base64 audio
        elif request.is_json:
            data = request.get_json()
            audio_b64 = data.get('audio_base64') or data.get('audio')
            
            if not audio_b64:
                return jsonify({"error": "No audio data", "text": ""}), 400
            
            # Decode and save
            audio_bytes = base64.b64decode(audio_b64)
            with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as f:
                f.write(audio_bytes)
                temp_path = f.name
        
        # Handle raw bytes
        elif request.data:
            with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as f:
                f.write(request.data)
                temp_path = f.name
        
        else:
            return jsonify({"error": "No audio provided", "text": ""}), 400
        
        # Transcribe
        result = transcribe_with_whisper(temp_path, language)
        
        return jsonify(result)
    
    except Exception as e:
        return jsonify({"error": str(e), "text": ""}), 500
    
    finally:
        # Cleanup temp file
        if temp_path and os.path.exists(temp_path):
            try:
                os.unlink(temp_path)
            except:
                pass


@voice_bp.route('/models', methods=['GET'])
def list_models():
    """List available Whisper models."""
    return jsonify({
        "available_models": [
            {
                "name": "tiny",
                "size": "39 MB",
                "speed": "~32x realtime",
                "accuracy": "Good for clear speech"
            },
            {
                "name": "base",
                "size": "74 MB",
                "speed": "~16x realtime",
                "accuracy": "Recommended for most uses"
            },
            {
                "name": "small",
                "size": "244 MB",
                "speed": "~6x realtime",
                "accuracy": "Better accuracy"
            },
            {
                "name": "medium",
                "size": "769 MB",
                "speed": "~2x realtime",
                "accuracy": "High accuracy"
            },
            {
                "name": "large-v3",
                "size": "1550 MB",
                "speed": "~1x realtime",
                "accuracy": "Best accuracy"
            }
        ],
        "current_model": "base",
        "recommendation": "Use 'base' for fast responses, 'small' for better accuracy"
    })


@voice_bp.route('/load-model', methods=['POST'])
def load_model():
    """
    Load a specific Whisper model.
    
    JSON body:
    - model: Model name (tiny, base, small, medium, large-v3)
    """
    global whisper_model
    
    if not WHISPER_AVAILABLE:
        return jsonify({"error": "Whisper not available"}), 503
    
    data = request.get_json(silent=True)
    model_name = data.get('model', 'base') if data else 'base'
    
    valid_models = ['tiny', 'base', 'small', 'medium', 'large-v3']
    if model_name not in valid_models:
        return jsonify({
            "error": f"Invalid model. Choose from: {valid_models}"
        }), 400
    
    # Unload current model
    whisper_model = None
    
    # Load new model
    try:
        if WHISPER_TYPE == "faster-whisper":
            whisper_model = WhisperModel(
                model_name,
                device="cpu",
                compute_type="int8"
            )
        else:
            import whisper
            whisper_model = whisper.load_model(model_name)
        
        return jsonify({
            "status": "loaded",
            "model": model_name
        })
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@voice_bp.route('/test', methods=['GET'])
def test_page():
    """Return simple test info."""
    return jsonify({
        "message": "Voice API is working!",
        "endpoints": {
            "/voice/status": "Check Whisper availability",
            "/voice/transcribe": "Transcribe audio (POST)",
            "/voice/models": "List available models",
            "/voice/load-model": "Load different model (POST)"
        },
        "whisper_ready": WHISPER_AVAILABLE
    })
"""
=====================================================
ARES WEB APPLICATION - INTEGRATED
=====================================================
Main Flask application for ARES.

Features:
? Web UI (JARVIS-style interface)
? AI Brain (Ollama/Llama3)
? Desktop Automation
? Whisper Voice Recognition
? Text-to-Speech (via browser)

All accessible from ONE entry point: main_web.py

Author: ARES AI Assistant
For: Shobutik Panja
=====================================================
"""

from flask import Flask, render_template, request, jsonify, send_from_directory
from pathlib import Path
import datetime
import traceback
import base64
import tempfile
import os

# ===========================================
# APP SETUP
# ===========================================

BASE_DIR = Path(__file__).resolve().parent

app = Flask(
    __name__,
    template_folder=str(BASE_DIR / "templates"),
    static_folder=str(BASE_DIR / "static")
)

# ===========================================
# COMPONENT LOADING
# ===========================================

# AI Brain
try:
    from ai.brain import AIBrain
    brain = AIBrain()
    print("? AI Brain loaded")
except Exception as e:
    brain = None
    print(f"? AI Brain not available: {e}")

# Desktop Controller - FIXED IMPORT
try:
    from automation import execute_command as desktop_execute
    from automation.desktop_control import desktop
    DESKTOP_OK = True
    print("? Desktop automation loaded")
except Exception as e:
    DESKTOP_OK = False
    desktop = None
    desktop_execute = None
    print(f"? Desktop automation not available: {e}")

# Whisper Voice Recognition
try:
    from faster_whisper import WhisperModel
    whisper_model = WhisperModel("base", device="cpu", compute_type="int8")
    WHISPER_OK = True
    print("? Whisper loaded")
except Exception as e:
    whisper_model = None
    WHISPER_OK = False
    print(f"? Whisper not available: {e}")

# Reminder System
try:
    from automation.reminders import get_reminder_manager
    reminder_manager = get_reminder_manager()
    REMINDERS_OK = True
    print("? Reminders loaded")
except Exception as e:
    reminder_manager = None
    REMINDERS_OK = False
    print(f"? Reminders not available: {e}")


# ===========================================
# STARTUP BANNER FUNCTION
# ===========================================

def print_startup():
    """Print startup banner with component status"""
    print("\n" + "=" * 60)
    print("   ?? ARES - Autonomous Runtime AI Agent")
    print("=" * 60)
    print(f"   AI Brain:    {'?' if brain else '?'}")
    print(f"   Desktop:     {'?' if DESKTOP_OK else '?'}")
    print(f"   Whisper:     {'?' if WHISPER_OK else '?'}")
    print(f"   Reminders:   {'?' if REMINDERS_OK else '?'}")
    print("=" * 60)
    print("   Modern UI: http://127.0.0.1:5000/")
    print("   Classic UI: http://127.0.0.1:5000/classic")
    print("   Memory: http://127.0.0.1:5000/memory")
    print("   Voice Test: http://127.0.0.1:5000/voice/test")
    print("=" * 60 + "\n")


# ===========================================
# BASIC ROUTES
# ===========================================

@app.route("/")
def index():
    """Main ARES UI - Modern JARVIS-style"""
    return render_template("index_modern.html")


@app.route("/classic")
def classic():
    """Classic ARES UI"""
    return render_template("index.html")


@app.route("/memory")
def memory_page():
    """Memory/Profile management page"""
    return render_template("memory.html")


@app.route("/health")
def health():
    """System health check."""
    return jsonify({
        "agent": "ARES",
        "status": "ONLINE",
        "time": datetime.datetime.now().isoformat(),
        "components": {
            "ai_brain": brain is not None,
            "desktop": DESKTOP_OK,
            "whisper": WHISPER_OK,
            "reminders": REMINDERS_OK
        }
    })


@app.route("/status")
def status():
    """Enhanced status endpoint"""
    return jsonify({
        "agent": "ARES",
        "status": "ONLINE",
        "version": "2.0",
        "time": datetime.datetime.now().isoformat(),
        "features": {
            "ai_brain": brain is not None,
            "desktop_automation": DESKTOP_OK,
            "whisper_available": WHISPER_OK,
            "reminders": REMINDERS_OK
        }
    })


@app.route("/tasks")
def tasks():
    """Available tasks."""
    return jsonify([
        {"name": "DESKTOP_CONTROL"},
        {"name": "VOICE_COMMAND"},
        {"name": "AI_CONVERSATION"},
        {"name": "REMINDERS"}
    ])


@app.route("/schedules")
def schedules():
    """Scheduled tasks."""
    return jsonify([])


@app.route("/reload-schedules", methods=["POST"])
def reload_schedules():
    """Reload schedules."""
    return jsonify({"status": "OK"})


# ===========================================
# REMINDER API ROUTES
# ===========================================

@app.route("/reminders")
def get_reminders():
    """Get all active reminders."""
    if not REMINDERS_OK or not reminder_manager:
        return jsonify({"error": "Reminder system not available"}), 503
    
    reminders = reminder_manager.get_all()
    return jsonify({
        "reminders": [r.to_dict() for r in reminders],
        "count": len(reminders)
    })


@app.route("/reminders/triggered")
def get_triggered_reminders():
    """Get triggered reminders (for notifications)."""
    if not REMINDERS_OK or not reminder_manager:
        return jsonify({"triggered": []})
    
    triggered = reminder_manager.get_triggered()
    return jsonify({
        "triggered": [r.to_dict() for r in triggered]
    })


@app.route("/reminders/add", methods=["POST"])
def add_reminder():
    """Add a new reminder via API."""
    if not REMINDERS_OK or not reminder_manager:
        return jsonify({"error": "Reminder system not available"}), 503
    
    data = request.get_json(silent=True)
    if not data:
        return jsonify({"error": "No data provided"}), 400
    
    message = data.get("message", "Reminder")
    minutes = data.get("minutes", 0)
    hours = data.get("hours", 0)
    seconds = data.get("seconds", 0)
    
    try:
        reminder = reminder_manager.add_relative(
            message=message,
            minutes=minutes,
            hours=hours,
            seconds=seconds
        )
        return jsonify({
            "success": True,
            "reminder": reminder.to_dict()
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/reminders/delete/<reminder_id>", methods=["DELETE"])
def delete_reminder(reminder_id):
    """Delete a reminder."""
    if not REMINDERS_OK or not reminder_manager:
        return jsonify({"error": "Reminder system not available"}), 503
    
    if reminder_manager.delete(reminder_id):
        return jsonify({"success": True})
    return jsonify({"error": "Reminder not found"}), 404


@app.route("/reminders/clear", methods=["POST"])
def clear_reminders():
    """Clear all reminders."""
    if not REMINDERS_OK or not reminder_manager:
        return jsonify({"error": "Reminder system not available"}), 503
    
    count = reminder_manager.clear_all()
    return jsonify({"success": True, "deleted": count})


# ===========================================
# MAIN AI COMMAND ENDPOINT
# ===========================================

@app.route("/ai-command", methods=["POST"])
def ai_command():
    """
    Main command endpoint.
    Handles all commands - desktop, conversation, reminders, etc.
    """
    try:
        data = request.get_json(silent=True)
        
        if not data or "command" not in data:
            return jsonify({"error": "No command provided"}), 400
        
        user_input = data["command"].strip()
        
        if not user_input:
            return jsonify({"error": "Empty command"}), 400
        
        text = user_input.lower()
        
        # ===========================================
        # TRY DESKTOP AUTOMATION FIRST
        # ===========================================
        if DESKTOP_OK and desktop_execute:
            try:
                success, response = desktop_execute(user_input)
                
                # If desktop handled it successfully
                if success:
                    return jsonify({
                        "reply": response,
                        "response": response,
                        "speech": response,
                        "action": "desktop",
                        "success": True,
                        "source": "desktop"
                    })
            except Exception as e:
                print(f"Desktop execution error: {e}")
        
        # ===========================================
        # FAST GREETINGS (No AI needed)
        # ===========================================
        if text in ["hi", "hello", "hey", "hii", "hello there"]:
            hour = datetime.datetime.now().hour
            if hour < 12:
                greet = "Good morning"
            elif hour < 18:
                greet = "Good afternoon"
            else:
                greet = "Good evening"
            
            reply = f"{greet}! I'm ARES. How can I help you?"
            return jsonify({
                "reply": reply,
                "response": reply,
                "speech": reply,
                "source": "fast"
            })
        
        # ===========================================
        # AI BRAIN FOR CONVERSATION
        # ===========================================
        if brain:
            try:
                response = brain.converse(user_input)
                if response:
                    return jsonify({
                        "reply": response,
                        "response": response,
                        "speech": response,
                        "source": "ai"
                    })
            except Exception as e:
                print(f"AI Brain error: {e}")
        
        # ===========================================
        # FALLBACK
        # ===========================================
        return jsonify({
            "reply": f"I heard: '{user_input}'. Try asking 'help' to see what I can do.",
            "response": f"Command received: {user_input}",
            "speech": "I'm not sure how to help with that.",
            "source": "fallback"
        })
    
    except Exception as e:
        print(f"? Error in /ai-command: {e}")
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500


# ===========================================
# VOICE RECOGNITION ROUTES
# ===========================================

@app.route("/voice/status")
def voice_status():
    """Voice recognition status."""
    return jsonify({
        "available": WHISPER_OK,
        "model": "base" if WHISPER_OK else None
    })


@app.route("/voice/transcribe", methods=["POST"])
def voice_transcribe():
    """
    Transcribe audio to text using Whisper.
    Accepts: audio file, base64, or raw bytes.
    """
    if not WHISPER_OK:
        return jsonify({"error": "Whisper not available"}), 503
    
    try:
        temp_path = None
        
        # Handle different input formats
        if request.files and 'audio' in request.files:
            # File upload
            audio_file = request.files['audio']
            temp_path = tempfile.mktemp(suffix=".wav")
            audio_file.save(temp_path)
        
        elif request.is_json:
            data = request.get_json()
            
            if 'audio_base64' in data:
                # Base64 encoded audio
                audio_bytes = base64.b64decode(data['audio_base64'])
                temp_path = tempfile.mktemp(suffix=".wav")
                with open(temp_path, 'wb') as f:
                    f.write(audio_bytes)
        
        else:
            # Raw bytes
            audio_bytes = request.data
            if audio_bytes:
                temp_path = tempfile.mktemp(suffix=".wav")
                with open(temp_path, 'wb') as f:
                    f.write(audio_bytes)
        
        if not temp_path or not os.path.exists(temp_path):
            return jsonify({"error": "No audio data provided"}), 400
        
        # Transcribe with Whisper
        segments, info = whisper_model.transcribe(
            temp_path,
            language="en",
            beam_size=5,
            vad_filter=True
        )
        
        text = " ".join([seg.text for seg in segments]).strip()
        
        # Cleanup
        if temp_path and os.path.exists(temp_path):
            os.unlink(temp_path)
        
        return jsonify({
            "success": True,
            "text": text,
            "language": info.language if info else "en"
        })
    
    except Exception as e:
        print(f"? Transcription error: {e}")
        traceback.print_exc()
        if temp_path and os.path.exists(temp_path):
            os.unlink(temp_path)
        return jsonify({"error": str(e)}), 500


# ===========================================
# MEMORY ROUTES
# ===========================================

@app.route("/memory/profile")
def memory_profile():
    """Get user profile and memory info"""
    if not brain:
        return jsonify({"error": "AI Brain not available"}), 503
    
    try:
        profile_data = brain.profile.get_full_profile()
        memory_export = brain.memory.export_memory()
        
        return jsonify({
            "profile": profile_data.get("user", {}),
            "preferences": memory_export.get("preferences", {}),
            "facts": memory_export.get("facts", [])
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/memory/conversations")
def memory_conversations():
    """Get conversation history"""
    if not brain:
        return jsonify({"error": "AI Brain not available"}), 503
    
    try:
        limit = int(request.args.get("limit", 10))
        conversations = brain.memory.get_recent_conversations(limit)
        return jsonify({"conversations": conversations})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/memory/clear-conversations", methods=["POST"])
def memory_clear_conversations():
    """Clear conversation history"""
    if not brain:
        return jsonify({"error": "AI Brain not available"}), 503
    
    try:
        brain.memory.clear_conversations()
        return jsonify({"success": True})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/memory/clear-all", methods=["POST"])
def memory_clear_all():
    """Clear ALL memory"""
    if not brain:
        return jsonify({"error": "AI Brain not available"}), 503
    
    try:
        brain.memory.clear_all_memory()
        return jsonify({"success": True})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/memory/export")
def memory_export():
    """Export all memory"""
    if not brain:
        return jsonify({"error": "AI Brain not available"}), 503
    
    try:
        memory_data = brain.memory.export_memory()
        profile_data = brain.profile.get_full_profile()
        
        return jsonify({
            "memory": memory_data,
            "profile": profile_data,
            "exported_at": datetime.datetime.now().isoformat()
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500


# ===========================================
# STATIC FILES
# ===========================================

@app.route("/static/<path:filename>")
def serve_static(filename):
    """Serve static files."""
    return send_from_directory(app.static_folder, filename)


# ===========================================
# MAIN
# ===========================================

if __name__ == "__main__":
    print_startup()
    app.run(host="127.0.0.1", port=5000, debug=True)
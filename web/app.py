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

# Desktop Controller
try:
    from desktop import handle_command as desktop_handle
    from desktop import desktop
    DESKTOP_OK = True
    print("? Desktop automation loaded")
except Exception as e:
    DESKTOP_OK = False
    desktop = None
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
except Exception as e:
    reminder_manager = None
    REMINDERS_OK = False
    print(f"? Reminders not available: {e}")


# ===========================================
# BASIC ROUTES
# ===========================================

@app.route("/")
def index():
    """Main ARES UI."""
    return render_template("index.html")


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


@app.route("/tasks")
def tasks():
    """Available tasks."""
    return jsonify([
        {"name": "TEST_TASK"},
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
    Handles all commands - desktop, conversation, etc.
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
        if DESKTOP_OK:
            result = desktop_handle(user_input)
            
            # If desktop handled it successfully
            if result.get("success") or result.get("action") not in ["unknown", "conversation", None]:
                return jsonify({
                    "reply": result.get("response", "Done."),
                    "action": result.get("action"),
                    "data": result.get("data"),
                    "source": "desktop"
                })
        
        # ===========================================
        # FAST GREETINGS (No AI needed)
        # ===========================================
        if text in ["hi", "hello", "hey", "hii"]:
            hour = datetime.datetime.now().hour
            if hour < 12:
                greet = "Good morning"
            elif hour < 18:
                greet = "Good afternoon"
            else:
                greet = "Good evening"
            
            reply = f"{greet}, Shobutik! I'm ARES. How can I help you?"
            return jsonify({
                "reply": reply,
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
                        "source": "ai"
                    })
            except Exception as e:
                print(f"AI Brain error: {e}")
        
        # ===========================================
        # FALLBACK
        # ===========================================
        return jsonify({
            "reply": f"I heard: '{user_input}'. Try asking for 'help' to see what I can do.",
            "source": "fallback"
        })
    
    except Exception as e:
        print(f"? Error in /ai-command: {e}")
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500


# ===========================================
# DESKTOP AUTOMATION ROUTES
# ===========================================

@app.route("/desktop/status")
def desktop_status():
    """Desktop automation status."""
    if DESKTOP_OK and desktop:
        return jsonify(desktop.get_status())
    return jsonify({"available": False})


@app.route("/desktop/action", methods=["POST"])
def desktop_action():
    """Execute a specific desktop action."""
    if not DESKTOP_OK:
        return jsonify({"error": "Desktop automation not available"}), 503
    
    try:
        data = request.get_json()
        action = data.get("action")
        params = data.get("params", {})
        
        # Map actions to methods
        actions = {
            "open_app": lambda: desktop.open_app(params.get("app", "")),
            "close_app": lambda: desktop.close_app(params.get("app", "")),
            "open_folder": lambda: desktop.open_folder(params.get("folder", "")),
            "search_google": lambda: desktop.search_google(params.get("query", "")),
            "search_youtube": lambda: desktop.search_youtube(params.get("query", "")),
            "open_website": lambda: desktop.open_website(params.get("url", "")),
            "screenshot": lambda: desktop.take_screenshot(),
            "volume_up": lambda: desktop.volume_up(),
            "volume_down": lambda: desktop.volume_down(),
            "mute": lambda: desktop.mute(),
            "play_pause": lambda: desktop.play_pause(),
            "next_track": lambda: desktop.next_track(),
            "previous_track": lambda: desktop.previous_track(),
            "minimize_all": lambda: desktop.minimize_all(),
            "lock": lambda: desktop.lock_computer(),
            "time": lambda: (True, f"The time is {desktop.get_time()}"),
            "date": lambda: (True, f"Today is {desktop.get_date()}"),
            "battery": lambda: (True, desktop.get_battery()),
        }
        
        if action not in actions:
            return jsonify({"error": f"Unknown action: {action}"}), 400
        
        success, response = actions[action]()
        return jsonify({
            "success": success,
            "response": response,
            "action": action
        })
    
    except Exception as e:
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
# SYSTEM INFO ROUTES
# ===========================================

@app.route("/system/info")
def system_info():
    """Get system information."""
    if DESKTOP_OK and desktop:
        return jsonify(desktop.get_system_info())
    return jsonify({"error": "Desktop not available"}), 503


@app.route("/system/apps")
def running_apps():
    """Get running applications."""
    if DESKTOP_OK and desktop:
        return jsonify({"apps": desktop.list_running_apps()})
    return jsonify({"error": "Desktop not available"}), 503


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
    print("\n" + "=" * 50)
    print("   ARES - Autonomous Runtime AI Agent")
    print("=" * 50)
    print(f"   AI Brain:    {'?' if brain else '?'}")
    print(f"   Desktop:     {'?' if DESKTOP_OK else '?'}")
    print(f"   Whisper:     {'?' if WHISPER_OK else '?'}")
    print("=" * 50)
    print("   Open: http://127.0.0.1:5000")
    print("=" * 50 + "\n")
    
    app.run(host="127.0.0.1", port=5000, debug=True)
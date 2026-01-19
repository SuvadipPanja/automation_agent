"""
=====================================================
ARES - AUTONOMOUS RUNTIME AI AGENT
=====================================================
UNIFIED WEB APPLICATION - EVERYTHING IN ONE PLACE!

Just run: python main_web.py
Open: http://127.0.0.1:5000

Features:
? Web UI (JARVIS-style)
? Voice Recognition (Whisper)
? AI Brain (Ollama/Llama3)
? Desktop Automation
? Text-to-Speech

Author: ARES AI Assistant
For: Shobutik Panja
=====================================================
"""

from flask import Flask, render_template, request, jsonify
from pathlib import Path
import datetime
import traceback
import sys
import os
import base64
import tempfile

# -------------------------------
# PATH SETUP
# -------------------------------
BASE_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = BASE_DIR.parent
sys.path.insert(0, str(PROJECT_ROOT))

# -------------------------------
# FLASK APP
# -------------------------------
app = Flask(
    __name__,
    template_folder=str(BASE_DIR / "templates"),
    static_folder=str(BASE_DIR / "static")
)

print()
print("=" * 60)
print("  ?? ARES - Autonomous Runtime AI Agent")
print("=" * 60)
print()

# =====================================================
# COMPONENT LOADING
# =====================================================

# --- AI BRAIN ---
brain = None
try:
    from ai.brain import AIBrain
    brain = AIBrain()
    print("  ? AI Brain loaded (Ollama/Llama3)")
except Exception as e:
    print(f"  ??  AI Brain not available: {e}")

# --- WHISPER (Speech Recognition) ---
whisper_model = None
WHISPER_AVAILABLE = False

try:
    from faster_whisper import WhisperModel
    WHISPER_AVAILABLE = True
    print("  ? Whisper available (loads on first use)")
except ImportError:
    print("  ??  Whisper not installed: pip install faster-whisper")

def get_whisper():
    """Lazy load Whisper model on first use."""
    global whisper_model
    if whisper_model is None and WHISPER_AVAILABLE:
        print("  ?? Loading Whisper model (first time)...")
        try:
            whisper_model = WhisperModel("base", device="cpu", compute_type="int8")
            print("  ? Whisper model loaded!")
        except Exception as e:
            print(f"  ? Whisper failed: {e}")
    return whisper_model

# --- DESKTOP AUTOMATION ---
desktop = None
command_parser = None
CommandType = None
CommandExecutor = None
DESKTOP_AVAILABLE = False

try:
    import pyautogui
    import psutil
    pyautogui.FAILSAFE = True
    pyautogui.PAUSE = 0.1
    DESKTOP_AVAILABLE = True
    print("  ? Desktop automation available (pyautogui)")
except ImportError:
    print("  ??  Desktop not installed: pip install pyautogui psutil")

try:
    from automation.desktop_control import DesktopAutomation
    from automation.command_parser import CommandParser, CommandExecutor as CmdExec, CommandType as CmdType
    desktop = DesktopAutomation()
    command_parser = CommandParser()
    CommandType = CmdType
    CommandExecutor = CmdExec
    print("  ? Desktop automation modules loaded")
except Exception as e:
    print(f"  ??  Desktop modules not found: {e}")

print()
print("=" * 60)

# =====================================================
# PAGE ROUTES
# =====================================================

@app.route("/")
def index():
    """Main JARVIS-style UI"""
    return render_template("index_modern.html")

@app.route("/classic")
def classic():
    """Classic minimal UI"""
    try:
        return render_template("index.html")
    except:
        return render_template("index_modern.html")

@app.route("/voicetest")
def voice_test():
    """Voice test page"""
    try:
        return render_template("voice_test.html")
    except:
        return "<h1>Voice Test</h1><p>Test page not available</p>"

@app.route("/memory")
def memory_page():
    """Memory management page"""
    try:
        return render_template("memory.html")
    except:
        return "<h1>Memory</h1><p>Memory page not available</p>"

# =====================================================
# SYSTEM STATUS
# =====================================================

@app.route("/health")
def health():
    """Quick health check."""
    return jsonify({
        "agent": "ARES",
        "status": "ONLINE",
        "time": datetime.datetime.now().isoformat()
    })

@app.route("/status")
def status():
    """Detailed system status."""
    user_name = "Unknown"
    try:
        user_name = os.getlogin() if os.name == 'nt' else os.environ.get('USER', 'user')
    except:
        pass
    
    status_info = {
        "agent": "ARES",
        "version": "2.0",
        "status": "ONLINE",
        "time": datetime.datetime.now().isoformat(),
        "user": user_name,
        "features": {
            "ai_brain": brain is not None,
            "whisper_available": WHISPER_AVAILABLE,
            "whisper_loaded": whisper_model is not None,
            "desktop_automation": DESKTOP_AVAILABLE,
            "desktop_loaded": desktop is not None
        }
    }
    
    # Add system info
    if desktop:
        try:
            status_info["system"] = desktop.get_system_info()
            status_info["battery"] = desktop.get_battery_status()
        except:
            pass
    
    return jsonify(status_info)

@app.route("/tasks")
def tasks():
    return jsonify([
        {"name": "TEST_TASK"},
        {"name": "DESKTOP_CONTROL"},
        {"name": "VOICE_ASSISTANT"}
    ])

@app.route("/schedules")
def schedules():
    return jsonify([
        {"enabled": True, "task": "TEST_TASK", "time": "11:15", "type": "daily"}
    ])

@app.route("/reload-schedules", methods=["POST"])
def reload_schedules():
    return jsonify({"status": "Schedules reloaded"})

# =====================================================
# VOICE ROUTES (Whisper Transcription)
# =====================================================

@app.route("/voice/status")
def voice_status():
    """Check voice system status."""
    return jsonify({
        "whisper_available": WHISPER_AVAILABLE,
        "whisper_loaded": whisper_model is not None,
        "model": "base" if WHISPER_AVAILABLE else None
    })

@app.route("/voice/transcribe", methods=["POST"])
def voice_transcribe():
    """Transcribe audio using Whisper."""
    if not WHISPER_AVAILABLE:
        return jsonify({
            "error": "Whisper not installed",
            "hint": "Run: pip install faster-whisper"
        }), 503
    
    # Get Whisper model
    whisper = get_whisper()
    if not whisper:
        return jsonify({"error": "Failed to load Whisper model"}), 500
    
    language = request.args.get("language", "en")
    
    try:
        audio_data = None
        
        # Check for file upload
        if 'audio' in request.files:
            audio_file = request.files['audio']
            audio_data = audio_file.read()
        
        # Check for base64 audio
        elif request.is_json:
            data = request.get_json()
            if data and 'audio' in data:
                audio_b64 = data['audio']
                if ',' in audio_b64:
                    audio_b64 = audio_b64.split(',')[1]
                audio_data = base64.b64decode(audio_b64)
        
        # Check for raw bytes
        elif request.data:
            audio_data = request.data
        
        if not audio_data:
            return jsonify({"error": "No audio data provided"}), 400
        
        # Save to temp file
        with tempfile.NamedTemporaryFile(suffix=".webm", delete=False) as f:
            f.write(audio_data)
            temp_path = f.name
        
        try:
            # Transcribe
            segments, info = whisper.transcribe(
                temp_path,
                language=language,
                beam_size=5,
                vad_filter=True
            )
            
            text = " ".join([seg.text for seg in segments]).strip()
            
            return jsonify({
                "text": text,
                "language": info.language,
                "duration": info.duration
            })
            
        finally:
            # Clean up
            try:
                os.unlink(temp_path)
            except:
                pass
    
    except Exception as e:
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500

# =====================================================
# DESKTOP AUTOMATION ROUTES
# =====================================================

@app.route("/desktop/execute", methods=["POST"])
def desktop_execute():
    """Execute a desktop command directly."""
    if not DESKTOP_AVAILABLE or not desktop:
        return jsonify({
            "success": False,
            "error": "Desktop automation not available"
        }), 503
    
    data = request.get_json(silent=True)
    if not data or "command" not in data:
        return jsonify({"success": False, "error": "No command"}), 400
    
    command = data["command"]
    
    try:
        if CommandExecutor:
            executor = CommandExecutor()
            success, response = executor.execute(command)
        else:
            success, response = False, "Parser not available"
        
        return jsonify({
            "success": success,
            "response": response
        })
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@app.route("/desktop/info")
def desktop_info():
    """Get system information."""
    if not desktop:
        return jsonify({"error": "Desktop not available"}), 503
    
    return jsonify({
        "time": desktop.get_time(),
        "date": desktop.get_date(),
        "battery": desktop.get_battery_status(),
        "system": desktop.get_system_info()
    })

# =====================================================
# MEMORY ROUTES
# =====================================================

@app.route("/memory/profile", methods=["GET"])
def get_memory_profile():
    if not brain or not hasattr(brain, 'memory') or not brain.memory:
        return jsonify({"error": "Memory not available"}), 500
    
    return jsonify({
        "profile": brain.memory.get_full_profile(),
        "preferences": brain.memory.get_preferences(),
        "facts": brain.memory.get_facts(limit=10)
    })

@app.route("/memory/set-info", methods=["POST"])
def set_user_info():
    if not brain or not hasattr(brain, 'memory') or not brain.memory:
        return jsonify({"error": "Memory not available"}), 500
    
    data = request.get_json(silent=True)
    if not data or "key" not in data or "value" not in data:
        return jsonify({"error": "Missing key or value"}), 400
    
    brain.memory.set_user_info(data["key"], data["value"])
    
    if data["key"] == "name":
        brain.user_name = data["value"]
    
    return jsonify({"status": "Saved"})

# =====================================================
# MAIN AI COMMAND ENDPOINT
# =====================================================
# This is the UNIFIED endpoint that handles EVERYTHING:
# - Desktop commands (open app, screenshot, etc.)
# - Information queries (time, battery, etc.)
# - Conversation (AI chat)
# =====================================================

@app.route("/ai-command", methods=["POST"])
def ai_command():
    """
    UNIFIED COMMAND ENDPOINT
    
    Handles ALL user commands:
    1. Desktop automation (open, close, screenshot, etc.)
    2. System queries (time, date, battery)
    3. AI conversation
    """
    try:
        data = request.get_json(silent=True)
        
        if not data or "command" not in data:
            return jsonify({"error": "No command provided"}), 400
        
        user_input = data["command"].strip()
        
        if not user_input:
            return jsonify({"error": "Empty command"}), 400
        
        text_lower = user_input.lower()
        
        # =========================================
        # STEP 1: Check for Desktop Commands
        # =========================================
        if command_parser and desktop and CommandType and CommandExecutor:
            parsed = command_parser.parse(user_input)
            
            # List of desktop command types
            desktop_commands = [
                CommandType.OPEN_APP, CommandType.CLOSE_APP,
                CommandType.SEARCH_GOOGLE, CommandType.SEARCH_YOUTUBE,
                CommandType.OPEN_WEBSITE, CommandType.OPEN_FOLDER,
                CommandType.TAKE_SCREENSHOT,
                CommandType.MINIMIZE_WINDOW, CommandType.MAXIMIZE_WINDOW,
                CommandType.CLOSE_WINDOW, CommandType.MINIMIZE_ALL, 
                CommandType.SWITCH_WINDOW,
                CommandType.LOCK_COMPUTER,
                CommandType.VOLUME_UP, CommandType.VOLUME_DOWN, CommandType.MUTE,
                CommandType.PLAY_PAUSE, CommandType.NEXT_TRACK, CommandType.PREVIOUS_TRACK,
                CommandType.TYPE_TEXT, CommandType.COPY, CommandType.PASTE,
                CommandType.SAVE, CommandType.UNDO, CommandType.REDO, CommandType.SELECT_ALL,
                CommandType.GET_TIME, CommandType.GET_DATE, CommandType.GET_BATTERY,
                CommandType.GET_SYSTEM_INFO, CommandType.LIST_RUNNING_APPS,
                CommandType.HELP
            ]
            
            if parsed.command_type in desktop_commands:
                # Execute desktop command
                executor = CommandExecutor()
                success, response = executor.execute(user_input)
                
                return jsonify({
                    "reply": response,
                    "speech": response,
                    "type": "desktop",
                    "success": success
                })
        
        # =========================================
        # STEP 2: Fast Greetings
        # =========================================
        if text_lower in ["hi", "hello", "hey", "hii", "hola"]:
            hour = datetime.datetime.now().hour
            if hour < 12:
                greet = "Good morning"
            elif hour < 18:
                greet = "Good afternoon"
            else:
                greet = "Good evening"
            
            user_name = "Shobutik"
            if brain and hasattr(brain, 'user_name') and brain.user_name:
                user_name = brain.user_name
            
            reply = f"{greet}, {user_name}! I am ARES. How can I help you?"
            return jsonify({
                "reply": reply,
                "speech": reply,
                "type": "greeting"
            })
        
        # Identity questions
        if text_lower in ["who are you", "your name", "what are you"]:
            features = []
            if brain: features.append("AI conversation")
            if DESKTOP_AVAILABLE: features.append("desktop control")
            if WHISPER_AVAILABLE: features.append("voice recognition")
            
            reply = f"I am ARES - Autonomous Runtime AI Agent. I can help you with {', '.join(features)}!"
            return jsonify({
                "reply": reply,
                "speech": reply,
                "type": "introduction"
            })
        
        # =========================================
        # STEP 3: AI Brain for Conversation
        # =========================================
        if brain:
            plan = brain.think(user_input)
            
            if isinstance(plan, dict):
                intent = plan.get("intent", "UNKNOWN")
                
                # Pre-built reply
                if intent == "CHAT" and plan.get("reply"):
                    return jsonify({
                        "reply": plan.get("reply"),
                        "speech": plan.get("reply"),
                        "type": "chat"
                    })
                
                # Status query
                elif intent == "STATUS":
                    reply = f"System Status:\n\n"
                    reply += f" AI Brain: {'? Online' if brain else '? Offline'}\n"
                    reply += f" Whisper: {'? Available' if WHISPER_AVAILABLE else '? Not installed'}\n"
                    reply += f" Desktop: {'? Ready' if DESKTOP_AVAILABLE else '? Not installed'}\n"
                    reply += f" Status: ONLINE"
                    return jsonify({
                        "reply": reply,
                        "speech": "All systems operational.",
                        "type": "status"
                    })
                
                # Capabilities
                elif intent == "CAPABILITIES":
                    reply = "I can help you with:\n\n"
                    reply += "??? Desktop Control - Open apps, screenshots, volume\n"
                    reply += "?? Web Search - Google, YouTube\n"
                    reply += "?? Files - Open folders\n"
                    reply += "?? Conversation - Chat with me\n"
                    reply += "?? Voice - Speak commands"
                    return jsonify({
                        "reply": reply,
                        "speech": "I can control your desktop, search the web, and chat with you.",
                        "type": "capabilities"
                    })
                
                # General conversation
                else:
                    response_text = brain.converse(user_input)
                    return jsonify({
                        "reply": response_text,
                        "speech": response_text,
                        "type": "conversation"
                    })
            
            # Plan is not dict, use conversation
            else:
                response_text = brain.converse(user_input)
                return jsonify({
                    "reply": response_text,
                    "speech": response_text,
                    "type": "conversation"
                })
        
        # =========================================
        # STEP 4: Fallback (No AI Brain)
        # =========================================
        return jsonify({
            "reply": f"Received: {user_input}\n\nAI Brain not available. Make sure Ollama is running.",
            "speech": "Command received, but AI is not available.",
            "type": "fallback"
        })
    
    except Exception as e:
        print("?? Error in /ai-command:")
        traceback.print_exc()
        return jsonify({
            "error": str(e),
            "reply": f"Error: {str(e)}",
            "type": "error"
        }), 500


# =====================================================
# STARTUP
# =====================================================

def print_startup():
    print()
    print("  ?? Open: http://127.0.0.1:5000")
    print()
    print("  Commands:")
    print("     'Open Chrome'")
    print("     'Search Google for Python'")
    print("     'Take a screenshot'")
    print("     'What time is it?'")
    print("     'Volume up'")
    print()
    print("=" * 60)
    print("  ?? ARES is ready!")
    print("=" * 60)
    print()


if __name__ == "__main__":
    print_startup()
    app.run(host="127.0.0.1", port=5000, debug=True)
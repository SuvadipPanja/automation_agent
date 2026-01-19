from flask import Flask, render_template, request, jsonify
from pathlib import Path
import datetime
import traceback
import sys

# -------------------------------
# FIX PYTHON PATH FOR IMPORTS
# -------------------------------
# Add parent directory to path so we can import 'ai' module
BASE_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = BASE_DIR.parent
sys.path.insert(0, str(PROJECT_ROOT))

# -------------------------------
# APP SETUP (VERY IMPORTANT)
# -------------------------------
app = Flask(
    __name__,
    template_folder=str(BASE_DIR / "templates"),
    static_folder=str(BASE_DIR / "static")
)

# -------------------------------
# SAFE AI BRAIN IMPORT
# -------------------------------
try:
    from ai.brain import AIBrain
    brain = AIBrain()
    print("? AI Brain loaded successfully")
except Exception as e:
    brain = None
    print("? AI Brain not loaded:", e)
    print("   Make sure 'ai' folder exists in project root")
    print("   Make sure 'ai/__init__.py' exists")
    print("   ARES will work with limited responses")

# -------------------------------
# VOICE ASSISTANT SETUP
# -------------------------------
try:
    from web.voice_routes import voice_bp
    app.register_blueprint(voice_bp)
    print("? Voice Assistant routes registered")
except Exception as e:
    print("? Voice Assistant not available:", e)
    print("   Voice features will use browser-based speech only")

# -------------------------------
# ROUTES
# -------------------------------

@app.route("/")
def index():
    """Serve the modern JARVIS-style UI"""
    return render_template("index_modern.html")

@app.route("/classic")
def classic():
    """Serve the classic minimal UI"""
    return render_template("index.html")

@app.route("/voicetest")
def voice_test():
    """Simple voice test page for debugging"""
    return render_template("voice_test.html")


@app.route("/memory")
def memory_page():
    """ARES Memory & Profile Management page"""
    return render_template("memory.html")


@app.route("/health")
def health():
    return jsonify({
        "agent": "ARES",
        "status": "ONLINE",
        "time": datetime.datetime.now().isoformat()
    })


@app.route("/tasks")
def tasks():
    return jsonify([
        {"name": "TEST_TASK"},
        {"name": "EMAIL_READ"},
        {"name": "BROWSER_AUTOMATION"}
    ])


@app.route("/schedules")
def schedules():
    return jsonify([
        {
            "enabled": True,
            "task": "TEST_TASK",
            "time": "11:15",
            "type": "daily"
        }
    ])


@app.route("/reload-schedules", methods=["POST"])
def reload_schedules():
    return jsonify({"status": "Schedules reloaded successfully"})


# -------------------------------
# MEMORY MANAGEMENT ROUTES
# -------------------------------
@app.route("/memory/profile", methods=["GET"])
def get_memory_profile():
    """Get user profile from memory."""
    if not brain or not brain.memory:
        return jsonify({"error": "Memory system not available"}), 500
    
    profile = brain.memory.get_full_profile()
    preferences = brain.memory.get_preferences()
    facts = brain.memory.get_facts(limit=10)
    
    return jsonify({
        "profile": profile,
        "preferences": preferences,
        "facts": facts
    })


@app.route("/memory/conversations", methods=["GET"])
def get_conversations():
    """Get recent conversation history."""
    if not brain or not brain.memory:
        return jsonify({"error": "Memory system not available"}), 500
    
    limit = request.args.get('limit', 20, type=int)
    conversations = brain.memory.get_recent_conversations(limit=limit)
    
    return jsonify({"conversations": conversations})


@app.route("/memory/clear-conversations", methods=["POST"])
def clear_conversations():
    """Clear conversation history but keep profile."""
    if not brain or not brain.memory:
        return jsonify({"error": "Memory system not available"}), 500
    
    brain.memory.clear_conversations()
    return jsonify({"status": "Conversations cleared successfully"})


@app.route("/memory/clear-all", methods=["POST"])
def clear_all_memory():
    """Clear ALL memory (reset everything)."""
    if not brain or not brain.memory:
        return jsonify({"error": "Memory system not available"}), 500
    
    brain.memory.clear_all_memory()
    return jsonify({"status": "All memory cleared successfully"})


@app.route("/memory/export", methods=["GET"])
def export_memory():
    """Export all memory data."""
    if not brain or not brain.memory:
        return jsonify({"error": "Memory system not available"}), 500
    
    memory_data = brain.memory.export_memory()
    return jsonify(memory_data)


@app.route("/memory/set-info", methods=["POST"])
def set_user_info():
    """Manually set user information."""
    if not brain or not brain.memory:
        return jsonify({"error": "Memory system not available"}), 500
    
    data = request.get_json(silent=True)
    if not data or "key" not in data or "value" not in data:
        return jsonify({"error": "Missing key or value"}), 400
    
    brain.memory.set_user_info(data["key"], data["value"])
    
    # Update brain's cached name if setting name
    if data["key"] == "name":
        brain.user_name = data["value"]
    
    return jsonify({"status": "User info saved successfully"})


# -------------------------------
# AI COMMAND (MAIN LOGIC)
# -------------------------------
@app.route("/ai-command", methods=["POST"])
def ai_command():
    try:
        data = request.get_json(silent=True)

        if not data or "command" not in data:
            return jsonify({"error": "No command provided"}), 400

        user_input = data["command"].strip()

        if not user_input:
            return jsonify({"error": "Empty command"}), 400

        text = user_input.lower()

        # -------------------------------
        # FAST CONVERSATION LAYER
        # -------------------------------
        if text in ["hi", "hello", "hey"]:
            hour = datetime.datetime.now().hour
            if hour < 12:
                greet = "Good morning"
            elif hour < 18:
                greet = "Good afternoon"
            else:
                greet = "Good evening"

            reply = f"{greet}. I am ARES, your autonomous AI agent. How can I assist you today?"
            return jsonify({
                "reply": reply,
                "speech": reply
            })

        if text in ["who are you", "your name", "what are you"]:
            reply = "I am ARES - Autonomous Runtime AI Agent. I'm here to help you with automation, tasks, and intelligent assistance."
            return jsonify({
                "reply": reply,
                "speech": reply
            })

        # -------------------------------
        # AI BRAIN (LLAMA / OLLAMA)
        # -------------------------------
        if brain:
            # First, classify the intent
            plan = brain.think(user_input)

            # Handle different intents
            if isinstance(plan, dict):
                intent = plan.get("intent", "UNKNOWN")
                
                # For CHAT intent with a pre-built reply, use it directly
                if intent == "CHAT" and plan.get("reply"):
                    response_text = plan.get("reply")
                    return jsonify({
                        "reply": response_text,
                        "speech": response_text
                    })
                
                # For CHAT intent without reply, use conversational AI
                elif intent == "CHAT":
                    response_text = brain.converse(user_input)
                    return jsonify({
                        "reply": response_text,
                        "speech": response_text
                    })
                
                # For STATUS queries, provide system status
                elif intent == "STATUS":
                    reply = f"System Status:\n\n" \
                            f" AI Model: Llama3 (Ollama)\n" \
                            f" Tasks Available: 3 (TEST_TASK, EMAIL_READ, BROWSER_AUTOMATION)\n" \
                            f" Active Schedules: 1\n" \
                            f" Status: ONLINE and operational"
                    return jsonify({
                        "reply": reply,
                        "speech": "System is fully operational with 3 tasks available and 1 active schedule."
                    })
                
                # For CAPABILITIES queries
                elif intent == "CAPABILITIES":
                    reply = "I can help you with:\n\n" \
                            " Natural Conversation - Chat naturally with me\n" \
                            " Task Automation - Execute scheduled and on-demand tasks\n" \
                            " System Monitoring - Track schedules and system health\n" \
                            " Voice Commands - Speak naturally to control ARES\n" \
                            " Information Retrieval - Answer questions and provide help"
                    return jsonify({
                        "reply": reply,
                        "speech": "I can help with conversations, task automation, system monitoring, and voice commands."
                    })
                
                # For RUN_TASK intent
                elif intent == "RUN_TASK":
                    task_name = plan.get("task")
                    if task_name:
                        reply = f"Task execution requested: {task_name}\n\n" \
                                f"Note: Task execution integration coming soon!"
                        return jsonify({
                            "reply": reply,
                            "speech": f"Task {task_name} execution requested."
                        })
                
                # For anything else, use conversational AI
                else:
                    response_text = brain.converse(user_input)
                    return jsonify({
                        "reply": response_text,
                        "speech": response_text
                    })
            
            # If plan is not a dict, convert to conversation
            else:
                response_text = brain.converse(user_input)
                return jsonify({
                    "reply": response_text,
                    "speech": response_text
                })

        # -------------------------------
        # FALLBACK (NO AI BRAIN)
        # -------------------------------
        return jsonify({
            "reply": f"Command received: {user_input}\n\nAI Brain is currently unavailable. Please ensure Ollama is running with the llama3 model.",
            "speech": "Command received. AI brain unavailable."
        })

    except Exception as e:
        print("? AI Command Error")
        traceback.print_exc()
        return jsonify({
            "error": str(e),
            "reply": f"An error occurred: {str(e)}"
        }), 500


# -------------------------------
# MAIN ENTRY
# -------------------------------
if __name__ == "__main__":
    print("=" * 50)
    print("  ARES - Autonomous Runtime AI Agent")
    print("=" * 50)
    print(f"  Modern UI: http://127.0.0.1:5000/")
    print(f"  Classic UI: http://127.0.0.1:5000/classic")
    print(f"  Voice Test: http://127.0.0.1:5000/voicetest")
    print("=" * 50)
    app.run(host="127.0.0.1", port=5000, debug=True)
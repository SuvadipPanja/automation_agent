from flask import Flask, render_template, request, jsonify
from pathlib import Path
import datetime
import traceback

# -------------------------------
# APP SETUP (VERY IMPORTANT)
# -------------------------------
BASE_DIR = Path(__file__).resolve().parent

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
except Exception as e:
    brain = None
    print("? AI Brain not loaded:", e)

# -------------------------------
# ROUTES
# -------------------------------

@app.route("/")
def index():
    return render_template("index.html")


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

            reply = f"{greet}. I am ARES. How can I help you?"
            return jsonify({
                "response": reply,
                "speech": reply
            })

        if text in ["who are you", "your name"]:
            reply = "I am ARES, your autonomous AI agent."
            return jsonify({
                "response": reply,
                "speech": reply
            })

        # -------------------------------
        # AI BRAIN (LLAMA / OLLAMA)
        # -------------------------------
        if brain:
            plan = brain.think(user_input)

            # If AI decides it's not an action, talk normally
            if isinstance(plan, dict) and plan.get("intent") == "CHAT":
                return jsonify({
                    "response": plan.get("response", "Okay."),
                    "speech": plan.get("response", "")
                })

            return jsonify({
                "response": plan,
                "speech": "Command understood. Processing."
            })

        # -------------------------------
        # FALLBACK (NO AI)
        # -------------------------------
        return jsonify({
            "response": f"Command received: {user_input}",
            "speech": "Command received."
        })

    except Exception as e:
        print("? AI Command Error")
        traceback.print_exc()
        return jsonify({
            "error": str(e)
        }), 500


# -------------------------------
# MAIN ENTRY
# -------------------------------
if __name__ == "__main__":
    app.run(debug=True)

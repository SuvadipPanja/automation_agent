"""
=====================================================
ARES - Main Web Entry Point
=====================================================

SINGLE ENTRY POINT FOR PRODUCTION

Usage:
    python main_web.py

This script:
1. Sets up project paths
2. Initializes ARES Manager (orchestrates all services)
3. Starts Flask web server
4. Handles graceful shutdown

Everything runs in the backend via the manager.
Frontend only sends commands via API endpoints.

Author: ARES Development
For: Suvadip Panja
=====================================================
"""

import os
import sys
import logging
from pathlib import Path
from typing import Optional

# ===================================================
# PROJECT STRUCTURE SETUP
# ===================================================

# Get project root
PROJECT_ROOT = Path(__file__).resolve().parent
print(f"\n📁 Project Root: {PROJECT_ROOT}")
print(f"🐍 Python Version: {sys.version.split()[0]}")

# Add to Python path
sys.path.insert(0, str(PROJECT_ROOT))
sys.path.insert(0, str(PROJECT_ROOT / "web"))
sys.path.insert(0, str(PROJECT_ROOT / "automation"))
sys.path.insert(0, str(PROJECT_ROOT / "ai"))

# Verify critical directories exist
required_dirs = [
    PROJECT_ROOT / "web",
    PROJECT_ROOT / "web" / "templates",
    PROJECT_ROOT / "web" / "static",
]

print("\n📂 Checking directory structure...")
for dir_path in required_dirs:
    if dir_path.exists():
        print(f"  ✅ {dir_path.name}")
    else:
        print(f"  ⚠️  {dir_path.name} - Not found")

# ===================================================
# ARES MANAGER INITIALIZATION
# ===================================================

print("\n🚀 Initializing ARES Manager...")
print("=" * 70)

from ares_manager import initialize_ares, get_manager

try:
    # Initialize all backend services
    ares = initialize_ares()
    print("✅ ARES Manager initialized successfully")
except Exception as e:
    print(f"❌ ARES Manager initialization failed: {e}")
    sys.exit(1)

# ===================================================
# FLASK APP SETUP
# ===================================================

print("\n" + "=" * 70)
print("🌐 Initializing Flask Web Server...")
print("=" * 70)

from flask import Flask, render_template, request, jsonify

# Create Flask app
app = Flask(
    __name__,
    template_folder=str(PROJECT_ROOT / "web" / "templates"),
    static_folder=str(PROJECT_ROOT / "web" / "static")
)

app.config['JSON_SORT_KEYS'] = False
app.config['MAX_CONTENT_LENGTH'] = 100 * 1024 * 1024  # 100MB max upload

print("✅ Flask app created")


# ===================================================
# API ROUTES - UNIFIED COMMAND INTERFACE
# ===================================================

@app.route("/")
def index():
    """Serve modern ARES UI."""
    return render_template("index_modern.html")


@app.route("/classic")
def index_classic():
    """Serve classic ARES UI."""
    return render_template("index.html")


@app.route("/health", methods=["GET"])
def health_check():
    """System health check."""
    manager = get_manager()
    status = manager.get_all_status()
    available_services = sum(1 for s in status.values() if s["available"])
    total_services = len(status)
    
    return jsonify({
        "status": "ONLINE",
        "agent": "ARES",
        "services_available": available_services,
        "services_total": total_services,
        "details": status
    })


@app.route("/status", methods=["GET"])
def status():
    """Get current system status."""
    manager = get_manager()
    status_info = manager.get_all_status()
    
    return jsonify({
        "online": True,
        "mode": "production",
        "user": "Suvadip Panja",
        "components": status_info,
        "all_ready": all(s["available"] for s in status_info.values())
    })


# ===================================================
# COMMAND EXECUTION - ALL COMMANDS ROUTE HERE
# ===================================================

@app.route("/command", methods=["POST"])
def execute_command_endpoint():
    """
    Universal command endpoint.
    
    All commands (voice, text, buttons) route here.
    Manager handles intelligent routing to appropriate service.
    
    Request: {"command": "user input"}
    Response: Command execution result
    """
    try:
        data = request.get_json(silent=True)
        if not data or "command" not in data:
            return jsonify({"error": "No command provided"}), 400
        
        command = data["command"].strip()
        if not command:
            return jsonify({"error": "Empty command"}), 400
        
        # Execute via manager
        manager = get_manager()
        result = manager.execute_command(command)
        
        return jsonify(result.to_dict())
    
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e),
            "action": "error"
        }), 500


# ===================================================
# LEGACY ENDPOINTS (For compatibility)
# ===================================================

@app.route("/ai-command", methods=["POST"])
def ai_command_legacy():
    """Legacy AI command endpoint - routes to new command endpoint."""
    return execute_command_endpoint()


@app.route("/direct-action", methods=["POST"])
def direct_action_legacy():
    """Legacy direct action endpoint - routes to new command endpoint."""
    return execute_command_endpoint()


# ===================================================
# SERVICE SPECIFIC ENDPOINTS
# ===================================================

@app.route("/tasks", methods=["GET"])
def get_tasks():
    """Get all tasks from task service."""
    manager = get_manager()
    tasks_service = manager.services.get("tasks")
    
    if not tasks_service or not tasks_service.initialized:
        return jsonify({"error": "Task system not available", "tasks": []}), 503
    
    tasks = tasks_service.get_all_tasks()
    return jsonify({
        "tasks": tasks,
        "count": len(tasks),
        "success": True
    })


@app.route("/schedules", methods=["GET"])
def get_schedules():
    """Get all schedules from scheduler service."""
    manager = get_manager()
    scheduler_service = manager.services.get("scheduler")
    
    if not scheduler_service or not scheduler_service.initialized:
        return jsonify({"error": "Scheduler not available", "schedules": []}), 503
    
    schedules = scheduler_service.get_all_schedules()
    return jsonify({
        "schedules": schedules,
        "count": len(schedules),
        "success": True
    })


@app.route("/reminders", methods=["GET"])
def get_reminders():
    """Get all reminders from reminder service."""
    manager = get_manager()
    reminder_service = manager.services.get("reminders")
    
    if not reminder_service or not reminder_service.initialized:
        return jsonify({"error": "Reminder system not available", "reminders": []}), 503
    
    reminders = reminder_service.get_all_reminders()
    return jsonify({
        "reminders": reminders,
        "count": len(reminders),
        "success": True
    })


# ===================================================
# VOICE TRANSCRIPTION ENDPOINT
# ===================================================

@app.route("/voice/transcribe", methods=["POST"])
def voice_transcribe():
    """Transcribe audio using voice service."""
    manager = get_manager()
    voice_service = manager.services.get("voice")
    
    if not voice_service or not voice_service.initialized:
        return jsonify({"error": "Voice service not available"}), 503
    
    try:
        import tempfile
        import base64
        
        # Get audio data
        if request.files and 'audio' in request.files:
            audio_file = request.files['audio']
            temp_path = tempfile.mktemp(suffix=".wav")
            audio_file.save(temp_path)
        elif request.is_json:
            data = request.get_json()
            if 'audio_base64' in data:
                audio_bytes = base64.b64decode(data['audio_base64'])
                temp_path = tempfile.mktemp(suffix=".wav")
                with open(temp_path, 'wb') as f:
                    f.write(audio_bytes)
            else:
                return jsonify({"error": "No audio data"}), 400
        else:
            return jsonify({"error": "No audio data"}), 400
        
        # Transcribe
        success, text = voice_service.transcribe(temp_path)
        
        if success:
            # Clean up temp file
            import os
            if os.path.exists(temp_path):
                os.unlink(temp_path)
            
            return jsonify({
                "success": True,
                "text": text,
                "language": "en"
            })
        else:
            return jsonify({"error": text}), 400
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500


# ===================================================
# ERROR HANDLERS
# ===================================================

@app.errorhandler(404)
def not_found(error):
    """Handle 404 errors."""
    return jsonify({
        "error": "Endpoint not found",
        "status": 404
    }), 404


@app.errorhandler(500)
def server_error(error):
    """Handle 500 errors."""
    return jsonify({
        "error": "Internal server error",
        "status": 500
    }), 500


# ===================================================
# STATIC FILES
# ===================================================

@app.route("/static/<path:filename>")
def serve_static(filename):
    """Serve static files."""
    from flask import send_from_directory
    return send_from_directory(app.static_folder, filename)


# ===================================================
# STARTUP AND SHUTDOWN
# ===================================================

def print_startup_info():
    """Print startup information."""
    import datetime
    
    manager = get_manager()
    
    print("\n" + "=" * 70)
    print("  ✅ ARES - FULLY INITIALIZED & ONLINE")
    print("=" * 70)
    print()
    print("  🌐 Web Interface:")
    print("     Modern UI: http://127.0.0.1:5000/")
    print("     Classic UI: http://127.0.0.1:5000/classic")
    print()
    print("  📊 API Endpoints:")
    print("     /command (POST)          - Execute any command")
    print("     /status (GET)            - System status")
    print("     /health (GET)            - Health check")
    print("     /tasks (GET)             - List all tasks")
    print("     /schedules (GET)         - List all schedules")
    print("     /reminders (GET)         - List all reminders")
    print("     /voice/transcribe (POST) - Voice transcription")
    print()
    print("  🔧 Server Configuration:")
    print(f"     Host: 127.0.0.1")
    print(f"     Port: 5000")
    print(f"     Debug: True")
    print(f"     Time: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    print("  📝 Usage:")
    print("     1. Open: http://127.0.0.1:5000/")
    print("     2. Click buttons or speak commands")
    print("     3. All requests route through /command endpoint")
    print("     4. Manager intelligently routes to appropriate service")
    print()
    print("=" * 70)
    print("  Press CTRL+C to stop server")
    print("=" * 70 + "\n")


if __name__ == "__main__":
    try:
        print_startup_info()
        
        # Start Flask development server
        app.run(
            host="127.0.0.1",
            port=5000,
            debug=True,
            use_reloader=False  # Disable reloader to avoid double initialization
        )
    
    except KeyboardInterrupt:
        print("\n\n⏹️  Shutting down ARES...")
        manager = get_manager()
        manager.shutdown()
        print("✅ ARES shutdown complete")
        sys.exit(0)
    
    except Exception as e:
        print(f"\n❌ Error: {e}")
        sys.exit(1)
"""
=====================================================
ARES - Autonomous Runtime AI Assistant
Web Backend (Flask) - ENHANCED WITH DIRECT AUTOMATION
=====================================================
Production-ready Flask application with:
- Direct automation endpoint for instant execution
- AI routing for conversations
- All components integrated

Author: ARES Development
For: Suvadip Panja
=====================================================
"""

import os
import sys
import json
import base64
import tempfile
import traceback
import datetime
from pathlib import Path
from typing import Dict, Any, Tuple

# ===================================================
# IMPORTS
# ===================================================
from flask import (
    Flask, render_template, request, jsonify, 
    send_from_directory, send_file
)

# Add project root to path
PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))


# ===================================================
# FLASK APP SETUP
# ===================================================
BASE_DIR = Path(__file__).resolve().parent

app = Flask(
    __name__,
    template_folder=str(BASE_DIR / "templates"),
    static_folder=str(BASE_DIR / "static")
)

# Flask configuration
app.config['JSON_SORT_KEYS'] = False
app.config['MAX_CONTENT_LENGTH'] = 100 * 1024 * 1024  # 100MB max file upload


# ===================================================
# COMPONENT INITIALIZATION
# ===================================================

# Status tracking
COMPONENTS = {
    "ai_brain": False,
    "desktop_automation": False,
    "whisper_voice": False,
    "reminders": False,
    "tasks": False,
    "scheduler": False
}

# Component instances
brain = None
desktop = None
whisper_model = None
reminder_manager = None
task_manager = None
scheduler = None


# ===================================================
# AI BRAIN INITIALIZATION
# ===================================================
try:
    from ai.brain import AIBrain
    brain = AIBrain()
    COMPONENTS["ai_brain"] = True
    print("✅ AI Brain loaded successfully")
except Exception as e:
    print(f"⚠️  AI Brain initialization failed: {e}")
    brain = None


# ===================================================
# DESKTOP AUTOMATION INITIALIZATION
# ===================================================
try:
    from desktop import handle_command as desktop_handle
    from desktop import desktop as desktop_module
    desktop = desktop_module
    COMPONENTS["desktop_automation"] = True
    print("✅ Desktop automation loaded successfully")
except Exception as e:
    print(f"⚠️  Desktop automation initialization failed: {e}")
    desktop = None
    desktop_handle = None


# ===================================================
# WHISPER VOICE RECOGNITION INITIALIZATION
# ===================================================
try:
    from faster_whisper import WhisperModel
    whisper_model = WhisperModel("base", device="cpu", compute_type="int8")
    COMPONENTS["whisper_voice"] = True
    print("✅ Whisper voice recognition loaded successfully")
except Exception as e:
    print(f"⚠️  Whisper initialization failed: {e}")
    whisper_model = None


# ===================================================
# REMINDER SYSTEM INITIALIZATION
# ===================================================
try:
    from automation.reminders import get_reminder_manager
    reminder_manager = get_reminder_manager()
    COMPONENTS["reminders"] = True
    print("✅ Reminder system loaded successfully")
except Exception as e:
    print(f"⚠️  Reminder system initialization failed: {e}")
    reminder_manager = None


# ===================================================
# TASK SYSTEM INITIALIZATION
# ===================================================
try:
    from automation.tasks import get_task_manager
    task_manager = get_task_manager()
    COMPONENTS["tasks"] = True
    print("✅ Task system loaded successfully")
except Exception as e:
    print(f"⚠️  Task system initialization failed: {e}")
    task_manager = None


# ===================================================
# SCHEDULER SYSTEM INITIALIZATION
# ===================================================
try:
    from automation.scheduler import get_scheduler
    scheduler = get_scheduler()
    COMPONENTS["scheduler"] = True
    print("✅ Scheduler system loaded successfully")
except Exception as e:
    print(f"⚠️  Scheduler initialization failed: {e}")
    scheduler = None


# ===================================================
# UTILITY FUNCTIONS
# ===================================================

def log_event(event_type: str, message: str, data: Any = None):
    """Log events for debugging and monitoring."""
    timestamp = datetime.datetime.now().isoformat()
    log_entry = {
        "timestamp": timestamp,
        "type": event_type,
        "message": message,
        "data": data
    }
    print(f"[{timestamp}] {event_type}: {message}")
    return log_entry


def safe_execute(func, *args, **kwargs) -> Tuple[bool, Any, str]:
    """
    Safely execute a function with error handling.
    Returns: (success, result, error_message)
    """
    try:
        result = func(*args, **kwargs)
        return True, result, None
    except Exception as e:
        error_msg = str(e)
        log_event("ERROR", f"Execution failed: {error_msg}")
        return False, None, error_msg


# ===================================================
# QUICK ACTION COMMAND MAP
# ===================================================
QUICK_ACTION_MAP = {
    # System & Info
    "time": {"type": "info", "action": "get_time"},
    "date": {"type": "info", "action": "get_date"},
    "battery": {"type": "info", "action": "get_battery"},
    "status": {"type": "system", "action": "get_status"},
    "help": {"type": "info", "action": "get_help"},
    
    # Applications
    "chrome": {"type": "app", "action": "open_app", "param": "chrome"},
    "notepad": {"type": "app", "action": "open_app", "param": "notepad"},
    "files": {"type": "app", "action": "open_app", "param": "explorer"},
    "desktop": {"type": "app", "action": "open_app", "param": "desktop"},
    
    # System Actions
    "screenshot": {"type": "system", "action": "screenshot"},
    "lock": {"type": "system", "action": "lock_computer"},
    "mute": {"type": "system", "action": "mute"},
    
    # Volume Control
    "vol+": {"type": "system", "action": "volume_up"},
    "volume up": {"type": "system", "action": "volume_up"},
    "vol-": {"type": "system", "action": "volume_down"},
    "volume down": {"type": "system", "action": "volume_down"},
    
    # Timers & Reminders
    "5min timer": {"type": "reminder", "action": "add_timer", "minutes": 5},
    "10min timer": {"type": "reminder", "action": "add_timer", "minutes": 10},
    "reminders": {"type": "reminder", "action": "list_reminders"},
    
    # Tasks
    "morning": {"type": "task", "action": "run_task", "task": "morning_routine"},
    "focus": {"type": "task", "action": "run_task", "task": "focus_mode"},
    "break": {"type": "task", "action": "run_task", "task": "break_reminder"},
    "tasks": {"type": "task", "action": "list_tasks"},
    "work": {"type": "task", "action": "run_task", "task": "work_mode"},
    "end day": {"type": "task", "action": "run_task", "task": "end_of_day"},
    
    # Schedules & Management
    "schedules": {"type": "schedule", "action": "list_schedules"},
    "clear all": {"type": "system", "action": "clear_all"},
}


# ===================================================
# SYSTEM ROUTES
# ===================================================

@app.route("/")
def index():
    """Serve modern ARES UI (primary interface)."""
    return render_template("index_modern.html")


@app.route("/classic")
def index_classic():
    """Serve classic ARES UI (fallback interface)."""
    return render_template("index.html")


@app.route("/health")
def health_check():
    """System health check endpoint."""
    return jsonify({
        "agent": "ARES",
        "status": "ONLINE",
        "timestamp": datetime.datetime.now().isoformat(),
        "components": COMPONENTS,
        "all_ready": all(COMPONENTS.values()),
        "message": "All systems operational" if all(COMPONENTS.values()) 
                   else "Some components degraded"
    })


@app.route("/status")
def status():
    """Get current system status (short form)."""
    return jsonify({
        "status": "ONLINE",
        "components": COMPONENTS,
        "features": {
            "ai_brain": COMPONENTS["ai_brain"],
            "voice_recognition": COMPONENTS["whisper_voice"],
            "desktop_automation": COMPONENTS["desktop_automation"],
            "task_execution": COMPONENTS["tasks"],
            "scheduling": COMPONENTS["scheduler"],
            "reminders": COMPONENTS["reminders"]
        }
    })


@app.route("/info")
def system_info():
    """Get detailed system information."""
    return jsonify({
        "system": "ARES",
        "version": "2.0.0",
        "mode": "production",
        "components": COMPONENTS,
        "time": datetime.datetime.now().isoformat(),
        "user": "Suvadip Panja"
    })


# ===================================================
# DIRECT ACTION ENDPOINT (Real-time, No AI)
# ===================================================

@app.route("/direct-action", methods=["POST"])
def direct_action():
    """
    Direct automation endpoint for quick actions.
    Bypasses AI processing for real-time execution.
    
    Request: {"action": "volume_up"}
    Response: Immediate execution result
    """
    try:
        data = request.get_json(silent=True)
        if not data or "action" not in data:
            return jsonify({"error": "No action provided"}), 400
        
        action = data["action"].lower().strip()
        log_event("DIRECT_ACTION", f"Received: {action}")
        
        # ===============================================
        # HANDLE QUICK ACTIONS
        # ===============================================
        
        # Get action mapping
        if action in QUICK_ACTION_MAP:
            action_map = QUICK_ACTION_MAP[action]
            action_type = action_map["type"]
            
            # ===============================================
            # INFO ACTIONS
            # ===============================================
            if action_type == "info":
                if action_map["action"] == "get_time":
                    current_time = datetime.datetime.now().strftime("%I:%M %p")
                    response = f"The current time is {current_time}"
                    return jsonify({
                        "success": True,
                        "response": response,
                        "action": action,
                        "source": "direct"
                    })
                
                elif action_map["action"] == "get_date":
                    current_date = datetime.datetime.now().strftime("%A, %B %d, %Y")
                    response = f"Today is {current_date}"
                    return jsonify({
                        "success": True,
                        "response": response,
                        "action": action,
                        "source": "direct"
                    })
                
                elif action_map["action"] == "get_battery":
                    if COMPONENTS["desktop_automation"] and desktop:
                        try:
                            battery = desktop.get_battery()
                            response = f"Battery: {battery}"
                        except:
                            response = "Battery information unavailable"
                    else:
                        response = "Desktop automation not available"
                    return jsonify({
                        "success": True,
                        "response": response,
                        "action": action,
                        "source": "direct"
                    })
                
                elif action_map["action"] == "get_help":
                    response = """I can help you with:
                    
✅ Voice Commands - Talk naturally
✅ App Control - Open Chrome, Notepad, Files
✅ System - Volume, Screenshot, Lock
✅ Timers - Set 5 or 10 min timers
✅ Tasks - Morning, Focus, Break, Work, End Day
✅ Schedules - View and manage schedules
✅ Info - Time, Date, Battery, Status

Just click buttons or speak commands!"""
                    return jsonify({
                        "success": True,
                        "response": response,
                        "action": action,
                        "source": "direct"
                    })
            
            # ===============================================
            # APP ACTIONS (Open applications)
            # ===============================================
            elif action_type == "app":
                if COMPONENTS["desktop_automation"] and desktop:
                    try:
                        app_name = action_map["param"]
                        desktop.open_app(app_name)
                        response = f"Opening {app_name.title()}..."
                        log_event("APP_OPEN", f"Opened {app_name}")
                        return jsonify({
                            "success": True,
                            "response": response,
                            "action": action,
                            "source": "direct"
                        })
                    except Exception as e:
                        return jsonify({
                            "success": False,
                            "error": str(e),
                            "action": action
                        }), 500
                else:
                    return jsonify({
                        "error": "Desktop automation not available"
                    }), 503
            
            # ===============================================
            # SYSTEM ACTIONS (Volume, screenshot, etc)
            # ===============================================
            elif action_type == "system":
                if COMPONENTS["desktop_automation"] and desktop:
                    try:
                        action_name = action_map["action"]
                        
                        if action_name == "volume_up":
                            desktop.volume_up()
                            response = "Volume increased"
                        elif action_name == "volume_down":
                            desktop.volume_down()
                            response = "Volume decreased"
                        elif action_name == "mute":
                            desktop.mute()
                            response = "Muted"
                        elif action_name == "screenshot":
                            desktop.take_screenshot()
                            response = "Screenshot taken"
                        elif action_name == "lock_computer":
                            desktop.lock_computer()
                            response = "Computer locked"
                        elif action_name == "get_status":
                            response = "System is operational"
                        else:
                            response = "Action executed"
                        
                        log_event("SYSTEM_ACTION", action_name)
                        return jsonify({
                            "success": True,
                            "response": response,
                            "action": action,
                            "source": "direct"
                        })
                    except Exception as e:
                        return jsonify({
                            "success": False,
                            "error": str(e),
                            "action": action
                        }), 500
                else:
                    return jsonify({
                        "error": "Desktop automation not available"
                    }), 503
            
            # ===============================================
            # REMINDER ACTIONS
            # ===============================================
            elif action_type == "reminder":
                if COMPONENTS["reminders"] and reminder_manager:
                    try:
                        if action_map["action"] == "add_timer":
                            minutes = action_map.get("minutes", 5)
                            reminder = reminder_manager.add_relative(
                                message=f"{minutes} minute timer",
                                minutes=minutes
                            )
                            response = f"Timer set for {minutes} minutes"
                        elif action_map["action"] == "list_reminders":
                            reminders = reminder_manager.get_all()
                            response = f"You have {len(reminders)} active reminders"
                        else:
                            response = "Reminder action executed"
                        
                        log_event("REMINDER_ACTION", response)
                        return jsonify({
                            "success": True,
                            "response": response,
                            "action": action,
                            "source": "direct"
                        })
                    except Exception as e:
                        return jsonify({
                            "success": False,
                            "error": str(e),
                            "action": action
                        }), 500
                else:
                    return jsonify({
                        "error": "Reminder system not available"
                    }), 503
            
            # ===============================================
            # TASK ACTIONS
            # ===============================================
            elif action_type == "task":
                if COMPONENTS["tasks"] and task_manager:
                    try:
                        if action_map["action"] == "list_tasks":
                            tasks = task_manager.get_all()
                            response = f"You have {len(tasks)} available tasks"
                        elif action_map["action"] == "run_task":
                            task_name = action_map.get("task", "")
                            result = task_manager.run_task_by_name(task_name)
                            if result:
                                response = f"Running {task_name.replace('_', ' ').title()}"
                            else:
                                response = f"Task '{task_name}' not found"
                        else:
                            response = "Task action executed"
                        
                        log_event("TASK_ACTION", response)
                        return jsonify({
                            "success": True,
                            "response": response,
                            "action": action,
                            "source": "direct"
                        })
                    except Exception as e:
                        return jsonify({
                            "success": False,
                            "error": str(e),
                            "action": action
                        }), 500
                else:
                    return jsonify({
                        "error": "Task system not available"
                    }), 503
            
            # ===============================================
            # SCHEDULE ACTIONS
            # ===============================================
            elif action_type == "schedule":
                if COMPONENTS["scheduler"] and scheduler:
                    try:
                        if action_map["action"] == "list_schedules":
                            schedules = scheduler.get_all()
                            response = f"You have {len(schedules)} active schedules"
                        else:
                            response = "Schedule action executed"
                        
                        log_event("SCHEDULE_ACTION", response)
                        return jsonify({
                            "success": True,
                            "response": response,
                            "action": action,
                            "source": "direct"
                        })
                    except Exception as e:
                        return jsonify({
                            "success": False,
                            "error": str(e),
                            "action": action
                        }), 500
                else:
                    return jsonify({
                        "error": "Scheduler not available"
                    }), 503
        
        # Unknown action
        return jsonify({
            "error": f"Unknown action: {action}",
            "action": action
        }), 400
    
    except Exception as e:
        log_event("DIRECT_ACTION_ERROR", str(e))
        traceback.print_exc()
        return jsonify({
            "error": str(e)
        }), 500


# ===================================================
# MAIN AI COMMAND ENDPOINT (For conversations)
# ===================================================

@app.route("/ai-command", methods=["POST"])
def ai_command():
    """
    Main unified command endpoint.
    Intelligently routes commands to appropriate handler:
    - Desktop automation
    - Task execution
    - Scheduling
    - AI conversation
    - Reminders
    
    Request body: {"command": "user command"}
    """
    try:
        # Parse request
        data = request.get_json(silent=True)
        
        if not data or "command" not in data:
            return jsonify({"error": "No command provided"}), 400
        
        user_input = data["command"].strip()
        
        if not user_input:
            return jsonify({"error": "Empty command"}), 400
        
        text = user_input.lower()
        
        log_event("COMMAND", f"Received: {user_input}")
        
        # ===============================================
        # PRIORITY 1: DESKTOP AUTOMATION
        # ===============================================
        if COMPONENTS["desktop_automation"] and desktop_handle:
            success, result, error = safe_execute(desktop_handle, user_input)
            
            if success and result:
                action = result.get("action", "unknown")
                
                # If desktop recognized the command
                if action not in ["unknown", "conversation", None]:
                    log_event("DESKTOP", f"Handled: {action}")
                    return jsonify({
                        "reply": result.get("response", "Command executed."),
                        "action": action,
                        "data": result.get("data"),
                        "source": "desktop",
                        "success": True
                    })
        
        # ===============================================
        # PRIORITY 2: FAST PATTERNS (No AI needed)
        # ===============================================
        
        # Greetings
        if text in ["hi", "hello", "hey", "hii", "hola"]:
            hour = datetime.datetime.now().hour
            greeting = "Good morning" if hour < 12 else "Good afternoon" if hour < 18 else "Good evening"
            reply = f"{greeting}, Suvadip! 👋 I'm ARES. How can I help you?"
            log_event("GREETING", "Greeting sent")
            return jsonify({"reply": reply, "source": "pattern", "success": True})
        
        # Help command
        if text in ["help", "what can you do", "capabilities", "features"]:
            reply = """🤖 I can help you with:
            
✅ Voice Commands - Talk to me naturally
✅ Desktop Control - Open apps, control system
✅ Task Execution - Run predefined workflows
✅ Task Scheduling - Schedule tasks automatically
✅ Reminders - Set alarms and timers
✅ Information - Get time, weather, news
✅ System Control - Lock PC, adjust volume, etc.

Try: "open chrome", "set reminder in 5 minutes", "run morning routine"
            """
            log_event("HELP", "Help menu displayed")
            return jsonify({"reply": reply, "source": "pattern", "success": True})
        
        # List tasks
        if "list" in text and ("task" in text or "can do" in text):
            if COMPONENTS["tasks"] and task_manager:
                tasks = task_manager.get_all()
                task_list = ", ".join([t.name for t in tasks[:10]])
                reply = f"Available tasks: {task_list}"
            else:
                reply = "Task system not available"
            log_event("LIST_TASKS", "Tasks listed")
            return jsonify({"reply": reply, "source": "pattern", "success": True})
        
        # List schedules
        if "list" in text and "schedule" in text:
            if COMPONENTS["scheduler"] and scheduler:
                schedules = scheduler.get_all()
                schedule_count = len(schedules)
                reply = f"You have {schedule_count} active schedules."
            else:
                reply = "Scheduler not available"
            log_event("LIST_SCHEDULES", "Schedules listed")
            return jsonify({"reply": reply, "source": "pattern", "success": True})
        
        # Time
        if text in ["time", "what time is it", "tell me time", "current time"]:
            current_time = datetime.datetime.now().strftime("%I:%M %p")
            reply = f"The current time is {current_time}"
            log_event("TIME", reply)
            return jsonify({"reply": reply, "source": "pattern", "success": True})
        
        # Date
        if text in ["date", "what date", "today date", "current date"]:
            current_date = datetime.datetime.now().strftime("%A, %B %d, %Y")
            reply = f"Today is {current_date}"
            log_event("DATE", reply)
            return jsonify({"reply": reply, "source": "pattern", "success": True})
        
        # ===============================================
        # PRIORITY 3: AI BRAIN CONVERSATION
        # ===============================================
        if COMPONENTS["ai_brain"] and brain:
            success, response, error = safe_execute(brain.converse, user_input)
            
            if success and response:
                log_event("AI_BRAIN", "Conversation handled")
                return jsonify({
                    "reply": response,
                    "source": "ai",
                    "success": True
                })
            elif error:
                log_event("AI_ERROR", error)
        
        # ===============================================
        # FALLBACK
        # ===============================================
        reply = f"I understood: '{user_input}'. Try 'help' to see what I can do."
        log_event("FALLBACK", "No handler matched")
        return jsonify({
            "reply": reply,
            "source": "fallback",
            "success": False
        })
    
    except Exception as e:
        log_event("CRITICAL_ERROR", str(e))
        traceback.print_exc()
        return jsonify({
            "error": str(e),
            "success": False
        }), 500


# ===================================================
# TASK MANAGEMENT ROUTES
# ===================================================

@app.route("/tasks")
def get_all_tasks():
    """Get list of all available tasks."""
    if not COMPONENTS["tasks"] or not task_manager:
        return jsonify({"error": "Task system not available", "tasks": []}), 503
    
    try:
        tasks = task_manager.get_all()
        return jsonify({
            "tasks": [t.to_dict() for t in tasks],
            "count": len(tasks),
            "success": True
        })
    except Exception as e:
        return jsonify({"error": str(e), "tasks": []}), 500


@app.route("/tasks/<task_id>")
def get_task(task_id):
    """Get specific task details."""
    if not COMPONENTS["tasks"] or not task_manager:
        return jsonify({"error": "Task system not available"}), 503
    
    try:
        task = task_manager.get_by_id(task_id)
        if task:
            return jsonify({"task": task.to_dict(), "success": True})
        return jsonify({"error": "Task not found"}), 404
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/tasks/run/<task_id>", methods=["POST"])
def run_task_by_id(task_id):
    """Execute a task by ID."""
    if not COMPONENTS["tasks"] or not task_manager:
        return jsonify({"error": "Task system not available"}), 503
    
    try:
        result = task_manager.run_task(task_id)
        if result:
            log_event("TASK_EXECUTION", f"Task {task_id} executed")
            return jsonify({
                "success": result.status == "completed",
                "task_id": result.task_id,
                "task_name": result.task_name,
                "status": result.status,
                "message": result.message,
                "speak_text": result.speak_text
            })
        return jsonify({"error": "Task not found"}), 404
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/tasks/run-by-name", methods=["POST"])
def run_task_by_name():
    """Execute a task by name."""
    if not COMPONENTS["tasks"] or not task_manager:
        return jsonify({"error": "Task system not available"}), 503
    
    try:
        data = request.get_json(silent=True)
        if not data or "name" not in data:
            return jsonify({"error": "No task name provided"}), 400
        
        task_name = data["name"]
        result = task_manager.run_task_by_name(task_name)
        
        if result:
            log_event("TASK_EXECUTION", f"Task '{task_name}' executed")
            return jsonify({
                "success": result.status == "completed",
                "task_id": result.task_id,
                "task_name": result.task_name,
                "status": result.status,
                "message": result.message,
                "speak_text": result.speak_text
            })
        return jsonify({"error": f"Task '{task_name}' not found"}), 404
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/tasks/categories")
def task_categories():
    """Get tasks grouped by category."""
    if not COMPONENTS["tasks"] or not task_manager:
        return jsonify({"error": "Task system not available", "categories": {}}), 503
    
    try:
        tasks = task_manager.get_all()
        categories = {}
        
        for task in tasks:
            cat = task.category
            if cat not in categories:
                categories[cat] = []
            categories[cat].append(task.to_dict())
        
        return jsonify({
            "categories": categories,
            "count": len(tasks),
            "success": True
        })
    except Exception as e:
        return jsonify({"error": str(e), "categories": {}}), 500


# ===================================================
# SCHEDULER ROUTES
# ===================================================

@app.route("/schedules")
def get_all_schedules():
    """Get list of all schedules."""
    if not COMPONENTS["scheduler"] or not scheduler:
        return jsonify({"error": "Scheduler not available", "schedules": []}), 503
    
    try:
        schedules = scheduler.get_all()
        return jsonify({
            "schedules": [s.to_dict() for s in schedules],
            "count": len(schedules),
            "success": True
        })
    except Exception as e:
        return jsonify({"error": str(e), "schedules": []}), 500


@app.route("/schedules/<schedule_id>")
def get_schedule(schedule_id):
    """Get specific schedule details."""
    if not COMPONENTS["scheduler"] or not scheduler:
        return jsonify({"error": "Scheduler not available"}), 503
    
    try:
        schedule = scheduler.get_by_id(schedule_id)
        if schedule:
            return jsonify({"schedule": schedule.to_dict(), "success": True})
        return jsonify({"error": "Schedule not found"}), 404
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/schedules/add", methods=["POST"])
def create_schedule():
    """Create a new schedule."""
    if not COMPONENTS["scheduler"] or not scheduler:
        return jsonify({"error": "Scheduler not available"}), 503
    
    try:
        data = request.get_json(silent=True)
        if not data:
            return jsonify({"error": "No schedule data provided"}), 400
        
        task_id = data.get("task_id")
        task_name = data.get("task_name", "Task")
        schedule_type = data.get("type", "daily")
        
        if schedule_type == "daily":
            hour = data.get("hour", 9)
            minute = data.get("minute", 0)
            schedule = scheduler.create_daily_schedule(task_id, task_name, hour, minute)
        
        elif schedule_type == "interval":
            minutes = data.get("minutes", 60)
            schedule = scheduler.create_interval_schedule(task_id, task_name, minutes)
        
        elif schedule_type == "weekly":
            days = data.get("days", [0])
            hour = data.get("hour", 9)
            minute = data.get("minute", 0)
            schedule = scheduler.create_weekly_schedule(task_id, task_name, days, hour, minute)
        
        elif schedule_type == "hourly":
            schedule = scheduler.create_interval_schedule(task_id, task_name, 60)
        
        else:
            return jsonify({"error": f"Invalid schedule type: {schedule_type}"}), 400
        
        log_event("SCHEDULE_CREATED", f"Schedule created for task '{task_name}'")
        return jsonify({
            "success": True,
            "schedule": schedule.to_dict()
        })
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/schedules/<schedule_id>/delete", methods=["POST", "DELETE"])
def delete_schedule(schedule_id):
    """Delete a schedule."""
    if not COMPONENTS["scheduler"] or not scheduler:
        return jsonify({"error": "Scheduler not available"}), 503
    
    try:
        if scheduler.delete(schedule_id):
            log_event("SCHEDULE_DELETED", f"Schedule {schedule_id} deleted")
            return jsonify({"success": True})
        return jsonify({"error": "Schedule not found"}), 404
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/schedules/<schedule_id>/enable", methods=["POST"])
def enable_schedule(schedule_id):
    """Enable a schedule."""
    if not COMPONENTS["scheduler"] or not scheduler:
        return jsonify({"error": "Scheduler not available"}), 503
    
    try:
        if scheduler.enable(schedule_id, True):
            return jsonify({"success": True})
        return jsonify({"error": "Schedule not found"}), 404
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/schedules/<schedule_id>/disable", methods=["POST"])
def disable_schedule(schedule_id):
    """Disable a schedule."""
    if not COMPONENTS["scheduler"] or not scheduler:
        return jsonify({"error": "Scheduler not available"}), 503
    
    try:
        if scheduler.enable(schedule_id, False):
            return jsonify({"success": True})
        return jsonify({"error": "Schedule not found"}), 404
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/schedules/clear", methods=["POST"])
def clear_all_schedules():
    """Clear all schedules."""
    if not COMPONENTS["scheduler"] or not scheduler:
        return jsonify({"error": "Scheduler not available"}), 503
    
    try:
        count = scheduler.clear_all()
        log_event("SCHEDULES_CLEARED", f"Cleared {count} schedules")
        return jsonify({"success": True, "deleted": count})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


# ===================================================
# REMINDER ROUTES
# ===================================================

@app.route("/reminders")
def get_all_reminders():
    """Get all reminders."""
    if not COMPONENTS["reminders"] or not reminder_manager:
        return jsonify({"error": "Reminder system not available", "reminders": []}), 503
    
    try:
        reminders = reminder_manager.get_all()
        return jsonify({
            "reminders": [r.to_dict() for r in reminders],
            "count": len(reminders),
            "success": True
        })
    except Exception as e:
        return jsonify({"error": str(e), "reminders": []}), 500


@app.route("/reminders/triggered")
def get_triggered_reminders():
    """Get currently triggered reminders (for notifications)."""
    if not COMPONENTS["reminders"] or not reminder_manager:
        return jsonify({"triggered": []})
    
    try:
        triggered = reminder_manager.get_triggered()
        return jsonify({
            "triggered": [r.to_dict() for r in triggered],
            "count": len(triggered)
        })
    except Exception as e:
        return jsonify({"triggered": []})


@app.route("/reminders/add", methods=["POST"])
def add_reminder():
    """Add a new reminder."""
    if not COMPONENTS["reminders"] or not reminder_manager:
        return jsonify({"error": "Reminder system not available"}), 503
    
    try:
        data = request.get_json(silent=True)
        if not data:
            return jsonify({"error": "No reminder data provided"}), 400
        
        message = data.get("message", "Reminder")
        minutes = data.get("minutes", 0)
        hours = data.get("hours", 0)
        seconds = data.get("seconds", 0)
        
        reminder = reminder_manager.add_relative(
            message=message,
            minutes=minutes,
            hours=hours,
            seconds=seconds
        )
        
        log_event("REMINDER_ADDED", message)
        return jsonify({
            "success": True,
            "reminder": reminder.to_dict()
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/reminders/<reminder_id>/delete", methods=["POST", "DELETE"])
def delete_reminder(reminder_id):
    """Delete a reminder."""
    if not COMPONENTS["reminders"] or not reminder_manager:
        return jsonify({"error": "Reminder system not available"}), 503
    
    try:
        if reminder_manager.delete(reminder_id):
            return jsonify({"success": True})
        return jsonify({"error": "Reminder not found"}), 404
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/reminders/clear", methods=["POST"])
def clear_all_reminders():
    """Clear all reminders."""
    if not COMPONENTS["reminders"] or not reminder_manager:
        return jsonify({"error": "Reminder system not available"}), 503
    
    try:
        count = reminder_manager.clear_all()
        log_event("REMINDERS_CLEARED", f"Cleared {count} reminders")
        return jsonify({"success": True, "deleted": count})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


# ===================================================
# VOICE RECOGNITION ROUTES
# ===================================================

@app.route("/voice/status")
def voice_status():
    """Get voice recognition status."""
    return jsonify({
        "available": COMPONENTS["whisper_voice"],
        "model": "base" if COMPONENTS["whisper_voice"] else None,
        "status": "ready" if COMPONENTS["whisper_voice"] else "unavailable"
    })


@app.route("/voice/transcribe", methods=["POST"])
def voice_transcribe():
    """
    Transcribe audio using Whisper.
    
    Accepts:
    - Form file: audio file with key 'audio'
    - JSON base64: {"audio_base64": "..."}
    - Raw bytes: raw audio data
    """
    if not COMPONENTS["whisper_voice"] or not whisper_model:
        return jsonify({"error": "Whisper not available"}), 503
    
    temp_path = None
    try:
        # Parse input
        if request.files and 'audio' in request.files:
            # File upload
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
            # Raw bytes
            audio_bytes = request.data
            if audio_bytes:
                temp_path = tempfile.mktemp(suffix=".wav")
                with open(temp_path, 'wb') as f:
                    f.write(audio_bytes)
        
        if not temp_path or not os.path.exists(temp_path):
            return jsonify({"error": "No audio data provided"}), 400
        
        # Transcribe
        segments, info = whisper_model.transcribe(
            temp_path,
            language="en",
            beam_size=5,
            vad_filter=True
        )
        
        text = " ".join([seg.text for seg in segments]).strip()
        
        log_event("VOICE_TRANSCRIBED", text)
        
        return jsonify({
            "success": True,
            "text": text,
            "language": info.language if info else "en"
        })
    
    except Exception as e:
        log_event("VOICE_ERROR", str(e))
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500
    
    finally:
        # Cleanup
        if temp_path and os.path.exists(temp_path):
            try:
                os.unlink(temp_path)
            except:
                pass


# ===================================================
# STATIC FILE SERVING
# ===================================================

@app.route("/static/<path:filename>")
def serve_static(filename):
    """Serve static files (CSS, JS, images)."""
    return send_from_directory(app.static_folder, filename)


@app.route("/favicon.ico")
def favicon():
    """Serve favicon."""
    return send_from_directory(
        os.path.join(app.static_folder, "images"),
        "favicon.ico"
    )


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


@app.errorhandler(405)
def method_not_allowed(error):
    """Handle 405 errors."""
    return jsonify({
        "error": "Method not allowed",
        "status": 405
    }), 405


# ===================================================
# STARTUP & MAIN
# ===================================================

def print_startup():
    """
    Print comprehensive startup information.
    Called by main_web.py entry point.
    """
    print("\n" + "=" * 70)
    print("  🚀 ARES - Autonomous Runtime AI Assistant")
    print("=" * 70)
    print(f"  Status: ONLINE")
    print(f"  Mode: Production")
    print(f"  User: Suvadip Panja")
    print()
    print("  Component Status:")
    print(f"    {'✅' if COMPONENTS['ai_brain'] else '❌'} AI Brain ............ {COMPONENTS['ai_brain']}")
    print(f"    {'✅' if COMPONENTS['desktop_automation'] else '❌'} Desktop Automation .. {COMPONENTS['desktop_automation']}")
    print(f"    {'✅' if COMPONENTS['whisper_voice'] else '❌'} Voice Recognition ... {COMPONENTS['whisper_voice']}")
    print(f"    {'✅' if COMPONENTS['tasks'] else '❌'} Task System ......... {COMPONENTS['tasks']}")
    print(f"    {'✅' if COMPONENTS['scheduler'] else '❌'} Scheduler ........... {COMPONENTS['scheduler']}")
    print(f"    {'✅' if COMPONENTS['reminders'] else '❌'} Reminders ........... {COMPONENTS['reminders']}")
    print()
    print("  Web Interface:")
    print("    📱 Modern UI: http://127.0.0.1:5000/")
    print("    📱 Classic UI: http://127.0.0.1:5000/classic")
    print()
    print("  API Endpoints:")
    print("    🎯 Direct Automation: POST /direct-action")
    print("    💬 AI Commands: POST /ai-command")
    print("    📋 Tasks: GET /tasks")
    print("    📅 Schedules: GET /schedules")
    print("    🔔 Reminders: GET /reminders")
    print()
    print("=" * 70 + "\n")


if __name__ == "__main__":
    print_startup()
    
    # Run Flask app
    app.run(
        host="127.0.0.1",
        port=5000,
        debug=True,
        use_reloader=True
    )
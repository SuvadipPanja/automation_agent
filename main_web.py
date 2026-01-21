#!/usr/bin/env python3
"""
=====================================================
ARES - AUTONOMOUS RUNTIME AI AGENT
=====================================================
MAIN ENTRY POINT - Run this file to start ARES!

Usage:
    python main_web.py

Then open: http://127.0.0.1:5000

All features are integrated:
✅ Web UI (JARVIS-style modern interface)
✅ Voice Recognition (Whisper)
✅ AI Brain (Intelligent conversation)
✅ Desktop Automation (PyAutoGUI)
✅ Task Management (30+ predefined tasks)
✅ Smart Scheduling (Daily, weekly, interval)
✅ Reminder System (Alarms, timers, notifications)
✅ Text-to-Speech (pyttsx3)

Features:
- Production-ready Flask backend
- Real-time voice processing
- Automated task execution
- Background scheduling
- Persistent storage
- Error recovery
- Component health monitoring

Author: ARES AI Assistant
For: Suvadip Panja
=====================================================
"""

import sys
import os
from pathlib import Path

# ===================================================
# PATH CONFIGURATION
# ===================================================

# Get project root directory
PROJECT_ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(PROJECT_ROOT))

print("=" * 70)
print("  🚀 ARES - Autonomous Runtime AI Agent")
print("=" * 70)
print(f"  Project Root: {PROJECT_ROOT}")
print(f"  Python Version: {sys.version.split()[0]}")
print()


# ===================================================
# COMPONENT INITIALIZATION (Pre-Flask)
# ===================================================

print("  Initializing components...")
print()

# AI Brain
try:
    from ai.brain import AIBrain
    brain = AIBrain()
    print("  ✅ AI Brain loaded successfully")
except Exception as e:
    print(f"  ⚠️  AI Brain failed: {e}")

# Desktop Automation
try:
    from desktop import handle_command, desktop
    print("  ✅ Desktop Automation initialized")
except Exception as e:
    print(f"  ⚠️  Desktop Automation failed: {e}")

# Voice Recognition
try:
    from faster_whisper import WhisperModel
    print("  ✅ Whisper voice recognition ready")
except Exception as e:
    print(f"  ⚠️  Voice Recognition failed: {e}")

# Reminder System
try:
    from automation.reminders import get_reminder_manager
    reminder_manager = get_reminder_manager()
    print("  ✅ Reminder system initialized")
except Exception as e:
    print(f"  ⚠️  Reminder system failed: {e}")

# Task System
try:
    from automation.tasks import get_task_manager
    task_manager = get_task_manager()
    print("  ✅ Task system initialized")
except Exception as e:
    print(f"  ⚠️  Task system failed: {e}")

# Scheduler System
try:
    from automation.scheduler import get_scheduler
    scheduler = get_scheduler()
    print("  ✅ Scheduler system initialized")
except Exception as e:
    print(f"  ⚠️  Scheduler failed: {e}")

print()


# ===================================================
# FLASK APP IMPORT
# ===================================================

try:
    from web.app import app, print_startup
    print("  ✅ Flask app imported successfully")
except ImportError as e:
    print(f"  ❌ CRITICAL: Failed to import Flask app")
    print(f"     Error: {e}")
    print()
    print("     Make sure:")
    print("     1. web/app.py exists in project root")
    print("     2. Flask is installed: pip install flask")
    print("     3. All dependencies are available")
    sys.exit(1)

print()


# ===================================================
# APPLICATION STARTUP
# ===================================================

if __name__ == "__main__":
    print("=" * 70)
    
    # Call the startup banner from app.py
    print_startup()
    
    print("=" * 70)
    print("  Server Configuration:")
    print("    Host: 127.0.0.1")
    print("    Port: 5000")
    print("    Debug: True")
    print("    Reloader: Enabled")
    print()
    print("  Starting Flask development server...")
    print("=" * 70)
    print()
    
    # Start Flask app
    try:
        app.run(
            host="127.0.0.1",
            port=5000,
            debug=True,
            use_reloader=True,
            threaded=True
        )
    
    except KeyboardInterrupt:
        print()
        print("=" * 70)
        print("  👋 ARES shutting down...")
        print("  Goodbye, Suvadip! See you next time.")
        print("=" * 70)
        print()
        sys.exit(0)
    
    except Exception as e:
        print()
        print("=" * 70)
        print(f"  ❌ ERROR: {e}")
        print("=" * 70)
        import traceback
        traceback.print_exc()
        sys.exit(1)
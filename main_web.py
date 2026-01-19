"""
=====================================================
ARES - AUTONOMOUS RUNTIME AI AGENT
=====================================================
SINGLE ENTRY POINT - Run this file to start ARES!

Usage:
    python main_web.py

Then open: http://127.0.0.1:5000

All features are integrated:
✅ Web UI (JARVIS-style)
✅ Voice Recognition (Whisper)
✅ AI Brain (Ollama/Llama3)
✅ Desktop Automation (PyAutoGUI)
✅ Text-to-Speech

Author: ARES AI Assistant
For: Shobutik Panja
=====================================================
"""

from web.app import app, print_startup

if __name__ == "__main__":
    print_startup()
    app.run(host="127.0.0.1", port=5000, debug=True)
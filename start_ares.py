#!/usr/bin/env python3
"""
ARES Startup Script
Ensures all paths are set correctly before starting the web interface
"""

import sys
from pathlib import Path

# Add project root to Python path
PROJECT_ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(PROJECT_ROOT))

# Import and run Flask app
from web.app import app

if __name__ == "__main__":
    print("=" * 60)
    print("  🚀 ARES - Autonomous Runtime AI Agent")
    print("=" * 60)
    print(f"  Modern UI: http://127.0.0.1:5000/")
    print(f"  Classic UI: http://127.0.0.1:5000/classic")
    print("=" * 60)
    print()
    
    # Run Flask
    app.run(host="127.0.0.1", port=5000, debug=True)
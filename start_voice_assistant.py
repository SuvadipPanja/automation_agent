"""
=====================================================
🎤 ARES VOICE ASSISTANT - WAKE WORD MODE
=====================================================
Run this script to start ARES in always-listening mode.

Just say "Hey ARES" and speak your command!

Usage:
    python start_voice_assistant.py

Requirements:
    pip install faster-whisper sounddevice numpy pyttsx3
=====================================================
"""

import sys
import os

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def main():
    print("""
    ╔═══════════════════════════════════════════════════════╗
    ║                                                       ║
    ║     █████╗ ██████╗ ███████╗███████╗                  ║
    ║    ██╔══██╗██╔══██╗██╔════╝██╔════╝                  ║
    ║    ███████║██████╔╝█████╗  ███████╗                  ║
    ║    ██╔══██║██╔══██╗██╔══╝  ╚════██║                  ║
    ║    ██║  ██║██║  ██║███████╗███████║                  ║
    ║    ╚═╝  ╚═╝╚═╝  ╚═╝╚══════╝╚══════╝                  ║
    ║                                                       ║
    ║         🎤 VOICE ASSISTANT - WAKE WORD MODE          ║
    ║                                                       ║
    ╚═══════════════════════════════════════════════════════╝
    """)
    
    # Check dependencies
    print("🔍 Checking dependencies...")
    
    missing = []
    
    try:
        import sounddevice
        print("  ✅ sounddevice")
    except ImportError:
        print("  ❌ sounddevice")
        missing.append("sounddevice")
    
    try:
        import numpy
        print("  ✅ numpy")
    except ImportError:
        print("  ❌ numpy")
        missing.append("numpy")
    
    try:
        from faster_whisper import WhisperModel
        print("  ✅ faster-whisper")
    except ImportError:
        print("  ❌ faster-whisper")
        missing.append("faster-whisper")
    
    try:
        import pyttsx3
        print("  ✅ pyttsx3")
    except ImportError:
        print("  ⚠ pyttsx3 (optional, for voice output)")
    
    if missing:
        print(f"\n❌ Missing packages: {', '.join(missing)}")
        print(f"\nInstall with: pip install {' '.join(missing)}")
        sys.exit(1)
    
    print("\n✅ All dependencies OK!\n")
    
    # Import and start
    from voice.wake_word_engine import AresVoiceAssistant, create_ai_callback
    
    # Create assistant
    print("🔄 Initializing ARES Voice Assistant...")
    assistant = AresVoiceAssistant(whisper_model="base")
    
    # Connect to AI brain
    ai_callback = create_ai_callback()
    if ai_callback:
        assistant.set_ai_callback(ai_callback)
    else:
        print("⚠ Running without AI brain (echo mode)")
    
    # Wake word handler
    def on_wake():
        assistant.speak("Yes? How can I help you?")
    
    assistant.on_wake_word = on_wake
    
    # Start!
    print("\n" + "=" * 55)
    print("  🎤 Say 'Hey ARES' to wake me up!")
    print("  🛑 Say 'ARES stop' or press Ctrl+C to exit")
    print("=" * 55 + "\n")
    
    try:
        assistant.start()
    except KeyboardInterrupt:
        print("\n\n👋 Goodbye, Shobutik!")
        assistant.stop()


if __name__ == "__main__":
    main()
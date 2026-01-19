"""
ARES Voice Module
=================
Voice assistant capabilities for ARES.

Components:
- voice_engine: Low-level speech recognition and TTS
- voice_assistant: High-level assistant with AI integration
"""

from voice.voice_engine import VoiceEngine, VoiceConfig, VoiceState
from voice.voice_assistant import AresVoiceAssistant

__all__ = [
    'VoiceEngine',
    'VoiceConfig', 
    'VoiceState',
    'AresVoiceAssistant'
]
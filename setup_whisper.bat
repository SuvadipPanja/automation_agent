@echo off
echo ================================================
echo   ARES Whisper Voice Setup
echo ================================================
echo.

echo Installing Whisper Speech Recognition...
echo.

REM Install faster-whisper (recommended)
pip install faster-whisper

REM Install audio libraries
pip install sounddevice
pip install numpy
pip install scipy

echo.
echo ================================================
echo   Testing Whisper...
echo ================================================
python -c "from faster_whisper import WhisperModel; print('✓ Whisper installed successfully!')"

echo.
echo ================================================
echo   Setup Complete!
echo ================================================
echo.
echo Now run: python voice/whisper_engine.py
echo To test voice recognition.
echo.
pause
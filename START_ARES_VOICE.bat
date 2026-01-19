@echo off
title ARES Voice Assistant
color 0A

echo.
echo  =============================================
echo   ARES Voice Assistant - Wake Word Mode
echo  =============================================
echo.
echo  Starting ARES...
echo  Say "Hey ARES" to activate!
echo.

cd /d "%~dp0"
python start_voice_assistant.py

pause
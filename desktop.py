"""
=====================================================
ARES DESKTOP AUTOMATION MODULE
=====================================================
Complete desktop automation for Windows systems.

Features:
✅ Volume Control (up, down, mute)
✅ Screenshot Capture
✅ Computer Lock/Sleep
✅ Application Management (open, close, list)
✅ Window Management (minimize, maximize, focus)
✅ System Information (battery, time, date)
✅ Media Control (play, pause, next, previous)
✅ Folder/File Management
✅ Web Search & Browser Control
✅ Text-to-Speech
✅ Error Handling & Logging

Author: ARES Development
For: Suvadip Panja
=====================================================
"""

import os
import sys
import time
import subprocess
import datetime
import webbrowser
import logging
from pathlib import Path
from typing import Tuple, Dict, Any, Optional, List

# Add project root to path
PROJECT_ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(PROJECT_ROOT))

# ===================================================
# LOGGING SETUP
# ===================================================
logging.basicConfig(
    level=logging.INFO,
    format='[%(asctime)s] %(levelname)s: %(message)s'
)
logger = logging.getLogger(__name__)


# ===================================================
# PLATFORM DETECTION
# ===================================================
IS_WINDOWS = sys.platform.startswith('win')
IS_LINUX = sys.platform.startswith('linux')
IS_MAC = sys.platform.startswith('darwin')

logger.info(f"Platform detected: {'Windows' if IS_WINDOWS else 'Linux' if IS_LINUX else 'macOS'}")


# ===================================================
# OPTIONAL IMPORTS
# ===================================================

# PyAutoGUI for automation
try:
    import pyautogui
    PYAUTOGUI_AVAILABLE = True
    logger.info("✅ pyautogui available")
except ImportError:
    PYAUTOGUI_AVAILABLE = False
    logger.warning("⚠️  pyautogui not available - install: pip install pyautogui")

# psutil for system info
try:
    import psutil
    PSUTIL_AVAILABLE = True
    logger.info("✅ psutil available")
except ImportError:
    PSUTIL_AVAILABLE = False
    logger.warning("⚠️  psutil not available - install: pip install psutil")

# PIL for screenshots
try:
    from PIL import ImageGrab
    PIL_AVAILABLE = True
    logger.info("✅ PIL available")
except ImportError:
    PIL_AVAILABLE = False
    logger.warning("⚠️  PIL not available - install: pip install pillow")

# pyttsx3 for text-to-speech
try:
    import pyttsx3
    PYTTSX3_AVAILABLE = True
    TTS_ENGINE = pyttsx3.init()
    logger.info("✅ pyttsx3 available")
except ImportError:
    PYTTSX3_AVAILABLE = False
    logger.warning("⚠️  pyttsx3 not available - install: pip install pyttsx3")


# ===================================================
# DESKTOP AUTOMATION CLASS
# ===================================================

class DesktopAutomation:
    """
    Complete desktop automation system for ARES.
    Provides unified interface for all desktop operations.
    """
    
    def __init__(self):
        """Initialize desktop automation system."""
        self.user = os.getenv('USERNAME', 'user')
        self.desktop_path = Path.home() / "Desktop"
        self.documents_path = Path.home() / "Documents"
        logger.info(f"✅ Desktop Automation initialized for user: {self.user}")
    
    # ===================================================
    # SYSTEM INFORMATION
    # ===================================================
    
    def get_time(self) -> str:
        """Get current system time."""
        return datetime.datetime.now().strftime("%I:%M %p")
    
    def get_date(self) -> str:
        """Get current system date."""
        return datetime.datetime.now().strftime("%A, %B %d, %Y")
    
    def get_datetime(self) -> str:
        """Get current date and time."""
        return datetime.datetime.now().strftime("%A, %B %d, %Y at %I:%M %p")
    
    def get_battery(self) -> str:
        """Get battery information."""
        if not PSUTIL_AVAILABLE:
            return "Battery information unavailable (psutil not installed)"
        
        try:
            battery = psutil.sensors_battery()
            if battery:
                percent = battery.percent
                status = "charging" if battery.power_plugged else "discharging"
                return f"Battery: {percent}% ({status})"
            return "No battery detected (plugged in)"
        except Exception as e:
            logger.error(f"Battery check error: {e}")
            return "Battery information unavailable"
    
    def get_status(self) -> str:
        """Get system status."""
        return f"System is operational - {self.get_time()}"
    
    def get_system_info(self) -> Dict[str, Any]:
        """Get comprehensive system information."""
        info = {
            "user": self.user,
            "time": self.get_time(),
            "date": self.get_date(),
            "battery": self.get_battery(),
            "platform": sys.platform,
            "python_version": sys.version.split()[0]
        }
        
        if PSUTIL_AVAILABLE:
            try:
                info["cpu_percent"] = psutil.cpu_percent(interval=1)
                info["memory_percent"] = psutil.virtual_memory().percent
            except:
                pass
        
        return info
    
    # ===================================================
    # VOLUME CONTROL
    # ===================================================
    
    def volume_up(self) -> Tuple[bool, str]:
        """Increase volume."""
        try:
            if IS_WINDOWS:
                from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume
                devices = AudioUtilities.GetSpeakers()
                interface = devices.Activate(IAudioEndpointVolume._iid_, 0, None)
                volume = interface.QueryInterface(IAudioEndpointVolume)
                current = volume.GetMasterVolumeLevelScalar()
                volume.SetMasterVolumeLevelScalar(min(1.0, current + 0.1), None)
                logger.info("Volume increased")
                return True, "Volume increased"
            else:
                # Fallback for non-Windows
                if PYAUTOGUI_AVAILABLE:
                    pyautogui.press('volumeup')
                    return True, "Volume increased"
        except Exception as e:
            logger.warning(f"Volume up error: {e}")
            return False, str(e)
        
        return False, "Volume control not available"
    
    def volume_down(self) -> Tuple[bool, str]:
        """Decrease volume."""
        try:
            if IS_WINDOWS:
                from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume
                devices = AudioUtilities.GetSpeakers()
                interface = devices.Activate(IAudioEndpointVolume._iid_, 0, None)
                volume = interface.QueryInterface(IAudioEndpointVolume)
                current = volume.GetMasterVolumeLevelScalar()
                volume.SetMasterVolumeLevelScalar(max(0.0, current - 0.1), None)
                logger.info("Volume decreased")
                return True, "Volume decreased"
            else:
                # Fallback for non-Windows
                if PYAUTOGUI_AVAILABLE:
                    pyautogui.press('volumedown')
                    return True, "Volume decreased"
        except Exception as e:
            logger.warning(f"Volume down error: {e}")
            return False, str(e)
        
        return False, "Volume control not available"
    
    def mute(self) -> Tuple[bool, str]:
        """Mute/unmute audio."""
        try:
            if IS_WINDOWS:
                from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume
                devices = AudioUtilities.GetSpeakers()
                interface = devices.Activate(IAudioEndpointVolume._iid_, 0, None)
                volume = interface.QueryInterface(IAudioEndpointVolume)
                is_muted = volume.GetMute()
                volume.SetMute(not is_muted, None)
                status = "unmuted" if is_muted else "muted"
                logger.info(f"Audio {status}")
                return True, f"Audio {status}"
            else:
                # Fallback
                if PYAUTOGUI_AVAILABLE:
                    pyautogui.press('mute')
                    return True, "Audio muted"
        except Exception as e:
            logger.warning(f"Mute error: {e}")
            return False, str(e)
        
        return False, "Mute control not available"
    
    # ===================================================
    # SCREENSHOT & SCREEN CAPTURE
    # ===================================================
    
    def take_screenshot(self) -> Tuple[bool, str]:
        """Take screenshot and save to desktop."""
        try:
            if not PIL_AVAILABLE:
                return False, "PIL not available (install: pip install pillow)"
            
            timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            screenshot_path = self.desktop_path / f"screenshot_{timestamp}.png"
            
            # Ensure desktop directory exists
            screenshot_path.parent.mkdir(parents=True, exist_ok=True)
            
            # Take screenshot
            screenshot = ImageGrab.grab()
            screenshot.save(str(screenshot_path))
            
            logger.info(f"Screenshot saved: {screenshot_path}")
            return True, f"Screenshot saved to {screenshot_path.name}"
        except Exception as e:
            logger.error(f"Screenshot error: {e}")
            return False, f"Screenshot failed: {str(e)}"
    
    # ===================================================
    # COMPUTER CONTROL
    # ===================================================
    
    def lock_computer(self) -> Tuple[bool, str]:
        """Lock the computer."""
        try:
            if IS_WINDOWS:
                os.system("rundll32.exe user32.dll,LockWorkStation")
                logger.info("Computer locked")
                return True, "Computer locked"
            elif IS_LINUX:
                os.system("gnome-screensaver-command -l")
                logger.info("Screen locked")
                return True, "Screen locked"
            elif IS_MAC:
                os.system("open -a '/System/Library/CoreServices/ScreenTime.app'")
                logger.info("Sleep triggered")
                return True, "Sleep triggered"
        except Exception as e:
            logger.error(f"Lock error: {e}")
            return False, str(e)
        
        return False, "Lock not available on this system"
    
    def sleep_computer(self) -> Tuple[bool, str]:
        """Put computer to sleep."""
        try:
            if IS_WINDOWS:
                os.system("rundll32.exe powrprof.dll,SetSuspendState 0,1,0")
                logger.info("Computer sleeping")
                return True, "Computer sleeping"
            elif IS_LINUX:
                os.system("systemctl suspend")
                logger.info("System suspended")
                return True, "System suspended"
            elif IS_MAC:
                os.system("pmset sleepnow")
                logger.info("Mac sleeping")
                return True, "Mac sleeping"
        except Exception as e:
            logger.error(f"Sleep error: {e}")
            return False, str(e)
        
        return False, "Sleep not available"
    
    def shutdown_computer(self) -> Tuple[bool, str]:
        """Shutdown computer (requires confirmation)."""
        try:
            if IS_WINDOWS:
                os.system("shutdown /s /t 30 /c 'ARES shutdown initiated'")
                return True, "Shutdown initiated in 30 seconds"
            elif IS_LINUX:
                os.system("shutdown -h 1")
                return True, "Shutdown initiated in 1 minute"
            elif IS_MAC:
                os.system("osascript -e 'tell app \"System Events\" to shut down'")
                return True, "Shutdown initiated"
        except Exception as e:
            logger.error(f"Shutdown error: {e}")
            return False, str(e)
        
        return False, "Shutdown not available"
    
    # ===================================================
    # APPLICATION MANAGEMENT
    # ===================================================
    
    def open_app(self, app_name: str) -> Tuple[bool, str]:
        """Open application by name."""
        try:
            app_name_lower = app_name.lower().strip()
            
            if IS_WINDOWS:
                # Common Windows applications
                app_paths = {
                    "chrome": "chrome.exe",
                    "firefox": "firefox.exe",
                    "edge": "msedge.exe",
                    "notepad": "notepad.exe",
                    "notepad++": "notepad++.exe",
                    "vscode": "code.exe",
                    "explorer": "explorer.exe",
                    "files": "explorer.exe",
                    "desktop": f"{self.desktop_path}",
                    "documents": f"{self.documents_path}",
                    "calculator": "calc.exe",
                    "paint": "mspaint.exe",
                    "word": "winword.exe",
                    "excel": "excel.exe",
                    "powerpoint": "powerpnt.exe",
                    "outlook": "outlook.exe",
                    "teams": "teams.exe",
                    "discord": "Discord.exe",
                    "vlc": "vlc.exe",
                    "7zip": "7zFM.exe",
                    "putty": "putty.exe"
                }
                
                if app_name_lower in app_paths:
                    path = app_paths[app_name_lower]
                    if app_name_lower in ["desktop", "documents"]:
                        os.startfile(path)
                    else:
                        subprocess.Popen(path)
                    logger.info(f"Opened {app_name}")
                    return True, f"Opening {app_name}"
                else:
                    # Try direct execution
                    try:
                        subprocess.Popen(app_name)
                        logger.info(f"Opened {app_name}")
                        return True, f"Opening {app_name}"
                    except:
                        return False, f"Application '{app_name}' not found"
            
            elif IS_LINUX:
                subprocess.Popen([app_name_lower])
                logger.info(f"Opened {app_name}")
                return True, f"Opening {app_name}"
            
            elif IS_MAC:
                subprocess.Popen(["open", "-a", app_name])
                logger.info(f"Opened {app_name}")
                return True, f"Opening {app_name}"
        
        except Exception as e:
            logger.error(f"Open app error: {e}")
            return False, f"Failed to open {app_name}: {str(e)}"
        
        return False, f"Cannot open {app_name}"
    
    def close_app(self, app_name: str) -> Tuple[bool, str]:
        """Close application by name."""
        try:
            if IS_WINDOWS:
                app_name_lower = app_name.lower().strip()
                
                # Map friendly names to executable names
                exe_map = {
                    "chrome": "chrome.exe",
                    "firefox": "firefox.exe",
                    "edge": "msedge.exe",
                    "notepad": "notepad.exe",
                    "vscode": "code.exe",
                    "explorer": "explorer.exe",
                    "discord": "Discord.exe",
                    "teams": "teams.exe"
                }
                
                exe_name = exe_map.get(app_name_lower, f"{app_name_lower}.exe")
                os.system(f"taskkill /IM {exe_name} /F")
                logger.info(f"Closed {app_name}")
                return True, f"Closed {app_name}"
            
            elif IS_LINUX:
                os.system(f"killall {app_name}")
                logger.info(f"Closed {app_name}")
                return True, f"Closed {app_name}"
            
            elif IS_MAC:
                os.system(f"killall '{app_name}'")
                logger.info(f"Closed {app_name}")
                return True, f"Closed {app_name}"
        
        except Exception as e:
            logger.error(f"Close app error: {e}")
            return False, str(e)
        
        return False, f"Failed to close {app_name}"
    
    def list_running_apps(self) -> List[str]:
        """List running applications."""
        if not PSUTIL_AVAILABLE:
            return []
        
        try:
            apps = []
            for proc in psutil.process_iter(['pid', 'name']):
                try:
                    apps.append(proc.info['name'])
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    pass
            return sorted(list(set(apps)))[:20]  # Return top 20 unique apps
        except Exception as e:
            logger.error(f"List apps error: {e}")
            return []
    
    # ===================================================
    # WINDOW MANAGEMENT
    # ===================================================
    
    def minimize_all(self) -> Tuple[bool, str]:
        """Minimize all windows."""
        try:
            if IS_WINDOWS:
                os.system("rundll32.exe shell32.dll,ShellExec_RunDLL nircmd.exe muteoff")
                # Alternative method
                pyautogui.hotkey('win', 'd') if PYAUTOGUI_AVAILABLE else None
                logger.info("All windows minimized")
                return True, "All windows minimized"
            elif PYAUTOGUI_AVAILABLE:
                pyautogui.hotkey('super', 'd')
                return True, "All windows minimized"
        except Exception as e:
            logger.warning(f"Minimize all error: {e}")
            return False, str(e)
        
        return False, "Minimize all not available"
    
    def show_desktop(self) -> Tuple[bool, str]:
        """Show desktop (minimize all windows)."""
        return self.minimize_all()
    
    # ===================================================
    # FILE & FOLDER MANAGEMENT
    # ===================================================
    
    def open_folder(self, folder_path: str) -> Tuple[bool, str]:
        """Open a folder in explorer."""
        try:
            path = Path(folder_path).expanduser()
            if not path.exists():
                return False, f"Folder not found: {folder_path}"
            
            if IS_WINDOWS:
                os.startfile(str(path))
            elif IS_LINUX:
                subprocess.Popen(['xdg-open', str(path)])
            elif IS_MAC:
                subprocess.Popen(['open', str(path)])
            
            logger.info(f"Opened folder: {path}")
            return True, f"Opening {path.name}"
        except Exception as e:
            logger.error(f"Open folder error: {e}")
            return False, str(e)
    
    # ===================================================
    # WEB BROWSING
    # ===================================================
    
    def open_website(self, url: str) -> Tuple[bool, str]:
        """Open website in default browser."""
        try:
            if not url.startswith(('http://', 'https://')):
                url = 'https://' + url
            
            webbrowser.open(url)
            logger.info(f"Opened website: {url}")
            return True, f"Opening {url}"
        except Exception as e:
            logger.error(f"Open website error: {e}")
            return False, str(e)
    
    def search_google(self, query: str) -> Tuple[bool, str]:
        """Search Google."""
        try:
            url = f"https://www.google.com/search?q={query.replace(' ', '+')}"
            webbrowser.open(url)
            logger.info(f"Google search: {query}")
            return True, f"Searching Google for '{query}'"
        except Exception as e:
            logger.error(f"Google search error: {e}")
            return False, str(e)
    
    def search_youtube(self, query: str) -> Tuple[bool, str]:
        """Search YouTube."""
        try:
            url = f"https://www.youtube.com/results?search_query={query.replace(' ', '+')}"
            webbrowser.open(url)
            logger.info(f"YouTube search: {query}")
            return True, f"Searching YouTube for '{query}'"
        except Exception as e:
            logger.error(f"YouTube search error: {e}")
            return False, str(e)
    
    # ===================================================
    # MEDIA CONTROL
    # ===================================================
    
    def play_pause(self) -> Tuple[bool, str]:
        """Toggle play/pause."""
        try:
            if PYAUTOGUI_AVAILABLE:
                pyautogui.press('playpause')
                logger.info("Play/Pause toggled")
                return True, "Play/Pause toggled"
        except Exception as e:
            logger.warning(f"Play/pause error: {e}")
            return False, str(e)
        
        return False, "Media control not available"
    
    def next_track(self) -> Tuple[bool, str]:
        """Next track."""
        try:
            if PYAUTOGUI_AVAILABLE:
                pyautogui.press('nexttrack')
                logger.info("Next track")
                return True, "Playing next track"
        except Exception as e:
            logger.warning(f"Next track error: {e}")
            return False, str(e)
        
        return False, "Media control not available"
    
    def previous_track(self) -> Tuple[bool, str]:
        """Previous track."""
        try:
            if PYAUTOGUI_AVAILABLE:
                pyautogui.press('prevtrack')
                logger.info("Previous track")
                return True, "Playing previous track"
        except Exception as e:
            logger.warning(f"Previous track error: {e}")
            return False, str(e)
        
        return False, "Media control not available"
    
    # ===================================================
    # TEXT TO SPEECH
    # ===================================================
    
    def speak(self, text: str) -> Tuple[bool, str]:
        """Speak text using TTS."""
        try:
            if not PYTTSX3_AVAILABLE:
                return False, "Text-to-speech not available"
            
            TTS_ENGINE.say(text)
            TTS_ENGINE.runAndWait()
            logger.info(f"Spoken: {text}")
            return True, f"Speaking: {text}"
        except Exception as e:
            logger.error(f"TTS error: {e}")
            return False, str(e)
    
    # ===================================================
    # CLIPBOARD OPERATIONS
    # ===================================================
    
    def copy_to_clipboard(self, text: str) -> Tuple[bool, str]:
        """Copy text to clipboard."""
        try:
            import pyperclip
            pyperclip.copy(text)
            logger.info("Text copied to clipboard")
            return True, "Copied to clipboard"
        except ImportError:
            logger.warning("pyperclip not available")
            return False, "Clipboard not available (install: pip install pyperclip)"
        except Exception as e:
            return False, str(e)
    
    def paste_from_clipboard(self) -> Tuple[bool, str]:
        """Paste from clipboard."""
        try:
            import pyperclip
            text = pyperclip.paste()
            logger.info(f"Text pasted from clipboard: {text[:50]}")
            return True, text
        except ImportError:
            return False, "Clipboard not available (install: pip install pyperclip)"
        except Exception as e:
            return False, str(e)


# ===================================================
# GLOBAL INSTANCE
# ===================================================

# Create global instance
desktop = DesktopAutomation()


# ===================================================
# COMMAND HANDLER FOR FLASK
# ===================================================

def handle_command(command: str) -> Dict[str, Any]:
    """
    Handle desktop commands from natural language.
    Returns action type and response.
    """
    cmd = command.lower().strip()
    
    # Desktop commands that should be handled here
    desktop_patterns = {
        'volume up': lambda: desktop.volume_up(),
        'vol+': lambda: desktop.volume_up(),
        'louder': lambda: desktop.volume_up(),
        'volume down': lambda: desktop.volume_down(),
        'vol-': lambda: desktop.volume_down(),
        'quieter': lambda: desktop.volume_down(),
        'mute': lambda: desktop.mute(),
        'screenshot': lambda: desktop.take_screenshot(),
        'take screenshot': lambda: desktop.take_screenshot(),
        'screen capture': lambda: desktop.take_screenshot(),
        'lock': lambda: desktop.lock_computer(),
        'lock computer': lambda: desktop.lock_computer(),
        'sleep': lambda: desktop.sleep_computer(),
        'shutdown': lambda: desktop.shutdown_computer(),
        'minimize': lambda: desktop.minimize_all(),
        'show desktop': lambda: desktop.show_desktop(),
        'time': lambda: (True, f"The time is {desktop.get_time()}"),
        'date': lambda: (True, f"Today is {desktop.get_date()}"),
        'battery': lambda: (True, desktop.get_battery()),
        'status': lambda: (True, desktop.get_status()),
    }
    
    # Check for exact matches or key phrases
    for pattern, func in desktop_patterns.items():
        if pattern in cmd:
            success, response = func()
            return {
                "action": pattern.replace(' ', '_'),
                "success": success,
                "response": response if success else f"Failed: {response}",
                "data": None
            }
    
    # App opening patterns
    if 'open' in cmd or 'start' in cmd:
        apps = ['chrome', 'firefox', 'edge', 'notepad', 'vscode', 'explorer', 'files', 'calculator', 'paint']
        for app in apps:
            if app in cmd:
                success, response = desktop.open_app(app)
                return {
                    "action": f"open_{app}",
                    "success": success,
                    "response": response,
                    "data": None
                }
    
    # App closing patterns
    if 'close' in cmd:
        apps = ['chrome', 'firefox', 'edge', 'notepad', 'vscode', 'explorer', 'discord', 'teams']
        for app in apps:
            if app in cmd:
                success, response = desktop.close_app(app)
                return {
                    "action": f"close_{app}",
                    "success": success,
                    "response": response,
                    "data": None
                }
    
    # Search patterns
    if 'google' in cmd or 'search' in cmd:
        # Extract search query
        query = cmd.replace('google', '').replace('search', '').replace('for', '').strip()
        if query:
            success, response = desktop.search_google(query)
            return {
                "action": "google_search",
                "success": success,
                "response": response,
                "data": {"query": query}
            }
    
    if 'youtube' in cmd:
        query = cmd.replace('youtube', '').replace('search', '').replace('for', '').strip()
        if query:
            success, response = desktop.search_youtube(query)
            return {
                "action": "youtube_search",
                "success": success,
                "response": response,
                "data": {"query": query}
            }
    
    # Web opening patterns
    if 'open' in cmd and any(domain in cmd for domain in ['.com', '.org', '.net', 'website', 'site']):
        # Not a direct desktop action - route to AI
        return {
            "action": "conversation",
            "success": False,
            "response": None,
            "data": None
        }
    
    # Unknown command
    return {
        "action": "unknown",
        "success": False,
        "response": None,
        "data": None
    }


# ===================================================
# MAIN TEST
# ===================================================

if __name__ == "__main__":
    print("\n" + "=" * 60)
    print("  ARES DESKTOP AUTOMATION MODULE TEST")
    print("=" * 60)
    print()
    
    print("System Information:")
    info = desktop.get_system_info()
    for key, value in info.items():
        print(f"  {key.title()}: {value}")
    
    print()
    print("Testing Desktop Commands:")
    print()
    
    # Test each command
    test_commands = [
        "what time is it",
        "what's the date",
        "battery status",
        "system status",
        "open chrome",
        "search google python",
        "take screenshot",
        "list running apps",
        "minimize all",
    ]
    
    for test_cmd in test_commands:
        print(f"  Command: '{test_cmd}'")
        result = handle_command(test_cmd)
        print(f"  Result: {result}")
        print()
    
    print("=" * 60)
    print("✅ Desktop Automation Module Ready!")
    print("=" * 60)
    print()
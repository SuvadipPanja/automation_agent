"""
=====================================================
ARES DESKTOP AUTOMATION - PRODUCTION READY
=====================================================
Complete desktop control system for Windows.

Features:
- Open/Close applications
- Window management
- Keyboard & Mouse control
- Screenshots
- System controls (volume, brightness, lock)
- File & Folder operations
- Web searches
- Clipboard operations
- Process management

Author: ARES AI Assistant
For: Shobutik Panja
=====================================================
"""

import os
import sys
import time
import subprocess
import platform
import datetime
import webbrowser
import urllib.parse
from pathlib import Path
from typing import Optional, List, Dict, Tuple

# Third-party imports
try:
    import pyautogui
    pyautogui.FAILSAFE = True  # Move mouse to corner to abort
    pyautogui.PAUSE = 0.1  # Small pause between actions
    PYAUTOGUI_AVAILABLE = True
except ImportError:
    PYAUTOGUI_AVAILABLE = False
    print("⚠ pyautogui not installed. Run: pip install pyautogui")

try:
    import psutil
    PSUTIL_AVAILABLE = True
except ImportError:
    PSUTIL_AVAILABLE = False
    print("⚠ psutil not installed. Run: pip install psutil")

try:
    from PIL import ImageGrab
    PIL_AVAILABLE = True
except ImportError:
    PIL_AVAILABLE = False

# Windows-specific imports
IS_WINDOWS = platform.system() == "Windows"

if IS_WINDOWS:
    try:
        import ctypes
        from ctypes import wintypes
        CTYPES_AVAILABLE = True
    except:
        CTYPES_AVAILABLE = False


# =====================================================
# APPLICATION DATABASE
# =====================================================
# Common Windows applications and their paths/commands

APP_DATABASE = {
    # Browsers
    "chrome": {
        "names": ["chrome", "google chrome", "browser"],
        "paths": [
            r"C:\Program Files\Google\Chrome\Application\chrome.exe",
            r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",
        ],
        "command": "chrome"
    },
    "firefox": {
        "names": ["firefox", "mozilla firefox"],
        "paths": [
            r"C:\Program Files\Mozilla Firefox\firefox.exe",
            r"C:\Program Files (x86)\Mozilla Firefox\firefox.exe",
        ],
        "command": "firefox"
    },
    "edge": {
        "names": ["edge", "microsoft edge"],
        "paths": [
            r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe",
        ],
        "command": "msedge"
    },
    "brave": {
        "names": ["brave", "brave browser"],
        "paths": [
            r"C:\Program Files\BraveSoftware\Brave-Browser\Application\brave.exe",
        ],
        "command": "brave"
    },
    
    # Development
    "vscode": {
        "names": ["vs code", "vscode", "visual studio code", "code"],
        "paths": [
            r"C:\Users\{user}\AppData\Local\Programs\Microsoft VS Code\Code.exe",
            r"C:\Program Files\Microsoft VS Code\Code.exe",
        ],
        "command": "code"
    },
    "notepad": {
        "names": ["notepad", "text editor"],
        "paths": [r"C:\Windows\System32\notepad.exe"],
        "command": "notepad"
    },
    "notepad++": {
        "names": ["notepad++", "notepad plus plus", "npp"],
        "paths": [
            r"C:\Program Files\Notepad++\notepad++.exe",
            r"C:\Program Files (x86)\Notepad++\notepad++.exe",
        ],
        "command": "notepad++"
    },
    "cmd": {
        "names": ["cmd", "command prompt", "terminal", "command line"],
        "paths": [r"C:\Windows\System32\cmd.exe"],
        "command": "cmd"
    },
    "powershell": {
        "names": ["powershell", "power shell"],
        "paths": [r"C:\Windows\System32\WindowsPowerShell\v1.0\powershell.exe"],
        "command": "powershell"
    },
    "git bash": {
        "names": ["git bash", "bash"],
        "paths": [
            r"C:\Program Files\Git\git-bash.exe",
        ],
        "command": "git-bash"
    },
    
    # Microsoft Office
    "word": {
        "names": ["word", "microsoft word", "ms word"],
        "paths": [
            r"C:\Program Files\Microsoft Office\root\Office16\WINWORD.EXE",
            r"C:\Program Files (x86)\Microsoft Office\root\Office16\WINWORD.EXE",
        ],
        "command": "winword"
    },
    "excel": {
        "names": ["excel", "microsoft excel", "ms excel"],
        "paths": [
            r"C:\Program Files\Microsoft Office\root\Office16\EXCEL.EXE",
            r"C:\Program Files (x86)\Microsoft Office\root\Office16\EXCEL.EXE",
        ],
        "command": "excel"
    },
    "powerpoint": {
        "names": ["powerpoint", "microsoft powerpoint", "ppt", "ms powerpoint"],
        "paths": [
            r"C:\Program Files\Microsoft Office\root\Office16\POWERPNT.EXE",
            r"C:\Program Files (x86)\Microsoft Office\root\Office16\POWERPNT.EXE",
        ],
        "command": "powerpnt"
    },
    "outlook": {
        "names": ["outlook", "microsoft outlook", "email client"],
        "paths": [
            r"C:\Program Files\Microsoft Office\root\Office16\OUTLOOK.EXE",
        ],
        "command": "outlook"
    },
    
    # Utilities
    "calculator": {
        "names": ["calculator", "calc"],
        "paths": [],
        "command": "calc"
    },
    "paint": {
        "names": ["paint", "ms paint", "mspaint"],
        "paths": [r"C:\Windows\System32\mspaint.exe"],
        "command": "mspaint"
    },
    "snipping tool": {
        "names": ["snipping tool", "snip", "screenshot tool"],
        "paths": [],
        "command": "snippingtool"
    },
    "task manager": {
        "names": ["task manager", "taskmgr"],
        "paths": [r"C:\Windows\System32\Taskmgr.exe"],
        "command": "taskmgr"
    },
    "control panel": {
        "names": ["control panel", "settings"],
        "paths": [],
        "command": "control"
    },
    "file explorer": {
        "names": ["file explorer", "explorer", "my computer", "this pc", "files"],
        "paths": [r"C:\Windows\explorer.exe"],
        "command": "explorer"
    },
    
    # Media
    "spotify": {
        "names": ["spotify", "music"],
        "paths": [
            r"C:\Users\{user}\AppData\Roaming\Spotify\Spotify.exe",
        ],
        "command": "spotify"
    },
    "vlc": {
        "names": ["vlc", "vlc player", "media player"],
        "paths": [
            r"C:\Program Files\VideoLAN\VLC\vlc.exe",
            r"C:\Program Files (x86)\VideoLAN\VLC\vlc.exe",
        ],
        "command": "vlc"
    },
    
    # Communication
    "discord": {
        "names": ["discord"],
        "paths": [
            r"C:\Users\{user}\AppData\Local\Discord\app-*\Discord.exe",
        ],
        "command": "discord"
    },
    "telegram": {
        "names": ["telegram"],
        "paths": [
            r"C:\Users\{user}\AppData\Roaming\Telegram Desktop\Telegram.exe",
        ],
        "command": "telegram"
    },
    "whatsapp": {
        "names": ["whatsapp", "whats app"],
        "paths": [],
        "command": "whatsapp"  # Windows Store app
    },
    "zoom": {
        "names": ["zoom", "zoom meeting"],
        "paths": [
            r"C:\Users\{user}\AppData\Roaming\Zoom\bin\Zoom.exe",
        ],
        "command": "zoom"
    },
    "teams": {
        "names": ["teams", "microsoft teams", "ms teams"],
        "paths": [
            r"C:\Users\{user}\AppData\Local\Microsoft\Teams\current\Teams.exe",
        ],
        "command": "teams"
    },
}

# Special folders
SPECIAL_FOLDERS = {
    "desktop": os.path.join(os.path.expanduser("~"), "Desktop"),
    "documents": os.path.join(os.path.expanduser("~"), "Documents"),
    "downloads": os.path.join(os.path.expanduser("~"), "Downloads"),
    "pictures": os.path.join(os.path.expanduser("~"), "Pictures"),
    "music": os.path.join(os.path.expanduser("~"), "Music"),
    "videos": os.path.join(os.path.expanduser("~"), "Videos"),
    "home": os.path.expanduser("~"),
    "user": os.path.expanduser("~"),
}


# =====================================================
# DESKTOP AUTOMATION CLASS
# =====================================================

class DesktopAutomation:
    """
    Complete desktop automation for ARES.
    Controls applications, windows, keyboard, mouse, and system.
    """
    
    def __init__(self):
        self.username = os.getlogin() if IS_WINDOWS else os.environ.get("USER", "user")
        self.screenshot_folder = os.path.join(os.path.expanduser("~"), "Pictures", "ARES_Screenshots")
        
        # Ensure screenshot folder exists
        os.makedirs(self.screenshot_folder, exist_ok=True)
        
        print(f"✅ Desktop Automation initialized for user: {self.username}")
    
    # ===========================================
    # APPLICATION CONTROL
    # ===========================================
    
    def open_application(self, app_name: str) -> Tuple[bool, str]:
        """
        Open an application by name.
        
        Args:
            app_name: Name of the application (e.g., "chrome", "notepad")
            
        Returns:
            (success, message)
        """
        app_name_lower = app_name.lower().strip()
        
        # Find app in database
        app_info = None
        for key, info in APP_DATABASE.items():
            if app_name_lower in info["names"] or app_name_lower == key:
                app_info = info
                break
        
        if not app_info:
            # Try to open directly
            try:
                if IS_WINDOWS:
                    os.startfile(app_name)
                else:
                    subprocess.Popen([app_name])
                return True, f"Opened {app_name}"
            except:
                return False, f"I don't know how to open '{app_name}'. Please tell me the exact name."
        
        # Try paths first
        for path in app_info.get("paths", []):
            # Replace {user} with actual username
            path = path.replace("{user}", self.username)
            
            # Handle wildcards
            if "*" in path:
                from glob import glob
                matches = glob(path)
                if matches:
                    path = matches[0]
                else:
                    continue
            
            if os.path.exists(path):
                try:
                    subprocess.Popen([path])
                    return True, f"Opening {app_name}..."
                except Exception as e:
                    continue
        
        # Try command
        command = app_info.get("command")
        if command:
            try:
                if IS_WINDOWS:
                    subprocess.Popen(f"start {command}", shell=True)
                else:
                    subprocess.Popen([command])
                return True, f"Opening {app_name}..."
            except:
                pass
        
        return False, f"Could not open {app_name}. It may not be installed."
    
    def close_application(self, app_name: str) -> Tuple[bool, str]:
        """
        Close an application by name.
        """
        if not PSUTIL_AVAILABLE:
            return False, "Cannot close applications without psutil installed."
        
        app_name_lower = app_name.lower().strip()
        closed_count = 0
        
        # Get process names to look for
        process_names = [app_name_lower]
        
        for key, info in APP_DATABASE.items():
            if app_name_lower in info["names"] or app_name_lower == key:
                process_names.append(key)
                # Add exe name from paths
                for path in info.get("paths", []):
                    exe_name = os.path.basename(path).lower()
                    process_names.append(exe_name.replace(".exe", ""))
        
        # Find and terminate processes
        for proc in psutil.process_iter(['name', 'pid']):
            try:
                proc_name = proc.info['name'].lower().replace(".exe", "")
                if any(name in proc_name for name in process_names):
                    proc.terminate()
                    closed_count += 1
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                continue
        
        if closed_count > 0:
            return True, f"Closed {app_name} ({closed_count} process{'es' if closed_count > 1 else ''})"
        else:
            return False, f"No running instance of {app_name} found."
    
    def list_running_apps(self) -> List[str]:
        """Get list of running applications."""
        if not PSUTIL_AVAILABLE:
            return []
        
        apps = set()
        for proc in psutil.process_iter(['name']):
            try:
                name = proc.info['name']
                if name and not name.startswith("_"):
                    apps.add(name.replace(".exe", ""))
            except:
                continue
        
        return sorted(list(apps))
    
    # ===========================================
    # FOLDER OPERATIONS
    # ===========================================
    
    def open_folder(self, folder_name: str) -> Tuple[bool, str]:
        """
        Open a folder in file explorer.
        """
        folder_lower = folder_name.lower().strip()
        
        # Check special folders
        if folder_lower in SPECIAL_FOLDERS:
            path = SPECIAL_FOLDERS[folder_lower]
        else:
            # Try as direct path
            if os.path.exists(folder_name):
                path = folder_name
            elif os.path.exists(os.path.join(os.path.expanduser("~"), folder_name)):
                path = os.path.join(os.path.expanduser("~"), folder_name)
            else:
                return False, f"Folder '{folder_name}' not found."
        
        try:
            if IS_WINDOWS:
                os.startfile(path)
            else:
                subprocess.Popen(["xdg-open", path])
            return True, f"Opening {folder_name} folder..."
        except Exception as e:
            return False, f"Could not open folder: {e}"
    
    # ===========================================
    # WEB OPERATIONS
    # ===========================================
    
    def search_google(self, query: str) -> Tuple[bool, str]:
        """Search Google for a query."""
        encoded_query = urllib.parse.quote(query)
        url = f"https://www.google.com/search?q={encoded_query}"
        
        try:
            webbrowser.open(url)
            return True, f"Searching Google for: {query}"
        except Exception as e:
            return False, f"Could not open browser: {e}"
    
    def search_youtube(self, query: str) -> Tuple[bool, str]:
        """Search YouTube for a query."""
        encoded_query = urllib.parse.quote(query)
        url = f"https://www.youtube.com/results?search_query={encoded_query}"
        
        try:
            webbrowser.open(url)
            return True, f"Searching YouTube for: {query}"
        except Exception as e:
            return False, f"Could not open browser: {e}"
    
    def open_website(self, url: str) -> Tuple[bool, str]:
        """Open a website."""
        if not url.startswith(("http://", "https://")):
            url = "https://" + url
        
        try:
            webbrowser.open(url)
            return True, f"Opening {url}"
        except Exception as e:
            return False, f"Could not open website: {e}"
    
    # ===========================================
    # SCREENSHOT
    # ===========================================
    
    def take_screenshot(self, name: str = None) -> Tuple[bool, str]:
        """Take a screenshot and save it."""
        if not PYAUTOGUI_AVAILABLE:
            return False, "Screenshot requires pyautogui. Run: pip install pyautogui"
        
        try:
            # Generate filename
            timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            if name:
                filename = f"{name}_{timestamp}.png"
            else:
                filename = f"screenshot_{timestamp}.png"
            
            filepath = os.path.join(self.screenshot_folder, filename)
            
            # Take screenshot
            screenshot = pyautogui.screenshot()
            screenshot.save(filepath)
            
            return True, f"Screenshot saved: {filepath}"
        except Exception as e:
            return False, f"Could not take screenshot: {e}"
    
    # ===========================================
    # KEYBOARD CONTROL
    # ===========================================
    
    def type_text(self, text: str, interval: float = 0.02) -> Tuple[bool, str]:
        """Type text using keyboard."""
        if not PYAUTOGUI_AVAILABLE:
            return False, "Typing requires pyautogui."
        
        try:
            pyautogui.typewrite(text, interval=interval)
            return True, f"Typed: {text}"
        except Exception as e:
            return False, f"Could not type: {e}"
    
    def press_key(self, key: str) -> Tuple[bool, str]:
        """Press a keyboard key."""
        if not PYAUTOGUI_AVAILABLE:
            return False, "Key press requires pyautogui."
        
        try:
            pyautogui.press(key)
            return True, f"Pressed {key}"
        except Exception as e:
            return False, f"Could not press key: {e}"
    
    def hotkey(self, *keys) -> Tuple[bool, str]:
        """Press a keyboard shortcut."""
        if not PYAUTOGUI_AVAILABLE:
            return False, "Hotkey requires pyautogui."
        
        try:
            pyautogui.hotkey(*keys)
            return True, f"Pressed {'+'.join(keys)}"
        except Exception as e:
            return False, f"Could not press hotkey: {e}"
    
    # ===========================================
    # WINDOW CONTROL
    # ===========================================
    
    def minimize_all_windows(self) -> Tuple[bool, str]:
        """Minimize all windows (show desktop)."""
        if not PYAUTOGUI_AVAILABLE:
            return False, "Window control requires pyautogui."
        
        try:
            pyautogui.hotkey('win', 'd')
            return True, "Minimized all windows"
        except Exception as e:
            return False, f"Could not minimize windows: {e}"
    
    def maximize_window(self) -> Tuple[bool, str]:
        """Maximize current window."""
        if not PYAUTOGUI_AVAILABLE:
            return False, "Window control requires pyautogui."
        
        try:
            pyautogui.hotkey('win', 'up')
            return True, "Maximized window"
        except Exception as e:
            return False, f"Could not maximize window: {e}"
    
    def minimize_window(self) -> Tuple[bool, str]:
        """Minimize current window."""
        if not PYAUTOGUI_AVAILABLE:
            return False, "Window control requires pyautogui."
        
        try:
            pyautogui.hotkey('win', 'down')
            return True, "Minimized window"
        except Exception as e:
            return False, f"Could not minimize window: {e}"
    
    def close_window(self) -> Tuple[bool, str]:
        """Close current window."""
        if not PYAUTOGUI_AVAILABLE:
            return False, "Window control requires pyautogui."
        
        try:
            pyautogui.hotkey('alt', 'f4')
            return True, "Closed window"
        except Exception as e:
            return False, f"Could not close window: {e}"
    
    def switch_window(self) -> Tuple[bool, str]:
        """Switch to next window (Alt+Tab)."""
        if not PYAUTOGUI_AVAILABLE:
            return False, "Window control requires pyautogui."
        
        try:
            pyautogui.hotkey('alt', 'tab')
            return True, "Switched window"
        except Exception as e:
            return False, f"Could not switch window: {e}"
    
    # ===========================================
    # SYSTEM CONTROLS
    # ===========================================
    
    def lock_computer(self) -> Tuple[bool, str]:
        """Lock the computer."""
        try:
            if IS_WINDOWS:
                ctypes.windll.user32.LockWorkStation()
            else:
                subprocess.run(["gnome-screensaver-command", "-l"])
            return True, "Computer locked"
        except Exception as e:
            return False, f"Could not lock computer: {e}"
    
    def volume_up(self, times: int = 2) -> Tuple[bool, str]:
        """Increase volume."""
        if not PYAUTOGUI_AVAILABLE:
            return False, "Volume control requires pyautogui."
        
        try:
            for _ in range(times):
                pyautogui.press('volumeup')
            return True, "Volume increased"
        except Exception as e:
            return False, f"Could not change volume: {e}"
    
    def volume_down(self, times: int = 2) -> Tuple[bool, str]:
        """Decrease volume."""
        if not PYAUTOGUI_AVAILABLE:
            return False, "Volume control requires pyautogui."
        
        try:
            for _ in range(times):
                pyautogui.press('volumedown')
            return True, "Volume decreased"
        except Exception as e:
            return False, f"Could not change volume: {e}"
    
    def mute_volume(self) -> Tuple[bool, str]:
        """Mute/unmute volume."""
        if not PYAUTOGUI_AVAILABLE:
            return False, "Volume control requires pyautogui."
        
        try:
            pyautogui.press('volumemute')
            return True, "Volume muted/unmuted"
        except Exception as e:
            return False, f"Could not mute volume: {e}"
    
    def play_pause_media(self) -> Tuple[bool, str]:
        """Play/pause media."""
        if not PYAUTOGUI_AVAILABLE:
            return False, "Media control requires pyautogui."
        
        try:
            pyautogui.press('playpause')
            return True, "Media play/pause toggled"
        except Exception as e:
            return False, f"Could not control media: {e}"
    
    def next_track(self) -> Tuple[bool, str]:
        """Next media track."""
        if not PYAUTOGUI_AVAILABLE:
            return False, "Media control requires pyautogui."
        
        try:
            pyautogui.press('nexttrack')
            return True, "Next track"
        except Exception as e:
            return False, f"Could not control media: {e}"
    
    def previous_track(self) -> Tuple[bool, str]:
        """Previous media track."""
        if not PYAUTOGUI_AVAILABLE:
            return False, "Media control requires pyautogui."
        
        try:
            pyautogui.press('prevtrack')
            return True, "Previous track"
        except Exception as e:
            return False, f"Could not control media: {e}"
    
    # ===========================================
    # CLIPBOARD
    # ===========================================
    
    def copy_to_clipboard(self, text: str) -> Tuple[bool, str]:
        """Copy text to clipboard."""
        try:
            import pyperclip
            pyperclip.copy(text)
            return True, f"Copied to clipboard: {text[:50]}..."
        except ImportError:
            return False, "Clipboard requires pyperclip. Run: pip install pyperclip"
        except Exception as e:
            return False, f"Could not copy to clipboard: {e}"
    
    def paste_from_clipboard(self) -> Tuple[bool, str]:
        """Paste from clipboard."""
        if not PYAUTOGUI_AVAILABLE:
            return False, "Paste requires pyautogui."
        
        try:
            pyautogui.hotkey('ctrl', 'v')
            return True, "Pasted from clipboard"
        except Exception as e:
            return False, f"Could not paste: {e}"
    
    # ===========================================
    # SYSTEM INFO
    # ===========================================
    
    def get_time(self) -> str:
        """Get current time."""
        now = datetime.datetime.now()
        return now.strftime("%I:%M %p")  # e.g., "03:45 PM"
    
    def get_date(self) -> str:
        """Get current date."""
        now = datetime.datetime.now()
        return now.strftime("%A, %B %d, %Y")  # e.g., "Monday, January 20, 2025"
    
    def get_battery_status(self) -> str:
        """Get battery status."""
        if not PSUTIL_AVAILABLE:
            return "Battery status requires psutil."
        
        try:
            battery = psutil.sensors_battery()
            if battery:
                percent = battery.percent
                plugged = "charging" if battery.power_plugged else "not charging"
                return f"Battery is at {percent}% and {plugged}."
            else:
                return "No battery detected. This might be a desktop computer."
        except:
            return "Could not get battery status."
    
    def get_system_info(self) -> Dict:
        """Get system information."""
        info = {
            "os": platform.system(),
            "os_version": platform.version(),
            "machine": platform.machine(),
            "processor": platform.processor(),
            "username": self.username,
        }
        
        if PSUTIL_AVAILABLE:
            info["cpu_percent"] = psutil.cpu_percent()
            info["memory_percent"] = psutil.virtual_memory().percent
            info["disk_percent"] = psutil.disk_usage('/').percent if not IS_WINDOWS else psutil.disk_usage('C:').percent
        
        return info


# Create global instance
desktop = DesktopAutomation()
"""
=====================================================
ARES COMMAND PARSER - PRODUCTION READY
=====================================================
Intelligent parser that understands natural language
commands and routes them to appropriate actions.

This module converts spoken commands like:
- "Open Chrome" → open_app("chrome")
- "Search Google for Python tutorials" → search_google("Python tutorials")
- "Take a screenshot" → take_screenshot()
- "What time is it" → get_time()

Author: ARES AI Assistant
For: Shobutik Panja
=====================================================
"""

import re
from typing import Tuple, Optional, Dict, Any
from dataclasses import dataclass
from enum import Enum


class CommandType(Enum):
    """Types of commands ARES can execute."""
    
    # Application Control
    OPEN_APP = "open_app"
    CLOSE_APP = "close_app"
    SWITCH_APP = "switch_app"
    
    # Browser/Web
    SEARCH_GOOGLE = "search_google"
    SEARCH_YOUTUBE = "search_youtube"
    OPEN_WEBSITE = "open_website"
    
    # File/Folder
    OPEN_FOLDER = "open_folder"
    OPEN_FILE = "open_file"
    
    # Screenshot
    TAKE_SCREENSHOT = "take_screenshot"
    
    # Window Control
    MINIMIZE_WINDOW = "minimize_window"
    MAXIMIZE_WINDOW = "maximize_window"
    CLOSE_WINDOW = "close_window"
    MINIMIZE_ALL = "minimize_all"
    SWITCH_WINDOW = "switch_window"
    
    # System Control
    LOCK_COMPUTER = "lock_computer"
    SHUTDOWN = "shutdown"
    RESTART = "restart"
    SLEEP = "sleep"
    
    # Volume Control
    VOLUME_UP = "volume_up"
    VOLUME_DOWN = "volume_down"
    MUTE = "mute"
    UNMUTE = "unmute"
    
    # Media Control
    PLAY_PAUSE = "play_pause"
    NEXT_TRACK = "next_track"
    PREVIOUS_TRACK = "previous_track"
    STOP_MEDIA = "stop_media"
    
    # Keyboard
    TYPE_TEXT = "type_text"
    PRESS_KEY = "press_key"
    COPY = "copy"
    PASTE = "paste"
    UNDO = "undo"
    REDO = "redo"
    SELECT_ALL = "select_all"
    SAVE = "save"
    
    # Information
    GET_TIME = "get_time"
    GET_DATE = "get_date"
    GET_BATTERY = "get_battery"
    GET_SYSTEM_INFO = "get_system_info"
    LIST_RUNNING_APPS = "list_running_apps"
    
    # Conversation
    GREETING = "greeting"
    HELP = "help"
    STOP = "stop"
    UNKNOWN = "unknown"


@dataclass
class ParsedCommand:
    """Represents a parsed voice command."""
    command_type: CommandType
    parameters: Dict[str, Any]
    original_text: str
    confidence: float = 1.0


class CommandParser:
    """
    Natural language command parser for ARES.
    Converts spoken commands to actionable instructions.
    """
    
    # ===========================================
    # COMMAND PATTERNS
    # ===========================================
    
    # Each pattern: (regex, command_type, parameter_extractor)
    PATTERNS = [
        # ============ OPEN APPLICATIONS ============
        (r"(?:open|launch|start|run)\s+(?:the\s+)?(.+?)(?:\s+app(?:lication)?)?$", 
         CommandType.OPEN_APP, "app_name"),
        
        # ============ CLOSE APPLICATIONS ============
        (r"(?:close|quit|exit|kill|stop|end)\s+(?:the\s+)?(.+?)(?:\s+app(?:lication)?)?$", 
         CommandType.CLOSE_APP, "app_name"),
        
        # ============ GOOGLE SEARCH ============
        (r"(?:search|google|look up|find)\s+(?:for\s+|google\s+for\s+|on\s+google\s+)?(.+)$", 
         CommandType.SEARCH_GOOGLE, "query"),
        (r"google\s+(.+)$", 
         CommandType.SEARCH_GOOGLE, "query"),
        
        # ============ YOUTUBE SEARCH ============
        (r"(?:search|find|play|look for)\s+(?:on\s+)?youtube\s+(?:for\s+)?(.+)$", 
         CommandType.SEARCH_YOUTUBE, "query"),
        (r"youtube\s+(?:search\s+)?(?:for\s+)?(.+)$", 
         CommandType.SEARCH_YOUTUBE, "query"),
        
        # ============ OPEN WEBSITE ============
        (r"(?:open|go to|visit|navigate to)\s+(?:the\s+)?(?:website\s+)?(?:www\.)?(\S+\.(?:com|org|net|io|co|in|edu|gov)\S*)$", 
         CommandType.OPEN_WEBSITE, "url"),
        (r"(?:open|go to)\s+(\S+\.(?:com|org|net|io|co|in))\s*$", 
         CommandType.OPEN_WEBSITE, "url"),
        
        # ============ OPEN FOLDER ============
        (r"(?:open|show|go to)\s+(?:my\s+)?(?:the\s+)?(desktop|documents?|downloads?|pictures?|music|videos?|home|files?)\s*(?:folder)?$", 
         CommandType.OPEN_FOLDER, "folder_name"),
        (r"(?:open|show)\s+(?:the\s+)?folder\s+(.+)$", 
         CommandType.OPEN_FOLDER, "folder_name"),
        
        # ============ SCREENSHOT ============
        (r"(?:take|capture|grab|get)\s+(?:a\s+)?screenshot", 
         CommandType.TAKE_SCREENSHOT, None),
        (r"screenshot", 
         CommandType.TAKE_SCREENSHOT, None),
        
        # ============ WINDOW CONTROL ============
        (r"minimize\s+(?:this\s+|current\s+)?(?:all\s+)?window(?:s)?", 
         CommandType.MINIMIZE_WINDOW, None),
        (r"minimize\s+all(?:\s+windows)?", 
         CommandType.MINIMIZE_ALL, None),
        (r"show\s+(?:the\s+)?desktop", 
         CommandType.MINIMIZE_ALL, None),
        (r"maximize\s+(?:this\s+|current\s+)?window", 
         CommandType.MAXIMIZE_WINDOW, None),
        (r"(?:close|exit)\s+(?:this\s+|current\s+)?window", 
         CommandType.CLOSE_WINDOW, None),
        (r"switch\s+(?:to\s+)?(?:next\s+)?window", 
         CommandType.SWITCH_WINDOW, None),
        (r"alt\s*tab", 
         CommandType.SWITCH_WINDOW, None),
        (r"next\s+window", 
         CommandType.SWITCH_WINDOW, None),
        
        # ============ SYSTEM CONTROL ============
        (r"lock\s+(?:the\s+)?(?:computer|pc|screen|system)", 
         CommandType.LOCK_COMPUTER, None),
        (r"lock\s+(?:it)?$", 
         CommandType.LOCK_COMPUTER, None),
        (r"(?:shut\s*down|shutdown|power\s+off|turn\s+off)\s+(?:the\s+)?(?:computer|pc|system)?", 
         CommandType.SHUTDOWN, None),
        (r"restart\s+(?:the\s+)?(?:computer|pc|system)?", 
         CommandType.RESTART, None),
        (r"(?:sleep|hibernate)\s+(?:the\s+)?(?:computer|pc)?", 
         CommandType.SLEEP, None),
        
        # ============ VOLUME CONTROL ============
        (r"(?:turn\s+)?(?:volume\s+)?up(?:\s+volume)?", 
         CommandType.VOLUME_UP, None),
        (r"(?:increase|raise)\s+(?:the\s+)?volume", 
         CommandType.VOLUME_UP, None),
        (r"louder", 
         CommandType.VOLUME_UP, None),
        (r"(?:turn\s+)?(?:volume\s+)?down(?:\s+volume)?", 
         CommandType.VOLUME_DOWN, None),
        (r"(?:decrease|lower|reduce)\s+(?:the\s+)?volume", 
         CommandType.VOLUME_DOWN, None),
        (r"quieter", 
         CommandType.VOLUME_DOWN, None),
        (r"mute(?:\s+(?:the\s+)?(?:volume|sound|audio))?", 
         CommandType.MUTE, None),
        (r"unmute(?:\s+(?:the\s+)?(?:volume|sound|audio))?", 
         CommandType.UNMUTE, None),
        (r"(?:turn\s+)?(?:sound|audio)\s+(?:on|off)", 
         CommandType.MUTE, None),
        
        # ============ MEDIA CONTROL ============
        (r"(?:play|pause|resume)(?:\s+(?:the\s+)?music)?", 
         CommandType.PLAY_PAUSE, None),
        (r"(?:next|skip)\s+(?:track|song)", 
         CommandType.NEXT_TRACK, None),
        (r"(?:previous|last|back)\s+(?:track|song)", 
         CommandType.PREVIOUS_TRACK, None),
        (r"stop\s+(?:the\s+)?(?:music|playing|media)", 
         CommandType.STOP_MEDIA, None),
        
        # ============ KEYBOARD SHORTCUTS ============
        (r"(?:type|write|enter)\s+(.+)$", 
         CommandType.TYPE_TEXT, "text"),
        (r"copy(?:\s+(?:this|that|it))?", 
         CommandType.COPY, None),
        (r"paste(?:\s+(?:this|that|it))?", 
         CommandType.PASTE, None),
        (r"undo", 
         CommandType.UNDO, None),
        (r"redo", 
         CommandType.REDO, None),
        (r"select\s+all", 
         CommandType.SELECT_ALL, None),
        (r"save(?:\s+(?:this|file|document))?", 
         CommandType.SAVE, None),
        (r"press\s+(?:the\s+)?(.+)\s+key", 
         CommandType.PRESS_KEY, "key"),
        
        # ============ INFORMATION ============
        (r"(?:what(?:'s|\s+is)\s+)?(?:the\s+)?(?:current\s+)?time(?:\s+(?:is\s+it|now))?", 
         CommandType.GET_TIME, None),
        (r"(?:what(?:'s|\s+is)\s+)?(?:the\s+)?(?:today(?:'s)?\s+)?date(?:\s+(?:is\s+it|today))?", 
         CommandType.GET_DATE, None),
        (r"(?:what(?:'s|\s+is)\s+)?(?:the\s+)?(?:my\s+)?battery(?:\s+(?:status|level|percentage))?", 
         CommandType.GET_BATTERY, None),
        (r"(?:how\s+much\s+)?battery(?:\s+(?:do\s+i\s+have|left|remaining))?", 
         CommandType.GET_BATTERY, None),
        (r"(?:system|computer)\s+(?:info|information|status)", 
         CommandType.GET_SYSTEM_INFO, None),
        (r"(?:what(?:'s|\s+is)|show(?:\s+me)?|list)\s+(?:all\s+)?(?:the\s+)?(?:running|open)\s+(?:apps?|applications?|programs?)", 
         CommandType.LIST_RUNNING_APPS, None),
        (r"what\s+(?:apps?|applications?)\s+(?:are|is)\s+(?:running|open)", 
         CommandType.LIST_RUNNING_APPS, None),
        
        # ============ GREETINGS ============
        (r"^(?:hi|hello|hey|good\s+(?:morning|afternoon|evening))(?:\s+ares)?$", 
         CommandType.GREETING, None),
        
        # ============ HELP ============
        (r"(?:help|what\s+can\s+you\s+do|commands?|capabilities)", 
         CommandType.HELP, None),
        
        # ============ STOP ============
        (r"(?:stop|quit|exit|bye|goodbye|shut\s*up)(?:\s+(?:ares|listening))?$", 
         CommandType.STOP, None),
    ]
    
    # ===========================================
    # APP NAME CORRECTIONS
    # ===========================================
    
    APP_CORRECTIONS = {
        # Chrome variations
        "chrome": "chrome", "krom": "chrome", "crome": "chrome", "browser": "chrome",
        "google chrome": "chrome", "google": "chrome",
        
        # VS Code variations
        "vs code": "vscode", "visual studio code": "vscode", "code": "vscode",
        "vscode": "vscode", "vs": "vscode", "visual studio": "vscode",
        
        # Notepad variations
        "notepad": "notepad", "note pad": "notepad", "text editor": "notepad",
        "notepad plus plus": "notepad++", "notepad++": "notepad++",
        
        # File Explorer variations
        "file explorer": "explorer", "explorer": "explorer", "files": "explorer",
        "my computer": "explorer", "this pc": "explorer", "folder": "explorer",
        
        # Calculator variations
        "calculator": "calculator", "calc": "calculator", "calculate": "calculator",
        
        # Command Prompt variations
        "cmd": "cmd", "command prompt": "cmd", "terminal": "cmd",
        "command line": "cmd", "powershell": "powershell",
        
        # Office applications
        "word": "word", "microsoft word": "word", "ms word": "word",
        "excel": "excel", "microsoft excel": "excel", "spreadsheet": "excel",
        "powerpoint": "powerpoint", "ppt": "powerpoint", "presentation": "powerpoint",
        "outlook": "outlook", "email": "outlook",
        
        # Media
        "spotify": "spotify", "music": "spotify",
        "vlc": "vlc", "media player": "vlc", "video player": "vlc",
        
        # Communication
        "discord": "discord", "telegram": "telegram", "whatsapp": "whatsapp",
        "teams": "teams", "microsoft teams": "teams", "zoom": "zoom",
        
        # Development
        "git bash": "git bash", "bash": "git bash",
        
        # Utilities
        "paint": "paint", "task manager": "task manager", "control panel": "control panel",
        "settings": "settings", "snipping tool": "snipping tool",
    }
    
    # ===========================================
    # FOLDER NAME CORRECTIONS
    # ===========================================
    
    FOLDER_CORRECTIONS = {
        "desktop": "desktop",
        "document": "documents", "documents": "documents", "docs": "documents",
        "download": "downloads", "downloads": "downloads",
        "picture": "pictures", "pictures": "pictures", "photos": "pictures",
        "music": "music", "songs": "music",
        "video": "videos", "videos": "videos", "movies": "videos",
        "home": "home", "user": "home",
    }
    
    def __init__(self):
        # Compile regex patterns
        self.compiled_patterns = [
            (re.compile(pattern, re.IGNORECASE), cmd_type, param_name)
            for pattern, cmd_type, param_name in self.PATTERNS
        ]
    
    def parse(self, text: str) -> ParsedCommand:
        """
        Parse a voice command into an actionable instruction.
        
        Args:
            text: The spoken command text
            
        Returns:
            ParsedCommand object with command type and parameters
        """
        text = text.strip().lower()
        original_text = text
        
        # Clean up common speech recognition artifacts
        text = self._clean_text(text)
        
        # Try to match against patterns
        for pattern, cmd_type, param_name in self.compiled_patterns:
            match = pattern.search(text)
            if match:
                parameters = {}
                
                if param_name and match.groups():
                    param_value = match.group(1).strip()
                    
                    # Apply corrections based on parameter type
                    if param_name == "app_name":
                        param_value = self._correct_app_name(param_value)
                    elif param_name == "folder_name":
                        param_value = self._correct_folder_name(param_value)
                    elif param_name == "query":
                        param_value = self._clean_query(param_value)
                    
                    parameters[param_name] = param_value
                
                return ParsedCommand(
                    command_type=cmd_type,
                    parameters=parameters,
                    original_text=original_text,
                    confidence=0.9
                )
        
        # No pattern matched - unknown command
        return ParsedCommand(
            command_type=CommandType.UNKNOWN,
            parameters={"text": original_text},
            original_text=original_text,
            confidence=0.0
        )
    
    def _clean_text(self, text: str) -> str:
        """Clean up speech recognition artifacts."""
        # Remove filler words
        fillers = ["um", "uh", "like", "you know", "please", "can you", 
                   "could you", "would you", "i want you to", "i need you to"]
        for filler in fillers:
            text = text.replace(filler, " ")
        
        # Normalize spacing
        text = " ".join(text.split())
        
        return text
    
    def _correct_app_name(self, app_name: str) -> str:
        """Correct common speech recognition errors for app names."""
        app_name = app_name.strip().lower()
        
        # Direct correction lookup
        if app_name in self.APP_CORRECTIONS:
            return self.APP_CORRECTIONS[app_name]
        
        # Try partial match
        for key, value in self.APP_CORRECTIONS.items():
            if key in app_name or app_name in key:
                return value
        
        return app_name
    
    def _correct_folder_name(self, folder_name: str) -> str:
        """Correct common speech recognition errors for folder names."""
        folder_name = folder_name.strip().lower()
        
        if folder_name in self.FOLDER_CORRECTIONS:
            return self.FOLDER_CORRECTIONS[folder_name]
        
        return folder_name
    
    def _clean_query(self, query: str) -> str:
        """Clean up a search query."""
        # Remove "for" at the start
        query = re.sub(r"^for\s+", "", query)
        return query.strip()


# ===========================================
# COMMAND EXECUTOR
# ===========================================

class CommandExecutor:
    """
    Executes parsed commands using desktop automation.
    """
    
    def __init__(self):
        from automation.desktop_control import DesktopAutomation
        self.desktop = DesktopAutomation()
        self.parser = CommandParser()
    
    def execute(self, command: str) -> Tuple[bool, str]:
        """
        Execute a voice command.
        
        Args:
            command: The spoken command
            
        Returns:
            (success, response_message)
        """
        # Parse the command
        parsed = self.parser.parse(command)
        
        # Execute based on command type
        return self._execute_command(parsed)
    
    def _execute_command(self, cmd: ParsedCommand) -> Tuple[bool, str]:
        """Execute a parsed command."""
        
        ct = cmd.command_type
        params = cmd.parameters
        
        # ===========================================
        # APPLICATION COMMANDS
        # ===========================================
        
        if ct == CommandType.OPEN_APP:
            app_name = params.get("app_name", "")
            return self.desktop.open_application(app_name)
        
        elif ct == CommandType.CLOSE_APP:
            app_name = params.get("app_name", "")
            return self.desktop.close_application(app_name)
        
        # ===========================================
        # WEB COMMANDS
        # ===========================================
        
        elif ct == CommandType.SEARCH_GOOGLE:
            query = params.get("query", "")
            return self.desktop.search_google(query)
        
        elif ct == CommandType.SEARCH_YOUTUBE:
            query = params.get("query", "")
            return self.desktop.search_youtube(query)
        
        elif ct == CommandType.OPEN_WEBSITE:
            url = params.get("url", "")
            return self.desktop.open_website(url)
        
        # ===========================================
        # FILE/FOLDER COMMANDS
        # ===========================================
        
        elif ct == CommandType.OPEN_FOLDER:
            folder = params.get("folder_name", "")
            return self.desktop.open_folder(folder)
        
        # ===========================================
        # SCREENSHOT
        # ===========================================
        
        elif ct == CommandType.TAKE_SCREENSHOT:
            return self.desktop.take_screenshot()
        
        # ===========================================
        # WINDOW COMMANDS
        # ===========================================
        
        elif ct == CommandType.MINIMIZE_WINDOW:
            return self.desktop.minimize_window()
        
        elif ct == CommandType.MAXIMIZE_WINDOW:
            return self.desktop.maximize_window()
        
        elif ct == CommandType.CLOSE_WINDOW:
            return self.desktop.close_window()
        
        elif ct == CommandType.MINIMIZE_ALL:
            return self.desktop.minimize_all_windows()
        
        elif ct == CommandType.SWITCH_WINDOW:
            return self.desktop.switch_window()
        
        # ===========================================
        # SYSTEM COMMANDS
        # ===========================================
        
        elif ct == CommandType.LOCK_COMPUTER:
            return self.desktop.lock_computer()
        
        elif ct == CommandType.SHUTDOWN:
            return True, "I won't shut down without confirmation. Say 'confirm shutdown' to proceed."
        
        elif ct == CommandType.RESTART:
            return True, "I won't restart without confirmation. Say 'confirm restart' to proceed."
        
        # ===========================================
        # VOLUME COMMANDS
        # ===========================================
        
        elif ct == CommandType.VOLUME_UP:
            return self.desktop.volume_up()
        
        elif ct == CommandType.VOLUME_DOWN:
            return self.desktop.volume_down()
        
        elif ct == CommandType.MUTE or ct == CommandType.UNMUTE:
            return self.desktop.mute_volume()
        
        # ===========================================
        # MEDIA COMMANDS
        # ===========================================
        
        elif ct == CommandType.PLAY_PAUSE:
            return self.desktop.play_pause_media()
        
        elif ct == CommandType.NEXT_TRACK:
            return self.desktop.next_track()
        
        elif ct == CommandType.PREVIOUS_TRACK:
            return self.desktop.previous_track()
        
        # ===========================================
        # KEYBOARD COMMANDS
        # ===========================================
        
        elif ct == CommandType.TYPE_TEXT:
            text = params.get("text", "")
            return self.desktop.type_text(text)
        
        elif ct == CommandType.COPY:
            return self.desktop.hotkey('ctrl', 'c')
        
        elif ct == CommandType.PASTE:
            return self.desktop.hotkey('ctrl', 'v')
        
        elif ct == CommandType.UNDO:
            return self.desktop.hotkey('ctrl', 'z')
        
        elif ct == CommandType.REDO:
            return self.desktop.hotkey('ctrl', 'y')
        
        elif ct == CommandType.SELECT_ALL:
            return self.desktop.hotkey('ctrl', 'a')
        
        elif ct == CommandType.SAVE:
            return self.desktop.hotkey('ctrl', 's')
        
        # ===========================================
        # INFORMATION COMMANDS
        # ===========================================
        
        elif ct == CommandType.GET_TIME:
            time_str = self.desktop.get_time()
            return True, f"The current time is {time_str}"
        
        elif ct == CommandType.GET_DATE:
            date_str = self.desktop.get_date()
            return True, f"Today is {date_str}"
        
        elif ct == CommandType.GET_BATTERY:
            battery = self.desktop.get_battery_status()
            return True, battery
        
        elif ct == CommandType.GET_SYSTEM_INFO:
            info = self.desktop.get_system_info()
            msg = f"System: {info.get('os', 'Unknown')}\n"
            msg += f"CPU: {info.get('cpu_percent', 'N/A')}% used\n"
            msg += f"Memory: {info.get('memory_percent', 'N/A')}% used"
            return True, msg
        
        elif ct == CommandType.LIST_RUNNING_APPS:
            apps = self.desktop.list_running_apps()[:15]  # Top 15
            if apps:
                return True, f"Running apps: {', '.join(apps[:10])}..."
            else:
                return True, "Could not get running apps."
        
        # ===========================================
        # CONVERSATIONAL
        # ===========================================
        
        elif ct == CommandType.GREETING:
            import datetime
            hour = datetime.datetime.now().hour
            if hour < 12:
                greeting = "Good morning"
            elif hour < 18:
                greeting = "Good afternoon"
            else:
                greeting = "Good evening"
            return True, f"{greeting}, Shobutik! How can I help you?"
        
        elif ct == CommandType.HELP:
            return True, self._get_help_message()
        
        elif ct == CommandType.STOP:
            return True, "STOP_LISTENING"
        
        # ===========================================
        # UNKNOWN
        # ===========================================
        
        elif ct == CommandType.UNKNOWN:
            return False, f"I'm not sure how to do that. You said: '{cmd.original_text}'"
        
        return False, "Command not implemented yet."
    
    def _get_help_message(self) -> str:
        """Get help message with available commands."""
        return """Here's what I can do:

📱 APPS: "Open Chrome", "Close Notepad"
🔍 SEARCH: "Search Google for Python", "YouTube cat videos"
🌐 WEB: "Open github.com"
📁 FILES: "Open Downloads folder"
📸 SCREENSHOT: "Take a screenshot"
🪟 WINDOWS: "Minimize window", "Show desktop"
🔊 VOLUME: "Volume up", "Mute"
🎵 MEDIA: "Play", "Next track"
⌨️ TYPE: "Type hello world"
🔒 SYSTEM: "Lock computer"
⏰ INFO: "What time is it?", "Battery status"

Just speak naturally!"""


# Create global instance
command_executor = None

def get_executor() -> CommandExecutor:
    """Get or create command executor."""
    global command_executor
    if command_executor is None:
        command_executor = CommandExecutor()
    return command_executor


# ===========================================
# TEST
# ===========================================

if __name__ == "__main__":
    parser = CommandParser()
    
    test_commands = [
        "Open Chrome",
        "search google for python tutorials",
        "take a screenshot",
        "what time is it",
        "open my downloads folder",
        "close notepad",
        "volume up",
        "minimize all windows",
        "type hello world",
        "lock computer",
    ]
    
    print("Testing Command Parser")
    print("=" * 50)
    
    for cmd in test_commands:
        result = parser.parse(cmd)
        print(f"Input: '{cmd}'")
        print(f"  → Type: {result.command_type.value}")
        print(f"  → Params: {result.parameters}")
        print()
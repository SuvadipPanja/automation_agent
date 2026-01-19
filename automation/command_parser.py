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
    
    # Reminders & Alarms
    SET_REMINDER = "set_reminder"
    SET_ALARM = "set_alarm"
    SET_TIMER = "set_timer"
    LIST_REMINDERS = "list_reminders"
    DELETE_REMINDER = "delete_reminder"
    DELETE_ALL_REMINDERS = "delete_all_reminders"
    SNOOZE = "snooze"
    
    # Tasks & Scheduling
    RUN_TASK = "run_task"
    LIST_TASKS = "list_tasks"
    CREATE_SCHEDULE = "create_schedule"
    LIST_SCHEDULES = "list_schedules"
    DELETE_SCHEDULE = "delete_schedule"
    ENABLE_SCHEDULE = "enable_schedule"
    DISABLE_SCHEDULE = "disable_schedule"
    
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
        
        # ============ REMINDERS & ALARMS ============
        # Set reminder with duration: "remind me in 30 minutes to..."
        (r"(?:remind\s+me|set\s+(?:a\s+)?reminder)\s+(?:in\s+)?(.+)", 
         CommandType.SET_REMINDER, "reminder_text"),
        
        # Set alarm: "set alarm for 7am", "alarm at 7:30"
        (r"(?:set\s+(?:an?\s+)?alarm|alarm)\s+(?:for\s+|at\s+)?(.+)", 
         CommandType.SET_ALARM, "alarm_text"),
        (r"wake\s+(?:me\s+)?(?:up\s+)?(?:at\s+)?(.+)", 
         CommandType.SET_ALARM, "alarm_text"),
        
        # Set timer: "set timer for 10 minutes", "timer 5 minutes"
        (r"(?:set\s+(?:a\s+)?timer|timer)\s+(?:for\s+)?(.+)", 
         CommandType.SET_TIMER, "timer_text"),
        (r"(?:start\s+)?countdown\s+(?:for\s+)?(.+)", 
         CommandType.SET_TIMER, "timer_text"),
        
        # List reminders
        (r"(?:what|show|list|display)\s+(?:are\s+)?(?:my\s+)?(?:all\s+)?reminders?", 
         CommandType.LIST_REMINDERS, None),
        (r"(?:what|show|list)\s+(?:are\s+)?(?:my\s+)?(?:all\s+)?(?:alarms?|timers?)", 
         CommandType.LIST_REMINDERS, None),
        (r"(?:do\s+i\s+have\s+)?(?:any\s+)?reminders?", 
         CommandType.LIST_REMINDERS, None),
        
        # Delete reminders
        (r"(?:delete|remove|cancel|clear)\s+(?:all\s+)?(?:my\s+)?reminders?", 
         CommandType.DELETE_ALL_REMINDERS, None),
        (r"(?:delete|remove|cancel)\s+(?:reminder|alarm|timer)\s+(.+)", 
         CommandType.DELETE_REMINDER, "reminder_id"),
        
        # Snooze
        (r"snooze(?:\s+(?:for\s+)?(\d+)\s*(?:min(?:ute)?s?)?)?", 
         CommandType.SNOOZE, "snooze_minutes"),
        
        # ============ TASKS & SCHEDULING ============
        # Run task: "run morning routine", "execute backup task", "start work apps"
        (r"(?:run|execute|start|do|perform)\s+(?:the\s+)?(?:task\s+)?(.+?)(?:\s+task)?$", 
         CommandType.RUN_TASK, "task_name"),
        
        # List tasks
        (r"(?:show|list|what)\s+(?:are\s+)?(?:my\s+|the\s+|all\s+)?(?:available\s+)?tasks?", 
         CommandType.LIST_TASKS, None),
        (r"what\s+tasks\s+(?:can\s+you|do\s+you|are)", 
         CommandType.LIST_TASKS, None),
        
        # Create schedule: "schedule backup daily at 6pm", "schedule morning routine every day at 9am"
        (r"schedule\s+(.+?)\s+(daily|every\s+day|every\s+\d+\s*(?:hour|minute|min|hr)s?|every\s+(?:monday|tuesday|wednesday|thursday|friday|saturday|sunday|weekday)s?)\s*(?:at\s+)?(.+)?", 
         CommandType.CREATE_SCHEDULE, "schedule_params"),
        (r"(?:create|add|set)\s+(?:a\s+)?schedule\s+(?:for\s+)?(.+)", 
         CommandType.CREATE_SCHEDULE, "schedule_params"),
        
        # List schedules
        (r"(?:show|list|what)\s+(?:are\s+)?(?:my\s+|the\s+|all\s+)?schedules?", 
         CommandType.LIST_SCHEDULES, None),
        (r"(?:what|show)\s+(?:is|are)\s+scheduled", 
         CommandType.LIST_SCHEDULES, None),
        
        # Delete schedule
        (r"(?:delete|remove|cancel|clear)\s+(?:all\s+)?schedules?", 
         CommandType.DELETE_SCHEDULE, None),
        (r"(?:delete|remove|cancel)\s+schedule\s+(\d+)", 
         CommandType.DELETE_SCHEDULE, "schedule_index"),
        
        # Enable/disable schedule
        (r"(?:enable|activate|turn\s+on)\s+schedule\s+(\d+)", 
         CommandType.ENABLE_SCHEDULE, "schedule_index"),
        (r"(?:disable|deactivate|turn\s+off)\s+schedule\s+(\d+)", 
         CommandType.DISABLE_SCHEDULE, "schedule_index"),
        
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
        # REMINDER COMMANDS
        # ===========================================
        
        elif ct == CommandType.SET_REMINDER:
            return self._handle_set_reminder(params.get("reminder_text", ""), cmd.original_text)
        
        elif ct == CommandType.SET_ALARM:
            return self._handle_set_alarm(params.get("alarm_text", ""), cmd.original_text)
        
        elif ct == CommandType.SET_TIMER:
            return self._handle_set_timer(params.get("timer_text", ""), cmd.original_text)
        
        elif ct == CommandType.LIST_REMINDERS:
            return self._handle_list_reminders()
        
        elif ct == CommandType.DELETE_REMINDER:
            reminder_id = params.get("reminder_id", "")
            return self._handle_delete_reminder(reminder_id)
        
        elif ct == CommandType.DELETE_ALL_REMINDERS:
            return self._handle_delete_all_reminders()
        
        elif ct == CommandType.SNOOZE:
            minutes = params.get("snooze_minutes", "5")
            return self._handle_snooze(minutes)
        
        # ===========================================
        # TASK & SCHEDULE COMMANDS
        # ===========================================
        
        elif ct == CommandType.RUN_TASK:
            task_name = params.get("task_name", "")
            return self._handle_run_task(task_name)
        
        elif ct == CommandType.LIST_TASKS:
            return self._handle_list_tasks()
        
        elif ct == CommandType.CREATE_SCHEDULE:
            schedule_params = params.get("schedule_params", "")
            return self._handle_create_schedule(schedule_params, cmd.original_text)
        
        elif ct == CommandType.LIST_SCHEDULES:
            return self._handle_list_schedules()
        
        elif ct == CommandType.DELETE_SCHEDULE:
            schedule_index = params.get("schedule_index", "")
            return self._handle_delete_schedule(schedule_index, cmd.original_text)
        
        elif ct == CommandType.ENABLE_SCHEDULE:
            schedule_index = params.get("schedule_index", "")
            return self._handle_enable_schedule(schedule_index, True)
        
        elif ct == CommandType.DISABLE_SCHEDULE:
            schedule_index = params.get("schedule_index", "")
            return self._handle_enable_schedule(schedule_index, False)
        
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
    
    # ===========================================
    # REMINDER HANDLERS
    # ===========================================
    
    def _handle_set_reminder(self, text: str, original: str) -> Tuple[bool, str]:
        """Handle setting a reminder."""
        try:
            from automation.reminders import get_reminder_manager, TimeParser
            manager = get_reminder_manager()
            
            # Extract message first
            message = TimeParser.extract_message(original)
            
            # Try to parse duration (in X minutes/hours)
            duration = TimeParser.parse_relative(text)
            if duration:
                hours = duration.get("hours", 0)
                minutes = duration.get("minutes", 0)
                seconds = duration.get("seconds", 0)
                
                if hours > 0 or minutes > 0 or seconds > 0:
                    reminder = manager.add_relative(
                        message,
                        hours=hours,
                        minutes=minutes,
                        seconds=seconds
                    )
                    time_str = reminder.time_until()
                    return True, f"📝 Reminder set: '{message}' in {time_str}."
            
            # Try to parse absolute time (at X:XX)
            time_info = TimeParser.parse_absolute(text)
            if time_info:
                reminder = manager.add_at_time(
                    message,
                    hour=time_info["hour"],
                    minute=time_info["minute"]
                )
                time_str = reminder.trigger_time.strftime("%I:%M %p")
                date_str = "today" if reminder.trigger_time.date() == __import__('datetime').datetime.now().date() else "tomorrow"
                return True, f"📝 Reminder: '{message}' at {time_str} {date_str}."
            
            return False, "I couldn't understand the time. Try: 'remind me in 30 minutes to take a break' or 'remind me at 5pm to call mom'"
            
        except Exception as e:
            return False, f"Could not set reminder: {e}"
    
    def _handle_set_alarm(self, text: str, original: str) -> Tuple[bool, str]:
        """Handle setting an alarm."""
        try:
            from automation.reminders import get_reminder_manager, TimeParser
            manager = get_reminder_manager()
            
            time_info = TimeParser.parse_absolute(text)
            if time_info:
                recurring = 'daily' in text.lower() or 'every' in text.lower()
                alarm = manager.set_alarm(
                    hour=time_info["hour"],
                    minute=time_info["minute"],
                    recurring=recurring
                )
                
                time_str = alarm.trigger_time.strftime("%I:%M %p")
                rec_str = " (daily)" if recurring else ""
                return True, f"⏰ Alarm set for {time_str}{rec_str}!"
            
            return False, "I couldn't understand the time. Try: 'set alarm for 7am' or 'alarm at 14:30'"
            
        except Exception as e:
            return False, f"Could not set alarm: {e}"
    
    def _handle_set_timer(self, text: str, original: str) -> Tuple[bool, str]:
        """Handle setting a timer."""
        try:
            from automation.reminders import get_reminder_manager, TimeParser
            manager = get_reminder_manager()
            
            duration = TimeParser.parse_relative(text)
            if duration:
                hours = duration.get("hours", 0)
                minutes = duration.get("minutes", 0)
                seconds = duration.get("seconds", 0)
                
                total_minutes = hours * 60 + minutes
                
                if total_minutes > 0 or seconds > 0:
                    timer = manager.set_timer(total_minutes, seconds)
                    time_str = timer.time_until()
                    return True, f"⏱️ Timer set for {time_str}!"
            
            return False, "I couldn't understand the duration. Try: 'set timer for 10 minutes' or 'timer 30 seconds'"
            
        except Exception as e:
            return False, f"Could not set timer: {e}"
    
    def _handle_list_reminders(self) -> Tuple[bool, str]:
        """Handle listing reminders."""
        try:
            from automation.reminders import get_reminder_manager
            manager = get_reminder_manager()
            return True, manager.format_list()
        except Exception as e:
            return False, f"Could not list reminders: {e}"
    
    def _handle_delete_reminder(self, reminder_id: str) -> Tuple[bool, str]:
        """Handle deleting a specific reminder."""
        try:
            from automation.reminders import get_reminder_manager
            manager = get_reminder_manager()
            
            # Try to delete by index if it's a number
            try:
                index = int(reminder_id.strip())
                if manager.delete_by_index(index):
                    return True, f"🗑️ Deleted reminder {index}."
                return False, f"Reminder {index} not found."
            except ValueError:
                pass
            
            # Try to delete by ID
            if manager.delete(reminder_id.strip()):
                return True, f"🗑️ Reminder deleted."
            return False, f"Could not find reminder: {reminder_id}"
            
        except Exception as e:
            return False, f"Could not delete reminder: {e}"
    
    def _handle_delete_all_reminders(self) -> Tuple[bool, str]:
        """Handle deleting all reminders."""
        try:
            from automation.reminders import get_reminder_manager
            manager = get_reminder_manager()
            
            count = manager.clear_all()
            
            if count > 0:
                return True, f"🗑️ Deleted {count} reminder(s)."
            else:
                return True, "No reminders to delete."
            
        except Exception as e:
            return False, f"Could not delete reminders: {e}"
    
    def _handle_snooze(self, minutes_str: str) -> Tuple[bool, str]:
        """Handle snoozing a reminder."""
        try:
            from automation.reminders import get_reminder_manager
            manager = get_reminder_manager()
            
            minutes = 5  # Default
            if minutes_str:
                try:
                    minutes = int(minutes_str)
                except:
                    pass
            
            # Get recently triggered reminders
            triggered = manager.get_triggered()
            
            if triggered:
                reminder = triggered[-1]
                if manager.snooze(reminder.id, minutes):
                    return True, f"😴 Snoozed for {minutes} minutes."
            
            return False, "No recent reminder to snooze."
            
        except Exception as e:
            return False, f"Could not snooze: {e}"
    
    def _extract_reminder_message(self, text: str) -> str:
        """Extract the reminder message from text."""
        import re
        
        # Remove common patterns
        patterns = [
            r'remind\s+me\s+',
            r'set\s+(?:a\s+)?reminder\s+',
            r'in\s+\d+\s*(?:hour|hr|h|minute|min|m|second|sec|s)s?\s*',
            r'at\s+\d{1,2}(?::\d{2})?\s*(?:am|pm)?\s*',
            r'to\s+',
            r'that\s+',
            r'tomorrow\s*',
        ]
        
        result = text.lower()
        for pattern in patterns:
            result = re.sub(pattern, '', result, flags=re.IGNORECASE)
        
        result = result.strip(' .,')
        
        return result if result else "Reminder"
    
    # ===========================================
    # TASK & SCHEDULE HANDLERS
    # ===========================================
    
    def _handle_run_task(self, task_name: str) -> Tuple[bool, str]:
        """Handle running a task by name."""
        try:
            from automation.tasks import get_task_manager
            manager = get_task_manager()
            
            # Clean task name
            task_name = task_name.strip().lower()
            task_name = re.sub(r'\s+task$', '', task_name)
            
            # Try to find and run task
            result = manager.run_task_by_name(task_name)
            
            if result:
                if result.status == "completed":
                    msg = f"✅ Task '{result.task_name}' completed!"
                    if result.speak_text:
                        msg += f"\n{result.speak_text}"
                    return True, msg
                elif result.status == "skipped":
                    return False, f"⚠️ Task '{result.task_name}' is disabled."
                else:
                    return False, f"❌ Task failed: {result.message}"
            else:
                # List similar tasks
                tasks = manager.get_all()
                task_names = [t.name for t in tasks[:5]]
                return False, f"Task not found: '{task_name}'. Available: {', '.join(task_names)}"
            
        except Exception as e:
            return False, f"Could not run task: {e}"
    
    def _handle_list_tasks(self) -> Tuple[bool, str]:
        """Handle listing available tasks."""
        try:
            from automation.tasks import get_task_manager
            manager = get_task_manager()
            return True, manager.format_list()
        except Exception as e:
            return False, f"Could not list tasks: {e}"
    
    def _handle_create_schedule(self, params: str, original: str) -> Tuple[bool, str]:
        """Handle creating a schedule."""
        try:
            from automation.tasks import get_task_manager
            from automation.scheduler import get_scheduler, ScheduleParser
            
            task_manager = get_task_manager()
            scheduler = get_scheduler()
            
            text = original.lower()
            
            # Parse schedule time
            schedule_info = ScheduleParser.parse(text)
            
            if not schedule_info:
                return False, "I couldn't understand the schedule. Try: 'schedule morning routine daily at 9am'"
            
            # Find task name in the command
            # Pattern: "schedule <task_name> <schedule>"
            task_name = None
            
            # Try common patterns
            patterns = [
                r'schedule\s+(.+?)\s+(?:daily|every|at\s+\d)',
                r'schedule\s+(.+?)\s+(?:on\s+)',
            ]
            
            for pattern in patterns:
                match = re.search(pattern, text)
                if match:
                    task_name = match.group(1).strip()
                    break
            
            if not task_name:
                return False, "Please specify which task to schedule. Try: 'schedule morning routine daily at 9am'"
            
            # Find the task
            task = task_manager.get_by_name(task_name)
            if not task:
                return False, f"Task not found: '{task_name}'. Say 'list tasks' to see available tasks."
            
            # Create schedule based on type
            if schedule_info["type"] == "daily":
                schedule = scheduler.create_daily_schedule(
                    task_id=task.id,
                    task_name=task.name,
                    hour=schedule_info["hour"],
                    minute=schedule_info.get("minute", 0)
                )
                time_str = f"{schedule_info['hour']:02d}:{schedule_info.get('minute', 0):02d}"
                return True, f"📅 Scheduled '{task.name}' daily at {time_str}"
            
            elif schedule_info["type"] == "interval":
                schedule = scheduler.create_interval_schedule(
                    task_id=task.id,
                    task_name=task.name,
                    minutes=schedule_info["minutes"]
                )
                mins = schedule_info["minutes"]
                if mins >= 60:
                    time_str = f"{mins // 60} hour{'s' if mins >= 120 else ''}"
                else:
                    time_str = f"{mins} minute{'s' if mins > 1 else ''}"
                return True, f"📅 Scheduled '{task.name}' every {time_str}"
            
            elif schedule_info["type"] == "weekly":
                schedule = scheduler.create_weekly_schedule(
                    task_id=task.id,
                    task_name=task.name,
                    days=schedule_info["days"],
                    hour=schedule_info["hour"],
                    minute=schedule_info.get("minute", 0)
                )
                day_names = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']
                days_str = ', '.join([day_names[d] for d in schedule_info["days"]])
                return True, f"📅 Scheduled '{task.name}' on {days_str}"
            
            return False, "Could not create schedule."
            
        except Exception as e:
            return False, f"Could not create schedule: {e}"
    
    def _handle_list_schedules(self) -> Tuple[bool, str]:
        """Handle listing schedules."""
        try:
            from automation.scheduler import get_scheduler
            scheduler = get_scheduler()
            return True, scheduler.format_list()
        except Exception as e:
            return False, f"Could not list schedules: {e}"
    
    def _handle_delete_schedule(self, index_str: str, original: str) -> Tuple[bool, str]:
        """Handle deleting a schedule."""
        try:
            from automation.scheduler import get_scheduler
            scheduler = get_scheduler()
            
            # Check if deleting all
            if 'all' in original.lower():
                count = scheduler.clear_all()
                return True, f"🗑️ Deleted {count} schedule(s)."
            
            # Delete by index
            if index_str:
                try:
                    index = int(index_str)
                    if scheduler.delete_by_index(index):
                        return True, f"🗑️ Deleted schedule {index}."
                    return False, f"Schedule {index} not found."
                except ValueError:
                    pass
            
            return False, "Specify which schedule to delete (e.g., 'delete schedule 1')."
            
        except Exception as e:
            return False, f"Could not delete schedule: {e}"
    
    def _handle_enable_schedule(self, index_str: str, enable: bool) -> Tuple[bool, str]:
        """Handle enabling/disabling a schedule."""
        try:
            from automation.scheduler import get_scheduler
            scheduler = get_scheduler()
            
            if not index_str:
                return False, f"Specify which schedule to {'enable' if enable else 'disable'}."
            
            try:
                index = int(index_str)
                schedules = scheduler.get_all()
                
                if 1 <= index <= len(schedules):
                    schedule_id = schedules[index - 1].id
                    if scheduler.enable(schedule_id, enable):
                        action = "enabled" if enable else "disabled"
                        return True, f"✅ Schedule {index} {action}."
                
                return False, f"Schedule {index} not found."
            except ValueError:
                return False, "Invalid schedule number."
            
        except Exception as e:
            return False, f"Could not modify schedule: {e}"
    
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

⏰ REMINDERS:
• "Remind me in 30 minutes to take a break"
• "Set alarm for 7am"
• "Set timer for 10 minutes"
• "Show my reminders"

📋 TASKS:
• "Run morning routine"
• "Run focus mode"
• "Show tasks"

📅 SCHEDULES:
• "Schedule morning routine daily at 9am"
• "Schedule break reminder every 2 hours"
• "Show schedules"
• "Delete schedule 1"

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
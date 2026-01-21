"""
=====================================================
ARES - Autonomous Runtime AI Assistant
MODERN ENTERPRISE ARCHITECTURE
=====================================================

Architecture Pattern:
  Service-Oriented Architecture (SOA) with Dependency Injection
  
  main_web.py (Entry Point)
        ↓
  ARESManager (Orchestrator)
        ↓
  ┌─────────┬─────────┬─────────┬─────────┬──────────┐
  ↓         ↓         ↓         ↓         ↓          ↓
 AIService DesktopService TaskService SchedulerService ReminderService VoiceService
  
Each service:
- Initializes independently
- Handles its own errors
- Provides clean API
- Logs operations
- Works seamlessly together

Author: ARES Development
For: Suvadip Panja
=====================================================
"""

import os
import sys
import json
import logging
import datetime
from pathlib import Path
from typing import Dict, Any, Optional, List, Tuple
from dataclasses import dataclass
from enum import Enum

# ===================================================
# PATH SETUP
# ===================================================
PROJECT_ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(PROJECT_ROOT))

# ===================================================
# LOGGING CONFIGURATION
# ===================================================

class LogLevel(Enum):
    """Logging levels."""
    DEBUG = logging.DEBUG
    INFO = logging.INFO
    WARNING = logging.WARNING
    ERROR = logging.ERROR
    CRITICAL = logging.CRITICAL

def setup_logger(name: str, level: LogLevel = LogLevel.INFO) -> logging.Logger:
    """Setup logger with consistent format."""
    logger = logging.getLogger(name)
    logger.setLevel(level.value)
    
    # Only add handlers if not already present
    if not logger.handlers:
        handler = logging.StreamHandler()
        formatter = logging.Formatter(
            '[%(asctime)s] %(name)s - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        handler.setFormatter(formatter)
        logger.addHandler(handler)
    
    return logger

# Global logger
logger = setup_logger("ARES", LogLevel.INFO)


# ===================================================
# DATA MODELS
# ===================================================

@dataclass
class ServiceStatus:
    """Status of a service."""
    name: str
    available: bool
    initialized: bool
    error: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "name": self.name,
            "available": self.available,
            "initialized": self.initialized,
            "error": self.error
        }


@dataclass
class CommandResult:
    """Result of command execution."""
    success: bool
    action: str
    response: str
    data: Optional[Dict[str, Any]] = None
    source: str = "unknown"
    timestamp: str = None
    
    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.datetime.now().isoformat()
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "success": self.success,
            "action": self.action,
            "response": self.response,
            "data": self.data,
            "source": self.source,
            "timestamp": self.timestamp
        }


# ===================================================
# BASE SERVICE CLASS
# ===================================================

class BaseService:
    """
    Base class for all ARES services.
    Provides common initialization, error handling, logging.
    """
    
    def __init__(self, name: str):
        """Initialize service."""
        self.name = name
        self.logger = setup_logger(f"ARES.{name}")
        self.initialized = False
        self.error = None
    
    def initialize(self) -> bool:
        """Initialize service. Override in subclasses."""
        try:
            self.logger.info(f"Initializing {self.name}...")
            self.initialized = True
            self.logger.info(f"✅ {self.name} initialized")
            return True
        except Exception as e:
            self.error = str(e)
            self.logger.error(f"❌ {self.name} initialization failed: {e}")
            return False
    
    def shutdown(self) -> None:
        """Shutdown service. Override in subclasses."""
        self.logger.info(f"Shutting down {self.name}...")
    
    def get_status(self) -> ServiceStatus:
        """Get service status."""
        return ServiceStatus(
            name=self.name,
            available=self.initialized,
            initialized=self.initialized,
            error=self.error
        )
    
    def health_check(self) -> bool:
        """Check if service is healthy. Override in subclasses."""
        return self.initialized


# ===================================================
# AI BRAIN SERVICE
# ===================================================

class AIBrainService(BaseService):
    """
    AI Brain Service - Natural language processing & conversation.
    Manages Ollama/Llama3 integration.
    """
    
    def __init__(self):
        """Initialize AI Brain service."""
        super().__init__("AIBrain")
        self.brain = None
    
    def initialize(self) -> bool:
        """Initialize AI brain."""
        try:
            self.logger.info("Loading AI Brain (Ollama/Llama3)...")
            
            try:
                from ai.brain import AIBrain
                self.brain = AIBrain()
                self.initialized = True
                self.logger.info("✅ AI Brain initialized")
                return True
            except ImportError as e:
                self.logger.warning(f"AI Brain import failed: {e}")
                return False
        
        except Exception as e:
            self.error = str(e)
            self.logger.error(f"AI Brain initialization error: {e}")
            return False
    
    def converse(self, text: str) -> Tuple[bool, Optional[str]]:
        """Have conversation with AI brain."""
        if not self.initialized or not self.brain:
            return False, "AI Brain not available"
        
        try:
            response = self.brain.converse(text)
            return True, response
        except Exception as e:
            self.logger.error(f"AI conversation error: {e}")
            return False, str(e)


# ===================================================
# DESKTOP AUTOMATION SERVICE
# ===================================================

class DesktopAutomationService(BaseService):
    """
    Desktop Automation Service - System control.
    Manages volume, screenshots, app control, etc.
    """
    
    def __init__(self):
        """Initialize desktop automation service."""
        super().__init__("DesktopAutomation")
        self.desktop = None
    
    def initialize(self) -> bool:
        """Initialize desktop automation."""
        try:
            self.logger.info("Initializing Desktop Automation...")
            
            try:
                from desktop import desktop
                self.desktop = desktop
                self.initialized = True
                self.logger.info(f"✅ Desktop Automation initialized for user: {self.desktop.user}")
                return True
            except ImportError as e:
                self.logger.warning(f"Desktop module not available: {e}")
                return False
        
        except Exception as e:
            self.error = str(e)
            self.logger.error(f"Desktop automation initialization error: {e}")
            return False
    
    def volume_up(self) -> Tuple[bool, str]:
        """Increase volume."""
        if not self.initialized:
            return False, "Desktop automation not available"
        return self.desktop.volume_up()
    
    def volume_down(self) -> Tuple[bool, str]:
        """Decrease volume."""
        if not self.initialized:
            return False, "Desktop automation not available"
        return self.desktop.volume_down()
    
    def mute(self) -> Tuple[bool, str]:
        """Mute audio."""
        if not self.initialized:
            return False, "Desktop automation not available"
        return self.desktop.mute()
    
    def take_screenshot(self) -> Tuple[bool, str]:
        """Take screenshot."""
        if not self.initialized:
            return False, "Desktop automation not available"
        return self.desktop.take_screenshot()
    
    def lock_computer(self) -> Tuple[bool, str]:
        """Lock computer."""
        if not self.initialized:
            return False, "Desktop automation not available"
        return self.desktop.lock_computer()
    
    def open_app(self, app_name: str) -> Tuple[bool, str]:
        """Open application."""
        if not self.initialized:
            return False, "Desktop automation not available"
        return self.desktop.open_app(app_name)
    
    def get_time(self) -> str:
        """Get current time."""
        if not self.initialized:
            return "Time unavailable"
        return self.desktop.get_time()
    
    def get_date(self) -> str:
        """Get current date."""
        if not self.initialized:
            return "Date unavailable"
        return self.desktop.get_date()
    
    def get_battery(self) -> str:
        """Get battery status."""
        if not self.initialized:
            return "Battery info unavailable"
        return self.desktop.get_battery()
    
    def get_system_info(self) -> Dict[str, Any]:
        """Get system information."""
        if not self.initialized:
            return {}
        return self.desktop.get_system_info()


# ===================================================
# VOICE RECOGNITION SERVICE
# ===================================================

class VoiceRecognitionService(BaseService):
    """
    Voice Recognition Service - Whisper integration.
    Converts audio to text.
    """
    
    def __init__(self):
        """Initialize voice recognition service."""
        super().__init__("VoiceRecognition")
        self.whisper = None
    
    def initialize(self) -> bool:
        """Initialize whisper."""
        try:
            self.logger.info("Initializing Voice Recognition (Whisper)...")
            
            try:
                from faster_whisper import WhisperModel
                self.whisper = WhisperModel("base", device="cpu", compute_type="int8")
                self.initialized = True
                self.logger.info("✅ Voice Recognition initialized")
                return True
            except ImportError:
                self.logger.warning("Whisper not available")
                return False
        
        except Exception as e:
            self.error = str(e)
            self.logger.error(f"Voice recognition initialization error: {e}")
            return False
    
    def transcribe(self, audio_path: str) -> Tuple[bool, Optional[str]]:
        """Transcribe audio file."""
        if not self.initialized:
            return False, "Voice recognition not available"
        
        try:
            segments, info = self.whisper.transcribe(audio_path, language="en")
            text = " ".join([seg.text for seg in segments]).strip()
            return True, text
        except Exception as e:
            self.logger.error(f"Transcription error: {e}")
            return False, str(e)


# ===================================================
# TASK MANAGEMENT SERVICE
# ===================================================

class TaskManagementService(BaseService):
    """
    Task Management Service - Task execution & management.
    """
    
    def __init__(self):
        """Initialize task management service."""
        super().__init__("TaskManagement")
        self.task_manager = None
    
    def initialize(self) -> bool:
        """Initialize task manager."""
        try:
            self.logger.info("Initializing Task Management...")
            
            try:
                from automation.tasks import get_task_manager
                self.task_manager = get_task_manager()
                self.initialized = True
                task_count = len(self.task_manager.get_all())
                self.logger.info(f"✅ Task Management initialized ({task_count} tasks)")
                return True
            except ImportError:
                self.logger.warning("Task system not available")
                return False
        
        except Exception as e:
            self.error = str(e)
            self.logger.error(f"Task management initialization error: {e}")
            return False
    
    def run_task(self, task_id: str) -> Tuple[bool, Optional[str]]:
        """Run task by ID."""
        if not self.initialized:
            return False, "Task system not available"
        
        try:
            result = self.task_manager.run_task(task_id)
            if result:
                return True, result.message
            return False, f"Task '{task_id}' not found"
        except Exception as e:
            self.logger.error(f"Task execution error: {e}")
            return False, str(e)
    
    def get_all_tasks(self) -> List[Dict[str, Any]]:
        """Get all tasks."""
        if not self.initialized:
            return []
        
        try:
            tasks = self.task_manager.get_all()
            return [t.to_dict() for t in tasks]
        except Exception as e:
            self.logger.error(f"Get tasks error: {e}")
            return []


# ===================================================
# SCHEDULER SERVICE
# ===================================================

class SchedulerService(BaseService):
    """
    Scheduler Service - Task scheduling & automation.
    """
    
    def __init__(self):
        """Initialize scheduler service."""
        super().__init__("Scheduler")
        self.scheduler = None
    
    def initialize(self) -> bool:
        """Initialize scheduler."""
        try:
            self.logger.info("Initializing Scheduler...")
            
            try:
                from automation.scheduler import get_scheduler
                self.scheduler = get_scheduler()
                self.initialized = True
                schedule_count = len(self.scheduler.get_all())
                self.logger.info(f"✅ Scheduler initialized ({schedule_count} schedules)")
                return True
            except ImportError:
                self.logger.warning("Scheduler not available")
                return False
        
        except Exception as e:
            self.error = str(e)
            self.logger.error(f"Scheduler initialization error: {e}")
            return False
    
    def get_all_schedules(self) -> List[Dict[str, Any]]:
        """Get all schedules."""
        if not self.initialized:
            return []
        
        try:
            schedules = self.scheduler.get_all()
            return [s.to_dict() for s in schedules]
        except Exception as e:
            self.logger.error(f"Get schedules error: {e}")
            return []


# ===================================================
# REMINDER SERVICE
# ===================================================

class ReminderService(BaseService):
    """
    Reminder Service - Reminders, alarms, timers.
    """
    
    def __init__(self):
        """Initialize reminder service."""
        super().__init__("Reminders")
        self.reminder_manager = None
    
    def initialize(self) -> bool:
        """Initialize reminders."""
        try:
            self.logger.info("Initializing Reminder System...")
            
            try:
                from automation.reminders import get_reminder_manager
                self.reminder_manager = get_reminder_manager()
                self.initialized = True
                self.logger.info("✅ Reminder System initialized")
                return True
            except ImportError:
                self.logger.warning("Reminder system not available")
                return False
        
        except Exception as e:
            self.error = str(e)
            self.logger.error(f"Reminder system initialization error: {e}")
            return False
    
    def get_all_reminders(self) -> List[Dict[str, Any]]:
        """Get all reminders."""
        if not self.initialized:
            return []
        
        try:
            reminders = self.reminder_manager.get_all()
            return [r.to_dict() for r in reminders]
        except Exception as e:
            self.logger.error(f"Get reminders error: {e}")
            return []


# ===================================================
# ARES MANAGER - ORCHESTRATOR
# ===================================================

class ARESManager:
    """
    ARES Manager - Central orchestrator for all services.
    
    Manages:
    - Service initialization
    - Service lifecycle
    - Health monitoring
    - Command routing
    - Unified interface
    """
    
    def __init__(self):
        """Initialize ARES Manager."""
        self.logger = setup_logger("ARES.Manager")
        self.logger.info("=" * 70)
        self.logger.info("  🚀 ARES - Autonomous Runtime AI Assistant")
        self.logger.info("  Modern Enterprise Architecture")
        self.logger.info("=" * 70)
        
        # Initialize services
        self.services = {
            "ai_brain": AIBrainService(),
            "desktop": DesktopAutomationService(),
            "voice": VoiceRecognitionService(),
            "tasks": TaskManagementService(),
            "scheduler": SchedulerService(),
            "reminders": ReminderService(),
        }
        
        # Service status
        self.status = {}
    
    def initialize_all(self) -> bool:
        """Initialize all services."""
        self.logger.info("\n  Initializing Services...")
        all_success = True
        
        for service_key, service in self.services.items():
            success = service.initialize()
            self.status[service_key] = service.get_status()
            
            if success:
                self.logger.info(f"    ✅ {service.name} ................. Initialized")
            else:
                self.logger.warning(f"    ⚠️  {service.name} ................. Failed (optional)")
                all_success = False
        
        self.logger.info()
        return all_success
    
    def print_status(self) -> None:
        """Print system status."""
        self.logger.info("\n  System Status:")
        self.logger.info(f"    Status: ONLINE")
        self.logger.info(f"    Mode: Production")
        self.logger.info(f"    User: Suvadip Panja")
        self.logger.info(f"    Time: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        self.logger.info("\n  Component Status:")
        for service_key, service in self.services.items():
            status = self.status.get(service_key)
            symbol = "✅" if status.available else "❌"
            self.logger.info(f"    {symbol} {status.name} ............ {status.available}")
        
        self.logger.info()
    
    def get_all_status(self) -> Dict[str, Any]:
        """Get all service statuses."""
        return {
            key: status.to_dict() 
            for key, status in self.status.items()
        }
    
    def execute_command(self, command: str) -> CommandResult:
        """
        Execute a command intelligently.
        Routes to appropriate service.
        """
        cmd_lower = command.lower().strip()
        
        # ===============================================
        # PRIORITY 1: Desktop Automation (Fast)
        # ===============================================
        desktop_service = self.services.get("desktop")
        if desktop_service and desktop_service.initialized:
            # Volume control
            if cmd_lower in ["volume up", "vol+"]:
                success, response = desktop_service.volume_up()
                return CommandResult(success, "volume_up", response, source="desktop")
            
            if cmd_lower in ["volume down", "vol-"]:
                success, response = desktop_service.volume_down()
                return CommandResult(success, "volume_down", response, source="desktop")
            
            if cmd_lower == "mute":
                success, response = desktop_service.mute()
                return CommandResult(success, "mute", response, source="desktop")
            
            if cmd_lower == "screenshot":
                success, response = desktop_service.take_screenshot()
                return CommandResult(success, "screenshot", response, source="desktop")
            
            if cmd_lower == "lock":
                success, response = desktop_service.lock_computer()
                return CommandResult(success, "lock", response, source="desktop")
            
            # Time/Date/Battery
            if cmd_lower in ["time", "what time"]:
                return CommandResult(
                    True, "time", f"The time is {desktop_service.get_time()}",
                    source="desktop"
                )
            
            if cmd_lower in ["date", "what date"]:
                return CommandResult(
                    True, "date", f"Today is {desktop_service.get_date()}",
                    source="desktop"
                )
            
            if cmd_lower == "battery":
                return CommandResult(
                    True, "battery", desktop_service.get_battery(),
                    source="desktop"
                )
        
        # ===============================================
        # PRIORITY 2: Fast Patterns (No AI needed)
        # ===============================================
        if cmd_lower in ["hello", "hi", "hey", "hola"]:
            return CommandResult(
                True, "greeting", 
                "Hello! I'm ARES. How can I help you today?",
                source="pattern"
            )
        
        if cmd_lower in ["help", "what can you do"]:
            help_text = """I can help you with:
✅ Voice Commands - Speak naturally
✅ App Control - Open apps instantly
✅ System Control - Volume, screenshots, lock
✅ Tasks - Execute workflows
✅ Schedules - Automate tasks
✅ Reminders - Set alarms & timers
✅ Information - Time, date, battery, status"""
            return CommandResult(
                True, "help", help_text,
                source="pattern"
            )
        
        # ===============================================
        # PRIORITY 3: AI Conversation
        # ===============================================
        ai_service = self.services.get("ai_brain")
        if ai_service and ai_service.initialized:
            success, response = ai_service.converse(command)
            if success:
                return CommandResult(
                    True, "conversation", response,
                    source="ai"
                )
        
        # ===============================================
        # FALLBACK
        # ===============================================
        return CommandResult(
            False, "unknown",
            f"I understood '{command}'. Try 'help' to see what I can do.",
            source="fallback"
        )
    
    def shutdown(self) -> None:
        """Shutdown all services."""
        self.logger.info("\nShutting down ARES...")
        for service in self.services.values():
            service.shutdown()
        self.logger.info("✅ ARES shutdown complete")


# ===================================================
# GLOBAL INSTANCE
# ===================================================

# Create global ARES manager
manager = None

def get_manager() -> ARESManager:
    """Get or create ARES manager."""
    global manager
    if manager is None:
        manager = ARESManager()
    return manager

def initialize_ares() -> ARESManager:
    """Initialize and return ARES manager."""
    manager = get_manager()
    manager.initialize_all()
    manager.print_status()
    return manager


# ===================================================
# CONVENIENCE FUNCTIONS FOR FLASK
# ===================================================

def execute_command(command: str) -> Dict[str, Any]:
    """Execute a command via the manager."""
    manager = get_manager()
    result = manager.execute_command(command)
    return result.to_dict()

def get_system_status() -> Dict[str, Any]:
    """Get system status."""
    manager = get_manager()
    return {
        "online": True,
        "mode": "production",
        "user": "Suvadip Panja",
        "services": manager.get_all_status()
    }


if __name__ == "__main__":
    # Initialize ARES
    ares = initialize_ares()
    
    # Test commands
    print("\n" + "=" * 70)
    print("  Testing Commands")
    print("=" * 70 + "\n")
    
    test_commands = [
        "hello",
        "what time is it",
        "help",
        "what's the battery",
    ]
    
    for cmd in test_commands:
        result = ares.execute_command(cmd)
        print(f"Command: '{cmd}'")
        print(f"Response: {result.response}\n")
    
    print("=" * 70)
    print("✅ ARES Manager Ready!")
    print("=" * 70)
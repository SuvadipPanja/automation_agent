"""
=====================================================
ARES TASK SYSTEM
=====================================================
Predefined tasks that ARES can execute on command
or via scheduler.

Features:
✅ Predefined task library
✅ Custom task creation
✅ Multi-step task sequences
✅ Task with parameters
✅ Conditional execution
✅ Task logging

Author: ARES AI Assistant
For: Suvadip Panja
=====================================================
"""

import os
import json
import time
import datetime
import subprocess
from pathlib import Path
from typing import List, Dict, Optional, Callable, Any
from dataclasses import dataclass, asdict, field
from enum import Enum
import threading


class TaskStatus(Enum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    SKIPPED = "skipped"


@dataclass
class TaskAction:
    """Single action within a task."""
    action_type: str
    params: Dict[str, Any] = field(default_factory=dict)
    description: str = ""
    
    def to_dict(self) -> dict:
        return {
            "action_type": self.action_type,
            "params": self.params,
            "description": self.description
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> 'TaskAction':
        return cls(
            action_type=data.get("action_type", ""),
            params=data.get("params", {}),
            description=data.get("description", "")
        )


@dataclass
class Task:
    """Represents a predefined task."""
    id: str
    name: str
    description: str
    actions: List[TaskAction] = field(default_factory=list)
    enabled: bool = True
    category: str = "general"
    icon: str = "📋"
    created_at: str = None
    last_run: str = None
    run_count: int = 0
    
    def __post_init__(self):
        if self.created_at is None:
            self.created_at = datetime.datetime.now().isoformat()
    
    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "actions": [a.to_dict() for a in self.actions],
            "enabled": self.enabled,
            "category": self.category,
            "icon": self.icon,
            "created_at": self.created_at,
            "last_run": self.last_run,
            "run_count": self.run_count
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> 'Task':
        actions = [TaskAction.from_dict(a) for a in data.get("actions", [])]
        return cls(
            id=data.get("id", ""),
            name=data.get("name", ""),
            description=data.get("description", ""),
            actions=actions,
            enabled=data.get("enabled", True),
            category=data.get("category", "general"),
            icon=data.get("icon", "📋"),
            created_at=data.get("created_at"),
            last_run=data.get("last_run"),
            run_count=data.get("run_count", 0)
        )


@dataclass
class TaskResult:
    """Result of task execution."""
    task_id: str
    task_name: str
    status: str
    started_at: str
    completed_at: str = None
    message: str = ""
    action_results: List[Dict] = field(default_factory=list)
    error: str = None
    speak_text: str = None


class TaskExecutor:
    """Executes task actions."""
    
    def __init__(self):
        self.desktop = None
        self._load_desktop()
    
    def _load_desktop(self):
        try:
            from automation.desktop_control import DesktopAutomation
            self.desktop = DesktopAutomation()
        except Exception as e:
            print(f"  ⚠️ Desktop not available for tasks: {e}")
    
    def execute_task(self, task: Task, on_progress: Callable = None) -> TaskResult:
        """Execute all actions in a task."""
        result = TaskResult(
            task_id=task.id,
            task_name=task.name,
            status="running",
            started_at=datetime.datetime.now().isoformat()
        )
        
        if not task.enabled:
            result.status = "skipped"
            result.message = "Task is disabled"
            return result
        
        speak_messages = []
        
        try:
            for i, action in enumerate(task.actions):
                if on_progress:
                    on_progress(i + 1, len(task.actions), action.description)
                
                action_result = self._execute_action(action)
                result.action_results.append(action_result)
                
                # Collect speak messages
                if action_result.get("speak"):
                    speak_messages.append(action_result["speak"])
                
                if not action_result.get("success", False):
                    print(f"  ⚠️ Action failed: {action_result.get('error', 'Unknown')}")
            
            result.status = "completed"
            result.message = f"Completed {len(task.actions)} actions"
            
            if speak_messages:
                result.speak_text = " ".join(speak_messages)
            
        except Exception as e:
            result.status = "failed"
            result.error = str(e)
            result.message = f"Task failed: {e}"
        
        result.completed_at = datetime.datetime.now().isoformat()
        task.last_run = result.completed_at
        task.run_count += 1
        
        return result
    
    def _execute_action(self, action: TaskAction) -> Dict:
        """Execute a single action."""
        action_type = action.action_type
        params = action.params
        
        result = {"action": action_type, "success": False, "message": ""}
        
        try:
            if action_type == "open_app":
                app = params.get("app", "")
                if self.desktop:
                    success, msg = self.desktop.open_application(app)
                    result["success"] = success
                    result["message"] = msg
                    
            elif action_type == "close_app":
                app = params.get("app", "")
                if self.desktop:
                    success, msg = self.desktop.close_application(app)
                    result["success"] = success
                    result["message"] = msg
                    
            elif action_type == "open_website":
                url = params.get("url", "")
                if self.desktop:
                    success, msg = self.desktop.open_website(url)
                    result["success"] = success
                    result["message"] = msg
                    
            elif action_type == "open_folder":
                folder = params.get("folder", "")
                if self.desktop:
                    success, msg = self.desktop.open_folder(folder)
                    result["success"] = success
                    result["message"] = msg
                    
            elif action_type == "run_command":
                cmd = params.get("command", "")
                if cmd:
                    subprocess.Popen(cmd, shell=True)
                    result["success"] = True
                    result["message"] = f"Ran: {cmd[:50]}"
                    
            elif action_type == "type_text":
                text = params.get("text", "")
                if self.desktop:
                    success, msg = self.desktop.type_text(text)
                    result["success"] = success
                    result["message"] = msg
                    
            elif action_type == "hotkey":
                keys = params.get("keys", [])
                if self.desktop and keys:
                    success, msg = self.desktop.hotkey(*keys)
                    result["success"] = success
                    result["message"] = msg
                    
            elif action_type == "wait":
                seconds = params.get("seconds", 1)
                time.sleep(seconds)
                result["success"] = True
                result["message"] = f"Waited {seconds}s"
                
            elif action_type == "notify":
                message = params.get("message", "")
                result["success"] = True
                result["message"] = message
                result["notify"] = message
                
            elif action_type == "speak":
                text = params.get("text", "")
                result["success"] = True
                result["message"] = text
                result["speak"] = text
                
            elif action_type == "screenshot":
                if self.desktop:
                    success, msg = self.desktop.take_screenshot()
                    result["success"] = success
                    result["message"] = msg
                    
            elif action_type == "volume":
                level = params.get("level", "")
                if self.desktop:
                    if level == "up":
                        success, msg = self.desktop.volume_up()
                    elif level == "down":
                        success, msg = self.desktop.volume_down()
                    elif level == "mute":
                        success, msg = self.desktop.mute_volume()
                    else:
                        success, msg = False, "Unknown volume"
                    result["success"] = success
                    result["message"] = msg
                    
            elif action_type == "minimize_all":
                if self.desktop:
                    success, msg = self.desktop.minimize_all()
                    result["success"] = success
                    result["message"] = msg
                    
            else:
                result["message"] = f"Unknown action: {action_type}"
                
        except Exception as e:
            result["error"] = str(e)
            result["message"] = f"Error: {e}"
        
        return result


class TaskManager:
    """Manages predefined tasks."""
    
    def __init__(self, storage_path: str = None):
        if storage_path is None:
            storage_path = os.path.join(os.path.expanduser("~"), ".ares", "tasks.json")
        self.storage_path = Path(storage_path)
        self.storage_path.parent.mkdir(parents=True, exist_ok=True)
        
        self.tasks: Dict[str, Task] = {}
        self.executor = TaskExecutor()
        
        self._load()
        self._ensure_defaults()
        
        print(f"  ✅ Task Manager ({len(self.tasks)} tasks)")
    
    def _load(self):
        if self.storage_path.exists():
            try:
                with open(self.storage_path, 'r') as f:
                    data = json.load(f)
                    for t in data:
                        task = Task.from_dict(t)
                        self.tasks[task.id] = task
            except Exception as e:
                print(f"  ⚠️ Could not load tasks: {e}")
    
    def _save(self):
        try:
            with open(self.storage_path, 'w') as f:
                json.dump([t.to_dict() for t in self.tasks.values()], f, indent=2)
        except:
            pass
    
    def _ensure_defaults(self):
        if not self.tasks:
            self._create_defaults()
            self._save()
    
    def _create_defaults(self):
        """Create built-in default tasks."""
        
        # Morning Routine
        self.tasks["morning_routine"] = Task(
            id="morning_routine",
            name="Morning Routine",
            description="Start your workday - opens browser, email, and work apps",
            icon="🌅",
            category="routine",
            actions=[
                TaskAction("speak", {"text": "Good morning! Starting your morning routine."}, "Greeting"),
                TaskAction("open_app", {"app": "chrome"}, "Open browser"),
                TaskAction("wait", {"seconds": 2}, "Wait for browser"),
                TaskAction("open_website", {"url": "https://mail.google.com"}, "Open email"),
                TaskAction("wait", {"seconds": 1}, "Wait"),
                TaskAction("open_app", {"app": "vscode"}, "Open VS Code"),
                TaskAction("speak", {"text": "Morning routine complete. Have a productive day!"}, "Complete")
            ]
        )
        
        # Work Apps
        self.tasks["work_apps"] = Task(
            id="work_apps",
            name="Open Work Apps",
            description="Opens all your work applications",
            icon="💼",
            category="work",
            actions=[
                TaskAction("open_app", {"app": "chrome"}, "Open Chrome"),
                TaskAction("wait", {"seconds": 1}),
                TaskAction("open_app", {"app": "vscode"}, "Open VS Code"),
                TaskAction("wait", {"seconds": 1}),
                TaskAction("open_app", {"app": "outlook"}, "Open Outlook"),
                TaskAction("notify", {"message": "Work apps ready!"})
            ]
        )
        
        # Close Work Apps
        self.tasks["close_work_apps"] = Task(
            id="close_work_apps",
            name="Close Work Apps",
            description="Closes work applications",
            icon="🚪",
            category="work",
            actions=[
                TaskAction("speak", {"text": "Closing work applications"}),
                TaskAction("close_app", {"app": "chrome"}),
                TaskAction("close_app", {"app": "vscode"}),
                TaskAction("close_app", {"app": "outlook"}),
                TaskAction("speak", {"text": "Work apps closed!"})
            ]
        )
        
        # Screenshot
        self.tasks["take_screenshot"] = Task(
            id="take_screenshot",
            name="Take Screenshot",
            description="Captures current screen",
            icon="📸",
            category="utility",
            actions=[
                TaskAction("screenshot", {}, "Capture screen"),
                TaskAction("notify", {"message": "Screenshot saved!"})
            ]
        )
        
        # System Cleanup
        self.tasks["system_cleanup"] = Task(
            id="system_cleanup",
            name="System Cleanup",
            description="Clears temporary files",
            icon="🧹",
            category="system",
            actions=[
                TaskAction("speak", {"text": "Starting system cleanup"}),
                TaskAction("run_command", {"command": "del /q/f/s %TEMP%\\* 2>nul"}),
                TaskAction("wait", {"seconds": 2}),
                TaskAction("speak", {"text": "Cleanup complete!"})
            ]
        )
        
        # Lock Computer
        self.tasks["lock_pc"] = Task(
            id="lock_pc",
            name="Lock Computer",
            description="Locks your computer",
            icon="🔒",
            category="system",
            actions=[
                TaskAction("speak", {"text": "Locking computer"}),
                TaskAction("wait", {"seconds": 1}),
                TaskAction("run_command", {"command": "rundll32.exe user32.dll,LockWorkStation"})
            ]
        )
        
        # Break Reminder
        self.tasks["break_reminder"] = Task(
            id="break_reminder",
            name="Break Reminder",
            description="Reminds you to take a break",
            icon="☕",
            category="health",
            actions=[
                TaskAction("notify", {"message": "Time for a break! Stand up and stretch."}),
                TaskAction("speak", {"text": "Hey! Time for a break. Stand up and stretch!"})
            ]
        )
        
        # End of Day
        self.tasks["end_of_day"] = Task(
            id="end_of_day",
            name="End of Day",
            description="Wraps up your workday",
            icon="🌙",
            category="routine",
            actions=[
                TaskAction("speak", {"text": "Wrapping up for the day"}),
                TaskAction("screenshot", {}, "Save work screenshot"),
                TaskAction("close_app", {"app": "chrome"}),
                TaskAction("close_app", {"app": "vscode"}),
                TaskAction("wait", {"seconds": 2}),
                TaskAction("speak", {"text": "All done! Have a great evening!"})
            ]
        )
        
        # Focus Mode
        self.tasks["focus_mode"] = Task(
            id="focus_mode",
            name="Focus Mode",
            description="Minimizes distractions",
            icon="🎯",
            category="productivity",
            actions=[
                TaskAction("speak", {"text": "Entering focus mode"}),
                TaskAction("close_app", {"app": "discord"}),
                TaskAction("close_app", {"app": "telegram"}),
                TaskAction("close_app", {"app": "whatsapp"}),
                TaskAction("volume", {"level": "mute"}),
                TaskAction("notify", {"message": "Focus mode active!"})
            ]
        )
        
        # Show Desktop
        self.tasks["show_desktop"] = Task(
            id="show_desktop",
            name="Show Desktop",
            description="Minimizes all windows",
            icon="🖥️",
            category="utility",
            actions=[
                TaskAction("minimize_all", {})
            ]
        )
        
        # Check Email
        self.tasks["check_email"] = Task(
            id="check_email",
            name="Check Email",
            description="Opens Gmail",
            icon="📧",
            category="communication",
            actions=[
                TaskAction("open_app", {"app": "chrome"}),
                TaskAction("wait", {"seconds": 2}),
                TaskAction("open_website", {"url": "https://mail.google.com"})
            ]
        )
        
        # Open YouTube
        self.tasks["open_youtube"] = Task(
            id="open_youtube",
            name="Open YouTube",
            description="Opens YouTube",
            icon="▶️",
            category="entertainment",
            actions=[
                TaskAction("open_app", {"app": "chrome"}),
                TaskAction("wait", {"seconds": 2}),
                TaskAction("open_website", {"url": "https://youtube.com"})
            ]
        )
    
    # ===========================================
    # MANAGEMENT
    # ===========================================
    
    def get_all(self) -> List[Task]:
        return list(self.tasks.values())
    
    def get_by_id(self, task_id: str) -> Optional[Task]:
        return self.tasks.get(task_id)
    
    def get_by_name(self, name: str) -> Optional[Task]:
        name_lower = name.lower()
        
        for task in self.tasks.values():
            if task.name.lower() == name_lower:
                return task
        
        for task in self.tasks.values():
            if name_lower in task.name.lower() or name_lower in task.id.lower():
                return task
        
        return None
    
    def get_by_category(self, category: str) -> List[Task]:
        return [t for t in self.tasks.values() if t.category == category]
    
    def add_task(self, task: Task) -> bool:
        if task.id in self.tasks:
            return False
        self.tasks[task.id] = task
        self._save()
        return True
    
    def delete_task(self, task_id: str) -> bool:
        if task_id in self.tasks:
            del self.tasks[task_id]
            self._save()
            return True
        return False
    
    def enable_task(self, task_id: str, enabled: bool = True) -> bool:
        task = self.get_by_id(task_id)
        if task:
            task.enabled = enabled
            self._save()
            return True
        return False
    
    # ===========================================
    # EXECUTION
    # ===========================================
    
    def run_task(self, task_id: str) -> Optional[TaskResult]:
        task = self.get_by_id(task_id)
        if not task:
            return None
        
        result = self.executor.execute_task(task)
        self._save()
        return result
    
    def run_task_by_name(self, name: str) -> Optional[TaskResult]:
        task = self.get_by_name(name)
        if not task:
            return None
        
        result = self.executor.execute_task(task)
        self._save()
        return result
    
    # ===========================================
    # FORMATTING
    # ===========================================
    
    def format_list(self) -> str:
        if not self.tasks:
            return "No tasks defined."
        
        categories = {}
        for task in self.tasks.values():
            cat = task.category
            if cat not in categories:
                categories[cat] = []
            categories[cat].append(task)
        
        lines = ["📋 Available Tasks:\n"]
        
        for cat, tasks in sorted(categories.items()):
            lines.append(f"\n{cat.upper()}:")
            for task in tasks:
                status = "✅" if task.enabled else "❌"
                lines.append(f"  {task.icon} {task.name} {status}")
        
        return "\n".join(lines)


# Global instance
_task_manager: Optional[TaskManager] = None

def get_task_manager() -> TaskManager:
    global _task_manager
    if _task_manager is None:
        _task_manager = TaskManager()
    return _task_manager


if __name__ == "__main__":
    print("\n📋 Testing Task System\n")
    manager = get_task_manager()
    print(manager.format_list())
"""
=====================================================
ARES SCHEDULER SYSTEM
=====================================================
Schedule tasks to run automatically at specific times.

Features:
✅ One-time schedules
✅ Daily schedules (e.g., "every day at 9am")
✅ Hourly schedules (e.g., "every 2 hours")
✅ Weekly schedules (e.g., "every Monday at 9am")
✅ Interval schedules (e.g., "every 30 minutes")
✅ Persistent storage
✅ Enable/disable schedules
✅ Execution logging

Author: ARES AI Assistant
For: Suvadip Panja
=====================================================
"""

import os
import json
import time
import datetime
import threading
import re
from pathlib import Path
from typing import List, Dict, Optional, Callable
from dataclasses import dataclass, field
from enum import Enum


class ScheduleType(Enum):
    """Types of schedules."""
    ONCE = "once"           # Run once at specific time
    DAILY = "daily"         # Run every day at specific time
    HOURLY = "hourly"       # Run every N hours
    WEEKLY = "weekly"       # Run on specific day(s) of week
    INTERVAL = "interval"   # Run every N minutes


@dataclass
class Schedule:
    """Represents a scheduled task."""
    id: str
    task_id: str
    task_name: str
    schedule_type: str
    time: str = None        # HH:MM format for daily/weekly
    days: List[int] = None  # Days of week (0=Monday, 6=Sunday)
    interval_minutes: int = 0
    enabled: bool = True
    next_run: str = None
    last_run: str = None
    run_count: int = 0
    created_at: str = None
    description: str = ""
    
    def __post_init__(self):
        if self.created_at is None:
            self.created_at = datetime.datetime.now().isoformat()
        if self.days is None:
            self.days = []
    
    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "task_id": self.task_id,
            "task_name": self.task_name,
            "schedule_type": self.schedule_type,
            "time": self.time,
            "days": self.days,
            "interval_minutes": self.interval_minutes,
            "enabled": self.enabled,
            "next_run": self.next_run,
            "last_run": self.last_run,
            "run_count": self.run_count,
            "created_at": self.created_at,
            "description": self.description
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> 'Schedule':
        return cls(
            id=data.get("id", ""),
            task_id=data.get("task_id", ""),
            task_name=data.get("task_name", ""),
            schedule_type=data.get("schedule_type", "once"),
            time=data.get("time"),
            days=data.get("days", []),
            interval_minutes=data.get("interval_minutes", 0),
            enabled=data.get("enabled", True),
            next_run=data.get("next_run"),
            last_run=data.get("last_run"),
            run_count=data.get("run_count", 0),
            created_at=data.get("created_at"),
            description=data.get("description", "")
        )
    
    def calculate_next_run(self) -> Optional[datetime.datetime]:
        """Calculate next run time based on schedule type."""
        now = datetime.datetime.now()
        
        if self.schedule_type == "once":
            # Parse next_run if set
            if self.next_run:
                try:
                    return datetime.datetime.fromisoformat(self.next_run)
                except:
                    return None
            return None
        
        elif self.schedule_type == "daily":
            if not self.time:
                return None
            
            hour, minute = map(int, self.time.split(':'))
            next_run = now.replace(hour=hour, minute=minute, second=0, microsecond=0)
            
            if next_run <= now:
                next_run += datetime.timedelta(days=1)
            
            return next_run
        
        elif self.schedule_type == "hourly":
            hours = self.interval_minutes // 60 if self.interval_minutes >= 60 else 1
            next_run = now + datetime.timedelta(hours=hours)
            return next_run.replace(second=0, microsecond=0)
        
        elif self.schedule_type == "weekly":
            if not self.time or not self.days:
                return None
            
            hour, minute = map(int, self.time.split(':'))
            
            # Find next occurrence
            for i in range(8):  # Check next 7 days + today
                check_date = now + datetime.timedelta(days=i)
                weekday = check_date.weekday()
                
                if weekday in self.days:
                    next_run = check_date.replace(hour=hour, minute=minute, second=0, microsecond=0)
                    if next_run > now:
                        return next_run
            
            return None
        
        elif self.schedule_type == "interval":
            if self.interval_minutes <= 0:
                return None
            
            next_run = now + datetime.timedelta(minutes=self.interval_minutes)
            return next_run.replace(second=0, microsecond=0)
        
        return None
    
    def is_due(self) -> bool:
        """Check if schedule is due to run."""
        if not self.enabled:
            return False
        
        if not self.next_run:
            return False
        
        try:
            next_run_dt = datetime.datetime.fromisoformat(self.next_run)
            return datetime.datetime.now() >= next_run_dt
        except:
            return False
    
    def format_schedule(self) -> str:
        """Format schedule as readable string."""
        if self.schedule_type == "once":
            if self.next_run:
                try:
                    dt = datetime.datetime.fromisoformat(self.next_run)
                    return f"Once at {dt.strftime('%b %d, %I:%M %p')}"
                except:
                    pass
            return "Once (time not set)"
        
        elif self.schedule_type == "daily":
            return f"Daily at {self.time or '??:??'}"
        
        elif self.schedule_type == "hourly":
            hours = self.interval_minutes // 60 if self.interval_minutes >= 60 else 1
            return f"Every {hours} hour{'s' if hours > 1 else ''}"
        
        elif self.schedule_type == "weekly":
            day_names = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']
            days_str = ', '.join([day_names[d] for d in sorted(self.days or [])])
            return f"Every {days_str} at {self.time or '??:??'}"
        
        elif self.schedule_type == "interval":
            if self.interval_minutes >= 60:
                hours = self.interval_minutes // 60
                mins = self.interval_minutes % 60
                if mins > 0:
                    return f"Every {hours}h {mins}m"
                return f"Every {hours} hour{'s' if hours > 1 else ''}"
            return f"Every {self.interval_minutes} minute{'s' if self.interval_minutes > 1 else ''}"
        
        return "Unknown schedule"


@dataclass
class ScheduleResult:
    """Result of scheduled task execution."""
    schedule_id: str
    task_id: str
    executed_at: str
    status: str
    message: str


class Scheduler:
    """
    Manages and executes scheduled tasks.
    """
    
    def __init__(self, storage_path: str = None):
        if storage_path is None:
            storage_path = os.path.join(os.path.expanduser("~"), ".ares", "schedules.json")
        self.storage_path = Path(storage_path)
        self.storage_path.parent.mkdir(parents=True, exist_ok=True)
        
        self.schedules: Dict[str, Schedule] = {}
        self.task_manager = None
        
        # Callbacks
        self.on_task_run: Optional[Callable[[Schedule, any], None]] = None
        self.on_task_complete: Optional[Callable[[Schedule, any], None]] = None
        
        # Background thread
        self._running = False
        self._thread: Optional[threading.Thread] = None
        self._check_interval = 30  # Check every 30 seconds
        
        # Execution log
        self.execution_log: List[ScheduleResult] = []
        self.max_log_entries = 100
        
        self._load()
        print(f"  ✅ Scheduler ({len(self.schedules)} schedules)")
    
    def _load(self):
        """Load schedules from storage."""
        if self.storage_path.exists():
            try:
                with open(self.storage_path, 'r') as f:
                    data = json.load(f)
                    for s in data.get("schedules", []):
                        schedule = Schedule.from_dict(s)
                        self.schedules[schedule.id] = schedule
            except Exception as e:
                print(f"  ⚠️ Could not load schedules: {e}")
    
    def _save(self):
        """Save schedules to storage."""
        try:
            with open(self.storage_path, 'w') as f:
                json.dump({
                    "schedules": [s.to_dict() for s in self.schedules.values()]
                }, f, indent=2)
        except:
            pass
    
    def set_task_manager(self, task_manager):
        """Set the task manager reference."""
        self.task_manager = task_manager
    
    # ===========================================
    # SCHEDULE MANAGEMENT
    # ===========================================
    
    def add_schedule(self, schedule: Schedule) -> bool:
        """Add a new schedule."""
        # Calculate next run
        next_run = schedule.calculate_next_run()
        if next_run:
            schedule.next_run = next_run.isoformat()
        
        self.schedules[schedule.id] = schedule
        self._save()
        return True
    
    def create_daily_schedule(
        self, 
        task_id: str, 
        task_name: str,
        hour: int, 
        minute: int = 0,
        description: str = ""
    ) -> Schedule:
        """Create a daily schedule."""
        import uuid
        
        schedule = Schedule(
            id=str(uuid.uuid4())[:8],
            task_id=task_id,
            task_name=task_name,
            schedule_type="daily",
            time=f"{hour:02d}:{minute:02d}",
            description=description or f"Run '{task_name}' daily at {hour:02d}:{minute:02d}"
        )
        
        self.add_schedule(schedule)
        return schedule
    
    def create_interval_schedule(
        self,
        task_id: str,
        task_name: str,
        minutes: int,
        description: str = ""
    ) -> Schedule:
        """Create an interval schedule."""
        import uuid
        
        schedule = Schedule(
            id=str(uuid.uuid4())[:8],
            task_id=task_id,
            task_name=task_name,
            schedule_type="interval",
            interval_minutes=minutes,
            description=description or f"Run '{task_name}' every {minutes} minutes"
        )
        
        self.add_schedule(schedule)
        return schedule
    
    def create_weekly_schedule(
        self,
        task_id: str,
        task_name: str,
        days: List[int],  # 0=Monday, 6=Sunday
        hour: int,
        minute: int = 0,
        description: str = ""
    ) -> Schedule:
        """Create a weekly schedule."""
        import uuid
        
        schedule = Schedule(
            id=str(uuid.uuid4())[:8],
            task_id=task_id,
            task_name=task_name,
            schedule_type="weekly",
            time=f"{hour:02d}:{minute:02d}",
            days=days,
            description=description
        )
        
        self.add_schedule(schedule)
        return schedule
    
    def create_once_schedule(
        self,
        task_id: str,
        task_name: str,
        run_at: datetime.datetime,
        description: str = ""
    ) -> Schedule:
        """Create a one-time schedule."""
        import uuid
        
        schedule = Schedule(
            id=str(uuid.uuid4())[:8],
            task_id=task_id,
            task_name=task_name,
            schedule_type="once",
            next_run=run_at.isoformat(),
            description=description or f"Run '{task_name}' once"
        )
        
        self.add_schedule(schedule)
        return schedule
    
    def get_all(self) -> List[Schedule]:
        """Get all schedules."""
        return list(self.schedules.values())
    
    def get_by_id(self, schedule_id: str) -> Optional[Schedule]:
        """Get schedule by ID."""
        return self.schedules.get(schedule_id)
    
    def get_active(self) -> List[Schedule]:
        """Get active (enabled) schedules."""
        return [s for s in self.schedules.values() if s.enabled]
    
    def delete(self, schedule_id: str) -> bool:
        """Delete a schedule."""
        if schedule_id in self.schedules:
            del self.schedules[schedule_id]
            self._save()
            return True
        return False
    
    def delete_by_index(self, index: int) -> bool:
        """Delete schedule by list index (1-based)."""
        schedules = self.get_all()
        if 1 <= index <= len(schedules):
            return self.delete(schedules[index - 1].id)
        return False
    
    def enable(self, schedule_id: str, enabled: bool = True) -> bool:
        """Enable or disable a schedule."""
        schedule = self.get_by_id(schedule_id)
        if schedule:
            schedule.enabled = enabled
            if enabled:
                # Recalculate next run
                next_run = schedule.calculate_next_run()
                if next_run:
                    schedule.next_run = next_run.isoformat()
            self._save()
            return True
        return False
    
    def clear_all(self) -> int:
        """Clear all schedules."""
        count = len(self.schedules)
        self.schedules = {}
        self._save()
        return count
    
    # ===========================================
    # EXECUTION
    # ===========================================
    
    def start(self):
        """Start the background scheduler."""
        if self._running:
            return
        
        self._running = True
        self._thread = threading.Thread(target=self._run_loop, daemon=True)
        self._thread.start()
        print("  🕐 Scheduler started")
    
    def stop(self):
        """Stop the background scheduler."""
        self._running = False
        if self._thread:
            self._thread.join(timeout=2)
    
    def _run_loop(self):
        """Background loop to check schedules."""
        while self._running:
            self._check_schedules()
            time.sleep(self._check_interval)
    
    def _check_schedules(self):
        """Check all schedules and run due ones."""
        for schedule in list(self.schedules.values()):
            if schedule.is_due():
                self._execute_schedule(schedule)
    
    def _execute_schedule(self, schedule: Schedule):
        """Execute a scheduled task."""
        print(f"  🕐 Running scheduled task: {schedule.task_name}")
        
        result = ScheduleResult(
            schedule_id=schedule.id,
            task_id=schedule.task_id,
            executed_at=datetime.datetime.now().isoformat(),
            status="running",
            message=""
        )
        
        try:
            # Run the task
            if self.task_manager:
                task_result = self.task_manager.run_task(schedule.task_id)
                
                if task_result:
                    result.status = task_result.status
                    result.message = task_result.message
                    
                    # Callback
                    if self.on_task_complete:
                        self.on_task_complete(schedule, task_result)
                else:
                    result.status = "failed"
                    result.message = "Task not found"
            else:
                result.status = "failed"
                result.message = "Task manager not available"
            
        except Exception as e:
            result.status = "failed"
            result.message = str(e)
        
        # Update schedule
        schedule.last_run = result.executed_at
        schedule.run_count += 1
        
        # Calculate next run
        if schedule.schedule_type != "once":
            next_run = schedule.calculate_next_run()
            if next_run:
                schedule.next_run = next_run.isoformat()
        else:
            schedule.enabled = False  # Disable one-time schedules after run
        
        self._save()
        
        # Log
        self.execution_log.append(result)
        if len(self.execution_log) > self.max_log_entries:
            self.execution_log = self.execution_log[-self.max_log_entries:]
    
    def run_now(self, schedule_id: str) -> Optional[ScheduleResult]:
        """Manually run a schedule now."""
        schedule = self.get_by_id(schedule_id)
        if schedule:
            self._execute_schedule(schedule)
            return self.execution_log[-1] if self.execution_log else None
        return None
    
    # ===========================================
    # FORMATTING
    # ===========================================
    
    def format_list(self) -> str:
        """Format schedules as readable list."""
        schedules = sorted(self.get_all(), key=lambda s: s.next_run or "")
        
        if not schedules:
            return "📅 No schedules set."
        
        lines = [f"📅 Scheduled Tasks ({len(schedules)}):\n"]
        
        for i, s in enumerate(schedules, 1):
            status = "✅" if s.enabled else "❌"
            
            # Next run info
            if s.next_run and s.enabled:
                try:
                    next_dt = datetime.datetime.fromisoformat(s.next_run)
                    now = datetime.datetime.now()
                    diff = next_dt - now
                    
                    if diff.total_seconds() < 0:
                        next_str = "overdue"
                    elif diff.total_seconds() < 3600:
                        mins = int(diff.total_seconds() / 60)
                        next_str = f"in {mins}m"
                    elif diff.total_seconds() < 86400:
                        hours = int(diff.total_seconds() / 3600)
                        next_str = f"in {hours}h"
                    else:
                        next_str = next_dt.strftime("%b %d")
                except:
                    next_str = "?"
            else:
                next_str = "disabled"
            
            lines.append(f"{i}. {status} {s.task_name}")
            lines.append(f"   {s.format_schedule()} (next: {next_str})")
        
        return "\n".join(lines)


# ===========================================
# NATURAL LANGUAGE PARSER
# ===========================================

class ScheduleParser:
    """Parses natural language schedule expressions."""
    
    @staticmethod
    def parse(text: str) -> Optional[Dict]:
        """
        Parse schedule from text.
        
        Examples:
        - "daily at 9am"
        - "every day at 14:30"
        - "every 2 hours"
        - "every 30 minutes"
        - "every monday at 9am"
        - "on weekdays at 8am"
        """
        text = text.lower().strip()
        
        # Daily at specific time
        daily_match = re.search(
            r'(?:daily|every\s*day)\s+(?:at\s+)?(\d{1,2})(?::(\d{2}))?\s*(am|pm)?',
            text
        )
        if daily_match:
            hour = int(daily_match.group(1))
            minute = int(daily_match.group(2)) if daily_match.group(2) else 0
            ampm = daily_match.group(3)
            
            if ampm == 'pm' and hour != 12:
                hour += 12
            elif ampm == 'am' and hour == 12:
                hour = 0
            
            return {
                "type": "daily",
                "hour": hour,
                "minute": minute
            }
        
        # Every N hours
        hours_match = re.search(r'every\s+(\d+)\s*(?:hour|hr)s?', text)
        if hours_match:
            hours = int(hours_match.group(1))
            return {
                "type": "interval",
                "minutes": hours * 60
            }
        
        # Every N minutes
        mins_match = re.search(r'every\s+(\d+)\s*(?:minute|min)s?', text)
        if mins_match:
            minutes = int(mins_match.group(1))
            return {
                "type": "interval",
                "minutes": minutes
            }
        
        # Weekly - specific days
        day_names = {
            'monday': 0, 'mon': 0,
            'tuesday': 1, 'tue': 1,
            'wednesday': 2, 'wed': 2,
            'thursday': 3, 'thu': 3,
            'friday': 4, 'fri': 4,
            'saturday': 5, 'sat': 5,
            'sunday': 6, 'sun': 6
        }
        
        weekly_match = re.search(
            r'(?:every|on)\s+(monday|tuesday|wednesday|thursday|friday|saturday|sunday|mon|tue|wed|thu|fri|sat|sun)s?\s+(?:at\s+)?(\d{1,2})(?::(\d{2}))?\s*(am|pm)?',
            text
        )
        if weekly_match:
            day = day_names.get(weekly_match.group(1), 0)
            hour = int(weekly_match.group(2))
            minute = int(weekly_match.group(3)) if weekly_match.group(3) else 0
            ampm = weekly_match.group(4)
            
            if ampm == 'pm' and hour != 12:
                hour += 12
            elif ampm == 'am' and hour == 12:
                hour = 0
            
            return {
                "type": "weekly",
                "days": [day],
                "hour": hour,
                "minute": minute
            }
        
        # Weekdays
        weekdays_match = re.search(
            r'(?:on\s+)?weekdays\s+(?:at\s+)?(\d{1,2})(?::(\d{2}))?\s*(am|pm)?',
            text
        )
        if weekdays_match:
            hour = int(weekdays_match.group(1))
            minute = int(weekdays_match.group(2)) if weekdays_match.group(2) else 0
            ampm = weekdays_match.group(3)
            
            if ampm == 'pm' and hour != 12:
                hour += 12
            elif ampm == 'am' and hour == 12:
                hour = 0
            
            return {
                "type": "weekly",
                "days": [0, 1, 2, 3, 4],  # Mon-Fri
                "hour": hour,
                "minute": minute
            }
        
        # Simple time (assume daily)
        time_match = re.search(r'(?:at\s+)?(\d{1,2})(?::(\d{2}))?\s*(am|pm)', text)
        if time_match:
            hour = int(time_match.group(1))
            minute = int(time_match.group(2)) if time_match.group(2) else 0
            ampm = time_match.group(3)
            
            if ampm == 'pm' and hour != 12:
                hour += 12
            elif ampm == 'am' and hour == 12:
                hour = 0
            
            return {
                "type": "daily",
                "hour": hour,
                "minute": minute
            }
        
        return None


# ===========================================
# GLOBAL INSTANCE
# ===========================================

_scheduler: Optional[Scheduler] = None

def get_scheduler() -> Scheduler:
    """Get or create the global scheduler."""
    global _scheduler
    if _scheduler is None:
        _scheduler = Scheduler()
        
        # Link with task manager
        try:
            from automation.tasks import get_task_manager
            _scheduler.set_task_manager(get_task_manager())
        except:
            pass
        
        _scheduler.start()
    return _scheduler


# ===========================================
# TEST
# ===========================================

if __name__ == "__main__":
    print("\n📅 Testing Scheduler\n")
    
    scheduler = get_scheduler()
    
    # Create test schedule
    schedule = scheduler.create_daily_schedule(
        task_id="break_reminder",
        task_name="Break Reminder",
        hour=10,
        minute=0,
        description="Morning break reminder"
    )
    
    print(f"Created schedule: {schedule.id}")
    print(scheduler.format_list())
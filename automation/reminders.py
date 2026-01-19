"""
=====================================================
ARES REMINDER & ALARM SYSTEM - FIXED
=====================================================
Complete reminder, alarm, and timer functionality.

Features:
✅ One-time reminders ("remind me at 5pm")
✅ Relative reminders ("remind me in 30 minutes")
✅ Recurring daily reminders
✅ Alarms with sound
✅ Countdown timers - FIXED
✅ Persistent storage (survives restart)
✅ Natural language parsing

Author: ARES AI Assistant
For: Shobutik Panja
=====================================================
"""

import os
import json
import time
import threading
import datetime
import re
import uuid
from pathlib import Path
from typing import List, Dict, Optional, Callable
from dataclasses import dataclass
from enum import Enum


class ReminderType(Enum):
    REMINDER = "reminder"
    ALARM = "alarm"
    TIMER = "timer"


@dataclass
class Reminder:
    """Represents a reminder, alarm, or timer."""
    id: str
    message: str
    trigger_time: datetime.datetime
    reminder_type: str
    status: str = "active"
    recurring: bool = False
    recurring_time: str = None
    created_at: str = None
    
    def __post_init__(self):
        if self.created_at is None:
            self.created_at = datetime.datetime.now().isoformat()
    
    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "message": self.message,
            "trigger_time": self.trigger_time.isoformat() if isinstance(self.trigger_time, datetime.datetime) else self.trigger_time,
            "reminder_type": self.reminder_type,
            "status": self.status,
            "recurring": self.recurring,
            "recurring_time": self.recurring_time,
            "created_at": self.created_at
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> 'Reminder':
        trigger_time = data.get("trigger_time")
        if isinstance(trigger_time, str):
            trigger_time = datetime.datetime.fromisoformat(trigger_time)
        
        return cls(
            id=data.get("id"),
            message=data.get("message"),
            trigger_time=trigger_time,
            reminder_type=data.get("reminder_type", "reminder"),
            status=data.get("status", "active"),
            recurring=data.get("recurring", False),
            recurring_time=data.get("recurring_time"),
            created_at=data.get("created_at")
        )
    
    def is_due(self) -> bool:
        if self.status != "active":
            return False
        return datetime.datetime.now() >= self.trigger_time
    
    def time_until(self) -> str:
        delta = self.trigger_time - datetime.datetime.now()
        
        if delta.total_seconds() < 0:
            return "now"
        
        total_seconds = int(delta.total_seconds())
        
        if total_seconds < 60:
            return f"{total_seconds} seconds"
        elif total_seconds < 3600:
            minutes = total_seconds // 60
            return f"{minutes} minute{'s' if minutes != 1 else ''}"
        elif total_seconds < 86400:
            hours = total_seconds // 3600
            minutes = (total_seconds % 3600) // 60
            if minutes > 0:
                return f"{hours}h {minutes}m"
            return f"{hours} hour{'s' if hours != 1 else ''}"
        else:
            days = total_seconds // 86400
            return f"{days} day{'s' if days != 1 else ''}"


class ReminderManager:
    """Manages all reminders, alarms, and timers."""
    
    def __init__(self, storage_path: str = None):
        if storage_path is None:
            storage_path = os.path.join(os.path.expanduser("~"), ".ares", "reminders.json")
        self.storage_path = Path(storage_path)
        self.storage_path.parent.mkdir(parents=True, exist_ok=True)
        
        self.reminders: List[Reminder] = []
        self.on_trigger: Optional[Callable[[Reminder], None]] = None
        self.triggered_queue: List[Reminder] = []
        
        self._running = False
        self._thread: Optional[threading.Thread] = None
        
        self._load()
        print(f"  ✅ Reminder system initialized ({len(self.reminders)} active)")
    
    def _load(self):
        """Load reminders from storage"""
        if self.storage_path.exists():
            try:
                with open(self.storage_path, 'r') as f:
                    data = json.load(f)
                    self.reminders = [Reminder.from_dict(r) for r in data]
                    # Keep only active reminders
                    self.reminders = [r for r in self.reminders if r.status == "active"]
                    print(f"  📥 Loaded {len(self.reminders)} reminders from storage")
            except Exception as e:
                print(f"  ⚠️ Could not load reminders: {e}")
                self.reminders = []
        else:
            print(f"  📝 No existing reminders (new database)")
    
    def _save(self):
        """Save reminders to storage"""
        try:
            with open(self.storage_path, 'w') as f:
                json.dump([r.to_dict() for r in self.reminders], f, indent=2)
        except Exception as e:
            print(f"  ⚠️ Could not save reminders: {e}")
    
    def add(self, message: str, trigger_time: datetime.datetime, 
            reminder_type: str = "reminder", recurring: bool = False,
            recurring_time: str = None) -> Reminder:
        """Add a new reminder/alarm/timer"""
        reminder = Reminder(
            id=str(uuid.uuid4())[:8],
            message=message,
            trigger_time=trigger_time,
            reminder_type=reminder_type,
            recurring=recurring,
            recurring_time=recurring_time
        )
        self.reminders.append(reminder)
        self._save()
        print(f"  ✅ Added {reminder_type}: {message} (triggers in {reminder.time_until()})")
        return reminder
    
    def add_relative(self, message: str, minutes: int = 0, 
                     hours: int = 0, seconds: int = 0,
                     reminder_type: str = "reminder") -> Reminder:
        """Add reminder with relative time (e.g., in 5 minutes)"""
        trigger_time = datetime.datetime.now() + datetime.timedelta(
            hours=hours, minutes=minutes, seconds=seconds
        )
        return self.add(message, trigger_time, reminder_type)
    
    def add_at_time(self, message: str, hour: int, minute: int = 0,
                    reminder_type: str = "reminder", recurring: bool = False) -> Reminder:
        """Add reminder at specific time (e.g., at 5:30 PM)"""
        now = datetime.datetime.now()
        trigger_time = now.replace(hour=hour, minute=minute, second=0, microsecond=0)
        
        # If time has passed today, schedule for tomorrow
        if trigger_time <= now:
            trigger_time += datetime.timedelta(days=1)
        
        recurring_time = f"{hour:02d}:{minute:02d}" if recurring else None
        return self.add(message, trigger_time, reminder_type, recurring, recurring_time)
    
    def set_timer(self, minutes: int, seconds: int = 0, message: str = None) -> Reminder:
        """Set a countdown timer"""
        if message is None:
            if minutes > 0 and seconds > 0:
                message = f"Timer: {minutes}m {seconds}s"
            elif minutes > 0:
                message = f"Timer: {minutes} minute{'s' if minutes != 1 else ''}"
            else:
                message = f"Timer: {seconds} second{'s' if seconds != 1 else ''}"
        
        print(f"  ⏱️ Setting timer for {minutes}m {seconds}s")
        return self.add_relative(message, minutes=minutes, seconds=seconds, reminder_type="timer")
    
    def set_alarm(self, hour: int, minute: int = 0, recurring: bool = False) -> Reminder:
        """Set an alarm at specific time"""
        message = f"Alarm: {hour:02d}:{minute:02d}"
        return self.add_at_time(message, hour, minute, "alarm", recurring)
    
    def get_all(self) -> List[Reminder]:
        """Get all active reminders"""
        return [r for r in self.reminders if r.status == "active"]
    
    def get_by_id(self, reminder_id: str) -> Optional[Reminder]:
        """Get reminder by ID"""
        for r in self.reminders:
            if r.id == reminder_id:
                return r
        return None
    
    def delete(self, reminder_id: str) -> bool:
        """Delete a reminder by ID"""
        for i, r in enumerate(self.reminders):
            if r.id == reminder_id:
                self.reminders.pop(i)
                self._save()
                print(f"  🗑️ Deleted reminder: {r.message}")
                return True
        return False
    
    def delete_by_index(self, index: int) -> bool:
        """Delete reminder by index (1-based)"""
        active = self.get_all()
        if 1 <= index <= len(active):
            return self.delete(active[index - 1].id)
        return False
    
    def clear_all(self) -> int:
        """Clear all reminders"""
        count = len(self.reminders)
        self.reminders = []
        self._save()
        print(f"  🗑️ Cleared {count} reminders")
        return count
    
    def snooze(self, reminder_id: str, minutes: int = 5) -> bool:
        """Snooze a reminder"""
        reminder = self.get_by_id(reminder_id)
        if reminder:
            reminder.trigger_time = datetime.datetime.now() + datetime.timedelta(minutes=minutes)
            reminder.status = "active"
            self._save()
            print(f"  😴 Snoozed reminder for {minutes} minutes")
            return True
        return False
    
    def start(self):
        """Start background checking thread"""
        if self._running:
            print("  ⚠️ Reminder checker already running")
            return
        
        self._running = True
        self._thread = threading.Thread(target=self._check_loop, daemon=True)
        self._thread.start()
        print("  🚀 Reminder checker started")
    
    def stop(self):
        """Stop background checking"""
        self._running = False
        if self._thread:
            self._thread.join(timeout=2)
        print("  🛑 Reminder checker stopped")
    
    def _check_loop(self):
        """Background loop that checks for due reminders"""
        print("  🔄 Reminder check loop running...")
        while self._running:
            try:
                self._check_reminders()
                time.sleep(1)  # Check every second
            except Exception as e:
                print(f"  ⚠️ Error in reminder check loop: {e}")
                time.sleep(5)
    
    def _check_reminders(self):
        """Check if any reminders are due"""
        for reminder in self.reminders[:]:  # Copy list to allow modification
            if reminder.status == "active" and reminder.is_due():
                self._trigger(reminder)
    
    def _trigger(self, reminder: Reminder):
        """Trigger a reminder"""
        print(f"  🔔 TRIGGERED: {reminder.message}")
        reminder.status = "triggered"
        self.triggered_queue.append(reminder)
        
        # Handle recurring reminders
        if reminder.recurring and reminder.recurring_time:
            hour, minute = map(int, reminder.recurring_time.split(':'))
            next_time = datetime.datetime.now().replace(
                hour=hour, minute=minute, second=0, microsecond=0
            ) + datetime.timedelta(days=1)
            print(f"  🔁 Scheduling recurring reminder for tomorrow")
            self.add(reminder.message, next_time, reminder.reminder_type, True, reminder.recurring_time)
        
        # Call callback if set
        if self.on_trigger:
            try:
                self.on_trigger(reminder)
            except Exception as e:
                print(f"  ⚠️ Error in trigger callback: {e}")
        
        self._save()
    
    def get_triggered(self) -> List[Reminder]:
        """Get and clear triggered reminders queue"""
        triggered = self.triggered_queue.copy()
        self.triggered_queue = []
        return triggered
    
    def format_list(self) -> str:
        """Format all reminders as text"""
        active = sorted(self.get_all(), key=lambda r: r.trigger_time)
        
        if not active:
            return "📋 No active reminders."
        
        lines = [f"📋 You have {len(active)} reminder{'s' if len(active) != 1 else ''}:\n"]
        for i, r in enumerate(active, 1):
            time_str = r.trigger_time.strftime("%I:%M %p")
            icon = {"reminder": "📝", "alarm": "⏰", "timer": "⏱️"}.get(r.reminder_type, "📝")
            recurring = " 🔁" if r.recurring else ""
            
            if r.trigger_time.date() == datetime.datetime.now().date():
                date_str = "Today"
            elif r.trigger_time.date() == (datetime.datetime.now() + datetime.timedelta(days=1)).date():
                date_str = "Tomorrow"
            else:
                date_str = r.trigger_time.strftime("%b %d")
            
            lines.append(f"{i}. {icon} {r.message}{recurring}")
            lines.append(f"   {date_str} at {time_str} (in {r.time_until()})")
        
        return "\n".join(lines)


class TimeParser:
    """Parses natural language time expressions."""
    
    @staticmethod
    def parse_relative(text: str) -> Optional[Dict]:
        """Parse relative time expressions like '5 minutes', '2 hours 30 minutes'"""
        text = text.lower()
        result = {}
        
        # Hours
        match = re.search(r'(\d+)\s*(?:hour|hr|h)s?', text)
        if match:
            result['hours'] = int(match.group(1))
        
        # Minutes
        match = re.search(r'(\d+)\s*(?:minute|min|m)(?:ute)?s?', text)
        if match:
            result['minutes'] = int(match.group(1))
        
        # Seconds
        match = re.search(r'(\d+)\s*(?:second|sec|s)s?', text)
        if match:
            result['seconds'] = int(match.group(1))
        
        # Half hour
        if 'half hour' in text or 'half an hour' in text:
            result['minutes'] = result.get('minutes', 0) + 30
        
        return result if result else None
    
    @staticmethod
    def parse_absolute(text: str) -> Optional[Dict]:
        """Parse absolute time expressions like '5pm', '14:30'"""
        text = text.lower()
        
        # 12-hour: "5pm", "5:30pm", "5 pm"
        match = re.search(r'(\d{1,2})(?::(\d{2}))?\s*(am|pm)', text)
        if match:
            hour = int(match.group(1))
            minute = int(match.group(2)) if match.group(2) else 0
            ampm = match.group(3)
            
            if ampm == 'pm' and hour != 12:
                hour += 12
            elif ampm == 'am' and hour == 12:
                hour = 0
            
            return {'hour': hour, 'minute': minute}
        
        # 24-hour: "14:30"
        match = re.search(r'(\d{1,2}):(\d{2})(?!\s*(?:am|pm))', text)
        if match:
            return {'hour': int(match.group(1)), 'minute': int(match.group(2))}
        
        # O'clock: "5 o'clock"
        match = re.search(r'(\d{1,2})\s*o\'?clock', text)
        if match:
            hour = int(match.group(1))
            if 1 <= hour <= 6:
                hour += 12
            return {'hour': hour, 'minute': 0}
        
        # Special times
        specials = {
            'noon': (12, 0), 'midnight': (0, 0),
            'morning': (9, 0), 'afternoon': (14, 0),
            'evening': (18, 0), 'night': (21, 0)
        }
        for word, (h, m) in specials.items():
            if word in text:
                return {'hour': h, 'minute': m}
        
        return None
    
    @staticmethod
    def extract_message(text: str) -> str:
        """Extract reminder message from command text"""
        # Remove command prefixes
        prefixes = [
            r'^remind\s+me\s+(?:to\s+)?',
            r'^set\s+(?:a\s+)?reminder\s+(?:to\s+)?',
            r'^don\'t\s+(?:let\s+me\s+)?forget\s+(?:to\s+)?',
        ]
        
        message = text
        for p in prefixes:
            message = re.sub(p, '', message, flags=re.IGNORECASE)
        
        # Remove time expressions
        time_patterns = [
            r'\s+in\s+\d+\s*(?:minutes?|mins?|hours?|hrs?|seconds?|secs?).*$',
            r'\s+at\s+\d{1,2}(?::\d{2})?\s*(?:am|pm)?.*$',
            r'\s+at\s+(?:noon|midnight|morning|afternoon|evening|night).*$',
            r'\s+tomorrow.*$',
            r'\s+today.*$',
        ]
        
        for p in time_patterns:
            message = re.sub(p, '', message, flags=re.IGNORECASE)
        
        return message.strip() or "Reminder"


# =====================================================
# GLOBAL INSTANCE
# =====================================================

_manager: Optional[ReminderManager] = None

def get_reminder_manager() -> ReminderManager:
    """Get or create global reminder manager instance"""
    global _manager
    if _manager is None:
        print("  🚀 Creating reminder manager...")
        _manager = ReminderManager()
        _manager.start()  # CRITICAL: Start background checking
        print("  ✅ Reminder manager ready")
    return _manager


# =====================================================
# COMMAND PROCESSING
# =====================================================

def process_reminder_command(command: str) -> tuple:
    """Process reminder command. Returns (success, response)."""
    manager = get_reminder_manager()
    text = command.lower().strip()
    
    # List reminders
    if any(x in text for x in ['show reminder', 'list reminder', 'my reminder', 'what reminder']):
        return True, manager.format_list()
    
    # Delete reminders
    if any(x in text for x in ['delete reminder', 'cancel reminder', 'remove reminder', 'clear reminder']):
        if 'all' in text:
            count = manager.clear_all()
            return True, f"🗑️ Cleared {count} reminders."
        
        match = re.search(r'(?:delete|cancel|remove)\s+reminder\s*(\d+)', text)
        if match:
            idx = int(match.group(1))
            if manager.delete_by_index(idx):
                return True, f"🗑️ Deleted reminder {idx}."
            return False, f"Reminder {idx} not found."
        
        return False, "Specify which reminder (e.g., 'delete reminder 1')."
    
    # Set timer
    if 'timer' in text:
        duration = TimeParser.parse_relative(text)
        if duration:
            mins = duration.get('minutes', 0) + duration.get('hours', 0) * 60
            secs = duration.get('seconds', 0)
            if mins > 0 or secs > 0:
                r = manager.set_timer(mins, secs)
                return True, f"⏱️ Timer set for {r.time_until()}!"
        return False, "Specify duration (e.g., 'set timer for 10 minutes')."
    
    # Set alarm
    if 'alarm' in text:
        time_info = TimeParser.parse_absolute(text)
        if time_info:
            recurring = 'daily' in text or 'every' in text
            r = manager.set_alarm(time_info['hour'], time_info['minute'], recurring)
            time_str = r.trigger_time.strftime("%I:%M %p")
            rec_str = " (daily)" if recurring else ""
            return True, f"⏰ Alarm set for {time_str}{rec_str}!"
        return False, "Specify time (e.g., 'set alarm for 7am')."
    
    # Set reminder
    if any(x in text for x in ['remind', 'don\'t forget']):
        message = TimeParser.extract_message(command)
        
        # Try relative time
        relative = TimeParser.parse_relative(text)
        if relative:
            r = manager.add_relative(
                message,
                hours=relative.get('hours', 0),
                minutes=relative.get('minutes', 0),
                seconds=relative.get('seconds', 0)
            )
            return True, f"📝 Reminder set: '{message}' in {r.time_until()}."
        
        # Try absolute time
        absolute = TimeParser.parse_absolute(text)
        if absolute:
            recurring = 'daily' in text or 'every' in text
            r = manager.add_at_time(message, absolute['hour'], absolute['minute'], recurring=recurring)
            time_str = r.trigger_time.strftime("%I:%M %p")
            date_str = "today" if r.trigger_time.date() == datetime.datetime.now().date() else "tomorrow"
            rec_str = " (daily)" if recurring else ""
            return True, f"📝 Reminder: '{message}' at {time_str} {date_str}{rec_str}."
        
        return False, "Specify when (e.g., 'in 30 minutes' or 'at 5pm')."
    
    # Snooze
    if 'snooze' in text:
        triggered = manager.get_triggered()
        if triggered:
            mins = 5
            match = re.search(r'(\d+)\s*min', text)
            if match:
                mins = int(match.group(1))
            manager.snooze(triggered[-1].id, mins)
            return True, f"😴 Snoozed for {mins} minutes."
        return False, "No reminder to snooze."
    
    return False, None


# =====================================================
# TEST
# =====================================================

if __name__ == "__main__":
    print("\n🔔 Testing Reminder System\n")
    
    tests = [
        "set timer for 5 minutes",
        "set timer for 10 seconds",
        "remind me to take a break in 30 minutes",
        "set alarm for 7am",
        "show my reminders",
    ]
    
    for cmd in tests:
        success, response = process_reminder_command(cmd)
        print(f"'{cmd}'")
        print(f"  → {response}\n")
    
    print("Waiting 15 seconds to see if 10-second timer triggers...")
    time.sleep(15)
    
    manager = get_reminder_manager()
    triggered = manager.get_triggered()
    if triggered:
        print(f"✅ Got triggered reminders: {[r.message for r in triggered]}")
    else:
        print("❌ No triggered reminders")
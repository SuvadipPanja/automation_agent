import json
import sqlite3
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional


class MemorySystem:
    """
    ARES Memory System - Persistent user memory and conversation history.
    
    Stores:
    - User profile (name, preferences, interests)
    - Conversation history
    - Learned preferences
    - Important facts about the user
    """
    
    def __init__(self, db_path: str = "data/ares_memory.db"):
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self.init_database()
    
    def init_database(self):
        """Initialize SQLite database with tables for memory."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # User profile table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS user_profile (
                key TEXT PRIMARY KEY,
                value TEXT NOT NULL,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Conversation history table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS conversations (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                user_message TEXT NOT NULL,
                ares_response TEXT NOT NULL,
                context_used TEXT
            )
        ''')
        
        # User preferences table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS preferences (
                category TEXT NOT NULL,
                preference TEXT NOT NULL,
                confidence REAL DEFAULT 1.0,
                learned_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                PRIMARY KEY (category, preference)
            )
        ''')
        
        # Important facts table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS facts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                fact TEXT NOT NULL,
                category TEXT,
                importance REAL DEFAULT 1.0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        conn.commit()
        conn.close()
    
    # =====================================
    # USER PROFILE MANAGEMENT
    # =====================================
    
    def set_user_info(self, key: str, value: str):
        """Store user information (name, email, location, etc.)"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT OR REPLACE INTO user_profile (key, value, updated_at)
            VALUES (?, ?, ?)
        ''', (key, value, datetime.now().isoformat()))
        
        conn.commit()
        conn.close()
    
    def get_user_info(self, key: str) -> Optional[str]:
        """Retrieve user information."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('SELECT value FROM user_profile WHERE key = ?', (key,))
        result = cursor.fetchone()
        
        conn.close()
        return result[0] if result else None
    
    def get_full_profile(self) -> Dict[str, str]:
        """Get complete user profile."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('SELECT key, value FROM user_profile')
        profile = {row[0]: row[1] for row in cursor.fetchall()}
        
        conn.close()
        return profile
    
    # =====================================
    # CONVERSATION HISTORY
    # =====================================
    
    def save_conversation(self, user_message: str, ares_response: str, context: str = ""):
        """Save a conversation turn."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO conversations (user_message, ares_response, context_used)
            VALUES (?, ?, ?)
        ''', (user_message, ares_response, context))
        
        conn.commit()
        conn.close()
    
    def get_recent_conversations(self, limit: int = 10) -> List[Dict]:
        """Get recent conversation history."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT timestamp, user_message, ares_response
            FROM conversations
            ORDER BY timestamp DESC
            LIMIT ?
        ''', (limit,))
        
        conversations = []
        for row in cursor.fetchall():
            conversations.append({
                'timestamp': row[0],
                'user': row[1],
                'ares': row[2]
            })
        
        conn.close()
        return list(reversed(conversations))  # Return in chronological order
    
    def search_conversations(self, keyword: str, limit: int = 5) -> List[Dict]:
        """Search past conversations by keyword."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT timestamp, user_message, ares_response
            FROM conversations
            WHERE user_message LIKE ? OR ares_response LIKE ?
            ORDER BY timestamp DESC
            LIMIT ?
        ''', (f'%{keyword}%', f'%{keyword}%', limit))
        
        conversations = []
        for row in cursor.fetchall():
            conversations.append({
                'timestamp': row[0],
                'user': row[1],
                'ares': row[2]
            })
        
        conn.close()
        return conversations
    
    # =====================================
    # PREFERENCES & LEARNING
    # =====================================
    
    def learn_preference(self, category: str, preference: str, confidence: float = 1.0):
        """Learn a user preference."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT OR REPLACE INTO preferences (category, preference, confidence, learned_at)
            VALUES (?, ?, ?, ?)
        ''', (category, preference, confidence, datetime.now().isoformat()))
        
        conn.commit()
        conn.close()
    
    def get_preferences(self, category: Optional[str] = None) -> Dict[str, List[str]]:
        """Get user preferences, optionally filtered by category."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        if category:
            cursor.execute('''
                SELECT category, preference FROM preferences
                WHERE category = ?
                ORDER BY confidence DESC
            ''', (category,))
        else:
            cursor.execute('''
                SELECT category, preference FROM preferences
                ORDER BY category, confidence DESC
            ''')
        
        preferences = {}
        for row in cursor.fetchall():
            cat, pref = row[0], row[1]
            if cat not in preferences:
                preferences[cat] = []
            preferences[cat].append(pref)
        
        conn.close()
        return preferences
    
    # =====================================
    # IMPORTANT FACTS
    # =====================================
    
    def add_fact(self, fact: str, category: str = "general", importance: float = 1.0):
        """Store an important fact about the user."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO facts (fact, category, importance)
            VALUES (?, ?, ?)
        ''', (fact, category, importance))
        
        conn.commit()
        conn.close()
    
    def get_facts(self, category: Optional[str] = None, limit: int = 10) -> List[str]:
        """Retrieve important facts about the user."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        if category:
            cursor.execute('''
                SELECT fact FROM facts
                WHERE category = ?
                ORDER BY importance DESC, created_at DESC
                LIMIT ?
            ''', (category, limit))
        else:
            cursor.execute('''
                SELECT fact FROM facts
                ORDER BY importance DESC, created_at DESC
                LIMIT ?
            ''', (limit,))
        
        facts = [row[0] for row in cursor.fetchall()]
        
        conn.close()
        return facts
    
    # =====================================
    # CONTEXT GENERATION
    # =====================================
    
    def get_context_for_llm(self) -> str:
        """Generate context string to inject into LLM prompts."""
        profile = self.get_full_profile()
        preferences = self.get_preferences()
        facts = self.get_facts(limit=5)
        recent_convos = self.get_recent_conversations(limit=3)
        
        context_parts = []
        
        # User profile
        if profile:
            context_parts.append("USER PROFILE:")
            for key, value in profile.items():
                context_parts.append(f"- {key}: {value}")
        
        # Important facts
        if facts:
            context_parts.append("\nIMPORTANT FACTS:")
            for fact in facts:
                context_parts.append(f"- {fact}")
        
        # Preferences
        if preferences:
            context_parts.append("\nUSER PREFERENCES:")
            for category, prefs in preferences.items():
                context_parts.append(f"- {category}: {', '.join(prefs)}")
        
        # Recent context (last 3 messages)
        if recent_convos:
            context_parts.append("\nRECENT CONVERSATION:")
            for convo in recent_convos[-3:]:
                context_parts.append(f"User: {convo['user']}")
                context_parts.append(f"ARES: {convo['ares']}")
        
        return "\n".join(context_parts)
    
    # =====================================
    # MEMORY MANAGEMENT
    # =====================================
    
    def clear_conversations(self):
        """Clear conversation history (but keep profile and preferences)."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('DELETE FROM conversations')
        conn.commit()
        conn.close()
    
    def clear_all_memory(self):
        """Clear ALL memory (reset everything)."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('DELETE FROM user_profile')
        cursor.execute('DELETE FROM conversations')
        cursor.execute('DELETE FROM preferences')
        cursor.execute('DELETE FROM facts')
        conn.commit()
        conn.close()
    
    def export_memory(self) -> Dict:
        """Export all memory to a dictionary."""
        return {
            'profile': self.get_full_profile(),
            'preferences': self.get_preferences(),
            'facts': self.get_facts(limit=100),
            'recent_conversations': self.get_recent_conversations(limit=50)
        }
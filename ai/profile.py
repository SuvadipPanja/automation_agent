import json
from pathlib import Path
from datetime import datetime
from typing import Optional, Dict, Any


class UserProfile:
    """
    Manages user profile information, preferences, and personal data.
    ARES uses this to personalize interactions and remember the user.
    """

    def __init__(self, profile_path: str = "data/user_profile.json"):
        self.profile_path = Path(profile_path)
        self.profile_path.parent.mkdir(exist_ok=True)
        self.data = self._load_profile()

    def _load_profile(self) -> Dict[str, Any]:
        """Load user profile from file"""
        if self.profile_path.exists():
            try:
                with open(self.profile_path, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception as e:
                print(f"Error loading profile: {e}")
                return self._default_profile()
        return self._default_profile()

    def _default_profile(self) -> Dict[str, Any]:
        """Create default profile structure"""
        return {
            "user": {
                "name": None,
                "nickname": None,
                "age": None,
                "location": None,
                "occupation": None,
                "timezone": None
            },
            "preferences": {
                "communication_style": "friendly",  # formal, casual, friendly
                "detail_level": "medium",  # brief, medium, detailed
                "language": "English",
                "voice_enabled": True
            },
            "interests": [],
            "skills": [],
            "goals": [],
            "important_facts": [],
            "metadata": {
                "created_at": datetime.now().isoformat(),
                "last_updated": datetime.now().isoformat(),
                "total_conversations": 0,
                "favorite_topics": []
            }
        }

    def _save_profile(self):
        """Save profile to file"""
        try:
            self.data["metadata"]["last_updated"] = datetime.now().isoformat()
            with open(self.profile_path, 'w', encoding='utf-8') as f:
                json.dump(self.data, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"Error saving profile: {e}")

    # ========================
    # USER INFORMATION
    # ========================

    def set_name(self, name: str):
        """Set user's name"""
        self.data["user"]["name"] = name
        self._save_profile()

    def get_name(self) -> Optional[str]:
        """Get user's name"""
        return self.data["user"].get("name")

    def set_nickname(self, nickname: str):
        """Set user's nickname"""
        self.data["user"]["nickname"] = nickname
        self._save_profile()

    def get_nickname(self) -> Optional[str]:
        """Get user's nickname"""
        return self.data["user"].get("nickname")

    def set_location(self, location: str):
        """Set user's location"""
        self.data["user"]["location"] = location
        self._save_profile()

    def get_location(self) -> Optional[str]:
        """Get user's location"""
        return self.data["user"].get("location")

    def set_occupation(self, occupation: str):
        """Set user's occupation"""
        self.data["user"]["occupation"] = occupation
        self._save_profile()

    def get_occupation(self) -> Optional[str]:
        """Get user's occupation"""
        return self.data["user"].get("occupation")

    # ========================
    # PREFERENCES
    # ========================

    def set_preference(self, key: str, value: Any):
        """Set a preference"""
        self.data["preferences"][key] = value
        self._save_profile()

    def get_preference(self, key: str, default=None) -> Any:
        """Get a preference"""
        return self.data["preferences"].get(key, default)

    # ========================
    # INTERESTS & SKILLS
    # ========================

    def add_interest(self, interest: str):
        """Add an interest"""
        if interest not in self.data["interests"]:
            self.data["interests"].append(interest)
            self._save_profile()

    def remove_interest(self, interest: str):
        """Remove an interest"""
        if interest in self.data["interests"]:
            self.data["interests"].remove(interest)
            self._save_profile()

    def get_interests(self) -> list:
        """Get all interests"""
        return self.data["interests"]

    def add_skill(self, skill: str):
        """Add a skill"""
        if skill not in self.data["skills"]:
            self.data["skills"].append(skill)
            self._save_profile()

    def get_skills(self) -> list:
        """Get all skills"""
        return self.data["skills"]

    # ========================
    # IMPORTANT FACTS
    # ========================

    def add_fact(self, fact: str):
        """Add an important fact about the user"""
        fact_entry = {
            "text": fact,
            "added_at": datetime.now().isoformat()
        }
        self.data["important_facts"].append(fact_entry)
        self._save_profile()

    def get_facts(self) -> list:
        """Get all important facts"""
        return [f["text"] for f in self.data["important_facts"]]

    # ========================
    # CONTEXT SUMMARY
    # ========================

    def get_context_summary(self) -> str:
        """
        Generate a summary of user context for AI prompts
        This is injected into LLM prompts so ARES knows about the user
        """
        name = self.get_name()
        nickname = self.get_nickname()
        location = self.get_location()
        occupation = self.get_occupation()
        interests = self.get_interests()
        skills = self.get_skills()
        facts = self.get_facts()

        summary_parts = []

        # Basic info
        if name:
            display_name = nickname if nickname else name
            summary_parts.append(f"You are talking to {display_name}.")

        if occupation:
            summary_parts.append(f"They work as a {occupation}.")

        if location:
            summary_parts.append(f"They are located in {location}.")

        # Interests
        if interests:
            interests_str = ", ".join(interests[:5])  # Limit to 5
            summary_parts.append(f"Their interests include: {interests_str}.")

        # Skills
        if skills:
            skills_str = ", ".join(skills[:5])
            summary_parts.append(f"They have skills in: {skills_str}.")

        # Important facts
        if facts:
            facts_str = " ".join(facts[:3])  # Limit to 3 most recent
            summary_parts.append(f"Important to know: {facts_str}")

        return " ".join(summary_parts) if summary_parts else ""

    # ========================
    # STATISTICS
    # ========================

    def increment_conversation_count(self):
        """Increment total conversations"""
        self.data["metadata"]["total_conversations"] += 1
        self._save_profile()

    def get_conversation_count(self) -> int:
        """Get total conversations"""
        return self.data["metadata"]["total_conversations"]

    def is_first_time(self) -> bool:
        """Check if this is the first conversation"""
        return self.data["metadata"]["total_conversations"] == 0

    # ========================
    # EXPORT
    # ========================

    def get_full_profile(self) -> Dict[str, Any]:
        """Get complete profile data"""
        return self.data

    def export_summary(self) -> str:
        """Export a human-readable summary"""
        name = self.get_name() or "Unknown"
        lines = [
            f"📋 User Profile: {name}",
            "=" * 50,
            ""
        ]

        if self.get_nickname():
            lines.append(f"Nickname: {self.get_nickname()}")

        if self.get_occupation():
            lines.append(f"Occupation: {self.get_occupation()}")

        if self.get_location():
            lines.append(f"Location: {self.get_location()}")

        if self.get_interests():
            lines.append(f"Interests: {', '.join(self.get_interests())}")

        if self.get_skills():
            lines.append(f"Skills: {', '.join(self.get_skills())}")

        lines.append(f"\nTotal Conversations: {self.get_conversation_count()}")

        return "\n".join(lines)
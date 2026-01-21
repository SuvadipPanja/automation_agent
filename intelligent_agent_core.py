#!/usr/bin/env python3
"""
ARES - ENHANCED AI AGENT VERSION
Real AI Assistant with intelligent app control, song playing, and web automation

Features:
- Open apps intelligently
- Play songs on YouTube/Spotify with search
- Multi-step task execution
- Browser automation
- Real agent-like behavior

Installation:
  pip install selenium webdriver-manager pyautogui psutil
"""

import os
import sys
import time
import json
import psutil
import webbrowser
import subprocess
import re
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Tuple, Optional, Any
from dataclasses import dataclass
from enum import Enum
import threading
import logging

# ===================================================
# IMPORTS FOR WEB AUTOMATION
# ===================================================

try:
    from selenium import webdriver
    from selenium.webdriver.common.by import By
    from selenium.webdriver.common.keys import Keys
    from selenium.webdriver.support.ui import WebDriverWait
    from selenium.webdriver.support import expected_conditions as EC
    from webdriver_manager.chrome import ChromeDriverManager
    SELENIUM_AVAILABLE = True
except ImportError:
    SELENIUM_AVAILABLE = False
    print("⚠️  Selenium not installed. Some features will be limited.")
    print("   Install: pip install selenium webdriver-manager")

try:
    import pyautogui
    PYAUTOGUI_AVAILABLE = True
except ImportError:
    PYAUTOGUI_AVAILABLE = False


# ===================================================
# CONFIGURATION
# ===================================================

class AppRegistry:
    """Registry of applications and their launch methods"""
    
    APPS = {
        # Browsers
        "chrome": {
            "names": ["chrome", "google chrome", "browser"],
            "path": "C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe",
            "alt_paths": [
                "C:\\Program Files (x86)\\Google\\Chrome\\Application\\chrome.exe",
                "C:\\Users\\%USERNAME%\\AppData\\Local\\Google\\Chrome\\Application\\chrome.exe"
            ],
            "type": "browser"
        },
        "edge": {
            "names": ["edge", "microsoft edge"],
            "path": "C:\\Program Files (x86)\\Microsoft\\Edge\\Application\\msedge.exe",
            "alt_paths": [
                "C:\\Program Files\\Microsoft\\Edge\\Application\\msedge.exe"
            ],
            "type": "browser"
        },
        "firefox": {
            "names": ["firefox"],
            "path": "C:\\Program Files\\Mozilla Firefox\\firefox.exe",
            "alt_paths": [
                "C:\\Program Files (x86)\\Mozilla Firefox\\firefox.exe"
            ],
            "type": "browser"
        },
        
        # Development
        "vscode": {
            "names": ["vscode", "vs code", "code"],
            "path": "C:\\Users\\%USERNAME%\\AppData\\Local\\Programs\\Microsoft VS Code\\Code.exe",
            "alt_paths": ["C:\\Program Files\\Microsoft VS Code\\Code.exe"],
            "type": "editor"
        },
        
        # Office
        "notepad": {
            "names": ["notepad"],
            "path": "C:\\Windows\\System32\\notepad.exe",
            "type": "editor"
        },
        "word": {
            "names": ["word", "microsoft word"],
            "path": "C:\\Program Files\\Microsoft Office\\root\\Office16\\WINWORD.EXE",
            "type": "office"
        },
        "excel": {
            "names": ["excel", "microsoft excel"],
            "path": "C:\\Program Files\\Microsoft Office\\root\\Office16\\EXCEL.EXE",
            "type": "office"
        },
        
        # Communication
        "teams": {
            "names": ["teams", "microsoft teams"],
            "path": "C:\\Users\\%USERNAME%\\AppData\\Local\\Microsoft\\Teams\\Teams.exe",
            "type": "communication"
        },
        "discord": {
            "names": ["discord"],
            "path": "C:\\Users\\%USERNAME%\\AppData\\Local\\Discord\\Update.exe",
            "type": "communication"
        },
        
        # File Management
        "explorer": {
            "names": ["explorer", "file explorer"],
            "path": "C:\\Windows\\explorer.exe",
            "type": "system"
        },
        
        # Entertainment
        "spotify": {
            "names": ["spotify"],
            "path": "C:\\Users\\%USERNAME%\\AppData\\Roaming\\Spotify\\spotify.exe",
            "type": "music"
        },
        "vlc": {
            "names": ["vlc", "media player"],
            "path": "C:\\Program Files\\VideoLAN\\VLC\\vlc.exe",
            "type": "media"
        }
    }
    
    @classmethod
    def find_app(cls, app_name: str) -> Optional[Dict[str, Any]]:
        """Find app by name"""
        app_name_lower = app_name.lower().strip()
        
        # Direct match
        if app_name_lower in cls.APPS:
            return cls.APPS[app_name_lower]
        
        # Match by alias
        for app_id, app_info in cls.APPS.items():
            if app_name_lower in app_info.get("names", []):
                return app_info
        
        return None
    
    @classmethod
    def launch_app(cls, app_name: str) -> Tuple[bool, str]:
        """Launch application"""
        app_info = cls.find_app(app_name)
        
        if not app_info:
            return False, f"App '{app_name}' not found in registry"
        
        # Try main path
        path = os.path.expandvars(app_info["path"])
        if os.path.exists(path):
            try:
                subprocess.Popen(path)
                return True, f"Opening {app_name}"
            except Exception as e:
                return False, f"Failed to open {app_name}: {e}"
        
        # Try alternative paths
        for alt_path in app_info.get("alt_paths", []):
            alt_path = os.path.expandvars(alt_path)
            if os.path.exists(alt_path):
                try:
                    subprocess.Popen(alt_path)
                    return True, f"Opening {app_name}"
                except Exception as e:
                    continue
        
        # Try launching by name (Windows search)
        try:
            os.system(f"start {app_name}")
            return True, f"Opening {app_name}"
        except:
            return False, f"Could not find or open {app_name}"


# ===================================================
# WEB AUTOMATION MODULE
# ===================================================

class WebAgent:
    """Web automation agent for browser control"""
    
    def __init__(self):
        self.driver = None
        self.wait = None
        self.logger = logging.getLogger("WebAgent")
    
    def initialize_browser(self, headless: bool = False) -> bool:
        """Initialize Selenium WebDriver"""
        if not SELENIUM_AVAILABLE:
            self.logger.warning("Selenium not available")
            return False
        
        try:
            options = webdriver.ChromeOptions()
            if headless:
                options.add_argument("--headless")
            
            self.driver = webdriver.Chrome(
                service=webdriver.chrome_service.Service(
                    ChromeDriverManager().install()
                ),
                options=options
            )
            self.wait = WebDriverWait(self.driver, 10)
            self.logger.info("Browser initialized")
            return True
        except Exception as e:
            self.logger.error(f"Browser initialization failed: {e}")
            return False
    
    def close_browser(self):
        """Close browser"""
        if self.driver:
            try:
                self.driver.quit()
                self.logger.info("Browser closed")
            except:
                pass
            self.driver = None
    
    def open_youtube_and_play(self, song_name: str) -> Tuple[bool, str]:
        """Open YouTube and play a song"""
        if not self.driver:
            if not self.initialize_browser():
                return False, "Could not initialize browser"
        
        try:
            # Navigate to YouTube
            self.driver.get("https://www.youtube.com")
            time.sleep(2)
            
            # Find search box
            search_box = self.wait.until(
                EC.presence_of_element_located((By.NAME, "search_query"))
            )
            
            # Type song name
            search_box.clear()
            search_box.send_keys(song_name)
            search_box.send_keys(Keys.RETURN)
            
            time.sleep(3)
            
            # Click first video
            first_video = self.wait.until(
                EC.element_to_be_clickable(
                    (By.CSS_SELECTOR, "ytd-video-renderer:first-child a#video-title")
                )
            )
            first_video.click()
            
            time.sleep(2)
            
            self.logger.info(f"Playing '{song_name}' on YouTube")
            return True, f"Playing '{song_name}' on YouTube"
        
        except Exception as e:
            self.logger.error(f"YouTube play error: {e}")
            return False, f"Error playing song: {e}"
    
    def open_spotify_and_play(self, song_name: str) -> Tuple[bool, str]:
        """Open Spotify and search for a song"""
        try:
            # Try to launch Spotify app first
            success, msg = AppRegistry.launch_app("spotify")
            if success:
                time.sleep(3)
            
            # Open Spotify web
            webbrowser.open("https://open.spotify.com/search")
            time.sleep(2)
            
            if self.driver:
                self.driver.get("https://open.spotify.com/search")
                time.sleep(2)
                
                # Find and fill search
                try:
                    search_box = self.wait.until(
                        EC.presence_of_element_located((By.CSS_SELECTOR, "input[type='search']"))
                    )
                    search_box.send_keys(song_name)
                    search_box.send_keys(Keys.RETURN)
                    
                    time.sleep(3)
                    
                    # Click first result
                    first_result = self.wait.until(
                        EC.element_to_be_clickable((By.CSS_SELECTOR, "a[href*='/track/']"))
                    )
                    first_result.click()
                    
                    return True, f"Playing '{song_name}' on Spotify"
                except:
                    pass
            
            return True, f"Opened Spotify to search '{song_name}'"
        
        except Exception as e:
            return False, f"Spotify error: {e}"
    
    def open_url_in_app(self, app_name: str, url: str) -> Tuple[bool, str]:
        """Open URL in specific app"""
        app_info = AppRegistry.find_app(app_name)
        
        if not app_info:
            return False, f"App '{app_name}' not found"
        
        try:
            # Launch app with URL
            path = os.path.expandvars(app_info["path"])
            if os.path.exists(path):
                subprocess.Popen([path, url])
                return True, f"Opening {url} in {app_name}"
        
        except Exception as e:
            pass
        
        # Fallback: use default browser
        webbrowser.open(url)
        return True, f"Opening {url} in default browser"


# ===================================================
# INTELLIGENT COMMAND PARSER
# ===================================================

class IntelligentParser:
    """Parse commands with intent detection and entity extraction"""
    
    # Intent patterns
    PATTERNS = {
        "play_song": [
            r"play\s+(.+?)(?:\s+on\s+(?:youtube|spotify))?$",
            r"play\s+(?:song\s+)?(.+?)(?:\s+on\s+(?:youtube|spotify))?$",
            r"(?:can\s+you\s+)?play\s+(.+?)$",
        ],
        "open_app_and_site": [
            r"open\s+(.+?)\s+and\s+(.+?)$",
            r"open\s+(.+?)\s+(?:to|at)\s+(.+?)$",
        ],
        "open_app": [
            r"open\s+(.+?)$",
            r"launch\s+(.+?)$",
            r"start\s+(.+?)$",
        ],
        "search_online": [
            r"(?:search|find|look\s+for)\s+(.+?)(?:\s+on\s+(?:google|youtube|web))?$",
        ],
    }
    
    @classmethod
    def parse(cls, command: str) -> Tuple[str, Dict[str, Any]]:
        """Parse command and return intent + entities"""
        command_lower = command.lower().strip()
        
        # Play song
        for pattern in cls.PATTERNS["play_song"]:
            match = re.match(pattern, command_lower)
            if match:
                song_name = match.group(1).strip()
                
                # Detect if Spotify or YouTube mentioned
                platform = "youtube"
                if "spotify" in command_lower:
                    platform = "spotify"
                
                return "play_song", {
                    "song_name": song_name,
                    "platform": platform
                }
        
        # Open app and go to site
        for pattern in cls.PATTERNS["open_app_and_site"]:
            match = re.match(pattern, command_lower)
            if match:
                app = match.group(1).strip()
                destination = match.group(2).strip()
                return "open_app_and_site", {
                    "app": app,
                    "destination": destination
                }
        
        # Open app
        for pattern in cls.PATTERNS["open_app"]:
            match = re.match(pattern, command_lower)
            if match:
                app = match.group(1).strip()
                return "open_app", {
                    "app": app
                }
        
        # Search online
        for pattern in cls.PATTERNS["search_online"]:
            match = re.match(pattern, command_lower)
            if match:
                query = match.group(1).strip()
                return "search_online", {
                    "query": query
                }
        
        return "unknown", {}


# ===================================================
# INTELLIGENT AGENT EXECUTOR
# ===================================================

class IntelligentAgent:
    """AI Agent that executes commands intelligently"""
    
    def __init__(self):
        self.logger = logging.getLogger("IntelligentAgent")
        self.web_agent = WebAgent()
        self.command_history = []
    
    def execute(self, command: str) -> Tuple[bool, str]:
        """Execute command intelligently"""
        self.logger.info(f"Processing: {command}")
        
        # Parse command
        intent, entities = IntelligentParser.parse(command)
        self.logger.info(f"Intent: {intent}, Entities: {entities}")
        
        # Execute based on intent
        if intent == "play_song":
            return self._play_song(entities)
        
        elif intent == "open_app_and_site":
            return self._open_app_and_site(entities)
        
        elif intent == "open_app":
            return self._open_app(entities)
        
        elif intent == "search_online":
            return self._search_online(entities)
        
        else:
            return False, "Could not understand command"
    
    def _play_song(self, entities: Dict[str, Any]) -> Tuple[bool, str]:
        """Play a song on YouTube or Spotify"""
        song_name = entities.get("song_name", "")
        platform = entities.get("platform", "youtube")
        
        if not song_name:
            return False, "No song name provided"
        
        self.logger.info(f"Playing '{song_name}' on {platform}")
        
        if platform == "spotify":
            return self.web_agent.open_spotify_and_play(song_name)
        else:
            # YouTube is default
            return self.web_agent.open_youtube_and_play(song_name)
    
    def _open_app_and_site(self, entities: Dict[str, Any]) -> Tuple[bool, str]:
        """Open app and navigate to destination"""
        app = entities.get("app", "").strip()
        destination = entities.get("destination", "").strip()
        
        if not app:
            return False, "No app specified"
        
        # Map common destinations
        url_map = {
            "youtube": "https://youtube.com",
            "google": "https://google.com",
            "facebook": "https://facebook.com",
            "gmail": "https://gmail.com",
            "twitter": "https://twitter.com",
            "reddit": "https://reddit.com",
            "github": "https://github.com",
        }
        
        # Get URL
        url = url_map.get(destination.lower(), f"https://{destination}")
        
        self.logger.info(f"Opening {url} in {app}")
        
        # Launch app
        success, msg = AppRegistry.launch_app(app)
        if not success:
            return False, f"Could not open {app}"
        
        time.sleep(2)
        
        # Open URL
        return self.web_agent.open_url_in_app(app, url)
    
    def _open_app(self, entities: Dict[str, Any]) -> Tuple[bool, str]:
        """Open application"""
        app = entities.get("app", "").strip()
        
        if not app:
            return False, "No app specified"
        
        self.logger.info(f"Opening {app}")
        return AppRegistry.launch_app(app)
    
    def _search_online(self, entities: Dict[str, Any]) -> Tuple[bool, str]:
        """Search online"""
        query = entities.get("query", "").strip()
        
        if not query:
            return False, "No search query provided"
        
        search_url = f"https://www.google.com/search?q={query.replace(' ', '+')}"
        webbrowser.open(search_url)
        
        return True, f"Searching for '{query}' on Google"
    
    def shutdown(self):
        """Shutdown agent"""
        self.web_agent.close_browser()


# ===================================================
# LOGGING SETUP
# ===================================================

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)


# ===================================================
# EXAMPLE USAGE
# ===================================================

if __name__ == "__main__":
    agent = IntelligentAgent()
    
    # Test commands
    test_commands = [
        "play tum hi ho",
        "play shape of you on spotify",
        "open youtube",
        "open chrome and google",
        "open edge and youtube",
        "search for python tutorials",
        "play despacito",
    ]
    
    print("\n" + "="*60)
    print("ARES - INTELLIGENT AI AGENT")
    print("="*60 + "\n")
    
    for command in test_commands:
        print(f"\n📝 Command: {command}")
        success, message = agent.execute(command)
        print(f"✅ {message}" if success else f"❌ {message}")
        time.sleep(2)
    
    agent.shutdown()
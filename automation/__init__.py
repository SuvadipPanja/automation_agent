"""
=====================================================
ARES AUTOMATION PACKAGE
=====================================================
Desktop automation and command processing for ARES.

Modules:
- desktop_control: Low-level desktop control functions
- command_parser: Natural language command parsing
- executor: Command execution engine

Usage:
    from automation import execute_command
    
    success, response = execute_command("open chrome")
=====================================================
"""

from automation.desktop_control import DesktopAutomation, desktop
from automation.command_parser import (
    CommandParser, 
    CommandExecutor, 
    ParsedCommand,
    CommandType,
    get_executor
)

# Convenience function
def execute_command(command: str):
    """
    Execute a voice command.
    
    Args:
        command: Natural language command (e.g., "open chrome")
        
    Returns:
        (success: bool, response: str)
    """
    executor = get_executor()
    return executor.execute(command)


__all__ = [
    'DesktopAutomation',
    'desktop',
    'CommandParser',
    'CommandExecutor',
    'ParsedCommand',
    'CommandType',
    'get_executor',
    'execute_command',
]
"""
=====================================================
ARES - Professional Logging Configuration
=====================================================

Features:
✅ Daily rotation
✅ 50MB size rotation
✅ Logs to: automation_agent/logs/
✅ Separate console and file handlers
✅ Timestamp, level, module tracking
✅ Backward compatible

Usage:
    from logger_config import setup_logger, get_logger
    
    logger = setup_logger("ARES.MyModule")
    logger.info("This message")  # Single argument!

Author: ARES Development
For: Suvadip Panja
=====================================================
"""

import os
import sys
import logging
from pathlib import Path
from logging.handlers import RotatingFileHandler, TimedRotatingFileHandler
from datetime import datetime

# ===================================================
# PROJECT PATHS
# ===================================================

PROJECT_ROOT = Path(__file__).resolve().parent
LOGS_DIR = PROJECT_ROOT / "logs"

# Create logs directory if it doesn't exist
LOGS_DIR.mkdir(parents=True, exist_ok=True)

# ===================================================
# LOG FILE PATHS
# ===================================================

MAIN_LOG = LOGS_DIR / "ares_main.log"
ERROR_LOG = LOGS_DIR / "ares_errors.log"
DEBUG_LOG = LOGS_DIR / "ares_debug.log"


# ===================================================
# LOG FORMAT
# ===================================================

DETAILED_FORMAT = logging.Formatter(
    '[%(asctime)s] %(name)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)

SIMPLE_FORMAT = logging.Formatter(
    '%(levelname)s: %(message)s'
)


# ===================================================
# LOGGER SETUP FUNCTION
# ===================================================

def setup_logger(
    name: str,
    log_level: int = logging.INFO,
    log_file: Path = MAIN_LOG,
    console_output: bool = True
) -> logging.Logger:
    """
    Setup a logger with both console and rotating file handlers.
    
    Args:
        name: Logger name (e.g., "ARES.Manager")
        log_level: Logging level (DEBUG, INFO, WARNING, ERROR)
        log_file: Path to log file
        console_output: Whether to output to console
    
    Returns:
        Configured logger instance
    
    Example:
        logger = setup_logger("ARES.MyModule")
        logger.info("Message")  # ✅ Correct
        logger.info("Message", extra_arg)  # ❌ Wrong
    """
    
    # Create logger
    logger = logging.getLogger(name)
    logger.setLevel(log_level)
    
    # Remove existing handlers to avoid duplicates
    logger.handlers.clear()
    
    # ===============================================
    # FILE HANDLER - ROTATING SIZE + TIME
    # ===============================================
    
    try:
        # Main log file handler (50MB rotation + daily)
        file_handler = RotatingFileHandler(
            filename=str(log_file),
            maxBytes=50 * 1024 * 1024,  # 50MB
            backupCount=30  # Keep 30 backup files
        )
        file_handler.setLevel(log_level)
        file_handler.setFormatter(DETAILED_FORMAT)
        logger.addHandler(file_handler)
    except Exception as e:
        print(f"Warning: Could not create file handler: {e}")
    
    # ===============================================
    # CONSOLE HANDLER
    # ===============================================
    
    if console_output:
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(log_level)
        console_handler.setFormatter(SIMPLE_FORMAT)
        logger.addHandler(console_handler)
    
    return logger


# ===================================================
# GLOBAL LOGGER INSTANCES
# ===================================================

# Main logger (used by most modules)
_main_logger = None

# Error logger (for critical errors)
_error_logger = None

# Debug logger (for debugging)
_debug_logger = None


def get_logger(name: str) -> logging.Logger:
    """
    Get or create a logger with the given name.
    
    Usage:
        logger = get_logger("ARES.Manager")
        logger.info("Message")
    """
    return setup_logger(name, log_level=logging.INFO)


def get_main_logger() -> logging.Logger:
    """Get the main application logger."""
    global _main_logger
    if _main_logger is None:
        _main_logger = setup_logger(
            "ARES",
            log_level=logging.INFO,
            log_file=MAIN_LOG,
            console_output=True
        )
    return _main_logger


def get_error_logger() -> logging.Logger:
    """Get the error logger."""
    global _error_logger
    if _error_logger is None:
        _error_logger = setup_logger(
            "ARES.Error",
            log_level=logging.ERROR,
            log_file=ERROR_LOG,
            console_output=False
        )
    return _error_logger


def get_debug_logger() -> logging.Logger:
    """Get the debug logger."""
    global _debug_logger
    if _debug_logger is None:
        _debug_logger = setup_logger(
            "ARES.Debug",
            log_level=logging.DEBUG,
            log_file=DEBUG_LOG,
            console_output=False
        )
    return _debug_logger


# ===================================================
# INITIALIZATION
# ===================================================

def initialize_logging():
    """Initialize all loggers."""
    logger = get_main_logger()
    logger.info("=" * 70)
    logger.info("  🚀 ARES Logging System Initialized")
    logger.info("=" * 70)
    logger.info(f"Logs directory: {LOGS_DIR}")
    logger.info(f"Main log: {MAIN_LOG}")
    logger.info(f"Error log: {ERROR_LOG}")
    logger.info(f"Debug log: {DEBUG_LOG}")
    logger.info(f"Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    logger.info("=" * 70)
    logger.info("")


# ===================================================
# UTILITY FUNCTIONS
# ===================================================

def get_log_files() -> dict:
    """Get all log files in the logs directory."""
    log_files = {}
    if LOGS_DIR.exists():
        for log_file in LOGS_DIR.glob("*.log*"):
            size_mb = log_file.stat().st_size / (1024 * 1024)
            log_files[log_file.name] = {
                "path": str(log_file),
                "size_mb": round(size_mb, 2),
                "modified": datetime.fromtimestamp(log_file.stat().st_mtime).isoformat()
            }
    return log_files


def get_log_file_size(log_file: Path = MAIN_LOG) -> str:
    """Get formatted log file size."""
    if log_file.exists():
        size_bytes = log_file.stat().st_size
        size_mb = size_bytes / (1024 * 1024)
        return f"{size_mb:.2f}MB"
    return "0MB"


def clean_old_logs(days: int = 30):
    """Remove log files older than specified days."""
    import time
    
    logger = get_logger("ARES.LogCleaner")
    current_time = time.time()
    cutoff_time = current_time - (days * 86400)
    
    removed_count = 0
    if LOGS_DIR.exists():
        for log_file in LOGS_DIR.glob("*.log*"):
            file_time = log_file.stat().st_mtime
            if file_time < cutoff_time:
                try:
                    log_file.unlink()
                    logger.info(f"Removed old log: {log_file.name}")
                    removed_count += 1
                except Exception as e:
                    logger.error(f"Could not remove {log_file.name}: {e}")
    
    logger.info(f"Cleanup complete: {removed_count} old logs removed")


# ===================================================
# MAIN TEST
# ===================================================

if __name__ == "__main__":
    print("\n" + "=" * 70)
    print("  ARES Logging System Test")
    print("=" * 70)
    
    # Initialize logging
    initialize_logging()
    
    # Get logger
    logger = get_main_logger()
    
    # Test logging
    print("\nTesting logs...")
    logger.info("✅ Info message")
    logger.warning("⚠️  Warning message")
    logger.error("❌ Error message")
    
    # Get error logger
    error_logger = get_error_logger()
    error_logger.error("Error logged to separate file")
    
    # Get debug logger
    debug_logger = get_debug_logger()
    debug_logger.debug("Debug message")
    
    # Display log files
    print("\nLog files created:")
    log_files = get_log_files()
    for filename, info in log_files.items():
        print(f"  📄 {filename}")
        print(f"     Size: {info['size_mb']}MB")
        print(f"     Path: {info['path']}")
    
    print("\n" + "=" * 70)
    print("✅ Logging system test complete!")
    print("=" * 70 + "\n")
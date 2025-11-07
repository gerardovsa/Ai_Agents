"""
Centralized Logging Configuration for V4 Agent System
Provides comprehensive logging with multiple outputs and levels.

Features:
- Console output (INFO level) - Real-time monitoring
- Daily log files (INFO level) - Production logs
- Daily debug files (DEBUG level) - Detailed debugging
- UTF-8 encoding support
- Automatic log rotation by day
- Module/function/line number tracking
"""

import logging
import sys
from pathlib import Path
from datetime import datetime

# ============================================================
# LOG DIRECTORY SETUP
# ============================================================

# Create logs directory at project root
LOGS_DIR = Path(__file__).parent.parent.parent / 'logs'
LOGS_DIR.mkdir(exist_ok=True)

# Log file paths with date-based rotation
TODAY = datetime.now().strftime("%Y%m%d")
LOG_FILE = LOGS_DIR / f'v4_agent_{TODAY}.log'
DEBUG_FILE = LOGS_DIR / f'v4_debug_{TODAY}.log'

# ============================================================
# LOG FORMAT CONFIGURATION
# ============================================================

# Detailed format with emoji indicators for easy scanning
LOG_FORMAT = '[%(asctime)s] %(levelname)-8s [%(name)s.%(funcName)s:%(lineno)d] %(message)s'
DATE_FORMAT = '%Y-%m-%d %H:%M:%S'

# Color codes for console output (optional, works on most terminals)
COLORS = {
    'DEBUG': '\033[36m',     # Cyan
    'INFO': '\033[32m',      # Green
    'WARNING': '\033[33m',   # Yellow
    'ERROR': '\033[31m',     # Red
    'CRITICAL': '\033[35m',  # Magenta
    'RESET': '\033[0m'       # Reset
}

# ============================================================
# LOGGER FACTORY
# ============================================================

def get_logger(name: str) -> logging.Logger:
    """
    Get a configured logger instance with multiple output handlers.
    
    Usage:
        from utils.logger import get_logger
        logger = get_logger(__name__)
        
        logger.debug("Detailed debug info")
        logger.info("Important events")
        logger.warning("Warning messages")
        logger.error("Error messages", exc_info=True)
    
    Args:
        name: Module name (use __name__ for automatic naming)
        
    Returns:
        Configured logger instance
        
    Output Destinations:
        1. Console (stdout) - INFO and above
        2. Daily log file - INFO and above
        3. Daily debug file - DEBUG and above (everything)
    """
    logger = logging.getLogger(name)
    
    # Only configure handlers once per logger
    if not logger.handlers:
        logger.setLevel(logging.DEBUG)
        logger.propagate = False  # Don't pass to parent loggers
        
        # ========================================
        # HANDLER 1: Console Output (INFO level)
        # ========================================
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(logging.INFO)
        console_formatter = logging.Formatter(LOG_FORMAT, DATE_FORMAT)
        console_handler.setFormatter(console_formatter)
        logger.addHandler(console_handler)
        
        # ========================================
        # HANDLER 2: Info Log File (INFO level)
        # ========================================
        try:
            file_handler = logging.FileHandler(LOG_FILE, encoding='utf-8', mode='a')
            file_handler.setLevel(logging.INFO)
            file_formatter = logging.Formatter(LOG_FORMAT, DATE_FORMAT)
            file_handler.setFormatter(file_formatter)
            logger.addHandler(file_handler)
        except Exception as e:
            print(f"⚠️ Warning: Could not create log file {LOG_FILE}: {e}")
        
        # ========================================
        # HANDLER 3: Debug Log File (DEBUG level)
        # ========================================
        try:
            debug_handler = logging.FileHandler(DEBUG_FILE, encoding='utf-8', mode='a')
            debug_handler.setLevel(logging.DEBUG)
            debug_formatter = logging.Formatter(LOG_FORMAT, DATE_FORMAT)
            debug_handler.setFormatter(debug_formatter)
            logger.addHandler(debug_handler)
        except Exception as e:
            print(f"⚠️ Warning: Could not create debug file {DEBUG_FILE}: {e}")
    
    return logger


# ============================================================
# CONVENIENCE FUNCTIONS
# ============================================================

def log_system_startup(logger, component_name: str, version: str = "v4"):
    """Log system startup banner"""
    logger.info("=" * 60)
    logger.info(f"🚀 {component_name} Starting ({version})")
    logger.info(f"📅 Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    logger.info(f"📝 Log file: {LOG_FILE}")
    logger.info(f"🔍 Debug file: {DEBUG_FILE}")
    logger.info("=" * 60)


def log_system_shutdown(logger, component_name: str):
    """Log system shutdown banner"""
    logger.info("=" * 60)
    logger.info(f"🛑 {component_name} Shutting Down")
    logger.info(f"📅 Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    logger.info("=" * 60)


def log_request_start(logger, endpoint: str, method: str, params: dict = None):
    """Log incoming request"""
    logger.info(f"📨 Incoming {method} request: {endpoint}")
    if params:
        logger.debug(f"Request params: {params}")


def log_request_end(logger, endpoint: str, duration: float, success: bool = True):
    """Log request completion"""
    status = "" if success else ""
    logger.info(f"{status} Request completed: {endpoint} ({duration:.2f}s)")


# ============================================================
# EXAMPLE USAGE (for testing)
# ============================================================

if __name__ == "__main__":
    # Create test logger
    test_logger = get_logger("test_module")
    
    # Log system startup
    log_system_startup(test_logger, "Test Component", "v4-test")
    
    # Test different log levels
    test_logger.debug("🔍 This is a DEBUG message (only in debug file)")
    test_logger.info("ℹ️ This is an INFO message (console + files)")
    test_logger.warning("⚠️ This is a WARNING message")
    test_logger.error(" This is an ERROR message")
    
    # Test request logging
    log_request_start(test_logger, "/api/test", "POST", {"param": "value"})
    log_request_end(test_logger, "/api/test", 1.23, success=True)
    
    # Test exception logging
    try:
        raise ValueError("Test exception")
    except Exception as e:
        test_logger.error(f" Exception occurred: {e}", exc_info=True)
    
    # Log shutdown
    log_system_shutdown(test_logger, "Test Component")
    
    print(f"\nTest complete! Check logs:")
    print(f"   INFO: {LOG_FILE}")
    print(f"   DEBUG: {DEBUG_FILE}")


# Export public API
__all__ = [
    'get_logger',
    'log_system_startup',
    'log_system_shutdown',
    'log_request_start',
    'log_request_end',
    'LOGS_DIR',
    'LOG_FILE',
    'DEBUG_FILE'
]

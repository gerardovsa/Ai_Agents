"""
Test script to demonstrate error highlighting in logs
Shows red text for the word "error" and red separator lines around ERROR messages
"""

import sys
from pathlib import Path

# Add AI_infrastructure to path
sys.path.insert(0, str(Path(__file__).parent / 'AI_infrastructure'))

from utils.logger import get_logger
from utils.logger_config import setup_logger

print("=" * 100)
print("TESTING ERROR HIGHLIGHTING IN LOGS")
print("=" * 100)
print()

# Test with logger.py (new system)
print("1. Testing with utils.logger (new system):")
print("-" * 100)
logger1 = get_logger("test.logger_v4")

logger1.info("This is a normal INFO message - no highlighting")
logger1.warning("This is a WARNING message - no highlighting")
logger1.info("This message contains the word error but is INFO level")
logger1.warning("This warning mentions an error that occurred")
logger1.error("This is an ERROR message - should have red separators!")
logger1.error("Another error: Database connection failed")
logger1.critical("CRITICAL: System error detected!")

print()
print()

# Test with logger_config.py (old system)
print("2. Testing with utils.logger_config (old system):")
print("-" * 100)
logger2 = setup_logger("test.logger_config")

from utils.logger_config import log_success, log_warning, log_error

log_success(logger2, "Operation completed successfully")
log_warning(logger2, "This warning mentions an error condition")
log_error(logger2, "Database connection failed")
logger2.error("File not found error at line 42")
logger2.critical("Critical system error - immediate action required!")

print()
print()
print("=" * 100)
print("TEST COMPLETE")
print("=" * 100)
print()
print("WHAT YOU SHOULD SEE:")
print("- The word 'error' in RED text (case-insensitive)")
print("- RED separator lines (100 '=' characters) ABOVE and BELOW ERROR/CRITICAL messages")
print("- Normal colored output for other log levels")
print()
print("NOTE: If running in a terminal that doesn't support ANSI colors,")
print("you may see escape codes instead of colors.")

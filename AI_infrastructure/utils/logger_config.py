"""
Unified Logging Configuration for AI Infrastructure
Provides consistent log formatting across all modules

Log Format:
    INFO:module.name: [CATEGORY] Message
    
Categories:
    - INIT: Initialization/startup
    - CONFIG: Configuration loading
    - ROUTE: Route registration/endpoint activity
    - DB: Database operations
    - AUTH: Authentication/authorization
    - TOOL: Tool loading/execution
    - MODULE: Module loading/plugin system
    - ERROR: Error conditions
    - SUCCESS: Successful operations
    - WARNING: Warning conditions
"""

import logging
import sys
from typing import Optional

# ANSI color codes for terminal output
class Colors:
    RESET = '\033[0m'
    BOLD = '\033[1m'
    
    # Status colors
    SUCCESS = '\033[92m'  # Green
    INFO = '\033[94m'     # Blue
    WARNING = '\033[93m'  # Yellow
    ERROR = '\033[91m'    # Red
    DEBUG = '\033[95m'    # Magenta
    
    # Category colors
    INIT = '\033[96m'     # Cyan
    CONFIG = '\033[94m'   # Blue
    ROUTE = '\033[95m'    # Magenta
    DB = '\033[93m'       # Yellow
    AUTH = '\033[92m'     # Green
    TOOL = '\033[94m'     # Blue
    MODULE = '\033[96m'   # Cyan


class ColoredFormatter(logging.Formatter):
    """Custom formatter that adds color to log levels and categories"""
    
    LEVEL_COLORS = {
        logging.DEBUG: Colors.DEBUG,
        logging.INFO: Colors.INFO,
        logging.WARNING: Colors.WARNING,
        logging.ERROR: Colors.ERROR,
        logging.CRITICAL: Colors.ERROR + Colors.BOLD,
    }
    
    CATEGORY_COLORS = {
        'INIT': Colors.INIT,
        'CONFIG': Colors.CONFIG,
        'ROUTE': Colors.ROUTE,
        'DB': Colors.DB,
        'AUTH': Colors.AUTH,
        'TOOL': Colors.TOOL,
        'MODULE': Colors.MODULE,
        'SUCCESS': Colors.SUCCESS,
        'ERROR': Colors.ERROR,
        'WARNING': Colors.WARNING,
        'OK': Colors.SUCCESS,
        'PLUGIN': Colors.MODULE,
        'DISCOVER': Colors.INFO,
        'LOAD': Colors.TOOL,
    }
    
    def format(self, record):
        # Add color to level name
        level_color = self.LEVEL_COLORS.get(record.levelno, '')
        record.levelname = f"{level_color}{record.levelname}{Colors.RESET}"
        
        # Format the message
        message = super().format(record)
        
        # Add color to category markers [CATEGORY] - match case-insensitive
        import re
        for category, color in self.CATEGORY_COLORS.items():
            # Match [CATEGORY] at start of message or after ": "
            pattern = r'(\[' + category + r'\])'
            colored_marker = f'{color}\\1{Colors.RESET}'
            message = re.sub(pattern, colored_marker, message, flags=re.IGNORECASE)
        
        # Highlight the word "error" in red anywhere in the message (case-insensitive)
        error_pattern = r'\b(error|ERROR|Error)\b'
        message = re.sub(error_pattern, f'{Colors.ERROR}\\1{Colors.RESET}', message)
        
        # Add red separator lines for ERROR and CRITICAL level messages
        if record.levelno >= logging.ERROR:
            separator = f"{Colors.ERROR}{'=' * 100}{Colors.RESET}"
            message = f"\n{separator}\n{message}\n{separator}"
        
        return message


def setup_logger(
    name: str,
    level: int = logging.INFO,
    use_colors: bool = True
) -> logging.Logger:
    """
    Setup a logger with standardized formatting
    
    Args:
        name: Logger name (usually __name__)
        level: Logging level (default: INFO)
        use_colors: Whether to use colored output (default: True)
    
    Returns:
        Configured logger instance
    """
    logger = logging.getLogger(name)
    
    # Avoid duplicate handlers - clear existing handlers first
    if logger.handlers:
        logger.handlers.clear()
    
    # Prevent propagation to avoid duplicate logs from parent loggers
    logger.propagate = False
    
    logger.setLevel(level)
    
    # Create console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(level)
    
    # Set formatter
    if use_colors and sys.stdout.isatty():
        formatter = ColoredFormatter(
            '%(levelname)s:%(name)s: %(message)s'
        )
    else:
        formatter = logging.Formatter(
            '%(levelname)s:%(name)s: %(message)s'
        )
    
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)
    
    return logger


def log_init(logger: logging.Logger, message: str):
    """Log initialization message"""
    logger.info(f"[INIT] {message}")


def log_config(logger: logging.Logger, message: str):
    """Log configuration message"""
    logger.info(f"[CONFIG] {message}")


def log_route(logger: logging.Logger, message: str):
    """Log route registration message"""
    logger.info(f"[ROUTE] {message}")


def log_db(logger: logging.Logger, message: str):
    """Log database operation message"""
    logger.info(f"[DB] {message}")


def log_auth(logger: logging.Logger, message: str):
    """Log authentication message"""
    logger.info(f"[AUTH] {message}")


def log_tool(logger: logging.Logger, message: str):
    """Log tool operation message"""
    logger.info(f"[TOOL] {message}")


def log_module(logger: logging.Logger, message: str):
    """Log module loading message"""
    logger.info(f"[MODULE] {message}")


def log_success(logger: logging.Logger, message: str):
    """Log success message"""
    logger.info(f"[SUCCESS] {message}")


def log_error(logger: logging.Logger, message: str):
    """Log error message"""
    logger.error(f"[ERROR] {message}")


def log_warning(logger: logging.Logger, message: str):
    """Log warning message"""
    logger.warning(f"[WARNING] {message}")


def log_tool_success(tool_name: str, tokens: int):
    """Log successful tool execution with formatting"""
    tool_upper = tool_name.upper()
    print(f"{Colors.INFO}{tool_upper}{Colors.RESET} - {Colors.SUCCESS}SUCCESSFUL{Colors.RESET} ({tokens:,} tokens)")


def log_tool_failure(tool_name: str, error: str, tokens: int = 0):
    """Log failed tool execution with formatting"""
    tool_upper = tool_name.upper()
    token_info = f" ({tokens:,} tokens)" if tokens > 0 else ""
    print(f"{Colors.INFO}{tool_upper}{Colors.RESET} - {Colors.ERROR}FAILED{Colors.RESET}{token_info}: {error}")


# Default application logger
app_logger = setup_logger('AI_infrastructure')

"""
Config Package
Centralized configuration for V4 Agent System
"""

# Import all constants for easy access
from .constants import (
    MAX_TURNS,
    MAX_TOKENS,
    TEMPERATURE,
    THINKING_BUDGET,
    CLAUDE_MODEL,
    ANTHROPIC_BETA_HEADERS,
    SESSION_TIMEOUT,
    MAX_CONVERSATION_LENGTH,
    QUEUE_TIMEOUT,
    MAX_QUEUE_TIMEOUTS,
    MAX_FILE_SIZE,
    ALLOWED_FILE_TYPES,
    FILE_TYPE_MAPPING,
    TOOL_TIMEOUT,
    MAX_TOOL_RETRIES,
    TOOL_RETRY_DELAY,
    DB_PATH,
    SESSIONS_DB_PATH,
    DB_POOL_SIZE,
    UPLOAD_STORAGE_PATH,
    MAX_USER_STORAGE,
    FILE_RETENTION_DAYS,
    DB_TIMEOUT,
    SUPPORTED_PLATFORMS,
    PLATFORM_NAMES,
    RATE_LIMIT_PER_USER
)

# Note: Don't import logging_config here to avoid circular imports
# Import it directly where needed: from config.logging_config import root_logger

__all__ = [
    'MAX_TURNS',
    'MAX_TOKENS',
    'TEMPERATURE',
    'THINKING_BUDGET',
    'CLAUDE_MODEL',
    'ANTHROPIC_BETA_HEADERS',
    'SESSION_TIMEOUT',
    'MAX_CONVERSATION_LENGTH',
    'QUEUE_TIMEOUT',
    'MAX_QUEUE_TIMEOUTS',
    'MAX_FILE_SIZE',
    'ALLOWED_FILE_TYPES',
    'FILE_TYPE_MAPPING',
    'TOOL_TIMEOUT',
    'MAX_TOOL_RETRIES',
    'TOOL_RETRY_DELAY',
    'DB_PATH',
    'SESSIONS_DB_PATH',
    'DB_POOL_SIZE',
    'UPLOAD_STORAGE_PATH',
    'MAX_USER_STORAGE',
    'FILE_RETENTION_DAYS',
    'DB_TIMEOUT',
    'SUPPORTED_PLATFORMS',
    'PLATFORM_NAMES',
    'RATE_LIMIT_PER_USER'
]

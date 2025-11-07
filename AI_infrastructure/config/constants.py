"""
Configuration Constants for V4 Agent System
Centralized configuration values used across all modules.
"""

# ============================================================
# CONVERSATION SETTINGS
# ============================================================

# Maximum turns in multi-turn conversations
# Prevents infinite loops while allowing complex workflows
MAX_TURNS = 20

# Maximum tokens for Claude responses
MAX_TOKENS = 16000

# Temperature for Claude API (0.0-1.0)
# 0.0 = deterministic, 1.0 = creative
TEMPERATURE = 1.0

# Thinking budget tokens (for interleaved thinking)
THINKING_BUDGET = 10000

# ============================================================
# ANTHROPIC API SETTINGS
# ============================================================

# Model selection
CLAUDE_MODEL = "claude-sonnet-4-5-20250929"

# Beta headers for advanced features
# Format: List of beta feature names (Anthropic SDK expects list, not dict)
# See: https://docs.anthropic.com/en/docs/build-with-claude/extended-thinking#interleaved-thinking
ANTHROPIC_BETA_HEADERS = ["interleaved-thinking-2025-05-14"]

# ============================================================
# SESSION MANAGEMENT
# ============================================================

# Session timeout (seconds)
SESSION_TIMEOUT = 3600  # 1 hour

# Maximum conversation history length (messages)
MAX_CONVERSATION_LENGTH = 100

# Queue timeout for SSE streaming (seconds)
QUEUE_TIMEOUT = 30

# Maximum queue timeouts before giving up
MAX_QUEUE_TIMEOUTS = 3

# ============================================================
# FILE UPLOAD SETTINGS
# ============================================================

# Maximum file size (bytes)
MAX_FILE_SIZE = 32 * 1024 * 1024  # 32 MB

# Allowed file types
ALLOWED_FILE_TYPES = {
    'application/pdf',
    'image/jpeg',
    'image/png',
    'image/gif',
    'image/webp'
}

# File type to block type mapping
FILE_TYPE_MAPPING = {
    'application/pdf': 'document',
    'image/jpeg': 'image',
    'image/png': 'image',
    'image/gif': 'image',
    'image/webp': 'image'
}

# ============================================================
# TOOL EXECUTION SETTINGS
# ============================================================

# Tool execution timeout (seconds)
TOOL_TIMEOUT = 120

# Maximum retry attempts for failed tools
MAX_TOOL_RETRIES = 3

# Retry delay (seconds)
TOOL_RETRY_DELAY = 2

# ============================================================
# DATABASE SETTINGS
# ============================================================

# Database paths (relative to project root AI_agents/)
DB_PATH = 'data/ai_infrastructure.db'
SESSIONS_DB_PATH = 'data/sessions.db'

# Connection pool size
DB_POOL_SIZE = 5

# Query timeout (seconds)
DB_TIMEOUT = 30

# ============================================================
# PLATFORM SETTINGS
# ============================================================

# Supported platforms for OAuth
SUPPORTED_PLATFORMS = [
    'google',
    'microsoft',
    'woocommerce'
]

# Platform display names
PLATFORM_NAMES = {
    'google': 'Google Workspace',
    'microsoft': 'Microsoft 365',
    'woocommerce': 'WooCommerce'
}

# ============================================================
# API RATE LIMITS
# ============================================================

# Rate limit per user (requests per minute)
RATE_LIMIT_PER_USER = 60

# Rate limit per IP (requests per minute)
RATE_LIMIT_PER_IP = 100

# ============================================================
# LOGGING SETTINGS
# ============================================================

# Log file rotation
LOG_ROTATION_DAYS = 7  # Keep logs for 7 days

# Log levels by environment
LOG_LEVELS = {
    'development': 'DEBUG',
    'staging': 'INFO',
    'production': 'INFO'
}

# ============================================================
# ENVIRONMENT DETECTION
# ============================================================

import os

# Detect environment
ENVIRONMENT = os.getenv('FLASK_ENV', 'development')

# Debug mode
DEBUG = ENVIRONMENT == 'development'

# ============================================================
# EXPORT ALL CONSTANTS
# ============================================================

__all__ = [
    # Conversation
    'MAX_TURNS',
    'MAX_TOKENS',
    'TEMPERATURE',
    'THINKING_BUDGET',
    
    # API
    'CLAUDE_MODEL',
    'ANTHROPIC_BETA_HEADERS',
    
    # Sessions
    'SESSION_TIMEOUT',
    'MAX_CONVERSATION_LENGTH',
    'QUEUE_TIMEOUT',
    'MAX_QUEUE_TIMEOUTS',
    
    # Files
    'MAX_FILE_SIZE',
    'ALLOWED_FILE_TYPES',
    'FILE_TYPE_MAPPING',
    
    # Tools
    'TOOL_TIMEOUT',
    'MAX_TOOL_RETRIES',
    'TOOL_RETRY_DELAY',
    
    # Database
    'DB_PATH',
    'SESSIONS_DB_PATH',
    'DB_POOL_SIZE',
    'DB_TIMEOUT',
    
    # Platforms
    'SUPPORTED_PLATFORMS',
    'PLATFORM_NAMES',
    
    # Rate Limits
    'RATE_LIMIT_PER_USER',
    'RATE_LIMIT_PER_IP',
    
    # Logging
    'LOG_ROTATION_DAYS',
    'LOG_LEVELS',
    
    # Environment
    'ENVIRONMENT',
    'DEBUG'
]

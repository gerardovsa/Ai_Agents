"""
Threads Module Constants

Defines enums, constants, and configuration values for thread management.
"""

from enum import Enum


class ThreadStatus(str, Enum):
    """Thread lifecycle status"""
    ACTIVE = "active"
    ARCHIVED = "archived"
    DELETED = "deleted"
    DRAFT = "draft"


class ThreadVisibility(str, Enum):
    """Thread visibility/sharing settings"""
    PRIVATE = "private"          # Only owner can access
    WORKSPACE = "workspace"      # All workspace members can access
    SHARED = "shared"            # Specific users granted access
    PUBLIC = "public"            # Anyone with link can access (future)


class MessageRole(str, Enum):
    """Message role types (Anthropic standard)"""
    USER = "user"
    ASSISTANT = "assistant"
    SYSTEM = "system"


class MessageContentType(str, Enum):
    """Message content block types"""
    TEXT = "text"
    IMAGE = "image"
    DOCUMENT = "document"
    TOOL_USE = "tool_use"
    TOOL_RESULT = "tool_result"
    THINKING = "thinking"


class SharePermission(str, Enum):
    """Thread sharing permission levels"""
    VIEW = "view"                # Can read thread and messages
    COMMENT = "comment"          # Can add messages
    EDIT = "edit"                # Can modify thread settings
    ADMIN = "admin"              # Can share and delete


# Thread Configuration
DEFAULT_THREAD_NAME = "New Conversation"
MAX_THREAD_NAME_LENGTH = 200
MAX_THREAD_DESCRIPTION_LENGTH = 1000
MAX_MESSAGES_PER_THREAD = 10000  # Soft limit for performance

# Message Configuration
MAX_MESSAGE_CONTENT_LENGTH = 100000  # 100KB per message
MAX_ATTACHMENTS_PER_MESSAGE = 10

# Thread Slug Generation
THREAD_SLUG_LENGTH = 16  # Length of random thread slug
THREAD_SLUG_CHARSET = "0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ"

# Pagination
DEFAULT_PAGE_SIZE = 50
MAX_PAGE_SIZE = 200

# Archiving
AUTO_ARCHIVE_DAYS = 90  # Auto-archive threads after 90 days inactive
RETENTION_DAYS = 365    # Keep deleted threads for 365 days before purge

# Rate Limits (per user per minute)
RATE_LIMIT_CREATE_THREAD = 10
RATE_LIMIT_SEND_MESSAGE = 60
RATE_LIMIT_SHARE_THREAD = 20

# Database Table Names
TABLE_THREADS = "threads"
TABLE_MESSAGES = "messages"
TABLE_THREAD_USERS = "thread_users"
TABLE_THREAD_SHARES = "thread_shares"

# Error Messages
ERROR_THREAD_NOT_FOUND = "Thread not found"
ERROR_MESSAGE_NOT_FOUND = "Message not found"
ERROR_PERMISSION_DENIED = "Permission denied"
ERROR_THREAD_ARCHIVED = "Cannot modify archived thread"
ERROR_THREAD_DELETED = "Thread has been deleted"
ERROR_INVALID_SLUG = "Invalid thread slug"
ERROR_DUPLICATE_SHARE = "User already has access to this thread"
ERROR_CANNOT_SHARE_WITH_SELF = "Cannot share thread with yourself"
ERROR_MAX_MESSAGES_REACHED = "Maximum messages per thread reached"

# Success Messages
SUCCESS_THREAD_CREATED = "Thread created successfully"
SUCCESS_THREAD_UPDATED = "Thread updated successfully"
SUCCESS_THREAD_DELETED = "Thread deleted successfully"
SUCCESS_THREAD_ARCHIVED = "Thread archived successfully"
SUCCESS_THREAD_RESTORED = "Thread restored successfully"
SUCCESS_MESSAGE_SENT = "Message sent successfully"
SUCCESS_THREAD_SHARED = "Thread shared successfully"
SUCCESS_SHARE_REMOVED = "Share removed successfully"

# Event Types (for logging/audit)
EVENT_THREAD_CREATED = "thread.created"
EVENT_THREAD_UPDATED = "thread.updated"
EVENT_THREAD_DELETED = "thread.deleted"
EVENT_THREAD_ARCHIVED = "thread.archived"
EVENT_THREAD_RESTORED = "thread.restored"
EVENT_MESSAGE_SENT = "message.sent"
EVENT_MESSAGE_DELETED = "message.deleted"
EVENT_THREAD_SHARED = "thread.shared"
EVENT_SHARE_REMOVED = "thread.share_removed"
EVENT_PERMISSION_CHANGED = "thread.permission_changed"

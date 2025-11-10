"""
Threads Module - Thread and Message Management

This module handles all thread-related operations including:
- Thread lifecycle (create, update, delete, archive)
- Message management (add, retrieve, search)
- Thread sharing and permissions
- Thread metadata and settings

Exports:
    ThreadManager: Main thread operations manager
    MessageManager: Message-specific operations
    ThreadPermissions: Permission checks and validation
    
Usage:
    from threads import ThreadManager, MessageManager
    
    thread_mgr = ThreadManager()
    msg_mgr = MessageManager()
"""

from .constants import (
    ThreadStatus,
    ThreadVisibility,
    DEFAULT_THREAD_NAME,
    MAX_THREAD_NAME_LENGTH,
    MAX_MESSAGES_PER_THREAD
)

from .models import (
    Thread,
    ThreadCreate,
    ThreadUpdate,
    Message,
    MessageCreate,
    ThreadShare,
    ThreadSettings
)

# Import managers
from .thread_manager import ThreadManager
from .message_manager import MessageManager

__all__ = [
    # Constants
    'ThreadStatus',
    'ThreadVisibility',
    'DEFAULT_THREAD_NAME',
    'MAX_THREAD_NAME_LENGTH',
    'MAX_MESSAGES_PER_THREAD',
    
    # Models
    'Thread',
    'ThreadCreate',
    'ThreadUpdate',
    'Message',
    'MessageCreate',
    'ThreadShare',
    'ThreadSettings',
    
    # Managers
    'ThreadManager',
    'MessageManager',
]

__version__ = '1.0.0'

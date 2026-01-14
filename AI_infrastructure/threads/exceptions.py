"""
Threads Module Exceptions

Custom exception classes for thread and message operations.
"""

from typing import Optional


class ThreadError(Exception):
    """Base exception for thread-related errors"""
    def __init__(self, message: str, status_code: int = 500, details: Optional[dict] = None):
        self.message = message
        self.status_code = status_code
        self.details = details or {}
        super().__init__(self.message)


class ThreadNotFoundError(ThreadError):
    """Thread does not exist"""
    def __init__(self, thread_id: Optional[int] = None, thread_slug: Optional[str] = None):
        message = "Thread not found"
        if thread_id:
            message = f"Thread with ID {thread_id} not found"
        elif thread_slug:
            message = f"Thread with slug '{thread_slug}' not found"
        super().__init__(message, status_code=404, details={"thread_id": thread_id, "thread_slug": thread_slug})


class MessageNotFoundError(ThreadError):
    """Message does not exist"""
    def __init__(self, message_id: int):
        super().__init__(f"Message with ID {message_id} not found", status_code=404, details={"message_id": message_id})


class ThreadPermissionError(ThreadError):
    """User lacks permission for this operation"""
    def __init__(self, user_id: int, thread_id: int, required_permission: str):
        super().__init__(
            f"User {user_id} lacks '{required_permission}' permission for thread {thread_id}",
            status_code=403,
            details={"user_id": user_id, "thread_id": thread_id, "required_permission": required_permission}
        )


class ThreadArchivedError(ThreadError):
    """Cannot perform operation on archived thread"""
    def __init__(self, thread_id: int):
        super().__init__(f"Thread {thread_id} is archived", status_code=400, details={"thread_id": thread_id})


class ThreadDeletedError(ThreadError):
    """Cannot perform operation on deleted thread"""
    def __init__(self, thread_id: int):
        super().__init__(f"Thread {thread_id} has been deleted", status_code=410, details={"thread_id": thread_id})


class InvalidThreadSlugError(ThreadError):
    """Thread slug is invalid"""
    def __init__(self, slug: str):
        super().__init__(f"Invalid thread slug: '{slug}'", status_code=400, details={"slug": slug})


class DuplicateThreadError(ThreadError):
    """Thread with this identifier already exists"""
    def __init__(self, slug: str):
        super().__init__(f"Thread with slug '{slug}' already exists", status_code=409, details={"slug": slug})


class MaxMessagesReachedError(ThreadError):
    """Thread has reached maximum message limit"""
    def __init__(self, thread_id: int, max_messages: int):
        super().__init__(
            f"Thread {thread_id} has reached maximum of {max_messages} messages",
            status_code=400,
            details={"thread_id": thread_id, "max_messages": max_messages}
        )


class InvalidMessageContentError(ThreadError):
    """Message content is invalid"""
    def __init__(self, reason: str):
        super().__init__(f"Invalid message content: {reason}", status_code=400, details={"reason": reason})


class WorkspaceNotFoundError(ThreadError):
    """Workspace does not exist"""
    def __init__(self, workspace_id: int):
        super().__init__(f"Workspace with ID {workspace_id} not found", status_code=404, details={"workspace_id": workspace_id})


class UserNotFoundError(ThreadError):
    """User does not exist"""
    def __init__(self, user_id: int):
        super().__init__(f"User with ID {user_id} not found", status_code=404, details={"user_id": user_id})


class DuplicateShareError(ThreadError):
    """User already has access to this thread"""
    def __init__(self, user_id: int, thread_id: int):
        super().__init__(
            f"User {user_id} already has access to thread {thread_id}",
            status_code=409,
            details={"user_id": user_id, "thread_id": thread_id}
        )


class CannotShareWithSelfError(ThreadError):
    """Cannot share thread with yourself"""
    def __init__(self, user_id: int):
        super().__init__(f"User {user_id} cannot share thread with themselves", status_code=400, details={"user_id": user_id})


class ShareNotFoundError(ThreadError):
    """Thread share record not found"""
    def __init__(self, share_id: int):
        super().__init__(f"Share with ID {share_id} not found", status_code=404, details={"share_id": share_id})


class DatabaseError(ThreadError):
    """Database operation failed"""
    def __init__(self, operation: str, error: str):
        super().__init__(
            f"Database operation '{operation}' failed: {error}",
            status_code=500,
            details={"operation": operation, "error": error}
        )


class ValidationError(ThreadError):
    """Data validation failed"""
    def __init__(self, field: str, reason: str):
        super().__init__(
            f"Validation error for field '{field}': {reason}",
            status_code=400,
            details={"field": field, "reason": reason}
        )


class RateLimitError(ThreadError):
    """Rate limit exceeded"""
    def __init__(self, operation: str, limit: int, retry_after: int):
        super().__init__(
            f"Rate limit exceeded for '{operation}' (limit: {limit} per minute)",
            status_code=429,
            details={"operation": operation, "limit": limit, "retry_after": retry_after}
        )

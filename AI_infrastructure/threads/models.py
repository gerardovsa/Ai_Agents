"""
Threads Module Models

Pydantic models for thread and message data validation and serialization.
"""

from typing import Optional, List, Dict, Any
from datetime import datetime
from pydantic import BaseModel, Field, validator
from .constants import (
    ThreadStatus,
    ThreadVisibility,
    MessageRole,
    SharePermission,
    MAX_THREAD_NAME_LENGTH,
    MAX_THREAD_DESCRIPTION_LENGTH,
    MAX_MESSAGE_CONTENT_LENGTH,
    DEFAULT_THREAD_NAME
)


# ============================================================
# Thread Models
# ============================================================

class ThreadBase(BaseModel):
    """Base thread model with common fields"""
    name: str = Field(default=DEFAULT_THREAD_NAME, max_length=MAX_THREAD_NAME_LENGTH)
    description: Optional[str] = Field(default=None, max_length=MAX_THREAD_DESCRIPTION_LENGTH)
    status: ThreadStatus = Field(default=ThreadStatus.ACTIVE)
    visibility: ThreadVisibility = Field(default=ThreadVisibility.PRIVATE)
    
    @validator('name')
    def validate_name(cls, v):
        if v:
            v = v.strip()
            if not v:
                return DEFAULT_THREAD_NAME
        return v


class ThreadCreate(ThreadBase):
    """Model for creating a new thread"""
    workspace_id: int = Field(..., description="Workspace ID this thread belongs to")
    user_id: int = Field(..., description="Owner user ID")
    agent_id: Optional[str] = Field(default="1", description="Agent ID (1, 2, 3, etc.)")
    
    class Config:
        schema_extra = {
            "example": {
                "name": "Customer Support Chat",
                "description": "Discussion about product features",
                "workspace_id": 1,
                "user_id": 1,
                "agent_id": "1",
                "status": "active",
                "visibility": "private"
            }
        }


class ThreadUpdate(BaseModel):
    """Model for updating an existing thread"""
    name: Optional[str] = Field(None, max_length=MAX_THREAD_NAME_LENGTH)
    description: Optional[str] = Field(None, max_length=MAX_THREAD_DESCRIPTION_LENGTH)
    status: Optional[ThreadStatus] = None
    visibility: Optional[ThreadVisibility] = None
    metadata: Optional[Dict[str, Any]] = None
    
    class Config:
        schema_extra = {
            "example": {
                "name": "Updated Thread Name",
                "status": "archived",
                "visibility": "workspace"
            }
        }


class Thread(ThreadBase):
    """Complete thread model (from database)"""
    id: int
    thread_slug: str
    workspace_id: int
    user_id: int
    agent_id: Optional[str] = "1"
    message_count: int = 0
    last_message_at: Optional[datetime] = None
    metadata: Optional[Dict[str, Any]] = None
    created_at: datetime
    updated_at: datetime
    archived_at: Optional[datetime] = None
    deleted_at: Optional[datetime] = None
    
    class Config:
        orm_mode = True
        schema_extra = {
            "example": {
                "id": 1,
                "thread_slug": "abc123def456",
                "name": "Customer Support Chat",
                "description": "Discussion about product features",
                "workspace_id": 1,
                "user_id": 1,
                "agent_id": "1",
                "status": "active",
                "visibility": "private",
                "message_count": 15,
                "last_message_at": "2025-11-09T20:30:00",
                "created_at": "2025-11-09T10:00:00",
                "updated_at": "2025-11-09T20:30:00"
            }
        }


class ThreadWithMessages(Thread):
    """Thread model including messages"""
    messages: List['Message'] = []


class ThreadSettings(BaseModel):
    """Thread-specific settings"""
    auto_archive: bool = False
    archive_after_days: int = 90
    allow_workspace_access: bool = False
    allow_external_sharing: bool = False
    notification_enabled: bool = True
    metadata: Optional[Dict[str, Any]] = None


# ============================================================
# Message Models
# ============================================================

class MessageBase(BaseModel):
    """Base message model"""
    role: MessageRole
    content: str = Field(..., max_length=MAX_MESSAGE_CONTENT_LENGTH)
    
    @validator('content')
    def validate_content(cls, v):
        if not v or not v.strip():
            raise ValueError("Message content cannot be empty")
        return v


class MessageCreate(MessageBase):
    """Model for creating a new message"""
    thread_id: int = Field(..., description="Thread ID this message belongs to")
    user_id: int = Field(..., description="User ID who sent the message")
    workspace_id: int = Field(..., description="Workspace ID for access control")
    prompt: Optional[str] = None
    include: Optional[str] = None
    tool_calls: Optional[str] = None
    tokens_used: Optional[int] = None
    response_time_ms: Optional[int] = None
    metadata: Optional[Dict[str, Any]] = None
    
    class Config:
        schema_extra = {
            "example": {
                "thread_id": 1,
                "user_id": 1,
                "workspace_id": 1,
                "role": "user",
                "content": "Hello! How can I calculate a quote?"
            }
        }


class MessageUpdate(BaseModel):
    """Model for updating a message (limited fields)"""
    content: Optional[str] = Field(None, max_length=MAX_MESSAGE_CONTENT_LENGTH)
    metadata: Optional[Dict[str, Any]] = None


class Message(MessageBase):
    """Complete message model (from database)"""
    id: int
    thread_id: int
    workspace_id: int
    user_id: int
    prompt: Optional[str] = None
    include: Optional[str] = None
    tool_calls: Optional[str] = None
    tokens_used: Optional[int] = None
    response_time_ms: Optional[int] = None
    metadata: Optional[Dict[str, Any]] = None
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        orm_mode = True
        schema_extra = {
            "example": {
                "id": 1,
                "thread_id": 1,
                "workspace_id": 1,
                "user_id": 1,
                "role": "user",
                "content": "Hello! How can I calculate a quote?",
                "tokens_used": 15,
                "created_at": "2025-11-09T20:30:00"
            }
        }


# ============================================================
# Thread Sharing Models
# ============================================================

class ThreadShareCreate(BaseModel):
    """Model for sharing a thread with a user"""
    thread_id: int = Field(..., description="Thread ID to share")
    user_id: int = Field(..., description="User ID to share with")
    permission: SharePermission = Field(default=SharePermission.VIEW)
    shared_by: int = Field(..., description="User ID who is sharing")
    message: Optional[str] = Field(None, max_length=500, description="Optional message to recipient")
    
    class Config:
        schema_extra = {
            "example": {
                "thread_id": 1,
                "user_id": 2,
                "permission": "view",
                "shared_by": 1,
                "message": "Check out this conversation"
            }
        }


class ThreadShare(BaseModel):
    """Complete thread share record"""
    id: int
    thread_id: int
    user_id: int
    permission: SharePermission
    shared_by: int
    message: Optional[str] = None
    accepted: bool = False
    accepted_at: Optional[datetime] = None
    created_at: datetime
    revoked_at: Optional[datetime] = None
    
    class Config:
        orm_mode = True


class ThreadShareUpdate(BaseModel):
    """Model for updating share permissions"""
    permission: Optional[SharePermission] = None
    accepted: Optional[bool] = None


# ============================================================
# Pagination and List Models
# ============================================================

class ThreadListParams(BaseModel):
    """Query parameters for listing threads"""
    workspace_id: Optional[int] = None
    user_id: Optional[int] = None
    status: Optional[ThreadStatus] = None
    visibility: Optional[ThreadVisibility] = None
    search: Optional[str] = None
    page: int = Field(default=1, ge=1)
    page_size: int = Field(default=50, ge=1, le=200)
    sort_by: str = Field(default="updated_at")
    sort_order: str = Field(default="desc")


class ThreadListResponse(BaseModel):
    """Response model for thread list"""
    threads: List[Thread]
    total: int
    page: int
    page_size: int
    has_more: bool


class MessageListParams(BaseModel):
    """Query parameters for listing messages"""
    thread_id: int
    page: int = Field(default=1, ge=1)
    page_size: int = Field(default=50, ge=1, le=200)
    role: Optional[MessageRole] = None


class MessageListResponse(BaseModel):
    """Response model for message list"""
    messages: List[Message]
    total: int
    page: int
    page_size: int
    has_more: bool


# Update forward references
ThreadWithMessages.update_forward_refs()

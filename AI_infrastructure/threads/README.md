# Threads Module

**Purpose:** Comprehensive thread and message management for the AI agent system.

## Overview

The threads module handles all aspects of conversation thread management including:
- Thread lifecycle (create, read, update, delete, archive)
- Message storage and retrieval
- Thread sharing and permissions
- Multi-user access control
- Integration with workspace system

## Module Structure

```
threads/
├── __init__.py           # Module exports and initialization
├── constants.py          # Enums, constants, and configuration (140 lines)
├── models.py             # Pydantic models for validation (330 lines)
├── exceptions.py         # Custom exception classes (150 lines)
├── thread_manager.py     # Thread CRUD operations (TODO: #3)
├── message_manager.py    # Message operations (TODO: #4)
├── permissions.py        # Access control logic (TODO: planned)
└── README.md             # This file
```

## Key Components

### Constants (`constants.py`)

**Enums:**
- `ThreadStatus`: ACTIVE, ARCHIVED, DELETED, DRAFT
- `ThreadVisibility`: PRIVATE, WORKSPACE, SHARED, PUBLIC
- `MessageRole`: USER, ASSISTANT, SYSTEM
- `SharePermission`: VIEW, COMMENT, EDIT, ADMIN

**Configuration:**
- Thread limits and defaults
- Message size constraints
- Pagination settings
- Rate limits
- Error/success messages

### Models (`models.py`)

**Thread Models:**
- `Thread`: Complete thread record
- `ThreadCreate`: New thread creation
- `ThreadUpdate`: Thread modification
- `ThreadWithMessages`: Thread + messages
- `ThreadSettings`: Thread-specific settings

**Message Models:**
- `Message`: Complete message record
- `MessageCreate`: New message creation
- `MessageUpdate`: Message modification

**Sharing Models:**
- `ThreadShare`: Share record
- `ThreadShareCreate`: New share
- `ThreadShareUpdate`: Permission changes

**List/Pagination:**
- `ThreadListParams`: Query parameters
- `ThreadListResponse`: Paginated results
- `MessageListParams`: Message queries
- `MessageListResponse`: Message pagination

### Exceptions (`exceptions.py`)

**Base:**
- `ThreadError`: Base exception class

**Specific Errors:**
- `ThreadNotFoundError`: Thread doesn't exist
- `MessageNotFoundError`: Message doesn't exist
- `ThreadPermissionError`: Access denied
- `ThreadArchivedError`: Thread is archived
- `ThreadDeletedError`: Thread is deleted
- `InvalidThreadSlugError`: Bad slug format
- `DuplicateThreadError`: Slug collision
- `MaxMessagesReachedError`: Thread full
- `DuplicateShareError`: Already shared
- `DatabaseError`: Database operation failed
- `ValidationError`: Data validation failed
- `RateLimitError`: Rate limit exceeded

## Usage Examples

### Creating a Thread

```python
from threads import ThreadCreate
from threads.thread_manager import ThreadManager

# Create thread data
thread_data = ThreadCreate(
    name="Customer Support Chat",
    description="Help with product features",
    workspace_id=1,
    user_id=1,
    agent_id="1",
    visibility=ThreadVisibility.PRIVATE
)

# Create thread
thread_mgr = ThreadManager()
thread = thread_mgr.create_thread(thread_data)
print(f"Created thread: {thread.thread_slug}")
```

### Adding Messages

```python
from threads import MessageCreate
from threads.message_manager import MessageManager

# Create message
msg_data = MessageCreate(
    thread_id=1,
    user_id=1,
    workspace_id=1,
    role=MessageRole.USER,
    content="Hello! How can I get a quote?"
)

# Save message
msg_mgr = MessageManager()
message = msg_mgr.add_message(msg_data)
```

### Sharing a Thread

```python
from threads import ThreadShareCreate, SharePermission

share_data = ThreadShareCreate(
    thread_id=1,
    user_id=2,
    permission=SharePermission.VIEW,
    shared_by=1,
    message="Check out this conversation"
)

thread_mgr.share_thread(share_data)
```

### Listing Threads

```python
from threads import ThreadListParams, ThreadStatus

params = ThreadListParams(
    workspace_id=1,
    status=ThreadStatus.ACTIVE,
    page=1,
    page_size=50,
    sort_by="updated_at",
    sort_order="desc"
)

result = thread_mgr.list_threads(params)
print(f"Found {result.total} threads")
for thread in result.threads:
    print(f"  - {thread.name} ({thread.message_count} messages)")
```

## Error Handling

```python
from threads.exceptions import (
    ThreadNotFoundError,
    ThreadPermissionError,
    ThreadArchivedError
)

try:
    thread = thread_mgr.get_thread(thread_slug="abc123")
except ThreadNotFoundError as e:
    print(f"Error: {e.message}")
    print(f"Status: {e.status_code}")
    print(f"Details: {e.details}")
except ThreadPermissionError as e:
    print(f"Access denied: {e.message}")
except ThreadArchivedError as e:
    print(f"Thread is archived: {e.message}")
```

## Database Integration

The threads module works with these tables:
- `threads` - Thread metadata
- `messages` - Message content
- `thread_users` - User access (Option B)
- `thread_shares` - Sharing records

See `THREAD_DATABASE_REFERENCE.md` for complete schema.

## Configuration

Key settings from `constants.py`:

```python
# Thread limits
MAX_THREAD_NAME_LENGTH = 200
MAX_MESSAGES_PER_THREAD = 10000

# Message limits
MAX_MESSAGE_CONTENT_LENGTH = 100000
MAX_ATTACHMENTS_PER_MESSAGE = 10

# Pagination
DEFAULT_PAGE_SIZE = 50
MAX_PAGE_SIZE = 200

# Rate limits (per user per minute)
RATE_LIMIT_CREATE_THREAD = 10
RATE_LIMIT_SEND_MESSAGE = 60
```

## Integration with Workspace Module

```python
from workspace import WorkspaceManager
from threads import ThreadManager

workspace_mgr = WorkspaceManager()
thread_mgr = ThreadManager()

# Get workspace
workspace = workspace_mgr.get_workspace(workspace_id=1)

# Create thread in workspace
thread = thread_mgr.create_thread(ThreadCreate(
    name="New Thread",
    workspace_id=workspace.id,
    user_id=current_user_id
))

# Check permissions
can_access = workspace_mgr.check_access(
    workspace_id=workspace.id,
    user_id=current_user_id
)
```

## Next Steps (TODOs)

- [ ] **Todo #3:** Create `thread_manager.py` (thread CRUD operations)
- [ ] **Todo #4:** Create `message_manager.py` (message operations)
- [ ] Create `permissions.py` (access control helpers)
- [ ] Add search functionality
- [ ] Add message filtering/sorting
- [ ] Add thread templates
- [ ] Add bulk operations

## Testing

```bash
# Run thread module tests
pytest AI_infrastructure/tests/test_threads/

# Test specific functionality
pytest AI_infrastructure/tests/test_threads/test_thread_manager.py
pytest AI_infrastructure/tests/test_threads/test_message_manager.py
```

## Dependencies

- `pydantic`: Data validation and serialization
- `sqlite3`: Database operations
- `typing`: Type hints
- `datetime`: Timestamp handling
- `enum`: Enumeration types

## Related Documentation

- `THREAD_DATABASE_REFERENCE.md` - Database schema
- `THREAD_ID_ARCHITECTURE.md` - Thread slug system
- `MESSAGE_STORAGE_COMPLETE_ANALYSIS.md` - Message flow
- `WORKSPACE_MODULE_STRUCTURE.md` - Workspace integration

---

**Status:** Foundation complete (constants, models, exceptions)  
**Next:** Implement managers (TodosΒ #3, #4)  
**Version:** 1.0.0  
**Last Updated:** November 9, 2025

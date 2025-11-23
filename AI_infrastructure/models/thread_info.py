"""
Universal Thread Info Structure - Single Source of Truth
Date: November 17, 2025
Purpose: Standardized thread data structure used across all APIs and UI components
"""
from shared.database_utils import convert_sql_placeholders

from typing import Optional, List, Dict, Any
from datetime import datetime
from dataclasses import dataclass, asdict
from enum import Enum


class ThreadLocation(str, Enum):
    """Thread location options"""
    PRIME = "prime"
    AGENT_1 = "agent-1"
    AGENT_2 = "agent-2"
    AGENT_3 = "agent-3"


@dataclass
class ThreadInfo:
    """
    Universal Thread Info Structure
    
    This is the SINGLE SOURCE OF TRUTH for thread data across:
    - Backend APIs (thread_routes.py, thread_assignment_routes.py, etc.)
    - Frontend UI (ThreadManager, MultiAgent, Synergy)
    - Database (sessions.threads table)
    
    All APIs should return this structure, all UI should consume this structure.
    """
    
    # ========== CORE IDENTITY ==========
    id: str  # thread_slug (external ID used in UI)
    thread_id: int  # Internal database ID
    
    # ========== BASIC INFO ==========
    title: str  # Thread name/title
    created_at: str  # ISO 8601 timestamp
    updated_at: str  # ISO 8601 timestamp
    
    # ========== OWNERSHIP & CONTEXT ==========
    user_id: Optional[int] = None
    workspace_id: Optional[int] = None
    
    # ========== LOCATION & ASSIGNMENT (CASCADE PATTERN) ==========
    location: Optional[str] = None  # 'prime', 'agent-1', 'agent-2', 'agent-3', or None
    
    # ========== THREAD MANAGEMENT ==========
    archived: bool = False
    token_count: int = 0
    message_count: int = 0
    
    # ========== LOCKING (USER-BASED) ==========
    thread_lock_user_id: Optional[int] = None  # NULL = unlocked, user_id = locked
    locked_at: Optional[str] = None  # ISO 8601 timestamp when locked
    locked_by_username: Optional[str] = None  # Username of lock owner (computed)
    is_locked: bool = False  # Computed property (thread_lock_user_id IS NOT NULL)
    
    # ========== UI LINKS (EXTERNAL SYSTEMS) ==========
    synergy_card_id: Optional[str] = None  # Synergy session UUID/slug
    synergy_card_name: Optional[str] = None  # Synergy session title (computed from API)
    synergy_card_desc: Optional[str] = None  # Synergy session description (computed)
    synergy_card_priority: Optional[str] = None  # Synergy priority level (computed)
    
    workflow_slug: Optional[str] = None  # Workflow identifier
    workflow_title: Optional[str] = None  # Workflow display name
    
    internal_doc_slug: Optional[str] = None  # Internal documentation slug
    internal_doc_title: Optional[str] = None  # Internal documentation title
    
    automation_slug: Optional[str] = None  # Automation identifier (NEW)
    automation_title: Optional[str] = None  # Automation display name (NEW)
    
    # ========== BRANCHING/FORKING ==========
    parent_thread_id: Optional[int] = None  # Parent thread ID (for forks)
    branch_name: Optional[str] = None  # Branch label
    branch_point_message_id: Optional[str] = None  # Message ID where branch occurred
    
    # ========== METADATA ==========
    tags: List[str] = None  # List of tags
    metadata: Optional[Dict[str, Any]] = None  # Custom JSON data
    
    # ========== MESSAGES (Optional - loaded on demand) ==========
    messages: Optional[List[Dict[str, Any]]] = None  # Thread conversation
    
    def __post_init__(self):
        """Post-initialization to compute derived fields"""
        # Convert tags from JSON string to list if needed
        if isinstance(self.tags, str):
            import json
            try:
                self.tags = json.loads(self.tags)
            except:
                self.tags = []
        if self.tags is None:
            self.tags = []
        
        # Convert metadata from JSON string to dict if needed
        if isinstance(self.metadata, str):
            import json
            try:
                self.metadata = json.loads(self.metadata)
            except:
                self.metadata = {}
        if self.metadata is None:
            self.metadata = {}
        
        # Compute is_locked property
        self.is_locked = self.thread_lock_user_id is not None
    
    @classmethod
    def from_db_row(cls, row: Dict[str, Any]) -> 'ThreadInfo':
        """
        Create ThreadInfo from database row
        
        Args:
            row: Database row as dict (from sqlite3.Row or psycopg2 DictCursor)
        
        Returns:
            ThreadInfo instance
        """
        return cls(
            id=row.get('thread_slug'),
            thread_id=row.get('id'),
            title=row.get('name', 'Untitled'),
            created_at=row.get('created_at'),
            updated_at=row.get('updated_at'),
            user_id=row.get('user_id'),
            workspace_id=row.get('workspace_id'),
            location=row.get('location'),
            archived=bool(row.get('archived', 0)),
            token_count=row.get('token_count', 0),
            message_count=row.get('message_count', 0),
            thread_lock_user_id=row.get('thread_lock_user_id'),
            locked_at=row.get('locked_at'),
            synergy_card_id=row.get('synergy_card_id'),
            workflow_slug=row.get('workflow_slug'),
            workflow_title=row.get('workflow_title'),
            internal_doc_slug=row.get('internal_doc_slug'),
            internal_doc_title=row.get('internal_doc_title'),
            automation_slug=row.get('automation_slug'),
            automation_title=row.get('automation_title'),
            parent_thread_id=row.get('parent_thread_id'),
            branch_name=row.get('branch_name'),
            branch_point_message_id=row.get('branch_point_message_id'),
            tags=row.get('tags'),
            metadata=row.get('metadata')
        )
    
    def to_dict(self, include_messages: bool = False) -> Dict[str, Any]:
        """
        Convert to dictionary for JSON serialization
        
        Args:
            include_messages: Whether to include messages array (can be large)
        
        Returns:
            Dictionary representation
        """
        data = asdict(self)
        
        # Remove messages if not requested (saves bandwidth)
        if not include_messages:
            data.pop('messages', None)
        
        # Remove None values to reduce payload size
        return {k: v for k, v in data.items() if v is not None}
    
    def to_frontend_format(self) -> Dict[str, Any]:
        """
        Convert to frontend format (legacy compatibility)
        
        Frontend expects:
        - id (thread_slug)
        - title (name)
        - created (created_at)
        - updated (updated_at)
        - agent (location) - for backwards compatibility
        - message_count
        - etc.
        
        Returns:
            Dictionary in frontend format
        """
        return {
            'id': self.id,
            'title': self.title,
            'created': self.created_at,
            'updated': self.updated_at,
            'agent': self.location,  # Legacy field name
            'location': self.location,
            'archived': self.archived,
            'token_count': self.token_count,
            'message_count': self.message_count,
            'messages': self.messages or [],
            
            # Locking
            'thread_lock_user_id': self.thread_lock_user_id,
            'locked_at': self.locked_at,
            'locked_by_username': self.locked_by_username,
            'is_locked': self.is_locked,
            
            # UI Links
            'synergy_card_id': self.synergy_card_id,
            'synergy_card_name': self.synergy_card_name,
            'synergy_card_desc': self.synergy_card_desc,
            'synergy_card_priority': self.synergy_card_priority,
            
            'workflow_slug': self.workflow_slug,
            'workflow_title': self.workflow_title,
            'workflow_id': self.workflow_slug,  # Legacy alias
            'workflow_name': self.workflow_title,  # Legacy alias
            
            'internal_doc_slug': self.internal_doc_slug,
            'internal_doc_title': self.internal_doc_title,
            
            'automation_slug': self.automation_slug,
            'automation_title': self.automation_title,
            
            # Branching
            'parent_thread_id': self.parent_thread_id,
            'branch_name': self.branch_name,
            'branch_point_message_id': self.branch_point_message_id,
            
            # Metadata
            'tags': self.tags,
            'metadata': self.metadata,
            
            # User/Workspace
            'user_id': self.user_id,
            'workspace_id': self.workspace_id
        }


# ========== SQL QUERY TEMPLATES ==========

THREAD_SELECT_COLUMNS = """
    t.id,
    t.thread_slug,
    t.name,
    t.created_at,
    t.updated_at,
    t.user_id,
    t.workspace_id,
    t.location,
    t.archived,
    t.token_count,
    t.thread_lock_user_id,
    t.locked_at,
    t.synergy_card_id,
    t.workflow_slug,
    t.workflow_title,
    t.internal_doc_slug,
    t.internal_doc_title,
    t.automation_slug,
    t.automation_title,
    t.parent_thread_id,
    t.branch_name,
    t.branch_point_message_id,
    t.tags,
    t.metadata,
    COUNT(m.id) as message_count
"""

THREAD_SELECT_FROM = """
FROM sessions.threads t
LEFT JOIN sessions.messages m ON t.id = m.thread_id
"""

THREAD_SELECT_GROUP_BY = """
GROUP BY t.id, t.thread_slug, t.name, t.user_id, t.created_at, t.updated_at,
         t.workspace_id, t.location, t.archived, t.token_count,
         t.thread_lock_user_id, t.locked_at,
         t.synergy_card_id, t.workflow_slug, t.workflow_title,
         t.internal_doc_slug, t.internal_doc_title,
         t.automation_slug, t.automation_title,
         t.parent_thread_id, t.branch_name, t.branch_point_message_id,
         t.tags, t.metadata
"""

THREAD_SELECT_ORDER_BY = """
ORDER BY t.updated_at DESC
"""


# ========== HELPER FUNCTIONS ==========

def get_thread_by_slug(cursor, thread_slug: str) -> Optional[ThreadInfo]:
    """
    Get single thread by slug with message count
    
    Args:
        cursor: Database cursor
        thread_slug: Thread slug to fetch
    
    Returns:
        ThreadInfo instance or None if not found
    """
    query = f"""
        SELECT {THREAD_SELECT_COLUMNS}
        {THREAD_SELECT_FROM}
        WHERE t.thread_slug = %s
        {THREAD_SELECT_GROUP_BY}
    """
    
    cursor.execute(query, [thread_slug])
    row = cursor.fetchone()
    
    if not row:
        return None
    
    # Convert row to dict (handles both sqlite3.Row and psycopg2)
    if hasattr(row, 'keys'):
        row_dict = dict(row)
    else:
        columns = [desc[0] for desc in cursor.description]
        row_dict = dict(zip(columns, row))
    
    return ThreadInfo.from_db_row(row_dict)


def get_all_threads(cursor, user_id: Optional[int] = None, 
                    include_archived: bool = False) -> List[ThreadInfo]:
    """
    Get all threads for user with message counts
    
    Args:
        cursor: Database cursor
        user_id: Filter by user ID (optional)
        include_archived: Include archived threads (default: False)
    
    Returns:
        List of ThreadInfo instances
    """
    query = f"""
        SELECT {THREAD_SELECT_COLUMNS}
        {THREAD_SELECT_FROM}
        WHERE 1=1
    """
    
    params = []
    
    if user_id:
        query += " AND t.user_id = %s"
        params.append(user_id)
    
    if not include_archived:
        query += " AND t.archived = 0"
    
    query += f"""
        {THREAD_SELECT_GROUP_BY}
        {THREAD_SELECT_ORDER_BY}
    """
    
    cursor.execute(query, params)
    rows = cursor.fetchall()
    
    threads = []
    for row in rows:
        # Convert row to dict
        if hasattr(row, 'keys'):
            row_dict = dict(row)
        else:
            columns = [desc[0] for desc in cursor.description]
            row_dict = dict(zip(columns, row))
        
        threads.append(ThreadInfo.from_db_row(row_dict))
    
    return threads


def update_thread_location(cursor, thread_slug: str, location: str) -> bool:
    """
    Update thread location (CASCADE PATTERN - Database First)
    
    Args:
        cursor: Database cursor
        thread_slug: Thread slug to update
        location: New location ('prime', 'agent-1', etc.)
    
    Returns:
        True if updated, False if not found
    """
    query = """
        UPDATE sessions.threads
        SET location = %s,
            updated_at = CURRENT_TIMESTAMP
        WHERE thread_slug = %s
    """
    
    cursor.execute(query, [location, thread_slug])
    return cursor.rowcount > 0


def lock_thread(cursor, thread_slug: str, user_id: int) -> bool:
    """
    Lock thread for editing by user
    
    Args:
        cursor: Database cursor
        thread_slug: Thread slug to lock
        user_id: User ID who is locking
    
    Returns:
        True if locked, False if already locked by someone else
    """
    # Check if already locked
    cursor.execute("""
        SELECT thread_lock_user_id, locked_at
        FROM sessions.threads
        WHERE thread_slug = %s
    """, [thread_slug])
    
    row = cursor.fetchone()
    if not row:
        return False
    
    current_lock_user = row[0] if isinstance(row, tuple) else row['thread_lock_user_id']
    
    if current_lock_user and current_lock_user != user_id:
        # Already locked by someone else
        # Check if lock is stale (>30 minutes)
        from datetime import datetime, timedelta
        locked_at = row[1] if isinstance(row, tuple) else row['locked_at']
        
        if locked_at:
            lock_time = datetime.fromisoformat(locked_at)
            if datetime.now() - lock_time < timedelta(minutes=30):
                return False  # Lock is fresh, can't steal it
    
    # Lock thread
    cursor.execute("""
        UPDATE sessions.threads
        SET thread_lock_user_id = %s,
            locked_at = CURRENT_TIMESTAMP
        WHERE thread_slug = %s
    """, [user_id, thread_slug])
    
    return True


def unlock_thread(cursor, thread_slug: str, user_id: Optional[int] = None) -> bool:
    """
    Unlock thread
    
    Args:
        cursor: Database cursor
        thread_slug: Thread slug to unlock
        user_id: User ID who is unlocking (optional - if provided, only unlock if this user owns the lock)
    
    Returns:
        True if unlocked, False if not found or not authorized
    """
    if user_id:
        # Only unlock if this user owns the lock
        query = """
            UPDATE sessions.threads
            SET thread_lock_user_id = NULL,
                locked_at = NULL
            WHERE thread_slug = %s
              AND thread_lock_user_id = %s
        """
        cursor.execute(query, [thread_slug, user_id])
    else:
        # Force unlock (admin action)
        query = """
            UPDATE sessions.threads
            SET thread_lock_user_id = NULL,
                locked_at = NULL
            WHERE thread_slug = %s
        """
        cursor.execute(query, [thread_slug])
    
    return cursor.rowcount > 0


# ========== USAGE EXAMPLES ==========

"""
# Backend API Example (thread_routes.py)

@thread_bp.route('/list', methods=['GET'])
def list_threads():
    user_id = request.args.get('user_id', 1)
    include_archived = request.args.get('archived', 'false') == 'true'
    
    conn = get_database_connection('sessions')
    cursor = conn.cursor()
    
    # Get all threads using universal structure
    threads = get_all_threads(cursor, user_id, include_archived)
    
    conn.close()
    
    # Convert to frontend format
    return jsonify({
        'success': True,
        'threads': [t.to_frontend_format() for t in threads]
    })


# Frontend JavaScript Example (ThreadManager)

async loadThreads() {
    const response = await fetch('/api/threads/list?user_id=1');
    const data = await response.json();
    
    // All threads now have consistent structure
    this.threads = data.threads;
    
    // Access fields consistently
    this.threads.forEach(thread => {
        console.log(`Thread: ${thread.title}`);
        console.log(`Location: ${thread.location}`);
        console.log(`Locked: ${thread.is_locked}`);
        console.log(`Synergy: ${thread.synergy_card_name}`);
        console.log(`Automation: ${thread.automation_title}`);
    });
}
"""

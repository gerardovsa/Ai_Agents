"""
Thread Management Routes
Thread/conversation management for all AI agents
"""

from flask import Blueprint, request
import json
from datetime import datetime, timedelta

# Import infrastructure
from core.agent_state_manager import agent_state_manager
from utils.database_helpers import (
    execute_sqlite_query, execute_sqlite_update,
    get_sessions_database_path, DatabaseConnectionError  # FIXED: Use sessions.db, not stock db
)
from utils.response_helpers import (
    success_response, error_response, list_response,
    deleted_response, updated_response
)

# Create blueprint
thread_bp = Blueprint('threads', __name__, url_prefix='/api/threads')


# ============================================================
# THREAD CREATION
# ============================================================

@thread_bp.route('/create', methods=['POST'])
def create_thread():
    """
    Create a new thread with backend-generated UUID
    
    Body params:
        user_id (int, required): User creating the thread
        agent_id (str, optional): Agent ID (default: 'prime')
        title (str, optional): Thread title (default: 'New Chat')
        parent_thread_id (str, optional): Parent thread ID for branching
        branch_point_message_id (str, optional): Message ID to branch from
        branch_name (str, optional): Name of the branch
    
    Returns:
        {
            "success": true,
            "thread": {
                "id": "uuid-generated-by-backend",
                "title": "New Chat",
                "created": "ISO timestamp",
                "agent_id": "prime",
                "parent_thread_id": "...",
                "branch_point_message_id": "...",
                "branch_name": "..."
            }
        }
    """
    try:
        import uuid
        
        data = request.get_json() or {}
        user_id = data.get('user_id')
        agent_id = data.get('agent_id', 'prime')
        title = data.get('title', 'New Chat')
        location = data.get('location', 'prime')
        tags = data.get('tags', [])
        synergy_card_id = data.get('synergy_card_id')
        
        # NEW: Branching parameters
        parent_thread_id = data.get('parent_thread_id')
        branch_point_message_id = data.get('branch_point_message_id')
        branch_name = data.get('branch_name')
        
        if not user_id:
            return error_response('user_id required', 400)
        
        # Generate timestamp-based ID (consistent with frontend)
        thread_id = str(int(datetime.now().timestamp() * 1000))
        created = datetime.now().isoformat()
        
        # Insert into database
        db_path = get_sessions_database_path()
        
        insert_query = """
            INSERT INTO threads (
                thread_slug, workspace_id, name, user_id, created_at, updated_at,
                metadata, location, tags, synergy_card_id,
                parent_thread_id, branch_point_message_id, branch_name
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """
        
        execute_sqlite_update(
            db_path,
            insert_query,
            (
                thread_id,                      # thread_slug
                1,                              # workspace_id (default workspace)
                title,                          # name
                user_id,                        # user_id
                created,                        # created_at
                created,                        # updated_at
                json.dumps({}),                 # metadata
                location,                       # location
                json.dumps(tags),               # tags (NEW: from request)
                synergy_card_id,                # synergy_card_id (NEW: from request)
                parent_thread_id,               # parent_thread_id
                branch_point_message_id,        # branch_point_message_id
                branch_name                     # branch_name
            )
        )
        
        thread_data = {
            'id': thread_id,
            'title': title,
            'created': created,
            'agent_id': agent_id,
            'user_id': user_id,
            'parent_thread_id': parent_thread_id,
            'branch_point_message_id': branch_point_message_id,
            'branch_name': branch_name
        }
        
        return success_response(
            {'thread': thread_data},
            message='Thread created successfully'
        )
        
    except Exception as e:
        return error_response(f'Failed to create thread: {str(e)}', 500)


# ============================================================
# THREAD LISTING & SEARCH
# ============================================================

@thread_bp.route('/list', methods=['GET'])
def list_threads():
    """
    List threads from database for a specific user
    
    Query params:
        ?user_id=1 (required): User ID to list threads for
        ?limit=50 (optional): Max threads to return
    
    Returns list of threads from sessions.db threads table
    """
    try:
        user_id = request.args.get('user_id')
        if not user_id:
            return error_response("user_id is required", 400)
        
        limit = int(request.args.get('limit', 50))
        
        # Query threads from database with message counts and metadata
        db_path = get_sessions_database_path()
        
        query = """
            SELECT 
                t.id,
                t.thread_slug, 
                t.name, 
                t.user_id, 
                t.created_at, 
                t.updated_at, 
                t.metadata, 
                t.location, 
                t.tags, 
                t.synergy_card_id, 
                t.parent_thread_id, 
                t.branch_name,
                COUNT(m.id) as message_count,
                MAX(m.timestamp) as last_message_time,
                (SELECT role FROM messages WHERE thread_id = t.id ORDER BY timestamp DESC LIMIT 1) as last_message_role
            FROM threads t
            LEFT JOIN messages m ON t.id = m.thread_id
            WHERE t.user_id = ?
            GROUP BY t.id, t.thread_slug, t.name, t.user_id, t.created_at, t.updated_at, 
                     t.metadata, t.location, t.tags, t.synergy_card_id, 
                     t.parent_thread_id, t.branch_name
            ORDER BY t.updated_at DESC
            LIMIT ?
        """
        
        # execute_sqlite_query returns list of dicts directly
        rows = execute_sqlite_query(db_path, query, (user_id, limit))
        
        threads = []
        for row in rows:
            # Rows are returned as dicts from execute_sqlite_query
            thread_data = {
                'id': row['thread_slug'],
                'thread_id': row['id'],  # Internal database ID
                'title': row['name'],
                'user_id': row['user_id'],
                'created': row['created_at'],
                'updated': row['updated_at'],
                'metadata': json.loads(row['metadata']) if row['metadata'] else {},
                'location': row['location'] or 'prime',
                'agent': row['location'] or 'main',  # Alias for frontend compatibility
                'tags': json.loads(row['tags']) if row['tags'] else [],
                'synergy_card_id': row['synergy_card_id'],
                'parent_thread_id': row['parent_thread_id'],
                'branch_name': row['branch_name'],
                'message_count': row['message_count'] or 0,
                'last_message_time': row['last_message_time'],
                'last_message_role': row['last_message_role'],
                'archived': False  # Default for now, add column later if needed
            }
            threads.append(thread_data)
        
        return success_response({
            'threads': threads,
            'count': len(threads)
        }, message=f"Found {len(threads)} threads for user {user_id}")
    
    except Exception as e:
        return error_response(f"Failed to list threads: {str(e)}", 500)


@thread_bp.route('/list-legacy', methods=['GET'])
def list_threads_legacy():
    """
    LEGACY: List all conversation threads across all agents from agent_state_manager
    
    Query params:
        ?agent_id=stock_ai (optional filter)
        ?limit=50 (default 50)
        ?days=30 (show threads from last N days)
    
    Returns list of threads with metadata
    """
    try:
        agent_filter = request.args.get('agent_id')
        limit = int(request.args.get('limit', 50))
        days = int(request.args.get('days', 30))
        
        cutoff_date = datetime.now() - timedelta(days=days)
        
        threads = []
        
        # Get threads from agent_state_manager
        for agent_id, sessions in agent_state_manager._agent_states.items():
            # Filter by agent if specified
            if agent_filter and agent_id != agent_filter:
                continue
            
            for session_id, state in sessions.items():
                # Get last activity timestamp
                last_activity = state.get('last_activity')
                
                # Filter by date if we have timestamp
                if last_activity:
                    try:
                        activity_time = datetime.fromisoformat(last_activity)
                        if activity_time < cutoff_date:
                            continue
                    except:
                        pass
                
                # Get agent display name
                agent_name = agent_state_manager._agent_names.get(agent_id, agent_id)
                
                threads.append({
                    'thread_id': f"{agent_id}_{session_id}",
                    'session_id': session_id,
                    'agent_id': agent_id,
                    'agent_name': agent_name,
                    'message_count': len(state['conversation']),
                    'status': state['status'],
                    'created_at': state.get('created_at'),
                    'last_activity': last_activity,
                    'context': state.get('context', {}),
                    'location': state.get('location', 'prime'),  # NEW: Thread location
                    'user_id': state.get('user_id', 1)  # NEW: User ID
                })
        
        # Sort by last activity (most recent first)
        threads.sort(key=lambda x: x.get('last_activity', ''), reverse=True)
        
        # Apply limit
        threads = threads[:limit]
        
        return list_response(threads, message=f"Found {len(threads)} threads")
    
    except Exception as e:
        return error_response(str(e), 500)


@thread_bp.route('/search', methods=['GET'])
def search_threads():
    """
    Search threads by message content
    
    Query params:
        ?q=invoice (required - search keyword)
        ?agent_id=stock_ai (optional filter)
        ?limit=20 (default 20)
    
    Searches conversation content for keyword
    """
    try:
        keyword = request.args.get('q', '').strip().lower()
        agent_filter = request.args.get('agent_id')
        limit = int(request.args.get('limit', 20))
        
        if not keyword:
            return error_response("Missing search keyword 'q'", 400)
        
        matching_threads = []
        
        # Search through all agent states
        for agent_id, sessions in agent_state_manager._agent_states.items():
            if agent_filter and agent_id != agent_filter:
                continue
            
            for session_id, state in sessions.items():
                # Search conversation content
                matches = []
                for i, message in enumerate(state['conversation']):
                    content = str(message.get('content', '')).lower()
                    if keyword in content:
                        matches.append({
                            'message_index': i,
                            'role': message.get('role'),
                            'snippet': content[:200]  # First 200 chars
                        })
                
                if matches:
                    agent_name = agent_state_manager._agent_names.get(agent_id, agent_id)
                    
                    matching_threads.append({
                        'thread_id': f"{agent_id}_{session_id}",
                        'session_id': session_id,
                        'agent_id': agent_id,
                        'agent_name': agent_name,
                        'message_count': len(state['conversation']),
                        'match_count': len(matches),
                        'matches': matches[:3],  # First 3 matches
                        'last_activity': state.get('last_activity')
                    })
        
        # Sort by match count (most matches first)
        matching_threads.sort(key=lambda x: x['match_count'], reverse=True)
        
        # Apply limit
        matching_threads = matching_threads[:limit]
        
        return list_response(
            matching_threads,
            message=f"Found {len(matching_threads)} threads matching '{keyword}'"
        )
    
    except Exception as e:
        return error_response(str(e), 500)


# ============================================================
# THREAD OPERATIONS (CRUD)
# ============================================================

@thread_bp.route('/save', methods=['POST'])
def save_thread():
    """
    Save thread to persistent storage
    
    FLEXIBLE PARAMETERS - Accepts both formats:
    
    Format 1 (Backend format):
    {
        "agent_id": "stock_ai",
        "session_id": "uuid",
        "thread_name": "Invoice Analysis Oct 2025" (optional),
        "user_id": 1 (optional)
    }
    
    Format 2 (Frontend format):
    {
        "thread_id": "xyz",
        "title": "My Thread",
        "messages": [...],
        "agent": "main",
        "user_id": 1,
        "location": "agent-1" (optional - for thread assignment integration)
    }
    
    Saves thread to SQLite for long-term storage
    """
    try:
        data = request.json
        
        # FLEXIBLE PARAMETER MAPPING: Support both formats
        # Format 1: agent_id + session_id
        # Format 2: thread_id + messages + title
        
        # Detect format and normalize
        if 'thread_id' in data and 'messages' in data:
            # Format 2 (Frontend) - convert to internal format
            thread_id = str(data.get('thread_id'))  # Convert to string immediately
            title = data.get('title', 'Untitled Thread')
            messages = data.get('messages', [])
            agent = data.get('agent', 'prime')
            user_id = data.get('user_id', 1)
            location = str(data.get('location', 'prime'))  # Convert to string
            
            # NEW METADATA FIELDS
            tags = json.dumps(data.get('tags', []))
            synergy_card_id = data.get('synergy_card_id')
            parent_thread_id = data.get('parent_thread_id')
            branch_point_message_id = data.get('branch_point_message_id')
            branch_name = data.get('branch_name')
            summary = data.get('summary')
            summary_generated_at = data.get('summary_generated_at')
            
            # Parse thread_id if it's in format "agent_session"
            if '_' in thread_id:
                parts = thread_id.split('_', 1)
                agent_id = parts[0]
                session_id = parts[1]
            else:
                agent_id = agent
                session_id = thread_id
            
            thread_name = title
            conversation = messages
            
        else:
            # Format 1 (Backend) - use as-is
            agent_id = data.get('agent_id')
            session_id = data.get('session_id')
            thread_name = data.get('thread_name', '')
            user_id = data.get('user_id', 1)
            location = data.get('location', 'prime')
            conversation = None  # Will fetch from agent_state_manager
            
            # NEW METADATA FIELDS (default to None for backend format)
            tags = '[]'
            synergy_card_id = None
            parent_thread_id = None
            branch_point_message_id = None
            branch_name = None
            summary = None
            summary_generated_at = None
        
        # Validate required fields
        if not agent_id or not session_id:
            return error_response("Missing agent_id/session_id or thread_id", 400)
        
        # Ensure agent_id and session_id are strings (not integers)
        agent_id = str(agent_id) if agent_id is not None else None
        session_id = str(session_id) if session_id is not None else None
        location = str(location) if location is not None else 'prime'
        
        # Get thread state from agent_state_manager if conversation not provided
        if conversation is None:
            state = agent_state_manager.get_or_create_state(agent_id, session_id, {})
            
            if not state['conversation']:
                return error_response("Thread has no messages to save", 400)
            
            conversation = state['conversation']
        
        if not conversation:
            return error_response("Thread has no messages to save", 400)
        
        # Save to SQLite
        db_path = get_sessions_database_path()
        
        # Create threads table if not exists (UPDATED SCHEMA with new metadata fields)
        create_table_query = """
            CREATE TABLE IF NOT EXISTS saved_threads (
                thread_id TEXT PRIMARY KEY,
                agent_id TEXT NOT NULL,
                session_id TEXT NOT NULL,
                user_id INTEGER DEFAULT 1,
                location TEXT DEFAULT 'prime',
                thread_name TEXT,
                conversation TEXT NOT NULL,
                message_count INTEGER,
                context TEXT,
                created_at TEXT,
                saved_at TEXT DEFAULT CURRENT_TIMESTAMP,
                last_updated TEXT DEFAULT CURRENT_TIMESTAMP,
                tags TEXT DEFAULT '[]',
                synergy_card_id TEXT DEFAULT NULL,
                parent_thread_id TEXT DEFAULT NULL,
                branch_point_message_id TEXT DEFAULT NULL,
                branch_name TEXT DEFAULT NULL,
                summary TEXT DEFAULT NULL,
                summary_generated_at TEXT DEFAULT NULL
            )
        """
        execute_sqlite_update(db_path, create_table_query, None)
        
        # Insert thread
        thread_id = f"{agent_id}_{session_id}"
        conversation_json = json.dumps(conversation)
        context_json = json.dumps({})  # Empty context for frontend threads
        
        insert_query = """
            INSERT OR REPLACE INTO saved_threads 
            (thread_id, agent_id, session_id, user_id, location, thread_name, conversation, 
             message_count, context, saved_at, last_updated,
             tags, synergy_card_id, parent_thread_id, branch_point_message_id, 
             branch_name, summary, summary_generated_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, datetime('now'), datetime('now'),
                    ?, ?, ?, ?, ?, ?, ?)
        """
        
        params = [
            thread_id,
            agent_id,
            session_id,
            user_id,
            location,
            thread_name,
            conversation_json,
            len(conversation),
            context_json,
            # NEW METADATA FIELDS
            tags,
            synergy_card_id,
            parent_thread_id,
            branch_point_message_id,
            branch_name,
            summary,
            summary_generated_at
        ]
        
        execute_sqlite_update(db_path, insert_query, params)
        
        # INTEGRATION: Update thread assignments in sessions.db if location is an agent
        if location and location != 'prime' and location.startswith('agent-'):
            try:
                from routes.thread_assignment_routes import enforce_thread_assignment_rules
                enforce_thread_assignment_rules(user_id, session_id, location)
                print(f"✅ [Thread Save] Updated thread assignment: {session_id} -> {location}")
            except Exception as e:
                print(f"⚠️ [Thread Save] Failed to update thread assignment: {e}")
        
        return success_response({
            'thread_id': thread_id,
            'message_count': len(conversation),
            'saved_at': datetime.now().isoformat(),
            'location': location
        }, message="Thread saved successfully")
    
    except DatabaseConnectionError as e:
        return error_response(f"Database error: {str(e)}", 500)
    except Exception as e:
        return error_response(str(e), 500)


@thread_bp.route('/load/<thread_id>', methods=['GET'])
def load_thread(thread_id):
    """
    Load saved thread from persistent storage
    
    Returns thread with full conversation history
    """
    try:
        db_path = get_sessions_database_path()
        
        query = """
            SELECT 
                thread_id,
                agent_id,
                session_id,
                user_id,
                location,
                thread_name,
                conversation,
                message_count,
                context,
                created_at,
                saved_at,
                last_updated
            FROM saved_threads
            WHERE thread_id = ?
        """
        
        results = execute_sqlite_query(db_path, query, [thread_id])
        
        if not results:
            return error_response(f"Thread {thread_id} not found", 404)
        
        thread = results[0]
        
        # Parse JSON fields
        thread['conversation'] = json.loads(thread['conversation'])
        thread['context'] = json.loads(thread.get('context', '{}'))
        
        return success_response(thread, message="Thread loaded successfully")
    
    except DatabaseConnectionError as e:
        return error_response(f"Database error: {str(e)}", 500)
    except Exception as e:
        return error_response(str(e), 500)


# NOTE: The /details endpoint is defined later (line ~1015) with comprehensive agent assignment support
# This duplicate has been removed to prevent route conflicts


@thread_bp.route('/<thread_id>', methods=['DELETE'])
def delete_thread(thread_id):
    """
    Delete saved thread from persistent storage
    
    Supports both formats:
    - UUID format: "sess_abc123" or any UUID
    - Legacy format: "agent_id_session_id"
    
    Also clears from agent_state_manager if active
    """
    try:
        # Try to parse as legacy format (agent_id_session_id)
        parts = thread_id.split('_', 1)
        if len(parts) == 2 and not thread_id.startswith('sess_'):
            # Legacy format
            agent_id, session_id = parts
            
            # Clear from agent_state_manager if active
            agent_state_manager.clear_conversation(agent_id, session_id)
        else:
            # UUID format (sess_abc123 or similar) - no need to parse
            # Just clear from state manager with the full ID
            agent_state_manager.clear_conversation('prime', thread_id)
        
        # Delete from SQLite (saved_threads table)
        db_path = get_sessions_database_path()
        
        delete_query = """
            DELETE FROM saved_threads
            WHERE thread_id = ?
        """
        
        rowcount = execute_sqlite_update(db_path, delete_query, [thread_id])
        
        if rowcount == 0:
            return error_response(f"Thread {thread_id} not found", 404)
        
        return deleted_response(
            message="Thread deleted successfully",
            deleted_count=rowcount
        )
    
    except DatabaseConnectionError as e:
        return error_response(f"Database error: {str(e)}", 500)
    except Exception as e:
        return error_response(str(e), 500)
        return error_response(str(e), 500)


@thread_bp.route('/<thread_id>/update', methods=['PATCH'])
def update_thread_metadata(thread_id):
    """
    Update thread metadata (title, tags, synergy_card_id, etc.)
    
    Request JSON:
    {
        "name": "New Thread Title" (optional),
        "tags": ["tag1", "tag2"] (optional),
        "synergy_card_id": "sess_xxx" (optional),
        "location": "prime" (optional)
    }
    """
    try:
        data = request.json
        if not data:
            return error_response("No data provided", 400)
        
        # Build dynamic UPDATE query
        update_fields = []
        params = []
        
        if 'name' in data:
            update_fields.append("name = ?")
            params.append(data['name'])
        
        if 'tags' in data:
            update_fields.append("tags = ?")
            params.append(json.dumps(data['tags']))
        
        if 'synergy_card_id' in data:
            update_fields.append("synergy_card_id = ?")
            params.append(data['synergy_card_id'])
        
        if 'location' in data:
            update_fields.append("location = ?")
            params.append(data['location'])
        
        if not update_fields:
            return error_response("No valid fields to update", 400)
        
        # Add updated_at timestamp
        update_fields.append("updated_at = datetime('now')")
        params.append(thread_id)
        
        # Execute UPDATE
        db_path = get_sessions_database_path()
        update_query = f"""
            UPDATE threads
            SET {', '.join(update_fields)}
            WHERE thread_slug = ?
        """
        
        rowcount = execute_sqlite_update(db_path, update_query, params)
        
        if rowcount == 0:
            return error_response(f"Thread {thread_id} not found", 404)
        
        return success_response({
            'thread_id': thread_id,
            'updated_fields': list(data.keys())
        }, message="Thread updated successfully")
    
    except DatabaseConnectionError as e:
        return error_response(f"Database error: {str(e)}", 500)
    except Exception as e:
        return error_response(str(e), 500)


# ============================================================
# THREAD STATISTICS
# ============================================================

@thread_bp.route('/stats', methods=['GET'])
def get_thread_stats():
    """
    Get thread statistics across all agents
    
    Returns:
    {
        "total_threads": 45,
        "total_messages": 1250,
        "by_agent": {
            "stock_ai": {"threads": 20, "messages": 500},
            "data_agent": {"threads": 15, "messages": 450}
        },
        "active_threads": 12,
        "saved_threads": 8
    }
    """
    try:
        stats = {
            'total_threads': 0,
            'total_messages': 0,
            'by_agent': {},
            'active_threads': 0,
            'saved_threads': 0
        }
        
        # Count active threads from agent_state_manager
        for agent_id, sessions in agent_state_manager._agent_states.items():
            agent_thread_count = len(sessions)
            agent_message_count = sum(len(s['conversation']) for s in sessions.values())
            
            stats['by_agent'][agent_id] = {
                'threads': agent_thread_count,
                'messages': agent_message_count,
                'agent_name': agent_state_manager._agent_names.get(agent_id, agent_id)
            }
            
            stats['total_threads'] += agent_thread_count
            stats['total_messages'] += agent_message_count
        
        stats['active_threads'] = stats['total_threads']
        
        # Count saved threads from SQLite
        try:
            db_path = get_sessions_database_path()
            
            count_query = """
                SELECT COUNT(*) as count
                FROM saved_threads
            """
            
            results = execute_sqlite_query(db_path, count_query, None)
            if results:
                stats['saved_threads'] = results[0]['count']
        except:
            # Table might not exist yet
            stats['saved_threads'] = 0
        
        return success_response(stats, message="Thread statistics")
    
    except Exception as e:
        return error_response(str(e), 500)


# ============================================================
# AUTO-SAVE & MARK READ
# ============================================================

@thread_bp.route('/autosave', methods=['POST'])
def autosave_thread():
    """
    Auto-save thread during conversation
    
    Request JSON:
    {
        "agent_id": "stock_ai",
        "session_id": "uuid"
    }
    
    Automatically saves thread every N messages
    """
    try:
        data = request.json
        agent_id = data.get('agent_id')
        session_id = data.get('session_id')
        
        if not agent_id or not session_id:
            return error_response("Missing agent_id or session_id", 400)
        
        # Get thread state
        state = agent_state_manager.get_or_create_state(agent_id, session_id, {})
        
        message_count = len(state['conversation'])
        
        # Only auto-save if we have messages
        if message_count == 0:
            return success_response({
                'autosaved': False,
                'reason': 'No messages to save'
            })
        
        # Auto-save every 5 messages
        if message_count % 5 == 0:
            # Save to SQLite
            db_path = get_sessions_database_path()
            
            # Ensure table exists
            create_table_query = """
                CREATE TABLE IF NOT EXISTS saved_threads (
                    thread_id TEXT PRIMARY KEY,
                    agent_id TEXT NOT NULL,
                    session_id TEXT NOT NULL,
                    thread_name TEXT,
                    conversation TEXT NOT NULL,
                    message_count INTEGER,
                    context TEXT,
                    created_at TEXT,
                    saved_at TEXT DEFAULT CURRENT_TIMESTAMP
                )
            """
            execute_sqlite_update(db_path, create_table_query, None)
            
            # Save thread
            thread_id = f"{agent_id}_{session_id}"
            conversation_json = json.dumps(state['conversation'])
            context_json = json.dumps(state.get('context', {}))
            
            insert_query = """
                INSERT OR REPLACE INTO saved_threads 
                (thread_id, agent_id, session_id, thread_name, conversation, 
                 message_count, context, created_at, saved_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, datetime('now'))
            """
            
            params = [
                thread_id,
                agent_id,
                session_id,
                f"Auto-saved conversation ({message_count} messages)",
                conversation_json,
                message_count,
                context_json,
                state.get('created_at')
            ]
            
            execute_sqlite_update(db_path, insert_query, params)
            
            return success_response({
                'autosaved': True,
                'message_count': message_count,
                'thread_id': thread_id
            }, message="Thread auto-saved")
        
        return success_response({
            'autosaved': False,
            'reason': f"Waiting for milestone ({message_count} messages)"
        })
    
    except Exception as e:
        return error_response(str(e), 500)


@thread_bp.route('/<thread_id>/mark-read', methods=['POST'])
def mark_thread_read(thread_id):
    """
    Mark thread as read
    
    Updates last_read timestamp for thread
    """
    try:
        db_path = get_sessions_database_path()
        
        # Ensure table has last_read column
        alter_query = """
            ALTER TABLE saved_threads
            ADD COLUMN last_read TEXT
        """
        
        try:
            execute_sqlite_update(db_path, alter_query, None)
        except:
            # Column might already exist
            pass
        
        # Update last_read
        update_query = """
            UPDATE saved_threads
            SET last_read = datetime('now')
            WHERE thread_id = ?
        """
        
        rowcount = execute_sqlite_update(db_path, update_query, [thread_id])
        
        if rowcount == 0:
            return error_response(f"Thread {thread_id} not found", 404)
        
        return updated_response(
            message="Thread marked as read",
            updated_count=rowcount
        )
    
    except DatabaseConnectionError as e:
        return error_response(f"Database error: {str(e)}", 500)
    except Exception as e:
        return error_response(str(e), 500)


@thread_bp.route('/details', methods=['POST'])
def get_threads_details():
    """
    Get detailed information for multiple threads including agent assignments
    
    SYNERGY INTEGRATION: Used to display linked threads in Synergy cards
    Fetches thread details from threads table and agent assignments from thread_assignments table
    
    Body params:
        thread_ids (list): Array of thread IDs to fetch details for
    
    Returns:
        Array of thread objects with: id, name, thread_slug, agent_id, agent_name, created, updated
    """
    print("[THREADS DETAILS] Endpoint called!")
    print("[THREADS DETAILS] Step 1: Getting request data...")
    try:
        data = request.get_json()
        print(f"[THREADS DETAILS] Step 2: Got data: {data}")
        thread_ids = data.get('thread_ids', [])
        print(f"[THREADS DETAILS] Step 3: Thread IDs: {thread_ids}")
        
        if not thread_ids or not isinstance(thread_ids, list):
            return error_response("thread_ids array required", 400)
        
        if len(thread_ids) == 0:
            return success_response([])
        
        print("[THREADS DETAILS] Step 4: Building query...")
        # Build query with placeholders
        placeholders = ','.join(['?' for _ in thread_ids])
        print(f"[THREADS DETAILS] Step 5: Placeholders: {placeholders}")
        
        # Query threads from sessions.db
        print("[THREADS DETAILS] Step 6: Getting database path...")
        # Note: thread_assignments is in ai_infrastructure.db, not sessions.db
        # We need to query sessions.db for threads, then join with assignments separately
        db_path = get_sessions_database_path()
        print(f"[THREADS DETAILS] Step 7: DB path: {db_path}")
        query = f"""
            SELECT 
                t.id,
                t.thread_slug,
                t.name,
                t.created_at,
                t.updated_at,
                t.synergy_card_id,
                t.location
            FROM threads t
            WHERE t.id IN ({placeholders}) OR t.thread_slug IN ({placeholders})
            ORDER BY t.updated_at DESC
        """
        
        # Duplicate thread_ids for both id and thread_slug matching
        params = thread_ids + thread_ids
        print(f"[THREADS DETAILS] Step 8: Executing query with {len(params)} params...")
        threads = execute_sqlite_query(db_path, query, params)
        print(f"[THREADS DETAILS] Step 9: Got {len(threads)} threads")
        
        # Now get agent assignments from ai_infrastructure.db
        print("[THREADS DETAILS] Step 10: Getting agent assignments...")
        from pathlib import Path
        import sqlite3
        root_dir = Path(__file__).parent.parent.parent
        ai_db = root_dir / 'data' / 'ai_infrastructure.db'
        print(f"[THREADS DETAILS] Step 11: AI DB path: {ai_db}")
        
        assignments = {}
        try:
            print("[THREADS DETAILS] Step 12: Connecting to AI DB...")
            conn = sqlite3.connect(str(ai_db))
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            print("[THREADS DETAILS] Step 13: Connected, querying assignments...")
            
            # thread_assignments uses session_id (which matches thread.id or thread.thread_slug)
            for thread_id in thread_ids:
                cursor.execute("""
                    SELECT session_id, location 
                    FROM thread_assignments 
                    WHERE session_id = ?
                    ORDER BY updated_at DESC
                    LIMIT 1
                """, (thread_id,))
                
                row = cursor.fetchone()
                if row:
                    assignments[thread_id] = {
                        'location': row['location'],  # e.g., "alpha-3", "prime"
                        'agent_name': row['location'].upper() if row['location'] else 'No Agent'
                    }
            
            conn.close()
            print(f"[THREADS DETAILS] Step 14: Got {len(assignments)} assignments")
        except Exception as e:
            print(f"[THREADS] Warning: Could not fetch agent assignments: {e}")
            print("[THREADS DETAILS] Step 14b: Assignment lookup failed (non-fatal)")
        
        # Convert to list of dicts
        print("[THREADS DETAILS] Step 15: Building result array...")
        result = []
        for thread in threads:
            # FIXED: execute_sqlite_query returns dicts, not Row objects - use dict keys not array indices
            thread_id = thread['id']
            thread_slug = thread['thread_slug']
            location_from_threads = thread.get('location')  # threads.location column
            
            # Use location from threads table first, then fall back to assignments table
            # The threads.location column is the primary source of truth
            if location_from_threads:
                agent_location = location_from_threads
                agent_display_name = location_from_threads.upper()
            else:
                # Check assignments by both id and slug
                assignment = assignments.get(str(thread_id)) or assignments.get(thread_slug) or {}
                agent_location = assignment.get('location', 'prime')
                agent_display_name = assignment.get('agent_name', 'Prime')
            
            result.append({
                'id': thread_id,
                'thread_slug': thread_slug,
                'name': thread.get('name') or thread_slug or str(thread_id),  # Fallback to slug or id
                'created': thread.get('created_at'),
                'updated': thread.get('updated_at'),
                'synergy_card_id': thread.get('synergy_card_id'),
                'synergy_card_name': None,  # Not stored in threads table, could fetch from synergy_sessions if needed
                'agent_id': agent_location,
                'agent_name': agent_display_name
            })
        
        print(f"[THREADS DETAILS] Step 16: Returning {len(result)} threads")
        return success_response(result)
    
    except DatabaseConnectionError as e:
        print(f"[THREADS ERROR] DatabaseConnectionError: {e}")
        import traceback
        traceback.print_exc()
        return error_response(f"Database error: {str(e)}", 500)
    except Exception as e:
        print(f"[THREADS ERROR] Exception type: {type(e).__name__}")
        print(f"[THREADS ERROR] Exception value: {e}")
        print(f"[THREADS ERROR] Exception str: {str(e)}")
        import traceback
        traceback.print_exc()
        return error_response(f"Thread details error: {str(e)}", 500)


# ============================================================
# MESSAGE SAVING (NEW - FIX FOR THREAD MESSAGE LINKING)
# ============================================================

@thread_bp.route('/messages/save', methods=['POST'])
def save_messages():
    """
    Save messages directly to the messages table
    CRITICAL FIX: Links messages to threads so they show up in thread list
    
    POST /api/threads/messages/save
    {
        "thread_id": "1762593367878",
        "user_id": 14,
        "messages": [
            {"role": "user", "content": "hello", "timestamp": 1699999999},
            {"role": "assistant", "content": "Hi!", "timestamp": 1699999999}
        ]
    }
    
    Returns:
        {"success": true, "thread_id": "...", "messages_saved": 2}
    """
    try:
        from thread_manager import ThreadManager
        
        data = request.get_json() or {}
        thread_id = str(data.get('thread_id'))
        messages = data.get('messages', [])
        user_id = data.get('user_id', 1)
        
        if not thread_id:
            return error_response('thread_id required', 400)
        
        if not messages or not isinstance(messages, list):
            return error_response('messages array required', 400)
        
        print(f"[MESSAGE SAVE] Thread: {thread_id}, User: {user_id}, Messages: {len(messages)}")
        
        # Initialize ThreadManager
        thread_mgr = ThreadManager(get_sessions_database_path())
        
        # APPEND MODE: Only save messages that don't already exist
        # Check existing message count to determine which messages to save
        db_path = get_sessions_database_path()
        
        # Get the internal thread database ID
        query = "SELECT id FROM threads WHERE thread_slug = ?"
        rows = execute_sqlite_query(db_path, query, (thread_id,))
        
        existing_message_count = 0
        if rows and len(rows) > 0:
            internal_thread_id = rows[0]['id']
            
            # Count existing messages for this thread
            count_query = "SELECT COUNT(*) as count FROM messages WHERE thread_id = ?"
            count_result = execute_sqlite_query(db_path, count_query, (internal_thread_id,))
            if count_result and len(count_result) > 0:
                existing_message_count = count_result[0]['count']
                print(f"[MESSAGE SAVE] Thread {thread_id} has {existing_message_count} existing messages")
        
        # Only save NEW messages (skip messages that already exist)
        messages_to_save = messages[existing_message_count:]
        print(f"[MESSAGE SAVE] Appending {len(messages_to_save)} new messages (skipping first {existing_message_count})")
        
        # Save each NEW message
        saved_count = 0
        for msg in messages_to_save:
            role = msg.get('role')
            content = msg.get('content')
            
            if not role or not content:
                print(f"[MESSAGE SAVE] Skipping invalid message: {msg}")
                continue
            
            try:
                # Add message to database
                thread_mgr.add_message(
                    workspace_slug='default',
                    thread_slug=thread_id,
                    role=role,
                    content=content,
                    user_id=user_id,
                    prompt=content if role == 'user' else None,
                    include=True,
                    tool_calls=msg.get('tool_calls'),
                    tokens_used=msg.get('tokens_used'),
                    response_time_ms=msg.get('response_time_ms'),
                    metadata=msg.get('metadata', {})
                )
                saved_count += 1
                print(f"[MESSAGE SAVE] Saved {role} message to thread {thread_id}")
            except Exception as msg_error:
                print(f"[MESSAGE SAVE ERROR] Failed to save message: {msg_error}")
                continue
        
        return success_response({
            'thread_id': thread_id,
            'messages_saved': saved_count
        }, message=f'Saved {saved_count} messages to thread')
    
    except Exception as e:
        print(f"[MESSAGE SAVE ERROR] {str(e)}")
        import traceback
        traceback.print_exc()
        return error_response(f'Failed to save messages: {str(e)}', 500)


@thread_bp.route('/messages/get', methods=['GET'])
def get_messages():
    """
    Get messages for a thread
    
    GET /api/threads/messages/get?thread_id=1762614784052
    
    Returns:
        {"success": true, "messages": [...], "count": 2}
    """
    try:
        thread_id = request.args.get('thread_id')
        if not thread_id:
            return error_response('thread_id required', 400)
        
        db_path = get_sessions_database_path()
        
        # Query messages by thread_slug (which matches thread_id)
        query = """
            SELECT 
                m.id,
                m.role,
                m.content,
                m.tool_calls,
                m.tokens_used,
                m.created_at,
                m.metadata
            FROM messages m
            JOIN threads t ON m.thread_id = t.id
            WHERE t.thread_slug = ?
            ORDER BY m.created_at ASC
        """
        
        rows = execute_sqlite_query(db_path, query, (thread_id,))
        
        messages = []
        for row in rows:
            # Parse metadata JSON if it exists
            metadata = {}
            if row.get('metadata'):
                try:
                    metadata = json.loads(row['metadata'])
                except:
                    metadata = {}
            
            messages.append({
                'id': row['id'],
                'role': row['role'],
                'content': row['content'],
                'tool_calls': json.loads(row['tool_calls']) if row['tool_calls'] else [],
                'tokens_used': row.get('tokens_used'),
                'response_time_ms': None,  # Not stored in DB (log only)
                'timestamp': row['created_at'],
                'metadata': metadata  # Now properly loaded from database
            })
        
        return success_response({
            'messages': messages,
            'count': len(messages)
        }, message=f'Found {len(messages)} messages')
    
    except Exception as e:
        print(f"[MESSAGE GET ERROR] {str(e)}")
        import traceback
        traceback.print_exc()
        return error_response(f'Failed to get messages: {str(e)}', 500)


# ============================================================
# THREAD ASSIGNMENTS (DELETE ENDPOINT)
# ============================================================

@thread_bp.route('/assignments/<location>', methods=['DELETE'])
def delete_assignment(location):
    """
    Delete thread assignment for a specific location
    
    DELETE /api/threads/assignments/{location}
    
    Removes the thread assignment from the specified agent/location.
    Used when cleaning up stale assignments (thread deleted but assignment remains).
    
    Returns:
        {"success": true, "message": "Assignment cleared"}
    """
    try:
        import sqlite3
        from pathlib import Path
        import json
        
        # Clean location (remove extra spaces)
        location = location.strip()
        
        # Get user_id from request (Authorization header or query param)
        user_id = None
        auth_header = request.headers.get('Authorization')
        if auth_header and auth_header.startswith('Bearer '):
            # Extract user_id from JWT token
            try:
                import jwt
                token = auth_header.split(' ')[1]
                payload = jwt.decode(token, options={"verify_signature": False})
                user_id = payload.get('user_id')
            except:
                pass
        
        # Fallback to query param
        if not user_id:
            user_id = request.args.get('user_id', type=int)
        
        # Fallback to default user
        if not user_id:
            user_id = 1
        
        print(f"[DELETE ASSIGNMENT] Clearing assignment for location: {location}, user_id: {user_id}")
        
        # FIXED: Use sessions.db with users.metadata column (same as thread_assignment_routes.py)
        root_dir = Path(__file__).parent.parent.parent
        db_path = root_dir / 'data' / 'sessions.db'
        
        conn = sqlite3.connect(str(db_path))
        cursor = conn.cursor()
        
        # Ensure user row exists
        cursor.execute("SELECT id FROM users WHERE id = ?", (user_id,))
        if not cursor.fetchone():
            cursor.execute("""
                INSERT INTO users (id, username, email, metadata)
                VALUES (?, ?, ?, ?)
            """, (user_id, f'user_{user_id}', f'user_{user_id}@example.com', '{}'))
            print(f'[DELETE ASSIGNMENT] Created user row for user {user_id}')
        
        # Get current metadata
        cursor.execute("SELECT metadata FROM users WHERE id = ?", (user_id,))
        row = cursor.fetchone()
        metadata = json.loads(row[0] or '{}')
        
        # Remove assignment from metadata
        assignments = metadata.get('thread_assignments', {})
        session_id = assignments.pop(location, None)
        
        # Update metadata
        metadata['thread_assignments'] = assignments
        cursor.execute("""
            UPDATE users
            SET metadata = ?
            WHERE id = ?
        """, (json.dumps(metadata), user_id))
        
        conn.commit()
        conn.close()
        
        deleted_count = 1 if session_id else 0
        print(f"[DELETE ASSIGNMENT] Cleared {location} assignment for user {user_id} (session_id: {session_id})")
        
        return success_response(
            {'location': location, 'deleted': deleted_count, 'session_id': session_id},
            message=f'Assignment cleared for {location}'
        )
    
    except Exception as e:
        print(f"[DELETE ASSIGNMENT ERROR] {str(e)}")
        import traceback
        traceback.print_exc()
        return error_response(f'Failed to delete assignment: {str(e)}', 500)



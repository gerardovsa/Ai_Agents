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
                thread_slug, name, user_id, created_at, updated_at,
                metadata, location, tags, synergy_card_id,
                parent_thread_id, branch_point_message_id, branch_name
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """
        
        execute_sqlite_update(
            db_path,
            insert_query,
            (
                thread_id,                      # thread_slug
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
        
        # Query threads from database
        db_path = get_sessions_database_path()
        
        query = """
            SELECT thread_slug, name, user_id, created_at, updated_at, 
                   metadata, location, tags, synergy_card_id, 
                   parent_thread_id, branch_name
            FROM threads
            WHERE user_id = ?
            ORDER BY updated_at DESC
            LIMIT ?
        """
        
        # execute_sqlite_query returns list of dicts directly
        rows = execute_sqlite_query(db_path, query, (user_id, limit))
        
        threads = []
        for row in rows:
            # Rows are returned as dicts from execute_sqlite_query
            thread_data = {
                'id': row['thread_slug'],
                'title': row['name'],
                'user_id': row['user_id'],
                'created': row['created_at'],
                'updated': row['updated_at'],
                'metadata': json.loads(row['metadata']) if row['metadata'] else {},
                'location': row['location'] or 'prime',
                'tags': json.loads(row['tags']) if row['tags'] else [],
                'synergy_card_id': row['synergy_card_id'],
                'parent_thread_id': row['parent_thread_id'],
                'branch_name': row['branch_name']
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
            thread_id = data.get('thread_id')
            title = data.get('title', 'Untitled Thread')
            messages = data.get('messages', [])
            agent = data.get('agent', 'prime')
            user_id = data.get('user_id', 1)
            location = data.get('location', 'prime')
            
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
        
        if not agent_id or not session_id:
            return error_response("Missing agent_id/session_id or thread_id", 400)
        
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
             message_count, context, created_at, saved_at, last_updated,
             tags, synergy_card_id, parent_thread_id, branch_point_message_id, 
             branch_name, summary, summary_generated_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, datetime('now'), datetime('now'), datetime('now'),
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
            datetime.now().isoformat(),
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


@thread_bp.route('/<thread_id>', methods=['DELETE'])
def delete_thread(thread_id):
    """
    Delete saved thread from persistent storage
    
    Also clears from agent_state_manager if active
    """
    try:
        # Parse thread_id (format: "agent_id_session_id")
        parts = thread_id.split('_', 1)
        if len(parts) != 2:
            return error_response("Invalid thread_id format", 400)
        
        agent_id, session_id = parts
        
        # Clear from agent_state_manager if active
        agent_state_manager.clear_conversation(agent_id, session_id)
        
        # Delete from SQLite
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


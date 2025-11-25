"""
Thread Management Routes
Thread/conversation management for all AI agents
"""

from flask import Blueprint, request
import json
from datetime import datetime, timedelta

# Import infrastructure
from core.agent_state_manager import agent_state_manager
from shared.database_utils import (
    get_database_connection, is_using_supabase, convert_sql_placeholders
)
from utils.response_helpers import (
    success_response, error_response, list_response,
    deleted_response, updated_response
)
from utils.database_helpers import DatabaseConnectionError

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
    conn = None  # CRITICAL: Initialize outside try block for finally access
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
        
        # Insert into database - PostgreSQL/Supabase only
        conn = get_database_connection('sessions')
        cursor = conn.cursor()
        
        # PostgreSQL: Exclude id column to let sequence auto-generate
        insert_query = """
            INSERT INTO sessions.threads (
                thread_slug, workspace_id, name, user_id, created_at, updated_at,
                metadata, location, tags, synergy_card_id,
                parent_thread_id, branch_point_message_id, branch_name
            ) VALUES (
                %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s
            )
            RETURNING id
        """
        
        cursor.execute(
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
                json.dumps(tags),               # tags
                synergy_card_id,                # synergy_card_id
                parent_thread_id,               # parent_thread_id
                branch_point_message_id,        # branch_point_message_id
                branch_name                     # branch_name
            )
        )
        
        # Get the auto-generated id
        generated_id_result = cursor.fetchone()
        generated_id = generated_id_result[0] if isinstance(generated_id_result, tuple) else generated_id_result['id']
        conn.commit()
        
        # Don't close connection here - finally block will handle it
        
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
    finally:
        # CRITICAL: Always close connection, even if exception raised
        if conn:
            conn.close()


@thread_bp.route('/upsert', methods=['POST'])
def upsert_thread():
    """
    Create or update thread in sessions.threads table
    UPSERT pattern - creates if doesn't exist, updates if exists
    
    Body params:
        thread_id (str, required): Thread slug/ID from frontend
        user_id (int, required): User ID
        title (str, optional): Thread title
        location (str, optional): Thread location/agent
        tags (list, optional): Thread tags
        synergy_card_id (str, optional): Linked Synergy card
    
    Returns:
        {"success": true, "thread_id": "..."}
    """
    conn = None  # CRITICAL: Initialize outside try block for finally access
    try:
        data = request.get_json() or {}
        thread_id = str(data.get('thread_id'))
        user_id = data.get('user_id')
        title = data.get('title', 'Untitled Thread')
        location = data.get('location', 'prime')
        tags = data.get('tags', [])
        synergy_card_id = data.get('synergy_card_id')
        
        if not thread_id or not user_id:
            return error_response('thread_id and user_id required', 400)
        
        conn = get_database_connection('sessions')
        cursor = conn.cursor()
        
        # UPSERT: Insert or update on conflict
        upsert_query = """
            INSERT INTO sessions.threads (
                thread_slug, workspace_id, name, user_id, created_at, updated_at,
                metadata, location, tags, synergy_card_id
            ) VALUES (
                %s, %s, %s, %s, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP, %s, %s, %s, %s
            )
            ON CONFLICT (thread_slug) DO UPDATE SET
                name = EXCLUDED.name,
                location = EXCLUDED.location,
                tags = EXCLUDED.tags,
                synergy_card_id = EXCLUDED.synergy_card_id,
                updated_at = CURRENT_TIMESTAMP
            RETURNING id
        """
        
        cursor.execute(
            upsert_query,
            (
                thread_id,
                1,  # workspace_id
                title,
                user_id,
                json.dumps({}),  # metadata
                location,
                json.dumps(tags),
                synergy_card_id
            )
        )
        
        result = cursor.fetchone()
        internal_id = result[0] if isinstance(result, tuple) else result['id']
        
        conn.commit()
        conn.close()
        
        print(f"✅ [THREAD UPSERT] Thread {thread_id} (DB ID: {internal_id}) created/updated")
        
        return success_response({
            'thread_id': thread_id,
            'internal_id': internal_id
        }, message='Thread saved successfully')
        
    except Exception as e:
        print(f"❌ [THREAD UPSERT ERROR] {str(e)}")
        import traceback
        traceback.print_exc()
        return error_response(f'Failed to upsert thread: {str(e)}', 500)
    finally:
        # CRITICAL: Always close connection, even if exception raised
        if conn:
            conn.close()


# ============================================================
# THREAD PRIME-LOADED MARKER
# ============================================================

@thread_bp.route('/mark-prime-loaded', methods=['POST'])
def mark_thread_as_prime_loaded():
    """
    Mark a thread as 'prime-loaded' (single thread to load on Prime startup)
    Automatically unmarks any existing prime-loaded thread first
    
    Body params:
        thread_id (str, required): Thread slug to mark as prime-loaded
        user_id (int, required): User ID (security check)
    
    Returns:
        {"success": true, "message": "Thread marked as prime-loaded"}
    """
    try:
        data = request.get_json() or {}
        thread_id = data.get('thread_id')
        user_id = data.get('user_id')
        
        if not thread_id or not user_id:
            return error_response('thread_id and user_id required', 400)
        
        conn = get_database_connection('sessions')
        cursor = conn.cursor()
        
        # Step 1: Unmark all existing prime-loaded threads for this user
        sql, params = convert_sql_placeholders("""
            UPDATE sessions.threads
            SET location = 'prime', updated_at = CURRENT_TIMESTAMP
            WHERE user_id = %s AND location = 'prime-loaded'
        """, (user_id,))

        cursor.execute(sql, params)
        
        unmarked_count = cursor.rowcount
        print(f"🔄 [PRIME-LOADED] Unmarked {unmarked_count} existing prime-loaded threads for user {user_id}")
        
        # Step 2: Mark the new thread as prime-loaded
        sql, params = convert_sql_placeholders("""
            UPDATE sessions.threads
            SET location = 'prime-loaded', updated_at = CURRENT_TIMESTAMP
            WHERE thread_slug = %s AND user_id = %s
            RETURNING id
        """, (thread_id, user_id))

        cursor.execute(sql, params)
        
        result = cursor.fetchone()
        if not result:
            conn.close()
            return error_response(f'Thread {thread_id} not found for user {user_id}', 404)
        
        conn.commit()
        conn.close()
        
        print(f"✅ [PRIME-LOADED] Thread {thread_id} marked as prime-loaded for user {user_id}")
        
        return success_response({
            'thread_id': thread_id,
            'message': 'Thread will load on Prime startup'
        }, message='Thread marked as prime-loaded')
        
    except Exception as e:
        print(f"❌ [PRIME-LOADED ERROR] {str(e)}")
        import traceback
        traceback.print_exc()
        return error_response(f'Failed to mark thread: {str(e)}', 500)


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
    
    Returns list of threads FROM sessions.sessions schema (Supabase) or sessions.db (SQLite)
    """
    conn = None  # CRITICAL: Initialize outside try block for finally access
    try:
        user_id = request.args.get('user_id')
        if not user_id:
            return error_response("user_id is required", 400)
        
        limit = int(request.args.get('limit', 50))
        
        print(f"\n🔍 [THREAD API] /api/threads/list called")
        print(f"📊 [THREAD API] Parameters: user_id={user_id}, limit={limit}")
        print(f"🗄️ [THREAD API] Database: {'Supabase' if is_using_supabase() else 'SQLite'}")
        
        # Get database connection (auto-detects SQLite vs Supabase)
        conn = get_database_connection('sessions')
        cursor = conn.cursor()
        
        # Build query with proper placeholders
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
                t.synergy_card_name,
                t.parent_thread_id, 
                t.branch_name,
                t.workflow_id,
                t.workflow_name,
                t.workflow_slug,
                t.workflow_title,
                t.internal_doc_slug,
                t.internal_doc_title,
                COUNT(m.id) as message_count,
                MAX(m.timestamp) as last_message_time,
                (SELECT role FROM sessions.messages WHERE thread_id = t.id ORDER BY timestamp DESC LIMIT 1) as last_message_role
            FROM sessions.threads t
            LEFT JOIN sessions.messages m ON t.id = m.thread_id
            WHERE t.user_id = %s
            GROUP BY t.id, t.thread_slug, t.name, t.user_id, t.created_at, t.updated_at, 
                     t.metadata, t.location, t.tags, t.synergy_card_id, t.synergy_card_name,
                     t.parent_thread_id, t.branch_name, t.workflow_id, t.workflow_name,
                     t.workflow_slug, t.workflow_title, t.internal_doc_slug, t.internal_doc_title
            ORDER BY t.updated_at DESC
            LIMIT %s
        """
        
        # Convert ? placeholders to %s for PostgreSQL
        query = convert_sql_placeholders(query)
        
        # Execute query
        cursor.execute(query, (user_id, limit))
        rows = cursor.fetchall()
        
        print(f"✅ [THREAD API] Query returned {len(rows)} rows")
        
        # Log location distribution
        location_counts = {}
        for row in rows:
            loc = row['location'] or 'prime'
            location_counts[loc] = location_counts.get(loc, 0) + 1
        print(f"📍 [THREAD API] Location distribution: {location_counts}")
        
        threads = []
        for row in rows:
            # Rows returned as dicts (RealDictCursor for Supabase, Row for SQLite)
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
                'synergy_card_name': row['synergy_card_name'],
                'parent_thread_id': row['parent_thread_id'],
                'branch_name': row['branch_name'],
                'workflow_id': row['workflow_id'],
                'workflow_name': row['workflow_name'],
                'workflow_slug': row['workflow_slug'],
                'workflow_title': row['workflow_title'],
                'internal_doc_slug': row['internal_doc_slug'],
                'internal_doc_title': row['internal_doc_title'],
                'message_count': row['message_count'] or 0,
                'last_message_time': row['last_message_time'],
                'last_message_role': row['last_message_role'],
                'archived': False  # Default for now, add column later if needed
            }
            threads.append(thread_data)
        
        # Don't close connection here - finally block will handle it
        
        print(f"📤 [THREAD API] Returning {len(threads)} threads")
        for thread in threads[:5]:  # Log first 5 threads
            print(f"   🧵 {thread['id']}: '{thread['title']}' → location={thread['location']}")
        if len(threads) > 5:
            print(f"   ... and {len(threads) - 5} more threads")
        
        return success_response({
            'threads': threads,
            'count': len(threads)
        }, message=f"Found {len(threads)} threads for user {user_id}")
    
    except Exception as e:
        return error_response(f"Failed to list threads: {str(e)}", 500)
    finally:
        # CRITICAL: Always close connection, even if exception raised
        if conn:
            conn.close()


@thread_bp.route('/metadata/update', methods=['POST'])
def update_thread_metadata_fields():
    """
    Update thread metadata fields (workflow_slug, workflow_title, internal_doc_slug, internal_doc_title)
    
    Body params:
        thread_slug (str, required): Thread slug to update
        workflow_slug (str, optional): Workflow slug to link
        workflow_title (str, optional): Workflow title
        internal_doc_slug (str, optional): Internal document slug
        internal_doc_title (str, optional): Internal document title
    
    Returns success response
    """
    try:
        data = request.json
        thread_slug = data.get('thread_slug')
        
        if not thread_slug:
            return error_response('thread_slug required', 400)
        
        # Build UPDATE query for metadata fields only
        update_query = """
            UPDATE sessions.threads SET
                workflow_slug = %s,
                workflow_title = %s,
                internal_doc_slug = %s,
                internal_doc_title = %s,
                updated_at = CURRENT_TIMESTAMP
            WHERE thread_slug = %s
        """
        
        conn = get_database_connection('sessions')
        cursor = conn.cursor()
        cursor.execute(
            update_query,
            (
                data.get('workflow_slug'),
                data.get('workflow_title'),
                data.get('internal_doc_slug'),
                data.get('internal_doc_title'),
                thread_slug
            )
        )
        conn.commit()
        conn.close()
        
        return success_response({
            'thread_slug': thread_slug,
            'updated_fields': {
                'workflow_slug': data.get('workflow_slug'),
                'workflow_title': data.get('workflow_title'),
                'internal_doc_slug': data.get('internal_doc_slug'),
                'internal_doc_title': data.get('internal_doc_title')
            }
        }, message='Thread metadata updated successfully')
    
    except Exception as e:
        return error_response(f'Failed to update thread metadata: {str(e)}', 500)


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
        
        # Save to Supabase
        
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
        
        # Use Supabase connection
        conn = get_database_connection('sessions')
        cursor = conn.cursor()
        try:
            cursor.execute(create_table_query)
            conn.commit()
        except Exception as e:
            print(f"⚠️ [Thread Save] Table already exists or creation failed: {e}")
            conn.rollback()
        
        # Insert thread
        thread_id = f"{agent_id}_{session_id}"
        conversation_json = json.dumps(conversation)
        context_json = json.dumps({})  # Empty context for frontend threads
        
        # PostgreSQL: INSERT ... ON CONFLICT (upsert)
        insert_query = """
            INSERT INTO sessions.saved_threads 
            (thread_id, agent_id, session_id, user_id, location, thread_name, conversation, 
             message_count, context, saved_at, last_updated,
             tags, synergy_card_id, parent_thread_id, branch_point_message_id, 
             branch_name, summary, summary_generated_at)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, NOW(), NOW(),
                    %s, %s, %s, %s, %s, %s, %s)
            ON CONFLICT (thread_id) DO UPDATE SET
                thread_name = EXCLUDED.thread_name,
                conversation = EXCLUDED.conversation,
                message_count = EXCLUDED.message_count,
                last_updated = NOW(),
                tags = EXCLUDED.tags,
                synergy_card_id = EXCLUDED.synergy_card_id
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
        
        cursor.execute(insert_query, params)
        conn.commit()
        conn.close()
        
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
            FROM sessions.saved_threads
            WHERE thread_id = %s
        """
        
        conn = get_database_connection('sessions')
        cursor = conn.cursor()
        cursor.execute(query, (thread_id,))
        results = cursor.fetchall()
        conn.close()
        
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
    - UUID format: "sess_abc123" or any UUID (thread_slug)
    - Legacy format: "agent_id_session_id"
    
    Also clears from agent_state_manager if active and deletes related messages
    """
    try:
        print(f"[DELETE THREAD] Attempting to delete thread: {thread_id}")
        
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
        
        # Delete from Supabase (sessions.threads table)
        conn = get_database_connection('sessions')
        cursor = conn.cursor()
        
        # First, get the internal thread ID
        select_query = """
            SELECT id FROM sessions.threads
            WHERE thread_slug = %s
        """
        
        cursor.execute(select_query, [thread_id])
        result = cursor.fetchone()
        
        if not result:
            conn.close()
            print(f"[DELETE THREAD] Thread not found: {thread_id}")
            return error_response(f"Thread {thread_id} not found", 404)
        
        internal_thread_id = result[0] if isinstance(result, tuple) else result['id']
        print(f"[DELETE THREAD] Found thread with internal ID: {internal_thread_id}")
        
        # Delete related messages first (foreign key constraint)
        delete_messages_query = """
            DELETE FROM sessions.messages
            WHERE thread_id = %s
        """
        
        cursor.execute(delete_messages_query, [internal_thread_id])
        messages_deleted = cursor.rowcount
        print(f"[DELETE THREAD] Deleted {messages_deleted} messages")
        
        # Now delete the thread
        delete_thread_query = """
            DELETE FROM sessions.threads
            WHERE id = %s
        """
        
        cursor.execute(delete_thread_query, [internal_thread_id])
        threads_deleted = cursor.rowcount
        
        conn.commit()
        conn.close()
        
        print(f"[DELETE THREAD] Successfully deleted thread {thread_id} (internal ID: {internal_thread_id})")
        
        return deleted_response(
            message=f"Thread deleted successfully ({messages_deleted} messages removed)",
            deleted_count=threads_deleted
        )
    
    except DatabaseConnectionError as e:
        print(f"[DELETE THREAD] Database connection error: {str(e)}")
        return error_response(f"Database connection error: {str(e)}", 500)
    except Exception as e:
        print(f"[DELETE THREAD] Error deleting thread: {str(e)}")
        import traceback
        traceback.print_exc()
        return error_response(f"Failed to delete thread from database: {str(e)}", 500)


@thread_bp.route('/<thread_id>/update', methods=['PATCH'])
def update_thread_metadata(thread_id):
    """
    Update thread metadata (title, tags, synergy_card_id, workflow_id, etc.)
    
    Request JSON:
    {
        "name": "New Thread Title" (optional),
        "tags": ["tag1", "tag2"] (optional),
        "synergy_card_id": "sess_xxx" (optional),
        "synergy_card_name": "Session Name" (optional),
        "workflow_id": "workflow_123" (optional),
        "workflow_name": "Workflow Name" (optional),
        "location": "prime" (optional)
    }
    """
    try:
        data = request.json
        if not data:
            return error_response("No data provided", 400)
        
        # Build dynamic UPDATE query for PostgreSQL
        update_fields = []
        params = []
        param_counter = 1
        
        if 'name' in data:
            update_fields.append(f"name = %s")
            params.append(data['name'])
            param_counter += 1
        
        if 'tags' in data:
            update_fields.append(f"tags = %s")
            params.append(json.dumps(data['tags']))
            param_counter += 1
        
        if 'synergy_card_id' in data:
            update_fields.append(f"synergy_card_id = %s")
            params.append(data['synergy_card_id'])
            param_counter += 1
        
        if 'synergy_card_name' in data:
            update_fields.append(f"synergy_card_name = %s")
            params.append(data['synergy_card_name'])
            param_counter += 1
        
        if 'workflow_id' in data:
            update_fields.append(f"workflow_id = %s")
            params.append(data['workflow_id'])
            param_counter += 1
        
        if 'workflow_name' in data:
            update_fields.append(f"workflow_name = %s")
            params.append(data['workflow_name'])
            param_counter += 1
        
        if 'location' in data:
            update_fields.append(f"location = %s")
            params.append(data['location'])
            param_counter += 1
        
        if not update_fields:
            return error_response("No valid fields to update", 400)
        
        # Add updated_at timestamp (PostgreSQL syntax)
        update_fields.append("updated_at = NOW()")
        
        # Add thread_id to params for WHERE clause
        params.append(thread_id)
        
        # Execute UPDATE using Supabase connection
        conn = get_database_connection('sessions')
        cursor = conn.cursor()
        
        update_query = f"""
            UPDATE sessions.threads
            SET {', '.join(update_fields)}
            WHERE thread_slug = %s
        """
        
        cursor.execute(update_query, params)
        rowcount = cursor.rowcount
        conn.commit()
        conn.close()
        
        if rowcount == 0:
            return error_response(f"Thread {thread_id} not found", 404)
        
        return success_response({
            'thread_id': thread_id,
            'updated_fields': list(data.keys())
        }, message="Thread updated successfully")
    
    except Exception as e:
        import traceback
        print(f"❌ [UPDATE THREAD] Error: {e}")
        print(traceback.format_exc())
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
            count_query = """
                SELECT COUNT(*) as count
                FROM sessions.saved_threads
            """
            
            conn = get_database_connection('sessions')
            cursor = conn.cursor()
            cursor.execute(count_query)
            results = cursor.fetchall()
            conn.close()
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
            # Save to Supabase
            
            # Ensure table exists (PostgreSQL)
            conn = get_database_connection('sessions')
            cursor = conn.cursor()
            
            create_table_query = """
                CREATE TABLE IF NOT EXISTS sessions.saved_threads (
                    thread_id TEXT PRIMARY KEY,
                    agent_id TEXT NOT NULL,
                    session_id TEXT NOT NULL,
                    thread_name TEXT,
                    conversation TEXT NOT NULL,
                    message_count INTEGER,
                    context TEXT,
                    created_at TIMESTAMP,
                    saved_at TIMESTAMP DEFAULT NOW()
                )
            """
            try:
                cursor.execute(create_table_query)
                conn.commit()
            except Exception as e:
                conn.rollback()
                print(f"⚠️ [Autosave] Table exists: {e}")
            
            # Save thread
            thread_id = f"{agent_id}_{session_id}"
            conversation_json = json.dumps(state['conversation'])
            context_json = json.dumps(state.get('context', {}))
            
            insert_query = """
                INSERT INTO sessions.saved_threads 
                (thread_id, agent_id, session_id, thread_name, conversation, 
                 message_count, context, created_at, saved_at)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, NOW())
                ON CONFLICT (thread_id) DO UPDATE SET
                    conversation = EXCLUDED.conversation,
                    message_count = EXCLUDED.message_count,
                    saved_at = NOW()
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
            
            cursor.execute(insert_query, params)
            conn.commit()
            conn.close()
            
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
        # PostgreSQL connection
        conn = get_database_connection('sessions')
        cursor = conn.cursor()
        
        # Ensure table has last_read column
        alter_query = """
            ALTER TABLE sessions.saved_threads
            ADD COLUMN IF NOT EXISTS last_read TIMESTAMP
        """
        
        try:
            cursor.execute(alter_query)
            conn.commit()
        except Exception as e:
            conn.rollback()
            # Column might already exist
            pass
        
        # Update last_read
        update_query = """
            UPDATE sessions.saved_threads
            SET last_read = NOW()
            WHERE thread_id = %s
        """
        
        cursor.execute(update_query, [thread_id])
        rowcount = cursor.rowcount
        conn.commit()
        conn.close()
        
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
    Fetches thread details FROM sessions.threads table and agent assignments FROM sessions.threads.location column
    
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
        placeholders = ','.join(['%s' for _ in thread_ids])
        print(f"[THREADS DETAILS] Step 5: Placeholders: {placeholders}")
        
        # Query threads FROM sessions.sessions database (includes location column for agent assignments)
        print("[THREADS DETAILS] Step 6: Getting database connection...")
        # Note: threads.location is the primary source of truth for agent assignments
        # See: THREAD_LOCATION_ARCHITECTURE.md
        conn = get_database_connection('sessions')
        print(f"[THREADS DETAILS] Step 7: Connected to database")
        
        # Build query with placeholder conversion for PostgreSQL
        # IMPORTANT: Only match against thread_slug (TEXT column)
        # The id column is an INTEGER auto-increment in Supabase
        # Thread identifiers like '1762851232975' are stored in thread_slug
        query = f"""
            SELECT 
                t.id,
                t.thread_slug,
                t.name,
                t.created_at,
                t.updated_at,
                t.synergy_card_id,
                t.location
            FROM sessions.threads t
            WHERE t.thread_slug IN ({placeholders})
            ORDER BY t.updated_at DESC
        """
        
        # Convert SQL placeholders for PostgreSQL compatibility
        query = convert_sql_placeholders(query)
        
        # Only match against thread_slug (not id)
        params = thread_ids
        print(f"[THREADS DETAILS] Step 8: Executing query with {len(params)} params...")
        
        cursor = conn.cursor()
        cursor.execute(query, params)
        threads_raw = cursor.fetchall()
        
        # Convert to list of dicts
        threads = []
        for row in threads_raw:
            threads.append({
                'id': row['id'],
                'thread_slug': row['thread_slug'],
                'name': row['name'],
                'created_at': row['created_at'],
                'updated_at': row['updated_at'],
                'synergy_card_id': row['synergy_card_id'],
                'location': row['location']
            })
        
        cursor.close()
        conn.close()
        
        print(f"[THREADS DETAILS] Step 9: Got {len(threads)} threads")
        
        # Populate agent assignments FROM sessions.threads.location (primary source)
        print("[THREADS DETAILS] Step 10: Populating assignments FROM sessions.threads.location...")
        assignments = {}
        try:
            for t in threads:
                loc = t.get('location')
                if loc:
                    # Map by both id (string) and thread_slug for lookups later
                    assignments[str(t.get('id'))] = {
                        'location': loc,
                        'agent_name': loc.upper()
                    }
                    thread_slug = t.get('thread_slug')
                    if thread_slug:
                        assignments[thread_slug] = {
                            'location': loc,
                            'agent_name': loc.upper()
                        }
            print(f"[THREADS DETAILS] Step 14: Got {len(assignments)} assignments FROM sessions.threads.location")
        except Exception as e:
            # Extremely unlikely, but keep logging safe fallback
            print(f"[THREADS] Warning: Failed to populate assignments FROM sessions.threads.location: {e}")
            assignments = {}
        
        # Convert to list of dicts
        print("[THREADS DETAILS] Step 15: Building result array...")
        result = []
        for thread in threads:
            # FIXED: execute_sqlite_query returns dicts, not Row objects - use dict keys not array indices
            thread_id = thread['id']
            thread_slug = thread['thread_slug']
            location_from_threads = thread.get('location')  # threads.location column
            
            # Use location FROM sessions.threads table first, then fall back to assignments table
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
                'synergy_card_name': None,  # Not stored in threads table, could fetch FROM synergy_sessions.synergy_sessions if needed
                'agent_id': agent_location,
                'agent_name': agent_display_name
            })
        
        print(f"[THREADS DETAILS] Step 16: Returning {len(result)} threads")
        return success_response(result)
    
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
    conn = None
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
        
        # Get database connection ONCE and reuse
        conn = get_database_connection('sessions')
        cursor = conn.cursor()
        
        # Get the internal thread database ID and count in ONE query
        query = """
            SELECT t.id, COUNT(m.id) as message_count
            FROM sessions.threads t
            LEFT JOIN sessions.messages m ON m.thread_id = t.id
            WHERE t.thread_slug = %s
            GROUP BY t.id
        """
        cursor.execute(query, (thread_id,))
        result = cursor.fetchone()
        
        if not result:
            cursor.close()
            conn.close()
            return error_response(f'Thread {thread_id} not found', 404)
        
        internal_thread_id = result['id']
        existing_message_count = result['message_count'] or 0
        print(f"[MESSAGE SAVE] Thread {thread_id} (DB ID: {internal_thread_id}) has {existing_message_count} existing messages")
        
        # Only save NEW messages (skip messages that already exist)
        messages_to_save = messages[existing_message_count:]
        print(f"[MESSAGE SAVE] Appending {len(messages_to_save)} new messages (skipping first {existing_message_count})")
        
        # Batch insert messages directly (MUCH faster than ThreadManager loop)
        saved_count = 0
        insert_query = """
            INSERT INTO sessions.messages (thread_id, role, content, created_at)
            VALUES (%s, %s, %s, CURRENT_TIMESTAMP)
        """
        
        for msg in messages_to_save:
            role = msg.get('role')
            content = msg.get('content')
            
            if not role or not content:
                print(f"[MESSAGE SAVE] Skipping invalid message: {msg}")
                continue
            
            # CRITICAL FIX (Nov 21, 2025): Skip empty/whitespace-only messages
            # Check if message has real content (not just whitespace)
            has_real_content = False
            if isinstance(content, str):
                has_real_content = content.strip() != ''
            elif isinstance(content, list):
                for block in content:
                    if isinstance(block, dict):
                        if block.get('type') == 'text':
                            text_content = block.get('text', '').strip()
                            if text_content:
                                has_real_content = True
                                break
                        elif block.get('type') in ('thinking', 'tool_use', 'tool_result', 'image'):
                            has_real_content = True
                            break
            
            if not has_real_content:
                print(f"[MESSAGE SAVE] Skipping empty/whitespace-only message: {role}")
                continue
            
            try:
                # Serialize content to JSON if it's a dict/list (Anthropic format)
                content_str = json.dumps(content) if isinstance(content, (dict, list)) else content
                cursor.execute(insert_query, (internal_thread_id, role, content_str))
                saved_count += 1
            except Exception as msg_error:
                print(f"[MESSAGE SAVE ERROR] Failed to save message: {msg_error}")
                continue
        
        # Commit all inserts at once
        conn.commit()
        cursor.close()
        conn.close()
        
        print(f"[MESSAGE SAVE] Successfully saved {saved_count} messages to thread {thread_id}")
        
        return success_response({
            'thread_id': thread_id,
            'messages_saved': saved_count
        }, message=f'Saved {saved_count} messages to thread')
    
    except Exception as e:
        print(f"[MESSAGE SAVE ERROR] {str(e)}")
        import traceback
        traceback.print_exc()
        
        # Ensure connection is closed on error
        if conn:
            try:
                conn.rollback()
                conn.close()
            except:
                pass
        
        return error_response(f'Failed to save messages: {str(e)}', 500)


@thread_bp.route('/messages/get', methods=['GET'])
def get_messages():
    """
    Get messages for a thread (with optional pagination)
    
    GET /api/threads/messages/get?thread_id=1762614784052
    GET /api/threads/messages/get?thread_id=1762614784052&limit=5&offset=0
    
    Query params:
        thread_id (required): Thread slug/ID
        limit (optional): Max messages to return (default: all messages)
        offset (optional): Number of messages to skip (default: 0)
    
    Returns:
        {"success": true, "messages": [...], "count": 2, "total": 37}
    """
    conn = None  # CRITICAL: Initialize outside try block for finally access
    try:
        thread_id = request.args.get('thread_id')
        if not thread_id:
            return error_response('thread_id required', 400)
        
        # Get pagination params
        limit = request.args.get('limit', type=int)
        offset = request.args.get('offset', default=0, type=int)
        
        # First, get total message count for this thread
        count_query = """
            SELECT COUNT(m.id) as total
            FROM sessions.messages m
            JOIN sessions.threads t ON m.thread_id = t.id
            WHERE t.thread_slug = %s
        """
        
        # Query messages by thread_slug (with optional pagination)
        if limit:
            # Paginated query - get MOST RECENT messages first, then reverse
            query = """
                SELECT 
                    m.id,
                    m.role,
                    m.content,
                    m.tool_calls,
                    m.tokens_used,
                    m.created_at,
                    m.metadata
                FROM sessions.messages m
                JOIN sessions.threads t ON m.thread_id = t.id
                WHERE t.thread_slug = %s
                ORDER BY m.created_at DESC
                LIMIT %s OFFSET %s
            """
        else:
            # No pagination - get all messages in chronological order
            query = """
                SELECT 
                    m.id,
                    m.role,
                    m.content,
                    m.tool_calls,
                    m.tokens_used,
                    m.created_at,
                    m.metadata
                FROM sessions.messages m
                JOIN sessions.threads t ON m.thread_id = t.id
                WHERE t.thread_slug = %s
                ORDER BY m.created_at ASC
            """
        
        conn = get_database_connection('sessions')
        cursor = conn.cursor()
        
        # Get total count
        cursor.execute(count_query, (thread_id,))
        total_count = cursor.fetchone()['total']
        
        # Get messages
        if limit:
            cursor.execute(query, (thread_id, limit, offset))
        else:
            cursor.execute(query, (thread_id,))
        
        rows = cursor.fetchall()
        
        # Don't close connection here - finally block will handle it
        
        messages = []
        for row in rows:
            # Parse metadata JSON if it exists
            metadata = {}
            if row.get('metadata'):
                try:
                    metadata = json.loads(row['metadata'])
                except:
                    metadata = {}
            
            # Parse content JSON if it's a JSON string (Anthropic format)
            content = row['content']
            try:
                # Try to parse as JSON (multi-block Anthropic format)
                content = json.loads(content)
            except:
                # If parsing fails, keep as string (simple text message)
                pass
            
            messages.append({
                'id': row['id'],
                'role': row['role'],
                'content': content,
                'tool_calls': json.loads(row['tool_calls']) if row['tool_calls'] else [],
                'tokens_used': row.get('tokens_used'),
                'response_time_ms': None,  # Not stored in DB (log only)
                'timestamp': row['created_at'],
                'metadata': metadata  # Now properly loaded from database
            })
        
        # If paginated, reverse messages to get chronological order
        if limit:
            messages.reverse()
        
        pagination_info = f' (page: {offset // limit + 1}, showing {offset + 1}-{offset + len(messages)} of {total_count})' if limit else ''
        
        return success_response({
            'messages': messages,
            'count': len(messages),
            'total': total_count,
            'offset': offset,
            'limit': limit,
            'has_more': (offset + len(messages)) < total_count if limit else False
        }, message=f'Found {len(messages)} messages{pagination_info}')
    
    except Exception as e:
        print(f"[MESSAGE GET ERROR] {str(e)}")
        import traceback
        traceback.print_exc()
        return error_response(f'Failed to get messages: {str(e)}', 500)
    finally:
        # CRITICAL: Always close connection, even if exception raised
        if conn:
            conn.close()


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
        from shared.database_utils import get_database_connection
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
        conn = get_database_connection('sessions')
        cursor = conn.cursor()
        
        # Ensure user row exists
        cursor.execute("SELECT id FROM ai_infrastructure.users WHERE id = %s", (user_id,))
        if not cursor.fetchone():
            sql, params = convert_sql_placeholders("""
                INSERT INTO ai_infrastructure.users (id, username, email, metadata)
                VALUES (%s, %s, %s, %s)
            """, (user_id, f'user_{user_id}', f'user_{user_id}@example.com', '{}'))

            cursor.execute(sql, params)
            print(f'[DELETE ASSIGNMENT] Created user row for user {user_id}')
        
        # Get current metadata
        cursor.execute("SELECT metadata FROM ai_infrastructure.users WHERE id = %s", (user_id,))
        row = cursor.fetchone()
        metadata = json.loads(row[0] or '{}')
        
        # Remove assignment from metadata
        assignments = metadata.get('thread_assignments', {})
        session_id = assignments.pop(location, None)
        
        # Update metadata
        metadata['thread_assignments'] = assignments
        cursor.execute("""
            UPDATE ai_infrastructure.users
            SET metadata = %s
            WHERE id = %s
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


# ============================================================
# DEVICE LOCK/UNLOCK (Multi-Device Locking Feature)
# ============================================================

@thread_bp.route('/<thread_id>/lock', methods=['POST'])
def lock_thread(thread_id):
    """
    Lock a thread to a specific device
    
    Body:
        device_id (str, required): Unique device identifier
        device_name (str, required): Human-readable device name
    
    Returns:
        {
            "success": true,
            "locked_by_device": "device_123",
            "locked_by_device_name": "Chrome Browser",
            "locked_at": "2025-11-14T10:30:00"
        }
    """
    try:
        data = request.get_json()
        device_id = data.get('device_id')
        device_name = data.get('device_name')
        
        if not device_id or not device_name:
            return error_response('device_id and device_name required', 400)
        
        # Update thread with lock info
        locked_at = datetime.now().isoformat()
        
        conn = get_database_connection('sessions')
        cursor = conn.cursor()
        
        query = """
            UPDATE sessions.threads 
            SET locked_by_device = %s,
                locked_by_device_name = %s,
                locked_at = %s
            WHERE id = %s
        """
        
        cursor.execute(query, (device_id, device_name, locked_at, thread_id))
        rowcount = cursor.rowcount
        conn.commit()
        conn.close()
        
        if rowcount == 0:
            return error_response('Thread not found', 404)
        
        print(f"[DEVICE LOCK] Thread {thread_id} locked to device {device_name} ({device_id})")
        
        return success_response({
            'thread_id': thread_id,
            'locked_by_device': device_id,
            'locked_by_device_name': device_name,
            'locked_at': locked_at
        }, message=f'Thread locked to {device_name}')
    
    except Exception as e:
        print(f"[DEVICE LOCK ERROR] {str(e)}")
        import traceback
        traceback.print_exc()
        return error_response(f'Failed to lock thread: {str(e)}', 500)


@thread_bp.route('/<thread_id>/unlock', methods=['POST'])
def unlock_thread(thread_id):
    """
    Unlock a thread (remove device lock)
    
    Returns:
        {
            "success": true,
            "message": "Thread unlocked successfully"
        }
    """
    try:
        # Clear lock fields (PostgreSQL)
        conn = get_database_connection('sessions')
        cursor = conn.cursor()
        
        query = """
            UPDATE sessions.threads 
            SET locked_by_device = NULL,
                locked_by_device_name = NULL,
                locked_at = NULL
            WHERE id = %s
        """
        
        cursor.execute(query, (thread_id,))
        rowcount = cursor.rowcount
        conn.commit()
        conn.close()
        
        if rowcount == 0:
            return error_response('Thread not found', 404)
        
        print(f"[DEVICE LOCK] Thread {thread_id} unlocked")
        
        return success_response({
            'thread_id': thread_id
        }, message='Thread unlocked successfully')
    
    except Exception as e:
        print(f"[DEVICE UNLOCK ERROR] {str(e)}")
        import traceback
        traceback.print_exc()
        return error_response(f'Failed to unlock thread: {str(e)}', 500)


@thread_bp.route('/<thread_id>/lock-status', methods=['GET'])
def get_lock_status(thread_id):
    """
    Get current lock status of a thread
    
    Returns:
        {
            "success": true,
            "locked": true,
            "locked_by_device": "device_123",
            "locked_by_device_name": "Chrome Browser",
            "locked_at": "2025-11-14T10:30:00"
        }
    """
    try:
        query = """
            SELECT locked_by_device, locked_by_device_name, locked_at
            FROM sessions.threads
            WHERE id = %s
        """
        
        conn = get_database_connection('sessions')
        cursor = conn.cursor()
        cursor.execute(query, (thread_id,))
        results = cursor.fetchall()
        conn.close()
        
        if not results:
            return error_response('Thread not found', 404)
        
        row = results[0]
        locked = bool(row.get('locked_by_device'))
        
        return success_response({
            'thread_id': thread_id,
            'locked': locked,
            'locked_by_device': row.get('locked_by_device'),
            'locked_by_device_name': row.get('locked_by_device_name'),
            'locked_at': row.get('locked_at')
        })
    
    except Exception as e:
        print(f"[DEVICE LOCK STATUS ERROR] {str(e)}")
        return error_response(f'Failed to get lock status: {str(e)}', 500)



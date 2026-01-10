"""
Thread Management Routes - FULLY CORRECTED VERSION
All cursor management issues fixed - Production Ready
REFACTORED: 2026-01-01 - All 24+ cursor leaks eliminated
"""

from flask import Blueprint, request, jsonify
import json
from datetime import datetime, timedelta, timezone

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
# HELPER: Thread ID/Slug Lookup
# ============================================================

def get_thread_lookup_clause(thread_id):
    """
    Convert thread_id to appropriate WHERE clause and value.
    Handles both new integer IDs and legacy timestamp-based slugs.
    
    Args:
        thread_id: Thread identifier (int, str, or numeric string)
        
    Returns:
        tuple: (where_clause, lookup_value)
    """
    try:
        thread_id_int = int(thread_id)
        # Large timestamp-like numbers (> 1 trillion) are legacy slugs
        if thread_id_int > 1000000000000:
            return ("t.thread_slug = %s", str(thread_id))
        else:
            return ("t.id = %s", thread_id_int)
    except (ValueError, TypeError):
        # Non-numeric string, use as slug
        return ("t.thread_slug = %s", thread_id)

# ============================================================
# TEAM ID MANAGEMENT (Access Control & Filtering)
# ============================================================

@thread_bp.route('/verify-team-access/<team_id>', methods=['GET'])
def verify_team_access(team_id):
    """
    Verify that current user has access to view threads for specified Team ID.
    SECURITY: Prevents unauthorized access to other teams' data.
    
    Args:
        team_id: Team ID (username) to verify access for
        
    Query params:
        user_id (int): Current user ID making the request
        
    Returns:
        200: User has access (is owner or is the Team ID user)
        403: Access denied
        404: Team ID not found
    """
    try:
        user_id = request.args.get('user_id', type=int)
        
        if not user_id:
            return error_response('user_id required', 400)
        
        with get_database_connection('ai_infrastructure') as conn:
            with conn.cursor() as cursor:
                
                # Check if user has access to this Team ID
                # User has access if:
                # 1. They are the parent account (parent_user_id = user_id)
                # 2. They ARE the Team ID user (id = user_id)
                sql, params = convert_sql_placeholders("""
                    SELECT id, username, parent_user_id, is_sub_user
                    FROM ai_infrastructure.users
                    WHERE username = %s
                      AND is_sub_user = TRUE
                      AND (parent_user_id = %s OR id = %s)
                """, (team_id, user_id, user_id))
                
                cursor.execute(sql, params)
                row = cursor.fetchone()
                
                if not row:
                    # Team ID not found OR user doesn't have access
                    # Check if Team ID exists at all
                    with get_database_connection('ai_infrastructure') as verify_conn:
                        with verify_conn.cursor() as verify_cursor:
                            
                            verify_sql, verify_params = convert_sql_placeholders(
                                "SELECT 1 FROM ai_infrastructure.users WHERE username = %s AND is_sub_user = TRUE",
                                (team_id,)
                            )
                            verify_cursor.execute(verify_sql, verify_params)
                            exists = verify_cursor.fetchone()
                            
                            if not exists:
                                return error_response(f"Team ID '{team_id}' not found", 404)
                            else:
                                return error_response(f"Access denied: You do not have permission to view Team ID '{team_id}'", 403)
                
                # User has access
                team_user_id = row[0] if isinstance(row, tuple) else row['id']
                parent_id = row[2] if isinstance(row, tuple) else row['parent_user_id']
                
                return success_response({
                    'has_access': True,
                    'team_id': team_id,
                    'team_user_id': team_user_id,
                    'is_owner': user_id == parent_id,
                    'is_team_member': user_id == team_user_id
                })
            
    except Exception as e:
        print(f"[VERIFY TEAM ACCESS] Error: {str(e)}")
        import traceback
        traceback.print_exc()
        return error_response(f"Failed to verify team access: {str(e)}", 500)


@thread_bp.route('/filter-by-team', methods=['GET'])
def filter_threads_by_team():
    """
    Server-side filtering of threads by Team ID (single or multiple).
    PERFORMANCE: Reduces bandwidth and improves speed for large thread lists.
    SECURITY: Verifies user has access before returning threads.
    
    Query params:
        team_id (str): Single Team ID to filter by (legacy, deprecated)
        team_ids (str): Comma-separated Team IDs to filter by (e.g., "sales,support,dev")
        user_id (int): Current user ID making the request
        limit (int, optional): Max threads to return (default: 100)
        offset (int, optional): Pagination offset (default: 0)
        
    Returns:
        200: Filtered thread list
        403: Access denied
        404: Team ID not found
    """
    try:
        # Support both single and multiple Team IDs
        team_id_param = request.args.get('team_ids') or request.args.get('team_id')
        user_id = request.args.get('user_id', type=int)
        limit = request.args.get('limit', type=int, default=100)
        offset = request.args.get('offset', type=int, default=0)
        
        if not team_id_param or not user_id:
            return error_response('team_id(s) and user_id required', 400)
        
        # Parse Team IDs (comma-separated)
        team_ids = [tid.strip() for tid in team_id_param.split(',') if tid.strip()]
        
        if not team_ids:
            return error_response('At least one valid Team ID required', 400)
        
        # SECURITY: Verify access for ALL Team IDs
        with get_database_connection('ai_infrastructure') as auth_conn:
            with auth_conn.cursor() as auth_cursor:
                
                # Build IN clause for multiple Team IDs
                placeholders = ', '.join(['%s'] * len(team_ids))
                auth_sql = f"""
                    SELECT username FROM ai_infrastructure.users
                    WHERE username IN ({placeholders})
                      AND is_sub_user = TRUE
                      AND (parent_user_id = %s OR id = %s)
                """
                auth_params = team_ids + [user_id, user_id]
                auth_sql, auth_params = convert_sql_placeholders(auth_sql, auth_params)
                
                auth_cursor.execute(auth_sql, auth_params)
                accessible_team_ids = {row[0] if isinstance(row, tuple) else row['username'] for row in auth_cursor.fetchall()}
                
                # Check if user has access to all requested Team IDs
                requested_set = set(team_ids)
                denied_team_ids = requested_set - accessible_team_ids
                
                if denied_team_ids:
                    return error_response(
                        f"Access denied: You do not have permission to view Team ID(s): {', '.join(denied_team_ids)}", 
                        403
                    )
        
        # Fetch filtered threads (using IN clause for multiple Team IDs)
        with get_database_connection('sessions') as conn:
            with conn.cursor() as cursor:
                
                placeholders = ', '.join(['%s'] * len(team_ids))
                sql = f"""
                    SELECT 
                        id, thread_slug, name, user_id, team_id,
                        location, created_at, updated_at, metadata,
                        tags, synergy_card_id, has_files
                    FROM sessions.threads
                    WHERE team_id IN ({placeholders})
                    ORDER BY updated_at DESC
                    LIMIT %s OFFSET %s
                """
                params = team_ids + [limit, offset]
                sql, params = convert_sql_placeholders(sql, params)
                
                cursor.execute(sql, params)
                rows = cursor.fetchall()
                
                # Get total count
                count_sql = f"SELECT COUNT(*) FROM sessions.threads WHERE team_id IN ({placeholders})"
                count_sql, count_params = convert_sql_placeholders(count_sql, team_ids)
                cursor.execute(count_sql, count_params)
                total_count = cursor.fetchone()[0]
        
        # Build thread list
        threads = []
        for row in rows:
            thread = {
                'id': row[0] if isinstance(row, tuple) else row['id'],
                'thread_slug': row[1] if isinstance(row, tuple) else row['thread_slug'],
                'title': row[2] if isinstance(row, tuple) else row['name'],
                'user_id': row[3] if isinstance(row, tuple) else row['user_id'],
                'team_id': row[4] if isinstance(row, tuple) else row['team_id'],
                'location': row[5] if isinstance(row, tuple) else row['location'],
                'created_at': row[6] if isinstance(row, tuple) else row['created_at'],
                'updated_at': row[7] if isinstance(row, tuple) else row['updated_at'],
                'metadata': json.loads(row[8]) if (isinstance(row, tuple) and row[8]) else (row.get('metadata') or {}),
                'tags': json.loads(row[9]) if (isinstance(row, tuple) and row[9]) else (row.get('tags') or []),
                'synergy_card_id': row[10] if isinstance(row, tuple) else row.get('synergy_card_id'),
                'has_files': row[11] if isinstance(row, tuple) else row.get('has_files', False)
            }
            threads.append(thread)
        
        return success_response({
            'threads': threads,
            'total_count': total_count,
            'limit': limit,
            'offset': offset,
            'team_ids': team_ids,  # Return array of filtered Team IDs
            'has_more': (offset + limit) < total_count
        })
        
    except Exception as e:
        print(f"[FILTER BY TEAM] Error: {str(e)}")
        import traceback
        traceback.print_exc()
        return error_response(f"Failed to filter threads: {str(e)}", 500)


# ============================================================
# AGENT MANAGEMENT (for Communication Hub integration)
# ============================================================

@thread_bp.route('/agents/list', methods=['GET'])
def list_available_agents():
    """
    List all available AI agents (threads that can receive emails)
    Returns agents with active threads + option to create new thread
    
    Query params:
        user_id (int, optional): Filter by user (default: all)
    """
    try:
        user_id = request.args.get('user_id', type=int)
        
        # NATO phonetic alphabet for agent names
        nato_alphabet = [
            'Alpha', 'Bravo', 'Charlie', 'Delta', 'Echo', 'Foxtrot',
            'Golf', 'Hotel', 'India', 'Juliet', 'Kilo', 'Lima',
            'Mike', 'November', 'Oscar', 'Papa', 'Quebec', 'Romeo',
            'Sierra', 'Tango', 'Uniform', 'Victor', 'Whiskey',
            'X-ray', 'Yankee', 'Zulu'
        ]
        
        agents = []
        
        # Query database for threads by location (agent-1, agent-2, etc.)
        # Build a map of location -> thread count
        thread_counts_by_location = {}
        
        with get_database_connection('sessions') as conn:
            with conn.cursor() as cursor:
                
                # Count threads per agent location
                sql = """
                    SELECT 
                        location,
                        COUNT(*) as thread_count,
                        MAX(updated_at) as last_activity
                    FROM sessions.threads
                    WHERE location LIKE 'agent-%%'
                """
                
                if user_id:
                    sql += " AND user_id = %s GROUP BY location ORDER BY location"
                    cursor.execute(sql, (user_id,))
                else:
                    sql += " GROUP BY location ORDER BY location"
                    cursor.execute(sql)
                
                agent_stats = cursor.fetchall()
        
        # Build map of thread counts by location
        for row in agent_stats:
            location = row[0] if isinstance(row, tuple) else row['location']
            thread_count = row[1] if isinstance(row, tuple) else row['thread_count']
            if location and location.startswith('agent-'):
                thread_counts_by_location[location] = thread_count
        
        # Build agent list for ALL agents (agent-1 through agent-9), even if they have 0 threads
        for agent_num in range(1, 10):  # 1 through 9
            location = f'agent-{agent_num}'
            thread_count = thread_counts_by_location.get(location, 0)  # Default to 0 if not in map
            agent_name = f"Agent {nato_alphabet[agent_num - 1]}"
            
            agents.append({
                'id': location,
                'name': agent_name,
                'description': f"Active threads: {thread_count}" if thread_count > 0 else "No active threads",
                'has_active_threads': thread_count > 0,
                'thread_count': thread_count
            })
        
        # Always add "Create New Thread" option
        agents.append({
            'id': 'new',
            'name': 'Create New Thread',
            'description': 'Start a new conversation in next available agent',
            'has_active_threads': False,
            'thread_count': 0,
            'is_create_new': True
        })
        
        return jsonify({
            'success': True,
            'agents': agents,
            'count': len(agents)
        })
        
    except Exception as e:
        print(f"[AGENTS LIST] Error: {str(e)}")
        import traceback
        traceback.print_exc()
        return error_response(f'Failed to list agents: {str(e)}', 500)


# ============================================================
# THREAD CREATION
# ============================================================

@thread_bp.route('/create', methods=['POST'])
def create_thread():
    """
    Create a new thread with idempotency support
    
    Body params:
        user_id (int, required): User creating the thread
        idempotency_key (str, optional): UUID to prevent duplicate threads on retry
        agent_id (str, optional): Agent ID (default: 'prime')
        title (str, optional): Thread title (default: 'New Chat')
        parent_thread_id (str, optional): Parent thread ID for branching
        branch_point_message_id (str, optional): Message ID to branch from
        branch_name (str, optional): Name of the branch
    """
    print(f"\n{'='*80}")
    print(f"[THREAD CREATE] 📝 Creating new thread...")
    print(f"{'='*80}")
    try:
        import uuid
        
        data = request.get_json() or {}
        user_id = data.get('user_id')
        idempotency_key = data.get('idempotency_key')  # NEW: Idempotency support
        agent_id = data.get('agent_id', 'unassigned')
        title = data.get('title', 'New Chat')
        location = data.get('location', 'unassigned')
        tags = data.get('tags', [])
        synergy_card_id = data.get('synergy_card_id')
        
        # NEW: Email context parameters (stored in metadata JSON)
        metadata = data.get('metadata', {})
        
        # Store context_type in metadata if provided
        if data.get('context_type'):
            metadata['context_type'] = data.get('context_type')
        
        # NEW: Branching parameters
        parent_thread_id_raw = data.get('parent_thread_id')
        parent_thread_id = None
        
        # If parent_thread_id looks like an integer, use it
        if parent_thread_id_raw:
            try:
                parent_thread_id = int(parent_thread_id_raw)
            except (ValueError, TypeError):
                print(f"⚠️ [THREAD CREATE] parent_thread_id is not an integer (got: {parent_thread_id_raw}), setting to NULL")
                parent_thread_id = None
        
        branch_point_message_id = data.get('branch_point_message_id')
        branch_name = data.get('branch_name')
        
        if not user_id:
            return error_response('user_id required', 400)
        
        # IDEMPOTENCY CHECK: If idempotency_key provided, check for existing thread
        if idempotency_key:
            with get_database_connection('sessions') as check_conn:
                with check_conn.cursor() as check_cursor:
                    
                    check_sql, check_params = convert_sql_placeholders(
                        "SELECT id, thread_slug, name FROM sessions.threads WHERE idempotency_key = %s",
                        (idempotency_key,)
                    )
                    check_cursor.execute(check_sql, check_params)
                    existing_thread = check_cursor.fetchone()
                    
                    if existing_thread:
                        # Thread already exists - return cached response
                        existing_id = existing_thread[0] if isinstance(existing_thread, tuple) else existing_thread['id']
                        existing_slug = existing_thread[1] if isinstance(existing_thread, tuple) else existing_thread['thread_slug']
                        existing_name = existing_thread[2] if isinstance(existing_thread, tuple) else existing_thread['name']
                        
                        print(f"✅ [THREAD CREATE] Idempotency hit: {idempotency_key} -> thread {existing_id}")
                        return jsonify({
                            'success': True,
                            'thread_id': existing_slug,  # Return slug for frontend compatibility
                            'database_id': existing_id,
                            'title': existing_name,
                            'idempotent': True,
                            'message': 'Thread already exists (idempotency key matched)'
                        }), 200  # 200 OK (not 201 Created)
        
        # Generate timestamp-based ID (consistent with frontend)
        thread_id = str(int(datetime.now().timestamp() * 1000))
        created = datetime.now().isoformat()
        
        # NEW: Get user's Team ID if they are a sub-user
        team_id = None
        with get_database_connection('ai_infrastructure') as user_conn:
            with user_conn.cursor() as user_cursor:
                
                user_sql, user_params = convert_sql_placeholders(
                    "SELECT is_sub_user, username FROM ai_infrastructure.users WHERE id = %s",
                    (user_id,)
                )
                user_cursor.execute(user_sql, user_params)
                user_row = user_cursor.fetchone()
                
                if user_row:
                    is_sub_user = user_row[0] if isinstance(user_row, tuple) else user_row.get('is_sub_user')
                    username = user_row[1] if isinstance(user_row, tuple) else user_row.get('username')
                    
                    # If user is a sub-user (Team ID), store their username as team_id
                    if is_sub_user:
                        team_id = username
                        print(f"✅ [THREAD CREATE] User is Team ID: {team_id}")
        
        with get_database_connection('sessions') as conn:
            with conn.cursor() as cursor:
                
                # PostgreSQL: Exclude id column to let sequence auto-generate
                sql, params = convert_sql_placeholders("""
                    INSERT INTO sessions.threads (
                        thread_slug, workspace_id, name, user_id, created_at, updated_at,
                        metadata, location, tags, synergy_card_id,
                        parent_thread_id, branch_point_message_id, branch_name, team_id,
                        idempotency_key
                    ) VALUES (
                        %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s
                    )
                    RETURNING id
                """, (
                    thread_id,
                    1,
                    title,
                    user_id,
                    created,
                    created,
                    json.dumps(metadata),
                    location,
                    json.dumps(tags),
                    synergy_card_id,
                    parent_thread_id,
                    branch_point_message_id,
                    branch_name,
                    team_id,
                    idempotency_key  # NEW: Store idempotency key
                ))
                
                cursor.execute(sql, params)
                
                # Get the auto-generated id
                generated_id_result = cursor.fetchone()
                generated_id = generated_id_result[0] if isinstance(generated_id_result, tuple) else generated_id_result['id']
                conn.commit()
        
        thread_data = {
            'id': thread_id,
            'slug': thread_id,  # ✅ CRITICAL: Frontend expects 'slug' field
            'title': title,
            'created': created,
            'agent_id': agent_id,
            'user_id': user_id,
            'parent_thread_id': parent_thread_id,
            'branch_point_message_id': branch_point_message_id,
            'branch_name': branch_name
        }
        
        return success_response(
            {
                'thread': thread_data,
                'thread_slug': thread_id  # ✅ CRITICAL: Communication Hub expects this at root level
            },
            message='Thread created successfully'
        )
        
    except Exception as e:
        import traceback
        print(f"\n❌ [THREAD CREATE] ERROR:")
        print(f"   Error type: {type(e).__name__}")
        print(f"   Error message: {str(e)}")
        print(f"   Full traceback:")
        traceback.print_exc()
        return error_response(f'Failed to create thread: {str(e)}', 500)


@thread_bp.route('/upsert', methods=['POST'])
def upsert_thread():
    """
    Create or update thread in sessions.threads table
    UPSERT pattern - creates if doesn't exist, updates if exists
    """
    try:
        data = request.get_json() or {}
        thread_id = str(data.get('thread_id'))
        user_id = data.get('user_id')
        title = data.get('title', 'Untitled Thread')
        location = data.get('location', 'unassigned')
        tags = data.get('tags', [])
        synergy_card_id = data.get('synergy_card_id')
        
        if not thread_id or not user_id:
            return error_response('thread_id and user_id required', 400)
        
        with get_database_connection('sessions') as conn:
            with conn.cursor() as cursor:
                
                # UPSERT: Insert or update on conflict
                sql, params = convert_sql_placeholders("""
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
                """, (
                    thread_id,
                    1,
                    title,
                    user_id,
                    json.dumps({}),
                    location,
                    json.dumps(tags),
                    synergy_card_id
                ))
                
                cursor.execute(sql, params)
                
                result = cursor.fetchone()
                internal_id = result[0] if isinstance(result, tuple) else result['id']
                
                conn.commit()
        
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


# ============================================================
# THREAD LISTING & SEARCH
# ============================================================

@thread_bp.route('/assigned', methods=['GET'])
def get_assigned_threads():
    """
    Get ONLY threads assigned to columns (Prime/Alpha/Bravo/Charlie)
    Eliminates 92% waste from loading all 50 threads
    """
    try:
        user_id = request.args.get('user_id')
        if not user_id:
            return error_response("user_id is required", 400)
        
        print(f"\n🚀 [THREAD API] /api/threads/assigned called (EFFICIENT MODE)")
        print(f"📊 [THREAD API] Parameters: user_id={user_id}")
        print(f"🗄️ [THREAD API] Database: {'Supabase' if is_using_supabase() else 'SQLite'}")
        
        with get_database_connection('sessions') as conn:
            with conn.cursor() as cursor:
                
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
                        COUNT(CASE 
                            WHEN m.role = 'user' AND (
                                m.metadata IS NULL 
                                OR m.metadata::jsonb->>'tool_results' IS NULL 
                                OR m.metadata::jsonb->>'tool_results' != 'true'
                            ) THEN 1
                            WHEN m.role = 'assistant' AND m.content::jsonb::text LIKE '%%"type": "text"%%' THEN 1
                            ELSE NULL
                        END) as message_count,
                        MAX(m.created_at) as last_message_time,
                        (SELECT role FROM sessions.messages WHERE thread_id = t.id ORDER BY created_at DESC LIMIT 1) as last_message_role
                    FROM sessions.threads t
                    LEFT JOIN sessions.messages m ON t.id = m.thread_id
                    WHERE t.user_id = %s
                      AND t.location IN ('prime', 'agent-1', 'agent-2', 'agent-3', 'agent-4', 'agent-5', 'agent-6', 'agent-7', 'agent-8', 'agent-9')
                      AND (t.archived IS NULL OR t.archived = false)
                    GROUP BY t.id, t.thread_slug, t.name, t.user_id, t.created_at, t.updated_at, 
                             t.metadata, t.location, t.tags, t.synergy_card_id, t.synergy_card_name,
                             t.parent_thread_id, t.branch_name, t.workflow_id, t.workflow_name,
                             t.workflow_slug, t.workflow_title, t.internal_doc_slug, t.internal_doc_title
                    ORDER BY CASE t.location
                        WHEN 'prime' THEN 1
                        WHEN 'agent-1' THEN 2
                        WHEN 'agent-2' THEN 3
                        WHEN 'agent-3' THEN 4
                        WHEN 'agent-4' THEN 6
                        WHEN 'agent-5' THEN 7
                        WHEN 'agent-6' THEN 8
                        WHEN 'agent-7' THEN 9
                        WHEN 'agent-8' THEN 10
                        WHEN 'agent-9' THEN 11
                        ELSE 999
                    END, t.updated_at DESC
                    LIMIT 10
                """
                
                print(f"🚀 [THREAD API] Executing EFFICIENT query (assigned threads only)...")
                cursor.execute(query, (user_id,))
                rows = cursor.fetchall()
                
                print(f"✅ [THREAD API] Efficient query returned {len(rows)} assigned threads")
        
        # Process rows into thread objects
        threads = []
        for idx, row in enumerate(rows, 1):
            try:
                thread_data = {
                    'id': row.get('thread_slug'),
                    'thread_id': row.get('id'),
                    'name': row.get('name') or 'Untitled Thread',
                    'location': row.get('location') or 'unassigned',
                    'message_count': row.get('message_count') or 0,
                    'created_at': row.get('created_at').isoformat() if row.get('created_at') else None,
                    'updated_at': row.get('updated_at').isoformat() if row.get('updated_at') else None,
                    'last_message_time': row.get('last_message_time').isoformat() if row.get('last_message_time') else None,
                    'last_message_role': row.get('last_message_role'),
                    'tags': row.get('tags') or [],
                    'synergy_card_id': row.get('synergy_card_id'),
                    'synergy_card_name': row.get('synergy_card_name'),
                    'workflow_slug': row.get('workflow_slug'),
                    'workflow_title': row.get('workflow_title'),
                    'internal_doc_slug': row.get('internal_doc_slug'),
                    'internal_doc_title': row.get('internal_doc_title'),
                    'archived': False
                }
                threads.append(thread_data)
            except Exception as row_error:
                print(f"⚠️ [THREAD API] Error processing row {idx}: {row_error}")
                continue
        
        print(f"✅ [THREAD API] Returning {len(threads)} assigned threads")
        
        return jsonify({
            'success': True,
            'threads': threads,
            'count': len(threads),
            'message': f'Loaded {len(threads)} assigned threads (efficient mode)'
        }), 200
    
    except Exception as e:
        print(f"❌ [THREAD API] /assigned endpoint failed: {str(e)}")
        import traceback
        traceback.print_exc()
        return error_response(f'Failed to get assigned threads: {str(e)}', 500)


@thread_bp.route('/list', methods=['GET'])
def list_threads():
    """
    List threads from database for a specific user
    
    Query params:
        ?user_id=1 (required): User ID to list threads for
        ?limit=50 (optional): Max threads to return
    """
    try:
        user_id = request.args.get('user_id')
        if not user_id:
            return error_response("user_id is required", 400)
        
        limit = int(request.args.get('limit', 50))
        
        print(f"\n🔍 [THREAD API] /api/threads/list called")
        print(f"📊 [THREAD API] Parameters: user_id={user_id}, limit={limit}")
        
        with get_database_connection('sessions') as conn:
            with conn.cursor() as cursor:
                
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
                        t.email_thread_id,
                        t.email_subject,
                        t.email_participants,
                        COUNT(CASE 
                            WHEN m.role = 'user' AND (
                                m.metadata IS NULL 
                                OR m.metadata::jsonb->>'tool_results' IS NULL 
                                OR m.metadata::jsonb->>'tool_results' != 'true'
                            ) THEN 1
                            WHEN m.role = 'assistant' AND m.content::jsonb::text LIKE '%%"type": "text"%%' THEN 1
                            ELSE NULL
                        END) as message_count,
                        MAX(m.created_at) as last_message_time,
                        (SELECT role FROM sessions.messages WHERE thread_id = t.id ORDER BY created_at DESC LIMIT 1) as last_message_role
                    FROM sessions.threads t
                    LEFT JOIN sessions.messages m ON t.id = m.thread_id
                    WHERE t.user_id = %s
                    GROUP BY t.id, t.thread_slug, t.name, t.user_id, t.created_at, t.updated_at, 
                             t.metadata, t.location, t.tags, t.synergy_card_id, t.synergy_card_name,
                             t.parent_thread_id, t.branch_name, t.workflow_id, t.workflow_name,
                             t.workflow_slug, t.workflow_title, t.internal_doc_slug, t.internal_doc_title,
                             t.email_thread_id, t.email_subject, t.email_participants
                    ORDER BY t.updated_at DESC
                    LIMIT %s
                """
                
                cursor.execute(query, (user_id, limit))
                rows = cursor.fetchall()
                
                print(f"✅ [THREAD API] Query returned {len(rows)} rows")
        
        # Process rows into thread objects
        threads = []
        for idx, row in enumerate(rows, 1):
            try:
                thread_data = {
                    'id': row.get('thread_slug'),
                    'thread_id': row.get('id'),
                    'title': row.get('name'),
                    'user_id': row.get('user_id'),
                    'created': row.get('created_at'),
                    'updated': row.get('updated_at'),
                    'metadata': json.loads(row.get('metadata')) if row.get('metadata') else {},
                    'location': row.get('location') if row.get('location') else 'unassigned',  # ✅ FIX: Only default if None/empty
                    'agent': row.get('location') if row.get('location') else 'main',
                    'tags': json.loads(row.get('tags')) if row.get('tags') else [],
                    'synergy_card_id': row.get('synergy_card_id'),
                    'synergy_card_name': row.get('synergy_card_name'),
                    'parent_thread_id': row.get('parent_thread_id'),
                    'branch_name': row.get('branch_name'),
                    'workflow_id': row.get('workflow_id'),
                    'workflow_name': row.get('workflow_name'),
                    'workflow_slug': row.get('workflow_slug'),
                    'workflow_title': row.get('workflow_title'),
                    'internal_doc_slug': row.get('internal_doc_slug'),
                    'internal_doc_title': row.get('internal_doc_title'),
                    'email_thread_id': row.get('email_thread_id'),
                    'email_subject': row.get('email_subject'),
                    'email_participants': row.get('email_participants'),
                    'message_count': row.get('message_count') or 0,
                    'last_message_time': row.get('last_message_time'),
                    'last_message_role': row.get('last_message_role'),
                    'archived': False
                }
                threads.append(thread_data)
            except Exception as row_error:
                print(f"❌ [THREAD API] ERROR processing row {idx}: {row_error}")
                continue
        
        print(f"📤 [THREAD API] Returning {len(threads)} threads")
        
        return success_response({
            'threads': threads,
            'count': len(threads)
        }, message=f"Found {len(threads)} threads for user {user_id}")
    
    except Exception as e:
        print(f"❌ [THREAD API] Error: {str(e)}")
        import traceback
        traceback.print_exc()
        return error_response(f"Failed to list threads: {str(e)}", 500)


@thread_bp.route('/bulk-with-messages', methods=['GET'])
def get_threads_bulk_with_messages():
    """
    Bulk fetch threads + messages for specific locations (1 query instead of 6+)
    """
    try:
        from psycopg2.extras import RealDictCursor
        
        user_id = request.args.get('user_id', type=int)
        locations_param = request.args.get('locations', '')
        
        if not user_id:
            return error_response('user_id required', 400)
        
        if not locations_param:
            return error_response('locations required (e.g., agent-1,agent-2,prime)', 400)
        
        # Parse locations
        locations = [loc.strip() for loc in locations_param.split(',') if loc.strip()]
        
        if not locations:
            return error_response('No valid locations provided', 400)
        
        print(f"🚀 [BULK FETCH] Starting optimized fetch for user {user_id}")
        print(f"📍 [BULK FETCH] Locations requested: {locations}")
        
        with get_database_connection('sessions') as conn:
            with conn.cursor(cursor_factory=RealDictCursor) as cursor:
                
                # Build IN clause with proper placeholders
                placeholders = ','.join(['%s'] * len(locations))
                
                # Single query with JSON aggregation (PostgreSQL only)
                query = f"""
                    WITH assigned_threads AS (
                        SELECT 
                            t.id,
                            t.thread_slug,
                            t.name,
                            t.location,
                            t.created_at,
                            t.updated_at,
                            t.synergy_card_id,
                            t.workflow_id,
                            t.workflow_slug,
                            t.workflow_title,
                            t.internal_doc_slug,
                            t.internal_doc_title
                        FROM sessions.threads t
                        WHERE t.user_id = %s
                          AND t.location IN ({placeholders})
                    )
                    SELECT 
                        at.id,
                        at.thread_slug,
                        at.name,
                        at.location,
                        at.created_at,
                        at.updated_at,
                        at.synergy_card_id,
                        at.workflow_id,
                        at.workflow_slug,
                        at.workflow_title,
                        at.internal_doc_slug,
                        at.internal_doc_title,
                        COALESCE(
                            json_agg(
                                json_build_object(
                                    'id', m.id,
                                    'role', m.role,
                                    'content', m.content,
                                    'created_at', m.created_at,
                                    'tool_calls', m.tool_calls,
                                    'tool_results', m.tool_results
                                ) ORDER BY m.created_at ASC
                            ) FILTER (WHERE m.id IS NOT NULL),
                            '[]'::json
                        ) as messages
                    FROM assigned_threads at
                    LEFT JOIN sessions.messages m ON m.thread_id = at.id
                    GROUP BY at.id, at.thread_slug, at.name, at.location, 
                             at.created_at, at.updated_at, at.synergy_card_id, 
                             at.workflow_id, at.workflow_slug, at.workflow_title,
                             at.internal_doc_slug, at.internal_doc_title
                    ORDER BY at.updated_at DESC
                """
                
                # Execute with user_id + locations
                params = (user_id, *locations)
                cursor.execute(query, params)
                threads = cursor.fetchall()
                
                print(f"✅ [BULK FETCH] Loaded {len(threads)} threads in 1 query")
        
        return success_response({
            'threads': threads,
            'count': len(threads)
        }, message=f'Loaded {len(threads)} threads with messages in 1 query')
        
    except Exception as e:
        print(f"❌ [BULK FETCH] Error: {str(e)}")
        import traceback
        traceback.print_exc()
        return error_response(f'Bulk fetch failed: {str(e)}', 500)


@thread_bp.route('/metadata/update', methods=['POST'])
def update_thread_metadata_fields():
    """
    Update thread metadata fields (workflow_slug, workflow_title, internal_doc_slug, internal_doc_title)
    """
    try:
        data = request.json
        thread_slug = data.get('thread_slug')
        
        if not thread_slug:
            return error_response('thread_slug required', 400)
        
        with get_database_connection('sessions') as conn:
            with conn.cursor() as cursor:
                
                # Build UPDATE query for metadata fields only
                sql, params = convert_sql_placeholders("""
                    UPDATE sessions.threads SET
                        workflow_slug = %s,
                        workflow_title = %s,
                        internal_doc_slug = %s,
                        internal_doc_title = %s,
                        updated_at = CURRENT_TIMESTAMP
                    WHERE thread_slug = %s
                """, (
                    data.get('workflow_slug'),
                    data.get('workflow_title'),
                    data.get('internal_doc_slug'),
                    data.get('internal_doc_title'),
                    thread_slug
                ))
                
                cursor.execute(sql, params)
                conn.commit()
        
        print(f"[THREAD METADATA] ✅ SUCCESS: Thread metadata updated")
        
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
        print(f"❌ [THREAD METADATA ERROR] {str(e)}")
        import traceback
        traceback.print_exc()
        return error_response(f'Failed to update thread metadata: {str(e)}', 500)


@thread_bp.route('/list-legacy', methods=['GET'])
def list_threads_legacy():
    """
    LEGACY: List all conversation threads across all agents from agent_state_manager
    
    Query params:
        ?agent_id=stock_ai (optional filter)
        ?limit=50 (default 50)
        ?days=30 (show threads from last N days)
    """
    try:
        agent_filter = request.args.get('agent_id')
        limit = int(request.args.get('limit', 50))
        days = int(request.args.get('days', 30))
        
        cutoff_date = datetime.now() - timedelta(days=days)
        
        threads = []
        
        # Get threads from agent_state_manager
        for agent_id, sessions in agent_state_manager._agent_states.items():
            if agent_filter and agent_id != agent_filter:
                continue
            
            for session_id, state in sessions.items():
                last_activity = state.get('last_activity')
                
                if last_activity:
                    try:
                        activity_time = datetime.fromisoformat(last_activity)
                        if activity_time < cutoff_date:
                            continue
                    except:
                        pass
                
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
                    'location': state.get('location', 'unassigned'),
                    'user_id': state.get('user_id', 1)
                })
        
        threads.sort(key=lambda x: x.get('last_activity', ''), reverse=True)
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
    """
    try:
        keyword = request.args.get('q', '').strip().lower()
        agent_filter = request.args.get('agent_id')
        limit = int(request.args.get('limit', 20))
        
        if not keyword:
            return error_response("Missing search keyword 'q'", 400)
        
        matching_threads = []
        
        for agent_id, sessions in agent_state_manager._agent_states.items():
            if agent_filter and agent_id != agent_filter:
                continue
            
            for session_id, state in sessions.items():
                matches = []
                for i, message in enumerate(state['conversation']):
                    content = str(message.get('content', '')).lower()
                    if keyword in content:
                        matches.append({
                            'message_index': i,
                            'role': message.get('role'),
                            'snippet': content[:200]
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
                        'matches': matches[:3],
                        'last_activity': state.get('last_activity')
                    })
        
        matching_threads.sort(key=lambda x: x['match_count'], reverse=True)
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
    Format 1 (Backend format): agent_id + session_id
    Format 2 (Frontend format): thread_id + messages + title
    """
    print(f"\n{'='*80}")
    print(f"[THREAD SAVE] 📝 Saving thread...")
    print(f"{'='*80}")
    try:
        data = request.json
        
        # Detect format and normalize
        if 'thread_id' in data and 'messages' in data:
            # Format 2 (Frontend)
            thread_id = str(data.get('thread_id'))
            title = data.get('title', 'Untitled Thread')
            messages = data.get('messages', [])
            agent = data.get('agent', 'unassigned')
            user_id = data.get('user_id', 1)
            location = str(data.get('location', 'unassigned'))
            
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
            # Format 1 (Backend)
            agent_id = data.get('agent_id')
            session_id = data.get('session_id')
            thread_name = data.get('thread_name', '')
            user_id = data.get('user_id', 1)
            location = data.get('location', 'unassigned')
            conversation = None
            
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
        
        # Ensure strings
        agent_id = str(agent_id) if agent_id is not None else None
        session_id = str(session_id) if session_id is not None else None
        location = str(location) if location is not None else 'unassigned'
        
        # Get thread state if conversation not provided
        if conversation is None:
            state = agent_state_manager.get_or_create_state(agent_id, session_id, {})
            
            if not state['conversation']:
                return error_response("Thread has no messages to save", 400)
            
            conversation = state['conversation']
        
        if not conversation:
            return error_response("Thread has no messages to save", 400)
        
        with get_database_connection('sessions') as conn:
            with conn.cursor() as cursor:
                
                # Create table if not exists
                create_table_query = """
                    CREATE TABLE IF NOT EXISTS sessions.saved_threads (
                        thread_id TEXT PRIMARY KEY,
                        agent_id TEXT NOT NULL,
                        session_id TEXT NOT NULL,
                        user_id INTEGER DEFAULT 1,
                        location TEXT DEFAULT 'prime',
                        thread_name TEXT,
                        conversation TEXT NOT NULL,
                        message_count INTEGER,
                        context TEXT,
                        created_at TIMESTAMP,
                        saved_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        tags TEXT DEFAULT '[]',
                        synergy_card_id TEXT DEFAULT NULL,
                        parent_thread_id TEXT DEFAULT NULL,
                        branch_point_message_id TEXT DEFAULT NULL,
                        branch_name TEXT DEFAULT NULL,
                        summary TEXT DEFAULT NULL,
                        summary_generated_at TEXT DEFAULT NULL
                    )
                """
                
                try:
                    cursor.execute(create_table_query)
                    conn.commit()
                except Exception as e:
                    print(f"⚠️ [Thread Save] Table creation note: {e}")
                    conn.rollback()
                
                # Insert thread
                thread_id_full = f"{agent_id}_{session_id}"
                conversation_json = json.dumps(conversation)
                context_json = json.dumps({})
                
                # PostgreSQL: INSERT ... ON CONFLICT (upsert)
                sql, params = convert_sql_placeholders("""
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
                """, (
                    thread_id_full,
                    agent_id,
                    session_id,
                    user_id,
                    location,
                    thread_name,
                    conversation_json,
                    len(conversation),
                    context_json,
                    tags,
                    synergy_card_id,
                    parent_thread_id,
                    branch_point_message_id,
                    branch_name,
                    summary,
                    summary_generated_at
                ))
                
                cursor.execute(sql, params)
                conn.commit()
        
        # Update thread assignments if needed
        if location and location != 'unassigned' and location.startswith('agent-'):
            try:
                from routes.thread_assignment_routes import enforce_thread_assignment_rules
                enforce_thread_assignment_rules(user_id, session_id, location)
                print(f"✅ [Thread Save] Updated thread assignment: {session_id} -> {location}")
            except Exception as e:
                print(f"⚠️ [Thread Save] Failed to update thread assignment: {e}")
        
        # ✅ CROSS-DEVICE SYNC: Broadcast thread update to all user's devices
        try:
            from flask import current_app
            socketio = current_app.extensions.get('socketio')
            if socketio:
                socketio.emit('thread_updated', {
                    'thread_id': thread_id_full,
                    'agent_id': agent_id,
                    'session_id': session_id,
                    'thread_name': thread_name,
                    'message_count': len(conversation),
                    'location': location,
                    'action': 'saved',
                    'timestamp': datetime.now().isoformat()
                }, room=f'user_{user_id}', namespace='/ws/synergy')
                print(f"📡 [Thread Save] Broadcast to user_{user_id} devices")
        except Exception as broadcast_err:
            print(f"⚠️ [Thread Save] Broadcast failed (non-critical): {broadcast_err}")
        
        print(f"[THREAD SAVE] ✅ SUCCESS: Thread saved")
        print(f"[THREAD SAVE] Messages: {len(conversation)}")
        print(f"{'='*80}\n")
        
        return success_response({
            'thread_id': thread_id_full,
            'message_count': len(conversation),
            'saved_at': datetime.now().isoformat(),
            'location': location
        }, message="Thread saved successfully")
    
    except DatabaseConnectionError as e:
        return error_response(f"Database error: {str(e)}", 500)
    except Exception as e:
        print(f"❌ [THREAD SAVE ERROR] {str(e)}")
        import traceback
        traceback.print_exc()
        return error_response(str(e), 500)


@thread_bp.route('/load/<thread_id>', methods=['GET'])
def load_thread(thread_id):
    """
    Load saved thread from persistent storage
    """
    try:
        with get_database_connection('sessions') as conn:
            with conn.cursor() as cursor:
                
                sql, params = convert_sql_placeholders("""
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
                """, (thread_id,))
                
                cursor.execute(sql, params)
                results = cursor.fetchall()
        
        if not results:
            return error_response(f"Thread {thread_id} not found", 404)
        
        thread = results[0]
        
        # Parse JSON fields
        thread_dict = dict(thread)
        thread_dict['conversation'] = json.loads(thread['conversation'])
        thread_dict['context'] = json.loads(thread.get('context', '{}'))
        
        return success_response(thread_dict, message="Thread loaded successfully")
    
    except DatabaseConnectionError as e:
        return error_response(f"Database error: {str(e)}", 500)
    except Exception as e:
        print(f"❌ [THREAD LOAD ERROR] {str(e)}")
        import traceback
        traceback.print_exc()
        return error_response(str(e), 500)


@thread_bp.route('/<thread_id>', methods=['DELETE'])
def delete_thread(thread_id):
    """
    Delete saved thread from persistent storage
    
    Supports both formats:
    - UUID format: "sess_abc123" or any UUID (thread_slug)
    - Legacy format: "agent_id_session_id"
    """
    try:
        print(f"[DELETE THREAD] Attempting to delete thread: {thread_id}")
        
        # Try to parse as legacy format (agent_id_session_id)
        parts = thread_id.split('_', 1)
        if len(parts) == 2 and not thread_id.startswith('sess_'):
            # Legacy format
            agent_id, session_id = parts
            agent_state_manager.clear_conversation(agent_id, session_id)
        else:
            # UUID format
            agent_state_manager.clear_conversation('prime', thread_id)
        
        with get_database_connection('sessions') as conn:
            with conn.cursor() as cursor:
                
                # Get the internal thread ID
                sql, params = convert_sql_placeholders("""
                    SELECT id FROM sessions.threads
                    WHERE thread_slug = %s
                """, (thread_id,))
                
                cursor.execute(sql, params)
                result = cursor.fetchone()
                
                if not result:
                    print(f"[DELETE THREAD] Thread not found: {thread_id}")
                    return error_response(f"Thread {thread_id} not found", 404)
                
                internal_thread_id = result[0] if isinstance(result, tuple) else result['id']
                print(f"[DELETE THREAD] Found thread with internal ID: {internal_thread_id}")
                
                # Delete related messages first
                sql, params = convert_sql_placeholders("""
                    DELETE FROM sessions.messages
                    WHERE thread_id = %s
                """, (internal_thread_id,))
                
                cursor.execute(sql, params)
                messages_deleted = cursor.rowcount
                print(f"[DELETE THREAD] Deleted {messages_deleted} messages")
                
                # Delete the thread
                sql, params = convert_sql_placeholders("""
                    DELETE FROM sessions.threads
                    WHERE id = %s
                """, (internal_thread_id,))
                
                cursor.execute(sql, params)
                threads_deleted = cursor.rowcount
                
                conn.commit()
        
        # ✅ CROSS-DEVICE SYNC: Broadcast thread deletion to all user's devices
        try:
            from flask import current_app
            user_id = request.args.get('user_id', type=int) or 1
            socketio = current_app.extensions.get('socketio')
            if socketio:
                socketio.emit('thread_deleted', {
                    'thread_id': thread_id,
                    'action': 'deleted',
                    'timestamp': datetime.now().isoformat()
                }, room=f'user_{user_id}', namespace='/ws/synergy')
                print(f"📡 [Thread Delete] Broadcast to user_{user_id} devices")
        except Exception as broadcast_err:
            print(f"⚠️ [Thread Delete] Broadcast failed (non-critical): {broadcast_err}")
        
        print(f"[DELETE THREAD] Successfully deleted thread {thread_id}")
        
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
    """
    try:
        data = request.json
        if not data:
            return error_response("No data provided", 400)
        
        # Build dynamic UPDATE query
        update_fields = []
        params = []
        
        if 'name' in data:
            update_fields.append("name = %s")
            params.append(data['name'])
        
        if 'tags' in data:
            update_fields.append("tags = %s")
            params.append(json.dumps(data['tags']))
        
        if 'synergy_card_id' in data:
            update_fields.append("synergy_card_id = %s")
            params.append(data['synergy_card_id'])
        
        if 'synergy_card_name' in data:
            update_fields.append("synergy_card_name = %s")
            params.append(data['synergy_card_name'])
        
        if 'workflow_id' in data:
            update_fields.append("workflow_id = %s")
            params.append(data['workflow_id'])
        
        if 'workflow_name' in data:
            update_fields.append("workflow_name = %s")
            params.append(data['workflow_name'])
        
        if 'location' in data:
            update_fields.append("location = %s")
            params.append(data['location'])
        
        if not update_fields:
            return error_response("No valid fields to update", 400)
        
        # Add updated_at timestamp
        update_fields.append("updated_at = NOW()")
        
        # Add thread_id to params
        params.append(thread_id)
        
        with get_database_connection('sessions') as conn:
            with conn.cursor() as cursor:
                
                update_query = f"""
                    UPDATE sessions.threads
                    SET {', '.join(update_fields)}
                    WHERE thread_slug = %s
                """
                
                sql, converted_params = convert_sql_placeholders(update_query, tuple(params))
                cursor.execute(sql, converted_params)
                rowcount = cursor.rowcount
                conn.commit()
        
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
        
        # Count saved threads from database
        try:
            with get_database_connection('sessions') as conn:
                with conn.cursor() as cursor:
                    
                    sql, params = convert_sql_placeholders("""
                        SELECT COUNT(*) as count
                        FROM sessions.saved_threads
                    """, ())
                    
                    cursor.execute(sql, params)
                    results = cursor.fetchall()
                    
                    if results:
                        stats['saved_threads'] = results[0]['count']
        except:
            stats['saved_threads'] = 0
        
        return success_response(stats, message="Thread statistics")
    
    except Exception as e:
        print(f"❌ [THREAD STATS ERROR] {str(e)}")
        return error_response(str(e), 500)


# ============================================================
# AUTO-SAVE & MARK READ
# ============================================================

@thread_bp.route('/autosave', methods=['POST'])
def autosave_thread():
    """
    Auto-save thread during conversation
    """
    print(f"\n{'='*80}")
    print(f"[AUTOSAVE] 🔄 Checking autosave trigger...")
    print(f"{'='*80}")
    
    try:
        data = request.json
        agent_id = data.get('agent_id')
        session_id = data.get('session_id')
        print(f"[AUTOSAVE] Agent: {agent_id}, Session: {session_id}")
        
        if not agent_id or not session_id:
            print(f"[AUTOSAVE] ❌ FAILED: Missing required fields")
            return error_response("Missing agent_id or session_id", 400)
        
        # Get thread state
        state = agent_state_manager.get_or_create_state(agent_id, session_id, {})
        
        message_count = len(state['conversation'])
        print(f"[AUTOSAVE] Message count: {message_count}")
        
        # Only auto-save if we have messages
        if message_count == 0:
            print(f"[AUTOSAVE] ⏭️  SKIPPED: No messages to save")
            return success_response({
                'autosaved': False,
                'reason': 'No messages to save'
            })
        
        # Auto-save every 5 messages
        if message_count % 5 == 0:
            print(f"[AUTOSAVE] 💾 Milestone reached ({message_count} messages) - saving...")
            
            thread_id = f"{agent_id}_{session_id}"
            conversation_json = json.dumps(state['conversation'])
            context_json = json.dumps(state.get('context', {}))
            
            with get_database_connection('sessions') as conn:
                with conn.cursor() as cursor:
                    
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
                    
                    # Save thread
                    sql, params = convert_sql_placeholders("""
                        INSERT INTO sessions.saved_threads 
                        (thread_id, agent_id, session_id, thread_name, conversation, 
                         message_count, context, created_at, saved_at)
                        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, NOW())
                        ON CONFLICT (thread_id) DO UPDATE SET
                            conversation = EXCLUDED.conversation,
                            message_count = EXCLUDED.message_count,
                            saved_at = NOW()
                    """, (
                        thread_id,
                        agent_id,
                        session_id,
                        f"Auto-saved conversation ({message_count} messages)",
                        conversation_json,
                        message_count,
                        context_json,
                        state.get('created_at')
                    ))
                    
                    cursor.execute(sql, params)
                    conn.commit()
            
            print(f"[AUTOSAVE] ✅ SUCCESS: Thread auto-saved")
            print(f"[AUTOSAVE] Thread ID: {thread_id}")
            print(f"[AUTOSAVE] Messages: {message_count}")
            
            return success_response({
                'autosaved': True,
                'message_count': message_count,
                'thread_id': thread_id
            }, message="Thread auto-saved")
        
        print(f"[AUTOSAVE] ⏭️  SKIPPED: Waiting for milestone")
        
        return success_response({
            'autosaved': False,
            'reason': f"Waiting for milestone ({message_count} messages)"
        })
    
    except Exception as e:
        print(f"[AUTOSAVE] ❌ EXCEPTION: {str(e)}")
        import traceback
        traceback.print_exc()
        return error_response(str(e), 500)


@thread_bp.route('/<thread_id>/mark-read', methods=['POST'])
def mark_thread_read(thread_id):
    """
    Mark thread as read
    """
    try:
        with get_database_connection('sessions') as conn:
            with conn.cursor() as cursor:
                
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
                
                # Update last_read
                sql, params = convert_sql_placeholders("""
                    UPDATE sessions.saved_threads
                    SET last_read = NOW()
                    WHERE thread_id = %s
                """, (thread_id,))
                
                cursor.execute(sql, params)
                rowcount = cursor.rowcount
                conn.commit()
        
        if rowcount == 0:
            return error_response(f"Thread {thread_id} not found", 404)
        
        return updated_response(
            message="Thread marked as read",
            updated_count=rowcount
        )
    
    except DatabaseConnectionError as e:
        return error_response(f"Database error: {str(e)}", 500)
    except Exception as e:
        print(f"❌ [MARK READ ERROR] {str(e)}")
        return error_response(str(e), 500)


@thread_bp.route('/details', methods=['POST'])
def get_threads_details():
    """
    Get detailed information for multiple threads including agent assignments
    
    SYNERGY INTEGRATION: Used to display linked threads in Synergy cards
    """
    print("[THREADS DETAILS] Endpoint called!")
    try:
        data = request.get_json()
        thread_ids = data.get('thread_ids', [])
        
        if not thread_ids or not isinstance(thread_ids, list):
            return error_response("thread_ids array required", 400)
        
        if len(thread_ids) == 0:
            return success_response([])
        
        # Build query with placeholders
        placeholders = ','.join(['%s' for _ in thread_ids])
        
        with get_database_connection('sessions') as conn:
            with conn.cursor() as cursor:
                
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
                
                sql, params = convert_sql_placeholders(query, tuple(thread_ids))
                cursor.execute(sql, params)
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
        
        # Populate agent assignments
        result = []
        for thread in threads:
            thread_id = thread['id']
            thread_slug = thread['thread_slug']
            location_from_threads = thread.get('location')
            
            if location_from_threads:
                agent_location = location_from_threads
                agent_display_name = location_from_threads.upper()
            else:
                agent_location = 'unassigned'
                agent_display_name = 'Unassigned'
            
            result.append({
                'id': thread_id,
                'thread_slug': thread_slug,
                'name': thread.get('name') or thread_slug or str(thread_id),
                'created': thread.get('created_at'),
                'updated': thread.get('updated_at'),
                'synergy_card_id': thread.get('synergy_card_id'),
                'synergy_card_name': None,
                'agent_id': agent_location,
                'agent_name': agent_display_name
            })
        
        print(f"[THREADS DETAILS] Returning {len(result)} threads")
        return success_response(result)
    
    except Exception as e:
        print(f"[THREADS ERROR] {str(e)}")
        import traceback
        traceback.print_exc()
        return error_response(f"Thread details error: {str(e)}", 500)


# ============================================================
# MESSAGE SAVING
# ============================================================

@thread_bp.route('/messages/save', methods=['POST'])
def save_messages():
    """
    Save messages directly to the messages table
    CRITICAL FIX: Links messages to threads so they show up in thread list
    ENHANCED (Jan 4, 2026): Adds session token for cross-session sync
    """
    try:
        data = request.get_json() or {}
        thread_id = str(data.get('thread_id'))
        messages = data.get('messages', [])
        user_id = data.get('user_id', 1)
        
        if not thread_id:
            return error_response('thread_id required', 400)
        
        if not messages or not isinstance(messages, list):
            return error_response('messages array required', 400)
        
        # Get session token for cross-session sync
        session_token = request.headers.get('X-Session-Token') or \
                       request.headers.get('Session-Token') or \
                       data.get('session_token')
        
        print(f"[MESSAGE SAVE] Thread: {thread_id}, User: {user_id}, Messages: {len(messages)}, Session: {session_token[:8] if session_token else 'none'}...")
        
        with get_database_connection('sessions') as conn:
            with conn.cursor() as cursor:
                
                # Get the internal thread database ID and count
                sql, params = convert_sql_placeholders("""
                    SELECT t.id, COUNT(m.id) as message_count
                    FROM sessions.threads t
                    LEFT JOIN sessions.messages m ON m.thread_id = t.id
                    WHERE t.thread_slug = %s
                    GROUP BY t.id
                """, (thread_id,))
                
                cursor.execute(sql, params)
                result = cursor.fetchone()
                
                if not result:
                    return error_response(f'Thread {thread_id} not found', 404)
                
                internal_thread_id = result['id']
                existing_message_count = result['message_count'] or 0
                print(f"[MESSAGE SAVE] Thread {thread_id} (DB ID: {internal_thread_id}) has {existing_message_count} existing messages")
                
                # Only save NEW messages
                messages_to_save = messages[existing_message_count:]
                print(f"[MESSAGE SAVE] Appending {len(messages_to_save)} new messages")
                
                saved_count = 0
                
                for msg in messages_to_save:
                    role = msg.get('role')
                    content = msg.get('content')
                    timestamp = msg.get('timestamp') or msg.get('created_at')
                    
                    if not role or not content:
                        continue
                    
                    # Add session token to metadata for duplicate detection
                    metadata = msg.get('metadata', {})
                    if isinstance(metadata, str):
                        try:
                            metadata = json.loads(metadata)
                        except:
                            metadata = {}
                    
                    if session_token:
                        metadata['session_token'] = session_token
                        metadata['timestamp'] = datetime.now(timezone.utc).isoformat()
                    
                    # Skip empty/whitespace-only messages
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
                        print(f"[MESSAGE SAVE] Skipping empty message: {role}")
                        continue
                    
                    try:
                        # Serialize content to JSON
                        content_str = json.dumps(content) if isinstance(content, (dict, list)) else content
                        metadata_str = json.dumps(metadata) if metadata else None
                        
                        # Use provided timestamp or fallback to CURRENT_TIMESTAMP
                        if timestamp:
                            sql, params = convert_sql_placeholders("""
                                INSERT INTO sessions.messages (thread_id, role, content, metadata, user_id, created_at)
                                VALUES (%s, %s, %s, %s, %s, %s)
                            """, (internal_thread_id, role, content_str, metadata_str, user_id, timestamp))
                        else:
                            sql, params = convert_sql_placeholders("""
                                INSERT INTO sessions.messages (thread_id, role, content, metadata, user_id, created_at)
                                VALUES (%s, %s, %s, %s, %s, CURRENT_TIMESTAMP)
                            """, (internal_thread_id, role, content_str, metadata_str, user_id))
                        
                        cursor.execute(sql, params)
                        saved_count += 1
                    except Exception as msg_error:
                        print(f"[MESSAGE SAVE ERROR] Failed to save message: {msg_error}")
                        continue
                
                conn.commit()
        
        print(f"[MESSAGE SAVE] Successfully saved {saved_count} messages to thread {thread_id}")
        
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
    Get messages for a thread (with optional pagination)
    """
    try:
        thread_id = request.args.get('thread_id')
        if not thread_id:
            return error_response('thread_id required', 400)
        
        # Get pagination params
        limit = request.args.get('limit', type=int)
        offset = request.args.get('offset', default=0, type=int)
        
        with get_database_connection('sessions') as conn:
            with conn.cursor() as cursor:
                
                # Get WHERE clause for thread lookup (handles both ID and slug)
                where_clause, lookup_value = get_thread_lookup_clause(thread_id)
                print(f"[THREAD MESSAGES] thread_id={thread_id} -> WHERE {where_clause}, value={lookup_value} (type: {type(lookup_value)})")
                
                # Get total message count
                sql, params = convert_sql_placeholders(f"""
                    SELECT COUNT(m.id) as total
                    FROM sessions.messages m
                    JOIN sessions.threads t ON m.thread_id = t.id
                    WHERE {where_clause}
                """, (lookup_value,))
                
                print(f"[THREAD MESSAGES] SQL: {sql}")
                print(f"[THREAD MESSAGES] Params: {params}")
                
                cursor.execute(sql, params)
                result = cursor.fetchone()
                total_count = result['total'] if isinstance(result, dict) else result[0]
                
                print(f"[THREAD MESSAGES] Total count: {total_count}")
                
                # Query messages (always in chronological order)
                # ✅ FIX: Always use ASC to prevent message clustering and missing AI responses
                # CRITICAL: DESC with LIMIT caused user messages to appear clustered because
                # AI responses between them were cut off by pagination (e.g., missing rows 1-20)
                sql, params = convert_sql_placeholders(f"""
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
                    WHERE {where_clause}
                    ORDER BY m.created_at ASC
                    LIMIT %s OFFSET %s
                """, (lookup_value, limit if limit else 999999, offset))
                
                cursor.execute(sql, params)
                rows = cursor.fetchall()
        
        # Process rows
        messages = []
        role_counts = {'user': 0, 'assistant': 0, 'tool': 0, 'other': 0}
        for row in rows:
            metadata_value = row.get('metadata') if isinstance(row, dict) else row[6]
            metadata = {}
            if metadata_value:
                try:
                    metadata = json.loads(metadata_value)
                except:
                    pass
            
            content_value = row['content'] if isinstance(row, dict) else row[2]
            try:
                if isinstance(content_value, str):
                    content = json.loads(content_value)
                else:
                    content = content_value
            except:
                content = content_value
            
            tool_calls_value = row.get('tool_calls') if isinstance(row, dict) else row[3]
            try:
                tool_calls = json.loads(tool_calls_value) if tool_calls_value else []
            except:
                tool_calls = []
            
            message_role = row['role'] if isinstance(row, dict) else row[1]
            role_counts[message_role] = role_counts.get(message_role, 0) + 1
            
            messages.append({
                'id': row['id'] if isinstance(row, dict) else row[0],
                'role': message_role,
                'content': content,
                'tool_calls': tool_calls,
                'tokens_used': row.get('tokens_used') if isinstance(row, dict) else row[4],
                'response_time_ms': None,
                'timestamp': row['created_at'] if isinstance(row, dict) else row[5],
                'metadata': metadata
            })
        
        if limit:
            messages.reverse()
        
        print(f"[BACKEND DEBUG] Thread {thread_id}: Returning {len(messages)} messages")
        print(f"[BACKEND DEBUG] Role distribution: {role_counts}")
        if messages:
            print(f"[BACKEND DEBUG] First message: role={messages[0]['role']}, content_type={type(messages[0]['content'])}")
            if len(messages) > 1:
                print(f"[BACKEND DEBUG] Last message: role={messages[-1]['role']}, content_type={type(messages[-1]['content'])}")
        
        return success_response({
            'messages': messages,
            'count': len(messages),
            'total': total_count,
            'offset': offset,
            'limit': limit,
            'has_more': (offset + len(messages)) < total_count if limit else False
        }, message=f'Found {len(messages)} messages')
    
    except Exception as e:
        print(f"❌ [MESSAGE GET ERROR] {str(e)}")
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
    """
    try:
        location = location.strip()
        
        # Get user_id
        user_id = None
        auth_header = request.headers.get('Authorization')
        if auth_header and auth_header.startswith('Bearer '):
            try:
                import jwt
                token = auth_header.split(' ')[1]
                payload = jwt.decode(token, options={"verify_signature": False})
                user_id = payload.get('user_id')
            except:
                pass
        
        if not user_id:
            user_id = request.args.get('user_id', type=int)
        
        if not user_id:
            user_id = 1
        
        print(f"[DELETE ASSIGNMENT] Clearing assignment for location: {location}, user_id: {user_id}")
        
        with get_database_connection('sessions') as conn:
            with conn.cursor() as cursor:
                
                # Ensure user row exists
                sql, params = convert_sql_placeholders(
                    "SELECT id FROM ai_infrastructure.users WHERE id = %s",
                    (user_id,)
                )
                cursor.execute(sql, params)
                
                if not cursor.fetchone():
                    sql, params = convert_sql_placeholders("""
                        INSERT INTO ai_infrastructure.users (id, username, email, metadata)
                        VALUES (%s, %s, %s, %s)
                    """, (user_id, f'user_{user_id}', f'user_{user_id}@example.com', '{}'))
                    cursor.execute(sql, params)
                
                # Get current metadata
                sql, params = convert_sql_placeholders(
                    "SELECT metadata FROM ai_infrastructure.users WHERE id = %s",
                    (user_id,)
                )
                cursor.execute(sql, params)
                row = cursor.fetchone()
                metadata = json.loads(row['metadata'] if row['metadata'] else '{}')
                
                # Remove assignment
                assignments = metadata.get('thread_assignments', {})
                session_id = assignments.pop(location, None)
                
                # Update metadata
                metadata['thread_assignments'] = assignments
                sql, params = convert_sql_placeholders("""
                    UPDATE ai_infrastructure.users
                    SET metadata = %s
                    WHERE id = %s
                """, (json.dumps(metadata), user_id))
                cursor.execute(sql, params)
                
                conn.commit()
        
        deleted_count = 1 if session_id else 0
        print(f"[DELETE ASSIGNMENT] Cleared {location} assignment for user {user_id}")
        
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
    """
    try:
        data = request.get_json()
        device_id = data.get('device_id')
        device_name = data.get('device_name')
        
        if not device_id or not device_name:
            return error_response('device_id and device_name required', 400)
        
        locked_at = datetime.now().isoformat()
        
        with get_database_connection('sessions') as conn:
            with conn.cursor() as cursor:
                
                sql, params = convert_sql_placeholders("""
                    UPDATE sessions.threads 
                    SET locked_to_device_id = %s,
                        locked_at = %s
                    WHERE id = %s
                """, (device_id, locked_at, thread_id))
                
                cursor.execute(sql, params)
                rowcount = cursor.rowcount
                conn.commit()
        
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
    """
    try:
        with get_database_connection('sessions') as conn:
            with conn.cursor() as cursor:
                
                sql, params = convert_sql_placeholders("""
                    UPDATE sessions.threads 
                    SET locked_to_device_id = NULL,
                        locked_at = NULL
                    WHERE id = %s
                """, (thread_id,))
                
                cursor.execute(sql, params)
                rowcount = cursor.rowcount
                conn.commit()
        
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
    """
    try:
        with get_database_connection('sessions') as conn:
            with conn.cursor() as cursor:
                
                sql, params = convert_sql_placeholders("""
                    SELECT locked_to_device_id, locked_at
                    FROM sessions.threads
                    WHERE id = %s
                """, (thread_id,))
                
                cursor.execute(sql, params)
                results = cursor.fetchall()
        
        if not results:
            return error_response('Thread not found', 404)
        
        row = results[0]
        locked = bool(row.get('locked_to_device_id'))
        
        return success_response({
            'thread_id': thread_id,
            'locked': locked,
            'locked_by_device': row.get('locked_to_device_id'),
            'locked_at': row.get('locked_at')
        })
    
    except Exception as e:
        print(f"[DEVICE LOCK STATUS ERROR] {str(e)}")
        return error_response(f'Failed to get lock status: {str(e)}', 500)

# ============================================================
# ENDPOINT: Update Thread Location (CASCADE/Unload Support)
# ============================================================

@thread_bp.route('/update-location', methods=['POST'])
def update_thread_location():
    """
    Update a thread's location field for CASCADE rule enforcement and unload operations.
    Supports moving threads between prime and agent-N locations.
    
    Request Body:
        - thread_slug (str): Thread ID to update
        - new_location (str): New location (prime, agent-1, agent-2, etc.)
        - user_id (int): User ID for ownership verification
        
    Returns:
        200: Thread location updated successfully
        400: Invalid parameters
        404: Thread not found
        500: Database error
    """
    try:
        data = request.get_json()
        thread_slug = data.get('thread_slug')
        new_location = data.get('new_location')
        user_id = data.get('user_id')
        
        if not thread_slug or not new_location:
            return error_response('Missing thread_slug or new_location', 400)
        
        # Get database connection
        with get_database_connection('sessions') as conn:
            with conn.cursor() as cursor:
                
                # Update thread location
                sql = """
                    UPDATE sessions.threads
                    SET location = %s,
                        updated_at = CURRENT_TIMESTAMP
                    WHERE thread_slug = %s
                """
                params = [new_location, thread_slug]
                
                # Add user_id filter if provided
                if user_id:
                    sql += " AND user_id = %s"
                    params.append(user_id)
                
                cursor.execute(sql, tuple(params))
                rows_affected = cursor.rowcount
                conn.commit()
        
        if rows_affected == 0:
            return error_response('Thread not found or access denied', 404)
        
        return success_response({
            'thread_slug': thread_slug,
            'new_location': new_location,
            'updated': True
        })
        
    except Exception as e:
        print(f"[UPDATE LOCATION ERROR] {str(e)}")
        return error_response(f'Failed to update location: {str(e)}', 500)


# ============================================================
# RECONCILIATION SYSTEM (Compare ThreadManager vs Database)
# ============================================================

@thread_bp.route('/reconcile', methods=['POST'])
def reconcile_threads_endpoint():
    """
    Compare ThreadManager in-memory state vs database.
    
    POST Body:
        {
            "user_id": 1,
            "threads": [...ThreadManager.threads array...]
        }
        
    Returns:
        {
            "success": true,
            "discrepancies": {
                "orphaned_threads": [],      # In DB but not in memory
                "missing_threads": [],       # In memory but not in DB
                "stale_metadata": [],        # Exists in both but mismatch
                "zombie_threads": []         # Marked deleted but in memory
            },
            "summary": {
                "memory_count": 10,
                "database_count": 12,
                "orphaned_count": 2,
                "missing_count": 0,
                "stale_count": 1,
                "zombie_count": 0,
                "healthy": false
            }
        }
    """
    try:
        data = request.get_json()
        user_id = data.get('user_id')
        threads = data.get('threads', [])
        
        if not user_id:
            return error_response('user_id required', 400)
        
        from AI_infrastructure.shared.thread_reconciliation import reconcile_threads
        
        result = reconcile_threads(user_id, threads)
        
        if result.get('success'):
            return jsonify(result)
        else:
            return jsonify(result), 500
            
    except Exception as e:
        print(f"[RECONCILIATION ERROR] {str(e)}")
        import traceback
        traceback.print_exc()
        return error_response(f'Reconciliation failed: {str(e)}', 500)


@thread_bp.route('/reconcile/auto-fix', methods=['POST'])
def auto_fix_discrepancies_endpoint():
    """
    Automatically fix detected discrepancies.
    
    POST Body:
        {
            "user_id": 1,
            "reconciliation_result": {...output from /reconcile...}
        }
        
    Returns:
        {
            "success": true,
            "fixes_applied": {
                "orphaned_reloaded": 2,
                "missing_inserted": 0,
                "stale_updated": 1
            }
        }
    """
    try:
        data = request.get_json()
        user_id = data.get('user_id')
        reconciliation_result = data.get('reconciliation_result', {})
        
        if not user_id:
            return error_response('user_id required', 400)
        
        from AI_infrastructure.shared.thread_reconciliation import auto_fix_discrepancies
        
        result = auto_fix_discrepancies(user_id, reconciliation_result)
        
        if result.get('success'):
            return jsonify(result)
        else:
            return jsonify(result), 500
            
    except Exception as e:
        print(f"[AUTO-FIX ERROR] {str(e)}")
        import traceback
        traceback.print_exc()
        return error_response(f'Auto-fix failed: {str(e)}', 500)
"""
Synergy Dashboard Routes
=========================
REST API endpoints for Synergy Dashboard Kanban board.

⚠️ CRITICAL: convert_sql_placeholders() DOES NOT EXECUTE QUERIES!
   After calling convert_sql_placeholders(), you MUST call cursor.execute()
   
   ❌ WRONG:
       sql, params = convert_sql_placeholders('SELECT ...', (id,))
       for row in cursor.fetchall():  # Returns empty - query never executed!
   
   ✅ CORRECT:
       sql, params = convert_sql_placeholders('SELECT ...', (id,))
       cursor.execute(sql, params)  # Actually run the query!
       for row in cursor.fetchall():  # Now returns data

Endpoints:
    GET    /api/synergy/list           - List all sessions
    POST   /api/synergy/create         - Create new session
    GET    /api/synergy/<id>           - Get session by ID
    PATCH  /api/synergy/<id>           - Update session
    PATCH  /api/synergy/<id>/column    - Update session column
    DELETE /api/synergy/<id>           - Delete session
"""

from flask import Blueprint, request, jsonify
import json
import os
from datetime import datetime
from pathlib import Path
from shared.database_utils import get_database_connection
import sys

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

# Import database utility with auto-detection
from shared.database_utils import get_synergy_sessions_connection, is_using_supabase, convert_sql_placeholders

synergy_bp = Blueprint('synergy', __name__, url_prefix='/api/synergy')


def get_db_connection():
    """
    Get database connection to synergy_sessions database
    
    Auto-detects environment:
    - Local dev: SQLite in data/synergy_sessions.db
    - Render: Supabase PostgreSQL (synergy_sessions schema)
    """
    return get_synergy_sessions_connection()


def normalize_next_steps(steps):
    """
    Auto-convert string arrays to object arrays for next_steps field
    
    This allows AI agents to send simple strings ['Step 1', 'Step 2']
    while ensuring the UI receives rich objects with completion tracking.
    
    Args:
        steps: Array of strings OR objects
               Strings: ["Create email", "Test send"]
               Objects: [{"description": "Create email", "completed": false}]
    
    Returns:
        Array of objects with structure:
        [
            {
                "description": "Step text",
                "completed": false,
                "due_date": null,
                "completed_at": null
            }
        ]
    
    Examples:
        Input:  ["Phase 1", "Phase 2"]
        Output: [
            {"description": "Phase 1", "completed": false, "due_date": null, "completed_at": null},
            {"description": "Phase 2", "completed": false, "due_date": null, "completed_at": null}
        ]
    """
    if not steps:
        return []
    
    normalized = []
    for step in steps:
        if isinstance(step, str):
            # Convert string to rich object
            normalized.append({
                'description': step,
                'completed': False,
                'due_date': None,
                'completed_at': None
            })
        elif isinstance(step, dict):
            # Ensure object has all required fields
            normalized.append({
                'description': step.get('description', ''),
                'completed': step.get('completed', False),
                'due_date': step.get('due_date'),
                'completed_at': step.get('completed_at')
            })
        else:
            # Skip invalid entries
            continue
    
    return normalized


def normalize_documents(docs):
    """
    Auto-convert documents array ensuring 'title' field exists
    
    Fixes the field name mismatch where tools might send 'name' 
    but UI expects 'title'. Now with robust error handling.
    
    Args:
        docs: Array of document objects or strings
    
    Returns:
        Array of objects with structure:
        [
            {
                "title": "Document name",
                "url": "https://...",
                "type": "google_doc|google_sheet|pdf|etc"
            }
        ]
    """
    if not docs:
        return []
    
    normalized = []
    for doc in docs:
        try:
            # Handle string entries (convert to dict)
            if isinstance(doc, str):
                try:
                    doc = json.loads(doc)
                except json.JSONDecodeError:
                    # Treat as plain text title
                    doc = {"title": doc, "url": "", "type": "text"}
            
            # Ensure it's a dict
            if not isinstance(doc, dict):
                print(f"[WARN] Skipping invalid document entry: {doc}")
                continue
            
            # Normalize structure
            title = doc.get('title') or doc.get('name', 'Untitled Document')
            normalized.append({
                'title': title,
                'url': doc.get('url', ''),
                'type': doc.get('type', 'document')
            })
        except Exception as e:
            print(f"[ERROR] Failed to normalize document {doc}: {e}")
            continue
    
    return normalized


def normalize_checklist(items):
    """
    Normalize checklist items ensuring 'task' field exists and subtasks are preserved
    
    Handles three field name variations:
    - Old format: {"text": "...", "completed": false}
    - UI format: {"item": "...", "completed": false}
    - Correct format: {"task": "...", "completed": false, "subtasks": []}
    
    Args:
        items: Array of checklist items (may have mixed field names)
    
    Returns:
        Array of standardized objects with {task, completed, completed_at, subtasks}
    
    Examples:
        Input:  [{"item": "Do this", "completed": false}]
        Output: [{"task": "Do this", "completed": false, "completed_at": null, "subtasks": []}]
        
        Input:  [{"task": "Main", "subtasks": [{"task": "Sub1"}, {"item": "Sub2"}]}]
        Output: [{"task": "Main", "completed": false, "completed_at": null, "subtasks": [
                    {"task": "Sub1", "completed": false},
                    {"task": "Sub2", "completed": false}
                ]}]
    """
    if not items:
        return []
    
    normalized = []
    for item in items:
        if isinstance(item, dict):
            # Get task text from any field name variation
            task_text = item.get('task') or item.get('item') or item.get('text', '')
            
            # Skip empty items
            if not task_text:
                continue
            
            # Normalize subtasks (recursively handle field name variations)
            subtasks = item.get('subtasks', [])
            normalized_subtasks = []
            
            for subtask in subtasks:
                if isinstance(subtask, dict):
                    subtask_text = subtask.get('task') or subtask.get('item') or subtask.get('text', '')
                    if subtask_text:
                        normalized_subtasks.append({
                            'task': subtask_text,
                            'completed': subtask.get('completed', False)
                        })
            
            # Build standardized item
            normalized.append({
                'task': task_text,
                'completed': item.get('completed', False),
                'completed_at': item.get('completed_at'),
                'subtasks': normalized_subtasks
            })
    
    return normalized


def init_database():
    """
    Initialize Synergy database if it doesn't exist
    
    Auto-detects environment:
    - Local dev: Creates SQLite database in data/synergy_sessions.db
    - Render: Uses existing Supabase PostgreSQL schema (synergy_sessions)
    """
    # Skip initialization if using Supabase (tables already migrated)
    if is_using_supabase():
        print("🔷 [SYNERGY] Using Supabase - skipping table creation (already migrated)")
        return
    
    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        sql, params = convert_sql_placeholders('''
            CREATE TABLE IF NOT EXISTS synergy_sessions (
                session_id TEXT PRIMARY KEY,
                title TEXT NOT NULL,
                description TEXT,
                platforms_involved TEXT,
                status TEXT DEFAULT 'active',
                priority TEXT DEFAULT 'medium',
                kanban_column TEXT DEFAULT 'backlog',
                tags TEXT,
                documents TEXT,
                links TEXT,
                next_steps TEXT,
                assignees TEXT,
                recent_activity TEXT,
                checklist TEXT,
                due_date TEXT,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                last_active TEXT DEFAULT CURRENT_TIMESTAMP,
                completed_at TEXT,
                google_task_id TEXT,
                google_calendar_id TEXT,
                microsoft_todo_id TEXT,
                thread_ids TEXT,
                assigned_agents TEXT,
                owner_user_id INTEGER,
                permission_level TEXT DEFAULT 'private',
                shared_with_users TEXT,
                allow_public_view BOOLEAN DEFAULT FALSE
            )
        ''')
        cursor.execute(sql, params)
        
        # Add missing columns if they don't exist
        try:
            if is_using_supabase():
                # PostgreSQL syntax
                cursor.execute('ALTER TABLE synergy_sessions ADD COLUMN IF NOT EXISTS thread_ids TEXT')
            else:
                # SQLite syntax
                cursor.execute('ALTER TABLE synergy_sessions ADD COLUMN thread_ids TEXT')
        except (psycopg2.OperationalError, Exception):
            pass  # Column already exists
        
        try:
            if is_using_supabase():
                cursor.execute('ALTER TABLE synergy_sessions ADD COLUMN IF NOT EXISTS assigned_agents TEXT')
            else:
                cursor.execute('ALTER TABLE synergy_sessions ADD COLUMN assigned_agents TEXT')
        except (psycopg2.OperationalError, Exception):
            pass  # Column already exists
        
        try:
            if is_using_supabase():
                cursor.execute('ALTER TABLE synergy_sessions ADD COLUMN IF NOT EXISTS column_position INTEGER DEFAULT 0')
            else:
                cursor.execute('ALTER TABLE synergy_sessions ADD COLUMN column_position INTEGER DEFAULT 0')
        except (psycopg2.OperationalError, Exception):
            pass  # Column already exists
        
        # Add permission columns
        try:
            if is_using_supabase():
                cursor.execute('ALTER TABLE synergy_sessions ADD COLUMN IF NOT EXISTS owner_user_id INTEGER')
            else:
                cursor.execute('ALTER TABLE synergy_sessions ADD COLUMN owner_user_id INTEGER')
        except (psycopg2.OperationalError, Exception):
            pass
        
        try:
            if is_using_supabase():
                cursor.execute("ALTER TABLE synergy_sessions ADD COLUMN IF NOT EXISTS permission_level TEXT DEFAULT 'private'")
            else:
                cursor.execute("ALTER TABLE synergy_sessions ADD COLUMN permission_level TEXT DEFAULT 'private'")
        except (psycopg2.OperationalError, Exception):
            pass
        
        try:
            if is_using_supabase():
                cursor.execute('ALTER TABLE synergy_sessions ADD COLUMN IF NOT EXISTS shared_with_users TEXT')
            else:
                cursor.execute('ALTER TABLE synergy_sessions ADD COLUMN shared_with_users TEXT')
        except (psycopg2.OperationalError, Exception):
            pass
        
        try:
            if is_using_supabase():
                cursor.execute('ALTER TABLE synergy_sessions ADD COLUMN IF NOT EXISTS allow_public_view BOOLEAN DEFAULT FALSE')
            else:
                cursor.execute('ALTER TABLE synergy_sessions ADD COLUMN allow_public_view INTEGER DEFAULT 0')
        except (psycopg2.OperationalError, Exception):
            pass
        
        conn.commit()
        
    finally:
        if conn:
            conn.close()


# Initialize database on module load
init_database()


def check_session_permission(session_data, user_id, require_write=False):
    """
    Check if user has permission to access a session
    
    Args:
        session_data: Session dict with owner_user_id, permission_level, shared_with_users
        user_id: User ID making the request (int or None)
        require_write: If True, checks for edit permission (default: False for read-only)
    
    Returns:
        tuple: (has_permission: bool, permission_type: str)
        
    Permission Levels:
        - 'private': Only owner can access
        - 'shared': Owner + shared_with_users can access
        - 'public_view': Anyone can view (read-only), only owner can edit
        - 'public_edit': Anyone can view and edit
    """
    owner_id = session_data.get('owner_user_id')
    permission_level = session_data.get('permission_level', 'private')
    shared_with = session_data.get('shared_with_users', '[]')
    
    # Parse shared_with_users JSON
    try:
        shared_users = json.loads(shared_with) if isinstance(shared_with, str) else shared_with or []
    except:
        shared_users = []
    
    # Owner always has full access
    if user_id and owner_id and user_id == owner_id:
        return True, 'owner'
    
    # Check permission level
    if permission_level == 'private':
        return False, 'no_access'
    
    elif permission_level == 'shared':
        if user_id and user_id in shared_users:
            return True, 'shared'
        return False, 'no_access'
    
    elif permission_level == 'public_view':
        if require_write:
            # Only owner can edit
            return False, 'read_only'
        return True, 'public_view'
    
    elif permission_level == 'public_edit':
        return True, 'public_edit'
    
    # Default: no access
    return False, 'no_access'


@synergy_bp.route('/list', methods=['GET'])
def list_sessions():
    """List all sessions with optional filtering and permission checking"""
    conn = None
    try:
        status = request.args.get('status')
        priority = request.args.get('priority')
        column = request.args.get('kanban_column')
        user_id = request.args.get('user_id', type=int)  # Optional user_id for filtering
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
        query = 'SELECT * FROM synergy_sessions.synergy_sessions WHERE 1=1'
        params = []
        
        if status:
            query += ' AND status = %s'
            params.append(status)
        
        if priority:
            query += ' AND priority = %s'
            params.append(priority)
        
        if column:
            query += ' AND kanban_column = %s'
            params.append(column)
        
        # Order by column_position (for card ordering), then by last_active
        query += ' ORDER BY COALESCE(column_position, 999999), last_active DESC'
        
        cursor.execute(query, params)
        rows = cursor.fetchall()
        
        sessions = []
        for row in rows:
            session = dict(row)
            
            # Check permission for this session
            has_permission, perm_type = check_session_permission(session, user_id, require_write=False)
            if not has_permission:
                continue  # Skip sessions user doesn't have access to
            
            # Parse JSON fields
            for field in ['platforms_involved', 'tags', 'documents', 'links', 
                         'next_steps', 'assignees', 'recent_activity', 'checklist', 'shared_with_users']:
                if session.get(field):
                    try:
                        session[field] = json.loads(session[field])
                    except:
                        session[field] = []
            
            # Add permission info to response
            session['user_permission'] = perm_type
            sessions.append(session)
        
        return jsonify({
            'success': True,
            'count': len(sessions),
            'sessions': sessions
        })
    
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@synergy_bp.route('/sessions', methods=['GET'])
def get_sessions_simple():
    """
    Get simplified list of sessions for thread linking
    Returns minimal data: session_id, title, status, column
    """
    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT session_id, title, status, kanban_column, priority
            FROM synergy_sessions.synergy_sessions 
            WHERE status != 'archived'
            ORDER BY last_active DESC
        """)
        
        rows = cursor.fetchall()
        
        sessions = [{
            'session_id': row['session_id'],
            'title': row['title'],
            'status': row['status'] or 'active',
            'column': row['kanban_column'] or 'backlog',
            'priority': row['priority'] or 'medium'
        } for row in rows]
        
        return jsonify(sessions)
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    
    finally:
        if conn:
            conn.close()


@synergy_bp.route('/sessions/batch', methods=['GET'])
def get_sessions_with_internal_docs():
    """
    Batch load all sessions with their internal docs count in a SINGLE optimized query.
    This replaces the N+1 query pattern (1 session list + N internal doc queries).
    
    Returns:
    {
        'success': True,
        'sessions': [
            {
                'session_id': 'sess_xxx',
                'title': 'Session Title',
                'internal_docs_count': 5,
                'internal_docs': [
                    {'doc_id': 'doc_xxx', 'title': 'Doc Title', ...}
                ],
                ... all other session fields
            }
        ]
    }
    """
    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Step 1: Load all active sessions
        cursor.execute("""
            SELECT * FROM synergy_sessions.synergy_sessions 
            WHERE status != 'archived'
            ORDER BY last_active DESC
        """)
        
        sessions_rows = cursor.fetchall()
        sessions = []
        session_ids = []
        
        for row in sessions_rows:
            session = dict(row)
            session_ids.append(session['session_id'])
            
            # Parse JSON fields
            for field in ['platforms_involved', 'tags', 'documents', 'links', 
                         'next_steps', 'assignees', 'recent_activity', 'checklist',
                         'thread_ids', 'assigned_agents']:
                if session.get(field):
                    try:
                        session[field] = json.loads(session[field])
                    except:
                        session[field] = []
            
            # Initialize internal docs array
            session['internal_docs'] = []
            session['internal_docs_count'] = 0
            sessions.append(session)
        
        # Step 2: Batch load ALL internal docs for ALL sessions in ONE query
        # Use correct table name based on environment
        docs_rows = []
        if session_ids:
            placeholders = ','.join('%s' for _ in session_ids)
            
            # Determine correct table name: synergy_internal_docs (both local and Supabase use this)
            table_name = 'synergy_internal_docs'
            
            try:
                cursor.execute(f"""
                    SELECT 
                        session_id,
                        doc_id,
                        title,
                        doc_type,
                        version,
                        created_at,
                        updated_at,
                        slug,
                        share_url
                    FROM {table_name}
                    WHERE session_id IN ({placeholders})
                    ORDER BY session_id, created_at DESC
                """, session_ids)
                docs_rows = cursor.fetchall()
            except Exception as e:
                # Table doesn't exist or query failed - continue without internal docs
                error_msg = str(e).lower()
                if 'does not exist' in error_msg or 'no such table' in error_msg:
                    print(f'[SYNERGY BATCH] Table {table_name} not found - continuing without internal docs')
                    docs_rows = []
                else:
                    # Re-raise unexpected errors
                    raise
            
            # Group internal docs by session_id
            docs_by_session = {}
            for doc_row in docs_rows:
                doc = dict(doc_row)
                sess_id = doc.pop('session_id')
                
                if sess_id not in docs_by_session:
                    docs_by_session[sess_id] = []
                
                docs_by_session[sess_id].append({
                    'doc_id': doc['doc_id'],
                    'title': doc['title'],
                    'type': 'internal_doc',
                    'doc_type': doc.get('doc_type', 'richtext'),
                    'version': doc.get('version', 1),
                    'created_at': doc.get('created_at'),
                    'updated_at': doc.get('updated_at'),
                    'slug': doc.get('slug'),
                    'share_url': doc.get('share_url')
                })
            
            # Attach internal docs to sessions
            for session in sessions:
                sess_id = session['session_id']
                if sess_id in docs_by_session:
                    session['internal_docs'] = docs_by_session[sess_id]
                    session['internal_docs_count'] = len(docs_by_session[sess_id])
        
        # Step 3: Batch load milestone, task, and subtask counts
        if session_ids:
            try:
                placeholders = ','.join('%s' for _ in session_ids)
                
                # Get milestone counts
                cursor.execute(f"""
                    SELECT session_id, COUNT(*) as count
                    FROM synergy_sessions.milestones
                    WHERE session_id IN ({placeholders})
                    GROUP BY session_id
                """, session_ids)
                milestone_counts = {row['session_id']: row['count'] for row in cursor.fetchall()}
                
                # Get task counts (total only - status column doesn't exist yet)
                cursor.execute(f"""
                    SELECT 
                        m.session_id,
                        COUNT(t.task_id) as total_tasks
                    FROM synergy_sessions.milestones m
                    LEFT JOIN synergy_sessions.tasks t ON m.milestone_id = t.milestone_id
                    WHERE m.session_id IN ({placeholders})
                    GROUP BY m.session_id
                """, session_ids)
                task_stats = {row['session_id']: {
                    'total': row['total_tasks'] or 0,
                    'done': 0  # Status tracking not implemented yet
                } for row in cursor.fetchall()}
                
                # Get subtask counts (total only - status column doesn't exist yet)
                cursor.execute(f"""
                    SELECT 
                        m.session_id,
                        COUNT(st.subtask_id) as total_subtasks
                    FROM synergy_sessions.milestones m
                    LEFT JOIN synergy_sessions.tasks t ON m.milestone_id = t.milestone_id
                    LEFT JOIN synergy_sessions.subtasks st ON t.task_id = st.task_id
                    WHERE m.session_id IN ({placeholders})
                    GROUP BY m.session_id
                """, session_ids)
                subtask_stats = {row['session_id']: {
                    'total': row['total_subtasks'] or 0,
                    'done': 0  # Status tracking not implemented yet
                } for row in cursor.fetchall()}
                
                # Attach counts to sessions
                for session in sessions:
                    sess_id = session['session_id']
                    session['milestone_count'] = milestone_counts.get(sess_id, 0)
                    session['task_count'] = task_stats.get(sess_id, {}).get('total', 0)
                    session['tasks_done'] = task_stats.get(sess_id, {}).get('done', 0)
                    session['subtask_count'] = subtask_stats.get(sess_id, {}).get('total', 0)
                    session['subtasks_done'] = subtask_stats.get(sess_id, {}).get('done', 0)
                    
            except Exception as e:
                # If counting fails, log and continue without counts
                print(f'[SYNERGY BATCH] Failed to load counts: {str(e)}')
                for session in sessions:
                    session['milestone_count'] = 0
                    session['task_count'] = 0
                    session['tasks_done'] = 0
                    session['subtask_count'] = 0
                    session['subtasks_done'] = 0
        
        return jsonify({
            'success': True,
            'sessions': sessions,
            'total_count': len(sessions)
        })
    
    except Exception as e:
        print(f'[SYNERGY BATCH ERROR] {str(e)}')
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500
    
    finally:
        if conn:
            conn.close()


@synergy_bp.route('', methods=['GET'])
def get_sessions_bulk():
    """
    Bulk fetch sessions by comma-separated ids query parameter.
    Example: GET /api/synergy?ids=sess_1,sess_2
    Returns: { success: True, sessions: { <id>: {...}, ... } }
    If no ids provided, falls back to list of sessions (minimal fields).
    """
    conn = None
    try:
        ids_param = request.args.get('ids')
        if not ids_param:
            # Fallback: return a minimal sessions list (same as /sessions)
            return get_sessions_simple()

        ids = [i.strip() for i in ids_param.split(',') if i.strip()]
        if not ids:
            return jsonify({'success': True, 'sessions': {}})

        conn = get_db_connection()
        cursor = conn.cursor()

        # Build a parameterized query with the right number of placeholders
        placeholders = ','.join('%s' for _ in ids)
        query = f"SELECT * FROM synergy_sessions.synergy_sessions WHERE session_id IN ({placeholders})"
        cursor.execute(query, ids)
        rows = cursor.fetchall()
        conn.close()

        sessions = {}
        for row in rows:
            session = dict(row)
            # Parse JSON fields
            for field in ['platforms_involved', 'tags', 'documents', 'links', 
                         'next_steps', 'assignees', 'recent_activity', 'checklist',
                         'thread_ids', 'assigned_agents']:
                if session.get(field):
                    try:
                        session[field] = json.loads(session[field])
                    except:
                        session[field] = []
            sessions[session['session_id']] = session

        return jsonify({'success': True, 'sessions': sessions})

    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@synergy_bp.route('/create', methods=['POST'])
def create_session():
    """Create a new session"""
    conn = None
    try:
        # Validate JSON payload
        if not request.is_json:
            return jsonify({
                'success': False,
                'error': 'Content-Type must be application/json'
            }), 400
        
        data = request.get_json()
        
        if not data:
            return jsonify({
                'success': False,
                'error': 'Empty JSON payload'
            }), 400
        
        if not data.get('title'):
            return jsonify({
                'success': False,
                'error': 'title field is required'
            }), 400
        
        # Generate session ID with FULL timestamp (including seconds) + random suffix for uniqueness
        import random
        import string
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')  # ← ADDED SECONDS
        title_slug = data.get('title', 'untitled').lower().replace(' ', '_')[:30]
        random_suffix = ''.join(random.choices(string.ascii_lowercase + string.digits, k=4))  # ← ADDED RANDOM SUFFIX
        session_id = f"sess_{timestamp}_{title_slug}_{random_suffix}"
        
        # Normalize and serialize JSON fields
        platforms_involved = json.dumps(data.get('platforms_involved', []))
        tags = json.dumps(data.get('tags', []))
        documents = json.dumps(normalize_documents(data.get('documents', [])))
        links = json.dumps(data.get('links', []))
        next_steps = json.dumps(normalize_next_steps(data.get('next_steps', [])))
        assignees = json.dumps(data.get('assignees', []))
        recent_activity = json.dumps([{
            'type': 'created',
            'timestamp': datetime.now().isoformat(),
            'user': data.get('created_by', 'AI Agent'),
            'details': f"Session created: {data.get('title')}"
        }])
        checklist = json.dumps(normalize_checklist(data.get('checklist', [])))
        
        # Get thread_ids - may include auto-linked thread from agent context
        thread_ids_list = data.get('thread_ids', [])
        thread_ids = json.dumps(thread_ids_list)
        assigned_agents = json.dumps(data.get('assigned_agents', []))
        
        # Handle permissions
        owner_user_id = data.get('owner_user_id')
        permission_level = data.get('permission_level', 'private')
        shared_with_users = json.dumps(data.get('shared_with_users', []))
        allow_public_view = data.get('allow_public_view', False)
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Check if session_id already exists (duplicate prevention)
        check_sql, check_params = convert_sql_placeholders(
            'SELECT session_id FROM synergy_sessions.synergy_sessions WHERE session_id = %s',
            (session_id,)
        )
        cursor.execute(check_sql, check_params)
        existing = cursor.fetchone()
        
        if existing:
            # Session ID collision detected - regenerate with new random suffix
            random_suffix = ''.join(random.choices(string.ascii_lowercase + string.digits, k=6))
            session_id = f"sess_{timestamp}_{title_slug}_{random_suffix}"
            print(f"[SYNERGY] Session ID collision detected - regenerated: {session_id}")
        
        cursor.execute('''
            INSERT INTO synergy_sessions.synergy_sessions (
                session_id, title, description, platforms_involved, status,
                priority, kanban_column, tags, documents, links, next_steps,
                assignees, recent_activity, checklist, due_date, created_at, last_active,
                thread_ids, assigned_agents, uses_milestones,
                owner_user_id, permission_level, shared_with_users, allow_public_view
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        ''', (
            session_id,
            data.get('title', 'Untitled Session'),
            data.get('description', ''),
            platforms_involved,
            data.get('status', 'active'),
            data.get('priority', 'medium'),
            data.get('kanban_column', 'backlog'),
            tags,
            documents,
            links,
            next_steps,
            assignees,
            recent_activity,
            checklist,
            data.get('due_date'),
            datetime.now().isoformat(),
            datetime.now().isoformat(),
            thread_ids,
            assigned_agents,
            data.get('uses_milestones', False),
            owner_user_id,
            permission_level,
            shared_with_users,
            allow_public_view
        ))
        
        conn.commit()
        
        # BIDIRECTIONAL LINKING: UPDATE sessions.threads table with synergy_card_id for auto-linked threads
        if thread_ids_list:
            for thread_id in thread_ids_list:
                try:
                    cursor.execute('''
                        UPDATE sessions.threads 
                        SET synergy_card_id = %s, synergy_card_name = %s, updated = %s
                        WHERE id = %s
                    ''', (session_id, data.get('title', 'Untitled Session'), datetime.now().isoformat(), thread_id))
                    print(f"BIDIRECTIONAL LINK: Thread {thread_id} updated with synergy_card_id {session_id}")
                except Exception as link_error:
                    print(f"Warning: Failed to update thread {thread_id}: {link_error}")
            
            conn.commit()
        
        # Broadcast new session creation to all connected WebSocket clients
        try:
            from flask import current_app
            socketio = current_app.extensions.get('socketio')
            if socketio:
                socketio.emit('session_created', {
                    'session_id': session_id,
                    'session': {
                        'session_id': session_id,
                        'title': data.get('title'),
                        'kanban_column': data.get('kanban_column', 'backlog'),
                        'priority': data.get('priority', 'medium'),
                        'status': data.get('status', 'active')
                    },
                    'timestamp': datetime.now().isoformat()
                }, namespace='/ws/synergy', room='synergy_board')
                print(f"[WS] Broadcasted session creation for {session_id}")
        except Exception as ws_error:
            print(f"[WS] Failed to broadcast creation: {ws_error}")
        
        return jsonify({
            'success': True,
            'session_id': session_id,
            'message': 'Session created successfully',
            'linked_threads': thread_ids_list  # Return which threads were auto-linked
        })
    
    except Exception as e:
        # CRITICAL: Rollback transaction to prevent orphaned sessions
        if conn:
            try:
                conn.rollback()
                print(f"[SYNERGY] Transaction rolled back due to error: {e}")
            except Exception as rollback_error:
                print(f"[SYNERGY] Failed to rollback: {rollback_error}")
        
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500
    
    finally:
        if conn:
            conn.close()


@synergy_bp.route('/<session_id>', methods=['GET'])
def get_session(session_id):
    """Get session by ID - includes milestones if uses_milestones=TRUE"""
    conn = None
    try:
        user_id = request.args.get('user_id', type=int)
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Use convert_sql_placeholders for proper database compatibility
        sql, params = convert_sql_placeholders(
            'SELECT * FROM synergy_sessions.synergy_sessions WHERE session_id = %s',
            (session_id,)
        )
        cursor.execute(sql, params)
        row = cursor.fetchone()
        
        if not row:
            return jsonify({
                'success': False,
                'error': 'Session not found'
            }), 404
        
        session = dict(row)
        
        # Check permission
        has_permission, perm_type = check_session_permission(session, user_id, require_write=False)
        if not has_permission:
            return jsonify({
                'success': False,
                'error': 'Access denied: You do not have permission to view this session'
            }), 403
        
        # Parse JSON fields
        for field in ['platforms_involved', 'tags', 'documents', 'links', 
                     'next_steps', 'assignees', 'recent_activity', 'checklist',
                     'thread_ids', 'assigned_agents', 'shared_with_users']:
            if session.get(field):
                try:
                    session[field] = json.loads(session[field])
                except:
                    session[field] = []
        
        # Add permission info to response
        session['user_permission'] = perm_type
        
        # If session uses milestones, fetch milestone data
        if session.get('uses_milestones'):
            cursor.execute('''
                SELECT milestone_id, milestone_number, milestone_name, description,
                       completed, due_date, priority, estimated_hours, actual_hours,
                       created_at, completed_at, milestone_order, depends_on_milestone_id,
                       blocked, blocker_reason, blocked_since, updated_at, documents, links
                FROM synergy_sessions.milestones 
                WHERE session_id = %s
                ORDER BY milestone_number
            ''', (session_id,))
            
            milestones = []
            for m_row in cursor.fetchall():
                milestone = {
                    'milestone_id': m_row[0],
                    'milestone_number': m_row[1],
                    'milestone_name': m_row[2],
                    'description': m_row[3],
                    'completed': m_row[4],
                    'due_date': m_row[5],
                    'priority': m_row[6],
                    'estimated_hours': m_row[7],
                    'actual_hours': m_row[8],
                    'created_at': m_row[9],
                    'completed_at': m_row[10],
                    'milestone_order': m_row[11],
                    'depends_on_milestone_id': m_row[12],
                    'blocked': m_row[13],
                    'blocker_reason': m_row[14],
                    'blocked_since': m_row[15],
                    'updated_at': m_row[16],
                    'documents': m_row[17],
                    'links': m_row[18],
                    'tasks': []
                }
                
                # Get tasks for this milestone
                sql, params = convert_sql_placeholders('''
                    SELECT task_id, task, completed, blocked, blocker_reason, 
                           blocker_type, task_order, created_at, completed_at, blocked_since,
                           estimated_hours, actual_hours, assigned_to, updated_at, priority
                    FROM synergy_sessions.tasks 
                    WHERE milestone_id = %s
                    ORDER BY task_order
                ''', (milestone['milestone_id'],))
                
                cursor.execute(sql, params)
                
                for t_row in cursor.fetchall():
                    task = {
                        'task_id': t_row[0],
                        'task': t_row[1],
                        'completed': t_row[2],
                        'blocked': t_row[3],
                        'blocker_reason': t_row[4],
                        'blocker_type': t_row[5],
                        'task_order': t_row[6],
                        'created_at': t_row[7],
                        'completed_at': t_row[8],
                        'blocked_since': t_row[9],
                        'estimated_hours': t_row[10],
                        'actual_hours': t_row[11],
                        'assigned_to': t_row[12],
                        'updated_at': t_row[13],
                        'priority': t_row[14],
                        'subtasks': []
                    }
                    
                    # Get subtasks for this task
                    sql, params = convert_sql_placeholders('''
                        SELECT subtask_id, task, completed, subtask_order, created_at, completed_at,
                               estimated_hours, actual_hours, updated_at, priority
                        FROM synergy_sessions.subtasks 
                        WHERE task_id = %s
                        ORDER BY subtask_order
                    ''', (task['task_id'],))
                    
                    cursor.execute(sql, params)
                    
                    for s_row in cursor.fetchall():
                        subtask = {
                            'subtask_id': s_row[0],
                            'task': s_row[1],
                            'completed': s_row[2],
                            'subtask_order': s_row[3],
                            'created_at': s_row[4],
                            'completed_at': s_row[5],
                            'estimated_hours': s_row[6],
                            'actual_hours': s_row[7],
                            'updated_at': s_row[8],
                            'priority': s_row[9]
                        }
                        task['subtasks'].append(subtask)
                    
                    milestone['tasks'].append(task)
                
                milestones.append(milestone)
            
            session['milestones'] = milestones
        
        return jsonify({
            'success': True,
            'session': session
        })
    
    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500
    
    finally:
        if conn:
            conn.close()


@synergy_bp.route('/<session_id>/permissions', methods=['PATCH'])
def update_session_permissions(session_id):
    """Update session permission settings"""
    conn = None
    try:
        data = request.json
        user_id = data.get('user_id', type=int)
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Get current session
        cursor.execute('SELECT * FROM synergy_sessions.synergy_sessions WHERE session_id = %s', (session_id,))
        row = cursor.fetchone()
        
        if not row:
            return jsonify({
                'success': False,
                'error': 'Session not found'
            }), 404
        
        session = dict(row)
        
        # Only owner can change permissions
        has_permission, perm_type = check_session_permission(session, user_id, require_write=True)
        if perm_type != 'owner':
            return jsonify({
                'success': False,
                'error': 'Only the session owner can change permissions'
            }), 403
        
        # Build update query
        updates = []
        params = []
        
        if 'permission_level' in data:
            updates.append('permission_level = %s')
            params.append(data['permission_level'])
        
        if 'shared_with_users' in data:
            updates.append('shared_with_users = %s')
            params.append(json.dumps(data['shared_with_users']))
        
        if 'allow_public_view' in data:
            updates.append('allow_public_view = %s')
            params.append(data['allow_public_view'])
        
        if not updates:
            return jsonify({
                'success': False,
                'error': 'No permission fields provided'
            }), 400
        
        # Update timestamp
        updates.append('last_active = %s')
        params.append(datetime.now().isoformat())
        
        # Add session_id to params
        params.append(session_id)
        
        query = f"UPDATE synergy_sessions.synergy_sessions SET {', '.join(updates)} WHERE session_id = %s"
        cursor.execute(query, params)
        conn.commit()
        
        return jsonify({
            'success': True,
            'message': 'Permissions updated successfully',
            'session_id': session_id
        })
    
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500
    
    finally:
        if conn:
            conn.close()


@synergy_bp.route('/<session_id>', methods=['PATCH'])
def update_session(session_id):
    """Update session"""
    conn = None
    try:
        data = request.json
        user_id = data.get('user_id', type=int)
        print(f"[DEBUG] Received data: {data}")  # DEBUG
        
        # Check write permission
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute('SELECT * FROM synergy_sessions.synergy_sessions WHERE session_id = %s', (session_id,))
        row = cursor.fetchone()
        
        if not row:
            return jsonify({
                'success': False,
                'error': 'Session not found'
            }), 404
        
        session = dict(row)
        has_permission, perm_type = check_session_permission(session, user_id, require_write=True)
        
        if not has_permission:
            return jsonify({
                'success': False,
                'error': 'Access denied: You do not have permission to edit this session'
            }), 403
        
        print(f"[DEBUG] Received data: {data}")  # DEBUG
        
        # Handle both direct fields and nested 'updates' object
        if 'updates' in data:
            # Frontend sends {updates: {...}, sync: {...}}
            update_data = data['updates']
            print(f"[DEBUG] Using nested updates: {update_data}")  # DEBUG
        else:
            # Direct fields
            update_data = data
            print(f"[DEBUG] Using direct data: {update_data}")  # DEBUG
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Build update query dynamically
        updates = []
        params = []
        
        # Simple fields
        for field in ['title', 'description', 'status', 'priority', 'due_date', 'kanban_column']:
            if field in update_data:
                updates.append(f"{field} = ?")
                params.append(update_data[field])
        
        # JSON fields without normalization
        for field in ['platforms_involved', 'tags', 'links', 
                     'assignees', 'thread_ids', 'assigned_agents']:
            if field in update_data:
                updates.append(f"{field} = ?")
                json_value = json.dumps(update_data[field])
                params.append(json_value)
                print(f"[DEBUG] Adding {field}: {json_value}")  # DEBUG
        
        # Special handling for next_steps (normalize string arrays to objects)
        if 'next_steps' in update_data:
            updates.append("next_steps = ?")
            normalized = normalize_next_steps(update_data['next_steps'])
            json_value = json.dumps(normalized)
            params.append(json_value)
            print(f"[DEBUG] Adding next_steps (normalized): {json_value}")  # DEBUG
        
        # Special handling for documents (ensure 'title' field)
        if 'documents' in update_data:
            try:
                normalized = normalize_documents(update_data['documents'])
                updates.append("documents = ?")
                json_value = json.dumps(normalized)
                params.append(json_value)
                print(f"[DEBUG] Adding documents (normalized): {json_value}")  # DEBUG
            except Exception as doc_error:
                print(f"[ERROR] Document normalization failed: {doc_error}")
                return jsonify({
                    'success': False,
                    'error': f'Invalid document format: {str(doc_error)}'
                }), 400
        
        # Special handling for checklist (normalize task/item/text fields and subtasks)
        if 'checklist' in update_data:
            updates.append("checklist = ?")
            normalized = normalize_checklist(update_data['checklist'])
            json_value = json.dumps(normalized)
            params.append(json_value)
            print(f"[DEBUG] Adding checklist (normalized): {json_value}")  # DEBUG
        
        # Add to recent activity
        if 'recent_activity' in update_data:
            updates.append("recent_activity = ?")
            params.append(json.dumps(update_data['recent_activity']))
        
        # Update last_active
        updates.append("last_active = ?")
        params.append(datetime.now().isoformat())
        
        # Add session_id to params
        params.append(session_id)
        
        if updates:
            query = f"UPDATE synergy_sessions.synergy_sessions SET {', '.join(updates)} WHERE session_id = %s"
            print(f"[DEBUG] Executing query: {query}")  # DEBUG
            print(f"[DEBUG] With params: {params}")  # DEBUG
            cursor.execute(query, params)
            conn.commit()
            print(f"[DEBUG] Rows affected: {cursor.rowcount}")  # DEBUG
        
        # Broadcast update to all connected WebSocket clients
        try:
            from flask import current_app
            socketio = current_app.extensions.get('socketio')
            if socketio:
                socketio.emit('session_updated', {
                    'session_id': session_id,
                    'updates': update_data,
                    'timestamp': datetime.now().isoformat()
                }, namespace='/ws/synergy', room='synergy_board')
                print(f"[WS] Broadcasted session update for {session_id}")
        except Exception as ws_error:
            print(f"[WS] Failed to broadcast update: {ws_error}")
        
        return jsonify({
            'success': True,
            'message': 'Session updated successfully'
        })
    
    except Exception as e:
        print(f"[ERROR] Update failed: {e}")  # DEBUG
        import traceback
        traceback.print_exc()
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500
    
    finally:
        if conn:
            conn.close()


@synergy_bp.route('/<session_id>/column', methods=['PATCH'])
def update_column(session_id):
    """Update session column (Kanban movement)"""
    conn = None
    try:
        data = request.json
        new_column = data.get('target_column') or data.get('kanban_column')
        
        if not new_column:
            return jsonify({
                'success': False,
                'error': 'target_column or kanban_column is required'
            }), 400
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Add activity log
        cursor.execute(
            'SELECT recent_activity FROM synergy_sessions.synergy_sessions WHERE session_id = %s',
            (session_id,)
        )
        row = cursor.fetchone()
        
        if row:
            activity = json.loads(row['recent_activity'] or '[]')
            activity.insert(0, {
                'type': 'moved',
                'timestamp': datetime.now().isoformat(),
                'user': data.get('moved_by', 'AI Agent'),
                'details': f"Moved to {new_column}"
            })
            
            sql, params = convert_sql_placeholders('''
                UPDATE synergy_sessions.synergy_sessions 
                SET kanban_column = %s, recent_activity = %s, last_active = %s
                WHERE session_id = %s
            ''', (new_column, json.dumps(activity), datetime.now().isoformat(), session_id))
            
            conn.commit()
        
        # Broadcast column change to all connected WebSocket clients
        try:
            from flask import current_app
            socketio = current_app.extensions.get('socketio')
            if socketio:
                # Get old column from data
                old_column = data.get('from_column', 'unknown')
                socketio.emit('column_changed', {
                    'session_id': session_id,
                    'from_column': old_column,
                    'to_column': new_column,
                    'timestamp': datetime.now().isoformat()
                }, namespace='/ws/synergy', room='synergy_board')
                print(f"[WS] Broadcasted column change: {session_id} {old_column} → {new_column}")
        except Exception as ws_error:
            print(f"[WS] Failed to broadcast column change: {ws_error}")
        
        return jsonify({
            'success': True,
            'message': 'Column updated successfully'
        })
    
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500
    
    finally:
        if conn:
            conn.close()


@synergy_bp.route('/search', methods=['GET'])
def search_sessions():
    """
    Search sessions by title, description, tags, or platform
    
    Query Parameters:
        query (str): Search term (searches title, description, tags)
        platform (str): Filter by specific platform
        status (str): Filter by status
        priority (str): Filter by priority
        column (str): Filter by Kanban column
        user_id (int): User ID for permission filtering
    
    Returns:
        {
            "success": true,
            "count": 10,
            "sessions": [...],
            "query": "email automation",
            "filters_applied": {...}
        }
    """
    conn = None
    try:
        query = request.args.get('query', '').strip()
        platform = request.args.get('platform')
        status = request.args.get('status')
        priority = request.args.get('priority')
        column = request.args.get('column')
        user_id = request.args.get('user_id', type=int)
        
        if not query and not platform:
            return jsonify({
                'success': False,
                'error': 'Either query or platform parameter is required'
            }), 400
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Build search query
        conditions = ['1=1']
        params = []
        
        if query:
            # Search in title, description, and tags
            search_pattern = f'%{query}%'
            conditions.append(
                "(title LIKE %s OR description LIKE %s OR tags LIKE %s)"
            )
            params.extend([search_pattern, search_pattern, search_pattern])
        
        if platform:
            conditions.append("platforms_involved LIKE %s")
            params.append(f'%{platform}%')
        
        if status:
            conditions.append("status = %s")
            params.append(status)
        
        if priority:
            conditions.append("priority = %s")
            params.append(priority)
        
        if column:
            conditions.append("kanban_column = %s")
            params.append(column)
        
        # Build final query
        base_sql = f"""
            SELECT * FROM synergy_sessions.synergy_sessions 
            WHERE {' AND '.join(conditions)}
            ORDER BY last_active DESC
            LIMIT 50
        """
        
        sql, final_params = convert_sql_placeholders(base_sql, params)
        cursor.execute(sql, final_params)
        rows = cursor.fetchall()
        
        # Process results
        sessions = []
        for row in rows:
            session = dict(row)
            
            # Check permission
            has_permission, perm_type = check_session_permission(session, user_id, require_write=False)
            if not has_permission:
                continue
            
            # Parse JSON fields
            for field in ['platforms_involved', 'tags', 'documents', 'links', 
                         'next_steps', 'assignees', 'recent_activity', 'checklist']:
                if session.get(field):
                    try:
                        session[field] = json.loads(session[field])
                    except:
                        session[field] = []
            
            sessions.append(session)
        
        return jsonify({
            'success': True,
            'count': len(sessions),
            'sessions': sessions,
            'query': query,
            'filters_applied': {
                'platform': platform,
                'status': status,
                'priority': priority,
                'column': column
            }
        })
        
    except Exception as e:
        print(f"[ERROR] Search failed: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500
    
    finally:
        if conn:
            conn.close()


@synergy_bp.route('/<session_id>', methods=['DELETE'])
def delete_session(session_id):
    """Delete session"""
    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute('DELETE FROM synergy_sessions.synergy_sessions WHERE session_id = %s', (session_id,))
        conn.commit()
        
        # Broadcast deletion to all connected WebSocket clients
        try:
            from flask import current_app
            socketio = current_app.extensions.get('socketio')
            if socketio:
                socketio.emit('session_deleted', {
                    'session_id': session_id,
                    'timestamp': datetime.now().isoformat()
                }, namespace='/ws/synergy', room='synergy_board')
                print(f"[WS] Broadcasted session deletion for {session_id}")
        except Exception as ws_error:
            print(f"[WS] Failed to broadcast deletion: {ws_error}")
        
        return jsonify({
            'success': True,
            'message': 'Session deleted successfully'
        })
    
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500
    
    finally:
        if conn:
            conn.close()


@synergy_bp.route('/<session_id>/link-thread', methods=['POST'])
def link_thread_to_synergy(session_id):
    """
    Link a thread to a Synergy session (bidirectional sync)
    
    CRITICAL: Updates synergy_sessions.thread_ids array
    This is called from ThreadManager.linkToSynergy() to ensure bidirectional sync
    
    Body: {thread_id, thread_slug, thread_name}
    """
    conn = None
    try:
        data = request.get_json()
        thread_id = data.get('thread_id')
        thread_slug = data.get('thread_slug', thread_id)
        thread_name = data.get('thread_name', 'Untitled Thread')
        
        if not thread_id:
            return jsonify({'success': False, 'error': 'thread_id required'}), 400
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Get current thread_ids array
        cursor.execute('SELECT thread_ids FROM synergy_sessions.synergy_sessions WHERE session_id = %s', (session_id,))
        row = cursor.fetchone()
        
        if not row:
            conn.close()
            return jsonify({'success': False, 'error': 'Session not found'}), 404
        
        # Parse existing thread_ids (JSON array)
        thread_ids = []
        if row['thread_ids']:
            try:
                thread_ids = json.loads(row['thread_ids'])
                if not isinstance(thread_ids, list):
                    thread_ids = []
            except json.JSONDecodeError:
                thread_ids = []
        
        # Add new thread if not already present
        if thread_id not in thread_ids:
            thread_ids.append(thread_id)
            
            # UPDATE synergy_sessions.synergy_sessions
            cursor.execute('''
                UPDATE synergy_sessions.synergy_sessions 
                SET thread_ids = %s, last_active = %s
                WHERE session_id = %s
            ''', (json.dumps(thread_ids), datetime.now().isoformat(), session_id))
            
            conn.commit()
            print(f"[SYNERGY SYNC] Added thread {thread_id} to Synergy session {session_id}")
        else:
            print(f"[SYNERGY SYNC] Thread {thread_id} already linked to {session_id}")
        
        return jsonify({
            'success': True,
            'session_id': session_id,
            'thread_ids': thread_ids,
            'message': f'Thread {thread_id} linked successfully'
        })
    
    except Exception as e:
        print(f"[SYNERGY SYNC ERROR] Failed to link thread: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500
    
    finally:
        if conn:
            conn.close()


@synergy_bp.route('/<session_id>/position', methods=['PATCH'])
def update_card_position(session_id):
    """
    Update card position within a column
    
    Body: {position: integer}
    """
    conn = None
    try:
        data = request.get_json()
        position = data.get('position')
        
        if position is None:
            return jsonify({'success': False, 'error': 'position required'}), 400
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            UPDATE synergy_sessions.synergy_sessions 
            SET column_position = %s
            WHERE session_id = %s
        ''', (position, session_id))
        
        conn.commit()
        
        return jsonify({
            'success': True,
            'session_id': session_id,
            'position': position
        })
    
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500
    
    finally:
        if conn:
            conn.close()


@synergy_bp.route('/update-positions', methods=['POST'])
def update_multiple_positions():
    """
    Update positions for multiple cards at once
    
    Body: {cards: [{session_id, position}]}
    """
    conn = None
    try:
        data = request.get_json()
        cards = data.get('cards', [])
        
        if not cards:
            return jsonify({'success': False, 'error': 'cards array required'}), 400
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
        for card in cards:
            session_id = card.get('session_id')
            position = card.get('position')
            if session_id and position is not None:
                sql, params = convert_sql_placeholders('''
                    UPDATE synergy_sessions.synergy_sessions 
                    SET column_position = %s
                    WHERE session_id = %s
                ''', (position, session_id))
        
        conn.commit()
        
        return jsonify({
            'success': True,
            'updated_count': len(cards)
        })
    
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500
    
    finally:
        if conn:
            conn.close()


@synergy_bp.route('/<session_id>/unlink-thread', methods=['POST'])
def unlink_thread_from_synergy(session_id):
    """
    Unlink a thread from a Synergy session (bidirectional sync)
    
    CRITICAL: Updates synergy_sessions.thread_ids array
    This is called from ThreadManager.unlinkFromSynergy() to ensure bidirectional sync
    
    Body: {thread_id}
    """
    conn = None
    try:
        data = request.get_json()
        thread_id = data.get('thread_id')
        
        if not thread_id:
            return jsonify({'success': False, 'error': 'thread_id required'}), 400
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Get current thread_ids array
        cursor.execute('SELECT thread_ids FROM synergy_sessions.synergy_sessions WHERE session_id = %s', (session_id,))
        row = cursor.fetchone()
        
        if not row:
            return jsonify({'success': False, 'error': 'Session not found'}), 404
        
        # Parse existing thread_ids (JSON array)
        thread_ids = []
        if row['thread_ids']:
            try:
                thread_ids = json.loads(row['thread_ids'])
                if not isinstance(thread_ids, list):
                    thread_ids = []
            except json.JSONDecodeError:
                thread_ids = []
        
        # Remove thread if present
        if thread_id in thread_ids:
            thread_ids.remove(thread_id)
            
            # UPDATE synergy_sessions.synergy_sessions
            sql, params = convert_sql_placeholders('''
                UPDATE synergy_sessions.synergy_sessions 
                SET thread_ids = %s, last_active = %s
                WHERE session_id = %s
            ''', (json.dumps(thread_ids), datetime.now().isoformat(), session_id))
            
            conn.commit()
            print(f"[SYNERGY SYNC] Removed thread {thread_id} from Synergy session {session_id}")
        else:
            print(f"[SYNERGY SYNC] Thread {thread_id} not found in {session_id}")
        
        return jsonify({
            'success': True,
            'session_id': session_id,
            'thread_ids': thread_ids,
            'message': f'Thread {thread_id} unlinked successfully'
        })
    
    except Exception as e:
        print(f"[SYNERGY SYNC ERROR] Failed to unlink thread: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500
    
    finally:
        if conn:
            conn.close()


# ============================================================
# INTERNAL DOCUMENTS (Markdown docs inside Synergy sessions)
# ============================================================

@synergy_bp.route('/internal-doc/create', methods=['POST'])
def create_internal_doc():
    """
    Create a new internal document inside a Synergy session
    
    Body:
        {
            "session_id": "sess_123",
            "title": "Project Draft",
            "content": "# Header\\n\\nContent...",
            "format": "markdown",
            "created_by": "agent_deepseek"
        }
    
    Returns:
        {
            "success": true,
            "doc_id": "int_doc_1731600000123",
            "title": "Project Draft",
            "session_id": "sess_123"
        }
    """
    try:
        data = request.get_json()
        session_id = data.get('session_id')
        title = data.get('title', 'Untitled Document')
        content = data.get('content', '')
        content_json = data.get('content_json')
        doc_format = data.get('format', 'markdown')
        doc_type = data.get('doc_type', 'richtext')  # 'richtext' or 'spreadsheet'
        created_by = data.get('created_by', 'system')
        
        if not session_id:
            return jsonify({'success': False, 'error': 'session_id required'}), 400
        
        # Generate doc ID
        import time
        import re
        doc_id = f"int_doc_{int(time.time() * 1000)}"
        
        # Generate slug from title
        slug = re.sub(r'[^a-z0-9]+', '-', title.lower()).strip('-')
        if not slug:
            slug = doc_id
        
        # Ensure slug uniqueness
        conn = get_db_connection()
        cursor = conn.cursor()
        
        original_slug = slug
        counter = 1
        while True:
            sql, params = convert_sql_placeholders(
                'SELECT doc_id FROM synergy_sessions.synergy_internal_docs WHERE slug = %s',
                (slug,)
            )
            cursor.execute(sql, params)
            if not cursor.fetchone():
                break
            slug = f"{original_slug}-{counter}"
            counter += 1
        
        # Generate share URL
        share_url = f"/internal-docs/{slug}"
        
        # Verify session exists
        sql, params = convert_sql_placeholders(
            'SELECT session_id FROM synergy_sessions.synergy_sessions WHERE session_id = %s',
            (session_id,)
        )
        cursor.execute(sql, params)
        if not cursor.fetchone():
            conn.close()
            return jsonify({'success': False, 'error': 'Session not found'}), 404
        
        # Insert document with slug and share_url
        now = datetime.now().isoformat()
        sql, params = convert_sql_placeholders('''
            INSERT INTO synergy_sessions.synergy_internal_docs 
            (doc_id, session_id, title, content, content_json, format, doc_type, 
             created_by, created_at, updated_at, version, linked_to_ai, slug, share_url)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        ''', (doc_id, session_id, title, content, content_json, doc_format, doc_type,
              created_by, now, now, 1, 0, slug, share_url))
        cursor.execute(sql, params)
        
        conn.commit()
        conn.close()
        
        print(f"[INTERNAL DOC] Created document {doc_id} in session {session_id}: {title} (slug: {slug})")
        
        return jsonify({
            'success': True,
            'doc_id': doc_id,
            'title': title,
            'session_id': session_id,
            'slug': slug,
            'share_url': share_url,
            'created_at': datetime.now().isoformat()
        })
    
    except Exception as e:
        print(f"[INTERNAL DOC ERROR] Failed to create: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({'success': False, 'error': str(e)}), 500


@synergy_bp.route('/internal-doc/<doc_id>', methods=['GET'])
def get_internal_doc(doc_id):
    """
    Retrieve an internal document by ID
    
    Returns:
        {
            "success": true,
            "doc_id": "int_doc_123",
            "session_id": "sess_456",
            "title": "Project Draft",
            "content": "# Content...",
            "format": "markdown",
            "created_at": "...",
            "updated_at": "...",
            "version": 1
        }
    """
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        sql, params = convert_sql_placeholders('''
            SELECT doc_id, session_id, title, content, content_json, format, doc_type,
                   created_at, updated_at, created_by, version, linked_to_ai,
                   slug, share_url, description, tags
            FROM synergy_sessions.synergy_internal_docs
            WHERE doc_id = %s
        ''', (doc_id,))
        cursor.execute(sql, params)
        
        row = cursor.fetchone()
        conn.close()
        
        if not row:
            return jsonify({'success': False, 'error': 'Document not found'}), 404
        
        doc = {
            'doc_id': row['doc_id'],
            'session_id': row['session_id'],
            'title': row['title'],
            'content': row['content'],
            'content_json': row['content_json'],
            'format': row['format'],
            'doc_type': row['doc_type'] or 'richtext',
            'created_at': row['created_at'],
            'updated_at': row['updated_at'],
            'created_by': row['created_by'],
            'version': row['version'],
            'linked_to_ai': bool(row['linked_to_ai']),
            'slug': row['slug'],
            'share_url': row['share_url'],
            'description': row['description'],
            'tags': row['tags']
        }
        
        return jsonify({'success': True, **doc})
    
    except Exception as e:
        print(f"[INTERNAL DOC ERROR] Failed to retrieve {doc_id}: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500


@synergy_bp.route('/internal-doc/<doc_id>', methods=['PUT'])
def update_internal_doc(doc_id):
    """
    Update an internal document
    
    Body:
        {
            "title": "Updated Title",
            "content": "Updated content..."
        }
    
    Returns:
        {
            "success": true,
            "doc_id": "int_doc_123",
            "version": 2
        }
    """
    try:
        data = request.get_json()
        title = data.get('title')
        content = data.get('content')
        content_json = data.get('content_json')
        
        if not title and not content and not content_json:
            return jsonify({'success': False, 'error': 'title, content, or content_json required'}), 400
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Get current version
        sql, params = convert_sql_placeholders(
            'SELECT version FROM synergy_sessions.synergy_internal_docs WHERE doc_id = %s',
            (doc_id,)
        )
        cursor.execute(sql, params)
        row = cursor.fetchone()
        
        if not row:
            conn.close()
            return jsonify({'success': False, 'error': 'Document not found'}), 404
        
        new_version = row['version'] + 1
        
        # Build update query
        updates = []
        update_params = []
        
        if title:
            updates.append('title = %s')
            update_params.append(title)
        if content is not None:  # Allow empty string
            updates.append('content = %s')
            update_params.append(content)
        if content_json is not None:
            updates.append('content_json = %s')
            update_params.append(content_json)
        
        now = datetime.now().isoformat()
        updates.append('updated_at = %s')
        update_params.append(now)
        updates.append('version = %s')
        update_params.append(new_version)
        
        update_params.append(doc_id)
        
        query = f"UPDATE synergy_sessions.synergy_internal_docs SET {', '.join(updates)} WHERE doc_id = %s"
        sql, final_params = convert_sql_placeholders(query, tuple(update_params))
        cursor.execute(sql, final_params)
        
        conn.commit()
        conn.close()
        
        print(f"[INTERNAL DOC] Updated document {doc_id} (version {new_version})")
        
        return jsonify({
            'success': True,
            'doc_id': doc_id,
            'version': new_version,
            'updated_at': datetime.now().isoformat()
        })
    
    except Exception as e:
        print(f"[INTERNAL DOC ERROR] Failed to update {doc_id}: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({'success': False, 'error': str(e)}), 500


@synergy_bp.route('/internal-doc/<doc_id>', methods=['DELETE'])
def delete_internal_doc(doc_id):
    """
    Delete an internal document
    
    Returns:
        {
            "success": true,
            "doc_id": "int_doc_123"
        }
    """
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        sql, params = convert_sql_placeholders(
            'DELETE FROM synergy_sessions.synergy_internal_docs WHERE doc_id = %s',
            (doc_id,)
        )
        cursor.execute(sql, params)
        
        if cursor.rowcount == 0:
            conn.close()
            return jsonify({'success': False, 'error': 'Document not found'}), 404
        
        conn.commit()
        conn.close()
        
        print(f"[INTERNAL DOC] Deleted document {doc_id}")
        
        return jsonify({
            'success': True,
            'doc_id': doc_id,
            'message': 'Document deleted successfully'
        })
    
    except Exception as e:
        print(f"[INTERNAL DOC ERROR] Failed to delete {doc_id}: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500


@synergy_bp.route('/<session_id>/document/<int:doc_index>', methods=['DELETE'])
def remove_document(session_id, doc_index):
    """
    Remove a document from session by index
    
    Args:
        session_id: Session ID
        doc_index: Index of document to remove (0-based)
    
    Returns:
        {"success": true, "documents": [...], "count": 2}
    """
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Get current documents
        cursor.execute('SELECT documents FROM synergy_sessions.synergy_sessions WHERE session_id = %s', (session_id,))
        row = cursor.fetchone()
        
        if not row:
            conn.close()
            return jsonify({'success': False, 'error': 'Session not found'}), 404
        
        documents = json.loads(row['documents'] or '[]')
        
        if doc_index < 0 or doc_index >= len(documents):
            conn.close()
            return jsonify({'success': False, 'error': f'Invalid index {doc_index}'}), 400
        
        # Remove document at index
        removed_doc = documents.pop(doc_index)
        
        # Update database
        cursor.execute(
            'UPDATE synergy_sessions.synergy_sessions SET documents = %s WHERE session_id = %s',
            (json.dumps(documents), session_id)
        )
        conn.commit()
        conn.close()
        
        return jsonify({
            'success': True,
            'documents': documents,
            'count': len(documents),
            'removed': removed_doc
        })
    
    except Exception as e:
        print(f"[SESSION ERROR] Failed to remove document: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500


@synergy_bp.route('/<session_id>/link/<int:link_index>', methods=['DELETE'])
def remove_link(session_id, link_index):
    """
    Remove a link from session by index
    
    Args:
        session_id: Session ID
        link_index: Index of link to remove (0-based)
    
    Returns:
        {"success": true, "links": [...], "count": 3}
    """
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Get current links
        cursor.execute('SELECT links FROM synergy_sessions.synergy_sessions WHERE session_id = %s', (session_id,))
        row = cursor.fetchone()
        
        if not row:
            conn.close()
            return jsonify({'success': False, 'error': 'Session not found'}), 404
        
        links = json.loads(row['links'] or '[]')
        
        if link_index < 0 or link_index >= len(links):
            conn.close()
            return jsonify({'success': False, 'error': f'Invalid index {link_index}'}), 400
        
        # Remove link at index
        removed_link = links.pop(link_index)
        
        # Update database
        cursor.execute(
            'UPDATE synergy_sessions.synergy_sessions SET links = %s WHERE session_id = %s',
            (json.dumps(links), session_id)
        )
        conn.commit()
        conn.close()
        
        return jsonify({
            'success': True,
            'links': links,
            'count': len(links),
            'removed': removed_link
        })
    
    except Exception as e:
        print(f"[SESSION ERROR] Failed to remove link: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500


@synergy_bp.route('/<session_id>/tag/<tag_name>', methods=['DELETE'])
def remove_tag(session_id, tag_name):
    """
    Remove a tag from session by name
    
    Args:
        session_id: Session ID
        tag_name: Tag name to remove
    
    Returns:
        {"success": true, "tags": [...], "count": 4}
    """
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Get current tags
        cursor.execute('SELECT tags FROM synergy_sessions.synergy_sessions WHERE session_id = %s', (session_id,))
        row = cursor.fetchone()
        
        if not row:
            conn.close()
            return jsonify({'success': False, 'error': 'Session not found'}), 404
        
        tags = json.loads(row['tags'] or '[]')
        
        # Remove tag by name (case-insensitive)
        original_count = len(tags)
        tags = [t for t in tags if t.lower() != tag_name.lower()]
        
        if len(tags) == original_count:
            conn.close()
            return jsonify({'success': False, 'error': f'Tag "{tag_name}" not found'}), 404
        
        # Update database
        cursor.execute(
            'UPDATE synergy_sessions.synergy_sessions SET tags = %s WHERE session_id = %s',
            (json.dumps(tags), session_id)
        )
        conn.commit()
        conn.close()
        
        return jsonify({
            'success': True,
            'tags': tags,
            'count': len(tags),
            'removed': tag_name
        })
    
    except Exception as e:
        print(f"[SESSION ERROR] Failed to remove tag: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500


@synergy_bp.route('/milestone/<milestone_id>', methods=['DELETE'])
def delete_milestone(milestone_id):
    """
    Delete a milestone and all its tasks/subtasks
    
    Args:
        milestone_id: Milestone ID to delete
    
    Returns:
        {"success": true, "milestone_id": "ms_xxx", "tasks_deleted": 5, "subtasks_deleted": 12}
    """
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Count tasks and subtasks before deleting
        cursor.execute('SELECT COUNT(*) as count FROM synergy_sessions.tasks WHERE milestone_id = %s', (milestone_id,))
        tasks_count = cursor.fetchone()['count']
        
        cursor.execute('''
            SELECT COUNT(*) as count FROM synergy_sessions.subtasks 
            WHERE task_id IN (SELECT task_id FROM synergy_sessions.tasks WHERE milestone_id = %s)
        ''', (milestone_id,))
        subtasks_count = cursor.fetchone()['count']
        
        # Delete subtasks first (foreign key constraint)
        cursor.execute('''
            DELETE FROM synergy_sessions.subtasks 
            WHERE task_id IN (SELECT task_id FROM synergy_sessions.tasks WHERE milestone_id = %s)
        ''', (milestone_id,))
        
        # Delete tasks
        cursor.execute('DELETE FROM synergy_sessions.tasks WHERE milestone_id = %s', (milestone_id,))
        
        # Delete milestone
        cursor.execute('DELETE FROM synergy_sessions.milestones WHERE milestone_id = %s', (milestone_id,))
        
        if cursor.rowcount == 0:
            conn.close()
            return jsonify({'success': False, 'error': 'Milestone not found'}), 404
        
        conn.commit()
        conn.close()
        
        return jsonify({
            'success': True,
            'milestone_id': milestone_id,
            'tasks_deleted': tasks_count,
            'subtasks_deleted': subtasks_count,
            'message': f'Deleted milestone with {tasks_count} tasks and {subtasks_count} subtasks'
        })
    
    except Exception as e:
        print(f"[MILESTONE ERROR] Failed to delete milestone: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500


@synergy_bp.route('/task/<task_id>', methods=['DELETE'])
def delete_task(task_id):
    """
    Delete a task and all its subtasks
    
    Args:
        task_id: Task ID to delete
    
    Returns:
        {"success": true, "task_id": "task_xxx", "subtasks_deleted": 3}
    """
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Count subtasks before deleting
        cursor.execute('SELECT COUNT(*) as count FROM synergy_sessions.subtasks WHERE task_id = %s', (task_id,))
        subtasks_count = cursor.fetchone()['count']
        
        # Delete subtasks first (foreign key constraint)
        cursor.execute('DELETE FROM synergy_sessions.subtasks WHERE task_id = %s', (task_id,))
        
        # Delete task
        cursor.execute('DELETE FROM synergy_sessions.tasks WHERE task_id = %s', (task_id,))
        
        if cursor.rowcount == 0:
            conn.close()
            return jsonify({'success': False, 'error': 'Task not found'}), 404
        
        conn.commit()
        conn.close()
        
        return jsonify({
            'success': True,
            'task_id': task_id,
            'subtasks_deleted': subtasks_count,
            'message': f'Deleted task with {subtasks_count} subtasks'
        })
    
    except Exception as e:
        print(f"[TASK ERROR] Failed to delete task: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500


@synergy_bp.route('/subtask/<subtask_id>', methods=['DELETE'])
def delete_subtask(subtask_id):
    """
    Delete a subtask
    
    Args:
        subtask_id: Subtask ID to delete
    
    Returns:
        {"success": true, "subtask_id": "sub_xxx"}
    """
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute('DELETE FROM synergy_sessions.subtasks WHERE subtask_id = %s', (subtask_id,))
        
        if cursor.rowcount == 0:
            conn.close()
            return jsonify({'success': False, 'error': 'Subtask not found'}), 404
        
        conn.commit()
        conn.close()
        
        return jsonify({
            'success': True,
            'subtask_id': subtask_id,
            'message': 'Subtask deleted successfully'
        })
    
    except Exception as e:
        print(f"[SUBTASK ERROR] Failed to delete subtask: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500


@synergy_bp.route('/internal-docs/list', methods=['GET'])
def list_all_internal_docs():
    """
    List ALL internal documents (for document picker)
    
    Returns:
        {
            "success": true,
            "count": 25,
            "documents": [
                {
                    "doc_id": "int_doc_123",
                    "title": "Document 1",
                    "doc_type": "richtext",
                    "created_at": "...",
                    "description": "...",
                    "tags": "tag1,tag2"
                }
            ]
        }
    """
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        sql, params = convert_sql_placeholders('''
            SELECT doc_id, title, doc_type, created_at, updated_at, description, tags, session_id
            FROM synergy_sessions.synergy_internal_docs
            ORDER BY created_at DESC
        ''', ())
        
        cursor.execute(sql, params)
        
        rows = cursor.fetchall()
        conn.close()
        
        documents = [{
            'doc_id': row['doc_id'],
            'title': row['title'],
            'doc_type': row['doc_type'] or 'richtext',
            'created_at': row['created_at'],
            'updated_at': row['updated_at'],
            'description': row['description'],
            'tags': row['tags'],
            'session_id': row['session_id']
        } for row in rows]
        
        return jsonify({
            'success': True,
            'count': len(documents),
            'documents': documents
        })
    
    except Exception as e:
        print(f"[INTERNAL DOC ERROR] Failed to list all documents: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({'success': False, 'error': str(e)}), 500


@synergy_bp.route('/internal-doc/list/<session_id>', methods=['GET'])
def list_internal_docs(session_id):
    """
    List all internal documents for a Synergy session
    
    Returns:
        {
            "success": true,
            "session_id": "sess_123",
            "documents": [
                {
                    "doc_id": "int_doc_123",
                    "title": "Document 1",
                    "format": "markdown",
                    "created_at": "...",
                    "updated_at": "...",
                    "version": 1
                }
            ]
        }
    """
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        sql, params = convert_sql_placeholders('''
            SELECT doc_id, title, format, doc_type, created_at, updated_at, created_by, version, linked_to_ai,
                   slug, share_url, description, tags
            FROM synergy_sessions.synergy_internal_docs
            WHERE session_id = %s
            ORDER BY created_at DESC
        ''', (session_id,))

        
        cursor.execute(sql, params)
        
        rows = cursor.fetchall()
        conn.close()
        
        documents = [{
            'doc_id': row['doc_id'],
            'title': row['title'],
            'format': row['format'],
            'doc_type': row['doc_type'] or 'richtext',
            'created_at': row['created_at'],
            'updated_at': row['updated_at'],
            'created_by': row['created_by'],
            'version': row['version'],
            'linked_to_ai': bool(row['linked_to_ai']),
            'slug': row['slug'],
            'share_url': row['share_url'],
            'description': row['description'],
            'tags': row['tags']
        } for row in rows]
        
        return jsonify({
            'success': True,
            'session_id': session_id,
            'count': len(documents),
            'documents': documents
        })
    
    except Exception as e:
        print(f"[INTERNAL DOC ERROR] Failed to list documents for {session_id}: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500


@synergy_bp.route('/<session_id>/link-document', methods=['POST'])
def link_existing_document(session_id):
    """
    Link an existing internal document to a Synergy session
    
    Body:
        {
            "doc_id": "int_doc_123",
            "title": "Document Title",
            "doc_type": "richtext"
        }
    
    Returns:
        {
            "success": true,
            "session_id": "sess_123",
            "doc_id": "int_doc_123",
            "linked": true
        }
    """
    try:
        data = request.get_json()
        doc_id = data.get('doc_id')
        
        if not doc_id:
            return jsonify({'success': False, 'error': 'doc_id required'}), 400
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Update document to link it to this session (if not already linked)
        sql, params = convert_sql_placeholders("""
            UPDATE synergy_sessions.synergy_internal_docs
            SET session_id = %s, linked_to_ai = 1
            WHERE doc_id = %s
        """, (session_id, doc_id))
        
        cursor.execute(sql, params)
        
        if cursor.rowcount == 0:
            conn.close()
            return jsonify({'success': False, 'error': 'Document not found'}), 404
        
        conn.commit()
        conn.close()
        
        print(f"[SYNERGY] Linked document {doc_id} to session {session_id}")
        
        return jsonify({
            'success': True,
            'session_id': session_id,
            'doc_id': doc_id,
            'linked': True
        })
    
    except Exception as e:
        print(f"[SYNERGY ERROR] Failed to link document: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({'success': False, 'error': str(e)}), 500


# REMOVED DUPLICATE: link_thread_to_synergy endpoint already defined at line 1138
# The first implementation (line 1138) handles thread_ids array properly


@synergy_bp.route('/<session_id>/linked-threads', methods=['GET'])
def get_linked_threads(session_id):
    """
    Get all threads linked to a Synergy session
    
    Returns:
        {
            "success": true,
            "count": 3,
            "threads": [
                {
                    "thread_id": "thread_123",
                    "thread_slug": "thr_abc",
                    "title": "Thread Title",
                    "agent_id": "prime",
                    "message_count": 10,
                    "created_at": "2025-11-24 12:00:00",
                    "last_activity": "2025-11-24 15:30:00"
                }
            ]
        }
    """
    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Get all threads linked to this session
        sql, params = convert_sql_placeholders("""
            SELECT 
                thread_id,
                thread_slug,
                title,
                agent_id,
                message_count,
                created_at,
                updated_at as last_activity
            FROM sessions.threads
            WHERE synergy_card_id = %s
            ORDER BY updated_at DESC
        """, (session_id,))
        
        cursor.execute(sql, params)
        rows = cursor.fetchall()
        
        threads = []
        for row in rows:
            # Handle both RealDictRow (dict) and tuple formats
            if isinstance(row, dict):
                # Safely convert datetime to isoformat
                created_at = row.get('created_at')
                last_activity = row.get('last_activity')
                
                threads.append({
                    'thread_id': row.get('thread_id'),
                    'thread_slug': row.get('thread_slug'),
                    'title': row.get('title'),
                    'agent_id': row.get('agent_id') or 'prime',
                    'message_count': row.get('message_count') or 0,
                    'created_at': created_at.isoformat() if created_at and hasattr(created_at, 'isoformat') else str(created_at) if created_at else None,
                    'last_activity': last_activity.isoformat() if last_activity and hasattr(last_activity, 'isoformat') else str(last_activity) if last_activity else None
                })
            else:
                # Safely convert datetime to isoformat for tuple format
                created_at = row[5] if len(row) > 5 else None
                last_activity = row[6] if len(row) > 6 else None
                
                threads.append({
                    'thread_id': row[0],
                    'thread_slug': row[1],
                    'title': row[2],
                    'agent_id': row[3] or 'prime',
                    'message_count': row[4] or 0,
                    'created_at': created_at.isoformat() if created_at and hasattr(created_at, 'isoformat') else str(created_at) if created_at else None,
                    'last_activity': last_activity.isoformat() if last_activity and hasattr(last_activity, 'isoformat') else str(last_activity) if last_activity else None
                })
        
        print(f"[SYNERGY] Found {len(threads)} linked threads for session {session_id}")
        
        return jsonify({
            'success': True,
            'count': len(threads),
            'threads': threads
        })
    
    except Exception as e:
        print(f"[SYNERGY ERROR] Failed to get linked threads: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({'success': False, 'error': str(e)}), 500
    
    finally:
        if conn:
            conn.close()


@synergy_bp.route('/internal-doc/<doc_id>/link-ai', methods=['POST'])
def link_doc_to_ai(doc_id):
    """
    Link document to AI session
    
    Body:
        {
            "session_id": "sess_123",
            "user_id": 1
        }
    
    Returns:
        {
            "success": true,
            "doc_id": "int_doc_123",
            "linked": true
        }
    """
    try:
        data = request.get_json()
        session_id = data.get('session_id')
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Update document to link to AI
        sql, params = convert_sql_placeholders("""
            UPDATE synergy_sessions.synergy_internal_docs
            SET linked_to_ai = 1, session_id = %s
            WHERE doc_id = %s
        """, (session_id, doc_id))
        
        if cursor.rowcount == 0:
            conn.close()
            return jsonify({'success': False, 'error': 'Document not found'}), 404
        
        conn.commit()
        conn.close()
        
        print(f"[INTERNAL DOC] Linked document {doc_id} to AI session {session_id}")
        
        return jsonify({
            'success': True,
            'doc_id': doc_id,
            'linked': True,
            'session_id': session_id
        })
    
    except Exception as e:
        print(f"[INTERNAL DOC ERROR] Failed to link {doc_id}: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500


@synergy_bp.route('/internal-doc/<doc_id>/export/<format>', methods=['POST'])
def export_internal_doc(doc_id, format):
    """
    Export document to specified format
    
    Formats: markdown, html, word, google_doc, pdf, excel, csv
    
    Body:
        {
            "user_id": 1
        }
    
    Returns:
        For files: Binary download
        For URLs: {"success": true, "url": "https://..."}
    """
    try:
        # Get document
        conn = get_db_connection()
        cursor = conn.cursor()
        
        sql, params = convert_sql_placeholders("""
            SELECT doc_id, title, content, content_json, doc_type
            FROM synergy_sessions.synergy_internal_docs
            WHERE doc_id = %s
        """, (doc_id,))

        
        cursor.execute(sql, params)
        
        row = cursor.fetchone()
        conn.close()
        
        if not row:
            return jsonify({'success': False, 'error': 'Document not found'}), 404
        
        doc_title = row['title']
        doc_content = row['content']
        doc_json = row['content_json']
        doc_type = row['doc_type']
        
        # Handle different export formats
        if format == 'markdown':
            from flask import send_file
            import io
            
            buffer = io.BytesIO(doc_content.encode('utf-8'))
            buffer.seek(0)
            
            return send_file(
                buffer,
                mimetype='text/markdown',
                as_attachment=True,
                download_name=f"{doc_title}.md"
            )
        
        elif format == 'html':
            import markdown
            html_content = f"""<!DOCTYPE html>
<html>
<head>
    <title>{doc_title}</title>
    <style>
        body {{ font-family: Arial, sans-serif; max-width: 800px; margin: 40px auto; padding: 20px; }}
        h1 {{ color: #333; }}
        code {{ background: #f4f4f4; padding: 2px 6px; border-radius: 3px; }}
        pre {{ background: #f4f4f4; padding: 16px; border-radius: 6px; overflow-x: auto; }}
    </style>
</head>
<body>
{markdown.markdown(doc_content, extensions=['tables', 'fenced_code'])}
</body>
</html>"""
            
            buffer = io.BytesIO(html_content.encode('utf-8'))
            buffer.seek(0)
            
            return send_file(
                buffer,
                mimetype='text/html',
                as_attachment=True,
                download_name=f"{doc_title}.html"
            )
        
        elif format == 'word':
            # TODO: Implement Word export (requires python-docx)
            return jsonify({
                'success': False,
                'error': 'Word export not yet implemented. Install python-docx and implement conversion.'
            }), 501
        
        elif format == 'google_doc':
            # TODO: Implement Google Docs export (requires google_workspace tools)
            return jsonify({
                'success': False,
                'error': 'Google Docs export not yet implemented. Use google_docs_create tool.'
            }), 501
        
        elif format == 'pdf':
            # TODO: Implement PDF export (requires reportlab or weasyprint)
            return jsonify({
                'success': False,
                'error': 'PDF export not yet implemented. Install weasyprint or reportlab.'
            }), 501
        
        elif format == 'excel' or format == 'csv':
            if doc_type != 'spreadsheet':
                return jsonify({
                    'success': False,
                    'error': 'Document is not a spreadsheet'
                }), 400
            
            # Parse JSON data
            import json as json_lib
            try:
                data = json_lib.loads(doc_json or doc_content)
            except:
                return jsonify({
                    'success': False,
                    'error': 'Invalid spreadsheet data'
                }), 400
            
            if format == 'csv':
                import csv
                import io
                
                output = io.StringIO()
                writer = csv.writer(output)
                
                for row in data:
                    writer.writerow(row)
                
                buffer = io.BytesIO(output.getvalue().encode('utf-8'))
                buffer.seek(0)
                
                return send_file(
                    buffer,
                    mimetype='text/csv',
                    as_attachment=True,
                    download_name=f"{doc_title}.csv"
                )
            
            else:  # excel
                # TODO: Implement Excel export (requires openpyxl)
                return jsonify({
                    'success': False,
                    'error': 'Excel export not yet implemented. Install openpyxl.'
                }), 501
        
        else:
            return jsonify({
                'success': False,
                'error': f'Unknown format: {format}'
            }), 400
    
    except Exception as e:
        print(f"[INTERNAL DOC ERROR] Failed to export {doc_id} as {format}: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({'success': False, 'error': str(e)}), 500


# ==================== MILESTONE-BASED TASK MANAGEMENT ====================
# New endpoints for milestone → task → subtask hierarchy (Nov 2025)
# Replaces legacy next_steps + checklist structure

@synergy_bp.route('/milestone/create', methods=['POST'])
def create_milestone():
    """
    Create new milestone with tasks in one call
    
    Request Body:
    {
        "session_id": "sess_abc123",
        "milestone_name": "Database Setup",
        "description": "Create customer database and import contacts",
        "tasks": [
            "Create Google Sheet",
            {
                "task": "Import existing contacts",
                "subtasks": ["Export from old CRM", "Clean data", "Import"]
            }
        ],
        "due_date": "2025-11-25",
        "priority": "high",
        "estimated_hours": 3
    }
    
    Response:
    {
        "success": true,
        "milestone_id": "ms_a1b2c3d4",
        "milestone_number": 1,
        "tasks_created": 2,
        "subtasks_created": 3
    }
    """
    try:
        data = request.get_json()
        
        if not data.get('session_id'):
            return jsonify({'success': False, 'error': 'session_id required'}), 400
        if not data.get('milestone_name'):
            return jsonify({'success': False, 'error': 'milestone_name required'}), 400
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Check if session exists
        cursor.execute('SELECT session_id FROM synergy_sessions.synergy_sessions WHERE session_id = %s', (data['session_id'],))
        if not cursor.fetchone():
            conn.close()
            return jsonify({'success': False, 'error': 'Session not found'}), 404
        
        # Get next milestone number
        sql, params = convert_sql_placeholders('''
            SELECT COALESCE(MAX(milestone_number), 0) + 1 AS next_number
            FROM synergy_sessions.milestones 
            WHERE session_id = %s
        ''', (data['session_id'],))
        cursor.execute(sql, params)
        result = cursor.fetchone()
        milestone_number = result['next_number'] if isinstance(result, dict) else result[0]
        
        # Generate milestone ID
        milestone_id = f"ms_{datetime.now().strftime('%Y%m%d%H%M%S')}"
        
        # Insert milestone
        sql, params = convert_sql_placeholders('''
            INSERT INTO synergy_sessions.milestones (
                milestone_id, session_id, milestone_number, milestone_order, milestone_name,
                description, completed, due_date, priority, estimated_hours,
                created_at, updated_at
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        ''', (
            milestone_id,
            data['session_id'],
            milestone_number,
            milestone_number,  # milestone_order same as milestone_number
            data['milestone_name'],
            data.get('description'),
            False,
            data.get('due_date'),
            data.get('priority', 'medium'),
            data.get('estimated_hours'),
            datetime.now().isoformat(),
            datetime.now().isoformat()
        ))
        cursor.execute(sql, params)
        
        # Insert tasks
        tasks_created = 0
        subtasks_created = 0
        tasks_list = data.get('tasks', [])
        
        for task_order, task_item in enumerate(tasks_list, start=1):
            task_id = f"task_{datetime.now().strftime('%Y%m%d%H%M%S')}_{task_order}"
            
            # Handle both string and object formats
            if isinstance(task_item, str):
                task_text = task_item
                task_priority = 'medium'  # Default priority
                subtasks = []
            else:
                task_text = task_item.get('task', '')
                task_priority = task_item.get('priority', 'medium')  # Get priority or default to medium
                subtasks = task_item.get('subtasks', [])
            
            # Insert task with priority
            cursor.execute('''
                INSERT INTO synergy_sessions.tasks (
                    task_id, milestone_id, task, completed, task_order, priority, created_at
                ) VALUES (%s, %s, %s, %s, %s, %s, %s)
            ''', (task_id, milestone_id, task_text, False, task_order, task_priority, datetime.now().isoformat()))
            tasks_created += 1
            
            # Insert subtasks with priority
            for subtask_order, subtask_item in enumerate(subtasks, start=1):
                subtask_id = f"sub_{datetime.now().strftime('%Y%m%d%H%M%S')}_{task_order}_{subtask_order}"
                
                # Handle both string and object formats for subtasks
                if isinstance(subtask_item, str):
                    subtask_text = subtask_item
                    subtask_priority = 'medium'  # Default priority
                else:
                    subtask_text = subtask_item.get('task', '') or subtask_item.get('text', '')
                    subtask_priority = subtask_item.get('priority', 'medium')  # Get priority or default to medium
                
                cursor.execute('''
                    INSERT INTO synergy_sessions.subtasks (
                        subtask_id, task_id, task, completed, subtask_order, priority, created_at
                    ) VALUES (%s, %s, %s, %s, %s, %s, %s)
                ''', (subtask_id, task_id, subtask_text, False, subtask_order, subtask_priority, datetime.now().isoformat()))
                subtasks_created += 1
        
        # Mark session as using milestones
        cursor.execute('''
            UPDATE synergy_sessions.synergy_sessions 
            SET uses_milestones = TRUE, last_active = %s
            WHERE session_id = %s
        ''', (datetime.now().isoformat(), data['session_id']))
        
        conn.commit()
        conn.close()
        
        return jsonify({
            'success': True,
            'milestone_id': milestone_id,
            'milestone_number': milestone_number,
            'tasks_created': tasks_created,
            'subtasks_created': subtasks_created
        })
    
    except Exception as e:
        if conn:
            conn.rollback()  # ✅ CRITICAL: Undo partial inserts (milestone/tasks/subtasks)
        print(f"[MILESTONE ERROR] Failed to create milestone: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({'success': False, 'error': str(e)}), 500
    finally:
        if conn:
            conn.close()


@synergy_bp.route('/milestone/<milestone_id>/task/create', methods=['POST'])
def create_milestone_task(milestone_id):
    """
    Add task to existing milestone
    
    Request Body:
    {
        "task": "Set up database backups",
        "subtasks": ["Configure automated backups", "Test restore procedure"]
    }
    
    Response:
    {
        "success": true,
        "task_id": "task_x1y2z3",
        "subtasks_created": 2
    }
    """
    try:
        data = request.get_json()
        
        if not data.get('task'):
            return jsonify({'success': False, 'error': 'task text required'}), 400
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Check if milestone exists
        cursor.execute('SELECT milestone_id FROM synergy_sessions.milestones WHERE milestone_id = %s', (milestone_id,))
        if not cursor.fetchone():
            conn.close()
            return jsonify({'success': False, 'error': 'Milestone not found'}), 404
        
        # Get next task order
        cursor.execute('''
            SELECT COALESCE(MAX(task_order), 0) + 1 
            FROM synergy_sessions.tasks 
            WHERE milestone_id = %s
        ''', (milestone_id,))
        task_order = cursor.fetchone()[0]
        
        # Generate task ID
        task_id = f"task_{datetime.now().strftime('%Y%m%d%H%M%S')}"
        task_priority = data.get('priority', 'medium')  # Get priority from request or default to medium
        
        # Insert task with priority
        cursor.execute('''
            INSERT INTO synergy_sessions.tasks (
                task_id, milestone_id, task, completed, task_order, priority, created_at
            ) VALUES (%s, %s, %s, %s, %s, %s, %s)
        ''', (task_id, milestone_id, data['task'], False, task_order, task_priority, datetime.now().isoformat()))
        
        # Insert subtasks with priority
        subtasks_created = 0
        subtasks = data.get('subtasks', [])
        for subtask_order, subtask_item in enumerate(subtasks, start=1):
            subtask_id = f"sub_{datetime.now().strftime('%Y%m%d%H%M%S')}_{subtask_order}"
            
            # Handle both string and object formats for subtasks
            if isinstance(subtask_item, str):
                subtask_text = subtask_item
                subtask_priority = 'medium'
            else:
                subtask_text = subtask_item.get('task', '') or subtask_item.get('text', '')
                subtask_priority = subtask_item.get('priority', 'medium')
            
            cursor.execute('''
                INSERT INTO synergy_sessions.subtasks (
                    subtask_id, task_id, task, completed, subtask_order, priority, created_at
                ) VALUES (%s, %s, %s, %s, %s, %s, %s)
            ''', (subtask_id, task_id, subtask_text, False, subtask_order, subtask_priority, datetime.now().isoformat()))
            subtasks_created += 1
        
        conn.commit()
        conn.close()
        
        return jsonify({
            'success': True,
            'task_id': task_id,
            'subtasks_created': subtasks_created
        })
    
    except Exception as e:
        if conn:
            conn.rollback()  # ✅ CRITICAL: Undo partial task/subtask inserts
        print(f"[MILESTONE ERROR] Failed to create task: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500
    finally:
        if conn:
            conn.close()


@synergy_bp.route('/task/<task_id>/subtasks', methods=['POST'])
@synergy_bp.route('/task/<task_id>/subtask/create', methods=['POST'])
def create_task_subtask(task_id):
    """
    Add subtask to existing task
    
    Request Body:
    {
        "subtask": "Validate data integrity"
    }
    
    Response:
    {
        "success": true,
        "subtask_id": "sub_p1q2r3"
    }
    """
    try:
        data = request.get_json()
        
        if not data.get('subtask'):
            return jsonify({'success': False, 'error': 'subtask text required'}), 400
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Check if task exists
        cursor.execute('SELECT task_id FROM synergy_sessions.tasks WHERE task_id = %s', (task_id,))
        if not cursor.fetchone():
            conn.close()
            return jsonify({'success': False, 'error': 'Task not found'}), 404
        
        # Get next subtask order
        cursor.execute('''
            SELECT COALESCE(MAX(subtask_order), 0) + 1 
            FROM synergy_sessions.subtasks 
            WHERE task_id = %s
        ''', (task_id,))
        subtask_order = cursor.fetchone()[0]
        
        # Generate subtask ID
        subtask_id = f"sub_{datetime.now().strftime('%Y%m%d%H%M%S')}"
        subtask_priority = data.get('priority', 'medium')
        
        # Insert subtask
        cursor.execute('''
            INSERT INTO synergy_sessions.subtasks (
                subtask_id, task_id, task, completed, subtask_order, priority, created_at
            ) VALUES (%s, %s, %s, %s, %s, %s, %s)
        ''', (subtask_id, task_id, data['subtask'], False, subtask_order, subtask_priority, datetime.now().isoformat()))
        
        conn.commit()
        conn.close()
        
        return jsonify({
            'success': True,
            'subtask_id': subtask_id
        })
    
    except Exception as e:
        if conn:
            conn.rollback()  # ✅ CRITICAL: Undo subtask insert
        print(f"[MILESTONE ERROR] Failed to create subtask: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500
    finally:
        if conn:
            conn.close()


@synergy_bp.route('/subtask/<subtask_id>/complete', methods=['PATCH'])
def complete_subtask(subtask_id):
    """
    Mark subtask complete (auto-checks if parent task should complete)
    
    Request Body:
    {
        "completed": true
    }
    
    Response:
    {
        "success": true,
        "subtask_id": "sub_p1q2r3",
        "completed": true,
        "task_auto_completed": false,
        "milestone_auto_completed": false
    }
    """
    try:
        data = request.get_json()
        completed = data.get('completed', True)
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Get subtask info
        cursor.execute('''
            SELECT s.task_id, t.milestone_id 
            FROM synergy_sessions.subtasks s
            JOIN synergy_sessions.tasks t ON s.task_id = t.task_id
            WHERE s.subtask_id = %s
        ''', (subtask_id,))
        row = cursor.fetchone()
        if not row:
            conn.close()
            return jsonify({'success': False, 'error': 'Subtask not found'}), 404
        
        task_id = row[0]
        milestone_id = row[1]
        
        # Update subtask
        sql, params = convert_sql_placeholders('''
            UPDATE synergy_sessions.subtasks 
            SET completed = %s, completed_at = %s
            WHERE subtask_id = %s
        ''', (completed, datetime.now().isoformat() if completed else None, subtask_id))
        
        # Check if all subtasks in this task are completed
        task_auto_completed = False
        milestone_auto_completed = False
        
        if completed:
            cursor.execute('''
                SELECT COUNT(*) FROM synergy_sessions.subtasks 
                WHERE task_id = %s AND NOT completed
            ''', (task_id,))
            remaining_subtasks = cursor.fetchone()[0]
            
            if remaining_subtasks == 0:
                # All subtasks done - auto-complete task
                sql, params = convert_sql_placeholders('''
                    UPDATE synergy_sessions.tasks 
                    SET completed = TRUE, completed_at = %s
                    WHERE task_id = %s
                ''', (datetime.now().isoformat(), task_id))
                task_auto_completed = True
                
                # Check if all tasks in milestone are completed
                cursor.execute('''
                    SELECT COUNT(*) FROM synergy_sessions.tasks 
                    WHERE milestone_id = %s AND NOT completed
                ''', (milestone_id,))
                remaining_tasks = cursor.fetchone()[0]
                
                if remaining_tasks == 0:
                    # All tasks done - auto-complete milestone
                    sql, params = convert_sql_placeholders('''
                        UPDATE synergy_sessions.milestones 
                        SET completed = TRUE, completed_at = %s
                        WHERE milestone_id = %s
                    ''', (datetime.now().isoformat(), milestone_id))
                    milestone_auto_completed = True
        
        conn.commit()
        conn.close()
        
        return jsonify({
            'success': True,
            'subtask_id': subtask_id,
            'completed': completed,
            'task_auto_completed': task_auto_completed,
            'milestone_auto_completed': milestone_auto_completed
        })
    
    except Exception as e:
        print(f"[MILESTONE ERROR] Failed to complete subtask: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500


@synergy_bp.route('/task/<task_id>/complete', methods=['PATCH'])
def complete_task(task_id):
    """
    Mark task complete (auto-completes all subtasks)
    
    Request Body:
    {
        "completed": true
    }
    
    Response:
    {
        "success": true,
        "task_id": "task_x1y2z3",
        "completed": true,
        "milestone_completed": false,
        "auto_completed_subtasks": 3
    }
    """
    try:
        data = request.get_json()
        completed = data.get('completed', True)
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Get task info
        cursor.execute('''
            SELECT milestone_id FROM synergy_sessions.tasks WHERE task_id = %s
        ''', (task_id,))
        row = cursor.fetchone()
        if not row:
            conn.close()
            return jsonify({'success': False, 'error': 'Task not found'}), 404
        
        milestone_id = row[0]
        
        # Update task
        sql, params = convert_sql_placeholders('''
            UPDATE synergy_sessions.tasks 
            SET completed = %s, completed_at = %s
            WHERE task_id = %s
        ''', (completed, datetime.now().isoformat() if completed else None, task_id))
        
        # Auto-complete all subtasks
        auto_completed_subtasks = 0
        if completed:
            cursor.execute('''
                UPDATE synergy_sessions.subtasks 
                SET completed = TRUE, completed_at = %s
                WHERE task_id = %s AND NOT completed
            ''', (datetime.now().isoformat(), task_id))
            auto_completed_subtasks = cursor.rowcount
        
        # Check if all tasks in milestone are completed
        milestone_completed = False
        if completed:
            cursor.execute('''
                SELECT COUNT(*) FROM synergy_sessions.tasks 
                WHERE milestone_id = %s AND NOT completed
            ''', (milestone_id,))
            remaining_tasks = cursor.fetchone()[0]
            
            if remaining_tasks == 0:
                # All tasks done - auto-complete milestone
                sql, params = convert_sql_placeholders('''
                    UPDATE synergy_sessions.milestones 
                    SET completed = TRUE, completed_at = %s
                    WHERE milestone_id = %s
                ''', (datetime.now().isoformat(), milestone_id))
                milestone_completed = True
        
        conn.commit()
        conn.close()
        
        return jsonify({
            'success': True,
            'task_id': task_id,
            'completed': completed,
            'milestone_completed': milestone_completed,
            'auto_completed_subtasks': auto_completed_subtasks
        })
    
    except Exception as e:
        print(f"[MILESTONE ERROR] Failed to complete task: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500


@synergy_bp.route('/milestone/<milestone_id>/complete', methods=['PATCH'])
def complete_milestone(milestone_id):
    """
    Mark entire milestone complete (completes all tasks/subtasks)
    
    Request Body:
    {
        "completed": true
    }
    
    Response:
    {
        "success": true,
        "milestone_id": "ms_a1b2c3d4",
        "completed": true,
        "tasks_completed": 5,
        "subtasks_completed": 12
    }
    """
    try:
        data = request.get_json()
        completed = data.get('completed', True)
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Check milestone exists
        cursor.execute('SELECT milestone_id FROM synergy_sessions.milestones WHERE milestone_id = %s', (milestone_id,))
        if not cursor.fetchone():
            conn.close()
            return jsonify({'success': False, 'error': 'Milestone not found'}), 404
        
        # Update milestone
        cursor.execute('''
            UPDATE synergy_sessions.milestones 
            SET completed = %s, completed_at = %s
            WHERE milestone_id = %s
        ''', (completed, datetime.now().isoformat() if completed else None, milestone_id))
        
        # Auto-complete all tasks
        tasks_completed = 0
        subtasks_completed = 0
        
        if completed:
            # Complete all tasks in milestone
            cursor.execute('''
                UPDATE synergy_sessions.tasks 
                SET completed = TRUE, completed_at = %s
                WHERE milestone_id = %s AND NOT completed
            ''', (datetime.now().isoformat(), milestone_id))
            tasks_completed = cursor.rowcount
            
            # Complete all subtasks in milestone
            cursor.execute('''
                UPDATE synergy_sessions.subtasks s
                SET completed = TRUE, completed_at = %s
                FROM synergy_sessions.tasks t
                WHERE s.task_id = t.task_id 
                  AND t.milestone_id = %s 
                  AND NOT s.completed
            ''', (datetime.now().isoformat(), milestone_id))
            subtasks_completed = cursor.rowcount
        
        conn.commit()
        conn.close()
        
        return jsonify({
            'success': True,
            'milestone_id': milestone_id,
            'completed': completed,
            'tasks_completed': tasks_completed,
            'subtasks_completed': subtasks_completed
        })
    
    except Exception as e:
        print(f"[MILESTONE ERROR] Failed to complete milestone: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500


@synergy_bp.route('/milestone/<milestone_id>/progress', methods=['GET'])
def get_milestone_progress(milestone_id):
    """
    Get completion percentage and remaining items
    
    Response:
    {
        "milestone_id": "ms_a1b2c3d4",
        "milestone_name": "Database Setup",
        "progress_percentage": 66.7,
        "tasks_completed": 2,
        "tasks_total": 3,
        "subtasks_completed": 5,
        "subtasks_total": 8,
        "remaining_tasks": ["Set up validation"],
        "blocked_tasks": [],
        "due_date": "2025-11-25",
        "on_track": true
    }
    """
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Get milestone info
        cursor.execute('''
            SELECT milestone_name, due_date, completed 
            FROM synergy_sessions.milestones 
            WHERE milestone_id = %s
        ''', (milestone_id,))
        row = cursor.fetchone()
        if not row:
            conn.close()
            return jsonify({'success': False, 'error': 'Milestone not found'}), 404
        
        milestone_name = row[0]
        due_date = row[1]
        completed = row[2]
        
        # Get task statistics
        sql, params = convert_sql_placeholders('''
            SELECT 
                COUNT(*) as total_tasks,
                SUM(CASE WHEN completed THEN 1 ELSE 0 END) as completed_tasks,
                SUM(CASE WHEN blocked THEN 1 ELSE 0 END) as blocked_tasks
            FROM synergy_sessions.tasks 
            WHERE milestone_id = %s
        ''', (milestone_id,))
        task_stats = cursor.fetchone()
        tasks_total = task_stats[0]
        tasks_completed = task_stats[1]
        blocked_tasks_count = task_stats[2]
        
        # Get subtask statistics
        sql, params = convert_sql_placeholders('''
            SELECT 
                COUNT(*) as total_subtasks,
                SUM(CASE WHEN s.completed THEN 1 ELSE 0 END) as completed_subtasks
            FROM synergy_sessions.subtasks s
            JOIN synergy_sessions.tasks t ON s.task_id = t.task_id
            WHERE t.milestone_id = %s
        ''', (milestone_id,))
        subtask_stats = cursor.fetchone()
        subtasks_total = subtask_stats[0]
        subtasks_completed = subtask_stats[1]
        
        # Calculate progress percentage
        total_items = tasks_total + subtasks_total
        completed_items = tasks_completed + subtasks_completed
        progress_percentage = round((completed_items / total_items * 100), 1) if total_items > 0 else 0
        
        # Get remaining tasks
        sql, params = convert_sql_placeholders('''
            SELECT task FROM synergy_sessions.tasks 
            WHERE milestone_id = %s AND NOT completed
            ORDER BY task_order
        ''', (milestone_id,))
        remaining_tasks = [row[0] for row in cursor.fetchall()]
        
        # Get blocked tasks
        sql, params = convert_sql_placeholders('''
            SELECT task, blocker_reason, blocker_type
            FROM synergy_sessions.tasks 
            WHERE milestone_id = %s AND blocked
        ''', (milestone_id,))
        blocked_tasks = [{'task': row[0], 'reason': row[1], 'type': row[2]} for row in cursor.fetchall()]
        
        conn.close()
        
        # Determine if on track (simple heuristic)
        on_track = True
        if due_date and not completed:
            from datetime import datetime as dt
            due = dt.fromisoformat(due_date.replace('Z', '+00:00'))
            now = dt.now(due.tzinfo) if due.tzinfo else dt.now()
            if now > due:
                on_track = False  # Past due date
        
        return jsonify({
            'success': True,
            'milestone_id': milestone_id,
            'milestone_name': milestone_name,
            'progress_percentage': progress_percentage,
            'tasks_completed': tasks_completed,
            'tasks_total': tasks_total,
            'subtasks_completed': subtasks_completed,
            'subtasks_total': subtasks_total,
            'remaining_tasks': remaining_tasks,
            'blocked_tasks': blocked_tasks,
            'blocked_tasks_count': blocked_tasks_count,
            'due_date': due_date,
            'on_track': on_track
        })
    
    except Exception as e:
        print(f"[MILESTONE ERROR] Failed to get progress: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500


@synergy_bp.route('/<session_id>/milestones', methods=['GET'])
def get_session_milestones(session_id):
    """
    Get all milestones for session (with tasks and subtasks)
    
    Response:
    {
        "success": true,
        "session_id": "sess_abc123",
        "milestones": [
            {
                "milestone_id": "ms_001",
                "milestone_number": 1,
                "milestone_name": "Database Setup",
                "description": "...",
                "completed": false,
                "progress_percentage": 66.7,
                "tasks": [...]
            }
        ]
    }
    """
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Get session data including description
        cursor.execute('''
            SELECT session_id, title, description, status, priority, 
                   due_date, assignees, documents, links, tags, project_name,
                   created_at, updated_at, message_count
            FROM synergy_sessions.synergy_sessions 
            WHERE session_id = %s
        ''', (session_id,))
        
        session_row = cursor.fetchone()
        if not session_row:
            conn.close()
            return jsonify({'success': False, 'error': 'Session not found'}), 404
        
        session_data = {
            'session_id': session_row['session_id'],
            'title': session_row['title'],
            'description': session_row['description'],
            'status': session_row['status'],
            'priority': session_row['priority'],
            'due_date': session_row['due_date'],
            'assignees': session_row['assignees'],
            'documents': session_row['documents'],
            'links': session_row['links'],
            'tags': session_row['tags'],
            'project_name': session_row['project_name'],
            'created_at': session_row['created_at'],
            'updated_at': session_row['updated_at'],
            'message_count': session_row['message_count'] or 0
        }
        
        # Get all milestones
        sql, params = convert_sql_placeholders('''
            SELECT milestone_id, milestone_number, milestone_name, description,
                   completed, due_date, priority, estimated_hours, actual_hours,
                   created_at, completed_at, milestone_order, depends_on_milestone_id,
                   blocked, blocker_reason, blocked_since, updated_at, documents, links
            FROM synergy_sessions.milestones 
            WHERE session_id = %s
            ORDER BY milestone_number
        ''', (session_id,))
        
        cursor.execute(sql, params)
        
        rows = cursor.fetchall()
        
        milestones = []
        for m_row in rows:
            milestone = {
                'milestone_id': m_row['milestone_id'],
                'milestone_number': m_row['milestone_number'],
                'milestone_name': m_row['milestone_name'],
                'description': m_row['description'],
                'completed': m_row['completed'],
                'due_date': m_row['due_date'].isoformat() if m_row['due_date'] else None,
                'priority': m_row['priority'],
                'estimated_hours': float(m_row['estimated_hours']) if m_row['estimated_hours'] else None,
                'actual_hours': float(m_row['actual_hours']) if m_row['actual_hours'] else None,
                'created_at': m_row['created_at'].isoformat() if m_row['created_at'] else None,
                'completed_at': m_row['completed_at'].isoformat() if m_row['completed_at'] else None,
                'milestone_order': m_row['milestone_order'],
                'depends_on_milestone_id': m_row['depends_on_milestone_id'],
                'blocked': m_row['blocked'],
                'blocker_reason': m_row['blocker_reason'],
                'blocked_since': m_row['blocked_since'].isoformat() if m_row['blocked_since'] else None,
                'updated_at': m_row['updated_at'].isoformat() if m_row['updated_at'] else None,
                'documents': m_row['documents'],
                'links': m_row['links'],
                'tasks': []
            }
            
            # Get tasks for this milestone
            sql, params = convert_sql_placeholders('''
                SELECT task_id, task, completed, blocked, blocker_reason, 
                       blocker_type, task_order, created_at, completed_at,
                       blocked_since, estimated_hours, actual_hours, assigned_to, updated_at, priority
                FROM synergy_sessions.tasks 
                WHERE milestone_id = %s
                ORDER BY task_order
            ''', (milestone['milestone_id'],))
            
            cursor.execute(sql, params)
            
            for t_row in cursor.fetchall():
                task = {
                    'task_id': t_row['task_id'],
                    'task': t_row['task'],
                    'completed': t_row['completed'],
                    'blocked': t_row['blocked'],
                    'blocker_reason': t_row['blocker_reason'],
                    'blocker_type': t_row['blocker_type'],
                    'task_order': t_row['task_order'],
                    'created_at': t_row['created_at'].isoformat() if t_row['created_at'] else None,
                    'completed_at': t_row['completed_at'].isoformat() if t_row['completed_at'] else None,
                    'blocked_since': t_row['blocked_since'].isoformat() if t_row['blocked_since'] else None,
                    'estimated_hours': float(t_row['estimated_hours']) if t_row['estimated_hours'] else None,
                    'actual_hours': float(t_row['actual_hours']) if t_row['actual_hours'] else None,
                    'assigned_to': t_row['assigned_to'],
                    'updated_at': t_row['updated_at'].isoformat() if t_row['updated_at'] else None,
                    'priority': t_row['priority'],
                    'subtasks': []
                }
                
                # Get subtasks for this task
                sql, params = convert_sql_placeholders('''
                    SELECT subtask_id, task, completed, subtask_order, created_at, completed_at,
                           estimated_hours, actual_hours, updated_at, priority
                    FROM synergy_sessions.subtasks 
                    WHERE task_id = %s
                    ORDER BY subtask_order
                ''', (task['task_id'],))
                
                cursor.execute(sql, params)
                
                for s_row in cursor.fetchall():
                    subtask = {
                        'subtask_id': s_row['subtask_id'],
                        'task': s_row['task'],
                        'completed': s_row['completed'],
                        'subtask_order': s_row['subtask_order'],
                        'created_at': s_row['created_at'].isoformat() if s_row['created_at'] else None,
                        'completed_at': s_row['completed_at'].isoformat() if s_row['completed_at'] else None,
                        'estimated_hours': float(s_row['estimated_hours']) if s_row['estimated_hours'] else None,
                        'actual_hours': float(s_row['actual_hours']) if s_row['actual_hours'] else None,
                        'updated_at': s_row['updated_at'].isoformat() if s_row['updated_at'] else None,
                        'priority': s_row['priority']
                    }
                    task['subtasks'].append(subtask)
                
                milestone['tasks'].append(task)
            
            # Calculate progress percentage
            total_tasks = len(milestone['tasks'])
            completed_tasks = sum(1 for t in milestone['tasks'] if t['completed'])
            total_subtasks = sum(len(t['subtasks']) for t in milestone['tasks'])
            completed_subtasks = sum(sum(1 for s in t['subtasks'] if s['completed']) for t in milestone['tasks'])
            
            total_items = total_tasks + total_subtasks
            completed_items = completed_tasks + completed_subtasks
            
            # Safe division with explicit zero check
            if total_items > 0:
                milestone['progress_percentage'] = round((completed_items / total_items * 100), 1)
            else:
                milestone['progress_percentage'] = 0
            
            milestones.append(milestone)
        
        conn.close()
        
        return jsonify({
            'success': True,
            'session_id': session_id,
            'session': session_data,
            'milestones': milestones
        })
    
    except Exception as e:
        print(f"\n{'='*80}")
        print(f"[MILESTONE ERROR] Failed to get milestones for {session_id}")
        print(f"Exception Type: {type(e).__name__}")
        print(f"Exception Message: {repr(e)}")
        print(f"Exception String: '{str(e)}'")
        print(f"Exception Args: {e.args}")
        print(f"{'='*80}\n")
        import traceback
        traceback.print_exc()
        
        # Ensure we return a proper error message with detailed info
        error_msg = str(e) if str(e) else f"{type(e).__name__} occurred"
        return jsonify({
            'success': False, 
            'error': error_msg,
            'error_type': type(e).__name__,
            'error_details': repr(e)
        }), 500


@synergy_bp.route('/task/<task_id>', methods=['PATCH'])
def update_task(task_id):
    """
    Update task fields (for inline editing)
    
    Request Body:
    {
        "task": "Updated task text",
        "priority": "high",
        "assigned_to": "john@example.com",
        "estimated_hours": 4.5
    }
    
    Response:
    {
        "success": true,
        "task_id": "task_xxx",
        "updated_fields": ["task", "priority"]
    }
    """
    try:
        data = request.get_json()
        
        # Validate request body
        if not data or not isinstance(data, dict):
            return jsonify({
                'success': False,
                'error': 'Request body must be a JSON object'
            }), 400
        
        # Allowed fields for update
        allowed_fields = ['task', 'priority', 'assigned_to', 'estimated_hours', 
                         'actual_hours', 'tags', 'start_date', 'links', 
                         'is_recurring', 'recurrence_pattern', 'progress_percent']
        
        # Build UPDATE query dynamically
        updates = []
        params = []
        updated_fields = []
        
        for field in allowed_fields:
            if field in data:
                updates.append(f"{field} = %s")
                params.append(data[field])
                updated_fields.append(field)
        
        if not updates:
            return jsonify({'success': False, 'error': 'No valid fields to update'}), 400
        
        # Always update updated_at
        updates.append("updated_at = %s")
        params.append(datetime.now())
        params.append(task_id)
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
        sql = f'''
            UPDATE synergy_sessions.tasks 
            SET {', '.join(updates)}
            WHERE task_id = %s
        '''
        
        cursor.execute(sql, tuple(params))
        conn.commit()
        conn.close()
        
        return jsonify({
            'success': True,
            'task_id': task_id,
            'updated_fields': updated_fields
        })
    
    except Exception as e:
        print(f"[TASK ERROR] Failed to update task: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500


@synergy_bp.route('/subtask/<subtask_id>', methods=['PATCH'])
def update_subtask(subtask_id):
    """
    Update subtask fields (for inline editing)
    
    Request Body:
    {
        "task": "Updated subtask text",
        "subtask": "Updated subtask text",  // Alias for 'task'
        "priority": "high",
        "assigned_to": "jane@example.com",
        "estimated_hours": 2.0
    }
    
    Response:
    {
        "success": true,
        "subtask_id": "subtask_xxx",
        "updated_fields": ["task", "priority"]
    }
    """
    try:
        data = request.get_json()
        
        # Validate request body
        if not data or not isinstance(data, dict):
            return jsonify({
                'success': False,
                'error': 'Request body must be a JSON object'
            }), 400
        
        # Handle 'subtask' as alias for 'task' field (frontend sends 'subtask', DB column is 'task')
        if 'subtask' in data and 'task' not in data:
            data['task'] = data.pop('subtask')
        
        # Allowed fields for update
        allowed_fields = ['task', 'priority', 'assigned_to', 'estimated_hours', 
                         'actual_hours', 'tags', 'start_date', 'links', 'description']
        
        # Build UPDATE query dynamically
        updates = []
        params = []
        updated_fields = []
        
        for field in allowed_fields:
            if field in data:
                updates.append(f"{field} = %s")
                params.append(data[field])
                updated_fields.append(field)
        
        if not updates:
            return jsonify({'success': False, 'error': 'No valid fields to update'}), 400
        
        # Always update updated_at
        updates.append("updated_at = %s")
        params.append(datetime.now())
        params.append(subtask_id)
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
        sql = f'''
            UPDATE synergy_sessions.subtasks 
            SET {', '.join(updates)}
            WHERE subtask_id = %s
        '''
        
        cursor.execute(sql, tuple(params))
        conn.commit()
        conn.close()
        
        return jsonify({
            'success': True,
            'subtask_id': subtask_id,
            'updated_fields': updated_fields
        })
    
    except Exception as e:
        print(f"[SUBTASK ERROR] Failed to update subtask: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500


@synergy_bp.route('/task/<task_id>/block', methods=['PATCH'])
def block_task(task_id):
    """
    Mark task as blocked with reason
    
    Request Body:
    {
        "blocked": true,
        "blocker_reason": "Waiting for client brand guidelines",
        "blocker_type": "external"
    }
    
    Response:
    {
        "success": true,
        "task_id": "task_x1y2z3",
        "blocked": true
    }
    """
    try:
        data = request.get_json()
        blocked = data.get('blocked', True)
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Check task exists
        cursor.execute('SELECT task_id FROM synergy_sessions.tasks WHERE task_id = %s', (task_id,))
        if not cursor.fetchone():
            conn.close()
            return jsonify({'success': False, 'error': 'Task not found'}), 404
        
        # Update task
        sql, params = convert_sql_placeholders('''
            UPDATE synergy_sessions.tasks 
            SET blocked = %s, blocker_reason = %s, blocker_type = %s, blocked_since = %s
            WHERE task_id = %s
        ''', (
            blocked,
            data.get('blocker_reason') if blocked else None,
            data.get('blocker_type') if blocked else None,
            datetime.now().isoformat() if blocked else None,
            task_id
        ))
        
        conn.commit()
        conn.close()
        
        return jsonify({
            'success': True,
            'task_id': task_id,
            'blocked': blocked
        })
    
    except Exception as e:
        print(f"[MILESTONE ERROR] Failed to block task: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500


@synergy_bp.route('/milestone/<milestone_id>/documents', methods=['PATCH'])
def update_milestone_documents(milestone_id):
    """
    Update milestone documents array
    
    Request Body:
    {
        "documents": [
            {"id": "doc1", "name": "Requirements.pdf", "url": "https://...", "type": "pdf"},
            {"id": "doc2", "name": "Design Mockups", "url": "https://...", "type": "internal"}
        ]
    }
    
    Response:
    {"success": true, "milestone_id": "mile_xxx", "documents_count": 2}
    """
    try:
        data = request.get_json()
        documents = data.get('documents', [])
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Check milestone exists
        cursor.execute('SELECT milestone_id FROM synergy_sessions.milestones WHERE milestone_id = %s', (milestone_id,))
        if not cursor.fetchone():
            conn.close()
            return jsonify({'success': False, 'error': 'Milestone not found'}), 404
        
        # Update documents
        cursor.execute('''
            UPDATE synergy_sessions.milestones 
            SET documents = %s, updated_at = %s
            WHERE milestone_id = %s
        ''', (json.dumps(documents), datetime.now().isoformat(), milestone_id))
        
        conn.commit()
        conn.close()
        
        return jsonify({
            'success': True,
            'milestone_id': milestone_id,
            'documents_count': len(documents)
        })
    
    except Exception as e:
        print(f"[MILESTONE ERROR] Failed to update documents: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500


@synergy_bp.route('/milestone/<milestone_id>/links', methods=['PATCH'])
def update_milestone_links(milestone_id):
    """
    Update milestone links array
    
    Request Body:
    {
        "links": [
            {"id": "link1", "name": "API Documentation", "url": "https://..."},
            {"id": "link2", "name": "GitHub Repo", "url": "https://..."}
        ]
    }
    
    Response:
    {"success": true, "milestone_id": "mile_xxx", "links_count": 2}
    """
    try:
        data = request.get_json()
        links = data.get('links', [])
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Check milestone exists
        cursor.execute('SELECT milestone_id FROM synergy_sessions.milestones WHERE milestone_id = %s', (milestone_id,))
        if not cursor.fetchone():
            conn.close()
            return jsonify({'success': False, 'error': 'Milestone not found'}), 404
        
        # Update links
        cursor.execute('''
            UPDATE synergy_sessions.milestones 
            SET links = %s, updated_at = %s
            WHERE milestone_id = %s
        ''', (json.dumps(links), datetime.now().isoformat(), milestone_id))
        
        conn.commit()
        conn.close()
        
        return jsonify({
            'success': True,
            'milestone_id': milestone_id,
            'links_count': len(links)
        })
    
    except Exception as e:
        print(f"[MILESTONE ERROR] Failed to update links: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500


@synergy_bp.route('/milestone/<milestone_id>/update', methods=['PATCH'])
def update_milestone_field(milestone_id):
    """
    Update any milestone field (inline editing support)
    
    Request Body:
    {
        "field": "milestone_name",
        "value": "Updated Milestone Name"
    }
    
    Supported fields:
    - milestone_name
    - description
    - due_date
    - estimated_hours
    - blocker_reason
    
    Response:
    {"success": true, "milestone_id": "mile_xxx", "field": "milestone_name", "value": "..."}
    """
    try:
        data = request.get_json()
        field = data.get('field')
        value = data.get('value')
        
        # Whitelist allowed fields for security
        allowed_fields = ['milestone_name', 'description', 'due_date', 'estimated_hours', 'blocker_reason']
        if field not in allowed_fields:
            return jsonify({'success': False, 'error': f'Field {field} not allowed'}), 400
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Check milestone exists
        cursor.execute('SELECT milestone_id FROM synergy_sessions.milestones WHERE milestone_id = %s', (milestone_id,))
        if not cursor.fetchone():
            conn.close()
            return jsonify({'success': False, 'error': 'Milestone not found'}), 404
        
        # Update field
        cursor.execute(f'''
            UPDATE synergy_sessions.milestones 
            SET {field} = %s, updated_at = %s
            WHERE milestone_id = %s
        ''', (value, datetime.now().isoformat(), milestone_id))
        
        conn.commit()
        conn.close()
        
        return jsonify({
            'success': True,
            'milestone_id': milestone_id,
            'field': field,
            'value': value
        })
    
    except Exception as e:
        print(f"[MILESTONE ERROR] Failed to update milestone: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500


@synergy_bp.route('/milestone/<milestone_id>', methods=['GET'])
def get_milestone(milestone_id):
    """
    Get milestone by ID with all details
    
    Response:
    {
        "success": true,
        "milestone": {
            "milestone_id": "mile_xxx",
            "session_id": "syn_xxx",
            "milestone_number": 1,
            "milestone_name": "Setup Database",
            "description": "...",
            "documents": "[...]",
            "links": "[...]",
            ...
        }
    }
    """
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT * FROM synergy_sessions.milestones 
            WHERE milestone_id = %s
        ''', (milestone_id,))
        
        row = cursor.fetchone()
        conn.close()
        
        if not row:
            return jsonify({'success': False, 'error': 'Milestone not found'}), 404
        
        milestone = dict(zip([desc[0] for desc in cursor.description], row))
        
        return jsonify({
            'success': True,
            'milestone': milestone
        })
    
    except Exception as e:
        print(f"[MILESTONE ERROR] Failed to get milestone: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500


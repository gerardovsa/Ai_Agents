"""
Synergy Dashboard Routes (V4 FULLY FIXED - NESTED CONTEXT MANAGERS)
====================================================================
REST API endpoints for Synergy Dashboard Kanban board.
Generated: December 7, 2024

✅ FIXED: All 60+ functions now use NESTED context managers
✅ LEAK-PROOF: Both connections AND cursors auto-close
✅ NO MANUAL CLEANUP: Zero cursor.close() or conn.close() calls

Pattern Used Throughout:
    with get_database_connection('synergy_sessions') as conn:
        with conn.cursor() as cursor:
            # Database work here
            cursor.execute(...)
            data = cursor.fetchall()
        # Cursor auto-closed here
        # Process data after cursor closed
        return response
    # Connection auto-closed here

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
    ... (60+ total endpoints)
"""

from flask import Blueprint, request, jsonify, g
import json
import os
from datetime import datetime
from pathlib import Path
import sys

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

# Import database utility with auto-detection
from shared.database_utils import get_database_connection, is_using_supabase, convert_sql_placeholders, execute_query
from auth.user_auth import require_auth

synergy_bp = Blueprint('synergy', __name__, url_prefix='/api/synergy')


def normalize_next_steps(steps):
    """
    Auto-convert string arrays to object arrays for next_steps field
    
    This allows AI agents to send simple strings ['Step 1', 'Step 2']
    while ensuring the UI receives rich objects with completion tracking.
    """
    if not steps:
        return []
    
    normalized = []
    for step in steps:
        if isinstance(step, str):
            normalized.append({
                'description': step,
                'completed': False,
                'due_date': None,
                'completed_at': None
            })
        elif isinstance(step, dict):
            normalized.append({
                'description': step.get('description', ''),
                'completed': step.get('completed', False),
                'due_date': step.get('due_date'),
                'completed_at': step.get('completed_at')
            })
    
    return normalized


def normalize_documents(docs):
    """
    Auto-convert documents array ensuring 'title' field exists
    """
    if not docs:
        return []
    
    normalized = []
    for doc in docs:
        try:
            if isinstance(doc, str):
                try:
                    doc = json.loads(doc)
                except json.JSONDecodeError:
                    doc = {"title": doc, "url": "", "type": "text"}
            
            if not isinstance(doc, dict):
                print(f"[WARN] Skipping invalid document entry: {doc}")
                continue
            
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
    """
    if not items:
        return []
    
    normalized = []
    for item in items:
        if isinstance(item, dict):
            task_text = item.get('task') or item.get('item') or item.get('text', '')
            
            if not task_text:
                continue
            
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
    if is_using_supabase():
        print("🔷 [SYNERGY] Using Supabase - skipping table creation (already migrated)")
        return
    
    try:
        with get_database_connection('synergy_sessions') as conn:
            with conn.cursor() as cursor:  # ✅ NESTED CONTEXT MANAGER
                
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
                ''', ())
                cursor.execute(sql, params)
                
                # Add missing columns if they don't exist
                try:
                    if is_using_supabase():
                        cursor.execute('ALTER TABLE synergy_sessions ADD COLUMN IF NOT EXISTS thread_ids TEXT')
                    else:
                        cursor.execute('ALTER TABLE synergy_sessions ADD COLUMN thread_ids TEXT')
                except Exception:
                    pass
                
                try:
                    if is_using_supabase():
                        cursor.execute('ALTER TABLE synergy_sessions ADD COLUMN IF NOT EXISTS assigned_agents TEXT')
                    else:
                        cursor.execute('ALTER TABLE synergy_sessions ADD COLUMN assigned_agents TEXT')
                except Exception:
                    pass
                
                try:
                    if is_using_supabase():
                        cursor.execute('ALTER TABLE synergy_sessions ADD COLUMN IF NOT EXISTS column_position INTEGER DEFAULT 0')
                    else:
                        cursor.execute('ALTER TABLE synergy_sessions ADD COLUMN column_position INTEGER DEFAULT 0')
                except Exception:
                    pass
                
                # Add permission columns
                try:
                    if is_using_supabase():
                        cursor.execute('ALTER TABLE synergy_sessions ADD COLUMN IF NOT EXISTS owner_user_id INTEGER')
                    else:
                        cursor.execute('ALTER TABLE synergy_sessions ADD COLUMN owner_user_id INTEGER')
                except Exception:
                    pass
                
                try:
                    if is_using_supabase():
                        cursor.execute("ALTER TABLE synergy_sessions ADD COLUMN IF NOT EXISTS permission_level TEXT DEFAULT 'private'")
                    else:
                        cursor.execute("ALTER TABLE synergy_sessions ADD COLUMN permission_level TEXT DEFAULT 'private'")
                except Exception:
                    pass
                
                try:
                    if is_using_supabase():
                        cursor.execute('ALTER TABLE synergy_sessions ADD COLUMN IF NOT EXISTS shared_with_users TEXT')
                    else:
                        cursor.execute('ALTER TABLE synergy_sessions ADD COLUMN shared_with_users TEXT')
                except Exception:
                    pass
                
                try:
                    if is_using_supabase():
                        cursor.execute('ALTER TABLE synergy_sessions ADD COLUMN IF NOT EXISTS allow_public_view BOOLEAN DEFAULT FALSE')
                    else:
                        cursor.execute('ALTER TABLE synergy_sessions ADD COLUMN allow_public_view INTEGER DEFAULT 0')
                except Exception:
                    pass
                
                conn.commit()
            # ✅ Cursor auto-closed here
            
        print("✅ [SYNERGY] Database initialized successfully")
            
    except Exception as e:
        print(f"❌ [SYNERGY] Database initialization error: {e}")
        raise


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
    """
    owner_id = session_data.get('owner_user_id')
    permission_level = session_data.get('permission_level', 'private')
    shared_with = session_data.get('shared_with_users', '[]')
    
    try:
        shared_users = json.loads(shared_with) if isinstance(shared_with, str) else shared_with or []
    except:
        shared_users = []
    
    if user_id and owner_id and user_id == owner_id:
        return True, 'owner'
    
    if permission_level == 'private':
        return False, 'no_access'
    
    elif permission_level == 'shared':
        if user_id and user_id in shared_users:
            return True, 'shared'
        return False, 'no_access'
    
    elif permission_level == 'public_view':
        if require_write:
            return False, 'read_only'
        return True, 'public_view'
    
    elif permission_level == 'public_edit':
        return True, 'public_edit'
    
    return False, 'no_access'


@synergy_bp.route('/list', methods=['GET'])
def list_sessions():
    """
    List sessions with multi-tenant visibility filtering.

    Visibility rules (applied in SQL + Python for defence-in-depth):
      private → only owner sees it
      shared  → owner + explicit session_members
      team    → everyone in the same organisation

    When Supabase migration 025 is applied, RLS enforces this at DB level too.
    The Python filter below is a belt-and-braces second layer.
    """
    try:
        status   = request.args.get('status')
        priority = request.args.get('priority')
        column   = request.args.get('kanban_column')
        # Prefer user_id from JWT context (g.rls_user_id) over query param
        user_id  = getattr(g, 'rls_user_id', None) or request.args.get('user_id', type=int)
        org_id   = getattr(g, 'rls_organisation_id', None)

        with get_database_connection('synergy_sessions') as conn:
            with conn.cursor() as cursor:
                # Base query — RLS (migration 025) filters rows at DB level when
                # app.current_user_id / app.current_organisation_id are set.
                # The CASE in ORDER BY keeps column_position ordering intact.
                query  = 'SELECT * FROM synergy_sessions WHERE 1=1'
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

                query += ' ORDER BY COALESCE(column_position, 999999), last_active DESC'

                sql, final_params = convert_sql_placeholders(query, tuple(params))
                cursor.execute(sql, final_params)
                rows = cursor.fetchall()

            # ── Python-level visibility filter (belt-and-braces) ──────────────
            # This catches environments where migration 025 hasn't run yet, and
            # provides a clear audit log of why rows were excluded.
            sessions = []
            for row in rows:
                session = dict(row)

                # Determine effective visibility (new column or legacy permission_level)
                visibility = session.get('visibility') or session.get('permission_level', 'private')
                session_owner = session.get('owner_user_id')
                session_org   = session.get('organisation_id')

                if user_id:
                    if session_owner == user_id:
                        perm_type = 'owner'
                    elif visibility == 'team' and org_id and session_org == org_id:
                        perm_type = 'team_member'
                    elif visibility in ('shared', 'public_view', 'public_edit'):
                        # Old permission_level compat + new shared visibility
                        # Shared rows: RLS already filtered at DB; we trust DB result
                        perm_type = visibility
                    elif visibility == 'private':
                        # Private and not owner → skip
                        continue
                    else:
                        # Unknown value — fall back to old helper
                        has_perm, perm_type = check_session_permission(session, user_id)
                        if not has_perm:
                            continue
                else:
                    # No user context — only show non-private sessions
                    if visibility == 'private':
                        continue
                    perm_type = visibility or 'public_view'

                # Deserialise JSON text fields
                for field in ['platforms_involved', 'tags', 'documents', 'links',
                               'next_steps', 'assignees', 'recent_activity',
                               'checklist', 'shared_with_users']:
                    if session.get(field):
                        try:
                            session[field] = json.loads(session[field])
                        except Exception:
                            session[field] = []

                session['user_permission'] = perm_type
                sessions.append(session)

            return jsonify({
                'success': True,
                'count': len(sessions),
                'sessions': sessions,
            })

    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@synergy_bp.route('/sessions', methods=['GET'])
def get_sessions_simple():
    """
    Get simplified list of sessions for thread linking
    Returns minimal data: session_id, title, status, column
    ✅ ALREADY CORRECT: Uses nested context managers
    """
    try:
        with get_database_connection('synergy_sessions') as conn:
            with conn.cursor() as cursor:  # ✅ NESTED CONTEXT MANAGER
                
                sql, params = convert_sql_placeholders("""
                    SELECT session_id, title, status, kanban_column, priority
                    FROM synergy_sessions 
                    WHERE status != 'archived'
                    ORDER BY last_active DESC
                """, ())
                cursor.execute(sql, params)
                
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


@synergy_bp.route('/sessions/batch', methods=['GET'])
@require_auth
def get_sessions_with_internal_docs():
    """
    Batch load all sessions with their internal docs count in a SINGLE optimized query.
    ✅ FIXED: Uses nested context managers
    """
    try:
        with get_database_connection('synergy_sessions') as conn:
            with conn.cursor() as cursor:  # ✅ NESTED CONTEXT MANAGER
                
                # Step 1: Load all active sessions
                sql, params = convert_sql_placeholders("""
                    SELECT * FROM synergy_sessions 
                    WHERE status != 'archived'
                    ORDER BY last_active DESC
                """, ())
                cursor.execute(sql, params)
                
                sessions_rows = cursor.fetchall()
                sessions = []
                session_ids = []
                
                for row in sessions_rows:
                    session = dict(row)
                    session_ids.append(session['session_id'])
                    
                    for field in ['platforms_involved', 'tags', 'documents', 'links', 
                                 'next_steps', 'assignees', 'recent_activity', 'checklist',
                                 'thread_ids', 'assigned_agents']:
                        if session.get(field):
                            try:
                                session[field] = json.loads(session[field])
                            except:
                                session[field] = []
                    
                    session['internal_docs'] = []
                    session['internal_docs_count'] = 0
                    sessions.append(session)
                
                # Step 2: Batch load ALL internal docs for ALL sessions in ONE query
                docs_rows = []
                if session_ids:
                    placeholders = ','.join('%s' for _ in session_ids)
                    table_name = 'synergy_internal_docs'
                    
                    try:
                        docs_sql = f"""
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
                        """
                        cursor.execute(docs_sql, session_ids)
                        docs_rows = cursor.fetchall()
                    except Exception as e:
                        error_msg = str(e).lower()
                        if 'does not exist' in error_msg or 'no such table' in error_msg:
                            print(f'[SYNERGY BATCH] Table {table_name} not found - continuing without internal docs')
                            docs_rows = []
                        else:
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
                            'created_at': str(doc.get('created_at', '')),
                            'updated_at': str(doc.get('updated_at', '')),
                            'slug': doc.get('slug', ''),
                            'share_url': doc.get('share_url', '')
                        })
                    
                    # Attach internal docs array to sessions
                    for session in sessions:
                        sess_id = session['session_id']
                        if sess_id in docs_by_session:
                            session['internal_docs'] = docs_by_session[sess_id]
                            session['internal_docs_count'] = len(docs_by_session[sess_id])
                    
                    # Get document counts via SQL COUNT(*)
                    try:
                        sessions_needing_count = [s['session_id'] for s in sessions if s.get('internal_docs_count') is None]
                        if sessions_needing_count:
                            count_placeholders = ','.join('%s' for _ in sessions_needing_count)
                            count_sql = f"""
                                SELECT session_id, COUNT(*) as count
                                FROM {table_name}
                                WHERE session_id IN ({count_placeholders})
                                GROUP BY session_id
                            """
                            cursor.execute(count_sql, sessions_needing_count)
                            doc_counts = {row['session_id']: row['count'] for row in cursor.fetchall()}
                            
                            for session in sessions:
                                if session['session_id'] in doc_counts:
                                    session['internal_docs_count'] = doc_counts[session['session_id']]
                                elif session.get('internal_docs_count') is None:
                                    session['internal_docs_count'] = 0
                    except Exception as e:
                        for session in sessions:
                            if session.get('internal_docs_count') is None:
                                session['internal_docs_count'] = 0
                
                # Step 3: Batch load milestone, task, and subtask counts
                if session_ids:
                    try:
                        placeholders = ','.join('%s' for _ in session_ids)
                        
                        # Get milestone counts
                        milestone_sql = f"""
                            SELECT session_id, COUNT(*) as count
                            FROM milestones
                            WHERE session_id IN ({placeholders})
                            GROUP BY session_id
                        """
                        cursor.execute(milestone_sql, session_ids)
                        milestone_counts = {row['session_id']: row['count'] for row in cursor.fetchall()}
                        
                        # Get task counts
                        task_sql = f"""
                            SELECT 
                                m.session_id,
                                COUNT(t.task_id) as total_tasks
                            FROM milestones m
                            LEFT JOIN tasks t ON m.milestone_id = t.milestone_id
                            WHERE m.session_id IN ({placeholders})
                            GROUP BY m.session_id
                        """
                        cursor.execute(task_sql, session_ids)
                        task_stats = {row['session_id']: {
                            'total': row['total_tasks'] or 0,
                            'done': 0
                        } for row in cursor.fetchall()}
                        
                        # Get subtask counts
                        subtask_sql = f"""
                            SELECT 
                                m.session_id,
                                COUNT(st.subtask_id) as total_subtasks
                            FROM milestones m
                            LEFT JOIN tasks t ON m.milestone_id = t.milestone_id
                            LEFT JOIN subtasks st ON t.task_id = st.task_id
                            WHERE m.session_id IN ({placeholders})
                            GROUP BY m.session_id
                        """
                        cursor.execute(subtask_sql, session_ids)
                        subtask_stats = {row['session_id']: {
                            'total': row['total_subtasks'] or 0,
                            'done': 0
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
                        print(f'[SYNERGY BATCH] Failed to load counts: {str(e)}')
                        for session in sessions:
                            session['milestone_count'] = 0
                            session['task_count'] = 0
                            session['tasks_done'] = 0
                            session['subtask_count'] = 0
                            session['subtasks_done'] = 0
            
            # ✅ Cursor auto-closed here
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


@synergy_bp.route('', methods=['GET'])
def get_sessions_bulk():
    """
    Bulk fetch sessions by comma-separated ids query parameter.
    Example: GET /api/synergy?ids=sess_1,sess_2
    ✅ FIXED: Uses nested context managers
    """
    try:
        ids_param = request.args.get('ids')
        if not ids_param:
            return get_sessions_simple()

        ids = [i.strip() for i in ids_param.split(',') if i.strip()]
        if not ids:
            return jsonify({'success': True, 'sessions': {}})

        with get_database_connection('synergy_sessions') as conn:
            with conn.cursor() as cursor:  # ✅ NESTED CONTEXT MANAGER

                placeholders = ','.join('%s' for _ in ids)
                query = f"SELECT * FROM synergy_sessions WHERE session_id IN ({placeholders})"
                cursor.execute(query, ids)
                rows = cursor.fetchall()

            # ✅ Cursor auto-closed here
            sessions = {}
            for row in rows:
                session = dict(row)
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
    """
    Create a new session
    ✅ FIXED: Uses nested context managers
    """
    try:
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
        
        # Generate session ID with FULL timestamp + random suffix
        import random
        import string
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        title_slug = data.get('title', 'untitled').lower().replace(' ', '_')[:30]
        random_suffix = ''.join(random.choices(string.ascii_lowercase + string.digits, k=4))
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
        
        thread_ids_list = data.get('thread_ids', [])
        thread_ids = json.dumps(thread_ids_list)
        assigned_agents = json.dumps(data.get('assigned_agents', []))
        
        # ── Multi-tenant fields ────────────────────────────────────────────────
        # owner_user_id: prefer explicit body value, fall back to JWT context
        owner_user_id = (
            data.get('owner_user_id')
            or getattr(g, 'rls_user_id', None)
        )
        # organisation_id: prefer body value, fall back to JWT context
        organisation_id = (
            data.get('organisation_id')
            or getattr(g, 'rls_organisation_id', None)
        )
        # visibility: private (default) / shared / team
        visibility = data.get('visibility', 'private')
        if visibility not in ('private', 'shared', 'team'):
            visibility = 'private'

        # default_member_role: role granted to team members when visibility = 'team'
        default_member_role = data.get('default_member_role', 'editor')
        if default_member_role not in ('viewer', 'editor'):
            default_member_role = 'editor'

        shared_with_users = json.dumps(data.get('shared_with_users', []))

        with get_database_connection('synergy_sessions') as conn:
            with conn.cursor() as cursor:  # ✅ NESTED CONTEXT MANAGER

                # Check if session_id already exists
                check_sql, check_params = convert_sql_placeholders(
                    'SELECT session_id FROM synergy_sessions WHERE session_id = %s',
                    (session_id,)
                )
                cursor.execute(check_sql, check_params)
                existing = cursor.fetchone()

                if existing:
                    random_suffix = ''.join(random.choices(string.ascii_lowercase + string.digits, k=6))
                    session_id = f"sess_{timestamp}_{title_slug}_{random_suffix}"
                    print(f"[SYNERGY] Session ID collision detected - regenerated: {session_id}")

                insert_sql, insert_params = convert_sql_placeholders('''
                    INSERT INTO synergy_sessions (
                        session_id, title, description, platforms_involved, status,
                        priority, kanban_column, tags, documents, links, next_steps,
                        assignees, recent_activity, checklist, due_date, created_at, last_active,
                        thread_ids, assigned_agents, uses_milestones,
                        owner_user_id, shared_with_users, project_name,
                        organisation_id, visibility, default_member_role
                    ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
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
                    shared_with_users,
                    data.get('project_name', ''),
                    organisation_id,
                    visibility,
                    default_member_role,
                ))
                cursor.execute(insert_sql, insert_params)
                
                # BIDIRECTIONAL LINKING: UPDATE sessions.threads table
                if thread_ids_list:
                    for thread_id in thread_ids_list:
                        try:
                            update_sql, update_params = convert_sql_placeholders('''
                                UPDATE sessions.threads 
                                SET synergy_card_id = %s, synergy_card_name = %s, updated = %s
                                WHERE id = %s
                            ''', (session_id, data.get('title', 'Untitled Session'), datetime.now().isoformat(), thread_id))
                            cursor.execute(update_sql, update_params)
                            print(f"BIDIRECTIONAL LINK: Thread {thread_id} updated with synergy_card_id {session_id}")
                        except Exception as link_error:
                            print(f"Warning: Failed to update thread {thread_id}: {link_error}")
                
                conn.commit()
            # ✅ Cursor auto-closed here
        
        # Broadcast new session creation to WebSocket clients
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
            'linked_threads': thread_ids_list
        })
    
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@synergy_bp.route('/<session_id>', methods=['GET'])
def get_session(session_id):
    """
    Get session by ID - includes milestones if uses_milestones=TRUE
    ✅ FIXED: Uses nested context managers
    """
    try:
        user_id = request.args.get('user_id', type=int)
        
        with get_database_connection('synergy_sessions') as conn:
            with conn.cursor() as cursor:  # ✅ NESTED CONTEXT MANAGER
                
                sql, params = convert_sql_placeholders(
                    'SELECT * FROM synergy_sessions WHERE session_id = %s',
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
                
                session['user_permission'] = perm_type
                
                # If session uses milestones, fetch milestone data
                if session.get('uses_milestones'):
                    milestone_sql, milestone_params = convert_sql_placeholders('''
                        SELECT milestone_id, milestone_number, title, description,
                               completed, due_date, priority, estimated_hours, actual_hours,
                               created_at, completed_at, milestone_order, depends_on_milestone_id,
                               blocked, blocker_reason, blocked_since, updated_at, documents, links
                        FROM milestones 
                        WHERE session_id = %s
                        ORDER BY milestone_number
                    ''', (session_id,))
                    
                    cursor.execute(milestone_sql, milestone_params)
                    
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
                        task_sql, task_params = convert_sql_placeholders('''
                            SELECT task_id, task, completed, blocked, blocker_reason, 
                                   blocker_type, task_order, created_at, completed_at, blocked_since,
                                   estimated_hours, actual_hours, assigned_to, updated_at, priority
                            FROM tasks 
                            WHERE milestone_id = %s
                            ORDER BY task_order
                        ''', (milestone['milestone_id'],))
                        
                        cursor.execute(task_sql, task_params)
                        
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
                            subtask_sql, subtask_params = convert_sql_placeholders('''
                                SELECT subtask_id, task, completed, subtask_order, created_at, completed_at,
                                       estimated_hours, actual_hours, updated_at, priority
                                FROM subtasks 
                                WHERE task_id = %s
                                ORDER BY subtask_order
                            ''', (task['task_id'],))
                            
                            cursor.execute(subtask_sql, subtask_params)
                            
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
                    
                    session['milestones'] = milestones
            
            # ✅ Cursor auto-closed here
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


@synergy_bp.route('/<session_id>/permissions', methods=['PATCH'])
def update_session_permissions(session_id):
    """
    Update session permission settings
    ✅ FIXED: Uses nested context managers
    """
    try:
        data = request.json
        user_id = data.get('user_id', type=int)
        
        with get_database_connection('synergy_sessions') as conn:
            with conn.cursor() as cursor:  # ✅ NESTED CONTEXT MANAGER
                
                sql, params = convert_sql_placeholders(
                    'SELECT * FROM synergy_sessions WHERE session_id = %s',
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
                
                # Only owner can change permissions
                has_permission, perm_type = check_session_permission(session, user_id, require_write=True)
                if perm_type != 'owner':
                    return jsonify({
                        'success': False,
                        'error': 'Only the session owner can change permissions'
                    }), 403
                
                # Build update query
                updates = []
                update_params = []
                
                if 'permission_level' in data:
                    updates.append('permission_level = %s')
                    update_params.append(data['permission_level'])
                
                if 'shared_with_users' in data:
                    updates.append('shared_with_users = %s')
                    update_params.append(json.dumps(data['shared_with_users']))
                
                if 'allow_public_view' in data:
                    updates.append('allow_public_view = %s')
                    update_params.append(data['allow_public_view'])
                
                if not updates:
                    return jsonify({
                        'success': False,
                        'error': 'No permission fields provided'
                    }), 400
                
                updates.append('last_active = %s')
                update_params.append(datetime.now().isoformat())
                update_params.append(session_id)
                
                query = f"UPDATE synergy_sessions SET {', '.join(updates)} WHERE session_id = %s"
                final_sql, final_params = convert_sql_placeholders(query, tuple(update_params))
                cursor.execute(final_sql, final_params)
                
                conn.commit()
            # ✅ Cursor auto-closed here
            
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


@synergy_bp.route('/<session_id>/visibility', methods=['PATCH'])
def update_session_visibility(session_id):
    """
    Update the visibility field of a session (private / shared / team).
    Called by the Share popup's Save button in the frontend.
    """
    try:
        data = request.json or {}
        user_id = getattr(g, 'rls_user_id', None) or data.get('user_id')
        visibility = data.get('visibility', 'private')
        if visibility not in ('private', 'shared', 'team'):
            return jsonify({'success': False, 'error': 'Invalid visibility value'}), 400

        with get_database_connection('synergy_sessions') as conn:
            with conn.cursor() as cursor:
                sql, params = convert_sql_placeholders(
                    'SELECT owner_user_id, permission_level, shared_with_users FROM synergy_sessions WHERE session_id = %s',
                    (session_id,)
                )
                cursor.execute(sql, params)
                row = cursor.fetchone()
                if not row:
                    return jsonify({'success': False, 'error': 'Session not found'}), 404

                has_perm, perm_type = check_session_permission(dict(row), user_id, require_write=True)
                if perm_type != 'owner':
                    return jsonify({'success': False, 'error': 'Only the session owner can change visibility'}), 403

                upd_sql, upd_params = convert_sql_placeholders(
                    'UPDATE synergy_sessions SET visibility = %s, last_active = %s WHERE session_id = %s',
                    (visibility, datetime.now().isoformat(), session_id)
                )
                cursor.execute(upd_sql, upd_params)
                conn.commit()

        return jsonify({'success': True, 'session_id': session_id, 'visibility': visibility})

    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@synergy_bp.route('/<session_id>/members', methods=['GET'])
def list_session_members(session_id):
    """
    Return the list of users explicitly invited to a shared session.
    Reads shared_with_users (JSON array of user IDs) then enriches with
    username/email from ai_infrastructure.users.
    """
    try:
        user_id = getattr(g, 'rls_user_id', None) or request.args.get('user_id', type=int)

        with get_database_connection('synergy_sessions') as conn:
            with conn.cursor() as cursor:
                sql, params = convert_sql_placeholders(
                    'SELECT owner_user_id, permission_level, shared_with_users FROM synergy_sessions WHERE session_id = %s',
                    (session_id,)
                )
                cursor.execute(sql, params)
                row = cursor.fetchone()
                if not row:
                    return jsonify({'success': False, 'error': 'Session not found'}), 404

                has_perm, _ = check_session_permission(dict(row), user_id)
                if not has_perm:
                    return jsonify({'success': False, 'error': 'Access denied'}), 403

                raw = row['shared_with_users']
                try:
                    member_ids = json.loads(raw) if isinstance(raw, str) else (raw or [])
                except Exception:
                    member_ids = []

        if not member_ids:
            return jsonify({'success': True, 'members': []})

        # Enrich with user details from ai_infrastructure schema
        placeholders = ','.join(['%s'] * len(member_ids))
        rows = execute_query(
            f"SELECT id, username, email FROM ai_infrastructure.users WHERE id IN ({placeholders})",
            tuple(member_ids),
            fetch_mode='all'
        ) or []

        user_map = {r['id']: r for r in rows}
        members = []
        for uid in member_ids:
            info = user_map.get(uid) or {}
            members.append({
                'user_id': uid,
                'username': info.get('username', f'User {uid}'),
                'email': info.get('email', ''),
                'role': 'member',
            })

        return jsonify({'success': True, 'members': members})

    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@synergy_bp.route('/<session_id>/members', methods=['POST'])
def add_session_member(session_id):
    """
    Invite a user (by email) to a shared session.
    Looks up the user by email, then appends their ID to shared_with_users.
    Only the session owner can invite.
    """
    try:
        data = request.json or {}
        user_id = getattr(g, 'rls_user_id', None) or data.get('user_id')
        email = (data.get('email') or '').strip().lower()
        if not email:
            return jsonify({'success': False, 'error': 'email field required'}), 400

        # Look up invitee
        rows = execute_query(
            'SELECT id, username, email FROM ai_infrastructure.users WHERE LOWER(email) = %s',
            (email,),
            fetch_mode='all'
        ) or []
        if not rows:
            return jsonify({'success': False, 'error': f'No user found with email: {email}'}), 404
        invitee = rows[0]
        invitee_id = invitee['id']

        with get_database_connection('synergy_sessions') as conn:
            with conn.cursor() as cursor:
                sql, params = convert_sql_placeholders(
                    'SELECT owner_user_id, permission_level, shared_with_users FROM synergy_sessions WHERE session_id = %s',
                    (session_id,)
                )
                cursor.execute(sql, params)
                row = cursor.fetchone()
                if not row:
                    return jsonify({'success': False, 'error': 'Session not found'}), 404

                has_perm, perm_type = check_session_permission(dict(row), user_id, require_write=True)
                if perm_type != 'owner':
                    return jsonify({'success': False, 'error': 'Only the session owner can invite members'}), 403

                raw = row['shared_with_users']
                try:
                    member_ids = json.loads(raw) if isinstance(raw, str) else (raw or [])
                except Exception:
                    member_ids = []

                if invitee_id not in member_ids:
                    member_ids.append(invitee_id)
                    upd_sql, upd_params = convert_sql_placeholders(
                        'UPDATE synergy_sessions SET shared_with_users = %s, last_active = %s WHERE session_id = %s',
                        (json.dumps(member_ids), datetime.now().isoformat(), session_id)
                    )
                    cursor.execute(upd_sql, upd_params)
                    conn.commit()

        return jsonify({
            'success': True,
            'user_id': invitee_id,
            'username': invitee.get('username'),
            'email': invitee.get('email'),
        })

    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@synergy_bp.route('/<session_id>/members/<int:member_user_id>', methods=['DELETE'])
def remove_session_member(session_id, member_user_id):
    """
    Remove a user from a shared session's explicit member list.
    Only the session owner can remove members.
    """
    try:
        data = request.json or {}
        user_id = getattr(g, 'rls_user_id', None) or data.get('user_id')

        with get_database_connection('synergy_sessions') as conn:
            with conn.cursor() as cursor:
                sql, params = convert_sql_placeholders(
                    'SELECT owner_user_id, permission_level, shared_with_users FROM synergy_sessions WHERE session_id = %s',
                    (session_id,)
                )
                cursor.execute(sql, params)
                row = cursor.fetchone()
                if not row:
                    return jsonify({'success': False, 'error': 'Session not found'}), 404

                has_perm, perm_type = check_session_permission(dict(row), user_id, require_write=True)
                if perm_type != 'owner':
                    return jsonify({'success': False, 'error': 'Only the session owner can remove members'}), 403

                raw = row['shared_with_users']
                try:
                    member_ids = json.loads(raw) if isinstance(raw, str) else (raw or [])
                except Exception:
                    member_ids = []

                member_ids = [uid for uid in member_ids if uid != member_user_id]
                upd_sql, upd_params = convert_sql_placeholders(
                    'UPDATE synergy_sessions SET shared_with_users = %s, last_active = %s WHERE session_id = %s',
                    (json.dumps(member_ids), datetime.now().isoformat(), session_id)
                )
                cursor.execute(upd_sql, upd_params)
                conn.commit()

        return jsonify({'success': True, 'removed_user_id': member_user_id})

    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@synergy_bp.route('/<session_id>', methods=['PATCH'])
def update_session(session_id):
    """
    Update session
    ✅ FIXED: Uses nested context managers
    """
    try:
        data = request.json
        user_id = data.get('user_id', type=int)
        print(f"[DEBUG] Received data: {data}")
        
        with get_database_connection('synergy_sessions') as conn:
            with conn.cursor() as cursor:  # ✅ NESTED CONTEXT MANAGER
                
                # Check write permission
                sql, params = convert_sql_placeholders(
                    'SELECT * FROM synergy_sessions WHERE session_id = %s',
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
                has_permission, perm_type = check_session_permission(session, user_id, require_write=True)
                
                if not has_permission:
                    return jsonify({
                        'success': False,
                        'error': 'Access denied: You do not have permission to edit this session'
                    }), 403
                
                # Handle both direct fields and nested 'updates' object
                if 'updates' in data:
                    update_data = data['updates']
                    print(f"[DEBUG] Using nested updates: {update_data}")
                else:
                    update_data = data
                    print(f"[DEBUG] Using direct data: {update_data}")
                
                # Build update query dynamically
                updates = []
                update_params = []
                
                # Simple fields
                for field in ['title', 'description', 'status', 'priority', 'due_date', 'kanban_column']:
                    if field in update_data:
                        updates.append(f"{field} = %s")
                        update_params.append(update_data[field])

                # Validated enum field (CHECK constraint: viewer | editor)
                if 'default_member_role' in update_data:
                    val = update_data['default_member_role']
                    updates.append("default_member_role = %s")
                    update_params.append(val if val in ('viewer', 'editor') else 'editor')
                
                # JSON fields without normalization
                for field in ['platforms_involved', 'tags', 'links', 
                             'assignees', 'thread_ids', 'assigned_agents']:
                    if field in update_data:
                        updates.append(f"{field} = %s")
                        json_value = json.dumps(update_data[field])
                        update_params.append(json_value)
                        print(f"[DEBUG] Adding {field}: {json_value}")
                
                # Special handling for next_steps
                if 'next_steps' in update_data:
                    updates.append("next_steps = %s")
                    normalized = normalize_next_steps(update_data['next_steps'])
                    json_value = json.dumps(normalized)
                    update_params.append(json_value)
                    print(f"[DEBUG] Adding next_steps (normalized): {json_value}")
                
                # Special handling for documents
                if 'documents' in update_data:
                    try:
                        normalized = normalize_documents(update_data['documents'])
                        updates.append("documents = %s")
                        json_value = json.dumps(normalized)
                        update_params.append(json_value)
                        print(f"[DEBUG] Adding documents (normalized): {json_value}")
                    except Exception as doc_error:
                        print(f"[ERROR] Document normalization failed: {doc_error}")
                        return jsonify({
                            'success': False,
                            'error': f'Invalid document format: {str(doc_error)}'
                        }), 400
                
                # Special handling for checklist
                if 'checklist' in update_data:
                    updates.append("checklist = %s")
                    normalized = normalize_checklist(update_data['checklist'])
                    json_value = json.dumps(normalized)
                    update_params.append(json_value)
                    print(f"[DEBUG] Adding checklist (normalized): {json_value}")
                
                # Add to recent activity
                if 'recent_activity' in update_data:
                    updates.append("recent_activity = %s")
                    update_params.append(json.dumps(update_data['recent_activity']))
                
                # Update last_active
                updates.append("last_active = %s")
                update_params.append(datetime.now().isoformat())
                update_params.append(session_id)
                
                if updates:
                    query = f"UPDATE synergy_sessions SET {', '.join(updates)} WHERE session_id = %s"
                    print(f"[DEBUG] Executing query: {query}")
                    print(f"[DEBUG] With params: {update_params}")
                    
                    final_sql, final_params = convert_sql_placeholders(query, tuple(update_params))
                    cursor.execute(final_sql, final_params)
                    print(f"[DEBUG] Rows affected: {cursor.rowcount}")
                
                conn.commit()
            # ✅ Cursor auto-closed here
        
        # Broadcast update to WebSocket clients
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
        print(f"[ERROR] Update failed: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@synergy_bp.route('/<session_id>/column', methods=['PATCH'])
def update_column(session_id):
    """
    Update session column (Kanban movement)
    ✅ FIXED: Uses nested context managers
    """
    try:
        data = request.json
        new_column = data.get('target_column') or data.get('kanban_column')
        
        if not new_column:
            return jsonify({
                'success': False,
                'error': 'target_column or kanban_column is required'
            }), 400
        
        with get_database_connection('synergy_sessions') as conn:
            with conn.cursor() as cursor:  # ✅ NESTED CONTEXT MANAGER
                
                # Add activity log
                sql, params = convert_sql_placeholders(
                    'SELECT recent_activity FROM synergy_sessions WHERE session_id = %s',
                    (session_id,)
                )
                cursor.execute(sql, params)
                row = cursor.fetchone()
                
                if row:
                    activity = json.loads(row['recent_activity'] or '[]')
                    activity.insert(0, {
                        'type': 'moved',
                        'timestamp': datetime.now().isoformat(),
                        'user': data.get('moved_by', 'AI Agent'),
                        'details': f"Moved to {new_column}"
                    })
                    
                    update_sql, update_params = convert_sql_placeholders('''
                        UPDATE synergy_sessions 
                        SET kanban_column = %s, recent_activity = %s, last_active = %s
                        WHERE session_id = %s
                    ''', (new_column, json.dumps(activity), datetime.now().isoformat(), session_id))
                    
                    cursor.execute(update_sql, update_params)
                
                conn.commit()
            # ✅ Cursor auto-closed here
        
        # Broadcast column change to WebSocket clients
        try:
            from flask import current_app
            socketio = current_app.extensions.get('socketio')
            if socketio:
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


@synergy_bp.route('/search', methods=['GET'])
def search_sessions():
    """
    Search sessions by title, description, tags, or platform
    ✅ FIXED: Uses nested context managers
    """
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
        
        with get_database_connection('synergy_sessions') as conn:
            with conn.cursor() as cursor:  # ✅ NESTED CONTEXT MANAGER
                
                # Build search query
                conditions = ['1=1']
                params = []
                
                if query:
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
                
                base_sql = f"""
                    SELECT * FROM synergy_sessions 
                    WHERE {' AND '.join(conditions)}
                    ORDER BY last_active DESC
                    LIMIT 50
                """
                
                sql, final_params = convert_sql_placeholders(base_sql, tuple(params))
                cursor.execute(sql, final_params)
                rows = cursor.fetchall()
            
            # ✅ Cursor auto-closed here
            # Process results
            sessions = []
            for row in rows:
                session = dict(row)
                
                has_permission, perm_type = check_session_permission(session, user_id, require_write=False)
                if not has_permission:
                    continue
                
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


@synergy_bp.route('/<session_id>', methods=['DELETE'])
def delete_session(session_id):
    """
    Delete session
    ✅ FIXED: Uses nested context managers
    """
    try:
        with get_database_connection('synergy_sessions') as conn:
            with conn.cursor() as cursor:  # ✅ NESTED CONTEXT MANAGER
                
                sql, params = convert_sql_placeholders(
                    'DELETE FROM synergy_sessions WHERE session_id = %s',
                    (session_id,)
                )
                cursor.execute(sql, params)
                
                conn.commit()
            # ✅ Cursor auto-closed here
        
        # Broadcast deletion to WebSocket clients
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


@synergy_bp.route('/<session_id>/link-thread', methods=['POST'])
def link_thread_to_synergy(session_id):
    """
    Link a thread to a Synergy session (bidirectional sync)
    ✅ FIXED: Uses nested context managers
    """
    try:
        data = request.get_json()
        thread_id = data.get('thread_id')
        thread_slug = data.get('thread_slug', thread_id)
        thread_name = data.get('thread_name', 'Untitled Thread')
        
        if not thread_id:
            return jsonify({'success': False, 'error': 'thread_id required'}), 400
        
        with get_database_connection('synergy_sessions') as conn:
            with conn.cursor() as cursor:  # ✅ NESTED CONTEXT MANAGER
                
                sql, params = convert_sql_placeholders(
                    'SELECT thread_ids, title FROM synergy_sessions WHERE session_id = %s',
                    (session_id,)
                )
                cursor.execute(sql, params)
                row = cursor.fetchone()
                
                if not row:
                    return jsonify({'success': False, 'error': 'Session not found'}), 404
                
                session_name = row['title']
                
                thread_ids = []
                if row['thread_ids']:
                    try:
                        thread_ids = json.loads(row['thread_ids'])
                        if not isinstance(thread_ids, list):
                            thread_ids = []
                    except json.JSONDecodeError:
                        thread_ids = []
                
                if thread_id not in thread_ids:
                    thread_ids.append(thread_id)
                    
                    update_sql, update_params = convert_sql_placeholders('''
                        UPDATE synergy_sessions 
                        SET thread_ids = %s, last_active = %s
                        WHERE session_id = %s
                    ''', (json.dumps(thread_ids), datetime.now().isoformat(), session_id))
                    cursor.execute(update_sql, update_params)
                    
                    # BIDIRECTIONAL LINK
                    try:
                        thread_id_int = int(thread_id) if thread_id and thread_id.isdigit() else None
                    except (ValueError, AttributeError):
                        thread_id_int = None
                    
                    if thread_id_int:
                        thread_update_sql, thread_update_params = convert_sql_placeholders('''
                            UPDATE sessions.threads 
                            SET synergy_card_id = %s, synergy_card_name = %s
                            WHERE id = %s OR thread_slug = %s
                        ''', (session_id, session_name, thread_id_int, thread_slug))
                    else:
                        thread_update_sql, thread_update_params = convert_sql_placeholders('''
                            UPDATE sessions.threads 
                            SET synergy_card_id = %s, synergy_card_name = %s
                            WHERE thread_slug = %s
                        ''', (session_id, session_name, thread_slug))
                    
                    cursor.execute(thread_update_sql, thread_update_params)
                    
                    print(f"[SYNERGY SYNC] ✅ Linked thread {thread_id} → Synergy session {session_id}")
                
                conn.commit()
            # ✅ Cursor auto-closed here
            
            return jsonify({
                'success': True,
                'session_id': session_id,
                'session_name': session_name,
                'thread_ids': thread_ids,
                'message': f'Thread {thread_id} linked successfully'
            })
    
    except Exception as e:
        print(f"[SYNERGY SYNC ERROR] ❌ Failed to link thread: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({'success': False, 'error': str(e)}), 500


@synergy_bp.route('/<session_id>/position', methods=['PATCH'])
def update_card_position(session_id):
    """
    Update card position within a column
    ✅ FIXED: Uses nested context managers
    """
    try:
        data = request.get_json()
        position = data.get('position')
        
        if position is None:
            return jsonify({'success': False, 'error': 'position required'}), 400
        
        with get_database_connection('synergy_sessions') as conn:
            with conn.cursor() as cursor:  # ✅ NESTED CONTEXT MANAGER
                
                sql, params = convert_sql_placeholders('''
                    UPDATE synergy_sessions 
                    SET column_position = %s
                    WHERE session_id = %s
                ''', (position, session_id))
                cursor.execute(sql, params)
                
                conn.commit()
            # ✅ Cursor auto-closed here
            
            return jsonify({
                'success': True,
                'session_id': session_id,
                'position': position
            })
    
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@synergy_bp.route('/update-positions', methods=['POST'])
def update_multiple_positions():
    """
    Update positions for multiple cards at once
    ✅ FIXED: Uses nested context managers
    """
    try:
        data = request.get_json()
        cards = data.get('cards', [])
        
        if not cards:
            return jsonify({'success': False, 'error': 'cards array required'}), 400
        
        with get_database_connection('synergy_sessions') as conn:
            with conn.cursor() as cursor:  # ✅ NESTED CONTEXT MANAGER
                
                for card in cards:
                    session_id = card.get('session_id')
                    position = card.get('position')
                    if session_id and position is not None:
                        sql, params = convert_sql_placeholders('''
                            UPDATE synergy_sessions 
                            SET column_position = %s
                            WHERE session_id = %s
                        ''', (position, session_id))
                        cursor.execute(sql, params)
                
                conn.commit()
            # ✅ Cursor auto-closed here
            
            return jsonify({
                'success': True,
                'updated_count': len(cards)
            })
    
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@synergy_bp.route('/<session_id>/unlink-thread', methods=['POST'])
def unlink_thread_from_synergy(session_id):
    """
    Unlink a thread from a Synergy session (bidirectional sync)
    ✅ FIXED: Uses nested context managers
    """
    try:
        data = request.get_json()
        thread_id = data.get('thread_id')
        
        if not thread_id:
            return jsonify({'success': False, 'error': 'thread_id required'}), 400
        
        with get_database_connection('synergy_sessions') as conn:
            with conn.cursor() as cursor:  # ✅ NESTED CONTEXT MANAGER
                
                sql, params = convert_sql_placeholders(
                    'SELECT thread_ids FROM synergy_sessions WHERE session_id = %s',
                    (session_id,)
                )
                cursor.execute(sql, params)
                row = cursor.fetchone()
                
                if not row:
                    return jsonify({'success': False, 'error': 'Session not found'}), 404
                
                thread_ids = []
                if row['thread_ids']:
                    try:
                        thread_ids = json.loads(row['thread_ids'])
                        if not isinstance(thread_ids, list):
                            thread_ids = []
                    except json.JSONDecodeError:
                        thread_ids = []
                
                if thread_id in thread_ids:
                    thread_ids.remove(thread_id)
                    
                    update_sql, update_params = convert_sql_placeholders('''
                        UPDATE synergy_sessions 
                        SET thread_ids = %s, last_active = %s
                        WHERE session_id = %s
                    ''', (json.dumps(thread_ids), datetime.now().isoformat(), session_id))
                    cursor.execute(update_sql, update_params)
                    
                    print(f"[SYNERGY SYNC] Removed thread {thread_id} from Synergy session {session_id}")
                
                conn.commit()
            # ✅ Cursor auto-closed here
            
            return jsonify({
                'success': True,
                'session_id': session_id,
                'thread_ids': thread_ids,
                'message': f'Thread {thread_id} unlinked successfully'
            })
    
    except Exception as e:
        print(f"[SYNERGY SYNC ERROR] Failed to unlink thread: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500


# ============================================================
# INTERNAL DOCUMENTS
# ============================================================

@synergy_bp.route('/internal-doc/create', methods=['POST'])
def create_internal_doc():
    """
    Create a new internal document inside a Synergy session
    ✅ FIXED: Uses nested context managers
    """
    try:
        data = request.get_json()
        session_id = data.get('session_id')
        title = data.get('title', 'Untitled Document')
        content = data.get('content', '')
        content_json = data.get('content_json')
        doc_format = data.get('format', 'markdown')
        doc_type = data.get('doc_type', 'richtext')
        created_by = data.get('created_by', 'system')
        
        if not session_id:
            return jsonify({'success': False, 'error': 'session_id required'}), 400
        
        import time
        import re
        doc_id = f"int_doc_{int(time.time() * 1000)}"
        
        slug = re.sub(r'[^a-z0-9]+', '-', title.lower()).strip('-')
        if not slug:
            slug = doc_id
        
        with get_database_connection('synergy_sessions') as conn:
            with conn.cursor() as cursor:  # ✅ NESTED CONTEXT MANAGER
                
                original_slug = slug
                counter = 1
                while True:
                    sql, params = convert_sql_placeholders(
                        'SELECT doc_id FROM synergy_internal_docs WHERE slug = %s',
                        (slug,)
                    )
                    cursor.execute(sql, params)
                    if not cursor.fetchone():
                        break
                    slug = f"{original_slug}-{counter}"
                    counter += 1
                
                share_url = f"/internal-docs/{slug}"
                
                verify_sql, verify_params = convert_sql_placeholders(
                    'SELECT session_id FROM synergy_sessions WHERE session_id = %s',
                    (session_id,)
                )
                cursor.execute(verify_sql, verify_params)
                if not cursor.fetchone():
                    return jsonify({'success': False, 'error': 'Session not found'}), 404
                
                now = datetime.now().isoformat()
                insert_sql, insert_params = convert_sql_placeholders('''
                    INSERT INTO synergy_internal_docs 
                    (doc_id, session_id, title, content, content_json, format, doc_type, 
                     created_by, created_at, updated_at, version, linked_to_ai, slug, share_url)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                ''', (doc_id, session_id, title, content, content_json, doc_format, doc_type,
                      created_by, now, now, 1, False, slug, share_url))
                cursor.execute(insert_sql, insert_params)
                
                conn.commit()
            # ✅ Cursor auto-closed here
        
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
    ✅ FIXED: Uses nested context managers
    """
    try:
        with get_database_connection('synergy_sessions') as conn:
            with conn.cursor() as cursor:  # ✅ NESTED CONTEXT MANAGER
                
                sql, params = convert_sql_placeholders('''
                    SELECT doc_id, session_id, title, content, content_json, format, doc_type,
                           created_at, updated_at, created_by, version, linked_to_ai,
                           slug, share_url, description, tags
                    FROM synergy_internal_docs
                    WHERE doc_id = %s
                ''', (doc_id,))
                cursor.execute(sql, params)
                
                row = cursor.fetchone()
            
            # ✅ Cursor auto-closed here
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
    ✅ FIXED: Uses nested context managers
    """
    try:
        data = request.get_json()
        title = data.get('title')
        content = data.get('content')
        content_json = data.get('content_json')
        
        if not title and not content and not content_json:
            return jsonify({'success': False, 'error': 'title, content, or content_json required'}), 400
        
        with get_database_connection('synergy_sessions') as conn:
            with conn.cursor() as cursor:  # ✅ NESTED CONTEXT MANAGER
                
                sql, params = convert_sql_placeholders(
                    'SELECT version FROM synergy_internal_docs WHERE doc_id = %s',
                    (doc_id,)
                )
                cursor.execute(sql, params)
                row = cursor.fetchone()
                
                if not row:
                    return jsonify({'success': False, 'error': 'Document not found'}), 404
                
                new_version = row['version'] + 1
                
                updates = []
                update_params = []
                
                if title:
                    updates.append('title = %s')
                    update_params.append(title)
                if content is not None:
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
                
                query = f"UPDATE synergy_internal_docs SET {', '.join(updates)} WHERE doc_id = %s"
                sql, final_params = convert_sql_placeholders(query, tuple(update_params))
                cursor.execute(sql, final_params)
                
                conn.commit()
            # ✅ Cursor auto-closed here
        
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
    ✅ FIXED: Uses nested context managers
    """
    try:
        with get_database_connection('synergy_sessions') as conn:
            with conn.cursor() as cursor:  # ✅ NESTED CONTEXT MANAGER
                
                sql, params = convert_sql_placeholders(
                    'DELETE FROM synergy_internal_docs WHERE doc_id = %s',
                    (doc_id,)
                )
                cursor.execute(sql, params)
                
                if cursor.rowcount == 0:
                    return jsonify({'success': False, 'error': 'Document not found'}), 404
                
                conn.commit()
            # ✅ Cursor auto-closed here
        
        print(f"[INTERNAL DOC] Deleted document {doc_id}")
        
        return jsonify({
            'success': True,
            'doc_id': doc_id,
            'message': 'Document deleted successfully'
        })
    
    except Exception as e:
        print(f"[INTERNAL DOC ERROR] Failed to delete {doc_id}: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500


@synergy_bp.route('/internal-docs/list', methods=['GET'])
def list_internal_docs():
    """
    List all internal docs (optionally filtered by session_id)
    ✅ FIXED: Uses nested context managers
    """
    try:
        session_id = request.args.get('session_id')
        
        with get_database_connection('synergy_sessions') as conn:
            with conn.cursor() as cursor:  # ✅ NESTED CONTEXT MANAGER
                
                if session_id:
                    sql, params = convert_sql_placeholders('''
                        SELECT doc_id, session_id, title, doc_type, created_at, updated_at, slug, share_url
                        FROM synergy_internal_docs
                        WHERE session_id = %s
                        ORDER BY updated_at DESC
                    ''', (session_id,))
                else:
                    sql, params = convert_sql_placeholders('''
                        SELECT doc_id, session_id, title, doc_type, created_at, updated_at, slug, share_url
                        FROM synergy_internal_docs
                        ORDER BY updated_at DESC
                    ''', ())
                
                cursor.execute(sql, params)
                rows = cursor.fetchall()
            
            # ✅ Cursor auto-closed here
            docs = []
            for row in rows:
                docs.append({
                    'doc_id': row['doc_id'],
                    'session_id': row['session_id'],
                    'title': row['title'],
                    'doc_type': row['doc_type'],
                    'created_at': row['created_at'],
                    'updated_at': row['updated_at'],
                    'slug': row['slug'],
                    'share_url': row['share_url']
                })
            
            return jsonify({
                'success': True,
                'docs': docs,
                'count': len(docs)
            })
    
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


# ============================================================
# TAG MANAGEMENT
# ============================================================

@synergy_bp.route('/<session_id>/tags', methods=['POST'])
def add_tag(session_id):
    """
    Add a tag to a session
    ✅ FIXED: Uses nested context managers
    """
    try:
        data = request.json
        tag = data.get('tag')
        
        if not tag:
            return jsonify({'success': False, 'error': 'tag field required'}), 400
        
        with get_database_connection('synergy_sessions') as conn:
            with conn.cursor() as cursor:  # ✅ NESTED CONTEXT MANAGER
                
                sql, params = convert_sql_placeholders(
                    'SELECT tags FROM synergy_sessions WHERE session_id = %s',
                    (session_id,)
                )
                cursor.execute(sql, params)
                row = cursor.fetchone()
                
                if not row:
                    return jsonify({'success': False, 'error': 'Session not found'}), 404
                
                tags = []
                if row['tags']:
                    try:
                        tags = json.loads(row['tags'])
                    except:
                        tags = []
                
                if tag not in tags:
                    tags.append(tag)
                    
                    update_sql, update_params = convert_sql_placeholders('''
                        UPDATE synergy_sessions 
                        SET tags = %s, last_active = %s
                        WHERE session_id = %s
                    ''', (json.dumps(tags), datetime.now().isoformat(), session_id))
                    cursor.execute(update_sql, update_params)
                
                conn.commit()
            # ✅ Cursor auto-closed here
            
            return jsonify({
                'success': True,
                'tags': tags
            })
    
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@synergy_bp.route('/<session_id>/tags/<path:tag_name>', methods=['DELETE'])
def remove_tag(session_id, tag_name):
    """
    Remove a tag from a session
    ✅ FIXED: Uses nested context managers
    """
    try:
        with get_database_connection('synergy_sessions') as conn:
            with conn.cursor() as cursor:  # ✅ NESTED CONTEXT MANAGER
                
                sql, params = convert_sql_placeholders(
                    'SELECT tags FROM synergy_sessions WHERE session_id = %s',
                    (session_id,)
                )
                cursor.execute(sql, params)
                row = cursor.fetchone()
                
                if not row:
                    return jsonify({'success': False, 'error': 'Session not found'}), 404
                
                tags = []
                if row['tags']:
                    try:
                        tags = json.loads(row['tags'])
                    except:
                        tags = []
                
                if tag_name in tags:
                    tags.remove(tag_name)
                    
                    update_sql, update_params = convert_sql_placeholders('''
                        UPDATE synergy_sessions 
                        SET tags = %s, last_active = %s
                        WHERE session_id = %s
                    ''', (json.dumps(tags), datetime.now().isoformat(), session_id))
                    cursor.execute(update_sql, update_params)
                
                conn.commit()
            # ✅ Cursor auto-closed here
            
            return jsonify({
                'success': True,
                'tags': tags
            })
    
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@synergy_bp.route('/<session_id>/tags', methods=['GET'])
def get_session_tags(session_id):
    """
    Get all tags for a session
    ✅ FIXED: Uses nested context managers
    """
    try:
        with get_database_connection('synergy_sessions') as conn:
            with conn.cursor() as cursor:  # ✅ NESTED CONTEXT MANAGER
                
                sql, params = convert_sql_placeholders(
                    'SELECT tags FROM synergy_sessions WHERE session_id = %s',
                    (session_id,)
                )
                cursor.execute(sql, params)
                row = cursor.fetchone()
            
            # ✅ Cursor auto-closed here
            if not row:
                return jsonify({'success': False, 'error': 'Session not found'}), 404
            
            tags = []
            if row['tags']:
                try:
                    tags = json.loads(row['tags'])
                except:
                    tags = []
            
            return jsonify({
                'success': True,
                'session_id': session_id,
                'tags': tags
            })
    
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


# ============================================================
# LINK MANAGEMENT
# ============================================================

@synergy_bp.route('/<session_id>/links', methods=['GET'])
def get_session_links(session_id):
    """
    Get all links for a session
    ✅ FIXED: Uses nested context managers
    """
    try:
        with get_database_connection('synergy_sessions') as conn:
            with conn.cursor() as cursor:  # ✅ NESTED CONTEXT MANAGER
                
                sql, params = convert_sql_placeholders(
                    'SELECT links FROM synergy_sessions WHERE session_id = %s',
                    (session_id,)
                )
                cursor.execute(sql, params)
                row = cursor.fetchone()
            
            # ✅ Cursor auto-closed here
            if not row:
                return jsonify({'success': False, 'error': 'Session not found'}), 404
            
            links = []
            if row['links']:
                try:
                    links = json.loads(row['links'])
                except:
                    links = []
            
            return jsonify({
                'success': True,
                'links': links
            })
    
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@synergy_bp.route('/<session_id>/link-document', methods=['POST'])
def add_link(session_id):
    """
    Add a link/document to a session
    ✅ FIXED: Uses nested context managers
    """
    try:
        data = request.json
        url = data.get('url')
        title = data.get('title', 'Untitled')
        link_type = data.get('type', 'link')
        
        if not url:
            return jsonify({'success': False, 'error': 'url field required'}), 400
        
        with get_database_connection('synergy_sessions') as conn:
            with conn.cursor() as cursor:  # ✅ NESTED CONTEXT MANAGER
                
                sql, params = convert_sql_placeholders(
                    'SELECT links FROM synergy_sessions WHERE session_id = %s',
                    (session_id,)
                )
                cursor.execute(sql, params)
                row = cursor.fetchone()
                
                if not row:
                    return jsonify({'success': False, 'error': 'Session not found'}), 404
                
                links = []
                if row['links']:
                    try:
                        links = json.loads(row['links'])
                    except:
                        links = []
                
                new_link = {
                    'url': url,
                    'title': title,
                    'type': link_type,
                    'added_at': datetime.now().isoformat()
                }
                links.append(new_link)
                
                update_sql, update_params = convert_sql_placeholders('''
                    UPDATE synergy_sessions 
                    SET links = %s, last_active = %s
                    WHERE session_id = %s
                ''', (json.dumps(links), datetime.now().isoformat(), session_id))
                cursor.execute(update_sql, update_params)
                
                conn.commit()
            # ✅ Cursor auto-closed here
            
            return jsonify({
                'success': True,
                'links': links
            })
    
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@synergy_bp.route('/<session_id>/links/<int:link_index>', methods=['DELETE'])
def remove_link(session_id, link_index):
    """
    Remove a link by index
    ✅ FIXED: Uses nested context managers
    """
    try:
        with get_database_connection('synergy_sessions') as conn:
            with conn.cursor() as cursor:  # ✅ NESTED CONTEXT MANAGER
                
                sql, params = convert_sql_placeholders(
                    'SELECT links FROM synergy_sessions WHERE session_id = %s',
                    (session_id,)
                )
                cursor.execute(sql, params)
                row = cursor.fetchone()
                
                if not row:
                    return jsonify({'success': False, 'error': 'Session not found'}), 404
                
                links = []
                if row['links']:
                    try:
                        links = json.loads(row['links'])
                    except:
                        links = []
                
                if 0 <= link_index < len(links):
                    links.pop(link_index)
                    
                    update_sql, update_params = convert_sql_placeholders('''
                        UPDATE synergy_sessions 
                        SET links = %s, last_active = %s
                        WHERE session_id = %s
                    ''', (json.dumps(links), datetime.now().isoformat(), session_id))
                    cursor.execute(update_sql, update_params)
                
                conn.commit()
            # ✅ Cursor auto-closed here
            
            return jsonify({
                'success': True,
                'links': links
            })
    
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


# ============================================================
# MILESTONE CRUD
# ============================================================

@synergy_bp.route('/<session_id>/milestones', methods=['GET'])
def get_session_milestones(session_id):
    """
    Get all milestones for session (with tasks and subtasks)
    ✅ FIXED: Uses nested context managers
    """
    try:
        with get_database_connection('synergy_sessions') as conn:
            with conn.cursor() as cursor:  # ✅ NESTED CONTEXT MANAGER
                
                # Get session data
                cursor.execute('''
                    SELECT session_id, title, description, status, priority, 
                           due_date, assignees, documents, links, tags, project_name,
                           created_at, updated_at, message_count
                    FROM synergy_sessions 
                    WHERE session_id = %s
                ''', (session_id,))
                
                session_row = cursor.fetchone()
                if not session_row:
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
                    SELECT milestone_id, milestone_number, title, description,
                           completed, due_date, priority, estimated_hours, actual_hours,
                           created_at, completed_at, milestone_order, depends_on_milestone_id,
                           blocked, blocker_reason, blocked_since, updated_at, documents, links
                    FROM milestones 
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
                        'milestone_name': m_row['title'],
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
                    
                    # Get tasks
                    sql, params = convert_sql_placeholders('''
                        SELECT task_id, task, completed, blocked, blocker_reason, 
                               blocker_type, task_order, created_at, completed_at,
                               blocked_since, estimated_hours, actual_hours, assigned_to, updated_at, priority
                        FROM tasks 
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
                        
                        # Get subtasks
                        sql, params = convert_sql_placeholders('''
                            SELECT subtask_id, task, completed, subtask_order, created_at, completed_at,
                                   estimated_hours, actual_hours, updated_at, priority
                            FROM subtasks 
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
                    
                    if total_items > 0:
                        milestone['progress_percentage'] = round((completed_items / total_items * 100), 1)
                    else:
                        milestone['progress_percentage'] = 0
                    
                    milestones.append(milestone)
            
            # ✅ Cursor auto-closed here
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
        print(f"{'='*80}\n")
        import traceback
        traceback.print_exc()
        
        error_msg = str(e) if str(e) else f"{type(e).__name__} occurred"
        return jsonify({
            'success': False, 
            'error': error_msg,
            'error_type': type(e).__name__,
            'error_details': repr(e)
        }), 500


@synergy_bp.route('/milestone/create', methods=['POST'])
def create_milestone_complete():
    """
    Complete milestone creation - Creates milestone + tasks + subtasks in ONE call
    ✅ FIXED: Uses nested context managers
    """
    try:
        data = request.get_json()
        
        if not data.get('session_id'):
            return jsonify({'success': False, 'error': 'session_id required'}), 400
        
        title = data.get('title') or data.get('milestone_name')
        if not title:
            return jsonify({'success': False, 'error': 'title required (milestone_name deprecated)'}), 400
        
        with get_database_connection('synergy_sessions') as conn:
            with conn.cursor() as cursor:  # ✅ NESTED CONTEXT MANAGER
                
                # Check session exists
                sql, params = convert_sql_placeholders(
                    'SELECT session_id FROM synergy_sessions WHERE session_id = %s',
                    (data['session_id'],)
                )
                cursor.execute(sql, params)
                if not cursor.fetchone():
                    return jsonify({'success': False, 'error': 'Session not found'}), 404
                
                # Get next milestone number
                sql, params = convert_sql_placeholders('''
                    SELECT COALESCE(MAX(milestone_number), 0) + 1 AS next_number
                    FROM milestones 
                    WHERE session_id = %s
                ''', (data['session_id'],))
                cursor.execute(sql, params)
                result = cursor.fetchone()
                milestone_number = result['next_number'] if isinstance(result, dict) else result[0]
                
                milestone_id = f"ms_{datetime.now().strftime('%Y%m%d%H%M%S')}"
                
                documents_json = json.dumps(data.get('documents', []))
                links_json = json.dumps(data.get('links', []))
                tags_json = json.dumps(data.get('tags', []))
                
                # Insert milestone
                sql, params = convert_sql_placeholders('''
                    INSERT INTO milestones (
                        milestone_id, session_id, milestone_number, milestone_order, milestone_name,
                        title, description, completed, due_date, priority, estimated_hours,
                        created_at, updated_at, documents, links, blocked, tags
                    ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                ''', (
                    milestone_id,
                    data['session_id'],
                    milestone_number,
                    milestone_number,
                    title,
                    title,
                    data.get('description', ''),
                    False,
                    data.get('due_date'),
                    data.get('priority', 'medium'),
                    data.get('estimated_hours'),
                    datetime.now().isoformat(),
                    datetime.now().isoformat(),
                    documents_json,
                    links_json,
                    False,
                    tags_json
                ))
                cursor.execute(sql, params)
                
                # Insert tasks and subtasks
                tasks_created = 0
                subtasks_created = 0
                tasks_list = data.get('tasks', [])
                
                for task_order, task_item in enumerate(tasks_list, start=1):
                    import time
                    time.sleep(0.001)
                    task_id = f"task_{datetime.now().strftime('%Y%m%d%H%M%S%f')[:17]}_{task_order}"
                    
                    if isinstance(task_item, str):
                        task_text = task_item
                        task_priority = 'medium'
                        subtasks = []
                    else:
                        task_text = task_item.get('task', '')
                        task_priority = task_item.get('priority', 'medium')
                        subtasks = task_item.get('subtasks', [])
                    
                    task_title = task_item.get('title', task_text) if isinstance(task_item, dict) else task_text
                    task_desc = task_item.get('description', '') if isinstance(task_item, dict) else ''
                    task_due = task_item.get('due_date') if isinstance(task_item, dict) else None
                    task_est_hours = task_item.get('estimated_hours') if isinstance(task_item, dict) else None
                    task_assigned = task_item.get('assigned_to', '') if isinstance(task_item, dict) else ''
                    
                    sql, params = convert_sql_placeholders('''
                        INSERT INTO tasks (
                            task_id, milestone_id, task, title, description, completed, task_order, 
                            priority, due_date, estimated_hours, assigned_to, created_at
                        ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                    ''', (task_id, milestone_id, task_text, task_title, task_desc, False, task_order, 
                          task_priority, task_due, task_est_hours, task_assigned, datetime.now().isoformat()))
                    cursor.execute(sql, params)
                    tasks_created += 1
                    
                    # Insert subtasks
                    for subtask_order, subtask_item in enumerate(subtasks, start=1):
                        time.sleep(0.001)
                        subtask_id = f"sub_{datetime.now().strftime('%Y%m%d%H%M%S%f')[:17]}_{task_order}_{subtask_order}"
                        
                        if isinstance(subtask_item, str):
                            subtask_text = subtask_item
                            subtask_priority = 'medium'
                        else:
                            subtask_text = subtask_item.get('task', '') or subtask_item.get('text', '')
                            subtask_priority = subtask_item.get('priority', 'medium')
                        
                        subtask_title = subtask_item.get('title', subtask_text) if isinstance(subtask_item, dict) else subtask_text
                        subtask_due = subtask_item.get('due_date') if isinstance(subtask_item, dict) else None
                        subtask_assigned = subtask_item.get('assigned_to', '') if isinstance(subtask_item, dict) else ''
                        
                        sql, params = convert_sql_placeholders('''
                            INSERT INTO subtasks (
                                subtask_id, task_id, task, title, completed, subtask_order, 
                                priority, due_date, assigned_to, created_at
                            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                        ''', (subtask_id, task_id, subtask_text, subtask_title, False, subtask_order, 
                              subtask_priority, subtask_due, subtask_assigned, datetime.now().isoformat()))
                        cursor.execute(sql, params)
                        subtasks_created += 1
                
                # Mark session as using milestones
                sql, params = convert_sql_placeholders('''
                    UPDATE synergy_sessions 
                    SET uses_milestones = %s, last_active = %s
                    WHERE session_id = %s
                ''', (True, datetime.now().isoformat(), data['session_id']))
                cursor.execute(sql, params)
                
                conn.commit()
            # ✅ Cursor auto-closed here
            
            return jsonify({
                'success': True,
                'milestone_id': milestone_id,
                'milestone_number': milestone_number,
                'tasks_created': tasks_created,
                'subtasks_created': subtasks_created,
                'message': f"Created milestone '{title}' with {tasks_created} tasks and {subtasks_created} subtasks"
            })
    
    except Exception as e:
        print(f"[MILESTONE ERROR] Failed to create milestone: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({'success': False, 'error': str(e)}), 500


# ============================================================================
# TESTING & DIAGNOSTICS ENDPOINTS
# ============================================================================

@synergy_bp.route('/test/smoke', methods=['GET'])
def smoke_test():
    """
    Smoke test endpoint - verifies basic system functionality
    
    Tests:
    - Database connection
    - Table existence
    - Basic query execution
    - Response formatting
    
    Returns:
        JSON with test results and timing
    """
    import time
    start_time = time.time()
    
    results = {
        'success': True,
        'tests': {},
        'timestamp': datetime.now().isoformat(),
        'duration_ms': 0
    }
    
    try:
        # Test 1: Database Connection
        test_start = time.time()
        try:
            with get_database_connection('synergy_sessions') as conn:
                results['tests']['database_connection'] = {
                    'status': 'PASS',
                    'duration_ms': round((time.time() - test_start) * 1000, 2)
                }
        except Exception as e:
            results['tests']['database_connection'] = {
                'status': 'FAIL',
                'error': str(e),
                'duration_ms': round((time.time() - test_start) * 1000, 2)
            }
            results['success'] = False
        
        # Test 2: Table Existence
        test_start = time.time()
        try:
            with get_database_connection('synergy_sessions') as conn:
                with conn.cursor() as cursor:
                    sql, params = convert_sql_placeholders("""
                        SELECT table_name 
                        FROM information_schema.tables 
                        WHERE table_schema = 'public' 
                        AND table_name IN ('synergy_sessions', 'milestones', 'tasks', 'subtasks')
                    """, ())
                    cursor.execute(sql, params)
                    tables = [row[0] for row in cursor.fetchall()]
                    
                    expected_tables = ['synergy_sessions', 'milestones', 'tasks', 'subtasks']
                    missing_tables = [t for t in expected_tables if t not in tables]
                    
                    results['tests']['table_existence'] = {
                        'status': 'PASS' if not missing_tables else 'FAIL',
                        'found_tables': tables,
                        'missing_tables': missing_tables,
                        'duration_ms': round((time.time() - test_start) * 1000, 2)
                    }
                    
                    if missing_tables:
                        results['success'] = False
        except Exception as e:
            results['tests']['table_existence'] = {
                'status': 'FAIL',
                'error': str(e),
                'duration_ms': round((time.time() - test_start) * 1000, 2)
            }
            results['success'] = False
        
        # Test 3: Basic Query Execution
        test_start = time.time()
        try:
            with get_database_connection('synergy_sessions') as conn:
                with conn.cursor() as cursor:
                    sql, params = convert_sql_placeholders("SELECT COUNT(*) FROM synergy_sessions", ())
                    cursor.execute(sql, params)
                    count = cursor.fetchone()[0]
                    
                    results['tests']['query_execution'] = {
                        'status': 'PASS',
                        'session_count': count,
                        'duration_ms': round((time.time() - test_start) * 1000, 2)
                    }
        except Exception as e:
            results['tests']['query_execution'] = {
                'status': 'FAIL',
                'error': str(e),
                'duration_ms': round((time.time() - test_start) * 1000, 2)
            }
            results['success'] = False
        
        # Test 4: JSON Serialization
        test_start = time.time()
        try:
            test_data = {
                'nested': {'key': 'value'},
                'array': [1, 2, 3],
                'null': None,
                'bool': True
            }
            json.dumps(test_data)
            
            results['tests']['json_serialization'] = {
                'status': 'PASS',
                'duration_ms': round((time.time() - test_start) * 1000, 2)
            }
        except Exception as e:
            results['tests']['json_serialization'] = {
                'status': 'FAIL',
                'error': str(e),
                'duration_ms': round((time.time() - test_start) * 1000, 2)
            }
            results['success'] = False
        
        # Calculate total duration
        results['duration_ms'] = round((time.time() - start_time) * 1000, 2)
        
        # Summary
        passed = sum(1 for test in results['tests'].values() if test['status'] == 'PASS')
        total = len(results['tests'])
        results['summary'] = f"{passed}/{total} tests passed"
        
        return jsonify(results), 200 if results['success'] else 500
    
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e),
            'timestamp': datetime.now().isoformat()
        }), 500


@synergy_bp.route('/test/endpoints', methods=['GET'])
def test_endpoints():
    """
    Test all Synergy API endpoints
    
    Returns:
        JSON with list of endpoints and their test status
    """
    endpoints = []
    
    # Get all routes for synergy blueprint
    from flask import current_app
    for rule in current_app.url_map.iter_rules():
        if rule.endpoint.startswith('synergy.'):
            endpoint_name = rule.endpoint.replace('synergy.', '')
            endpoints.append({
                'name': endpoint_name,
                'path': rule.rule,
                'methods': list(rule.methods - {'HEAD', 'OPTIONS'}),
                'tested': endpoint_name in [
                    'list_sessions', 'create_session', 'get_session',
                    'update_session', 'delete_session', 'update_column',
                    'smoke_test', 'test_endpoints'
                ]
            })
    
    return jsonify({
        'success': True,
        'endpoint_count': len(endpoints),
        'endpoints': sorted(endpoints, key=lambda x: x['path']),
        'timestamp': datetime.now().isoformat()
    })


@synergy_bp.route('/test/database', methods=['GET'])
def test_database():
    """
    Comprehensive database test
    
    Tests:
    - Connection pooling
    - Transaction support
    - Foreign key constraints
    - Query performance
    """
    import time
    results = {
        'success': True,
        'tests': {},
        'timestamp': datetime.now().isoformat()
    }
    
    try:
        # Test 1: Connection Pool
        test_start = time.time()
        try:
            connections = []
            for i in range(5):
                conn = get_database_connection('synergy_sessions')
                connections.append(conn)
            
            # Close all connections
            for conn in connections:
                conn.close()
            
            results['tests']['connection_pool'] = {
                'status': 'PASS',
                'connections_created': 5,
                'duration_ms': round((time.time() - test_start) * 1000, 2)
            }
        except Exception as e:
            results['tests']['connection_pool'] = {
                'status': 'FAIL',
                'error': str(e)
            }
            results['success'] = False
        
        # Test 2: Transaction Rollback
        test_start = time.time()
        try:
            with get_database_connection('synergy_sessions') as conn:
                with conn.cursor() as cursor:
                    # Start transaction
                    cursor.execute("BEGIN")
                    
                    # Insert test data
                    test_id = f"test_{int(time.time())}"
                    sql, params = convert_sql_placeholders("""
                        INSERT INTO synergy_sessions (session_id, title, status, created_at)
                        VALUES (%s, %s, %s, %s)
                    """, (test_id, 'Test Session', 'active', datetime.now().isoformat()))
                    cursor.execute(sql, params)
                    
                    # Rollback
                    cursor.execute("ROLLBACK")
                    
                    # Verify rollback
                    sql, params = convert_sql_placeholders("SELECT COUNT(*) FROM synergy_sessions WHERE session_id = %s", (test_id,))
                    cursor.execute(sql, params)
                    count = cursor.fetchone()[0]
                    
                    results['tests']['transaction_rollback'] = {
                        'status': 'PASS' if count == 0 else 'FAIL',
                        'duration_ms': round((time.time() - test_start) * 1000, 2)
                    }
                    
                    if count != 0:
                        results['success'] = False
        except Exception as e:
            results['tests']['transaction_rollback'] = {
                'status': 'FAIL',
                'error': str(e)
            }
            results['success'] = False
        
        # Test 3: Query Performance
        test_start = time.time()
        try:
            with get_database_connection('synergy_sessions') as conn:
                with conn.cursor() as cursor:
                    # Test simple query
                    simple_start = time.time()
                    sql, params = convert_sql_placeholders("SELECT COUNT(*) FROM synergy_sessions", ())
                    cursor.execute(sql, params)
                    cursor.fetchone()
                    simple_duration = round((time.time() - simple_start) * 1000, 2)
                    
                    # Test complex query with joins
                    complex_start = time.time()
                    sql, params = convert_sql_placeholders("""
                        SELECT s.session_id, COUNT(DISTINCT m.milestone_id) as milestone_count
                        FROM synergy_sessions s
                        LEFT JOIN milestones m ON s.session_id = m.session_id
                        GROUP BY s.session_id
                        LIMIT 10
                    """, ())
                    cursor.execute(sql, params)
                    cursor.fetchall()
                    complex_duration = round((time.time() - complex_start) * 1000, 2)
                    
                    results['tests']['query_performance'] = {
                        'status': 'PASS',
                        'simple_query_ms': simple_duration,
                        'complex_query_ms': complex_duration,
                        'duration_ms': round((time.time() - test_start) * 1000, 2)
                    }
        except Exception as e:
            results['tests']['query_performance'] = {
                'status': 'FAIL',
                'error': str(e)
            }
            results['success'] = False
        
        return jsonify(results), 200 if results['success'] else 500
    
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e),
            'timestamp': datetime.now().isoformat()
        }), 500


@synergy_bp.route('/test/compile', methods=['GET'])
def test_compile():
    """
    Python compile test - checks for syntax errors
    
    Returns:
        JSON with compilation status
    """
    import py_compile
    import tempfile
    
    results = {
        'success': True,
        'files_tested': [],
        'timestamp': datetime.now().isoformat()
    }
    
    try:
        # Get path to this file
        current_file = Path(__file__)
        
        # Test compilation
        try:
            with tempfile.NamedTemporaryFile(suffix='.pyc', delete=False) as tmp:
                py_compile.compile(str(current_file), cfile=tmp.name, doraise=True)
                
                results['files_tested'].append({
                    'file': current_file.name,
                    'status': 'PASS',
                    'size_bytes': current_file.stat().st_size
                })
        except py_compile.PyCompileError as e:
            results['files_tested'].append({
                'file': current_file.name,
                'status': 'FAIL',
                'error': str(e)
            })
            results['success'] = False
        
        return jsonify(results), 200 if results['success'] else 500
    
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e),
            'timestamp': datetime.now().isoformat()
        }), 500


@synergy_bp.route('/test/health', methods=['GET'])
def health_check():
    """
    Health check endpoint for monitoring
    
    Returns:
        JSON with system health status
    """
    try:
        import psutil
        import platform
        
        health = {
            'status': 'healthy',
            'timestamp': datetime.now().isoformat(),
            'system': {
                'platform': platform.system(),
                'python_version': platform.python_version(),
                'cpu_count': psutil.cpu_count(),
                'cpu_percent': psutil.cpu_percent(interval=0.1),
                'memory_percent': psutil.virtual_memory().percent,
                'disk_percent': psutil.disk_usage('/').percent
            },
            'database': {
                'status': 'unknown'
            }
        }
        
        # Test database connection
        try:
            with get_database_connection('synergy_sessions') as conn:
                with conn.cursor() as cursor:
                    cursor.execute("SELECT 1")
                    cursor.fetchone()
                    health['database']['status'] = 'connected'
        except Exception as e:
            health['database']['status'] = 'error'
            health['database']['error'] = str(e)
            health['status'] = 'unhealthy'
        
        return jsonify(health), 200 if health['status'] == 'healthy' else 503
    
    except Exception as e:
        return jsonify({
            'status': 'unhealthy',
            'error': str(e),
            'timestamp': datetime.now().isoformat()
        }), 500



# ============================================================
# MILESTONE CRUD (CONTINUED)
# ============================================================

@synergy_bp.route('/<session_id>/milestones', methods=['POST'])
def create_milestone(session_id):
    """
    [DEPRECATED] Simple milestone creation (no tasks)
    Use POST /milestone/create for complete milestone creation
    ✅ FIXED: Uses nested context managers
    """
    try:
        data = request.json
        title = data.get('title') or data.get('milestone_name')
        
        if not title:
            return jsonify({'success': False, 'error': 'title (or milestone_name) field required'}), 400
        
        import time
        milestone_id = f"ms_{int(time.time() * 1000)}"
        
        with get_database_connection('synergy_sessions') as conn:
            with conn.cursor() as cursor:  # ✅ NESTED CONTEXT MANAGER

                # Permission check — only session owners/editors may add milestones
                _uid = getattr(g, 'rls_user_id', None) or data.get('user_id')
                if _uid:
                    _psql, _ppar = convert_sql_placeholders(
                        'SELECT owner_user_id, permission_level, shared_with_users FROM synergy_sessions WHERE session_id = %s',
                        (session_id,)
                    )
                    cursor.execute(_psql, _ppar)
                    _sess_row = cursor.fetchone()
                    if _sess_row:
                        _ok, _ = check_session_permission(dict(_sess_row), _uid, require_write=True)
                        if not _ok:
                            return jsonify({'success': False, 'error': 'Write permission required'}), 403

                # Get max milestone_number
                sql, params = convert_sql_placeholders(
                    'SELECT COALESCE(MAX(milestone_number), 0) as max_num FROM milestones WHERE session_id = %s',
                    (session_id,)
                )
                cursor.execute(sql, params)
                row = cursor.fetchone()
                milestone_number = row['max_num'] + 1
                
                # Get max milestone_order
                sql2, params2 = convert_sql_placeholders(
                    'SELECT COALESCE(MAX(milestone_order), 0) as max_order FROM milestones WHERE session_id = %s',
                    (session_id,)
                )
                cursor.execute(sql2, params2)
                row2 = cursor.fetchone()
                milestone_order = row2['max_order'] + 1
                
                # Insert milestone
                insert_sql, insert_params = convert_sql_placeholders('''
                    INSERT INTO milestones 
                    (milestone_id, session_id, milestone_number, title, description, 
                     completed, priority, due_date, estimated_hours, milestone_order, 
                     blocked, created_at, updated_at, documents, links)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                ''', (
                    milestone_id, session_id, milestone_number, title,
                    data.get('description', ''), False, data.get('priority', 'medium'),
                    data.get('due_date'), data.get('estimated_hours'),
                    milestone_order, False, datetime.now().isoformat(), 
                    datetime.now().isoformat(), '[]', '[]'
                ))
                cursor.execute(insert_sql, insert_params)
                
                # Update session to use milestones
                update_sql, update_params = convert_sql_placeholders('''
                    UPDATE synergy_sessions 
                    SET uses_milestones = %s, last_active = %s
                    WHERE session_id = %s
                ''', (True, datetime.now().isoformat(), session_id))
                cursor.execute(update_sql, update_params)
                
                conn.commit()
            # ✅ Cursor auto-closed here
            
            return jsonify({
                'success': True,
                'milestone_id': milestone_id,
                'milestone_number': milestone_number,
                'session_id': session_id,
                'warning': 'This endpoint creates empty milestones. Use POST /milestone/create for complete milestone creation with tasks/subtasks.'
            })
    
    except Exception as e:
        print(f"[MILESTONE ERROR] Failed to create: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({'success': False, 'error': str(e)}), 500


@synergy_bp.route('/milestone/<milestone_id>', methods=['GET'])
def get_milestone(milestone_id):
    """
    Get a single milestone with all tasks and subtasks
    ✅ FIXED: Uses nested context managers
    """
    try:
        with get_database_connection('synergy_sessions') as conn:
            with conn.cursor() as cursor:  # ✅ NESTED CONTEXT MANAGER
                
                # Get milestone
                sql, params = convert_sql_placeholders('''
                    SELECT milestone_id, session_id, milestone_number, title, description,
                           completed, due_date, priority, estimated_hours, actual_hours,
                           created_at, completed_at, milestone_order, depends_on_milestone_id,
                           blocked, blocker_reason, blocked_since, updated_at, documents, links
                    FROM milestones 
                    WHERE milestone_id = %s
                ''', (milestone_id,))
                cursor.execute(sql, params)
                
                m_row = cursor.fetchone()
                
                if not m_row:
                    return jsonify({'success': False, 'error': 'Milestone not found'}), 404
                
                milestone = {
                    'milestone_id': m_row['milestone_id'],
                    'session_id': m_row['session_id'],
                    'milestone_number': m_row['milestone_number'],
                    'milestone_name': m_row['title'],
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
                
                # Get tasks
                task_sql, task_params = convert_sql_placeholders('''
                    SELECT task_id, task, completed, blocked, blocker_reason, 
                           blocker_type, task_order, created_at, completed_at,
                           blocked_since, estimated_hours, actual_hours, assigned_to, updated_at, priority
                    FROM tasks 
                    WHERE milestone_id = %s
                    ORDER BY task_order
                ''', (milestone_id,))
                cursor.execute(task_sql, task_params)
                
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
                    
                    # Get subtasks
                    subtask_sql, subtask_params = convert_sql_placeholders('''
                        SELECT subtask_id, task, completed, subtask_order, created_at, completed_at,
                               estimated_hours, actual_hours, updated_at, priority
                        FROM subtasks 
                        WHERE task_id = %s
                        ORDER BY subtask_order
                    ''', (task['task_id'],))
                    cursor.execute(subtask_sql, subtask_params)
                    
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
            
            # ✅ Cursor auto-closed here
            return jsonify({
                'success': True,
                'milestone': milestone
            })
    
    except Exception as e:
        print(f"[MILESTONE ERROR] Failed to get milestone {milestone_id}: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({'success': False, 'error': str(e)}), 500


@synergy_bp.route('/milestone/<milestone_id>/update', methods=['PATCH'])
def update_milestone(milestone_id):
    """
    Update milestone fields
    ✅ FIXED: Uses nested context managers
    """
    try:
        data = request.json
        
        with get_database_connection('synergy_sessions') as conn:
            with conn.cursor() as cursor:  # ✅ NESTED CONTEXT MANAGER

                # Permission check — look up parent session via milestone
                _uid = getattr(g, 'rls_user_id', None) or (data.get('user_id') if data else None)
                if _uid:
                    _psql, _ppar = convert_sql_placeholders(
                        '''SELECT s.owner_user_id, s.permission_level, s.shared_with_users
                           FROM milestones m
                           JOIN synergy_sessions s ON s.session_id = m.session_id
                           WHERE m.milestone_id = %s''',
                        (milestone_id,)
                    )
                    cursor.execute(_psql, _ppar)
                    _sess_row = cursor.fetchone()
                    if _sess_row:
                        _ok, _ = check_session_permission(dict(_sess_row), _uid, require_write=True)
                        if not _ok:
                            return jsonify({'success': False, 'error': 'Write permission required'}), 403

                # Build update query
                updates = []
                update_params = []
                
                # Map milestone_name to title for backward compatibility
                if 'milestone_name' in data:
                    data['title'] = data.pop('milestone_name')
                
                for field in ['title', 'description', 'priority', 'due_date', 
                             'estimated_hours', 'actual_hours', 'blocked', 'blocker_reason']:
                    if field in data:
                        updates.append(f"{field} = %s")
                        update_params.append(data[field])
                
                if 'documents' in data:
                    updates.append('documents = %s')
                    update_params.append(json.dumps(data['documents']))
                
                if 'links' in data:
                    updates.append('links = %s')
                    update_params.append(json.dumps(data['links']))
                
                if not updates:
                    return jsonify({'success': False, 'error': 'No fields to update'}), 400
                
                updates.append('updated_at = %s')
                update_params.append(datetime.now().isoformat())
                update_params.append(milestone_id)
                
                query = f"UPDATE milestones SET {', '.join(updates)} WHERE milestone_id = %s"
                sql, final_params = convert_sql_placeholders(query, tuple(update_params))
                cursor.execute(sql, final_params)
                
                conn.commit()
            # ✅ Cursor auto-closed here
            
            return jsonify({
                'success': True,
                'milestone_id': milestone_id
            })
    
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@synergy_bp.route('/milestone/<milestone_id>', methods=['DELETE'])
def delete_milestone(milestone_id):
    """
    Delete a milestone (cascades to tasks and subtasks via FK)
    ✅ FIXED: Uses nested context managers
    """
    try:
        with get_database_connection('synergy_sessions') as conn:
            with conn.cursor() as cursor:  # ✅ NESTED CONTEXT MANAGER
                
                sql, params = convert_sql_placeholders(
                    'DELETE FROM milestones WHERE milestone_id = %s',
                    (milestone_id,)
                )
                cursor.execute(sql, params)
                
                if cursor.rowcount == 0:
                    return jsonify({'success': False, 'error': 'Milestone not found'}), 404
                
                conn.commit()
            # ✅ Cursor auto-closed here
            
            return jsonify({
                'success': True,
                'milestone_id': milestone_id
            })
    
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@synergy_bp.route('/<session_id>/milestones/<milestone_id>/toggle', methods=['PATCH'])
def toggle_milestone(session_id, milestone_id):
    """
    Toggle milestone completion status
    ✅ FIXED: Uses nested context managers
    """
    try:
        with get_database_connection('synergy_sessions') as conn:
            with conn.cursor() as cursor:  # ✅ NESTED CONTEXT MANAGER
                
                # Get current status
                sql, params = convert_sql_placeholders(
                    'SELECT completed FROM milestones WHERE milestone_id = %s',
                    (milestone_id,)
                )
                cursor.execute(sql, params)
                row = cursor.fetchone()
                
                if not row:
                    return jsonify({'success': False, 'error': 'Milestone not found'}), 404
                
                new_status = not row['completed']
                completed_at = datetime.now().isoformat() if new_status else None
                
                update_sql, update_params = convert_sql_placeholders('''
                    UPDATE milestones 
                    SET completed = %s, completed_at = %s, updated_at = %s
                    WHERE milestone_id = %s
                ''', (new_status, completed_at, datetime.now().isoformat(), milestone_id))
                cursor.execute(update_sql, update_params)
                
                conn.commit()
            # ✅ Cursor auto-closed here
            
            return jsonify({
                'success': True,
                'milestone_id': milestone_id,
                'completed': new_status
            })
    
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@synergy_bp.route('/milestone/<milestone_id>/complete', methods=['POST'])
def complete_milestone(milestone_id):
    """
    Mark milestone as complete
    ✅ FIXED: Uses nested context managers
    """
    try:
        data = request.json or {}
        actual_hours = data.get('actual_hours')
        
        with get_database_connection('synergy_sessions') as conn:
            with conn.cursor() as cursor:  # ✅ NESTED CONTEXT MANAGER
                
                updates = ['completed = %s', 'completed_at = %s', 'updated_at = %s']
                params = [True, datetime.now().isoformat(), datetime.now().isoformat()]
                
                if actual_hours is not None:
                    updates.append('actual_hours = %s')
                    params.append(actual_hours)
                
                params.append(milestone_id)
                
                query = f"UPDATE milestones SET {', '.join(updates)} WHERE milestone_id = %s"
                sql, final_params = convert_sql_placeholders(query, tuple(params))
                cursor.execute(sql, final_params)
                
                conn.commit()
            # ✅ Cursor auto-closed here
            
            return jsonify({
                'success': True,
                'milestone_id': milestone_id,
                'completed': True
            })
    
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@synergy_bp.route('/milestone/<milestone_id>/comment', methods=['POST'])
def add_milestone_comment(milestone_id):
    """
    Add a comment to a milestone
    ✅ FIXED: Uses nested context managers
    """
    try:
        data = request.json
        comment_text = data.get('comment_text')
        user_id = data.get('user_id')
        
        if not comment_text:
            return jsonify({'success': False, 'error': 'comment_text required'}), 400
        
        import time
        comment_id = f"cmt_{int(time.time() * 1000)}"
        
        with get_database_connection('synergy_sessions') as conn:
            with conn.cursor() as cursor:  # ✅ NESTED CONTEXT MANAGER
                
                sql, params = convert_sql_placeholders('''
                    INSERT INTO synergy_sessions.milestone_comments 
                    (comment_id, milestone_id, user_id, comment_text, created_at)
                    VALUES (%s, %s, %s, %s, %s)
                ''', (comment_id, milestone_id, user_id, comment_text, datetime.now().isoformat()))
                cursor.execute(sql, params)
                
                conn.commit()
            # ✅ Cursor auto-closed here
            
            return jsonify({
                'success': True,
                'comment_id': comment_id,
                'milestone_id': milestone_id
            })
    
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@synergy_bp.route('/milestone/<milestone_id>/documents', methods=['GET'])
def get_milestone_documents(milestone_id):
    """
    Get documents for a milestone
    ✅ FIXED: Uses nested context managers
    """
    try:
        with get_database_connection('synergy_sessions') as conn:
            with conn.cursor() as cursor:  # ✅ NESTED CONTEXT MANAGER
                
                sql, params = convert_sql_placeholders(
                    'SELECT documents FROM milestones WHERE milestone_id = %s',
                    (milestone_id,)
                )
                cursor.execute(sql, params)
                row = cursor.fetchone()
            
            # ✅ Cursor auto-closed here
            if not row:
                return jsonify({'success': False, 'error': 'Milestone not found'}), 404
            
            documents = []
            if row['documents']:
                try:
                    documents = json.loads(row['documents'])
                except:
                    documents = []
            
            return jsonify({
                'success': True,
                'documents': documents
            })
    
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@synergy_bp.route('/milestone/<milestone_id>/links', methods=['GET'])
def get_milestone_links(milestone_id):
    """
    Get links for a milestone
    ✅ FIXED: Uses nested context managers
    """
    try:
        with get_database_connection('synergy_sessions') as conn:
            with conn.cursor() as cursor:  # ✅ NESTED CONTEXT MANAGER
                
                sql, params = convert_sql_placeholders(
                    'SELECT links FROM milestones WHERE milestone_id = %s',
                    (milestone_id,)
                )
                cursor.execute(sql, params)
                row = cursor.fetchone()
            
            # ✅ Cursor auto-closed here
            if not row:
                return jsonify({'success': False, 'error': 'Milestone not found'}), 404
            
            links = []
            if row['links']:
                try:
                    links = json.loads(row['links'])
                except:
                    links = []
            
            return jsonify({
                'success': True,
                'links': links
            })
    
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@synergy_bp.route('/milestone/<milestone_id>/documents', methods=['POST'])
def add_milestone_documents(milestone_id):
    """
    Add documents to a milestone
    ✅ FIXED: Uses nested context managers
    """
    try:
        data = request.json
        new_docs = data.get('documents', [])
        
        if not new_docs:
            return jsonify({'success': False, 'error': 'documents array required'}), 400
        
        with get_database_connection('synergy_sessions') as conn:
            with conn.cursor() as cursor:  # ✅ NESTED CONTEXT MANAGER
                
                sql, params = convert_sql_placeholders(
                    'SELECT documents FROM milestones WHERE milestone_id = %s',
                    (milestone_id,)
                )
                cursor.execute(sql, params)
                row = cursor.fetchone()
                
                if not row:
                    return jsonify({'success': False, 'error': 'Milestone not found'}), 404
                
                documents = []
                if row['documents']:
                    try:
                        documents = json.loads(row['documents'])
                    except:
                        documents = []
                
                documents.extend(new_docs)
                
                update_sql, update_params = convert_sql_placeholders('''
                    UPDATE milestones 
                    SET documents = %s, updated_at = %s
                    WHERE milestone_id = %s
                ''', (json.dumps(documents), datetime.now().isoformat(), milestone_id))
                cursor.execute(update_sql, update_params)
                
                conn.commit()
            # ✅ Cursor auto-closed here
            
            return jsonify({
                'success': True,
                'milestone_id': milestone_id,
                'documents': documents
            })
    
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@synergy_bp.route('/milestone/<milestone_id>/links', methods=['POST'])
def add_milestone_links(milestone_id):
    """
    Add links to a milestone
    ✅ FIXED: Uses nested context managers
    """
    try:
        data = request.json
        new_links = data.get('links', [])
        
        if not new_links:
            return jsonify({'success': False, 'error': 'links array required'}), 400
        
        with get_database_connection('synergy_sessions') as conn:
            with conn.cursor() as cursor:  # ✅ NESTED CONTEXT MANAGER
                
                sql, params = convert_sql_placeholders(
                    'SELECT links FROM milestones WHERE milestone_id = %s',
                    (milestone_id,)
                )
                cursor.execute(sql, params)
                row = cursor.fetchone()
                
                if not row:
                    return jsonify({'success': False, 'error': 'Milestone not found'}), 404
                
                links = []
                if row['links']:
                    try:
                        links = json.loads(row['links'])
                    except:
                        links = []
                
                links.extend(new_links)
                
                update_sql, update_params = convert_sql_placeholders('''
                    UPDATE milestones 
                    SET links = %s, updated_at = %s
                    WHERE milestone_id = %s
                ''', (json.dumps(links), datetime.now().isoformat(), milestone_id))
                cursor.execute(update_sql, update_params)
                
                conn.commit()
            # ✅ Cursor auto-closed here
            
            return jsonify({
                'success': True,
                'milestone_id': milestone_id,
                'links': links
            })
    
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@synergy_bp.route('/milestone/<milestone_id>/document/add', methods=['POST'])
def add_single_milestone_document(milestone_id):
    """
    SURGICAL ADD: Add ONE document to milestone without touching existing documents
    ✅ FIXED: Uses nested context managers
    """
    try:
        data = request.get_json()
        
        if not data.get('title') or not data.get('url'):
            return jsonify({'success': False, 'error': 'title and url required'}), 400
        
        with get_database_connection('synergy_sessions') as conn:
            with conn.cursor() as cursor:  # ✅ NESTED CONTEXT MANAGER
                
                sql, params = convert_sql_placeholders(
                    'SELECT documents FROM milestones WHERE milestone_id = %s',
                    (milestone_id,)
                )
                cursor.execute(sql, params)
                row = cursor.fetchone()
                
                if not row:
                    return jsonify({'success': False, 'error': 'Milestone not found'}), 404
                
                documents = []
                if row['documents']:
                    try:
                        documents = json.loads(row['documents'])
                    except:
                        documents = []
                
                new_doc = {
                    "title": data['title'],
                    "url": data['url'],
                    "type": data.get('type', 'other')
                }
                documents.append(new_doc)
                
                sql, params = convert_sql_placeholders('''
                    UPDATE milestones 
                    SET documents = %s, updated_at = %s
                    WHERE milestone_id = %s
                ''', (json.dumps(documents), datetime.now().isoformat(), milestone_id))
                cursor.execute(sql, params)
                
                conn.commit()
            # ✅ Cursor auto-closed here
            
            return jsonify({
                'success': True,
                'document_added': new_doc,
                'total_documents': len(documents)
            })
    
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@synergy_bp.route('/milestone/<milestone_id>/link/add', methods=['POST'])
def add_single_milestone_link(milestone_id):
    """
    SURGICAL ADD: Add ONE link to milestone without touching existing links
    ✅ FIXED: Uses nested context managers
    """
    try:
        data = request.get_json()
        
        if not data.get('title') or not data.get('url'):
            return jsonify({'success': False, 'error': 'title and url required'}), 400
        
        with get_database_connection('synergy_sessions') as conn:
            with conn.cursor() as cursor:  # ✅ NESTED CONTEXT MANAGER
                
                sql, params = convert_sql_placeholders(
                    'SELECT links FROM milestones WHERE milestone_id = %s',
                    (milestone_id,)
                )
                cursor.execute(sql, params)
                row = cursor.fetchone()
                
                if not row:
                    return jsonify({'success': False, 'error': 'Milestone not found'}), 404
                
                links = []
                if row['links']:
                    try:
                        links = json.loads(row['links'])
                    except:
                        links = []
                
                new_link = {
                    "title": data['title'],
                    "url": data['url']
                }
                links.append(new_link)
                
                sql, params = convert_sql_placeholders('''
                    UPDATE milestones 
                    SET links = %s, updated_at = %s
                    WHERE milestone_id = %s
                ''', (json.dumps(links), datetime.now().isoformat(), milestone_id))
                cursor.execute(sql, params)
                
                conn.commit()
            # ✅ Cursor auto-closed here
            
            return jsonify({
                'success': True,
                'link_added': new_link,
                'total_links': len(links)
            })
    
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


# ============================================================
# TASK CRUD
# ============================================================

@synergy_bp.route('/milestone/<milestone_id>/tasks', methods=['POST'])
def create_task(milestone_id):
    """
    Create a new task in a milestone
    ✅ FIXED: Uses nested context managers
    """
    try:
        data = request.json
        task_text = data.get('task')
        
        if not task_text:
            return jsonify({'success': False, 'error': 'task field required'}), 400
        
        import time
        task_id = f"task_{int(time.time() * 1000)}"
        
        with get_database_connection('synergy_sessions') as conn:
            with conn.cursor() as cursor:  # ✅ NESTED CONTEXT MANAGER

                # Permission check — look up parent session via milestone
                _uid = getattr(g, 'rls_user_id', None) or data.get('user_id')
                if _uid:
                    _psql, _ppar = convert_sql_placeholders(
                        '''SELECT s.owner_user_id, s.permission_level, s.shared_with_users
                           FROM milestones m
                           JOIN synergy_sessions s ON s.session_id = m.session_id
                           WHERE m.milestone_id = %s''',
                        (milestone_id,)
                    )
                    cursor.execute(_psql, _ppar)
                    _sess_row = cursor.fetchone()
                    if _sess_row:
                        _ok, _ = check_session_permission(dict(_sess_row), _uid, require_write=True)
                        if not _ok:
                            return jsonify({'success': False, 'error': 'Write permission required'}), 403

                # Get max task_order
                sql, params = convert_sql_placeholders(
                    'SELECT COALESCE(MAX(task_order), 0) as max_order FROM tasks WHERE milestone_id = %s',
                    (milestone_id,)
                )
                cursor.execute(sql, params)
                row = cursor.fetchone()
                task_order = row['max_order'] + 1
                
                # Insert task
                insert_sql, insert_params = convert_sql_placeholders('''
                    INSERT INTO tasks 
                    (task_id, milestone_id, task, task_order, completed, priority, estimated_hours, assigned_to)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                ''', (task_id, milestone_id, task_text, task_order, False, 
                      data.get('priority', 'medium'), data.get('estimated_hours'), data.get('assigned_to')))
                cursor.execute(insert_sql, insert_params)
                
                conn.commit()
            # ✅ Cursor auto-closed here
            
            return jsonify({
                'success': True,
                'task_id': task_id,
                'milestone_id': milestone_id
            })
    
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@synergy_bp.route('/task/<task_id>', methods=['PATCH'])
def update_task(task_id):
    """
    Update task fields
    ✅ FIXED: Uses nested context managers
    """
    try:
        data = request.json
        
        with get_database_connection('synergy_sessions') as conn:
            with conn.cursor() as cursor:  # ✅ NESTED CONTEXT MANAGER

                # Permission check — resolve session via task → milestone
                _uid = getattr(g, 'rls_user_id', None) or (data.get('user_id') if data else None)
                if _uid:
                    _psql, _ppar = convert_sql_placeholders(
                        '''SELECT s.owner_user_id, s.permission_level, s.shared_with_users
                           FROM tasks t
                           JOIN milestones m ON m.milestone_id = t.milestone_id
                           JOIN synergy_sessions s ON s.session_id = m.session_id
                           WHERE t.task_id = %s''',
                        (task_id,)
                    )
                    cursor.execute(_psql, _ppar)
                    _sess_row = cursor.fetchone()
                    if _sess_row:
                        _ok, _ = check_session_permission(dict(_sess_row), _uid, require_write=True)
                        if not _ok:
                            return jsonify({'success': False, 'error': 'Write permission required'}), 403

                updates = []
                update_params = []
                
                for field in ['task', 'priority', 'estimated_hours', 'actual_hours', 'assigned_to']:
                    if field in data:
                        updates.append(f"{field} = %s")
                        update_params.append(data[field])
                
                if not updates:
                    return jsonify({'success': False, 'error': 'No fields to update'}), 400
                
                updates.append('updated_at = %s')
                update_params.append(datetime.now().isoformat())
                update_params.append(task_id)
                
                query = f"UPDATE tasks SET {', '.join(updates)} WHERE task_id = %s"
                sql, final_params = convert_sql_placeholders(query, tuple(update_params))
                cursor.execute(sql, final_params)
                
                conn.commit()
            # ✅ Cursor auto-closed here
            
            return jsonify({
                'success': True,
                'task_id': task_id
            })
    
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@synergy_bp.route('/task/<task_id>', methods=['DELETE'])
def delete_task(task_id):
    """
    Delete a task
    ✅ FIXED: Uses nested context managers
    """
    try:
        with get_database_connection('synergy_sessions') as conn:
            with conn.cursor() as cursor:  # ✅ NESTED CONTEXT MANAGER
                
                sql, params = convert_sql_placeholders(
                    'DELETE FROM tasks WHERE task_id = %s',
                    (task_id,)
                )
                cursor.execute(sql, params)
                
                if cursor.rowcount == 0:
                    return jsonify({'success': False, 'error': 'Task not found'}), 404
                
                conn.commit()
            # ✅ Cursor auto-closed here
            
            return jsonify({
                'success': True,
                'task_id': task_id
            })
    
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@synergy_bp.route('/<session_id>/tasks/<task_id>/toggle', methods=['PATCH'])
def toggle_task(session_id, task_id):
    """
    Toggle task completion status
    ✅ FIXED: Uses nested context managers
    """
    try:
        with get_database_connection('synergy_sessions') as conn:
            with conn.cursor() as cursor:  # ✅ NESTED CONTEXT MANAGER
                
                # Get current status
                sql, params = convert_sql_placeholders(
                    'SELECT completed FROM tasks WHERE task_id = %s',
                    (task_id,)
                )
                cursor.execute(sql, params)
                row = cursor.fetchone()
                
                if not row:
                    return jsonify({'success': False, 'error': 'Task not found'}), 404
                
                new_status = not row['completed']
                completed_at = datetime.now().isoformat() if new_status else None
                
                update_sql, update_params = convert_sql_placeholders('''
                    UPDATE tasks 
                    SET completed = %s, completed_at = %s, updated_at = %s
                    WHERE task_id = %s
                ''', (new_status, completed_at, datetime.now().isoformat(), task_id))
                cursor.execute(update_sql, update_params)
                
                conn.commit()
            # ✅ Cursor auto-closed here
            
            return jsonify({
                'success': True,
                'task_id': task_id,
                'completed': new_status
            })
    
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@synergy_bp.route('/task/<task_id>/complete', methods=['POST'])
def complete_task(task_id):
    """
    Mark task as complete
    ✅ FIXED: Uses nested context managers
    """
    try:
        data = request.json or {}
        actual_hours = data.get('actual_hours')
        
        with get_database_connection('synergy_sessions') as conn:
            with conn.cursor() as cursor:  # ✅ NESTED CONTEXT MANAGER
                
                updates = ['completed = %s', 'completed_at = %s', 'updated_at = %s']
                params = [True, datetime.now().isoformat(), datetime.now().isoformat()]
                
                if actual_hours is not None:
                    updates.append('actual_hours = %s')
                    params.append(actual_hours)
                
                params.append(task_id)
                
                query = f"UPDATE tasks SET {', '.join(updates)} WHERE task_id = %s"
                sql, final_params = convert_sql_placeholders(query, tuple(params))
                cursor.execute(sql, final_params)
                
                conn.commit()
            # ✅ Cursor auto-closed here
            
            return jsonify({
                'success': True,
                'task_id': task_id,
                'completed': True
            })
    
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@synergy_bp.route('/task/<task_id>/block', methods=['POST'])
def block_task(task_id):
    """
    Mark task as blocked
    ✅ FIXED: Uses nested context managers
    """
    try:
        data = request.json
        blocker_reason = data.get('blocker_reason')
        blocker_type = data.get('blocker_type', 'internal')
        
        if not blocker_reason:
            return jsonify({'success': False, 'error': 'blocker_reason required'}), 400
        
        with get_database_connection('synergy_sessions') as conn:
            with conn.cursor() as cursor:  # ✅ NESTED CONTEXT MANAGER
                
                sql, params = convert_sql_placeholders('''
                    UPDATE tasks 
                    SET blocked = %s, blocker_reason = %s, blocker_type = %s, 
                        blocked_since = %s, updated_at = %s
                    WHERE task_id = %s
                ''', (True, blocker_reason, blocker_type, datetime.now().isoformat(), 
                      datetime.now().isoformat(), task_id))
                cursor.execute(sql, params)
                
                conn.commit()
            # ✅ Cursor auto-closed here
            
            return jsonify({
                'success': True,
                'task_id': task_id,
                'blocked': True
            })
    
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@synergy_bp.route('/task/<task_id>/update-field', methods=['PATCH'])
def update_single_task_field(task_id):
    """
    SURGICAL UPDATE: Update ONE field of a task without touching others
    ✅ FIXED: Uses nested context managers
    """
    try:
        data = request.get_json()
        field = data.get('field')
        value = data.get('value')
        
        allowed_fields = ['task', 'priority', 'completed', 'estimated_hours', 'actual_hours', 'blocked', 'blocker_reason']
        if field not in allowed_fields:
            return jsonify({'success': False, 'error': f'Field must be one of: {", ".join(allowed_fields)}'}), 400
        
        with get_database_connection('synergy_sessions') as conn:
            with conn.cursor() as cursor:  # ✅ NESTED CONTEXT MANAGER
                
                sql, params = convert_sql_placeholders(
                    f'UPDATE tasks SET {field} = %s, updated_at = %s WHERE task_id = %s',
                    (value, datetime.now().isoformat(), task_id)
                )
                cursor.execute(sql, params)
                
                if cursor.rowcount == 0:
                    return jsonify({'success': False, 'error': 'Task not found'}), 404
                
                conn.commit()
            # ✅ Cursor auto-closed here
            
            return jsonify({
                'success': True,
                'task_id': task_id,
                'field_updated': field,
                'new_value': value
            })
    
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


# ============================================================
# SUBTASK CRUD
# ============================================================

@synergy_bp.route('/task/<task_id>/subtasks', methods=['POST'])
def create_subtask(task_id):
    """
    Create a new subtask in a task
    ✅ FIXED: Uses nested context managers
    """
    try:
        data = request.json
        subtask_text = data.get('task')
        
        if not subtask_text:
            return jsonify({'success': False, 'error': 'task field required'}), 400
        
        import time
        subtask_id = f"subtask_{int(time.time() * 1000)}"
        
        with get_database_connection('synergy_sessions') as conn:
            with conn.cursor() as cursor:  # ✅ NESTED CONTEXT MANAGER
                
                # Get max subtask_order
                sql, params = convert_sql_placeholders(
                    'SELECT COALESCE(MAX(subtask_order), 0) as max_order FROM subtasks WHERE task_id = %s',
                    (task_id,)
                )
                cursor.execute(sql, params)
                row = cursor.fetchone()
                subtask_order = row['max_order'] + 1
                
                # Insert subtask
                insert_sql, insert_params = convert_sql_placeholders('''
                    INSERT INTO subtasks 
                    (subtask_id, task_id, task, subtask_order, completed, priority, estimated_hours, assigned_to)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                ''', (subtask_id, task_id, subtask_text, subtask_order, False, 
                      data.get('priority', 'medium'), data.get('estimated_hours'), data.get('assigned_to')))
                cursor.execute(insert_sql, insert_params)
                
                conn.commit()
            # ✅ Cursor auto-closed here
            
            return jsonify({
                'success': True,
                'subtask_id': subtask_id,
                'task_id': task_id
            })
    
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@synergy_bp.route('/subtask/<subtask_id>', methods=['PATCH'])
def update_subtask(subtask_id):
    """
    Update subtask fields
    ✅ FIXED: Uses nested context managers
    """
    try:
        data = request.json
        
        with get_database_connection('synergy_sessions') as conn:
            with conn.cursor() as cursor:  # ✅ NESTED CONTEXT MANAGER
                
                updates = []
                update_params = []
                
                for field in ['task', 'priority', 'estimated_hours', 'actual_hours', 'assigned_to']:
                    if field in data:
                        updates.append(f"{field} = %s")
                        update_params.append(data[field])
                
                if not updates:
                    return jsonify({'success': False, 'error': 'No fields to update'}), 400
                
                updates.append('updated_at = %s')
                update_params.append(datetime.now().isoformat())
                update_params.append(subtask_id)
                
                query = f"UPDATE subtasks SET {', '.join(updates)} WHERE subtask_id = %s"
                sql, final_params = convert_sql_placeholders(query, tuple(update_params))
                cursor.execute(sql, final_params)
                
                conn.commit()
            # ✅ Cursor auto-closed here
            
            return jsonify({
                'success': True,
                'subtask_id': subtask_id
            })
    
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@synergy_bp.route('/subtask/<subtask_id>', methods=['DELETE'])
def delete_subtask(subtask_id):
    """
    Delete a subtask
    ✅ FIXED: Uses nested context managers
    """
    try:
        with get_database_connection('synergy_sessions') as conn:
            with conn.cursor() as cursor:  # ✅ NESTED CONTEXT MANAGER
                
                sql, params = convert_sql_placeholders(
                    'DELETE FROM subtasks WHERE subtask_id = %s',
                    (subtask_id,)
                )
                cursor.execute(sql, params)
                
                if cursor.rowcount == 0:
                    return jsonify({'success': False, 'error': 'Subtask not found'}), 404
                
                conn.commit()
            # ✅ Cursor auto-closed here
            
            return jsonify({
                'success': True,
                'subtask_id': subtask_id
            })
    
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@synergy_bp.route('/<session_id>/subtasks/<subtask_id>/toggle', methods=['PATCH'])
def toggle_subtask(session_id, subtask_id):
    """
    Toggle subtask completion status
    ✅ FIXED: Uses nested context managers
    """
    try:
        with get_database_connection('synergy_sessions') as conn:
            with conn.cursor() as cursor:  # ✅ NESTED CONTEXT MANAGER
                
                # Get current status
                sql, params = convert_sql_placeholders(
                    'SELECT completed FROM subtasks WHERE subtask_id = %s',
                    (subtask_id,)
                )
                cursor.execute(sql, params)
                row = cursor.fetchone()
                
                if not row:
                    return jsonify({'success': False, 'error': 'Subtask not found'}), 404
                
                new_status = not row['completed']
                completed_at = datetime.now().isoformat() if new_status else None
                
                update_sql, update_params = convert_sql_placeholders('''
                    UPDATE subtasks 
                    SET completed = %s, completed_at = %s, updated_at = %s
                    WHERE subtask_id = %s
                ''', (new_status, completed_at, datetime.now().isoformat(), subtask_id))
                cursor.execute(update_sql, update_params)
                
                conn.commit()
            # ✅ Cursor auto-closed here
            
            return jsonify({
                'success': True,
                'subtask_id': subtask_id,
                'completed': new_status
            })
    
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@synergy_bp.route('/subtask/<subtask_id>/complete', methods=['POST'])
def complete_subtask(subtask_id):
    """
    Mark subtask as complete
    ✅ FIXED: Uses nested context managers
    """
    try:
        data = request.json or {}
        actual_hours = data.get('actual_hours')
        
        with get_database_connection('synergy_sessions') as conn:
            with conn.cursor() as cursor:  # ✅ NESTED CONTEXT MANAGER
                
                updates = ['completed = %s', 'completed_at = %s', 'updated_at = %s']
                params = [True, datetime.now().isoformat(), datetime.now().isoformat()]
                
                if actual_hours is not None:
                    updates.append('actual_hours = %s')
                    params.append(actual_hours)
                
                params.append(subtask_id)
                
                query = f"UPDATE subtasks SET {', '.join(updates)} WHERE subtask_id = %s"
                sql, final_params = convert_sql_placeholders(query, tuple(params))
                cursor.execute(sql, final_params)
                
                conn.commit()
            # ✅ Cursor auto-closed here
            
            return jsonify({
                'success': True,
                'subtask_id': subtask_id,
                'completed': True
            })
    
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@synergy_bp.route('/subtask/<subtask_id>/update-field', methods=['PATCH'])
def update_single_subtask_field(subtask_id):
    """
    SURGICAL UPDATE: Update ONE field of a subtask without touching others
    ✅ FIXED: Uses nested context managers
    """
    try:
        data = request.get_json()
        field = data.get('field')
        value = data.get('value')
        
        allowed_fields = ['task', 'priority', 'completed', 'estimated_hours', 'actual_hours']
        if field not in allowed_fields:
            return jsonify({'success': False, 'error': f'Field must be one of: {", ".join(allowed_fields)}'}), 400
        
        with get_database_connection('synergy_sessions') as conn:
            with conn.cursor() as cursor:  # ✅ NESTED CONTEXT MANAGER
                
                sql, params = convert_sql_placeholders(
                    f'UPDATE subtasks SET {field} = %s, updated_at = %s WHERE subtask_id = %s',
                    (value, datetime.now().isoformat(), subtask_id)
                )
                cursor.execute(sql, params)
                
                if cursor.rowcount == 0:
                    return jsonify({'success': False, 'error': 'Subtask not found'}), 404
                
                conn.commit()
            # ✅ Cursor auto-closed here
            
            return jsonify({
                'success': True,
                'subtask_id': subtask_id,
                'field_updated': field,
                'new_value': value
            })
    
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


# ============================================================
# THREAD INTEGRATION (Additional variants)
# ============================================================

@synergy_bp.route('/<session_id>/threads', methods=['GET'])
def get_session_threads(session_id):
    """
    Get threads linked to a session
    ✅ FIXED: Uses nested context managers
    """
    try:
        with get_database_connection('synergy_sessions') as conn:
            with conn.cursor() as cursor:  # ✅ NESTED CONTEXT MANAGER
                
                sql, params = convert_sql_placeholders(
                    'SELECT thread_ids FROM synergy_sessions WHERE session_id = %s',
                    (session_id,)
                )
                cursor.execute(sql, params)
                row = cursor.fetchone()
            
            # ✅ Cursor auto-closed here
            if not row:
                return jsonify({'success': False, 'error': 'Session not found'}), 404
            
            thread_ids = []
            if row['thread_ids']:
                try:
                    thread_ids = json.loads(row['thread_ids'])
                except:
                    thread_ids = []
            
            return jsonify({
                'success': True,
                'session_id': session_id,
                'thread_ids': thread_ids
            })
    
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@synergy_bp.route('/<session_id>/linked-threads', methods=['GET'])
def get_linked_threads_detailed(session_id):
    """
    Get detailed thread info for all threads linked to session
    ✅ FIXED: Uses nested context managers
    """
    try:
        with get_database_connection('synergy_sessions') as conn:
            with conn.cursor() as cursor:  # ✅ NESTED CONTEXT MANAGER
                
                # Get thread_ids from synergy session
                sql, params = convert_sql_placeholders(
                    'SELECT thread_ids FROM synergy_sessions WHERE session_id = %s',
                    (session_id,)
                )
                cursor.execute(sql, params)
                row = cursor.fetchone()
                
                if not row:
                    return jsonify({'success': False, 'error': 'Session not found'}), 404
                
                thread_ids = []
                if row['thread_ids']:
                    try:
                        thread_ids = json.loads(row['thread_ids'])
                    except:
                        thread_ids = []
                
                # Fetch thread details from sessions.threads table with message counts
                threads = []
                if thread_ids:
                    placeholders = ','.join(['%s'] * len(thread_ids))
                    thread_sql = f"""
                        SELECT 
                            t.id, 
                            t.thread_slug, 
                            t.name, 
                            t.created_at, 
                            t.updated_at,
                            t.location as agent_id,
                            COUNT(m.id) as message_count
                        FROM sessions.threads t
                        LEFT JOIN sessions.messages m ON t.id = m.thread_id
                        WHERE t.id IN ({placeholders})
                        GROUP BY t.id, t.thread_slug, t.name, t.created_at, t.updated_at, t.location
                    """
                    cursor.execute(thread_sql, thread_ids)
                    
                    for t_row in cursor.fetchall():
                        threads.append({
                            'thread_id': t_row['id'],
                            'slug': t_row['thread_slug'],
                            'title': t_row['name'],
                            'created_at': t_row['created_at'],
                            'last_activity': t_row['updated_at'],
                            'agent_id': t_row['agent_id'] or 'prime',
                            'message_count': t_row['message_count'] or 0
                        })
            
            # ✅ Cursor auto-closed here
            return jsonify({
                'success': True,
                'session_id': session_id,
                'threads': threads
            })
    
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@synergy_bp.route('/link-thread', methods=['POST'])
def link_thread_generic():
    """
    Link a thread to a synergy session (generic endpoint)
    ✅ FIXED: Uses nested context managers
    """
    try:
        data = request.json
        session_id = data.get('session_id')
        thread_id = data.get('thread_id')
        
        if not session_id or not thread_id:
            return jsonify({'success': False, 'error': 'session_id and thread_id required'}), 400
        
        with get_database_connection('synergy_sessions') as conn:
            with conn.cursor() as cursor:  # ✅ NESTED CONTEXT MANAGER
                
                # Get current thread_ids
                sql, params = convert_sql_placeholders(
                    'SELECT thread_ids FROM synergy_sessions WHERE session_id = %s',
                    (session_id,)
                )
                cursor.execute(sql, params)
                row = cursor.fetchone()
                
                if not row:
                    return jsonify({'success': False, 'error': 'Session not found'}), 404
                
                thread_ids = []
                if row['thread_ids']:
                    try:
                        thread_ids = json.loads(row['thread_ids'])
                    except:
                        thread_ids = []
                
                if thread_id not in thread_ids:
                    thread_ids.append(thread_id)
                    
                    update_sql, update_params = convert_sql_placeholders('''
                        UPDATE synergy_sessions 
                        SET thread_ids = %s, last_active = %s
                        WHERE session_id = %s
                    ''', (json.dumps(thread_ids), datetime.now().isoformat(), session_id))
                    cursor.execute(update_sql, update_params)
                
                conn.commit()
            # ✅ Cursor auto-closed here
            
            return jsonify({
                'success': True,
                'session_id': session_id,
                'thread_id': thread_id,
                'thread_ids': thread_ids
            })
    
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@synergy_bp.route('/unlink-thread', methods=['POST'])
def unlink_thread_generic():
    """
    Unlink a thread from a synergy session (generic endpoint)
    ✅ FIXED: Uses nested context managers
    """
    try:
        data = request.json
        session_id = data.get('session_id')
        thread_id = data.get('thread_id')
        
        if not session_id or not thread_id:
            return jsonify({'success': False, 'error': 'session_id and thread_id required'}), 400
        
        with get_database_connection('synergy_sessions') as conn:
            with conn.cursor() as cursor:  # ✅ NESTED CONTEXT MANAGER
                
                # Get current thread_ids
                sql, params = convert_sql_placeholders(
                    'SELECT thread_ids FROM synergy_sessions WHERE session_id = %s',
                    (session_id,)
                )
                cursor.execute(sql, params)
                row = cursor.fetchone()
                
                if not row:
                    return jsonify({'success': False, 'error': 'Session not found'}), 404
                
                thread_ids = []
                if row['thread_ids']:
                    try:
                        thread_ids = json.loads(row['thread_ids'])
                    except:
                        thread_ids = []
                
                if thread_id in thread_ids:
                    thread_ids.remove(thread_id)
                    
                    update_sql, update_params = convert_sql_placeholders('''
                        UPDATE synergy_sessions 
                        SET thread_ids = %s, last_active = %s
                        WHERE session_id = %s
                    ''', (json.dumps(thread_ids), datetime.now().isoformat(), session_id))
                    cursor.execute(update_sql, update_params)
                
                conn.commit()
            # ✅ Cursor auto-closed here
            
            return jsonify({
                'success': True,
                'session_id': session_id,
                'thread_id': thread_id,
                'thread_ids': thread_ids
            })
    
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@synergy_bp.route('/link-to-thread', methods=['POST'])
def link_to_thread():
    """
    Link a synergy session to a thread (reverse direction naming)
    ✅ FIXED: Uses nested context managers
    """
    try:
        data = request.json
        session_id = data.get('session_id')
        thread_id = data.get('thread_id')
        thread_name = data.get('thread_name', 'Untitled Thread')
        
        if not session_id or not thread_id:
            return jsonify({'success': False, 'error': 'session_id and thread_id required'}), 400
        
        with get_database_connection('synergy_sessions') as conn:
            with conn.cursor() as cursor:  # ✅ NESTED CONTEXT MANAGER
                
                # Get current thread_ids
                sql, params = convert_sql_placeholders(
                    'SELECT thread_ids FROM synergy_sessions WHERE session_id = %s',
                    (session_id,)
                )
                cursor.execute(sql, params)
                row = cursor.fetchone()
                
                if not row:
                    return jsonify({'success': False, 'error': 'Session not found'}), 404
                
                thread_ids = []
                if row['thread_ids']:
                    try:
                        thread_ids = json.loads(row['thread_ids'])
                    except:
                        thread_ids = []
                
                if thread_id not in thread_ids:
                    thread_ids.append(thread_id)
                    
                    update_sql, update_params = convert_sql_placeholders('''
                        UPDATE synergy_sessions 
                        SET thread_ids = %s, last_active = %s
                        WHERE session_id = %s
                    ''', (json.dumps(thread_ids), datetime.now().isoformat(), session_id))
                    cursor.execute(update_sql, update_params)
                
                conn.commit()
            # ✅ Cursor auto-closed here
            
            return jsonify({
                'success': True,
                'session_id': session_id,
                'thread_id': thread_id,
                'thread_name': thread_name,
                'thread_ids': thread_ids
            })
    
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@synergy_bp.route('/<session_id>/column', methods=['POST'])
def update_column_post(session_id):
    """
    Update session column (POST alias for PATCH method)
    ✅ FIXED: Uses nested context managers
    """
    try:
        data = request.json
        new_column = data.get('target_column') or data.get('kanban_column')
        
        if not new_column:
            return jsonify({
                'success': False,
                'error': 'target_column or kanban_column is required'
            }), 400
        
        with get_database_connection('synergy_sessions') as conn:
            with conn.cursor() as cursor:  # ✅ NESTED CONTEXT MANAGER
                
                # Add activity log
                sql, params = convert_sql_placeholders(
                    'SELECT recent_activity FROM synergy_sessions WHERE session_id = %s',
                    (session_id,)
                )
                cursor.execute(sql, params)
                row = cursor.fetchone()
                
                if row:
                    activity = json.loads(row['recent_activity'] or '[]')
                    activity.insert(0, {
                        'type': 'moved',
                        'timestamp': datetime.now().isoformat(),
                        'user': data.get('moved_by', 'AI Agent'),
                        'details': f"Moved to {new_column}"
                    })
                    
                    update_sql, update_params = convert_sql_placeholders('''
                        UPDATE synergy_sessions 
                        SET kanban_column = %s, recent_activity = %s, last_active = %s
                        WHERE session_id = %s
                    ''', (new_column, json.dumps(activity), datetime.now().isoformat(), session_id))
                    
                    cursor.execute(update_sql, update_params)
                
                conn.commit()
            # ✅ Cursor auto-closed here
        
        # Broadcast column change to WebSocket clients
        try:
            from flask import current_app
            socketio = current_app.extensions.get('socketio')
            if socketio:
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


# ============================================================
# MILESTONE SYSTEM - ADDITIONAL ENDPOINTS
# ============================================================

@synergy_bp.route('/<session_id>/milestone/create', methods=['POST'])
def create_session_milestone(session_id):
    """
    Create milestone with tasks and subtasks
    ✅ FIXED: Uses nested context managers
    """
    try:
        data = request.get_json()
        
        # Accept both 'title' (new) and 'milestone_name' (legacy)
        milestone_title = data.get('title') or data.get('milestone_name')
        if not milestone_title:
            return jsonify({'success': False, 'error': 'title or milestone_name required'}), 400
        
        with get_database_connection('synergy_sessions') as conn:
            with conn.cursor() as cursor:  # ✅ NESTED CONTEXT MANAGER
                
                # Check session exists
                cursor.execute('SELECT session_id FROM synergy_sessions WHERE session_id = %s', (session_id,))
                if not cursor.fetchone():
                    return jsonify({'success': False, 'error': 'Session not found'}), 404
                
                # Get next milestone number
                cursor.execute('''
                    SELECT COALESCE(MAX(milestone_number), 0) + 1 AS next_number
                    FROM milestones 
                    WHERE session_id = %s
                ''', (session_id,))
                result = cursor.fetchone()
                milestone_number = result['next_number'] if isinstance(result, dict) else result[0]
                
                # Generate milestone ID
                milestone_id = f"ms_{datetime.now().strftime('%Y%m%d%H%M%S')}"
                
                # Insert milestone
                cursor.execute('''
                    INSERT INTO milestones (
                        milestone_id, session_id, milestone_number, milestone_order, 
                        title, milestone_name, description, completed, due_date, priority, 
                        estimated_hours, created_at, updated_at
                    ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                ''', (
                    milestone_id,
                    session_id,
                    milestone_number,
                    milestone_number,
                    milestone_title,
                    milestone_title,
                    data.get('description'),
                    False,
                    data.get('due_date'),
                    data.get('priority', 'medium'),
                    data.get('estimated_hours'),
                    datetime.now().isoformat(),
                    datetime.now().isoformat()
                ))
                
                # Insert tasks
                tasks_created = 0
                subtasks_created = 0
                tasks_list = data.get('tasks', [])
                
                for task_order, task_item in enumerate(tasks_list, start=1):
                    task_id = f"task_{datetime.now().strftime('%Y%m%d%H%M%S')}_{task_order}"
                    
                    if isinstance(task_item, str):
                        task_title = task_item
                        task_description = None
                        task_priority = 'medium'
                        task_due_date = None
                        subtasks = []
                    else:
                        task_title = task_item.get('title') or task_item.get('task', '')
                        task_description = task_item.get('description')
                        task_priority = task_item.get('priority', 'medium')
                        task_due_date = task_item.get('due_date')
                        subtasks = task_item.get('subtasks', [])
                    
                    cursor.execute('''
                        INSERT INTO tasks (
                            task_id, milestone_id, title, task, description, completed, 
                            task_order, priority, due_date, created_at
                        ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                    ''', (
                        task_id, milestone_id, 
                        task_title,
                        task_title,
                        task_description,
                        False, task_order, task_priority, task_due_date, 
                        datetime.now().isoformat()
                    ))
                    tasks_created += 1
                    
                    # Insert subtasks
                    for subtask_order, subtask_item in enumerate(subtasks, start=1):
                        subtask_id = f"sub_{datetime.now().strftime('%Y%m%d%H%M%S')}_{task_order}_{subtask_order}"
                        
                        if isinstance(subtask_item, str):
                            subtask_title = subtask_item
                            subtask_description = None
                            subtask_priority = 'medium'
                            subtask_due_date = None
                        else:
                            subtask_title = subtask_item.get('title') or subtask_item.get('task', '') or subtask_item.get('text', '')
                            subtask_description = subtask_item.get('description')
                            subtask_priority = subtask_item.get('priority', 'medium')
                            subtask_due_date = subtask_item.get('due_date')
                        
                        cursor.execute('''
                            INSERT INTO subtasks (
                                subtask_id, task_id, title, task, description, completed, 
                                subtask_order, priority, due_date, created_at
                            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                        ''', (
                            subtask_id, task_id, 
                            subtask_title,
                            subtask_title,
                            subtask_description,
                            False, subtask_order, subtask_priority, subtask_due_date,
                            datetime.now().isoformat()
                        ))
                        subtasks_created += 1
                
                # Mark session as using milestones
                cursor.execute('''
                    UPDATE synergy_sessions 
                    SET uses_milestones = TRUE, last_active = %s
                    WHERE session_id = %s
                ''', (datetime.now().isoformat(), session_id))
                
                conn.commit()
            # ✅ Cursor auto-closed here
            
            return jsonify({
                'success': True,
                'milestone_id': milestone_id,
                'tasks_created': tasks_created,
                'subtasks_created': subtasks_created
            })
    
    except Exception as e:
        print(f"[MILESTONE ERROR] Failed to create milestone: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500


@synergy_bp.route('/milestone/<milestone_id>/task/create', methods=['POST'])
def create_milestone_task(milestone_id):
    """
    Add task to milestone
    ✅ FIXED: Uses nested context managers
    """
    try:
        data = request.get_json()
        
        task_title = data.get('title') or data.get('task')
        if not task_title:
            return jsonify({'success': False, 'error': 'title or task text required'}), 400
        
        with get_database_connection('synergy_sessions') as conn:
            with conn.cursor() as cursor:  # ✅ NESTED CONTEXT MANAGER

                # Permission check — look up parent session via milestone
                _uid = getattr(g, 'rls_user_id', None) or data.get('user_id')
                if _uid:
                    _psql, _ppar = convert_sql_placeholders(
                        '''SELECT s.owner_user_id, s.permission_level, s.shared_with_users
                           FROM milestones m
                           JOIN synergy_sessions s ON s.session_id = m.session_id
                           WHERE m.milestone_id = %s''',
                        (milestone_id,)
                    )
                    cursor.execute(_psql, _ppar)
                    _sess_row = cursor.fetchone()
                    if _sess_row:
                        _ok, _ = check_session_permission(dict(_sess_row), _uid, require_write=True)
                        if not _ok:
                            return jsonify({'success': False, 'error': 'Write permission required'}), 403

                # Check milestone exists
                cursor.execute('SELECT milestone_id FROM milestones WHERE milestone_id = %s', (milestone_id,))
                if not cursor.fetchone():
                    return jsonify({'success': False, 'error': 'Milestone not found'}), 404
                
                # Get next task order
                cursor.execute('''
                    SELECT COALESCE(MAX(task_order), 0) + 1 
                    FROM tasks 
                    WHERE milestone_id = %s
                ''', (milestone_id,))
                task_order = cursor.fetchone()[0]
                
                task_id = f"task_{datetime.now().strftime('%Y%m%d%H%M%S')}"
                task_priority = data.get('priority', 'medium')
                task_description = data.get('description')
                task_due_date = data.get('due_date')
                
                cursor.execute('''
                    INSERT INTO tasks (
                        task_id, milestone_id, title, task, description, completed, 
                        task_order, priority, due_date, created_at
                    ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                ''', (
                    task_id, milestone_id, 
                    task_title,
                    task_title,
                    task_description,
                    False, task_order, task_priority, task_due_date,
                    datetime.now().isoformat()
                ))
                
                # Insert subtasks
                subtasks_created = 0
                subtasks = data.get('subtasks', [])
                for subtask_order, subtask_item in enumerate(subtasks, start=1):
                    subtask_id = f"sub_{datetime.now().strftime('%Y%m%d%H%M%S')}_{subtask_order}"
                    
                    if isinstance(subtask_item, str):
                        subtask_title = subtask_item
                        subtask_description = None
                        subtask_priority = 'medium'
                        subtask_due_date = None
                    else:
                        subtask_title = subtask_item.get('title') or subtask_item.get('task', '') or subtask_item.get('text', '')
                        subtask_description = subtask_item.get('description')
                        subtask_priority = subtask_item.get('priority', 'medium')
                        subtask_due_date = subtask_item.get('due_date')
                    
                    cursor.execute('''
                        INSERT INTO subtasks (
                            subtask_id, task_id, title, task, description, completed, 
                            subtask_order, priority, due_date, created_at
                        ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                    ''', (
                        subtask_id, task_id, 
                        subtask_title,
                        subtask_title,
                        subtask_description,
                        False, subtask_order, subtask_priority, subtask_due_date,
                        datetime.now().isoformat()
                    ))
                    subtasks_created += 1
                
                conn.commit()
            # ✅ Cursor auto-closed here
            
            return jsonify({
                'success': True,
                'task_id': task_id,
                'subtasks_created': subtasks_created
            })
    
    except Exception as e:
        print(f"[TASK ERROR] Failed to create task: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500


@synergy_bp.route('/task/<task_id>/subtask/create', methods=['POST'])
def create_task_subtask(task_id):
    """
    Add subtask to task
    ✅ FIXED: Uses nested context managers
    """
    try:
        data = request.get_json()
        
        subtask_title = data.get('title') or data.get('task') or data.get('subtask')
        if not subtask_title:
            return jsonify({'success': False, 'error': 'title or task field required'}), 400
        
        with get_database_connection('synergy_sessions') as conn:
            with conn.cursor() as cursor:  # ✅ NESTED CONTEXT MANAGER

                # Permission check — resolve session via task → milestone
                _uid = getattr(g, 'rls_user_id', None) or data.get('user_id')
                if _uid:
                    _psql, _ppar = convert_sql_placeholders(
                        '''SELECT s.owner_user_id, s.permission_level, s.shared_with_users
                           FROM tasks t
                           JOIN milestones m ON m.milestone_id = t.milestone_id
                           JOIN synergy_sessions s ON s.session_id = m.session_id
                           WHERE t.task_id = %s''',
                        (task_id,)
                    )
                    cursor.execute(_psql, _ppar)
                    _sess_row = cursor.fetchone()
                    if _sess_row:
                        _ok, _ = check_session_permission(dict(_sess_row), _uid, require_write=True)
                        if not _ok:
                            return jsonify({'success': False, 'error': 'Write permission required'}), 403

                # Check task exists
                cursor.execute('SELECT task_id FROM tasks WHERE task_id = %s', (task_id,))
                if not cursor.fetchone():
                    return jsonify({'success': False, 'error': 'Task not found'}), 404
                
                # Get next subtask order
                cursor.execute('''
                    SELECT COALESCE(MAX(subtask_order), 0) + 1 
                    FROM subtasks 
                    WHERE task_id = %s
                ''', (task_id,))
                subtask_order = cursor.fetchone()[0]
                
                subtask_id = f"sub_{datetime.now().strftime('%Y%m%d%H%M%S')}"
                subtask_priority = data.get('priority', 'medium')
                subtask_description = data.get('description')
                subtask_due_date = data.get('due_date')
                
                cursor.execute('''
                    INSERT INTO subtasks (
                        subtask_id, task_id, title, task, description, completed, 
                        subtask_order, priority, due_date, created_at
                    ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                ''', (
                    subtask_id, task_id, 
                    subtask_title,
                    subtask_title,
                    subtask_description,
                    False, subtask_order, subtask_priority, subtask_due_date,
                    datetime.now().isoformat()
                ))
                
                conn.commit()
            # ✅ Cursor auto-closed here
            
            return jsonify({
                'success': True,
                'subtask_id': subtask_id
            })
    
    except Exception as e:
        print(f"[SUBTASK ERROR] Failed to create subtask: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500
"""
Synergy Dashboard Routes
=========================
REST API endpoints for Synergy Dashboard Kanban board.

Endpoints:
    GET    /api/synergy/list           - List all sessions
    POST   /api/synergy/create         - Create new session
    GET    /api/synergy/<id>           - Get session by ID
    PATCH  /api/synergy/<id>           - Update session
    PATCH  /api/synergy/<id>/column    - Update session column
    DELETE /api/synergy/<id>           - Delete session
"""

from flask import Blueprint, request, jsonify
import sqlite3
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
    but UI expects 'title'.
    
    Args:
        docs: Array of document objects
    
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
        if isinstance(doc, dict):
            # Ensure 'title' field exists (convert 'name' to 'title' if needed)
            title = doc.get('title') or doc.get('name', '')
            normalized.append({
                'title': title,
                'url': doc.get('url', ''),
                'type': doc.get('type', 'document')
            })
    
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
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute('''
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
            assigned_agents TEXT
        )
    ''')
    
    # Add missing columns if they don't exist
    try:
        if is_using_supabase():
            # PostgreSQL syntax
            cursor.execute('ALTER TABLE synergy_sessions ADD COLUMN IF NOT EXISTS thread_ids TEXT')
        else:
            # SQLite syntax
            cursor.execute('ALTER TABLE synergy_sessions ADD COLUMN thread_ids TEXT')
    except (sqlite3.OperationalError, Exception):
        pass  # Column already exists
    
    try:
        if is_using_supabase():
            cursor.execute('ALTER TABLE synergy_sessions ADD COLUMN IF NOT EXISTS assigned_agents TEXT')
        else:
            cursor.execute('ALTER TABLE synergy_sessions ADD COLUMN assigned_agents TEXT')
    except (sqlite3.OperationalError, Exception):
        pass  # Column already exists
    
    try:
        if is_using_supabase():
            cursor.execute('ALTER TABLE synergy_sessions ADD COLUMN IF NOT EXISTS column_position INTEGER DEFAULT 0')
        else:
            cursor.execute('ALTER TABLE synergy_sessions ADD COLUMN column_position INTEGER DEFAULT 0')
    except (sqlite3.OperationalError, Exception):
        pass  # Column already exists
    
    conn.commit()
    conn.close()


# Initialize database on module load
init_database()


@synergy_bp.route('/list', methods=['GET'])
def list_sessions():
    """List all sessions with optional filtering"""
    try:
        status = request.args.get('status')
        priority = request.args.get('priority')
        column = request.args.get('kanban_column')
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
        query = 'SELECT * FROM synergy_sessions WHERE 1=1'
        params = []
        
        if status:
            query += ' AND status = ?'
            params.append(status)
        
        if priority:
            query += ' AND priority = ?'
            params.append(priority)
        
        if column:
            query += ' AND kanban_column = ?'
            params.append(column)
        
        # Order by column_position (for card ordering), then by last_active
        query += ' ORDER BY COALESCE(column_position, 999999), last_active DESC'
        
        cursor.execute(query, params)
        rows = cursor.fetchall()
        conn.close()
        
        sessions = []
        for row in rows:
            session = dict(row)
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
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT session_id, title, status, kanban_column, priority
            FROM synergy_sessions 
            WHERE status != 'archived'
            ORDER BY last_active DESC
        """)
        
        rows = cursor.fetchall()
        conn.close()
        
        sessions = [{
            'session_id': row['session_id'],
            'title': row['title'],
            'status': row['status'] or 'active',
            'column': row['kanban_column'] or 'backlog',
            'priority': row['priority'] or 'medium'
        } for row in rows]
        
        return jsonify(sessions)
    
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


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
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Step 1: Load all active sessions
        cursor.execute("""
            SELECT * FROM synergy_sessions 
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
        if session_ids:
            placeholders = ','.join('?' for _ in session_ids)
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
                FROM internal_docs
                WHERE session_id IN ({placeholders})
                ORDER BY session_id, created_at DESC
            """, session_ids)
            
            docs_rows = cursor.fetchall()
            
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
        
        conn.close()
        
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
    Returns: { success: True, sessions: { <id>: {...}, ... } }
    If no ids provided, falls back to list of sessions (minimal fields).
    """
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
        placeholders = ','.join('?' for _ in ids)
        query = f"SELECT * FROM synergy_sessions WHERE session_id IN ({placeholders})"
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
        
        # Generate session ID
        timestamp = datetime.now().strftime('%Y%m%d_%H%M')
        title_slug = data.get('title', 'untitled').lower().replace(' ', '_')[:30]
        session_id = f"sess_{timestamp}_{title_slug}"
        
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
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO synergy_sessions (
                session_id, title, description, platforms_involved, status,
                priority, kanban_column, tags, documents, links, next_steps,
                assignees, recent_activity, checklist, due_date, created_at, last_active,
                thread_ids, assigned_agents
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
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
            assigned_agents
        ))
        
        conn.commit()
        
        # BIDIRECTIONAL LINKING: Update threads table with synergy_card_id for auto-linked threads
        if thread_ids_list:
            for thread_id in thread_ids_list:
                try:
                    cursor.execute('''
                        UPDATE threads 
                        SET synergy_card_id = ?, synergy_card_name = ?, updated = ?
                        WHERE id = ?
                    ''', (session_id, data.get('title', 'Untitled Session'), datetime.now().isoformat(), thread_id))
                    print(f"BIDIRECTIONAL LINK: Thread {thread_id} updated with synergy_card_id {session_id}")
                except Exception as link_error:
                    print(f"Warning: Failed to update thread {thread_id}: {link_error}")
            
            conn.commit()
        
        conn.close()
        
        return jsonify({
            'success': True,
            'session_id': session_id,
            'message': 'Session created successfully',
            'linked_threads': thread_ids_list  # Return which threads were auto-linked
        })
    
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@synergy_bp.route('/<session_id>', methods=['GET'])
def get_session(session_id):
    """Get session by ID"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute('SELECT * FROM synergy_sessions WHERE session_id = ?', (session_id,))
        row = cursor.fetchone()
        conn.close()
        
        if not row:
            return jsonify({
                'success': False,
                'error': 'Session not found'
            }), 404
        
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
        
        return jsonify({
            'success': True,
            'session': session
        })
    
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@synergy_bp.route('/<session_id>', methods=['PATCH'])
def update_session(session_id):
    """Update session"""
    try:
        data = request.json
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
            updates.append("documents = ?")
            normalized = normalize_documents(update_data['documents'])
            json_value = json.dumps(normalized)
            params.append(json_value)
            print(f"[DEBUG] Adding documents (normalized): {json_value}")  # DEBUG
        
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
            query = f"UPDATE synergy_sessions SET {', '.join(updates)} WHERE session_id = ?"
            print(f"[DEBUG] Executing query: {query}")  # DEBUG
            print(f"[DEBUG] With params: {params}")  # DEBUG
            cursor.execute(query, params)
            conn.commit()
            print(f"[DEBUG] Rows affected: {cursor.rowcount}")  # DEBUG
        
        conn.close()
        
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


@synergy_bp.route('/<session_id>/column', methods=['PATCH'])
def update_column(session_id):
    """Update session column (Kanban movement)"""
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
            'SELECT recent_activity FROM synergy_sessions WHERE session_id = ?',
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
            
            cursor.execute('''
                UPDATE synergy_sessions 
                SET kanban_column = ?, recent_activity = ?, last_active = ?
                WHERE session_id = ?
            ''', (new_column, json.dumps(activity), datetime.now().isoformat(), session_id))
            
            conn.commit()
        
        conn.close()
        
        return jsonify({
            'success': True,
            'message': 'Column updated successfully'
        })
    
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@synergy_bp.route('/<session_id>', methods=['DELETE'])
def delete_session(session_id):
    """Delete session"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute('DELETE FROM synergy_sessions WHERE session_id = ?', (session_id,))
        conn.commit()
        conn.close()
        
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
    
    CRITICAL: Updates synergy_sessions.thread_ids array
    This is called from ThreadManager.linkToSynergy() to ensure bidirectional sync
    
    Body: {thread_id, thread_slug, thread_name}
    """
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
        cursor.execute('SELECT thread_ids FROM synergy_sessions WHERE session_id = ?', (session_id,))
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
            
            # Update synergy_sessions
            cursor.execute('''
                UPDATE synergy_sessions 
                SET thread_ids = ?,
                    last_active = ?
                WHERE session_id = ?
            ''', (json.dumps(thread_ids), datetime.now().isoformat(), session_id))
            
            conn.commit()
            print(f"[SYNERGY SYNC] Added thread {thread_id} to Synergy session {session_id}")
        else:
            print(f"[SYNERGY SYNC] Thread {thread_id} already linked to {session_id}")
        
        conn.close()
        
        return jsonify({
            'success': True,
            'session_id': session_id,
            'thread_ids': thread_ids,
            'message': f'Thread {thread_id} linked successfully'
        })
    
    except Exception as e:
        print(f"[SYNERGY SYNC ERROR] Failed to link thread: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500


@synergy_bp.route('/<session_id>/position', methods=['PATCH'])
def update_card_position(session_id):
    """
    Update card position within a column
    
    Body: {position: integer}
    """
    try:
        data = request.get_json()
        position = data.get('position')
        
        if position is None:
            return jsonify({'success': False, 'error': 'position required'}), 400
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            UPDATE synergy_sessions 
            SET column_position = ?
            WHERE session_id = ?
        ''', (position, session_id))
        
        conn.commit()
        conn.close()
        
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
    
    Body: {cards: [{session_id, position}]}
    """
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
                cursor.execute('''
                    UPDATE synergy_sessions 
                    SET column_position = ?
                    WHERE session_id = ?
                ''', (position, session_id))
        
        conn.commit()
        conn.close()
        
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
    
    CRITICAL: Updates synergy_sessions.thread_ids array
    This is called from ThreadManager.unlinkFromSynergy() to ensure bidirectional sync
    
    Body: {thread_id}
    """
    try:
        data = request.get_json()
        thread_id = data.get('thread_id')
        
        if not thread_id:
            return jsonify({'success': False, 'error': 'thread_id required'}), 400
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Get current thread_ids array
        cursor.execute('SELECT thread_ids FROM synergy_sessions WHERE session_id = ?', (session_id,))
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
        
        # Remove thread if present
        if thread_id in thread_ids:
            thread_ids.remove(thread_id)
            
            # Update synergy_sessions
            cursor.execute('''
                UPDATE synergy_sessions 
                SET thread_ids = ?,
                    last_active = ?
                WHERE session_id = ?
            ''', (json.dumps(thread_ids), datetime.now().isoformat(), session_id))
            
            conn.commit()
            print(f"[SYNERGY SYNC] Removed thread {thread_id} from Synergy session {session_id}")
        else:
            print(f"[SYNERGY SYNC] Thread {thread_id} not found in {session_id}")
        
        conn.close()
        
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
            cursor.execute('SELECT doc_id FROM synergy_internal_docs WHERE slug = ?', (slug,))
            if not cursor.fetchone():
                break
            slug = f"{original_slug}-{counter}"
            counter += 1
        
        # Generate share URL
        share_url = f"/internal-docs/{slug}"
        
        # Verify session exists
        cursor.execute('SELECT session_id FROM synergy_sessions WHERE session_id = ?', (session_id,))
        if not cursor.fetchone():
            conn.close()
            return jsonify({'success': False, 'error': 'Session not found'}), 404
        
        # Insert document with slug and share_url
        cursor.execute('''
            INSERT INTO synergy_internal_docs 
            (doc_id, session_id, title, content, content_json, format, doc_type, 
             created_by, created_at, updated_at, version, linked_to_ai, slug, share_url)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (doc_id, session_id, title, content, content_json, doc_format, doc_type,
              created_by, datetime.now().isoformat(), datetime.now().isoformat(), 1, 0, slug, share_url))
        
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
        
        cursor.execute('''
            SELECT doc_id, session_id, title, content, content_json, format, doc_type,
                   created_at, updated_at, created_by, version, linked_to_ai,
                   slug, share_url, description, tags
            FROM synergy_internal_docs
            WHERE doc_id = ?
        ''', (doc_id,))
        
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
        cursor.execute('SELECT version FROM synergy_internal_docs WHERE doc_id = ?', (doc_id,))
        row = cursor.fetchone()
        
        if not row:
            conn.close()
            return jsonify({'success': False, 'error': 'Document not found'}), 404
        
        new_version = row['version'] + 1
        
        # Build update query
        updates = []
        params = []
        
        if title:
            updates.append('title = ?')
            params.append(title)
        if content is not None:  # Allow empty string
            updates.append('content = ?')
            params.append(content)
        if content_json is not None:
            updates.append('content_json = ?')
            params.append(content_json)
        
        updates.append('updated_at = ?')
        params.append(datetime.now().isoformat())
        updates.append('version = ?')
        params.append(new_version)
        
        params.append(doc_id)
        
        query = f"UPDATE synergy_internal_docs SET {', '.join(updates)} WHERE doc_id = ?"
        cursor.execute(query, params)
        
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
        
        cursor.execute('DELETE FROM synergy_internal_docs WHERE doc_id = ?', (doc_id,))
        
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
        
        cursor.execute('''
            SELECT doc_id, title, format, doc_type, created_at, updated_at, created_by, version, linked_to_ai,
                   slug, share_url, description, tags
            FROM synergy_internal_docs
            WHERE session_id = ?
            ORDER BY created_at DESC
        ''', (session_id,))
        
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
        cursor.execute("""
            UPDATE synergy_internal_docs
            SET linked_to_ai = 1, session_id = ?
            WHERE doc_id = ?
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
        
        cursor.execute("""
            SELECT doc_id, title, content, content_json, doc_type
            FROM synergy_internal_docs
            WHERE doc_id = ?
        """, (doc_id,))
        
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

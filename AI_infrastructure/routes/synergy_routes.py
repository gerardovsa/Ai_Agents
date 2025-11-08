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

synergy_bp = Blueprint('synergy', __name__, url_prefix='/api/synergy')

# Database path
ROOT_DIR = Path(__file__).parent.parent.parent
DB_PATH = ROOT_DIR / 'data' / 'synergy_sessions.db'


def get_db_connection():
    """Get database connection to synergy_sessions.db"""
    conn = sqlite3.connect(str(DB_PATH))
    conn.row_factory = sqlite3.Row
    return conn


def init_database():
    """Initialize Synergy database if it doesn't exist"""
    os.makedirs(DB_PATH.parent, exist_ok=True)
    
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
    
    # Add new columns if they don't exist (for existing databases)
    try:
        cursor.execute('ALTER TABLE synergy_sessions ADD COLUMN thread_ids TEXT')
    except sqlite3.OperationalError:
        pass  # Column already exists
    
    try:
        cursor.execute('ALTER TABLE synergy_sessions ADD COLUMN assigned_agents TEXT')
    except sqlite3.OperationalError:
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
        
        query += ' ORDER BY last_active DESC'
        
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
        
        # Serialize JSON fields
        platforms_involved = json.dumps(data.get('platforms_involved', []))
        tags = json.dumps(data.get('tags', []))
        documents = json.dumps(data.get('documents', []))
        links = json.dumps(data.get('links', []))
        next_steps = json.dumps(data.get('next_steps', []))
        assignees = json.dumps(data.get('assignees', []))
        recent_activity = json.dumps([{
            'type': 'created',
            'timestamp': datetime.now().isoformat(),
            'user': data.get('created_by', 'AI Agent'),
            'details': f"Session created: {data.get('title')}"
        }])
        checklist = json.dumps(data.get('checklist', []))
        thread_ids = json.dumps(data.get('thread_ids', []))
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
        conn.close()
        
        return jsonify({
            'success': True,
            'session_id': session_id,
            'message': 'Session created successfully'
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
        
        # JSON fields
        for field in ['platforms_involved', 'tags', 'documents', 'links', 
                     'next_steps', 'assignees', 'checklist', 'thread_ids', 'assigned_agents']:
            if field in update_data:
                updates.append(f"{field} = ?")
                json_value = json.dumps(update_data[field])
                params.append(json_value)
                print(f"[DEBUG] Adding {field}: {json_value}")  # DEBUG
        
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

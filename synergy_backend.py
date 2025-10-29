"""
Synergy Dashboard Backend Server
==================================
REST API + WebSocket Server for real-time collaboration

Features:
- REST API for CRUD operations on sessions
- WebSocket for real-time updates across clients
- Google Tasks/Calendar sync integration (via service account)
- Microsoft To Do sync integration
- Universal task sync across platforms
- SQLite database for persistence
- CORS enabled for frontend access

Usage:
    python synergy_backend.py

Endpoints:
    GET    /api/sessions/list           - List all sessions
    POST   /api/sessions/create         - Create new session
    GET    /api/sessions/:id            - Get session by ID
    PATCH  /api/sessions/:id            - Update session
    PATCH  /api/sessions/:id/column     - Update session column
    DELETE /api/sessions/:id            - Delete session
    
    POST   /api/sync/google-tasks/create     - Sync to Google Tasks
    POST   /api/sync/microsoft-todo/create   - Sync to Microsoft To Do
    POST   /api/sync/google-calendar/create  - Sync to Google Calendar
    POST   /api/sync/bidirectional/:id       - Sync to all platforms
    GET    /api/sync/status/:id              - Get sync status
    GET    /api/sync/list                    - List synced tasks
    
WebSocket:
    /ws/synergy - Real-time collaboration channel
"""

from flask import Flask, request, jsonify
from flask_cors import CORS
from flask_socketio import SocketIO, emit, join_room, leave_room
import sqlite3
import json
import os
import sys
from datetime import datetime
from typing import Dict, List, Optional
import logging

# Add parent directory to path to import google_workspace
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Import Google authentication helpers
try:
    from google_workspace.google_auth_helper import get_service_account_credentials
    from googleapiclient.discovery import build
    GOOGLE_SERVICES_AVAILABLE = True
    logger_init = logging.getLogger(__name__)
    logger_init.info("✅ Google Workspace authentication helpers loaded")
except ImportError as e:
    GOOGLE_SERVICES_AVAILABLE = False
    logger_init = logging.getLogger(__name__)
    logger_init.warning(f"⚠️ Google services unavailable: {e}")

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# ============================================
# FLASK APP INITIALIZATION
# ============================================

app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'synergy-dashboard-secret-key-2025')
CORS(app)  # Enable CORS for all routes

# Initialize SocketIO
socketio = SocketIO(
    app, 
    cors_allowed_origins="*",
    async_mode='threading',
    logger=True,
    engineio_logger=True
)

# Register sync routes blueprint
try:
    from routes.task_sync_routes import task_sync_bp
    app.register_blueprint(task_sync_bp)
    logger.info("✅ Task sync routes registered at /api/sync/*")
except ImportError as e:
    logger.warning(f"⚠️ Task sync routes not available: {e}")

# ============================================
# DATABASE SETUP
# ============================================

DATABASE_PATH = os.path.join(os.path.dirname(__file__), 'data', 'synergy_sessions.db')

def init_database():
    """Initialize SQLite database with sessions table"""
    os.makedirs(os.path.dirname(DATABASE_PATH), exist_ok=True)
    
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()
    
    # Create sessions table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS sessions (
            session_id TEXT PRIMARY KEY,
            title TEXT NOT NULL,
            description TEXT,
            project_name TEXT,
            priority TEXT DEFAULT 'medium',
            status TEXT DEFAULT 'active',
            kanban_column TEXT DEFAULT 'backlog',
            due_date TEXT,
            created_at TEXT NOT NULL,
            updated_at TEXT NOT NULL,
            assignees TEXT,
            tags TEXT,
            notes TEXT,
            documents TEXT,
            links TEXT,
            next_steps TEXT,
            checklist TEXT,
            google_task_id TEXT,
            google_calendar_event_id TEXT,
            session_data TEXT
        )
    ''')
    
    conn.commit()
    conn.close()
    logger.info(f"✅ Database initialized at {DATABASE_PATH}")

def get_db_connection():
    """Get database connection"""
    conn = sqlite3.connect(DATABASE_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def dict_from_row(row: sqlite3.Row) -> Dict:
    """Convert SQLite row to dictionary"""
    if row is None:
        return None
    
    data = dict(row)
    
    # Parse JSON fields
    json_fields = ['assignees', 'tags', 'documents', 'links', 'next_steps', 'checklist', 'session_data']
    for field in json_fields:
        if data.get(field):
            try:
                data[field] = json.loads(data[field])
            except json.JSONDecodeError:
                data[field] = []
        else:
            data[field] = [] if field != 'session_data' else {}
    
    return data

# ============================================
# REST API ENDPOINTS
# ============================================

@app.route('/api/sessions/list', methods=['GET'])
def list_sessions():
    """Get all sessions"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Get filter parameters
        column = request.args.get('column')
        priority = request.args.get('priority')
        status = request.args.get('status')
        
        query = 'SELECT * FROM sessions WHERE 1=1'
        params = []
        
        if column:
            query += ' AND kanban_column = ?'
            params.append(column)
        
        if priority:
            query += ' AND priority = ?'
            params.append(priority)
        
        if status:
            query += ' AND status = ?'
            params.append(status)
        
        query += ' ORDER BY created_at DESC'
        
        cursor.execute(query, params)
        rows = cursor.fetchall()
        conn.close()
        
        sessions = [dict_from_row(row) for row in rows]
        
        logger.info(f"📊 Listed {len(sessions)} sessions")
        return jsonify(sessions), 200
        
    except Exception as e:
        logger.error(f"❌ Error listing sessions: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/sessions/create', methods=['POST'])
def create_session():
    """Create new session"""
    try:
        data = request.json
        
        # Generate session ID
        timestamp = datetime.now().strftime('%Y%m%d_%H%M')
        user = data.get('user', 'system')
        title_slug = data['title'][:30].lower().replace(' ', '_')
        session_id = f"sess_{timestamp}_{user}_{title_slug}"
        
        now = datetime.now().isoformat()
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Prepare JSON fields
        assignees = json.dumps(data.get('assignees', []))
        tags = json.dumps(data.get('tags', []))
        documents = json.dumps(data.get('documents', []))
        links = json.dumps(data.get('links', []))
        next_steps = json.dumps(data.get('next_steps', []))
        checklist = json.dumps(data.get('checklist', []))
        session_data = json.dumps(data.get('session_data', {}))
        
        cursor.execute('''
            INSERT INTO sessions (
                session_id, title, description, project_name, priority, status,
                kanban_column, due_date, created_at, updated_at, assignees, tags,
                notes, documents, links, next_steps, checklist, session_data
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            session_id,
            data['title'],
            data.get('description', ''),
            data.get('project_name', ''),
            data.get('priority', 'medium'),
            data.get('status', 'active'),
            data.get('kanban_column', 'backlog'),
            data.get('due_date'),
            now,
            now,
            assignees,
            tags,
            data.get('notes', ''),
            documents,
            links,
            next_steps,
            checklist,
            session_data
        ))
        
        conn.commit()
        conn.close()
        
        # Get created session
        session = get_session_by_id(session_id)
        
        # Broadcast via WebSocket
        socketio.emit('card_created', {
            'sessionId': session_id,
            'session': session,
            'user': user
        }, namespace='/ws/synergy')
        
        logger.info(f"✅ Created session: {session_id}")
        return jsonify(session), 201
        
    except Exception as e:
        logger.error(f"❌ Error creating session: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/sessions/<session_id>', methods=['GET'])
def get_session(session_id):
    """Get session by ID"""
    try:
        session = get_session_by_id(session_id)
        
        if not session:
            return jsonify({'error': 'Session not found'}), 404
        
        logger.info(f"📖 Retrieved session: {session_id}")
        return jsonify(session), 200
        
    except Exception as e:
        logger.error(f"❌ Error getting session: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/sessions/<session_id>', methods=['PATCH'])
def update_session(session_id):
    """Update session fields"""
    try:
        data = request.json
        updates = data.get('updates', {})
        sync = data.get('sync', {})
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Build UPDATE query dynamically
        set_clauses = []
        params = []
        
        # Simple text fields
        text_fields = ['title', 'description', 'project_name', 'priority', 'status', 
                       'kanban_column', 'due_date', 'notes', 'google_task_id', 
                       'google_calendar_event_id']
        
        for field in text_fields:
            if field in updates:
                set_clauses.append(f"{field} = ?")
                params.append(updates[field])
        
        # JSON fields
        json_fields = ['assignees', 'tags', 'documents', 'links', 'next_steps', 'checklist', 'session_data']
        
        for field in json_fields:
            if field in updates:
                set_clauses.append(f"{field} = ?")
                params.append(json.dumps(updates[field]))
        
        # Always update updated_at
        set_clauses.append("updated_at = ?")
        params.append(datetime.now().isoformat())
        
        params.append(session_id)
        
        query = f"UPDATE sessions SET {', '.join(set_clauses)} WHERE session_id = ?"
        
        cursor.execute(query, params)
        conn.commit()
        conn.close()
        
        # Get updated session
        session = get_session_by_id(session_id)
        
        # Handle Google sync
        if sync.get('google_tasks'):
            logger.info(f"🔄 Google Tasks sync requested for {session_id}")
            try:
                task_id = sync_session_to_google_tasks(session)
                if task_id:
                    # Update session with Google Task ID
                    conn = get_db_connection()
                    cursor = conn.cursor()
                    cursor.execute(
                        'UPDATE sessions SET google_task_id = ? WHERE session_id = ?',
                        (task_id, session_id)
                    )
                    conn.commit()
                    conn.close()
                    session['google_task_id'] = task_id
                    logger.info(f"✅ Synced to Google Tasks: {task_id}")
            except Exception as e:
                logger.error(f"❌ Google Tasks sync failed: {e}")
        
        if sync.get('google_calendar'):
            logger.info(f"🔄 Google Calendar sync requested for {session_id}")
            try:
                event_id = sync_session_to_google_calendar(session)
                if event_id:
                    # Update session with Google Calendar event ID
                    conn = get_db_connection()
                    cursor = conn.cursor()
                    cursor.execute(
                        'UPDATE sessions SET google_calendar_event_id = ? WHERE session_id = ?',
                        (event_id, session_id)
                    )
                    conn.commit()
                    conn.close()
                    session['google_calendar_event_id'] = event_id
                    logger.info(f"✅ Synced to Google Calendar: {event_id}")
            except Exception as e:
                logger.error(f"❌ Google Calendar sync failed: {e}")
        
        # Broadcast via WebSocket
        socketio.emit('card_edited', {
            'sessionId': session_id,
            'updates': updates,
            'user': data.get('user', 'system')
        }, namespace='/ws/synergy')
        
        logger.info(f"✅ Updated session: {session_id}")
        return jsonify(session), 200
        
    except Exception as e:
        logger.error(f"❌ Error updating session: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/sessions/<session_id>/column', methods=['PATCH'])
def update_session_column(session_id):
    """Update session column (for drag & drop)"""
    try:
        data = request.json
        new_column = data['column']
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Get old column
        cursor.execute('SELECT kanban_column FROM sessions WHERE session_id = ?', (session_id,))
        row = cursor.fetchone()
        old_column = row['kanban_column'] if row else None
        
        # Update column
        cursor.execute('''
            UPDATE sessions 
            SET kanban_column = ?, updated_at = ?
            WHERE session_id = ?
        ''', (new_column, datetime.now().isoformat(), session_id))
        
        conn.commit()
        conn.close()
        
        # Broadcast via WebSocket
        socketio.emit('card_moved', {
            'sessionId': session_id,
            'newColumn': new_column,
            'oldColumn': old_column,
            'user': data.get('user', 'system')
        }, namespace='/ws/synergy')
        
        logger.info(f"✅ Moved session {session_id}: {old_column} → {new_column}")
        return jsonify({
            'success': True,
            'sessionId': session_id,
            'newColumn': new_column,
            'oldColumn': old_column
        }), 200
        
    except Exception as e:
        logger.error(f"❌ Error updating column: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/sessions/<session_id>', methods=['DELETE'])
def delete_session(session_id):
    """Delete session"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute('DELETE FROM sessions WHERE session_id = ?', (session_id,))
        conn.commit()
        conn.close()
        
        # Broadcast via WebSocket
        socketio.emit('card_deleted', {
            'sessionId': session_id,
            'user': request.args.get('user', 'system')
        }, namespace='/ws/synergy')
        
        logger.info(f"✅ Deleted session: {session_id}")
        return jsonify({'success': True}), 200
        
    except Exception as e:
        logger.error(f"❌ Error deleting session: {e}")
        return jsonify({'error': str(e)}), 500

def get_session_by_id(session_id: str) -> Optional[Dict]:
    """Helper function to get session by ID"""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM sessions WHERE session_id = ?', (session_id,))
    row = cursor.fetchone()
    conn.close()
    
    if row:
        return dict_from_row(row)
    return None

# ============================================
# WEBSOCKET HANDLERS
# ============================================

@socketio.on('connect', namespace='/ws/synergy')
def handle_connect():
    """Handle WebSocket connection"""
    logger.info(f"🔌 Client connected: {request.sid}")
    emit('connected', {
        'message': 'Connected to Synergy Dashboard',
        'timestamp': datetime.now().isoformat()
    })

@socketio.on('disconnect', namespace='/ws/synergy')
def handle_disconnect():
    """Handle WebSocket disconnection"""
    logger.info(f"🔌 Client disconnected: {request.sid}")

@socketio.on('subscribe', namespace='/ws/synergy')
def handle_subscribe(data):
    """Handle channel subscription"""
    channel = data.get('channel', 'synergy_board')
    join_room(channel)
    logger.info(f"✅ Client {request.sid} subscribed to {channel}")
    emit('subscribed', {'channel': channel})

@socketio.on('unsubscribe', namespace='/ws/synergy')
def handle_unsubscribe(data):
    """Handle channel unsubscription"""
    channel = data.get('channel', 'synergy_board')
    leave_room(channel)
    logger.info(f"✅ Client {request.sid} unsubscribed from {channel}")
    emit('unsubscribed', {'channel': channel})

@socketio.on('broadcast', namespace='/ws/synergy')
def handle_broadcast(data):
    """Handle broadcast message from client"""
    message_type = data.get('messageType')
    message_data = data.get('data')
    
    logger.info(f"📡 Broadcasting {message_type}: {message_data}")
    
    # Broadcast to all clients except sender
    emit(message_type, message_data, broadcast=True, include_self=False)

@socketio.on('ping', namespace='/ws/synergy')
def handle_ping():
    """Handle ping from client"""
    emit('pong', {'timestamp': datetime.now().isoformat()})

# ============================================
# HEALTH CHECK & INFO
# ============================================

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'service': 'Synergy Dashboard Backend',
        'timestamp': datetime.now().isoformat(),
        'database': 'connected' if os.path.exists(DATABASE_PATH) else 'not initialized'
    }), 200

@app.route('/api/info', methods=['GET'])
def api_info():
    """API information endpoint"""
    return jsonify({
        'name': 'Synergy Dashboard API',
        'version': '1.0.0',
        'endpoints': {
            'sessions': {
                'list': 'GET /api/sessions/list',
                'create': 'POST /api/sessions/create',
                'get': 'GET /api/sessions/:id',
                'update': 'PATCH /api/sessions/:id',
                'updateColumn': 'PATCH /api/sessions/:id/column',
                'delete': 'DELETE /api/sessions/:id'
            },
            'websocket': 'ws://localhost:4000/ws/synergy'
        }
    }), 200

# ============================================
# SEED DATA (Development)
# ============================================

def seed_database():
    """Seed database with sample data for development"""
    logger.info("🌱 Seeding database with sample data...")
    
    sample_sessions = [
        {
            'title': 'Email Marketing Campaign',
            'description': 'Design and launch Q4 email campaign',
            'project_name': 'Q4 Marketing',
            'priority': 'high',
            'status': 'active',
            'kanban_column': 'in_progress',
            'due_date': '2025-11-15',
            'assignees': ['John Doe', 'Sarah Smith'],
            'tags': ['marketing', 'email', 'Q4'],
            'user': 'john'
        },
        {
            'title': 'Update API Documentation',
            'description': 'Document new REST endpoints and WebSocket events',
            'project_name': 'Backend Development',
            'priority': 'medium',
            'status': 'active',
            'kanban_column': 'backlog',
            'due_date': '2025-11-30',
            'assignees': ['Mike Johnson'],
            'tags': ['documentation', 'api'],
            'user': 'mike'
        },
        {
            'title': 'Fix Login Bug',
            'description': 'Users cannot log in with Google OAuth',
            'project_name': 'Authentication',
            'priority': 'urgent',
            'status': 'active',
            'kanban_column': 'in_progress',
            'due_date': '2025-10-29',
            'assignees': ['Emily Chen'],
            'tags': ['bug', 'auth', 'urgent'],
            'user': 'emily'
        }
    ]
    
    for session_data in sample_sessions:
        try:
            # Use create_session endpoint logic
            response = create_session_internal(session_data)
            logger.info(f"✅ Seeded: {session_data['title']}")
        except Exception as e:
            logger.error(f"❌ Failed to seed session: {e}")

def create_session_internal(data: Dict) -> Dict:
    """Internal function to create session (used by seeding)"""
    timestamp = datetime.now().strftime('%Y%m%d_%H%M')
    user = data.get('user', 'system')
    title_slug = data['title'][:30].lower().replace(' ', '_')
    session_id = f"sess_{timestamp}_{user}_{title_slug}"
    
    now = datetime.now().isoformat()
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    assignees = json.dumps(data.get('assignees', []))
    tags = json.dumps(data.get('tags', []))
    documents = json.dumps(data.get('documents', []))
    links = json.dumps(data.get('links', []))
    next_steps = json.dumps(data.get('next_steps', []))
    checklist = json.dumps(data.get('checklist', []))
    session_data = json.dumps(data.get('session_data', {}))
    
    cursor.execute('''
        INSERT INTO sessions (
            session_id, title, description, project_name, priority, status,
            kanban_column, due_date, created_at, updated_at, assignees, tags,
            notes, documents, links, next_steps, checklist, session_data
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (
        session_id, data['title'], data.get('description', ''),
        data.get('project_name', ''), data.get('priority', 'medium'),
        data.get('status', 'active'), data.get('kanban_column', 'backlog'),
        data.get('due_date'), now, now, assignees, tags,
        data.get('notes', ''), documents, links, next_steps, checklist, session_data
    ))
    
    conn.commit()
    conn.close()
    
    return get_session_by_id(session_id)

# ============================================
# GOOGLE SERVICES SYNC FUNCTIONS
# ============================================

def sync_session_to_google_tasks(session: Dict) -> Optional[str]:
    """
    Sync session to Google Tasks using service account
    
    Args:
        session: Session dictionary with title, description, due_date, etc.
        
    Returns:
        Task ID if successful, None otherwise
    """
    if not GOOGLE_SERVICES_AVAILABLE:
        logger.warning("⚠️ Google services not available")
        return None
    
    try:
        # Get credentials with Tasks scope
        scopes = ['https://www.googleapis.com/auth/tasks']
        credentials = get_service_account_credentials(scopes)
        
        # Build Tasks service
        service = build('tasks', 'v1', credentials=credentials)
        
        # Prepare task data
        task_body = {
            'title': session.get('title', 'Untitled Task'),
        }
        
        # Add notes (description + additional info)
        notes_parts = []
        if session.get('description'):
            notes_parts.append(session['description'])
        if session.get('project_name'):
            notes_parts.append(f"\nProject: {session['project_name']}")
        if session.get('assignees'):
            assignees = session['assignees'] if isinstance(session['assignees'], list) else []
            if assignees:
                notes_parts.append(f"Assignees: {', '.join(assignees)}")
        if session.get('tags'):
            tags = session['tags'] if isinstance(session['tags'], list) else []
            if tags:
                notes_parts.append(f"Tags: {', '.join(tags)}")
        
        if notes_parts:
            task_body['notes'] = '\n'.join(notes_parts)
        
        # Add due date if available
        if session.get('due_date'):
            # Google Tasks expects RFC 3339 timestamp
            # If due_date is just a date, convert to datetime
            due_date = session['due_date']
            if 'T' not in due_date:
                due_date = f"{due_date}T00:00:00Z"
            task_body['due'] = due_date
        
        # Add status
        if session.get('status') == 'completed':
            task_body['status'] = 'completed'
        else:
            task_body['status'] = 'needsAction'
        
        # Check if task already exists (update vs create)
        if session.get('google_task_id'):
            # Update existing task
            result = service.tasks().update(
                tasklist='@default',
                task=session['google_task_id'],
                body=task_body
            ).execute()
            logger.info(f"✅ Updated Google Task: {result.get('id')}")
        else:
            # Create new task
            result = service.tasks().insert(
                tasklist='@default',
                body=task_body
            ).execute()
            logger.info(f"✅ Created Google Task: {result.get('id')}")
        
        return result.get('id')
        
    except Exception as e:
        logger.error(f"❌ Google Tasks sync failed: {e}")
        return None


def sync_session_to_google_calendar(session: Dict) -> Optional[str]:
    """
    Sync session to Google Calendar using service account
    
    Args:
        session: Session dictionary with title, description, due_date, etc.
        
    Returns:
        Event ID if successful, None otherwise
    """
    if not GOOGLE_SERVICES_AVAILABLE:
        logger.warning("⚠️ Google services not available")
        return None
    
    try:
        # Get credentials with Calendar scope
        scopes = ['https://www.googleapis.com/auth/calendar']
        credentials = get_service_account_credentials(scopes)
        
        # Build Calendar service
        service = build('calendar', 'v3', credentials=credentials)
        
        # Prepare event data
        event_body = {
            'summary': session.get('title', 'Untitled Event'),
        }
        
        # Add description
        description_parts = []
        if session.get('description'):
            description_parts.append(session['description'])
        if session.get('project_name'):
            description_parts.append(f"\nProject: {session['project_name']}")
        if session.get('priority'):
            description_parts.append(f"Priority: {session['priority']}")
        if session.get('assignees'):
            assignees = session['assignees'] if isinstance(session['assignees'], list) else []
            if assignees:
                description_parts.append(f"Assignees: {', '.join(assignees)}")
        if session.get('session_id'):
            description_parts.append(f"\nSession ID: {session['session_id']}")
        
        if description_parts:
            event_body['description'] = '\n'.join(description_parts)
        
        # Add start and end times
        if session.get('due_date'):
            due_date = session['due_date']
            # If it's just a date, make it an all-day event
            if 'T' not in due_date:
                event_body['start'] = {'date': due_date}
                event_body['end'] = {'date': due_date}
            else:
                # If it's a datetime, use dateTime with timezone
                event_body['start'] = {
                    'dateTime': due_date,
                    'timeZone': 'UTC'
                }
                # Set end time to 1 hour later
                from datetime import datetime as dt, timedelta
                start_dt = dt.fromisoformat(due_date.replace('Z', '+00:00'))
                end_dt = start_dt + timedelta(hours=1)
                event_body['end'] = {
                    'dateTime': end_dt.isoformat(),
                    'timeZone': 'UTC'
                }
        else:
            # No due date, create event for today
            today = datetime.now().date().isoformat()
            event_body['start'] = {'date': today}
            event_body['end'] = {'date': today}
        
        # Add color based on priority
        priority_colors = {
            'urgent': '11',  # Red
            'high': '11',    # Red
            'medium': '5',   # Yellow
            'low': '2'       # Green
        }
        if session.get('priority') in priority_colors:
            event_body['colorId'] = priority_colors[session['priority']]
        
        # Check if event already exists (update vs create)
        if session.get('google_calendar_event_id'):
            # Update existing event
            result = service.events().update(
                calendarId='primary',
                eventId=session['google_calendar_event_id'],
                body=event_body
            ).execute()
            logger.info(f"✅ Updated Google Calendar event: {result.get('id')}")
        else:
            # Create new event
            result = service.events().insert(
                calendarId='primary',
                body=event_body
            ).execute()
            logger.info(f"✅ Created Google Calendar event: {result.get('id')}")
        
        return result.get('id')
        
    except Exception as e:
        logger.error(f"❌ Google Calendar sync failed: {e}")
        return None

# ============================================
# MAIN
# ============================================

if __name__ == '__main__':
    logger.info("🚀 Starting Synergy Dashboard Backend Server...")
    
    # Initialize database
    init_database()
    
    # Check if database is empty and seed if needed
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT COUNT(*) as count FROM sessions')
    count = cursor.fetchone()['count']
    conn.close()
    
    if count == 0:
        logger.info("📊 Database is empty, seeding with sample data...")
        seed_database()
    else:
        logger.info(f"📊 Database has {count} sessions")
    
    # Start server
    logger.info("✅ Server starting on http://localhost:5001")
    logger.info("✅ WebSocket available at ws://localhost:5001/ws/synergy")
    logger.info("✅ API docs at http://localhost:5001/api/info")
    
    socketio.run(
        app, 
        host='0.0.0.0', 
        port=5001, 
        debug=True,
        use_reloader=False  # Disable reloader to prevent double initialization
    )

"""
Universal Task Sync Routes
===========================
RESTful API for bidirectional sync between Kanban board and:
- Google Tasks
- Microsoft To Do  
- Google Calendar (for reminders/recurrence)

Last Updated: December 7, 2025
Cursor Management: FIXED - All database operations use proper resource cleanup

Features:
- Create/update/delete sync across platforms
- Field mapping with platform-specific handling
- Conflict resolution
- Sync status tracking
"""

from flask import Blueprint, request, jsonify
import json
import sys
import os
from datetime import datetime
from pathlib import Path

# Import universal mapper from scripts/utilities/
ai_agents_root = Path(__file__).parent.parent.parent  # Go up to AI_agents root
sys.path.insert(0, str(ai_agents_root))
sys.path.insert(0, str(ai_agents_root / 'scripts' / 'utilities'))
from task_sync_universal import UniversalTaskMapper

# Import tool registry for Google/Microsoft API calls
from tools.registry import ToolRegistry

# Import database utilities - PostgreSQL only
from shared.database_utils import convert_sql_placeholders, get_database_connection

# Initialize
task_sync_bp = Blueprint('task_sync', __name__, url_prefix='/api/sync')
tool_registry = ToolRegistry()
mapper = UniversalTaskMapper()

def get_db_connection():
    """Get Supabase PostgreSQL connection for synergy_sessions schema"""
    return get_database_connection('synergy_sessions')

def dict_from_row(row):
    """Convert SQLite row to dict"""
    if row is None:
        return None
    return dict(row)

# ============================================
# SYNC TO GOOGLE TASKS
# ============================================

@task_sync_bp.route('/google-tasks/create', methods=['POST'])
def sync_to_google_tasks():
    """
    Create Google Task from Kanban card
    
    Request Body:
    {
        "session_id": "20251028_1400_task123",
        "user_email": "user@example.com"
    }
    
    Response:
    {
        "success": true,
        "google_task_id": "task_abc123",
        "google_task": {...},
        "calendar_event_id": "event_xyz789" (if reminder/recurrence)
    }
    
    ✅ FIXED: Proper cursor/connection management with finally block
    """
    cursor = None  # ✅ Initialize before try
    conn = None
    try:
        data = request.json
        session_id = data.get('session_id')
        user_email = data.get('user_email', 'default')
        
        # Get Kanban card
        conn = get_db_connection()
        cursor = conn.cursor()
        sql, params = convert_sql_placeholders('SELECT * FROM sessions WHERE session_id = ?', (session_id,))
        cursor.execute(sql, params)
        row = cursor.fetchone()
        
        if not row:
            # ✅ Close before early return
            cursor.close()
            cursor = None
            conn.close()
            conn = None
            return jsonify({'error': 'Session not found'}), 404
        
        kanban_card = dict_from_row(row)
        
        # Convert to Google Tasks format
        google_task = mapper.kanban_to_google_task(kanban_card)
        
        # Create task via Google Tasks API
        tool_schema = tool_registry.get_tool_schema('google_tasks_create_task')
        if not tool_schema:
            # ✅ Close before early return
            cursor.close()
            cursor = None
            conn.close()
            conn = None
            return jsonify({'error': 'Google Tasks tool not available'}), 500
        
        # Execute tool via registry
        result = tool_registry.execute_tool(
            tool_name='google_tasks_create_task',
            title=google_task['title'],
            notes=google_task.get('notes', ''),
            due=google_task.get('due'),
            list_id=kanban_card.get('google_task_list_id', '@default')
        )
        
        if not result.get('success'):
            # ✅ Close before early return
            cursor.close()
            cursor = None
            conn.close()
            conn = None
            return jsonify({'error': f'Failed to create Google Task: {result.get("error")}'}), 500
        
        task_data = result.get('task', {})
        google_task_id = task_data.get('id')
        
        # Store sync metadata
        sql, params = convert_sql_placeholders('''
            INSERT INTO task_sync_metadata 
            (session_id, platform, platform_task_id, sync_status, last_synced_at)
            VALUES (?, 'google_tasks', ?, 'synced', ?)
        ''', (session_id, google_task_id, datetime.now().isoformat()))
        cursor.execute(sql, params)
        
        # Update session with google_task_id
        sql, params = convert_sql_placeholders('''
            UPDATE sessions SET google_task_id = ?, updated_at = ? WHERE session_id = ?
        ''', (google_task_id, datetime.now().isoformat(), session_id))
        cursor.execute(sql, params)
        
        # Handle reminder/recurrence via Google Calendar
        calendar_event_id = None
        has_reminder = kanban_card.get('reminder_date') or kanban_card.get('reminder_minutes_before')
        has_recurrence = kanban_card.get('recurrence_type') and kanban_card.get('recurrence_type') != 'none'
        
        if has_reminder or has_recurrence:
            calendar_result = _create_google_calendar_event(kanban_card, user_email, cursor)
            if calendar_result.get('success'):
                calendar_event_id = calendar_result.get('event_id')
        
        conn.commit()
        
        # ✅ Close cursor BEFORE processing result
        cursor.close()
        cursor = None
        conn.close()
        conn = None
        
        return jsonify({
            'success': True,
            'google_task_id': google_task_id,
            'google_task': task_data,
            'calendar_event_id': calendar_event_id,
            'message': 'Task synced to Google Tasks' + (' with Calendar event' if calendar_event_id else '')
        }), 201
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    finally:
        # ✅ GUARANTEED cleanup
        if cursor:
            try:
                cursor.close()
            except:
                pass
        if conn:
            try:
                conn.close()
            except:
                pass


# ============================================
# SYNC TO MICROSOFT TO DO
# ============================================

@task_sync_bp.route('/microsoft-todo/create', methods=['POST'])
def sync_to_microsoft_todo():
    """
    Create Microsoft To Do task from Kanban card
    
    Request Body:
    {
        "session_id": "20251028_1400_task123",
        "user_email": "user@example.com"
    }
    
    Response:
    {
        "success": true,
        "microsoft_todo_id": "task_abc123",
        "microsoft_task": {...}
    }
    
    ✅ FIXED: Proper cursor/connection management with finally block
    """
    cursor = None  # ✅ Initialize before try
    conn = None
    try:
        data = request.json
        session_id = data.get('session_id')
        user_email = data.get('user_email', 'default')
        
        # Get Kanban card
        conn = get_db_connection()
        cursor = conn.cursor()
        sql, params = convert_sql_placeholders('SELECT * FROM sessions WHERE session_id = ?', (session_id,))
        cursor.execute(sql, params)
        row = cursor.fetchone()
        
        if not row:
            # ✅ Close before early return
            cursor.close()
            cursor = None
            conn.close()
            conn = None
            return jsonify({'error': 'Session not found'}), 404
        
        kanban_card = dict_from_row(row)
        
        # Convert to Microsoft To Do format
        ms_task = mapper.kanban_to_microsoft_todo(kanban_card)
        
        # Create task via Microsoft To Do API
        tool_schema = tool_registry.get_tool_schema('todo_create_task')
        if not tool_schema:
            # ✅ Close before early return
            cursor.close()
            cursor = None
            conn.close()
            conn = None
            return jsonify({'error': 'Microsoft To Do tool not available'}), 500
        
        # Build parameters
        params = {
            'title': ms_task['title'],
            'body': ms_task.get('body', {}).get('content', ''),
            'importance': ms_task.get('importance', 'normal'),
            'status': ms_task.get('status', 'notStarted')
        }
        
        if ms_task.get('dueDateTime'):
            params['due_date'] = ms_task['dueDateTime']['dateTime']
        
        if ms_task.get('reminderDateTime'):
            params['reminder'] = ms_task['reminderDateTime']['dateTime']
        
        if ms_task.get('categories'):
            params['categories'] = ms_task['categories']
        
        result = tool_registry.execute_tool(tool_name='todo_create_task', **params)
        
        if not result.get('success'):
            # ✅ Close before early return
            cursor.close()
            cursor = None
            conn.close()
            conn = None
            return jsonify({'error': f'Failed to create Microsoft To Do task: {result.get("error")}'}), 500
        
        task_data = result.get('task', {})
        ms_todo_id = task_data.get('id')
        
        # Store sync metadata
        sql_insert, params_insert = convert_sql_placeholders('''
            INSERT INTO task_sync_metadata 
            (session_id, platform, platform_task_id, sync_status, last_synced_at)
            VALUES (?, 'microsoft_todo', ?, 'synced', ?)
        ''', (session_id, ms_todo_id, datetime.now().isoformat()))
        cursor.execute(sql_insert, params_insert)
        
        # Update session with microsoft_todo_id
        sql_update, params_update = convert_sql_placeholders('''
            UPDATE sessions SET microsoft_todo_id = ?, updated_at = ? WHERE session_id = ?
        ''', (ms_todo_id, datetime.now().isoformat(), session_id))
        cursor.execute(sql_update, params_update)
        
        conn.commit()
        
        # ✅ Close cursor BEFORE processing result
        cursor.close()
        cursor = None
        conn.close()
        conn = None
        
        return jsonify({
            'success': True,
            'microsoft_todo_id': ms_todo_id,
            'microsoft_task': task_data,
            'message': 'Task synced to Microsoft To Do'
        }), 201
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    finally:
        # ✅ GUARANTEED cleanup
        if cursor:
            try:
                cursor.close()
            except:
                pass
        if conn:
            try:
                conn.close()
            except:
                pass


# ============================================
# SYNC TO GOOGLE CALENDAR (for reminders/recurrence)
# ============================================

@task_sync_bp.route('/google-calendar/create', methods=['POST'])
def sync_to_google_calendar():
    """
    Create Google Calendar event for Kanban task with reminders/recurrence
    
    Request Body:
    {
        "session_id": "20251028_1400_task123",
        "user_email": "user@example.com"
    }
    
    Response:
    {
        "success": true,
        "event_id": "event_xyz789",
        "event": {...}
    }
    
    ✅ FIXED: Proper cursor/connection management with finally block
    """
    cursor = None  # ✅ Initialize before try
    conn = None
    try:
        data = request.json
        session_id = data.get('session_id')
        user_email = data.get('user_email', 'default')
        
        # Get Kanban card
        conn = get_db_connection()
        cursor = conn.cursor()
        sql, params = convert_sql_placeholders('SELECT * FROM sessions WHERE session_id = ?', (session_id,))
        cursor.execute(sql, params)
        row = cursor.fetchone()
        
        if not row:
            # ✅ Close before early return
            cursor.close()
            cursor = None
            conn.close()
            conn = None
            return jsonify({'error': 'Session not found'}), 404
        
        kanban_card = dict_from_row(row)
        
        result = _create_google_calendar_event(kanban_card, user_email, cursor)
        
        if result.get('success'):
            conn.commit()
        
        # ✅ Close cursor BEFORE processing result
        cursor.close()
        cursor = None
        conn.close()
        conn = None
        
        if result.get('success'):
            return jsonify(result), 201
        else:
            return jsonify(result), 500
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    finally:
        # ✅ GUARANTEED cleanup
        if cursor:
            try:
                cursor.close()
            except:
                pass
        if conn:
            try:
                conn.close()
            except:
                pass


def _create_google_calendar_event(kanban_card, user_email, cursor):
    """
    Helper to create Google Calendar event
    
    ✅ FIXED: Cursor passed as parameter, managed by caller
    Note: This function receives cursor from parent, doesn't manage it
    """
    try:
        session_id = kanban_card['session_id']
        
        # Build event details
        summary = f"⏰ Reminder: {kanban_card['title']}"
        description = kanban_card.get('description', '')
        
        # Determine start time
        start_time = kanban_card.get('reminder_date') or kanban_card.get('due_date')
        if not start_time:
            return {'success': False, 'error': 'No reminder_date or due_date found'}
        
        # Reminders
        reminders = []
        if kanban_card.get('reminder_minutes_before'):
            reminders.append({
                'method': 'popup',
                'minutes': kanban_card['reminder_minutes_before']
            })
        
        # Recurrence
        recurrence = None
        if kanban_card.get('recurrence_rule'):
            recurrence = [kanban_card['recurrence_rule']]
        elif kanban_card.get('recurrence_type') and kanban_card['recurrence_type'] != 'none':
            # Convert recurrence_type to RRULE
            rec_type = kanban_card['recurrence_type'].upper()
            recurrence = [f"RRULE:FREQ={rec_type}"]
        
        # Create event via Google Calendar API
        tool_schema = tool_registry.get_tool_schema('google_calendar_create_event')
        if not tool_schema:
            return {'success': False, 'error': 'Google Calendar tool not available'}
        
        params = {
            'summary': summary,
            'description': description,
            'start': start_time,
            'end': start_time  # Same as start for reminder events
        }
        
        if reminders:
            params['reminders'] = reminders
        
        if recurrence:
            params['recurrence'] = recurrence
        
        if kanban_card.get('location'):
            params['location'] = kanban_card['location']
        
        result = tool_registry.execute_tool(tool_name='google_calendar_create_event', **params)
        
        if not result.get('success'):
            return {'success': False, 'error': f'Failed to create Calendar event: {result.get("error")}'}
        
        event_data = result.get('event', {})
        event_id = event_data.get('id')
        
        # Store sync metadata (using passed cursor)
        sql_insert, params_insert = convert_sql_placeholders('''
            INSERT INTO task_sync_metadata 
            (session_id, platform, platform_task_id, sync_status, last_synced_at)
            VALUES (?, 'google_calendar', ?, 'synced', ?)
        ''', (session_id, event_id, datetime.now().isoformat()))
        cursor.execute(sql_insert, params_insert)
        
        # Update session with google_calendar_event_id
        sql_update, params_update = convert_sql_placeholders('''
            UPDATE sessions SET google_calendar_event_id = ?, updated_at = ? WHERE session_id = ?
        ''', (event_id, datetime.now().isoformat(), session_id))
        cursor.execute(sql_update, params_update)
        
        return {
            'success': True,
            'event_id': event_id,
            'event': event_data,
            'message': 'Calendar event created for reminders/recurrence'
        }
        
    except Exception as e:
        return {'success': False, 'error': str(e)}


# ============================================
# BIDIRECTIONAL SYNC
# ============================================

@task_sync_bp.route('/bidirectional/<session_id>', methods=['POST'])
def bidirectional_sync(session_id):
    """
    Sync Kanban card to ALL platforms (Google Tasks, Microsoft To Do, Google Calendar)
    
    Request Body:
    {
        "user_email": "user@example.com",
        "platforms": ["google_tasks", "microsoft_todo", "google_calendar"] (optional)
    }
    
    Response:
    {
        "success": true,
        "synced_platforms": {
            "google_tasks": {"success": true, "task_id": "..."},
            "microsoft_todo": {"success": true, "task_id": "..."},
            "google_calendar": {"success": true, "event_id": "..."}
        }
    }
    
    ✅ FIXED: Proper cursor/connection management with finally block
    """
    cursor = None  # ✅ Initialize before try
    conn = None
    try:
        data = request.json or {}
        user_email = data.get('user_email', 'default')
        requested_platforms = data.get('platforms', ['google_tasks', 'microsoft_todo'])
        
        # Get Kanban card
        conn = get_db_connection()
        cursor = conn.cursor()
        sql, params = convert_sql_placeholders('SELECT * FROM sessions WHERE session_id = ?', (session_id,))
        cursor.execute(sql, params)
        row = cursor.fetchone()
        
        if not row:
            # ✅ Close before early return
            cursor.close()
            cursor = None
            conn.close()
            conn = None
            return jsonify({'error': 'Session not found'}), 404
        
        kanban_card = dict_from_row(row)
        
        results = {}
        
        # Sync to Google Tasks
        if 'google_tasks' in requested_platforms:
            try:
                google_result = _sync_to_google_tasks_internal(kanban_card, user_email, cursor)
                results['google_tasks'] = google_result
            except Exception as e:
                results['google_tasks'] = {'success': False, 'error': str(e)}
        
        # Sync to Microsoft To Do
        if 'microsoft_todo' in requested_platforms:
            try:
                ms_result = _sync_to_microsoft_todo_internal(kanban_card, user_email, cursor)
                results['microsoft_todo'] = ms_result
            except Exception as e:
                results['microsoft_todo'] = {'success': False, 'error': str(e)}
        
        # Sync to Google Calendar (if has reminders/recurrence)
        has_reminder = kanban_card.get('reminder_date') or kanban_card.get('reminder_minutes_before')
        has_recurrence = kanban_card.get('recurrence_type') and kanban_card.get('recurrence_type') != 'none'
        
        if (has_reminder or has_recurrence) and 'google_calendar' in requested_platforms:
            try:
                calendar_result = _create_google_calendar_event(kanban_card, user_email, cursor)
                results['google_calendar'] = calendar_result
            except Exception as e:
                results['google_calendar'] = {'success': False, 'error': str(e)}
        
        conn.commit()
        
        # ✅ Close cursor BEFORE processing result
        cursor.close()
        cursor = None
        conn.close()
        conn = None
        
        # Count successes
        success_count = sum(1 for r in results.values() if r.get('success'))
        
        return jsonify({
            'success': success_count > 0,
            'synced_platforms': results,
            'message': f'Synced to {success_count}/{len(results)} platforms'
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    finally:
        # ✅ GUARANTEED cleanup
        if cursor:
            try:
                cursor.close()
            except:
                pass
        if conn:
            try:
                conn.close()
            except:
                pass


def _sync_to_google_tasks_internal(kanban_card, user_email, cursor):
    """
    Internal helper for Google Tasks sync
    
    ✅ FIXED: Cursor passed as parameter, managed by caller
    Note: This function receives cursor from parent, doesn't manage it
    """
    google_task = mapper.kanban_to_google_task(kanban_card)
    
    tool_schema = tool_registry.get_tool_schema('google_tasks_create_task')
    if not tool_schema:
        return {'success': False, 'error': 'Google Tasks tool not available'}
    
    result = tool_registry.execute_tool(
        tool_name='google_tasks_create_task',
        title=google_task['title'],
        notes=google_task.get('notes', ''),
        due=google_task.get('due'),
        list_id=kanban_card.get('google_task_list_id', '@default')
    )
    
    if not result.get('success'):
        return {'success': False, 'error': f'Failed to create Google Task: {result.get("error")}'}
    
    task_data = result.get('task', {})
    google_task_id = task_data.get('id')
    
    sql_insert, params_insert = convert_sql_placeholders('''
        INSERT INTO task_sync_metadata 
        (session_id, platform, platform_task_id, sync_status, last_synced_at)
        VALUES (?, 'google_tasks', ?, 'synced', ?)
    ''', (kanban_card['session_id'], google_task_id, datetime.now().isoformat()))
    cursor.execute(sql_insert, params_insert)
    
    sql_update, params_update = convert_sql_placeholders('''
        UPDATE sessions SET google_task_id = ?, updated_at = ? WHERE session_id = ?
    ''', (google_task_id, datetime.now().isoformat(), kanban_card['session_id']))
    cursor.execute(sql_update, params_update)
    
    return {'success': True, 'task_id': google_task_id, 'task': task_data}


def _sync_to_microsoft_todo_internal(kanban_card, user_email, cursor):
    """
    Internal helper for Microsoft To Do sync
    
    ✅ FIXED: Cursor passed as parameter, managed by caller
    Note: This function receives cursor from parent, doesn't manage it
    """
    ms_task = mapper.kanban_to_microsoft_todo(kanban_card)
    
    tool_schema = tool_registry.get_tool_schema('todo_create_task')
    if not tool_schema:
        return {'success': False, 'error': 'Microsoft To Do tool not available'}
    
    params = {
        'title': ms_task['title'],
        'body': ms_task.get('body', {}).get('content', ''),
        'importance': ms_task.get('importance', 'normal'),
        'status': ms_task.get('status', 'notStarted')
    }
    
    if ms_task.get('dueDateTime'):
        params['due_date'] = ms_task['dueDateTime']['dateTime']
    
    if ms_task.get('reminderDateTime'):
        params['reminder'] = ms_task['reminderDateTime']['dateTime']
    
    if ms_task.get('categories'):
        params['categories'] = ms_task['categories']
    
    result = tool_registry.execute_tool(tool_name='todo_create_task', **params)
    
    if not result.get('success'):
        return {'success': False, 'error': f'Failed to create Microsoft To Do task: {result.get("error")}'}
    
    task_data = result.get('task', {})
    ms_todo_id = task_data.get('id')
    
    sql_insert, params_insert = convert_sql_placeholders('''
        INSERT INTO task_sync_metadata 
        (session_id, platform, platform_task_id, sync_status, last_synced_at)
        VALUES (?, 'microsoft_todo', ?, 'synced', ?)
    ''', (kanban_card['session_id'], ms_todo_id, datetime.now().isoformat()))
    cursor.execute(sql_insert, params_insert)
    
    sql_update, params_update = convert_sql_placeholders('''
        UPDATE sessions SET microsoft_todo_id = ?, updated_at = ? WHERE session_id = ?
    ''', (ms_todo_id, datetime.now().isoformat(), kanban_card['session_id']))
    cursor.execute(sql_update, params_update)
    
    return {'success': True, 'task_id': ms_todo_id, 'task': task_data}


# ============================================
# SYNC STATUS & MANAGEMENT
# ============================================

@task_sync_bp.route('/status/<session_id>', methods=['GET'])
def get_sync_status(session_id):
    """
    Get sync status for a Kanban card across all platforms
    
    Response:
    {
        "session_id": "20251028_1400_task123",
        "platforms": {
            "google_tasks": {"synced": true, "task_id": "...", "last_sync": "..."},
            "microsoft_todo": {"synced": true, "task_id": "...", "last_sync": "..."},
            "google_calendar": {"synced": false, "event_id": null, "last_sync": null}
        }
    }
    
    ✅ FIXED: Proper cursor/connection management with finally block
    """
    cursor = None  # ✅ Initialize before try
    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        sql, params = convert_sql_placeholders('''
            SELECT platform, platform_task_id, sync_status, last_synced_at
            FROM task_sync_metadata
            WHERE session_id = ?
        ''', (session_id,))
        cursor.execute(sql, params)
        
        rows = cursor.fetchall()
        
        # ✅ Close cursor BEFORE processing results
        cursor.close()
        cursor = None
        conn.close()
        conn = None
        
        platforms = {}
        for row in rows:
            platforms[row['platform']] = {
                'synced': row['sync_status'] == 'synced',
                'task_id': row['platform_task_id'],
                'last_sync': row['last_synced_at'],
                'status': row['sync_status']
            }
        
        return jsonify({
            'session_id': session_id,
            'platforms': platforms
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    finally:
        # ✅ GUARANTEED cleanup
        if cursor:
            try:
                cursor.close()
            except:
                pass
        if conn:
            try:
                conn.close()
            except:
                pass


@task_sync_bp.route('/list', methods=['GET'])
def list_synced_tasks():
    """
    List all synced tasks with their sync status
    
    Query Parameters:
    - platform: Filter by platform (google_tasks, microsoft_todo, google_calendar)
    - status: Filter by sync status (synced, pending, conflict, error)
    
    Response:
    {
        "tasks": [
            {
                "session_id": "...",
                "title": "...",
                "platforms": {...}
            }
        ],
        "total": 50
    }
    
    ✅ FIXED: Proper cursor/connection management with finally block
    """
    cursor = None  # ✅ Initialize before try
    conn = None
    try:
        platform_filter = request.args.get('platform')
        status_filter = request.args.get('status')
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
        query = '''
            SELECT DISTINCT s.*, tsm.platform, tsm.platform_task_id, tsm.sync_status, tsm.last_synced_at
            FROM sessions s
            LEFT JOIN task_sync_metadata tsm ON s.session_id = tsm.session_id
            WHERE 1=1
        '''
        params = []
        
        if platform_filter:
            query += ' AND tsm.platform = ?'
            params.append(platform_filter)
        
        if status_filter:
            query += ' AND tsm.sync_status = ?'
            params.append(status_filter)
        
        query += ' ORDER BY s.created_at DESC'
        
        sql, params = convert_sql_placeholders(query, tuple(params))
        cursor.execute(sql, params)
        rows = cursor.fetchall()
        
        # ✅ Close cursor BEFORE processing results
        cursor.close()
        cursor = None
        conn.close()
        conn = None
        
        # Group by session_id
        tasks_map = {}
        for row in rows:
            session_id = row['session_id']
            if session_id not in tasks_map:
                tasks_map[session_id] = {
                    'session_id': session_id,
                    'title': row['title'],
                    'description': row['description'],
                    'priority': row['priority'],
                    'status': row['status'],
                    'platforms': {}
                }
            
            if row['platform']:
                tasks_map[session_id]['platforms'][row['platform']] = {
                    'task_id': row['platform_task_id'],
                    'sync_status': row['sync_status'],
                    'last_synced': row['last_synced_at']
                }
        
        tasks = list(tasks_map.values())
        
        return jsonify({
            'tasks': tasks,
            'total': len(tasks)
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    finally:
        # ✅ GUARANTEED cleanup
        if cursor:
            try:
                cursor.close()
            except:
                pass
        if conn:
            try:
                conn.close()
            except:
                pass


# ============================================
# HEALTH CHECK
# ============================================

@task_sync_bp.route('/health', methods=['GET'])
def health_check():
    """
    Health check for sync service
    
    ✅ No database operations - safe
    """
    return jsonify({
        'status': 'healthy',
        'service': 'task_sync',
        'tools_available': {
            'google_tasks': tool_registry.get_tool_schema('google_tasks_create_task') is not None,
            'microsoft_todo': tool_registry.get_tool_schema('todo_create_task') is not None,
            'google_calendar': tool_registry.get_tool_schema('google_calendar_create_event') is not None
        }
    }), 200
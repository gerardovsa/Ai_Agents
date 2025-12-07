"""
Kanban Board Routes - Integrated with AI Infrastructure
=========================================================
FULLY FIXED VERSION - Production Ready
All cursor management issues resolved

⚠️ CRITICAL DATABASE PATTERN (FIXED NOV 25, 2024):
   convert_sql_placeholders() ONLY converts ? to %s - it does NOT execute queries!
   
   ✅ CORRECT:
       sql, params = convert_sql_placeholders('INSERT ...', (...))
       cursor.execute(sql, params)  # Actually run the query!
       conn.commit()  # Commits the executed query

Features:
- Session CRUD operations
- Kanban column management
- AI agent assignment
- Bridge table integration
- Real-time WebSocket updates (future)

Endpoints:
    GET    /api/kanban/sessions           - List all sessions
    POST   /api/kanban/sessions           - Create new session
    GET    /api/kanban/sessions/:id       - Get session by ID
    PATCH  /api/kanban/sessions/:id       - Update session
    DELETE /api/kanban/sessions/:id       - Delete session
    
    POST   /api/kanban/sessions/:id/assign-agent     - Assign to AI agent
    GET    /api/kanban/sessions/:id/agent-status     - Get agent work status
    PATCH  /api/kanban/sessions/:id/sync-from-agent  - Sync status from agent
"""

from flask import Blueprint, request, jsonify
import sqlite3
import json
import os
from datetime import datetime
from typing import Dict, Optional
import logging

logger = logging.getLogger(__name__)

# Create blueprint
kanban_bp = Blueprint('kanban', __name__, url_prefix='/api/kanban')

# Import database path helpers
from pathlib import Path
from shared.database_utils import get_database_connection, convert_sql_placeholders
import sys
sys.path.insert(0, str(Path(__file__).parent.parent))

# Import database utility with auto-detection
from shared.database_utils import (
    get_synergy_sessions_connection,
    get_ai_infrastructure_connection,
    is_using_supabase
)


# ============================================
# HELPER FUNCTIONS
# ============================================

def get_synergy_db():
    """
    Get connection to Synergy database
    
    Auto-detects environment:
    - Local dev: SQLite in data/synergy_sessions.db
    - Render: Supabase PostgreSQL (synergy_sessions schema)
    """
    return get_synergy_sessions_connection()

def get_ai_db():
    """
    Get connection to AI Infrastructure database
    
    Auto-detects environment:
    - Local dev: SQLite in data/ai_infrastructure.db
    - Render: Supabase PostgreSQL (ai_infrastructure schema)
    """
    return get_ai_infrastructure_connection()


# ============================================
# SESSION MANAGEMENT ENDPOINTS
# ============================================

@kanban_bp.route('/sessions', methods=['GET'])
def list_sessions():
    """
    List all Kanban sessions
    
    Query params:
        - status: Filter by status (active, archived, completed)
        - column: Filter by kanban column
        - limit: Max results (default 100)
    """
    cursor = None
    conn = None
    try:
        status = request.args.get('status')
        column = request.args.get('column')
        limit = int(request.args.get('limit', 100))
        
        conn = get_synergy_db()
        cursor = conn.cursor()
        
        query = 'SELECT * FROM sessions.sessions WHERE 1=1'
        params = []
        
        if status:
            query += ' AND status = %s'
            params.append(status)
        
        if column:
            query += ' AND kanban_column = %s'
            params.append(column)
        
        query += ' ORDER BY created_at DESC LIMIT %s'
        params.append(limit)
        
        cursor.execute(query, params)
        sessions = [dict(row) for row in cursor.fetchall()]
        
        cursor.close()
        cursor = None
        conn.close()
        conn = None
        
        return jsonify({
            'success': True,
            'sessions': sessions,
            'count': len(sessions)
        })
        
    except Exception as e:
        logger.error(f"Failed to list sessions: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500
    finally:
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


@kanban_bp.route('/sessions', methods=['POST'])
def create_session():
    """
    Create new Kanban session
    
    Body:
        {
            "title": "Task title",
            "description": "Task description",
            "priority": "high|medium|low",
            "kanban_column": "backlog|to_do|in_progress|done",
            "tags": ["tag1", "tag2"],
            "project_name": "Project name"
        }
    """
    cursor = None
    conn = None
    try:
        data = request.get_json()
        
        # Generate session ID
        import uuid
        session_id = str(uuid.uuid4())
        
        # Required fields
        title = data.get('title')
        if not title:
            return jsonify({'success': False, 'error': 'Title is required'}), 400
        
        # Optional fields with defaults
        description = data.get('description', '')
        priority = data.get('priority', 'medium')
        kanban_column = data.get('kanban_column', 'backlog')
        status = 'active'
        tags = json.dumps(data.get('tags', []))
        project_name = data.get('project_name', '')
        
        conn = get_synergy_db()
        cursor = conn.cursor()
        
        sql, params = convert_sql_placeholders('''
            INSERT INTO sessions.sessions 
            (session_id, title, description, priority, status, kanban_column, 
             tags, project_name, created_at, updated_at)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        ''', (session_id, title, description, priority, status, kanban_column,
              tags, project_name, datetime.now().isoformat(), datetime.now().isoformat()))
        
        cursor.execute(sql, params)  # ✅ Actually execute the INSERT query
        conn.commit()
        
        cursor.close()
        cursor = None
        conn.close()
        conn = None
        
        logger.info(f"Created Kanban session: {session_id}")
        
        return jsonify({
            'success': True,
            'session_id': session_id,
            'title': title,
            'kanban_column': kanban_column,
            'status': status
        }), 201
        
    except Exception as e:
        logger.error(f"Failed to create session: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500
    finally:
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


@kanban_bp.route('/sessions/<session_id>', methods=['GET'])
def get_session(session_id):
    """Get session by ID with optional agent status"""
    cursor = None
    conn = None
    ai_cursor = None
    ai_conn = None
    try:
        # Get Kanban session
        conn = get_synergy_db()
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM sessions.sessions WHERE session_id = %s', (session_id,))
        session = cursor.fetchone()
        
        cursor.close()
        cursor = None
        conn.close()
        conn = None
        
        if not session:
            return jsonify({'success': False, 'error': 'Session not found'}), 404
        
        session_data = dict(session)
        
        # Check for agent assignment
        ai_conn = get_ai_db()
        ai_cursor = ai_conn.cursor()
        
        sql, params = convert_sql_placeholders('''
            SELECT * FROM kanban_task_links 
            WHERE kanban_session_id = %s
        ''', (session_id,))
        
        ai_cursor.execute(sql, params)
        agent_link = ai_cursor.fetchone()
        
        ai_cursor.close()
        ai_cursor = None
        ai_conn.close()
        ai_conn = None
        
        if agent_link:
            session_data['agent_assigned'] = True
            session_data['agent_info'] = dict(agent_link)
        else:
            session_data['agent_assigned'] = False
        
        return jsonify({
            'success': True,
            'session': session_data
        })
        
    except Exception as e:
        logger.error(f"Failed to get session: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500
    finally:
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
        if ai_cursor:
            try:
                ai_cursor.close()
            except:
                pass
        if ai_conn:
            try:
                ai_conn.close()
            except:
                pass


@kanban_bp.route('/sessions/<session_id>', methods=['PATCH'])
def update_session(session_id):
    """Update session fields"""
    cursor = None
    conn = None
    try:
        data = request.get_json()
        
        # Build dynamic update query
        fields = []
        values = []
        
        allowed_fields = ['title', 'description', 'priority', 'status', 
                         'kanban_column', 'tags', 'project_name', 'notes']
        
        for field in allowed_fields:
            if field in data:
                fields.append(f"{field} = %s")
                values.append(json.dumps(data[field]) if field == 'tags' else data[field])
        
        if not fields:
            return jsonify({'success': False, 'error': 'No fields to update'}), 400
        
        # Add updated_at
        fields.append('updated_at = %s')
        values.append(datetime.now().isoformat())
        values.append(session_id)
        
        conn = get_synergy_db()
        cursor = conn.cursor()
        
        query = f"UPDATE sessions.sessions SET {', '.join(fields)} WHERE session_id = %s"
        cursor.execute(query, values)
        conn.commit()
        
        if cursor.rowcount == 0:
            cursor.close()
            cursor = None
            conn.close()
            conn = None
            return jsonify({'success': False, 'error': 'Session not found'}), 404
        
        cursor.close()
        cursor = None
        conn.close()
        conn = None
        
        logger.info(f"Updated Kanban session: {session_id}")
        
        return jsonify({
            'success': True,
            'session_id': session_id,
            'updated_fields': list(data.keys())
        })
        
    except Exception as e:
        logger.error(f"Failed to update session: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500
    finally:
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


@kanban_bp.route('/sessions/<session_id>', methods=['DELETE'])
def delete_session(session_id):
    """Delete session (and remove agent links)"""
    cursor = None
    conn = None
    ai_cursor = None
    ai_conn = None
    try:
        # Delete from Kanban DB
        conn = get_synergy_db()
        cursor = conn.cursor()
        cursor.execute('DELETE FROM sessions.sessions WHERE session_id = %s', (session_id,))
        conn.commit()
        
        if cursor.rowcount == 0:
            cursor.close()
            cursor = None
            conn.close()
            conn = None
            return jsonify({'success': False, 'error': 'Session not found'}), 404
        
        cursor.close()
        cursor = None
        conn.close()
        conn = None
        
        # Delete from bridge table
        ai_conn = get_ai_db()
        ai_cursor = ai_conn.cursor()
        ai_cursor.execute('DELETE FROM kanban_task_links WHERE kanban_session_id = %s', (session_id,))
        ai_conn.commit()
        
        ai_cursor.close()
        ai_cursor = None
        ai_conn.close()
        ai_conn = None
        
        logger.info(f"Deleted Kanban session: {session_id}")
        
        return jsonify({
            'success': True,
            'session_id': session_id,
            'deleted': True
        })
        
    except Exception as e:
        logger.error(f"Failed to delete session: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500
    finally:
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
        if ai_cursor:
            try:
                ai_cursor.close()
            except:
                pass
        if ai_conn:
            try:
                ai_conn.close()
            except:
                pass


# ============================================
# AI AGENT INTEGRATION ENDPOINTS
# ============================================

@kanban_bp.route('/sessions/<session_id>/assign-agent', methods=['POST'])
def assign_agent(session_id):
    """
    Assign Kanban task to AI agent
    
    Body:
        {
            "agent_id": "agent-001",
            "agent_name": "Data Processing Agent",
            "sync_direction": "bidirectional|ai_to_kanban|kanban_to_ai",
            "auto_sync_enabled": true
        }
    """
    cursor = None
    conn = None
    ai_cursor = None
    ai_conn = None
    try:
        data = request.get_json()
        
        agent_id = data.get('agent_id')
        agent_name = data.get('agent_name')
        
        if not agent_id or not agent_name:
            return jsonify({'success': False, 'error': 'agent_id and agent_name required'}), 400
        
        # Check if session exists
        conn = get_synergy_db()
        cursor = conn.cursor()
        cursor.execute('SELECT title, status, kanban_column FROM sessions.sessions WHERE session_id = %s', (session_id,))
        session = cursor.fetchone()
        
        cursor.close()
        cursor = None
        conn.close()
        conn = None
        
        if not session:
            return jsonify({'success': False, 'error': 'Session not found'}), 404
        
        # Create agent link
        ai_conn = get_ai_db()
        ai_cursor = ai_conn.cursor()
        
        sync_direction = data.get('sync_direction', 'bidirectional')
        auto_sync = data.get('auto_sync_enabled', True)
        
        sql, params = convert_sql_placeholders('''
            INSERT INTO kanban_task_links 
            (agent_id, agent_name, kanban_session_id, kanban_title, kanban_status,
             kanban_column, sync_direction, auto_sync_enabled, agent_work_status,
             created_at, updated_at)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, 'pending', %s, %s)
            ON CONFLICT(kanban_session_id) DO UPDATE SET
                agent_id = excluded.agent_id,
                agent_name = excluded.agent_name,
                sync_direction = excluded.sync_direction,
                auto_sync_enabled = excluded.auto_sync_enabled,
                updated_at = excluded.updated_at
        ''', (agent_id, agent_name, session_id, session['title'], session['status'],
              session['kanban_column'], sync_direction, auto_sync,
              datetime.now().isoformat(), datetime.now().isoformat()))
        
        ai_cursor.execute(sql, params)  # ✅ Actually execute the INSERT query
        ai_conn.commit()
        link_id = ai_cursor.lastrowid
        
        ai_cursor.close()
        ai_cursor = None
        ai_conn.close()
        ai_conn = None
        
        logger.info(f"Assigned agent {agent_id} to Kanban task {session_id}")
        
        return jsonify({
            'success': True,
            'session_id': session_id,
            'agent_id': agent_id,
            'link_id': link_id,
            'sync_direction': sync_direction
        }), 201
        
    except Exception as e:
        logger.error(f"Failed to assign agent: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500
    finally:
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
        if ai_cursor:
            try:
                ai_cursor.close()
            except:
                pass
        if ai_conn:
            try:
                ai_conn.close()
            except:
                pass


@kanban_bp.route('/sessions/<session_id>/agent-status', methods=['GET'])
def get_agent_status(session_id):
    """Get agent work status for this task"""
    cursor = None
    conn = None
    try:
        conn = get_ai_db()
        cursor = conn.cursor()
        
        sql, params = convert_sql_placeholders('''
            SELECT * FROM kanban_task_links 
            WHERE kanban_session_id = %s
        ''', (session_id,))
        
        cursor.execute(sql, params)
        agent_link = cursor.fetchone()
        
        cursor.close()
        cursor = None
        conn.close()
        conn = None
        
        if not agent_link:
            return jsonify({
                'success': True,
                'assigned': False,
                'message': 'No agent assigned to this task'
            })
        
        return jsonify({
            'success': True,
            'assigned': True,
            'agent': dict(agent_link)
        })
        
    except Exception as e:
        logger.error(f"Failed to get agent status: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500
    finally:
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


@kanban_bp.route('/sessions/<session_id>/sync-from-agent', methods=['PATCH'])
def sync_from_agent(session_id):
    """
    Update Kanban task based on agent work status
    
    Body:
        {
            "agent_work_status": "pending|in_progress|completed|failed",
            "notes": "Optional update notes"
        }
    """
    ai_cursor = None
    ai_conn = None
    cursor = None
    conn = None
    try:
        data = request.get_json()
        agent_status = data.get('agent_work_status')
        
        if not agent_status:
            return jsonify({'success': False, 'error': 'agent_work_status required'}), 400
        
        # Get agent link
        ai_conn = get_ai_db()
        ai_cursor = ai_conn.cursor()
        
        sql, params = convert_sql_placeholders('''
            SELECT * FROM kanban_task_links 
            WHERE kanban_session_id = %s
        ''', (session_id,))
        
        ai_cursor.execute(sql, params)
        agent_link = ai_cursor.fetchone()
        
        if not agent_link:
            ai_cursor.close()
            ai_cursor = None
            ai_conn.close()
            ai_conn = None
            return jsonify({'success': False, 'error': 'No agent assigned'}), 404
        
        # Update agent status
        sql, params = convert_sql_placeholders('''
            UPDATE kanban_task_links
            SET agent_work_status = %s, last_synced_at = %s,
                notes = COALESCE(%s, notes)
            WHERE kanban_session_id = %s
        ''', (agent_status, datetime.now().isoformat(), data.get('notes'), session_id))
        
        ai_cursor.execute(sql, params)
        ai_conn.commit()
        
        ai_cursor.close()
        ai_cursor = None
        ai_conn.close()
        ai_conn = None
        
        # Map agent status to Kanban column
        status_to_column = {
            'pending': 'backlog',
            'in_progress': 'in_progress',
            'completed': 'done',
            'failed': 'backlog'  # Move failed tasks back to backlog
        }
        
        new_column = status_to_column.get(agent_status, 'backlog')
        
        # Update Kanban board
        conn = get_synergy_db()
        cursor = conn.cursor()
        
        sql, params = convert_sql_placeholders('''
            UPDATE sessions.sessions
            SET kanban_column = %s, updated_at = %s,
                notes = COALESCE(notes || '\n' || %s, notes)
            WHERE session_id = %s
        ''', (new_column, datetime.now().isoformat(), 
              f"Agent status: {agent_status}", session_id))
        
        cursor.execute(sql, params)
        conn.commit()
        
        cursor.close()
        cursor = None
        conn.close()
        conn = None
        
        logger.info(f"Synced Kanban task {session_id} from agent status: {agent_status}")
        
        return jsonify({
            'success': True,
            'session_id': session_id,
            'agent_work_status': agent_status,
            'kanban_column': new_column,
            'synced': True
        })
        
    except Exception as e:
        logger.error(f"Failed to sync from agent: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500
    finally:
        if ai_cursor:
            try:
                ai_cursor.close()
            except:
                pass
        if ai_conn:
            try:
                ai_conn.close()
            except:
                pass
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

@kanban_bp.route('/health', methods=['GET'])
def health():
    """Health check for Kanban routes"""
    cursor = None
    conn = None
    ai_cursor = None
    ai_conn = None
    try:
        # Test Synergy DB
        conn = get_synergy_db()
        cursor = conn.cursor()
        cursor.execute('SELECT COUNT(*) FROM sessions.sessions')
        session_count = cursor.fetchone()[0]
        
        cursor.close()
        cursor = None
        conn.close()
        conn = None
        
        # Test AI Infrastructure DB
        ai_conn = get_ai_db()
        ai_cursor = ai_conn.cursor()
        ai_cursor.execute('SELECT COUNT(*) FROM kanban_task_links')
        link_count = ai_cursor.fetchone()[0]
        
        ai_cursor.close()
        ai_cursor = None
        ai_conn.close()
        ai_conn = None
        
        return jsonify({
            'status': 'healthy',
            'synergy_db': 'connected',
            'ai_infrastructure_db': 'connected',
            'sessions': session_count,
            'agent_links': link_count
        })
        
    except Exception as e:
        return jsonify({
            'status': 'unhealthy',
            'error': str(e)
        }), 500
    finally:
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
        if ai_cursor:
            try:
                ai_cursor.close()
            except:
                pass
        if ai_conn:
            try:
                ai_conn.close()
            except:
                pass
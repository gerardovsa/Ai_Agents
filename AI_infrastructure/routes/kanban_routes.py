"""
Kanban Board Routes - Integrated with AI Infrastructure
=========================================================
Consolidated Kanban board management on port 5001

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
from shared.database_utils import get_database_connection
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
    try:
        status = request.args.get('status')
        column = request.args.get('column')
        limit = int(request.args.get('limit', 100))
        
        conn = get_synergy_db()
        cursor = conn.cursor()
        
        query = 'SELECT * FROM sessions WHERE 1=1'
        params = []
        
        if status:
            query += ' AND status = ?'
            params.append(status)
        
        if column:
            query += ' AND kanban_column = ?'
            params.append(column)
        
        query += ' ORDER BY created_at DESC LIMIT ?'
        params.append(limit)
        
        cursor.execute(query, params)
        sessions = [dict(row) for row in cursor.fetchall()]
        conn.close()
        
        return jsonify({
            'success': True,
            'sessions': sessions,
            'count': len(sessions)
        })
        
    except Exception as e:
        logger.error(f"Failed to list sessions: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500


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
        
        cursor.execute('''
            INSERT INTO sessions 
            (session_id, title, description, priority, status, kanban_column, 
             tags, project_name, created_at, updated_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (session_id, title, description, priority, status, kanban_column,
              tags, project_name, datetime.now().isoformat(), datetime.now().isoformat()))
        
        conn.commit()
        conn.close()
        
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


@kanban_bp.route('/sessions/<session_id>', methods=['GET'])
def get_session(session_id):
    """Get session by ID with optional agent status"""
    try:
        # Get Kanban session
        conn = get_synergy_db()
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM sessions WHERE session_id = ?', (session_id,))
        session = cursor.fetchone()
        conn.close()
        
        if not session:
            return jsonify({'success': False, 'error': 'Session not found'}), 404
        
        session_data = dict(session)
        
        # Check for agent assignment
        ai_conn = get_ai_db()
        cursor = ai_conn.cursor()
        cursor.execute('''
            SELECT * FROM kanban_task_links 
            WHERE kanban_session_id = ?
        ''', (session_id,))
        agent_link = cursor.fetchone()
        ai_conn.close()
        
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


@kanban_bp.route('/sessions/<session_id>', methods=['PATCH'])
def update_session(session_id):
    """Update session fields"""
    try:
        data = request.get_json()
        
        # Build dynamic update query
        fields = []
        values = []
        
        allowed_fields = ['title', 'description', 'priority', 'status', 
                         'kanban_column', 'tags', 'project_name', 'notes']
        
        for field in allowed_fields:
            if field in data:
                fields.append(f"{field} = ?")
                values.append(json.dumps(data[field]) if field == 'tags' else data[field])
        
        if not fields:
            return jsonify({'success': False, 'error': 'No fields to update'}), 400
        
        # Add updated_at
        fields.append('updated_at = ?')
        values.append(datetime.now().isoformat())
        values.append(session_id)
        
        conn = get_synergy_db()
        cursor = conn.cursor()
        
        query = f"UPDATE sessions SET {', '.join(fields)} WHERE session_id = ?"
        cursor.execute(query, values)
        conn.commit()
        
        if cursor.rowcount == 0:
            conn.close()
            return jsonify({'success': False, 'error': 'Session not found'}), 404
        
        conn.close()
        
        logger.info(f"Updated Kanban session: {session_id}")
        
        return jsonify({
            'success': True,
            'session_id': session_id,
            'updated_fields': list(data.keys())
        })
        
    except Exception as e:
        logger.error(f"Failed to update session: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500


@kanban_bp.route('/sessions/<session_id>', methods=['DELETE'])
def delete_session(session_id):
    """Delete session (and remove agent links)"""
    try:
        # Delete from Kanban DB
        conn = get_synergy_db()
        cursor = conn.cursor()
        cursor.execute('DELETE FROM sessions WHERE session_id = ?', (session_id,))
        conn.commit()
        
        if cursor.rowcount == 0:
            conn.close()
            return jsonify({'success': False, 'error': 'Session not found'}), 404
        
        conn.close()
        
        # Delete from bridge table
        ai_conn = get_ai_db()
        cursor = ai_conn.cursor()
        cursor.execute('DELETE FROM kanban_task_links WHERE kanban_session_id = ?', (session_id,))
        ai_conn.commit()
        ai_conn.close()
        
        logger.info(f"Deleted Kanban session: {session_id}")
        
        return jsonify({
            'success': True,
            'session_id': session_id,
            'deleted': True
        })
        
    except Exception as e:
        logger.error(f"Failed to delete session: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500


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
    try:
        data = request.get_json()
        
        agent_id = data.get('agent_id')
        agent_name = data.get('agent_name')
        
        if not agent_id or not agent_name:
            return jsonify({'success': False, 'error': 'agent_id and agent_name required'}), 400
        
        # Check if session exists
        conn = get_synergy_db()
        cursor = conn.cursor()
        cursor.execute('SELECT title, status, kanban_column FROM sessions WHERE session_id = ?', (session_id,))
        session = cursor.fetchone()
        conn.close()
        
        if not session:
            return jsonify({'success': False, 'error': 'Session not found'}), 404
        
        # Create agent link
        ai_conn = get_ai_db()
        cursor = ai_conn.cursor()
        
        sync_direction = data.get('sync_direction', 'bidirectional')
        auto_sync = data.get('auto_sync_enabled', True)
        
        cursor.execute('''
            INSERT INTO kanban_task_links 
            (agent_id, agent_name, kanban_session_id, kanban_title, kanban_status,
             kanban_column, sync_direction, auto_sync_enabled, agent_work_status,
             created_at, updated_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, 'pending', ?, ?)
            ON CONFLICT(kanban_session_id) DO UPDATE SET
                agent_id = excluded.agent_id,
                agent_name = excluded.agent_name,
                sync_direction = excluded.sync_direction,
                auto_sync_enabled = excluded.auto_sync_enabled,
                updated_at = excluded.updated_at
        ''', (agent_id, agent_name, session_id, session['title'], session['status'],
              session['kanban_column'], sync_direction, auto_sync,
              datetime.now().isoformat(), datetime.now().isoformat()))
        
        ai_conn.commit()
        link_id = cursor.lastrowid
        ai_conn.close()
        
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


@kanban_bp.route('/sessions/<session_id>/agent-status', methods=['GET'])
def get_agent_status(session_id):
    """Get agent work status for this task"""
    try:
        ai_conn = get_ai_db()
        cursor = ai_conn.cursor()
        cursor.execute('''
            SELECT * FROM kanban_task_links 
            WHERE kanban_session_id = ?
        ''', (session_id,))
        agent_link = cursor.fetchone()
        ai_conn.close()
        
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
    try:
        data = request.get_json()
        agent_status = data.get('agent_work_status')
        
        if not agent_status:
            return jsonify({'success': False, 'error': 'agent_work_status required'}), 400
        
        # Get agent link
        ai_conn = get_ai_db()
        cursor = ai_conn.cursor()
        cursor.execute('''
            SELECT * FROM kanban_task_links 
            WHERE kanban_session_id = ?
        ''', (session_id,))
        agent_link = cursor.fetchone()
        
        if not agent_link:
            ai_conn.close()
            return jsonify({'success': False, 'error': 'No agent assigned'}), 404
        
        # Update agent status
        cursor.execute('''
            UPDATE kanban_task_links
            SET agent_work_status = ?,
                last_synced_at = ?,
                notes = COALESCE(?, notes)
            WHERE kanban_session_id = ?
        ''', (agent_status, datetime.now().isoformat(), data.get('notes'), session_id))
        
        ai_conn.commit()
        ai_conn.close()
        
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
        cursor.execute('''
            UPDATE sessions
            SET kanban_column = ?,
                updated_at = ?,
                notes = COALESCE(notes || '\n' || ?, notes)
            WHERE session_id = ?
        ''', (new_column, datetime.now().isoformat(), 
              f"Agent status: {agent_status}", session_id))
        
        conn.commit()
        conn.close()
        
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


# ============================================
# HEALTH CHECK
# ============================================

@kanban_bp.route('/health', methods=['GET'])
def health():
    """Health check for Kanban routes"""
    try:
        # Test Synergy DB
        conn = get_synergy_db()
        cursor = conn.cursor()
        cursor.execute('SELECT COUNT(*) FROM sessions')
        session_count = cursor.fetchone()[0]
        conn.close()
        
        # Test AI Infrastructure DB
        ai_conn = get_ai_db()
        cursor = ai_conn.cursor()
        cursor.execute('SELECT COUNT(*) FROM kanban_task_links')
        link_count = cursor.fetchone()[0]
        ai_conn.close()
        
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

"""
Token Tracking Routes - Real-time token count endpoints

FILE: AI_infrastructure/routes/token_routes.py
PURPOSE: Provide API endpoints for token tracking and updates

ENDPOINTS:
- GET /api/tokens/<thread_id> - Get current token count for thread
- POST /api/tokens/<thread_id> - Update token count for thread
- GET /api/tokens/session/<session_id> - Get token count by session_id

DEPENDENCIES:
- Flask - Web framework
- sqlite3 - Database access

NOTES:
- Token counts updated after each AI response
- Frontend polls this endpoint every 10 seconds
- Returns 0 if thread not found

LAST MODIFIED: 2025-11-14 - Initial implementation
"""

from flask import Blueprint, jsonify, request
import sqlite3
from pathlib import Path
from shared.database_utils import get_database_connection

token_routes = Blueprint('token_routes', __name__)

def get_db_connection():
    """Get database connection to sessions.db"""
    root_dir = Path(__file__).parent.parent.parent
    conn = get_database_connection('ai_infrastructure')
    conn.row_factory = sqlite3.Row
    return conn


@token_routes.route('/api/tokens/<thread_id>', methods=['GET'])
def get_token_count(thread_id):
    """
    Get current token count for a thread
    
    Returns:
        {
            "success": true,
            "thread_id": "...",
            "token_count": 12345,
            "percentage": 6.2,
            "status": "NORMAL"
        }
    """
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT token_count
            FROM sessions.sessions.threads
            WHERE id = ?
        """, (thread_id,))
        
        row = cursor.fetchone()
        conn.close()
        
        if not row:
            return jsonify({
                'success': False,
                'error': 'Thread not found',
                'thread_id': thread_id,
                'token_count': 0
            }), 404
        
        token_count = row['token_count'] or 0
        
        # Calculate percentage and status
        limit = 200000  # Default limit
        percentage = (token_count / limit * 100) if limit > 0 else 0
        
        if percentage >= 95:
            status = 'EMERGENCY'
        elif percentage >= 80:
            status = 'CRITICAL'
        elif percentage >= 50:
            status = 'CAUTION'
        else:
            status = 'NORMAL'
        
        return jsonify({
            'success': True,
            'thread_id': thread_id,
            'token_count': token_count,
            'percentage': round(percentage, 1),
            'status': status,
            'limit': limit
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e),
            'thread_id': thread_id
        }), 500


@token_routes.route('/api/tokens/<thread_id>', methods=['POST'])
def update_token_count(thread_id):
    """
    Update token count for a thread
    
    Body:
        {
            "token_count": 12345
        }
    
    Returns:
        {
            "success": true,
            "thread_id": "...",
            "token_count": 12345
        }
    """
    try:
        data = request.get_json()
        token_count = data.get('token_count', 0)
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            UPDATE sessions.sessions.threads
            SET token_count = ?
            WHERE id = ?
        """, (token_count, thread_id))
        
        conn.commit()
        conn.close()
        
        return jsonify({
            'success': True,
            'thread_id': thread_id,
            'token_count': token_count
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e),
            'thread_id': thread_id
        }), 500


@token_routes.route('/api/tokens/session/<session_id>', methods=['GET'])
def get_token_count_by_session(session_id):
    """
    Get token count by session_id (alias for GET /api/tokens/<thread_id>)
    """
    return get_token_count(session_id)

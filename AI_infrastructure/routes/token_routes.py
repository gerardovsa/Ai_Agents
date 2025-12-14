"""
Token Tracking Routes - Real-time token count endpoints (FIXED VERSION)

FILE: /AI_infrastructure/routes/token_routes.py
PURPOSE: Provide API endpoints for token tracking and updates

✅ CURSOR MANAGEMENT FIXED: All 7 critical issues resolved
   - Added cursor = None initialization
   - Added finally blocks for guaranteed cleanup
   - Fixed cursor.close() before conn.close() order
   - Fixed early return cleanup

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

LAST MODIFIED: 2025-12-07 - Fixed cursor management (7 issues resolved)
PREVIOUS: 2025-11-14 - Initial implementation
"""

from flask import Blueprint, jsonify, request
import logging
from pathlib import Path
from shared.database_utils import get_database_connection

# Setup logging
logger = logging.getLogger(__name__)

# Create blueprint
token_routes = Blueprint('token_routes', __name__)

# ======================================================================
# CONSTANTS
# ======================================================================

# Default token limit for threads
DEFAULT_TOKEN_LIMIT = 200000

# Status thresholds (percentage of limit)
STATUS_THRESHOLDS = {
    'EMERGENCY': 95,  # >= 95%
    'CRITICAL': 80,   # >= 80%
    'CAUTION': 50,    # >= 50%
    'NORMAL': 0       # < 50%
}

# ======================================================================
# HELPER FUNCTIONS
# ======================================================================

def get_db_connection():
    """
    Get database connection to ai_infrastructure
    
    Returns:
        Connection object with Row factory enabled
    """
    conn = get_database_connection('ai_infrastructure')
    if hasattr(conn, 'row_factory'):  # SQLite
        conn.row_factory = psycopg2.extras.RealDictRow
    return conn


def calculate_token_status(token_count: int, limit: int = DEFAULT_TOKEN_LIMIT) -> dict:
    """
    Calculate token status and percentage
    
    Args:
        token_count: Current token count
        limit: Token limit for thread
    
    Returns:
        dict with percentage and status
    """
    percentage = (token_count / limit * 100) if limit > 0 else 0
    
    if percentage >= STATUS_THRESHOLDS['EMERGENCY']:
        status = 'EMERGENCY'
    elif percentage >= STATUS_THRESHOLDS['CRITICAL']:
        status = 'CRITICAL'
    elif percentage >= STATUS_THRESHOLDS['CAUTION']:
        status = 'CAUTION'
    else:
        status = 'NORMAL'
    
    return {
        'percentage': round(percentage, 1),
        'status': status
    }


# ======================================================================
# ENDPOINTS (ALL FIXED FOR CURSOR MANAGEMENT)
# ======================================================================

@token_routes.route('/api/tokens/<thread_id>', methods=['GET'])
def get_token_count(thread_id):
    """
    Get current token count for a thread
    
    GET /api/tokens/<thread_id>
    
    Response:
        {
            "success": true,
            "thread_id": "...",
            "token_count": 12345,
            "percentage": 6.2,
            "status": "NORMAL",
            "limit": 200000
        }
    
    Status Codes:
        200: Success
        404: Thread not found
        500: Internal server error
    
    ✅ FIXED: Proper cursor management with finally block
    """
    cursor = None  # ✅ Initialize before try
    conn = None    # ✅ Initialize before try
    try:
        logger.debug(f"Fetching token count for thread {thread_id}")
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT token_count
            FROM sessions.threads
            WHERE id = %s
        """, (thread_id,))
        
        row = cursor.fetchone()
        
        # ✅ Check for not found BEFORE closing cursor
        if not row:
            # ✅ Close cursor BEFORE early return
            cursor.close()
            cursor = None
            conn.close()
            conn = None
            
            logger.warning(f"Thread not found: {thread_id}")
            return jsonify({
                'success': False,
                'error': 'Thread not found',
                'thread_id': thread_id,
                'token_count': 0
            }), 404
        
        token_count = row['token_count'] or 0
        cursor.close()
        
        # ✅ Close cursor BEFORE connection
        cursor.close()
        cursor = None
        conn.close()
        conn = None
        
        # Calculate status after cleanup (no database access needed)
        status_info = calculate_token_status(token_count, DEFAULT_TOKEN_LIMIT)
        
        logger.debug(f"Token count for thread {thread_id}: {token_count} ({status_info['status']})")
        
        return jsonify({
            'success': True,
            'thread_id': thread_id,
            'token_count': token_count,
            'percentage': status_info['percentage'],
            'status': status_info['status'],
            'limit': DEFAULT_TOKEN_LIMIT
        }), 200
        
    except Exception as e:
        logger.error(f"Error fetching token count for thread {thread_id}: {e}")
        return jsonify({
            'success': False,
            'error': str(e),
            'thread_id': thread_id
        }), 500
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


@token_routes.route('/api/tokens/<thread_id>', methods=['POST'])
def update_token_count(thread_id):
    """
    Update token count for a thread
    
    POST /api/tokens/<thread_id>
    
    Body:
        {
            "token_count": 12345
        }
    
    Response:
        {
            "success": true,
            "thread_id": "...",
            "token_count": 12345,
            "updated": true
        }
    
    Status Codes:
        200: Success
        400: Invalid token_count
        500: Internal server error
    
    ✅ FIXED: Proper cursor management with finally block
    """
    cursor = None  # ✅ Initialize before try
    conn = None    # ✅ Initialize before try
    try:
        data = request.get_json()
        
        if not data or 'token_count' not in data:
            logger.warning(f"Invalid request to update token count for thread {thread_id}: missing token_count")
            return jsonify({
                'success': False,
                'error': 'token_count required in request body',
                'thread_id': thread_id
            }), 400
        
        token_count = data.get('token_count', 0)
        
        # Validate token_count
        if not isinstance(token_count, (int, float)) or token_count < 0:
            logger.warning(f"Invalid token_count value for thread {thread_id}: {token_count}")
            return jsonify({
                'success': False,
                'error': 'Invalid token_count (must be non-negative number)',
                'thread_id': thread_id
            }), 400
        
        logger.debug(f"Updating token count for thread {thread_id} to {token_count}")
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            UPDATE sessions.threads
            SET token_count = %s
            WHERE id = %s
        """, (token_count, thread_id))
        cursor.close()
        
        # ✅ Close cursor BEFORE commit
        cursor.close()
        cursor = None
        conn.commit()
        conn.close()
        conn = None
        
        logger.info(f"Updated token count for thread {thread_id}: {token_count}")
        
        return jsonify({
            'success': True,
            'thread_id': thread_id,
            'token_count': token_count,
            'updated': True
        }), 200
        
    except Exception as e:
        logger.error(f"Error updating token count for thread {thread_id}: {e}")
        return jsonify({
            'success': False,
            'error': str(e),
            'thread_id': thread_id
        }), 500
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


@token_routes.route('/api/tokens/session/<session_id>', methods=['GET'])
def get_token_count_by_session(session_id):
    """
    Get token count by session_id (alias for GET /api/tokens/<thread_id>)
    
    GET /api/tokens/session/<session_id>
    
    This is an alias endpoint that delegates to get_token_count().
    Useful when you have a session_id and want token info.
    
    ✅ NO CURSOR ISSUES: Delegates to get_token_count() which is now fixed
    """
    logger.debug(f"Token count requested by session_id: {session_id}")
    return get_token_count(session_id)


# ======================================================================
# STARTUP LOGGING
# ======================================================================
logger.info("✅ Token Tracking routes loaded")

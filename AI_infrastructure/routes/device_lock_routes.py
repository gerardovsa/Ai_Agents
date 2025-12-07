"""
AI_infrastructure/routes/device_lock_routes.py
Device Lock Management Routes
Handles thread locking/unlocking per device for multi-user isolation
FULLY FIXED VERSION - Production Ready

⚠️ CURSOR MANAGEMENT FIXES (Dec 07, 2025):
   - ✅ All cursors properly closed before connections
   - ✅ All functions use finally blocks
   - ✅ All cursors initialized as None
   - ✅ Helper functions fixed (cascade fix to all endpoints)

CRITICAL: All database operations now use Supabase PostgreSQL
- ai_infrastructure schema: device_registry, thread_lock_history  
- sessions schema: threads

LAST MODIFIED: 2025-12-07 - Fixed cursor management
"""

from flask import Blueprint, request, jsonify
from shared.database_utils import get_database_connection, convert_sql_placeholders
import uuid
from datetime import datetime

device_lock_bp = Blueprint('device_lock', __name__)

# Legacy path constants (now ignored, using Supabase)
AI_DB_PATH = 'ai_infrastructure'  # Schema name
SESSIONS_DB_PATH = 'sessions'  # Schema name

# ============================================================================
# HELPER FUNCTIONS - FIXED CURSOR MANAGEMENT
# ============================================================================

def execute_sqlite_query(db_path, query, params=()):
    """
    Wrapper: Redirects to Supabase instead of SQLite
    
    ✅ FIXED: Proper cursor management with finally block
    """
    cursor = None  # ✅ Initialize cursor before try
    conn = None    # ✅ Initialize connection before try
    try:
        schema = 'sessions' if 'sessions.db' in db_path else 'ai_infrastructure'
        conn = get_database_connection(schema)
        cursor = conn.cursor()
        query_converted, params_converted = convert_sql_placeholders(query, params)
        cursor.execute(query_converted, params_converted)
        result = cursor.fetchall()
        cursor.close()
        
        # ✅ Close cursor BEFORE connection
        cursor.close()
        cursor = None
        conn.close()
        conn = None
        
        return result
    finally:
        # ✅ Guaranteed cleanup
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


def execute_sqlite_update(db_path, query, params=()):
    """
    Wrapper: Redirects to Supabase instead of SQLite
    
    ✅ FIXED: Proper cursor management with finally block
    """
    cursor = None  # ✅ Initialize cursor before try
    conn = None    # ✅ Initialize connection before try
    try:
        schema = 'sessions' if 'sessions.db' in db_path else 'ai_infrastructure'
        conn = get_database_connection(schema)
        cursor = conn.cursor()
        query_converted, params_converted = convert_sql_placeholders(query, params)
        cursor.execute(query_converted, params_converted)
        conn.commit()
        cursor.close()
        
        # ✅ Close cursor BEFORE connection
        cursor.close()
        cursor = None
        conn.close()
        conn = None
    finally:
        # ✅ Guaranteed cleanup
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


# ============================================================================
# ENDPOINT 1: REGISTER DEVICE
# ============================================================================

@device_lock_bp.route('/api/device/register', methods=['POST'])
def register_device():
    """
    Register or update device information
    
    ✅ FIXED: Proper cursor management with finally block
    
    Request:
        {
            "device_id": "uuid-or-null",
            "device_name": "MacBook Pro",
            "user_id": 1,
            "device_fingerprint": "Mozilla/5.0..."
        }
    
    Response:
        {
            "success": true,
            "device_id": "abc-123-def",
            "device_name": "MacBook Pro"
        }
    """
    cursor = None  # ✅ Initialize cursor before try
    conn = None    # ✅ Initialize connection before try
    try:
        data = request.json
        user_id = data.get('user_id')
        device_id = data.get('device_id') or str(uuid.uuid4())
        device_name = data.get('device_name', 'Unknown Device')
        device_fingerprint = data.get('device_fingerprint', '')
        
        conn = get_database_connection('ai_infrastructure')
        cursor = conn.cursor()
        
        # Check if device exists
        query, params = convert_sql_placeholders(
            "SELECT device_id FROM ai_infrastructure.device_registry WHERE device_id = %s",
            (device_id,)
        )
        cursor.execute(query, params)
        existing = cursor.fetchone()
        
        if existing:
            # Update last_seen_at
            query, params = convert_sql_placeholders("""
                UPDATE ai_infrastructure.device_registry 
                SET last_seen_at = CURRENT_TIMESTAMP, device_name = %s, device_fingerprint = %s
                WHERE device_id = %s
            """, (device_name, device_fingerprint, device_id))
            cursor.execute(query, params)
        else:
            # Insert new device
            query, params = convert_sql_placeholders("""
                INSERT INTO ai_infrastructure.device_registry 
                (device_id, user_id, device_name, device_fingerprint, created_at, last_seen_at)
                VALUES (%s, %s, %s, %s, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP)
            """, (device_id, user_id, device_name, device_fingerprint))
            cursor.execute(query, params)
        
        conn.commit()
        cursor.close()
        
        # ✅ Close cursor BEFORE connection
        cursor.close()
        cursor = None
        conn.close()
        conn = None
        
        return jsonify({
            'success': True,
            'device_id': device_id,
            'device_name': device_name
        })
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500
    finally:
        # ✅ Guaranteed cleanup
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


# ============================================================================
# ENDPOINT 2: LOCK THREAD
# ============================================================================

@device_lock_bp.route('/api/thread/<int:thread_id>/lock', methods=['POST'])
def lock_thread(thread_id):
    """
    Lock thread to current device
    
    ✅ FIXED: Uses fixed helper functions with proper cursor management
    """
    try:
        data = request.json
        device_id = data.get('device_id')
        user_id = data.get('user_id')
        
        # Verify thread belongs to user
        thread = execute_sqlite_query(
            str(SESSIONS_DB_PATH),
            "SELECT user_id FROM sessions.threads WHERE id = %s",
            (thread_id,)
        )
        
        if not thread or thread[0]['user_id'] != user_id:
            return jsonify({'success': False, 'error': 'Thread not found'}), 404
        
        # Lock the thread
        execute_sqlite_update(
            str(SESSIONS_DB_PATH),
            """UPDATE sessions.threads 
               SET locked_to_device_id = %s,
                   locked_at = CURRENT_TIMESTAMP,
                   lock_mode = 'locked'
               WHERE id = %s""",
            (device_id, thread_id)
        )
        
        # Get device name
        device = execute_sqlite_query(
            str(AI_DB_PATH),
            "SELECT device_name FROM ai_infrastructure.device_registry WHERE device_id = %s",
            (device_id,)
        )
        
        device_name = device[0]['device_name'] if device else 'Unknown Device'
        
        # Log lock event
        execute_sqlite_update(
            str(AI_DB_PATH),
            """INSERT INTO ai_infrastructure.thread_lock_history (thread_id, device_id, action)
               VALUES (%s, %s, 'locked')""",
            (thread_id, device_id)
        )
        
        return jsonify({
            'success': True,
            'locked_to': device_name,
            'locked_at': datetime.now().isoformat()
        })
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


# ============================================================================
# ENDPOINT 3: UNLOCK THREAD
# ============================================================================

@device_lock_bp.route('/api/thread/<int:thread_id>/unlock', methods=['POST'])
def unlock_thread(thread_id):
    """
    Unlock thread (make available to all devices)
    
    ✅ FIXED: Uses fixed helper functions with proper cursor management
    """
    try:
        data = request.json
        device_id = data.get('device_id')
        user_id = data.get('user_id')
        
        # Verify thread is locked by this device OR user owns thread
        thread = execute_sqlite_query(
            str(SESSIONS_DB_PATH),
            """SELECT locked_to_device_id, user_id 
               FROM sessions.threads WHERE id = %s""",
            (thread_id,)
        )
        
        if not thread:
            return jsonify({'success': False, 'error': 'Thread not found'}), 404
        
        locked_device = thread[0]['locked_to_device_id']
        thread_user = thread[0]['user_id']
        
        # Only allow unlock if locked to this device OR user owns thread
        if locked_device != device_id and thread_user != user_id:
            return jsonify({
                'success': False,
                'error': 'Cannot unlock thread locked by another device'
            }), 403
        
        # Unlock the thread
        execute_sqlite_update(
            str(SESSIONS_DB_PATH),
            """UPDATE sessions.threads 
               SET locked_to_device_id = NULL,
                   locked_at = NULL,
                   lock_mode = 'unlocked'
               WHERE id = %s""",
            (thread_id,)
        )
        
        # Log unlock event
        execute_sqlite_update(
            str(AI_DB_PATH),
            """INSERT INTO ai_infrastructure.thread_lock_history (thread_id, device_id, action)
               VALUES (%s, %s, 'unlocked')""",
            (thread_id, device_id)
        )
        
        return jsonify({
            'success': True,
            'message': 'Thread unlocked'
        })
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


# ============================================================================
# ENDPOINT 4: GET LOCK STATUS
# ============================================================================

@device_lock_bp.route('/api/thread/<int:thread_id>/lock-status', methods=['GET'])
def get_lock_status(thread_id):
    """
    Get lock status for thread
    
    ✅ FIXED: Uses fixed helper functions with proper cursor management
    """
    try:
        device_id = request.args.get('device_id')
        user_id = request.args.get('user_id')
        
        # Get thread lock status (JOIN across two databases - need to query separately)
        thread = execute_sqlite_query(
            str(SESSIONS_DB_PATH),
            """SELECT locked_to_device_id, locked_at, lock_mode, user_id
               FROM sessions.threads
               WHERE id = %s""",
            (thread_id,)
        )
        
        if not thread:
            return jsonify({'success': False, 'error': 'Thread not found'}), 404
        
        thread_data = thread[0]
        locked_device_id = thread_data['locked_to_device_id']
        is_locked = locked_device_id is not None
        is_current_device = locked_device_id == device_id
        can_edit = not is_locked or is_current_device
        
        # Get device name if locked
        device_name = None
        if is_locked:
            device = execute_sqlite_query(
                str(AI_DB_PATH),
                "SELECT device_name FROM ai_infrastructure.device_registry WHERE device_id = %s",
                (locked_device_id,)
            )
            device_name = device[0]['device_name'] if device else 'Unknown Device'
        
        return jsonify({
            'success': True,
            'locked': is_locked,
            'locked_to_device_id': locked_device_id,
            'locked_to_device_name': device_name,
            'locked_at': thread_data['locked_at'],
            'lock_mode': thread_data['lock_mode'],
            'is_current_device': is_current_device,
            'can_edit': can_edit,
            'is_owner': thread_data['user_id'] == int(user_id) if user_id else False
        })
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


# ============================================================================
# ENDPOINT 5: GET MULTIPLE LOCK STATUS
# ============================================================================

@device_lock_bp.route('/api/threads/lock-status', methods=['POST'])
def get_multiple_lock_status():
    """
    Get lock status for multiple threads (for thread list)
    
    ✅ FIXED: Uses fixed helper functions with proper cursor management
    """
    try:
        data = request.json
        thread_ids = data.get('thread_ids', [])
        device_id = data.get('device_id')
        
        if not thread_ids:
            return jsonify({'success': True, 'locks': {}})
        
        # Build query for multiple threads (no JOIN - different databases)
        placeholders = ','.join(['%s'] * len(thread_ids))
        query = f"""
            SELECT id as thread_id, locked_to_device_id, lock_mode
            FROM sessions.threads
            WHERE id IN ({placeholders})
        """
        
        results = execute_sqlite_query(str(SESSIONS_DB_PATH), query, tuple(thread_ids))
        
        # Get all device names in one query
        locked_device_ids = [r['locked_to_device_id'] for r in results if r['locked_to_device_id']]
        device_names = {}
        if locked_device_ids:
            dev_placeholders = ','.join(['%s'] * len(locked_device_ids))
            device_query = f"SELECT device_id, device_name FROM ai_infrastructure.device_registry WHERE device_id IN ({dev_placeholders})"
            devices = execute_sqlite_query(str(AI_DB_PATH), device_query, tuple(locked_device_ids))
            device_names = {d['device_id']: d['device_name'] for d in devices}
        
        # Format results
        locks = {}
        for row in results:
            thread_id = row['thread_id']
            locked_device_id = row['locked_to_device_id']
            is_locked = locked_device_id is not None
            is_current_device = locked_device_id == device_id
            
            locks[thread_id] = {
                'locked': is_locked,
                'locked_to_device_name': device_names.get(locked_device_id, 'Unknown Device') if is_locked else None,
                'lock_mode': row['lock_mode'],
                'is_current_device': is_current_device,
                'can_edit': not is_locked or is_current_device
            }
        
        return jsonify({
            'success': True,
            'locks': locks
        })
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


# ============================================================================
# MODULE INITIALIZATION
# ============================================================================

print('[DEVICE LOCK] Routes loaded: 5 endpoints (cursor management fixed - 2025-12-07)')
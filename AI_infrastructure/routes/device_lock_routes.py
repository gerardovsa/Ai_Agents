"""
Device Lock Management Routes
Handles thread locking/unlocking per device for multi-user isolation
"""

from flask import Blueprint, request, jsonify
from AI_infrastructure.utils.database_helpers import (
    get_pooled_sqlite_connection,
    execute_sqlite_query,
    execute_sqlite_update
)
from pathlib import Path
import uuid
from datetime import datetime

device_lock_bp = Blueprint('device_lock', __name__)
AI_DB_PATH = Path(__file__).parent.parent.parent / 'data' / 'ai_infrastructure.db'
SESSIONS_DB_PATH = Path(__file__).parent.parent.parent / 'data' / 'sessions.db'


@device_lock_bp.route('/api/device/register', methods=['POST'])
def register_device():
    """
    Register or update device information
    
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
    data = request.json
    user_id = data.get('user_id')
    device_id = data.get('device_id') or str(uuid.uuid4())
    device_name = data.get('device_name', 'Unknown Device')
    device_fingerprint = data.get('device_fingerprint', '')
    
    try:
        # Check if device exists
        existing = execute_sqlite_query(
            str(AI_DB_PATH),
            "SELECT device_id FROM ai_infrastructure.device_registry WHERE device_id = ?",
            (device_id,)
        )
        
        if existing:
            # Update last_seen_at
            execute_sqlite_update(
                str(AI_DB_PATH),
                """UPDATE ai_infrastructure.device_registry 
                   SET last_seen_at = CURRENT_TIMESTAMP,
                       device_name = ?,
                       device_fingerprint = ?
                   WHERE device_id = ?""",
                (device_name, device_fingerprint, device_id)
            )
        else:
            # Insert new device
            execute_sqlite_update(
                str(AI_DB_PATH),
                """INSERT INTO ai_infrastructure.device_registry 
                   (device_id, user_id, device_name, device_fingerprint)
                   VALUES (?, ?, ?, ?)""",
                (device_id, user_id, device_name, device_fingerprint)
            )
        
        return jsonify({
            'success': True,
            'device_id': device_id,
            'device_name': device_name
        })
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@device_lock_bp.route('/api/thread/<int:thread_id>/lock', methods=['POST'])
def lock_thread(thread_id):
    """Lock thread to current device"""
    data = request.json
    device_id = data.get('device_id')
    user_id = data.get('user_id')
    
    try:
        # Verify thread belongs to user
        thread = execute_sqlite_query(
            str(SESSIONS_DB_PATH),
            "SELECT user_id FROM sessions.sessions.threads WHERE id = ?",
            (thread_id,)
        )
        
        if not thread or thread[0]['user_id'] != user_id:
            return jsonify({'success': False, 'error': 'Thread not found'}), 404
        
        # Lock the thread
        execute_sqlite_update(
            str(SESSIONS_DB_PATH),
            """UPDATE sessions.sessions.threads 
               SET locked_to_device_id = ?,
                   locked_at = CURRENT_TIMESTAMP,
                   lock_mode = 'locked'
               WHERE id = ?""",
            (device_id, thread_id)
        )
        
        # Get device name
        device = execute_sqlite_query(
            str(AI_DB_PATH),
            "SELECT device_name FROM ai_infrastructure.device_registry WHERE device_id = ?",
            (device_id,)
        )
        
        device_name = device[0]['device_name'] if device else 'Unknown Device'
        
        # Log lock event
        execute_sqlite_update(
            str(AI_DB_PATH),
            """INSERT INTO ai_infrastructure.thread_lock_history (thread_id, device_id, action)
               VALUES (?, ?, 'locked')""",
            (thread_id, device_id)
        )
        
        return jsonify({
            'success': True,
            'locked_to': device_name,
            'locked_at': datetime.now().isoformat()
        })
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@device_lock_bp.route('/api/thread/<int:thread_id>/unlock', methods=['POST'])
def unlock_thread(thread_id):
    """Unlock thread (make available to all devices)"""
    data = request.json
    device_id = data.get('device_id')
    user_id = data.get('user_id')
    
    try:
        # Verify thread is locked by this device OR user owns thread
        thread = execute_sqlite_query(
            str(SESSIONS_DB_PATH),
            """SELECT locked_to_device_id, user_id 
               FROM sessions.sessions.threads WHERE id = ?""",
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
            """UPDATE sessions.sessions.threads 
               SET locked_to_device_id = NULL,
                   locked_at = NULL,
                   lock_mode = 'unlocked'
               WHERE id = ?""",
            (thread_id,)
        )
        
        # Log unlock event
        execute_sqlite_update(
            str(AI_DB_PATH),
            """INSERT INTO ai_infrastructure.thread_lock_history (thread_id, device_id, action)
               VALUES (?, ?, 'unlocked')""",
            (thread_id, device_id)
        )
        
        return jsonify({
            'success': True,
            'message': 'Thread unlocked'
        })
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@device_lock_bp.route('/api/thread/<int:thread_id>/lock-status', methods=['GET'])
def get_lock_status(thread_id):
    """Get lock status for thread"""
    device_id = request.args.get('device_id')
    user_id = request.args.get('user_id')
    
    try:
        # Get thread lock status (JOIN across two databases - need to query separately)
        thread = execute_sqlite_query(
            str(SESSIONS_DB_PATH),
            """SELECT locked_to_device_id, locked_at, lock_mode, user_id
               FROM sessions.sessions.threads
               WHERE id = ?""",
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
                "SELECT device_name FROM ai_infrastructure.device_registry WHERE device_id = ?",
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


@device_lock_bp.route('/api/threads/lock-status', methods=['POST'])
def get_multiple_lock_status():
    """Get lock status for multiple threads (for thread list)"""
    data = request.json
    thread_ids = data.get('thread_ids', [])
    device_id = data.get('device_id')
    
    try:
        if not thread_ids:
            return jsonify({'success': True, 'locks': {}})
        
        # Build query for multiple threads (no JOIN - different databases)
        placeholders = ','.join('?' * len(thread_ids))
        query = f"""
            SELECT id as thread_id, locked_to_device_id, lock_mode
            FROM sessions.sessions.threads
            WHERE id IN ({placeholders})
        """
        
        results = execute_sqlite_query(str(SESSIONS_DB_PATH), query, tuple(thread_ids))
        
        # Get all device names in one query
        locked_device_ids = [r['locked_to_device_id'] for r in results if r['locked_to_device_id']]
        device_names = {}
        if locked_device_ids:
            dev_placeholders = ','.join('?' * len(locked_device_ids))
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

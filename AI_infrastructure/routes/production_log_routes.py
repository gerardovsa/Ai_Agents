"""
Production Log API Routes

Endpoints for managing production log entries:
- GET /api/production-log/:ticket_id - Get all log entries for a job
- POST /api/production-log/:ticket_id - Add new log entry
- PUT /api/production-log/:log_id - Edit existing log entry
- DELETE /api/production-log/:log_id - Delete log entry
- POST /api/production-log/:ticket_id/stage-change - Auto-log stage transition
- POST /api/production-log/:ticket_id/notification - Log client notification
"""

from flask import Blueprint, request, jsonify
import sqlite3
from pathlib import Path
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

# Create blueprint
production_log_bp = Blueprint('production_log', __name__, url_prefix='/api/production-log')

def get_db_connection():
    """Get database connection to kanban analytics"""
    db_path = Path(__file__).parent.parent.parent / 'data' / 'kanban_analytics.db'
    conn = sqlite3.connect(str(db_path))
    conn.row_factory = sqlite3.Row
    return conn

# ============================================
# READ OPERATIONS
# ============================================

@production_log_bp.route('/<int:ticket_id>', methods=['GET'])
def get_production_log(ticket_id: int):
    """
    Get all production log entries for a job
    
    Query params:
    - entry_type: Filter by type (stage_change, note, wastage, delay, client_notification)
    - limit: Max entries to return (default: 100)
    """
    try:
        entry_type = request.args.get('entry_type')
        limit = int(request.args.get('limit', 100))
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
        query = """
            SELECT 
                log_id,
                ticket_id,
                log_date,
                log_time,
                user_initials,
                entry_type,
                
                -- Stage transition
                from_stage_id,
                to_stage_id,
                from_stage_name,
                to_stage_name,
                
                -- General
                note_text,
                
                -- Wastage
                wastage_amount,
                wastage_unit,
                wastage_type,
                wastage_reason,
                
                -- Stock
                stock_item,
                stock_quantity_change,
                stock_reason,
                
                -- Delay
                delay_hours,
                delay_reason,
                delay_resolved,
                
                -- Client notification
                notification_type,
                notification_recipient,
                notification_subject,
                notification_message,
                notification_status,
                notification_sent_at,
                
                -- Metadata
                is_edited,
                created_at,
                updated_at,
                created_by_user
            FROM production_log
            WHERE ticket_id = ?
        """
        
        params = [ticket_id]
        
        if entry_type:
            query += " AND entry_type = ?"
            params.append(entry_type)
        
        query += " ORDER BY log_date DESC, log_time DESC LIMIT ?"
        params.append(limit)
        
        cursor.execute(query, params)
        entries = [dict(row) for row in cursor.fetchall()]
        
        conn.close()
        
        return jsonify({
            'success': True,
            'ticket_id': ticket_id,
            'count': len(entries),
            'entries': entries
        }), 200
        
    except Exception as e:
        logger.error(f"Failed to get production log: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@production_log_bp.route('/entry/<int:log_id>', methods=['GET'])
def get_log_entry(log_id: int):
    """Get single log entry by ID"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT * FROM production_log WHERE log_id = ?
        """, (log_id,))
        
        entry = cursor.fetchone()
        conn.close()
        
        if not entry:
            return jsonify({
                'success': False,
                'error': 'Log entry not found'
            }), 404
        
        return jsonify({
            'success': True,
            'entry': dict(entry)
        }), 200
        
    except Exception as e:
        logger.error(f"Failed to get log entry: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

# ============================================
# CREATE OPERATIONS
# ============================================

@production_log_bp.route('/<int:ticket_id>', methods=['POST'])
def add_log_entry(ticket_id: int):
    """
    Add new production log entry
    
    Body (JSON):
    {
        "user_initials": "JD",
        "entry_type": "note|wastage|delay|stock_change",
        "note_text": "...",
        "wastage_amount": 50,
        "wastage_unit": "sheets",
        "wastage_type": "paper",
        "wastage_reason": "...",
        "delay_hours": 2.5,
        "delay_reason": "equipment_failure",
        "stock_item": "...",
        "stock_quantity_change": -10
    }
    """
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({
                'success': False,
                'error': 'Request body required'
            }), 400
        
        # Required fields
        user_initials = data.get('user_initials')
        entry_type = data.get('entry_type', 'note')
        
        if not user_initials:
            return jsonify({
                'success': False,
                'error': 'user_initials required'
            }), 400
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Build insert query dynamically based on entry type
        fields = {
            'ticket_id': ticket_id,
            'user_initials': user_initials,
            'entry_type': entry_type,
            'note_text': data.get('note_text'),
            'created_by_user': data.get('created_by_user', user_initials)
        }
        
        # Add type-specific fields
        if entry_type == 'wastage':
            fields.update({
                'wastage_amount': data.get('wastage_amount'),
                'wastage_unit': data.get('wastage_unit'),
                'wastage_type': data.get('wastage_type'),
                'wastage_reason': data.get('wastage_reason')
            })
        elif entry_type == 'delay':
            fields.update({
                'delay_hours': data.get('delay_hours'),
                'delay_reason': data.get('delay_reason'),
                'delay_resolved': data.get('delay_resolved', 0)
            })
        elif entry_type == 'stock_change':
            fields.update({
                'stock_item': data.get('stock_item'),
                'stock_quantity_change': data.get('stock_quantity_change'),
                'stock_reason': data.get('stock_reason')
            })
        
        # Build SQL
        cols = ', '.join(fields.keys())
        placeholders = ', '.join('?' * len(fields))
        values = tuple(fields.values())
        
        cursor.execute(f"""
            INSERT INTO production_log ({cols})
            VALUES ({placeholders})
        """, values)
        
        log_id = cursor.lastrowid
        conn.commit()
        conn.close()
        
        return jsonify({
            'success': True,
            'log_id': log_id,
            'message': 'Log entry created'
        }), 201
        
    except Exception as e:
        logger.error(f"Failed to add log entry: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@production_log_bp.route('/<int:ticket_id>/stage-change', methods=['POST'])
def log_stage_change(ticket_id: int):
    """
    Log automatic stage transition (called when dragging job between columns)
    
    Body:
    {
        "user_initials": "JD",
        "from_stage_id": 3,
        "to_stage_id": 5,
        "from_stage_name": "Design",
        "to_stage_name": "Press"
    }
    """
    try:
        data = request.get_json()
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT INTO production_log (
                ticket_id,
                user_initials,
                entry_type,
                from_stage_id,
                to_stage_id,
                from_stage_name,
                to_stage_name,
                note_text
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            ticket_id,
            data.get('user_initials', 'USER'),
            'stage_change',
            data.get('from_stage_id'),
            data.get('to_stage_id'),
            data.get('from_stage_name'),
            data.get('to_stage_name'),
            f"Moved from {data.get('from_stage_name')} to {data.get('to_stage_name')}"
        ))
        
        log_id = cursor.lastrowid
        conn.commit()
        conn.close()
        
        return jsonify({
            'success': True,
            'log_id': log_id,
            'message': 'Stage change logged'
        }), 201
        
    except Exception as e:
        logger.error(f"Failed to log stage change: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@production_log_bp.route('/<int:ticket_id>/notification', methods=['POST'])
def log_client_notification(ticket_id: int):
    """
    Log client notification
    
    Body:
    {
        "user_initials": "JD",
        "notification_type": "email|sms|phone|whatsapp",
        "notification_recipient": "client@example.com",
        "notification_subject": "Your order update",
        "notification_message": "...",
        "notification_status": "sent|pending|failed"
    }
    """
    try:
        data = request.get_json()
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT INTO production_log (
                ticket_id,
                user_initials,
                entry_type,
                notification_type,
                notification_recipient,
                notification_subject,
                notification_message,
                notification_status,
                notification_sent_at,
                note_text,
                created_by_user
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            ticket_id,
            data.get('user_initials', 'USER'),
            'client_notification',
            data.get('notification_type'),
            data.get('notification_recipient'),
            data.get('notification_subject'),
            data.get('notification_message'),
            data.get('notification_status', 'pending'),
            data.get('notification_sent_at', datetime.now().isoformat()),
            f"{data.get('notification_type', 'Notification')} sent to {data.get('notification_recipient')}",
            data.get('created_by_user')
        ))
        
        log_id = cursor.lastrowid
        conn.commit()
        conn.close()
        
        return jsonify({
            'success': True,
            'log_id': log_id,
            'message': 'Notification logged'
        }), 201
        
    except Exception as e:
        logger.error(f"Failed to log notification: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

# ============================================
# UPDATE OPERATIONS
# ============================================

@production_log_bp.route('/entry/<int:log_id>', methods=['PUT'])
def update_log_entry(log_id: int):
    """
    Edit existing log entry
    
    Body: Fields to update (only note_text, wastage_reason, delay_reason, etc.)
    """
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({
                'success': False,
                'error': 'Request body required'
            }), 400
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Check entry exists
        cursor.execute("SELECT * FROM production_log WHERE log_id = ?", (log_id,))
        if not cursor.fetchone():
            conn.close()
            return jsonify({
                'success': False,
                'error': 'Log entry not found'
            }), 404
        
        # Build update query
        allowed_fields = [
            'note_text', 'wastage_reason', 'delay_reason', 'stock_reason',
            'delay_resolved', 'notification_status'
        ]
        
        updates = []
        values = []
        
        for field in allowed_fields:
            if field in data:
                updates.append(f"{field} = ?")
                values.append(data[field])
        
        if not updates:
            conn.close()
            return jsonify({
                'success': False,
                'error': 'No valid fields to update'
            }), 400
        
        # Add metadata
        updates.append("updated_at = CURRENT_TIMESTAMP")
        updates.append("is_edited = 1")
        
        values.append(log_id)
        
        cursor.execute(f"""
            UPDATE production_log 
            SET {', '.join(updates)}
            WHERE log_id = ?
        """, values)
        
        conn.commit()
        conn.close()
        
        return jsonify({
            'success': True,
            'message': 'Log entry updated'
        }), 200
        
    except Exception as e:
        logger.error(f"Failed to update log entry: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

# ============================================
# DELETE OPERATIONS
# ============================================

@production_log_bp.route('/entry/<int:log_id>', methods=['DELETE'])
def delete_log_entry(log_id: int):
    """Delete log entry (only manual entries, not auto stage changes)"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Check if entry can be deleted (not auto stage change)
        cursor.execute("""
            SELECT entry_type FROM production_log WHERE log_id = ?
        """, (log_id,))
        
        result = cursor.fetchone()
        if not result:
            conn.close()
            return jsonify({
                'success': False,
                'error': 'Log entry not found'
            }), 404
        
        if result[0] == 'stage_change':
            conn.close()
            return jsonify({
                'success': False,
                'error': 'Cannot delete automatic stage change entries'
            }), 403
        
        # Delete entry
        cursor.execute("DELETE FROM production_log WHERE log_id = ?", (log_id,))
        conn.commit()
        conn.close()
        
        return jsonify({
            'success': True,
            'message': 'Log entry deleted'
        }), 200
        
    except Exception as e:
        logger.error(f"Failed to delete log entry: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

# ============================================
# ANALYTICS ENDPOINTS
# ============================================

@production_log_bp.route('/<int:ticket_id>/summary', methods=['GET'])
def get_production_summary(ticket_id: int):
    """Get production log summary with counts by type"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT 
                entry_type,
                COUNT(*) as count
            FROM production_log
            WHERE ticket_id = ?
            GROUP BY entry_type
        """, (ticket_id,))
        
        summary = {}
        for row in cursor.fetchall():
            summary[row[0]] = row[1]
        
        # Get totals
        cursor.execute("""
            SELECT 
                SUM(wastage_amount) as total_wastage,
                SUM(delay_hours) as total_delay_hours,
                COUNT(CASE WHEN notification_status = 'sent' THEN 1 END) as notifications_sent
            FROM production_log
            WHERE ticket_id = ?
        """, (ticket_id,))
        
        totals = cursor.fetchone()
        
        conn.close()
        
        return jsonify({
            'success': True,
            'ticket_id': ticket_id,
            'entry_counts': summary,
            'total_wastage': totals[0] or 0,
            'total_delay_hours': totals[1] or 0,
            'notifications_sent': totals[2] or 0
        }), 200
        
    except Exception as e:
        logger.error(f"Failed to get summary: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

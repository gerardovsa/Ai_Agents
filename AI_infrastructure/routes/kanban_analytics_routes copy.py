"""
FILE: AI_infrastructure/routes/kanban_analytics_routes.py
PURPOSE: REST API endpoints for Kanban Analytics SQLite database

FEATURES:
- Custom analytics queries
- Performance metrics
- Stage transitions tracking
- Customer analytics
- Bottleneck detection
- Custom notes and tags

ENDPOINTS:
    POST   /api/kanban-analytics/sync             - Trigger database sync
    GET    /api/kanban-analytics/jobs             - Get jobs with analytics
    GET    /api/kanban-analytics/jobs/:id         - Get job details with analytics
    POST   /api/kanban-analytics/jobs/:id/notes   - Add custom note
    POST   /api/kanban-analytics/jobs/:id/tags    - Add tag to job
    GET    /api/kanban-analytics/performance/:id  - Get job performance metrics
    POST   /api/kanban-analytics/performance/:id  - Update performance metrics
    GET    /api/kanban-analytics/transitions/:id  - Get stage transition history
    GET    /api/kanban-analytics/bottlenecks      - Get current bottlenecks
    GET    /api/kanban-analytics/customers        - Get customer analytics
    GET    /api/kanban-analytics/tags             - Get available tags
    GET    /api/kanban-analytics/at-risk          - Get at-risk jobs
    GET    /api/kanban-analytics/sync-history     - Get sync history

LAST MODIFIED: 2025-11-06 - Initial creation
"""

from flask import Blueprint, request, jsonify
import sqlite3
import json
from datetime import datetime
from typing import Dict, List, Optional
from pathlib import Path
import logging

# Import sync module
import sys
sys.path.insert(0, str(Path(__file__).parent.parent))
from sync.kanban_db_sync import KanbanDatabaseSync, sync_from_sql_server, get_sync_history

logger = logging.getLogger(__name__)

# Create blueprint
kanban_analytics_bp = Blueprint('kanban_analytics', __name__, url_prefix='/api/kanban-analytics')

# Database path
PROJECT_ROOT = Path(__file__).parent.parent.parent
# DEPRECATED: SQLite path no longer used (keeping for reference)
SQLITE_DB_PATH = PROJECT_ROOT / 'data' / 'kanban_analytics.db'

# Import Supabase connection utility
import sys
sys.path.insert(0, str(Path(__file__).parent.parent))
from shared.database_utils import get_database_connection

def get_db_connection():
    """Get Supabase database connection to kanban_analytics schema"""
    conn = get_database_connection('kanban_analytics')
    if hasattr(conn, 'row_factory'):  # SQLite compatibility
        import sqlite3
        conn.row_factory = sqlite3.Row
    return conn


# ============================================
# SYNC ENDPOINTS
# ============================================

@kanban_analytics_bp.route('/sync', methods=['POST'])
def trigger_sync():
    """
    Trigger database sync from SQL Server
    
    Body:
        sync_type: 'full' or 'incremental' (default: incremental)
    """
    try:
        data = request.get_json() or {}
        sync_type = data.get('sync_type', 'incremental')
        
        full_sync = sync_type == 'full'
        
        logger.info(f"Triggering {sync_type} sync via API...")
        
        result = sync_from_sql_server(full_sync=full_sync)
        
        return jsonify({
            'success': True,
            'sync_type': sync_type,
            'result': result
        }), 200
        
    except Exception as e:
        logger.error(f"Sync failed: {e}", exc_info=True)
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@kanban_analytics_bp.route('/sync-history', methods=['GET'])
def get_sync_history_endpoint():
    """Get sync history"""
    try:
        limit = int(request.args.get('limit', 10))
        history = get_sync_history(limit=limit)
        
        return jsonify({
            'success': True,
            'history': history
        }), 200
        
    except Exception as e:
        logger.error(f"Failed to get sync history: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


# ============================================
# JOB ENDPOINTS WITH ANALYTICS
# ============================================

@kanban_analytics_bp.route('/jobs', methods=['GET'])
def get_jobs_with_analytics():
    """
    Get jobs with analytics data
    
    Query params:
        stage_id: Filter by stage
        priority: Filter by priority label
        has_notes: Filter jobs with custom notes (true/false)
        has_tags: Filter jobs with tags (true/false)
        limit: Max results (default: 100)
    """
    try:
        stage_id = request.args.get('stage_id')
        priority = request.args.get('priority')
        has_notes = request.args.get('has_notes') == 'true'
        has_tags = request.args.get('has_tags') == 'true'
        limit = int(request.args.get('limit', 100))
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Build query
        query = """
            SELECT 
                jt.*,
                jp.quality_score,
                jp.actual_hours,
                jp.on_time_delivery,
                jp.customer_satisfaction,
                jp.profit_margin,
                (SELECT COUNT(*) FROM custom_job_notes WHERE ticket_id = jt.ticket_id AND resolved = 0) as open_notes,
                (SELECT GROUP_CONCAT(ct.tag_name, ', ') FROM job_tags jts 
                 JOIN custom_tags ct ON jts.tag_id = ct.tag_id 
                 WHERE jts.ticket_id = jt.ticket_id) as tags
            FROM job_tickets jt
            LEFT JOIN job_performance jp ON jt.ticket_id = jp.ticket_id
            WHERE 1=1
        """
        
        params = []
        
        if stage_id:
            query += " AND jt.stage_id = %s"
            params.append(int(stage_id))
        
        if priority:
            query += " AND jt.priority_label = %s"
            params.append(priority)
        
        if has_notes:
            query += " AND EXISTS (SELECT 1 FROM custom_job_notes WHERE ticket_id = jt.ticket_id)"
        
        if has_tags:
            query += " AND EXISTS (SELECT 1 FROM job_tags WHERE ticket_id = jt.ticket_id)"
        
        query += " ORDER BY jt.ai_priority_score DESC LIMIT %s"
        params.append(limit)
        
        cursor.execute(query, params)
        
        jobs = [dict(row) for row in cursor.fetchall()]
        conn.close()
        
        return jsonify({
            'success': True,
            'count': len(jobs),
            'jobs': jobs
        }), 200
        
    except Exception as e:
        logger.error(f"Failed to get jobs: {e}", exc_info=True)
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@kanban_analytics_bp.route('/jobs/<int:ticket_id>', methods=['GET'])
def get_job_details(ticket_id: int):
    """Get complete job details with all analytics"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Get job with performance
        cursor.execute("""
            SELECT jt.*, jp.*
            FROM job_tickets jt
            LEFT JOIN job_performance jp ON jt.ticket_id = jp.ticket_id
            WHERE jt.ticket_id = %s
        """, (ticket_id,))
        
        job = cursor.fetchone()
        if not job:
            return jsonify({
                'success': False,
                'error': 'Job not found'
            }), 404
        
        job_dict = dict(job)
        
        # Get notes
        cursor.execute("""
            SELECT * FROM custom_job_notes
            WHERE ticket_id = %s
            ORDER BY created_at DESC
        """, (ticket_id,))
        job_dict['notes'] = [dict(row) for row in cursor.fetchall()]
        
        # Get tags
        cursor.execute("""
            SELECT ct.*, jts.assigned_at
            FROM job_tags jts
            JOIN custom_tags ct ON jts.tag_id = ct.tag_id
            WHERE jts.ticket_id = %s
        """, (ticket_id,))
        job_dict['tags'] = [dict(row) for row in cursor.fetchall()]
        
        # Get transition history
        cursor.execute("""
            SELECT st.*, js.stage_description
            FROM stage_transitions st
            JOIN job_stages js ON st.to_stage_id = js.stage_id
            WHERE st.ticket_id = %s
            ORDER BY st.transition_date DESC
        """, (ticket_id,))
        job_dict['transition_history'] = [dict(row) for row in cursor.fetchall()]
        
        # Get AI predictions
        cursor.execute("""
            SELECT * FROM ai_predictions
            WHERE ticket_id = %s
            ORDER BY predicted_at DESC
            LIMIT 1
        """, (ticket_id,))
        prediction = cursor.fetchone()
        job_dict['ai_prediction'] = dict(prediction) if prediction else None
        
        conn.close()
        
        return jsonify({
            'success': True,
            'job': job_dict
        }), 200
        
    except Exception as e:
        logger.error(f"Failed to get job details: {e}", exc_info=True)
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


# ============================================
# CUSTOM NOTES
# ============================================

@kanban_analytics_bp.route('/jobs/<int:ticket_id>/notes', methods=['POST'])
def add_job_note(ticket_id: int):
    """
    Add custom note to job
    
    Body:
        note_text: Note content (required)
        note_type: Type (issue, reminder, quality, customer_request)
        priority: Priority level (low, medium, high, critical)
        created_by: User who created note
    """
    try:
        data = request.get_json()
        
        if not data or 'note_text' not in data:
            return jsonify({
                'success': False,
                'error': 'note_text required'
            }), 400
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT INTO custom_job_notes (ticket_id, note_text, note_type, priority, created_by)
            VALUES (%s, %s, %s, %s, %s)
        """, (
            ticket_id,
            data['note_text'],
            data.get('note_type', 'general'),
            data.get('priority', 'medium'),
            data.get('created_by', 'system')
        ))
        
        note_id = cursor.lastrowid
        conn.commit()
        conn.close()
        
        return jsonify({
            'success': True,
            'note_id': note_id
        }), 201
        
    except Exception as e:
        logger.error(f"Failed to add note: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@kanban_analytics_bp.route('/jobs/<int:ticket_id>/notes/<int:note_id>/resolve', methods=['PUT'])
def resolve_note(ticket_id: int, note_id: int):
    """Mark note as resolved"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            UPDATE custom_job_notes
            SET resolved = 1, resolved_at = CURRENT_TIMESTAMP
            WHERE note_id = %s AND ticket_id = %s
        """, (note_id, ticket_id))
        
        conn.commit()
        conn.close()
        
        return jsonify({
            'success': True
        }), 200
        
    except Exception as e:
        logger.error(f"Failed to resolve note: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


# ============================================
# TAGS
# ============================================

@kanban_analytics_bp.route('/tags', methods=['GET'])
def get_tags():
    """Get all available tags"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute("SELECT * FROM custom_tags ORDER BY tag_category, tag_name")
        tags = [dict(row) for row in cursor.fetchall()]
        
        conn.close()
        
        return jsonify({
            'success': True,
            'tags': tags
        }), 200
        
    except Exception as e:
        logger.error(f"Failed to get tags: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@kanban_analytics_bp.route('/jobs/<int:ticket_id>/tags', methods=['POST'])
def add_job_tag(ticket_id: int):
    """
    Add tag to job
    
    Body:
        tag_id: Tag ID (required)
        assigned_by: User who assigned tag
    """
    try:
        data = request.get_json()
        
        if not data or 'tag_id' not in data:
            return jsonify({
                'success': False,
                'error': 'tag_id required'
            }), 400
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT OR IGNORE INTO job_tags (ticket_id, tag_id, assigned_by)
            VALUES (%s, %s, %s)
        """, (ticket_id, data['tag_id'], data.get('assigned_by', 'system')))
        
        conn.commit()
        conn.close()
        
        return jsonify({
            'success': True
        }), 201
        
    except Exception as e:
        logger.error(f"Failed to add tag: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@kanban_analytics_bp.route('/jobs/<int:ticket_id>/tags/<int:tag_id>', methods=['DELETE'])
def remove_job_tag(ticket_id: int, tag_id: int):
    """Remove tag from job"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            DELETE FROM job_tags
            WHERE ticket_id = %s AND tag_id = %s
        """, (ticket_id, tag_id))
        
        conn.commit()
        conn.close()
        
        return jsonify({
            'success': True
        }), 200
        
    except Exception as e:
        logger.error(f"Failed to remove tag: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


# ============================================
# PERFORMANCE METRICS
# ============================================

@kanban_analytics_bp.route('/performance/<int:ticket_id>', methods=['GET'])
def get_performance_metrics(ticket_id: int):
    """Get performance metrics for job"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT * FROM job_performance
            WHERE ticket_id = %s
        """, (ticket_id,))
        
        performance = cursor.fetchone()
        conn.close()
        
        if not performance:
            return jsonify({
                'success': False,
                'error': 'No performance data found'
            }), 404
        
        return jsonify({
            'success': True,
            'performance': dict(performance)
        }), 200
        
    except Exception as e:
        logger.error(f"Failed to get performance: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@kanban_analytics_bp.route('/performance/<int:ticket_id>', methods=['POST', 'PUT'])
def update_performance_metrics(ticket_id: int):
    """
    Update performance metrics for job
    
    Body: Any fields from job_performance table
    """
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({
                'success': False,
                'error': 'No data provided'
            }), 400
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Build update query
        fields = []
        values = []
        
        for field in ['estimated_hours', 'actual_hours', 'setup_time_hours', 'production_time_hours',
                      'finishing_time_hours', 'quality_score', 'rework_required', 'rework_hours',
                      'defect_count', 'material_waste_percentage', 'on_time_delivery',
                      'customer_satisfaction', 'material_cost', 'labor_cost', 'overhead_cost',
                      'total_actual_cost', 'profit_margin', 'recorded_by']:
            if field in data:
                fields.append(f"{field} = %s")
                values.append(data[field])
        
        if not fields:
            return jsonify({
                'success': False,
                'error': 'No valid fields provided'
            }), 400
        
        # Check if record exists
        cursor.execute("SELECT performance_id FROM job_performance WHERE ticket_id = %s", (ticket_id,))
        existing = cursor.fetchone()
        
        if existing:
            # Update existing
            query = f"UPDATE job_performance SET {', '.join(fields)}, updated_at = CURRENT_TIMESTAMP WHERE ticket_id = %s"
            values.append(ticket_id)
            cursor.execute(query, values)
        else:
            # Insert new
            fields.append('ticket_id')
            values.append(ticket_id)
            placeholders = ', '.join(['%s' for _ in values])
            query = f"INSERT INTO job_performance ({', '.join(fields).replace(' = %s', '')}) VALUES ({placeholders})"
            cursor.execute(query, values)
        
        conn.commit()
        conn.close()
        
        return jsonify({
            'success': True
        }), 200
        
    except Exception as e:
        logger.error(f"Failed to update performance: {e}", exc_info=True)
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


# ============================================
# ANALYTICS ENDPOINTS
# ============================================

@kanban_analytics_bp.route('/bottlenecks', methods=['GET'])
def get_bottlenecks():
    """Get current stage bottlenecks"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT * FROM v_current_bottlenecks
        """)
        
        bottlenecks = [dict(row) for row in cursor.fetchall()]
        conn.close()
        
        return jsonify({
            'success': True,
            'bottlenecks': bottlenecks
        }), 200
        
    except Exception as e:
        logger.error(f"Failed to get bottlenecks: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@kanban_analytics_bp.route('/at-risk', methods=['GET'])
def get_at_risk_jobs():
    """Get jobs at risk of delays or quality issues"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT * FROM v_jobs_at_risk
        """)
        
        jobs = [dict(row) for row in cursor.fetchall()]
        conn.close()
        
        return jsonify({
            'success': True,
            'count': len(jobs),
            'jobs': jobs
        }), 200
        
    except Exception as e:
        logger.error(f"Failed to get at-risk jobs: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@kanban_analytics_bp.route('/customers', methods=['GET'])
def get_customer_analytics():
    """Get customer performance analytics"""
    try:
        limit = int(request.args.get('limit', 50))
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT * FROM v_customer_summary
            ORDER BY total_value DESC
            LIMIT %s
        """, (limit,))
        
        customers = [dict(row) for row in cursor.fetchall()]
        conn.close()
        
        return jsonify({
            'success': True,
            'count': len(customers),
            'customers': customers
        }), 200
        
    except Exception as e:
        logger.error(f"Failed to get customer analytics: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@kanban_analytics_bp.route('/transitions/<int:ticket_id>', methods=['GET'])
def get_stage_transitions(ticket_id: int):
    """Get stage transition history for job"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT 
                st.*,
                js_from.stage_description as from_stage_name,
                js_to.stage_description as to_stage_name
            FROM stage_transitions st
            LEFT JOIN job_stages js_from ON st.from_stage_id = js_from.stage_id
            JOIN job_stages js_to ON st.to_stage_id = js_to.stage_id
            WHERE st.ticket_id = %s
            ORDER BY st.transition_date ASC
        """, (ticket_id,))
        
        transitions = [dict(row) for row in cursor.fetchall()]
        conn.close()
        
        return jsonify({
            'success': True,
            'count': len(transitions),
            'transitions': transitions
        }), 200
        
    except Exception as e:
        logger.error(f"Failed to get transitions: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


# ============================================
# HEALTH CHECK
# ============================================

@kanban_analytics_bp.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Check database
        cursor.execute("SELECT COUNT(*) FROM job_tickets")
        job_count = cursor.fetchone()[0]
        
        # Get last sync
        cursor.execute("SELECT sync_end, sync_status FROM sync_history ORDER BY sync_id DESC LIMIT 1")
        last_sync = cursor.fetchone()
        
        conn.close()
        
        return jsonify({
            'status': 'healthy',
            'database': 'connected',
            'database_path': str(SQLITE_DB_PATH),
            'job_count': job_count,
            'last_sync': dict(last_sync) if last_sync else None
        }), 200
        
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return jsonify({
            'status': 'unhealthy',
            'error': str(e)
        }), 500


if __name__ == '__main__':
    print("Kanban Analytics Routes Blueprint")
    print(f"Database: {SQLITE_DB_PATH}")
    print("\nAvailable endpoints:")
    for rule in kanban_analytics_bp.url_map.iter_rules():
        print(f"  {rule.methods} {rule.rule}")

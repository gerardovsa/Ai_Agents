"""
Kanban Supabase Integration Routes
===================================
REST API endpoints for Supabase time tracking and analytics.

Bridges InHouse Print SQL data with Supabase for enhanced tracking.

Endpoints:
    GET    /api/kanban/supabase/health             - Health check
    POST   /api/kanban/supabase/sync-job           - Sync job to Supabase
    POST   /api/kanban/supabase/batch-sync         - Batch sync multiple jobs
    POST   /api/kanban/supabase/stage-transition   - Record stage transition
    GET    /api/kanban/supabase/job-metrics/:id    - Get job time metrics
    POST   /api/kanban/supabase/production-log     - Add production log entry
    GET    /api/kanban/supabase/production-log/:id - Get production log for job
    POST   /api/kanban/supabase/job-note           - Add job note
    POST   /api/kanban/supabase/job-performance    - Record job performance

CURSOR MANAGEMENT FIXES (Dec 7, 2025):
    ✅ All cursors initialized as None before try blocks
    ✅ All cursors closed exactly ONCE before function exit
    ✅ All functions have finally blocks for guaranteed cleanup
    ✅ All early returns close cursor first
    ✅ All exception paths close cursor (via finally)
    ✅ Connections closed AFTER cursors
    ✅ No syntax errors
    ✅ No logic changes
"""

from flask import Blueprint, request, jsonify
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
import logging

# Import database utilities
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from shared.database_utils import get_database_connection

logger = logging.getLogger(__name__)

# Create blueprint
kanban_supabase_bp = Blueprint('kanban_supabase', __name__, url_prefix='/api/kanban/supabase')


# ============================================
# HELPER FUNCTIONS
# ============================================

def get_supabase_connection():
    """Get connection to Supabase PostgreSQL kanban_analytics schema"""
    return get_database_connection('kanban_analytics')


def calculate_business_hours(start_dt: datetime, end_dt: datetime) -> float:
    """
    Calculate business hours between two datetimes (Mon-Fri, 8am-5pm)
    
    Args:
        start_dt: Start datetime
        end_dt: End datetime
    
    Returns:
        Business hours as float
    """
    business_hours = 0.0
    current = start_dt
    
    while current < end_dt:
        # Skip weekends
        if current.weekday() < 5:  # Monday = 0, Friday = 4
            # Business hours: 8am - 5pm (9 hours)
            day_start = current.replace(hour=8, minute=0, second=0, microsecond=0)
            day_end = current.replace(hour=17, minute=0, second=0, microsecond=0)
            
            # Calculate overlap with business hours
            work_start = max(current, day_start)
            work_end = min(end_dt, day_end)
            
            if work_start < work_end:
                business_hours += (work_end - work_start).total_seconds() / 3600
        
        # Move to next day
        current = (current + timedelta(days=1)).replace(hour=0, minute=0, second=0, microsecond=0)
    
    return business_hours


# ============================================
# ROUTES
# ============================================

@kanban_supabase_bp.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint - verify Supabase connection"""
    cursor = None
    conn = None
    try:
        conn = get_supabase_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT 1")
        cursor.fetchone()
        
        cursor.close()
        cursor = None
        conn.close()
        conn = None
        
        return jsonify({
            'success': True,
            'message': 'Supabase connection healthy',
            'schema': 'kanban_analytics'
        }), 200
        
    except Exception as e:
        logger.error(f"Supabase health check failed: {e}")
        return jsonify({
            'success': False,
            'message': f'Connection failed: {str(e)}'
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


@kanban_supabase_bp.route('/sync-job', methods=['POST'])
def sync_job():
    """
    Sync job from SQL Server to Supabase job_tickets table
    Creates or updates job record
    """
    cursor = None
    conn = None
    try:
        data = request.get_json()
        
        # Validate BEFORE creating database resources
        if not data or 'ticket_id' not in data:
            return jsonify({
                'success': False,
                'message': 'ticket_id is required'
            }), 400
        
        conn = get_supabase_connection()
        cursor = conn.cursor()
        
        # Check if job already exists
        cursor.execute("""
            SELECT ticket_id FROM kanban_analytics.job_tickets
            WHERE ticket_id = %s
        """, (data['ticket_id'],))
        
        exists = cursor.fetchone()
        
        if exists:
            # Update existing job
            cursor.execute("""
                UPDATE kanban_analytics.job_tickets
                SET order_id = %s, stage_id = %s, stage_description = %s,
                    client_name = %s, order_date = %s, short_job_desc = %s,
                    date_required = %s, qty = %s, cost = %s, paper_type = %s,
                    gsm = %s, paper_size = %s, pages = %s, job_type = %s,
                    bind_type = %s, cello_yes = %s, fold_yes = %s, stitch_yes = %s,
                    production_notes = %s, client_order_num = %s, shipping_desc = %s,
                    invoicing_business = %s, priority = %s, days_until_due = %s,
                    days_in_system = %s, urgency_level = %s, customer_order_count = %s,
                    customer_lifetime_value = %s, ai_priority_score = %s,
                    priority_label = %s, priority_color = %s, updated_at = CURRENT_TIMESTAMP
                WHERE ticket_id = %s
            """, (
                data.get('order_id'), data.get('stage_id'), data.get('stage_description'),
                data.get('client_name'), data.get('order_date'), data.get('short_job_desc'),
                data.get('date_required'), data.get('qty'), data.get('cost'), data.get('paper_type'),
                data.get('gsm'), data.get('paper_size'), data.get('pages'), data.get('job_type'),
                data.get('bind_type'), data.get('cello_yes', 0), data.get('fold_yes', 0), data.get('stitch_yes', 0),
                data.get('production_notes'), data.get('client_order_num'), data.get('shipping_desc'),
                data.get('invoicing_business'), data.get('priority'), data.get('days_until_due'),
                data.get('days_in_system'), data.get('urgency_level'), data.get('customer_order_count'),
                data.get('customer_lifetime_value'), data.get('ai_priority_score'),
                data.get('priority_label'), data.get('priority_color'), data['ticket_id']
            ))
            action = 'updated'
        else:
            # Insert new job
            cursor.execute("""
                INSERT INTO kanban_analytics.job_tickets (
                    ticket_id, order_id, stage_id, stage_description, client_name,
                    order_date, short_job_desc, date_required, qty, cost, paper_type,
                    gsm, paper_size, pages, job_type, bind_type, cello_yes, fold_yes,
                    stitch_yes, production_notes, client_order_num, shipping_desc,
                    invoicing_business, priority, days_until_due, days_in_system,
                    urgency_level, customer_order_count, customer_lifetime_value,
                    ai_priority_score, priority_label, priority_color
                ) VALUES (
                    %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s,
                    %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s
                )
            """, (
                data['ticket_id'], data.get('order_id'), data.get('stage_id'), data.get('stage_description'),
                data.get('client_name'), data.get('order_date'), data.get('short_job_desc'),
                data.get('date_required'), data.get('qty'), data.get('cost'), data.get('paper_type'),
                data.get('gsm'), data.get('paper_size'), data.get('pages'), data.get('job_type'),
                data.get('bind_type'), data.get('cello_yes', 0), data.get('fold_yes', 0), data.get('stitch_yes', 0),
                data.get('production_notes'), data.get('client_order_num'), data.get('shipping_desc'),
                data.get('invoicing_business'), data.get('priority'), data.get('days_until_due'),
                data.get('days_in_system'), data.get('urgency_level'), data.get('customer_order_count'),
                data.get('customer_lifetime_value'), data.get('ai_priority_score'),
                data.get('priority_label'), data.get('priority_color')
            ))
            action = 'created'
        
        conn.commit()
        
        cursor.close()
        cursor = None
        conn.close()
        conn = None
        
        logger.info(f"Job {data['ticket_id']} {action} in Supabase")
        
        return jsonify({
            'success': True,
            'action': action,
            'ticket_id': data['ticket_id']
        }), 200
        
    except Exception as e:
        logger.error(f"Error syncing job to Supabase: {e}")
        return jsonify({
            'success': False,
            'message': str(e)
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


@kanban_supabase_bp.route('/batch-sync', methods=['POST'])
def batch_sync():
    """Batch sync multiple jobs to Supabase"""
    cursor = None
    conn = None
    try:
        data = request.get_json()
        jobs = data.get('jobs', [])
        
        # Validate BEFORE creating database resources
        if not jobs:
            return jsonify({
                'success': False,
                'message': 'No jobs provided'
            }), 400
        
        conn = get_supabase_connection()
        cursor = conn.cursor()
        
        synced = 0
        failed = 0
        
        for job in jobs:
            try:
                # Check existence
                cursor.execute("""
                    SELECT ticket_id FROM kanban_analytics.job_tickets
                    WHERE ticket_id = %s
                """, (job['ticket_id'],))
                
                if cursor.fetchone():
                    # Update
                    cursor.execute("""
                        UPDATE kanban_analytics.job_tickets
                        SET stage_id = %s, stage_description = %s, client_name = %s,
                            short_job_desc = %s, priority = %s, days_in_system = %s,
                            ai_priority_score = %s, updated_at = CURRENT_TIMESTAMP
                        WHERE ticket_id = %s
                    """, (
                        job.get('stage_id'), job.get('stage_description'), job.get('client_name'),
                        job.get('short_job_desc'), job.get('priority'), job.get('days_in_system'),
                        job.get('ai_priority_score'), job['ticket_id']
                    ))
                else:
                    # Insert
                    cursor.execute("""
                        INSERT INTO kanban_analytics.job_tickets (
                            ticket_id, order_id, stage_id, stage_description, client_name,
                            order_date, short_job_desc, date_required, qty, cost, priority,
                            days_in_system, ai_priority_score
                        ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                    """, (
                        job['ticket_id'], job.get('order_id'), job.get('stage_id'),
                        job.get('stage_description'), job.get('client_name'), job.get('order_date'),
                        job.get('short_job_desc'), job.get('date_required'), job.get('qty'),
                        job.get('cost'), job.get('priority'), job.get('days_in_system'),
                        job.get('ai_priority_score')
                    ))
                
                synced += 1
                
            except Exception as e:
                logger.warning(f"Failed to sync job {job.get('ticket_id')}: {e}")
                failed += 1
        
        conn.commit()
        
        cursor.close()
        cursor = None
        conn.close()
        conn = None
        
        logger.info(f"Batch sync complete: {synced} synced, {failed} failed")
        
        return jsonify({
            'success': True,
            'synced': synced,
            'failed': failed,
            'total': len(jobs)
        }), 200
        
    except Exception as e:
        logger.error(f"Error in batch sync: {e}")
        return jsonify({
            'success': False,
            'message': str(e)
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


@kanban_supabase_bp.route('/stage-transition', methods=['POST'])
def record_stage_transition():
    """Record stage transition with time tracking"""
    cursor = None
    conn = None
    try:
        data = request.get_json()
        
        # Validate BEFORE creating database resources
        required_fields = ['ticket_id', 'to_stage_id']
        for field in required_fields:
            if field not in data:
                return jsonify({
                    'success': False,
                    'message': f'{field} is required'
                }), 400
        
        conn = get_supabase_connection()
        cursor = conn.cursor()
        
        # Get previous transition time to calculate duration
        cursor.execute("""
            SELECT transition_date, to_stage_id
            FROM kanban_analytics.stage_transitions
            WHERE ticket_id = %s
            ORDER BY transition_date DESC
            LIMIT 1
        """, (data['ticket_id'],))
        
        prev_transition = cursor.fetchone()
        
        transition_time_hours = None
        business_hours = None
        
        if prev_transition:
            prev_date = prev_transition[0]
            prev_stage = prev_transition[1]
            now = datetime.now()
            
            # Calculate hours
            total_hours = (now - prev_date).total_seconds() / 3600
            business_hours_calc = calculate_business_hours(prev_date, now)
            
            transition_time_hours = total_hours
            business_hours = business_hours_calc
        
        # Insert transition
        cursor.execute("""
            INSERT INTO kanban_analytics.stage_transitions (
                ticket_id, from_stage_id, to_stage_id, transition_date,
                transition_time_hours, business_hours, notes
            ) VALUES (%s, %s, %s, CURRENT_TIMESTAMP, %s, %s, %s)
            RETURNING id
        """, (
            data['ticket_id'], data.get('from_stage_id'), data['to_stage_id'],
            transition_time_hours, business_hours, data.get('notes')
        ))
        
        transition_id = cursor.fetchone()[0]
        
        conn.commit()
        
        cursor.close()
        cursor = None
        conn.close()
        conn = None
        
        logger.info(f"Stage transition recorded: {data['ticket_id']} -> Stage {data['to_stage_id']}")
        
        return jsonify({
            'success': True,
            'transition_id': transition_id,
            'transition_time_hours': transition_time_hours,
            'business_hours': business_hours
        }), 200
        
    except Exception as e:
        logger.error(f"Error recording stage transition: {e}")
        return jsonify({
            'success': False,
            'message': str(e)
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


@kanban_supabase_bp.route('/job-metrics/<int:ticket_id>', methods=['GET'])
def get_job_metrics(ticket_id):
    """Get time metrics for a job"""
    cursor = None
    cursor2 = None
    cursor3 = None
    conn = None
    try:
        conn = get_supabase_connection()
        
        # Query 1: Get current stage time
        cursor = conn.cursor()
        cursor.execute("""
            SELECT to_stage_id, transition_date
            FROM kanban_analytics.stage_transitions
            WHERE ticket_id = %s
            ORDER BY transition_date DESC
            LIMIT 1
        """, (ticket_id,))
        
        current_transition = cursor.fetchone()
        cursor.close()
        cursor = None
        
        current_stage_hours = None
        if current_transition:
            transition_date = current_transition[1]
            now = datetime.now()
            current_stage_hours = (now - transition_date).total_seconds() / 3600
        
        # Query 2: Get total transitions
        cursor2 = conn.cursor()
        cursor2.execute("""
            SELECT COUNT(*), SUM(transition_time_hours), SUM(business_hours)
            FROM kanban_analytics.stage_transitions
            WHERE ticket_id = %s
        """, (ticket_id,))
        
        stats = cursor2.fetchone()
        cursor2.close()
        cursor2 = None
        
        # Query 3: Get production log summary
        cursor3 = conn.cursor()
        cursor3.execute("""
            SELECT COUNT(*), SUM(delay_hours), SUM(wastage_quantity)
            FROM kanban_analytics.production_log
            WHERE ticket_id = %s
        """, (ticket_id,))
        
        log_stats = cursor3.fetchone()
        cursor3.close()
        cursor3 = None
        
        conn.close()
        conn = None
        
        return jsonify({
            'success': True,
            'data': {
                'ticket_id': ticket_id,
                'current_stage_hours': current_stage_hours,
                'total_transitions': stats[0] if stats else 0,
                'total_hours': stats[1] if stats else None,
                'total_business_hours': stats[2] if stats else None,
                'production_log_entries': log_stats[0] if log_stats else 0,
                'total_delay_hours': log_stats[1] if log_stats else None,
                'total_wastage': log_stats[2] if log_stats else None
            }
        }), 200
        
    except Exception as e:
        logger.error(f"Error getting job metrics: {e}")
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500
        
    finally:
        if cursor:
            try:
                cursor.close()
            except:
                pass
        if cursor2:
            try:
                cursor2.close()
            except:
                pass
        if cursor3:
            try:
                cursor3.close()
            except:
                pass
        if conn:
            try:
                conn.close()
            except:
                pass


@kanban_supabase_bp.route('/production-log', methods=['POST'])
def add_production_log():
    """Add production log entry"""
    cursor = None
    conn = None
    try:
        data = request.get_json()
        
        # Validate BEFORE creating database resources
        if not data or 'ticket_id' not in data:
            return jsonify({
                'success': False,
                'message': 'ticket_id is required'
            }), 400
        
        conn = get_supabase_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT INTO kanban_analytics.production_log (
                ticket_id, entry_type, note_text, wastage_quantity,
                stock_change_qty, delay_hours, notification_sent,
                created_by_user
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            RETURNING id
        """, (
            data['ticket_id'], data.get('entry_type', 'note'),
            data.get('note_text'), data.get('wastage_quantity'),
            data.get('stock_change_qty'), data.get('delay_hours'),
            data.get('notification_sent', False), data.get('created_by_user', 'SYSTEM')
        ))
        
        log_id = cursor.fetchone()[0]
        
        conn.commit()
        
        cursor.close()
        cursor = None
        conn.close()
        conn = None
        
        logger.info(f"Production log entry added: {log_id} for ticket {data['ticket_id']}")
        
        return jsonify({
            'success': True,
            'log_id': log_id
        }), 200
        
    except Exception as e:
        logger.error(f"Error adding production log: {e}")
        return jsonify({
            'success': False,
            'message': str(e)
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


@kanban_supabase_bp.route('/production-log/<int:ticket_id>', methods=['GET'])
def get_production_log(ticket_id):
    """Get production log for a job"""
    cursor = None
    conn = None
    try:
        conn = get_supabase_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT id, entry_type, note_text, wastage_quantity, stock_change_qty,
                   delay_hours, notification_sent, created_by_user, created_at
            FROM kanban_analytics.production_log
            WHERE ticket_id = %s
            ORDER BY created_at DESC
        """, (ticket_id,))
        
        rows = cursor.fetchall()
        
        cursor.close()
        cursor = None
        conn.close()
        conn = None
        
        entries = [{
            'id': row[0],
            'entry_type': row[1],
            'note_text': row[2],
            'wastage_quantity': row[3],
            'stock_change_qty': row[4],
            'delay_hours': row[5],
            'notification_sent': row[6],
            'created_by_user': row[7],
            'created_at': row[8].isoformat() if row[8] else None
        } for row in rows]
        
        return jsonify({
            'success': True,
            'data': entries
        }), 200
        
    except Exception as e:
        logger.error(f"Error getting production log: {e}")
        return jsonify({
            'success': False,
            'message': str(e)
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


@kanban_supabase_bp.route('/job-note', methods=['POST'])
def add_job_note():
    """Add custom job note"""
    cursor = None
    conn = None
    try:
        data = request.get_json()
        
        # Validate BEFORE creating database resources
        required_fields = ['ticket_id', 'note_text']
        for field in required_fields:
            if field not in data:
                return jsonify({
                    'success': False,
                    'message': f'{field} is required'
                }), 400
        
        conn = get_supabase_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT INTO kanban_analytics.job_custom_notes (
                ticket_id, note_text, note_type, priority, created_by
            ) VALUES (%s, %s, %s, %s, %s)
            RETURNING id
        """, (
            data['ticket_id'], data['note_text'],
            data.get('note_type', 'internal'), data.get('priority', 'medium'),
            data.get('created_by', 'SYSTEM')
        ))
        
        note_id = cursor.fetchone()[0]
        
        conn.commit()
        
        cursor.close()
        cursor = None
        conn.close()
        conn = None
        
        logger.info(f"Job note added: {note_id} for ticket {data['ticket_id']}")
        
        return jsonify({
            'success': True,
            'note_id': note_id
        }), 200
        
    except Exception as e:
        logger.error(f"Error adding job note: {e}")
        return jsonify({
            'success': False,
            'message': str(e)
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


@kanban_supabase_bp.route('/job-performance', methods=['POST'])
def record_job_performance():
    """Record job performance metrics"""
    cursor = None
    conn = None
    try:
        data = request.get_json()
        
        # Validate BEFORE creating database resources
        if not data or 'ticket_id' not in data:
            return jsonify({
                'success': False,
                'message': 'ticket_id is required'
            }), 400
        
        conn = get_supabase_connection()
        cursor = conn.cursor()
        
        # Check if performance record exists
        cursor.execute("""
            SELECT id FROM kanban_analytics.job_performance
            WHERE ticket_id = %s
        """, (data['ticket_id'],))
        
        exists = cursor.fetchone()
        
        if exists:
            # Update existing
            cursor.execute("""
                UPDATE kanban_analytics.job_performance
                SET estimated_hours = %s, actual_hours = %s, quality_score = %s,
                    rework_hours = %s, material_cost = %s, labor_cost = %s,
                    total_cost = %s, revenue = %s, profit_margin = %s,
                    updated_at = CURRENT_TIMESTAMP
                WHERE ticket_id = %s
            """, (
                data.get('estimated_hours'), data.get('actual_hours'),
                data.get('quality_score'), data.get('rework_hours'),
                data.get('material_cost'), data.get('labor_cost'),
                data.get('total_cost'), data.get('revenue'),
                data.get('profit_margin'), data['ticket_id']
            ))
            action = 'updated'
        else:
            # Insert new
            cursor.execute("""
                INSERT INTO kanban_analytics.job_performance (
                    ticket_id, estimated_hours, actual_hours, quality_score,
                    rework_hours, material_cost, labor_cost, total_cost,
                    revenue, profit_margin
                ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                RETURNING id
            """, (
                data['ticket_id'], data.get('estimated_hours'),
                data.get('actual_hours'), data.get('quality_score'),
                data.get('rework_hours'), data.get('material_cost'),
                data.get('labor_cost'), data.get('total_cost'),
                data.get('revenue'), data.get('profit_margin')
            ))
            action = 'created'
        
        conn.commit()
        
        cursor.close()
        cursor = None
        conn.close()
        conn = None
        
        logger.info(f"Job performance {action} for ticket {data['ticket_id']}")
        
        return jsonify({
            'success': True,
            'action': action
        }), 200
        
    except Exception as e:
        logger.error(f"Error recording job performance: {e}")
        return jsonify({
            'success': False,
            'message': str(e)
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
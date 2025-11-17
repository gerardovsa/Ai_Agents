"""
Automation Visual Workflows API Routes
=======================================
REST API endpoints for visual automation canvas and AI-interpreted workflows.

Endpoints:
    POST   /api/automation/parse            - Parse visual flow and interpret intent
    POST   /api/automation/refine           - AI refines user's workflow  
    POST   /api/automation/save             - Save automation to database
    GET    /api/automation/list             - List user's automations
    GET    /api/automation/<id>             - Get automation details
    DELETE /api/automation/<id>             - Delete automation
    POST   /api/automation/<id>/activate    - Schedule automation
    POST   /api/automation/<id>/deactivate  - Unschedule automation
    GET    /api/automation/<id>/history     - Get execution history
    GET    /api/automation/<id>/export      - Export for canvas rendering
"""

from flask import Blueprint, request, jsonify
from datetime import datetime
import json
import sys
from pathlib import Path
import os

# Add parent directory for imports
sys.path.insert(0, str(Path(__file__).parent.parent))
from scheduler import get_scheduler
from shared.database_utils import get_database_connection

automation_bp = Blueprint('automation', __name__, url_prefix='/api/automation')


def get_db_connection():
    """
    Get database connection using centralized utility (supports Supabase + SQLite)
    Uses centralized database_utils for automatic environment detection
    
    Returns:
        Database connection with row_factory for dict-like access
    """
    conn = get_database_connection('ai_infrastructure')
    return conn


def init_automation_tables():
    """
    Initialize database tables for visual automations
    
    For PostgreSQL (Supabase):
        Tables should be created via migration file: supabase_migrations/004_automation_tables.sql
        This function only validates table existence.
    
    For SQLite (local):
        Creates tables if they don't exist.
    
    Tables:
    - visual_automations: Stores automation metadata and visual flow JSON
    - automation_executions: Tracks execution history and results
    """
    try:
        conn = get_database_connection('ai_infrastructure')
        cursor = conn.cursor()
        
        # Check if we're using PostgreSQL or SQLite
        from shared.database_utils import is_using_supabase
        if is_using_supabase():
            # PostgreSQL - tables created via migration, just validate
            # Check if tables exist
            cursor.execute("""
                SELECT EXISTS (
                    SELECT 1 FROM information_schema.tables 
                    WHERE table_name = 'visual_automations'
                )
            """)
            result = cursor.fetchone()
            exists = result['exists'] if isinstance(result, dict) else result[0]
            
            conn.close()
            
            if not exists:
                print("⚠️  WARNING: visual_automations table not found in PostgreSQL")
                print("   Run migration: supabase_migrations/004_automation_tables.sql")
            else:
                print("✅ Automation tables exist in PostgreSQL")
            
            return
        
        # SQLite - create tables if they don't exist
        # Visual automations table (SQLite version)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS visual_automations (
                automation_id TEXT PRIMARY KEY,
                user_id INTEGER NOT NULL,
                title TEXT NOT NULL,
                slug TEXT NOT NULL UNIQUE,
                description TEXT,
                category TEXT DEFAULT 'other',
                ui_json TEXT NOT NULL DEFAULT '{}',
                execution_json TEXT NOT NULL DEFAULT '{}',
                schedule_cron TEXT,
                schedule_datetime TEXT,
                timezone TEXT DEFAULT 'UTC',
                status TEXT DEFAULT 'draft',
                is_scheduled BOOLEAN DEFAULT 0,
                scheduler_task_id TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                last_executed_at TIMESTAMP,
                execution_count INTEGER DEFAULT 0,
                FOREIGN KEY (user_id) REFERENCES users(user_id)
            )
        """)
        
        # Automation executions table (SQLite version)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS automation_executions (
                execution_id INTEGER PRIMARY KEY AUTOINCREMENT,
                automation_id TEXT NOT NULL,
                user_id INTEGER NOT NULL,
                thread_id INTEGER,
                triggered_by TEXT NOT NULL,
                started_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                completed_at TIMESTAMP,
                duration_ms INTEGER,
                status TEXT NOT NULL,
                tools_used TEXT DEFAULT '[]',
                result_summary TEXT,
                error_message TEXT,
                FOREIGN KEY (automation_id) REFERENCES visual_automations(automation_id),
                FOREIGN KEY (user_id) REFERENCES users(user_id),
                FOREIGN KEY (thread_id) REFERENCES threads(thread_id)
            )
        """)
        
        conn.commit()
        conn.close()
        print("✅ Automation tables initialized (SQLite)")
    
    except Exception as e:
        print(f"❌ Error initializing automation tables: {e}")
        if 'conn' in locals():
            conn.close()


# Initialize tables on module load
init_automation_tables()


@automation_bp.route('/parse', methods=['POST'])
def parse_visual_flow():
    """
    Parse visual automation JSON and interpret user intent
    
    Request body:
    {
        "visual_flow_json": "{\"shapes\": [...], \"connections\": [...]}",
        "automation_title": "Daily Email Management",
        "user_context": "I want to check emails every morning"
    }
    
    Returns:
    {
        "interpretation": "Natural language explanation",
        "tools_sequence": ["tool1", "tool2"],
        "execution_plan": [{"step": 1, "tool": "...", "params": {...}}],
        "suggestions": ["Add error handling", "Include notification"],
        "complexity_score": 7
    }
    """
    try:
        data = request.json
        
        # Validate required fields
        if 'visual_flow_json' not in data:
            return jsonify({'error': 'visual_flow_json required'}), 400
        
        # Parse visual flow
        visual_flow = json.loads(data['visual_flow_json'])
        shapes = visual_flow.get('shapes', [])
        connections = visual_flow.get('connections', [])
        
        # Analyze workflow
        interpretation = _analyze_workflow(shapes, connections)
        tools_sequence = _extract_tools(shapes)
        execution_plan = _generate_execution_plan(shapes, connections)
        suggestions = _generate_suggestions(shapes, connections)
        complexity_score = _calculate_complexity(shapes, connections)
        
        return jsonify({
            'success': True,
            'interpretation': interpretation,
            'tools_sequence': tools_sequence,
            'execution_plan': execution_plan,
            'suggestions': suggestions,
            'complexity_score': complexity_score
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@automation_bp.route('/refine', methods=['POST'])
def refine_automation():
    """
    AI refines user's workflow with improvements
    
    Request body:
    {
        "original_automation_id": "auto_123",
        "original_visual_flow": "{\"shapes\": [...]}",
        "improvements": ["Add error handling", "Include notification"],
        "tools_sequence": ["tool1", "tool2"],
        "execution_prompt": "Detailed prompt for execution"
    }
    """
    try:
        data = request.json
        
        # Generate refined automation ID
        original_id = data.get('original_automation_id', f'auto_{int(datetime.now().timestamp())}')
        refined_id = f'{original_id}_refined'
        
        # Parse original flow
        original_flow = json.loads(data['original_visual_flow'])
        
        # Apply improvements
        refined_flow = _apply_improvements(
            original_flow,
            data.get('improvements', []),
            data.get('tools_sequence', [])
        )
        
        return jsonify({
            'success': True,
            'automation_id': refined_id,
            'visual_flow_json': json.dumps(refined_flow),
            'execution_prompt': data.get('execution_prompt'),
            'tools_sequence': data.get('tools_sequence', []),
            'improvements_applied': data.get('improvements', [])
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@automation_bp.route('/save', methods=['POST'])
def save_automation():
    """
    Save automation to database
    
    Request body:
    {
        "slug": "workflow-123",  // Required, workflow identifier
        "title": "Daily Email Management",
        "description": "Check emails and create summary",
        "status": "draft",  // draft, active, inactive
        "ui_json": {"shapes": [...], "connections": [...]},
        "execution_json": {"steps": [...]},
        "parent_automation_id": "auto_parent"  // Optional
    }
    """
    try:
        data = request.json
        user_id = request.headers.get('X-User-ID', 1)  # TODO: Get from auth
        
        # Validate required fields
        required = ['slug', 'title']
        for field in required:
            if field not in data:
                return jsonify({'error': f'Missing required field: {field}'}), 400
        
        # Use slug as automation_id
        automation_id = data['slug']
        
        # Convert ui_json and execution_json to strings for database
        ui_json_str = json.dumps(data.get('ui_json', {}))
        execution_json_str = json.dumps(data.get('execution_json', {}))
        
        # Get slug from data (required for workflow identification)
        slug = data.get('slug', '')
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Check if exists (upsert)
        cursor.execute("""
            SELECT automation_id FROM visual_automations WHERE automation_id = %s
        """, (automation_id,))
        
        existing = cursor.fetchone()
        
        if existing:
            # Update
            cursor.execute("""
                UPDATE visual_automations 
                SET title = %s, slug = %s, description = %s, category = %s, ui_json = %s, execution_json = %s, status = %s,
                    updated_at = CURRENT_TIMESTAMP
                WHERE automation_id = %s
            """, (
                data['title'],
                slug,
                data.get('description', ''),
                data.get('category', 'workflow'),
                ui_json_str,
                execution_json_str,
                data.get('status', 'draft'),
                automation_id
            ))
        else:
            # Insert
            cursor.execute("""
                INSERT INTO visual_automations (
                    automation_id, user_id, title, slug, description, category,
                    ui_json, execution_json, status
                ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
            """, (
                automation_id,
                user_id,
                data['title'],
                slug,
                data.get('description', ''),
                data.get('category', 'workflow'),
                ui_json_str,
                execution_json_str,
                data.get('status', 'draft')
            ))
        
        conn.commit()
        conn.close()
        
        return jsonify({
            'success': True,
            'automation_id': automation_id,
            'created_at': datetime.now().isoformat()
        }), 201
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@automation_bp.route('/list', methods=['GET'])
def list_automations():
    """List user's automations with optional filters"""
    try:
        user_id = request.headers.get('X-User-ID', 1)
        
        # Query parameters
        category = request.args.get('category')
        status = request.args.get('status')
        slug = request.args.get('slug')  # NEW: Filter by slug
        limit = int(request.args.get('limit', 50))
        
        conn = get_db_connection()
        cursor = conn.cursor()  # DatabaseConnection wrapper handles cursor type
        
        # Use PostgreSQL placeholder
        placeholder = '%s'
        
        query = f"""
            SELECT automation_id, slug, title, description, category, status,
                   ui_json, execution_json, is_scheduled, schedule_cron,
                   created_at, updated_at, last_executed_at, execution_count
            FROM visual_automations
            WHERE user_id = {placeholder}
        """
        params = [user_id]
        
        # NEW: Filter by slug (for workflow slug integration)
        if slug:
            query += f" AND slug = {placeholder}"
            params.append(slug)
        
        if category:
            query += f" AND category = {placeholder}"
            params.append(category)
        
        if status:
            query += f" AND status = {placeholder}"
            params.append(status)
        
        query += f" ORDER BY updated_at DESC LIMIT {placeholder}"
        params.append(limit)
        
        cursor.execute(query, params)
        rows = cursor.fetchall()
        conn.close()
        
        automations = []
        for row in rows:
            # Parse JSON fields
            ui_json = json.loads(row['ui_json']) if isinstance(row['ui_json'], str) else row['ui_json']
            execution_json = json.loads(row['execution_json']) if isinstance(row['execution_json'], str) else row['execution_json']
            
            automations.append({
                'id': row['automation_id'],
                'slug': row['slug'],
                'title': row['title'],
                'description': row['description'],
                'category': row['category'],
                'status': row['status'],
                'ui_json': ui_json,
                'execution_json': execution_json,
                'is_scheduled': bool(row['is_scheduled']),
                'schedule_cron': row['schedule_cron'],
                'created_at': str(row['created_at']),
                'updated_at': str(row['updated_at']),
                'last_executed_at': str(row['last_executed_at']) if row['last_executed_at'] else None,
                'execution_count': row['execution_count']
            })
        
        return jsonify({
            'success': True,
            'workflows': automations,
            'count': len(automations)
        })
        
    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500


@automation_bp.route('/<automation_id>', methods=['GET'])
def get_automation(automation_id):
    """Get full automation details including visual flow JSON"""
    try:
        user_id = request.headers.get('X-User-ID', 1)
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT * FROM visual_automations 
            WHERE automation_id = %s AND user_id = %s
        """, (automation_id, user_id))
        
        row = cursor.fetchone()
        conn.close()
        
        if not row:
            return jsonify({'error': 'Automation not found'}), 404
        
        automation = {
            'automation_id': row['automation_id'],
            'title': row['title'],
            'description': row['description'],
            'visual_flow_json': row['visual_flow_json'],
            'execution_prompt': row['execution_prompt'],
            'tools_sequence': json.loads(row['tools_sequence']) if row['tools_sequence'] else [],
            'schedule_cron': row['schedule_cron'],
            'schedule_datetime': row['schedule_datetime'],
            'timezone': row['timezone'],
            'is_active': bool(row['is_active']),
            'is_scheduled': bool(row['is_scheduled']),
            'scheduler_task_id': row['scheduler_task_id'],
            'parent_automation_id': row['parent_automation_id'],
            'created_at': row['created_at'],
            'updated_at': row['updated_at']
        }
        
        return jsonify({
            'success': True,
            'automation': automation
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@automation_bp.route('/<automation_id>', methods=['DELETE'])
def delete_automation(automation_id):
    """Delete automation and deactivate any scheduled tasks"""
    try:
        user_id = request.headers.get('X-User-ID', 1)
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Get automation to check scheduler_task_id
        cursor.execute("""
            SELECT scheduler_task_id FROM visual_automations
            WHERE automation_id = %s AND user_id = %s
        """, (automation_id, user_id))
        
        row = cursor.fetchone()
        
        if not row:
            conn.close()
            return jsonify({'error': 'Automation not found'}), 404
        
        # Deactivate scheduler task if exists
        if row['scheduler_task_id']:
            try:
                scheduler = get_scheduler()
                scheduler.delete_task(row['scheduler_task_id'])
            except:
                pass  # Task may already be deleted
        
        # Delete automation
        cursor.execute("""
            DELETE FROM visual_automations 
            WHERE automation_id = %s AND user_id = %s
        """, (automation_id, user_id))
        
        conn.commit()
        conn.close()
        
        return jsonify({
            'success': True,
            'message': f'Automation {automation_id} deleted'
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@automation_bp.route('/<automation_id>/activate', methods=['POST'])
def activate_automation(automation_id):
    """
    Activate automation on scheduler
    
    Request body:
    {
        "trigger_type": "cron",  // or "datetime"
        "cron_schedule": "0 7 * * *",
        "datetime_trigger": "2025-11-16T14:00:00Z",
        "timezone": "America/New_York",
        "requires_approval": false
    }
    """
    try:
        user_id = request.headers.get('X-User-ID', 1)
        data = request.json
        
        # Get automation
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT * FROM visual_automations
            WHERE automation_id = %s AND user_id = %s
        """, (automation_id, user_id))
        
        row = cursor.fetchone()
        
        if not row:
            conn.close()
            return jsonify({'error': 'Automation not found'}), 404
        
        # Create scheduler task
        scheduler = get_scheduler()
        
        task_data = {
            'task_name': f'Automation: {row["title"]}',
            'description': row['description'] or 'Visual automation execution',
            'created_by': 'user',
            'created_by_user_id': user_id,
            'trigger_type': data.get('trigger_type', 'cron'),
            'action_type': 'execute_automation',
            'action_payload': json.dumps({
                'automation_id': automation_id,
                'visual_flow_json': row['visual_flow_json'],
                'execution_prompt': row['execution_prompt'],
                'tools_sequence': json.loads(row['tools_sequence']) if row['tools_sequence'] else []
            }),
            'requires_approval': data.get('requires_approval', False),
            'enabled': True
        }
        
        if data.get('trigger_type') == 'cron':
            task_data['cron_expression'] = data.get('cron_schedule')
        elif data.get('trigger_type') == 'datetime':
            task_data['datetime_trigger'] = data.get('datetime_trigger')
        
        task_id = scheduler.create_task(task_data)
        
        # Update automation with scheduler info
        cursor.execute("""
            UPDATE visual_automations
            SET is_active = 1,
                is_scheduled = 1, scheduler_task_id = %s, schedule_cron = %s, schedule_datetime = %s, timezone = %s,
                updated_at = CURRENT_TIMESTAMP
            WHERE automation_id = %s
        """, (
            task_id,
            data.get('cron_schedule'),
            data.get('datetime_trigger'),
            data.get('timezone', 'UTC'),
            automation_id
        ))
        
        conn.commit()
        conn.close()
        
        # Get next run time
        task = scheduler.get_task(task_id)
        
        return jsonify({
            'success': True,
            'task_id': task_id,
            'next_run': task.get('next_run'),
            'message': f'Automation activated successfully'
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@automation_bp.route('/<automation_id>/deactivate', methods=['POST'])
def deactivate_automation(automation_id):
    """Deactivate scheduled automation"""
    try:
        user_id = request.headers.get('X-User-ID', 1)
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT scheduler_task_id FROM visual_automations
            WHERE automation_id = %s AND user_id = %s
        """, (automation_id, user_id))
        
        row = cursor.fetchone()
        
        if not row:
            conn.close()
            return jsonify({'error': 'Automation not found'}), 404
        
        # Delete scheduler task
        if row['scheduler_task_id']:
            scheduler = get_scheduler()
            scheduler.delete_task(row['scheduler_task_id'])
        
        # Update automation
        cursor.execute("""
            UPDATE visual_automations
            SET is_active = 0,
                is_scheduled = 0,
                scheduler_task_id = NULL,
                updated_at = CURRENT_TIMESTAMP
            WHERE automation_id = %s
        """, (automation_id,))
        
        conn.commit()
        conn.close()
        
        return jsonify({
            'success': True,
            'message': f'Automation {automation_id} deactivated'
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@automation_bp.route('/<automation_id>/history', methods=['GET'])
def get_execution_history(automation_id):
    """Get automation execution history"""
    try:
        user_id = request.headers.get('X-User-ID', 1)
        limit = int(request.args.get('limit', 10))
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT * FROM automation_executions
            WHERE automation_id = %s AND user_id = %s
            ORDER BY started_at DESC
            LIMIT %s
        """, (automation_id, user_id, limit))
        
        rows = cursor.fetchall()
        conn.close()
        
        executions = []
        for row in rows:
            executions.append({
                'execution_id': row['execution_id'],
                'thread_id': row['thread_id'],
                'triggered_by': row['triggered_by'],
                'started_at': row['started_at'],
                'completed_at': row['completed_at'],
                'status': row['status'],
                'tools_used': json.loads(row['tools_used']) if row['tools_used'] else [],
                'result_summary': row['result_summary'],
                'error_message': row['error_message']
            })
        
        return jsonify({
            'success': True,
            'executions': executions,
            'count': len(executions)
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@automation_bp.route('/<automation_id>/export', methods=['GET'])
def export_automation(automation_id):
    """Export automation for canvas rendering"""
    try:
        user_id = request.headers.get('X-User-ID', 1)
        format_type = request.args.get('format', 'detailed')
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT * FROM visual_automations
            WHERE automation_id = %s AND user_id = %s
        """, (automation_id, user_id))
        
        row = cursor.fetchone()
        conn.close()
        
        if not row:
            return jsonify({'error': 'Automation not found'}), 404
        
        visual_flow = json.loads(row['visual_flow_json'])
        
        if format_type == 'simplified':
            # Return minimal data for quick preview
            export_data = {
                'automation_id': automation_id,
                'title': row['title'],
                'shapes': visual_flow.get('shapes', []),
                'connections': visual_flow.get('connections', [])
            }
        else:
            # Return full data for editing
            export_data = {
                'automation_id': automation_id,
                'title': row['title'],
                'description': row['description'],
                'shapes': visual_flow.get('shapes', []),
                'connections': visual_flow.get('connections', []),
                'execution_prompt': row['execution_prompt'],
                'tools_sequence': json.loads(row['tools_sequence']) if row['tools_sequence'] else [],
                'metadata': {
                    'is_active': bool(row['is_active']),
                    'is_scheduled': bool(row['is_scheduled']),
                    'created_at': row['created_at'],
                    'updated_at': row['updated_at']
                }
            }
        
        return jsonify({
            'success': True,
            'export': export_data
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


# Helper functions for workflow analysis
def _analyze_workflow(shapes, connections):
    """Generate natural language interpretation of workflow"""
    if not shapes:
        return "Empty workflow"
    
    interpretation_parts = []
    
    # Identify triggers (circles)
    triggers = [s for s in shapes if s['type'] == 'circle']
    if triggers:
        interpretation_parts.append(f"Workflow starts with: {triggers[0]['text']}")
    
    # Count action steps
    actions = [s for s in shapes if s['type'] in ['rectangle', 'rounded']]
    if actions:
        interpretation_parts.append(f"Contains {len(actions)} action steps")
    
    # Check for decisions
    decisions = [s for s in shapes if s['type'] in ['hexagon', 'diamond']]
    if decisions:
        interpretation_parts.append(f"Includes {len(decisions)} decision points")
    
    return ". ".join(interpretation_parts)


def _extract_tools(shapes):
    """Extract potential tool names from shape text"""
    tools = []
    keywords_to_tools = {
        'outlook': 'outlook_list_messages',
        'email': 'gmail_send_email',
        'calendar': 'google_calendar_create_event',
        'synergy': 'synergy_create_session',
        'spreadsheet': 'google_sheets_create'
    }
    
    for shape in shapes:
        text_lower = shape['text'].lower()
        for keyword, tool in keywords_to_tools.items():
            if keyword in text_lower and tool not in tools:
                tools.append(tool)
    
    return tools


def _generate_execution_plan(shapes, connections):
    """Generate step-by-step execution plan"""
    # TODO: Implement full execution plan generation
    return [{"step": i+1, "shape_id": s['id'], "text": s['text']} 
            for i, s in enumerate(shapes)]


def _generate_suggestions(shapes, connections):
    """Generate AI suggestions for improvements"""
    suggestions = []
    
    # Check for error handling
    if not any(s['type'] == 'hexagon' for s in shapes):
        suggestions.append("Consider adding decision points for error handling")
    
    # Check for notifications
    notification_keywords = ['notify', 'alert', 'email', 'message']
    has_notification = any(any(kw in s['text'].lower() for kw in notification_keywords) 
                          for s in shapes)
    if not has_notification:
        suggestions.append("Consider adding notification step for completion/errors")
    
    return suggestions


def _calculate_complexity(shapes, connections):
    """Calculate workflow complexity score (1-10)"""
    score = len(shapes)  # Base on number of shapes
    score += len(connections) * 0.5  # Connections add complexity
    score += len([s for s in shapes if s['type'] in ['hexagon', 'diamond']]) * 2  # Decisions increase complexity
    
    return min(int(score), 10)


def _apply_improvements(original_flow, improvements, tools_sequence):
    """Apply AI improvements to visual flow"""
    refined_flow = original_flow.copy()
    
    # TODO: Implement actual improvement application
    # For now, just return original with updated metadata
    refined_flow['improvements_applied'] = improvements
    refined_flow['tools_sequence'] = tools_sequence
    
    return refined_flow

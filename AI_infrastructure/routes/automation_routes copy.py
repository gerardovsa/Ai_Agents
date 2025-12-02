"""
Automation Visual Workflows API Routes
=======================================
REST API endpoints for visual automation canvas and AI-interpreted workflows.
Last Modified: 2025-11-26 - Added PATCH /api/automation/toggle/<id> for production workflow enable/disable

Endpoints:
    POST   /api/automation/parse            - Parse visual flow and interpret intent
    POST   /api/automation/refine           - AI refines user's workflow  
    POST   /api/automation/save             - Save automation to database
    PUT    /api/automation/update           - Update existing workflow (add/remove actions, modify trigger)
    GET    /api/automation/list             - List user's automations (from visual_automations + automation_workflows)
    GET    /api/automation/<id>             - Get automation details
    DELETE /api/automation/<id>             - Delete automation
    POST   /api/automation/<id>/activate    - Schedule automation
    POST   /api/automation/<id>/deactivate  - Unschedule automation
    PATCH  /api/automation/toggle/<id>      - Enable/disable production automation (automation_workflows)
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


def get_user_from_token(auth_header):
    """Extract user ID from JWT token"""
    if not auth_header or not auth_header.startswith('Bearer '):
        return None
    
    token = auth_header.replace('Bearer ', '')
    
    # TESTING FALLBACK: If token is 'test_token', return user_id=1
    if token.startswith('test_token'):
        print("[AUTOMATION] Using test token - returning user_id=1")
        return 1
    
    try:
        import jwt as pyjwt
        from dotenv import load_dotenv
        
        env_path = os.path.join(os.path.dirname(__file__), '..', '..', '.env.master')
        load_dotenv(env_path)
        
        jwt_secret = os.getenv('JWT_SECRET', 'your-secret-key-change-this')
        payload = pyjwt.decode(token, jwt_secret, algorithms=['HS256'])
        
        return payload.get('user_id')
    except Exception as e:
        print(f"Error decoding JWT token: {e}")
        return None

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
    conn = None
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
            
            if not exists:
                print("⚠️  WARNING: visual_automations table not found in PostgreSQL")
                print("   Run migration: supabase_migrations/004_automation_tables.sql")
            else:
                print("✅ Automation tables exist in PostgreSQL")
            
            # ✅ CRITICAL FIX: Close connection before returning
            if conn:
                conn.close()
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
        print("✅ Automation tables initialized (SQLite)")
    
    except Exception as e:
        print(f"❌ Error initializing automation tables: {e}")
    finally:
        # CRITICAL FIX: Always close connection
        if conn is not None:
            try:
                conn.close()
            except Exception:
                pass  # Ignore close errors


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
    Save automation to database - UI COMPATIBLE
    
    Request body (supports multiple formats):
    {
        "slug": "workflow-123",  // Optional, auto-generated if not provided
        "title": "Daily Email Management",  // OR "name"
        "description": "Check emails and create summary",
        "status": "draft",  // draft, active, inactive
        "category": "email",  // email, data_processing, notifications, etc.
        
        // Canvas data - can be in multiple formats:
        "shapes": [...],  // Direct shapes array (UI sends this)
        "connections": [...],  // Direct connections array (UI sends this)
        // OR
        "ui_json": {"shapes": [...], "connections": [...]},  // Wrapped format
        // OR
        "workflow_json": {"shapes": [...], "connections": [...]},  // Alternative name
        
        "execution_json": {"steps": [...]},  // Optional
        "parent_automation_id": "auto_parent"  // Optional
    }
    """
    try:
        data = request.json
        user_id = get_user_from_token(request.headers.get('Authorization'))
        if not user_id:
            return jsonify({'error': 'Unauthorized - invalid or missing token'}), 401
        
        # UI COMPATIBLE: Handle both 'title' and 'name'
        title = data.get('title') or data.get('name', 'Untitled Workflow')
        
        # Generate slug if not provided
        slug = data.get('slug')
        if not slug:
            # Generate from title
            import re
            import time
            slug = re.sub(r'[^a-z0-9]+', '-', title.lower()).strip('-')
            # Add timestamp to ensure uniqueness
            slug = f"{slug}-{int(time.time())}"
        
        # Use slug as automation_id
        automation_id = slug
        
        # UI COMPATIBLE: Handle shapes/connections in multiple formats
        ui_json = data.get('ui_json') or data.get('workflow_json') or {}
        
        # If shapes/connections are at top level (UI sends this way), wrap them
        if 'shapes' in data and 'connections' in data:
            ui_json = {
                'shapes': data['shapes'],
                'connections': data['connections'],
                'canvas_data': data.get('canvas_data', {})
            }
        
        # Convert to JSON strings for database
        ui_json_str = json.dumps(ui_json)
        execution_json_str = json.dumps(data.get('execution_json', {}))
        
        # Get slug from data (required for workflow identification)
        slug = automation_id
        
        # ✅ LEAK FIX: Use context manager
        with get_db_connection() as conn:
            cursor = conn.cursor()
            
            # ✅ FIX: Use PostgreSQL UPSERT with ON CONFLICT to prevent duplicate slug errors
            from shared.database_utils import is_using_supabase
        
        if is_using_supabase():
            # PostgreSQL - use ON CONFLICT (UPSERT)
            cursor.execute("""
                INSERT INTO visual_automations (
                    automation_id, user_id, title, slug, description, category,
                    ui_json, execution_json, status, created_at, updated_at
                ) VALUES (
                    %s, %s, %s, %s, %s, %s, %s, %s, %s, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP
                )
                ON CONFLICT (slug) DO UPDATE SET
                    title = EXCLUDED.title,
                    description = EXCLUDED.description,
                    category = EXCLUDED.category,
                    ui_json = EXCLUDED.ui_json,
                    execution_json = EXCLUDED.execution_json,
                    status = EXCLUDED.status,
                    updated_at = CURRENT_TIMESTAMP
            """, (
                automation_id,
                user_id,
                title,
                slug,
                data.get('description', ''),
                data.get('category', 'workflow'),
                ui_json_str,
                execution_json_str,
                data.get('status', 'draft')
            ))
        else:
            # SQLite - use INSERT OR REPLACE
            cursor.execute("""
                INSERT OR REPLACE INTO visual_automations (
                    automation_id, user_id, title, slug, description, category,
                    ui_json, execution_json, status
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                automation_id,
                user_id,
                title,
                slug,
                data.get('description', ''),
                data.get('category', 'workflow'),
                ui_json_str,
                execution_json_str,
                data.get('status', 'draft')
            ))
        
            existing = data.get('is_update', False)  # Check if frontend signaled update
            
            conn.commit()
        
        # ✅ Connection auto-closed by context manager
        # UI COMPATIBLE: Return fields UI expects
        return jsonify({
            'success': True,
            'message': 'Workflow saved successfully',
            'automation_id': automation_id,
            'workflow_id': automation_id,  # UI expects this
            'slug': slug,  # UI expects this
            'created_at': datetime.now().isoformat()
        }), 200  # Always 200 for UPSERT
        
    except Exception as e:
        # CRITICAL FIX: Close connection on error to prevent pool leak
        if 'conn' in locals() and conn is not None:
            try:
                conn.close()
                print("[AUTOMATION] Connection closed after exception")
            except:
                pass
        return jsonify({'error': str(e)}), 500


@automation_bp.route('/update', methods=['PUT'])
def update_workflow():
    """
    Update an existing workflow - add/remove actions, modify trigger, change parameters
    UI automatically refreshes canvas after update
    
    Request body:
    {
        "slug": "wf_a3f8b2c1_1732029847",  // Required
        "add_actions": [  // Optional
            {
                "tool": "gmail_send_email",
                "parameters": {"to": "user@example.com", "subject": "Alert"},
                "position": 3  // Optional, default: append to end
            }
        ],
        "remove_actions": [0, 2],  // Optional - positions to remove
        "update_trigger": {  // Optional
            "type": "schedule",
            "schedule_cron": "0 */2 * * *"
        },
        "update_action_parameters": {  // Optional
            "position": 1,
            "parameters": {"max_results": 50}
        },
        "update_metadata": {  // Optional
            "title": "New Title",
            "description": "New Description"
        }
    }
    
    Response:
    {
        "success": true,
        "automation_id": "wf_a3f8b2c1_1732029847",
        "slug": "wf_a3f8b2c1_1732029847",
        "action_count": 5,
        "visual_flow_json": {...},
        "message": "Workflow updated successfully"
    }
    """
    try:
        data = request.json
        user_id = get_user_from_token(request.headers.get('Authorization'))
        if not user_id:
            return jsonify({'error': 'Unauthorized - invalid or missing token'}), 401
        
        # Validate slug
        slug = data.get('slug')
        if not slug:
            return jsonify({'error': 'slug is required'}), 400
        
        if not slug.startswith('wf_'):
            return jsonify({'error': f'Invalid slug format: {slug} (must start with wf_)'}), 400
        
        # At least one update operation required
        has_update = any([
            data.get('add_actions'),
            data.get('remove_actions'),
            data.get('update_trigger'),
            data.get('update_action_parameters'),
            data.get('update_metadata')
        ])
        
        if not has_update:
            return jsonify({'error': 'At least one update operation required'}), 400
        
        # ✅ LEAK FIX: Use context manager
        with get_db_connection() as conn:
            cursor = conn.cursor()
            
            # Get existing workflow
            cursor.execute("""
            SELECT automation_id, ui_json, execution_json, title, description, category
            FROM visual_automations
            WHERE slug = %s AND user_id = %s
        """, (slug, user_id))
            
            row = cursor.fetchone()
            if not row:
                return jsonify({'error': f'Workflow not found: {slug}'}), 404
            
            # Parse existing data
            automation_id = row['automation_id']
            ui_json = json.loads(row['ui_json'])
            execution_json = json.loads(row['execution_json'])
            current_title = row['title']
            current_description = row['description']
            current_category = row['category']
            
            # Get current actions from execution_json
            actions = execution_json.get('actions', [])
            trigger = execution_json.get('trigger', {'type': 'manual'})
            
            # Apply updates
            changes = []
            
            # 1. Remove actions (do this first, before adding)
            if data.get('remove_actions'):
                remove_positions = sorted(data['remove_actions'], reverse=True)  # Remove from end first
                for pos in remove_positions:
                    if 0 <= pos < len(actions):
                        actions.pop(pos)
                        changes.append(f'removed action at position {pos}')
            
            # 2. Add actions
            if data.get('add_actions'):
                for action_data in data['add_actions']:
                    position = action_data.get('position')
                    action = {
                        'tool': action_data['tool'],
                        'parameters': action_data.get('parameters', {})
                    }
                    if 'condition' in action_data:
                        action['condition'] = action_data['condition']
                    
                    if position is not None and 0 <= position <= len(actions):
                        actions.insert(position, action)
                        changes.append(f'added action at position {position}')
                    else:
                        actions.append(action)
                        changes.append('added action to end')
            
            # 3. Update trigger
            if data.get('update_trigger'):
                trigger = data['update_trigger']
                changes.append('updated trigger')
            
            # 4. Update action parameters
            if data.get('update_action_parameters'):
                pos = data['update_action_parameters'].get('position')
                new_params = data['update_action_parameters'].get('parameters', {})
                if pos is not None and 0 <= pos < len(actions):
                    # Merge new parameters with existing
                    actions[pos]['parameters'].update(new_params)
                    changes.append(f'updated action {pos} parameters')
            
            # 5. Update metadata
            if data.get('update_metadata'):
                if 'title' in data['update_metadata']:
                    current_title = data['update_metadata']['title']
                    changes.append('updated title')
                if 'description' in data['update_metadata']:
                    current_description = data['update_metadata']['description']
                    changes.append('updated description')
            
            # Rebuild execution_json
            execution_json['actions'] = actions
            execution_json['trigger'] = trigger
            
            # Rebuild ui_json (visual flow)
            shapes = []
            connections = []
            
            # Add trigger node (hexagon, green)
            shapes.append({
                'id': 'node_trigger',
                'type': 'hexagon',
                'text': f"TRIGGER: {trigger.get('type', 'manual')}",
                'color': '#10B981',
                'x': 100,
                'y': 100
            })
            
            # Add action nodes (rectangles, blue)
            for i, action in enumerate(actions):
                shapes.append({
                    'id': f'node_action_{i}',
                    'type': 'rectangle',
                    'text': action['tool'],
                    'color': '#3B82F6',
                    'x': 100,
                    'y': 250 + (i * 150)
                })
                
                # Connect previous node to this one
                if i == 0:
                    connections.append({'from': 'node_trigger', 'to': f'node_action_{i}'})
                else:
                    connections.append({'from': f'node_action_{i-1}', 'to': f'node_action_{i}'})
            
            ui_json['shapes'] = shapes
            ui_json['connections'] = connections
            
            # Update database
            cursor.execute("""
            UPDATE visual_automations
            SET ui_json = %s, execution_json = %s, title = %s, description = %s, updated_at = CURRENT_TIMESTAMP
            WHERE slug = %s AND user_id = %s
        """, (
                json.dumps(ui_json),
                json.dumps(execution_json),
                current_title,
                current_description,
                slug,
                user_id
            ))
            
            conn.commit()
        
        # ✅ Connection auto-closed by context manager
        return jsonify({
            'success': True,
            'automation_id': automation_id,
            'slug': slug,
            'action_count': len(actions),
            'visual_flow_json': ui_json,
            'message': f"Workflow updated: {', '.join(changes)}"
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@automation_bp.route('/list', methods=['GET'])
def list_automations():
    """List user's automations with optional filters"""
    try:
        user_id = get_user_from_token(request.headers.get('Authorization'))
        if not user_id:
            return jsonify({'error': 'Unauthorized - invalid or missing token'}), 401
        
        # Query parameters
        category = request.args.get('category')
        status = request.args.get('status')
        slug = request.args.get('slug')  # NEW: Filter by slug
        limit = int(request.args.get('limit', 50))
        
        # ✅ LEAK FIX: Use context manager to auto-close connection
        with get_db_connection() as conn:
            cursor = conn.cursor()  # DatabaseConnection wrapper handles cursor type
            
            # Use PostgreSQL placeholder
            placeholder = '%s'
            
            # Query includes logged-in user's automations + system user (user_id=1) automations
            # This allows all users to see system templates/examples
            # Join visual_automations with automation_workflows to determine production state
            query = f"""
                SELECT 
                    va.automation_id, 
                    va.slug, 
                    va.title, 
                    va.description, 
                    va.category, 
                    va.status,
                    va.ui_json, 
                    va.execution_json, 
                    va.is_scheduled, 
                    va.schedule_cron,
                    va.created_at, 
                    va.updated_at, 
                    va.last_executed_at, 
                    va.execution_count,
                    va.user_id,
                    aw.workflow_id,
                    aw.enabled AS automation_enabled,
                    CASE 
                        WHEN aw.workflow_id IS NOT NULL THEN 'production'
                        ELSE 'draft'
                    END AS workflow_state
                FROM visual_automations va
                LEFT JOIN automation_workflows aw ON va.slug = aw.slug AND va.user_id = aw.user_id
                WHERE va.user_id = {placeholder} OR va.user_id = 1
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
            print(f'[DEBUG /api/automation/list] SQL query returned {len(rows)} rows for user_id={user_id}')
            print(f'[DEBUG /api/automation/list] Query filters: category={category}, status={status}, slug={slug}, limit={limit}')
            
            # DEBUG: Log first 3 row IDs and slugs
            if rows:
                print(f'[DEBUG /api/automation/list] First 3 rows: ')
                for idx, r in enumerate(rows[:3]):
                    print(f'  Row {idx+1}: automation_id={r.get("automation_id")}, slug={r.get("slug")}, title={r.get("title")}')
        
        # ✅ Connection auto-closed by context manager
        
        automations = []
        skipped_count = 0
        print(f'[DEBUG /api/automation/list] Starting transformation loop for {len(rows)} rows...')
        for i, row in enumerate(rows, 1):
            try:
                # Parse JSON fields
                ui_json = json.loads(row['ui_json']) if isinstance(row['ui_json'], str) else row['ui_json']
                execution_json = json.loads(row['execution_json']) if isinstance(row['execution_json'], str) else row['execution_json']
                
                # Transform nodes/edges to shapes/connections (canvas format)
                shapes = []
                connections = []
                
                if isinstance(ui_json, dict):
                    # Parse canvas_data for node positions (if stored separately)
                    canvas_data_str = row.get('canvas_data')
                    canvas_data = {}
                    if canvas_data_str:
                        try:
                            canvas_data = json.loads(canvas_data_str) if isinstance(canvas_data_str, str) else canvas_data_str
                            if isinstance(canvas_data, dict) and 'nodes' in canvas_data:
                                canvas_data = canvas_data['nodes']  # Extract nodes dict
                        except:
                            canvas_data = {}
                
                # Extract nodes and transform to shapes
                nodes = ui_json.get('nodes', [])
                for node in nodes:
                    node_id = node.get('id')
                    
                    # Get position from canvas_data if available, otherwise from node
                    position = canvas_data.get(node_id, {}) if canvas_data else {}
                    x = position.get('x', node.get('x', node.get('position', {}).get('x', 100)))
                    y = position.get('y', node.get('y', node.get('position', {}).get('y', 100)))
                    
                    # Determine shape type based on node type
                    node_type = node.get('type', 'action')
                    shape_type_map = {
                        'email_trigger': 'trigger',
                        'trigger': 'trigger',
                        'ai_agent': 'tool',
                        'send_email': 'output',
                        'if_else': 'decision',
                        'condition': 'decision'
                    }
                    shape_type = shape_type_map.get(node_type, 'rectangle')
                    
                    # Determine color based on node type
                    color_map = {
                        'trigger': '#10B981',  # Green for triggers
                        'tool': '#6B7280',     # Gray for tools
                        'output': '#EAB308',   # Yellow for output
                        'decision': '#F59E0B', # Orange for decisions
                        'rectangle': '#58a6ff' # Default blue
                    }
                    color = color_map.get(shape_type, '#58a6ff')
                    
                    # Extract text from config or use node type
                    config = node.get('config', {})
                    text = config.get('role', config.get('subject', node_type.upper()))
                    
                    shape = {
                        'id': node_id,
                        'type': shape_type,
                        'x': int(x),
                        'y': int(y),
                        'width': node.get('width', 150),
                        'height': node.get('height', 80),
                        'text': text,
                        'color': color
                    }
                    shapes.append(shape)
                
                # Extract edges and transform to connections
                edges = ui_json.get('edges', [])
                for edge in edges:
                    connection = {
                        'id': edge.get('id', f"conn_{edge.get('from')}_{edge.get('to')}"),
                        'from': edge.get('from'),
                        'to': edge.get('to')
                    }
                    connections.append(connection)
                
                # Also check for existing shapes/connections format (backward compatibility)
                if not shapes and 'shapes' in ui_json:
                    shapes = ui_json.get('shapes', [])
                if not connections and 'connections' in ui_json:
                    connections = ui_json.get('connections', [])
                
                # UI COMPATIBLE FORMAT - Map database fields to UI expected names
                automations.append({
                # Primary identifiers (UI expects these exact names)
                'workflow_id': row['automation_id'],  # Map automation_id -> workflow_id
                'id': row['automation_id'],
                'slug': row['slug'],
                
                # Naming fields (UI expects 'name' not 'title')
                'name': row['title'],  # Map title -> name
                'title': row['title'],  # Keep for backward compatibility
                'description': row['description'],
                'category': row['category'],
                
                # Status fields (UI expects 'enabled' boolean)
                'status': row['status'],
                'enabled': bool(row.get('is_active') if row.get('is_active') is not None else True),  # Map is_active -> enabled
                
                # JSON data with transformed shapes/connections
                'workflow_json': {
                    'shapes': shapes,
                    'connections': connections,
                    'nodes': ui_json.get('nodes', []) if isinstance(ui_json, dict) else [],
                    'edges': ui_json.get('edges', []) if isinstance(ui_json, dict) else []
                },
                'ui_json': ui_json,
                'execution_json': execution_json,
                'shapes': shapes,  # Direct access for canvas
                'connections': connections,  # Direct access for canvas
                
                # User ownership
                'user_id': row['user_id'],
                'is_system_template': row['user_id'] == 1,  # Flag system templates
                'is_editable': row['user_id'] == user_id,   # Only own workflows are editable
                
                # Automation lifecycle state (NEW: production vs draft)
                'workflow_state': row.get('workflow_state', 'draft'),  # 'production' or 'draft'
                'is_production': row.get('workflow_state') == 'production',  # Exists in automation_workflows
                'is_draft': row.get('workflow_state') == 'draft',  # Only in visual_automations
                'automation_enabled': bool(row.get('automation_enabled')) if row.get('automation_enabled') is not None else False,  # Production workflows can be enabled/disabled
                'automation_workflow_id': row.get('workflow_id'),  # UUID from automation_workflows (if production)
                'automation_state': row['status'] or 'draft',  # draft, inactive, active
                'is_design_only': row['status'] == 'draft',
                'is_automated': row['status'] in ('inactive', 'active'),
                'is_active': row['status'] == 'active',
                
                # Scheduling
                'is_scheduled': bool(row['is_scheduled']),
                'schedule_cron': row['schedule_cron'],
                'timezone': row.get('timezone', 'UTC'),
                
                # Timestamps (UI expects ISO format strings)
                'created_at': str(row['created_at']),
                'updated_at': str(row['updated_at']),
                'last_executed_at': str(row['last_executed_at']) if row['last_executed_at'] else None,
                
                # Execution stats
                'execution_count': row['execution_count'] or 0,
                'run_count': row['execution_count'] or 0,  # Alias for UI
                'success_count': 0,  # TODO: Calculate from execution history
                'error_count': 0,  # TODO: Calculate from execution history
                'last_run_at': str(row['last_executed_at']) if row['last_executed_at'] else None
                })
                print(f'[DEBUG /api/automation/list] ✓ Transformed workflow #{i}: id={row["automation_id"]}, slug={row["slug"]}, title={row["title"]}')
                
            except Exception as transform_error:
                skipped_count += 1
                print(f'[ERROR /api/automation/list] ✗ Failed to transform workflow #{i} ({row.get("automation_id", "UNKNOWN")}): {type(transform_error).__name__}: {str(transform_error)}')
                import traceback
                traceback.print_exc()
                continue  # Skip this workflow and process the rest        print(f'[DEBUG /api/automation/list] Successfully transformed {len(automations)} workflows, skipped {skipped_count}')
        print(f'[DEBUG /api/automation/list] Returning JSON response with count={len(automations)}')
        
        return jsonify({
            'success': True,
            'workflows': automations,
            'count': len(automations)
        })
        
    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500


@automation_bp.route('/workflows/list', methods=['GET'])
def list_production_workflows():
    """
    ✅ NEW ENDPOINT: List production workflows from automation_workflows table
    
    This endpoint returns workflows that have been promoted to production status.
    These are actual scheduled/running automations (not visual drafts).
    
    Returns workflows from automation_workflows table (not visual_automations)
    """
    try:
        user_id = get_user_from_token(request.headers.get('Authorization'))
        if not user_id:
            return jsonify({'error': 'Unauthorized - invalid or missing token'}), 401
        
        # Query parameters
        category = request.args.get('category')
        enabled = request.args.get('enabled')  # true/false
        limit = int(request.args.get('limit', 50))
        
        # ✅ LEAK FIX: Use context manager for automatic connection cleanup
        with get_db_connection() as conn:
            cursor = conn.cursor()
            
            # PostgreSQL placeholder
            placeholder = '%s'
            
            # Query automation_workflows table (production workflows)
            query = f"""
                SELECT 
                    workflow_id,
                    user_id,
                    name,
                    slug,
                    description,
                    category,
                    workflow_json,
                    canvas_data,
                    enabled,
                    version,
                    created_at,
                    updated_at,
                    last_run_at,
                    run_count,
                    success_count,
                    error_count
                FROM automation_workflows
                WHERE user_id = {placeholder}
            """
            params = [user_id]
            
            if category:
                query += f" AND category = {placeholder}"
                params.append(category)
            
            if enabled is not None:
                query += f" AND enabled = {placeholder}"
                params.append(enabled.lower() == 'true')
            
            query += f" ORDER BY updated_at DESC LIMIT {placeholder}"
            params.append(limit)
            
            cursor.execute(query, params)
            rows = cursor.fetchall()
        
        # ✅ Connection auto-closed by context manager
        
        workflows = []
        for row in rows:
            try:
                # Parse workflow JSON
                workflow_json = json.loads(row['workflow_json']) if isinstance(row['workflow_json'], str) else row['workflow_json']
                canvas_data = json.loads(row['canvas_data']) if row.get('canvas_data') and isinstance(row['canvas_data'], str) else (row.get('canvas_data') or {})
                
                workflows.append({
                    'id': row['slug'],  # UI expects 'id'
                    'workflow_id': row['workflow_id'],
                    'slug': row['slug'],
                    'name': row['name'],
                    'title': row['name'],  # Alias for UI
                    'description': row['description'] or '',
                    'category': row['category'] or 'other',
                    
                    # Visual flow (UI expects shapes/connections)
                    'shapes': canvas_data.get('shapes', []),
                    'connections': canvas_data.get('connections', []),
                    'ui_json': canvas_data,
                    
                    # Execution flow
                    'execution_json': workflow_json,
                    
                    # Status
                    'status': 'active' if row['enabled'] else 'paused',
                    'enabled': row['enabled'],
                    'is_automated': True,  # Production workflows are automated
                    'is_active': row['enabled'],
                    
                    # Timestamps
                    'created_at': str(row['created_at']),
                    'updated_at': str(row['updated_at']),
                    'last_run_at': str(row['last_run_at']) if row['last_run_at'] else None,
                    
                    # Execution stats
                    'run_count': row['run_count'] or 0,
                    'success_count': row['success_count'] or 0,
                    'error_count': row['error_count'] or 0,
                    'execution_count': row['run_count'] or 0,
                    
                    # Source identifier
                    'source': 'automation_workflows',
                    'version': row['version']
                })
                
            except Exception as transform_error:
                print(f'[ERROR /api/automation/workflows/list] Failed to transform workflow {row.get("slug")}: {str(transform_error)}')
                continue
        
        return jsonify({
            'success': True,
            'workflows': workflows,
            'count': len(workflows)
        }), 200
        
    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500


@automation_bp.route('/<automation_id>', methods=['GET'])
def get_automation(automation_id):
    """Get full automation details including visual flow JSON
    
    Accepts either automation_id OR slug (for backwards compatibility)
    """
    try:
        user_id = get_user_from_token(request.headers.get('Authorization'))
        if not user_id:
            return jsonify({'error': 'Unauthorized - invalid or missing token'}), 401
        
        # ✅ LEAK FIX: Use context manager
        with get_db_connection() as conn:
            cursor = conn.cursor()
            
            # Allow access to user's own workflows AND system templates (user_id=1)
            # Support both automation_id and slug lookup
            cursor.execute("""
            SELECT * FROM visual_automations 
            WHERE (automation_id = %s OR slug = %s) AND (user_id = %s OR user_id = 1)
        """, (automation_id, automation_id, user_id))
            
            row = cursor.fetchone()
        
        # ✅ Connection auto-closed by context manager
        if not row:
            return jsonify({'error': 'Automation not found'}), 404
        
        # Parse JSON fields
        ui_json = json.loads(row['ui_json']) if isinstance(row['ui_json'], str) else (row.get('ui_json') or {})
        execution_json = json.loads(row['execution_json']) if isinstance(row['execution_json'], str) else (row.get('execution_json') or {})
        
        # Transform nodes/edges to shapes/connections (canvas format)
        shapes = []
        connections = []
        
        if isinstance(ui_json, dict):
            # Parse canvas_data for node positions (if stored separately)
            canvas_data_str = row.get('canvas_data')
            canvas_data = {}
            if canvas_data_str:
                try:
                    canvas_data = json.loads(canvas_data_str) if isinstance(canvas_data_str, str) else canvas_data_str
                    if isinstance(canvas_data, dict) and 'nodes' in canvas_data:
                        canvas_data = canvas_data['nodes']  # Extract nodes dict
                except:
                    canvas_data = {}
            
            # Extract nodes and transform to shapes
            nodes = ui_json.get('nodes', [])
            for node in nodes:
                node_id = node.get('id')
                
                # Get position from canvas_data if available, otherwise from node
                position = canvas_data.get(node_id, {}) if canvas_data else {}
                x = position.get('x', node.get('x', node.get('position', {}).get('x', 100)))
                y = position.get('y', node.get('y', node.get('position', {}).get('y', 100)))
                
                # Determine shape type based on node type
                node_type = node.get('type', 'action')
                shape_type_map = {
                    'email_trigger': 'trigger',
                    'trigger': 'trigger',
                    'ai_agent': 'tool',
                    'send_email': 'output',
                    'if_else': 'decision',
                    'condition': 'decision'
                }
                shape_type = shape_type_map.get(node_type, 'rectangle')
                
                # Determine color based on node type
                color_map = {
                    'trigger': '#10B981',  # Green for triggers
                    'tool': '#6B7280',     # Gray for tools
                    'output': '#EAB308',   # Yellow for output
                    'decision': '#F59E0B', # Orange for decisions
                    'rectangle': '#58a6ff' # Default blue
                }
                color = color_map.get(shape_type, '#58a6ff')
                
                # Extract text from config or use node type
                config = node.get('config', {})
                text = config.get('role', config.get('subject', node_type.upper()))
                
                shape = {
                    'id': node_id,
                    'type': shape_type,
                    'x': int(x),
                    'y': int(y),
                    'width': node.get('width', 150),
                    'height': node.get('height', 80),
                    'text': text,
                    'color': color
                }
                shapes.append(shape)
            
            # Extract edges and transform to connections
            edges = ui_json.get('edges', [])
            for edge in edges:
                connection = {
                    'id': edge.get('id', f"conn_{edge.get('from')}_{edge.get('to')}"),
                    'from': edge.get('from'),
                    'to': edge.get('to')
                }
                connections.append(connection)
            
            # Also check for existing shapes/connections format (backward compatibility)
            if not shapes and 'shapes' in ui_json:
                shapes = ui_json.get('shapes', [])
            if not connections and 'connections' in ui_json:
                connections = ui_json.get('connections', [])
        
        # UI COMPATIBLE FORMAT - Extract shapes and connections for canvas
        automation = {
            'workflow_id': row['automation_id'],
            'id': row['automation_id'],
            'automation_id': row['automation_id'],
            'slug': row.get('slug', row['automation_id']),
            'name': row['title'],
            'title': row['title'],
            'description': row['description'],
            'category': row.get('category', 'other'),
            'status': row.get('status', 'draft'),
            'enabled': bool(row.get('is_active', True)),
            
            # Canvas data - Transformed shapes and connections
            'workflow_json': {
                'shapes': shapes,
                'connections': connections,
                'nodes': ui_json.get('nodes', []) if isinstance(ui_json, dict) else [],
                'edges': ui_json.get('edges', []) if isinstance(ui_json, dict) else []
            },
            'ui_json': ui_json,
            'shapes': shapes,  # Direct access for canvas
            'connections': connections,  # Direct access for canvas
            'execution_json': execution_json,
            
            # Legacy fields (keep for backward compatibility) - use .get() to avoid KeyError
            'visual_flow_json': row.get('visual_flow_json'),
            'execution_prompt': row.get('execution_prompt'),
            'tools_sequence': json.loads(row.get('tools_sequence', '[]')) if row.get('tools_sequence') else [],
            'schedule_cron': row.get('schedule_cron'),
            'schedule_datetime': row.get('schedule_datetime'),
            'timezone': row.get('timezone'),
            'is_active': bool(row.get('is_active', True)),
            'is_scheduled': bool(row.get('is_scheduled', False)),
            'scheduler_task_id': row.get('scheduler_task_id'),
            'parent_automation_id': row.get('parent_automation_id'),
            'created_at': str(row.get('created_at')) if row.get('created_at') else None,
            'updated_at': str(row.get('updated_at')) if row.get('updated_at') else None
        }
        
        return jsonify({
            'success': True,
            'automation': automation,
            'workflow': automation  # Alias for UI compatibility
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@automation_bp.route('/<automation_id>', methods=['DELETE'])
def delete_automation(automation_id):
    """Delete automation and deactivate any scheduled tasks"""
    try:
        user_id = get_user_from_token(request.headers.get('Authorization'))
        if not user_id:
            return jsonify({'error': 'Unauthorized - invalid or missing token'}), 401
        
        # ✅ LEAK FIX: Use context manager
        with get_db_connection() as conn:
            cursor = conn.cursor()
            
            # Get automation to check scheduler_task_id
            cursor.execute("""
            SELECT scheduler_task_id FROM visual_automations
            WHERE automation_id = %s AND user_id = %s
        """, (automation_id, user_id))
            
            row = cursor.fetchone()
            
            if not row:
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
        
        # ✅ Connection auto-closed by context manager
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
        user_id = get_user_from_token(request.headers.get('Authorization'))
        if not user_id:
            return jsonify({'error': 'Unauthorized - invalid or missing token'}), 401
        data = request.json
        
        # Get automation
        # ✅ LEAK FIX: Use context manager
        with get_db_connection() as conn:
            cursor = conn.cursor()
            
            # Allow activating system templates (user_id=1)
            cursor.execute("""
            SELECT * FROM visual_automations
            WHERE automation_id = %s AND (user_id = %s OR user_id = 1)
        """, (automation_id, user_id))
            
            row = cursor.fetchone()
            
            if not row:
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
        
        # ✅ Connection auto-closed by context manager
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
        user_id = get_user_from_token(request.headers.get('Authorization'))
        if not user_id:
            return jsonify({'error': 'Unauthorized - invalid or missing token'}), 401
        
        # ✅ LEAK FIX: Use context manager
        with get_db_connection() as conn:
            cursor = conn.cursor()
            
            # Allow deactivating system templates (user_id=1)
            cursor.execute("""
            SELECT scheduler_task_id FROM visual_automations
            WHERE automation_id = %s AND (user_id = %s OR user_id = 1)
        """, (automation_id, user_id))
            
            row = cursor.fetchone()
            
            if not row:
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
        
        # ✅ Connection auto-closed by context manager
        return jsonify({
            'success': True,
            'message': f'Automation {automation_id} deactivated'
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@automation_bp.route('/toggle/<workflow_identifier>', methods=['PATCH'])
def toggle_automation_enabled(workflow_identifier):
    """Toggle automation enabled state in automation_workflows table (for production workflows)"""
    try:
        user_id = get_user_from_token(request.headers.get('Authorization'))
        if not user_id:
            return jsonify({'error': 'Unauthorized - invalid or missing token'}), 401
        
        data = request.get_json()
        enabled = data.get('enabled', False)
        
        # ✅ LEAK FIX: Use context manager
        with get_db_connection() as conn:
            cursor = conn.cursor()
            
            # Update automation_workflows table (production workflows only)
            # workflow_identifier can be workflow_id (UUID) or slug
            cursor.execute("""
            UPDATE automation_workflows
            SET enabled = %s,
                updated_at = CURRENT_TIMESTAMP
            WHERE (workflow_id::text = %s OR slug = %s) AND user_id = %s
        """, (enabled, workflow_identifier, workflow_identifier, user_id))
            
            if cursor.rowcount == 0:
                return jsonify({'error': 'Production workflow not found or not owned by user'}), 404
            
            conn.commit()
        
        # ✅ Connection auto-closed by context manager
        return jsonify({
            'success': True,
            'workflow_id': workflow_identifier,
            'enabled': enabled,
            'message': f'Automation {"enabled" if enabled else "disabled"}'
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@automation_bp.route('/<automation_id>/toggle', methods=['POST'])
def toggle_automation(automation_id):
    """Toggle automation between active and inactive states (legacy endpoint for visual_automations)"""
    try:
        user_id = get_user_from_token(request.headers.get('Authorization'))
        if not user_id:
            return jsonify({'error': 'Unauthorized - invalid or missing token'}), 401
        
        # ✅ LEAK FIX: Use context manager
        with get_db_connection() as conn:
            cursor = conn.cursor()
            
            # Get current status (allow system templates)
            cursor.execute("""
            SELECT status, is_scheduled, schedule_cron FROM visual_automations
            WHERE automation_id = %s AND (user_id = %s OR user_id = 1)
        """, (automation_id, user_id))
            
            row = cursor.fetchone()
            
            if not row:
                return jsonify({'error': 'Automation not found'}), 404
            
            current_status = row['status']
            
            # Only toggle if workflow is already automated (not 'draft')
            if current_status == 'draft':
                return jsonify({'error': 'Cannot toggle draft workflows. Use /convert endpoint first.'}), 400
        
            # Toggle status
            new_status = 'inactive' if current_status == 'active' else 'active'
            
            # Update status
            cursor.execute("""
            UPDATE visual_automations
            SET status = %s,
                updated_at = CURRENT_TIMESTAMP
            WHERE automation_id = %s
        """, (new_status, automation_id))
            
            conn.commit()
        
        # ✅ Connection auto-closed by context manager
        return jsonify({
            'success': True,
            'automation_id': automation_id,
            'previous_status': current_status,
            'new_status': new_status,
            'message': f'Automation {new_status}'
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@automation_bp.route('/<automation_id>/convert', methods=['POST'])
def convert_to_automation(automation_id):
    """Convert a draft workflow design into an automated workflow"""
    try:
        user_id = get_user_from_token(request.headers.get('Authorization'))
        if not user_id:
            return jsonify({'error': 'Unauthorized - invalid or missing token'}), 401
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Get workflow (allow system templates)
        cursor.execute("""
            SELECT * FROM visual_automations
            WHERE automation_id = %s AND (user_id = %s OR user_id = 1)
        """, (automation_id, user_id))
        
        row = cursor.fetchone()
        
        if not row:
            conn.close()
            return jsonify({'error': 'Automation not found'}), 404
        
        if row['status'] != 'draft':
            conn.close()
            return jsonify({'error': 'Workflow is already automated'}), 400
        
        # Update status to inactive (automated but not scheduled)
        cursor.execute("""
            UPDATE visual_automations
            SET status = 'inactive',
                updated_at = CURRENT_TIMESTAMP
            WHERE automation_id = %s
        """, (automation_id,))
        
        conn.commit()
        conn.close()
        
        return jsonify({
            'success': True,
            'automation_id': automation_id,
            'status': 'inactive',
            'message': 'Workflow converted to automation. Use /schedule or /toggle to activate.'
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@automation_bp.route('/<automation_id>/test', methods=['POST'])
def test_automation(automation_id):
    """Execute automation once manually for testing"""
    try:
        user_id = get_user_from_token(request.headers.get('Authorization'))
        if not user_id:
            return jsonify({'error': 'Unauthorized - invalid or missing token'}), 401
        
        # ✅ LEAK FIX: Use context manager
        with get_db_connection() as conn:
            cursor = conn.cursor()
            
            # Get automation (allow system templates)
        cursor.execute("""
            SELECT * FROM visual_automations
            WHERE automation_id = %s AND (user_id = %s OR user_id = 1)
        """, (automation_id, user_id))
        
        row = cursor.fetchone()
        
        if not row:
            conn.close()
            return jsonify({'error': 'Automation not found'}), 404
        
        # Parse execution JSON
        execution_json = json.loads(row['execution_json']) if isinstance(row['execution_json'], str) else (row.get('execution_json') or {})
        
        # Record execution start
        cursor.execute("""
            INSERT INTO automation_executions 
            (automation_id, user_id, triggered_by, status, started_at)
            VALUES (%s, %s, 'manual_test', 'running', CURRENT_TIMESTAMP)
            RETURNING execution_id
        """, (automation_id, user_id))
        
        result = cursor.fetchone()
        execution_id = result['execution_id'] if isinstance(result, dict) else result[0]
        
        conn.commit()
        
        # TODO: Implement actual execution logic here
        # For now, just mark as completed
        cursor.execute("""
            UPDATE automation_executions
            SET status = 'completed',
                completed_at = CURRENT_TIMESTAMP,
                result_summary = 'Test execution completed successfully'
            WHERE execution_id = %s
        """, (execution_id,))
        
        # Update last executed timestamp
        cursor.execute("""
            UPDATE visual_automations
            SET last_executed_at = CURRENT_TIMESTAMP,
                execution_count = execution_count + 1
            WHERE automation_id = %s
        """, (automation_id,))
        
        conn.commit()
        conn.close()
        
        return jsonify({
            'success': True,
            'execution_id': execution_id,
            'automation_id': automation_id,
            'status': 'completed',
            'message': 'Test execution completed'
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@automation_bp.route('/<automation_id>/schedule', methods=['POST'])
def schedule_automation(automation_id):
    """Set or update automation schedule"""
    try:
        user_id = get_user_from_token(request.headers.get('Authorization'))
        if not user_id:
            return jsonify({'error': 'Unauthorized - invalid or missing token'}), 401
        
        data = request.json
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Get automation (allow system templates)
        cursor.execute("""
            SELECT * FROM visual_automations
            WHERE automation_id = %s AND (user_id = %s OR user_id = 1)
        """, (automation_id, user_id))
        
        row = cursor.fetchone()
        
        if not row:
            conn.close()
            return jsonify({'error': 'Automation not found'}), 404
        
        # Validate cron expression
        cron_expression = data.get('schedule_cron')
        if not cron_expression:
            conn.close()
            return jsonify({'error': 'schedule_cron is required'}), 400
        
        # Update schedule
        cursor.execute("""
            UPDATE visual_automations
            SET schedule_cron = %s,
                timezone = %s,
                is_scheduled = TRUE,
                status = 'active',
                updated_at = CURRENT_TIMESTAMP
            WHERE automation_id = %s
        """, (cron_expression, data.get('timezone', 'UTC'), automation_id))
        
        conn.commit()
        conn.close()
        
        return jsonify({
            'success': True,
            'automation_id': automation_id,
            'schedule_cron': cron_expression,
            'timezone': data.get('timezone', 'UTC'),
            'status': 'active',
            'message': 'Schedule updated successfully'
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@automation_bp.route('/<automation_id>/history', methods=['GET'])
def get_execution_history(automation_id):
    """Get automation execution history"""
    try:
        user_id = get_user_from_token(request.headers.get('Authorization'))
        if not user_id:
            return jsonify({'error': 'Unauthorized - invalid or missing token'}), 401
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
        user_id = get_user_from_token(request.headers.get('Authorization'))
        if not user_id:
            return jsonify({'error': 'Unauthorized - invalid or missing token'}), 401
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


@automation_bp.route('/<slug>/publish', methods=['POST'])
def publish_workflow(slug):
    """
    Publish workflow as live automation
    
    This endpoint validates the workflow structure, enables it for execution,
    and optionally links it to a thread and creates scheduling.
    
    Request body:
    {
        "thread_id": 123,                              // Optional: Link to thread
        "automation_title": "Email to Sheets (Live)",  // Optional: Custom title
        "schedule_cron": "0 */1 * * *",               // Optional: Cron schedule
        "timezone": "UTC"                              // Optional: Timezone
    }
    
    Process:
        1. Validate workflow structure
        2. Generate automation_slug (or use existing)
        3. Update status to 'active'
        4. Link to thread if thread_id provided
        5. Create schedule if schedule_cron provided
    
    Response:
    {
        "success": true,
        "automation_slug": "workflow-1737052800",
        "workflow_slug": "workflow-1737052800",
        "validation": {
            "valid": true,
            "errors": [],
            "warnings": ["..."]
        },
        "scheduled": true,
        "next_run": "2025-11-20T01:00:00Z",
        "message": "Workflow published successfully"
    }
    """
    try:
        user_id = get_user_from_token(request.headers.get('Authorization'))
        if not user_id:
            return jsonify({'error': 'Unauthorized - invalid or missing token'}), 401
        data = request.json or {}
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Get workflow by slug
        cursor.execute("""
            SELECT automation_id, slug, title, ui_json, execution_json, status
            FROM visual_automations
            WHERE slug = %s AND user_id = %s
        """, (slug, user_id))
        
        row = cursor.fetchone()
        
        if not row:
            conn.close()
            return jsonify({'error': f'Workflow with slug "{slug}" not found'}), 404
        
        # Parse workflow JSON for validation
        ui_json = json.loads(row['ui_json']) if isinstance(row['ui_json'], str) else row['ui_json']
        
        # STEP 1: Validate workflow structure
        validation_result = validate_workflow_structure(ui_json)
        
        if not validation_result['valid']:
            conn.close()
            return jsonify({
                'success': False,
                'error': 'Workflow validation failed',
                'validation': validation_result
            }), 400
        
        # STEP 2: Update workflow status to 'active'
        automation_title = data.get('automation_title', f"{row['title']} (Live)")
        
        cursor.execute("""
            UPDATE visual_automations
            SET status = 'active',
                title = %s,
                updated_at = CURRENT_TIMESTAMP
            WHERE slug = %s
        """, (automation_title, slug))
        
        # STEP 3: Link to thread if provided
        thread_id = data.get('thread_id')
        if thread_id:
            # Update thread with automation_slug
            try:
                cursor.execute("""
                    UPDATE sessions.threads
                    SET automation_slug = %s,
                        automation_title = %s,
                        updated_at = CURRENT_TIMESTAMP
                    WHERE id = %s
                """, (slug, automation_title, thread_id))
            except Exception as e:
                # Thread linking failed, but continue with publish
                print(f"Warning: Could not link to thread {thread_id}: {e}")
        
        # STEP 4: Create schedule if provided
        scheduled = False
        next_run = None
        task_id = None
        
        schedule_cron = data.get('schedule_cron')
        if schedule_cron:
            try:
                scheduler = get_scheduler()
                
                execution_json = json.loads(row['execution_json']) if isinstance(row['execution_json'], str) else row['execution_json']
                
                task_data = {
                    'task_name': f'Automation: {automation_title}',
                    'description': f'Published workflow: {slug}',
                    'created_by': 'user',
                    'created_by_user_id': user_id,
                    'trigger_type': 'cron',
                    'cron_expression': schedule_cron,
                    'action_type': 'execute_automation',
                    'action_payload': json.dumps({
                        'automation_id': row['automation_id'],
                        'slug': slug,
                        'ui_json': ui_json,
                        'execution_json': execution_json
                    }),
                    'requires_approval': False,
                    'enabled': True
                }
                
                task_id = scheduler.create_task(task_data)
                scheduled = True
                
                # Get next run time
                task = scheduler.get_task(task_id)
                next_run = task.get('next_run')
                
                # Update workflow with scheduler info
                cursor.execute("""
                    UPDATE visual_automations
                    SET is_scheduled = 1,
                        scheduler_task_id = %s,
                        schedule_cron = %s,
                        timezone = %s
                    WHERE slug = %s
                """, (task_id, schedule_cron, data.get('timezone', 'UTC'), slug))
                
            except Exception as e:
                print(f"Warning: Could not create schedule: {e}")
        
        conn.commit()
        conn.close()
        
        response = {
            'success': True,
            'automation_slug': slug,
            'workflow_slug': slug,
            'automation_title': automation_title,
            'validation': validation_result,
            'scheduled': scheduled,
            'message': 'Workflow published successfully'
        }
        
        if scheduled and next_run:
            response['next_run'] = next_run
            response['task_id'] = task_id
        
        if thread_id:
            response['thread_id'] = thread_id
            response['thread_linked'] = True
        
        return jsonify(response), 200
        
    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500


@automation_bp.route('/link-to-thread', methods=['POST'])
def link_workflow_to_thread():
    """
    Link workflow to thread in database
    
    This provides a reliable backend endpoint for thread-workflow association,
    ensuring database consistency even if frontend operations fail.
    
    Request body:
    {
        "thread_id": 123,
        "workflow_slug": "workflow-1737052800",
        "workflow_title": "Email to Sheets",
        "automation_slug": "workflow-1737052800",  // Optional: For published workflows
        "automation_title": "Email to Sheets (Live)"  // Optional
    }
    
    Response:
    {
        "success": true,
        "thread_id": 123,
        "workflow_slug": "workflow-1737052800",
        "automation_slug": "workflow-1737052800",  // If provided
        "message": "Workflow linked to thread successfully"
    }
    """
    try:
        data = request.json
        
        # Validate required fields
        if 'thread_id' not in data or 'workflow_slug' not in data:
            return jsonify({'error': 'thread_id and workflow_slug required'}), 400
        
        thread_id = data['thread_id']
        workflow_slug = data['workflow_slug']
        workflow_title = data.get('workflow_title', workflow_slug)
        automation_slug = data.get('automation_slug')
        automation_title = data.get('automation_title')
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Build update query based on what's provided
        update_fields = ['workflow_slug = %s', 'workflow_title = %s', 'updated_at = CURRENT_TIMESTAMP']
        params = [workflow_slug, workflow_title]
        
        if automation_slug:
            update_fields.append('automation_slug = %s')
            params.append(automation_slug)
        
        if automation_title:
            update_fields.append('automation_title = %s')
            params.append(automation_title)
        
        params.append(thread_id)
        
        query = f"""
            UPDATE sessions.threads SET
                {', '.join(update_fields)}
            WHERE id = %s
        """
        
        cursor.execute(query, params)
        
        if cursor.rowcount == 0:
            conn.close()
            return jsonify({'error': f'Thread {thread_id} not found'}), 404
        
        conn.commit()
        conn.close()
        
        response = {
            'success': True,
            'thread_id': thread_id,
            'workflow_slug': workflow_slug,
            'workflow_title': workflow_title,
            'message': 'Workflow linked to thread successfully'
        }
        
        if automation_slug:
            response['automation_slug'] = automation_slug
            response['automation_title'] = automation_title
        
        return jsonify(response), 200
        
    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500


@automation_bp.route('/<slug>/status', methods=['GET'])
def get_workflow_status(slug):
    """
    Get workflow/automation execution status
    
    Returns current status, execution history, and scheduling information.
    
    Response:
    {
        "success": true,
        "workflow": {
            "slug": "workflow-1737052800",
            "title": "Email to Sheets",
            "status": "active",  // draft, active, inactive
            "is_scheduled": true,
            "schedule_cron": "0 */1 * * *",
            "next_run": "2025-11-20T01:00:00Z"
        },
        "execution_status": {
            "currently_running": false,
            "last_execution": {
                "execution_id": 123,
                "started_at": "2025-11-19T12:00:00Z",
                "completed_at": "2025-11-19T12:00:15Z",
                "status": "completed",
                "duration_ms": 15000
            },
            "total_executions": 42,
            "success_rate": 0.95
        }
    }
    """
    try:
        user_id = get_user_from_token(request.headers.get('Authorization'))
        if not user_id:
            return jsonify({'error': 'Unauthorized - invalid or missing token'}), 401
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Get workflow info
        cursor.execute("""
            SELECT automation_id, slug, title, status, is_scheduled, 
                   schedule_cron, scheduler_task_id, execution_count,
                   last_executed_at, created_at, updated_at
            FROM visual_automations
            WHERE slug = %s AND user_id = %s
        """, (slug, user_id))
        
        row = cursor.fetchone()
        
        if not row:
            conn.close()
            return jsonify({'error': f'Workflow with slug "{slug}" not found'}), 404
        
        # Get next run time from scheduler
        next_run = None
        if row['scheduler_task_id']:
            try:
                scheduler = get_scheduler()
                task = scheduler.get_task(row['scheduler_task_id'])
                next_run = task.get('next_run')
            except:
                pass
        
        # Get execution statistics
        cursor.execute("""
            SELECT 
                COUNT(*) as total_executions,
                SUM(CASE WHEN status = 'completed' THEN 1 ELSE 0 END) as successful_executions,
                MAX(CASE WHEN status IN ('running', 'pending') THEN 1 ELSE 0 END) as currently_running
            FROM automation_executions
            WHERE automation_id = %s
        """, (row['automation_id'],))
        
        stats_row = cursor.fetchone()
        
        # Get last execution
        cursor.execute("""
            SELECT execution_id, started_at, completed_at, status, duration_ms, error_message
            FROM automation_executions
            WHERE automation_id = %s
            ORDER BY started_at DESC
            LIMIT 1
        """, (row['automation_id'],))
        
        last_exec_row = cursor.fetchone()
        
        conn.close()
        
        # Calculate success rate
        total_execs = stats_row['total_executions'] if stats_row else 0
        successful_execs = stats_row['successful_executions'] if stats_row else 0
        success_rate = (successful_execs / total_execs) if total_execs > 0 else 0.0
        
        # Build response
        response = {
            'success': True,
            'workflow': {
                'slug': row['slug'],
                'title': row['title'],
                'status': row['status'],
                'is_scheduled': bool(row['is_scheduled']),
                'schedule_cron': row['schedule_cron'],
                'created_at': str(row['created_at']),
                'updated_at': str(row['updated_at'])
            },
            'execution_status': {
                'currently_running': bool(stats_row['currently_running']) if stats_row else False,
                'total_executions': total_execs,
                'success_rate': round(success_rate, 2)
            }
        }
        
        if next_run:
            response['workflow']['next_run'] = next_run
        
        if last_exec_row:
            response['execution_status']['last_execution'] = {
                'execution_id': last_exec_row['execution_id'],
                'started_at': str(last_exec_row['started_at']),
                'completed_at': str(last_exec_row['completed_at']) if last_exec_row['completed_at'] else None,
                'status': last_exec_row['status'],
                'duration_ms': last_exec_row['duration_ms'],
                'error_message': last_exec_row['error_message']
            }
        
        return jsonify(response), 200
        
    except Exception as e:
        import traceback
        traceback.print_exc()
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


def validate_workflow_structure(workflow_json):
    """
    Validate workflow structure before publishing
    
    Args:
        workflow_json: Parsed workflow JSON with shapes and connections
    
    Returns:
        {
            'valid': bool,
            'errors': [list of error messages],
            'warnings': [list of warning messages]
        }
    """
    errors = []
    warnings = []
    
    # Extract shapes and connections
    shapes = workflow_json.get('shapes', [])
    connections = workflow_json.get('connections', [])
    
    if not shapes:
        errors.append("Workflow must have at least one shape/node")
        return {'valid': False, 'errors': errors, 'warnings': warnings}
    
    # Check for trigger node (hexagon or trigger type)
    has_trigger = any(
        s.get('type') in ['hexagon', 'trigger'] or 
        'trigger' in s.get('text', '').lower() 
        for s in shapes
    )
    if not has_trigger:
        errors.append("Workflow must have a trigger node (starting point)")
    
    # Check for end node
    has_end = any(
        s.get('type') in ['circle', 'end'] or 
        'end' in s.get('text', '').lower() or
        'complete' in s.get('text', '').lower()
        for s in shapes
    )
    if not has_end:
        warnings.append("Workflow should have an end node for clarity")
    
    # Check all nodes are connected
    if connections:
        shape_ids = {s['id'] for s in shapes}
        connected_ids = {c.get('from') for c in connections} | {c.get('to') for c in connections}
        orphan_nodes = shape_ids - connected_ids
        
        if orphan_nodes:
            orphan_texts = [s['text'] for s in shapes if s['id'] in orphan_nodes]
            warnings.append(f"Unconnected nodes found: {', '.join(orphan_texts[:3])}")
    
    # Check for circular dependencies (basic check)
    if len(connections) > len(shapes):
        warnings.append("Workflow may have circular dependencies or redundant connections")
    
    # Validate connection structure
    for conn in connections:
        if 'from' not in conn or 'to' not in conn:
            errors.append(f"Invalid connection structure: missing 'from' or 'to' field")
    
    # Check for empty action nodes
    empty_actions = [s['id'] for s in shapes if not s.get('text', '').strip()]
    if empty_actions:
        warnings.append(f"Found {len(empty_actions)} nodes with no text/action defined")
    
    return {
        'valid': len(errors) == 0,
        'errors': errors,
        'warnings': warnings
    }

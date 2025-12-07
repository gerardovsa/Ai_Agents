"""
Scheduler API Routes
====================
API endpoints for managing scheduled automation tasks.

Endpoints:
    POST   /api/scheduler/tasks              - Create new task
    GET    /api/scheduler/tasks              - List all tasks
    GET    /api/scheduler/tasks/<task_id>    - Get task details
    PATCH  /api/scheduler/tasks/<task_id>    - Update task
    DELETE /api/scheduler/tasks/<task_id>    - Delete task
    POST   /api/scheduler/tasks/<task_id>/execute - Manual execution
    POST   /api/scheduler/tasks/<task_id>/approve - Approve task
    POST   /api/scheduler/tasks/<task_id>/reject  - Reject task
    GET    /api/scheduler/tasks/<task_id>/history - Get execution history
    POST   /api/webhook/scheduler/trigger/<task_id> - Webhook trigger
"""

from flask import Blueprint, request, jsonify
from datetime import datetime
import json
import sys
from pathlib import Path

# Add parent directory for imports
sys.path.insert(0, str(Path(__file__).parent.parent))
from scheduler import get_scheduler

scheduler_bp = Blueprint('scheduler', __name__)


@scheduler_bp.route('/api/scheduler/tasks', methods=['POST'])
def create_task():
    """
    Create a new scheduled task
    
    Request body:
    {
        "task_name": "Send Daily Report",
        "description": "Email daily analytics report",
        "created_by": "user",  // or "ai"
        "created_by_user_id": 1,
        
        "trigger_type": "cron",  // "cron", "datetime", "webhook", "conditional", "manual"
        "cron_expression": "0 9 * * 1-5",  // Mon-Fri at 9am
        "datetime_trigger": "2025-11-16T14:00:00Z",  // For one-time
        
        "action_type": "resume_session",  // "resume_session", "send_message", "execute_tool", "run_workflow"
        "synergy_session_id": "sess_12345678",
        "thread_id": "thread_abc123",
        "agent_name": "Email Agent",
        "location": "synergy_sidebar",
        
        "action_payload": {  // Action-specific data
            "message": "Generate and send report",
            "tools": ["gmail_send_email"],
            "context": {}
        },
        "context_instructions": "Include last 7 days of data",
        
        "requires_approval": false,
        "enabled": true,
        "tags": ["reports", "email", "daily"],
        "priority": 7,
        "timeout_seconds": 300,
        "max_retries": 3,
        "retry_delay_seconds": 300
    }
    """
    try:
        data = request.json
        
        # Validate required fields
        required_fields = ['task_name', 'trigger_type', 'action_type']
        for field in required_fields:
            if field not in data:
                return jsonify({'error': f'Missing required field: {field}'}), 400
        
        # Validate trigger configuration
        trigger_type = data['trigger_type']
        if trigger_type == 'cron' and not data.get('cron_expression'):
            return jsonify({'error': 'cron_expression required for cron trigger'}), 400
        if trigger_type == 'datetime' and not data.get('datetime_trigger'):
            return jsonify({'error': 'datetime_trigger required for datetime trigger'}), 400
        
        # Convert action_payload to JSON string if dict
        if 'action_payload' in data and isinstance(data['action_payload'], dict):
            data['action_payload'] = json.dumps(data['action_payload'])
        
        # Convert tags to JSON string if list
        if 'tags' in data and isinstance(data['tags'], list):
            data['tags'] = json.dumps(data['tags'])
        
        # Create task
        scheduler = get_scheduler()
        task_id = scheduler.create_task(data)
        
        # Get created task
        task = scheduler.get_task(task_id)
        
        return jsonify({
            'success': True,
            'task_id': task_id,
            'task': task,
            'message': f'Task "{data["task_name"]}" created successfully'
        }), 201
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@scheduler_bp.route('/api/scheduler/tasks', methods=['GET'])
def list_tasks():
    """
    List scheduled tasks with optional filters
    
    Query parameters:
        synergy_session_id - Filter by session
        thread_id - Filter by thread
        agent_name - Filter by agent
        enabled - Filter by enabled status (true/false)
        created_by - Filter by creator (user/ai)
    """
    try:
        filters = {}
        
        if request.args.get('synergy_session_id'):
            filters['synergy_session_id'] = request.args.get('synergy_session_id')
        if request.args.get('thread_id'):
            filters['thread_id'] = request.args.get('thread_id')
        if request.args.get('agent_name'):
            filters['agent_name'] = request.args.get('agent_name')
        if request.args.get('enabled'):
            filters['enabled'] = request.args.get('enabled').lower() == 'true'
        if request.args.get('created_by'):
            filters['created_by'] = request.args.get('created_by')
        
        scheduler = get_scheduler()
        tasks = scheduler.list_tasks(filters)
        
        # Parse JSON fields for frontend
        for task in tasks:
            if task.get('action_payload'):
                try:
                    task['action_payload'] = json.loads(task['action_payload'])
                except:
                    pass
            if task.get('tags'):
                try:
                    task['tags'] = json.loads(task['tags'])
                except:
                    pass
        
        return jsonify({
            'success': True,
            'tasks': tasks,
            'count': len(tasks)
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@scheduler_bp.route('/api/scheduler/tasks/<task_id>', methods=['GET'])
def get_task(task_id):
    """Get task details by ID"""
    try:
        scheduler = get_scheduler()
        task = scheduler.get_task(task_id)
        
        if not task:
            return jsonify({'error': 'Task not found'}), 404
        
        # Parse JSON fields
        if task.get('action_payload'):
            try:
                task['action_payload'] = json.loads(task['action_payload'])
            except:
                pass
        if task.get('tags'):
            try:
                task['tags'] = json.loads(task['tags'])
            except:
                pass
        
        return jsonify({
            'success': True,
            'task': task
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@scheduler_bp.route('/api/scheduler/tasks/<task_id>', methods=['PATCH'])
def update_task(task_id):
    """
    Update task fields
    
    Request body can include any task fields to update
    """
    try:
        data = request.json
        
        # Convert complex fields to JSON strings
        if 'action_payload' in data and isinstance(data['action_payload'], dict):
            data['action_payload'] = json.dumps(data['action_payload'])
        if 'tags' in data and isinstance(data['tags'], list):
            data['tags'] = json.dumps(data['tags'])
        
        scheduler = get_scheduler()
        success = scheduler.update_task(task_id, data)
        
        if not success:
            return jsonify({'error': 'Task not found or update failed'}), 404
        
        # Get updated task
        task = scheduler.get_task(task_id)
        
        return jsonify({
            'success': True,
            'task': task,
            'message': 'Task updated successfully'
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@scheduler_bp.route('/api/scheduler/tasks/<task_id>', methods=['DELETE'])
def delete_task(task_id):
    """Delete a scheduled task"""
    try:
        scheduler = get_scheduler()
        success = scheduler.delete_task(task_id)
        
        if not success:
            return jsonify({'error': 'Task not found'}), 404
        
        return jsonify({
            'success': True,
            'message': f'Task {task_id} deleted successfully'
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@scheduler_bp.route('/api/scheduler/tasks/<task_id>/execute', methods=['POST'])
def execute_task(task_id):
    """Manually trigger task execution"""
    try:
        scheduler = get_scheduler()
        task = scheduler.get_task(task_id)
        
        if not task:
            return jsonify({'error': 'Task not found'}), 404
        
        # Execute task immediately
        scheduler._execute_task(task_id)
        
        return jsonify({
            'success': True,
            'message': f'Task {task_id} execution triggered'
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@scheduler_bp.route('/api/scheduler/tasks/<task_id>/approve', methods=['POST'])
def approve_task(task_id):
    """
    Approve a task that requires approval
    
    Request body:
    {
        "approved_by_user_id": 1,
        "approval_note": "Approved for production use"
    }
    """
    try:
        data = request.json
        
        updates = {
            'approval_status': 'approved',
            'approved_by_user_id': data.get('approved_by_user_id'),
            'approval_note': data.get('approval_note', ''),
            'approved_at': datetime.now().isoformat()
        }
        
        scheduler = get_scheduler()
        success = scheduler.update_task(task_id, updates)
        
        if not success:
            return jsonify({'error': 'Task not found'}), 404
        
        # Task will be automatically scheduled after approval
        
        return jsonify({
            'success': True,
            'message': 'Task approved and scheduled',
            'task_id': task_id
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@scheduler_bp.route('/api/scheduler/tasks/<task_id>/reject', methods=['POST'])
def reject_task(task_id):
    """
    Reject a task that requires approval
    
    Request body:
    {
        "approved_by_user_id": 1,
        "approval_note": "Security concerns - needs review"
    }
    """
    try:
        data = request.json
        
        updates = {
            'approval_status': 'rejected',
            'approved_by_user_id': data.get('approved_by_user_id'),
            'approval_note': data.get('approval_note', ''),
            'approved_at': datetime.now().isoformat(),
            'enabled': False  # Disable rejected tasks
        }
        
        scheduler = get_scheduler()
        success = scheduler.update_task(task_id, updates)
        
        if not success:
            return jsonify({'error': 'Task not found'}), 404
        
        return jsonify({
            'success': True,
            'message': 'Task rejected',
            'task_id': task_id
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@scheduler_bp.route('/api/scheduler/tasks/<task_id>/history', methods=['GET'])
def get_task_history(task_id):
    """
    Get execution history for a task
    
    Query parameters:
        limit - Max number of executions to return (default: 50)
    """
    try:
        limit = int(request.args.get('limit', 50))
        
        scheduler = get_scheduler()
        history = scheduler.get_execution_history(task_id, limit)
        
        # Parse result_data JSON
        for execution in history:
            if execution.get('result_data'):
                try:
                    execution['result_data'] = json.loads(execution['result_data'])
                except:
                    pass
        
        return jsonify({
            'success': True,
            'task_id': task_id,
            'executions': history,
            'count': len(history)
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@scheduler_bp.route('/api/webhook/scheduler/trigger/<task_id>', methods=['POST'])
def webhook_trigger(task_id):
    """
    Webhook endpoint for external systems to trigger tasks
    
    Request body can include additional context data
    """
    try:
        scheduler = get_scheduler()
        task = scheduler.get_task(task_id)
        
        if not task:
            return jsonify({'error': 'Task not found'}), 404
        
        if task['trigger_type'] != 'webhook' and task['trigger_type'] != 'manual':
            return jsonify({'error': 'Task does not support webhook triggers'}), 400
        
        # Execute task
        scheduler._execute_task(task_id)
        
        return jsonify({
            'success': True,
            'message': f'Task {task_id} triggered via webhook',
            'task_name': task['task_name']
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

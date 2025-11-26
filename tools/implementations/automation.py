"""
FILE: tools/implementations/automation.py
PURPOSE: Visual automation workflow creation, management, and execution tools

DEPENDENCIES:
- requests - HTTP client for API calls
- json - JSON parsing
- typing - Type hints

EXPORTS:
- automation_create_workflow(title, actions, **kwargs) - Create new workflow
- automation_update_workflow(slug, add_actions, remove_actions, **kwargs) - Update existing workflow
- automation_list_workflows(**kwargs) - List user's workflows
- automation_get_workflow(automation_id, **kwargs) - Get workflow details
- automation_execute_workflow(automation_id, **kwargs) - Execute workflow
- automation_schedule_workflow(automation_id, schedule_cron, **kwargs) - Schedule workflow
- automation_deactivate_workflow(automation_id, **kwargs) - Deactivate workflow
- automation_delete_workflow(automation_id, **kwargs) - Delete workflow
- automation_get_execution_history(automation_id, **kwargs) - Get execution history
- automation_export_workflow(automation_id, **kwargs) - Export workflow JSON
- automation_get_workflow_by_slug(slug, **kwargs) - Get workflow by slug
- automation_open_workflow_in_canvas(slug, message_to_user, **kwargs) - Open workflow in UI
- automation_publish_workflow(slug, thread_id, **kwargs) - Publish workflow as live automation
- automation_get_workflow_status(slug, **kwargs) - Get workflow execution status

USED BY:
- AI agents via tools registry for workflow automation

NOTES:
- All functions use credential injection via **kwargs
- API endpoint: https://ai-agents-backend-singapore.onrender.com/api/automation/ (default, configurable via API_BASE_URL env var)
- Returns standardized JSON responses

LAST MODIFIED: 2025-11-20 - Added automation_update_workflow for programmatic workflow updates
"""

import requests
import json
import random
import string
import sys
from pathlib import Path
from typing import Dict, Any, List, Optional
from datetime import datetime

# Add AI_infrastructure to path for direct database access
sys.path.insert(0, str(Path(__file__).parent.parent.parent / 'AI_infrastructure'))
from shared.database_utils import get_database_connection


class AutomationError(Exception):
    """Custom exception for automation errors"""
    pass


def _generate_unique_slug() -> str:
    """Generate unique workflow slug: wf_<8-random-chars>_<timestamp>"""
    random_chars = ''.join(random.choices(string.ascii_lowercase + string.digits, k=8))
    timestamp = int(datetime.now().timestamp())
    return f"wf_{random_chars}_{timestamp}"


def _get_api_url() -> str:
    """Get API base URL from environment or default to Render deployment"""
    import os
    return os.getenv('API_BASE_URL', 'https://ai-agents-backend-singapore.onrender.com')


def _get_headers(kwargs: dict) -> dict:
    """Build request headers with authentication"""
    jwt_token = kwargs.get('jwt_token') or kwargs.get('access_token')
    user_id = kwargs.get('_user_id', 1)
    
    return {
        'Content-Type': 'application/json',
        'Authorization': f'Bearer {jwt_token}' if jwt_token else '',
        'X-User-ID': str(user_id)
    }


def automation_create_workflow(
    title: str,
    actions: List[Dict[str, Any]],
    description: Optional[str] = None,
    trigger: Optional[Dict[str, Any]] = None,
    category: str = 'other',
    **kwargs
) -> Dict[str, Any]:
    """
    Create a new visual automation workflow
    
    Args:
        title: Workflow title
        actions: List of action objects with tool, parameters, and optional condition
        description: What this workflow does (optional)
        trigger: Trigger configuration (manual, schedule, webhook, event)
        category: Workflow category for organization
        **kwargs: Credential injection (jwt_token, _user_id)
    
    Returns:
        Dict with automation_id, slug, visual_flow_json, and creation metadata
    
    Raises:
        AutomationError: If creation fails
    
    Example:
        result = automation_create_workflow(
            title="Daily Email Summary",
            description="Summarize unread emails every morning",
            trigger={"type": "schedule", "schedule_cron": "0 9 * * *"},
            actions=[
                {"tool": "gmail_list_messages", "parameters": {"max_results": 10}},
                {"tool": "ai_summarize_text", "parameters": {"text": "{{emails}}"}}
            ],
            category="email"
        )
    """
    try:
        api_url = _get_api_url()
        headers = _get_headers(kwargs)
        
        # Generate automation ID
        automation_id = f"auto_{int(datetime.now().timestamp())}"
        
        # Build visual flow (convert actions to nodes)
        shapes = []
        connections = []
        
        # Add trigger node
        if trigger:
            shapes.append({
                'id': f'node_trigger',
                'type': 'hexagon',
                'x': 100,
                'y': 100,
                'width': 150,
                'height': 80,
                'text': f"TRIGGER: {trigger.get('type', 'manual')}",
                'color': '#10B981'
            })
        
        # Add action nodes
        for idx, action in enumerate(actions):
            node_id = f'node_action_{idx}'
            prev_node = f'node_trigger' if idx == 0 else f'node_action_{idx-1}'
            
            shapes.append({
                'id': node_id,
                'type': 'diamond' if action.get('condition') else 'rectangle',
                'x': 100,
                'y': 200 + (idx * 150),
                'width': 150,
                'height': 80,
                'text': action['tool'],
                'color': '#F59E0B' if action.get('condition') else '#3B82F6'
            })
            
            connections.append({
                'id': f'conn_{idx}',
                'from': prev_node,
                'to': node_id
            })
        
        visual_flow_json = json.dumps({
            'shapes': shapes,
            'connections': connections
        })
        
        # Build execution prompt
        execution_prompt = f"Execute workflow '{title}':\n"
        for idx, action in enumerate(actions):
            execution_prompt += f"{idx + 1}. {action['tool']} with {action['parameters']}\n"
        
        # Prepare request payload
        payload = {
            'automation_id': automation_id,
            'title': title,
            'description': description or '',
            'visual_flow_json': visual_flow_json,
            'execution_prompt': execution_prompt,
            'tools_sequence': [a['tool'] for a in actions],
            'category': category,
            'slug': _generate_unique_slug(),  # Use unique slug format: wf_<random>_<timestamp>
            'schedule_cron': trigger.get('schedule_cron') if trigger and trigger.get('type') == 'schedule' else None
        }
        
        # Call API
        response = requests.post(
            f'{api_url}/api/automation/save',
            json=payload,
            headers=headers
        )
        response.raise_for_status()
        
        result = response.json()
        return {
            'success': True,
            'automation_id': automation_id,
            'slug': payload['slug'],
            'title': title,
            'visual_flow_json': visual_flow_json,
            'message': f"Workflow '{title}' created successfully with {len(actions)} actions"
        }
        
    except requests.exceptions.RequestException as e:
        raise AutomationError(f"Failed to create workflow: {str(e)}")
    except Exception as e:
        raise AutomationError(f"Error creating workflow: {str(e)}")


def automation_update_workflow(
    slug: str,
    add_actions: Optional[List[Dict[str, Any]]] = None,
    remove_actions: Optional[List[int]] = None,
    update_trigger: Optional[Dict[str, Any]] = None,
    update_action_parameters: Optional[Dict[str, Any]] = None,
    update_metadata: Optional[Dict[str, Any]] = None,
    **kwargs
) -> Dict[str, Any]:
    """
    Update an existing workflow - add/remove actions, modify trigger, change parameters
    UI automatically refreshes canvas after update
    
    Args:
        slug: Workflow slug (wf_<8random>_<timestamp>) - REQUIRED
        add_actions: Actions to add (with optional position)
        remove_actions: Array of action positions to remove
        update_trigger: New trigger configuration
        update_action_parameters: Update parameters of existing action
        update_metadata: Update title/description
        **kwargs: Credential injection (jwt_token, _user_id)
    
    Returns:
        Dict with updated workflow, action_count, visual_flow_json, message
    
    Raises:
        AutomationError: If update fails
    
    Examples:
        # Add email notification
        automation_update_workflow(
            slug='wf_a3f8b2c1_1732029847',
            add_actions=[{
                'tool': 'gmail_send_email',
                'parameters': {'to': 'user@example.com', 'subject': 'Done'}
            }]
        )
        
        # Change schedule to every 2 hours
        automation_update_workflow(
            slug='wf_a3f8b2c1_1732029847',
            update_trigger={'type': 'schedule', 'schedule_cron': '0 */2 * * *'}
        )
        
        # Remove first action
        automation_update_workflow(
            slug='wf_a3f8b2c1_1732029847',
            remove_actions=[0]
        )
    """
    if not slug:
        raise AutomationError("slug is required")
    
    if not slug.startswith('wf_'):
        raise AutomationError(f"Invalid slug format: {slug} (must start with 'wf_')")
    
    # Build update payload
    payload = {'slug': slug}
    
    if add_actions:
        payload['add_actions'] = add_actions
    
    if remove_actions:
        payload['remove_actions'] = remove_actions
    
    if update_trigger:
        payload['update_trigger'] = update_trigger
    
    if update_action_parameters:
        payload['update_action_parameters'] = update_action_parameters
    
    if update_metadata:
        payload['update_metadata'] = update_metadata
    
    # At least one update operation required
    if not any([add_actions, remove_actions, update_trigger, update_action_parameters, update_metadata]):
        raise AutomationError("At least one update operation required (add_actions, remove_actions, update_trigger, update_action_parameters, or update_metadata)")
    
    api_url = _get_api_url()
    headers = _get_headers(kwargs)
    
    try:
        response = requests.put(
            f'{api_url}/api/automation/update',
            json=payload,
            headers=headers,
            timeout=30
        )
        
        if response.status_code == 404:
            raise AutomationError(f"Workflow not found: {slug}")
        
        if response.status_code == 400:
            error_data = response.json()
            raise AutomationError(f"Invalid update: {error_data.get('error', 'Unknown error')}")
        
        response.raise_for_status()
        data = response.json()
        
        # Build success message
        changes = []
        if add_actions:
            changes.append(f"added {len(add_actions)} action(s)")
        if remove_actions:
            changes.append(f"removed {len(remove_actions)} action(s)")
        if update_trigger:
            changes.append("updated trigger")
        if update_action_parameters:
            changes.append(f"updated action {update_action_parameters.get('position', '?')} parameters")
        if update_metadata:
            changes.append("updated metadata")
        
        changes_text = ", ".join(changes)
        
        return {
            'success': True,
            'automation_id': data.get('automation_id'),
            'slug': slug,
            'action_count': data.get('action_count', 0),
            'visual_flow_json': data.get('visual_flow_json'),
            'ui_refreshed': True,
            'message': f"Workflow updated successfully: {changes_text}. UI canvas has auto-refreshed."
        }
        
    except requests.exceptions.RequestException as e:
        raise AutomationError(f"Failed to update workflow: {str(e)}")
    except Exception as e:
        raise AutomationError(f"Error updating workflow: {str(e)}")


def automation_list_workflows(
    category: Optional[str] = None,
    status: str = 'all',
    limit: int = 50,
    **kwargs
) -> List[Dict[str, Any]]:
    """
    List all saved automation workflows
    
    Args:
        category: Filter by category (optional)
        status: Filter by status (draft, active, inactive, all)
        limit: Max workflows to return
        **kwargs: Credential injection (_user_id)
    
    Returns:
        List of workflows with metadata
    """
    try:
        # Get user_id from kwargs
        user_id = kwargs.get('_user_id', 1)
        
        # Connect directly to Supabase PostgreSQL
        conn = get_database_connection('ai_infrastructure')
        cursor = conn.cursor()
        
        # Build query - include user's workflows + system templates (user_id=1)
        query = """
            SELECT automation_id, slug, title, description, category, status,
                   ui_json, execution_json, is_scheduled, schedule_cron,
                   created_at, updated_at, last_executed_at, execution_count,
                   user_id
            FROM visual_automations
            WHERE user_id = %s OR user_id = 1
        """
        params = [user_id]
        
        # Add filters
        if category:
            query += " AND category = %s"
            params.append(category)
        
        if status != 'all':
            query += " AND status = %s"
            params.append(status)
        
        query += " ORDER BY updated_at DESC LIMIT %s"
        params.append(limit)
        
        # Execute query
        cursor.execute(query, params)
        rows = cursor.fetchall()
        conn.close()
        
        # Transform rows to workflow dictionaries
        workflows = []
        for row in rows:
            # Parse JSON fields
            ui_json = json.loads(row['ui_json']) if isinstance(row['ui_json'], str) else row['ui_json']
            execution_json = json.loads(row['execution_json']) if isinstance(row['execution_json'], str) else row['execution_json']
            
            workflows.append({
                'automation_id': row['automation_id'],
                'slug': row['slug'],
                'title': row['title'],
                'description': row['description'],
                'category': row['category'],
                'status': row['status'],
                'is_scheduled': row['is_scheduled'],
                'schedule_cron': row['schedule_cron'],
                'execution_count': row['execution_count'],
                'last_executed_at': str(row['last_executed_at']) if row['last_executed_at'] else None,
                'created_at': str(row['created_at']) if row['created_at'] else None,
                'updated_at': str(row['updated_at']) if row['updated_at'] else None,
                'user_id': row['user_id'],
                'ui_json': ui_json,
                'execution_json': execution_json
            })
        
        return {
            'success': True,
            'count': len(workflows),
            'workflows': workflows
        }
        
    except Exception as e:
        raise AutomationError(f"Failed to list workflows: {str(e)}")


def automation_get_workflow(
    automation_id: str,
    **kwargs
) -> Dict[str, Any]:
    """
    Get detailed workflow information
    
    Args:
        automation_id: Workflow ID or slug
        **kwargs: Credential injection (_user_id)
    
    Returns:
        Workflow details with nodes, connections, and execution data
    """
    try:
        # Get user_id from kwargs
        user_id = kwargs.get('_user_id', 1)
        
        # Connect directly to Supabase PostgreSQL
        conn = get_database_connection('ai_infrastructure')
        cursor = conn.cursor()
        
        # Query by automation_id or slug, include system templates (user_id=1)
        cursor.execute("""
            SELECT * FROM visual_automations 
            WHERE (automation_id = %s OR slug = %s) 
            AND (user_id = %s OR user_id = 1)
        """, (automation_id, automation_id, user_id))
        
        row = cursor.fetchone()
        conn.close()
        
        if not row:
            raise AutomationError(f"Workflow not found: {automation_id}")
        
        # Parse JSON fields
        ui_json = json.loads(row['ui_json']) if isinstance(row['ui_json'], str) else row['ui_json']
        execution_json = json.loads(row['execution_json']) if isinstance(row['execution_json'], str) else row['execution_json']
        
        return {
            'success': True,
            'automation_id': row['automation_id'],
            'slug': row['slug'],
            'title': row['title'],
            'description': row['description'],
            'category': row['category'],
            'status': row['status'],
            'is_scheduled': row['is_scheduled'],
            'schedule_cron': row['schedule_cron'],
            'execution_count': row['execution_count'],
            'last_executed_at': str(row['last_executed_at']) if row['last_executed_at'] else None,
            'created_at': str(row['created_at']) if row['created_at'] else None,
            'updated_at': str(row['updated_at']) if row['updated_at'] else None,
            'user_id': row['user_id'],
            'ui_json': ui_json,
            'execution_json': execution_json
        }
        
    except Exception as e:
        raise AutomationError(f"Failed to get workflow: {str(e)}")


def automation_execute_workflow(
    automation_id: str,
    input_data: Optional[Dict[str, Any]] = None,
    thread_id: Optional[int] = None,
    **kwargs
) -> Dict[str, Any]:
    """
    Execute a workflow immediately
    
    Args:
        automation_id: Workflow ID or slug
        input_data: Optional input data to pass to workflow
        thread_id: Optional thread ID to associate execution
        **kwargs: Credential injection
    
    Returns:
        Execution result with execution_id, status, and output
    """
    try:
        api_url = _get_api_url()
        headers = _get_headers(kwargs)
        
        payload = {
            'input_data': input_data or {},
            'thread_id': thread_id
        }
        
        response = requests.post(
            f'{api_url}/api/automation/{automation_id}/execute',
            json=payload,
            headers=headers
        )
        response.raise_for_status()
        
        return response.json()
        
    except requests.exceptions.RequestException as e:
        raise AutomationError(f"Failed to execute workflow: {str(e)}")


def automation_schedule_workflow(
    automation_id: str,
    schedule_cron: str,
    timezone: str = 'UTC',
    **kwargs
) -> Dict[str, Any]:
    """
    Schedule a workflow to run automatically
    
    Args:
        automation_id: Workflow ID
        schedule_cron: Cron expression (e.g., '0 9 * * *')
        timezone: Timezone for schedule
        **kwargs: Credential injection
    
    Returns:
        Schedule confirmation with scheduler_task_id
    """
    try:
        api_url = _get_api_url()
        headers = _get_headers(kwargs)
        
        payload = {
            'schedule_cron': schedule_cron,
            'timezone': timezone
        }
        
        response = requests.post(
            f'{api_url}/api/automation/{automation_id}/activate',
            json=payload,
            headers=headers
        )
        response.raise_for_status()
        
        return response.json()
        
    except requests.exceptions.RequestException as e:
        raise AutomationError(f"Failed to schedule workflow: {str(e)}")


def automation_deactivate_workflow(
    automation_id: str,
    **kwargs
) -> Dict[str, Any]:
    """
    Deactivate a scheduled workflow
    
    Args:
        automation_id: Workflow ID
        **kwargs: Credential injection
    
    Returns:
        Deactivation confirmation
    """
    try:
        api_url = _get_api_url()
        headers = _get_headers(kwargs)
        
        response = requests.post(
            f'{api_url}/api/automation/{automation_id}/deactivate',
            headers=headers
        )
        response.raise_for_status()
        
        return response.json()
        
    except requests.exceptions.RequestException as e:
        raise AutomationError(f"Failed to deactivate workflow: {str(e)}")


def automation_delete_workflow(
    automation_id: str,
    **kwargs
) -> Dict[str, Any]:
    """
    Delete a workflow permanently
    
    Args:
        automation_id: Workflow ID
        **kwargs: Credential injection
    
    Returns:
        Deletion confirmation
    """
    try:
        api_url = _get_api_url()
        headers = _get_headers(kwargs)
        
        response = requests.delete(
            f'{api_url}/api/automation/{automation_id}',
            headers=headers
        )
        response.raise_for_status()
        
        return response.json()
        
    except requests.exceptions.RequestException as e:
        raise AutomationError(f"Failed to delete workflow: {str(e)}")


def automation_get_execution_history(
    automation_id: str,
    limit: int = 20,
    status_filter: str = 'all',
    **kwargs
) -> List[Dict[str, Any]]:
    """
    Get execution history for a workflow
    
    Args:
        automation_id: Workflow ID or slug
        limit: Max executions to return
        status_filter: Filter by status (success, failure, running, all)
        **kwargs: Credential injection (_user_id)
    
    Returns:
        List of executions with timestamps, status, and results
    """
    try:
        user_id = kwargs.get('_user_id', 1)
        
        conn = get_database_connection('ai_infrastructure')
        cursor = conn.cursor()
        
        # Build query with optional status filter
        query = """
            SELECT execution_id, automation_id, status, started_at, completed_at,
                   duration_ms, error_message, input_data, output_data
            FROM automation_executions
            WHERE automation_id = %s
        """
        params = [automation_id]
        
        if status_filter != 'all':
            query += " AND status = %s"
            params.append(status_filter)
        
        query += " ORDER BY started_at DESC LIMIT %s"
        params.append(limit)
        
        cursor.execute(query, params)
        rows = cursor.fetchall()
        conn.close()
        
        executions = []
        for row in rows:
            executions.append({
                'execution_id': row['execution_id'],
                'automation_id': row['automation_id'],
                'status': row['status'],
                'started_at': str(row['started_at']) if row['started_at'] else None,
                'completed_at': str(row['completed_at']) if row['completed_at'] else None,
                'duration_ms': row['duration_ms'],
                'error_message': row['error_message'],
                'input_data': json.loads(row['input_data']) if row['input_data'] else None,
                'output_data': json.loads(row['output_data']) if row['output_data'] else None
            })
        
        return {
            'success': True,
            'count': len(executions),
            'executions': executions
        }
        
    except Exception as e:
        raise AutomationError(f"Failed to get execution history: {str(e)}")


def automation_export_workflow(
    automation_id: str,
    include_history: bool = False,
    **kwargs
) -> Dict[str, Any]:
    """
    Export workflow as JSON
    
    Args:
        automation_id: Workflow ID or slug
        include_history: Include execution history in export
        **kwargs: Credential injection (_user_id)
    
    Returns:
        Workflow JSON export
    """
    try:
        user_id = kwargs.get('_user_id', 1)
        
        conn = get_database_connection('ai_infrastructure')
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT * FROM visual_automations 
            WHERE (automation_id = %s OR slug = %s) AND (user_id = %s OR user_id = 1)
        """, (automation_id, automation_id, user_id))
        
        row = cursor.fetchone()
        
        if not row:
            conn.close()
            raise AutomationError(f"Workflow not found: {automation_id}")
        
        # Parse JSON fields
        ui_json = json.loads(row['ui_json']) if isinstance(row['ui_json'], str) else row['ui_json']
        execution_json = json.loads(row['execution_json']) if isinstance(row['execution_json'], str) else row['execution_json']
        
        export_data = {
            'automation_id': row['automation_id'],
            'slug': row['slug'],
            'title': row['title'],
            'description': row['description'],
            'category': row['category'],
            'status': row['status'],
            'ui_json': ui_json,
            'execution_json': execution_json,
            'is_scheduled': row['is_scheduled'],
            'schedule_cron': row['schedule_cron'],
            'created_at': str(row['created_at']) if row['created_at'] else None,
            'updated_at': str(row['updated_at']) if row['updated_at'] else None
        }
        
        # Include execution history if requested
        if include_history:
            cursor.execute("""
                SELECT execution_id, status, started_at, completed_at, duration_ms, error_message
                FROM automation_executions
                WHERE automation_id = %s
                ORDER BY started_at DESC
                LIMIT 50
            """, (row['automation_id'],))
            
            history_rows = cursor.fetchall()
            export_data['execution_history'] = [{
                'execution_id': h['execution_id'],
                'status': h['status'],
                'started_at': str(h['started_at']) if h['started_at'] else None,
                'completed_at': str(h['completed_at']) if h['completed_at'] else None,
                'duration_ms': h['duration_ms'],
                'error_message': h['error_message']
            } for h in history_rows]
        
        conn.close()
        
        return {
            'success': True,
            'export': export_data
        }
        
    except Exception as e:
        raise AutomationError(f"Failed to export workflow: {str(e)}")


def automation_get_workflow_by_slug(
    slug: str,
    **kwargs
) -> Dict[str, Any]:
    """
    Get workflow details by slug
    
    Args:
        slug: Workflow slug (e.g., 'workflow-email-to-sheets', 'workflow-1234567890')
        **kwargs: Credential injection (_user_id)
    
    Returns:
        Dict with workflow details:
        - success: Boolean
        - workflow: Workflow object with id, slug, title, description, ui_json, execution_json, status, etc.
        - message: Success message
    
    Raises:
        AutomationError: If workflow not found or fetch fails
    
    Example:
        >>> result = automation_get_workflow_by_slug('workflow-email-to-sheets')
        >>> print(result['workflow']['title'])
        'Email to Google Sheets'
        >>> print(result['workflow']['ui_json']['shapes'])
        [{'type': 'trigger', 'text': 'New Gmail', ...}, ...]
    """
    try:
        user_id = kwargs.get('_user_id', 1)
        
        conn = get_database_connection('ai_infrastructure')
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT * FROM visual_automations 
            WHERE slug = %s AND (user_id = %s OR user_id = 1)
        """, (slug, user_id))
        
        row = cursor.fetchone()
        conn.close()
        
        if not row:
            raise AutomationError(f"Workflow not found: {slug}")
        
        # Parse JSON fields
        ui_json = json.loads(row['ui_json']) if isinstance(row['ui_json'], str) else row['ui_json']
        execution_json = json.loads(row['execution_json']) if isinstance(row['execution_json'], str) else row['execution_json']
        
        workflow = {
            'automation_id': row['automation_id'],
            'slug': row['slug'],
            'title': row['title'],
            'description': row['description'],
            'category': row['category'],
            'status': row['status'],
            'is_scheduled': row['is_scheduled'],
            'schedule_cron': row['schedule_cron'],
            'execution_count': row['execution_count'],
            'last_executed_at': str(row['last_executed_at']) if row['last_executed_at'] else None,
            'created_at': str(row['created_at']) if row['created_at'] else None,
            'updated_at': str(row['updated_at']) if row['updated_at'] else None,
            'user_id': row['user_id'],
            'ui_json': ui_json,
            'execution_json': execution_json
        }
        
        return {
            'success': True,
            'workflow': workflow,
            'message': f"Workflow '{workflow.get('title')}' retrieved successfully"
        }
    
    except Exception as e:
        raise AutomationError(f"Failed to get workflow: {str(e)}")


def automation_open_workflow_in_canvas(
    slug: str,
    message_to_user: str = None,
    **kwargs
) -> Dict[str, Any]:
    """
    Open workflow in visual automation canvas
    
    This tool triggers a frontend event to switch to the Automation tab
    and load the specified workflow for visual editing.
    
    Args:
        slug: Workflow slug (e.g., 'workflow-email-to-sheets')
        message_to_user: Optional message to display to user
        **kwargs: Credential injection
    
    Returns:
        Dict with:
        - success: Boolean
        - ui_command: Command for frontend ('open_workflow')
        - slug: Workflow slug
        - workflow_title: Workflow title
        - message: Message to display
        - instructions: Instructions for user
    
    Example:
        >>> result = automation_open_workflow_in_canvas(
        ...     'workflow-email-to-sheets',
        ...     'Here is your email automation workflow.'
        ... )
        >>> print(result['ui_command'])
        'open_workflow'
        >>> print(result['message'])
        'Opening workflow "Email to Sheets" in canvas...'
    """
    # First verify workflow exists and get its title
    workflow_data = automation_get_workflow_by_slug(slug, **kwargs)
    workflow = workflow_data['workflow']
    
    return {
        'success': True,
        'ui_command': 'open_workflow',
        'slug': slug,
        'workflow_title': workflow['title'],
        'message': message_to_user or f"Opening workflow '{workflow['title']}' in canvas...",
        'instructions': 'The workflow is now displayed in the Automation Canvas. You can edit shapes, connections, and settings visually.'
    }


def automation_publish_workflow(
    slug: str,
    thread_id: Optional[int] = None,
    automation_title: Optional[str] = None,
    schedule_cron: Optional[str] = None,
    timezone: str = 'UTC',
    **kwargs
) -> Dict[str, Any]:
    """
    Publish a draft workflow as a live automation
    
    This function validates the workflow structure, activates it for execution,
    optionally schedules it with a cron expression, and links it to a thread.
    
    Args:
        slug: Workflow slug to publish (e.g., 'workflow-1737052800')
        thread_id: Thread ID to link the automation to (optional)
        automation_title: Custom title for live automation (optional, adds '(Live)' if not provided)
        schedule_cron: Cron expression for scheduling (optional, e.g., '0 9 * * *')
        timezone: Timezone for schedule (optional, defaults to 'UTC')
        **kwargs: Credential injection (jwt_token, _user_id)
    
    Returns:
        Dict with:
        - success: Boolean
        - automation_slug: Published automation slug
        - workflow_slug: Original workflow slug
        - automation_title: Title of published automation
        - validation: Validation result with errors/warnings
        - scheduled: Whether automation was scheduled
        - next_run: Next execution time (if scheduled)
        - task_id: Scheduler task ID (if scheduled)
        - thread_id: Linked thread ID (if provided)
        - thread_linked: Whether thread linking succeeded
        - message: Success message
    
    Raises:
        AutomationError: If publishing fails or validation errors exist
    
    Example:
        >>> result = automation_publish_workflow(
        ...     slug='workflow-email-processor',
        ...     thread_id=123,
        ...     schedule_cron='0 */1 * * *',
        ...     timezone='America/New_York'
        ... )
        >>> print(result['message'])
        'Workflow published successfully'
        >>> print(result['next_run'])
        '2025-11-20T01:00:00Z'
    """
    try:
        api_url = _get_api_url()
        headers = _get_headers(kwargs)
        
        # Build request payload
        payload = {
            'thread_id': thread_id,
            'automation_title': automation_title,
            'schedule_cron': schedule_cron,
            'timezone': timezone
        }
        
        # Remove None values
        payload = {k: v for k, v in payload.items() if v is not None}
        
        # Call publish endpoint
        response = requests.post(
            f'{api_url}/api/automation/{slug}/publish',
            json=payload,
            headers=headers,
            timeout=30
        )
        
        if response.status_code == 400:
            # Validation failed
            data = response.json()
            error_msg = data.get('error', 'Workflow validation failed')
            validation = data.get('validation', {})
            
            error_details = []
            if validation.get('errors'):
                error_details.append(f"Errors: {', '.join(validation['errors'])}")
            if validation.get('warnings'):
                error_details.append(f"Warnings: {', '.join(validation['warnings'])}")
            
            full_error = f"{error_msg}. {' '.join(error_details)}" if error_details else error_msg
            raise AutomationError(full_error)
        
        response.raise_for_status()
        data = response.json()
        
        if not data.get('success'):
            raise AutomationError(data.get('error', 'Unknown error during publish'))
        
        return {
            'success': True,
            'automation_slug': data['automation_slug'],
            'workflow_slug': data['workflow_slug'],
            'automation_title': data['automation_title'],
            'validation': data['validation'],
            'scheduled': data.get('scheduled', False),
            'next_run': data.get('next_run'),
            'task_id': data.get('task_id'),
            'thread_id': data.get('thread_id'),
            'thread_linked': data.get('thread_linked', False),
            'message': data['message']
        }
        
    except requests.exceptions.RequestException as e:
        raise AutomationError(f'Failed to publish workflow: {str(e)}')
    except Exception as e:
        raise AutomationError(f'Unexpected error during publish: {str(e)}')


def automation_get_workflow_status(
    slug: str,
    **kwargs
) -> Dict[str, Any]:
    """
    Get workflow/automation execution status
    
    Returns current status, execution history, scheduling information,
    and performance statistics for a workflow.
    
    Args:
        slug: Workflow slug (e.g., 'workflow-1737052800')
        **kwargs: Credential injection (jwt_token, _user_id)
    
    Returns:
        Dict with:
        - success: Boolean
        - workflow: Workflow metadata
            - slug: Workflow slug
            - title: Workflow title
            - status: Current status (draft, active, inactive)
            - is_scheduled: Whether workflow is scheduled
            - schedule_cron: Cron expression (if scheduled)
            - next_run: Next execution time (if scheduled)
            - created_at: Creation timestamp
            - updated_at: Last update timestamp
        - execution_status: Execution statistics
            - currently_running: Whether workflow is currently executing
            - total_executions: Total number of runs
            - success_rate: Success rate (0.0 to 1.0)
            - last_execution: Last execution details
                - execution_id: Execution ID
                - started_at: Start timestamp
                - completed_at: Completion timestamp
                - status: Execution status (completed, failed, running)
                - duration_ms: Execution duration in milliseconds
                - error_message: Error message (if failed)
    
    Raises:
        AutomationError: If status check fails or workflow not found
    
    Example:
        >>> result = automation_get_workflow_status('workflow-email-to-sheets')
        >>> print(f"Status: {result['workflow']['status']}")
        Status: active
        >>> print(f"Success rate: {result['execution_status']['success_rate']*100:.1f}%")
        Success rate: 95.2%
        >>> if result['workflow']['is_scheduled']:
        ...     print(f"Next run: {result['workflow']['next_run']}")
        Next run: 2025-11-20T09:00:00Z
    """
    try:
        user_id = kwargs.get('_user_id', 1)
        
        conn = get_database_connection('ai_infrastructure')
        cursor = conn.cursor()
        
        # Get workflow metadata
        cursor.execute("""
            SELECT automation_id, slug, title, status, is_scheduled, schedule_cron,
                   execution_count, created_at, updated_at, last_executed_at
            FROM visual_automations 
            WHERE slug = %s AND (user_id = %s OR user_id = 1)
        """, (slug, user_id))
        
        row = cursor.fetchone()
        
        if not row:
            conn.close()
            raise AutomationError(f'Workflow with slug "{slug}" not found')
        
        workflow_data = {
            'slug': row['slug'],
            'title': row['title'],
            'status': row['status'],
            'is_scheduled': row['is_scheduled'],
            'schedule_cron': row['schedule_cron'],
            'created_at': str(row['created_at']) if row['created_at'] else None,
            'updated_at': str(row['updated_at']) if row['updated_at'] else None,
            'last_executed_at': str(row['last_executed_at']) if row['last_executed_at'] else None
        }
        
        # Get execution statistics
        cursor.execute("""
            SELECT 
                COUNT(*) as total_executions,
                SUM(CASE WHEN status = 'completed' THEN 1 ELSE 0 END) as successful,
                MAX(started_at) as last_execution_time
            FROM automation_executions
            WHERE automation_id = %s
        """, (row['automation_id'],))
        
        stats_row = cursor.fetchone()
        
        # Get last execution details
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
        total_execs = stats_row['total_executions'] or 0
        successful_execs = stats_row['successful'] or 0
        success_rate = successful_execs / total_execs if total_execs > 0 else 0.0
        
        execution_status = {
            'currently_running': last_exec_row['status'] == 'running' if last_exec_row else False,
            'total_executions': total_execs,
            'success_rate': success_rate,
            'last_execution': {
                'execution_id': last_exec_row['execution_id'],
                'started_at': str(last_exec_row['started_at']) if last_exec_row['started_at'] else None,
                'completed_at': str(last_exec_row['completed_at']) if last_exec_row['completed_at'] else None,
                'status': last_exec_row['status'],
                'duration_ms': last_exec_row['duration_ms'],
                'error_message': last_exec_row['error_message']
            } if last_exec_row else None
        }
        
        return {
            'success': True,
            'workflow': workflow_data,
            'execution_status': execution_status
        }
        
    except Exception as e:
        raise AutomationError(f'Failed to get workflow status: {str(e)}')

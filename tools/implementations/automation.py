"""
FILE: tools/implementations/automation.py
PURPOSE: Visual automation workflow creation, management, and execution tools

DEPENDENCIES:
- requests - HTTP client for API calls
- json - JSON parsing
- typing - Type hints

EXPORTS:
- automation_create_workflow(title, actions, **kwargs) - Create new workflow
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

USED BY:
- AI agents via tools registry for workflow automation

NOTES:
- All functions use credential injection via **kwargs
- API endpoint: http://localhost:5001/api/automation/
- Returns standardized JSON responses

LAST MODIFIED: 2025-11-16 - Initial creation for automation canvas integration
"""

import requests
import json
from typing import Dict, Any, List, Optional
from datetime import datetime


class AutomationError(Exception):
    """Custom exception for automation errors"""
    pass


def _get_api_url() -> str:
    """Get API base URL from environment or default to localhost"""
    import os
    return os.getenv('API_BASE_URL', 'http://localhost:5001')


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
            'slug': f"workflow_{title.lower().replace(' ', '_')}",
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
        **kwargs: Credential injection
    
    Returns:
        List of workflows with metadata
    """
    try:
        api_url = _get_api_url()
        headers = _get_headers(kwargs)
        
        params = {'limit': limit}
        if category:
            params['category'] = category
        if status != 'all':
            params['status'] = status
        
        response = requests.get(
            f'{api_url}/api/automation/list',
            params=params,
            headers=headers
        )
        response.raise_for_status()
        
        result = response.json()
        workflows = result.get('automations', [])
        
        return {
            'success': True,
            'count': len(workflows),
            'workflows': workflows
        }
        
    except requests.exceptions.RequestException as e:
        raise AutomationError(f"Failed to list workflows: {str(e)}")


def automation_get_workflow(
    automation_id: str,
    **kwargs
) -> Dict[str, Any]:
    """
    Get detailed workflow information
    
    Args:
        automation_id: Workflow ID or slug
        **kwargs: Credential injection
    
    Returns:
        Workflow details with nodes, connections, and execution data
    """
    try:
        api_url = _get_api_url()
        headers = _get_headers(kwargs)
        
        response = requests.get(
            f'{api_url}/api/automation/{automation_id}',
            headers=headers
        )
        response.raise_for_status()
        
        return response.json()
        
    except requests.exceptions.RequestException as e:
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
        automation_id: Workflow ID
        limit: Max executions to return
        status_filter: Filter by status (success, failure, running, all)
        **kwargs: Credential injection
    
    Returns:
        List of executions with timestamps, status, and results
    """
    try:
        api_url = _get_api_url()
        headers = _get_headers(kwargs)
        
        params = {'limit': limit}
        if status_filter != 'all':
            params['status'] = status_filter
        
        response = requests.get(
            f'{api_url}/api/automation/{automation_id}/history',
            params=params,
            headers=headers
        )
        response.raise_for_status()
        
        return response.json()
        
    except requests.exceptions.RequestException as e:
        raise AutomationError(f"Failed to get execution history: {str(e)}")


def automation_export_workflow(
    automation_id: str,
    include_history: bool = False,
    **kwargs
) -> Dict[str, Any]:
    """
    Export workflow as JSON
    
    Args:
        automation_id: Workflow ID
        include_history: Include execution history in export
        **kwargs: Credential injection
    
    Returns:
        Workflow JSON export
    """
    try:
        api_url = _get_api_url()
        headers = _get_headers(kwargs)
        
        params = {'include_history': include_history}
        
        response = requests.get(
            f'{api_url}/api/automation/{automation_id}/export',
            params=params,
            headers=headers
        )
        response.raise_for_status()
        
        return response.json()
        
    except requests.exceptions.RequestException as e:
        raise AutomationError(f"Failed to export workflow: {str(e)}")


def automation_get_workflow_by_slug(
    slug: str,
    **kwargs
) -> Dict[str, Any]:
    """
    Get workflow details by slug
    
    Args:
        slug: Workflow slug (e.g., 'workflow-email-to-sheets', 'workflow-1234567890')
        **kwargs: Credential injection (user_id, access_token, etc.)
    
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
        api_url = _get_api_url()
        headers = _get_headers(kwargs)
        
        # Query by slug using /list endpoint with slug parameter
        response = requests.get(
            f'{api_url}/api/automation/list',
            params={'slug': slug},
            headers=headers,
            timeout=10
        )
        response.raise_for_status()
        data = response.json()
        
        workflows = data.get('workflows', [])
        if not workflows:
            raise AutomationError(f"Workflow not found: {slug}")
        
        workflow = workflows[0]
        
        # Parse JSON fields if they're strings
        if isinstance(workflow.get('ui_json'), str):
            workflow['ui_json'] = json.loads(workflow['ui_json'])
        if isinstance(workflow.get('execution_json'), str):
            workflow['execution_json'] = json.loads(workflow['execution_json'])
        
        return {
            'success': True,
            'workflow': workflow,
            'message': f"Workflow '{workflow.get('title')}' retrieved successfully"
        }
    
    except requests.exceptions.RequestException as e:
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

"""
Scheduler Tools - Wrapper functions for AI Automation Scheduler
Provides tool functions that match the schema definitions in scheduler_tools.json
"""

import sys
from pathlib import Path
import json
from typing import Dict, List, Any, Optional

# Add AI_infrastructure to path for scheduler imports
ai_infra_path = Path(__file__).parent.parent.parent / 'AI_infrastructure'
if str(ai_infra_path) not in sys.path:
    sys.path.insert(0, str(ai_infra_path))

# Import scheduler instance
from scheduler import get_scheduler


def scheduler_create_task(
    task_name: str,
    trigger_type: str,
    action_type: str,
    description: Optional[str] = None,
    cron_expression: Optional[str] = None,
    datetime_trigger: Optional[str] = None,
    synergy_session_id: Optional[str] = None,
    thread_id: Optional[str] = None,
    agent_name: Optional[str] = None,
    location: Optional[str] = None,
    action_payload: Optional[Dict] = None,
    context_instructions: Optional[str] = None,
    requires_approval: bool = False,
    enabled: bool = True,
    tags: Optional[List[str]] = None,
    priority: int = 5,
    timeout_seconds: int = 300,
    max_retries: int = 3,
    retry_delay_seconds: int = 300,
    **kwargs
) -> Dict[str, Any]:
    """
    Create a scheduled automation task
    
    Args:
        task_name: Clear, descriptive task name
        trigger_type: 'cron', 'datetime', 'webhook', 'conditional', or 'manual'
        action_type: 'resume_session', 'send_message', 'execute_tool', or 'run_workflow'
        description: What this task does
        cron_expression: Cron schedule (if trigger_type='cron')
        datetime_trigger: ISO datetime (if trigger_type='datetime')
        synergy_session_id: Link to Synergy session
        thread_id: Conversation thread ID
        agent_name: Which AI agent executes
        location: Where task runs in UI
        action_payload: Action-specific configuration
        context_instructions: Additional AI instructions
        requires_approval: If true, user must approve
        enabled: If false, task is disabled
        tags: Tags for organization
        priority: Priority 1-10 (10 = highest)
        timeout_seconds: Max execution time
        max_retries: Retry attempts on failure
        retry_delay_seconds: Seconds between retries
        **kwargs: Additional parameters (includes _user_id for user tracking)
    
    Returns:
        Dict with success, task_id, task object, and message
    """
    # Get user_id from kwargs (injected by agent system)
    user_id = kwargs.get('_user_id', 1)
    
    # Build task data
    task_data = {
        'task_name': task_name,
        'description': description,
        'created_by': 'ai',  # AI is creating this task
        'created_by_user_id': user_id,
        'trigger_type': trigger_type,
        'cron_expression': cron_expression,
        'datetime_trigger': datetime_trigger,
        'action_type': action_type,
        'synergy_session_id': synergy_session_id,
        'thread_id': thread_id,
        'agent_name': agent_name,
        'location': location,
        'action_payload': json.dumps(action_payload) if action_payload else None,
        'context_instructions': context_instructions,
        'requires_approval': requires_approval,
        'enabled': enabled,
        'tags': json.dumps(tags) if tags else None,
        'priority': priority,
        'timeout_seconds': timeout_seconds,
        'max_retries': max_retries,
        'retry_delay_seconds': retry_delay_seconds
    }
    
    # Create task via scheduler
    scheduler = get_scheduler()
    task_id = scheduler.create_task(task_data)
    
    # Get created task
    task = scheduler.get_task(task_id)
    
    # Parse JSON fields for response
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
    
    return {
        'success': True,
        'task_id': task_id,
        'task': task,
        'message': f"Task '{task_name}' created successfully. Task ID: {task_id}",
        'next_execution_time': task.get('next_execution_time', 'Not scheduled yet')
    }


def scheduler_list_tasks(
    synergy_session_id: Optional[str] = None,
    thread_id: Optional[str] = None,
    agent_name: Optional[str] = None,
    enabled: Optional[bool] = None,
    created_by: Optional[str] = None,
    **kwargs
) -> Dict[str, Any]:
    """
    List scheduled tasks with optional filters
    
    Args:
        synergy_session_id: Filter by Synergy session
        thread_id: Filter by thread
        agent_name: Filter by agent
        enabled: Filter by enabled status
        created_by: Filter by creator ('user' or 'ai')
        **kwargs: Additional parameters
    
    Returns:
        Dict with success, tasks list, and count
    """
    # Build filters
    filters = {}
    if synergy_session_id:
        filters['synergy_session_id'] = synergy_session_id
    if thread_id:
        filters['thread_id'] = thread_id
    if agent_name:
        filters['agent_name'] = agent_name
    if enabled is not None:
        filters['enabled'] = enabled
    if created_by:
        filters['created_by'] = created_by
    
    # Get tasks from scheduler
    scheduler = get_scheduler()
    tasks = scheduler.list_tasks(filters)
    
    # Parse JSON fields
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
    
    return {
        'success': True,
        'tasks': tasks,
        'count': len(tasks)
    }


def scheduler_get_task(
    task_id: str,
    **kwargs
) -> Dict[str, Any]:
    """
    Get detailed information about a specific task
    
    Args:
        task_id: Task ID to retrieve
        **kwargs: Additional parameters
    
    Returns:
        Dict with success and task object
    """
    scheduler = get_scheduler()
    task = scheduler.get_task(task_id)
    
    if not task:
        return {
            'success': False,
            'error': f'Task not found: {task_id}'
        }
    
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
    
    return {
        'success': True,
        'task': task
    }


def scheduler_update_task(
    task_id: str,
    enabled: Optional[bool] = None,
    cron_expression: Optional[str] = None,
    datetime_trigger: Optional[str] = None,
    priority: Optional[int] = None,
    context_instructions: Optional[str] = None,
    action_payload: Optional[Dict] = None,
    **kwargs
) -> Dict[str, Any]:
    """
    Update an existing task
    
    Args:
        task_id: Task ID to update
        enabled: Enable or disable task
        cron_expression: New cron schedule
        datetime_trigger: New datetime trigger
        priority: New priority (1-10)
        context_instructions: Updated AI instructions
        action_payload: Updated action configuration
        **kwargs: Additional parameters
    
    Returns:
        Dict with success, updated task, and message
    """
    # Build updates
    updates = {}
    if enabled is not None:
        updates['enabled'] = enabled
    if cron_expression is not None:
        updates['cron_expression'] = cron_expression
    if datetime_trigger is not None:
        updates['datetime_trigger'] = datetime_trigger
    if priority is not None:
        updates['priority'] = priority
    if context_instructions is not None:
        updates['context_instructions'] = context_instructions
    if action_payload is not None:
        updates['action_payload'] = json.dumps(action_payload)
    
    # Update task
    scheduler = get_scheduler()
    success = scheduler.update_task(task_id, updates)
    
    if not success:
        return {
            'success': False,
            'error': f'Task not found or update failed: {task_id}'
        }
    
    # Get updated task
    task = scheduler.get_task(task_id)
    
    # Parse JSON fields
    if task.get('action_payload'):
        try:
            task['action_payload'] = json.loads(task['action_payload'])
        except:
            pass
    
    return {
        'success': True,
        'task': task,
        'message': f'Task {task_id} updated successfully'
    }


def scheduler_delete_task(
    task_id: str,
    **kwargs
) -> Dict[str, Any]:
    """
    Delete a scheduled task permanently
    
    Args:
        task_id: Task ID to delete
        **kwargs: Additional parameters
    
    Returns:
        Dict with success and message
    """
    scheduler = get_scheduler()
    success = scheduler.delete_task(task_id)
    
    if not success:
        return {
            'success': False,
            'error': f'Task not found: {task_id}'
        }
    
    return {
        'success': True,
        'message': f'Task {task_id} deleted successfully'
    }


def scheduler_execute_now(
    task_id: str,
    **kwargs
) -> Dict[str, Any]:
    """
    Manually trigger immediate execution of a task
    
    Args:
        task_id: Task ID to execute
        **kwargs: Additional parameters
    
    Returns:
        Dict with success and message
    """
    scheduler = get_scheduler()
    task = scheduler.get_task(task_id)
    
    if not task:
        return {
            'success': False,
            'error': f'Task not found: {task_id}'
        }
    
    # Execute task immediately
    scheduler._execute_task(task_id)
    
    return {
        'success': True,
        'message': f'Task {task_id} execution triggered',
        'task_id': task_id
    }


def scheduler_get_history(
    task_id: str,
    limit: int = 50,
    **kwargs
) -> Dict[str, Any]:
    """
    Get execution history for a task
    
    Args:
        task_id: Task ID to get history for
        limit: Max number of executions to return
        **kwargs: Additional parameters
    
    Returns:
        Dict with success, executions list, and count
    """
    # Convert limit to int if string
    if isinstance(limit, str):
        try:
            limit = int(limit)
        except:
            limit = 50
    
    scheduler = get_scheduler()
    history = scheduler.get_execution_history(task_id, limit)
    
    # Parse result_data JSON
    for execution in history:
        if execution.get('result_data'):
            try:
                execution['result_data'] = json.loads(execution['result_data'])
            except:
                pass
    
    return {
        'success': True,
        'task_id': task_id,
        'executions': history,
        'count': len(history)
    }


def scheduler_approve_task(
    task_id: str,
    approval_note: Optional[str] = None,
    **kwargs
) -> Dict[str, Any]:
    """
    Approve a task that requires approval
    
    Args:
        task_id: Task ID to approve
        approval_note: Optional approval note
        **kwargs: Additional parameters (includes _user_id)
    
    Returns:
        Dict with success and message
    """
    from datetime import datetime
    
    user_id = kwargs.get('_user_id', 1)
    
    updates = {
        'approval_status': 'approved',
        'approved_by_user_id': user_id,
        'approval_note': approval_note or '',
        'approved_at': datetime.now().isoformat()
    }
    
    scheduler = get_scheduler()
    success = scheduler.update_task(task_id, updates)
    
    if not success:
        return {
            'success': False,
            'error': f'Task not found: {task_id}'
        }
    
    return {
        'success': True,
        'message': 'Task approved and scheduled',
        'task_id': task_id
    }


def scheduler_reject_task(
    task_id: str,
    approval_note: Optional[str] = None,
    **kwargs
) -> Dict[str, Any]:
    """
    Reject a task that requires approval
    
    Args:
        task_id: Task ID to reject
        approval_note: Reason for rejection
        **kwargs: Additional parameters (includes _user_id)
    
    Returns:
        Dict with success and message
    """
    from datetime import datetime
    
    user_id = kwargs.get('_user_id', 1)
    
    updates = {
        'approval_status': 'rejected',
        'approved_by_user_id': user_id,
        'approval_note': approval_note or '',
        'approved_at': datetime.now().isoformat(),
        'enabled': False  # Disable rejected tasks
    }
    
    scheduler = get_scheduler()
    success = scheduler.update_task(task_id, updates)
    
    if not success:
        return {
            'success': False,
            'error': f'Task not found: {task_id}'
        }
    
    return {
        'success': True,
        'message': 'Task rejected',
        'task_id': task_id
    }

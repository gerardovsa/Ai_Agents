"""
Google Tasks API Integration
=============================

Complete implementation of Google Tasks with SMART bundled tools for AI agents.

Features:
- Task list management (create, get, list, delete)
- Task operations (create, update, complete, delete)
- SMART bundled tools for complex workflows
- Batch operations for efficiency
"""

import os
import sys
from pathlib import Path
from datetime import datetime, timedelta
from typing import List, Dict, Optional, Any

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

try:
    from googleapiclient.discovery import build
    from googleapiclient.errors import HttpError
except ImportError:
    print("⚠️ Google API libraries not installed. Install: pip install google-auth google-auth-oauthlib google-auth-httplib2 google-api-python-client")
    sys.exit(1)

# Google Tasks API scopes
SCOPES = ['https://www.googleapis.com/auth/tasks']

# ==================== SERVICE INITIALIZATION ====================

def build_tasks_service(_user_id=None, _injected_credentials=None, **kwargs):
    """
    Build and return Google Tasks API service using DATABASE OAuth ONLY.
    
    Args:
        _user_id: User ID for database OAuth credential lookup (REQUIRED)
        _injected_credentials: Flag to use database OAuth credentials (REQUIRED)
    
    Returns:
        Google Tasks service object
        
    Raises:
        Exception: If _user_id or _injected_credentials not provided
    """
    if _user_id and _injected_credentials:
        from AI_infrastructure.auth.credential_injector import get_user_tasks_service
        return get_user_tasks_service(user_id=_user_id, _user_id=_user_id)
    
    # No credentials provided - throw clear error
    raise Exception(
        "❌ Google Tasks requires database OAuth!\n\n"
        "File-based OAuth is no longer supported.\n"
        "All credentials must be in: data/ai_infrastructure.db (oauth_tokens table)\n\n"
        "To authenticate:\n"
        "1. Visit: http://localhost:5001/auth/google/login\n"
        "2. Sign in and grant permissions\n"
        "3. Credentials will be saved to database\n\n"
        f"Received: _user_id={_user_id}, _injected_credentials={_injected_credentials}\n"
    )




# ==================== TASK LIST OPERATIONS ====================

def google_tasks_list_task_lists(_user_id=None, _injected_credentials=None, **kwargs):
    """
    List all task lists.
    
    Args:
        _user_id: User ID for database OAuth credential lookup
        _injected_credentials: Flag to use database OAuth credentials
    
    Returns:
        dict: {
            'task_lists': [
                {
                    'id': 'list_id',
                    'title': 'My Tasks',
                    'updated': '2025-10-28T10:00:00.000Z'
                }
            ],
            'total': 3
        }
    """
    try:
        service = build_tasks_service(_user_id=_user_id, _injected_credentials=_injected_credentials)
        results = service.tasklists().list().execute()
        task_lists = results.get('items', [])
        
        return {
            'task_lists': task_lists,
            'total': len(task_lists)
        }
    except Exception as e:
        return {'error': str(e), 'success': False}


def google_tasks_create_task_list(title, _user_id=None, _injected_credentials=None, **kwargs):
    """
    Create a new task list.
    
    Args:
        title (str): Task list title
    
    Returns:
        dict: Created task list with id, title, updated
    """
    try:
        service = build_tasks_service(_user_id=_user_id, _injected_credentials=_injected_credentials)
        task_list = {
            'title': title
        }
        
        result = service.tasklists().insert(body=task_list).execute()
        
        return {
            'task_list_id': result['id'],
            'title': result['title'],
            'updated': result.get('updated'),
            'success': True
        }
    except Exception as e:
        return {'error': str(e), 'success': False}


def google_tasks_get_task_list(task_list_id, _user_id=None, _injected_credentials=None, **kwargs):
    """
    Get a specific task list.
    
    Args:
        task_list_id (str): Task list ID
    
    Returns:
        dict: Task list details
    """
    try:
        service = build_tasks_service(_user_id=_user_id, _injected_credentials=_injected_credentials)
        result = service.tasklists().get(tasklist=task_list_id).execute()
        
        return {
            'task_list_id': result['id'],
            'title': result['title'],
            'updated': result.get('updated'),
            'success': True
        }
    except Exception as e:
        return {'error': str(e), 'success': False}


def google_tasks_delete_task_list(task_list_id, _user_id=None, _injected_credentials=None, **kwargs):
    """
    Delete a task list.
    
    Args:
        task_list_id (str): Task list ID to delete
    
    Returns:
        dict: Success status
    """
    try:
        service = build_tasks_service(_user_id=_user_id, _injected_credentials=_injected_credentials)
        service.tasklists().delete(tasklist=task_list_id).execute()
        
        return {
            'success': True,
            'message': f'Task list {task_list_id} deleted'
        }
    except Exception as e:
        return {'error': str(e), 'success': False}


# ==================== TASK OPERATIONS ====================

def google_tasks_list_tasks(task_list_id='@default', show_completed=False, show_hidden=False, _user_id=None, _injected_credentials=None, **kwargs):
    """
    List tasks in a task list.
    
    Args:
        task_list_id (str): Task list ID (default: '@default')
        show_completed (bool): Show completed tasks
        show_hidden (bool): Show hidden tasks
    
    Returns:
        dict: {
            'tasks': [...],
            'total': 5,
            'task_list_id': 'list_id'
        }
    """
    try:
        service = build_tasks_service(_user_id=_user_id, _injected_credentials=_injected_credentials)
        results = service.tasks().list(
            tasklist=task_list_id,
            showCompleted=show_completed,
            showHidden=show_hidden
        ).execute()
        
        tasks = results.get('items', [])
        
        return {
            'tasks': tasks,
            'total': len(tasks),
            'task_list_id': task_list_id,
            'success': True
        }
    except Exception as e:
        return {'error': str(e), 'success': False}


def google_tasks_create_task(title, task_list_id='@default', notes=None, due=None, parent=None, _user_id=None, _injected_credentials=None, **kwargs):
    """
    Create a new task.
    
    Args:
        title (str): Task title
        task_list_id (str): Task list ID (default: '@default')
        notes (str): Task notes/description
        due (str): Due date in RFC 3339 format (e.g., '2025-10-30T17:00:00.000Z')
        parent (str): Parent task ID for subtasks
    
    Returns:
        dict: Created task with id, title, status, etc.
    """
    try:
        service = build_tasks_service(_user_id=_user_id, _injected_credentials=_injected_credentials)
        
        task = {
            'title': title
        }
        
        if notes:
            task['notes'] = notes
        
        if due:
            task['due'] = due
        
        result = service.tasks().insert(
            tasklist=task_list_id,
            body=task,
            parent=parent
        ).execute()
        
        return {
            'task_id': result['id'],
            'title': result['title'],
            'status': result.get('status'),
            'due': result.get('due'),
            'notes': result.get('notes'),
            'task_list_id': task_list_id,
            'success': True
        }
    except Exception as e:
        return {'error': str(e), 'success': False}


def google_tasks_update_task(task_id, task_list_id='@default', title=None, notes=None, 
                             status=None, due=None, **kwargs):
    """
    Update an existing task.
    
    Args:
        task_id (str): Task ID
        task_list_id (str): Task list ID
        title (str): New title
        notes (str): New notes
        status (str): New status ('needsAction' or 'completed')
        due (str): New due date in RFC 3339 format
    
    Returns:
        dict: Updated task
    """
    try:
        service = build_tasks_service(_user_id=_user_id, _injected_credentials=_injected_credentials)
        
        # Get current task
        task = service.tasks().get(tasklist=task_list_id, task=task_id).execute()
        
        # Update fields
        if title is not None:
            task['title'] = title
        if notes is not None:
            task['notes'] = notes
        if status is not None:
            task['status'] = status
        if due is not None:
            task['due'] = due
        
        result = service.tasks().update(
            tasklist=task_list_id,
            task=task_id,
            body=task
        ).execute()
        
        return {
            'task_id': result['id'],
            'title': result['title'],
            'status': result.get('status'),
            'due': result.get('due'),
            'notes': result.get('notes'),
            'updated': result.get('updated'),
            'success': True
        }
    except Exception as e:
        return {'error': str(e), 'success': False}


def google_tasks_complete_task(task_id, task_list_id='@default', _user_id=None, _injected_credentials=None, **kwargs):
    """
    Mark a task as completed.
    
    Args:
        task_id (str): Task ID
        task_list_id (str): Task list ID
    
    Returns:
        dict: Updated task with completed status
    """
    try:
        service = build_tasks_service(_user_id=_user_id, _injected_credentials=_injected_credentials)
        
        task = service.tasks().get(tasklist=task_list_id, task=task_id).execute()
        task['status'] = 'completed'
        
        result = service.tasks().update(
            tasklist=task_list_id,
            task=task_id,
            body=task
        ).execute()
        
        return {
            'task_id': result['id'],
            'title': result['title'],
            'status': result.get('status'),
            'completed': result.get('completed'),
            'success': True
        }
    except Exception as e:
        return {'error': str(e), 'success': False}


def google_tasks_delete_task(task_id, task_list_id='@default', _user_id=None, _injected_credentials=None, **kwargs):
    """
    Delete a task.
    
    Args:
        task_id (str): Task ID
        task_list_id (str): Task list ID
    
    Returns:
        dict: Success status
    """
    try:
        service = build_tasks_service(_user_id=_user_id, _injected_credentials=_injected_credentials)
        service.tasks().delete(tasklist=task_list_id, task=task_id).execute()
        
        return {
            'success': True,
            'message': f'Task {task_id} deleted from list {task_list_id}'
        }
    except Exception as e:
        return {'error': str(e), 'success': False}


# ==================== SMART BUNDLED TOOLS ====================

def google_tasks_smart_create_project(project_name, tasks_list, task_list_id='@default', 
                                     due_date=None, **kwargs):
    """
    🤖 SMART TOOL: Create a complete project with multiple tasks in ONE call.
    
    Creates a parent task for the project and multiple subtasks underneath.
    
    Args:
        project_name (str): Name of the project (becomes parent task)
        tasks_list (list): List of task dictionaries with 'title', 'notes', 'due'
        task_list_id (str): Task list ID (default: '@default')
        due_date (str): Project due date in RFC 3339 format
    
    Returns:
        dict: {
            'project_task_id': 'parent_id',
            'project_name': 'Launch Website',
            'subtasks_created': 5,
            'subtasks': [...],
            'task_list_id': 'list_id'
        }
    
    Example:
        google_tasks_smart_create_project(
            project_name="Launch Marketing Campaign",
            tasks_list=[
                {"title": "Design landing page", "notes": "Use brand colors", "due": "2025-10-30T17:00:00.000Z"},
                {"title": "Write copy", "notes": "Focus on benefits"},
                {"title": "Set up analytics"}
            ]
        )
    """
    try:
        print(f"🤖 Creating project: {project_name} with {len(tasks_list)} tasks...")
        
        # Create parent task (project)
        parent_result = google_tasks_create_task(
            title=project_name,
            task_list_id=task_list_id,
            notes=f"Project with {len(tasks_list)} subtasks",
            due=due_date
        )
        
        if not parent_result.get('success'):
            return parent_result
        
        parent_id = parent_result['task_id']
        subtasks = []
        
        # Create subtasks
        for task_data in tasks_list:
            subtask_result = google_tasks_create_task(
                title=task_data.get('title', 'Untitled Task'),
                task_list_id=task_list_id,
                notes=task_data.get('notes'),
                due=task_data.get('due'),
                parent=parent_id
            )
            
            if subtask_result.get('success'):
                subtasks.append(subtask_result)
        
        print(f" Project created with {len(subtasks)} subtasks")
        
        return {
            'project_task_id': parent_id,
            'project_name': project_name,
            'subtasks_created': len(subtasks),
            'subtasks': subtasks,
            'task_list_id': task_list_id,
            'success': True
        }
    except Exception as e:
        return {'error': str(e), 'success': False}


def google_tasks_smart_bulk_complete(task_ids, task_list_id='@default', _user_id=None, _injected_credentials=None, **kwargs):
    """
    🤖 SMART TOOL: Complete multiple tasks in ONE call.
    
    Efficiently marks multiple tasks as completed in batch.
    
    Args:
        task_ids (list): List of task IDs to complete
        task_list_id (str): Task list ID
    
    Returns:
        dict: {
            'total_tasks': 10,
            'completed': 10,
            'failed': 0,
            'completed_tasks': [...],
            'failed_tasks': [...]
        }
    
    Example:
        google_tasks_smart_bulk_complete(
            task_ids=['task1', 'task2', 'task3']
        )
    """
    try:
        print(f"🤖 Completing {len(task_ids)} tasks in bulk...")
        
        completed_tasks = []
        failed_tasks = []
        
        for task_id in task_ids:
            result = google_tasks_complete_task(task_id, task_list_id)
            
            if result.get('success'):
                completed_tasks.append(result)
            else:
                failed_tasks.append({
                    'task_id': task_id,
                    'error': result.get('error')
                })
        
        print(f" Completed {len(completed_tasks)}/{len(task_ids)} tasks")
        
        return {
            'total_tasks': len(task_ids),
            'completed': len(completed_tasks),
            'failed': len(failed_tasks),
            'completed_tasks': completed_tasks,
            'failed_tasks': failed_tasks,
            'task_list_id': task_list_id,
            'success': True
        }
    except Exception as e:
        return {'error': str(e), 'success': False}


def google_tasks_smart_organize_by_priority(task_list_id='@default', _user_id=None, _injected_credentials=None, **kwargs):
    """
    🤖 SMART TOOL: Organize tasks by detecting priority keywords and updating them.
    
    Analyzes task titles/notes for priority keywords (urgent, important, ASAP, etc.)
    and reorganizes them by adding priority prefixes.
    
    Args:
        task_list_id (str): Task list ID to organize
    
    Returns:
        dict: {
            'tasks_analyzed': 20,
            'high_priority': 5,
            'medium_priority': 10,
            'low_priority': 5,
            'reorganized_tasks': [...]
        }
    
    Example:
        google_tasks_smart_organize_by_priority(task_list_id='@default')
    """
    try:
        print(f"🤖 Analyzing and organizing tasks by priority...")
        
        # Get all tasks
        tasks_result = google_tasks_list_tasks(task_list_id, show_completed=False)
        
        if not tasks_result.get('success'):
            return tasks_result
        
        tasks = tasks_result.get('tasks', [])
        
        high_priority_keywords = ['urgent', 'asap', 'critical', 'important', 'emergency', '!!!']
        medium_priority_keywords = ['soon', 'needed', 'required', 'deadline']
        
        high_priority = []
        medium_priority = []
        low_priority = []
        
        for task in tasks:
            title = task.get('title', '').lower()
            notes = task.get('notes', '').lower()
            combined_text = f"{title} {notes}"
            
            # Determine priority
            if any(keyword in combined_text for keyword in high_priority_keywords):
                priority = 'HIGH'
                high_priority.append(task)
            elif any(keyword in combined_text for keyword in medium_priority_keywords):
                priority = 'MEDIUM'
                medium_priority.append(task)
            else:
                priority = 'LOW'
                low_priority.append(task)
            
            # Update task title with priority prefix if not already there
            current_title = task.get('title', '')
            if not current_title.startswith('['):
                new_title = f"[{priority}] {current_title}"
                google_tasks_update_task(
                    task_id=task['id'],
                    task_list_id=task_list_id,
                    title=new_title
                )
        
        print(f" Organized {len(tasks)} tasks: {len(high_priority)} high, {len(medium_priority)} medium, {len(low_priority)} low")
        
        return {
            'tasks_analyzed': len(tasks),
            'high_priority': len(high_priority),
            'medium_priority': len(medium_priority),
            'low_priority': len(low_priority),
            'high_priority_tasks': high_priority,
            'medium_priority_tasks': medium_priority,
            'low_priority_tasks': low_priority,
            'success': True
        }
    except Exception as e:
        return {'error': str(e), 'success': False}


# ==================== EXPORTS ====================

__all__ = [
    # Service
    'build_tasks_service',
    
    # Task Lists
    'google_tasks_list_task_lists',
    'google_tasks_create_task_list',
    'google_tasks_get_task_list',
    'google_tasks_delete_task_list',
    
    # Tasks
    'google_tasks_list_tasks',
    'google_tasks_create_task',
    'google_tasks_update_task',
    'google_tasks_complete_task',
    'google_tasks_delete_task',
    
    # SMART Bundled Tools
    'google_tasks_smart_create_project',
    'google_tasks_smart_bulk_complete',
    'google_tasks_smart_organize_by_priority',
]

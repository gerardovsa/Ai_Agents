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
    from google.oauth2.credentials import Credentials
    from google.auth.transport.requests import Request
    from google_auth_oauthlib.flow import InstalledAppFlow
    from googleapiclient.discovery import build
    from googleapiclient.errors import HttpError
except ImportError:
    print("⚠️ Google API libraries not installed. Install: pip install google-auth google-auth-oauthlib google-auth-httplib2 google-api-python-client")
    sys.exit(1)

# Google Tasks API scopes
SCOPES = ['https://www.googleapis.com/auth/tasks']

# ==================== SERVICE INITIALIZATION ====================

def build_tasks_service():
    """
    Build and return Google Tasks API service.
    Supports both desktop (local) and web (deployed) OAuth flows.
    
    Environment variables:
    - GOOGLE_TASKS_OAUTH_MODE: 'desktop' (local testing) or 'web' (Render deployment)
    - GOOGLE_TASKS_CREDENTIALS_FILE_DESKTOP: Desktop app credentials
    - GOOGLE_TASKS_TOKEN_FILE_DESKTOP: Desktop token storage
    - GOOGLE_TASKS_CREDENTIALS_FILE_WEB: Web app credentials
    - GOOGLE_TASKS_TOKEN_FILE_WEB: Web token storage
    
    Returns:
        Google Tasks service object
    """
    # Get OAuth mode from environment
    oauth_mode = os.getenv('GOOGLE_TASKS_OAUTH_MODE', 'desktop').lower()
    
    print(f"🔑 Google Tasks OAuth Mode: {oauth_mode}")
    
    if oauth_mode == 'desktop':
        return _build_tasks_service_desktop()
    elif oauth_mode == 'web':
        return _build_tasks_service_web()
    else:
        # Fallback to legacy single-file mode
        print(f"⚠️  Unknown OAuth mode '{oauth_mode}', using legacy single-file mode")
        return _build_tasks_service_legacy()


def _build_tasks_service_desktop():
    """
    Desktop app OAuth flow (opens local browser).
    Used for local development and testing.
    """
    creds = None
    
    # Get paths from environment or use defaults
    token_path = Path(os.getenv('GOOGLE_TASKS_TOKEN_FILE_DESKTOP', 
                                str(Path(__file__).parent.parent / 'token_desktop.json')))
    credentials_path = Path(os.getenv('GOOGLE_TASKS_CREDENTIALS_FILE_DESKTOP',
                                     str(Path(__file__).parent.parent / 'credentials_desktop.json')))
    
    # Get scopes from environment
    scopes_env = os.getenv('GOOGLE_TASKS_SCOPES', 'https://www.googleapis.com/auth/tasks')
    scopes = [s.strip() for s in scopes_env.split(',')]
    
    print(f"   Credentials: {credentials_path}")
    print(f"   Token: {token_path}")
    print(f"   Scopes: {scopes}")
    
    # Load existing token
    if token_path.exists():
        creds = Credentials.from_authorized_user_file(str(token_path), scopes)
        print(f"   ✅ Loaded existing token")
    
    # Refresh or get new credentials
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            print(f"   🔄 Refreshing expired token...")
            creds.refresh(Request())
            print(f"   ✅ Token refreshed")
        else:
            if not credentials_path.exists():
                raise FileNotFoundError(
                    f"❌ Desktop credentials not found: {credentials_path}\n\n"
                    f"📋 Setup Instructions:\n"
                    f"1. Go to: https://console.cloud.google.com/apis/credentials\n"
                    f"2. Select project: vsa-anythingllm-project\n"
                    f"3. Click 'Create Credentials' → 'OAuth 2.0 Client ID'\n"
                    f"4. Application type: 'Desktop app'\n"
                    f"5. Download JSON and save as: {credentials_path}\n"
                )
            print(f"   🔐 Starting OAuth flow (browser will open)...")
            flow = InstalledAppFlow.from_client_secrets_file(str(credentials_path), scopes)
            creds = flow.run_local_server(port=0)
            print(f"   ✅ Authentication successful!")
        
        # Save credentials
        with open(token_path, 'w') as token:
            token.write(creds.to_json())
        print(f"   💾 Token saved to: {token_path}")
    
    # Build and return service
    service = build('tasks', 'v1', credentials=creds)
    print(f"   ✅ Google Tasks service ready (desktop mode)")
    return service


def _build_tasks_service_web():
    """
    Web app OAuth flow (for deployed Render app).
    Requires stored credentials from OAuth callback.
    """
    creds = None
    
    # Get paths from environment
    token_path = Path(os.getenv('GOOGLE_TASKS_TOKEN_FILE_WEB',
                                str(Path(__file__).parent.parent / 'token_web.json')))
    credentials_path = Path(os.getenv('GOOGLE_TASKS_CREDENTIALS_FILE_WEB',
                                     str(Path(__file__).parent.parent / 'credentials_web.json')))
    
    # Get scopes
    scopes_env = os.getenv('GOOGLE_TASKS_SCOPES', 'https://www.googleapis.com/auth/tasks')
    scopes = [s.strip() for s in scopes_env.split(',')]
    
    print(f"   Credentials: {credentials_path}")
    print(f"   Token: {token_path}")
    print(f"   Scopes: {scopes}")
    
    # Load existing token
    if token_path.exists():
        creds = Credentials.from_authorized_user_file(str(token_path), scopes)
        print(f"   ✅ Loaded existing token")
    else:
        print(f"   ❌ No token found. User needs to authenticate via web OAuth.")
        print(f"   👉 Visit: http://localhost:4000/oauth/tasks/start")
        print(f"   👉 Or on Render: https://your-app.onrender.com/oauth/tasks/start")
        raise FileNotFoundError(
            "Google Tasks authentication required. "
            "User must authenticate via /oauth/tasks/start endpoint."
        )
    
    # Refresh if expired
    if creds and creds.expired and creds.refresh_token:
        print(f"   🔄 Refreshing expired token...")
        creds.refresh(Request())
        with open(token_path, 'w') as token:
            token.write(creds.to_json())
        print(f"   ✅ Token refreshed")
    
    # Build and return service
    service = build('tasks', 'v1', credentials=creds)
    print(f"   ✅ Google Tasks service ready (web mode)")
    return service


def _build_tasks_service_legacy():
    """
    Legacy single-file OAuth flow (backward compatibility).
    Uses GOOGLE_TASKS_CREDENTIALS_FILE and GOOGLE_TASKS_TOKEN_FILE.
    """
    creds = None
    
    # Get paths from environment or use defaults
    token_path = Path(os.getenv('GOOGLE_TASKS_TOKEN_FILE', 
                                str(Path(__file__).parent.parent / 'token.json')))
    credentials_path = Path(os.getenv('GOOGLE_TASKS_CREDENTIALS_FILE',
                                     str(Path(__file__).parent.parent / 'credentials.json')))
    
    # Get scopes from environment
    scopes_env = os.getenv('GOOGLE_TASKS_SCOPES', 'https://www.googleapis.com/auth/tasks')
    scopes = [s.strip() for s in scopes_env.split(',')]
    
    print(f"   Token file: {token_path}")
    print(f"   Credentials file: {credentials_path}")
    print(f"   Scopes: {scopes}")
    
    # Load existing token
    if token_path.exists():
        creds = Credentials.from_authorized_user_file(str(token_path), scopes)
        print(f"   ✅ Loaded existing token from: {token_path}")
    
    # Refresh or get new credentials
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            print(f"   🔄 Refreshing expired token...")
            creds.refresh(Request())
            print(f"   ✅ Token refreshed successfully")
        else:
            if not credentials_path.exists():
                raise FileNotFoundError(
                    f"❌ credentials.json not found at {credentials_path}\n\n"
                    f"📋 Setup Instructions:\n"
                    f"1. Go to: https://console.cloud.google.com/apis/credentials\n"
                    f"2. Select project: vsa-anythingllm-project\n"
                    f"3. Click 'Create Credentials' → 'OAuth 2.0 Client ID'\n"
                    f"4. Application type: 'Desktop app'\n"
                    f"5. Name it: 'AI Agents - Google Tasks'\n"
                    f"6. Download JSON file and save as: {credentials_path}\n"
                    f"7. Set in .env: GOOGLE_TASKS_CREDENTIALS_FILE={credentials_path}\n"
                )
            print(f"   🔐 Starting OAuth authentication flow...")
            flow = InstalledAppFlow.from_client_secrets_file(str(credentials_path), scopes)
            creds = flow.run_local_server(port=0)
            print(f"   ✅ Authentication successful!")
        
        # Save credentials
        with open(token_path, 'w') as token:
            token.write(creds.to_json())
        print(f"   💾 Token saved to: {token_path}")
    
    # Build and return service
    service = build('tasks', 'v1', credentials=creds)
    print(f"   ✅ Google Tasks service ready (legacy mode)")
    return service


# ==================== TASK LIST OPERATIONS ====================

def google_tasks_list_task_lists():
    """
    List all task lists.
    
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
        service = build_tasks_service()
        results = service.tasklists().list().execute()
        task_lists = results.get('items', [])
        
        return {
            'task_lists': task_lists,
            'total': len(task_lists)
        }
    except Exception as e:
        return {'error': str(e), 'success': False}


def google_tasks_create_task_list(title):
    """
    Create a new task list.
    
    Args:
        title (str): Task list title
    
    Returns:
        dict: Created task list with id, title, updated
    """
    try:
        service = build_tasks_service()
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


def google_tasks_get_task_list(task_list_id):
    """
    Get a specific task list.
    
    Args:
        task_list_id (str): Task list ID
    
    Returns:
        dict: Task list details
    """
    try:
        service = build_tasks_service()
        result = service.tasklists().get(tasklist=task_list_id).execute()
        
        return {
            'task_list_id': result['id'],
            'title': result['title'],
            'updated': result.get('updated'),
            'success': True
        }
    except Exception as e:
        return {'error': str(e), 'success': False}


def google_tasks_delete_task_list(task_list_id):
    """
    Delete a task list.
    
    Args:
        task_list_id (str): Task list ID to delete
    
    Returns:
        dict: Success status
    """
    try:
        service = build_tasks_service()
        service.tasklists().delete(tasklist=task_list_id).execute()
        
        return {
            'success': True,
            'message': f'Task list {task_list_id} deleted'
        }
    except Exception as e:
        return {'error': str(e), 'success': False}


# ==================== TASK OPERATIONS ====================

def google_tasks_list_tasks(task_list_id='@default', show_completed=False, show_hidden=False):
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
        service = build_tasks_service()
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


def google_tasks_create_task(title, task_list_id='@default', notes=None, due=None, parent=None):
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
        service = build_tasks_service()
        
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
                             status=None, due=None):
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
        service = build_tasks_service()
        
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


def google_tasks_complete_task(task_id, task_list_id='@default'):
    """
    Mark a task as completed.
    
    Args:
        task_id (str): Task ID
        task_list_id (str): Task list ID
    
    Returns:
        dict: Updated task with completed status
    """
    try:
        service = build_tasks_service()
        
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


def google_tasks_delete_task(task_id, task_list_id='@default'):
    """
    Delete a task.
    
    Args:
        task_id (str): Task ID
        task_list_id (str): Task list ID
    
    Returns:
        dict: Success status
    """
    try:
        service = build_tasks_service()
        service.tasks().delete(tasklist=task_list_id, task=task_id).execute()
        
        return {
            'success': True,
            'message': f'Task {task_id} deleted from list {task_list_id}'
        }
    except Exception as e:
        return {'error': str(e), 'success': False}


# ==================== SMART BUNDLED TOOLS ====================

def google_tasks_smart_create_project(project_name, tasks_list, task_list_id='@default', 
                                     due_date=None):
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
        
        print(f"✅ Project created with {len(subtasks)} subtasks")
        
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


def google_tasks_smart_bulk_complete(task_ids, task_list_id='@default'):
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
        
        print(f"✅ Completed {len(completed_tasks)}/{len(task_ids)} tasks")
        
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


def google_tasks_smart_organize_by_priority(task_list_id='@default'):
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
        
        print(f"✅ Organized {len(tasks)} tasks: {len(high_priority)} high, {len(medium_priority)} medium, {len(low_priority)} low")
        
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

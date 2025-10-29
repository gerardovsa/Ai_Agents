"""
AI Personal Task Management System
===================================

Enables the AI agent to create and manage its own tasks in Google Tasks.
This provides persistent memory and task tracking across conversations.

The AI has its own dedicated task list called "AI Agent Tasks" where it can:
- Create tasks for things it needs to remember
- Track multi-step work across conversations
- Update progress as work is completed
- Organize by priority
- Set reminders for follow-ups
"""

import os
import sys
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from google_workspace.google_tasks import (
    google_tasks_list_task_lists,
    google_tasks_create_task_list,
    google_tasks_list_tasks,
    google_tasks_create_task,
    google_tasks_update_task,
    google_tasks_complete_task,
    google_tasks_delete_task,
    google_tasks_smart_organize_by_priority
)

# Configuration
AI_TASKLIST_NAME = "🤖 AI Agent Tasks"
AI_TASKLIST_ID = None  # Will be set on first use


def _get_or_create_ai_tasklist():
    """
    Get or create the AI's dedicated task list.
    
    Returns:
        str: Task list ID for AI Agent Tasks
    """
    global AI_TASKLIST_ID
    
    if AI_TASKLIST_ID:
        return AI_TASKLIST_ID
    
    # Check if AI task list already exists
    result = google_tasks_list_task_lists()
    
    if result.get('success'):
        for tasklist in result.get('task_lists', []):
            if tasklist['title'] == AI_TASKLIST_NAME:
                AI_TASKLIST_ID = tasklist['id']
                print(f"✅ Found existing AI task list: {AI_TASKLIST_ID}")
                return AI_TASKLIST_ID
    
    # Create new AI task list
    print(f"📝 Creating new AI task list: {AI_TASKLIST_NAME}")
    result = google_tasks_create_task_list(title=AI_TASKLIST_NAME)
    
    if result.get('success'):
        AI_TASKLIST_ID = result['task_list']['id']
        print(f"✅ Created AI task list: {AI_TASKLIST_ID}")
        return AI_TASKLIST_ID
    
    raise Exception(f"Failed to create AI task list: {result.get('error')}")


def ai_create_task(title: str, notes: str = None, due_date: str = None, 
                   priority: str = "medium") -> Dict[str, Any]:
    """
    🤖 AI creates a task for itself.
    
    Use this when the AI needs to:
    - Remember something for later
    - Track multi-step work
    - Set a reminder for follow-up
    - Keep context across conversations
    
    Args:
        title: Task title (what needs to be done)
        notes: Detailed notes/context (optional)
        due_date: Due date in ISO format YYYY-MM-DD (optional)
        priority: Priority level - "high", "medium", "low" (default: "medium")
    
    Returns:
        dict: Task creation result with task ID
    
    Example:
        # AI remembers to follow up
        ai_create_task(
            title="Follow up with user about Gmail integration",
            notes="User requested bulk email feature. Need to check if they tested it.",
            due_date="2025-10-30",
            priority="high"
        )
    """
    try:
        tasklist_id = _get_or_create_ai_tasklist()
        
        # Add priority emoji to title
        priority_emoji = {
            "high": "🔴",
            "medium": "🟡", 
            "low": "🟢"
        }
        emoji = priority_emoji.get(priority.lower(), "🟡")
        enhanced_title = f"{emoji} {title}"
        
        # Add priority to notes
        enhanced_notes = f"Priority: {priority.upper()}\n\n"
        if notes:
            enhanced_notes += notes
        enhanced_notes += f"\n\n---\nCreated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
        
        result = google_tasks_create_task(
            tasklist_id=tasklist_id,
            title=enhanced_title,
            notes=enhanced_notes,
            due=due_date
        )
        
        if result.get('success'):
            print(f"✅ AI created task: {enhanced_title}")
            return {
                'success': True,
                'task_id': result['task']['id'],
                'title': enhanced_title,
                'message': f"AI task created: {title}"
            }
        
        return {
            'success': False,
            'error': result.get('error', 'Unknown error')
        }
        
    except Exception as e:
        return {
            'success': False,
            'error': str(e)
        }


def ai_list_my_tasks(show_completed: bool = False, limit: int = 20) -> Dict[str, Any]:
    """
    🤖 AI lists its own tasks.
    
    Use this when the AI needs to:
    - Check what it's working on
    - Review pending tasks
    - Resume work from previous conversation
    - See completed tasks
    
    Args:
        show_completed: Include completed tasks (default: False)
        limit: Maximum number of tasks to return (default: 20)
    
    Returns:
        dict: List of AI's tasks with details
    
    Example:
        # AI checks what it needs to do
        tasks = ai_list_my_tasks()
        print(f"I have {len(tasks['tasks'])} pending tasks")
    """
    try:
        tasklist_id = _get_or_create_ai_tasklist()
        
        result = google_tasks_list_tasks(
            tasklist_id=tasklist_id,
            show_completed=show_completed,
            max_results=limit
        )
        
        if result.get('success'):
            tasks = result.get('tasks', [])
            print(f"✅ AI has {len(tasks)} tasks")
            
            return {
                'success': True,
                'tasks': tasks,
                'count': len(tasks),
                'message': f"AI has {len(tasks)} tasks"
            }
        
        return {
            'success': False,
            'error': result.get('error', 'Unknown error')
        }
        
    except Exception as e:
        return {
            'success': False,
            'error': str(e)
        }


def ai_update_task(task_id: str, title: str = None, notes: str = None, 
                   due_date: str = None, status: str = None) -> Dict[str, Any]:
    """
    🤖 AI updates one of its tasks.
    
    Use this when the AI needs to:
    - Update progress notes
    - Change due date
    - Modify task details
    - Add new information
    
    Args:
        task_id: ID of the task to update
        title: New title (optional)
        notes: Updated notes (optional)
        due_date: New due date YYYY-MM-DD (optional)
        status: "needsAction" or "completed" (optional)
    
    Returns:
        dict: Update result
    
    Example:
        # AI updates progress
        ai_update_task(
            task_id="task123",
            notes="Updated: User confirmed Gmail integration works. Moving to next phase."
        )
    """
    try:
        tasklist_id = _get_or_create_ai_tasklist()
        
        # Add update timestamp to notes
        if notes:
            notes += f"\n\n---\nUpdated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
        
        result = google_tasks_update_task(
            tasklist_id=tasklist_id,
            task_id=task_id,
            title=title,
            notes=notes,
            due=due_date,
            status=status
        )
        
        if result.get('success'):
            print(f"✅ AI updated task: {task_id}")
            return {
                'success': True,
                'task_id': task_id,
                'message': "AI task updated"
            }
        
        return {
            'success': False,
            'error': result.get('error', 'Unknown error')
        }
        
    except Exception as e:
        return {
            'success': False,
            'error': str(e)
        }


def ai_complete_task(task_id: str, completion_notes: str = None) -> Dict[str, Any]:
    """
    🤖 AI marks one of its tasks as complete.
    
    Use this when the AI:
    - Finishes a task
    - Completes a multi-step project
    - Resolves a tracked issue
    
    Args:
        task_id: ID of the task to complete
        completion_notes: Notes about completion (optional)
    
    Returns:
        dict: Completion result
    
    Example:
        # AI completes a task
        ai_complete_task(
            task_id="task123",
            completion_notes="Gmail integration tested and working. User confirmed success."
        )
    """
    try:
        tasklist_id = _get_or_create_ai_tasklist()
        
        # Add completion notes if provided
        if completion_notes:
            result = ai_update_task(
                task_id=task_id,
                notes=f"COMPLETED: {completion_notes}\n\nCompleted: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
            )
        
        result = google_tasks_complete_task(
            tasklist_id=tasklist_id,
            task_id=task_id
        )
        
        if result.get('success'):
            print(f"✅ AI completed task: {task_id}")
            return {
                'success': True,
                'task_id': task_id,
                'message': "AI task completed"
            }
        
        return {
            'success': False,
            'error': result.get('error', 'Unknown error')
        }
        
    except Exception as e:
        return {
            'success': False,
            'error': str(e)
        }


def ai_organize_tasks() -> Dict[str, Any]:
    """
    🤖 AI organizes its tasks by priority.
    
    Use this when the AI needs to:
    - Prioritize work
    - Reorder tasks
    - Focus on high-priority items
    
    Returns:
        dict: Organization result with reordered tasks
    
    Example:
        # AI organizes its workload
        result = ai_organize_tasks()
        print(f"Organized {result['tasks_organized']} tasks by priority")
    """
    try:
        tasklist_id = _get_or_create_ai_tasklist()
        
        result = google_tasks_smart_organize_by_priority(
            tasklist_id=tasklist_id
        )
        
        if result.get('success'):
            count = result.get('tasks_organized', 0)
            print(f"✅ AI organized {count} tasks by priority")
            return {
                'success': True,
                'tasks_organized': count,
                'message': f"AI organized {count} tasks"
            }
        
        return {
            'success': False,
            'error': result.get('error', 'Unknown error')
        }
        
    except Exception as e:
        return {
            'success': False,
            'error': str(e)
        }


def ai_create_project_tasks(project_name: str, task_list: List[str], 
                            due_date: str = None, priority: str = "high") -> Dict[str, Any]:
    """
    🤖 AI creates multiple related tasks for a project.
    
    Use this when the AI needs to:
    - Break down complex work
    - Track multi-step projects
    - Remember sequential tasks
    
    Args:
        project_name: Name of the project
        task_list: List of task titles to create
        due_date: Due date for all tasks YYYY-MM-DD (optional)
        priority: Priority for all tasks (default: "high")
    
    Returns:
        dict: Results with created task IDs
    
    Example:
        # AI creates project plan
        ai_create_project_tasks(
            project_name="User Dashboard Redesign",
            task_list=[
                "Review current dashboard design",
                "Gather user feedback",
                "Create mockups",
                "Implement changes",
                "Test with users"
            ],
            due_date="2025-11-15",
            priority="high"
        )
    """
    try:
        created_tasks = []
        
        # Create parent project task
        parent_result = ai_create_task(
            title=f"📋 PROJECT: {project_name}",
            notes=f"Project with {len(task_list)} tasks\n\nTasks:\n" + "\n".join([f"- {t}" for t in task_list]),
            due_date=due_date,
            priority=priority
        )
        
        if parent_result.get('success'):
            created_tasks.append(parent_result)
        
        # Create individual tasks
        for i, task_title in enumerate(task_list, 1):
            result = ai_create_task(
                title=f"{i}. {task_title}",
                notes=f"Part of project: {project_name}",
                due_date=due_date,
                priority=priority
            )
            
            if result.get('success'):
                created_tasks.append(result)
        
        print(f"✅ AI created {len(created_tasks)} tasks for project: {project_name}")
        
        return {
            'success': True,
            'project_name': project_name,
            'tasks_created': len(created_tasks),
            'task_ids': [t['task_id'] for t in created_tasks],
            'message': f"Created {len(created_tasks)} tasks for {project_name}"
        }
        
    except Exception as e:
        return {
            'success': False,
            'error': str(e)
        }


def ai_check_pending_work() -> Dict[str, Any]:
    """
    🤖 AI checks what work is pending from previous sessions.
    
    Use this at the start of a conversation to:
    - Resume previous work
    - Check for follow-ups
    - See high-priority items
    
    Returns:
        dict: Summary of pending work with high-priority items
    
    Example:
        # AI checks for pending work
        pending = ai_check_pending_work()
        if pending['high_priority_count'] > 0:
            print(f"I have {pending['high_priority_count']} high-priority tasks to address")
    """
    try:
        result = ai_list_my_tasks(show_completed=False)
        
        if not result.get('success'):
            return result
        
        tasks = result.get('tasks', [])
        
        # Categorize by priority
        high_priority = [t for t in tasks if '🔴' in t.get('title', '')]
        medium_priority = [t for t in tasks if '🟡' in t.get('title', '')]
        low_priority = [t for t in tasks if '🟢' in t.get('title', '')]
        
        # Check for overdue
        today = datetime.now().date()
        overdue = []
        for task in tasks:
            if task.get('due'):
                due_date = datetime.fromisoformat(task['due'].replace('Z', '+00:00')).date()
                if due_date < today:
                    overdue.append(task)
        
        summary = {
            'success': True,
            'total_pending': len(tasks),
            'high_priority_count': len(high_priority),
            'medium_priority_count': len(medium_priority),
            'low_priority_count': len(low_priority),
            'overdue_count': len(overdue),
            'high_priority_tasks': high_priority[:5],  # Top 5
            'overdue_tasks': overdue,
            'message': f"AI has {len(tasks)} pending tasks ({len(high_priority)} high priority, {len(overdue)} overdue)"
        }
        
        print(f"✅ {summary['message']}")
        
        return summary
        
    except Exception as e:
        return {
            'success': False,
            'error': str(e)
        }


# Example usage and self-documentation
if __name__ == "__main__":
    print("🤖 AI Personal Task Management System")
    print("=" * 50)
    
    # AI creates a task for itself
    result = ai_create_task(
        title="Test AI task management system",
        notes="Verify that AI can create and manage its own tasks",
        priority="high"
    )
    print(f"\nCreated task: {result}")
    
    # AI lists its tasks
    tasks = ai_list_my_tasks()
    print(f"\nMy tasks: {tasks}")
    
    # AI checks pending work
    pending = ai_check_pending_work()
    print(f"\nPending work: {pending}")

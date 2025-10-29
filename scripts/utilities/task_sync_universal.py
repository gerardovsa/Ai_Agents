"""
Universal Task Sync Module
===========================
Bidirectional sync between Kanban Board ↔ Google Tasks ↔ Microsoft 365 To Do

This module implements a UNIVERSAL field mapping strategy where:
- Kanban board has ALL fields from both platforms
- Sync functions map between universal format ↔ platform-specific format
- One source of truth (sessions table) syncs to multiple platforms

Author: System Architect
Date: 2025-10-28
Version: 1.0.0
"""

import re
import json
from typing import Dict, List, Optional, Any
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

# ============================================
# UNIVERSAL FIELD MAPPINGS
# ============================================

class UniversalTaskMapper:
    """Maps between Kanban universal format and platform-specific formats"""
    
    @staticmethod
    def kanban_to_google_task(kanban_card: Dict) -> Dict:
        """
        Convert Kanban card to Google Tasks format
        
        Args:
            kanban_card: Universal Kanban card data
            
        Returns:
            Google Tasks API compatible dictionary
        """
        # Build notes with embedded metadata
        notes_parts = [kanban_card.get('description', '')]
        
        # Add project
        if kanban_card.get('project_name'):
            notes_parts.append(f"\n📋 Project: {kanban_card['project_name']}")
        
        # Add tags
        if kanban_card.get('tags'):
            tags_str = ' '.join(f"#{tag}" for tag in kanban_card['tags'])
            notes_parts.append(f"🏷️ Tags: {tags_str}")
        
        # Add assignees
        if kanban_card.get('assignees'):
            assignees_str = ' '.join(f"@{a}" for a in kanban_card['assignees'])
            notes_parts.append(f"👥 Assignees: {assignees_str}")
        
        # Add Kanban column metadata (hidden in notes)
        notes_parts.append(f"\n📊 Kanban: <!-- KANBAN:{kanban_card.get('kanban_column', 'backlog')} -->")
        
        # Add documents
        if kanban_card.get('documents'):
            notes_parts.append("\n📄 Documents:")
            for doc in kanban_card['documents']:
                notes_parts.append(f"- [{doc.get('title', 'Document')}]({doc.get('url', '#')})")
        
        # Add links
        if kanban_card.get('links'):
            notes_parts.append("\n🔗 Links:")
            for link in kanban_card['links']:
                notes_parts.append(f"- [{link.get('title', 'Link')}]({link.get('url', '#')})")
        
        # Priority prefix in title
        priority_map = {
            'high': '[HIGH] ',
            'medium': '[MED] ',
            'low': '[LOW] '
        }
        priority_prefix = priority_map.get(kanban_card.get('priority', 'medium'), '')
        
        # Build Google Tasks object
        google_task = {
            'title': f"{priority_prefix}{kanban_card['title']}",
            'notes': '\n'.join(notes_parts),
            'status': 'completed' if kanban_card.get('status') == 'completed' else 'needsAction'
        }
        
        # Add due date if present
        if kanban_card.get('due_date'):
            google_task['due'] = kanban_card['due_date']
        
        logger.info(f"🔄 Mapped Kanban → Google Tasks: {kanban_card['title']}")
        return google_task
    
    @staticmethod
    def kanban_to_microsoft_todo(kanban_card: Dict) -> Dict:
        """
        Convert Kanban card to Microsoft To Do format
        
        Args:
            kanban_card: Universal Kanban card data
            
        Returns:
            Microsoft Graph API compatible dictionary
        """
        # Build body content
        body_parts = [kanban_card.get('description', '')]
        
        # Add project
        if kanban_card.get('project_name'):
            body_parts.append(f"\n📋 Project: {kanban_card['project_name']}")
        
        # Add assignees (To Do is personal, but we can store it)
        if kanban_card.get('assignees'):
            assignees_str = ' '.join(f"@{a}" for a in kanban_card['assignees'])
            body_parts.append(f"👥 Assignees: {assignees_str}")
        
        # Add Kanban column metadata (hidden in body)
        body_parts.append(f"\n📊 Kanban: <!-- KANBAN:{kanban_card.get('kanban_column', 'backlog')} -->")
        
        # Add documents
        if kanban_card.get('documents'):
            body_parts.append("\n📄 Documents:")
            for doc in kanban_card['documents']:
                body_parts.append(f"- [{doc.get('title', 'Document')}]({doc.get('url', '#')})")
        
        # Add links
        if kanban_card.get('links'):
            body_parts.append("\n🔗 Links:")
            for link in kanban_card['links']:
                body_parts.append(f"- [{link.get('title', 'Link')}]({link.get('url', '#')})")
        
        # Build categories (project + tags)
        categories = []
        if kanban_card.get('project_name'):
            categories.append(kanban_card['project_name'])
        if kanban_card.get('tags'):
            categories.extend(kanban_card['tags'])
        
        # Build checklist items
        checklist_items = []
        if kanban_card.get('checklist'):
            for item in kanban_card['checklist']:
                checklist_items.append({
                    'displayName': item.get('item', ''),
                    'isChecked': item.get('completed', False)
                })
        
        if kanban_card.get('next_steps'):
            for step in kanban_card['next_steps']:
                checklist_items.append({
                    'displayName': step.get('description', ''),
                    'isChecked': step.get('completed', False)
                })
        
        # Build Microsoft To Do object
        ms_task = {
            'title': kanban_card['title'],  # No prefix needed - direct importance field!
            'body': {
                'content': '\n'.join(body_parts),
                'contentType': 'text'
            },
            'importance': kanban_card.get('priority', 'normal'),  # Direct mapping!
            'status': 'completed' if kanban_card.get('status') == 'completed' else 'notStarted'
        }
        
        # Add optional fields
        if kanban_card.get('due_date'):
            ms_task['dueDateTime'] = {
                'dateTime': kanban_card['due_date'].replace('Z', ''),
                'timeZone': 'UTC'
            }
        
        if categories:
            ms_task['categories'] = categories
        
        if checklist_items:
            ms_task['checklistItems'] = checklist_items
        
        if kanban_card.get('reminder_date'):
            ms_task['reminderDateTime'] = {
                'dateTime': kanban_card['reminder_date'].replace('Z', ''),
                'timeZone': 'UTC'
            }
        
        logger.info(f"🔄 Mapped Kanban → Microsoft To Do: {kanban_card['title']}")
        return ms_task
    
    @staticmethod
    def google_task_to_kanban(google_task: Dict, subtasks: Optional[List[Dict]] = None) -> Dict:
        """
        Convert Google Tasks to Kanban card format
        
        Args:
            google_task: Google Tasks API response
            subtasks: List of subtasks (optional)
            
        Returns:
            Universal Kanban card dictionary
        """
        # Extract priority from title prefix
        title = google_task.get('title', 'Untitled Task')
        priority = 'medium'
        
        if title.startswith('[HIGH]'):
            priority = 'high'
            title = title.replace('[HIGH] ', '', 1)
        elif title.startswith('[LOW]'):
            priority = 'low'
            title = title.replace('[LOW] ', '', 1)
        elif title.startswith('[MED]'):
            title = title.replace('[MED] ', '', 1)
        
        # Parse notes for metadata
        notes = google_task.get('notes', '')
        
        # Extract Kanban column
        kanban_column = 'backlog'
        kanban_match = re.search(r'<!-- KANBAN:(\w+) -->', notes)
        if kanban_match:
            kanban_column = kanban_match.group(1)
        
        # Extract project name
        project_name = None
        project_match = re.search(r'📋 Project: (.+)', notes)
        if project_match:
            project_name = project_match.group(1).strip()
        
        # Extract tags
        tags = []
        tags_match = re.search(r'🏷️ Tags: (.+)', notes)
        if tags_match:
            tags = [tag.strip('#').strip() for tag in tags_match.group(1).split()]
        
        # Extract assignees
        assignees = []
        assignees_match = re.search(r'👥 Assignees: (.+)', notes)
        if assignees_match:
            assignees = [a.strip('@').strip() for a in assignees_match.group(1).split()]
        
        # Extract documents and links
        documents = []
        links = []
        doc_matches = re.findall(r'\[(.+?)\]\((.+?)\)', notes)
        
        in_docs_section = False
        in_links_section = False
        for line in notes.split('\n'):
            if '📄 Documents:' in line:
                in_docs_section = True
                in_links_section = False
            elif '🔗 Links:' in line:
                in_links_section = True
                in_docs_section = False
            elif line.startswith('- ['):
                match = re.search(r'\[(.+?)\]\((.+?)\)', line)
                if match:
                    item = {'title': match.group(1), 'url': match.group(2)}
                    if in_docs_section:
                        documents.append(item)
                    elif in_links_section:
                        links.append(item)
        
        # Convert subtasks to checklist
        checklist = []
        if subtasks:
            for subtask in subtasks:
                checklist.append({
                    'item': subtask.get('title', ''),
                    'completed': subtask.get('status') == 'completed'
                })
        
        # Clean description (remove metadata sections)
        description = notes
        for pattern in [r'📋 Project:.+', r'🏷️ Tags:.+', r'👥 Assignees:.+', 
                       r'📊 Kanban:.+', r'📄 Documents:.+', r'🔗 Links:.+',
                       r'<!-- KANBAN:\w+ -->']:
            description = re.sub(pattern, '', description, flags=re.MULTILINE)
        description = description.strip()
        
        # Build Kanban card
        kanban_card = {
            'title': title,
            'description': description,
            'priority': priority,
            'status': 'completed' if google_task.get('status') == 'completed' else 'active',
            'kanban_column': kanban_column,
            'project_name': project_name,
            'tags': tags,
            'assignees': assignees,
            'checklist': checklist,
            'documents': documents,
            'links': links,
            'created_at': google_task.get('created'),
            'updated_at': google_task.get('updated')
        }
        
        if google_task.get('due'):
            kanban_card['due_date'] = google_task['due']
        
        logger.info(f"🔄 Mapped Google Tasks → Kanban: {title}")
        return kanban_card
    
    @staticmethod
    def microsoft_todo_to_kanban(ms_task: Dict) -> Dict:
        """
        Convert Microsoft To Do to Kanban card format
        
        Args:
            ms_task: Microsoft Graph API response
            
        Returns:
            Universal Kanban card dictionary
        """
        # Extract body content
        body_content = ''
        if ms_task.get('body'):
            body_content = ms_task['body'].get('content', '')
        
        # Extract Kanban column
        kanban_column = 'backlog'
        kanban_match = re.search(r'<!-- KANBAN:(\w+) -->', body_content)
        if kanban_match:
            kanban_column = kanban_match.group(1)
        
        # Extract project name (first category)
        project_name = None
        categories = ms_task.get('categories', [])
        if categories:
            project_name = categories[0]
        
        # Other categories are tags
        tags = categories[1:] if len(categories) > 1 else []
        
        # Extract assignees
        assignees = []
        assignees_match = re.search(r'👥 Assignees: (.+)', body_content)
        if assignees_match:
            assignees = [a.strip('@').strip() for a in assignees_match.group(1).split()]
        
        # Extract documents and links
        documents = []
        links = []
        
        in_docs_section = False
        in_links_section = False
        for line in body_content.split('\n'):
            if '📄 Documents:' in line:
                in_docs_section = True
                in_links_section = False
            elif '🔗 Links:' in line:
                in_links_section = True
                in_docs_section = False
            elif line.startswith('- ['):
                match = re.search(r'\[(.+?)\]\((.+?)\)', line)
                if match:
                    item = {'title': match.group(1), 'url': match.group(2)}
                    if in_docs_section:
                        documents.append(item)
                    elif in_links_section:
                        links.append(item)
        
        # Convert checklist items
        checklist = []
        if ms_task.get('checklistItems'):
            for item in ms_task['checklistItems']:
                checklist.append({
                    'item': item.get('displayName', ''),
                    'completed': item.get('isChecked', False)
                })
        
        # Clean description (remove metadata sections)
        description = body_content
        for pattern in [r'📋 Project:.+', r'👥 Assignees:.+', 
                       r'📊 Kanban:.+', r'📄 Documents:.+', r'🔗 Links:.+',
                       r'<!-- KANBAN:\w+ -->']:
            description = re.sub(pattern, '', description, flags=re.MULTILINE)
        description = description.strip()
        
        # Parse due date
        due_date = None
        if ms_task.get('dueDateTime'):
            due_date = ms_task['dueDateTime'].get('dateTime', '') + 'Z'
        
        # Parse reminder
        reminder_date = None
        if ms_task.get('reminderDateTime'):
            reminder_date = ms_task['reminderDateTime'].get('dateTime', '') + 'Z'
        
        # Build Kanban card
        kanban_card = {
            'title': ms_task.get('title', 'Untitled Task'),
            'description': description,
            'priority': ms_task.get('importance', 'normal'),  # Direct mapping!
            'status': 'completed' if ms_task.get('status') == 'completed' else 'active',
            'kanban_column': kanban_column,
            'project_name': project_name,
            'tags': tags,
            'assignees': assignees,
            'checklist': checklist,
            'documents': documents,
            'links': links,
            'created_at': ms_task.get('createdDateTime'),
            'updated_at': ms_task.get('lastModifiedDateTime')
        }
        
        if due_date:
            kanban_card['due_date'] = due_date
        
        if reminder_date:
            kanban_card['reminder_date'] = reminder_date
        
        logger.info(f"🔄 Mapped Microsoft To Do → Kanban: {kanban_card['title']}")
        return kanban_card


# ============================================
# SYNC HELPER FUNCTIONS
# ============================================

def create_google_task_with_checklist(kanban_card: Dict, google_tasks_client) -> Dict:
    """
    Create Google Task with checklist as subtasks
    
    Args:
        kanban_card: Universal Kanban card
        google_tasks_client: Google Tasks API client
        
    Returns:
        Created task info with subtask IDs
    """
    mapper = UniversalTaskMapper()
    
    # Create main task
    main_task_data = mapper.kanban_to_google_task(kanban_card)
    task_list_id = kanban_card.get('google_task_list_id', '@default')
    
    main_task = google_tasks_client.create_task(
        task_list_id=task_list_id,
        **main_task_data
    )
    
    # Create subtasks for checklist items
    subtask_ids = []
    if kanban_card.get('checklist'):
        for item in kanban_card['checklist']:
            subtask = google_tasks_client.create_task(
                task_list_id=task_list_id,
                title=item['item'],
                parent=main_task['id'],
                status='completed' if item.get('completed') else 'needsAction'
            )
            subtask_ids.append(subtask['id'])
    
    # Create subtasks for next_steps
    if kanban_card.get('next_steps'):
        for step in kanban_card['next_steps']:
            subtask = google_tasks_client.create_task(
                task_list_id=task_list_id,
                title=step['description'],
                parent=main_task['id'],
                status='completed' if step.get('completed') else 'needsAction'
            )
            subtask_ids.append(subtask['id'])
    
    logger.info(f"✅ Created Google Task with {len(subtask_ids)} subtasks: {main_task['id']}")
    
    return {
        'main_task': main_task,
        'subtask_ids': subtask_ids
    }


def create_microsoft_todo_task(kanban_card: Dict, microsoft_client) -> Dict:
    """
    Create Microsoft To Do task with checklist
    
    Args:
        kanban_card: Universal Kanban card
        microsoft_client: Microsoft Graph API client
        
    Returns:
        Created task info
    """
    mapper = UniversalTaskMapper()
    
    # Convert to Microsoft format (includes checklist automatically!)
    ms_task_data = mapper.kanban_to_microsoft_todo(kanban_card)
    list_id = kanban_card.get('microsoft_todo_list_id')
    
    # Create task
    ms_task = microsoft_client.create_task(
        list_id=list_id,
        **ms_task_data
    )
    
    logger.info(f"✅ Created Microsoft To Do task: {ms_task['id']}")
    
    return ms_task


def update_google_task_from_kanban(kanban_card: Dict, google_task_id: str, 
                                   google_tasks_client) -> Dict:
    """
    Update existing Google Task from Kanban changes
    
    Args:
        kanban_card: Updated Kanban card
        google_task_id: Google Task ID to update
        google_tasks_client: Google Tasks API client
        
    Returns:
        Updated task info
    """
    mapper = UniversalTaskMapper()
    
    # Map to Google format
    update_data = mapper.kanban_to_google_task(kanban_card)
    task_list_id = kanban_card.get('google_task_list_id', '@default')
    
    # Update main task
    updated_task = google_tasks_client.update_task(
        task_list_id=task_list_id,
        task_id=google_task_id,
        **update_data
    )
    
    # TODO: Handle subtask updates (requires fetching existing subtasks)
    
    logger.info(f"✅ Updated Google Task: {google_task_id}")
    return updated_task


def update_microsoft_todo_from_kanban(kanban_card: Dict, ms_task_id: str,
                                     microsoft_client) -> Dict:
    """
    Update existing Microsoft To Do task from Kanban changes
    
    Args:
        kanban_card: Updated Kanban card
        ms_task_id: Microsoft To Do task ID
        microsoft_client: Microsoft Graph API client
        
    Returns:
        Updated task info
    """
    mapper = UniversalTaskMapper()
    
    # Map to Microsoft format
    update_data = mapper.kanban_to_microsoft_todo(kanban_card)
    
    # Update task
    updated_task = microsoft_client.update_task(
        task_id=ms_task_id,
        **update_data
    )
    
    logger.info(f"✅ Updated Microsoft To Do task: {ms_task_id}")
    return updated_task


# ============================================
# EXAMPLE USAGE
# ============================================

if __name__ == "__main__":
    # Example: Create universal Kanban card
    kanban_card = {
        'title': 'Review Q4 Budget',
        'description': 'Focus on marketing spend and ROI analysis',
        'priority': 'high',
        'status': 'active',
        'due_date': '2025-10-31T17:00:00Z',
        'kanban_column': 'in_progress',
        'project_name': 'Finance Review',
        'tags': ['budget', 'q4', 'urgent'],
        'assignees': ['John Doe', 'Jane Smith'],
        'checklist': [
            {'item': 'Review marketing budget', 'completed': False},
            {'item': 'Analyze ROI metrics', 'completed': False}
        ],
        'documents': [
            {'title': 'Budget Spreadsheet', 'url': 'https://docs.google.com/...'}
        ]
    }
    
    # Map to Google Tasks
    mapper = UniversalTaskMapper()
    google_format = mapper.kanban_to_google_task(kanban_card)
    print("Google Tasks Format:")
    print(json.dumps(google_format, indent=2))
    
    # Map to Microsoft To Do
    ms_format = mapper.kanban_to_microsoft_todo(kanban_card)
    print("\nMicrosoft To Do Format:")
    print(json.dumps(ms_format, indent=2))

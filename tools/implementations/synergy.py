"""
Synergy Dashboard Tools - Visual Kanban Project Management
============================================================

Integration with Synergy Dashboard for visual project tracking.
Uses REST API at http://localhost:5001/api/synergy/*

Functions:
- synergy_smart_project_tracker: SMART TOOL - Complete project setup in ONE call
- synergy_create_session: Create new project card
- synergy_list_sessions: List/filter sessions
- synergy_get_session: Get session details
- synergy_update_session: Update session (add documents, change status, etc.)
- synergy_move_session: Move between Kanban columns
- synergy_delete_session: Delete session
- synergy_sync_to_google: Sync to Google Tasks/Calendar
"""

import requests
from typing import Dict, List, Optional, Any
import json

# Synergy backend URL
SYNERGY_API_BASE = "http://localhost:5001/api/synergy"


class SynergyError(Exception):
    """Custom exception for Synergy API errors"""
    pass


def synergy_smart_project_tracker(
    title: str,
    platforms_involved: List[str],
    next_steps: List[str],
    description: Optional[str] = None,
    priority: str = "high",
    start_in_column: str = "in_progress",
    initial_documents: Optional[List[Dict[str, str]]] = None,
    due_date: Optional[str] = None,
    tags: Optional[List[str]] = None,
    auto_update_mode: bool = True,
    sync_to_google: bool = False,
    notify_user: bool = True,
    **kwargs
) -> Dict[str, Any]:
    """
    SMART TOOL: Complete multi-platform project tracking in ONE call
    
    This is your PRIMARY tool for complex multi-step projects. It:
    1. Creates Synergy session with proper structure
    2. Sets up initial documents (if provided)
    3. Configures next steps checklist
    4. Places in correct Kanban column
    5. Optionally syncs to Google Tasks
    6. Returns dashboard URL and session info
    
    Use this INSTEAD of calling synergy_create_session + synergy_update_session
    
    Args:
        title: Project title (required)
        platforms_involved: List of platforms ['gmail', 'sheets', 'forms', etc.]
        next_steps: Action items checklist
        description: What you're building (auto-generated if not provided)
        priority: Priority level (default: high)
        start_in_column: backlog or in_progress (default: in_progress)
        initial_documents: Documents already created [{"name": "", "url": "", "type": ""}]
        due_date: Due date ISO format
        tags: Tags for filtering
        auto_update_mode: AI updates automatically (default: true)
        sync_to_google: Also create Google Task (default: false)
        notify_user: Tell user about dashboard (default: true)
        
    Returns:
        Dict with:
        - session_id: For future updates
        - session: Complete session object
        - dashboard_url: http://localhost:5001
        - message: User-friendly status message
        - auto_update_enabled: Whether AI will auto-update
        
    Example:
        result = synergy_smart_project_tracker(
            title="Customer Onboarding System",
            platforms_involved=["gmail", "forms", "sheets"],
            next_steps=[
                "Create welcome email template",
                "Create signup form",
                "Create tracking spreadsheet"
            ],
            priority="high"
        )
        
        print(result["message"])
        # "✅ Project tracker created! View dashboard: http://localhost:5001"
        # AI will auto-update as you create documents
    """
    try:
        # Parse JSON strings if needed
        if isinstance(platforms_involved, str):
            try:
                platforms_involved = json.loads(platforms_involved)
            except json.JSONDecodeError:
                raise SynergyError(f"Invalid JSON for platforms_involved: {platforms_involved}")
        
        if isinstance(next_steps, str):
            try:
                next_steps = json.loads(next_steps)
            except json.JSONDecodeError:
                raise SynergyError(f"Invalid JSON for next_steps: {next_steps}")
        
        if initial_documents and isinstance(initial_documents, str):
            try:
                initial_documents = json.loads(initial_documents)
            except json.JSONDecodeError:
                raise SynergyError(f"Invalid JSON for initial_documents: {initial_documents}")
        
        if tags and isinstance(tags, str):
            try:
                tags = json.loads(tags)
            except json.JSONDecodeError:
                raise SynergyError(f"Invalid JSON for tags: {tags}")
        
        # Auto-generate description if not provided
        if not description:
            platform_str = ", ".join(platforms_involved)
            description = f"Multi-platform project involving: {platform_str}"
        
        # Auto-generate tags from platforms if not provided
        if not tags:
            tags = platforms_involved + ["multi-platform", "automation"]
        
        # Build payload
        payload = {
            "title": title,
            "description": description,
            "project_name": title,  # Use title as project name
            "priority": priority,
            "kanban_column": start_in_column,
            "status": "active",
            "assignees": ["AI Agent"],
            "tags": tags,
            "notes": f"Auto-update mode: {'ON' if auto_update_mode else 'OFF'}\nPlatforms: {', '.join(platforms_involved)}",
            "documents": initial_documents or [],
            "links": [],
            "next_steps": next_steps
        }
        
        if due_date:
            payload["due_date"] = due_date
        
        # Create session via API
        response = requests.post(
            f"{SYNERGY_API_BASE}/create",
            json=payload,
            headers={"Content-Type": "application/json"},
            timeout=10
        )
        
        response.raise_for_status()
        session = response.json()
        session_id = session.get("session_id")
        
        # Optionally sync to Google Tasks
        google_sync_status = ""
        if sync_to_google:
            try:
                sync_response = requests.patch(
                    f"{SYNERGY_API_BASE}/{session_id}",
                    json={
                        "updates": {},
                        "sync_options": {
                            "sync_google_tasks": True,
                            "sync_google_calendar": False
                        }
                    },
                    timeout=10
                )
                if sync_response.ok:
                    google_sync_status = " (Also synced to Google Tasks)"
            except:
                google_sync_status = " (Google sync failed - continuing with Synergy only)"
        
        # Build user message
        dashboard_url = "http://localhost:5001"
        doc_count = len(initial_documents) if initial_documents else 0
        
        message_parts = [
            f"✅ Project tracker created: {title}",
            f"📊 Dashboard: {dashboard_url}",
            f"🎯 Priority: {priority}",
            f"📋 Next Steps: {len(next_steps)} action items",
            f"🔧 Platforms: {', '.join(platforms_involved)}"
        ]
        
        if doc_count > 0:
            message_parts.append(f"📄 Initial Documents: {doc_count}")
        
        if auto_update_mode:
            message_parts.append("🤖 AI will auto-update as work progresses")
        
        if google_sync_status:  # Only append if not empty string
            message_parts.append(google_sync_status)
        
        user_message = "\n".join(message_parts)
        
        return {
            "success": True,
            "session_id": session_id,
            "session": session,
            "dashboard_url": dashboard_url,
            "message": user_message,
            "auto_update_enabled": auto_update_mode,
            "platforms": platforms_involved,
            "notify_user": notify_user
        }
        
    except requests.exceptions.RequestException as e:
        raise SynergyError(f"Failed to create smart project tracker: {str(e)}")
    except Exception as e:
        raise SynergyError(f"Unexpected error in smart project tracker: {str(e)}")


def synergy_create_session(
    title: str,
    description: Optional[str] = None,
    project_name: Optional[str] = None,
    priority: str = "medium",
    kanban_column: str = "backlog",
    due_date: Optional[str] = None,
    assignees: Optional[List[str]] = None,
    tags: Optional[List[str]] = None,
    notes: Optional[str] = None,
    documents: Optional[List[Dict[str, str]]] = None,
    links: Optional[List[Dict[str, str]]] = None,
    next_steps: Optional[List[str]] = None,
    thread_ids: Optional[List[str]] = None,
    assigned_agents: Optional[List[str]] = None,
    sync_google_tasks: bool = False,
    sync_google_calendar: bool = False,
    **kwargs
) -> Dict[str, Any]:
    # CRITICAL AUTO-LINKING: Extract thread_id and agent context from kwargs
    current_thread_id = kwargs.get('thread_id') or kwargs.get('_thread_id')
    current_agent_id = kwargs.get('agent_id') or kwargs.get('_agent_id')
    
    # Auto-link current thread if available
    if current_thread_id:
        if thread_ids is None:
            thread_ids = []
        if current_thread_id not in thread_ids:
            thread_ids.append(current_thread_id)
            print(f"AUTO-LINK: Thread {current_thread_id} automatically linked to new Synergy session")
    
    # Auto-assign current agent if available
    if current_agent_id:
        if assigned_agents is None:
            assigned_agents = []
        agent_name = f"Agent-{current_agent_id}" if current_agent_id.isdigit() else current_agent_id
        if agent_name not in assigned_agents:
            assigned_agents.append(agent_name)
            print(f"AUTO-ASSIGN: Agent {agent_name} automatically assigned to new Synergy session")
    """
    Create a new session card in Synergy Dashboard
    
    Args:
        title: Session title (required)
        description: Detailed description
        project_name: Project name for grouping
        priority: Priority level (low|medium|high|critical)
        kanban_column: Kanban column (backlog|in_progress|review|done)
        due_date: Due date (ISO format)
        assignees: List of assignee names/emails
        tags: List of tags for categorization
        notes: Additional notes
        documents: List of document objects with name, url, type
        links: List of link objects with title, url
        next_steps: List of next action items
        thread_ids: Link conversation thread IDs to this session
        assigned_agents: AI agents assigned to work on this session
        sync_google_tasks: Sync to Google Tasks
        sync_google_calendar: Sync to Google Calendar
        
    Returns:
        Dict with session object including session_id
        
    Raises:
        SynergyError: If API call fails
    """
    try:
        payload = {
            "title": title,
            "description": description or "",
            "project_name": project_name or "",
            "priority": priority,
            "kanban_column": kanban_column,
            "status": "active",
            "assignees": assignees or [],
            "tags": tags or [],
            "notes": notes or "",
            "documents": documents or [],
            "links": links or [],
            "next_steps": next_steps or [],
            "thread_ids": thread_ids or [],
            "assigned_agents": assigned_agents or []
        }
        
        if due_date:
            payload["due_date"] = due_date
        
        response = requests.post(
            f"{SYNERGY_API_BASE}/create",
            json=payload,
            headers={"Content-Type": "application/json"},
            timeout=10
        )
        
        response.raise_for_status()
        session = response.json()
        
        # Handle Google sync if requested
        if sync_google_tasks or sync_google_calendar:
            session_id = session.get("session_id")
            if session_id:
                try:
                    sync_result = synergy_sync_to_google(
                        session_id=session_id,
                        sync_tasks=sync_google_tasks,
                        sync_calendar=sync_google_calendar
                    )
                    # Update session with sync IDs
                    if sync_result:
                        session.update(sync_result)
                except Exception as e:
                    print(f"⚠️ Google sync failed: {e}")
        
        return {
            "success": True,
            "session_id": session.get("session_id"),
            "session": session,
            "message": f"✅ Created session: {title}",
            "kanban_column": kanban_column,
            "synced_to_google_tasks": sync_google_tasks and session.get("google_task_id") is not None,
            "synced_to_google_calendar": sync_google_calendar and session.get("google_calendar_event_id") is not None
        }
        
    except requests.exceptions.RequestException as e:
        raise SynergyError(f"Failed to create session: {str(e)}")


def synergy_list_sessions(
    column: Optional[str] = None,
    priority: Optional[str] = None,
    status: Optional[str] = None,
    **kwargs
) -> List[Dict[str, Any]]:
    """
    List sessions from Synergy Dashboard with optional filtering
    
    Args:
        column: Filter by Kanban column (backlog|in_progress|review|done)
        priority: Filter by priority (low|medium|high|critical)
        status: Filter by status (active|completed|archived)
        
    Returns:
        List of session objects
        
    Raises:
        SynergyError: If API call fails
    """
    try:
        params = {}
        if column:
            params["column"] = column
        if priority:
            params["priority"] = priority
        if status:
            params["status"] = status
        
        response = requests.get(
            f"{SYNERGY_API_BASE}/list",
            params=params,
            timeout=10
        )
        
        response.raise_for_status()
        sessions = response.json()
        
        return {
            "success": True,
            "count": len(sessions),
            "sessions": sessions,
            "filters": {
                "column": column,
                "priority": priority,
                "status": status
            }
        }
        
    except requests.exceptions.RequestException as e:
        raise SynergyError(f"Failed to list sessions: {str(e)}")


def synergy_get_session(
    session_id: str,
    **kwargs
) -> Dict[str, Any]:
    """
    Get a specific session by ID
    
    Args:
        session_id: Session ID to retrieve
        
    Returns:
        Session object with all fields
        
    Raises:
        SynergyError: If API call fails or session not found
    """
    try:
        response = requests.get(
            f"{SYNERGY_API_BASE}/{session_id}",
            timeout=10
        )
        
        response.raise_for_status()
        session = response.json()
        
        return {
            "success": True,
            "session": session
        }
        
    except requests.exceptions.RequestException as e:
        raise SynergyError(f"Failed to get session {session_id}: {str(e)}")


def synergy_update_session(
    session_id: str,
    title: Optional[str] = None,
    description: Optional[str] = None,
    priority: Optional[str] = None,
    status: Optional[str] = None,
    kanban_column: Optional[str] = None,
    due_date: Optional[str] = None,
    documents: Optional[List[Dict[str, str]]] = None,
    links: Optional[List[Dict[str, str]]] = None,
    next_steps: Optional[List[str]] = None,
    tags: Optional[List[str]] = None,
    assignees: Optional[List[str]] = None,
    platforms_involved: Optional[List[str]] = None,
    checklist: Optional[List[Dict[str, Any]]] = None,
    thread_ids: Optional[List[str]] = None,
    assigned_agents: Optional[List[str]] = None,
    sync_google_tasks: bool = False,
    sync_google_calendar: bool = False,
    **kwargs
) -> Dict[str, Any]:
    """
    SMART UPDATE TOOL: Update any field(s) in a Synergy session
    
    This tool intelligently handles all session updates in ONE call.
    Pass only the fields you want to update - omitted fields stay unchanged.
    
    CRITICAL FOR ARRAYS (documents, links, next_steps, etc.):
    - Arrays REPLACE the entire field
    - To ADD an item: Pass ALL existing items PLUS the new one
    - To REMOVE an item: Pass only the items you want to keep
    
    Args:
        session_id: Session ID to update (required)
        title: Update title
        description: Update description
        priority: Update priority (low|medium|high|critical)
        status: Update status (active|completed|archived)
        kanban_column: Move to column (backlog|in_progress|review|done)
        due_date: Update due date (ISO format YYYY-MM-DD)
        documents: REPLACE all documents. Format: [{"title": "Name", "url": "https://...", "type": "google_doc"}]
        links: REPLACE all links. Format: [{"title": "Dashboard", "url": "https://..."}]
        next_steps: REPLACE all next steps. Format: ["Step 1", "Step 2"]
        tags: REPLACE all tags. Format: ["email", "automation"]
        assignees: REPLACE all assignees. Format: ["John Doe", "jane@example.com"]
        platforms_involved: REPLACE platforms list. Format: ["gmail", "sheets"]
        checklist: REPLACE checklist. Format: [{"text": "Task", "completed": false}]
        thread_ids: REPLACE thread IDs. Link conversation threads. Format: ["thread_123", "thread_456"]
        assigned_agents: REPLACE assigned agents. AI agents working on this. Format: ["Research Agent", "Email Agent"]
        sync_google_tasks: Also sync to Google Tasks (if linked)
        sync_google_calendar: Also sync to Google Calendar (if linked)
        
    Returns:
        Dict with success status, updated session, and confirmation message
        
    Raises:
        SynergyError: If API call fails
        
    Examples:
        # Add a new document (must include ALL documents)
        synergy_update_session(
            session_id="sess_123",
            documents=[
                {"title": "Existing Doc", "url": "https://...", "type": "google_doc"},
                {"title": "New Doc", "url": "https://...", "type": "google_sheet"}
            ]
        )
        
        # Link thread and assign agents
        synergy_update_session(
            session_id="sess_123",
            thread_ids=["thread_abc123", "thread_def456"],
            assigned_agents=["Research Agent", "Email Agent", "Data Analysis Agent"]
        )
        
        # Update priority and move column
        synergy_update_session(
            session_id="sess_123",
            priority="high",
            kanban_column="review"
        )
    """
    try:
        # Build updates dict from provided parameters
        updates = {}
        
        # Simple fields
        if title is not None:
            updates["title"] = title
        if description is not None:
            updates["description"] = description
        if priority is not None:
            updates["priority"] = priority
        if status is not None:
            updates["status"] = status
        if kanban_column is not None:
            updates["kanban_column"] = kanban_column
        if due_date is not None:
            updates["due_date"] = due_date
        
        # Array fields (these REPLACE the entire field)
        if documents is not None:
            # Parse JSON string if needed
            if isinstance(documents, str):
                try:
                    documents = json.loads(documents)
                except json.JSONDecodeError:
                    raise SynergyError(f"Invalid JSON for documents parameter: {documents}")
            
            # Normalize document structure: name -> title
            normalized_docs = []
            for doc in documents:
                # If doc is a string, convert to dict
                if isinstance(doc, str):
                    try:
                        doc = json.loads(doc)
                    except json.JSONDecodeError:
                        raise SynergyError(f"Invalid JSON for document entry: {doc}")
                
                # Now copy the dict
                normalized_doc = doc.copy()
                if 'name' in normalized_doc and 'title' not in normalized_doc:
                    normalized_doc['title'] = normalized_doc.pop('name')
                normalized_docs.append(normalized_doc)
            updates["documents"] = normalized_docs
            
        if links is not None:
            # Parse JSON string if needed
            if isinstance(links, str):
                try:
                    links = json.loads(links)
                except json.JSONDecodeError:
                    raise SynergyError(f"Invalid JSON for links parameter: {links}")
            
            # Normalize link structure: name -> title
            normalized_links = []
            for link in links:
                # If link is a string, convert to dict
                if isinstance(link, str):
                    try:
                        link = json.loads(link)
                    except json.JSONDecodeError:
                        raise SynergyError(f"Invalid JSON for link entry: {link}")
                
                # Now copy the dict
                normalized_link = link.copy()
                if 'name' in normalized_link and 'title' not in normalized_link:
                    normalized_link['title'] = normalized_link.pop('name')
                normalized_links.append(normalized_link)
            updates["links"] = normalized_links
            
        if next_steps is not None:
            # Parse JSON string if needed
            if isinstance(next_steps, str):
                try:
                    next_steps = json.loads(next_steps)
                except json.JSONDecodeError:
                    raise SynergyError(f"Invalid JSON for next_steps parameter: {next_steps}")
            updates["next_steps"] = next_steps
            
        if tags is not None:
            # Parse JSON string if needed
            if isinstance(tags, str):
                try:
                    tags = json.loads(tags)
                except json.JSONDecodeError:
                    raise SynergyError(f"Invalid JSON for tags parameter: {tags}")
            updates["tags"] = tags
            
        if assignees is not None:
            # Parse JSON string if needed
            if isinstance(assignees, str):
                try:
                    assignees = json.loads(assignees)
                except json.JSONDecodeError:
                    raise SynergyError(f"Invalid JSON for assignees parameter: {assignees}")
            updates["assignees"] = assignees
            
        if platforms_involved is not None:
            # Parse JSON string if needed
            if isinstance(platforms_involved, str):
                try:
                    platforms_involved = json.loads(platforms_involved)
                except json.JSONDecodeError:
                    raise SynergyError(f"Invalid JSON for platforms_involved parameter: {platforms_involved}")
            updates["platforms_involved"] = platforms_involved
            
        if checklist is not None:
            # Parse JSON string if needed
            if isinstance(checklist, str):
                try:
                    checklist = json.loads(checklist)
                except json.JSONDecodeError:
                    raise SynergyError(f"Invalid JSON for checklist parameter: {checklist}")
            updates["checklist"] = checklist
            
        if thread_ids is not None:
            # Parse JSON string if needed
            if isinstance(thread_ids, str):
                try:
                    thread_ids = json.loads(thread_ids)
                except json.JSONDecodeError:
                    raise SynergyError(f"Invalid JSON for thread_ids parameter: {thread_ids}")
            updates["thread_ids"] = thread_ids
            
        if assigned_agents is not None:
            # Parse JSON string if needed
            if isinstance(assigned_agents, str):
                try:
                    assigned_agents = json.loads(assigned_agents)
                except json.JSONDecodeError:
                    raise SynergyError(f"Invalid JSON for assigned_agents parameter: {assigned_agents}")
            updates["assigned_agents"] = assigned_agents
        
        # Build payload
        payload = {
            "updates": updates
        }
        
        # Add sync options if requested
        if sync_google_tasks or sync_google_calendar:
            payload["sync"] = {
                "google_tasks": sync_google_tasks,
                "google_calendar": sync_google_calendar
            }
        
        # Make API call
        response = requests.patch(
            f"{SYNERGY_API_BASE}/{session_id}",
            json=payload,
            headers={"Content-Type": "application/json"},
            timeout=10
        )
        
        response.raise_for_status()
        result = response.json()
        
        # Build user-friendly message
        updated_fields = list(updates.keys())
        field_summary = []
        
        if "documents" in updated_fields:
            doc_count = len(documents) if documents else 0
            field_summary.append(f"📄 {doc_count} documents")
        if "links" in updated_fields:
            link_count = len(links) if links else 0
            field_summary.append(f"🔗 {link_count} links")
        if "next_steps" in updated_fields:
            step_count = len(next_steps) if next_steps else 0
            field_summary.append(f"📋 {step_count} next steps")
        if "thread_ids" in updated_fields:
            thread_count = len(thread_ids) if thread_ids else 0
            field_summary.append(f"💬 {thread_count} threads")
        if "assigned_agents" in updated_fields:
            agent_count = len(assigned_agents) if assigned_agents else 0
            field_summary.append(f"🤖 {agent_count} agents")
        if "priority" in updated_fields:
            field_summary.append(f"🎯 Priority: {priority}")
        if "kanban_column" in updated_fields:
            field_summary.append(f"📊 Column: {kanban_column}")
        if "status" in updated_fields:
            field_summary.append(f"⚡ Status: {status}")
        
        summary_str = ", ".join(field_summary) if field_summary else "session"
        
        return {
            "success": True,
            "session_id": session_id,
            "message": f"✅ Updated {summary_str}",
            "updated_fields": updated_fields,
            "session": result
        }
        
    except requests.exceptions.RequestException as e:
        raise SynergyError(f"Failed to update session {session_id}: {str(e)}")


def synergy_move_session(
    session_id: str,
    target_column: str,
    notes: Optional[str] = None,
    **kwargs
) -> Dict[str, Any]:
    """
    Move a session to a different Kanban column
    
    Args:
        session_id: Session ID to move
        target_column: Target column (backlog|in_progress|review|done)
        notes: Optional notes about the move/progress
        
    Returns:
        Updated session object
        
    Raises:
        SynergyError: If API call fails
    """
    try:
        payload = {
            "target_column": target_column
        }
        
        if notes:
            payload["notes"] = notes
        
        response = requests.patch(
            f"{SYNERGY_API_BASE}/{session_id}/column",
            json=payload,
            headers={"Content-Type": "application/json"},
            timeout=10
        )
        
        response.raise_for_status()
        session = response.json()
        
        return {
            "success": True,
            "session_id": session_id,
            "session": session,
            "message": f"✅ Moved session to {target_column}",
            "previous_column": session.get("kanban_column"),
            "new_column": target_column
        }
        
    except requests.exceptions.RequestException as e:
        raise SynergyError(f"Failed to move session {session_id}: {str(e)}")


def synergy_delete_session(
    session_id: str,
    **kwargs
) -> Dict[str, Any]:
    """
    Delete a session from Synergy Dashboard
    
    Args:
        session_id: Session ID to delete
        
    Returns:
        Success message
        
    Raises:
        SynergyError: If API call fails
    """
    try:
        response = requests.delete(
            f"{SYNERGY_API_BASE}/{session_id}",
            timeout=10
        )
        
        response.raise_for_status()
        result = response.json()
        
        return {
            "success": True,
            "session_id": session_id,
            "message": f"✅ Deleted session: {session_id}"
        }
        
    except requests.exceptions.RequestException as e:
        raise SynergyError(f"Failed to delete session {session_id}: {str(e)}")


def synergy_sync_to_google(
    session_id: str,
    sync_tasks: bool = False,
    sync_calendar: bool = False,
    **kwargs
) -> Dict[str, Any]:
    """
    Sync an existing session to Google Tasks and/or Google Calendar
    
    Args:
        session_id: Session ID to sync
        sync_tasks: Sync to Google Tasks
        sync_calendar: Sync to Google Calendar
        
    Returns:
        Session object with google_task_id and/or google_calendar_event_id
        
    Raises:
        SynergyError: If API call fails
    """
    try:
        payload = {
            "updates": {},
            "sync": {
                "google_tasks": sync_tasks,
                "google_calendar": sync_calendar
            }
        }
        
        response = requests.patch(
            f"{SYNERGY_API_BASE}/{session_id}",
            json=payload,
            headers={"Content-Type": "application/json"},
            timeout=10
        )
        
        response.raise_for_status()
        session = response.json()
        
        return {
            "success": True,
            "session_id": session_id,
            "session": session,
            "message": f"✅ Synced to Google",
            "google_task_id": session.get("google_task_id"),
            "google_calendar_event_id": session.get("google_calendar_event_id"),
            "synced_to_tasks": sync_tasks and session.get("google_task_id") is not None,
            "synced_to_calendar": sync_calendar and session.get("google_calendar_event_id") is not None
        }
        
    except requests.exceptions.RequestException as e:
        raise SynergyError(f"Failed to sync session {session_id} to Google: {str(e)}")


# ============================================================================
# APPEND-ONLY HELPER FUNCTIONS (Efficient single-item additions)
# ============================================================================

def synergy_add_document(
    session_id: str,
    title: str,
    url: str,
    type: Optional[str] = None,
    **kwargs
) -> Dict[str, Any]:
    """
    APPEND a single document to existing session (preserves existing documents)
    
    Much more efficient than synergy_update_session for adding one document.
    No need to fetch existing documents first - this appends automatically.
    
    Args:
        session_id: Session ID (required)
        title: Document name/title (required)
        url: Document URL (required)
        type: Document type (google_doc|google_sheet|google_form|google_slides|pdf|etc.)
        
    Returns:
        Updated session with new document appended
        
    Raises:
        SynergyError: If API call fails
        
    Example:
        synergy_add_document(
            session_id="sess_123",
            title="Customer Survey Results",
            url="https://docs.google.com/spreadsheets/d/...",
            type="google_sheet"
        )
    """
    try:
        # First, get current session to fetch existing documents
        response = requests.get(f"{SYNERGY_API_BASE}/{session_id}", timeout=10)
        response.raise_for_status()
        session = response.json()
        
        # Get existing documents (or empty list)
        existing_docs = session.get("documents", [])
        
        # Build new document object
        new_doc = {"title": title, "url": url}
        if type:
            new_doc["type"] = type
        
        # Append new document to existing
        updated_docs = existing_docs + [new_doc]
        
        # Update session with complete documents list
        payload = {"updates": {"documents": updated_docs}}
        
        response = requests.patch(
            f"{SYNERGY_API_BASE}/{session_id}",
            json=payload,
            headers={"Content-Type": "application/json"},
            timeout=10
        )
        
        response.raise_for_status()
        updated_session = response.json()
        
        return {
            "success": True,
            "session_id": session_id,
            "session": updated_session,
            "message": f"✅ Added document: {title}",
            "document_count": len(updated_session.get("documents", []))
        }
        
    except requests.exceptions.RequestException as e:
        raise SynergyError(f"Failed to add document to session {session_id}: {str(e)}")


def synergy_add_link(
    session_id: str,
    title: str,
    url: str,
    **kwargs
) -> Dict[str, Any]:
    """
    APPEND a single link to existing session (preserves existing links)
    
    Args:
        session_id: Session ID (required)
        title: Link title/description (required)
        url: Link URL (required)
        
    Returns:
        Updated session with new link appended
        
    Raises:
        SynergyError: If API call fails
    """
    try:
        # Get current session
        response = requests.get(f"{SYNERGY_API_BASE}/{session_id}", timeout=10)
        response.raise_for_status()
        session = response.json()
        
        # Get existing links
        existing_links = session.get("links", [])
        
        # Append new link
        new_link = {"title": title, "url": url}
        updated_links = existing_links + [new_link]
        
        # Update session
        payload = {"updates": {"links": updated_links}}
        
        response = requests.patch(
            f"{SYNERGY_API_BASE}/{session_id}",
            json=payload,
            headers={"Content-Type": "application/json"},
            timeout=10
        )
        
        response.raise_for_status()
        updated_session = response.json()
        
        return {
            "success": True,
            "session_id": session_id,
            "session": updated_session,
            "message": f"✅ Added link: {title}",
            "link_count": len(updated_session.get("links", []))
        }
        
    except requests.exceptions.RequestException as e:
        raise SynergyError(f"Failed to add link to session {session_id}: {str(e)}")


def synergy_add_next_step(
    session_id: str,
    step: str,
    **kwargs
) -> Dict[str, Any]:
    """
    APPEND a single next step to existing session (preserves existing steps)
    
    Args:
        session_id: Session ID (required)
        step: Next step description (required)
        
    Returns:
        Updated session with new step appended
        
    Raises:
        SynergyError: If API call fails
    """
    try:
        # Get current session
        response = requests.get(f"{SYNERGY_API_BASE}/{session_id}", timeout=10)
        response.raise_for_status()
        session = response.json()
        
        # Get existing steps
        existing_steps = session.get("next_steps", [])
        
        # Append new step
        updated_steps = existing_steps + [step]
        
        # Update session
        payload = {"updates": {"next_steps": updated_steps}}
        
        response = requests.patch(
            f"{SYNERGY_API_BASE}/{session_id}",
            json=payload,
            headers={"Content-Type": "application/json"},
            timeout=10
        )
        
        response.raise_for_status()
        updated_session = response.json()
        
        return {
            "success": True,
            "session_id": session_id,
            "session": updated_session,
            "message": f"✅ Added next step: {step}",
            "next_steps_count": len(updated_session.get("next_steps", []))
        }
        
    except requests.exceptions.RequestException as e:
        raise SynergyError(f"Failed to add next step to session {session_id}: {str(e)}")


def synergy_add_tag(
    session_id: str,
    tag: str,
    **kwargs
) -> Dict[str, Any]:
    """
    APPEND a single tag to existing session (preserves existing tags)
    
    Args:
        session_id: Session ID (required)
        tag: Tag to add (required)
        
    Returns:
        Updated session with new tag appended
        
    Raises:
        SynergyError: If API call fails
    """
    try:
        # Get current session
        response = requests.get(f"{SYNERGY_API_BASE}/{session_id}", timeout=10)
        response.raise_for_status()
        session = response.json()
        
        # Get existing tags
        existing_tags = session.get("tags", [])
        
        # Append new tag (avoid duplicates)
        if tag not in existing_tags:
            updated_tags = existing_tags + [tag]
        else:
            updated_tags = existing_tags
        
        # Update session
        payload = {"updates": {"tags": updated_tags}}
        
        response = requests.patch(
            f"{SYNERGY_API_BASE}/{session_id}",
            json=payload,
            headers={"Content-Type": "application/json"},
            timeout=10
        )
        
        response.raise_for_status()
        updated_session = response.json()
        
        return {
            "success": True,
            "session_id": session_id,
            "session": updated_session,
            "message": f"✅ Added tag: {tag}",
            "tag_count": len(updated_session.get("tags", []))
        }
        
    except requests.exceptions.RequestException as e:
        raise SynergyError(f"Failed to add tag to session {session_id}: {str(e)}")


def synergy_link_thread(
    session_id: str,
    thread_id: str,
    **kwargs
) -> Dict[str, Any]:
    """
    APPEND a thread ID to link conversation to session (preserves existing links)
    
    Args:
        session_id: Session ID (required)
        thread_id: Thread ID to link (required)
        
    Returns:
        Updated session with thread linked
        
    Raises:
        SynergyError: If API call fails
    """
    try:
        # Get current session
        response = requests.get(f"{SYNERGY_API_BASE}/{session_id}", timeout=10)
        response.raise_for_status()
        session = response.json()
        
        # Get existing thread IDs
        existing_threads = session.get("thread_ids", [])
        
        # Append new thread ID (avoid duplicates)
        if thread_id not in existing_threads:
            updated_threads = existing_threads + [thread_id]
        else:
            updated_threads = existing_threads
        
        # Update session
        payload = {"updates": {"thread_ids": updated_threads}}
        
        response = requests.patch(
            f"{SYNERGY_API_BASE}/{session_id}",
            json=payload,
            headers={"Content-Type": "application/json"},
            timeout=10
        )
        
        response.raise_for_status()
        updated_session = response.json()
        
        return {
            "success": True,
            "session_id": session_id,
            "session": updated_session,
            "message": f"✅ Linked thread: {thread_id}",
            "thread_count": len(updated_session.get("thread_ids", []))
        }
        
    except requests.exceptions.RequestException as e:
        raise SynergyError(f"Failed to link thread to session {session_id}: {str(e)}")


def synergy_assign_agent(
    session_id: str,
    agent_name: str,
    **kwargs
) -> Dict[str, Any]:
    """
    APPEND an AI agent to session's assigned agents (preserves existing assignments)
    
    Args:
        session_id: Session ID (required)
        agent_name: AI agent name to assign (required)
        
    Returns:
        Updated session with agent assigned
        
    Raises:
        SynergyError: If API call fails
    """
    try:
        # Get current session
        response = requests.get(f"{SYNERGY_API_BASE}/{session_id}", timeout=10)
        response.raise_for_status()
        session = response.json()
        
        # Get existing assigned agents
        existing_agents = session.get("assigned_agents", [])
        
        # Append new agent (avoid duplicates)
        if agent_name not in existing_agents:
            updated_agents = existing_agents + [agent_name]
        else:
            updated_agents = existing_agents
        
        # Update session
        payload = {"updates": {"assigned_agents": updated_agents}}
        
        response = requests.patch(
            f"{SYNERGY_API_BASE}/{session_id}",
            json=payload,
            headers={"Content-Type": "application/json"},
            timeout=10
        )
        
        response.raise_for_status()
        updated_session = response.json()
        
        return {
            "success": True,
            "session_id": session_id,
            "session": updated_session,
            "message": f"✅ Assigned agent: {agent_name}",
            "agent_count": len(updated_session.get("assigned_agents", []))
        }
        
    except requests.exceptions.RequestException as e:
        raise SynergyError(f"Failed to assign agent to session {session_id}: {str(e)}")


# ============================================================================
# EDIT TOOLS (Description, Notes, and Checklist Management)
# ============================================================================

def synergy_edit_description(
    session_id: str,
    description: str,
    **kwargs
) -> Dict[str, Any]:
    """
    UPDATE the description field (replaces existing description)
    
    Args:
        session_id: Session ID (required)
        description: New description text (required)
        
    Returns:
        Updated session with new description
        
    Raises:
        SynergyError: If API call fails
    """
    try:
        payload = {"updates": {"description": description}}
        
        response = requests.patch(
            f"{SYNERGY_API_BASE}/{session_id}",
            json=payload,
            headers={"Content-Type": "application/json"},
            timeout=10
        )
        
        response.raise_for_status()
        updated_session = response.json()
        
        return {
            "success": True,
            "session_id": session_id,
            "session": updated_session,
            "message": "✅ Description updated"
        }
        
    except requests.exceptions.RequestException as e:
        raise SynergyError(f"Failed to update description for session {session_id}: {str(e)}")


def synergy_edit_notes(
    session_id: str,
    notes: str,
    **kwargs
) -> Dict[str, Any]:
    """
    UPDATE the notes field (replaces existing notes)
    
    Args:
        session_id: Session ID (required)
        notes: New notes text (required)
        
    Returns:
        Updated session with new notes
        
    Raises:
        SynergyError: If API call fails
    """
    try:
        payload = {"updates": {"notes": notes}}
        
        response = requests.patch(
            f"{SYNERGY_API_BASE}/{session_id}",
            json=payload,
            headers={"Content-Type": "application/json"},
            timeout=10
        )
        
        response.raise_for_status()
        updated_session = response.json()
        
        return {
            "success": True,
            "session_id": session_id,
            "session": updated_session,
            "message": "✅ Notes updated"
        }
        
    except requests.exceptions.RequestException as e:
        raise SynergyError(f"Failed to update notes for session {session_id}: {str(e)}")


# ============================================================================
# CHECKLIST MANAGEMENT TOOLS
# ============================================================================

def synergy_checklist_add_item(
    session_id: str,
    text: str,
    completed: bool = False,
    parent_index: Optional[int] = None,
    **kwargs
) -> Dict[str, Any]:
    """
    ADD a new item to the checklist (preserves existing items)
    
    Args:
        session_id: Session ID (required)
        text: Checklist item text (required)
        completed: Initial completion status (default: false)
        parent_index: Parent item index for sub-items (optional)
        
    Returns:
        Updated session with new checklist item appended
        
    Raises:
        SynergyError: If API call fails
    """
    try:
        # Get current session
        response = requests.get(f"{SYNERGY_API_BASE}/{session_id}", timeout=10)
        response.raise_for_status()
        session = response.json()
        
        # Get existing checklist
        existing_checklist = session.get("checklist", [])
        
        # Create new item
        new_item = {
            "text": text,
            "completed": completed
        }
        
        # If parent_index provided, add as sub-item
        if parent_index is not None:
            if 0 <= parent_index < len(existing_checklist):
                parent_item = existing_checklist[parent_index]
                if "sub_items" not in parent_item:
                    parent_item["sub_items"] = []
                parent_item["sub_items"].append(new_item)
                updated_checklist = existing_checklist
            else:
                raise SynergyError(f"Invalid parent_index: {parent_index}")
        else:
            # Add as top-level item
            updated_checklist = existing_checklist + [new_item]
        
        # Update session
        payload = {"updates": {"checklist": updated_checklist}}
        
        response = requests.patch(
            f"{SYNERGY_API_BASE}/{session_id}",
            json=payload,
            headers={"Content-Type": "application/json"},
            timeout=10
        )
        
        response.raise_for_status()
        updated_session = response.json()
        
        return {
            "success": True,
            "session_id": session_id,
            "session": updated_session,
            "message": f"✅ Added checklist item: {text}",
            "checklist_count": len(updated_session.get("checklist", []))
        }
        
    except requests.exceptions.RequestException as e:
        raise SynergyError(f"Failed to add checklist item to session {session_id}: {str(e)}")


def synergy_checklist_edit_item(
    session_id: str,
    item_index: int,
    new_text: str,
    sub_item_index: Optional[int] = None,
    **kwargs
) -> Dict[str, Any]:
    """
    EDIT an existing checklist item's text (preserves completion status)
    
    Args:
        session_id: Session ID (required)
        item_index: Item index to edit (0-based) (required)
        new_text: New text for the item (required)
        sub_item_index: Sub-item index if editing a sub-item (optional)
        
    Returns:
        Updated session with edited checklist item
        
    Raises:
        SynergyError: If API call fails
    """
    try:
        # Get current session
        response = requests.get(f"{SYNERGY_API_BASE}/{session_id}", timeout=10)
        response.raise_for_status()
        session = response.json()
        
        # Get existing checklist
        existing_checklist = session.get("checklist", [])
        
        if not existing_checklist or item_index >= len(existing_checklist):
            raise SynergyError(f"Invalid item_index: {item_index}")
        
        # Edit the item
        if sub_item_index is not None:
            # Edit sub-item
            parent_item = existing_checklist[item_index]
            sub_items = parent_item.get("sub_items", [])
            if sub_item_index >= len(sub_items):
                raise SynergyError(f"Invalid sub_item_index: {sub_item_index}")
            sub_items[sub_item_index]["text"] = new_text
        else:
            # Edit top-level item
            existing_checklist[item_index]["text"] = new_text
        
        # Update session
        payload = {"updates": {"checklist": existing_checklist}}
        
        response = requests.patch(
            f"{SYNERGY_API_BASE}/{session_id}",
            json=payload,
            headers={"Content-Type": "application/json"},
            timeout=10
        )
        
        response.raise_for_status()
        updated_session = response.json()
        
        return {
            "success": True,
            "session_id": session_id,
            "session": updated_session,
            "message": f"✅ Edited checklist item to: {new_text}"
        }
        
    except requests.exceptions.RequestException as e:
        raise SynergyError(f"Failed to edit checklist item in session {session_id}: {str(e)}")


def synergy_checklist_toggle_item(
    session_id: str,
    item_index: int,
    sub_item_index: Optional[int] = None,
    completed: Optional[bool] = None,
    **kwargs
) -> Dict[str, Any]:
    """
    TOGGLE completion status of a checklist item (check/uncheck)
    
    Args:
        session_id: Session ID (required)
        item_index: Item index to toggle (0-based) (required)
        sub_item_index: Sub-item index if toggling a sub-item (optional)
        completed: Set specific completion state instead of toggling (optional)
        
    Returns:
        Updated session with toggled item
        
    Raises:
        SynergyError: If API call fails
    """
    try:
        # Get current session
        response = requests.get(f"{SYNERGY_API_BASE}/{session_id}", timeout=10)
        response.raise_for_status()
        session = response.json()
        
        # Get existing checklist
        existing_checklist = session.get("checklist", [])
        
        if not existing_checklist or item_index >= len(existing_checklist):
            raise SynergyError(f"Invalid item_index: {item_index}")
        
        # Toggle the item
        if sub_item_index is not None:
            # Toggle sub-item
            parent_item = existing_checklist[item_index]
            sub_items = parent_item.get("sub_items", [])
            if sub_item_index >= len(sub_items):
                raise SynergyError(f"Invalid sub_item_index: {sub_item_index}")
            
            if completed is not None:
                sub_items[sub_item_index]["completed"] = completed
            else:
                sub_items[sub_item_index]["completed"] = not sub_items[sub_item_index].get("completed", False)
            
            new_status = sub_items[sub_item_index]["completed"]
        else:
            # Toggle top-level item
            if completed is not None:
                existing_checklist[item_index]["completed"] = completed
            else:
                existing_checklist[item_index]["completed"] = not existing_checklist[item_index].get("completed", False)
            
            new_status = existing_checklist[item_index]["completed"]
        
        # Update session
        payload = {"updates": {"checklist": existing_checklist}}
        
        response = requests.patch(
            f"{SYNERGY_API_BASE}/{session_id}",
            json=payload,
            headers={"Content-Type": "application/json"},
            timeout=10
        )
        
        response.raise_for_status()
        updated_session = response.json()
        
        status_text = "✅ Marked complete" if new_status else "⬜ Marked incomplete"
        
        return {
            "success": True,
            "session_id": session_id,
            "session": updated_session,
            "message": status_text,
            "completed": new_status
        }
        
    except requests.exceptions.RequestException as e:
        raise SynergyError(f"Failed to toggle checklist item in session {session_id}: {str(e)}")


def synergy_checklist_delete_item(
    session_id: str,
    item_index: int,
    sub_item_index: Optional[int] = None,
    **kwargs
) -> Dict[str, Any]:
    """
    DELETE a checklist item completely (removes from array)
    
    Args:
        session_id: Session ID (required)
        item_index: Item index to delete (0-based) (required)
        sub_item_index: Sub-item index if deleting a sub-item (optional)
        
    Returns:
        Updated session with item removed
        
    Raises:
        SynergyError: If API call fails
    """
    try:
        # Get current session
        response = requests.get(f"{SYNERGY_API_BASE}/{session_id}", timeout=10)
        response.raise_for_status()
        session = response.json()
        
        # Get existing checklist
        existing_checklist = session.get("checklist", [])
        
        if not existing_checklist or item_index >= len(existing_checklist):
            raise SynergyError(f"Invalid item_index: {item_index}")
        
        # Delete the item
        if sub_item_index is not None:
            # Delete sub-item
            parent_item = existing_checklist[item_index]
            sub_items = parent_item.get("sub_items", [])
            if sub_item_index >= len(sub_items):
                raise SynergyError(f"Invalid sub_item_index: {sub_item_index}")
            
            deleted_text = sub_items[sub_item_index]["text"]
            del sub_items[sub_item_index]
        else:
            # Delete top-level item
            deleted_text = existing_checklist[item_index]["text"]
            del existing_checklist[item_index]
        
        # Update session
        payload = {"updates": {"checklist": existing_checklist}}
        
        response = requests.patch(
            f"{SYNERGY_API_BASE}/{session_id}",
            json=payload,
            headers={"Content-Type": "application/json"},
            timeout=10
        )
        
        response.raise_for_status()
        updated_session = response.json()
        
        return {
            "success": True,
            "session_id": session_id,
            "session": updated_session,
            "message": f"✅ Deleted checklist item: {deleted_text}",
            "checklist_count": len(updated_session.get("checklist", []))
        }
        
    except requests.exceptions.RequestException as e:
        raise SynergyError(f"Failed to delete checklist item in session {session_id}: {str(e)}")


def synergy_checklist_add_sub_item(
    session_id: str,
    parent_index: int,
    text: str,
    completed: bool = False,
    **kwargs
) -> Dict[str, Any]:
    """
    ADD a sub-item to an existing checklist item (creates nested structure)
    
    Args:
        session_id: Session ID (required)
        parent_index: Parent item index (0-based) (required)
        text: Sub-item text (required)
        completed: Initial completion status (default: false)
        
    Returns:
        Updated session with new sub-item added
        
    Raises:
        SynergyError: If API call fails
    """
    try:
        # Get current session
        response = requests.get(f"{SYNERGY_API_BASE}/{session_id}", timeout=10)
        response.raise_for_status()
        session = response.json()
        
        # Get existing checklist
        existing_checklist = session.get("checklist", [])
        
        if not existing_checklist or parent_index >= len(existing_checklist):
            raise SynergyError(f"Invalid parent_index: {parent_index}")
        
        # Add sub-item to parent
        parent_item = existing_checklist[parent_index]
        if "sub_items" not in parent_item:
            parent_item["sub_items"] = []
        
        new_sub_item = {
            "text": text,
            "completed": completed
        }
        parent_item["sub_items"].append(new_sub_item)
        
        # Update session
        payload = {"updates": {"checklist": existing_checklist}}
        
        response = requests.patch(
            f"{SYNERGY_API_BASE}/{session_id}",
            json=payload,
            headers={"Content-Type": "application/json"},
            timeout=10
        )
        
        response.raise_for_status()
        updated_session = response.json()
        
        return {
            "success": True,
            "session_id": session_id,
            "session": updated_session,
            "message": f"✅ Added sub-item: {text}",
            "parent_text": parent_item["text"]
        }
        
    except requests.exceptions.RequestException as e:
        raise SynergyError(f"Failed to add sub-item to session {session_id}: {str(e)}")

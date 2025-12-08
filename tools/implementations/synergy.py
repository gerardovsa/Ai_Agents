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
import os

# Synergy backend URL - use environment variable or default to Render deployment
SYNERGY_API_BASE = os.getenv('API_BASE_URL', 'https://ai-agents-backend-singapore.onrender.com').rstrip('/') + '/api/synergy'


class SynergyError(Exception):
    """Custom exception for Synergy API errors"""
    pass


def synergy_smart_project_tracker(
    title: str,
    platforms_involved: List[str],
    next_steps: Optional[List[str]] = None,
    description: Optional[str] = None,
    priority: str = "high",
    start_in_column: str = "in_progress",
    initial_documents: Optional[List[Dict[str, str]]] = None,
    due_date: Optional[str] = None,
    tags: Optional[List[str]] = None,
    auto_update_mode: bool = True,
    sync_to_google: bool = False,
    notify_user: bool = True,
    use_milestones: bool = False,
    initial_milestones: Optional[List[Dict[str, Any]]] = None,
    **kwargs
) -> Dict[str, Any]:
    """
    SMART TOOL: Complete multi-platform project tracking in ONE call
    
    This is your PRIMARY tool for complex multi-step projects. It:
    1. Creates Synergy session with proper structure (flat OR milestone-based)
    2. Sets up initial milestones with tasks/subtasks (if use_milestones=True)
    3. Sets up initial documents (if provided)
    4. Configures next steps checklist (if flat structure)
    5. Places in correct Kanban column
    6. Optionally syncs to Google Tasks
    7. Returns dashboard URL and session info
    
    Use this INSTEAD of calling synergy_create_session + synergy_create_milestone separately
    
    Args:
        title: Project title (required)
        platforms_involved: List of platforms ['gmail', 'sheets', 'forms', etc.]
        next_steps: Action items checklist (for flat structure) - Optional if using milestones
        description: What you're building (auto-generated if not provided)
        priority: Priority level (default: high)
        start_in_column: backlog or in_progress (default: in_progress)
        initial_documents: Documents already created [{"title": "", "url": "", "type": ""}]
        due_date: Due date ISO format
        tags: Tags for filtering
        auto_update_mode: AI updates automatically (default: true)
        sync_to_google: Also create Google Task (default: false)
        notify_user: Tell user about dashboard (default: true)
        use_milestones: Use milestone-based structure instead of flat (default: false)
        initial_milestones: List of milestones to create [{"milestone_name": "", "tasks": [], ...}]
        
    Returns:
        Dict with:
        - session_id: For future updates
        - session: Complete session object
        - dashboard_url: https://ai-agents-backend-singapore.onrender.com
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
        # "✅ Project tracker created! View dashboard: https://ai-agents-backend-singapore.onrender.com"
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
        
        if initial_milestones and isinstance(initial_milestones, str):
            try:
                initial_milestones = json.loads(initial_milestones)
            except json.JSONDecodeError:
                raise SynergyError(f"Invalid JSON for initial_milestones: {initial_milestones}")
        
        # Auto-generate description if not provided
        if not description:
            platform_str = ", ".join(platforms_involved)
            description = f"Multi-platform project involving: {platform_str}"
        
        # Auto-generate tags from platforms if not provided
        if not tags:
            tags = platforms_involved + ["multi-platform", "automation"]
        
        # Validate structure choice
        if use_milestones and initial_milestones is None:
            raise SynergyError("use_milestones=True but no initial_milestones provided. Either provide milestones or use flat structure.")
        
        if not use_milestones and next_steps is None:
            raise SynergyError("Flat structure requires next_steps. Either provide next_steps or use use_milestones=True.")
        
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
            "uses_milestones": use_milestones
        }
        
        # Add next_steps for flat structure
        if not use_milestones:
            payload["next_steps"] = next_steps
        
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
        
        # Create milestones if using milestone structure
        created_milestones = []
        if use_milestones and initial_milestones:
            for milestone_data in initial_milestones:
                try:
                    milestone_result = synergy_create_milestone(
                        session_id=session_id,
                        **milestone_data
                    )
                    created_milestones.append(milestone_result)
                except Exception as e:
                    print(f"Warning: Failed to create milestone '{milestone_data.get('milestone_name', 'Unknown')}': {str(e)}")
        
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
        dashboard_url = os.getenv('API_BASE_URL', 'https://ai-agents-backend-singapore.onrender.com').rstrip('/')
        doc_count = len(initial_documents) if initial_documents else 0
        
        message_parts = [
            f"✅ Project tracker created: {title}",
            f"📊 Dashboard: {dashboard_url}",
            f"🎯 Priority: {priority}",
            f"🔧 Platforms: {', '.join(platforms_involved)}"
        ]
        
        if use_milestones:
            milestone_count = len(created_milestones)
            # tasks_created can be int (count) or list (IDs), handle both
            total_tasks = sum(
                m.get('tasks_created', 0) if isinstance(m.get('tasks_created'), int) else len(m.get('tasks_created', []))
                for m in created_milestones
            )
            message_parts.append(f"📊 Structure: Milestone-based ({milestone_count} milestones, {total_tasks} tasks)")
        else:
            message_parts.append(f"📋 Next Steps: {len(next_steps)} action items")
        
        if doc_count > 0:
            message_parts.append(f"📄 Initial Documents: {doc_count}")
        
        if auto_update_mode:
            message_parts.append("🤖 AI will auto-update as work progresses")
        
        if google_sync_status:  # Only append if not empty string
            message_parts.append(google_sync_status)
        
        user_message = "\n".join(message_parts)
        
        result = {
            "success": True,
            "session_id": session_id,
            "session": session,
            "dashboard_url": dashboard_url,
            "message": user_message,
            "auto_update_enabled": auto_update_mode,
            "platforms": platforms_involved,
            "notify_user": notify_user,
            "uses_milestones": use_milestones
        }
        
        if use_milestones:
            result["milestones_created"] = created_milestones
            result["milestone_count"] = len(created_milestones)
        
        return result
        
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
    uses_milestones: bool = False,
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
        uses_milestones: Use milestone-based structure (default: false for flat structure)
        
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
            "uses_milestones": uses_milestones,
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


def synergy_search_sessions(
    query: Optional[str] = None,
    platform: Optional[str] = None,
    status: Optional[str] = None,
    priority: Optional[str] = None,
    column: Optional[str] = None,
    **kwargs
) -> Dict[str, Any]:
    """
    Search sessions by title, description, tags, or platform
    
    Use this tool to find specific sessions when you know keywords or platforms
    but not the exact session ID. Searches across:
    - Session title
    - Description text
    - Tags
    - Platform names
    
    Args:
        query: Search term to find in title/description/tags (optional if platform provided)
        platform: Filter by specific platform (gmail, sheets, docs, etc.)
        status: Filter by status (active|completed|archived)
        priority: Filter by priority (low|medium|high|critical)
        column: Filter by Kanban column (backlog|in_progress|review|done)
        
    Returns:
        Dict with:
        - success: bool
        - count: int (number of matches)
        - sessions: List[Dict] (matching sessions)
        - query: str (search term used)
        - filters_applied: Dict (filters that were active)
        
    Raises:
        SynergyError: If API call fails
        
    Examples:
        # Search for email-related projects
        synergy_search_sessions(query="email automation")
        
        # Find all Gmail projects
        synergy_search_sessions(platform="gmail")
        
        # Search with filters
        synergy_search_sessions(
            query="dashboard",
            priority="high",
            column="in_progress"
        )
    """
    try:
        if not query and not platform:
            raise SynergyError("Either query or platform parameter is required")
        
        params = {}
        if query:
            params["query"] = query
        if platform:
            params["platform"] = platform
        if status:
            params["status"] = status
        if priority:
            params["priority"] = priority
        if column:
            params["column"] = column
        
        response = requests.get(
            f"{SYNERGY_API_BASE}/search",
            params=params,
            timeout=10
        )
        
        response.raise_for_status()
        result = response.json()
        
        return {
            "success": True,
            "count": result.get("count", 0),
            "sessions": result.get("sessions", []),
            "query": query,
            "filters_applied": result.get("filters_applied", {})
        }
        
    except requests.exceptions.RequestException as e:
        raise SynergyError(f"Failed to search sessions: {str(e)}")


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
        # MILESTONE AWARENESS: Check if session uses milestones
        # Fetch current session to check structure
        session_response = requests.get(
            f"{SYNERGY_API_BASE}/{session_id}",
            timeout=10
        )
        session_response.raise_for_status()
        current_session = session_response.json()
        uses_milestones = current_session.get('uses_milestones', False)
        
        # Validate: Don't allow flat structure updates on milestone sessions
        if uses_milestones and (next_steps is not None or checklist is not None):
            raise SynergyError(
                f"Session {session_id} uses MILESTONE structure. "
                f"Cannot update 'next_steps' or 'checklist' on milestone sessions. "
                f"Use synergy_create_milestone(), synergy_update_milestone(), synergy_create_task(), etc. instead. "
                f"To learn about milestone operations, call: synergy_agent_instructions(topic='milestones')"
            )
        
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


def synergy_update_session_permissions(
    session_id: str,
    user_id: int,
    permission_level: Optional[str] = None,
    shared_with_users: Optional[List[int]] = None,
    allow_public_view: Optional[bool] = None,
    **kwargs
) -> Dict[str, Any]:
    """
    Update permission settings for a Synergy session (owner-only operation)
    
    This tool controls who can access and edit a session. Four permission levels:
    
    1. 'private' (default): Owner-only access (most secure)
    2. 'shared': Owner + specified users can edit
    3. 'public_view': Anyone can view, only owner can edit
    4. 'public_edit': Anyone can view and edit (least secure)
    
    SECURITY NOTES:
    - Only session OWNER can change permissions
    - Owner always has full access regardless of permission_level
    - Changing to 'private' clears shared_with_users automatically
    - public_edit allows ANYONE to modify - use with caution
    
    Args:
        session_id: Session ID to update permissions for (required)
        user_id: User ID of person making change (for ownership verification - required)
        permission_level: New permission level (optional):
            - 'private': Owner only
            - 'shared': Owner + specified users
            - 'public_view': Public read, owner edit
            - 'public_edit': Public read/write
        shared_with_users: Array of user IDs to share with (optional, only for 'shared' level)
            Pass empty array [] to remove all shared users
        allow_public_view: Enable public link sharing (optional, for public levels)
        
    Returns:
        Dict with success status, updated permissions, and confirmation message
        
    Raises:
        SynergyError: If API call fails or user is not owner
        
    Examples:
        # Make session private (remove all sharing)
        synergy_update_session_permissions(
            session_id="sess_123",
            user_id=1,
            permission_level="private",
            shared_with_users=[]
        )
        
        # Share with team members
        synergy_update_session_permissions(
            session_id="sess_123",
            user_id=1,
            permission_level="shared",
            shared_with_users=[2, 5, 8, 12]
        )
        
        # Make publicly viewable (portfolio)
        synergy_update_session_permissions(
            session_id="sess_123",
            user_id=1,
            permission_level="public_view",
            allow_public_view=True
        )
        
        # Open for community editing
        synergy_update_session_permissions(
            session_id="sess_123",
            user_id=1,
            permission_level="public_edit",
            allow_public_view=True
        )
    """
    try:
        # Build permission updates dict from provided parameters
        permission_updates = {}
        
        if permission_level is not None:
            # Validate permission level
            valid_levels = ['private', 'shared', 'public_view', 'public_edit']
            if permission_level not in valid_levels:
                raise SynergyError(
                    f"Invalid permission_level '{permission_level}'. "
                    f"Must be one of: {', '.join(valid_levels)}"
                )
            permission_updates["permission_level"] = permission_level
        
        if shared_with_users is not None:
            # Parse JSON string if needed
            if isinstance(shared_with_users, str):
                try:
                    shared_with_users = json.loads(shared_with_users)
                except json.JSONDecodeError:
                    raise SynergyError(f"Invalid JSON for shared_with_users parameter: {shared_with_users}")
            
            # Validate it's a list of integers
            if not isinstance(shared_with_users, list):
                raise SynergyError(f"shared_with_users must be an array of user IDs")
            
            for uid in shared_with_users:
                if not isinstance(uid, int):
                    raise SynergyError(f"shared_with_users must contain only integers (user IDs), got: {uid}")
            
            permission_updates["shared_with_users"] = shared_with_users
        
        if allow_public_view is not None:
            permission_updates["allow_public_view"] = allow_public_view
        
        # Build payload
        payload = {
            "user_id": user_id,
            "permission_updates": permission_updates
        }
        
        # Make API call to permission update endpoint
        response = requests.patch(
            f"{SYNERGY_API_BASE}/{session_id}/permissions",
            json=payload,
            headers={"Content-Type": "application/json"},
            timeout=10
        )
        
        response.raise_for_status()
        result = response.json()
        
        # Build user-friendly message
        permission_summary = []
        
        if permission_level:
            level_names = {
                'private': '🔒 Private (owner only)',
                'shared': '👥 Shared (team collaboration)',
                'public_view': '👁️ Public View (read-only)',
                'public_edit': '🌍 Public Edit (open collaboration)'
            }
            permission_summary.append(level_names.get(permission_level, permission_level))
        
        if shared_with_users is not None:
            user_count = len(shared_with_users)
            if user_count > 0:
                permission_summary.append(f"Shared with {user_count} user(s)")
            else:
                permission_summary.append("Sharing removed")
        
        if allow_public_view is not None:
            permission_summary.append(f"Public link: {'enabled' if allow_public_view else 'disabled'}")
        
        summary_str = ", ".join(permission_summary) if permission_summary else "permissions updated"
        
        return {
            "success": True,
            "session_id": session_id,
            "message": f"✅ Updated permissions: {summary_str}",
            "updated_permissions": result.get("updated_permissions", permission_updates),
            "result": result
        }
        
    except requests.exceptions.HTTPError as e:
        if e.response.status_code == 403:
            raise SynergyError(
                f"Permission denied: Only the session owner can change permissions. "
                f"User {user_id} is not the owner of session {session_id}."
            )
        raise SynergyError(f"Failed to update permissions for session {session_id}: {str(e)}")
    except requests.exceptions.RequestException as e:
        raise SynergyError(f"Failed to update permissions for session {session_id}: {str(e)}")


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


# ============================================================
# INTERNAL DOCUMENTS
# ============================================================

def synergy_create_internal_doc(
    session_id: str,
    title: str,
    content: str,
    format: str = "markdown",
    linked_milestone_id: Optional[str] = None,
    **kwargs
) -> Dict[str, Any]:
    """
    Create an internal document within a Synergy session
    
    This stores long-form content (meeting notes, drafts, summaries) directly
    in the Synergy database without requiring external Drive/OneDrive.
    
    Content is stored as MARKDOWN for AI-friendly processing. The document will
    appear in the session's Documents section. Users can click to open an editor
    modal where they can:
    - Edit content with live markdown preview
    - Export to Word/Google Docs/PDF/Email
    - Copy doc_id for AI processing
    
    NEW: Can be linked to a specific milestone using linked_milestone_id parameter.
    This allows you to organize documents by project phase and see which documents
    belong to which milestone.
    
    Args:
        session_id: Synergy session ID (format: sess_YYYYMMDD_HHMM_title)
        title: Document title (e.g., 'Meeting Summary', 'Q4 Strategy')
        content: Document content in MARKDOWN format. Supports:
                 - **bold**, *italic*
                 - # headers (H1), ## (H2), etc.
                 - - bullet lists
                 - - [ ] checklists
                 - Links, code blocks, etc.
        format: Content format (default: 'markdown'). Can be 'html' but markdown
                is preferred for AI editability
        linked_milestone_id: Optional milestone ID to link this document to.
                            Use when document is specific to a project phase.
                            Format: ms_20251124120000
                            Example: Link "Phase 1 Summary" to milestone 1
        **kwargs: Additional parameters (e.g., _user_id)
    
    Returns:
        Dict with:
        - success: bool
        - doc_id: str (format: int_doc_<timestamp>) - SAVE THIS for later retrieval
        - title: str
        - preview: str (first 100 chars of content)
        - message: str
        
    Example:
        result = synergy_create_internal_doc(
            session_id='sess_20251114_1200_project_alpha',
            title='Meeting Summary - Nov 14',
            content='''# Meeting Summary
            
## Attendees
- John Smith
- Sarah Johnson

## Key Decisions
1. **Budget Approved** - $50K for Q1
2. **Timeline Set** - Launch by March 15

## Action Items
- [ ] John: Draft project proposal
- [ ] Sarah: Schedule follow-up meeting

## Next Steps
Review proposal next week.'''
        )
        
        # Returns: {"success": True, "doc_id": "int_doc_1731600000123", ...}
        # User can paste "int_doc_1731600000123" in chat for AI to read it
    """
    try:
        payload = {
            'session_id': session_id,
            'title': title,
            'content': content,
            'format': format,
            'created_by': kwargs.get('_user_id', 'ai_agent')
        }
        
        # Add linked_milestone_id if provided
        if linked_milestone_id:
            payload['linked_milestone_id'] = linked_milestone_id
        
        response = requests.post(
            f'{SYNERGY_API_BASE}/internal-doc/create',
            json=payload
        )
        
        response.raise_for_status()
        data = response.json()
        
        link_msg = f" (linked to milestone)" if linked_milestone_id else ""
        
        return {
            'success': True,
            'doc_id': data.get('doc_id'),
            'title': data.get('title'),
            'preview': data.get('preview', content[:100]),
            'linked_milestone_id': linked_milestone_id,
            'message': f"✅ Created internal document: {title}{link_msg}. Doc ID: {data.get('doc_id')} (user can paste in chat for AI to read)"
        }
        
    except requests.exceptions.RequestException as e:
        raise SynergyError(f"Failed to create internal document: {str(e)}")


def synergy_update_internal_doc(
    doc_id: str,
    content: Optional[str] = None,
    title: Optional[str] = None,
    **kwargs
) -> Dict[str, Any]:
    """
    Update an existing internal document's content or title
    
    This increments the version number for tracking changes. Use when user
    requests modifications to an existing internal document.
    
    Args:
        doc_id: Internal document ID (format: int_doc_<timestamp>)
        content: Updated content in markdown (optional)
        title: Updated title (optional)
        **kwargs: Additional parameters
    
    Returns:
        Dict with success status, updated version, and message
        
    Example:
        result = synergy_update_internal_doc(
            doc_id='int_doc_1731600000123',
            content='# Updated Summary\n\nNew content here...'
        )
    """
    try:
        updates = {}
        if content is not None:
            updates['content'] = content
        if title is not None:
            updates['title'] = title
            
        if not updates:
            return {
                'success': False,
                'error': 'No updates provided (need content or title)'
            }
        
        response = requests.put(
            f'{SYNERGY_API_BASE}/internal-doc/{doc_id}',
            json=updates
        )
        
        response.raise_for_status()
        data = response.json()
        
        return {
            'success': True,
            'doc_id': doc_id,
            'version': data.get('version'),
            'message': f"✅ Updated internal document (version {data.get('version')})"
        }
        
    except requests.exceptions.RequestException as e:
        raise SynergyError(f"Failed to update internal document {doc_id}: {str(e)}")


def synergy_get_internal_doc(
    doc_id: str,
    **kwargs
) -> Dict[str, Any]:
    """
    Retrieve the full content of an internal document
    
    Use this when user pastes a doc_id in chat and asks you to read,
    summarize, or process the document.
    
    Args:
        doc_id: Internal document ID (format: int_doc_<timestamp>)
        **kwargs: Additional parameters
    
    Returns:
        Dict with:
        - success: bool
        - doc_id: str
        - session_id: str
        - title: str
        - content: str (complete markdown content, HTML stripped)
        - content_html: str (original HTML content)
        - format: str
        - version: int
        - created_at: str
        - updated_at: str
        - created_by: str
        
    Example:
        # User pastes in chat: "Summarize int_doc_1731600000123"
        doc = synergy_get_internal_doc(doc_id='int_doc_1731600000123')
        # Now you can read doc['content'] and provide summary
    """
    try:
        import re
        import json
        
        response = requests.get(f'{SYNERGY_API_BASE}/internal-doc/{doc_id}')
        response.raise_for_status()
        data = response.json()
        
        doc_type = data.get('doc_type', 'richtext')
        
        # For spreadsheets, use structured JSON data
        if doc_type == 'spreadsheet':
            content_json = data.get('content_json', '[]')
            try:
                spreadsheet_data = json.loads(content_json) if isinstance(content_json, str) else content_json
                # Format spreadsheet as readable text for AI
                clean_content = f"Spreadsheet: {data.get('title')}\n\n"
                if isinstance(spreadsheet_data, list) and len(spreadsheet_data) > 0:
                    # First row as headers
                    headers = spreadsheet_data[0] if len(spreadsheet_data) > 0 else []
                    clean_content += "Columns: " + " | ".join(str(h) for h in headers) + "\n\n"
                    # Data rows
                    for row_idx, row in enumerate(spreadsheet_data[1:], 1):
                        clean_content += f"Row {row_idx}: " + " | ".join(str(cell) for cell in row) + "\n"
                else:
                    clean_content += "Empty spreadsheet"
            except json.JSONDecodeError:
                clean_content = "Spreadsheet data format error"
        else:
            # For richtext documents, strip HTML to get clean text
            raw_content = data.get('content', '')
            clean_content = re.sub(r'<[^>]+>', '', raw_content)
            clean_content = clean_content.strip()
            
            # Replace multiple whitespace with single space
            clean_content = re.sub(r'\s+', ' ', clean_content)
            
            # Replace common HTML entities
            clean_content = clean_content.replace('&nbsp;', ' ')
            clean_content = clean_content.replace('&amp;', '&')
            clean_content = clean_content.replace('&lt;', '<')
            clean_content = clean_content.replace('&gt;', '>')
            clean_content = clean_content.replace('&quot;', '"')
        
        return {
            'success': True,
            'doc_id': data.get('doc_id'),
            'session_id': data.get('session_id'),
            'title': data.get('title'),
            'doc_type': doc_type,
            'content': clean_content,  # Clean text for AI (parsed based on doc_type)
            'content_html': data.get('content', ''),  # Original HTML (for richtext)
            'content_json': data.get('content_json', ''),  # Structured data (for spreadsheet)
            'format': data.get('format'),
            'version': data.get('version'),
            'created_at': data.get('created_at'),
            'updated_at': data.get('updated_at'),
            'created_by': data.get('created_by')
        }
        
    except requests.exceptions.RequestException as e:
        if 'Not Found' in str(e) or '404' in str(e):
            raise SynergyError(f"Internal document {doc_id} not found")
        raise SynergyError(f"Failed to get internal document {doc_id}: {str(e)}")


def synergy_export_internal_doc(
    doc_id: str,
    export_format: str,
    email_to: Optional[str] = None,
    email_subject: Optional[str] = None,
    **kwargs
) -> Dict[str, Any]:
    """
    Export an internal document to various formats
    
    Converts markdown content to formatted output and exports to:
    - 'word': Creates .docx file in OneDrive
    - 'google_doc': Creates Google Doc in Drive
    - 'pdf': Creates Word doc then converts to PDF
    - 'email': Sends document content via Gmail
    
    User must have OAuth credentials configured for the target platform.
    
    Args:
        doc_id: Internal document ID to export
        export_format: 'word', 'google_doc', 'pdf', or 'email'
        email_to: Recipient email (required for 'email' format)
        email_subject: Email subject (optional, for 'email' format)
        **kwargs: Additional parameters (includes _user_id for OAuth)
    
    Returns:
        Dict with:
        - success: bool
        - url: str (for word/google_doc - opens in browser)
        - file_id: str (for OneDrive)
        - document_id: str (for Google Docs)
        - message: str (for email confirmation)
        - format: str
        
    Example:
        # Export to Word
        result = synergy_export_internal_doc(
            doc_id='int_doc_1731600000123',
            export_format='word'
        )
        # Returns: {"success": True, "url": "https://onedrive.live.com/...", ...}
        
        # Send via email
        result = synergy_export_internal_doc(
            doc_id='int_doc_1731600000123',
            export_format='email',
            email_to='user@example.com',
            email_subject='Meeting Summary - Nov 14'
        )
    """
    try:
        if export_format == 'email' and not email_to:
            return {
                'success': False,
                'error': 'email_to is required for email export format'
            }
        
        payload = {}
        if email_to:
            payload['to'] = email_to
        if email_subject:
            payload['subject'] = email_subject
            
        # Add user_id header for OAuth credential injection
        headers = {}
        if kwargs.get('_user_id'):
            headers['X-User-ID'] = str(kwargs.get('_user_id'))
        
        response = requests.post(
            f'{SYNERGY_API_BASE}/internal-doc/{doc_id}/export/{export_format}',
            json=payload,
            headers=headers
        )
        
        response.raise_for_status()
        data = response.json()
        
        format_names = {
            'word': 'Word document',
            'google_doc': 'Google Doc',
            'pdf': 'PDF',
            'email': 'email'
        }
        
        return {
            'success': True,
            'doc_id': doc_id,
            'format': export_format,
            'url': data.get('url'),
            'file_id': data.get('file_id'),
            'document_id': data.get('document_id'),
            'message': data.get('message') or f"✅ Exported as {format_names.get(export_format, export_format)}"
        }
        
    except requests.exceptions.RequestException as e:
        if 'Permission denied' in str(e):
            raise SynergyError(f"Export failed: User needs to configure {export_format} OAuth credentials")
        raise SynergyError(f"Failed to export internal document {doc_id}: {str(e)}")


# ============================================================================
# MILESTONE-BASED PROJECT MANAGEMENT
# ============================================================================

def synergy_create_milestone(
    session_id: str,
    milestone_name: str,
    description: Optional[str] = None,
    tasks: Optional[List[Any]] = None,
    due_date: Optional[str] = None,
    priority: str = "medium",
    estimated_hours: Optional[float] = None,
    documents: Optional[List[Dict[str, str]]] = None,
    links: Optional[List[Dict[str, str]]] = None,
    tags: Optional[List[str]] = None,
    start_date: Optional[str] = None,
    depends_on_milestone_id: Optional[str] = None,
    color_hex: Optional[str] = None,
    **kwargs
) -> Dict[str, Any]:
    """
    Create a new milestone with tasks and subtasks in one call
    
    Milestones are major phases in a Synergy session. Each milestone can have:
    - Multiple tasks (smaller units of work)
    - Each task can have subtasks (granular steps)
    - Documents specific to this milestone
    - Links and tags for organization
    - Priority, due dates, time estimates
    - Dependencies on other milestones
    
    Use this when you have a structured project with clear phases like:
    - "Phase 1: Planning", "Phase 2: Development", "Phase 3: Testing"
    - "Database Setup", "API Integration", "UI Development"
    
    Args:
        session_id: Synergy session ID (required)
        milestone_name: Milestone title (required)
        description: Detailed milestone description
        tasks: List of tasks - can be strings or objects with subtasks
               Examples:
               - ["Create database", "Import data"]
               - [{"task": "Setup infrastructure", "subtasks": ["Create server", "Configure DNS"]}]
        due_date: Due date in ISO format (YYYY-MM-DD)
        priority: Priority level (low|medium|high|critical) - default: medium
        estimated_hours: Estimated hours to complete milestone
        documents: Documents specific to this milestone
                   Format: [{"title": "Design Doc", "url": "https://...", "type": "google_doc"}]
        links: Related links
               Format: [{"title": "Dashboard", "url": "https://..."}]
        tags: Tags for categorization (e.g., ["backend", "database", "critical"])
        start_date: Start date in ISO format (YYYY-MM-DD)
        depends_on_milestone_id: ID of milestone that must complete first
        color_hex: Color for visual identification (e.g., "#FF5733")
        
    Returns:
        Dict with:
        - success: bool
        - milestone_id: str (save this for updates!)
        - milestone_number: int (auto-incremented)
        - tasks_created: int
        - subtasks_created: int
        - message: str
        
    Example:
        result = synergy_create_milestone(
            session_id="sess_abc123",
            milestone_name="Database Setup",
            description="Set up customer database and import existing contacts",
            tasks=[
                "Create Google Sheet for customer data",
                {
                    "task": "Import existing contacts",
                    "subtasks": [
                        "Export from old CRM",
                        "Clean and format data",
                        "Import to new sheet"
                    ]
                },
                "Set up automated backups"
            ],
            due_date="2025-12-01",
            priority="high",
            estimated_hours=8,
            tags=["database", "migration", "critical"]
        )
        
        milestone_id = result["milestone_id"]  # Save this!
    """
    try:
        payload = {
            "session_id": session_id,
            "milestone_name": milestone_name,
            "description": description,
            "tasks": tasks or [],
            "due_date": due_date,
            "priority": priority,
            "estimated_hours": estimated_hours
        }
        
        # Add optional fields if provided
        if documents:
            payload["documents"] = documents
        if links:
            payload["links"] = links
        if tags:
            payload["tags"] = tags
        if start_date:
            payload["start_date"] = start_date
        if depends_on_milestone_id:
            payload["depends_on_milestone_id"] = depends_on_milestone_id
        if color_hex:
            payload["color_hex"] = color_hex
        
        response = requests.post(
            f"{SYNERGY_API_BASE}/milestone/create",
            json=payload,
            headers={"Content-Type": "application/json"},
            timeout=10
        )
        
        response.raise_for_status()
        result = response.json()
        
        return {
            "success": True,
            "milestone_id": result.get("milestone_id"),
            "milestone_number": result.get("milestone_number"),
            "tasks_created": result.get("tasks_created", 0),
            "subtasks_created": result.get("subtasks_created", 0),
            "message": f"✅ Created milestone: {milestone_name} (#{result.get('milestone_number')})"
        }
        
    except requests.exceptions.RequestException as e:
        raise SynergyError(f"Failed to create milestone: {str(e)}")


def synergy_get_milestones(
    session_id: str,
    include_archived: bool = False,
    **kwargs
) -> Dict[str, Any]:
    """
    Get all milestones for a Synergy session
    
    Returns complete milestone data including:
    - All milestone fields (name, description, dates, priority, etc.)
    - Counts of tasks and subtasks
    - Completion status and progress
    - Documents and links attached to each milestone
    
    Args:
        session_id: Synergy session ID
        include_archived: Include archived milestones (default: False)
        
    Returns:
        Dict with:
        - success: bool
        - count: int (number of milestones)
        - milestones: List of milestone objects
        - session_uses_milestones: bool
        
    Example:
        result = synergy_get_milestones(session_id="sess_abc123")
        
        for milestone in result["milestones"]:
            print(f"{milestone['milestone_number']}. {milestone['milestone_name']}")
            print(f"   Tasks: {milestone['task_count']}")
            print(f"   Status: {'✅ Done' if milestone['completed'] else '⏳ In Progress'}")
    """
    try:
        params = {"include_archived": "true" if include_archived else "false"}
        
        response = requests.get(
            f"{SYNERGY_API_BASE}/{session_id}/milestones",
            params=params,
            timeout=10
        )
        
        response.raise_for_status()
        data = response.json()
        
        return {
            "success": True,
            "count": len(data.get("milestones", [])),
            "milestones": data.get("milestones", []),
            "session_uses_milestones": data.get("uses_milestones", False)
        }
        
    except requests.exceptions.RequestException as e:
        raise SynergyError(f"Failed to get milestones for session {session_id}: {str(e)}")


def synergy_update_milestone(
    milestone_id: str,
    milestone_name: Optional[str] = None,
    description: Optional[str] = None,
    priority: Optional[str] = None,
    due_date: Optional[str] = None,
    start_date: Optional[str] = None,
    estimated_hours: Optional[float] = None,
    actual_hours: Optional[float] = None,
    completed: Optional[bool] = None,
    blocked: Optional[bool] = None,
    blocker_reason: Optional[str] = None,
    documents: Optional[List[Dict[str, str]]] = None,
    links: Optional[List[Dict[str, str]]] = None,
    tags: Optional[List[str]] = None,
    archived: Optional[bool] = None,
    depends_on_milestone_id: Optional[str] = None,
    color_hex: Optional[str] = None,
    **kwargs
) -> Dict[str, Any]:
    """
    Update any field(s) of an existing milestone
    
    CRITICAL: Only pass the fields you want to UPDATE. Omitted fields remain unchanged.
    
    For arrays (documents, links, tags): These REPLACE the entire array.
    To add items, you must:
    1. Get current milestone data
    2. Append new items to existing array
    3. Pass complete array to this function
    
    Args:
        milestone_id: Milestone ID to update (required)
        milestone_name: Update milestone title
        description: Update description
        priority: Update priority (low|medium|high|critical)
        due_date: Update due date (YYYY-MM-DD)
        start_date: Update start date (YYYY-MM-DD)
        estimated_hours: Update time estimate
        actual_hours: Update actual time spent
        completed: Mark as complete (true) or incomplete (false)
        blocked: Mark as blocked (true) or unblocked (false)
        blocker_reason: Reason for block (required if blocked=true)
        documents: REPLACE all documents
                   Format: [{"title": "Doc", "url": "https://...", "type": "google_doc"}]
        links: REPLACE all links
               Format: [{"title": "Link", "url": "https://..."}]
        tags: REPLACE all tags
              Format: ["tag1", "tag2"]
        archived: Archive milestone (true) or unarchive (false)
        depends_on_milestone_id: Update dependency milestone ID
        color_hex: Update color (e.g., "#FF5733")
        
    Returns:
        Dict with:
        - success: bool
        - milestone_id: str
        - updated_fields: list of field names updated
        - message: str
        
    Example:
        # Mark milestone as complete
        synergy_update_milestone(
            milestone_id="ms_20251124120000",
            completed=True,
            actual_hours=6.5
        )
        
        # Add a document (must include existing docs)
        current = synergy_get_milestones(session_id="sess_abc")
        milestone = [m for m in current["milestones"] if m["milestone_id"] == "ms_20251124120000"][0]
        existing_docs = milestone.get("documents", [])
        
        synergy_update_milestone(
            milestone_id="ms_20251124120000",
            documents=existing_docs + [{"title": "New Doc", "url": "https://...", "type": "pdf"}]
        )
    """
    try:
        updates = {}
        
        # Simple field updates
        if milestone_name is not None:
            updates["milestone_name"] = milestone_name
        if description is not None:
            updates["description"] = description
        if priority is not None:
            updates["priority"] = priority
        if due_date is not None:
            updates["due_date"] = due_date
        if start_date is not None:
            updates["start_date"] = start_date
        if estimated_hours is not None:
            updates["estimated_hours"] = estimated_hours
        if actual_hours is not None:
            updates["actual_hours"] = actual_hours
        if completed is not None:
            updates["completed"] = completed
        if blocked is not None:
            updates["blocked"] = blocked
        if blocker_reason is not None:
            updates["blocker_reason"] = blocker_reason
        if archived is not None:
            updates["archived"] = archived
        if depends_on_milestone_id is not None:
            updates["depends_on_milestone_id"] = depends_on_milestone_id
        if color_hex is not None:
            updates["color_hex"] = color_hex
        
        # Array fields (REPLACE entire array)
        if documents is not None:
            response = requests.patch(
                f"{SYNERGY_API_BASE}/milestone/{milestone_id}/documents",
                json={"documents": documents},
                headers={"Content-Type": "application/json"},
                timeout=10
            )
            response.raise_for_status()
            updates["documents"] = len(documents)
        
        if links is not None:
            response = requests.patch(
                f"{SYNERGY_API_BASE}/milestone/{milestone_id}/links",
                json={"links": links},
                headers={"Content-Type": "application/json"},
                timeout=10
            )
            response.raise_for_status()
            updates["links"] = len(links)
        
        if tags is not None:
            updates["tags"] = tags
        
        # Send simple field updates
        if len(updates) > 0:
            response = requests.patch(
                f"{SYNERGY_API_BASE}/milestone/{milestone_id}/update",
                json=updates,
                headers={"Content-Type": "application/json"},
                timeout=10
            )
            response.raise_for_status()
        
        return {
            "success": True,
            "milestone_id": milestone_id,
            "updated_fields": list(updates.keys()),
            "message": f"✅ Updated milestone ({len(updates)} fields)"
        }
        
    except requests.exceptions.RequestException as e:
        raise SynergyError(f"Failed to update milestone {milestone_id}: {str(e)}")


def synergy_create_task(
    milestone_id: str,
    task: str,
    subtasks: Optional[List[str]] = None,
    priority: str = "medium",
    estimated_hours: Optional[float] = None,
    assigned_to: Optional[str] = None,
    tags: Optional[List[str]] = None,
    start_date: Optional[str] = None,
    depends_on_task_id: Optional[str] = None,
    links: Optional[List[Dict[str, str]]] = None,
    **kwargs
) -> Dict[str, Any]:
    """
    Add a new task to an existing milestone
    
    Tasks are units of work within a milestone. Each task can have:
    - Subtasks (smaller steps)
    - Priority, time estimates, assignments
    - Dependencies on other tasks
    - Links and tags
    
    Args:
        milestone_id: Parent milestone ID (required)
        task: Task description (required)
        subtasks: List of subtask descriptions
                  Example: ["Step 1", "Step 2", "Step 3"]
        priority: Priority level (low|medium|high|critical) - default: medium
        estimated_hours: Estimated time to complete
        assigned_to: Person assigned to this task
        tags: Tags for categorization
        start_date: Start date (YYYY-MM-DD)
        depends_on_task_id: ID of task that must complete first
        links: Related links
               Format: [{"title": "Reference", "url": "https://..."}]
        
    Returns:
        Dict with:
        - success: bool
        - task_id: str (save this for updates!)
        - subtasks_created: int
        - message: str
        
    Example:
        result = synergy_create_task(
            milestone_id="ms_20251124120000",
            task="Set up database backups",
            subtasks=[
                "Configure automated daily backups",
                "Test restore procedure",
                "Document backup process"
            ],
            priority="high",
            estimated_hours=2,
            assigned_to="DevOps Team"
        )
        
        task_id = result["task_id"]  # Save this!
    """
    try:
        payload = {
            "task": task,
            "subtasks": subtasks or [],
            "priority": priority
        }
        
        # Add optional fields
        if estimated_hours is not None:
            payload["estimated_hours"] = estimated_hours
        if assigned_to:
            payload["assigned_to"] = assigned_to
        if tags:
            payload["tags"] = tags
        if start_date:
            payload["start_date"] = start_date
        if depends_on_task_id:
            payload["depends_on_task_id"] = depends_on_task_id
        if links:
            payload["links"] = links
        
        response = requests.post(
            f"{SYNERGY_API_BASE}/milestone/{milestone_id}/task/create",
            json=payload,
            headers={"Content-Type": "application/json"},
            timeout=10
        )
        
        response.raise_for_status()
        result = response.json()
        
        return {
            "success": True,
            "task_id": result.get("task_id"),
            "subtasks_created": result.get("subtasks_created", 0),
            "message": f"✅ Created task: {task[:50]}..."
        }
        
    except requests.exceptions.RequestException as e:
        raise SynergyError(f"Failed to create task: {str(e)}")


def synergy_update_task(
    task_id: str,
    task: Optional[str] = None,
    priority: Optional[str] = None,
    completed: Optional[bool] = None,
    blocked: Optional[bool] = None,
    blocker_reason: Optional[str] = None,
    estimated_hours: Optional[float] = None,
    actual_hours: Optional[float] = None,
    assigned_to: Optional[str] = None,
    tags: Optional[List[str]] = None,
    start_date: Optional[str] = None,
    archived: Optional[bool] = None,
    depends_on_task_id: Optional[str] = None,
    links: Optional[List[Dict[str, str]]] = None,
    **kwargs
) -> Dict[str, Any]:
    """
    Update any field(s) of an existing task
    
    CRITICAL: Only pass fields you want to UPDATE. Omitted fields remain unchanged.
    
    Args:
        task_id: Task ID to update (required)
        task: Update task description
        priority: Update priority (low|medium|high|critical)
        completed: Mark as complete (true) or incomplete (false)
        blocked: Mark as blocked (true) or unblocked (false)
        blocker_reason: Reason for block
        estimated_hours: Update time estimate
        actual_hours: Update actual time spent
        assigned_to: Update assignee
        tags: REPLACE all tags
        start_date: Update start date (YYYY-MM-DD)
        archived: Archive task (true) or unarchive (false)
        depends_on_task_id: Update dependency task ID
        links: REPLACE all links
        
    Returns:
        Dict with:
        - success: bool
        - task_id: str
        - updated_fields: list
        - message: str
        
    Example:
        # Mark task as complete
        synergy_update_task(
            task_id="task_20251124120000",
            completed=True,
            actual_hours=2.5
        )
        
        # Block task with reason
        synergy_update_task(
            task_id="task_20251124120000",
            blocked=True,
            blocker_reason="Waiting for API credentials"
        )
    """
    try:
        updates = {}
        
        if task is not None:
            updates["task"] = task
        if priority is not None:
            updates["priority"] = priority
        if completed is not None:
            updates["completed"] = completed
        if blocked is not None:
            updates["blocked"] = blocked
        if blocker_reason is not None:
            updates["blocker_reason"] = blocker_reason
        if estimated_hours is not None:
            updates["estimated_hours"] = estimated_hours
        if actual_hours is not None:
            updates["actual_hours"] = actual_hours
        if assigned_to is not None:
            updates["assigned_to"] = assigned_to
        if tags is not None:
            updates["tags"] = tags
        if start_date is not None:
            updates["start_date"] = start_date
        if archived is not None:
            updates["archived"] = archived
        if depends_on_task_id is not None:
            updates["depends_on_task_id"] = depends_on_task_id
        if links is not None:
            updates["links"] = links
        
        response = requests.patch(
            f"{SYNERGY_API_BASE}/task/{task_id}",
            json=updates,
            headers={"Content-Type": "application/json"},
            timeout=10
        )
        
        response.raise_for_status()
        
        return {
            "success": True,
            "task_id": task_id,
            "updated_fields": list(updates.keys()),
            "message": f"✅ Updated task ({len(updates)} fields)"
        }
        
    except requests.exceptions.RequestException as e:
        raise SynergyError(f"Failed to update task {task_id}: {str(e)}")


def synergy_create_subtask(
    task_id: str,
    task: str,
    priority: str = "medium",
    estimated_hours: Optional[float] = None,
    assigned_to: Optional[str] = None,
    tags: Optional[List[str]] = None,
    **kwargs
) -> Dict[str, Any]:
    """
    Add a new subtask to an existing task
    
    Subtasks are granular steps within a task. Use them for:
    - Breaking down complex tasks into smaller steps
    - Tracking detailed progress
    - Assigning specific steps to individuals
    
    Args:
        task_id: Parent task ID (required)
        task: Subtask description (required)
        priority: Priority level (low|medium|high|critical) - default: medium
        estimated_hours: Estimated time
        assigned_to: Person assigned
        tags: Tags for categorization
        
    Returns:
        Dict with:
        - success: bool
        - subtask_id: str
        - message: str
        
    Example:
        result = synergy_create_subtask(
            task_id="task_20251124120000",
            task="Review and approve backup configuration",
            priority="high",
            assigned_to="Team Lead"
        )
        
        subtask_id = result["subtask_id"]
    """
    try:
        payload = {
            "task": task,
            "priority": priority
        }
        
        if estimated_hours is not None:
            payload["estimated_hours"] = estimated_hours
        if assigned_to:
            payload["assigned_to"] = assigned_to
        if tags:
            payload["tags"] = tags
        
        response = requests.post(
            f"{SYNERGY_API_BASE}/task/{task_id}/subtask/create",
            json=payload,
            headers={"Content-Type": "application/json"},
            timeout=10
        )
        
        response.raise_for_status()
        result = response.json()
        
        return {
            "success": True,
            "subtask_id": result.get("subtask_id"),
            "message": f"✅ Created subtask: {task[:50]}..."
        }
        
    except requests.exceptions.RequestException as e:
        raise SynergyError(f"Failed to create subtask: {str(e)}")


def synergy_update_subtask(
    subtask_id: str,
    task: Optional[str] = None,
    priority: Optional[str] = None,
    completed: Optional[bool] = None,
    estimated_hours: Optional[float] = None,
    actual_hours: Optional[float] = None,
    assigned_to: Optional[str] = None,
    tags: Optional[List[str]] = None,
    archived: Optional[bool] = None,
    **kwargs
) -> Dict[str, Any]:
    """
    Update any field(s) of an existing subtask
    
    Args:
        subtask_id: Subtask ID to update (required)
        task: Update subtask description
        priority: Update priority
        completed: Mark as complete/incomplete
        estimated_hours: Update time estimate
        actual_hours: Update actual time spent
        assigned_to: Update assignee
        tags: REPLACE all tags
        archived: Archive subtask
        
    Returns:
        Dict with success status and updated fields
        
    Example:
        synergy_update_subtask(
            subtask_id="sub_20251124120000",
            completed=True,
            actual_hours=0.5
        )
    """
    try:
        updates = {}
        
        if task is not None:
            updates["task"] = task
        if priority is not None:
            updates["priority"] = priority
        if completed is not None:
            updates["completed"] = completed
        if estimated_hours is not None:
            updates["estimated_hours"] = estimated_hours
        if actual_hours is not None:
            updates["actual_hours"] = actual_hours
        if assigned_to is not None:
            updates["assigned_to"] = assigned_to
        if tags is not None:
            updates["tags"] = tags
        if archived is not None:
            updates["archived"] = archived
        
        response = requests.patch(
            f"{SYNERGY_API_BASE}/subtask/{subtask_id}",
            json=updates,
            headers={"Content-Type": "application/json"},
            timeout=10
        )
        
        response.raise_for_status()
        
        return {
            "success": True,
            "subtask_id": subtask_id,
            "updated_fields": list(updates.keys()),
            "message": f"✅ Updated subtask ({len(updates)} fields)"
        }
        
    except requests.exceptions.RequestException as e:
        raise SynergyError(f"Failed to update subtask {subtask_id}: {str(e)}")


# ============================================================================
# DELETE OPERATIONS
# ============================================================================

def synergy_remove_document(
    session_id: str,
    doc_index: int,
    **kwargs
) -> Dict[str, Any]:
    """
    Remove a document from session by index position
    
    More efficient than synergy_update_session for removing a single document.
    
    Args:
        session_id: Session ID (required)
        doc_index: Index of document to remove (0-based)
                   Example: 0 = first document, 1 = second document
        
    Returns:
        Dict with updated documents array and removed document info
        
    Raises:
        SynergyError: If API call fails or index out of range
        
    Example:
        # Remove the second document (index 1)
        result = synergy_remove_document(
            session_id="sess_abc123",
            doc_index=1
        )
        # Returns: {"success": True, "documents": [...], "count": 2, "removed": {...}}
    """
    try:
        response = requests.delete(
            f"{SYNERGY_API_BASE}/{session_id}/document/{doc_index}",
            timeout=10
        )
        
        response.raise_for_status()
        result = response.json()
        
        return {
            "success": True,
            "session_id": session_id,
            "documents": result.get("documents", []),
            "count": result.get("count", 0),
            "removed": result.get("removed"),
            "message": f"✅ Removed document: {result.get('removed', {}).get('title', 'Unknown')}"
        }
        
    except requests.exceptions.RequestException as e:
        raise SynergyError(f"Failed to remove document from session {session_id}: {str(e)}")


def synergy_remove_link(
    session_id: str,
    link_index: int,
    **kwargs
) -> Dict[str, Any]:
    """
    Remove a link from session by index position
    
    Args:
        session_id: Session ID (required)
        link_index: Index of link to remove (0-based)
        
    Returns:
        Dict with updated links array and removed link info
        
    Raises:
        SynergyError: If API call fails or index out of range
        
    Example:
        result = synergy_remove_link(
            session_id="sess_abc123",
            link_index=0
        )
    """
    try:
        response = requests.delete(
            f"{SYNERGY_API_BASE}/{session_id}/link/{link_index}",
            timeout=10
        )
        
        response.raise_for_status()
        result = response.json()
        
        return {
            "success": True,
            "session_id": session_id,
            "links": result.get("links", []),
            "count": result.get("count", 0),
            "removed": result.get("removed"),
            "message": f"✅ Removed link: {result.get('removed', {}).get('title', 'Unknown')}"
        }
        
    except requests.exceptions.RequestException as e:
        raise SynergyError(f"Failed to remove link from session {session_id}: {str(e)}")


def synergy_remove_tag(
    session_id: str,
    tag_name: str,
    **kwargs
) -> Dict[str, Any]:
    """
    Remove a tag from session by name
    
    Args:
        session_id: Session ID (required)
        tag_name: Tag name to remove (case-insensitive)
        
    Returns:
        Dict with updated tags array
        
    Raises:
        SynergyError: If API call fails or tag not found
        
    Example:
        result = synergy_remove_tag(
            session_id="sess_abc123",
            tag_name="urgent"
        )
    """
    try:
        response = requests.delete(
            f"{SYNERGY_API_BASE}/{session_id}/tag/{tag_name}",
            timeout=10
        )
        
        response.raise_for_status()
        result = response.json()
        
        return {
            "success": True,
            "session_id": session_id,
            "tags": result.get("tags", []),
            "count": result.get("count", 0),
            "removed": tag_name,
            "message": f"✅ Removed tag: {tag_name}"
        }
        
    except requests.exceptions.RequestException as e:
        raise SynergyError(f"Failed to remove tag from session {session_id}: {str(e)}")


def synergy_delete_milestone(
    milestone_id: str,
    **kwargs
) -> Dict[str, Any]:
    """
    Delete a milestone and all its tasks/subtasks permanently
    
    CRITICAL: This is a destructive operation. All tasks and subtasks
    under this milestone will also be deleted (cascade delete).
    
    Args:
        milestone_id: Milestone ID to delete (required)
        
    Returns:
        Dict with deletion counts for milestone, tasks, and subtasks
        
    Raises:
        SynergyError: If API call fails or milestone not found
        
    Example:
        result = synergy_delete_milestone(
            milestone_id="ms_20251124120000"
        )
        # Returns: {
        #   "success": True,
        #   "milestone_id": "ms_20251124120000",
        #   "tasks_deleted": 5,
        #   "subtasks_deleted": 12
        # }
    """
    try:
        response = requests.delete(
            f"{SYNERGY_API_BASE}/milestone/{milestone_id}",
            timeout=10
        )
        
        response.raise_for_status()
        result = response.json()
        
        return {
            "success": True,
            "milestone_id": milestone_id,
            "tasks_deleted": result.get("tasks_deleted", 0),
            "subtasks_deleted": result.get("subtasks_deleted", 0),
            "message": result.get("message", f"✅ Deleted milestone {milestone_id}")
        }
        
    except requests.exceptions.RequestException as e:
        raise SynergyError(f"Failed to delete milestone {milestone_id}: {str(e)}")


def synergy_delete_task(
    task_id: str,
    **kwargs
) -> Dict[str, Any]:
    """
    Delete a task and all its subtasks permanently
    
    CRITICAL: This is a destructive operation. All subtasks under this
    task will also be deleted (cascade delete).
    
    Args:
        task_id: Task ID to delete (required)
        
    Returns:
        Dict with deletion count for subtasks
        
    Raises:
        SynergyError: If API call fails or task not found
        
    Example:
        result = synergy_delete_task(
            task_id="task_20251124120000"
        )
        # Returns: {
        #   "success": True,
        #   "task_id": "task_20251124120000",
        #   "subtasks_deleted": 3
        # }
    """
    try:
        response = requests.delete(
            f"{SYNERGY_API_BASE}/task/{task_id}",
            timeout=10
        )
        
        response.raise_for_status()
        result = response.json()
        
        return {
            "success": True,
            "task_id": task_id,
            "subtasks_deleted": result.get("subtasks_deleted", 0),
            "message": result.get("message", f"✅ Deleted task {task_id}")
        }
        
    except requests.exceptions.RequestException as e:
        raise SynergyError(f"Failed to delete task {task_id}: {str(e)}")


def synergy_delete_subtask(
    subtask_id: str,
    **kwargs
) -> Dict[str, Any]:
    """
    Delete a subtask permanently
    
    Args:
        subtask_id: Subtask ID to delete (required)
        
    Returns:
        Dict with success status
        
    Raises:
        SynergyError: If API call fails or subtask not found
        
    Example:
        result = synergy_delete_subtask(
            subtask_id="sub_20251124120000"
        )
    """
    try:
        response = requests.delete(
            f"{SYNERGY_API_BASE}/subtask/{subtask_id}",
            timeout=10
        )
        
        response.raise_for_status()
        result = response.json()
        
        return {
            "success": True,
            "subtask_id": subtask_id,
            "message": f"✅ Deleted subtask {subtask_id}"
        }
        
    except requests.exceptions.RequestException as e:
        raise SynergyError(f"Failed to delete subtask {subtask_id}: {str(e)}")


def synergy_set_milestone_blocker(
    milestone_id: str,
    blocked: bool,
    blocker_reason: Optional[str] = None,
    **kwargs
) -> Dict[str, Any]:
    """
    Mark a milestone as blocked or unblocked
    
    This is a convenience wrapper around synergy_update_milestone().
    
    Args:
        milestone_id: Milestone ID (required)
        blocked: True to block, False to unblock (required)
        blocker_reason: Reason for blocking (required if blocked=True)
        
    Returns:
        Dict with success status
        
    Raises:
        SynergyError: If API call fails
        
    Example:
        # Block a milestone
        synergy_set_milestone_blocker(
            milestone_id="ms_20251124120000",
            blocked=True,
            blocker_reason="Waiting for API credentials"
        )
        
        # Unblock a milestone
        synergy_set_milestone_blocker(
            milestone_id="ms_20251124120000",
            blocked=False
        )
    """
    if blocked and not blocker_reason:
        raise SynergyError("blocker_reason is required when blocked=True")
    
    return synergy_update_milestone(
        milestone_id=milestone_id,
        blocked=blocked,
        blocker_reason=blocker_reason if blocked else None,
        **kwargs
    )


def synergy_set_task_blocker(
    task_id: str,
    blocked: bool,
    blocker_reason: Optional[str] = None,
    **kwargs
) -> Dict[str, Any]:
    """
    Mark a task as blocked or unblocked
    
    This is a convenience wrapper around synergy_update_task().
    
    Args:
        task_id: Task ID (required)
        blocked: True to block, False to unblock (required)
        blocker_reason: Reason for blocking (required if blocked=True)
        
    Returns:
        Dict with success status
        
    Raises:
        SynergyError: If API call fails
        
    Example:
        # Block a task
        synergy_set_task_blocker(
            task_id="task_20251124120000",
            blocked=True,
            blocker_reason="Waiting for database access"
        )
        
        # Unblock a task
        synergy_set_task_blocker(
            task_id="task_20251124120000",
            blocked=False
        )
    """
    if blocked and not blocker_reason:
        raise SynergyError("blocker_reason is required when blocked=True")
    
    return synergy_update_task(
        task_id=task_id,
        blocked=blocked,
        blocker_reason=blocker_reason if blocked else None,
        **kwargs
    )


# ============================================================
# 🆕 SURGICAL UPDATE FUNCTIONS - No array rewrites
# ============================================================

def synergy_add_milestone_document(
    milestone_id: str,
    title: str,
    url: str,
    doc_type: str = "other",
    **kwargs
) -> Dict[str, Any]:
    """
    🆕 SURGICAL ADD: Add ONE document to a milestone without rewriting the entire documents array
    
    This function APPENDS a single document to the existing documents list.
    It does NOT touch or rewrite any existing documents.
    
    Args:
        milestone_id: Milestone ID (required)
        title: Document title (required)
        url: Document URL (required)
        doc_type: Document type (default: "other")
                  Options: "google_doc", "google_sheet", "figma", "pdf", "other"
        
    Returns:
        Dict with:
        - success: bool
        - document_added: Dict with title, url, type
        - total_documents: int (new count after addition)
        
    Raises:
        SynergyError: If API call fails
        
    Example:
        result = synergy_add_milestone_document(
            milestone_id="ms_20251124120000",
            title="API Documentation",
            url="https://docs.google.com/document/d/abc123",
            doc_type="google_doc"
        )
        # Result: {"success": True, "document_added": {...}, "total_documents": 3}
        
    Note: This is MUCH faster than fetching all documents, appending, and rewriting the array.
    """
    try:
        payload = {
            "title": title,
            "url": url,
            "type": doc_type
        }
        
        response = requests.post(
            f"{SYNERGY_API_BASE}/milestone/{milestone_id}/document/add",
            json=payload,
            headers={"Content-Type": "application/json"},
            timeout=10
        )
        
        response.raise_for_status()
        result = response.json()
        
        return {
            "success": True,
            "document_added": result.get("document_added"),
            "total_documents": result.get("total_documents"),
            "message": f"✅ Added document '{title}' to milestone"
        }
        
    except requests.exceptions.RequestException as e:
        raise SynergyError(f"Failed to add document to milestone: {str(e)}")


def synergy_add_milestone_link(
    milestone_id: str,
    title: str,
    url: str,
    **kwargs
) -> Dict[str, Any]:
    """
    🆕 SURGICAL ADD: Add ONE link to a milestone without rewriting the entire links array
    
    This function APPENDS a single link to the existing links list.
    It does NOT touch or rewrite any existing links.
    
    Args:
        milestone_id: Milestone ID (required)
        title: Link title (required)
        url: Link URL (required)
        
    Returns:
        Dict with:
        - success: bool
        - link_added: Dict with title, url
        - total_links: int (new count after addition)
        
    Raises:
        SynergyError: If API call fails
        
    Example:
        result = synergy_add_milestone_link(
            milestone_id="ms_20251124120000",
            title="Production Dashboard",
            url="https://dashboard.example.com"
        )
        # Result: {"success": True, "link_added": {...}, "total_links": 2}
    """
    try:
        payload = {
            "title": title,
            "url": url
        }
        
        response = requests.post(
            f"{SYNERGY_API_BASE}/milestone/{milestone_id}/link/add",
            json=payload,
            headers={"Content-Type": "application/json"},
            timeout=10
        )
        
        response.raise_for_status()
        result = response.json()
        
        return {
            "success": True,
            "link_added": result.get("link_added"),
            "total_links": result.get("total_links"),
            "message": f"✅ Added link '{title}' to milestone"
        }
        
    except requests.exceptions.RequestException as e:
        raise SynergyError(f"Failed to add link to milestone: {str(e)}")


def synergy_update_task_field(
    task_id: str,
    field: str,
    value: Any,
    **kwargs
) -> Dict[str, Any]:
    """
    🆕 SURGICAL UPDATE: Update ONE field of a task without touching other fields
    
    This function updates a SINGLE field on a task. No other fields are touched.
    This is MUCH faster than fetching the entire task, modifying it, and sending it back.
    
    Args:
        task_id: Task ID (required)
        field: Field name to update (required)
               Allowed: "task", "priority", "completed", "estimated_hours", 
                       "actual_hours", "blocked", "blocker_reason"
        value: New value for the field (required)
        
    Returns:
        Dict with:
        - success: bool
        - task_id: str
        - field_updated: str
        - new_value: Any
        
    Raises:
        SynergyError: If API call fails or field is invalid
        
    Examples:
        # Update task text
        synergy_update_task_field(
            task_id="task_20251124120000",
            field="task",
            value="Update user authentication flow"
        )
        
        # Change priority
        synergy_update_task_field(
            task_id="task_20251124120000",
            field="priority",
            value="high"
        )
        
        # Mark complete
        synergy_update_task_field(
            task_id="task_20251124120000",
            field="completed",
            value=True
        )
        
        # Add blocker
        synergy_update_task_field(
            task_id="task_20251124120000",
            field="blocked",
            value=True
        )
        synergy_update_task_field(
            task_id="task_20251124120000",
            field="blocker_reason",
            value="Waiting for API keys"
        )
    """
    try:
        allowed_fields = ['task', 'priority', 'completed', 'estimated_hours', 
                         'actual_hours', 'blocked', 'blocker_reason']
        
        if field not in allowed_fields:
            raise SynergyError(f"Invalid field '{field}'. Allowed: {', '.join(allowed_fields)}")
        
        payload = {
            "field": field,
            "value": value
        }
        
        response = requests.patch(
            f"{SYNERGY_API_BASE}/task/{task_id}/update-field",
            json=payload,
            headers={"Content-Type": "application/json"},
            timeout=10
        )
        
        response.raise_for_status()
        result = response.json()
        
        return {
            "success": True,
            "task_id": result.get("task_id"),
            "field_updated": result.get("field_updated"),
            "new_value": result.get("new_value"),
            "message": f"✅ Updated task.{field} = {value}"
        }
        
    except requests.exceptions.RequestException as e:
        raise SynergyError(f"Failed to update task field: {str(e)}")


def synergy_update_subtask_field(
    subtask_id: str,
    field: str,
    value: Any,
    **kwargs
) -> Dict[str, Any]:
    """
    🆕 SURGICAL UPDATE: Update ONE field of a subtask without touching other fields
    
    This function updates a SINGLE field on a subtask. No other fields are touched.
    This is MUCH faster than fetching the entire subtask, modifying it, and sending it back.
    
    Args:
        subtask_id: Subtask ID (required)
        field: Field name to update (required)
               Allowed: "task", "priority", "completed", "estimated_hours", "actual_hours"
        value: New value for the field (required)
        
    Returns:
        Dict with:
        - success: bool
        - subtask_id: str
        - field_updated: str
        - new_value: Any
        
    Raises:
        SynergyError: If API call fails or field is invalid
        
    Examples:
        # Update subtask text
        synergy_update_subtask_field(
            subtask_id="subtask_20251124120000",
            field="task",
            value="Test OAuth flow with Google"
        )
        
        # Change priority
        synergy_update_subtask_field(
            subtask_id="subtask_20251124120000",
            field="priority",
            value="high"
        )
        
        # Mark complete
        synergy_update_subtask_field(
            subtask_id="subtask_20251124120000",
            field="completed",
            value=True
        )
    """
    try:
        allowed_fields = ['task', 'priority', 'completed', 'estimated_hours', 'actual_hours']
        
        if field not in allowed_fields:
            raise SynergyError(f"Invalid field '{field}'. Allowed: {', '.join(allowed_fields)}")
        
        payload = {
            "field": field,
            "value": value
        }
        
        response = requests.patch(
            f"{SYNERGY_API_BASE}/subtask/{subtask_id}/update-field",
            json=payload,
            headers={"Content-Type": "application/json"},
            timeout=10
        )
        
        response.raise_for_status()
        result = response.json()
        
        return {
            "success": True,
            "subtask_id": result.get("subtask_id"),
            "field_updated": result.get("field_updated"),
            "new_value": result.get("new_value"),
            "message": f"✅ Updated subtask.{field} = {value}"
        }
        
    except requests.exceptions.RequestException as e:
        raise SynergyError(f"Failed to update subtask field: {str(e)}")

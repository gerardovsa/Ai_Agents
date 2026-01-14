"""
Synergy Tool Recommender - Intelligent tool selection guide for AI agents

This tool analyzes the AI's current situation and recommends which Synergy tool
to use next, along with complete usage instructions and schema information.

Functions:
- synergy_recommend_next_tool: Get personalized tool recommendation based on context
"""

from typing import Dict, Any, Optional, List


def synergy_recommend_next_tool(
    current_situation: str,
    have_session_id: bool = False,
    resources_created: int = 0,
    task_type: Optional[str] = None,
    **kwargs
) -> Dict[str, Any]:
    """
    Get intelligent recommendation for which Synergy tool to use next
    
    This tool analyzes your current situation and recommends:
    1. Which tool to call next
    2. Why this tool is appropriate
    3. Complete parameter list with examples
    4. Step-by-step execution instructions
    5. What to do after this tool succeeds
    
    Args:
        current_situation: Your current state. Options:
            - "just_starting" - First time using Synergy, need to create project
            - "structured_project" - Multi-phase project, need milestone-based structure
            - "project_created" - Have session_id, created first resource
            - "adding_resources" - Adding more resources to existing project
            - "need_to_update" - Have resources, need to update Synergy
            - "moving_card" - Want to change Kanban column
            - "checking_status" - Want to see current project state
            - "listing_projects" - Want to see all Synergy projects
            - "troubleshooting" - Something went wrong
            - "learning" - Need to understand Synergy concepts
            
        have_session_id: Do you have a session_id saved? (True/False)
        
        resources_created: How many resources have you created so far?
            - 0 = Haven't created anything yet
            - 1-2 = Created some resources
            - 3+ = Created multiple resources
            
        task_type: (Optional) What kind of project?
            - "multi_platform" - Using 3+ different platforms
            - "automation" - Building automated workflow
            - "data_pipeline" - Data collection/processing
            - "customer_system" - Customer-facing system
            - "internal_tool" - Internal business tool
            
        **kwargs: Credential injection (not used for this tool)
    
    Returns:
        Dict with:
        - success: True/False
        - recommended_tool: Tool name to call next
        - reason: Why this tool is recommended
        - parameters: Complete parameter list with types
        - example: Working code example
        - next_steps: What to do after this tool succeeds
        - warning: Critical warnings (if any)
        - schema_to_fetch: Which schemas to get with get_tool_schema()
    
    Example:
        # Just starting a multi-platform project
        rec = synergy_recommend_next_tool(
            current_situation="just_starting",
            have_session_id=False,
            resources_created=0,
            task_type="multi_platform"
        )
        
        print(rec["recommended_tool"])
        # "synergy_smart_project_tracker"
        
        print(rec["reason"])
        # "You're starting a new multi-platform project..."
        
        print(rec["example"])
        # [Complete working code example]
    """
    
    # Recommendation logic based on situation
    recommendations = {
        "structured_project": {
            "recommended_tool": "synergy_smart_project_tracker",
            "reason": """
You're working on a STRUCTURED multi-phase project. Use the SMART TOOL with MILESTONES!

The synergy_smart_project_tracker() with use_milestones=True is the EASIEST way to create 
complete structured projects in ONE CALL. It automatically:
- Creates the Synergy session
- Creates all milestones with tasks and subtasks
- Sets up dependencies and time tracking
- Returns all milestone IDs for future updates

Milestones are perfect when:
- Project has clear phases (Planning → Development → Testing)
- Need dependencies between phases
- Want phase-specific documents and time tracking
- Need to track progress through structured stages
- Need phase-specific documents and resources
- Want to set dependencies between phases

WORKFLOW:
1. Create session with synergy_create_session()
2. Create milestone for each major phase
3. Each milestone contains tasks and subtasks
4. Add documents specific to each phase
5. Track progress through milestone completion

This provides MUCH better structure than flat next_steps lists!
            """,
            "parameters": {
                "title": {
                    "type": "string",
                    "required": True,
                    "description": "Project title",
                    "example": "Customer Database Migration"
                },
                "platforms_involved": {
                    "type": "array",
                    "required": True,
                    "description": "List of platforms used",
                    "example": ["sheets", "forms", "gmail", "drive"]
                },
                "use_milestones": {
                    "type": "boolean",
                    "required": True,
                    "description": "Set to True for milestone structure",
                    "example": True
                },
                "initial_milestones": {
                    "type": "array",
                    "required": True,
                    "description": "Array of milestones to create",
                    "example": [
                        {
                            "milestone_name": "Phase 1: Setup",
                            "tasks": ["Create sheet", "Design schema"],
                            "priority": "critical",
                            "estimated_hours": 8
                        }
                    ]
                },
                "priority": {
                    "type": "string",
                    "required": False,
                    "default": "high",
                    "options": ["low", "medium", "high", "critical"],
                    "example": "critical"
                },
                "tags": {
                    "type": "array",
                    "required": False,
                    "description": "Tags for categorization",
                    "example": ["migration", "database", "multi-phase"]
                }
            },
            "example": """
# EASIEST WAY: Create complete milestone project in ONE CALL!

result = synergy_smart_project_tracker(
    title="Customer Database Migration",
    description="Multi-phase migration from legacy CRM to Google Sheets",
    platforms_involved=["sheets", "forms", "gmail", "drive"],
    priority="critical",
    start_in_column="in_progress",
    tags=["migration", "database"],
    
    # KEY: Enable milestone structure
    use_milestones=True,
    
    # KEY: Provide all milestones in initial_milestones array
    initial_milestones=[
        {
            "milestone_name": "Phase 1: Database Setup",
            "description": "Create new database infrastructure",
            "tasks": [
                "Create Google Sheet with schema",
                {
                    "task": "Design data model",
                    "subtasks": [
                        "Define customer fields",
                        "Set up validation rules",
                        "Create lookup tables"
                    ]
                },
                "Import test data"
            ],
            "priority": "critical",
            "due_date": "2025-12-01",
            "estimated_hours": 8,
            "tags": ["database", "setup"]
        },
        {
            "milestone_name": "Phase 2: Data Import",
            "description": "Import existing customer data",
            "tasks": [
                {
                    "task": "Export from legacy CRM",
                    "subtasks": [
                        "Connect to old system",
                        "Export customer records",
                        "Export transaction history"
                    ]
                },
                "Clean and format data",
                "Import to new database"
            ],
            "priority": "high",
            "due_date": "2025-12-08",
            "estimated_hours": 12,
            "tags": ["migration", "data"]
        },
        {
            "milestone_name": "Phase 3: Integration & Testing",
            "description": "Connect forms and test workflow",
            "tasks": [
                "Create Google Form for new entries",
                "Set up form-to-sheet automation",
                "Create email notification triggers",
                "Test complete workflow"
            ],
            "priority": "medium",
            "due_date": "2025-12-15",
            "estimated_hours": 6,
            "tags": ["automation", "testing"]
        }
    ]
)

# Save everything!
session_id = result["session_id"]
milestones = result["milestones_created"]

# Extract milestone IDs
m1_id = milestones[0]["milestone_id"]
m2_id = milestones[1]["milestone_id"]
m3_id = milestones[2]["milestone_id"]

# Now work on Phase 1
sheet = google_sheets_create(title="Customer Database")

# Add to Phase 1
synergy_update_milestone(
    milestone_id=m1_id,
    documents=[{
        "title": "Customer Database Sheet",
        "url": sheet["spreadsheet_url"],
        "type": "google_sheet"
    }]
)

# Complete Phase 1
synergy_update_milestone(
    milestone_id=m1_id,
    completed=True,
    actual_hours=7.5
)

# Phase 2 is now automatically unblocked!
            """,
            "next_steps": """
After creating project with smart tool:

1. **SAVE IDs** - You need these for updates!
   ```python
   session_id = result["session_id"]
   milestones = result["milestones_created"]
   m1_id = milestones[0]["milestone_id"]
   m2_id = milestones[1]["milestone_id"]
   m3_id = milestones[2]["milestone_id"]
   ```

2. **Work on first milestone**:
   - Create resources for Phase 1
   - Add documents with synergy_update_milestone()
   - Complete tasks as you go

3. **Update milestone with documents**:
   ```python
   sheet = google_sheets_create(...)
   
   synergy_update_milestone(
       milestone_id=m1_id,
       documents=[{
           "title": "Database Sheet",
           "url": sheet["spreadsheet_url"],
           "type": "google_sheet"
       }]
   )
   ```

4. **Complete milestone when done**:
   ```python
   synergy_update_milestone(
       milestone_id=m1_id,
       completed=True,
       actual_hours=8
   )
   ```

5. **Move to next milestone**:
   - Phase 2 automatically unblocked
   - Repeat process for next phase

6. **View progress**:
   ```python
   milestones = synergy_get_milestones(session_id=session_id)
   # See all milestones with completion status
   ```

7. **Learn more**:
   ```python
   synergy_agent_instructions(topic="smart_tool_milestones")
   ```
            """,
            "warning": """
⚠️ MILESTONE vs FLAT STRUCTURE:

Use MILESTONES when:
✅ Multi-phase project (Planning → Dev → Test → Deploy)
✅ Need phase-specific documents
✅ Want to track progress through stages
✅ Need dependencies between phases

Use FLAT (next_steps) when:
❌ Simple checklist project
❌ Single-phase work
❌ Quick one-off tasks

DON'T mix both in same session - choose one structure!
            """,
            "schema_to_fetch": [
                "synergy_smart_project_tracker",
                "synergy_update_milestone",
                "synergy_get_milestones",
                "synergy_get_milestones",
                "synergy_agent_instructions"
            ]
        },
        "just_starting": {
            "recommended_tool": "synergy_smart_project_tracker",
            "reason": """
You're starting a NEW multi-platform project. Use synergy_smart_project_tracker()
because it sets up everything in ONE call:
- Creates Synergy session
- Sets up Kanban card
- Initializes next steps checklist
- Configures platforms list
- Returns session_id for future updates

This is your PRIMARY tool for starting projects. It's 5x faster than calling
individual functions.
            """,
            "parameters": {
                "title": {
                    "type": "string",
                    "required": True,
                    "description": "Project title - clear, descriptive name",
                    "example": "Customer Onboarding System"
                },
                "platforms_involved": {
                    "type": "array[string]",
                    "required": True,
                    "description": "List of platforms you'll use",
                    "example": ["gmail", "sheets", "forms", "docs"]
                },
                "next_steps": {
                    "type": "array[string]",
                    "required": True,
                    "description": "Action items checklist",
                    "example": [
                        "Create welcome email template",
                        "Create signup form",
                        "Create tracking spreadsheet"
                    ]
                },
                "description": {
                    "type": "string",
                    "required": False,
                    "description": "What you're building and why",
                    "example": "Multi-platform workflow to onboard new customers with automated emails, forms, and tracking"
                },
                "priority": {
                    "type": "string",
                    "required": False,
                    "default": "high",
                    "options": ["low", "medium", "high", "critical"],
                    "example": "high"
                },
                "start_in_column": {
                    "type": "string",
                    "required": False,
                    "default": "in_progress",
                    "options": ["backlog", "in_progress"],
                    "description": "Start in backlog (planning) or in_progress (active work)",
                    "example": "in_progress"
                }
            },
            "example": """
# Complete working example
result = synergy_smart_project_tracker(
    title="Customer Feedback System",
    platforms_involved=["forms", "sheets", "gmail"],
    next_steps=[
        "Create feedback form",
        "Create response tracking sheet",
        "Set up email notifications"
    ],
    description="Collect and track customer feedback with automated notifications",
    priority="high",
    start_in_column="in_progress"
)

# CRITICAL: Save session_id immediately!
session_id = result["session_id"]
print(f"Session ID: {session_id}")  # Save this for all future updates

# Tell user
print(f"Dashboard: {result['dashboard_url']}")
print(f"Status: {result['message']}")
            """,
            "next_steps": """
After synergy_smart_project_tracker() succeeds:

1. **SAVE SESSION_ID** - You'll need this for ALL future updates!
   ```python
   session_id = result["session_id"]  # DON'T LOSE THIS!
   ```

2. **Create your first resource** (doc, sheet, form, email, etc.)

3. **Update Synergy after EACH resource** (CRITICAL - see Rule #2):
   - Call synergy_get_session(session_id) first
   - Add new resource to existing documents array
   - Call synergy_update_session(session_id, documents=all_docs)

4. **Tell user about dashboard**:
   ```markdown
   ✅ Project created: [Title]
   Dashboard: http://localhost:5001/synergy.html
   Resources will be added as you create them.
   ```

5. **If you need help with updates**, call:
   ```python
   synergy_recommend_next_tool(
       current_situation="need_to_update",
       have_session_id=True,
       resources_created=1
   )
   ```
            """,
            "warning": """
⚠️ CRITICAL WARNINGS:

1. **MUST save session_id** - You can't update project without it!
2. **MUST update after EACH resource** - Or dashboard shows 0 documents
3. **MUST fetch before updating arrays** - Or you'll delete existing data

If you forget these, call:
synergy_recommend_next_tool(current_situation="troubleshooting")
            """,
            "schema_to_fetch": ["synergy_smart_project_tracker"]
        },
        
        "project_created": {
            "recommended_tool": "synergy_get_session",
            "reason": """
You created a Synergy project and now you've created your FIRST resource.
Before adding it to Synergy, you MUST fetch the current state first!

Call synergy_get_session() to:
- Get current documents array (even if empty)
- See current project state
- Prepare for safe update

This prevents data loss when updating arrays.
            """,
            "parameters": {
                "session_id": {
                    "type": "string",
                    "required": True,
                    "description": "Session ID from synergy_smart_project_tracker() result",
                    "example": "1731026474751"
                }
            },
            "example": """
# You have: session_id = "1731026474751"
# You created: sheet with URL https://docs.google.com/spreadsheets/d/ABC123/edit

# Step 1: Get current session
session = synergy_get_session(session_id="1731026474751")

# Step 2: Get existing documents (might be empty)
existing_docs = session["session"]["documents"]
print(f"Current docs: {len(existing_docs)}")  # Probably 0 right now

# Step 3: Add your new resource
new_doc = {
    "name": "Customer Tracking Sheet",
    "url": "https://docs.google.com/spreadsheets/d/ABC123/edit",
    "type": "google_sheet"
}

# Step 4: Combine existing + new
all_docs = existing_docs + [new_doc]

# Step 5: Update with ALL documents
synergy_update_session(
    session_id=session_id,
    documents=all_docs  # ← ALL docs, not just new one
)

print(f"Updated! Now {len(all_docs)} documents on dashboard")
            """,
            "next_steps": """
After synergy_get_session() succeeds:

1. **Extract existing documents array**:
   ```python
   existing_docs = session["session"]["documents"]
   ```

2. **Create new document object** for your resource:
   ```python
   new_doc = {
       "name": "Resource Name",
       "url": "https://...",
       "type": "google_sheet|google_doc|google_form|email|pdf|etc"
   }
   ```

3. **Combine existing + new**:
   ```python
   all_docs = existing_docs + [new_doc]
   ```

4. **Update session with ALL documents**:
   ```python
   synergy_update_session(session_id, documents=all_docs)
   ```

5. **Repeat this pattern for EACH new resource** you create

6. **If creating another resource now**, call:
   ```python
   synergy_recommend_next_tool(
       current_situation="adding_resources",
       have_session_id=True,
       resources_created=2
   )
   ```
            """,
            "warning": """
⚠️ CRITICAL: Always fetch before updating!

If you skip synergy_get_session() and call synergy_update_session() directly:
- You'll REPLACE the documents array
- Any existing documents will be DELETED
- Dashboard will show wrong information

Pattern: FETCH → COMBINE → UPDATE (always in this order!)
            """,
            "schema_to_fetch": ["synergy_get_session", "synergy_update_session"]
        },
        
        "adding_resources": {
            "recommended_tool": "synergy_get_session → synergy_update_session",
            "reason": f"""
You're adding resource #{resources_created + 1} to your Synergy project.
Follow the FETCH → COMBINE → UPDATE pattern again.

Even though you just updated Synergy with resource #{resources_created},
you MUST fetch again before adding resource #{resources_created + 1}.

Why? Because the documents array might have changed, and you need the
current state to avoid data loss.
            """,
            "parameters": {
                "synergy_get_session": {
                    "session_id": {
                        "type": "string",
                        "required": True,
                        "example": "Your saved session_id"
                    }
                },
                "synergy_update_session": {
                    "session_id": {
                        "type": "string",
                        "required": True,
                        "example": "Same session_id"
                    },
                    "documents": {
                        "type": "array[object]",
                        "required": True,
                        "description": "ALL documents (existing + new)",
                        "example": [
                            {"name": "Doc 1", "url": "...", "type": "google_sheet"},
                            {"name": "Doc 2", "url": "...", "type": "google_form"}
                        ]
                    }
                }
            },
            "example": f"""
# You have: {resources_created} resources already in Synergy
# You just created: New resource with URL

# Step 1: Fetch current state (MANDATORY!)
session = synergy_get_session(session_id=session_id)
existing_docs = session["session"]["documents"]
print(f"Current docs: {{len(existing_docs)}}")  # Should be {resources_created}

# Step 2: Create new document object
new_doc = {{
    "name": "New Resource Name",
    "url": "https://...",
    "type": "google_doc"  # or google_sheet, google_form, email, etc.
}}

# Step 3: Combine (this is safe because we fetched first)
all_docs = existing_docs + [new_doc]
print(f"Total docs: {{len(all_docs)}}")  # Should be {resources_created + 1}

# Step 4: Update with ALL
synergy_update_session(session_id=session_id, documents=all_docs)

print(f"✅ Updated! Dashboard now shows {{len(all_docs)}} resources")
            """,
            "next_steps": """
After updating with this resource:

1. **If creating MORE resources**:
   - Create next resource
   - Call synergy_get_session() again (yes, again!)
   - Add to existing array
   - Update with ALL documents
   - Repeat for each resource

2. **If done creating resources**:
   - Check if project is ready for review
   - Move to review column if ready:
     ```python
     synergy_move_session(session_id, "review")
     ```

3. **If project is complete**:
   - Move to done column:
     ```python
     synergy_move_session(session_id, "done")
     ```

4. **Tell user about all resources created**:
   ```markdown
   ✅ Resources Created:
   - Resource 1: [URL]
   - Resource 2: [URL]
   - Resource 3: [URL]
   
   View on dashboard: http://localhost:5001/synergy.html
   ```
            """,
            "warning": """
⚠️ DON'T SKIP THE FETCH!

Even though you JUST updated Synergy, you MUST fetch again before
adding the next resource. This ensures you always have the current
state and prevents any race conditions or data loss.

Pattern for each resource:
1. Create resource
2. synergy_get_session()
3. Add to array
4. synergy_update_session()
5. Repeat
            """,
            "schema_to_fetch": ["synergy_get_session", "synergy_update_session"]
        },
        
        "need_to_update": {
            "recommended_tool": "synergy_get_session",
            "reason": """
You need to update a Synergy project. ALWAYS start with synergy_get_session()
to fetch the current state first!

This is CRITICAL because:
- Arrays (documents, links, tags) REPLACE entirely when updated
- If you don't fetch first, you'll lose existing data
- You need to know current state before modifying

After fetching, you can safely update.
            """,
            "parameters": {
                "session_id": {
                    "type": "string",
                    "required": True,
                    "description": "Session ID you saved earlier",
                    "example": "1731026474751"
                }
            },
            "example": """
# Scenario: You have session_id, want to add a document

# Step 1: Fetch current state (CRITICAL!)
session = synergy_get_session(session_id=session_id)

# Step 2: Extract what you need
existing_docs = session["session"]["documents"]
existing_tags = session["session"]["tags"]
current_priority = session["session"]["priority"]

print(f"Current state:")
print(f"  - Documents: {len(existing_docs)}")
print(f"  - Tags: {existing_tags}")
print(f"  - Priority: {current_priority}")

# Step 3: Modify what you need
new_doc = {"name": "New Doc", "url": "...", "type": "google_doc"}
all_docs = existing_docs + [new_doc]

# Step 4: Update (only updating documents, other fields unchanged)
synergy_update_session(
    session_id=session_id,
    documents=all_docs
)

print(f"✅ Updated! {len(all_docs)} documents now on dashboard")
            """,
            "next_steps": """
After synergy_get_session() succeeds:

1. **Extract the fields you want to modify**:
   ```python
   existing_docs = session["session"]["documents"]
   existing_tags = session["session"]["tags"]
   existing_links = session["session"]["links"]
   ```

2. **Modify as needed**:
   ```python
   # Add document
   all_docs = existing_docs + [new_doc]
   
   # Add tag
   all_tags = existing_tags + ["new_tag"]
   
   # Add link
   all_links = existing_links + [{"title": "...", "url": "..."}]
   ```

3. **Update with ALL items**:
   ```python
   synergy_update_session(
       session_id=session_id,
       documents=all_docs,    # ALL docs
       tags=all_tags,         # ALL tags
       links=all_links        # ALL links
   )
   ```

4. **For simple field updates** (title, description, priority):
   ```python
   # These don't need fetching, just update directly
   synergy_update_session(
       session_id=session_id,
       priority="critical",
       description="Updated description"
   )
   ```
            """,
            "warning": """
⚠️ ARRAY FIELDS REPLACE ENTIRELY:

These fields REPLACE when updated (must include ALL items):
- documents
- links
- next_steps
- checklist
- tags
- assignees
- platforms_involved

These fields UPDATE individually (no fetch needed):
- title
- description
- priority
- status
- kanban_column
- due_date
- notes

If you're updating an ARRAY field → MUST fetch first!
If you're updating a SIMPLE field → Can update directly!
            """,
            "schema_to_fetch": ["synergy_get_session", "synergy_update_session"]
        },
        
        "moving_card": {
            "recommended_tool": "synergy_move_session",
            "reason": """
You want to change the Kanban column (move the card).
Use synergy_move_session() - it's simple and safe.

Kanban columns:
- backlog → Planning/not started
- in_progress → Actively working
- review → Ready for review/testing
- done → Completed

This is a simple field update, doesn't affect arrays.
            """,
            "parameters": {
                "session_id": {
                    "type": "string",
                    "required": True,
                    "description": "Session ID",
                    "example": "1731026474751"
                },
                "new_column": {
                    "type": "string",
                    "required": True,
                    "options": ["backlog", "in_progress", "review", "done"],
                    "description": "Target column",
                    "example": "review"
                }
            },
            "example": """
# Move to review when ready for testing
result = synergy_move_session(
    session_id=session_id,
    new_column="review"
)

print(result["message"])
# "Session moved to review"

# Move to done when complete
result = synergy_move_session(
    session_id=session_id,
    new_column="done"
)

print(result["message"])
# "Session moved to done"
            """,
            "next_steps": """
After moving card:

1. **Tell user about status change**:
   ```markdown
   ✅ Project moved to [column]
   View dashboard: http://localhost:5001/synergy.html
   ```

2. **If moving to review**:
   - Ask user if they want to test/review
   - Offer to move to done after review

3. **If moving to done**:
   - Congratulate on completion!
   - Ask if user wants to archive or keep visible

4. **Typical workflow progression**:
   ```
   in_progress → review → done
   ```
            """,
            "warning": None,
            "schema_to_fetch": ["synergy_move_session"]
        },
        
        "checking_status": {
            "recommended_tool": "synergy_get_session",
            "reason": """
You want to see the current state of a Synergy project.
Use synergy_get_session() to fetch all details.

This returns:
- All 22 fields
- Current documents, links, tags
- Next steps checklist
- Kanban column position
- Everything about the project
            """,
            "parameters": {
                "session_id": {
                    "type": "string",
                    "required": True,
                    "description": "Session ID to check",
                    "example": "1731026474751"
                }
            },
            "example": """
# Get complete project status
session = synergy_get_session(session_id=session_id)

# Extract key information
project = session["session"]
title = project["title"]
status = project["kanban_column"]
docs = project["documents"]
next_steps = project["next_steps"]
tags = project["tags"]

# Report to user
print(f"Project: {title}")
print(f"Status: {status}")
print(f"Documents: {len(docs)}")
print(f"Next Steps: {len(next_steps)}")
print(f"Tags: {', '.join(tags)}")

# Show resources
for doc in docs:
    print(f"  - {doc['name']}: {doc['url']}")
            """,
            "next_steps": """
After getting session status:

1. **Report key information to user**:
   - Project title and description
   - Current Kanban column
   - Number of documents/links
   - Next steps checklist
   - Resource URLs

2. **Offer actions based on status**:
   - If in_progress → "Want to add more resources?"
   - If review → "Ready to mark as done?"
   - If done → "Want to start related project?"

3. **If user wants to modify**, use the information you just fetched
   to update safely (you already have current arrays!)
            """,
            "warning": None,
            "schema_to_fetch": ["synergy_get_session"]
        },
        
        "listing_projects": {
            "recommended_tool": "synergy_list_sessions",
            "reason": """
You want to see ALL Synergy projects (or filter by criteria).
Use synergy_list_sessions() to get a list.

This returns:
- All sessions matching filters
- Basic info for each (title, status, priority)
- Total count
- Can filter by status, priority, tags
            """,
            "parameters": {
                "status": {
                    "type": "string",
                    "required": False,
                    "options": ["active", "completed", "all"],
                    "description": "Filter by status",
                    "example": "active"
                },
                "priority": {
                    "type": "string",
                    "required": False,
                    "options": ["low", "medium", "high", "critical"],
                    "description": "Filter by priority",
                    "example": "high"
                },
                "tags": {
                    "type": "array[string]",
                    "required": False,
                    "description": "Filter by tags",
                    "example": ["urgent", "customer"]
                }
            },
            "example": """
# Get all active projects
result = synergy_list_sessions(status="active")

sessions = result["sessions"]
print(f"Found {result['total']} active projects")

for session in sessions:
    print(f"- {session['title']}")
    print(f"  Status: {session['kanban_column']}")
    print(f"  Priority: {session['priority']}")
    print(f"  Documents: {len(session['documents'])}")
    print()

# Get high priority projects
result = synergy_list_sessions(priority="high")

# Get projects with specific tag
result = synergy_list_sessions(tags=["urgent"])
            """,
            "next_steps": """
After listing sessions:

1. **Show user the list** with key details

2. **If user wants to work on one**:
   - Get the session_id from the list
   - Call synergy_get_session(session_id) for full details

3. **If user wants to create new project**:
   ```python
   synergy_recommend_next_tool(
       current_situation="just_starting",
       have_session_id=False,
       resources_created=0
   )
   ```

4. **Offer to filter** if too many results:
   - By status (active/completed)
   - By priority (high/critical)
   - By tags
            """,
            "warning": None,
            "schema_to_fetch": ["synergy_list_sessions"]
        },
        
        "troubleshooting": {
            "recommended_tool": "synergy_agent_instructions",
            "reason": """
Something went wrong! Get comprehensive troubleshooting guide.
Call synergy_agent_instructions(topic="troubleshooting") for:
- Common errors and solutions
- Data loss recovery
- Wrong field names
- Update pattern issues
            """,
            "parameters": {
                "topic": {
                    "type": "string",
                    "required": True,
                    "value": "troubleshooting",
                    "description": "Get troubleshooting guide"
                }
            },
            "example": """
# Get troubleshooting guide
guide = synergy_agent_instructions(topic="troubleshooting")

print(guide["guide"])
# Shows common errors:
# - Documents disappearing
# - Field name errors
# - Update failures
# - How to recover
            """,
            "next_steps": """
After reading troubleshooting guide:

1. **Common Issue: Documents disappeared**
   - Cause: Updated without fetching first
   - Solution: Always fetch → combine → update

2. **Common Issue: Field name error**
   - Cause: Wrong field name (e.g., "docs" instead of "documents")
   - Solution: Call synergy_agent_instructions(topic="field_reference")

3. **Common Issue: Lost session_id**
   - Cause: Didn't save session_id variable
   - Solution: Call synergy_list_sessions() and find your project

4. **Still stuck?**
   - Call synergy_agent_instructions(topic="examples") for working code
   - Call synergy_recommend_next_tool() with your current situation
            """,
            "warning": """
⚠️ MOST COMMON ERROR: Data Loss from Wrong Update Pattern

If documents disappeared:
1. You updated without fetching first
2. Arrays REPLACE entirely
3. You need to include ALL items when updating

Prevention:
- ALWAYS: synergy_get_session() first
- COMBINE: existing + new
- UPDATE: with complete array
            """,
            "schema_to_fetch": ["synergy_agent_instructions"]
        },
        
        "learning": {
            "recommended_tool": "synergy_agent_instructions",
            "reason": """
You want to learn about Synergy concepts and patterns.
Use synergy_agent_instructions() with different topics:

- "overview" - What Synergy is, when to use
- "quickstart" - Step-by-step first project guide
- "workflow" - Complete multi-platform project pattern
- "updating_arrays" - CRITICAL - Safe update patterns
- "field_reference" - All 22 fields explained
- "troubleshooting" - Common errors
- "examples" - Real-world use cases with code
            """,
            "parameters": {
                "topic": {
                    "type": "string",
                    "required": True,
                    "options": [
                        "overview",
                        "quickstart",
                        "workflow",
                        "updating_arrays",
                        "field_reference",
                        "troubleshooting",
                        "examples"
                    ],
                    "description": "Which aspect to learn about",
                    "example": "quickstart"
                }
            },
            "example": """
# Learn the basics
guide = synergy_agent_instructions(topic="overview")
print(guide["guide"])

# Get step-by-step guide
guide = synergy_agent_instructions(topic="quickstart")
print(guide["guide"])

# Learn safe update patterns (CRITICAL!)
guide = synergy_agent_instructions(topic="updating_arrays")
print(guide["guide"])

# See all available fields
guide = synergy_agent_instructions(topic="field_reference")
print(guide["guide"])
            """,
            "next_steps": """
After learning:

1. **If ready to start project**:
   ```python
   synergy_recommend_next_tool(
       current_situation="just_starting",
       task_type="multi_platform"
   )
   ```

2. **If need more examples**:
   ```python
   synergy_agent_instructions(topic="examples")
   ```

3. **If ready to execute**:
   - Get schema: get_tool_schema("synergy_smart_project_tracker")
   - Create project: synergy_smart_project_tracker(...)
   - Follow the workflow!
            """,
            "warning": """
⚠️ KEY CONCEPTS TO UNDERSTAND:

1. **Arrays REPLACE entirely** - Must fetch before updating
2. **session_id is critical** - Save it immediately
3. **Update after EACH resource** - Or dashboard shows nothing
4. **Pattern: Fetch → Combine → Update** - Always in this order

These are the most important concepts to master!
            """,
            "schema_to_fetch": ["synergy_agent_instructions"]
        }
    }
    
    # Get recommendation based on situation
    if current_situation not in recommendations:
        return {
            "success": False,
            "error": f"Unknown situation: {current_situation}",
            "valid_situations": list(recommendations.keys()),
            "suggestion": "Use 'learning' to understand Synergy, or 'just_starting' to begin"
        }
    
    rec = recommendations[current_situation]
    
    return {
        "success": True,
        "current_situation": current_situation,
        "have_session_id": have_session_id,
        "resources_created": resources_created,
        "task_type": task_type,
        "recommended_tool": rec["recommended_tool"],
        "reason": rec["reason"].strip(),
        "parameters": rec["parameters"],
        "example": rec["example"].strip(),
        "next_steps": rec["next_steps"].strip(),
        "warning": rec["warning"].strip() if rec["warning"] else None,
        "schema_to_fetch": rec["schema_to_fetch"],
        "how_to_proceed": f"""
RECOMMENDED WORKFLOW:

1. GET SCHEMA:
   {', '.join([f'get_tool_schema("{tool}")' for tool in rec["schema_to_fetch"]])}

2. EXECUTE:
   {rec["recommended_tool"]}

3. FOLLOW NEXT STEPS:
   {rec["next_steps"].strip()}
        """.strip()
    }

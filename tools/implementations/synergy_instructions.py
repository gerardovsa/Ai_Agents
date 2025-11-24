"""
Synergy Agent Instructions - On-demand learning system for AI agents

This tool provides comprehensive Synergy Dashboard workflow guidance,
best practices, and troubleshooting help. AI agents call this tool
when they need detailed instructions for specific aspects of Synergy.

Functions:
- synergy_agent_instructions: Get detailed guidance on specific topics
"""

from typing import Dict, Any


def synergy_agent_instructions(topic: str = "overview", **kwargs) -> Dict[str, Any]:
    """
    Get comprehensive Synergy Dashboard workflow instructions
    
    Args:
        topic: Which aspect of Synergy you need guidance on:
            - overview: What Synergy is, when to use, available tools
            - quickstart: Step-by-step first project creation
            - smart_tool_milestones: Using synergy_smart_project_tracker() with milestone structure
            - workflow: Complete multi-platform project pattern
            - milestones: Detailed milestone/task/subtask system guide
            - updating_arrays: How to safely add/remove items without data loss
            - field_reference: All 22 fields explained with examples
            - troubleshooting: Common errors and solutions
            - examples: Real-world use case patterns with code
        **kwargs: Credential injection (not used for this tool)
    
    Returns:
        Dict with success status, topic, and comprehensive markdown guide
    """
    
    guides = {
        "overview": """
# Synergy Dashboard Overview

## What It Is
- Visual Kanban board: Backlog → In Progress → Review → Done
- Tracks multi-platform projects across conversations
- Stores all resource links (docs, sheets, forms, emails)
- Auto-updates as you work

## When To Use
✅ Projects involving 3+ different tools/platforms
✅ Creating multiple related resources
✅ Need visual progress tracking
✅ Want to maintain context across conversations
✅ Building complex workflows (automations, systems)

❌ Simple single-tool tasks
❌ One-off document creation
❌ Quick lookups or searches

## Available Tools
- synergy_smart_project_tracker() - Create project (use this FIRST)
- synergy_list_sessions() - List all projects
- synergy_get_session() - Get project details  
- synergy_update_session() - Modify project (careful with arrays!)
- synergy_move_session() - Change Kanban column
- synergy_delete_session() - Remove project

Next: Call synergy_agent_instructions("quickstart") for step-by-step guide
        """,
        
        "quickstart": """
# Synergy Quick Start Guide

## Step-by-Step: Your First Project

### 1. Create Project (ONE CALL)
```python
result = synergy_smart_project_tracker(
    title="Email Automation System",
    platforms_involved=["gmail", "sheets", "forms"],
    next_steps=[
        "Create Gmail filter",
        "Set up tracking spreadsheet",
        "Design response form"
    ],
    priority="high",
    start_in_column="in_progress"
)

session_id = result["session_id"]  # Save this!
```

### 2. Create Your Resources
```python
# Create Gmail filter
gmail_create_filter(...)

# Create Google Sheet
sheet = google_sheets_create(title="Email Tracker")

# Create Google Form  
form = google_forms_create(title="Response Form")
```

### 3. Update Session with Resource Links
⚠️ CRITICAL: Do this after EACH resource creation!

```python
# Get current session first
session = synergy_get_session(session_id)
existing_docs = session["session"]["documents"]

# Add new resource
new_doc = {
    "name": "Email Tracker Spreadsheet",
    "url": sheet["url"],
    "type": "google_sheet"
}

# Combine existing + new
all_docs = existing_docs + [new_doc]

# Update session
synergy_update_session(
    session_id=session_id,
    documents=all_docs  # ← ALL documents, not just new one
)
```

### 4. Move Through Workflow
```python
# Move to review when ready
synergy_move_session(session_id, "review")

# Mark complete when done
synergy_move_session(session_id, "done")
```

### 5. Tell User
```markdown
✅ Project Created: Email Automation System

Resources Created:
- Email Tracker Spreadsheet: [link]
- Response Form: [link]

Status: In Progress → Review
```

## Common Mistakes

❌ **NOT updating session after creating resources**
Result: Dashboard shows 0 documents

❌ **Updating documents without fetching existing ones first**
Result: Previous documents deleted (array replacement)

❌ **Forgetting to save session_id**
Result: Can't update project later

✅ **Always:**
1. Save session_id immediately
2. Fetch existing data before updating arrays
3. Update after EACH resource creation
4. Tell user about created resources

Next: Call synergy_agent_instructions("updating_arrays") for safe update patterns
        """,
        
        "updating_arrays": """
# Synergy: Safe Array Update Patterns

## THE PROBLEM

Synergy array fields (documents, links, next_steps, checklist) **REPLACE** the entire array when updated.

### ❌ WRONG (Data Loss):
```python
# Session currently has 15 documents
# You want to add 1 more

synergy_update_session(
    session_id="sess_123",
    documents=[{new_doc}]  # ← ONLY new doc
)

# Result: 15 documents DELETED, only 1 remains!
```

### ✅ CORRECT (Data Preserved):
```python
# Step 1: Fetch existing
session = synergy_get_session(session_id="sess_123")
existing_docs = session["session"]["documents"]  # 15 documents

# Step 2: Add new
new_doc = {"name": "New Doc", "url": "https://...", "type": "pdf"}
all_docs = existing_docs + [new_doc]  # 16 documents

# Step 3: Update with ALL
synergy_update_session(
    session_id="sess_123",
    documents=all_docs  # ← All 16 documents
)

# Result: All 15 preserved + 1 new = 16 total ✅
```

## SAFE PATTERNS

### Adding Items
```python
# Get existing
session = synergy_get_session(session_id)
existing_items = session["session"]["documents"]  # or links, next_steps, etc.

# Add new
new_item = {...}
all_items = existing_items + [new_item]

# Update
synergy_update_session(session_id, documents=all_items)
```

### Removing Items
```python
# Get existing
session = synergy_get_session(session_id)
existing_docs = session["session"]["documents"]

# Filter out unwanted
filtered_docs = [doc for doc in existing_docs if doc["url"] != url_to_remove]

# Update
synergy_update_session(session_id, documents=filtered_docs)
```

### Replacing ALL Items
```python
# When you truly want to replace everything
new_docs = [{doc1}, {doc2}, {doc3}]

synergy_update_session(session_id, documents=new_docs)
# Old documents gone, new ones in place
```

## WHICH FIELDS ARE ARRAYS?

**Arrays (REPLACE behavior):**
- documents
- links
- next_steps
- tags
- assignees
- platforms_involved
- checklist
- thread_ids
- assigned_agents

**Simple Fields (UPDATE behavior):**
- title
- description
- priority
- status
- kanban_column
- due_date
- notes

## RULE OF THUMB

**Before updating ANY array field:**
1. Call `synergy_get_session(session_id)`
2. Get the current array value
3. Modify the array locally
4. Update with the COMPLETE modified array

**Exception:** Creating new session - no need to fetch, arrays start empty

Next: Call synergy_agent_instructions("field_reference") for all field details
        """,
        
        "field_reference": """
# Synergy Field Reference

## Complete Field List (22 fields)

### Basic Info
- **title** (string) - Session title
- **description** (string) - Detailed description
- **session_id** (string) - Auto-generated ID (e.g., "sess_20251108_1234_project_name")

### Organization
- **kanban_column** (enum) - backlog | in_progress | review | done
- **status** (enum) - active | completed | archived
- **priority** (enum) - low | medium | high | critical
- **tags** (array[string]) - ["automation", "urgent", "email"]
- **platforms_involved** (array[string]) - ["gmail", "sheets", "forms"]

### People
- **assignees** (array[string]) - ["John Doe", "jane@example.com"]
- **assigned_agents** (array[string]) - ["Research Agent", "Email Agent"]

### Resources
- **documents** (array[object]) - Created resources
  ```json
  {
    "name": "Document Title",
    "url": "https://...",
    "type": "google_doc|google_sheet|pdf|email|etc."
  }
  ```
  
- **links** (array[object]) - External links
  ```json
  {
    "title": "Dashboard",
    "url": "https://..."
  }
  ```

### Tasks
- **next_steps** (array) - Can be strings or objects
  ```json
  // Simple (recommended for AI agents)
  ["Step 1", "Step 2", "Step 3"]
  
  // Complex (for completion tracking)
  {
    "description": "Step text",
    "completed": false,
    "completed_at": null,
    "due_date": "2025-11-10"
  }
  ```

- **checklist** (array[object]) - Task checklist
  ```json
  {
    "task": "Item text",
    "completed": false,
    "completed_at": null,
    "subtasks": [
      {"task": "Subtask 1", "completed": false}
    ]
  }
  ```

### Timeline
- **due_date** (string) - ISO format "YYYY-MM-DD"
- **created_at** (string) - Auto-set timestamp
- **last_active** (string) - Auto-updated timestamp
- **completed_at** (string) - Set when marked done

### Activity
- **recent_activity** (array[object]) - Activity log
  ```json
  {
    "timestamp": "2025-11-08T14:30:00Z",
    "description": "Created session",
    "user": "AI Agent"
  }
  ```

### Integrations
- **thread_ids** (array[string]) - Link conversation threads
- **google_task_id** (string) - If synced to Google Tasks
- **google_calendar_id** (string) - If synced to Google Calendar

## Field Behaviors

### Auto-Set (Don't Provide)
- session_id
- created_at
- last_active (updates on any change)

### Optional
- description
- due_date
- notes
- All array fields (default to empty arrays)

### Required
- title (only required field for creation)

## Common Field Mistakes

❌ **documents using "title" instead of "name"**
✅ Use: `{"name": "Doc", ...}`

❌ **checklist using "item" or "text" instead of "task"**
✅ Use: `{"task": "Item", ...}`

❌ **next_steps as strings when need completion tracking**
✅ Use: Objects with `completed` field

❌ **Forgetting "type" field on documents**
✅ Include: `"type": "google_doc"` etc.

Next: Call synergy_agent_instructions("examples") for real-world patterns
        """,
        
        "workflow": """
# Synergy Complete Workflow Guide

## Multi-Platform Project Pattern

### Phase 1: Planning & Setup
```python
# 1. Create Synergy session (FIRST THING)
result = synergy_smart_project_tracker(
    title="Customer Onboarding System",
    description="Automated onboarding with forms, emails, and tracking",
    platforms_involved=["gmail", "forms", "sheets", "docs", "calendar"],
    next_steps=[
        "Create welcome email template",
        "Design onboarding form",
        "Set up tracking spreadsheet",
        "Create document templates",
        "Schedule follow-up automation"
    ],
    priority="high",
    start_in_column="in_progress",
    tags=["automation", "customer-success", "onboarding"],
    due_date="2025-11-15"
)

session_id = result["session_id"]  # CRITICAL: Save this!
```

### Phase 2: Resource Creation
```python
# 2. Create first resource - Gmail template
template = gmail_create_draft(
    to="{{customer_email}}",
    subject="Welcome to Our Platform!",
    body="..."
)

# 3. IMMEDIATELY update Synergy
session = synergy_get_session(session_id)
synergy_update_session(
    session_id=session_id,
    documents=session["session"]["documents"] + [{
        "name": "Welcome Email Template",
        "url": template["draft_url"],
        "type": "email"
    }]
)

# 4. Create second resource - Google Form
form = google_forms_create(
    title="Customer Onboarding Form",
    description="Please complete this form..."
)

# 5. IMMEDIATELY update Synergy
session = synergy_get_session(session_id)
synergy_update_session(
    session_id=session_id,
    documents=session["session"]["documents"] + [{
        "name": "Onboarding Form",
        "url": form["formUrl"],
        "type": "google_form"
    }]
)

# Repeat for each resource...
```

### Phase 3: Progress Tracking
```python
# Move to review when resources created
synergy_move_session(session_id, "review")

# Add notes about progress
synergy_update_session(
    session_id=session_id,
    notes="All resources created. Ready for testing."
)
```

### Phase 4: Completion
```python
# Mark complete
synergy_move_session(session_id, "done")

# Update status
synergy_update_session(
    session_id=session_id,
    status="completed"
)
```

## Cross-Conversation Context

### Starting New Conversation
```python
# 1. Check existing projects
sessions = synergy_list_sessions(column="in_progress")

# 2. Find relevant project
matching = [s for s in sessions if "onboarding" in s["title"].lower()]

if matching:
    session_id = matching[0]["session_id"]
    # Continue working on existing project
else:
    # Create new project
```

### Resuming Work
```python
# User: "Continue work on onboarding system"

# 1. Search for project
sessions = synergy_list_sessions()
project = [s for s in sessions if "onboarding" in s["title"].lower()][0]

# 2. Get full details
session = synergy_get_session(project["session_id"])

# 3. Review what's done
documents = session["session"]["documents"]
next_steps = session["session"]["next_steps"]

# 4. Continue from where left off
```

## User Communication Pattern

### Initial Creation
```markdown
✅ Created Project: Customer Onboarding System

Initial Setup:
- Priority: High
- Status: In Progress
- Due: November 15, 2025

Next Steps:
1. Create welcome email template
2. Design onboarding form
3. Set up tracking spreadsheet

I'll create these resources now and keep the dashboard updated.
```

### After Each Resource
```markdown
✅ Created: Welcome Email Template
   - Type: Gmail Draft
   - URL: [link]
   - Added to Synergy dashboard

Next: Creating onboarding form...
```

### Completion
```markdown
✅ Project Complete: Customer Onboarding System

Resources Created (5 total):
1. Welcome Email Template [link]
2. Onboarding Form [link]
3. Tracking Spreadsheet [link]
4. Document Templates [link]
5. Follow-up Calendar Events [link]

Status: Done ✓
All resources are accessible from the dashboard.
```

Next: Call synergy_agent_instructions("milestones") for structured project workflows
        """,
        
        "milestones": """
# Synergy Milestone-Based Project Management

## What Are Milestones?

Milestones are major phases/stages in a Synergy project. Each milestone contains:
- **Tasks** - Units of work within the milestone
- **Subtasks** - Granular steps within tasks
- **Documents** - Resources specific to this phase
- **Links** - References and dashboards
- **Priority, Due Dates, Time Estimates** - Planning data
- **Dependencies** - Milestone/task ordering
- **Tags** - Categorization

## When to Use Milestones

✅ **Use milestones when:**
- Project has clear phases (Planning → Development → Testing)
- Need to track progress through structured stages
- Want to organize tasks into logical groups
- Need milestone-specific documents and resources
- Want to set dependencies between phases
- Building complex systems with multiple deliverables

❌ **Don't use milestones when:**
- Simple project with just a checklist (use next_steps)
- Single-phase work (use flat task list)
- Quick one-off tasks

## Milestones vs Flat Structure

### Flat Structure (next_steps)
```
Session: "Email Campaign"
└─ Next Steps:
   - Create email template
   - Send to list
   - Track responses
```
**Use for:** Simple linear workflows, quick projects

### Milestone Structure
```
Session: "Customer Database System"
├─ Milestone 1: Database Setup
│  ├─ Task: Create Google Sheet
│  ├─ Task: Design schema
│  │  └─ Subtask: Define fields
│  │  └─ Subtask: Set validation rules
│  └─ Task: Import test data
│
├─ Milestone 2: Data Import
│  ├─ Task: Export from old CRM
│  ├─ Task: Clean data
│  │  └─ Subtask: Remove duplicates
│  │  └─ Subtask: Standardize formats
│  └─ Task: Import to new sheet
│
└─ Milestone 3: Integration
   ├─ Task: Create API
   ├─ Task: Connect to forms
   └─ Task: Test workflow
```
**Use for:** Multi-phase projects, complex systems

## Complete Milestone Workflow

### Step 1: Create Session
```python
# Create Synergy session first
result = synergy_create_session(
    title="Customer Database System",
    description="Multi-phase database setup with import and integration",
    priority="high",
    tags=["database", "migration", "customer-data"]
)

session_id = result["session_id"]  # Save this!
```

### Step 2: Create Milestones
```python
# Milestone 1: Database Setup
m1 = synergy_create_milestone(
    session_id=session_id,
    milestone_name="Database Setup",
    description="Create and configure customer database",
    tasks=[
        "Create Google Sheet for customer data",
        {
            "task": "Design database schema",
            "subtasks": [
                "Define required fields",
                "Set up data validation",
                "Create lookup tables"
            ]
        },
        "Import test data for validation"
    ],
    priority="critical",
    due_date="2025-12-01",
    estimated_hours=8,
    tags=["database", "setup", "critical"]
)

milestone1_id = m1["milestone_id"]  # Save this!

# Milestone 2: Data Import (depends on M1)
m2 = synergy_create_milestone(
    session_id=session_id,
    milestone_name="Data Import",
    description="Import existing customer data from old CRM",
    tasks=[
        {
            "task": "Export from old CRM",
            "subtasks": [
                "Connect to legacy system",
                "Export customer records",
                "Export transaction history"
            ]
        },
        {
            "task": "Clean and format data",
            "subtasks": [
                "Remove duplicates",
                "Standardize address formats",
                "Validate email addresses"
            ]
        },
        "Import to new database"
    ],
    priority="high",
    due_date="2025-12-08",
    estimated_hours=12,
    depends_on_milestone_id=milestone1_id,  # Can't start until M1 done
    tags=["migration", "data-cleaning"]
)

milestone2_id = m2["milestone_id"]

# Milestone 3: Integration
m3 = synergy_create_milestone(
    session_id=session_id,
    milestone_name="Integration & Testing",
    description="Connect database to forms and test workflows",
    tasks=[
        "Create Google Form for new entries",
        "Set up form-to-sheet integration",
        "Create automated email triggers",
        "Test complete workflow"
    ],
    priority="medium",
    due_date="2025-12-15",
    estimated_hours=6,
    depends_on_milestone_id=milestone2_id,
    tags=["integration", "testing"]
)

milestone3_id = m3["milestone_id"]
```

### Step 3: Work on Milestone 1
```python
# Create first resource
sheet = google_sheets_create(
    title="Customer Database",
    headers=["Name", "Email", "Phone", "Company", "Status"]
)

# Add document to milestone
synergy_update_milestone(
    milestone_id=milestone1_id,
    documents=[{
        "title": "Customer Database Sheet",
        "url": sheet["spreadsheet_url"],
        "type": "google_sheet"
    }]
)

# Create schema doc
doc = google_docs_create(
    title="Database Schema Design"
)

# Get existing docs and add new one
milestones = synergy_get_milestones(session_id=session_id)
m1_data = [m for m in milestones["milestones"] if m["milestone_id"] == milestone1_id][0]
existing_docs = m1_data.get("documents", [])

synergy_update_milestone(
    milestone_id=milestone1_id,
    documents=existing_docs + [{
        "title": "Schema Design Doc",
        "url": doc["document_url"],
        "type": "google_doc"
    }]
)

# Mark first task complete
# (This would typically be done via UI, but can be done programmatically)
synergy_update_task(
    task_id="task_xyz",  # Get from milestones data
    completed=True,
    actual_hours=2.5
)

# Mark milestone complete when all tasks done
synergy_update_milestone(
    milestone_id=milestone1_id,
    completed=True,
    actual_hours=7.5  # Total time spent
)
```

### Step 4: Continue with Next Milestones
```python
# Milestone 2 automatically unblocked now that M1 is complete
# (UI will show M2 is now available to work on)

# Work on milestone 2...
# Then milestone 3...
```

### Step 5: View Progress
```python
# Get all milestones to see progress
milestones = synergy_get_milestones(session_id=session_id)

for m in milestones["milestones"]:
    status = "✅ Complete" if m["completed"] else "⏳ In Progress"
    print(f"{m['milestone_number']}. {m['milestone_name']} - {status}")
    print(f"   Tasks: {m['task_count']} | Docs: {len(m.get('documents', []))}")
```

## Thread Linking

### Linking Conversations to Sessions
```python
# When creating session, current thread is auto-linked
result = synergy_create_session(
    title="Customer Database System",
    # thread_ids automatically includes current thread
)

# Manually link additional threads
synergy_update_session(
    session_id=session_id,
    thread_ids=["thread_abc123", "thread_def456", "thread_ghi789"]
)

# User can now see in UI:
# - Thread shows Synergy indicator
# - Session shows linked thread IDs
# - Click to navigate between conversation and project
```

### When to Link Threads
- Multi-conversation project (discussions span multiple sessions)
- Resuming work from different conversations
- Collaboration across team members
- Tracking which conversations contributed to which projects

## Priority Management

### Priority Levels
- **critical** - Blocking work, must be done ASAP
- **high** - Important, high urgency
- **medium** - Normal priority (default)
- **low** - Nice-to-have, low urgency

### Setting Priority
```python
# At milestone level
synergy_create_milestone(
    session_id=session_id,
    milestone_name="Security Audit",
    priority="critical"  # Blocks other work
)

# At task level
synergy_create_task(
    milestone_id=milestone_id,
    task="Fix SQL injection vulnerability",
    priority="critical"
)

# At subtask level
synergy_create_subtask(
    task_id=task_id,
    task="Update parameterized queries",
    priority="critical"
)

# Update priority later
synergy_update_milestone(
    milestone_id=milestone_id,
    priority="high"  # Downgrade from critical
)
```

## Dependency Tracking

### Milestone Dependencies
```python
# Milestone 2 depends on Milestone 1
synergy_create_milestone(
    milestone_name="Data Import",
    depends_on_milestone_id=milestone1_id  # Can't start until M1 done
)

# UI shows:
# - M2 is "blocked by M1"
# - M2 automatically unblocks when M1 marked complete
```

### Task Dependencies
```python
# Task B depends on Task A
synergy_create_task(
    milestone_id=milestone_id,
    task="Deploy to production",
    depends_on_task_id=test_task_id  # Must pass tests first
)
```

## Blocking and Blockers

### Setting Blockers
```python
# Block milestone
synergy_update_milestone(
    milestone_id=milestone_id,
    blocked=True,
    blocker_reason="Waiting for API credentials from vendor"
)

# Block task
synergy_update_task(
    task_id=task_id,
    blocked=True,
    blocker_reason="Need design approval before coding"
)

# Unblock when resolved
synergy_update_milestone(
    milestone_id=milestone_id,
    blocked=False,
    blocker_reason=None  # Clear reason
)
```

### Blocker Types (for tasks)
- **internal** - Blocked by something in your control
- **external** - Waiting on outside party
- **dependency** - Waiting for another task/milestone
- **approval** - Waiting for sign-off

## Document Management at Milestone Level

### Milestone-Specific Documents
```python
# Add documents to milestone (not session)
synergy_update_milestone(
    milestone_id=milestone_id,
    documents=[
        {
            "title": "Phase 1 Design Spec",
            "url": "https://docs.google.com/...",
            "type": "google_doc"
        },
        {
            "title": "Database Schema Diagram",
            "url": "https://drive.google.com/...",
            "type": "pdf"
        }
    ]
)

# These appear ONLY in this milestone's documents
# Session-level documents appear across all milestones
```

### Internal Document Integration
```python
# Create internal doc linked to milestone
doc = synergy_create_internal_doc(
    session_id=session_id,
    title="Milestone 1 Summary",
    content="# Milestone 1 Complete\n\n## Achievements...",
    linked_milestone_id=milestone1_id  # Links to specific milestone
)

# Doc appears in milestone's document list
```

## Time Tracking

### Setting Estimates
```python
# At milestone level
synergy_create_milestone(
    milestone_name="API Development",
    estimated_hours=40  # Total for milestone
)

# At task level
synergy_create_task(
    milestone_id=milestone_id,
    task="Implement authentication endpoint",
    estimated_hours=8
)

# At subtask level
synergy_create_subtask(
    task_id=task_id,
    task="Write unit tests",
    estimated_hours=2
)
```

### Recording Actuals
```python
# When completing
synergy_update_task(
    task_id=task_id,
    completed=True,
    actual_hours=9.5  # Took longer than estimate
)

# Milestone actual_hours auto-calculates from task actuals
```

## Best Practices

### 1. Plan Milestones First
```python
# Bad: Create milestone as you go
# Good: Plan all milestones upfront

# Create session
session = synergy_create_session(title="Project X")

# Create ALL milestones at once
m1 = synergy_create_milestone(...)
m2 = synergy_create_milestone(...)
m3 = synergy_create_milestone(...)

# Then work through them in order
```

### 2. Use Clear Naming
```python
# Bad names
synergy_create_milestone(milestone_name="Part 1")
synergy_create_milestone(milestone_name="Step 2")

# Good names
synergy_create_milestone(milestone_name="Database Setup & Schema Design")
synergy_create_milestone(milestone_name="Customer Data Import from Legacy CRM")
```

### 3. Set Realistic Dependencies
```python
# Bad: Too many dependencies (overly complex)
# Good: Only critical path dependencies

# Example: Only set dependency if MUST complete first
synergy_create_milestone(
    milestone_name="Production Deployment",
    depends_on_milestone_id=testing_milestone_id  # Can't deploy before testing
)

# Don't set dependency for parallel work
```

### 4. Keep Tasks Focused
```python
# Bad: Huge task with many steps
synergy_create_task(
    task="Build entire authentication system"
)

# Good: Break into focused tasks with subtasks
synergy_create_task(
    task="Implement user login endpoint",
    subtasks=["Create route", "Add validation", "Write tests"]
)
synergy_create_task(
    task="Implement password reset flow",
    subtasks=["Email template", "Token generation", "Reset endpoint"]
)
```

### 5. Update Documents Immediately
```python
# Bad: Create many resources, update once at end
# (Risk losing track of what was created)

# Good: Update after EACH resource
sheet = google_sheets_create(...)
synergy_update_milestone(milestone_id=m_id, documents=[...])

form = google_forms_create(...)
synergy_update_milestone(milestone_id=m_id, documents=[...])  # Fetch existing first!
```

## Common Patterns

### Pattern 1: Sequential Phases
```
Phase 1 (Planning) → Phase 2 (Development) → Phase 3 (Testing) → Phase 4 (Deployment)
Each depends on previous completing
```

### Pattern 2: Parallel Streams
```
Frontend Milestone (no dependencies)
Backend Milestone  (no dependencies)
Integration Milestone (depends on both)
```

### Pattern 3: Iterative Sprints
```
Sprint 1 Milestone → Sprint 2 Milestone → Sprint 3 Milestone
Each has similar task structure, no hard dependencies
```

Next: Call synergy_agent_instructions("troubleshooting") for common issues
        """,
        
        "smart_tool_milestones": """
# Smart Project Tracker with Milestones - Complete Guide

## Overview

The `synergy_smart_project_tracker()` tool can create complete multi-phase projects with milestones in **ONE CALL**. This is the EASIEST way to set up structured projects.

## When to Use Smart Tool with Milestones

✅ **Use smart tool with milestones when:**
- Multi-phase project (3+ major stages)
- Clear phase separation (Setup → Development → Testing)
- Need dependencies between phases
- Want phase-specific documents
- Time tracking per phase
- Different priorities per phase

✅ **Use smart tool WITHOUT milestones (flat) when:**
- Simple linear workflow
- Single phase project
- Quick tasks list
- No phase dependencies needed

## Step-by-Step: Create Milestone Project in ONE Call

### 1. Plan Your Milestones

Before calling, decide:
- What are the major phases? (3-5 is ideal)
- What tasks in each phase?
- Any subtasks needed?
- Dependencies between phases?
- Time estimates?

### 2. Call Smart Tool with Milestones

```python
result = synergy_smart_project_tracker(
    title="Customer Database Migration",
    description="Multi-phase migration from legacy CRM to Google Sheets",
    platforms_involved=["sheets", "forms", "gmail", "drive"],
    priority="critical",
    start_in_column="in_progress",
    tags=["migration", "database", "multi-phase"],
    
    # KEY: Set use_milestones=True
    use_milestones=True,
    
    # KEY: Provide initial_milestones array
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
            "description": "Connect forms and test complete workflow",
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

# Save these!
session_id = result["session_id"]
milestones_created = result["milestones_created"]

# Extract milestone IDs for later use
m1_id = milestones_created[0]["milestone_id"]
m2_id = milestones_created[1]["milestone_id"]
m3_id = milestones_created[2]["milestone_id"]
```

### 3. What Gets Created

The smart tool automatically creates:
- ✅ Synergy session with `uses_milestones=True`
- ✅ All milestones with their metadata
- ✅ All tasks within each milestone
- ✅ All subtasks within tasks
- ✅ Complete project structure in ONE call

### 4. Work on Phase 1

```python
# Create your resources
sheet = google_sheets_create(
    title="Customer Database",
    headers=["Name", "Email", "Phone", "Company", "Status"]
)

# Add to Phase 1 milestone
synergy_update_milestone(
    milestone_id=m1_id,
    documents=[{
        "title": "Customer Database Sheet",
        "url": sheet["spreadsheet_url"],
        "type": "google_sheet"
    }]
)

# Complete Phase 1 when done
synergy_update_milestone(
    milestone_id=m1_id,
    completed=True,
    actual_hours=7.5
)
```

### 5. Phase 2 Automatically Unblocked

If Phase 2 depends on Phase 1, it's automatically unblocked when Phase 1 completes!

### 6. Continue Through All Phases

Work through each milestone, adding documents and completing tasks.

## Complete Example: E-commerce Integration

```python
result = synergy_smart_project_tracker(
    title="E-commerce Order Processing System",
    platforms_involved=["shopify", "gmail", "sheets", "slack"],
    priority="high",
    use_milestones=True,
    initial_milestones=[
        {
            "milestone_name": "Setup Phase",
            "description": "Configure all platforms and connections",
            "tasks": [
                "Connect to Shopify API",
                "Set up Gmail integration",
                {
                    "task": "Create tracking spreadsheet",
                    "subtasks": [
                        "Design columns",
                        "Add formulas",
                        "Create charts"
                    ]
                }
            ],
            "priority": "critical",
            "estimated_hours": 6,
            "tags": ["setup", "configuration"]
        },
        {
            "milestone_name": "Automation Phase",
            "description": "Build order processing automation",
            "tasks": [
                "Create order webhook handler",
                "Set up email notifications",
                "Configure Slack alerts"
            ],
            "priority": "high",
            "estimated_hours": 10,
            "tags": ["automation", "development"]
        },
        {
            "milestone_name": "Testing & Deployment",
            "description": "Test and launch system",
            "tasks": [
                "Test with sample orders",
                "Fix any issues",
                "Deploy to production"
            ],
            "priority": "medium",
            "estimated_hours": 4,
            "tags": ["testing", "deployment"]
        }
    ]
)
```

## Flat vs Milestone Structure Comparison

### Flat Structure (use_milestones=False)
```python
synergy_smart_project_tracker(
    title="Quick Email Setup",
    platforms_involved=["gmail", "sheets"],
    next_steps=[
        "Create email template",
        "Create tracking sheet",
        "Test automation"
    ],
    use_milestones=False  # or omit (default is False)
)
```

**Best for:**
- Simple projects (3-10 steps)
- Single phase work
- No dependencies
- Quick tasks

### Milestone Structure (use_milestones=True)
```python
synergy_smart_project_tracker(
    title="Multi-Phase Migration",
    platforms_involved=["sheets", "forms", "gmail"],
    use_milestones=True,
    initial_milestones=[
        {"milestone_name": "Phase 1", "tasks": [...]},
        {"milestone_name": "Phase 2", "tasks": [...]},
        {"milestone_name": "Phase 3", "tasks": [...]}
    ]
)
```

**Best for:**
- Complex projects (3+ phases)
- Clear stage separation
- Dependencies between phases
- Phase-specific documents
- Time tracking per phase

## initial_milestones Structure Reference

```python
{
    "milestone_name": str,              # Required - Phase name
    "description": str,                 # Optional - What this phase does
    "tasks": [                          # Required - Array of tasks
        "Simple task string",           # Can be simple string
        {                               # Or object with subtasks
            "task": "Complex task",
            "subtasks": [
                "Subtask 1",
                "Subtask 2"
            ]
        }
    ],
    "priority": "low|medium|high|critical",  # Optional - Default: medium
    "due_date": "YYYY-MM-DD",           # Optional - ISO format
    "estimated_hours": 8.5,             # Optional - Time estimate
    "tags": ["tag1", "tag2"],           # Optional - For filtering
    "depends_on_milestone_id": "m_id",  # Optional - Blocks until dependency done
    "color_hex": "#FF5733"              # Optional - Visual color coding
}
```

## Best Practices

### 1. Plan Milestones First
Think through your phases before calling the smart tool. You can't easily restructure later.

### 2. Keep Milestones Focused
- 3-5 milestones is ideal
- Each milestone = one major phase
- Don't create milestones for tiny steps

### 3. Use Clear Names
```python
# Good milestone names
"Phase 1: Database Setup"
"Phase 2: Data Import"
"Phase 3: Integration"

# Bad milestone names
"First Part"
"Do Stuff"
"Other Things"
```

### 4. Set Realistic Time Estimates
```python
"estimated_hours": 8,  # Good - specific estimate
"estimated_hours": 100,  # Bad - too vague/large
```

### 5. Save Milestone IDs
```python
milestones = result["milestones_created"]
phase1_id = milestones[0]["milestone_id"]
phase2_id = milestones[1]["milestone_id"]

# Use these IDs for updates later!
```

## Common Mistakes

❌ **Creating too many milestones**
```python
# Bad: 15 milestones for small project
# Good: 3-5 major phases
```

❌ **Forgetting to save milestone IDs**
```python
# Bad
result = synergy_smart_project_tracker(...)
# Don't extract IDs - can't update later!

# Good
milestones = result["milestones_created"]
m1_id = milestones[0]["milestone_id"]
```

❌ **Using flat structure for complex project**
```python
# Bad: Trying to track multi-phase project with flat next_steps
synergy_smart_project_tracker(
    title="Complex 6-Month Migration",
    next_steps=[...50 steps...],  # Hard to organize!
    use_milestones=False
)

# Good: Use milestones for structured phases
```

❌ **Mixing structures**
```python
# Bad: Can't do this!
synergy_smart_project_tracker(
    use_milestones=True,
    initial_milestones=[...],
    next_steps=[...]  # ← Error! Pick one structure
)
```

## Advantages of Smart Tool with Milestones

1. **One Call = Complete Project**
   - No need for multiple API calls
   - Atomically creates everything
   - Faster and simpler

2. **Automatic Structure Validation**
   - Tool validates milestone structure
   - Ensures tasks array exists
   - Prevents common errors

3. **Consistent Project Setup**
   - Same pattern every time
   - Easy to learn and remember
   - Less room for mistakes

4. **Immediate Usability**
   - Project ready to use immediately
   - All milestones created
   - All tasks and subtasks ready

## When NOT to Use Smart Tool with Milestones

❌ **When structure might change frequently**
- Use flat structure for flexibility
- Add/remove steps easily

❌ **When you don't know phases upfront**
- Start with flat structure
- Convert to milestones later if needed

❌ **For very simple projects (1-3 steps)**
- Milestones add unnecessary complexity
- Flat structure is simpler

## Summary

The `synergy_smart_project_tracker()` with `use_milestones=True` is the **EASIEST and FASTEST** way to create structured multi-phase projects in Synergy.

**Key Points:**
- Set `use_milestones=True`
- Provide `initial_milestones` array
- Save returned milestone IDs
- Work through phases sequentially
- Update milestones with documents as you create resources
- Complete milestones to unblock dependencies

Next: Call synergy_agent_instructions("milestones") for detailed milestone operations
        """,
        
        "troubleshooting": """
# Synergy Troubleshooting Guide

## Common Issues & Solutions

### Issue 1: Documents Not Showing on Dashboard
**Symptoms:** Dashboard shows "0 documents" but you created resources

**Cause:** Forgot to update session after creating resources

**Solution:**
```python
# After creating ANY resource:
session = synergy_get_session(session_id)
synergy_update_session(
    session_id=session_id,
    documents=session["session"]["documents"] + [new_doc]
)
```

---

### Issue 2: Documents Disappeared
**Symptoms:** Dashboard had 15 documents, now has 1

**Cause:** Updated documents without fetching existing ones first (array replacement)

**Solution:**
```python
# ALWAYS fetch first
session = synergy_get_session(session_id)
existing = session["session"]["documents"]

# Then update with ALL
synergy_update_session(
    session_id=session_id,
    documents=existing + [new_doc]
)
```

**Recovery:** If already lost, you'll need to manually re-add URLs

---

### Issue 3: "'str' object has no attribute 'copy'"
**Symptoms:** Tool execution fails with .copy() error

**Cause:** Bug in synergy.py (fixed in latest version)

**Solution:** ✅ Already fixed - documents/links now handle string inputs

---

### Issue 4: Documents Have Wrong Field Names
**Symptoms:** Document "name" shows as blank, or "title" not working

**Cause:** Field name inconsistency - use "name" not "title"

**Solution:**
```python
# ✅ CORRECT
document = {
    "name": "My Document",
    "url": "https://...",
    "type": "google_doc"
}

# ❌ WRONG
document = {
    "title": "My Document",
    ...
}
```

---

### Issue 5: Checklist Items Not Showing
**Symptoms:** Checklist shows empty but you added items

**Cause:** Used "item" or "text" field instead of "task"

**Solution:**
```python
# ✅ CORRECT
checklist_item = {
    "task": "Complete onboarding",
    "completed": false
}

# ❌ WRONG
checklist_item = {
    "item": "Complete onboarding",
    ...
}
```

---

### Issue 6: Can't Check Next Steps
**Symptoms:** Next steps show but checkboxes don't work

**Cause:** Next steps are strings, not objects

**Solution:**
```python
# Strings can't be checked:
next_steps = ["Step 1", "Step 2"]  # ❌ Not checkable

# Objects can be checked:
next_steps = [
    {"description": "Step 1", "completed": false},
    {"description": "Step 2", "completed": false}
]  # ✅ Checkable
```

---

### Issue 7: Session ID Lost
**Symptoms:** Can't update project because don't have session_id

**Cause:** Didn't save session_id after creation

**Solution:**
```python
# Find via list
sessions = synergy_list_sessions()
matching = [s for s in sessions if "project name" in s["title"].lower()]
session_id = matching[0]["session_id"]
```

**Prevention:** ALWAYS save session_id immediately after creation

---

### Issue 8: Dashboard Doesn't Update
**Symptoms:** Made changes but dashboard still shows old data

**Cause:** Browser cache or need to refresh

**Solution:**
1. Hard refresh: Ctrl+Shift+R (Windows) or Cmd+Shift+R (Mac)
2. Check Flask server is running
3. Verify update succeeded (check tool response)

---

### Issue 9: Tool Returns 404 or 500 Error
**Symptoms:** Synergy tools fail with HTTP errors

**Cause:** Flask server not running or database issue

**Solution:**
1. Check server is running
2. Restart server: `BISTART` command
3. Check database: Verify `data/synergy_sessions.db` exists

---

### Issue 10: Syncing to Google Doesn't Work
**Symptoms:** `sync_google_tasks=True` but no Google Task created

**Cause:** Feature incomplete in backend

**Solution:** Don't rely on Google sync yet - use Synergy dashboard only

---

## Debugging Checklist

When Synergy isn't working:

- [ ] Flask server running?
- [ ] Saved session_id after creation?
- [ ] Fetching existing data before updating arrays?
- [ ] Using correct field names? ("name" for docs, "task" for checklist)
- [ ] Updating session after EACH resource creation?
- [ ] Hard refreshed dashboard? (Ctrl+Shift+R)
- [ ] Checked tool response for errors?
- [ ] Verified database file exists? (data/synergy_sessions.db)

Next: Call synergy_agent_instructions("examples") for working patterns
        """,
        
        "examples": """
# Synergy Real-World Examples

## Example 1: Email Marketing Campaign

### Scenario
Create email campaign with template, tracking sheet, and form

### Code
```python
# 1. Create project
result = synergy_smart_project_tracker(
    title="Q4 Email Marketing Campaign",
    platforms_involved=["gmail", "sheets", "forms"],
    next_steps=[
        "Design email template",
        "Create tracking spreadsheet",
        "Set up feedback form"
    ],
    priority="high"
)
session_id = result["session_id"]

# 2. Create email template
template = gmail_create_draft(
    subject="Q4 Special Offers",
    body="..."
)

# 3. Update Synergy
session = synergy_get_session(session_id)
synergy_update_session(
    session_id=session_id,
    documents=session["session"]["documents"] + [{
        "name": "Q4 Email Template",
        "url": template["draft_url"],
        "type": "email"
    }]
)

# 4. Create tracking sheet
sheet = google_sheets_create(
    title="Q4 Campaign Tracker",
    headers=["Date", "Recipient", "Opened", "Clicked", "Converted"]
)

# 5. Update Synergy
session = synergy_get_session(session_id)
synergy_update_session(
    session_id=session_id,
    documents=session["session"]["documents"] + [{
        "name": "Campaign Tracker",
        "url": sheet["spreadsheet_url"],
        "type": "google_sheet"
    }]
)

# 6. Create feedback form
form = google_forms_create(
    title="Campaign Feedback",
    questions=[...]
)

# 7. Update Synergy
session = synergy_get_session(session_id)
synergy_update_session(
    session_id=session_id,
    documents=session["session"]["documents"] + [{
        "name": "Feedback Form",
        "url": form["formUrl"],
        "type": "google_form"
    }]
)

# 8. Mark complete
synergy_move_session(session_id, "done")
```

---

## Example 2: Client Onboarding Automation

### Scenario
Automate new client setup with docs, calendar, and tasks

### Code
```python
# 1. Create project with detailed checklist
result = synergy_smart_project_tracker(
    title="Client Onboarding - Acme Corp",
    platforms_involved=["gmail", "docs", "calendar", "forms"],
    next_steps=[
        "Send welcome email",
        "Create project doc",
        "Schedule kickoff meeting",
        "Send onboarding form"
    ],
    checklist=[
        {
            "task": "Documentation",
            "completed": false,
            "subtasks": [
                {"task": "Create NDA", "completed": false},
                {"task": "Create project brief", "completed": false},
                {"task": "Share drive folder", "completed": false}
            ]
        },
        {
            "task": "Communication",
            "completed": false,
            "subtasks": [
                {"task": "Send welcome email", "completed": false},
                {"task": "Schedule kickoff", "completed": false},
                {"task": "Add to Slack", "completed": false}
            ]
        }
    ],
    priority="high",
    due_date="2025-11-12",
    assignees=["John Doe", "jane@example.com"]
)
session_id = result["session_id"]

# 2. Send welcome email
gmail_send_email(
    to="client@acme.com",
    subject="Welcome to Our Platform",
    body="..."
)

# 3. Create project doc
doc = google_docs_create(
    title="Acme Corp - Project Brief"
)

# 4. Update Synergy with both
session = synergy_get_session(session_id)
synergy_update_session(
    session_id=session_id,
    documents=session["session"]["documents"] + [
        {
            "name": "Welcome Email",
            "url": "gmail://sent/...",
            "type": "email"
        },
        {
            "name": "Project Brief",
            "url": doc["documentUrl"],
            "type": "google_doc"
        }
    ]
)

# 5. Schedule meeting
event = google_calendar_create_event(
    title="Kickoff Meeting - Acme Corp",
    start_time="2025-11-10T10:00:00Z",
    duration_minutes=60
)

# 6. Update Synergy
session = synergy_get_session(session_id)
synergy_update_session(
    session_id=session_id,
    documents=session["session"]["documents"] + [{
        "name": "Kickoff Meeting",
        "url": event["event_url"],
        "type": "calendar_event"
    }]
)
```

---

## Example 3: Research Project

### Scenario
Research topic across multiple sources with findings doc

### Code
```python
# 1. Create research project
result = synergy_smart_project_tracker(
    title="Market Research - AI Tools",
    platforms_involved=["web_search", "docs", "sheets"],
    next_steps=[
        "Search for AI tools",
        "Analyze competitors",
        "Create findings doc",
        "Build comparison sheet"
    ],
    tags=["research", "ai", "market-analysis"]
)
session_id = result["session_id"]

# 2. Perform web searches
results1 = web_search("AI automation tools 2025")
results2 = web_search("AI agent platforms comparison")

# 3. Create findings doc
doc = google_docs_create(
    title="AI Tools Market Research - Findings"
)

# Add research to doc
google_docs_append_text(
    document_id=doc["documentId"],
    text="Research Findings:\n\n" + results1["content"]
)

# 4. Create comparison sheet
sheet = google_sheets_create(
    title="AI Tools Comparison",
    headers=["Tool", "Features", "Pricing", "Rating"]
)

# 5. Update Synergy with all resources
session = synergy_get_session(session_id)
synergy_update_session(
    session_id=session_id,
    documents=session["session"]["documents"] + [
        {
            "name": "Market Research Findings",
            "url": doc["documentUrl"],
            "type": "google_doc"
        },
        {
            "name": "Tool Comparison Sheet",
            "url": sheet["spreadsheet_url"],
            "type": "google_sheet"
        }
    ],
    links=[
        {"title": "Source 1", "url": results1["sources"][0]["url"]},
        {"title": "Source 2", "url": results2["sources"][0]["url"]}
    ]
)

# 6. Move to review
synergy_move_session(session_id, "review")
```

---

## Example 4: Resuming Work Across Conversations

### Scenario
User returns days later asking to continue project

### Code
```python
# User: "Continue work on the email campaign"

# 1. Search for project
sessions = synergy_list_sessions(status="active")
campaign = [s for s in sessions if "email campaign" in s["title"].lower()]

if not campaign:
    # Ask user for clarification
    "I don't see an active email campaign project. Which project did you mean?"
else:
    # 2. Get project details
    session_id = campaign[0]["session_id"]
    session = synergy_get_session(session_id)
    
    # 3. Review current state
    docs = session["session"]["documents"]
    next_steps = session["session"]["next_steps"]
    
    # 4. Report to user
    f\"\"\"
    Found project: {session["session"]["title"]}
    
    Current Status: {session["session"]["kanban_column"]}
    Resources Created: {len(docs)}
    
    Completed Steps:
    {[step for step in next_steps if step.get("completed")]}
    
    Remaining Steps:
    {[step for step in next_steps if not step.get("completed")]}
    
    What would you like to do next?
    \"\"\"
```

---

## Pattern Summary

### Always Do
1. Create Synergy project FIRST
2. Save session_id immediately
3. Fetch existing data before updating arrays
4. Update after EACH resource creation
5. Use correct field names (name, task)
6. Tell user about created resources

### Never Do
1. Update arrays without fetching existing
2. Forget to update after creating resources
3. Lose session_id
4. Use wrong field names (title, item)
5. Assume sync features work

### Best Practices
1. Start every multi-platform project with Synergy
2. Keep dashboard updated in real-time
3. Use descriptive titles and tags
4. Add notes for important decisions
5. Move through Kanban columns as you progress
6. Tell user when project is complete

---

End of Instructions. Call synergy_agent_instructions("overview") to return to main menu.
        """
    }
    
    return {
        "success": True,
        "topic": topic,
        "guide": guides.get(topic, guides["overview"])
    }

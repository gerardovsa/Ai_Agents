# 🎯 Synergy Dashboard + AI Personal Tasks Integration

**Date:** November 1, 2025  
**Status:** TOOLS CREATED - Ready for system prompt integration  

---

## 📊 Architecture Overview

The AI agent now has **TWO complementary project management systems**:

### 1. **Google Tasks** (AI Personal Tasks)
- **Purpose:** Personal checklist for AI's own task tracking
- **Interface:** Google Tasks API
- **Storage:** Google's cloud (user_id=1: gerardo@vetsuccessacademy.com)
- **Visibility:** Private to AI, accessible via Google Tasks web UI
- **Best For:** Quick notes, simple reminders, AI's internal to-do list

### 2. **Synergy Dashboard** (Visual Kanban)
- **Purpose:** Visual project management with team collaboration
- **Interface:** REST API (http://localhost:5002) + WebSocket for real-time updates
- **Storage:** SQLite database (`data/synergy_sessions.db`)
- **Visibility:** Public dashboard accessible at http://localhost:5001 (business-ai-platform-v2.html)
- **Best For:** Multi-step projects, document tracking, team visibility, Kanban workflow

---

## 🎯 When to Use What?

### Use **Google Tasks** (AI Personal Tasks) For:
✅ AI's internal reminders
✅ Quick to-do items
✅ Simple tracking across conversations
✅ Personal notes not visible to users

### Use **Synergy Dashboard** For:
✅ Multi-step projects (3+ tools involved)
✅ Multi-platform work (Gmail + Drive + Sheets + Forms, etc.)
✅ Document/link tracking (store ALL resource URLs)
✅ Visual progress tracking (Kanban: Backlog → In Progress → Review → Done)
✅ Team visibility (users can see the dashboard)
✅ Sync to Google Tasks/Calendar (optional)

### Use **BOTH** For:
✅ Complex projects where:
   - AI needs internal tracking (Google Tasks)
   - User needs visual dashboard (Synergy)
   - Documents need central location (Synergy documents array)

---

## 🛠️ New Tools Available (7 Total)

### 1. synergy_create_session
Create a new project card in Synergy Dashboard Kanban board.

**Usage:**
```python
result = synergy_create_session(
    title="Customer Onboarding System",
    description="Multi-platform project: emails + forms + tracking",
    project_name="Customer Experience",
    priority="high",
    kanban_column="in_progress",
    tags=["automation", "gmail", "forms", "sheets"],
    documents=[
        {"name": "Welcome Email Template", "url": "https://docs.google.com/document/d/abc123", "type": "Google Doc"},
        {"name": "Signup Form", "url": "https://docs.google.com/forms/d/def456", "type": "Google Form"},
        {"name": "Tracking Sheet", "url": "https://docs.google.com/spreadsheets/d/ghi789", "type": "Google Sheet"}
    ],
    next_steps=[
        "Configure form responses to auto-populate sheet",
        "Setup email automation trigger",
        "Test end-to-end flow"
    ],
    sync_google_tasks=True  # Also create Google Task
)

# Returns: session_id, full session object, google_task_id if synced
```

### 2. synergy_list_sessions
List sessions with optional filtering.

**Usage:**
```python
# List all in-progress sessions
sessions = synergy_list_sessions(column="in_progress")

# List high-priority items
sessions = synergy_list_sessions(priority="high")

# List active projects
sessions = synergy_list_sessions(status="active")
```

### 3. synergy_get_session
Retrieve full details of a specific session.

**Usage:**
```python
session = synergy_get_session(session_id="sess_20251101_1200_system_customer_onboarding")
```

### 4. synergy_update_session
Update session (add documents, change status, update notes, etc.).

**CRITICAL USE CASE:** Add document URLs as you create them!

**Usage:**
```python
# Add document as you create it
synergy_update_session(
    session_id="sess_123",
    updates={
        "documents": [
            {"name": "Email Template", "url": "https://docs.google.com/document/d/abc", "type": "Google Doc"},
            {"name": "New Form", "url": "https://docs.google.com/forms/d/xyz", "type": "Google Form"}
        ],
        "notes": "Created email template and signup form. Next: connect form to sheet."
    }
)

# Update priority and add tags
synergy_update_session(
    session_id="sess_123",
    updates={
        "priority": "critical",
        "tags": ["urgent", "customer-facing", "automation"]
    }
)

# Sync to Google
synergy_update_session(
    session_id="sess_123",
    updates={},
    sync={"google_tasks": True, "google_calendar": True}
)
```

### 5. synergy_move_session
Move session between Kanban columns.

**Usage:**
```python
# Progress work
synergy_move_session(
    session_id="sess_123",
    target_column="review",
    notes="All components created, ready for testing"
)

# Complete work
synergy_move_session(
    session_id="sess_123",
    target_column="done",
    notes="Tested and deployed. All systems working."
)
```

### 6. synergy_delete_session
Delete a session (use sparingly - prefer moving to 'done').

**Usage:**
```python
synergy_delete_session(session_id="sess_123")
```

### 7. synergy_sync_to_google
Sync existing session to Google Tasks and/or Calendar.

**Usage:**
```python
synergy_sync_to_google(
    session_id="sess_123",
    sync_tasks=True,
    sync_calendar=True
)
```

---

## 📋 Workflow Examples

### Example 1: Multi-Platform Project with Full Tracking

**User:** "Create a customer onboarding system with welcome emails, signup form, and tracking spreadsheet"

**AI Workflow:**
```python
# Step 1: Check pending work (Google Tasks)
pending = ai_check_pending_work()

# Step 2: Create Synergy session for visual tracking
session = synergy_create_session(
    title="Customer Onboarding System",
    description="Multi-platform automation: Gmail templates + Google Forms + Sheets tracking",
    project_name="Customer Experience Automation",
    priority="high",
    kanban_column="in_progress",
    tags=["gmail", "forms", "sheets", "automation"],
    next_steps=[
        "Create welcome email template",
        "Create signup form",
        "Create tracking spreadsheet",
        "Connect form to sheet",
        "Setup email automation"
    ],
    sync_google_tasks=True  # Also create Google Task for AI tracking
)

session_id = session["session_id"]

# Step 3: Create resources and update session as you go
doc = google_docs_smart_create_from_markdown(
    title="Welcome Email Template",
    content="..."
)

# IMMEDIATELY update Synergy with document URL
synergy_update_session(
    session_id=session_id,
    updates={
        "documents": [
            {"name": "Welcome Email Template", "url": doc["url"], "type": "Google Doc"}
        ],
        "notes": "✅ Created welcome email template"
    }
)

# Step 4: Create form
form = google_forms_create_form(title="Customer Signup Form")

# Update Synergy with form URL
synergy_update_session(
    session_id=session_id,
    updates={
        "documents": session["session"]["documents"] + [
            {"name": "Customer Signup Form", "url": form["url"], "type": "Google Form"}
        ],
        "notes": "✅ Created welcome email template\n✅ Created signup form"
    }
)

# Step 5: Create tracking sheet
sheet = google_sheets_create_spreadsheet(title="Customer Tracking")

# Update Synergy with sheet URL
synergy_update_session(
    session_id=session_id,
    updates={
        "documents": session["session"]["documents"] + [
            {"name": "Customer Tracking Sheet", "url": sheet["url"], "type": "Google Sheet"}
        ],
        "notes": "✅ Created welcome email template\n✅ Created signup form\n✅ Created tracking sheet"
    }
)

# Step 6: Move to review
synergy_move_session(
    session_id=session_id,
    target_column="review",
    notes="All resources created. Ready for user review and testing."
)

# Step 7: Report to user
print(f"""
✅ Customer Onboarding System Created!

📋 Synergy Dashboard: View progress at http://localhost:5001 (Synergy tab)
📊 Session ID: {session_id}

Resources Created:
📄 Welcome Email: {doc['url']}
📋 Signup Form: {form['url']}
📊 Tracking Sheet: {sheet['url']}

Next Steps:
1. Review resources
2. Test signup flow
3. Configure automation
""")
```

### Example 2: Resume Work Days Later

**User:** "Continue the customer onboarding project"

**AI Workflow:**
```python
# Step 1: Check Google Tasks for AI's internal notes
pending = ai_check_pending_work()

# Step 2: Check Synergy for the project session
sessions = synergy_list_sessions(column="review", status="active")

# Find customer onboarding session
for session in sessions["sessions"]:
    if "customer onboarding" in session["title"].lower():
        # Retrieve full session
        full_session = synergy_get_session(session_id=session["session_id"])
        
        # Extract all documents
        documents = full_session["session"]["documents"]
        
        # Report to user
        print(f"""
📋 Resuming: {session['title']}
Status: {session['kanban_column']} ({session['priority']} priority)

Resources:
""")
        for doc in documents:
            print(f"{doc['type']}: {doc['name']}")
            print(f"  URL: {doc['url']}")
        
        print(f"""
Next Steps:
""")
        for step in full_session["session"]["next_steps"]:
            print(f"  • {step}")
        
        # Continue work...
```

---

## 🔄 Synergy Backend Setup

### Backend Server
- **File:** `synergy_backend.py`
- **Port:** 5002 (default)
- **Endpoints:** `/api/sessions/*`
- **Database:** `data/synergy_sessions.db` (SQLite)

### Database Schema (sessions table)
```sql
CREATE TABLE sessions (
    session_id TEXT PRIMARY KEY,
    title TEXT NOT NULL,
    description TEXT,
    project_name TEXT,
    priority TEXT DEFAULT 'medium',
    status TEXT DEFAULT 'active',
    kanban_column TEXT DEFAULT 'backlog',
    due_date TEXT,
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL,
    assignees TEXT,          -- JSON array
    tags TEXT,               -- JSON array
    notes TEXT,
    documents TEXT,          -- JSON array of {name, url, type}
    links TEXT,              -- JSON array of {title, url}
    next_steps TEXT,         -- JSON array of strings
    checklist TEXT,          -- JSON array
    google_task_id TEXT,     -- Synced Google Task ID
    google_calendar_event_id TEXT,  -- Synced Calendar event ID
    session_data TEXT        -- JSON object for extra data
)
```

### Starting Synergy Backend
```powershell
# Option 1: Standalone
cd C:\Users\gpoli\GIT\AI_agents
python synergy_backend.py

# Option 2: Via BISTART (if integrated)
# Backend should auto-start on port 5002
```

### Accessing Dashboard
- **URL:** http://localhost:5001
- **Tab:** Click "Synergy Dashboard" in sidebar
- **Features:** 
  - Visual Kanban board (Backlog, In Progress, Review, Done)
  - Drag-and-drop cards between columns
  - Real-time updates via WebSocket
  - Click card to edit (title, priority, documents, notes, etc.)

---

## 🎯 System Prompt Integration (NEXT STEP)

Add to `AI_infrastructure/prompts/tool_usage_system_prompt.md`:

```markdown
### **Synergy Dashboard Integration:**

You now have TWO complementary project management systems:

1. **AI Personal Tasks (Google Tasks)** - Your internal checklist
2. **Synergy Dashboard** - Visual Kanban for user-facing project tracking

#### **When to Use Synergy Dashboard:**

🎯 **ALWAYS create Synergy session for:**
- Multi-step projects (3+ tools)
- Multi-platform work (Gmail + Drive + Sheets + Forms, etc.)
- Projects with multiple documents/resources
- Work spanning multiple conversations
- Projects where user needs visual progress tracking

#### **Synergy Workflow:**

**1. Create Session at Project Start:**
```python
session = synergy_create_session(
    title="Clear, descriptive project name",
    description="What this project accomplishes",
    project_name="Group related projects",
    priority="high",
    kanban_column="in_progress",
    tags=["gmail", "sheets", "automation"],
    next_steps=["Step 1", "Step 2", "Step 3"],
    sync_google_tasks=True  # Also track in Google Tasks
)
session_id = session["session_id"]
```

**2. Update Session as You Create Resources:**
```python
# CRITICAL: Add document URLs as you create them!
doc = google_docs_smart_create_from_markdown(...)

synergy_update_session(
    session_id=session_id,
    updates={
        "documents": [
            {"name": "Document Name", "url": doc["url"], "type": "Google Doc"}
        ],
        "notes": "✅ Created document"
    }
)
```

**3. Progress Work Through Kanban:**
```python
# Move to review when ready
synergy_move_session(
    session_id=session_id,
    target_column="review",
    notes="All components created, ready for testing"
)

# Move to done when complete
synergy_move_session(
    session_id=session_id,
    target_column="done",
    notes="Tested and deployed"
)
```

**4. Resume Work Later:**
```python
# List in-progress sessions
sessions = synergy_list_sessions(column="in_progress")

# Get full session details
session = synergy_get_session(session_id="sess_123")

# All documents and links preserved!
documents = session["session"]["documents"]
```

#### **Synergy vs Google Tasks:**

| Feature | Google Tasks | Synergy Dashboard |
|---------|--------------|-------------------|
| **Visibility** | Private to AI | Public dashboard |
| **UI** | Simple list | Visual Kanban |
| **Documents** | Notes field only | Full documents array with URLs |
| **Collaboration** | Solo | Team-friendly |
| **Workflow** | Flat list | Kanban stages |
| **Best For** | Quick notes | Full projects |

#### **Critical Rules:**

✅ **CREATE Synergy session** for ANY multi-platform project (3+ tools)
✅ **UPDATE session with document URLs** as you create them (MANDATORY!)
✅ **USE both systems** for complex projects (Google Tasks for AI, Synergy for user)
✅ **MOVE cards** through Kanban as work progresses
✅ **SYNC to Google** when user wants external calendar/task tracking
❌ **NEVER lose document links** - always add to Synergy session
❌ **DON'T create Synergy session** for simple 1-2 tool tasks

#### **Example Multi-Platform Project:**

User: "Create a customer onboarding system"

AI Response:
```
This is a multi-step, multi-platform project. I'll create a Synergy Dashboard 
session to track our progress and store all document links.

✅ Created Synergy session: "Customer Onboarding System"
📋 View progress at http://localhost:5001 (Synergy tab)

Now creating resources:
1. Welcome email template...
2. Signup form...
3. Tracking spreadsheet...

[Updates Synergy session with each document URL as created]
```
```

---

## ✅ Status

- [x] **Synergy backend analyzed** - REST API + WebSocket, port 5002
- [x] **Database schema understood** - SQLite with 20 columns, documents/links arrays
- [x] **Tool schema created** - `tools/schemas/synergy_tools.json` (7 functions)
- [x] **Implementation created** - `tools/implementations/synergy.py` (7 functions)
- [x] **Documentation complete** - This file (SYNERGY_INTEGRATION_COMPLETE.md)
- [ ] **System prompt updated** - Add Synergy instructions to tool_usage_system_prompt.md
- [ ] **Test integration** - Start Synergy backend, test tools, verify dashboard updates
- [ ] **Test with AI agent** - Multi-platform project with full Synergy tracking

---

## 🧪 Testing Checklist

### Phase 1: Backend Setup
- [ ] Start Synergy backend: `python synergy_backend.py`
- [ ] Verify API responds: `curl http://localhost:5002/api/sessions/list`
- [ ] Open dashboard: http://localhost:5001 → Synergy tab
- [ ] Verify empty Kanban board visible

### Phase 2: Tool Testing
- [ ] Test create: `synergy_create_session(title="Test Project")`
- [ ] Verify card appears on dashboard
- [ ] Test update: Add document URL
- [ ] Verify document appears on card
- [ ] Test move: Move to "in_progress"
- [ ] Verify card moved on dashboard
- [ ] Test list: Get all sessions
- [ ] Test delete: Remove test session

### Phase 3: AI Integration
- [ ] Update system prompt with Synergy instructions
- [ ] Restart Flask: `BISTART`
- [ ] Test: `CHAT "Create customer onboarding with emails and forms"`
- [ ] Verify: AI creates Synergy session
- [ ] Verify: AI updates session with document URLs
- [ ] Verify: All links visible on dashboard
- [ ] Test resume: Close conversation, reopen, ask to continue
- [ ] Verify: AI retrieves session with all documents

### Phase 4: Google Sync
- [ ] Test: Create session with `sync_google_tasks=True`
- [ ] Verify: Google Task created
- [ ] Check: https://tasks.google.com → AI Agent Tasks list
- [ ] Test: Create session with `sync_google_calendar=True`
- [ ] Verify: Calendar event created

---

**Next Action:** Update system prompt with Synergy instructions, then test with real multi-platform project!

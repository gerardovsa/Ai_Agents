# 🌐 Synergy Dashboard - Universal Platform Guide

**Date:** November 1, 2025  
**Status:** PRIMARY AI project management platform  
**Users:** Both Google AND Microsoft users

---

## 🎯 **CORRECTED UNDERSTANDING:**

### ❌ **WRONG (Previous Misunderstanding):**
- Google Tasks is primary, Synergy is secondary
- Synergy is just visual add-on
- Google Tasks needed for AI tracking

### ✅ **CORRECT:**
- **Synergy Dashboard is PRIMARY** project management platform
- Google Tasks is **optional sync target** (not required)
- Synergy works for Google AND Microsoft users (platform-agnostic)
- Synergy has comprehensive tracking (documents, links, next steps, etc.)

---

## 🏗️ **HOW SYNERGY DASHBOARD WORKS:**

### **Architecture:**

```
┌──────────────────────────────────────────────────────────┐
│           SYNERGY DASHBOARD (PRIMARY)                    │
│                                                          │
│  📊 Visual Kanban Board                                 │
│  ├─ 📦 Backlog      (Ideas, planning)                   │
│  ├─ 🚀 In Progress  (Active work)                       │
│  ├─ 👁️ Review       (Testing, verification)             │
│  └─ ✅ Done         (Completed)                          │
│                                                          │
│  🎴 Rich Cards (Sessions):                              │
│  ├─ Title, Description, Priority                        │
│  ├─ Documents Array (ALL resource URLs!)                │
│  ├─ Links Array (related resources)                     │
│  ├─ Next Steps (action checklist)                       │
│  ├─ Tags, Assignees, Status                             │
│  └─ Created/Updated timestamps                          │
│                                                          │
│  💾 SQLite Database (synergy_sessions.db)               │
│  🌐 REST API: http://localhost:5001/api/kanban/*        │
│  🔌 WebSocket: Real-time updates                         │
│  🔄 Optional Sync: → Google OR Microsoft (user choice)  │
└──────────────────────────────────────────────────────────┘
```

### **Database Schema:**

```sql
CREATE TABLE sessions (
    -- Core identification
    session_id TEXT PRIMARY KEY,          -- Unique ID (UUID)
    title TEXT NOT NULL,                  -- Card title
    description TEXT,                     -- Detailed description
    project_name TEXT,                    -- Project grouping
    
    -- Workflow management
    priority TEXT DEFAULT 'medium',       -- high | medium | low
    status TEXT DEFAULT 'active',         -- active | archived | completed
    kanban_column TEXT DEFAULT 'backlog', -- backlog | to_do | in_progress | done
    
    -- Rich content (JSON arrays) - THE POWER OF SYNERGY!
    documents TEXT,                       -- [{"name": "Doc", "url": "...", "type": "..."}]
    links TEXT,                           -- [{"title": "Link", "url": "..."}]
    next_steps TEXT,                      -- ["Step 1", "Step 2", "Step 3"]
    checklist TEXT,                       -- [{"item": "Task", "done": false}]
    tags TEXT,                            -- ["gmail", "sheets", "automation"]
    assignees TEXT,                       -- ["AI Agent", "User", "Team"]
    
    -- Metadata
    notes TEXT,                           -- Freeform notes field
    due_date TEXT,                        -- ISO date string
    created_at TEXT NOT NULL,             -- ISO timestamp
    updated_at TEXT NOT NULL,             -- ISO timestamp
    
    -- Optional external sync (NOT REQUIRED!)
    google_task_id TEXT,                  -- If user wants Google Tasks sync
    google_calendar_event_id TEXT,        -- If user wants Google Calendar sync
    microsoft_todo_id TEXT,               -- If user wants Microsoft To Do sync
    microsoft_calendar_id TEXT,           -- If user wants Outlook Calendar sync
    session_data TEXT                     -- Additional metadata (JSON)
)
```

**Key Points:**
- ✅ **Platform-agnostic**: No Google/Microsoft dependency in core schema
- ✅ **Rich data**: Documents array stores ALL resource links
- ✅ **Optional sync**: External platforms are add-ons, not requirements
- ✅ **Universal**: Works for Google users, Microsoft users, or no auth

---

## 🎯 **AI WORKFLOW WITH SYNERGY:**

### **Example: Multi-Platform Project**

**User Request:**
```
"Create customer onboarding with welcome emails, signup form, and tracking spreadsheet"
```

### **Step 1: AI Creates Synergy Session** (PRIMARY action!)

```python
session = synergy_create_session(
    title="Customer Onboarding System",
    description="Multi-platform automation: Gmail + Forms + Sheets",
    project_name="Customer Experience",
    priority="high",
    kanban_column="in_progress",
    tags=["gmail", "forms", "sheets", "automation"],
    next_steps=[
        "Create welcome email template",
        "Create signup form",
        "Create tracking spreadsheet",
        "Connect form responses to sheet",
        "Test automation flow"
    ],
    assignees=["AI Agent"]
)

session_id = session["session_id"]  # e.g., "uuid-1234-5678"
```

**Result:** Card appears in "In Progress" column on Kanban board

### **Step 2: AI Creates Resources & Updates Session**

```python
# Create Google Doc
doc = google_docs_smart_create_from_markdown(
    title="Welcome Email Template",
    content="..."
)

# ✅ CRITICAL: Update Synergy with document URL IMMEDIATELY
synergy_update_session(
    session_id=session_id,
    updates={
        "documents": [
            {
                "name": "Welcome Email Template",
                "url": doc["url"],
                "type": "Google Doc"
            }
        ],
        "notes": "✅ Created email template\n"
    }
)

# Create Google Form
form = google_forms_create_form(
    title="Customer Signup Form",
    # ... form config ...
)

# ✅ Add form URL to documents array
synergy_update_session(
    session_id=session_id,
    updates={
        "documents": [
            # Keep existing documents
            {"name": "Welcome Email Template", "url": doc["url"], "type": "Google Doc"},
            # Add new document
            {"name": "Customer Signup Form", "url": form["url"], "type": "Google Form"}
        ],
        "notes": "✅ Created email template\n✅ Created signup form\n"
    }
)

# Create Google Sheet
sheet = google_sheets_create_spreadsheet(
    title="Customer Tracking",
    # ... sheet config ...
)

# ✅ Add sheet URL to documents array (ALL LINKS IN ONE PLACE!)
synergy_update_session(
    session_id=session_id,
    updates={
        "documents": [
            {"name": "Welcome Email Template", "url": doc["url"], "type": "Google Doc"},
            {"name": "Customer Signup Form", "url": form["url"], "type": "Google Form"},
            {"name": "Customer Tracking Sheet", "url": sheet["url"], "type": "Google Sheet"}
        ],
        "notes": "✅ Email template\n✅ Signup form\n✅ Tracking sheet\n"
    }
)
```

**Result:** Card now shows 3 document links - user can click any to open!

### **Step 3: AI Progresses Work Through Kanban**

```python
# Move to Review when ready for testing
synergy_move_session(
    session_id=session_id,
    target_column="review",
    notes="All resources created. Ready for user testing and approval."
)

# User tests system...

# After user approval, move to Done
synergy_move_session(
    session_id=session_id,
    target_column="done",
    notes="✅ User approved. System deployed to production."
)
```

**Result:** Card visually moves across board - user sees progress!

### **Step 4: User Views Dashboard**

User opens: **http://localhost:5001** → Click "Kanban Board" tab

**Sees visual card:**

```
┌─────────────────────────────────────────────────┐
│ 🔴 Customer Onboarding System                   │  ← High priority badge
├─────────────────────────────────────────────────┤
│ Multi-platform automation: Gmail + Forms +      │
│ Sheets for customer signup workflow             │
│                                                 │
│ 📄 Documents (3):                               │
│ • 📝 Welcome Email Template [Open]              │  ← Clickable links!
│ • 📋 Customer Signup Form [Open]                │
│ • 📊 Customer Tracking Sheet [Open]             │
│                                                 │
│ 📋 Next Steps:                                  │
│ • ✅ Create welcome email template              │
│ • ✅ Create signup form                         │
│ • ✅ Create tracking spreadsheet                │
│ • ⬜ Connect form responses to sheet            │
│ • ⬜ Test automation flow                       │
│                                                 │
│ 🏷️ Tags: gmail, forms, sheets, automation      │
│ 👤 Assigned: AI Agent                           │
│ 📅 Status: In Review                            │
│ ⏰ Created: Nov 1, 2025 2:30pm                  │
│ ⏰ Updated: Nov 1, 2025 2:45pm                  │
└─────────────────────────────────────────────────┘
```

**User Actions:**
- ✅ Click document links to open resources
- ✅ Drag card to "Done" column when approved
- ✅ Add comments/notes to card
- ✅ Check off completed next steps
- ✅ See real-time updates as AI works

---

## 🌐 **PLATFORM INDEPENDENCE:**

### **Current Implementation:**

✅ **Core Synergy (Universal):**
- SQLite database (no cloud dependency)
- REST API on port 5001 (platform-agnostic)
- WebSocket for real-time updates (universal)
- Rich data model (documents, links, next steps)
- Visual Kanban interface (browser-based)

⚠️ **Sync Features (Platform-Specific):**
- Google Tasks sync (Google users only)
- Google Calendar sync (Google users only)
- Microsoft To Do sync (NOT YET IMPLEMENTED)
- Outlook Calendar sync (NOT YET IMPLEMENTED)

### **How It Works for Different Users:**

#### **Scenario 1: Google User**

```python
# Create session (works for everyone)
session = synergy_create_session(title="My Project", ...)

# Optional: Sync to Google (Google user only)
synergy_sync_to_google(
    session_id=session_id,
    sync_google_tasks=True,      # Creates Google Task
    sync_google_calendar=True    # Creates calendar event
)
```

**Result:**
- ✅ Synergy card created (primary)
- ✅ Google Task created (optional backup)
- ✅ Google Calendar event created (optional reminder)
- User sees project in 3 places: Synergy (primary) + Google Tasks + Google Calendar

#### **Scenario 2: Microsoft User**

```python
# Create session (works for everyone)
session = synergy_create_session(title="My Project", ...)

# Optional: Sync to Microsoft (Microsoft user only)
synergy_sync_to_microsoft(
    session_id=session_id,
    sync_microsoft_todo=True,      # Creates To Do task
    sync_outlook_calendar=True     # Creates Outlook event
)
```

**Result:**
- ✅ Synergy card created (primary)
- ✅ Microsoft To Do task created (optional backup)
- ✅ Outlook Calendar event created (optional reminder)
- User sees project in 3 places: Synergy (primary) + To Do + Outlook

#### **Scenario 3: No External Auth (Standalone)**

```python
# Create session (works for everyone)
session = synergy_create_session(title="My Project", ...)

# No sync - Synergy only
# User just uses Synergy Dashboard
```

**Result:**
- ✅ Synergy card created (only place)
- User manages everything through Synergy Dashboard
- No external platform dependencies

---

## 🛠️ **WHAT NEEDS TO BE ADDED:**

### **1. Microsoft To Do Sync Function** (NEW)

**Tool Schema:** `tools/schemas/synergy_tools.json`
```json
{
  "name": "synergy_sync_to_microsoft",
  "description": "Sync Synergy session to Microsoft To Do and/or Outlook Calendar",
  "parameters": {
    "session_id": {
      "type": "string",
      "description": "Synergy session ID to sync"
    },
    "sync_microsoft_todo": {
      "type": "boolean",
      "description": "Create/update Microsoft To Do task",
      "default": true
    },
    "sync_outlook_calendar": {
      "type": "boolean",
      "description": "Create/update Outlook Calendar event",
      "default": false
    }
  }
}
```

**Implementation:** `tools/implementations/synergy.py`
```python
def synergy_sync_to_microsoft(
    session_id: str,
    sync_microsoft_todo: bool = True,
    sync_outlook_calendar: bool = False,
    **kwargs
) -> Dict[str, Any]:
    """
    Sync Synergy session to Microsoft platforms
    
    Uses Microsoft Graph API to:
    - Create/update To Do task
    - Create/update Outlook Calendar event
    """
    # Get Microsoft OAuth credentials from kwargs
    access_token = kwargs.get('access_token')
    
    # Call Synergy backend endpoint
    response = requests.post(
        'http://localhost:5001/api/kanban/sessions/{session_id}/sync-microsoft',
        json={
            'sync_todo': sync_microsoft_todo,
            'sync_calendar': sync_outlook_calendar
        },
        headers={'Authorization': f'Bearer {access_token}'}
    )
    
    return response.json()
```

**Backend Endpoint:** `synergy_backend.py` or `AI_infrastructure/routes/kanban_routes.py`
```python
@app.route('/api/kanban/sessions/<session_id>/sync-microsoft', methods=['POST'])
def sync_session_to_microsoft(session_id):
    """Sync Synergy session to Microsoft To Do and/or Outlook Calendar"""
    
    data = request.json
    access_token = request.headers.get('Authorization', '').replace('Bearer ', '')
    
    # Get session from database
    session = get_session_by_id(session_id)
    
    results = {}
    
    # Sync to Microsoft To Do
    if data.get('sync_todo'):
        todo_task = create_microsoft_todo_task(
            access_token=access_token,
            title=session['title'],
            notes=session['description'],
            due_date=session.get('due_date')
        )
        
        # Store task ID in database
        update_session(session_id, {'microsoft_todo_id': todo_task['id']})
        results['todo_task_id'] = todo_task['id']
    
    # Sync to Outlook Calendar
    if data.get('sync_calendar'):
        calendar_event = create_outlook_calendar_event(
            access_token=access_token,
            title=session['title'],
            description=session['description'],
            start_time=session.get('due_date')
        )
        
        # Store event ID in database
        update_session(session_id, {'microsoft_calendar_id': calendar_event['id']})
        results['calendar_event_id'] = calendar_event['id']
    
    return jsonify({'success': True, **results})
```

### **2. System Prompt Update**

Add to `AI_infrastructure/prompts/tool_usage_system_prompt.md`:

```markdown
## 🎯 SYNERGY DASHBOARD (PRIMARY PROJECT MANAGEMENT)

**SYNERGY IS YOUR PRIMARY PROJECT TRACKING PLATFORM** - Use for ALL multi-platform work!

### When to Create Synergy Sessions:

✅ **ALWAYS create Synergy session for:**
- Multi-step projects (3+ actions)
- Multi-platform work (Gmail + Drive + Sheets + Forms, etc.)
- Projects with multiple documents/resources
- Work spanning multiple conversations
- User needs visual progress tracking

### Critical Workflow:

1. **CREATE SESSION** at project start:
```python
session = synergy_create_session(
    title="Project Name",
    description="What we're building",
    priority="high",
    kanban_column="in_progress",
    tags=["gmail", "sheets", "automation"],
    next_steps=["Step 1", "Step 2", "Step 3"]
)
session_id = session["session_id"]
```

2. **UPDATE SESSION** as you create resources (CRITICAL!):
```python
# After creating EACH resource, update session with URL!
synergy_update_session(
    session_id=session_id,
    updates={
        "documents": [
            {"name": "Resource Name", "url": "https://...", "type": "Google Doc"}
        ],
        "notes": "✅ Created resource\n"
    }
)
```

3. **PROGRESS THROUGH KANBAN**:
```python
# Move card as work progresses
synergy_move_session(session_id, "review")  # When ready for testing
synergy_move_session(session_id, "done")    # When complete
```

4. **OPTIONAL SYNC** (based on user platform):
```python
# Google users
synergy_sync_to_google(session_id, sync_google_tasks=True)

# Microsoft users  
synergy_sync_to_microsoft(session_id, sync_microsoft_todo=True)
```

### Platform Support:

- ✅ **Google Users:** Can sync to Google Tasks + Calendar (optional)
- ✅ **Microsoft Users:** Can sync to To Do + Outlook (optional)
- ✅ **Standalone:** Synergy works without external platforms

### User Dashboard:

User can view all sessions at: **http://localhost:5001** (Kanban Board tab)
- Visual Kanban board with drag-and-drop
- Click cards to see all document links
- Real-time updates via WebSocket
- Complete project history
```

---

## 📊 **SYNERGY vs GOOGLE TASKS COMPARISON:**

| Feature | Synergy Dashboard | Google Tasks |
|---------|------------------|--------------|
| **Primary Purpose** | Project management | Simple to-do list |
| **Rich Data** | ✅ Documents, links, next steps | ❌ Title + notes only |
| **Visual Interface** | ✅ Kanban board | ❌ Text list |
| **Multi-platform** | ✅ Google + Microsoft | ❌ Google only |
| **Document Storage** | ✅ Documents array | ❌ No links |
| **Progress Tracking** | ✅ 4 kanban columns | ⚠️ Complete/incomplete |
| **Real-time Updates** | ✅ WebSocket | ❌ Manual refresh |
| **Platform Independent** | ✅ SQLite (local) | ❌ Google cloud |
| **User Visibility** | ✅ Dashboard UI | ⚠️ Google Tasks app |
| **AI Tracking** | ✅ PRIMARY | ❌ Optional sync |

**Verdict:** Synergy Dashboard is SUPERIOR for AI project management!

---

## 🚀 **NEXT STEPS:**

### 1. ✅ Start Synergy Backend
```powershell
cd C:\Users\gpoli\GIT\AI_agents
python synergy_backend.py
```

### 2. ⏳ Initialize Database
Backend will auto-create tables on first run

### 3. ⏳ Add Microsoft Sync Function
- Create tool schema: `synergy_sync_to_microsoft`
- Implement in `synergy.py`
- Add backend endpoint for Microsoft Graph API
- Update system prompt

### 4. ⏳ Update System Prompt
Add Synergy instructions (see template above)

### 5. ⏳ Test Integration
```powershell
CHAT "Create customer onboarding with emails, forms, and tracking"
```

Expected: AI creates Synergy session, adds document URLs, user sees on dashboard!

---

## 💡 **KEY INSIGHTS:**

### **Why Synergy is Better:**

1. **Document Persistence** - ALL resource links in one place (documents array)
2. **Visual Progress** - User sees Kanban workflow (Backlog → In Progress → Review → Done)
3. **Platform Agnostic** - Works for Google, Microsoft, or standalone
4. **Rich Metadata** - Tags, assignees, next steps, checklist, notes
5. **Real-time Updates** - WebSocket keeps everyone in sync
6. **Complete History** - All project details preserved across conversations

### **Why NOT Just Google Tasks:**

1. ❌ No document link storage (just text notes)
2. ❌ No visual interface (plain list)
3. ❌ Google-only (Microsoft users excluded)
4. ❌ Simple data model (title + notes)
5. ❌ No progress tracking (just done/not done)
6. ❌ Manual sync required (no real-time)

---

## 🎉 **BOTTOM LINE:**

**Synergy Dashboard is your PRIMARY project management platform!**

- ✅ Works for Google AND Microsoft users
- ✅ Rich data model (documents, links, next steps)
- ✅ Visual Kanban interface
- ✅ Platform-independent (SQLite + REST API)
- ✅ Optional external sync (Google Tasks, To Do, calendars)
- ✅ Real-time collaboration (WebSocket)
- ✅ Complete project history

**Google Tasks / Microsoft To Do are OPTIONAL sync targets, NOT primary platforms!**

---

**Status:** ✅ Core complete, needs Microsoft sync function + system prompt update

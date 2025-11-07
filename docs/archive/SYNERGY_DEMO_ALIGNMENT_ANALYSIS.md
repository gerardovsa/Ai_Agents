# Synergy Demo Tasks vs Implementation Analysis

**Date:** November 1, 2025  
**Analysis:** Comparing demo tasks with SMART tool instructions and implementation

---

## 🎯 Demo Tasks Review

### Task 1: Email Marketing Campaign
- **Title:** Email Marketing Campaign
- **Description:** Design and launch Q4 email campaign
- **Column:** in_progress
- **Priority:** high
- **Tags:** ["marketing", "email", "Q4"]
- **Next Steps:** [] (empty)
- **Documents:** [] (empty)

### Task 2: Update API Documentation  
- **Title:** Update API Documentation
- **Description:** Document new REST endpoints and WebSocket events
- **Column:** backlog
- **Priority:** medium
- **Tags:** ["documentation", "api"]
- **Next Steps:** [] (empty)
- **Documents:** [] (empty)

### Task 3: Fix Login Bug
- **Title:** Fix Login Bug
- **Description:** Users cannot log in with Google OAuth
- **Column:** in_progress
- **Priority:** urgent
- **Tags:** ["bug", "auth", "urgent"]
- **Next Steps:** [] (empty)
- **Documents:** [] (empty)

---

## ⚠️ CRITICAL ISSUES IDENTIFIED

### Issue 1: Demo Tasks Don't Match SMART Tool Pattern

**Problem:** Demo tasks are NOT multi-platform projects!

- Email Marketing Campaign → Single focus (email), not multi-platform
- Update API Documentation → Single focus (documentation), not multi-platform
- Fix Login Bug → Single focus (bug fix), not multi-platform

**SMART Tool Purpose:** Create complete multi-platform project trackers in ONE call
- Example: Customer Onboarding (Gmail + Forms + Sheets)
- Example: E-commerce Setup (WooCommerce + Stripe + Gmail + Sheets + Forms)

**Demo Tasks Don't Show:**
- ❌ Multi-platform coordination (Gmail + Drive + Sheets + Forms)
- ❌ platforms_involved field (doesn't exist in schema!)
- ❌ Rich next_steps arrays (all empty in demo)
- ❌ Document links (all empty in demo)
- ❌ Auto-update workflow demonstration

---

### Issue 2: Missing `platforms_involved` Column

**Problem:** Database schema doesn't have `platforms_involved` column!

**Current Schema:**
```sql
CREATE TABLE sessions (
    session_id TEXT,
    title TEXT,
    description TEXT,
    project_name TEXT,
    priority TEXT,
    status TEXT,
    kanban_column TEXT,
    due_date TEXT,
    created_at TEXT,
    updated_at TEXT,
    assignees TEXT,        -- JSON array
    tags TEXT,             -- JSON array
    notes TEXT,
    documents TEXT,        -- JSON array
    links TEXT,            -- JSON array
    next_steps TEXT,       -- JSON array
    checklist TEXT,        -- JSON array
    google_task_id TEXT,
    google_calendar_event_id TEXT,
    session_data TEXT      -- JSON object
)
```

**SMART Tool Expected Schema:**
```python
synergy_smart_project_tracker(
    platforms_involved=["gmail", "drive", "sheets"],  # WHERE DOES THIS GO?
    ...
)
```

**Current Implementation:** Stores in `tags` array (mixed with other tags)
**Better Solution:** Add dedicated `platforms_involved` column

---

### Issue 3: Empty next_steps Arrays

**Problem:** All demo tasks have empty next_steps: `[]`

**SMART Tool Emphasis:**
```python
synergy_smart_project_tracker(
    next_steps=[
        "Create welcome email template",
        "Create customer signup form",
        "Create tracking spreadsheet"
    ]  # Required parameter!
)
```

**Demo Tasks Should Have:**
- Email Marketing Campaign → ["Design email template", "Create subscriber list", "Schedule campaign", "Monitor metrics"]
- Update API Documentation → ["Document REST endpoints", "Document WebSocket events", "Create code examples", "Review with team"]
- Fix Login Bug → ["Reproduce issue", "Debug OAuth flow", "Fix authentication", "Test with users", "Deploy fix"]

---

### Issue 4: Empty Documents Arrays

**Problem:** All demo tasks have empty documents: `[]`

**SMART Tool Feature - Auto-Update:**
```python
# AI creates resources
doc = google_docs_smart_create_from_markdown(...)
# AI AUTO-ADDS to session:
synergy_update_session(session_id, updates={
    "documents": [{"name": "Email Template", "url": doc_url, "type": "Google Doc"}]
})
```

**Demo Tasks Should Show:**
- Email Marketing Campaign → [{"name": "Email Template", "url": "...", "type": "Google Doc"}, {"name": "Subscriber List", "url": "...", "type": "Google Sheet"}]
- Update API Documentation → [{"name": "API Guide", "url": "...", "type": "Google Doc"}]

---

## 📊 Alignment Analysis

### What ALIGNS ✅

1. **Kanban Column System**
   - ✅ Demo uses: backlog, in_progress
   - ✅ Matches system prompt: "Backlog → In Progress → Review → Done"

2. **Priority Levels**
   - ✅ Demo uses: high, medium, urgent
   - ✅ Matches implementation: "high", "medium", "low"

3. **Tags Array Structure**
   - ✅ Demo uses JSON arrays: ["marketing", "email", "Q4"]
   - ✅ Matches SMART tool auto-generation

4. **Session ID Format**
   - ✅ Demo uses: `sess_20251101_1352_john_email_marketing_campaign`
   - ✅ Matches implementation pattern: `sess_{timestamp}_{user}_{title_slug}`

5. **Basic Structure**
   - ✅ Title, description, priority, kanban_column all present
   - ✅ Database schema supports JSON arrays for tags, documents, next_steps

### What MISALIGNS ❌

1. **Use Case Mismatch**
   - ❌ Demo tasks are NOT multi-platform projects
   - ❌ Demo tasks don't demonstrate SMART tool purpose
   - ❌ Demo tasks look like generic project management (Trello/Asana style)

2. **Missing platforms_involved Field**
   - ❌ No dedicated column for platform tracking
   - ❌ Stored in tags (mixed with other metadata)
   - ❌ Can't easily query "all Gmail projects"

3. **Empty Critical Fields**
   - ❌ No next_steps (key feature of SMART tool)
   - ❌ No documents (defeats auto-update purpose)
   - ❌ No links (can't demonstrate resource tracking)

4. **Missing System Prompt Examples**
   - ❌ Demo doesn't show: Customer Onboarding System
   - ❌ Demo doesn't show: E-commerce Store Setup
   - ❌ Demo doesn't show: Multi-platform coordination

5. **assignees Field Mismatch**
   - Demo has: `assignees: ['John Doe', 'Sarah Smith']` (user names)
   - SMART tool doesn't set this (it's for team collaboration, not AI work)
   - System prompt doesn't mention assignees

---

## 🔧 Recommended Fixes

### Fix 1: Update Demo Tasks to Multi-Platform Examples

**Replace current demo tasks with:**

```python
demo_tasks = [
    {
        'title': 'Customer Onboarding System',
        'description': 'Multi-platform customer onboarding: email welcome + signup form + tracking spreadsheet',
        'project_name': 'Customer Onboarding',
        'priority': 'high',
        'kanban_column': 'in_progress',
        'tags': ['gmail', 'forms', 'sheets', 'multi-platform', 'automation'],
        'next_steps': [
            'Create welcome email template',
            'Create customer signup form',
            'Create tracking spreadsheet',
            'Connect form to sheet'
        ],
        'documents': [
            {
                'name': 'Welcome Email Template',
                'url': 'https://docs.google.com/document/d/demo123',
                'type': 'Google Doc'
            },
            {
                'name': 'Customer Signup Form',
                'url': 'https://docs.google.com/forms/d/demo456',
                'type': 'Google Form'
            },
            {
                'name': 'Customer Tracking Spreadsheet',
                'url': 'https://docs.google.com/spreadsheets/d/demo789',
                'type': 'Google Sheet'
            }
        ]
    },
    {
        'title': 'E-commerce Store Setup',
        'description': 'Complete store setup: WooCommerce config + Stripe payments + order notification emails',
        'project_name': 'E-commerce Setup',
        'priority': 'high',
        'kanban_column': 'in_progress',
        'tags': ['woocommerce', 'stripe', 'gmail', 'sheets', 'multi-platform'],
        'next_steps': [
            'Configure WooCommerce settings',
            'Setup Stripe payment gateway',
            'Create order notification emails',
            'Create order tracking spreadsheet',
            'Test checkout flow'
        ],
        'documents': [
            {
                'name': 'Store Configuration Guide',
                'url': 'https://docs.google.com/document/d/store123',
                'type': 'Google Doc'
            },
            {
                'name': 'Order Tracking Sheet',
                'url': 'https://docs.google.com/spreadsheets/d/orders456',
                'type': 'Google Sheet'
            }
        ]
    },
    {
        'title': 'Content Creation Workflow',
        'description': 'Multi-platform content pipeline: Docs → Slides → Drive organization → Calendar scheduling',
        'project_name': 'Content Creation',
        'priority': 'medium',
        'kanban_column': 'review',
        'tags': ['google_docs', 'google_slides', 'google_drive', 'google_calendar', 'multi-platform'],
        'next_steps': [
            'Create content template',
            'Generate slide deck',
            'Organize in Drive',
            'Schedule publication'
        ],
        'documents': [
            {
                'name': 'Content Template',
                'url': 'https://docs.google.com/document/d/content123',
                'type': 'Google Doc'
            },
            {
                'name': 'Presentation Deck',
                'url': 'https://docs.google.com/presentation/d/deck456',
                'type': 'Google Slides'
            }
        ]
    }
]
```

---

### Fix 2: Add platforms_involved Column to Schema

**Database Migration:**

```sql
ALTER TABLE sessions ADD COLUMN platforms_involved TEXT;  -- JSON array
```

**Update synergy_backend.py seed function:**

```python
sample_sessions = [
    {
        'title': 'Customer Onboarding System',
        'platforms_involved': ['gmail', 'forms', 'sheets'],  # NEW FIELD
        'tags': ['multi-platform', 'automation'],
        'next_steps': [...],
        'documents': [...]
    }
]
```

**Update synergy.py SMART tool:**

```python
def synergy_smart_project_tracker(platforms_involved, ...):
    payload = {
        'platforms_involved': json.dumps(platforms_involved),  # NEW FIELD
        ...
    }
```

---

### Fix 3: Update System Prompt Examples

**Current system prompt shows:**
```python
synergy_smart_project_tracker(
    title="Customer Onboarding System",
    platforms_involved=["gmail", "forms", "sheets"],
    next_steps=[...]
)
```

**Demo tasks should match this exactly!**

---

### Fix 4: Remove assignees from Demo (AI Use Case)

**Current:** Demo has `assignees: ['John Doe', 'Sarah Smith']`  
**Problem:** Synergy is for AI agent tracking its own work, not team collaboration  
**Solution:** Remove assignees or set to `["AI Agent"]`

---

## 📝 Summary

### Alignment Score: 4/10 ⚠️

**What Works:**
- ✅ Basic Kanban structure (4 columns)
- ✅ Priority system
- ✅ Tags array format
- ✅ Session ID pattern

**Critical Misalignments:**
- ❌ Demo tasks aren't multi-platform (defeats SMART tool purpose)
- ❌ Missing platforms_involved column
- ❌ Empty next_steps arrays (key feature unused)
- ❌ Empty documents arrays (auto-update can't demo)
- ❌ Use case mismatch (generic PM vs multi-platform AI coordination)

### Immediate Actions Required:

1. **Update Demo Tasks** - Replace with multi-platform examples (Customer Onboarding, E-commerce Setup, Content Workflow)
2. **Add platforms_involved Column** - Dedicated field for platform tracking
3. **Populate next_steps** - Show checklist feature
4. **Populate documents** - Demonstrate auto-update workflow
5. **Align with System Prompt** - Demo tasks should match examples in tool_usage_system_prompt.md

### Files to Update:

1. `synergy_backend.py` lines 572-610 - Replace sample_sessions
2. `synergy_backend.py` line ~80 - Add platforms_involved to schema
3. `tools/implementations/synergy.py` - Update SMART tool to use platforms_involved column
4. `SYNERGY_SMART_TOOL_GUIDE.md` - Update to match actual database schema

---

**Conclusion:** Demo tasks don't demonstrate SMART tool's core value proposition (multi-platform project coordination). They look like generic project management tasks. Need to update demos to show Gmail + Forms + Sheets + WooCommerce + Stripe coordination that the system prompt describes.

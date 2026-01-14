# 🎯 Universal Kanban Board - Field Mapping Architecture

**Date:** October 28, 2025  
**Purpose:** Universal field structure that syncs directly to Google Tasks & Microsoft 365 To Do  
**Status:** ✅ Complete Specification

---

## 🏗️ Design Philosophy

**One Structure → Two Platforms**

The Kanban board uses a **universal field schema** that contains ALL fields from both platforms. When syncing:
- **Outbound:** Map Kanban fields → Platform-specific fields
- **Inbound:** Map Platform fields → Kanban universal fields
- **Result:** One source of truth, consistent data everywhere

---

## 📊 Universal Kanban Field Schema

### **Core Fields (Supported by Both Platforms)**

| Universal Field | Type | Google Tasks Field | Microsoft To Do Field | Description |
|---|---|---|---|---|
| `title` | string | `title` | `title` | Task name/title |
| `description` | text | `notes` | `body.content` | Task description/notes |
| `status` | enum | `status` | `status` | Completion status |
| `due_date` | datetime | `due` | `dueDateTime.dateTime` | Due date/time |
| `completed` | boolean | `status='completed'` | `status='completed'` | Is task done? |
| `created_at` | datetime | `created` | `createdDateTime` | Creation timestamp |
| `updated_at` | datetime | `updated` | `lastModifiedDateTime` | Last update timestamp |

### **Priority/Importance Fields**

| Universal Field | Type | Google Tasks | Microsoft To Do | Mapping Logic |
|---|---|---|---|---|
| `priority` | enum | N/A (custom) | `importance` | **G:** Title prefix `[HIGH]` / `[MED]` / `[LOW]`<br>**M:** Direct field `low/normal/high` |

### **Organization Fields**

| Universal Field | Type | Google Tasks | Microsoft To Do | Mapping Logic |
|---|---|---|---|---|
| `kanban_column` | enum | N/A (custom) | N/A (custom) | **Both:** Store in `notes`/`body` as metadata<br>**Format:** `<!-- KANBAN:in_progress -->` |
| `project_name` | string | N/A (custom) | `categories[0]` | **G:** In notes<br>**M:** First category |
| `tags` | array | N/A (custom) | `categories` | **G:** In notes as `#tag1 #tag2`<br>**M:** Direct array |

### **Collaboration Fields**

| Universal Field | Type | Google Tasks | Microsoft To Do | Mapping Logic |
|---|---|---|---|---|
| `assignees` | array | N/A (personal) | N/A (To Do is personal) | **Both:** Store in notes/body<br>**Format:** `@assignee1 @assignee2` |

### **Sub-Tasks & Checklists**

| Universal Field | Type | Google Tasks | Microsoft To Do | Mapping Logic |
|---|---|---|---|---|
| `next_steps` | array | Subtasks (child tasks) | `checklistItems` | **G:** Create child tasks with `parent` field<br>**M:** Use native checklist |
| `checklist` | array | Subtasks (child tasks) | `checklistItems` | **G:** Create child tasks<br>**M:** Use native checklist |

### **Documents & Links**

| Universal Field | Type | Google Tasks | Microsoft To Do | Mapping Logic |
|---|---|---|---|---|
| `documents` | array | N/A | N/A | **Both:** Store in notes/body as markdown links<br>**Format:** `[Doc Name](url)` |
| `links` | array | `links` (if supported) | `linkedResources` | **G:** In notes<br>**M:** Use native links |

### **Microsoft-Specific Fields**

| Universal Field | Type | Google Tasks | Microsoft To Do | Mapping Logic |
|---|---|---|---|---|
| `reminder` | datetime | N/A | `reminderDateTime` | **G:** Not supported (ignore)<br>**M:** Direct field |
| `recurrence` | object | N/A | `recurrence` | **G:** Not supported (ignore)<br>**M:** Direct field |

---

## 🔄 Bidirectional Sync Logic

### **Scenario 1: Create Task in Kanban → Sync to Both Platforms**

**User Action:** Creates card in Kanban board

```javascript
// Kanban Card Data
const kanbanCard = {
    title: "Review Q4 Budget",
    description: "Focus on marketing spend and ROI analysis",
    priority: "high",
    due_date: "2025-10-31T17:00:00Z",
    kanban_column: "in_progress",
    project_name: "Finance Review",
    tags: ["budget", "q4", "urgent"],
    assignees: ["John Doe", "Jane Smith"],
    checklist: [
        { item: "Review marketing budget", completed: false },
        { item: "Analyze ROI metrics", completed: false },
        { item: "Prepare presentation", completed: false }
    ],
    documents: [
        { title: "Budget Spreadsheet", url: "https://docs.google.com/..." }
    ]
};
```

**Sync to Google Tasks:**

```javascript
// Map to Google Tasks Format
const googleTask = {
    title: "[HIGH] Review Q4 Budget",  // Add priority prefix
    notes: `
Focus on marketing spend and ROI analysis

📋 Project: Finance Review
🏷️ Tags: #budget #q4 #urgent
👥 Assignees: @John Doe @Jane Smith
📊 Kanban: <!-- KANBAN:in_progress -->

📄 Documents:
- [Budget Spreadsheet](https://docs.google.com/...)

✅ Checklist:
→ Will be created as subtasks
    `.trim(),
    due: "2025-10-31T17:00:00.000Z",
    status: "needsAction"
};

// Create main task
const mainTask = await google_tasks_create_task(googleTask);

// Create checklist as subtasks
for (const item of kanbanCard.checklist) {
    await google_tasks_create_task({
        title: item.item,
        parent: mainTask.id,
        status: item.completed ? "completed" : "needsAction"
    });
}
```

**Sync to Microsoft To Do:**

```javascript
// Map to Microsoft To Do Format
const microsoftTask = {
    title: "Review Q4 Budget",
    body: {
        content: `
Focus on marketing spend and ROI analysis

📋 Project: Finance Review
👥 Assignees: @John Doe @Jane Smith
📊 Kanban: <!-- KANBAN:in_progress -->

📄 Documents:
- [Budget Spreadsheet](https://docs.google.com/...)
        `.trim(),
        contentType: "text"
    },
    importance: "high",  // Direct field!
    dueDateTime: {
        dateTime: "2025-10-31T17:00:00",
        timeZone: "UTC"
    },
    status: "notStarted",
    categories: ["Finance Review", "budget", "q4", "urgent"],  // Project + tags
    checklistItems: [
        { displayName: "Review marketing budget", isChecked: false },
        { displayName: "Analyze ROI metrics", isChecked: false },
        { displayName: "Prepare presentation", isChecked: false }
    ]
};

// Create task (single call with all data!)
const msTask = await microsoft_todo_create_task(microsoftTask);
```

---

### **Scenario 2: Update Task in Google Tasks → Sync Back to Kanban & Microsoft**

**User Action:** Completes a subtask in Google Tasks

```javascript
// Google Tasks detects change
const updatedTask = {
    id: "task_123",
    title: "[HIGH] Review Q4 Budget",
    status: "needsAction",
    updated: "2025-10-28T15:30:00Z"
};

// Fetch all subtasks to check checklist status
const subtasks = await google_tasks_list_subtasks(updatedTask.id);
const completedCount = subtasks.filter(t => t.status === 'completed').length;

// Update Kanban Card
await updateKanbanCard(kanbanCard.session_id, {
    checklist: subtasks.map(t => ({
        item: t.title,
        completed: t.status === 'completed'
    })),
    updated_at: updatedTask.updated
});

// Sync to Microsoft To Do
await microsoft_todo_update_task(msTask.id, {
    checklistItems: subtasks.map(t => ({
        displayName: t.title,
        isChecked: t.status === 'completed'
    }))
});
```

---

### **Scenario 3: Update Task in Microsoft To Do → Sync Back to Kanban & Google**

**User Action:** Changes importance level in Microsoft To Do

```javascript
// Microsoft To Do webhook/polling detects change
const updatedMsTask = {
    id: "AAMkAGI...",
    title: "Review Q4 Budget",
    importance: "low",  // Changed from "high"
    lastModifiedDateTime: "2025-10-28T16:00:00Z"
};

// Update Kanban Card
await updateKanbanCard(kanbanCard.session_id, {
    priority: "low",  // Map importance → priority
    updated_at: updatedMsTask.lastModifiedDateTime
});

// Update Google Tasks (change title prefix)
const googleTaskId = getGoogleTaskId(kanbanCard.session_id);
await google_tasks_update_task(googleTaskId, {
    title: "[LOW] Review Q4 Budget"  // Change prefix
});
```

---

## 🔧 Enhanced Database Schema

### **Updated `sessions` Table**

```sql
CREATE TABLE sessions (
    session_id TEXT PRIMARY KEY,
    
    -- ✅ UNIVERSAL CORE FIELDS (Both platforms)
    title TEXT NOT NULL,
    description TEXT,
    status TEXT DEFAULT 'active' CHECK(status IN ('active', 'completed', 'paused')),
    due_date TEXT,  -- ISO 8601
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL,
    
    -- ✅ UNIVERSAL ORGANIZATION FIELDS
    priority TEXT DEFAULT 'medium' CHECK(priority IN ('low', 'medium', 'high')),
    kanban_column TEXT DEFAULT 'backlog' CHECK(kanban_column IN ('backlog', 'in_progress', 'review', 'done')),
    project_name TEXT,
    
    -- ✅ UNIVERSAL ARRAYS (JSON)
    tags TEXT DEFAULT '[]',           -- ["tag1", "tag2"]
    assignees TEXT DEFAULT '[]',      -- ["user1", "user2"]
    checklist TEXT DEFAULT '[]',      -- [{"item": "...", "completed": false}]
    next_steps TEXT DEFAULT '[]',     -- [{"description": "...", "completed": false}]
    documents TEXT DEFAULT '[]',      -- [{"title": "...", "url": "..."}]
    links TEXT DEFAULT '[]',          -- [{"title": "...", "url": "..."}]
    
    -- ✅ MICROSOFT-SPECIFIC FIELDS
    reminder_date TEXT,               -- ISO 8601
    recurrence_pattern TEXT,          -- JSON: {"pattern": "daily", "interval": 1}
    
    -- ✅ METADATA
    notes TEXT,
    session_data TEXT DEFAULT '{}',   -- Additional flexible storage
    
    -- ✅ SYNC IDENTIFIERS
    google_task_id TEXT,
    google_task_list_id TEXT DEFAULT '@default',
    microsoft_todo_id TEXT,
    microsoft_todo_list_id TEXT,
    google_calendar_event_id TEXT
);
```

---

## 🔀 Field Mapping Functions (Python)

### **Kanban → Google Tasks**

```python
def kanban_to_google_task(kanban_card):
    """Convert Kanban card to Google Tasks format"""
    
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
    
    # Add Kanban column metadata
    notes_parts.append(f"\n📊 Kanban: <!-- KANBAN:{kanban_card['kanban_column']} -->")
    
    # Add documents
    if kanban_card.get('documents'):
        notes_parts.append("\n📄 Documents:")
        for doc in kanban_card['documents']:
            notes_parts.append(f"- [{doc['title']}]({doc['url']})")
    
    # Priority prefix in title
    priority_prefix = {
        'high': '[HIGH] ',
        'medium': '[MED] ',
        'low': '[LOW] '
    }.get(kanban_card.get('priority', 'medium'), '')
    
    return {
        'title': f"{priority_prefix}{kanban_card['title']}",
        'notes': '\n'.join(notes_parts),
        'due': kanban_card.get('due_date'),
        'status': 'completed' if kanban_card.get('status') == 'completed' else 'needsAction'
    }
```

### **Kanban → Microsoft To Do**

```python
def kanban_to_microsoft_todo(kanban_card):
    """Convert Kanban card to Microsoft To Do format"""
    
    # Build body content
    body_parts = [kanban_card.get('description', '')]
    
    # Add project
    if kanban_card.get('project_name'):
        body_parts.append(f"\n📋 Project: {kanban_card['project_name']}")
    
    # Add assignees (To Do is personal, but we can store it)
    if kanban_card.get('assignees'):
        assignees_str = ' '.join(f"@{a}" for a in kanban_card['assignees'])
        body_parts.append(f"👥 Assignees: {assignees_str}")
    
    # Add Kanban column metadata
    body_parts.append(f"\n📊 Kanban: <!-- KANBAN:{kanban_card['kanban_column']} -->")
    
    # Add documents
    if kanban_card.get('documents'):
        body_parts.append("\n📄 Documents:")
        for doc in kanban_card['documents']:
            body_parts.append(f"- [{doc['title']}]({doc['url']})")
    
    # Build categories (project + tags)
    categories = []
    if kanban_card.get('project_name'):
        categories.append(kanban_card['project_name'])
    if kanban_card.get('tags'):
        categories.extend(kanban_card['tags'])
    
    # Build checklist
    checklist_items = []
    if kanban_card.get('checklist'):
        for item in kanban_card['checklist']:
            checklist_items.append({
                'displayName': item['item'],
                'isChecked': item.get('completed', False)
            })
    
    return {
        'title': kanban_card['title'],  # No prefix needed!
        'body': {
            'content': '\n'.join(body_parts),
            'contentType': 'text'
        },
        'importance': kanban_card.get('priority', 'normal'),  # Direct mapping!
        'dueDateTime': {
            'dateTime': kanban_card.get('due_date', '').replace('Z', ''),
            'timeZone': 'UTC'
        } if kanban_card.get('due_date') else None,
        'status': 'completed' if kanban_card.get('status') == 'completed' else 'notStarted',
        'categories': categories,
        'checklistItems': checklist_items,
        'reminderDateTime': {
            'dateTime': kanban_card.get('reminder_date', '').replace('Z', ''),
            'timeZone': 'UTC'
        } if kanban_card.get('reminder_date') else None
    }
```

### **Google Tasks → Kanban**

```python
def google_task_to_kanban(google_task, subtasks=None):
    """Convert Google Tasks to Kanban card format"""
    
    # Extract priority from title prefix
    title = google_task['title']
    priority = 'medium'
    if title.startswith('[HIGH]'):
        priority = 'high'
        title = title.replace('[HIGH] ', '')
    elif title.startswith('[LOW]'):
        priority = 'low'
        title = title.replace('[LOW] ', '')
    elif title.startswith('[MED]'):
        title = title.replace('[MED] ', '')
    
    # Parse notes for metadata
    notes = google_task.get('notes', '')
    
    # Extract Kanban column
    kanban_column = 'backlog'
    if '<!-- KANBAN:' in notes:
        import re
        match = re.search(r'<!-- KANBAN:(\w+) -->', notes)
        if match:
            kanban_column = match.group(1)
    
    # Extract project name
    project_name = None
    if '📋 Project:' in notes:
        import re
        match = re.search(r'📋 Project: (.+)', notes)
        if match:
            project_name = match.group(1).strip()
    
    # Extract tags
    tags = []
    if '🏷️ Tags:' in notes:
        import re
        match = re.search(r'🏷️ Tags: (.+)', notes)
        if match:
            tags = [tag.strip('#') for tag in match.group(1).split()]
    
    # Extract assignees
    assignees = []
    if '👥 Assignees:' in notes:
        import re
        match = re.search(r'👥 Assignees: (.+)', notes)
        if match:
            assignees = [a.strip('@') for a in match.group(1).split()]
    
    # Extract documents
    documents = []
    import re
    doc_matches = re.findall(r'\[(.+?)\]\((.+?)\)', notes)
    for title, url in doc_matches:
        documents.append({'title': title, 'url': url})
    
    # Convert subtasks to checklist
    checklist = []
    if subtasks:
        for subtask in subtasks:
            checklist.append({
                'item': subtask['title'],
                'completed': subtask['status'] == 'completed'
            })
    
    # Clean description (remove metadata)
    description = notes.split('📋 Project:')[0].strip()
    
    return {
        'title': title,
        'description': description,
        'priority': priority,
        'status': 'completed' if google_task.get('status') == 'completed' else 'active',
        'due_date': google_task.get('due'),
        'kanban_column': kanban_column,
        'project_name': project_name,
        'tags': tags,
        'assignees': assignees,
        'checklist': checklist,
        'documents': documents,
        'created_at': google_task.get('created'),
        'updated_at': google_task.get('updated')
    }
```

### **Microsoft To Do → Kanban**

```python
def microsoft_todo_to_kanban(ms_task):
    """Convert Microsoft To Do to Kanban card format"""
    
    # Extract body content
    body_content = ''
    if ms_task.get('body'):
        body_content = ms_task['body'].get('content', '')
    
    # Extract Kanban column
    kanban_column = 'backlog'
    if '<!-- KANBAN:' in body_content:
        import re
        match = re.search(r'<!-- KANBAN:(\w+) -->', body_content)
        if match:
            kanban_column = match.group(1)
    
    # Extract project name (first category)
    project_name = None
    categories = ms_task.get('categories', [])
    if categories:
        project_name = categories[0]
    
    # Other categories are tags
    tags = categories[1:] if len(categories) > 1 else []
    
    # Extract assignees
    assignees = []
    if '👥 Assignees:' in body_content:
        import re
        match = re.search(r'👥 Assignees: (.+)', body_content)
        if match:
            assignees = [a.strip('@') for a in match.group(1).split()]
    
    # Extract documents
    documents = []
    import re
    doc_matches = re.findall(r'\[(.+?)\]\((.+?)\)', body_content)
    for title, url in doc_matches:
        documents.append({'title': title, 'url': url})
    
    # Convert checklist items
    checklist = []
    if ms_task.get('checklistItems'):
        for item in ms_task['checklistItems']:
            checklist.append({
                'item': item['displayName'],
                'completed': item.get('isChecked', False)
            })
    
    # Clean description (remove metadata)
    description = body_content.split('📋 Project:')[0].strip()
    
    # Parse due date
    due_date = None
    if ms_task.get('dueDateTime'):
        due_date = ms_task['dueDateTime']['dateTime'] + 'Z'
    
    # Parse reminder
    reminder_date = None
    if ms_task.get('reminderDateTime'):
        reminder_date = ms_task['reminderDateTime']['dateTime'] + 'Z'
    
    return {
        'title': ms_task['title'],
        'description': description,
        'priority': ms_task.get('importance', 'normal'),  # Direct mapping!
        'status': 'completed' if ms_task.get('status') == 'completed' else 'active',
        'due_date': due_date,
        'reminder_date': reminder_date,
        'kanban_column': kanban_column,
        'project_name': project_name,
        'tags': tags,
        'assignees': assignees,
        'checklist': checklist,
        'documents': documents,
        'created_at': ms_task.get('createdDateTime'),
        'updated_at': ms_task.get('lastModifiedDateTime')
    }
```

---

## 🎯 Sync Workflow Summary

### **Create Flow**

```
User creates Kanban card
    ↓
1. Save to sessions table (universal format)
    ↓
2. Map → Google Tasks format
    ↓
3. Create Google task + subtasks
    ↓
4. Save google_task_id to sync_metadata
    ↓
5. Map → Microsoft To Do format
    ↓
6. Create Microsoft task (with checklist)
    ↓
7. Save microsoft_todo_id to sync_metadata
    ↓
✅ All three systems synced!
```

### **Update Flow (Kanban)**

```
User updates Kanban card
    ↓
1. Update sessions table
    ↓
2. Get google_task_id from sync_metadata
    ↓
3. Map changes → Google format
    ↓
4. Update Google task
    ↓
5. Get microsoft_todo_id from sync_metadata
    ↓
6. Map changes → Microsoft format
    ↓
7. Update Microsoft task
    ↓
✅ Changes propagated to both platforms!
```

### **Update Flow (External Platform)**

```
Google Tasks change detected
    ↓
1. Fetch updated task + subtasks
    ↓
2. Map → Kanban format
    ↓
3. Update sessions table
    ↓
4. Get microsoft_todo_id from sync_metadata
    ↓
5. Map → Microsoft format
    ↓
6. Update Microsoft task
    ↓
✅ Change synced across all systems!
```

---

## ✅ Universal Kanban Benefits

**For Users:**
- ✅ **One interface** to rule them all
- ✅ **No platform-specific limitations** - use best features from both
- ✅ **Consistent experience** regardless of sync source
- ✅ **No data loss** - all fields preserved in universal format

**For Developers:**
- ✅ **Single source of truth** (sessions table)
- ✅ **Clear field mappings** (documented above)
- ✅ **Predictable sync behavior**
- ✅ **Easy to extend** to new platforms (Asana, Trello, etc.)

**Result:**
The Kanban board becomes a **universal task management hub** that seamlessly works with Google Tasks, Microsoft 365 To Do, and can easily be extended to support any other task platform in the future! 🚀

# Synergy Board Card Structure Documentation

**Date:** November 9, 2025  
**Example Session:** `sess_20251107_2211_email_thread_quote_processing_`  
**Database:** `data/synergy_sessions.db`  
**Table:** `synergy_sessions`

---

## Overview

The Synergy board displays project/task cards in a Kanban-style interface. Each card represents a session with detailed project information, documents, tasks, and linked threads.

---

## Card Views

### 1. Collapsed View (Default)
Displays compact card information:
- Priority indicator (colored dot)
- Title
- Project name
- Status badge
- Last active time
- Statistics (messages, documents, tasks)
- Session ID
- Tags (first 3)
- Action buttons (expand, pop-out, resume, edit, delete)

### 2. Expanded View (Double-click or Expand button)
Shows full card details with all sections:
- All collapsed view elements
- Full description
- Complete document list
- Link list
- Next steps with checkboxes
- Checklist with progress
- Assignees
- Due dates
- Linked threads
- Assigned AI agents

---

## Database Schema

### Table: `synergy_sessions`
**Location:** `c:\Users\gpoli\GIT\AI_agents\data\synergy_sessions.db`

| Column Name | Type | Required | Default | Description | JSON Structure Link |
|-------------|------|----------|---------|-------------|---------------------|
| `session_id` | TEXT | Yes (PK) | - | Unique session identifier (e.g., `sess_20251107_2211_email_thread_quote_processing_`) | N/A - Simple TEXT |
| `title` | TEXT | Yes | - | Card title displayed prominently | N/A - Simple TEXT |
| `description` | TEXT | No | NULL | Full project description (shown in expanded view) | N/A - Simple TEXT |
| `platforms_involved` | TEXT | No | NULL | **JSON Array** - List of platforms used | [See Platforms Array](#platforms-array) |
| `status` | TEXT | No | 'active' | Status: 'active', 'paused', 'completed' | N/A - Simple TEXT |
| `priority` | TEXT | No | 'medium' | Priority: 'low', 'medium', 'high', 'critical' | N/A - Simple TEXT |
| `kanban_column` | TEXT | No | 'backlog' | Column: 'backlog', 'in_progress', 'review', 'completed' | N/A - Simple TEXT |
| `tags` | TEXT | No | NULL | **JSON Array** - Tags for categorization | [See Tags Array](#tags-array) |
| `documents` | TEXT | No | NULL | **JSON Array** - Document objects | [See Documents Array](#documents-array) |
| `links` | TEXT | No | NULL | **JSON Array** - External link objects | [See Links Array](#links-array) |
| `next_steps` | TEXT | No | NULL | **JSON Array** - Action items with checkboxes | [See Next Steps Array](#next-steps-array) |
| `assignees` | TEXT | No | NULL | **JSON Array** - People assigned to this card | [See Assignees Array](#assignees-array) |
| `recent_activity` | TEXT | No | NULL | **JSON Array** - Activity log entries | [See Recent Activity Array](#recent-activity-array) |
| `checklist` | TEXT | No | NULL | **JSON Array** - Checklist items with completion status | [See Checklist Array](#checklist-array) |
| `due_date` | TEXT | No | NULL | ISO date string for deadline | N/A - Simple TEXT (ISO format) |
| `created_at` | TEXT | No | CURRENT_TIMESTAMP | ISO timestamp of creation | N/A - Simple TEXT (ISO format) |
| `last_active` | TEXT | No | CURRENT_TIMESTAMP | ISO timestamp of last activity | N/A - Simple TEXT (ISO format) |
| `completed_at` | TEXT | No | NULL | ISO timestamp when completed | N/A - Simple TEXT (ISO format) |
| `google_task_id` | TEXT | No | NULL | Google Tasks integration ID | N/A - Simple TEXT |
| `google_calendar_id` | TEXT | No | NULL | Google Calendar event ID | N/A - Simple TEXT |
| `microsoft_todo_id` | TEXT | No | NULL | Microsoft To Do task ID | N/A - Simple TEXT |
| `thread_ids` | TEXT | No | NULL | **JSON Array** - Linked thread IDs | [See Thread IDs Array](#thread-ids-array) |
| `assigned_agents` | TEXT | No | NULL | **JSON Array** - AI agents assigned | [See Assigned Agents Array](#assigned-agents-array) |

---

## JSON Array Field Structures (Complete Reference)

### Platforms Array
**Database Column:** `platforms_involved`  
**Type:** JSON Array of strings  
**Storage:** TEXT column containing JSON string

**Structure:**
```json
["Google Docs", "Gmail", "Google Sheets", "Slack"]
```

**Example:**
```json
["Google Workspace", "Microsoft 365", "Stripe"]
```

**Usage:** Track which platforms/tools are involved in this project/task

---

### Tags Array
**Database Column:** `tags`  
**Type:** JSON Array of strings  
**Storage:** TEXT column containing JSON string

**Structure:**
```json
["tag1", "tag2", "tag3"]
```

**Example:**
```json
["quotes", "customer_service", "email_processing", "word_docs", "excel_tracking"]
```

**Usage:** Categorize and filter cards by topic/type

---

### Documents Array
**Database Column:** `documents`  
**Type:** JSON Array of document objects  
**Storage:** TEXT column containing JSON string

**Object Structure:**
```json
{
  "name": "String - Display name (REQUIRED)",
  "url": "String - Full URL (REQUIRED)",
  "size": "String - Human-readable size (OPTIONAL)",
  "type": "String - Document type (OPTIONAL)",
  "created_at": "String - ISO timestamp (OPTIONAL)"
}
```

**Complete Example:**
```json
[
  {
    "name": "Email Thread 1 - Leanne Catalano Corflute",
    "url": "https://docs.google.com/document/d/abc123xyz",
    "type": "google_doc",
    "created_at": "2025-11-07T22:11:43.207462"
  },
  {
    "name": "Quote Tracking Spreadsheet",
    "url": "https://sheets.google.com/spreadsheets/d/def456uvw",
    "type": "google_sheet",
    "size": "45 KB"
  },
  {
    "name": "Customer Requirements.pdf",
    "url": "https://drive.google.com/file/d/ghi789rst",
    "type": "pdf",
    "size": "1.2 MB"
  }
]
```

**Usage:** Store references to all documents related to this project

### HTML Rendering

**Collapsed View:** Shows document count only
```html
<span class="card-stat">
  <i class="fas fa-file"></i> 3
</span>
```

**Expanded View:** Shows full document list
```html
<div class="card-section">
  <div class="section-title">
    <i class="fas fa-file-alt"></i> Documents (3)
  </div>
  <div class="document-list">
    <div class="document-item">
      <i class="fas fa-file"></i>
      <span class="doc-name">Email Thread 1 - Leanne Catalano Corflute</span>
      <span class="doc-size">N/A</span>
    </div>
    <!-- More documents... -->
  </div>
</div>
```

### JavaScript Access

```javascript
// Parse documents from session object
const documents = this.parseJsonField(session.documents, []);

// Documents is now an array of document objects
documents.forEach(doc => {
  console.log(doc.name);  // "Email Thread 1 - Leanne Catalano Corflute"
  console.log(doc.url);   // "https://docs.google.com/document/d/xxx"
  console.log(doc.size);  // "1.2 MB" or undefined
});
```

---

### Links Array
**Database Column:** `links`  
**Type:** JSON Array of link objects  
**Storage:** TEXT column containing JSON string

**Object Structure:**
```json
{
  "title": "String - Display text for link (REQUIRED)",
  "url": "String - Full URL (REQUIRED)",
  "type": "String - Link type/category (OPTIONAL)"
}
```

**Complete Example:**
```json
[
  {
    "title": "Campaign Brief",
    "url": "https://notion.so/campaign-brief",
    "type": "notion"
  },
  {
    "title": "Design Mockups",
    "url": "https://figma.com/mockups",
    "type": "figma"
  },
  {
    "title": "Customer Portal",
    "url": "https://portal.example.com",
    "type": "external"
  }
]
```

**Usage:** Store external references and related resources

---

### Next Steps Array
**Database Column:** `next_steps`  
**Type:** JSON Array of action item objects  
**Storage:** TEXT column containing JSON string

**Object Structure:**
```json
{
  "description": "String - Task description (REQUIRED)",
  "completed": "Boolean - Completion status (REQUIRED)",
  "due_date": "String - ISO date (OPTIONAL)",
  "assigned_to": "String - Person assigned (OPTIONAL)"
}
```

**Complete Example:**
```json
[
  {
    "description": "Create quote for Leanne Catalano - Corflute signs (4 size options)",
    "completed": false,
    "due_date": "2025-11-10T00:00:00Z",
    "assigned_to": "Sales Team"
  },
  {
    "description": "Send follow-up email to John Smith",
    "completed": true,
    "due_date": "2025-11-08T00:00:00Z"
  },
  {
    "description": "Update quote tracking spreadsheet",
    "completed": false
  }
]
```

**Usage:** Track action items and to-dos for the project. Displays with checkboxes in UI.

---

### Assignees Array
**Database Column:** `assignees`  
**Type:** JSON Array of strings  
**Storage:** TEXT column containing JSON string

**Structure:**
```json
["Person Name 1", "Person Name 2", "Person Name 3"]
```

**Example:**
```json
["John Doe", "AI Assistant", "Sales Team", "Marketing Manager"]
```

**Usage:** Track people/teams assigned to work on this card

---

### Checklist Array
**Database Column:** `checklist`  
**Type:** JSON Array of checklist item objects  
**Storage:** TEXT column containing JSON string

**Object Structure:**
```json
{
  "item": "String - Checklist item text (REQUIRED)",
  "completed": "Boolean - Completion status (REQUIRED)"
}
```

**Complete Example:**
```json
[
  {
    "item": "Gather customer requirements",
    "completed": true
  },
  {
    "item": "Create initial quote draft",
    "completed": true
  },
  {
    "item": "Review quote with manager",
    "completed": false
  },
  {
    "item": "Send quote to customer",
    "completed": false
  }
]
```

**Usage:** Track completion of sub-tasks. Shows progress (e.g., "2/4 completed") in UI.

---

### Recent Activity Array
**Database Column:** `recent_activity`  
**Type:** JSON Array of activity log objects  
**Storage:** TEXT column containing JSON string

**Object Structure:**
```json
{
  "type": "String - Activity type (REQUIRED)",
  "timestamp": "String - ISO timestamp (REQUIRED)",
  "user": "String - User who performed action (REQUIRED)",
  "description": "String - Activity description (OPTIONAL)"
}
```

**Complete Example:**
```json
[
  {
    "type": "created",
    "timestamp": "2025-11-07T22:11:43.207462",
    "user": "AI Agent",
    "description": "Session created"
  },
  {
    "type": "updated",
    "timestamp": "2025-11-08T10:30:00.000000",
    "user": "John Doe",
    "description": "Added 3 documents"
  },
  {
    "type": "comment",
    "timestamp": "2025-11-08T14:15:00.000000",
    "user": "Sales Team",
    "description": "Customer confirmed pricing acceptable"
  }
]
```

**Usage:** Audit trail of all actions taken on this card

---

### Thread IDs Array
**Database Column:** `thread_ids`  
**Type:** JSON Array of strings (thread identifiers)  
**Storage:** TEXT column containing JSON string

**Structure:**
```json
["thread_id_1", "thread_id_2", "thread_id_3"]
```

**Example:**
```json
["1762602241803", "1762602241804", "1762602241805"]
```

**Note:** These IDs reference threads in the `sessions.db` database (threads table). Used to link conversation threads to synergy cards.

**Usage:** Connect AI conversation threads to project cards for context

---

### Assigned Agents Array
**Database Column:** `assigned_agents`  
**Type:** JSON Array of strings (agent names)  
**Storage:** TEXT column containing JSON string

**Structure:**
```json
["Agent Name 1", "Agent Name 2"]
```

**Example:**
```json
["Prime Agent", "Alpha-3", "Beta-2"]
```

**Usage:** Track which AI agents are working on this project

---

## Fields NOT in Database (Computed at Display Time)

These fields appear in the UI but are NOT stored in `synergy_sessions`:

### 1. `message_count`
- **Source:** Computed from linked threads
- **Location:** Not stored in synergy_sessions
- **Calculation:** Count of messages across all linked thread_ids
- **Display:** Shows in collapsed view statistics

### 2. `project_name`
- **Source:** Either from mock data or derived from title/description
- **Location:** Not a database column
- **Fallback:** Uses "No Project" if not set
- **Display:** Shows in card meta section

### 3. `synergy_card_name`
- **Source:** Thread assignment data
- **Location:** Referenced in thread_details API but not stored
- **Purpose:** Links threads back to their synergy card

---

## API Endpoints

### Get All Sessions
```http
GET /api/synergy/list
```

**Response:**
```json
{
  "success": true,
  "count": 15,
  "sessions": [
    {
      "session_id": "sess_20251107_2211_email_thread_quote_processing_",
      "title": "Email Thread Quote Processing",
      "description": "Processing 10 customer email inquiries...",
      "status": "active",
      "priority": "high",
      "kanban_column": "in_progress",
      "tags": ["quotes", "customer_service"],
      "documents": [/* array of document objects */],
      "thread_ids": ["1762602241803"],
      // ... all other fields
    }
  ]
}
```

### Get Thread Details (for linked threads display)
```http
POST /api/threads/details
Content-Type: application/json

{
  "thread_ids": ["1762602241803", "1762602241804"]
}
```

**Response:**
```json
{
  "success": true,
  "data": [
    {
      "id": "1762602241803",
      "thread_slug": "email-thread-quotes",
      "name": "Email Thread Quotes",
      "created": "2025-11-07T22:00:00Z",
      "updated": "2025-11-08T21:44:01Z",
      "synergy_card_id": "sess_20251107_2211_email_thread_quote_processing_",
      "agent_id": "prime",
      "agent_name": "PRIME"
    }
  ]
}
```

---

## Data Flow

### 1. Card Creation
```
User/AI creates session
  → POST /api/synergy/sessions
  → Saves to synergy_sessions.db
  → Returns session object with JSON fields parsed
```

### 2. Card Display
```
Page loads
  → GET /api/synergy/list
  → Receives all sessions with JSON strings
  → JavaScript parses JSON fields to arrays/objects
  → renderCard() creates HTML
  → Displays collapsed view by default
```

### 3. Document Display
```
Card expanded
  → parseJsonField(session.documents, [])
  → Iterates over document objects
  → Renders each document with name, size, icon
  → Clicking document opens URL
```

### 4. Linked Threads
```
Card rendered
  → Checks session.thread_ids
  → If present, calls POST /api/threads/details
  → Receives thread data from sessions.db
  → Renders linked threads section asynchronously
```

---

## Key Files

### Frontend
- **HTML:** `UI/business-ai-platform-v2.html`
  - Lines 22956-23300: `renderCard()`, `renderCardExpanded()`, `renderCardCollapsed()`
  - Lines 24455-24520: `renderLinkedThreads()`

### Backend
- **Synergy Routes:** `AI_infrastructure/routes/synergy_routes.py`
  - Lines 44-67: Database schema creation
  - Lines 90-143: `/list` endpoint
- **Thread Routes:** `AI_infrastructure/routes/thread_routes.py`
  - Lines 920-1065: `/details` endpoint

### Database
- **Synergy DB:** `data/synergy_sessions.db` (single table: synergy_sessions)
- **Threads DB:** `data/sessions.db` (threads table with thread assignments)

---

## Document Section - Complete Breakdown

### Storage
- **Database Column:** `synergy_sessions.documents`
- **Data Type:** TEXT (JSON string)
- **Can be NULL:** Yes
- **Default:** NULL (empty)

### Structure When Populated
```json
[
  {
    "name": "String - Display name of document (REQUIRED)",
    "url": "String - Full URL to document (REQUIRED)",
    "size": "String - Human-readable size (OPTIONAL)",
    "type": "String - Document type identifier (OPTIONAL)",
    "created_at": "String - ISO timestamp (OPTIONAL)"
  }
]
```

### Required Fields
- `name` - Must have a name to display
- `url` - Must have a URL to link to

### Optional Fields
- `size` - Displays file size (e.g., "1.2 MB", "45 KB")
- `type` - Can be used for custom icons (google_doc, google_sheet, pdf, etc.)
- `created_at` - Timestamp for sorting or display

### Empty State
If `documents` is NULL or empty array:
- Collapsed view: Shows "0" in document count
- Expanded view: Does not show Documents section at all

### Example Usage

**Creating a session with documents:**
```python
import json

documents = [
    {
        "name": "Project Proposal",
        "url": "https://docs.google.com/document/d/abc123",
        "type": "google_doc"
    },
    {
        "name": "Budget Spreadsheet",
        "url": "https://sheets.google.com/spreadsheets/d/xyz789",
        "size": "128 KB",
        "type": "google_sheet"
    }
]

# Store as JSON string in database
documents_json = json.dumps(documents)
# Result: '[{"name":"Project Proposal",...}]'
```

**Retrieving and displaying:**
```javascript
// In JavaScript frontend
const documents = JSON.parse(session.documents || '[]');

documents.forEach(doc => {
    console.log(`Document: ${doc.name}`);
    console.log(`URL: ${doc.url}`);
    console.log(`Size: ${doc.size || 'N/A'}`);
});
```

---

## Quick Reference - All JSON Array Fields

| Database Column | Array Type | Object Structure | Required Fields | Optional Fields |
|-----------------|------------|------------------|-----------------|-----------------|
| `platforms_involved` | Simple strings | `["string1", "string2"]` | N/A | N/A |
| `tags` | Simple strings | `["string1", "string2"]` | N/A | N/A |
| `documents` | Objects | `{name, url, size, type, created_at}` | name, url | size, type, created_at |
| `links` | Objects | `{title, url, type}` | title, url | type |
| `next_steps` | Objects | `{description, completed, due_date, assigned_to}` | description, completed | due_date, assigned_to |
| `assignees` | Simple strings | `["string1", "string2"]` | N/A | N/A |
| `recent_activity` | Objects | `{type, timestamp, user, description}` | type, timestamp, user | description |
| `checklist` | Objects | `{item, completed}` | item, completed | None |
| `thread_ids` | Simple strings | `["string1", "string2"]` | N/A | N/A |
| `assigned_agents` | Simple strings | `["string1", "string2"]` | N/A | N/A |

---

## Summary

### Core Database Fields (23 columns)

**Simple TEXT Fields (13):**
- Identity: `session_id` (PK)
- Basic: `title`, `description`, `status`, `priority`, `kanban_column`
- Dates: `created_at`, `last_active`, `completed_at`, `due_date`
- Integrations: `google_task_id`, `google_calendar_id`, `microsoft_todo_id`

**JSON Array Fields (10):**
1. `platforms_involved` - Simple string array
2. `tags` - Simple string array
3. `documents` - Object array (name, url, size, type, created_at)
4. `links` - Object array (title, url, type)
5. `next_steps` - Object array (description, completed, due_date, assigned_to)
6. `assignees` - Simple string array
7. `recent_activity` - Object array (type, timestamp, user, description)
8. `checklist` - Object array (item, completed)
9. `thread_ids` - Simple string array (references threads in sessions.db)
10. `assigned_agents` - Simple string array

### Document Section Specifically
- **Column:** `documents` (TEXT, JSON Array of objects)
- **Required fields:** name, url
- **Optional fields:** size, type, created_at
- **Display:** Document count in collapsed view, full list in expanded view
- **Access:** Parsed from JSON string to JavaScript array

### Computed at Display Time (NOT in DB)
- `message_count` - Calculated from linked threads
- `project_name` - From mock data or derived from title

### Data Flow
Database (JSON string) → API (parsed to array) → JavaScript (array of objects) → HTML (rendered list)

---

**Last Updated:** November 9, 2025  
**Author:** AI Agent (Documentation Generator)

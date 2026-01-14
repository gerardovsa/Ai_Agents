# How Synergy Sessions and Threads Get Linked

## Overview

Threads (AI conversations) can be linked to Synergy Cards (Kanban tasks) using a **simple foreign key relationship** stored in the `synergy_card_id` column.

---

## Database Architecture

### **Two Separate Databases:**

```
data/
├── sessions.db           # Thread data
│   └── threads table
│       └── synergy_card_id column (TEXT, nullable)
│
└── synergy_sessions.db   # Synergy Kanban data
    └── synergy_sessions table
        └── session_id column (TEXT, primary key)
```

### **Linking Field:**
```sql
-- threads table in sessions.db
CREATE TABLE threads (
    ...
    synergy_card_id TEXT DEFAULT NULL,  -- Foreign key to synergy_sessions.session_id
    ...
);

-- synergy_sessions table in synergy_sessions.db
CREATE TABLE synergy_sessions (
    session_id TEXT PRIMARY KEY,        -- Referenced by threads.synergy_card_id
    title TEXT NOT NULL,
    project TEXT,
    kanban_column TEXT,
    ...
);
```

---

## How Linking Works - Step by Step

### **1. User Interface Flow:**

```
[Thread in sidebar]
    ↓
[User clicks 🔗 Synergy button]
    ↓
[Modal shows list of available Synergy cards]
    ↓
[User selects a card]
    ↓
[Thread is linked to Synergy card]
    ↓
[Badge appears showing 🎯 Synergy link]
```

### **2. Frontend Code Flow:**

**Step 1: User clicks Synergy button**
```javascript
// In business-ai-platform-v2.html
<button onclick="ThreadManager.showSynergyCardPicker('thread-123')">
    🔗 Link to Synergy
</button>
```

**Step 2: Fetch available Synergy cards**
```javascript
async showSynergyCardPicker(threadId) {
    // Call backend to get list of Synergy cards
    const response = await fetch('/api/synergy/sessions');
    const sessions = await response.json();
    
    // sessions = [
    //   {session_id: 'sess_20251107_budget_review', title: 'Budget Review', ...},
    //   {session_id: 'sess_20251107_client_meeting', title: 'Client Meeting', ...}
    // ]
    
    // Show modal with cards
    // User clicks on a card...
}
```

**Step 3: Link thread to selected card**
```javascript
async linkToSynergyCard(threadId, synergyCardId) {
    // Update thread object
    const thread = this.threads.find(t => t.id === threadId);
    thread.synergy_card_id = synergyCardId;  // e.g., 'sess_20251107_budget_review'
    
    // Save to backend
    await fetch('/api/threads/save', {
        method: 'POST',
        body: JSON.stringify({
            thread_id: threadId,
            synergy_card_id: synergyCardId  // Store the link!
        })
    });
    
    // Update UI to show badge
    this.renderThreadList();
}
```

### **3. Backend Processing:**

**Endpoint: POST /api/threads/save**
```python
# In AI_infrastructure/routes/thread_routes.py

@thread_bp.route('/save', methods=['POST'])
def save_thread():
    data = request.get_json()
    
    thread_id = data.get('thread_id')
    synergy_card_id = data.get('synergy_card_id')  # Can be session_id or null
    
    # Save to database
    db_path = get_sessions_database_path()  # data/sessions.db
    
    query = """
        UPDATE threads 
        SET synergy_card_id = ?,
            updated_at = CURRENT_TIMESTAMP
        WHERE thread_slug = ?
    """
    
    execute_sqlite_update(db_path, query, (synergy_card_id, thread_id))
    
    return success_response({'saved': True})
```

### **4. Database Storage:**

**After linking, the database looks like this:**

```sql
-- sessions.db > threads table
SELECT thread_slug, name, synergy_card_id FROM threads;

thread_slug          | name                  | synergy_card_id
---------------------|------------------------|---------------------------
1762192838469        | "Budget Discussion"   | sess_20251107_budget_review
1762193002345        | "Client Questions"    | sess_20251107_client_meeting
1762194567890        | "General Chat"        | NULL (not linked)
```

```sql
-- synergy_sessions.db > synergy_sessions table
SELECT session_id, title, kanban_column FROM synergy_sessions;

session_id                   | title             | kanban_column
-----------------------------|-------------------|---------------
sess_20251107_budget_review  | Budget Review     | in-progress
sess_20251107_client_meeting | Client Meeting    | backlog
```

---

## How Data Flows Between Systems

### **Frontend → Backend → Database**

```
┌─────────────────────────────────────────────────────────────┐
│ FRONTEND (business-ai-platform-v2.html)                     │
│                                                              │
│  1. User clicks "Link to Synergy" button                    │
│     ↓                                                        │
│  2. GET /api/synergy/sessions                               │
│     ↓                                                        │
│  3. Display modal with Synergy cards                        │
│     ↓                                                        │
│  4. User selects card "sess_20251107_budget_review"         │
│     ↓                                                        │
│  5. POST /api/threads/save {synergy_card_id: "sess_..."}    │
└─────────────────────────────────────────────────────────────┘
                             ↓
┌─────────────────────────────────────────────────────────────┐
│ BACKEND (Flask - thread_routes.py)                          │
│                                                              │
│  6. Receive POST /api/threads/save request                  │
│     ↓                                                        │
│  7. Extract synergy_card_id from JSON                       │
│     ↓                                                        │
│  8. UPDATE threads SET synergy_card_id = ? WHERE ...        │
└─────────────────────────────────────────────────────────────┘
                             ↓
┌─────────────────────────────────────────────────────────────┐
│ DATABASE (data/sessions.db)                                 │
│                                                              │
│  threads table:                                             │
│  ┌────────────────┬──────────────┬──────────────────────┐   │
│  │ thread_slug    │ name         │ synergy_card_id      │   │
│  ├────────────────┼──────────────┼──────────────────────┤   │
│  │ 1762192838469  │ Budget Talk  │ sess_20251107_...    │   │
│  └────────────────┴──────────────┴──────────────────────┘   │
└─────────────────────────────────────────────────────────────┘
```

---

## API Endpoints Involved

### **1. GET /api/synergy/sessions**
- **Purpose**: Get list of available Synergy cards to link to
- **File**: `AI_infrastructure/routes/synergy_routes.py` (line 135)
- **Database**: `data/synergy_sessions.db`
- **Response**:
```json
[
  {
    "session_id": "sess_20251107_budget_review",
    "title": "Budget Review",
    "project": "Q4 Planning",
    "column": "in-progress"
  },
  {
    "session_id": "sess_20251107_client_meeting",
    "title": "Client Meeting",
    "project": "Acme Corp",
    "column": "backlog"
  }
]
```

### **2. POST /api/threads/save**
- **Purpose**: Save thread with synergy_card_id link
- **File**: `AI_infrastructure/routes/thread_routes.py` (line 268)
- **Database**: `data/sessions.db`
- **Request**:
```json
{
  "thread_id": "1762192838469",
  "user_id": 1,
  "synergy_card_id": "sess_20251107_budget_review"
}
```
- **Response**:
```json
{
  "success": true,
  "saved": true
}
```

### **3. GET /api/threads/list**
- **Purpose**: Load threads with their Synergy links
- **File**: `AI_infrastructure/routes/thread_routes.py` (line 118)
- **Database**: `data/sessions.db`
- **Response**:
```json
{
  "success": true,
  "threads": [
    {
      "id": "1762192838469",
      "title": "Budget Discussion",
      "synergy_card_id": "sess_20251107_budget_review",
      "location": "prime",
      "tags": ["finance", "Q4"]
    }
  ]
}
```

---

## Frontend Implementation Details

### **Key Methods in ThreadManager:**

**1. showSynergyCardPicker(threadId)**
```javascript
// Location: business-ai-platform-v2.html, line ~15660
// - Fetches Synergy cards from /api/synergy/sessions
// - Displays modal with card list
// - Attaches click listeners to cards
```

**2. linkToSynergyCard(threadId, synergyCardId)**
```javascript
// Location: business-ai-platform-v2.html, line ~15738
// - Updates thread.synergy_card_id
// - Saves to backend via POST /api/threads/save
// - Updates UI to show badge
```

**3. unlinkFromSynergyCard(threadId)**
```javascript
// Location: business-ai-platform-v2.html, line ~15777
// - Sets thread.synergy_card_id = null
// - Saves to backend
// - Removes badge from UI
```

**4. renderThreadList()**
```javascript
// Location: business-ai-platform-v2.html, line ~14512
// - Fetches threads with /api/threads/list
// - Displays 🎯 badge if synergy_card_id exists
// - Badge shows card title on hover
```

---

## UI Elements

### **Synergy Button:**
```html
<button class="btn-icon" onclick="ThreadManager.showSynergyCardPicker('thread-123')">
    🔗 Synergy
</button>
```

### **Synergy Badge (when linked):**
```html
<span class="thread-badge synergy-badge" title="Linked to: Budget Review">
    🎯 Synergy
</span>
```

### **Synergy Picker Modal:**
```html
<div class="modal-overlay">
    <div class="synergy-picker-modal">
        <h3>🎯 Link to Synergy Card</h3>
        
        <div class="synergy-card-list">
            <div class="synergy-card-item" data-session-id="sess_...">
                <div class="card-title">Budget Review</div>
                <div class="card-meta">
                    <span class="card-project">Q4 Planning</span>
                    <span class="card-column">in-progress</span>
                </div>
            </div>
            <!-- More cards... -->
        </div>
        
        <button class="btn-secondary">Cancel</button>
    </div>
</div>
```

---

## Data Relationship Diagram

```
┌─────────────────────────────────────────────────────────────┐
│                    SYNERGY SESSIONS                         │
│                (synergy_sessions.db)                        │
│                                                              │
│  ┌───────────────────────────────────────────────────┐      │
│  │ synergy_sessions table                            │      │
│  ├───────────────────────────────────────────────────┤      │
│  │ session_id (PK)  │ title         │ kanban_column │      │
│  ├──────────────────┼───────────────┼───────────────┤      │
│  │ sess_2025...001  │ Budget Review │ in-progress   │ ←──┐ │
│  │ sess_2025...002  │ Client Meet   │ backlog       │ ←─┐│ │
│  └──────────────────┴───────────────┴───────────────┘   ││ │
└─────────────────────────────────────────────────────────┼┼─┘
                                                          ││
                                 Foreign Key Relationship ││
                                 (synergy_card_id)        ││
                                                          ││
┌─────────────────────────────────────────────────────────┼┼─┐
│                        THREADS                          ││ │
│                    (sessions.db)                        ││ │
│                                                          ││ │
│  ┌───────────────────────────────────────────────────┐  ││ │
│  │ threads table                                     │  ││ │
│  ├───────────────────────────────────────────────────┤  ││ │
│  │ thread_slug (PK) │ name          │ synergy_card_id│  ││ │
│  ├──────────────────┼───────────────┼────────────────┤  ││ │
│  │ 1762192838469    │ Budget Talk   │ sess_2025...001├──┘│ │
│  │ 1762193002345    │ Client Chat   │ sess_2025...002├───┘ │
│  │ 1762194567890    │ General       │ NULL           │     │
│  └──────────────────┴───────────────┴────────────────┘     │
└─────────────────────────────────────────────────────────────┘

Legend:
  ─── = Foreign Key Relationship
  (PK) = Primary Key
  NULL = Not linked to any Synergy card
```

---

## Example: Complete Linking Flow

### **Scenario**: Link "Budget Discussion" thread to "Budget Review" Synergy card

**Step 1: Initial State**
```sql
-- threads table
thread_slug: "1762192838469"
name: "Budget Discussion"
synergy_card_id: NULL  ← Not linked yet
```

**Step 2: User Action**
- Opens thread "Budget Discussion"
- Clicks 🔗 Synergy button in sidebar

**Step 3: Frontend Fetches Cards**
```javascript
GET /api/synergy/sessions

Response:
[
  {
    session_id: "sess_20251107_budget_review",
    title: "Budget Review",
    project: "Q4 Planning",
    column: "in-progress"
  },
  // ... more cards
]
```

**Step 4: Modal Displays**
```
┌────────────────────────────────────┐
│  🎯 Link to Synergy Card           │
│                                    │
│  ┌──────────────────────────────┐ │
│  │ Budget Review                │ │ ← User clicks here
│  │ Q4 Planning • in-progress    │ │
│  └──────────────────────────────┘ │
│                                    │
│  ┌──────────────────────────────┐ │
│  │ Client Meeting               │ │
│  │ Acme Corp • backlog          │ │
│  └──────────────────────────────┘ │
│                                    │
│  [Cancel]                          │
└────────────────────────────────────┘
```

**Step 5: Frontend Saves Link**
```javascript
POST /api/threads/save
{
  "thread_id": "1762192838469",
  "user_id": 1,
  "synergy_card_id": "sess_20251107_budget_review"
}
```

**Step 6: Backend Updates Database**
```sql
UPDATE threads 
SET synergy_card_id = 'sess_20251107_budget_review',
    updated_at = CURRENT_TIMESTAMP
WHERE thread_slug = '1762192838469'
```

**Step 7: Final State**
```sql
-- threads table
thread_slug: "1762192838469"
name: "Budget Discussion"
synergy_card_id: "sess_20251107_budget_review"  ← NOW LINKED!
```

**Step 8: UI Updates**
```
Thread sidebar now shows:

┌──────────────────────────────┐
│ Budget Discussion            │
│ 🎯 Synergy: Budget Review    │ ← Badge appears!
│ Nov 7, 2:30 PM               │
└──────────────────────────────┘
```

---

## Unlinking Process

**To remove the link:**

```javascript
// User clicks "Unlink" button
await ThreadManager.unlinkFromSynergyCard('1762192838469');

// Backend call
POST /api/threads/save
{
  "thread_id": "1762192838469",
  "synergy_card_id": null  ← Set to null
}

// Database update
UPDATE threads 
SET synergy_card_id = NULL
WHERE thread_slug = '1762192838469'

// Result: Badge disappears from UI
```

---

## Key Files

| File | Purpose | Lines |
|------|---------|-------|
| `AI_infrastructure/routes/thread_routes.py` | Thread CRUD with synergy_card_id | 268-500 |
| `AI_infrastructure/routes/synergy_routes.py` | Synergy session endpoints | 135-165 |
| `UI/business-ai-platform-v2.html` | Frontend linking UI | 15660-15820 |
| `data/sessions.db` | Thread storage | threads.synergy_card_id |
| `data/synergy_sessions.db` | Synergy card storage | synergy_sessions.session_id |

---

## Testing the Link

**Quick test from browser console:**

```javascript
// 1. Get available Synergy cards
const cards = await fetch('/api/synergy/sessions').then(r => r.json());
console.log(cards);

// 2. Link current thread to first card
const threadId = ThreadManager.currentThreadId;
const cardId = cards[0].session_id;

await ThreadManager.linkToSynergyCard(threadId, cardId);
// Should see: ✅ [linkToSynergyCard] Linked to backend

// 3. Verify in database
// Open: data/sessions.db
// Query: SELECT synergy_card_id FROM threads WHERE thread_slug = ?
```

---

## Summary

**The linking is simple:**

1. **Storage**: `threads.synergy_card_id` → `synergy_sessions.session_id`
2. **UI**: 🔗 Button → Modal → Select card → Save
3. **Backend**: POST /api/threads/save with synergy_card_id
4. **Display**: 🎯 Badge shows when linked
5. **Persistence**: Both databases maintain their own data, linked by ID

**No complex join tables, no sync issues** - just a straightforward foreign key reference stored in the threads table!

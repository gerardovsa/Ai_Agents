# Thread System Architecture

**Last Updated:** January 18, 2026  
**Components:** Thread Manager, Thread Cards, Thread Assignments, Locations  
**Database:** sessions schema (threads, messages, thread_assignments tables)  
**Frontend:** business-ai-platform-v2.html (ThreadManager class)

> **📘 CONSOLIDATED DOCUMENTATION**  
> This is the **master thread system documentation** consolidating thread management, isolation, metadata, locations, and UI components. Supersedes 63+ scattered thread files.

---

## 🎯 Quick Reference

### What is a Thread?

A **thread** is a persistent conversation with an AI agent containing:
- **Messages** - User inputs and AI responses
- **Location** - Where it's displayed (Prime, Agent-1 through Agent-26)
- **Metadata** - Title, tags, linked Synergy cards, workflows
- **Slug** - Unique URL-safe identifier (`th_a3f8b2c1_1733049600`)

### Thread Lifecycle

```
┌──────────────────────────────────────────────────────────┐
│ 1. CREATE    → User sends first message                  │
│ 2. ASSIGN    → Place in location (Prime/Agent column)    │
│ 3. PERSIST   → Save to database + localStorage           │
│ 4. UPDATE    → Add messages, change metadata             │
│ 5. MOVE      → Drag to different agent column            │
│ 6. LINK      → Connect to Synergy card or workflow       │
│ 7. SHARE     → Grant access to other users (future)      │
│ 8. ARCHIVE   → Save to saved_threads table               │
│ 9. DELETE    → Remove from database                      │
└──────────────────────────────────────────────────────────┘
```

---

## 🏗️ Architecture Overview

### Three-Layer System

```
┌─────────────────────────────────────────────────────────────┐
│                    FRONTEND (UI Layer)                       │
│  ┌──────────────────────────────────────────────────────┐  │
│  │  ThreadManager (JavaScript Class)                     │  │
│  │  • Thread CRUD operations                             │  │
│  │  • Location management (Prime/Agent-1/etc.)           │  │
│  │  │  • UI rendering and card display                    │  │
│  │  • localStorage synchronization                       │  │
│  └──────────────────────────────────────────────────────┘  │
│                        ↕ REST API                            │
│  ┌──────────────────────────────────────────────────────┐  │
│  │  thread_routes.py (Flask Blueprint)                   │  │
│  │  • /api/thread/* endpoints                            │  │
│  │  • Thread isolation enforcement                       │  │
│  │  • Message persistence                                │  │
│  └──────────────────────────────────────────────────────┘  │
│                        ↕ SQL                                 │
│  ┌──────────────────────────────────────────────────────┐  │
│  │  sessions.threads (PostgreSQL)                        │  │
│  │  sessions.messages                                    │  │
│  │  sessions.thread_assignments                          │  │
│  └──────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────┘
```

---

## 📊 Database Schema

### sessions.threads Table

```sql
CREATE TABLE sessions.threads (
    id SERIAL PRIMARY KEY,
    slug VARCHAR(100) UNIQUE NOT NULL,
    title VARCHAR(500),
    user_id INTEGER NOT NULL,
    agent VARCHAR(50), -- 'prime', 'agent-1', 'agent-2', etc.
    ai_model VARCHAR(50) DEFAULT 'claude-3-5-sonnet',
    system_prompt TEXT,
    synergy_card_id INTEGER, -- Link to synergy_sessions.synergy_sessions(id)
    workflow_slug VARCHAR(100), -- Link to public.visual_automations(slug)
    tags TEXT[],
    metadata JSONB,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_threads_user_id ON sessions.threads(user_id);
CREATE INDEX idx_threads_slug ON sessions.threads(slug);
CREATE INDEX idx_threads_agent ON sessions.threads(agent);
```

**Key Fields:**

- **slug** - Unique identifier format: `th_<random8>_<timestamp>`
  - Example: `th_a3f8b2c1_1733049600`
  - Used in URLs, localStorage keys, API calls
  - Generated once on creation, never changes

- **agent** - Current location (where thread is displayed)
  - Values: `prime`, `agent-1` through `agent-26` (Alpha → Zulu)
  - Null = thread exists but not assigned to location
  - Can change via drag-and-drop

- **synergy_card_id** - Bidirectional link to Kanban board
  - Allows threads to be part of project management workflow
  - Card can have multiple threads: `synergy_sessions.linked_thread_ids[]`

- **workflow_slug** - Link to automation workflow
  - Threads can trigger/monitor automated workflows
  - Soft foreign key to `public.visual_automations`

- **tags** - Array of strings for categorization
  - Examples: `['urgent', 'customer-support', 'quote-calculation']`
  - Used for filtering and search

- **metadata** - JSON object for extensibility
  - Custom fields per client deployment
  - Examples: `{"priority": "high", "department": "sales"}`

---

### sessions.messages Table

```sql
CREATE TABLE sessions.messages (
    id SERIAL PRIMARY KEY,
    thread_id INTEGER REFERENCES threads(id) ON DELETE CASCADE,
    role VARCHAR(20) NOT NULL, -- 'user', 'assistant', 'system'
    content TEXT NOT NULL,
    tool_results JSONB,
    thinking_content TEXT, -- Claude extended thinking
    token_count INTEGER,
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_messages_thread_id ON sessions.messages(thread_id);
CREATE INDEX idx_messages_created_at ON sessions.messages(created_at);
```

**Message Types:**

1. **user** - User input
   ```json
   {
     "role": "user",
     "content": "Calculate quote for 1000 business cards"
   }
   ```

2. **assistant** - AI response
   ```json
   {
     "role": "assistant",
     "content": "I'll calculate that quote for you...",
     "tool_results": {
       "tool_use_id": "toolu_123",
       "tool_name": "calculate_business_card_quote",
       "tool_input": {"quantity": 1000, "stock": "satin_350gsm"},
       "tool_result": {"price": 285, "breakdown": {...}}
     },
     "thinking_content": "User wants business card quote. I should use the calculator tool...",
     "token_count": 1523
   }
   ```

3. **system** - System notifications
   ```json
   {
     "role": "system",
     "content": "Thread linked to Synergy card: Project Alpha"
   }
   ```

---

### sessions.thread_assignments Table

```sql
CREATE TABLE sessions.thread_assignments (
    id SERIAL PRIMARY KEY,
    thread_id INTEGER REFERENCES threads(id) ON DELETE CASCADE,
    user_id INTEGER NOT NULL,
    location VARCHAR(50) NOT NULL, -- 'prime', 'agent-1', etc.
    email_thread_id VARCHAR(255), -- For communication hub threads
    email_subject TEXT,
    email_participants JSONB,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    UNIQUE(thread_id, user_id)
);

CREATE INDEX idx_thread_assignments_user_id ON sessions.thread_assignments(user_id);
CREATE INDEX idx_thread_assignments_location ON sessions.thread_assignments(location);
```

**Purpose:** Track thread locations per user

**Why Separate Table?**
- Allows multi-device synchronization
- Enables real-time updates via Supabase subscriptions
- Supports future multi-user thread sharing
- Separates location (UI state) from thread (data)

---

## 🎨 Frontend Architecture

### ThreadManager Class

**File:** `UI/business-ai-platform-v2.html` (Lines ~5000-8000)

**Core Methods:**

```javascript
class ThreadManager {
    constructor() {
        this.threads = [];           // All threads loaded from database
        this.activeThread = null;    // Currently selected thread
        this.localStorage = window.localStorage;
    }
    
    // CRUD Operations
    async createThread(title, agent = 'prime')
    async loadThread(slug)
    async saveThread(thread)
    async deleteThread(slug)
    
    // Location Management
    async moveThreadToAgent(slug, agentName)
    getThreadsByAgent(agentName)
    getThreadByAgent(agentName)
    
    // Metadata
    async updateThreadTitle(slug, newTitle)
    async updateThreadTags(slug, tags)
    async linkThreadToSynergy(slug, cardId)
    async linkThreadToWorkflow(slug, workflowSlug)
    
    // UI Rendering
    renderThreadCard(thread, container)
    renderThreadList(location)
    expandThreadCard(cardElement)
    collapseThreadCard(cardElement)
    
    // Synchronization
    syncToLocalStorage()
    syncFromDatabase()
    syncThreadAssignments()
}
```

---

### Thread Creation Flow

```javascript
// 1. User sends first message in Prime panel
async function handlePrimeMessage(userInput) {
    // Check if thread exists
    let thread = ThreadManager.getThreadByAgent('prime');
    
    if (!thread) {
        // Create new thread
        const slug = generateThreadSlug(); // th_<random>_<timestamp>
        
        thread = await ThreadManager.createThread({
            slug: slug,
            title: extractTitle(userInput), // First 50 chars
            agent: 'prime',
            user_id: getCurrentUserId(),
            ai_model: 'claude-3-5-sonnet'
        });
        
        // Save to database
        const response = await fetch('/api/thread/create', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify(thread)
        });
        
        // Add to thread list
        ThreadManager.threads.push(thread);
        ThreadManager.renderThreadCard(thread, 'sidebar-thread-list');
    }
    
    // Add message to thread
    await addMessageToThread(thread.slug, {
        role: 'user',
        content: userInput
    });
    
    // Send to AI
    streamAIResponse(thread.slug, userInput);
}
```

---

### Thread Slug Format

**Pattern:** `th_<8-char-hex>_<unix-timestamp>`

**Generation:**
```javascript
function generateThreadSlug() {
    const randomPart = Math.random().toString(16).substr(2, 8);
    const timestamp = Date.now();
    return `th_${randomPart}_${timestamp}`;
}

// Examples:
// th_a3f8b2c1_1733049600
// th_7e4f9a2c_1733050123
// th_d8c3b1a4_1733050456
```

**Benefits:**
- **Unique:** Random + timestamp = collision-free
- **Sortable:** Timestamp allows chronological sorting
- **Readable:** `th_` prefix clearly identifies threads
- **URL-safe:** No special characters, works in routes

---

## 📍 Thread Locations

### Available Locations

```
Prime Chat     → agent: 'prime'
Agent-1 (Alpha)  → agent: 'agent-1'
Agent-2 (Bravo)  → agent: 'agent-2'
Agent-3 (Charlie) → agent: 'agent-3'
...
Agent-26 (Zulu)  → agent: 'agent-26'
```

### Location Assignment Rules

1. **One thread per location** (per user)
   - User can only have 1 thread in Prime at a time
   - User can have 1 thread in each agent column
   - Total: 27 concurrent threads max (Prime + 26 agents)

2. **Drag-and-drop to move**
   - Drag thread card from sidebar to agent column
   - Automatically updates database
   - Previous thread in that location returns to sidebar

3. **Location persistence**
   - Stored in `sessions.thread_assignments` table
   - Synced across devices via WebSocket
   - Cached in localStorage for offline access

---

### Moving Threads

**Frontend:**
```javascript
// Drag thread card to Agent-3 column
async function onThreadDrop(threadSlug, targetAgent) {
    // Get current thread in Agent-3
    const existingThread = ThreadManager.getThreadByAgent(targetAgent);
    
    if (existingThread) {
        // Unassign existing thread
        await ThreadManager.moveThreadToAgent(existingThread.slug, null);
    }
    
    // Assign new thread to Agent-3
    await ThreadManager.moveThreadToAgent(threadSlug, targetAgent);
    
    // Update UI
    ThreadManager.renderThreadList('sidebar');
    ThreadManager.loadThreadInAgent(targetAgent, threadSlug);
}
```

**Backend:**
```python
@thread_bp.route('/assignments', methods=['POST'])
def assign_thread_location():
    """Assign thread to agent location."""
    data = request.json
    thread_id = data.get('thread_id')
    location = data.get('location')  # 'prime', 'agent-1', etc.
    user_id = data.get('user_id')
    
    # Delete existing assignment for this location
    execute_query("""
        DELETE FROM sessions.thread_assignments 
        WHERE user_id=%s AND location=%s
    """, (user_id, location))
    
    # Create new assignment
    execute_query("""
        INSERT INTO sessions.thread_assignments 
        (thread_id, user_id, location, created_at)
        VALUES (%s, %s, %s, NOW())
    """, (thread_id, user_id, location))
    
    # Update thread's agent field
    execute_query("""
        UPDATE sessions.threads 
        SET agent=%s, updated_at=NOW()
        WHERE id=%s
    """, (location, thread_id))
    
    return jsonify({'success': True})
```

---

## 🔒 Thread Isolation

### Critical Pattern: session_id === thread_id

**Problem:** Messages leaking between threads

**Cause:** Frontend sent messages from Thread A with session_id from Thread B

**Solution:** Always use `thread.id` as `session_id`

**Frontend Fix:**
```javascript
// ❌ WRONG: Random session ID
const sessionId = MultiAgent.sessions[agentId];  // Could be from different thread!
const thread = ThreadManager.getThreadByAgent(agentName);

// ✅ CORRECT: Thread ID as session ID
const thread = ThreadManager.getThreadByAgent(agentName);
const sessionId = thread ? thread.id : Date.now().toString();
MultiAgent.sessions[agentId] = sessionId;  // Sync to match thread
```

**Backend Fix:**
```python
# Enforce session_id === thread_id
if thread_id:
    if session_id != thread_id:
        print(f"⚠️  THREAD ISOLATION WARNING: session_id != thread_id")
        session_id = thread_id  # Force isolation
else:
    thread_id = session_id
```

**Result:**
- ✅ Messages always saved to correct thread
- ✅ Conversation history stays isolated
- ✅ No message leakage between threads

---

## 🎴 Thread Cards UI

### Card Structure

```html
<div class="thread-card" data-thread-slug="th_a3f8b2c1_1733049600">
    <!-- Header -->
    <div class="thread-card-header">
        <span class="thread-icon">💬</span>
        <span class="thread-title">Business Card Quote</span>
        <span class="thread-location-badge">Agent-3</span>
    </div>
    
    <!-- Metadata (Collapsed - 2 rows) -->
    <div class="thread-card-meta">
        <span class="thread-date">2 hours ago</span>
        <span class="thread-message-count">12 messages</span>
    </div>
    
    <!-- Expanded Content (Visible on hover - 6 rows) -->
    <div class="thread-card-expanded">
        <div class="thread-tags">
            <span class="tag">urgent</span>
            <span class="tag">quote-calculation</span>
        </div>
        
        <div class="thread-links">
            <a href="#" class="synergy-link">🎯 Project Alpha</a>
            <a href="#" class="workflow-link">⚙️ Quote Workflow</a>
        </div>
        
        <div class="thread-actions">
            <button class="btn-rename">✏️ Rename</button>
            <button class="btn-delete">🗑️ Delete</button>
            <button class="btn-share">👥 Share</button>
        </div>
    </div>
</div>
```

### Hover Expansion

**CSS:**
```css
.thread-card {
    height: 80px; /* 2 rows */
    transition: height 0.2s ease;
    overflow: hidden;
}

.thread-card:hover {
    height: 240px; /* 6 rows */
}

.thread-card-expanded {
    opacity: 0;
    max-height: 0;
    transition: opacity 0.2s ease, max-height 0.2s ease;
}

.thread-card:hover .thread-card-expanded {
    opacity: 1;
    max-height: 200px;
}
```

**Benefits:**
- Compact list view (more threads visible)
- Rich information on hover
- Smooth animation
- No need to click to see details

---

## 🔗 Thread Linking

### Link to Synergy Card

**Purpose:** Associate thread with project management card

**Frontend:**
```javascript
async function linkThreadToSynergy(threadSlug, cardId) {
    // Update thread
    await fetch('/api/thread/link-synergy', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({
            thread_slug: threadSlug,
            card_id: cardId
        })
    });
    
    // Show notification
    showToast(`Thread linked to Synergy card #${cardId}`);
    
    // Refresh thread card
    const thread = ThreadManager.getThreadBySlug(threadSlug);
    ThreadManager.renderThreadCard(thread, 'sidebar-thread-list');
}
```

**Backend:**
```python
@thread_bp.route('/link-synergy', methods=['POST'])
def link_thread_to_synergy():
    """Link thread to Synergy Kanban card."""
    data = request.json
    thread_slug = data.get('thread_slug')
    card_id = data.get('card_id')
    
    # Update thread
    execute_query("""
        UPDATE sessions.threads 
        SET synergy_card_id=%s, updated_at=NOW()
        WHERE slug=%s
    """, (card_id, thread_slug))
    
    # Get thread_id
    thread_id = execute_query("""
        SELECT id FROM sessions.threads WHERE slug=%s
    """, (thread_slug,), fetch_mode='value')
    
    # Update Synergy card (bidirectional link)
    execute_query("""
        UPDATE synergy_sessions.synergy_sessions
        SET linked_thread_ids = array_append(linked_thread_ids, %s),
            updated_at = NOW()
        WHERE id=%s AND NOT (%s = ANY(linked_thread_ids))
    """, (thread_id, card_id, thread_id), schema='synergy_sessions')
    
    return jsonify({'success': True})
```

**Use Cases:**
- Track all threads related to a project
- Navigate from Kanban card to conversations
- See project progress through thread activity

---

### Link to Workflow

**Purpose:** Associate thread with automation workflow

**Frontend:**
```javascript
async function linkThreadToWorkflow(threadSlug, workflowSlug) {
    await fetch('/api/thread/link-workflow', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({
            thread_slug: threadSlug,
            workflow_slug: workflowSlug
        })
    });
    
    showToast(`Thread linked to workflow: ${workflowSlug}`);
}
```

**Use Cases:**
- Trigger workflow from thread
- Monitor workflow execution in conversation
- Automate responses based on workflow output

---

## 💾 Data Persistence

### Dual Storage Pattern

Threads are stored in **two places** for different purposes:

1. **Database (Supabase PostgreSQL)** - Source of truth
   - Permanent storage
   - Shared across devices
   - Real-time sync via WebSocket

2. **localStorage (Browser)** - Performance cache
   - Fast access
   - Offline availability
   - Reduced database queries

---

### localStorage Structure

```javascript
// Thread assignments (which thread is in which location)
localStorage.setItem('thread_assignments', JSON.stringify({
    prime: 'th_a3f8b2c1_1733049600',
    'agent-1': 'th_7e4f9a2c_1733050123',
    'agent-3': 'th_d8c3b1a4_1733050456'
}));

// Thread metadata cache
localStorage.setItem('thread_th_a3f8b2c1_1733049600', JSON.stringify({
    slug: 'th_a3f8b2c1_1733049600',
    title: 'Business Card Quote',
    agent: 'agent-3',
    message_count: 12,
    last_updated: '2026-01-18T10:30:00Z'
}));

// Active thread (currently selected)
localStorage.setItem('active_thread', 'th_a3f8b2c1_1733049600');
```

---

### Synchronization Pattern

```javascript
// On page load
async function initializeThreads() {
    // 1. Load from localStorage (fast)
    const cachedAssignments = JSON.parse(localStorage.getItem('thread_assignments') || '{}');
    ThreadManager.renderFromCache(cachedAssignments);
    
    // 2. Fetch from database (authoritative)
    const response = await fetch('/api/thread/assignments?user_id=' + userId);
    const dbAssignments = await response.json();
    
    // 3. Sync differences
    if (JSON.stringify(cachedAssignments) !== JSON.stringify(dbAssignments)) {
        console.log('Thread assignments out of sync, updating...');
        localStorage.setItem('thread_assignments', JSON.stringify(dbAssignments));
        ThreadManager.renderFromDatabase(dbAssignments);
    }
}

// On thread change
async function onThreadUpdated(threadSlug) {
    // 1. Update database
    await fetch('/api/thread/update', {
        method: 'PUT',
        body: JSON.stringify({...})
    });
    
    // 2. Update localStorage
    const thread = ThreadManager.getThreadBySlug(threadSlug);
    localStorage.setItem(`thread_${threadSlug}`, JSON.stringify(thread));
    
    // 3. Broadcast to other tabs (same device)
    window.dispatchEvent(new CustomEvent('thread-updated', {
        detail: {thread_slug: threadSlug}
    }));
}
```

---

### Real-Time Sync (Supabase)

```javascript
// Subscribe to thread_assignments changes
const subscription = supabase
    .from('thread_assignments')
    .on('INSERT', payload => {
        console.log('Thread assigned:', payload.new);
        ThreadManager.handleAssignmentChange(payload.new);
    })
    .on('UPDATE', payload => {
        console.log('Thread moved:', payload.new);
        ThreadManager.handleAssignmentChange(payload.new);
    })
    .on('DELETE', payload => {
        console.log('Thread unassigned:', payload.old);
        ThreadManager.handleAssignmentRemove(payload.old);
    })
    .subscribe();
```

---

## 🔍 Thread Operations

### Create Thread

**Endpoint:** `POST /api/thread/create`

```python
@thread_bp.route('/create', methods=['POST'])
def create_thread():
    """Create new thread."""
    data = request.json
    
    # Generate slug if not provided
    slug = data.get('slug') or generate_thread_slug()
    
    # Insert thread
    thread_id = execute_query("""
        INSERT INTO sessions.threads 
        (slug, title, user_id, agent, ai_model, created_at, updated_at)
        VALUES (%s, %s, %s, %s, %s, NOW(), NOW())
        RETURNING id
    """, (
        slug,
        data.get('title', 'New Conversation'),
        data.get('user_id'),
        data.get('agent', 'prime'),
        data.get('ai_model', 'claude-3-5-sonnet')
    ), fetch_mode='value')
    
    # Create assignment if agent specified
    if data.get('agent'):
        execute_query("""
            INSERT INTO sessions.thread_assignments 
            (thread_id, user_id, location, created_at)
            VALUES (%s, %s, %s, NOW())
        """, (thread_id, data.get('user_id'), data.get('agent')))
    
    return jsonify({'success': True, 'thread_id': thread_id, 'slug': slug})
```

---

### Load Thread

**Endpoint:** `GET /api/thread/<slug>`

```python
@thread_bp.route('/<slug>', methods=['GET'])
def get_thread(slug):
    """Get thread by slug."""
    user_id = request.args.get('user_id')
    
    # Get thread
    thread = execute_query("""
        SELECT t.*, 
               (SELECT COUNT(*) FROM sessions.messages WHERE thread_id=t.id) as message_count,
               ta.location
        FROM sessions.threads t
        LEFT JOIN sessions.thread_assignments ta ON ta.thread_id=t.id AND ta.user_id=%s
        WHERE t.slug=%s AND t.user_id=%s
    """, (user_id, slug, user_id), fetch_mode='one')
    
    if not thread:
        return jsonify({'error': 'Thread not found'}), 404
    
    # Get messages
    messages = execute_query("""
        SELECT * FROM sessions.messages 
        WHERE thread_id=%s 
        ORDER BY created_at ASC
    """, (thread['id'],), fetch_mode='all')
    
    thread['messages'] = messages
    return jsonify({'success': True, 'thread': thread})
```

---

### Update Thread

**Endpoint:** `PUT /api/thread/<slug>`

```python
@thread_bp.route('/<slug>', methods=['PUT'])
def update_thread(slug):
    """Update thread metadata."""
    data = request.json
    user_id = data.get('user_id')
    
    # Build update query dynamically
    updates = []
    params = []
    
    if 'title' in data:
        updates.append("title=%s")
        params.append(data['title'])
    
    if 'tags' in data:
        updates.append("tags=%s")
        params.append(data['tags'])
    
    if 'system_prompt' in data:
        updates.append("system_prompt=%s")
        params.append(data['system_prompt'])
    
    if 'metadata' in data:
        updates.append("metadata=%s")
        params.append(json.dumps(data['metadata']))
    
    updates.append("updated_at=NOW()")
    
    # Execute update
    params.extend([slug, user_id])
    execute_query(f"""
        UPDATE sessions.threads 
        SET {', '.join(updates)}
        WHERE slug=%s AND user_id=%s
    """, tuple(params))
    
    return jsonify({'success': True})
```

---

### Delete Thread

**Endpoint:** `DELETE /api/thread/<slug>`

```python
@thread_bp.route('/<slug>', methods=['DELETE'])
def delete_thread(slug):
    """Delete thread and all messages."""
    user_id = request.args.get('user_id')
    
    # Get thread_id
    thread_id = execute_query("""
        SELECT id FROM sessions.threads 
        WHERE slug=%s AND user_id=%s
    """, (slug, user_id), fetch_mode='value')
    
    if not thread_id:
        return jsonify({'error': 'Thread not found'}), 404
    
    # Delete messages (CASCADE will handle this, but explicit for clarity)
    execute_query("""
        DELETE FROM sessions.messages WHERE thread_id=%s
    """, (thread_id,))
    
    # Delete assignments
    execute_query("""
        DELETE FROM sessions.thread_assignments WHERE thread_id=%s
    """, (thread_id,))
    
    # Delete thread
    execute_query("""
        DELETE FROM sessions.threads WHERE id=%s
    """, (thread_id,))
    
    return jsonify({'success': True})
```

---

## 🧪 Testing Thread System

### Manual Testing Checklist

**Thread Creation:**
- [ ] Create thread in Prime chat
- [ ] Thread appears in sidebar
- [ ] Thread has unique slug
- [ ] Thread saved to database
- [ ] Thread cached in localStorage

**Thread Assignment:**
- [ ] Drag thread to Agent-1 column
- [ ] Thread opens in Agent-1 panel
- [ ] Thread card shows "Agent-1" badge
- [ ] Database updated with location
- [ ] localStorage synced

**Thread Isolation:**
- [ ] Send message in Prime thread
- [ ] Message appears only in Prime thread
- [ ] Send message in Agent-1 thread
- [ ] Message appears only in Agent-1 thread
- [ ] No message leakage between threads

**Thread Metadata:**
- [ ] Rename thread
- [ ] Add tags to thread
- [ ] Link thread to Synergy card
- [ ] Link thread to workflow
- [ ] Changes persist after refresh

**Thread Persistence:**
- [ ] Create thread, refresh page
- [ ] Thread still visible in sidebar
- [ ] Thread location restored
- [ ] Messages still present
- [ ] Metadata unchanged

---

### Automated Tests

```python
# tests/test_threads.py
import pytest
from AI_infrastructure.shared.database_utils import execute_query

def test_create_thread():
    """Test thread creation."""
    response = client.post('/api/thread/create', json={
        'title': 'Test Thread',
        'user_id': 1,
        'agent': 'prime'
    })
    
    assert response.status_code == 200
    assert response.json['success'] == True
    assert 'slug' in response.json
    
    # Verify in database
    slug = response.json['slug']
    thread = execute_query(
        "SELECT * FROM sessions.threads WHERE slug=%s",
        (slug,),
        fetch_mode='one'
    )
    
    assert thread is not None
    assert thread['title'] == 'Test Thread'
    assert thread['agent'] == 'prime'

def test_thread_isolation():
    """Test that messages stay in correct thread."""
    # Create two threads
    thread1 = create_test_thread(user_id=1, agent='prime')
    thread2 = create_test_thread(user_id=1, agent='agent-1')
    
    # Add message to thread1
    add_message(thread1['id'], role='user', content='Message 1')
    
    # Add message to thread2
    add_message(thread2['id'], role='user', content='Message 2')
    
    # Verify isolation
    thread1_messages = get_messages(thread1['id'])
    thread2_messages = get_messages(thread2['id'])
    
    assert len(thread1_messages) == 1
    assert len(thread2_messages) == 1
    assert thread1_messages[0]['content'] == 'Message 1'
    assert thread2_messages[0]['content'] == 'Message 2'

def test_thread_assignment():
    """Test thread location assignment."""
    thread = create_test_thread(user_id=1)
    
    # Assign to Agent-3
    response = client.post('/api/thread/assignments', json={
        'thread_id': thread['id'],
        'user_id': 1,
        'location': 'agent-3'
    })
    
    assert response.status_code == 200
    
    # Verify assignment
    assignment = execute_query("""
        SELECT * FROM sessions.thread_assignments 
        WHERE thread_id=%s AND user_id=%s
    """, (thread['id'], 1), fetch_mode='one')
    
    assert assignment['location'] == 'agent-3'
```

---

## 🐛 Troubleshooting

### Issue: Messages appearing in wrong thread

**Symptom:** Message sent in Thread A appears in Thread B

**Cause:** `session_id !== thread_id`

**Solution:**
```javascript
// Frontend: Always use thread.id as session_id
const thread = ThreadManager.getThreadByAgent(agentName);
const sessionId = thread.id;  // Not MultiAgent.sessions[agentId]
```

---

### Issue: Thread not appearing in sidebar

**Symptom:** Thread created but not visible in sidebar

**Cause:** Thread assignment not created

**Solution:**
```python
# Backend: Always create assignment when creating thread
execute_query("""
    INSERT INTO sessions.thread_assignments 
    (thread_id, user_id, location, created_at)
    VALUES (%s, %s, %s, NOW())
""", (thread_id, user_id, 'prime'))
```

---

### Issue: Thread location not persisting

**Symptom:** Thread location resets after refresh

**Cause:** localStorage and database out of sync

**Solution:**
```javascript
// Frontend: Sync on every location change
async function onThreadMoved(threadSlug, newLocation) {
    // 1. Update database
    await fetch('/api/thread/assignments', {
        method: 'POST',
        body: JSON.stringify({thread_slug: threadSlug, location: newLocation})
    });
    
    // 2. Update localStorage
    const assignments = JSON.parse(localStorage.getItem('thread_assignments') || '{}');
    assignments[newLocation] = threadSlug;
    localStorage.setItem('thread_assignments', JSON.stringify(assignments));
}
```

---

### Issue: Thread slug collision

**Symptom:** "Unique constraint violation" on slug

**Cause:** Random part of slug not random enough

**Solution:**
```javascript
// Use crypto.randomUUID() for better randomness
function generateThreadSlug() {
    const uuid = crypto.randomUUID();
    const randomPart = uuid.split('-')[0]; // First 8 hex chars
    const timestamp = Date.now();
    return `th_${randomPart}_${timestamp}`;
}
```

---

## 📈 Performance Optimization

### Lazy Load Messages

```javascript
// Don't load all messages on thread open
async function loadThread(threadSlug, messageLimit = 50) {
    const response = await fetch(
        `/api/thread/${threadSlug}/messages?limit=${messageLimit}&offset=0`
    );
    const data = await response.json();
    
    // Show "Load more" button if more messages exist
    if (data.total > messageLimit) {
        showLoadMoreButton(threadSlug, messageLimit);
    }
    
    return data.messages;
}
```

---

### Cache Thread Metadata

```javascript
// Cache thread list to avoid repeated database queries
const THREAD_CACHE_TTL = 5 * 60 * 1000; // 5 minutes

class ThreadCache {
    constructor() {
        this.cache = new Map();
    }
    
    get(key) {
        const entry = this.cache.get(key);
        if (!entry) return null;
        
        if (Date.now() - entry.timestamp > THREAD_CACHE_TTL) {
            this.cache.delete(key);
            return null;
        }
        
        return entry.data;
    }
    
    set(key, data) {
        this.cache.set(key, {
            data: data,
            timestamp: Date.now()
        });
    }
}

const threadCache = new ThreadCache();
```

---

### Batch Thread Operations

```python
# Load multiple threads in one query
@thread_bp.route('/batch', methods=['POST'])
def get_threads_batch():
    """Get multiple threads by slugs."""
    slugs = request.json.get('slugs', [])
    user_id = request.json.get('user_id')
    
    if not slugs:
        return jsonify({'threads': []})
    
    placeholders = ','.join(['%s'] * len(slugs))
    threads = execute_query(f"""
        SELECT t.*,
               (SELECT COUNT(*) FROM sessions.messages WHERE thread_id=t.id) as message_count
        FROM sessions.threads t
        WHERE t.slug IN ({placeholders}) AND t.user_id=%s
    """, (*slugs, user_id), fetch_mode='all')
    
    return jsonify({'threads': threads})
```

---

## 📚 Related Documentation

- [ARCHITECTURE.md](ARCHITECTURE.md) - Overall system architecture
- [SUPABASE_DATABASE.md](SUPABASE_DATABASE.md) - Database schema details
- [AI_AGENTS.md](AI_AGENTS.md) - Multi-agent system architecture
- [SYNERGY_COLLABORATION.md](SYNERGY_COLLABORATION.md) - Kanban board integration

---

## 📋 Files Consolidated

This document consolidates the following 63 thread documentation files:

- THREAD_SYSTEM_CHANGES_SUMMARY.md
- THREAD_ISOLATION_FIX_COMPLETE.md
- THREAD_ASSIGNMENTS_EXPLAINED.md
- THREAD_CARD_EXPANSION_FIX_EXPLANATION.md
- THREAD_ENDPOINTS_DATABASE_ANALYSIS.md
- THREAD_INFO_CARD_EXPANSION_FIX_DEC12_2025.md
- THREAD_LOADING_SYSTEM_FIX_COMPLETE.md
- THREAD_METADATA_FIX_COMPLETE.md
- THREAD_SHARING_FIX_COMPLETE.md
- THREAD_SLUG_FIX_NOV19.md
- THREAD_SYNERGY_LINKING_COMPLETE.md
- THREAD_UNLOAD_FIX_COMPLETE.md
- THREADMANAGER_MODULE_MERGE_FIX_NOV21.md
- [And 50+ more thread-related files]

---

**Last Updated:** January 18, 2026  
**Document Version:** 1.0  
**Maintained By:** Valor Studio AI Development Team

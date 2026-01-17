# SYNERGY & COLLABORATION - Technical Documentation

**Version:** 2.1.0
**Status:** ✅ Production Ready
**Last Updated:** January 18, 2026
**Module Type:** Multi-Agent Coordination + Project Management

---

## 📋 Table of Contents

1. [Overview](#overview)
2. [Architecture](#architecture)
3. [Synergy Dashboard](#synergy-dashboard)
4. [Multi-Agent Coordination](#multi-agent-coordination)
5. [Thread System Integration](#thread-system-integration)
6. [Implementation Details](#implementation-details)
7. [API Reference](#api-reference)
8. [Configuration](#configuration)
9. [Critical Fixes](#critical-fixes)
10. [Testing & Debugging](#testing--debugging)
11. [Known Issues](#known-issues)
12. [Appendix](#appendix)

---

## Overview

### Purpose

The Synergy & Collaboration system provides two interconnected capabilities:

1. **Synergy Dashboard** - Visual Kanban-style project management system
2. **Multi-Agent Coordination** - 26 AI agents (Alpha→Zulu) working in parallel with cross-thread communication

Together, these systems enable complex multi-step projects to be broken down, distributed across AI agents, tracked visually, and coordinated automatically.

### Key Capabilities

**Synergy Dashboard:**
- 4-column Kanban board (Backlog → In Progress → Review → Done)
- Rich project cards with documents, links, checklists, notes
- Activity logs with icons and timestamps
- Bidirectional linking with AI threads
- Real-time updates via WebSocket (when enabled)

**Multi-Agent Coordination:**
- 26 NATO-named agents (Alpha, Bravo, Charlie... Zulu)
- Cross-thread request/response communication
- Automatic thread creation and resource assignment
- UI automation (tab switching, column highlighting)
- Synergy session linking for unified project view

### Statistics

**Synergy Dashboard:**
- Database Tables: 2 (`synergy_sessions`, `synergy_internal_docs`)
- Backend Routes: 60+ endpoints (4,953 lines)
- Tool Schemas: 15 AI tools
- Frontend Code: ~1,200 lines JavaScript

**Multi-Agent Coordination:**
- AI Tools: 3 core coordination tools
- Backend Implementation: 576 lines
- UI Command Processor: 428 lines
- Database Table: `cross_thread_requests`
- Agent Locations: 27 (Prime + 26 agents)

---

## Architecture

### System Overview

```
┌─────────────────────────────────────────────────────────────────────┐
│                         USER INTERFACE                               │
│  ┌────────────────────────────┐  ┌───────────────────────────────┐ │
│  │   Synergy Dashboard Tab     │  │   Multi-Agent Dashboard Tab   │ │
│  │   • Kanban Board            │  │   • 26 Agent Columns          │ │
│  │   • Project Cards           │  │   • Thread Management         │ │
│  │   • Activity Logs           │  │   • Cross-Thread Requests     │ │
│  └────────────┬───────────────┘  └──────────────┬────────────────┘ │
└───────────────┼────────────────────────────────────┼──────────────────┘
                │                                    │
                │ REST API                           │ REST API
                │                                    │
┌───────────────▼────────────────────────────────────▼──────────────────┐
│                      FLASK BACKEND                                     │
│  ┌────────────────────────┐  ┌────────────────────────────────────┐  │
│  │  synergy_routes.py      │  │  advanced_agent_coordination.py    │  │
│  │  (4,953 lines)          │  │  (576 lines)                       │  │
│  │  • CRUD operations      │  │  • assign_and_activate_agent      │  │
│  │  • Column management    │  │  • request_update_from_thread     │  │
│  │  • Thread linking       │  │  • respond_to_cross_thread        │  │
│  └────────────┬───────────┘  └────────────┬───────────────────────┘  │
└───────────────┼────────────────────────────┼──────────────────────────┘
                │                            │
                │ SQL                        │ SQL
                │                            │
┌───────────────▼────────────────────────────▼──────────────────────────┐
│                  SUPABASE POSTGRESQL DATABASE                          │
│  ┌──────────────────────────┐  ┌─────────────────────────────────┐   │
│  │  synergy_sessions schema  │  │  sessions schema                │   │
│  │  • synergy_sessions       │  │  • threads                      │   │
│  │  • synergy_internal_docs  │  │  • messages                     │   │
│  │                           │  │  • cross_thread_requests        │   │
│  │  Bidirectional Linking:   │  │                                 │   │
│  │  linked_thread_ids[] ←→   │  │  ←→ synergy_card_id            │   │
│  └──────────────────────────┘  └─────────────────────────────────┘   │
└────────────────────────────────────────────────────────────────────────┘
```

### Design Patterns

**1. Bidirectional Linking Pattern**
- Synergy cards store array of thread IDs: `linked_thread_ids[]`
- Threads store single Synergy ID: `synergy_card_id`
- Allows many-to-one relationship (many threads → one project)

**2. NATO Alphabet Mapping**
- User-friendly names: "Alpha", "Bravo", "Charlie"
- Maps to database locations: "agent-1", "agent-2", "agent-3"
- Flexible input: NATO name, location string, or number (1-26)

**3. Context Injection**
- Tools receive `_user_id`, `_source_thread_id` from backend
- No need for AI to know its own context
- Enables proper isolation and security

**4. UI Command Pattern**
- Backend tools return `ui_commands` array
- Frontend processor executes commands automatically
- Enables backend-driven UI automation

**5. Nested Context Managers (Database Safety)**
```python
with get_database_connection('synergy_sessions') as conn:
    with conn.cursor() as cursor:
        cursor.execute(...)
        data = cursor.fetchall()
    # Cursor auto-closed
    return response
# Connection auto-closed
```

### Data Flow

#### Synergy Card Creation
```
User → AI Agent → synergy_smart_project_tracker(action='create', ...)
           ↓
    tools/implementations/synergy.py
           ↓
    POST /api/synergy/create (synergy_routes.py)
           ↓
    INSERT INTO synergy_sessions.synergy_sessions
           ↓
    WebSocket broadcast (socket.emit 'synergy_update')
           ↓
    All clients refresh Kanban board
```

#### Multi-Agent Work Distribution
```
User: "Build e-commerce platform"
           ↓
Prime AI analyzes task
           ↓
assign_and_activate_agent_with_slugs() × 3
    • Agent Alpha: Frontend (React)
    • Agent Bravo: Backend (Node.js)
    • Agent Delta: Database (PostgreSQL)
           ↓
Creates 3 threads at agent locations
Inserts instruction messages
Returns UI commands
           ↓
Frontend executes commands:
    • Switch to Multi-Agent tab
    • Open Alpha, Bravo, Delta columns
    • Show thread info cards
    • Highlight with animation
           ↓
User sees 3 agents working simultaneously
```

#### Cross-Thread Communication
```
Agent Alpha (Frontend) needs API specs
           ↓
request_update_from_thread(
    target='Bravo',
    message='What endpoints are ready?',
    priority='high'
)
           ↓
INSERT INTO cross_thread_requests
INSERT INTO Agent Bravo's thread messages
           ↓
Agent Bravo processes request
           ↓
respond_to_cross_thread_request(
    request_id='req_abc',
    response='GET /products, POST /orders ready'
)
           ↓
UPDATE cross_thread_requests SET status='completed'
INSERT INTO Agent Alpha's thread messages
           ↓
Agent Alpha receives response
```

---

## Synergy Dashboard

### Purpose

Visual project management system integrated into AI Agents platform. Provides Kanban-style tracking for complex multi-step projects that span multiple AI conversations, tools, and platforms.

### When to Use Synergy

✅ **Use Synergy for:**
- Projects with 3+ distinct phases/milestones
- Work involving multiple tools (Google, Xero, Shopify, etc.)
- Projects spanning multiple AI conversations
- Team collaboration with task assignments
- Visual progress tracking needs

❌ **Don't use Synergy for:**
- Simple one-off tasks
- Quick calculations or data queries
- Single-tool operations
- Ephemeral conversations

### Kanban Board Columns

| Column | Purpose | Typical Contents |
|--------|---------|------------------|
| **Backlog** | Ideas & planned work | Research tasks, feature requests, bug reports |
| **In Progress** | Active work | Development tasks, content creation, integrations |
| **Review** | Needs validation | Testing items, awaiting approval, documentation review |
| **Done** | Completed work | Deployed features, resolved bugs, published content |

**Drag-and-drop enabled** - Move cards between columns by dragging

### Card Structure

Each Synergy card contains:

```
┌─────────────────────────────────────────────────┐
│ 📌 Project Title                         Priority │
├─────────────────────────────────────────────────┤
│ Description                                       │
│ Plain text description of project goals           │
├─────────────────────────────────────────────────┤
│ 📄 Documents (3)                                 │
│ • Design Mockup (Google Drive)                   │
│ • API Spec (Microsoft Word)                      │
│ • User Stories (PDF)                             │
├─────────────────────────────────────────────────┤
│ 🔗 Links (2)                                     │
│ • GitHub Repository                              │
│ • Production URL                                 │
├─────────────────────────────────────────────────┤
│ ✅ Checklist (5 items, 3 completed)             │
│ ☑ Setup development environment                  │
│ ☑ Create database schema                         │
│ ☑ Build authentication flow                      │
│ ☐ Write API documentation                        │
│ ☐ Deploy to production                           │
├─────────────────────────────────────────────────┤
│ 📝 Next Steps (2)                                │
│ 1. Complete API documentation by Friday          │
│ 2. Schedule deployment for Monday 9am            │
├─────────────────────────────────────────────────┤
│ 🧵 Linked Threads (3)                            │
│ • Alpha: Frontend Development (5 messages)       │
│ • Bravo: API Implementation (12 messages)        │
│ • Delta: Database Design (8 messages)            │
├─────────────────────────────────────────────────┤
│ 💬 Notes                                         │
│ User feedback: Need dark mode support            │
├─────────────────────────────────────────────────┤
│ 📊 Activity Log                                  │
│ ✏️ User updated description - 2 hours ago        │
│ ↗️ User moved to In Progress - 1 day ago         │
│ ➕ User created card - 3 days ago                │
├─────────────────────────────────────────────────┤
│ 🔑 Session ID: sess_abc123xyz789                 │
│    (click to copy)                               │
└─────────────────────────────────────────────────┘
```

### Database Schema

#### `synergy_sessions.synergy_sessions` Table

```sql
CREATE TABLE synergy_sessions.synergy_sessions (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL,
    title VARCHAR(500) NOT NULL,
    description TEXT,
    
    -- Organization
    priority VARCHAR(20), -- 'low', 'medium', 'high', 'urgent'
    milestone VARCHAR(100),
    status VARCHAR(50) DEFAULT 'backlog', -- Column name
    tags TEXT[],
    
    -- Rich Content
    documents JSONB, -- [{name, url, type, size}]
    links JSONB, -- [{title, url, description}]
    checklist JSONB, -- [{task, completed, subtasks}]
    next_steps JSONB, -- [{description, completed, due_date}]
    notes TEXT,
    activity_log JSONB, -- [{user, action, timestamp, details}]
    
    -- Linking
    linked_thread_ids INTEGER[], -- Array of sessions.threads.id
    
    -- Metadata
    due_date TIMESTAMP,
    assigned_to VARCHAR(255),
    estimated_hours NUMERIC,
    actual_hours NUMERIC,
    
    -- Timestamps
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_synergy_user_id ON synergy_sessions.synergy_sessions(user_id);
CREATE INDEX idx_synergy_status ON synergy_sessions.synergy_sessions(status);
CREATE INDEX idx_synergy_priority ON synergy_sessions.synergy_sessions(priority);
```

#### `synergy_sessions.synergy_internal_docs` Table

```sql
CREATE TABLE synergy_sessions.synergy_internal_docs (
    id SERIAL PRIMARY KEY,
    card_id INTEGER REFERENCES synergy_sessions(id) ON DELETE CASCADE,
    content TEXT NOT NULL,
    format VARCHAR(50) DEFAULT 'markdown', -- 'markdown', 'html'
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);
```

**Purpose:** Store rich-text documentation attached to Synergy cards (e.g., technical specifications, design docs, meeting notes).

---

## Multi-Agent Coordination

### Purpose

Enable AI Prime to distribute complex projects across 26 specialized AI agents, coordinate their work, and facilitate communication between agents without manual intervention.

### Agent Architecture

**27 Total Locations:**
- **1 Prime** - Main AI agent (default conversation location)
- **26 Agents** - Specialized workers (Alpha through Zulu)

**NATO Alphabet Mapping:**
```
Alpha → agent-1      Juliet → agent-10     Sierra → agent-19
Bravo → agent-2      Kilo → agent-11       Tango → agent-20
Charlie → agent-3    Lima → agent-12       Uniform → agent-21
Delta → agent-4      Mike → agent-13       Victor → agent-22
Echo → agent-5       November → agent-14   Whiskey → agent-23
Foxtrot → agent-6    Oscar → agent-15      X-ray → agent-24
Golf → agent-7       Papa → agent-16       Yankee → agent-25
Hotel → agent-8      Quebec → agent-17     Zulu → agent-26
India → agent-9      Romeo → agent-18
```

### Core Tools

#### 1. `assign_and_activate_agent_with_slugs`

**Purpose:** All-in-one tool for distributing work to agents with automatic UI updates.

**Capabilities:**
- Create or update thread at agent location
- Assign multiple resources (workflow, internal doc, synergy session)
- Insert instruction message into thread
- Optionally trigger agent AI processing immediately
- Return UI commands for frontend automation

**Example Usage:**
```python
assign_and_activate_agent_with_slugs(
    target_agent='Alpha',  # NATO name, 'agent-1', or '1' all work
    thread_title='E-Commerce Frontend Development',
    instructions='''
        Build React frontend for e-commerce platform:
        - Product catalog with search/filter
        - Shopping cart with checkout flow
        - User authentication and profiles
        - Responsive design (mobile-first)
        - Integration with backend API
    ''',
    slugs={
        'workflow_slug': 'react-development-workflow',
        'internal_doc_slug': 'react-component-library',
        'synergy_session_id': 'sess_ecommerce_project'
    },
    auto_trigger=True,  # Immediately start Agent Alpha
    open_ui=True  # Automatically open Alpha's column in UI
)
```

**Returns:**
```python
{
    'success': True,
    'thread_id': '1763287449123',
    'agent_location': 'agent-1',
    'agent_name': 'Alpha',
    'assigned_slugs': {
        'workflow_slug': 'react-development-workflow',
        'workflow_title': 'React Development Workflow',
        'internal_doc_slug': 'react-component-library',
        'internal_doc_title': 'React Component Library Guide',
        'synergy_session_id': 'sess_ecommerce_project'
    },
    'ui_commands': [
        {'command': 'switch_tab', 'tab_name': 'multi-agent'},
        {'command': 'open_agent_column', 'agent_number': 1, 'agent_name': 'Alpha', 'highlight': True},
        {'command': 'show_thread_info', 'thread_id': '1763287449123', 'badges': {...}},
        {'command': 'trigger_agent_request', 'thread_id': '1763287449123'}
    ]
}
```

#### 2. `request_update_from_thread`

**Purpose:** Cross-thread communication - request information/status from another agent.

**Example Usage:**
```python
request_update_from_thread(
    target_thread_id='Bravo',  # Or 'agent-2' or '2'
    request_message='What is the status of the API endpoints? Are /products and /orders ready for testing?',
    request_type='status_update',  # Or 'deliverable', 'question', 'coordination', 'resource_request'
    priority='high',  # 'low', 'medium', 'high', 'urgent'
    wait_for_response=True,  # Poll for response
    timeout=300  # 5 minutes
)
```

**Priority Levels:**
- **urgent** 🔴 - Red icon, critical blocking issue
- **high** 🟠 - Orange icon, important for progress
- **medium** 🟡 - Yellow icon, normal priority
- **low** 🔵 - Blue icon, nice-to-have

**Returns:**
```python
{
    'success': True,
    'request_id': 'req_abc123xyz',
    'status': 'pending',  # Or 'completed' if wait_for_response=True
    'target_agent': 'Bravo',
    'message_inserted': True,
    'response': 'Both endpoints ready. See test results in thread.'  # If wait_for_response=True
}
```

#### 3. `respond_to_cross_thread_request`

**Purpose:** Respond to incoming requests from other agents.

**Example Usage:**
```python
respond_to_cross_thread_request(
    request_id='req_abc123xyz',
    response_message='''
        API Status Update:
        
        ✅ GET /products - Complete (includes search, filter, pagination)
        ✅ POST /orders - Complete (validation, inventory check)
        ✅ Authentication middleware working
        
        Test coverage: 94%
        Ready for integration testing.
    '''
)
```

**Returns:**
```python
{
    'success': True,
    'request_id': 'req_abc123xyz',
    'status': 'completed',
    'response_delivered_to': 'agent-1',
    'source_agent': 'Alpha'
}
```

### Database Schema

#### `sessions.cross_thread_requests` Table

```sql
CREATE TABLE sessions.cross_thread_requests (
    id SERIAL PRIMARY KEY,
    request_id VARCHAR(100) UNIQUE NOT NULL,
    source_thread_id VARCHAR(100) NOT NULL,  -- Thread making request
    target_thread_id VARCHAR(100) NOT NULL,  -- Thread receiving request
    request_message TEXT NOT NULL,
    request_type VARCHAR(50) DEFAULT 'status_update',
    priority VARCHAR(20) DEFAULT 'medium',
    status VARCHAR(50) DEFAULT 'pending',  -- 'pending', 'completed'
    response_message TEXT,
    user_id INTEGER NOT NULL,
    created_at TIMESTAMP DEFAULT NOW(),
    responded_at TIMESTAMP
);

CREATE INDEX idx_cross_thread_target ON sessions.cross_thread_requests(target_thread_id, status);
CREATE INDEX idx_cross_thread_source ON sessions.cross_thread_requests(source_thread_id, created_at);
CREATE INDEX idx_cross_thread_status ON sessions.cross_thread_requests(status, created_at);
```

### Workflow Patterns

#### Pattern A: Parallel Project Distribution

**User Request:** "Build a full-stack e-commerce platform"

**Prime AI Strategy:**
1. Analyze requirements (frontend, backend, database)
2. Distribute across 3 agents
3. Link all to same Synergy session for unified tracking

**Implementation:**
```python
# Agent Alpha - Frontend
assign_and_activate_agent_with_slugs(
    target_agent='Alpha',
    thread_title='E-Commerce Frontend',
    instructions='Build React frontend with product catalog, cart, checkout...',
    slugs={'synergy_session_id': 'sess_ecommerce'},
    auto_trigger=True
)

# Agent Bravo - Backend
assign_and_activate_agent_with_slugs(
    target_agent='Bravo',
    thread_title='E-Commerce Backend API',
    instructions='Build Node.js/Express REST API with authentication...',
    slugs={'synergy_session_id': 'sess_ecommerce'},
    auto_trigger=True
)

# Agent Delta - Database
assign_and_activate_agent_with_slugs(
    target_agent='Delta',
    thread_title='E-Commerce Database Design',
    instructions='Design PostgreSQL schema for products, orders, users...',
    slugs={'synergy_session_id': 'sess_ecommerce'},
    auto_trigger=True
)
```

**Result:**
- 3 agents working simultaneously
- All linked to same Synergy card
- User can monitor progress on Kanban board
- Agents can request updates from each other

#### Pattern B: Sequential Dependency Chain

**User Request:** "Deploy authentication system to production"

**Prime AI Strategy:**
1. Agent Alpha: Write tests
2. Agent Bravo: Deploy to staging (after tests pass)
3. Agent Charlie: Deploy to production (after staging validated)

**Implementation:**
```python
# Step 1: Agent Alpha writes tests
assign_and_activate_agent_with_slugs(
    target_agent='Alpha',
    thread_title='Authentication Tests',
    instructions='Write unit and integration tests for auth system...',
    auto_trigger=True
)

# Step 2: Wait for Alpha to complete, then Agent Bravo
# (Prime monitors Alpha's thread, triggers Bravo when ready)
request_update_from_thread(
    target_thread_id='Alpha',
    request_message='Are all authentication tests passing?',
    priority='high',
    wait_for_response=True
)

# Once tests pass:
assign_and_activate_agent_with_slugs(
    target_agent='Bravo',
    thread_title='Deploy Auth to Staging',
    instructions='Deploy authentication system to staging environment...',
    auto_trigger=True
)

# Step 3: Agent Charlie deploys to production after staging validation
# (Similar pattern)
```

#### Pattern C: Cross-Agent Collaboration

**Scenario:** Frontend agent needs API specs from backend agent

**Agent Alpha (Frontend):**
```python
request_update_from_thread(
    target_thread_id='Bravo',
    request_message='Can you provide API endpoint documentation? Need URL paths, request/response schemas, and authentication requirements.',
    request_type='deliverable',
    priority='high',
    wait_for_response=True,
    timeout=600
)
```

**System Action:**
1. Creates request record in database
2. Inserts message into Agent Bravo's thread with 🟠 high priority icon
3. Agent Bravo processes request
4. Agent Bravo calls `respond_to_cross_thread_request()`
5. Response delivered back to Agent Alpha's thread
6. Agent Alpha continues work with API documentation

---

## Thread System Integration

### Bidirectional Linking

**Thread → Synergy:**
- Thread stores: `synergy_card_id INTEGER`
- Single card per thread
- Displayed as 🟢 green pill in thread UI

**Synergy → Threads:**
- Card stores: `linked_thread_ids INTEGER[]`
- Multiple threads per card
- Displayed in "Linked Threads" section with thread info cards

### Thread Metadata

Each thread can have:
```sql
CREATE TABLE sessions.threads (
    id SERIAL PRIMARY KEY,
    slug VARCHAR(100) UNIQUE NOT NULL,
    title VARCHAR(500),
    user_id INTEGER NOT NULL,
    agent VARCHAR(50),  -- 'prime', 'agent-1', etc.
    
    -- Resource Links
    synergy_card_id INTEGER,  -- Link to Synergy card
    workflow_slug VARCHAR(100),  -- Visual automation workflow
    internal_doc_slug VARCHAR(100),  -- Internal documentation
    
    -- ... other fields
);
```

### UI Indicators

**Thread Pills (Top Right of Thread):**
- 🟢 **Synergy** - Card title (click to open Synergy tab)
- 🟠 **Workflow** - Workflow name (click to open workflow)
- 🔵 **Internal Doc** - Doc title (click to view doc)

**Thread Info Card (Multi-Agent Dashboard):**
```
┌─────────────────────────────────────┐
│ 🧵 Thread: E-Commerce Frontend      │
├─────────────────────────────────────┤
│ Agent: Alpha                         │
│ Messages: 15                         │
│                                      │
│ Resources:                           │
│ 🟠 Workflow: React Dev Workflow      │
│ 🔵 Doc: Component Library Guide      │
│ 🟢 Synergy: E-Commerce Project       │
└─────────────────────────────────────┘
```

---

## Implementation Details

### File Structure

```
AI_infrastructure/
├── routes/
│   ├── synergy_routes.py                    # 4,953 lines - 60+ endpoints
│   └── thread_routes.py                     # Thread CRUD + assignments
├── tools/
│   ├── implementations/
│   │   ├── advanced_agent_coordination.py   # 576 lines - 3 core tools
│   │   └── synergy.py                       # Synergy tool wrappers
│   └── schemas/
│       ├── advanced_agent_coordination_tools.json  # 265 lines
│       └── synergy_tools.json               # 15 tool definitions
└── shared/
    └── database_utils.py                    # Connection pooling

UI/
├── modules_external/
│   └── ui-command-processor.js              # 428 lines - UI automation
└── business-ai-platform-v2.html             # Main UI (~45,000 lines)
    ├── Synergy Dashboard (lines ~21000-24000)
    └── Multi-Agent Dashboard (lines ~14000-17000)

data/
└── sessions.db                              # SQLite (development only)

DATABASE (Supabase PostgreSQL - Production):
├── synergy_sessions schema
│   ├── synergy_sessions table
│   └── synergy_internal_docs table
└── sessions schema
    ├── threads table
    ├── messages table
    ├── cross_thread_requests table
    └── thread_assignments table
```

### Key Components

#### Synergy Routes (`synergy_routes.py`)

**Line Count:** 4,953 lines
**Endpoints:** 60+
**Pattern:** Nested context managers (leak-proof)

**Major Endpoint Groups:**

1. **CRUD Operations** (Lines ~100-500)
   - `POST /api/synergy/create` - Create new card
   - `GET /api/synergy/list` - List all cards
   - `GET /api/synergy/<id>` - Get single card
   - `PATCH /api/synergy/<id>` - Update card
   - `DELETE /api/synergy/<id>` - Delete card

2. **Column Management** (Lines ~500-800)
   - `PATCH /api/synergy/<id>/column` - Move to different column
   - `POST /api/synergy/bulk-move` - Move multiple cards

3. **Thread Linking** (Lines ~800-1200)
   - `POST /api/synergy/<id>/link-thread` - Link thread to card
   - `DELETE /api/synergy/<id>/unlink-thread` - Unlink thread

4. **Rich Content** (Lines ~1200-2000)
   - `POST /api/synergy/<id>/documents` - Add document
   - `POST /api/synergy/<id>/links` - Add link
   - `POST /api/synergy/<id>/checklist` - Update checklist
   - `POST /api/synergy/<id>/next-steps` - Update next steps
   - `PATCH /api/synergy/<id>/notes` - Update notes

5. **Internal Docs** (Lines ~2000-2400)
   - `POST /api/synergy/<id>/internal-doc` - Create/update doc
   - `GET /api/synergy/<id>/internal-doc` - Get doc content
   - `DELETE /api/synergy/<id>/internal-doc` - Delete doc

6. **Testing Endpoints** (Lines ~2619-2878)
   - `GET /api/synergy/test/smoke` - Quick health check
   - `GET /api/synergy/test/endpoints` - List all endpoints
   - `GET /api/synergy/test/database` - Database tests
   - `GET /api/synergy/test/compile` - Syntax validation
   - `GET /api/synergy/test/health` - System metrics

**Critical Pattern (Used Throughout):**
```python
@synergy_bp.route('/endpoint', methods=['POST'])
def endpoint_handler():
    """
    Docstring explaining endpoint purpose
    """
    # ✅ NESTED CONTEXT MANAGERS (leak-proof)
    with get_database_connection('synergy_sessions') as conn:
        with conn.cursor() as cursor:
            # Database work
            sql, params = convert_sql_placeholders(
                "SELECT * FROM synergy_sessions WHERE id = ?",
                (session_id,)
            )
            cursor.execute(sql, params)
            data = cursor.fetchall()
        # Cursor auto-closed here
        
        # Process data outside cursor context
        result = process_data(data)
        return jsonify(result)
    # Connection auto-closed here
```

#### Agent Coordination (`advanced_agent_coordination.py`)

**Line Count:** 576 lines
**Tools:** 3
**Helper Functions:** 4

**Function Breakdown:**

**Lines 1-40:** Imports, NATO alphabet mapping, error class
```python
NATO_ALPHABET = {
    'Alpha': 1, 'Bravo': 2, 'Charlie': 3, ...
}
REVERSE_NATO = {v: k for k, v in NATO_ALPHABET.items()}
```

**Lines 41-90:** Database connection and agent identifier parsing
```python
def parse_agent_identifier(agent_id: str) -> str:
    """
    Converts 'Alpha', 'agent-1', or '1' → 'agent-1'
    """
```

**Lines 91-350:** `assign_and_activate_agent_with_slugs()`
- Parse agent identifier
- Get/create thread at location
- Update thread metadata (slugs)
- Insert instruction message
- Build UI commands
- Return comprehensive result

**Lines 351-480:** `request_update_from_thread()`
- Parse agent identifiers
- Create request record in database
- Insert formatted message into target thread with priority icon
- Optionally poll for response
- Return request details

**Lines 481-576:** `respond_to_cross_thread_request()`
- Fetch request record
- Update status to 'completed'
- Store response message
- Insert response into source thread
- Return confirmation

#### UI Command Processor (`ui-command-processor.js`)

**Line Count:** 428 lines
**Commands:** 6

**Structure:**
```javascript
const UICommandProcessor = {
    processCommands: function(commands) {...},
    executeCommand: function(cmd, index) {...},
    switchTab: function(cmd) {...},             // Lines 93-115
    openAgentColumn: function(cmd) {...},       // Lines 117-157
    showThreadInfo: function(cmd) {...},        // Lines 159-229
    triggerAgentRequest: function(cmd) {...},   // Lines 231-280
    showCrossThreadRequest: function(cmd) {...}, // Lines 282-350
    notifyThreadResponse: function(cmd) {...}   // Lines 352-428
};
```

**Integration (in business-ai-platform-v2.html):**
```javascript
// Listen for tool responses
document.addEventListener('tool-response-received', (event) => {
    const result = event.detail;
    if (result.ui_commands && Array.isArray(result.ui_commands)) {
        UICommandProcessor.processCommands(result.ui_commands);
    }
});
```

### Data Normalization

**Problem:** AI agents may send different field names (e.g., `title` vs `name`, `task` vs `item`)

**Solution:** Normalization functions in `synergy_routes.py`

```python
def normalize_next_steps(steps):
    """Convert string arrays to object arrays"""
    if not steps:
        return []
    
    normalized = []
    for step in steps:
        if isinstance(step, str):
            normalized.append({
                'description': step,
                'completed': False,
                'due_date': None,
                'completed_at': None
            })
        elif isinstance(step, dict):
            normalized.append({
                'description': step.get('description', ''),
                'completed': step.get('completed', False),
                'due_date': step.get('due_date'),
                'completed_at': step.get('completed_at')
            })
    return normalized

def normalize_documents(docs):
    """Ensure 'title' field exists (handles 'name' vs 'title')"""
    if not docs:
        return []
    
    normalized = []
    for doc in docs:
        if isinstance(doc, str):
            # Simple URL string
            normalized.append({
                'title': doc,
                'url': doc,
                'type': 'unknown',
                'size': None
            })
        elif isinstance(doc, dict):
            # Handle both 'title' and 'name' fields
            normalized.append({
                'title': doc.get('title') or doc.get('name', 'Untitled'),
                'url': doc.get('url', ''),
                'type': doc.get('type', 'unknown'),
                'size': doc.get('size')
            })
    return normalized
```

---

## API Reference

### Synergy Dashboard Endpoints

#### Create Session
```http
POST /api/synergy/create
Content-Type: application/json

{
    "title": "Project Alpha",
    "description": "Build customer portal",
    "priority": "high",
    "status": "backlog",
    "tags": ["frontend", "react"],
    "user_id": 1
}
```

**Response:**
```json
{
    "success": true,
    "session": {
        "id": 123,
        "title": "Project Alpha",
        "status": "backlog",
        "created_at": "2026-01-18T10:30:00Z"
    }
}
```

#### List Sessions
```http
GET /api/synergy/list?user_id=1
```

**Response:**
```json
{
    "success": true,
    "sessions": [
        {
            "id": 123,
            "title": "Project Alpha",
            "status": "in-progress",
            "priority": "high",
            "linked_thread_ids": [45, 67, 89],
            "created_at": "2026-01-18T10:30:00Z"
        }
    ],
    "count": 1
}
```

#### Update Session
```http
PATCH /api/synergy/<session_id>
Content-Type: application/json

{
    "title": "Project Alpha (Updated)",
    "description": "Build customer portal with admin dashboard",
    "priority": "urgent"
}
```

#### Move to Column
```http
PATCH /api/synergy/<session_id>/column
Content-Type: application/json

{
    "status": "in-progress",
    "user_id": 1
}
```

#### Link Thread
```http
POST /api/synergy/<session_id>/link-thread
Content-Type: application/json

{
    "thread_id": 45,
    "user_id": 1
}
```

#### Add Document
```http
POST /api/synergy/<session_id>/documents
Content-Type: application/json

{
    "documents": [
        {
            "title": "Design Mockup",
            "url": "https://drive.google.com/file/d/abc123",
            "type": "google_drive"
        }
    ],
    "user_id": 1
}
```

#### Update Checklist
```http
POST /api/synergy/<session_id>/checklist
Content-Type: application/json

{
    "checklist": [
        {
            "task": "Setup development environment",
            "completed": true
        },
        {
            "task": "Create database schema",
            "completed": false,
            "subtasks": [
                {"task": "Design ERD", "completed": true},
                {"task": "Write migration", "completed": false}
            ]
        }
    ],
    "user_id": 1
}
```

### Multi-Agent Coordination Tools

#### Assign and Activate Agent

**Tool Call (from AI):**
```python
assign_and_activate_agent_with_slugs(
    target_agent='Alpha',
    thread_title='Frontend Development',
    instructions='Build React frontend...',
    slugs={
        'workflow_slug': 'react-workflow',
        'synergy_session_id': 'sess_123'
    },
    auto_trigger=True,
    open_ui=True
)
```

**Backend Implementation:** `tools/implementations/advanced_agent_coordination.py` (Lines 91-350)

**Database Operations:**
1. Parse `target_agent` → `agent-1`
2. Query `sessions.threads` for existing thread at location
3. If exists: UPDATE thread metadata
4. If not: INSERT new thread
5. INSERT instruction message into `sessions.messages`
6. Build UI commands array
7. RETURN result with `ui_commands`

**Return Value:**
```python
{
    'success': True,
    'thread_id': '1763287449123',
    'agent_location': 'agent-1',
    'agent_name': 'Alpha',
    'action': 'updated',  # Or 'created'
    'assigned_slugs': {
        'workflow_slug': 'react-workflow',
        'workflow_title': 'React Development Workflow',
        'synergy_session_id': 'sess_123'
    },
    'ui_commands': [
        {'command': 'switch_tab', 'tab_name': 'multi-agent'},
        {'command': 'open_agent_column', 'agent_number': 1, 'agent_name': 'Alpha', 'highlight': True},
        {'command': 'show_thread_info', 'thread_id': '1763287449123', 'badges': {...}},
        {'command': 'trigger_agent_request', 'thread_id': '1763287449123'}
    ]
}
```

#### Request Update from Thread

**Tool Call:**
```python
request_update_from_thread(
    target_thread_id='Bravo',
    request_message='What is the API status?',
    request_type='status_update',
    priority='high',
    wait_for_response=False
)
```

**Backend Implementation:** `advanced_agent_coordination.py` (Lines 351-480)

**Database Operations:**
1. Parse `target_thread_id` → `agent-2`
2. Generate `request_id` (UUID)
3. INSERT INTO `sessions.cross_thread_requests`
4. Format message with priority icon
5. INSERT message into target thread
6. If `wait_for_response=True`: Poll for completion
7. RETURN request details

**Priority Icons:**
- 🔴 urgent
- 🟠 high
- 🟡 medium
- 🔵 low

**Return Value:**
```python
{
    'success': True,
    'request_id': 'req_abc123xyz',
    'status': 'pending',
    'target_agent': 'Bravo',
    'message_inserted': True,
    'formatted_message': '🟠 HIGH PRIORITY REQUEST from Alpha:\n\nWhat is the API status?'
}
```

#### Respond to Cross-Thread Request

**Tool Call:**
```python
respond_to_cross_thread_request(
    request_id='req_abc123xyz',
    response_message='API is 90% complete. Endpoints ready for testing.'
)
```

**Backend Implementation:** `advanced_agent_coordination.py` (Lines 481-576)

**Database Operations:**
1. SELECT request from `sessions.cross_thread_requests` WHERE `request_id`
2. UPDATE `status='completed'`, `response_message`, `responded_at`
3. Format response message with checkmark
4. INSERT response into source thread
5. RETURN confirmation

**Return Value:**
```python
{
    'success': True,
    'request_id': 'req_abc123xyz',
    'status': 'completed',
    'response_delivered_to': 'agent-1',
    'source_agent': 'Alpha',
    'formatted_response': '✅ RESPONSE from Bravo:\n\nAPI is 90% complete. Endpoints ready for testing.'
}
```

---

## Configuration

### Environment Variables

```bash
# Database (Supabase)
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_KEY=your-anon-key
SUPABASE_DB_PASSWORD=your-db-password
POOL_ENABLED=True  # Enable connection pooling

# WebSocket (optional - for real-time updates)
SOCKETIO_ENABLED=True
SOCKETIO_NAMESPACE=/

# Agent Coordination
MAX_AGENTS=26  # Number of agent columns (Alpha-Zulu)
```

### Database Configuration

**Connection Pooling (database_utils.py):**
```python
synergy_pool = psycopg2.pool.ThreadedConnectionPool(
    minconn=2,
    maxconn=10,
    host=SUPABASE_HOST,
    database=SUPABASE_DB_NAME,
    user='postgres',
    password=SUPABASE_DB_PASSWORD,
    options="-c search_path=synergy_sessions,public"
)
```

**Search Path Priority:**
1. `synergy_sessions` schema (Synergy tables)
2. `sessions` schema (Thread tables)
3. `public` schema (Workflows, users)

### Frontend Configuration

**business-ai-platform-v2.html:**

**Synergy Dashboard Configuration (Lines ~21000):**
```javascript
const synergyBoard = {
    columns: ['backlog', 'in-progress', 'review', 'done'],
    columnTitles: {
        'backlog': 'Backlog',
        'in-progress': 'In Progress',
        'review': 'Review',
        'done': 'Done'
    },
    apiBase: '/api/synergy',
    dragEnabled: true,
    autoSave: true,
    saveDelay: 500  // ms
};
```

**Multi-Agent Configuration (Lines ~14000):**
```javascript
const multiAgent = {
    totalAgents: 26,  // Alpha to Zulu
    agentNames: ['Alpha', 'Bravo', 'Charlie', ...],
    locations: ['agent-1', 'agent-2', 'agent-3', ...],
    apiBase: '/api/threads',
    autoLoad: true,  // Load threads on tab open
    pollInterval: 30000  // 30 seconds
};
```

---

## Critical Fixes

### 1. ✅ RESOLVED: Synergy UI Field Display Issues (November 9, 2025)

**Problem:** 11 critical UI display issues in Synergy cards

**Root Causes:**
1. Documents showed only icons, no clickable links
2. Field name inconsistencies (`title` vs `name`, `task` vs `item`)
3. Empty sections not visible
4. Activity log had poor formatting
5. Session ID not easily copyable
6. Linked threads showed spinner forever (missing backend endpoint)

**Solutions:**

**A. Documents Display** (Lines 22910-22927 in business-ai-platform-v2.html)
```javascript
// BEFORE: Just icon + name
<div>${doc.name}</div>

// AFTER: Clickable link with type badge
<a href="${doc.url}" target="_blank">${doc.name}</a>
<span class="doc-type-badge">${docTypeLabel}</span>
```

**B. Field Name Handling** (Lines 22975-23012)
```javascript
// Flexible field name handling
const taskText = item.task || item.item || 'Unnamed task';
const linkTitle = link.title || link.name || 'Untitled';
const stepText = step.description || step.text || step.step || step.title;
```

**C. Linked Threads Backend** (thread_routes.py, Line 593)
```python
@thread_bp.route('/details', methods=['POST'])
def get_thread_details():
    """Get details for multiple threads by their IDs"""
    thread_ids = request.json.get('thread_ids', [])
    
    threads = []
    for thread_id in thread_ids:
        thread = query_thread_by_id(thread_id)
        if thread:
            threads.append({
                'id': thread['id'],
                'title': thread['title'],
                'agent': thread['agent'],
                'created_at': thread['created_at'],
                'updated_at': thread['updated_at'],
                'message_count': get_message_count(thread_id)
            })
    
    return jsonify({'success': True, 'threads': threads})
```

**D. Activity Log Icons** (Lines 23115-23147)
```javascript
// Icon mapping
if (activityType.includes('create')) icon = 'fa-plus-circle';
else if (activityType.includes('update')) icon = 'fa-edit';
else if (activityType.includes('delete')) icon = 'fa-trash';
else if (activityType.includes('move')) icon = 'fa-arrow-right';
else if (activityType.includes('assign')) icon = 'fa-user-plus';
```

**Files Modified:**
- `UI/business-ai-platform-v2.html` (Lines 22910-24284)
- `AI_infrastructure/routes/thread_routes.py` (Line 593+)

**Impact:**
- All Synergy card data now displays correctly
- Improved UX with icons, badges, click-to-copy
- Fixed linked threads loading (no more infinite spinner)
- Professional activity logs with timestamps

---

### 2. ✅ RESOLVED: Connection Leak Audit (December 6, 2025)

**Problem:** Potential connection leaks in `synergy_routes.py`

**Solution:** Converted all 60+ functions to nested context managers

**Pattern Applied:**
```python
# ❌ OLD PATTERN (potential leak)
conn = get_database_connection('synergy_sessions')
cursor = conn.cursor()
cursor.execute(...)
data = cursor.fetchall()
cursor.close()  # Manual cleanup
conn.close()  # Manual cleanup

# ✅ NEW PATTERN (leak-proof)
with get_database_connection('synergy_sessions') as conn:
    with conn.cursor() as cursor:
        cursor.execute(...)
        data = cursor.fetchall()
    # Cursor auto-closed
    # Process data here
# Connection auto-closed
```

**Files Modified:**
- `AI_infrastructure/routes/synergy_routes.py` (All 60+ functions)

**Verification:**
```powershell
python AI_infrastructure/tools/audit_connection_leaks.py
# Output: 0 potential leaks found
```

**Impact:**
- Zero connection leaks
- Automatic resource cleanup
- More robust error handling
- Production-ready reliability

---

### 3. ✅ RESOLVED: Multi-Agent DOM Race Condition (Date Unknown)

**Problem:** UI command processor tried to access DOM elements before they were rendered

**Root Cause:** Async tool execution returned UI commands before frontend rendered agent columns

**Solution:** Added existence checks and graceful degradation

**Code Changes (ui-command-processor.js):**
```javascript
openAgentColumn: function(cmd) {
    const agentColumn = document.querySelector(`[data-agent="${agentNum}"]`);
    
    if (!agentColumn) {
        console.warn(`Agent column ${agentNum} not found - may not be rendered yet`);
        // Retry after delay
        setTimeout(() => this.openAgentColumn(cmd), 500);
        return;
    }
    
    // Proceed with UI updates
}
```

**Impact:**
- No more "cannot read property of null" errors
- Graceful handling of async rendering
- Better UX with automatic retries

---

### 4. ✅ RESOLVED: Thread Slug Assignment Persistence (November 17, 2025)

**Problem:** Workflow slugs (🟠 orange pills) and Synergy slugs (🟢 green pills) not persisting after thread location changes

**Root Cause:** Thread move operations didn't include slug fields in UPDATE statement

**Solution:** Modified thread assignment endpoint to preserve metadata

**Code Changes (thread_routes.py):**
```python
@thread_bp.route('/assign', methods=['POST'])
def assign_thread():
    # ... validation ...
    
    # ✅ FIX: Include ALL metadata fields in UPDATE
    sql = """
        UPDATE sessions.threads
        SET 
            agent = %s,
            updated_at = NOW(),
            workflow_slug = COALESCE(%s, workflow_slug),  -- Preserve if null
            workflow_title = COALESCE(%s, workflow_title),
            internal_doc_slug = COALESCE(%s, internal_doc_slug),
            internal_doc_title = COALESCE(%s, internal_doc_title),
            synergy_card_id = COALESCE(%s, synergy_card_id)
        WHERE id = %s AND user_id = %s
    """
```

**Files Modified:**
- `AI_infrastructure/routes/thread_routes.py` (Lines ~450-520)

**Impact:**
- Pills persist across agent column moves
- No data loss when dragging threads
- Consistent UI state

---

### 5. ⚠️ CRITICAL: convert_sql_placeholders() Does NOT Execute Queries

**Problem:** Common mistake - calling `convert_sql_placeholders()` without `cursor.execute()`

**Explanation:**
```python
# ❌ WRONG - query never executed!
sql, params = convert_sql_placeholders('SELECT * FROM table WHERE id = ?', (id,))
for row in cursor.fetchall():  # Returns empty!
    print(row)

# ✅ CORRECT - query executed
sql, params = convert_sql_placeholders('SELECT * FROM table WHERE id = ?', (id,))
cursor.execute(sql, params)  # Actually run the query
for row in cursor.fetchall():  # Now returns data
    print(row)
```

**Why This Matters:**
- `convert_sql_placeholders()` only converts `?` → `%s` (SQLite → PostgreSQL)
- Does NOT execute the query
- Must call `cursor.execute(sql, params)` separately

**Documentation Added:**
- Header comment in `synergy_routes.py` (Lines 1-67)
- Inline comments throughout codebase
- Warning in `.github/copilot-instructions.md`

---

## Testing & Debugging

### Manual Testing Checklist

#### Synergy Dashboard Tests

```bash
# 1. Start Flask server
cd AI_infrastructure
python flask_app.py

# 2. Open browser
# Navigate to: http://localhost:5000
# Click "Synergy" tab

# 3. Test card creation
# - Click "Add Card" button
# - Fill in title, description, priority
# - Click "Create"
# - Verify card appears in Backlog column

# 4. Test drag-and-drop
# - Drag card from Backlog to In Progress
# - Verify card moves
# - Refresh page - verify persistence

# 5. Test documents
# - Click card to open popout
# - Click "Add Document"
# - Enter title and URL
# - Verify clickable link appears

# 6. Test thread linking
# - Open Prime AI
# - Send message with Synergy tool call
# - Verify thread linked to card
# - Check "Linked Threads" section shows thread info

# 7. Test activity log
# - Make several changes to card
# - Open popout
# - Scroll to Activity Log
# - Verify icons and timestamps correct
```

#### Multi-Agent Coordination Tests

```bash
# 1. Test agent assignment
# Open Prime AI, send:
"Distribute this project across 3 agents: Alpha (frontend), Bravo (backend), Delta (database)"

# Verify:
# - Switches to Multi-Agent tab automatically
# - Opens Alpha, Bravo, Delta columns with highlight animation
# - Shows thread info cards with resource badges
# - Agents start processing (if auto_trigger=True)

# 2. Test cross-thread requests
# In Agent Alpha's thread, send:
"Request API documentation from Agent Bravo"

# Verify:
# - Request appears in Bravo's thread with 🟡 medium priority icon
# - Request ID generated
# - Database record created in cross_thread_requests

# In Agent Bravo's thread, send:
"Respond to Alpha's request: API docs are ready at /docs/api"

# Verify:
# - Response appears in Alpha's thread with ✅ checkmark
# - Request status updated to 'completed' in database
# - Response_message stored

# 3. Test Synergy integration
# Create Synergy card "Project X"
# Assign to 3 agents with same synergy_session_id

# Verify:
# - All 3 threads show 🟢 Synergy pill
# - Card shows 3 linked threads
# - Clicking pill opens Synergy tab with card highlighted
```

### Automated Testing

**Backend Tests:**
```bash
# Run Synergy endpoint tests
python AI_infrastructure/test_synergy_endpoints.py

# Expected output:
# ✅ Smoke Test - 45ms
# ✅ Endpoints List - 12ms
# ✅ Database Test - 156ms
# ✅ Compile Test - 432ms
# ✅ Health Check - 23ms
# Total: 5/5 tests passed
```

**Agent Coordination Tests:**
```bash
# Run coordination tool tests
cd tools
python test_agent_coordination.py

# Expected output:
# ✅ Tool Loading (3/3 tools found)
# ✅ Registry Integration (754 total tools)
# ✅ Anthropic Format Validation
# ✅ Database Migration Verified
# Total: 4/4 tests passed
```

### Debugging Common Issues

#### Issue: Synergy Cards Not Loading

**Symptoms:**
- Empty Kanban board
- "Loading..." spinner never stops
- Console error: "Failed to fetch"

**Diagnosis:**
```bash
# Check Flask server is running
curl http://localhost:5000/api/synergy/list?user_id=1

# Check database connection
python -c "from AI_infrastructure.shared.database_utils import execute_query; print(execute_query('SELECT COUNT(*) FROM synergy_sessions.synergy_sessions', fetch_mode='value'))"
```

**Fix:**
1. Verify Flask server running on port 5000
2. Check `.env` has correct SUPABASE_URL and credentials
3. Run database migrations if tables missing
4. Check browser console for CORS errors

---

#### Issue: Agent Not Receiving Work Assignment

**Symptoms:**
- `assign_and_activate_agent_with_slugs()` returns success
- But agent column shows no thread
- UI doesn't switch to Multi-Agent tab

**Diagnosis:**
```python
# Check if thread was created
from AI_infrastructure.shared.database_utils import execute_query
result = execute_query(
    "SELECT * FROM sessions.threads WHERE agent = %s ORDER BY updated_at DESC LIMIT 1",
    ('agent-1',),
    fetch_mode='one'
)
print(result)

# Check UI command processor is loaded
# In browser console:
console.log(typeof UICommandProcessor);  // Should be 'object'
```

**Fix:**
1. Verify `ui-command-processor.js` included in HTML
2. Check `ui_commands` array in tool response
3. Check event listener is registered for 'tool-response-received'
4. Verify agent columns are rendered in DOM

---

#### Issue: Cross-Thread Request Not Appearing

**Symptoms:**
- `request_update_from_thread()` returns success
- But target agent's thread doesn't show request message
- No priority icon visible

**Diagnosis:**
```python
# Check database record
from AI_infrastructure.shared.database_utils import execute_query
request = execute_query(
    "SELECT * FROM sessions.cross_thread_requests WHERE request_id = %s",
    ('req_abc123',),
    fetch_mode='one'
)
print(request)

# Check message was inserted
messages = execute_query(
    "SELECT * FROM sessions.messages WHERE thread_id = %s ORDER BY created_at DESC LIMIT 5",
    (target_thread_id,),
    fetch_mode='all'
)
print(messages)
```

**Fix:**
1. Verify `target_thread_id` is correct (thread must exist)
2. Check message formatting (should include priority icon)
3. Refresh agent's thread in UI
4. Verify user_id matches between request and thread

---

### Backend Logs

**Normal Operation:**
```
[2026-01-18 10:30:00] INFO: [SYNERGY] Creating new session: Project Alpha
[2026-01-18 10:30:00] INFO: [SYNERGY] Session created with ID: 123
[2026-01-18 10:30:00] INFO: [SYNERGY] Broadcasting update to 3 clients
[2026-01-18 10:30:01] INFO: [AGENT_COORD] Assigning work to agent-1 (Alpha)
[2026-01-18 10:30:01] INFO: [AGENT_COORD] Thread created: 1763287449123
[2026-01-18 10:30:01] INFO: [AGENT_COORD] Instruction message inserted
[2026-01-18 10:30:01] INFO: [AGENT_COORD] UI commands: 4 total
```

**Error Logs:**
```
[2026-01-18 10:35:00] ERROR: [SYNERGY] Database connection failed: connection refused
[2026-01-18 10:35:00] ERROR: [AGENT_COORD] Invalid agent identifier: 'Omega'
[2026-01-18 10:35:01] ERROR: [CROSS_THREAD] Request not found: req_xyz789
[2026-01-18 10:35:01] ERROR: [SYNERGY] Field 'title' is required but missing
```

**Viewing Logs:**
```powershell
# Real-time log monitoring
Get-Content AI_infrastructure/flask_app.log -Tail 50 -Wait

# Filter for errors only
Get-Content AI_infrastructure/flask_app.log | Select-String -Pattern "ERROR"

# Search for specific component
Get-Content AI_infrastructure/flask_app.log | Select-String -Pattern "\[SYNERGY\]"
```

---

## Known Issues

### 1. ⚠️ KNOWN: WebSocket Broadcast Performance

**Status:** Optimization Needed
**Severity:** Medium
**Impact:** With 10+ simultaneous users, Synergy card updates can lag by 1-2 seconds

**Details:**
- Current implementation broadcasts ALL card updates to ALL users
- No filtering by user_id or card ownership
- Can cause unnecessary network traffic and UI re-renders

**Workaround:**
- Use polling fallback (already implemented)
- Disable WebSocket via `SOCKETIO_ENABLED=False` in `.env`

**Planned Fix:**
- Implement user-specific WebSocket rooms
- Only broadcast updates to users who own the card
- Add rate limiting for high-frequency updates

---

### 2. ⚠️ KNOWN: Agent Limit Hard-Coded to 26

**Status:** By Design
**Severity:** Low
**Impact:** Cannot exceed 26 agents (Alpha-Zulu)

**Details:**
- NATO alphabet has only 26 letters
- Database schema uses `agent-1` through `agent-26`
- UI renders 26 columns max

**Workaround:**
- None - this is intentional design decision
- For more parallelism, use multiple Synergy cards with same agents

**Future Enhancement:**
- Could extend to `agent-27`, `agent-28`, etc. with numeric names
- Would require UI redesign (scrollable agent grid)

---

### 3. 📋 KNOWN: No Automatic Thread Threading (Email-Style)

**Status:** Feature Request
**Severity:** Low
**Impact:** Cross-thread requests don't automatically create parent-child relationships

**Details:**
- Current system tracks requests in separate table
- No visual "reply chain" like email threads
- Can't see conversation history between agents at a glance

**Workaround:**
- Query `cross_thread_requests` table to see request/response history
- Check activity logs in each agent's thread

**Planned Feature:**
- Add "Thread View" to Multi-Agent dashboard
- Show conversation tree between agents
- Clickable links to navigate between related threads

---

### 4. ⚠️ KNOWN: Synergy Card Duplication Risk

**Status:** Edge Case
**Severity:** Low
**Impact:** Rapidly clicking "Create Card" can create duplicates

**Details:**
- No duplicate prevention at API level
- Frontend doesn't disable button during creation
- Can create multiple cards with same title

**Workaround:**
- Don't click "Create" multiple times
- Delete duplicate cards manually

**Planned Fix:**
- Add unique constraint on `(user_id, title)` in database
- Disable create button during API call
- Add "Creating..." loading indicator

---

## Appendix

### Glossary

**Agent** - One of 26 AI workers (Alpha-Zulu) that can execute tasks in parallel

**Bidirectional Linking** - Two-way relationship between threads and Synergy cards (`synergy_card_id` ↔ `linked_thread_ids[]`)

**Cross-Thread Request** - Message sent from one agent to another requesting information or status update

**Kanban** - Visual project management system with columns representing workflow stages

**Location** - Where a thread is displayed (`prime`, `agent-1` through `agent-26`)

**NATO Alphabet** - Alpha, Bravo, Charlie... Zulu - used for agent names

**Nested Context Managers** - Python pattern for automatic resource cleanup (`with ... as ...:`)

**Priority Icon** - Visual indicator for request urgency (🔴🟠🟡🔵)

**Session** - Synergy card representing a project (not to be confused with thread)

**Slug** - URL-safe unique identifier for threads, workflows, internal docs

**Synergy Card** - Individual project card on Kanban board

**Thread** - Persistent AI conversation with message history

**UI Commands** - Array of instructions returned by tools to automate frontend updates

**Workflow** - Visual automation canvas with nodes and connections

---

### Related Documentation

**Core System:**
- [ARCHITECTURE.md](./ARCHITECTURE.md) - Overall system architecture
- [DATABASE.md](./DATABASE.md) - Complete database schema reference
- [THREAD_SYSTEM.md](./THREAD_SYSTEM.md) - Thread management deep dive
- [MODULES.md](./MODULES.md) - Module plugin system

**Features:**
- [COMMUNICATION_HUB.md](./COMMUNICATION_HUB.md) - Email integration (thread linking)
- [AI_AGENTS.md](./AI_AGENTS.md) - AI agent configuration and prompts

**User Guides:**
- `AI_infrastructure/docs/user_instructions/synergy_dashboard_complete_guide.md`
- `AI_infrastructure/docs/user_instructions/multi_agent_command_centre_guide.md`

**Implementation Reference:**
- `docs/synergy/SYNERGY_COMPLETE_REFERENCE_NOV9_2025.md` - Detailed November 2025 fixes
- `MULTI_AGENT_COORDINATION_IMPLEMENTATION_COMPLETE.md` - Coordination system build log
- `AGENT_COORDINATION_QUICK_REFERENCE.md` - Tool discovery and usage patterns

---

### External Resources

**Technologies:**
- [Supabase Documentation](https://supabase.com/docs) - PostgreSQL database hosting
- [Flask Documentation](https://flask.palletsprojects.com/) - Python web framework
- [Flask-SocketIO](https://flask-socketio.readthedocs.io/) - WebSocket support
- [psycopg2](https://www.psycopg.org/docs/) - PostgreSQL adapter for Python

**Patterns:**
- [Context Managers in Python](https://docs.python.org/3/reference/compound_stmts.html#with)
- [Kanban Methodology](https://en.wikipedia.org/wiki/Kanban)
- [NATO Phonetic Alphabet](https://en.wikipedia.org/wiki/NATO_phonetic_alphabet)

---

### File Locations (Quick Reference)

**Backend:**
```
AI_infrastructure/
├── routes/synergy_routes.py               # 4,953 lines - Synergy API
├── routes/thread_routes.py                # Thread API + assignments
├── tools/implementations/
│   ├── advanced_agent_coordination.py     # 576 lines - Coordination tools
│   └── synergy.py                         # Synergy tool wrappers
├── tools/schemas/
│   ├── advanced_agent_coordination_tools.json
│   └── synergy_tools.json
├── shared/database_utils.py               # Connection pooling
└── test_synergy_endpoints.py              # Automated tests
```

**Frontend:**
```
UI/
├── modules_external/ui-command-processor.js  # 428 lines - UI automation
└── business-ai-platform-v2.html              # ~45,000 lines total
    ├── Synergy Dashboard (lines ~21000-24000)
    └── Multi-Agent Dashboard (lines ~14000-17000)
```

**Database:**
```
Supabase PostgreSQL:
├── synergy_sessions schema
│   ├── synergy_sessions (main cards table)
│   └── synergy_internal_docs (rich text docs)
└── sessions schema
    ├── threads (conversation threads)
    ├── messages (thread messages)
    ├── cross_thread_requests (agent communication)
    └── thread_assignments (location tracking)
```

---

### Migration History

| Date | Migration | Description | Status |
|------|-----------|-------------|--------|
| Oct 2025 | `001_create_synergy_schema.sql` | Initial Synergy tables | ✅ Complete |
| Oct 2025 | `002_add_linked_thread_ids.sql` | Bidirectional linking | ✅ Complete |
| Nov 2025 | `003_add_cross_thread_requests.sql` | Agent communication table | ✅ Complete |
| Nov 2025 | `004_synergy_ui_fixes.sql` | Field name normalization | ✅ Complete |
| Dec 2025 | `005_connection_pooling.sql` | Add connection pool config | ✅ Complete |

**Running Migrations:**
```bash
cd AI_infrastructure/migrations
python run_migration.py 003_add_cross_thread_requests.sql

# Verify migration
python -c "from shared.database_utils import execute_query; print(execute_query('SELECT COUNT(*) FROM sessions.cross_thread_requests', fetch_mode='value'))"
```

---

### Performance Metrics

**Measured on Production (Render.com):**

| Operation | Average Time | 95th Percentile | Notes |
|-----------|-------------|-----------------|-------|
| List Synergy cards (50 cards) | 156ms | 230ms | Includes thread count queries |
| Create Synergy card | 45ms | 78ms | Single INSERT |
| Update Synergy card | 38ms | 65ms | Single UPDATE |
| Move card between columns | 42ms | 71ms | UPDATE + activity log |
| Link thread to card | 67ms | 95ms | UPDATE + bidirectional sync |
| Assign agent work | 123ms | 189ms | Thread CREATE + message INSERT + UI commands |
| Cross-thread request | 89ms | 134ms | Request INSERT + message INSERT |
| Respond to request | 76ms | 112ms | UPDATE + message INSERT |

**Database Query Counts (Typical User Session):**
- Initial Synergy load: 3 queries (cards, threads, docs)
- Agent assignment: 5 queries (thread check, create/update, message, slugs)
- Cross-thread communication: 4 queries (request INSERT, SELECT, message INSERTs)

**Optimization Opportunities:**
1. Add Redis cache for frequently-accessed cards
2. Batch thread detail queries (currently N+1)
3. Implement WebSocket-only updates (skip polling)
4. Add database indexes on `linked_thread_ids` (GIN index for array)

---

### Database Indexes (Complete List)

```sql
-- synergy_sessions.synergy_sessions
CREATE INDEX idx_synergy_user_id ON synergy_sessions.synergy_sessions(user_id);
CREATE INDEX idx_synergy_status ON synergy_sessions.synergy_sessions(status);
CREATE INDEX idx_synergy_priority ON synergy_sessions.synergy_sessions(priority);
CREATE INDEX idx_synergy_created_at ON synergy_sessions.synergy_sessions(created_at DESC);

-- sessions.threads
CREATE INDEX idx_threads_user_id ON sessions.threads(user_id);
CREATE INDEX idx_threads_slug ON sessions.threads(slug);
CREATE INDEX idx_threads_agent ON sessions.threads(agent);
CREATE INDEX idx_threads_synergy_card_id ON sessions.threads(synergy_card_id);

-- sessions.messages
CREATE INDEX idx_messages_thread_id ON sessions.messages(thread_id);
CREATE INDEX idx_messages_created_at ON sessions.messages(created_at DESC);

-- sessions.cross_thread_requests
CREATE INDEX idx_cross_thread_target ON sessions.cross_thread_requests(target_thread_id, status);
CREATE INDEX idx_cross_thread_source ON sessions.cross_thread_requests(source_thread_id, created_at DESC);
CREATE INDEX idx_cross_thread_status ON sessions.cross_thread_requests(status, created_at DESC);
```

**Query Optimization Examples:**
```sql
-- ✅ FAST (uses idx_synergy_user_id + idx_synergy_status)
SELECT * FROM synergy_sessions.synergy_sessions
WHERE user_id = 1 AND status = 'in-progress'
ORDER BY created_at DESC;

-- ❌ SLOW (no index on tags[])
SELECT * FROM synergy_sessions.synergy_sessions
WHERE 'urgent' = ANY(tags);

-- ✅ FIX: Add GIN index
CREATE INDEX idx_synergy_tags ON synergy_sessions.synergy_sessions USING GIN(tags);
```

---

**End of Documentation**

**Document Version:** 2.1.0  
**Last Updated:** January 18, 2026  
**Total Sections:** 11  
**Code Examples:** 47  
**Diagrams:** 3  
**API Endpoints Documented:** 15+  
**Tools Documented:** 3

**Status:** ✅ Production Ready - Comprehensive Reference

---

**Changelog:**

- **v2.1.0 (Jan 18, 2026)** - Consolidated documentation from 30+ scattered files
- **v2.0 (Nov 9, 2025)** - Synergy UI fixes (11 critical issues resolved)
- **v1.9 (Nov 16, 2025)** - Multi-agent coordination tools complete
- **v1.8 (Dec 6, 2025)** - Connection leak fixes (nested context managers)
- **v1.7 (Nov 17, 2025)** - Thread slug persistence fix
- **v1.0 (Oct 2025)** - Initial release (Synergy Dashboard + basic agent support)

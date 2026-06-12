# AI Agents Platform - Complete System Documentation
**Last Updated:** November 8, 2025  
**Version:** 3.0 - Consolidated Documentation  
**Status:** Production Ready

---

## 📋 TABLE OF CONTENTS

1. [System Overview](#system-overview)
2. [Architecture](#architecture)
3. [Database Schema](#database-schema)
4. [Key Features](#key-features)
5. [Tool System](#tool-system)
6. [UI Components](#ui-components)
7. [API Endpoints](#api-endpoints)
8. [Authentication & OAuth](#authentication--oauth)
9. [Synergy Board](#synergy-board)
10. [Thread Persistence](#thread-persistence)
11. [Development Guide](#development-guide)
12. [Troubleshooting](#troubleshooting)

---

## SYSTEM OVERVIEW

### The Grand Vision

This is a **professional AI orchestration platform** designed to revolutionize how people work with AI. Instead of one AI conversation that gets lost or forgotten, this system enables:

- **Multiple AI agents working in parallel** on different specialized tasks
- **Persistent thread storage** - conversations never die, always resumable
- **Flexible agent assignment** - drag threads between agents, assign to Prime panel
- **Project coordination** - Synergy board integration for Kanban-style workflow
- **Enterprise-grade UX** - Professional interface designed for power users
- **594 tools across 20+ platforms** - Comprehensive automation ecosystem

### Technology Stack

**Backend:**
- Flask (Python 3.12+) on port 5001
- SQLite (3 databases: sessions, ai_infrastructure, synergy_sessions)
- OAuth 2.0 (Google, Microsoft)
- Anthropic Claude API (primary AI provider)
- OpenAI API (fallback)
- DeepSeek API (fallback)

**Frontend:**
- Vanilla JavaScript (ES6+)
- No framework dependencies
- Modular architecture
- LocalStorage for caching
- Server-Sent Events (SSE) for streaming

**Infrastructure:**
- Docker deployment ready
- Render.com hosting capable
- CloudFlare tunneling support
- Australia region optimized

---

## ARCHITECTURE

### Core Components

#### 1. Prime Panel (Single AI Column)
- Main AI conversation area
- Single-agent focus mode
- Persistent thread storage
- Full conversation history
- Drag-and-drop receiver for threads

#### 2. Multi-Agent Panel (NATO Columns)
- Parallel AI conversations (Alpha-1 through Zulu-26)
- Each agent has independent conversation
- Drag-and-drop thread assignment
- Collapsible columns for workspace management
- Width toggle (400px ⇄ 600px)

#### 3. Thread History Sidebar
- Complete thread archive
- Drag-and-drop to agents
- Thread metadata (title, tags, Synergy links)
- Search and filter capabilities

#### 4. Synergy Board Integration
- Kanban-style project management
- Bidirectional thread-to-project linking
- Create threads from Synergy cards
- Visual workflow coordination

### Directory Structure

```
AI_agents/
├── AI_infrastructure/          # Backend core
│   ├── core/                  # Agent workers, session managers
│   ├── routes/                # Flask API endpoints
│   ├── auth/                  # OAuth & credential management
│   ├── builders/              # Response builders
│   ├── prompts/               # System prompts
│   └── flask_app.py           # Main Flask application
├── tools/                     # Tool registry system
│   ├── implementations/       # Python tool implementations
│   ├── schemas/               # JSON tool definitions
│   └── registry_v3.py         # Tool loading & execution
├── google_workspace/          # Google API integrations
├── Microsoft_365_Connection/  # Microsoft Graph API
├── UI/                        # Frontend interface
│   ├── js/                    # JavaScript modules
│   ├── css/                   # Stylesheets
│   └── external/modules/      # External modules
├── data/                      # SQLite databases
│   ├── ai_infrastructure.db   # User data & OAuth tokens
│   ├── sessions.db            # Thread storage
│   └── synergy_sessions.db    # Project management
├── scripts/                   # Utility scripts
│   ├── startup/               # BISTART, BISTOP
│   ├── setup/                 # Initial setup scripts
│   ├── testing/               # Test scripts
│   └── maintenance/           # Cleanup & fix utilities
├── config.py                  # Global API keys
└── .env.master                # Environment variables
```

### Storage Architecture

```
Backend SQLite Databases (persistent)
    ↓
localStorage (frontend cache: thread_assignments, multi_agent_state)
    ↓
JavaScript Runtime Objects (MultiAgent, ThreadManager, AppState)
```

---

## DATABASE SCHEMA

### Three Database System

#### 1. sessions.db → `threads` table
Primary thread storage with complete conversation data.

```sql
CREATE TABLE threads (
    id TEXT PRIMARY KEY,
    user_id INTEGER NOT NULL,
    title TEXT NOT NULL,
    messages TEXT NOT NULL,  -- JSON array
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    metadata TEXT,           -- JSON object
    synergy_project_id TEXT  -- Link to Synergy board
);
```

**Purpose:**
- Store complete conversation history
- Thread titles and metadata
- Synergy project bidirectional links
- User ownership

#### 2. ai_infrastructure.db → `thread_assignments` table
Authoritative source for agent assignments.

```sql
CREATE TABLE thread_assignments (
    thread_id TEXT PRIMARY KEY,
    user_id INTEGER NOT NULL,
    assigned_location TEXT NOT NULL,  -- 'prime' or 'agent-1' through 'agent-26'
    assigned_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id)
);
```

**Purpose:**
- Track which agent each thread is assigned to
- Restore agent layout on page reload
- Support drag-and-drop functionality
- User-specific assignments

#### 3. synergy_sessions.db → `synergy_sessions` table
Synergy board project data.

```sql
CREATE TABLE synergy_sessions (
    session_id TEXT PRIMARY KEY,
    user_id INTEGER NOT NULL,
    name TEXT NOT NULL,
    description TEXT,
    status TEXT DEFAULT 'backlog',  -- backlog, in_progress, review, done
    priority TEXT DEFAULT 'medium',  -- low, medium, high, critical
    platforms TEXT,                  -- JSON array
    integrations TEXT,               -- JSON array
    documents TEXT,                  -- JSON array
    links TEXT,                      -- JSON array
    tags TEXT,                       -- JSON array
    checklist TEXT,                  -- JSON array
    start_date TEXT,
    due_date TEXT,
    progress INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    thread_ids TEXT                  -- JSON array - links to threads
);
```

**Purpose:**
- Store Synergy Kanban projects
- Support multi-platform coordination
- Bidirectional thread linking
- Rich metadata for project management

### Additional Tables (ai_infrastructure.db)

#### users table
```sql
CREATE TABLE users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    email TEXT UNIQUE NOT NULL,
    display_name TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

#### user_platform_credentials table
```sql
CREATE TABLE user_platform_credentials (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    platform TEXT NOT NULL,  -- 'google', 'microsoft', etc.
    access_token TEXT NOT NULL,
    refresh_token TEXT,
    token_expiry TEXT,
    scopes TEXT,  -- JSON array
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id)
);
```

---

## KEY FEATURES

### 1. Progressive Tool Loading (January 2025) 🎉 NEW

**CRITICAL FEATURE**: Claude now discovers tools hierarchically instead of receiving all 594 tools upfront!

**System Overview:**
- **First turn**: Send only 5 meta-tools (99.2% token reduction: 70,844 → 431 tokens)
- **Subsequent turns**: Send all 594 tools after discovery
- **Cost savings**: $211/day with 1,000 requests
- **Implementation**: `AI_infrastructure/core/agent_worker.py` lines 236-258

**How It Works:**
```python
conversation_length = len(conversation_history or [])

if conversation_length == 0:
    # First turn: 5 meta-tools only
    meta_tool_names = ['list_available_platforms', 'list_platform_tools', 
                       'get_platform_guide', 'recommend_tools_for_task',
                       'get_workflow_steps']
    tools = [all_tools_dict[name] for name in meta_tool_names]
else:
    # Subsequent turns: 594 full tools
    tools = registry.get_anthropic_tools()
```

**Status:** ✅ PRODUCTION READY

### 2. Calculator Tools Integration (January 2025)

**NEW**: InHouse Print quote calculators now accessible to AI agents!

**Available Calculator Tools (7 total):**
1. `calculate_business_cards` - Business cards with Shopify pricing
2. `calculate_flyers` - Flyers/leaflets
3. `calculate_perfect_bound_books` - Perfect bound books with glued spine
4. `calculate_corflute_signs` - Rigid signage with tier pricing
5. `calculate_booklets` - Saddle-stitched booklets
6. `get_stock_list` - Available paper stocks
7. `get_calculator_requirements` - Parameter requirements

**Integration:**
- Direct import from In_House_SQL project
- Connects to database: `C:\Users\gpoli\GIT\In_House_SQL\G_Folder`
- Uses `ComprehensiveQuoteCalculator` class
- No HTTP wrapper needed

### 3. Google Sheets Markdown Formatting v2.0 (November 2025)

Create beautifully formatted spreadsheets using simple markdown syntax.

**Usage:**
```python
registry.execute_tool(
    'google_sheets_create',
    title='Sales Report',
    headers=['# Product', '**Q3**', '**Q4**', '**Status**'],
    data=[
        ['**Premium**', '$145K', '$168K', '[G]+16%[/G]'],
        ['Standard', '$85K', '$78K', '[R]-8%[/R]']
    ],
    parse_markdown=True  # ✨ ENABLE FORMATTING
)
```

**v2.0 Compact Syntax:**
- `(L)`, `(R)`, `(C)` - Alignment (left, right, center)
- `[R]`, `[G]`, `[B]`, `[P]`, `[GR]`, `[BK]` - Text colors (no closing tag)
- `{LR}`, `{LG}`, `{LB}`, `{LP}`, `{LGR}` - Background colors (no closing tag)
- `**bold**`, `*italic*`, `# Header` - Standard markdown

**Benefits:**
- 96% time savings (15 min → 30 sec per sheet)
- 100% backward compatible (opt-in)
- Professional formatting
- Color-coded dashboards

### 4. Synergy Board Progressive Disclosure (November 2025)

4-layer progressive disclosure architecture for Synergy tools.

**Layers:**
1. **Awareness** - System prompt (8 lines, was 46)
2. **Discovery** - Meta-tools (existing system)
3. **Instruction** - On-demand tool with 7 comprehensive topics
4. **Execution** - Enhanced schemas with guidance blocks

**Instruction Tool Topics:**
1. overview - Synergy Dashboard concept
2. quickstart - Create your first project
3. workflow - Typical usage patterns
4. updating_arrays - Safe array field updates (CRITICAL)
5. field_reference - Complete field documentation
6. troubleshooting - Common issues & solutions
7. examples - Real-world use cases

**Token Savings:** 80% reduction (8,600 → 600 tokens base)

### 5. Thread Persistence System

Complete conversation restoration after browser reload/crash.

**Features:**
- Automatic save to SQLite on every message
- localStorage caching for instant load
- Agent assignment restoration
- Synergy link preservation
- No data loss on browser close

**Implementation:**
- Backend: SQLite `threads` table + `thread_assignments` table
- Frontend: `ThreadManager.js` + localStorage sync
- Passive auto-save every 30 seconds
- Immediate save on critical events

### 6. Multi-Agent Coordination

26 parallel AI agents working simultaneously.

**NATO Agent Names:**
Alpha-1, Bravo-2, Charlie-3, Delta-4, Echo-5, Foxtrot-6, Golf-7, Hotel-8, 
India-9, Juliet-10, Kilo-11, Lima-12, Mike-13, November-14, Oscar-15, 
Papa-16, Quebec-17, Romeo-18, Sierra-19, Tango-20, Uniform-21, Victor-22, 
Whiskey-23, X-ray-24, Yankee-25, Zulu-26

**Capabilities:**
- Independent conversations per agent
- Drag-and-drop thread assignment
- Width toggling (400px/600px)
- Collapsible columns
- Persistent state across reloads

---

## TOOL SYSTEM

### Architecture Overview

**594 tools across 20+ platforms:**
- Google Workspace (Gmail, Docs, Sheets, Calendar, Drive, Meet, Tasks, Slides)
- Microsoft 365 (Outlook, Word, Excel, PowerPoint, OneDrive, Teams, Calendar)
- Stripe (payments, customers, subscriptions)
- Slack (messaging, channels)
- Calculator (InHouse Print quotes)
- Synergy (project management)
- Meta-tools (tool discovery)
- And more...

### Tool Structure - Two Required Files

Every tool needs:
1. **Schema file** (JSON) in `tools/schemas/` - Defines the tool interface
2. **Implementation file** (Python) in `tools/implementations/` - Contains the code

### Tool Loading Process

1. **Schema Loading** - Loads JSON schemas from `tools/schemas/`
2. **Implementation Loading** - Loads Python implementations from `tools/implementations/`
3. **Registry Creation** - Creates unified registry with 594 tools
4. **Credential Injection** - Injects user credentials at runtime

### Adding New Tools

**Step 1: Create Schema**

`tools/schemas/my_platform_tools.json`:
```json
{
  "platform": "my_platform",
  "description": "Brief description",
  "tools": [
    {
      "name": "my_platform_create_item",
      "description": "Create a new item",
      "platform": "my_platform",
      "parameters": {
        "type": "object",
        "properties": {
          "title": {
            "type": "string",
            "description": "Item title"
          }
        },
        "required": ["title"]
      }
    }
  ]
}
```

**Step 2: Create Implementation**

`tools/implementations/my_platform.py`:
```python
def my_platform_create_item(title: str, **kwargs) -> dict:
    """Create a new item"""
    access_token = kwargs.get('access_token')
    if not access_token:
        raise ValueError("access_token required")
    
    # API call
    response = requests.post(
        'https://api.myplatform.com/items',
        json={'title': title},
        headers={'Authorization': f'Bearer {access_token}'}
    )
    
    return response.json()
```

**Step 3: Test**

```python
from tools.registry_v3 import RegistryV3
registry = RegistryV3()
print(f"Total tools: {len(registry.tools)}")
```

### Credential Injection Pattern

All tools receive credentials via `**kwargs`:

```python
def my_tool(param1, param2, **kwargs):
    # Credentials injected at runtime
    access_token = kwargs.get('access_token')
    refresh_token = kwargs.get('refresh_token')
    
    # Use credentials for API calls
    headers = {'Authorization': f'Bearer {access_token}'}
```

**Credentials are fetched from:**
- `user_platform_credentials` table in `ai_infrastructure.db`
- By `CredentialInjector` class in `AI_infrastructure/auth/credential_injector.py`

---

## UI COMPONENTS

### Modular Architecture

**Core Modules:**
- `UI/js/multi-agent.js` - Multi-agent panel management
- `UI/js/thread-manager.js` - Thread CRUD operations
- `UI/js/synergy-board.js` - Synergy Kanban board
- `UI/js/tabulator-functions.js` - Table rendering utilities
- `UI/js/app-state.js` - Global state management

**External Modules:**
- `UI/external/modules/stock-management/` - Stock inventory module
- `UI/external/modules/inhouse-print/` - InHouse Print module
- `UI/external/modules/quote-calculator/` - Quote calculator module
- `UI/external/modules/inhouse-kanban/` - Kanban board module
- `UI/external/modules/database-visualizer/` - DB visualization module

### Key UI Features

**1. Drag-and-Drop System**
- Drag threads from sidebar to agents
- Drag threads between agents
- Visual feedback during drag
- Drop zones highlight on hover

**2. Responsive Design**
- Desktop-first design (1920x1080 optimal)
- Resizable panels
- Collapsible columns
- Mobile-friendly layouts

**3. Real-time Updates**
- Server-Sent Events (SSE) for streaming
- Live message updates
- Instant agent state changes
- Automatic UI synchronization

**4. Visual Feedback**
- Loading spinners
- Success/error toasts
- Progress indicators
- Badge notifications

---

## API ENDPOINTS

### Base URL
```
http://localhost:5001/api
```

### Agent Routes (`/api/agent/*`)

#### POST /api/agent/chat
Send message to AI agent.

**Request:**
```json
{
  "message": "Hello, help me with X",
  "user_id": 1,
  "thread_id": "thread_abc123",
  "location": "prime"
}
```

**Response:**
```json
{
  "success": true,
  "response": "AI response text",
  "thread_id": "thread_abc123",
  "session_id": "session_xyz789"
}
```

#### POST /api/agent/stream
Stream AI responses via Server-Sent Events.

**Request:** Same as /api/agent/chat

**Response:** SSE stream
```
data: {"type": "text", "content": "AI response chunk"}
data: {"type": "tool_use", "name": "gmail_send_email", "input": {...}}
data: {"type": "tool_result", "result": {...}}
data: {"type": "done"}
```

#### GET /api/agent/threads
List all threads for user.

**Query Params:**
- `user_id` (required)

**Response:**
```json
{
  "success": true,
  "threads": [
    {
      "id": "thread_abc123",
      "title": "Help with marketing",
      "created_at": "2025-11-08T10:00:00Z",
      "updated_at": "2025-11-08T10:30:00Z",
      "synergy_project_id": "proj_xyz"
    }
  ]
}
```

#### GET /api/agent/threads/<thread_id>
Get specific thread details.

**Response:**
```json
{
  "success": true,
  "thread": {
    "id": "thread_abc123",
    "title": "Help with marketing",
    "messages": [...],
    "metadata": {...},
    "synergy_project_id": "proj_xyz"
  }
}
```

#### PUT /api/agent/threads/<thread_id>
Update thread details.

**Request:**
```json
{
  "title": "Updated title",
  "metadata": {...}
}
```

#### DELETE /api/agent/threads/<thread_id>
Delete thread.

#### POST /api/agent/threads/<thread_id>/assign
Assign thread to agent.

**Request:**
```json
{
  "user_id": 1,
  "location": "agent-5"
}
```

#### GET /api/agent/assignments
Get all thread assignments for user.

**Query Params:**
- `user_id` (required)

**Response:**
```json
{
  "success": true,
  "assignments": {
    "thread_abc123": "prime",
    "thread_def456": "agent-3"
  }
}
```

### Synergy Routes (`/api/synergy/*`)

#### POST /api/synergy/sessions
Create new Synergy project.

**Request:**
```json
{
  "user_id": 1,
  "name": "Website Redesign",
  "description": "Q4 2025 website overhaul",
  "status": "backlog",
  "priority": "high",
  "platforms": ["google_workspace", "slack"],
  "tags": ["website", "design"]
}
```

#### GET /api/synergy/sessions
List all Synergy projects.

#### GET /api/synergy/sessions/<session_id>
Get specific project.

#### PUT /api/synergy/sessions/<session_id>
Update project.

#### DELETE /api/synergy/sessions/<session_id>
Delete project.

#### POST /api/synergy/sessions/<session_id>/move
Move project to different status column.

**Request:**
```json
{
  "status": "in_progress"
}
```

---

## AUTHENTICATION & OAUTH

### OAuth Flow

**Google OAuth:**
1. User clicks "Connect Google Account"
2. Redirects to `/api/oauth/google/authorize`
3. Google consent screen
4. Callback to `/api/oauth/google/callback`
5. Store tokens in `user_platform_credentials` table

**Microsoft OAuth:**
1. User clicks "Connect Microsoft Account"
2. Redirects to `/api/oauth/microsoft/authorize`
3. Microsoft consent screen
4. Callback to `/api/oauth/microsoft/callback`
5. Store tokens in `user_platform_credentials` table

### Required Environment Variables

**.env.master:**
```bash
# Google OAuth (uses service-account.json)
# No env vars needed

# Microsoft OAuth
MICROSOFT_CLIENT_ID=your_client_id
MICROSOFT_CLIENT_SECRET=your_client_secret
MICROSOFT_TENANT_ID=common

# AI Providers
ANTHROPIC_API_KEY=sk-ant-...
OPENAI_API_KEY=sk-...
DEEPSEEK_API_KEY_1=sk-...
```

### Credential Storage

**Table:** `user_platform_credentials`

**Fields:**
- `user_id` - User ID
- `platform` - Platform name ('google', 'microsoft', etc.)
- `access_token` - OAuth access token
- `refresh_token` - OAuth refresh token
- `token_expiry` - Token expiration timestamp
- `scopes` - JSON array of granted scopes

**Token Refresh:**
- Automatic refresh when expired
- Implemented in `CredentialInjector.get_google_credentials()`
- Uses refresh token to get new access token

---

## SYNERGY BOARD

### Overview

Synergy is a Kanban-style project management system integrated into the AI Agents Platform. It provides visual coordination for multi-platform projects and bidirectional linking with AI threads.

### Board Layout

**4 Columns:**
1. **Backlog** - Projects not yet started
2. **In Progress** - Active projects
3. **Review** - Projects pending review
4. **Done** - Completed projects

### Card Fields

**Required:**
- `name` - Project name
- `description` - Project description
- `status` - Current status (backlog, in_progress, review, done)

**Optional:**
- `priority` - Priority level (low, medium, high, critical)
- `platforms` - Array of platforms used (e.g., ["google_workspace", "slack"])
- `integrations` - Array of integrations
- `documents` - Array of document objects with `name`, `url`, `type`
- `links` - Array of link objects with `name`, `url`
- `tags` - Array of tag strings
- `checklist` - Array of checklist items with `task`, `completed`
- `start_date` - Project start date (ISO 8601)
- `due_date` - Project due date (ISO 8601)
- `progress` - Progress percentage (0-100)
- `thread_ids` - Array of linked thread IDs

### Creating Projects

**Via UI:**
1. Click "New Project" button
2. Fill in project details
3. Select platforms and add metadata
4. Click "Create"

**Via AI Agent:**
```
User: "Create a Synergy project for email automation campaign"
AI: Calls synergy_smart_project_tracker(
    action="create",
    name="Email Automation Campaign",
    platforms=["google_workspace", "microsoft_365"],
    ...
)
```

### Linking Threads

**Create Thread from Project:**
1. Click Synergy card
2. Click "Create AI Thread"
3. Thread opens in Prime with pre-populated context
4. Badge shows Synergy link: 🔗 Project Name

**Link Existing Thread:**
1. Drag thread to Synergy card
2. OR use AI command: "Link this thread to Synergy project X"

### Array Field Safety

**CRITICAL:** Array fields (documents, links, tags, checklist) require special handling.

**❌ WRONG (Data Loss):**
```python
synergy_smart_project_tracker(
    action="update",
    session_id="proj_123",
    documents=[{"name": "New Doc", "url": "..."}]  # DELETES existing documents!
)
```

**✅ CORRECT (Safe Update):**
```python
# Step 1: Get current project
project = synergy_smart_project_tracker(
    action="get",
    session_id="proj_123"
)

# Step 2: Append to existing array
current_docs = project.get('documents', [])
current_docs.append({"name": "New Doc", "url": "..."})

# Step 3: Update with complete array
synergy_smart_project_tracker(
    action="update",
    session_id="proj_123",
    documents=current_docs  # ✅ Preserves existing + adds new
)
```

**Use Instruction Tool:**
```
Call synergy_agent_instructions('updating_arrays') for detailed guidance
```

---

## THREAD PERSISTENCE

### How It Works

**3-Layer Storage:**
1. **SQLite Database** - Persistent backend storage
2. **localStorage** - Frontend cache for instant load
3. **JavaScript Runtime** - Active state in memory

### Save Flow

```
User sends message
    ↓
AI processes & responds
    ↓
Backend saves to sessions.db (threads table)
    ↓
Backend updates thread_assignments table
    ↓
Frontend receives response
    ↓
Frontend updates localStorage cache
    ↓
JavaScript runtime state updated
```

### Restore Flow

```
Page load
    ↓
Frontend checks localStorage cache
    ↓
Load cached threads instantly (optimistic UI)
    ↓
Backend fetches latest from database
    ↓
Frontend reconciles cache with database
    ↓
Update UI with authoritative data
    ↓
Restore agent assignments
```

### Auto-Save

**Passive auto-save every 30 seconds:**
- Saves all active threads
- Updates localStorage cache
- No user interaction required
- Silent operation

**Immediate save triggers:**
- User sends message
- Thread title changed
- Agent assignment changed
- Synergy link added/removed
- Critical state changes

### Data Loss Prevention

**Strategies:**
1. **Optimistic UI** - Show changes immediately, sync in background
2. **Debounced saves** - Batch updates to reduce server load
3. **Conflict resolution** - Last-write-wins for most fields
4. **Version tracking** - `updated_at` timestamps for conflict detection
5. **Error recovery** - Retry failed saves with exponential backoff

---

## DEVELOPMENT GUIDE

### Getting Started

**1. Clone repository:**
```bash
git clone https://github.com/gerardovsa/AI_agents.git
cd AI_agents
```

**2. Install dependencies:**
```bash
pip install -r requirements.txt
```

**3. Configure environment:**
```bash
cp .env.example .env.master
# Edit .env.master with your API keys
```

**4. Start server:**
```bash
cd AI_infrastructure
python flask_app.py
# OR use PATH command:
BISTART
```

**5. Open browser:**
```
http://localhost:5001
```

### Adding New Features

**Follow the documentation standards:**
- File headers required (see `templates/FILE_HEADER_TEMPLATE.md`)
- README.md for every folder
- NOTES.md for active development
- CHANGELOG.md for production code
- Update existing files, never create duplicates

**Tool development:**
1. Create schema in `tools/schemas/`
2. Create implementation in `tools/implementations/`
3. Test with `python -c "from tools.registry_v3 import RegistryV3; r = RegistryV3()"`
4. Verify in Flask app

**UI development:**
1. Add module to `UI/external/modules/` if external
2. Add JavaScript to `UI/js/` if core
3. Update `UI/business-ai-platform-v2.html` for integration
4. Test in browser

### Testing

**Backend tests:**
```bash
cd scripts/testing
python test_oauth_all.py
python test_microsoft_google_execution.py
```

**Tool tests:**
```bash
cd testing_tools
python test_sheets_markdown.py
python test_all_google_platforms.py
```

**Manual testing:**
```bash
# Start server
BISTART

# In another terminal, test API
curl -X POST http://localhost:5001/api/agent/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "Hello", "user_id": 1}'
```

### Code Conventions

**Python:**
- PEP 8 style guide
- Type hints required
- Docstrings for all public functions
- Never use emojis in code (causes encoding errors)

**JavaScript:**
- ES6+ features
- Async/await over promises
- No console.log in production
- Use proper error handling

**Database:**
- Always use `data/` folder for SQLite files
- Use parameterized queries (prevent SQL injection)
- Include timestamps (created_at, updated_at)

---

## TROUBLESHOOTING

### Common Issues

#### 1. Server won't start

**Error:** `Address already in use: 5001`

**Solution:**
```bash
# Find process using port 5001
netstat -ano | findstr :5001

# Kill process
taskkill /PID <process_id> /F

# Restart server
BISTART
```

#### 2. Tool not loading

**Error:** `Tool 'X' not found in registry`

**Check:**
1. Schema exists in `tools/schemas/`
2. Implementation exists in `tools/implementations/`
3. Function name matches schema `name` field
4. Registry reloaded: Restart Flask app

#### 3. OAuth not working

**Error:** `Invalid credentials` or `Token expired`

**Check:**
1. Environment variables set in `.env.master`
2. Client ID/Secret correct
3. Redirect URI matches OAuth app settings
4. Token refresh implemented in credential injector

#### 4. Thread not persisting

**Error:** Thread disappears on reload

**Check:**
1. `sessions.db` exists in `data/` folder
2. Thread saved to backend (check Flask logs)
3. `thread_assignments` table updated
4. localStorage not disabled in browser

#### 5. Synergy card not updating

**Error:** Changes not saved or data loss

**Check:**
1. Using correct update pattern (get → modify → update)
2. Not replacing array fields directly
3. Session ID correct
4. Backend logs for errors

### Debug Commands

**Check databases:**
```bash
cd data
sqlite3 ai_infrastructure.db "SELECT * FROM users;"
sqlite3 sessions.db "SELECT id, title FROM threads LIMIT 10;"
sqlite3 synergy_sessions.db "SELECT session_id, name, status FROM synergy_sessions;"
```

**Check tool loading:**
```python
from tools.registry_v3 import RegistryV3
registry = RegistryV3()
print(f"Total tools: {len(registry.tools)}")
print(f"Platforms: {registry.get_all_platforms()}")
```

**Check OAuth tokens:**
```python
import sqlite3
conn = sqlite3.connect('data/ai_infrastructure.db')
cursor = conn.execute("SELECT platform, token_expiry FROM user_platform_credentials WHERE user_id=1")
for row in cursor:
    print(f"{row[0]}: {row[1]}")
```

### Performance Issues

**Slow AI responses:**
1. Check API key rate limits
2. Verify network connectivity
3. Use streaming endpoint (`/api/agent/stream`)
4. Consider caching frequent responses

**Large database:**
1. Archive old threads to separate database
2. Vacuum SQLite databases: `VACUUM;`
3. Add indexes for frequently queried fields
4. Consider pagination for thread list

**Memory leaks:**
1. Check browser console for errors
2. Clear localStorage periodically
3. Restart Flask app
4. Monitor Python memory usage

---

## APPENDIX

### Quick Reference

**Start server:**
```bash
BISTART
```

**Talk to AI:**
```bash
CHAT "Your message here"
```

**Test tool loading:**
```bash
python -c "from tools.registry_v3 import RegistryV3; print(f'{len(RegistryV3().tools)} tools')"
```

**Important Files:**
- `config.py` - API keys
- `AI_infrastructure/flask_app.py` - Main server
- `tools/registry_v3.py` - Tool registry
- `UI/business-ai-platform-v2.html` - Main UI

**Important URLs:**
- Dashboard: `http://localhost:5001`
- API: `http://localhost:5001/api`
- OAuth callback: `http://localhost:5001/api/oauth/google/callback`

### Version History

**v3.0 (November 2025):**
- Consolidated documentation
- Cleanup of redundant files
- Progressive tool loading stable
- Synergy progressive disclosure complete

**v2.5 (November 2025):**
- Google Sheets markdown formatting v2.0
- Synergy board enhancements
- Thread persistence fixes
- UI standardization

**v2.0 (October 2025):**
- Multi-agent panel (26 agents)
- Thread persistence system
- Synergy board integration
- Calculator tools integration

**v1.0 (September 2025):**
- Initial release
- Single agent conversation
- Basic tool system
- Google/Microsoft OAuth

---

**END OF DOCUMENTATION**

For additional help, see:
- `.github/copilot-instructions.md` - GitHub Copilot context
- `README.md` - Quick start guide
- `tools/` folder - Tool implementation examples
- `UI/module_development/` - UI module development guide

# AI Agents Platform - System Architecture

**Last Updated:** January 14, 2026  
**Production Branch:** `v10`  
**Deployment Target:** Render.com (Docker)  
**Database:** Supabase PostgreSQL  
**Region:** Singapore (optimized for Australia, ~100-150ms latency)

---

## 🎯 System Overview

### What is This System?

The **AI Agents Platform** is a professional multi-tenant AI orchestration system that enables organizations to:
- Deploy **multiple AI agents** working in parallel on specialized tasks
- Maintain **persistent conversation threads** that never expire
- Integrate **80+ business tools** across platforms (Xero, Shopify, Google Workspace, Microsoft 365, InHouse Print databases)
- Build **custom calculators** for complex pricing and quote generation
- Manage **visual automation workflows** with drag-and-drop canvas
- Provide **enterprise-grade project coordination** via Synergy Kanban board

### Who Is It For?

**Primary Use Case:** Printing & publishing companies (InHouse Print) needing:
- Complex quote calculations (business cards, flyers, books, booklets)
- Production workflow management
- Customer relationship intelligence
- Multi-platform integration (Xero accounting, Shopify e-commerce, SQL databases)

**Deployment Model:** 
- **Multi-tenant SaaS** - Each client gets isolated instance on their own Render account
- **White-label ready** - Client-specific branding and module configurations
- **Plug-and-play modules** - Enable/disable features per client deployment

---

## 🏗️ Technology Stack

### Backend

| Component | Technology | Version | Purpose |
|-----------|------------|---------|---------|
| **Runtime** | Python | 3.11 | Core application logic |
| **Web Framework** | Flask | 3.0.0 | REST API + WebSocket server |
| **WSGI Server** | Gunicorn | 21.2.0 | Production HTTP server with gevent workers |
| **Real-time** | Flask-SocketIO | 5.5.1 | WebSocket bidirectional communication |
| **Database** | PostgreSQL (Supabase) | 15+ | Primary data store (4 schemas) |
| **Connection Pooling** | psycopg2-binary | 2.9.9 | Thread-safe DB connections (PgBouncer) |
| **AI Models** | Anthropic Claude | Latest | Primary AI (Claude 3.5 Sonnet, Opus) |
| | OpenAI GPT | 1.35.0 | Secondary AI + embeddings |
| | DeepSeek | Latest | Alternative AI provider |
| **Vector Search** | Pinecone | 3.0+ | Semantic document search |
| | Qdrant | 1.7+ | Alternative vector database |
| **Document Processing** | python-docx | 1.1.0 | DOCX extraction with formatting |
| | openpyxl | 3.1.0+ | Excel extraction with tables |
| | pypdf | 3.17.0+ | PDF text extraction |
| | pytesseract | 0.3.10+ | OCR for images |
| **ML & Analytics** | pandas | 2.3.3 | Data manipulation |
| | numpy | 2.3.3 | Numerical operations |
| | scikit-learn | 1.3.0+ | ML models (forecasting, predictions) |
| | statsmodels | 0.14.0+ | Time series forecasting (ARIMA) |
| **Engineering** | CadQuery | 2.6.1 | Parametric 3D CAD modeling |
| | matplotlib | 3.10.5 | Engineering charts and diagrams |
| **Integrations** | xero-python | 9.3.0+ | Xero accounting API |
| | ShopifyAPI | 12.7.0+ | Shopify e-commerce API |
| | google-api-python-client | 2.100.0+ | Google Workspace APIs |
| | pymssql | 2.2.0+ | SQL Server connections (InHouse Print) |

### Frontend

| Component | Technology | Purpose |
|-----------|------------|---------|
| **Architecture** | Single-Page Application | Vanilla HTML/CSS/JavaScript |
| **Main File** | `business-ai-platform-v2.html` | ~15,000 lines - main UI |
| **Real-time** | WebSockets (SocketIO client) | Bidirectional server communication |
| **Rendering** | Marked.js | Markdown to HTML conversion |
| **Code Highlighting** | Highlight.js | Syntax highlighting in code blocks |
| **Module System** | ES6 modules | Dynamic plugin loading |
| **State Management** | localStorage + sessionStorage | Thread persistence, user preferences |
| **CSS Framework** | Custom (no Bootstrap/Tailwind) | ~3,000 lines custom CSS |

### Infrastructure

| Component | Technology | Purpose |
|-----------|------------|---------|
| **Hosting** | Render.com | Docker-based deployment |
| **Container** | Docker | Multi-stage build (Python 3.11-slim) |
| **Database** | Supabase | Managed PostgreSQL with PgBouncer |
| **Storage** | Render Persistent Disk | 10GB for file uploads, logs |
| **CI/CD** | GitHub Actions | Docker image build + push to GHCR |
| **Region** | Singapore | 100-150ms latency to Australia |
| **Monitoring** | Render Logs + Custom | Flask logging + APScheduler monitoring |

---

## 📁 Project Architecture

### High-Level Directory Structure

```
AI_agents/
├── 🔧 AI_infrastructure/           # Backend core (Flask, database, auth)
│   ├── flask_app.py                # Main Flask server (4,127 lines)
│   ├── routes/                     # 70+ API route files
│   ├── shared/                     # Database utilities, clients
│   ├── auth/                       # User authentication, OAuth
│   ├── core/                       # Session manager, AI client
│   ├── tools/                      # Tool execution engine
│   ├── migrations/                 # Database schema migrations
│   └── logs/                       # Application logs
│
├── 🎨 UI/                          # Frontend application
│   ├── business-ai-platform-v2.html # Main SPA (~15,000 lines)
│   ├── modules_internal/           # Core platform modules
│   │   ├── agents/                 # Multi-agent system
│   │   ├── communication-hub/      # Email integration
│   │   ├── synergy/                # Kanban project board
│   │   ├── automation-workflows/   # Visual workflow canvas
│   │   ├── settings-sidebar/       # User preferences
│   │   └── thread-manager/         # Thread lifecycle
│   │
│   └── modules_external/           # Pluggable business modules
│       ├── quote-calculator/       # InHouse Print pricing (80 tools)
│       ├── xero/                   # Xero accounting integration
│       ├── shopify/                # Shopify e-commerce
│       ├── inhouse-print/          # Fred database tools
│       ├── inhouse-kanban/         # Production workflow
│       ├── stock-management/       # Inventory tracking
│       ├── google-drive/           # Google Drive integration
│       ├── microsoft-onedrive/     # OneDrive integration
│       ├── parametric-cad/         # 3D CAD modeling
│       └── [15+ more modules]
│
├── 🛠️ tools/                       # Tool registry & execution
│   ├── registry_v3.py              # Tool discovery & registration
│   ├── schemas/                    # 200+ tool JSON schemas
│   └── implementations/            # Tool wrapper functions
│
├── 📦 Deployment Files
│   ├── render.yaml                 # Render.com configuration
│   ├── Dockerfile                  # Docker multi-stage build
│   ├── requirements.txt            # Python dependencies (120+)
│   ├── package.json                # Node.js CAD libraries
│   └── startup.sh                  # Container initialization
│
└── 📚 Documentation                # 500+ markdown files
    ├── ARCHITECTURE.md             # This file
    ├── README.md                   # Project overview
    ├── COMPLETE_DATABASE_ARCHITECTURE.md
    └── [extensive module docs]
```

---

## 🎯 Core Components Deep Dive

### 1. Flask Backend (`AI_infrastructure/`)

**Purpose:** REST API server + WebSocket handler + Tool execution engine

**Key Files:**
- **`flask_app.py`** (4,127 lines) - Main application server
  - Tool registry initialization (80+ tools from modules)
  - Route blueprint registration (70+ route files)
  - WebSocket handlers for real-time streaming
  - Database connection management
  - OAuth callback routing

- **`shared/database_utils.py`** (1,130 lines) - **ALL database operations**
  - Connection pooling (psycopg2 + PgBouncer)
  - `execute_query()` - Single interface for all DB operations
  - Schema management (ai_infrastructure, sessions, synergy_sessions, public)
  - Thread-safe connection handling
  - Automatic rollback on errors

- **`routes/`** - 70+ API endpoint files
  - `agent_routes_v4.py` - AI streaming endpoints
  - `thread_routes.py` - Thread CRUD operations
  - `communication_routes.py` - Email/messaging integration
  - `automation_routes.py` - Visual workflow execution
  - `synergy_routes.py` - Kanban board operations
  - `auth_routes.py` - User authentication
  - `google_auth_routes_V2_FIXED.py` - Google OAuth
  - `microsoft_auth_routes_V2_FIXED.py` - Microsoft OAuth
  - `quote_calculator_routes.py` - InHouse Print pricing
  - `xero/*_routes.py` - Xero accounting (10+ files)

**Responsibilities:**
- Handle HTTP requests from frontend
- Stream AI responses via Server-Sent Events (SSE)
- Execute tools requested by AI agents
- Manage user sessions and authentication
- Coordinate database transactions
- OAuth token refresh automation

**Dependencies:**
- Sessions schema (threads, messages, user_sessions)
- ai_infrastructure schema (users, oauth_tokens, credentials)
- Tool registry (200+ tools across 25+ modules)

### 2. Tool System (`tools/`)

**Purpose:** Discover, register, and execute 200+ business tools

**Architecture:**
```
Module Plugin System → Tool Registry V3 → Tool Executor → External APIs
```

**Key Files:**

**`tools/registry_v3.py`** (1,075 lines)
- Auto-discovers modules from `UI/modules_external/*/tools/*.json`
- Loads tool schemas (name, description, parameters)
- Loads implementations from `*/implementations/*_wrapper.py`
- Credential injection (`_user_id`, `_injected_credentials`)
- Redis caching for 50x faster startup
- Thread-local storage for worker thread context

**Tool Definition Pattern (JSON):**
```json
{
  "name": "xero_get_invoices",
  "description": "Get invoices from Xero accounting",
  "parameters": {
    "type": "object",
    "properties": {
      "status": {
        "type": "string",
        "enum": ["DRAFT", "SUBMITTED", "AUTHORISED", "PAID"]
      },
      "date_from": {"type": "string", "format": "date"},
      "date_to": {"type": "string", "format": "date"}
    }
  },
  "platform": "xero"
}
```

**Tool Implementation Pattern (Python):**
```python
from tools.registry_v3 import tool_executor

@tool_executor()
def xero_get_invoices(status: str = None, date_from: str = None, 
                      date_to: str = None, **kwargs):
    """Get invoices from Xero accounting."""
    try:
        from AI_infrastructure.shared.database_utils import execute_query
        
        # Get user credentials from database
        user_id = kwargs.get('_user_id')
        credentials = execute_query(
            "SELECT * FROM ai_infrastructure.user_platform_credentials WHERE user_id=%s",
            (user_id,), fetch_mode='one'
        )
        
        # Execute API call
        from xero import XeroAPI
        api = XeroAPI(credentials['client_id'], credentials['client_secret'])
        invoices = api.get_invoices(status, date_from, date_to)
        
        return {"success": True, "data": invoices}
    except Exception as e:
        return {"success": False, "error": str(e)}
```

**Module Organization:**
```
UI/modules_external/xero/
├── manifest.json              # Module metadata (name, icon, tabs)
├── tools/
│   ├── xero_invoices.json     # Tool definitions
│   ├── xero_contacts.json
│   └── xero_reports.json
├── implementations/
│   └── xero_wrapper.py        # Tool implementations
└── ui/
    └── xero.html              # Optional UI components
```

**Tool Categories:**
- **Quote Calculator** (80 tools) - Business cards, flyers, books, pricing
- **Xero Accounting** (25 tools) - Invoices, contacts, reports, bank transactions
- **Shopify** (15 tools) - Products, orders, inventory
- **Google Workspace** (20 tools) - Drive, Docs, Sheets, Gmail, Calendar
- **Microsoft 365** (18 tools) - OneDrive, Outlook, Word, Excel
- **InHouse Print** (12 tools) - Fred database queries, production workflow
- **Stock Management** (10 tools) - Inventory tracking, reorder alerts
- **[15+ more modules]** - GitHub, Salesforce, CAD, VSA alerts, etc.

### 3. Frontend Architecture (`UI/`)

**Purpose:** Single-page application with modular plugin system

**Main File: `business-ai-platform-v2.html`** (~15,000 lines)

**Structure:**
```html
<!DOCTYPE html>
<html>
<head>
    <!-- Styles: ~3,000 lines CSS -->
    <style>/* Custom CSS framework */</style>
</head>
<body>
    <!-- HTML Structure: ~2,000 lines -->
    <div id="app-container">
        <!-- Left Sidebar: Thread list, Synergy board -->
        <!-- Center: Prime AI / Multi-Agent columns -->
        <!-- Right Sidebar: Dynamic modules -->
    </div>
    
    <!-- JavaScript: ~10,000 lines -->
    <script>
        // Core Classes
        class AppState { /* Global state manager */ }
        class ThreadManager { /* Thread lifecycle */ }
        class MultiAgent { /* Agent orchestration */ }
        class MessageStore { /* Message persistence */ }
        class ModuleLoader { /* Plugin system */ }
        
        // Module Integration
        const moduleRegistry = {
            'quote-calculator': QuoteCalculatorModule,
            'communication-hub': CommunicationHubModule,
            'synergy': SynergyModule,
            // ... 20+ modules
        };
    </script>
</body>
</html>
```

**Key JavaScript Classes:**

**`ThreadManager`**
- Create, load, save, delete threads
- Sync thread locations (Prime, Agent-1, Agent-2, etc.)
- Thread metadata (title, tags, workflow links)
- Database synchronization

**`MultiAgent`**
- Manage 26 parallel agent columns (Alpha-1 → Zulu-26)
- Drag-and-drop thread assignment
- Column collapse/expand state
- Width toggle (400px ⇄ 600px)

**`MessageStore`**
- Centralized message storage
- Real-time updates via WebSocket
- Markdown rendering with code highlighting
- Tool result bubbles

**`ModuleLoader`**
- Dynamic ES6 module loading
- Manifest parsing (`manifest.json`)
- Sidebar registration
- Tab management

**Module Types:**

**Internal Modules (`modules_internal/`)** - Core platform features:
- `agents/` - Multi-agent system
- `communication-hub/` - Email/SMS integration
- `synergy/` - Kanban project board
- `automation-workflows/` - Visual workflow canvas
- `thread-manager/` - Thread operations
- `settings-sidebar/` - User preferences
- `universal-search/` - Semantic search across all data

**External Modules (`modules_external/`)** - Client-specific plugins:
- Each module has `manifest.json` defining:
  - `id` - Unique identifier
  - `name` - Display name
  - `icon` - Font Awesome icon
  - `color` - Brand color
  - `tabs` - Sub-sections within module
  - `tools` - Enabled/disabled tool list

**Example Module Manifest:**
```json
{
  "id": "quote-calculator",
  "name": "Quote Calculator",
  "version": "1.0.0",
  "icon": "fas fa-calculator",
  "color": "#ffb347",
  "tabs": [
    {"id": "business-cards", "name": "Business Cards", "default": true},
    {"id": "flyers", "name": "Flyers"},
    {"id": "query-library", "name": "Query Library"}
  ],
  "tools": {
    "enabled": true,
    "count": 80
  }
}
```

### 4. Database Architecture (Supabase PostgreSQL)

**Four Schema System:**

#### **1. `ai_infrastructure` Schema** (19 tables)
**Purpose:** User management, authentication, credentials, automation

| Table | Purpose | Key Fields |
|-------|---------|------------|
| `users` | User accounts | email, password_hash, role |
| `user_sessions` | Active login sessions | token, user_id, expires_at |
| `oauth_tokens` | Google/Microsoft tokens | platform, access_token, refresh_token |
| `user_platform_credentials` | API credentials storage | platform, connection_string, encrypted |
| `user_preferences` | User settings | theme, agent_slug, default_ai_model |
| `prompt_library` | Saved prompts | title, content, category |
| `device_registry` | Multi-device management | device_id, user_id, locked_threads |
| `automation_executions` | Workflow run history | automation_id, status, output |
| `workspaces` | Team workspaces | name, owner_id |
| `workspace_users` | Team membership | workspace_id, user_id, role |

#### **2. `sessions` Schema** (9 tables)
**Purpose:** Thread management, messages, conversation storage

| Table | Purpose | Key Fields |
|-------|---------|------------|
| `threads` | Conversation threads | title, user_id, agent, synergy_card_id, workflow_slug |
| `messages` | Chat messages | thread_id, role, content, tool_results |
| `thread_assignments` | Thread locations | thread_id, location (prime/agent-1/etc.) |
| `thread_shares` | Shared threads | thread_id, shared_with_user_id, permission |
| `saved_threads` | Archived threads | thread_data JSON |

**Key Relationships:**
- `threads.user_id` → `ai_infrastructure.users.id`
- `threads.synergy_card_id` → `synergy_sessions.synergy_sessions.id` (soft FK)
- `threads.workflow_slug` → `public.visual_automations.slug` (soft FK)

#### **3. `synergy_sessions` Schema** (2 tables)
**Purpose:** Kanban project management

| Table | Purpose | Key Fields |
|-------|---------|------------|
| `synergy_sessions` | Kanban cards | title, description, priority, milestone, tags |
| `synergy_internal_docs` | Rich-text documents | content, card_id |

**Bidirectional Linking:**
- Thread → Synergy: `threads.synergy_card_id`
- Synergy → Thread: `synergy_sessions.linked_thread_ids` (JSON array)

#### **4. `public` Schema** (7 tables)
**Purpose:** Visual automation workflows

| Table | Purpose | Key Fields |
|-------|---------|------------|
| `visual_automations` | Canvas workflows | slug, name, definition JSON |
| `automation_workflows` | Legacy workflows | id, steps JSON |
| `workflow_executions` | Execution history | workflow_id, status, output |
| `workflow_schedules` | Cron schedules | workflow_id, cron_expression |

**Connection Pooling Configuration:**
```python
# Supabase PgBouncer Settings
POOL_MODE = 'transaction'  # Best for Flask/serverless
MAX_CLIENT_CONN = 20       # Max concurrent Flask connections
DEFAULT_POOL_SIZE = 5      # Connections per database
```

---

## 🔄 Data Flow Examples

### Example 1: User Sends Message to AI Agent

```
1. USER ACTION
   └── Frontend: User types message in Prime panel
       └── JavaScript: ThreadManager.sendMessage()

2. HTTP REQUEST
   └── POST /api/agent/prime/start
       └── Body: {thread_id: 2112, message: "Calculate quote for 1000 business cards"}

3. FLASK BACKEND
   └── routes/agent_routes_v4.py
       ├── Authenticate user (JWT token)
       ├── Save message to sessions.messages
       ├── Build context (thread history + system prompt + tools)
       └── Stream to AI (Anthropic Claude API)

4. AI RESPONSE STREAMING
   └── Server-Sent Events (SSE)
       ├── thinking_start: AI begins reasoning
       ├── thinking_content: Claude's internal thoughts
       ├── thinking_end: Reasoning complete
       ├── tool_use_start: AI calls quote_calculator tool
       ├── tool_result: Tool execution result
       └── text_content: AI's final response

5. TOOL EXECUTION
   └── tools/registry_v3.py
       ├── Find tool: "calculate_business_card_quote"
       ├── Load implementation: quote-calculator/implementations/calculator_wrapper.py
       ├── Inject credentials: user_id from session
       ├── Execute: calculate_quote(quantity=1000, stock="satin_350gsm")
       └── Return: {price: $285, breakdown: {...}}

6. DATABASE SAVE
   └── shared/database_utils.py
       ├── INSERT INTO sessions.messages (role='assistant', content='...')
       ├── UPDATE sessions.threads SET updated_at=NOW()
       └── COMMIT transaction

7. FRONTEND UPDATE
   └── WebSocket: Real-time message bubbles
       ├── MessageStore.addMessage()
       ├── Render markdown with syntax highlighting
       ├── Show tool result bubble
       └── Update thread card timestamp
```

### Example 2: Drag Thread to Agent Column

```
1. USER ACTION
   └── Frontend: Drag thread card from sidebar to Agent-3 column
       └── Event: dragend → ThreadManager.dropToAgent()

2. DATABASE UPDATE
   └── POST /api/thread/assignments
       ├── DELETE FROM ai_infrastructure.thread_assignments WHERE thread_id=2112
       ├── INSERT INTO ai_infrastructure.thread_assignments (thread_id, location) 
       │   VALUES (2112, 'agent-3')
       └── UPDATE sessions.threads SET agent='agent-3' WHERE id=2112

3. LOCAL STORAGE SYNC
   └── JavaScript: localStorage.setItem('thread_assignments', {...})
       └── Ensures thread location persists across browser sessions

4. UI UPDATE
   └── ThreadManager.loadThreadInAgent('agent-3', 2112)
       ├── Fetch thread data from database
       ├── Fetch message history
       ├── Render messages in Agent-3 column
       └── Remove thread from Prime panel (if applicable)

5. REALTIME SYNC (if multi-device)
   └── WebSocket: Broadcast thread_assignment_changed event
       └── Other open tabs/devices update their UI
```

### Example 3: Module Plugin Loads

```
1. PAGE LOAD
   └── Frontend: business-ai-platform-v2.html loads
       └── ModuleLoader.initialize()

2. DISCOVER MODULES
   └── Read: UI/modules_external/manifest.json
       ├── 25+ modules listed
       └── Filter: enabled: true

3. LOAD MODULE MANIFESTS
   └── For each module:
       ├── Fetch: UI/modules_external/quote-calculator/manifest.json
       ├── Parse: {id, name, icon, color, tabs, tools}
       └── Register in moduleRegistry

4. LOAD MODULE SCRIPTS
   └── Dynamic import:
       ├── import('./modules_external/quote-calculator/quote-calculator.js')
       ├── Instantiate: new QuoteCalculatorModule()
       └── Call: module.initialize()

5. REGISTER SIDEBARS
   └── For each module with UI:
       ├── Create sidebar button (icon + color)
       ├── Attach click handler
       └── Load HTML: modules_external/quote-calculator/quote-calculator.html

6. REGISTER TOOLS
   └── Backend: tools/registry_v3.py
       ├── Scan: UI/modules_external/quote-calculator/tools/*.json
       ├── Load: 80 tool definitions
       ├── Load implementations: implementations/calculator_wrapper.py
       └── Cache in Redis (1 hour TTL)
```

---

## 🚀 Deployment Architecture

### Development Environment

**Local Setup:**
```bash
# .env file
USE_SUPABASE=false
DATABASE_PATH=data/ai_infrastructure.db  # SQLite fallback
```

**Run Locally:**
```powershell
cd AI_infrastructure
python flask_app.py  # Runs on http://localhost:5001
```

**Database:** Local SQLite files in `data/` folder

### Production Environment (Render.com)

**Branch:** `v10` (auto-deploys on push)

**Build Process:**
```
1. GitHub Push → v10 branch
2. GitHub Actions → Build Docker image
3. Push to GitHub Container Registry (GHCR)
4. Render detects new commit
5. Pull Docker image from GHCR
6. Deploy to Render service
7. Health check: /health endpoint
8. Live in ~3-5 minutes
```

**Docker Multi-Stage Build:**
```dockerfile
FROM python:3.11-slim

# Layer 1: System dependencies (CACHED)
RUN apt-get install build-essential libpq-dev ...

# Layer 2: Python dependencies (CACHED if requirements.txt unchanged)
COPY requirements.txt .
RUN pip install -r requirements.txt

# Layer 3: Node.js dependencies (CACHED if package.json unchanged)
COPY package.json .
RUN npm install

# Layer 4: Application code (REBUILT EVERY TIME)
COPY . .
```

**Optimization Results:**
- **Before:** 30-minute builds (re-downloading everything)
- **After:** 5-10 minute builds (layer caching)

**Environment Variables (Render Dashboard):**
```bash
# AI Providers
ANTHROPIC_API_KEY=sk-ant-...
OPENAI_API_KEY=sk-...
DEEPSEEK_API_KEY_1=sk-...

# Database
USE_SUPABASE=true
SUPABASE_URL=https://project.supabase.co
SUPABASE_SERVICE_KEY=eyJ...
SUPABASE_DB_URL_POOLER=postgresql://postgres:password@pooler:6543/postgres

# OAuth
MICROSOFT_CLIENT_ID=...
MICROSOFT_CLIENT_SECRET=...
GOOGLE_OAUTH_CLIENT_ID=...
GOOGLE_OAUTH_CLIENT_SECRET=...
FRONTEND_URL=https://ai-agents-v10.onrender.com  # OAuth redirect base

# Security
SECRET_KEY=<hex-generated-secret>
```

**Persistent Storage:**
```
/data/  # 10GB Render persistent disk
├── logs/
├── uploads/
└── cache/
```

**Resource Allocation:**
- **Plan:** Starter ($7/month)
- **CPU:** Shared
- **RAM:** 512 MB
- **Disk:** 10 GB persistent
- **Region:** Singapore (ap-southeast-1)

---

## 🔐 Client Deployment Process

### Prerequisites for New Client

**1. GitHub Account Setup**
- Create new GitHub organization (e.g., `clientname-print`)
- Fork `gerardovsa/AI_agents` repository
- Set default branch to `v10`

**2. Render Account Setup**
- Create Render account (clientname@company.com)
- Connect GitHub organization
- Enable Docker deployment

**3. Supabase Account Setup**
- Create Supabase project (Region: Singapore)
- Note: Project URL, Anon key, Service key, DB URL
- Enable PgBouncer connection pooling

**4. API Keys Required**
- **Anthropic:** Claude API key (primary AI)
- **OpenAI:** GPT API key (secondary AI + embeddings)
- **Google OAuth:** Client ID + Secret (Google Workspace)
- **Microsoft OAuth:** Client ID + Secret (Microsoft 365)
- **Xero:** Credentials stored in database (no env vars)
- **Shopify:** API key + secret (per store)
- **InHouse Print:** SQL Server connection strings (in database)

### Deployment Steps

#### Step 1: Fork Repository (5 min)

```bash
# On GitHub
1. Go to https://github.com/gerardovsa/AI_agents
2. Click "Fork" → Create in client's organization
3. Set default branch to "v10"
4. Clone to client's GitHub Actions
```

#### Step 2: Configure Render Service (10 min)

**Create New Web Service:**
```yaml
# Render Dashboard → New → Web Service
Name: clientname-ai-agents
Repository: clientname-print/AI_agents
Branch: v10
Runtime: Docker
Region: Singapore
Plan: Starter ($7/month)

# Build Settings (auto-detected from render.yaml)
Build Command: docker build -t ai-agents .
Start Command: ./startup.sh

# Persistent Disk
Name: ai-agents-data
Mount Path: /data
Size: 10 GB
```

**Add Environment Variables:**
```bash
# Copy from .env.example
# Add manually in Render dashboard (Settings → Environment)

ANTHROPIC_API_KEY=<client-claude-key>
OPENAI_API_KEY=<client-gpt-key>
SUPABASE_URL=<client-supabase-url>
SUPABASE_SERVICE_KEY=<client-supabase-key>
SUPABASE_DB_URL_POOLER=<client-db-url>
MICROSOFT_CLIENT_ID=<client-azure-app-id>
MICROSOFT_CLIENT_SECRET=<client-azure-secret>
GOOGLE_OAUTH_CLIENT_ID=<client-google-client-id>
GOOGLE_OAUTH_CLIENT_SECRET=<client-google-secret>
FRONTEND_URL=https://clientname-ai-agents.onrender.com
SECRET_KEY=<generate-with-python-secrets>
```

#### Step 3: Initialize Supabase Database (15 min)

**Run Migration Scripts:**
```sql
-- Connect to Supabase SQL Editor

-- 1. Create schemas
CREATE SCHEMA IF NOT EXISTS ai_infrastructure;
CREATE SCHEMA IF NOT EXISTS sessions;
CREATE SCHEMA IF NOT EXISTS synergy_sessions;

-- 2. Run migrations in order
-- Execute all files in AI_infrastructure/migrations/ folder
-- (001_create_users.sql → 020_latest_migration.sql)

-- 3. Create admin user
INSERT INTO ai_infrastructure.users (email, password_hash, role)
VALUES ('admin@clientname.com', '<bcrypt-hash>', 'admin');

-- 4. Verify schemas
SELECT schema_name FROM information_schema.schemata
WHERE schema_name IN ('ai_infrastructure', 'sessions', 'synergy_sessions');
-- Should return 3 rows
```

#### Step 4: Configure OAuth Redirects (10 min)

**Google Cloud Console:**
```
1. Go to https://console.cloud.google.com
2. Create new project: "ClientName AI Platform"
3. Enable APIs: Drive, Docs, Sheets, Gmail, Calendar
4. Create OAuth 2.0 Client ID (Web application)
5. Authorized redirect URIs:
   - https://clientname-ai-agents.onrender.com/api/auth/google/callback
   - https://clientname-ai-agents.onrender.com/oauth2callback
6. Copy Client ID + Secret to Render environment variables
```

**Microsoft Azure Portal:**
```
1. Go to https://portal.azure.com
2. Azure Active Directory → App registrations → New registration
3. Name: "ClientName AI Platform"
4. Supported account types: Accounts in any organizational directory
5. Redirect URI (Web):
   - https://clientname-ai-agents.onrender.com/api/auth/microsoft/callback
6. API Permissions:
   - Microsoft Graph: User.Read, Files.ReadWrite.All, Mail.Read, Mail.Send
7. Copy Application ID + Secret to Render environment variables
```

#### Step 5: Configure Client-Specific Modules (20 min)

**Enable/Disable Modules:**
```json
// Edit: UI/modules_external/manifest.json
{
  "modules": [
    {"id": "quote-calculator", "enabled": true},   // Always enabled for InHouse Print
    {"id": "xero", "enabled": true},               // If client uses Xero
    {"id": "shopify", "enabled": false},           // If client doesn't use Shopify
    {"id": "stock-management", "enabled": true},
    {"id": "inhouse-kanban", "enabled": true},
    // ... customize per client
  ]
}
```

**Add Client Credentials to Database:**
```sql
-- Xero credentials
INSERT INTO ai_infrastructure.user_platform_credentials 
(user_id, platform, client_id, client_secret, tenant_id, scopes)
VALUES 
(1, 'xero_print', '<client-xero-id>', '<client-xero-secret>', '<tenant>', 'accounting.transactions');

-- InHouse Print SQL Server
INSERT INTO ai_infrastructure.user_platform_credentials 
(user_id, platform, connection_string)
VALUES 
(1, 'inhouse_print', 'Server=client-sql.com;Database=Fred;UID=user;PWD=pass');
```

#### Step 6: Deploy & Test (15 min)

**Trigger Deployment:**
```bash
# Push commit to trigger deployment
git add .
git commit -m "Configure for ClientName deployment"
git push origin v10

# Monitor deployment in Render dashboard
# Wait for "Live" status (~3-5 minutes)
```

**Verify Deployment:**
```bash
# 1. Health check
curl https://clientname-ai-agents.onrender.com/health
# Should return: {"status": "ok", "database": "connected"}

# 2. Test login
# Go to: https://clientname-ai-agents.onrender.com
# Login with admin@clientname.com

# 3. Test AI conversation
# Create new thread → Send message → Verify AI response

# 4. Test tool execution
# Ask AI: "Get my Xero invoices from last month"
# Verify tool executes and returns data

# 5. Test OAuth
# Settings → Connect Google Drive
# Verify OAuth flow completes
```

### Post-Deployment Configuration

**1. Create Additional Users**
```sql
INSERT INTO ai_infrastructure.users (email, password_hash, role)
VALUES 
('user1@clientname.com', '<bcrypt-hash>', 'user'),
('user2@clientname.com', '<bcrypt-hash>', 'user');
```

**2. Configure User Preferences**
```sql
INSERT INTO ai_infrastructure.user_preferences (user_id, theme, default_ai_model)
VALUES 
(2, 'dark', 'claude-3-5-sonnet'),
(3, 'light', 'gpt-4');
```

**3. Set Up Automation Schedules** (Optional)
```sql
INSERT INTO public.workflow_schedules (workflow_id, cron_expression, enabled)
VALUES 
('<workflow-id>', '0 9 * * 1', true);  -- Every Monday at 9am
```

**4. Monitor Logs**
```bash
# Render Dashboard → Logs tab
# Watch for:
# - Connection pool stats
# - Tool execution logs
# - OAuth token refreshes
# - Database query performance
```

---

## 🔑 Key Architectural Patterns

### 1. **Modular Plugin Architecture**

**Pattern:** External modules as self-contained plugins

**Implementation:**
```
Module Structure:
UI/modules_external/[module-name]/
├── manifest.json          # Metadata (icon, color, tabs)
├── tools/                 # Tool definitions (JSON)
├── implementations/       # Tool code (Python)
├── ui/                    # Frontend components (HTML/JS/CSS)
└── docs/                  # Documentation

Registry loads modules at startup:
1. Scan UI/modules_external/ for manifest.json files
2. Load tool definitions from tools/*.json
3. Import implementations from implementations/*.py
4. Register in tool_executor decorator system
```

**Benefits:**
- **Plug-and-play:** Enable/disable modules per client
- **Isolated:** Module bugs don't affect core platform
- **Versioned:** Each module has independent version
- **Maintainable:** Developers work on one module at a time

### 2. **Database Connection Pooling**

**Pattern:** Single interface for all database operations

**Implementation:**
```python
# ALL code uses this single function
from AI_infrastructure.shared.database_utils import execute_query

# Read operation
rows = execute_query(
    "SELECT * FROM sessions.threads WHERE user_id=%s",
    (user_id,),
    fetch_mode='all'  # or 'one', 'value'
)

# Write operation (auto-uses transaction mode)
execute_query(
    "INSERT INTO sessions.messages (thread_id, role, content) VALUES (%s, %s, %s)",
    (thread_id, 'user', message)
)

# Schema operations (with error handling)
try:
    execute_query("CREATE SCHEMA IF NOT EXISTS customer_schema")
except Exception as e:
    # Rollback happens automatically
    logger.error(f"Schema creation failed: {e}")
```

**Benefits:**
- **Consistent:** All DB operations use same interface
- **Safe:** Automatic rollback on errors
- **Performant:** Connection pooling (PgBouncer)
- **Maintainable:** Single place to add logging, caching

### 3. **Credential Injection System**

**Pattern:** Automatic credential injection into tool calls

**Implementation:**
```python
# Tool definition has NO credential parameters
@tool_executor()
def xero_get_invoices(status: str = None):
    """Get Xero invoices for current user."""
    
    # Credentials auto-injected by registry
    user_id = kwargs.get('_user_id')  # From JWT token
    credentials = kwargs.get('_injected_credentials')  # From database
    
    # Use credentials to call API
    api = XeroAPI(credentials['client_id'], credentials['client_secret'])
    return api.get_invoices(status)
```

**Flow:**
```
1. AI calls tool: execute_tool('xero_get_invoices', status='PAID')
2. Registry intercepts call
3. Registry fetches credentials from database:
   SELECT * FROM ai_infrastructure.user_platform_credentials 
   WHERE user_id=14 AND platform='xero'
4. Registry injects credentials:
   execute_tool('xero_get_invoices', status='PAID', 
                _user_id=14, _injected_credentials={...})
5. Tool receives credentials automatically
```

**Benefits:**
- **Security:** Credentials never exposed to AI
- **Multi-tenant:** Each user has own credentials
- **Maintainable:** Tools don't handle credential fetching
- **Auditable:** All credential access logged

### 4. **Real-Time Streaming Architecture**

**Pattern:** Server-Sent Events (SSE) for AI responses

**Implementation:**
```python
# Backend: routes/agent_routes_v4.py
@agent_bp.route('/stream/<agent_id>', methods=['GET'])
def stream_agent(agent_id):
    """Stream AI responses as they generate."""
    
    def generate():
        # Stream AI response chunks
        for chunk in ai_client.stream(messages, tools):
            if chunk['type'] == 'thinking':
                yield f"event: thinking_content\ndata: {chunk['content']}\n\n"
            elif chunk['type'] == 'tool_use':
                result = execute_tool(chunk['name'], chunk['input'])
                yield f"event: tool_result\ndata: {json.dumps(result)}\n\n"
            elif chunk['type'] == 'text':
                yield f"event: text_content\ndata: {chunk['content']}\n\n"
    
    return Response(generate(), mimetype='text/event-stream')
```

```javascript
// Frontend: business-ai-platform-v2.html
const eventSource = new EventSource('/api/stream/prime');

eventSource.addEventListener('thinking_content', (e) => {
    appendThinkingBlock(e.data);
});

eventSource.addEventListener('tool_result', (e) => {
    const result = JSON.parse(e.data);
    renderToolBubble(result);
});

eventSource.addEventListener('text_content', (e) => {
    appendTextToMessage(e.data);
});
```

**Benefits:**
- **Real-time:** User sees AI thinking in real-time
- **Non-blocking:** UI remains responsive during generation
- **Resumable:** Can reconnect if connection drops
- **Efficient:** HTTP/1.1 persistent connection

---

## 🔍 Common Development Scenarios

### Scenario 1: Add New External Module

**Goal:** Create "Stripe Payments" module with 5 tools

**Steps:**

1. **Create module folder structure:**
```bash
mkdir -p UI/modules_external/stripe
cd UI/modules_external/stripe
```

2. **Create manifest.json:**
```json
{
  "id": "stripe",
  "name": "Stripe Payments",
  "version": "1.0.0",
  "icon": "fab fa-stripe",
  "color": "#635bff",
  "tabs": [
    {"id": "customers", "name": "Customers", "default": true},
    {"id": "payments", "name": "Payments"}
  ],
  "tools": {"enabled": true}
}
```

3. **Create tool definitions:**
```bash
mkdir tools
# Create: tools/stripe_customers.json
# Create: tools/stripe_payments.json
```

4. **Create implementations:**
```bash
mkdir implementations
# Create: implementations/stripe_wrapper.py
```

5. **Register in main manifest:**
```json
// Edit: UI/modules_external/manifest.json
{
  "modules": [
    // ... existing modules
    {
      "id": "stripe",
      "name": "Stripe Payments",
      "manifestPath": "external/modules/stripe/manifest.json",
      "enabled": true
    }
  ]
}
```

6. **Restart Flask server:**
```bash
# Registry auto-discovers new module
# 5 tools loaded from stripe/tools/*.json
```

### Scenario 2: Deploy to New Client

**Goal:** Deploy AI platform to "ABC Printing" on their Render account

**Checklist:**

- [ ] **GitHub:** Fork repo to `abc-printing` organization
- [ ] **Render:** Create service connected to `abc-printing/AI_agents`
- [ ] **Supabase:** Create project in Singapore region
- [ ] **Environment Variables:** Add 15+ required vars to Render
- [ ] **Database:** Run migrations (20 SQL files)
- [ ] **OAuth:** Configure Google + Microsoft redirect URLs
- [ ] **Credentials:** Add Xero, InHouse Print DB credentials
- [ ] **Modules:** Customize manifest.json for ABC's needs
- [ ] **Test:** Verify login, AI chat, tool execution
- [ ] **Users:** Create accounts for ABC staff

**Time Estimate:** 1-2 hours for experienced developer

### Scenario 3: Debug Production Issue

**Goal:** User reports "502 Bad Gateway" error

**Debugging Steps:**

1. **Check Render logs:**
```bash
# Render Dashboard → Service → Logs
# Look for:
# - Connection pool exhaustion
# - Database query timeouts
# - Uncaught exceptions
```

2. **Check database connections:**
```sql
-- Supabase Dashboard → SQL Editor
SELECT count(*) as active_connections
FROM pg_stat_activity
WHERE datname = 'postgres';
-- Should be < 20 (connection pool max)
```

3. **Check health endpoint:**
```bash
curl https://abc-printing.onrender.com/health
# {"status": "ok"} = healthy
# {"status": "error"} = problem
```

4. **Common fixes:**
- **Connection leak:** Route missing `conn.close()` or context manager
- **Pool exhaustion:** Too many concurrent requests
- **Long-running query:** Add `SET statement_timeout = '30s'`
- **OAuth token expired:** Manual token refresh needed

---

## 📈 Performance Optimizations

### 1. **Docker Layer Caching**
- **Before:** 30-minute builds
- **After:** 5-10 minute builds
- **Method:** Multi-stage Dockerfile with dependency layers cached

### 2. **Redis Tool Caching**
- **Before:** 3-second registry load (200+ tools)
- **After:** 0.06-second cache hit (50x faster)
- **Method:** Cache tool schemas + implementations in Redis (1-hour TTL)

### 3. **Database Connection Pooling**
- **Before:** New connection per request (slow)
- **After:** Reuse connections from pool
- **Method:** PgBouncer transaction mode + psycopg2 pools

### 4. **Lazy Module Loading**
- **Before:** Load all 25+ modules on page load
- **After:** Load modules when user clicks sidebar
- **Method:** Dynamic ES6 `import()` on demand

---

## 🔒 Security Measures

### 1. **Authentication**
- **JWT tokens** (24-hour expiry)
- **bcrypt password hashing** (cost factor 12)
- **Session tokens** in database (revocable)

### 2. **Authorization**
- **Row-level security:** Users only see their threads
- **Platform credentials:** Encrypted in database
- **Tool filtering:** Only tools user has credentials for

### 3. **Input Validation**
- **SQL parameterization:** All queries use `%s` placeholders
- **Tool parameter validation:** JSON schema enforcement
- **File upload restrictions:** Whitelist allowed extensions

### 4. **OAuth Security**
- **State parameter:** CSRF protection
- **Token refresh:** Automatic before expiry
- **Scope limitation:** Request minimum required permissions

---

## 📝 Key Documentation Files

**Architecture & Design:**
- `ARCHITECTURE.md` - This file
- `COMPLETE_DATABASE_ARCHITECTURE.md` - Database schema reference
- `DATABASE_SCHEMA_RELATIONSHIPS.md` - Table relationships
- `README.md` - Project overview

**Module Documentation:**
- `UI/modules_external/quote-calculator/README.md` - Quote calculator guide
- `UI/modules_external/xero/README.md` - Xero integration guide
- `INHOUSE_TOOLS_COMPLETE_FIX_JAN13_2026.md` - InHouse Print tools

**Deployment:**
- `DEPLOYMENT_CHECKLIST.md` - Deployment steps
- `RENDER_DEPLOYMENT_GUIDE.md` - Render.com setup
- `SUPABASE_SETUP_COMPLETE.md` - Database initialization

**Development:**
- `.github/copilot-instructions.md` - AI assistant context
- `TOOL_CONSTRUCTION_PROCESS.md` - How to build tools
- `MODULE_SYSTEM_ARCHITECTURE_COMPLETE.md` - Plugin system

---

## 🚨 Known Issues & Limitations

### Current Limitations

1. **Single-region deployment:** Singapore only (high latency for US/EU)
   - **Workaround:** Deploy separate instance in US-East or EU-West

2. **Connection pool limit:** 20 max concurrent connections
   - **Workaround:** Upgrade Supabase plan or implement queue system

3. **File upload size:** 10 MB limit (Render free tier)
   - **Workaround:** Upgrade to paid plan or use external storage (S3)

4. **AI rate limits:** Claude API throttles after 100 requests/minute
   - **Workaround:** Implement request queue or use multiple API keys

5. **No built-in user registration:** Admin must create accounts
   - **Future:** Add self-service registration with email verification

### Technical Debt

1. **Mixed localStorage + database:** Thread assignments stored in both
   - **Plan:** Migrate to database-only with WebSocket sync

2. **Duplicate code:** Some tools have similar implementations
   - **Plan:** Create shared utility library

3. **Large HTML file:** 15,000-line SPA needs refactoring
   - **Plan:** Split into multiple files with build step

4. **SQLite fallback:** Rarely used, adds complexity
   - **Plan:** Remove SQLite support, Supabase-only

---

## 🎓 Learning Resources

### For New Developers

**Start Here:**
1. Read `README.md` - Project overview
2. Read `ARCHITECTURE.md` - This file
3. Explore `UI/modules_external/quote-calculator/` - Example module
4. Review `tools/registry_v3.py` - Tool system core

**Key Concepts to Understand:**
- Flask blueprints and route registration
- PostgreSQL schema separation (ai_infrastructure vs sessions)
- Tool executor decorator pattern
- WebSocket streaming with SSE
- Module manifest.json structure

**Common Tasks:**
- Add new tool: See `TOOL_CONSTRUCTION_PROCESS.md`
- Add new module: See `MODULE_SYSTEM_ARCHITECTURE_COMPLETE.md`
- Fix database issue: See `COMPLETE_DATABASE_ARCHITECTURE.md`
- Debug deployment: See `DEPLOYMENT_CHECKLIST.md`

---

## 📞 Support & Contact

**For Deployment Issues:**
- Check Render logs first
- Review `DEPLOYMENT_CHECKLIST.md`
- Contact: gerardo@valorstudio.com.au

**For Module Development:**
- Review existing modules in `UI/modules_external/`
- See `TOOL_CONSTRUCTION_PROCESS.md`
- Test locally before deploying

**For Database Issues:**
- Check Supabase dashboard query logs
- Review `COMPLETE_DATABASE_ARCHITECTURE.md`
- Verify connection pool status

---

## 🗺️ Future Roadmap

### Short-Term (Q1 2026)

- [ ] **Multi-region deployment** - US-East + EU-West instances
- [ ] **Self-service registration** - Email verification flow
- [ ] **Admin dashboard** - User management UI
- [ ] **Module marketplace** - Community-contributed modules
- [ ] **Improved caching** - Redis for thread metadata

### Medium-Term (Q2 2026)

- [ ] **Mobile app** - React Native iOS/Android
- [ ] **API Gateway** - RESTful API for third-party integrations
- [ ] **Webhook system** - Push notifications to external systems
- [ ] **Advanced analytics** - Usage tracking, cost per user
- [ ] **Multi-language support** - i18n framework

### Long-Term (Q3-Q4 2026)

- [ ] **On-premise deployment** - Docker Compose for enterprise
- [ ] **SAML/SSO integration** - Enterprise authentication
- [ ] **Compliance certifications** - SOC 2, ISO 27001
- [ ] **Advanced AI features** - Fine-tuned models per client
- [ ] **Real-time collaboration** - Multi-user threads

---

**Last Updated:** January 14, 2026  
**Document Version:** 1.0  
**Maintained By:** Valor Studio AI Development Team

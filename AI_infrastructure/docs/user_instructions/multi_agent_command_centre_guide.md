# Multi-Agent Command Centre - Complete User Guide

**Version:** 1.0  
**Last Updated:** November 22, 2025  
**Audience:** End Users, Power Users, Project Managers, AI Agents

---

## Table of Contents

1. [What is the Multi-Agent Command Centre?](#what-is-the-multi-agent-command-centre)
2. [Getting Started](#getting-started)
3. [Understanding the 26 NATO Agents](#understanding-the-26-nato-agents)
4. [Working with Agent Columns](#working-with-agent-columns)
5. [Distributing Work Across Agents](#distributing-work-across-agents)
6. [Cross-Agent Communication](#cross-agent-communication)
7. [Advanced Coordination Patterns](#advanced-coordination-patterns)
8. [Real-World Use Case Scenarios](#real-world-use-case-scenarios)
9. [Best Practices](#best-practices)
10. [Frequently Asked Questions](#frequently-asked-questions)
11. [AI Agent Instructions](#ai-agent-instructions)

---

## What is the Multi-Agent Command Centre?

The **Multi-Agent Command Centre** is a powerful project orchestration system that allows you to **distribute complex work across up to 26 specialized AI agents** working in parallel. Think of it as your **AI project management headquarters** where you can coordinate multiple AI assistants, each handling different parts of a larger project.

### Key Concepts

**🎯 Command Centre Philosophy:**
- **One human orchestrator** (you)
- **26 AI specialists** (Alpha through Zulu)
- **Parallel execution** (agents work simultaneously)
- **Centralized coordination** (you oversee everything)
- **Resource sharing** (workflows, docs, and project data)

### Visual Architecture

```
┌────────────────────────────────────────────────────────────────┐
│                  MULTI-AGENT COMMAND CENTRE                    │
├────────────────────────────────────────────────────────────────┤
│                                                                │
│  ┌──────┐  ┌──────┐  ┌──────┐  ┌──────┐  ┌──────┐  ┌──────┐ │
│  │Alpha │  │Bravo │  │Charlie│ │Delta │  │Echo  │  │...   │ │
│  │      │  │      │  │      │  │      │  │      │  │      │ │
│  │🏗️ UI │  │🗄️ DB │  │🔧 API│  │🧪Test│  │📄Doc │  │      │ │
│  │      │  │      │  │      │  │      │  │      │  │      │ │
│  │ [💬] │  │ [💬] │  │ [💬] │  │ [💬] │  │ [💬] │  │ [💬] │ │
│  └──────┘  └──────┘  └──────┘  └──────┘  └──────┘  └──────┘ │
│     ↓         ↓         ↓         ↓         ↓         ↓      │
│     └─────────┴─────────┴─────────┴─────────┴─────────┘      │
│                         ↓                                     │
│              ┌─────────────────────┐                         │
│              │  YOU (Orchestrator)  │                         │
│              │  🎯 Assign Work      │                         │
│              │  📊 Monitor Progress │                         │
│              │  🔗 Coordinate Agents│                         │
│              └─────────────────────┘                         │
└────────────────────────────────────────────────────────────────┘
```

### Why Use Multi-Agent Coordination?

**❌ WITHOUT Multi-Agent Command Centre:**
```
Day 1: "Build e-commerce platform with frontend, backend, and database"
        ↓
AI Agent: "That's a massive project. Let me work on the frontend first..."
        ↓
Day 2: Frontend half-done
        ↓
Day 3: Starting backend (frontend incomplete)
        ↓
Day 4: Database design (backend incomplete)
        ↓
Result: Sequential work, long timeline, context switching issues
```

**✅ WITH Multi-Agent Command Centre:**
```
Hour 1: Distribute work to 3 agents
        ↓
Alpha → Frontend (React, UI components)
Bravo → Backend (Node.js API, auth)
Charlie → Database (Schema design, migrations)
        ↓
Hour 3: All three working in PARALLEL
        ↓
Hour 6: Components ready for integration
        ↓
Result: 3x faster, specialized focus, no context switching
```

### Core Features

| Feature | Description | Benefit |
|---------|-------------|---------|
| **26 NATO Agents** | Alpha through Zulu specialist agents | Massive parallelization |
| **Work Distribution** | Assign tasks with one command | Instant delegation |
| **Resource Linking** | Attach workflows, docs, Synergy cards | Shared context |
| **Cross-Agent Messaging** | Agents request updates from each other | Autonomous coordination |
| **UI Automation** | Automatic tab switching, column opening | Zero manual setup |
| **Thread Isolation** | Each agent has independent conversation | No context mixing |
| **Priority Levels** | 4-tier priority system (low/medium/high/urgent) | Smart routing |
| **Visual Management** | Collapsible columns, status indicators | Easy monitoring |

### System Components

**1. Agent Columns (UI)**
- 26 vertical panels (one per agent)
- Collapsible/expandable design
- Thread info display
- Independent chat interfaces
- Status indicators

**2. Coordination Tools (Backend)**
- `assign_and_activate_agent_with_slugs` - Work distribution
- `request_update_from_thread` - Cross-agent messaging
- `respond_to_cross_thread_request` - Response handling

**3. Database Layer**
- Thread management (threads table)
- Cross-thread requests (cross_thread_requests table)
- Resource linking (thread_internal_docs, thread_synergy_sessions, thread_workflow)

**4. Integration Hubs**
- Automation Workflows (visual task sequences)
- Synergy Dashboard (project cards)
- Internal Docs (knowledge base)

---

## Getting Started

### Accessing the Command Centre

**Step 1: Navigate to Multi-Agent Tab**

The Multi-Agent Command Centre is accessed via the **main navigation bar**:

```
┌─────────────────────────────────────────────────────┐
│ [AI Prime] [Multi-Agent] [Synergy] [Settings]      │  ← Click "Multi-Agent"
└─────────────────────────────────────────────────────┘
```

**Step 2: Understanding the Layout**

When you open Multi-Agent tab, you'll see:

```
┌──────────────────────────────────────────────────────────────┐
│  MULTI-AGENT COMMAND CENTRE                                  │
├──────────────────────────────────────────────────────────────┤
│                                                              │
│  ┌──────┐  ┌──────┐  ┌──────┐  ┌──────┐  ┌──────┐  [+]    │
│  │Alpha │  │Bravo │  │Charlie│ │Delta │  │Echo  │  Add     │
│  │  1   │  │  2   │  │  3   │  │  4   │  │  5   │  Agent   │
│  ├──────┤  ├──────┤  ├──────┤  ├──────┤  ├──────┤          │
│  │      │  │      │  │      │  │      │  │      │          │
│  │ 💬   │  │ 💬   │  │ 💬   │  │ 💬   │  │ 💬   │          │
│  │      │  │      │  │      │  │      │  │      │          │
│  └──────┘  └──────┘  └──────┘  └──────┘  └──────┘          │
└──────────────────────────────────────────────────────────────┘
```

**Components:**
- **Agent Columns** - Each vertical panel is an independent AI agent
- **NATO Names** - Alpha, Bravo, Charlie, etc. (phonetic alphabet)
- **Agent Numbers** - 1-26 (alternate identifier)
- **Add Agent Button** - Expand to show more agents (up to 26 total)
- **Chat Interface** - Each agent has its own conversation area

### First-Time Setup

**Default State:**
- All 26 agents are available but **collapsed** (vertical bars)
- No threads assigned
- Empty state messages visible
- Ready for work distribution

**Initial Actions:**

1. **Decide on project structure**
   - How many agents do you need? (3-5 for typical projects)
   - What will each agent handle? (frontend, backend, testing, etc.)

2. **Expand needed agents**
   - Click on collapsed agent bars to expand them
   - Or use work distribution tool (auto-expands agents)

3. **Start distributing work**
   - Use AI Prime to orchestrate
   - Call `assign_and_activate_agent_with_slugs` tool
   - Agents automatically receive tasks

---

## Understanding the 26 NATO Agents

### The NATO Alphabet System

The platform uses the **NATO phonetic alphabet** for agent naming. This provides:
- ✅ Clear, unambiguous names (no "Agent 1" vs "Agent One" confusion)
- ✅ Professional military-style designation
- ✅ Easy verbal communication ("assign to Bravo")
- ✅ Memorable identifiers

### Complete Agent Roster

| ID | NATO Name | Alternate IDs | Typical Use Cases |
|----|-----------|---------------|-------------------|
| 1  | **Alpha** | agent-1, "1" | Frontend development, UI design |
| 2  | **Bravo** | agent-2, "2" | Backend APIs, server logic |
| 3  | **Charlie** | agent-3, "3" | Database design, schema |
| 4  | **Delta** | agent-4, "4" | Testing, QA, validation |
| 5  | **Echo** | agent-5, "5" | Documentation, technical writing |
| 6  | **Foxtrot** | agent-6, "6" | DevOps, deployment, CI/CD |
| 7  | **Golf** | agent-7, "7" | Security, authentication |
| 8  | **Hotel** | agent-8, "8" | Performance optimization |
| 9  | **India** | agent-9, "9" | Data analytics, reporting |
| 10 | **Juliet** | agent-10, "10" | Integration testing |
| 11 | **Kilo** | agent-11, "11" | Mobile development |
| 12 | **Lima** | agent-12, "12" | Email/notification systems |
| 13 | **Mike** | agent-13, "13" | Monitoring, logging |
| 14 | **November** | agent-14, "14" | Backup, recovery |
| 15 | **Oscar** | agent-15, "15" | User research, UX |
| 16 | **Papa** | agent-16, "16" | Payment integration |
| 17 | **Quebec** | agent-17, "17" | Search functionality |
| 18 | **Romeo** | agent-18, "18" | Real-time features |
| 19 | **Sierra** | agent-19, "19" | State management |
| 20 | **Tango** | agent-20, "20" | Third-party integrations |
| 21 | **Uniform** | agent-21, "21" | User management, admin |
| 22 | **Victor** | agent-22, "22" | Version control, Git |
| 23 | **Whiskey** | agent-23, "23" | Workflow automation |
| 24 | **X-ray** | agent-24, "24" | Error handling, debugging |
| 25 | **Yankee** | agent-25, "25" | YAML/config management |
| 26 | **Zulu** | agent-26, "26" | Time zone, i18n, localization |

### Agent Identifier Flexibility

You can reference agents in **THREE ways**:

**Method 1: NATO Name** (Recommended)
```python
target_agent='Alpha'
target_agent='Bravo'
target_agent='Charlie'
```

**Method 2: Agent Location**
```python
target_agent='agent-1'
target_agent='agent-2'
target_agent='agent-3'
```

**Method 3: Simple Number**
```python
target_agent='1'
target_agent='2'
target_agent='3'
```

**All three methods work identically** - the backend automatically converts them.

### Agent Specialization (Recommended Pattern)

While agents are **generalist AI assistants** (they can do anything), it's best to **assign specialized roles**:

**Why specialize?**
- ✅ Context stays focused (no topic switching)
- ✅ Expertise builds over conversation
- ✅ Easier to track progress
- ✅ Clearer handoffs between agents

**Example Specialization:**
```
E-Commerce Project:

Alpha   → React frontend (components, routing, state)
Bravo   → Express backend (API, middleware, auth)
Charlie → PostgreSQL database (schema, queries, migrations)
Delta   → Jest testing (unit tests, integration tests)
Echo    → Technical docs (API docs, README, setup guides)
```

---

## Working with Agent Columns

### Column States

Each agent column can be in one of **three states**:

**1. Collapsed (Default)**
```
│
│ A
│ l
│ p
│ h
│ a
│
│ 1
│
```
- Vertical bar with agent name
- Minimal screen space
- Click to expand

**2. Normal Width (400px)**
```
┌──────────────┐
│ Alpha        │
│ [Thread Info]│
├──────────────┤
│              │
│   Messages   │
│              │
├──────────────┤
│ [Input Box]  │
└──────────────┘
```
- Standard working mode
- Full chat interface
- Thread management

**3. Wide Width (600px)**
```
┌─────────────────────┐
│ Alpha               │
│ [Thread Info]       │
├─────────────────────┤
│                     │
│   Messages          │
│   (more room)       │
│                     │
├─────────────────────┤
│ [Input Box]         │
└─────────────────────┘
```
- Extra space for long code blocks
- Better for complex content
- Toggle with width button

### Column Anatomy

**Header Section:**
```
┌──────────────────────────────────────┐
│ 🤖 Alpha              [⚙️] [↔️] [×]  │  ← Name + Controls
├──────────────────────────────────────┤
│ 📋 Thread: "Build Frontend"          │  ← Thread Info
│ 🏷️ #frontend #react                  │  ← Tags
│ 🔗 Workflow: wf_abc123                │  ← Linked Resources
│ 📊 Synergy: Backend API Project       │  ← Project Link
└──────────────────────────────────────┘
```

**Controls Explained:**
- **[⚙️] Menu** - Hamburger menu (settings, clear, export)
- **[↔️] Width Toggle** - Switch between 400px and 600px
- **[×] Collapse** - Minimize to vertical bar

**Messages Section:**
```
┌──────────────────────────────────────┐
│                                      │
│  👤 You:                             │
│  "Create a React component for..."   │
│                                      │
│  🤖 Alpha:                           │
│  "Here's the component with hooks..." │
│  ```jsx                              │
│  function MyComponent() { ... }      │
│  ```                                 │
│                                      │
│  👤 You:                             │
│  "Add error handling"                │
│                                      │
│  🤖 Alpha (typing...)                │
│                                      │
└──────────────────────────────────────┘
```

**Input Section:**
```
┌──────────────────────────────────────┐
│ [📎] Attach files                    │
│ ┌────────────────────────────────┐   │
│ │ Type your message...           │   │
│ │                                │   │
│ │                                │   │
│ └────────────────────────────────┘   │
│              [➤ Send] [🎤]           │
└──────────────────────────────────────┘
```

### Managing Columns

**Expanding a Collapsed Column:**
1. Click anywhere on the vertical bar
2. Column animates to normal width (400px)
3. Thread info displays (if thread assigned)
4. Ready for interaction

**Collapsing an Expanded Column:**
1. Click the [×] button in header
2. Column animates to vertical bar
3. Saves screen space
4. Thread remains active (not deleted)

**Toggling Width:**
1. Click [↔️] width button in header
2. Toggles between 400px (normal) and 600px (wide)
3. Useful for viewing long code blocks
4. Independent per agent

**Removing an Agent Column:**
1. Click [⚙️] menu → "Remove Agent"
2. Confirmation prompt appears
3. Confirm removal
4. Column deleted (thread unassigned, not deleted)

### Thread Management in Columns

**Empty State (No Thread Assigned):**
```
┌──────────────────────────────────────┐
│ 🤖 Alpha                             │
├──────────────────────────────────────┤
│                                      │
│         📭                           │
│    No Thread Assigned                │
│                                      │
│  [📋 Select Thread] [➕ New Thread]  │
│                                      │
└──────────────────────────────────────┘
```

**With Thread Assigned:**
```
┌──────────────────────────────────────┐
│ 🤖 Alpha                             │
├──────────────────────────────────────┤
│ 📋 Thread: "React Frontend"          │
│ 🕒 Started: 2 hours ago              │
│ 💬 12 messages                       │
│ 🏷️ #frontend #react #ui             │
└──────────────────────────────────────┘
```

**Thread Actions:**
- **[📋] Thread Info** - Click to see full thread details
- **[🔄] Switch Thread** - Assign different thread to this agent
- **[➕] New Thread** - Create and assign new thread
- **[×] Unassign** - Clear thread from agent (thread not deleted)

---

## Distributing Work Across Agents

### The Primary Tool: assign_and_activate_agent_with_slugs

This is your **main orchestration command** - a powerful all-in-one tool that:
1. ✅ Creates or updates agent thread
2. ✅ Sends detailed instructions
3. ✅ Attaches resources (workflows, docs, Synergy cards)
4. ✅ Opens UI automatically
5. ✅ Triggers agent to start working

### Basic Work Distribution

**Scenario:** You want Alpha to build a frontend.

**Method 1: Through AI Prime (Recommended)**

You to AI Prime:
```
"Assign Alpha to build the React frontend for our e-commerce site. 
Include Material-UI components, routing, and state management."
```

AI Prime executes behind the scenes:
```python
assign_and_activate_agent_with_slugs(
    target_agent='Alpha',
    thread_title='Build React Frontend',
    instructions='''Create a React frontend for an e-commerce platform with:
    - Material-UI components
    - React Router for navigation
    - Redux for state management
    - Shopping cart functionality
    - Product listing pages
    - Checkout flow
    
    Focus on responsive design and accessibility.''',
    auto_trigger=True,
    open_ui=True
)
```

**Result:**
1. Multi-Agent tab automatically opens
2. Alpha column expands
3. New thread created: "Build React Frontend"
4. Instructions appear in Alpha's chat
5. Alpha starts responding with implementation plan

**Method 2: Direct Tool Call (Power Users)**

If you're in AI Prime and want explicit control:
```
You: "Use the agent coordination tool to assign Alpha with these 
specifications: [details]"

AI Prime: [calls tool with your specifications]
```

### Multi-Agent Distribution

**Scenario:** E-commerce project with 3 components.

**You to AI Prime:**
```
"Distribute this e-commerce project across 3 agents:
- Alpha: React frontend
- Bravo: Node.js backend API
- Charlie: PostgreSQL database schema"
```

**AI Prime executes 3 calls:**

```python
# Agent 1: Alpha - Frontend
assign_and_activate_agent_with_slugs(
    target_agent='Alpha',
    thread_title='E-Commerce Frontend (React)',
    instructions='''Build React frontend with:
    - Product catalog pages
    - Shopping cart
    - Checkout flow
    - User authentication UI
    - Material-UI components
    - Responsive design''',
    auto_trigger=True,
    open_ui=True
)

# Agent 2: Bravo - Backend
assign_and_activate_agent_with_slugs(
    target_agent='Bravo',
    thread_title='E-Commerce Backend API (Node.js)',
    instructions='''Build Express.js backend with:
    - RESTful API endpoints
    - JWT authentication
    - Product CRUD operations
    - Order management
    - Payment integration (Stripe)
    - Input validation''',
    auto_trigger=True,
    open_ui=True
)

# Agent 3: Charlie - Database
assign_and_activate_agent_with_slugs(
    target_agent='Charlie',
    thread_title='E-Commerce Database (PostgreSQL)',
    instructions='''Design PostgreSQL database with:
    - Users table (auth, profiles)
    - Products table (inventory)
    - Orders table (transactions)
    - Order_items table (line items)
    - Proper indexes and foreign keys
    - Migration scripts''',
    auto_trigger=True,
    open_ui=True
)
```

**Result:**
- All 3 agents receive work **simultaneously**
- Each agent works **independently** on their component
- You can monitor all 3 conversations in parallel
- **3x faster** than sequential work

### Attaching Resources (Slugs)

**What are slugs?**
Slugs are **unique identifiers** for platform resources:
- `workflow_slug` - Visual automation workflows
- `internal_doc_slug` - Internal documentation
- `synergy_session_id` - Synergy project cards

**Why attach resources?**
✅ Agents get shared context  
✅ No need to re-explain background  
✅ Centralized project view  
✅ Consistent specifications

**Example with Resources:**

```python
assign_and_activate_agent_with_slugs(
    target_agent='Alpha',
    thread_title='Build Payment UI',
    instructions='Create payment form component with Stripe integration',
    slugs={
        'workflow_slug': 'wf_payment_flow_abc123',      # Visual workflow
        'internal_doc_slug': 'doc_stripe_guide_xyz789', # Stripe setup guide
        'synergy_session_id': 'sess_ecommerce_project'  # Project card
    },
    auto_trigger=True,
    open_ui=True
)
```

**What Alpha sees:**
```
📋 Thread: "Build Payment UI"

🔗 Linked Resources:
- 🔄 Workflow: wf_payment_flow_abc123 (Payment Flow)
- 📄 Doc: doc_stripe_guide_xyz789 (Stripe Integration Guide)
- 📊 Project: sess_ecommerce_project (E-Commerce Project)

💬 Instructions:
"Create payment form component with Stripe integration..."
```

**Alpha can now:**
- View the visual workflow for payment steps
- Reference the Stripe setup documentation
- Update progress in the Synergy project card
- Work with full context

### Auto-Trigger Behavior

**auto_trigger=True (Recommended):**
- Agent receives instructions
- Agent **immediately starts responding**
- You get instant progress
- Agent works autonomously

**auto_trigger=False:**
- Agent receives instructions
- Instructions appear as **user message** in thread
- Agent waits for you to say "proceed" or similar
- More manual control

**Example:**
```python
# With auto-trigger
assign_and_activate_agent_with_slugs(
    target_agent='Alpha',
    thread_title='Build Login Page',
    instructions='Create login page with email/password',
    auto_trigger=True  # ← Agent starts immediately
)

# Without auto-trigger
assign_and_activate_agent_with_slugs(
    target_agent='Bravo',
    thread_title='Setup CI/CD',
    instructions='Configure GitHub Actions for deployment',
    auto_trigger=False  # ← Agent waits for your command
)
```

### UI Automation (open_ui Parameter)

**open_ui=True (Default):**
- Automatically switches to Multi-Agent tab
- Expands the assigned agent column
- Displays thread info
- Scrolls to agent if needed
- **You see the work immediately**

**open_ui=False:**
- Work assigned silently in background
- No UI changes
- You can view agent later manually
- Useful for bulk assignments

---

## Cross-Agent Communication

Agents can **talk to each other** without your intervention using the cross-thread request system.

### The Request/Response System

**How it works:**

```
┌─────────┐                    ┌─────────┐
│  Alpha  │                    │  Bravo  │
│         │                    │         │
│  "I need│──── REQUEST ────→ │         │
│   API   │                    │ "Here's │
│   docs" │                    │  the    │
│         │←──── RESPONSE ──── │  doc"   │
└─────────┘                    └─────────┘
```

### Tool 1: request_update_from_thread

**Purpose:** Agent requests information from another agent.

**Use Cases:**
- Status updates ("Is the API ready?")
- Deliverables ("Send me the database schema")
- Questions ("What authentication method are you using?")
- Coordination ("When will testing be complete?")
- Resources ("Share the API documentation")

**Example:**

Alpha (frontend) needs to know when Bravo's (backend) API is ready:

```python
request_update_from_thread(
    target_thread_id='Bravo',
    request_message='What is the current status of the authentication API? I need the endpoint URLs to connect the frontend login form.',
    request_type='status_update',
    priority='high',
    wait_for_response=True,
    timeout=300
)
```

**What happens:**

1. **Request created** in database (cross_thread_requests table)
2. **Bravo's thread displays request** as special message:
   ```
   ┌────────────────────────────────────────┐
   │ 🚨 REQUEST FROM ALPHA (HIGH PRIORITY)  │
   │                                        │
   │ "What is the current status of the    │
   │  authentication API? I need endpoint  │
   │  URLs for frontend login form."       │
   │                                        │
   │ Request Type: status_update            │
   │ Priority: high 🟠                      │
   │                                        │
   │ [Respond to Request]                   │
   └────────────────────────────────────────┘
   ```

3. **Bravo processes request** and formulates answer
4. **Bravo calls respond tool** (see below)
5. **Alpha receives response** in their thread
6. **Request marked complete** in database

### Tool 2: respond_to_cross_thread_request

**Purpose:** Agent responds to incoming request.

**Bravo's response:**

```python
respond_to_cross_thread_request(
    request_id='req_abc123',  # From database
    response_message='''Authentication API is 90% complete. 

Available endpoints:
- POST /api/auth/login (ready)
- POST /api/auth/register (ready)
- POST /api/auth/logout (ready)
- GET /api/auth/verify (in testing)

Base URL: http://localhost:3000
Auth method: JWT tokens in Authorization header

Expected completion: End of day today.
Let me know if you need example requests.'''
)
```

**What happens:**

1. **Response stored** in database
2. **Alpha's thread receives notification:**
   ```
   ┌────────────────────────────────────────┐
   │ ✅ RESPONSE FROM BRAVO                 │
   │                                        │
   │ "Authentication API is 90% complete.  │
   │  Available endpoints:                  │
   │  - POST /api/auth/login (ready)       │
   │  - POST /api/auth/register (ready)    │
   │  - POST /api/auth/logout (ready)      │
   │  - GET /api/auth/verify (testing)     │
   │                                        │
   │  Base URL: http://localhost:3000      │
   │  Auth: JWT tokens in Authorization    │
   │                                        │
   │  Expected completion: EOD today."      │
   └────────────────────────────────────────┘
   ```

3. **Request status** → `completed`
4. **Alpha continues work** with new information

### Priority Levels

Requests have **4 priority levels** with color coding:

| Priority | Color | Icon | Use When |
|----------|-------|------|----------|
| **Low** | Blue 🔵 | ℹ️ | "FYI", optional info, low urgency |
| **Medium** | Yellow 🟡 | ⚠️ | Standard requests, normal timeline |
| **High** | Orange 🟠 | 🚨 | Blocking work, need soon |
| **Urgent** | Red 🔴 | 🚨🚨 | Critical blocker, immediate attention |

**Example Priority Usage:**

```python
# LOW: Optional enhancement suggestion
request_update_from_thread(
    target_thread_id='Delta',
    request_message='If you have time, could you add some edge case tests?',
    priority='low'
)

# MEDIUM: Standard coordination
request_update_from_thread(
    target_thread_id='Echo',
    request_message='Please document the new API endpoints when ready',
    priority='medium'
)

# HIGH: Blocking progress
request_update_from_thread(
    target_thread_id='Bravo',
    request_message='I cannot deploy without the production database credentials',
    priority='high'
)

# URGENT: Critical issue
request_update_from_thread(
    target_thread_id='Alpha',
    request_message='Production login is broken! Users cannot sign in!',
    priority='urgent'
)
```

### Request Types

**5 request types** for categorization:

1. **status_update** - "Where are you at?"
2. **deliverable** - "Send me the output"
3. **question** - "How does X work?"
4. **coordination** - "When should we integrate?"
5. **resource_request** - "I need Y file/doc/key"

**Type affects how agents prioritize and respond:**

```python
# Status update - expect progress summary
request_type='status_update'

# Deliverable - expect files, code, or output
request_type='deliverable'

# Question - expect explanatory answer
request_type='question'

# Coordination - expect timeline or plan
request_type='coordination'

# Resource - expect link, file, or credentials
request_type='resource_request'
```

---

## Advanced Coordination Patterns

### Pattern 1: Parallel Component Development

**Scenario:** Build 3 independent components simultaneously.

**Setup:**
```python
# Assign 3 agents to separate components
assign_and_activate_agent_with_slugs(target_agent='Alpha', 
    thread_title='User Profile Component', ...)
assign_and_activate_agent_with_slugs(target_agent='Bravo', 
    thread_title='Dashboard Component', ...)
assign_and_activate_agent_with_slugs(target_agent='Charlie', 
    thread_title='Settings Component', ...)
```

**Workflow:**
```
Hour 1: All agents receive specifications
Hour 2: All agents build components in parallel
Hour 3: All components ready for integration
Hour 4: Main agent integrates all components

Result: 3 components in 4 hours (vs 12 hours sequential)
```

**Benefits:**
- ✅ 3x speed increase
- ✅ No context switching
- ✅ Specialized focus per agent
- ✅ Independent testing

### Pattern 2: Pipeline Architecture

**Scenario:** Multi-stage data pipeline.

**Setup:**
```
Alpha  → Data Collection (scraping, API calls)
   ↓
Bravo  → Data Processing (cleaning, transformation)
   ↓
Charlie → Data Analysis (insights, visualization)
   ↓
Delta  → Report Generation (dashboard, PDF export)
```

**Workflow:**
```python
# Stage 1: Alpha collects data
assign_and_activate_agent_with_slugs(
    target_agent='Alpha',
    thread_title='Data Collection Pipeline',
    instructions='Scrape product data from competitor websites...'
)

# Wait for Alpha to finish (or Alpha triggers next)
# Alpha sends completion message to Bravo:
request_update_from_thread(
    target_thread_id='Bravo',
    request_message='Data collection complete. 10,000 records ready in CSV format at /data/raw/products.csv',
    request_type='deliverable',
    priority='medium'
)

# Stage 2: Bravo processes data
assign_and_activate_agent_with_slugs(
    target_agent='Bravo',
    thread_title='Data Processing Pipeline',
    instructions='Clean and transform raw product data...'
)

# Bravo → Charlie (after processing)
# Charlie → Delta (after analysis)
# Result: Automated pipeline with agent handoffs
```

### Pattern 3: Review/QA Chain

**Scenario:** Code review and quality assurance.

**Setup:**
```
Alpha  → Implement feature
   ↓
Bravo  → Code review (logic, style, best practices)
   ↓
Charlie → Security audit (vulnerabilities, auth)
   ↓
Delta  → Performance testing (load, memory)
   ↓
Echo  → Documentation review
```

**Workflow:**
```python
# 1. Alpha builds feature
assign_and_activate_agent_with_slugs(
    target_agent='Alpha',
    thread_title='Payment Integration Feature',
    instructions='Implement Stripe payment processing...'
)

# 2. Alpha requests code review from Bravo
request_update_from_thread(
    target_thread_id='Bravo',
    request_message='Payment feature complete. Please review code at /src/payment.js',
    request_type='deliverable',
    priority='high'
)

# 3. Bravo reviews and responds
respond_to_cross_thread_request(
    request_id='req_abc',
    response_message='Code review complete. Found 3 issues: ...'
)

# 4. Alpha fixes issues, requests security audit from Charlie
request_update_from_thread(
    target_thread_id='Charlie',
    request_message='Issues fixed. Please run security audit',
    priority='high'
)

# 5. Continue chain...
# Result: Multi-stage quality gates
```

### Pattern 4: Synergy-Linked Team

**Scenario:** All agents working on same project with unified dashboard.

**Setup:**
```python
# Create Synergy session first (via Synergy Dashboard)
synergy_id = 'sess_ecommerce_mvp'

# Assign all agents to same Synergy session
assign_and_activate_agent_with_slugs(
    target_agent='Alpha',
    thread_title='Frontend Development',
    slugs={'synergy_session_id': synergy_id},
    ...
)

assign_and_activate_agent_with_slugs(
    target_agent='Bravo',
    thread_title='Backend Development',
    slugs={'synergy_session_id': synergy_id},
    ...
)

assign_and_activate_agent_with_slugs(
    target_agent='Charlie',
    thread_title='Database Design',
    slugs={'synergy_session_id': synergy_id},
    ...
)
```

**Result:**
- All 3 agents linked to same Synergy project card
- Synergy dashboard shows unified progress
- Milestones visible across all agents
- Centralized project management
- Easy status reporting

### Pattern 5: Specialization Matrix

**Scenario:** Large enterprise application with 10+ components.

**Setup:**
```
FRONTEND (3 agents):
- Alpha: React components
- Bravo: State management (Redux)
- Charlie: UI/UX polish

BACKEND (3 agents):
- Delta: Express API
- Echo: Authentication service
- Foxtrot: Payment processing

DATA (2 agents):
- Golf: PostgreSQL schema
- Hotel: Data migrations

INFRASTRUCTURE (2 agents):
- India: AWS deployment
- Juliet: CI/CD pipeline
```

**Workflow:**
```python
# Assign all 10 agents in parallel
for agent_config in team_structure:
    assign_and_activate_agent_with_slugs(**agent_config)

# Result: 10 agents working simultaneously
# Coordination via cross-agent messaging
# Completion in 1/10th the time
```

---

## Real-World Use Case Scenarios

### Use Case 1: E-Commerce Platform (3-Agent Team)

**Goal:** Build an MVP e-commerce site in 1 week.

**Team Structure:**
- **Alpha** - Frontend (React, Tailwind CSS)
- **Bravo** - Backend (Node.js, Express, Stripe)
- **Charlie** - Database (PostgreSQL, schema, seeds)

**Day 1: Setup & Architecture**

You to AI Prime:
```
"Set up 3-agent team for e-commerce MVP:
- Alpha: React frontend
- Bravo: Express backend  
- Charlie: PostgreSQL database

All agents should reference the wf_ecommerce_mvp workflow 
and link to sess_ecommerce_project Synergy card."
```

AI Prime distributes work (3 parallel calls):
```python
# Alpha assignment
assign_and_activate_agent_with_slugs(
    target_agent='Alpha',
    thread_title='E-Commerce Frontend (React)',
    instructions='''Build React e-commerce frontend with:
    
    PAGES:
    - Home (hero, featured products)
    - Product listing (filters, search, pagination)
    - Product detail (images, description, add to cart)
    - Shopping cart (item management, quantity)
    - Checkout (shipping, payment form)
    - Order confirmation
    
    FEATURES:
    - Responsive design (mobile-first)
    - Tailwind CSS styling
    - React Router navigation
    - Redux state management
    - API integration ready (mock data initially)
    
    DELIVERABLES:
    - Component library
    - Page layouts
    - State management structure
    - Mock data for testing
    ''',
    slugs={
        'workflow_slug': 'wf_ecommerce_mvp',
        'synergy_session_id': 'sess_ecommerce_project'
    },
    auto_trigger=True,
    open_ui=True
)

# Bravo assignment
assign_and_activate_agent_with_slugs(
    target_agent='Bravo',
    thread_title='E-Commerce Backend API (Node.js)',
    instructions='''Build Express.js backend API with:
    
    ENDPOINTS:
    Products:
    - GET /api/products (list with filters)
    - GET /api/products/:id (single product)
    - POST /api/products (admin create)
    
    Cart:
    - POST /api/cart/add (add item)
    - GET /api/cart (view cart)
    - DELETE /api/cart/:id (remove item)
    
    Orders:
    - POST /api/orders (create order)
    - GET /api/orders/:id (order status)
    
    Auth:
    - POST /api/auth/register
    - POST /api/auth/login (JWT)
    - GET /api/auth/verify
    
    Payment:
    - POST /api/payment/stripe (Stripe integration)
    
    FEATURES:
    - JWT authentication
    - Input validation (Joi)
    - Error handling middleware
    - CORS configuration
    - Rate limiting
    
    DELIVERABLES:
    - API endpoints
    - Middleware stack
    - Integration tests
    - API documentation (Postman collection)
    ''',
    slugs={
        'workflow_slug': 'wf_ecommerce_mvp',
        'synergy_session_id': 'sess_ecommerce_project'
    },
    auto_trigger=True,
    open_ui=True
)

# Charlie assignment
assign_and_activate_agent_with_slugs(
    target_agent='Charlie',
    thread_title='E-Commerce Database (PostgreSQL)',
    instructions='''Design PostgreSQL database schema for e-commerce:
    
    TABLES:
    users:
    - id, email, password_hash, name, created_at
    
    products:
    - id, name, description, price, stock, image_url, category_id
    
    categories:
    - id, name, slug
    
    orders:
    - id, user_id, total, status, shipping_address, created_at
    
    order_items:
    - id, order_id, product_id, quantity, price_at_purchase
    
    cart_items:
    - id, user_id, product_id, quantity, added_at
    
    FEATURES:
    - Foreign key constraints
    - Indexes on frequently queried columns
    - Default values and NOT NULL constraints
    - Timestamps (created_at, updated_at)
    
    DELIVERABLES:
    - Schema migration scripts
    - Seed data (sample products, categories)
    - Database diagram
    - Query examples
    ''',
    slugs={
        'workflow_slug': 'wf_ecommerce_mvp',
        'synergy_session_id': 'sess_ecommerce_project'
    },
    auto_trigger=True,
    open_ui=True
)
```

**Result:**
- All 3 agents receive work simultaneously
- Multi-Agent tab opens showing all 3 columns
- Each agent starts building their component
- All linked to same Synergy project card

**Day 2-3: Development (Parallel)**

Each agent works independently:

**Alpha's Progress:**
- Day 2 AM: Component structure, routing setup
- Day 2 PM: Home page, product listing
- Day 3 AM: Product detail, cart UI
- Day 3 PM: Checkout form, integration prep

**Bravo's Progress:**
- Day 2 AM: Express setup, middleware stack
- Day 2 PM: Product endpoints, validation
- Day 3 AM: Auth endpoints, JWT logic
- Day 3 PM: Order endpoints, Stripe integration

**Charlie's Progress:**
- Day 2 AM: Schema design, table creation
- Day 2 PM: Indexes, foreign keys, constraints
- Day 3 AM: Migration scripts tested
- Day 3 PM: Seed data created (100 products)

**Day 4: Cross-Agent Coordination**

Alpha needs API details from Bravo:
```python
# Alpha → Bravo request
request_update_from_thread(
    target_thread_id='Bravo',
    request_message='Frontend is ready to integrate. Please provide:
    1. API base URL
    2. Authentication flow details
    3. Example request/response for each endpoint
    4. Error codes and handling',
    request_type='deliverable',
    priority='high'
)
```

Bravo responds:
```python
respond_to_cross_thread_request(
    request_id='req_alpha_api_details',
    response_message='''API integration details:

    BASE URL: http://localhost:3000/api
    
    AUTHENTICATION:
    1. User registers/logs in → receives JWT token
    2. Include token in all requests:
       Header: Authorization: Bearer <token>
    
    ENDPOINTS:
    [Detailed documentation with examples...]
    
    ERROR CODES:
    400: Bad request (validation failed)
    401: Unauthorized (no/invalid token)
    404: Resource not found
    500: Server error
    '''
)
```

Charlie shares database credentials with Bravo:
```python
request_update_from_thread(
    target_thread_id='Bravo',
    request_message='Database is ready. Connection details:
    Host: localhost
    Database: ecommerce_db
    User: [credentials]
    Schema: [attached]',
    request_type='resource_request',
    priority='medium'
)
```

**Day 5-6: Integration & Testing**

All agents coordinate final integration:
- Alpha connects to Bravo's API
- Bravo connects to Charlie's database
- End-to-end testing across all 3 components

**Day 7: Deployment & Documentation**

- Agents collaborate on deployment checklist
- Documentation compiled from all 3 agents
- MVP ready for launch

**Result:**
✅ Full e-commerce MVP in 1 week  
✅ 3 specialists working in parallel  
✅ Organized via Synergy dashboard  
✅ Clean handoffs via cross-agent messaging  
✅ 3x faster than single-agent approach  

---

### Use Case 2: API Migration (5-Agent Pipeline)

**Goal:** Migrate legacy REST API to GraphQL.

**Team Structure:**
- **Alpha** - Audit existing REST API (endpoints, schemas)
- **Bravo** - Design GraphQL schema (types, queries, mutations)
- **Charlie** - Implement GraphQL resolvers
- **Delta** - Write integration tests
- **Echo** - Update documentation

**Week 1: Sequential Pipeline**

**Stage 1: Alpha - API Audit**
```python
assign_and_activate_agent_with_slugs(
    target_agent='Alpha',
    thread_title='REST API Audit',
    instructions='Audit all 47 REST endpoints. Document:
    - Endpoint URLs and HTTP methods
    - Request/response schemas
    - Authentication requirements
    - Rate limits
    - Usage statistics
    Output: Complete API inventory spreadsheet'
)
```

**Stage 2: Alpha → Bravo Handoff**

Alpha completes audit, notifies Bravo:
```python
request_update_from_thread(
    target_thread_id='Bravo',
    request_message='API audit complete. 47 endpoints documented.
    Attached: api_inventory.xlsx
    Ready for GraphQL schema design.',
    request_type='deliverable',
    priority='high'
)
```

**Stage 3: Bravo - GraphQL Schema Design**

Bravo receives Alpha's work:
```python
assign_and_activate_agent_with_slugs(
    target_agent='Bravo',
    thread_title='GraphQL Schema Design',
    instructions='Design GraphQL schema based on Alpha\'s audit.
    Create:
    - Type definitions for all resources
    - Query operations (single, list, filtered)
    - Mutation operations (create, update, delete)
    - Pagination strategy
    - Error handling types
    Output: schema.graphql file'
)
```

**Stage 4: Bravo → Charlie Handoff**

Bravo completes schema, notifies Charlie:
```python
request_update_from_thread(
    target_thread_id='Charlie',
    request_message='GraphQL schema complete.
    Attached: schema.graphql
    22 types, 15 queries, 12 mutations defined.
    Ready for resolver implementation.',
    request_type='deliverable',
    priority='high'
)
```

**Stage 5: Charlie - Resolver Implementation**

Charlie builds resolvers:
```python
assign_and_activate_agent_with_slugs(
    target_agent='Charlie',
    thread_title='GraphQL Resolver Implementation',
    instructions='Implement resolvers for Bravo\'s schema.
    - Connect to existing database
    - Map REST calls to resolvers (transitional)
    - Implement pagination
    - Add authentication checks
    - Handle errors gracefully
    Output: Working GraphQL server'
)
```

**Stages 6-7: Parallel Testing & Documentation**

Charlie notifies both Delta and Echo simultaneously:
```python
# To Delta (Testing)
request_update_from_thread(
    target_thread_id='Delta',
    request_message='GraphQL server is live at http://localhost:4000.
    Please write integration tests for all queries and mutations.',
    request_type='coordination',
    priority='high'
)

# To Echo (Documentation)
request_update_from_thread(
    target_thread_id='Echo',
    request_message='GraphQL API is ready for documentation.
    Schema attached. Please create:
    - API reference guide
    - Migration guide for clients
    - Example queries
    - Authentication guide',
    request_type='coordination',
    priority='medium'
)
```

Delta and Echo work in parallel on final stage.

**Result:**
✅ API migration in 2 weeks  
✅ Structured pipeline with clear handoffs  
✅ Final 2 stages parallelized  
✅ Documentation and testing together  
✅ Smooth coordination via request system  

---

### Use Case 3: Security Audit (Specialist Team)

**Goal:** Comprehensive security audit of web application.

**Team Structure (8 specialized agents):**
- **Alpha** - Authentication & Authorization
- **Bravo** - Input Validation & SQL Injection
- **Charlie** - XSS & CSRF Protection
- **Delta** - API Security & Rate Limiting
- **Echo** - Secrets Management
- **Foxtrot** - Dependency Vulnerabilities (npm audit)
- **Golf** - Network Security (HTTPS, CORS, headers)
- **Hotel** - Compliance Check (GDPR, CCPA)

**Parallel Execution:**

All 8 agents receive assignments simultaneously:
```python
security_areas = [
    ('Alpha', 'Authentication & Authorization Audit'),
    ('Bravo', 'Input Validation & SQL Injection Check'),
    ('Charlie', 'XSS & CSRF Protection Review'),
    ('Delta', 'API Security & Rate Limiting'),
    ('Echo', 'Secrets Management Audit'),
    ('Foxtrot', 'Dependency Vulnerability Scan'),
    ('Golf', 'Network Security Configuration'),
    ('Hotel', 'Compliance Check (GDPR/CCPA)')
]

for agent, audit_area in security_areas:
    assign_and_activate_agent_with_slugs(
        target_agent=agent,
        thread_title=f'Security Audit: {audit_area}',
        instructions=f'Comprehensive {audit_area} audit. Report:
        - Vulnerabilities found (severity: critical/high/medium/low)
        - Code examples of issues
        - Recommended fixes
        - Implementation steps',
        slugs={'synergy_session_id': 'sess_security_audit'},
        auto_trigger=True
    )
```

**Day 1-2: Parallel Audits**

All 8 agents work simultaneously, each producing detailed reports.

**Day 3: Consolidation**

AI Prime (you) reviews all 8 reports:
```
You: "Compile all security findings into priority-ordered list"

AI Prime: [Aggregates findings from all 8 agents]
- 3 critical issues (immediate fix required)
- 7 high-priority issues (fix this week)
- 12 medium issues (fix this month)
- 8 low issues (nice-to-have)
```

**Result:**
✅ Complete security audit in 3 days  
✅ 8 specialized focus areas  
✅ Parallel execution = 8x faster  
✅ Comprehensive coverage  
✅ Actionable remediation plan  

---

### Use Case 4: Content Generation (Marketing Campaign)

**Goal:** Launch marketing campaign with 5 content types.

**Team Structure:**
- **Alpha** - Blog articles (3 long-form posts)
- **Bravo** - Social media content (50 posts across platforms)
- **Charlie** - Email campaigns (5 email sequences)
- **Delta** - Landing pages (3 conversion-optimized pages)
- **Echo** - Video scripts (5 YouTube scripts)

**Day 1: Content Briefs**

You provide master brief to AI Prime:
```
"Launch marketing campaign for new SaaS product. Target: B2B tech companies.

Need:
- 3 blog posts (SEO-optimized, 2000+ words)
- 50 social media posts (LinkedIn, Twitter)
- 5 email sequences (welcome, onboarding, conversion)
- 3 landing pages (homepage, pricing, demo request)
- 5 YouTube video scripts (product tutorials)

Brand voice: Professional but approachable. Focus on ROI and efficiency.
Keywords: automation, workflow, productivity"
```

AI Prime distributes to 5 agents:
```python
for agent_config in content_team:
    assign_and_activate_agent_with_slugs(
        target_agent=agent_config['agent'],
        thread_title=agent_config['title'],
        instructions=agent_config['instructions'],
        slugs={'internal_doc_slug': 'doc_brand_guidelines'},
        auto_trigger=True
    )
```

**Day 2-3: Parallel Content Creation**

All 5 agents create content simultaneously:
- Alpha writes 3 blog posts
- Bravo creates 50 social posts
- Charlie designs 5 email sequences
- Delta builds 3 landing pages
- Echo writes 5 video scripts

**Day 4: Review & Integration**

You review content from all 5 agents in parallel:
```
- Open Alpha's column: Read blog post drafts
- Open Bravo's column: Review social media calendar
- Open Charlie's column: Test email flows
- Open Delta's column: Check landing page copy
- Open Echo's column: Review video scripts
```

Request revisions via each agent's thread:
```
You to Alpha: "Blog post 2 needs more data points. Add 3 case studies."
You to Bravo: "Social posts are too formal. Make them more conversational."
You to Charlie: "Email 3 subject line needs A/B test variants."
You to Delta: "Landing page CTAs could be stronger."
You to Echo: "Video 4 script too long. Target 8 minutes instead of 12."
```

**Result:**
✅ 66 pieces of content in 4 days  
✅ 5 content types simultaneously  
✅ Consistent brand voice (shared doc)  
✅ Efficient review process (parallel columns)  
✅ Campaign ready for launch  

---

## Best Practices

### Work Distribution Strategy

**✅ DO:**

1. **Assign clear, focused tasks**
   ```python
   # GOOD: Specific scope
   assign_and_activate_agent_with_slugs(
       target_agent='Alpha',
       thread_title='User Authentication Module',
       instructions='Build JWT-based auth with login, register, logout'
   )
   
   # BAD: Vague scope
   assign_and_activate_agent_with_slugs(
       target_agent='Alpha',
       thread_title='Handle User Stuff',
       instructions='Do user things'
   )
   ```

2. **Provide sufficient context**
   - Attach relevant workflows
   - Link to documentation
   - Reference Synergy projects
   - Include specifications

3. **Set realistic boundaries**
   - One major feature per agent
   - Break large projects into agent-sized chunks
   - Don't overload a single agent

4. **Use descriptive thread titles**
   - ✅ "E-Commerce Checkout Flow (React)"
   - ✅ "PostgreSQL Database Schema Design"
   - ❌ "Frontend"
   - ❌ "Agent 1 Work"

**❌ DON'T:**

1. **Don't assign overlapping work**
   ```python
   # BAD: Both agents doing same thing
   assign_and_activate_agent_with_slugs(target_agent='Alpha', 
       instructions='Build user login')
   assign_and_activate_agent_with_slugs(target_agent='Bravo', 
       instructions='Create user authentication')
   ```

2. **Don't create artificial dependencies**
   - If tasks can be parallel, make them parallel
   - Don't force sequential work unnecessarily

3. **Don't forget resource links**
   - Agents need context to work effectively
   - Always attach relevant workflows/docs

### Agent Naming & Organization

**✅ DO:**

1. **Use NATO names consistently**
   ```python
   target_agent='Alpha'   # Preferred
   target_agent='Bravo'   # Clear
   target_agent='Charlie' # Professional
   ```

2. **Assign logical roles**
   ```
   Alpha → Frontend
   Bravo → Backend
   Charlie → Database
   Delta → Testing
   Echo → Documentation
   ```

3. **Keep track of assignments**
   - Document which agent handles what
   - Maintain agent roster in Synergy
   - Use consistent naming across projects

**❌ DON'T:**

1. **Don't mix identifier styles**
   ```python
   # BAD: Inconsistent
   target_agent='Alpha'   # NATO name
   target_agent='agent-2' # Location format
   target_agent='3'       # Number only
   
   # GOOD: Pick one and stick with it
   target_agent='Alpha'
   target_agent='Bravo'
   target_agent='Charlie'
   ```

2. **Don't reuse agents for unrelated work**
   - If Alpha is doing frontend, don't suddenly assign backend
   - Finish one thread before starting completely different work

### Cross-Agent Communication

**✅ DO:**

1. **Use appropriate priority levels**
   ```python
   # Blocking work
   priority='urgent'
   
   # Standard request
   priority='medium'
   
   # Optional info
   priority='low'
   ```

2. **Provide complete context in requests**
   ```python
   # GOOD: Clear request
   request_message='''I need the API authentication flow details:
   1. Token format (JWT/session)
   2. Where to include token (header/body)
   3. Token expiration time
   4. Refresh token mechanism
   5. Example requests'''
   
   # BAD: Vague request
   request_message='How does auth work?'
   ```

3. **Choose correct request types**
   - Status update → "Where are you at?"
   - Deliverable → "Send me the code"
   - Question → "How does X work?"
   - Coordination → "When should we sync?"
   - Resource → "I need Y file"

**❌ DON'T:**

1. **Don't spam requests**
   - Wait for responses before re-requesting
   - Give agents time to work
   - Use appropriate timeouts

2. **Don't set all requests to 'urgent'**
   - Reserve urgent for true blockers
   - Overusing urgent dilutes its meaning

3. **Don't forget to respond**
   - If an agent requests info from you, respond promptly
   - Stalled requests block progress

### UI Management

**✅ DO:**

1. **Collapse unused agents**
   - Keep workspace clean
   - Only expand agents actively working
   - Collapse after work complete

2. **Use width toggle strategically**
   - Normal (400px) for most work
   - Wide (600px) for code reviews, long output

3. **Monitor all active agents**
   - Check progress periodically
   - Read new messages
   - Respond to requests

4. **Use thread info effectively**
   - Click thread info to see full context
   - Check linked resources
   - Review tags and metadata

**❌ DON'T:**

1. **Don't leave all 26 agents expanded**
   - Cluttered workspace
   - Hard to focus
   - Performance impact

2. **Don't lose track of which agents are working**
   - Mark completed agents
   - Close threads when done
   - Maintain organized workspace

### Project Organization

**✅ DO:**

1. **Link agents to Synergy projects**
   ```python
   # All agents on same project
   slugs={'synergy_session_id': 'sess_project_abc'}
   ```

2. **Use consistent documentation**
   - Share brand guidelines
   - Link to specs
   - Provide API docs

3. **Establish communication patterns**
   - Define when agents should request updates
   - Set response time expectations
   - Use priority levels correctly

4. **Review agent work regularly**
   - Check progress daily
   - Provide feedback
   - Adjust course if needed

**❌ DON'T:**

1. **Don't let agents diverge**
   - Ensure consistency across agents
   - Regular check-ins
   - Centralized specifications

2. **Don't ignore cross-agent requests**
   - Agents need coordination
   - Blocked agents = delayed project

---

## Frequently Asked Questions

### General Questions

**Q: How many agents can I use at once?**
A: Up to 26 agents (Alpha through Zulu). However, 3-5 agents is optimal for most projects. Using all 26 is rare and typically only for massive enterprise projects.

**Q: Can agents see each other's conversations?**
A: No. Each agent has an isolated thread. Agents can only communicate via the cross-thread request system, where they explicitly send messages to each other.

**Q: Do I need to manually open agent columns?**
A: No. When you use `assign_and_activate_agent_with_slugs` with `open_ui=True`, the UI automatically switches to Multi-Agent tab and opens the assigned agent column.

**Q: What happens if I assign work to an agent that's already busy?**
A: The tool will either:
1. Create a new thread for that agent (if you want separate work)
2. Or update the existing thread with new instructions (if continuing same work)

You control this by checking if the agent has an active thread before assigning.

**Q: Can I reassign an agent to different work mid-project?**
A: Yes, but it's not recommended. Agents work best when focused on one area. If you need to switch, consider:
1. Finishing current work first
2. Using a different agent for new work
3. Explicitly closing the old thread before starting new work

### Work Distribution

**Q: Should I use AI Prime to distribute work, or call tools directly?**
A: **Use AI Prime** (recommended). Tell AI Prime what you want to accomplish, and it will handle the tool calls. This is easier and more natural than manually crafting tool parameters.

**Q: Can I distribute work without the UI opening?**
A: Yes. Set `open_ui=False` in the tool call. Work is assigned silently in the background. Useful for bulk assignments where you don't want 5+ tabs opening at once.

**Q: How do I know if an agent received my assignment?**
A: Check the agent's column:
- Thread title appears in header
- Instructions show as first message
- Agent starts responding (if `auto_trigger=True`)
- Thread info displays resources

**Q: Can I assign the same workflow to multiple agents?**
A: Yes. Multiple agents can reference the same workflow slug. Each agent gets their own copy of the context.

### Cross-Agent Communication

**Q: Do agents automatically communicate, or do I need to tell them?**
A: **Semi-automatic**:
- You can instruct agents to request updates from each other
- AI Prime can orchestrate cross-agent messaging
- Agents won't spontaneously message each other without direction

**Q: What if Agent A requests info from Agent B, but B is still working?**
A: The request appears in B's thread as a special message. Agent B will see it and respond when ready. You can also respond on B's behalf if needed.

**Q: Can I see all cross-agent requests in one place?**
A: Not currently in the UI. Requests appear in the target agent's thread. You can query the `cross_thread_requests` table in the database for a global view.

**Q: How long should I wait for an agent to respond to a request?**
A: Use the `timeout` parameter in `request_update_from_thread`. Typical values:
- 60 seconds for quick status updates
- 300 seconds (5 min) for deliverables
- 600 seconds (10 min) for complex questions

### UI & Columns

**Q: How do I collapse all agents at once?**
A: Currently, you collapse individually. Click the [×] button on each expanded agent header. A "Collapse All" button may be added in a future update.

**Q: Can I rearrange agent columns?**
A: Not currently. Agents are in fixed order (Alpha → Zulu, 1 → 26). Rearrangement may be added later.

**Q: What's the difference between collapsing and removing an agent?**
A: 
- **Collapse**: Agent column becomes vertical bar. Thread remains active. Click to re-expand.
- **Remove**: Agent column deleted from UI. Thread unassigned (but not deleted). Agent can be re-added later.

**Q: Can I view an agent on mobile?**
A: The Multi-Agent Command Centre is optimized for desktop/laptop. Mobile support is limited due to horizontal scrolling requirement.

### Troubleshooting

**Q: I assigned work to an agent, but nothing happened. Why?**
A: Check:
1. Is `auto_trigger` set to `True`? (If `False`, agent waits for you to say "proceed")
2. Is `open_ui` set to `True`? (If `False`, UI won't update)
3. Did the tool call succeed? (Check AI Prime's response for errors)
4. Is the agent column expanded? (Click to expand if collapsed)

**Q: Agent stopped responding mid-conversation. What do I do?**
A: 
1. Check if agent is still processing (wait 30 seconds)
2. Send a follow-up message: "Please continue"
3. If stuck, click the agent menu → "Reset Agent"
4. If still broken, assign work to a different agent

**Q: Cross-agent request isn't being answered. Why?**
A: 
1. Check if target agent has seen the request (open their column)
2. Verify request appears in target's message thread
3. Check priority level - maybe it's low priority and agent is busy
4. Respond manually on behalf of target agent if urgent

**Q: Can I undo an agent assignment?**
A: Not directly "undo", but you can:
1. Clear the agent's thread (removes messages)
2. Unassign thread from agent
3. Reassign agent to different work
4. Or simply ignore the old work and start fresh

---

## AI Agent Instructions

*This section is specifically for AI assistants (like AI Prime) that orchestrate multi-agent work distribution.*

### AI Agent Core Responsibilities

When users request multi-agent coordination, you must:

1. ✅ **Analyze project structure** - Identify parallelizable components
2. ✅ **Propose agent distribution** - Suggest which agents handle what
3. ✅ **Call coordination tools** - Execute `assign_and_activate_agent_with_slugs`
4. ✅ **Monitor progress** - Check on agent threads periodically
5. ✅ **Facilitate communication** - Orchestrate cross-agent requests
6. ✅ **Consolidate results** - Gather outputs from all agents

### Decision Tree: When to Use Multi-Agent

**Evaluate the user's request:**

```
Is the project large? (Yes/No)
├─ No → Use single agent (AI Prime or one NATO agent)
└─ Yes → Can it be parallelized? (Yes/No)
    ├─ No → Use single agent with sequential workflow
    └─ Yes → Use multi-agent coordination
        └─ How many components? (2-26)
            └─ Assign one agent per component
```

**Size Heuristics:**

- **Small**: < 500 lines of code, < 1 day work → Single agent
- **Medium**: 500-2000 lines, 1-3 days → 2-3 agents
- **Large**: 2000-5000 lines, 1-2 weeks → 3-5 agents
- **Enterprise**: 5000+ lines, multi-week → 5-10 agents

**Parallelization Heuristics:**

✅ **Good for multi-agent:**
- Frontend + Backend + Database (3 components)
- Multiple microservices
- Multi-stage pipelines (data collection → processing → analysis)
- Specialized audits (security, performance, code quality)
- Content generation (blog, social, email, video)

❌ **Not suitable for multi-agent:**
- Single feature within one codebase
- Highly coupled code (everything depends on everything)
- Sequential steps that must happen in order
- Small scripts or utilities

### Template: Proposing Multi-Agent Distribution

When user says: "Build an e-commerce platform"

```markdown
**AI Response:**

This is a great candidate for multi-agent coordination! Here's my proposed distribution:

**Recommended Agents: 3**

🤖 **Alpha - Frontend Development**
- React components (product listing, cart, checkout)
- Routing and navigation
- State management (Redux)
- Responsive UI with Tailwind CSS
- **Estimated time**: 3-4 days

🤖 **Bravo - Backend API**
- Express.js REST API
- JWT authentication
- Product/cart/order endpoints
- Stripe payment integration
- **Estimated time**: 3-4 days

🤖 **Charlie - Database Design**
- PostgreSQL schema
- Tables: users, products, orders, cart_items
- Indexes and foreign keys
- Migration scripts and seed data
- **Estimated time**: 2-3 days

**Benefits of this approach:**
✅ All 3 components built in parallel (vs 10 days sequential)
✅ Each agent specializes in one area
✅ Clear interfaces between components
✅ Easier testing and integration

**Resources:**
- All agents will be linked to Synergy project: "E-Commerce MVP"
- Shared documentation: Brand guidelines, API specs

Would you like me to proceed with this distribution?
```

### Template: Executing Multi-Agent Distribution

After user approves:

```python
# Agent 1: Frontend
assign_and_activate_agent_with_slugs(
    target_agent='Alpha',
    thread_title='E-Commerce Frontend (React)',
    instructions='''[Detailed frontend instructions]
    
    Your role: Build the React frontend.
    Dependencies: Backend API (Bravo will provide).
    Deliverables: Component library, page layouts, state management.
    Timeline: 3-4 days.
    
    Begin with project structure and component planning.''',
    slugs={
        'synergy_session_id': 'sess_ecommerce_mvp',
        'internal_doc_slug': 'doc_brand_guidelines'
    },
    auto_trigger=True,
    open_ui=True
)

# Agent 2: Backend
assign_and_activate_agent_with_slugs(
    target_agent='Bravo',
    thread_title='E-Commerce Backend API (Express)',
    instructions='''[Detailed backend instructions]
    
    Your role: Build the Express.js backend.
    Dependencies: Database schema (Charlie will provide).
    Deliverables: API endpoints, authentication, payment integration.
    Timeline: 3-4 days.
    
    Begin with API structure and endpoint planning.''',
    slugs={
        'synergy_session_id': 'sess_ecommerce_mvp'
    },
    auto_trigger=True,
    open_ui=True
)

# Agent 3: Database
assign_and_activate_agent_with_slugs(
    target_agent='Charlie',
    thread_title='E-Commerce Database (PostgreSQL)',
    instructions='''[Detailed database instructions]
    
    Your role: Design the PostgreSQL database.
    Dependencies: None (you start first).
    Deliverables: Schema, migrations, seed data.
    Timeline: 2-3 days.
    
    Begin with entity relationship diagram and table design.''',
    slugs={
        'synergy_session_id': 'sess_ecommerce_mvp'
    },
    auto_trigger=True,
    open_ui=True
)
```

**Then report back to user:**

```markdown
✅ **Multi-agent distribution complete!**

**Agents Assigned:**
- 🤖 Alpha → Frontend (React)
- 🤖 Bravo → Backend API (Express)
- 🤖 Charlie → Database (PostgreSQL)

**Status:**
- Multi-Agent tab has opened automatically
- All 3 agents have received their instructions
- Each agent has started working on their component
- All agents are linked to Synergy project: "E-Commerce MVP"

**Next Steps:**
1. Monitor agent progress (check each column periodically)
2. I'll coordinate cross-agent communication (API details, DB schema sharing)
3. Integration phase will begin after all components are ready (~Day 4)

**You can:**
- View agent progress by clicking each agent column
- Ask me for status updates: "What's the status of all agents?"
- Provide feedback directly in each agent's thread
```

### Template: Cross-Agent Coordination

**When Agent A needs info from Agent B:**

```python
# Orchestrate the request
request_update_from_thread(
    target_thread_id='Bravo',
    request_message='''Alpha (frontend) needs API integration details:

    Required information:
    1. API base URL (dev environment)
    2. Authentication method (JWT format, header name)
    3. Complete endpoint list with request/response examples
    4. Error codes and handling
    5. Rate limiting details
    
    Priority: High (Alpha is blocked without this)
    Deadline: End of day today
    
    Please provide comprehensive documentation.''',
    request_type='deliverable',
    priority='high',
    wait_for_response=True,
    timeout=600
)
```

**Then notify user:**

```markdown
📨 **Cross-agent request sent**

**From:** Alpha (Frontend)  
**To:** Bravo (Backend)  
**Request:** API integration documentation  
**Priority:** High  

I've requested that Bravo provide Alpha with complete API details. I'm waiting for Bravo's response (timeout: 10 minutes).

I'll update you when Bravo responds.
```

### Template: Status Check Across All Agents

When user asks: "What's the status of all agents?"

```markdown
📊 **Multi-Agent Status Report**

**🤖 Alpha - Frontend (React)**
- Status: In progress (65% complete)
- Latest: Completed product listing component
- Current: Working on shopping cart UI
- Next: Checkout flow
- Blocked: No

**🤖 Bravo - Backend API (Express)**
- Status: In progress (80% complete)
- Latest: All CRUD endpoints tested
- Current: Integrating Stripe payment
- Next: API documentation
- Blocked: No

**🤖 Charlie - Database (PostgreSQL)**
- Status: Complete ✅
- Latest: All tables created, seed data loaded
- Deliverables: schema.sql, migrations/, seed_data.sql
- Status: Ready for integration

**Overall Progress: 75% complete**

**Estimated completion: 2 days**

**Next milestones:**
1. Alpha finishes checkout UI (tomorrow AM)
2. Bravo completes Stripe integration (tomorrow PM)
3. Integration testing begins (Day 4)
```

### Safety Rules

**NEVER:**
- ❌ Assign agent work without user approval (always propose first)
- ❌ Distribute work that's too coupled (must be parallelizable)
- ❌ Overload a single agent with multiple unrelated tasks
- ❌ Forget to link agents to Synergy/workflows (shared context crucial)
- ❌ Let agents work in isolation without coordination

**ALWAYS:**
- ✅ Propose agent distribution before executing
- ✅ Explain why multi-agent is appropriate (or not)
- ✅ Link all agents to same Synergy project (if applicable)
- ✅ Monitor progress and report back to user
- ✅ Facilitate cross-agent communication when needed
- ✅ Consolidate results from all agents

---

## Quick Reference Card

### Agent Identifiers

| NATO Name | Location | Number | Use |
|-----------|----------|--------|-----|
| Alpha | agent-1 | 1 | Frontend, UI |
| Bravo | agent-2 | 2 | Backend, APIs |
| Charlie | agent-3 | 3 | Database |
| Delta | agent-4 | 4 | Testing |
| Echo | agent-5 | 5 | Documentation |
| ... | ... | ... | ... |
| Zulu | agent-26 | 26 | i18n, timezones |

### Primary Tool: assign_and_activate_agent_with_slugs

```python
assign_and_activate_agent_with_slugs(
    target_agent='Alpha',        # NATO name, agent-N, or N
    thread_title='Descriptive Title',
    instructions='Detailed task instructions...',
    slugs={                      # Optional resource links
        'workflow_slug': 'wf_xxx',
        'internal_doc_slug': 'doc_xxx',
        'synergy_session_id': 'sess_xxx'
    },
    auto_trigger=True,           # Start immediately
    open_ui=True                 # Auto-open UI
)
```

### Cross-Agent Request

```python
request_update_from_thread(
    target_thread_id='Bravo',
    request_message='What is the status?',
    request_type='status_update',  # or deliverable, question, etc.
    priority='high',                # low, medium, high, urgent
    wait_for_response=True,
    timeout=300
)
```

### Cross-Agent Response

```python
respond_to_cross_thread_request(
    request_id='req_abc123',
    response_message='Here is the information...'
)
```

### Column Controls

| Action | Method |
|--------|--------|
| Expand collapsed agent | Click vertical bar |
| Collapse expanded agent | Click [×] button |
| Toggle width (400px/600px) | Click [↔️] button |
| Open menu | Click [⚙️] button |
| Switch thread | Thread info → Switch Thread |
| Clear messages | Menu → Clear |

### Priority Levels

| Priority | Color | Use When |
|----------|-------|----------|
| Low | 🔵 Blue | Optional, FYI |
| Medium | 🟡 Yellow | Standard request |
| High | 🟠 Orange | Blocking work |
| Urgent | 🔴 Red | Critical, immediate |

### Request Types

- `status_update` - Progress check
- `deliverable` - Need output/files
- `question` - How does X work?
- `coordination` - Timeline/planning
- `resource_request` - Need file/doc/key

---

**End of Complete Guide**

*For additional help with multi-agent coordination, consult the Synergy Dashboard guide for project-level management and the Automation Workflows guide for task sequences.*

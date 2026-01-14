# Synergy Dashboard & Sidebar - Complete User Guide

**Version:** 1.0  
**Last Updated:** November 22, 2025  
**Audience:** End Users, Power Users, AI Agents

---

## 📋 Table of Contents

1. [What is the Synergy Dashboard?](#what-is-the-synergy-dashboard)
2. [Getting Started](#getting-started)
3. [Understanding the Interface](#understanding-the-interface)
4. [Creating and Managing Sessions](#creating-and-managing-sessions)
5. [Working with Milestones](#working-with-milestones)
6. [Thread Linking](#thread-linking)
7. [Synergy Sidebar](#synergy-sidebar)
8. [AI Collaboration with Synergy](#ai-collaboration-with-synergy)
9. [Best Practices](#best-practices)
10. [Frequently Asked Questions](#frequently-asked-questions)
11. [AI Agent Instructions](#ai-agent-instructions)

---

## What is the Synergy Dashboard?

The Synergy Dashboard is a **visual Kanban-style project management board** designed for complex, multi-step tasks that require collaboration between you, AI agents, and your team. Think of it as a **mission control center** for projects that span multiple conversations, platforms, and files.

### Key Features

- 🎯 **Visual Project Tracking** - See all your projects in a Kanban board
- 📊 **Milestone System** - Break projects into trackable stages
- 🔗 **Thread Linking** - Connect AI conversations to project cards
- 👥 **Multi-Agent Coordination** - Assign different AI agents to project tasks
- 📝 **Document Creation** - Create and store project documents directly in Synergy
- ⏱️ **Real-Time Updates** - Changes sync instantly across all open tabs
- 📱 **Sidebar Access** - Quick access via collapsible sidebar

### When to Use Synergy?

Use Synergy when your project needs:

✅ **Multi-Round Work** - Tasks requiring multiple sessions over days/weeks
✅ **Multiple AI Agents** - When different specialized agents need context
✅ **Cross-Platform Integration** - Work spanning Google Workspace, Microsoft 365, etc.
✅ **Multiple Files** - Projects touching many files/documents
✅ **Team Collaboration** - Projects with multiple people involved
✅ **Context Preservation** - Important project history you'll reference later

### When NOT to Use Synergy?

Skip Synergy for:

❌ Simple one-off questions
❌ Single-session tasks
❌ Quick file edits
❌ Basic information lookups
❌ Tasks completed in < 10 minutes

---

## Getting Started

### Accessing the Synergy Dashboard

**Method 1: Dashboard Icon (Full View)**
1. Click the **purple Synergy icon** (📊) in the left sidebar
2. The full Kanban dashboard opens in the main view
3. You'll see columns: Backlog, In Progress, Review, Done

**Method 2: Sidebar (Quick Access)**
1. Click the **Synergy tab** in the collapsible sidebar (right edge of screen)
2. The 450px sidebar slides out showing your active sessions
3. Click any session card to view details
4. Click "Open Dashboard" to see the full board

### First Time Setup

When you first open Synergy, you'll see:

- Empty Kanban board with 4 columns
- "Create New Session" button in each column
- Sidebar with no sessions (if opened)
- Welcome message explaining the interface

**Your first Synergy session:**
1. Click "Create New Session" in the **Backlog** column
2. Fill out the session details:
   - **Title** - Brief project name (e.g., "Email Automation Setup")
   - **Description** - What the project is about (2-3 sentences)
   - **Priority** - Low/Medium/High (default: Medium)
   - **Tags** - Keywords for filtering (e.g., "automation, email, google")
3. Click "Create"
4. Your first session card appears in Backlog!

---

## Understanding the Interface

### Kanban Board Layout

The Synergy Dashboard uses a **4-column Kanban board**:

```
┌─────────────┬─────────────┬─────────────┬─────────────┐
│   BACKLOG   │ IN PROGRESS │   REVIEW    │    DONE     │
├─────────────┼─────────────┼─────────────┼─────────────┤
│  Planned    │   Active    │  Testing/   │  Completed  │
│  Not Yet    │   Working   │  Checking   │  Archived   │
│  Started    │   On It     │  QA         │  Finished   │
└─────────────┴─────────────┴─────────────┴─────────────┘
```

**Column Meanings:**

1. **Backlog** 📋
   - Projects you plan to do
   - Ideas and proposals
   - Not yet started
   - No active work happening

2. **In Progress** 🔄
   - Currently active projects
   - AI is working on these
   - Requires your attention
   - Daily/weekly work

3. **Review** 👀
   - Needs checking/testing
   - Waiting for approval
   - QA/validation phase
   - Almost done, needs review

4. **Done** ✅
   - Completed projects
   - Archived work
   - Reference material
   - Success stories

### Session Card Anatomy

Each Synergy session card shows:

```
┌─────────────────────────────────────────┐
│ 🟢 PROJECT TITLE                        │  ← Priority color + title
├─────────────────────────────────────────┤
│ Brief description of what this          │  ← Short description
│ project is about and its goals          │
├─────────────────────────────────────────┤
│ 📊 Milestones: 3/5 complete (60%)      │  ← Progress bar
├─────────────────────────────────────────┤
│ 🔗 Linked Threads: 2                    │  ← Connected AI conversations
│ 👥 Agents: Prime, Agent-1              │  ← Assigned AI agents
│ 🏷️ Tags: automation, email             │  ← Keywords
├─────────────────────────────────────────┤
│ 📅 Last Updated: 2 hours ago            │  ← Activity timestamp
│ ⚙️ [Edit] [Archive] [Delete]           │  ← Action buttons
└─────────────────────────────────────────┘
```

**Priority Colors:**
- 🔴 **Red** - High priority (urgent, critical)
- 🟡 **Yellow** - Medium priority (important, normal)
- 🟢 **Green** - Low priority (nice-to-have, later)

**Card Status Indicators:**
- ⏸️ **Paused icon** - Project temporarily on hold
- 🔥 **Fire icon** - Recently active (updated in last hour)
- 📌 **Pin icon** - Pinned to sidebar for quick access
- 🔒 **Lock icon** - Read-only (archived/completed)

### Session Details Popup

Click any session card to open the **detailed view popup**:

**Popup Contains:**
- Full title and description
- Detailed milestone list with progress
- Linked threads with agent badges
- Tags and metadata
- Activity log
- Edit/delete/archive options
- Document creation tools
- Agent assignment controls

---

## Creating and Managing Sessions

### Creating a New Session

**Method 1: Click "Create New Session" Button**
1. Click the button in any Kanban column
2. Form appears with fields:
   - **Title** (required) - Max 100 characters
   - **Description** (optional) - Max 500 characters
   - **Priority** - Low/Medium/High dropdown
   - **Tags** - Comma-separated keywords
   - **Column** - Pre-filled with column you clicked
3. Fill out details
4. Click "Create"

**Method 2: Ask AI to Create It**
```
User: "Create a Synergy session for website redesign project"

AI creates session with:
- Title: "Website Redesign Project"
- Description: Auto-generated from context
- Priority: Medium (default)
- Tags: web, design, frontend
- Initial milestones: Project phases
```

**Method 3: Drag Thread to Dashboard**
1. Open AI conversation (thread)
2. Drag thread card from sidebar
3. Drop onto Kanban column
4. AI auto-creates Synergy session from thread context
5. Thread is automatically linked to new session

### Editing a Session

**Method 1: Edit Button in Card**
1. Click **⚙️ Edit** button on session card
2. Edit form appears with current values
3. Modify any field
4. Click "Save Changes"

**Method 2: Click Card to Open Popup, Then Edit**
1. Click session card to open details
2. Click "Edit Session" button in popup header
3. Edit inline or in full form
4. Changes save automatically or click "Save"

**Method 3: Ask AI to Update**
```
User: "[session-id] Change priority to high and add 'urgent' tag"

AI updates:
- Priority: Medium → High
- Tags: [...existing, 'urgent']
- Confirms changes made
```

### Moving Sessions Between Columns

**Method 1: Drag and Drop**
1. Click and hold session card
2. Drag to target column
3. Drop in position
4. Card moves, status updates

**Method 2: Status Dropdown**
1. Click session card to open popup
2. Find "Status" dropdown
3. Select new status (Backlog/In Progress/Review/Done)
4. Card moves to corresponding column

**Method 3: Ask AI**
```
User: "Move website project to In Progress"

AI finds session and updates status
```

### Archiving vs Deleting

**Archive a Session:**
- Keeps all data and history
- Moves to "Done" column
- Marked as read-only
- Can be restored later
- Good for completed projects

**Delete a Session:**
- Permanently removes session
- Cannot be undone
- Unlinks all threads (threads remain, but lose Synergy link)
- Deletes all milestones
- Use for mistakes or test data

---

## Working with Milestones

Milestones are **trackable stages** within a Synergy session. They break large projects into manageable chunks.

### Milestone Structure

Each milestone has:

```
┌──────────────────────────────────────────┐
│ ✅ Milestone 1: Setup Development Env   │  ← Completed
│    Status: DONE | Due: Nov 20, 2025     │
│    Description: Install tools and deps   │
│    📎 Deliverables:                      │
│       • package.json created             │
│       • Docker configured                │
├──────────────────────────────────────────┤
│ 🔄 Milestone 2: Build API Endpoints     │  ← In Progress
│    Status: IN_PROGRESS | Due: Nov 25    │
│    Description: Create REST API routes   │
│    📎 Deliverables:                      │
│       • /api/users endpoint              │
│       • /api/posts endpoint              │
├──────────────────────────────────────────┤
│ ⏸️ Milestone 3: Frontend Integration    │  ← Not Started
│    Status: NOT_STARTED | Due: Dec 1     │
│    Description: Connect UI to backend    │
│    📎 Deliverables:                      │
│       • Login page wired up              │
│       • Dashboard displays data          │
└──────────────────────────────────────────┘
```

### Creating Milestones

**Method 1: During Session Creation**
```
When creating a session, AI can auto-generate milestones:

User: "Create a Synergy session for building a contact form"

AI creates session with default milestones:
1. Design form layout (NOT_STARTED)
2. Implement HTML/CSS (NOT_STARTED)
3. Add validation logic (NOT_STARTED)
4. Connect to backend API (NOT_STARTED)
5. Test and deploy (NOT_STARTED)
```

**Method 2: Add After Session Created**
1. Open session details popup
2. Scroll to "Milestones" section
3. Click "+ Add Milestone"
4. Fill out:
   - **Name** - Milestone title
   - **Description** - What needs to be done
   - **Status** - NOT_STARTED/IN_PROGRESS/DONE/BLOCKED
   - **Due Date** - Target completion date
   - **Deliverables** - Expected outputs (bullet list)
5. Click "Add"

**Method 3: Ask AI**
```
User: "[session-id] Add a milestone for database migration"

AI creates:
- Name: "Database Migration"
- Description: "Migrate data from old schema to new"
- Status: NOT_STARTED
- Adds to session
```

### Updating Milestone Progress

**Method 1: Status Dropdown**
1. Open session details
2. Find milestone in list
3. Click status dropdown
4. Select new status:
   - **NOT_STARTED** - Haven't begun
   - **IN_PROGRESS** - Currently working
   - **DONE** - Completed
   - **BLOCKED** - Waiting on something

**Method 2: Check Off Deliverables**
1. Each milestone has checklist of deliverables
2. Click checkbox next to deliverable when done
3. Progress percentage updates automatically
4. When all deliverables checked, milestone auto-marks DONE

**Method 3: AI Updates Progress**
```
AI automatically updates milestones when working:

AI: "I've completed the API endpoints. Marking Milestone 2 as DONE."

[AI calls synergy_update_session]
- Milestone 2 status: IN_PROGRESS → DONE
- Overall progress: 40% → 60%
- Last active timestamp updated
```

### Milestone Best Practices

✅ **DO:**
- Keep milestones focused (1-3 days of work each)
- Use clear, action-oriented names ("Build X", "Test Y")
- Include 2-5 deliverables per milestone
- Set realistic due dates
- Update status as you progress

❌ **DON'T:**
- Create massive milestones (> 1 week of work)
- Use vague names ("Do stuff", "Work on project")
- Skip deliverables (harder to track progress)
- Ignore due dates (they help prioritize)
- Forget to mark milestones DONE (satisfying!)

---

## Thread Linking

One of Synergy's most powerful features is **linking AI conversation threads to project sessions**. This connects your chat history with project context.

### What is Thread Linking?

**Thread Linking means:**
- An AI conversation (thread) is associated with a Synergy project (session)
- The thread shows a Synergy badge in the sidebar
- The Synergy card shows linked threads in its details
- AI can reference Synergy context when responding in the thread
- Both stay in sync (bidirectional linking)

**Why Link Threads?**
- **Context Preservation** - AI remembers project goals across conversations
- **Multi-Session Projects** - Continue work over days/weeks
- **Team Visibility** - Everyone sees which threads relate to which projects
- **Agent Coordination** - Different agents can contribute to same project
- **History Tracking** - See all conversations about a project

### How Thread Linking Works

**Bidirectional Sync:**

```
┌─────────────────┐         ┌──────────────────┐
│   THREAD        │ ←─────→ │  SYNERGY SESSION │
│  (Conversation) │         │   (Project)      │
└─────────────────┘         └──────────────────┘
     ↓                              ↓
synergy_card_id          thread_ids: [...]
points to session        array of threads
```

**When you link a thread:**
1. **Thread** gets `synergy_card_id` field (points to session)
2. **Session** adds thread to `thread_ids` array (list of linked threads)
3. Both databases update instantly
4. UI refreshes showing the connection

### Linking Threads to Synergy

**Method 1: Drag and Drop**
1. Open Synergy Dashboard (full view)
2. Find thread in left sidebar (AI Agents tab)
3. Drag thread card
4. Drop onto Synergy session card
5. Badge appears on thread showing Synergy link

**Method 2: Right-Click Thread**
1. Right-click thread in sidebar
2. Select "Link to Synergy Session"
3. Modal shows list of Synergy sessions
4. Click session to link
5. Confirmation appears

**Method 3: Link from Synergy Card**
1. Open session details popup
2. Scroll to "Linked Threads" section
3. Click "+ Link Thread"
4. Select thread from dropdown
5. Thread added to session

**Method 4: Ask AI**
```
User: "Link this thread to the website redesign project"

AI:
1. Searches for Synergy session matching "website redesign"
2. Links current thread to that session
3. Confirms: "Linked this conversation to [Session Name]"
```

### Unlinking Threads

**Method 1: Unlink Button on Thread Badge**
1. Find thread with Synergy badge in sidebar
2. Hover over badge
3. Click the **× (unlink)** icon
4. Confirm unlink
5. Badge disappears from thread

**Method 2: Remove from Synergy Card**
1. Open session details popup
2. Scroll to "Linked Threads" section
3. Find thread in list
4. Click **× Remove** button
5. Thread unlinked (thread remains, just no longer connected)

**Method 3: Ask AI**
```
User: "Unlink this thread from Synergy"

AI:
1. Removes synergy_card_id from thread
2. Removes thread from session's thread_ids
3. Confirms: "Unlinked thread from [Session Name]"
```

### Viewing Linked Threads

**From Thread Sidebar:**
- Threads with Synergy links show an orange **🔗 badge**
- Badge displays session name (truncated)
- Click badge to open Synergy session details
- Hover for full session name tooltip

**From Synergy Card:**
1. Click session card to open details
2. "Linked Threads" section shows all connected threads
3. Each thread displays:
   - Thread title/name
   - Agent assignment (Prime, Agent-1, etc.)
   - Last updated timestamp
   - Message count
4. Click thread to open it in AI chat

**Example Display:**
```
🔗 Linked Threads (3)
┌─────────────────────────────────────┐
│ 🤖 Prime: "Email automation setup"  │ 
│    12 messages · 2 hours ago        │
├─────────────────────────────────────┤
│ 🤖 Agent-1: "Database schema design"│
│    8 messages · 1 day ago           │
├─────────────────────────────────────┤
│ 🤖 Prime: "Frontend component work" │
│    5 messages · 3 hours ago         │
└─────────────────────────────────────┘
```

### Thread Badges in Sidebar

When a thread is linked to Synergy, it displays a badge:

```
Thread Card:
┌────────────────────────────────────┐
│ Thread Title                       │
│ 12 messages · Updated 2h ago       │
│                                    │
│ 🔗 Website Redesign ×              │  ← Synergy Badge
└────────────────────────────────────┘
```

**Badge Features:**
- **🔗 Icon** - Indicates Synergy link
- **Session Name** - Truncated session title
- **× Unlink** - Click to remove link
- **Click Badge** - Opens Synergy session details
- **Tooltip** - Hover for full session name, description, priority

### Multi-Thread Projects

You can link **multiple threads** to a single Synergy session:

**Use Cases:**
1. **Long-running projects** - New conversation each week
2. **Multi-agent projects** - Each agent has their own thread
3. **Different phases** - Thread per milestone
4. **Parallel work** - Multiple people/agents working simultaneously

**Example:**
```
Synergy Session: "E-Commerce Redesign"
├─ Thread 1 (Prime): Homepage layout discussion
├─ Thread 2 (Agent-1): Database schema design  
├─ Thread 3 (Prime): Product page components
├─ Thread 4 (Agent-2): Payment integration
└─ Thread 5 (Prime): Testing and deployment
```

All 5 threads share the same Synergy context, but each focuses on different aspects of the project.

---

## Synergy Sidebar

The **Synergy Sidebar** provides quick access to your active sessions without leaving the AI chat view.

### Opening the Sidebar

**Location:** Right edge of screen (next to AI Agent columns)

**How to Open:**
1. Click the **Synergy tab** on the right sidebar toggle
2. The 450px sidebar slides out from the right
3. Shows your active Synergy sessions

**Sidebar Tabs:**
- **List View** - All sessions organized by column
- **Pinned View** - Only pinned sessions (your favorites)

### Sidebar Features

**List View:**
```
┌──────────────────────────────────────┐
│ SYNERGY SESSIONS           [Pin All] │
│ ──────────────────────────────────── │
│ 🔍 Search sessions...                │
│ 📊 Filter: [All] [Status] [Priority] │
│ ──────────────────────────────────── │
│                                      │
│ BACKLOG (2)                          │
│ ┌──────────────────────────────────┐ │
│ │ 🟡 Email Automation Setup        │ │
│ │ 📊 50% · 🔗 2 threads            │ │
│ │ 📅 Updated 3 hours ago     📌    │ │
│ └──────────────────────────────────┘ │
│ ┌──────────────────────────────────┐ │
│ │ 🟢 Database Migration            │ │
│ │ 📊 25% · 🔗 1 thread             │ │
│ │ 📅 Updated 1 day ago       📌    │ │
│ └──────────────────────────────────┘ │
│                                      │
│ IN PROGRESS (3)                      │
│ ┌──────────────────────────────────┐ │
│ │ 🔴 Website Redesign              │ │
│ │ 📊 75% · 🔗 5 threads            │ │
│ │ 📅 Updated 10 minutes ago  📌    │ │
│ └──────────────────────────────────┘ │
│ ...                                  │
└──────────────────────────────────────┘
```

**Pinned View:**
- Shows only sessions you've pinned with 📌 icon
- Sorted by most recently updated
- Quick access to your most important projects

### Sidebar Actions

**Click Session Card:**
- Opens session details popup overlay
- View milestones, threads, documents
- Edit or update session

**Click Pin Icon (📌):**
- Pins/unpins session
- Pinned sessions appear in "Pinned View" tab
- Stays pinned across sessions

**Click Thread Link (🔗):**
- Opens linked thread in AI chat
- Switches to appropriate agent column
- Loads thread conversation

**Search Box:**
- Type to filter sessions by title, description, tags
- Real-time filtering as you type
- Case-insensitive

**Filter Dropdown:**
- **By Status:** All, Backlog, In Progress, Review, Done
- **By Priority:** All, High, Medium, Low
- Combine filters (e.g., "High priority + In Progress")

### Sidebar vs Dashboard

**Use Sidebar When:**
- ✅ Working in AI chat, need quick Synergy reference
- ✅ Want to link current thread to session
- ✅ Checking project status while chatting
- ✅ Opening a specific linked thread

**Use Dashboard When:**
- ✅ Managing multiple projects at once
- ✅ Creating new sessions
- ✅ Dragging sessions between columns
- ✅ Viewing full project details
- ✅ Organizing and prioritizing work

---

## AI Collaboration with Synergy

### How AI Uses Synergy

AI agents can interact with Synergy to:

1. **Create sessions** - When you describe a complex project
2. **Update progress** - Mark milestones complete as work is done
3. **Link threads** - Automatically connect conversations to projects
4. **Create documents** - Generate project docs and store in Synergy
5. **Track tasks** - Add/complete milestones as work progresses
6. **Provide context** - Reference Synergy data when responding

### Asking AI to Create a Synergy Session

**Example Requests:**

**Simple:**
```
User: "Create a Synergy session for building a contact form"

AI Response:
I've created a Synergy session for you!

📊 **Session Created:**
- **Title:** Contact Form Development
- **Description:** Build a responsive contact form with validation and backend integration
- **Status:** Backlog
- **Priority:** Medium
- **Milestones:** 5 stages (Design, HTML/CSS, Validation, Backend, Testing)

🔗 This conversation is now linked to the session.

You can view it in:
- Synergy Dashboard → Backlog column
- Synergy Sidebar → Click the orange badge on this thread

Would you like me to start with the first milestone?
```

**Detailed:**
```
User: "I need a Synergy session for a multi-phase e-commerce project. We need to redesign the homepage, build a new product catalog, integrate with Stripe, and deploy to AWS. Make it high priority."

AI Response:
I've created a comprehensive Synergy session for your e-commerce project!

📊 **Session Created:**
- **Title:** E-Commerce Platform Redesign
- **Description:** Multi-phase project to modernize the entire e-commerce experience with new homepage, product catalog, payment integration, and AWS deployment
- **Status:** In Progress
- **Priority:** 🔴 High
- **Tags:** ecommerce, redesign, stripe, aws, frontend, backend

🎯 **Milestones (6 phases):**
1. ⏸️ **Phase 1: Homepage Redesign** (NOT_STARTED)
   - Deliverables: Wireframes, Mockups, Component library
   - Due: Dec 1, 2025

2. ⏸️ **Phase 2: Product Catalog** (NOT_STARTED)
   - Deliverables: Database schema, API endpoints, Product cards
   - Due: Dec 10, 2025

3. ⏸️ **Phase 3: Stripe Integration** (NOT_STARTED)
   - Deliverables: Payment flow, Webhook handlers, Receipt system
   - Due: Dec 15, 2025

4. ⏸️ **Phase 4: AWS Deployment** (NOT_STARTED)
   - Deliverables: EC2 setup, RDS config, Load balancer
   - Due: Dec 20, 2025

5. ⏸️ **Phase 5: Testing** (NOT_STARTED)
   - Deliverables: Unit tests, Integration tests, E2E tests
   - Due: Dec 25, 2025

6. ⏸️ **Phase 6: Production Launch** (NOT_STARTED)
   - Deliverables: Monitoring setup, Docs, Go-live checklist
   - Due: Dec 31, 2025

🔗 **This thread is now linked** to the session.

Shall I start with Phase 1 (Homepage Redesign)?
```

### AI Updating Synergy Progress

AI automatically updates Synergy as work progresses:

**Example Flow:**
```
User: "Build the homepage header component"

AI: "I'll create the header component for you."
[AI creates code, tests it, saves files]

AI: "✅ Header component complete! 

I've updated the Synergy session:
- Milestone 1: Homepage Redesign → 33% complete
- Deliverable 'Header component' → ✅ DONE
- Session last updated: just now

Next up: Hero section (Deliverable 2 of 3)"
```

**AI Milestone Updates:**
```
User: "Is the database schema done?"

AI: "Let me check the Synergy session..."
[AI calls synergy_get_session]

AI: "Yes! The database schema milestone is marked DONE (completed 2 days ago).

📊 Deliverables completed:
✅ User table schema
✅ Product table schema  
✅ Order table schema
✅ Migration scripts

The project is now 40% complete. Next milestone is 'API Endpoints'."
```

### AI Creating Documents in Synergy

AI can create project documents and store them in Synergy:

```
User: "Create a technical spec document for this project"

AI: "I'll create a comprehensive technical specification."
[AI calls synergy_smart_create_document]

AI: "✅ Technical Specification created!

📄 **Document Details:**
- **Type:** Google Doc
- **Title:** E-Commerce Redesign - Technical Specification
- **Location:** Stored in Synergy session
- **Sections:** 
  - Project Overview
  - Technical Architecture
  - Database Schema
  - API Design
  - Frontend Components
  - Security Considerations
  - Deployment Plan

🔗 **Access:**
- Click 'Documents' tab in Synergy session
- Document link: [Google Doc URL]

The document is now part of the project's permanent record."
```

### Common AI Synergy Commands

**Creation:**
- "Create a Synergy session for [project]"
- "Start a Synergy project called [name]"
- "I need a project board for [description]"

**Updating:**
- "Update Synergy with my progress"
- "Mark the [milestone] as complete"
- "Change priority to high"
- "Move to In Progress"

**Linking:**
- "Link this thread to [session name]"
- "Connect this conversation to Synergy"
- "Add this chat to the [project] session"

**Viewing:**
- "Show me my Synergy projects"
- "What's the status of [project]?"
- "List all milestones in [session]"
- "How much progress have we made?"

**Documents:**
- "Create a [doc type] in Synergy"
- "Generate a project plan document"
- "Make a spec doc for this feature"

### AI Synergy Best Practices

✅ **AI SHOULD:**
- Create Synergy sessions for multi-step projects (automatically)
- Update milestones as work is completed (real-time)
- Link threads when starting work on a Synergy project
- Reference Synergy context in responses ("As noted in the project spec...")
- Suggest creating Synergy when user describes complex work

❌ **AI SHOULD NOT:**
- Create Synergy for simple one-off tasks
- Delete sessions without explicit user permission
- Change priorities without asking
- Unlink threads unexpectedly
- Create duplicate sessions for the same project

---

## Best Practices

### Project Organization

**Naming Conventions:**
- ✅ Use descriptive, action-oriented titles
  - Good: "Email Automation Setup"
  - Good: "Customer Dashboard Redesign"
  - Bad: "Project 1"
  - Bad: "Work stuff"

**Descriptions:**
- ✅ Be specific about goals and scope
- ✅ Include key technologies/platforms
- ✅ Mention stakeholders or team members
- ❌ Don't leave blank
- ❌ Avoid vague statements like "Do the thing"

**Tags:**
- ✅ Use consistent tag vocabulary
  - Technical: `frontend`, `backend`, `api`, `database`
  - Platforms: `google`, `microsoft`, `slack`, `shopify`
  - Categories: `automation`, `redesign`, `migration`, `integration`
- ✅ 3-7 tags per session
- ❌ Don't over-tag (> 10 tags)
- ❌ Avoid duplicate/similar tags (`email` vs `emails`)

### Milestone Management

**Sizing:**
- ✅ Each milestone = 1-3 days of work
- ✅ Break large tasks into smaller milestones
- ❌ Don't create milestones larger than 1 week

**Ordering:**
- ✅ Order milestones chronologically (what happens first)
- ✅ Use dependencies (Milestone 2 depends on Milestone 1)
- ✅ Group related work together

**Deliverables:**
- ✅ List concrete outputs (files, documents, features)
- ✅ Make deliverables checkable (binary yes/no)
- ❌ Don't use vague deliverables ("Make progress", "Do work")

### Thread Linking Strategy

**When to Link:**
- ✅ When starting work on a Synergy project
- ✅ When creating a new thread for an existing project
- ✅ When continuing work from a previous session
- ✅ When multiple agents need shared context

**When NOT to Link:**
- ❌ Quick questions unrelated to the project
- ❌ General chit-chat
- ❌ One-off requests
- ❌ Temporary debugging sessions

**Multiple Threads:**
- ✅ Use separate threads for different milestones (focus)
- ✅ Create new thread when previous is cluttered (> 50 messages)
- ✅ Use different threads for different agents (clear ownership)

### Workflow Recommendations

**Weekly Review:**
1. Open Synergy Dashboard
2. Check "In Progress" column - still relevant?
3. Move completed projects to "Done"
4. Archive old "Done" projects (> 30 days)
5. Review "Backlog" - prioritize next work
6. Update milestone due dates if needed

**Daily Habits:**
1. Check pinned sessions in sidebar (morning)
2. Update progress as you work (real-time)
3. Link new threads to relevant sessions
4. Mark deliverables complete when done
5. Move sessions between columns as status changes

**Project Kickoff Checklist:**
1. ✅ Create Synergy session with clear title/description
2. ✅ Set appropriate priority (High/Medium/Low)
3. ✅ Add relevant tags
4. ✅ Define 3-7 milestones
5. ✅ Set milestone due dates
6. ✅ Link initial thread to session
7. ✅ Create any necessary documents (specs, plans)
8. ✅ Pin session if high priority

**Project Completion Checklist:**
1. ✅ Mark all milestones DONE
2. ✅ Verify all deliverables checked off
3. ✅ Move session to "Done" column
4. ✅ Review linked threads (any loose ends?)
5. ✅ Create completion document (if needed)
6. ✅ Archive after 7 days in "Done"

---

## Frequently Asked Questions

### General Questions

**Q: How many Synergy sessions can I create?**
A: No limit. However, we recommend archiving completed projects to keep the board manageable. Aim for < 20 active sessions at a time.

**Q: Can I share Synergy sessions with others?**
A: Currently, Synergy is per-user. Team collaboration features (shared sessions, permissions) are planned for a future release.

**Q: What happens to threads when I delete a Synergy session?**
A: Threads remain intact. The Synergy link is removed from the thread (badge disappears), but the conversation history is preserved.

**Q: Can I export Synergy data?**
A: Yes. Click session → "Export" → Choose format (JSON, CSV). Exports include milestones, linked threads, metadata.

### Thread Linking Questions

**Q: Can one thread be linked to multiple Synergy sessions?**
A: No. Each thread can only be linked to ONE Synergy session at a time. This keeps context clear. If you need multi-project context, create separate threads.

**Q: What happens when I link a thread that's already linked?**
A: The old link is replaced with the new link. You'll see a confirmation: "This thread is already linked to [Session A]. Switch to [Session B]?"

**Q: Can AI automatically link threads?**
A: Yes. When you start working on a Synergy project, AI will ask: "Should I link this thread to [Session Name]?" or auto-link if obvious from context.

**Q: How do I see ALL threads linked to a session?**
A: Open the session details popup → "Linked Threads" section shows all connected threads with agent badges and timestamps.

### Milestone Questions

**Q: Can I reorder milestones?**
A: Yes. Open session details → Drag milestone handles to reorder. Changes save automatically.

**Q: What's the difference between milestone status and session status?**
A: 
- **Milestone status** = Progress of individual stage (NOT_STARTED/IN_PROGRESS/DONE/BLOCKED)
- **Session status** = Overall project stage (Backlog/In Progress/Review/Done)

**Q: Can milestones have sub-tasks?**
A: Yes, via deliverables. Each milestone can have multiple deliverable checkboxes. For complex milestones, consider creating a separate session instead.

**Q: What happens if I skip a milestone?**
A: Nothing enforced. Milestones are guidance, not requirements. You can complete them in any order or skip entirely.

### Sidebar Questions

**Q: Can I customize sidebar width?**
A: The sidebar is fixed at 450px (matches Automations sidebar). Customizable width is a planned feature.

**Q: Why don't I see all my sessions in the sidebar?**
A: Check filters! The sidebar respects filters (status, priority, search). Reset filters to see all sessions.

**Q: Can I have sidebar open while using AI chat?**
A: Yes! The sidebar overlays on the right side without blocking the chat. You can interact with both simultaneously.

**Q: What's the difference between pinning and starring a session?**
A: "Pinning" is the only feature. Pinned sessions appear in the "Pinned View" tab for quick access. (Note: "Starring" is not currently implemented.)

### Troubleshooting Questions

**Q: Why isn't my session appearing on the dashboard?**
A: Check:
1. Did it save? (Refresh the page)
2. Is it in a different column than expected?
3. Are filters hiding it? (Reset filters)
4. Try searching for it by name

**Q: Why did my thread's Synergy badge disappear?**
A: Possible causes:
- The Synergy session was deleted
- Thread was unlinked (intentionally or by AI)
- Data sync issue (refresh page)

**Q: Why can't I drag sessions between columns?**
A: Ensure:
1. You're on the full dashboard (not sidebar)
2. Session is not archived/read-only
3. Browser supports drag-and-drop (try different browser)
4. No JS errors (check browser console)

**Q: Why isn't AI updating my Synergy session?**
A: Check:
1. Is the thread linked to the session? (AI needs the link)
2. Did you give AI permission? (Some updates require approval)
3. Is the session active? (AI can't update archived sessions)
4. Check AI's response - did it encounter an error?

---

## AI Agent Instructions

*This section is specifically for AI assistants helping users with Synergy.*

### AI Agent Core Responsibilities

When a user works with Synergy, you must:

1. ✅ **Recognize Synergy contexts** - Detect when user needs project management
2. ✅ **Suggest Synergy proactively** - Offer to create session for complex work
3. ✅ **Create sessions intelligently** - Auto-generate milestones based on project scope
4. ✅ **Update progress automatically** - Mark milestones complete as work is done
5. ✅ **Link threads logically** - Connect conversations to relevant sessions
6. ✅ **Reference Synergy context** - Use session data when responding
7. ✅ **Guide users** - Explain Synergy features when they're new
8. ✅ **Keep Synergy current** - Update sessions, don't let data become stale

### AI Tool Selection Decision Tree

#### STEP 1: Should I suggest Synergy?

**Signals that Synergy is appropriate:**
- User describes multi-step project (> 3 major tasks)
- Work will span multiple days/weeks
- Requires coordination across multiple files/platforms
- User mentions "project", "plan", "roadmap", "phases"
- Previous similar work exists (continue in Synergy)

**Signals that Synergy is NOT needed:**
- Single, simple request
- Quick question or lookup
- One-file edit
- Task completable in < 10 minutes
- User explicitly says "quick question"

#### STEP 2: What Synergy action is needed?

**User says:** "Create a project for [description]"
**AI action:** `synergy_smart_project_tracker` (create new session)

**User says:** "Update [session] with progress"
**AI action:** `synergy_update_session` (update milestones/status)

**User says:** "Show me my projects"
**AI action:** `synergy_list_sessions` (retrieve all sessions)

**User says:** "What's the status of [project]?"
**AI action:** `synergy_get_session` (get session details)

**User says:** "Link this thread to [project]"
**AI action:** Link via ThreadManager + update session thread_ids

**User says:** "Create a [doc] for this project"
**AI action:** `synergy_smart_create_document` (create and store doc)

#### STEP 3: Execute and confirm

After using Synergy tools:
1. ✅ Confirm what was created/updated
2. ✅ Show user where to find it (Dashboard, Sidebar)
3. ✅ Explain what happens next
4. ✅ Ask if they want additional actions

### AI Response Templates

#### Template: Creating Synergy Session

````markdown
I've created a Synergy session to help track this project!

📊 **Session Created:**
- **Title:** [Project Title]
- **Description:** [Brief description]
- **Status:** [Backlog/In Progress/Review/Done]
- **Priority:** [🔴 High / 🟡 Medium / 🟢 Low]
- **Tags:** [tag1, tag2, tag3]

🎯 **Milestones ([X] phases):**
1. ⏸️ **[Milestone 1 Name]** (NOT_STARTED)
   - Due: [Date]
   - Deliverables: [List of outputs]
   
2. ⏸️ **[Milestone 2 Name]** (NOT_STARTED)
   - Due: [Date]
   - Deliverables: [List of outputs]

[... more milestones ...]

🔗 **This conversation is now linked** to the session.

📍 **Where to find it:**
- **Dashboard:** Click Synergy icon (📊) → [Column] column
- **Sidebar:** Synergy tab → Look for "[Title]"
- **This thread:** Orange badge showing Synergy link

**Next Steps:**
- Shall I start with Milestone 1?
- Want to add more milestones?
- Need to adjust priorities or dates?
````

#### Template: Updating Progress

````markdown
✅ Progress updated in Synergy!

📊 **[Session Name]:**
- Overall Progress: [X]% → [Y]% (+[Z]%)
- Milestone "[Milestone Name]": [OLD_STATUS] → [NEW_STATUS]

**What was completed:**
✅ [Deliverable 1]
✅ [Deliverable 2]
✅ [Deliverable 3]

**Next Up:**
⏸️ [Next Milestone Name]
   - Deliverables remaining: [List]
   - Due: [Date]

The Synergy dashboard will reflect these changes immediately.

Ready to continue with the next milestone?
````

#### Template: Suggesting Synergy

````markdown
This looks like a multi-phase project! Would you like me to create a Synergy session to track it?

**Why Synergy helps here:**
- Break down work into [X] manageable milestones
- Track progress as we complete each phase
- Keep all project context in one place
- Easily pick up where we left off in future conversations

**What I'll create:**
- Session: "[Suggested Project Name]"
- Milestones: [Brief list of phases]
- Linked to this conversation
- Priority: [Suggested priority]

Would you like me to set this up? (Or we can continue without Synergy if you prefer.)
````

#### Template: Milestone Completion

````markdown
🎉 Milestone complete!

✅ **[Milestone Name]** - DONE

**Completed Deliverables:**
✅ [Deliverable 1] - [Brief description of what was done]
✅ [Deliverable 2] - [Brief description]
✅ [Deliverable 3] - [Brief description]

📊 **Project Progress:**
- [Project Name]: [X]% → [Y]% complete
- Milestones: [N] of [M] complete
- [Column] → [New Column] (if status changed)

🎯 **What's Next:**
- Next Milestone: "[Next Milestone Name]"
- Due: [Date]
- Estimated time: [Time estimate]

Shall I begin the next milestone, or would you like to take a break?
````

#### Template: Showing Project Status

````markdown
Here's the current status of your project:

📊 **[Project Name]**
- **Status:** [Column] ([Priority] priority)
- **Overall Progress:** [X]% complete
- **Last Updated:** [Timestamp]
- **Linked Threads:** [N] conversations

🎯 **Milestones:**
1. ✅ **[Milestone 1]** - DONE ([Date])
   - All [N] deliverables complete
   
2. 🔄 **[Milestone 2]** - IN PROGRESS ([X]% done)
   - ✅ [Completed deliverable]
   - ⏸️ [Pending deliverable]
   - Due: [Date]
   
3. ⏸️ **[Milestone 3]** - NOT STARTED
   - Due: [Date]
   - [N] deliverables planned

**Timeline:**
- Started: [Start date]
- Expected completion: [End date]
- Time remaining: [Days/weeks]

Would you like to:
- Continue with current milestone?
- Review any completed work?
- Adjust priorities or dates?
````

### AI Best Practices for Synergy

#### Communication Style

✅ **DO:**
- Suggest Synergy proactively when appropriate
- Explain Synergy benefits for complex projects
- Show where to find created sessions (Dashboard, Sidebar)
- Update Synergy automatically as work progresses
- Reference Synergy context in responses
- Celebrate milestone completions
- Keep session data current

❌ **DON'T:**
- Force Synergy on simple tasks
- Create sessions without user awareness
- Let sessions become stale (update them!)
- Delete sessions without explicit permission
- Unlink threads unexpectedly
- Over-complicate with too many milestones
- Ignore existing Synergy sessions

#### Session Creation Guidelines

When creating Synergy sessions:

1. ✅ **Infer project details from user description**
   - Title: Extract key project name
   - Description: Summarize goals and scope
   - Priority: Default to Medium unless urgent language used
   - Tags: Extract key technologies/platforms

2. ✅ **Generate meaningful milestones**
   - 3-7 milestones (not too few, not too many)
   - Chronological order (what happens first)
   - Actionable names ("Build X", "Deploy Y")
   - 2-5 deliverables per milestone

3. ✅ **Set realistic due dates**
   - Estimate based on milestone complexity
   - Space out milestones (don't cluster)
   - Leave buffer time between phases

4. ✅ **Link the current thread automatically**
   - User is already discussing the project
   - Link makes sense by default
   - Mention that thread is linked

#### Progress Update Guidelines

Update Synergy automatically when:

✅ You complete a task related to a milestone
✅ User asks for progress update
✅ A deliverable is finished
✅ You're about to start a new milestone
✅ User completes work and tells you about it

**Example:**
```python
# After completing a task
if task_complete and thread_linked_to_synergy:
    # Get session details
    session = synergy_get_session(session_id)
    
    # Find relevant milestone
    milestone = find_milestone_for_task(task, session.milestones)
    
    # Update milestone
    if deliverable_complete:
        mark_deliverable_complete(milestone, deliverable)
    
    if all_deliverables_done(milestone):
        mark_milestone_done(milestone)
    
    # Update session
    synergy_update_session(session_id, updated_data)
    
    # Inform user
    celebrate_progress(milestone_name, new_percentage)
```

#### Context Preservation

Use Synergy to preserve context across conversations:

**When starting a new thread for existing project:**
```markdown
AI: "I see you're continuing work on [Project Name] from our previous conversation.

I've linked this new thread to the existing Synergy session. Here's where we left off:

Last Milestone: ✅ [Milestone X] - Complete
Current Milestone: 🔄 [Milestone Y] - 60% done
Remaining: [List of pending deliverables]

Shall I continue with [Current Milestone]?"
```

**When referencing project history:**
```markdown
AI: "As documented in the Synergy session, we decided to use PostgreSQL instead of MongoDB (see Milestone 2 notes).

I'll continue with that architecture for this new feature."
```

### AI Safety Rules

#### Never Do These Without Explicit User Approval:

❌ **Delete Synergy sessions** - Always confirm first
❌ **Unlink threads from sessions** - Ask before removing
❌ **Change project priorities** - Confirm with user
❌ **Archive sessions** - User decides when project is done
❌ **Share session data** - Privacy is paramount
❌ **Create duplicate sessions** - Check for existing first

#### Always Do These:

✅ **Suggest Synergy** when projects are complex
✅ **Update progress** automatically as work is done
✅ **Link threads** when starting work on Synergy project
✅ **Reference context** from Synergy when relevant
✅ **Explain benefits** when user is new to Synergy
✅ **Keep data current** - don't let sessions become outdated
✅ **Celebrate milestones** - make completion satisfying

### AI Knowledge Base

#### Common Project Patterns

**Web Development Project:**
```
Milestones:
1. Design & Planning
2. Backend API Development
3. Frontend Components
4. Integration & Testing
5. Deployment & Launch
```

**Data Migration Project:**
```
Milestones:
1. Audit Current Data
2. Design New Schema
3. Write Migration Scripts
4. Test Migration (Staging)
5. Production Migration
6. Validation & Rollback Plan
```

**Automation Setup:**
```
Milestones:
1. Requirements Analysis
2. Tool Selection
3. Workflow Design
4. Implementation
5. Testing & Refinement
6. Documentation & Training
```

**Integration Project:**
```
Milestones:
1. API Discovery
2. Authentication Setup
3. Core Integration Logic
4. Error Handling
5. Testing
6. Deployment
```

#### Synergy Tool Parameters

**synergy_smart_project_tracker:**
```python
{
    "title": "Project Name",
    "description": "What the project does",
    "priority": "low|medium|high",
    "tags": ["tag1", "tag2"],
    "status": "backlog|in_progress|review|done",
    "milestones": [
        {
            "name": "Milestone Name",
            "description": "What needs to be done",
            "status": "not_started|in_progress|done|blocked",
            "due_date": "YYYY-MM-DD",
            "deliverables": ["Output 1", "Output 2"]
        }
    ],
    "assigned_agents": ["prime", "agent-1"],
    "thread_ids": ["1762530418975"]
}
```

**synergy_update_session:**
```python
{
    "session_id": "sess_20251107_2211_...",
    "updates": {
        "title": "New title (optional)",
        "description": "New description (optional)",
        "status": "new_status (optional)",
        "priority": "new_priority (optional)",
        "milestones": [updated_milestone_array]
    }
}
```

#### Status Transitions

Valid status transitions:

```
Backlog → In Progress → Review → Done
   ↓          ↓           ↓
   └──────────┴───────────┴──────→ Done (can skip)
   
   Any status ←→ Backlog (can move back)
```

---

## Quick Reference Card

### Dashboard Navigation

| Action | Method |
|--------|--------|
| Open Dashboard | Click 📊 icon in left sidebar |
| Open Sidebar | Click Synergy tab on right edge |
| Create Session | "Create New Session" button in any column |
| View Session | Click session card |
| Move Session | Drag card to new column |
| Edit Session | Click card → Edit button |
| Link Thread | Drag thread onto session card |
| Unlink Thread | Click × on thread badge |

### Keyboard Shortcuts

| Shortcut | Action |
|----------|--------|
| `Ctrl+K` | Quick search sessions |
| `Ctrl+N` | New session (when dashboard open) |
| `Escape` | Close popup/modal |
| `Tab` | Navigate between fields in forms |
| `Enter` | Submit form/save changes |

### Status Icons

| Icon | Meaning |
|------|---------|
| 📋 | Backlog - Not started |
| 🔄 | In Progress - Active work |
| 👀 | Review - Needs checking |
| ✅ | Done - Completed |
| 🔴 | High priority |
| 🟡 | Medium priority |
| 🟢 | Low priority |
| 📌 | Pinned session |
| 🔗 | Thread link |
| ⏸️ | Paused/Not started |
| 🔥 | Recently active |

### Session Lifecycle

```
1. CREATE    → Fill form with project details
2. PLAN      → Add milestones and deliverables
3. LINK      → Connect thread(s) to session
4. WORK      → Update progress as you go
5. REVIEW    → Move to Review column when done
6. COMPLETE  → Move to Done when verified
7. ARCHIVE   → Clean up after 30 days
```

---

**End of Complete Guide**

*For additional help, use the AI chat or visit the Synergy Dashboard.*

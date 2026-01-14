# Database Schema Relationships - Automation & Threads

**Date:** November 19, 2025  
**Purpose:** Document how automation tables connect with sessions.threads

---

## 📊 Table Relationship Diagram

```
┌─────────────────────────────────────────────────────────────────────────┐
│                         SESSIONS SCHEMA                                 │
└─────────────────────────────────────────────────────────────────────────┘

                    ┌─────────────────────────────┐
                    │   sessions.threads          │
                    │  (Chat Conversations)       │
                    ├─────────────────────────────┤
                    │ PK: id (serial)             │
                    │     thread_slug (text)      │
                    │     user_id (integer)       │
                    │     name (text)             │
                    │                             │
                    │ WORKFLOW LINKS (Soft FK):   │
                    │  workflow_slug   ────┐      │ 🟢 Draft/Design
                    │  workflow_title      │      │
                    │  automation_slug ────┼──┐   │ 🔵 Published/Live
                    │  automation_title    │  │   │
                    │                      │  │   │
                    │ SYNERGY LINK:        │  │   │
                    │  synergy_card_id     │  │   │
                    │                      │  │   │
                    │ INTERNAL DOCS:       │  │   │
                    │  internal_doc_slug   │  │   │
                    │  internal_doc_title  │  │   │
                    └──────────────────────┼──┼───┘
                                          │  │
                                          │  │
┌─────────────────────────────────────────┼──┼───────────────────────────┐
│                    PUBLIC SCHEMA        │  │                           │
└─────────────────────────────────────────┼──┼───────────────────────────┘
                                          │  │
                    ┌─────────────────────▼──▼────────────────┐
                    │  public.visual_automations              │
                    │  (Visual Workflow Canvas - UI Storage)  │
                    ├─────────────────────────────────────────┤
                    │ PK: automation_id (text)                │
                    │     slug (text, UNIQUE) ◄───────────────┼─── Linked via slug
                    │     user_id (integer)                   │     (soft reference)
                    │     title (text)                        │
                    │     ui_json (jsonb)    ← Canvas shapes  │
                    │     execution_json     ← Steps          │
                    │     status (draft/active/paused)        │
                    │     is_scheduled (boolean)              │
                    │     scheduler_task_id (text)            │
                    │     execution_count (integer)           │
                    └─────────────────────────────────────────┘
                                          │
                                          │ automation_id
                                          │ (FK relationship)
                                          ▼
                    ┌─────────────────────────────────────────┐
                    │  public.automation_executions           │
                    │  (Execution History & Logs)             │
                    ├─────────────────────────────────────────┤
                    │ PK: execution_id (serial)               │
                    │ FK: automation_id → visual_automations  │
                    │     thread_id (integer) ────────────────┼─── Links to thread
                    │     user_id (integer)                   │     where executed
                    │     triggered_by (manual/schedule/api)  │
                    │     status (running/completed/failed)   │
                    │     started_at, completed_at            │
                    │     duration_ms (integer)               │
                    │     tools_used (jsonb)                  │
                    │     error_message (text)                │
                    └─────────────────────────────────────────┘


                    ┌─────────────────────────────────────────┐
                    │  public.automation_workflows            │
                    │  (New Workflow System - JSON-based)     │
                    ├─────────────────────────────────────────┤
                    │ PK: workflow_id (uuid)                  │
                    │     slug (text, UNIQUE) ◄───────────────┼─── Linked via slug
                    │     user_id (integer)                   │     (soft reference)
                    │     name (text)                         │
                    │     workflow_json (text) ← Steps        │
                    │     canvas_data (text)   ← UI data      │
                    │     enabled (boolean)                   │
                    │     run_count, success_count            │
                    └─────────────┬───────────────────────────┘
                                  │
                                  │ workflow_id
                                  │ (FK relationship)
                                  ▼
                    ┌─────────────────────────────────────────┐
                    │  public.workflow_executions             │
                    │  (Execution History for JSON workflows) │
                    ├─────────────────────────────────────────┤
                    │ PK: execution_id (uuid)                 │
                    │ FK: workflow_id → automation_workflows  │
                    │     status (running/completed/failed)   │
                    │     error_message (text)                │
                    │     duration_ms (integer)               │
                    │     executed_by (integer) ← user_id     │
                    └─────────────────────────────────────────┘
                                  │
                                  │ workflow_id
                                  │ (FK relationship)
                                  ▼
                    ┌─────────────────────────────────────────┐
                    │  public.workflow_schedules              │
                    │  (Scheduling Configuration)             │
                    ├─────────────────────────────────────────┤
                    │ PK: schedule_id (uuid)                  │
                    │ FK: workflow_id → automation_workflows  │
                    │     schedule_type (cron/interval/once)  │
                    │     cron_expression (text)              │
                    │     enabled (boolean)                   │
                    │     next_run_at (timestamp)             │
                    └─────────────────────────────────────────┘


                    ┌─────────────────────────────────────────┐
                    │  public.workflow_templates              │
                    │  (Pre-built Workflow Templates)         │
                    ├─────────────────────────────────────────┤
                    │ PK: template_id (uuid)                  │
                    │     slug (text, UNIQUE)                 │
                    │     name (text)                         │
                    │     template_json (text)                │
                    │     category (text)                     │
                    │     featured (boolean)                  │
                    └─────────────────────────────────────────┘


                    ┌─────────────────────────────────────────┐
                    │  public.workflow_node_library           │
                    │  (Custom Node Definitions)              │
                    ├─────────────────────────────────────────┤
                    │ PK: node_id (uuid)                      │
                    │     user_id (integer)                   │
                    │     name (text)                         │
                    │     node_type (text)                    │
                    │     config_schema (text)                │
                    └─────────────────────────────────────────┘


                    ┌─────────────────────────────────────────┐
                    │  public.saved_threads                   │
                    │  (Legacy Thread Storage - Being Phased) │
                    ├─────────────────────────────────────────┤
                    │ PK: thread_id (text)                    │
                    │     conversation (text)                 │
                    │     synergy_card_id (text)              │
                    └─────────────────────────────────────────┘
```

---

## 🔗 Connection Types

### 1. **Soft Foreign Keys (Slug-based Linking)**

These are **NOT enforced by database constraints** but linked via application logic:

```sql
-- sessions.threads links to workflows via slug
sessions.threads.workflow_slug      → visual_automations.slug       (🟢 Draft)
sessions.threads.automation_slug    → visual_automations.slug       (🔵 Published)

sessions.threads.workflow_slug      → automation_workflows.slug     (Alternative)
```

**Why Soft Keys?**
- Workflows can exist without threads
- Threads can exist without workflows
- Users can delete workflows without breaking threads
- More flexible for drag-and-drop UI

---

### 2. **Hard Foreign Keys (Database Enforced)**

These have actual `FOREIGN KEY` constraints:

```sql
-- Execution tables have hard FK to their parent workflows
automation_executions.automation_id → visual_automations.automation_id
workflow_executions.workflow_id     → automation_workflows.workflow_id
workflow_schedules.workflow_id      → automation_workflows.workflow_id

-- Executions can optionally link to threads
automation_executions.thread_id     → sessions.threads.id (soft, no FK)
```

---

## 📋 Column Purpose Reference

### sessions.threads Workflow Columns

| Column | Type | Purpose | UI Display | Links To |
|--------|------|---------|------------|----------|
| `workflow_slug` | TEXT | Draft/design workflow | 🟢 Green "Workflow" pill | `visual_automations.slug` |
| `workflow_title` | TEXT | Display name | Tooltip text | - |
| `automation_slug` | TEXT | Published/live automation | 🔵 Blue "Automation" pill | `visual_automations.slug` |
| `automation_title` | TEXT | Live automation name | Tooltip text | - |
| `workflow_id` | TEXT | Legacy/alternative ID | (Deprecated) | - |
| `workflow_name` | TEXT | Legacy name | (Deprecated) | - |

**Lifecycle:**
1. **Design Phase:** User creates workflow → `workflow_slug` set → 🟢 Pill shown
2. **Publish Phase:** AI publishes → `automation_slug` set → 🔵 Pill added
3. **Editing:** User edits design → Updates workflow via `workflow_slug`
4. **Execution:** System runs automation via `automation_slug`

---

## 🎯 Two Workflow Systems (Current State)

### System 1: Visual Automation Canvas (PRIMARY)
**Tables:** `visual_automations` + `automation_executions`

**Purpose:** Drag-and-drop visual workflow builder  
**Storage Format:** JSONB (ui_json + execution_json)  
**Primary Key:** `automation_id` (text)  
**Unique Key:** `slug` (text)  
**Status:** ✅ Active, production-ready  

**Features:**
- Visual canvas with shapes (rectangles, hexagons, circles)
- Connections between nodes
- UI-driven workflow creation
- AI-interpretable execution format
- Auto-save functionality
- Thread linking via slug drag-and-drop

**Backend Routes:** `/api/automation/*`  
**Frontend:** `UI/external/modules/automation-workflows/`

---

### System 2: JSON Workflow Engine (SECONDARY)
**Tables:** `automation_workflows` + `workflow_executions` + `workflow_schedules`

**Purpose:** JSON-based workflow execution engine  
**Storage Format:** Text (workflow_json + canvas_data)  
**Primary Key:** `workflow_id` (uuid)  
**Unique Key:** `slug` (text)  
**Status:** ⚠️ Exists but less used  

**Features:**
- JSON-defined workflows
- Separate execution tracking
- Scheduling system
- Template library support
- Node library for custom nodes

**Overlap:** Both systems use `slug` for linking to threads!

---

## 🔄 Data Flow Examples

### Example 1: User Creates Workflow

```
1. User opens Automation Canvas
   ├─ UI loads empty canvas
   └─ No database records yet

2. User drags shapes, makes connections
   ├─ JavaScript tracks in memory
   └─ Still no database records

3. User clicks "Save" or auto-save triggers
   ├─ POST /api/automation/save
   ├─ Generates slug: "workflow-1737052800"
   └─ INSERT INTO visual_automations (
         slug = 'workflow-1737052800',
         status = 'draft',
         ui_json = {...shapes, connections...},
         execution_json = {...steps...}
       )

4. User drags slug to thread card
   ├─ POST /api/automation/link-to-thread
   ├─ UPDATE sessions.threads SET
         workflow_slug = 'workflow-1737052800',
         workflow_title = 'My Workflow'
       WHERE id = 123
   └─ UI shows 🟢 Green "Workflow" pill
```

---

### Example 2: AI Publishes Workflow

```
1. User asks: "Publish this workflow to run hourly"

2. AI calls: automation_publish_workflow(slug, schedule_cron)
   ├─ POST /api/automation/{slug}/publish
   ├─ Validates workflow structure
   └─ If valid, continues...

3. Backend updates workflow status
   ├─ UPDATE visual_automations SET
         status = 'active',
         is_scheduled = true,
         schedule_cron = '0 */1 * * *'
       WHERE slug = 'workflow-1737052800'
   
4. Backend links automation to thread
   ├─ UPDATE sessions.threads SET
         automation_slug = 'workflow-1737052800',
         automation_title = 'My Workflow (Live)'
       WHERE workflow_slug = 'workflow-1737052800'
   └─ UI adds 🔵 Blue "Automation" pill

5. Backend creates scheduler task
   ├─ Creates task in scheduler
   └─ Updates scheduler_task_id in visual_automations
```

---

### Example 3: Workflow Executes

```
1. Scheduler triggers workflow
   ├─ Finds workflow by slug: 'workflow-1737052800'
   └─ Loads execution_json with steps

2. Creates execution record
   ├─ INSERT INTO automation_executions (
         automation_id = 'workflow-1737052800',
         thread_id = 123,  ← Links to thread!
         triggered_by = 'schedule',
         status = 'running',
         started_at = NOW()
       )
   
3. Executes workflow steps
   ├─ Step 1: gmail_list_messages
   ├─ Step 2: ai_extract_invoice
   └─ Step 3: google_sheets_append

4. Updates execution record
   ├─ UPDATE automation_executions SET
         status = 'completed',
         completed_at = NOW(),
         duration_ms = 15000,
         tools_used = '["gmail_list_messages", ...]'::jsonb
       WHERE execution_id = 42

5. Updates workflow stats
   └─ UPDATE visual_automations SET
         execution_count = execution_count + 1,
         last_executed_at = NOW()
       WHERE automation_id = 'workflow-1737052800'
```

---

### Example 4: User Checks Status

```
1. User asks: "How is my workflow doing?"

2. AI calls: automation_get_workflow_status(slug)
   ├─ GET /api/automation/{slug}/status
   
3. Backend queries workflow info
   ├─ SELECT * FROM visual_automations
       WHERE slug = 'workflow-1737052800'
   
4. Backend queries execution stats
   ├─ SELECT
         COUNT(*) as total,
         COUNT(*) FILTER (WHERE status = 'completed') as success
       FROM automation_executions
       WHERE automation_id = 'workflow-1737052800'
   
5. Backend queries last execution
   └─ SELECT * FROM automation_executions
       WHERE automation_id = 'workflow-1737052800'
       ORDER BY started_at DESC LIMIT 1

6. Returns combined status
   └─ {
         workflow: {status: 'active', ...},
         execution_status: {
           total_executions: 24,
           success_rate: 0.958,
           last_execution: {...}
         }
       }
```

---

## 🔍 Query Examples

### Get Thread with Workflow Info

```sql
SELECT 
  t.id,
  t.name,
  t.workflow_slug,
  t.workflow_title,
  t.automation_slug,
  t.automation_title,
  vw.status as workflow_status,
  vw.execution_count,
  vw.last_executed_at
FROM sessions.threads t
LEFT JOIN public.visual_automations vw 
  ON vw.slug = t.workflow_slug
WHERE t.id = 123;
```

### Get Workflow with Execution History

```sql
SELECT 
  vw.slug,
  vw.title,
  vw.status,
  COUNT(ae.execution_id) as total_runs,
  COUNT(ae.execution_id) FILTER (WHERE ae.status = 'completed') as successful_runs,
  MAX(ae.started_at) as last_run
FROM public.visual_automations vw
LEFT JOIN public.automation_executions ae 
  ON ae.automation_id = vw.automation_id
WHERE vw.slug = 'workflow-1737052800'
GROUP BY vw.slug, vw.title, vw.status;
```

### Get All Workflows for a Thread

```sql
-- Get draft workflow
SELECT * FROM public.visual_automations
WHERE slug = (
  SELECT workflow_slug FROM sessions.threads WHERE id = 123
);

-- Get published automation
SELECT * FROM public.visual_automations
WHERE slug = (
  SELECT automation_slug FROM sessions.threads WHERE id = 123
);
```

### Get Thread Executions

```sql
SELECT 
  ae.*,
  t.name as thread_name
FROM public.automation_executions ae
JOIN sessions.threads t ON t.id = ae.thread_id
WHERE ae.thread_id = 123
ORDER BY ae.started_at DESC;
```

---

## 🚨 Important Notes

### Soft FK Considerations

**Advantages:**
- ✅ Flexible: Can delete workflows without breaking threads
- ✅ Simple: No cascade delete logic needed
- ✅ Fast: No foreign key constraint checks

**Disadvantages:**
- ⚠️ Orphaned references: Thread may point to deleted workflow
- ⚠️ No automatic cleanup: Manual maintenance required
- ⚠️ Referential integrity not enforced by database

**Mitigation:**
```sql
-- Check for orphaned workflow slugs
SELECT t.id, t.workflow_slug
FROM sessions.threads t
LEFT JOIN public.visual_automations vw ON vw.slug = t.workflow_slug
WHERE t.workflow_slug IS NOT NULL 
  AND vw.slug IS NULL;

-- Clean up orphaned references
UPDATE sessions.threads
SET workflow_slug = NULL, workflow_title = NULL
WHERE workflow_slug NOT IN (SELECT slug FROM public.visual_automations);
```

---

### Schema Evolution

**Current State (Nov 2025):**
- `visual_automations` - Primary system (active)
- `automation_workflows` - Secondary system (less used)
- Both link to threads via `slug`

**Future Considerations:**
1. **Consolidation:** Merge both systems into one
2. **Hard FK:** Add actual foreign key constraints
3. **UUIDs:** Standardize on UUID vs text IDs
4. **Cascade:** Add ON DELETE CASCADE where appropriate

---

## 📝 Summary

**Key Relationships:**

| From | To | Link Type | Column | Purpose |
|------|----|-----------| -------|---------|
| `sessions.threads` | `visual_automations` | Soft FK | `workflow_slug` | Draft workflow link |
| `sessions.threads` | `visual_automations` | Soft FK | `automation_slug` | Published automation link |
| `automation_executions` | `visual_automations` | Hard FK | `automation_id` | Execution belongs to workflow |
| `automation_executions` | `sessions.threads` | Soft FK | `thread_id` | Execution context |
| `workflow_executions` | `automation_workflows` | Hard FK | `workflow_id` | Execution belongs to workflow |
| `workflow_schedules` | `automation_workflows` | Hard FK | `workflow_id` | Schedule belongs to workflow |

**Connection Pattern:**
```
Thread ──(workflow_slug)──> Visual Automation ──(automation_id)──> Executions
   │                              │
   │                              └──(last_executed_at, execution_count)
   │
   └──(automation_slug)──> Published Automation ──> Scheduler Tasks
```

---

**Last Updated:** November 19, 2025  
**Author:** AI Agent (Claude Sonnet 4.5)  
**Status:** ✅ Complete Documentation

# 🔍 Automation vs Workflow Tables - Complete Analysis

## Executive Summary

The AI Agents platform uses **TWO parallel table systems** for managing visual automation workflows:

1. **`visual_automations`** - Canvas/Design table (PRIMARY for UI)
2. **`automation_workflows`** - Production/Execution table (SECONDARY for runtime)

These tables serve **different purposes** in the workflow lifecycle and should be **synchronized**, not duplicated.

---

## 📊 Table Comparison Matrix

| Feature | `visual_automations` | `automation_workflows` |
|---------|---------------------|------------------------|
| **Primary Purpose** | Visual canvas design & storage | Production workflow execution |
| **User Interaction** | Direct (drag-and-drop canvas) | Indirect (via promotion/deployment) |
| **Data Format** | `ui_json` (shapes/connections) + `execution_json` (tool definitions) | `workflow_json` (complete definition) + `canvas_data` (positions) |
| **Lifecycle Stage** | Draft → Active → Archived | Enabled/Disabled (production only) |
| **ID Type** | `automation_id` (TEXT) | `workflow_id` (UUID) |
| **Slug** | `slug` (TEXT, UNIQUE) | `slug` (VARCHAR(250), UNIQUE) |
| **Status Field** | `status` (draft/active/paused/archived) | `enabled` (boolean) |
| **Scheduling** | `is_scheduled`, `schedule_cron`, `schedule_datetime` | External `workflow_schedules` table |
| **Execution Tracking** | `execution_count`, `last_executed_at` | `run_count`, `success_count`, `error_count`, `last_run_at` |
| **Schema** | `public` | `public` |
| **Created By** | Migration `004_automation_tables.sql` | Migration `005_automation_workflow_tables.sql` |
| **Used By UI** | ✅ PRIMARY (canvas rendering) | ❌ SECONDARY (status only) |
| **Used By Backend** | ✅ Read for display | ✅ Read/Write for execution |

---

## 🏗️ Table Schemas (Side-by-Side)

### `visual_automations` (Canvas/Design Table)

```sql
CREATE TABLE public.visual_automations (
  automation_id TEXT NOT NULL PRIMARY KEY,        -- Custom slug format: wf_abc123_timestamp
  user_id INTEGER NOT NULL,                       -- Owner
  title TEXT NOT NULL,                            -- Display name
  slug TEXT NOT NULL UNIQUE,                      -- Human-readable identifier
  description TEXT,                               -- User description
  category TEXT DEFAULT 'other',                  -- email, data_processing, notifications, etc.
  
  -- Canvas data (shapes, connections, visual layout)
  ui_json JSONB NOT NULL DEFAULT '{}',           -- { shapes: [...], connections: [...] }
  
  -- Execution data (tool calls, parameters)
  execution_json JSONB NOT NULL DEFAULT '{}',    -- { actions: [...], trigger: {...} }
  
  -- Scheduling
  schedule_cron TEXT,                             -- '0 9 * * *' (cron syntax)
  schedule_datetime TIMESTAMP WITH TIME ZONE,    -- One-time scheduled execution
  timezone TEXT DEFAULT 'UTC',
  is_scheduled BOOLEAN DEFAULT false,
  scheduler_task_id TEXT,                        -- APScheduler task reference
  
  -- Lifecycle state
  status TEXT DEFAULT 'draft',                   -- draft, active, paused, archived
  
  -- Execution tracking
  execution_count INTEGER DEFAULT 0,
  last_executed_at TIMESTAMP WITH TIME ZONE,
  
  -- Timestamps
  created_at TIMESTAMP WITH TIME ZONE DEFAULT now(),
  updated_at TIMESTAMP WITH TIME ZONE DEFAULT now()
);
```

**Key Features**:
- ✅ Visual canvas data (`ui_json` with shapes/connections)
- ✅ Execution definitions (`execution_json` with tool calls)
- ✅ Built-in scheduling (cron + datetime)
- ✅ Status lifecycle (draft → active → paused → archived)
- ✅ Direct execution tracking

---

### `automation_workflows` (Production/Execution Table)

```sql
CREATE TABLE public.automation_workflows (
  workflow_id UUID NOT NULL DEFAULT gen_random_uuid() PRIMARY KEY,
  user_id INTEGER NOT NULL,
  name VARCHAR(200) NOT NULL,                    -- Display name
  slug VARCHAR(250) NOT NULL UNIQUE,             -- Matches visual_automations.slug
  description TEXT,
  category VARCHAR(50),
  
  -- Complete workflow definition
  workflow_json TEXT NOT NULL,                   -- Full workflow structure (merged ui_json + execution_json)
  canvas_data TEXT,                              -- UI positioning (x, y coordinates)
  
  -- Production state
  enabled BOOLEAN DEFAULT true,                  -- Enable/disable execution
  version VARCHAR(20) DEFAULT '1.0',             -- Versioning support
  
  -- Execution tracking (detailed)
  run_count INTEGER DEFAULT 0,
  success_count INTEGER DEFAULT 0,
  error_count INTEGER DEFAULT 0,
  last_run_at TIMESTAMP,
  
  -- Timestamps
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

**Key Features**:
- ✅ Production-ready flag (`enabled`)
- ✅ Detailed execution stats (success/error counts)
- ✅ Version tracking
- ✅ External scheduling via `workflow_schedules` table
- ✅ UUID-based IDs (more robust)

---

## 🔄 Relationship & Data Flow

### Current Implementation (From Code Analysis)

```
┌─────────────────────────────────────────────────────────────┐
│                    USER INTERACTION                         │
│                                                             │
│  1. User designs workflow in visual canvas                 │
│  2. Drag shapes, connect nodes, configure tools            │
│  3. Click "Save" button                                     │
└──────────────────────┬──────────────────────────────────────┘
                       │
                       ↓
┌─────────────────────────────────────────────────────────────┐
│              visual_automations TABLE                       │
│  ┌───────────────────────────────────────────────────────┐  │
│  │ automation_id: wf_abc123_1732029847                   │  │
│  │ slug: workflow-email-summary                          │  │
│  │ title: "Daily Email Summary"                          │  │
│  │ status: "draft"                                       │  │
│  │ ui_json: { shapes: [...], connections: [...] }       │  │
│  │ execution_json: { actions: [...], trigger: {...} }   │  │
│  │ schedule_cron: "0 9 * * *"                           │  │
│  │ is_scheduled: false (not yet activated)              │  │
│  └───────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────┘
                       │
                       │ User clicks "Activate" or "Deploy to Production"
                       │
                       ↓
┌─────────────────────────────────────────────────────────────┐
│         PROMOTION TO PRODUCTION (Manual Step)               │
│                                                             │
│  Backend copies/transforms workflow data:                  │
│  • Validates execution_json                                │
│  • Merges ui_json + execution_json → workflow_json         │
│  • Extracts canvas positions → canvas_data                 │
│  • Creates entry in automation_workflows                   │
└──────────────────────┬──────────────────────────────────────┘
                       │
                       ↓
┌─────────────────────────────────────────────────────────────┐
│           automation_workflows TABLE                        │
│  ┌───────────────────────────────────────────────────────┐  │
│  │ workflow_id: 550e8400-e29b-41d4-a716-446655440000     │  │
│  │ slug: workflow-email-summary (SAME as visual)         │  │
│  │ name: "Daily Email Summary"                           │  │
│  │ enabled: true (ready for execution)                   │  │
│  │ workflow_json: { merged ui + execution data }         │  │
│  │ canvas_data: { nodes: { node_1: {x: 100, y: 200} } } │  │
│  └───────────────────────────────────────────────────────┘  │
│                                                             │
│  Optional: Create schedule in workflow_schedules            │
│  ┌───────────────────────────────────────────────────────┐  │
│  │ workflow_id: 550e8400-e29b-41d4-a716-446655440000     │  │
│  │ schedule_type: "cron"                                 │  │
│  │ cron_expression: "0 9 * * *"                          │  │
│  │ enabled: true                                         │  │
│  └───────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────┘
                       │
                       │ Scheduler triggers execution
                       │
                       ↓
┌─────────────────────────────────────────────────────────────┐
│              WORKFLOW EXECUTION                             │
│                                                             │
│  1. Scheduler/API calls execution endpoint                 │
│  2. Loads from automation_workflows (not visual_automations)│
│  3. Executes tools in sequence                             │
│  4. Logs execution in workflow_executions                  │
│  5. Updates stats in automation_workflows                  │
└─────────────────────────────────────────────────────────────┘
```

---

## 🎯 Intended Use Cases

### `visual_automations` - Canvas/Design Phase

**Use When:**
- ✅ User is designing workflow in UI canvas
- ✅ Dragging shapes, creating connections
- ✅ Configuring tool parameters
- ✅ Saving draft workflows (not yet production)
- ✅ Testing workflows manually
- ✅ Previewing workflow structure

**Operations:**
- `INSERT` - Create new workflow from canvas
- `UPDATE` - Auto-save canvas changes
- `SELECT` - Load workflow into canvas for editing
- `DELETE` - Remove draft workflow

**Status Lifecycle:**
```
draft → active → paused → archived
  ↑       ↓
  └───────┘ (can toggle)
```

---

### `automation_workflows` - Production/Execution Phase

**Use When:**
- ✅ Workflow is promoted to production
- ✅ Workflow needs to be scheduled/executed
- ✅ Tracking execution statistics (success/error counts)
- ✅ Enabling/disabling production workflows
- ✅ Versioning workflows
- ✅ Production monitoring and logging

**Operations:**
- `INSERT` - Promote workflow from visual_automations
- `UPDATE` - Toggle enabled state, update stats
- `SELECT` - Load for execution
- `DELETE` - Remove from production (keep in visual_automations as archive)

**Enabled State:**
```
enabled: true  → Workflow actively executes on triggers
enabled: false → Workflow paused (not deleted, can re-enable)
```

---

## 🔗 JOIN Pattern (Current Implementation)

From `automation_routes.py` lines 652-677:

```python
query = """
    SELECT 
        va.automation_id, 
        va.slug, 
        va.title, 
        va.description, 
        va.category, 
        va.status,
        va.ui_json, 
        va.execution_json, 
        va.is_scheduled, 
        va.schedule_cron,
        va.created_at, 
        va.updated_at, 
        va.last_executed_at, 
        va.execution_count,
        va.user_id,
        aw.workflow_id,
        aw.enabled AS automation_enabled,
        CASE 
            WHEN aw.workflow_id IS NOT NULL THEN 'production'
            ELSE 'draft'
        END AS workflow_state
    FROM visual_automations va
    LEFT JOIN automation_workflows aw ON va.slug = aw.slug AND va.user_id = aw.user_id
    WHERE va.user_id = %s OR va.user_id = 1
"""
```

**JOIN Logic**:
- **PRIMARY source**: `visual_automations` (all workflows shown)
- **LEFT JOIN**: `automation_workflows` (check if promoted to production)
- **Slug matching**: Same slug links canvas design to production instance
- **Workflow state**:
  - `aw.workflow_id IS NOT NULL` → "production" (exists in both tables)
  - `aw.workflow_id IS NULL` → "draft" (only in visual_automations)

---

## 🔍 Key Differences Breakdown

### 1. ID Strategy

**`visual_automations`**:
```sql
automation_id TEXT PRIMARY KEY
-- Format: wf_abc12345_1732029847
-- Custom slug-based ID with timestamp
```

**`automation_workflows`**:
```sql
workflow_id UUID PRIMARY KEY DEFAULT gen_random_uuid()
-- Format: 550e8400-e29b-41d4-a716-446655440000
-- Standard UUID for robust references
```

**Why Different?**:
- Canvas IDs need to be human-readable and timestamp-based
- Production IDs need to be globally unique and immutable
- Both tables use `slug` as the linking key (more stable than IDs)

---

### 2. JSON Data Structure

**`visual_automations`** - Split JSON:
```json
{
  "ui_json": {
    "shapes": [
      {"id": "trigger_1", "type": "hexagon", "x": 100, "y": 100, "text": "TRIGGER: schedule"},
      {"id": "action_1", "type": "rectangle", "x": 100, "y": 250, "text": "gmail_list_messages"}
    ],
    "connections": [
      {"id": "conn_1", "from": "trigger_1", "to": "action_1"}
    ]
  },
  "execution_json": {
    "trigger": {"type": "schedule", "schedule_cron": "0 9 * * *"},
    "actions": [
      {"tool": "gmail_list_messages", "parameters": {"max_results": 20}}
    ]
  }
}
```

**`automation_workflows`** - Merged JSON:
```json
{
  "workflow_json": {
    "nodes": [
      {"id": "trigger_1", "type": "trigger", "config": {"schedule_cron": "0 9 * * *"}},
      {"id": "action_1", "type": "action", "tool": "gmail_list_messages", "config": {"max_results": 20}}
    ],
    "edges": [
      {"from": "trigger_1", "to": "action_1"}
    ]
  },
  "canvas_data": {
    "nodes": {
      "trigger_1": {"x": 100, "y": 100},
      "action_1": {"x": 100, "y": 250}
    }
  }
}
```

**Why Different?**:
- Canvas needs separation for rendering (ui) vs execution (logic)
- Production needs unified structure for execution engine
- Canvas data extracted separately for efficiency

---

### 3. Scheduling Approach

**`visual_automations`** - Built-in scheduling:
```sql
schedule_cron TEXT,              -- '0 9 * * *'
schedule_datetime TIMESTAMP,     -- One-time execution
is_scheduled BOOLEAN,            -- Activation flag
scheduler_task_id TEXT,          -- APScheduler reference
timezone TEXT DEFAULT 'UTC'
```

**`automation_workflows`** - External scheduling:
```sql
-- No built-in scheduling fields
-- Uses separate workflow_schedules table:
CREATE TABLE workflow_schedules (
  schedule_id UUID PRIMARY KEY,
  workflow_id UUID REFERENCES automation_workflows(workflow_id),
  schedule_type VARCHAR(20),     -- 'cron', 'interval', 'once'
  cron_expression VARCHAR(100),
  interval_minutes INTEGER,
  run_at TIMESTAMP,
  enabled BOOLEAN,
  last_run_at TIMESTAMP,
  next_run_at TIMESTAMP
);
```

**Why Different?**:
- Canvas scheduling: Simple, immediate activation
- Production scheduling: Flexible, supports multiple schedules per workflow

---

### 4. Status vs Enabled

**`visual_automations.status`** (Lifecycle):
```
draft      → User still designing (not yet functional)
active     → Workflow completed and activated
paused     → Temporarily disabled (can resume)
archived   → No longer used (soft delete)
```

**`automation_workflows.enabled`** (Production Toggle):
```
true   → Workflow executes on triggers
false  → Workflow paused (not deleted)
```

**Relationship**:
- `visual_automations.status = 'draft'` → NOT in `automation_workflows`
- `visual_automations.status = 'active'` → EXISTS in `automation_workflows` with `enabled = true`
- `visual_automations.status = 'paused'` → EXISTS in `automation_workflows` with `enabled = false`
- `visual_automations.status = 'archived'` → DELETED from `automation_workflows` (or kept with `enabled = false`)

---

## ⚠️ Current Issues & Anti-Patterns

### Issue 1: Data Duplication

**Problem**: Same workflow data stored in both tables with slight variations

**Evidence**:
```python
# From check_workflows.py lines 67-69:
if count == 0 and count2 > 0:
    print('ISSUE: Data exists in automation_workflows but NOT in visual_automations!')
    print('  - Need to migrate/copy workflows from automation_workflows → visual_automations')
```

**Impact**:
- Data inconsistency between canvas and production
- Confusion about which table is source of truth
- Update anomalies (update one table but not the other)

---

### Issue 2: Unclear Promotion Process

**Problem**: No clear API endpoint or function to promote workflow from design to production

**Current State**:
- Tools like `supabase_create_workflow` insert into `automation_workflows` directly
- Canvas saves to `visual_automations` directly
- No synchronization between the two

**What's Missing**:
```python
# Should exist but doesn't:
def promote_workflow_to_production(automation_id):
    """
    Promotes workflow from visual_automations to automation_workflows
    
    1. Validate workflow in visual_automations
    2. Transform ui_json + execution_json → workflow_json
    3. Create entry in automation_workflows
    4. Update visual_automations.status = 'active'
    5. Create schedule in workflow_schedules if needed
    """
    pass
```

---

### Issue 3: Confusing Terminology

**Problem**: Multiple overlapping terms for same concepts

| What It Means | Different Names Used |
|---------------|---------------------|
| Workflow identifier | `automation_id`, `workflow_id`, `slug` |
| Workflow name | `title`, `name` |
| Production state | `status`, `enabled`, `workflow_state`, `is_production` |
| Execution definition | `execution_json`, `workflow_json`, `ui_json.nodes` |

**Impact**: Developer confusion, harder to maintain

---

## ✅ Recommended Handling Strategy

### 1. Establish Clear Roles

**`visual_automations`** = **"Canvas Table"** (Source of Truth for Design)
- Primary storage for all workflow designs
- User interacts with this table via canvas UI
- Contains both visual (shapes/connections) and execution (tool calls) data
- Supports draft, active, paused, archived states

**`automation_workflows`** = **"Production Table"** (Derived from Canvas)
- Secondary storage for production-ready workflows
- Generated by promoting workflows from `visual_automations`
- Contains optimized execution format (merged JSON)
- Supports enabled/disabled production state

---

### 2. Implement Workflow Lifecycle

```
┌─────────────────────────────────────────────────────────────┐
│                     WORKFLOW LIFECYCLE                      │
└─────────────────────────────────────────────────────────────┘

1. CREATE (Draft)
   ↓
   [visual_automations]
   status: draft
   ↓
   User designs workflow in canvas

2. VALIDATE
   ↓
   Check execution_json is complete
   Verify tool parameters are valid
   ↓
   Update visual_automations.status = 'active'

3. PROMOTE TO PRODUCTION
   ↓
   Transform: ui_json + execution_json → workflow_json
   ↓
   INSERT into automation_workflows
   ↓
   Link via slug (visual_automations.slug = automation_workflows.slug)
   ↓
   Create schedule in workflow_schedules (if needed)

4. EXECUTE (Production)
   ↓
   Scheduler/API loads from automation_workflows
   ↓
   Execute tools in sequence
   ↓
   Log in workflow_executions
   ↓
   Update stats in automation_workflows

5. PAUSE/UNPAUSE (Production Control)
   ↓
   UPDATE automation_workflows SET enabled = false/true
   ↓
   (Keep in visual_automations for re-editing)

6. ARCHIVE/DELETE
   ↓
   DELETE from automation_workflows (remove from production)
   ↓
   UPDATE visual_automations SET status = 'archived'
   ↓
   (Keep for history, can restore later)
```

---

### 3. Add Missing API Endpoints

**Endpoint 1: Promote Workflow**
```python
@automation_bp.route('/<automation_id>/promote', methods=['POST'])
def promote_workflow_to_production(automation_id):
    """
    Promote workflow from visual_automations to automation_workflows
    
    Request: POST /api/automation/{automation_id}/promote
    Body: { "schedule": { "type": "cron", "expression": "0 9 * * *" } }
    
    Returns:
    {
        "success": true,
        "workflow_id": "550e8400-e29b-41d4-a716-446655440000",
        "message": "Workflow promoted to production"
    }
    """
    # 1. Load from visual_automations
    # 2. Validate execution_json
    # 3. Transform to workflow_json format
    # 4. Insert into automation_workflows
    # 5. Create schedule in workflow_schedules (if requested)
    # 6. Update visual_automations.status = 'active'
    pass
```

**Endpoint 2: Sync Production Stats**
```python
@automation_bp.route('/<automation_id>/sync-stats', methods=['POST'])
def sync_production_stats(automation_id):
    """
    Sync execution stats from automation_workflows back to visual_automations
    
    Request: POST /api/automation/{automation_id}/sync-stats
    
    Updates visual_automations with:
    - execution_count
    - last_executed_at
    - (from automation_workflows.run_count, last_run_at)
    """
    pass
```

**Endpoint 3: Demote from Production**
```python
@automation_bp.route('/<automation_id>/demote', methods=['POST'])
def demote_workflow_from_production(automation_id):
    """
    Remove workflow from production (keep in visual_automations)
    
    Request: POST /api/automation/{automation_id}/demote
    
    Actions:
    1. Delete from automation_workflows
    2. Delete associated schedules from workflow_schedules
    3. Update visual_automations.status = 'draft' or 'paused'
    """
    pass
```

---

### 4. Synchronization Pattern

**Option A: One-Way Sync (Recommended)**
```
visual_automations (Source) → automation_workflows (Derived)

Changes in visual_automations trigger updates to automation_workflows
Changes in automation_workflows DO NOT trigger updates to visual_automations
(except for execution stats like run_count)
```

**Option B: Two-Way Sync (More Complex)**
```
visual_automations ↔ automation_workflows

Any change to either table syncs to the other
Requires conflict resolution strategy
More prone to errors
```

**Recommendation**: Use **Option A (One-Way Sync)** with explicit promotion/demotion

---

### 5. Database Triggers (Optional)

**Trigger 1: Auto-promote on Status Change**
```sql
CREATE OR REPLACE FUNCTION auto_promote_workflow()
RETURNS TRIGGER AS $$
BEGIN
    -- If status changed from 'draft' to 'active'
    IF OLD.status = 'draft' AND NEW.status = 'active' THEN
        -- Check if not already in production
        IF NOT EXISTS (
            SELECT 1 FROM automation_workflows 
            WHERE slug = NEW.slug AND user_id = NEW.user_id
        ) THEN
            -- Insert into production table
            INSERT INTO automation_workflows (
                user_id, name, slug, description, category,
                workflow_json, canvas_data, enabled
            )
            VALUES (
                NEW.user_id,
                NEW.title,
                NEW.slug,
                NEW.description,
                NEW.category,
                -- Merge ui_json + execution_json
                jsonb_build_object(
                    'nodes', NEW.execution_json->'actions',
                    'trigger', NEW.execution_json->'trigger',
                    'ui', NEW.ui_json
                )::TEXT,
                NEW.ui_json::TEXT,
                true
            );
        END IF;
    END IF;
    
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trigger_auto_promote_workflow
    AFTER UPDATE ON visual_automations
    FOR EACH ROW
    EXECUTE FUNCTION auto_promote_workflow();
```

**Trigger 2: Sync Execution Stats**
```sql
CREATE OR REPLACE FUNCTION sync_execution_stats()
RETURNS TRIGGER AS $$
BEGIN
    -- Update visual_automations with latest stats from automation_workflows
    UPDATE visual_automations
    SET 
        execution_count = NEW.run_count,
        last_executed_at = NEW.last_run_at
    WHERE slug = (SELECT slug FROM automation_workflows WHERE workflow_id = NEW.workflow_id)
      AND user_id = NEW.user_id;
    
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trigger_sync_execution_stats
    AFTER UPDATE ON automation_workflows
    FOR EACH ROW
    WHEN (NEW.run_count IS DISTINCT FROM OLD.run_count)
    EXECUTE FUNCTION sync_execution_stats();
```

---

## 📝 Code Usage Examples

### Example 1: Create Draft Workflow (Canvas)

```python
# User saves workflow from canvas
conn = get_db_connection()
cursor = conn.cursor()

cursor.execute("""
    INSERT INTO visual_automations (
        automation_id, user_id, slug, title, description, category,
        ui_json, execution_json, status, is_scheduled
    )
    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
""", (
    'wf_abc123_1732029847',
    user_id,
    'daily-email-summary',
    'Daily Email Summary',
    'Summarizes unread emails every morning',
    'email',
    json.dumps({
        'shapes': [
            {'id': 'trigger_1', 'type': 'hexagon', 'x': 100, 'y': 100, 'text': 'TRIGGER: schedule'},
            {'id': 'action_1', 'type': 'rectangle', 'x': 100, 'y': 250, 'text': 'gmail_list_messages'}
        ],
        'connections': [
            {'id': 'conn_1', 'from': 'trigger_1', 'to': 'action_1'}
        ]
    }),
    json.dumps({
        'trigger': {'type': 'schedule', 'schedule_cron': '0 9 * * *'},
        'actions': [
            {'tool': 'gmail_list_messages', 'parameters': {'max_results': 20}}
        ]
    }),
    'draft',  # Status: draft (not yet production)
    False     # Not scheduled yet
))

conn.commit()
conn.close()
```

---

### Example 2: Promote to Production

```python
# User clicks "Activate" button in UI
automation_id = 'wf_abc123_1732029847'

conn = get_db_connection()
cursor = conn.cursor()

# 1. Load from visual_automations
cursor.execute("""
    SELECT slug, title, description, category, ui_json, execution_json, schedule_cron
    FROM visual_automations
    WHERE automation_id = %s AND user_id = %s
""", (automation_id, user_id))

row = cursor.fetchone()
if not row:
    raise ValueError('Workflow not found')

# 2. Transform to production format
workflow_json = {
    'trigger': json.loads(row['execution_json']).get('trigger'),
    'actions': json.loads(row['execution_json']).get('actions'),
    'ui': json.loads(row['ui_json'])
}

# 3. Insert into automation_workflows
cursor.execute("""
    INSERT INTO automation_workflows (
        user_id, slug, name, description, category, workflow_json, canvas_data, enabled
    )
    VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
    RETURNING workflow_id
""", (
    user_id,
    row['slug'],
    row['title'],
    row['description'],
    row['category'],
    json.dumps(workflow_json),
    json.dumps(json.loads(row['ui_json'])),  # Canvas data
    True  # Enabled by default
))

workflow_id = cursor.fetchone()['workflow_id']

# 4. Create schedule (if needed)
if row['schedule_cron']:
    cursor.execute("""
        INSERT INTO workflow_schedules (
            workflow_id, schedule_type, cron_expression, enabled
        )
        VALUES (%s, %s, %s, %s)
    """, (workflow_id, 'cron', row['schedule_cron'], True))

# 5. Update visual_automations status
cursor.execute("""
    UPDATE visual_automations
    SET status = 'active', is_scheduled = TRUE
    WHERE automation_id = %s
""", (automation_id,))

conn.commit()
conn.close()
```

---

### Example 3: Load Workflow for Canvas (UI)

```python
# Frontend requests workflow for canvas rendering
automation_id = 'wf_abc123_1732029847'

conn = get_db_connection()
cursor = conn.cursor()

# Query ONLY visual_automations (canvas source)
cursor.execute("""
    SELECT 
        va.automation_id,
        va.slug,
        va.title,
        va.description,
        va.category,
        va.status,
        va.ui_json,
        va.execution_json,
        va.is_scheduled,
        va.schedule_cron,
        aw.workflow_id AS production_workflow_id,
        aw.enabled AS is_production_enabled
    FROM visual_automations va
    LEFT JOIN automation_workflows aw ON va.slug = aw.slug AND va.user_id = aw.user_id
    WHERE va.automation_id = %s AND va.user_id = %s
""", (automation_id, user_id))

row = cursor.fetchone()
conn.close()

# Return to frontend
workflow_data = {
    'automation_id': row['automation_id'],
    'slug': row['slug'],
    'title': row['title'],
    'description': row['description'],
    'category': row['category'],
    'status': row['status'],
    'is_production': row['production_workflow_id'] is not None,
    'is_production_enabled': row['is_production_enabled'],
    'shapes': json.loads(row['ui_json']).get('shapes', []),
    'connections': json.loads(row['ui_json']).get('connections', []),
    'execution_json': json.loads(row['execution_json'])
}
```

---

### Example 4: Execute Production Workflow

```python
# Scheduler or API executes production workflow
slug = 'daily-email-summary'

conn = get_db_connection()
cursor = conn.cursor()

# Query automation_workflows (NOT visual_automations)
cursor.execute("""
    SELECT workflow_id, workflow_json, enabled
    FROM automation_workflows
    WHERE slug = %s AND user_id = %s AND enabled = TRUE
""", (slug, user_id))

row = cursor.fetchone()
if not row:
    raise ValueError('Production workflow not found or disabled')

workflow_json = json.loads(row['workflow_json'])

# Execute workflow
execution_id = str(uuid.uuid4())
started_at = datetime.now()

try:
    # Execute actions in sequence
    for action in workflow_json['actions']:
        execute_tool(action['tool'], action['parameters'])
    
    # Log success
    cursor.execute("""
        INSERT INTO workflow_executions (
            execution_id, workflow_id, status, started_at, completed_at
        )
        VALUES (%s, %s, %s, %s, %s)
    """, (execution_id, row['workflow_id'], 'completed', started_at, datetime.now()))
    
    # Update stats
    cursor.execute("""
        UPDATE automation_workflows
        SET run_count = run_count + 1,
            success_count = success_count + 1,
            last_run_at = NOW()
        WHERE workflow_id = %s
    """, (row['workflow_id'],))
    
    conn.commit()

except Exception as e:
    # Log failure
    cursor.execute("""
        INSERT INTO workflow_executions (
            execution_id, workflow_id, status, error_message, started_at, completed_at
        )
        VALUES (%s, %s, %s, %s, %s, %s)
    """, (execution_id, row['workflow_id'], 'failed', str(e), started_at, datetime.now()))
    
    cursor.execute("""
        UPDATE automation_workflows
        SET run_count = run_count + 1,
            error_count = error_count + 1,
            last_run_at = NOW()
        WHERE workflow_id = %s
    """, (row['workflow_id'],))
    
    conn.commit()
    raise

finally:
    conn.close()
```

---

## 🚀 Implementation Roadmap

### Phase 1: Clarify Separation (Immediate)
- ✅ Document table purposes (this file!)
- ✅ Update code comments to indicate which table is used where
- ✅ Audit current codebase for inconsistent usage

### Phase 2: Add Promotion Workflow (Week 1)
- Create `/api/automation/{id}/promote` endpoint
- Create `/api/automation/{id}/demote` endpoint
- Add UI button "Activate Workflow" (calls promote)
- Add UI button "Deactivate Workflow" (calls demote)

### Phase 3: Implement Sync (Week 2)
- Add database trigger to sync execution stats
- Create `/api/automation/{id}/sync-stats` endpoint
- Add periodic sync job (every 5 minutes)

### Phase 4: Refactor Tools (Week 3)
- Update `automation_create_workflow` to use `visual_automations` only
- Update `automation_schedule_workflow` to check `automation_workflows`
- Update execution tools to read from `automation_workflows` only

### Phase 5: Migration (Week 4)
- Create migration script to sync existing data
- Identify orphaned records (in one table but not the other)
- Run data integrity checks

---

## 📊 Summary Table

| Aspect | `visual_automations` | `automation_workflows` |
|--------|---------------------|------------------------|
| **When to Use** | Design, edit, preview workflows | Execute, schedule, monitor production workflows |
| **Primary User** | Frontend/UI (canvas) | Backend/Scheduler (execution engine) |
| **Data Quality** | Can be incomplete (drafts) | Must be complete and validated |
| **Stability** | Frequently changed (user edits) | Stable (only updated on promotion) |
| **Performance** | Optimized for quick saves | Optimized for fast execution |
| **Query Pattern** | `SELECT` for display/editing | `SELECT` for execution |
| **Deletion** | Soft delete (status='archived') | Hard delete (remove from production) |

---

## 🎯 Key Takeaways

1. **Two tables, two purposes**: Don't treat them as duplicates
2. **Canvas is primary**: `visual_automations` is source of truth for design
3. **Production is derived**: `automation_workflows` is generated from canvas
4. **Use slug as link**: Both tables share the same `slug` for synchronization
5. **Explicit promotion**: Don't auto-sync; use deliberate promote/demote actions
6. **One-way sync for stats**: Execution stats flow back from production to canvas
7. **Never query both simultaneously for execution**: Always use `automation_workflows` for runtime

---

**Last Updated**: November 28, 2024
**Version**: 1.0.0
**Status**: ✅ Analysis Complete

# 📊 Automation Workflow Tables - Visual Guide

## Two-Table Architecture

```
┌──────────────────────────────────────────────────────────────┐
│                    WORKFLOW LIFECYCLE                         │
└──────────────────────────────────────────────────────────────┘

                  USER CREATES WORKFLOW IN CANVAS
                              ↓
┌────────────────────────────────────────────────────────────────┐
│  TABLE: visual_automations                                     │
│  Purpose: Draft/Design Storage                                 │
│  Status: "draft", "active", "paused", "archived"              │
├────────────────────────────────────────────────────────────────┤
│  Fields:                                                       │
│  - automation_id (PK): "wf_abc123_1732029847"                 │
│  - slug (UNIQUE): "quote-request-synergy-1763946900"          │
│  - title: "Quote Request Handler"                             │
│  - ui_json: {"shapes": [...], "connections": [...]}           │
│  - execution_json: {"steps": [...]}                           │
│  - status: "draft"                                            │
│  - is_scheduled: false                                        │
├────────────────────────────────────────────────────────────────┤
│  API Endpoint: GET /api/automation/list                       │
│  Used By: Load Workflow Modal → "Visual Automations" tab     │
└────────────────────────────────────────────────────────────────┘
                              ↓
                  USER CLICKS "PROMOTE TO AUTOMATION"
                              ↓
┌────────────────────────────────────────────────────────────────┐
│  TABLE: automation_workflows                                   │
│  Purpose: Production Scheduled Workflows                       │
│  Status: enabled (true/false)                                 │
├────────────────────────────────────────────────────────────────┤
│  Fields:                                                       │
│  - workflow_id (PK): UUID (gen_random_uuid())                 │
│  - slug (UNIQUE): "quote-request-synergy-1763946900"          │
│  - name: "Quote Request Handler"                              │
│  - workflow_json: {"trigger": {...}, "actions": [...]}        │
│  - canvas_data: {"shapes": [...], "connections": [...]}       │
│  - enabled: true                                              │
│  - run_count: 45                                              │
│  - success_count: 43                                          │
│  - error_count: 2                                             │
├────────────────────────────────────────────────────────────────┤
│  API Endpoint: GET /api/automation/workflows/list  (NEW!)    │
│  Used By: Load Workflow Modal → "Automations" tab            │
└────────────────────────────────────────────────────────────────┘
                              ↓
                    SCHEDULER RUNS WORKFLOW
                              ↓
┌────────────────────────────────────────────────────────────────┐
│  TABLE: automation_executions                                  │
│  Purpose: Execution History & Logs                            │
├────────────────────────────────────────────────────────────────┤
│  Fields:                                                       │
│  - execution_id (PK): Auto-increment                          │
│  - automation_id: Links to visual_automations OR workflows    │
│  - status: "success", "failed", "running"                     │
│  - started_at, completed_at, duration_ms                      │
│  - result_summary, error_message                              │
└────────────────────────────────────────────────────────────────┘
```

---

## Key Differences Between Tables

| Feature | visual_automations | automation_workflows |
|---------|-------------------|---------------------|
| **Purpose** | Design/Draft storage | Production execution |
| **Status Field** | `status` (draft/active/paused) | `enabled` (true/false) |
| **Execution** | Not scheduled | Scheduled/running |
| **Stats Tracking** | `execution_count` only | Full stats (run/success/error) |
| **Visual Data** | `ui_json` (shapes/connections) | `canvas_data` (shapes/connections) |
| **Execution Data** | `execution_json` (generic) | `workflow_json` (structured) |
| **Scheduler** | No scheduler task | Has `scheduler_task_id` |
| **API Endpoint** | `/api/automation/list` | `/api/automation/workflows/list` |

---

## Load Workflow Modal - UI Layout

```
┌─────────────────────────────────────────────────────────────┐
│  Load Workflow                                          [X]  │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  [ Visual Automations ]  [ Automations ]   ← TABS          │
│   ════════════════════    ─────────────                     │
│                                                             │
│  TAB 1: Visual Automations (visual_automations table)      │
│  ┌───────────────────────────────────────────────────┐    │
│  │  📝 Quote Request Handler (DRAFT)                  │    │
│  │  Created: Nov 24, 2025 | Updated: 2 hours ago      │    │
│  │  [Load] [Edit] [Delete]                            │    │
│  └───────────────────────────────────────────────────┘    │
│                                                             │
│  ┌───────────────────────────────────────────────────┐    │
│  │  📝 Email Summarizer (ACTIVE)                      │    │
│  │  Created: Nov 20, 2025 | Updated: 1 day ago        │    │
│  │  [Load] [Edit] [Delete]                            │    │
│  └───────────────────────────────────────────────────┘    │
│                                                             │
│  TAB 2: Automations (automation_workflows table)           │
│  ┌───────────────────────────────────────────────────┐    │
│  │  ⚡ Daily Gmail Summary (RUNNING)                  │    │
│  │  Last run: 2 hours ago | Runs: 45 | Errors: 2      │    │
│  │  [Load] [Pause] [View Stats]                       │    │
│  └───────────────────────────────────────────────────┘    │
│                                                             │
│  ┌───────────────────────────────────────────────────┐    │
│  │  ⚡ Invoice Processor (ENABLED)                    │    │
│  │  Last run: 5 hours ago | Runs: 120 | Errors: 3     │    │
│  │  [Load] [Pause] [View Stats]                       │    │
│  └───────────────────────────────────────────────────┘    │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

---

## Frontend Loading Logic

### Before Fix (Only visual_automations):
```javascript
async loadWorkflows() {
    const response = await fetch('/api/automation/list');
    const data = await response.json();
    this.workflows = data.workflows;  // ❌ Only drafts
    this.renderWorkflowList();
}
```

### After Fix (Both tables):
```javascript
async loadWorkflows() {
    // ✅ Load BOTH tables in parallel
    const [visualResponse, productionResponse] = await Promise.all([
        fetch('/api/automation/list'),           // visual_automations
        fetch('/api/automation/workflows/list')  // automation_workflows
    ]);
    
    // Parse responses
    let visualWorkflows = [];
    let productionWorkflows = [];
    
    if (visualResponse.ok) {
        const data = await visualResponse.json();
        visualWorkflows = data.workflows.map(w => ({
            ...w, 
            source: 'visual_automations'  // ✅ Tag source
        }));
    }
    
    if (productionResponse.ok) {
        const data = await productionResponse.json();
        productionWorkflows = data.workflows.map(w => ({
            ...w, 
            source: 'automation_workflows'  // ✅ Tag source
        }));
    }
    
    // Store separately for tab filtering
    this.visualWorkflows = visualWorkflows;
    this.productionWorkflows = productionWorkflows;
    this.workflows = [...visualWorkflows, ...productionWorkflows];
    
    this.renderWorkflowList();  // ✅ Shows both types
}
```

---

## Backend Endpoint Comparison

### Endpoint 1: Visual Automations (Existing)
```python
@automation_bp.route('/list', methods=['GET'])
def list_automations():
    """List visual automation drafts"""
    query = """
        SELECT automation_id, slug, title, ui_json, execution_json, 
               status, created_at, updated_at, execution_count
        FROM visual_automations
        WHERE user_id = %s
        ORDER BY updated_at DESC
    """
    # Returns: workflows with status='draft/active/paused'
```

### Endpoint 2: Production Automations (NEW)
```python
@automation_bp.route('/workflows/list', methods=['GET'])
def list_production_workflows():
    """List production scheduled workflows"""
    query = """
        SELECT workflow_id, slug, name, workflow_json, canvas_data,
               enabled, run_count, success_count, error_count,
               last_run_at, created_at, updated_at
        FROM automation_workflows
        WHERE user_id = %s
        ORDER BY updated_at DESC
    """
    # Returns: workflows with enabled=true/false + execution stats
```

---

## Data Flow Diagram

```
┌─────────────┐
│   USER      │
│  (Canvas)   │
└──────┬──────┘
       │ Creates workflow
       ↓
┌─────────────────────────────────┐
│  POST /api/automation/save      │  ← Auto-save (every 2 seconds)
│  ↓                               │
│  visual_automations INSERT/UPDATE│  ← UPSERT (ON CONFLICT DO UPDATE)
└─────────────────────────────────┘
       │
       │ User clicks "Promote to Automation"
       ↓
┌─────────────────────────────────┐
│  POST /api/automation/promote   │
│  ↓                               │
│  automation_workflows INSERT    │  ← Creates production workflow
│  ↓                               │
│  Scheduler registers cron task  │  ← APScheduler adds job
└─────────────────────────────────┘
       │
       │ Scheduled time arrives
       ↓
┌─────────────────────────────────┐
│  Scheduler executes workflow    │
│  ↓                               │
│  automation_executions INSERT   │  ← Logs execution
│  ↓                               │
│  automation_workflows UPDATE    │  ← Increment run_count
└─────────────────────────────────┘
       │
       │ User opens Load Workflow modal
       ↓
┌─────────────────────────────────┐
│  GET /api/automation/list       │  ← Tab 1: Visual Automations
│  GET /api/automation/workflows/list │  ← Tab 2: Automations
│  ↓                               │
│  Render modal with both tabs    │
└─────────────────────────────────┘
```

---

## Slug Uniqueness Enforcement

### Both tables enforce unique slugs:

```sql
-- visual_automations
ALTER TABLE visual_automations 
ADD CONSTRAINT visual_automations_slug_key UNIQUE (slug);

-- automation_workflows
ALTER TABLE automation_workflows 
ADD CONSTRAINT automation_workflows_slug_key UNIQUE (slug);
```

### UPSERT prevents duplicates:
```sql
-- PostgreSQL (Supabase)
INSERT INTO visual_automations (...) VALUES (...)
ON CONFLICT (slug) DO UPDATE SET
    title = EXCLUDED.title,
    ui_json = EXCLUDED.ui_json,
    updated_at = CURRENT_TIMESTAMP;

-- SQLite (Local)
INSERT OR REPLACE INTO visual_automations (...) VALUES (...);
```

---

## Testing Scenarios

### Scenario 1: Draft Workflow
```
1. User creates workflow in canvas
2. Auto-save → visual_automations INSERT
3. Load Workflow modal → Shows in "Visual Automations" tab
4. Status: "draft", No execution stats
```

### Scenario 2: Promoted Workflow
```
1. User clicks "Promote to Automation"
2. Backend:
   - Reads from visual_automations
   - Creates entry in automation_workflows
   - Schedules with APScheduler
3. Load Workflow modal → Shows in BOTH tabs:
   - "Visual Automations" tab: Original draft
   - "Automations" tab: Production version with stats
```

### Scenario 3: Executed Workflow
```
1. Scheduler triggers workflow
2. Backend:
   - Creates automation_executions record
   - Updates automation_workflows.run_count
   - Updates success_count or error_count
3. Load Workflow modal → "Automations" tab shows updated stats
```

---

## Migration Path

### Existing Workflows:
- ✅ Stay in `visual_automations` table
- ✅ Visible in "Visual Automations" tab
- ✅ Can be promoted to `automation_workflows` anytime

### New Workflows:
- ✅ Created in `visual_automations` (draft status)
- ✅ Promoted to `automation_workflows` when scheduled
- ✅ Both entries maintained (draft + production)

### No Data Loss:
- ✅ Both tables coexist independently
- ✅ No migration script required
- ✅ Backward compatible

---

**Document Version:** 1.0.0  
**Last Updated:** November 28, 2025  
**Status:** ✅ Production Ready

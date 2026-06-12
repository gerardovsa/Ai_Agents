# Automation Slug Architecture - Complete Integration Guide

**Date:** November 17, 2024  
**Status:** DESIGN COMPLETE  
**Database:** Updated with automation_slug + automation_title columns

---

## Architecture Overview

### Two-Column Design Pattern

Your `sessions.threads` table now has **TWO distinct workflow linking mechanisms**:

| Column | Purpose | Use Case | System |
|--------|---------|----------|--------|
| `workflow_slug` + `workflow_title` | **UI Canvas Link** | Visual editing, design phase | Workflow Canvas UI |
| `automation_slug` + `automation_title` | **Execution Link** | Production automation, running workflows | Automation Engine |

---

## Complete Workflow Lifecycle

```
┌─────────────────────────────────────────────────────────────────┐
│ PHASE 1: DESIGN (workflow_slug)                                 │
├─────────────────────────────────────────────────────────────────┤
│ User: Create new workflow in visual canvas                      │
│ System: Generate workflow_slug (e.g., "invoice-automation-v1")  │
│ Database: UPDATE threads SET workflow_slug='...' WHERE id=X     │
│ AI: Can read/modify workflow_json + canvas_data via slug        │
│ UI: Shows green "Workflow" pill on thread card                  │
└─────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│ PHASE 2: FINALIZATION (workflow_slug → automation_slug)         │
├─────────────────────────────────────────────────────────────────┤
│ User: Click "Publish Workflow" or "Enable Automation"           │
│ System: Validate workflow structure, test connections           │
│ System: Create automation record in automation_workflows table  │
│ System: Generate automation_slug (e.g., "auto-invoice-live")    │
│ Database: UPDATE threads SET automation_slug='...' WHERE id=X   │
│ Result: workflow_slug REMAINS (for editing), automation_slug    │
│         added (for execution)                                    │
└─────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│ PHASE 3: EXECUTION (automation_slug)                            │
├─────────────────────────────────────────────────────────────────┤
│ Trigger: Schedule, webhook, or manual execution                 │
│ System: Load automation by automation_slug                      │
│ System: Execute workflow nodes in sequence                      │
│ System: Log execution to workflow_executions table              │
│ AI: Can monitor execution, see logs, debug issues               │
│ UI: Shows orange "Automation" pill on thread card               │
└─────────────────────────────────────────────────────────────────┘
```

---

## Database Integration

### Column Usage Examples

**Design Phase Only:**
```sql
-- User creates workflow in canvas, AI helps design it
UPDATE sessions.threads SET
  workflow_slug = 'invoice-workflow-draft',
  workflow_title = 'Invoice Processing Workflow'
WHERE id = 123;

-- Result: Thread linked to canvas for editing
-- automation_slug = NULL (not published yet)
```

**After Publishing:**
```sql
-- User publishes workflow, becomes live automation
UPDATE sessions.threads SET
  workflow_slug = 'invoice-workflow-draft',  -- Keep for editing
  workflow_title = 'Invoice Processing Workflow',
  automation_slug = 'auto-invoice-live',      -- NEW: Execution link
  automation_title = 'Invoice Automation (Live)'
WHERE id = 123;

-- Result: Thread linked to BOTH canvas (for editing) AND automation (for execution)
```

**After Unpublishing/Pausing:**
```sql
-- User pauses automation but keeps design
UPDATE sessions.threads SET
  workflow_slug = 'invoice-workflow-draft',  -- Keep for editing
  workflow_title = 'Invoice Processing Workflow',
  automation_slug = NULL,                     -- Remove execution link
  automation_title = NULL
WHERE id = 123;

-- Result: Thread linked to canvas only, automation disabled
```

---

## UI Pill Display Logic

### Visual Indicators on Thread Cards

**Thread with workflow_slug only (Design phase):**
```html
<div class="thread-item">
  <span class="thread-title">Invoice Processing</span>
  <div class="thread-pills">
    <span class="pill-workflow">🎨 Workflow</span>  <!-- Orange -->
  </div>
</div>
```

**Thread with automation_slug only (Execution only, no canvas):**
```html
<div class="thread-item">
  <span class="thread-title">Invoice Processing</span>
  <div class="thread-pills">
    <span class="pill-automation">🤖 Automation</span>  <!-- Blue -->
  </div>
</div>
```

**Thread with BOTH (Design + Execution):**
```html
<div class="thread-item">
  <span class="thread-title">Invoice Processing</span>
  <div class="thread-pills">
    <span class="pill-workflow">🎨 Workflow</span>     <!-- Orange -->
    <span class="pill-automation">🤖 Automation</span> <!-- Blue -->
  </div>
</div>
```

---

## Implementation: When to Set automation_slug

### Option 1: Manual Publishing (Recommended)

**User Action:** Click "Publish Workflow" button in canvas

**Backend Endpoint:** `POST /api/automation/publish`

```javascript
// Request
{
  workflow_slug: 'invoice-workflow-draft',
  thread_id: 123
}

// Backend Process:
1. Validate workflow structure (all nodes connected, valid config)
2. Create automation record in automation_workflows table
3. Generate automation_slug (e.g., workflow_slug + '-live')
4. Update thread with automation_slug + automation_title
5. Enable workflow in automation_workflows (enabled=true)

// Response
{
  success: true,
  automation_slug: 'auto-invoice-live',
  automation_title: 'Invoice Automation (Live)',
  message: 'Workflow published successfully'
}

// SQL Executed:
INSERT INTO automation_workflows (user_id, name, slug, workflow_json, enabled)
VALUES (1, 'Invoice Automation', 'auto-invoice-live', '...', true)
RETURNING workflow_id, slug;

UPDATE sessions.threads SET
  automation_slug = 'auto-invoice-live',
  automation_title = 'Invoice Automation (Live)',
  updated_at = NOW()
WHERE id = 123;
```

---

### Option 2: Automatic Publishing on Save

**Trigger:** Every time workflow is saved with `enabled=true`

**Backend Logic:**
```python
def save_workflow(workflow_data, thread_id):
    # Save workflow to automation_workflows table
    workflow = create_or_update_workflow(workflow_data)
    
    # If workflow is enabled, link it to thread as automation
    if workflow['enabled']:
        update_thread_automation_link(
            thread_id=thread_id,
            automation_slug=workflow['slug'],
            automation_title=workflow['name']
        )
    else:
        # If disabled, keep workflow_slug but remove automation_slug
        clear_thread_automation_link(thread_id)
```

---

### Option 3: AI-Triggered Publishing

**Scenario:** AI detects workflow is complete and suggests publishing

**AI Message:**
```
AI: "Your workflow looks complete! All nodes are connected and configured. 
     Would you like me to publish this as a live automation?"

User: "Yes, publish it"

AI: [Calls automation_workflow_create tool]
AI: [Calls update_thread_automation_link]
AI: "✅ Automation published! Your workflow is now live and will run 
     automatically when triggered."
```

---

## AI Tool Integration

### New Tool: `link_thread_to_automation`

**Schema:** `tools/schemas/thread_automation_tools.json`

```json
{
  "platform": "thread_management",
  "description": "Link AI threads to workflow automations",
  "tools": [
    {
      "name": "link_thread_to_automation",
      "description": "Link a thread to a published automation workflow",
      "platform": "thread_management",
      "parameters": {
        "type": "object",
        "properties": {
          "thread_id": {
            "type": "string",
            "description": "Thread ID to link"
          },
          "automation_slug": {
            "type": "string",
            "description": "Automation workflow slug"
          },
          "automation_title": {
            "type": "string",
            "description": "Display name for automation"
          }
        },
        "required": ["thread_id", "automation_slug"]
      }
    },
    {
      "name": "unlink_thread_from_automation",
      "description": "Remove automation link from thread (keeps workflow link)",
      "platform": "thread_management",
      "parameters": {
        "type": "object",
        "properties": {
          "thread_id": {
            "type": "string",
            "description": "Thread ID to unlink"
          }
        },
        "required": ["thread_id"]
      }
    },
    {
      "name": "get_thread_automation_status",
      "description": "Check if thread has linked automation and its execution status",
      "platform": "thread_management",
      "parameters": {
        "type": "object",
        "properties": {
          "thread_id": {
            "type": "string",
            "description": "Thread ID to check"
          }
        },
        "required": ["thread_id"]
      }
    }
  ]
}
```

**Implementation:** `tools/implementations/thread_automation.py`

```python
"""
Thread Automation Linking Tools

Functions:
- link_thread_to_automation: Link thread to published automation
- unlink_thread_from_automation: Remove automation link
- get_thread_automation_status: Check automation status
"""

import psycopg2
from typing import Dict, Any, Optional


def link_thread_to_automation(
    thread_id: str,
    automation_slug: str,
    automation_title: Optional[str] = None,
    **kwargs
) -> Dict[str, Any]:
    """
    Link a thread to a published automation workflow
    
    Args:
        thread_id: Thread ID
        automation_slug: Automation workflow slug
        automation_title: Display name (optional)
        **kwargs: Credential injection
    
    Returns:
        Dict with success status and automation info
    """
    # Get database connection
    conn = psycopg2.connect(
        host='localhost',
        database='ai_infrastructure',
        user='postgres',
        password=kwargs.get('db_password', '')
    )
    cursor = conn.cursor()
    
    try:
        # Verify automation exists
        cursor.execute("""
            SELECT workflow_id, name, enabled
            FROM automation_workflows
            WHERE slug = %s
        """, (automation_slug,))
        
        automation = cursor.fetchone()
        if not automation:
            return {
                'success': False,
                'error': f'Automation "{automation_slug}" not found'
            }
        
        workflow_id, name, enabled = automation
        
        if not enabled:
            return {
                'success': False,
                'error': f'Automation "{automation_slug}" is disabled'
            }
        
        # Use automation name if title not provided
        if not automation_title:
            automation_title = name
        
        # Update thread with automation link
        cursor.execute("""
            UPDATE sessions.threads SET
                automation_slug = %s,
                automation_title = %s,
                updated_at = NOW()
            WHERE id = %s
            RETURNING thread_slug, name
        """, (automation_slug, automation_title, thread_id))
        
        result = cursor.fetchone()
        if not result:
            return {
                'success': False,
                'error': f'Thread {thread_id} not found'
            }
        
        thread_slug, thread_name = result
        
        conn.commit()
        
        return {
            'success': True,
            'thread_id': thread_id,
            'thread_slug': thread_slug,
            'thread_name': thread_name,
            'automation_slug': automation_slug,
            'automation_title': automation_title,
            'automation_id': workflow_id,
            'message': f'Thread linked to automation "{automation_title}"'
        }
    
    except Exception as e:
        conn.rollback()
        return {
            'success': False,
            'error': str(e)
        }
    finally:
        cursor.close()
        conn.close()


def unlink_thread_from_automation(
    thread_id: str,
    **kwargs
) -> Dict[str, Any]:
    """
    Remove automation link from thread (keeps workflow_slug)
    
    Args:
        thread_id: Thread ID
        **kwargs: Credential injection
    
    Returns:
        Dict with success status
    """
    conn = psycopg2.connect(
        host='localhost',
        database='ai_infrastructure',
        user='postgres',
        password=kwargs.get('db_password', '')
    )
    cursor = conn.cursor()
    
    try:
        cursor.execute("""
            UPDATE sessions.threads SET
                automation_slug = NULL,
                automation_title = NULL,
                updated_at = NOW()
            WHERE id = %s
            RETURNING thread_slug, name
        """, (thread_id,))
        
        result = cursor.fetchone()
        if not result:
            return {
                'success': False,
                'error': f'Thread {thread_id} not found'
            }
        
        thread_slug, thread_name = result
        
        conn.commit()
        
        return {
            'success': True,
            'thread_id': thread_id,
            'thread_slug': thread_slug,
            'thread_name': thread_name,
            'message': 'Automation link removed from thread'
        }
    
    except Exception as e:
        conn.rollback()
        return {
            'success': False,
            'error': str(e)
        }
    finally:
        cursor.close()
        conn.close()


def get_thread_automation_status(
    thread_id: str,
    **kwargs
) -> Dict[str, Any]:
    """
    Get thread's automation link status and execution history
    
    Args:
        thread_id: Thread ID
        **kwargs: Credential injection
    
    Returns:
        Dict with automation status and execution info
    """
    conn = psycopg2.connect(
        host='localhost',
        database='ai_infrastructure',
        user='postgres',
        password=kwargs.get('db_password', '')
    )
    cursor = conn.cursor()
    
    try:
        # Get thread with automation links
        cursor.execute("""
            SELECT 
                t.thread_slug,
                t.name,
                t.workflow_slug,
                t.workflow_title,
                t.automation_slug,
                t.automation_title
            FROM sessions.threads t
            WHERE t.id = %s
        """, (thread_id,))
        
        thread = cursor.fetchone()
        if not thread:
            return {
                'success': False,
                'error': f'Thread {thread_id} not found'
            }
        
        thread_slug, name, workflow_slug, workflow_title, automation_slug, automation_title = thread
        
        result = {
            'success': True,
            'thread_id': thread_id,
            'thread_slug': thread_slug,
            'thread_name': name,
            'has_workflow': workflow_slug is not None,
            'has_automation': automation_slug is not None
        }
        
        # Add workflow info if linked
        if workflow_slug:
            result['workflow'] = {
                'slug': workflow_slug,
                'title': workflow_title
            }
        
        # Add automation info if linked
        if automation_slug:
            # Get automation details
            cursor.execute("""
                SELECT 
                    workflow_id,
                    enabled,
                    last_run_at,
                    run_count,
                    success_count,
                    error_count
                FROM automation_workflows
                WHERE slug = %s
            """, (automation_slug,))
            
            automation = cursor.fetchone()
            if automation:
                workflow_id, enabled, last_run, run_count, success_count, error_count = automation
                
                result['automation'] = {
                    'slug': automation_slug,
                    'title': automation_title,
                    'workflow_id': workflow_id,
                    'enabled': enabled,
                    'last_run_at': last_run.isoformat() if last_run else None,
                    'execution_stats': {
                        'total_runs': run_count or 0,
                        'successful': success_count or 0,
                        'failed': error_count or 0,
                        'success_rate': f'{(success_count / run_count * 100):.1f}%' if run_count > 0 else 'N/A'
                    }
                }
                
                # Get recent executions
                cursor.execute("""
                    SELECT 
                        execution_id,
                        status,
                        started_at,
                        completed_at,
                        duration_ms,
                        error_message
                    FROM workflow_executions
                    WHERE workflow_id = %s
                    ORDER BY started_at DESC
                    LIMIT 5
                """, (workflow_id,))
                
                executions = cursor.fetchall()
                result['automation']['recent_executions'] = [
                    {
                        'execution_id': exec_id,
                        'status': status,
                        'started_at': started.isoformat() if started else None,
                        'completed_at': completed.isoformat() if completed else None,
                        'duration_ms': duration,
                        'error': error
                    }
                    for exec_id, status, started, completed, duration, error in executions
                ]
        
        return result
    
    except Exception as e:
        return {
            'success': False,
            'error': str(e)
        }
    finally:
        cursor.close()
        conn.close()
```

---

## Frontend Integration

### Update Thread Manager to Show Automation Pills

**File:** `UI/business-ai-platform-v2.html`

**Location:** `ThreadManager.updateThreadPills()` function

```javascript
updateThreadPills(threadElement, thread) {
    let pillsContainer = threadElement.querySelector('.thread-ui-pills');
    if (!pillsContainer) {
        pillsContainer = document.createElement('div');
        pillsContainer.className = 'thread-ui-pills';
        pillsContainer.style.cssText = 'display: flex; gap: 6px; margin-top: 6px; flex-wrap: wrap;';
        threadElement.appendChild(pillsContainer);
    }

    pillsContainer.innerHTML = '';

    // Synergy pill (green)
    if (thread.synergy_card_id) {
        const synergyPill = document.createElement('span');
        synergyPill.className = 'thread-pill thread-pill-synergy';
        synergyPill.style.cssText = 'background: #10b981; color: white; padding: 3px 8px; border-radius: 12px; font-size: 11px; display: flex; align-items: center; gap: 4px;';
        synergyPill.innerHTML = `<i class="fas fa-link" style="font-size: 10px;"></i> Synergy`;
        synergyPill.title = thread.synergy_card_name || thread.synergy_card_id;
        pillsContainer.appendChild(synergyPill);
    }

    // Workflow pill (orange) - Design/Canvas link
    if (thread.workflow_slug) {
        const workflowPill = document.createElement('span');
        workflowPill.className = 'thread-pill thread-pill-workflow';
        workflowPill.style.cssText = 'background: #f97316; color: white; padding: 3px 8px; border-radius: 12px; font-size: 11px; display: flex; align-items: center; gap: 4px;';
        workflowPill.innerHTML = `<i class="fas fa-palette" style="font-size: 10px;"></i> Workflow`;
        workflowPill.title = thread.workflow_title || thread.workflow_slug;
        pillsContainer.appendChild(workflowPill);
    }

    // Automation pill (blue) - Execution/Live link
    if (thread.automation_slug) {
        const automationPill = document.createElement('span');
        automationPill.className = 'thread-pill thread-pill-automation';
        automationPill.style.cssText = 'background: #3b82f6; color: white; padding: 3px 8px; border-radius: 12px; font-size: 11px; display: flex; align-items: center; gap: 4px;';
        automationPill.innerHTML = `<i class="fas fa-robot" style="font-size: 10px;"></i> Automation`;
        automationPill.title = thread.automation_title || thread.automation_slug;
        pillsContainer.appendChild(automationPill);
    }
}
```

---

## Use Case Examples

### Use Case 1: Design Workflow in Canvas

```
User: "Create a workflow to process invoices"

1. User opens Workflow Canvas module
2. Creates workflow with visual nodes
3. System generates workflow_slug='invoice-workflow-v1'
4. System updates thread: workflow_slug='invoice-workflow-v1'
5. AI can now access workflow via automation_workflow_get(slug='invoice-workflow-v1')
6. Thread shows orange "Workflow" pill

Database state:
- workflow_slug: 'invoice-workflow-v1'
- workflow_title: 'Invoice Processing'
- automation_slug: NULL  (not published yet)
- automation_title: NULL
```

---

### Use Case 2: Publish Workflow as Automation

```
User: "Publish this workflow and make it live"

1. User clicks "Publish" button in Workflow Canvas
2. System validates workflow structure
3. System creates automation record in automation_workflows table
4. System generates automation_slug='auto-invoice-v1-live'
5. System updates thread: automation_slug='auto-invoice-v1-live'
6. Thread now shows BOTH orange "Workflow" + blue "Automation" pills

Database state:
- workflow_slug: 'invoice-workflow-v1'      (keeps for editing)
- workflow_title: 'Invoice Processing'
- automation_slug: 'auto-invoice-v1-live'  (NEW - for execution)
- automation_title: 'Invoice Automation (Live)'
```

---

### Use Case 3: Monitor Automation Execution

```
User: "How many times has my invoice automation run?"

AI calls: get_thread_automation_status(thread_id=current_thread)

Response:
{
  "has_automation": true,
  "automation": {
    "slug": "auto-invoice-v1-live",
    "title": "Invoice Automation (Live)",
    "enabled": true,
    "execution_stats": {
      "total_runs": 47,
      "successful": 45,
      "failed": 2,
      "success_rate": "95.7%"
    },
    "recent_executions": [...]
  }
}

AI: "Your Invoice Automation has run 47 times with a 95.7% success rate.
     45 successful executions, 2 failures. Would you like to see the error logs?"
```

---

### Use Case 4: Unpublish Automation (Keep Design)

```
User: "Pause the automation but keep the workflow design"

1. User clicks "Unpublish" or "Disable" in Workflow Canvas
2. System sets automation_workflows.enabled=false
3. System updates thread: automation_slug=NULL, automation_title=NULL
4. Thread shows only orange "Workflow" pill (automation pill removed)

Database state:
- workflow_slug: 'invoice-workflow-v1'  (kept for editing)
- workflow_title: 'Invoice Processing'
- automation_slug: NULL                  (removed)
- automation_title: NULL
```

---

## Database Query Examples

### Get All Threads with Active Automations

```sql
SELECT 
    t.id,
    t.thread_slug,
    t.name AS thread_name,
    t.automation_slug,
    t.automation_title,
    aw.workflow_id,
    aw.enabled,
    aw.run_count,
    aw.success_count
FROM sessions.threads t
INNER JOIN automation_workflows aw ON t.automation_slug = aw.slug
WHERE aw.enabled = true
ORDER BY aw.last_run_at DESC;
```

---

### Get Thread with Both Workflow + Automation Links

```sql
SELECT 
    t.id,
    t.thread_slug,
    t.name,
    t.workflow_slug,
    t.workflow_title,
    t.automation_slug,
    t.automation_title
FROM sessions.threads t
WHERE t.workflow_slug IS NOT NULL
  AND t.automation_slug IS NOT NULL;
```

---

### Find Automations Without Thread Links (Orphaned)

```sql
SELECT 
    aw.workflow_id,
    aw.slug,
    aw.name
FROM automation_workflows aw
LEFT JOIN sessions.threads t ON t.automation_slug = aw.slug
WHERE t.id IS NULL
  AND aw.enabled = true;
```

---

## Summary: When to Use Each Column

| Scenario | workflow_slug | automation_slug |
|----------|---------------|-----------------|
| **Designing workflow in canvas** | ✅ SET | ❌ NULL |
| **Testing workflow** | ✅ SET | ❌ NULL |
| **Publishing workflow** | ✅ KEEP | ✅ SET |
| **Running automation** | ✅ KEEP | ✅ SET |
| **Pausing automation** | ✅ KEEP | ❌ NULL |
| **Editing live automation** | ✅ KEEP | ✅ KEEP |
| **Deleting automation** | ✅ KEEP | ❌ NULL |
| **Archiving workflow** | ❌ NULL | ❌ NULL |

---

## Migration Script

```sql
-- Add columns to existing threads table (if not already added)
ALTER TABLE sessions.threads ADD COLUMN IF NOT EXISTS automation_slug TEXT;
ALTER TABLE sessions.threads ADD COLUMN IF NOT EXISTS automation_title TEXT;

-- Add indexes for performance
CREATE INDEX IF NOT EXISTS idx_threads_automation_slug ON sessions.threads(automation_slug);
CREATE INDEX IF NOT EXISTS idx_threads_workflow_slug ON sessions.threads(workflow_slug);

-- Verify columns exist
SELECT 
    column_name,
    data_type,
    is_nullable
FROM information_schema.columns
WHERE table_schema = 'sessions'
  AND table_name = 'threads'
  AND column_name IN ('automation_slug', 'automation_title', 'workflow_slug', 'workflow_title');
```

---

## Conclusion

**Perfect Architecture! ✅**

Your two-column design (`workflow_slug` + `automation_slug`) elegantly separates:

1. **Design/Editing Phase** → `workflow_slug` (Canvas UI)
2. **Execution Phase** → `automation_slug` (Live Automation)

**Key Benefits:**
- ✅ Clear separation of concerns
- ✅ Keep workflow editable even when automation is live
- ✅ Can pause automation without losing workflow design
- ✅ Thread can link to BOTH canvas and automation simultaneously
- ✅ Visual pills clearly show what's linked (orange=design, blue=live)

**Status:** Architecture design complete, ready for implementation! 🎉

---

**Last Updated:** November 17, 2024  
**Database Columns:** automation_slug + automation_title added  
**Integration:** Workflow Canvas + Automation Engine  
**Documentation:** Complete architecture guide created

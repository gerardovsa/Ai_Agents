# SYNERGY MILESTONE MIGRATION - COMPLETE IMPLEMENTATION PLAN

## 🎯 OVERVIEW

Migrating Synergy sessions from:
- **BEFORE:** `next_steps` (JSON array) + `checklist` (JSON array with subtasks)
- **AFTER:** Proper relational structure: `milestones` → `tasks` → `subtasks`

---

## ✅ STEP 1: DATABASE SCHEMA (COMPLETED)

**File Created:** `data/synergy_milestone_migration.sql`

**New Tables:**
1. `synergy_sessions.milestones` - Top-level project phases
2. `synergy_sessions.tasks` - Tasks within each milestone
3. `synergy_sessions.subtasks` - Subtasks within each task
4. `synergy_sessions.milestone_comments` - Comments/notes per milestone/task
5. `synergy_sessions.milestone_history` - Version control for milestones

**Views Created:**
1. `v_milestone_progress` - Calculates completion % per milestone
2. `v_task_progress` - Calculates subtask completion % per task

**Migration Strategy:**
- Keep `next_steps` and `checklist` columns → rename to `next_steps_deprecated`, `checklist_deprecated`
- Add `uses_milestones` BOOLEAN flag to indicate new structure
- Allows gradual migration and rollback capability

---

## 📋 STEP 2: BACKEND API ROUTES (synergy_routes.py)

**File to Update:** `AI_infrastructure/routes/synergy_routes.py`

### New Endpoints to Add:

#### 1. **POST** `/api/synergy/milestone/create`
**Purpose:** Create new milestone with tasks in one call

**Request Body:**
```json
{
  "session_id": "sess_abc123",
  "milestone_name": "Database Setup",
  "description": "Create customer database and import contacts",
  "tasks": [
    "Create Google Sheet",
    {
      "task": "Import existing contacts",
      "subtasks": ["Export from old CRM", "Clean data", "Import"]
    }
  ],
  "due_date": "2025-11-25",
  "priority": "high",
  "estimated_hours": 3
}
```

**Response:**
```json
{
  "success": true,
  "milestone_id": "ms_a1b2c3d4",
  "milestone_number": 1,
  "tasks_created": 2,
  "subtasks_created": 3
}
```

---

#### 2. **POST** `/api/synergy/milestone/<milestone_id>/task/create`
**Purpose:** Add task to existing milestone (incremental)

**Request Body:**
```json
{
  "task": "Set up database backups",
  "subtasks": ["Configure automated backups", "Test restore procedure"]
}
```

**Response:**
```json
{
  "success": true,
  "task_id": "task_x1y2z3",
  "subtasks_created": 2
}
```

---

#### 3. **POST** `/api/synergy/task/<task_id>/subtask/create`
**Purpose:** Add subtask to existing task

**Request Body:**
```json
{
  "subtask": "Validate data integrity"
}
```

**Response:**
```json
{
  "success": true,
  "subtask_id": "sub_p1q2r3"
}
```

---

#### 4. **PATCH** `/api/synergy/task/<task_id>/complete`
**Purpose:** Mark task complete (auto-completes all subtasks)

**Request Body:**
```json
{
  "completed": true
}
```

**Response:**
```json
{
  "success": true,
  "task_id": "task_x1y2z3",
  "completed": true,
  "completed_at": "2025-11-19T14:30:00Z",
  "milestone_completed": false,
  "auto_completed_subtasks": 3
}
```

---

#### 5. **PATCH** `/api/synergy/subtask/<subtask_id>/complete`
**Purpose:** Mark subtask complete (auto-checks if parent task should complete)

**Request Body:**
```json
{
  "completed": true
}
```

**Response:**
```json
{
  "success": true,
  "subtask_id": "sub_p1q2r3",
  "completed": true,
  "task_auto_completed": true,
  "milestone_auto_completed": false
}
```

---

#### 6. **PATCH** `/api/synergy/milestone/<milestone_id>/complete`
**Purpose:** Mark entire milestone complete (completes all tasks/subtasks)

**Request Body:**
```json
{
  "completed": true
}
```

**Response:**
```json
{
  "success": true,
  "milestone_id": "ms_a1b2c3d4",
  "completed": true,
  "tasks_completed": 5,
  "subtasks_completed": 12
}
```

---

#### 7. **GET** `/api/synergy/milestone/<milestone_id>/progress`
**Purpose:** Get completion percentage and remaining items

**Response:**
```json
{
  "milestone_id": "ms_a1b2c3d4",
  "milestone_name": "Database Setup",
  "progress_percentage": 66.7,
  "tasks_completed": 2,
  "tasks_total": 3,
  "subtasks_completed": 5,
  "subtasks_total": 8,
  "remaining_tasks": ["Set up validation"],
  "blocked_tasks": [],
  "estimated_completion": "2025-11-21",
  "due_date": "2025-11-25",
  "on_track": true
}
```

---

#### 8. **POST** `/api/synergy/task/<task_id>/block`
**Purpose:** Mark task as blocked with reason

**Request Body:**
```json
{
  "blocked": true,
  "blocker_reason": "Waiting for client brand guidelines",
  "blocker_type": "external",
  "blocked_by_user": "client_john@example.com",
  "expected_resolution": "2025-11-22"
}
```

**Response:**
```json
{
  "success": true,
  "task_id": "task_x1y2z3",
  "blocked": true,
  "blocked_since": "2025-11-19T14:30:00Z"
}
```

---

#### 9. **GET** `/api/synergy/<session_id>/milestones`
**Purpose:** Get all milestones for session (with tasks and subtasks)

**Response:**
```json
{
  "success": true,
  "session_id": "sess_abc123",
  "milestones": [
    {
      "milestone_id": "ms_001",
      "milestone_number": 1,
      "milestone_name": "Database Setup",
      "description": "...",
      "completed": false,
      "progress_percentage": 66.7,
      "due_date": "2025-11-25",
      "priority": "high",
      "tasks": [
        {
          "task_id": "task_001",
          "task": "Create Google Sheet",
          "completed": true,
          "subtasks": []
        },
        {
          "task_id": "task_002",
          "task": "Import contacts",
          "completed": false,
          "blocked": true,
          "blocker_reason": "...",
          "subtasks": [...]
        }
      ]
    }
  ]
}
```

---

#### 10. **POST** `/api/synergy/milestone/<milestone_id>/comment`
**Purpose:** Add comment/note to milestone or task

**Request Body:**
```json
{
  "task_id": "task_001",  // Optional, omit for milestone-level comment
  "author": "ai_agent",
  "comment_text": "Created spreadsheet with 15 columns",
  "comment_type": "update"  // note | update | decision | question
}
```

---

#### 11. **PATCH** `/api/synergy/milestone/reorder`
**Purpose:** Change milestone order

**Request Body:**
```json
{
  "session_id": "sess_abc123",
  "milestone_ids_ordered": ["ms_003", "ms_001", "ms_002"]
}
```

---

### Modified Existing Endpoints:

#### **GET** `/api/synergy/<session_id>`
**Change:** Add `milestones` to response if `uses_milestones = TRUE`

**Response:**
```json
{
  "success": true,
  "session": {
    "session_id": "sess_abc123",
    "title": "Email Campaign",
    "uses_milestones": true,
    "milestones": [...],  // ← NEW
    "next_steps_deprecated": [...],  // Old data archived
    "checklist_deprecated": [...]    // Old data archived
  }
}
```

---

#### **POST** `/api/synergy/create`
**Change:** Accept `milestones` in request body instead of `next_steps`

**Request Body (NEW format):**
```json
{
  "title": "Email Campaign",
  "description": "...",
  "platforms_involved": ["gmail", "google_sheets"],
  "milestones": [  // ← NEW (replaces next_steps)
    {
      "milestone_name": "Database Setup",
      "tasks": ["Create sheet", "Import contacts"]
    }
  ]
}
```

---

## 🎨 STEP 3: FRONTEND - SYNERGY CARD RENDERER MODULE

**File to Update:** `UI/external/modules/synergy-card-renderer.js`

### Changes Needed:

1. **Replace Methods:**
   - Remove: `renderNextSteps()`
   - Remove: `renderChecklist()`
   - Add: `renderMilestones(session)` - New unified method

2. **New Method Signature:**
```javascript
renderMilestones(milestones, sessionId) {
    let html = `
        <div class="synergy-card-section milestones-section">
            <div class="synergy-card-section-title">
                <i class="fas fa-bullseye"></i>
                Milestones (${completedCount}/${totalCount})
            </div>
            <div class="milestones-container">
    `;
    
    milestones.forEach(milestone => {
        html += this.renderMilestone(milestone, sessionId);
    });
    
    html += `</div></div>`;
    return html;
}
```

3. **New Helper Methods:**
```javascript
renderMilestone(milestone, sessionId) {
    const progress = this.calculateMilestoneProgress(milestone);
    const isExpanded = this.isMilestoneExpanded(milestone.milestone_id);
    
    return `
        <div class="milestone-item ${milestone.completed ? 'completed' : ''}" 
             data-milestone-id="${milestone.milestone_id}">
            
            <!-- Milestone Header -->
            <div class="milestone-header" 
                 onclick="SynergyCard.toggleMilestone('${milestone.milestone_id}')">
                <button class="milestone-expand-btn">
                    <i class="fas fa-chevron-${isExpanded ? 'down' : 'right'}"></i>
                </button>
                <span class="milestone-number">M${milestone.milestone_number}</span>
                <input type="checkbox" 
                       ${milestone.completed ? 'checked' : ''}
                       onclick="event.stopPropagation(); SynergyCard.completeMilestone('${sessionId}', '${milestone.milestone_id}')" />
                <span class="milestone-name">${milestone.milestone_name}</span>
                <span class="milestone-progress">${progress}%</span>
                ${milestone.due_date ? `<span class="milestone-due">${milestone.due_date}</span>` : ''}
            </div>
            
            <!-- Milestone Body (collapsible) -->
            <div class="milestone-body ${isExpanded ? 'expanded' : 'collapsed'}">
                ${milestone.description ? `<div class="milestone-description">${milestone.description}</div>` : ''}
                
                <!-- Tasks -->
                <div class="milestone-tasks">
                    ${milestone.tasks.map((task, idx) => this.renderTask(task, milestone, sessionId)).join('')}
                </div>
                
                <!-- Milestone Footer -->
                ${this.renderMilestoneFooter(milestone)}
            </div>
        </div>
    `;
}

renderTask(task, milestone, sessionId) {
    const hasSubtasks = task.subtasks && task.subtasks.length > 0;
    const isExpanded = hasSubtasks && this.isTaskExpanded(task.task_id);
    
    return `
        <div class="task-item ${task.completed ? 'completed' : ''} ${task.blocked ? 'blocked' : ''}"
             data-task-id="${task.task_id}">
            
            ${hasSubtasks ? `
                <button class="task-expand-btn" 
                        onclick="SynergyCard.toggleTask('${task.task_id}')">
                    <i class="fas fa-chevron-${isExpanded ? 'down' : 'right'}"></i>
                </button>
            ` : ''}
            
            <span class="task-number">T${milestone.milestone_number}.${task.task_order}</span>
            <input type="checkbox" 
                   ${task.completed ? 'checked' : ''}
                   ${task.blocked ? 'disabled' : ''}
                   onclick="SynergyCard.completeTask('${sessionId}', '${task.task_id}')" />
            <span class="task-name">${task.task}</span>
            
            ${task.blocked ? `
                <span class="blocker-badge">
                    🚧 BLOCKED: ${task.blocker_reason} 
                    (${this.calculateDaysSince(task.blocked_since)} days)
                </span>
            ` : ''}
            
            <!-- Subtasks -->
            ${hasSubtasks ? `
                <div class="task-subtasks ${isExpanded ? 'expanded' : 'collapsed'}">
                    ${task.subtasks.map((subtask, subIdx) => 
                        this.renderSubtask(subtask, task, milestone, sessionId)
                    ).join('')}
                </div>
            ` : ''}
        </div>
    `;
}

renderSubtask(subtask, task, milestone, sessionId) {
    return `
        <div class="subtask-item ${subtask.completed ? 'completed' : ''}"
             data-subtask-id="${subtask.subtask_id}">
            <span class="subtask-number">S${milestone.milestone_number}.${task.task_order}.${subtask.subtask_order}</span>
            <input type="checkbox" 
                   ${subtask.completed ? 'checked' : ''}
                   onclick="SynergyCard.completeSubtask('${sessionId}', '${subtask.subtask_id}')" />
            <span class="subtask-name">${subtask.task}</span>
        </div>
    `;
}
```

---

## 🎨 STEP 4: CSS STYLES

**File to Update:** `UI/business-ai-platform-v2.html` (add to `<style>` section)

```css
/* ==================== MILESTONE STYLES ==================== */

.milestones-section {
    margin-bottom: 24px;
}

.milestones-container {
    display: flex;
    flex-direction: column;
    gap: 12px;
}

.milestone-item {
    border: 1px solid var(--border-default);
    border-radius: 8px;
    overflow: hidden;
    transition: all 0.3s ease;
}

.milestone-item.completed {
    opacity: 0.7;
    background: var(--bg-quaternary);
}

/* Milestone Header */
.milestone-header {
    display: flex;
    align-items: center;
    gap: 12px;
    padding: 12px;
    background: linear-gradient(135deg, #3b82f6 0%, #2563eb 100%);
    color: white;
    cursor: pointer;
    user-select: none;
}

.milestone-header:hover {
    background: linear-gradient(135deg, #2563eb 0%, #1d4ed8 100%);
}

.milestone-item.completed .milestone-header {
    background: linear-gradient(135deg, #22c55e 0%, #16a34a 100%);
}

.milestone-expand-btn {
    background: none;
    border: none;
    color: white;
    cursor: pointer;
    padding: 4px;
    width: 24px;
    height: 24px;
    display: flex;
    align-items: center;
    justify-content: center;
    transition: transform 0.2s;
}

.milestone-expand-btn i {
    transition: transform 0.2s;
}

.milestone-number {
    display: inline-flex;
    align-items: center;
    justify-content: center;
    min-width: 36px;
    height: 28px;
    background: rgba(255, 255, 255, 0.2);
    border-radius: 6px;
    font-weight: 700;
    font-size: 12px;
}

.milestone-name {
    flex: 1;
    font-weight: 600;
    font-size: 14px;
}

.milestone-progress {
    background: rgba(255, 255, 255, 0.2);
    padding: 4px 12px;
    border-radius: 12px;
    font-size: 12px;
    font-weight: 600;
}

.milestone-due {
    background: rgba(255, 255, 255, 0.2);
    padding: 4px 10px;
    border-radius: 12px;
    font-size: 11px;
    display: flex;
    align-items: center;
    gap: 4px;
}

/* Milestone Body */
.milestone-body {
    padding: 0;
    max-height: 0;
    overflow: hidden;
    transition: max-height 0.3s ease, padding 0.3s ease;
}

.milestone-body.expanded {
    max-height: 2000px;
    padding: 16px;
}

.milestone-description {
    padding: 12px;
    background: var(--bg-quaternary);
    border-radius: 6px;
    margin-bottom: 12px;
    font-size: 13px;
    line-height: 1.6;
    color: var(--text-secondary);
}

/* Tasks */
.milestone-tasks {
    display: flex;
    flex-direction: column;
    gap: 8px;
}

.task-item {
    display: flex;
    align-items: flex-start;
    gap: 8px;
    padding: 10px;
    background: var(--bg-secondary);
    border-radius: 6px;
    border-left: 3px solid var(--accent-primary);
    transition: all 0.2s;
}

.task-item:hover {
    background: var(--bg-tertiary);
}

.task-item.completed {
    opacity: 0.6;
    border-left-color: #22c55e;
}

.task-item.blocked {
    border-left-color: #dc2626;
    background: #fef2f2;
}

.task-expand-btn {
    background: none;
    border: none;
    color: var(--text-primary);
    cursor: pointer;
    padding: 4px;
    width: 20px;
    height: 20px;
    display: flex;
    align-items: center;
    justify-content: center;
}

.task-number {
    display: inline-flex;
    align-items: center;
    justify-content: center;
    min-width: 48px;
    padding: 4px 8px;
    background: var(--accent-primary);
    color: white;
    border-radius: 4px;
    font-weight: 600;
    font-size: 11px;
    font-family: 'Courier New', monospace;
}

.task-name {
    flex: 1;
    font-size: 13px;
    line-height: 1.4;
}

.task-item.completed .task-name {
    text-decoration: line-through;
}

.blocker-badge {
    background: #dc2626;
    color: white;
    padding: 4px 12px;
    border-radius: 12px;
    font-size: 10px;
    font-weight: 600;
    white-space: nowrap;
}

/* Subtasks */
.task-subtasks {
    margin-left: 56px;
    margin-top: 8px;
    max-height: 0;
    overflow: hidden;
    transition: max-height 0.3s ease;
}

.task-subtasks.expanded {
    max-height: 500px;
}

.subtask-item {
    display: flex;
    align-items: center;
    gap: 8px;
    padding: 6px 12px;
    background: var(--bg-primary);
    border-radius: 4px;
    margin-bottom: 4px;
    border-left: 2px solid var(--border-default);
}

.subtask-item.completed {
    opacity: 0.6;
}

.subtask-number {
    display: inline-flex;
    align-items: center;
    justify-content: center;
    min-width: 60px;
    padding: 2px 8px;
    background: #f3f4f6;
    border: 1px solid #e5e7eb;
    border-radius: 3px;
    font-family: 'Courier New', monospace;
    font-size: 9px;
    color: #6b7280;
    font-weight: 600;
}

.subtask-name {
    flex: 1;
    font-size: 12px;
}

.subtask-item.completed .subtask-name {
    text-decoration: line-through;
}

/* Milestone Footer */
.milestone-footer {
    margin-top: 16px;
    padding-top: 12px;
    border-top: 1px solid var(--border-muted);
    display: flex;
    justify-content: space-between;
    align-items: center;
    font-size: 12px;
    color: var(--text-muted);
}

.milestone-footer-stats {
    display: flex;
    gap: 16px;
}

.milestone-footer-actions {
    display: flex;
    gap: 8px;
}

.milestone-comment-btn {
    background: var(--bg-quaternary);
    border: 1px solid var(--border-default);
    padding: 4px 12px;
    border-radius: 4px;
    cursor: pointer;
    font-size: 12px;
    display: flex;
    align-items: center;
    gap: 6px;
    transition: all 0.2s;
}

.milestone-comment-btn:hover {
    background: var(--bg-tertiary);
}
```

---

## 🔧 STEP 5: JAVASCRIPT INTERACTIONS

**File to Update:** `UI/external/modules/synergy-card-renderer.js`

Add interaction methods:

```javascript
// Track expansion state
expandedMilestones: new Set(),
expandedTasks: new Set(),

toggleMilestone(milestoneId) {
    const milestone = document.querySelector(`[data-milestone-id="${milestoneId}"]`);
    const body = milestone.querySelector('.milestone-body');
    const btn = milestone.querySelector('.milestone-expand-btn i');
    
    if (this.expandedMilestones.has(milestoneId)) {
        this.expandedMilestones.delete(milestoneId);
        body.classList.remove('expanded');
        body.classList.add('collapsed');
        btn.classList.replace('fa-chevron-down', 'fa-chevron-right');
    } else {
        this.expandedMilestones.add(milestoneId);
        body.classList.remove('collapsed');
        body.classList.add('expanded');
        btn.classList.replace('fa-chevron-right', 'fa-chevron-down');
    }
},

async completeMilestone(sessionId, milestoneId) {
    try {
        const response = await fetch(`${API_BASE_URL}/api/synergy/milestone/${milestoneId}/complete`, {
            method: 'PATCH',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({completed: true})
        });
        
        const result = await response.json();
        if (result.success) {
            showNotification(`Milestone completed (${result.tasks_completed} tasks)`, 'success');
            // Refresh card
            await this.refreshCard(sessionId);
        }
    } catch (error) {
        showNotification('Error completing milestone', 'error');
    }
},

async completeTask(sessionId, taskId) {
    try {
        const response = await fetch(`${API_BASE_URL}/api/synergy/task/${taskId}/complete`, {
            method: 'PATCH',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({completed: true})
        });
        
        const result = await response.json();
        if (result.success) {
            if (result.milestone_completed) {
                showNotification('Task completed - Milestone auto-completed!', 'success');
            } else {
                showNotification('Task completed', 'success');
            }
            await this.refreshCard(sessionId);
        }
    } catch (error) {
        showNotification('Error completing task', 'error');
    }
},

async completeSubtask(sessionId, subtaskId) {
    try {
        const response = await fetch(`${API_BASE_URL}/api/synergy/subtask/${subtaskId}/complete`, {
            method: 'PATCH',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({completed: true})
        });
        
        const result = await response.json();
        if (result.success) {
            let msg = 'Subtask completed';
            if (result.task_auto_completed) msg += ' - Task auto-completed';
            if (result.milestone_auto_completed) msg += ' - Milestone auto-completed!';
            showNotification(msg, 'success');
            await this.refreshCard(sessionId);
        }
    } catch (error) {
        showNotification('Error completing subtask', 'error');
    }
}
```

---

## ✅ IMPLEMENTATION CHECKLIST

- [x] **Step 1:** Create migration SQL (`synergy_milestone_migration.sql`)
- [ ] **Step 2:** Update `synergy_routes.py` with 11 new endpoints
- [ ] **Step 3:** Update `synergy-card-renderer.js` with milestone rendering
- [ ] **Step 4:** Add milestone CSS styles to HTML
- [ ] **Step 5:** Add JavaScript interactions to renderer module
- [ ] **Step 6:** Update tool schemas (`tools/schemas/synergy_tools.json`)
- [ ] **Step 7:** Test with sample Synergy session
- [ ] **Step 8:** Run migration on existing data

---

## 🚀 DEPLOYMENT PLAN

1. **Run migration SQL** on database
2. **Deploy backend** with new API endpoints
3. **Deploy frontend** with milestone rendering
4. **Migrate existing sessions** (or mark as legacy)
5. **Monitor** for issues
6. **Deprecate** old next_steps/checklist endpoints after 3 months

---

**Estimated Implementation Time:** 6-8 hours
**Priority:** High (architectural improvement)
**Risk Level:** Medium (requires careful testing)

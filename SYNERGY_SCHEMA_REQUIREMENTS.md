# Synergy Schema Requirements - December 1, 2025

## 📋 Current vs. Required Schema Comparison

---

## 🎯 MILESTONES

### Current Schema ✅
```sql
CREATE TABLE synergy_sessions.milestones (
    milestone_id TEXT PRIMARY KEY,
    session_id TEXT NOT NULL,
    milestone_number INTEGER NOT NULL,
    milestone_name TEXT NOT NULL,          -- ✅ TITLE EXISTS
    description TEXT,                      -- ✅ DESCRIPTION EXISTS
    completed BOOLEAN DEFAULT FALSE,
    completed_at TEXT,
    due_date TEXT,                         -- ✅ DUE DATE EXISTS
    priority TEXT DEFAULT 'medium'         -- ✅ PRIORITY EXISTS
        CHECK (priority IN ('low', 'medium', 'high', 'critical')),
    estimated_hours DECIMAL(5,2),
    actual_hours DECIMAL(5,2),
    depends_on TEXT,
    created_at TEXT,
    updated_at TEXT
);
```

### Status: ✅ **ALL FIELDS EXIST - NO CHANGES NEEDED**

**Fields You Want:**
- ✅ Title → `milestone_name` (exists)
- ✅ Description → `description` (exists)
- ✅ Priority Level → `priority` with enum validation (exists)
- ✅ Due Date → `due_date` (exists)

---

## 📝 TASKS

### Current Schema ❌
```sql
CREATE TABLE synergy_sessions.tasks (
    task_id TEXT PRIMARY KEY,
    milestone_id TEXT NOT NULL,
    task TEXT NOT NULL,                    -- ❌ SINGLE FIELD (title + description)
    task_order INTEGER,
    completed BOOLEAN DEFAULT FALSE,
    completed_at TEXT,
    assigned_to TEXT,
    blocked BOOLEAN DEFAULT FALSE,
    blocker_reason TEXT,
    blocker_type TEXT,
    blocked_since TEXT,
    blocked_by_user TEXT,
    expected_resolution TEXT,
    created_at TEXT,
    updated_at TEXT
    -- ❌ MISSING: priority field
);
```

### Status: ❌ **MISSING PRIORITY FIELD**

**Fields You Want:**
- ✅ Title/Description → `task` field (exists, single field is OK per your note "the title is ok or the field is ok")
- ❌ Priority Level → **MISSING** (need to add)

### Required Change:
```sql
-- Add priority column to tasks table
ALTER TABLE synergy_sessions.tasks 
ADD COLUMN priority TEXT DEFAULT 'medium' 
CHECK (priority IN ('low', 'medium', 'high', 'critical'));

-- Create index for filtering by priority
CREATE INDEX idx_tasks_priority ON synergy_sessions.tasks(priority);
```

---

## 📌 SUBTASKS

### Current Schema ❌
```sql
CREATE TABLE synergy_sessions.subtasks (
    subtask_id TEXT PRIMARY KEY,
    task_id TEXT NOT NULL,
    task TEXT NOT NULL,                    -- ✅ TEXT FIELD (title/description)
    subtask_order INTEGER,
    completed BOOLEAN DEFAULT FALSE,
    completed_at TEXT,
    created_at TEXT,
    updated_at TEXT
    -- ❌ MISSING: priority field
);
```

### Status: ❌ **MISSING PRIORITY FIELD**

**Fields You Want:**
- ✅ Text field (title/description) → `task` field (exists)
- ❌ Priority Level → **MISSING** (need to add)

### Required Change:
```sql
-- Add priority column to subtasks table
ALTER TABLE synergy_sessions.subtasks 
ADD COLUMN priority TEXT DEFAULT 'medium' 
CHECK (priority IN ('low', 'medium', 'high', 'critical'));

-- Create index for filtering by priority
CREATE INDEX idx_subtasks_priority ON synergy_sessions.subtasks(priority);
```

---

## 🎨 MARKDOWN RENDERING REQUIREMENT

### Current State: ❌ **NOT IMPLEMENTED**

**Location:** `UI/modules_internal/synergy/synergy-sidebar-renderer-v2-FLAT.js` (line 270)

**Current Rendering (Plain Text):**
```javascript
<div class="synergy-flat-description" contenteditable="false" data-field="description">
    ${this.escapeHtml(description)}  // ❌ Only escapes HTML, no markdown parsing
</div>
```

**Required:** Render markdown syntax (bold, italic, links, lists, code blocks, etc.)

### Solution Options:

#### Option 1: Use marked.js (Recommended)
```javascript
// Add marked.js library
<script src="https://cdn.jsdelivr.net/npm/marked/marked.min.js"></script>

// Update rendering
<div class="synergy-flat-description" contenteditable="false" data-field="description">
    ${this.renderMarkdown(description)}  // ✅ Parse markdown
</div>

// Add method
renderMarkdown(text) {
    if (!text) return '';
    if (typeof marked !== 'undefined') {
        return marked.parse(text);
    }
    return this.escapeHtml(text);  // Fallback
}
```

#### Option 2: Use DOMPurify + marked.js (More Secure)
```javascript
// Add both libraries
<script src="https://cdn.jsdelivr.net/npm/marked/marked.min.js"></script>
<script src="https://cdn.jsdelivr.net/npm/dompurify/dist/purify.min.js"></script>

// Secure markdown rendering
renderMarkdown(text) {
    if (!text) return '';
    if (typeof marked !== 'undefined' && typeof DOMPurify !== 'undefined') {
        const rawHtml = marked.parse(text);
        return DOMPurify.sanitize(rawHtml);  // ✅ XSS protection
    }
    return this.escapeHtml(text);
}
```

#### Option 3: Simple Regex-Based Markdown (No Dependencies)
```javascript
renderMarkdown(text) {
    if (!text) return '';
    
    // Escape HTML first
    let html = this.escapeHtml(text);
    
    // Convert markdown syntax
    html = html.replace(/\*\*(.+?)\*\*/g, '<strong>$1</strong>');  // **bold**
    html = html.replace(/\*(.+?)\*/g, '<em>$1</em>');              // *italic*
    html = html.replace(/`(.+?)`/g, '<code>$1</code>');            // `code`
    html = html.replace(/\[(.+?)\]\((.+?)\)/g, '<a href="$2" target="_blank">$1</a>');  // [link](url)
    html = html.replace(/\n/g, '<br>');                            // Line breaks
    
    return html;
}
```

---

## 📊 Summary of Required Changes

### 1. Database Schema Changes (SQL)
```sql
-- File: migrations/add_task_subtask_priority.sql

-- Add priority to tasks
ALTER TABLE synergy_sessions.tasks 
ADD COLUMN priority TEXT DEFAULT 'medium' 
CHECK (priority IN ('low', 'medium', 'high', 'critical'));

-- Add priority to subtasks
ALTER TABLE synergy_sessions.subtasks 
ADD COLUMN priority TEXT DEFAULT 'medium' 
CHECK (priority IN ('low', 'medium', 'high', 'critical'));

-- Create indexes
CREATE INDEX idx_tasks_priority ON synergy_sessions.tasks(priority);
CREATE INDEX idx_subtasks_priority ON synergy_sessions.subtasks(priority);

-- Update existing rows to have default priority
UPDATE synergy_sessions.tasks SET priority = 'medium' WHERE priority IS NULL;
UPDATE synergy_sessions.subtasks SET priority = 'medium' WHERE priority IS NULL;
```

### 2. Backend API Changes (Python)

#### File: `AI_infrastructure/routes/synergy_routes.py`

**Task Creation - Add Priority:**
```python
# Line ~3015 - Update task creation
cursor.execute('''
    INSERT INTO synergy_sessions.tasks (
        task_id, milestone_id, task, completed, task_order, 
        priority,  # ← ADD THIS
        created_at
    ) VALUES (%s, %s, %s, %s, %s, %s, %s)
''', (
    task_id, milestone_id, task_text, False, task_order, 
    task_item.get('priority', 'medium') if isinstance(task_item, dict) else 'medium',  # ← ADD THIS
    datetime.now().isoformat()
))
```

**Subtask Creation - Add Priority:**
```python
# Line ~3025 - Update subtask creation
for subtask_order, subtask_item in enumerate(subtasks, start=1):
    subtask_id = f"sub_{datetime.now().strftime('%Y%m%d%H%M%S')}_{task_order}_{subtask_order}"
    
    # Handle both string and object formats
    if isinstance(subtask_item, str):
        subtask_text = subtask_item
        subtask_priority = 'medium'
    else:
        subtask_text = subtask_item.get('task', subtask_item.get('subtask', ''))
        subtask_priority = subtask_item.get('priority', 'medium')
    
    cursor.execute('''
        INSERT INTO synergy_sessions.subtasks (
            subtask_id, task_id, task, completed, subtask_order, 
            priority,  # ← ADD THIS
            created_at
        ) VALUES (%s, %s, %s, %s, %s, %s, %s)
    ''', (
        subtask_id, task_id, subtask_text, False, subtask_order, 
        subtask_priority,  # ← ADD THIS
        datetime.now().isoformat()
    ))
```

### 3. Tool Schema Changes (JSON)

#### File: `tools/schemas/synergy_tools.json`

**Update Task Schema:**
```json
{
  "type": "object",
  "properties": {
    "task": {
      "type": "string",
      "description": "Task description"
    },
    "priority": {
      "type": "string",
      "enum": ["low", "medium", "high", "critical"],
      "description": "Task priority level (default: medium)",
      "default": "medium"
    },
    "subtasks": {
      "type": "array",
      "items": {
        "oneOf": [
          {
            "type": "string",
            "description": "Simple subtask text (default priority: medium)"
          },
          {
            "type": "object",
            "properties": {
              "task": {
                "type": "string",
                "description": "Subtask description"
              },
              "priority": {
                "type": "string",
                "enum": ["low", "medium", "high", "critical"],
                "description": "Subtask priority level (default: medium)",
                "default": "medium"
              }
            },
            "required": ["task"]
          }
        ]
      }
    }
  },
  "required": ["task"]
}
```

**Example Usage:**
```json
{
  "initial_milestones": [
    {
      "milestone_name": "Phase 1: Database Setup",
      "description": "Create and configure database",
      "priority": "critical",
      "due_date": "2025-12-15",
      "tasks": [
        {
          "task": "Design database schema",
          "priority": "critical",
          "subtasks": [
            {
              "task": "Define customer fields",
              "priority": "critical"
            },
            {
              "task": "Set up validation rules",
              "priority": "high"
            },
            "Create test data"  // ← String format uses default priority
          ]
        },
        "Import existing data"  // ← String format uses default priority
      ]
    }
  ]
}
```

### 4. Frontend Rendering Changes (JavaScript)

#### File: `UI/modules_internal/synergy/synergy-milestone-renderer.js`

**Task Rendering - Add Priority Badge:**
```javascript
// Line ~200 - Update task rendering
renderTask(task, milestone, sessionId) {
    const hasSubtasks = task.subtasks && task.subtasks.length > 0;
    const isExpanded = hasSubtasks && this.isTaskExpanded(task.task_id);
    const expandIcon = isExpanded ? 'fa-chevron-down' : 'fa-chevron-right';
    
    // ✅ ADD: Priority badge
    const priorityColor = this.getPriorityColor(task.priority || 'medium');
    const priorityBadge = `<span class="priority-badge" style="background-color: ${priorityColor};" title="Priority: ${task.priority || 'medium'}">${(task.priority || 'medium').toUpperCase()}</span>`;
    
    return `
        <div class="task-item ${task.completed ? 'completed' : ''} ${task.blocked ? 'blocked' : ''}"
             data-task-id="${task.task_id}">
            
            ${hasSubtasks ? `
                <button class="task-expand-btn" 
                        onclick="SynergyMilestoneInteractions.toggleTask('${task.task_id}')">
                    <i class="fas ${expandIcon}"></i>
                </button>
            ` : '<span style="width: 20px;"></span>'}
            
            <span class="task-number">T${milestone.milestone_number}.${task.task_order}</span>
            
            ${priorityBadge}  <!-- ✅ ADD PRIORITY BADGE -->
            
            <input type="checkbox" 
                   ${task.completed ? 'checked' : ''}
                   ${task.blocked ? 'disabled' : ''}
                   onclick="SynergyMilestoneInteractions.completeTask('${sessionId}', '${task.task_id}')" />
            
            <span class="task-name ${task.completed ? 'task-completed' : ''}">
                ${this.escapeHtml(task.task)}
            </span>
            
            ${task.blocked ? `
                <span class="blocker-badge" title="${this.escapeHtml(task.blocker_reason)}">
                    <i class="fas fa-exclamation-triangle"></i> BLOCKED
                </span>
            ` : ''}
            
            ${hasSubtasks ? `
                <div class="task-subtasks ${isExpanded ? 'expanded' : 'collapsed'}">
                    ${task.subtasks.map(subtask =>
                        this.renderSubtask(subtask, task, milestone, sessionId)
                    ).join('')}
                </div>
            ` : ''}
        </div>
    `;
}

// ✅ ADD: Priority color helper
getPriorityColor(priority) {
    const colors = {
        'critical': '#dc2626',  // Red
        'high': '#ef4444',      // Light red
        'medium': '#fbbf24',    // Amber
        'low': '#22c55e'        // Green
    };
    return colors[priority] || colors['medium'];
}
```

**Subtask Rendering - Add Priority Badge:**
```javascript
// Line ~240 - Update subtask rendering
renderSubtask(subtask, task, milestone, sessionId) {
    // ✅ ADD: Priority badge
    const priorityColor = this.getPriorityColor(subtask.priority || 'medium');
    const priorityBadge = `<span class="priority-badge priority-badge-small" style="background-color: ${priorityColor};" title="Priority: ${subtask.priority || 'medium'}">${(subtask.priority || 'medium')[0].toUpperCase()}</span>`;
    
    return `
        <div class="subtask-item ${subtask.completed ? 'completed' : ''}"
             data-subtask-id="${subtask.subtask_id}">
            
            <span class="subtask-number">S${milestone.milestone_number}.${task.task_order}.${subtask.subtask_order}</span>
            
            ${priorityBadge}  <!-- ✅ ADD PRIORITY BADGE -->
            
            <input type="checkbox" 
                   ${subtask.completed ? 'checked' : ''}
                   onclick="SynergyMilestoneInteractions.completeSubtask('${sessionId}', '${subtask.subtask_id}')" />
            
            <span class="subtask-name ${subtask.completed ? 'subtask-completed' : ''}">
                ${this.escapeHtml(subtask.task)}
            </span>
        </div>
    `;
}
```

#### File: `UI/modules_internal/synergy/synergy-sidebar-renderer-v2-FLAT.js`

**Markdown Rendering for Description:**
```javascript
// Line ~260 - Update description rendering
renderDescription(description) {
    const hasDescription = description && description.trim().length > 0;
    
    return `
        <div class="synergy-flat-section" data-section="description">
            <div class="synergy-flat-section-header">
                <b>Description</b>
                <div class="synergy-flat-header-right">
                    <button class="synergy-flat-action-btn synergy-edit-description-btn" title="Edit Description">
                        <i class="fas fa-pen"></i>
                    </button>
                </div>
            </div>
            <div class="synergy-flat-description-container" data-editing="false">
                ${hasDescription ? `
                    <div class="synergy-flat-description" contenteditable="false" data-field="description">
                        ${this.renderMarkdown(description)}  <!-- ✅ RENDER MARKDOWN -->
                    </div>
                ` : `
                    <div class="synergy-flat-description synergy-flat-empty-editable" contenteditable="false" data-field="description" data-placeholder="Click edit to add a description">
                        <i class="fas fa-align-left"></i>
                        <div>No description provided</div>
                    </div>
                `}
                <div class="synergy-flat-edit-actions" style="display: none;">
                    <button class="synergy-flat-action-btn synergy-save-description-btn">Save</button>
                    <button class="synergy-flat-action-btn synergy-cancel-description-btn">Cancel</button>
                </div>
            </div>
        </div>
    `;
}

// ✅ ADD: Markdown rendering method
renderMarkdown(text) {
    if (!text) return '';
    
    // Use marked.js if available
    if (typeof marked !== 'undefined') {
        // Secure rendering with DOMPurify if available
        if (typeof DOMPurify !== 'undefined') {
            const rawHtml = marked.parse(text);
            return DOMPurify.sanitize(rawHtml);
        }
        return marked.parse(text);
    }
    
    // Fallback: Simple markdown parsing
    let html = this.escapeHtml(text);
    
    // Bold: **text**
    html = html.replace(/\*\*(.+?)\*\*/g, '<strong>$1</strong>');
    
    // Italic: *text* or _text_
    html = html.replace(/\*(.+?)\*/g, '<em>$1</em>');
    html = html.replace(/_(.+?)_/g, '<em>$1</em>');
    
    // Code: `code`
    html = html.replace(/`(.+?)`/g, '<code>$1</code>');
    
    // Links: [text](url)
    html = html.replace(/\[(.+?)\]\((.+?)\)/g, '<a href="$2" target="_blank">$1</a>');
    
    // Line breaks
    html = html.replace(/\n/g, '<br>');
    
    // Headings: ## Heading
    html = html.replace(/^## (.+?)$/gm, '<h2>$1</h2>');
    html = html.replace(/^### (.+?)$/gm, '<h3>$1</h3>');
    
    // Bullet lists: - item
    html = html.replace(/^- (.+?)$/gm, '<li>$1</li>');
    html = html.replace(/(<li>.*<\/li>)/s, '<ul>$1</ul>');
    
    return html;
}
```

### 5. CSS Styles (Optional - For Priority Badges)

#### File: `UI/modules_internal/synergy/synergy-milestone-styles.css`

```css
/* Priority badges */
.priority-badge {
    display: inline-block;
    padding: 2px 6px;
    border-radius: 3px;
    font-size: 9px;
    font-weight: 600;
    color: white;
    text-transform: uppercase;
    letter-spacing: 0.5px;
    margin-left: 6px;
    margin-right: 6px;
}

.priority-badge-small {
    font-size: 8px;
    padding: 1px 4px;
}

/* Markdown content styles */
.synergy-flat-description code {
    background-color: #f3f4f6;
    padding: 2px 4px;
    border-radius: 3px;
    font-family: 'Courier New', monospace;
    font-size: 0.9em;
}

.synergy-flat-description strong {
    font-weight: 600;
}

.synergy-flat-description em {
    font-style: italic;
}

.synergy-flat-description a {
    color: #3b82f6;
    text-decoration: underline;
}

.synergy-flat-description a:hover {
    color: #2563eb;
}

.synergy-flat-description ul {
    margin: 8px 0;
    padding-left: 20px;
}

.synergy-flat-description li {
    margin: 4px 0;
}

.synergy-flat-description h2 {
    font-size: 1.2em;
    font-weight: 600;
    margin: 12px 0 6px 0;
}

.synergy-flat-description h3 {
    font-size: 1.1em;
    font-weight: 600;
    margin: 10px 0 4px 0;
}
```

---

## 🔧 Implementation Checklist

### Phase 1: Database Schema (5 minutes)
- [ ] Create migration file: `migrations/add_task_subtask_priority.sql`
- [ ] Run migration on Supabase
- [ ] Verify columns added: `SELECT * FROM synergy_sessions.tasks LIMIT 1`
- [ ] Verify indexes created: `\d synergy_sessions.tasks`

### Phase 2: Backend API (15 minutes)
- [ ] Update `synergy_routes.py` - task creation (line ~3015)
- [ ] Update `synergy_routes.py` - subtask creation (line ~3025)
- [ ] Update `synergy_routes.py` - task update endpoint
- [ ] Update `synergy_routes.py` - subtask update endpoint
- [ ] Test with curl/Postman

### Phase 3: Tool Schema (10 minutes)
- [ ] Update `synergy_tools.json` - task parameters
- [ ] Update `synergy_tools.json` - subtask parameters
- [ ] Add examples showing priority usage
- [ ] Reload tools: `BISTART`

### Phase 4: Frontend Rendering (20 minutes)
- [ ] Update `synergy-milestone-renderer.js` - add `getPriorityColor()`
- [ ] Update `synergy-milestone-renderer.js` - task rendering
- [ ] Update `synergy-milestone-renderer.js` - subtask rendering
- [ ] Update `synergy-sidebar-renderer-v2-FLAT.js` - add `renderMarkdown()`
- [ ] Update `synergy-sidebar-renderer-v2-FLAT.js` - description rendering
- [ ] Add marked.js library to HTML head
- [ ] Add DOMPurify library to HTML head

### Phase 5: CSS Styling (5 minutes)
- [ ] Add priority badge styles
- [ ] Add markdown content styles
- [ ] Test visual appearance

### Phase 6: Testing (15 minutes)
- [ ] Create test session with priorities
- [ ] Verify priority badges appear
- [ ] Test markdown rendering (bold, italic, links, lists)
- [ ] Test priority filtering (if implemented)
- [ ] Verify existing sessions still work

---

## 📈 Total Estimated Time: **70 minutes**

---

## 🎯 Priority Levels Enum

**Consistent across all entities (milestone, task, subtask):**

```
'low'      → 🟢 Green (#22c55e)
'medium'   → 🟡 Amber (#fbbf24)
'high'     → 🟠 Light Red (#ef4444)
'critical' → 🔴 Red (#dc2626)
```

---

## ✅ Final Schema Summary

| Entity | Title Field | Description Field | Priority Field | Due Date Field |
|--------|------------|-------------------|----------------|----------------|
| **Milestone** | ✅ `milestone_name` | ✅ `description` | ✅ `priority` | ✅ `due_date` |
| **Task** | ✅ `task` | N/A (single field) | ❌ **ADD** | N/A |
| **Subtask** | ✅ `task` | N/A (single field) | ❌ **ADD** | N/A |

**Markdown Rendering:** ❌ **ADD** to `synergy-flat-description` container

---

**Document Status:** ✅ Complete Requirements Specification
**Next Step:** Review and approve, then proceed with implementation

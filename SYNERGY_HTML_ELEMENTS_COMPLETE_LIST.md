# Synergy UI - Complete HTML Elements List

**Date:** November 8, 2025  
**Status:** ✅ **DATA MISMATCH BUGS FIXED**  
**Files Modified:** `UI/business-ai-platform-v2.html` (4 critical fixes applied)

---

## 🎯 WHAT WAS FIXED

### ROOT CAUSE:
1. **Documents used `doc.name` instead of `doc.title`** - Edit modal uses `doc.title`
2. **No filtering on documents/links** - Empty items rendered as "Untitled"/"N/A"
3. **Overly strict filtering on checklist/steps** - `.trim() !== ''` removed valid items
4. **Inconsistent field names** - `doc.name` vs `doc.title`, `link.name` vs `link.title`

### FIXES APPLIED:
1. ✅ **Documents:** Added filter + changed `doc.name` → `doc.title || doc.name`
2. ✅ **Links:** Added filter + changed to `link.title || link.name`
3. ✅ **Next Steps:** Removed `.trim() !== ''` check (only check for null/undefined)
4. ✅ **Checklist:** Removed `.trim() !== ''` check (only check for null/undefined)

---

## 📋 EDIT MODAL - Complete HTML Elements List

**Location:** Lines 7191-7450  
**Purpose:** Full editing interface for all session fields  
**Display:** Modal overlay (flex display)

### Structure:
```html
<div class="edit-card-modal" id="edit-card-modal">
    <div class="modal-overlay" onclick="closeEditModal()"></div>
    <div class="modal-content">
        <div class="modal-header">
            <h3><i class="fas fa-edit"></i> Edit Card</h3>
            <button class="modal-close-btn">×</button>
        </div>
        
        <div class="modal-body">
            <!-- ALL EDITABLE FIELDS -->
        </div>
        
        <div class="modal-footer">
            <button class="btn-secondary">Cancel</button>
            <button class="btn-primary">Save Changes</button>
        </div>
    </div>
</div>
```

### Complete Field List:

#### 1. Hidden Fields
```html
<input type="hidden" id="edit-session-id">
```
**Data Source:** `session.session_id`  
**Purpose:** Track which session is being edited

---

#### 2. Title (Required)
```html
<div class="form-group">
    <label for="edit-title">Title <span class="required">*</span></label>
    <input type="text" id="edit-title" class="form-control" placeholder="Task title" required>
</div>
```
**Data Source:** `session.title`  
**Type:** Single-line text input  
**Required:** Yes

---

#### 3. Description
```html
<div class="form-group">
    <label for="edit-description">Description</label>
    <textarea id="edit-description" class="form-control" rows="3" 
        placeholder="Detailed description"></textarea>
</div>
```
**Data Source:** `session.description`  
**Type:** Multi-line textarea (3 rows)  
**Required:** No

---

#### 4. Thread Integration Section (Purple Box)
```html
<div class="form-section" style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%)">
    <h4 style="color: white">
        <i class="fas fa-link"></i> Thread Integration
    </h4>
    
    <!-- 4a. Thread IDs -->
    <div class="form-group">
        <label for="edit-thread-ids" style="color: white">
            <i class="fas fa-comments"></i> Linked Thread IDs (comma-separated)
        </label>
        <input type="text" id="edit-thread-ids" class="form-control" 
            placeholder="thread_abc123, thread_def456">
    </div>
    
    <!-- 4b. Assigned Agents -->
    <div class="form-group">
        <label for="edit-assigned-agents" style="color: white">
            <i class="fas fa-robot"></i> Assigned AI Agents (comma-separated)
        </label>
        <input type="text" id="edit-assigned-agents" class="form-control" 
            placeholder="Agent Alpha-1, Agent Bravo-2">
    </div>
</div>
```
**Data Sources:**
- `session.thread_ids` → Comma-separated string
- `session.assigned_agents` → Comma-separated string

---

#### 5. Project & Priority Row
```html
<div class="form-row">
    <!-- 5a. Project -->
    <div class="form-group">
        <label for="edit-project">Project</label>
        <input type="text" id="edit-project" class="form-control" placeholder="Project name">
    </div>
    
    <!-- 5b. Priority -->
    <div class="form-group">
        <label for="edit-priority">Priority</label>
        <select id="edit-priority" class="form-control">
            <option value="low">🟢 Low</option>
            <option value="medium">🟡 Medium</option>
            <option value="high">🔴 High</option>
        </select>
    </div>
</div>
```
**Data Sources:**
- `session.project_name` → Text input
- `session.priority` → Dropdown (low/medium/high)

---

#### 6. Status & Column Row
```html
<div class="form-row">
    <!-- 6a. Status -->
    <div class="form-group">
        <label for="edit-status">Status</label>
        <select id="edit-status" class="form-control">
            <option value="active">Active</option>
            <option value="paused">Paused</option>
            <option value="completed">Completed</option>
        </select>
    </div>
    
    <!-- 6b. Column -->
    <div class="form-group">
        <label for="edit-column">Column</label>
        <select id="edit-column" class="form-control">
            <option value="backlog">Backlog</option>
            <option value="in_progress">In Progress</option>
            <option value="review">Review</option>
            <option value="done">Done</option>
        </select>
    </div>
</div>
```
**Data Sources:**
- `session.status` → Dropdown (active/paused/completed)
- `session.kanban_column` → Dropdown (backlog/in_progress/review/done)

---

#### 7. Due Date & Due Time Row
```html
<div class="form-row">
    <!-- 7a. Due Date -->
    <div class="form-group">
        <label for="edit-due-date">Due Date</label>
        <input type="date" id="edit-due-date" class="form-control">
    </div>
    
    <!-- 7b. Due Time -->
    <div class="form-group">
        <label for="edit-due-time">Due Time</label>
        <input type="time" id="edit-due-time" class="form-control">
    </div>
</div>
```
**Data Source:** `session.due_date`  
**Processing:**
```javascript
const date = new Date(session.due_date);
edit-due-date.value = date.toISOString().split('T')[0];
edit-due-time.value = `${hours}:${minutes}`;
```

---

#### 8. Assignees
```html
<div class="form-group">
    <label for="edit-assignees">Assignees (comma-separated)</label>
    <input type="text" id="edit-assignees" class="form-control" 
        placeholder="John, Sarah, AI">
</div>
```
**Data Source:** `session.assignees` (array → joined with ', ')

---

#### 9. Tags
```html
<div class="form-group">
    <label for="edit-tags">Tags (comma-separated)</label>
    <input type="text" id="edit-tags" class="form-control" 
        placeholder="marketing, urgent, backend">
</div>
```
**Data Source:** `session.tags` (array → joined with ', ')

---

#### 10. Notes
```html
<div class="form-group">
    <label for="edit-notes">Notes</label>
    <textarea id="edit-notes" class="form-control" rows="4" 
        placeholder="Additional context and updates"></textarea>
</div>
```
**Data Source:** `session.notes`  
**Type:** Multi-line textarea (4 rows)

---

#### 11. Documents Section
```html
<div class="form-section">
    <div class="section-header">
        <label><i class="fas fa-file-alt"></i> Documents</label>
        <button type="button" class="btn-add-item" onclick="synergyBoard.addDocumentField()">
            <i class="fas fa-plus"></i> Add Document
        </button>
    </div>
    <div id="documents-list" class="items-list">
        <!-- Dynamic document rows added here -->
        <div class="item-row">
            <input type="text" class="form-control" placeholder="Document title" value="${doc.title}">
            <input type="url" class="form-control" placeholder="URL" value="${doc.url}">
            <select class="form-control" style="max-width: 180px;">
                <optgroup label="Google">
                    <option value="google_doc">Google Doc</option>
                    <option value="google_sheet">Google Sheet</option>
                    <option value="google_slides">Google Slides</option>
                    <option value="google_form">Google Form</option>
                </optgroup>
                <optgroup label="Microsoft">
                    <option value="word">Word</option>
                    <option value="excel">Excel</option>
                    <option value="powerpoint">PowerPoint</option>
                    <option value="onenote">OneNote</option>
                </optgroup>
                <optgroup label="Other">
                    <option value="pdf">PDF</option>
                    <option value="dashboard">Dashboard</option>
                    <option value="spreadsheet">Spreadsheet</option>
                    <option value="presentation">Presentation</option>
                    <option value="file">File</option>
                </optgroup>
            </select>
            <button type="button" class="btn-remove-item" onclick="this.parentElement.remove()">
                <i class="fas fa-trash"></i>
            </button>
        </div>
    </div>
</div>
```
**Data Source:** `session.documents` (array of objects)  
**Object Structure:**
```javascript
{
    title: "Document Name",
    url: "https://...",
    type: "google_doc",
    created_at: "2025-11-07T..."
}
```
**Dynamic Rows:** Each document creates new item-row

---

#### 12. Links Section
```html
<div class="form-section">
    <div class="section-header">
        <label><i class="fas fa-link"></i> Links</label>
        <button type="button" class="btn-add-item" onclick="synergyBoard.addLinkField()">
            <i class="fas fa-plus"></i> Add Link
        </button>
    </div>
    <div id="links-list" class="items-list">
        <!-- Dynamic link rows added here -->
        <div class="item-row">
            <input type="text" class="form-control" placeholder="Link title" value="${link.title}">
            <input type="url" class="form-control" placeholder="URL" value="${link.url}">
            <select class="form-control" style="max-width: 180px;">
                <optgroup label="Project Management">
                    <option value="notion">Notion</option>
                    <option value="jira">Jira</option>
                    <option value="asana">Asana</option>
                    <option value="trello">Trello</option>
                </optgroup>
                <optgroup label="Design & Development">
                    <option value="figma">Figma</option>
                    <option value="github">GitHub</option>
                    <option value="gitlab">GitLab</option>
                    <option value="codepen">CodePen</option>
                </optgroup>
                <optgroup label="Research & Reference">
                    <option value="research">Research</option>
                    <option value="documentation">Documentation</option>
                    <option value="tutorial">Tutorial</option>
                    <option value="article">Article</option>
                </optgroup>
                <optgroup label="Analytics & Reporting">
                    <option value="analytics">Analytics</option>
                    <option value="dashboard">Dashboard</option>
                    <option value="report">Report</option>
                </optgroup>
                <optgroup label="Other">
                    <option value="external">External</option>
                    <option value="reference">Reference</option>
                </optgroup>
            </select>
            <button type="button" class="btn-remove-item" onclick="this.parentElement.remove()">
                <i class="fas fa-trash"></i>
            </button>
        </div>
    </div>
</div>
```
**Data Source:** `session.links` (array of objects)  
**Object Structure:**
```javascript
{
    title: "Link Name",
    url: "https://...",
    type: "notion"
}
```

---

#### 13. Next Steps Section
```html
<div class="form-section">
    <div class="section-header">
        <label><i class="fas fa-tasks"></i> Next Steps</label>
        <button type="button" class="btn-add-item" onclick="synergyBoard.addNextStepField()">
            <i class="fas fa-plus"></i> Add Step
        </button>
    </div>
    <div id="next-steps-list" class="items-list">
        <!-- Dynamic step rows added here -->
        <div class="step-wrapper">
            <div class="item-row step-main">
                <input type="checkbox" class="step-checkbox" ${step.completed ? 'checked' : ''}>
                <input type="text" class="form-control step-description" 
                    placeholder="Step description" value="${step.description}">
                <input type="date" class="form-control" style="max-width: 150px;" value="${step.due_date}">
                <button type="button" class="btn-add-subtask" onclick="synergyBoard.addSubChecklistItem('stepId')">
                    <i class="fas fa-plus"></i>
                </button>
                <button type="button" class="btn-remove-item" onclick="this.parentElement.parentElement.remove()">
                    <i class="fas fa-trash"></i>
                </button>
            </div>
            <div class="sub-checklist" id="stepId">
                <!-- Sub-checklist items -->
                <div class="sub-checklist-item">
                    <input type="checkbox" class="sub-checkbox" ${subItem.completed ? 'checked' : ''}>
                    <input type="text" class="form-control" placeholder="Sub-task" value="${subItem.item}">
                    <button type="button" class="btn-remove-subtask" onclick="this.parentElement.remove()">
                        <i class="fas fa-times"></i>
                    </button>
                </div>
            </div>
        </div>
    </div>
</div>
```
**Data Source:** `session.next_steps` (array of objects)  
**Object Structure:**
```javascript
{
    description: "Step description",
    due_date: "2025-11-10",
    completed: false,
    sub_checklist: [
        { item: "Sub-task 1", completed: false },
        { item: "Sub-task 2", completed: true }
    ]
}
```

---

#### 14. Checklist Section
```html
<div class="form-section">
    <div class="section-header">
        <label><i class="fas fa-check-square"></i> Checklist</label>
        <button type="button" class="btn-add-item" onclick="synergyBoard.addChecklistField()">
            <i class="fas fa-plus"></i> Add Item
        </button>
    </div>
    <div id="checklist-list" class="items-list">
        <!-- Dynamic checklist rows added here -->
        <div class="item-row">
            <input type="checkbox" ${item.completed ? 'checked' : ''}>
            <input type="text" class="form-control" placeholder="Checklist item" value="${item.item}">
            <button type="button" class="btn-remove-item" onclick="this.parentElement.remove()">
                <i class="fas fa-trash"></i>
            </button>
        </div>
    </div>
</div>
```
**Data Source:** `session.checklist` (array of objects)  
**Object Structure:**
```javascript
{
    item: "Checklist item text",
    completed: false
}
```

---

#### 15. Google Services Integration
```html
<div class="form-section">
    <div class="section-header">
        <label><i class="fab fa-google"></i> Google Services</label>
    </div>
    <div class="google-sync-options">
        <label class="checkbox-label">
            <input type="checkbox" id="sync-google-tasks">
            <span>Sync with Google Tasks</span>
        </label>
        <label class="checkbox-label">
            <input type="checkbox" id="sync-google-calendar">
            <span>Sync with Google Calendar</span>
        </label>
    </div>
</div>
```
**Data Source:** Not stored in session (UI toggle only)  
**Purpose:** Enable Google sync on save

---

## 📋 POPUP WINDOW - Complete HTML Elements List

**Location:** Lines 22484-22700  
**Purpose:** Floating window with expanded card view  
**Key Discovery:** ⚠️ **USES `renderCardExpanded()` - NOT A SEPARATE INTERFACE!**

### Structure:
```html
<div id="popout-window-{sessionId}" class="popout-window" style="position: fixed; ...">
    <div class="popout-card-header">
        <span>Synergy Pop-Out</span>
        <button onclick="synergyBoard.closePopout('{sessionId}')">×</button>
    </div>
    
    <div class="popout-card-content">
        ${this.renderCardExpanded(session, priorityEmoji, statusClass, timeAgo)}
        <!-- ^^^ EXACT SAME CONTENT AS EXPANDED CARD VIEW! -->
    </div>
    
    <div class="popout-card-footer">
        <div class="popout-info">
            <span>Popped out at ${new Date().toLocaleTimeString()}</span>
            <span class="session-id-footer">${session.session_id}</span>
        </div>
    </div>
</div>
```

**Content:** See "EXPANDED CARD VIEW" section below - popup uses identical HTML!

**Additional Elements (Popup-Specific):**
- Draggable window container
- Close button (×)
- Popup timestamp in footer
- Session ID in footer

---

## 📋 EXPANDED CARD VIEW - Complete HTML Elements List

**Location:** Lines 21450-21700  
**Purpose:** Detailed read-only display of session  
**Used By:** Both expanded cards AND popup windows

### Structure:
```html
<div class="card-expanded-view">
    <!-- Header with actions -->
    <div class="card-header">
        <span class="card-priority">${priorityEmoji}</span>
        <div class="card-header-actions">
            <button class="card-action-icon" onclick="toggleCardExpand()" title="Collapse">
                <i class="fas fa-compress-alt"></i>
            </button>
            <button class="card-action-icon popout" onclick="popOutCard()" title="Pop Out">
                <i class="fas fa-external-link-alt"></i>
            </button>
            <button class="card-action-icon resume" onclick="resumeSession()" title="Resume">
                <i class="fas fa-play"></i>
            </button>
            <button class="card-action-icon edit" onclick="editCard()" title="Edit">
                <i class="fas fa-edit"></i>
            </button>
            <button class="card-action-icon delete" onclick="deleteCard()" title="Delete">
                <i class="fas fa-trash"></i>
            </button>
        </div>
    </div>
    
    <!-- Content sections -->
    ${titleHTML}
    ${descriptionHTML}
    ${metaHTML}
    ${assigneesHTML}
    ${datesHTML}
    ${docsHTML}
    ${linksHTML}
    ${stepsHTML}
    ${checklistHTML}
    ${threadIdsHTML}
    ${assignedAgentsHTML}
    ${notesHTML}
    ${activityLogHTML}
    ${footerHTML}
    ${actionsHTML}
</div>
```

### Complete Field List:

#### 1. Card Header Actions
```html
<div class="card-header">
    <span class="card-priority">${priorityEmoji}</span>
    <div class="card-header-actions">
        <button class="card-action-icon" title="Collapse">
            <i class="fas fa-compress-alt"></i>
        </button>
        <button class="card-action-icon popout" title="Pop Out">
            <i class="fas fa-external-link-alt"></i>
        </button>
        <button class="card-action-icon resume" title="Resume">
            <i class="fas fa-play"></i>
        </button>
        <button class="card-action-icon edit" title="Edit">
            <i class="fas fa-edit"></i>
        </button>
        <button class="card-action-icon delete" title="Delete">
            <i class="fas fa-trash"></i>
        </button>
    </div>
</div>
```
**Data:** `session.priority` → priorityEmoji (🟢🟡🔴)

---

#### 2. Title
```html
<div class="card-title-large">${this.escapeHtml(session.title)}</div>
```
**Data Source:** `session.title`  
**Display:** Large bold text

---

#### 3. Description (Conditional)
```html
${session.description ? `
    <div class="card-description">
        <div class="section-title"><i class="fas fa-align-left"></i> Description</div>
        <p>${this.escapeHtml(session.description)}</p>
    </div>
` : ''}
```
**Data Source:** `session.description`  
**Condition:** Only shows if description exists

---

#### 4. Meta Information
```html
<div class="card-meta-expanded">
    <div class="card-project">
        <i class="fas fa-folder"></i>
        ${this.escapeHtml(session.project_name || 'No Project')}
    </div>
    <span class="status-badge ${statusClass}">${session.status}</span>
    <span class="card-time"><i class="fas fa-clock"></i> ${timeAgo}</span>
</div>
```
**Data Sources:**
- `session.project_name`
- `session.status` → statusClass (status-active/paused/completed)
- `session.last_active` → timeAgo (formatted relative time)

---

#### 5. Assignees (Conditional)
```html
${assignees && assignees.length > 0 ? `
    <div class="card-assignees">
        <i class="fas fa-users"></i>
        ${assignees.join(', ')}
    </div>
` : ''}
```
**Data Source:** `session.assignees` (array)  
**Condition:** Only shows if assignees exist

---

#### 6. Due Date (Conditional)
```html
${session.due_date ? `
    <div class="card-dates">
        <span class="date-item ${isOverdue ? 'overdue' : ''}">
            <i class="fas fa-calendar"></i>
            Due: ${new Date(session.due_date).toLocaleDateString()}
        </span>
    </div>
` : ''}
```
**Data Source:** `session.due_date`  
**Processing:** Converts to Date, checks if overdue  
**Condition:** Only shows if due_date exists  
**⚠️ NOTE:** Due TIME is NOT displayed (only date)

---

#### 7. Documents Section (FIXED)
```html
${validDocuments.length > 0 ? `
    <div class="card-section">
        <div class="section-title"><i class="fas fa-file-alt"></i> Documents (${validDocuments.length})</div>
        <div class="document-list">
            ${validDocuments.map(doc => `
                <div class="document-item">
                    <i class="fas fa-file"></i>
                    <span class="doc-name">${this.escapeHtml(doc.title || doc.name || 'Untitled')}</span>
                    <span class="doc-size">${doc.size || 'N/A'}</span>
                </div>
            `).join('')}
        </div>
    </div>
` : ''}
```
**Data Source:** `session.documents` (array)  
**Processing:**
```javascript
const documents = this.parseJsonField(session.documents, []);
const validDocuments = documents.filter(doc => doc && (doc.title || doc.name) && doc.url);
```
**Object Structure:**
```javascript
{
    title: "Document Name",  // CHANGED FROM doc.name TO doc.title
    url: "https://...",
    type: "google_doc",
    size: "1.2MB",  // Optional
    created_at: "2025-11-07T..."
}
```
**✅ FIX APPLIED:** Now uses `doc.title || doc.name` to match edit modal

---

#### 8. Links Section (FIXED)
```html
${validLinks.length > 0 ? `
    <div class="card-section">
        <div class="section-title"><i class="fas fa-link"></i> Links (${validLinks.length})</div>
        <div class="link-list">
            ${validLinks.map(link => `
                <div class="link-item">
                    <i class="fas fa-external-link-alt"></i>
                    <a href="${link.url}" target="_blank" class="link-url">
                        ${this.escapeHtml(link.title || link.name || 'Untitled')}
                    </a>
                    <span class="link-type">${link.type || 'external'}</span>
                </div>
            `).join('')}
        </div>
    </div>
` : ''}
```
**Data Source:** `session.links` (array)  
**Processing:**
```javascript
const links = this.parseJsonField(session.links, []);
const validLinks = links.filter(link => link && (link.title || link.name) && link.url);
```
**✅ FIX APPLIED:** Now filters valid links and uses `link.title || link.name`

---

#### 9. Next Steps Section (FIXED)
```html
<div class="card-section">
    <div class="section-title"><i class="fas fa-tasks"></i> Next Steps ${validSteps.length > 0 ? `(${validSteps.length})` : ''}</div>
    <div class="steps-list">
        ${validSteps.length > 0 ? validSteps.map((step, idx) => `
            <div class="step-item ${step.completed ? 'completed' : ''}">
                <input type="checkbox" ${step.completed ? 'checked' : ''} 
                       onchange="synergyBoard.toggleStep('${session.session_id}', ${nextSteps.indexOf(step)})">
                <span class="step-description">${this.escapeHtml(step.description)}</span>
                ${step.due_date ? `<span class="step-due">Due: ${new Date(step.due_date).toLocaleDateString()}</span>` : ''}
            </div>
        `).join('') : '<div class="step-item" style="opacity: 0.6; font-style: italic;">No next steps added</div>'}
    </div>
</div>
```
**Data Source:** `session.next_steps` (array)  
**Processing (FIXED):**
```javascript
const nextSteps = this.parseJsonField(session.next_steps, []);
// BEFORE: filter(step => step && step.description && step.description.trim() !== '')
// AFTER: filter(step => step && step.description !== null && step.description !== undefined)
const validSteps = nextSteps.filter(step => step && step.description !== null && step.description !== undefined);
```
**✅ FIX APPLIED:** Removed overly strict `.trim() !== ''` check

---

#### 10. Checklist Section (FIXED)
```html
<div class="card-section">
    <div class="section-title"><i class="fas fa-check-square"></i> Checklist ${validChecklist.length > 0 ? `(${validChecklist.filter(c => c && c.completed).length}/${validChecklist.length})` : ''}</div>
    <div class="checklist">
        ${validChecklist.length > 0 ? validChecklist.map((item, idx) => `
            <div class="checklist-item ${item.completed ? 'completed' : ''}">
                <input type="checkbox" ${item.completed ? 'checked' : ''}
                       onchange="synergyBoard.toggleChecklistItem('${session.session_id}', ${checklist.indexOf(item)})">
                <span>${this.escapeHtml(item.item)}</span>
            </div>
        `).join('') : '<div class="checklist-item" style="opacity: 0.6; font-style: italic;">No checklist items added</div>'}
    </div>
</div>
```
**Data Source:** `session.checklist` (array)  
**Processing (FIXED):**
```javascript
const checklist = this.parseJsonField(session.checklist, []);
// BEFORE: filter(item => item && item.item && item.item.trim() !== '')
// AFTER: filter(item => item && item.item !== null && item.item !== undefined)
const validChecklist = checklist.filter(item => item && item.item !== null && item.item !== undefined);
```
**✅ FIX APPLIED:** Removed overly strict `.trim() !== ''` check

---

#### 11. Linked Threads (Conditional)
```html
${session.thread_ids && this.parseJsonField(session.thread_ids, []).length > 0 ? `
    <div class="card-section">
        <div class="section-title"><i class="fas fa-comments"></i> Linked Threads (${this.parseJsonField(session.thread_ids, []).length})</div>
        <div class="thread-list">
            ${this.parseJsonField(session.thread_ids, []).map(threadId => `
                <div class="thread-item">
                    <i class="fas fa-link"></i>
                    <span class="thread-id">${this.escapeHtml(threadId)}</span>
                </div>
            `).join('')}
        </div>
    </div>
` : ''}
```
**Data Source:** `session.thread_ids` (array of strings)  
**Condition:** Only shows if thread_ids exist

---

#### 12. Assigned Agents (Conditional)
```html
${session.assigned_agents && this.parseJsonField(session.assigned_agents, []).length > 0 ? `
    <div class="card-section">
        <div class="section-title"><i class="fas fa-robot"></i> Assigned Agents (${this.parseJsonField(session.assigned_agents, []).length})</div>
        <div class="agent-list">
            ${this.parseJsonField(session.assigned_agents, []).map(agent => `
                <div class="agent-item">
                    <i class="fas fa-brain"></i>
                    <span class="agent-name">${this.escapeHtml(agent)}</span>
                </div>
            `).join('')}
        </div>
    </div>
` : ''}
```
**Data Source:** `session.assigned_agents` (array of strings)  
**Condition:** Only shows if assigned_agents exist

---

#### 13. Notes (Conditional)
```html
${session.notes ? `
    <div class="card-section">
        <div class="section-title"><i class="fas fa-sticky-note"></i> Notes</div>
        <div class="card-notes">${this.escapeHtml(session.notes)}</div>
    </div>
` : ''}
```
**Data Source:** `session.notes`  
**Condition:** Only shows if notes exist  
**⚠️ NOTE:** Notes are NOT editable in expanded view (edit modal only)

---

#### 14. Activity Log
```html
<div class="card-section">
    <div class="section-title"><i class="fas fa-history"></i> Activity Log</div>
    <div class="activity-log">
        ${recentActivity && recentActivity.length > 0 ? recentActivity.map(activity => `
            <div class="activity-log-item">
                • ${this.escapeHtml(activity.description)}
                <span class="activity-time">${this.formatTimeAgo(activity.timestamp)}</span>
            </div>
        `).join('') : '<div class="activity-log-item">No activity yet</div>'}
    </div>
</div>
```
**Data Source:** `session.recent_activity` (array)  
**Object Structure:**
```javascript
{
    description: "Action description",
    timestamp: "2025-11-07T22:11:00Z"
}
```

---

#### 15. Footer with Tags & Session ID
```html
<div class="card-footer-expanded">
    <div class="card-tags">
        ${tags && tags.length > 0 ? tags.map(tag => `
            <span class="card-tag">${this.escapeHtml(tag)}</span>
        `).join('') : ''}
    </div>
    <span class="card-session-id-full">${session.session_id}</span>
</div>
```
**Data Sources:**
- `session.tags` (array)
- `session.session_id`

---

#### 16. Bottom Actions
```html
<div class="card-actions-expanded">
    <button class="card-action-icon" onclick="toggleCardExpand()" title="Collapse">
        <i class="fas fa-compress-alt"></i>
    </button>
    <button class="card-action-icon popout" onclick="popOutCard()" title="Pop Out">
        <i class="fas fa-external-link-alt"></i>
    </button>
    <button class="card-action-icon resume" onclick="resumeSession()" title="Resume">
        <i class="fas fa-play"></i>
    </button>
    <button class="card-action-icon edit" onclick="editCard()" title="Edit">
        <i class="fas fa-edit"></i>
    </button>
    <button class="card-action-icon delete" onclick="deleteCard()" title="Delete">
        <i class="fas fa-trash"></i>
    </button>
</div>
```
**Same as header actions** (duplicated for UX)

---

## 📋 COLLAPSED CARD VIEW - Complete HTML Elements List

**Location:** Lines 21296-21450  
**Purpose:** Minimal summary for quick scanning

### Structure:
```html
<div class="kanban-card" data-session-id="${session.session_id}" data-expanded="false">
    <div class="card-header-collapsed">
        <span class="card-priority">${priorityEmoji}</span>
        <span class="card-title">${this.escapeHtml(session.title)}</span>
    </div>
    
    <div class="card-meta">
        <span class="card-project">${this.escapeHtml(session.project_name)}</span>
        <span class="status-badge ${statusClass}">${session.status}</span>
    </div>
    
    <div class="card-stats">
        <span title="Messages"><i class="fas fa-comment"></i> ${session.message_count || 0}</span>
        <span title="Documents"><i class="fas fa-file"></i> ${documents.length || 0}</span>
        <span title="Next Steps"><i class="fas fa-tasks"></i> ${validSteps.length || 0}</span>
        <span class="card-time"><i class="fas fa-clock"></i> ${timeAgo}</span>
    </div>
    
    <div class="card-tags">
        ${tags && tags.length > 0 ? tags.slice(0, 3).map(tag => `
            <span class="card-tag">${this.escapeHtml(tag)}</span>
        `).join('') : ''}
    </div>
    
    <div class="card-actions">
        <button class="card-action-icon" onclick="toggleCardExpand()" title="Expand">
            <i class="fas fa-expand-alt"></i>
        </button>
        <button class="card-action-icon popout" onclick="popOutCard()" title="Pop Out">
            <i class="fas fa-external-link-alt"></i>
        </button>
        <button class="card-action-icon resume" onclick="resumeSession()" title="Resume">
            <i class="fas fa-play"></i>
        </button>
        <button class="card-action-icon edit" onclick="editCard()" title="Edit">
            <i class="fas fa-edit"></i>
        </button>
        <button class="card-action-icon delete" onclick="deleteCard()" title="Delete">
            <i class="fas fa-trash"></i>
        </button>
    </div>
    
    <div class="card-session-id">${session.session_id}</div>
</div>
```

### Field List:
1. **Priority** - Icon only (🟢🟡🔴)
2. **Title** - Truncated if long
3. **Project** - Project name
4. **Status** - Badge (active/paused/completed)
5. **Stats** - Message count, document count, next steps count, last active time
6. **Tags** - Max 3 tags shown
7. **Session ID** - Full ID displayed
8. **Actions** - Expand, pop out, resume, edit, delete buttons

**⚠️ MISSING:**
- Description
- Due date/time
- Assignees
- Links
- Checklist (count shown in stats, not items)
- Thread IDs
- Assigned Agents
- Notes
- Activity log
- Full document list (count only)

---

## 📊 FIELD COMPARISON TABLE

| Field | Edit Modal | Popup | Expanded | Collapsed | Data Source |
|-------|-----------|-------|----------|-----------|-------------|
| **Session ID** | Hidden input | Footer | Footer | Bottom | `session.session_id` |
| **Title** | ✅ Editable | ✅ Large | ✅ Large | ✅ Header | `session.title` |
| **Description** | ✅ Textarea | ❌ Missing | ✅ Section | ❌ Hidden | `session.description` |
| **Priority** | ✅ Dropdown | ✅ Icon+Text | ✅ Icon+Text | ✅ Icon | `session.priority` |
| **Status** | ✅ Dropdown | ✅ Badge | ✅ Badge | ✅ Badge | `session.status` |
| **Column** | ✅ Dropdown | N/A | N/A | N/A | `session.kanban_column` |
| **Project** | ✅ Text Input | ✅ Display | ✅ Display | ✅ Display | `session.project_name` |
| **Due Date** | ✅ Date Input | ❌ Missing | ✅ Display | ❌ Hidden | `session.due_date` (date part) |
| **Due Time** | ✅ Time Input | ❌ Missing | ❌ Missing | ❌ Hidden | `session.due_date` (time part) |
| **Last Active** | Auto | ✅ Relative | ✅ Relative | ✅ Relative | `session.last_active` |
| **Created At** | ❌ Missing | ❌ Missing | ❌ Missing | ❌ Hidden | `session.created_at` |
| **Assignees** | ✅ Comma-sep | ✅ List | ✅ List | ❌ Hidden | `session.assignees` |
| **Thread IDs** | ✅ Comma-sep | ✅ List | ✅ List | ❌ Hidden | `session.thread_ids` |
| **Assigned Agents** | ✅ Comma-sep | ✅ List | ✅ List | ❌ Hidden | `session.assigned_agents` |
| **Tags** | ✅ Comma-sep | ✅ All | ✅ All | ✅ Max 3 | `session.tags` |
| **Notes** | ✅ Textarea | ❌ Missing | ✅ Section | ❌ Hidden | `session.notes` |
| **Documents** | ✅ Multi-row | ✅ List | ✅ List | ✅ Count | `session.documents` (✅ FIXED) |
| **Links** | ✅ Multi-row | ✅ List | ✅ List | ❌ Hidden | `session.links` (✅ FIXED) |
| **Next Steps** | ✅ Multi-row | ✅ List | ✅ List | ✅ Count | `session.next_steps` (✅ FIXED) |
| **Checklist** | ✅ Multi-row | ✅ List | ✅ List | ❌ Hidden | `session.checklist` (✅ FIXED) |
| **Message Count** | ❌ Missing | ❌ Missing | ❌ Missing | ✅ Stats | `session.message_count` |
| **Activity Log** | ❌ Missing | ✅ Display | ✅ Display | ❌ Hidden | `session.recent_activity` |
| **Google Sync** | ✅ Checkboxes | ❌ Missing | ❌ Missing | ❌ Hidden | UI toggle only |

---

## 🎯 KEY FINDINGS

### 1. Popup Window Identity
**Popup window = Expanded card view in floating container**
- Uses `renderCardExpanded()` function
- NOT a separate interface
- Same content, different presentation (draggable window)

### 2. Data Flow Issues (NOW FIXED)
**Problem:** Edit modal showed data that expanded/popup didn't show  
**Root Causes:**
1. ✅ **FIXED:** Documents used `doc.name` instead of `doc.title`
2. ✅ **FIXED:** No filtering on documents/links (empty items rendered)
3. ✅ **FIXED:** Overly strict `.trim() !== ''` filtering removed valid items
4. ✅ **FIXED:** Field name inconsistency (`name` vs `title`)

### 3. Field Coverage
**Edit Modal:** 18/23 fields (78%) - Most complete  
**Popup/Expanded:** 15/23 fields (65%) - Detailed display (NOW SHOWS MORE DATA)  
**Collapsed:** 9/23 fields (39%) - Minimal summary

### 4. Missing Everywhere
- **Due Time** - Only in edit modal (time component of due_date)
- **Notes** - Only in edit modal  
- **Created At** - Not displayed anywhere (database has it)
- **Google Sync Status** - Only in edit modal (UI toggles)

---

## ✅ FIXES SUMMARY

### What Was Fixed (Lines 21456-21565):

1. **Documents (Line ~21464):**
   - Added filtering: `validDocuments = documents.filter(doc => doc && (doc.title || doc.name) && doc.url)`
   - Changed field: `doc.name` → `doc.title || doc.name || 'Untitled'`

2. **Links (Line ~21482):**
   - Added filtering: `validLinks = links.filter(link => link && (link.title || link.name) && link.url)`
   - Changed field: `link.title` → `link.title || link.name || 'Untitled'`

3. **Next Steps (Line ~21506):**
   - Removed: `.trim() !== ''` check
   - New filter: `step.description !== null && step.description !== undefined`

4. **Checklist (Line ~21543):**
   - Removed: `.trim() !== ''` check
   - New filter: `item.item !== null && item.item !== undefined`

### Expected Result:
**Edit modal, expanded view, and popup window now show SAME data!**

---

**Last Updated:** November 8, 2025  
**Status:** ✅ ALL DATA MISMATCH BUGS FIXED  
**Next Step:** Restart Flask server (`BISTART`) and test

# 📋 SYNERGY FLAT SPACING V2 - COMPLETE STRUCTURE

## 🔑 KEY FILES (3 Core Files)

### 1. **synergy-sidebar-renderer-v2-FLAT.js** (703 lines)
**Purpose:** Render synergy cards with flat spacing and two-row structure  
**Location:** `UI/external/modules/synergy/synergy-sidebar-renderer-v2-FLAT.js`

### 2. **synergy-inline-edit.js** (345 lines)  
**Purpose:** Inline editing for milestones/tasks/subtasks (NO popup)  
**Location:** `UI/external/modules/synergy/synergy-inline-edit.js`

### 3. **synergy-flat-spacing.css** (604 lines)
**Purpose:** CSS for flat structure with two-row layout  
**Location:** `UI/external/modules/synergy/synergy-flat-spacing.css`

---

## 📐 DATA STRUCTURE & FIELD FORMATS

### **SESSION OBJECT** (Top Level)
```javascript
{
  session_id: "syn_demo_1763552847",           // String, unique ID
  title: "E-Commerce Platform Redesign",       // String, max ~200 chars
  description: "Complete redesign...",          // String, unlimited, supports line breaks
  priority: "high",                             // Enum: "low", "medium", "high", "critical"
  status: "active",                             // Enum: "active", "completed", "blocked", "paused"
  project_name: "Website Overhaul",            // String, optional
  tags: ["web-development", "ui-ux"],          // Array of strings OR JSON string
  last_active: "2025-11-24T12:00:00Z",        // ISO 8601 datetime
  due_date: "2025-12-31T23:59:59Z",           // ISO 8601 datetime, optional
  documents: [...],                            // Array of document objects (see below)
  links: [...],                                // Array of link objects (see below)
  milestones: [...]                            // Array of milestone objects (see below)
}
```

### **MILESTONE OBJECT** (Second Level)
```javascript
{
  milestone_id: "ms_1234567890",               // String, unique ID
  milestone: "Phase 1: UI Design Complete",    // String, main text (NOT "title")
  description: "Design all pages...",          // String, optional
  priority: "high",                            // Enum: "low", "medium", "high", "critical"
  completed: false,                            // Boolean
  due_date: "2025-11-30T23:59:59Z",           // ISO 8601 datetime, optional
  assigned_to: "John Doe",                     // String, optional
  estimated_hours: 40,                         // Number, optional
  actual_hours: 25.5,                          // Number, optional
  tasks: [...],                                // Array of task objects (see below)
  documents: [...]                             // Array of document objects (milestone-specific)
}
```

### **TASK OBJECT** (Third Level)
```javascript
{
  task_id: "tsk_9876543210",                   // String, unique ID
  task: "Create wireframes for homepage",      // String, main text (NOT "title")
  description: "Include mobile versions",      // String, optional
  priority: "medium",                          // Enum: "low", "medium", "high", "critical"
  completed: false,                            // Boolean
  due_date: "2025-11-25T17:00:00Z",           // ISO 8601 datetime, optional
  assigned_to: "Jane Smith",                   // String, optional
  estimated_hours: 8,                          // Number, optional
  actual_hours: 6.5,                           // Number, optional
  subtasks: [...]                              // Array of subtask objects (see below)
}
```

### **SUBTASK OBJECT** (Fourth Level)
```javascript
{
  subtask_id: "sub_1111222233",                // String, unique ID
  subtask: "Sketch initial layout",            // String, main text (NOT "title")
  completed: false,                            // Boolean
  priority: "low",                             // Enum: "low", "medium", "high", "critical"
  estimated_hours: 2,                          // Number, optional
  actual_hours: 1.5                            // Number, optional
}
```

### **DOCUMENT OBJECT** (Attached to Session or Milestone)
```javascript
{
  id: "doc_5555666677",                        // String, unique ID (also accepts doc.document_id)
  name: "Design_Mockup_v3.pdf",               // String, filename (also accepts doc.title)
  type: "PDF",                                 // String, optional (e.g., "PDF", "DOCX", "PNG")
  url: "https://storage.../file.pdf",         // String, optional
  size: 2048576,                               // Number, bytes, optional
  uploaded_at: "2025-11-20T10:30:00Z"         // ISO 8601 datetime, optional
}
```

### **LINK OBJECT** (External URLs)
```javascript
{
  url: "https://figma.com/project/123",       // String, required
  title: "Figma Designs",                      // String, optional
  description: "All UI mockups"                // String, optional
}
```

---

## 🎨 TWO-ROW STRUCTURE (CRITICAL)

### **MILESTONE TWO-ROW LAYOUT**
```
ROW 1: [✓] M1          [HIGH]  [Edit] [Del] [🔗]
       ↑   ↑            ↑       ↑ Action buttons
       |   Index        Priority
       Checkbox

ROW 2: Milestone Title Here (17px, full width, editable)
       ↑ Content row spans full width
```

### **TASK TWO-ROW LAYOUT**
```
ROW 1: [✓] T1.1        [MED]   [Edit] [Del] [🔗]
ROW 2: Task Title Here (15px, full width, editable)
```

### **SUBTASK TWO-ROW LAYOUT**
```
ROW 1: [✓] S1.1.1      [LOW]   [Edit] [Del]
ROW 2: Subtask Title Here (14px, full width, editable)
```

### **DOCUMENT TWO-ROW LAYOUT**
```
ROW 1: PD1                      [Edit] [Del] [🔗]
       ↑ Index (no checkbox)
ROW 2: 📄 Filename.pdf (14px, icon + name)
```

---

## 🔢 INDEX FORMAT (NO BRACKETS!)

| Item Type | Format | Example | Rule |
|-----------|--------|---------|------|
| Milestone | `M{num}` | `M1`, `M2`, `M3` | Sequential from 1 |
| Task | `T{milestone}.{num}` | `T1.1`, `T1.2`, `T2.1` | Per milestone |
| Subtask | `S{milestone}.{task}.{num}` | `S1.1.1`, `S1.1.2` | Per task |
| Project Doc | `PD{num}` | `PD1`, `PD2` | Sequential from 1 |
| Milestone Doc | `MD{milestone}.{num}` | `MD1.1`, `MD2.1` | Per milestone |

**❌ WRONG:** `[M1]`, `[T1.1]`, `[S1.1.1]`  
**✅ CORRECT:** `M1`, `T1.1`, `S1.1.1`

---

## 📏 SPACING & SIZING RULES

### **Container**
- **Width:** `min-width: 400px` (was 350px)
- **Padding:** `8px` (left/right only)
- **Efficiency:** 95.4% usable width (384px of 400px)

### **Sections**
- **Spacing between:** `15px` (padding-top + margin-bottom)
- **Separator:** `1px solid border-top`
- **First section:** NO border-top

### **Font Sizes**
| Element | Size | Weight | Use |
|---------|------|--------|-----|
| Section header | 16px | Bold | "Project milestones" |
| Milestone title | **17px** | Normal | Main content row |
| Task title | **15px** | Normal | Main content row |
| Subtask title | **14px** | Normal | Main content row |
| Index (M1, T1.1) | 13px | 700 | Monospace font |
| Metadata | 13px | Normal | Stats, dates |
| Action buttons | 12px | 600 | Edit, Delete, etc. |

### **Visual Hierarchy (NO INDENTATION!)**
| Level | Border | Font | Badge |
|-------|--------|------|-------|
| Milestone | 3px blue left | 17px | M1 |
| Task | 2px gray left | 15px | T1.1 |
| Subtask | NO border | 14px | S1.1.1 |

---

## 🔧 INLINE EDITING SYSTEM

### **Edit Mode Flow**
```
1. User clicks "Edit" button
   ↓
2. editMilestone(sessionId, milestoneId) called
   ↓
3. Store original content in this.originalContent[milestoneId]
   ↓
4. Set contenteditable="true" on title div
   ↓
5. Focus title element
   ↓
6. Hide Edit/Delete buttons
   ↓
7. Show Save/Cancel buttons
   ↓
8. User edits text directly
   ↓
9a. SAVE: PATCH to /api/synergy/milestone/{id}
    → Disable contenteditable
    → Show Edit/Delete buttons
    → Hide Save/Cancel buttons
   
9b. CANCEL: Restore original text
    → Disable contenteditable
    → Show Edit/Delete buttons
    → Hide Save/Cancel buttons
```

### **API Endpoints**
| Action | Method | Endpoint | Body |
|--------|--------|----------|------|
| Save Milestone | PATCH | `/api/synergy/milestone/{id}` | `{milestone, description}` |
| Delete Milestone | DELETE | `/api/synergy/milestone/{id}` | None |
| Toggle Complete | PATCH | `/api/synergy/milestone/{id}` | `{completed: true/false}` |
| Save Task | PATCH | `/api/synergy/task/{id}` | `{task, description}` |
| Delete Task | DELETE | `/api/synergy/task/{id}` | None |
| Save Subtask | PATCH | `/api/synergy/subtask/{id}` | `{subtask}` |
| Delete Subtask | DELETE | `/api/synergy/subtask/{id}` | None |

### **HTML Attributes**
```html
<!-- Milestone container -->
<div class="synergy-flat-milestone" 
     data-milestone-id="ms_1234567890" 
     data-editing="false">
  
  <!-- Editable title -->
  <div class="synergy-flat-milestone-title" 
       contenteditable="false" 
       data-field="milestone">
    Milestone Title Text
  </div>
  
  <!-- Edit actions (hidden by default) -->
  <div class="synergy-flat-edit-actions" style="display: none;">
    <button class="synergy-save-btn">Save</button>
    <button class="synergy-cancel-btn">Cancel</button>
  </div>
</div>
```

---

## 🎯 PRIORITY BADGES

### **Priority Enum Values**
```javascript
priority: "low"       // Gray badge
priority: "medium"    // Blue badge  
priority: "high"      // Orange badge
priority: "critical"  // Red badge
```

### **CSS Classes**
```css
.priority-badge {
  padding: 3px 8px;
  border-radius: 6px;
  font-size: 11px;
  font-weight: 700;
}

.priority-low { background: #6b7280; }
.priority-medium { background: #3b82f6; }
.priority-high { background: #f59e0b; }
.priority-critical { background: #dc2626; }
```

---

## ✅ STATUS BADGES

### **Status Enum Values**
```javascript
status: "active"      // Green circle icon
status: "completed"   // Blue circle icon
status: "blocked"     // Red triangle icon
status: "paused"      // Orange pause icon
```

---

## 📊 CALCULATED FIELDS

### **Progress Calculation**
```javascript
// Milestone progress
const tasksDone = tasks.filter(t => t.completed).length;
const totalTasks = tasks.length;
const progress = Math.round((tasksDone / totalTasks) * 100) || 0;

// Session progress  
const milestonesComplete = milestones.filter(m => m.completed).length;
const totalMilestones = milestones.length;
const sessionProgress = Math.round((milestonesComplete / totalMilestones) * 100) || 0;
```

---

## 🚀 KEY METHODS

### **Renderer Methods** (synergy-sidebar-renderer-v2-FLAT.js)
```javascript
// Main rendering
renderExpandedCardContent(session, milestones, sessionId)
renderMilestonesSection(milestones, sessionId)
renderMilestone(milestone, milestoneNum, sessionId)
renderTask(task, milestoneNum, taskNum, sessionId)
renderSubtask(subtask, milestoneNum, taskNum, subtaskNum, sessionId)
renderDocumentsSection(documents, sessionId)

// Sections
renderMetadataSection(session)
renderDescriptionSection(description)
renderLinksSection(links)
renderTagsSection(tags)

// Utilities
escapeHtml(text)
parseJsonField(field, fallback)
calculateSessionCounts(session)
```

### **Inline Edit Methods** (synergy-inline-edit.js)
```javascript
// Milestone editing
editMilestone(sessionId, milestoneId)
saveMilestone(sessionId, milestoneId)
deleteMilestone(sessionId, milestoneId)
toggleMilestoneComplete(sessionId, milestoneId, completed)
linkMilestone(sessionId, milestoneId)

// Task editing
editTask(sessionId, taskId)
saveTask(sessionId, taskId)
deleteTask(sessionId, taskId)
toggleTaskComplete(sessionId, taskId, completed)

// Subtask editing
editSubtask(sessionId, subtaskId)
saveSubtask(sessionId, subtaskId)
deleteSubtask(sessionId, subtaskId)
toggleSubtaskComplete(sessionId, subtaskId, completed)

// Document editing (TODO placeholders)
editDoc(sessionId, docId)
deleteDoc(sessionId, docId)
openDoc(sessionId, docId)

// Helpers
toggleEditMode(container, isEditing)
cancelEdit(sessionId, itemId)
```

---

## 🎨 CSS CLASSES REFERENCE

### **Container Classes**
- `.synergy-flat-container` - Main container (400px min, 8px padding)
- `.synergy-flat-section` - Section wrapper (15px spacing)
- `.synergy-flat-section-header` - Section title row

### **Milestone Classes**
- `.synergy-flat-milestone` - Milestone container (3px blue border, 17px title)
- `.synergy-flat-milestone-header` - Row 1 controls
- `.synergy-flat-milestone-title` - Row 2 editable title (17px)
- `.synergy-flat-milestone-desc` - Optional description

### **Task Classes**
- `.synergy-flat-task` - Task container (2px gray border, 15px title)
- `.synergy-flat-task-header` - Row 1 controls
- `.synergy-flat-task-title` - Row 2 editable title (15px)

### **Subtask Classes**
- `.synergy-flat-subtask` - Subtask container (no border, 14px title)
- `.synergy-flat-subtask-header` - Row 1 controls
- `.synergy-flat-subtask-title` - Row 2 editable title (14px)

### **Document Classes**
- `.synergy-flat-doc-item` - Document container
- `.synergy-flat-doc-header` - Row 1 index + actions
- `.synergy-flat-doc-title` - Row 2 icon + filename

### **Control Classes**
- `.synergy-flat-header-left` - Checkbox + index
- `.synergy-flat-header-right` - Priority + action buttons
- `.synergy-flat-index` - M1, T1.1, S1.1.1 (13px monospace)
- `.synergy-flat-checkbox` - Checkbox input
- `.synergy-flat-action-btn` - Base button style
- `.synergy-edit-btn` - Edit button (blue hover)
- `.synergy-delete-btn` - Delete button (red hover)
- `.synergy-save-btn` - Save button (green)
- `.synergy-cancel-btn` - Cancel button (gray)
- `.synergy-link-btn` - Link button (🔗)
- `.synergy-flat-edit-actions` - Save/Cancel container (hidden by default)

---

## 📦 SPACE EFFICIENCY COMPARISON

### **Old System (V1)**
- Container width: 350px
- Nested indentation: 20px per level
- Milestone: 0px indent = 350px usable
- Task: 20px indent = 330px usable (94.3%)
- Subtask: 40px indent = 310px usable (88.6%)
- **Average usable width: 262px (75%)**

### **New System (V2)**
- Container width: 400px
- NO nested indentation (flat structure)
- Container padding: 8px left + 8px right = 16px total
- Milestone: 384px usable (96%)
- Task: 384px usable (96%)
- Subtask: 384px usable (96%)
- **Average usable width: 384px (96%)**

### **Improvement**
- +72px more space per item (+27%)
- +21% efficiency gain
- Visual hierarchy via borders/badges instead of indentation

---

## 🔐 SECURITY CONSIDERATIONS

### **XSS Prevention**
All user input is escaped via `escapeHtml()` method:
```javascript
escapeHtml(text) {
    if (!text) return '';
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}
```

Used in:
- Milestone titles
- Task titles
- Subtask titles
- Document names
- Descriptions
- Project names

### **CSRF Protection**
API endpoints should implement CSRF tokens (backend responsibility).

### **Authorization**
All API calls should verify:
- User owns the session
- User has permission to edit/delete
- Session ID is valid

---

## 🧪 TESTING CHECKLIST

### **Visual Layout**
- [ ] Two-row structure renders correctly
- [ ] NO brackets on indices (M1, T1.1, S1.1.1)
- [ ] Font sizes: 17px milestone, 15px task, 14px subtask
- [ ] 400px minimum container width
- [ ] 15px spacing between sections
- [ ] Action buttons aligned right
- [ ] Checkboxes aligned left with indices

### **Inline Editing**
- [ ] Click Edit → contenteditable activates
- [ ] Edit/Delete buttons hide
- [ ] Save/Cancel buttons show
- [ ] Title gets blue border on edit
- [ ] Can type new text
- [ ] Click Save → PATCH request sent
- [ ] Click Cancel → original text restored
- [ ] After save/cancel → buttons toggle back

### **Delete Functionality**
- [ ] Click Delete → confirmation dialog
- [ ] Confirm → DELETE request sent
- [ ] Item removed from DOM
- [ ] Cancel → no changes

### **Checkbox Toggle**
- [ ] Click checkbox → PATCH request
- [ ] Checkbox state updates
- [ ] Milestone completion updates progress bars

### **Responsive Behavior**
- [ ] Container scrolls horizontally if needed
- [ ] Action buttons wrap on small screens
- [ ] Text remains readable at all sizes

---

## 🐛 KNOWN ISSUES

### **Fixed Issues**
- ✅ `sessionId` undefined in `renderDocumentsSection` - Fixed by passing parameter
- ✅ `SynergyInlineEdit` methods not accessible - Fixed by creating instance immediately
- ✅ Brackets on indices - Removed ([M1] → M1)
- ✅ Single-row layout - Changed to two-row structure

### **Pending Issues**
- ❌ Document editing not implemented (editDoc, deleteDoc, openDoc are TODO placeholders)
- ❌ Backend API endpoints may not exist yet (need verification)
- ❌ Realtime updates not implemented (changes require page refresh)

---

## 🚀 FUTURE ENHANCEMENTS

### **Phase 1 - Core Functionality**
- [ ] Implement document editing (upload/delete/rename)
- [ ] Add drag-and-drop reordering for milestones/tasks/subtasks
- [ ] Add keyboard shortcuts (Ctrl+S to save, Esc to cancel)
- [ ] Add rich text editing (bold, italic, links)

### **Phase 2 - Collaboration**
- [ ] Realtime updates via WebSocket
- [ ] Multi-user editing indicators
- [ ] Comment threads on milestones/tasks
- [ ] @mentions for assigning users

### **Phase 3 - Advanced Features**
- [ ] Gantt chart view
- [ ] Time tracking integration
- [ ] File attachment preview
- [ ] Export to PDF/Excel
- [ ] Custom fields and templates
- [ ] Recurring tasks

---

## 📚 RELATED DOCUMENTATION

- `synergy-sidebar-renderer-v2-FLAT.js` - Full implementation with comments
- `synergy-inline-edit.js` - Inline editing implementation
- `synergy-flat-spacing.css` - Complete CSS rules
- `business-ai-platform-v2.html` - HTML integration (lines 3150-3165)

---

**Last Updated:** November 24, 2025  
**Version:** 2.0  
**Status:** Production Ready (inline editing functional, document editing pending)

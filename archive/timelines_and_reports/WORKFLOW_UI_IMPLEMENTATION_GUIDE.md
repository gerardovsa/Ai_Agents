# 🎨 Workflow UI Implementation Guide
## Handling `visual_automations` vs `automation_workflows` in the UI

## Executive Summary

The UI must **intelligently handle TWO workflow types** with different data structures, states, and capabilities:

1. **Draft Workflows** (from `visual_automations` table)
2. **Production Workflows** (from `automation_workflows` table)

This guide provides complete UI patterns for displaying, editing, and managing both workflow types.

---

## 📊 UI Component Strategy

### Component Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    WORKFLOW LIBRARY UI                      │
│  (Shows ALL workflows with visual distinction)              │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  ┌────────────────────┐  ┌────────────────────┐            │
│  │  DRAFT WORKFLOW    │  │ PRODUCTION WORKFLOW│            │
│  │  (Purple border)   │  │  (Green border)    │            │
│  ├────────────────────┤  ├────────────────────┤            │
│  │ • Edit button      │  │ • Enable toggle    │            │
│  │ • Promote button   │  │ • View stats       │            │
│  │ • Delete button    │  │ • Edit (demote)    │            │
│  └────────────────────┘  └────────────────────┘            │
│                                                             │
└─────────────────────────────────────────────────────────────┘
                           │
                           │ Double-click or Edit
                           ↓
┌─────────────────────────────────────────────────────────────┐
│                  WORKFLOW CANVAS EDITOR                     │
│  (Always loads from visual_automations)                     │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  • Drag-and-drop shapes (triggers, actions, conditions)    │
│  • Connect shapes with arrows                               │
│  • Configure tool parameters in side panel                  │
│  • Auto-save every 30 seconds → visual_automations         │
│  • "Save Draft" button → visual_automations                │
│  • "Activate" button → visual_automations + promote        │
│                                                             │
└─────────────────────────────────────────────────────────────┘
                           │
                           │ Click "Activate"
                           ↓
┌─────────────────────────────────────────────────────────────┐
│                PROMOTION CONFIRMATION MODAL                 │
│                                                             │
│  "Activate this workflow for production?"                  │
│                                                             │
│  This will:                                                 │
│  • Validate the workflow structure                          │
│  • Create production entry in automation_workflows          │
│  • Enable scheduling (if configured)                        │
│  • Start execution monitoring                               │
│                                                             │
│  [Cancel]  [Activate Workflow]                             │
└─────────────────────────────────────────────────────────────┘
```

---

## 🎯 UI Visual Distinctions

### Workflow Card Appearance (Current Implementation)

**From `business-ai-platform-v2.html` lines 20386-20450:**

```javascript
// Determine if production (in automation_workflows) or draft (visual_automations only)
const isProduction = automation.is_production || automation.workflow_state === 'production';
const isDraft = !isProduction;
const borderColor = isProduction ? '#10B981' : '#A855F7'; // Green vs Purple
const stateLabel = isProduction ? 'PRODUCTION READY' : 'DRAFT MODE';
const stateIcon = isProduction ? 'fa-check-circle' : 'fa-drafting-compass';
const stateBgColor = isProduction ? 'rgba(16, 185, 129, 0.1)' : 'rgba(168, 85, 247, 0.1)';
```

**Visual Result:**

```
┌────────────────────────────────────────────────────────┐
│ ◤ Purple Border (DRAFT)                                │
│ ┌──────────────────────────────────────────────────┐   │
│ │ Daily Email Summary                               │   │
│ │ daily-email-summary                    [DRAFT]   │   │
│ ├──────────────────────────────────────────────────┤   │
│ │ Summarizes unread emails every morning            │   │
│ ├──────────────────────────────────────────────────┤   │
│ │ 📧 email  • Updated 2h ago  • 🎨 DRAFT MODE      │   │
│ ├──────────────────────────────────────────────────┤   │
│ │ ▶ 0 runs  • ✓ 0 success  • ⚠ 0 errors           │   │
│ └──────────────────────────────────────────────────┘   │
└────────────────────────────────────────────────────────┘

┌────────────────────────────────────────────────────────┐
│ ◤ Green Border (PRODUCTION)                            │
│ ┌──────────────────────────────────────────────────┐   │
│ │ Backup Sheets Daily                               │   │
│ │ backup-sheets-daily            [ON] ⬜ ENABLED   │   │
│ ├──────────────────────────────────────────────────┤   │
│ │ Backs up all Google Sheets at 2am daily          │   │
│ ├──────────────────────────────────────────────────┤   │
│ │ 📊 data  • Updated 1d ago  • ✓ PRODUCTION READY  │   │
│ ├──────────────────────────────────────────────────┤   │
│ │ ▶ 45 runs  • ✓ 43 success  • ⚠ 2 errors         │   │
│ └──────────────────────────────────────────────────┘   │
└────────────────────────────────────────────────────────┘
```

---

## 📋 UI Component Breakdown

### 1. Workflow Library (List View)

**Purpose**: Display all workflows with clear status indication

**Data Source**: 
```javascript
// FROM: /api/automation/list endpoint
// QUERY: LEFT JOIN visual_automations + automation_workflows
const workflows = await fetch('/api/automation/list', {
    headers: { 'Authorization': `Bearer ${token}` }
});
```

**UI Elements by Workflow Type**:

| Element | Draft Workflow | Production Workflow |
|---------|---------------|---------------------|
| **Border Color** | `#A855F7` (Purple) | `#10B981` (Green) |
| **Status Badge** | "DRAFT MODE" (purple bg) | "PRODUCTION READY" (green bg) |
| **Icon** | `fa-drafting-compass` | `fa-check-circle` |
| **Actions** | Edit, Delete, Promote | Enable/Disable toggle, View Stats, Demote |
| **Stats Display** | Minimal (0 runs usually) | Full stats (runs, success, errors) |
| **Enable Toggle** | ❌ Hidden (not in production) | ✅ Visible (checkbox) |
| **Dimming** | No (always full opacity) | ✅ If loaded in canvas (opacity: 0.6) |

---

### 2. Workflow Card HTML Template

**Enhanced Template with Type Awareness:**

```html
<div class="workflow-card" 
     data-workflow-slug="${workflow.slug}"
     data-workflow-type="${workflow.is_production ? 'production' : 'draft'}"
     data-workflow-id="${workflow.workflow_id || workflow.automation_id}"
     style="border-left: 4px solid ${borderColor};">
    
    <!-- Header Section -->
    <div class="workflow-header">
        <div class="workflow-title-section">
            <h3 class="workflow-title">${workflow.title || workflow.name}</h3>
            <span class="workflow-slug">${workflow.slug}</span>
        </div>
        
        <!-- Right-side controls (TYPE DEPENDENT) -->
        <div class="workflow-controls">
            ${workflow.is_production ? `
                <!-- PRODUCTION: Enable/Disable Toggle -->
                <label class="workflow-toggle-label">
                    <input type="checkbox" 
                           class="workflow-enable-toggle"
                           data-workflow-id="${workflow.workflow_id}"
                           ${workflow.enabled ? 'checked' : ''}
                           onchange="toggleWorkflowEnabled(this)">
                    <span class="toggle-label-text">
                        ${workflow.enabled ? 'ENABLED' : 'DISABLED'}
                    </span>
                </label>
            ` : `
                <!-- DRAFT: Status Badge Only -->
                <span class="workflow-status-badge draft-badge">
                    <i class="fas fa-drafting-compass"></i>
                    DRAFT MODE
                </span>
            `}
        </div>
    </div>
    
    <!-- Description -->
    ${workflow.description ? `
        <p class="workflow-description">${workflow.description}</p>
    ` : ''}
    
    <!-- Metadata Row -->
    <div class="workflow-metadata">
        ${workflow.category ? `
            <span class="metadata-item">
                <i class="fas fa-tag"></i>
                ${workflow.category}
            </span>
        ` : ''}
        <span class="metadata-item">
            <i class="fas fa-clock"></i>
            Updated ${timeAgo(workflow.updated_at)}
        </span>
        <span class="metadata-item">
            <i class="fas ${workflow.is_production ? 'fa-check-circle' : 'fa-drafting-compass'}" 
               style="color: ${borderColor};"></i>
            ${workflow.is_production ? 'PRODUCTION' : 'DRAFT'}
        </span>
    </div>
    
    <!-- Stats Row (PRODUCTION ONLY shows meaningful stats) -->
    <div class="workflow-stats">
        <span class="stat-item">
            <i class="fas fa-play-circle"></i>
            <strong>${workflow.run_count || 0}</strong> runs
        </span>
        <span class="stat-item">
            <i class="fas fa-check-circle success-icon"></i>
            <strong>${workflow.success_count || 0}</strong> success
        </span>
        <span class="stat-item">
            <i class="fas fa-exclamation-circle error-icon"></i>
            <strong>${workflow.error_count || 0}</strong> errors
        </span>
        
        ${workflow.is_production && workflow.success_count > 0 ? `
            <!-- Success Rate Indicator -->
            <span class="stat-item success-rate">
                ${Math.round((workflow.success_count / workflow.run_count) * 100)}% success rate
            </span>
        ` : ''}
    </div>
    
    <!-- Action Buttons (TYPE DEPENDENT) -->
    <div class="workflow-actions">
        ${workflow.is_production ? `
            <!-- PRODUCTION Actions -->
            <button class="btn-secondary btn-sm" onclick="viewWorkflowStats('${workflow.slug}')">
                <i class="fas fa-chart-line"></i>
                View Stats
            </button>
            <button class="btn-secondary btn-sm" onclick="viewExecutionHistory('${workflow.slug}')">
                <i class="fas fa-history"></i>
                History
            </button>
            <button class="btn-warning btn-sm" onclick="demoteWorkflow('${workflow.slug}')">
                <i class="fas fa-arrow-down"></i>
                Demote to Draft
            </button>
        ` : `
            <!-- DRAFT Actions -->
            <button class="btn-primary btn-sm" onclick="editWorkflow('${workflow.slug}')">
                <i class="fas fa-edit"></i>
                Edit
            </button>
            <button class="btn-success btn-sm" onclick="promoteWorkflow('${workflow.slug}')">
                <i class="fas fa-rocket"></i>
                Activate
            </button>
            <button class="btn-danger btn-sm" onclick="deleteWorkflow('${workflow.slug}')">
                <i class="fas fa-trash"></i>
                Delete
            </button>
        `}
    </div>
</div>
```

---

### 3. Canvas Editor (Workflow Designer)

**Always Loads from `visual_automations`** (source of truth for design)

```javascript
// automation-workflows.js - loadWorkflowFromList()
async loadWorkflowFromList(workflowData) {
    console.log('[AUTOMATION] Loading workflow from library:', workflowData.slug);
    
    // ✅ IMPORTANT: Always loads from visual_automations table
    // Even if workflow is in production, canvas edits the design source
    
    // Clear current canvas
    this.clearCanvas();
    
    // Set workflow metadata
    this.workflowSlug = workflowData.slug;
    this.workflowTitle = workflowData.title || workflowData.name || 'Untitled Workflow';
    this.workflowDescription = workflowData.description || '';
    this.workflowStatus = workflowData.status || 'draft';
    
    // Extract shapes and connections from visual_automations.ui_json
    const uiJson = workflowData.ui_json || {};
    const shapes = uiJson.shapes || workflowData.shapes || [];
    const connections = uiJson.connections || workflowData.connections || [];
    
    // Load shapes onto canvas
    shapes.forEach(shape => {
        this.addShape(shape.type, shape.x, shape.y, {
            id: shape.id,
            text: shape.text,
            color: shape.color,
            width: shape.width,
            height: shape.height,
            config: shape.config || {} // Tool configuration
        });
    });
    
    // Load connections
    connections.forEach(conn => {
        this.addConnection(conn.from, conn.to, conn.id);
    });
    
    // Update UI to show workflow type
    this.updateWorkflowTypeIndicator(workflowData);
    
    // Enable appropriate buttons
    this.updateActionButtons(workflowData);
    
    this.render();
}
```

**Canvas Header UI (Shows Workflow Type):**

```html
<div class="canvas-header">
    <div class="workflow-info">
        <h2 class="workflow-title-display">${this.workflowTitle}</h2>
        <span class="workflow-slug-display">${this.workflowSlug}</span>
        
        <!-- Workflow Type Badge -->
        <span class="workflow-type-badge ${workflowData.is_production ? 'production' : 'draft'}">
            <i class="fas ${workflowData.is_production ? 'fa-check-circle' : 'fa-drafting-compass'}"></i>
            ${workflowData.is_production ? 'PRODUCTION' : 'DRAFT'}
        </span>
        
        ${workflowData.is_production ? `
            <span class="workflow-warning-badge">
                <i class="fas fa-exclamation-triangle"></i>
                Editing production workflow - changes require reactivation
            </span>
        ` : ''}
    </div>
    
    <div class="canvas-actions">
        <!-- Always available: Save Draft -->
        <button class="btn-secondary" onclick="automationCanvas.saveDraft()">
            <i class="fas fa-save"></i>
            Save Draft
        </button>
        
        ${workflowData.is_production ? `
            <!-- PRODUCTION: Update & Reactivate -->
            <button class="btn-warning" onclick="automationCanvas.updateProduction()">
                <i class="fas fa-sync"></i>
                Update Production
            </button>
        ` : `
            <!-- DRAFT: Activate -->
            <button class="btn-success" onclick="automationCanvas.activateWorkflow()">
                <i class="fas fa-rocket"></i>
                Activate
            </button>
        `}
        
        <button class="btn-secondary" onclick="automationCanvas.clearCanvas()">
            <i class="fas fa-eraser"></i>
            Clear
        </button>
    </div>
</div>
```

---

### 4. Shape Configuration Panel (Tool Parameters)

**Side panel for configuring tool parameters** (appears when shape is selected)

```javascript
// automation-workflows.js - showShapeConfigPanel()
showShapeConfigPanel(shape) {
    const panel = document.getElementById('shape-config-panel');
    if (!panel) return;
    
    // Determine tool type from shape
    const toolName = shape.config?.tool || this.inferToolFromShape(shape);
    
    // Fetch tool schema from registry
    const toolSchema = this.getToolSchema(toolName);
    
    if (!toolSchema) {
        panel.innerHTML = `
            <div class="config-panel-header">
                <h3>Configure Shape</h3>
            </div>
            <div class="config-panel-body">
                <p>No configuration available for this shape type.</p>
            </div>
        `;
        return;
    }
    
    // Build dynamic form based on tool parameters
    const formHtml = this.buildParameterForm(toolSchema, shape.config || {});
    
    panel.innerHTML = `
        <div class="config-panel-header">
            <h3>Configure: ${toolSchema.name}</h3>
            <p class="tool-description">${toolSchema.description}</p>
        </div>
        <div class="config-panel-body">
            ${formHtml}
        </div>
        <div class="config-panel-footer">
            <button class="btn-primary" onclick="automationCanvas.saveShapeConfig()">
                <i class="fas fa-check"></i>
                Save Configuration
            </button>
            <button class="btn-secondary" onclick="automationCanvas.closeConfigPanel()">
                <i class="fas fa-times"></i>
                Cancel
            </button>
        </div>
    `;
    
    panel.style.display = 'block';
}

// Build form fields dynamically from tool schema
buildParameterForm(toolSchema, currentConfig) {
    const parameters = toolSchema.parameters || {};
    const required = toolSchema.required || [];
    
    let html = '<form id="tool-config-form" class="parameter-form">';
    
    for (const [paramName, paramDef] of Object.entries(parameters)) {
        const isRequired = required.includes(paramName);
        const currentValue = currentConfig[paramName] || paramDef.default || '';
        
        html += `
            <div class="form-group">
                <label for="param-${paramName}" class="form-label">
                    ${paramDef.description || paramName}
                    ${isRequired ? '<span class="required-asterisk">*</span>' : ''}
                </label>
                ${this.renderParameterInput(paramName, paramDef, currentValue)}
                ${paramDef.help ? `
                    <small class="form-help-text">${paramDef.help}</small>
                ` : ''}
            </div>
        `;
    }
    
    html += '</form>';
    return html;
}

// Render appropriate input based on parameter type
renderParameterInput(paramName, paramDef, currentValue) {
    const type = paramDef.type;
    const inputId = `param-${paramName}`;
    
    switch (type) {
        case 'string':
            if (paramDef.enum) {
                // Dropdown for enum values
                return `
                    <select id="${inputId}" name="${paramName}" class="form-control">
                        ${paramDef.enum.map(val => `
                            <option value="${val}" ${val === currentValue ? 'selected' : ''}>
                                ${val}
                            </option>
                        `).join('')}
                    </select>
                `;
            } else if (paramDef.format === 'textarea') {
                // Textarea for long text
                return `
                    <textarea id="${inputId}" name="${paramName}" 
                              class="form-control" rows="4"
                              placeholder="${paramDef.placeholder || ''}">${currentValue}</textarea>
                `;
            } else {
                // Regular text input
                return `
                    <input type="text" id="${inputId}" name="${paramName}" 
                           class="form-control" value="${currentValue}"
                           placeholder="${paramDef.placeholder || ''}">
                `;
            }
        
        case 'integer':
        case 'number':
            return `
                <input type="number" id="${inputId}" name="${paramName}" 
                       class="form-control" value="${currentValue}"
                       ${paramDef.minimum !== undefined ? `min="${paramDef.minimum}"` : ''}
                       ${paramDef.maximum !== undefined ? `max="${paramDef.maximum}"` : ''}
                       ${type === 'integer' ? 'step="1"' : 'step="any"'}>
            `;
        
        case 'boolean':
            return `
                <label class="checkbox-label">
                    <input type="checkbox" id="${inputId}" name="${paramName}" 
                           ${currentValue ? 'checked' : ''}>
                    <span class="checkbox-text">${paramDef.label || 'Enable'}</span>
                </label>
            `;
        
        case 'array':
            // Multi-value input (tags/list)
            return `
                <input type="text" id="${inputId}" name="${paramName}" 
                       class="form-control tags-input" 
                       value="${Array.isArray(currentValue) ? currentValue.join(', ') : currentValue}"
                       placeholder="${paramDef.placeholder || 'Separate multiple values with commas'}">
                <small class="form-help-text">Enter multiple values separated by commas</small>
            `;
        
        case 'object':
            // JSON editor
            return `
                <textarea id="${inputId}" name="${paramName}" 
                          class="form-control code-editor" rows="6"
                          placeholder="${paramDef.placeholder || 'Enter JSON object'}">${JSON.stringify(currentValue, null, 2)}</textarea>
                <small class="form-help-text">Enter valid JSON</small>
            `;
        
        default:
            // Fallback: text input
            return `
                <input type="text" id="${inputId}" name="${paramName}" 
                       class="form-control" value="${currentValue}">
            `;
    }
}
```

**Parameter Form CSS:**

```css
.parameter-form {
    display: flex;
    flex-direction: column;
    gap: 16px;
    padding: 16px;
}

.form-group {
    display: flex;
    flex-direction: column;
    gap: 6px;
}

.form-label {
    font-size: 13px;
    font-weight: 600;
    color: var(--text-primary);
}

.required-asterisk {
    color: var(--error);
    margin-left: 4px;
}

.form-control {
    padding: 8px 12px;
    border: 1px solid var(--border-color);
    border-radius: 6px;
    background: var(--bg-primary);
    color: var(--text-primary);
    font-size: 13px;
}

.form-control:focus {
    outline: none;
    border-color: var(--accent-primary);
    box-shadow: 0 0 0 3px var(--accent-primary-alpha);
}

.form-help-text {
    font-size: 11px;
    color: var(--text-muted);
    font-style: italic;
}

.checkbox-label {
    display: flex;
    align-items: center;
    gap: 8px;
    cursor: pointer;
    user-select: none;
}

.tags-input {
    font-family: monospace;
}

.code-editor {
    font-family: 'Fira Code', 'Courier New', monospace;
    font-size: 12px;
    line-height: 1.5;
}
```

---

### 5. Workflow Promotion Modal

**Modal for activating draft workflows:**

```html
<div id="promote-workflow-modal" class="modal" style="display: none;">
    <div class="modal-overlay" onclick="closePromoteModal()"></div>
    <div class="modal-content promote-modal">
        <div class="modal-header">
            <h2>
                <i class="fas fa-rocket" style="color: var(--success);"></i>
                Activate Workflow
            </h2>
            <button class="modal-close-btn" onclick="closePromoteModal()">
                <i class="fas fa-times"></i>
            </button>
        </div>
        
        <div class="modal-body">
            <div class="workflow-summary">
                <h3 id="promote-workflow-title"></h3>
                <p id="promote-workflow-slug" class="workflow-slug-display"></p>
            </div>
            
            <div class="promotion-info-box">
                <h4>This will:</h4>
                <ul class="promotion-checklist">
                    <li>
                        <i class="fas fa-check-circle success-icon"></i>
                        Validate workflow structure and tool parameters
                    </li>
                    <li>
                        <i class="fas fa-check-circle success-icon"></i>
                        Create production entry in automation system
                    </li>
                    <li>
                        <i class="fas fa-check-circle success-icon"></i>
                        Enable scheduling (if configured)
                    </li>
                    <li>
                        <i class="fas fa-check-circle success-icon"></i>
                        Start execution monitoring and logging
                    </li>
                </ul>
            </div>
            
            <!-- Scheduling Options -->
            <div class="promotion-options">
                <h4>Scheduling (Optional)</h4>
                
                <label class="checkbox-label">
                    <input type="checkbox" id="enable-schedule-checkbox" 
                           onchange="toggleScheduleOptions()">
                    <span>Enable scheduled execution</span>
                </label>
                
                <div id="schedule-options" style="display: none; margin-top: 12px;">
                    <div class="form-group">
                        <label class="form-label">Schedule Type</label>
                        <select id="schedule-type" class="form-control" onchange="updateScheduleFields()">
                            <option value="cron">Cron Expression (Advanced)</option>
                            <option value="interval">Interval (Every X minutes)</option>
                            <option value="once">One-time (Specific date/time)</option>
                        </select>
                    </div>
                    
                    <!-- Cron Expression -->
                    <div id="cron-field" class="form-group" style="display: block;">
                        <label class="form-label">Cron Expression</label>
                        <input type="text" id="cron-expression" class="form-control" 
                               placeholder="0 9 * * *" value="0 9 * * *">
                        <small class="form-help-text">
                            Examples: <code>0 9 * * *</code> (daily at 9am), 
                            <code>0 */2 * * *</code> (every 2 hours)
                        </small>
                    </div>
                    
                    <!-- Interval -->
                    <div id="interval-field" class="form-group" style="display: none;">
                        <label class="form-label">Interval (minutes)</label>
                        <input type="number" id="interval-minutes" class="form-control" 
                               min="1" value="60" placeholder="60">
                    </div>
                    
                    <!-- One-time -->
                    <div id="once-field" class="form-group" style="display: none;">
                        <label class="form-label">Run At</label>
                        <input type="datetime-local" id="run-at-datetime" class="form-control">
                    </div>
                    
                    <div class="form-group">
                        <label class="form-label">Timezone</label>
                        <select id="schedule-timezone" class="form-control">
                            <option value="UTC">UTC</option>
                            <option value="America/New_York">America/New_York (EST/EDT)</option>
                            <option value="America/Los_Angeles">America/Los_Angeles (PST/PDT)</option>
                            <option value="Europe/London">Europe/London (GMT/BST)</option>
                            <option value="Asia/Tokyo">Asia/Tokyo (JST)</option>
                            <!-- Add more timezones as needed -->
                        </select>
                    </div>
                </div>
            </div>
        </div>
        
        <div class="modal-footer">
            <button class="btn-secondary" onclick="closePromoteModal()">
                <i class="fas fa-times"></i>
                Cancel
            </button>
            <button class="btn-success" onclick="confirmPromotion()">
                <i class="fas fa-rocket"></i>
                Activate Workflow
            </button>
        </div>
    </div>
</div>
```

**JavaScript for Promotion:**

```javascript
// Show promotion modal
function promoteWorkflow(slug) {
    const workflow = AutomationsSidebar.automations.find(a => a.slug === slug);
    if (!workflow) {
        showNotification('Workflow not found', 'error');
        return;
    }
    
    // Populate modal
    document.getElementById('promote-workflow-title').textContent = workflow.title || workflow.name;
    document.getElementById('promote-workflow-slug').textContent = slug;
    
    // Show modal
    document.getElementById('promote-workflow-modal').style.display = 'flex';
}

// Close modal
function closePromoteModal() {
    document.getElementById('promote-workflow-modal').style.display = 'none';
}

// Toggle schedule options
function toggleScheduleOptions() {
    const checkbox = document.getElementById('enable-schedule-checkbox');
    const options = document.getElementById('schedule-options');
    options.style.display = checkbox.checked ? 'block' : 'none';
}

// Update schedule fields based on type
function updateScheduleFields() {
    const type = document.getElementById('schedule-type').value;
    document.getElementById('cron-field').style.display = type === 'cron' ? 'block' : 'none';
    document.getElementById('interval-field').style.display = type === 'interval' ? 'block' : 'none';
    document.getElementById('once-field').style.display = type === 'once' ? 'block' : 'none';
}

// Confirm and execute promotion
async function confirmPromotion() {
    const slug = document.getElementById('promote-workflow-slug').textContent;
    const enableSchedule = document.getElementById('enable-schedule-checkbox').checked;
    
    const data = { slug };
    
    if (enableSchedule) {
        const scheduleType = document.getElementById('schedule-type').value;
        data.schedule = {
            type: scheduleType,
            timezone: document.getElementById('schedule-timezone').value
        };
        
        if (scheduleType === 'cron') {
            data.schedule.cron_expression = document.getElementById('cron-expression').value;
        } else if (scheduleType === 'interval') {
            data.schedule.interval_minutes = parseInt(document.getElementById('interval-minutes').value);
        } else if (scheduleType === 'once') {
            data.schedule.run_at = document.getElementById('run-at-datetime').value;
        }
    }
    
    try {
        const response = await fetch(`/api/automation/${slug}/promote`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${localStorage.getItem('authToken')}`
            },
            body: JSON.stringify(data)
        });
        
        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.message || 'Promotion failed');
        }
        
        const result = await response.json();
        
        showNotification(`Workflow activated successfully! ${enableSchedule ? 'Schedule enabled.' : ''}`, 'success');
        closePromoteModal();
        
        // Refresh workflow list
        if (typeof AutomationsSidebar !== 'undefined') {
            await AutomationsSidebar.loadAutomations();
        }
        
    } catch (error) {
        console.error('[PROMOTION] Error:', error);
        showNotification(`Activation failed: ${error.message}`, 'error');
    }
}
```

---

## 🔄 Data Flow Patterns

### Pattern 1: Loading Workflows (List View)

```javascript
// AutomationsSidebar.loadAutomations()
async loadAutomations() {
    try {
        const response = await fetch('/api/automation/list', {
            headers: { 'Authorization': `Bearer ${token}` }
        });
        
        const data = await response.json();
        this.automations = data.workflows; // Contains BOTH draft and production
        
        // Process each workflow to add UI-specific flags
        this.automations.forEach(workflow => {
            // Determine type
            workflow.is_production = workflow.workflow_state === 'production';
            workflow.is_draft = !workflow.is_production;
            
            // UI display properties
            workflow.borderColor = workflow.is_production ? '#10B981' : '#A855F7';
            workflow.stateLabel = workflow.is_production ? 'PRODUCTION READY' : 'DRAFT MODE';
            workflow.stateIcon = workflow.is_production ? 'fa-check-circle' : 'fa-drafting-compass';
            
            // Available actions
            workflow.canEdit = true; // All workflows can be edited (loads from visual_automations)
            workflow.canPromote = workflow.is_draft; // Only draft can be promoted
            workflow.canDemote = workflow.is_production; // Only production can be demoted
            workflow.canToggleEnabled = workflow.is_production; // Only production can be enabled/disabled
            workflow.canDelete = workflow.is_draft; // Only draft can be deleted (production must be demoted first)
        });
        
        this.automationsLoaded = true;
        this.renderAutomationList();
        
    } catch (error) {
        console.error('[AUTOMATIONS] Load failed:', error);
        showNotification('Failed to load workflows', 'error');
    }
}
```

---

### Pattern 2: Editing Workflow (Canvas)

```javascript
// Edit button clicked on workflow card
async function editWorkflow(slug) {
    // ALWAYS loads from visual_automations (via API JOIN)
    const workflow = AutomationsSidebar.automations.find(a => a.slug === slug);
    
    if (!workflow) {
        showNotification('Workflow not found', 'error');
        return;
    }
    
    // Show confirmation if production workflow
    if (workflow.is_production) {
        const confirmed = confirm(
            'This is a production workflow.\n\n' +
            'Changes will be saved as a draft and require reactivation.\n\n' +
            'Continue?'
        );
        
        if (!confirmed) return;
    }
    
    // Open automation canvas panel
    showPanelSlot('automations-slot');
    
    // Load workflow into canvas
    await window.automationCanvas.loadWorkflowFromList(workflow);
    
    // Update canvas header to show production warning (if applicable)
    if (workflow.is_production) {
        showProductionWarningBanner();
    }
}

function showProductionWarningBanner() {
    const banner = document.createElement('div');
    banner.className = 'production-warning-banner';
    banner.innerHTML = `
        <i class="fas fa-exclamation-triangle"></i>
        <span>Editing production workflow - changes require reactivation</span>
        <button onclick="this.parentElement.remove()">
            <i class="fas fa-times"></i>
        </button>
    `;
    document.querySelector('.canvas-container').prepend(banner);
}
```

---

### Pattern 3: Saving Changes

```javascript
// automation-workflows.js - saveDraft()
async saveDraft() {
    try {
        // Collect canvas data
        const workflowData = {
            slug: this.workflowSlug,
            title: this.workflowTitle,
            description: this.workflowDescription,
            category: this.workflowCategory,
            status: 'draft', // Always save as draft when editing
            ui_json: {
                shapes: this.shapes.map(s => ({
                    id: s.id,
                    type: s.type,
                    x: s.x,
                    y: s.y,
                    width: s.width,
                    height: s.height,
                    text: s.text,
                    color: s.color,
                    config: s.config || {}
                })),
                connections: this.connections.map(c => ({
                    id: c.id,
                    from: c.from,
                    to: c.to
                }))
            },
            execution_json: this.buildExecutionJson() // Extract tool calls
        };
        
        // Save to visual_automations table via API
        const response = await fetch(`/api/automation/save`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${token}`
            },
            body: JSON.stringify(workflowData)
        });
        
        if (!response.ok) throw new Error('Save failed');
        
        const result = await response.json();
        
        this.isDirty = false;
        this.lastSaved = new Date();
        
        showNotification('Draft saved successfully', 'success');
        
        // If this was a production workflow, show reactivation prompt
        if (this.wasProduction) {
            showReactivationPrompt();
        }
        
    } catch (error) {
        console.error('[AUTOMATION] Save failed:', error);
        showNotification('Failed to save draft', 'error');
    }
}

// Build execution JSON from canvas shapes
buildExecutionJson() {
    const execution = {
        trigger: null,
        actions: []
    };
    
    // Find trigger shape
    const triggerShape = this.shapes.find(s => s.type === 'hexagon' || s.config?.type === 'trigger');
    if (triggerShape && triggerShape.config) {
        execution.trigger = {
            type: triggerShape.config.trigger_type || 'manual',
            schedule_cron: triggerShape.config.schedule_cron,
            webhook_url: triggerShape.config.webhook_url,
            event_type: triggerShape.config.event_type
        };
    }
    
    // Extract actions in order (follow connections)
    const actionShapes = this.shapes.filter(s => 
        s.type === 'rectangle' && s.config?.tool
    );
    
    actionShapes.forEach(shape => {
        execution.actions.push({
            tool: shape.config.tool,
            parameters: shape.config.parameters || {},
            condition: shape.config.condition // For conditional execution
        });
    });
    
    return execution;
}
```

---

### Pattern 4: Toggle Enable/Disable (Production Only)

```javascript
// Toggle production workflow enabled state
async function toggleWorkflowEnabled(checkbox) {
    const workflowId = checkbox.dataset.workflowId;
    const slug = checkbox.dataset.slug;
    const enabled = checkbox.checked;
    
    try {
        const response = await fetch(`/api/automation/toggle/${workflowId}`, {
            method: 'PATCH',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${token}`
            },
            body: JSON.stringify({ enabled })
        });
        
        if (!response.ok) throw new Error('Toggle failed');
        
        // Update UI
        const label = checkbox.nextElementSibling;
        label.textContent = enabled ? 'ENABLED' : 'DISABLED';
        label.style.color = enabled ? 'var(--success)' : 'var(--text-muted)';
        
        showNotification(
            `Workflow ${enabled ? 'enabled' : 'disabled'} successfully`,
            'success'
        );
        
    } catch (error) {
        console.error('[TOGGLE] Error:', error);
        checkbox.checked = !enabled; // Revert checkbox
        showNotification('Failed to toggle workflow', 'error');
    }
}
```

---

## 📐 CSS Styling Guide

```css
/* Workflow Card Base Styles */
.workflow-card {
    position: relative;
    padding: 16px;
    margin-bottom: 12px;
    background: var(--bg-primary);
    border-radius: 8px;
    border-left: 4px solid var(--border-color);
    transition: all 0.2s ease;
    cursor: pointer;
}

.workflow-card:hover {
    background: var(--bg-secondary);
    transform: translateX(2px);
    box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

/* Draft vs Production Borders */
.workflow-card[data-workflow-type="draft"] {
    border-left-color: #A855F7; /* Purple */
}

.workflow-card[data-workflow-type="production"] {
    border-left-color: #10B981; /* Green */
}

/* Workflow Type Badge */
.workflow-status-badge {
    display: inline-flex;
    align-items: center;
    gap: 6px;
    padding: 4px 10px;
    border-radius: 4px;
    font-size: 11px;
    font-weight: 600;
    text-transform: uppercase;
}

.workflow-status-badge.draft-badge {
    background: rgba(168, 85, 247, 0.1);
    color: #A855F7;
}

.workflow-status-badge.production-badge {
    background: rgba(16, 185, 129, 0.1);
    color: #10B981;
}

/* Production Warning Banner (Canvas) */
.production-warning-banner {
    display: flex;
    align-items: center;
    gap: 12px;
    padding: 12px 16px;
    background: rgba(251, 191, 36, 0.1);
    border-left: 4px solid #F59E0B;
    color: #F59E0B;
    font-size: 13px;
    font-weight: 500;
    margin-bottom: 16px;
}

.production-warning-banner i {
    font-size: 18px;
}

.production-warning-banner button {
    margin-left: auto;
    background: transparent;
    border: none;
    color: #F59E0B;
    cursor: pointer;
    padding: 4px;
}

/* Enable/Disable Toggle */
.workflow-toggle-label {
    display: flex;
    align-items: center;
    gap: 8px;
    padding: 4px 8px;
    background: var(--bg-secondary);
    border-radius: 6px;
    cursor: pointer;
    user-select: none;
}

.workflow-enable-toggle {
    width: 16px;
    height: 16px;
    cursor: pointer;
}

.toggle-label-text {
    font-size: 11px;
    font-weight: 600;
    color: var(--text-secondary);
}

/* Modal Styles */
.modal {
    position: fixed;
    top: 0;
    left: 0;
    width: 100%;
    height: 100%;
    z-index: 10000;
    display: flex;
    align-items: center;
    justify-content: center;
}

.modal-overlay {
    position: absolute;
    top: 0;
    left: 0;
    width: 100%;
    height: 100%;
    background: rgba(0, 0, 0, 0.7);
    backdrop-filter: blur(4px);
}

.modal-content {
    position: relative;
    width: 90%;
    max-width: 600px;
    max-height: 80vh;
    overflow-y: auto;
    background: var(--bg-primary);
    border-radius: 12px;
    box-shadow: 0 20px 60px rgba(0, 0, 0, 0.3);
}

.modal-header {
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: 20px 24px;
    border-bottom: 1px solid var(--border-color);
}

.modal-header h2 {
    margin: 0;
    font-size: 20px;
    font-weight: 600;
    display: flex;
    align-items: center;
    gap: 12px;
}

.modal-close-btn {
    background: transparent;
    border: none;
    color: var(--text-muted);
    cursor: pointer;
    padding: 8px;
    border-radius: 4px;
    transition: all 0.2s;
}

.modal-close-btn:hover {
    background: var(--bg-secondary);
    color: var(--text-primary);
}

.modal-body {
    padding: 24px;
}

.modal-footer {
    display: flex;
    gap: 12px;
    justify-content: flex-end;
    padding: 16px 24px;
    border-top: 1px solid var(--border-color);
}

/* Promotion Specific Styles */
.promotion-info-box {
    background: rgba(59, 130, 246, 0.05);
    border: 1px solid rgba(59, 130, 246, 0.2);
    border-radius: 8px;
    padding: 16px;
    margin: 16px 0;
}

.promotion-info-box h4 {
    margin: 0 0 12px 0;
    font-size: 14px;
    font-weight: 600;
    color: var(--text-primary);
}

.promotion-checklist {
    list-style: none;
    padding: 0;
    margin: 0;
}

.promotion-checklist li {
    display: flex;
    align-items: center;
    gap: 10px;
    padding: 8px 0;
    font-size: 13px;
    color: var(--text-secondary);
}

.success-icon {
    color: var(--success);
}

.error-icon {
    color: var(--error);
}
```

---

## 🚀 Summary: UI Handling Strategy

### Key Principles

1. **Visual Distinction First**
   - Purple border = Draft (visual_automations only)
   - Green border = Production (exists in automation_workflows)
   - Clear labels and icons for status

2. **Context-Aware Actions**
   - Draft: Edit, Promote, Delete
   - Production: Enable/Disable toggle, View Stats, Demote

3. **Always Edit from Source**
   - Canvas loads from visual_automations (design source)
   - Even production workflows edited as drafts first
   - Reactivation required after editing production workflows

4. **Progressive Enhancement**
   - Start with basic list view (shows both types)
   - Add promotion modal for activation
   - Include scheduling configuration in promotion
   - Show execution stats for production workflows

5. **Parameter Configuration**
   - Dynamic form generation from tool schemas
   - Type-aware input rendering (text, number, boolean, array, object)
   - Validation before save/promotion
   - Help text and examples for complex parameters

---

**Last Updated**: November 28, 2024
**Version**: 1.0.0
**Status**: ✅ Complete UI Implementation Guide

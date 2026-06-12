# SYNERGY MILESTONE UI REDESIGN - CSS MAPPING PLAN

**Date:** November 19, 2025  
**Purpose:** Map existing CSS classes to new milestone structure

---

## 🎨 EXISTING CSS CLASSES (To Reuse)

### From `business-ai-platform-v2.html` (lines 2840-3100):

```css
/* ✅ KEEP - Card Container */
.synergy-card-collapsed {
    display: none;
    padding: var(--space-3);
    border-top: 1px solid var(--border-default);
    max-height: 0;
    overflow: hidden;
    transition: max-height 0.3s ease;
}

.synergy-session-item.expanded .synergy-card-collapsed {
    display: block;
    max-height: calc(100vh - 250px);
    overflow-y: auto;
}

/* ✅ KEEP - Section Structure */
.synergy-card-section {
    margin-bottom: var(--space-3);
}

.synergy-card-section:last-child {
    margin-bottom: 0;
}

.synergy-card-section-title {
    font-size: 12px;
    font-weight: 600;
    color: var(--text-muted);
    text-transform: uppercase;
    letter-spacing: 0.5px;
    margin-bottom: var(--space-2);
    display: flex;
    align-items: center;
    gap: 6px;
}

/* ✅ KEEP - Description */
.synergy-card-description {
    font-size: 13px;
    color: var(--text-secondary);
    line-height: 1.5;
    padding: var(--space-2);
    background: var(--bg-secondary);
    border-radius: 6px;
    max-height: 200px;
    overflow-y: auto;
}

/* ✅ KEEP - Card Meta (Assignees, Due Date) */
.synergy-item-meta .card-meta {
    margin-left: auto;
}
```

### From `synergy-milestone-styles.css` (existing):

```css
/* ✅ KEEP - Milestone Item Container */
.milestone-item {
    border: 1px solid var(--border-default);
    border-radius: 8px;
    overflow: hidden;
    transition: all 0.3s ease;
    background: var(--bg-primary);
}

.milestone-item:hover {
    box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08);
}

/* ✅ KEEP - Milestone Header */
.milestone-header {
    display: flex;
    align-items: center;
    gap: 12px;
    padding: 12px;
    background: linear-gradient(135deg, #3b82f6 0%, #2563eb 100%);
    color: white;
    cursor: pointer;
}

.milestone-item.completed .milestone-header {
    background: linear-gradient(135deg, #22c55e 0%, #16a34a 100%);
}

/* ✅ KEEP - Expand Button */
.milestone-expand-btn {
    background: none;
    border: none;
    color: white;
    cursor: pointer;
    padding: 4px;
    width: 24px;
    height: 24px;
    transition: transform 0.2s ease;
}
```

---

## 🔄 NEW CSS CLASSES NEEDED (To Create)

### Based on Your HTML Structure:

```html
<div class="synergy-card-collapsed">
    <!-- Card Meta (assignees, due date) -->
    <div class="card-meta">
        <span>👥 Assignees</span>
        <span>📅 Due Date</span>
    </div>
    
    <!-- Card Stats (SIMPLIFIED) -->
    <div class="card-stats">
        <span>💬 Messages: 12</span>
        <span>📄 Documents: 3</span>
        <span>🎯 Milestones: 2/4</span>
        <span>⏰ Est. 11 hrs remaining</span>
    </div>
```

**New Classes Needed:**

```css
/* 🆕 ADD - Card Stats Row */
.card-stats {
    display: flex;
    align-items: center;
    gap: 16px;
    padding: 12px;
    background: var(--bg-secondary);
    border-radius: 6px;
    margin-bottom: 16px;
    font-size: 12px;
    color: var(--text-secondary);
    flex-wrap: wrap;
}

.card-stats span {
    display: flex;
    align-items: center;
    gap: 4px;
}

/* 🆕 ADD - Milestone Number Badge */
.milestone-number {
    background: rgba(255, 255, 255, 0.2);
    padding: 4px 8px;
    border-radius: 4px;
    font-weight: 700;
    font-size: 12px;
    min-width: 32px;
    text-align: center;
}

/* 🆕 ADD - Milestone Progress Badge */
.milestone-progress {
    margin-left: auto;
    font-size: 12px;
    font-weight: 600;
    padding: 4px 8px;
    border-radius: 4px;
    background: rgba(255, 255, 255, 0.2);
}

/* 🆕 ADD - Milestone Due Date */
.milestone-due {
    font-size: 11px;
    padding: 4px 8px;
    border-radius: 4px;
    background: rgba(255, 255, 255, 0.15);
}

/* 🆕 ADD - AI Prediction Badge */
.milestone-prediction {
    font-size: 11px;
    padding: 4px 8px;
    border-radius: 4px;
    background: rgba(251, 191, 36, 0.2);
    color: #fbbf24;
    border: 1px solid rgba(251, 191, 36, 0.3);
}

/* 🆕 ADD - Milestone Description */
.milestone-description {
    padding: 8px 12px;
    font-size: 12px;
    color: rgba(255, 255, 255, 0.8);
    background: rgba(0, 0, 0, 0.1);
    border-bottom: 1px solid rgba(255, 255, 255, 0.1);
}

/* 🆕 ADD - Milestone Footer */
.milestone-footer {
    display: flex;
    align-items: center;
    gap: 12px;
    padding: 8px 12px;
    background: var(--bg-quaternary);
    border-top: 1px solid var(--border-default);
    font-size: 11px;
    color: var(--text-muted);
}

.milestone-footer button {
    margin-left: auto;
    padding: 4px 12px;
    background: var(--accent-primary);
    color: white;
    border: none;
    border-radius: 4px;
    cursor: pointer;
    font-size: 11px;
}

/* 🆕 ADD - Milestone Dependencies */
.milestone-depends {
    font-size: 11px;
    padding: 4px 8px;
    border-radius: 4px;
    background: rgba(255, 255, 255, 0.1);
    color: rgba(255, 255, 255, 0.7);
    display: flex;
    align-items: center;
    gap: 4px;
}

/* 🆕 ADD - Blocker Badge */
.blocker-badge {
    display: inline-flex;
    align-items: center;
    gap: 6px;
    padding: 6px 12px;
    background: #ef4444;
    color: white;
    border-radius: 4px;
    font-size: 11px;
    font-weight: 600;
    margin-top: 6px;
}

.task-item.blocked {
    opacity: 0.6;
    background: rgba(239, 68, 68, 0.05);
}
```

---

## 📋 MAPPING TABLE

| Your HTML Element | Existing CSS Class | Status | Notes |
|-------------------|-------------------|--------|-------|
| `<div class="synergy-card-collapsed">` | ✅ `.synergy-card-collapsed` | KEEP | Already has expand/collapse logic |
| `<div class="card-meta">` | ⚠️ `.synergy-item-meta .card-meta` | MODIFY | Need to add to card body (not just header) |
| `<div class="card-stats">` | 🆕 NEW | CREATE | New simplified stats row |
| `<div class="synergy-card-section">` | ✅ `.synergy-card-section` | KEEP | Perfect for all sections |
| `<div class="synergy-card-section-title">` | ✅ `.synergy-card-section-title` | KEEP | Already styled with emojis |
| `<div class="synergy-card-description">` | ✅ `.synergy-card-description` | KEEP | Scrollable description |
| `<div class="milestone-item">` | ✅ `.milestone-item` | KEEP | Container with hover effect |
| `<div class="milestone-header">` | ✅ `.milestone-header` | KEEP | Gradient header with badges |
| `<span class="milestone-number">` | 🆕 NEW | CREATE | M1, M2, M3 badges |
| `<span class="milestone-progress">` | 🆕 NEW | CREATE | Percentage badge |
| `<span class="milestone-due">` | 🆕 NEW | CREATE | Due date badge |
| `<span class="milestone-prediction">` | 🆕 NEW | CREATE | AI prediction badge |
| `<div class="milestone-description">` | 🆕 NEW | CREATE | Inside milestone header area |
| `<div class="milestone-tasks">` | ✅ `.milestone-body` (rename) | KEEP | Collapsible task container |
| `<div class="task-item">` | ✅ `.task-item` | KEEP | Task row styling |
| `<span class="task-number">` | ✅ `.task-number` | KEEP | T1.1, T1.2 badges |
| `<div class="task-subtasks">` | ✅ `.task-subtasks` | KEEP | Indented subtask container |
| `<div class="subtask-item">` | ✅ `.subtask-item` | KEEP | Subtask row |
| `<span class="subtask-number">` | ✅ `.subtask-number` | KEEP | S1.2.1 badges |
| `<span class="blocker-badge">` | 🆕 NEW | CREATE | Red blocker indicator |
| `<div class="milestone-footer">` | 🆕 NEW | CREATE | Time tracking + comments |

---

## 🎯 IMPLEMENTATION PLAN

### Phase 1: Update Existing CSS File
**File:** `UI/external/styles/synergy-milestone-styles.css`

**Add these new classes:**
1. `.card-stats` (stats row at top of card)
2. `.milestone-number` (M# badge)
3. `.milestone-progress` (percentage badge)
4. `.milestone-due` (due date badge)
5. `.milestone-prediction` (AI prediction badge)
6. `.milestone-description` (description under header)
7. `.milestone-footer` (time tracking row)
8. `.milestone-depends` (dependency indicator)
9. `.blocker-badge` (blocked task indicator)

### Phase 2: Update Renderer
**File:** `UI/external/modules/synergy-milestone-renderer.js`

**Update methods to generate new HTML structure:**
```javascript
renderMilestoneHeader(milestone) {
    return `
        <div class="milestone-header" onclick="toggleMilestone('${milestone.milestone_id}')">
            <button class="milestone-expand-btn">▼</button>
            <span class="milestone-number">M${milestone.milestone_number}</span>
            <input type="checkbox" ${milestone.completed ? 'checked' : ''} />
            <span class="milestone-name">${milestone.milestone_name}</span>
            <span class="milestone-progress">${this.calculateProgress(milestone)}%</span>
            ${milestone.due_date ? `<span class="milestone-due">📅 ${formatDate(milestone.due_date)}</span>` : ''}
            ${milestone.prediction ? `<span class="milestone-prediction">📅 Est. ${milestone.prediction}</span>` : ''}
        </div>
    `;
}
```

### Phase 3: Add Card Stats Section
**File:** `UI/external/modules/synergy-card-renderer.js`

**Add new method:**
```javascript
renderCardStats(session) {
    const messageCount = session.message_count || 0;
    const docCount = (session.documents ? JSON.parse(session.documents).length : 0);
    const milestoneStats = this.getMilestoneStats(session.milestones);
    const estHours = this.calculateRemainingHours(session.milestones);
    
    return `
        <div class="card-stats">
            <span>💬 Messages: ${messageCount}</span>
            <span>📄 Documents: ${docCount}</span>
            <span>🎯 Milestones: ${milestoneStats.completed}/${milestoneStats.total}</span>
            <span>⏰ Est. ${estHours} hrs remaining</span>
        </div>
    `;
}
```

---

## 🚀 TESTING CHECKLIST

Before deploying:
- [ ] Card stats row displays correctly at top
- [ ] Milestone badges (M#) render properly
- [ ] Progress percentages calculate correctly
- [ ] Due date badges show formatted dates
- [ ] AI prediction badges appear when available
- [ ] Blocker badges display on blocked tasks
- [ ] Milestone footer shows time tracking
- [ ] Expand/collapse animations work smoothly
- [ ] Hover effects on all interactive elements
- [ ] Responsive design on mobile
- [ ] Dark mode colors work properly

---

## 📝 SUMMARY

**Reusing from existing:** 75% of CSS classes  
**New classes needed:** 9 classes (25%)

**Key advantages:**
- ✅ Consistent with existing Synergy UI patterns
- ✅ Uses same CSS variables and color scheme
- ✅ Minimal changes to working code
- ✅ Maintains expand/collapse logic
- ✅ Responsive design already built-in

**Next step:** Update `synergy-milestone-styles.css` with new classes, then modify renderers to use new structure.

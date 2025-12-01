# InHouse Kanban - V9 Card Structure Restoration

**Date**: December 1, 2025  
**Status**: Ready for Implementation  
**Files**: inhouse-kanban-V4-COMPLETE.js

---

## Summary of Changes

Restoring V9's cleaner card layout with comprehensive content sections while maintaining V4's advanced features (mute functionality, color toggles, advanced settings).

### Key Improvements:
1. ✅ **Stage Time Section** - Color-coded duration display (missing in V4)
2. ✅ **Status Badge** - DELAYED/AT_RISK/ON_TRACK visual indicators  
3. ✅ **Cleaner Layout** - Better spacing and visual hierarchy
4. ✅ **Darker Modal Theme** - Professional gray/blue color scheme (not bright blue)
5. ✅ **Keep V4 Features** - Mute functionality, color toggles, advanced settings

---

## Data Field Mapping (V9 → V4)

| V9 Field | V4 Equivalent | Usage |
|----------|---------------|-------|
| `job.TicketID` | `job.ticket_number` | Ticket number |
| `job.ShortJobDesc` | `job.job_name` | Job description |
| `job.ClientName` | `job.client_name` | Client name |
| `job.Cost` | `job.cost` or calculated | Job cost |
| `job.DaysInSystem` | Calculate from `created_at` | Total days |
| `job.WIPStatus` | `job.status` | Status badge |
| `job.DaysInCurrentStage` | `daysInStage` calculation | Stage duration |
| `job.CurrentStageName` | `stage.name` | Current stage |

---

## Card Structure Comparison

### V4 CURRENT (Simplified):
```
┌──────────────────────────────┐
│ [BANNER if muted/overdue]   │
│ ⚠️ #12345    [Mute Button]  │
│ ABC Corporation              │
│ Business Cards - Premium     │
│ 📅 Due: Dec 15  🕐 5d       │
│ [View] [Notify] [Move]      │
└──────────────────────────────┘
```

### V9 TARGET (Comprehensive):
```
┌──────────────────────────────┐
│ [BANNER: "Overdue!"]        │ ← Conditional alert
├──────────────────────────────┤
│ ⚠️                [Mute]    │ ← Priority icon + mute
├──────────────────────────────┤
│ Business Cards - Premium     │ ← Title (job description)
├──────────────────────────────┤
│ 🏢 ABC Corporation          │ ← Client name
│ [AT_RISK] 15d in system     │ ← Status badge + total days
├──────────────────────────────┤
│ 🕐 3d in Quote              │ ← **STAGE TIME** (color-coded!)
├──────────────────────────────┤
│ #12345    $1,450.00         │ ← Ticket # + Cost
└──────────────────────────────┘
```

---

## Implementation Code

### 1. Updated renderJobCard Method

Replace the current `renderJobCard(job, stage)` method (lines 1203-1330) with:

```javascript
renderJobCard(job, stage) {
    const isMuted = this.isCardMuted(job.id);
    const muteSettings = this.getMuteSettings(job.id);

    // Calculate styling
    const borderStyle = this.getCardBorderStyle(job, muteSettings);
    const bgStyle = this.getCardBackgroundStyle(job, muteSettings);
    const bannerHtml = this.getCardBanner(job, muteSettings);

    const cardId = `job-card-${job.id}`;
    const priorityIcon = this.getPriorityIcon(job.priority);
    const daysInStage = this.calculateDaysInStage(job);
    
    // Calculate stage time info with color coding
    const stageTimeInfo = this.calculateStageTimeInfo(job, stage, daysInStage);
    
    // Calculate total days in system
    const daysInSystem = this.calculateDaysInSystem(job);
    
    // Get status badge
    const statusClass = this.getStatusBadgeClass(job.status);
    const statusText = (job.status || 'ACTIVE').toUpperCase();

    return `
        <div 
            class="kanban-card ${isMuted ? 'muted-card' : ''}" 
            id="${cardId}"
            data-job-id="${job.id}" 
            draggable="true"
            onclick="window.currentKanbanModule.openJobDetails(${job.id})"
            style="
                background: ${bgStyle};
                border: ${borderStyle};
                opacity: ${isMuted ? '0.5' : '1'};
                cursor: pointer;
            "
        >
            ${bannerHtml}
            
            <div class="card-header">
                <div class="card-priority">
                    ${priorityIcon}
                </div>
                <button 
                    class="card-mute-btn" 
                    onclick="event.stopPropagation(); window.currentKanbanModule.toggleCardMute(event, ${job.id})"
                    title="${isMuted ? 'Unmute card' : 'Mute card'}"
                >
                    <i class="fas ${isMuted ? 'fa-bell-slash' : 'fa-bell'}"></i>
                </button>
            </div>
            
            <div class="card-title">${this.escapeHtml(job.job_name || 'No description')}</div>
            
            <div class="card-meta">
                <div class="card-project">
                    <i class="fas fa-building"></i>
                    ${this.escapeHtml(job.client_name || 'Unknown Client')}
                </div>
                <div class="card-status-row">
                    <span class="status-badge ${statusClass}">
                        ${statusText}
                    </span>
                    <span class="card-time">${daysInSystem}d in system</span>
                </div>
            </div>
            
            <div class="card-stage-time ${stageTimeInfo.cssClass}">
                <i class="fas fa-clock"></i>
                <span class="stage-time-text">${stageTimeInfo.display}</span>
            </div>
            
            <div class="card-footer">
                <div class="card-tags">
                    <span class="card-tag">
                        <i class="fas fa-hashtag"></i> ${job.ticket_number || 'N/A'}
                    </span>
                    ${job.cost ? `
                        <span class="card-tag">
                            <i class="fas fa-dollar-sign"></i> ${this.formatCurrency(job.cost)}
                        </span>
                    ` : ''}
                </div>
            </div>
        </div>
    `;
}
```

### 2. New Helper Methods

Add these methods after the existing helper methods:

```javascript
/**
 * Calculate total days in system
 */
calculateDaysInSystem(job) {
    if (!job.created_at) return 0;
    const created = new Date(job.created_at);
    const now = new Date();
    const diffTime = Math.abs(now - created);
    const diffDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24));
    return diffDays;
}

/**
 * Calculate stage time info with color coding
 */
calculateStageTimeInfo(job, stage, daysInStage) {
    const stageName = stage?.name || 'this stage';
    let cssClass = 'stage-normal';
    let display = `${daysInStage}d in ${stageName}`;

    // Color coding based on duration
    if (daysInStage > 7) {
        cssClass = 'stage-overdue';  // Red - over 7 days
    } else if (daysInStage > 3) {
        cssClass = 'stage-warning';   // Yellow - 4-7 days
    }
    // else 'stage-normal' (gray - 0-3 days)

    return { display, cssClass };
}

/**
 * Get status badge class
 */
getStatusBadgeClass(status) {
    if (!status) return 'status-active';
    const statusLower = status.toLowerCase();
    if (statusLower.includes('delayed')) return 'status-delayed';
    if (statusLower.includes('risk') || statusLower.includes('warning')) return 'status-warning';
    if (statusLower.includes('on track') || statusLower.includes('complete')) return 'status-success';
    return 'status-active';
}
```

### 3. Updated CSS Classes

Add these new CSS classes in the `getStyles()` method:

```css
/* Card Structure - V9 Style */
#tab-inhouse-kanban.active .kanban-card {
    background: #0d1117;
    border: 1px solid #30363d;
    border-radius: 8px;
    padding: 12px;
    margin-bottom: 12px;
    cursor: pointer;
    transition: all 0.2s ease;
}

#tab-inhouse-kanban.active .kanban-card:hover {
    transform: translateY(-2px);
    box-shadow: 0 4px 12px rgba(88, 166, 255, 0.3);
}

/* Card Header */
#tab-inhouse-kanban.active .card-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 8px;
}

#tab-inhouse-kanban.active .card-priority {
    font-size: 16px;
    display: flex;
    align-items: center;
}

#tab-inhouse-kanban.active .card-mute-btn {
    background: transparent;
    border: none;
    color: #6e7681;
    cursor: pointer;
    padding: 4px;
    font-size: 14px;
    transition: color 0.2s;
}

#tab-inhouse-kanban.active .card-mute-btn:hover {
    color: #f85149;
}

#tab-inhouse-kanban.active .muted-card .card-mute-btn {
    color: #f85149;
}

/* Card Title */
#tab-inhouse-kanban.active .card-title {
    font-size: 13px;
    font-weight: 600;
    color: #e6edf3;
    margin-bottom: 8px;
    line-height: 1.4;
}

/* Card Meta Section */
#tab-inhouse-kanban.active .card-meta {
    display: flex;
    flex-direction: column;
    gap: 6px;
    margin-top: 8px;
    padding-top: 8px;
    border-top: 1px solid #30363d;
}

#tab-inhouse-kanban.active .card-project {
    font-size: 12px;
    color: #8b949e;
    display: flex;
    align-items: center;
    gap: 6px;
}

#tab-inhouse-kanban.active .card-status-row {
    display: flex;
    align-items: center;
    justify-content: space-between;
    gap: 8px;
}

/* Status Badges */
#tab-inhouse-kanban.active .status-badge {
    padding: 2px 6px;
    border-radius: 3px;
    font-size: 9px;
    font-weight: 700;
    text-transform: uppercase;
}

#tab-inhouse-kanban.active .status-active {
    background: rgba(87, 171, 90, 0.2);
    color: #57ab5a;
}

#tab-inhouse-kanban.active .status-success {
    background: rgba(16, 185, 129, 0.2);
    color: #10b981;
}

#tab-inhouse-kanban.active .status-delayed {
    background: rgba(248, 81, 73, 0.2);
    color: #f85149;
}

#tab-inhouse-kanban.active .status-warning {
    background: rgba(251, 191, 36, 0.2);
    color: #fbbf24;
}

#tab-inhouse-kanban.active .card-time {
    font-size: 10px;
    color: #6e7681;
}

/* Stage Time Section - KEY NEW FEATURE */
#tab-inhouse-kanban.active .card-stage-time {
    display: flex;
    align-items: center;
    gap: 6px;
    font-size: 11px;
    margin-top: 8px;
    padding-top: 8px;
    border-top: 1px solid #30363d;
}

#tab-inhouse-kanban.active .stage-normal {
    color: #8b949e;
}

#tab-inhouse-kanban.active .stage-warning {
    color: #fbbf24;
    font-weight: 600;
}

#tab-inhouse-kanban.active .stage-overdue {
    color: #f85149;
    font-weight: 700;
}

#tab-inhouse-kanban.active .stage-time-text {
    flex: 1;
}

/* Card Footer */
#tab-inhouse-kanban.active .card-footer {
    margin-top: 8px;
}

#tab-inhouse-kanban.active .card-tags {
    display: flex;
    gap: 8px;
    flex-wrap: wrap;
}

#tab-inhouse-kanban.active .card-tag {
    font-size: 11px;
    padding: 3px 8px;
    background: #161b22;
    color: #8b949e;
    border-radius: 4px;
    display: flex;
    align-items: center;
    gap: 4px;
}

#tab-inhouse-kanban.active .card-tag i {
    font-size: 9px;
}

/* MODAL STYLING - DARKER THEME */
.modal-overlay {
    position: fixed;
    top: 0;
    left: 0;
    width: 100%;
    height: 100%;
    background: rgba(0, 0, 0, 0.85);
    z-index: 10000;
    display: flex;
    justify-content: center;
    align-items: center;
    backdrop-filter: blur(4px);
}

.modal-content {
    background: #0d1117;
    border-radius: 12px;
    width: 90%;
    max-width: 1000px;
    max-height: 85vh;
    display: flex;
    flex-direction: column;
    border: 1px solid #30363d;
    box-shadow: 0 20px 60px rgba(0, 0, 0, 0.7);
}

.modal-header {
    background: linear-gradient(135deg, #21262d 0%, #161b22 100%);
    border-bottom: 2px solid #30363d;
    color: #e6edf3;
    padding: 20px 24px;
    border-radius: 12px 12px 0 0;
    display: flex;
    justify-content: space-between;
    align-items: center;
    flex-shrink: 0;
    user-select: none;
    cursor: move;
}

.modal-header h3 {
    margin: 0;
    font-size: 16px;
    font-weight: 700;
    display: flex;
    align-items: center;
    gap: 12px;
    color: #e6edf3;
}

.modal-header h3 i {
    font-size: 16px;
    color: #58a6ff;
}

.modal-close {
    background: transparent;
    border: none;
    color: #8b949e;
    font-size: 20px;
    cursor: pointer;
    padding: 8px;
    width: 36px;
    height: 36px;
    border-radius: 6px;
    display: flex;
    align-items: center;
    justify-content: center;
    transition: all 0.2s ease;
}

.modal-close:hover {
    background: rgba(248, 81, 73, 0.2);
    color: #f85149;
}

.modal-body {
    flex: 1;
    overflow-y: auto;
    overflow-x: hidden;
    padding: 24px;
    background: #0d1117;
}

.modal-section {
    margin-bottom: 24px;
}

.modal-section:last-child {
    margin-bottom: 0;
}

.modal-section-title {
    font-size: 13px;
    font-weight: 700;
    color: #58a6ff;
    margin-bottom: 14px;
    display: flex;
    align-items: center;
    gap: 10px;
    text-transform: uppercase;
    letter-spacing: 0.8px;
    padding-bottom: 8px;
    border-bottom: 2px solid #30363d;
}

.modal-section-title i {
    color: #58a6ff;
    font-size: 14px;
}

.modal-section-content {
    background: #161b22;
    border: 1px solid #30363d;
    border-radius: 8px;
    padding: 16px;
}

.detail-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
    gap: 12px;
}

.detail-item {
    display: flex;
    flex-direction: column;
    gap: 4px;
}

.detail-label {
    font-size: 10px;
    font-weight: 600;
    color: #58a6ff;
    text-transform: uppercase;
    letter-spacing: 0.5px;
}

.detail-value {
    font-size: 14px;
    color: #e6edf3;
    font-weight: 600;
}

.modal-footer {
    background: #0d1117;
    border-top: 1px solid #30363d;
    padding: 16px 24px;
    display: flex;
    justify-content: flex-end;
    gap: 12px;
    flex-shrink: 0;
}
```

---

## Testing Checklist

After implementation:

1. ✅ **Card Rendering**
   - Cards show all 6 sections (banner, header, title, meta, stage time, footer)
   - Stage time section visible with color coding
   - Status badge displays correctly
   - Days in system calculates accurately

2. ✅ **Color Coding**
   - 0-3 days in stage → Gray (stage-normal)
   - 4-7 days in stage → Yellow (stage-warning)
   - 8+ days in stage → Red (stage-overdue)

3. ✅ **Mute Functionality**
   - Mute button still works (V4 feature preserved)
   - Muted cards show dimmed appearance
   - Mute icon changes when toggled

4. ✅ **Modal Theme**
   - Darker gray/black background (not bright blue)
   - Section titles in cyan (#58a6ff)
   - Detail labels in cyan
   - Detail values in white
   - Close button hover effect (red)

5. ✅ **Advanced Features**
   - Color toggles still functional
   - Advanced settings collapsible
   - Custom color overrides work
   - All V4 features preserved

---

## Before vs After

### BEFORE (V4 - Simplified):
- ❌ No stage time section
- ❌ No status badge visual
- ❌ No "days in system" display
- ❌ Bright blue modal theme
- ✅ Mute functionality
- ✅ Color toggles

### AFTER (V9 Restoration - Comprehensive):
- ✅ Stage time section with color coding
- ✅ Status badge (DELAYED/AT_RISK/ACTIVE)
- ✅ Days in system counter
- ✅ Darker professional modal theme
- ✅ Mute functionality (preserved)
- ✅ Color toggles (preserved)
- ✅ Cleaner visual hierarchy
- ✅ Better content organization

---

## File Locations

- **Main File**: `c:\Users\gpoli\GIT\AI_agents\UI\modules_external\inhouse-kanban\inhouse-kanban-V4-COMPLETE.js`
- **V9 Reference**: `c:\Users\gpoli\GIT\AI_agents\TEMP_V9_analysis.js`
- **Analysis Doc**: `c:\Users\gpoli\GIT\AI_agents\UI\modules_external\inhouse-kanban\V9_CARD_STRUCTURE_ANALYSIS.md`

---

## Next Steps

1. Implement `renderJobCard` method replacement
2. Add new helper methods (`calculateDaysInSystem`, `calculateStageTimeInfo`, `getStatusBadgeClass`)
3. Add new CSS classes for stage time section and status badges
4. Update modal CSS for darker theme
5. Test with sample data
6. Verify all V4 features still work
7. Hard refresh browser (Ctrl+Shift+F5)

---

**Status**: Ready for implementation  
**Approval**: Awaiting user confirmation  
**Implementation Time**: ~15 minutes

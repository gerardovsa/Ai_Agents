# 🎨 Supabase UI Integration Guide

## What Was Created

I've built a complete UI layer (`kanban-supabase-ui.js`) with these components:

✅ **Enhanced Kanban Cards** - Time metrics badges on cards  
✅ **Job Details Modal** - Comprehensive job view with all Supabase data  
✅ **Production Log Viewer** - View and add log entries  
✅ **Time Tracking Controls** - Start/stop timer buttons  
✅ **Performance Metrics Form** - Record hours, quality, costs  
✅ **Analytics Tab Content** - Sidebar analytics integration  

---

## Quick Integration (5 Steps)

### Step 1: Load Scripts in HTML

Add these scripts to your main HTML file (after existing Kanban scripts):

```html
<!-- Supabase Integration -->
<script src="UI/external/modules/inhouse-kanban/kanban-supabase-integration.js"></script>
<script src="UI/external/modules/inhouse-kanban/kanban-supabase-ui.js"></script>
```

### Step 2: Initialize UI on Module Load

In `inhouse-kanban.js`, add initialization:

```javascript
class InhouseKanbanModule extends BaseModule {
    async init() {
        // Existing initialization...
        
        // Initialize Supabase UI (NEW!)
        if (window.kanbanSupabaseUI) {
            await window.kanbanSupabaseUI.initialize();
            console.log('✅ Supabase UI ready');
        }
        
        // Load jobs and render board...
    }
}
```

### Step 3: Enhance Cards with Time Metrics

In `inhouse-kanban.js`, after rendering each card:

```javascript
async renderJobCard(job) {
    // Existing card rendering...
    const cardHtml = `<div class="kanban-card" data-ticket-id="${job.TicketID}">...</div>`;
    
    // Create card element
    const cardElement = document.createElement('div');
    cardElement.innerHTML = cardHtml;
    const card = cardElement.firstChild;
    
    // Enhance with Supabase metrics (NEW!)
    if (window.kanbanSupabaseUI) {
        await window.kanbanSupabaseUI.enhanceCard(card, job.TicketID);
    }
    
    return card;
}
```

### Step 4: Add "View Details" Button to Cards

Update card template to include details button:

```javascript
const cardHtml = `
    <div class="kanban-card" data-ticket-id="${job.TicketID}">
        <!-- Existing card content -->
        
        <!-- NEW: Details Button -->
        <button class="card-details-btn" onclick="window.kanbanSupabaseUI.showJobDetailsModal(${job.TicketID}, ${JSON.stringify(job).replace(/"/g, '&quot;')})">
            <i class="fas fa-info-circle"></i> Details
        </button>
    </div>
`;
```

### Step 5: Integrate Analytics Tab

In the sidebar HTML or initialization:

```javascript
// When Analytics tab is clicked
document.querySelector('[data-tab="analytics-view"]').addEventListener('click', () => {
    const analyticsContainer = document.getElementById('analytics-view');
    window.kanbanSupabaseUI.renderAnalyticsTab(analyticsContainer);
});
```

---

## Complete Integration Example

Here's a complete example of integrating into `inhouse-kanban.js`:

```javascript
class InhouseKanbanModule extends BaseModule {
    async init() {
        console.log('🔧 Initializing InHouse Kanban...');
        
        // Initialize Supabase components
        await this.initializeSupabase();
        
        // Load jobs from SQL Server
        this.jobs = await this.fetchJobs();
        
        // Batch sync to Supabase
        if (this.supabaseEnabled) {
            await window.KanbanSupabaseIntegration.batchSyncJobs(this.jobs);
            console.log(`✅ ${this.jobs.length} jobs synced to Supabase`);
        }
        
        // Render Kanban board
        this.renderBoard();
    }
    
    async initializeSupabase() {
        // Initialize data layer
        if (window.KanbanSupabaseIntegration) {
            const ready = await window.KanbanSupabaseIntegration.initialize();
            this.supabaseEnabled = ready;
        }
        
        // Initialize UI layer
        if (window.kanbanSupabaseUI) {
            await window.kanbanSupabaseUI.initialize();
            console.log('✅ Supabase UI ready');
        }
    }
    
    async renderJobCard(job) {
        const cardHtml = `
            <div class="kanban-card" 
                 data-ticket-id="${job.TicketID}"
                 data-stage-id="${job.StageID}"
                 draggable="true">
                
                <!-- Card Header -->
                <div class="card-header">
                    <div class="card-priority" style="background: ${job.PriorityColorHex};">
                        ${job.Priority}
                    </div>
                    <div class="card-banner">
                        ${job.TicketID} - ${job.OrderID}
                    </div>
                </div>
                
                <!-- Card Meta -->
                <div class="card-meta">
                    <div class="card-project">${job.ClientName}</div>
                    <div class="card-description">${job.ShortJobDesc}</div>
                    ${job.Qty ? `<div class="card-quantity">Qty: ${job.Qty}</div>` : ''}
                </div>
                
                <!-- Card Stage Time -->
                <div class="card-stage-time">
                    <span class="status-badge status-${job.UrgencyLevel}">${job.PriorityLabel}</span>
                    <span class="card-time-info">
                        <i class="fas fa-calendar-day"></i>
                        <span class="stage-time-text">${job.DaysInSystem} days</span>
                    </span>
                </div>
                
                <!-- NEW: Details Button -->
                <button class="card-details-btn" onclick="event.stopPropagation(); window.kanbanSupabaseUI.showJobDetailsModal(${job.TicketID}, ${JSON.stringify(job).replace(/"/g, '&quot;')})">
                    <i class="fas fa-info-circle"></i> View Details
                </button>
            </div>
        `;
        
        // Create card element
        const tempDiv = document.createElement('div');
        tempDiv.innerHTML = cardHtml.trim();
        const cardElement = tempDiv.firstChild;
        
        // Enhance with Supabase metrics
        if (this.supabaseEnabled && window.kanbanSupabaseUI) {
            await window.kanbanSupabaseUI.enhanceCard(cardElement, job.TicketID);
        }
        
        // Add drag event listeners
        this.attachCardDragEvents(cardElement);
        
        return cardElement;
    }
    
    async handleDrop(event) {
        event.preventDefault();
        
        const ticketId = parseInt(event.dataTransfer.getData('ticketId'));
        const fromStageId = parseInt(event.dataTransfer.getData('stageId'));
        const toStageId = parseInt(event.target.dataset.stageId);
        
        if (fromStageId === toStageId) return;
        
        // Record stage transition in Supabase (NEW!)
        if (this.supabaseEnabled) {
            const result = await window.KanbanSupabaseIntegration.recordStageTransition(
                ticketId, fromStageId, toStageId
            );
            
            if (result && result.success) {
                console.log(`✅ Stage transition: ${ticketId} (${fromStageId} → ${toStageId})`);
                console.log(`   Time in previous stage: ${result.transition_time_hours?.toFixed(2) || 'N/A'}h`);
            }
        }
        
        // Existing drop logic (update UI, etc.)
        this.updateCardStage(ticketId, toStageId);
    }
}
```

---

## UI Components Reference

### 1. Enhanced Card Badge

Automatically adds time metrics badge to cards:

```
┌─────────────────────────────────────┐
│ Card Content                        │
│ ...                                 │
├─────────────────────────────────────┤
│ ⏳ 4.5h | 🕐 12.8h | 🔄 3          │ ← NEW: Metrics badge
└─────────────────────────────────────┘
```

### 2. Job Details Modal

Comprehensive modal with 5 sections:

```
╔═══════════════════════════════════════╗
║ Job Details - 12345            [X]    ║
╠═══════════════════════════════════════╣
║ 📋 Job Information                    ║
║   Client, Order ID, Stage, etc.       ║
║                                       ║
║ ⏱️ Time Metrics                       ║
║   Current Stage: 4.5h                 ║
║   Total Time: 12.8h                   ║
║   Transitions: 3                      ║
║                                       ║
║ 📝 Production Log         [+ Add]     ║
║   • 2024-11-29 10:30 - Customer call  ║
║   • 2024-11-29 09:15 - Started work   ║
║                                       ║
║ ⏱️ Time Tracking                      ║
║   [▶ Start Timer] or [⏹ Stop Timer]  ║
║                                       ║
║ 📊 Performance Metrics                ║
║   Estimated Hours: [ 3.0 ]            ║
║   Actual Hours: [ 2.5 ]               ║
║   Quality Score: [ 95 ]               ║
║   [💾 Save Metrics]                   ║
╚═══════════════════════════════════════╝
```

### 3. Production Log Form

Add entries directly in modal:

```javascript
// Show form
window.kanbanSupabaseUI.showAddLogEntryForm(12345);

// Form fields:
// - Entry Type: note, wastage, delay, etc.
// - Description: textarea
// - [Add Entry] [Cancel]
```

### 4. Time Tracking Controls

Start/stop timer with one click:

```javascript
// Start timer
window.kanbanSupabaseUI.startTimer(12345);

// Stop timer
window.kanbanSupabaseUI.stopTimer(12345);
// Returns: { duration_hours: 2.5, duration_minutes: 150 }
```

### 5. Analytics Tab

Render in sidebar analytics tab:

```javascript
const analyticsContainer = document.getElementById('analytics-view');
window.kanbanSupabaseUI.renderAnalyticsTab(analyticsContainer);
```

---

## CSS Customization

All styles are injected automatically. To customize:

```javascript
// Modify in kanban-supabase-ui.js _injectModalStyles() method

// Color scheme
--primary-color: #3b82f6;
--success-color: #10b981;
--danger-color: #ef4444;
--warning-color: #f97316;

// Backgrounds
--modal-bg: #161b22;
--card-bg: #0d1117;
--border-color: #30363d;

// Text colors
--text-primary: #f3f4f6;
--text-secondary: #9ca3af;
```

---

## API Methods Available

### Card Enhancement
```javascript
await window.kanbanSupabaseUI.enhanceCard(cardElement, ticketId);
```

### Job Details Modal
```javascript
await window.kanbanSupabaseUI.showJobDetailsModal(ticketId, jobObject);
```

### Production Log
```javascript
// Show add form
await window.kanbanSupabaseUI.showAddLogEntryForm(ticketId);

// Submit entry
await window.kanbanSupabaseUI.submitLogEntry(ticketId);
```

### Time Tracking
```javascript
// Start timer
window.kanbanSupabaseUI.startTimer(ticketId);

// Stop timer
await window.kanbanSupabaseUI.stopTimer(ticketId);
```

### Performance Metrics
```javascript
await window.kanbanSupabaseUI.submitPerformance(ticketId);
```

### Analytics Tab
```javascript
await window.kanbanSupabaseUI.renderAnalyticsTab(containerElement);
```

---

## Testing the UI

### 1. Test Card Enhancement

```javascript
// In browser console
const card = document.querySelector('.kanban-card');
const ticketId = card.dataset.ticketId;
await window.kanbanSupabaseUI.enhanceCard(card, ticketId);
```

**Expected:** Time metrics badge appears below card content.

### 2. Test Job Details Modal

```javascript
// In browser console
const job = {
    TicketID: 12345,
    ClientName: 'Test Corp',
    OrderID: 'ORD-001',
    ShortJobDesc: 'Test Job',
    StageID: 2,
    StageDescription: 'In Production',
    Priority: 5,
    DaysInSystem: 3
};

await window.kanbanSupabaseUI.showJobDetailsModal(12345, job);
```

**Expected:** Modal opens with all sections (Job Info, Time Metrics, Production Log, Time Tracking, Performance).

### 3. Test Time Tracking

```javascript
// Start timer
window.kanbanSupabaseUI.startTimer(12345);
// Wait a few seconds
// Stop timer
await window.kanbanSupabaseUI.stopTimer(12345);
```

**Expected:** Console shows duration, production log entry created.

### 4. Test Production Log

```javascript
await window.kanbanSupabaseUI.showAddLogEntryForm(12345);
// Fill form and submit
await window.kanbanSupabaseUI.submitLogEntry(12345);
```

**Expected:** Entry appears in production log list.

---

## Troubleshooting

### Issue: Metrics badge not appearing

**Check:**
1. `window.KanbanSupabaseIntegration` exists
2. `window.kanbanSupabaseUI` exists
3. Both initialized: `window.kanbanSupabaseUI.initialized === true`
4. Call `enhanceCard()` AFTER card is in DOM

### Issue: Modal styles missing

**Solution:** Styles inject automatically on first modal open. If missing:
```javascript
window.kanbanSupabaseUI._injectModalStyles();
```

### Issue: Timer not working

**Check:**
1. Stage ID is valid: `window.kanbanSupabaseUI.startTimer(ticketId, stageId)`
2. Backend health: `http://localhost:5001/api/kanban/supabase/health`
3. Console for errors

---

## Next Steps

Once basic integration is working:

1. ✅ **Customize card details button styling**
2. ✅ **Add keyboard shortcuts** (e.g., `D` key for details modal)
3. ✅ **Implement analytics dashboard** with charts
4. ✅ **Add batch operations** (e.g., bulk timer start/stop)
5. ✅ **Create reports** (weekly time summary, bottleneck analysis)

---

**Created:** November 29, 2025  
**Version:** 1.0.0  
**Status:** ✅ Production Ready - Full UI Component Library

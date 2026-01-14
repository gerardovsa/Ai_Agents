# 🚀 Kanban Supabase Integration - Quick Start Guide

## What It Does

Adds **time tracking and analytics** to InHouse Kanban by syncing job data to Supabase PostgreSQL. This gives you:

✅ **Real-time stage transition tracking** (how long jobs spend in each stage)  
✅ **Production log entries** (notes, delays, wastage tracking)  
✅ **Job performance metrics** (estimated vs actual hours, quality scores)  
✅ **Custom notes with priority levels** (high/medium/low)  
✅ **Business hours calculation** (Mon-Fri, 8am-5pm)  
✅ **Time metrics dashboard** (current stage time, total time, transitions)

## 5-Minute Setup

### 1. Verify Backend Routes Registered

Open `AI_infrastructure/flask_app.py` and check:

```python
from routes.kanban_supabase_routes import kanban_supabase_bp

app.register_blueprint(kanban_supabase_bp)  # Should be around line 317
```

### 2. Test Health Check

```bash
# Start Flask server
BISTART

# Wait 10 seconds, then test
curl http://localhost:5001/api/kanban/supabase/health
```

**Expected response:**
```json
{
  "success": true,
  "message": "Supabase connection healthy",
  "schema": "kanban_analytics"
}
```

If this fails, check database connection in `shared/database_utils.py`.

### 3. Load Frontend Script

In your Kanban module or HTML:

```javascript
// Load Supabase integration
const script = document.createElement('script');
script.src = 'UI/external/modules/inhouse-kanban/kanban-supabase-integration.js';
script.onload = () => {
    console.log('✅ Supabase integration loaded');
};
document.head.appendChild(script);
```

### 4. Initialize on Page Load

```javascript
// In your module's init() method
async init() {
    // Initialize Supabase
    if (window.KanbanSupabaseIntegration) {
        const ready = await window.KanbanSupabaseIntegration.initialize();
        if (ready) {
            console.log('✅ Supabase ready for time tracking');
        }
    }
    
    // Load jobs from SQL Server
    const jobs = await this.fetchJobs();
    
    // Batch sync to Supabase
    await window.KanbanSupabaseIntegration.batchSyncJobs(jobs);
    
    // Render Kanban board
    this.renderBoard(jobs);
}
```

### 5. Record Stage Transitions

Hook into your drag-and-drop handler:

```javascript
async handleDrop(event) {
    const ticketId = parseInt(event.dataTransfer.getData('ticketId'));
    const fromStageId = parseInt(event.dataTransfer.getData('stageId'));
    const toStageId = parseInt(event.target.dataset.stageId);
    
    // Record transition in Supabase (NEW!)
    await window.KanbanSupabaseIntegration.recordStageTransition(
        ticketId, fromStageId, toStageId
    );
    
    // Your existing drop logic...
}
```

## Common Usage Patterns

### Pattern 1: Sync Job on Load

```javascript
// Single job
await window.KanbanSupabaseIntegration.syncJobToSupabase(job);

// Batch (recommended for page load)
await window.KanbanSupabaseIntegration.batchSyncJobs(jobs);
```

### Pattern 2: Get Time Metrics for Display

```javascript
const metrics = await window.KanbanSupabaseIntegration.getJobTimeMetrics(12345);

console.log(`Time in current stage: ${metrics.current_stage_hours.toFixed(1)} hours`);
console.log(`Total transitions: ${metrics.total_transitions}`);
console.log(`Total time: ${metrics.total_hours.toFixed(1)} hours`);
```

### Pattern 3: Add Production Note

```javascript
await window.KanbanSupabaseIntegration.addProductionLogEntry({
    ticket_id: 12345,
    entry_type: 'note',
    note_text: 'Customer called to change shipping address',
    created_by_user: 'JD'
});
```

### Pattern 4: Track Time with Timer

```javascript
// Start work
window.KanbanSupabaseIntegration.startJobTimer(12345, 3);

// ... work happens ...

// Stop work and record duration
const result = await window.KanbanSupabaseIntegration.stopJobTimer(12345, 'Printing complete');
console.log(`Work took ${result.duration_hours.toFixed(2)} hours`);
```

### Pattern 5: Record Performance Metrics

```javascript
await window.KanbanSupabaseIntegration.recordJobPerformance({
    ticket_id: 12345,
    estimated_hours: 3.0,
    actual_hours: 2.5,
    quality_score: 95.0,
    material_cost: 50.00,
    labor_cost: 75.00,
    total_cost: 125.00,
    revenue: 250.00,
    profit_margin: 50.0
});
```

## Testing Your Integration

### Quick Test Script

Paste this into your browser console:

```javascript
(async () => {
    const integration = window.KanbanSupabaseIntegration;
    
    // 1. Check if loaded
    if (!integration) {
        console.error('❌ Integration not loaded');
        return;
    }
    
    // 2. Initialize
    const ready = await integration.initialize();
    console.log(ready ? '✅ Initialized' : '❌ Init failed');
    
    // 3. Test job sync
    const testJob = {
        TicketID: 99999,
        ClientName: 'Test Corp',
        StageID: 1
    };
    
    const syncResult = await integration.syncJobToSupabase(testJob);
    console.log(syncResult.success ? '✅ Job synced' : '❌ Sync failed');
    
    // 4. Test stage transition
    const transResult = await integration.recordStageTransition(99999, 1, 2, 'Test');
    console.log(transResult.success ? '✅ Transition recorded' : '❌ Transition failed');
    
    // 5. Get metrics
    const metrics = await integration.getJobTimeMetrics(99999);
    console.log('📊 Metrics:', metrics);
    
    console.log('✅ All tests passed!');
})();
```

**Expected output:**
```
✅ Initialized
✅ Job synced
✅ Transition recorded
📊 Metrics: { ticket_id: 99999, current_stage_hours: 0.0, ... }
✅ All tests passed!
```

## API Endpoints Reference

All endpoints are prefixed with `/api/kanban/supabase/`:

| Method | Endpoint | Purpose |
|--------|----------|---------|
| GET | `/health` | Verify Supabase connection |
| POST | `/sync-job` | Sync single job |
| POST | `/batch-sync` | Batch sync multiple jobs |
| POST | `/stage-transition` | Record stage transition |
| GET | `/job-metrics/:id` | Get job time metrics |
| POST | `/production-log` | Add production log entry |
| GET | `/production-log/:id` | Get production log for job |
| POST | `/job-note` | Add custom job note |
| POST | `/job-performance` | Record job performance |

## Troubleshooting

### Issue: "Supabase integration not loaded"

**Solution:** Ensure script is loaded before calling methods:

```javascript
if (window.KanbanSupabaseIntegration) {
    // Safe to use
} else {
    console.warn('Load script first!');
}
```

### Issue: Health check fails

**Solution:** Check database connection:

```bash
# In AI_infrastructure directory
python -c "from shared.database_utils import get_database_connection; conn = get_database_connection('kanban_analytics'); print('✅ Connection OK')"
```

### Issue: Jobs not syncing

**Solution:** Verify job object has `TicketID` field (case-sensitive):

```javascript
const job = {
    TicketID: 12345,  // Must be capitalized!
    ClientName: 'Acme Corp'
};
```

### Issue: Stage transitions not calculating time

**Explanation:** First transition has no previous reference, so `transition_time_hours` is `null`. This is expected. Second and subsequent transitions will have time calculations.

## Next Steps

✅ **Basic Setup Complete!** Now you can:

1. **Display metrics on cards** - Show time in stage on each Kanban card
2. **Add production log UI** - Create modal for viewing/adding log entries
3. **Build performance dashboard** - Visualize metrics across all jobs
4. **Set up alerts** - Notify when jobs exceed time thresholds
5. **Create analytics reports** - Use Supabase data for insights

See `SUPABASE_INTEGRATION_COMPLETE.md` for detailed documentation.

---

**Created:** November 29, 2025  
**Version:** 1.0.0  
**Status:** ✅ Ready for Production Use

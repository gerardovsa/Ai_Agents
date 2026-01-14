# Supabase UI Integration - Browser Testing Guide

## Quick Status Check

Run this in the browser console to check if Supabase UI is loaded:

```javascript
// Check if scripts are loaded
console.log('✅ Supabase Integration Scripts Status:');
console.log('  - KanbanSupabaseIntegration:', typeof window.KanbanSupabaseIntegration !== 'undefined' ? '✅ LOADED' : '❌ NOT LOADED');
console.log('  - kanbanSupabaseUI:', typeof window.kanbanSupabaseUI !== 'undefined' ? '✅ LOADED' : '❌ NOT LOADED');

if (window.kanbanSupabaseUI) {
    console.log('  - UI initialized:', window.kanbanSupabaseUI.initialized ? '✅ YES' : '⚠️ NO');
    console.log('\n✅ UI methods available:', Object.keys(window.kanbanSupabaseUI).filter(k => typeof window.kanbanSupabaseUI[k] === 'function').join(', '));
}
```

## Test Individual Features

### 1. Test Card Enhancement

```javascript
// Find a card in the DOM
const card = document.querySelector('.kanban-card');
const ticketId = card.dataset.ticketId || 12345;

// Enhance the card with Supabase time metrics
await window.kanbanSupabaseUI.enhanceCard(card, ticketId);
console.log('✅ Card enhanced with time metrics badge');
```

### 2. Test Job Details Modal

```javascript
// Open job details modal (use real ticket ID from your system)
const ticketId = 12345; // Replace with real ticket ID

await window.kanbanSupabaseUI.showJobDetailsModal(ticketId, {
    TicketID: ticketId,
    ClientName: 'Test Corporation',
    ShortJobDesc: 'Test Job Description',
    StageID: 2,
    StageName: 'Pre-press'
});

console.log('✅ Job details modal opened');
```

### 3. Test Production Log Entry

```javascript
// Show production log entry form
const ticketId = 12345; // Replace with real ticket ID

window.kanbanSupabaseUI.showAddLogEntryForm(ticketId);
console.log('✅ Production log entry form displayed');
```

### 4. Test Timer System

```javascript
// Start work timer
const ticketId = 12345; // Replace with real ticket ID

await window.kanbanSupabaseUI.startTimer(ticketId);
console.log('✅ Timer started for ticket', ticketId);

// Wait a few seconds, then stop timer
setTimeout(async () => {
    await window.kanbanSupabaseUI.stopTimer(ticketId);
    console.log('✅ Timer stopped for ticket', ticketId);
}, 5000); // Wait 5 seconds
```

### 5. Test Performance Metrics Form

```javascript
// Submit performance metrics
const ticketId = 12345; // Replace with real ticket ID

// This would normally be called from the modal form
// For testing, you can call the backend API directly:
const result = await window.KanbanSupabaseIntegration.recordJobPerformance(
    ticketId,
    8.5, // hours_worked
    95, // quality_score (0-100)
    125.00, // actual_cost
    100.00 // estimated_cost (optional)
);

console.log('✅ Performance metrics recorded:', result);
```

## Troubleshooting

### Issue: Scripts Not Loaded

**Symptom:** `window.kanbanSupabaseUI` is `undefined`

**Solutions:**

1. Check manifest.json has `additional_scripts`:
   ```javascript
   // In browser console
   fetch('external/modules/inhouse-kanban/manifest.json')
       .then(r => r.json())
       .then(m => console.log('Additional scripts:', m.additional_scripts));
   ```

2. Check if scripts exist in file system:
   ```javascript
   // Test script URLs
   fetch('external/modules/inhouse-kanban/kanban-supabase-integration.js')
       .then(r => console.log('Integration script:', r.ok ? '✅ EXISTS' : '❌ NOT FOUND'));
   
   fetch('external/modules/inhouse-kanban/kanban-supabase-ui.js')
       .then(r => console.log('UI script:', r.ok ? '✅ EXISTS' : '❌ NOT FOUND'));
   ```

3. Force reload the module:
   ```javascript
   // Reload InHouse Kanban module
   location.reload(); // Or hard refresh (Ctrl+Shift+R)
   ```

### Issue: Backend API Not Responding

**Symptom:** API calls fail with 404 or 500 errors

**Solutions:**

1. Check Flask server is running:
   ```powershell
   # In PowerShell terminal
   BISTART
   ```

2. Verify Supabase routes are registered:
   ```javascript
   // Test health endpoint
   fetch('http://localhost:5001/api/kanban/supabase/health')
       .then(r => r.json())
       .then(d => console.log('Supabase backend:', d));
   ```

3. Check browser console for CORS errors

### Issue: Modal Doesn't Display

**Symptom:** Modal function runs but nothing appears

**Solutions:**

1. Check if backdrop exists:
   ```javascript
   console.log('Modal backdrop:', document.querySelector('.kanban-modal-backdrop'));
   ```

2. Check CSS injection:
   ```javascript
   console.log('UI styles injected:', window.kanbanSupabaseUI.stylesInjected);
   ```

3. Check z-index conflicts:
   ```javascript
   // Modals use z-index: 10000
   // Check if anything else has higher z-index
   const elements = document.querySelectorAll('*');
   const highZIndex = Array.from(elements).filter(el => {
       const z = parseInt(window.getComputedStyle(el).zIndex);
       return z > 10000;
   });
   console.log('Elements with z-index > 10000:', highZIndex);
   ```

## Expected Console Output After Module Load

When InHouse Kanban module loads successfully with Supabase integration:

```
🏭 Initializing InHouse Kanban Module...
✅ Data already loaded: 42 jobs
✅ Sidebar HTML already loaded by ModuleLoader
✅ Supabase integration scripts detected, initializing UI...
[Supabase UI] Initializing...
[Supabase UI] Integration layer status: ✅ LOADED
[Supabase UI] Injecting modal styles...
[Supabase UI] ✅ Initialization complete
✅ Supabase UI initialized successfully
✅ InHouse Kanban Module initialized successfully
```

## Next Steps After Successful Testing

1. **Add "View Details" button to card template** (see SUPABASE_UI_INTEGRATION_GUIDE.md)
2. **Hook stage transitions** to record timing automatically
3. **Implement Analytics tab** with aggregated metrics
4. **Customize CSS** if needed (see guide for theme variables)

## Need More Help?

See the complete integration guide:
- `SUPABASE_UI_INTEGRATION_GUIDE.md` - Step-by-step setup instructions
- `SUPABASE_INTEGRATION_COMPLETE.md` - Full technical reference
- `SUPABASE_QUICK_START.md` - Quick start guide for developers

---

**Created:** November 29, 2025  
**Version:** 1.0.0  
**Status:** ✅ Ready for Testing

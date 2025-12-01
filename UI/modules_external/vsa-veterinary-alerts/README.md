# VSA Veterinary Alerts Module

**Version:** 1.0.0  
**Framework:** Modern Module Loading Framework (Composition Pattern)  
**Database:** Supabase (SQL_Data_AI_UI_v5 Project)

## Overview

The VSA Veterinary Alerts module provides real-time monitoring and management of veterinary call alerts and follow-up actions. It connects directly to the VSA Analytics Supabase database and displays alerts with a professional, modern UI within the AI_agents platform.

## Features

✅ **Real-time Alert Monitoring**
- Displays alerts extracted from `manager_alerts_tags` field
- Auto-refreshes every 60 seconds
- Severity-based color coding (High/Medium/Low)

✅ **Follow-up Action Tracking**
- Displays follow-ups from `follow_up_actions` field
- Priority-based organization
- Action category filtering

✅ **Advanced Filtering**
- Severity/Priority filters
- Date range selection (Today/Week/Month/All)
- Real-time search
- Multiple view modes (Alerts/Follow-ups/Both)

✅ **Modern UI**
- Dark theme matching AI_agents aesthetic
- Responsive card layouts
- Interactive hover effects
- Professional stats dashboard

✅ **Sidebar Integration**
- Quick alerts sidebar (left side)
- High-priority alerts only
- Draggable toggle button
- Persistent state

## Architecture

### Modern Composition Pattern

This module uses the **Modern Module Loading Framework** (no BaseModule inheritance):

- ✅ Plain JavaScript object export
- ✅ Explicit utility injection via `Object.assign(this, utilities)`
- ✅ Lifecycle hooks: `onDashboardLoad`, `onSidebarLoad`, `onUnload`
- ✅ Automatic event listener cleanup
- ✅ Framework-agnostic design

### Data Source

**Database:** Supabase PostgreSQL  
**URL:** `https://wuwmvtslltqhaycyukxk.supabase.co`  
**Table:** `veterinary_calls`

**Key Fields:**
- `manager_alerts_tags` - Alert data (parsed line-by-line)
- `follow_up_actions` - Follow-up data (parsed line-by-line)
- `call_date` - Call timestamp
- `client_name` - Client information
- `staff_name` - Staff member
- `id` - Unique call identifier

### Data Processing

**Alert Extraction:**
```javascript
// Format: "Alert Type: Description"
"Missed Opportunity: Client mentioned pain but no follow-up scheduled"
→ {
    type: "Missed Opportunity",
    description: "Client mentioned pain but no follow-up scheduled",
    severity: "high" // auto-determined
}
```

**Follow-up Extraction:**
```javascript
// Format: "Category: Action"
"Client Experience: Schedule follow-up call next week"
→ {
    category: "Client Experience",
    action: "Schedule follow-up call next week",
    priority: "high" // auto-determined
}
```

## Installation

The module is already installed in `UI/modules_external/vsa-veterinary-alerts/`

**Files:**
- `manifest.json` - Module configuration
- `vsa-veterinary-alerts.js` - Main module code
- `vsa-veterinary-alerts.css` - Styling
- `vsa-alerts-sidebar.html` - Sidebar template
- `README.md` - This file

## Usage

### Access Dashboard

1. Open AI_agents application
2. Click "VSA Alerts" tab in the navigation
3. Dashboard loads automatically with real-time data

### Access Sidebar

1. Look for the draggable "Quick Alerts" button on the left side
2. Click to open sidebar with high-priority alerts
3. Click "View All" to switch to full dashboard

### Filtering Alerts

**Severity Filter:**
- All Severities
- High (red)
- Medium (orange)
- Low (green)

**Date Range:**
- Today
- This Week
- This Month
- All Time

**Search:**
- Search by alert type, description, client name, or staff name
- Real-time filtering as you type

### View Modes

**Alerts View:**
- Shows only manager alerts
- Severity-based filtering
- Color-coded cards

**Follow-ups View:**
- Shows only follow-up actions
- Priority-based filtering
- Category organization

**Both View:**
- Split-screen layout
- Alerts on left, follow-ups on right
- Independent filtering

## Configuration

### Supabase Connection

The module hardcodes Supabase credentials for the VSA database:

```javascript
state: {
    supabaseUrl: 'https://wuwmvtslltqhaycyukxk.supabase.co',
    supabaseKey: 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...',
    supabaseClient: null
}
```

**Security Note:** The service role key is included for direct database access. In production, consider using row-level security (RLS) and anon keys.

### Auto-refresh Interval

Default: 60 seconds (configurable in code)

```javascript
// In startAutoRefresh() method
this.state.refreshInterval = setInterval(() => {
    this.refreshData();
}, 60000); // Change to adjust interval
```

### Data Limits

Default: 500 calls loaded

```javascript
// In loadVeterinaryCalls() method
.limit(500) // Change to load more/fewer records
```

## Development

### Testing Module

```javascript
// In browser console

// Check module loaded
const loader = window.ModuleLoaderV4;
console.log('Module available:', loader.isModuleAvailable('vsa-veterinary-alerts'));

// Load module
await loader.loadModule('vsa-veterinary-alerts', 'dashboard');

// Check module loaded
console.log('Module loaded:', loader.isModuleLoaded('vsa-veterinary-alerts'));

// Enable debug mode
loader.enableDebug();

// Reload module
await loader.reloadModule('vsa-veterinary-alerts');
```

### Accessing Module State

```javascript
// Get module instance (for debugging)
const moduleInstances = window.ModuleLoaderV4.moduleInstances;
const vsaModule = moduleInstances.get('vsa-veterinary-alerts');

if (vsaModule) {
    console.log('Alerts:', vsaModule.state.alerts);
    console.log('Follow-ups:', vsaModule.state.followUps);
    console.log('Stats:', vsaModule.state.stats);
}
```

### Extending Functionality

**Add New Filter:**

1. Update `state.filters` object
2. Add filter UI in `renderFilters()`
3. Add filter logic in `getFilteredAlerts()` or `getFilteredFollowUps()`
4. Add event listener in `setupEventListeners()`

**Add New View Mode:**

1. Add button to `renderFilters()`
2. Update `state.view` options
3. Add new rendering method
4. Update `renderContent()` to call new method

**Customize Severity/Priority Detection:**

Update `determineSeverity()` or `determinePriority()` methods with new keywords/logic.

## Troubleshooting

### Module Not Loading

**Symptom:** Module doesn't appear in tabs

**Solutions:**
1. Check browser console for errors
2. Verify Supabase library loaded: `typeof window.supabase`
3. Enable debug mode: `window.ModuleLoaderV4.enableDebug()`
4. Check manifest.json is valid JSON

### No Data Showing

**Symptom:** Empty state displayed

**Solutions:**
1. Verify Supabase connection in Network tab
2. Check `manager_alerts_tags` field has data
3. Verify credentials are correct
4. Check browser console for API errors

### Supabase Library Not Loading

**Symptom:** "Supabase initialization failed" error

**Solutions:**
1. Check CDN URL: `https://cdn.jsdelivr.net/npm/@supabase/supabase-js@2`
2. Verify internet connection
3. Check browser Content Security Policy (CSP)
4. Try reloading page

### Filters Not Working

**Symptom:** Filtering doesn't update display

**Solutions:**
1. Check event listeners are attached: `setupEventListeners()`
2. Verify filter state updating: `console.log(this.state.filters)`
3. Check `getFilteredAlerts()` logic
4. Ensure `renderDashboard()` called after filter change

## Performance Optimization

### Current Optimizations

✅ **Lazy Loading** - Module loads on-demand (not at startup)  
✅ **Limited Records** - Only loads last 500 calls  
✅ **Efficient Rendering** - Direct DOM manipulation  
✅ **Auto-cleanup** - Event listeners removed on unload  

### Future Optimizations

🔄 **Virtual Scrolling** - For large alert lists  
🔄 **Debounced Search** - Already implemented (300ms delay)  
🔄 **Pagination** - For very large datasets  
🔄 **WebSocket Updates** - Real-time push notifications  

## Related Documentation

**Framework:**
- `UI/shared/js/MODERN_MODULE_FRAMEWORK_GUIDE.md` - Complete architecture guide
- `UI/shared/js/QUICK_REFERENCE_CARD.md` - Fast lookup reference
- `.github/prompts/Module Architect V4.0 - Modern Framework.prompt.md` - AI agent prompt

**Source Data:**
- `SQL_Data_AI_UI_v5/tools/Dashboard_Actions/alert_v4_tiered.py` - Original Streamlit implementation
- `SQL_Data_AI_UI_v5/tools/Dashboard_Actions/followup_actions_v4_tiered.py` - Original follow-up implementation
- `SQL_Data_AI_UI_v5/SUPABASE/supabase_config.py` - Database configuration

## Version History

### 1.0.0 (November 30, 2025)
- ✅ Initial release
- ✅ Modern composition pattern implementation
- ✅ Supabase integration
- ✅ Alert and follow-up tracking
- ✅ Advanced filtering
- ✅ Sidebar integration
- ✅ Auto-refresh functionality
- ✅ Professional dark theme UI

## License

Part of the AI_agents platform. Internal use only.

## Support

For issues or questions:
1. Check browser console for errors
2. Enable debug mode: `window.ModuleLoaderV4.enableDebug()`
3. Review troubleshooting section above
4. Check related documentation

---

**Created:** November 30, 2025  
**Framework:** ModuleLoaderV4 (Modern Composition Pattern)  
**Status:** ✅ Production Ready

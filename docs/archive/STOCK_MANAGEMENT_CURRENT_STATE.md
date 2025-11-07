# Stock Management Module - Current State Analysis

**Date:** November 3, 2025  
**Status:** REVERTED - Need to re-apply fixes to correct file

---

## 📂 File Structure

### Current Files:
1. **`stock-management.js`** (1,933 lines) - BASE module
2. **`stock-management-enhanced.js`** (598 lines) - ENHANCED version with Plotly
3. **`stock-management.css`** - Styling
4. **`manifest.json`** - Configuration

---

## 🔍 Current State

### Manifest Configuration:
```json
{
    "scriptPath": "external/modules/stock-management/stock-management.js",
    "enhancedScript": "external/modules/stock-management/stock-management-enhanced.js",
}
```

**This means:**
- The module loader uses `stock-management.js` as the base
- Then EXTENDS it with `stock-management-enhanced.js` features
- The enhanced file adds Plotly charts, SQL viewer, and inline editing

---

## ❌ Problem

The user reverted ALL changes, which means:
1. ✅ `stock-management.js` - Back to ORIGINAL (no refresh buttons added)
2. ✅ `stock-management-enhanced.js` - Back to ORIGINAL (no changes)
3. ✅ `stock-management.css` - Back to ORIGINAL (no header styling)

**What was lost:**
- Individual refresh buttons in each sub-tab
- Per-tab refresh functions
- Card header styling with left/right layout
- SQL query execution functions
- Data loading improvements

---

## 🎯 What Needs to be Done

### Option 1: Modify Base File (`stock-management.js`)
**Pros:**
- All changes in one place
- Works even if enhanced script not loaded

**Cons:**
- Enhanced script extends base, so changes here affect everything
- Larger file to maintain

### Option 2: Modify Enhanced File (`stock-management-enhanced.js`)
**Pros:**
- Keeps base clean
- Enhanced features stay in enhanced file
- Cleaner separation of concerns

**Cons:**
- Enhanced script must be loaded
- Need to ensure proper extension

---

## 🔧 Recommended Approach

**MODIFY THE ENHANCED FILE** (`stock-management-enhanced.js`)

Why:
1. The enhanced file is meant to EXTEND the base
2. Refresh buttons = enhancement feature
3. Keep base file as stable foundation
4. Enhanced file already has hooks for SQL viewer, charts, etc.

---

## 📋 What to Add to Enhanced File

### 1. Per-Tab Refresh Functions
```javascript
StockManagementModule.prototype.refreshInvoiceTab = function() {
    console.log('[REFRESH] Clearing invoice processor...');
    // Clear upload form
};

StockManagementModule.prototype.refreshUsageAnalyticsTab = function() {
    console.log('[REFRESH] Refreshing usage analytics...');
    this.loadUsageAnalytics();
};

StockManagementModule.prototype.refreshReorderDashboardTab = function() {
    console.log('[REFRESH] Refreshing reorder dashboard...');
    this.loadReorderDashboard();
};

StockManagementModule.prototype.refreshProfitAnalysisTab = function() {
    console.log('[REFRESH] Refreshing profit analysis...');
    const periodSelector = document.getElementById('profit-period-selector');
    const days = periodSelector ? parseInt(periodSelector.value) : 90;
    this.loadProfitAnalysis(days);
};

StockManagementModule.prototype.refreshSQLViewerTab = function() {
    console.log('[REFRESH] Refreshing SQL viewer...');
    // Re-execute last query
};

StockManagementModule.prototype.refreshAIAnalyticsTab = function() {
    console.log('[REFRESH] Refreshing AI analytics...');
    this.loadAIAnalyticsData();
};
```

### 2. Override Tab Initialization (Add Refresh Buttons)
```javascript
// Override initializeUsageAnalyticsTab to add refresh button
const originalInitUsageAnalytics = StockManagementModule.prototype.initializeUsageAnalyticsTab;
StockManagementModule.prototype.initializeUsageAnalyticsTab = function() {
    // Call original
    originalInitUsageAnalytics.call(this);
    
    // Add refresh button to header
    const tab = this.getSubTabContainer('usage-analytics');
    if (tab) {
        const header = tab.querySelector('.dashboard-card .card-header');
        if (header) {
            // Inject refresh button
            // ...
        }
    }
};
```

### 3. Add CSS for Card Headers
Add to `stock-management.css`:
```css
.dashboard-card .card-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 15px 20px;
    background: var(--bg-secondary, #161b22);
    border: 1px solid var(--border-default, #30363d);
    border-radius: 6px 6px 0 0;
    margin-bottom: 20px;
}

.dashboard-card .card-header .header-left {
    flex: 1;
}

.dashboard-card .card-header .header-right {
    display: flex;
    align-items: center;
    gap: 10px;
}
```

---

## 🚀 Next Steps

1. **Add refresh functions** to `stock-management-enhanced.js`
2. **Override tab initialization** to inject refresh buttons
3. **Add CSS styling** to `stock-management.css`
4. **Test each tab** to ensure buttons work

---

## 📝 Key Points

- ✅ DO NOT modify `stock-management.js` (it's the stable base)
- ✅ DO modify `stock-management-enhanced.js` (that's what it's for)
- ✅ DO add CSS to `stock-management.css` (styling goes here)
- ✅ DO test with backend running (SQL queries need API)

---

## 🧪 Testing Plan

After changes:
1. Start backend: `cd C:\Users\gpoli\GIT\In_House_SQL\G_Folder\AI_infrastructure && python flask_app.py`
2. Open UI: `http://localhost:5001`
3. Navigate to Stock Management module
4. Test each sub-tab's refresh button
5. Verify data loads correctly
6. Check console for errors

---

**Ready to proceed with modifications to the ENHANCED file?**

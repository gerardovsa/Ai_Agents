# 🚀 Automation Settings - Quick Reference

**Date:** November 28, 2025  
**Version:** 1.0.0

---

## 📍 Quick Links

**Full Documentation:** `AUTOMATION_SETTINGS_INTEGRATION_COMPLETE.md`

---

## 🎯 What Was Implemented

✅ **Sidebar Settings Panel** - View/edit automation settings in right sidebar  
✅ **Canvas Settings Overlay** - Floating settings panel on automation canvas  
✅ **Bidirectional Sync** - Changes in one location update the other automatically  
✅ **Auto-Save** - Settings save automatically 2 seconds after changes  
✅ **Draft Mode** - Settings disabled for draft workflows with "Convert" button  
✅ **Promotion Modal** - Choose schedule type when converting draft to automation

---

## 📁 Files Created

### **New Files:**
1. `UI/modules/components/automation-settings-sync.js` (400 lines)
2. `UI/modules/components/automation-settings.css` (800 lines)

### **Modified Files:**
3. `UI/modules/components/automations.js` (+700 lines)
4. `UI/modules/automation-workflows/automation-workflows.js` (+250 lines)
5. `UI/business-ai-platform-v2.html` (toolbar button + imports)

---

## 🔑 Key Components

### **AutomationSettingsSync (Central State Manager)**

```javascript
// Load settings
await AutomationSettingsSync.loadSettings('wf_a3f8b2c1_1732029847');

// Update setting
AutomationSettingsSync.updateSetting('schedule.cron', '0 9 * * *');

// Subscribe to changes
const unsubscribe = AutomationSettingsSync.subscribe((eventType, data) => {
    console.log('Settings changed:', eventType, data.automation);
});

// Save manually
await AutomationSettingsSync.save();

// Revert changes
AutomationSettingsSync.revert();

// Check draft mode
const isDraft = AutomationSettingsSync.isDraft();
```

### **Sidebar Settings Panel**

```javascript
// Open settings panel (replaces automation list)
await AutomationsSidebar.openSettingsPanel(automation);

// Close settings panel (back to list)
AutomationsSidebar.closeSettingsPanel();

// Render settings sections
AutomationsSidebar.renderSchedulingSettings(automation, isDraft);
AutomationsSidebar.renderTriggerSettings(automation, isDraft);
AutomationsSidebar.renderExecutionSettings(automation, isDraft);
AutomationsSidebar.renderNotificationSettings(automation, isDraft);
```

### **Canvas Settings Overlay**

```javascript
// Show floating settings panel
await automationCanvas.showSettingsPanel();

// Close overlay
automationCanvas.closeSettingsPanel();

// Promote draft to automation
await automationCanvas.promoteToAutomation('wf_draft_123');
```

---

## 🎨 Settings Categories

### **1. Scheduling**
- Manual (run on demand)
- Cron (e.g., `0 9 * * *` = daily at 9am)
- Interval (every X minutes/hours/days)
- One-Time (specific date/time)

### **2. Triggers**
- Manual
- Schedule (time-based)
- Webhook (HTTP POST to unique URL)
- Event (platform events like Gmail, Shopify)

### **3. Execution Options**
- Retry Policy (none, exponential, fixed)
- Max Retries (1-10)
- Timeout (10-3600 seconds)
- Error Handling (stop, continue, rollback)
- Allow Concurrent Executions (checkbox)

### **4. Notifications**
- Notify on Success (checkbox)
- Notify on Failure (checkbox)
- Channels (email, slack, webhook)
- Email Recipients (comma-separated)
- Daily Summary Report (checkbox)

---

## 🔄 User Flows

### **Flow 1: Edit Settings in Sidebar**
1. Open automations sidebar
2. Click automation card → Settings panel opens
3. Edit settings (e.g., change cron schedule)
4. Auto-save triggers after 2 seconds
5. Click "Edit in Canvas" to switch to canvas
6. Canvas settings overlay shows same data (synced)

### **Flow 2: Edit Settings in Canvas**
1. Load workflow in canvas
2. Click settings icon (⚙️) in toolbar
3. Floating overlay appears (right side)
4. Edit settings (e.g., enable notifications)
5. Auto-save triggers after 2 seconds
6. Sidebar panel updates (if open)

### **Flow 3: Promote Draft to Automation**
1. Click "Convert to Automation" button
2. Modal appears with 4 schedule options
3. Select schedule type (e.g., "Scheduled - Cron")
4. Click "Convert to Automation"
5. Backend creates `automation_workflows` entry
6. Settings panel refreshes (no longer draft mode)
7. All settings now editable

---

## 🎯 CSS Classes

### **Settings Panel:**
- `.automation-settings-panel` - Main sidebar panel
- `.canvas-settings-overlay` - Floating canvas overlay
- `.settings-section` - Section container
- `.settings-form` - Form container
- `.settings-disabled` - Draft mode disabled state

### **Form Elements:**
- `.form-group` - Form field container
- `.form-hint` - Helper text
- `.checkbox-label` - Checkbox with label
- `.interval-input` - Interval number + unit
- `.webhook-url-container` - Webhook URL + copy button

### **Buttons:**
- `.btn-primary` - Primary action (save)
- `.btn-secondary` - Secondary action (revert)
- `.btn-promote` - Convert to automation
- `.settings-back-btn` - Back to list

### **Draft Mode:**
- `.draft-mode-banner` - Yellow warning banner
- `.canvas-draft-banner` - Banner in canvas

### **Modal:**
- `.promotion-modal-overlay` - Modal backdrop
- `.promotion-modal` - Modal container
- `.promotion-option` - Radio option card

---

## 🔧 API Endpoints

### **GET /api/automation/{slug}**
Load automation settings
```json
{
  "success": true,
  "automation": {
    "slug": "wf_a3f8b2c1_1732029847",
    "name": "Daily Gmail Summary",
    "enabled": true,
    "type": "production",  // or "draft"
    "schedule": { ... },
    "trigger": { ... },
    "execution_options": { ... },
    "notifications": { ... },
    "run_count": 45,
    "success_count": 43,
    "error_count": 2,
    "last_run_at": "2025-11-28T09:00:00Z"
  }
}
```

### **PUT /api/automation/{slug}**
Save automation settings (entire automation object)

### **POST /api/automation/{slug}/promote**
Promote draft to automation
```json
{
  "schedule": {
    "type": "cron"  // or "manual", "interval", "webhook"
  }
}
```

---

## ⚡ Quick Tips

### **For Developers:**

1. **Always load settings first:**
   ```javascript
   await AutomationSettingsSync.loadSettings(slug);
   ```

2. **Subscribe to changes in both panels:**
   ```javascript
   this.settingsSyncUnsubscribe = AutomationSettingsSync.subscribe((eventType, data) => {
       if (eventType === 'update' || eventType === 'save') {
           this.refreshSettingsPanel();
       }
   });
   ```

3. **Unsubscribe when closing:**
   ```javascript
   if (this.settingsSyncUnsubscribe) {
       this.settingsSyncUnsubscribe();
   }
   ```

4. **Check draft mode before enabling settings:**
   ```javascript
   const isDraft = AutomationSettingsSync.isDraft();
   // Add disabled attribute if isDraft is true
   ```

5. **Use validation before save:**
   ```javascript
   const validation = AutomationSettingsSync.validate();
   if (!validation.valid) {
       console.error('Validation errors:', validation.errors);
       return;
   }
   ```

### **For Users:**

1. **Open settings:** Click automation card in sidebar OR settings icon in canvas
2. **Edit safely:** All changes auto-save after 2 seconds
3. **Revert mistakes:** Click "Revert Changes" to undo
4. **Switch views:** Use "Edit in Canvas" button to switch
5. **Draft mode:** Click "Convert to Automation" to enable scheduling

---

## 🐛 Troubleshooting

### **Settings not syncing?**
- Check console for errors
- Verify `AutomationSettingsSync` is loaded
- Ensure both panels are subscribed to changes

### **Auto-save not working?**
- Check network tab for PUT request
- Verify backend endpoint exists
- Check for validation errors in console

### **Promotion modal not appearing?**
- Verify `window.promotionModalResolve` is set
- Check for JavaScript errors in console
- Ensure modal HTML is correct

### **Draft mode not showing?**
- Check `automation.type` field
- Verify `AutomationSettingsSync.isDraft()` logic
- Ensure workflow_id is null for drafts

---

## 📦 Import Order

**Correct order in HTML:**
```html
<!-- 1. CSS first -->
<link rel="stylesheet" href="modules/components/automation-settings.css">

<!-- 2. Sync manager (no dependencies) -->
<script src="modules/components/automation-settings-sync.js"></script>

<!-- 3. Automations sidebar (uses sync manager) -->
<script src="modules/components/automations.js"></script>

<!-- 4. Canvas workflows (uses sync manager + sidebar render methods) -->
<script src="modules/automation-workflows/automation-workflows.js"></script>
```

---

## ✅ Testing Checklist

**Sidebar:**
- [ ] Opens on card click
- [ ] Back button works
- [ ] All form elements render
- [ ] Auto-save works
- [ ] Revert works

**Canvas:**
- [ ] Settings button exists
- [ ] Overlay appears/closes
- [ ] Scrollable
- [ ] Syncs with sidebar

**Sync:**
- [ ] Sidebar → Canvas sync
- [ ] Canvas → Sidebar sync
- [ ] Auto-save triggers
- [ ] isDirty tracking

**Promotion:**
- [ ] Modal opens
- [ ] Radio buttons work
- [ ] Promotion succeeds
- [ ] Settings enabled after

---

## 🎉 Success Indicators

✅ Click automation card → Settings panel opens  
✅ Change setting → Auto-save after 2 seconds  
✅ Edit in sidebar → Canvas overlay updates  
✅ Edit in canvas → Sidebar panel updates  
✅ Draft mode → Settings disabled + convert button  
✅ Convert → Settings enabled  
✅ All form elements work  
✅ Validation prevents bad saves  
✅ Responsive on mobile  

---

**Quick Reference Version:** 1.0.0  
**Last Updated:** November 28, 2025  
**See Full Docs:** `AUTOMATION_SETTINGS_INTEGRATION_COMPLETE.md`

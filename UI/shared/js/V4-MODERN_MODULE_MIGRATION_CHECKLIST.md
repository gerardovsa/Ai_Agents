# 🔄 BaseModule → Modern Composition Migration Checklist

**Date**: November 29, 2025  
**Status**: In Progress  
**Progress**: 0/16 modules migrated

---

## 📊 Migration Status

### Modules Requiring Migration (16 Total)

| # | Module | Type | Priority | Status | Notes |
|---|--------|------|----------|--------|-------|
| 1 | inhouse-kanban | external | HIGH | ⏳ Pending | Dashboard + Sidebar |
| 2 | communication-hub | external | HIGH | ⏳ Pending | Dashboard + Sidebar |
| 3 | stock-management | external | MEDIUM | ⏳ Pending | Dashboard only |
| 4 | shopify | external | MEDIUM | ⏳ Pending | Dashboard only |
| 5 | xero | external | MEDIUM | ⏳ Pending | Dashboard only |
| 6 | quote-calculator | external | MEDIUM | ⏳ Pending | Dashboard only |
| 7 | salesforce | external | LOW | ⏳ Pending | Dashboard only |
| 8 | render-management | external | LOW | ⏳ Pending | Dashboard only |
| 9 | production-analytics | external | LOW | ⏳ Pending | Dashboard only |
| 10 | github | external | LOW | ⏳ Pending | Dashboard only |
| 11 | database-visualizer | external | LOW | ⏳ Pending | Dashboard only |
| 12 | stock-management (copy) | external | SKIP | ⏭️ Skipped | Duplicate file |
| 13 | stock-management (copy 2) | external | SKIP | ⏭️ Skipped | Duplicate file |
| 14 | stock-management (archive) | external | SKIP | ⏭️ Skipped | Archived |
| 15 | stock-management (archive 2) | external | SKIP | ⏭️ Skipped | Archived |
| 16 | inhouse-kanban (copy) | external | SKIP | ⏭️ Skipped | Duplicate file |

**Active Modules**: 11  
**Duplicates/Archives**: 5

---

## ✅ Migration Checklist (Per Module)

### Phase 1: Preparation (Before Changes)

- [ ] **Read current module code**
  - [ ] Identify class name and inheritance
  - [ ] Map constructor parameters
  - [ ] Find all `super.initialize()` calls
  - [ ] List all instance methods
  - [ ] Note all event listeners
  - [ ] Document data flow

- [ ] **Analyze manifest**
  - [ ] Check manifest version (V1.0 vs V3.0)
  - [ ] Note capabilities (dashboard, sidebar)
  - [ ] Identify HTML files referenced
  - [ ] Check for missing dependencies

- [ ] **Test current functionality**
  - [ ] Sidebar button works
  - [ ] Floating toggle works (if applicable)
  - [ ] Dashboard renders correctly
  - [ ] Sidebar renders correctly (if applicable)
  - [ ] All features functional
  - [ ] Take screenshots for comparison

### Phase 2: Code Migration

- [ ] **Create backup**
  - [ ] Copy original file to `[module-name]-LEGACY.js`
  - [ ] Commit to git before changes

- [ ] **Update file header**
  ```javascript
  /**
   * FILE: UI/modules_external/[module]/[module].js
   * MODULE TYPE: external
   * ARCHITECTURE: Framework-modern (Composition pattern)
   * 
   * CAPABILITIES:
   * [✅/❌] Dashboard: [ENABLED/DISABLED]
   * [✅/❌] Sidebar: [ENABLED/DISABLED]
   * 
   * DEPENDENCIES:
   * - dom, api, storage, events, log
   * 
   * LAST MODIFIED: [DATE] - Migrated to modern composition pattern
   */
  ```

- [ ] **Convert class to object**
  - [ ] Remove `extends BaseModule`
  - [ ] Change `class MyModule` to `export default { ... }`
  - [ ] Remove `constructor()` method
  - [ ] Move constructor assignments to object properties

- [ ] **Add state properties**
  ```javascript
  export default {
      // Utilities (injected)
      dom: null,
      api: null,
      storage: null,
      events: null,
      log: null,
      
      // Module state
      data: [],
      filters: {},
      dashboardContainer: null,
      sidebarContainer: null,
      eventCleanupFns: [],
      
      // ... rest of module
  };
  ```

- [ ] **Convert `initialize()` to lifecycle hooks**
  - [ ] Replace `async initialize()` with `async onDashboardLoad(utilities)`
  - [ ] Remove `await super.initialize()`
  - [ ] Add `Object.assign(this, utilities)` at start
  - [ ] Store container reference explicitly

- [ ] **Add `onSidebarLoad()` if needed**
  - [ ] Create separate hook for sidebar
  - [ ] Move sidebar-specific initialization
  - [ ] Get sidebar container explicitly

- [ ] **Add `onUnload()` cleanup**
  - [ ] Add cleanup method
  - [ ] Call all cleanup functions
  - [ ] Clear references

### Phase 3: Pattern Replacements

- [ ] **Replace container access**
  ```javascript
  // Before:
  this.containerElement
  
  // After:
  this.dashboardContainer = this.dom.getContainer('tab-module-id');
  ```

- [ ] **Replace API calls**
  ```javascript
  // Before:
  const response = await fetch(`${this.API_BASE_URL}/api/data`);
  const data = await response.json();
  
  // After:
  const data = await this.api.get('/api/data');
  ```

- [ ] **Replace event listeners**
  ```javascript
  // Before:
  element.addEventListener('click', handler);
  
  // After:
  const cleanup = this.dom.on(element, 'click', handler);
  this.eventCleanupFns.push(cleanup);
  ```

- [ ] **Replace logging**
  ```javascript
  // Before:
  console.log('[ModuleName] Message');
  
  // After:
  this.log.info('Message');
  ```

- [ ] **Replace `this.manifest`**
  ```javascript
  // Before:
  const tabId = this.manifest.main_tab_id;
  
  // After:
  // Manifest data not needed - framework handles it
  // Or access from utilities if needed
  ```

### Phase 4: Manifest Migration

- [ ] **Update manifest to V3.0**
  - [ ] Remove V1.0 root properties
  - [ ] Add `capabilities` object
  - [ ] Add `dependencies` object
  - [ ] Update file paths

- [ ] **Add dependencies section**
  ```json
  "dependencies": {
      "utilities": ["dom", "api", "storage", "events"]
  }
  ```

- [ ] **Define capabilities**
  ```json
  "capabilities": {
      "dashboard": {
          "enabled": true,
          "tab_id": "module-id",
          "rendering": "js-controlled",
          "initialization": "lazy"
      },
      "sidebar": {
          "enabled": true,
          "html_file": "module-SIDEBAR.html",
          "width": "480px"
      }
  }
  ```

### Phase 5: Cleanup

- [ ] **Remove manual instantiation**
  ```javascript
  // DELETE THIS:
  if (typeof window !== 'undefined') {
      window.moduleId = new ModuleClass('module-id');
      window.moduleId.initialize();
  }
  ```

- [ ] **Remove unused methods**
  - [ ] Remove empty methods
  - [ ] Remove deprecated code
  - [ ] Clean up comments

- [ ] **Update imports/exports**
  - [ ] Ensure `export default` at end
  - [ ] Remove window assignments
  - [ ] Clean up require/import statements

### Phase 6: Testing

- [ ] **Load module in browser**
  ```javascript
  const moduleLoader = window.ModuleLoaderV4;
  await moduleLoader.loadModule('module-id', 'dashboard');
  ```

- [ ] **Test dashboard**
  - [ ] Click sidebar button
  - [ ] Dashboard renders
  - [ ] Data loads correctly
  - [ ] All buttons work
  - [ ] No console errors

- [ ] **Test sidebar (if applicable)**
  - [ ] Click floating toggle
  - [ ] Sidebar opens
  - [ ] Sidebar HTML loads
  - [ ] Quick actions work
  - [ ] No console errors

- [ ] **Test interactions**
  - [ ] Create/update operations
  - [ ] Delete operations
  - [ ] Filter/search functionality
  - [ ] Modal dialogs
  - [ ] Form submissions

- [ ] **Test cleanup**
  - [ ] Switch to different module
  - [ ] Switch back
  - [ ] No duplicate event handlers
  - [ ] No memory leaks

- [ ] **Compare with backup**
  - [ ] All features still work
  - [ ] UI looks identical
  - [ ] No missing functionality

### Phase 7: Documentation

- [ ] **Update module README**
  - [ ] Add architecture notes
  - [ ] Document lifecycle hooks
  - [ ] Update usage examples

- [ ] **Add migration notes**
  ```markdown
  ## Migration History
  
  **Date**: [YYYY-MM-DD]
  **From**: BaseModule (inheritance)
  **To**: Modern Composition pattern
  **Breaking Changes**: None (backward compatible)
  **Testing**: ✅ All features verified
  ```

- [ ] **Update module metadata**
  - [ ] Increment version number
  - [ ] Add "migrated" tag
  - [ ] Update last modified date

### Phase 8: Finalization

- [ ] **Git commit**
  ```bash
  git add UI/modules_external/module-name/
  git commit -m "refactor(module-name): Migrate to modern composition pattern
  
  - Removed BaseModule inheritance
  - Added composition-based lifecycle hooks
  - Updated manifest to V3.0
  - Added proper cleanup handlers
  - All tests passing ✅"
  ```

- [ ] **Update migration status**
  - [ ] Mark module as ✅ Complete in this document
  - [ ] Increment progress counter
  - [ ] Add completion date

- [ ] **Delete backup (if tests pass)**
  - [ ] Remove `[module-name]-LEGACY.js`
  - [ ] Or move to archive folder

---

## 🎯 Priority Order

### High Priority (Complete First)

1. **inhouse-kanban** - Most used, complex dashboard + sidebar
2. **communication-hub** - Critical for workflow, dashboard + sidebar

### Medium Priority (Complete Second)

3. **stock-management** - Inventory critical
4. **shopify** - E-commerce integration
5. **xero** - Accounting critical
6. **quote-calculator** - Sales tool

### Low Priority (Complete Last)

7. **salesforce** - CRM integration
8. **render-management** - Deployment tool
9. **production-analytics** - Reporting
10. **github** - DevOps tool
11. **database-visualizer** - Admin tool

---

## 📝 Migration Template

Copy this for each module:

```markdown
## Module: [module-name]

**Date Started**: [YYYY-MM-DD]
**Date Completed**: [YYYY-MM-DD]
**Migrated By**: [Name]

### Pre-Migration

- Class Name: `[ClassName]Module`
- Extends: `BaseModule`
- Capabilities: Dashboard [✅/❌], Sidebar [✅/❌]
- Lines of Code: [XXX]
- Event Listeners: [XX]

### Changes Made

1. Converted class to object
2. Added lifecycle hooks:
   - [✅/❌] onDashboardLoad
   - [✅/❌] onSidebarLoad
   - [✅/❌] onUnload
3. Replaced patterns:
   - [XX] container accesses
   - [XX] API calls
   - [XX] event listeners
   - [XX] log statements
4. Updated manifest to V3.0
5. Removed manual instantiation

### Testing Results

- [✅/❌] Dashboard loads
- [✅/❌] Sidebar loads
- [✅/❌] Data operations work
- [✅/❌] UI identical to original
- [✅/❌] No console errors
- [✅/❌] Cleanup works correctly

### Issues Encountered

[None / List issues and solutions]

### Notes

[Any special considerations or learnings]
```

---

## 🚀 Quick Start (First Migration)

### Step 1: Start with Communication Hub

```bash
# 1. Create backup
cd UI/modules_external/communication-hub
cp communication-hub.js communication-hub-LEGACY.js

# 2. Open in editor
code communication-hub.js
```

### Step 2: Follow Checklist

Work through Phase 1-8 for communication-hub module

### Step 3: Test Thoroughly

```javascript
// In browser console
const moduleLoader = window.ModuleLoaderV4;
await moduleLoader.loadModule('communication-hub', 'dashboard');
```

### Step 4: Document & Commit

Update this file with progress, commit changes

---

## 📊 Progress Tracking

### Week 1 (Nov 29 - Dec 5)
- [ ] communication-hub (HIGH)
- [ ] inhouse-kanban (HIGH)

### Week 2 (Dec 6 - Dec 12)
- [ ] stock-management (MEDIUM)
- [ ] shopify (MEDIUM)
- [ ] xero (MEDIUM)

### Week 3 (Dec 13 - Dec 19)
- [ ] quote-calculator (MEDIUM)
- [ ] salesforce (LOW)
- [ ] render-management (LOW)

### Week 4 (Dec 20 - Dec 26)
- [ ] production-analytics (LOW)
- [ ] github (LOW)
- [ ] database-visualizer (LOW)

---

## 🎓 Lessons Learned

### Common Patterns

[To be filled in during migration]

### Gotchas

[To be filled in during migration]

### Best Practices Discovered

[To be filled in during migration]

---

**Last Updated**: November 29, 2025  
**Next Review**: After first 2 migrations complete  
**Status**: Ready to begin ✅

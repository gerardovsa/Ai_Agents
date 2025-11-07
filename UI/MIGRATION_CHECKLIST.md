# UI Standardization Migration Checklist

Version: 1.0.0  
Date: November 7, 2025

## Pre-Migration Steps

- [ ] **Backup your code** - Create git commit before starting migration
- [ ] **Review documentation** - Read `UI_STANDARDIZATION_COMPLETE.md` fully
- [ ] **Test reference page** - Open `test-ui-standards.html` in browser to see all components
- [ ] **Identify modules** - List all modules that need migration

## Installation (One-Time Setup)

- [ ] Add `<link rel="stylesheet" href="/UI/css/ui-standards.css">` to HTML header
- [ ] Add `<script src="/UI/js/ui-builder.js"></script>` before closing `</body>` tag
- [ ] Verify CSS loads AFTER theme.css but BEFORE module-specific CSS
- [ ] Test in browser console: `typeof UIBuilder !== 'undefined'` should be `true`

## Migration By Component Type

### Metric/Stat Cards

**Find and Replace:**

Search for:
```
.stat-card
.metric-card  
.sm-stat-card
.dashboard-metric
```

**Before (Stock Management Pattern):**
```html
<div class="sm-stat-card sm-critical">
    <div class="sm-stat-icon"><i class="fas fa-exclamation-triangle"></i></div>
    <div class="sm-stat-content">
        <div class="sm-stat-label">Critical Stock</div>
        <div class="sm-stat-value">24</div>
    </div>
</div>
```

**After (Standardized):**
```html
<div class="metric-card accent-error">
    <div class="metric-card-header">
        <i class="fas fa-exclamation-triangle metric-card-icon"></i>
        <div class="metric-card-label">Critical Stock</div>
    </div>
    <div class="metric-card-value">24</div>
</div>
```

**Checklist:**
- [ ] Replace `.sm-stat-card` with `.metric-card`
- [ ] Replace `.sm-critical` with `.accent-error`
- [ ] Replace `.sm-warning` with `.accent-warning`
- [ ] Replace `.sm-success` with `.accent-success`
- [ ] Replace `.sm-stat-icon` with `.metric-card-icon`
- [ ] Replace `.sm-stat-label` with `.metric-card-label`
- [ ] Replace `.sm-stat-value` with `.metric-card-value`
- [ ] Wrap icon + label in `.metric-card-header`
- [ ] Test hover effect works (card should lift on hover)
- [ ] Verify accent color border shows on left side

---

### Dashboard Cards

**Find and Replace:**

Search for:
```
<div class="dashboard-card">
<div class="card-header">
```

**Before (Inline Styles):**
```html
<div style="background: #1A1F2E; border: 1px solid #2A3142; padding: 20px;">
    <h3 style="margin-bottom: 16px;">Title</h3>
    <!-- Content -->
</div>
```

**After (Standardized):**
```html
<div class="dashboard-card">
    <div class="dashboard-card-header">
        <div class="dashboard-card-title">
            <i class="fas fa-icon dashboard-card-icon"></i>
            <span>Title</span>
        </div>
    </div>
    <div class="dashboard-card-body">
        <!-- Content -->
    </div>
</div>
```

**Checklist:**
- [ ] Remove inline `style` attributes
- [ ] Use `.dashboard-card` class instead
- [ ] Add `.dashboard-card-header` with title
- [ ] Add `.dashboard-card-body` for content
- [ ] Add `.dashboard-card-footer` if needed
- [ ] Add action buttons in `.dashboard-card-actions` if needed
- [ ] Test responsive behavior on mobile

---

### Subtab Buttons

**Find and Replace:**

Search for:
```
button[data-tab-id]
.tab-button
.subtab
```

**Before (Inconsistent Styling):**
```html
<button style="padding: 10px 20px; border-bottom: 3px solid transparent;" onclick="showTab('overview')">
    <i class="fas fa-home"></i> Overview
</button>
```

**After (Standardized):**
```html
<button class="subtab-btn active" data-tab-id="overview">
    <i class="fas fa-home"></i>
    <span>Overview</span>
</button>
```

**Checklist:**
- [ ] Remove inline `style` attributes
- [ ] Use `.subtab-btn` class
- [ ] Add `.active` to active tab
- [ ] Wrap tabs in `.subtab-container`
- [ ] Wrap label text in `<span>` tag
- [ ] Verify all tabs have same text size (14px)
- [ ] Test active state shows colored bottom border
- [ ] Test hover effect works

---

### Filter Rows

**Find and Replace:**

Search for:
```
.btn.active[data-filter]
style="display: flex; gap: 8px;"
```

**Before (Stock Management Pattern):**
```html
<div style="display: flex; gap: 8px; margin: 20px 0;">
    <button class="btn btn-sm active" data-filter="all" style="padding: 6px 16px;">
        <i class="fas fa-list"></i> All
    </button>
</div>
```

**After (Standardized):**
```html
<div class="filter-row">
    <button class="filter-btn active" data-filter-id="all">
        <i class="fas fa-list"></i>
        <span>All</span>
    </button>
</div>
```

**Checklist:**
- [ ] Replace inline flex div with `.filter-row`
- [ ] Replace `.btn.btn-sm` with `.filter-btn`
- [ ] Remove inline `style` attributes
- [ ] Change `data-filter` to `data-filter-id`
- [ ] Wrap label text in `<span>` tag
- [ ] Test filter toggle functionality
- [ ] Verify consistent spacing between buttons

---

### Grid Layouts

**Find and Replace:**

Search for:
```
style="display: grid; grid-template-columns:"
style="display: flex; gap:"
```

**Before (Causes "Fucked Up" Layouts):**
```html
<div style="display: grid; grid-template-columns: repeat(4, 1fr); gap: 16px;">
    <div class="metric-card">...</div>
</div>
```

**After (Standardized):**
```html
<div class="grid-auto-fit">
    <div class="metric-card">...</div>
</div>
```

**Checklist:**
- [ ] Replace inline grid with `.grid-auto-fit` (most common)
- [ ] Use `.grid-cols-2`, `.grid-cols-3`, `.grid-cols-4` for fixed columns
- [ ] Use `.gap-2`, `.gap-3`, `.gap-4` for custom gap sizes
- [ ] Replace flex layouts for control rows with `.control-row`
- [ ] Test responsive behavior (should wrap on mobile)
- [ ] Verify no overflow issues

---

### Buttons

**Find and Replace:**

Search for:
```
.btn.btn-sm
style="padding:"
```

**Before (Inconsistent):**
```html
<button style="padding: 8px 16px; background: #667eea; color: white;" onclick="save()">
    Save
</button>
```

**After (Standardized):**
```html
<button class="btn btn-primary">
    <i class="fas fa-save"></i>
    <span>Save</span>
</button>
```

**Checklist:**
- [ ] Remove inline `style` attributes
- [ ] Use `.btn` base class
- [ ] Add type class: `.btn-primary`, `.btn-secondary`, etc.
- [ ] Add size class if needed: `.btn-sm`, `.btn-lg`
- [ ] Wrap text in `<span>` tag
- [ ] Add icon with `<i>` tag
- [ ] Test all button states (hover, disabled)
- [ ] Verify consistent sizing across all buttons

---

### Section Headers

**Find and Replace:**

Search for:
```
<h1>, <h2>, <h3> (page titles)
.page-title
.module-title
```

**Before (Inconsistent):**
```html
<h2 style="font-size: 28px; margin-bottom: 16px;">
    Stock Management
</h2>
<p style="color: #9CA3AF;">Manage inventory levels</p>
```

**After (Standardized):**
```html
<div class="section-header">
    <h2 class="section-title">
        <i class="fas fa-warehouse"></i>
        <span>Stock Management</span>
    </h2>
    <p class="section-subtitle">Manage inventory levels</p>
</div>
```

**Checklist:**
- [ ] Wrap title and subtitle in `.section-header`
- [ ] Use `.section-title` for main heading
- [ ] Use `.section-subtitle` for description
- [ ] Add badges in `.section-meta` if needed
- [ ] Test responsive behavior

---

### Expanders

**Find and Replace:**

Search for:
```
.collapsible
.accordion
data-toggle="collapse"
```

**Before (Custom Implementation):**
```html
<div class="collapsible">
    <div class="collapsible-header" onclick="toggle()">
        Settings
    </div>
    <div class="collapsible-content hidden">
        <!-- Content -->
    </div>
</div>
```

**After (Standardized):**
```html
<div class="expander">
    <div class="expander-header">
        <div class="expander-title">
            <i class="fas fa-cog"></i>
            <span>Settings</span>
        </div>
        <i class="fas fa-chevron-down expander-icon"></i>
    </div>
    <div class="expander-content">
        <!-- Content -->
    </div>
</div>
```

**Checklist:**
- [ ] Replace custom classes with `.expander`
- [ ] Add `.expander-header`, `.expander-title`, `.expander-content`
- [ ] Add chevron icon with `.expander-icon`
- [ ] Add `.expanded` class for initially open sections
- [ ] Add toggle functionality (see test-ui-standards.html)
- [ ] Test smooth animation

---

### Form Inputs

**Find and Replace:**

Search for:
```
<input type="text">
<select>
<textarea>
```

**Before (Inconsistent):**
```html
<label>Stock ID</label>
<input type="text" style="width: 100%; padding: 10px; background: #0B0E13;">
```

**After (Standardized):**
```html
<div class="form-group">
    <label class="form-label" for="stock-id">Stock ID</label>
    <input type="text" id="stock-id" class="form-input" placeholder="Enter stock ID...">
</div>
```

**Checklist:**
- [ ] Wrap each input in `.form-group`
- [ ] Use `.form-label` for labels
- [ ] Use `.form-input` for text inputs
- [ ] Use `.form-select` for dropdowns
- [ ] Use `.form-textarea` for textareas
- [ ] Remove inline `style` attributes
- [ ] Add `id` and `for` attributes for accessibility
- [ ] Test focus states (should show colored border)

---

## Module-Specific Migrations

### Stock Management Module

**Priority:**  
**Estimated Time:** 2 hours

**Components to Replace:**
- [ ] 30+ `.sm-stat-card` instances → `.metric-card`
- [ ] 4 filter buttons → `.filter-row` + `.filter-btn`
- [ ] Search input → `.form-input`
- [ ] Grid layouts → `.grid-auto-fit`
- [ ] Chart containers → `.dashboard-card`

**Files to Update:**
- [ ] `stock-management.js`
- [ ] `stock-management.css` (remove redundant styles)

---

### Production Workflow Board

**Priority:**  
**Estimated Time:** 1.5 hours

**Components to Replace:**
- [ ] 5+ `.metric-card` instances (already similar)
- [ ] Kanban columns → `.dashboard-card`
- [ ] Kanban cards → standardized card structure
- [ ] Metric icons → consistent sizing

**Files to Update:**
- [ ] `inhouse-kanban.js`
- [ ] `inhouse-kanban.css`

---

### Business AI Platform

**Priority:**  
**Estimated Time:** 3 hours

**Components to Replace:**
- [ ] 25+ `.stat-card` instances
- [ ] Multiple custom card types
- [ ] Inconsistent button styles
- [ ] Mixed grid layouts

**Files to Update:**
- [ ] `business-ai-platform-v2.html`
- [ ] Module-specific CSS files

---

### Database Visualizer

**Priority:**  
**Estimated Time:** 1 hour

**Components to Replace:**
- [ ] 15+ `.stat-card` instances
- [ ] Dashboard cards
- [ ] Filter buttons

**Files to Update:**
- [ ] `database-visualizer.js`

---

### Transcript Processor

**Priority:**  
**Estimated Time:** 1 hour

**Components to Replace:**
- [ ] 10+ `.metric-card` instances
- [ ] Control rows
- [ ] Form inputs

**Files to Update:**
- [ ] `transcript_processor.html`

---

## Testing Checklist

After migrating each module:

### Visual Testing
- [ ] All metric cards display correctly
- [ ] Accent colors show on left border
- [ ] Hover effects work (cards lift slightly)
- [ ] Text sizes are consistent across subtabs
- [ ] Active states work (subtabs, filters)
- [ ] Grid layouts don't overflow
- [ ] No "fucked up" alignment issues
- [ ] Buttons have consistent sizing
- [ ] Form inputs have focus states

### Responsive Testing
- [ ] Test on mobile (Chrome DevTools device toolbar)
- [ ] Grid wraps correctly on small screens
- [ ] Buttons don't overflow
- [ ] Text is readable on mobile
- [ ] Touch targets are large enough

### Functionality Testing
- [ ] All click handlers still work
- [ ] Filter toggles work
- [ ] Subtab navigation works
- [ ] Expanders open/close smoothly
- [ ] Form inputs accept user input
- [ ] Buttons trigger correct actions

### Accessibility Testing
- [ ] Tab navigation works with keyboard
- [ ] Focus indicators are visible
- [ ] Labels are associated with inputs
- [ ] Buttons have clear text/icons
- [ ] Color contrast meets WCAG standards

---

## Cleanup Checklist

After successful migration:

### CSS Cleanup
- [ ] Remove `.sm-stat-card` styles from module CSS
- [ ] Remove `.stat-card` custom styles
- [ ] Remove `.metric-card` custom styles
- [ ] Remove inline `style` attributes from HTML
- [ ] Remove redundant button styles
- [ ] Remove custom grid layout styles

### JavaScript Cleanup
- [ ] Update dynamic card creation to use `UIBuilder`
- [ ] Remove custom toggle functions (use standard expanders)
- [ ] Remove inline style generation
- [ ] Update event handlers to use standard classes

### Documentation
- [ ] Update module README with new component usage
- [ ] Document any custom extensions
- [ ] Update screenshots if needed
- [ ] Add migration notes to CHANGELOG

---

## Rollback Plan

If migration causes issues:

1. **Revert Git Commit**
   ```bash
   git log --oneline  # Find pre-migration commit
   git revert <commit-hash>
   ```

2. **Remove Standard CSS/JS**
   - Comment out `<link>` to ui-standards.css
   - Comment out `<script>` to ui-builder.js

3. **Restore Module-Specific Styles**
   - Uncomment old CSS
   - Restore inline styles if needed

4. **Report Issues**
   - Document what broke
   - Include screenshots
   - Note browser/version

---

## Success Metrics

Migration is successful when:

- All components render correctly
- No visual regressions
- All functionality works
- Responsive behavior is correct
- Code is cleaner (less duplication)
- Future changes are easier (update one file, not 15)

---

## Timeline Estimate

**Total Time:** ~10-12 hours (depending on module complexity)

**Breakdown:**
- Stock Management: 2 hours
- Workflow Board: 1.5 hours
- Business AI Platform: 3 hours
- Database Visualizer: 1 hour
- Transcript Processor: 1 hour
- Other modules: 2-3 hours
- Testing & cleanup: 2 hours

**Recommendation:** Migrate one module at a time, test thoroughly, then proceed to next.

---

**Last Updated:** November 7, 2025  
**Version:** 1.0.0  
**Status:** Ready for Use

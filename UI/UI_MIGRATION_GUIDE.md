# UI Standardization Quick Migration Guide

**Date**: November 7, 2025  
**Status**: Based on user feedback - Compact metrics, larger subtabs, centered headers, less rounded

---

## ✅ What Changed Based on Feedback

### 1. **Metric Cards** - NOW COMPACT
- ✅ Icon on left (40px, not 48px)
- ✅ Title above value (proper hierarchy)
- ✅ Change and context on same line divided by `|`
- ✅ Left border (3px colored indicator)
- ✅ Less padding (space-3 instead of space-4)
- ✅ Height: ~85px (was ~110px)

**Migration Example:**
```html
<!-- OLD (big cards) -->
<div class="stat-card">
    <div class="stat-icon primary"><i class="fas fa-comments"></i></div>
    <div class="stat-content">
        <div class="stat-label">Messages Sent</div>
        <div class="stat-value">1,234</div>
        <div class="stat-change">+12%</div>
    </div>
</div>

<!-- NEW (compact metric cards) -->
<div class="metric-card success">
    <div class="metric-icon success"><i class="fas fa-comments"></i></div>
    <div class="metric-content">
        <div class="metric-label">Messages Sent</div>
        <div class="metric-value">1,234</div>
        <div class="metric-footer">
            <span class="metric-change positive"><i class="fas fa-arrow-up"></i> +12%</span>
            <span class="divider">|</span>
            <span>vs last month</span>
        </div>
    </div>
</div>
```

### 2. **Subtab Navigation** - NOW LARGER TEXT
- ✅ Font size: 16px (was 14px)
- ✅ Medium weight: 500 (not bold 700)
- ✅ Active state: primary color border-bottom
- ✅ Clean hover states

**Migration Example:**
```html
<!-- OLD -->
<button class="woocommerce-subtab active" data-wc-subtab="orders"
    style="padding: var(--space-3) var(--space-4); font-size: 14px; font-weight: 600;">
    📦 Orders
</button>

<!-- NEW -->
<button class="subtab-btn active">
    <i class="fas fa-box"></i> Orders
</button>
```

### 3. **Section Headers** - NOW CENTERED
- ✅ Centered title with icons on sides
- ✅ Borders extend from center
- ✅ Font size: 20px (--font-size-xl)
- ✅ Medium weight (500, not bold)

**Migration Example:**
```html
<!-- OLD -->
<h2 style="margin-bottom: var(--space-5); font-size: 28px;">
    <i class="fas fa-tachometer-alt"></i> Dashboard Overview
</h2>

<!-- NEW -->
<div class="section-header">
    <h2 class="section-title">
        <i class="fas fa-tachometer-alt"></i>
        Dashboard Overview
    </h2>
    <p class="section-subtitle">Real-time business metrics and insights</p>
</div>
```

### 4. **Buttons** - LESS ROUNDED
- ✅ Border radius: 4px (was 8px or 12px)
- ✅ Consistent sizing (sm, md, lg)
- ✅ Clean variants (primary, secondary, success, error, warning, ghost)

**Migration Example:**
```html
<!-- OLD -->
<button class="btn btn-primary" style="border-radius: 12px;">
    Save
</button>

<!-- NEW -->
<button class="btn">
    <i class="fas fa-save"></i> Save
</button>
```

### 5. **Grid Layouts** - MIN 4 COLUMNS
- ✅ `auto-fit` with minmax(240px, 1fr)
- ✅ Forces 4 columns on screens > 1400px
- ✅ Forces 5 columns on screens > 1800px
- ❌ No more wide 3-column layouts

**Migration Example:**
```html
<!-- OLD -->
<div class="stats-grid" style="grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));">

<!-- NEW -->
<div class="metrics-grid">
    <!-- Automatically 4+ columns on large screens -->
</div>
```

---

## 📋 Complete Component Reference

### Metric Card (Compact)
```html
<div class="metric-card success">
    <div class="metric-icon success">
        <i class="fas fa-dollar-sign"></i>
    </div>
    <div class="metric-content">
        <div class="metric-label">Total Revenue</div>
        <div class="metric-value">$45.2K</div>
        <div class="metric-footer">
            <span class="metric-change positive">
                <i class="fas fa-arrow-up"></i> +8.5%
            </span>
            <span class="divider">|</span>
            <span>This month</span>
        </div>
    </div>
</div>
```

### Subtab Navigation (Larger)
```html
<div class="subtab-nav">
    <button class="subtab-btn active">
        <i class="fas fa-box"></i> Orders
    </button>
    <button class="subtab-btn">
        <i class="fas fa-shopping-bag"></i> Products
    </button>
    <button class="subtab-btn">
        <i class="fas fa-users"></i> Customers
    </button>
</div>
```

### Section Header (Centered)
```html
<div class="section-header">
    <h2 class="section-title">
        <i class="fas fa-chart-line"></i>
        Analytics Dashboard
    </h2>
    <p class="section-subtitle">Track your business performance</p>
</div>
```

### Action Bar (Timeline, Refresh, Filters)
```html
<div class="action-bar">
    <div class="action-bar-left">
        <button class="btn btn-ghost btn-sm">
            <i class="fas fa-calendar"></i> Last 30 Days
        </button>
        <button class="btn btn-ghost btn-sm">
            <i class="fas fa-sync-alt"></i> Refresh
        </button>
    </div>
    <div class="action-bar-center">
        <input type="text" class="form-control" placeholder="Search...">
    </div>
    <div class="action-bar-right">
        <button class="btn btn-primary btn-sm">
            <i class="fas fa-plus"></i> Add New
        </button>
    </div>
</div>
```

### Filter Row
```html
<div class="filter-row">
    <button class="filter-btn active">
        <i class="fas fa-globe"></i> All Items
    </button>
    <button class="filter-btn">
        <i class="fas fa-clock"></i> Pending
    </button>
    <button class="filter-btn">
        <i class="fas fa-check-circle"></i> Completed
    </button>
</div>
```

### Expander
```html
<div class="expander expanded">
    <div class="expander-header" onclick="toggleExpander(this)">
        <div class="expander-title">
            <i class="fas fa-info-circle"></i>
            Order Details
        </div>
        <div class="expander-toggle">
            <i class="fas fa-chevron-down"></i>
        </div>
    </div>
    <div class="expander-content">
        <!-- Content here -->
    </div>
</div>

<script>
function toggleExpander(header) {
    const expander = header.closest('.expander');
    expander.classList.toggle('expanded');
}
</script>
```

---

## 🎨 CSS Custom Properties

All colors and sizes use CSS variables:

```css
:root {
    /* Typography - Updated */
    --font-size-xs: 11px;
    --font-size-sm: 13px;
    --font-size-md: 14px;
    --font-size-lg: 16px;
    --font-size-xl: 20px;      /* For subtabs */
    --font-size-xxl: 28px;     /* For metric values */
    
    /* Border Radius - Less rounded */
    --border-radius-sm: 4px;
    --border-radius-md: 6px;
    --border-radius-lg: 8px;
    
    /* Spacing */
    --space-1: 4px;
    --space-2: 8px;
    --space-3: 12px;
    --space-4: 16px;
    --space-5: 24px;
    
    /* Colors */
    --primary-color: #667eea;
    --success-color: #28a745;
    --error-color: #dc3545;
    --warning-color: #ffc107;
    --info-color: #17a2b8;
}
```

---

## 🚀 How to Apply to Existing Pages

### Step 1: Add CSS
```html
<link rel="stylesheet" href="css/ui-standardization.css">
<link rel="stylesheet" href="css/tabulator-toast.css">
```

### Step 2: Replace Components
Use find/replace to update class names:

| Old Class | New Class |
|-----------|-----------|
| `.stat-card` | `.metric-card` |
| `.stat-icon` | `.metric-icon` |
| `.stat-content` | `.metric-content` |
| `.stat-value` | `.metric-value` |
| `.woocommerce-subtab` | `.subtab-btn` |
| `.wc-filter-btn` | `.filter-btn` |

### Step 3: Update Grids
```html
<!-- Replace all -->
<div class="stats-grid">
<!-- With -->
<div class="metrics-grid">
```

### Step 4: Update Headers
```html
<!-- Replace -->
<h2>Title</h2>
<!-- With -->
<div class="section-header">
    <h2 class="section-title"><i class="fas fa-icon"></i> Title</h2>
</div>
```

---

## ✅ Checklist for Each Page

- [ ] Replace metric/stat cards with compact `metric-card`
- [ ] Update subtab navigation to use `subtab-nav` and `subtab-btn`
- [ ] Center section headers with `section-header`
- [ ] Replace filter buttons with `filter-btn`
- [ ] Use `action-bar` for timeline/refresh/controls
- [ ] Update button border-radius (remove inline styles)
- [ ] Change grid to `metrics-grid` for 4+ column layout
- [ ] Add expanders where appropriate
- [ ] Update toast position to bottom-left
- [ ] Test responsive behavior on mobile

---

## 📱 Responsive Behavior

- **Desktop (>1400px)**: 4 columns minimum
- **Tablet (768-1400px)**: auto-fit based on content
- **Mobile (<768px)**: 1 column, stacked layout

---

## 🎯 Priority Pages to Update

1. **Dashboard (Home Tab)** - Metric cards, section headers
2. **WooCommerce (Sales Tab)** - Subtabs, filters, action bar
3. **Stock Management** - Expanders, metric cards
4. **Analytics** - Charts, metrics grid
5. **Multi-Agent Dashboard** - All components

---

## 💡 Tips

- Use `.flex`, `.flex-col`, `.gap-3` utility classes for quick layouts
- Use `.text-center`, `.text-secondary` for text styling
- Use `.mb-4`, `.mt-3` for margins instead of inline styles
- All components have hover states built-in
- Expanders auto-handle max-height transitions

---

**Questions?** Check `ui-standardization-demo.html` for live examples of all components.

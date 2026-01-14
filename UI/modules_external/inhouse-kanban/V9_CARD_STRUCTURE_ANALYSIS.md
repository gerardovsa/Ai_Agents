# InHouse Kanban V9 Card Structure Analysis

## 📋 Complete Card Anatomy

### HTML Structure (5 Main Sections)

```html
<div class="kanban-card [pulse-border]" 
     data-job-id="12345"
     data-stage-id="8"
     style="[dynamic border/background styles]">
    
    <!-- 1. BANNER (conditional - overdue/due today alerts) -->
    <div class="card-banner">Overdue!</div>
    
    <!-- 2. CARD HEADER (priority icon) -->
    <div class="card-header">
        <div class="card-priority" style="color: #ef4444;">
            <i class="fas fa-exclamation-circle"></i>
        </div>
    </div>
    
    <!-- 3. CARD TITLE (job description) -->
    <div class="card-title">Business Cards - Full Color CMYK</div>
    
    <!-- 4. CARD META (client + status) -->
    <div class="card-meta">
        <div class="card-project">
            <i class="fas fa-building"></i>
            ABC Corporation
        </div>
        <div class="card-status-row">
            <span class="status-badge status-at-risk">AT_RISK</span>
            <span class="card-time">15d in system</span>
        </div>
    </div>
    
    <!-- 5. CARD STAGE TIME (time in current stage) -->
    <div class="card-stage-time stage-warning">
        <i class="fas fa-clock"></i>
        <span class="stage-time-text">3d in Quote</span>
    </div>
    
    <!-- 6. CARD FOOTER (ticket # + cost) -->
    <div class="card-footer">
        <div class="card-tags">
            <span class="card-tag">
                <i class="fas fa-hashtag"></i> 12345
            </span>
            <span class="card-tag">
                <i class="fas fa-dollar-sign"></i> $1,450.00
            </span>
        </div>
    </div>
</div>
```

---

## 🎨 Visual Layout Breakdown

### Card Container
```
┌─────────────────────────────┐
│ [BANNER: "Overdue!"]       │ ← Conditional (red/orange)
├─────────────────────────────┤
│ ⚠️                          │ ← Priority icon (top-right)
├─────────────────────────────┤
│ Business Cards - CMYK       │ ← Title (bold, 14px)
├─────────────────────────────┤
│ 🏢 ABC Corporation         │ ← Client name
│ [AT_RISK] 15d in system    │ ← Status badge + days
├─────────────────────────────┤
│ 🕐 3d in Quote             │ ← Stage time (color-coded)
├─────────────────────────────┤
│ #12345    $1,450.00        │ ← Ticket # + Cost
└─────────────────────────────┘
```

---

## 📐 Spacing & Dimensions

### Card Container
- **Background**: `#0B0E13` (dark gray)
- **Border**: `1px solid #2A3142` (gray border)
- **Border-radius**: `6px`
- **Padding**: `12px` (all sides)
- **Margin-bottom**: `12px` (spacing between cards)
- **Hover effect**: Lifts 2px + blue glow shadow

### Section Spacing
- **Header**: `margin-bottom: 12px`
- **Title**: No explicit margin (flows naturally)
- **Meta section**: `margin-top: 8px`, `padding-top: 8px`, `border-top: 1px solid #2A3142`
- **Stage time**: Flows after meta
- **Footer**: Flows after stage time

---

## 🎯 Content Details

### 1. Banner (Conditional)
**When shown**: Overdue or due today jobs
```javascript
if (job.DateRequired && daysUntilDue <= 0) {
    banner = '<div class="card-banner overdue">Overdue!</div>';
} else if (daysUntilDue <= 1) {
    banner = '<div class="card-banner due-today">Due Today</div>';
}
```

**Styling**:
- Position: absolute, top: 0, left/right: 0
- Font: 11px, uppercase, bold
- Colors: Red (#EF4444) or Orange (#F97316)

---

### 2. Card Header (Priority Icon)
**Content**: FontAwesome icon based on priority score
```javascript
{
    icon: 'fa-exclamation-circle',  // Critical (800-999)
    icon: 'fa-arrow-up',            // High (600-799)
    icon: 'fa-equals',              // Normal (400-599)
    icon: 'fa-arrow-down'           // Low (0-399)
}
```

**Styling**:
- Color: `job.PriorityColorHex` (dynamic)
- Position: Top-right of card
- Size: Inherits from icon size

---

### 3. Card Title
**Content**: `job.ShortJobDesc` (HTML escaped)
```javascript
<div class="card-title">${this.escapeHtml(job.ShortJobDesc || 'No description')}</div>
```

**Styling**:
- Font-size: 13px (implicit from V9)
- Color: `#E5E7EB` (light gray)
- Font-weight: 600 (semi-bold)

---

### 4. Card Meta (Client + Status)

#### 4a. Client Name
```html
<div class="card-project">
    <i class="fas fa-building"></i>
    ABC Corporation
</div>
```
**Styling**:
- Icon + text with gap
- Font-size: 13px
- Color: `#E5E7EB`

#### 4b. Status Row (2 items side-by-side)
```html
<div class="card-status-row">
    <span class="status-badge status-at-risk">AT_RISK</span>
    <span class="card-time">15d in system</span>
</div>
```

**Status Badge Colors**:
- `DELAYED`: Red background (`rgba(239, 68, 68, 0.2)`)
- `AT_RISK`: Orange background (`rgba(249, 115, 22, 0.2)`)
- `ON_TRACK`: Blue background (`rgba(59, 130, 246, 0.2)`)
- `ACTIVE`: Gray background (`rgba(107, 114, 128, 0.2)`)

**Styling**:
- Badge: 3px 8px padding, 4px border-radius, 10px font, uppercase, bold
- Time: 11px font, `#9CA3AF` color

---

### 5. Card Stage Time
**Content**: Time elapsed in current stage
```javascript
<div class="card-stage-time stage-warning">
    <i class="fas fa-clock"></i>
    <span class="stage-time-text">3d in Quote</span>
</div>
```

**Time Classes** (color-coded by duration):
- `stage-normal`: 0-2 days (gray `#9CA3AF`)
- `stage-warning`: 3-5 days (yellow `#FBBF24`)
- `stage-critical`: 6-9 days (orange `#F97316`)
- `stage-overdue`: 10+ days (red `#EF4444`)

**Calculation Logic**:
```javascript
calculateTimeInStage(job) {
    const daysInStage = job.DaysInCurrentStage || 0;
    const stageName = job.CurrentStageName || 'this stage';
    
    let cssClass = 'stage-normal';
    if (daysInStage >= 10) cssClass = 'stage-overdue';
    else if (daysInStage >= 6) cssClass = 'stage-critical';
    else if (daysInStage >= 3) cssClass = 'stage-warning';
    
    return {
        display: `${daysInStage}d in ${stageName}`,
        cssClass: cssClass
    };
}
```

---

### 6. Card Footer (Tags)
**Content**: Ticket number + Cost
```html
<div class="card-footer">
    <div class="card-tags">
        <span class="card-tag">
            <i class="fas fa-hashtag"></i> 12345
        </span>
        <span class="card-tag">
            <i class="fas fa-dollar-sign"></i> $1,450.00
        </span>
    </div>
</div>
```

**Styling**:
- Tags: 11px font, `#9CA3AF` color
- Icon + text with 4px gap
- Display: flex with gap between tags

---

## 🌈 Color Coding System (3 Toggle Controls)

### 1. Border Colors (Priority)
**Toggle**: `showBorderColors`
```javascript
if (colorToggles.showBorderColors) {
    border-left: 4px solid ${job.PriorityColorHex};
}
```

**Priority Colors**:
- Critical: `#EF4444` (red)
- High: `#F97316` (orange)
- Normal: `#3B82F6` (blue)
- Low: `#6B7280` (gray)

---

### 2. Background Colors (Due Date)
**Toggle**: `showBackgroundColors`
```javascript
if (colorToggles.showBackgroundColors && job.DateRequired) {
    const daysUntilDue = calculateDaysUntilDue(job.DateRequired);
    if (daysUntilDue <= 0) {
        background: rgba(239, 68, 68, 0.1);  // Red tint
    } else if (daysUntilDue <= 1) {
        background: rgba(249, 115, 22, 0.1);  // Orange tint
    }
}
```

**Background Tints**:
- Overdue: Red `rgba(239, 68, 68, 0.1)`
- Due Today: Orange `rgba(249, 115, 22, 0.1)`
- Due Soon: Yellow `rgba(251, 191, 36, 0.1)`

---

### 3. Banner Colors (Alerts)
**Toggle**: `showBannerColors`
```javascript
if (colorToggles.showBannerColors && daysUntilDue <= 0) {
    banner = `<div class="card-banner overdue">Overdue!</div>`;
}
```

**Banner Colors**:
- Overdue: Red background `#EF4444`
- Due Today: Orange background `#F97316`

---

## 🔄 Dynamic Styles (Inline)

### Card Style Composition
```javascript
let cardStyle = '';

// 1. Priority border (if enabled)
if (showBorderColors) {
    cardStyle += `border-left: 4px solid ${job.PriorityColorHex} !important; `;
}

// 2. Due date border + background (overrides priority if both enabled)
if (showBackgroundColors && job.DateRequired) {
    const dueDateColors = getDueDateColors(daysUntilDue);
    cardStyle += `border: ${dueDateColors.borderWidth} ${dueDateColors.borderStyle} ${dueDateColors.borderColor} !important; `;
    cardStyle += `background-color: ${dueDateColors.backgroundColor} !important; `;
}

// Applied to card:
<div class="kanban-card" style="${cardStyle}">
```

---

## ⚡ Interactive Features

### 1. Hover Effect
```css
.kanban-card:hover {
    border-color: #00509E !important;
    transform: translateY(-2px) !important;
    box-shadow: 0 4px 12px rgba(0, 80, 158, 0.3) !important;
}
```

### 2. Drag & Drop
```html
<div class="kanban-card"
     draggable="true"
     ondragstart="handleDragStart(event, 12345, 8)">
```

### 3. Click to View Details
```html
<div class="kanban-card"
     onclick="showJobDetailsModal(12345)">
```

---

## 📊 Data Fields Used

| Field | Purpose | Location |
|-------|---------|----------|
| `TicketID` | Job number | Footer tag |
| `ShortJobDesc` | Job description | Card title |
| `ClientName` | Customer name | Card meta (project) |
| `Cost` | Job value | Footer tag ($) |
| `WIPStatus` | Work status | Card meta (badge) |
| `DaysInSystem` | Total age | Card meta (time) |
| `DaysInCurrentStage` | Stage age | Stage time section |
| `CurrentStageName` | Stage name | Stage time section |
| `AIPriorityScore` | Priority | Header icon |
| `PriorityColorHex` | Border color | Card border |
| `DateRequired` | Due date | Background/banner |
| `StageID` | Current stage | Data attribute |

---

## 🎭 CSS Class Reference

### Card Container
- `.kanban-card` - Base card styling
- `.pulse-border` - Pulsing animation for overdue

### Card Sections
- `.card-banner` - Top alert banner
- `.card-header` - Priority icon container
- `.card-priority` - Priority icon wrapper
- `.card-title` - Job description text
- `.card-meta` - Client + status section
- `.card-project` - Client name row
- `.card-status-row` - Status + time row
- `.card-stage-time` - Stage duration section
- `.card-footer` - Bottom tags section
- `.card-tags` - Tag container

### Status Classes
- `.status-badge` - Base status badge
- `.status-delayed` - Red status
- `.status-at-risk` - Orange status
- `.status-on-track` - Blue status
- `.status-active` - Gray status

### Stage Time Classes
- `.stage-normal` - 0-2 days (gray)
- `.stage-warning` - 3-5 days (yellow)
- `.stage-critical` - 6-9 days (orange)
- `.stage-overdue` - 10+ days (red)

---

## 🔍 Key Differences from V4-COMPLETE

### V9 (Original)
✅ **Simpler structure** - 6 sections, no mute settings
✅ **Stage time section** - Dedicated section with color coding
✅ **Card-tags in footer** - Ticket # + Cost side-by-side
✅ **Status row** - Badge + system time together
✅ **No advanced color customization** - Fixed color scheme
✅ **No mute functionality** - All cards visible

### V4-COMPLETE (Current)
❌ **More complex** - Additional mute settings logic
❌ **Metric cards** - Separate metric card system (now removed)
❌ **Advanced color settings** - Customizable colors per priority/due date
❌ **Mute functionality** - Can hide individual cards
❌ **Different field mapping** - API field transformations needed

---

## 💡 Recommendations for V4

### Option A: Restore V9 Simple Structure
- Remove mute settings complexity
- Restore stage time color coding
- Simplify footer tags layout
- Use fixed color scheme

### Option B: Keep V4 with V9 Visual Style
- Keep advanced features (mute, custom colors)
- Apply V9 visual styling (spacing, fonts, layout)
- Restore stage time section
- Keep flexible color system

### Option C: Hybrid Approach
- V9 card layout + spacing
- V4 color customization (collapsible)
- V9 stage time section
- Optional mute functionality (hidden by default)

---

**Analysis Date**: December 1, 2025  
**V9 File Size**: 188.43 KB (4,240 lines)  
**V4 File Size**: ~2,890 lines (after compacting)

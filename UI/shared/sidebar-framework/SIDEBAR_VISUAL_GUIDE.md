# Sidebar Framework - Visual Guide

## 📐 Layout Architecture

### Complete Screen Layout with 60px Offsets

```
┌─────────────────────────────────────────────────────────────────────┐
│                        60px Header                                  │
└─────────────────────────────────────────────────────────────────────┘
┌──────┬────────────────────────────────────────────────────┬─────────┐
│ 60px │                                                    │  60px   │
│ Main │                 Main Content Area                  │ Right   │
│ Side │                                                    │ Spacing │
│ bar  │                                                    │         │
│      │                                                    │         │
│ Menu │                                                    │         │
│      │                                                    │         │
│ ▀▀▀▀ │  ← Module sidebars slide in here                 │         │
│ ▀▀▀▀ │     (60px from edges)                            │         │
│ ▀▀▀▀ │                                                    │         │
│ ▀▀▀▀ │                                                    │         │
└──────┴────────────────────────────────────────────────────┴─────────┘
   ↑                                                             ↑
   60px buffer zone                                         60px buffer
   (for main sidebar menu)                                  (for future UI)
```

---

## 🎯 Toggle Button Positioning

### Default Positions (Initial Load)

```
┌─────────────────────────────────────────────────────────────────────┐
│                        60px Header                                  │
└─────────────────────────────────────────────────────────────────────┘
┌──────┬────────────────────────────────────────────────────┬─────────┐
│ 60px │  80px from top ↓                                   │  60px   │
│ Main │                                                    │         │
│ Side │    ╔═══╗  ← Left Toggle (80px from left)          │    ╔═══╗│
│ bar  │    ║ ● ║     (60px sidebar + 20px spacing)        │    ║ ● ║│
│      │    ╚═══╝                                           │    ╚═══╝│
│ Menu │    80px ↑                                          │    ↑80px│
│      │                                                    │         │
│      │                                                    │  Right  │
│      │                                                    │  Toggle │
│      │                                                    │         │
└──────┴────────────────────────────────────────────────────┴─────────┘
```

**Left Toggle:**
- X: 80px from left (60px main sidebar + 20px spacing)
- Y: 80px from top (60px header + 20px spacing)

**Right Toggle:**
- X: 80px from right (60px spacing + 20px margin)
- Y: 80px from top (60px header + 20px spacing)

---

## 🎨 Sidebar Animation - Left Side

### State 1: Closed (Hidden)
```
┌──────┬────────────────────────────────────────────────────┬─────────┐
│ 60px │                                                    │  60px   │
│ Main │                 Main Content Area                  │         │
│ Side │                                                    │         │
│ bar  │                                                    │         │
│      │    ╔═══╗                                           │         │
│ Menu │    ║ ● ║  ← Inactive toggle                       │         │
│      │    ╚═══╝                                           │         │
│      │                                                    │         │
└──────┴────────────────────────────────────────────────────┴─────────┘
       ↑
       Sidebar hidden beyond left edge
       transform: translateX(calc(-100% - 60px))
```

### State 2: Opening (Sliding In)
```
┌──────┬────────────────────────────────────────────────────┬─────────┐
│ 60px │                                                    │  60px   │
│ Main │ ┌────────────┐                                     │         │
│ Side │ │  Module    │   Main Content Area                 │         │
│ bar  │ │  Sidebar   │                                     │         │
│      │ │            │   ╔═══╗                             │         │
│ Menu │ │  Sliding → │   ║ ● ║  ← Active toggle (blue)    │         │
│      │ │            │   ╚═══╝                             │         │
│      │ └────────────┘                                     │         │
└──────┴────────────────────────────────────────────────────┴─────────┘
       ↑
       Sidebar sliding from left wall towards right
       Animation in progress
```

### State 3: Open (Visible at 60px)
```
┌──────┬────────────────────────────────────────────────────┬─────────┐
│ 60px │┌────────────┐                                      │  60px   │
│ Main ││  Module    │  Main Content Area                   │         │
│ Side ││  Sidebar   │  (pushed right)                      │         │
│ bar  ││            │                                       │         │
│      ││  Content   │  ╔═══╗                               │         │
│ Menu ││  Visible   │  ║ ● ║  ← Active toggle (blue)      │         │
│      ││            │  ╚═══╝                               │         │
│      │└────────────┘                                      │         │
└──────┴────────────────────────────────────────────────────┴─────────┘
       ↑ 60px gap
       Sidebar stopped at 60px from left edge
       transform: translateX(0)
```

---

## 🎨 Sidebar Animation - Right Side

### State 1: Closed (Hidden)
```
┌──────┬────────────────────────────────────────────────────┬─────────┐
│ 60px │                                                    │  60px   │
│ Main │                 Main Content Area                  │         │
│ Side │                                                    │         │
│ bar  │                                                    │   ╔═══╗ │
│      │                                                    │   ║ ● ║ │
│ Menu │                                                    │   ╚═══╝ │
│      │                                                    │    ↑    │
│      │                                                    │ Inactive│
└──────┴────────────────────────────────────────────────────┴─────────┘
                                                                 ↑
                                                     Sidebar hidden beyond right edge
                                                     transform: translateX(calc(100% + 60px))
```

### State 2: Opening (Sliding In)
```
┌──────┬────────────────────────────────────────────────────┬─────────┐
│ 60px │                                                    │  60px   │
│ Main │                              ┌────────────┐        │         │
│ Side │  Main Content Area           │  Module    │        │         │
│ bar  │                              │  Sidebar   │        │         │
│      │                              │            │ ╔═══╗  │         │
│ Menu │                              │  ← Sliding │ ║ ● ║  │         │
│      │                              │            │ ╚═══╝  │         │
│      │                              └────────────┘  ↑     │         │
└──────┴────────────────────────────────────────────────────┴─────────┘
                                                      Active (blue)
                                         Sidebar sliding from right wall towards left
                                         Animation in progress
```

### State 3: Open (Visible at 60px from right)
```
┌──────┬────────────────────────────────────────────────────┬─────────┐
│ 60px │                          ┌────────────┐            │  60px   │
│ Main │  Main Content Area       │  Module    │            │         │
│ Side │  (pushed left)           │  Sidebar   │            │         │
│ bar  │                          │            │            │         │
│      │                          │  Content   │  ╔═══╗     │         │
│ Menu │                          │  Visible   │  ║ ● ║     │         │
│      │                          │            │  ╚═══╝     │         │
│      │                          └────────────┘    ↑       │         │
└──────┴────────────────────────────────────────────────────┴─────────┘
                                               Active (blue)
                                                      60px gap ↑
                                         Sidebar stopped at 60px from right edge
                                         transform: translateX(0)
```

---

## 🔄 Dynamic Side Detection (Drag Behavior)

### Scenario: Dragging Toggle from Left to Right

**Step 1: Initial State (Left Side)**
```
┌──────┬────────────────────────────────────────────────────┬─────────┐
│ 60px │                                                    │  60px   │
│ Main │    ╔═══╗  ← Toggle on left                        │         │
│ Side │    ║ ● ║     Side: 'left'                         │         │
│ bar  │    ╚═══╝                                           │         │
└──────┴────────────────────────────────────────────────────┴─────────┘
```

**Step 2: User Drags Toggle**
```
┌──────┬────────────────────────────────────────────────────┬─────────┐
│ 60px │                                                    │  60px   │
│ Main │              ╔═══╗ → → → → → → →                  │         │
│ Side │              ║ ● ║  Dragging across screen        │         │
│ bar  │              ╚═══╝                                 │         │
└──────┴────────────────────────────────────────────────────┴─────────┘
                       ↑
                 Crossing center line...
```

**Step 3: Toggle Released on Right Half**
```
┌──────┬────────────────────────────────────────────────────┬─────────┐
│ 60px │                                                    │  60px   │
│ Main │                                            ╔═══╗   │         │
│ Side │                                            ║ ● ║   │         │
│ bar  │                                            ╚═══╝   │         │
│      │                                              ↑     │         │
└──────┴────────────────────────────────────────────────────┴─────────┘
                                              System detects:
                                              "Toggle in right half!"
                                              Side: 'left' → 'right'
```

**Step 4: Sidebar Reconfigured for Right Side**
```
┌──────┬────────────────────────────────────────────────────┬─────────┐
│ 60px │                          ┌────────────┐            │  60px   │
│ Main │                          │  Module    │            │         │
│ Side │  Next click opens →      │  Sidebar   │  ╔═══╗    │         │
│ bar  │  from RIGHT now          │            │  ║ ● ║    │         │
│      │                          └────────────┘  ╚═══╝    │         │
└──────┴────────────────────────────────────────────────────┴─────────┘
                                         Sidebar will now:
                                         - Slide in from RIGHT wall
                                         - Stop at 60px from right edge
```

---

## 📏 Measurement Reference

### Key Distances

**Horizontal Offsets:**
```
Left Edge    Main Sidebar    Toggle      Content Area          Toggle    Right Edge
    |            60px          |              ...                |         |
    |─────────────────────────|──────────────────────────────────|────────|
    0px         60px         80px                             80px     100%
                              ↑                                 ↑
                        Default left position           Default right position
```

**Vertical Offsets:**
```
Top Edge
    |
    |──────────────  0px
    |
    |  Header (60px)
    |
    |──────────────  60px (Sidebar top)
    |
    |  20px spacing
    |
    |──────────────  80px (Toggle default Y position)
    |
    |  Content continues...
    |
```

---

## 🎭 Toggle Button States

### Visual State Progression

**1. Inactive (Default)**
```
╔═══════╗
║   ●   ║  Gray background
║       ║  Gray border
╚═══════╝  Gray icon
```

**2. Hover**
```
╔═══════╗
║   ●   ║  Darker background
║       ║  Blue border
╚═══════╝  Blue icon
           + Slight scale (1.05)
           + Enhanced shadow
```

**3. Active (Sidebar Open)**
```
╔═══════╗
║   ●   ║  Blue background (#4F6CFF)
║       ║  Blue border
╚═══════╝  White icon
           + Glow effect (0 0 20px rgba(79, 108, 255, 0.4))
```

---

## 🔍 Z-Index Layering

### Stacking Order (Back to Front)

```
Layer 1: Main Content (z-index: 1)
Layer 2: Main Sidebar Menu (z-index: 1000)
Layer 3: Module Sidebars (z-index: 9000, 9100, 9200, etc.)
Layer 4: Toggle Buttons (z-index: 10000)
Layer 5: Modals/Overlays (z-index: 11000+)
```

**Why Toggle Buttons are Highest:**
- Must always be clickable
- Never covered by sidebars
- User can always close/reposition

---

## 💡 Design Principles

### 1. **60px Grid System**
Everything aligns to 60px increments:
- Header: 60px
- Main sidebar: 60px
- Sidebar offsets: 60px
- Default spacing: 60px + 20px = 80px

### 2. **Smooth Animations**
- Cubic-bezier easing: `cubic-bezier(0.4, 0, 0.2, 1)`
- Duration: 300ms
- Feels natural, not robotic

### 3. **Smart Defaults, User Control**
- Sensible initial positions
- User can override anything
- System adapts to user intent

### 4. **Visual Feedback**
- Hover states: "You can interact"
- Active states: "This is open"
- Smooth transitions: "Things are changing"

---

## 🚀 Real-World Examples

### Example 1: Communication Hub (Left Side)
```
┌──────┬────────────────────────────────────────────────────┬─────────┐
│ 60px │┌────────────┐                                      │  60px   │
│ Main ││ Comm Hub   │  Main Content                        │         │
│ Side ││ ========   │                                       │         │
│ bar  ││ 📧 Gmail   │                                       │         │
│      ││ 📧 Outlook │  ╔═══╗                               │         │
│ Menu ││ 💬 Slack   │  ║📨 ║  ← Communication Hub toggle  │         │
│      ││ 💬 Teams   │  ╚═══╝                               │         │
│      │└────────────┘                                      │         │
└──────┴────────────────────────────────────────────────────┴─────────┘
       ↑ 60px clear of main sidebar menu
```

### Example 2: Synergy Sessions (Right Side)
```
┌──────┬────────────────────────────────────────────────────┬─────────┐
│ 60px │                          ┌────────────┐            │  60px   │
│ Main │  Main Content            │  Synergy   │            │         │
│ Side │                          │  ========  │            │         │
│ bar  │                          │ 🤖 Agent 1 │            │         │
│      │                          │ 🤖 Agent 2 │  ╔═══╗     │         │
│ Menu │                          │ 📊 Tasks   │  ║⚡ ║     │         │
│      │                          │ 📈 Status  │  ╚═══╝     │         │
│      │                          └────────────┘    ↑       │         │
└──────┴────────────────────────────────────────────────────┴─────────┘
                                         Synergy toggle
                                         60px clear of right edge ↑
```

---

**Visual Guide Version:** 1.0  
**Last Updated:** November 29, 2025  
**Companion Document:** SIDEBAR_TOGGLE_IMPROVEMENTS_NOV29.md

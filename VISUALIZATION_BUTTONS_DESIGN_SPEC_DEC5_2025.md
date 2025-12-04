# 🎨 Visualization Action Buttons - Design Specification
**Created:** December 5, 2025  
**Project:** AI_agents (v10 branch)  
**Designer:** GitHub Copilot

---

## 🎯 Design Goals

1. **Discoverability:** Buttons immediately visible but non-intrusive
2. **Consistency:** Match existing AI_agents UI/UX patterns
3. **Accessibility:** High contrast, keyboard navigation, screen reader support
4. **Performance:** Smooth animations, GPU-accelerated transforms
5. **Responsiveness:** Adapt to mobile, tablet, desktop

---

## 📐 Visual Design System

### **Color Palette**

```css
/* Light Mode */
--button-bg: rgba(255, 255, 255, 0.95);
--button-border: #d1d5db;
--button-hover-bg: #f9fafb;
--button-hover-border: #0066cc;
--button-active-bg: #e5e7eb;
--button-text: #374151;
--button-icon: #6b7280;
--button-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);

/* Dark Mode */
--button-bg-dark: rgba(40, 40, 40, 0.95);
--button-border-dark: #4b5563;
--button-hover-bg-dark: #4b5563;
--button-hover-border-dark: #0088ff;
--button-active-bg-dark: #374151;
--button-text-dark: #f3f4f6;
--button-icon-dark: #9ca3af;
--button-shadow-dark: 0 2px 8px rgba(0, 0, 0, 0.4);

/* Accent Colors */
--success-color: #10b981;
--error-color: #ef4444;
--warning-color: #f59e0b;
--info-color: #3b82f6;
```

### **Typography**

```css
--font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'Roboto', 'Oxygen', 
               'Ubuntu', 'Cantarell', 'Fira Sans', 'Droid Sans', 'Helvetica Neue', 
               sans-serif;
--font-size-icon: 16px;
--font-size-label: 13px;
--font-weight-normal: 400;
--font-weight-medium: 500;
--font-weight-bold: 600;
```

### **Spacing & Sizing**

```css
--button-size: 36px;          /* Square buttons */
--button-size-mobile: 44px;   /* Larger for touch */
--button-gap: 6px;            /* Space between buttons */
--button-padding: 8px;        /* Internal padding */
--button-radius: 6px;         /* Rounded corners */
--bar-padding: 8px;           /* Action bar padding */
--bar-radius: 10px;           /* Action bar rounded corners */
```

### **Animation Timing**

```css
--transition-fast: 150ms;
--transition-normal: 250ms;
--transition-slow: 350ms;
--easing: cubic-bezier(0.4, 0, 0.2, 1);
--bounce: cubic-bezier(0.68, -0.55, 0.265, 1.55);
```

---

## 🖼️ Component Designs

### **1. Action Button Bar (In-Message)**

**Position:** Top-right corner of visualization container  
**Visibility:** Appears on hover, persists while buttons are hovered  
**Layout:** Horizontal flex row

```
┌────────────────────────────────────────────────┐
│  [Mermaid Diagram SVG]                         │
│                                                 │
│                          ┌──────────────────┐  │
│                          │ ⧉ A- Aa A+ ↔ 🎨 ⛶│  │
│                          └──────────────────┘  │
│                                                 │
└────────────────────────────────────────────────┘
```

**Visual Specification:**
- **Background:** Semi-transparent white/dark with backdrop-filter blur
- **Border:** 1px solid with subtle shadow
- **Buttons:** 36×36px squares with 6px gap
- **Hover Effect:** Lift 2px, increase shadow, blue border
- **Click Effect:** Scale down briefly (0.95), bounce back

**CSS Implementation:**
```css
.viz-action-bar {
    position: absolute;
    top: 12px;
    right: 12px;
    display: flex;
    align-items: center;
    gap: 6px;
    padding: 8px;
    background: var(--button-bg);
    backdrop-filter: blur(10px);
    -webkit-backdrop-filter: blur(10px);
    border: 1px solid var(--button-border);
    border-radius: 10px;
    box-shadow: var(--button-shadow);
    z-index: 100;
    opacity: 0;
    transform: translateY(-4px);
    transition: opacity 250ms var(--easing), 
                transform 250ms var(--easing);
    pointer-events: none;
}

.viz-container:hover .viz-action-bar,
.viz-action-bar:hover {
    opacity: 1;
    transform: translateY(0);
    pointer-events: auto;
}

.viz-action-btn {
    display: flex;
    align-items: center;
    justify-content: center;
    width: 36px;
    height: 36px;
    padding: 0;
    background: white;
    border: 1px solid var(--button-border);
    border-radius: 6px;
    font-size: 16px;
    color: var(--button-icon);
    cursor: pointer;
    transition: all 150ms var(--easing);
    user-select: none;
}

.viz-action-btn:hover {
    background: var(--button-hover-bg);
    border-color: var(--button-hover-border);
    transform: translateY(-2px);
    box-shadow: 0 4px 8px rgba(0, 0, 0, 0.12);
}

.viz-action-btn:active {
    transform: scale(0.95);
    box-shadow: none;
}

.viz-action-btn:disabled {
    opacity: 0.4;
    cursor: not-allowed;
    transform: none;
}

/* Dark Mode */
.dark-mode .viz-action-bar {
    background: var(--button-bg-dark);
    border-color: var(--button-border-dark);
}

.dark-mode .viz-action-btn {
    background: #2d3748;
    border-color: var(--button-border-dark);
    color: var(--button-icon-dark);
}

.dark-mode .viz-action-btn:hover {
    background: var(--button-hover-bg-dark);
    border-color: var(--button-hover-border-dark);
}
```

---

### **2. Fullscreen Overlay Design**

**Layout:** Fixed viewport overlay with centered content  
**Background:** Dark semi-transparent (rgba(0, 0, 0, 0.95))  
**Content Area:** White background with diagram centered

```
┌──────────────────────────────────────────────────────────┐
│ ░░░░░░░░░░░░░░░░░░ FULLSCREEN OVERLAY ░░░░░░░░░░░░░░░░░░│
│ ░                                                        ░│
│ ░  ┌──────────────────────────────────────────────┐    ░│
│ ░  │ ⛶ Mermaid Diagram          ⧉ A- Aa A+ ↔ 🎨 ⬇│✕  ░│
│ ░  ├──────────────────────────────────────────────┤    ░│
│ ░  │                                              │    ░│
│ ░  │        [Diagram Content - Zoomable]         │    ░│
│ ░  │                                              │    ░│
│ ░  │                125%                          │    ░│
│ ░  │           [- ⊙ + ⊡]                          │    ░│
│ ░  └──────────────────────────────────────────────┘    ░│
│ ░                                                        ░│
│ ░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░│
└──────────────────────────────────────────────────────────┘

Legend:
- Top Bar: Title + Action Buttons + Close
- Center: Diagram (pannable, zoomable)
- Zoom Indicator: Current scale (e.g., "125%")
- Zoom Controls: Zoom out, Reset, Zoom in, Fit to screen
```

**Visual Specification:**

**Header:**
- Height: 60px
- Background: rgba(255, 255, 255, 0.1)
- Border-bottom: 1px solid rgba(255, 255, 255, 0.2)
- Left: Title with fullscreen icon
- Right: Action buttons + Close button

**Content:**
- Background: white
- Centered flexbox
- Cursor: grab (when pannable)

**Zoom Controls:**
- Position: Bottom-center, 20px from edge
- Background: rgba(0, 0, 0, 0.8)
- Border-radius: 20px
- Buttons: 40×40px circular
- Gap: 8px

**Zoom Indicator:**
- Position: Top-center, 20px from edge
- Background: rgba(0, 0, 0, 0.8)
- Color: white
- Padding: 8px 16px
- Border-radius: 20px
- Font: 14px bold

**CSS Implementation:**
```css
.mermaid-fullscreen-overlay {
    position: fixed;
    top: 0;
    left: 0;
    width: 100vw;
    height: 100vh;
    background: rgba(0, 0, 0, 0.95);
    z-index: 10000;
    display: flex;
    flex-direction: column;
    animation: fadeIn 250ms var(--easing);
}

@keyframes fadeIn {
    from { opacity: 0; }
    to { opacity: 1; }
}

.mermaid-fullscreen-container {
    flex: 1;
    display: flex;
    flex-direction: column;
    max-width: 95%;
    max-height: 95%;
    margin: auto;
    background: rgba(255, 255, 255, 0.05);
    border-radius: 12px;
    overflow: hidden;
    box-shadow: 0 20px 60px rgba(0, 0, 0, 0.5);
}

.mermaid-fullscreen-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    height: 60px;
    padding: 0 20px;
    background: rgba(255, 255, 255, 0.1);
    border-bottom: 1px solid rgba(255, 255, 255, 0.2);
}

.mermaid-fullscreen-title {
    display: flex;
    align-items: center;
    gap: 12px;
    font-size: 18px;
    font-weight: 600;
    color: white;
}

.mermaid-fullscreen-title i {
    font-size: 20px;
    opacity: 0.8;
}

.fullscreen-action-bar {
    display: flex;
    gap: 8px;
    align-items: center;
}

.fullscreen-action-btn {
    display: flex;
    align-items: center;
    justify-content: center;
    width: 40px;
    height: 40px;
    background: rgba(255, 255, 255, 0.15);
    border: 1px solid rgba(255, 255, 255, 0.25);
    border-radius: 6px;
    color: white;
    font-size: 18px;
    cursor: pointer;
    transition: all 150ms var(--easing);
}

.fullscreen-action-btn:hover {
    background: rgba(255, 255, 255, 0.25);
    border-color: rgba(255, 255, 255, 0.4);
    transform: translateY(-2px);
}

.fullscreen-close-btn {
    width: 44px;
    height: 44px;
    background: rgba(239, 68, 68, 0.2);
    border-color: rgba(239, 68, 68, 0.4);
    margin-left: 12px;
}

.fullscreen-close-btn:hover {
    background: rgba(239, 68, 68, 0.4);
    border-color: rgba(239, 68, 68, 0.6);
}

.mermaid-fullscreen-content {
    flex: 1;
    position: relative;
    overflow: hidden;
    background: white;
}

.mermaid-fullscreen-viewport {
    position: absolute;
    inset: 0;
    overflow: hidden;
    display: flex;
    align-items: center;
    justify-content: center;
    cursor: grab;
}

.mermaid-fullscreen-viewport:active {
    cursor: grabbing;
}

.mermaid-fullscreen-controls {
    position: absolute;
    bottom: 20px;
    left: 50%;
    transform: translateX(-50%);
    display: flex;
    gap: 10px;
    background: rgba(0, 0, 0, 0.85);
    padding: 12px;
    border-radius: 24px;
    box-shadow: 0 8px 24px rgba(0, 0, 0, 0.4);
    backdrop-filter: blur(10px);
}

.mermaid-fullscreen-controls button {
    width: 40px;
    height: 40px;
    background: rgba(255, 255, 255, 0.2);
    border: 1px solid rgba(255, 255, 255, 0.3);
    border-radius: 50%;
    color: white;
    font-size: 18px;
    font-weight: 700;
    cursor: pointer;
    transition: all 150ms var(--easing);
    display: flex;
    align-items: center;
    justify-content: center;
}

.mermaid-fullscreen-controls button:hover {
    background: rgba(255, 255, 255, 0.3);
    border-color: rgba(255, 255, 255, 0.5);
    transform: scale(1.1);
}

.mermaid-fullscreen-controls button:active {
    transform: scale(0.95);
}

.mermaid-zoom-indicator {
    position: absolute;
    top: 20px;
    left: 50%;
    transform: translateX(-50%);
    background: rgba(0, 0, 0, 0.85);
    color: white;
    padding: 10px 20px;
    border-radius: 24px;
    font-size: 15px;
    font-weight: 600;
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.3);
    backdrop-filter: blur(10px);
    pointer-events: none;
    min-width: 80px;
    text-align: center;
    transition: opacity 250ms var(--easing);
}
```

---

### **3. Notification Toast Design**

**Position:** Top-right corner, fixed  
**Animation:** Slide in from right, fade out  
**Duration:** 3 seconds auto-dismiss

```
┌────────────────────────────────────────┐
│                                        │
│              ┌──────────────────────┐ │
│              │ ✅ Code copied!      │ │
│              └──────────────────────┘ │
│                                        │
│              ┌──────────────────────┐ │
│              │ ❌ Export failed     │ │
│              └──────────────────────┘ │
│                                        │
└────────────────────────────────────────┘
```

**Visual Specification:**
- Width: 280px (min)
- Height: Auto (min 48px)
- Border-left: 4px solid (color based on type)
- Shadow: Medium elevation
- Types: success (green), error (red), warning (orange), info (blue)

**CSS Implementation:**
```css
.viz-notification {
    position: fixed;
    top: 20px;
    right: 20px;
    min-width: 280px;
    background: white;
    border: 1px solid #e5e7eb;
    border-left: 4px solid var(--accent-color);
    border-radius: 8px;
    padding: 14px 18px;
    box-shadow: 0 10px 25px rgba(0, 0, 0, 0.15);
    z-index: 10001;
    opacity: 0;
    transform: translateX(120px);
    transition: all 350ms var(--bounce);
    display: flex;
    align-items: center;
    gap: 12px;
}

.viz-notification.show {
    opacity: 1;
    transform: translateX(0);
}

.viz-notification::before {
    content: '';
    font-size: 20px;
}

.viz-notification-success {
    --accent-color: #10b981;
}

.viz-notification-success::before {
    content: '✅';
}

.viz-notification-error {
    --accent-color: #ef4444;
}

.viz-notification-error::before {
    content: '❌';
}

.viz-notification-warning {
    --accent-color: #f59e0b;
}

.viz-notification-warning::before {
    content: '⚠️';
}

.viz-notification-info {
    --accent-color: #3b82f6;
}

.viz-notification-info::before {
    content: 'ℹ️';
}

.viz-notification-message {
    flex: 1;
    font-size: 14px;
    font-weight: 500;
    color: #374151;
    line-height: 1.4;
}

/* Dark Mode */
.dark-mode .viz-notification {
    background: #1f2937;
    border-color: #374151;
}

.dark-mode .viz-notification-message {
    color: #f3f4f6;
}
```

---

### **4. Modal Dialog Design (Font Size Menu, Theme Picker, Export Options)**

**Layout:** Centered overlay with blurred background  
**Size:** 400px wide (max), auto height

```
┌──────────────────────────────────────────────┐
│ ░░░░░░░░░░░░ MODAL BACKDROP ░░░░░░░░░░░░░░░│
│ ░                                           ░│
│ ░    ┌─────────────────────────────┐       ░│
│ ░    │ Select Font Size        [×] │       ░│
│ ░    ├─────────────────────────────┤       ░│
│ ░    │                             │       ░│
│ ░    │  ○ 🔍 Tiny (10px)           │       ░│
│ ░    │  ○ 📝 Small (12px)          │       ░│
│ ░    │  ● 📄 Normal (14px)         │       ░│
│ ░    │  ○ 📋 Medium (16px)         │       ░│
│ ░    │  ○ 📊 Large (18px)          │       ░│
│ ░    │  ○ 📈 Huge (22px)           │       ░│
│ ░    │  ○ 📐 Giant (26px)          │       ░│
│ ░    │                             │       ░│
│ ░    └─────────────────────────────┘       ░│
│ ░                                           ░│
│ ░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░│
└──────────────────────────────────────────────┘
```

**Visual Specification:**

**Backdrop:**
- Background: rgba(0, 0, 0, 0.5)
- Backdrop-filter: blur(4px)
- Click to close

**Modal Container:**
- Width: 400px max, 90% mobile
- Background: white
- Border-radius: 12px
- Shadow: Large elevation
- Animation: Scale up + fade in

**Header:**
- Height: 56px
- Padding: 16px 20px
- Border-bottom: 1px solid #e5e7eb
- Title: 16px bold
- Close button: Top-right, 32×32px

**Content:**
- Padding: 20px
- Max-height: 70vh
- Overflow: auto

**Options:**
- Each option: 48px height
- Padding: 12px 16px
- Border-radius: 6px
- Hover: Light gray background
- Selected: Blue background, white text
- Icon + Label layout

**CSS Implementation:**
```css
.viz-modal-backdrop {
    position: fixed;
    inset: 0;
    background: rgba(0, 0, 0, 0.5);
    backdrop-filter: blur(4px);
    -webkit-backdrop-filter: blur(4px);
    z-index: 9999;
    display: flex;
    align-items: center;
    justify-content: center;
    padding: 20px;
    animation: backdropFadeIn 250ms var(--easing);
}

@keyframes backdropFadeIn {
    from {
        opacity: 0;
    }
    to {
        opacity: 1;
    }
}

.viz-modal {
    width: 100%;
    max-width: 400px;
    background: white;
    border-radius: 12px;
    box-shadow: 0 20px 60px rgba(0, 0, 0, 0.3);
    animation: modalScaleIn 300ms var(--bounce);
    overflow: hidden;
}

@keyframes modalScaleIn {
    from {
        opacity: 0;
        transform: scale(0.9) translateY(-20px);
    }
    to {
        opacity: 1;
        transform: scale(1) translateY(0);
    }
}

.viz-modal-header {
    display: flex;
    align-items: center;
    justify-content: space-between;
    height: 56px;
    padding: 0 20px;
    border-bottom: 1px solid #e5e7eb;
}

.viz-modal-title {
    font-size: 16px;
    font-weight: 600;
    color: #111827;
}

.viz-modal-close {
    width: 32px;
    height: 32px;
    display: flex;
    align-items: center;
    justify-content: center;
    background: transparent;
    border: none;
    border-radius: 6px;
    color: #6b7280;
    font-size: 20px;
    cursor: pointer;
    transition: all 150ms var(--easing);
}

.viz-modal-close:hover {
    background: #f3f4f6;
    color: #111827;
}

.viz-modal-content {
    padding: 20px;
    max-height: 70vh;
    overflow-y: auto;
}

.viz-option-list {
    display: flex;
    flex-direction: column;
    gap: 8px;
}

.viz-option {
    display: flex;
    align-items: center;
    gap: 12px;
    height: 48px;
    padding: 0 16px;
    background: transparent;
    border: 1px solid transparent;
    border-radius: 6px;
    cursor: pointer;
    transition: all 150ms var(--easing);
    font-size: 14px;
    color: #374151;
}

.viz-option:hover {
    background: #f9fafb;
    border-color: #e5e7eb;
}

.viz-option.selected {
    background: #3b82f6;
    border-color: #3b82f6;
    color: white;
}

.viz-option-icon {
    font-size: 20px;
    width: 24px;
    text-align: center;
}

.viz-option-label {
    flex: 1;
    font-weight: 500;
}

.viz-option-value {
    font-size: 13px;
    opacity: 0.7;
}

/* Dark Mode */
.dark-mode .viz-modal {
    background: #1f2937;
}

.dark-mode .viz-modal-header {
    border-color: #374151;
}

.dark-mode .viz-modal-title {
    color: #f3f4f6;
}

.dark-mode .viz-option {
    color: #e5e7eb;
}

.dark-mode .viz-option:hover {
    background: #374151;
    border-color: #4b5563;
}
```

---

### **5. Button Icon Reference**

**Copy Code:**
```
Symbol: ⧉
Unicode: U+29C9
Alt: 📋 (clipboard emoji)
```

**Font Size:**
```
Smaller: A-
Menu: Aa
Larger: A+
```

**Direction:**
```
Symbol: ↔
Unicode: U+2194 (left-right arrow)
Alt: ⇄ (U+21C4)
```

**Themes:**
```
Symbol: 🎨
Unicode: U+1F3A8 (artist palette)
Alt: 🌈 (rainbow), ⚙️ (gear)
```

**Spacing:**
```
Compact: ⊟ (U+229F)
Normal: ⊡ (U+22A1)
Wide: ⊞ (U+229E)
Alt: ⊟⊡⊞ or ▭▢▭
```

**Export:**
```
Symbol: ⬇
Unicode: U+2B07 (down arrow)
Alt: 💾 (floppy disk), 📥 (inbox tray)
```

**Fullscreen:**
```
Symbol: ⛶
Unicode: U+26F6
Alt: ⛶ ⛶ ◱ ⤢
```

**Zoom:**
```
In: 🔍+ or + or ⊕
Out: 🔍- or - or ⊖
Reset: ⊙ or ○ or 100%
Fit: ⊡ or ⊞ or ▣
```

**Close:**
```
Symbol: ✕
Unicode: U+2715
Alt: × (U+00D7), ⊗ (U+2297)
```

---

## 📱 Responsive Design

### **Mobile (< 600px)**

**Changes:**
- Action bar: Larger buttons (44×44px for touch)
- Button gap: 8px
- Icon-only buttons (no labels)
- Fullscreen: Controls at bottom, larger tap targets
- Modal: Full-width with safe area insets
- Notification: Full-width, top of screen

```css
@media (max-width: 600px) {
    .viz-action-btn {
        width: 44px;
        height: 44px;
        font-size: 18px;
    }
    
    .viz-action-bar {
        gap: 8px;
        padding: 10px;
    }
    
    .mermaid-fullscreen-controls button {
        width: 52px;
        height: 52px;
        font-size: 20px;
    }
    
    .viz-modal {
        width: 100%;
        max-width: 100%;
        margin: 0;
        border-radius: 12px 12px 0 0;
        max-height: 90vh;
    }
    
    .viz-notification {
        top: 10px;
        right: 10px;
        left: 10px;
        transform: translateY(-120px);
    }
    
    .viz-notification.show {
        transform: translateY(0);
    }
}
```

### **Tablet (600px - 1024px)**

**Changes:**
- Normal button size (36×36px)
- Optimized spacing
- Modal: Centered, max-width 500px

### **Desktop (> 1024px)**

**Changes:**
- Full feature set
- Hover states enabled
- Keyboard shortcuts active
- Tooltips on hover (200ms delay)

---

## ♿ Accessibility Features

### **Keyboard Navigation**

```javascript
// Action Bar: Tab through buttons
document.addEventListener('keydown', (e) => {
    if (e.key === 'Tab' && e.target.closest('.viz-action-bar')) {
        // Focus next button
    }
    
    // Fullscreen: ESC to close
    if (e.key === 'Escape' && document.querySelector('.mermaid-fullscreen-overlay')) {
        closeFullscreen();
    }
    
    // Zoom shortcuts
    if (e.ctrlKey || e.metaKey) {
        if (e.key === '+' || e.key === '=') {
            e.preventDefault();
            zoomIn();
        } else if (e.key === '-') {
            e.preventDefault();
            zoomOut();
        } else if (e.key === '0') {
            e.preventDefault();
            resetZoom();
        }
    }
});
```

### **ARIA Labels**

```html
<button 
    class="viz-action-btn" 
    data-action="copy"
    aria-label="Copy diagram code to clipboard"
    title="Copy Code">
    ⧉
</button>

<button 
    class="viz-action-btn" 
    data-action="fontUp"
    aria-label="Increase font size"
    title="Larger Font (A+)">
    A+
</button>

<div 
    class="mermaid-fullscreen-overlay" 
    role="dialog" 
    aria-modal="true"
    aria-labelledby="fullscreen-title">
    <h2 id="fullscreen-title" class="sr-only">Diagram Fullscreen View</h2>
    <!-- Content -->
</div>
```

### **Screen Reader Support**

```html
<span class="sr-only">
    Diagram controls: 
    Copy code, adjust font size, toggle direction, change theme, 
    export as image, or view in fullscreen
</span>

<div role="status" aria-live="polite" class="sr-only">
    <span id="zoom-status"></span>
</div>

<script>
    function updateZoom(newZoom) {
        document.getElementById('zoom-status').textContent = 
            `Zoom level: ${Math.round(newZoom * 100)} percent`;
    }
</script>
```

### **Focus Indicators**

```css
.viz-action-btn:focus-visible {
    outline: 2px solid #3b82f6;
    outline-offset: 2px;
    box-shadow: 0 0 0 4px rgba(59, 130, 246, 0.2);
}

.viz-option:focus-visible {
    outline: 2px solid #3b82f6;
    outline-offset: -2px;
}
```

---

## 🎭 Animation States

### **Button Click Feedback**

```css
@keyframes buttonClick {
    0% { transform: scale(1); }
    50% { transform: scale(0.95); }
    100% { transform: scale(1); }
}

.viz-action-btn.clicked {
    animation: buttonClick 200ms var(--easing);
}
```

### **Success Pulse**

```css
@keyframes successPulse {
    0% { 
        background: #10b981; 
        transform: scale(1);
    }
    50% { 
        background: #34d399; 
        transform: scale(1.05);
    }
    100% { 
        background: #10b981; 
        transform: scale(1);
    }
}

.viz-action-btn.success {
    animation: successPulse 400ms var(--easing);
}
```

### **Loading Spinner**

```css
@keyframes spin {
    from { transform: rotate(0deg); }
    to { transform: rotate(360deg); }
}

.viz-action-btn.loading::after {
    content: '';
    position: absolute;
    width: 20px;
    height: 20px;
    border: 2px solid rgba(59, 130, 246, 0.3);
    border-top-color: #3b82f6;
    border-radius: 50%;
    animation: spin 600ms linear infinite;
}
```

---

## 🧩 Component Hierarchy

```
VisualizationContainer
├── MermaidDiagram (SVG)
└── VizActionBar
    ├── CopyButton
    ├── FontSizeDownButton
    ├── FontSizeMenuButton
    │   └── FontSizeModal
    │       └── FontSizeOptionList
    ├── FontSizeUpButton
    ├── DirectionToggleButton
    ├── ThemeButton
    │   └── ThemePickerModal
    │       └── ThemeOptionGrid
    ├── SpacingCompactButton (fullscreen only)
    ├── SpacingNormalButton (fullscreen only)
    ├── SpacingWideButton (fullscreen only)
    ├── ExportButton
    │   └── ExportModal
    │       └── ExportFormatOptions
    └── FullscreenButton
        └── FullscreenOverlay
            ├── FullscreenHeader
            │   ├── Title
            │   ├── ActionBar (duplicated)
            │   └── CloseButton
            ├── FullscreenContent
            │   └── Viewport (pannable, zoomable)
            │       └── DiagramClone
            ├── ZoomIndicator
            └── ZoomControls
                ├── ZoomOutButton
                ├── ZoomResetButton
                ├── ZoomInButton
                └── FitToScreenButton
```

---

## 🎨 Design Tokens (CSS Variables)

```css
:root {
    /* Colors */
    --viz-btn-bg: rgba(255, 255, 255, 0.95);
    --viz-btn-bg-hover: #f9fafb;
    --viz-btn-bg-active: #e5e7eb;
    --viz-btn-border: #d1d5db;
    --viz-btn-border-hover: #0066cc;
    --viz-btn-text: #374151;
    --viz-btn-icon: #6b7280;
    
    /* Spacing */
    --viz-btn-size: 36px;
    --viz-btn-gap: 6px;
    --viz-btn-padding: 8px;
    --viz-btn-radius: 6px;
    --viz-bar-padding: 8px;
    --viz-bar-radius: 10px;
    
    /* Typography */
    --viz-font-size: 14px;
    --viz-font-size-icon: 16px;
    --viz-font-weight: 500;
    
    /* Shadows */
    --viz-shadow-sm: 0 2px 8px rgba(0, 0, 0, 0.1);
    --viz-shadow-md: 0 4px 16px rgba(0, 0, 0, 0.15);
    --viz-shadow-lg: 0 10px 30px rgba(0, 0, 0, 0.2);
    
    /* Transitions */
    --viz-transition-fast: 150ms cubic-bezier(0.4, 0, 0.2, 1);
    --viz-transition-normal: 250ms cubic-bezier(0.4, 0, 0.2, 1);
    --viz-transition-slow: 350ms cubic-bezier(0.4, 0, 0.2, 1);
    
    /* Z-index */
    --viz-z-actionbar: 100;
    --viz-z-modal: 9999;
    --viz-z-fullscreen: 10000;
    --viz-z-notification: 10001;
}

[data-theme="dark"] {
    --viz-btn-bg: rgba(40, 40, 40, 0.95);
    --viz-btn-bg-hover: #4b5563;
    --viz-btn-bg-active: #374151;
    --viz-btn-border: #4b5563;
    --viz-btn-border-hover: #0088ff;
    --viz-btn-text: #f3f4f6;
    --viz-btn-icon: #9ca3af;
}
```

---

## 🧪 Interactive Prototype (HTML/CSS/JS)

```html
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Visualization Action Buttons - Prototype</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            padding: 40px;
            background: #f3f4f6;
        }
        
        .viz-container {
            position: relative;
            max-width: 800px;
            margin: 0 auto;
            background: white;
            border: 1px solid #e5e7eb;
            border-radius: 12px;
            padding: 40px;
            box-shadow: 0 4px 16px rgba(0, 0, 0, 0.08);
        }
        
        .viz-placeholder {
            width: 100%;
            height: 400px;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            border-radius: 8px;
            display: flex;
            align-items: center;
            justify-content: center;
            color: white;
            font-size: 24px;
            font-weight: 600;
        }
        
        .viz-action-bar {
            position: absolute;
            top: 52px;
            right: 52px;
            display: flex;
            gap: 6px;
            padding: 8px;
            background: rgba(255, 255, 255, 0.95);
            backdrop-filter: blur(10px);
            border: 1px solid #d1d5db;
            border-radius: 10px;
            box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
            opacity: 0;
            transform: translateY(-4px);
            transition: opacity 250ms ease, transform 250ms ease;
        }
        
        .viz-container:hover .viz-action-bar,
        .viz-action-bar:hover {
            opacity: 1;
            transform: translateY(0);
        }
        
        .viz-action-btn {
            width: 36px;
            height: 36px;
            background: white;
            border: 1px solid #d1d5db;
            border-radius: 6px;
            font-size: 16px;
            color: #6b7280;
            cursor: pointer;
            transition: all 150ms ease;
            display: flex;
            align-items: center;
            justify-content: center;
        }
        
        .viz-action-btn:hover {
            background: #f9fafb;
            border-color: #0066cc;
            transform: translateY(-2px);
            box-shadow: 0 4px 8px rgba(0, 0, 0, 0.12);
        }
        
        .viz-action-btn:active {
            transform: scale(0.95);
        }
        
        .viz-notification {
            position: fixed;
            top: 20px;
            right: 20px;
            min-width: 280px;
            background: white;
            border: 1px solid #e5e7eb;
            border-left: 4px solid #10b981;
            border-radius: 8px;
            padding: 14px 18px;
            box-shadow: 0 10px 25px rgba(0, 0, 0, 0.15);
            display: flex;
            align-items: center;
            gap: 12px;
            opacity: 0;
            transform: translateX(120px);
            transition: all 350ms cubic-bezier(0.68, -0.55, 0.265, 1.55);
        }
        
        .viz-notification.show {
            opacity: 1;
            transform: translateX(0);
        }
        
        .viz-notification::before {
            content: '✅';
            font-size: 20px;
        }
    </style>
</head>
<body>
    <div class="viz-container">
        <div class="viz-placeholder">
            Mermaid Diagram
        </div>
        
        <div class="viz-action-bar">
            <button class="viz-action-btn" title="Copy Code" onclick="showNotification()">⧉</button>
            <button class="viz-action-btn" title="Smaller Font">A-</button>
            <button class="viz-action-btn" title="Font Size Menu">Aa</button>
            <button class="viz-action-btn" title="Larger Font">A+</button>
            <button class="viz-action-btn" title="Toggle Direction">↔</button>
            <button class="viz-action-btn" title="Color Themes">🎨</button>
            <button class="viz-action-btn" title="Export">⬇</button>
            <button class="viz-action-btn" title="Fullscreen">⛶</button>
        </div>
    </div>
    
    <div id="notification" class="viz-notification">
        <span>Code copied to clipboard!</span>
    </div>
    
    <script>
        function showNotification() {
            const notification = document.getElementById('notification');
            notification.classList.add('show');
            setTimeout(() => {
                notification.classList.remove('show');
            }, 3000);
        }
    </script>
</body>
</html>
```

---

## ✅ Design Checklist

- [x] Color palette defined (light + dark mode)
- [x] Typography system established
- [x] Spacing/sizing tokens created
- [x] Button states designed (default, hover, active, disabled)
- [x] Action bar layout specified
- [x] Fullscreen overlay designed
- [x] Modal dialog patterns created
- [x] Notification toast designed
- [x] Mobile responsive breakpoints defined
- [x] Accessibility features included
- [x] Animation timings specified
- [x] Icon reference completed
- [x] Component hierarchy mapped
- [x] CSS variables documented
- [x] Interactive prototype created

---

## 📝 Implementation Notes

**Priority Order:**
1. **Action Bar Structure** - Foundation for all buttons
2. **Copy Button** - Simplest, highest value
3. **Font Size System** - Re-uses existing controller
4. **Fullscreen Mode** - Most impactful UX improvement
5. **Export Functionality** - Professional feature
6. **Theme Picker** - Nice-to-have customization
7. **Direction Toggle** - Simple utility
8. **Spacing Controls** - Advanced feature

**Estimated Implementation:**
- Design system setup: 2 hours
- Action bar component: 3 hours
- Individual buttons: 1-2 hours each
- Fullscreen overlay: 5 hours
- Testing & polish: 4 hours

**Total: ~20-25 hours for complete system**

---

**Design Complete** ✅  
**Ready for Development** ✅  
**Date:** December 5, 2025

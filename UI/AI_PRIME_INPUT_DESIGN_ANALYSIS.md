# AI Prime Input Area - Design & Intent Analysis

**Date:** November 15, 2025  
**Purpose:** Document the design philosophy and architecture of the AI Prime chat input area  
**Status:** Complete Analysis

---

## 🎯 Overview

The **AI Prime Input Area** is the primary user interface for interacting with the AI agent. It's designed as a **multi-layered, context-aware input system** with several sophisticated features working together harmoniously.

---

## 📐 Architecture Breakdown

### **Container Hierarchy**

```
.ai-chat-input-container (position: absolute, bottom: 0)
├── .user-feedback-container (collapsible feedback area)
│   ├── .feedback-header
│   ├── .feedback-body
│   │   ├── .feedback-textarea
│   │   └── .feedback-quick-buttons
│   │       ├── Pause button
│   │       ├── Stop button
│   │       ├── Explain button
│   │       └── Send feedback button
│   │
└── .ai-chat-input-wrapper (main input area)
    ├── .ai-chat-attached-files (file chips)
    └── .ai-chat-input-controls (textarea + buttons)
        ├── .ai-chat-center (textarea wrapper)
        │   └── textarea.ai-chat-input
        │
        └── .ai-chat-right-buttons (vertical stack of 5 buttons)
            ├── Prompt Library button
            ├── Auto-scroll toggle button
            ├── Feedback toggle button
            ├── Attach files button
            └── Send message button
```

---

## 🎨 Design Philosophy

### **1. Transparency-First Approach**

**Intent:** Maintain visual focus on the conversation, not the input area.

```css
.ai-chat-input-container {
    background: transparent;
    pointer-events: none;  /* Ghost container */
}

.ai-chat-input-wrapper {
    pointer-events: auto;  /* Only input area is interactive */
}
```

**Why?**
- Input area "floats" above the chat messages
- No visual clutter when not in use
- User focuses on conversation, not UI chrome

---

### **2. Progressive Disclosure**

**Intent:** UI elements appear only when needed, reducing cognitive load.

#### **Resting State (No Interaction)**
```
┌─────────────────────────────────────────────┐
│                                             │
│  [transparent textarea with faint border]   │
│                                             │
│  [🔗] ← Almost invisible (opacity: 0.5)    │
│  [💬]                                       │
│  [📎]                                       │
│  [✈️] ← Barely visible (opacity: 0.5)     │
│                                             │
└─────────────────────────────────────────────┘
```

#### **Hover State (User Approaching)**
```css
.ai-chat-input-container:hover .ai-chat-input {
    background: rgba(0, 0, 0, 0.60);
    border-color: rgba(255, 255, 255, 0.18);
    box-shadow: 0 6px 20px rgba(0, 0, 0, 0.45);
}

.ai-chat-input-container:hover .ai-chat-attach-btn,
.ai-chat-input-container:hover .ai-chat-feedback-btn {
    border: 1px solid var(--border-default);
    color: var(--text-primary);
}

.ai-chat-input-container:hover .ai-chat-send-btn {
    background: var(--accent-primary);
    color: white;
    opacity: 1;  /* Becomes fully visible */
}
```

**Result:**
```
┌─────────────────────────────────────────────┐
│                                             │
│  [dark semi-transparent textarea]           │
│  [with soft shadow and glow]                │
│                                             │
│  [🔗] ← Fully visible with borders         │
│  [💬]                                       │
│  [📎]                                       │
│  [✈️] ← Bright blue, fully opaque         │
│                                             │
└─────────────────────────────────────────────┘
```

---

### **3. Vertical Button Stack (Right Side)**

**Intent:** Maximize textarea width while keeping all controls accessible.

```css
.ai-chat-right-buttons {
    display: flex;
    flex-direction: column;
    gap: 6px;
    width: 32px;  /* Fixed width */
}
```

**Button Order (Top to Bottom):**

| Button | Icon | Purpose | Visual State |
|--------|------|---------|--------------|
| **Prompt Library** | ⚡ | Insert pre-made prompts | Transparent → Bordered on hover |
| **Auto-scroll** | ⏬ | Toggle auto-scroll to bottom | Active state when enabled |
| **Feedback** | 💬 | Toggle feedback container | Transparent → Bordered on hover |
| **Attach Files** | 📎 | Upload PDFs/images | Transparent → Bordered on hover |
| **Send Message** | ✈️ | Submit message | Blue accent, glows on hover |

**Why This Order?**
1. **Prompt Library (Top)** - Used first when composing message
2. **Auto-scroll (Middle)** - Toggle setting, less frequently used
3. **Feedback (Middle)** - Special feature, less common
4. **Attach Files (Bottom)** - Pre-send action
5. **Send Message (Bottom)** - Final action, most prominent

---

### **4. Button State System**

**Three Visual States for Utility Buttons:**

#### **State 1: Dormant (No Hover)**
```css
.ai-chat-attach-btn {
    background: transparent;
    color: rgba(139, 148, 158, 0.5);  /* Very muted */
    border: none;
}
```
- Almost invisible
- User isn't distracted

#### **State 2: Available (Container Hover)**
```css
.ai-chat-input-container:hover .ai-chat-attach-btn {
    background: transparent;
    border: 1px solid var(--border-default);
    color: var(--text-primary);
}
```
- Shows borders and full color
- "I'm here if you need me"

#### **State 3: Active (Button Hover)**
```css
.ai-chat-attach-btn:hover {
    background: transparent !important;
    color: var(--accent-primary);
    border-color: var(--accent-primary) !important;
    transform: scale(1.05);
}
```
- Accent color (blue)
- Slight scale-up
- Clear interactive feedback

**Send Button Has Different States:**

```css
/* Dormant */
.ai-chat-send-btn {
    opacity: 0.5;
    border: 1px solid var(--accent-primary);
    color: var(--accent-primary);
}

/* Container Hover */
.ai-chat-input-container:hover .ai-chat-send-btn {
    background: var(--accent-primary);
    color: white;
    opacity: 1;
}

/* Button Hover */
.ai-chat-send-btn:hover {
    transform: scale(1.1);
    box-shadow: 0 2px 8px rgba(88, 166, 255, 0.4);
}
```

**Why Different?**
- Send is the **primary action**
- Always visible (even when faint)
- Blue color signals "go"
- Most prominent on hover

---

### **5. Feedback Container (Collapsible)**

**Intent:** Allow in-flight guidance to AI without blocking input area.

```css
.user-feedback-container {
    display: none;
    flex-direction: column;
    opacity: 0;
    max-height: 0;
    transition: all 0.3s ease;
}

.user-feedback-container.active {
    display: flex;
    opacity: 1;
    max-height: 300px;
}
```

**Position:** **Above** the main input area (not overlaying it)

**Features:**
- ✅ Expand/collapse animation (smooth 300ms transition)
- ✅ Separate textarea for feedback
- ✅ Quick action buttons (Pause, Stop, Explain)
- ✅ Dedicated send button
- ✅ Close button in header

**Use Case:**
```
User sends long request: "Analyze these 50 emails..."
AI starts processing...
User realizes: "Wait, I only need legal emails!"
User clicks feedback button
Feedback area expands
User types: "Focus on legal emails only"
Feedback sent WITHOUT interrupting AI
```

---

### **6. File Attachment System**

**Design:** Chips appear **above** the textarea when files are attached.

```css
.ai-chat-attached-files {
    display: flex;
    flex-wrap: wrap;
    gap: var(--space-2);
    margin-bottom: var(--space-2);
    order: -1;  /* Always appears first */
}
```

**File Chip Structure:**
```
┌────────────────────────────┐
│ 📄 document.pdf (245KB) ×  │
└────────────────────────────┘
   ↑        ↑           ↑
  icon    name        remove
```

**Supported Files:**
- PDF (max 32MB)
- Images: PNG, JPG, GIF, WebP (max 5MB)

**Interaction:**
- Click **×** to remove individual file
- Drag & drop onto textarea
- Click **📎** button to browse

---

### **7. Textarea Auto-Expand**

**Intent:** Grow textarea as user types, up to a limit.

```css
.ai-chat-input {
    min-height: 80px;
    max-height: 300px;
    overflow-y: auto;
    resize: none;
}
```

**Behavior:**
- Starts at 80px (3-4 lines)
- Expands to fit content
- Caps at 300px (scrollbar appears)
- User can't manually resize (prevents layout breaks)

**Why Auto-Expand?**
- Multi-line prompts are common
- Manual scrolling is awkward
- Fixed height wastes space or clips content

---

### **8. Scrollbar Styling (Dual Standard)**

**Intent:** Beautiful, consistent scrollbars across browsers.

**Webkit (Chrome, Safari, Edge):**
```css
.ai-chat-input::-webkit-scrollbar {
    width: 8px;
}

.ai-chat-input::-webkit-scrollbar-thumb {
    background: var(--border-default);
    border-radius: 4px;
}

.ai-chat-input::-webkit-scrollbar-thumb:hover {
    background: var(--accent-primary);
}
```

**Firefox:**
```css
.ai-chat-input {
    scrollbar-color: var(--border-default) transparent;
    scrollbar-width: thin;
}

.ai-chat-input:hover {
    scrollbar-color: var(--accent-primary) transparent;
}
```

**Result:** Thin, subtle scrollbar that turns blue on hover (both standards).

---

### **9. Drag-and-Drop Visual Feedback**

**Intent:** Clear visual indication when dragging files over textarea.

```css
.ai-chat-input.drag-over {
    border-color: var(--accent-primary);
    background: rgba(88, 166, 255, 0.05);
}
```

**Behavior:**
```
Normal state:
┌─────────────────────────┐
│                         │
│  Type your message...   │
│                         │
└─────────────────────────┘

Dragging file over:
┌═════════════════════════┐  ← Blue border
│░░░░░░░░░░░░░░░░░░░░░░░░░│  ← Light blue tint
│  Drop files here        │
│░░░░░░░░░░░░░░░░░░░░░░░░░│
└═════════════════════════┘
```

---

### **10. Prompt Library Integration**

**Location:** Top button in right stack (⚡ icon)

**Design:** Matches other utility buttons in style.

```css
.ai-chat-prompt-library-btn {
    width: 32px;
    height: 32px;
    background: transparent;
    color: rgba(139, 148, 158, 0.5);
    border: 1px solid transparent;
}

.ai-chat-input-container:hover .ai-chat-prompt-library-btn {
    border-color: var(--border-default);
    color: var(--text-primary);
}

.ai-chat-prompt-library-btn:hover {
    color: var(--accent-primary) !important;
    border-color: var(--accent-primary) !important;
    transform: scale(1.05);
}

.ai-chat-prompt-library-btn.active {
    color: var(--accent-primary);
    border-color: var(--accent-primary);
    background: rgba(88, 166, 255, 0.1);
}
```

**Active State:** When dropdown is open, button stays highlighted.

**Badge:** Shows count of selected prompts (red circle with number).

---

## 🎭 Visual States Comparison

### **AI Prime Input vs. Agent Input**

| Feature | AI Prime Input | Agent Input |
|---------|---------------|-------------|
| **Container** | `.ai-chat-input-container` | `.agent-input-group` |
| **Position** | Absolute, bottom: 0 | Relative, in flex column |
| **Background** | Transparent (ghost mode) | Solid background |
| **Button Layout** | Vertical stack (5 buttons) | Vertical stack (2 buttons) |
| **Buttons** | Prompt Library, Auto-scroll, Feedback, Attach, Send | Attach, Send only |
| **Feedback System** | ✅ Collapsible container | ❌ Not available |
| **Auto-expand** | ✅ 80px → 300px | ✅ 80px → 200px |
| **Hover Effects** | Progressive disclosure | Same concept, simpler |
| **File Attachments** | ✅ Chips above textarea | ✅ Chips above textarea |
| **Scrollbar Style** | ✅ Custom (Webkit + Firefox) | ✅ Custom (Webkit + Firefox) |

---

## 🧩 Key Differences Explained

### **Why Different from Agent Input?**

**AI Prime is the PRIMARY interface:**
- More features (prompt library, feedback, auto-scroll)
- More sophisticated visual states
- Transparency for minimal distraction
- Advanced interaction patterns

**Agent columns are SECONDARY interfaces:**
- Simpler (just attach + send)
- Always visible (not transparent)
- Focus on quick messages
- Part of multi-column layout

---

## 💡 Design Principles

### **1. Invisible Until Needed**
- Transparency keeps focus on conversation
- Hover reveals full functionality
- No visual clutter at rest

### **2. Progressive Enhancement**
- Basic input always available
- Advanced features appear on interaction
- Graceful degradation if JS fails

### **3. Consistent Hover Language**
```
No Hover    → Transparent, muted
Parent Hover → Bordered, visible
Button Hover → Blue accent, scale up
Active State → Blue accent, persists
```

### **4. Spatial Grouping**
```
Top → Prompt Library (compose-time tool)
Middle → Auto-scroll, Feedback (settings/special)
Bottom → Attach, Send (message actions)
```

### **5. Primary Action Prominence**
- Send button is always most visible
- Blue color signals "go"
- Largest scale-up on hover (1.1x)
- Glowing shadow effect

---

## 🔧 Technical Implementation

### **Z-Index Layers**

```
z-index: 100  → .ai-chat-input-container (base)
z-index: 1000 → .inline-prompt-dropdown (popup)
z-index: 10000 → Modals (if any)
```

### **Pointer Events Strategy**

```css
.ai-chat-input-container {
    pointer-events: none;  /* Ghost container */
}

.ai-chat-input-wrapper,
.user-feedback-container {
    pointer-events: auto;  /* Only input areas clickable */
}
```

**Why?**
- Container covers entire bottom area
- But only input elements should be interactive
- Allows clicks to pass through to content below

### **Transition Timing**

```css
transition: all 0.3s ease;  /* Most elements */
transition: all 0.2s ease;  /* Quick interactions */
```

**0.3s** - Containers, major state changes  
**0.2s** - Buttons, hover effects

---

## 🎯 User Journey

### **Scenario 1: Simple Message**

```
1. User hovers over input area
   → Buttons become visible
   → Textarea gets dark background
   → Send button turns blue

2. User types message
   → Textarea auto-expands

3. User clicks Send
   → Button scales up, glows
   → Message sent
   → Textarea resets to 80px
```

### **Scenario 2: Message with File**

```
1. User clicks Attach button (📎)
   → File picker opens

2. User selects PDF
   → File chip appears above textarea
   → Shows icon, name, size, remove button

3. User types message

4. User clicks Send
   → Message + file sent together
   → File chip disappears
```

### **Scenario 3: Using Prompt Library**

```
1. User clicks Prompt Library button (⚡)
   → Button turns blue (active state)
   → Dropdown appears above input

2. User selects prompt
   → Prompt text inserted into textarea
   → Dropdown stays open (can select more)

3. User clicks button again
   → Dropdown closes
   → Button returns to normal state
```

### **Scenario 4: In-Flight Feedback**

```
1. User sends long request

2. AI starts processing

3. User clicks Feedback button (💬)
   → Feedback container expands above input
   → Main input remains available

4. User types guidance: "Focus on X only"

5. User clicks Send in feedback area
   → Feedback sent to AI
   → AI adjusts mid-process
   → Container stays open
```

---

## 📏 Dimensions & Spacing

```
Container:
- padding: 20px
- position: absolute bottom: 0

Textarea:
- min-height: 80px
- max-height: 300px
- padding: var(--space-3) (~12px)
- border-radius: 6px

Buttons:
- width: 32px
- height: 32px
- gap between: 6px
- border-radius: 6px

File Chips:
- padding: var(--space-1) var(--space-2) (~4px 8px)
- font-size: 12px
- border-radius: 4px

Feedback Container:
- max-height: 300px (when active)
- padding: var(--space-3) (~12px)
```

---

## 🎨 Color System

```
Text Colors:
- Primary: var(--text-primary) #e5e7eb
- Secondary: var(--text-secondary) #d1d5db
- Muted: rgba(139, 148, 158, 0.5)

Backgrounds:
- Transparent: transparent
- Input hover: rgba(0, 0, 0, 0.60)
- Tertiary: var(--bg-tertiary) #1c2128

Accents:
- Primary: var(--accent-primary) #58a6ff (blue)
- Error: var(--accent-error) #f85149 (red)

Borders:
- Default: var(--border-default) #30363d
- Hover: rgba(255, 255, 255, 0.18)
- Active: var(--accent-primary) #58a6ff
```

---

## 🚀 Performance Considerations

### **CSS Transitions (Not Animations)**
- Uses `transition` for smooth state changes
- GPU-accelerated properties (`transform`, `opacity`)
- No layout thrashing

### **Pointer Events Optimization**
- Ghost container reduces event listeners
- Only interactive elements handle events
- Improves scrolling performance

### **Auto-Expand via JavaScript**
```javascript
textarea.addEventListener('input', () => {
    textarea.style.height = 'auto';
    textarea.style.height = Math.min(textarea.scrollHeight, 300) + 'px';
});
```
- Efficient height calculation
- Capped at 300px (prevents infinite growth)
- No reflows outside textarea

---

## 🔐 Locked Thread State

**Special State:** When thread is read-only (locked).

```css
.ai-chat-input-container.locked-read-only {
    opacity: 0.6;
    pointer-events: none;
}

.ai-chat-input-container.locked-read-only::after {
    content: '';
    position: absolute;
    background: rgba(0, 0, 0, 0.05);
}
```

**Visual Effect:**
- Input area dims (60% opacity)
- All interactions disabled
- Overlay prevents clicking
- Banner above explains status

---

## ✅ Design Success Criteria

| Criterion | Status | Evidence |
|-----------|--------|----------|
| **Minimal Visual Footprint** | ✅ | Transparent at rest |
| **Clear Affordances on Hover** | ✅ | All buttons appear with borders |
| **Primary Action Prominence** | ✅ | Send button blue, glows |
| **Smooth Transitions** | ✅ | 0.3s ease on all states |
| **Accessible File Upload** | ✅ | Drag-drop + button + visual feedback |
| **Non-Blocking Feedback** | ✅ | Separate container, doesn't cover input |
| **Responsive to Content** | ✅ | Auto-expand textarea |
| **Consistent with System** | ✅ | Matches agent input patterns |
| **Cross-Browser Scrollbars** | ✅ | Webkit + Firefox standards |
| **Clear Interactive Feedback** | ✅ | Scale, color, shadow on hover |

---

## 📚 Related Components

- **Agent Input Area** - Simplified version in multi-agent columns
- **Feedback Container** - Collapsible guidance system
- **Prompt Library** - Dropdown for pre-made prompts
- **Thread Manager** - Thread switching and history
- **Auto-scroll Toggle** - Chat behavior control

---

## 🔮 Future Enhancements

- [ ] Voice input button
- [ ] Slash commands (/help, /clear, etc.)
- [ ] Rich text formatting toolbar
- [ ] Emoji picker
- [ ] Template variables (@user, @date, etc.)
- [ ] Keyboard shortcuts indicator
- [ ] Character/token counter
- [ ] Draft autosave

---

**Last Updated:** November 15, 2025  
**Status:** ✅ Production Implementation  
**Version:** v2.1

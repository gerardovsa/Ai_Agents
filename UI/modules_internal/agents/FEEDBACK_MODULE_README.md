# 🎯 Feedback Module - External Architecture Documentation

**Version:** 2.0.0  
**Type:** Reusable UI Component + JavaScript Module  
**Status:** Production Ready ✅

---

## 📋 Table of Contents

1. [Overview](#overview)
2. [Architecture](#architecture)
3. [Quick Start](#quick-start)
4. [API Reference](#api-reference)
5. [Integration Guide](#integration-guide)
6. [Usage Examples](#usage-examples)
7. [Customization](#customization)
8. [Events](#events)
9. [Best Practices](#best-practices)
10. [Troubleshooting](#troubleshooting)

---

## 🌟 Overview

The Feedback Module is a **standalone, reusable feedback widget system** designed for AI agent interactions. It provides a complete external module architecture that can be integrated into any web application.

### Key Features

- ✅ **Class-based Singleton Pattern** - Single global instance management
- ✅ **Event-Driven Architecture** - Custom events for all actions
- ✅ **Multiple Contexts** - Per-agent, per-widget, or global feedback
- ✅ **Quick Templates** - Predefined feedback buttons (pause, stop, explain)
- ✅ **API Integration** - Built-in feedback submission endpoints
- ✅ **Theme Support** - Dark/light themes with CSS variables
- ✅ **Keyboard Shortcuts** - Ctrl+Enter to send, Escape to close
- ✅ **LocalStorage Persistence** - Automatic history saving
- ✅ **Accessibility** - ARIA labels, focus management, keyboard navigation
- ✅ **Responsive Design** - Mobile-friendly with touch support

### Module Files

```
modules_internal/agents/
├── feedback-module.js      # Core JavaScript module (900+ lines)
├── feedback-styles.css     # Scoped styles with themes (400+ lines)
├── feedback-demo.html      # Standalone demo page
└── FEEDBACK_MODULE_README.md  # This file
```

---

## 🏗️ Architecture

### Component Structure

```
┌─────────────────────────────────────────┐
│         FeedbackModule (Singleton)       │
│                                          │
│  ┌────────────────────────────────────┐ │
│  │  Widget Manager                    │ │
│  │  - Create/Destroy widgets          │ │
│  │  - Map<widgetId, widget>           │ │
│  └────────────────────────────────────┘ │
│                                          │
│  ┌────────────────────────────────────┐ │
│  │  Event System                      │ │
│  │  - widget:created                  │ │
│  │  - feedback:sent                   │ │
│  │  - widget:destroyed                │ │
│  └────────────────────────────────────┘ │
│                                          │
│  ┌────────────────────────────────────┐ │
│  │  History Manager                   │ │
│  │  - LocalStorage persistence        │ │
│  │  - Array<feedbackData>             │ │
│  └────────────────────────────────────┘ │
│                                          │
│  ┌────────────────────────────────────┐ │
│  │  Template System                   │ │
│  │  - QUICK_TEMPLATES (6 presets)     │ │
│  │  - insertQuickFeedback()           │ │
│  └────────────────────────────────────┘ │
└─────────────────────────────────────────┘
```

### Widget Lifecycle

```
┌───────────────────────────────────────────────┐
│ 1. CREATE                                     │
│    feedback.createWidget('agent-1', options)  │
│    ↓                                          │
│    - Build DOM structure                      │
│    - Attach event listeners                   │
│    - Store in widgets Map                     │
│    - Emit 'widget:created' event              │
└───────────────────────────────────────────────┘
         ↓
┌───────────────────────────────────────────────┐
│ 2. SHOW/HIDE                                  │
│    feedback.toggle('agent-1')                 │
│    ↓                                          │
│    - Add/remove 'visible' class               │
│    - Focus textarea on show                   │
│    - Emit 'widget:shown/hidden' events        │
└───────────────────────────────────────────────┘
         ↓
┌───────────────────────────────────────────────┐
│ 3. INTERACT                                   │
│    - Type in textarea                         │
│    - Click quick buttons                      │
│    - Ctrl+Enter to send                       │
│    - Escape to close                          │
└───────────────────────────────────────────────┘
         ↓
┌───────────────────────────────────────────────┐
│ 4. SEND                                       │
│    feedback.send('agent-1')                   │
│    ↓                                          │
│    - Create feedbackData object               │
│    - Add to history                           │
│    - Call onSend callback                     │
│    - Emit 'feedback:sent' event               │
│    - Clear textarea and hide widget           │
└───────────────────────────────────────────────┘
         ↓
┌───────────────────────────────────────────────┐
│ 5. DESTROY (Optional)                         │
│    feedback.destroyWidget('agent-1')          │
│    ↓                                          │
│    - Remove from DOM                          │
│    - Delete from widgets Map                  │
│    - Emit 'widget:destroyed' event            │
└───────────────────────────────────────────────┘
```

---

## 🚀 Quick Start

### 1. Include Files

```html
<!-- In your HTML <head> -->
<link rel="stylesheet" href="path/to/feedback-styles.css">

<!-- Before closing </body> -->
<script src="path/to/feedback-module.js"></script>
```

### 2. Initialize Module

```javascript
// Get singleton instance
const feedback = FeedbackModule.getInstance({
    theme: 'dark',
    enableKeyboardShortcuts: true,
    enableLocalStorage: true,
    apiEndpoint: '/api/feedback'
});
```

### 3. Create Widget

```javascript
// Create feedback widget
feedback.createWidget('my-widget', {
    contextType: 'agent',
    contextId: 123,
    placeholder: 'Type your feedback...',
    onSend: (text, data) => {
        console.log('Feedback:', text);
    }
});

// Get widget DOM element
const widgetElement = feedback.getWidgetElement('my-widget');

// Attach to your container
document.getElementById('container').appendChild(widgetElement);
```

### 4. Toggle Visibility

```javascript
// Show widget
feedback.show('my-widget');

// Hide widget
feedback.hide('my-widget');

// Toggle
feedback.toggle('my-widget');
```

---

## 📖 API Reference

### FeedbackModule.getInstance(config)

Get or create the singleton instance.

**Parameters:**
- `config` (Object, optional) - Configuration object

**Configuration Options:**
```javascript
{
    theme: 'dark',                    // 'dark' or 'light'
    enableKeyboardShortcuts: true,    // Enable Ctrl+Shift+F
    enableLocalStorage: true,         // Save history to localStorage
    animationDuration: 200,           // Animation duration (ms)
    maxHistoryItems: 50,              // Max history items to store
    apiEndpoint: '/api/feedback'      // API endpoint for submissions
}
```

**Returns:** `Feedback` instance

---

### feedback.createWidget(widgetId, options)

Create a new feedback widget.

**Parameters:**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `widgetId` | String | ✅ | Unique widget identifier |
| `options` | Object | ✅ | Widget configuration |

**Options Object:**

```javascript
{
    contextType: 'agent',              // Context type (agent, global, custom)
    contextId: 123,                    // Context identifier (agent ID, etc.)
    placeholder: 'Type feedback...',   // Textarea placeholder
    quickButtons: ['pause', 'stop'],   // Quick feedback buttons
    onSend: (text, data) => {},        // Callback when feedback is sent
    onCancel: () => {},                // Callback when widget is closed
    container: null                    // Optional: Custom container element
}
```

**Quick Button Options:**
- `'pause'` - "Please pause and wait for my next instruction."
- `'stop'` - "Stop the current operation immediately."
- `'explain'` - "Please explain what you just did in more detail."
- `'clarify'` - "I need clarification on your last response."
- `'continue'` - "Continue with the current task."
- `'retry'` - "Please retry the last operation with corrections."

**Returns:** Widget instance object

**Example:**

```javascript
const widget = feedback.createWidget('agent-1', {
    contextType: 'agent',
    contextId: 1,
    placeholder: 'Provide guidance to Agent Alpha...',
    quickButtons: ['pause', 'stop', 'explain'],
    onSend: async (text, data) => {
        console.log('Feedback text:', text);
        console.log('Context:', data.contextType, data.contextId);
        
        // Send to your API
        await fetch('/api/agent/feedback', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(data)
        });
    },
    onCancel: () => {
        console.log('User cancelled feedback');
    }
});
```

---

### feedback.show(widgetId)

Show a widget.

**Parameters:**
- `widgetId` (String) - Widget ID

**Example:**

```javascript
feedback.show('agent-1');
```

---

### feedback.hide(widgetId)

Hide a widget.

**Parameters:**
- `widgetId` (String) - Widget ID

**Example:**

```javascript
feedback.hide('agent-1');
```

---

### feedback.toggle(widgetId)

Toggle widget visibility.

**Parameters:**
- `widgetId` (String) - Widget ID

**Example:**

```javascript
feedback.toggle('agent-1');
```

---

### feedback.send(widgetId)

Send feedback from widget.

**Parameters:**
- `widgetId` (String) - Widget ID

**Behavior:**
1. Validates textarea is not empty
2. Creates `feedbackData` object
3. Adds to history
4. Calls `onSend` callback
5. Emits `feedback:sent` event
6. Clears textarea
7. Hides widget

**Example:**

```javascript
// Manual send (usually triggered by button)
feedback.send('agent-1');
```

---

### feedback.insertQuickFeedback(widgetId, templateKey)

Insert quick feedback template into textarea.

**Parameters:**
- `widgetId` (String) - Widget ID
- `templateKey` (String) - Template key (pause, stop, explain, etc.)

**Example:**

```javascript
feedback.insertQuickFeedback('agent-1', 'pause');
// Textarea now contains: "Please pause and wait for my next instruction."
```

---

### feedback.getWidgetElement(widgetId)

Get widget DOM element for manual attachment.

**Parameters:**
- `widgetId` (String) - Widget ID

**Returns:** HTMLElement or null

**Example:**

```javascript
const widgetElement = feedback.getWidgetElement('agent-1');
document.getElementById('my-container').appendChild(widgetElement);
```

---

### feedback.destroyWidget(widgetId)

Destroy widget and clean up.

**Parameters:**
- `widgetId` (String) - Widget ID

**Example:**

```javascript
feedback.destroyWidget('agent-1');
```

---

### feedback.getHistory(filters)

Get feedback history with optional filters.

**Parameters:**
- `filters` (Object, optional) - Filter options

**Filter Options:**

```javascript
{
    contextType: 'agent',   // Filter by context type
    contextId: 123,         // Filter by context ID
    limit: 10               // Limit number of results
}
```

**Returns:** Array of feedback objects

**Example:**

```javascript
// Get last 10 feedback items for agent 1
const history = feedback.getHistory({
    contextType: 'agent',
    contextId: 1,
    limit: 10
});

history.forEach(item => {
    console.log(item.text);
    console.log(item.timestamp);
});
```

---

### feedback.clearHistory()

Clear all feedback history.

**Example:**

```javascript
feedback.clearHistory();
```

---

### feedback.setTheme(theme)

Set theme (dark/light).

**Parameters:**
- `theme` (String) - 'dark' or 'light'

**Example:**

```javascript
feedback.setTheme('light');
```

---

### feedback.getStats()

Get module statistics.

**Returns:** Object with stats

```javascript
{
    widgetCount: 3,        // Number of widgets
    historyCount: 15,      // Number of history items
    activeWidgets: 1       // Number of visible widgets
}
```

**Example:**

```javascript
const stats = feedback.getStats();
console.log(`Active widgets: ${stats.activeWidgets}`);
```

---

### feedback.on(eventName, callback)

Add event listener.

**Parameters:**
- `eventName` (String) - Event name
- `callback` (Function) - Callback function

**Events:**
- `widget:created`
- `widget:shown`
- `widget:hidden`
- `widget:destroyed`
- `feedback:sent`
- `template:inserted`
- `history:cleared`

**Example:**

```javascript
feedback.on('feedback:sent', (data) => {
    console.log('Feedback sent:', data);
});
```

---

### feedback.off(eventName, callback)

Remove event listener.

**Parameters:**
- `eventName` (String) - Event name
- `callback` (Function) - Callback function reference

**Example:**

```javascript
const handler = (data) => console.log(data);
feedback.on('feedback:sent', handler);
feedback.off('feedback:sent', handler);
```

---

## 🔗 Integration Guide

### Integration with Agent Column

The feedback module is integrated into [agent-column.js](agent-column.js) as an external module.

**Step 1: Include Module Files**

Add to your main HTML:

```html
<link rel="stylesheet" href="modules_internal/agents/feedback-styles.css">
<script src="modules_internal/agents/feedback-module.js"></script>
<script src="modules_internal/agents/agent-column.js"></script>
```

**Step 2: Initialize in Agent Column**

The agent column automatically initializes feedback widgets when created:

```javascript
// In agent-column.js (automatically done)
function initializeFeedbackWidget(agentId, agentName) {
    const feedback = FeedbackModule.getInstance();
    
    feedback.createWidget(`agent-${agentId}`, {
        contextType: 'agent',
        contextId: agentId,
        placeholder: `Guidance for ${agentName}...`,
        quickButtons: ['pause', 'stop', 'explain', 'continue'],
        onSend: async (text, data) => {
            await AgentInput.sendFeedback(agentId, text);
        }
    });
    
    const widgetElement = feedback.getWidgetElement(`agent-${agentId}`);
    document.getElementById(`agent-feedback-${agentId}`)
        .appendChild(widgetElement);
}
```

**Step 3: Use in Your Code**

```javascript
// Toggle feedback for agent 1
AgentColumn.toggleFeedback(1);
```

---

### Integration with Custom UI

**Basic Integration:**

```javascript
// Initialize module
const feedback = FeedbackModule.getInstance();

// Create widget
feedback.createWidget('custom-widget', {
    contextType: 'custom',
    contextId: 'my-feature',
    placeholder: 'Your feedback...',
    onSend: (text, data) => {
        // Handle feedback
        console.log('Feedback:', text);
    }
});

// Add to page
const container = document.getElementById('feedback-container');
container.appendChild(feedback.getWidgetElement('custom-widget'));

// Show when needed
document.getElementById('feedback-btn').addEventListener('click', () => {
    feedback.toggle('custom-widget');
});
```

---

## 💡 Usage Examples

### Example 1: Simple Feedback Widget

```javascript
const feedback = FeedbackModule.getInstance();

feedback.createWidget('simple', {
    contextType: 'global',
    placeholder: 'Send us your feedback...',
    quickButtons: [],
    onSend: (text) => {
        alert(`Thanks for your feedback: ${text}`);
    }
});

document.getElementById('container')
    .appendChild(feedback.getWidgetElement('simple'));

feedback.show('simple');
```

---

### Example 2: Multi-Agent Feedback

```javascript
const feedback = FeedbackModule.getInstance();

// Create widgets for 3 agents
[1, 2, 3].forEach(agentId => {
    feedback.createWidget(`agent-${agentId}`, {
        contextType: 'agent',
        contextId: agentId,
        placeholder: `Feedback for Agent ${agentId}...`,
        quickButtons: ['pause', 'stop', 'explain'],
        onSend: async (text, data) => {
            await fetch('/api/agent/feedback', {
                method: 'POST',
                body: JSON.stringify(data)
            });
        }
    });
    
    const container = document.getElementById(`agent-${agentId}-feedback`);
    container.appendChild(feedback.getWidgetElement(`agent-${agentId}`));
});

// Toggle specific agent's feedback
document.getElementById('toggle-agent-1').addEventListener('click', () => {
    feedback.toggle('agent-1');
});
```

---

### Example 3: Custom Quick Templates

```javascript
// Access template system
const templates = FeedbackModule.QUICK_TEMPLATES;

// Create widget with all templates
feedback.createWidget('advanced', {
    contextType: 'advanced',
    quickButtons: Object.keys(templates), // All 6 templates
    onSend: (text, data) => {
        console.log('Template used:', data.text === templates.pause.text);
    }
});
```

---

### Example 4: Event-Driven Architecture

```javascript
const feedback = FeedbackModule.getInstance();

// Listen to all events
feedback.on('widget:created', (data) => {
    console.log('Widget created:', data.widgetId);
});

feedback.on('feedback:sent', (data) => {
    console.log('Feedback sent:', data.text);
    console.log('Context:', data.contextType, data.contextId);
    
    // Update UI
    updateFeedbackCount();
});

feedback.on('widget:shown', (data) => {
    console.log('Widget visible:', data.widgetId);
});

feedback.on('widget:hidden', (data) => {
    console.log('Widget hidden:', data.widgetId);
});

// Also listen via DOM events
document.addEventListener('feedback:sent', (e) => {
    console.log('DOM Event:', e.detail);
});
```

---

### Example 5: History Management

```javascript
const feedback = FeedbackModule.getInstance();

// Get all history
const allHistory = feedback.getHistory();
console.log(`Total feedback: ${allHistory.length}`);

// Get agent-specific history
const agentHistory = feedback.getHistory({
    contextType: 'agent',
    contextId: 1
});
console.log(`Agent 1 feedback: ${agentHistory.length}`);

// Display recent feedback
const recent = feedback.getHistory({ limit: 5 });
recent.forEach(item => {
    console.log(`[${new Date(item.timestamp).toLocaleString()}] ${item.text}`);
});

// Clear history
feedback.clearHistory();
```

---

## 🎨 Customization

### CSS Variables

Override theme colors:

```css
.feedback-widget[data-theme="dark"] {
    --feedback-bg-primary: rgba(31, 41, 55, 0.98);
    --feedback-accent: #667eea;
    --feedback-text-primary: #e5e7eb;
}

.feedback-widget[data-theme="custom"] {
    --feedback-bg-primary: #2c3e50;
    --feedback-accent: #e74c3c;
    --feedback-text-primary: #ecf0f1;
}
```

### Custom Styling

Add custom classes:

```javascript
const widgetElement = feedback.getWidgetElement('my-widget');
widgetElement.classList.add('my-custom-class');
```

```css
.feedback-widget.my-custom-class {
    border-radius: 20px;
    box-shadow: 0 20px 60px rgba(0, 0, 0, 0.8);
}
```

---

## 🎭 Events

### Event Reference

| Event Name | When Fired | Event Detail |
|-----------|------------|--------------|
| `widget:created` | Widget is created | `{ widgetId, widget }` |
| `widget:shown` | Widget becomes visible | `{ widgetId, widget }` |
| `widget:hidden` | Widget becomes hidden | `{ widgetId, widget }` |
| `widget:destroyed` | Widget is destroyed | `{ widgetId }` |
| `feedback:sent` | Feedback is submitted | `{ text, contextType, contextId, timestamp, widgetId }` |
| `template:inserted` | Quick template inserted | `{ widgetId, templateKey, text }` |
| `history:cleared` | History is cleared | `{}` |

### Listening to Events

**Method 1: Module API**

```javascript
feedback.on('feedback:sent', (data) => {
    console.log('Feedback:', data);
});
```

**Method 2: DOM Events**

```javascript
document.addEventListener('feedback:sent', (e) => {
    console.log('Feedback:', e.detail);
});
```

---

## ✅ Best Practices

### 1. Single Instance

Always use the singleton pattern:

```javascript
// ✅ Good
const feedback = FeedbackModule.getInstance();

// ❌ Bad
const feedback = new FeedbackModule(); // This will return singleton anyway
```

### 2. Unique Widget IDs

Use descriptive, unique IDs:

```javascript
// ✅ Good
feedback.createWidget('agent-1-feedback', { ... });
feedback.createWidget('prime-feedback', { ... });

// ❌ Bad
feedback.createWidget('widget1', { ... });
feedback.createWidget('widget2', { ... });
```

### 3. Clean Up Widgets

Destroy widgets when no longer needed:

```javascript
// When closing agent column
function closeAgentColumn(agentId) {
    feedback.destroyWidget(`agent-${agentId}`);
    // ... other cleanup
}
```

### 4. Error Handling

Always handle errors in callbacks:

```javascript
feedback.createWidget('my-widget', {
    onSend: async (text, data) => {
        try {
            await sendToAPI(data);
        } catch (error) {
            console.error('Failed to send feedback:', error);
            alert('Failed to send feedback. Please try again.');
        }
    }
});
```

### 5. Theme Consistency

Set theme once globally:

```javascript
const feedback = FeedbackModule.getInstance({
    theme: document.body.dataset.theme || 'dark'
});

// Update theme when app theme changes
document.addEventListener('theme-changed', (e) => {
    feedback.setTheme(e.detail.theme);
});
```

---

## 🔧 Troubleshooting

### Widget Not Showing

**Problem:** Widget created but not visible

**Solution:**
```javascript
// Check if widget exists
const widget = feedback.getWidgetElement('my-widget');
console.log('Widget exists:', !!widget);

// Check if attached to DOM
console.log('In DOM:', document.contains(widget));

// Check visibility state
const instance = feedback.widgets.get('my-widget');
console.log('Is visible:', instance?.isVisible);

// Manually show
feedback.show('my-widget');
```

---

### Feedback Not Sending

**Problem:** Click send button but nothing happens

**Solution:**
```javascript
// Check textarea has content
const widget = feedback.widgets.get('my-widget');
console.log('Textarea value:', widget.textareaElement?.value);

// Check onSend callback is defined
console.log('Has callback:', !!widget.onSend);

// Test callback
if (widget.onSend) {
    widget.onSend('Test', { contextType: 'test' });
}
```

---

### Keyboard Shortcuts Not Working

**Problem:** Ctrl+Enter doesn't send feedback

**Solution:**
```javascript
// Check if shortcuts are enabled
const feedback = FeedbackModule.getInstance();
console.log('Shortcuts enabled:', feedback.config.enableKeyboardShortcuts);

// Re-enable shortcuts
feedback.config.enableKeyboardShortcuts = true;
```

---

### History Not Persisting

**Problem:** History cleared on page refresh

**Solution:**
```javascript
// Check localStorage is enabled
console.log('LocalStorage enabled:', feedback.config.enableLocalStorage);

// Check localStorage quota
try {
    const test = 'test';
    localStorage.setItem(test, test);
    localStorage.removeItem(test);
    console.log('LocalStorage available: ✅');
} catch (e) {
    console.error('LocalStorage not available:', e);
}

// Manually save history
feedback._saveHistory();
```

---

## 📚 Additional Resources

- **Live Demo:** Open [feedback-demo.html](feedback-demo.html) in browser
- **Source Code:** [feedback-module.js](feedback-module.js)
- **Styles:** [feedback-styles.css](feedback-styles.css)
- **Integration:** [agent-column.js](agent-column.js) lines 1-50, 250-310

---

## 📝 Version History

### v2.0.0 (Current)
- ✅ External module architecture
- ✅ Singleton pattern implementation
- ✅ Event-driven system
- ✅ Complete API documentation
- ✅ Demo page with examples
- ✅ Integration with agent-column.js

### v1.0.0 (Legacy)
- Inline implementation in agent-column.js
- No external module support
- Limited reusability

---

## 🤝 Contributing

To extend the feedback module:

1. Add new quick templates to `QUICK_TEMPLATES`
2. Extend configuration options in `DEFAULT_CONFIG`
3. Add new events to `_emit()` system
4. Update documentation

---

## 📄 License

Part of Valor AI infrastructure system.

---

**Questions?** Check [feedback-demo.html](feedback-demo.html) for interactive examples!

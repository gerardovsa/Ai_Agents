# Message Bubble Fullscreen View Implementation
**Date**: December 4, 2025

## Feature Description

Implement fullscreen/popup view for message bubbles that can be triggered by:
1. **Double-clicking** on any message bubble
2. **Clicking** the fullscreen button in the viz-action-bar

## Implementation

### 1. Double-Click Handler for Message Bubbles

Add event listener to all message bubbles to open fullscreen view on double-click.

**Location**: `UI/modules_internal/agents/prime_ai_chat.js`

```javascript
// After bubble creation, add double-click handler
bubble.addEventListener('dblclick', (e) => {
    e.stopPropagation();
    openMessageFullscreen(bubble);
});
```

### 2. Fullscreen Modal System

Create modal overlay system for displaying message content in fullscreen.

```javascript
function openMessageFullscreen(bubbleElement) {
    // Get bubble content
    const content = bubbleElement.querySelector('.ai-message-content')?.innerHTML || 
                   bubbleElement.innerHTML;
    
    // Create fullscreen modal
    const modal = document.createElement('div');
    modal.className = 'message-fullscreen-modal';
    modal.innerHTML = `
        <div class="fullscreen-overlay"></div>
        <div class="fullscreen-content">
            <div class="fullscreen-header">
                <h3>Message Content</h3>
                <div class="fullscreen-actions">
                    <button class="fullscreen-action-btn" data-action="copy">
                        <i class="fas fa-copy"></i> Copy
                    </button>
                    <button class="fullscreen-action-btn" data-action="close">
                        <i class="fas fa-times"></i> Close
                    </button>
                </div>
            </div>
            <div class="fullscreen-body">
                ${content}
            </div>
        </div>
    `;
    
    // Add to body
    document.body.appendChild(modal);
    
    // Setup event handlers
    setupFullscreenHandlers(modal, content);
    
    // Show with animation
    requestAnimationFrame(() => {
        modal.classList.add('active');
    });
}

function setupFullscreenHandlers(modal, content) {
    // Close button
    modal.querySelector('[data-action="close"]').addEventListener('click', () => {
        closeMessageFullscreen(modal);
    });
    
    // Copy button
    modal.querySelector('[data-action="copy"]').addEventListener('click', () => {
        copyToClipboard(content);
    });
    
    // Close on overlay click
    modal.querySelector('.fullscreen-overlay').addEventListener('click', () => {
        closeMessageFullscreen(modal);
    });
    
    // Close on ESC key
    const escHandler = (e) => {
        if (e.key === 'Escape') {
            closeMessageFullscreen(modal);
            document.removeEventListener('keydown', escHandler);
        }
    };
    document.addEventListener('keydown', escHandler);
}

function closeMessageFullscreen(modal) {
    modal.classList.remove('active');
    setTimeout(() => {
        modal.remove();
    }, 300); // Wait for animation
}
```

### 3. CSS Styles

Add styles for fullscreen modal:

```css
.message-fullscreen-modal {
    position: fixed;
    top: 0;
    left: 0;
    width: 100%;
    height: 100%;
    z-index: 10000;
    display: none;
    opacity: 0;
    transition: opacity 0.3s ease;
}

.message-fullscreen-modal.active {
    display: flex;
    opacity: 1;
}

.fullscreen-overlay {
    position: absolute;
    top: 0;
    left: 0;
    width: 100%;
    height: 100%;
    background: rgba(0, 0, 0, 0.85);
    backdrop-filter: blur(5px);
}

.fullscreen-content {
    position: relative;
    width: 90%;
    height: 90%;
    max-width: 1400px;
    margin: auto;
    background: var(--surface-primary, #1e1e1e);
    border-radius: 12px;
    box-shadow: 0 20px 60px rgba(0, 0, 0, 0.5);
    display: flex;
    flex-direction: column;
    overflow: hidden;
    animation: slideIn 0.3s ease;
}

@keyframes slideIn {
    from {
        transform: translateY(-20px) scale(0.95);
        opacity: 0;
    }
    to {
        transform: translateY(0) scale(1);
        opacity: 1;
    }
}

.fullscreen-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 20px 30px;
    border-bottom: 1px solid var(--border-color, #333);
    background: var(--surface-secondary, #252525);
}

.fullscreen-header h3 {
    margin: 0;
    font-size: 1.5rem;
    color: var(--text-primary, #fff);
}

.fullscreen-actions {
    display: flex;
    gap: 10px;
}

.fullscreen-action-btn {
    padding: 8px 16px;
    border: none;
    border-radius: 6px;
    background: var(--button-bg, #333);
    color: var(--text-primary, #fff);
    cursor: pointer;
    transition: all 0.2s ease;
}

.fullscreen-action-btn:hover {
    background: var(--button-hover, #444);
    transform: translateY(-1px);
}

.fullscreen-action-btn[data-action="close"] {
    background: #dc3545;
}

.fullscreen-action-btn[data-action="close"]:hover {
    background: #c82333;
}

.fullscreen-body {
    flex: 1;
    padding: 30px;
    overflow-y: auto;
    color: var(--text-primary, #fff);
}

/* Scrollbar styling */
.fullscreen-body::-webkit-scrollbar {
    width: 10px;
}

.fullscreen-body::-webkit-scrollbar-track {
    background: var(--surface-primary, #1e1e1e);
}

.fullscreen-body::-webkit-scrollbar-thumb {
    background: var(--scrollbar-thumb, #555);
    border-radius: 5px;
}

.fullscreen-body::-webkit-scrollbar-thumb:hover {
    background: var(--scrollbar-thumb-hover, #666);
}

/* Cursor hint for double-click */
.ai-message {
    cursor: pointer;
}

.ai-message:hover {
    opacity: 0.95;
}
```

### 4. Integration Points

#### A. Prime AI Chat (prime_ai_chat.js)

Add double-click handlers after bubble creation:

```javascript
// After line 844 (thinking bubble creation)
thinkingBubble.addEventListener('dblclick', (e) => {
    e.stopPropagation();
    if (typeof openMessageFullscreen === 'function') {
        openMessageFullscreen(thinkingBubble);
    }
});

// After line 968 (tool bubble creation)
toolBubble.addEventListener('dblclick', (e) => {
    e.stopPropagation();
    if (typeof openMessageFullscreen === 'function') {
        openMessageFullscreen(toolBubble);
    }
});

// After line 1093 (text bubble creation)
textBubble.addEventListener('dblclick', (e) => {
    e.stopPropagation();
    if (typeof openMessageFullscreen === 'function') {
        openMessageFullscreen(textBubble);
    }
});
```

#### B. Visualization Engine (visualisation_copy.js)

Connect the fullscreen button to the handler:

```javascript
// Update case 'fullscreenView': (around line 5591)
case 'fullscreenView':
    // Check if this is a message bubble or viz container
    const messageBubble = button.closest('.ai-message');
    if (messageBubble && typeof openMessageFullscreen === 'function') {
        openMessageFullscreen(messageBubble);
    } else {
        this.openMermaidFullscreen(vizContainer, diagramContent, chartId);
    }
    break;
```

## Files to Modify

1. **UI/modules_internal/agents/prime_ai_chat.js**
   - Add double-click handlers to all bubble types
   - Import/define fullscreen functions

2. **UI/visualisation_engine/visualisation_copy.js**
   - Update fullscreenView case to handle message bubbles
   - Ensure proper element detection

3. **UI/triple_agent.html** (or main HTML file)
   - Add CSS styles for fullscreen modal
   - Add global fullscreen functions

4. **UI/modules_internal/agents/shared-functions.js** (create if needed)
   - Define `openMessageFullscreen()` function
   - Define `closeMessageFullscreen()` function
   - Define `setupFullscreenHandlers()` function

## Testing Checklist

- [ ] Double-click on thinking bubble opens fullscreen
- [ ] Double-click on tool bubble opens fullscreen
- [ ] Double-click on text bubble opens fullscreen
- [ ] Fullscreen button in viz-action-bar works
- [ ] ESC key closes fullscreen
- [ ] Overlay click closes fullscreen
- [ ] Close button closes fullscreen
- [ ] Copy button works
- [ ] Content displays correctly in fullscreen
- [ ] Scrolling works for long content
- [ ] Animation plays smoothly
- [ ] No console errors

## User Experience

**Before**: Users could only view messages in their original size within the chat flow.

**After**: 
- Users can double-click any message bubble for fullscreen view
- Users can click the fullscreen button in viz-action-bar
- Easy to read long messages or complex visualizations
- Copy functionality available in fullscreen
- Smooth animations and transitions
- Keyboard shortcuts (ESC to close)

## Implementation Time

Estimated: 30-45 minutes
- Code implementation: 20 min
- CSS styling: 10 min
- Testing: 10-15 min

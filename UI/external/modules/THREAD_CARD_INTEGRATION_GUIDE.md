# Thread Card Integration Guide for Module Developers

**Date:** November 28, 2025  
**Status:** Production Ready  
**Audience:** Module developers adding thread card integration to existing/new modules

---

## 🎯 Overview

This guide shows you how to add **drag-and-drop** and **badge display** capabilities to your module so it integrates with thread info cards (the single source of truth for thread linkages).

**Key Benefits:**
- ✅ Users can drag your module items onto thread cards
- ✅ Thread cards automatically show badges when linked to your module
- ✅ Real-time updates via WebSocket events
- ✅ Zero changes to thread card code
- ✅ Follows existing module system patterns

---

## 📋 Prerequisites

Before adding thread card integration, your module should:

1. ✅ Have a `manifest.json` file (existing module system requirement)
2. ✅ Be registered in `/api/modules/list` endpoint
3. ✅ Have a JavaScript controller file (e.g., `synergy.js`)
4. ✅ Store linkage data in database (e.g., `thread.synergy_session_id`)

**If you don't have a module yet, see:** `MODULE_SYSTEM_ARCHITECTURE_COMPLETE.md`

---

## 🚀 Step-by-Step Integration

### Step 1: Update Your manifest.json

Add the `thread_card_integration` section to your existing manifest:

**File:** `UI/modules/your_module/manifest.json`

```json
{
  "id": "your_module",
  "name": "Your Module Name",
  "version": "1.0.0",
  "icon": "fa-your-icon",
  "color": "#10b981",
  
  ...existing fields (html_file, js_file, required_platforms, etc.)...,
  
  "thread_card_integration": {
    "enabled": true,
    
    "drag_and_drop": {
      "accepts": [
        {
          "data_type": "your-item-type",
          "mime_type": "application/x-your-item",
          "handler": "window.YourModule.linkToThread"
        }
      ],
      "provides": [
        {
          "data_type": "your-item-type",
          "mime_type": "application/x-your-item",
          "handler": "window.YourModule.startDrag"
        }
      ]
    },
    
    "badge": {
      "enabled": true,
      "condition": "thread.your_module_id !== null",
      "render_function": "window.YourModule.renderThreadBadge",
      "config": {
        "icon": "fa-your-icon",
        "color": "#10b981",
        "label": "Your Module",
        "tooltip_template": "Linked to: {your_item_title}",
        "click_action": "window.YourModule.openLinkedItem",
        "show_count": false,
        "priority": 3
      }
    },
    
    "realtime_events": {
      "enabled": true,
      "events": [
        "thread_linked_to_your_module",
        "thread_unlinked_from_your_module"
      ],
      "handler": "window.YourModule.handleRealtimeUpdate"
    },
    
    "database_fields": {
      "thread_link_column": "your_module_id",
      "thread_link_column_type": "VARCHAR",
      "thread_metadata_column": "your_module_title"
    }
  }
}
```

---

### Step 2: Implement Drag Handlers

Add drag handlers to your module's JavaScript file:

**File:** `UI/modules/your_module/your_module.js`

```javascript
// ==================== THREAD CARD INTEGRATION ====================

window.YourModule = window.YourModule || {};

/**
 * DRAG START: User drags your module item
 * Add draggable="true" and ondragstart to your HTML elements
 */
window.YourModule.startDrag = function(event, itemId, itemData) {
    console.log('[YourModule] Starting drag:', itemId);
    
    // Set drag data (thread cards will read this)
    event.dataTransfer.effectAllowed = 'link';
    event.dataTransfer.setData('application/x-your-item', JSON.stringify({
        item_id: itemId,
        item_title: itemData.title,
        item_type: itemData.type
    }));
    
    // Visual feedback
    event.target.classList.add('dragging');
};

/**
 * DRAG END: Cleanup
 */
window.YourModule.endDrag = function(event) {
    event.target.classList.remove('dragging');
};

/**
 * DROP HANDLER: User drops your item on thread card
 * Called by ThreadCardRegistry when drop detected
 */
window.YourModule.linkToThread = async function(itemDataJson, threadId, location) {
    try {
        const itemData = JSON.parse(itemDataJson);
        
        console.log('[YourModule] Linking item to thread:', {
            item_id: itemData.item_id,
            thread_id: threadId,
            location: location
        });
        
        // Call your backend API to link
        const response = await fetch('/api/your-module/link-to-thread', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                item_id: itemData.item_id,
                thread_id: threadId,
                item_title: itemData.item_title
            })
        });
        
        if (!response.ok) {
            throw new Error(`HTTP ${response.status}`);
        }
        
        const result = await response.json();
        
        if (result.success) {
            console.log('✅ [YourModule] Successfully linked to thread');
            
            // Show success notification
            if (typeof showNotification === 'function') {
                showNotification(`Linked ${itemData.item_title} to thread`, 'success');
            }
            
            // Refresh thread card badge
            if (window.ThreadManager?.refreshThreadCard) {
                window.ThreadManager.refreshThreadCard(threadId);
            }
        }
        
    } catch (error) {
        console.error('❌ [YourModule] Failed to link:', error);
        if (typeof showNotification === 'function') {
            showNotification('Failed to link item to thread', 'error');
        }
    }
};

/**
 * BADGE RENDERER: Show badge on thread card
 * Called by ThreadCardRegistry when rendering thread cards
 */
window.YourModule.renderThreadBadge = function(thread, config) {
    // Check if thread has your module linked
    if (!thread.your_module_id) {
        return ''; // No badge
    }
    
    const itemTitle = thread.your_module_title || 'Unknown Item';
    const tooltip = config.tooltip_template.replace('{your_item_title}', itemTitle);
    
    return `
        <div class="thread-badge your-module-badge" 
             style="background: ${config.color}; cursor: pointer;"
             title="${tooltip}"
             onclick="${config.click_action}('${thread.your_module_id}', '${thread.id}')">
            <i class="fas ${config.icon}"></i>
            <span>${config.label}</span>
            ${config.show_count && thread.your_module_count ? `<span class="badge-count">${thread.your_module_count}</span>` : ''}
        </div>
    `;
};

/**
 * BADGE CLICK: User clicks badge
 */
window.YourModule.openLinkedItem = function(itemId, threadId) {
    console.log('[YourModule] Opening linked item:', itemId);
    
    // Your logic to open the item (e.g., open sidebar, navigate to item)
    // Example:
    // window.moduleLoader.toggleModule('your_module');
    // window.YourModule.selectItem(itemId);
};

/**
 * REALTIME UPDATE: WebSocket event received
 * Called by ThreadCardRegistry when linkage changes
 */
window.YourModule.handleRealtimeUpdate = function(eventData) {
    console.log('[YourModule] Realtime update received:', eventData);
    
    const { thread_id, item_id, action } = eventData;
    
    // Refresh thread card to show updated badge
    if (window.ThreadManager?.refreshThreadCard) {
        window.ThreadManager.refreshThreadCard(thread_id);
    }
    
    // Refresh your module UI if open
    if (window.YourModule.isOpen?.()) {
        window.YourModule.refreshUI();
    }
};
```

---

### Step 3: Make Your Items Draggable

Update your HTML templates to make items draggable:

**Before (not draggable):**
```html
<div class="your-item" data-item-id="${item.id}">
    <span>${item.title}</span>
</div>
```

**After (draggable):**
```html
<div class="your-item" 
     data-item-id="${item.id}"
     draggable="true"
     ondragstart="YourModule.startDrag(event, '${item.id}', ${JSON.stringify(item)})"
     ondragend="YourModule.endDrag(event)">
    <span>${item.title}</span>
    <i class="fas fa-grip-vertical drag-handle"></i>
</div>
```

**CSS for drag feedback:**
```css
.your-item[draggable="true"] {
    cursor: move;
    transition: opacity 0.2s ease;
}

.your-item.dragging {
    opacity: 0.5;
}

.drag-handle {
    color: var(--text-tertiary);
    margin-left: auto;
}
```

---

### Step 4: Add Backend API Endpoint

Create an API endpoint to handle thread linkage:

**File:** `AI_infrastructure/routes/your_module_routes.py`

```python
from flask import Blueprint, request, jsonify
from shared.database_utils import get_database_connection

your_module_bp = Blueprint('your_module', __name__)

@your_module_bp.route('/api/your-module/link-to-thread', methods=['POST'])
def link_to_thread():
    """
    Link your module item to a thread
    
    Body:
        item_id: Your item identifier
        thread_id: Thread identifier
        item_title: Item title (for display)
    
    Returns:
        {success: true, thread_id: "...", item_id: "..."}
    """
    try:
        data = request.json
        item_id = data.get('item_id')
        thread_id = data.get('thread_id')
        item_title = data.get('item_title')
        
        if not item_id or not thread_id:
            return jsonify({'success': False, 'error': 'Missing required fields'}), 400
        
        # Update thread record
        conn = get_database_connection('sessions')
        cursor = conn.cursor()
        
        cursor.execute("""
            UPDATE sessions.threads
            SET your_module_id = %s,
                your_module_title = %s,
                updated_at = NOW()
            WHERE thread_id = %s OR thread_slug = %s
        """, (item_id, item_title, thread_id, thread_id))
        
        conn.commit()
        conn.close()
        
        # Emit WebSocket event for real-time update
        from AI_infrastructure.core.realtime_manager import emit_websocket_event
        emit_websocket_event('thread_linked_to_your_module', {
            'thread_id': thread_id,
            'item_id': item_id,
            'item_title': item_title,
            'action': 'linked'
        })
        
        return jsonify({
            'success': True,
            'thread_id': thread_id,
            'item_id': item_id,
            'linked': True
        })
        
    except Exception as e:
        print(f"❌ [YourModule] Link error: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500
```

**Don't forget to register the blueprint in `flask_app.py`:**
```python
from routes.your_module_routes import your_module_bp
app.register_blueprint(your_module_bp)
```

---

### Step 5: Update Database Schema

Add columns to `sessions.threads` table for your module linkage:

```sql
ALTER TABLE sessions.threads
ADD COLUMN your_module_id VARCHAR(255),
ADD COLUMN your_module_title TEXT,
ADD INDEX idx_threads_your_module_id (your_module_id);
```

**Or use migration script:**
```python
# migrations/add_your_module_to_threads.py
def upgrade():
    conn = get_database_connection('sessions')
    cursor = conn.cursor()
    
    cursor.execute("""
        ALTER TABLE sessions.threads
        ADD COLUMN IF NOT EXISTS your_module_id VARCHAR(255),
        ADD COLUMN IF NOT EXISTS your_module_title TEXT
    """)
    
    cursor.execute("""
        CREATE INDEX IF NOT EXISTS idx_threads_your_module_id
        ON sessions.threads(your_module_id)
    """)
    
    conn.commit()
    conn.close()
```

---

## 🧪 Testing Your Integration

### Test 1: Verify ThreadCardRegistry Detects Your Module

```javascript
// In browser console after page load
console.log('Modules with thread card integration:', 
    Array.from(window.ThreadCardRegistry.modules.keys())
);
// Should include 'your_module'

console.log('Your module config:',
    window.ThreadCardRegistry.modules.get('your_module')
);
// Should show your drag_and_drop, badge, realtime_events config
```

### Test 2: Test Drag and Drop

1. Open your module sidebar
2. Drag one of your items
3. Drop it on a thread card (in sidebar, Prime, or agent column)
4. Check browser console for success message
5. Verify thread card shows your badge

### Test 3: Test Badge Display

1. Link an item to a thread (via drag-drop or API)
2. Refresh the page
3. Find the thread card
4. Verify your badge appears in Row 4
5. Click the badge - should trigger your click handler

### Test 4: Test Real-Time Updates

1. Open thread card in one browser tab
2. Link an item in another tab/window
3. Verify badge appears in first tab WITHOUT refresh
4. Check WebSocket event in console

---

## 📊 Complete Example: Synergy Module

See `UI/external/modules/synergy/` for complete working implementation:

- `manifest.json` - Has thread_card_integration section
- `synergy-thread-integration.js` - Implements all handlers
- `synergy.css` - Badge styling
- `AI_infrastructure/routes/synergy_routes.py` - Backend API

**Key files to reference:**
```
UI/external/modules/synergy/
├── manifest.json (thread_card_integration config)
├── synergy-thread-integration.js (drag/badge handlers)
└── synergy.css (badge styles)

AI_infrastructure/routes/
└── synergy_routes.py (link-to-thread endpoint)
```

---

## 🎨 Badge Styling Best Practices

### Badge Colors by Module Type

- **Green (#10b981)**: Projects/Workspaces (Synergy)
- **Orange (#f97316)**: Workflows/Processes
- **Blue (#3b82f6)**: Documents/Files
- **Purple (#8b5cf6)**: Data/Analytics
- **Yellow (#f59e0b)**: Tasks/To-Dos
- **Red (#ef4444)**: Alerts/Issues

### Badge Priority (Display Order)

Set `priority` in badge config:
- `1`: Most important (Synergy, primary projects)
- `2`: Secondary (Workflows, Documents)
- `3`: Tertiary (Tasks, Analytics)
- `4+`: Lower priority

Badges are sorted by priority (lower numbers appear first).

---

## 🚨 Common Issues

### Issue 1: Badge Doesn't Appear

**Symptoms:** Dropped item links successfully but no badge shows

**Solutions:**
1. Check `thread.your_module_id` is being saved to database
2. Verify badge condition evaluates to true: `thread.your_module_id !== null`
3. Check `render_function` name matches your actual function
4. Look for JavaScript errors in console

### Issue 2: Drag-and-Drop Not Working

**Symptoms:** Can't drag items or drop has no effect

**Solutions:**
1. Verify `draggable="true"` on your HTML elements
2. Check `ondragstart` handler is called (console.log)
3. Verify MIME type matches: `application/x-your-item`
4. Check ThreadCardRegistry registered your handler

### Issue 3: Real-Time Updates Not Working

**Symptoms:** Badge doesn't update without page refresh

**Solutions:**
1. Verify WebSocket event name matches manifest
2. Check backend emits event after linkage
3. Verify handler function is called (console.log)
4. Check RealtimeManager is connected

---

## 📚 Additional Resources

- **Module System Architecture:** `MODULE_SYSTEM_ARCHITECTURE_COMPLETE.md`
- **Module Integration Guide:** `MODULE_SYSTEM_INTEGRATION_GUIDE.md`
- **Thread Card Templates:** `UI/external/modules/thread-cards/thread-card-templates.js`
- **Thread Card Registry:** `THREAD_CARD_MODULE_REGISTRY_ARCHITECTURE.md`

---

## ✅ Integration Checklist

Before submitting your module with thread card integration:

- [ ] Added `thread_card_integration` section to manifest.json
- [ ] Implemented drag start/end handlers
- [ ] Implemented drop handler (linkToThread)
- [ ] Implemented badge renderer function
- [ ] Implemented realtime update handler
- [ ] Added `draggable="true"` to your HTML items
- [ ] Created backend API endpoint for linking
- [ ] Added database columns to sessions.threads
- [ ] Tested drag-and-drop functionality
- [ ] Tested badge display on thread cards
- [ ] Tested real-time updates via WebSocket
- [ ] Added CSS styling for badges
- [ ] Updated module documentation

---

**Status:** Ready for Production  
**Last Updated:** November 28, 2025  
**Maintained By:** Platform Architecture Team

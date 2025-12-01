# Manifest Schema Extension - Thread Card Integration

**Date:** November 28, 2025  
**Type:** Backward Compatible Extension  
**Status:** Ready for Implementation

---

## 📋 Schema Extension Overview

This document defines the **thread_card_integration** section that can be added to any existing module manifest.json to enable thread card integration.

---

## 🔧 Complete Schema Definition

### Base Schema (Existing - No Changes)

```json
{
  "id": "string (required)",
  "name": "string (required)",
  "version": "semver (required)",
  "description": "string (required)",
  "icon": "fontawesome-class (required)",
  "color": "hex-color (required)",
  
  "html_file": "relative-path.html",
  "js_file": "relative-path.js",
  "css_file": "relative-path.css",
  
  "required_platforms": ["platform-id"],
  "optional_platforms": ["platform-id"],
  
  "sidebar_position": "left|right",
  "sidebar_width": 450,
  "auto_load": false,
  "requires_auth": true,
  
  ...other existing fields...
}
```

### NEW: Thread Card Integration Section (Optional)

```json
{
  ...existing fields above...,
  
  "thread_card_integration": {
    "enabled": boolean,
    
    "drag_and_drop": {
      "accepts": [
        {
          "data_type": "string (unique identifier)",
          "mime_type": "application/x-your-type",
          "handler": "window.YourModule.handlerFunction"
        }
      ],
      "provides": [
        {
          "data_type": "string (same as accepts)",
          "mime_type": "application/x-your-type",
          "handler": "window.YourModule.dragStartHandler"
        }
      ]
    },
    
    "badge": {
      "enabled": boolean,
      "condition": "javascript-expression-as-string",
      "render_function": "window.YourModule.renderFunction",
      "config": {
        "icon": "fontawesome-class",
        "color": "hex-color",
        "label": "string",
        "tooltip_template": "string with {placeholders}",
        "click_action": "window.YourModule.clickHandler",
        "show_count": boolean,
        "priority": number
      }
    },
    
    "realtime_events": {
      "enabled": boolean,
      "events": ["event-name-1", "event-name-2"],
      "handler": "window.YourModule.realtimeHandler"
    },
    
    "database_fields": {
      "thread_link_column": "column-name",
      "thread_link_column_type": "VARCHAR|INTEGER|TEXT",
      "thread_metadata_column": "optional-title-column"
    }
  }
}
```

---

## 📖 Field Definitions

### thread_card_integration (object, optional)

Top-level configuration for thread card integration.

**Fields:**
- `enabled` (boolean, required): Master switch for thread card integration

---

### drag_and_drop (object, optional)

Defines drag-and-drop behavior.

#### accepts (array of objects, optional)

Defines what data types this module can accept when dropped on thread cards.

**Array Item Schema:**
- `data_type` (string, required): Unique identifier for this data type (e.g., "synergy-session")
- `mime_type` (string, required): MIME type for dataTransfer API (e.g., "application/x-synergy-session")
- `handler` (string, required): JavaScript function path to handle drop (e.g., "window.SynergyModule.linkToThread")

**Handler Signature:**
```javascript
async function(itemDataJson, threadId, targetLocation) {
    // itemDataJson: JSON string from dataTransfer
    // threadId: Thread being dropped on
    // targetLocation: 'prime', 'agent-1', etc.
}
```

#### provides (array of objects, optional)

Defines what data types this module provides for dragging.

**Array Item Schema:**
- `data_type` (string, required): Same as in accepts
- `mime_type` (string, required): Same MIME type
- `handler` (string, required): JavaScript function path for drag start

**Handler Signature:**
```javascript
function(event, itemId, itemData) {
    // event: DragEvent
    // itemId: Unique ID of dragged item
    // itemData: Object with item details
}
```

---

### badge (object, optional)

Defines badge display on thread cards.

**Fields:**

- `enabled` (boolean, required): Whether to show badge

- `condition` (string, required): JavaScript expression evaluating to boolean
  - Evaluated with `thread` object in scope
  - Example: `"thread.synergy_session_id !== null && thread.synergy_session_id !== ''"`
  - Example: `"thread.kanban_cards && thread.kanban_cards.length > 0"`

- `render_function` (string, required): JavaScript function path to render badge HTML
  - Example: `"window.SynergyModule.renderThreadBadge"`
  
- `config` (object, required): Badge display configuration
  - `icon` (string, required): FontAwesome class (e.g., "fa-project-diagram")
  - `color` (string, required): Hex color for badge background (e.g., "#10b981")
  - `label` (string, required): Badge text (e.g., "Synergy")
  - `tooltip_template` (string, optional): Tooltip with placeholders (e.g., "Linked to: {synergy_session_title}")
  - `click_action` (string, optional): JavaScript function for badge click (e.g., "window.SynergyModule.openSession")
  - `show_count` (boolean, optional): Whether to show count badge (e.g., for multiple items)
  - `priority` (number, optional): Display order priority (1 = highest, shown first)

**Render Function Signature:**
```javascript
function(thread, config) {
    // thread: Thread object with all fields
    // config: The badge.config object from manifest
    // Returns: HTML string for badge
}
```

**Click Action Signature:**
```javascript
function(itemId, threadId, event) {
    // itemId: Linked item identifier from thread
    // threadId: Thread ID
    // event: Click event (optional)
}
```

---

### realtime_events (object, optional)

Defines WebSocket event subscriptions.

**Fields:**

- `enabled` (boolean, required): Whether to subscribe to real-time events

- `events` (array of strings, required): WebSocket event names to subscribe to
  - Example: `["thread_linked_to_synergy", "synergy_session_updated"]`
  - Convention: Use snake_case
  
- `handler` (string, required): JavaScript function path to handle events
  - Example: `"window.SynergyModule.handleRealtimeUpdate"`

**Handler Signature:**
```javascript
function(eventData) {
    // eventData: Object with event details
    // Common fields: thread_id, item_id, action, timestamp
}
```

---

### database_fields (object, optional)

Defines database schema for linkage.

**Fields:**

- `thread_link_column` (string, required): Column name in `sessions.threads` table storing link
  - Example: `"synergy_session_id"`
  - Type: Usually VARCHAR or INTEGER
  
- `thread_link_column_type` (string, required): SQL column type
  - Example: `"VARCHAR(255)"`, `"INTEGER"`, `"TEXT"`
  
- `thread_metadata_column` (string, optional): Additional column for display data
  - Example: `"synergy_session_title"`
  - Used for badge tooltips without extra DB queries

---

## 📝 Complete Examples

### Example 1: Synergy Sessions (Full Featured)

```json
{
  "id": "synergy_sessions",
  "name": "Synergy Projects",
  "version": "1.0.0",
  "icon": "fa-project-diagram",
  "color": "#10b981",
  
  "thread_card_integration": {
    "enabled": true,
    
    "drag_and_drop": {
      "accepts": [{
        "data_type": "synergy-session",
        "mime_type": "application/x-synergy-session",
        "handler": "window.SynergyModule.linkThreadToSession"
      }],
      "provides": [{
        "data_type": "synergy-session",
        "mime_type": "application/x-synergy-session",
        "handler": "window.SynergyModule.startDragSession"
      }]
    },
    
    "badge": {
      "enabled": true,
      "condition": "thread.synergy_session_id !== null",
      "render_function": "window.SynergyModule.renderThreadBadge",
      "config": {
        "icon": "fa-project-diagram",
        "color": "#10b981",
        "label": "Synergy",
        "tooltip_template": "Linked to: {synergy_session_title}",
        "click_action": "window.SynergyModule.openSession",
        "show_count": false,
        "priority": 1
      }
    },
    
    "realtime_events": {
      "enabled": true,
      "events": [
        "thread_linked_to_synergy",
        "thread_unlinked_from_synergy",
        "synergy_session_updated"
      ],
      "handler": "window.SynergyModule.handleRealtimeUpdate"
    },
    
    "database_fields": {
      "thread_link_column": "synergy_session_id",
      "thread_link_column_type": "VARCHAR(255)",
      "thread_metadata_column": "synergy_session_title"
    }
  }
}
```

---

### Example 2: Kanban Tasks (With Count Badge)

```json
{
  "id": "inhouse_kanban",
  "name": "Production Workflow",
  "version": "3.0.1",
  "icon": "fa-industry",
  "color": "#00509E",
  
  "thread_card_integration": {
    "enabled": true,
    
    "drag_and_drop": {
      "accepts": [{
        "data_type": "kanban-card",
        "mime_type": "application/x-kanban-card",
        "handler": "window.InHouseKanban.linkCardToThread"
      }]
    },
    
    "badge": {
      "enabled": true,
      "condition": "thread.kanban_cards && thread.kanban_cards.length > 0",
      "render_function": "window.InHouseKanban.renderThreadBadge",
      "config": {
        "icon": "fa-tasks",
        "color": "#f59e0b",
        "label": "Tasks",
        "tooltip_template": "{count} production tasks linked",
        "click_action": "window.InHouseKanban.showLinkedTasks",
        "show_count": true,
        "priority": 2
      }
    },
    
    "realtime_events": {
      "enabled": true,
      "events": ["kanban_card_linked", "kanban_card_status_changed"],
      "handler": "window.InHouseKanban.handleRealtimeUpdate"
    },
    
    "database_fields": {
      "thread_link_column": "kanban_cards",
      "thread_link_column_type": "JSONB",
      "thread_metadata_column": "kanban_summary"
    }
  }
}
```

---

### Example 3: Documents (Simple Badge Only)

```json
{
  "id": "document_library",
  "name": "Document Library",
  "version": "1.0.0",
  "icon": "fa-file-alt",
  "color": "#3b82f6",
  
  "thread_card_integration": {
    "enabled": true,
    
    "drag_and_drop": {
      "accepts": [{
        "data_type": "document",
        "mime_type": "application/x-document",
        "handler": "window.DocumentLibrary.linkToThread"
      }]
    },
    
    "badge": {
      "enabled": true,
      "condition": "thread.linked_documents && thread.linked_documents.length > 0",
      "render_function": "window.DocumentLibrary.renderBadge",
      "config": {
        "icon": "fa-file-alt",
        "color": "#3b82f6",
        "label": "Docs",
        "show_count": true,
        "priority": 3
      }
    }
  }
}
```

---

## ✅ Validation Rules

### Required Combinations:

1. If `thread_card_integration.enabled = true`, at least ONE of these must exist:
   - `drag_and_drop.accepts`
   - `badge.enabled = true`

2. If `badge.enabled = true`, ALL these are required:
   - `badge.condition`
   - `badge.render_function`
   - `badge.config.icon`
   - `badge.config.color`
   - `badge.config.label`

3. If `realtime_events.enabled = true`, ALL these are required:
   - `realtime_events.events` (array with at least one event)
   - `realtime_events.handler`

### Optional Fields:

- `drag_and_drop.provides` (if module items aren't draggable)
- `badge.config.tooltip_template` (if no tooltip needed)
- `badge.config.click_action` (if badge isn't clickable)
- `badge.config.show_count` (defaults to false)
- `badge.config.priority` (defaults to 5)
- `database_fields.thread_metadata_column` (if no additional data needed)
- `realtime_events` (if no real-time updates needed)

---

## 🧪 Validation Script

```javascript
/**
 * Validate thread_card_integration section of manifest
 */
function validateThreadCardIntegration(manifest) {
    const errors = [];
    const integration = manifest.thread_card_integration;
    
    if (!integration) return errors; // Optional section
    
    if (!integration.enabled) return errors; // Disabled, skip validation
    
    // Must have at least drag-and-drop or badge
    if (!integration.drag_and_drop?.accepts?.length && !integration.badge?.enabled) {
        errors.push('Must have either drag_and_drop.accepts or badge.enabled when integration is enabled');
    }
    
    // Badge validation
    if (integration.badge?.enabled) {
        if (!integration.badge.condition) {
            errors.push('badge.condition is required when badge.enabled = true');
        }
        if (!integration.badge.render_function) {
            errors.push('badge.render_function is required');
        }
        if (!integration.badge.config) {
            errors.push('badge.config is required');
        } else {
            const config = integration.badge.config;
            if (!config.icon) errors.push('badge.config.icon is required');
            if (!config.color) errors.push('badge.config.color is required');
            if (!config.label) errors.push('badge.config.label is required');
        }
    }
    
    // Realtime events validation
    if (integration.realtime_events?.enabled) {
        if (!integration.realtime_events.events?.length) {
            errors.push('realtime_events.events array is required and must have at least one event');
        }
        if (!integration.realtime_events.handler) {
            errors.push('realtime_events.handler is required');
        }
    }
    
    return errors;
}
```

---

## 📚 Migration Guide

### Migrating Existing Hardcoded Integration

**Before (Hardcoded in thread-card-templates.js):**
```javascript
if (thread.synergy_session_id) {
    html += `<div class="thread-badge synergy-badge">...</div>`;
}
```

**After (Manifest-driven):**
```json
{
  "thread_card_integration": {
    "enabled": true,
    "badge": {
      "enabled": true,
      "condition": "thread.synergy_session_id !== null",
      "render_function": "window.SynergyModule.renderBadge",
      ...
    }
  }
}
```

**Steps:**
1. Add `thread_card_integration` to manifest.json
2. Move badge rendering to module's JS file
3. Remove hardcoded badge from thread-card-templates.js
4. Test via ThreadCardRegistry

---

**Last Updated:** November 28, 2025  
**Schema Version:** 1.0.0  
**Status:** Ready for Implementation

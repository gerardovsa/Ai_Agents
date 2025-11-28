# Thread Card Module Registry - Architecture Design

**Date:** November 28, 2025  
**Status:** Design Phase  
**Purpose:** Extend existing Module System with thread card integration capabilities

---

## 🎯 Core Concept

**Thread Info Cards = Single Source of Truth**

- **Current Problem:** Hardcoded badges (Synergy, Workflow, Automation) in thread card templates
- **Future Vision:** Modules declare thread card integration in existing manifest.json files
- **Key Benefit:** Add drag-drop/badges to modules without touching thread card code
- **Integration:** Extends existing ModuleLoader/ModuleRegistry (no breaking changes)

---

## 📋 Architecture Overview - Integration with Existing Module System

```
┌─────────────────────────────────────────────────────────────────┐
│                     THREAD INFO CARD (Core UI)                   │
│  ┌────────────────────────────────────────────────────────────┐ │
│  │ Row 1: Header (Title, Agent Badge, Actions)                │ │
│  │ Row 2: Meta (Message Count, Date, Time)                    │ │
│  │ Row 3: Thread ID Badge + Copy Dropdown                     │ │
│  │ Row 4: DYNAMIC MODULE BADGES (Auto-populated)  ← NEW       │ │
│  │ Row 5: Tags + Token Count                                  │ │
│  │ Row 6: Lock Controls                                       │ │
│  │ Row 7: Action Buttons                                      │ │
│  └────────────────────────────────────────────────────────────┘ │
│                            ↑                                     │
│              Reads from ThreadCardRegistry                      │
└─────────────────────────────────────────────────────────────────┘
                             ↑
                             │
┌────────────────────────────┴──────────────────────────────────┐
│         THREAD CARD REGISTRY (New Integration Layer)           │
│  ┌──────────────────────────────────────────────────────────┐ │
│  │  - Piggybacks on existing ModuleLoader                   │ │
│  │  - Reads thread_card_integration from manifests          │ │
│  │  - Provides badge/drop zone API to thread cards          │ │
│  │  - Manages WebSocket subscriptions                       │ │
│  │  - NO duplicate module scanning (uses ModuleLoader)      │ │
│  └──────────────────────────────────────────────────────────┘ │
└───────────────────────────────────────────────────────────────┘
                             ↑
                             │
                    Uses Existing Infrastructure
                             │
┌────────────────────────────┴──────────────────────────────────┐
│               EXISTING MODULE LOADER (UI/modules)              │
│  ┌──────────────────────────────────────────────────────────┐ │
│  │  ✓ Scans /modules/*/manifest.json                        │ │
│  │  ✓ Checks credentials via ModuleRegistry API            │ │
│  │  ✓ Generates sidebar buttons                            │ │
│  │  ✓ Loads HTML/CSS/JS on-demand                           │ │
│  └──────────────────────────────────────────────────────────┘ │
└───────────────────────────────────────────────────────────────┘
                             ↑
                             │
┌────────────────────────────┴──────────────────────────────────┐
│          EXISTING MODULE REGISTRY (Backend Python)             │
│  ┌──────────────────────────────────────────────────────────┐ │
│  │  ✓ Discovers modules in UI/modules/ and UI/external/    │ │
│  │  ✓ Validates credentials against schemas                │ │
│  │  ✓ Provides /api/modules/* endpoints                    │ │
│  └──────────────────────────────────────────────────────────┘ │
└───────────────────────────────────────────────────────────────┘
                             ↑
                             │
         ┌───────────────────┼───────────────────┐
         │                   │                   │
┌────────┴─────────┐ ┌──────┴────────┐ ┌───────┴──────────┐
│  Synergy Module  │ │ Kanban Module │ │ Quote Calc Mod   │
│  manifest.json   │ │ manifest.json │ │  manifest.json   │
│  + NEW section:  │ │ + NEW section │ │  + NEW section   │
│  thread_card_    │ │ thread_card_  │ │  thread_card_    │
│   integration {} │ │  integration  │ │   integration {} │
└──────────────────┘ └───────────────┘ └──────────────────┘
```

**Key Design Decision:** ThreadCardRegistry is a **lightweight integration layer** that reads from existing ModuleLoader infrastructure, NOT a parallel system.

---

## 📄 Extended Manifest Schema - Thread Card Integration

**Extends existing manifest.json format** (from MODULE_SYSTEM_ARCHITECTURE_COMPLETE.md)

**Base Schema (Already Exists):**
```json
{
  "id": "synergy_sessions",
  "name": "Synergy Projects", 
  "version": "1.0.0",
  "description": "Links threads to Synergy project sessions",
  "icon": "fa-project-diagram",
  "color": "#10b981",
  "html_file": "synergy.html",
  "js_file": "synergy.js",
  "css_file": "synergy.css",
  "required_platforms": [],
  "sidebar_position": "left",
  "auto_load": false
}
```

**NEW: Add thread_card_integration section** (backward compatible):

```json
{
  "id": "synergy_sessions",
  "name": "Synergy Projects",
  "version": "1.0.0",
  ...existing fields...,
  
  "thread_card_integration": {
    "enabled": true,
    "drag_and_drop": {
    "accepts": [
      {
        "data_type": "synergy-session",
        "mime_type": "application/x-synergy-session",
        "handler": "SynergyModule.handleThreadDrop"
      }
    ],
    "provides": [
      {
        "data_type": "synergy-session",
        "mime_type": "application/x-synergy-session",
        "handler": "SynergyModule.handleDragStart"
      }
    ]
  },
  
  "thread_card_badge": {
    "enabled": true,
    "condition": "thread.synergy_session_id !== null",
    "render_function": "SynergyModule.renderBadge",
    "badge_config": {
      "icon": "fa-project-diagram",
      "color": "#10b981",
      "label": "Synergy",
      "tooltip": "Linked to Synergy project",
      "click_action": "SynergyModule.openSynergySession",
      "show_count": false
    }
  },
  
  "database_schema": {
    "thread_column": "synergy_session_id",
    "thread_column_type": "VARCHAR",
    "link_table": null,
    "query_linked_items": "SELECT * FROM sessions.threads WHERE synergy_session_id = ?"
  },
  
  "api_endpoints": {
    "link": {
      "method": "POST",
      "path": "/api/synergy/{session_id}/link-thread",
      "body_params": ["thread_id"]
    },
    "unlink": {
      "method": "POST",
      "path": "/api/synergy/{session_id}/unlink-thread",
      "body_params": ["thread_id"]
    },
    "get_linked": {
      "method": "GET",
      "path": "/api/synergy/{session_id}/linked-threads"
    }
  },
  
  "realtime_updates": {
    "websocket_events": [
      "thread_linked_to_synergy",
      "thread_unlinked_from_synergy",
      "synergy_session_updated"
    ],
    "update_handler": "SynergyModule.handleRealtimeUpdate"
  },
  
  "css_overrides": {
    "badge_class": "synergy-badge-custom",
    "hover_color": "#059669"
  }
}
```

---

## 🏗️ Core Components

### 1. **ThreadCardRegistry** (Global Singleton) - Integration Layer

**File:** `UI/modules/thread-cards/thread-card-registry.js`

**Design Philosophy:** Piggyback on existing ModuleLoader, don't duplicate work!

```javascript
class ThreadCardRegistry {
    constructor() {
        this.modules = new Map(); // module_id → thread_card_integration config
        this.dragHandlers = new Map(); // data_type → handler
        this.badgeRenderers = new Map(); // module_id → render function
        this.realtimeSubscriptions = new Map(); // event_name → handlers[]
        this.initialized = false;
    }

    /**
     * PHASE 1: Initialize using existing ModuleLoader data
     * NO duplicate module scanning - reuse ModuleLoader.modules
     */
    async initialize() {
        console.log('🔍 [ThreadCardRegistry] Initializing...');
        
        // Wait for ModuleLoader to finish (it runs first)
        if (!window.moduleLoader || !window.moduleLoader.modules) {
            console.warn('[ThreadCardRegistry] ModuleLoader not ready, waiting...');
            await this.waitForModuleLoader();
        }
        
        console.log('[ThreadCardRegistry] ModuleLoader ready, processing modules...');
        
        // Extract thread card integration from loaded modules
        for (const [moduleId, manifest] of window.moduleLoader.modules) {
            if (manifest.thread_card_integration?.enabled) {
                await this.registerThreadCardIntegration(moduleId, manifest);
            }
        }
        
        console.log(`✅ [ThreadCardRegistry] Registered ${this.modules.size} modules with thread card integration`);
        this.initialized = true;
        this.notifyReady();
    }

    /**
     * Wait for ModuleLoader to initialize
     */
    async waitForModuleLoader() {
        return new Promise((resolve) => {
            const checkInterval = setInterval(() => {
                if (window.moduleLoader?.modules?.size > 0) {
                    clearInterval(checkInterval);
                    resolve();
                }
            }, 100);
            
            // Timeout after 10 seconds
            setTimeout(() => {
                clearInterval(checkInterval);
                console.error('[ThreadCardRegistry] ModuleLoader timeout');
                resolve();
            }, 10000);
        });
    }

    /**
     * PHASE 2: Register thread card integration from module
     * Reads thread_card_integration section from manifest
     */
    async registerThreadCardIntegration(moduleId, manifest) {
        try {
            const integration = manifest.thread_card_integration;
            
            if (!integration || !integration.enabled) {
                console.log(`[ThreadCardRegistry] Module ${moduleId} has no thread card integration`);
                return;
            }
            
            console.log(`📦 [ThreadCardRegistry] Registering ${moduleId} thread card integration`);
            
            // Store integration config
            this.modules.set(moduleId, integration);
            
            // Register drag-and-drop handlers
            if (integration.drag_and_drop?.accepts) {
                integration.drag_and_drop.accepts.forEach(accept => {
                    this.dragHandlers.set(accept.data_type, {
                        moduleId: moduleId,
                        handler: accept.handler,
                        mimeType: accept.mime_type
                    });
                    console.log(`  ✓ Drag handler: ${accept.data_type} → ${accept.handler}`);
                });
            }
            
            // Register badge renderer
            if (integration.badge?.enabled) {
                this.badgeRenderers.set(moduleId, {
                    condition: integration.badge.condition,
                    renderFunction: integration.badge.render_function,
                    config: integration.badge.config
                });
                console.log(`  ✓ Badge renderer: ${integration.badge.config.label}`);
            }
            
            // Register real-time event handlers
            if (integration.realtime_events?.events) {
                integration.realtime_events.events.forEach(event => {
                    if (!this.realtimeSubscriptions.has(event)) {
                        this.realtimeSubscriptions.set(event, []);
                    }
                    this.realtimeSubscriptions.get(event).push({
                        moduleId: moduleId,
                        handler: integration.realtime_events.handler
                    });
                    console.log(`  ✓ WebSocket event: ${event}`);
                });
            }
            
            console.log(`✅ [ThreadCardRegistry] Module ${moduleId} integrated successfully`);
            
        } catch (error) {
            console.error(`❌ [ThreadCardRegistry] Failed to register ${moduleId}:`, error);
        }
    }

    /**
     * PHASE 3: Render badges for a thread
     * Called by thread card template
     */
    renderBadgesForThread(thread) {
        const badges = [];
        
        for (const [moduleId, config] of this.badgeRenderers) {
            // Evaluate condition (e.g., "thread.synergy_session_id !== null")
            if (this.evaluateCondition(config.condition, thread)) {
                const renderFn = this.resolveFunction(config.renderFunction);
                if (renderFn) {
                    badges.push(renderFn(thread, config.config));
                }
            }
        }
        
        return badges.join('');
    }

    /**
     * PHASE 4: Handle drop events
     * Called by thread card drop handler
     */
    async handleDrop(event, threadId, targetLocation) {
        const dataTransferTypes = Array.from(event.dataTransfer.types);
        
        // Check all registered drag handlers
        for (const [dataType, handler] of this.dragHandlers) {
            if (dataTransferTypes.includes(handler.mimeType)) {
                const data = event.dataTransfer.getData(handler.mimeType);
                
                console.log(`🎯 [Registry] Handling drop: ${dataType} → thread ${threadId}`);
                
                const handlerFn = this.resolveFunction(handler.handler);
                if (handlerFn) {
                    await handlerFn(data, threadId, targetLocation);
                    return true; // Handled
                }
            }
        }
        
        return false; // Not handled
    }

    /**
     * PHASE 5: Real-time update broadcast
     * Called when WebSocket event received
     */
    handleRealtimeEvent(eventName, eventData) {
        const handlers = this.realtimeSubscriptions.get(eventName);
        
        if (handlers) {
            console.log(`📡 [Registry] Broadcasting ${eventName} to ${handlers.length} handlers`);
            
            handlers.forEach(({ moduleId, handler }) => {
                const handlerFn = this.resolveFunction(handler);
                if (handlerFn) {
                    handlerFn(eventData);
                }
            });
        }
    }

    /**
     * Helper: Resolve function from string path
     * "SynergyModule.handleDrop" → window.SynergyModule.handleDrop
     */
    resolveFunction(path) {
        const parts = path.split('.');
        let fn = window;
        for (const part of parts) {
            fn = fn[part];
            if (!fn) return null;
        }
        return fn;
    }

    /**
     * Helper: Evaluate condition string
     * "thread.synergy_session_id !== null" → true/false
     */
    evaluateCondition(condition, thread) {
        try {
            return new Function('thread', `return ${condition}`)(thread);
        } catch (error) {
            console.warn('[Registry] Invalid condition:', condition, error);
            return false;
        }
    }

    /**
     * Get all registered modules
     */
    getModules() {
        return Array.from(this.modules.values());
    }

    /**
     * Notify that registry is ready
     */
    notifyReady() {
        window.dispatchEvent(new CustomEvent('thread-card-registry-ready', {
            detail: { modules: this.getModules() }
        }));
    }
}

// Global singleton instance
window.ThreadCardRegistry = new ThreadCardModuleRegistry();
```

---

### 2. **Refactored Thread Card Template**

**File:** `UI/external/modules/thread-cards/thread-card-templates.js`

**Current (Hardcoded):**
```javascript
uiLinksRow(thread, location, synergyMeta) {
    let html = '';
    
    // Hardcoded Synergy badge
    if (thread.synergy_session_id) {
        html += `<div class="thread-badge synergy-badge">...</div>`;
    }
    
    // Hardcoded Workflow badge
    if (thread.workflow_slug) {
        html += `<div class="thread-badge workflow-badge">...</div>`;
    }
    
    return html;
}
```

**New (Dynamic):**
```javascript
uiLinksRow(thread, location, synergyMeta) {
    // Registry automatically renders all registered module badges
    if (window.ThreadCardRegistry?.initialized) {
        return window.ThreadCardRegistry.renderBadgesForThread(thread);
    }
    
    // Fallback: render hardcoded badges while registry initializes
    return this.renderFallbackBadges(thread);
}
```

---

### 3. **Backend Module Manifest API**

**File:** `AI_infrastructure/routes/module_registry_routes.py`

```python
from flask import Blueprint, jsonify
import os
import json

registry_bp = Blueprint('module_registry', __name__)

@registry_bp.route('/api/thread-card-modules/manifests', methods=['GET'])
def get_module_manifests():
    """
    Scan UI/modules/ for manifest.json files
    Returns list of manifest paths
    """
    manifests = []
    modules_dir = 'UI/modules'
    
    for root, dirs, files in os.walk(modules_dir):
        if 'manifest.json' in files:
            manifest_path = os.path.join(root, 'manifest.json')
            # Convert to web path
            relative_path = manifest_path.replace('UI/', '')
            manifests.append(relative_path)
    
    return jsonify({
        'success': True,
        'count': len(manifests),
        'manifests': manifests
    })

@registry_bp.route('/api/thread-card-modules/register', methods=['POST'])
def register_module_dynamically():
    """
    Hot-reload: Register new module without restart
    Body: { "manifest_path": "modules/new_module/manifest.json" }
    """
    data = request.json
    manifest_path = data.get('manifest_path')
    
    # Validate manifest exists
    full_path = os.path.join('UI', manifest_path)
    if not os.path.exists(full_path):
        return jsonify({'success': False, 'error': 'Manifest not found'}), 404
    
    # Broadcast to all connected WebSocket clients
    emit_websocket_event('module_registered', {
        'manifest_path': manifest_path,
        'timestamp': datetime.now().isoformat()
    })
    
    return jsonify({
        'success': True,
        'message': f'Module registered: {manifest_path}'
    })
```

---

### 4. **Real-Time Update System**

**WebSocket Event Flow:**

```javascript
// Listen for real-time updates
window.RealtimeManager.subscribe('thread_linked_to_synergy', (data) => {
    const { thread_id, synergy_session_id } = data;
    
    // Registry broadcasts to all module handlers
    window.ThreadCardRegistry.handleRealtimeEvent('thread_linked_to_synergy', data);
    
    // Thread card auto-refreshes its badges
    window.ThreadManager.refreshThreadCard(thread_id);
});
```

---

## 🎨 Example Module Integration

### Synergy Module Manifest

**File:** `UI/modules/synergy/manifest.json`

```json
{
  "module_id": "synergy_sessions",
  "version": "1.0.0",
  "display_name": "Synergy Projects",
  "description": "Links threads to Synergy project sessions",
  
  "drag_and_drop": {
    "accepts": [
      {
        "data_type": "synergy-session",
        "mime_type": "application/x-synergy-session",
        "handler": "window.SynergyModule.linkThreadToSession"
      }
    ],
    "provides": [
      {
        "data_type": "synergy-session",
        "mime_type": "application/x-synergy-session",
        "handler": "window.SynergyModule.startDragSession"
      }
    ]
  },
  
  "thread_card_badge": {
    "enabled": true,
    "condition": "thread.synergy_session_id !== null && thread.synergy_session_id !== ''",
    "render_function": "window.SynergyModule.renderThreadBadge",
    "badge_config": {
      "icon": "fa-project-diagram",
      "color": "#10b981",
      "label": "Synergy",
      "tooltip_template": "Linked to: {synergy_session_title}",
      "click_action": "window.SynergyModule.openSession",
      "show_count": false,
      "priority": 1
    }
  },
  
  "database_schema": {
    "thread_column": "synergy_session_id",
    "thread_column_type": "VARCHAR",
    "link_table": null
  },
  
  "api_endpoints": {
    "link": {
      "method": "POST",
      "path": "/api/synergy/{session_id}/link-thread",
      "body_params": ["thread_id"]
    },
    "get_linked": {
      "method": "GET",
      "path": "/api/synergy/{session_id}/linked-threads"
    }
  },
  
  "realtime_updates": {
    "websocket_events": [
      "thread_linked_to_synergy",
      "synergy_session_updated"
    ],
    "update_handler": "window.SynergyModule.handleRealtimeUpdate"
  }
}
```

### Synergy Module Handler

**File:** `UI/modules/synergy/synergy-thread-integration.js`

```javascript
window.SynergyModule = {
    /**
     * Render badge for thread card
     */
    renderThreadBadge(thread, config) {
        const sessionTitle = thread.synergy_session_title || 'Unknown Project';
        
        return `
            <div class="thread-badge synergy-badge" 
                 style="background: ${config.color};"
                 title="${config.tooltip_template.replace('{synergy_session_title}', sessionTitle)}"
                 onclick="${config.click_action}('${thread.synergy_session_id}')">
                <i class="fas ${config.icon}"></i>
                <span>${config.label}</span>
            </div>
        `;
    },

    /**
     * Handle thread drop on synergy session
     */
    async linkThreadToSession(sessionData, threadId, targetLocation) {
        const sessionId = JSON.parse(sessionData).session_id;
        
        const response = await fetch(`/api/synergy/${sessionId}/link-thread`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ thread_id: threadId })
        });
        
        if (response.ok) {
            console.log(`✅ Thread ${threadId} linked to Synergy ${sessionId}`);
            // Trigger badge refresh
            window.ThreadManager.refreshThreadCard(threadId);
        }
    },

    /**
     * Handle real-time updates
     */
    handleRealtimeUpdate(eventData) {
        const { thread_id } = eventData;
        // Refresh thread card badge
        window.ThreadManager.refreshThreadCard(thread_id);
    },

    /**
     * Open synergy session
     */
    openSession(sessionId) {
        window.synergyBoard?.expandCard(sessionId);
    }
};
```

---

## 🚀 Developer Experience

### Adding a New Module (e.g., Kanban Tasks)

**Step 1: Create manifest**
```bash
UI/modules/kanban/manifest.json
```

**Step 2: Define integration**
```json
{
  "module_id": "kanban_tasks",
  "drag_and_drop": {
    "accepts": [
      {
        "data_type": "kanban-card",
        "mime_type": "application/x-kanban-card",
        "handler": "window.KanbanModule.linkTaskToThread"
      }
    ]
  },
  "thread_card_badge": {
    "enabled": true,
    "condition": "thread.kanban_cards && thread.kanban_cards.length > 0",
    "render_function": "window.KanbanModule.renderBadge",
    "badge_config": {
      "icon": "fa-tasks",
      "color": "#f59e0b",
      "label": "Tasks",
      "show_count": true
    }
  }
}
```

**Step 3: Implement handler**
```javascript
// UI/modules/kanban/kanban-thread-integration.js
window.KanbanModule = {
    renderBadge(thread, config) {
        const count = thread.kanban_cards?.length || 0;
        return `<div class="thread-badge kanban-badge">
            <i class="fas ${config.icon}"></i>
            <span>${config.label} (${count})</span>
        </div>`;
    },
    
    async linkTaskToThread(cardData, threadId) {
        // Implementation
    }
};
```

**Step 4: Reload (HOT RELOAD)**
```javascript
// No restart needed! Registry auto-discovers
await fetch('/api/thread-card-modules/register', {
    method: 'POST',
    body: JSON.stringify({ manifest_path: 'modules/kanban/manifest.json' })
});
```

**Result:** Thread cards immediately show Kanban badges and accept Kanban card drops!

---

## 📊 Benefits

### 1. **Zero Touch Thread Cards**
- Add modules without editing thread card code
- Single source of truth (thread cards) stays consistent
- Eliminates merge conflicts in core UI code

### 2. **Hot Reload Support**
- Register new modules without server restart
- Update manifests dynamically
- A/B test different badge designs

### 3. **Real-Time Sync**
- WebSocket events broadcast to all modules
- Thread cards auto-refresh when linkages change
- Multi-user environments stay synchronized

### 4. **Developer Friendly**
- Clear manifest schema (JSON)
- Simple handler functions (no complex APIs)
- Example modules to copy from

### 5. **Future Proof**
- Add unlimited module types (Calendar, Documents, Emails, etc.)
- Each module is isolated (no cross-contamination)
- Easy to deprecate old modules (just remove manifest)

---

## 🧪 Testing Strategy

### Unit Tests
```javascript
describe('ThreadCardModuleRegistry', () => {
    it('should discover manifests on initialization', async () => {
        await registry.initialize();
        expect(registry.modules.size).toBeGreaterThan(0);
    });
    
    it('should render badges from registered modules', () => {
        const thread = { synergy_session_id: 'sess_123' };
        const html = registry.renderBadgesForThread(thread);
        expect(html).toContain('synergy-badge');
    });
    
    it('should handle drop events via registry', async () => {
        const event = createMockDropEvent('application/x-synergy-session', 'sess_123');
        const handled = await registry.handleDrop(event, 'thread_456', 'prime');
        expect(handled).toBe(true);
    });
});
```

### Integration Tests
- Test Synergy module linking
- Test Workflow module linking
- Test hot-reload of new module
- Test real-time badge updates

---

## 📝 Implementation Checklist

### Phase 1: Core Registry (2 hours)
- [ ] Create `ThreadCardModuleRegistry` class
- [ ] Implement manifest discovery
- [ ] Implement module registration
- [ ] Create backend `/api/thread-card-modules/manifests` endpoint

### Phase 2: Dynamic Rendering (2 hours)
- [ ] Refactor thread card templates to use registry
- [ ] Implement `renderBadgesForThread()` method
- [ ] Add fallback for uninitialized registry
- [ ] Test badge rendering with Synergy module

### Phase 3: Drag-and-Drop Integration (2 hours)
- [ ] Refactor `handleDrop()` to use registry
- [ ] Register Synergy drag handlers
- [ ] Register Workflow drag handlers
- [ ] Test drop events via registry

### Phase 4: Real-Time Updates (2 hours)
- [ ] Create WebSocket event subscription system
- [ ] Implement `handleRealtimeEvent()` method
- [ ] Connect to existing WebSocket manager
- [ ] Test badge refresh on link/unlink

### Phase 5: Example Modules (1 hour)
- [ ] Create Synergy manifest.json
- [ ] Create Workflow manifest.json
- [ ] Create example Kanban module
- [ ] Document developer guide

### Phase 6: Hot Reload (1 hour)
- [ ] Implement `/api/thread-card-modules/register` endpoint
- [ ] Add hot-reload UI in settings
- [ ] Test dynamic module registration
- [ ] Add error handling for invalid manifests

---

## 🎉 Success Metrics

**Before (Hardcoded):**
- Add new module type: Edit 5+ files, 200+ lines of code
- Risk breaking existing badges
- Manual real-time update wiring

**After (Registry):**
- Add new module type: Create 2 files (manifest + handler), ~50 lines
- Zero risk to thread cards (isolated)
- Automatic real-time updates

**Developer Time Savings:**
- New module integration: 4 hours → 30 minutes (87% reduction)
- Testing: Isolated unit tests per module
- Maintenance: Update manifest, no code changes

---

**Status:** Ready for Implementation  
**Estimated Time:** 10 hours total  
**Breaking Changes:** None (backward compatible)  
**Priority:** HIGH (architectural foundation)

# AI Agent Module Development Guide
## Complete Instructions for Creating Database-Backed UI Modules

**Version:** 1.0.0  
**Last Updated:** November 30, 2025  
**Purpose:** Enable AI agents to create production-ready, database-backed UI modules following established patterns  
**Audience:** AI assistants (Claude, GPT-4, DeepSeek, etc.) tasked with building new modules

---

## Table of Contents

1. [Overview](#overview)
2. [Architecture Pattern](#architecture-pattern)
3. [File Structure Requirements](#file-structure-requirements)
4. [Database Schema Design](#database-schema-design)
5. [Flask API Endpoint Pattern](#flask-api-endpoint-pattern)
6. [JavaScript Module Pattern](#javascript-module-pattern)
7. [CSS Styling Guidelines](#css-styling-guidelines)
8. [Integration Steps](#integration-steps)
9. [Testing Checklist](#testing-checklist)
10. [Complete Code Examples](#complete-code-examples)

---

## Overview

### What This Guide Covers

This guide provides **explicit, copy-paste-ready instructions** for AI agents to create new modules in the AI Agents Platform. All modules follow a **3-tier architecture**:

1. **Database Layer** (PostgreSQL/Supabase)
2. **Backend API Layer** (Flask/Python)
3. **Frontend Layer** (JavaScript + CSS)

### Key Principles

✅ **Database-backed persistence** (NOT localStorage)  
✅ **RESTful API design** with JWT authentication  
✅ **Event-driven updates** via CustomEvents  
✅ **Responsive design** (mobile-first CSS)  
✅ **Consistent patterns** across all modules  
✅ **Comprehensive error handling** at every layer

### Example Reference: Onboarding System

The **onboarding system** serves as the **reference implementation** for all future modules. It includes:

- **Database Table:** `ai_infrastructure.user_training` (25 columns, JSONB fields)
- **Flask Routes:** 8 authenticated endpoints at `/api/onboarding/*`
- **JavaScript Modules:** 5 classes (API, FRE, Checklist, Tours, etc.)
- **CSS Styling:** 800+ lines with animations and responsive design

**Location:** `UI/modules/onboarding/` + `AI_infrastructure/routes/onboarding_routes.py`

---

## Architecture Pattern

### 3-Tier Architecture Diagram

```
┌─────────────────────────────────────────────────────────────┐
│                      BROWSER (Frontend)                      │
│  - JavaScript ES6 Classes (window.* globals)                │
│  - CustomEvent dispatching for cross-component communication │
│  - Fetch API for backend calls                              │
│  - CSS with CSS variables for theming                       │
└────────────────────┬────────────────────────────────────────┘
                     │ HTTPS Requests
                     │ Authorization: Bearer <JWT>
                     ↓
┌─────────────────────────────────────────────────────────────┐
│                    FLASK SERVER (Backend)                    │
│  - Blueprint-based modular routes                           │
│  - @require_auth decorator on all endpoints                 │
│  - JSON request/response format                             │
│  - psycopg2 for database operations                         │
└────────────────────┬────────────────────────────────────────┘
                     │ SQL Queries
                     │ SELECT/INSERT/UPDATE/DELETE
                     ↓
┌─────────────────────────────────────────────────────────────┐
│              POSTGRESQL DATABASE (Supabase)                  │
│  - Schema: ai_infrastructure (main schema)                  │
│  - JSONB columns for flexible data                          │
│  - Indexes on frequently queried columns                    │
│  - Triggers for auto-updating timestamps                    │
└─────────────────────────────────────────────────────────────┘
```

### Data Flow Example: User Completes Onboarding Step

```
1. USER CLICKS: "Create First Thread" button
   ↓
2. FRONTEND DISPATCHES: CustomEvent('thread:created')
   ↓
3. JAVASCRIPT LISTENS: OnboardingChecklist.completeStep('first-thread')
   ↓
4. API CALL: POST /api/onboarding/complete-step {stepId, xp}
   ↓
5. FLASK VALIDATES: JWT token, user_id extraction
   ↓
6. DATABASE UPDATE: UPDATE user_training SET completed_steps = array_append(...), total_xp = total_xp + 50
   ↓
7. RESPONSE: {success: true, data: {total_xp: 150, proficiency_level: 'beginner'}}
   ↓
8. FRONTEND UPDATES: UI shows checkmark, +50 XP animation, progress bar update
   ↓
9. EVENT DISPATCHED: CustomEvent('onboarding:step-completed', {stepId, xp})
```

---

## File Structure Requirements

### Directory Organization

```
AI_agents/
├── data/
│   └── migrations/
│       └── YYYYMMDD_add_[module_name]_table.sql
│
├── AI_infrastructure/
│   ├── routes/
│   │   └── [module_name]_routes.py
│   └── docs/
│       └── user_instructions/
│           └── [MODULE_NAME]_IMPLEMENTATION_COMPLETE.md
│
└── UI/
    ├── modules/
    │   └── [module-name]/
    │       ├── [module-name]-api.js
    │       ├── [module-name]-[feature].js
    │       └── [module-name]-[feature2].js
    └── styles/
        └── [module-name].css
```

### Naming Conventions

| Component | Format | Example |
|-----------|--------|---------|
| **Database Table** | `{schema}.{module_name}` | `ai_infrastructure.user_training` |
| **Migration File** | `YYYYMMDD_add_{name}_table.sql` | `20251129_add_user_training_table.sql` |
| **Flask Routes** | `{module_name}_routes.py` | `onboarding_routes.py` |
| **JavaScript Dir** | `UI/modules/{module-name}/` | `UI/modules/onboarding/` |
| **JavaScript Files** | `{module-name}-{feature}.js` | `onboarding-checklist.js` |
| **CSS File** | `UI/styles/{module-name}.css` | `UI/styles/onboarding.css` |
| **API Endpoints** | `/api/{module-name}/{action}` | `/api/onboarding/complete-step` |

---

## Database Schema Design

### Step 1: Design Your Table

**Rules:**
- Primary key: `id SERIAL PRIMARY KEY`
- Foreign key to users: `user_id INTEGER REFERENCES ai_infrastructure.users(id) ON DELETE CASCADE`
- Timestamps: `created_at TIMESTAMPTZ DEFAULT NOW()`, `updated_at TIMESTAMPTZ DEFAULT NOW()`
- Use JSONB for arrays/objects: `completed_steps JSONB DEFAULT '[]'::jsonb`
- Add indexes on frequently queried columns

### Step 2: Migration File Template

**File:** `data/migrations/YYYYMMDD_add_[module_name]_table.sql`

```sql
-- =====================================================
-- MODULE: [Module Name]
-- PURPOSE: [Brief description of module functionality]
-- CREATED: YYYY-MM-DD
-- =====================================================

BEGIN;

-- Drop existing table if exists (for development only)
DROP TABLE IF EXISTS ai_infrastructure.[module_name] CASCADE;

-- Create main table
CREATE TABLE ai_infrastructure.[module_name] (
    -- Primary key
    id SERIAL PRIMARY KEY,
    
    -- Foreign key to users
    user_id INTEGER NOT NULL REFERENCES ai_infrastructure.users(id) ON DELETE CASCADE,
    
    -- Boolean flags
    is_active BOOLEAN DEFAULT TRUE,
    is_completed BOOLEAN DEFAULT FALSE,
    
    -- Integer counters
    total_count INTEGER DEFAULT 0,
    progress_percentage INTEGER DEFAULT 0,
    
    -- Text fields
    status TEXT DEFAULT 'pending',
    notes TEXT,
    
    -- JSONB fields for flexible data
    metadata JSONB DEFAULT '{}'::jsonb,
    configuration JSONB DEFAULT '{}'::jsonb,
    data_array JSONB DEFAULT '[]'::jsonb,
    
    -- Timestamps
    completed_at TIMESTAMPTZ,
    last_interaction_at TIMESTAMPTZ,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Create indexes for performance
CREATE INDEX idx_[module_name]_user_id ON ai_infrastructure.[module_name](user_id);
CREATE INDEX idx_[module_name]_status ON ai_infrastructure.[module_name](status);
CREATE INDEX idx_[module_name]_is_active ON ai_infrastructure.[module_name](is_active);
CREATE INDEX idx_[module_name]_created_at ON ai_infrastructure.[module_name](created_at);

-- Create trigger for auto-updating updated_at
CREATE OR REPLACE FUNCTION update_[module_name]_timestamp()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trigger_update_[module_name]_timestamp
BEFORE UPDATE ON ai_infrastructure.[module_name]
FOR EACH ROW
EXECUTE FUNCTION update_[module_name]_timestamp();

-- Insert default records for existing users
INSERT INTO ai_infrastructure.[module_name] (user_id)
SELECT id FROM ai_infrastructure.users
ON CONFLICT DO NOTHING;

-- Add table and column comments
COMMENT ON TABLE ai_infrastructure.[module_name] IS '[Module description and purpose]';
COMMENT ON COLUMN ai_infrastructure.[module_name].user_id IS 'Foreign key to users table';
COMMENT ON COLUMN ai_infrastructure.[module_name].metadata IS 'Flexible JSONB storage for additional data';

COMMIT;

-- =====================================================
-- ROLLBACK SCRIPT (if needed)
-- =====================================================
-- DROP TRIGGER IF EXISTS trigger_update_[module_name]_timestamp ON ai_infrastructure.[module_name];
-- DROP FUNCTION IF EXISTS update_[module_name]_timestamp();
-- DROP TABLE IF EXISTS ai_infrastructure.[module_name] CASCADE;
```

### Step 3: JSONB Column Guidelines

**When to use JSONB:**
- Arrays of strings/objects: `completed_steps JSONB DEFAULT '[]'::jsonb`
- Nested objects: `configuration JSONB DEFAULT '{}'::jsonb`
- Variable structure data: `metadata JSONB DEFAULT '{}'::jsonb`

**JSONB Query Examples:**
```sql
-- Append to array
UPDATE user_training 
SET completed_steps = completed_steps || '["new-step"]'::jsonb 
WHERE user_id = 1;

-- Update object property
UPDATE user_training 
SET metadata = jsonb_set(metadata, '{key}', '"value"'::jsonb) 
WHERE user_id = 1;

-- Check array contains value
SELECT * FROM user_training 
WHERE completed_steps @> '["step-1"]'::jsonb;

-- Extract object property
SELECT metadata->>'key' FROM user_training WHERE user_id = 1;
```

---

## Flask API Endpoint Pattern

### Step 1: Create Routes File

**File:** `AI_infrastructure/routes/[module_name]_routes.py`

```python
"""
FILE: AI_infrastructure/routes/[module_name]_routes.py
PURPOSE: Flask API endpoints for [Module Name] operations

ENDPOINTS:
- GET    /api/[module-name]/status          - Get user's module data
- POST   /api/[module-name]/create          - Create new record
- POST   /api/[module-name]/update          - Update existing record
- POST   /api/[module-name]/delete          - Delete record
- POST   /api/[module-name]/action          - Perform module-specific action
- GET    /api/[module-name]/analytics       - Admin analytics (role: admin)

AUTHENTICATION:
All endpoints require JWT authentication via @auth_manager.require_auth decorator

RESPONSE FORMAT:
Success: {success: True, data: {...}}
Error:   {success: False, error: "Error message"}

LAST MODIFIED: YYYY-MM-DD - Initial implementation
"""

from flask import Blueprint, request, jsonify
from AI_infrastructure.auth.user_auth import UserAuthManager
from shared.database_utils import get_database_connection
import traceback

# Initialize authentication manager
auth_manager = UserAuthManager()

# Create Blueprint
[module_name]_bp = Blueprint('[module_name]', __name__)


# =====================================================
# HELPER FUNCTIONS
# =====================================================

def get_[module_name]_record(user_id):
    """
    Get [module name] record for user from database
    
    Args:
        user_id (int): User ID
        
    Returns:
        dict or None: Record data or None if not found
    """
    try:
        conn = get_database_connection('ai_infrastructure')
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT 
                id, user_id, is_active, status, metadata,
                created_at, updated_at
            FROM ai_infrastructure.[module_name]
            WHERE user_id = %s
            ORDER BY created_at DESC
            LIMIT 1
        """, (user_id,))
        
        row = cursor.fetchone()
        conn.close()
        
        if row:
            return {
                'id': row[0],
                'user_id': row[1],
                'is_active': row[2],
                'status': row[3],
                'metadata': row[4],
                'created_at': row[5].isoformat() if row[5] else None,
                'updated_at': row[6].isoformat() if row[6] else None
            }
        
        return None
        
    except Exception as e:
        print(f"❌ Error fetching [module name] record: {e}")
        traceback.print_exc()
        return None


def create_[module_name]_record(user_id):
    """
    Create new [module name] record for user
    
    Args:
        user_id (int): User ID
        
    Returns:
        dict or None: Created record or None on error
    """
    try:
        conn = get_database_connection('ai_infrastructure')
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT INTO ai_infrastructure.[module_name] (user_id)
            VALUES (%s)
            RETURNING id, user_id, is_active, status, created_at
        """, (user_id,))
        
        row = cursor.fetchone()
        conn.commit()
        conn.close()
        
        if row:
            return {
                'id': row[0],
                'user_id': row[1],
                'is_active': row[2],
                'status': row[3],
                'created_at': row[4].isoformat() if row[4] else None
            }
        
        return None
        
    except Exception as e:
        print(f"❌ Error creating [module name] record: {e}")
        traceback.print_exc()
        return None


# =====================================================
# API ENDPOINTS
# =====================================================

@[module_name]_bp.route('/api/[module-name]/status', methods=['GET'])
@auth_manager.require_auth
def get_status():
    """
    Get user's [module name] status from database
    
    Returns:
        JSON: {success: bool, data: {...}}
    """
    try:
        user_id = request.user_id  # Injected by @require_auth
        
        print(f"🔧 Fetching [module name] status for user {user_id}")
        
        # Get existing record or create new one
        record = get_[module_name]_record(user_id)
        
        if not record:
            print(f"📝 Creating new [module name] record for user {user_id}")
            record = create_[module_name]_record(user_id)
        
        if record:
            return jsonify({
                'success': True,
                'data': record
            }), 200
        else:
            return jsonify({
                'success': False,
                'error': 'Failed to fetch or create record'
            }), 500
            
    except Exception as e:
        print(f"❌ Error in get_status: {e}")
        traceback.print_exc()
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@[module_name]_bp.route('/api/[module-name]/update', methods=['POST'])
@auth_manager.require_auth
def update_record():
    """
    Update user's [module name] record
    
    Request Body:
        {
            "status": "string",
            "metadata": {}
        }
        
    Returns:
        JSON: {success: bool, data: {...}}
    """
    try:
        user_id = request.user_id
        data = request.get_json()
        
        if not data:
            return jsonify({
                'success': False,
                'error': 'Request body required'
            }), 400
        
        print(f"🔧 Updating [module name] for user {user_id}")
        
        # Extract fields
        status = data.get('status')
        metadata = data.get('metadata', {})
        
        # Update database
        conn = get_database_connection('ai_infrastructure')
        cursor = conn.cursor()
        
        cursor.execute("""
            UPDATE ai_infrastructure.[module_name]
            SET 
                status = COALESCE(%s, status),
                metadata = COALESCE(%s::jsonb, metadata),
                updated_at = NOW()
            WHERE user_id = %s
            RETURNING id, status, metadata, updated_at
        """, (status, metadata if metadata else None, user_id))
        
        row = cursor.fetchone()
        conn.commit()
        conn.close()
        
        if row:
            return jsonify({
                'success': True,
                'data': {
                    'id': row[0],
                    'status': row[1],
                    'metadata': row[2],
                    'updated_at': row[3].isoformat() if row[3] else None
                }
            }), 200
        else:
            return jsonify({
                'success': False,
                'error': 'Record not found'
            }), 404
            
    except Exception as e:
        print(f"❌ Error in update_record: {e}")
        traceback.print_exc()
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@[module_name]_bp.route('/api/[module-name]/analytics', methods=['GET'])
@auth_manager.require_auth
def get_analytics():
    """
    Get aggregate analytics for [module name] (admin only)
    
    Returns:
        JSON: {success: bool, data: {...}}
    """
    try:
        user_id = request.user_id
        
        # Check if user is admin
        conn = get_database_connection('ai_infrastructure')
        cursor = conn.cursor()
        
        cursor.execute("SELECT role FROM ai_infrastructure.users WHERE id = %s", (user_id,))
        row = cursor.fetchone()
        
        if not row or row[0] != 'admin':
            return jsonify({
                'success': False,
                'error': 'Admin access required'
            }), 403
        
        print(f"🔧 Fetching [module name] analytics")
        
        # Get aggregate statistics
        cursor.execute("""
            SELECT 
                COUNT(*) as total_users,
                COUNT(CASE WHEN is_active = TRUE THEN 1 END) as active_users,
                COUNT(CASE WHEN status = 'completed' THEN 1 END) as completed_users,
                AVG(progress_percentage) as avg_progress
            FROM ai_infrastructure.[module_name]
        """)
        
        row = cursor.fetchone()
        conn.close()
        
        if row:
            return jsonify({
                'success': True,
                'data': {
                    'total_users': row[0],
                    'active_users': row[1],
                    'completed_users': row[2],
                    'avg_progress': float(row[3]) if row[3] else 0.0
                }
            }), 200
        else:
            return jsonify({
                'success': False,
                'error': 'No data available'
            }), 404
            
    except Exception as e:
        print(f"❌ Error in get_analytics: {e}")
        traceback.print_exc()
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


# =====================================================
# BLUEPRINT REGISTRATION
# =====================================================

def register_routes(app):
    """
    Register [module name] routes with Flask app
    
    Args:
        app: Flask application instance
    """
    app.register_blueprint([module_name]_bp)
    print(f"✅ [Module Name] routes registered")
```

### Step 2: Authentication Pattern

**All endpoints MUST use `@auth_manager.require_auth`:**

```python
from AI_infrastructure.auth.user_auth import UserAuthManager

auth_manager = UserAuthManager()

@[module_name]_bp.route('/api/[module-name]/endpoint', methods=['POST'])
@auth_manager.require_auth  # ← REQUIRED!
def endpoint_handler():
    user_id = request.user_id  # ← Automatically available after @require_auth
    # ... implementation
```

### Step 3: Response Format Standard

**Success Response:**
```python
return jsonify({
    'success': True,
    'data': {
        # ... response data
    }
}), 200
```

**Error Response:**
```python
return jsonify({
    'success': False,
    'error': 'Descriptive error message'
}), 400  # or 500, 404, 403, etc.
```

### Step 4: Register Routes in flask_app.py

**File:** `AI_infrastructure/flask_app.py`

Find the route registration section (typically around lines 50-100) and add:

```python
# Import your routes
from routes.[module_name]_routes import register_routes as register_[module_name]_routes

# ... existing imports ...

# Register routes (in route registration section)
register_[module_name]_routes(app)
```

---

## JavaScript Module Pattern

### Step 1: API Wrapper Class

**File:** `UI/modules/[module-name]/[module-name]-api.js`

```javascript
/**
 * FILE: UI/modules/[module-name]/[module-name]-api.js
 * PURPOSE: API wrapper for [Module Name] backend endpoints
 * 
 * FEATURES:
 * - Authenticated fetch requests with JWT
 * - Consistent error handling
 * - All [module name] API operations
 * 
 * DEPENDENCIES:
 * - sessionStorage/localStorage for JWT token
 * 
 * USAGE:
 * const api = new [ModuleName]API();
 * const status = await api.getStatus();
 * 
 * LAST MODIFIED: YYYY-MM-DD - Initial implementation
 */

class [ModuleName]API {
    constructor() {
        this.baseUrl = window.location.origin;
        this.apiPrefix = '/api/[module-name]';
    }

    /**
     * Get JWT authentication token from storage
     */
    getAuthToken() {
        // Try sessionStorage first, then localStorage
        return sessionStorage.getItem('authToken') || localStorage.getItem('authToken');
    }

    /**
     * Generic authenticated request wrapper
     */
    async request(endpoint, options = {}) {
        const token = this.getAuthToken();
        
        if (!token) {
            throw new Error('Authentication token not found');
        }

        const url = `${this.baseUrl}${this.apiPrefix}${endpoint}`;
        
        const headers = {
            'Content-Type': 'application/json',
            'Authorization': `Bearer ${token}`,
            ...options.headers
        };

        try {
            const response = await fetch(url, {
                ...options,
                headers
            });

            const data = await response.json();

            if (!response.ok) {
                throw new Error(data.error || `HTTP ${response.status}`);
            }

            return data;

        } catch (error) {
            console.error(`❌ API request failed: ${endpoint}`, error);
            throw error;
        }
    }

    /**
     * Get user's [module name] status
     */
    async getStatus() {
        return this.request('/status', {
            method: 'GET'
        });
    }

    /**
     * Update [module name] record
     */
    async updateRecord(data) {
        return this.request('/update', {
            method: 'POST',
            body: JSON.stringify(data)
        });
    }

    /**
     * Get analytics (admin only)
     */
    async getAnalytics() {
        return this.request('/analytics', {
            method: 'GET'
        });
    }

    // Add more methods as needed for your module
}

// Create global instance
window.[ModuleName]API = new [ModuleName]API();
```

### Step 2: Feature Module Class

**File:** `UI/modules/[module-name]/[module-name]-[feature].js`

```javascript
/**
 * FILE: UI/modules/[module-name]/[module-name]-[feature].js
 * PURPOSE: [Feature description]
 * 
 * FEATURES:
 * - [Feature 1]
 * - [Feature 2]
 * - Database persistence via API
 * 
 * DEPENDENCIES:
 * - window.[ModuleName]API ([module-name]-api.js)
 * - [module-name].css for styling
 * 
 * EVENTS LISTENED:
 * - [event:name]
 * 
 * EVENTS DISPATCHED:
 * - [module:event-name] (detail: {...})
 * 
 * USAGE:
 * const feature = new [FeatureName]();
 * await feature.init();
 * 
 * LAST MODIFIED: YYYY-MM-DD - Initial implementation
 */

class [FeatureName] {
    constructor() {
        // Configuration
        this.container = null;
        this.isInitialized = false;
        // ... other properties
    }

    /**
     * Initialize feature by fetching data from database
     */
    async init() {
        try {
            console.log('🔧 Initializing [feature name]...');
            
            // Fetch initial data from API
            const response = await window.[ModuleName]API.getStatus();
            
            if (!response || !response.success) {
                console.error('❌ Failed to fetch [module name] status');
                return;
            }

            const data = response.data;
            
            // Initialize state from database
            this.isInitialized = true;
            
            // Render UI
            this.render();
            
            // Attach event listeners
            this.attachEventListeners();
            
            console.log('✅ [Feature name] initialized');

        } catch (error) {
            console.error('❌ Error initializing [feature name]:', error);
        }
    }

    /**
     * Render the UI
     */
    render() {
        // Check if already rendered
        if (this.container) {
            console.log('⚠️ Already rendered');
            return;
        }

        // Create container
        this.container = document.createElement('div');
        this.container.className = '[module-name]-container';
        
        // Build HTML
        this.container.innerHTML = `
            <div class="[module-name]-header">
                <h2>[Feature Title]</h2>
            </div>
            <div class="[module-name]-body">
                <!-- Feature content -->
            </div>
        `;

        // Append to DOM
        document.body.appendChild(this.container);
        
        // Animate in
        setTimeout(() => {
            this.container.classList.add('[module-name]-visible');
        }, 100);
    }

    /**
     * Attach event listeners
     */
    attachEventListeners() {
        // Listen for custom events
        window.addEventListener('[event:name]', (e) => {
            this.handleEvent(e.detail);
        });
        
        // UI event listeners
        if (this.container) {
            // Example: button click
            const button = this.container.querySelector('.action-button');
            if (button) {
                button.addEventListener('click', () => {
                    this.performAction();
                });
            }
        }
    }

    /**
     * Perform action and update database
     */
    async performAction() {
        try {
            console.log('🔧 Performing action...');
            
            // Call API
            const result = await window.[ModuleName]API.updateRecord({
                status: 'active',
                metadata: { action: 'performed' }
            });
            
            if (result && result.success) {
                // Update UI
                this.updateUI(result.data);
                
                // Dispatch event
                window.dispatchEvent(new CustomEvent('[module:action-completed]', {
                    detail: result.data
                }));
                
                console.log('✅ Action completed');
            }
            
        } catch (error) {
            console.error('❌ Error performing action:', error);
        }
    }

    /**
     * Update UI after state change
     */
    updateUI(data) {
        if (!this.container) return;
        
        // Update DOM elements
        // Example: update status text
        const statusEl = this.container.querySelector('.status');
        if (statusEl) {
            statusEl.textContent = data.status;
        }
    }

    /**
     * Show the feature
     */
    show() {
        if (!this.container) {
            this.render();
        } else {
            this.container.classList.add('[module-name]-visible');
        }
    }

    /**
     * Hide the feature
     */
    hide() {
        if (this.container) {
            this.container.classList.remove('[module-name]-visible');
        }
    }

    /**
     * Clean up (remove from DOM)
     */
    destroy() {
        if (this.container) {
            this.container.remove();
            this.container = null;
        }
    }
}

// Create global instance
window.[FeatureName] = new [FeatureName]();

// Auto-initialize when DOM is ready
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', () => {
        window.[FeatureName].init();
    });
} else {
    window.[FeatureName].init();
}
```

### Step 3: Event Dispatching Pattern

**Dispatching Events:**
```javascript
// Dispatch custom event with data
window.dispatchEvent(new CustomEvent('[module:event-name]', {
    detail: {
        key: 'value',
        timestamp: Date.now()
    }
}));
```

**Listening to Events:**
```javascript
// Listen for custom events
window.addEventListener('[module:event-name]', (event) => {
    const data = event.detail;
    console.log('Event received:', data);
    // Handle event
});
```

---

## CSS Styling Guidelines

### Step 1: Create Stylesheet

**File:** `UI/styles/[module-name].css`

```css
/**
 * FILE: UI/styles/[module-name].css
 * PURPOSE: Styling for [Module Name] components
 * 
 * COMPONENTS:
 * - [component-1] - [description]
 * - [component-2] - [description]
 * 
 * THEME:
 * - Primary Color: #667eea (purple-blue gradient)
 * - Success: #10b981 (green)
 * - Error: #ef4444 (red)
 * - Warning: #f59e0b (orange)
 * 
 * RESPONSIVE:
 * - Mobile: base styles
 * - Tablet: 768px+
 * - Desktop: 1024px+
 * 
 * LAST MODIFIED: YYYY-MM-DD - Initial implementation
 */

/* =====================================================
   CSS VARIABLES
   ===================================================== */

:root {
    /* Colors */
    --[module-name]-primary: #667eea;
    --[module-name]-secondary: #764ba2;
    --[module-name]-gradient: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    
    --[module-name]-success: #10b981;
    --[module-name]-error: #ef4444;
    --[module-name]-warning: #f59e0b;
    --[module-name]-info: #3b82f6;
    
    --[module-name]-text: #1f2937;
    --[module-name]-text-light: #6b7280;
    --[module-name]-bg: #ffffff;
    --[module-name]-bg-secondary: #f9fafb;
    
    /* Spacing */
    --[module-name]-spacing-xs: 4px;
    --[module-name]-spacing-sm: 8px;
    --[module-name]-spacing-md: 16px;
    --[module-name]-spacing-lg: 24px;
    --[module-name]-spacing-xl: 32px;
    
    /* Typography */
    --[module-name]-font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'Roboto', sans-serif;
    --[module-name]-font-size-sm: 0.875rem;
    --[module-name]-font-size-base: 1rem;
    --[module-name]-font-size-lg: 1.125rem;
    --[module-name]-font-size-xl: 1.5rem;
    
    /* Z-index */
    --[module-name]-z-base: 1000;
    --[module-name]-z-modal: 2000;
    --[module-name]-z-overlay: 1999;
}

/* =====================================================
   ANIMATIONS
   ===================================================== */

@keyframes [module-name]-fadeIn {
    from {
        opacity: 0;
        transform: translateY(10px);
    }
    to {
        opacity: 1;
        transform: translateY(0);
    }
}

@keyframes [module-name]-slideInRight {
    from {
        opacity: 0;
        transform: translateX(20px);
    }
    to {
        opacity: 1;
        transform: translateX(0);
    }
}

@keyframes [module-name]-pulse {
    0%, 100% {
        transform: scale(1);
    }
    50% {
        transform: scale(1.05);
    }
}

/* =====================================================
   BASE CONTAINER
   ===================================================== */

.[module-name]-container {
    font-family: var(--[module-name]-font-family);
    font-size: var(--[module-name]-font-size-base);
    color: var(--[module-name]-text);
    
    /* Positioning */
    position: fixed;
    bottom: var(--[module-name]-spacing-lg);
    right: var(--[module-name]-spacing-lg);
    z-index: var(--[module-name]-z-base);
    
    /* Sizing */
    width: 360px;
    max-width: calc(100vw - 48px);
    max-height: 600px;
    
    /* Visual */
    background: var(--[module-name]-bg);
    border-radius: 12px;
    box-shadow: 0 10px 30px rgba(0, 0, 0, 0.15);
    
    /* Animation */
    opacity: 0;
    transform: translateY(20px);
    transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
}

.[module-name]-container.[module-name]-visible {
    opacity: 1;
    transform: translateY(0);
}

/* =====================================================
   HEADER
   ===================================================== */

.[module-name]-header {
    padding: var(--[module-name]-spacing-md);
    background: var(--[module-name]-gradient);
    color: white;
    border-radius: 12px 12px 0 0;
    
    display: flex;
    justify-content: space-between;
    align-items: center;
}

.[module-name]-header h2 {
    margin: 0;
    font-size: var(--[module-name]-font-size-lg);
    font-weight: 600;
}

/* =====================================================
   BODY
   ===================================================== */

.[module-name]-body {
    padding: var(--[module-name]-spacing-md);
    max-height: 500px;
    overflow-y: auto;
}

/* Custom scrollbar */
.[module-name]-body::-webkit-scrollbar {
    width: 6px;
}

.[module-name]-body::-webkit-scrollbar-track {
    background: var(--[module-name]-bg-secondary);
}

.[module-name]-body::-webkit-scrollbar-thumb {
    background: var(--[module-name]-text-light);
    border-radius: 3px;
}

/* =====================================================
   BUTTONS
   ===================================================== */

.[module-name]-button {
    padding: var(--[module-name]-spacing-sm) var(--[module-name]-spacing-md);
    background: var(--[module-name]-primary);
    color: white;
    border: none;
    border-radius: 6px;
    font-size: var(--[module-name]-font-size-base);
    font-weight: 500;
    cursor: pointer;
    transition: all 0.2s;
}

.[module-name]-button:hover {
    background: var(--[module-name]-secondary);
    transform: translateY(-1px);
    box-shadow: 0 4px 12px rgba(102, 126, 234, 0.4);
}

.[module-name]-button:active {
    transform: translateY(0);
}

/* =====================================================
   TOAST NOTIFICATIONS
   ===================================================== */

.[module-name]-toast {
    position: fixed;
    top: var(--[module-name]-spacing-lg);
    right: var(--[module-name]-spacing-lg);
    z-index: var(--[module-name]-z-modal);
    
    display: flex;
    align-items: center;
    gap: var(--[module-name]-spacing-sm);
    
    padding: var(--[module-name]-spacing-md);
    background: white;
    border-radius: 8px;
    box-shadow: 0 6px 20px rgba(0, 0, 0, 0.15);
    
    opacity: 0;
    transform: translateX(100px);
    transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
}

.[module-name]-toast.[module-name]-toast-visible {
    opacity: 1;
    transform: translateX(0);
}

.[module-name]-toast.toast-success {
    border-left: 4px solid var(--[module-name]-success);
}

.[module-name]-toast.toast-error {
    border-left: 4px solid var(--[module-name]-error);
}

/* =====================================================
   RESPONSIVE DESIGN
   ===================================================== */

/* Tablet (768px+) */
@media (min-width: 768px) {
    .[module-name]-container {
        width: 400px;
    }
}

/* Desktop (1024px+) */
@media (min-width: 1024px) {
    .[module-name]-container {
        width: 450px;
    }
}

/* Mobile (<768px) */
@media (max-width: 767px) {
    .[module-name]-container {
        width: calc(100vw - 32px);
        bottom: var(--[module-name]-spacing-md);
        right: var(--[module-name]-spacing-md);
    }
}

/* =====================================================
   ACCESSIBILITY
   ===================================================== */

/* Focus states */
.[module-name]-button:focus,
.[module-name]-input:focus {
    outline: 2px solid var(--[module-name]-primary);
    outline-offset: 2px;
}

/* Reduced motion */
@media (prefers-reduced-motion: reduce) {
    .[module-name]-container,
    .[module-name]-toast,
    .[module-name]-button {
        animation: none;
        transition: none;
    }
}

/* High contrast mode */
@media (prefers-contrast: high) {
    .[module-name]-container {
        border: 2px solid currentColor;
    }
}

/* Print styles */
@media print {
    .[module-name]-container,
    .[module-name]-toast {
        display: none;
    }
}
```

### Step 2: CSS Naming Conventions

**Use BEM-like naming:**
- Block: `.[module-name]-container`
- Element: `.[module-name]-header`, `.[module-name]-body`
- Modifier: `.[module-name]-visible`, `.[module-name]-collapsed`

**State classes:**
- `.is-active`, `.is-disabled`, `.is-loading`
- Use `[data-state="value"]` for complex states

---

## Integration Steps

### Step 1: Add HTML to Main Application

**File:** `UI/business-ai-platform-v2.html`

Find the closing `</body>` tag and add before it:

```html
<!-- [Module Name] Module -->
<!-- CSS -->
<link rel="stylesheet" href="UI/styles/[module-name].css">

<!-- JavaScript Modules -->
<script src="UI/modules/[module-name]/[module-name]-api.js"></script>
<script src="UI/modules/[module-name]/[module-name]-[feature].js"></script>
<!-- Add more module scripts as needed -->

<!-- [Module Name] HTML -->
<div id="[module-name]-mount-point">
    <!-- JavaScript will render here -->
</div>
```

### Step 2: Register Flask Routes

**File:** `AI_infrastructure/flask_app.py`

```python
# Import routes
from routes.[module_name]_routes import register_routes as register_[module_name]_routes

# In route registration section (find similar lines)
register_[module_name]_routes(app)
```

### Step 3: Execute Database Migration

```powershell
# From project root
cd c:\Users\gpoli\GIT\AI_agents

# Execute migration
psql $env:SUPABASE_DB_URL -f data/migrations/YYYYMMDD_add_[module_name]_table.sql

# Verify table created
psql $env:SUPABASE_DB_URL -c "SELECT * FROM ai_infrastructure.[module_name] LIMIT 1;"
```

### Step 4: Restart Flask Server

```powershell
# Stop Flask
Stop-Process -Name "python" -Force -ErrorAction SilentlyContinue

# Start Flask
cd c:\Users\gpoli\GIT\AI_agents
BISTART
```

### Step 5: Add Event Dispatchers

Find existing code that triggers your module's events and add dispatchers:

**Example: Thread creation**
```javascript
// In ThreadManager.createThread()
async createThread(title, agentId) {
    // ... existing code ...
    
    // Dispatch event for onboarding checklist
    window.dispatchEvent(new CustomEvent('thread:created', {
        detail: {
            threadId: newThread.id,
            title: title,
            agent: agentId
        }
    }));
    
    return newThread;
}
```

---

## Testing Checklist

### Database Layer Testing

```powershell
# Connect to database
psql $env:SUPABASE_DB_URL

# Check table exists
\dt ai_infrastructure.[module_name]

# Check indexes
\di ai_infrastructure.idx_[module_name]*

# Query sample data
SELECT * FROM ai_infrastructure.[module_name] LIMIT 5;

# Test JSONB operations
UPDATE ai_infrastructure.[module_name] 
SET metadata = jsonb_set(metadata, '{test}', '"value"'::jsonb) 
WHERE user_id = 1;
```

### Backend API Testing

```powershell
# Get JWT token (from browser localStorage)
$token = "eyJ0eXAiOiJKV1QiLCJhbGc..."

# Test GET endpoint
curl http://localhost:5001/api/[module-name]/status `
  -H "Authorization: Bearer $token"

# Test POST endpoint
curl http://localhost:5001/api/[module-name]/update `
  -X POST `
  -H "Authorization: Bearer $token" `
  -H "Content-Type: application/json" `
  -d '{"status":"active","metadata":{"test":true}}'

# Test analytics (admin)
curl http://localhost:5001/api/[module-name]/analytics `
  -H "Authorization: Bearer $token"
```

### Frontend Testing

**In Browser Console:**

```javascript
// Check global instance exists
console.log(window.[ModuleName]API);
console.log(window.[FeatureName]);

// Test API call
const status = await window.[ModuleName]API.getStatus();
console.log('Status:', status);

// Test feature initialization
await window.[FeatureName].init();

// Test event dispatching
window.dispatchEvent(new CustomEvent('[module:test]', {
    detail: { test: true }
}));

// Check DOM elements
document.querySelectorAll('.[module-name]-container').length;
```

### Integration Testing

**Full User Flow:**
1. Open application in browser
2. Log in with test user credentials
3. Navigate to module section
4. Perform module actions (create, update, etc.)
5. Verify database updates (query PostgreSQL)
6. Check UI updates in real-time
7. Verify events dispatch correctly
8. Test error handling (network errors, invalid data)
9. Test mobile responsiveness (DevTools mobile view)
10. Test accessibility (keyboard navigation, screen reader)

---

## Complete Code Examples

### Example 1: Simple Counter Module

**Use Case:** Track how many times user clicks a button, persist to database

**Database Migration:**
```sql
CREATE TABLE ai_infrastructure.user_clicks (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES ai_infrastructure.users(id) ON DELETE CASCADE,
    click_count INTEGER DEFAULT 0,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_user_clicks_user_id ON ai_infrastructure.user_clicks(user_id);
```

**Flask Route:**
```python
@clicks_bp.route('/api/clicks/increment', methods=['POST'])
@auth_manager.require_auth
def increment_clicks():
    user_id = request.user_id
    
    conn = get_database_connection('ai_infrastructure')
    cursor = conn.cursor()
    
    cursor.execute("""
        UPDATE ai_infrastructure.user_clicks
        SET click_count = click_count + 1, updated_at = NOW()
        WHERE user_id = %s
        RETURNING click_count
    """, (user_id,))
    
    row = cursor.fetchone()
    conn.commit()
    conn.close()
    
    return jsonify({
        'success': True,
        'data': {'click_count': row[0]}
    }), 200
```

**JavaScript:**
```javascript
class ClickCounter {
    constructor() {
        this.count = 0;
    }

    async init() {
        const response = await window.ClicksAPI.getStatus();
        this.count = response.data.click_count;
        this.render();
    }

    render() {
        const button = document.createElement('button');
        button.textContent = `Clicks: ${this.count}`;
        button.onclick = () => this.handleClick();
        document.body.appendChild(button);
    }

    async handleClick() {
        const result = await window.ClicksAPI.increment();
        this.count = result.data.click_count;
        document.querySelector('button').textContent = `Clicks: ${this.count}`;
    }
}

window.ClickCounter = new ClickCounter();
window.ClickCounter.init();
```

### Example 2: Progress Tracker Module

**Use Case:** Track user progress through a multi-step wizard

**Database Migration:**
```sql
CREATE TABLE ai_infrastructure.wizard_progress (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES ai_infrastructure.users(id) ON DELETE CASCADE,
    current_step INTEGER DEFAULT 1,
    completed_steps JSONB DEFAULT '[]'::jsonb,
    total_steps INTEGER DEFAULT 5,
    is_completed BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);
```

**Flask Route:**
```python
@wizard_bp.route('/api/wizard/complete-step', methods=['POST'])
@auth_manager.require_auth
def complete_step():
    user_id = request.user_id
    data = request.get_json()
    step_number = data.get('step')
    
    conn = get_database_connection('ai_infrastructure')
    cursor = conn.cursor()
    
    cursor.execute("""
        UPDATE ai_infrastructure.wizard_progress
        SET 
            completed_steps = completed_steps || %s::jsonb,
            current_step = %s + 1,
            updated_at = NOW()
        WHERE user_id = %s
        RETURNING current_step, total_steps, 
                  jsonb_array_length(completed_steps) as completed_count
    """, (f'[{step_number}]', step_number, user_id))
    
    row = cursor.fetchone()
    conn.commit()
    conn.close()
    
    return jsonify({
        'success': True,
        'data': {
            'current_step': row[0],
            'total_steps': row[1],
            'completed_count': row[2]
        }
    }), 200
```

**JavaScript:**
```javascript
class WizardProgress {
    constructor() {
        this.currentStep = 1;
        this.totalSteps = 5;
    }

    async init() {
        const response = await window.WizardAPI.getStatus();
        this.currentStep = response.data.current_step;
        this.totalSteps = response.data.total_steps;
        this.render();
    }

    render() {
        const progress = document.createElement('div');
        progress.className = 'wizard-progress';
        progress.innerHTML = `
            <div class="progress-bar">
                <div class="progress-fill" style="width: ${(this.currentStep / this.totalSteps) * 100}%"></div>
            </div>
            <span>Step ${this.currentStep} of ${this.totalSteps}</span>
        `;
        document.body.appendChild(progress);
    }

    async completeStep(stepNumber) {
        const result = await window.WizardAPI.completeStep(stepNumber);
        this.currentStep = result.data.current_step;
        
        // Update UI
        const fill = document.querySelector('.progress-fill');
        fill.style.width = `${(this.currentStep / this.totalSteps) * 100}%`;
        
        // Dispatch event
        window.dispatchEvent(new CustomEvent('wizard:step-completed', {
            detail: { step: stepNumber }
        }));
    }
}

window.WizardProgress = new WizardProgress();
```

---

## Final Checklist for AI Agents

When creating a new module, ensure you complete ALL of these steps:

### Database Layer
- [ ] Design table schema with proper columns
- [ ] Add foreign key to `ai_infrastructure.users(id)`
- [ ] Include `created_at`, `updated_at` timestamps
- [ ] Add indexes on frequently queried columns
- [ ] Use JSONB for arrays/objects
- [ ] Create migration file with rollback script
- [ ] Test migration execution

### Backend API Layer
- [ ] Create `[module_name]_routes.py` in `AI_infrastructure/routes/`
- [ ] Import `UserAuthManager` for authentication
- [ ] Create Blueprint: `[module_name]_bp = Blueprint('[module_name]', __name__)`
- [ ] Add `@auth_manager.require_auth` to all endpoints
- [ ] Implement helper functions (`get_record`, `create_record`)
- [ ] Use consistent response format: `{success: bool, data/error: object}`
- [ ] Add comprehensive error handling and logging
- [ ] Create `register_routes(app)` function
- [ ] Register blueprint in `flask_app.py`

### Frontend Layer
- [ ] Create `UI/modules/[module-name]/` directory
- [ ] Create API wrapper class (`[module-name]-api.js`)
- [ ] Implement `getAuthToken()` method
- [ ] Implement `request()` wrapper with authentication
- [ ] Create feature modules (`[module-name]-[feature].js`)
- [ ] Use ES6 classes with global window.* instances
- [ ] Implement `init()`, `render()`, `show()`, `hide()` methods
- [ ] Dispatch CustomEvents for cross-component communication
- [ ] Add event listeners for relevant triggers

### CSS Styling
- [ ] Create `UI/styles/[module-name].css`
- [ ] Define CSS variables for colors, spacing, typography
- [ ] Create animations (@keyframes)
- [ ] Style base container with positioning
- [ ] Add responsive breakpoints (768px, 1024px)
- [ ] Include accessibility features (focus states, reduced motion)
- [ ] Use consistent naming convention (BEM-like)

### Integration
- [ ] Add CSS link to `business-ai-platform-v2.html`
- [ ] Add script tags for all JavaScript modules
- [ ] Execute database migration
- [ ] Restart Flask server
- [ ] Add event dispatchers to existing code
- [ ] Test end-to-end user flow

### Testing
- [ ] Query database to verify table creation
- [ ] Test API endpoints with curl
- [ ] Test JavaScript initialization in browser console
- [ ] Verify UI renders correctly
- [ ] Test database updates on user actions
- [ ] Test event dispatching
- [ ] Test error handling
- [ ] Test mobile responsiveness
- [ ] Test accessibility (keyboard navigation)

### Documentation
- [ ] Create `[MODULE_NAME]_IMPLEMENTATION_COMPLETE.md`
- [ ] Document all database columns
- [ ] Document all API endpoints with examples
- [ ] Document all JavaScript classes and methods
- [ ] Include integration steps
- [ ] Include testing checklist
- [ ] Add code examples

---

## Common Pitfalls to Avoid

❌ **DON'T use localStorage for persistence** - Always use database  
❌ **DON'T skip authentication** - All endpoints need `@require_auth`  
❌ **DON'T forget to register routes** - Must call `register_routes(app)` in `flask_app.py`  
❌ **DON'T hardcode user IDs** - Always extract from `request.user_id`  
❌ **DON'T ignore error handling** - Wrap everything in try-catch  
❌ **DON'T forget JSONB casting** - Use `::jsonb` when inserting/updating  
❌ **DON'T skip event dispatching** - Other modules may depend on your events  
❌ **DON'T create duplicate code** - Follow established patterns  
❌ **DON'T forget responsive design** - Test on mobile breakpoints  
❌ **DON'T skip documentation** - Future you will thank present you

---

## Quick Command Reference

### Database Commands
```powershell
# Execute migration
psql $env:SUPABASE_DB_URL -f data/migrations/YYYYMMDD_add_[module]_table.sql

# Query table
psql $env:SUPABASE_DB_URL -c "SELECT * FROM ai_infrastructure.[module] LIMIT 5;"

# Drop table (careful!)
psql $env:SUPABASE_DB_URL -c "DROP TABLE ai_infrastructure.[module] CASCADE;"
```

### Flask Server Commands
```powershell
# Stop Flask
Stop-Process -Name "python" -Force -ErrorAction SilentlyContinue

# Start Flask
cd c:\Users\gpoli\GIT\AI_agents
BISTART

# Check Flask logs
cd c:\Users\gpoli\GIT\AI_agents\AI_infrastructure
python flask_app.py
```

### API Testing Commands
```powershell
# Test GET endpoint
curl http://localhost:5001/api/[module]/status -H "Authorization: Bearer $token"

# Test POST endpoint
curl http://localhost:5001/api/[module]/update -X POST -H "Authorization: Bearer $token" -H "Content-Type: application/json" -d '{"key":"value"}'
```

---

## Summary

This guide provides **everything** needed to create production-ready, database-backed modules for the AI Agents Platform. Follow these patterns precisely, and your modules will integrate seamlessly with the existing system.

**Key Takeaways:**
1. **Always use database** for persistence (never localStorage)
2. **Always authenticate** API endpoints with `@require_auth`
3. **Always follow patterns** from onboarding system reference
4. **Always test thoroughly** at database, API, and frontend layers
5. **Always document** with comprehensive implementation guides

**Reference Implementation:** `UI/modules/onboarding/` + `AI_infrastructure/routes/onboarding_routes.py`

---

**Last Updated:** November 30, 2025  
**Version:** 1.0.0  
**Status:** ✅ Production Ready

**Questions?** Review the onboarding system implementation as the gold standard for all future modules.

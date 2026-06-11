# Database Storage for Thread Assignments - Complete Implementation

**Date:** November 5, 2025  
**Databases:** `sessions.db` (existing) + new table  
**Status:** 📝 Implementation Plan

## Overview

Currently thread assignments are stored in `localStorage`. This implementation will:
1. Create `thread_assignments` table in `sessions.db`
2. Create Flask API endpoints for save/load
3. Update JavaScript to use API instead of localStorage
4. Keep localStorage as fallback for offline/cached data

---

## Step 1: Database Migration

### Create New Table in sessions.db

**File:** `AI_infrastructure/migrations/add_thread_assignments.sql`

```sql
-- Migration: Add thread_assignments table
-- Database: sessions.db
-- Date: 2025-11-05

CREATE TABLE IF NOT EXISTS thread_assignments (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    thread_slug TEXT NOT NULL,                 -- From threads.thread_slug
    location TEXT NOT NULL,                     -- 'prime', 'agent-1', 'agent-2', etc.
    workspace_id INTEGER,                       -- Optional workspace context
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    metadata TEXT,                              -- JSON for future extensibility
    
    -- Constraints
    UNIQUE(user_id, location),                  -- One thread per location per user
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY (thread_slug) REFERENCES threads(thread_slug) ON DELETE CASCADE,
    FOREIGN KEY (workspace_id) REFERENCES workspaces(id) ON DELETE SET NULL
);

-- Indexes for performance
CREATE INDEX IF NOT EXISTS idx_thread_assignments_user 
    ON thread_assignments(user_id);

CREATE INDEX IF NOT EXISTS idx_thread_assignments_thread 
    ON thread_assignments(thread_slug);

CREATE INDEX IF NOT EXISTS idx_thread_assignments_location 
    ON thread_assignments(user_id, location);

-- Trigger to update updated_at on changes
CREATE TRIGGER IF NOT EXISTS update_thread_assignment_timestamp 
    AFTER UPDATE ON thread_assignments
    FOR EACH ROW
BEGIN
    UPDATE thread_assignments 
    SET updated_at = CURRENT_TIMESTAMP 
    WHERE id = NEW.id;
END;
```

### Run Migration Script

**File:** `AI_infrastructure/migrations/run_migration.py`

```python
"""
Run database migration to add thread_assignments table
Usage: python run_migration.py
"""

import sqlite3
import os
from pathlib import Path

# Get database path
root_dir = Path(__file__).parent.parent.parent
db_path = root_dir / 'data' / 'sessions.db'

print(f"🔷 Migrating database: {db_path}")

# Read SQL migration
migration_file = Path(__file__).parent / 'add_thread_assignments.sql'
with open(migration_file, 'r') as f:
    migration_sql = f.read()

# Execute migration
conn = sqlite3.connect(str(db_path))
cursor = conn.cursor()

try:
    # Execute all statements
    cursor.executescript(migration_sql)
    conn.commit()
    print("✅ Migration completed successfully!")
    
    # Verify table was created
    cursor.execute("""
        SELECT name FROM sqlite_master 
        WHERE type='table' AND name='thread_assignments'
    """)
    
    if cursor.fetchone():
        print("✅ Table 'thread_assignments' verified")
        
        # Show table schema
        cursor.execute("PRAGMA table_info(thread_assignments)")
        columns = cursor.fetchall()
        print("\n📋 Table structure:")
        for col in columns:
            print(f"  - {col[1]} ({col[2]})")
    else:
        print("❌ Table creation failed")
        
except Exception as e:
    print(f"❌ Migration failed: {e}")
    conn.rollback()
finally:
    conn.close()
```

**Run it:**
```powershell
cd C:\Users\gpoli\GIT\AI_agents\AI_infrastructure\migrations
python run_migration.py
```

---

## Step 2: Flask API Endpoints

### Create Thread Assignments Routes

**File:** `AI_infrastructure/routes/thread_assignment_routes.py`

```python
"""
Thread Assignment Routes - Database storage for thread locations
Stores which thread is loaded in which location (Prime, Agent-1, etc.)
"""

from flask import Blueprint, request, jsonify
from pathlib import Path
import sqlite3
import json
from datetime import datetime

thread_assignment_bp = Blueprint('thread_assignments', __name__)

def get_db_connection():
    """Get connection to sessions.db"""
    root_dir = Path(__file__).parent.parent.parent
    db_path = root_dir / 'data' / 'sessions.db'
    
    conn = sqlite3.connect(str(db_path))
    conn.row_factory = sqlite3.Row
    return conn


@thread_assignment_bp.route('/api/thread-assignments', methods=['GET'])
def get_thread_assignments():
    """
    Get all thread assignments for the current user
    
    Returns:
        {
            "prime": "thread-slug-123",
            "agent-1": "thread-slug-456",
            "agent-2": null
        }
    """
    try:
        # Get user_id from session or request
        user_id = request.args.get('user_id', 1)  # Default to user 1 for now
        workspace_id = request.args.get('workspace_id')
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Query assignments
        query = """
            SELECT location, thread_slug, updated_at, metadata
            FROM thread_assignments
            WHERE user_id = ?
        """
        params = [user_id]
        
        if workspace_id:
            query += " AND workspace_id = ?"
            params.append(workspace_id)
        
        cursor.execute(query, params)
        rows = cursor.fetchall()
        conn.close()
        
        # Build response object
        assignments = {}
        for row in rows:
            assignments[row['location']] = row['thread_slug']
        
        return jsonify({
            'success': True,
            'assignments': assignments,
            'count': len(assignments)
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@thread_assignment_bp.route('/api/thread-assignments', methods=['POST'])
def save_thread_assignments():
    """
    Save thread assignments (batch update)
    
    Request body:
        {
            "user_id": 1,
            "assignments": {
                "prime": "thread-slug-123",
                "agent-1": "thread-slug-456",
                "agent-2": null
            }
        }
    """
    try:
        data = request.get_json()
        user_id = data.get('user_id', 1)
        assignments = data.get('assignments', {})
        workspace_id = data.get('workspace_id')
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Clear existing assignments for this user
        cursor.execute("""
            DELETE FROM thread_assignments 
            WHERE user_id = ?
        """, [user_id])
        
        # Insert new assignments
        for location, thread_slug in assignments.items():
            if thread_slug:  # Skip null assignments
                cursor.execute("""
                    INSERT INTO thread_assignments 
                    (user_id, thread_slug, location, workspace_id)
                    VALUES (?, ?, ?, ?)
                """, [user_id, thread_slug, location, workspace_id])
        
        conn.commit()
        conn.close()
        
        return jsonify({
            'success': True,
            'saved_count': len([v for v in assignments.values() if v])
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@thread_assignment_bp.route('/api/thread-assignments/assign', methods=['POST'])
def assign_thread():
    """
    Assign a single thread to a location
    
    Request body:
        {
            "user_id": 1,
            "thread_slug": "thread-123",
            "location": "agent-1"
        }
    """
    try:
        data = request.get_json()
        user_id = data.get('user_id', 1)
        thread_slug = data.get('thread_slug')
        location = data.get('location')
        workspace_id = data.get('workspace_id')
        
        if not thread_slug or not location:
            return jsonify({
                'success': False,
                'error': 'thread_slug and location are required'
            }), 400
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Remove thread from any previous location
        cursor.execute("""
            DELETE FROM thread_assignments 
            WHERE user_id = ? AND thread_slug = ?
        """, [user_id, thread_slug])
        
        # Remove any thread at target location
        cursor.execute("""
            DELETE FROM thread_assignments 
            WHERE user_id = ? AND location = ?
        """, [user_id, location])
        
        # Insert new assignment
        cursor.execute("""
            INSERT INTO thread_assignments 
            (user_id, thread_slug, location, workspace_id)
            VALUES (?, ?, ?, ?)
        """, [user_id, thread_slug, location, workspace_id])
        
        conn.commit()
        conn.close()
        
        return jsonify({
            'success': True,
            'assignment': {
                'thread_slug': thread_slug,
                'location': location
            }
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@thread_assignment_bp.route('/api/thread-assignments/unassign', methods=['POST'])
def unassign_thread():
    """
    Remove thread assignment (clear from location)
    
    Request body:
        {
            "user_id": 1,
            "thread_slug": "thread-123"
        }
    """
    try:
        data = request.get_json()
        user_id = data.get('user_id', 1)
        thread_slug = data.get('thread_slug')
        
        if not thread_slug:
            return jsonify({
                'success': False,
                'error': 'thread_slug is required'
            }), 400
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            DELETE FROM thread_assignments 
            WHERE user_id = ? AND thread_slug = ?
        """, [user_id, thread_slug])
        
        conn.commit()
        conn.close()
        
        return jsonify({
            'success': True,
            'deleted': cursor.rowcount
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@thread_assignment_bp.route('/api/thread-assignments/location/<thread_slug>', methods=['GET'])
def get_thread_location(thread_slug):
    """Get location of a specific thread"""
    try:
        user_id = request.args.get('user_id', 1)
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT location, updated_at 
            FROM thread_assignments
            WHERE user_id = ? AND thread_slug = ?
        """, [user_id, thread_slug])
        
        row = cursor.fetchone()
        conn.close()
        
        if row:
            return jsonify({
                'success': True,
                'location': row['location'],
                'updated_at': row['updated_at']
            })
        else:
            return jsonify({
                'success': True,
                'location': None
            })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@thread_assignment_bp.route('/api/thread-assignments/validate', methods=['POST'])
def validate_assignments():
    """
    Validate and fix assignment inconsistencies
    Returns report of issues found/fixed
    """
    try:
        user_id = request.args.get('user_id', 1)
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
        errors = []
        fixed = 0
        
        # Check for duplicate thread assignments
        cursor.execute("""
            SELECT thread_slug, COUNT(*) as count, GROUP_CONCAT(location) as locations
            FROM thread_assignments
            WHERE user_id = ?
            GROUP BY thread_slug
            HAVING count > 1
        """, [user_id])
        
        duplicates = cursor.fetchall()
        
        for dup in duplicates:
            errors.append(f"Thread {dup['thread_slug']} in multiple locations: {dup['locations']}")
            
            # Fix: Keep only the most recent assignment
            cursor.execute("""
                DELETE FROM thread_assignments
                WHERE user_id = ? AND thread_slug = ?
                AND id NOT IN (
                    SELECT id FROM thread_assignments
                    WHERE user_id = ? AND thread_slug = ?
                    ORDER BY updated_at DESC
                    LIMIT 1
                )
            """, [user_id, dup['thread_slug'], user_id, dup['thread_slug']])
            
            fixed += cursor.rowcount
        
        conn.commit()
        conn.close()
        
        return jsonify({
            'success': True,
            'valid': len(errors) == 0,
            'errors': errors,
            'fixed_count': fixed
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500
```

### Register Routes in Flask App

**File:** `AI_infrastructure/flask_app.py` (add this)

```python
# Add to imports
from routes.thread_assignment_routes import thread_assignment_bp

# Add to route registration (around line 200)
app.register_blueprint(thread_assignment_bp)
print(f"✅ Registered thread_assignment routes")
```

---

## Step 3: Update JavaScript to Use API

### Update ThreadManager in business-ai-platform-v2.html

**Replace the localStorage methods with API calls:**

```javascript
// In ThreadManager object

// Replace getThreadAssignments()
async getThreadAssignments() {
    try {
        // Try API first
        const response = await fetch('/api/thread-assignments?user_id=1');
        const data = await response.json();
        
        if (data.success) {
            // Cache in localStorage as backup
            localStorage.setItem('thread_assignments', JSON.stringify(data.assignments));
            return data.assignments;
        }
    } catch (error) {
        console.warn('⚠️ API failed, using localStorage fallback:', error);
    }
    
    // Fallback to localStorage
    try {
        const assignments = localStorage.getItem('thread_assignments');
        return assignments ? JSON.parse(assignments) : {};
    } catch (error) {
        console.error('Error loading thread assignments:', error);
        return {};
    }
},

// Replace saveThreadAssignments()
async saveThreadAssignments(assignments) {
    try {
        // Save to API
        const response = await fetch('/api/thread-assignments', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                user_id: 1,
                assignments: assignments
            })
        });
        
        const data = await response.json();
        
        if (data.success) {
            console.log('💾 Thread assignments saved to database:', assignments);
            
            // Also save to localStorage as cache
            localStorage.setItem('thread_assignments', JSON.stringify(assignments));
        } else {
            throw new Error(data.error || 'Failed to save assignments');
        }
    } catch (error) {
        console.error('Error saving thread assignments to database:', error);
        
        // Fallback to localStorage only
        try {
            localStorage.setItem('thread_assignments', JSON.stringify(assignments));
            console.log('💾 Thread assignments saved to localStorage (fallback)');
        } catch (e) {
            console.error('Failed to save to localStorage:', e);
        }
    }
},

// Replace assignThread() - make it async
async assignThread(threadId, location) {
    const assignments = await this.getThreadAssignments();
    
    // Remove thread from any previous location
    Object.keys(assignments).forEach(loc => {
        if (assignments[loc] === threadId) {
            delete assignments[loc];
            console.log(`🔄 Unassigned thread ${threadId} from ${loc}`);
        }
    });
    
    // Assign to new location if not null
    if (location) {
        if (assignments[location]) {
            const previousThread = assignments[location];
            console.log(`⚠️ Location ${location} already has thread ${previousThread}, replacing...`);
        }
        
        assignments[location] = threadId;
        console.log(`✅ Assigned thread ${threadId} to ${location}`);
    }
    
    await this.saveThreadAssignments(assignments);
    return assignments;
},

// Update validateAssignments() - make it async
async validateAssignments() {
    console.log('🔍 [ThreadManager] Validating thread assignments...');
    
    try {
        // Use database validation endpoint
        const response = await fetch('/api/thread-assignments/validate?user_id=1', {
            method: 'POST'
        });
        
        const result = await response.json();
        
        if (result.success) {
            if (result.fixed_count > 0) {
                console.log(`✅ Fixed ${result.fixed_count} assignment inconsistencies`);
            } else {
                console.log('✅ All thread assignments valid');
            }
            
            return result;
        }
    } catch (error) {
        console.warn('⚠️ Database validation failed, using client-side validation');
    }
    
    // Fallback to client-side validation (existing code)
    const assignments = await this.getThreadAssignments();
    const seenThreads = new Set();
    const errors = [];
    let fixed = false;
    
    // ... rest of existing validation logic ...
    
    return {
        valid: errors.length === 0,
        errors: errors,
        fixed: fixed,
        assignments: assignments
    };
},
```

### Update All Calls to Be Async

**In sendToAgent(), moveToPrime(), switchThread(), etc., update to:**

```javascript
// Before:
this.assignThread(threadId, targetLocation);

// After (make parent function async):
await this.assignThread(threadId, targetLocation);
```

---

## Step 4: Testing

### Test Migration

```powershell
# 1. Run migration
cd C:\Users\gpoli\GIT\AI_agents\AI_infrastructure\migrations
python run_migration.py

# 2. Verify table exists
sqlite3 C:\Users\gpoli\GIT\AI_agents\data\sessions.db "SELECT * FROM thread_assignments;"
```

### Test API Endpoints

```powershell
# Start Flask server
BISTART

# Test GET assignments (empty at first)
curl http://localhost:5001/api/thread-assignments?user_id=1

# Test POST assignments
curl -X POST http://localhost:5001/api/thread-assignments `
  -H "Content-Type: application/json" `
  -d '{\"user_id\": 1, \"assignments\": {\"prime\": \"thread-123\", \"agent-1\": \"thread-456\"}}'

# Test single assignment
curl -X POST http://localhost:5001/api/thread-assignments/assign `
  -H "Content-Type: application/json" `
  -d '{\"user_id\": 1, \"thread_slug\": \"thread-789\", \"location\": \"agent-2\"}'

# Test validate
curl -X POST http://localhost:5001/api/thread-assignments/validate?user_id=1
```

### Test UI Integration

1. Open browser at `localhost:5001`
2. Open DevTools console
3. Drag thread to agent column
4. Check console for "💾 Thread assignments saved to database"
5. Refresh page
6. Verify threads restored to correct locations
7. Check database: `SELECT * FROM thread_assignments;`

---

## Step 5: Migration from localStorage

### Create One-Time Migration Script

**Add to ThreadManager.init():**

```javascript
async migrateFromLocalStorage() {
    console.log('🔄 Checking for localStorage migration...');
    
    try {
        // Check if already migrated
        const migrated = localStorage.getItem('assignments_migrated');
        if (migrated === 'true') {
            console.log('✅ Already migrated to database');
            return;
        }
        
        // Get old localStorage assignments
        const oldAssignments = localStorage.getItem('thread_assignments');
        if (!oldAssignments) {
            console.log('📭 No localStorage assignments to migrate');
            localStorage.setItem('assignments_migrated', 'true');
            return;
        }
        
        const assignments = JSON.parse(oldAssignments);
        
        // Save to database
        const response = await fetch('/api/thread-assignments', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({
                user_id: 1,
                assignments: assignments
            })
        });
        
        const data = await response.json();
        
        if (data.success) {
            console.log(`✅ Migrated ${data.saved_count} assignments to database`);
            localStorage.setItem('assignments_migrated', 'true');
        }
        
    } catch (error) {
        console.error('❌ Migration failed:', error);
    }
},

// Call in init()
async init() {
    this.loadThreads();
    
    // Migrate old data
    await this.migrateFromLocalStorage();
    
    // ... rest of init code ...
}
```

---

## Benefits of Database Storage

| Feature | localStorage (Old) | Database (New) |
|---------|-------------------|----------------|
| **Multi-device sync** | ❌ Per browser | ✅ Synced |
| **Backup** | ❌ None | ✅ Database backup |
| **History** | ❌ No history | ✅ Can add history |
| **Sharing** | ❌ Can't share | ✅ Can share workspaces |
| **Capacity** | ⚠️ 5-10MB | ✅ Unlimited |
| **Query** | ❌ Load all | ✅ SQL queries |
| **Offline** | ✅ Works | ⚠️ Needs API |
| **Speed (first load)** | ⚡ Instant | 🐌 Network call |
| **Speed (cached)** | ⚡ Instant | ⚡ Instant |

---

## Files to Create/Modify

### New Files:
1. `AI_infrastructure/migrations/add_thread_assignments.sql`
2. `AI_infrastructure/migrations/run_migration.py`
3. `AI_infrastructure/routes/thread_assignment_routes.py`

### Modified Files:
1. `AI_infrastructure/flask_app.py` - Register blueprint
2. `UI/business-ai-platform-v2.html` - Update ThreadManager methods to async

---

## Summary

This implementation provides:
- ✅ Database storage in `sessions.db`
- ✅ Flask API endpoints for CRUD operations
- ✅ localStorage as fallback/cache
- ✅ One-time migration from old system
- ✅ Validation endpoint
- ✅ Multi-device sync capability

**Next Steps:**
1. Run migration to create table
2. Create Flask routes file
3. Update JavaScript to use API
4. Test thoroughly
5. Deploy!

Would you like me to create these files for you?

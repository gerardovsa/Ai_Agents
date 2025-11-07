# 🗄️ Module Database Guide - When & How to Create Module .db Files

**Created:** October 30, 2025  
**Version:** 1.0.0  
**Status:** Complete Guide

---

## 🎯 When to Create a Module Database

###  CREATE a Module .db When:

**1. Complex Module-Specific Data**
- Module manages its own entities (products, projects, tickets, etc.)
- Data has complex relationships (foreign keys, joins)
- Module needs **10+ database tables**
- Data should be **isolated** from main system

**Example:** Project Management Module
- Projects, tasks, subtasks, comments, attachments
- Custom fields, workflows, automation rules
- Should be deletable without affecting main system

**2. Large Data Volumes**
- Module stores thousands/millions of records
- Heavy read/write operations
- Needs separate indexing strategy
- Performance isolation from main database

**Example:** Analytics Module
- Event tracking (millions of rows)
- Aggregated reports
- Historical data archives

**3. Module Portability/Export**
- Module should be exportable with ALL its data
- Data needs to move between environments
- Module has import/export features
- Backup/restore at module level

**Example:** CRM Module
- Complete customer database
- Sales pipeline data
- Communication history
- Should export as single file

**4. Data Lifecycle Management**
- Module data has different retention policies
- Data should be deleted when module is removed
- Module needs versioning/migrations
- Data owned by module, not platform

---

###  DON'T CREATE Module .db When:

**1. Simple Display/API Modules**
- Module just displays data from external APIs
- No local data storage needed
- WooCommerce, Salesforce, HubSpot (API-only)

**2. Lightweight Configuration**
- Just storing user preferences
- Simple settings (< 5 fields)
- UI state/filters
- Use `localStorage` or shared `module_preferences` table

**3. Shared Data**
- Data used by multiple modules
- User accounts, authentication
- Global settings
- Platform-wide features

**4. Small Lookup Tables**
- < 10 tables
- < 1000 records total
- No complex relationships
- Better in main database with `module_id` field

---

## 📋 Decision Flowchart

```
Does module manage complex entities?
├─ NO → Use API calls or localStorage
└─ YES
    ├─ Is data shared across modules?
    │   ├─ YES → Use main database (ai_infrastructure.db)
    │   └─ NO → Continue
    │
    ├─ Will data volume be large (10k+ records)?
    │   ├─ YES → Create module .db 
    │   └─ NO → Continue
    │
    ├─ Should data be deletable with module?
    │   ├─ YES → Create module .db 
    │   └─ NO → Use main database
    │
    └─ Does module need 10+ tables?
        ├─ YES → Create module .db 
        └─ NO → Use main database with module_id prefix
```

---

## 🏗️ How to Create a Module Database

### Step 1: Module Structure with Database

```
UI/external/modules/project-manager/
├── manifest.json               # Module config
├── project-manager.js          # Module class
├── project-manager.css         # Styles
│
├── database/                   # Database files  NEW!
│   ├── schema.sql              # Database schema
│   ├── migrations/             # Schema migrations
│   │   ├── 001_initial.sql
│   │   ├── 002_add_tags.sql
│   │   └── migration_log.json
│   └── seeds/                  # Sample/test data
│       └── sample_data.sql
│
├── data/                       # Database instance  NEW!
│   └── project-manager.db      # SQLite database (gitignored)
│
└── tools/                      # AI-callable tools
    ├── manifest.json
    ├── projects.json
    └── tasks.json
```

---

### Step 2: Create Schema File

**File:** `database/schema.sql`

```sql
-- Project Manager Module Database Schema
-- Version: 1.0.0
-- Created: 2025-10-30

-- Enable foreign keys
PRAGMA foreign_keys = ON;

-- ==================== CORE TABLES ====================

-- Projects
CREATE TABLE projects (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    description TEXT,
    status TEXT DEFAULT 'active',  -- active, completed, archived
    priority TEXT DEFAULT 'medium', -- low, medium, high, urgent
    owner_user_id INTEGER NOT NULL, -- Reference to main system user
    start_date TEXT,
    due_date TEXT,
    completed_at TEXT,
    created_at TEXT NOT NULL DEFAULT (datetime('now')),
    updated_at TEXT NOT NULL DEFAULT (datetime('now')),
    
    -- Custom fields (JSON)
    metadata TEXT,  -- JSON: {"budget": 10000, "client": "Acme Corp"}
    
    -- Indexing
    CHECK (status IN ('active', 'completed', 'archived')),
    CHECK (priority IN ('low', 'medium', 'high', 'urgent'))
);

CREATE INDEX idx_projects_status ON projects(status);
CREATE INDEX idx_projects_owner ON projects(owner_user_id);
CREATE INDEX idx_projects_due_date ON projects(due_date);

-- Tasks
CREATE TABLE tasks (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    project_id INTEGER NOT NULL,
    title TEXT NOT NULL,
    description TEXT,
    status TEXT DEFAULT 'todo',  -- todo, in_progress, done
    priority TEXT DEFAULT 'medium',
    assigned_to_user_id INTEGER,
    parent_task_id INTEGER,  -- For subtasks
    
    -- Time tracking
    estimated_hours REAL,
    actual_hours REAL DEFAULT 0,
    
    -- Dates
    start_date TEXT,
    due_date TEXT,
    completed_at TEXT,
    created_at TEXT NOT NULL DEFAULT (datetime('now')),
    updated_at TEXT NOT NULL DEFAULT (datetime('now')),
    
    -- Relations
    FOREIGN KEY (project_id) REFERENCES projects(id) ON DELETE CASCADE,
    FOREIGN KEY (parent_task_id) REFERENCES tasks(id) ON DELETE CASCADE,
    
    CHECK (status IN ('todo', 'in_progress', 'done'))
);

CREATE INDEX idx_tasks_project ON tasks(project_id);
CREATE INDEX idx_tasks_status ON tasks(status);
CREATE INDEX idx_tasks_assigned ON tasks(assigned_to_user_id);
CREATE INDEX idx_tasks_parent ON tasks(parent_task_id);

-- Comments
CREATE TABLE comments (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    task_id INTEGER NOT NULL,
    user_id INTEGER NOT NULL,
    content TEXT NOT NULL,
    created_at TEXT NOT NULL DEFAULT (datetime('now')),
    updated_at TEXT NOT NULL DEFAULT (datetime('now')),
    
    FOREIGN KEY (task_id) REFERENCES tasks(id) ON DELETE CASCADE
);

CREATE INDEX idx_comments_task ON comments(task_id);

-- Attachments
CREATE TABLE attachments (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    task_id INTEGER NOT NULL,
    filename TEXT NOT NULL,
    file_path TEXT NOT NULL,  -- Relative path: data/attachments/...
    file_size INTEGER,
    mime_type TEXT,
    uploaded_by_user_id INTEGER NOT NULL,
    created_at TEXT NOT NULL DEFAULT (datetime('now')),
    
    FOREIGN KEY (task_id) REFERENCES tasks(id) ON DELETE CASCADE
);

CREATE INDEX idx_attachments_task ON attachments(task_id);

-- Tags (many-to-many)
CREATE TABLE tags (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT UNIQUE NOT NULL,
    color TEXT DEFAULT '#3B82F6',
    created_at TEXT NOT NULL DEFAULT (datetime('now'))
);

CREATE TABLE project_tags (
    project_id INTEGER NOT NULL,
    tag_id INTEGER NOT NULL,
    
    PRIMARY KEY (project_id, tag_id),
    FOREIGN KEY (project_id) REFERENCES projects(id) ON DELETE CASCADE,
    FOREIGN KEY (tag_id) REFERENCES tags(id) ON DELETE CASCADE
);

-- ==================== AUDIT/HISTORY ====================

-- Activity log (who did what when)
CREATE TABLE activity_log (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    entity_type TEXT NOT NULL,  -- project, task, comment
    entity_id INTEGER NOT NULL,
    action TEXT NOT NULL,  -- created, updated, deleted, status_changed
    user_id INTEGER NOT NULL,
    changes TEXT,  -- JSON: {"status": {"from": "todo", "to": "done"}}
    created_at TEXT NOT NULL DEFAULT (datetime('now'))
);

CREATE INDEX idx_activity_entity ON activity_log(entity_type, entity_id);
CREATE INDEX idx_activity_user ON activity_log(user_id);
CREATE INDEX idx_activity_date ON activity_log(created_at);

-- ==================== METADATA ====================

-- Schema version tracking
CREATE TABLE schema_version (
    version INTEGER PRIMARY KEY,
    description TEXT,
    applied_at TEXT NOT NULL DEFAULT (datetime('now'))
);

INSERT INTO schema_version (version, description) VALUES (1, 'Initial schema');

-- Module info
CREATE TABLE module_info (
    key TEXT PRIMARY KEY,
    value TEXT
);

INSERT INTO module_info (key, value) VALUES 
    ('module_id', 'project-manager'),
    ('module_version', '1.0.0'),
    ('schema_version', '1'),
    ('created_at', datetime('now'));
```

---

### Step 3: Create Database Initialization

**File:** `database/init.js` (loaded by module)

```javascript
/**
 * Database Initialization for Project Manager Module
 */
class ModuleDatabaseManager {
    constructor(moduleId) {
        this.moduleId = moduleId;
        this.dbPath = `external/modules/${moduleId}/data/${moduleId}.db`;
        this.schemaPath = `external/modules/${moduleId}/database/schema.sql`;
    }
    
    /**
     * Initialize module database
     * Called on first module load or after module reinstall
     */
    async initialize() {
        console.log(`🔧 Initializing ${this.moduleId} database...`);
        
        try {
            // Check if database exists
            const exists = await this.checkDatabaseExists();
            
            if (!exists) {
                console.log(`📦 Creating new database: ${this.dbPath}`);
                await this.createDatabase();
            } else {
                console.log(` Database exists: ${this.dbPath}`);
                // Check schema version and run migrations if needed
                await this.runMigrations();
            }
            
            return true;
        } catch (error) {
            console.error(` Database initialization failed:`, error);
            throw error;
        }
    }
    
    /**
     * Check if database file exists
     */
    async checkDatabaseExists() {
        const response = await fetch(`/api/modules/${this.moduleId}/database/exists`);
        const result = await response.json();
        return result.exists;
    }
    
    /**
     * Create new database from schema
     */
    async createDatabase() {
        // Load schema SQL
        const schemaResponse = await fetch(this.schemaPath);
        const schemaSql = await schemaResponse.text();
        
        // Send to backend to create database
        const response = await fetch(`/api/modules/${this.moduleId}/database/create`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ schema: schemaSql })
        });
        
        if (!response.ok) {
            throw new Error(`Failed to create database: ${response.statusText}`);
        }
        
        console.log(` Database created successfully`);
    }
    
    /**
     * Run pending migrations
     */
    async runMigrations() {
        const response = await fetch(`/api/modules/${this.moduleId}/database/migrate`, {
            method: 'POST'
        });
        
        const result = await response.json();
        
        if (result.migrations_applied > 0) {
            console.log(` Applied ${result.migrations_applied} migrations`);
        }
    }
    
    /**
     * Execute query against module database
     */
    async query(sql, params = []) {
        const response = await fetch(`/api/modules/${this.moduleId}/database/query`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ sql, params })
        });
        
        if (!response.ok) {
            throw new Error(`Query failed: ${response.statusText}`);
        }
        
        return await response.json();
    }
    
    /**
     * Execute update/insert/delete
     */
    async execute(sql, params = []) {
        const response = await fetch(`/api/modules/${this.moduleId}/database/execute`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ sql, params })
        });
        
        if (!response.ok) {
            throw new Error(`Execute failed: ${response.statusText}`);
        }
        
        return await response.json();
    }
    
    /**
     * Export database to JSON
     */
    async exportData() {
        const response = await fetch(`/api/modules/${this.moduleId}/database/export`);
        return await response.json();
    }
    
    /**
     * Import data from JSON
     */
    async importData(data) {
        const response = await fetch(`/api/modules/${this.moduleId}/database/import`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(data)
        });
        
        return await response.json();
    }
    
    /**
     * Backup database
     */
    async backup() {
        const response = await fetch(`/api/modules/${this.moduleId}/database/backup`, {
            method: 'POST'
        });
        
        const result = await response.json();
        console.log(` Database backed up: ${result.backup_path}`);
        return result;
    }
    
    /**
     * Delete module database (when module is uninstalled)
     */
    async destroy() {
        const confirmed = confirm(
            `⚠️ This will permanently delete all ${this.moduleId} data. Continue?`
        );
        
        if (!confirmed) return false;
        
        const response = await fetch(`/api/modules/${this.moduleId}/database/delete`, {
            method: 'DELETE'
        });
        
        if (response.ok) {
            console.log(` Database deleted: ${this.dbPath}`);
            return true;
        }
        
        return false;
    }
}
```

---

### Step 4: Integrate with Module Class

**File:** `project-manager.js`

```javascript
class ProjectManagerModule extends BaseModule {
    constructor(config) {
        super(config);
        
        // Initialize database manager
        this.db = new ModuleDatabaseManager(config.id);
        
        this.projects = [];
        this.tasks = [];
    }
    
    async initialize() {
        console.log('🔧 Initializing Project Manager module...');
        
        // Initialize module database
        await this.db.initialize();
        
        // Load tools
        await this.loadTools();
        this.registerToolsWithAI();
        
        // Apply colors
        this.applyModuleColors();
        
        // Initialize UI
        await super.initialize();
        
        console.log(' Project Manager module ready');
    }
    
    // ==================== TOOL IMPLEMENTATIONS ====================
    
    /**
     * Tool: Get Projects
     */
    async getProjects(params = {}) {
        const { status = 'active', limit = 50, offset = 0 } = params;
        
        const result = await this.db.query(`
            SELECT 
                p.*,
                COUNT(t.id) as task_count,
                SUM(CASE WHEN t.status = 'done' THEN 1 ELSE 0 END) as completed_tasks
            FROM projects p
            LEFT JOIN tasks t ON t.project_id = p.id
            WHERE p.status = ?
            GROUP BY p.id
            ORDER BY p.updated_at DESC
            LIMIT ? OFFSET ?
        `, [status, limit, offset]);
        
        return {
            projects: result.rows,
            total: result.total,
            pages: Math.ceil(result.total / limit)
        };
    }
    
    /**
     * Tool: Create Project
     */
    async createProject(params) {
        const { name, description, priority = 'medium', start_date, due_date } = params;
        
        // Get current user ID from session
        const userId = window.currentUser?.id || 1;
        
        const result = await this.db.execute(`
            INSERT INTO projects (name, description, priority, owner_user_id, start_date, due_date)
            VALUES (?, ?, ?, ?, ?, ?)
        `, [name, description, priority, userId, start_date, due_date]);
        
        // Log activity
        await this.logActivity('project', result.lastInsertId, 'created', userId);
        
        return {
            id: result.lastInsertId,
            name,
            description,
            priority,
            status: 'active'
        };
    }
    
    /**
     * Tool: Get Project with Tasks
     */
    async getProjectDetails(params) {
        const { project_id } = params;
        
        // Get project
        const projectResult = await this.db.query(
            'SELECT * FROM projects WHERE id = ?',
            [project_id]
        );
        
        if (projectResult.rows.length === 0) {
            throw new Error(`Project not found: ${project_id}`);
        }
        
        const project = projectResult.rows[0];
        
        // Get tasks
        const tasksResult = await this.db.query(`
            SELECT 
                t.*,
                COUNT(c.id) as comment_count,
                COUNT(a.id) as attachment_count
            FROM tasks t
            LEFT JOIN comments c ON c.task_id = t.id
            LEFT JOIN attachments a ON a.task_id = t.id
            WHERE t.project_id = ?
            GROUP BY t.id
            ORDER BY t.created_at DESC
        `, [project_id]);
        
        project.tasks = tasksResult.rows;
        
        // Get tags
        const tagsResult = await this.db.query(`
            SELECT tg.* FROM tags tg
            JOIN project_tags pt ON pt.tag_id = tg.id
            WHERE pt.project_id = ?
        `, [project_id]);
        
        project.tags = tagsResult.rows;
        
        return project;
    }
    
    /**
     * Smart Tool: Project Summary Report
     */
    async smartProjectReport(params) {
        const { project_id } = params;
        
        // Get full project details
        const project = await this.getProjectDetails({ project_id });
        
        // Calculate statistics
        const stats = {
            total_tasks: project.tasks.length,
            completed_tasks: project.tasks.filter(t => t.status === 'done').length,
            in_progress_tasks: project.tasks.filter(t => t.status === 'in_progress').length,
            overdue_tasks: project.tasks.filter(t => {
                return t.due_date && new Date(t.due_date) < new Date() && t.status !== 'done';
            }).length,
            total_estimated_hours: project.tasks.reduce((sum, t) => sum + (t.estimated_hours || 0), 0),
            total_actual_hours: project.tasks.reduce((sum, t) => sum + (t.actual_hours || 0), 0)
        };
        
        // Calculate completion percentage
        stats.completion_percentage = stats.total_tasks > 0
            ? Math.round((stats.completed_tasks / stats.total_tasks) * 100)
            : 0;
        
        // Get recent activity
        const activityResult = await this.db.query(`
            SELECT * FROM activity_log
            WHERE entity_type IN ('project', 'task')
            AND (entity_id = ? OR entity_id IN (
                SELECT id FROM tasks WHERE project_id = ?
            ))
            ORDER BY created_at DESC
            LIMIT 20
        `, [project_id, project_id]);
        
        return {
            project: {
                id: project.id,
                name: project.name,
                status: project.status,
                priority: project.priority
            },
            statistics: stats,
            recent_activity: activityResult.rows,
            recommendations: this.generateRecommendations(project, stats)
        };
    }
    
    /**
     * Generate AI recommendations
     */
    generateRecommendations(project, stats) {
        const recommendations = [];
        
        if (stats.overdue_tasks > 0) {
            recommendations.push({
                type: 'warning',
                message: `${stats.overdue_tasks} tasks are overdue`,
                action: 'Review and update due dates'
            });
        }
        
        if (stats.completion_percentage > 80 && project.status === 'active') {
            recommendations.push({
                type: 'success',
                message: 'Project is nearly complete',
                action: 'Consider moving to completed status'
            });
        }
        
        if (stats.total_actual_hours > stats.total_estimated_hours * 1.2) {
            recommendations.push({
                type: 'info',
                message: 'Actual hours exceed estimates by 20%',
                action: 'Review time estimates for future projects'
            });
        }
        
        return recommendations;
    }
    
    /**
     * Log activity to audit trail
     */
    async logActivity(entityType, entityId, action, userId) {
        await this.db.execute(`
            INSERT INTO activity_log (entity_type, entity_id, action, user_id)
            VALUES (?, ?, ?, ?)
        `, [entityType, entityId, action, userId]);
    }
    
    /**
     * Export module data
     */
    async exportDashboardData(params = {}) {
        const { subtab = 'all' } = params;
        
        const data = {
            module: this.config.id,
            timestamp: new Date().toISOString(),
            subtab
        };
        
        switch (subtab) {
            case 'projects':
            case 'all':
                data.projects = await this.getProjects({ limit: 1000 });
                if (subtab !== 'all') break;
                
            case 'tasks':
                data.tasks = await this.db.query('SELECT * FROM tasks ORDER BY created_at DESC LIMIT 1000');
                if (subtab !== 'all') break;
        }
        
        return data;
    }
    
    /**
     * Handle module uninstall
     */
    async onUninstall() {
        console.log('⚠️ Uninstalling Project Manager module...');
        
        // Backup data before deletion
        await this.db.backup();
        
        // Delete database
        const deleted = await this.db.destroy();
        
        if (deleted) {
            console.log(' Module data deleted successfully');
        }
    }
}
```

---

### Step 5: Backend API Routes

**File:** `AI_infrastructure/routes/module_database_routes.py`

```python
"""
Module Database Routes
Handles database operations for modules with their own .db files
"""

from flask import Blueprint, request, jsonify
import sqlite3
import os
import shutil
from datetime import datetime
from pathlib import Path

module_db_bp = Blueprint('module_database', __name__, url_prefix='/api/modules/<module_id>/database')

MODULE_BASE_PATH = Path('UI/external/modules')

def get_module_db_path(module_id: str) -> Path:
    """Get path to module database"""
    return MODULE_BASE_PATH / module_id / 'data' / f'{module_id}.db'

def get_module_schema_path(module_id: str) -> Path:
    """Get path to module schema"""
    return MODULE_BASE_PATH / module_id / 'database' / 'schema.sql'


@module_db_bp.route('/exists', methods=['GET'])
def check_database_exists(module_id):
    """Check if module database exists"""
    db_path = get_module_db_path(module_id)
    return jsonify({'exists': db_path.exists()})


@module_db_bp.route('/create', methods=['POST'])
def create_database(module_id):
    """Create new module database from schema"""
    try:
        data = request.get_json()
        schema_sql = data.get('schema')
        
        if not schema_sql:
            return jsonify({'error': 'Schema SQL required'}), 400
        
        # Ensure data directory exists
        db_path = get_module_db_path(module_id)
        db_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Create database
        conn = sqlite3.connect(str(db_path))
        cursor = conn.cursor()
        cursor.executescript(schema_sql)
        conn.commit()
        conn.close()
        
        return jsonify({
            'success': True,
            'db_path': str(db_path),
            'message': f'Database created for {module_id}'
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@module_db_bp.route('/query', methods=['POST'])
def execute_query(module_id):
    """Execute SELECT query"""
    try:
        data = request.get_json()
        sql = data.get('sql')
        params = data.get('params', [])
        
        db_path = get_module_db_path(module_id)
        
        if not db_path.exists():
            return jsonify({'error': 'Database not found'}), 404
        
        conn = sqlite3.connect(str(db_path))
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        cursor.execute(sql, params)
        rows = [dict(row) for row in cursor.fetchall()]
        
        # Get total count if LIMIT was used
        count_sql = sql.split('LIMIT')[0]
        cursor.execute(f"SELECT COUNT(*) as total FROM ({count_sql})")
        total = cursor.fetchone()['total']
        
        conn.close()
        
        return jsonify({
            'rows': rows,
            'total': total,
            'count': len(rows)
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@module_db_bp.route('/execute', methods=['POST'])
def execute_update(module_id):
    """Execute INSERT/UPDATE/DELETE"""
    try:
        data = request.get_json()
        sql = data.get('sql')
        params = data.get('params', [])
        
        db_path = get_module_db_path(module_id)
        
        if not db_path.exists():
            return jsonify({'error': 'Database not found'}), 404
        
        conn = sqlite3.connect(str(db_path))
        cursor = conn.cursor()
        
        cursor.execute(sql, params)
        conn.commit()
        
        result = {
            'rowcount': cursor.rowcount,
            'lastInsertId': cursor.lastrowid
        }
        
        conn.close()
        
        return jsonify(result)
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@module_db_bp.route('/backup', methods=['POST'])
def backup_database(module_id):
    """Backup module database"""
    try:
        db_path = get_module_db_path(module_id)
        
        if not db_path.exists():
            return jsonify({'error': 'Database not found'}), 404
        
        # Create backups directory
        backup_dir = MODULE_BASE_PATH / module_id / 'data' / 'backups'
        backup_dir.mkdir(parents=True, exist_ok=True)
        
        # Create backup with timestamp
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        backup_path = backup_dir / f'{module_id}_backup_{timestamp}.db'
        
        shutil.copy2(db_path, backup_path)
        
        return jsonify({
            'success': True,
            'backup_path': str(backup_path),
            'size': os.path.getsize(backup_path)
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@module_db_bp.route('/export', methods=['GET'])
def export_database(module_id):
    """Export database to JSON"""
    try:
        db_path = get_module_db_path(module_id)
        
        if not db_path.exists():
            return jsonify({'error': 'Database not found'}), 404
        
        conn = sqlite3.connect(str(db_path))
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        # Get all tables
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = [row['name'] for row in cursor.fetchall()]
        
        # Export all data
        export_data = {}
        for table in tables:
            cursor.execute(f"SELECT * FROM {table}")
            export_data[table] = [dict(row) for row in cursor.fetchall()]
        
        conn.close()
        
        return jsonify({
            'module_id': module_id,
            'exported_at': datetime.now().isoformat(),
            'tables': export_data
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@module_db_bp.route('/delete', methods=['DELETE'])
def delete_database(module_id):
    """Delete module database (uninstall)"""
    try:
        db_path = get_module_db_path(module_id)
        
        if not db_path.exists():
            return jsonify({'error': 'Database not found'}), 404
        
        # Delete database file
        os.remove(db_path)
        
        return jsonify({
            'success': True,
            'message': f'Database deleted for {module_id}'
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500
```

---

## 🔒 Security Considerations

### 1. SQL Injection Prevention
```javascript
//  GOOD - Use parameterized queries
await this.db.query(
    'SELECT * FROM projects WHERE owner_user_id = ?',
    [userId]
);

//  BAD - String concatenation
await this.db.query(
    `SELECT * FROM projects WHERE owner_user_id = ${userId}`
);
```

### 2. User Isolation
```sql
-- Always filter by user_id to prevent data leakage
SELECT * FROM projects 
WHERE owner_user_id = ?  -- Current user only
AND status = 'active';
```

### 3. Backup Before Destructive Operations
```javascript
async deleteProject(projectId) {
    // Backup first
    await this.db.backup();
    
    // Then delete
    await this.db.execute('DELETE FROM projects WHERE id = ?', [projectId]);
}
```

---

## 📦 Module Distribution & Updates

### .gitignore Configuration
```gitignore
# Module data directories (DO NOT commit)
UI/external/modules/*/data/*.db
UI/external/modules/*/data/backups/
UI/external/modules/*/data/attachments/

# Keep schema and migrations
!UI/external/modules/*/database/
```

### Migration System

**File:** `database/migrations/001_add_tags.sql`
```sql
-- Migration: Add tags support
-- Version: 2
-- Date: 2025-11-01

-- Add new tables
CREATE TABLE IF NOT EXISTS tags (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT UNIQUE NOT NULL,
    color TEXT DEFAULT '#3B82F6'
);

CREATE TABLE IF NOT EXISTS project_tags (
    project_id INTEGER NOT NULL,
    tag_id INTEGER NOT NULL,
    PRIMARY KEY (project_id, tag_id),
    FOREIGN KEY (project_id) REFERENCES projects(id) ON DELETE CASCADE,
    FOREIGN KEY (tag_id) REFERENCES tags(id) ON DELETE CASCADE
);

-- Update schema version
UPDATE schema_version SET version = 2, applied_at = datetime('now')
WHERE version = 1;
```

---

##  Complete Example: Task Manager Module

### Manifest
```json
{
    "id": "task-manager",
    "name": "Task Manager",
    "icon": "fas fa-tasks",
    "version": "1.0.0",
    "colors": {
        "primary": "#8b5cf6",
        "secondary": "#c4b5fd",
        "hover": "#7c3aed"
    },
    "has_database": true,
    "database": {
        "version": "1.0.0",
        "tables": 12,
        "migrations": true,
        "backup": true,
        "export": true
    },
    "tabs": [
        {"id": "projects", "label": "Projects", "icon": "fas fa-project-diagram", "default": true},
        {"id": "tasks", "label": "Tasks", "icon": "fas fa-check-square"},
        {"id": "reports", "label": "Reports", "icon": "fas fa-chart-bar"}
    ]
}
```

---

## 🎯 Best Practices Summary

###  DO:
- Create module .db for complex, self-contained data
- Use schema.sql for version-controlled schema
- Implement migration system for updates
- Backup before destructive operations
- Log all changes to audit trail
- Filter by user_id for security
- Use parameterized queries
- Export/import capabilities for portability

###  DON'T:
- Store shared/global data in module db
- Hardcode database paths
- Use string concatenation for SQL
- Skip foreign key constraints
- Forget to index frequently queried columns
- Commit .db files to git
- Skip backups before uninstall
- Allow cross-user data access

---

**Last Updated:** October 30, 2025  
**Version:** 1.0.0  
**Status:**  Production Ready

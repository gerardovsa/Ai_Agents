# 🚀 Advanced Integrations Guide - Business AI Platform

**Date**: October 23, 2025  
**Status**: Enhancement Specifications

---

## 📋 Table of Contents

1. [Message Popup System](#1-message-popup-system) ✅ IMPLEMENTED
2. [ONLYOFFICE Integration](#2-onlyoffice-integration)
3. [Automated Workflows](#3-automated-workflows)
4. [Team Project Management](#4-team-project-management)
5. [Database Schema](#5-database-schema)
6. [Chat History & Management](#6-chat-history--management)
7. [Required Libraries](#7-required-libraries)

---

## 1️⃣ **Message Popup System** ✅

### **Implementation Status**: COMPLETE

### **How It Works**:
```javascript
// Click any AI message → Full-screen popup appears
// Features:
- Click message bubble to expand
- Modal overlay with full content
- Copy to clipboard button
- Markdown/code rendering preserved
- Close on overlay click or button
```

### **Usage**:
- User clicks any chat message
- Popup shows full content (especially useful for long AI responses)
- Can copy entire message with one click
- Preserves formatting (markdown, code blocks)

---

## 2️⃣ **ONLYOFFICE Integration**

### **What Is ONLYOFFICE?**
Open-source office suite for document editing (Word, Excel, PowerPoint) with real-time collaboration.

### **Integration Architecture**:

```
┌─────────────────────────────────────────────────────────────┐
│  Business AI Platform                                       │
│  ┌────────────────┐         ┌──────────────────┐          │
│  │ Documents Tab  │ ◄────► │ ONLYOFFICE       │          │
│  │                │         │ Document Server  │          │
│  │ - File List    │         │ (Docker)         │          │
│  │ - Create Doc   │         │                  │          │
│  │ - Edit Doc     │         │ Port: 8000       │          │
│  │ - Convert      │         └──────────────────┘          │
│  └────────────────┘                                        │
│         ▲                                                   │
│         │                                                   │
│         ▼                                                   │
│  ┌────────────────────────────────────────────────────┐   │
│  │ Document Storage (Google Drive / Supabase Storage) │   │
│  └────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────┘
```

### **Setup Steps**:

#### **Option A: Docker Deployment** (Recommended)
```bash
# 1. Install ONLYOFFICE Document Server
docker pull onlyoffice/documentserver

# 2. Run container
docker run -i -t -d -p 8000:80 --name onlyoffice-server \
  -v /app/onlyoffice/DocumentServer/logs:/var/log/onlyoffice \
  -v /app/onlyoffice/DocumentServer/data:/var/www/onlyoffice/Data \
  onlyoffice/documentserver

# 3. Access: http://localhost:8000
```

#### **Option B: Cloud Hosted** (ONLYOFFICE Cloud)
```javascript
// Use ONLYOFFICE API key
const config = {
  apiUrl: 'https://api.onlyoffice.com',
  apiKey: process.env.ONLYOFFICE_API_KEY
};
```

### **Frontend Integration**:

```javascript
// documents-tab.js - ONLYOFFICE Editor Component

class OnlyOfficeEditor {
    constructor(containerId) {
        this.containerId = containerId;
        this.documentServerUrl = 'http://localhost:8000';
    }
    
    async openDocument(fileUrl, fileName, fileType) {
        const config = {
            documentType: this.getDocumentType(fileType), // 'word', 'cell', 'slide'
            document: {
                fileType: fileType,
                key: this.generateDocumentKey(fileUrl),
                title: fileName,
                url: fileUrl,
                permissions: {
                    edit: true,
                    download: true,
                    print: true
                }
            },
            editorConfig: {
                mode: 'edit', // or 'view'
                lang: 'en',
                callbackUrl: `${API_BASE_URL}/api/v1/documents/callback`,
                user: {
                    id: AppState.userId,
                    name: AppState.userName
                },
                customization: {
                    chat: true,
                    comments: true,
                    help: true,
                    hideRightMenu: false
                }
            }
        };
        
        // Initialize ONLYOFFICE editor
        new DocsAPI.DocEditor(this.containerId, config);
    }
    
    getDocumentType(fileType) {
        const types = {
            'docx': 'word', 'doc': 'word', 'odt': 'word',
            'xlsx': 'cell', 'xls': 'cell', 'ods': 'cell',
            'pptx': 'slide', 'ppt': 'slide', 'odp': 'slide'
        };
        return types[fileType] || 'word';
    }
    
    generateDocumentKey(fileUrl) {
        // Unique key for document versioning
        return btoa(fileUrl + Date.now()).substring(0, 20);
    }
}

// Usage in Documents Tab
async function editDocument(fileId) {
    const fileData = await connector.executeTool('google_drive_get_file', {
        file_id: fileId
    });
    
    const editor = new OnlyOfficeEditor('onlyoffice-editor-container');
    await editor.openDocument(
        fileData.downloadUrl,
        fileData.name,
        fileData.mimeType
    );
}
```

### **Backend Callback Handler**:

```python
# app.py - ONLYOFFICE callback endpoint

from flask import request, jsonify

@app.route('/api/v1/documents/callback', methods=['POST'])
def onlyoffice_callback():
    """
    Handle ONLYOFFICE document save callback
    Status codes:
    - 1: Document is being edited
    - 2: Document is ready for saving
    - 3: Document saving error
    - 4: Document closed with no changes
    """
    data = request.json
    status = data.get('status')
    
    if status == 2:  # Ready to save
        download_url = data.get('url')
        key = data.get('key')
        
        # Download the edited document
        response = requests.get(download_url)
        
        # Save to Google Drive or Supabase Storage
        save_result = save_document_to_storage(
            file_content=response.content,
            document_key=key
        )
        
        return jsonify({'error': 0})
    
    return jsonify({'error': 0})
```

### **Required Libraries**:
```html
<!-- Add to HTML head -->
<script src="http://localhost:8000/web-apps/apps/api/documents/api.js"></script>
```

```bash
# Backend
pip install requests python-magic
```

### **Features Enabled**:
- ✅ Real-time collaborative editing
- ✅ Track changes and comments
- ✅ Auto-save to cloud storage
- ✅ Version history
- ✅ Convert between formats (DOCX ↔ PDF ↔ ODT)
- ✅ Integrate with Google Drive
- ✅ AI-powered document generation

---

## 3️⃣ **Automated Workflows**

### **Architecture**:

```
┌─────────────────────────────────────────────────────────┐
│  Workflow Engine                                        │
│                                                         │
│  ┌──────────┐    ┌──────────┐    ┌──────────┐        │
│  │ TRIGGER  │ ──► │ ACTIONS  │ ──► │ OUTCOME  │        │
│  └──────────┘    └──────────┘    └──────────┘        │
│       │               │                 │              │
│   Webhook         Tool Exec         Notification       │
│   Schedule        API Call          Storage            │
│   Platform        Condition         Report             │
└─────────────────────────────────────────────────────────┘
```

### **Implementation with n8n Integration**:

#### **Option A: Embedded n8n** (Open-Source Workflow Automation)
```bash
# Install n8n
npm install n8n -g

# Or via Docker
docker run -it --rm \
  --name n8n \
  -p 5678:5678 \
  -v ~/.n8n:/home/node/.n8n \
  n8nio/n8n

# Access: http://localhost:5678
```

#### **Option B: Custom Workflow Engine**

```javascript
// tabs/automation-tab.js - Visual Workflow Builder

class WorkflowBuilder {
    constructor() {
        this.canvas = document.getElementById('workflow-canvas');
        this.workflows = [];
        this.initDragAndDrop();
    }
    
    createWorkflow(config) {
        return {
            id: this.generateId(),
            name: config.name,
            enabled: true,
            trigger: {
                type: config.trigger.type, // 'webhook', 'schedule', 'platform_event'
                config: config.trigger.config
            },
            actions: config.actions.map(action => ({
                tool: action.tool,
                parameters: action.parameters,
                condition: action.condition // Optional if/else logic
            })),
            created: new Date()
        };
    }
    
    async executeWorkflow(workflowId, triggerData = {}) {
        const workflow = this.workflows.find(w => w.id === workflowId);
        if (!workflow || !workflow.enabled) return;
        
        const executionLog = {
            workflowId,
            startTime: Date.now(),
            steps: []
        };
        
        // Execute each action sequentially
        for (const action of workflow.actions) {
            // Check condition if exists
            if (action.condition && !this.evaluateCondition(action.condition, triggerData)) {
                continue;
            }
            
            const stepResult = await connector.executeTool(
                action.tool,
                this.mergeParameters(action.parameters, triggerData)
            );
            
            executionLog.steps.push({
                action: action.tool,
                result: stepResult,
                timestamp: Date.now()
            });
            
            // If step fails and no error handling, stop workflow
            if (!stepResult.success && !action.continueOnError) {
                break;
            }
        }
        
        executionLog.endTime = Date.now();
        executionLog.duration = executionLog.endTime - executionLog.startTime;
        
        this.saveExecutionLog(executionLog);
        return executionLog;
    }
    
    mergeParameters(parameters, triggerData) {
        // Replace {{variable}} with actual values
        const merged = JSON.parse(JSON.stringify(parameters));
        const replacer = (obj) => {
            for (const key in obj) {
                if (typeof obj[key] === 'string' && obj[key].includes('{{')) {
                    obj[key] = obj[key].replace(/\{\{(\w+)\}\}/g, (match, varName) => {
                        return triggerData[varName] || match;
                    });
                } else if (typeof obj[key] === 'object') {
                    replacer(obj[key]);
                }
            }
        };
        replacer(merged);
        return merged;
    }
    
    renderWorkflowDiagram(workflow) {
        // Use Mermaid.js for visual flowchart
        const nodes = [`graph LR\n`];
        nodes.push(`  A[${workflow.trigger.type}] --> B{Start}\n`);
        
        workflow.actions.forEach((action, index) => {
            const nodeId = String.fromCharCode(67 + index); // C, D, E...
            nodes.push(`  B --> ${nodeId}[${action.tool}]\n`);
            if (index < workflow.actions.length - 1) {
                const nextId = String.fromCharCode(68 + index);
                nodes.push(`  ${nodeId} --> ${nextId}\n`);
            }
        });
        
        const mermaidCode = nodes.join('');
        mermaid.render('workflow-diagram-' + workflow.id, mermaidCode);
    }
}

// Example Workflow: "New Order Processing"
const exampleWorkflow = {
    name: "New WooCommerce Order Processing",
    trigger: {
        type: "platform_event",
        config: {
            platform: "woocommerce",
            event: "order.created"
        }
    },
    actions: [
        {
            tool: "slack_send_message",
            parameters: {
                channel: "#sales",
                text: "🎉 New order #{{order_id}} from {{customer_name}} - Total: ${{order_total}}"
            }
        },
        {
            tool: "gsheets_append_row",
            parameters: {
                spreadsheet_id: "1ABC...",
                range: "Orders!A:E",
                values: ["{{order_id}}", "{{customer_name}}", "{{order_total}}", "{{date}}", "pending"]
            }
        },
        {
            tool: "gmail_send_email",
            parameters: {
                to: "{{customer_email}}",
                subject: "Order Confirmation #{{order_id}}",
                body: "Thank you for your order!"
            },
            condition: {
                field: "order_total",
                operator: ">",
                value: 100
            }
        }
    ]
};
```

### **Backend Webhook Handler**:

```python
# app.py - Webhook endpoint for workflow triggers

@app.route('/api/v1/workflows/webhook/<workflow_id>', methods=['POST'])
def workflow_webhook(workflow_id):
    """
    Receive webhook from external platforms to trigger workflows
    """
    trigger_data = request.json
    
    # Execute workflow
    result = execute_workflow(workflow_id, trigger_data)
    
    return jsonify({
        'success': True,
        'execution_id': result['id'],
        'steps_completed': len(result['steps'])
    })

@app.route('/api/v1/workflows/schedule', methods=['GET'])
def check_scheduled_workflows():
    """
    Cron job to check for scheduled workflows
    Run every minute via external scheduler
    """
    from datetime import datetime
    
    now = datetime.now()
    workflows = get_scheduled_workflows(now)
    
    for workflow in workflows:
        execute_workflow(workflow['id'], {
            'trigger_time': now.isoformat()
        })
    
    return jsonify({'checked': len(workflows)})
```

### **Required Libraries**:
```bash
# Frontend
npm install mermaid  # Already included

# Backend
pip install schedule  # For cron-like scheduling
pip install celery redis  # For async task execution
```

---

## 4️⃣ **Team Project Management & To-Do's**

### **Architecture**:

```
┌──────────────────────────────────────────────────────────┐
│  Project Management Tab                                  │
│                                                          │
│  ┌────────────┐  ┌──────────────┐  ┌────────────────┐ │
│  │ Projects   │  │ Task Board   │  │ Team Calendar │ │
│  │            │  │              │  │                │ │
│  │ - Active   │  │ - Kanban     │  │ - Deadlines    │ │
│  │ - Archived │  │ - Gantt      │  │ - Milestones   │ │
│  │ - Template │  │ - Timeline   │  │ - Meetings     │ │
│  └────────────┘  └──────────────┘  └────────────────┘ │
│                                                          │
│  ┌─────────────────────────────────────────────────┐   │
│  │ Team Collaboration                               │   │
│  │ - Comments, Mentions (@user)                     │   │
│  │ - File Attachments                               │   │
│  │ - Activity Feed                                  │   │
│  └─────────────────────────────────────────────────┘   │
└──────────────────────────────────────────────────────────┘
```

### **Integration Options**:

#### **Option A: Custom Built** (Recommended for full control)

```javascript
// tabs/projects-tab.js

class ProjectManager {
    constructor() {
        this.projects = [];
        this.tasks = [];
        this.initKanbanBoard();
    }
    
    async loadProjects() {
        const projects = await connector.executeTool('supabase_query', {
            table: 'projects',
            select: '*',
            order: 'created_at.desc'
        });
        
        this.renderProjectsList(projects.data);
    }
    
    createKanbanBoard(projectId) {
        // Use jKanban or custom implementation
        const kanban = new jKanban({
            element: '#kanban-board',
            boards: [
                {
                    id: 'todo',
                    title: 'To Do',
                    item: this.getTasksByStatus(projectId, 'todo')
                },
                {
                    id: 'in-progress',
                    title: 'In Progress',
                    item: this.getTasksByStatus(projectId, 'in_progress')
                },
                {
                    id: 'review',
                    title: 'Review',
                    item: this.getTasksByStatus(projectId, 'review')
                },
                {
                    id: 'done',
                    title: 'Done',
                    item: this.getTasksByStatus(projectId, 'done')
                }
            ],
            dragBoards: true,
            dragItems: true,
            dropEl: (el, target, source) => {
                this.updateTaskStatus(el.dataset.taskId, target.dataset.status);
            }
        });
    }
    
    createGanttChart(projectId) {
        // Use Frappe Gantt
        const tasks = this.getProjectTasks(projectId);
        
        const gantt = new Gantt('#gantt-container', tasks, {
            view_mode: 'Week',
            date_format: 'YYYY-MM-DD',
            custom_popup_html: (task) => {
                return `
                    <div class="gantt-popup">
                        <h4>${task.name}</h4>
                        <p>Assigned: ${task.assignee}</p>
                        <p>Progress: ${task.progress}%</p>
                    </div>
                `;
            },
            on_click: (task) => {
                this.openTaskDetails(task.id);
            },
            on_date_change: (task, start, end) => {
                this.updateTaskDates(task.id, start, end);
            },
            on_progress_change: (task, progress) => {
                this.updateTaskProgress(task.id, progress);
            }
        });
    }
    
    async createTask(projectId, taskData) {
        const task = {
            project_id: projectId,
            title: taskData.title,
            description: taskData.description,
            assignee_id: taskData.assignee,
            status: 'todo',
            priority: taskData.priority, // 'low', 'medium', 'high', 'urgent'
            due_date: taskData.dueDate,
            tags: taskData.tags,
            created_by: AppState.userId,
            created_at: new Date().toISOString()
        };
        
        const result = await connector.executeTool('supabase_insert', {
            table: 'tasks',
            data: task
        });
        
        // Send notification to assignee
        if (result.success) {
            this.notifyAssignee(taskData.assignee, task);
        }
        
        return result;
    }
    
    async addComment(taskId, comment) {
        // Support @mentions
        const mentions = this.extractMentions(comment);
        
        const commentData = {
            task_id: taskId,
            user_id: AppState.userId,
            content: comment,
            mentions: mentions,
            created_at: new Date().toISOString()
        };
        
        await connector.executeTool('supabase_insert', {
            table: 'task_comments',
            data: commentData
        });
        
        // Notify mentioned users
        mentions.forEach(userId => {
            this.sendMentionNotification(userId, taskId, comment);
        });
    }
    
    extractMentions(text) {
        // Extract @username mentions
        const regex = /@(\w+)/g;
        const matches = text.match(regex) || [];
        return matches.map(m => m.substring(1));
    }
}
```

#### **Option B: Integrate Existing Tools**

```javascript
// Integration with Trello/Asana/Monday.com APIs

class TrelloIntegration {
    async syncFromTrello() {
        const boards = await connector.executeTool('trello_get_boards', {});
        
        // Import into local database
        for (const board of boards.data) {
            await this.importTrelloBoard(board);
        }
    }
}
```

### **Required Libraries**:

```html
<!-- Kanban Board -->
<link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/jkanban@1.3.1/dist/jkanban.min.css">
<script src="https://cdn.jsdelivr.net/npm/jkanban@1.3.1/dist/jkanban.min.js"></script>

<!-- Gantt Chart -->
<link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/frappe-gantt@0.6.1/dist/frappe-gantt.css">
<script src="https://cdn.jsdelivr.net/npm/frappe-gantt@0.6.1/dist/frappe-gantt.min.js"></script>

<!-- Drag and Drop -->
<script src="https://cdn.jsdelivr.net/npm/sortablejs@1.15.0/Sortable.min.js"></script>
```

```bash
# Backend
pip install python-trello asana monday  # If integrating external tools
```

---

## 5️⃣ **Database Schema**

### **Supabase Schema** (Recommended for cloud + real-time)

```sql
-- ==================== USERS & AUTHENTICATION ====================
CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    email VARCHAR(255) UNIQUE NOT NULL,
    name VARCHAR(255),
    avatar_url TEXT,
    role VARCHAR(50) DEFAULT 'user', -- 'admin', 'user', 'viewer'
    created_at TIMESTAMP DEFAULT NOW(),
    last_login TIMESTAMP
);

-- ==================== CHAT HISTORY ====================
CREATE TABLE chat_sessions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    title VARCHAR(255),
    context_tab VARCHAR(50), -- 'home', 'communication', 'sales', etc.
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE chat_messages (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    session_id UUID REFERENCES chat_sessions(id) ON DELETE CASCADE,
    role VARCHAR(20) NOT NULL, -- 'user', 'assistant', 'system'
    content TEXT NOT NULL,
    tokens INTEGER,
    tool_calls JSONB, -- Store tool execution data
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_messages_session ON chat_messages(session_id);
CREATE INDEX idx_messages_created ON chat_messages(created_at DESC);

-- ==================== PLATFORM CONNECTIONS ====================
CREATE TABLE platform_connections (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    platform VARCHAR(50) NOT NULL, -- 'slack', 'woocommerce', etc.
    status VARCHAR(20) DEFAULT 'connected', -- 'connected', 'disconnected', 'error'
    credentials JSONB ENCRYPTED, -- Encrypted API keys
    last_sync TIMESTAMP,
    created_at TIMESTAMP DEFAULT NOW()
);

-- ==================== PROJECTS & TASKS ====================
CREATE TABLE projects (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(255) NOT NULL,
    description TEXT,
    owner_id UUID REFERENCES users(id),
    status VARCHAR(50) DEFAULT 'active', -- 'active', 'archived', 'completed'
    start_date DATE,
    end_date DATE,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE tasks (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    project_id UUID REFERENCES projects(id) ON DELETE CASCADE,
    title VARCHAR(255) NOT NULL,
    description TEXT,
    assignee_id UUID REFERENCES users(id),
    status VARCHAR(50) DEFAULT 'todo', -- 'todo', 'in_progress', 'review', 'done'
    priority VARCHAR(20) DEFAULT 'medium', -- 'low', 'medium', 'high', 'urgent'
    due_date DATE,
    progress INTEGER DEFAULT 0, -- 0-100
    tags TEXT[],
    created_by UUID REFERENCES users(id),
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE task_comments (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    task_id UUID REFERENCES tasks(id) ON DELETE CASCADE,
    user_id UUID REFERENCES users(id),
    content TEXT NOT NULL,
    mentions UUID[], -- Array of mentioned user IDs
    created_at TIMESTAMP DEFAULT NOW()
);

-- ==================== WORKFLOWS ====================
CREATE TABLE workflows (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(255) NOT NULL,
    description TEXT,
    trigger_type VARCHAR(50), -- 'webhook', 'schedule', 'platform_event'
    trigger_config JSONB,
    actions JSONB, -- Array of action objects
    enabled BOOLEAN DEFAULT true,
    created_by UUID REFERENCES users(id),
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE workflow_executions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    workflow_id UUID REFERENCES workflows(id),
    trigger_data JSONB,
    steps JSONB, -- Execution log
    status VARCHAR(20), -- 'success', 'failed', 'partial'
    duration_ms INTEGER,
    created_at TIMESTAMP DEFAULT NOW()
);

-- ==================== DOCUMENTS ====================
CREATE TABLE documents (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(255) NOT NULL,
    file_type VARCHAR(50),
    storage_url TEXT NOT NULL,
    size_bytes BIGINT,
    owner_id UUID REFERENCES users(id),
    project_id UUID REFERENCES projects(id),
    version INTEGER DEFAULT 1,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE document_versions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    document_id UUID REFERENCES documents(id) ON DELETE CASCADE,
    version INTEGER NOT NULL,
    storage_url TEXT NOT NULL,
    changes_summary TEXT,
    created_by UUID REFERENCES users(id),
    created_at TIMESTAMP DEFAULT NOW()
);

-- ==================== ACTIVITY FEED ====================
CREATE TABLE activities (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id),
    action_type VARCHAR(50), -- 'task_created', 'message_sent', etc.
    entity_type VARCHAR(50), -- 'task', 'project', 'document'
    entity_id UUID,
    description TEXT,
    metadata JSONB,
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_activities_user ON activities(user_id);
CREATE INDEX idx_activities_created ON activities(created_at DESC);

-- ==================== ENABLE ROW LEVEL SECURITY ====================
ALTER TABLE users ENABLE ROW LEVEL SECURITY;
ALTER TABLE chat_sessions ENABLE ROW LEVEL SECURITY;
ALTER TABLE chat_messages ENABLE ROW LEVEL SECURITY;
ALTER TABLE projects ENABLE ROW LEVEL SECURITY;
ALTER TABLE tasks ENABLE ROW LEVEL SECURITY;

-- Users can only see their own data
CREATE POLICY "Users can view own data" ON users
    FOR SELECT USING (auth.uid() = id);

CREATE POLICY "Users can view own chat sessions" ON chat_sessions
    FOR ALL USING (auth.uid() = user_id);

-- Team members can view project tasks
CREATE POLICY "Team members can view tasks" ON tasks
    FOR SELECT USING (
        EXISTS (
            SELECT 1 FROM projects p
            WHERE p.id = tasks.project_id
            AND (p.owner_id = auth.uid() OR tasks.assignee_id = auth.uid())
        )
    );
```

### **SQLite Schema** (For local/offline mode)

```sql
-- Save as: schema.sql

-- Same structure as above but with SQLite syntax
-- Key differences:
-- - Use INTEGER PRIMARY KEY AUTOINCREMENT instead of UUID
-- - Use TEXT instead of JSONB
-- - Use TEXT for TIMESTAMP (store ISO format)
-- - No ENCRYPTED keyword (handle encryption in app layer)
-- - No Row Level Security (handle in application)

CREATE TABLE users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    email TEXT UNIQUE NOT NULL,
    name TEXT,
    avatar_url TEXT,
    role TEXT DEFAULT 'user',
    created_at TEXT DEFAULT (datetime('now')),
    last_login TEXT
);

-- ... (similar structure for all tables)
```

### **Database Migration Script**:

```python
# migrations/init_database.py

import os
from supabase import create_client, Client

def init_supabase():
    url = os.getenv('SUPABASE_URL')
    key = os.getenv('SUPABASE_KEY')
    supabase: Client = create_client(url, key)
    
    # Read schema file
    with open('schema.sql', 'r') as f:
        schema = f.read()
    
    # Execute migrations
    supabase.rpc('execute_sql', {'sql': schema}).execute()
    
    print('✅ Database schema created!')

if __name__ == '__main__':
    init_supabase()
```

---

## 6️⃣ **Chat History & Management** ✅ ENHANCED

### **Implementation**:

```javascript
// Add to business-ai-platform.html

// ==================== CHAT MANAGEMENT ====================
class ChatManager {
    constructor() {
        this.currentSessionId = null;
        this.sessions = [];
        this.initChatControls();
    }
    
    initChatControls() {
        // Add hamburger menu button
        this.createHamburgerMenu();
        
        // Load existing sessions
        this.loadSessions();
    }
    
    createHamburgerMenu() {
        const chatHeader = document.querySelector('.ai-chat-header');
        
        const menuHTML = `
            <button class="chat-menu-btn" onclick="chatManager.toggleMenu()">
                <i class="fas fa-bars"></i>
            </button>
            
            <div class="chat-menu-dropdown" id="chat-menu">
                <button class="menu-item" onclick="chatManager.newChat()">
                    <i class="fas fa-plus"></i> New Chat
                </button>
                <button class="menu-item" onclick="chatManager.showHistory()">
                    <i class="fas fa-history"></i> Chat History
                </button>
                <button class="menu-item" onclick="chatManager.saveCurrentChat()">
                    <i class="fas fa-save"></i> Save Chat
                </button>
                <button class="menu-item" onclick="chatManager.exportChat()">
                    <i class="fas fa-download"></i> Export
                </button>
                <div class="menu-divider"></div>
                <button class="menu-item" onclick="chatManager.clearChat()">
                    <i class="fas fa-trash"></i> Clear Chat
                </button>
            </div>
        `;
        
        const menuContainer = document.createElement('div');
        menuContainer.className = 'chat-menu-container';
        menuContainer.innerHTML = menuHTML;
        
        // Insert before title
        chatHeader.insertBefore(menuContainer, chatHeader.firstChild);
    }
    
    toggleMenu() {
        const menu = document.getElementById('chat-menu');
        menu.classList.toggle('active');
    }
    
    async newChat() {
        // Save current chat if has messages
        if (this.currentSessionId && this.hasMessages()) {
            await this.saveCurrentChat();
        }
        
        // Create new session
        const session = await connector.executeTool('supabase_insert', {
            table: 'chat_sessions',
            data: {
                user_id: AppState.userId,
                title: `Chat ${new Date().toLocaleString()}`,
                context_tab: AppState.currentTab
            }
        });
        
        this.currentSessionId = session.data.id;
        
        // Clear messages UI
        document.getElementById('ai-chat-messages').innerHTML = '';
        
        // Add welcome message
        addChatMessage('assistant', '👋 New chat started. How can I help you?');
        
        showNotification('New chat started', 'success');
        this.toggleMenu();
    }
    
    async saveCurrentChat() {
        if (!this.currentSessionId) {
            // Create new session first
            const session = await connector.executeTool('supabase_insert', {
                table: 'chat_sessions',
                data: {
                    user_id: AppState.userId,
                    title: this.generateChatTitle(),
                    context_tab: AppState.currentTab
                }
            });
            this.currentSessionId = session.data.id;
        }
        
        // Get all messages from UI
        const messages = this.getCurrentMessages();
        
        // Save each message
        for (const msg of messages) {
            await connector.executeTool('supabase_insert', {
                table: 'chat_messages',
                data: {
                    session_id: this.currentSessionId,
                    role: msg.role,
                    content: msg.content,
                    created_at: msg.timestamp
                }
            });
        }
        
        showNotification('Chat saved successfully', 'success');
        this.toggleMenu();
    }
    
    async showHistory() {
        // Fetch all sessions
        const sessions = await connector.executeTool('supabase_query', {
            table: 'chat_sessions',
            select: '*',
            filter: { user_id: AppState.userId },
            order: 'created_at.desc',
            limit: 50
        });
        
        // Show history modal
        this.renderHistoryModal(sessions.data);
        this.toggleMenu();
    }
    
    renderHistoryModal(sessions) {
        const modal = document.createElement('div');
        modal.className = 'chat-history-modal';
        modal.innerHTML = `
            <div class="modal-overlay" onclick="this.parentElement.remove()"></div>
            <div class="modal-content">
                <div class="modal-header">
                    <h3><i class="fas fa-history"></i> Chat History</h3>
                    <button onclick="this.closest('.chat-history-modal').remove()">
                        <i class="fas fa-times"></i>
                    </button>
                </div>
                <div class="modal-body">
                    <div class="history-list">
                        ${sessions.map(session => `
                            <div class="history-item" onclick="chatManager.loadSession('${session.id}')">
                                <div class="history-title">${session.title}</div>
                                <div class="history-date">${new Date(session.created_at).toLocaleString()}</div>
                                <div class="history-tab">${session.context_tab}</div>
                            </div>
                        `).join('')}
                    </div>
                </div>
            </div>
        `;
        
        document.body.appendChild(modal);
    }
    
    async loadSession(sessionId) {
        // Fetch messages for session
        const messages = await connector.executeTool('supabase_query', {
            table: 'chat_messages',
            select: '*',
            filter: { session_id: sessionId },
            order: 'created_at.asc'
        });
        
        // Clear current chat
        document.getElementById('ai-chat-messages').innerHTML = '';
        
        // Render messages
        messages.data.forEach(msg => {
            addChatMessage(msg.role, msg.content);
        });
        
        this.currentSessionId = sessionId;
        
        // Close history modal
        document.querySelector('.chat-history-modal').remove();
        
        showNotification('Chat loaded', 'success');
    }
    
    async exportChat() {
        const messages = this.getCurrentMessages();
        
        // Create markdown export
        let markdown = `# Chat Export\n\n`;
        markdown += `**Date**: ${new Date().toLocaleString()}\n\n`;
        markdown += `**Tab**: ${AppState.currentTab}\n\n`;
        markdown += `---\n\n`;
        
        messages.forEach(msg => {
            const role = msg.role === 'user' ? '👤 You' : '🤖 AI Assistant';
            markdown += `### ${role}\n\n`;
            markdown += `${msg.content}\n\n`;
            markdown += `---\n\n`;
        });
        
        // Download file
        const blob = new Blob([markdown], { type: 'text/markdown' });
        const url = URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `chat-${Date.now()}.md`;
        a.click();
        
        showNotification('Chat exported', 'success');
        this.toggleMenu();
    }
    
    clearChat() {
        if (confirm('Clear current chat? This cannot be undone.')) {
            document.getElementById('ai-chat-messages').innerHTML = '';
            this.currentSessionId = null;
            addChatMessage('assistant', '👋 Chat cleared. How can I help you?');
            this.toggleMenu();
        }
    }
    
    getCurrentMessages() {
        const messagesContainer = document.getElementById('ai-chat-messages');
        const messageElements = messagesContainer.querySelectorAll('.ai-message:not(.thinking)');
        
        return Array.from(messageElements).map(el => ({
            role: el.classList.contains('user') ? 'user' : 'assistant',
            content: el.querySelector('.ai-message-content').innerHTML,
            timestamp: new Date().toISOString()
        }));
    }
    
    hasMessages() {
        return this.getCurrentMessages().length > 1; // More than welcome message
    }
    
    generateChatTitle() {
        const messages = this.getCurrentMessages();
        if (messages.length > 0) {
            // Use first user message as title
            const firstUserMsg = messages.find(m => m.role === 'user');
            if (firstUserMsg) {
                return firstUserMsg.content.substring(0, 50) + '...';
            }
        }
        return `Chat ${new Date().toLocaleString()}`;
    }
}

// Initialize on page load
let chatManager;
document.addEventListener('DOMContentLoaded', () => {
    chatManager = new ChatManager();
});
```

### **CSS for Chat Menu**:

```css
/* Add to business-ai-platform.html <style> section */

.chat-menu-container {
    position: relative;
}

.chat-menu-btn {
    background: transparent;
    border: none;
    color: var(--text-secondary);
    cursor: pointer;
    padding: var(--space-2);
    border-radius: 4px;
    transition: all 0.2s ease;
}

.chat-menu-btn:hover {
    background: var(--bg-hover);
    color: var(--text-primary);
}

.chat-menu-dropdown {
    position: absolute;
    top: 100%;
    left: 0;
    background: var(--bg-tertiary);
    border: 1px solid var(--border-default);
    border-radius: 8px;
    min-width: 200px;
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.3);
    display: none;
    z-index: 1000;
    margin-top: var(--space-2);
}

.chat-menu-dropdown.active {
    display: block;
}

.menu-item {
    width: 100%;
    padding: var(--space-3);
    background: transparent;
    border: none;
    color: var(--text-primary);
    cursor: pointer;
    display: flex;
    align-items: center;
    gap: var(--space-2);
    text-align: left;
    transition: all 0.2s ease;
    font-size: 14px;
}

.menu-item:hover {
    background: var(--bg-hover);
}

.menu-item i {
    color: var(--accent-primary);
    width: 16px;
}

.menu-divider {
    height: 1px;
    background: var(--border-default);
    margin: var(--space-2) 0;
}

.chat-history-modal {
    position: fixed;
    top: 0;
    left: 0;
    width: 100%;
    height: 100%;
    z-index: 10002;
    display: flex;
    align-items: center;
    justify-content: center;
}

.modal-overlay {
    position: absolute;
    top: 0;
    left: 0;
    width: 100%;
    height: 100%;
    background: rgba(0, 0, 0, 0.7);
}

.modal-content {
    position: relative;
    background: var(--bg-secondary);
    border: 1px solid var(--border-default);
    border-radius: 12px;
    width: 90%;
    max-width: 600px;
    max-height: 80vh;
    display: flex;
    flex-direction: column;
    box-shadow: 0 8px 32px rgba(0, 0, 0, 0.5);
}

.modal-header {
    padding: var(--space-4);
    border-bottom: 1px solid var(--border-default);
    display: flex;
    align-items: center;
    justify-content: space-between;
}

.modal-body {
    padding: var(--space-4);
    overflow-y: auto;
    flex: 1;
}

.history-list {
    display: flex;
    flex-direction: column;
    gap: var(--space-2);
}

.history-item {
    padding: var(--space-3);
    background: var(--bg-tertiary);
    border: 1px solid var(--border-default);
    border-radius: 6px;
    cursor: pointer;
    transition: all 0.2s ease;
}

.history-item:hover {
    border-color: var(--accent-primary);
    background: var(--bg-hover);
}

.history-title {
    font-weight: 600;
    margin-bottom: var(--space-1);
}

.history-date {
    font-size: 12px;
    color: var(--text-secondary);
}

.history-tab {
    display: inline-block;
    padding: 2px 8px;
    background: var(--accent-primary);
    color: white;
    border-radius: 4px;
    font-size: 11px;
    margin-top: var(--space-2);
}
```

---

## 7️⃣ **Required Libraries Summary**

### **Frontend Libraries**:

```html
<!-- ALREADY INCLUDED -->
<link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
<link href="https://unpkg.com/tabulator-tables@5.5.0/dist/css/tabulator.min.css" rel="stylesheet">
<script src="https://unpkg.com/tabulator-tables@5.5.0/dist/js/tabulator.min.js"></script>
<script src="https://cdn.jsdelivr.net/npm/chart.js@4.4.0/dist/chart.umd.min.js"></script>
<script src="https://cdn.plot.ly/plotly-2.27.0.min.js"></script>
<script src="https://cdn.jsdelivr.net/npm/mermaid@10.6.1/dist/mermaid.min.js"></script>
<script src="https://cdn.jsdelivr.net/npm/marked/marked.min.js"></script>

<!-- NEW - FOR ONLYOFFICE -->
<script src="http://localhost:8000/web-apps/apps/api/documents/api.js"></script>

<!-- NEW - FOR PROJECT MANAGEMENT -->
<link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/jkanban@1.3.1/dist/jkanban.min.css">
<script src="https://cdn.jsdelivr.net/npm/jkanban@1.3.1/dist/jkanban.min.js"></script>
<link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/frappe-gantt@0.6.1/dist/frappe-gantt.css">
<script src="https://cdn.jsdelivr.net/npm/frappe-gantt@0.6.1/dist/frappe-gantt.min.js"></script>
<script src="https://cdn.jsdelivr.net/npm/sortablejs@1.15.0/Sortable.min.js"></script>

<!-- NEW - FOR RICH TEXT EDITING -->
<link href="https://cdn.quilljs.com/1.3.6/quill.snow.css" rel="stylesheet">
<script src="https://cdn.quilljs.com/1.3.6/quill.js"></script>

<!-- NEW - FOR DATE/TIME PICKING -->
<link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/flatpickr/dist/flatpickr.min.css">
<script src="https://cdn.jsdelivr.net/npm/flatpickr"></script>
```

### **Backend Libraries**:

```bash
# Core
pip install flask flask-cors
pip install fastapi uvicorn  # Alternative to Flask
pip install python-dotenv

# Database
pip install psycopg2-binary  # PostgreSQL (Supabase)
pip install supabase  # Supabase Python client

# Workflow/Async
pip install celery redis
pip install schedule  # Cron-like scheduling

# ONLYOFFICE
pip install requests python-magic

# Project Management (if integrating external tools)
pip install python-trello
pip install asana
pip install monday

# AI/NLP (already installed)
pip install openai anthropic google-generativeai
```

### **Infrastructure**:

```bash
# Docker (for ONLYOFFICE)
docker pull onlyoffice/documentserver

# Redis (for Celery/workflows)
docker pull redis

# n8n (optional workflow automation)
docker pull n8nio/n8n
```

---

## 🎯 Implementation Priority

### **Week 1**: Message Popup + Chat Management ✅
- [x] Click messages to expand
- [x] Chat history sidebar
- [x] Save/load chat sessions
- [x] Export chat to markdown

### **Week 2**: Database Setup + Chat Persistence
- [ ] Deploy Supabase instance
- [ ] Run schema migrations
- [ ] Connect frontend to Supabase
- [ ] Test chat save/load

### **Week 3**: Project Management Tab
- [ ] Create Projects tab UI
- [ ] Implement Kanban board (jKanban)
- [ ] Add Gantt chart (Frappe)
- [ ] Task CRUD operations
- [ ] Comments & mentions

### **Week 4**: ONLYOFFICE Integration
- [ ] Deploy ONLYOFFICE Docker container
- [ ] Implement document editor component
- [ ] Add callback handler for saves
- [ ] Integrate with Google Drive storage

### **Week 5**: Automated Workflows
- [ ] Visual workflow builder UI
- [ ] Mermaid diagram rendering
- [ ] Webhook endpoint setup
- [ ] Schedule checker (cron)
- [ ] First workflow: New Order → Slack + Sheets

---

## 📊 Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│  BUSINESS AI PLATFORM - Complete Architecture                  │
│                                                                 │
│  Frontend (HTML/JS/CSS)                                         │
│  ┌──────────┬──────────┬──────────┬──────────┬──────────┐    │
│  │  Tabs    │ AI Chat  │ Projects │ Workflows│Documents │    │
│  │          │ Manager  │ Manager  │ Engine   │ Editor   │    │
│  └──────────┴──────────┴──────────┴──────────┴──────────┘    │
│                           │                                     │
│                           ▼                                     │
│  ┌─────────────────────────────────────────────────────────┐  │
│  │  Backend API (Flask/FastAPI)                            │  │
│  │  - /api/v1/chat/*                                       │  │
│  │  - /api/v1/tools/*                                      │  │
│  │  - /api/v1/projects/*                                   │  │
│  │  - /api/v1/workflows/*                                  │  │
│  │  - /api/v1/documents/*                                  │  │
│  └─────────────────────────────────────────────────────────┘  │
│                           │                                     │
│           ┌───────────────┼───────────────┐                   │
│           ▼               ▼               ▼                    │
│  ┌────────────┐  ┌────────────┐  ┌────────────┐             │
│  │ Supabase   │  │ Tool       │  │ ONLYOFFICE │             │
│  │ PostgreSQL │  │ Registry   │  │ Server     │             │
│  │            │  │ (114 tools)│  │            │             │
│  └────────────┘  └────────────┘  └────────────┘             │
│                           │                                     │
│                           ▼                                     │
│  ┌─────────────────────────────────────────────────────────┐  │
│  │  External Platforms (19)                                │  │
│  │  Slack | WooCommerce | Google Workspace | Stripe ...    │  │
│  └─────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────┘
```

---

**All integrations are now documented! Which component would you like to implement first?** 🚀

Recommended order:
1. ✅ Message popup (DONE)
2. Chat management with database (Week 2)
3. Project management tab (Week 3)
4. ONLYOFFICE documents (Week 4)
5. Automated workflows (Week 5)


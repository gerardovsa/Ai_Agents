# 📚 Required Libraries - Complete Reference

**Quick lookup for all dependencies needed for Business AI Platform**

---

## 🎨 Frontend Libraries

### **Already Included in `business-ai-platform.html`**

| Library | Version | Purpose | CDN Link |
|---------|---------|---------|----------|
| **Font Awesome** | 6.4.0 | Icons | `https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css` |
| **Tabulator** | 5.5.0 | Data tables | `https://unpkg.com/tabulator-tables@5.5.0/dist/js/tabulator.min.js` |
| **Chart.js** | 4.4.0 | Charts | `https://cdn.jsdelivr.net/npm/chart.js@4.4.0/dist/chart.umd.min.js` |
| **Plotly** | 2.27.0 | Advanced viz | `https://cdn.plot.ly/plotly-2.27.0.min.js` |
| **Mermaid** | 10.6.1 | Diagrams | `https://cdn.jsdelivr.net/npm/mermaid@10.6.1/dist/mermaid.min.js` |
| **Marked.js** | Latest | Markdown | `https://cdn.jsdelivr.net/npm/marked/marked.min.js` |
| **Prism.js** | 1.29.0 | Code highlight | `https://cdnjs.cloudflare.com/ajax/libs/prism/1.29.0/prism.min.js` |
| **Luxon** | 3.4.4 | DateTime | `https://cdn.jsdelivr.net/npm/luxon@3.4.4/build/global/luxon.min.js` |

**Total Size**: ~850KB minified

---

### **New Libraries to Add**

#### **For ONLYOFFICE Document Editing**
```html
<!-- Add after DocumentServer is running -->
<script src="http://localhost:8000/web-apps/apps/api/documents/api.js"></script>
```
**Size**: ~200KB  
**Purpose**: Collaborative document editing (Word, Excel, PowerPoint)

---

#### **For Project Management (Kanban + Gantt)**
```html
<!-- jKanban - Kanban board -->
<link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/jkanban@1.3.1/dist/jkanban.min.css">
<script src="https://cdn.jsdelivr.net/npm/jkanban@1.3.1/dist/jkanban.min.js"></script>

<!-- Frappe Gantt - Gantt charts -->
<link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/frappe-gantt@0.6.1/dist/frappe-gantt.css">
<script src="https://cdn.jsdelivr.net/npm/frappe-gantt@0.6.1/dist/frappe-gantt.min.js"></script>

<!-- SortableJS - Drag and drop -->
<script src="https://cdn.jsdelivr.net/npm/sortablejs@1.15.0/Sortable.min.js"></script>
```
**Total Size**: ~120KB minified  
**Purpose**: Kanban boards, Gantt charts, drag-and-drop task management

---

#### **For Rich Text Editing (Task descriptions, comments)**
```html
<!-- Quill - Rich text editor -->
<link href="https://cdn.quilljs.com/1.3.6/quill.snow.css" rel="stylesheet">
<script src="https://cdn.quilljs.com/1.3.6/quill.js"></script>
```
**Size**: ~150KB minified  
**Purpose**: Rich text editing in task descriptions, comments, document notes

---

#### **For Date/Time Picking**
```html
<!-- Flatpickr - Date picker -->
<link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/flatpickr/dist/flatpickr.min.css">
<script src="https://cdn.jsdelivr.net/npm/flatpickr"></script>
```
**Size**: ~40KB minified  
**Purpose**: Date/time selection for tasks, deadlines, calendar events

---

#### **For File Uploads (Drag & Drop)**
```html
<!-- Dropzone.js - File upload -->
<link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/dropzone@5.9.3/dist/min/dropzone.min.css">
<script src="https://cdn.jsdelivr.net/npm/dropzone@5.9.3/dist/min/dropzone.min.js"></script>
```
**Size**: ~50KB minified  
**Purpose**: Drag-and-drop file uploads for documents, attachments

---

#### **For Notifications/Toasts (Enhanced)**
```html
<!-- Toastify - Better notifications -->
<link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/toastify-js/src/toastify.min.css">
<script src="https://cdn.jsdelivr.net/npm/toastify-js"></script>
```
**Size**: ~15KB minified  
**Purpose**: Enhanced toast notifications (already have basic, this is optional upgrade)

---

#### **For Real-time Updates (WebSocket alternative to SSE)**
```html
<!-- Socket.IO - Real-time communication -->
<script src="https://cdn.socket.io/4.5.4/socket.io.min.js"></script>
```
**Size**: ~35KB minified  
**Purpose**: Real-time updates for chat, notifications, collaborative editing

---

### **Complete HTML Head Section**

```html
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Business AI Platform</title>
    
    <!-- ==================== CORE LIBRARIES (ALREADY INCLUDED) ==================== -->
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
    <link href="https://unpkg.com/tabulator-tables@5.5.0/dist/css/tabulator.min.css" rel="stylesheet">
    <script src="https://unpkg.com/tabulator-tables@5.5.0/dist/js/tabulator.min.js"></script>
    <script src="https://cdn.jsdelivr.net/npm/chart.js@4.4.0/dist/chart.umd.min.js"></script>
    <script src="https://cdn.plot.ly/plotly-2.27.0.min.js"></script>
    <script src="https://cdn.jsdelivr.net/npm/mermaid@10.6.1/dist/mermaid.min.js"></script>
    <script src="https://cdn.jsdelivr.net/npm/marked/marked.min.js"></script>
    <link href="https://cdnjs.cloudflare.com/ajax/libs/prism/1.29.0/themes/prism-tomorrow.min.css" rel="stylesheet">
    <script src="https://cdnjs.cloudflare.com/ajax/libs/prism/1.29.0/prism.min.js"></script>
    <script src="https://cdn.jsdelivr.net/npm/luxon@3.4.4/build/global/luxon.min.js"></script>
    
    <!-- ==================== PROJECT MANAGEMENT ==================== -->
    <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/jkanban@1.3.1/dist/jkanban.min.css">
    <script src="https://cdn.jsdelivr.net/npm/jkanban@1.3.1/dist/jkanban.min.js"></script>
    <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/frappe-gantt@0.6.1/dist/frappe-gantt.css">
    <script src="https://cdn.jsdelivr.net/npm/frappe-gantt@0.6.1/dist/frappe-gantt.min.js"></script>
    <script src="https://cdn.jsdelivr.net/npm/sortablejs@1.15.0/Sortable.min.js"></script>
    
    <!-- ==================== RICH TEXT EDITOR ==================== -->
    <link href="https://cdn.quilljs.com/1.3.6/quill.snow.css" rel="stylesheet">
    <script src="https://cdn.quilljs.com/1.3.6/quill.js"></script>
    
    <!-- ==================== DATE PICKER ==================== -->
    <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/flatpickr/dist/flatpickr.min.css">
    <script src="https://cdn.jsdelivr.net/npm/flatpickr"></script>
    
    <!-- ==================== FILE UPLOAD ==================== -->
    <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/dropzone@5.9.3/dist/min/dropzone.min.css">
    <script src="https://cdn.jsdelivr.net/npm/dropzone@5.9.3/dist/min/dropzone.min.js"></script>
    
    <!-- ==================== REAL-TIME (OPTIONAL) ==================== -->
    <script src="https://cdn.socket.io/4.5.4/socket.io.min.js"></script>
    
    <!-- ==================== ONLYOFFICE (Load after server setup) ==================== -->
    <!-- <script src="http://localhost:8000/web-apps/apps/api/documents/api.js"></script> -->
</head>
```

**Total Frontend Size**: ~1.5MB (minified, gzipped: ~450KB)

---

## 🐍 Backend Python Libraries

### **Core Framework**

```bash
# Flask (REST API)
pip install flask==3.0.0
pip install flask-cors==4.0.0
pip install flask-socketio==5.3.5  # For real-time WebSocket

# OR FastAPI (Alternative, more modern)
pip install fastapi==0.104.1
pip install uvicorn[standard]==0.24.0
```

**Choice**:
- **Flask**: Simpler, more mature, good documentation
- **FastAPI**: Faster, auto-generated docs, better async support

**Recommendation**: Start with Flask, migrate to FastAPI later if needed

---

### **Database**

```bash
# Supabase (PostgreSQL cloud)
pip install supabase==2.0.3
pip install psycopg2-binary==2.9.9  # PostgreSQL driver

# SQLite (Local/offline mode)
# Built into Python, no installation needed

# SQLAlchemy (ORM - optional but recommended)
pip install sqlalchemy==2.0.23
```

---

### **AI & Tool Execution**

```bash
# Already installed (from your Tool Registry)
pip install openai==1.3.7
pip install anthropic==0.7.1
pip install google-generativeai==0.3.1

# Streaming responses
pip install sse-starlette==1.8.2  # For Server-Sent Events
```

---

### **Workflow Automation**

```bash
# Celery (async task queue)
pip install celery==5.3.4
pip install redis==5.0.1  # Celery broker

# Schedule (cron-like)
pip install schedule==1.2.0

# APScheduler (advanced scheduling)
pip install apscheduler==3.10.4
```

---

### **ONLYOFFICE Integration**

```bash
pip install requests==2.31.0  # HTTP requests
pip install python-magic==0.4.27  # File type detection
pip install cryptography==41.0.7  # For document encryption
```

---

### **Project Management Integrations (Optional)**

```bash
# Trello
pip install py-trello==0.19.0

# Asana
pip install asana==3.2.2

# Monday.com
pip install monday==1.3.9

# GitHub Projects
pip install PyGithub==2.1.1
```

---

### **File Processing**

```bash
# PDF generation
pip install reportlab==4.0.7
pip install pdfkit==1.0.0

# Excel generation
pip install openpyxl==3.1.2
pip install xlsxwriter==3.1.9

# CSV processing (built-in csv module is usually sufficient)
# But for advanced features:
pip install pandas==2.1.3
```

---

### **Utilities**

```bash
# Environment variables
pip install python-dotenv==1.0.0

# HTTP client (better than requests)
pip install httpx==0.25.2

# Date/time handling
pip install python-dateutil==2.8.2

# JSON Web Tokens (authentication)
pip install pyjwt==2.8.0

# Password hashing
pip install bcrypt==4.1.1
```

---

### **Complete `requirements.txt`**

```txt
# Core Framework
flask==3.0.0
flask-cors==4.0.0
flask-socketio==5.3.5
python-dotenv==1.0.0

# Database
supabase==2.0.3
psycopg2-binary==2.9.9
sqlalchemy==2.0.23

# AI & Streaming
openai==1.3.7
anthropic==0.7.1
google-generativeai==0.3.1
sse-starlette==1.8.2

# Async & Scheduling
celery==5.3.4
redis==5.0.1
schedule==1.2.0
apscheduler==3.10.4

# ONLYOFFICE
requests==2.31.0
python-magic==0.4.27
cryptography==41.0.7

# File Processing
reportlab==4.0.7
openpyxl==3.1.2
xlsxwriter==3.1.9
pandas==2.1.3

# Project Management (Optional)
py-trello==0.19.0
asana==3.2.2
PyGithub==2.1.1

# Utilities
httpx==0.25.2
python-dateutil==2.8.2
pyjwt==2.8.0
bcrypt==4.1.1
```

**Install all**:
```bash
pip install -r requirements.txt
```

---

## 🐳 Docker Containers

### **ONLYOFFICE Document Server**

```bash
# Pull image
docker pull onlyoffice/documentserver

# Run container
docker run -i -t -d -p 8000:80 \
  --name onlyoffice-server \
  -v /app/onlyoffice/logs:/var/log/onlyoffice \
  -v /app/onlyoffice/data:/var/www/onlyoffice/Data \
  onlyoffice/documentserver
```

**Access**: http://localhost:8000

---

### **Redis (for Celery)**

```bash
docker pull redis:7-alpine
docker run -d -p 6379:6379 --name redis redis:7-alpine
```

**Access**: localhost:6379

---

### **PostgreSQL (if not using Supabase cloud)**

```bash
docker pull postgres:15-alpine

docker run -d \
  --name postgres-ai-platform \
  -e POSTGRES_PASSWORD=your_password \
  -e POSTGRES_DB=ai_platform \
  -p 5432:5432 \
  postgres:15-alpine
```

**Access**: localhost:5432

---

### **n8n (Workflow Automation - Optional)**

```bash
docker pull n8nio/n8n

docker run -it --rm \
  --name n8n \
  -p 5678:5678 \
  -v ~/.n8n:/home/node/.n8n \
  n8nio/n8n
```

**Access**: http://localhost:5678

---

### **Docker Compose (All Services)**

```yaml
# docker-compose.yml
version: '3.8'

services:
  # ONLYOFFICE Document Server
  onlyoffice:
    image: onlyoffice/documentserver
    container_name: onlyoffice-server
    ports:
      - "8000:80"
    volumes:
      - ./data/onlyoffice/logs:/var/log/onlyoffice
      - ./data/onlyoffice/data:/var/www/onlyoffice/Data
    restart: unless-stopped

  # Redis (for Celery)
  redis:
    image: redis:7-alpine
    container_name: redis
    ports:
      - "6379:6379"
    restart: unless-stopped

  # PostgreSQL (optional - if not using Supabase)
  postgres:
    image: postgres:15-alpine
    container_name: postgres-ai-platform
    environment:
      POSTGRES_PASSWORD: ${DB_PASSWORD}
      POSTGRES_DB: ai_platform
    ports:
      - "5432:5432"
    volumes:
      - ./data/postgres:/var/lib/postgresql/data
    restart: unless-stopped

  # n8n (optional)
  n8n:
    image: n8nio/n8n
    container_name: n8n
    ports:
      - "5678:5678"
    volumes:
      - ./data/n8n:/home/node/.n8n
    restart: unless-stopped
```

**Start all services**:
```bash
docker-compose up -d
```

---

## 📊 Library Size Comparison

| Category | Libraries | Total Size (Minified) | Gzipped |
|----------|-----------|----------------------|---------|
| **Core (Included)** | Font Awesome, Tabulator, Chart.js, Plotly, Mermaid, Marked, Prism, Luxon | ~850KB | ~280KB |
| **Project Mgmt** | jKanban, Frappe Gantt, SortableJS | ~120KB | ~40KB |
| **Rich Text** | Quill | ~150KB | ~50KB |
| **Date Picker** | Flatpickr | ~40KB | ~15KB |
| **File Upload** | Dropzone | ~50KB | ~20KB |
| **Real-time** | Socket.IO | ~35KB | ~12KB |
| **ONLYOFFICE** | API.js | ~200KB | ~70KB |
| **TOTAL** | All libraries | **~1.45MB** | **~487KB** |

**Page Load Time** (with all libraries): ~2-3 seconds on 3G, <1 second on 4G/WiFi

---

## 🚀 Installation Commands

### **Frontend (No installation needed - all CDN)**
Just add `<script>` and `<link>` tags to HTML

### **Backend Python**
```bash
cd C:\Users\gpoli\GIT\AI_agents
pip install -r requirements.txt
```

### **Docker Services**
```bash
cd C:\Users\gpoli\GIT\AI_agents
docker-compose up -d
```

### **Database Setup**
```bash
# Supabase (cloud)
python migrations/init_database.py

# Or SQLite (local)
python scripts/init_sqlite.py
```

---

## ✅ What's Already Available

From your `AI_agents` folder:
- ✅ Tool Registry (114+ tools)
- ✅ 19 platform integrations
- ✅ Google Workspace tools
- ✅ Supabase client
- ✅ Microsoft 365 client
- ✅ Cloudflare integration
- ✅ Render deployment tools

**You only need to add**:
- Frontend libraries (CDN links - no installation)
- Docker containers (ONLYOFFICE, Redis)
- Flask backend server (new `app.py`)

---

## 📚 Documentation Links

| Library | Documentation | Use Case |
|---------|--------------|----------|
| **jKanban** | [GitHub](https://github.com/riktar/jkanban) | Kanban boards |
| **Frappe Gantt** | [Docs](https://frappe.io/gantt) | Gantt charts |
| **Quill** | [Docs](https://quilljs.com/docs/quickstart/) | Rich text editor |
| **Flatpickr** | [Docs](https://flatpickr.js.org/) | Date/time picker |
| **Dropzone** | [Docs](https://docs.dropzone.dev/) | File uploads |
| **Socket.IO** | [Docs](https://socket.io/docs/v4/) | Real-time communication |
| **ONLYOFFICE** | [API Docs](https://api.onlyoffice.com/editors/basic) | Document editing |

---

**All libraries documented! Ready to implement any feature.** 🎉

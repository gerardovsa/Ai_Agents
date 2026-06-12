# Synergy Files (Docs/Sheets) - Complete Integration Architecture

**Date**: December 9, 2025  
**Analysis Type**: System Integration Architecture  
**Scope**: Synergy Files integration with Sessions, Cards, Thread Info Tags, and UI  
**Methodology**: System Integration Architect (4-Phase Analysis)

---

## 📊 EXECUTIVE SUMMARY

**Synergy Files** (formerly "Internal Documents") are Synergy-native documents stored in the platform database. They come in two types:
- **Synergy Docs** (richtext) - Markdown documents
- **Synergy Sheets** (spreadsheet) - Data tables with formulas

This analysis documents the complete integration architecture across:
1. **Database Layer** - PostgreSQL/Supabase storage (`synergy_internal_docs` table)
2. **Backend API** - Flask REST endpoints in `synergy_routes.py`
3. **Tool Layer** - AI agent tools for creating/managing files
4. **UI Layer** - Modals, pickers, and session card integration
5. **Thread Integration** - Linking files to threads via thread info tags

---

## 🗺️ PHASE 1: SYSTEM LANDSCAPE DISCOVERY

### Systems Inventory (8 Systems)

#### 1. **Database: synergy_internal_docs Table**
- **Type**: PostgreSQL (Supabase) / SQLite (local dev)
- **Schema**: `synergy_sessions.synergy_internal_docs`
- **Access**: Direct via Flask routes
- **Authentication**: Inherits from Synergy session permissions
- **Columns**:
  ```sql
  doc_id VARCHAR(50) PRIMARY KEY
  session_id VARCHAR(100) FOREIGN KEY → synergy_sessions.session_id
  title VARCHAR(255)
  content TEXT
  content_json TEXT
  format VARCHAR(20) DEFAULT 'markdown'
  doc_type VARCHAR(20) DEFAULT 'richtext' -- 'richtext' or 'spreadsheet'
  created_by VARCHAR(100)
  created_at TIMESTAMP
  updated_at TIMESTAMP
  version INTEGER DEFAULT 1
  linked_to_ai BOOLEAN DEFAULT FALSE
  slug VARCHAR(255) UNIQUE
  share_url VARCHAR(500)
  description TEXT
  tags TEXT
  linked_milestone_id VARCHAR(50) -- Can link to specific milestone
  ```

**Indexes**:
```sql
CREATE INDEX idx_session_docs ON synergy_internal_docs(session_id);
CREATE UNIQUE INDEX idx_doc_slug ON synergy_internal_docs(slug);
CREATE INDEX idx_internal_docs_milestone ON synergy_internal_docs(linked_milestone_id);
```

#### 2. **Backend API: synergy_routes.py**
- **File**: `AI_infrastructure/routes/synergy_routes.py`
- **Lines**: 2119-2400 (internal doc routes)
- **Endpoints**:
  ```
  POST   /api/synergy/internal-doc/create
  GET    /api/synergy/internal-doc/<doc_id>
  PUT    /api/synergy/internal-doc/<doc_id>
  DELETE /api/synergy/internal-doc/<doc_id>
  GET    /api/synergy/internal-docs/list
  GET    /api/synergy/internal-doc/list/<session_id>
  ```
- **Features**:
  - Version control (increments on each update)
  - Slug generation (URL-friendly from title)
  - Share URL generation (`/internal-docs/{slug}`)
  - JSON content support (for spreadsheets)

#### 3. **AI Tool: synergy_create_internal_doc**
- **Schema File**: `tools/schemas/synergy_tools.json` (lines 1061-1200)
- **Implementation**: `tools/implementations/synergy.py` (line 2021)
- **Purpose**: AI-callable tool to create Synergy Files
- **Parameters**:
  ```json
  {
    "session_id": "sess_...",      // REQUIRED - which session to attach to
    "title": "Document Title",      // REQUIRED
    "doc_type": "richtext|spreadsheet",  // REQUIRED
    "content": "...",               // Optional initial content
    "description": "...",           // Optional
    "tags": "tag1, tag2"           // Optional
  }
  ```
- **Returns**:
  ```json
  {
    "success": true,
    "doc_id": "int_doc_1733760123456",
    "title": "Document Title",
    "slug": "document-title",
    "share_url": "/internal-docs/document-title",
    "session_id": "sess_...",
    "created_at": "2025-12-09T14:30:00Z"
  }
  ```

#### 4. **AI Tool: synergy_get_internal_doc**
- **Schema File**: `tools/schemas/synergy_tools.json` (lines 1845-1918)
- **Implementation**: `tools/implementations/synergy.py` (line 2191)
- **Purpose**: Retrieve Synergy File content
- **Parameters**:
  ```json
  {
    "doc_id": "int_doc_1733760123456"
  }
  ```
- **Returns**:
  - For richtext: Markdown content
  - For spreadsheet: JSON data structure with rows/columns

#### 5. **AI Tool: synergy_update_internal_doc**
- **Schema File**: `tools/schemas/synergy_tools.json` (lines 1918-2050)
- **Implementation**: `tools/implementations/synergy.py` (line 2132)
- **Purpose**: Update Synergy File content/metadata
- **Features**:
  - Version incrementing
  - Partial updates (can update just title, just content, or both)
  - Timestamp tracking

#### 6. **UI Modal: Synergy Popup (Session Details)**
- **File**: `UI/modules_internal/synergy/synergy-popup-modal.js`
- **Purpose**: Full-screen modal for viewing/editing Synergy sessions
- **Features**:
  - Draggable window
  - Shows session details including linked files
  - Renders file list (delegated to renderer)
- **Opening**: `window.SynergyPopupModal.open(session_id)`

#### 7. **UI Modal: Document Picker**
- **File**: `UI/modules_internal/synergy/synergy-doc-picker.js`
- **Purpose**: Modal for selecting existing Synergy Files to link
- **Features**:
  - Search by title/description
  - Filter by type (richtext/spreadsheet)
  - Filter by date range
  - Sort options
  - Callback on selection
- **Opening**: `window.SynergyDocPicker.open(callback)`

#### 8. **UI Renderer: Session Card**
- **Files**: 
  - `UI/modules_internal/synergy/synergy-sidebar-renderer-v2-FLAT.js` (main renderer)
  - `UI/modules_internal/synergy/synergy-board-init.js` (board management)
- **Purpose**: Renders Synergy session cards with file lists
- **Features**:
  - Shows file count badge
  - Lists files with icons (📄 docs, 📊 sheets)
  - Click to open file modal
  - "Add File" button

---

## 🔗 PHASE 2: INTEGRATION PATTERN ANALYSIS

### Integration 1: AI Tool → Database → API Response

**Pattern**: Request/Response (Synchronous)

**Data Flow**:
```
AI Agent calls synergy_create_internal_doc
    ↓
Python implementation (synergy.py)
    ↓
POST /api/synergy/internal-doc/create
    ↓
Flask route (synergy_routes.py)
    ↓
INSERT INTO synergy_internal_docs
    ↓
Generate doc_id, slug, share_url
    ↓
Return JSON response
    ↓
AI receives doc_id + metadata
```

**Data Transformation**:

```python
# INPUT (AI Tool)
{
    "session_id": "sess_20251209_1430_customer_onboarding",
    "title": "Project Requirements",
    "doc_type": "richtext",
    "content": "# Requirements\n\n- Feature 1\n- Feature 2"
}

# TRANSFORMED (Database)
{
    "doc_id": "int_doc_1733760123456",
    "session_id": "sess_20251209_1430_customer_onboarding",
    "title": "Project Requirements",
    "content": "# Requirements\n\n- Feature 1\n- Feature 2",
    "content_json": null,
    "format": "markdown",
    "doc_type": "richtext",
    "slug": "project-requirements",
    "share_url": "/internal-docs/project-requirements",
    "version": 1,
    "created_at": "2025-12-09T14:30:23Z",
    "updated_at": "2025-12-09T14:30:23Z"
}

# OUTPUT (API Response)
{
    "success": true,
    "doc_id": "int_doc_1733760123456",
    "title": "Project Requirements",
    "slug": "project-requirements",
    "share_url": "/internal-docs/project-requirements",
    "session_id": "sess_20251209_1430_customer_onboarding",
    "created_at": "2025-12-09T14:30:23Z"
}
```

**Error Handling**:
- **Missing session_id**: 400 Bad Request "session_id required"
- **Session not found**: 404 Not Found "Session not found"
- **Duplicate slug**: Auto-append `-1`, `-2`, etc.
- **Database error**: 500 Internal Server Error with error message

**Idempotency**: 
- NOT idempotent (each call creates new doc)
- Use `synergy_get_internal_doc` to check if doc exists first

---

### Integration 2: Session Card → File List Display

**Pattern**: Pull (UI queries API on demand)

**Data Flow**:
```
User opens Synergy session (clicks card)
    ↓
UI calls GET /api/synergy/<session_id>/milestones
    ↓
Backend queries:
    - synergy_sessions (main data)
    - synergy_internal_docs (WHERE session_id = ...)
    - milestones, tasks, subtasks
    ↓
Return combined JSON
    ↓
UI renders session popup with file list
    ↓
Files shown with icons and click handlers
```

**UI Display Pattern**:

```javascript
// Session popup shows files section:
<div class="synergy-files-section">
    <div class="files-header">
        <span>Synergy Files (3)</span>
        <button onclick="addSynergyFile()">+ Add File</button>
    </div>
    <div class="files-list">
        <!-- Synergy Doc -->
        <div class="file-item" onclick="openFile('int_doc_123')">
            <i class="fas fa-file-alt"></i>
            <span>Project Requirements</span>
            <span class="file-type">Doc</span>
        </div>
        
        <!-- Synergy Sheet -->
        <div class="file-item" onclick="openFile('int_doc_456')">
            <i class="fas fa-table"></i>
            <span>Budget Tracking</span>
            <span class="file-type">Sheet</span>
        </div>
        
        <!-- External link (for comparison) -->
        <div class="file-item" onclick="window.open('https://...')">
            <i class="fab fa-google-drive"></i>
            <span>Design Mockups</span>
            <span class="file-type">Google</span>
        </div>
    </div>
</div>
```

**Click Behavior**:
- **Synergy Docs/Sheets**: Open in modal popup (stay in-app)
- **External Links**: Open in new tab

---

### Integration 3: Thread Info Tags → Synergy Files

**Pattern**: Reference Display (metadata only)

**Current Implementation**: ⚠️ **PARTIAL - Files not yet displayed in thread info tags**

**Intended Data Flow**:
```
Thread has synergy_card_id = "sess_abc123"
    ↓
Thread card renders thread info tags
    ↓
Fetches Synergy session metadata:
    GET /api/synergy?ids=sess_abc123
    ↓
Session JSON includes internal_docs array
    ↓
Thread card shows:
    - Synergy badge with session title
    - File count badge (if >0)
    - Click to open Synergy popup
```

**UI Pattern (Thread Card)**:

```javascript
// Thread info row with Synergy badge
<div class="thread-item-synergy">
    <button class="synergy-badge"
            data-session-id="sess_abc123"
            data-file-count="3"
            onclick="openSynergyPopup('sess_abc123')">
        <i class="fas fa-link"></i>
        <span>Customer Onboarding Project</span>
        
        <!-- File count badge -->
        <span class="file-count-badge">3 files</span>
        
        <!-- Priority badge -->
        <span class="priority-badge high">High</span>
    </button>
</div>
```

**Missing Integration**: 
- Thread cards currently show Synergy badge but NOT file count
- Need to add `internal_docs_count` to session metadata
- Need to update thread card renderer to show file badge

---

### Integration 4: Document Picker Modal → Linking

**Pattern**: Event-Driven (Callback on Selection)

**Data Flow**:
```
User clicks "Link Existing File" button
    ↓
UI opens SynergyDocPicker.open(callback)
    ↓
Modal fetches: GET /api/synergy/internal-docs/list
    ↓
Shows searchable/filterable list
    ↓
User selects file
    ↓
Modal calls callback(doc_id, doc_data)
    ↓
Parent component links file to target:
    - Add to milestone.documents array
    - Add to session.documents array
    - Add to thread metadata
    ↓
POST update to API
```

**Example Usage**:

```javascript
// In milestone editor:
function linkFileToMilestone(milestoneId) {
    window.SynergyDocPicker.open((docId, docData) => {
        // Add to milestone
        fetch(`/api/synergy/milestone/${milestoneId}/document/add`, {
            method: 'POST',
            body: JSON.stringify({
                title: docData.title,
                url: `/internal-docs/${docData.slug}`,
                type: 'internal_doc',
                doc_id: docId
            })
        });
    });
}
```

---

### Integration 5: Batch Loading (Sessions with Docs)

**Pattern**: Optimized Batch Query

**Endpoint**: `GET /api/synergy/sessions/batch`

**Purpose**: Load all sessions with internal docs count in ONE query (no N+1 problem)

**SQL Query**:
```sql
-- Step 1: Get all sessions
SELECT * FROM synergy_sessions WHERE status != 'archived';

-- Step 2: Batch load internal docs for ALL sessions
SELECT session_id, COUNT(*) as doc_count
FROM synergy_internal_docs
WHERE session_id IN (sess_1, sess_2, sess_3, ...)
GROUP BY session_id;

-- Step 3: Merge in backend
```

**Response**:
```json
{
    "success": true,
    "sessions": [
        {
            "session_id": "sess_abc123",
            "title": "Customer Onboarding",
            "internal_docs_count": 5,
            "internal_docs": [
                {"doc_id": "...", "title": "Requirements", "type": "richtext"},
                {"doc_id": "...", "title": "Budget", "type": "spreadsheet"},
                ...
            ]
        }
    ]
}
```

**Performance**: Single query for all sessions (vs N separate queries)

---

## ⚠️ PHASE 3: GAP ANALYSIS - INTEGRATION ISSUES

### Gap 1: Thread Info Tags Don't Show File Count

**Issue**: Thread cards show Synergy badge but not how many files are in the session

**Impact**: User can't tell at a glance if session has documents

**Current Behavior**:
```html
<div class="synergy-badge">
    <i class="fas fa-link"></i>
    <span>Customer Onboarding Project</span>
    <!-- Missing file count -->
</div>
```

**Desired Behavior**:
```html
<div class="synergy-badge">
    <i class="fas fa-link"></i>
    <span>Customer Onboarding Project</span>
    <span class="file-badge">5 files</span>  <!-- NEW -->
</div>
```

**Fix Required**:
1. Update `GET /api/synergy?ids=...` to include `internal_docs_count`
2. Update thread card renderer to show file badge
3. Add CSS for `.file-badge` styling

**Files to Modify**:
- `AI_infrastructure/routes/synergy_routes.py` (bulk session query)
- `UI/modules_internal/thread-cards/thread-card-templates.js` (_synergyRow method)
- `UI/modules_internal/thread-cards/thread-card-styles.css` (new `.file-badge` class)

---

### Gap 2: No Direct "Open File" Link from Thread Card

**Issue**: To access Synergy File from thread, must:
1. Click Synergy badge → Opens session popup
2. Find file in list → Click file
3. File opens in modal

**Impact**: 3 clicks to access file

**Desired Flow**: 
- Show file list dropdown on hover
- Click file directly from thread card

**Proposed UI**:
```html
<div class="synergy-badge-with-dropdown">
    <button class="synergy-badge">
        <i class="fas fa-link"></i>
        <span>Customer Onboarding</span>
        <span class="file-badge">5 files</span>
    </button>
    
    <!-- Dropdown on hover -->
    <div class="files-dropdown">
        <div class="file-item" onclick="openFile('doc_123')">
            <i class="fas fa-file-alt"></i> Requirements
        </div>
        <div class="file-item" onclick="openFile('doc_456')">
            <i class="fas fa-table"></i> Budget
        </div>
        <div class="divider"></div>
        <button onclick="openSession('sess_abc')">
            View All Files →
        </button>
    </div>
</div>
```

**Implementation**:
1. Fetch file list when badge hovered (or on initial load)
2. Cache in ThreadManager.synergyFilesCache
3. Render dropdown with file links
4. CSS for hover dropdown positioning

---

### Gap 3: Synergy Files Not Searchable Globally

**Issue**: Can only find files by:
- Browsing session they're in
- Using doc picker modal (limited to one session context)

**Missing**: Global search for "Find all docs with keyword X"

**Desired Feature**:
```
Search Bar: "Find in Synergy Files..."
    ↓
GET /api/synergy/internal-docs/search?q=budget&type=spreadsheet
    ↓
Results:
    - Budget Q1 2025 (in Customer Onboarding)
    - Budget Q2 2025 (in Product Launch)
    - Annual Budget (in Finance Planning)
```

**API Endpoint Needed**:
```python
@synergy_bp.route('/internal-docs/search', methods=['GET'])
def search_internal_docs():
    query = request.args.get('q', '')
    doc_type = request.args.get('type')  # Optional filter
    
    sql = '''
        SELECT d.doc_id, d.title, d.doc_type, d.created_at,
               s.session_id, s.title as session_title
        FROM synergy_internal_docs d
        JOIN synergy_sessions s ON d.session_id = s.session_id
        WHERE (d.title LIKE %s OR d.content LIKE %s OR d.description LIKE %s)
        AND (d.doc_type = %s OR %s IS NULL)
        ORDER BY d.updated_at DESC
        LIMIT 50
    '''
    # Execute query...
```

---

### Gap 4: No File List in Session Batch Response

**Issue**: `GET /api/synergy/sessions/batch` returns `internal_docs_count` but NOT the actual file list

**Impact**: UI must make separate request for each session's files

**Current Response**:
```json
{
    "session_id": "sess_abc",
    "internal_docs_count": 5,
    "internal_docs": []  // Empty! Must fetch separately
}
```

**Desired Response**:
```json
{
    "session_id": "sess_abc",
    "internal_docs_count": 5,
    "internal_docs": [
        {
            "doc_id": "int_doc_123",
            "title": "Requirements",
            "doc_type": "richtext",
            "slug": "requirements",
            "updated_at": "2025-12-09T10:00:00Z"
        },
        // ... all 5 files
    ]
}
```

**Fix**: Update batch query in `synergy_routes.py` lines 574-620 to include full file objects

---

### Gap 5: Orphaned Code - Smart Internal Doc Tool Not Used

**Found**: `tools/implementations/synergy_smart_internal_doc.py` (1111 lines)

**Purpose**: AI-powered document creation with templates

**Issue**: This file exists but is NOT registered in tool schemas

**Templates Available**:
- Meeting notes
- Project plan
- Technical spec
- API documentation
- Troubleshooting guide
- Release notes

**Status**: ⚠️ **ORPHANED** - Code exists but unreachable by AI agents

**Decision Needed**:
1. **Option A**: Register these tools in `synergy_tools.json`
2. **Option B**: Merge functionality into main `synergy_create_internal_doc`
3. **Option C**: Archive if no longer needed

---

### Gap 6: No Version History Viewer

**Issue**: Files have `version` field that increments on each edit, but:
- No way to view previous versions
- No diff view between versions
- No rollback capability

**Impact**: User edits file → Accidentally deletes content → Can't undo

**Database Structure**:
```sql
-- Current (single version)
synergy_internal_docs:
    doc_id, content, version (INTEGER)

-- Needed (version history)
synergy_internal_docs_history:
    history_id, doc_id, version, content, changed_by, changed_at
```

**UI Needed**:
```
[File Header]
    Requirements.md (v5)
    [View History ▼]
        ↓
    Version History:
        v5 - Dec 9, 14:30 - AI Agent - "Added section 3"
        v4 - Dec 9, 10:15 - John Smith - "Updated requirements"
        v3 - Dec 8, 16:00 - AI Agent - "Initial draft"
        
    [Compare] [Restore]
```

---

### Gap 7: Files Not Linked to Specific Milestones

**Issue**: File can be linked to session, but not to specific milestone within session

**Current**: 
- File → Session (one-to-many)

**Desired**:
- File → Session → Milestone (many-to-one-to-one)

**Use Case**: 
- Session: "Customer Onboarding System"
  - Milestone 1: "Design Phase" → Requirements Doc, Wireframes
  - Milestone 2: "Development Phase" → API Spec, Test Plan
  - Milestone 3: "Launch Phase" → Launch Checklist

**Database Column Exists**: `linked_milestone_id VARCHAR(50)`

**Missing**: UI to link file to milestone during creation/editing

**Fix**: Add milestone picker to file creation modal

---

### Gap 8: No Inline File Preview in Session Popup

**Issue**: Must click file → Opens separate modal → View content

**Desired**: Show file preview inline in session popup

**UI Pattern**:
```html
<div class="synergy-files-section">
    <!-- File List -->
    <div class="file-item selected">
        <i class="fas fa-file-alt"></i>
        <span>Requirements</span>
    </div>
    
    <!-- PREVIEW PANE (NEW) -->
    <div class="file-preview-pane">
        <h3>Requirements.md</h3>
        <div class="preview-content">
            # Project Requirements
            
            ## Features
            - Feature 1
            - Feature 2
            
            ## Timeline
            ...
        </div>
        <button onclick="openFullEditor()">Edit Full Document</button>
    </div>
</div>
```

**Implementation**: Load file content via AJAX when file selected

---

## 📋 PHASE 4: INTEGRATION ARCHITECTURE DOCUMENT

### Complete Integration Map

```
┌─────────────────────────────────────────────────────────────┐
│                      AI AGENT LAYER                         │
│  synergy_create_internal_doc                                │
│  synergy_get_internal_doc                                   │
│  synergy_update_internal_doc                                │
└──────────────────────┬──────────────────────────────────────┘
                       │ HTTP POST/GET/PUT
                       ↓
┌─────────────────────────────────────────────────────────────┐
│                      API LAYER (Flask)                      │
│  POST   /api/synergy/internal-doc/create                    │
│  GET    /api/synergy/internal-doc/<doc_id>                  │
│  PUT    /api/synergy/internal-doc/<doc_id>                  │
│  DELETE /api/synergy/internal-doc/<doc_id>                  │
│  GET    /api/synergy/internal-docs/list                     │
│  GET    /api/synergy/sessions/batch (includes docs)         │
└──────────────────────┬──────────────────────────────────────┘
                       │ SQL Queries
                       ↓
┌─────────────────────────────────────────────────────────────┐
│                   DATABASE LAYER                            │
│  synergy_sessions.synergy_internal_docs                     │
│    - doc_id (PK)                                            │
│    - session_id (FK → synergy_sessions)                     │
│    - title, content, content_json                           │
│    - doc_type, version, slug, share_url                     │
│    - linked_milestone_id (FK → milestones)                  │
└──────────────────────┬──────────────────────────────────────┘
                       │ Query Results
                       ↓
┌─────────────────────────────────────────────────────────────┐
│                      UI LAYER                               │
│  ┌──────────────────────────────────────────────┐           │
│  │ Synergy Session Popup                        │           │
│  │   - Draggable window                         │           │
│  │   - File list with icons                     │           │
│  │   - "Add File" button                        │           │
│  └──────────────────────────────────────────────┘           │
│                                                              │
│  ┌──────────────────────────────────────────────┐           │
│  │ Document Picker Modal                        │           │
│  │   - Search/filter files                      │           │
│  │   - Callback on selection                    │           │
│  └──────────────────────────────────────────────┘           │
│                                                              │
│  ┌──────────────────────────────────────────────┐           │
│  │ Thread Info Card                             │           │
│  │   - Synergy badge with session name          │           │
│  │   - File count badge ⚠️ MISSING              │           │
│  │   - Click to open session popup              │           │
│  └──────────────────────────────────────────────┘           │
└─────────────────────────────────────────────────────────────┘
```

### Data Flow: Create File → Display in Thread

```
STEP 1: AI Agent Creates File
    AI: synergy_create_internal_doc(
        session_id="sess_abc123",
        title="Requirements",
        doc_type="richtext",
        content="# Requirements\n..."
    )
    ↓
    Implementation: POST /api/synergy/internal-doc/create
    ↓
    Database: INSERT INTO synergy_internal_docs
    ↓
    Response: {"doc_id": "int_doc_456", "slug": "requirements", ...}
    ↓
    AI: Receives doc_id and can reference later

STEP 2: Session Card Updates
    Backend: File count updated in synergy_sessions metadata
    (via batch query or cached count)
    ↓
    UI: Session card shows updated file count badge
    (requires Gap 1 fix)

STEP 3: Thread Card Shows File
    Thread with synergy_card_id = "sess_abc123"
    ↓
    Thread card fetches session metadata:
        GET /api/synergy?ids=sess_abc123
    ↓
    Response includes: internal_docs_count: 1
    (requires Gap 4 fix for full file list)
    ↓
    Thread card renders Synergy badge with file count
    ↓
    User clicks badge → Opens session popup
    ↓
    Popup shows file list with "Requirements" file
    ↓
    User clicks file → Opens file editor modal

STEP 4: User Edits File
    UI: PUT /api/synergy/internal-doc/int_doc_456
        {"content": "# Requirements\n\n## Updated"}
    ↓
    Backend: version++, updated_at = NOW()
    ↓
    UI: File list shows "(edited just now)"
```

---

## 🔧 RECOMMENDATIONS

### Priority 1 (High Impact, Low Effort)

**1. Add File Count to Thread Info Badges**
- **Gap**: #1
- **Effort**: 2 hours
- **Impact**: High (immediate visibility)
- **Files**: 
  - `synergy_routes.py` (add count to batch query)
  - `thread-card-templates.js` (show badge)

**2. Include Full File List in Batch Response**
- **Gap**: #4
- **Effort**: 3 hours
- **Impact**: High (eliminates N+1 queries)
- **Files**: `synergy_routes.py` lines 574-620

**3. Add Global File Search Endpoint**
- **Gap**: #3
- **Effort**: 4 hours
- **Impact**: Medium (discoverability)
- **Files**: `synergy_routes.py` (new route)

### Priority 2 (Medium Impact, Medium Effort)

**4. File Dropdown on Thread Badge Hover**
- **Gap**: #2
- **Effort**: 8 hours
- **Impact**: Medium (UX improvement)
- **Files**: 
  - `thread-card-templates.js`
  - `thread-card-styles.css`
  - Add caching in `thread_manager.js`

**5. Milestone-Specific File Linking**
- **Gap**: #7
- **Effort**: 6 hours
- **Impact**: Medium (better organization)
- **Files**:
  - UI modal for milestone picker
  - Update create/update API calls

### Priority 3 (High Impact, High Effort)

**6. Version History Viewer**
- **Gap**: #6
- **Effort**: 16+ hours
- **Impact**: High (safety feature)
- **Implementation**:
  - New table: `synergy_internal_docs_history`
  - Trigger on UPDATE to store old version
  - UI for viewing/comparing/restoring

**7. Inline File Preview**
- **Gap**: #8
- **Effort**: 12 hours
- **Impact**: Medium (UX enhancement)
- **Implementation**:
  - Add preview pane to session popup
  - Lazy load content on file selection
  - Syntax highlighting for markdown

### Priority 4 (Low Priority / Needs Decision)

**8. Register Smart Document Tools**
- **Gap**: #5
- **Effort**: 4 hours (if registering) OR 1 hour (if archiving)
- **Impact**: Low (alternative creation method)
- **Decision Needed**: Keep vs Remove orphaned code

---

## 📊 SUCCESS METRICS

After implementing fixes:

**Metric 1: Thread Card Integration**
- ✅ Thread cards show file count badge
- ✅ File count matches actual docs in session
- ✅ Badge updates when files added/removed

**Metric 2: Performance**
- ✅ Session batch load <500ms (for 50 sessions)
- ✅ File search <200ms (for 1000+ files)
- ✅ No N+1 query problems

**Metric 3: Usability**
- ✅ User can find file in <3 clicks from thread card
- ✅ File search returns relevant results
- ✅ Version history accessible

**Metric 4: Data Integrity**
- ✅ Files always linked to valid session
- ✅ Slug uniqueness enforced
- ✅ Version incrementing works correctly

---

## 🚀 ROLLOUT PLAN

### Phase A: Quick Wins (Week 1)
1. Add file count to thread badges
2. Include files in batch response
3. Test integration

### Phase B: Search & Discovery (Week 2)
1. Add global file search API
2. Update UI search bar
3. Add search to doc picker modal

### Phase C: UX Enhancements (Week 3-4)
1. File dropdown on hover
2. Milestone linking UI
3. Inline preview pane

### Phase D: Advanced Features (Week 5+)
1. Version history table
2. History viewer UI
3. Diff & restore capabilities

---

## 📚 RELATED DOCUMENTATION

- `SYNERGY_FILES_REBRANDING_DEC8_2025.md` - Terminology changes
- `SYNERGY_TOOLS_UPDATE_SUMMARY_DEC8_2025.md` - Tool schema updates
- `SYNERGY_TOOL_GUIDE_QUICK_REFERENCE.md` - Tool selection guide
- `INTERNAL_DOCUMENT_MODULE.md` - Original implementation docs
- `SYNERGY_DOCUMENT_PICKER_COMPLETE.md` - Picker modal specs

---

**Status**: ✅ ANALYSIS COMPLETE  
**Next Action**: Review recommendations with team → Prioritize fixes → Begin implementation

This integration architecture provides a complete map of how Synergy Files integrate across the platform, identifies 8 critical gaps, and provides actionable recommendations with effort estimates.

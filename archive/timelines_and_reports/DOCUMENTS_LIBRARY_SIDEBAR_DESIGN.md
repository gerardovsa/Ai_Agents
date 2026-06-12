# 📚 Documents Library Sidebar - Complete Design Specification
## December 10, 2025

---

## 🎯 Overview

**The Documents Library Sidebar** is a comprehensive document management center that brings together ALL Synergy Internal Documents and Thread Files into a single, powerful interface. Think of it as a "Mission Control" for all documents created within the AI platform.

### Key Philosophy
- **Centralized Access**: One place to find every document, regardless of where it was created
- **Multi-Context Awareness**: Documents can be linked to Synergy sessions, threads, users, projects
- **Power User Features**: Advanced search, filtering, bulk operations, analytics
- **Quick Actions**: Create, edit, share, export without leaving the sidebar

---

## 📊 Current State Analysis

### Existing Infrastructure
**Database: `synergy_sessions.synergy_internal_docs`**
```sql
CREATE TABLE synergy_internal_docs (
    doc_id TEXT PRIMARY KEY,
    session_id TEXT,              -- Linked Synergy session
    title TEXT,
    doc_type TEXT,                -- 'richtext' or 'spreadsheet'
    version INTEGER,
    slug TEXT,
    content TEXT,                 -- JSON for richtext, array for spreadsheet
    created_by TEXT,
    created_at TIMESTAMP,
    updated_at TIMESTAMP,
    last_edited_by TEXT,
    tags TEXT,                    -- JSON array
    visibility TEXT,              -- 'private', 'team', 'public'
    share_url TEXT,
    metadata JSONB                -- Custom fields
);
```

**Existing APIs:**
- ✅ `/api/synergy/internal-docs/search?q={query}` - Global search
- ✅ `/api/synergy/internal-docs/recent?limit=50` - Recent docs
- ✅ `/api/synergy/sessions/batch` - Returns internal_docs array per session
- ✅ `/api/synergy/internal-docs` (POST) - Create document
- ✅ `/api/synergy/internal-docs/{doc_id}` (GET/PUT/DELETE)
- ✅ `/api/document-library/search/fulltext` - Advanced search
- ✅ Document preview modal (`thread-file-preview.js`)

**Existing Components:**
- ✅ `InternalDocsManager` - Document CRUD operations
- ✅ File count badges in thread cards
- ✅ Documents section in Synergy sidebar
- ✅ File preview modal
- ✅ Search endpoints with proper cursor management

### What's Missing (The Gap This Sidebar Fills)
1. ❌ **No centralized library view** - Documents scattered across sessions
2. ❌ **No advanced filtering** - Can't filter by type, date range, tags, visibility
3. ❌ **No bulk operations** - Can't export, delete, or reassign multiple docs
4. ❌ **No analytics dashboard** - Don't know usage patterns, popular docs
5. ❌ **No orphan management** - Can't find documents not linked to sessions
6. ❌ **No version history viewer** - Can't see document evolution
7. ❌ **No collaboration features** - Can't see who's editing what
8. ❌ **No workspace organization** - Can't group docs by project/team

---

## 🎨 Sidebar Design Specifications

### Sidebar Layout (Right Side, 750px width)

```
┌─────────────────────────────────────────────────────┐
│ 📚 Documents Library              [⚙️] [✕]          │
├─────────────────────────────────────────────────────┤
│                                                     │
│ ┌─────────────────────────────────────────────┐   │
│ │ 🔍 Search documents...            [⊕ New ▾] │   │
│ └─────────────────────────────────────────────┘   │
│                                                     │
│ ┌─── Quick Stats ─────────────────────────────┐   │
│ │ 📄 245 Total  |  📝 189 Rich  |  📊 56 Sheets│   │
│ │ 🔗 198 Linked |  🎯 47 Orphaned              │   │
│ └────────────────────────────────────────────────┘   │
│                                                     │
│ ┌─── Views & Filters ──────────────────────────┐   │
│ │ 📋 All Documents        (245)               │   │
│ │ ⭐ Starred              (12)                │   │
│ │ 📅 Recent               (50)                │   │
│ │ 🎯 Synergy Linked       (198)               │   │
│ │ 💬 Thread Linked        (34)                │   │
│ │ 🚫 Orphaned             (47)                │   │
│ │ 👤 Created by Me        (89)                │   │
│ │ 🌐 Shared               (23)                │   │
│ │ 🗑️ Recently Deleted     (5)                 │   │
│ └────────────────────────────────────────────────┘   │
│                                                     │
│ ┌─── Advanced Filters ─────────────────────────┐   │
│ │ Type: [All ▾] [Rich ▾] [Sheet ▾]           │   │
│ │ Date: [Last 7 days ▾]                       │   │
│ │ Tags: [marketing] [x] [urgent] [x]          │   │
│ │ Visibility: [All ▾] [Private ▾] [Team ▾]   │   │
│ │ Session: [Select session... ▾]              │   │
│ │                        [Clear All Filters]   │   │
│ └────────────────────────────────────────────────┘   │
│                                                     │
│ ┌─── Document List (Scrollable) ───────────────┐   │
│ │                                               │   │
│ │ ┌───────────────────────────────────────┐    │   │
│ │ │ [☐] 📝 Q4 Marketing Strategy         │    │   │
│ │ │     🔗 Synergy: Marketing 2025        │    │   │
│ │ │     👤 John Doe • ⏰ 2 hours ago      │    │   │
│ │ │     🏷️ marketing, strategy            │    │   │
│ │ │     [👁️] [✏️] [📤] [⋮]                 │    │   │
│ │ └───────────────────────────────────────┘    │   │
│ │                                               │   │
│ │ ┌───────────────────────────────────────┐    │   │
│ │ │ [☐] 📊 Sales Data December            │    │   │
│ │ │     🔗 Synergy: Sales Review          │    │   │
│ │ │     👤 Jane Smith • ⏰ Yesterday       │    │   │
│ │ │     🏷️ sales, reports                 │    │   │
│ │ │     [👁️] [✏️] [📤] [⋮]                 │    │   │
│ │ └───────────────────────────────────────┘    │   │
│ │                                               │   │
│ │ ┌───────────────────────────────────────┐    │   │
│ │ │ [☐] 📝 Client Feedback Analysis       │    │   │
│ │ │     🚫 Not linked to any session      │    │   │
│ │ │     👤 You • ⏰ 3 days ago             │    │   │
│ │ │     🏷️ feedback, clients              │    │   │
│ │ │     [👁️] [✏️] [🔗] [⋮]                 │    │   │
│ │ └───────────────────────────────────────┘    │   │
│ │                                               │   │
│ │         ... (paginated, 50 per page)          │   │
│ │                                               │   │
│ └──────────────────────────────────────────────┘   │
│                                                     │
│ ┌─── Bulk Actions Bar (when items selected) ──┐   │
│ │ ✓ 3 selected                                 │   │
│ │ [📤 Export] [🔗 Link] [🏷️ Tag] [🗑️ Delete]  │   │
│ └────────────────────────────────────────────────┘   │
│                                                     │
│ ┌─── Footer ───────────────────────────────────┐   │
│ │ Showing 1-50 of 245 | [◀️ Prev] [Next ▶️]    │   │
│ └────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────┘
```

---

## 🔧 Feature Specifications

### 1. **Header Section**

#### Search Bar
```javascript
// Global search with autocomplete
<input 
    type="text" 
    placeholder="🔍 Search documents by title, content, tags..."
    class="doc-library-search"
    data-autocomplete="true"
/>

// Search capabilities:
- Title search (fuzzy)
- Full-text content search (PostgreSQL ts_vector)
- Tag search (#marketing)
- Creator search (@johndoe)
- Session search (synergy:marketing-2025)
- Date range (created:2025-12-01..2025-12-10)
```

#### New Document Dropdown
```javascript
[⊕ New ▾]
  ├─ 📝 Rich Text Document
  ├─ 📊 Spreadsheet
  ├─ 📋 Template
  │   ├─ Meeting Notes
  │   ├─ Project Brief
  │   ├─ Status Report
  │   └─ Financial Spreadsheet
  └─ 📁 Bulk Import (CSV/JSON)
```

### 2. **Quick Stats Dashboard**
```javascript
{
    totalDocuments: 245,
    richTextCount: 189,
    spreadsheetCount: 56,
    linkedToSynergy: 198,
    linkedToThreads: 34,
    orphaned: 47,
    sharedPublicly: 23,
    storageUsed: "45.2 MB",
    avgDocSize: "189 KB",
    mostActiveSession: "Marketing 2025 (34 docs)"
}
```

### 3. **Smart Views (Preset Filters)**

#### All Documents
- Default view showing all accessible documents
- Sorted by `updated_at DESC`

#### Starred (Favorites)
- User-specific starred documents
- Stored in `user_preferences.starred_docs`

#### Recent
- Documents updated in last 7 days
- Real-time updates

#### Synergy Linked
- Documents with `session_id NOT NULL`
- Shows which session they belong to
- Grouped by session option

#### Thread Linked
- Documents mentioned in thread messages
- Cross-reference with thread attachment metadata

#### Orphaned Documents
- Documents with `session_id IS NULL AND thread_id IS NULL`
- Priority: Help users link or archive these

#### Created by Me
- Filter by `created_by = current_user.username`

#### Shared
- Documents with `visibility IN ('team', 'public')`
- Shows share URLs and access stats

#### Recently Deleted
- Soft-deleted documents (30-day retention)
- Can restore or permanently delete

### 4. **Advanced Filters**

```javascript
const filters = {
    // Document Type
    docType: ['all', 'richtext', 'spreadsheet'],
    
    // Date Ranges
    dateRange: {
        last7days: moment().subtract(7, 'days'),
        last30days: moment().subtract(30, 'days'),
        last90days: moment().subtract(90, 'days'),
        thisYear: moment().startOf('year'),
        custom: { start: Date, end: Date }
    },
    
    // Tags (multi-select)
    tags: ['marketing', 'urgent', 'draft', 'final', 'review'],
    
    // Visibility
    visibility: ['all', 'private', 'team', 'public'],
    
    // Synergy Session (dropdown with search)
    sessionId: 'session_xxx',
    
    // Creator (multi-select)
    createdBy: ['john@example.com', 'jane@example.com'],
    
    // Version
    version: { min: 1, max: 10 },
    
    // Content Size
    sizeRange: { min: '0 KB', max: '10 MB' }
};
```

### 5. **Document Card Design**

```html
<div class="doc-library-card" data-doc-id="{doc_id}">
    <!-- Selection Checkbox -->
    <input type="checkbox" class="doc-select" />
    
    <!-- Document Icon (type-based) -->
    <div class="doc-icon">
        📝 <!-- Rich text -->
        📊 <!-- Spreadsheet -->
    </div>
    
    <!-- Document Info -->
    <div class="doc-info">
        <h4 class="doc-title">Q4 Marketing Strategy</h4>
        
        <!-- Context Links -->
        <div class="doc-context">
            <span class="context-badge synergy">
                🔗 Synergy: <a href="#session">Marketing 2025</a>
            </span>
            <!-- OR -->
            <span class="context-badge thread">
                💬 Thread: <a href="#thread">Client Discussion</a>
            </span>
            <!-- OR -->
            <span class="context-badge orphan">
                🚫 Not linked to any session
            </span>
        </div>
        
        <!-- Metadata -->
        <div class="doc-meta">
            <span class="creator">👤 John Doe</span>
            <span class="timestamp">⏰ 2 hours ago</span>
            <span class="version">v3</span>
            <span class="size">245 KB</span>
        </div>
        
        <!-- Tags -->
        <div class="doc-tags">
            <span class="tag">🏷️ marketing</span>
            <span class="tag">🏷️ strategy</span>
            <span class="tag">🏷️ q4</span>
        </div>
    </div>
    
    <!-- Quick Actions -->
    <div class="doc-actions">
        <button class="action-btn" title="View" onclick="viewDocument()">
            👁️
        </button>
        <button class="action-btn" title="Edit" onclick="editDocument()">
            ✏️
        </button>
        <button class="action-btn" title="Share" onclick="shareDocument()">
            📤
        </button>
        <button class="action-btn" title="More" onclick="showContextMenu()">
            ⋮
        </button>
    </div>
</div>
```

### 6. **Context Menu (⋮ More Actions)**

```javascript
const contextMenuActions = [
    { icon: '👁️', label: 'View', action: 'view' },
    { icon: '✏️', label: 'Edit', action: 'edit' },
    { icon: '📤', label: 'Share', action: 'share' },
    { icon: '🔗', label: 'Link to Synergy Session', action: 'linkSynergy' },
    { icon: '💬', label: 'Link to Thread', action: 'linkThread' },
    { icon: '📥', label: 'Download', submenu: [
        { label: 'As JSON', action: 'downloadJSON' },
        { label: 'As Markdown', action: 'downloadMD' },
        { label: 'As PDF', action: 'downloadPDF' },
        { label: 'As HTML', action: 'downloadHTML' }
    ]},
    { icon: '📋', label: 'Duplicate', action: 'duplicate' },
    { icon: '🏷️', label: 'Edit Tags', action: 'editTags' },
    { icon: '👥', label: 'Manage Access', action: 'manageAccess' },
    { icon: '📊', label: 'View Analytics', action: 'analytics' },
    { icon: '🕐', label: 'Version History', action: 'versionHistory' },
    { icon: '⭐', label: 'Star/Unstar', action: 'toggleStar' },
    { icon: '🔒', label: 'Change Visibility', submenu: [
        { label: 'Private', value: 'private' },
        { label: 'Team', value: 'team' },
        { label: 'Public', value: 'public' }
    ]},
    { icon: '🗑️', label: 'Delete', action: 'delete', destructive: true }
];
```

### 7. **Bulk Operations**

When multiple documents are selected:

```html
<div class="bulk-actions-bar">
    <div class="selection-count">
        ✓ <span id="selectedCount">3</span> selected
        <button onclick="selectAll()">Select All</button>
        <button onclick="deselectAll()">Clear</button>
    </div>
    
    <div class="bulk-action-buttons">
        <button class="bulk-btn" onclick="bulkExport()">
            📤 Export Selected
        </button>
        <button class="bulk-btn" onclick="bulkLink()">
            🔗 Link to Session
        </button>
        <button class="bulk-btn" onclick="bulkTag()">
            🏷️ Add Tags
        </button>
        <button class="bulk-btn" onclick="bulkVisibility()">
            🔒 Change Visibility
        </button>
        <button class="bulk-btn" onclick="bulkMove()">
            📁 Move to Session
        </button>
        <button class="bulk-btn destructive" onclick="bulkDelete()">
            🗑️ Delete Selected
        </button>
    </div>
</div>
```

**Bulk Export Options:**
- ZIP of all selected documents (JSON format)
- Combined PDF (all docs in one file)
- CSV metadata export
- Excel workbook (one sheet per doc)

---

## 🚀 Advanced Features

### 1. **Document Analytics Dashboard**

Click "View Analytics" on any document:

```
┌─── Document Analytics ─────────────────────────┐
│                                                │
│  📊 Q4 Marketing Strategy                     │
│  Created: Dec 1, 2025 by John Doe             │
│  Last updated: 2 hours ago                    │
│                                                │
│  ┌─── Usage Stats ─────────────────────────┐  │
│  │ 👁️ 127 views                            │  │
│  │ ✏️ 34 edits                              │  │
│  │ 👥 5 unique collaborators                │  │
│  │ 📤 12 shares                              │  │
│  │ ⏱️ Avg edit time: 15 minutes              │  │
│  └──────────────────────────────────────────┘  │
│                                                │
│  ┌─── Activity Timeline ────────────────────┐  │
│  │ [Line chart showing views/edits over time]│  │
│  └──────────────────────────────────────────┘  │
│                                                │
│  ┌─── Collaborators ────────────────────────┐  │
│  │ 👤 John Doe (Creator) - 18 edits         │  │
│  │ 👤 Jane Smith - 9 edits                  │  │
│  │ 👤 Bob Johnson - 5 edits                 │  │
│  │ 👤 Alice Chen - 2 edits                  │  │
│  └──────────────────────────────────────────┘  │
│                                                │
│  ┌─── Version History ──────────────────────┐  │
│  │ v3 - 2 hours ago by John (Current)       │  │
│  │ v2 - Yesterday by Jane                   │  │
│  │ v1 - Dec 1 by John (Original)            │  │
│  │      [View] [Restore] [Compare]           │  │
│  └──────────────────────────────────────────┘  │
│                                                │
│  ┌─── Related Documents ────────────────────┐  │
│  │ 📝 Q3 Marketing Review                   │  │
│  │ 📊 Marketing Budget 2025                 │  │
│  │ 📝 Competitor Analysis                   │  │
│  └──────────────────────────────────────────┘  │
│                                                │
│              [Export Analytics Report]         │
│                                                │
└────────────────────────────────────────────────┘
```

### 2. **Version History Viewer**

```javascript
// Version comparison view
const versionHistory = [
    {
        version: 3,
        created_at: '2025-12-10T14:30:00Z',
        created_by: 'john@example.com',
        changes: {
            added: 250,    // characters/cells added
            removed: 120,  // characters/cells removed
            modified: 45   // lines/rows modified
        },
        comment: 'Updated Q4 goals based on feedback',
        size: '245 KB'
    },
    {
        version: 2,
        created_at: '2025-12-09T10:15:00Z',
        created_by: 'jane@example.com',
        changes: {
            added: 500,
            removed: 50,
            modified: 120
        },
        comment: 'Added competitive analysis section',
        size: '198 KB'
    }
];

// Side-by-side comparison
<div class="version-comparison">
    <div class="version-left">
        <h4>Version 2 (Dec 9)</h4>
        <div class="diff-content">
            <del>Old content highlighted in red</del>
        </div>
    </div>
    <div class="version-right">
        <h4>Version 3 (Dec 10 - Current)</h4>
        <div class="diff-content">
            <ins>New content highlighted in green</ins>
        </div>
    </div>
</div>
```

### 3. **Smart Templates**

Pre-configured templates for common document types:

```javascript
const templates = {
    meetingNotes: {
        title: 'Meeting Notes - [Date]',
        docType: 'richtext',
        content: {
            sections: [
                { heading: 'Attendees', content: '- ' },
                { heading: 'Agenda', content: '1. ' },
                { heading: 'Discussion Points', content: '- ' },
                { heading: 'Action Items', content: '- [ ] ' },
                { heading: 'Next Steps', content: '- ' }
            ]
        },
        tags: ['meeting', 'notes'],
        visibility: 'team'
    },
    
    projectBrief: {
        title: 'Project Brief - [Project Name]',
        docType: 'richtext',
        content: {
            sections: [
                { heading: 'Project Overview', content: '' },
                { heading: 'Objectives', content: '1. \n2. \n3. ' },
                { heading: 'Scope', content: 'In Scope:\n- \n\nOut of Scope:\n- ' },
                { heading: 'Timeline', content: 'Start Date:\nEnd Date:\nMilestones:\n- ' },
                { heading: 'Budget', content: '' },
                { heading: 'Stakeholders', content: '- ' },
                { heading: 'Success Metrics', content: '- ' }
            ]
        },
        tags: ['project', 'brief'],
        visibility: 'team'
    },
    
    financialSpreadsheet: {
        title: 'Financial Report - [Month/Quarter]',
        docType: 'spreadsheet',
        content: {
            sheets: [
                {
                    name: 'Revenue',
                    headers: ['Category', 'Budgeted', 'Actual', 'Variance', 'Notes'],
                    rows: []
                },
                {
                    name: 'Expenses',
                    headers: ['Category', 'Budgeted', 'Actual', 'Variance', 'Notes'],
                    rows: []
                },
                {
                    name: 'Summary',
                    headers: ['Metric', 'Value'],
                    rows: [
                        ['Total Revenue', '=SUM(Revenue!B:B)'],
                        ['Total Expenses', '=SUM(Expenses!B:B)'],
                        ['Net Profit', '=Summary!B1-Summary!B2']
                    ]
                }
            ]
        },
        tags: ['financial', 'report'],
        visibility: 'private'
    }
};
```

### 4. **Collaboration Features**

**Real-time presence:**
```javascript
// Show who's currently viewing/editing
const liveUsers = [
    {
        userId: 'user_123',
        username: 'John Doe',
        action: 'editing',     // 'viewing' or 'editing'
        section: 'Section 3',  // Current location in doc
        lastActivity: Date.now(),
        cursorColor: '#3b82f6'
    }
];

// UI indicator
<div class="live-users">
    <span class="live-user" style="border-color: #3b82f6">
        👤 John Doe (editing Section 3)
    </span>
</div>
```

**Comment threads:**
```javascript
// Add comments to specific sections
const comments = [
    {
        commentId: 'comment_xxx',
        docId: 'doc_xxx',
        userId: 'user_123',
        username: 'Jane Smith',
        content: 'Should we revise these numbers?',
        section: 'Section 2, Line 45',
        created_at: '2025-12-10T10:00:00Z',
        resolved: false,
        replies: [
            {
                userId: 'user_456',
                username: 'John Doe',
                content: 'Good catch, I\'ll update them.',
                created_at: '2025-12-10T10:15:00Z'
            }
        ]
    }
];
```

### 5. **Export Engine**

**Single Document Export:**
```javascript
const exportFormats = {
    json: {
        mimeType: 'application/json',
        extension: '.json',
        processor: (doc) => JSON.stringify(doc, null, 2)
    },
    
    markdown: {
        mimeType: 'text/markdown',
        extension: '.md',
        processor: (doc) => convertRichTextToMarkdown(doc.content)
    },
    
    pdf: {
        mimeType: 'application/pdf',
        extension: '.pdf',
        processor: (doc) => generatePDF(doc),
        options: {
            pageSize: 'A4',
            margins: { top: 72, right: 72, bottom: 72, left: 72 },
            includeHeaders: true,
            includeFooters: true
        }
    },
    
    html: {
        mimeType: 'text/html',
        extension: '.html',
        processor: (doc) => renderHTML(doc),
        options: {
            includeCSS: true,
            standalone: true
        }
    },
    
    csv: {
        // For spreadsheet documents only
        mimeType: 'text/csv',
        extension: '.csv',
        processor: (doc) => convertSpreadsheetToCSV(doc.content)
    },
    
    excel: {
        // For spreadsheet documents
        mimeType: 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
        extension: '.xlsx',
        processor: (doc) => generateExcel(doc.content)
    }
};
```

**Bulk Export:**
```javascript
async function bulkExport(selectedDocs, format) {
    if (format === 'zip') {
        // Create ZIP with all docs
        const zip = new JSZip();
        selectedDocs.forEach(doc => {
            const filename = `${doc.slug || doc.doc_id}.json`;
            zip.file(filename, JSON.stringify(doc, null, 2));
        });
        return await zip.generateAsync({ type: 'blob' });
    }
    
    if (format === 'pdf-combined') {
        // Merge all docs into single PDF
        return await generateCombinedPDF(selectedDocs);
    }
    
    if (format === 'csv-metadata') {
        // Export document metadata as CSV
        const headers = ['Title', 'Type', 'Created By', 'Created At', 'Session', 'Tags'];
        const rows = selectedDocs.map(doc => [
            doc.title,
            doc.doc_type,
            doc.created_by,
            doc.created_at,
            doc.session_id || 'N/A',
            doc.tags?.join(', ') || ''
        ]);
        return generateCSV(headers, rows);
    }
}
```

---

## 💾 Backend Requirements

### New API Endpoints

#### 1. Document Library List (Enhanced)
```python
@document_library_bp.route('/list', methods=['GET'])
@require_auth
def list_documents():
    """
    Get paginated list of documents with filters
    
    Query Parameters:
    - page: int (default 1)
    - limit: int (default 50, max 200)
    - sort: str ('created_at', 'updated_at', 'title')
    - order: str ('asc', 'desc')
    - view: str ('all', 'starred', 'recent', 'orphaned', etc.)
    - doc_type: str ('richtext', 'spreadsheet', 'all')
    - date_from: ISO date
    - date_to: ISO date
    - tags: comma-separated string
    - visibility: str ('private', 'team', 'public')
    - session_id: str
    - created_by: str
    - search: str (full-text search)
    
    Returns:
    {
        "success": true,
        "documents": [{ doc object }],
        "pagination": {
            "page": 1,
            "limit": 50,
            "total": 245,
            "totalPages": 5,
            "hasNext": true,
            "hasPrev": false
        },
        "stats": {
            "totalDocuments": 245,
            "richTextCount": 189,
            "spreadsheetCount": 56,
            "linkedToSynergy": 198,
            "orphaned": 47
        }
    }
    """
```

#### 2. Document Analytics
```python
@document_library_bp.route('/<doc_id>/analytics', methods=['GET'])
@require_auth
def get_document_analytics(doc_id):
    """
    Get analytics for a specific document
    
    Returns:
    {
        "doc_id": "doc_xxx",
        "views": 127,
        "edits": 34,
        "uniqueCollaborators": 5,
        "shares": 12,
        "avgEditTime": 900,  # seconds
        "viewsOverTime": [{ date, count }],
        "editsOverTime": [{ date, count }],
        "collaborators": [{ user, editCount }],
        "relatedDocuments": [{ doc_id, title, similarity }]
    }
    """
```

#### 3. Version History
```python
@document_library_bp.route('/<doc_id>/versions', methods=['GET'])
@require_auth
def get_version_history(doc_id):
    """
    Get version history for document
    
    Returns:
    {
        "doc_id": "doc_xxx",
        "currentVersion": 3,
        "versions": [
            {
                "version": 3,
                "created_at": "2025-12-10T14:30:00Z",
                "created_by": "john@example.com",
                "changes": { "added": 250, "removed": 120, "modified": 45 },
                "comment": "Updated Q4 goals",
                "size": 251392,
                "contentSnapshot": "..." // Optional, for comparison
            }
        ]
    }
    """
```

#### 4. Bulk Operations
```python
@document_library_bp.route('/bulk/export', methods=['POST'])
@require_auth
def bulk_export():
    """
    Export multiple documents
    
    Request body:
    {
        "doc_ids": ["doc_1", "doc_2", "doc_3"],
        "format": "zip" | "pdf-combined" | "csv-metadata"
    }
    
    Returns: Binary file download
    """

@document_library_bp.route('/bulk/link', methods=['POST'])
@require_auth
def bulk_link_to_session():
    """
    Link multiple documents to a session
    
    Request body:
    {
        "doc_ids": ["doc_1", "doc_2", "doc_3"],
        "session_id": "session_xxx"
    }
    """

@document_library_bp.route('/bulk/tag', methods=['POST'])
@require_auth
def bulk_add_tags():
    """
    Add tags to multiple documents
    
    Request body:
    {
        "doc_ids": ["doc_1", "doc_2", "doc_3"],
        "tags": ["urgent", "review"]
    }
    """
```

#### 5. Template Management
```python
@document_library_bp.route('/templates', methods=['GET'])
def list_templates():
    """
    Get available document templates
    """

@document_library_bp.route('/templates/<template_id>', methods=['POST'])
@require_auth
def create_from_template(template_id):
    """
    Create new document from template
    
    Request body:
    {
        "title": "My New Document",
        "session_id": "session_xxx" (optional),
        "variables": { "project_name": "Project X" }
    }
    """
```

---

## 🎯 Implementation Roadmap

### Phase 1: Core Sidebar (Week 1) ⭐ PRIORITY
- [x] Database schema verification
- [ ] Sidebar framework integration (following Module Architect V5.0)
- [ ] Basic document list with pagination
- [ ] Search bar with autocomplete
- [ ] Quick stats dashboard
- [ ] Document card rendering
- [ ] View/Edit/Delete actions
- [ ] Integration with existing InternalDocsManager

**Files to Create:**
- `UI/modules_internal/document-library/document-library-sidebar.js`
- `UI/modules_internal/document-library/document-library-sidebar.html`
- `UI/modules_internal/document-library/document-library-sidebar.css`
- `UI/modules_internal/document-library/manifest.json`

**Files to Modify:**
- `UI/shared/sidebar-framework/sidebar-init.js` (register new sidebar)
- `UI/business-ai-platform-v2.html` (add toggle button)

### Phase 2: Filtering & Views (Week 2)
- [ ] Smart views implementation (All, Starred, Recent, etc.)
- [ ] Advanced filters panel
- [ ] Filter persistence (localStorage)
- [ ] Backend `/list` endpoint enhancement
- [ ] Tag management system
- [ ] Session/Thread linking dropdowns

### Phase 3: Bulk Operations (Week 3)
- [ ] Multi-select checkbox system
- [ ] Bulk actions bar
- [ ] Export engine (JSON, PDF, ZIP)
- [ ] Bulk tagging
- [ ] Bulk session linking
- [ ] Bulk delete with confirmation

### Phase 4: Advanced Features (Week 4)
- [ ] Analytics dashboard
- [ ] Version history viewer
- [ ] Version comparison (diff view)
- [ ] Template system
- [ ] Template variable substitution
- [ ] Collaboration indicators (live presence)

### Phase 5: Polish & Optimization (Week 5)
- [ ] Performance optimization (virtual scrolling)
- [ ] Keyboard shortcuts
- [ ] Accessibility (ARIA labels)
- [ ] Mobile responsive design
- [ ] Error handling & retry logic
- [ ] Comprehensive testing

---

## 🎨 Styling Guidelines

### Color Palette
```css
:root {
    /* Document Library Theme */
    --doc-library-primary: #3b82f6;      /* Blue accent */
    --doc-library-secondary: #8b5cf6;    /* Purple accent */
    --doc-library-success: #10b981;      /* Green for linked docs */
    --doc-library-warning: #f59e0b;      /* Orange for orphaned docs */
    --doc-library-danger: #ef4444;       /* Red for destructive actions */
    
    /* Background colors */
    --doc-library-bg-primary: var(--bg-primary);
    --doc-library-bg-secondary: var(--bg-secondary);
    --doc-library-bg-tertiary: var(--bg-tertiary);
    --doc-library-bg-hover: rgba(59, 130, 246, 0.1);
    
    /* Text colors */
    --doc-library-text-primary: var(--text-primary);
    --doc-library-text-secondary: var(--text-secondary);
    --doc-library-text-muted: var(--text-muted);
    
    /* Border colors */
    --doc-library-border: var(--border-default);
    --doc-library-border-focus: var(--doc-library-primary);
}
```

### Component Classes
```css
/* Sidebar container */
.document-library-sidebar {
    width: 750px;
    max-width: 90vw;
    background: var(--doc-library-bg-primary);
    border-left: 1px solid var(--doc-library-border);
    display: flex;
    flex-direction: column;
    height: 100%;
}

/* Search bar */
.doc-library-search {
    width: 100%;
    padding: var(--space-3);
    font-size: 14px;
    border: 1px solid var(--doc-library-border);
    border-radius: 8px;
    background: var(--doc-library-bg-secondary);
    transition: all 0.2s;
}

.doc-library-search:focus {
    outline: none;
    border-color: var(--doc-library-border-focus);
    box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.1);
}

/* Document card */
.doc-library-card {
    padding: var(--space-3);
    border: 1px solid var(--doc-library-border);
    border-radius: 8px;
    margin-bottom: var(--space-2);
    transition: all 0.2s;
    background: var(--doc-library-bg-secondary);
}

.doc-library-card:hover {
    border-color: var(--doc-library-primary);
    background: var(--doc-library-bg-hover);
    transform: translateY(-2px);
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
}

/* Context badges */
.context-badge {
    display: inline-flex;
    align-items: center;
    gap: var(--space-1);
    padding: var(--space-1) var(--space-2);
    border-radius: 4px;
    font-size: 12px;
    font-weight: 500;
}

.context-badge.synergy {
    background: linear-gradient(135deg, #10b981, #059669);
    color: white;
}

.context-badge.thread {
    background: linear-gradient(135deg, #3b82f6, #2563eb);
    color: white;
}

.context-badge.orphan {
    background: linear-gradient(135deg, #f59e0b, #d97706);
    color: white;
}
```

---

## 🧪 Testing Checklist

### Unit Tests
- [ ] Document list rendering with mock data
- [ ] Filter application logic
- [ ] Search autocomplete behavior
- [ ] Bulk selection state management
- [ ] Export format converters

### Integration Tests
- [ ] API endpoint integration
- [ ] Sidebar open/close with SidebarManager
- [ ] Document creation from templates
- [ ] Version history retrieval
- [ ] Bulk operations API calls

### E2E Tests
- [ ] Complete document lifecycle (create → edit → link → delete)
- [ ] Search and filter workflow
- [ ] Bulk export of multiple documents
- [ ] Template instantiation
- [ ] Collaboration indicator updates

### Performance Tests
- [ ] Load 1000+ documents without lag
- [ ] Search response time < 500ms
- [ ] Virtual scrolling smooth at 60fps
- [ ] Export of 100+ docs completes < 30s

---

## 📊 Success Metrics

### User Engagement
- **Daily Active Users**: Track sidebar opens per day
- **Documents Created**: New docs created via sidebar
- **Search Usage**: % of sessions using search
- **Bulk Operations**: Frequency of bulk actions

### Efficiency Gains
- **Time to Find Document**: Average time from sidebar open to document open
- **Orphan Resolution Rate**: % of orphaned docs linked per week
- **Export Frequency**: Documents exported per week
- **Template Adoption**: % of docs created from templates

### System Performance
- **API Response Time**: < 500ms for list endpoint
- **Search Latency**: < 300ms for autocomplete
- **Sidebar Load Time**: < 1s for initial render
- **Memory Usage**: < 100MB for 1000 docs loaded

---

## 🚀 Future Enhancements

### AI-Powered Features
- **Smart Suggestions**: "Documents similar to this one..."
- **Auto-Tagging**: ML-based tag recommendations
- **Content Summarization**: AI-generated document summaries
- **Duplicate Detection**: Find similar/duplicate documents

### Advanced Collaboration
- **Real-time Co-editing**: Multiple users editing simultaneously
- **Change Tracking**: Word-style track changes
- **Approval Workflows**: Document review and approval system
- **Mentions & Notifications**: @mention users in comments

### Enterprise Features
- **Document Permissions**: Granular access control
- **Audit Logs**: Complete edit history with user tracking
- **Compliance**: GDPR data export, retention policies
- **Integration**: Webhook support, API rate limiting

---

## 📚 Related Documentation

- `SYNERGY_FILES_ENHANCEMENTS_DEC9_2025.md` - Recent file enhancements
- `SYNERGY_DOCUMENTS_ADD_BUTTON_FIX_DEC10.md` - Documents section improvements
- `Module Architect V5.0 - Sidebar Framework Integration.prompt.md` - Sidebar framework guide
- `SIDEBAR_FRAMEWORK_GUIDE.md` - Universal sidebar framework docs
- `document_library_routes.py` - Existing document library API

---

## 🎓 Developer Notes

### Key Patterns to Follow

1. **Use Universal Sidebar Framework**
   - Register sidebar in `sidebar-init.js`
   - Follow button ID conventions
   - Use `SidebarManager.close()` for close buttons
   - No manual event handlers

2. **Cursor Management in APIs**
   - Always initialize `cursor = None` before try
   - Use try/finally blocks
   - Close cursor before connection
   - Handle early returns properly

3. **State Management**
   - Use `window.DocumentLibrary` for global state
   - Persist filters in localStorage
   - Debounce search input (300ms)
   - Cache document list for offline access

4. **Performance Optimization**
   - Virtual scrolling for 1000+ documents
   - Lazy load document previews
   - Paginate API requests (50 per page)
   - Compress export files

5. **Error Handling**
   - User-friendly error messages
   - Retry failed API calls (max 3 attempts)
   - Offline mode with cached data
   - Graceful degradation if features unavailable

---

## 🎉 Conclusion

The **Documents Library Sidebar** transforms scattered document management into a centralized, powerful hub. By combining existing infrastructure with new advanced features, it provides users with:

- ✅ **Visibility**: See all documents in one place
- ✅ **Control**: Advanced filtering and bulk operations
- ✅ **Efficiency**: Quick actions and keyboard shortcuts
- ✅ **Insights**: Analytics and version history
- ✅ **Collaboration**: Real-time presence and comments
- ✅ **Organization**: Smart views and templates

This comprehensive system elevates document management from a scattered afterthought to a core productivity feature of the platform.

---

**Ready to implement? Start with Phase 1 (Core Sidebar) and iterate based on user feedback!** 🚀

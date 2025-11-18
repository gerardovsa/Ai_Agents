# SYNERGY INTERNAL DOCS INTEGRATION GUIDE

**Date:** November 19, 2025  
**Purpose:** Document Internal Docs UI functionality for Synergy sessions

---

## 📋 OVERVIEW

**Synergy Internal Docs** are rich-text documents and spreadsheets embedded within Synergy sessions. They provide a collaborative workspace for:
- Meeting notes
- Project documentation
- Data tables and spreadsheets
- Decision logs
- Requirements specifications

---

## 🗄️ DATABASE SCHEMA

### Table: `synergy_sessions.synergy_internal_docs`

```sql
CREATE TABLE synergy_sessions.synergy_internal_docs (
  doc_id TEXT PRIMARY KEY,                    -- Unique document ID (doc_xxx)
  session_id TEXT NOT NULL,                   -- Parent session ID
  title TEXT NOT NULL,                        -- Document title
  content TEXT NOT NULL DEFAULT '',           -- Document content (markdown/plain text)
  format TEXT NOT NULL DEFAULT 'markdown',    -- Content format (markdown, html, plain)
  created_at TEXT,                            -- ISO timestamp
  updated_at TEXT,                            -- ISO timestamp
  created_by TEXT,                            -- User/agent who created
  version INTEGER DEFAULT 1,                  -- Version number for history
  content_json TEXT,                          -- JSON data for spreadsheets
  doc_type TEXT DEFAULT 'richtext',           -- 'richtext' or 'spreadsheet'
  linked_to_ai BOOLEAN DEFAULT FALSE,         -- If AI agent has access
  share_url TEXT,                             -- Public share URL (if shared)
  description TEXT,                           -- Short description
  tags TEXT,                                  -- JSON array of tags
  slug TEXT,                                  -- URL-friendly slug
  
  FOREIGN KEY (session_id) REFERENCES synergy_sessions.synergy_sessions(session_id) ON DELETE CASCADE
);

-- Indexes
CREATE INDEX idx_internal_docs_session ON synergy_sessions.synergy_internal_docs(session_id);
CREATE INDEX idx_internal_docs_type ON synergy_sessions.synergy_internal_docs(doc_type);
CREATE INDEX idx_internal_docs_linked_ai ON synergy_sessions.synergy_internal_docs(linked_to_ai);
```

---

## 🎨 UI COMPONENTS

### 1. Document List in Session Card

**Location:** Within Synergy session card, "Documents" section

**Visual Design:**
```
┌─ Documents (3) ──────────────────────────────┐
│ ┌─────────────────────────────────────────┐ │
│ │ [D1] 📄 Meeting Notes         v3 │ Rich  │ │
│ └─────────────────────────────────────────┘ │
│ ┌─────────────────────────────────────────┐ │
│ │ [D2] 📊 Customer Database     v2 │ Sheet │ │
│ └─────────────────────────────────────────┘ │
│ ┌─────────────────────────────────────────┐ │
│ │ [D3] 📄 Requirements Spec     v1 │ Rich  │ │
│ └─────────────────────────────────────────┘ │
└───────────────────────────────────────────┘
```

**Features:**
- Click to open in popup editor
- Version number badge
- Doc type indicator (Rich/Sheet)
- Sequential numbering (D1, D2, D3)

### 2. Internal Doc Editor Popup

**Opened via:** Click on document in list

**Layout:**
```
┌── Internal Document Editor ────────────── [×] ─┐
│ Title: [Meeting Notes                        ] │
│ Type:  ( ) Richtext  ( ) Spreadsheet           │
│                                                 │
│ ┌─ Content ──────────────────────────────────┐ │
│ │ # Meeting Notes - Nov 19, 2025            │ │
│ │                                            │ │
│ │ ## Attendees                              │ │
│ │ - John Smith                              │ │
│ │ - Sarah Johnson                           │ │
│ │                                            │ │
│ │ ## Action Items                           │ │
│ │ 1. Review requirements                    │ │
│ │ 2. Schedule follow-up                     │ │
│ └────────────────────────────────────────────┘ │
│                                                 │
│ [ Link to AI ]  [Cancel]  [Save Changes]       │
└─────────────────────────────────────────────────┘
```

**Editor Types:**

#### A. Rich Text Editor
- Markdown support with live preview
- Syntax highlighting
- Table support
- Image embedding
- Code blocks

#### B. Spreadsheet Editor
- Grid-based data entry
- Column headers
- Sort/filter capability
- Formula support (future)
- CSV export

### 3. Document Creation Flow

**Trigger:** "Add Document" button in session card

**Steps:**
1. Click "Add Document"
2. Popup opens with empty form
3. Enter title and select type
4. Click "Create"
5. Document appears in list with (D#) badge
6. Click to edit content

---

## 🔧 BACKEND API ENDPOINTS

### Existing Routes (in `synergy_routes.py`)

```python
# Create internal doc
POST /api/synergy/internal-doc/create
Body: {
    "session_id": "sess_xxx",
    "title": "Meeting Notes",
    "content": "# Meeting Notes...",
    "doc_type": "richtext",
    "format": "markdown"
}
Response: {
    "success": true,
    "doc_id": "doc_xxx",
    "version": 1
}

# Get internal doc
GET /api/synergy/internal-doc/<doc_id>
Response: {
    "success": true,
    "doc": {
        "doc_id": "doc_xxx",
        "title": "Meeting Notes",
        "content": "...",
        "doc_type": "richtext",
        "version": 3
    }
}

# Update internal doc
PATCH /api/synergy/internal-doc/<doc_id>
Body: {
    "content": "Updated content...",
    "title": "New Title (optional)"
}
Response: {
    "success": true,
    "version": 4
}

# Delete internal doc
DELETE /api/synergy/internal-doc/<doc_id>
Response: {
    "success": true
}

# List all docs for session
GET /api/synergy/internal-doc/list?session_id=sess_xxx
Response: {
    "success": true,
    "docs": [
        {"doc_id": "doc_1", "title": "Meeting Notes", ...},
        {"doc_id": "doc_2", "title": "Customer DB", ...}
    ]
}

# Link doc to AI agent
POST /api/synergy/internal-doc/<doc_id>/link-ai
Body: {
    "linked": true
}
Response: {
    "success": true,
    "linked_to_ai": true
}

# Export doc
GET /api/synergy/internal-doc/<doc_id>/export?format=markdown
Formats: markdown, html, csv (for spreadsheets)
```

---

## 🎯 INTEGRATION WITH MILESTONE SYSTEM

### How Internal Docs Work with Milestones:

**Use Case 1: Meeting Notes Document**
- Session: "Q1 Planning"
- Milestone 1: "Requirements Gathering"
  - Task 1.1: Document requirements
  - Task 1.2: Review with stakeholders
- **Internal Doc:** "Requirements Specification" (linked to session)
  - AI agent can read/write to this doc
  - Checklist in doc can sync with milestone tasks

**Use Case 2: Project Database Spreadsheet**
- Session: "Customer Onboarding Campaign"
- Milestone 2: "Database Setup"
  - Task 2.1: Create customer spreadsheet
  - Task 2.2: Import existing contacts
- **Internal Doc:** "Customer Database" (spreadsheet type)
  - Contains customer data in grid format
  - AI agent can add rows via API
  - Can export as CSV for external use

### Document References in Milestone Descriptions:

```javascript
// Milestone with doc reference
{
    "milestone_name": "Requirements Gathering",
    "description": "Document requirements in [D1: Requirements Spec]",
    "tasks": [
        "Read existing docs",
        "Update requirements doc",
        "Get stakeholder approval"
    ]
}
```

### AI Agent Document Access:

When `linked_to_ai: true`:
- AI agent can read document content
- AI agent can append to document
- Document appears in agent's context
- Agent can reference document by doc_id

---

## 🔄 WORKFLOW EXAMPLES

### Example 1: Meeting Notes Workflow

```
1. User creates Synergy session: "Weekly Planning Meeting"
2. User adds internal doc: "Meeting Notes Nov 19"
3. During meeting, user types notes in doc editor
4. User creates milestone from meeting: "Launch Email Campaign"
5. Milestone tasks reference doc: "See [D1] for requirements"
6. User links doc to AI agent
7. AI agent reads requirements from doc
8. AI agent creates detailed task breakdown
```

### Example 2: Project Database Workflow

```
1. User creates session: "Customer Onboarding"
2. User adds spreadsheet doc: "Customer List"
3. User creates milestone: "Import 100 Customers"
4. Tasks:
   - T1.1: Export from old CRM
   - T1.2: Clean data
   - T1.3: Import to [D1: Customer List]
5. AI agent checks doc for import status
6. When all customers imported, AI completes milestone
```

---

## 📊 STATISTICS & METRICS

### Document Counts in Session Card:

**Current Display:**
```
┌─ Card Stats ────────────────────┐
│ 💬 12  │  📄 3  │  ✅ 5/8  │
│ Messages│  Docs  │  Tasks   │
└─────────────────────────────────┘
```

**Documents Count:**
- Includes both internal docs and external links
- Internal docs have doc_type badge
- External links have 🔗 icon

---

## 🎨 STYLING GUIDELINES

### Document Badge Styles:

```css
.doc-badge {
    background: linear-gradient(135deg, #58a6ff 0%, #4a8fe7 100%);
    color: white;
    font-weight: 700;
    border-radius: 4px;
    font-size: 10px;
    padding: 0 6px;
    min-width: 28px;
    height: 22px;
}

.doc-item {
    display: flex;
    align-items: center;
    gap: 8px;
    padding: 8px;
    background: var(--bg-quaternary);
    border-radius: 4px;
    cursor: pointer;
    transition: background 0.2s;
}

.doc-item:hover {
    background: var(--bg-tertiary);
}

.doc-version-badge {
    font-size: 11px;
    color: var(--text-muted);
    padding: 2px 6px;
    background: var(--bg-secondary);
    border-radius: 3px;
}

.doc-type-badge {
    font-size: 10px;
    padding: 2px 6px;
    border-radius: 3px;
    background: var(--accent-primary);
    color: white;
}
```

---

## 🔗 INTEGRATION POINTS

### Where Internal Docs Appear:

1. **Synergy Session Card** - Documents section
2. **Session Popup View** - Dedicated docs tab
3. **Synergy Board** - Doc count badge on cards
4. **AI Agent Context** - Linked docs appear in system prompt
5. **Export** - Included in session export

### Document Linking:

**Link to AI Agent:**
- Checkbox in doc editor: "Allow AI access"
- When checked, sets `linked_to_ai: true`
- AI agent receives doc content in context
- AI can reference doc by ID in responses

**Link to External URLs:**
- Share button generates public URL
- Sets `share_url` field
- Anyone with link can view (read-only)

---

## 🧪 TESTING CHECKLIST

Before deploying Internal Docs redesign:

- [ ] Create rich text doc via API
- [ ] Create spreadsheet doc via API
- [ ] Open doc in popup editor
- [ ] Edit and save changes (verify version increments)
- [ ] Delete doc
- [ ] List all docs for session
- [ ] Link doc to AI agent
- [ ] Verify AI can read linked doc
- [ ] Generate share URL
- [ ] Access share URL (read-only view)
- [ ] Export doc as markdown
- [ ] Export spreadsheet as CSV
- [ ] Verify doc appears in session card
- [ ] Verify doc count in card stats
- [ ] Test responsive design on mobile
- [ ] Test dark mode

---

## 📝 FUTURE ENHANCEMENTS

### Phase 1 (Current):
- ✅ Basic rich text editor
- ✅ Spreadsheet grid editor
- ✅ Version tracking
- ✅ AI agent linking

### Phase 2 (Q1 2026):
- [ ] Real-time collaborative editing
- [ ] Comment threads on documents
- [ ] Document templates
- [ ] Spreadsheet formulas
- [ ] Document history/diff view

### Phase 3 (Q2 2026):
- [ ] OCR for image uploads
- [ ] AI-powered document summarization
- [ ] Auto-tagging based on content
- [ ] Document search across sessions

---

## 🔧 MAINTENANCE NOTES

### Document Cleanup:
- Orphaned docs (session deleted) are auto-deleted via CASCADE
- Old versions are kept in `milestone_history` table
- Share URLs expire after 30 days (implement expiry logic)

### Performance:
- Index on `session_id` for fast doc listing
- Paginate large document lists (> 20 docs)
- Lazy-load document content (fetch only when opened)

### Security:
- Validate user has access to session before showing docs
- Sanitize HTML content to prevent XSS
- Rate-limit share URL generation

---

**Last Updated:** November 19, 2025  
**Related Files:**
- `AI_infrastructure/routes/synergy_routes.py` (lines 1174-1728)
- `UI/external/modules/synergy-card-renderer.js` (renderDocuments method)
- `data/synergy_sessions_schema.sql`

# Internal Documents User Guide

**Created:** November 14, 2025  
**Status:** Backend Complete, UI In Progress  
**Version:** 1.0

---

## 📋 Overview

Internal Documents allow you to create and manage markdown documents **inside** Synergy sessions. Think of them as session-specific notes, drafts, or documentation that live alongside your project cards.

---

## 🎯 Current Implementation Status

### ✅ **Backend (100% Complete)**
- All API endpoints working
- Database table created
- Version tracking functional
- CRUD operations tested

### ⚠️ **Frontend UI (Not Yet Implemented)**
Currently, internal docs can **only be created by AI agents**, not by users directly through the UI.

---

## 🤖 How AI Agents Use Internal Docs

AI agents can create, read, update, and delete internal documents using these tools:

### 1. **Create Document**
```python
synergy_create_internal_doc(
    session_id='sess_123',
    title='Project Requirements',
    content='''# Requirements

## Core Features
1. User authentication
2. Dashboard interface
3. Data visualization

## Technical Stack
- Backend: Python Flask
- Frontend: JavaScript
- Database: SQLite
''',
    format='markdown',
    created_by='agent_deepseek'
)
```

### 2. **Read Document**
```python
synergy_get_internal_doc(
    doc_id='int_doc_1731600000123'
)
```

### 3. **Update Document**
```python
synergy_update_internal_doc(
    doc_id='int_doc_1731600000123',
    content='Updated content with new sections...'
)
```

### 4. **Delete Document**
```python
synergy_delete_internal_doc(
    doc_id='int_doc_1731600000123'
)
```

### 5. **List All Documents in Session**
```python
synergy_list_internal_docs(
    session_id='sess_123'
)
```

---

## 📝 Markdown Formatting Support

Internal docs support **full Markdown syntax**:

### Headers
```markdown
# H1 Header
## H2 Header
### H3 Header
#### H4 Header
```

### Text Formatting
```markdown
**Bold text**
*Italic text*
~~Strikethrough~~
`Inline code`
```

### Lists
```markdown
**Unordered:**
- Item 1
- Item 2
  - Nested item
  
**Ordered:**
1. First
2. Second
3. Third
```

### Code Blocks
````markdown
```python
def hello():
    print("Hello, world!")
```
````

### Links & Images
```markdown
[Link text](https://example.com)
![Image alt text](image-url.png)
```

### Tables
```markdown
| Column 1 | Column 2 | Column 3 |
|----------|----------|----------|
| Data 1   | Data 2   | Data 3   |
| Data 4   | Data 5   | Data 6   |
```

### Blockquotes
```markdown
> This is a quote
> It can span multiple lines
```

### Horizontal Rules
```markdown
---
```

---

## 🎨 Spacing & Formatting Best Practices

### Line Breaks
- **Single line break:** No effect in rendered markdown
- **Double line break:** Creates new paragraph
- **Two spaces at end of line:** Forces line break

```markdown
This is line 1
This is line 2 (same paragraph)

This is a new paragraph

This is line 1  
This is line 2 (forced break)
```

### Section Spacing
```markdown
## Section 1

Content here with good spacing.

## Section 2

More content with proper spacing.
```

### List Spacing
```markdown
1. Item with long description
   that wraps to multiple lines
   
2. Another item with space above

3. Third item
```

---

## 💾 Version Tracking

Every time a document is updated, the version number increments:

```
Version 1: Initial creation
Version 2: First update
Version 3: Second update
...
```

Version history is tracked in the database:
- `created_at` - When document was created
- `updated_at` - Last update timestamp
- `version` - Current version number

---

## 🔐 Access & Permissions

### Current Implementation
- Documents are tied to Synergy sessions
- Anyone with session access can read/edit docs
- No individual document permissions (yet)

### Deletion Behavior
- When a Synergy session is deleted, all its internal docs are **automatically deleted** (CASCADE)
- When a document is deleted individually, it's **permanently removed**

---

## 🚀 Planned UI Features (Coming Soon)

### 1. **Document List in Session Card**
- Show all internal docs in a Synergy card
- Click to view/edit
- Quick actions (duplicate, delete, export)

### 2. **Markdown Editor with Live Preview**
```
+------------------+------------------+
|   Editor         |   Preview        |
|   (Markdown)     |   (Rendered)     |
|                  |                  |
|  # My Doc        |  My Doc          |
|  Content...      |  Content...      |
+------------------+------------------+
```

### 3. **Document Actions**
- Export to Word
- Export to Google Doc
- Export to PDF
- Email document
- Copy markdown
- Duplicate document

### 4. **Templates**
- Project Brief
- Meeting Notes
- Technical Spec
- Requirements Doc
- Status Report

### 5. **Search & Filter**
- Search across all docs
- Filter by session
- Filter by date created
- Sort by title/date/version

---

## 📊 Database Structure

```sql
CREATE TABLE synergy_internal_docs (
    doc_id TEXT PRIMARY KEY,              -- int_doc_1731600000123
    session_id TEXT NOT NULL,             -- sess_123
    title TEXT NOT NULL,                  -- Document title
    content TEXT NOT NULL DEFAULT '',    -- Markdown content
    format TEXT NOT NULL DEFAULT 'markdown',
    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
    updated_at TEXT DEFAULT CURRENT_TIMESTAMP,
    created_by TEXT,                      -- Who created it
    version INTEGER DEFAULT 1,            -- Version tracking
    FOREIGN KEY (session_id) REFERENCES synergy_sessions(session_id) 
        ON DELETE CASCADE
);
```

---

## 🔗 API Endpoints

All endpoints are fully functional:

### Create Document
```
POST /api/synergy/internal-doc/create
Body: {
    "session_id": "sess_123",
    "title": "Document Title",
    "content": "# Markdown content...",
    "format": "markdown",
    "created_by": "user_name"
}
```

### Get Document
```
GET /api/synergy/internal-doc/<doc_id>
```

### Update Document
```
PUT /api/synergy/internal-doc/<doc_id>
Body: {
    "title": "Updated Title",
    "content": "Updated content..."
}
```

### Delete Document
```
DELETE /api/synergy/internal-doc/<doc_id>
```

### List Documents in Session
```
GET /api/synergy/internal-doc/list/<session_id>
```

---

## ✅ Testing

Full test suite available in `test_internal_docs_complete.py`:

```powershell
cd C:\Users\gpoli\GIT\AI_agents
python test_internal_docs_complete.py
```

Expected output:
```
✅ Create document
✅ Get document
✅ Update document (version 1 → 2)
✅ List documents (2 found)
✅ Delete document
✅ Verify deletion (1 remaining)

🎉 ALL TESTS PASSED!
```

---

## 🎯 Use Cases

### 1. **Project Requirements**
```markdown
# Project: E-Commerce Platform

## Objectives
- Build online store
- Support 10,000+ products
- Mobile responsive

## Timeline
- Phase 1: 2 months
- Phase 2: 3 months
```

### 2. **Meeting Notes**
```markdown
# Client Meeting - Nov 14, 2025

## Attendees
- John (Client)
- Sarah (PM)
- Mike (Dev Lead)

## Key Decisions
1. Launch date: Jan 15, 2026
2. Budget approved: $150K
3. Weekly status calls
```

### 3. **Technical Specifications**
```markdown
# API Specification

## Endpoints

### POST /api/users
**Request:**
```json
{
  "name": "John Doe",
  "email": "john@example.com"
}
```

**Response:**
```json
{
  "id": 123,
  "name": "John Doe"
}
```
```

### 4. **Status Reports**
```markdown
# Weekly Status Report - Week of Nov 14

## Completed ✅
- User authentication module
- Database migrations
- Unit tests (85% coverage)

## In Progress 🔄
- Payment integration
- Email notifications

## Blockers ⚠️
- Waiting for API keys from vendor
```

---

## 🔮 Future Enhancements

### Phase 2 (Q1 2026)
- [ ] Rich text editor option (alternative to markdown)
- [ ] Document templates library
- [ ] Collaborative editing (multiple users)
- [ ] Comment system
- [ ] Document sharing (public links)

### Phase 3 (Q2 2026)
- [ ] AI-assisted writing
- [ ] Auto-save drafts
- [ ] Document versioning with rollback
- [ ] Search with highlighting
- [ ] Export to more formats (LaTeX, EPUB)

---

## 📞 Support

For questions or issues:
1. Check test script: `test_internal_docs_complete.py`
2. Review API docs: `SYNERGY_INTERNAL_DOCS_ANALYSIS.md`
3. Check Flask logs for errors

---

**Last Updated:** November 14, 2025  
**Implementation:** Backend Complete ✅ | Frontend UI Pending ⏳

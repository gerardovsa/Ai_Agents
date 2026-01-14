# Synergy Internal Documents - Complete Analysis & Implementation Plan

**Date:** November 14, 2025  
**Purpose:** Enable AI agents and users to create, edit, and manage long-form documents directly within Synergy without requiring external Drive/OneDrive storage

---

## 📋 Problem Statement

**Current Pain:**
- AI agents need to create lengthy updates/summaries/drafts for Synergy sessions
- Must create Word/Google Doc externally and link it to the Synergy card
- Requires OAuth credentials for Drive/OneDrive
- Breaks workflow with external dependencies
- Content lives outside Synergy (version control, search, sync issues)

**Desired Solution:**
- Internal "digital documents" stored within Synergy database
- AI can create/update long-form content using tools
- Users can click document in card to open editor modal
- Edit content inline (rich text editor)
- Export to Word/Google Docs/PDF when needed
- No external dependencies required

---

## 🏗️ Architecture Analysis

### Current Synergy Database Structure

```sql
Table: synergy_sessions (31 columns)
- session_id (TEXT PRIMARY KEY)
- title, description, notes (TEXT)
- documents (TEXT) -- JSON array
- thread_ids (TEXT) -- JSON array
- assigned_agents (TEXT) -- JSON array
- checklist (TEXT) -- JSON array
- next_steps (TEXT) -- JSON array
- links (TEXT) -- JSON array
- ... (22 more fields)
```

**Documents Field Structure (current):**
```json
{
  "documents": [
    {
      "title": "Project Spec",
      "url": "https://docs.google.com/...",
      "type": "google_doc"
    }
  ]
}
```

---

## 🎯 Solution: Three Implementation Options

### Option 1: Simple Container (HTML/Markdown) ⭐ RECOMMENDED

**Pros:**
- ✅ Lightweight (~200 lines backend + 300 lines frontend)
- ✅ No external dependencies or services
- ✅ Instant implementation (1-2 hours)
- ✅ Perfect for AI-generated content
- ✅ Markdown = AI-friendly format
- ✅ Easy versioning and search
- ✅ Works offline

**Cons:**
- ❌ Limited formatting (bold, italic, lists, headers)
- ❌ No real-time collaboration (not needed for AI workflow)
- ❌ No complex tables or images inline

**Tech Stack:**
- Storage: New table `synergy_internal_docs` in `data/synergy_sessions.db`
- Editor: `<textarea>` with markdown preview OR simple contenteditable div
- Backend: 4 new endpoints in `synergy_routes.py`
- Frontend: Modal with editor (like existing edit modal pattern)

**Implementation:**
```
Database: synergy_internal_docs
  - doc_id (TEXT PRIMARY KEY)
  - session_id (TEXT, FK to synergy_sessions)
  - title (TEXT)
  - content (TEXT) -- Markdown or HTML
  - format (TEXT) -- 'markdown' or 'html'
  - created_at (TEXT)
  - updated_at (TEXT)
  - created_by (TEXT) -- agent_id or user_id
  - version (INTEGER) -- for versioning

Documents array entry:
  {
    "title": "Project Draft v3",
    "doc_id": "int_doc_123456",
    "type": "internal_doc",
    "format": "markdown",
    "preview": "First 100 chars..."
  }
```

---

### Option 2: OnlyOffice Integration 🚀 POWERFUL

**Pros:**
- ✅ Full MS Office compatibility (.docx, .xlsx, .pptx)
- ✅ Rich formatting (tables, images, charts)
- ✅ Real-time collaboration (multiple users)
- ✅ Professional document editing experience
- ✅ Already have Docker Compose file ready
- ✅ Self-hosted (no cloud dependencies)

**Cons:**
- ❌ Complex setup (Docker container + integration)
- ❌ Resource heavy (~1GB RAM for documentserver)
- ❌ Longer implementation time (2-3 days)
- ❌ Overkill for AI-generated text summaries
- ❌ Requires JWT tokens and API integration
- ❌ Not AI-friendly (binary formats, not markdown)

**Tech Stack:**
- OnlyOffice Document Server (Docker container - already in `docker-compose.yml`)
- PostgreSQL for OnlyOffice data
- JWT authentication for secure document access
- Webhook integration for save callbacks
- Backend bridge in `synergy_routes.py` to proxy requests

**Implementation:**
```
1. Start OnlyOffice container:
   docker-compose up -d onlyoffice-documentserver

2. Backend endpoints:
   POST /api/synergy/internal-doc/create-office
   GET  /api/synergy/internal-doc/<doc_id>/office-config
   POST /api/synergy/internal-doc/<doc_id>/office-callback

3. Frontend integration:
   <div id="onlyoffice-editor"></div>
   <script src="http://localhost:8080/web-apps/apps/api/documents/api.js"></script>

4. Document lifecycle:
   - Create doc → Generate JWT → Load OnlyOffice iframe
   - Edit → Auto-save to OnlyOffice storage
   - Close → Callback updates Synergy DB with latest version
```

**Docker Compose (already exists):**
```yaml
onlyoffice-documentserver:
  image: onlyoffice/documentserver:latest
  ports:
    - "8080:80"
  environment:
    - JWT_ENABLED=true
    - JWT_SECRET=${ONLYOFFICE_JWT_SECRET}
  volumes:
    - onlyoffice_data:/var/www/onlyoffice/Data
```

---

### Option 3: Hybrid Approach 🎨 BEST OF BOTH

**Pros:**
- ✅ Start simple (markdown editor)
- ✅ Add OnlyOffice later for power users
- ✅ AI uses markdown, humans use WYSIWYG
- ✅ Gradual implementation (MVP → Full features)
- ✅ Document type flag determines editor

**Cons:**
- ⚠️ Two editors to maintain
- ⚠️ Format conversion complexity

**Implementation:**
```javascript
// Frontend logic
if (doc.type === 'internal_doc_markdown') {
  openMarkdownEditor(doc.doc_id);
} else if (doc.type === 'internal_doc_office') {
  openOnlyOfficeEditor(doc.doc_id);
}
```

---

## 💡 Recommendation: Option 1 (Simple Container)

### Why Simple Markdown/HTML Container Wins:

1. **AI-First Design:**
   - AI agents generate markdown naturally
   - LLMs understand markdown structure
   - Easy to parse and search
   - Version control friendly (plain text)

2. **Immediate Value:**
   - Solves the core problem NOW
   - No external service dependencies
   - Fast to implement (1-2 hours total)
   - Zero infrastructure cost

3. **Perfect for Use Case:**
   - Summaries, drafts, notes = plain text
   - Don't need complex formatting
   - Export to Word/Docs when polished version needed
   - Internal content doesn't need collaboration

4. **Upgrade Path:**
   - Can add OnlyOffice later if needed
   - Markdown converts easily to .docx
   - Database schema supports both types

---

## 🛠️ Detailed Implementation Plan (Option 1)

### Phase 1: Database Schema (15 minutes)

**File:** `create_internal_docs_table.py`

```python
"""Create synergy_internal_docs table"""
import sqlite3
from pathlib import Path

db_path = Path(__file__).parent / 'data' / 'synergy_sessions.db'
conn = sqlite3.connect(str(db_path))
cursor = conn.cursor()

cursor.execute('''
CREATE TABLE IF NOT EXISTS synergy_internal_docs (
    doc_id TEXT PRIMARY KEY,
    session_id TEXT NOT NULL,
    title TEXT NOT NULL,
    content TEXT NOT NULL DEFAULT '',
    format TEXT NOT NULL DEFAULT 'markdown',
    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
    updated_at TEXT DEFAULT CURRENT_TIMESTAMP,
    created_by TEXT,
    version INTEGER DEFAULT 1,
    FOREIGN KEY (session_id) REFERENCES synergy_sessions(session_id) ON DELETE CASCADE
)
''')

# Index for fast lookups
cursor.execute('CREATE INDEX IF NOT EXISTS idx_internal_docs_session ON synergy_internal_docs(session_id)')

conn.commit()
conn.close()
print("✅ Created synergy_internal_docs table")
```

---

### Phase 2: Backend API Endpoints (60 minutes)

**File:** `AI_infrastructure/routes/synergy_routes.py`

```python
# Add to existing file

@synergy_bp.route('/internal-doc/create', methods=['POST'])
def create_internal_doc():
    """
    Create a new internal document
    
    Body:
        {
            "session_id": "sess_123",
            "title": "Project Draft",
            "content": "# Header\n\nContent...",
            "format": "markdown",
            "created_by": "agent_deepseek"
        }
    
    Returns:
        {
            "success": true,
            "doc_id": "int_doc_1731600000123",
            "title": "Project Draft"
        }
    """
    data = request.get_json()
    session_id = data.get('session_id')
    title = data.get('title', 'Untitled Document')
    content = data.get('content', '')
    doc_format = data.get('format', 'markdown')
    created_by = data.get('created_by', 'unknown')
    
    if not session_id:
        return jsonify({'success': False, 'error': 'session_id required'}), 400
    
    # Generate doc_id
    doc_id = f"int_doc_{int(datetime.now().timestamp() * 1000)}"
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        # Insert internal doc
        cursor.execute('''
            INSERT INTO synergy_internal_docs 
            (doc_id, session_id, title, content, format, created_by, created_at, updated_at)
            VALUES (?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP)
        ''', (doc_id, session_id, title, content, doc_format, created_by))
        
        # Add to session's documents array
        cursor.execute('SELECT documents FROM synergy_sessions WHERE session_id = ?', (session_id,))
        row = cursor.fetchone()
        
        documents = json.loads(row['documents']) if row and row['documents'] else []
        documents.append({
            'doc_id': doc_id,
            'title': title,
            'type': 'internal_doc',
            'format': doc_format,
            'preview': content[:100] + ('...' if len(content) > 100 else '')
        })
        
        cursor.execute('''
            UPDATE synergy_sessions 
            SET documents = ?, updated_at = CURRENT_TIMESTAMP
            WHERE session_id = ?
        ''', (json.dumps(documents), session_id))
        
        conn.commit()
        conn.close()
        
        return jsonify({
            'success': True,
            'doc_id': doc_id,
            'title': title,
            'session_id': session_id
        })
        
    except Exception as e:
        conn.close()
        return jsonify({'success': False, 'error': str(e)}), 500


@synergy_bp.route('/internal-doc/<doc_id>', methods=['GET'])
def get_internal_doc(doc_id):
    """
    Get internal document content
    
    Returns:
        {
            "success": true,
            "doc_id": "int_doc_123",
            "session_id": "sess_456",
            "title": "Project Draft",
            "content": "# Header...",
            "format": "markdown",
            "created_at": "2025-11-14T12:00:00",
            "updated_at": "2025-11-14T14:30:00",
            "created_by": "agent_deepseek",
            "version": 3
        }
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute('SELECT * FROM synergy_internal_docs WHERE doc_id = ?', (doc_id,))
    row = cursor.fetchone()
    conn.close()
    
    if not row:
        return jsonify({'success': False, 'error': 'Document not found'}), 404
    
    return jsonify({
        'success': True,
        'doc_id': row['doc_id'],
        'session_id': row['session_id'],
        'title': row['title'],
        'content': row['content'],
        'format': row['format'],
        'created_at': row['created_at'],
        'updated_at': row['updated_at'],
        'created_by': row['created_by'],
        'version': row['version']
    })


@synergy_bp.route('/internal-doc/<doc_id>', methods=['PUT'])
def update_internal_doc(doc_id):
    """
    Update internal document content
    
    Body:
        {
            "content": "Updated content...",
            "title": "New Title (optional)"
        }
    
    Returns:
        {
            "success": true,
            "doc_id": "int_doc_123",
            "version": 4
        }
    """
    data = request.get_json()
    content = data.get('content')
    title = data.get('title')
    
    if not content and not title:
        return jsonify({'success': False, 'error': 'content or title required'}), 400
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        # Build update query dynamically
        updates = []
        params = []
        
        if content is not None:
            updates.append('content = ?')
            params.append(content)
        
        if title is not None:
            updates.append('title = ?')
            params.append(title)
        
        updates.append('updated_at = CURRENT_TIMESTAMP')
        updates.append('version = version + 1')
        
        params.append(doc_id)
        
        cursor.execute(f'''
            UPDATE synergy_internal_docs 
            SET {', '.join(updates)}
            WHERE doc_id = ?
        ''', params)
        
        # Get new version
        cursor.execute('SELECT version, session_id FROM synergy_internal_docs WHERE doc_id = ?', (doc_id,))
        row = cursor.fetchone()
        
        # Update preview in session documents array
        if title and row:
            session_id = row['session_id']
            cursor.execute('SELECT documents FROM synergy_sessions WHERE session_id = ?', (session_id,))
            sess_row = cursor.fetchone()
            
            if sess_row and sess_row['documents']:
                documents = json.loads(sess_row['documents'])
                for doc in documents:
                    if doc.get('doc_id') == doc_id:
                        doc['title'] = title
                        if content:
                            doc['preview'] = content[:100] + ('...' if len(content) > 100 else '')
                        break
                
                cursor.execute('UPDATE synergy_sessions SET documents = ? WHERE session_id = ?',
                             (json.dumps(documents), session_id))
        
        conn.commit()
        conn.close()
        
        return jsonify({
            'success': True,
            'doc_id': doc_id,
            'version': row['version'] if row else None
        })
        
    except Exception as e:
        conn.close()
        return jsonify({'success': False, 'error': str(e)}), 500


@synergy_bp.route('/internal-doc/<doc_id>', methods=['DELETE'])
def delete_internal_doc(doc_id):
    """
    Delete internal document
    
    Returns:
        {"success": true}
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        # Get session_id before deleting
        cursor.execute('SELECT session_id FROM synergy_internal_docs WHERE doc_id = ?', (doc_id,))
        row = cursor.fetchone()
        
        if not row:
            conn.close()
            return jsonify({'success': False, 'error': 'Document not found'}), 404
        
        session_id = row['session_id']
        
        # Delete from internal_docs table
        cursor.execute('DELETE FROM synergy_internal_docs WHERE doc_id = ?', (doc_id,))
        
        # Remove from session documents array
        cursor.execute('SELECT documents FROM synergy_sessions WHERE session_id = ?', (session_id,))
        sess_row = cursor.fetchone()
        
        if sess_row and sess_row['documents']:
            documents = json.loads(sess_row['documents'])
            documents = [doc for doc in documents if doc.get('doc_id') != doc_id]
            cursor.execute('UPDATE synergy_sessions SET documents = ? WHERE session_id = ?',
                         (json.dumps(documents), session_id))
        
        conn.commit()
        conn.close()
        
        return jsonify({'success': True})
        
    except Exception as e:
        conn.close()
        return jsonify({'success': False, 'error': str(e)}), 500
```

---

### Phase 3: AI Agent Tools (30 minutes)

**File:** `tools/implementations/synergy.py`

```python
# Add to existing file

def synergy_create_internal_doc(
    session_id: str,
    title: str,
    content: str,
    format: str = 'markdown',
    **kwargs
) -> Dict[str, Any]:
    """
    Create an internal document in a Synergy session
    
    Use this when you need to:
    - Store long-form content (summaries, drafts, reports)
    - Create documentation without external Drive/OneDrive
    - Keep content searchable within Synergy
    
    Args:
        session_id: Synergy session ID
        title: Document title
        content: Document content (markdown or HTML)
        format: 'markdown' or 'html' (default: 'markdown')
    
    Returns:
        {
            "success": true,
            "doc_id": "int_doc_123",
            "title": "Project Draft",
            "session_id": "sess_456"
        }
    
    Example:
        synergy_create_internal_doc(
            session_id='sess_20251114_1200',
            title='Meeting Summary - Nov 14',
            content='''# Meeting Summary
            
## Attendees
- John, Sarah, Mike

## Key Decisions
1. **Budget approved** - $50K for Q1
2. **Timeline set** - Launch by March 15

## Next Steps
- [ ] John: Draft proposal
- [ ] Sarah: Schedule follow-up
            '''
        )
    """
    created_by = kwargs.get('agent_id', 'unknown')
    
    response = requests.post(
        'http://localhost:5001/api/synergy/internal-doc/create',
        json={
            'session_id': session_id,
            'title': title,
            'content': content,
            'format': format,
            'created_by': created_by
        }
    )
    
    return response.json()


def synergy_update_internal_doc(
    doc_id: str,
    content: Optional[str] = None,
    title: Optional[str] = None,
    **kwargs
) -> Dict[str, Any]:
    """
    Update an existing internal document
    
    Args:
        doc_id: Internal document ID (starts with 'int_doc_')
        content: Updated content (optional)
        title: Updated title (optional)
    
    Returns:
        {"success": true, "doc_id": "...", "version": 4}
    """
    payload = {}
    if content is not None:
        payload['content'] = content
    if title is not None:
        payload['title'] = title
    
    response = requests.put(
        f'http://localhost:5001/api/synergy/internal-doc/{doc_id}',
        json=payload
    )
    
    return response.json()


def synergy_get_internal_doc(
    doc_id: str,
    **kwargs
) -> Dict[str, Any]:
    """
    Retrieve internal document content
    
    Args:
        doc_id: Internal document ID
    
    Returns:
        {
            "success": true,
            "doc_id": "int_doc_123",
            "title": "...",
            "content": "...",
            "format": "markdown",
            "created_at": "...",
            "version": 3
        }
    """
    response = requests.get(
        f'http://localhost:5001/api/synergy/internal-doc/{doc_id}'
    )
    
    return response.json()
```

**File:** `tools/schemas/synergy_tools.json`

```json
{
  "name": "synergy_create_internal_doc",
  "description": "Create an internal document in a Synergy session for storing long-form content (summaries, drafts, reports) without external Drive/OneDrive",
  "platform": "synergy",
  "parameters": {
    "type": "object",
    "properties": {
      "session_id": {
        "type": "string",
        "description": "Synergy session ID (required)"
      },
      "title": {
        "type": "string",
        "description": "Document title (required)"
      },
      "content": {
        "type": "string",
        "description": "Document content in markdown format (required)"
      },
      "format": {
        "type": "string",
        "description": "Content format: 'markdown' or 'html' (default: 'markdown')",
        "enum": ["markdown", "html"],
        "default": "markdown"
      }
    },
    "required": ["session_id", "title", "content"]
  }
}
```

---

### Phase 4: Frontend UI (90 minutes)

**File:** `UI/business-ai-platform-v2.html`

```javascript
// Add to SynergyBoard object

openInternalDocViewer(docId, sessionId) {
    // Fetch document
    fetch(`/api/synergy/internal-doc/${docId}`)
        .then(res => res.json())
        .then(data => {
            if (!data.success) {
                alert('Failed to load document: ' + data.error);
                return;
            }
            
            // Show modal
            const modal = document.createElement('div');
            modal.className = 'modal-overlay';
            modal.id = 'internal-doc-modal';
            modal.innerHTML = `
                <div class="modal-content internal-doc-modal">
                    <div class="modal-header">
                        <h3>
                            <i class="fas fa-file-alt"></i>
                            <input type="text" id="doc-title" value="${this.escapeHtml(data.title)}" 
                                   class="doc-title-input" />
                        </h3>
                        <div class="doc-meta">
                            <span><i class="fas fa-code"></i> ${data.format}</span>
                            <span><i class="fas fa-clock"></i> v${data.version}</span>
                            <span><i class="fas fa-calendar"></i> ${new Date(data.updated_at).toLocaleString()}</span>
                        </div>
                        <button class="modal-close" onclick="document.getElementById('internal-doc-modal').remove()">
                            <i class="fas fa-times"></i>
                        </button>
                    </div>
                    
                    <div class="modal-body">
                        <div class="doc-editor-container">
                            ${data.format === 'markdown' ? `
                                <div class="editor-tabs">
                                    <button class="tab-btn active" onclick="synergyBoard.switchDocTab('edit')">
                                        <i class="fas fa-edit"></i> Edit
                                    </button>
                                    <button class="tab-btn" onclick="synergyBoard.switchDocTab('preview')">
                                        <i class="fas fa-eye"></i> Preview
                                    </button>
                                </div>
                                <textarea id="doc-content" class="doc-editor markdown-editor">${this.escapeHtml(data.content)}</textarea>
                                <div id="doc-preview" class="doc-preview markdown-content" style="display: none;"></div>
                            ` : `
                                <div contenteditable="true" id="doc-content" class="doc-editor html-editor">${data.content}</div>
                            `}
                        </div>
                    </div>
                    
                    <div class="modal-footer">
                        <div class="footer-left">
                            <button class="btn-secondary" onclick="synergyBoard.exportInternalDoc('${docId}', 'word')">
                                <i class="fas fa-file-word"></i> Export to Word
                            </button>
                            <button class="btn-secondary" onclick="synergyBoard.exportInternalDoc('${docId}', 'google')">
                                <i class="fas fa-file"></i> Export to Google Doc
                            </button>
                        </div>
                        <div class="footer-right">
                            <button class="btn-secondary" onclick="document.getElementById('internal-doc-modal').remove()">
                                <i class="fas fa-times"></i> Cancel
                            </button>
                            <button class="btn-primary" onclick="synergyBoard.saveInternalDoc('${docId}')">
                                <i class="fas fa-save"></i> Save Changes
                            </button>
                        </div>
                    </div>
                </div>
            `;
            
            document.body.appendChild(modal);
            
            // Auto-save every 30 seconds
            this.docAutoSaveInterval = setInterval(() => {
                this.saveInternalDoc(docId, true);
            }, 30000);
        })
        .catch(err => {
            console.error('Error loading document:', err);
            alert('Failed to load document');
        });
},

switchDocTab(tab) {
    const editBtn = document.querySelector('.editor-tabs .tab-btn:nth-child(1)');
    const previewBtn = document.querySelector('.editor-tabs .tab-btn:nth-child(2)');
    const editor = document.getElementById('doc-content');
    const preview = document.getElementById('doc-preview');
    
    if (tab === 'edit') {
        editBtn.classList.add('active');
        previewBtn.classList.remove('active');
        editor.style.display = 'block';
        preview.style.display = 'none';
    } else {
        editBtn.classList.remove('active');
        previewBtn.classList.add('active');
        editor.style.display = 'none';
        preview.style.display = 'block';
        
        // Render markdown preview
        preview.innerHTML = this.renderMarkdown(editor.value);
    }
},

saveInternalDoc(docId, isAutoSave = false) {
    const title = document.getElementById('doc-title').value;
    const content = document.getElementById('doc-content').value || 
                   document.getElementById('doc-content').innerHTML;
    
    fetch(`/api/synergy/internal-doc/${docId}`, {
        method: 'PUT',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({ title, content })
    })
    .then(res => res.json())
    .then(data => {
        if (data.success) {
            if (!isAutoSave) {
                document.getElementById('internal-doc-modal').remove();
                if (this.docAutoSaveInterval) {
                    clearInterval(this.docAutoSaveInterval);
                }
                this.loadSessions();
            } else {
                // Show auto-save indicator
                console.log('✅ Auto-saved v' + data.version);
            }
        } else {
            alert('Failed to save: ' + data.error);
        }
    })
    .catch(err => {
        console.error('Error saving document:', err);
        if (!isAutoSave) {
            alert('Failed to save document');
        }
    });
},

exportInternalDoc(docId, target) {
    // Get document content first
    fetch(`/api/synergy/internal-doc/${docId}`)
        .then(res => res.json())
        .then(data => {
            if (!data.success) {
                alert('Failed to export: ' + data.error);
                return;
            }
            
            // Use existing export tools
            if (target === 'word') {
                // Call microsoft_word_create_document tool via agent
                this.createWordFromInternalDoc(data);
            } else if (target === 'google') {
                // Call google_docs_smart_create_from_markdown tool
                this.createGoogleDocFromInternalDoc(data);
            }
        });
},

// Update document rendering in cards
renderCardExpanded(session, priorityEmoji, statusClass, timeAgo) {
    // ... existing code ...
    
    // Documents section - check for internal docs
    const validDocuments = Array.isArray(documents) ? documents.filter(doc => doc && doc.title && doc.title.trim() !== '') : [];
    
    docsHTML = `
        <div class="card-section">
            <div class="section-title"><i class="fas fa-file-alt"></i> Documents ${validDocuments.length > 0 ? `(${validDocuments.length})` : ''}</div>
            <div class="document-list">
                ${validDocuments.length > 0 ? validDocuments.map(doc => {
                    // Handle internal docs differently
                    if (doc.type === 'internal_doc') {
                        return `
                            <div class="document-item internal-doc-item" onclick="synergyBoard.openInternalDocViewer('${doc.doc_id}', '${session.session_id}')">
                                <i class="fas fa-file-alt"></i>
                                <div class="doc-info">
                                    <span class="doc-name">${this.escapeHtml(doc.title)}</span>
                                    <span class="doc-type">Internal Document (${doc.format})</span>
                                    ${doc.preview ? `<span class="doc-preview">${this.escapeHtml(doc.preview)}</span>` : ''}
                                </div>
                                <button class="doc-link" title="Open internal document">
                                    <i class="fas fa-edit"></i>
                                </button>
                            </div>
                        `;
                    } else {
                        // External doc (existing code)
                        const typeLabels = { /* ... */ };
                        // ... existing external doc rendering ...
                    }
                }).join('') : '<div class="document-item" style="opacity: 0.6; font-style: italic;">No documents added</div>'}
            </div>
        </div>
    `;
    
    // ... rest of function ...
}
```

**CSS Styles:**

```css
/* Add to business-ai-platform-v2.html <style> section */

.internal-doc-modal {
    max-width: 1200px;
    width: 90%;
    max-height: 90vh;
}

.doc-title-input {
    border: none;
    background: transparent;
    font-size: inherit;
    font-weight: inherit;
    width: 100%;
    padding: 4px 8px;
    border-radius: 4px;
}

.doc-title-input:focus {
    background: var(--bg-tertiary);
    outline: 2px solid var(--accent-blue);
}

.doc-meta {
    display: flex;
    gap: 16px;
    font-size: 13px;
    color: var(--text-secondary);
    margin-top: 8px;
}

.doc-editor-container {
    height: 600px;
    display: flex;
    flex-direction: column;
}

.editor-tabs {
    display: flex;
    gap: 8px;
    border-bottom: 2px solid var(--border-color);
    margin-bottom: 16px;
}

.tab-btn {
    padding: 8px 16px;
    background: transparent;
    border: none;
    border-bottom: 2px solid transparent;
    cursor: pointer;
    color: var(--text-secondary);
    transition: all 0.2s;
}

.tab-btn.active {
    color: var(--accent-blue);
    border-bottom-color: var(--accent-blue);
}

.doc-editor {
    flex: 1;
    width: 100%;
    padding: 16px;
    border: 1px solid var(--border-color);
    border-radius: 8px;
    font-family: 'Monaco', 'Courier New', monospace;
    font-size: 14px;
    line-height: 1.6;
    resize: none;
}

.markdown-editor {
    background: var(--bg-secondary);
    color: var(--text-primary);
}

.doc-preview {
    flex: 1;
    padding: 16px;
    border: 1px solid var(--border-color);
    border-radius: 8px;
    background: var(--bg-primary);
    overflow-y: auto;
}

.internal-doc-item {
    cursor: pointer;
    transition: background 0.2s;
}

.internal-doc-item:hover {
    background: var(--bg-secondary);
}

.doc-preview {
    font-size: 11px;
    color: var(--text-tertiary);
    font-style: italic;
    margin-top: 4px;
    display: block;
}

.footer-left,
.footer-right {
    display: flex;
    gap: 8px;
}

.modal-footer {
    display: flex;
    justify-content: space-between;
}
```

---

## 📊 Feature Comparison Matrix

| Feature | Simple Container | OnlyOffice | Hybrid |
|---------|-----------------|------------|--------|
| **Implementation Time** | 2 hours | 2-3 days | 1 week |
| **Complexity** | Low | High | Medium |
| **AI-Friendly** | ✅ Yes | ❌ No | ✅ Yes |
| **Rich Formatting** | ⚠️ Basic | ✅ Full | ✅ Full |
| **Real-time Collab** | ❌ No | ✅ Yes | ✅ Yes |
| **Resource Usage** | < 50MB | ~1GB | ~1GB |
| **External Dependencies** | None | Docker | Docker |
| **Search/Index** | ✅ Easy | ⚠️ Complex | ⚠️ Complex |
| **Version Control** | ✅ Easy | ⚠️ Complex | ⚠️ Complex |
| **Export Quality** | ⚠️ Basic | ✅ Native | ✅ Native |
| **Offline Support** | ✅ Yes | ❌ No | ⚠️ Partial |

---

## 🎯 Final Recommendation

### Phase 1: Implement Simple Container (NOW)
- **Timeline:** 2 hours
- **Effort:** Low
- **Value:** High
- **Risk:** None

**Benefits:**
- ✅ Solves immediate AI workflow pain
- ✅ No infrastructure changes needed
- ✅ Works offline
- ✅ Easy to search and version
- ✅ AI-native (markdown)

### Phase 2: Add OnlyOffice (LATER - if needed)
- **Timeline:** 2-3 days
- **Trigger:** When users request rich formatting
- **Value:** Medium (nice-to-have)

**Use Cases:**
- Complex reports with tables/charts
- Presentations for external sharing
- Collaborative editing sessions

---

## 🚀 Quick Start (Next 30 minutes)

```bash
# 1. Create database table
python create_internal_docs_table.py

# 2. Add API endpoints to synergy_routes.py
# (Copy Phase 2 code)

# 3. Add tool definitions to synergy_tools.json
# (Copy Phase 3 code)

# 4. Add tools to synergy.py
# (Copy Phase 3 code)

# 5. Add UI modal to business-ai-platform-v2.html
# (Copy Phase 4 code)

# 6. Test with AI agent:
CHAT "Create a Synergy session called 'Test Internal Docs' and add an internal document with a project summary"
```

---

## 📝 Testing Checklist

- [ ] Database table created successfully
- [ ] API endpoints return proper responses
- [ ] AI agent can create internal doc
- [ ] Document appears in Synergy card
- [ ] Clicking document opens editor modal
- [ ] Markdown preview works
- [ ] Save updates content and version
- [ ] Auto-save works every 30 seconds
- [ ] Export to Word creates .docx file
- [ ] Export to Google Doc creates doc in Drive
- [ ] Delete removes doc from card and database

---

## 🔮 Future Enhancements (Phase 3+)

1. **Version History:**
   - Store doc snapshots on each save
   - Show timeline of changes
   - Revert to previous version

2. **AI Summarization:**
   - Tool: `synergy_summarize_internal_doc(doc_id)`
   - Generates TL;DR summary
   - Updates preview field

3. **Search Integration:**
   - Full-text search across all internal docs
   - Filter by session, date, creator
   - Highlight matches

4. **Templates:**
   - Pre-defined doc templates
   - "Meeting Notes", "Project Spec", "Status Report"
   - AI can use templates for consistency

5. **Comments/Annotations:**
   - Inline comments on specific text
   - User mentions (@john)
   - Thread discussions per doc

---

## 🎓 Key Insights

**Why Simple Wins:**
1. AI workflow = text-first (markdown natural)
2. Speed matters = instant value vs weeks of integration
3. Complexity kills = fewer moving parts = fewer bugs
4. Search matters = plain text > binary formats
5. Versioning matters = git-style diffs work on text

**When to Add OnlyOffice:**
- User explicitly requests "I need tables/charts"
- Business requirement for MS Office compatibility
- Multi-user collaboration becomes critical
- External stakeholders need polished docs

**The Rule:**
> Start with the simplest solution that solves 80% of use cases.  
> Add complexity only when users demand it with specific examples.

---

## 📌 Implementation Priority

**Must Have (Phase 1 - 2 hours):**
- ✅ Database table
- ✅ CRUD API endpoints
- ✅ AI agent tools
- ✅ Basic editor modal
- ✅ Markdown support

**Should Have (Phase 2 - 4 hours):**
- Export to Word/Google Docs
- Auto-save functionality
- Version numbering
- Preview in card

**Nice to Have (Phase 3 - 8 hours):**
- OnlyOffice integration
- Version history viewer
- Templates library
- Search integration

**Future (Phase 4 - weeks):**
- Real-time collaboration
- Comments/annotations
- AI summarization
- Advanced search

---

**Status:** Ready to implement  
**Recommendation:** Start with Phase 1 (Simple Container)  
**Next Step:** Run `python create_internal_docs_table.py`

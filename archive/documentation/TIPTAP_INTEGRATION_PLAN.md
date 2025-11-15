# TipTap Rich Text Editor Integration Plan
**Date:** November 14, 2025  
**Status:** Planning Phase  
**Current Implementation:** Basic markdown editor with textarea

---

## 📊 Current State Analysis

### ✅ What's Already Built

**Database Schema** (`synergy_internal_docs` table):
```sql
- doc_id TEXT PRIMARY KEY (format: int_doc_<timestamp>)
- session_id TEXT NOT NULL
- title TEXT NOT NULL
- content TEXT (stores markdown currently)
- format TEXT DEFAULT 'markdown'
- created_at TIMESTAMP
- updated_at TIMESTAMP
- created_by TEXT
- version INTEGER DEFAULT 1
```

**Backend API Endpoints** (AI_infrastructure/routes/synergy_routes.py):
- ✅ `POST /api/synergy/internal-doc/create` - Create document
- ✅ `GET /api/synergy/internal-doc/<doc_id>` - Retrieve document
- ✅ `PUT /api/synergy/internal-doc/<doc_id>` - Update document
- ✅ `DELETE /api/synergy/internal-doc/<doc_id>` - Delete document
- ✅ `GET /api/synergy/internal-doc/list/<session_id>` - List all docs in session

**AI Agent Tools** (tools/implementations/synergy.py):
- ✅ `synergy_create_internal_doc()` - Create doc with markdown content
- ✅ `synergy_update_internal_doc()` - Update doc content/title
- ✅ `synergy_get_internal_doc()` - Retrieve full document
- ✅ `synergy_export_internal_doc()` - Export to Word/PDF/Google Docs

**Frontend UI** (UI/business-ai-platform-v2.html):
- ✅ Modal viewer for internal documents
- ✅ Split-pane editor: Edit (textarea) + Preview (rendered markdown)
- ✅ Tab switching between edit/preview modes
- ✅ Export buttons (Word, Google Doc, PDF, Email)
- ✅ Auto-save every 30 seconds
- ✅ Version tracking display
- ✅ Copy doc_id to clipboard

### 🔴 Current Limitations

1. **Plain textarea** - No rich formatting UI (bold, italic, lists, etc.)
2. **Manual markdown** - Users must know markdown syntax
3. **Basic tables** - No visual table editor
4. **No calculations** - Can't do spreadsheet formulas
5. **Limited AI editing** - AI works with markdown only
6. **No collaboration** - No real-time editing features

---

## 🎯 TipTap Integration Goals

### Primary Objectives

1. **Replace textarea with TipTap rich text editor**
2. **Keep markdown storage format** (AI-friendly, version-controllable)
3. **Add visual formatting toolbar** (WYSIWYG interface)
4. **Support tables with visual editing**
5. **Enable spreadsheet-like calculations** (optional extension)
6. **Maintain export functionality** (Word, PDF, Google Docs)
7. **AI compatibility** - Tools can still use markdown

### Why TipTap?

✅ **Modern & Maintained** - Active development, used by Notion, GitLab  
✅ **ProseMirror-based** - Robust document model  
✅ **JSON + Markdown** - Dual format support  
✅ **Extensions** - Tables, math, code blocks, mentions  
✅ **Headless** - Full control over styling  
✅ **Collaborative** - Can add Y.js for real-time editing later  
✅ **Export-friendly** - Easy to convert to HTML/Markdown/PDF  

---

## 🏗️ Architecture Design

### Data Flow

```
User Types → TipTap Editor → ProseMirror JSON → Convert to Markdown → Save to DB
                    ↓
            Live Preview (optional)
                    ↓
            Export to: Google Docs, Word, Excel, PDF
```

### Storage Strategy

**Option A: Store Both JSON + Markdown (RECOMMENDED)**
```sql
ALTER TABLE synergy_internal_docs ADD COLUMN content_json TEXT;
-- content = markdown (for AI tools)
-- content_json = TipTap JSON (for editor)
```

**Benefits:**
- AI tools continue using markdown (no changes needed)
- TipTap loads JSON instantly (no conversion lag)
- Markdown remains human-readable in database
- Version control works on markdown diffs

**Option B: Store JSON Only, Convert On-Demand**
```sql
-- content = TipTap JSON
-- Convert to markdown when AI requests via synergy_get_internal_doc()
```

**Benefits:**
- Single source of truth
- Smaller database
- No sync issues

**Recommendation:** Use **Option A** for reliability and AI compatibility.

---

## 📦 Implementation Phases

### Phase 1: Basic TipTap Integration (2-3 hours)

**Goal:** Replace textarea with TipTap, maintain current functionality

**Tasks:**
1. Add TipTap CDN links to HTML (or npm install if using build process)
2. Initialize TipTap editor with StarterKit
3. Load/save markdown content (convert to/from TipTap JSON)
4. Keep existing toolbar buttons (bold, italic, heading, list)
5. Maintain auto-save functionality
6. Test with existing documents

**Files to Modify:**
- `UI/business-ai-platform-v2.html` - Add TipTap scripts, replace textarea
- `AI_infrastructure/routes/synergy_routes.py` - Add content_json column support

**CDN Setup:**
```html
<!-- TipTap Core + Extensions -->
<script src="https://cdn.jsdelivr.net/npm/@tiptap/core@2.1.13/dist/tiptap-core.umd.min.js"></script>
<script src="https://cdn.jsdelivr.net/npm/@tiptap/starter-kit@2.1.13/dist/tiptap-starter-kit.umd.min.js"></script>
<script src="https://cdn.jsdelivr.net/npm/@tiptap/extension-table@2.1.13/dist/tiptap-extension-table.umd.min.js"></script>
<script src="https://cdn.jsdelivr.net/npm/@tiptap/extension-table-row@2.1.13/dist/tiptap-extension-table-row.umd.min.js"></script>
<script src="https://cdn.jsdelivr.net/npm/@tiptap/extension-table-cell@2.1.13/dist/tiptap-extension-table-cell.umd.min.js"></script>
<script src="https://cdn.jsdelivr.net/npm/@tiptap/extension-table-header@2.1.13/dist/tiptap-extension-table-header.umd.min.js"></script>
```

**JavaScript Initialization:**
```javascript
const tiptapEditor = new window.TiptapCore.Editor({
    element: document.querySelector('#tiptap-container'),
    extensions: [
        window.TiptapStarterKit.StarterKit,
        window.TiptapTable.Table.configure({ resizable: true }),
        window.TiptapTableRow.TableRow,
        window.TiptapTableHeader.TableHeader,
        window.TiptapTableCell.TableCell,
    ],
    content: '', // Load from markdown
    onUpdate: ({ editor }) => {
        // Auto-save on change
        scheduleAutoSave();
    }
});

// Load existing content
function loadDocument(markdownContent) {
    tiptapEditor.commands.setContent(
        window.TiptapCore.generateHTML(markdownContent, extensions)
    );
}

// Save to backend
function saveDocument() {
    const json = tiptapEditor.getJSON();
    const markdown = window.TiptapCore.generateText(json, extensions);
    
    fetch('/api/synergy/internal-doc/update', {
        method: 'PUT',
        body: JSON.stringify({
            content: markdown,
            content_json: JSON.stringify(json)
        })
    });
}
```

---

### Phase 2: Visual Toolbar & Formatting (1-2 hours)

**Goal:** Add professional formatting toolbar

**Features:**
- Bold, Italic, Underline, Strikethrough
- Headings (H1-H6)
- Lists (bullet, numbered, checklist)
- Links
- Code blocks
- Blockquotes
- Horizontal rules
- Text alignment
- Text/background colors

**UI Design:**
```html
<div class="tiptap-toolbar">
    <button onclick="editor.chain().focus().toggleBold().run()" class="toolbar-btn" title="Bold">
        <i class="fas fa-bold"></i>
    </button>
    <button onclick="editor.chain().focus().toggleItalic().run()" class="toolbar-btn" title="Italic">
        <i class="fas fa-italic"></i>
    </button>
    <!-- ... more buttons ... -->
    <select onchange="editor.chain().focus().toggleHeading({ level: parseInt(this.value) }).run()">
        <option value="">Normal</option>
        <option value="1">Heading 1</option>
        <option value="2">Heading 2</option>
        <option value="3">Heading 3</option>
    </select>
</div>

<div id="tiptap-container" class="tiptap-editor"></div>
```

**Styling:**
```css
.tiptap-editor {
    min-height: 400px;
    padding: 20px;
    border: 1px solid var(--border-color);
    border-radius: 8px;
    background: var(--bg-secondary);
    color: var(--text-primary);
}

.tiptap-editor:focus {
    outline: none;
    border-color: var(--primary-color);
}

.tiptap-toolbar {
    display: flex;
    gap: 4px;
    padding: 8px;
    background: var(--bg-primary);
    border: 1px solid var(--border-color);
    border-radius: 8px 8px 0 0;
    flex-wrap: wrap;
}

.toolbar-btn {
    width: 32px;
    height: 32px;
    border: none;
    background: transparent;
    color: var(--text-secondary);
    cursor: pointer;
    border-radius: 4px;
    transition: all 0.2s;
}

.toolbar-btn:hover {
    background: var(--hover-bg);
    color: var(--text-primary);
}

.toolbar-btn.is-active {
    background: var(--primary-color);
    color: white;
}
```

---

### Phase 3: Table Editing with Visual UI (2-3 hours)

**Goal:** Add interactive table creation and editing

**Features:**
- Insert table with row/col selector
- Add/delete rows/columns
- Merge/split cells
- Cell background colors
- Header row styling
- Resize columns (drag handles)

**Extensions Needed:**
```javascript
import { Table } from '@tiptap/extension-table'
import { TableRow } from '@tiptap/extension-table-row'
import { TableHeader } from '@tiptap/extension-table-header'
import { TableCell } from '@tiptap/extension-table-cell'
import { TextAlign } from '@tiptap/extension-text-align'
import { Color } from '@tiptap/extension-color'
import { Highlight } from '@tiptap/extension-highlight'
```

**Table Toolbar:**
```html
<div class="table-controls" style="display: none;" id="table-controls">
    <button onclick="insertTable()"><i class="fas fa-table"></i> Insert Table</button>
    <button onclick="addRowBefore()"><i class="fas fa-plus"></i> Row Above</button>
    <button onclick="addRowAfter()"><i class="fas fa-plus"></i> Row Below</button>
    <button onclick="addColumnBefore()"><i class="fas fa-plus"></i> Column Before</button>
    <button onclick="addColumnAfter()"><i class="fas fa-plus"></i> Column After</button>
    <button onclick="deleteRow()"><i class="fas fa-trash"></i> Delete Row</button>
    <button onclick="deleteColumn()"><i class="fas fa-trash"></i> Delete Column</button>
    <button onclick="deleteTable()"><i class="fas fa-trash-alt"></i> Delete Table</button>
</div>
```

**Table Insert Dialog:**
```javascript
function showTableInsertDialog() {
    const html = `
        <div class="table-insert-dialog">
            <h4>Insert Table</h4>
            <label>Rows: <input type="number" id="table-rows" value="3" min="1" max="20"></label>
            <label>Columns: <input type="number" id="table-cols" value="3" min="1" max="10"></label>
            <div class="table-preview" id="table-preview"></div>
            <button onclick="insertTableWithSize()">Insert</button>
            <button onclick="closeTableDialog()">Cancel</button>
        </div>
    `;
    document.body.insertAdjacentHTML('beforeend', html);
}

function insertTableWithSize() {
    const rows = parseInt(document.getElementById('table-rows').value);
    const cols = parseInt(document.getElementById('table-cols').value);
    
    editor.chain().focus().insertTable({ rows, cols, withHeaderRow: true }).run();
    closeTableDialog();
}
```

---

### Phase 4: Spreadsheet Calculations (Optional - 3-4 hours)

**Goal:** Add formula support for simple calculations

**Options:**

**Option A: Use Handsontable (Full Spreadsheet)**
```html
<script src="https://cdn.jsdelivr.net/npm/handsontable/dist/handsontable.full.min.js"></script>
<link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/handsontable/dist/handsontable.full.min.css">

<script>
// Switch to spreadsheet mode
function enableSpreadsheetMode() {
    const hot = new Handsontable(container, {
        data: [['', '', ''], ['', '', '']],
        colHeaders: true,
        rowHeaders: true,
        formulas: {
            engine: HyperFormula
        },
        contextMenu: true,
        manualColumnResize: true,
        manualRowResize: true
    });
}
</script>
```

**Option B: Custom Formula Extension for TipTap**
```javascript
const FormulaCell = TableCell.extend({
    addAttributes() {
        return {
            ...this.parent?.(),
            formula: {
                default: null,
            },
            computed: {
                default: null,
            }
        }
    },
    
    addCommands() {
        return {
            setFormula: (formula) => ({ commands }) => {
                return commands.updateAttributes('tableCell', { formula });
            }
        }
    }
});

// Calculate formulas
function calculateTableFormulas() {
    const tables = editor.getJSON().content.filter(n => n.type === 'table');
    tables.forEach(table => {
        table.content.forEach(row => {
            row.content.forEach(cell => {
                if (cell.attrs.formula) {
                    const result = evaluateFormula(cell.attrs.formula, table);
                    cell.attrs.computed = result;
                }
            });
        });
    });
}

function evaluateFormula(formula, table) {
    // Simple formula parser
    // =SUM(A1:A5), =A1+B1, =COUNT(B:B), etc.
    // Use a library like formulajs or write custom parser
}
```

**Recommendation:** Start with **Option B** (simpler) unless users explicitly need full Excel-like features.

---

### Phase 5: Export Converters (2-3 hours)

**Goal:** Convert TipTap JSON to various formats

**Backend Converter Module:**
```python
# AI_infrastructure/converters/tiptap_converter.py

import json
from typing import Dict, Any
from docx import Document
from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH

class TipTapConverter:
    """Convert TipTap JSON to Word, PDF, Google Docs, Markdown"""
    
    @staticmethod
    def to_markdown(tiptap_json: Dict) -> str:
        """
        Convert TipTap JSON to Markdown
        
        Handles:
        - Headings, paragraphs, lists
        - Bold, italic, code
        - Tables (markdown table syntax)
        - Links, images
        """
        content = tiptap_json.get('content', [])
        return TipTapConverter._nodes_to_markdown(content)
    
    @staticmethod
    def _nodes_to_markdown(nodes: list) -> str:
        md = []
        for node in nodes:
            node_type = node.get('type')
            
            if node_type == 'paragraph':
                text = TipTapConverter._marks_to_markdown(node.get('content', []))
                md.append(text + '\n')
            
            elif node_type == 'heading':
                level = node.get('attrs', {}).get('level', 1)
                text = TipTapConverter._marks_to_markdown(node.get('content', []))
                md.append(f"{'#' * level} {text}\n")
            
            elif node_type == 'bulletList':
                for item in node.get('content', []):
                    text = TipTapConverter._marks_to_markdown(item.get('content', []))
                    md.append(f"- {text}\n")
            
            elif node_type == 'orderedList':
                for i, item in enumerate(node.get('content', []), 1):
                    text = TipTapConverter._marks_to_markdown(item.get('content', []))
                    md.append(f"{i}. {text}\n")
            
            elif node_type == 'table':
                md.append(TipTapConverter._table_to_markdown(node))
            
            elif node_type == 'codeBlock':
                lang = node.get('attrs', {}).get('language', '')
                code = node.get('content', [{}])[0].get('text', '')
                md.append(f"```{lang}\n{code}\n```\n")
        
        return '\n'.join(md)
    
    @staticmethod
    def _marks_to_markdown(content: list) -> str:
        """Convert text with marks (bold, italic) to markdown"""
        text = ''
        for node in content:
            if node.get('type') == 'text':
                t = node.get('text', '')
                marks = node.get('marks', [])
                
                for mark in marks:
                    mark_type = mark.get('type')
                    if mark_type == 'bold':
                        t = f"**{t}**"
                    elif mark_type == 'italic':
                        t = f"*{t}*"
                    elif mark_type == 'code':
                        t = f"`{t}`"
                    elif mark_type == 'link':
                        href = mark.get('attrs', {}).get('href', '')
                        t = f"[{t}]({href})"
                
                text += t
        return text
    
    @staticmethod
    def _table_to_markdown(table_node: Dict) -> str:
        """Convert TipTap table to markdown table"""
        rows = table_node.get('content', [])
        md_rows = []
        
        for row_idx, row in enumerate(rows):
            cells = row.get('content', [])
            cell_texts = []
            
            for cell in cells:
                text = TipTapConverter._marks_to_markdown(cell.get('content', []))
                cell_texts.append(text.strip())
            
            md_rows.append('| ' + ' | '.join(cell_texts) + ' |')
            
            # Add separator after first row (header)
            if row_idx == 0:
                md_rows.append('| ' + ' | '.join(['---'] * len(cell_texts)) + ' |')
        
        return '\n'.join(md_rows) + '\n'
    
    @staticmethod
    def from_markdown(markdown: str) -> Dict:
        """Convert Markdown to TipTap JSON"""
        # Use a markdown parser like markdown-it or mistune
        # Convert AST to TipTap JSON format
        pass
    
    @staticmethod
    def to_word_docx(tiptap_json: Dict, title: str) -> bytes:
        """
        Create Word .docx from TipTap JSON
        Returns: DOCX file as bytes
        """
        doc = Document()
        doc.add_heading(title, 0)
        
        content = tiptap_json.get('content', [])
        TipTapConverter._nodes_to_docx(content, doc)
        
        # Return as bytes
        from io import BytesIO
        buffer = BytesIO()
        doc.save(buffer)
        buffer.seek(0)
        return buffer.getvalue()
    
    @staticmethod
    def _nodes_to_docx(nodes: list, doc: Document):
        """Convert TipTap nodes to Word document"""
        for node in nodes:
            node_type = node.get('type')
            
            if node_type == 'heading':
                level = node.get('attrs', {}).get('level', 1)
                text = TipTapConverter._extract_text(node)
                doc.add_heading(text, level)
            
            elif node_type == 'paragraph':
                text = TipTapConverter._extract_text(node)
                p = doc.add_paragraph(text)
            
            elif node_type == 'table':
                TipTapConverter._table_to_docx(node, doc)
    
    @staticmethod
    def _table_to_docx(table_node: Dict, doc: Document):
        """Convert TipTap table to Word table"""
        rows = table_node.get('content', [])
        if not rows:
            return
        
        # Count columns from first row
        cols = len(rows[0].get('content', []))
        
        table = doc.add_table(rows=len(rows), cols=cols)
        table.style = 'Light Grid Accent 1'
        
        for row_idx, row in enumerate(rows):
            cells = row.get('content', [])
            for col_idx, cell in enumerate(cells):
                text = TipTapConverter._extract_text(cell)
                table.rows[row_idx].cells[col_idx].text = text
    
    @staticmethod
    def to_google_doc(tiptap_json: Dict, title: str, user_id: int) -> str:
        """
        Create Google Doc from TipTap JSON
        Returns: Google Doc URL
        """
        # Convert to markdown first
        markdown = TipTapConverter.to_markdown(tiptap_json)
        
        # Use existing google_docs_smart_create_from_markdown tool
        from tools.implementations.google_workspace import google_docs_smart_create_from_markdown
        result = google_docs_smart_create_from_markdown(
            title=title,
            markdown_content=markdown,
            _user_id=user_id
        )
        
        return result.get('url')
```

---

### Phase 6: AI Agent Integration (1 hour)

**Goal:** Update AI tools to work with TipTap JSON

**Changes to `synergy.py`:**
```python
def synergy_create_internal_doc(
    session_id: str,
    title: str,
    content: str,  # AI provides markdown
    format: str = "markdown",
    **kwargs
) -> Dict[str, Any]:
    """
    AI creates document with markdown content.
    Backend converts to TipTap JSON automatically.
    """
    # Convert markdown to TipTap JSON on server
    from AI_infrastructure.converters.tiptap_converter import TipTapConverter
    
    try:
        tiptap_json = TipTapConverter.from_markdown(content)
    except:
        # Fallback to plain text if conversion fails
        tiptap_json = {
            "type": "doc",
            "content": [{
                "type": "paragraph",
                "content": [{"type": "text", "text": content}]
            }]
        }
    
    response = requests.post(
        f'{SYNERGY_API_BASE}/internal-doc/create',
        json={
            'session_id': session_id,
            'title': title,
            'content': content,  # markdown for AI
            'content_json': json.dumps(tiptap_json),  # JSON for TipTap
            'format': format
        }
    )
    
    return response.json()
```

**No changes needed for:**
- `synergy_get_internal_doc()` - Still returns markdown in `content` field
- `synergy_update_internal_doc()` - AI sends markdown, backend converts

---

## 🎨 UI/UX Enhancements

### Dark Theme Styling

```css
/* TipTap Dark Theme */
.ProseMirror {
    background: var(--bg-secondary);
    color: var(--text-primary);
    padding: 20px;
    min-height: 400px;
}

.ProseMirror h1 {
    font-size: 2em;
    font-weight: 600;
    margin-top: 1em;
    margin-bottom: 0.5em;
    color: var(--text-primary);
}

.ProseMirror h2 {
    font-size: 1.5em;
    font-weight: 600;
    margin-top: 0.8em;
    margin-bottom: 0.4em;
    color: var(--text-primary);
}

.ProseMirror table {
    border-collapse: collapse;
    width: 100%;
    margin: 1em 0;
}

.ProseMirror th,
.ProseMirror td {
    border: 1px solid var(--border-color);
    padding: 8px 12px;
    text-align: left;
}

.ProseMirror th {
    background: var(--bg-tertiary);
    font-weight: 600;
}

.ProseMirror tr:hover {
    background: var(--hover-bg);
}

.ProseMirror code {
    background: var(--bg-tertiary);
    padding: 2px 6px;
    border-radius: 4px;
    font-family: 'Courier New', monospace;
    font-size: 0.9em;
}

.ProseMirror pre {
    background: var(--bg-tertiary);
    padding: 16px;
    border-radius: 8px;
    overflow-x: auto;
}

.ProseMirror blockquote {
    border-left: 4px solid var(--primary-color);
    padding-left: 16px;
    margin-left: 0;
    font-style: italic;
    color: var(--text-secondary);
}

.ProseMirror a {
    color: var(--primary-color);
    text-decoration: none;
}

.ProseMirror a:hover {
    text-decoration: underline;
}

/* Placeholder */
.ProseMirror p.is-editor-empty:first-child::before {
    content: attr(data-placeholder);
    float: left;
    color: var(--text-tertiary);
    pointer-events: none;
    height: 0;
}

/* Selection */
.ProseMirror ::selection {
    background: rgba(79, 108, 255, 0.3);
}

/* Table cell selection */
.ProseMirror .selectedCell {
    background: rgba(79, 108, 255, 0.2);
}

/* Table controls */
.tableWrapper {
    position: relative;
    margin: 1em 0;
}

.tableWrapper .controls {
    position: absolute;
    top: -30px;
    left: 0;
    display: flex;
    gap: 4px;
    opacity: 0;
    transition: opacity 0.2s;
}

.tableWrapper:hover .controls {
    opacity: 1;
}
```

### Mobile Responsive Design

```css
@media (max-width: 768px) {
    .tiptap-toolbar {
        flex-wrap: wrap;
    }
    
    .tiptap-editor {
        min-height: 300px;
        padding: 12px;
    }
    
    .ProseMirror table {
        font-size: 0.9em;
    }
    
    .ProseMirror th,
    .ProseMirror td {
        padding: 6px 8px;
    }
}
```

---

## 🧪 Testing Strategy

### Test Cases

1. **Create Document** - AI creates doc with markdown, opens in TipTap
2. **Edit Document** - User types, formats text, adds tables
3. **Auto-Save** - Changes save every 30 seconds
4. **Version Tracking** - Version increments on save
5. **Export to Word** - TipTap JSON → DOCX download
6. **Export to Google Doc** - TipTap JSON → Markdown → Google Doc
7. **AI Read Document** - AI calls synergy_get_internal_doc(), gets markdown
8. **AI Update Document** - AI sends markdown, backend converts to JSON
9. **Table Editing** - Insert, add rows/cols, delete, merge cells
10. **Formulas (if enabled)** - =SUM(A1:A5) calculates correctly

### Test Script

```python
# test_tiptap_integration.py

import requests
import json

BASE_URL = 'http://localhost:5001'

def test_full_workflow():
    print("=== TipTap Integration Test ===\n")
    
    # 1. Create session
    session_resp = requests.post(f"{BASE_URL}/api/synergy/create", json={
        "title": "TipTap Test Session",
        "description": "Testing rich text editor"
    })
    session_id = session_resp.json()['session_id']
    print(f"✅ Session created: {session_id}")
    
    # 2. AI creates document with markdown
    markdown_content = """
# Project Requirements

## Overview
This is a **bold** statement with *italic* text.

## Features
- Feature A
- Feature B
- Feature C

## Table
| Name | Status | Priority |
|------|--------|----------|
| Task 1 | Done | High |
| Task 2 | In Progress | Medium |

## Code Example
```python
def hello():
    print("Hello, World!")
```
"""
    
    doc_resp = requests.post(f"{BASE_URL}/api/synergy/internal-doc/create", json={
        "session_id": session_id,
        "title": "Requirements Doc",
        "content": markdown_content,
        "format": "markdown"
    })
    doc_id = doc_resp.json()['doc_id']
    print(f"✅ Document created: {doc_id}")
    
    # 3. Retrieve document (should have content_json)
    get_resp = requests.get(f"{BASE_URL}/api/synergy/internal-doc/{doc_id}")
    doc_data = get_resp.json()
    
    assert 'content_json' in doc_data, "Missing content_json field"
    tiptap_json = json.loads(doc_data['content_json'])
    assert tiptap_json['type'] == 'doc', "Invalid TipTap JSON structure"
    print(f"✅ TipTap JSON structure validated")
    
    # 4. Update document (markdown)
    update_resp = requests.put(f"{BASE_URL}/api/synergy/internal-doc/{doc_id}", json={
        "content": "# Updated Title\n\nNew content here."
    })
    assert update_resp.json()['version'] == 2
    print(f"✅ Document updated (version 2)")
    
    # 5. Export to Word
    export_resp = requests.post(f"{BASE_URL}/api/synergy/internal-doc/{doc_id}/export/word")
    assert export_resp.status_code == 200
    print(f"✅ Exported to Word (file size: {len(export_resp.content)} bytes)")
    
    print("\n🎉 ALL TESTS PASSED!")

if __name__ == '__main__':
    test_full_workflow()
```

---

## 📈 Performance Considerations

### Optimization Strategies

1. **Lazy Load Extensions** - Only load table/formula extensions when needed
2. **Debounce Auto-Save** - Wait 2 seconds after typing stops before saving
3. **Virtual Scrolling** - For very long documents (>10,000 words)
4. **Web Workers** - Convert markdown↔JSON in background thread
5. **Compression** - Gzip content_json in database (SQLite compression)

### Bundle Size

**CDN Approach (Recommended for now):**
- TipTap Core: ~150KB
- StarterKit: ~80KB
- Table Extensions: ~40KB
- **Total: ~270KB** (gzipped: ~90KB)

**NPM + Build Approach (Future):**
- Tree-shake unused extensions
- Bundle with Rollup/Webpack
- Can reduce to ~150KB total

---

## 🚀 Deployment Checklist

### Before Going Live

- [ ] Database migration: Add `content_json` column
- [ ] Update all existing documents: Convert markdown → TipTap JSON
- [ ] Test backward compatibility: Old documents still open
- [ ] Update AI agent tools: Test markdown input/output
- [ ] Export functionality: Test Word, PDF, Google Doc
- [ ] Auto-save: Verify no data loss
- [ ] Error handling: Graceful degradation if TipTap fails
- [ ] Dark theme: Verify all colors work
- [ ] Mobile testing: Touch interactions work
- [ ] Performance: Test with 100-page document
- [ ] Documentation: Update user guide

### Migration Script

```python
# migrate_to_tiptap.py

import sqlite3
import json
from AI_infrastructure.converters.tiptap_converter import TipTapConverter

conn = sqlite3.connect('data/synergy_sessions.db')
cursor = conn.cursor()

# Add new column
cursor.execute('ALTER TABLE synergy_internal_docs ADD COLUMN content_json TEXT')

# Convert all existing documents
cursor.execute('SELECT doc_id, content FROM synergy_internal_docs')
docs = cursor.fetchall()

for doc_id, content in docs:
    try:
        tiptap_json = TipTapConverter.from_markdown(content)
        cursor.execute(
            'UPDATE synergy_internal_docs SET content_json = ? WHERE doc_id = ?',
            (json.dumps(tiptap_json), doc_id)
        )
        print(f"✅ Migrated {doc_id}")
    except Exception as e:
        print(f"❌ Failed to migrate {doc_id}: {e}")

conn.commit()
conn.close()
print("\n🎉 Migration complete!")
```

---

## 📝 Next Steps

### Immediate Actions (Today)

1. **Review this plan** - Confirm approach with team
2. **Choose storage strategy** - Option A (JSON + Markdown) or Option B (JSON only)
3. **Set up development** - Install TipTap via CDN or npm
4. **Phase 1 implementation** - Replace textarea with basic TipTap

### Week 1 Goals

- Complete Phases 1-2 (basic editor + toolbar)
- Test with existing Synergy sessions
- Gather user feedback

### Week 2 Goals

- Complete Phase 3 (table editing)
- Implement export converters
- Deploy to staging

### Future Enhancements

- Real-time collaboration (Y.js integration)
- Comments/suggestions (like Google Docs)
- @mentions for team members
- Version history viewer
- Template library
- AI writing assistant (inline suggestions)

---

## 🔗 Resources

### Documentation
- [TipTap Docs](https://tiptap.dev/)
- [ProseMirror Guide](https://prosemirror.net/docs/guide/)
- [TipTap Examples](https://tiptap.dev/examples)

### Extensions
- [TipTap Extensions](https://tiptap.dev/extensions)
- [Table Extension](https://tiptap.dev/api/nodes/table)
- [Collaboration Extension](https://tiptap.dev/guide/collaborative-editing)

### Alternatives Considered
- Quill.js - Good, but less extensible
- Draft.js - React-only, outdated
- Slate.js - Complex, steeper learning curve
- CKEditor - Bloated, not modern
- ProseMirror (raw) - Too low-level

---

**End of Plan** 🎯

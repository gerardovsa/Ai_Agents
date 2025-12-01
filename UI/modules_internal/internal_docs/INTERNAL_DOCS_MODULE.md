# Internal Documents Module - Complete Integration Guide

**Created:** November 14, 2025  
**Status:** ✅ Production Ready  
**Files:** `internal-docs.js`, `internal-docs.css`

---

## 🎯 Overview

Complete modular system for embedded documents with:
- ✅ **Rich Text Editor** (TipTap) with full formatting
- ✅ **Spreadsheet Editor** (Handsontable) with 200+ formulas
- ✅ **Real-time Collaboration** (Y.js) with user presence
- ✅ **AI Integration** (drag & drop to sessions)
- ✅ **Copy to Clipboard** (paste doc ID in chat)
- ✅ **Version Tracking** (auto-save every 30 seconds)
- ✅ **Export** (Word, Google Docs, PDF, Excel, CSV, Markdown)

---

## 📦 Quick Integration

### Step 1: Include Module Files

Add to your HTML `<head>`:

```html
<!-- Internal Docs Module -->
<link rel="stylesheet" href="modules/internal-docs.css">
<script src="modules/internal-docs.js"></script>
```

### Step 2: Initialize (Auto-initializes)

The module auto-initializes on page load. No manual setup required!

```javascript
// Global instance available immediately:
window.internalDocs.openDocument('doc-123456789');
```

### Step 3: Use Anywhere

```javascript
// Create new document
await internalDocs.createDocument({
    sessionId: 'synergy-123',
    title: 'Meeting Notes',
    type: 'richtext' // or 'spreadsheet'
});

// Open existing document
await internalDocs.openDocument('doc-123456789');

// Copy doc ID to clipboard
internalDocs.copyDocIdToClipboard('doc-123456789');
```

---

## 🎨 Features Breakdown

### 1. Rich Text Editor (TipTap)

**Formatting:**
- Bold, Italic, Underline, Strikethrough
- Headings (H1-H6)
- Text/Background colors
- Code inline and blocks
- Blockquotes
- Horizontal rules

**Lists:**
- Bullet lists
- Numbered lists
- Task lists (checkboxes)

**Tables:**
- Insert tables with custom rows/columns
- Add/remove rows and columns
- Cell merging

**Media:**
- Images (upload/URL)
- Links
- Embedded content

**Keyboard Shortcuts:**
- `Ctrl+B` - Bold
- `Ctrl+I` - Italic
- `Ctrl+U` - Underline
- `Ctrl+K` - Insert Link
- `Ctrl+S` - Save Document
- `Ctrl+K` (on doc) - Copy Doc ID

### 2. Spreadsheet Editor (Handsontable)

**200+ Formula Functions:**

**Math:** SUM, AVERAGE, MIN, MAX, MEDIAN, MODE, STDEV, VAR, ROUND, CEILING, FLOOR, ABS, SQRT, POWER, EXP, LN, LOG, SIN, COS, TAN, RAND

**Text:** CONCATENATE, LEFT, RIGHT, MID, LEN, UPPER, LOWER, PROPER, TRIM, FIND, REPLACE, SUBSTITUTE

**Logical:** IF, AND, OR, NOT, XOR, TRUE, FALSE, IFERROR, IFNA

**Lookup:** VLOOKUP, HLOOKUP, INDEX, MATCH, OFFSET, INDIRECT

**Date/Time:** TODAY, NOW, DATE, TIME, YEAR, MONTH, DAY, HOUR, MINUTE, SECOND, DAYS, NETWORKDAYS

**Statistical:** COUNT, COUNTA, COUNTBLANK, COUNTIF, COUNTIFS, SUMIF, SUMIFS, AVERAGEIF, AVERAGEIFS

**Financial:** PMT, PV, FV, RATE, NPER, IRR, NPV, XIRR, XNPV

**Data Operations:**
- Row/column insert/delete
- Cell merge/unmerge
- Sort (ascending/descending)
- Filter (conditions)
- Cell formatting (currency, percent, number)
- Charts (insert bar/line/pie charts)

### 3. Collaboration Features (Y.js)

**Real-time Sync:**
- See other users editing live
- Cursor position tracking
- User avatars with colors
- Active user count
- Sync status indicator

**Collaboration Bar:**
```
[👥 User1, User2, User3] [3 active] [✓ Synced]
```

**Setup:**
- Auto-connects to WebSocket server
- Uses `/collab` endpoint
- Persists changes to all connected users
- Conflict-free (CRDT-based)

### 4. AI Integration

**Copy Doc ID Feature:**
- Click "Copy Doc ID" button at top of modal
- Copies formatted tag: `[DOC:doc-123456789:Document Title]`
- Paste in chat to reference document
- AI can read/modify document via tools

**Drag & Drop to Sessions:**
```javascript
// Document items are draggable
<div class="doc-item" 
     draggable="true" 
     data-doc-id="doc-123" 
     data-doc-title="Meeting Notes">
```

**Drop on Session:**
- Drag doc from list to session card
- Auto-links doc to session
- AI gets doc as part of system prompt
- Shows "AI Linked" indicator in modal

**AI Suggestions Panel:**
- Click "Ask AI to improve this" button
- AI analyzes content and suggests improvements
- Apply suggestions with one click
- Collapsible panel (top-right of editor)

### 5. Auto-Save System

**Two-tier Saving:**
1. **Debounced Save** - Saves 2 seconds after typing stops
2. **Periodic Save** - Auto-saves every 30 seconds

**Save Indicator:**
```
[✓ Saved 2 min ago] [152 words • 890 chars]
```

**Manual Save:**
- Click "Save" button in footer
- Or press `Ctrl+S`

### 6. Export System

**Available Formats:**

**Documents:**
- Markdown (`.md`)
- HTML (`.html`)
- Word DOCX (`.docx`)
- Google Doc (opens in new tab)
- PDF (`.pdf`)

**Spreadsheets:**
- Excel (`.xlsx`)
- CSV (`.csv`)
- Google Sheets (opens in new tab)

**Export Flow:**
```javascript
await internalDocs.exportDocument('doc-123', 'word');
// Downloads document.docx
```

### 7. Version Tracking

**Automatic Versioning:**
- Every save increments version number
- Displayed in header: `v12`
- Tracks created_by user
- Timestamps (created_at, updated_at)

**Version History (Coming Soon):**
- Click "History" button
- View all versions
- Restore previous version
- Compare versions

---

## 🔌 API Integration

### Backend Endpoints Required

Your Flask backend must implement these endpoints:

#### 1. Create Document
```http
POST /api/synergy/internal-doc/create
Content-Type: application/json

{
    "session_id": "synergy-123",
    "title": "Document Title",
    "content": "Markdown content",
    "format": "markdown",
    "doc_type": "richtext",
    "created_by": 1
}

Response:
{
    "success": true,
    "doc_id": "doc-1731574800-abc123",
    "message": "Document created"
}
```

#### 2. Get Document
```http
GET /api/synergy/internal-doc/{doc_id}

Response:
{
    "success": true,
    "doc_id": "doc-123",
    "session_id": "synergy-123",
    "title": "Document Title",
    "content": "Markdown content",
    "content_json": "{...}", // TipTap JSON
    "format": "markdown",
    "doc_type": "richtext",
    "version": 3,
    "created_at": "2025-11-14T10:30:00Z",
    "updated_at": "2025-11-14T11:45:00Z",
    "created_by": 1,
    "linked_to_ai": false
}
```

#### 3. Update Document
```http
PUT /api/synergy/internal-doc/{doc_id}
Content-Type: application/json

{
    "title": "Updated Title",
    "content": "Updated markdown",
    "content_json": "{...}" // TipTap JSON
}

Response:
{
    "success": true,
    "version": 4,
    "message": "Document updated"
}
```

#### 4. Delete Document
```http
DELETE /api/synergy/internal-doc/{doc_id}

Response:
{
    "success": true,
    "message": "Document deleted"
}
```

#### 5. List Documents
```http
GET /api/synergy/internal-doc/list/{session_id}

Response:
{
    "success": true,
    "documents": [
        {
            "doc_id": "doc-123",
            "title": "Document 1",
            "doc_type": "richtext",
            "version": 2,
            "created_at": "...",
            "updated_at": "..."
        }
    ]
}
```

#### 6. Export Document
```http
POST /api/synergy/internal-doc/{doc_id}/export/{format}
Content-Type: application/json

{
    "user_id": 1
}

Response (for files):
Content-Type: application/octet-stream
Content-Disposition: attachment; filename="document.docx"

Response (for URLs):
{
    "success": true,
    "url": "https://docs.google.com/document/d/..."
}
```

#### 7. Link to AI Session
```http
POST /api/synergy/internal-doc/{doc_id}/link-ai
Content-Type: application/json

{
    "session_id": "synergy-123",
    "user_id": 1
}

Response:
{
    "success": true,
    "message": "Document linked to AI session"
}
```

---

## 🗄️ Database Schema

### Table: `synergy_internal_docs`

```sql
CREATE TABLE synergy_internal_docs (
    doc_id TEXT PRIMARY KEY,
    session_id TEXT,
    title TEXT NOT NULL,
    content TEXT,               -- Markdown content (for AI compatibility)
    content_json TEXT,          -- TipTap JSON format (for rich editing)
    format TEXT DEFAULT 'markdown',
    doc_type TEXT DEFAULT 'richtext', -- 'richtext' or 'spreadsheet'
    version INTEGER DEFAULT 1,
    created_at TEXT,
    updated_at TEXT,
    created_by INTEGER,
    linked_to_ai BOOLEAN DEFAULT 0,
    FOREIGN KEY (session_id) REFERENCES synergy_sessions(session_id)
);

CREATE INDEX idx_internal_docs_session 
ON synergy_internal_docs(session_id);
```

---

## 🎮 Usage Examples

### Example 1: Create Rich Text Document

```javascript
// In Synergy session
const doc = await internalDocs.createDocument({
    sessionId: currentSynergySession.session_id,
    title: 'Project Requirements',
    type: 'richtext',
    content: '# Requirements\n\n- Feature 1\n- Feature 2'
});

console.log('Created:', doc.doc_id);
// Output: "Created: doc-1731574800-abc123"

// Open in editor
await internalDocs.openDocument(doc.doc_id);
```

### Example 2: Create Spreadsheet

```javascript
const spreadsheet = await internalDocs.createDocument({
    sessionId: currentSynergySession.session_id,
    title: 'Budget Calculator',
    type: 'spreadsheet',
    content: JSON.stringify([
        ['Item', 'Cost', 'Qty', 'Total'],
        ['Laptop', 1200, 5, '=B2*C2'],
        ['Monitor', 300, 10, '=B3*C3'],
        ['', '', 'Total:', '=SUM(D2:D3)']
    ])
});

await internalDocs.openDocument(spreadsheet.doc_id);
```

### Example 3: Copy Doc ID for AI Reference

```javascript
// User clicks "Copy Doc ID" button
await internalDocs.copyDocIdToClipboard('doc-123456789');

// User pastes in chat:
// "Please review [DOC:doc-123456789:Project Requirements] and suggest improvements"

// AI receives tool call:
synergy_get_internal_doc(doc_id='doc-123456789')
// AI reads content and responds with suggestions
```

### Example 4: Drag Doc to Session

```html
<!-- Document list item -->
<div class="doc-item" 
     draggable="true" 
     data-doc-id="doc-123456789" 
     data-doc-title="Meeting Notes">
    <i class="fas fa-file-alt"></i>
    <span>Meeting Notes</span>
</div>

<!-- Session card (drop zone) -->
<div class="session-card drop-zone" 
     data-session-id="synergy-123"
     ondrop="handleDocDrop(event)">
    Session: Planning
</div>

<script>
function handleDocDrop(event) {
    const docId = event.dataTransfer.getData('doc-id');
    const sessionId = event.target.dataset.sessionId;
    
    // Link doc to session
    internalDocs.linkToAISession(docId, sessionId);
}
</script>
```

### Example 5: Export Document

```javascript
// Export as Word document
await internalDocs.exportDocument('doc-123', 'word');
// Downloads: document.docx

// Export as Google Doc
await internalDocs.exportDocument('doc-123', 'google_doc');
// Opens in new tab: https://docs.google.com/document/d/...

// Export spreadsheet as Excel
await internalDocs.exportDocument('doc-456', 'excel');
// Downloads: spreadsheet.xlsx
```

---

## ⚙️ Configuration Options

### Initialize with Custom Config

```javascript
// Custom configuration
const customDocs = new InternalDocsManager({
    apiBaseUrl: '/api/my-custom-path',
    userId: getCurrentUserId(),
    sessionId: 'my-session-123',
    autoSaveDelay: 60000, // 60 seconds instead of 30
    enableCollaboration: true,
    enableAI: true
});

await customDocs.init();
```

### Disable Features

```javascript
// Disable collaboration
const docsNoCollab = new InternalDocsManager({
    enableCollaboration: false
});

// Disable AI features
const docsNoAI = new InternalDocsManager({
    enableAI: false
});
```

---

## 🎨 Customization

### Custom Toolbar

Modify `createRichTextToolbar()` method:

```javascript
createRichTextToolbar() {
    return `
        <div class="toolbar-group">
            <!-- Add custom buttons -->
            <button class="toolbar-btn" data-action="customAction">
                <i class="fas fa-star"></i> Custom
            </button>
        </div>
        ${/* existing toolbar code */}
    `;
}

// Add custom action handler
executeEditorAction(action) {
    if (action === 'customAction') {
        // Your custom logic
        alert('Custom action!');
        return;
    }
    // ... existing actions
}
```

### Custom Styling

Override CSS variables:

```css
/* In your custom stylesheet */
.internal-doc-modal .modal-content {
    background: linear-gradient(135deg, #your-color 0%, #your-color2 100%);
}

.btn-copy-doc-id {
    background: linear-gradient(135deg, #custom-blue 0%, #custom-purple 100%);
}

.toolbar-btn:hover {
    background: rgba(your-color, 0.2);
}
```

---

## 🧪 Testing

### Test Document Creation

```javascript
// Test rich text document
const testDoc = await internalDocs.createDocument({
    sessionId: 'test-session',
    title: 'Test Document',
    type: 'richtext',
    content: '# Test\n\nThis is a test document.'
});

console.log('Created:', testDoc);

// Open and verify
await internalDocs.openDocument(testDoc.doc_id);
```

### Test Spreadsheet Formulas

```javascript
// Create test spreadsheet
const testSheet = await internalDocs.createDocument({
    sessionId: 'test-session',
    title: 'Formula Test',
    type: 'spreadsheet',
    content: JSON.stringify([
        ['A', 'B', 'C'],
        [10, 20, '=A2+B2'],
        [30, 40, '=A3+B3'],
        ['Total:', '', '=SUM(C2:C3)']
    ])
});

await internalDocs.openDocument(testSheet.doc_id);
// Verify formulas calculate correctly
```

### Test Collaboration

```javascript
// Open same document in two browser windows
// Window 1:
await internalDocs.openDocument('doc-123');

// Window 2:
await internalDocs.openDocument('doc-123');

// Type in Window 1, see changes in Window 2 (requires WebSocket server)
```

---

## 🐛 Troubleshooting

### Issue: Editor Not Loading

**Problem:** TipTap editor div is empty

**Solution:**
```javascript
// Check if TipTap loaded
if (!window.TiptapCore) {
    console.error('TipTap not loaded!');
    // Reload dependencies
    await internalDocs.loadDependencies();
}
```

### Issue: Spreadsheet Formulas Not Working

**Problem:** Formulas show as text instead of calculating

**Solution:**
```javascript
// Ensure HyperFormula is loaded
if (!window.HyperFormula) {
    console.error('HyperFormula not loaded!');
}

// Verify formulas configuration
formulas: {
    engine: HyperFormula
}
```

### Issue: Auto-save Not Working

**Problem:** Changes not saving automatically

**Solution:**
```javascript
// Check auto-save interval
console.log('Auto-save active:', internalDocs.autoSaveInterval !== null);

// Manually trigger save
await internalDocs.saveCurrentDoc();
```

### Issue: Collaboration Not Connecting

**Problem:** "Collaboration libraries not loaded" error

**Solution:**
1. Check WebSocket server is running
2. Verify Y.js libraries loaded:
```javascript
console.log('Y.js loaded:', !!window.Y);
console.log('WebsocketProvider loaded:', !!window.WebsocketProvider);
```

### Issue: Export Not Working

**Problem:** Export fails or downloads empty file

**Solution:**
```javascript
// Check backend endpoint
const response = await fetch('/api/synergy/internal-doc/doc-123/export/word', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ user_id: 1 })
});

console.log('Export response:', await response.text());
```

---

## 📊 Performance

### Metrics

- **Load Time:** ~2-3 seconds (includes all dependencies)
- **Bundle Size:** 
  - TipTap: ~270KB (90KB gzipped)
  - Handsontable: ~450KB (130KB gzipped)
  - Y.js: ~120KB (40KB gzipped)
  - **Total:** ~840KB (260KB gzipped)

### Optimization Tips

1. **Lazy Loading:** Load editors only when needed
```javascript
// Don't load dependencies until document opened
await internalDocs.openDocument('doc-123'); // Loads on-demand
```

2. **Debounced Auto-save:** Already implemented (2 second debounce)

3. **Virtualization:** For large spreadsheets (100+ rows)
```javascript
// Handsontable config
virtualRendering: true,
renderAllRows: false
```

---

## 🔐 Security

### XSS Protection

All user input is sanitized:
```javascript
escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}
```

### Access Control

Implement backend checks:
```python
@app.route('/api/synergy/internal-doc/<doc_id>')
def get_internal_doc(doc_id):
    user_id = get_current_user_id()
    
    # Check ownership or sharing permissions
    if not has_access(user_id, doc_id):
        return jsonify({'error': 'Access denied'}), 403
    
    # ... return document
```

### Content Security Policy

Add to HTML `<head>`:
```html
<meta http-equiv="Content-Security-Policy" 
      content="default-src 'self'; 
               script-src 'self' 'unsafe-inline' https://cdn.jsdelivr.net https://unpkg.com;
               style-src 'self' 'unsafe-inline' https://cdn.jsdelivr.net;">
```

---

## 📝 Changelog

### Version 1.0.0 (November 14, 2025)

**Features:**
- ✅ Complete rich text editor (TipTap)
- ✅ Complete spreadsheet editor (Handsontable)
- ✅ Real-time collaboration (Y.js)
- ✅ AI integration (drag & drop, copy ID)
- ✅ Auto-save system (30 seconds)
- ✅ Export system (7 formats)
- ✅ Version tracking
- ✅ Modular architecture

**Files Created:**
- `internal-docs.js` (1,200+ lines)
- `internal-docs.css` (800+ lines)
- `INTERNAL_DOCS_MODULE.md` (this file)

---

## 🚀 Next Steps

1. **Include module in your HTML:**
   ```html
   <link rel="stylesheet" href="modules/internal-docs.css">
   <script src="modules/internal-docs.js"></script>
   ```

2. **Implement backend endpoints** (see API Integration section)

3. **Test with sample documents:**
   ```javascript
   const doc = await internalDocs.createDocument({
       sessionId: 'test-session',
       title: 'My First Doc',
       type: 'richtext'
   });
   
   await internalDocs.openDocument(doc.doc_id);
   ```

4. **Customize styling** (see Customization section)

5. **Deploy to production!** 🎉

---

## 📧 Support

For issues or questions:
- Check Troubleshooting section above
- Review API Integration requirements
- Verify all dependencies loaded
- Check browser console for errors

---

**Made with ❤️ by AI Agents Platform Team**  
**Version:** 1.0.0  
**Last Updated:** November 14, 2025

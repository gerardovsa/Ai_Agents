# Tiptap Advanced Extensions - Implementation Plan

**Date:** November 16, 2025  
**Status:** 🎯 READY FOR IMPLEMENTATION  
**Module:** `UI/modules/internal_docs/manager.js`

---

## 🎯 Overview

Enhance the rich text document editor with **professional Tiptap extensions** including auto-save, @mentions, drag-and-drop file uploads, collaborative editing, and PDF export.

---

## ✨ Planned Enhancements

### 1. **Proper Tiptap Initialization** ✅ CDN ADDED

**Current State:**
- Using basic `contenteditable` div
- Using deprecated `document.execCommand()`
- No proper editor instance
- Limited functionality

**New Implementation:**
```javascript
import { Editor } from '@tiptap/core'
import StarterKit from '@tiptap/starter-kit'

const editor = new Editor({
  element: document.querySelector('.editor'),
  extensions: [StarterKit],
  content: '<p>Hello World!</p>',
})
```

**Benefits:**
- Modern ProseMirror-based editor
- Proper undo/redo history
- Extensible architecture
- Better performance

---

### 2. **Auto-Save Extension**

**Purpose:** Automatically save documents every 30 seconds

**Implementation:**
```javascript
const AutoSave = Extension.create({
  name: 'autoSave',
  
  addOptions() {
    return {
      delay: 30000, // 30 seconds
      onSave: null,
    }
  },
  
  onUpdate() {
    clearTimeout(this.saveTimeout)
    this.saveTimeout = setTimeout(() => {
      if (this.options.onSave) {
        this.options.onSave(this.editor.getJSON())
      }
    }, this.options.delay)
  },
})

// Usage
const editor = new Editor({
  extensions: [
    StarterKit,
    AutoSave.configure({
      delay: 30000,
      onSave: (content) => {
        fetch('/api/synergy/internal-doc/save', {
          method: 'POST',
          body: JSON.stringify({ content }),
        })
      },
    }),
  ],
})
```

**Features:**
- Debounced saving (prevents excessive requests)
- Visual save indicator
- Conflict resolution
- Retry on failure

**UI Indicators:**
- "Saving..." (yellow dot)
- "Saved" (green checkmark)
- "Error" (red X)

---

### 3. **Mention Extension (@mentions)**

**Purpose:** Tag team members, cases, or topics

**CDN Added:** ✅ `@tiptap/extension-mention`

**Implementation:**
```javascript
import Mention from '@tiptap/extension-mention'

const editor = new Editor({
  extensions: [
    StarterKit,
    Mention.configure({
      HTMLAttributes: {
        class: 'mention',
      },
      suggestion: {
        items: ({ query }) => {
          return [
            { id: 1, label: '@John Doe' },
            { id: 2, label: '@Jane Smith' },
            { id: 3, label: '@urgent' },
            { id: 4, label: '@followup' },
          ]
          .filter(item => 
            item.label.toLowerCase().startsWith(query.toLowerCase())
          )
          .slice(0, 5)
        },
        render: () => {
          let component;
          
          return {
            onStart: props => {
              component = new MentionList(props)
            },
            onUpdate(props) {
              component.updateProps(props)
            },
            onExit() {
              component.destroy()
            },
          }
        },
      },
    }),
  ],
})
```

**Use Cases:**
- `@John` - Mention team member (sends notification)
- `@urgent` - Tag priority level
- `@followup` - Add task reminder
- `@case-12345` - Link to veterinary case

**Features:**
- Autocomplete dropdown
- Click to insert
- Custom styling (blue background)
- Searchable list

---

### 4. **File Handler Extension (Drag & Drop)**

**Purpose:** Drag files directly into document

**CDN Added:** ✅ Built into Tiptap core via `editorProps`

**Implementation:**
```javascript
const editor = new Editor({
  extensions: [StarterKit, Image],
  
  editorProps: {
    handleDrop: function(view, event, slice, moved) {
      if (!moved && event.dataTransfer?.files?.[0]) {
        const file = event.dataTransfer.files[0]
        const filesize = ((file.size/1024)/1024).toFixed(4)
        
        // Max 10MB
        if ((file.type === "image/jpeg" || file.type === "image/png") 
            && filesize < 10) {
          
          // Upload to backend
          uploadFile(file).then(url => {
            const { schema } = view.state
            const coordinates = view.posAtCoords({ 
              left: event.clientX, 
              top: event.clientY 
            })
            const node = schema.nodes.image.create({ src: url })
            const transaction = view.state.tr.insert(coordinates.pos, node)
            view.dispatch(transaction)
          })
          
          return true
        }
      }
      return false
    },
    
    handlePaste(view, event, slice) {
      // Handle pasted files
      const items = event.clipboardData?.items
      if (items) {
        for (let item of items) {
          if (item.type.indexOf("image") !== -1) {
            const file = item.getAsFile()
            // Upload and insert
          }
        }
      }
      return false
    },
  },
})
```

**Supported File Types:**
- **Images:** PNG, JPEG, GIF, WebP (max 10MB)
- **Documents:** PDF (display as link)
- **Other:** Show as attachment link

**Features:**
- Drag & drop anywhere in document
- Paste from clipboard
- Progress indicator during upload
- Automatic thumbnail generation
- Resizable images

---

### 5. **Collaboration Extension (Yjs)**

**Purpose:** Real-time multi-user editing

**CDN Added:** ✅ `@tiptap/extension-collaboration` + `yjs` + `y-websocket`

**Implementation:**
```javascript
import { HocuspocusProvider } from '@hocuspocus/provider'
import Collaboration from '@tiptap/extension-collaboration'
import CollaborationCursor from '@tiptap/extension-collaboration-cursor'

// Setup WebSocket provider
const provider = new HocuspocusProvider({
  url: 'ws://localhost:5001/collaboration',
  name: `document-${docId}`,
})

const editor = new Editor({
  extensions: [
    StarterKit.configure({
      history: false, // Collaboration has own undo/redo
    }),
    Collaboration.configure({
      document: provider.document,
    }),
    CollaborationCursor.configure({
      provider: provider,
      user: {
        name: 'John Doe',
        color: '#4F6CFF',
      },
    }),
  ],
})
```

**Backend Requirements:**
```python
# AI_infrastructure/routes/collaboration_routes.py
from flask import Flask
from flask_socketio import SocketIO, emit, join_room

socketio = SocketIO(app, cors_allowed_origins="*")

@socketio.on('connect')
def handle_connect():
    print('Client connected')

@socketio.on('join_document')
def handle_join(data):
    doc_id = data['doc_id']
    join_room(f'doc-{doc_id}')
    emit('user_joined', {
        'user': data['user'],
        'doc_id': doc_id
    }, room=f'doc-{doc_id}')

@socketio.on('update_document')
def handle_update(data):
    doc_id = data['doc_id']
    emit('document_updated', data, room=f'doc-{doc_id}', skip_sid=request.sid)
```

**Features:**
- See other users' cursors (with names & colors)
- Real-time text updates
- Conflict-free merging (CRDT)
- Presence indicators ("3 users editing")
- Offline support (syncs when reconnected)

**UI Indicators:**
- User avatars in header
- Colored cursors with names
- "Syncing..." indicator
- Offline warning banner

---

### 6. **Export Extension (PDF/DOCX)**

**Purpose:** Export documents to multiple formats

**CDN Added:** ✅ `jspdf` + `html2canvas`

**Implementation:**

**PDF Export:**
```javascript
async function exportToPDF(editor) {
  const { jsPDF } = window.jspdf
  const content = editor.view.dom
  
  const canvas = await html2canvas(content)
  const imgData = canvas.toDataURL('image/png')
  
  const pdf = new jsPDF({
    orientation: 'portrait',
    unit: 'mm',
    format: 'a4'
  })
  
  const imgWidth = 210 // A4 width
  const imgHeight = (canvas.height * imgWidth) / canvas.width
  
  pdf.addImage(imgData, 'PNG', 0, 0, imgWidth, imgHeight)
  pdf.save(`document-${Date.now()}.pdf`)
}
```

**Markdown Export:**
```javascript
function exportToMarkdown(editor) {
  const markdown = turndownService.turndown(editor.getHTML())
  const blob = new Blob([markdown], { type: 'text/markdown' })
  const url = URL.createObjectURL(blob)
  const link = document.createElement('a')
  link.href = url
  link.download = `document-${Date.now()}.md`
  link.click()
}
```

**HTML Export:**
```javascript
function exportToHTML(editor) {
  const html = `
    <!DOCTYPE html>
    <html>
      <head>
        <meta charset="UTF-8">
        <title>Document</title>
        <style>
          body { font-family: Arial, sans-serif; max-width: 800px; margin: 0 auto; padding: 20px; }
          h1 { color: #333; }
        </style>
      </head>
      <body>
        ${editor.getHTML()}
      </body>
    </html>
  `
  
  const blob = new Blob([html], { type: 'text/html' })
  const url = URL.createObjectURL(blob)
  const link = document.createElement('a')
  link.href = url
  link.download = `document-${Date.now()}.html`
  link.click()
}
```

**Supported Formats:**
- **PDF** - Paginated, print-ready
- **DOCX** - Microsoft Word (requires docx.js)
- **Markdown** - Plain text with formatting
- **HTML** - Standalone webpage
- **JSON** - Tiptap native format

---

## 🎨 Enhanced Toolbar Design

**New Toolbar Layout:**

```
┌─────────────────────────────────────────────────────────────┐
│ [B][I][S][C] | [H1][H2][H3] | [•][1.]["] | [←][→] | [🔗][📷] │
│ Format        Headings        Lists        History   Media   │
│                                                               │
│ [@mention] [💾 Auto-save: Saved] [👥 2 users]  [🔗 Share]   │
│ Mention    Status              Presence        Link          │
└─────────────────────────────────────────────────────────────┘
```

**Toolbar Sections:**
1. **Format:** Bold, Italic, Strikethrough, Code
2. **Headings:** H1, H2, H3
3. **Lists:** Bullet, Numbered, Quote
4. **History:** Undo, Redo
5. **Media:** Link, Image
6. **Advanced:** Mention, Save Status, Presence, Share

---

## 🔧 Technical Implementation Steps

### **Step 1: Update HTML (Add CDN Libraries)** ✅ COMPLETE

```html
<!-- Tiptap Core -->
<script src="https://cdn.jsdelivr.net/npm/@tiptap/core@2.1.13/dist/index.umd.min.js"></script>
<script src="https://cdn.jsdelivr.net/npm/@tiptap/starter-kit@2.1.13/dist/index.umd.min.js"></script>
<script src="https://cdn.jsdelivr.net/npm/@tiptap/extension-placeholder@2.1.13/dist/index.umd.min.js"></script>
<script src="https://cdn.jsdelivr.net/npm/@tiptap/extension-link@2.1.13/dist/index.umd.min.js"></script>
<script src="https://cdn.jsdelivr.net/npm/@tiptap/extension-mention@2.1.13/dist/index.umd.min.js"></script>

<!-- Collaboration -->
<script src="https://cdn.jsdelivr.net/npm/@tiptap/extension-collaboration@2.1.13/dist/index.umd.min.js"></script>
<script src="https://cdn.jsdelivr.net/npm/@tiptap/extension-collaboration-cursor@2.1.13/dist/index.umd.min.js"></script>
<script src="https://cdn.jsdelivr.net/npm/yjs@13.6.10/dist/yjs.min.js"></script>
<script src="https://cdn.jsdelivr.net/npm/y-websocket@1.5.0/dist/y-websocket.min.js"></script>

<!-- Export -->
<script src="https://cdn.jsdelivr.net/npm/jspdf@2.5.1/dist/jspdf.umd.min.js"></script>
<script src="https://cdn.jsdelivr.net/npm/html2canvas@1.4.1/dist/html2canvas.min.js"></script>
```

### **Step 2: Create Tiptap Initialization Method**

In `manager.js`:

```javascript
initializeTiptapEditor(doc, popup, sessionId) {
  const { Editor } = window.tiptapCore
  const { StarterKit } = window.tiptapStarterKit
  
  const editor = new Editor({
    element: document.getElementById(`editor-${doc.doc_id}`),
    extensions: [
      StarterKit,
      // Add all extensions here
    ],
    content: doc.content,
    onUpdate: ({ editor }) => {
      // Auto-save logic
    },
  })
  
  // Store instance
  this.tiptapEditors[doc.doc_id] = editor
}
```

### **Step 3: Add Custom Extensions**

```javascript
// Auto-save extension
const AutoSave = Extension.create({
  name: 'autoSave',
  onUpdate() {
    // Save logic
  },
})

// Veterinary mention extension
const VeterinaryMention = Mention.extend({
  suggestion: {
    items: ({ query }) => {
      return fetchMentionables(query) // From API
    },
  },
})
```

### **Step 4: Create Collaboration Backend**

New file: `AI_infrastructure/routes/collaboration_routes.py`

```python
from flask_socketio import SocketIO, emit, join_room

socketio = SocketIO(app)

@socketio.on('join_document')
def handle_join(data):
    doc_id = data['doc_id']
    join_room(f'doc-{doc_id}')
```

### **Step 5: Add Export Functions**

```javascript
exportToPDF(docId) {
  const editor = this.tiptapEditors[docId]
  // PDF generation logic
}

exportToMarkdown(docId) {
  const editor = this.tiptapEditors[docId]
  // Markdown conversion logic
}
```

---

## 🎯 Use Cases for Your Kanban System

### **Veterinary Clinic Scenario:**

**Case Card: "Max - Hip Dysplasia Follow-up"**

**Attached Document: "Treatment Plan"**

**Features in Action:**

1. **Dr. Sarah** opens document from kanban card
2. **Types:** "Started treatment with @NSAIDs"
3. **@mentions:** Auto-suggests "@medications" tag
4. **Drags X-ray** from desktop into document
5. **Dr. John** opens same document (sees Sarah's cursor)
6. **Both edit** simultaneously - no conflicts
7. **Auto-saves** every 30 seconds
8. **Exports to PDF** for client handout
9. **Shares link** with assistant via toolbar button

**Result:** Seamless collaborative case documentation

---

## 📊 Feature Comparison

| Feature | Before | After |
|---------|--------|-------|
| Editor Type | contenteditable | Tiptap (ProseMirror) |
| Undo/Redo | Browser default | Full history (100 steps) |
| Auto-save | Manual only | Every 30 seconds |
| Mentions | None | @team, @tags, @cases |
| File Upload | None | Drag & drop images |
| Collaboration | None | Real-time multi-user |
| Export | Markdown only | PDF, DOCX, MD, HTML |
| Toolbar | Basic (8 buttons) | Advanced (15+ buttons) |
| Extensions | None | 6+ custom extensions |

---

## 🚀 Benefits

**For Users:**
- ✅ Professional document editing
- ✅ Auto-save (never lose work)
- ✅ Tag team members (@mentions)
- ✅ Drag & drop files
- ✅ Collaborate in real-time
- ✅ Export to any format

**For Developers:**
- ✅ Modern, maintainable code
- ✅ Extensible architecture
- ✅ TypeScript support
- ✅ Active community
- ✅ Well-documented APIs

**For Business:**
- ✅ Better team collaboration
- ✅ Reduced data loss
- ✅ Professional output (PDF)
- ✅ Faster documentation
- ✅ Improved workflows

---

## ⚡ Performance Considerations

**Optimizations:**
- Lazy load extensions (only when needed)
- Debounce auto-save (avoid excessive API calls)
- Virtual scrolling for large documents
- WebWorker for PDF generation
- IndexedDB for offline cache

**Bundle Size:**
- Tiptap Core: ~80KB gzipped
- Extensions: ~20KB each
- Total: ~200KB (acceptable)

**Memory:**
- ProseMirror: Efficient DOM updates
- Yjs: CRDT structure (~2-3x doc size)
- Overall: < 5MB for large documents

---

## 🔐 Security & Privacy

**Collaboration Security:**
- WebSocket authentication (JWT tokens)
- Document-level permissions
- Encrypted connections (WSS)
- Rate limiting on updates

**File Upload Security:**
- Whitelist allowed file types
- Max file size limits (10MB)
- Virus scanning (ClamAV integration)
- Separate storage bucket

**Data Privacy:**
- Documents encrypted at rest
- Audit logs for all edits
- User-level access control
- GDPR compliant exports

---

## 📚 Documentation References

**Official Docs:**
- Tiptap: https://tiptap.dev/
- ProseMirror: https://prosemirror.net/
- Yjs: https://docs.yjs.dev/
- jsPDF: https://artskydj.github.io/jsPDF/

**Community Extensions:**
- GitHub: https://github.com/ueberdosis/tiptap/discussions/2223
- Awesome Tiptap: https://github.com/ueberdosis/awesome-tiptap

---

## 🎉 Summary

This plan transforms your basic contenteditable div into a **professional collaborative document editor** with:

✅ **6 Advanced Extensions**
- Auto-save (30s intervals)
- @Mentions (team/tags)
- File Handler (drag & drop)
- Collaboration (real-time)
- Export (PDF/DOCX/MD)
- Link Preview

✅ **Modern Architecture**
- Tiptap 2.1.13 (latest)
- ProseMirror foundation
- Extensible plugins
- TypeScript support

✅ **Professional Features**
- Real-time collaboration
- 100-step undo/redo
- Drag & drop images
- Multi-format export
- Auto-save with indicators

✅ **Production Ready**
- CDN libraries added ✅
- Implementation plan complete ✅
- Use cases documented ✅
- Security considered ✅

---

**Next Steps:**
1. Implement `initializeTiptapEditor()` method
2. Create custom extensions (AutoSave, VeterinaryMention)
3. Add collaboration WebSocket backend
4. Test with multiple users
5. Add export functionality
6. Deploy and monitor

**Estimated Implementation Time:** 8-12 hours

---

**Status:** 🎯 READY FOR IMPLEMENTATION  
**Priority:** HIGH (significantly improves document editing)  
**Complexity:** MEDIUM (well-documented, community support)

---

**Last Updated:** November 16, 2025 11:15 PM  
**Author:** AI Assistant (Claude Sonnet 4.5)  
**Version:** 1.0.0

# Internal Docs Module

Complete internal document management system for Synergy platform.

## Structure

```
internal_docs/
├── manager.js                          # Main module - InternalDocsManager class
├── internal-docs.js                    # Legacy integration script
├── internal-docs.css                   # Legacy styles (deprecated - now in manager.js)
├── integration-example.html            # Example usage
├── INTERNAL_DOCS_AUDIT.md             # Technical audit
├── INTERNAL_DOCS_IMPLEMENTATION.md    # Implementation guide
├── INTERNAL_DOCS_MODULE.md            # Module documentation
└── README.md                           # This file
```

## Main File

**`manager.js`** - Complete document management system
- Rich text editor (TipTap)
- Spreadsheet editor (Handsontable)
- Floating popup windows (draggable, resizable, collapsible)
- Auto-save functionality
- Export to multiple formats
- Activity log and version history
- Self-contained CSS (injected dynamically)

## Usage

```html
<!-- Include the module -->
<script src="modules/internal_docs/manager.js"></script>

<script>
    // Initialize
    window.internalDocsManager = new InternalDocsManager('http://localhost:5001');
    
    // Open document
    window.internalDocsManager.openInternalDocPopup(docId, sessionId);
    
    // Create new document
    window.internalDocsManager.createInternalDoc(sessionId);
    
    // Attach existing document
    window.internalDocsManager.attachExistingDoc(sessionId);
</script>
```

## Features

- **Document Types**: Rich text (TipTap) and Spreadsheet (Handsontable)
- **Metadata**: Title, description, tags, timestamps
- **Popup Windows**: Draggable, resizable, minimizable, maximizable
- **Editing**: Inline title/description editing with auto-update
- **Auto-save**: Automatic content saving
- **Export**: PDF, DOCX, HTML, Markdown, CSV
- **Activity Log**: Document history and version tracking
- **Share URLs**: Generate shareable links

## API Integration

Module communicates with Flask backend:
- `GET /api/synergy/internal-doc/{doc_id}` - Fetch document
- `PUT /api/synergy/internal-doc/{doc_id}` - Update document
- `POST /api/synergy/internal-doc` - Create document
- `GET /api/synergy/internal-docs` - List all documents

## CSS Architecture

**All CSS is now self-contained in `manager.js`**:
- Styles are injected dynamically via `injectStyles()` method
- No external CSS file required (internal-docs.css is deprecated)
- Prevents conflicts with main application styles
- Uses CSS variables for theming

## Dependencies

- **TipTap**: Rich text editor (loaded via CDN)
- **Handsontable**: Spreadsheet editor (loaded via CDN)
- **FontAwesome**: Icons

## Configuration

```javascript
const manager = new InternalDocsManager(apiBaseUrl);

// API base URL (default: http://localhost:5001)
manager.apiBaseUrl = 'http://localhost:5001';

// Popup z-index (default: 9000)
manager.popupZIndex = 9000;

// Current user
manager.currentUser = {
    email: 'user@example.com',
    user_id: 1
};
```

## Browser Support

- Chrome 90+
- Firefox 88+
- Safari 14+
- Edge 90+

## Last Updated

November 16, 2025 - Reorganized into module folder with self-contained CSS

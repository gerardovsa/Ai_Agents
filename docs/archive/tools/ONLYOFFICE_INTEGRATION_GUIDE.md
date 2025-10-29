# ONLYOFFICE Integration Guide

## 🎯 Overview

**ONLYOFFICE** is an open-source office suite that provides powerful document editing capabilities (docs, sheets, slides, PDFs) that can be embedded into applications. It's a **self-hosted alternative** to Google Docs/Microsoft Office Online with extensive API support.

## 🌟 Key Capabilities

### What ONLYOFFICE Offers
1. **Document Editing**
   - Word processing (DOCX, DOC, ODT, RTF, TXT, HTML, EPUB)
   - Spreadsheets (XLSX, XLS, ODS, CSV)
   - Presentations (PPTX, PPT, ODP)
   - PDF editing and form filling
   - Markdown and HTML conversion

2. **Collaboration Features**
   - Real-time co-editing (character-level or paragraph-level)
   - Comments and mentions
   - Track changes and document comparison
   - Version history
   - Built-in chat and video calls (Jitsi/Rainbow integration)

3. **AI Integration**
   - Connect any AI model (including local models)
   - Text generation, rewriting, translation
   - Grammar checking
   - Image and code generation via AI plugins

4. **Security**
   - End-to-end encryption
   - GDPR compliance
   - Open-source transparency (AGPL v3.0 license)
   - Advanced document permissions

## 🛠️ Integration Options

### Option 1: ONLYOFFICE Docs API (Self-Hosted)
**Best for**: Full control, private data, enterprise use

```javascript
// Embed ONLYOFFICE editor in your web app
const docEditor = new DocsAPI.DocEditor("placeholder", {
    "document": {
        "fileType": "docx",
        "key": "document_key_12345",
        "title": "Example.docx",
        "url": "https://yourserver.com/documents/example.docx"
    },
    "documentType": "word", // "word", "cell", "slide"
    "editorConfig": {
        "mode": "edit", // "edit" or "view"
        "user": {
            "id": "user123",
            "name": "John Doe"
        },
        "customization": {
            "logo": {
                "image": "https://yourserver.com/logo.png"
            }
        }
    },
    "height": "100%",
    "width": "100%",
    "type": "desktop" // "desktop" or "mobile"
});
```

**Setup Steps**:
1. **Deploy ONLYOFFICE Document Server**:
   ```bash
   # Docker deployment (easiest)
   docker run -i -t -d -p 80:80 \
     -v /app/onlyoffice/DocumentServer/data:/var/www/onlyoffice/Data \
     onlyoffice/documentserver
   ```

2. **Install in your stack**:
   - Download: https://www.onlyoffice.com/download#docs-enterprise
   - Supports: Windows, Linux, Docker, Kubernetes
   - System requirements: 4GB RAM, 2 CPU cores minimum

3. **Connect to your app**:
   - Include ONLYOFFICE API script
   - Implement callback URL for document saving
   - Handle user authentication

### Option 2: ONLYOFFICE DocSpace
**Best for**: Team collaboration, secure rooms, cloud hosting

- **DocSpace Features**:
  - Room-based collaboration (Public, Collaboration, Custom rooms)
  - Flexible permissions per room
  - Free cloud hosting: https://www.onlyoffice.com/docspace-registration
  - Self-hosted option available

**API Access**:
```javascript
// DocSpace Backend REST API
const response = await fetch('https://your-docspace.com/api/2.0/files', {
    method: 'POST',
    headers: {
        'Authorization': 'Bearer YOUR_API_TOKEN',
        'Content-Type': 'application/json'
    },
    body: JSON.stringify({
        title: 'New Document.docx',
        folderId: 123456
    })
});
```

### Option 3: Desktop/Mobile Apps
**Best for**: Offline editing, local file management

- **Desktop Editors**: Windows, macOS, Linux (FREE)
- **Mobile Apps**: iOS, Android (FREE)
- Download: https://www.onlyoffice.com/download-desktop

### Option 4: Connectors (Pre-built Integrations)
**Best for**: Existing platforms

ONLYOFFICE has **40+ ready integrations**:
- **Cloud Storage**: Nextcloud, ownCloud, Box, Seafile
- **CMS**: WordPress, Drupal, Joomla, Alfresco
- **Collaboration**: Moodle, Confluence, Redmine
- **CRM**: Odoo, SuiteCRM
- **Development**: GitHub, GitLab (via integrations)

Example: **Nextcloud Integration**
```bash
# Install ONLYOFFICE app in Nextcloud
# Settings > Apps > Office & Text > ONLYOFFICE
# Configure document server URL
```

## 🔗 API Tools to Create

### ONLYOFFICE Tools Schema (25 Tools)

```json
{
  "platform": "onlyoffice",
  "description": "ONLYOFFICE Document Server API - Create, edit, collaborate on documents",
  "tools": [
    {
      "name": "onlyoffice_create_document",
      "description": "Create new document via Document Server",
      "parameters": {
        "title": "Document title",
        "type": "word|cell|slide",
        "content": "Initial content"
      }
    },
    {
      "name": "onlyoffice_open_editor",
      "description": "Open document in ONLYOFFICE editor",
      "parameters": {
        "document_url": "URL to document file",
        "document_key": "Unique document identifier",
        "user_id": "User identifier",
        "user_name": "User display name",
        "mode": "edit|view"
      }
    },
    {
      "name": "onlyoffice_save_document",
      "description": "Save document changes via callback",
      "parameters": {
        "document_key": "Document key",
        "url": "URL to download saved file"
      }
    },
    {
      "name": "onlyoffice_convert_document",
      "description": "Convert document format",
      "parameters": {
        "file_url": "Source file URL",
        "from_format": "Source format (docx, xlsx, pptx)",
        "to_format": "Target format (pdf, html, txt)"
      }
    },
    {
      "name": "onlyoffice_generate_pdf",
      "description": "Generate PDF from document",
      "parameters": {
        "document_url": "Document URL",
        "document_type": "word|cell|slide"
      }
    },
    {
      "name": "onlyoffice_collaborate_realtime",
      "description": "Start real-time collaboration session",
      "parameters": {
        "document_key": "Document key",
        "users": "Array of user objects",
        "edit_mode": "character|paragraph"
      }
    },
    {
      "name": "onlyoffice_add_comment",
      "description": "Add comment to document",
      "parameters": {
        "document_key": "Document key",
        "text": "Comment text",
        "user_id": "Commenter ID",
        "selection": "Selected text range"
      }
    },
    {
      "name": "onlyoffice_track_changes",
      "description": "Enable change tracking",
      "parameters": {
        "document_key": "Document key",
        "enabled": true|false
      }
    },
    {
      "name": "onlyoffice_compare_documents",
      "description": "Compare two document versions",
      "parameters": {
        "original_url": "Original document URL",
        "revised_url": "Revised document URL"
      }
    },
    {
      "name": "onlyoffice_fill_pdf_form",
      "description": "Fill PDF form programmatically",
      "parameters": {
        "form_url": "PDF form URL",
        "fields": "Object with field values"
      }
    },
    {
      "name": "onlyoffice_apply_watermark",
      "description": "Add watermark to document",
      "parameters": {
        "document_key": "Document key",
        "text": "Watermark text",
        "diagonal": true|false,
        "transparency": 0-1
      }
    },
    {
      "name": "onlyoffice_plugin_execute",
      "description": "Execute ONLYOFFICE plugin/macro",
      "parameters": {
        "document_key": "Document key",
        "plugin_id": "Plugin identifier",
        "params": "Plugin parameters"
      }
    },
    {
      "name": "onlyoffice_ai_generate_text",
      "description": "Generate text using AI assistant",
      "parameters": {
        "prompt": "Text generation prompt",
        "model": "AI model to use",
        "max_tokens": "Maximum tokens"
      }
    },
    {
      "name": "onlyoffice_ai_translate",
      "description": "Translate document using AI",
      "parameters": {
        "text": "Text to translate",
        "target_language": "Target language code"
      }
    },
    {
      "name": "onlyoffice_docspace_create_room",
      "description": "Create collaboration room in DocSpace",
      "parameters": {
        "title": "Room title",
        "type": "Public|Collaboration|Custom",
        "users": "Array of user emails"
      }
    },
    {
      "name": "onlyoffice_docspace_upload_file",
      "description": "Upload file to DocSpace",
      "parameters": {
        "room_id": "Room ID",
        "file_path": "Local file path",
        "title": "File title"
      }
    },
    {
      "name": "onlyoffice_docspace_share_file",
      "description": "Share file with users",
      "parameters": {
        "file_id": "File ID",
        "users": "Array of user emails",
        "access_level": "Read|Edit|Review"
      }
    },
    {
      "name": "onlyoffice_get_document_info",
      "description": "Get document metadata",
      "parameters": {
        "document_key": "Document key"
      }
    },
    {
      "name": "onlyoffice_get_version_history",
      "description": "Get document version history",
      "parameters": {
        "document_key": "Document key"
      }
    },
    {
      "name": "onlyoffice_restore_version",
      "description": "Restore previous document version",
      "parameters": {
        "document_key": "Document key",
        "version_number": "Version to restore"
      }
    }
  ]
}
```

## 💡 Use Cases for Your Project

### For MiniVetGuide Business:
1. **Customer Quote Documents**
   - Create branded quote PDFs using ONLYOFFICE
   - Fill PDF forms with customer data
   - Generate invoices from templates

2. **Internal Documentation**
   - Self-hosted document collaboration (HIPAA-compliant if needed)
   - Product manuals and guides
   - Training materials with version control

3. **Data Privacy**
   - Store sensitive vet records in self-hosted ONLYOFFICE
   - End-to-end encryption for client documents
   - No data sent to third parties (unlike Google Docs)

### For AI Agents Project:
1. **Document Processing**
   - Convert uploaded documents to text for AI analysis
   - Generate reports in DOCX/PDF format
   - Template-based document generation

2. **Collaboration**
   - Real-time document editing in web apps
   - Track changes made by AI agents vs humans
   - Comment system for AI suggestions

## 📊 Comparison: ONLYOFFICE vs Alternatives

| Feature | ONLYOFFICE | Google Docs | Microsoft 365 |
|---------|------------|-------------|---------------|
| **Self-Hosted** | ✅ Yes | ❌ No | ⚠️ Hybrid |
| **Open Source** | ✅ AGPL v3.0 | ❌ Proprietary | ❌ Proprietary |
| **Real-time Collab** | ✅ Yes | ✅ Yes | ✅ Yes |
| **Offline Editing** | ✅ Desktop apps | ⚠️ Limited | ✅ Desktop apps |
| **Format Support** | ✅ DOCX, XLSX, PPTX, PDF, ODT | ⚠️ Export only | ✅ Native |
| **Data Privacy** | ✅ Your server | ❌ Google has access | ⚠️ Microsoft has access |
| **Cost** | ✅ Free (self-hosted) | 💰 Free with limits | 💰 Subscription |
| **API Complexity** | ⚠️ Moderate | ⚠️ OAuth required | ⚠️ OAuth required |

## 🚀 Implementation Priority

### HIGH PRIORITY - Create ONLYOFFICE Tools
- **Reason**: Self-hosted = no API keys/rate limits/costs
- **Benefits**: 
  - Full control over document processing
  - Privacy compliance (GDPR, HIPAA)
  - Unlimited usage
  - AI integration capabilities

### Recommended Architecture:
```
AI Agents Backend
    ↓
ONLYOFFICE Document Server (Docker)
    ↓
Document Storage (local/S3/Supabase)
    ↓
Frontend (React/Vue with ONLYOFFICE editor embedded)
```

## 📝 Next Steps

1. **Deploy ONLYOFFICE Document Server** (Docker recommended)
2. **Create `onlyoffice_tools.json`** schema (25 tools as outlined above)
3. **Create `onlyoffice.py`** implementation using ONLYOFFICE API
4. **Test document creation/editing/conversion**
5. **Integrate with existing Gmail/Drive tools** for seamless workflow

## 🔗 Resources

- **Official API Docs**: https://api.onlyoffice.com/
- **Document Server GitHub**: https://github.com/ONLYOFFICE/DocumentServer
- **DocSpace API**: https://api.onlyoffice.com/docspace/
- **Plugins SDK**: https://api.onlyoffice.com/docspace/plugins-sdk/
- **Integration Examples**: https://github.com/ONLYOFFICE/document-server-integration

---

**Should I proceed with creating the ONLYOFFICE tools schema and implementation?** This would give you a powerful self-hosted document processing system without relying on Google/Microsoft APIs!

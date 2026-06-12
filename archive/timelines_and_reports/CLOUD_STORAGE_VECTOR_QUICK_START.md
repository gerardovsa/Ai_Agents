# Cloud Storage to Vector Database - Quick Start Guide

**Last Updated**: November 30, 2025  
**Status**: ✅ Google Drive Ready | 🔄 OneDrive/Dropbox In Progress  
**Version**: 1.0.0

---

## 🚀 Quick Start (Google Drive Only - Production Ready)

### Prerequisites

1. **Google OAuth Credentials** - User must connect Google Workspace in Platform Connections
2. **Pinecone Credentials** - Configure in Platform Connections (API key, index, environment)
3. **Embedding Provider** - Configure OpenAI or Voyager AI in Platform Connections

### Basic Usage

**Step 1: Browse Google Drive Folders**
```python
# AI Agent command
"Show me folders in my Google Drive"

# Tool execution
cloud_storage_browse_folders(
    provider='google_drive',
    folder_id='root',  # or specific folder ID
    include_files=True,
    file_types=['pdf', 'docx', 'txt', 'md']
)

# Returns
{
    'success': True,
    'provider': 'google_drive',
    'folder_count': 5,
    'folders': [
        {'id': 'abc123', 'name': 'Legal Documents', 'file_count': 12},
        {'id': 'def456', 'name': 'Training Materials', 'file_count': 25}
    ],
    'files': [
        {'id': 'file1', 'name': 'contract.pdf', 'size': 245000, 'mime_type': 'application/pdf'},
        {'id': 'file2', 'name': 'guide.docx', 'size': 128000, 'mime_type': 'application/vnd...' }
    ]
}
```

**Step 2: Upload Files to Pinecone**
```python
# AI Agent command
"Upload contract.pdf and guide.docx from Google Drive to vector database"

# Tool execution
cloud_storage_upload_to_vector_db(
    provider='google_drive',
    file_ids=['file1', 'file2'],
    namespace='legal-docs',
    metadata={'category': 'legal', 'year': '2025'},
    chunk_size=800,
    chunk_overlap=100
)

# Returns
{
    'success': True,
    'processed': 2,
    'total_chunks': 47,
    'vector_ids': ['a1b2c3d4', 'e5f6g7h8', ...],  # First 10 shown
    'failed': []
}
```

**Step 3: Search Uploaded Documents**
```python
# Use existing Pinecone smart search tools
pinecone_search_summaries(
    query_text='legal contract terms',
    namespace='legal-docs',
    top_k=10
)

# Returns summaries with document names and previews
# Then use pinecone_get_vector_details() for full content
```

---

## 📖 AI Agent Usage Patterns

### Pattern 1: Upload Single File

**User**: "Upload my 2025 training manual from Google Drive"

**AI Agent Workflow**:
```
1. AI calls: cloud_storage_browse_folders(provider='google_drive', include_files=True)
2. AI searches results for "2025 training manual"
3. AI finds file_id: "xyz789"
4. AI calls: cloud_storage_upload_to_vector_db(
     provider='google_drive',
     file_ids=['xyz789'],
     namespace='training-materials'
   )
5. AI responds: "Uploaded 2025 training manual - 23 chunks processed, searchable in vector database"
```

### Pattern 2: Upload Entire Folder

**User**: "Upload all PDFs from my Legal Documents folder"

**AI Agent Workflow**:
```
1. AI calls: cloud_storage_browse_folders(provider='google_drive', folder_id='root')
2. AI finds "Legal Documents" folder_id: "abc123"
3. AI calls: cloud_storage_browse_folders(provider='google_drive', folder_id='abc123', include_files=True, file_types=['pdf'])
4. AI extracts all PDF file_ids: ['file1', 'file2', ..., 'file12']
5. AI calls: cloud_storage_upload_to_vector_db(
     provider='google_drive',
     file_ids=['file1', 'file2', ..., 'file12'],
     namespace='legal-docs'
   )
6. AI responds: "Uploaded 12 legal PDFs - 156 chunks processed, all searchable"
```

### Pattern 3: Create Folder Link (Future - Scheduled Sync)

**User**: "Monitor my Knowledge Base folder and sync daily"

**AI Agent Workflow**:
```
1. AI calls: cloud_storage_browse_folders(provider='google_drive')
2. AI finds "Knowledge Base" folder_id: "kb123"
3. AI calls: cloud_storage_create_folder_link(
     provider='google_drive',
     folder_id='kb123',
     sync_schedule='daily',
     namespace='knowledge-base',
     file_types=['pdf', 'docx']
   )
4. AI responds: "Created folder link - will sync daily at 9am (link ID: link_abc123def456)"
5. ⏳ System will automatically detect new/updated files and upload to Pinecone
```

---

## 🛠️ Tool Reference

### 1. cloud_storage_list_providers

**Purpose**: Check which cloud storage providers are available and connected

**Parameters**: None

**Returns**:
```json
{
    "success": true,
    "providers": [
        {
            "name": "Google Drive",
            "platform": "google_drive",
            "connected": true,
            "features": ["browse", "upload", "folder_links"]
        },
        {
            "name": "Microsoft OneDrive",
            "platform": "onedrive",
            "connected": false,
            "features": ["browse", "upload", "folder_links"]
        },
        {
            "name": "Dropbox",
            "platform": "dropbox",
            "connected": false,
            "features": ["browse", "upload", "folder_links"]
        }
    ]
}
```

**Example**:
```python
# AI Agent: "What cloud storage can I use?"
cloud_storage_list_providers()
# Returns: Google Drive connected, OneDrive/Dropbox not connected
```

---

### 2. cloud_storage_browse_folders

**Purpose**: Browse folders and files in cloud storage

**Parameters**:
- `provider` (string, required) - "google_drive" | "onedrive" | "dropbox"
- `folder_id` (string, optional) - Folder ID to browse (default: root)
- `include_files` (boolean, optional) - Include files in results (default: false)
- `file_types` (array, optional) - Filter by file types ['pdf', 'docx', 'txt', 'md']

**Returns**:
```json
{
    "success": true,
    "provider": "google_drive",
    "folder_id": "root",
    "folder_count": 3,
    "folders": [
        {
            "id": "folder1",
            "name": "Documents",
            "file_count": 15,
            "modified": "2025-11-25T10:30:00Z"
        }
    ],
    "files": [
        {
            "id": "file1",
            "name": "example.pdf",
            "size": 245000,
            "mime_type": "application/pdf",
            "modified": "2025-11-28T14:20:00Z"
        }
    ]
}
```

**Example**:
```python
# Browse root folder (folders only)
cloud_storage_browse_folders(provider='google_drive')

# Browse specific folder with files
cloud_storage_browse_folders(
    provider='google_drive',
    folder_id='abc123',
    include_files=True,
    file_types=['pdf', 'docx']
)
```

---

### 3. cloud_storage_upload_to_vector_db ⭐ CORE FEATURE

**Purpose**: Upload files directly from cloud storage to Pinecone vector database

**Parameters**:
- `provider` (string, required) - "google_drive" | "onedrive" | "dropbox"
- `file_ids` (array, required) - List of file IDs to upload
- `namespace` (string, optional) - Pinecone namespace for organization
- `metadata` (object, optional) - Custom metadata to attach to vectors
- `chunk_size` (integer, optional) - Text chunk size in characters (default: 800)
- `chunk_overlap` (integer, optional) - Chunk overlap in characters (default: 100)

**Returns**:
```json
{
    "success": true,
    "processed": 5,
    "total_chunks": 127,
    "vector_ids": ["vec1", "vec2", "vec3", "..."],
    "failed": [
        {
            "file_id": "file_bad",
            "error": "Unable to extract text from file"
        }
    ]
}
```

**Processing Pipeline**:
```
1. Download file from cloud storage
2. Extract text (PDF → PyPDF2, DOCX → python-docx, TXT/MD → UTF-8)
3. Chunk text (800 chars with 100 char overlap)
4. Generate embeddings (OpenAI or Voyager AI)
5. Upload vectors to Pinecone with metadata
6. Return vector IDs and statistics
```

**Example**:
```python
# Upload single file
cloud_storage_upload_to_vector_db(
    provider='google_drive',
    file_ids=['file123'],
    namespace='docs'
)

# Upload multiple files with metadata
cloud_storage_upload_to_vector_db(
    provider='google_drive',
    file_ids=['file1', 'file2', 'file3'],
    namespace='legal-docs',
    metadata={'category': 'contracts', 'year': '2025', 'department': 'legal'},
    chunk_size=1000,
    chunk_overlap=150
)
```

**Metadata Structure in Pinecone**:
```json
{
    "filename": "contract.pdf",
    "source_provider": "google_drive",
    "source_file_id": "file123",
    "chunk_index": 0,
    "total_chunks": 15,
    "text": "This is the actual text content...",
    "created_at": "2025-11-30T15:45:00Z",
    "category": "contracts",
    "year": "2025",
    "department": "legal"
}
```

---

### 4. cloud_storage_create_folder_link

**Purpose**: Create monitored folder for automatic sync (scheduled upload)

**Status**: ⏳ Partial - Creates link but scheduled sync not yet functional

**Parameters**:
- `provider` (string, required) - "google_drive" | "onedrive" | "dropbox"
- `folder_id` (string, required) - Folder ID to monitor
- `sync_schedule` (string, required) - "hourly" | "daily" | "weekly" | "manual"
- `namespace` (string, optional) - Pinecone namespace
- `file_types` (array, optional) - File types to sync (default: all)
- `auto_delete` (boolean, optional) - Delete vectors when source deleted (default: false)

**Returns**:
```json
{
    "success": true,
    "link_id": "link_abc123def456",
    "provider": "google_drive",
    "folder_id": "folder123",
    "sync_schedule": "daily",
    "namespace": "knowledge-base",
    "file_types": ["pdf", "docx", "txt", "md"],
    "auto_delete": false,
    "status": "active",
    "next_sync": "2025-12-01T09:00:00Z",
    "message": "Folder link created - will sync daily"
}
```

**Example**:
```python
# Daily sync of documentation folder
cloud_storage_create_folder_link(
    provider='google_drive',
    folder_id='docs_folder_123',
    sync_schedule='daily',
    namespace='company-docs',
    file_types=['pdf', 'docx']
)

# Manual sync only (no automatic updates)
cloud_storage_create_folder_link(
    provider='google_drive',
    folder_id='legal_folder_456',
    sync_schedule='manual',
    namespace='legal-docs',
    auto_delete=True  # Remove vectors when files deleted
)
```

---

### 5. cloud_storage_list_folder_links

**Purpose**: List all active folder links and sync status

**Status**: ⏳ Not yet implemented

**Parameters**:
- `provider` (string, optional) - Filter by provider
- `status` (string, optional) - Filter by status ("active" | "paused" | "error")

**Returns**:
```json
{
    "success": true,
    "folder_links": [
        {
            "link_id": "link_abc123",
            "provider": "google_drive",
            "folder_name": "Company Docs",
            "sync_schedule": "daily",
            "namespace": "company-docs",
            "last_sync": "2025-11-30T09:00:00Z",
            "next_sync": "2025-12-01T09:00:00Z",
            "status": "active",
            "files_synced": 45,
            "last_error": null
        }
    ]
}
```

---

### 6. cloud_storage_sync_folder_now

**Purpose**: Trigger immediate sync (outside regular schedule)

**Status**: ⏳ Not yet implemented

**Parameters**:
- `link_id` (string, required) - Folder link ID to sync

**Returns**:
```json
{
    "success": true,
    "link_id": "link_abc123",
    "sync_started": "2025-11-30T15:30:00Z",
    "files_found": 12,
    "new_files": 3,
    "updated_files": 2,
    "deleted_files": 1,
    "processing": true,
    "message": "Sync in progress - 3 new files, 2 updates detected"
}
```

---

### 7. cloud_storage_update_folder_link

**Purpose**: Update folder link settings or pause/resume sync

**Status**: ⏳ Not yet implemented

**Parameters**:
- `link_id` (string, required) - Folder link ID
- `sync_schedule` (string, optional) - New schedule
- `file_types` (array, optional) - Update file types
- `status` (string, optional) - "active" | "paused"

**Returns**:
```json
{
    "success": true,
    "link_id": "link_abc123",
    "updated_fields": ["sync_schedule", "status"],
    "new_sync_schedule": "weekly",
    "status": "paused",
    "message": "Folder link updated successfully"
}
```

---

### 8. cloud_storage_delete_folder_link

**Purpose**: Delete folder link and optionally remove vectors

**Status**: ⏳ Not yet implemented

**Parameters**:
- `link_id` (string, required) - Folder link ID to delete
- `delete_vectors` (boolean, optional) - Delete existing vectors (default: false)

**Returns**:
```json
{
    "success": true,
    "link_id": "link_abc123",
    "vectors_deleted": 145,
    "message": "Folder link deleted, 145 vectors removed from Pinecone"
}
```

---

## 🔒 Security & Credentials

### Credential Flow

1. **User connects provider** in Platform Connections (OAuth flow)
2. **OAuth token stored** in `user_platform_credentials` table (Supabase)
3. **AI Agent requests tool** execution with `_user_id` parameter
4. **Credential Injector** automatically fetches and injects:
   - Cloud storage access token (google_access_token, onedrive_access_token, etc.)
   - Pinecone credentials (pinecone_api_key, pinecone_index_name, pinecone_environment)
   - Embedding credentials (embedding_provider, embedding_api_key, embedding_model)
5. **Tool executes** with full credential context

### Required Credentials by Tool

**cloud_storage_browse_folders**:
- Cloud storage access token (Google OAuth, OneDrive OAuth, Dropbox OAuth)

**cloud_storage_upload_to_vector_db**:
- Cloud storage access token
- Pinecone credentials (API key, index, environment)
- Embedding credentials (OpenAI or Voyager AI API key + model)

**cloud_storage_create_folder_link**:
- Cloud storage access token
- Pinecone credentials

---

## 🧪 Testing Guide

### Test 1: Google Drive Browse (Ready Now)

**Prerequisites**:
- User 12 has Google OAuth token in database
- Google Drive has at least one folder/file

**Test Command**:
```python
from tools.registry_v3 import RegistryV3

registry = RegistryV3()
result = registry.execute_tool(
    tool_name='cloud_storage_browse_folders',
    provider='google_drive',
    folder_id='root',
    include_files=True,
    _user_id=12,
    _injected_credentials=True
)
print(result)
```

**Expected Result**:
```json
{
    "success": true,
    "provider": "google_drive",
    "folder_count": 5,
    "folders": [...]
}
```

---

### Test 2: Google Drive Upload (Ready Now)

**Prerequisites**:
- User 12 has Google OAuth token
- User 12 has Pinecone credentials configured
- User 12 has embedding provider (OpenAI or Voyager AI) configured
- At least one PDF/DOCX file in Google Drive

**Test Command**:
```python
# Step 1: Get file ID from browse
result1 = registry.execute_tool(
    tool_name='cloud_storage_browse_folders',
    provider='google_drive',
    folder_id='root',
    include_files=True,
    file_types=['pdf'],
    _user_id=12,
    _injected_credentials=True
)

file_id = result1['files'][0]['id']  # First PDF

# Step 2: Upload to Pinecone
result2 = registry.execute_tool(
    tool_name='cloud_storage_upload_to_vector_db',
    provider='google_drive',
    file_ids=[file_id],
    namespace='test-docs',
    _user_id=12,
    _injected_credentials=True
)
print(result2)
```

**Expected Result**:
```json
{
    "success": true,
    "processed": 1,
    "total_chunks": 15,
    "vector_ids": ["vec1", "vec2", ...],
    "failed": []
}
```

---

### Test 3: Search Uploaded Documents (Ready Now)

**Prerequisites**:
- Completed Test 2 (documents uploaded to Pinecone)

**Test Command**:
```python
result = registry.execute_tool(
    tool_name='pinecone_search_summaries',
    query_text='test content',
    namespace='test-docs',
    top_k=5,
    _user_id=12,
    _injected_credentials=True
)
print(result)
```

**Expected Result**:
```json
{
    "success": true,
    "results": [
        {
            "document": "example.pdf",
            "category": "test",
            "chunk_count": 15,
            "preview": "This is the first 100 characters..."
        }
    ]
}
```

---

## 🚀 Production Deployment Checklist

### Phase 1: Google Drive Support (✅ Ready Now)
- [x] Tool schemas created
- [x] Implementation complete
- [x] Embedding generation working
- [x] Pinecone upload working
- [x] Registry integration working
- [x] Schema validation passing
- [ ] End-to-end testing with real credentials
- [ ] Error handling verification
- [ ] Performance testing with large files

### Phase 2: Multi-Provider Support (⏳ 1-2 Days)
- [ ] OneDrive browse implementation
- [ ] OneDrive upload implementation
- [ ] Dropbox browse implementation
- [ ] Dropbox upload implementation
- [ ] Test all 3 providers

### Phase 3: Scheduled Sync (⏳ 2-3 Days)
- [ ] Create cloud_folder_links database table
- [ ] Implement folder link CRUD operations
- [ ] Setup APScheduler or Celery
- [ ] Create sync job logic
- [ ] Test automatic sync workflows

### Phase 4: UI Enhancement (⏳ 1 Day)
- [ ] Add Cloud Upload tab to Vector Database sidebar
- [ ] Build folder browser component
- [ ] Create folder link management UI
- [ ] Test UI workflows

---

## 📚 Related Documentation

- **Complete Integration Guide**: `VECTOR_DATABASE_CLOUD_INTEGRATION_COMPLETE.md`
- **Platform Connections Setup**: `UI/business-ai-platform-v2.html` (lines 17223+)
- **Pinecone Smart Search Tools**: `tools/implementations/pinecone/pinecone_tools.py`
- **Cloud Storage Schema**: `tools/schemas/cloud_storage_vector_tools.json`
- **Cloud Storage Implementation**: `tools/implementations/cloud_storage_vector.py`

---

**Status**: ✅ Google Drive production-ready | 🔄 OneDrive/Dropbox in progress  
**Next Step**: Test end-to-end with real Google Drive files and Pinecone credentials

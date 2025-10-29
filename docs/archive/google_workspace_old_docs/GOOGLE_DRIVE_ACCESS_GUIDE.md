# 📁 Google Drive Access - Complete Guide

**Date:** October 27, 2025  
**Status:** ✅ **FULLY IMPLEMENTED**

---

## 🎯 Answer: YES - You Can Access Google Drives!

Your AI Agent has **full Google Drive access** with 15 different functions already implemented in the `google_workspace` package.

---

## 🔐 How Authentication Works

### **Current Setup: Service Account**

The system uses a **Service Account** (`vet-success-academy@appspot.gserviceaccount.com`) which:

✅ **Can access:**
- Files/folders it creates
- Files/folders shared with it
- Files/folders in Google Workspace domains (with domain-wide delegation)

❌ **Cannot access (by default):**
- Personal user files (unless explicitly shared)
- Files in user's "My Drive" (unless shared)

### **To Access User Files:**

**Option 1: Share Files with Service Account** (Easiest)
- User shares file/folder with `vet-success-academy@appspot.gserviceaccount.com`
- Service account can then read/write those files
- Works immediately, no configuration needed

**Option 2: Domain-Wide Delegation** (For Google Workspace)
- If users are on same Google Workspace domain
- Enable domain-wide delegation for service account
- Service account can impersonate users and access their files

**Option 3: OAuth User Authentication** (Most Flexible)
- Implement OAuth flow for users to grant access
- Each user authenticates and grants permissions
- Service acts on behalf of authenticated user

---

## 📋 Available Google Drive Functions (15 Total)

### **1. File Listing & Search**

**`google_drive_list_files(max_results=10, query=None, order_by=None)`**
```python
# List all files
files = google_drive_list_files(max_results=50)

# Search for specific files
files = google_drive_list_files(
    query="name contains 'report' and mimeType='application/pdf'"
)

# Ordered results
files = google_drive_list_files(
    order_by="modifiedTime desc",
    max_results=20
)
```

**`google_drive_search_files(query, max_results=10)`**
```python
# Search by name
results = google_drive_search_files("Budget 2025")

# Search by type
results = google_drive_search_files("mimeType='application/pdf'")
```

### **2. File Metadata**

**`google_drive_get_file(file_id, fields='*')`**
```python
# Get full file details
file_info = google_drive_get_file('1abc...xyz')

# Get specific fields
file_info = google_drive_get_file(
    '1abc...xyz',
    fields='name,mimeType,size,owners'
)
```

### **3. File Upload & Download**

**`google_drive_upload_file(file_path, name=None, mime_type=None, parent_folder_id=None)`**
```python
# Upload a file
result = google_drive_upload_file(
    file_path='C:/reports/monthly.pdf',
    name='Monthly Report',
    parent_folder_id='1abc...xyz'  # Optional folder
)
```

**`google_drive_export_file(file_id, mime_type)`**
```python
# Export Google Doc as PDF
pdf_content = google_drive_export_file(
    file_id='1abc...xyz',
    mime_type='application/pdf'
)

# Export Google Sheet as Excel
excel_content = google_drive_export_file(
    file_id='1abc...xyz',
    mime_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
)
```

### **4. File Management**

**`google_drive_update_file(file_id, file_path=None, name=None, description=None)`**
```python
# Update file content and name
google_drive_update_file(
    file_id='1abc...xyz',
    file_path='C:/new_version.pdf',
    name='Updated Report'
)
```

**`google_drive_delete_file(file_id)`**
```python
# Move to trash
google_drive_delete_file('1abc...xyz')
```

**`google_drive_restore_file(file_id)`**
```python
# Restore from trash
google_drive_restore_file('1abc...xyz')
```

**`google_drive_copy_file(file_id, name=None, parent_folder_id=None)`**
```python
# Copy a file
copy = google_drive_copy_file(
    file_id='1abc...xyz',
    name='Report Copy',
    parent_folder_id='1folder...xyz'
)
```

**`google_drive_move_file(file_id, new_parent_folder_id, previous_parent_folder_id=None)`**
```python
# Move file to different folder
google_drive_move_file(
    file_id='1abc...xyz',
    new_parent_folder_id='1newfolder...xyz'
)
```

### **5. Folder Operations**

**`google_drive_create_folder(name, parent_folder_id=None)`**
```python
# Create root folder
folder = google_drive_create_folder('Project Reports')

# Create nested folder
subfolder = google_drive_create_folder(
    name='2025 Reports',
    parent_folder_id=folder['id']
)
```

### **6. Sharing & Permissions**

**`google_drive_share_file(file_id, email, role='reader', type='user')`**
```python
# Share with user (read-only)
google_drive_share_file(
    file_id='1abc...xyz',
    email='user@example.com',
    role='reader'
)

# Share with edit access
google_drive_share_file(
    file_id='1abc...xyz',
    email='user@example.com',
    role='writer'
)

# Share with anyone (public link)
google_drive_share_file(
    file_id='1abc...xyz',
    email='',
    role='reader',
    type='anyone'
)
```

**`google_drive_list_permissions(file_id)`**
```python
# See who has access
permissions = google_drive_list_permissions('1abc...xyz')
```

**`google_drive_remove_permission(file_id, permission_id)`**
```python
# Remove access
google_drive_remove_permission('1abc...xyz', 'permission123')
```

### **7. Storage Management**

**`google_drive_get_storage_quota()`**
```python
# Check storage usage
quota = google_drive_get_storage_quota()
# Returns: {used, total, percentage}
```

---

## 🚀 Real-World Usage Examples

### **Example 1: Upload Report and Share with Team**

```python
from google_workspace import (
    google_drive_create_folder,
    google_drive_upload_file,
    google_drive_share_file
)

# Create project folder
folder = google_drive_create_folder('Q4 2025 Reports')

# Upload report
file = google_drive_upload_file(
    file_path='C:/reports/q4_summary.pdf',
    name='Q4 Financial Summary',
    parent_folder_id=folder['id']
)

# Share with team
team_emails = [
    'manager@company.com',
    'analyst@company.com',
    'director@company.com'
]

for email in team_emails:
    google_drive_share_file(
        file_id=file['id'],
        email=email,
        role='reader'
    )

print(f"✅ Report uploaded and shared with {len(team_emails)} people")
print(f"📁 Link: https://drive.google.com/file/d/{file['id']}")
```

### **Example 2: Find and Download Recent Files**

```python
from google_workspace import google_drive_list_files, google_drive_export_file

# Find PDFs modified in last 7 days
files = google_drive_list_files(
    query="mimeType='application/pdf' and modifiedTime > '2025-10-20'",
    order_by="modifiedTime desc",
    max_results=10
)

# Export each to local drive
for file in files['files']:
    content = google_drive_export_file(
        file_id=file['id'],
        mime_type='application/pdf'
    )
    
    with open(f"C:/downloads/{file['name']}", 'wb') as f:
        f.write(content)
    
    print(f"✅ Downloaded: {file['name']}")
```

### **Example 3: Create Organized Folder Structure**

```python
from google_workspace import google_drive_create_folder

# Create main project folder
main = google_drive_create_folder('MiniVet Guide Project')

# Create subfolders
subfolders = [
    'Documents',
    'Spreadsheets',
    'Presentations',
    'Images',
    'Videos'
]

for subfolder_name in subfolders:
    subfolder = google_drive_create_folder(
        name=subfolder_name,
        parent_folder_id=main['id']
    )
    print(f"✅ Created: {subfolder_name}")

print(f"📁 Main folder: https://drive.google.com/drive/folders/{main['id']}")
```

---

## 🤖 Using with AI Agent (CHAT Command)

Once you start the AI Agent with `BISTART`, you can use natural language:

```powershell
BISTART

# Wait for server to start, then:

CHAT List all PDF files in my Google Drive

CHAT Create a folder called "Client Reports" and upload the file at C:/reports/summary.pdf

CHAT Share the file with ID 1abc...xyz with john@example.com as a reader

CHAT Find all spreadsheets modified this week

CHAT Create a folder structure for our new project

CHAT Check my Google Drive storage quota

CHAT Download all files from the folder "Q4 Reports"
```

The AI will automatically:
- Choose the appropriate Google Drive function
- Execute the operation
- Return the results in natural language

---

## 🔐 Accessing User's Personal Drives

### **Current Limitation:**

The service account can only access:
- Files it created
- Files/folders explicitly shared with `vet-success-academy@appspot.gserviceaccount.com`

### **To Access User Files (3 Options):**

#### **Option 1: User Shares with Service Account (Easiest)**

1. User goes to their Google Drive
2. Right-click file/folder → Share
3. Enter: `vet-success-academy@appspot.gserviceaccount.com`
4. Choose permission level (Viewer/Editor)
5. Click Send

**✅ Now the AI Agent can access that file/folder!**

#### **Option 2: Domain-Wide Delegation (Google Workspace Only)**

If your users are on a Google Workspace domain (e.g., @vetsuccessacademy.com):

1. **Admin Console:** https://admin.google.com
2. **Security** → **API Controls** → **Domain-wide Delegation**
3. Add service account client ID
4. Grant scopes:
   - `https://www.googleapis.com/auth/drive`
   - `https://www.googleapis.com/auth/drive.file`

**Code change needed:**
```python
# Impersonate a user
credentials = credentials.with_subject('user@domain.com')
```

#### **Option 3: OAuth User Authentication (Best for Multi-User)**

Implement OAuth flow where:
1. User clicks "Connect Google Drive"
2. Authenticates with their Google account
3. Grants permissions to your app
4. App uses their credentials (not service account)

**This requires:**
- OAuth2 client ID/secret from Google Cloud Console
- User consent flow implementation
- Token storage per user

---

## 📊 Available Functions Summary

| Category | Function | What It Does |
|----------|----------|--------------|
| **Listing** | `google_drive_list_files` | List files with filters |
| | `google_drive_search_files` | Search by name/type |
| **Metadata** | `google_drive_get_file` | Get file details |
| **Upload/Download** | `google_drive_upload_file` | Upload files |
| | `google_drive_export_file` | Download/export files |
| **Management** | `google_drive_update_file` | Update file content |
| | `google_drive_delete_file` | Move to trash |
| | `google_drive_restore_file` | Restore from trash |
| | `google_drive_copy_file` | Duplicate file |
| | `google_drive_move_file` | Move to folder |
| **Folders** | `google_drive_create_folder` | Create folders |
| **Sharing** | `google_drive_share_file` | Share with users |
| | `google_drive_list_permissions` | List who has access |
| | `google_drive_remove_permission` | Remove access |
| **Storage** | `google_drive_get_storage_quota` | Check storage usage |

**Total: 15 functions covering all major Drive operations**

---

## 🧪 Test Drive Access

```powershell
cd C:\Users\gpoli\GIT\AI_agents
python -c "from google_workspace import google_drive_list_files, google_drive_create_folder; files = google_drive_list_files(); print(f'Found {files[\"count\"]} files'); folder = google_drive_create_folder('Test AI Agent Access'); print(f'Created folder: {folder[\"name\"]}')"
```

---

## 📚 Related Documentation

- `google_workspace/__init__.py` - Package exports
- `google_workspace/google_drive.py` - Implementation
- `google_workspace/google_auth_helper.py` - Authentication
- `tools/schemas/google_drive_tools.json` - AI tool definitions

---

## 🎯 Next Steps

1. **Test basic access:**
   ```powershell
   BISTART
   CHAT List files in my Google Drive
   ```

2. **Create test folder:**
   ```powershell
   CHAT Create a folder called "AI Agent Test"
   ```

3. **To access user files:**
   - Have users share folders with `vet-success-academy@appspot.gserviceaccount.com`
   - OR implement domain-wide delegation
   - OR implement OAuth user authentication

---

**Summary:** ✅ YES, full Google Drive access is implemented with 15 functions. Service account can access files it creates or files shared with it. For accessing user's personal files, users need to share folders with the service account email.

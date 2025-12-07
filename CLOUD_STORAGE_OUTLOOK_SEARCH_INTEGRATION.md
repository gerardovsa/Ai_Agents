# Cloud Storage & Outlook Universal Search Integration
**Date:** December 8, 2025  
**Status:** ✅ COMPLETE - Ready for Testing  
**Integration Type:** Google Drive, OneDrive, SharePoint, Outlook Email Search

---

## 🎯 Overview

Added **4 new cloud-based search sources** to the Universal Search system with proper credential-based authentication. Users can now search across:

### Google Services (using Google OAuth)
- **Google Drive** - Files, folders, shared documents
- **Gmail** - Emails (already implemented)

### Microsoft Services (using Microsoft OAuth)
- **OneDrive** - Personal cloud storage files
- **SharePoint** - Team sites and document libraries
- **Outlook** - Email messages

**Key Feature:** Only searches sources where user has connected their OAuth credentials - follows existing Gmail/Slack pattern.

---

## 📁 Files Modified

### 1. Backend: `AI_infrastructure/routes/universal_search_routes.py`

**Import Changes (Line 41-51):**
```python
from AI_infrastructure.auth.user_auth import require_auth, UserAuthManager

# Initialize auth manager for credential access
auth_manager = UserAuthManager()
```

**Parameters Added (Line 167-180):**
```python
include_google_drive = data.get('include_google_drive', 'google-drive' in sources)
include_onedrive = data.get('include_onedrive', 'onedrive' in sources)
include_sharepoint = data.get('include_sharepoint', 'sharepoint' in sources)
include_outlook = data.get('include_outlook', 'outlook' in sources)
```

**New Sections Added:**

#### Section 8: Google Drive Search (Lines ~720-765)
```python
if include_google_drive:
    google_creds = auth_manager.get_platform_credentials(user_id, 'google')
    if google_creds and google_creds.get('access_token'):
        # Use Google Drive API v3
        drive_query = f"name contains '{query}' or fullText contains '{query}'"
        response = requests.get(
            'https://www.googleapis.com/drive/v3/files',
            params={
                'q': drive_query,
                'pageSize': limit,
                'fields': 'files(id,name,mimeType,createdTime,modifiedTime,size,webViewLink,owners)'
            },
            headers={'Authorization': f'Bearer {google_creds.get("access_token")}'}
        )
```

#### Section 9: OneDrive Search (Lines ~766-810)
```python
if include_onedrive:
    microsoft_creds = auth_manager.get_platform_credentials(user_id, 'microsoft')
    if microsoft_creds and microsoft_creds.get('access_token'):
        # Use Microsoft Graph API
        response = requests.get(
            f'https://graph.microsoft.com/v1.0/me/drive/search(q=\'{query}\')',
            params={
                '$top': limit,
                '$select': 'id,name,createdDateTime,lastModifiedDateTime,size,webUrl,file,folder'
            },
            headers={'Authorization': f'Bearer {microsoft_creds.get("access_token")}'}
        )
```

#### Section 10: SharePoint Search (Lines ~811-870)
```python
if include_sharepoint:
    microsoft_creds = auth_manager.get_platform_credentials(user_id, 'microsoft')
    if microsoft_creds:
        # Get user's SharePoint sites
        sites_response = requests.get(
            'https://graph.microsoft.com/v1.0/sites?search=*',
            headers={'Authorization': f'Bearer {microsoft_creds.get("access_token")}'}
        )
        
        # Search each site's drive (first 3 sites, 5 results each)
        for site in sites[:3]:
            search_response = requests.get(
                f'https://graph.microsoft.com/v1.0/sites/{site_id}/drive/search(q=\'{query}\')',
                params={'$top': 5}
            )
```

#### Section 11: Outlook Search (Lines ~871-920)
```python
if include_outlook:
    microsoft_creds = auth_manager.get_platform_credentials(user_id, 'microsoft')
    if microsoft_creds:
        # Search Outlook emails
        response = requests.get(
            'https://graph.microsoft.com/v1.0/me/messages',
            params={
                '$search': f'"{query}"',
                '$top': limit,
                '$select': 'id,subject,from,receivedDateTime,bodyPreview,isRead,hasAttachments,webLink'
            },
            headers={
                'Authorization': f'Bearer {microsoft_creds.get("access_token")}',
                'ConsistencyLevel': 'eventual'  # Required for search
            }
        )
```

### 2. Frontend: `UI/modules_internal/universal-search/universal-search.js`

**Checkbox Sources Updated (Line 347-360):**
```javascript
const sources = [
    { id: 'documents', label: 'Documents', icon: 'fa-file-alt' },
    { id: 'vector-database', label: 'Vector Database (AI Search)', icon: 'fa-database' },
    { id: 'threads', label: 'Threads', icon: 'fa-comments' },
    { id: 'messages', label: 'Messages', icon: 'fa-envelope' },
    { id: 'synergy', label: 'Synergy Sessions', icon: 'fa-users' },
    { id: 'automations', label: 'Automations', icon: 'fa-robot' },
    { id: 'gmail', label: 'Gmail', icon: 'fa-google' },
    { id: 'outlook', label: 'Outlook', icon: 'fa-envelope-open' },       // NEW
    { id: 'slack', label: 'Slack', icon: 'fa-slack' },
    { id: 'google-drive', label: 'Google Drive', icon: 'fa-google-drive' }, // NEW
    { id: 'onedrive', label: 'OneDrive', icon: 'fa-cloud' },             // NEW
    { id: 'sharepoint', label: 'SharePoint', icon: 'fa-share-alt' },     // NEW
    { id: 'xero', label: 'Xero Accounting', icon: 'fa-file-invoice' },
    { id: 'inhouseprint', label: 'InHousePrint Projects', icon: 'fa-print' }
];
```

**Icon Mappings (Lines 607-620):**
```javascript
getSourceIcon(source) {
    const icons = {
        'google-drive': 'fab fa-google-drive',
        onedrive: 'fas fa-cloud',
        sharepoint: 'fas fa-share-alt',
        outlook: 'fas fa-envelope-open',
        // ... other sources
    };
}
```

**Label Mappings (Lines 622-635):**
```javascript
getSourceLabel(source) {
    const labels = {
        'google-drive': 'Google Drive',
        onedrive: 'OneDrive',
        sharepoint: 'SharePoint',
        outlook: 'Outlook',
        // ... other sources
    };
}
```

---

## 🔌 Integration Details

### Google Drive Search

**API:** Google Drive API v3  
**Endpoint:** `https://www.googleapis.com/drive/v3/files`  
**Authentication:** Google OAuth access token from `user_platform_credentials` table  
**Credential Platform:** `google`

**Search Capabilities:**
- **Query Syntax:** `name contains 'query' or fullText contains 'query'`
- **Searches:** File names, file content (Google Docs, Sheets, Slides)
- **Returns:** 
  - File ID, name, MIME type
  - Created/modified timestamps
  - File size, owner
  - Web view link

**Result Format:**
```json
{
  "type": "file",
  "id": "1ABC123...",
  "name": "Budget 2025.xlsx",
  "mime_type": "application/vnd.google-apps.spreadsheet",
  "created": "2025-01-01T10:00:00Z",
  "modified": "2025-12-01T15:30:00Z",
  "size": "45678",
  "link": "https://docs.google.com/spreadsheets/d/...",
  "owner": "John Smith"
}
```

### OneDrive Search

**API:** Microsoft Graph API v1.0  
**Endpoint:** `https://graph.microsoft.com/v1.0/me/drive/search(q='query')`  
**Authentication:** Microsoft OAuth access token from `user_platform_credentials` table  
**Credential Platform:** `microsoft`

**Search Capabilities:**
- **Query Syntax:** OData search query
- **Searches:** File names, file content
- **Returns:**
  - File/folder ID, name
  - Created/modified timestamps
  - File size, MIME type
  - Web URL

**Result Format:**
```json
{
  "type": "file",
  "id": "01ABC123...",
  "name": "Annual Report.docx",
  "created": "2025-01-15T09:00:00Z",
  "modified": "2025-12-05T14:20:00Z",
  "size": "123456",
  "link": "https://onedrive.live.com/...",
  "mime_type": "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
}
```

### SharePoint Search

**API:** Microsoft Graph API v1.0  
**Endpoint:** `https://graph.microsoft.com/v1.0/sites/{site-id}/drive/search(q='query')`  
**Authentication:** Microsoft OAuth access token from `user_platform_credentials` table  
**Credential Platform:** `microsoft`

**Search Capabilities:**
- **Multi-Site Search:** Searches user's first 3 SharePoint sites
- **Per-Site Limit:** 5 results per site (max 15 total)
- **Searches:** Document libraries across team sites
- **Returns:**
  - File ID, name, site name
  - Created/modified timestamps
  - File size
  - Web URL

**Result Format:**
```json
{
  "type": "file",
  "id": "01XYZ789...",
  "name": "Project Plan.mpp",
  "site": "Marketing Team Site",
  "created": "2025-02-01T11:00:00Z",
  "modified": "2025-12-07T16:45:00Z",
  "size": "234567",
  "link": "https://company.sharepoint.com/sites/marketing/..."
}
```

**Note:** SharePoint search is limited to 3 sites to prevent timeout. Sites are sorted by relevance from Graph API.

### Outlook Search

**API:** Microsoft Graph API v1.0  
**Endpoint:** `https://graph.microsoft.com/v1.0/me/messages`  
**Authentication:** Microsoft OAuth access token from `user_platform_credentials` table  
**Credential Platform:** `microsoft`  
**Special Header:** `ConsistencyLevel: eventual` (required for $search)

**Search Capabilities:**
- **Query Syntax:** Full-text search with `$search` parameter
- **Searches:** Email subject, body, sender, recipients
- **Ordering:** Sorted by received date (newest first)
- **Returns:**
  - Message ID, subject
  - Sender email and name
  - Received timestamp
  - Body preview (first 255 chars)
  - Read status, attachment flag
  - Web link

**Result Format:**
```json
{
  "type": "email",
  "id": "AAMkAGI...",
  "subject": "Budget Approval Request",
  "from": "john.smith@company.com",
  "from_name": "John Smith",
  "received": "2025-12-08T08:30:00Z",
  "preview": "Hi team, please review the attached budget proposal for Q1 2025...",
  "is_read": false,
  "has_attachments": true,
  "link": "https://outlook.office.com/mail/..."
}
```

---

## 🔐 Authentication & Credentials

### Credential Storage

All OAuth credentials are stored in the `user_platform_credentials` table:

```sql
SELECT * FROM ai_infrastructure.user_platform_credentials
WHERE user_id = ? AND platform IN ('google', 'microsoft');
```

**Google Platform:**
```json
{
  "access_token": "ya29.a0AfH6...",
  "refresh_token": "1//0gH...",
  "token_expiry": "2025-12-08T10:00:00Z"
}
```

**Microsoft Platform:**
```json
{
  "access_token": "eyJ0eXAiOiJKV1QiLC...",
  "refresh_token": "0.AXAA...",
  "token_expiry": "2025-12-08T10:00:00Z"
}
```

### Credential Checking Pattern

All new search sections follow this pattern:

```python
# 1. Check if user has connected this platform
platform_creds = auth_manager.get_platform_credentials(user_id, 'google' or 'microsoft')

# 2. Verify access token exists
if platform_creds and platform_creds.get('access_token'):
    # 3. Make API call with Bearer token
    headers = {'Authorization': f'Bearer {platform_creds.get("access_token")}'}
    response = requests.get(api_endpoint, headers=headers)
    
    # 4. Handle success/error
    if response.status_code == 200:
        results['sources']['source-name'] = {
            'count': len(items),
            'results': items
        }
    else:
        results['sources']['source-name'] = {
            'error': f'API error: {response.status_code}'
        }
else:
    # 5. Return error if not connected
    results['sources']['source-name'] = {
        'error': 'Credentials not found'
    }
```

### OAuth Setup Required

**For Google Services (Drive, Gmail):**
1. User must complete OAuth flow at `/api/google/auth`
2. Credentials stored with platform='google'
3. Refresh tokens auto-renewed by `UserAuthManager`

**For Microsoft Services (OneDrive, SharePoint, Outlook):**
1. User must complete OAuth flow at `/api/microsoft/auth`
2. Credentials stored with platform='microsoft'
3. Refresh tokens auto-renewed by `UserAuthManager`

---

## 🎨 User Interface

### Source Selection Panel

```
☐ Documents
☐ Vector Database (AI Search)
☐ Threads
☐ Messages
☐ Synergy Sessions
☐ Automations
☐ Gmail
☑ Outlook               ← NEW (grayed out if not connected)
☐ Slack
☑ Google Drive          ← NEW (grayed out if not connected)
☑ OneDrive              ← NEW (grayed out if not connected)
☑ SharePoint            ← NEW (grayed out if not connected)
☐ Xero Accounting
☐ InHousePrint Projects
```

### Search Result Display

**Google Drive Result:**
```
📄 Budget 2025.xlsx
   Owner: John Smith
   Modified: 2 days ago
   Size: 44.6 KB
   Type: Google Sheets
   [Open in Drive]
```

**OneDrive Result:**
```
📄 Annual Report.docx
   Modified: 3 days ago
   Size: 120.6 KB
   Type: Word Document
   [Open in OneDrive]
```

**SharePoint Result:**
```
📄 Project Plan.mpp
   Site: Marketing Team Site
   Modified: 1 day ago
   Size: 229.1 KB
   [Open in SharePoint]
```

**Outlook Result:**
```
✉️ Budget Approval Request
   From: John Smith (john.smith@company.com)
   Received: Today at 8:30 AM
   Preview: Hi team, please review the attached budget proposal...
   📎 Has attachments | Unread
   [Open in Outlook]
```

---

## 🚀 How to Use

### 1. Connect OAuth Accounts

**Google Services:**
```
Navigate to: Account Settings → Integrations → Google
Click: "Connect Google Account"
Authorize: Drive, Gmail access
```

**Microsoft Services:**
```
Navigate to: Account Settings → Integrations → Microsoft
Click: "Connect Microsoft Account"
Authorize: OneDrive, SharePoint, Outlook access
```

### 2. Enable Search Sources

In Universal Search module:
- ☑ Check **Google Drive** (if Google connected)
- ☑ Check **OneDrive** (if Microsoft connected)
- ☑ Check **SharePoint** (if Microsoft connected)
- ☑ Check **Outlook** (if Microsoft connected)

### 3. Search Queries

**Find document:**
```
Query: "budget 2025"
Results:
  ✅ Google Drive: Budget 2025.xlsx
  ✅ OneDrive: Budget 2025 - Draft.docx
  ✅ SharePoint: 2025 Budget Proposal.pdf
```

**Find email:**
```
Query: "invoice from john"
Results:
  ✅ Gmail: 3 emails
  ✅ Outlook: Invoice INV-2025-001 from john.smith@company.com
```

**Cross-platform search:**
```
Query: "project plan"
Results:
  ✅ Documents: Internal project plans (PostgreSQL)
  ✅ Google Drive: Project Plan 2025.gsheet
  ✅ SharePoint: Marketing Project.mpp
  ✅ OneDrive: Development Plan.docx
```

---

## ✅ Testing Checklist

### Backend Tests
- [ ] Google Drive search returns files when Google credentials present
- [ ] Google Drive returns error when credentials missing
- [ ] OneDrive search returns files when Microsoft credentials present
- [ ] SharePoint searches multiple sites (max 3)
- [ ] SharePoint returns combined results from all sites
- [ ] Outlook search returns emails with full metadata
- [ ] Outlook requires `ConsistencyLevel: eventual` header
- [ ] All sources handle 401 Unauthorized (expired token)
- [ ] All sources handle 403 Forbidden (insufficient permissions)
- [ ] All sources handle 429 Rate Limit Exceeded

### Frontend Tests
- [ ] Google Drive checkbox grayed out when not connected
- [ ] OneDrive checkbox grayed out when not connected
- [ ] SharePoint checkbox grayed out when not connected
- [ ] Outlook checkbox grayed out when not connected
- [ ] Icons display correctly (fa-google-drive, fa-cloud, fa-share-alt, fa-envelope-open)
- [ ] Results grouped by source
- [ ] Result cards show all fields correctly
- [ ] Click on result opens file/email in new tab

### Integration Tests
- [ ] Search with all cloud sources enabled
- [ ] Search with only Google services enabled
- [ ] Search with only Microsoft services enabled
- [ ] Cross-reference: Same file in Drive and OneDrive
- [ ] Performance acceptable (<3 seconds for all sources)
- [ ] No duplicate results between sources

---

## 🐛 Known Issues & Limitations

### Google Drive
1. **Content Search Limitations:**
   - Only works for Google Workspace files (Docs, Sheets, Slides)
   - Binary files (PDF, DOCX uploaded) search by name only
   - Consider adding OCR for uploaded PDFs

2. **Shared Drive Access:**
   - Currently searches "My Drive" only
   - Shared drives require additional API calls
   - Future: Add checkbox to include/exclude shared drives

3. **Rate Limits:**
   - 1,000 queries per 100 seconds per user
   - Implement caching for repeated queries

### OneDrive
1. **Search Syntax:**
   - Simple text match, no advanced operators
   - No wildcard support in Graph API search
   - Can't filter by file type in query

2. **Business vs Personal:**
   - Uses `/me/drive` (personal OneDrive)
   - Business OneDrive may need different endpoint
   - Detect account type and adjust endpoint

### SharePoint
1. **Site Limit:**
   - Hardcoded to first 3 sites (prevent timeout)
   - User might have 50+ sites
   - Future: Add site selection UI or search specific site

2. **Permissions:**
   - Only searches sites user has access to
   - No indication of restricted sites
   - Graph API handles permissions transparently

3. **Performance:**
   - 3 sites × 5 results = 15 API calls
   - Can be slow if sites have slow response
   - Consider parallel API calls with asyncio

### Outlook
1. **Search Limitations:**
   - $search requires `ConsistencyLevel: eventual`
   - May return stale results (5-10 min lag)
   - Not suitable for real-time search

2. **Folders:**
   - Searches all folders (Inbox, Sent, Drafts)
   - No folder filtering in query
   - Future: Add folder selection dropdown

3. **Attachments:**
   - Returns `has_attachments` flag only
   - Doesn't search attachment content
   - Doesn't return attachment filenames
   - Future: Add attachment metadata endpoint

### General
1. **Token Expiry:**
   - Access tokens expire after 1 hour (Google/Microsoft)
   - `UserAuthManager` should auto-refresh
   - If refresh fails, user must re-authenticate

2. **Error Messages:**
   - Generic errors shown to user
   - Doesn't distinguish between:
     - Network error
     - Invalid credentials
     - Insufficient permissions
     - Rate limit exceeded
   - Improve error handling with specific messages

---

## 🔄 Future Enhancements

### Short Term
1. **Add Dropbox Search:**
   - Use Dropbox API `/files/search_v2`
   - OAuth flow for Dropbox credentials
   - Search file names and content

2. **Add Box Search:**
   - Use Box API `/search`
   - OAuth flow for Box credentials

3. **Improve SharePoint:**
   - Let user select which sites to search
   - Remember user's preferred sites
   - Show site picker in UI

4. **Attachment Search:**
   - Extract attachment metadata from Outlook
   - Search attachment filenames
   - Show attachment count and types

### Long Term
1. **Unified File Deduplication:**
   - Detect same file across Drive, OneDrive, Dropbox
   - Compare by hash, size, name
   - Show "Available in 3 locations" badge

2. **Advanced Filtering:**
   - File type filters (PDF, DOCX, XLSX)
   - Date range filters
   - Owner/author filters
   - Folder/site filters

3. **Smart Suggestions:**
   - "Did you mean..." for typos
   - Related searches
   - Popular searches for this user

4. **Real-time Collaboration:**
   - Show who else is viewing/editing file
   - Live typing indicators for Google Docs
   - Recent collaborators

5. **Offline Cache:**
   - Cache recent search results
   - Search offline using IndexedDB
   - Sync when back online

---

## 📚 API References

### Google Drive API v3
- **Documentation:** https://developers.google.com/drive/api/v3/reference
- **Search Query Syntax:** https://developers.google.com/drive/api/v3/search-files
- **OAuth Scopes Required:**
  - `https://www.googleapis.com/auth/drive.readonly`
  - `https://www.googleapis.com/auth/drive.metadata.readonly`

### Microsoft Graph API v1.0
- **Documentation:** https://learn.microsoft.com/en-us/graph/api/overview
- **OneDrive Search:** https://learn.microsoft.com/en-us/graph/api/driveitem-search
- **SharePoint Search:** https://learn.microsoft.com/en-us/graph/api/site-search
- **Outlook Search:** https://learn.microsoft.com/en-us/graph/api/user-list-messages
- **OAuth Scopes Required:**
  - `Files.Read.All` (OneDrive/SharePoint)
  - `Mail.Read` (Outlook)
  - `Sites.Read.All` (SharePoint sites)

---

## 🎯 Success Criteria

✅ **Integration Complete** when:
1. Google Drive search returns files when credentials present
2. OneDrive search returns files when credentials present
3. SharePoint searches across multiple sites
4. Outlook search returns emails with metadata
5. UI shows grayed-out checkboxes when not connected
6. UI shows enabled checkboxes when connected
7. Results grouped correctly by source
8. Error messages shown when credentials missing
9. Performance acceptable (<3 seconds total)
10. No errors in console when sources disabled

---

## 📞 Support & Troubleshooting

### "Google Drive not returning results"
1. Check credentials: `SELECT * FROM user_platform_credentials WHERE platform='google'`
2. Verify access token not expired
3. Test Drive API directly: `curl -H "Authorization: Bearer TOKEN" https://www.googleapis.com/drive/v3/files`
4. Check OAuth scopes include `drive.readonly`

### "OneDrive returns 401 Unauthorized"
1. Access token expired - check `token_expiry` field
2. Trigger token refresh via `UserAuthManager`
3. If refresh fails, user must re-authenticate
4. Check Microsoft account status in Azure portal

### "SharePoint returns empty results"
1. User may not have access to any SharePoint sites
2. Check sites endpoint: `GET /v1.0/sites?search=*`
3. Verify `Sites.Read.All` permission granted
4. Some organizations disable SharePoint search API

### "Outlook search slow"
1. `ConsistencyLevel: eventual` causes delayed indexing
2. Results may be 5-10 minutes old
3. Use `/messages` with `$filter` for real-time (no $search)
4. Consider caching results for repeated queries

### "All sources show 'not connected'"
1. OAuth flow not completed
2. Check browser console for errors
3. Verify `/api/google/auth` and `/api/microsoft/auth` endpoints work
4. Check redirect URIs match OAuth app settings

---

**END OF DOCUMENTATION**

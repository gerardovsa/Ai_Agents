"""
Google Drive API Tool Implementations
=======================================

Implements Google Drive operations for file management, sharing, and storage.
"""

import os
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

try:
    from googleapiclient.http import MediaFileUpload, MediaIoBaseDownload
    from google_workspace.google_auth_helper import build_drive_service
    import io
    HAS_DRIVE_API = True
except ImportError:
    HAS_DRIVE_API = False
    print("⚠️ Google Drive API dependencies not available")


def _get_drive_service(user_id=None, injected_credentials=None):
    """Get authenticated Google Drive API service.

    Routing policy (Phase 3 — single shared contract):
      - When the caller supplies user context (``user_id`` + ``injected_credentials``),
        build the Drive service through the shared injector
        (``get_user_drive_service``) so proactive refresh, exact-row persistence,
        and storage-only enforcement are honoured. A missing/invalid user OAuth
        row raises — NEVER silently falls back to a service account.
      - When no user context is present at all, fall through to the legacy
        service-account helper. This is the only path that may use a service
        account, and only because the caller explicitly opted out of user OAuth.
    """
    if not HAS_DRIVE_API:
        raise Exception("Google Drive API not available - install google-api-python-client")

    if user_id and injected_credentials:
        # User context present — go through the shared injector.
        from AI_infrastructure.auth.credential_injector import get_user_drive_service
        return get_user_drive_service(user_id=user_id)

    # No user context — explicit service-account path. No fallback from a user OAuth
    # failure into this branch.
    return build_drive_service()


# ==================== FILE OPERATIONS ====================

def google_drive_list_files(max_results=10, query=None, order_by=None, page_token=None, _user_id=None, _injected_credentials=None, **kwargs):
    """List files in Drive
    
    Args:
        max_results: Maximum number of files to return
        query: Search query
        order_by: Sort order
        page_token: Page token for pagination
        _user_id: User ID for credential injection
        _injected_credentials: OAuth credentials dict
    """
    try:
        # Phase 3: route through the shared injector when user context is present
        service = _get_drive_service(user_id=_user_id, injected_credentials=_injected_credentials)
        
        params = {
            'pageSize': max_results,
            'fields': 'nextPageToken, files(id, name, mimeType, size, createdTime, modifiedTime, owners, parents)'
        }
        
        if query:
            params['q'] = query
        if order_by:
            params['orderBy'] = order_by
        if page_token:
            params['pageToken'] = page_token
        
        result = service.files().list(**params).execute()
        files = result.get('files', [])
        
        return {
            'files': files,
            'count': len(files),
            'next_page_token': result.get('nextPageToken')
        }
    
    except Exception as e:
        print(f" Failed to list files: {e}")
        raise


def google_drive_get_file(file_id, fields='*', _user_id=None, _injected_credentials=None, **kwargs):
    """Get file metadata
    
    Args:
        file_id: File ID
        fields: Fields to return
        _user_id: User ID for credential injection
        _injected_credentials: OAuth credentials dict
    """
    try:
        # Phase 3: route through the shared injector when user context is present
        service = _get_drive_service(user_id=_user_id, injected_credentials=_injected_credentials)
        
        file = service.files().get(fileId=file_id, fields=fields).execute()
        
        return file
    
    except Exception as e:
        print(f" Failed to get file: {e}")
        raise


def google_drive_upload_file(file_path, name=None, mime_type=None, parent_folder_id=None, _user_id=None, _injected_credentials=None, **kwargs):
    """Upload a file to Drive
    
    Args:
        file_path: Path to file to upload
        name: Optional name for file
        mime_type: Optional MIME type
        parent_folder_id: Optional parent folder ID
        _user_id: User ID for credential injection
        _injected_credentials: Flag for credential injection
    """
    try:
        # Phase 3: route through the shared injector when user context is present
        service = _get_drive_service(user_id=_user_id, injected_credentials=_injected_credentials)
        
        file_metadata = {'name': name or os.path.basename(file_path)}
        
        if parent_folder_id:
            file_metadata['parents'] = [parent_folder_id]
        
        media = MediaFileUpload(file_path, mimetype=mime_type, resumable=True)
        
        file = service.files().create(
            body=file_metadata,
            media_body=media,
            fields='id, name, mimeType, size, webViewLink'
        ).execute()
        
        return file
    
    except Exception as e:
        print(f" Failed to upload file: {e}")
        raise


def google_drive_update_file(file_id, file_path=None, name=None, description=None, _user_id=None, _injected_credentials=None, **kwargs):
    """Update an existing file
    
    Args:
        file_id: File ID to update
        file_path: Optional new file path
        name: Optional new name
        description: Optional new description
        _user_id: User ID for credential injection
        _injected_credentials: Flag for credential injection
    """
    try:
        # Phase 3: route through the shared injector when user context is present
        service = _get_drive_service(user_id=_user_id, injected_credentials=_injected_credentials)
        
        file_metadata = {}
        if name:
            file_metadata['name'] = name
        if description:
            file_metadata['description'] = description
        
        media = None
        if file_path:
            media = MediaFileUpload(file_path, resumable=True)
        
        file = service.files().update(
            fileId=file_id,
            body=file_metadata,
            media_body=media,
            fields='id, name, mimeType, modifiedTime'
        ).execute()
        
        return file
    
    except Exception as e:
        print(f" Failed to update file: {e}")
        raise


def google_drive_delete_file(file_id, _user_id=None, _injected_credentials=None, **kwargs):
    """Delete a file
    
    Args:
        file_id: File ID to delete
        _user_id: User ID for credential injection
        _injected_credentials: Flag for credential injection
    """
    try:
        # Phase 3: route through the shared injector when user context is present
        service = _get_drive_service(user_id=_user_id, injected_credentials=_injected_credentials)
        service.files().delete(fileId=file_id).execute()
        
        return {'deleted': True, 'file_id': file_id}
    
    except Exception as e:
        print(f" Failed to delete file: {e}")
        raise


# ==================== FOLDER OPERATIONS ====================

def google_drive_create_folder(name, parent_folder_id=None, _user_id=None, _injected_credentials=None, **kwargs):
    """Create a new folder
    
    Args:
        name: Folder name
        parent_folder_id: Optional parent folder ID
        _user_id: User ID for credential injection
        _injected_credentials: Flag for credential injection
    """
    try:
        # Phase 3: route through the shared injector when user context is present
        service = _get_drive_service(user_id=_user_id, injected_credentials=_injected_credentials)
        
        file_metadata = {
            'name': name,
            'mimeType': 'application/vnd.google-apps.folder'
        }
        
        if parent_folder_id:
            file_metadata['parents'] = [parent_folder_id]
        
        folder = service.files().create(
            body=file_metadata,
            fields='id, name, webViewLink'
        ).execute()
        
        return folder
    
    except Exception as e:
        print(f" Failed to create folder: {e}")
        raise


def google_drive_move_file(file_id, new_parent_folder_id, previous_parent_folder_id=None, _user_id=None, _injected_credentials=None, **kwargs):
    """Move a file to a different folder
    
    Args:
        file_id: File ID to move
        new_parent_folder_id: Destination folder ID
        previous_parent_folder_id: Optional current parent folder ID
        _user_id: User ID for credential injection
        _injected_credentials: Flag for credential injection
    """
    try:
        # Phase 3: route through the shared injector when user context is present
        service = _get_drive_service(user_id=_user_id, injected_credentials=_injected_credentials)
        
        # Get current parents if not provided
        if not previous_parent_folder_id:
            file = service.files().get(fileId=file_id, fields='parents').execute()
            previous_parent_folder_id = ','.join(file.get('parents', []))
        
        file = service.files().update(
            fileId=file_id,
            addParents=new_parent_folder_id,
            removeParents=previous_parent_folder_id,
            fields='id, name, parents'
        ).execute()
        
        return file
    
    except Exception as e:
        print(f" Failed to move file: {e}")
        raise


def google_drive_copy_file(file_id, name=None, parent_folder_id=None, _user_id=None, _injected_credentials=None, **kwargs):
    """Copy a file
    
    Args:
        file_id: File ID to copy
        name: Optional name for copy
        parent_folder_id: Optional destination folder
        _user_id: User ID for credential injection
        _injected_credentials: Flag for credential injection
    """
    try:
        # Phase 3: route through the shared injector when user context is present
        service = _get_drive_service(user_id=_user_id, injected_credentials=_injected_credentials)
        
        file_metadata = {}
        if name:
            file_metadata['name'] = name
        if parent_folder_id:
            file_metadata['parents'] = [parent_folder_id]
        
        file = service.files().copy(
            fileId=file_id,
            body=file_metadata,
            fields='id, name, webViewLink'
        ).execute()
        
        return file
    
    except Exception as e:
        print(f" Failed to copy file: {e}")
        raise


# ==================== SHARING & PERMISSIONS ====================

def google_drive_share_file(file_id, email, role='reader', type='user', _user_id=None, _injected_credentials=None, **kwargs):
    """Share a file with a user
    
    Args:
        file_id: File ID to share
        email: Email to share with
        role: Permission role (reader/writer/owner)
        type: Permission type (user/group/domain/anyone)
        _user_id: User ID for credential injection
        _injected_credentials: Flag for credential injection
    """
    try:
        # Phase 3: route through the shared injector when user context is present
        service = _get_drive_service(user_id=_user_id, injected_credentials=_injected_credentials)
        
        permission = {
            'type': type,
            'role': role,
            'emailAddress': email
        }
        
        result = service.permissions().create(
            fileId=file_id,
            body=permission,
            fields='id, type, role, emailAddress'
        ).execute()
        
        return result
    
    except Exception as e:
        print(f" Failed to share file: {e}")
        raise


def google_drive_list_permissions(file_id, _user_id=None, _injected_credentials=None, **kwargs):
    """List permissions for a file
    
    Args:
        file_id: File ID
        _user_id: User ID for credential injection
        _injected_credentials: Flag for credential injection
    """
    try:
        # Phase 3: route through the shared injector when user context is present
        service = _get_drive_service(user_id=_user_id, injected_credentials=_injected_credentials)
        
        result = service.permissions().list(
            fileId=file_id,
            fields='permissions(id, type, role, emailAddress, displayName)'
        ).execute()
        
        permissions = result.get('permissions', [])
        
        return {
            'permissions': permissions,
            'count': len(permissions)
        }
    
    except Exception as e:
        print(f" Failed to list permissions: {e}")
        raise


def google_drive_remove_permission(file_id, permission_id, _user_id=None, _injected_credentials=None, **kwargs):
    """Remove a permission from a file
    
    Args:
        file_id: File ID
        permission_id: Permission ID to remove
        _user_id: User ID for credential injection
        _injected_credentials: Flag for credential injection
    """
    try:
        # Phase 3: route through the shared injector when user context is present
        service = _get_drive_service(user_id=_user_id, injected_credentials=_injected_credentials)
        
        service.permissions().delete(fileId=file_id, permissionId=permission_id).execute()
        
        return {'removed': True, 'permission_id': permission_id}
    
    except Exception as e:
        print(f" Failed to remove permission: {e}")
        raise


# ==================== SEARCH & ADVANCED ====================

def google_drive_search_files(query=None, max_results=10, name_contains=None, mime_type=None,
                               modified_after=None, modified_before=None, owner_email=None,
                               shared_with_me=None, starred=None,
                               _user_id=None, _injected_credentials=None, **kwargs):
    """
    Search for files using either a raw Drive query string or schema-based filter parameters.

    Args:
        query: Raw Google Drive API query string (e.g. "name contains 'dental'")
        max_results: Maximum results to return
        name_contains: File name contains this text (builds Drive query automatically)
        mime_type: Specific MIME type filter
        modified_after: ISO 8601 date string - files modified after this date
        modified_before: ISO 8601 date string - files modified before this date
        owner_email: Filter by owner email address
        shared_with_me: True to return only files shared with the user
        starred: True to return only starred files
        _user_id: User ID for credential injection
        _injected_credentials: OAuth credentials flag
    """
    # Build Drive API query from schema parameters if no raw query provided
    if not query:
        parts = []
        if name_contains:
            parts.append(f"name contains '{name_contains}'")
        if mime_type:
            parts.append(f"mimeType = '{mime_type}'")
        if modified_after:
            parts.append(f"modifiedTime > '{modified_after}'")
        if modified_before:
            parts.append(f"modifiedTime < '{modified_before}'")
        if owner_email:
            parts.append(f"'{owner_email}' in owners")
        if shared_with_me is True:
            parts.append("sharedWithMe = true")
        if starred is True:
            parts.append("starred = true")
        # trashed = false is a sensible default
        parts.append("trashed = false")
        query = " and ".join(parts) if parts else None
    else:
        # If query looks like plain text (no Drive API operators), treat as name contains
        drive_operators = ['contains', ' = ', ' != ', ' < ', ' > ', 'in owners', 'sharedWithMe', 'mimeType', 'modifiedTime', 'trashed']
        if not any(op in query for op in drive_operators):
            query = f"name contains '{query}' and trashed = false"

    return google_drive_list_files(max_results=max_results, query=query, _user_id=_user_id, _injected_credentials=_injected_credentials, **kwargs)


def google_drive_export_file(file_id, mime_type, _user_id=None, _injected_credentials=None, **kwargs):
    """Export a Google Workspace file
    
    Args:
        file_id: File ID to export
        mime_type: Export MIME type
        _user_id: User ID for credential injection
        _injected_credentials: Flag for credential injection
    """
    try:
        # Phase 3: route through the shared injector when user context is present
        service = _get_drive_service(user_id=_user_id, injected_credentials=_injected_credentials)
        
        request = service.files().export_media(fileId=file_id, mimeType=mime_type)
        
        file = io.BytesIO()
        downloader = MediaIoBaseDownload(file, request)
        
        done = False
        while not done:
            status, done = downloader.next_chunk()
        
        return {
            'data': file.getvalue(),
            'mime_type': mime_type,
            'size': len(file.getvalue())
        }
    
    except Exception as e:
        print(f" Failed to export file: {e}")
        raise


def google_drive_get_storage_quota(_user_id=None, _injected_credentials=None, **kwargs):
    """Get storage quota information
    
    Args:
        _user_id: User ID for credential injection
        _injected_credentials: Flag for credential injection
    """
    try:
        # Phase 3: route through the shared injector when user context is present
        service = _get_drive_service(user_id=_user_id, injected_credentials=_injected_credentials)
        
        about = service.about().get(fields='storageQuota').execute()
        quota = about.get('storageQuota', {})
        
        return {
            'limit': int(quota.get('limit', 0)),
            'usage': int(quota.get('usage', 0)),
            'usage_in_drive': int(quota.get('usageInDrive', 0)),
            'usage_in_drive_trash': int(quota.get('usageInDriveTrash', 0))
        }
    
    except Exception as e:
        print(f" Failed to get storage quota: {e}")
        raise


def google_drive_restore_file(file_id, _user_id=None, _injected_credentials=None, **kwargs):
    """Restore a file from trash
    
    Args:
        file_id: File ID to restore
        _user_id: User ID for credential injection
        _injected_credentials: Flag for credential injection
    """
    try:
        # Phase 3: route through the shared injector when user context is present
        service = _get_drive_service(user_id=_user_id, injected_credentials=_injected_credentials)
        
        file = service.files().update(
            fileId=file_id,
            body={'trashed': False},
            fields='id, name, trashed'
        ).execute()
        
        return file
    
    except Exception as e:
        print(f" Failed to restore file: {e}")
        raise

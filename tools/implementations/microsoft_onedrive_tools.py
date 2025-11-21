"""
Microsoft OneDrive Tools
Provides cloud storage management, file operations, and sharing via Microsoft Graph API
"""

import os
import requests
import time
import hashlib
from datetime import datetime
from typing import List, Dict, Any, Optional
import json

class MicrosoftOneDriveTools:
    """Microsoft OneDrive cloud storage tools"""
    
    def __init__(self):
        # Credentials are injected dynamically per-user via credential_injector
        # No need to check environment variables at init time
        self.graph_api_base = 'https://graph.microsoft.com/v1.0'
    
    def _get_headers(self, **kwargs) -> Dict[str, str]:
        """Get authorization headers for Microsoft Graph API"""
        # Get access token from credential injector
        if '_user_id' in kwargs:
            import sys
            from pathlib import Path
            sys.path.insert(0, str(Path(__file__).parent.parent.parent / 'AI_infrastructure'))
            from auth.credential_injector import get_microsoft_access_token
            access_token = get_microsoft_access_token(**kwargs)
        else:
            raise Exception("No user credentials provided. User must be authenticated.")
        
        return {
            'Authorization': f'Bearer {access_token}',
            'Content-Type': 'application/json'
        }
    
    def _make_request(self, method: str, endpoint: str, data: Dict = None, params: Dict = None, **kwargs) -> Dict:
        """Make HTTP request to Microsoft Graph API"""
        url = f"{self.graph_api_base}{endpoint}"
        
        try:
            if method == 'GET':
                response = requests.get(url, headers=self._get_headers(**kwargs), params=params)
            elif method == 'POST':
                response = requests.post(url, headers=self._get_headers(**kwargs), json=data, params=params)
            elif method == 'PATCH':
                response = requests.patch(url, headers=self._get_headers(**kwargs), json=data)
            elif method == 'DELETE':
                response = requests.delete(url, headers=self._get_headers(**kwargs))
            elif method == 'PUT':
                response = requests.put(url, headers=self._get_headers(**kwargs), json=data)
            else:
                return {'success': False, 'error': f'Unsupported HTTP method: {method}'}
            
            response.raise_for_status()
            
            # Some endpoints return 204 No Content or 202 Accepted with empty body
            if response.status_code in (202, 204):
                return {'success': True}
            
            # Some endpoints return empty response on success
            if not response.text or response.text.strip() == '':
                return {'success': True}
            
            try:
                return {'success': True, 'data': response.json()}
            except ValueError as json_error:
                # Response was successful but not JSON (e.g., empty body)
                print(f"[WARNING] Microsoft OneDrive - Response not JSON: {response.status_code}, body length: {len(response.text)}")
                return {'success': True, 'data': None}
            
        except requests.exceptions.HTTPError as e:
            error_msg = str(e)
            try:
                error_data = e.response.json()
                error_msg = error_data.get('error', {}).get('message', str(e))
            except:
                pass
            return {'success': False, 'error': error_msg, 'status_code': e.response.status_code}
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def _get_file_hash(self, file_path: str, **kwargs) -> str:
        """Calculate SHA256 hash of file"""
        sha256_hash = hashlib.sha256()
        with open(file_path, "rb") as f:
            for byte_block in iter(lambda: f.read(4096), b""):
                sha256_hash.update(byte_block)
        return sha256_hash.hexdigest()
    
    def onedrive_list_files(self, folder_path: str = None, max_results: int = 100, **kwargs) -> Dict:
        """List files in OneDrive folder"""
        
        if folder_path:
            endpoint = f'/me/drive/root:/{folder_path}:/children'
        else:
            endpoint = '/me/drive/root/children'
        
        params = {'$top': min(max_results, 100)}
        result = self._make_request('GET', endpoint, params=params, **kwargs)
        
        if result['success']:
            items = result['data'].get('value', [])
            return {
                'success': True,
                'count': len(items),
                'folder_path': folder_path or 'root',
                'items': [{
                    'id': item.get('id'),
                    'name': item.get('name'),
                    'type': 'folder' if 'folder' in item else 'file',
                    'size': item.get('size'),
                    'created': item.get('createdDateTime'),
                    'modified': item.get('lastModifiedDateTime'),
                    'web_url': item.get('webUrl')
                } for item in items]
            }
        return result
    
    def onedrive_upload_file(self, local_file_path: str, 
                            onedrive_folder: str = None, new_name: str = None, **kwargs) -> Dict:
        """Upload file to OneDrive"""
        
        if not os.path.exists(local_file_path):
            return {'success': False, 'error': f'File not found: {local_file_path}'}
        
        file_name = new_name or os.path.basename(local_file_path)
        file_size = os.path.getsize(local_file_path)
        
        # For files < 4MB, use simple upload
        if file_size < 4 * 1024 * 1024:
            try:
                with open(local_file_path, 'rb') as f:
                    file_content = f.read()
                
                if onedrive_folder:
                    upload_url = f'/me/drive/root:/{onedrive_folder}/{file_name}:/content'
                else:
                    upload_url = f'/me/drive/root:/{file_name}:/content'
                
                headers = self._get_headers(**kwargs)
                headers['Content-Type'] = 'application/octet-stream'
                
                response = requests.put(
                    f'{self.graph_api_base}{upload_url}',
                    headers=headers,
                    data=file_content
                )
                
                response.raise_for_status()
                
                file_data = response.json()
                file_id = file_data.get('id')
                
                # Make file shareable with edit permissions
                share_result = self.onedrive_create_share_link(
                    user_id=user_id,
                    item_id=file_id,
                    link_type='edit',
                    scope='anonymous',
                    **kwargs
                )
                
                return {
                    'success': True,
                    'message': f'File "{file_name}" uploaded successfully',
                    'size': file_size,
                    'file': file_data,
                    'shareable': share_result.get('success', False),
                    'share_link': share_result.get('share_link', '')
                }
                
            except Exception as e:
                return {'success': False, 'error': str(e)}
        
        else:
            # Large file upload (>4MB) - requires upload session
            return {
                'success': False,
                'error': 'Large file upload (>4MB) requires upload session - not yet implemented'
            }
    
    def onedrive_download_file(self, item_id: str, save_path: str, **kwargs) -> Dict:
        """Download file from OneDrive"""
        
        # Get download URL
        result = self._make_request('GET', f'/me/drive/items/{item_id}', **kwargs)
        
        if not result['success']:
            return result
        
        download_url = result['data'].get('@microsoft.graph.downloadUrl')
        
        if not download_url:
            return {'success': False, 'error': 'Download URL not available'}
        
        try:
            response = requests.get(download_url)
            response.raise_for_status()
            
            os.makedirs(os.path.dirname(save_path), exist_ok=True)
            
            with open(save_path, 'wb') as f:
                f.write(response.content)
            
            return {
                'success': True,
                'message': f'File downloaded to {save_path}',
                'size': len(response.content)
            }
            
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def onedrive_get_file_info(self, item_id: str, **kwargs) -> Dict:
        """Get detailed information about a file or folder"""
        result = self._make_request('GET', f'/me/drive/items/{item_id}', **kwargs)
        
        if result['success']:
            item = result['data']
            return {
                'success': True,
                'item': {
                    'id': item.get('id'),
                    'name': item.get('name'),
                    'type': 'folder' if 'folder' in item else 'file',
                    'size': item.get('size'),
                    'created': item.get('createdDateTime'),
                    'modified': item.get('lastModifiedDateTime'),
                    'created_by': item.get('createdBy', {}).get('user', {}).get('displayName'),
                    'modified_by': item.get('lastModifiedBy', {}).get('user', {}).get('displayName'),
                    'web_url': item.get('webUrl'),
                    'parent_path': item.get('parentReference', {}).get('path')
                }
            }
        return result
    
    def onedrive_create_folder(self, folder_name: str, parent_path: str = None, **kwargs) -> Dict:
        """Create a new folder in OneDrive"""
        
        folder_data = {
            'name': folder_name,
            'folder': {},
            '@microsoft.graph.conflictBehavior': 'rename'
        }
        
        if parent_path:
            endpoint = f'/me/drive/root:/{parent_path}:/children'
        else:
            endpoint = '/me/drive/root/children'
        
        result = self._make_request('POST', endpoint, folder_data, **kwargs)
        
        if result['success']:
            folder_data_result = result['data']
            folder_id = folder_data_result.get('id')
            
            # Make folder shareable with edit permissions
            share_result = self.onedrive_create_share_link(
                user_id=user_id,
                item_id=folder_id,
                link_type='edit',
                scope='anonymous',
                **kwargs
            )
            
            return {
                'success': True,
                'message': f'Folder "{folder_name}" created successfully',
                'folder': folder_data_result,
                'shareable': share_result.get('success', False),
                'share_link': share_result.get('share_link', '')
            }
        return result
    
    def onedrive_delete_item(self, item_id: str, **kwargs) -> Dict:
        """Delete a file or folder"""
        result = self._make_request('DELETE', f'/me/drive/items/{item_id}', **kwargs)
        
        if result['success']:
            return {
                'success': True,
                'message': 'Item deleted successfully'
            }
        return result
    
    def onedrive_move_item(self, item_id: str, destination_folder_id: str,
                          new_name: str = None, **kwargs) -> Dict:
        """Move or rename a file/folder"""
        
        move_data = {
            'parentReference': {
                'id': destination_folder_id
            }
        }
        
        if new_name:
            move_data['name'] = new_name
        
        result = self._make_request('PATCH', f'/me/drive/items/{item_id}', move_data, **kwargs)
        
        if result['success']:
            return {
                'success': True,
                'message': 'Item moved successfully',
                'item': result['data']
            }
        return result
    
    def onedrive_copy_item(self, item_id: str, destination_folder_id: str,
                          new_name: str = None, **kwargs) -> Dict:
        """Copy a file or folder"""
        
        copy_data = {
            'parentReference': {
                'id': destination_folder_id
            }
        }
        
        if new_name:
            copy_data['name'] = new_name
        
        result = self._make_request('POST', f'/me/drive/items/{item_id}/copy', copy_data, **kwargs)
        
        if result['success']:
            return {
                'success': True,
                'message': 'Item copy initiated',
                'note': 'Copy operation runs asynchronously'
            }
        return result
    
    def onedrive_rename_item(self, item_id: str, new_name: str, **kwargs) -> Dict:
        """Rename a file or folder"""
        
        rename_data = {'name': new_name}
        result = self._make_request('PATCH', f'/me/drive/items/{item_id}', rename_data, **kwargs)
        
        if result['success']:
            return {
                'success': True,
                'message': f'Item renamed to "{new_name}"',
                'item': result['data']
            }
        return result
    
    def onedrive_search_files(self, query: str, folder_path: str = None,
                             max_results: int = 50, **kwargs) -> Dict:
        """Search for files in OneDrive"""
        
        if folder_path:
            endpoint = f'/me/drive/root:/{folder_path}:/search(q=\'{query}\')'
        else:
            endpoint = f'/me/drive/root/search(q=\'{query}\')'
        
        params = {'$top': min(max_results, 100)}
        result = self._make_request('GET', endpoint, params=params, **kwargs)
        
        if result['success']:
            items = result['data'].get('value', [])
            return {
                'success': True,
                'query': query,
                'count': len(items),
                'results': [{
                    'id': item.get('id'),
                    'name': item.get('name'),
                    'type': 'folder' if 'folder' in item else 'file',
                    'path': item.get('parentReference', {}).get('path'),
                    'web_url': item.get('webUrl')
                } for item in items]
            }
        return result
    
    def onedrive_get_file_versions(self, item_id: str, **kwargs) -> Dict:
        """Get version history of a file"""
        result = self._make_request('GET', f'/me/drive/items/{item_id}/versions', **kwargs)
        
        if result['success']:
            versions = result['data'].get('value', [])
            return {
                'success': True,
                'count': len(versions),
                'versions': [{
                    'id': v.get('id'),
                    'size': v.get('size'),
                    'last_modified': v.get('lastModifiedDateTime'),
                    'modified_by': v.get('lastModifiedBy', {}).get('user', {}).get('displayName')
                } for v in versions]
            }
        return result
    
    def onedrive_restore_version(self, item_id: str, version_id: str, **kwargs) -> Dict:
        """Restore a previous version of a file"""
        result = self._make_request('POST', f'/me/drive/items/{item_id}/versions/{version_id}/restoreVersion', **kwargs)
        
        if result['success']:
            return {
                'success': True,
                'message': 'File version restored successfully'
            }
        return result
    
    def onedrive_get_thumbnail(self, item_id: str, size: str = 'medium', **kwargs) -> Dict:
        """Get thumbnail image for a file"""
        result = self._make_request('GET', f'/me/drive/items/{item_id}/thumbnails', **kwargs)
        
        if result['success']:
            thumbnails = result['data'].get('value', [])
            if thumbnails:
                thumb = thumbnails[0].get(size, {})
                return {
                    'success': True,
                    'thumbnail_url': thumb.get('url'),
                    'size': size
                }
            return {'success': False, 'error': 'No thumbnails available'}
        return result
    
    def onedrive_create_share_link(self, item_id: str, 
                                   link_type: str = 'view', scope: str = 'anonymous', **kwargs) -> Dict:
        """Create a sharing link for a file or folder"""
        
        link_data = {
            'type': link_type,  # 'view', 'edit', 'embed'
            'scope': scope      # 'anonymous', 'organization'
        }
        
        result = self._make_request('POST', f'/me/drive/items/{item_id}/createLink', link_data, **kwargs)
        
        if result['success']:
            link_info = result['data']
            return {
                'success': True,
                'share_link': link_info.get('link', {}).get('webUrl'),
                'type': link_type,
                'scope': scope
            }
        return result
    
    def onedrive_share_with_users(self, item_id: str, recipients: List[str],
                                 message: str = None, role: str = 'read', **kwargs) -> Dict:
        """Share file/folder with specific users"""
        
        share_data = {
            'recipients': [{'email': email} for email in recipients],
            'requireSignIn': True,
            'sendInvitation': True,
            'roles': [role]
        }
        
        if message:
            share_data['message'] = message
        
        result = self._make_request('POST', f'/me/drive/items/{item_id}/invite', share_data, **kwargs)
        
        if result['success']:
            return {
                'success': True,
                'message': f'Shared with {len(recipients)} users',
                'recipients': recipients,
                'role': role
            }
        return result
    
    def onedrive_get_permissions(self, item_id: str, **kwargs) -> Dict:
        """Get sharing permissions for a file/folder"""
        result = self._make_request('GET', f'/me/drive/items/{item_id}/permissions', **kwargs)
        
        if result['success']:
            permissions = result['data'].get('value', [])
            return {
                'success': True,
                'count': len(permissions),
                'permissions': [{
                    'id': p.get('id'),
                    'role': p.get('roles', []),
                    'granted_to': p.get('grantedTo', {}).get('user', {}).get('displayName'),
                    'link': p.get('link', {}).get('webUrl')
                } for p in permissions]
            }
        return result
    
    def onedrive_revoke_permission(self, item_id: str, permission_id: str, **kwargs) -> Dict:
        """Revoke sharing permission"""
        result = self._make_request('DELETE', f'/me/drive/items/{item_id}/permissions/{permission_id}', **kwargs)
        
        if result['success']:
            return {
                'success': True,
                'message': 'Permission revoked successfully'
            }
        return result
    
    def onedrive_get_storage_info(self, **kwargs) -> Dict:
        """Get OneDrive storage quota information"""
        result = self._make_request('GET', '/me/drive', **kwargs)
        
        if result['success']:
            drive = result['data']
            quota = drive.get('quota', {})
            
            total = quota.get('total', 0)
            used = quota.get('used', 0)
            remaining = quota.get('remaining', 0)
            
            return {
                'success': True,
                'storage': {
                    'total_gb': round(total / (1024**3), 2),
                    'used_gb': round(used / (1024**3), 2),
                    'remaining_gb': round(remaining / (1024**3), 2),
                    'usage_percent': round((used / total * 100), 2) if total > 0 else 0
                }
            }
        return result
    
    def onedrive_get_recent_files(self, max_results: int = 20, **kwargs) -> Dict:
        """Get recently accessed files"""
        params = {'$top': min(max_results, 100)}
        result = self._make_request('GET', '/me/drive/recent', params=params, **kwargs)
        
        if result['success']:
            items = result['data'].get('value', [])
            return {
                'success': True,
                'count': len(items),
                'files': [{
                    'id': item.get('id'),
                    'name': item.get('name'),
                    'last_accessed': item.get('lastAccessedDateTime'),
                    'modified': item.get('lastModifiedDateTime'),
                    'web_url': item.get('webUrl')
                } for item in items]
            }
        return result
    
    def onedrive_smart_organize_by_type(self, source_folder: str = None, **kwargs) -> Dict:
        """Automatically organize files by type into folders"""
        
        # Get files from source folder
        files_result = self.onedrive_list_files(user_id, source_folder)
        
        if not files_result['success']:
            return files_result
        
        items = files_result['items']
        file_items = [item for item in items if item['type'] == 'file']
        
        # Group by extension
        grouped = {}
        for item in file_items:
            ext = os.path.splitext(item['name'])[1].lower()
            if ext:
                ext_folder = ext[1:].upper()  # Remove dot and uppercase
                if ext_folder not in grouped:
                    grouped[ext_folder] = []
                grouped[ext_folder].append(item)
        
        results = {
            'success': True,
            'organized': [],
            'failed': [],
            'folders_created': []
        }
        
        # Create folders and move files
        for ext_folder, files in grouped.items():
            # Create folder
            folder_path = f"{source_folder}/{ext_folder}" if source_folder else ext_folder
            folder_result = self.onedrive_create_folder(user_id, ext_folder, source_folder)
            
            if folder_result['success']:
                results['folders_created'].append(ext_folder)
                folder_id = folder_result['folder']['id']
                
                # Move files
                for file_item in files:
                    move_result = self.onedrive_move_item(user_id, file_item['id'], folder_id)
                    if move_result['success']:
                        results['organized'].append(file_item['name'])
                    else:
                        results['failed'].append({'file': file_item['name'], 'error': move_result.get('error')})
        
        results['message'] = f"Organized {len(results['organized'])} files into {len(results['folders_created'])} folders"
        
        return results
    
    def onedrive_smart_backup_folder(self, folder_path: str, **kwargs) -> Dict:
        """Create timestamped backup of entire folder"""
        
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        backup_name = f"Backup_{os.path.basename(folder_path)}_{timestamp}"
        
        # Get folder info
        folder_result = self._make_request('GET', f'/me/drive/root:/{folder_path}', **kwargs)
        
        if not folder_result['success']:
            return folder_result
        
        folder_id = folder_result['data']['id']
        parent_path = os.path.dirname(folder_path) or None
        
        # Create backup folder
        backup_result = self.onedrive_create_folder(user_id, backup_name, parent_path)
        
        if not backup_result['success']:
            return backup_result
        
        backup_folder_id = backup_result['folder']['id']
        
        # Copy folder contents
        copy_result = self.onedrive_copy_item(user_id, folder_id, backup_folder_id)
        
        if copy_result['success']:
            return {
                'success': True,
                'message': f'Backup created: {backup_name}',
                'backup_folder': backup_name
            }
        
        return copy_result
    
    def onedrive_smart_cleanup_duplicates(self, folder_path: str = None,
                                         strategy: str = 'keep_newest', **kwargs) -> Dict:
        """Find and remove duplicate files"""
        
        # Get files
        files_result = self.onedrive_list_files(user_id, folder_path)
        
        if not files_result['success']:
            return files_result
        
        items = [item for item in files_result['items'] if item['type'] == 'file']
        
        # Group by name and size
        duplicates = {}
        for item in items:
            key = (item['name'], item['size'])
            if key not in duplicates:
                duplicates[key] = []
            duplicates[key].append(item)
        
        # Find actual duplicates
        duplicate_groups = {k: v for k, v in duplicates.items() if len(v) > 1}
        
        results = {
            'success': True,
            'deleted': [],
            'kept': [],
            'failed': []
        }
        
        for (name, size), group in duplicate_groups.items():
            # Sort by modified date
            sorted_group = sorted(group, key=lambda x: x['modified'], reverse=(strategy == 'keep_newest'))
            
            # Keep first, delete rest
            results['kept'].append(sorted_group[0]['name'])
            
            for item in sorted_group[1:]:
                delete_result = self.onedrive_delete_item(user_id, item['id'])
                if delete_result['success']:
                    results['deleted'].append(item['name'])
                else:
                    results['failed'].append({'file': item['name'], 'error': delete_result.get('error')})
        
        results['message'] = f"Deleted {len(results['deleted'])} duplicate files"
        
        return results
    
    def onedrive_smart_sync_folders(self, source_folder: str, 
                                   destination_folder: str, sync_mode: str = 'one_way', **kwargs) -> Dict:
        """Synchronize two folders"""
        
        # Get source files
        source_result = self.onedrive_list_files(user_id, source_folder)
        if not source_result['success']:
            return source_result
        
        # Get destination files
        dest_result = self.onedrive_list_files(user_id, destination_folder)
        if not dest_result['success']:
            return dest_result
        
        source_files = {item['name']: item for item in source_result['items']}
        dest_files = {item['name']: item for item in dest_result['items']}
        
        results = {
            'success': True,
            'copied': [],
            'updated': [],
            'failed': []
        }
        
        # Get destination folder ID
        dest_folder_result = self._make_request('GET', f'/me/drive/root:/{destination_folder}', **kwargs)
        if not dest_folder_result['success']:
            return dest_folder_result
        
        dest_folder_id = dest_folder_result['data']['id']
        
        # Copy new files and update modified files
        for name, source_item in source_files.items():
            if name not in dest_files:
                # New file - copy
                copy_result = self.onedrive_copy_item(user_id, source_item['id'], dest_folder_id)
                if copy_result['success']:
                    results['copied'].append(name)
                else:
                    results['failed'].append({'file': name, 'error': copy_result.get('error')})
            
            elif source_item['modified'] > dest_files[name]['modified']:
                # Modified file - update
                delete_result = self.onedrive_delete_item(user_id, dest_files[name]['id'])
                if delete_result['success']:
                    copy_result = self.onedrive_copy_item(user_id, source_item['id'], dest_folder_id)
                    if copy_result['success']:
                        results['updated'].append(name)
        
        results['message'] = f"Synced: {len(results['copied'])} new, {len(results['updated'])} updated"
        
        return results


# ========================================
# GLOBAL INSTANCE & MODULE-LEVEL EXPORTS
# ========================================

# Create global instance
microsoft_onedrive_tools = MicrosoftOneDriveTools()

# Export all functions at module level
# Wrappers handle parameter transformation for registry compatibility

def microsoft_onedrive_upload_file(**kwargs):
    user_id = kwargs.pop('user_id', None)
    if user_id is None:
        raise ValueError("user_id is required")
    return microsoft_onedrive_tools.onedrive_upload_file(user_id, **kwargs)

def microsoft_onedrive_download_file(**kwargs):
    user_id = kwargs.pop('user_id', None)
    if user_id is None:
        raise ValueError("user_id is required")
    return microsoft_onedrive_tools.onedrive_download_file(user_id, **kwargs)

def microsoft_onedrive_get_file_info(**kwargs):
    user_id = kwargs.pop('user_id', None)
    if user_id is None:
        raise ValueError("user_id is required")
    return microsoft_onedrive_tools.onedrive_get_file_info(user_id, **kwargs)

def microsoft_onedrive_create_folder(**kwargs):
    user_id = kwargs.pop('user_id', None)
    if user_id is None:
        raise ValueError("user_id is required")
    return microsoft_onedrive_tools.onedrive_create_folder(user_id, **kwargs)

def microsoft_onedrive_delete_item(**kwargs):
    user_id = kwargs.pop('user_id', None)
    if user_id is None:
        raise ValueError("user_id is required")
    return microsoft_onedrive_tools.onedrive_delete_item(user_id, **kwargs)

def microsoft_onedrive_move_item(**kwargs):
    user_id = kwargs.pop('user_id', None)
    if user_id is None:
        raise ValueError("user_id is required")
    return microsoft_onedrive_tools.onedrive_move_item(user_id, **kwargs)

def microsoft_onedrive_copy_item(**kwargs):
    user_id = kwargs.pop('user_id', None)
    if user_id is None:
        raise ValueError("user_id is required")
    return microsoft_onedrive_tools.onedrive_copy_item(user_id, **kwargs)

def microsoft_onedrive_rename_item(**kwargs):
    user_id = kwargs.pop('user_id', None)
    if user_id is None:
        raise ValueError("user_id is required")
    return microsoft_onedrive_tools.onedrive_rename_item(user_id, **kwargs)

def microsoft_onedrive_search_files(**kwargs):
    user_id = kwargs.pop('user_id', None)
    if user_id is None:
        raise ValueError("user_id is required")
    return microsoft_onedrive_tools.onedrive_search_files(user_id, **kwargs)

def microsoft_onedrive_get_file_versions(**kwargs):
    user_id = kwargs.pop('user_id', None)
    if user_id is None:
        raise ValueError("user_id is required")
    return microsoft_onedrive_tools.onedrive_get_file_versions(user_id, **kwargs)

def microsoft_onedrive_restore_version(**kwargs):
    user_id = kwargs.pop('user_id', None)
    if user_id is None:
        raise ValueError("user_id is required")
    return microsoft_onedrive_tools.onedrive_restore_version(user_id, **kwargs)

def microsoft_onedrive_get_thumbnail(**kwargs):
    user_id = kwargs.pop('user_id', None)
    if user_id is None:
        raise ValueError("user_id is required")
    return microsoft_onedrive_tools.onedrive_get_thumbnail(user_id, **kwargs)

def microsoft_onedrive_create_share_link(**kwargs):
    user_id = kwargs.pop('user_id', None)
    if user_id is None:
        raise ValueError("user_id is required")
    return microsoft_onedrive_tools.onedrive_create_share_link(user_id, **kwargs)

def microsoft_onedrive_share_with_users(**kwargs):
    user_id = kwargs.pop('user_id', None)
    if user_id is None:
        raise ValueError("user_id is required")
    return microsoft_onedrive_tools.onedrive_share_with_users(user_id, **kwargs)

def microsoft_onedrive_get_permissions(**kwargs):
    user_id = kwargs.pop('user_id', None)
    if user_id is None:
        raise ValueError("user_id is required")
    return microsoft_onedrive_tools.onedrive_get_permissions(user_id, **kwargs)

def microsoft_onedrive_revoke_permission(**kwargs):
    user_id = kwargs.pop('user_id', None)
    if user_id is None:
        raise ValueError("user_id is required")
    return microsoft_onedrive_tools.onedrive_revoke_permission(user_id, **kwargs)

def microsoft_onedrive_get_storage_info(**kwargs):
    user_id = kwargs.pop('user_id', None)
    if user_id is None:
        raise ValueError("user_id is required")
    return microsoft_onedrive_tools.onedrive_get_storage_info(user_id, **kwargs)

def microsoft_onedrive_get_recent_files(**kwargs):
    user_id = kwargs.pop('user_id', None)
    if user_id is None:
        raise ValueError("user_id is required")
    return microsoft_onedrive_tools.onedrive_get_recent_files(user_id, **kwargs)

def microsoft_onedrive_smart_organize_by_type(**kwargs):
    user_id = kwargs.pop('user_id', None)
    if user_id is None:
        raise ValueError("user_id is required")
    return microsoft_onedrive_tools.onedrive_smart_organize_by_type(user_id, **kwargs)

def microsoft_onedrive_smart_backup_folder(**kwargs):
    user_id = kwargs.pop('user_id', None)
    if user_id is None:
        raise ValueError("user_id is required")
    return microsoft_onedrive_tools.onedrive_smart_backup_folder(user_id, **kwargs)

def microsoft_onedrive_smart_cleanup_duplicates(**kwargs):
    user_id = kwargs.pop('user_id', None)
    if user_id is None:
        raise ValueError("user_id is required")
    return microsoft_onedrive_tools.onedrive_smart_cleanup_duplicates(user_id, **kwargs)

def microsoft_onedrive_smart_sync_folders(**kwargs):
    user_id = kwargs.pop('user_id', None)
    if user_id is None:
        raise ValueError("user_id is required")
    return microsoft_onedrive_tools.onedrive_smart_sync_folders(user_id, **kwargs)


    if user_id is None:
        raise ValueError("user_id is required")
    return microsoft_onedrive_tools.onedrive_list_files(user_id, **kwargs)

def microsoft_onedrive_upload_file(**kwargs):
    user_id = kwargs.pop('user_id', None)
    if user_id is None:
        raise ValueError("user_id is required")
    return microsoft_onedrive_tools.onedrive_upload_file(user_id, **kwargs)

def microsoft_onedrive_download_file(**kwargs):
    user_id = kwargs.pop('user_id', None)
    if user_id is None:
        raise ValueError("user_id is required")
    return microsoft_onedrive_tools.onedrive_download_file(user_id, **kwargs)

def microsoft_onedrive_get_file_info(**kwargs):
    user_id = kwargs.pop('user_id', None)
    if user_id is None:
        raise ValueError("user_id is required")
    return microsoft_onedrive_tools.onedrive_get_file_info(user_id, **kwargs)

def microsoft_onedrive_create_folder(**kwargs):
    user_id = kwargs.pop('user_id', None)
    if user_id is None:
        raise ValueError("user_id is required")
    return microsoft_onedrive_tools.onedrive_create_folder(user_id, **kwargs)

def microsoft_onedrive_delete_item(**kwargs):
    user_id = kwargs.pop('user_id', None)
    if user_id is None:
        raise ValueError("user_id is required")
    return microsoft_onedrive_tools.onedrive_delete_item(user_id, **kwargs)

def microsoft_onedrive_move_item(**kwargs):
    user_id = kwargs.pop('user_id', None)
    if user_id is None:
        raise ValueError("user_id is required")
    return microsoft_onedrive_tools.onedrive_move_item(user_id, **kwargs)

def microsoft_onedrive_copy_item(**kwargs):
    user_id = kwargs.pop('user_id', None)
    if user_id is None:
        raise ValueError("user_id is required")
    return microsoft_onedrive_tools.onedrive_copy_item(user_id, **kwargs)

def microsoft_onedrive_rename_item(**kwargs):
    user_id = kwargs.pop('user_id', None)
    if user_id is None:
        raise ValueError("user_id is required")
    return microsoft_onedrive_tools.onedrive_rename_item(user_id, **kwargs)

def microsoft_onedrive_search_files(**kwargs):
    user_id = kwargs.pop('user_id', None)
    if user_id is None:
        raise ValueError("user_id is required")
    return microsoft_onedrive_tools.onedrive_search_files(user_id, **kwargs)

def microsoft_onedrive_get_file_versions(**kwargs):
    user_id = kwargs.pop('user_id', None)
    if user_id is None:
        raise ValueError("user_id is required")
    return microsoft_onedrive_tools.onedrive_get_file_versions(user_id, **kwargs)

def microsoft_onedrive_restore_version(**kwargs):
    user_id = kwargs.pop('user_id', None)
    if user_id is None:
        raise ValueError("user_id is required")
    return microsoft_onedrive_tools.onedrive_restore_version(user_id, **kwargs)

def microsoft_onedrive_get_thumbnail(**kwargs):
    user_id = kwargs.pop('user_id', None)
    if user_id is None:
        raise ValueError("user_id is required")
    return microsoft_onedrive_tools.onedrive_get_thumbnail(user_id, **kwargs)

def microsoft_onedrive_create_share_link(**kwargs):
    user_id = kwargs.pop('user_id', None)
    if user_id is None:
        raise ValueError("user_id is required")
    return microsoft_onedrive_tools.onedrive_create_share_link(user_id, **kwargs)

def microsoft_onedrive_share_with_users(**kwargs):
    user_id = kwargs.pop('user_id', None)
    if user_id is None:
        raise ValueError("user_id is required")
    return microsoft_onedrive_tools.onedrive_share_with_users(user_id, **kwargs)

def microsoft_onedrive_get_permissions(**kwargs):
    user_id = kwargs.pop('user_id', None)
    if user_id is None:
        raise ValueError("user_id is required")
    return microsoft_onedrive_tools.onedrive_get_permissions(user_id, **kwargs)

def microsoft_onedrive_revoke_permission(**kwargs):
    user_id = kwargs.pop('user_id', None)
    if user_id is None:
        raise ValueError("user_id is required")
    return microsoft_onedrive_tools.onedrive_revoke_permission(user_id, **kwargs)

def microsoft_onedrive_get_storage_info(**kwargs):
    user_id = kwargs.pop('user_id', None)
    if user_id is None:
        raise ValueError("user_id is required")
    return microsoft_onedrive_tools.onedrive_get_storage_info(user_id, **kwargs)

def microsoft_onedrive_get_recent_files(**kwargs):
    user_id = kwargs.pop('user_id', None)
    if user_id is None:
        raise ValueError("user_id is required")
    return microsoft_onedrive_tools.onedrive_get_recent_files(user_id, **kwargs)

def microsoft_onedrive_smart_organize_by_type(**kwargs):
    user_id = kwargs.pop('user_id', None)
    if user_id is None:
        raise ValueError("user_id is required")
    return microsoft_onedrive_tools.onedrive_smart_organize_by_type(user_id, **kwargs)

def microsoft_onedrive_smart_backup_folder(**kwargs):
    user_id = kwargs.pop('user_id', None)
    if user_id is None:
        raise ValueError("user_id is required")
    return microsoft_onedrive_tools.onedrive_smart_backup_folder(user_id, **kwargs)

def microsoft_onedrive_smart_cleanup_duplicates(**kwargs):
    user_id = kwargs.pop('user_id', None)
    if user_id is None:
        raise ValueError("user_id is required")
    return microsoft_onedrive_tools.onedrive_smart_cleanup_duplicates(user_id, **kwargs)

def microsoft_onedrive_smart_sync_folders(**kwargs):
    user_id = kwargs.pop('user_id', None)
    if user_id is None:
        raise ValueError("user_id is required")
    return microsoft_onedrive_tools.onedrive_smart_sync_folders(user_id, **kwargs)


microsoft_onedrive_upload_file = microsoft_onedrive_tools.onedrive_upload_file

microsoft_onedrive_download_file = microsoft_onedrive_tools.onedrive_download_file

microsoft_onedrive_get_file_info = microsoft_onedrive_tools.onedrive_get_file_info

microsoft_onedrive_create_folder = microsoft_onedrive_tools.onedrive_create_folder

microsoft_onedrive_delete_item = microsoft_onedrive_tools.onedrive_delete_item

microsoft_onedrive_move_item = microsoft_onedrive_tools.onedrive_move_item

microsoft_onedrive_copy_item = microsoft_onedrive_tools.onedrive_copy_item

microsoft_onedrive_rename_item = microsoft_onedrive_tools.onedrive_rename_item

microsoft_onedrive_search_files = microsoft_onedrive_tools.onedrive_search_files

microsoft_onedrive_get_file_versions = microsoft_onedrive_tools.onedrive_get_file_versions

microsoft_onedrive_restore_version = microsoft_onedrive_tools.onedrive_restore_version

microsoft_onedrive_get_thumbnail = microsoft_onedrive_tools.onedrive_get_thumbnail

microsoft_onedrive_create_share_link = microsoft_onedrive_tools.onedrive_create_share_link

microsoft_onedrive_share_with_users = microsoft_onedrive_tools.onedrive_share_with_users

microsoft_onedrive_get_permissions = microsoft_onedrive_tools.onedrive_get_permissions

microsoft_onedrive_revoke_permission = microsoft_onedrive_tools.onedrive_revoke_permission

microsoft_onedrive_get_storage_info = microsoft_onedrive_tools.onedrive_get_storage_info

microsoft_onedrive_get_recent_files = microsoft_onedrive_tools.onedrive_get_recent_files

microsoft_onedrive_smart_organize_by_type = microsoft_onedrive_tools.onedrive_smart_organize_by_type

microsoft_onedrive_smart_backup_folder = microsoft_onedrive_tools.onedrive_smart_backup_folder

microsoft_onedrive_smart_cleanup_duplicates = microsoft_onedrive_tools.onedrive_smart_cleanup_duplicates

microsoft_onedrive_smart_sync_folders = microsoft_onedrive_tools.onedrive_smart_sync_folders


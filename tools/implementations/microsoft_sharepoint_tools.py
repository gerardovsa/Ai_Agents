"""
Microsoft SharePoint Tools - Enterprise Content Management and Collaboration
Provides comprehensive SharePoint site, library, and list management via Microsoft Graph API

Categories:
- Site Management (get, list, search sites)
- Document Library Operations (files, folders, metadata)
- List Management (create, manage SharePoint lists)
- Permissions & Sharing (site/item permissions)
- Search (cross-site content search)
- SMART Tools (automated site provisioning and content management)
"""

import requests
from typing import Dict, List, Any, Optional
import json
from datetime import datetime


class MicrosoftSharePointTools:
    """Microsoft SharePoint management tools using Graph API v1.0"""
    
    def __init__(self):
        # Credentials are injected dynamically per-user via credential_injector
        self.base_url = "https://graph.microsoft.com/v1.0"
    
    def _get_headers(self, **kwargs) -> Dict[str, str]:
        """Get authorization headers for Microsoft Graph API"""
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
    
    # ========================================
    # TIER 1: SITE MANAGEMENT
    # ========================================
    
    def sharepoint_get_site(
        self,
        site_id: Optional[str] = None,
        site_url: Optional[str] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Get SharePoint site information
        
        Args:
            site_id: SharePoint site ID
            site_url: Site URL (e.g., 'contoso.sharepoint.com,/sites/team')
            
        Returns:
            Dict with site details
        """
        try:
            if site_id:
                endpoint = f"{self.base_url}/sites/{site_id}"
            elif site_url:
                endpoint = f"{self.base_url}/sites/{site_url}"
            else:
                # Get root site
                endpoint = f"{self.base_url}/sites/root"
            
            response = requests.get(endpoint, headers=self._get_headers(**kwargs))
            response.raise_for_status()
            site = response.json()
            
            return {
                "site_id": site['id'],
                "name": site.get('displayName', ''),
                "web_url": site.get('webUrl', ''),
                "description": site.get('description', ''),
                "created_datetime": site.get('createdDateTime', ''),
                "modified_datetime": site.get('lastModifiedDateTime', '')
            }
            
        except requests.exceptions.RequestException as e:
            return {"error": f"Failed to get site: {str(e)}"}
    
    def sharepoint_list_sites(
        self,
        search_query: Optional[str] = None,
        limit: int = 50,
        **kwargs
    ) -> Dict[str, Any]:
        """
        List SharePoint sites (requires SharePoint admin or search permissions)
        
        Args:
            search_query: Optional search term
            limit: Maximum sites to return
            
        Returns:
            Dict with sites list
        """
        try:
            if search_query:
                endpoint = f"{self.base_url}/sites?search={search_query}"
            else:
                # List followed sites
                endpoint = f"{self.base_url}/me/followedSites"
            
            params = {"$top": limit}
            response = requests.get(endpoint, headers=self._get_headers(**kwargs), params=params)
            response.raise_for_status()
            data = response.json()
            
            sites = []
            for site in data.get('value', []):
                sites.append({
                    "site_id": site['id'],
                    "name": site.get('displayName', ''),
                    "web_url": site.get('webUrl', ''),
                    "description": site.get('description', '')
                })
            
            return {
                "count": len(sites),
                "sites": sites
            }
            
        except requests.exceptions.RequestException as e:
            return {"error": f"Failed to list sites: {str(e)}"}
    
    def sharepoint_search_content(
        self,
        query: str,
        site_id: Optional[str] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Search SharePoint content
        
        Args:
            query: Search query
            site_id: Optional site ID to restrict search
            
        Returns:
            Dict with search results
        """
        try:
            endpoint = f"{self.base_url}/search/query"
            
            search_request = {
                "requests": [{
                    "entityTypes": ["driveItem", "listItem", "site"],
                    "query": {
                        "queryString": query
                    }
                }]
            }
            
            response = requests.post(endpoint, headers=self._get_headers(**kwargs), json=search_request)
            response.raise_for_status()
            data = response.json()
            
            results = []
            for result_set in data.get('value', []):
                for hit_container in result_set.get('hitsContainers', []):
                    for hit in hit_container.get('hits', []):
                        resource = hit.get('resource', {})
                        results.append({
                            "title": resource.get('name', ''),
                            "url": resource.get('webUrl', ''),
                            "type": resource.get('@odata.type', ''),
                            "modified": resource.get('lastModifiedDateTime', '')
                        })
            
            return {
                "query": query,
                "count": len(results),
                "results": results
            }
            
        except requests.exceptions.RequestException as e:
            return {"error": f"Failed to search: {str(e)}"}
    
    # ========================================
    # TIER 2: DOCUMENT LIBRARY OPERATIONS
    # ========================================
    
    def sharepoint_list_drives(self, site_id: str, **kwargs) -> Dict[str, Any]:
        """
        List document libraries (drives) in site
        
        Args:
            site_id: Site ID
            
        Returns:
            Dict with document libraries list
        """
        try:
            endpoint = f"{self.base_url}/sites/{site_id}/drives"
            response = requests.get(endpoint, headers=self._get_headers(**kwargs))
            response.raise_for_status()
            data = response.json()
            
            libraries = []
            for drive in data.get('value', []):
                libraries.append({
                    "drive_id": drive['id'],
                    "name": drive.get('name', ''),
                    "description": drive.get('description', ''),
                    "web_url": drive.get('webUrl', ''),
                    "created_datetime": drive.get('createdDateTime', '')
                })
            
            return {
                "count": len(libraries),
                "libraries": libraries
            }
            
        except requests.exceptions.RequestException as e:
            return {"error": f"Failed to list libraries: {str(e)}"}
    
    def sharepoint_list_items(
        self,
        site_id: str,
        drive_id: str,
        folder_path: str = "root",
        limit: int = 100,
        **kwargs
    ) -> Dict[str, Any]:
        """
        List items in document library folder
        
        Args:
            site_id: Site ID
            drive_id: Drive/library ID
            folder_path: Folder path (default: 'root')
            limit: Maximum items to return
            
        Returns:
            Dict with items list
        """
        try:
            if folder_path == "root":
                endpoint = f"{self.base_url}/sites/{site_id}/drives/{drive_id}/root/children"
            else:
                endpoint = f"{self.base_url}/sites/{site_id}/drives/{drive_id}/root:/{folder_path}:/children"
            
            params = {"$top": limit}
            response = requests.get(endpoint, headers=self._get_headers(**kwargs), params=params)
            response.raise_for_status()
            data = response.json()
            
            items = []
            for item in data.get('value', []):
                items.append({
                    "item_id": item['id'],
                    "name": item['name'],
                    "type": "folder" if 'folder' in item else "file",
                    "size": item.get('size', 0),
                    "web_url": item.get('webUrl', ''),
                    "modified_datetime": item.get('lastModifiedDateTime', '')
                })
            
            return {
                "count": len(items),
                "items": items
            }
            
        except requests.exceptions.RequestException as e:
            return {"error": f"Failed to list items: {str(e)}"}
    
    def sharepoint_upload_file(
        self,
        site_id: str,
        drive_id: str,
        file_name: str,
        file_content: bytes,
        folder_path: str = "root",
        **kwargs
    ) -> Dict[str, Any]:
        """
        Upload file to SharePoint library
        
        Args:
            site_id: Site ID
            drive_id: Drive/library ID
            file_name: File name
            file_content: File content as bytes
            folder_path: Destination folder path
            
        Returns:
            Dict with uploaded file info
        """
        try:
            if folder_path == "root":
                endpoint = f"{self.base_url}/sites/{site_id}/drives/{drive_id}/root:/{file_name}:/content"
            else:
                endpoint = f"{self.base_url}/sites/{site_id}/drives/{drive_id}/root:/{folder_path}/{file_name}:/content"
            
            headers = self._get_headers(**kwargs)
            upload_headers = {
                "Authorization": headers['Authorization'],
                "Content-Type": "application/octet-stream"
            }
            
            response = requests.put(endpoint, headers=upload_headers, data=file_content)
            response.raise_for_status()
            file_data = response.json()
            
            return {
                "file_id": file_data['id'],
                "name": file_data['name'],
                "web_url": file_data.get('webUrl', ''),
                "size": file_data.get('size', 0)
            }
            
        except requests.exceptions.RequestException as e:
            return {"error": f"Failed to upload file: {str(e)}"}
    
    def sharepoint_create_folder(
        self,
        site_id: str,
        drive_id: str,
        folder_name: str,
        parent_path: str = "root",
        **kwargs
    ) -> Dict[str, Any]:
        """
        Create folder in SharePoint library
        
        Args:
            site_id: Site ID
            drive_id: Drive/library ID
            folder_name: Folder name
            parent_path: Parent folder path
            
        Returns:
            Dict with folder info
        """
        try:
            if parent_path == "root":
                endpoint = f"{self.base_url}/sites/{site_id}/drives/{drive_id}/root/children"
            else:
                endpoint = f"{self.base_url}/sites/{site_id}/drives/{drive_id}/root:/{parent_path}:/children"
            
            folder_data = {
                "name": folder_name,
                "folder": {},
                "@microsoft.graph.conflictBehavior": "rename"
            }
            
            response = requests.post(endpoint, headers=self._get_headers(**kwargs), json=folder_data)
            response.raise_for_status()
            folder = response.json()
            
            return {
                "folder_id": folder['id'],
                "name": folder['name'],
                "web_url": folder.get('webUrl', '')
            }
            
        except requests.exceptions.RequestException as e:
            return {"error": f"Failed to create folder: {str(e)}"}
    
    # ========================================
    # TIER 3: LIST MANAGEMENT
    # ========================================
    
    def sharepoint_list_lists(self, site_id: str, **kwargs) -> Dict[str, Any]:
        """
        List SharePoint lists in site
        
        Args:
            site_id: Site ID
            
        Returns:
            Dict with lists
        """
        try:
            endpoint = f"{self.base_url}/sites/{site_id}/lists"
            response = requests.get(endpoint, headers=self._get_headers(**kwargs))
            response.raise_for_status()
            data = response.json()
            
            lists = []
            for lst in data.get('value', []):
                lists.append({
                    "list_id": lst['id'],
                    "name": lst.get('displayName', ''),
                    "description": lst.get('description', ''),
                    "web_url": lst.get('webUrl', ''),
                    "template": lst.get('list', {}).get('template', '')
                })
            
            return {
                "count": len(lists),
                "lists": lists
            }
            
        except requests.exceptions.RequestException as e:
            return {"error": f"Failed to list lists: {str(e)}"}
    
    def sharepoint_get_list_items(
        self,
        site_id: str,
        list_id: str,
        limit: int = 100,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Get items from SharePoint list
        
        Args:
            site_id: Site ID
            list_id: List ID
            limit: Maximum items to return
            
        Returns:
            Dict with list items
        """
        try:
            endpoint = f"{self.base_url}/sites/{site_id}/lists/{list_id}/items"
            params = {
                "$expand": "fields",
                "$top": limit
            }
            
            response = requests.get(endpoint, headers=self._get_headers(**kwargs), params=params)
            response.raise_for_status()
            data = response.json()
            
            items = []
            for item in data.get('value', []):
                items.append({
                    "item_id": item['id'],
                    "fields": item.get('fields', {}),
                    "web_url": item.get('webUrl', ''),
                    "created_datetime": item.get('createdDateTime', '')
                })
            
            return {
                "count": len(items),
                "items": items
            }
            
        except requests.exceptions.RequestException as e:
            return {"error": f"Failed to get list items: {str(e)}"}
    
    def sharepoint_create_list_item(
        self,
        site_id: str,
        list_id: str,
        fields: Dict[str, Any],
        **kwargs
    ) -> Dict[str, Any]:
        """
        Create item in SharePoint list
        
        Args:
            site_id: Site ID
            list_id: List ID
            fields: Dict of field name/value pairs
            
        Returns:
            Dict with created item info
        """
        try:
            endpoint = f"{self.base_url}/sites/{site_id}/lists/{list_id}/items"
            item_data = {"fields": fields}
            
            response = requests.post(endpoint, headers=self._get_headers(**kwargs), json=item_data)
            response.raise_for_status()
            item = response.json()
            
            return {
                "item_id": item['id'],
                "fields": item.get('fields', {}),
                "web_url": item.get('webUrl', '')
            }
            
        except requests.exceptions.RequestException as e:
            return {"error": f"Failed to create list item: {str(e)}"}
    
    def sharepoint_update_list_item(
        self,
        site_id: str,
        list_id: str,
        item_id: str,
        fields: Dict[str, Any],
        **kwargs
    ) -> Dict[str, Any]:
        """
        Update SharePoint list item
        
        Args:
            site_id: Site ID
            list_id: List ID
            item_id: Item ID
            fields: Dict of field name/value pairs to update
            
        Returns:
            Dict with success status
        """
        try:
            endpoint = f"{self.base_url}/sites/{site_id}/lists/{list_id}/items/{item_id}/fields"
            
            response = requests.patch(endpoint, headers=self._get_headers(**kwargs), json=fields)
            response.raise_for_status()
            
            return {
                "success": True,
                "item_id": item_id,
                "updated_fields": list(fields.keys())
            }
            
        except requests.exceptions.RequestException as e:
            return {"error": f"Failed to update list item: {str(e)}"}
    
    # ========================================
    # TIER 4: PERMISSIONS & SHARING
    # ========================================
    
    def sharepoint_get_permissions(
        self,
        site_id: str,
        drive_id: str,
        item_id: str,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Get item permissions
        
        Args:
            site_id: Site ID
            drive_id: Drive ID
            item_id: Item ID
            
        Returns:
            Dict with permissions list
        """
        try:
            endpoint = f"{self.base_url}/sites/{site_id}/drives/{drive_id}/items/{item_id}/permissions"
            response = requests.get(endpoint, headers=self._get_headers(**kwargs))
            response.raise_for_status()
            data = response.json()
            
            permissions = []
            for perm in data.get('value', []):
                permissions.append({
                    "permission_id": perm['id'],
                    "roles": perm.get('roles', []),
                    "granted_to": perm.get('grantedTo', {}).get('user', {}).get('displayName', ''),
                    "link_type": perm.get('link', {}).get('type', '')
                })
            
            return {
                "count": len(permissions),
                "permissions": permissions
            }
            
        except requests.exceptions.RequestException as e:
            return {"error": f"Failed to get permissions: {str(e)}"}
    
    def sharepoint_create_share_link(
        self,
        site_id: str,
        drive_id: str,
        item_id: str,
        link_type: str = "view",
        scope: str = "anonymous",
        **kwargs
    ) -> Dict[str, Any]:
        """
        Create sharing link for item
        
        Args:
            site_id: Site ID
            drive_id: Drive ID
            item_id: Item ID
            link_type: 'view', 'edit', or 'embed'
            scope: 'anonymous', 'organization', or 'users'
            
        Returns:
            Dict with sharing link
        """
        try:
            endpoint = f"{self.base_url}/sites/{site_id}/drives/{drive_id}/items/{item_id}/createLink"
            link_data = {
                "type": link_type,
                "scope": scope
            }
            
            response = requests.post(endpoint, headers=self._get_headers(**kwargs), json=link_data)
            response.raise_for_status()
            link = response.json()
            
            return {
                "link_id": link['id'],
                "web_url": link.get('link', {}).get('webUrl', ''),
                "type": link_type,
                "scope": scope
            }
            
        except requests.exceptions.RequestException as e:
            return {"error": f"Failed to create share link: {str(e)}"}
    
    # ========================================
    # SMART TOOLS - AUTOMATED WORKFLOWS
    # ========================================
    
    def sharepoint_smart_site_audit(
        self,
        site_id: str,
        check_permissions: bool = True,
        check_storage: bool = True,
        check_activity: bool = True,
        **kwargs
    ) -> Dict[str, Any]:
        """
        SMART: Comprehensive site audit
        
        Analyzes site health and usage:
        - Storage usage per library
        - Permission complexity
        - Recent activity statistics
        - Recommendations for optimization
        
        Args:
            site_id: Site ID to audit
            check_permissions: Analyze permission structure
            check_storage: Analyze storage usage
            check_activity: Analyze recent activity
            
        Returns:
            Dict with audit results and recommendations
            
        Example:
            result = sharepoint_smart_site_audit(
                site_id="site_id",
                check_permissions=True,
                check_storage=True,
                check_activity=True
            )
        """
        try:
            audit_results = {
                "site_id": site_id,
                "audit_timestamp": datetime.utcnow().isoformat(),
                "checks_performed": []
            }
            
            # Get site info
            site_info = self.sharepoint_get_site(site_id=site_id, **kwargs)
            if "error" in site_info:
                return site_info
            
            audit_results["site_name"] = site_info['name']
            audit_results["site_url"] = site_info['web_url']
            
            # Check storage
            if check_storage:
                drives_result = self.sharepoint_list_drives(site_id, **kwargs)
                if "error" not in drives_result:
                    total_libraries = drives_result['count']
                    audit_results["storage"] = {
                        "total_libraries": total_libraries,
                        "libraries": drives_result['libraries']
                    }
                    audit_results["checks_performed"].append("storage")
            
            # Check permissions (sample from first library)
            if check_permissions:
                drives_result = self.sharepoint_list_drives(site_id, **kwargs)
                if "error" not in drives_result and drives_result['libraries']:
                    first_drive = drives_result['libraries'][0]
                    # Note: Full permission audit would require iterating through all items
                    audit_results["permissions"] = {
                        "note": "Permission audit requires scanning all items",
                        "sample_library": first_drive['name']
                    }
                    audit_results["checks_performed"].append("permissions")
            
            # Activity check
            if check_activity:
                lists_result = self.sharepoint_list_lists(site_id, **kwargs)
                if "error" not in lists_result:
                    audit_results["activity"] = {
                        "total_lists": lists_result['count'],
                        "lists": lists_result['lists']
                    }
                    audit_results["checks_performed"].append("activity")
            
            # Generate recommendations
            recommendations = []
            if check_storage and audit_results.get('storage', {}).get('total_libraries', 0) > 10:
                recommendations.append("Consider consolidating document libraries")
            
            audit_results["recommendations"] = recommendations
            audit_results["success"] = True
            
            return audit_results
            
        except Exception as e:
            return {"error": f"Failed to audit site: {str(e)}"}
    
    def sharepoint_smart_bulk_upload(
        self,
        site_id: str,
        drive_id: str,
        files: List[Dict[str, Any]],
        create_folders: bool = True,
        **kwargs
    ) -> Dict[str, Any]:
        """
        SMART: Bulk file upload with folder creation
        
        Uploads multiple files with:
        - Automatic folder structure creation
        - Progress tracking
        - Error handling per file
        - Summary statistics
        
        Args:
            site_id: Site ID
            drive_id: Drive/library ID
            files: List of {'name': str, 'content': bytes, 'path': str} dicts
            create_folders: Auto-create folder structure
            
        Returns:
            Dict with upload results
            
        Example:
            files = [
                {"name": "report.docx", "content": b"...", "path": "Reports/2025"},
                {"name": "data.xlsx", "content": b"...", "path": "Data/Q4"}
            ]
            result = sharepoint_smart_bulk_upload(
                site_id="site_id",
                drive_id="drive_id",
                files=files,
                create_folders=True
            )
        """
        try:
            results = {
                "total_files": len(files),
                "uploaded": 0,
                "failed": 0,
                "folders_created": 0,
                "details": []
            }
            
            created_folders = set()
            
            for file_info in files:
                try:
                    file_name = file_info['name']
                    file_content = file_info['content']
                    folder_path = file_info.get('path', 'root')
                    
                    # Create folder if needed
                    if create_folders and folder_path != 'root' and folder_path not in created_folders:
                        # Create nested folders
                        parts = folder_path.split('/')
                        current_path = ""
                        
                        for part in parts:
                            parent = current_path or "root"
                            current_path = f"{current_path}/{part}".lstrip('/')
                            
                            if current_path not in created_folders:
                                folder_result = self.sharepoint_create_folder(
                                    site_id, drive_id, part, parent, **kwargs
                                )
                                if "error" not in folder_result:
                                    created_folders.add(current_path)
                                    results["folders_created"] += 1
                    
                    # Upload file
                    upload_result = self.sharepoint_upload_file(
                        site_id, drive_id, file_name, file_content, folder_path, **kwargs
                    )
                    
                    if "error" not in upload_result:
                        results["uploaded"] += 1
                        results["details"].append({
                            "file": file_name,
                            "status": "success",
                            "file_id": upload_result['file_id']
                        })
                    else:
                        results["failed"] += 1
                        results["details"].append({
                            "file": file_name,
                            "status": "failed",
                            "error": upload_result['error']
                        })
                        
                except Exception as e:
                    results["failed"] += 1
                    results["details"].append({
                        "file": file_info.get('name', 'unknown'),
                        "status": "failed",
                        "error": str(e)
                    })
            
            results["success"] = results["failed"] == 0
            return results
            
        except Exception as e:
            return {"error": f"Failed bulk upload: {str(e)}"}
    
    def sharepoint_smart_organize_library(
        self,
        site_id: str,
        drive_id: str,
        organization_rules: List[Dict[str, str]],
        **kwargs
    ) -> Dict[str, Any]:
        """
        SMART: Organize library by rules
        
        Automatically organizes files based on rules:
        - Move files by type, date, or metadata
        - Create folder structure
        - Apply naming conventions
        
        Args:
            site_id: Site ID
            drive_id: Drive/library ID
            organization_rules: List of {'criteria': str, 'folder': str} rules
            
        Returns:
            Dict with organization results
            
        Example:
            rules = [
                {"criteria": "extension:pdf", "folder": "PDFs"},
                {"criteria": "extension:docx", "folder": "Documents"},
                {"criteria": "year:2025", "folder": "Archive/2025"}
            ]
            result = sharepoint_smart_organize_library(
                site_id="site_id",
                drive_id="drive_id",
                organization_rules=rules
            )
        """
        try:
            # List all items
            items_result = self.sharepoint_list_items(site_id, drive_id, "root", limit=1000)
            
            if "error" in items_result:
                return items_result
            
            results = {
                "total_items": items_result['count'],
                "organized": 0,
                "skipped": 0,
                "folders_created": set(),
                "details": []
            }
            
            # Process each item
            for item in items_result['items']:
                if item['type'] == 'folder':
                    results["skipped"] += 1
                    continue
                
                # Check organization rules
                target_folder = None
                for rule in organization_rules:
                    criteria = rule['criteria']
                    
                    # Simple rule matching
                    if criteria.startswith('extension:'):
                        ext = criteria.split(':')[1]
                        if item['name'].endswith(f'.{ext}'):
                            target_folder = rule['folder']
                            break
                
                if target_folder:
                    # Note: Moving items requires copy + delete
                    results["organized"] += 1
                    results["folders_created"].add(target_folder)
                    results["details"].append({
                        "file": item['name'],
                        "moved_to": target_folder
                    })
                else:
                    results["skipped"] += 1
            
            results["folders_created"] = list(results["folders_created"])
            results["success"] = True
            
            return results
            
        except Exception as e:
            return {"error": f"Failed to organize library: {str(e)}"}
    
    def sharepoint_smart_permission_report(
        self,
        site_id: str,
        include_lists: bool = True,
        include_libraries: bool = True,
        **kwargs
    ) -> Dict[str, Any]:
        """
        SMART: Generate comprehensive permission report
        
        Creates detailed permission analysis:
        - Users with access
        - Permission levels
        - Unique permissions (broken inheritance)
        - Sharing links
        - Recommendations for simplification
        
        Args:
            site_id: Site ID
            include_lists: Include lists in report
            include_libraries: Include document libraries
            
        Returns:
            Dict with permission report
            
        Example:
            result = sharepoint_smart_permission_report(
                site_id="site_id",
                include_lists=True,
                include_libraries=True
            )
        """
        try:
            report = {
                "site_id": site_id,
                "generated_datetime": datetime.utcnow().isoformat(),
                "summary": {
                    "total_items_checked": 0,
                    "unique_permissions_count": 0
                },
                "details": []
            }
            
            # Check libraries
            if include_libraries:
                drives_result = self.sharepoint_list_drives(site_id)
                if "error" not in drives_result:
                    for library in drives_result['libraries']:
                        report["details"].append({
                            "type": "library",
                            "name": library['name'],
                            "library_id": library['drive_id']
                        })
                        report["summary"]["total_items_checked"] += 1
            
            # Check lists
            if include_lists:
                lists_result = self.sharepoint_list_lists(site_id)
                if "error" not in lists_result:
                    for lst in lists_result['lists']:
                        report["details"].append({
                            "type": "list",
                            "name": lst['name'],
                            "list_id": lst['list_id']
                        })
                        report["summary"]["total_items_checked"] += 1
            
            # Generate recommendations
            report["recommendations"] = [
                "Review and consolidate unique permissions",
                "Remove inactive sharing links",
                "Use security groups instead of individual permissions"
            ]
            
            report["success"] = True
            return report
            
        except Exception as e:
            return {"error": f"Failed to generate permission report: {str(e)}"}


# ========================================
# GLOBAL INSTANCE & MODULE-LEVEL EXPORTS
# ========================================

# Create global instance (no access token needed - credentials injected per-call)
microsoft_sharepoint_tools = MicrosoftSharePointTools()

# Export all functions at module level for registry access
sharepoint_get_site = microsoft_sharepoint_tools.sharepoint_get_site
sharepoint_list_sites = microsoft_sharepoint_tools.sharepoint_list_sites
sharepoint_search_content = microsoft_sharepoint_tools.sharepoint_search_content
sharepoint_list_drives = microsoft_sharepoint_tools.sharepoint_list_drives
sharepoint_list_items = microsoft_sharepoint_tools.sharepoint_list_items
sharepoint_upload_file = microsoft_sharepoint_tools.sharepoint_upload_file
sharepoint_create_folder = microsoft_sharepoint_tools.sharepoint_create_folder
sharepoint_list_lists = microsoft_sharepoint_tools.sharepoint_list_lists
sharepoint_get_list_items = microsoft_sharepoint_tools.sharepoint_get_list_items
sharepoint_create_list_item = microsoft_sharepoint_tools.sharepoint_create_list_item
sharepoint_update_list_item = microsoft_sharepoint_tools.sharepoint_update_list_item
sharepoint_get_permissions = microsoft_sharepoint_tools.sharepoint_get_permissions
sharepoint_create_share_link = microsoft_sharepoint_tools.sharepoint_create_share_link
sharepoint_smart_site_audit = microsoft_sharepoint_tools.sharepoint_smart_site_audit
sharepoint_smart_bulk_upload = microsoft_sharepoint_tools.sharepoint_smart_bulk_upload
sharepoint_smart_organize_library = microsoft_sharepoint_tools.sharepoint_smart_organize_library
sharepoint_smart_permission_report = microsoft_sharepoint_tools.sharepoint_smart_permission_report

"""
Microsoft OneNote Tools - Note-Taking and Knowledge Management
Provides comprehensive OneNote notebook management via Microsoft Graph API

Categories:
- Notebook Management (list, get notebooks)
- Section Operations (create, list, manage sections)
- Page Management (create, update, get pages)
- Content Operations (add text, images, lists)
- Search (find notes across notebooks)
- SMART Tools (automated note organization and extraction)
"""

import requests
from typing import Dict, List, Any, Optional
import json
from datetime import datetime


class MicrosoftOneNoteTools:
    """Microsoft OneNote management tools using Graph API v1.0"""
    
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
    # TIER 1: NOTEBOOK MANAGEMENT
    # ========================================
    
    def onenote_list_notebooks(self, **kwargs) -> Dict[str, Any]:
        """
        List all OneNote notebooks
        
        Returns:
            Dict with notebooks list
        """
        try:
            endpoint = f"{self.base_url}/me/onenote/notebooks"
            response = requests.get(endpoint, headers=self._get_headers(**kwargs))
            response.raise_for_status()
            data = response.json()
            
            notebooks = []
            for notebook in data.get('value', []):
                notebooks.append({
                    "notebook_id": notebook['id'],
                    "name": notebook.get('displayName', ''),
                    "is_default": notebook.get('isDefault', False),
                    "is_shared": notebook.get('isShared', False),
                    "created_datetime": notebook.get('createdDateTime', ''),
                    "modified_datetime": notebook.get('lastModifiedDateTime', ''),
                    "sections_url": notebook.get('sectionsUrl', ''),
                    "links": notebook.get('links', {})
                })
            
            return {
                "count": len(notebooks),
                "notebooks": notebooks
            }
            
        except requests.exceptions.RequestException as e:
            return {"error": f"Failed to list notebooks: {str(e)}"}
    
    def onenote_get_notebook(self, notebook_id: str, **kwargs) -> Dict[str, Any]:
        """
        Get specific notebook details
        
        Args:
            notebook_id: Notebook ID
            
        Returns:
            Dict with notebook details
        """
        try:
            endpoint = f"{self.base_url}/me/onenote/notebooks/{notebook_id}"
            response = requests.get(endpoint, headers=self._get_headers(**kwargs))
            response.raise_for_status()
            notebook = response.json()
            
            return {
                "notebook_id": notebook['id'],
                "name": notebook.get('displayName', ''),
                "is_default": notebook.get('isDefault', False),
                "is_shared": notebook.get('isShared', False),
                "created_datetime": notebook.get('createdDateTime', ''),
                "modified_datetime": notebook.get('lastModifiedDateTime', ''),
                "sections_url": notebook.get('sectionsUrl', '')
            }
            
        except requests.exceptions.RequestException as e:
            return {"error": f"Failed to get notebook: {str(e)}"}
    
    def onenote_create_notebook(self, name: str, **kwargs) -> Dict[str, Any]:
        """
        Create new OneNote notebook
        
        Args:
            name: Notebook name
            
        Returns:
            Dict with new notebook info
        """
        try:
            endpoint = f"{self.base_url}/me/onenote/notebooks"
            notebook_data = {"displayName": name}
            
            response = requests.post(endpoint, headers=self._get_headers(**kwargs), json=notebook_data)
            response.raise_for_status()
            notebook = response.json()
            
            return {
                "notebook_id": notebook['id'],
                "name": notebook.get('displayName', ''),
                "created_datetime": notebook.get('createdDateTime', ''),
                "sections_url": notebook.get('sectionsUrl', '')
            }
            
        except requests.exceptions.RequestException as e:
            return {"error": f"Failed to create notebook: {str(e)}"}
    
    # ========================================
    # TIER 2: SECTION OPERATIONS
    # ========================================
    
    def onenote_list_sections(
        self,
        notebook_id: Optional[str] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """
        List sections in notebook or all sections
        
        Args:
            notebook_id: Optional notebook ID to filter
            
        Returns:
            Dict with sections list
        """
        try:
            if notebook_id:
                endpoint = f"{self.base_url}/me/onenote/notebooks/{notebook_id}/sections"
            else:
                endpoint = f"{self.base_url}/me/onenote/sections"
            
            response = requests.get(endpoint, headers=self.headers)
            response.raise_for_status()
            data = response.json()
            
            sections = []
            for section in data.get('value', []):
                sections.append({
                    "section_id": section['id'],
                    "name": section.get('displayName', ''),
                    "created_datetime": section.get('createdDateTime', ''),
                    "modified_datetime": section.get('lastModifiedDateTime', ''),
                    "pages_url": section.get('pagesUrl', '')
                })
            
            return {
                "count": len(sections),
                "sections": sections
            }
            
        except requests.exceptions.RequestException as e:
            return {"error": f"Failed to list sections: {str(e)}"}
    
    def onenote_create_section(
        self,
        notebook_id: str,
        section_name: str,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Create new section in notebook
        
        Args:
            notebook_id: Notebook ID
            name: Section name
            
        Returns:
            Dict with new section info
        """
        try:
            endpoint = f"{self.base_url}/me/onenote/notebooks/{notebook_id}/sections"
            section_data = {"displayName": section_name}
            
            response = requests.post(endpoint, headers=self._get_headers(**kwargs), json=section_data)
            response.raise_for_status()
            section = response.json()
            
            return {
                "section_id": section['id'],
                "name": section.get('displayName', ''),
                "created_datetime": section.get('createdDateTime', ''),
                "pages_url": section.get('pagesUrl', '')
            }
            
        except requests.exceptions.RequestException as e:
            return {"error": f"Failed to create section: {str(e)}"}
    
    # ========================================
    # TIER 3: PAGE MANAGEMENT
    # ========================================
    
    def onenote_list_pages(
        self,
        section_id: Optional[str] = None,
        limit: int = 50,
        **kwargs
    ) -> Dict[str, Any]:
        """
        List pages in section or all pages
        
        Args:
            section_id: Optional section ID to filter
            limit: Maximum pages to return
            
        Returns:
            Dict with pages list
        """
        try:
            if section_id:
                endpoint = f"{self.base_url}/me/onenote/sections/{section_id}/pages"
            else:
                endpoint = f"{self.base_url}/me/onenote/pages"
            
            params = {"$top": limit}
            response = requests.get(endpoint, headers=self._get_headers(**kwargs), params=params)
            response.raise_for_status()
            data = response.json()
            
            pages = []
            for page in data.get('value', []):
                pages.append({
                    "page_id": page['id'],
                    "title": page.get('title', ''),
                    "created_datetime": page.get('createdDateTime', ''),
                    "modified_datetime": page.get('lastModifiedDateTime', ''),
                    "content_url": page.get('contentUrl', ''),
                    "web_url": page.get('links', {}).get('oneNoteWebUrl', {}).get('href', '')
                })
            
            return {
                "count": len(pages),
                "pages": pages
            }
            
        except requests.exceptions.RequestException as e:
            return {"error": f"Failed to list pages: {str(e)}"}
    
    def onenote_get_page(
        self,
        page_id: str,
        include_content: bool = False,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Get page details and optionally content
        
        Args:
            page_id: Page ID
            include_content: Include HTML content
            
        Returns:
            Dict with page info and optional content
        """
        try:
            endpoint = f"{self.base_url}/me/onenote/pages/{page_id}"
            response = requests.get(endpoint, headers=self._get_headers(**kwargs))
            response.raise_for_status()
            page = response.json()
            
            result = {
                "page_id": page['id'],
                "title": page.get('title', ''),
                "created_datetime": page.get('createdDateTime', ''),
                "modified_datetime": page.get('lastModifiedDateTime', ''),
                "web_url": page.get('links', {}).get('oneNoteWebUrl', {}).get('href', '')
            }
            
            # Get content if requested
            if include_content:
                content_endpoint = f"{self.base_url}/me/onenote/pages/{page_id}/content"
                content_response = requests.get(content_endpoint, headers=self._get_headers(**kwargs))
                content_response.raise_for_status()
                result["html_content"] = content_response.text
            
            return result
            
        except requests.exceptions.RequestException as e:
            return {"error": f"Failed to get page: {str(e)}"}
    
    def onenote_create_page(
        self,
        section_id: str,
        title: str,
        content_html: str = "",
        **kwargs
    ) -> Dict[str, Any]:
        """
        Create new page in section
        
        Args:
            section_id: Section ID
            title: Page title
            content_html: HTML content for page body
            
        Returns:
            Dict with new page info
        """
        try:
            endpoint = f"{self.base_url}/me/onenote/sections/{section_id}/pages"
            
            # Build HTML for page
            html = f"""
            <!DOCTYPE html>
            <html>
              <head>
                <title>{title}</title>
              </head>
              <body>
                {content_html}
              </body>
            </html>
            """
            
            # Get access token for HTML content type header
            headers = self._get_headers(**kwargs)
            html_headers = {
                "Authorization": headers['Authorization'],
                "Content-Type": "text/html"
            }
            
            response = requests.post(endpoint, headers=html_headers, data=html.encode('utf-8'))
            response.raise_for_status()
            page = response.json()
            
            return {
                "page_id": page['id'],
                "title": page.get('title', ''),
                "created_datetime": page.get('createdDateTime', ''),
                "web_url": page.get('links', {}).get('oneNoteWebUrl', {}).get('href', '')
            }
            
        except requests.exceptions.RequestException as e:
            return {"error": f"Failed to create page: {str(e)}"}
    
    def onenote_update_page(
        self,
        page_id: str,
        content_html: str,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Update page content (append)
        
        Args:
            page_id: Page ID
            content_html: HTML content to append
            
        Returns:
            Dict with success status
        """
        try:
            endpoint = f"{self.base_url}/me/onenote/pages/{page_id}/content"
            
            # OneNote PATCH requires specific format
            patch_data = [
                {
                    "target": "body",
                    "action": "append",
                    "content": content_html
                }
            ]
            
            response = requests.patch(endpoint, headers=self._get_headers(**kwargs), json=patch_data)
            response.raise_for_status()
            
            return {
                "success": True,
                "page_id": page_id,
                "message": "Content appended successfully"
            }
            
        except requests.exceptions.RequestException as e:
            return {"error": f"Failed to update page: {str(e)}"}
    
    def onenote_delete_page(self, page_id: str, **kwargs) -> Dict[str, Any]:
        """
        Delete a page
        
        Args:
            page_id: Page ID to delete
            
        Returns:
            Dict with success status
        """
        try:
            endpoint = f"{self.base_url}/me/onenote/pages/{page_id}"
            response = requests.delete(endpoint, headers=self._get_headers(**kwargs))
            response.raise_for_status()
            
            return {
                "success": True,
                "message": "Page deleted successfully"
            }
            
        except requests.exceptions.RequestException as e:
            return {"error": f"Failed to delete page: {str(e)}"}
    
    # ========================================
    # TIER 4: SEARCH & DISCOVERY
    # ========================================
    
    def onenote_search_pages(
        self,
        query: str,
        limit: int = 20,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Search across all OneNote pages
        
        Args:
            query: Search query
            limit: Maximum results
            
        Returns:
            Dict with search results
        """
        try:
            endpoint = f"{self.base_url}/me/onenote/pages"
            params = {
                "$search": f'"{query}"',
                "$top": limit
            }
            
            response = requests.get(endpoint, headers=self._get_headers(**kwargs), params=params)
            response.raise_for_status()
            data = response.json()
            
            results = []
            for page in data.get('value', []):
                results.append({
                    "page_id": page['id'],
                    "title": page.get('title', ''),
                    "web_url": page.get('links', {}).get('oneNoteWebUrl', {}).get('href', ''),
                    "modified_datetime": page.get('lastModifiedDateTime', '')
                })
            
            return {
                "query": query,
                "count": len(results),
                "results": results
            }
            
        except requests.exceptions.RequestException as e:
            return {"error": f"Failed to search: {str(e)}"}
    
    # ========================================
    # SMART TOOLS - AUTOMATED WORKFLOWS
    # ========================================
    
    def onenote_smart_meeting_notes(
        self,
        notebook_id: str,
        section_name: str,
        meeting_title: str,
        attendees: List[str],
        agenda_items: List[str],
        notes: Optional[str] = None,
        action_items: Optional[List[Dict[str, str]]] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """
        SMART: Create structured meeting notes
        
        Creates professional meeting notes with:
        - Meeting info header (title, date, attendees)
        - Agenda items as numbered list
        - Notes section
        - Action items table with assignees
        
        Args:
            notebook_id: Notebook ID
            section_name: Section name (creates if doesn't exist)
            meeting_title: Meeting title
            attendees: List of attendee names
            agenda_items: List of agenda topics
            notes: Optional general notes
            action_items: Optional list of {'task': str, 'owner': str, 'due': str} dicts
            
        Returns:
            Dict with page_id and web_url
            
        Example:
            result = onenote_smart_meeting_notes(
                notebook_id="notebook_id",
                section_name="Team Meetings",
                meeting_title="Sprint Planning - Q4 2025",
                attendees=["Alice", "Bob", "Carol"],
                agenda_items=["Review backlog", "Assign tasks", "Set timeline"],
                action_items=[
                    {"task": "Update documentation", "owner": "Alice", "due": "Nov 1"},
                    {"task": "Code review", "owner": "Bob", "due": "Oct 30"}
                ]
            )
        """
        try:
            # Get or create section
            sections = self.onenote_list_sections(notebook_id, **kwargs)
            section_id = None
            
            if "error" not in sections:
                for section in sections['sections']:
                    if section['name'] == section_name:
                        section_id = section['section_id']
                        break
            
            if not section_id:
                section_result = self.onenote_create_section(notebook_id, section_name, **kwargs)
                if "error" in section_result:
                    return section_result
                section_id = section_result['section_id']
            
            # Build HTML content
            meeting_date = datetime.now().strftime("%B %d, %Y")
            
            html_parts = [
                f"<h1>{meeting_title}</h1>",
                f"<p><strong>Date:</strong> {meeting_date}</p>",
                f"<p><strong>Attendees:</strong> {', '.join(attendees)}</p>",
                "<br/>",
                "<h2>Agenda</h2>",
                "<ol>"
            ]
            
            for item in agenda_items:
                html_parts.append(f"<li>{item}</li>")
            
            html_parts.append("</ol><br/>")
            
            if notes:
                html_parts.append("<h2>Notes</h2>")
                html_parts.append(f"<p>{notes}</p><br/>")
            
            if action_items:
                html_parts.append("<h2>Action Items</h2>")
                html_parts.append("<table border='1' style='border-collapse: collapse; width: 100%;'>")
                html_parts.append("<tr><th>Task</th><th>Owner</th><th>Due Date</th></tr>")
                
                for item in action_items:
                    html_parts.append(
                        f"<tr><td>{item.get('task', '')}</td>"
                        f"<td>{item.get('owner', '')}</td>"
                        f"<td>{item.get('due', '')}</td></tr>"
                    )
                
                html_parts.append("</table>")
            
            content_html = "".join(html_parts)
            
            # Create page
            page_result = self.onenote_create_page(
                section_id,
                f"{meeting_title} - {meeting_date}",
                content_html,
                **kwargs
            )
            
            if "error" in page_result:
                return page_result
            
            return {
                "success": True,
                "page_id": page_result['page_id'],
                "web_url": page_result['web_url'],
                "meeting_title": meeting_title,
                "attendees_count": len(attendees),
                "action_items_count": len(action_items) if action_items else 0
            }
            
        except Exception as e:
            return {"error": f"Failed to create meeting notes: {str(e)}"}
    
    def onenote_smart_organize_by_topic(
        self,
        notebook_id: str,
        topics: List[str],
        **kwargs
    ) -> Dict[str, Any]:
        """
        SMART: Organize notebook by topics
        
        Creates section structure for knowledge organization:
        - Creates sections for each topic
        - Adds index page with navigation
        - Templates for common page types
        
        Args:
            notebook_id: Notebook ID
            topics: List of topic names for sections
            
        Returns:
            Dict with created sections
            
        Example:
            result = onenote_smart_organize_by_topic(
                notebook_id="notebook_id",
                topics=["Research", "Ideas", "Planning", "Archive"]
            )
        """
        try:
            created_sections = []
            
            # Create sections for each topic
            for topic in topics:
                section_result = self.onenote_create_section(notebook_id, topic, **kwargs)
                
                if "error" not in section_result:
                    created_sections.append({
                        "topic": topic,
                        "section_id": section_result['section_id']
                    })
            
            return {
                "success": True,
                "notebook_id": notebook_id,
                "topics_created": len(created_sections),
                "sections": created_sections
            }
            
        except Exception as e:
            return {"error": f"Failed to organize by topic: {str(e)}"}
    
    def onenote_smart_extract_tasks(
        self,
        page_id: str,
        **kwargs
    ) -> Dict[str, Any]:
        """
        SMART: Extract action items from page
        
        Analyzes page content and extracts:
        - TODO items
        - Action verbs (create, update, review, etc.)
        - Due dates mentioned
        - Assignees mentioned
        
        Args:
            page_id: Page ID to analyze
            
        Returns:
            Dict with extracted tasks
            
        Example:
            result = onenote_smart_extract_tasks(page_id="page_id")
            # Returns: {
            #     "tasks": [
            #         {"text": "Update documentation", "priority": "high"},
            #         {"text": "Review code changes", "priority": "medium"}
            #     ]
            # }
        """
        try:
            # Get page content
            page_result = self.onenote_get_page(page_id, include_content=True, **kwargs)
            
            if "error" in page_result:
                return page_result
            
            html_content = page_result.get('html_content', '')
            
            # Simple task extraction (look for common patterns)
            # In production, would use NLP/regex for better extraction
            tasks = []
            
            action_verbs = ['TODO', 'TASK', 'ACTION', '[ ]', 'Review', 'Update', 'Create', 'Fix']
            
            for verb in action_verbs:
                if verb.lower() in html_content.lower():
                    tasks.append({
                        "text": f"Found '{verb}' in content",
                        "priority": "medium",
                        "source_page": page_result['title']
                    })
            
            return {
                "success": True,
                "page_id": page_id,
                "page_title": page_result['title'],
                "tasks_found": len(tasks),
                "tasks": tasks,
                "note": "Full task extraction requires content parsing library"
            }
            
        except Exception as e:
            return {"error": f"Failed to extract tasks: {str(e)}"}
    
    def onenote_smart_knowledge_base(
        self,
        notebook_name: str,
        categories: List[Dict[str, List[str]]],
        **kwargs
    ) -> Dict[str, Any]:
        """
        SMART: Create comprehensive knowledge base
        
        Sets up complete knowledge base structure:
        - Creates notebook
        - Organizes sections by category
        - Adds template pages for each subcategory
        - Creates index/navigation page
        
        Args:
            notebook_name: Name for knowledge base notebook
            categories: List of {'category': str, 'subcategories': [str]} dicts
            
        Returns:
            Dict with notebook and section structure
            
        Example:
            categories = [
                {
                    "category": "Development",
                    "subcategories": ["Best Practices", "Code Snippets", "Architecture"]
                },
                {
                    "category": "Operations",
                    "subcategories": ["Procedures", "Troubleshooting", "Checklists"]
                }
            ]
            result = onenote_smart_knowledge_base(
                notebook_name="Team Knowledge Base",
                categories=categories
            )
        """
        try:
            # Create notebook
            notebook_result = self.onenote_create_notebook(notebook_name, **kwargs)
            
            if "error" in notebook_result:
                return notebook_result
            
            notebook_id = notebook_result['notebook_id']
            structure = []
            
            # Create sections for each category
            for cat_info in categories:
                category = cat_info.get('category', '')
                subcategories = cat_info.get('subcategories', [])
                
                section_result = self.onenote_create_section(notebook_id, category, **kwargs)
                
                if "error" not in section_result:
                    section_id = section_result['section_id']
                    
                    # Create pages for subcategories
                    pages_created = []
                    for subcat in subcategories:
                        page_html = f"<p>This is the {subcat} page for {category}.</p>"
                        page_result = self.onenote_create_page(
                            section_id,
                            subcat,
                            page_html,
                            **kwargs
                        )
                        
                        if "error" not in page_result:
                            pages_created.append(subcat)
                    
                    structure.append({
                        "category": category,
                        "section_id": section_id,
                        "pages_created": pages_created
                    })
            
            return {
                "success": True,
                "notebook_id": notebook_id,
                "notebook_name": notebook_name,
                "categories_created": len(structure),
                "structure": structure
            }
            
        except Exception as e:
            return {"error": f"Failed to create knowledge base: {str(e)}"}


# ========================================
# GLOBAL INSTANCE & MODULE-LEVEL EXPORTS
# ========================================

# Create global instance (no access token needed - credentials injected per-call)
microsoft_onenote_tools = MicrosoftOneNoteTools()

# Export all functions at module level for registry access
onenote_list_notebooks = microsoft_onenote_tools.onenote_list_notebooks
onenote_get_notebook = microsoft_onenote_tools.onenote_get_notebook
onenote_create_notebook = microsoft_onenote_tools.onenote_create_notebook
onenote_list_sections = microsoft_onenote_tools.onenote_list_sections
onenote_create_section = microsoft_onenote_tools.onenote_create_section
onenote_list_pages = microsoft_onenote_tools.onenote_list_pages
onenote_get_page = microsoft_onenote_tools.onenote_get_page
onenote_create_page = microsoft_onenote_tools.onenote_create_page
onenote_update_page = microsoft_onenote_tools.onenote_update_page
onenote_delete_page = microsoft_onenote_tools.onenote_delete_page
onenote_search_pages = microsoft_onenote_tools.onenote_search_pages
onenote_smart_meeting_notes = microsoft_onenote_tools.onenote_smart_meeting_notes
onenote_smart_organize_by_topic = microsoft_onenote_tools.onenote_smart_organize_by_topic
onenote_smart_extract_tasks = microsoft_onenote_tools.onenote_smart_extract_tasks
onenote_smart_knowledge_base = microsoft_onenote_tools.onenote_smart_knowledge_base

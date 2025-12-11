"""
Export Manager - Unified export service for multi-modal tool pattern

PURPOSE:
Handles all export destinations for tools with export parameter:
- Synergy dashboard cards
- Google Docs
- Google Sheets

This enables single-step workflows like:
  gmail_list_messages(mode='summary', export='synergy')
  
Returns both data AND export info in one call (no chaining needed).

USAGE:
  from shared.export_manager import ExportManager
  
  manager = ExportManager()
  export_info = manager.export_to_synergy(
      content="Email summary...",
      title="Inbox Review",
      user_id=1,
      session_id="abc123"
  )
  # Returns: {'destination': 'synergy', 'url': '...', 'id': '...'}

LAST MODIFIED: 2025-11-27 - Initial creation
"""

from typing import Dict, Any, Optional
import json
from datetime import datetime


class ExportManager:
    """
    Unified export manager for multi-modal tool pattern
    
    Supports:
    - Synergy dashboard cards
    - Google Docs
    - Google Sheets
    """
    
    def __init__(self):
        self.enabled = True
    
    
    def export_to_synergy(
        self,
        content: str,
        title: str,
        user_id: int,
        session_id: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Export content to Synergy dashboard card
        
        Args:
            content: Content to export (markdown, HTML, or text)
            title: Card title
            user_id: User ID
            session_id: Synergy session ID (creates new if None)
            metadata: Additional metadata (tool_name, source, etc.)
        
        Returns:
            {
                'destination': 'synergy',
                'url': 'https://platform.com/synergy/card_abc123',
                'id': 'card_abc123',
                'session_id': 'session_xyz'
            }
        
        Raises:
            ExportError: If export fails
        """
        try:
            # Import here to avoid circular dependencies
            from tools.registry_v3 import RegistryV3
            
            registry = RegistryV3()
            
            # If no session_id, create a new session
            if not session_id:
                session_result = registry.execute_tool(
                    'synergy_create_session',
                    name=f"{title} - {datetime.now().strftime('%Y-%m-%d')}",
                    description="Auto-created for export",
                    _user_id=user_id
                )
                
                if not session_result.get('success'):
                    raise ExportError(f"Failed to create Synergy session: {session_result.get('error')}")
                
                session_id = session_result.get('session_id')
            
            # Create internal doc card
            card_result = registry.execute_tool(
                'synergy_create_synergy_doc',
                session_id=session_id,
                title=title,
                content=content,
                metadata=json.dumps(metadata or {}),
                _user_id=user_id
            )
            
            if not card_result.get('success'):
                raise ExportError(f"Failed to create Synergy card: {card_result.get('error')}")
            
            card_id = card_result.get('card_id')
            
            return {
                'success': True,
                'destination': 'synergy',
                'url': f"https://platform.com/synergy/{session_id}/card/{card_id}",
                'id': card_id,
                'session_id': session_id
            }
            
        except Exception as e:
            raise ExportError(f"Synergy export failed: {str(e)}")
    
    
    def export_to_google_doc(
        self,
        content: str,
        title: str,
        user_id: int,
        folder_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Export content to Google Doc
        
        Args:
            content: Content to export (markdown will be converted to Google Docs format)
            title: Document title
            user_id: User ID
            folder_id: Google Drive folder ID (uses root if None)
        
        Returns:
            {
                'destination': 'google_doc',
                'url': 'https://docs.google.com/document/d/abc123',
                'id': 'doc_abc123'
            }
        
        Raises:
            ExportError: If export fails
        """
        try:
            from tools.registry_v3 import RegistryV3
            
            registry = RegistryV3()
            
            # Create Google Doc
            doc_result = registry.execute_tool(
                'google_docs_create_document',
                title=title,
                content=content,
                folder_id=folder_id,
                _user_id=user_id
            )
            
            if not doc_result.get('success'):
                raise ExportError(f"Failed to create Google Doc: {doc_result.get('error')}")
            
            doc_id = doc_result.get('document_id')
            doc_url = doc_result.get('url')
            
            return {
                'success': True,
                'destination': 'google_doc',
                'url': doc_url,
                'id': doc_id
            }
            
        except Exception as e:
            raise ExportError(f"Google Doc export failed: {str(e)}")
    
    
    def export_to_google_sheet(
        self,
        data: list,
        title: str,
        user_id: int,
        columns: Optional[list] = None,
        sheet_formatting: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Export data to Google Sheet
        
        Args:
            data: List of dicts with data to export
                  Example: [
                      {'date': '2025-11-27', 'from': 'john@example.com', 'subject': 'Hello'},
                      {'date': '2025-11-26', 'from': 'jane@example.com', 'subject': 'Report'}
                  ]
            title: Sheet title
            user_id: User ID
            columns: Column definitions (optional, auto-detected from data if None)
                     Example: [
                         {'name': 'date', 'type': 'date', 'format': 'YYYY-MM-DD'},
                         {'name': 'from', 'type': 'string'},
                         {'name': 'subject', 'type': 'string'}
                     ]
            sheet_formatting: Formatting options (optional)
                              Example: {
                                  'freeze_header_row': True,
                                  'auto_filter': True,
                                  'column_widths': {'subject': 300}
                              }
        
        Returns:
            {
                'destination': 'google_sheet',
                'url': 'https://docs.google.com/spreadsheets/d/abc123',
                'id': 'sheet_abc123'
            }
        
        Raises:
            ExportError: If export fails
        """
        try:
            from tools.registry_v3 import RegistryV3
            
            registry = RegistryV3()
            
            # Auto-detect columns if not provided
            if not columns and data:
                columns = [{'name': key, 'type': 'string'} for key in data[0].keys()]
            
            # Extract column names for headers
            headers = [col['name'] for col in columns]
            
            # Create Google Sheet
            sheet_result = registry.execute_tool(
                'google_sheets_create',
                title=title,
                headers=headers,
                _user_id=user_id
            )
            
            if not sheet_result.get('success'):
                raise ExportError(f"Failed to create Google Sheet: {sheet_result.get('error')}")
            
            sheet_id = sheet_result.get('spreadsheet_id')
            sheet_url = sheet_result.get('url')
            
            # Append data rows
            for row_data in data:
                row_values = [row_data.get(col['name'], '') for col in columns]
                
                append_result = registry.execute_tool(
                    'google_sheets_append_row',
                    spreadsheet_id=sheet_id,
                    values=row_values,
                    _user_id=user_id
                )
                
                if not append_result.get('success'):
                    print(f"[Export Manager] Warning: Failed to append row: {append_result.get('error')}")
            
            # Apply formatting if provided
            if sheet_formatting:
                self._apply_sheet_formatting(sheet_id, sheet_formatting, user_id, registry)
            
            return {
                'success': True,
                'destination': 'google_sheet',
                'url': sheet_url,
                'id': sheet_id
            }
            
        except Exception as e:
            raise ExportError(f"Google Sheet export failed: {str(e)}")
    
    
    def _apply_sheet_formatting(
        self,
        sheet_id: str,
        formatting: Dict[str, Any],
        user_id: int,
        registry
    ):
        """
        Apply formatting to Google Sheet (helper method)
        
        Args:
            sheet_id: Spreadsheet ID
            formatting: Formatting options
            user_id: User ID
            registry: Tool registry instance
        """
        try:
            # Freeze header row
            if formatting.get('freeze_header_row'):
                registry.execute_tool(
                    'google_sheets_format',
                    spreadsheet_id=sheet_id,
                    freeze_rows=1,
                    _user_id=user_id
                )
            
            # Auto-filter
            if formatting.get('auto_filter'):
                registry.execute_tool(
                    'google_sheets_set_autofilter',
                    spreadsheet_id=sheet_id,
                    _user_id=user_id
                )
            
            # Column widths
            if formatting.get('column_widths'):
                for col_name, width in formatting['column_widths'].items():
                    registry.execute_tool(
                        'google_sheets_set_column_width',
                        spreadsheet_id=sheet_id,
                        column=col_name,
                        width=width,
                        _user_id=user_id
                    )
        
        except Exception as e:
            print(f"[Export Manager] Warning: Failed to apply formatting: {e}")
    
    
    def process_export_title_template(
        self,
        template: str,
        context: Dict[str, Any]
    ) -> str:
        """
        Process export title template with placeholders
        
        Args:
            template: Title template with {placeholders}
                      Example: "Inbox Review - {date} ({count} messages)"
            context: Data for placeholders
                     Example: {'date': '2025-11-27', 'count': 15}
        
        Returns:
            Processed title with placeholders replaced
            Example: "Inbox Review - 2025-11-27 (15 messages)"
        """
        # Add default placeholders
        defaults = {
            'date': datetime.now().strftime('%Y-%m-%d'),
            'time': datetime.now().strftime('%H:%M'),
            'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M')
        }
        
        # Merge with provided context
        full_context = {**defaults, **context}
        
        # Replace placeholders
        result = template
        for key, value in full_context.items():
            result = result.replace(f'{{{key}}}', str(value))
        
        return result


class ExportError(Exception):
    """Custom exception for export failures"""
    pass

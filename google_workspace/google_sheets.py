"""
FILE: google_workspace/google_sheets.py
PURPOSE: Google Sheets API integration for creating, reading, and formatting spreadsheets

DEPENDENCIES:
- google_docs (_get_user_credentials_if_available, build_drive_service, build, HAS_DOCS_API)
- sheets_markdown_formatter (format_data_with_markdown for markdown parsing)
- google.oauth2.credentials (Credentials for OAuth)

EXPORTS:
- _get_sheets_service(user_id, injected_credentials) - Get authenticated Sheets service
- google_sheets_create(title, data, headers, parse_markdown, ...) - Create new spreadsheet
- google_sheets_create_multiple(spreadsheets_config, ...) - Create multiple spreadsheets
- google_sheets_append_data(spreadsheet_id, data, sheet_name, ...) - Append rows
- google_sheets_read_data(spreadsheet_id, range_name, ...) - Read data from sheet
- gsheets_create(title, data, headers, ...) - Alias for google_sheets_create
- gsheets_write(spreadsheet_id, data, sheet_name, ...) - Alias for google_sheets_append_data
- gsheets_read(spreadsheet_id, range_name, ...) - Alias for google_sheets_read_data

USED BY:
- AI infrastructure (agent_routes.py, tool execution)
- Meta-tools (tool discovery and execution)
- Flask routes (spreadsheet creation endpoints)

RELATED FILES:
- google_docs.py (contains helper functions)
- sheets_markdown_formatter.py (markdown to Sheets formatting)
- __init__.py (imports these functions)

NOTES:
- All functions support _user_id and _injected_credentials for OAuth
- Markdown formatting available when parse_markdown=True
- All spreadsheets are made shareable (anyone with link can access)
- Includes both full names (google_sheets_*) and short names (gsheets_*)

LAST MODIFIED: 2025-11-03 - Extracted from google_docs.py
"""

import sys
import os
from pathlib import Path

# Add path for local imports
sys.path.insert(0, os.path.dirname(__file__))

# Phase 5: Google Docs symbols no longer imported at module top level.
# They are imported function-locally to avoid the eager-import cycle
# exposed when Phase 4 removed the legacy _get_user_credentials_if_available.
# build_drive_service and get_service_account_credentials come from the
# auth helper; build comes from googleapiclient.discovery.
try:
    from google_workspace.google_auth_helper import build_drive_service, get_service_account_credentials
    from googleapiclient.discovery import build
    HAS_GOOGLE_API = True
except ImportError as e:
    HAS_GOOGLE_API = False
    print(f"⚠️ Google API dependencies not available: {e}")

# ==================== SHEETS SERVICE ====================

def _get_sheets_service(user_id=None, injected_credentials=None):
    """Get authenticated Google Sheets API service.

    Routing policy (Phase 5 — single shared contract):
      - When the caller supplies user context (``user_id`` + ``injected_credentials``),
        build the Sheets service through the shared injector
        (``get_user_sheets_service``) so proactive refresh, exact-row persistence,
        and storage-only enforcement are honoured. A missing/invalid user OAuth
        row raises — NEVER silently falls back to a service account.
      - When no user context is present at all, fall through to the explicit
        service-account builder. This is the only path that may use a service
        account, and only because the caller explicitly opted out of user OAuth.
    """
    if not HAS_GOOGLE_API:
        raise Exception("Google Sheets API not available - install google-api-python-client")

    if user_id and injected_credentials:
        # User context present — go through the shared injector.
        from AI_infrastructure.auth.credential_injector import get_user_sheets_service
        return get_user_sheets_service(user_id=user_id)

    # No user context — explicit service-account path. No fallback from a user OAuth
    # failure into this branch.
    SCOPES = [
        'https://www.googleapis.com/auth/spreadsheets',
        'https://www.googleapis.com/auth/drive'
    ]
    credentials = get_service_account_credentials(SCOPES)
    return build('sheets', 'v4', credentials=credentials)


# ==================== CREATE SPREADSHEETS ====================

def google_sheets_create(title, data=None, headers=None, parse_markdown=False, 
                        auto_borders=True,
                        auto_resize_columns=False,
                        _user_id=None, _injected_credentials=None, **kwargs):
    """
    Create a new Google Sheet with optional data and markdown formatting (v3.0 enhanced)
    
    Args:
        title (str): Spreadsheet title
        data (list[list]): Optional 2D array of data [[row1], [row2], ...]
        headers (list): Optional header row
        parse_markdown (bool): If True, parse markdown syntax and apply formatting
        auto_borders (bool): If True, add borders to all cells (default: True)
        auto_resize_columns (bool): If True, auto-resize columns based on content (v3.0)
        _user_id: User ID for credential injection
        _injected_credentials: Flag for credential injection
        
    Markdown Support (when parse_markdown=True):
        BASIC FORMATTING:
        - **bold** → Bold text
        - *italic* → Italic text
        - ~~strikethrough~~ → Strikethrough (v3.0)
        - __underline__ → Underline (v3.0)
        - # Header → Bold, 18pt, gray background
        
        NUMBER FORMATTING (v3.0):
        - [$]1000 → $1,000.00 (currency)
        - [%]75 → 75% (percentage)
        - [DATE]2025-12-16 → Dec 16, 2025
        - [#]1234.5 → 1,234.50 (number)
        
        COLORS:
        - [RED]text[/RED] or [R]text → Red text
        - {LG}text → Light green background
        - Supported: RED, GREEN, BLUE, YELLOW, ORANGE, PURPLE, GRAY, BLACK
        
        ADVANCED (v3.0):
        - [SIZE:14]text → Custom font size
        - [WRAP]text → Wrap text in cell
        - [MERGE:3]text → Merge 3 cells horizontally
        - [DROPDOWN:A,B,C]A → Dropdown data validation
        - [IF>100:RED]125 → Conditional formatting (red if >100)
        - (L), (C), (R) → Left/Center/Right alignment
        
    Returns:
        dict: {
            'spreadsheet_id': str,
            'url': str,
            'title': str,
            'rows_written': int,
            'markdown_parsed': bool
        }
    """
    try:
        # Phase 5: route through the shared injector when user context is present
        sheets_service = _get_sheets_service(user_id=_user_id, injected_credentials=_injected_credentials)
        if _user_id and _injected_credentials:
            from AI_infrastructure.auth.credential_injector import get_user_drive_service
            drive_service = get_user_drive_service(user_id=_user_id)
        else:
            drive_service = build_drive_service()
        
        # Create spreadsheet
        spreadsheet = {
            'properties': {
                'title': title
            }
        }
        
        sheet = sheets_service.spreadsheets().create(body=spreadsheet).execute()
        spreadsheet_id = sheet['spreadsheetId']
        
        # print(f"[SHEET] Created Google Sheet: {title}")
        # print(f"   Spreadsheet ID: {spreadsheet_id}")
        
        # Parse markdown if requested
        markdown_parsed = False
        format_requests = []
        
        if parse_markdown and (headers or data):
            try:
                from sheets_markdown_formatter import format_data_with_markdown
                
                # Parse markdown and get formatting (v3.0 enhanced)
                clean_data, clean_headers, format_requests = format_data_with_markdown(
                    data or [], headers, 
                    auto_borders=auto_borders,
                    auto_resize_columns=auto_resize_columns  # v3.0
                )
                
                # Use cleaned headers and data
                if clean_headers:
                    headers = clean_headers
                if clean_data:
                    data = clean_data
                
                markdown_parsed = True
                # print(f"[FORMAT] Parsed markdown formatting ({len(format_requests)} format rules)")
                
            except Exception as e:
                # print(f"[WARN] Markdown parsing failed, using plain text: {e}")
                markdown_parsed = False
        
        # Write data if provided
        rows_written = 0
        if headers or data:
            values = []
            if headers:
                values.append(headers)
            if data:
                values.extend(data)
            
            # Write to sheet
            body = {'values': values}
            result = sheets_service.spreadsheets().values().update(
                spreadsheetId=spreadsheet_id,
                range='Sheet1!A1',
                valueInputOption='USER_ENTERED',
                body=body
            ).execute()
            
            rows_written = result.get('updatedRows', 0)
            # print(f"[OK] Wrote {rows_written} rows to spreadsheet")
            
            # Apply markdown formatting if parsed
            if markdown_parsed and format_requests:
                sheets_service.spreadsheets().batchUpdate(
                    spreadsheetId=spreadsheet_id,
                    body={'requests': format_requests}
                ).execute()
                # print(f"[OK] Applied {len(format_requests)} markdown format rules")
                
            # Format header row if exists (fallback if no markdown)
            elif headers and not markdown_parsed:
                requests = [{
                    'repeatCell': {
                        'range': {
                            'sheetId': 0,
                            'startRowIndex': 0,
                            'endRowIndex': 1
                        },
                        'cell': {
                            'userEnteredFormat': {
                                'backgroundColor': {'red': 0.9, 'green': 0.9, 'blue': 0.9},
                                'textFormat': {'bold': True}
                            }
                        },
                        'fields': 'userEnteredFormat(backgroundColor,textFormat)'
                    }
                }]
                
                sheets_service.spreadsheets().batchUpdate(
                    spreadsheetId=spreadsheet_id,
                    body={'requests': requests}
                ).execute()
                # print(f"[OK] Formatted header row")
        
        # Make shareable
        permission = {
            'type': 'anyone',
            'role': 'writer'
        }
        drive_service.permissions().create(
            fileId=spreadsheet_id,
            body=permission
        ).execute()
        
        url = f"https://docs.google.com/spreadsheets/d/{spreadsheet_id}/edit"
        # print(f"   Shareable URL: {share_url}")
        
        # Generate Excel export URL
        excel_export_url = f"https://docs.google.com/spreadsheets/d/{spreadsheet_id}/export?format=xlsx"
        
        return {
            'spreadsheet_id': spreadsheet_id,
            'url': url,
            'excel_export_url': excel_export_url,
            'title': title,
            'rows_written': rows_written,
            'markdown_parsed': markdown_parsed,
            'capabilities': {
                'view_online': url,
                'download_excel': excel_export_url,
                'download_csv': f"https://docs.google.com/spreadsheets/d/{spreadsheet_id}/export?format=csv",
                'download_pdf': f"https://docs.google.com/spreadsheets/d/{spreadsheet_id}/export?format=pdf"
            }
        }
        
    except Exception as e:
        # print(f"[ERROR] Failed to create Google Sheet: {e}")
        raise


def google_sheets_create_multiple(spreadsheets_config, _user_id=None, _injected_credentials=None, **kwargs):
    """
    Create multiple Google Sheets at once with optional markdown formatting (v3.0 enhanced)
    
    Args:
        spreadsheets_config (list): List of spreadsheet configs, each with:
            - title (str): Spreadsheet title
            - headers (list): Optional header row
            - data (list[list]): Optional 2D array of data
            - parse_markdown (bool): Optional, enable markdown (default: False)
            - auto_borders (bool): Optional, add borders (default: True)
            - auto_resize_columns (bool): Optional, auto-resize columns (v3.0)
        _user_id: User ID for credential injection
        _injected_credentials: Flag for credential injection
        
    Returns:
        dict: {
            'spreadsheets': [...],
            'total_created': int,
            'total_rows_written': int
        }
    """
    try:
        results = []
        total_rows = 0
        
        # print(f"[SHEET] Creating {len(spreadsheets_config)} Google Sheets...")
        
        for idx, config in enumerate(spreadsheets_config, 1):
            title = config.get('title', f'Spreadsheet {idx}')
            headers = config.get('headers')
            data = config.get('data')
            parse_markdown = config.get('parse_markdown', False)
            auto_borders = config.get('auto_borders', True)
            auto_resize_columns = config.get('auto_resize_columns', False)  # v3.0
            
            # print(f"   [{idx}/{len(spreadsheets_config)}] Creating: {title}")
            
            # Call google_sheets_create for each spreadsheet
            result = google_sheets_create(
                title=title,
                data=data,
                headers=headers,
                parse_markdown=parse_markdown,
                auto_borders=auto_borders,
                auto_resize_columns=auto_resize_columns,  # v3.0
                _user_id=_user_id,
                _injected_credentials=_injected_credentials
            )
            
            results.append(result)
            total_rows += result.get('rows_written', 0)
        
        # print(f"[OK] Successfully created {len(results)} spreadsheets ({total_rows} total rows)")
        
        return {
            'spreadsheets': results,
            'total_created': len(results),
            'total_rows_written': total_rows
        }
        
    except Exception as e:
        # print(f"[ERROR] Failed to create multiple sheets: {e}")
        raise


# ==================== READ/WRITE DATA ====================

def google_sheets_append_data(spreadsheet_id, data, sheet_name='Sheet1', _user_id=None, _injected_credentials=None, **kwargs):
    """
    Append data to existing Google Sheet
    
    Args:
        spreadsheet_id (str): Target spreadsheet ID
        data (list[list]): 2D array of data to append
        sheet_name (str): Sheet name (default: 'Sheet1')
        _user_id: User ID for credential injection
        _injected_credentials: OAuth credentials flag
        
    Returns:
        dict: {'rows_added': int, 'range_updated': str}
    """
    try:
        # Phase 5: route through the shared injector when user context is present
        sheets_service = _get_sheets_service(user_id=_user_id, injected_credentials=_injected_credentials)
        
        body = {'values': data}
        result = sheets_service.spreadsheets().values().append(
            spreadsheetId=spreadsheet_id,
            range=f'{sheet_name}!A1',
            valueInputOption='USER_ENTERED',
            body=body
        ).execute()
        
        rows_added = result.get('updates', {}).get('updatedRows', 0)
        range_updated = result.get('updates', {}).get('updatedRange', '')
        
        # print(f"[OK] Appended {rows_added} rows to {sheet_name}")
        
        return {
            'rows_added': rows_added,
            'range_updated': range_updated
        }
        
    except Exception as e:
        # print(f"[ERROR] Failed to append data: {e}")
        raise


def google_sheets_update_range(spreadsheet_id, range_name, data, mode='update', sheet_name=None, _user_id=None, _injected_credentials=None, **kwargs):
    """
    Update Google Sheets data with multiple modes.
    
    Args:
        spreadsheet_id: Spreadsheet ID
        range_name: A1 notation range (e.g., 'A1:C10' or 'Sheet1!A1:C10')
        data: 2D array of values to write [[row1], [row2], ...]
        mode: Update mode:
            - 'update': Overwrite specific range (default)
            - 'append': Add rows to end of existing data
            - 'clear': Clear range first, then write data
        sheet_name: Optional sheet name (if not in range_name)
        **kwargs: OAuth credentials
    
    Returns:
        dict with operation details
    """
    print(f"Updating spreadsheet {spreadsheet_id} with mode: {mode}")
    
    try:
        # Get credentials
        # Phase 5: route through the shared injector when user context is present
        sheets_service = _get_sheets_service(user_id=_user_id, injected_credentials=_injected_credentials)
        
        # Build full range if sheet_name provided
        if sheet_name and '!' not in range_name:
            full_range = f"{sheet_name}!{range_name}"
        else:
            full_range = range_name
        
        if mode == 'update':
            # Standard update - overwrite specific range
            body = {'values': data}
            result = sheets_service.spreadsheets().values().update(
                spreadsheetId=spreadsheet_id,
                range=full_range,
                valueInputOption='USER_ENTERED',
                body=body
            ).execute()
            
            updated_cells = result.get('updatedCells', 0)
            updated_rows = result.get('updatedRows', 0)
            updated_range = result.get('updatedRange', '')
            
            print(f"Updated {updated_cells} cells ({updated_rows} rows) in range {updated_range}")
            
            return {
                'success': True,
                'mode': 'update',
                'updated_cells': updated_cells,
                'updated_rows': updated_rows,
                'updated_range': updated_range
            }
            
        elif mode == 'append':
            # Append to end of existing data
            body = {'values': data}
            result = sheets_service.spreadsheets().values().append(
                spreadsheetId=spreadsheet_id,
                range=full_range,
                valueInputOption='USER_ENTERED',
                body=body
            ).execute()
            
            rows_added = result.get('updates', {}).get('updatedRows', 0)
            updated_range = result.get('updates', {}).get('updatedRange', '')
            
            print(f"Appended {rows_added} rows to end of data")
            
            return {
                'success': True,
                'mode': 'append',
                'rows_added': rows_added,
                'updated_range': updated_range
            }
            
        elif mode == 'clear':
            # Clear range first, then write new data
            # Step 1: Clear
            sheets_service.spreadsheets().values().clear(
                spreadsheetId=spreadsheet_id,
                range=full_range,
                body={}
            ).execute()
            
            # Step 2: Write new data
            body = {'values': data}
            result = sheets_service.spreadsheets().values().update(
                spreadsheetId=spreadsheet_id,
                range=full_range,
                valueInputOption='USER_ENTERED',
                body=body
            ).execute()
            
            updated_cells = result.get('updatedCells', 0)
            updated_rows = result.get('updatedRows', 0)
            updated_range = result.get('updatedRange', '')
            
            print(f"Cleared and wrote {updated_cells} cells ({updated_rows} rows)")
            
            return {
                'success': True,
                'mode': 'clear_and_update',
                'updated_cells': updated_cells,
                'updated_rows': updated_rows,
                'updated_range': updated_range
            }
            
        else:
            raise ValueError(f"Invalid mode: '{mode}'. Use 'update', 'append', or 'clear'")
        
    except Exception as e:
        print(f"Failed to update range: {e}")
        raise


def google_sheets_clear_range(spreadsheet_id, range_name, sheet_name=None, _user_id=None, _injected_credentials=None, **kwargs):
    """
    Clear all data in a specific range (delete content but keep formatting).
    
    Args:
        spreadsheet_id: Spreadsheet ID
        range_name: A1 notation range (e.g., 'A1:C10' or 'Sheet1!A1:C10')
        sheet_name: Optional sheet name (if not in range_name)
        **kwargs: OAuth credentials
    
    Returns:
        dict with success status and cleared_range
    """
    print(f"Clearing range {range_name} in spreadsheet {spreadsheet_id}")
    
    try:
        # Get credentials
        # Phase 5: route through the shared injector when user context is present
        sheets_service = _get_sheets_service(user_id=_user_id, injected_credentials=_injected_credentials)
        
        # Build full range if sheet_name provided
        if sheet_name and '!' not in range_name:
            full_range = f"{sheet_name}!{range_name}"
        else:
            full_range = range_name
        
        # Clear the range
        result = sheets_service.spreadsheets().values().clear(
            spreadsheetId=spreadsheet_id,
            range=full_range,
            body={}
        ).execute()
        
        cleared_range = result.get('clearedRange', '')
        
        print(f"Cleared range {cleared_range}")
        
        return {
            'success': True,
            'cleared_range': cleared_range
        }
        
    except Exception as e:
        print(f"Failed to clear range: {e}")
        raise


def google_sheets_read_data(spreadsheet_id, range_name='Sheet1!A1:Z1000', _user_id=None, _injected_credentials=None, **kwargs):
    """
    Read data from Google Sheet (LEGACY - use google_sheets_get_range instead)
    
    Args:
        spreadsheet_id (str): Source spreadsheet ID
        range_name (str): A1 notation range (e.g., 'Sheet1!A1:C10')
        _user_id: User ID for credential injection
        _injected_credentials: Flag for credential injection
        
    Returns:
        dict: {
            'values': list[list],
            'rows': int,
            'columns': int
        }
    """
    try:
        # Phase 5: route through the shared injector when user context is present
        sheets_service = _get_sheets_service(user_id=_user_id, injected_credentials=_injected_credentials)
        
        result = sheets_service.spreadsheets().values().get(
            spreadsheetId=spreadsheet_id,
            range=range_name
        ).execute()
        
        values = result.get('values', [])
        rows = len(values)
        cols = max(len(row) for row in values) if values else 0
        
        # print(f"[READ] Read {rows} rows x {cols} columns from {range_name}")
        
        return {
            'values': values,
            'rows': rows,
            'columns': cols
        }
        
    except Exception as e:
        # print(f"[ERROR] Failed to read data: {e}")
        raise


def google_sheets_get_range(spreadsheet_id, range='', format='summary', _user_id=None, _injected_credentials=None, **kwargs):
    """
    Get spreadsheet data with format control to prevent token overflow
    
    FORMAT OPTIONS:
    - 'summary' (DEFAULT): Returns title, sheet info, headers, first 3 rows preview (~500 tokens)
    - 'values': Returns raw cell values only, no formatting (~20K tokens for 100 rows)
    - 'markdown': Returns data as markdown table (~25K tokens for 100 rows)
    - 'full': Complete JSON with all formatting (LEGACY - NOT RECOMMENDED, ~150K tokens)
    
    Args:
        spreadsheet_id: Spreadsheet ID
        range: A1 notation (e.g., 'Sheet1!A1:Z100'). If empty, uses first sheet
        format: Output format ('summary', 'values', 'markdown', 'full')
        _user_id: User ID for OAuth credentials
        _injected_credentials: Flag for credential injection
    
    Returns:
        dict: Content in requested format
    """
    try:
        # Phase 5: route through the shared injector when user context is present
        sheets_service = _get_sheets_service(user_id=_user_id, injected_credentials=_injected_credentials)
        
        # Get spreadsheet metadata
        spreadsheet = sheets_service.spreadsheets().get(
            spreadsheetId=spreadsheet_id
        ).execute()
        
        title = spreadsheet.get('properties', {}).get('title', 'Untitled')
        sheets = spreadsheet.get('sheets', [])
        
        # Determine range to fetch
        if not range:
            # Use first sheet, all data
            if sheets:
                first_sheet = sheets[0].get('properties', {}).get('title', 'Sheet1')
                range = f"{first_sheet}!A1:Z1000"
            else:
                range = "Sheet1!A1:Z1000"
        
        # Get values
        result = sheets_service.spreadsheets().values().get(
            spreadsheetId=spreadsheet_id,
            range=range
        ).execute()
        
        values = result.get('values', [])
        rows = len(values)
        cols = max(len(row) for row in values) if values else 0
        
        # FORMAT: summary (DEFAULT - 500 tokens)
        if format == 'summary':
            headers = values[0] if values else []
            preview_rows = values[:3] if len(values) > 0 else []
            
            return {
                'success': True,
                'title': title,
                'spreadsheet_id': spreadsheet_id,
                'range': range,
                'row_count': rows,
                'column_count': cols,
                'headers': headers,
                'preview': preview_rows,
                'format': 'summary',
                'note': 'Showing first 3 rows. Use format="values" for all data or format="markdown" for formatted table.'
            }
        
        # FORMAT: values (20K tokens for 100 rows)
        elif format == 'values':
            return {
                'success': True,
                'spreadsheet_id': spreadsheet_id,
                'range': range,
                'values': values,
                'row_count': rows,
                'column_count': cols,
                'format': 'values'
            }
        
        # FORMAT: markdown (25K tokens for 100 rows)
        elif format == 'markdown':
            if not values:
                return {
                    'success': True,
                    'markdown': '(empty sheet)',
                    'format': 'markdown'
                }
            
            # Convert to markdown table
            markdown_lines = []
            
            # Headers (first row)
            if values:
                header_row = values[0]
                markdown_lines.append('| ' + ' | '.join(str(cell) for cell in header_row) + ' |')
                markdown_lines.append('|' + '|'.join(['---' for _ in header_row]) + '|')
            
            # Data rows
            for row in values[1:]:
                # Pad row to match header length
                padded_row = row + [''] * (len(header_row) - len(row))
                markdown_lines.append('| ' + ' | '.join(str(cell) for cell in padded_row) + ' |')
            
            markdown_content = '\n'.join(markdown_lines)
            
            return {
                'success': True,
                'spreadsheet_id': spreadsheet_id,
                'range': range,
                'markdown': markdown_content,
                'row_count': rows,
                'column_count': cols,
                'format': 'markdown',
                'note': 'Data converted to markdown table format'
            }
        
        # FORMAT: full (LEGACY - 150K+ tokens)
        elif format == 'full':
            return {
                'success': True,
                'spreadsheet': spreadsheet,
                'values': values,
                'format': 'full',
                'warning': 'Full format returns 150K+ tokens. Use format="summary" or "values" instead.'
            }
        
        else:
            raise ValueError(f"Invalid format: '{format}'. Use 'summary', 'values', 'markdown', or 'full'")
    
    except Exception as e:
        raise Exception(f"Failed to get spreadsheet range: {str(e)}")


def google_sheets_query_data(spreadsheet_id, range='', filters=None, _user_id=None, _injected_credentials=None, **kwargs):
    """
    Query/filter spreadsheet data by column values.
    
    Args:
        spreadsheet_id: The spreadsheet ID
        range: Range to query (e.g., 'Sheet1!A1:Z100')
        filters: List of filter conditions. Each filter is a dict with:
            - column: Column letter or index (e.g., 'A' or 0)
            - operator: '=', '!=', '>', '<', '>=', '<=', 'contains'
            - value: Value to compare against
        **kwargs: Optional OAuth credentials
    
    Returns:
        dict with:
        - filtered_rows: Rows matching all filter conditions
        - total_rows: Number of matching rows
        - filters_applied: List of filters that were applied
    """
    print(f"Querying data in spreadsheet {spreadsheet_id}, range: {range}")
    
    try:
        # Get service with OAuth or service account
        service = _get_sheets_service_with_oauth(_user_id, _injected_credentials)
        
        # Get the data
        result = service.spreadsheets().values().get(
            spreadsheetId=spreadsheet_id,
            range=range
        ).execute()
        
        values = result.get('values', [])
        
        if not values:
            print("No data found in range")
            return {
                'filtered_rows': [],
                'total_rows': 0,
                'filters_applied': filters or []
            }
        
        # If no filters, return all rows
        if not filters:
            return {
                'filtered_rows': values,
                'total_rows': len(values),
                'filters_applied': []
            }
        
        # Apply filters
        filtered_rows = []
        
        for row in values:
            matches_all = True
            
            for filter_cond in filters:
                column = filter_cond.get('column')
                operator = filter_cond.get('operator')
                filter_value = filter_cond.get('value')
                
                # Convert column letter to index if needed
                if isinstance(column, str):
                    column_index = ord(column.upper()) - ord('A')
                else:
                    column_index = column
                
                # Check if row has this column
                if column_index >= len(row):
                    matches_all = False
                    break
                
                cell_value = row[column_index]
                
                # Apply operator
                try:
                    if operator == '=':
                        if str(cell_value) != str(filter_value):
                            matches_all = False
                            break
                    elif operator == '!=':
                        if str(cell_value) == str(filter_value):
                            matches_all = False
                            break
                    elif operator == 'contains':
                        if str(filter_value).lower() not in str(cell_value).lower():
                            matches_all = False
                            break
                    elif operator in ['>', '<', '>=', '<=']:
                        # Try numeric comparison
                        try:
                            cell_num = float(cell_value)
                            filter_num = float(filter_value)
                            
                            if operator == '>' and not cell_num > filter_num:
                                matches_all = False
                                break
                            elif operator == '<' and not cell_num < filter_num:
                                matches_all = False
                                break
                            elif operator == '>=' and not cell_num >= filter_num:
                                matches_all = False
                                break
                            elif operator == '<=' and not cell_num <= filter_num:
                                matches_all = False
                                break
                        except (ValueError, TypeError):
                            # Can't compare non-numeric values
                            matches_all = False
                            break
                except Exception as e:
                    print(f"Filter comparison error: {e}")
                    matches_all = False
                    break
            
            if matches_all:
                filtered_rows.append(row)
        
        print(f"Found {len(filtered_rows)} rows matching filters")
        
        return {
            'filtered_rows': filtered_rows,
            'total_rows': len(filtered_rows),
            'filters_applied': filters
        }
    
    except Exception as e:
        print(f"Failed to query data: {e}")
        raise


def google_sheets_get_summary(spreadsheet_id, range='', group_by_column=None, aggregations=None, _user_id=None, _injected_credentials=None, **kwargs):
    """
    Get summary statistics from spreadsheet data (aggregate/group by column).
    
    Args:
        spreadsheet_id: The spreadsheet ID
        range: Range to summarize (e.g., 'Sheet1!A1:Z100')
        group_by_column: Column to group by (letter or index, e.g., 'A' or 0)
        aggregations: List of aggregation configs. Each is a dict with:
            - column: Column to aggregate (letter or index)
            - function: 'count', 'sum', 'average', 'min', 'max'
        **kwargs: Optional OAuth credentials
    
    Returns:
        dict with:
        - summary: List of summary rows with grouped values and aggregations
        - group_by_column: Column used for grouping
        - aggregations_applied: List of aggregation functions applied
    """
    print(f"Getting summary for spreadsheet {spreadsheet_id}, range: {range}")
    
    try:
        # Get service with OAuth or service account
        service = _get_sheets_service_with_oauth(_user_id, _injected_credentials)
        
        # Get the data
        result = service.spreadsheets().values().get(
            spreadsheetId=spreadsheet_id,
            range=range
        ).execute()
        
        values = result.get('values', [])
        
        if not values:
            print("No data found in range")
            return {
                'summary': [],
                'group_by_column': group_by_column,
                'aggregations_applied': aggregations or []
            }
        
        # If no group by, calculate aggregations for all data
        if group_by_column is None:
            summary_row = {'group': 'ALL'}
            
            for agg in (aggregations or []):
                agg_column = agg.get('column')
                agg_function = agg.get('function')
                
                # Convert column letter to index if needed
                if isinstance(agg_column, str):
                    col_index = ord(agg_column.upper()) - ord('A')
                else:
                    col_index = agg_column
                
                # Extract numeric values from column
                numeric_values = []
                for row in values:
                    if col_index < len(row):
                        try:
                            numeric_values.append(float(row[col_index]))
                        except (ValueError, TypeError):
                            pass
                
                # Calculate aggregation
                if agg_function == 'count':
                    summary_row[f'{agg_column}_{agg_function}'] = len(numeric_values)
                elif agg_function == 'sum' and numeric_values:
                    summary_row[f'{agg_column}_{agg_function}'] = sum(numeric_values)
                elif agg_function == 'average' and numeric_values:
                    summary_row[f'{agg_column}_{agg_function}'] = sum(numeric_values) / len(numeric_values)
                elif agg_function == 'min' and numeric_values:
                    summary_row[f'{agg_column}_{agg_function}'] = min(numeric_values)
                elif agg_function == 'max' and numeric_values:
                    summary_row[f'{agg_column}_{agg_function}'] = max(numeric_values)
            
            return {
                'summary': [summary_row],
                'group_by_column': None,
                'aggregations_applied': aggregations or []
            }
        
        # Group by column
        # Convert column letter to index if needed
        if isinstance(group_by_column, str):
            group_col_index = ord(group_by_column.upper()) - ord('A')
        else:
            group_col_index = group_by_column
        
        # Group rows by the group_by_column value
        groups = {}
        
        for row in values:
            if group_col_index >= len(row):
                continue
            
            group_value = row[group_col_index]
            
            if group_value not in groups:
                groups[group_value] = []
            
            groups[group_value].append(row)
        
        # Calculate aggregations for each group
        summary = []
        
        for group_value, group_rows in groups.items():
            summary_row = {'group': group_value}
            
            for agg in (aggregations or []):
                agg_column = agg.get('column')
                agg_function = agg.get('function')
                
                # Convert column letter to index if needed
                if isinstance(agg_column, str):
                    col_index = ord(agg_column.upper()) - ord('A')
                else:
                    col_index = agg_column
                
                # Extract numeric values from column in this group
                numeric_values = []
                for row in group_rows:
                    if col_index < len(row):
                        try:
                            numeric_values.append(float(row[col_index]))
                        except (ValueError, TypeError):
                            pass
                
                # Calculate aggregation
                if agg_function == 'count':
                    summary_row[f'{agg_column}_{agg_function}'] = len(numeric_values)
                elif agg_function == 'sum' and numeric_values:
                    summary_row[f'{agg_column}_{agg_function}'] = sum(numeric_values)
                elif agg_function == 'average' and numeric_values:
                    summary_row[f'{agg_column}_{agg_function}'] = sum(numeric_values) / len(numeric_values)
                elif agg_function == 'min' and numeric_values:
                    summary_row[f'{agg_column}_{agg_function}'] = min(numeric_values)
                elif agg_function == 'max' and numeric_values:
                    summary_row[f'{agg_column}_{agg_function}'] = max(numeric_values)
            
            summary.append(summary_row)
        
        print(f"Generated summary with {len(summary)} groups")
        
        return {
            'summary': summary,
            'group_by_column': group_by_column,
            'aggregations_applied': aggregations or []
        }
    
    except Exception as e:
        print(f"Failed to get summary: {e}")
        raise


# ==================== ALIASES (Short Names) ====================
# These aliases map schema names to implementation functions

def gsheets_create(title, data=None, headers=None, parse_markdown=False, **kwargs):
    """
    ⚠️ BASIC METHOD: Create simple spreadsheet (NO markdown support by default)
    
    Use this for basic spreadsheets without special formatting.
    For markdown formatting, set parse_markdown=True.
    
    Args:
        title (str): Spreadsheet title
        data (list, optional): 2D array [[row1], [row2], ...]
        headers (list, optional): Header row
        parse_markdown (bool, optional): Enable markdown formatting (default: False)
        **kwargs: _user_id, _injected_credentials for OAuth
    
    Returns:
        dict: {spreadsheet_id, url, title, rows_written}
        
    Note: For markdown formatting, use google_sheets_create with parse_markdown=True
    """
    return google_sheets_create(title=title, data=data, headers=headers, parse_markdown=parse_markdown, **kwargs)


def gsheets_create_complete_spreadsheet(title, data, headers=None, sheet_name='Sheet1', formatting=None, shareable=True, parse_markdown=False, **kwargs):
    """
    ⭐ PREFERRED METHOD: Create complete spreadsheet with data and formatting in ONE operation
    ✨ SUPPORTS MARKDOWN: Set parse_markdown=True to enable markdown formatting
    
    This is the MOST EFFICIENT method - creates spreadsheet with all formatting in one call.
    
    Args:
        title (str): Spreadsheet title
        data (list): 2D array of data [[row1], [row2], ...]
        headers (list, optional): Header row (will be bolded and frozen)
        sheet_name (str, optional): Name for first sheet (default: 'Sheet1')
        formatting (dict, optional): {bold_headers: bool, freeze_header: bool, auto_resize: bool}
        shareable (bool, optional): Make accessible to anyone with link (default: True)
        parse_markdown (bool, optional): Enable markdown formatting (default: False)
        **kwargs: _user_id, _injected_credentials for OAuth
    
    Markdown Support (when parse_markdown=True):
        - **bold** → Bold text
        - *italic* → Italic text  
        - # Header → Bold, larger font (18pt), gray background
        - [RED]text[/RED] → Red text
        - [GREEN]text[/GREEN] → Green text
        - [BLUE]text[/BLUE] → Blue text
        - [YELLOW]text[/YELLOW] → Yellow text
        - [ORANGE]text[/ORANGE] → Orange text
        - [PURPLE]text[/PURPLE] → Purple text
        - [GRAY]text[/GRAY] → Gray text
        - Automatic borders on all cells
    
    Returns:
        dict: {spreadsheet_id, url, title, rows_added, columns, markdown_parsed}
        
    Example:
        # Without markdown (plain text)
        result = gsheets_create_complete_spreadsheet(
            title="Sales Report",
            headers=["Product", "Revenue"],
            data=[["Widget A", "$100"], ["Widget B", "$200"]]
        )
        
        # With markdown formatting
        result = gsheets_create_complete_spreadsheet(
            title="Sales Report",
            headers=["# Product", "**Revenue**"],
            data=[["**Widget A**", "[GREEN]$100[/GREEN]"], 
                  ["Widget B", "[RED]$50[/RED]"]],
            parse_markdown=True  # ← ENABLE MARKDOWN
        )
    """
    # Use google_sheets_create which already handles markdown
    return google_sheets_create(
        title=title,
        data=data,
        headers=headers,
        parse_markdown=parse_markdown,
        **kwargs
    )


def gsheets_ai_generate_table(prompt, title=None, shareable=True, ai_model='gpt-4', **kwargs):
    """
    ⭐ AI-POWERED: Generate data table from natural language description
    
    Args:
        prompt (str): Natural language description of table to create
        title (str, optional): Spreadsheet title (AI generates if not provided)
        shareable (bool, optional): Make accessible to anyone with link
        ai_model (str, optional): OpenAI model to use
        **kwargs: _user_id, _injected_credentials for OAuth
    
    Returns:
        dict: {spreadsheet_id, url, title, rows_generated, ai_details}
    """
    import os
    import json
    
    # Check for OpenAI API key
    openai_key = os.getenv('OPENAI_API_KEY')
    if not openai_key:
        raise Exception("OPENAI_API_KEY environment variable required for AI table generation")
    
    try:
        from openai import OpenAI
        client = OpenAI(api_key=openai_key)
    except ImportError:
        raise Exception("openai package required: pip install openai")
    
    # Generate table structure and data using AI
    system_prompt = """You are a data table generator. Given a user's description, generate:
1. A title for the spreadsheet (if not provided)
2. Column headers (clear, concise)
3. Realistic sample data rows (at least 10 rows unless specified otherwise)

Return JSON format:
{
  "title": "Spreadsheet Title",
  "headers": ["Column1", "Column2", ...],
  "data": [
    ["value1", "value2", ...],
    ["value1", "value2", ...],
    ...
  ]
}"""
    
    response = client.chat.completions.create(
        model=ai_model,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": f"Generate table: {prompt}"}
        ],
        response_format={"type": "json_object"}
    )
    
    result = json.loads(response.choices[0].message.content)
    
    # Use provided title or AI-generated title
    final_title = title or result.get('title', 'AI Generated Table')
    headers = result.get('headers', [])
    data = result.get('data', [])
    
    # Create spreadsheet with AI-generated data
    sheet_result = google_sheets_create(
        title=final_title,
        headers=headers,
        data=data,
        **kwargs
    )
    
    # Add AI generation details
    sheet_result['rows_generated'] = len(data)
    sheet_result['ai_model'] = ai_model
    sheet_result['ai_prompt'] = prompt
    
    return sheet_result


def gsheets_bulk_create_multiple(spreadsheets_configs, shareable=True, **kwargs):
    """
    ⭐ BULK OPERATION: Create multiple spreadsheets at once
    
    Args:
        spreadsheets_configs (list): List of configs, each with:
            - title (str): Spreadsheet title
            - headers (list, optional): Header row
            - data (list): 2D array of data
            - sheet_name (str, optional): Sheet name
        shareable (bool, optional): Make all spreadsheets shareable
        **kwargs: _user_id, _injected_credentials for OAuth
    
    Returns:
        dict: {created_count, spreadsheets: [{spreadsheet_id, url, title}, ...]}
    """
    results = []
    
    for config in spreadsheets_configs:
        try:
            result = google_sheets_create(
                title=config.get('title', 'Untitled'),
                headers=config.get('headers'),
                data=config.get('data', []),
                **kwargs
            )
            results.append(result)
        except Exception as e:
            results.append({
                'title': config.get('title', 'Unknown'),
                'error': str(e),
                'success': False
            })
    
    return {
        'created_count': len([r for r in results if r.get('spreadsheet_id')]),
        'total_attempted': len(spreadsheets_configs),
        'spreadsheets': results
    }


def gsheets_write(spreadsheet_id, data, sheet_name='Sheet1', **kwargs):
    """Alias for google_sheets_append_data"""
    return google_sheets_append_data(spreadsheet_id=spreadsheet_id, data=data, sheet_name=sheet_name, **kwargs)


def gsheets_read(spreadsheet_id, range_name='Sheet1!A1:Z1000', **kwargs):
    """Alias for google_sheets_read_data"""
    return google_sheets_read_data(spreadsheet_id=spreadsheet_id, range_name=range_name, **kwargs)


def gsheets_append(spreadsheet_id, data, sheet_name='Sheet1', **kwargs):
    """Alias for google_sheets_append_data"""
    return google_sheets_append_data(spreadsheet_id=spreadsheet_id, data=data, sheet_name=sheet_name, **kwargs)


# ==================== ADDITIONAL FUNCTIONS ====================

def google_sheets_format_cells(spreadsheet_id, range_name, format_spec, **kwargs):
    """
    Apply formatting to cells in a Google Sheet
    
    Args:
        spreadsheet_id (str): Target spreadsheet ID
        range_name (str): A1 notation range (e.g., 'Sheet1!A1:C1')
        format_spec (dict): Formatting specification with:
            - bold (bool): Make text bold
            - italic (bool): Make text italic
            - fontSize (int): Font size in points
            - textColor (dict): RGB color {'red': 0-1, 'green': 0-1, 'blue': 0-1}
            - backgroundColor (dict): RGB background color
            - horizontalAlignment (str): 'LEFT', 'CENTER', 'RIGHT'
            
    Returns:
        dict: {'success': bool, 'range_updated': str}
    """
    try:
        sheets_service = _get_sheets_service(**kwargs)
        
        # Parse range to get sheetId
        if '!' in range_name:
            sheet_name, cell_range = range_name.split('!')
        else:
            sheet_name = 'Sheet1'
            cell_range = range_name
        
        # Get sheet ID by name
        spreadsheet = sheets_service.spreadsheets().get(
            spreadsheetId=spreadsheet_id
        ).execute()
        
        sheet_id = 0
        for sheet in spreadsheet.get('sheets', []):
            if sheet['properties']['title'] == sheet_name:
                sheet_id = sheet['properties']['sheetId']
                break
        
        # Build format request
        requests = [{
            'repeatCell': {
                'range': {
                    'sheetId': sheet_id,
                    'rowIndex': int(cell_range[1]) - 1 if len(cell_range) > 1 else 0
                },
                'cell': {
                    'userEnteredFormat': format_spec
                },
                'fields': 'userEnteredFormat'
            }
        }]
        
        sheets_service.spreadsheets().batchUpdate(
            spreadsheetId=spreadsheet_id,
            body={'requests': requests}
        ).execute()
        
        # print(f"[OK] Applied formatting to {range_name}")
        
        return {
            'success': True,
            'range_updated': range_name
        }
        
    except Exception as e:
        # print(f"[ERROR] Failed to format cells: {e}")
        raise


def google_sheets_delete(spreadsheet_id, **kwargs):
    """
    Delete a Google Sheet
    
    Args:
        spreadsheet_id (str): Spreadsheet ID to delete
        
    Returns:
        dict: {'success': bool, 'deleted_id': str}
    """
    try:
        drive_service = build_drive_service(**kwargs)
        
        drive_service.files().delete(fileId=spreadsheet_id).execute()
        
        # print(f"[OK] Deleted spreadsheet: {spreadsheet_id}")
        
        return {
            'success': True,
            'deleted_id': spreadsheet_id
        }
        
    except Exception as e:
        # print(f"[ERROR] Failed to delete spreadsheet: {e}")
        raise


# ==================== NEW ENHANCEMENT TOOLS (Dec 2025) ====================

def google_sheets_update_cell(spreadsheet_id, cell, value, value_type='auto', 
                               sheet_name=None, _user_id=None, _injected_credentials=None, **kwargs):
    """
    Update a single cell efficiently without reading entire range.
    
    95% faster than update_range for single-cell edits.
    
    Args:
        spreadsheet_id (str): Target spreadsheet ID
        cell (str): Cell reference in A1 notation (e.g., 'A5', 'Sheet1!B7')
        value (Any): Value to set (string, number, boolean, or formula)
        value_type (str): Type handling:
            - 'auto': Detect type automatically (default)
            - 'string': Force as text
            - 'number': Force as number
            - 'formula': Treat as Excel formula (must start with =)
            - 'boolean': Force as boolean
        sheet_name (str): Optional sheet name if not in cell reference
        
    Returns:
        dict: {
            'success': bool,
            'updated_cell': str,
            'value_set': any,
            'value_type': str
        }
    """
    print(f"Updating cell {cell} with value: {value}")
    
    try:
        # Get credentials
        # Phase 5: route through the shared injector when user context is present
        sheets_service = _get_sheets_service(user_id=_user_id, injected_credentials=_injected_credentials)
        
        # Build full cell reference
        if sheet_name and '!' not in cell:
            full_cell = f"{sheet_name}!{cell}"
        else:
            full_cell = cell
        
        # Determine value input option based on value_type
        if value_type == 'formula' or (value_type == 'auto' and isinstance(value, str) and value.startswith('=')):
            # Formula - use USER_ENTERED to parse formulas
            input_option = 'USER_ENTERED'
            final_value = value
            detected_type = 'formula'
        elif value_type == 'number' or (value_type == 'auto' and isinstance(value, (int, float))):
            input_option = 'USER_ENTERED'
            final_value = value
            detected_type = 'number'
        elif value_type == 'boolean' or (value_type == 'auto' and isinstance(value, bool)):
            input_option = 'USER_ENTERED'
            final_value = value
            detected_type = 'boolean'
        else:
            # String or auto-detected as string
            input_option = 'RAW'  # Prevent formula interpretation
            final_value = str(value)
            detected_type = 'string'
        
        # Update single cell
        body = {
            'values': [[final_value]]
        }
        
        result = sheets_service.spreadsheets().values().update(
            spreadsheetId=spreadsheet_id,
            range=full_cell,
            valueInputOption=input_option,
            body=body
        ).execute()
        
        updated_cells = result.get('updatedCells', 0)
        updated_range = result.get('updatedRange', '')
        
        print(f"✅ Updated cell {updated_range} ({detected_type})")
        
        return {
            'success': True,
            'updated_cell': updated_range,
            'value_set': final_value,
            'value_type': detected_type,
            'updated_cells': updated_cells
        }
        
    except Exception as e:
        print(f"❌ Failed to update cell: {e}")
        raise


def google_sheets_add_formula(spreadsheet_id, range, formula, parse_natural=True,
                               sheet_name=None, _user_id=None, _injected_credentials=None, **kwargs):
    """
    Add Excel-style formulas to cells with optional natural language parsing.
    
    Args:
        spreadsheet_id (str): Target spreadsheet ID
        range (str): A1 notation range (e.g., 'D2:D10' for column, 'Summary!A1' for single cell)
        formula (str): Formula to apply. Can be:
            - Excel syntax: "=SUM(A2:C2)"
            - Natural language: "sum columns A through C"
            - Natural language: "average of column B"
        parse_natural (bool): If True, convert natural language to Excel formulas
        sheet_name (str): Optional sheet name if not in range
        
    Returns:
        dict: {
            'success': bool,
            'formulas_added': int,
            'range_updated': str,
            'parsed_formula': str  # Final Excel formula used
        }
    """
    print(f"Adding formula to range {range}: {formula}")
    
    try:
        # Get credentials
        # Phase 5: route through the shared injector when user context is present
        sheets_service = _get_sheets_service(user_id=_user_id, injected_credentials=_injected_credentials)
        
        # Build full range
        if sheet_name and '!' not in range:
            full_range = f"{sheet_name}!{range}"
        else:
            full_range = range
        
        # Parse natural language to Excel formula if requested
        parsed_formula = formula
        if parse_natural and not formula.startswith('='):
            # Simple natural language parsing
            formula_lower = formula.lower()
            
            # SUM patterns
            if 'sum' in formula_lower:
                if 'column' in formula_lower or 'col' in formula_lower:
                    # Extract column references
                    import re
                    cols = re.findall(r'\b([A-Z])\b', formula.upper())
                    if len(cols) == 1:
                        parsed_formula = f"=SUM({cols[0]}:{cols[0]})"
                    elif len(cols) > 1:
                        parsed_formula = f"=SUM({cols[0]}:{cols[-1]})"
                elif 'row' in formula_lower:
                    # Row sum
                    nums = re.findall(r'\d+', formula)
                    if nums:
                        parsed_formula = f"=SUM({nums[0]}:{nums[0]})"
            
            # AVERAGE patterns
            elif 'average' in formula_lower or 'mean' in formula_lower:
                cols = re.findall(r'\b([A-Z])\b', formula.upper())
                if len(cols) == 1:
                    parsed_formula = f"=AVERAGE({cols[0]}:{cols[0]})"
                elif len(cols) > 1:
                    parsed_formula = f"=AVERAGE({cols[0]}:{cols[-1]})"
            
            # COUNT patterns
            elif 'count' in formula_lower:
                cols = re.findall(r'\b([A-Z])\b', formula.upper())
                if cols:
                    parsed_formula = f"=COUNT({cols[0]}:{cols[0]})"
            
            # MULTIPLY patterns
            elif 'multiply' in formula_lower or 'times' in formula_lower or '*' in formula:
                cols = re.findall(r'\b([A-Z])\b', formula.upper())
                if len(cols) >= 2:
                    parsed_formula = f"={cols[0]}*{cols[1]}"
            
            # If still no = sign, assume it's a direct formula
            if not parsed_formula.startswith('='):
                parsed_formula = f"={parsed_formula}"
        
        # Ensure formula starts with =
        if not parsed_formula.startswith('='):
            parsed_formula = f"={parsed_formula}"
        
        print(f"📝 Parsed formula: {parsed_formula}")
        
        # Determine if range is single cell or multiple cells
        # For single cell, apply formula directly
        # For range, apply formula with relative references
        
        # Get range dimensions
        result = sheets_service.spreadsheets().values().get(
            spreadsheetId=spreadsheet_id,
            range=full_range
        ).execute()
        
        existing_values = result.get('values', [[]])
        num_rows = len(existing_values) if existing_values else 1
        
        # Build formula list
        formulas = []
        if num_rows == 1:
            # Single row - one formula
            formulas = [[parsed_formula]]
        else:
            # Multiple rows - replicate formula for each row
            # (Sheets will auto-adjust row references)
            for _ in range(num_rows):
                formulas.append([parsed_formula])
        
        # Update with formulas
        body = {'values': formulas}
        update_result = sheets_service.spreadsheets().values().update(
            spreadsheetId=spreadsheet_id,
            range=full_range,
            valueInputOption='USER_ENTERED',  # Parse formulas
            body=body
        ).execute()
        
        updated_cells = update_result.get('updatedCells', 0)
        updated_range = update_result.get('updatedRange', '')
        
        print(f"✅ Added {updated_cells} formulas to {updated_range}")
        
        return {
            'success': True,
            'formulas_added': updated_cells,
            'range_updated': updated_range,
            'parsed_formula': parsed_formula,
            'original_input': formula
        }
        
    except Exception as e:
        print(f"❌ Failed to add formula: {e}")
        raise


def google_sheets_manage_sheets(spreadsheet_id, action, sheet_name=None, new_name=None,
                                 position=None, sheet_id=None, _user_id=None, _injected_credentials=None, **kwargs):
    """
    Manage sheets within a spreadsheet: add, delete, rename, reorder, duplicate.
    
    Args:
        spreadsheet_id (str): Target spreadsheet ID
        action (str): Operation to perform:
            - 'add': Create new sheet
            - 'delete': Remove sheet
            - 'rename': Change sheet name
            - 'duplicate': Copy sheet
            - 'reorder': Move sheet position
        sheet_name (str): Name of sheet to operate on (for delete/rename/duplicate)
        new_name (str): New name for sheet (for rename/add/duplicate)
        position (int): Sheet position (0-indexed, for add/reorder)
        sheet_id (int): Sheet ID (alternative to sheet_name)
        
    Returns:
        dict: {
            'success': bool,
            'action': str,
            'sheet_id': int,
            'sheet_name': str
        }
    """
    print(f"Managing sheets: {action} operation on '{sheet_name}'")
    
    try:
        # Get credentials
        # Phase 5: route through the shared injector when user context is present
        sheets_service = _get_sheets_service(user_id=_user_id, injected_credentials=_injected_credentials)
        
        # Get spreadsheet metadata to find sheet IDs
        spreadsheet = sheets_service.spreadsheets().get(
            spreadsheetId=spreadsheet_id
        ).execute()
        
        sheets = spreadsheet.get('sheets', [])
        
        # Find target sheet ID if name provided
        target_sheet_id = sheet_id
        if sheet_name and not target_sheet_id:
            for sheet in sheets:
                if sheet['properties']['title'] == sheet_name:
                    target_sheet_id = sheet['properties']['sheetId']
                    break
        
        # Build request based on action
        request = None
        result_sheet_id = None
        result_sheet_name = None
        
        if action == 'add':
            # Add new sheet
            add_sheet_name = new_name or f"Sheet{len(sheets) + 1}"
            request = {
                'addSheet': {
                    'properties': {
                        'title': add_sheet_name,
                        'index': position if position is not None else len(sheets)
                    }
                }
            }
            
        elif action == 'delete':
            # Delete sheet
            if not target_sheet_id:
                raise ValueError(f"Sheet '{sheet_name}' not found")
            request = {
                'deleteSheet': {
                    'sheetId': target_sheet_id
                }
            }
            result_sheet_id = target_sheet_id
            result_sheet_name = sheet_name
            
        elif action == 'rename':
            # Rename sheet
            if not target_sheet_id:
                raise ValueError(f"Sheet '{sheet_name}' not found")
            if not new_name:
                raise ValueError("new_name required for rename action")
            request = {
                'updateSheetProperties': {
                    'properties': {
                        'sheetId': target_sheet_id,
                        'title': new_name
                    },
                    'fields': 'title'
                }
            }
            result_sheet_id = target_sheet_id
            result_sheet_name = new_name
            
        elif action == 'duplicate':
            # Duplicate sheet
            if not target_sheet_id:
                raise ValueError(f"Sheet '{sheet_name}' not found")
            dup_name = new_name or f"Copy of {sheet_name}"
            request = {
                'duplicateSheet': {
                    'sourceSheetId': target_sheet_id,
                    'insertSheetIndex': position if position is not None else len(sheets),
                    'newSheetName': dup_name
                }
            }
            result_sheet_name = dup_name
            
        elif action == 'reorder':
            # Move sheet to different position
            if not target_sheet_id:
                raise ValueError(f"Sheet '{sheet_name}' not found")
            if position is None:
                raise ValueError("position required for reorder action")
            request = {
                'updateSheetProperties': {
                    'properties': {
                        'sheetId': target_sheet_id,
                        'index': position
                    },
                    'fields': 'index'
                }
            }
            result_sheet_id = target_sheet_id
            result_sheet_name = sheet_name
            
        else:
            raise ValueError(f"Invalid action: '{action}'. Use: add, delete, rename, duplicate, reorder")
        
        # Execute request
        response = sheets_service.spreadsheets().batchUpdate(
            spreadsheetId=spreadsheet_id,
            body={'requests': [request]}
        ).execute()
        
        # Extract sheet ID from response if add/duplicate
        if action == 'add':
            result_sheet_id = response['replies'][0]['addSheet']['properties']['sheetId']
            result_sheet_name = response['replies'][0]['addSheet']['properties']['title']
        elif action == 'duplicate':
            result_sheet_id = response['replies'][0]['duplicateSheet']['properties']['sheetId']
        
        print(f"✅ Sheet {action} completed: {result_sheet_name} (ID: {result_sheet_id})")
        
        return {
            'success': True,
            'action': action,
            'sheet_id': result_sheet_id,
            'sheet_name': result_sheet_name,
            'spreadsheet_id': spreadsheet_id
        }
        
    except Exception as e:
        print(f"❌ Failed to {action} sheet: {e}")
        raise


def google_sheets_insert_delete_dimensions(spreadsheet_id, dimension, action, start_index,
                                             end_index=None, count=1, sheet_name='Sheet1',
                                             _user_id=None, _injected_credentials=None, **kwargs):
    """
    Insert or delete rows/columns with shift operations.
    
    Args:
        spreadsheet_id (str): Target spreadsheet ID
        dimension (str): 'ROWS' or 'COLUMNS'
        action (str): 'insert' or 'delete'
        start_index (int): Starting position (0-indexed)
        end_index (int): Ending position (for delete, exclusive). If None, uses start_index + count
        count (int): Number of rows/columns (for insert, default: 1)
        sheet_name (str): Sheet name (default: 'Sheet1')
        
    Returns:
        dict: {
            'success': bool,
            'action': str,
            'dimension': str,
            'start_index': int,
            'count': int
        }
    """
    print(f"{action.title()} {count} {dimension.lower()} starting at index {start_index}")
    
    try:
        # Get credentials
        # Phase 5: route through the shared injector when user context is present
        sheets_service = _get_sheets_service(user_id=_user_id, injected_credentials=_injected_credentials)
        
        # Get sheet ID
        spreadsheet = sheets_service.spreadsheets().get(
            spreadsheetId=spreadsheet_id
        ).execute()
        
        sheet_id = 0
        for sheet in spreadsheet.get('sheets', []):
            if sheet['properties']['title'] == sheet_name:
                sheet_id = sheet['properties']['sheetId']
                break
        
        # Build request
        if action == 'insert':
            # Insert dimension
            request = {
                'insertDimension': {
                    'range': {
                        'sheetId': sheet_id,
                        'dimension': dimension,
                        'startIndex': start_index,
                        'endIndex': start_index + count
                    }
                }
            }
            affected_count = count
            
        elif action == 'delete':
            # Delete dimension
            if end_index is None:
                end_index = start_index + count
            
            request = {
                'deleteDimension': {
                    'range': {
                        'sheetId': sheet_id,
                        'dimension': dimension,
                        'startIndex': start_index,
                        'endIndex': end_index
                    }
                }
            }
            affected_count = end_index - start_index
            
        else:
            raise ValueError(f"Invalid action: '{action}'. Use 'insert' or 'delete'")
        
        # Execute request
        sheets_service.spreadsheets().batchUpdate(
            spreadsheetId=spreadsheet_id,
            body={'requests': [request]}
        ).execute()
        
        print(f"✅ {action.title()}ed {affected_count} {dimension.lower()}")
        
        return {
            'success': True,
            'action': action,
            'dimension': dimension,
            'start_index': start_index,
            'end_index': end_index if action == 'delete' else start_index + count,
            'count': affected_count,
            'sheet_name': sheet_name
        }
        
    except Exception as e:
        print(f"❌ Failed to {action} {dimension.lower()}: {e}")
        raise


def google_sheets_batch_update_cells(spreadsheet_id, updates, _user_id=None, _injected_credentials=None, **kwargs):
    """
    Update multiple non-contiguous cells efficiently in one API call.
    
    Perfect for scattered updates across different cells/sheets.
    
    Args:
        spreadsheet_id (str): Target spreadsheet ID
        updates (list): List of cell updates, each with:
            - cell (str): Cell reference (e.g., 'A1', 'Sheet1!B5')
            - value (any): Value to set
            - value_type (str): Optional, 'auto'/'string'/'number'/'formula'/'boolean'
        
    Example:
        updates = [
            {"cell": "A1", "value": "Updated"},
            {"cell": "Summary!B5", "value": "=SUM(A1:A4)", "value_type": "formula"},
            {"cell": "Data!C3", "value": 125}
        ]
        
    Returns:
        dict: {
            'success': bool,
            'cells_updated': int,
            'updates_applied': list
        }
    """
    print(f"Batch updating {len(updates)} cells")
    
    try:
        # Get credentials
        # Phase 5: route through the shared injector when user context is present
        sheets_service = _get_sheets_service(user_id=_user_id, injected_credentials=_injected_credentials)
        
        # Build batch update data
        data = []
        results = []
        
        for update in updates:
            cell = update.get('cell')
            value = update.get('value')
            value_type = update.get('value_type', 'auto')
            
            # Determine value input option
            if value_type == 'formula' or (value_type == 'auto' and isinstance(value, str) and value.startswith('=')):
                input_option = 'USER_ENTERED'
                detected_type = 'formula'
            elif value_type == 'number' or (value_type == 'auto' and isinstance(value, (int, float))):
                input_option = 'USER_ENTERED'
                detected_type = 'number'
            else:
                input_option = 'RAW'
                detected_type = 'string'
            
            data.append({
                'range': cell,
                'values': [[value]]
            })
            
            results.append({
                'cell': cell,
                'value': value,
                'type': detected_type
            })
        
        # Execute batch update
        body = {
            'valueInputOption': 'USER_ENTERED',  # Parse formulas
            'data': data
        }
        
        response = sheets_service.spreadsheets().values().batchUpdate(
            spreadsheetId=spreadsheet_id,
            body=body
        ).execute()
        
        total_updated = response.get('totalUpdatedCells', 0)
        
        print(f"✅ Updated {total_updated} cells in batch")
        
        return {
            'success': True,
            'cells_updated': total_updated,
            'updates_applied': results,
            'response': response
        }
        
    except Exception as e:
        print(f"❌ Failed to batch update cells: {e}")
        raise


def google_sheets_smart_builder(
    # MODE 1: CREATE multi-sheet spreadsheet
    spreadsheet_name=None,
    sheets=None,
    
    # MODE 2: UPDATE existing spreadsheet
    spreadsheet_id=None,
    operations=None,
    
    # MODE 3: LEGACY simple creation
    title=None,
    data=None,
    headers=None,
    parse_markdown=False,
    
    # Common parameters
    _user_id=None,
    _injected_credentials=None,
    **kwargs
):
    """
    🎯 COMPREHENSIVE SMART BUILDER - Create multi-sheet spreadsheets or update existing ones.
    
    ═══════════════════════════════════════════════════════════════════
    THREE MODES OF OPERATION
    ═══════════════════════════════════════════════════════════════════
    
    MODE 1: CREATE - Build multi-sheet spreadsheet from scratch
    MODE 2: UPDATE - Granular updates to existing spreadsheet
    MODE 3: LEGACY - Simple single-sheet creation (backward compatible)
    
    ═══════════════════════════════════════════════════════════════════
    MODE 1: CREATE MULTI-SHEET SPREADSHEET
    ═══════════════════════════════════════════════════════════════════
    
    Args:
        spreadsheet_name (str): New spreadsheet name
        sheets (list): List of sheet definitions, each with:
            - name (str): Sheet tab name
            - headers (list): Optional header row
            - data (list[list]): Optional 2D data array
            - formulas (list): Optional formula definitions:
                [{"range": "D2:D10", "formula": "=SUM(A2:C2)"}]
            - parse_markdown (bool): Enable markdown in this sheet
    
    Example:
        google_sheets_smart_builder(
            spreadsheet_name="Q4 Sales Report",
            sheets=[
                {
                    "name": "Sales Data",
                    "headers": ["Product", "Q3", "Q4", "Change"],
                    "data": [["Widget", 100, 150, ""], ["Gadget", 200, 180, ""]],
                    "formulas": [
                        {"range": "D2:D3", "formula": "=(C2-B2)/B2"}
                    ]
                },
                {
                    "name": "Summary",
                    "headers": ["Metric", "Value"],
                    "formulas": [
                        {"range": "B2", "formula": "=SUM('Sales Data'!C2:C10)"}
                    ]
                }
            ]
        )
    
    Returns:
        {
            'success': True,
            'mode': 'create',
            'spreadsheet_id': 'abc123',
            'url': 'https://docs.google.com/spreadsheets/...',
            'sheets_created': 2,
            'total_formulas': 3,
            'sheets': [...]
        }
    
    ═══════════════════════════════════════════════════════════════════
    MODE 2: UPDATE EXISTING SPREADSHEET
    ═══════════════════════════════════════════════════════════════════
    
    Args:
        spreadsheet_id (str): Existing spreadsheet ID
        operations (list): List of operations to perform:
            - {"action": "add_sheet", "name": "Q1 2026"}
            - {"action": "update_cell", "cell": "A1", "value": "New"}
            - {"action": "add_formula", "range": "D2:D10", "formula": "=SUM(A2:C2)"}
            - {"action": "delete_rows", "start": 5, "count": 3}
            - {"action": "insert_columns", "start": 2, "count": 1}
    
    Example:
        google_sheets_smart_builder(
            spreadsheet_id="abc123",
            operations=[
                {"action": "add_sheet", "name": "Q1 2026"},
                {"action": "update_cell", "sheet": "Summary", "cell": "A1", "value": "Updated"},
                {"action": "add_formula", "sheet": "Summary", "range": "B2", "formula": "=AVERAGE(Data!A:A)"}
            ]
        )
    
    Returns:
        {
            'success': True,
            'mode': 'update',
            'spreadsheet_id': 'abc123',
            'operations_completed': 3,
            'operations': [...]
        }
    
    ═══════════════════════════════════════════════════════════════════
    MODE 3: LEGACY - Simple Single-Sheet Creation
    ═══════════════════════════════════════════════════════════════════
    
    Args:
        title (str): Spreadsheet title
        data (list[list]): Data rows
        headers (list): Header row
        parse_markdown (bool): Enable markdown formatting
    
    Example:
        google_sheets_smart_builder(
            title="Contact List",
            headers=["Name", "Email"],
            data=[["John", "john@example.com"]]
        )
    
    Returns:
        {
            'success': True,
            'mode': 'legacy',
            'spreadsheet_id': 'abc123',
            'url': 'https://docs.google.com/spreadsheets/...'
        }
    """
    
    print("\n" + "="*70)
    print("🚀 GOOGLE SHEETS SMART BUILDER")
    print("="*70)
    
    try:
        # Phase 5: route through the shared injector when user context is present
        # (no local cred_dict needed — internal helpers receive _injected_credentials directly)

        # ═══════════════════════════════════════════════════════════════
        # DETERMINE MODE
        # ═══════════════════════════════════════════════════════════════

        if spreadsheet_name and sheets:
            # MODE 1: CREATE multi-sheet spreadsheet
            mode = 'create'
            print("📋 Mode: CREATE multi-sheet spreadsheet")
            print(f"   Name: {spreadsheet_name}")
            print(f"   Sheets: {len(sheets)}")

            return _smart_builder_create_multisheet(
                spreadsheet_name, sheets, _user_id, _injected_credentials
            )

        elif spreadsheet_id and operations:
            # MODE 2: UPDATE existing spreadsheet
            mode = 'update'
            print("✏️  Mode: UPDATE existing spreadsheet")
            print(f"   ID: {spreadsheet_id}")
            print(f"   Operations: {len(operations)}")

            return _smart_builder_update_existing(
                spreadsheet_id, operations, _user_id, _injected_credentials
            )
            
        elif title:
            # MODE 3: LEGACY simple creation
            mode = 'legacy'
            print("📄 Mode: LEGACY simple creation")
            print(f"   Title: {title}")
            
            return google_sheets_create(
                title=title,
                data=data,
                headers=headers,
                parse_markdown=parse_markdown,
                _user_id=_user_id,
                _injected_credentials=_injected_credentials
            )
            
        else:
            raise ValueError(
                "Invalid parameters. Choose one mode:\n"
                "MODE 1 (CREATE): spreadsheet_name + sheets\n"
                "MODE 2 (UPDATE): spreadsheet_id + operations\n"
                "MODE 3 (LEGACY): title + data/headers"
            )
            
    except Exception as e:
        print(f"\n❌ Smart builder failed: {e}")
        raise


def _smart_builder_create_multisheet(spreadsheet_name, sheets, user_id, injected_credentials):
    """MODE 1: Create multi-sheet spreadsheet"""

    sheets_service = _get_sheets_service(user_id=user_id, injected_credentials=injected_credentials)
    if user_id and injected_credentials:
        from AI_infrastructure.auth.credential_injector import get_user_drive_service
        drive_service = get_user_drive_service(user_id=user_id)
    else:
        drive_service = build_drive_service()
    
    # Step 1: Create spreadsheet with multiple sheets
    print(f"\n📝 Step 1: Creating spreadsheet with {len(sheets)} sheets...")
    
    sheet_properties = []
    for idx, sheet_def in enumerate(sheets):
        sheet_name = sheet_def.get('name', f'Sheet{idx + 1}')
        sheet_properties.append({
            'properties': {
                'title': sheet_name,
                'index': idx
            }
        })
    
    spreadsheet_body = {
        'properties': {'title': spreadsheet_name},
        'sheets': sheet_properties
    }
    
    spreadsheet = sheets_service.spreadsheets().create(body=spreadsheet_body).execute()
    spreadsheet_id = spreadsheet['spreadsheetId']
    
    print(f"   ✅ Created: {spreadsheet_id}")
    
    # Step 2: Populate each sheet with data
    print(f"\n📊 Step 2: Populating {len(sheets)} sheets...")
    
    sheet_results = []
    total_formulas = 0
    
    for idx, sheet_def in enumerate(sheets):
        sheet_name = sheet_def.get('name', f'Sheet{idx + 1}')
        headers = sheet_def.get('headers')
        data = sheet_def.get('data')
        formulas = sheet_def.get('formulas', [])
        parse_markdown = sheet_def.get('parse_markdown', False)
        
        print(f"\n   Sheet: {sheet_name}")
        
        # Write data
        if headers or data:
            values = []
            if headers:
                values.append(headers)
            if data:
                values.extend(data)
            
            range_name = f"{sheet_name}!A1"
            body = {'values': values}
            
            result = sheets_service.spreadsheets().values().update(
                spreadsheetId=spreadsheet_id,
                range=range_name,
                valueInputOption='USER_ENTERED',
                body=body
            ).execute()
            
            rows_written = result.get('updatedRows', 0)
            print(f"      ✅ Wrote {rows_written} rows")
        
        # Add formulas
        if formulas:
            for formula_def in formulas:
                formula_range = formula_def.get('range')
                formula_text = formula_def.get('formula')
                
                google_sheets_add_formula(
                    spreadsheet_id=spreadsheet_id,
                    range=formula_range,
                    formula=formula_text,
                    sheet_name=sheet_name,
                    parse_natural=True,
                    _user_id=user_id,
                    _injected_credentials=injected_credentials
                )
                
                total_formulas += 1
                print(f"      ✅ Added formula to {formula_range}")
        
        sheet_results.append({
            'name': sheet_name,
            'rows': len(values) if (headers or data) else 0,
            'formulas': len(formulas)
        })
    
    # Step 3: Make shareable
    print(f"\n🔓 Step 3: Making shareable...")
    
    permission = {'type': 'anyone', 'role': 'writer'}
    drive_service.permissions().create(
        fileId=spreadsheet_id,
        body=permission
    ).execute()
    
    url = f"https://docs.google.com/spreadsheets/d/{spreadsheet_id}/edit"
    
    print(f"\n✅ COMPLETE!")
    print(f"   URL: {url}")
    print(f"   Sheets: {len(sheets)}")
    print(f"   Formulas: {total_formulas}")
    print("="*70 + "\n")
    
    return {
        'success': True,
        'mode': 'create',
        'spreadsheet_id': spreadsheet_id,
        'url': url,
        'spreadsheet_name': spreadsheet_name,
        'sheets_created': len(sheets),
        'total_formulas': total_formulas,
        'sheets': sheet_results
    }


def _smart_builder_update_existing(spreadsheet_id, operations, user_id, injected_credentials):
    """MODE 2: Update existing spreadsheet"""
    
    print(f"\n🔧 Processing {len(operations)} operations...")
    
    results = []
    
    for idx, op in enumerate(operations):
        action = op.get('action')
        
        print(f"\n   [{idx+1}/{len(operations)}] {action.upper()}")
        
        try:
            if action == 'add_sheet':
                # Add new sheet
                result = google_sheets_manage_sheets(
                    spreadsheet_id=spreadsheet_id,
                    action='add',
                    new_name=op.get('name'),
                    position=op.get('position'),
                    _user_id=user_id,
                    _injected_credentials=injected_credentials
                )
                print(f"      ✅ Added sheet: {op.get('name')}")
                
            elif action == 'delete_sheet':
                # Delete sheet
                result = google_sheets_manage_sheets(
                    spreadsheet_id=spreadsheet_id,
                    action='delete',
                    sheet_name=op.get('name'),
                    _user_id=user_id,
                    _injected_credentials=injected_credentials
                )
                print(f"      ✅ Deleted sheet: {op.get('name')}")
                
            elif action == 'rename_sheet':
                # Rename sheet
                result = google_sheets_manage_sheets(
                    spreadsheet_id=spreadsheet_id,
                    action='rename',
                    sheet_name=op.get('old_name'),
                    new_name=op.get('new_name'),
                    _user_id=user_id,
                    _injected_credentials=injected_credentials
                )
                print(f"      ✅ Renamed: {op.get('old_name')} → {op.get('new_name')}")
                
            elif action == 'update_cell':
                # Update single cell
                result = google_sheets_update_cell(
                    spreadsheet_id=spreadsheet_id,
                    cell=op.get('cell'),
                    value=op.get('value'),
                    sheet_name=op.get('sheet'),
                    value_type=op.get('value_type', 'auto'),
                    _user_id=user_id,
                    _injected_credentials=injected_credentials
                )
                print(f"      ✅ Updated {op.get('cell')} = {op.get('value')}")
                
            elif action == 'add_formula':
                # Add formula
                result = google_sheets_add_formula(
                    spreadsheet_id=spreadsheet_id,
                    range=op.get('range'),
                    formula=op.get('formula'),
                    sheet_name=op.get('sheet'),
                    parse_natural=op.get('parse_natural', True),
                    _user_id=user_id,
                    _injected_credentials=injected_credentials
                )
                print(f"      ✅ Added formula to {op.get('range')}")
                
            elif action == 'delete_rows':
                # Delete rows
                result = google_sheets_insert_delete_dimensions(
                    spreadsheet_id=spreadsheet_id,
                    dimension='ROWS',
                    action='delete',
                    start_index=op.get('start'),
                    count=op.get('count', 1),
                    sheet_name=op.get('sheet', 'Sheet1'),
                    _user_id=user_id,
                    _injected_credentials=injected_credentials
                )
                print(f"      ✅ Deleted {op.get('count', 1)} rows")
                
            elif action == 'insert_rows':
                # Insert rows
                result = google_sheets_insert_delete_dimensions(
                    spreadsheet_id=spreadsheet_id,
                    dimension='ROWS',
                    action='insert',
                    start_index=op.get('start'),
                    count=op.get('count', 1),
                    sheet_name=op.get('sheet', 'Sheet1'),
                    _user_id=user_id,
                    _injected_credentials=injected_credentials
                )
                print(f"      ✅ Inserted {op.get('count', 1)} rows")
                
            elif action == 'delete_columns':
                # Delete columns
                result = google_sheets_insert_delete_dimensions(
                    spreadsheet_id=spreadsheet_id,
                    dimension='COLUMNS',
                    action='delete',
                    start_index=op.get('start'),
                    count=op.get('count', 1),
                    sheet_name=op.get('sheet', 'Sheet1'),
                    _user_id=user_id,
                    _injected_credentials=injected_credentials
                )
                print(f"      ✅ Deleted {op.get('count', 1)} columns")
                
            elif action == 'insert_columns':
                # Insert columns
                result = google_sheets_insert_delete_dimensions(
                    spreadsheet_id=spreadsheet_id,
                    dimension='COLUMNS',
                    action='insert',
                    start_index=op.get('start'),
                    count=op.get('count', 1),
                    sheet_name=op.get('sheet', 'Sheet1'),
                    _user_id=user_id,
                    _injected_credentials=injected_credentials
                )
                print(f"      ✅ Inserted {op.get('count', 1)} columns")
                
            elif action == 'batch_update':
                # Batch update cells
                result = google_sheets_batch_update_cells(
                    spreadsheet_id=spreadsheet_id,
                    updates=op.get('updates'),
                    _user_id=user_id,
                    _injected_credentials=injected_credentials
                )
                print(f"      ✅ Batch updated {len(op.get('updates', []))} cells")
                
            else:
                raise ValueError(f"Unknown action: {action}")
            
            results.append({
                'action': action,
                'success': True,
                'result': result
            })
            
        except Exception as e:
            print(f"      ❌ Failed: {e}")
            results.append({
                'action': action,
                'success': False,
                'error': str(e)
            })
    
    successful = sum(1 for r in results if r['success'])
    
    print(f"\n✅ COMPLETE!")
    print(f"   Operations: {successful}/{len(operations)} successful")
    print("="*70 + "\n")
    
    return {
        'success': True,
        'mode': 'update',
        'spreadsheet_id': spreadsheet_id,
        'operations_completed': successful,
        'operations_total': len(operations),
        'operations': results
    }

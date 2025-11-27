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

from google_docs import (
    _get_user_credentials_if_available,
    build_drive_service,
    build,
    HAS_DOCS_API,
    get_service_account_credentials
)

# ==================== SHEETS SERVICE ====================

def _get_sheets_service(user_id=None, injected_credentials=None):
    """Get authenticated Google Sheets API service
    
    Args:
        user_id: User ID for OAuth credentials from database
        injected_credentials: OAuth credentials dict (from database)
    
    Returns:
        Authenticated Sheets service
    """
    if not HAS_DOCS_API:
        raise Exception("Google Sheets API not available")
    
    # If user credentials provided, use them
    if user_id and injected_credentials:
        from google.oauth2.credentials import Credentials
        
        SCOPES = [
            'https://www.googleapis.com/auth/spreadsheets',
            'https://www.googleapis.com/auth/drive'
        ]
        
        credentials = Credentials(
            token=injected_credentials.get('access_token'),
            refresh_token=injected_credentials.get('refresh_token'),
            token_uri='https://oauth2.googleapis.com/token',
            client_id=injected_credentials.get('client_id'),
            client_secret=injected_credentials.get('client_secret'),
            scopes=SCOPES
        )
        
        service = build('sheets', 'v4', credentials=credentials)
        return service
    
    # Fall back to service account credentials
    SCOPES = [
        'https://www.googleapis.com/auth/spreadsheets',
        'https://www.googleapis.com/auth/drive'
    ]
    credentials = get_service_account_credentials(SCOPES)
    return build('sheets', 'v4', credentials=credentials)


# ==================== CREATE SPREADSHEETS ====================

def google_sheets_create(title, data=None, headers=None, parse_markdown=False, 
                        auto_borders=True,
                        _user_id=None, _injected_credentials=None, **kwargs):
    """
    Create a new Google Sheet with optional data and markdown formatting
    
    Args:
        title (str): Spreadsheet title
        data (list[list]): Optional 2D array of data [[row1], [row2], ...]
        headers (list): Optional header row
        parse_markdown (bool): If True, parse markdown syntax and apply formatting
        auto_borders (bool): If True, add borders to all cells (default: True)
        _user_id: User ID for credential injection
        _injected_credentials: Flag for credential injection
        
    Markdown Support (when parse_markdown=True):
        - **bold** → Bold text
        - *italic* → Italic text
        - # Header → Bold, larger font, gray background
        - [RED]text[/RED] → Red text (also: GREEN, BLUE, YELLOW, ORANGE, PURPLE, GRAY)
        - Tables get borders automatically
        
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
        # Get user credentials if available
        cred_dict = _get_user_credentials_if_available(_user_id, _injected_credentials)
        
        sheets_service = _get_sheets_service(user_id=_user_id, injected_credentials=cred_dict)
        drive_service = build_drive_service(user_id=_user_id, injected_credentials=cred_dict)
        
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
                
                # Parse markdown and get formatting
                clean_data, clean_headers, format_requests = format_data_with_markdown(
                    data or [], headers, 
                    auto_borders=auto_borders
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
    Create multiple Google Sheets at once with optional markdown formatting
    
    Args:
        spreadsheets_config (list): List of spreadsheet configs, each with:
            - title (str): Spreadsheet title
            - headers (list): Optional header row
            - data (list[list]): Optional 2D array of data
            - parse_markdown (bool): Optional, enable markdown (default: False)
            - auto_borders (bool): Optional, add borders (default: True)
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
            
            # print(f"   [{idx}/{len(spreadsheets_config)}] Creating: {title}")
            
            # Call google_sheets_create for each spreadsheet
            result = google_sheets_create(
                title=title,
                data=data,
                headers=headers,
                parse_markdown=parse_markdown,
                auto_borders=auto_borders,
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
        cred_dict = _get_user_credentials_if_available(_user_id, _injected_credentials)
        sheets_service = _get_sheets_service(user_id=_user_id, injected_credentials=cred_dict)
        
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
        cred_dict = _get_user_credentials_if_available(_user_id, _injected_credentials)
        sheets_service = _get_sheets_service(user_id=_user_id, injected_credentials=cred_dict)
        
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
        cred_dict = _get_user_credentials_if_available(_user_id, _injected_credentials)
        sheets_service = _get_sheets_service(user_id=_user_id, injected_credentials=cred_dict)
        
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
        cred_dict = _get_user_credentials_if_available(_user_id, _injected_credentials)
        sheets_service = _get_sheets_service(user_id=_user_id, injected_credentials=cred_dict)
        
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
        cred_dict = _get_user_credentials_if_available(_user_id, _injected_credentials)
        sheets_service = _get_sheets_service(user_id=_user_id, injected_credentials=cred_dict)
        
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

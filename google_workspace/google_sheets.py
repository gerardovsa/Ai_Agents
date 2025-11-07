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
        # print(f"[OK] Sheet made shareable and editable: {url}")
        
        return {
            'spreadsheet_id': spreadsheet_id,
            'url': url,
            'title': title,
            'rows_written': rows_written,
            'markdown_parsed': markdown_parsed
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


def google_sheets_read_data(spreadsheet_id, range_name='Sheet1!A1:Z1000', _user_id=None, _injected_credentials=None, **kwargs):
    """
    Read data from Google Sheet
    
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

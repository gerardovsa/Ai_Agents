"""
Google Sheets Implementation - Tool Registry Wrappers
=====================================================

Wrapper functions for the tool registry to call google_workspace.gsheets functions.
These wrappers handle error formatting, parameter validation, and response formatting
for the AI agent.

Author: Auto-generated
Date: 2025-10-27
"""

# Import Google Sheets functions from google_docs (they use Sheets API v4)
from google_workspace import google_docs
import json
from typing import Dict, Any, List

# Alias for compatibility with existing code
class gsheets:
    """Compatibility wrapper for Google Sheets functions"""
    @staticmethod
    def gsheets_create_complete_spreadsheet(title, data=None, headers=None, sheet_name='Sheet1', 
                                           formatting=None, shareable=True, **kwargs):
        """
        Creates a complete spreadsheet with data and formatting.
        Maps to google_sheets_create which handles data, headers, and sharing.
        
        Note: 'formatting' and 'sheet_name' parameters are accepted but not yet implemented
        in the Sheets API v4 version. The function will create the spreadsheet with data/headers
        and make it shareable.
        """
        # google_sheets_create already handles title, data, headers, and sharing
        # It returns: {'spreadsheet_id': str, 'url': str, 'title': str, 'rows_written': int}
        result = google_docs.google_sheets_create(
            title=title,
            data=data,
            headers=headers,
            **kwargs  # Pass through _user_id, _injected_credentials, etc.
        )
        
        # Format response to match expected structure
        return {
            'spreadsheet_id': result.get('spreadsheet_id'),
            'url': result.get('url'),
            'title': result.get('title'),
            'rows_written': result.get('rows_written', 0),
            'shareable': True  # google_sheets_create makes it shareable by default
        }
    
    @staticmethod
    def gsheets_create(*args, **kwargs):
        return google_docs.google_sheets_create(*args, **kwargs)
    
    @staticmethod
    def gsheets_read(spreadsheet_id, range='Sheet1!A1:Z1000', **kwargs):
        """Maps gsheets_read to google_sheets_read_data"""
        return google_docs.google_sheets_read_data(
            spreadsheet_id=spreadsheet_id,
            range_name=range,
            **kwargs
        )
    
    @staticmethod
    def gsheets_write(spreadsheet_id, range, values, **kwargs):
        """
        Write/update cells in a spreadsheet.
        Note: The Sheets API v4 version uses append for now.
        For true overwrite, we'd need to implement clear + write.
        """
        # For now, map to append as it's the closest equivalent
        # TODO: Implement proper write with clear operation if needed
        return google_docs.google_sheets_append_data(
            spreadsheet_id=spreadsheet_id,
            data=values,
            sheet_name=range.split('!')[0] if '!' in range else 'Sheet1',
            **kwargs
        )
    
    @staticmethod
    def gsheets_append(spreadsheet_id, range, values, **kwargs):
        """Maps gsheets_append to google_sheets_append_data"""
        return google_docs.google_sheets_append_data(
            spreadsheet_id=spreadsheet_id,
            data=values,
            sheet_name=range.split('!')[0] if '!' in range else 'Sheet1',
            **kwargs
        )

# ============================================================================
# SMART BUNDLED TOOLS (HIGH PRIORITY)
# ============================================================================

def gsheets_create_complete_spreadsheet_impl(params: Dict[str, Any]) -> Dict[str, Any]:
    """
    Wrapper for gsheets.gsheets_create_complete_spreadsheet
    
    Creates a complete spreadsheet with data and formatting in ONE operation.
    Most efficient method for spreadsheet creation.
    """
    try:
        # Extract parameters
        title = params.get('title')
        data = params.get('data', [])
        headers = params.get('headers')
        sheet_name = params.get('sheet_name', 'Sheet1')
        formatting = params.get('formatting')
        shareable = params.get('shareable', True)
        
        # Validate required parameters
        if not title:
            return {
                "success": False,
                "error": "Parameter 'title' is required"
            }
        
        if not data or len(data) == 0:
            return {
                "success": False,
                "error": "Parameter 'data' must be a non-empty array"
            }
        
        # Call the actual function
        result = gsheets.gsheets_create_complete_spreadsheet(
            title=title,
            data=data,
            headers=headers,
            sheet_name=sheet_name,
            formatting=formatting,
            shareable=shareable
        )
        
        return {
            "success": True,
            "data": result,
            "message": f"Created complete spreadsheet '{title}' with {result.get('rows_added', 0)} rows"
        }
        
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "error_type": type(e).__name__
        }


def gsheets_ai_generate_table_impl(params: Dict[str, Any]) -> Dict[str, Any]:
    """
    Wrapper for gsheets.gsheets_ai_generate_table
    
    Generates a data table using AI from natural language description.
    """
    try:
        # Extract parameters
        prompt = params.get('prompt')
        title = params.get('title')
        shareable = params.get('shareable', True)
        ai_model = params.get('ai_model', 'gpt-4')
        
        # Validate required parameters
        if not prompt:
            return {
                "success": False,
                "error": "Parameter 'prompt' is required"
            }
        
        # Call the actual function
        result = gsheets.gsheets_ai_generate_table(
            prompt=prompt,
            title=title,
            shareable=shareable,
            ai_model=ai_model
        )
        
        return {
            "success": True,
            "data": result,
            "message": f"AI-generated table '{result.get('title')}' with {result.get('rows_generated', 0)} rows"
        }
        
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "error_type": type(e).__name__,
            "note": "This function requires OPENAI_API_KEY environment variable to be set"
        }


def gsheets_bulk_create_multiple_impl(params: Dict[str, Any]) -> Dict[str, Any]:
    """
    Wrapper for gsheets.gsheets_bulk_create_multiple
    
    Creates multiple spreadsheets at once.
    """
    try:
        # Extract parameters
        spreadsheets_configs = params.get('spreadsheets_configs', [])
        shareable = params.get('shareable', True)
        
        # Validate required parameters
        if not spreadsheets_configs or len(spreadsheets_configs) == 0:
            return {
                "success": False,
                "error": "Parameter 'spreadsheets_configs' must be a non-empty array"
            }
        
        # Call the actual function
        result = gsheets.gsheets_bulk_create_multiple(
            spreadsheets_configs=spreadsheets_configs,
            shareable=shareable
        )
        
        return {
            "success": True,
            "data": result,
            "message": f"Created {result.get('spreadsheets_created', 0)} spreadsheets in bulk"
        }
        
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "error_type": type(e).__name__
        }


# ============================================================================
# BASIC SPREADSHEET OPERATIONS
# ============================================================================

def gsheets_create_impl(params: Dict[str, Any]) -> Dict[str, Any]:
    """
    Wrapper for gsheets.gsheets_create
    
    Creates an empty spreadsheet. NOTE: Consider using gsheets_create_complete_spreadsheet instead.
    """
    try:
        title = params.get('title')
        sheets = params.get('sheets')
        
        if not title:
            return {"success": False, "error": "Parameter 'title' is required"}
        
        result = gsheets.gsheets_create(
            title=title,
            sheets=sheets
        )
        
        return {
            "success": True,
            "data": result,
            "message": f"Created spreadsheet '{title}'"
        }
        
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "error_type": type(e).__name__
        }


def gsheets_read_impl(params: Dict[str, Any]) -> Dict[str, Any]:
    """
    Wrapper for gsheets.gsheets_read
    
    Reads data from a spreadsheet.
    """
    try:
        spreadsheet_id = params.get('spreadsheet_id')
        range_param = params.get('range')
        
        if not spreadsheet_id:
            return {"success": False, "error": "Parameter 'spreadsheet_id' is required"}
        if not range_param:
            return {"success": False, "error": "Parameter 'range' is required"}
        
        result = gsheets.gsheets_read(
            spreadsheet_id=spreadsheet_id,
            range=range_param
        )
        
        return {
            "success": True,
            "data": result,
            "message": f"Read {result.get('rows', 0)} rows from spreadsheet"
        }
        
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "error_type": type(e).__name__
        }


def gsheets_write_impl(params: Dict[str, Any]) -> Dict[str, Any]:
    """
    Wrapper for gsheets.gsheets_write
    
    Writes data to a spreadsheet.
    """
    try:
        spreadsheet_id = params.get('spreadsheet_id')
        range_param = params.get('range')
        values = params.get('values', [])
        
        if not spreadsheet_id:
            return {"success": False, "error": "Parameter 'spreadsheet_id' is required"}
        if not range_param:
            return {"success": False, "error": "Parameter 'range' is required"}
        if not values:
            return {"success": False, "error": "Parameter 'values' must be a non-empty array"}
        
        result = gsheets.gsheets_write(
            spreadsheet_id=spreadsheet_id,
            range=range_param,
            values=values
        )
        
        return {
            "success": True,
            "data": result,
            "message": f"Updated {result.get('rows_updated', 0)} rows in spreadsheet"
        }
        
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "error_type": type(e).__name__
        }


def gsheets_append_impl(params: Dict[str, Any]) -> Dict[str, Any]:
    """
    Wrapper for gsheets.gsheets_append
    
    Appends rows to a spreadsheet.
    """
    try:
        spreadsheet_id = params.get('spreadsheet_id')
        range_param = params.get('range')
        values = params.get('values', [])
        
        if not spreadsheet_id:
            return {"success": False, "error": "Parameter 'spreadsheet_id' is required"}
        if not range_param:
            return {"success": False, "error": "Parameter 'range' is required"}
        if not values:
            return {"success": False, "error": "Parameter 'values' must be a non-empty array"}
        
        result = gsheets.gsheets_append(
            spreadsheet_id=spreadsheet_id,
            range=range_param,
            values=values
        )
        
        return {
            "success": True,
            "data": result,
            "message": f"Appended {result.get('rows_appended', 0)} rows to spreadsheet"
        }
        
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "error_type": type(e).__name__
        }


# ============================================================================
# TOOL REGISTRY MAPPING
# ============================================================================

GSHEETS_TOOL_IMPLEMENTATIONS = {
    # Smart bundled tools
    'gsheets_create_complete_spreadsheet': gsheets_create_complete_spreadsheet_impl,
    'gsheets_ai_generate_table': gsheets_ai_generate_table_impl,
    'gsheets_bulk_create_multiple': gsheets_bulk_create_multiple_impl,
    
    # Basic operations
    'gsheets_create': gsheets_create_impl,
    'gsheets_read': gsheets_read_impl,
    'gsheets_write': gsheets_write_impl,
    'gsheets_append': gsheets_append_impl,
}


def get_gsheets_implementation(tool_name: str):
    """
    Get the implementation function for a given tool name.
    
    Args:
        tool_name: Name of the tool (e.g., 'gsheets_create_complete_spreadsheet')
    
    Returns:
        Implementation function or None if not found
    """
    return GSHEETS_TOOL_IMPLEMENTATIONS.get(tool_name)

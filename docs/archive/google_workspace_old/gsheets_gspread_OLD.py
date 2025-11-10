"""
Google Sheets Tool Implementations
===================================

This module provides tool implementations for Google Sheets.
"""

import os
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

try:
    from auth import get_authenticated_gspread_client_sync
    HAS_GSPREAD = True
except ImportError:
    HAS_GSPREAD = False
    print("⚠️ gspread dependencies not available")


def _get_client():
    """Get authenticated gspread client"""
    if not HAS_GSPREAD:
        raise Exception("gspread client not available - install dependencies")
    
    return get_authenticated_gspread_client_sync()


def gsheets_read(spreadsheet_id: str, range: str):
    """
    Read data from a Google Sheets spreadsheet.
    
    Args:
        spreadsheet_id: Spreadsheet ID from URL
        range: Cell range (e.g., 'Sheet1!A1:D10')
    
    Returns:
        Cell values as 2D array
    """
    print(f"🔧 Reading from Google Sheets: {spreadsheet_id}")
    
    try:
        client = _get_client()
        spreadsheet = client.open_by_key(spreadsheet_id)
        
        # Parse range
        if '!' in range:
            sheet_name, cell_range = range.split('!')
            worksheet = spreadsheet.worksheet(sheet_name)
        else:
            worksheet = spreadsheet.sheet1
            cell_range = range
        
        # Get values
        values = worksheet.get(cell_range)
        
        return {
            'values': values,
            'rows': len(values),
            'columns': len(values[0]) if values else 0
        }
        
    except Exception as e:
        print(f"❌ Failed to read spreadsheet: {e}")
        raise


def gsheets_write(spreadsheet_id: str, range: str, values: list):
    """
    Write data to a Google Sheets spreadsheet.
    
    Args:
        spreadsheet_id: Spreadsheet ID from URL
        range: Cell range to write to
        values: 2D array of values
    
    Returns:
        Update confirmation
    """
    print(f"🔧 Writing to Google Sheets: {spreadsheet_id}")
    
    try:
        client = _get_client()
        spreadsheet = client.open_by_key(spreadsheet_id)
        
        # Parse range
        if '!' in range:
            sheet_name, cell_range = range.split('!')
            worksheet = spreadsheet.worksheet(sheet_name)
        else:
            worksheet = spreadsheet.sheet1
            cell_range = range
        
        # Update values
        worksheet.update(cell_range, values)
        
        return {
            'updated': True,
            'range': range,
            'rows_updated': len(values),
            'cells_updated': sum(len(row) for row in values)
        }
        
    except Exception as e:
        print(f"❌ Failed to write to spreadsheet: {e}")
        raise


def gsheets_append(spreadsheet_id: str, range: str, values: list):
    """
    Append rows to the end of a sheet.
    
    Args:
        spreadsheet_id: Spreadsheet ID from URL
        range: Sheet name and starting column (e.g., 'Sheet1!A:D')
        values: 2D array of values to append
    
    Returns:
        Append confirmation
    """
    print(f"🔧 Appending to Google Sheets: {spreadsheet_id}")
    
    try:
        client = _get_client()
        spreadsheet = client.open_by_key(spreadsheet_id)
        
        # Parse range
        if '!' in range:
            sheet_name, _ = range.split('!')
            worksheet = spreadsheet.worksheet(sheet_name)
        else:
            worksheet = spreadsheet.sheet1
        
        # Append values
        worksheet.append_rows(values)
        
        return {
            'appended': True,
            'rows_appended': len(values),
            'range': range
        }
        
    except Exception as e:
        print(f"❌ Failed to append to spreadsheet: {e}")
        raise


def gsheets_create(title: str, sheets: list = None):
    """
    Create a new Google Sheets spreadsheet.
    
    Args:
        title: Spreadsheet title
        sheets: Array of sheet names to create
    
    Returns:
        Created spreadsheet details
    """
    print(f"🔧 Creating Google Sheets spreadsheet: {title}")
    
    try:
        client = _get_client()
        spreadsheet = client.create(title)
        
        # Add additional sheets if specified
        if sheets and len(sheets) > 1:
            for sheet_name in sheets[1:]:  # Skip first as it's already created
                spreadsheet.add_worksheet(title=sheet_name, rows=1000, cols=26)
        
        return {
            'title': spreadsheet.title,
            'id': spreadsheet.id,
            'url': spreadsheet.url,
            'created': True
        }
        
    except Exception as e:
        print(f"❌ Failed to create spreadsheet: {e}")
        raise


# ============================================================================
# SMART BUNDLED TOOLS (HIGH-LEVEL OPERATIONS)
# ============================================================================

def gsheets_create_complete_spreadsheet(
    title: str,
    data: list,
    sheet_name: str = "Sheet1",
    headers: list = None,
    formatting: dict = None,
    shareable: bool = True
):
    """
    ⭐ SMART BUNDLED TOOL: Create a complete spreadsheet with data and formatting in ONE call.
    
    This is the MOST EFFICIENT way to create spreadsheets. Instead of:
    1. Create spreadsheet
    2. Write data
    3. Format headers
    4. Set permissions
    
    This function does ALL of that in ONE operation.
    
    Args:
        title (str): Spreadsheet title
        data (list): 2D array of data [[row1], [row2], ...]
        sheet_name (str): Name for the first sheet (default: "Sheet1")
        headers (list): Optional header row (will be bolded automatically)
        formatting (dict): Optional formatting options:
            - bold_headers (bool): Make first row bold (default: True if headers provided)
            - freeze_header (bool): Freeze first row (default: True if headers provided)
            - auto_resize (bool): Auto-resize columns (default: True)
        shareable (bool): Make spreadsheet accessible to anyone with link (default: True)
    
    Returns:
        dict: {
            'id': str,              # Spreadsheet ID
            'url': str,             # Shareable URL
            'title': str,           # Spreadsheet title
            'rows_added': int,      # Total rows added
            'columns': int,         # Number of columns
            'shareable': bool,      # Whether it's shareable
            'sheet_name': str       # Name of the sheet
        }
    
    Example:
        # Simple data table
        result = gsheets_create_complete_spreadsheet(
            title="Q4 Sales Report",
            headers=["Product", "Revenue", "Units Sold"],
            data=[
                ["Widget A", 15000, 150],
                ["Widget B", 22000, 200],
                ["Widget C", 18500, 175]
            ],
            shareable=True
        )
        # Returns: {'id': '...', 'url': 'https://docs.google.com/spreadsheets/d/...', ...}
    
    Example with formatting:
        result = gsheets_create_complete_spreadsheet(
            title="Customer Data",
            headers=["Name", "Email", "Phone", "Status"],
            data=[
                ["John Doe", "john@example.com", "555-1234", "Active"],
                ["Jane Smith", "jane@example.com", "555-5678", "Active"]
            ],
            formatting={
                'bold_headers': True,
                'freeze_header': True,
                'auto_resize': True
            }
        )
    """
    print(f"🔧 Creating complete spreadsheet: {title}")
    
    try:
        # Set default formatting
        if formatting is None:
            formatting = {}
        
        bold_headers = formatting.get('bold_headers', headers is not None)
        freeze_header = formatting.get('freeze_header', headers is not None)
        auto_resize = formatting.get('auto_resize', True)
        
        # Step 1: Create spreadsheet
        client = _get_client()
        spreadsheet = client.create(title)
        
        # Rename first sheet if specified
        worksheet = spreadsheet.sheet1
        if sheet_name and sheet_name != "Sheet1":
            worksheet.update_title(sheet_name)
        
        # Step 2: Prepare data with headers
        all_data = []
        if headers:
            all_data.append(headers)
        if data:
            all_data.extend(data)
        
        # Step 3: Write all data at once
        if all_data:
            worksheet.update('A1', all_data)
        
        # Step 4: Apply formatting
        if bold_headers and headers:
            # Bold the header row
            worksheet.format('A1:Z1', {
                'textFormat': {'bold': True},
                'backgroundColor': {'red': 0.9, 'green': 0.9, 'blue': 0.9}
            })
        
        if freeze_header and headers:
            # Freeze first row
            worksheet.freeze(rows=1)
        
        if auto_resize:
            # Auto-resize columns to fit content
            worksheet.columns_auto_resize(0, len(headers) if headers else len(data[0]) if data else 1)
        
        # Step 5: Set permissions if shareable
        if shareable:
            try:
                spreadsheet.share('', perm_type='anyone', role='writer')
            except Exception as e:
                print(f"⚠️ Could not set sharing permissions: {e}")
        
        result = {
            'id': spreadsheet.id,
            'url': spreadsheet.url,
            'title': spreadsheet.title,
            'rows_added': len(all_data),
            'columns': len(headers) if headers else (len(data[0]) if data else 0),
            'shareable': shareable,
            'sheet_name': sheet_name
        }
        
        print(f"✅ Spreadsheet created: {title} ({len(all_data)} rows)")
        return result
        
    except Exception as e:
        print(f"❌ Failed to create complete spreadsheet: {e}")
        raise


def gsheets_ai_generate_table(
    prompt: str,
    title: str = None,
    shareable: bool = True,
    ai_model: str = "gpt-4"
):
    """
    ⭐ AI-POWERED: Generate a data table from natural language description.
    
    The AI will:
    - Determine appropriate columns
    - Generate realistic sample data
    - Create proper headers
    - Format the spreadsheet professionally
    
    Args:
        prompt (str): Natural language description of the table you want
        title (str): Spreadsheet title (optional, AI will generate if not provided)
        shareable (bool): Make spreadsheet accessible to anyone (default: True)
        ai_model (str): OpenAI model to use (default: "gpt-4")
    
    Returns:
        dict: {
            'id': str,
            'url': str,
            'title': str,
            'rows_generated': int,
            'ai_generated': bool
        }
    
    Example:
        result = gsheets_ai_generate_table(
            prompt="Create a sales tracking table with columns for date, product name, quantity sold, unit price, and total revenue. Include 10 sample rows of realistic data."
        )
        
    Example 2:
        result = gsheets_ai_generate_table(
            prompt="Make an employee directory with name, email, department, role, and hire date. Include 15 employees across different departments like Engineering, Sales, Marketing, and HR.",
            title="Company Directory 2025"
        )
    
    Requirements:
        - OPENAI_API_KEY environment variable must be set
    """
    print(f"🤖 AI generating table from prompt...")
    
    try:
        import openai
        import os
        
        # Check for API key
        api_key = os.getenv('OPENAI_API_KEY')
        if not api_key:
            raise Exception("OPENAI_API_KEY environment variable not set")
        
        openai.api_key = api_key
        
        # Create AI prompt
        system_prompt = """You are a data table generator. Generate realistic, well-structured data tables based on user descriptions.

Output format MUST be valid JSON:
{
    "title": "Table Title",
    "headers": ["Column1", "Column2", "Column3"],
    "data": [
        ["value1", "value2", "value3"],
        ["value1", "value2", "value3"]
    ]
}

Rules:
- Generate realistic, diverse data
- Use appropriate data types (numbers, dates, text)
- Include at least 5 rows unless specified otherwise
- Make data internally consistent
- Headers should be clear and professional
- NO explanatory text, ONLY the JSON object"""
        
        # Call OpenAI API
        response = openai.chat.completions.create(
            model=ai_model,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7
        )
        
        # Parse response
        import json
        ai_response = response.choices[0].message.content.strip()
        
        # Extract JSON if wrapped in code blocks
        if '```json' in ai_response:
            ai_response = ai_response.split('```json')[1].split('```')[0].strip()
        elif '```' in ai_response:
            ai_response = ai_response.split('```')[1].split('```')[0].strip()
        
        table_data = json.loads(ai_response)
        
        # Use provided title or AI-generated title
        final_title = title or table_data.get('title', 'AI Generated Table')
        
        # Create spreadsheet using the smart bundled tool
        result = gsheets_create_complete_spreadsheet(
            title=final_title,
            headers=table_data['headers'],
            data=table_data['data'],
            shareable=shareable,
            formatting={
                'bold_headers': True,
                'freeze_header': True,
                'auto_resize': True
            }
        )
        
        result['ai_generated'] = True
        result['rows_generated'] = len(table_data['data'])
        
        print(f"✅ AI generated table: {final_title} ({len(table_data['data'])} rows)")
        return result
        
    except ImportError:
        raise Exception("openai package not installed. Run: pip install openai")
    except Exception as e:
        print(f"❌ Failed to generate AI table: {e}")
        raise


def gsheets_bulk_create_multiple(
    spreadsheets_configs: list,
    shareable: bool = True
):
    """
    ⭐ BULK OPERATION: Create multiple spreadsheets at once.
    
    Most efficient way to create 2+ spreadsheets. Instead of calling
    gsheets_create_complete_spreadsheet multiple times, create all at once.
    
    Args:
        spreadsheets_configs (list): Array of spreadsheet configurations, each with:
            - title (str): Spreadsheet title
            - headers (list): Optional header row
            - data (list): 2D array of data
            - sheet_name (str): Optional sheet name
        shareable (bool): Make all spreadsheets shareable (default: True)
    
    Returns:
        dict: {
            'spreadsheets_created': int,
            'spreadsheets': [
                {'id': '...', 'url': '...', 'title': '...'},
                ...
            ]
        }
    
    Example:
        configs = [
            {
                'title': 'Q1 Sales - NYC',
                'headers': ['Product', 'Revenue'],
                'data': [['Widget A', 15000], ['Widget B', 22000]]
            },
            {
                'title': 'Q1 Sales - LA',
                'headers': ['Product', 'Revenue'],
                'data': [['Widget A', 18000], ['Widget B', 25000]]
            },
            {
                'title': 'Q1 Sales - Chicago',
                'headers': ['Product', 'Revenue'],
                'data': [['Widget A', 12000], ['Widget B', 19000]]
            }
        ]
        
        result = gsheets_bulk_create_multiple(configs)
        # Creates all 3 spreadsheets in one operation
    
    Use Cases:
        - Regional reports (one per location)
        - Department trackers (one per team)
        - Monthly reports (one per month)
        - Customer data (one per client)
    """
    print(f"📦 Bulk creating {len(spreadsheets_configs)} spreadsheets...")
    
    try:
        created_spreadsheets = []
        
        for config in spreadsheets_configs:
            title = config.get('title', 'Untitled Spreadsheet')
            headers = config.get('headers')
            data = config.get('data', [])
            sheet_name = config.get('sheet_name', 'Sheet1')
            
            # Create each spreadsheet using the smart bundled tool
            result = gsheets_create_complete_spreadsheet(
                title=title,
                headers=headers,
                data=data,
                sheet_name=sheet_name,
                shareable=shareable
            )
            
            created_spreadsheets.append({
                'id': result['id'],
                'url': result['url'],
                'title': result['title'],
                'rows': result['rows_added']
            })
        
        print(f"✅ Created {len(created_spreadsheets)} spreadsheets")
        
        return {
            'spreadsheets_created': len(created_spreadsheets),
            'spreadsheets': created_spreadsheets
        }
        
    except Exception as e:
        print(f"❌ Failed to bulk create spreadsheets: {e}")
        raise


if __name__ == "__main__":
    print("Google Sheets tools loaded")

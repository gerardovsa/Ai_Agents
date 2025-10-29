"""
Professional Google Sheets Chart Creator with Google Doc Integration + FOLDER ORGANIZATION

This script creates:
1. Google Drive folder (customizable name, default: "AI Agent Reports")
2. Google Doc with professional report structure (inside folder)
3. Google Sheets with multiple charts (inside folder)
4. Direct cell references from Doc to Sheet locations

Features:
- Automatic folder organization on Google Drive
- Multiple charts in one spreadsheet (each in separate sheets OR all in one)
- Chart titles, axis labels, legends with proper formatting
- Units (currency, percentage, etc.) in labels
- Spreadsheet name matches document name
- Editable and shareable (anyone with link)
- Document includes direct links to cell ranges where data lives
- User-friendly workflow: Open doc → See links → Go to spreadsheet → Copy charts
- Returns folder URL for easy access

NO EMOJIS - They break Google Docs!
"""

from pathlib import Path
from dotenv import load_dotenv
import sys

# Load .env.master credentials BEFORE importing tools
env_path = Path(__file__).parent / '.env.master'
load_dotenv(env_path, override=True)

from google_workspace.google_docs import google_docs_create_from_markdown
from google_workspace.google_drive import google_drive_create_folder, google_drive_move_file
from google_workspace.google_auth_helper import get_service_account_credentials
from googleapiclient.discovery import build


def build_sheets_service():
    """Get Google Sheets service"""
    SCOPES = [
        'https://www.googleapis.com/auth/spreadsheets',
        'https://www.googleapis.com/auth/drive'
    ]
    credentials = get_service_account_credentials(SCOPES)
    return build('sheets', 'v4', credentials=credentials)


def build_drive_service():
    """Get Google Drive service"""
    SCOPES = ['https://www.googleapis.com/auth/drive']
    credentials = get_service_account_credentials(SCOPES)
    return build('drive', 'v3', credentials=credentials)


def get_or_create_reports_folder(folder_name="AI Agent Reports", parent_folder_id=None):
    """
    Get existing folder or create new one
    
    Args:
        folder_name: Name of the folder (default: "AI Agent Reports")
        parent_folder_id: Optional parent folder ID (if None, creates in root)
    
    Returns:
        dict with folder_id, folder_name, folder_url
    """
    try:
        drive_service = build_drive_service()
        
        # Search for existing folder with this name
        query = f"name='{folder_name}' and mimeType='application/vnd.google-apps.folder' and trashed=false"
        if parent_folder_id:
            query += f" and '{parent_folder_id}' in parents"
        
        results = drive_service.files().list(
            q=query,
            spaces='drive',
            fields='files(id, name, webViewLink)'
        ).execute()
        
        folders = results.get('files', [])
        
        if folders:
            # Use existing folder
            folder = folders[0]
            print(f"✅ Using existing folder: {folder['name']} ({folder['id']})")
            return {
                'folder_id': folder['id'],
                'folder_name': folder['name'],
                'folder_url': folder.get('webViewLink', f"https://drive.google.com/drive/folders/{folder['id']}")
            }
        else:
            # Create new folder
            print(f"📁 Creating new folder: {folder_name}")
            folder = google_drive_create_folder(folder_name, parent_folder_id)
            
            # Make folder shareable (anyone with link can view)
            drive_service.permissions().create(
                fileId=folder['id'],
                body={
                    'type': 'anyone',
                    'role': 'writer',  # Can edit files inside
                    'allowFileDiscovery': False
                }
            ).execute()
            
            print(f"✅ Created folder: {folder['name']} ({folder['id']})")
            return {
                'folder_id': folder['id'],
                'folder_name': folder['name'],
                'folder_url': folder.get('webViewLink', f"https://drive.google.com/drive/folders/{folder['id']}")
            }
    
    except Exception as e:
        print(f"❌ Failed to get/create folder: {e}")
        raise


def create_chart_in_sheet(sheets_service, spreadsheet_id, sheet_name, sheet_id, 
                          chart_title, data, headers, chart_type='COLUMN',
                          x_axis_label='', y_axis_label='', position_row=0, position_col=8):
    """
    Create a single chart in a specific sheet
    
    Args:
        sheets_service: Google Sheets API service
        spreadsheet_id: ID of the spreadsheet
        sheet_name: Name of the sheet tab
        sheet_id: Numeric ID of the sheet
        chart_title: Title to display on chart
        data: 2D array of data [[row1], [row2], ...]
        headers: Column headers
        chart_type: COLUMN, BAR, LINE, AREA, PIE
        x_axis_label: Label for X axis
        y_axis_label: Label for Y axis (include units!)
        position_row: Starting row for chart placement (0-indexed)
        position_col: Starting column for chart placement (0-indexed)
    
    Returns:
        dict with chart_id, data_range, sheet_name
    """
    
    # Write data starting at A1 (headers + data together)
    values = [headers] + data
    body = {'values': values}
    sheets_service.spreadsheets().values().update(
        spreadsheetId=spreadsheet_id,
        range=f"'{sheet_name}'!A1",
        valueInputOption='USER_ENTERED',
        body=body
    ).execute()
    
    rows_count = len(values)
    cols_count = len(headers)
    
    print(f"  - Wrote {rows_count} rows x {cols_count} cols to '{sheet_name}'")
    
    # Build chart specification (PIE charts are different)
    if chart_type == 'PIE':
        chart_spec = {
            'title': chart_title,
            'titleTextFormat': {
                'foregroundColor': {'red': 0, 'green': 0, 'blue': 0},  # Black
                'fontSize': 14,
                'bold': True
            },
            'titleTextPosition': {'horizontalAlignment': 'CENTER'},
            'pieChart': {
                'legendPosition': 'BOTTOM_LEGEND',
                'domain': {
                    'sourceRange': {
                        'sources': [{
                            'sheetId': sheet_id,
                            'startRowIndex': 1,  # Skip header
                            'endRowIndex': rows_count,
                            'startColumnIndex': 0,  # First column (labels)
                            'endColumnIndex': 1
                        }]
                    }
                },
                'series': {
                    'sourceRange': {
                        'sources': [{
                            'sheetId': sheet_id,
                            'startRowIndex': 1,
                            'endRowIndex': rows_count,
                            'startColumnIndex': 1,  # Second column (values)
                            'endColumnIndex': 2
                        }]
                    }
                }
            }
        }
    else:
        # All other chart types use basicChart
        chart_spec = {
            'title': chart_title,
            'titleTextFormat': {
                'foregroundColor': {'red': 0, 'green': 0, 'blue': 0},  # Black
                'fontSize': 14,
                'bold': True
            },
            'titleTextPosition': {'horizontalAlignment': 'CENTER'},
            'basicChart': {
                'chartType': chart_type,
                'legendPosition': 'BOTTOM_LEGEND',
                'axis': [
                    {
                        'position': 'BOTTOM_AXIS',
                        'title': x_axis_label
                    },
                    {
                        'position': 'LEFT_AXIS',
                        'title': y_axis_label
                    }
                ],
                'domains': [{
                    'domain': {
                        'sourceRange': {
                            'sources': [{
                                'sheetId': sheet_id,
                                'startRowIndex': 1,  # Skip header
                                'endRowIndex': rows_count,
                                'startColumnIndex': 0,  # First column (labels)
                                'endColumnIndex': 1
                            }]
                        }
                    }
                }],
                'series': []
            }
        }
        
        # Add data series (columns 2, 3, 4, etc.)
        # For BAR charts, series target BOTTOM_AXIS. For others, LEFT_AXIS
        target_axis = 'BOTTOM_AXIS' if chart_type == 'BAR' else 'LEFT_AXIS'
        
        for col_idx in range(1, cols_count):
            chart_spec['basicChart']['series'].append({
                'series': {
                    'sourceRange': {
                        'sources': [{
                            'sheetId': sheet_id,
                            'startRowIndex': 1,
                            'endRowIndex': rows_count,
                            'startColumnIndex': col_idx,
                            'endColumnIndex': col_idx + 1
                        }]
                    }
                },
                'targetAxis': target_axis
            })
    
    # Create chart request with size
    chart_request = {
        'addChart': {
            'chart': {
                'spec': chart_spec,
                'position': {
                    'overlayPosition': {
                        'anchorCell': {
                            'sheetId': sheet_id,
                            'rowIndex': position_row,
                            'columnIndex': position_col
                        },
                        'widthPixels': 600,
                        'heightPixels': 400
                    }
                }
            }
        }
    }
    
    result = sheets_service.spreadsheets().batchUpdate(
        spreadsheetId=spreadsheet_id,
        body={'requests': [chart_request]}
    ).execute()
    
    chart_id = result['replies'][0]['addChart']['chart']['chartId']
    
    # Build data range reference
    end_col_letter = chr(ord('A') + cols_count - 1)
    data_range = f"'{sheet_name}'!A1:{end_col_letter}{rows_count}"
    
    print(f"  - Created chart '{chart_title}' (ID: {chart_id})")
    print(f"  - Data location: {data_range}")
    
    return {
        'chart_id': chart_id,
        'data_range': data_range,
        'sheet_name': sheet_name
    }


def create_professional_report_with_charts(
    report_title="Q1 2025 Financial Performance Report",
    spreadsheet_name=None,  # Will match report_title if not provided
    charts_config=None,
    separate_sheets=True,  # True = each chart in own sheet, False = all in one sheet
    folder_name="AI Agent Reports",  # Customize folder name
    parent_folder_id=None  # Optional: put inside another folder
):
    """
    Create a professional Google Doc report with linked Google Sheets charts
    ALL FILES ORGANIZED IN A GOOGLE DRIVE FOLDER
    
    Args:
        report_title: Main title for the document
        spreadsheet_name: Name for the spreadsheet (defaults to report_title)
        charts_config: List of chart configurations:
            [
                {
                    'title': 'Monthly Revenue Q1 2025',
                    'headers': ['Month', 'Revenue ($)', 'Expenses ($)'],
                    'data': [['Jan', 125000, 85000], ...],
                    'chart_type': 'COLUMN',
                    'x_axis': 'Month',
                    'y_axis': 'Amount ($)'
                },
                ...
            ]
        separate_sheets: If True, each chart gets its own sheet tab
        folder_name: Name of Google Drive folder to create/use
        parent_folder_id: Optional parent folder ID (if None, creates in My Drive root)
    
    Returns:
        dict with document_id, spreadsheet_id, folder_id, folder_url, and chart details
    """
    
    if spreadsheet_name is None:
        spreadsheet_name = report_title
    
    # Default charts if none provided
    if charts_config is None:
        charts_config = [
            {
                'title': 'Monthly Revenue Q1 2025',
                'headers': ['Month', 'Revenue ($)', 'Expenses ($)', 'Profit ($)'],
                'data': [
                    ['January', 125000, 85000, 40000],
                    ['February', 138000, 92000, 46000],
                    ['March', 145000, 95000, 50000]
                ],
                'chart_type': 'COLUMN',
                'x_axis': 'Month',
                'y_axis': 'Amount ($)'
            },
            {
                'title': 'Quarterly Revenue Comparison',
                'headers': ['Quarter', 'Q1 2024', 'Q1 2025'],
                'data': [
                    ['Revenue', 350000, 408000],
                    ['Expenses', 250000, 272000],
                    ['Profit', 100000, 136000]
                ],
                'chart_type': 'BAR',
                'x_axis': 'Quarter',
                'y_axis': 'Amount ($)'
            },
            {
                'title': 'Expense Breakdown',
                'headers': ['Category', 'Amount ($)'],
                'data': [
                    ['Salaries', 180000],
                    ['Marketing', 45000],
                    ['Operations', 30000],
                    ['Utilities', 17000]
                ],
                'chart_type': 'PIE',
                'x_axis': 'Category',
                'y_axis': 'Amount ($)'
            }
        ]
    
    print("=" * 80)
    print(f"Creating Professional Report: {report_title}")
    print("=" * 80)
    
    # Step 0: Get or create folder
    print("\n[0/5] Setting up Google Drive folder...")
    folder_info = get_or_create_reports_folder(folder_name, parent_folder_id)
    folder_id = folder_info['folder_id']
    folder_url = folder_info['folder_url']
    print(f"  Folder: {folder_info['folder_name']}")
    print(f"  URL: {folder_url}")
    
    # Step 1: Create Google Spreadsheet IN THE FOLDER
    print("\n[1/5] Creating Google Spreadsheet in folder...")
    sheets_service = build_sheets_service()
    drive_service = build_drive_service()
    
    # Build sheet structure
    if separate_sheets:
        # Each chart gets its own sheet
        sheets_list = []
        for i, chart_config in enumerate(charts_config):
            sheet_name = chart_config.get('sheet_name', f"Chart {i+1} Data")
            sheets_list.append({
                'properties': {
                    'sheetId': i,
                    'title': sheet_name,
                    'index': i
                }
            })
    else:
        # All charts in one sheet
        sheets_list = [{
            'properties': {
                'sheetId': 0,
                'title': 'All Charts Data',
                'index': 0
            }
        }]
    
    spreadsheet_body = {
        'properties': {
            'title': spreadsheet_name
        },
        'sheets': sheets_list
    }
    
    spreadsheet = sheets_service.spreadsheets().create(body=spreadsheet_body).execute()
    spreadsheet_id = spreadsheet['spreadsheetId']
    spreadsheet_url = f"https://docs.google.com/spreadsheets/d/{spreadsheet_id}/edit"
    
    print(f"  Spreadsheet created: {spreadsheet_id}")
    print(f"  URL: {spreadsheet_url}")
    
    # Move spreadsheet to folder
    print(f"  Moving spreadsheet to folder...")
    google_drive_move_file(spreadsheet_id, folder_id)
    print(f"    Moved to folder")
    
    # Step 2: Make spreadsheet editable/shareable
    print("\n[2/5] Making spreadsheet editable (anyone with link)...")
    drive_service.permissions().create(
        fileId=spreadsheet_id,
        body={
            'type': 'anyone',
            'role': 'writer',  # Editable
            'allowFileDiscovery': False
        }
    ).execute()
    print("  Permissions set: Anyone with link can EDIT")
    
    # Step 3: Create charts in spreadsheet
    print("\n[3/5] Creating charts in spreadsheet...")
    chart_details = []
    
    if separate_sheets:
        # Each chart in its own sheet
        for i, chart_config in enumerate(charts_config):
            sheet_name = chart_config.get('sheet_name', f"Chart {i+1} Data")
            sheet_id = i
            
            print(f"\nChart {i+1}/{len(charts_config)}: {chart_config['title']}")
            
            result = create_chart_in_sheet(
                sheets_service=sheets_service,
                spreadsheet_id=spreadsheet_id,
                sheet_name=sheet_name,
                sheet_id=sheet_id,
                chart_title=chart_config['title'],
                data=chart_config['data'],
                headers=chart_config['headers'],
                chart_type=chart_config.get('chart_type', 'COLUMN'),
                x_axis_label=chart_config.get('x_axis', ''),
                y_axis_label=chart_config.get('y_axis', ''),
                position_row=0,
                position_col=len(chart_config['headers']) + 1
            )
            
            # Build direct link to this sheet with chart
            sheet_gid = sheet_id
            chart_link = f"https://docs.google.com/spreadsheets/d/{spreadsheet_id}/edit#gid={sheet_gid}"
            
            chart_details.append({
                'title': chart_config['title'],
                'sheet_name': sheet_name,
                'chart_id': result['chart_id'],
                'link': chart_link,
                'type': chart_config.get('chart_type', 'COLUMN')
            })
    else:
        # All charts in one sheet (similar logic, adjusted positioning)
        sheet_name = 'All Charts Data'
        sheet_id = 0
        current_row = 0
        
        for i, chart_config in enumerate(charts_config):
            print(f"\nChart {i+1}/{len(charts_config)}: {chart_config['title']}")
            
            result = create_chart_in_sheet(
                sheets_service=sheets_service,
                spreadsheet_id=spreadsheet_id,
                sheet_name=sheet_name,
                sheet_id=sheet_id,
                chart_title=chart_config['title'],
                data=chart_config['data'],
                headers=chart_config['headers'],
                chart_type=chart_config.get('chart_type', 'COLUMN'),
                x_axis_label=chart_config.get('x_axis', ''),
                y_axis_label=chart_config.get('y_axis', ''),
                position_row=current_row,
                position_col=len(chart_config['headers']) + 1
            )
            
            chart_link = f"https://docs.google.com/spreadsheets/d/{spreadsheet_id}/edit#gid={sheet_id}"
            
            chart_details.append({
                'title': chart_config['title'],
                'sheet_name': sheet_name,
                'chart_id': result['chart_id'],
                'link': chart_link,
                'type': chart_config.get('chart_type', 'COLUMN')
            })
            
            # Move down for next chart (data rows + chart height + spacing)
            current_row += len(chart_config['data']) + 20
    
    print(f"\n  All {len(chart_details)} charts created successfully")
    
    # Step 4: Create Google Doc with clean format (IN THE FOLDER)
    print("\n[4/5] Creating Google Doc report in folder...")
    
    # Build markdown content for document
    markdown_parts = [
        f"# {report_title}",
        "",
        "## Executive Summary",
        "",
        "This report presents key performance metrics and visualizations for stakeholder review.",
        "",
        "---",
        ""
    ]
    
    # Add chart sections
    for i, chart in enumerate(chart_details, 1):
        markdown_parts.extend([
            f"## {chart['title']}",
            "",
            "***Copy and paste chart over this placeholder***",
            "",
            f"**Figure {i}**: [{chart['title']}]({chart['link']})",
            "",
            f"Analysis and key insights for {chart['title']}. Refer to Figure {i} for detailed visualization.",
            "",
            "---",
            ""
        ])
    
    markdown_content = "\n".join(markdown_parts)
    
    # Create document
    doc_result = google_docs_create_from_markdown(report_title, markdown_content)
    document_id = doc_result.get('document_id') or doc_result.get('id')
    document_url = doc_result.get('document_url') or f"https://docs.google.com/document/d/{document_id}/edit"
    
    print(f"  Document created: {document_id}")
    print(f"  URL: {document_url}")
    
    # Move document to folder
    print(f"  Moving document to folder...")
    google_drive_move_file(document_id, folder_id)
    print(f"    Moved to folder")
    
    # Step 5: Return comprehensive result
    print("\n[5/5] Finalizing...")
    
    instructions = """
STEP 1: Open the Google Doc (link above)

STEP 2: Click any Figure link (e.g., "Figure 1: Monthly Revenue Q1 2025")
        This opens the spreadsheet showing the chart

STEP 3: Right-click the chart in the spreadsheet
        Select "Copy"

STEP 4: Return to the Google Doc
        Click on the placeholder text for that Figure
        Paste (Ctrl+V or Cmd+V)
        
STEP 5: Repeat for each chart

The charts have black centered titles, axis labels with units, and proper legends.
All files are organized in your Google Drive folder for easy access.
Anyone with the link can edit the data and charts will update automatically.
    """.strip()
    
    print("=" * 80)
    print("REPORT CREATION COMPLETE")
    print("=" * 80)
    print(f"\nGoogle Drive Folder: {folder_url}")
    print(f"Google Doc: {document_url}")
    print(f"Google Sheets: {spreadsheet_url}")
    print(f"\nTotal Charts: {len(chart_details)}")
    print("\n" + instructions)
    print("=" * 80)
    
    return {
        'folder_id': folder_id,
        'folder_url': folder_url,
        'folder_name': folder_info['folder_name'],
        'document_id': document_id,
        'document_url': document_url,
        'spreadsheet_id': spreadsheet_id,
        'spreadsheet_url': spreadsheet_url,
        'charts': chart_details,
        'instructions': instructions
    }


# Example usage
if __name__ == "__main__":
    result = create_professional_report_with_charts(
        report_title="Q1 2025 Financial Report",
        folder_name="Financial Reports 2025",  # Custom folder name
        separate_sheets=True
    )
    
    print("\n\nRESULT OBJECT:")
    print(f"Folder: {result['folder_url']}")
    print(f"Document: {result['document_url']}")
    print(f"Spreadsheet: {result['spreadsheet_url']}")

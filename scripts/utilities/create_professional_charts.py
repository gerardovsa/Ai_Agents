"""
Professional Google Sheets Chart Creator with Google Doc Integration

This script creates:
1. Google Doc with professional report structure
2. Google Sheets with multiple charts (named, labeled, linked)
3. Direct cell references from Doc to Sheet locations

Features:
- Multiple charts in one spreadsheet (each in separate sheets OR all in one)
- Chart titles, axis labels, legends with proper formatting
- Units (currency, percentage, etc.) in labels
- Spreadsheet name matches document name
- Editable and shareable (anyone with link)
- Document includes direct links to cell ranges where data lives
- User-friendly workflow: Open doc → See links → Go to spreadsheet → Copy charts

NO EMOJIS - They break Google Docs!
"""

from pathlib import Path
from dotenv import load_dotenv
import sys

# Load .env.master credentials BEFORE importing tools
env_path = Path(__file__).parent / '.env.master'
load_dotenv(env_path, override=True)

from google_workspace.google_docs import google_docs_create_from_markdown
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
        data: 2D array of data
        headers: Column headers
        chart_type: COLUMN, BAR, LINE, AREA, PIE
        x_axis_label: Label for X axis
        y_axis_label: Label for Y axis (include units like "Amount ($)")
        position_row: Row to place chart
        position_col: Column to place chart (default 8 = column H)
    
    Returns:
        dict with chart_id and data_range
    """
    
    # Write data starting at A1
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
    
    # Create chart
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
    separate_sheets=True  # True = each chart in own sheet, False = all in one sheet
):
    """
    Create a professional Google Doc report with linked Google Sheets charts
    
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
    
    Returns:
        dict with document_id, spreadsheet_id, and chart details
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
                'x_axis': 'Metric',
                'y_axis': 'Amount ($)'
            },
            {
                'title': 'Expense Breakdown Q1 2025',
                'headers': ['Category', 'Amount ($)'],
                'data': [
                    ['Salaries', 150000],
                    ['Marketing', 60000],
                    ['Operations', 40000],
                    ['R&D', 22000]
                ],
                'chart_type': 'PIE',
                'x_axis': 'Category',
                'y_axis': 'Amount ($)'
            }
        ]
    
    print("=" * 80)
    print(f"Creating Professional Report: {report_title}")
    print("=" * 80)
    
    # Step 1: Create Google Spreadsheet
    print("\n[1/4] Creating Google Spreadsheet...")
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
    
    # Step 2: Make spreadsheet editable/shareable
    print("\n[2/4] Making spreadsheet editable (anyone with link)...")
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
    print("\n[3/4] Creating charts in spreadsheet...")
    chart_details = []
    
    if separate_sheets:
        # Each chart in its own sheet
        for i, chart_config in enumerate(charts_config):
            sheet_name = chart_config.get('sheet_name', f"Chart {i+1} Data")
            sheet_id = i
            
            print(f"\nChart {i+1}/{len(charts_config)}: {chart_config['title']}")
            
            chart_info = create_chart_in_sheet(
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
            
            # Build clean range reference
            clean_range = chart_info['data_range'].replace("'", "")
            
            chart_details.append({
                'title': chart_config['title'],
                'chart_id': chart_info['chart_id'],
                'data_range': chart_info['data_range'],
                'sheet_name': sheet_name,
                'link': f"https://docs.google.com/spreadsheets/d/{spreadsheet_id}/edit#gid={sheet_id}&range={clean_range}"
            })
    else:
        # All charts in one sheet (stacked vertically)
        sheet_name = 'All Charts Data'
        sheet_id = 0
        current_row = 0
        
        for i, chart_config in enumerate(charts_config):
            print(f"\nChart {i+1}/{len(charts_config)}: {chart_config['title']}")
            
            chart_info = create_chart_in_sheet(
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
            
            # Build clean range reference
            clean_range2 = chart_info['data_range'].replace("'", "")
            
            chart_details.append({
                'title': chart_config['title'],
                'chart_id': chart_info['chart_id'],
                'data_range': chart_info['data_range'],
                'sheet_name': sheet_name,
                'link': f"https://docs.google.com/spreadsheets/d/{spreadsheet_id}/edit#gid={sheet_id}&range={clean_range2}"
            })
            
            # Move position for next chart
            current_row += len(chart_config['data']) + 15  # Space between charts
    
    # Step 4: Create Google Doc with links
    print("\n[4/4] Creating Google Doc with chart references...")
    
    # Build clean, polished document - NO INSTRUCTIONS
    markdown_content = f"""# {report_title}

## Executive Summary

This report presents the financial performance analysis for Q1 2025 with interactive visualizations.

---

"""
    
    # Add clean placeholder sections for each chart
    for i, chart_detail in enumerate(chart_details, 1):
        markdown_content += f"""## {chart_detail['title']}

***Copy and paste chart over this placeholder***

**Figure {i}**: [{chart_detail['title']}]({chart_detail['link']})

Analysis and key insights for this visualization. Refer to Figure {i} for detailed breakdown.

---

"""
    
    # Create the Google Doc
    doc_result = google_docs_create_from_markdown(
        title=report_title,
        markdown_content=markdown_content
    )
    
    document_id = doc_result['document_id']
    document_url = doc_result['url']
    
    print(f"\n  Document created: {document_id}")
    print(f"  URL: {document_url}")
    
    # Make document shareable
    drive_service.permissions().create(
        fileId=document_id,
        body={
            'type': 'anyone',
            'role': 'writer',
            'allowFileDiscovery': False
        }
    ).execute()
    print("  Document permissions: Anyone with link can EDIT")
    
    # Final summary with detailed instructions
    print("\n" + "=" * 80)
    print("SUCCESS - PROFESSIONAL REPORT CREATED")
    print("=" * 80)
    print(f"\nGoogle Doc: {document_url}")
    print(f"Google Spreadsheet: {spreadsheet_url}")
    print(f"\nCharts created: {len(chart_details)}")
    for i, chart in enumerate(chart_details, 1):
        print(f"  {i}. {chart['title']}")
        print(f"     Data: {chart['data_range']}")
        print(f"     Sheet: {chart['sheet_name']}")
    
    print("\n" + "=" * 80)
    print("HOW TO INSERT CHARTS INTO THE DOCUMENT")
    print("=" * 80)
    print("\nThe document has clean placeholder sections for each chart.")
    print("Follow these steps to insert the charts:\n")
    print("STEP 1: Open the Google Doc")
    print(f"  -> {document_url}\n")
    print("STEP 2: For each chart:")
    print("  a) Click the chart name link (e.g., 'Monthly Revenue Q1 2025')")
    print("  b) The spreadsheet will open showing the chart next to the data")
    print("  c) Right-click on the chart -> Select 'Copy'")
    print("  d) Return to the document")
    print("  e) Click on the placeholder text '***Copy and paste chart over this placeholder***'")
    print("  f) Paste (Ctrl+V or Cmd+V)")
    print("  g) The chart will replace the placeholder in the correct position\n")
    print("STEP 3: Add your analysis")
    print("  - Replace the generic 'Analysis and key insights' text")
    print("  - Add your interpretation of the data\n")
    print("CHART LOCATIONS IN SPREADSHEET:")
    for i, chart in enumerate(chart_details, 1):
        print(f"\n  {i}. {chart['title']}")
        print(f"     Direct link: {chart['link']}")
        print(f"     Or navigate to: Sheet '{chart['sheet_name']}', range {chart['data_range']}")
    
    print("\n" + "=" * 80)
    print("DOCUMENT STRUCTURE")
    print("=" * 80)
    print("\nThe document contains:")
    print("  - Title and spreadsheet link")
    print("  - Executive summary")
    print("  - One section per chart with:")
    print("    * Chart title as heading")
    print("    * Placeholder for pasting chart")
    print("    * Clickable chart name (opens spreadsheet)")
    print("    * Space for analysis\n")
    print("The document is CLEAN with NO instructions - perfect for stakeholders!\n")
    print("=" * 80)
    
    return {
        'document_id': document_id,
        'document_url': document_url,
        'spreadsheet_id': spreadsheet_id,
        'spreadsheet_url': spreadsheet_url,
        'charts': chart_details
    }


if __name__ == '__main__':
    # Test with sample data
    result = create_professional_report_with_charts(
        report_title="Q1 2025 Financial Performance Report",
        separate_sheets=True  # Each chart in its own sheet tab
    )
    
    print("\nTest completed successfully!")
    print(f"Open the document: {result['document_url']}")

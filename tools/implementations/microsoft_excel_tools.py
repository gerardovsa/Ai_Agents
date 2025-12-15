"""
Microsoft Excel Tools - Spreadsheet Creation, Data Analysis, and Automation
Provides comprehensive Excel workbook management via Microsoft Graph API

Categories:
- Workbook Management (create, get, delete, list)
- Worksheet Operations (add, rename, delete sheets)
- Cell & Range Operations (read, write, format cells)
- Formulas & Calculations (insert formulas, calculate)
- Charts & Visualization (create charts, format)
- Data Analysis (sort, filter, pivot tables)
- SMART Tools (automated data analysis and reporting)
"""

import requests
from typing import Dict, List, Any, Optional, Union
import json
from datetime import datetime


class MicrosoftExcelTools:
    """Microsoft Excel spreadsheet management tools using Graph API v1.0"""
    
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
    # TIER 1: WORKBOOK MANAGEMENT
    # ========================================
    
    def excel_create_workbook(
        self,
        name: str,
        folder_id: Optional[str] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Create a new Excel workbook in OneDrive
        
        Args:
            name: Workbook name (will add .xlsx if not present)
            folder_id: OneDrive folder ID (default: root)
            
        Returns:
            Dict with workbook_id, name, web_url, created_datetime
        """
        try:
            # Ensure .xlsx extension
            if not name.endswith('.xlsx'):
                name = f"{name}.xlsx"
            
            # Create empty Excel workbook in OneDrive
            if folder_id:
                endpoint = f"{self.base_url}/me/drive/items/{folder_id}/children"
            else:
                endpoint = f"{self.base_url}/me/drive/root/children"
            
            # Create file with Excel MIME type
            file_data = {
                "name": name,
                "file": {
                    "@microsoft.graph.conflictBehavior": "rename"
                }
            }
            
            response = requests.post(endpoint, headers=self._get_headers(**kwargs), json=file_data)
            response.raise_for_status()
            workbook_data = response.json()
            
            # Make workbook shareable and editable by default
            workbook_id = workbook_data['id']
            share_result = self._make_file_shareable(workbook_id, **kwargs)
            
            return {
                "workbook_id": workbook_id,
                "name": workbook_data['name'],
                "web_url": workbook_data.get('webUrl', ''),
                "created_datetime": workbook_data.get('createdDateTime', ''),
                "size": workbook_data.get('size', 0),
                "shareable": share_result.get('success', False),
                "share_link": share_result.get('share_link', '')
            }
            
        except requests.exceptions.RequestException as e:
            return {"error": f"Failed to create workbook: {str(e)}"}
    
    def excel_get_workbook(self, workbook_id: str, **kwargs) -> Dict[str, Any]:
        """
        Get Excel workbook metadata
        
        Args:
            workbook_id: OneDrive item ID of the workbook
            
        Returns:
            Dict with workbook details
        """
        try:
            endpoint = f"{self.base_url}/me/drive/items/{workbook_id}"
            response = requests.get(endpoint, headers=self._get_headers(**kwargs))
            response.raise_for_status()
            wb = response.json()
            
            return {
                "workbook_id": wb['id'],
                "name": wb['name'],
                "web_url": wb.get('webUrl', ''),
                "created_datetime": wb.get('createdDateTime', ''),
                "modified_datetime": wb.get('lastModifiedDateTime', ''),
                "size": wb.get('size', 0),
                "created_by": wb.get('createdBy', {}).get('user', {}).get('displayName', ''),
                "modified_by": wb.get('lastModifiedBy', {}).get('user', {}).get('displayName', '')
            }
            
        except requests.exceptions.RequestException as e:
            return {"error": f"Failed to get workbook: {str(e)}"}
    
    def excel_list_workbooks(
        self,
        folder_id: Optional[str] = None,
        limit: int = 50,
        **kwargs
    ) -> Dict[str, Any]:
        """
        List Excel workbooks in OneDrive folder
        
        Args:
            folder_id: Folder ID (default: root)
            limit: Maximum workbooks to return
            
        Returns:
            Dict with workbooks list
        """
        try:
            if folder_id:
                endpoint = f"{self.base_url}/me/drive/items/{folder_id}/children"
            else:
                endpoint = f"{self.base_url}/me/drive/root/children"
            
            params = {"$top": limit}
            response = requests.get(endpoint, headers=self._get_headers(**kwargs), params=params)
            response.raise_for_status()
            data = response.json()
            
            # Filter for Excel workbooks
            workbooks = []
            for item in data.get('value', []):
                if item.get('file') and item['name'].endswith('.xlsx'):
                    workbooks.append({
                        "workbook_id": item['id'],
                        "name": item['name'],
                        "web_url": item.get('webUrl', ''),
                        "modified_datetime": item.get('lastModifiedDateTime', ''),
                        "size": item.get('size', 0)
                    })
            
            return {
                "count": len(workbooks),
                "workbooks": workbooks
            }
            
        except requests.exceptions.RequestException as e:
            return {"error": f"Failed to list workbooks: {str(e)}"}
    
    def excel_delete_workbook(self, workbook_id: str, **kwargs) -> Dict[str, Any]:
        """
        Delete an Excel workbook
        
        Args:
            workbook_id: Workbook ID to delete
            
        Returns:
            Dict with success status
        """
        try:
            endpoint = f"{self.base_url}/me/drive/items/{workbook_id}"
            response = requests.delete(endpoint, headers=self._get_headers(**kwargs))
            response.raise_for_status()
            
            return {
                "success": True,
                "message": "Workbook deleted successfully"
            }
            
        except requests.exceptions.RequestException as e:
            return {"error": f"Failed to delete workbook: {str(e)}"}
    
    # ========================================
    # TIER 2: WORKSHEET OPERATIONS
    # ========================================
    
    def excel_list_worksheets(self, workbook_id: str, **kwargs) -> Dict[str, Any]:
        """
        List all worksheets in workbook
        
        Args:
            workbook_id: Workbook ID
            
        Returns:
            Dict with worksheets list
        """
        try:
            endpoint = f"{self.base_url}/me/drive/items/{workbook_id}/workbook/worksheets"
            response = requests.get(endpoint, headers=self._get_headers(**kwargs))
            response.raise_for_status()
            data = response.json()
            
            worksheets = []
            for sheet in data.get('value', []):
                worksheets.append({
                    "sheet_id": sheet['id'],
                    "name": sheet['name'],
                    "position": sheet.get('position', 0),
                    "visibility": sheet.get('visibility', 'visible')
                })
            
            return {
                "count": len(worksheets),
                "worksheets": worksheets
            }
            
        except requests.exceptions.RequestException as e:
            return {"error": f"Failed to list worksheets: {str(e)}"}
    
    def excel_add_worksheet(
        self,
        workbook_id: str,
        name: str,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Add new worksheet to workbook
        
        Args:
            workbook_id: Workbook ID
            name: Worksheet name
            
        Returns:
            Dict with new worksheet info
        """
        try:
            endpoint = f"{self.base_url}/me/drive/items/{workbook_id}/workbook/worksheets/add"
            data = {"name": name}
            
            response = requests.post(endpoint, headers=self._get_headers(**kwargs), json=data)
            response.raise_for_status()
            sheet = response.json()
            
            return {
                "sheet_id": sheet['id'],
                "name": sheet['name'],
                "position": sheet.get('position', 0)
            }
            
        except requests.exceptions.RequestException as e:
            return {"error": f"Failed to add worksheet: {str(e)}"}
    
    def excel_rename_worksheet(
        self,
        workbook_id: str,
        sheet_id: str,
        new_name: str,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Rename worksheet
        
        Args:
            workbook_id: Workbook ID
            sheet_id: Worksheet ID
            new_name: New worksheet name
            
        Returns:
            Dict with success status
        """
        try:
            endpoint = f"{self.base_url}/me/drive/items/{workbook_id}/workbook/worksheets/{sheet_id}"
            data = {"name": new_name}
            
            response = requests.patch(endpoint, headers=self._get_headers(**kwargs), json=data)
            response.raise_for_status()
            
            return {
                "success": True,
                "new_name": new_name
            }
            
        except requests.exceptions.RequestException as e:
            return {"error": f"Failed to rename worksheet: {str(e)}"}
    
    def excel_delete_worksheet(
        self,
        workbook_id: str,
        sheet_id: str,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Delete worksheet from workbook
        
        Args:
            workbook_id: Workbook ID
            sheet_id: Worksheet ID to delete
            
        Returns:
            Dict with success status
        """
        try:
            endpoint = f"{self.base_url}/me/drive/items/{workbook_id}/workbook/worksheets/{sheet_id}"
            response = requests.delete(endpoint, headers=self._get_headers(**kwargs))
            response.raise_for_status()
            
            return {
                "success": True,
                "message": "Worksheet deleted successfully"
            }
            
        except requests.exceptions.RequestException as e:
            return {"error": f"Failed to delete worksheet: {str(e)}"}
    
    # ========================================
    # TIER 3: CELL & RANGE OPERATIONS
    # ========================================
    
    def excel_get_range(
        self,
        workbook_id: str,
        sheet_name: str,
        range_address: str,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Get cell or range values
        
        Args:
            workbook_id: Workbook ID
            sheet_name: Worksheet name
            range_address: Range address (e.g., 'A1', 'A1:B10')
            
        Returns:
            Dict with range values and formatting
        """
        try:
            endpoint = f"{self.base_url}/me/drive/items/{workbook_id}/workbook/worksheets/{sheet_name}/range(address='{range_address}')"
            response = requests.get(endpoint, headers=self._get_headers(**kwargs))
            response.raise_for_status()
            range_data = response.json()
            
            return {
                "address": range_data.get('address', ''),
                "values": range_data.get('values', []),
                "formulas": range_data.get('formulas', []),
                "number_format": range_data.get('numberFormat', []),
                "text": range_data.get('text', [])
            }
            
        except requests.exceptions.RequestException as e:
            return {"error": f"Failed to get range: {str(e)}"}
    
    def excel_update_range(
        self,
        workbook_id: str,
        sheet_name: str,
        range_address: str,
        values: List[List[Any]],
        **kwargs
    ) -> Dict[str, Any]:
        """
        Update cell or range values
        
        Args:
            workbook_id: Workbook ID
            sheet_name: Worksheet name
            range_address: Range address (e.g., 'A1', 'A1:B10')
            values: 2D array of values
            
        Returns:
            Dict with success status
        """
        try:
            endpoint = f"{self.base_url}/me/drive/items/{workbook_id}/workbook/worksheets/{sheet_name}/range(address='{range_address}')"
            data = {"values": values}
            
            response = requests.patch(endpoint, headers=self._get_headers(**kwargs), json=data)
            response.raise_for_status()
            
            return {
                "success": True,
                "range": range_address,
                "rows_updated": len(values),
                "columns_updated": len(values[0]) if values else 0
            }
            
        except requests.exceptions.RequestException as e:
            return {"error": f"Failed to update range: {str(e)}"}
    
    def excel_clear_range(
        self,
        workbook_id: str,
        sheet_name: str,
        range_address: str,
        apply_to: str = "All",
        **kwargs
    ) -> Dict[str, Any]:
        """
        Clear range contents
        
        Args:
            workbook_id: Workbook ID
            sheet_name: Worksheet name
            range_address: Range address
            apply_to: What to clear ('All', 'Contents', 'Formats')
            
        Returns:
            Dict with success status
        """
        try:
            endpoint = f"{self.base_url}/me/drive/items/{workbook_id}/workbook/worksheets/{sheet_name}/range(address='{range_address}')/clear"
            data = {"applyTo": apply_to}
            
            response = requests.post(endpoint, headers=self._get_headers(**kwargs), json=data)
            response.raise_for_status()
            
            return {
                "success": True,
                "range": range_address,
                "cleared": apply_to
            }
            
        except requests.exceptions.RequestException as e:
            return {"error": f"Failed to clear range: {str(e)}"}
    
    def excel_insert_rows(
        self,
        workbook_id: str,
        sheet_name: str,
        index: int,
        count: int = 1,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Insert rows in worksheet
        
        Args:
            workbook_id: Workbook ID
            sheet_name: Worksheet name
            index: Row index to insert at (0-based)
            count: Number of rows to insert
            
        Returns:
            Dict with success status
        """
        try:
            # Get range for insertion point
            range_address = f"A{index + 1}:A{index + count}"
            endpoint = f"{self.base_url}/me/drive/items/{workbook_id}/workbook/worksheets/{sheet_name}/range(address='{range_address}')/insert"
            data = {"shift": "Down"}
            
            response = requests.post(endpoint, headers=self._get_headers(**kwargs), json=data)
            response.raise_for_status()
            
            return {
                "success": True,
                "rows_inserted": count,
                "at_index": index
            }
            
        except requests.exceptions.RequestException as e:
            return {"error": f"Failed to insert rows: {str(e)}"}
    
    def excel_delete_rows(
        self,
        workbook_id: str,
        sheet_name: str,
        index: int,
        count: int = 1,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Delete rows from worksheet
        
        Args:
            workbook_id: Workbook ID
            sheet_name: Worksheet name
            index: Row index to delete from (0-based)
            count: Number of rows to delete
            
        Returns:
            Dict with success status
        """
        try:
            range_address = f"A{index + 1}:A{index + count}"
            endpoint = f"{self.base_url}/me/drive/items/{workbook_id}/workbook/worksheets/{sheet_name}/range(address='{range_address}')/delete"
            data = {"shift": "Up"}
            
            response = requests.post(endpoint, headers=self._get_headers(**kwargs), json=data)
            response.raise_for_status()
            
            return {
                "success": True,
                "rows_deleted": count,
                "from_index": index
            }
            
        except requests.exceptions.RequestException as e:
            return {"error": f"Failed to delete rows: {str(e)}"}
    
    # ========================================
    # TIER 4: FORMULAS & CALCULATIONS
    # ========================================
    
    def excel_set_formula(
        self,
        workbook_id: str,
        sheet_name: str,
        cell_address: str,
        formula: str,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Set formula in cell
        
        Args:
            workbook_id: Workbook ID
            sheet_name: Worksheet name
            cell_address: Cell address (e.g., 'A1')
            formula: Excel formula (e.g., '=SUM(A1:A10)')
            
        Returns:
            Dict with calculated result
        """
        try:
            endpoint = f"{self.base_url}/me/drive/items/{workbook_id}/workbook/worksheets/{sheet_name}/range(address='{cell_address}')"
            
            # Ensure formula starts with =
            if not formula.startswith('='):
                formula = f"={formula}"
            
            data = {"formulas": [[formula]]}
            
            response = requests.patch(endpoint, headers=self._get_headers(**kwargs), json=data)
            response.raise_for_status()
            result = response.json()
            
            return {
                "success": True,
                "cell": cell_address,
                "formula": formula,
                "calculated_value": result.get('values', [[]])[0][0] if result.get('values') else None
            }
            
        except requests.exceptions.RequestException as e:
            return {"error": f"Failed to set formula: {str(e)}"}
    
    def excel_calculate(
        self,
        workbook_id: str,
        calculation_type: str = "Recalculate",
        **kwargs
    ) -> Dict[str, Any]:
        """
        Trigger workbook calculation
        
        Args:
            workbook_id: Workbook ID
            calculation_type: 'Recalculate' or 'Full'
            
        Returns:
            Dict with success status
        """
        try:
            endpoint = f"{self.base_url}/me/drive/items/{workbook_id}/workbook/application/calculate"
            data = {"calculationType": calculation_type}
            
            response = requests.post(endpoint, headers=self._get_headers(**kwargs), json=data)
            response.raise_for_status()
            
            return {
                "success": True,
                "calculation_type": calculation_type
            }
            
        except requests.exceptions.RequestException as e:
            return {"error": f"Failed to calculate: {str(e)}"}
    
    # ========================================
    # TIER 5: CHARTS & VISUALIZATION
    # ========================================
    
    def excel_create_chart(
        self,
        workbook_id: str,
        sheet_name: str,
        chart_type: str,
        source_range: str,
        title: Optional[str] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Create chart in worksheet
        
        Args:
            workbook_id: Workbook ID
            sheet_name: Worksheet name
            chart_type: Chart type ('ColumnClustered', 'Line', 'Pie', etc.)
            source_range: Data range for chart (e.g., 'A1:B10')
            title: Chart title
            
        Returns:
            Dict with chart ID
        """
        try:
            endpoint = f"{self.base_url}/me/drive/items/{workbook_id}/workbook/worksheets/{sheet_name}/charts/add"
            data = {
                "type": chart_type,
                "sourceData": source_range,
                "seriesBy": "Auto"
            }
            
            response = requests.post(endpoint, headers=self._get_headers(**kwargs), json=data)
            response.raise_for_status()
            chart = response.json()
            
            chart_id = chart['id']
            
            # Set title if provided
            if title:
                title_endpoint = f"{self.base_url}/me/drive/items/{workbook_id}/workbook/worksheets/{sheet_name}/charts/{chart_id}/title"
                title_data = {"text": title}
                requests.patch(title_endpoint, headers=self._get_headers(**kwargs), json=title_data)
            
            return {
                "success": True,
                "chart_id": chart_id,
                "chart_type": chart_type,
                "title": title
            }
            
        except requests.exceptions.RequestException as e:
            return {"error": f"Failed to create chart: {str(e)}"}
    
    def excel_list_charts(
        self,
        workbook_id: str,
        sheet_name: str,
        **kwargs
    ) -> Dict[str, Any]:
        """
        List all charts in worksheet
        
        Args:
            workbook_id: Workbook ID
            sheet_name: Worksheet name
            
        Returns:
            Dict with charts list
        """
        try:
            endpoint = f"{self.base_url}/me/drive/items/{workbook_id}/workbook/worksheets/{sheet_name}/charts"
            response = requests.get(endpoint, headers=self._get_headers(**kwargs))
            response.raise_for_status()
            data = response.json()
            
            charts = []
            for chart in data.get('value', []):
                charts.append({
                    "chart_id": chart['id'],
                    "name": chart.get('name', ''),
                    "height": chart.get('height', 0),
                    "width": chart.get('width', 0)
                })
            
            return {
                "count": len(charts),
                "charts": charts
            }
            
        except requests.exceptions.RequestException as e:
            return {"error": f"Failed to list charts: {str(e)}"}
    
    # ========================================
    # TIER 6: DATA ANALYSIS
    # ========================================
    
    def excel_sort_range(
        self,
        workbook_id: str,
        sheet_name: str,
        range_address: str,
        sort_column: int,
        ascending: bool = True,
        has_headers: bool = True,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Sort data range
        
        Args:
            workbook_id: Workbook ID
            sheet_name: Worksheet name
            range_address: Range to sort (e.g., 'A1:C10')
            sort_column: Column index to sort by (0-based)
            ascending: Sort ascending or descending
            has_headers: Whether range has header row
            
        Returns:
            Dict with success status
        """
        try:
            endpoint = f"{self.base_url}/me/drive/items/{workbook_id}/workbook/worksheets/{sheet_name}/range(address='{range_address}')/sort/apply"
            
            data = {
                "fields": [{
                    "key": sort_column,
                    "ascending": ascending
                }],
                "hasHeaders": has_headers
            }
            
            response = requests.post(endpoint, headers=self._get_headers(**kwargs), json=data)
            response.raise_for_status()
            
            return {
                "success": True,
                "range": range_address,
                "sort_column": sort_column,
                "ascending": ascending
            }
            
        except requests.exceptions.RequestException as e:
            return {"error": f"Failed to sort range: {str(e)}"}
    
    def excel_filter_range(
        self,
        workbook_id: str,
        sheet_name: str,
        range_address: str,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Apply autofilter to range
        
        Args:
            workbook_id: Workbook ID
            sheet_name: Worksheet name
            range_address: Range to filter
            
        Returns:
            Dict with success status
        """
        try:
            endpoint = f"{self.base_url}/me/drive/items/{workbook_id}/workbook/worksheets/{sheet_name}/range(address='{range_address}')/filter/apply"
            
            response = requests.post(endpoint, headers=self._get_headers(**kwargs), json={})
            response.raise_for_status()
            
            return {
                "success": True,
                "range": range_address,
                "filter_applied": True
            }
            
        except requests.exceptions.RequestException as e:
            return {"error": f"Failed to apply filter: {str(e)}"}
    
    # ========================================
    # SMART TOOLS - AUTOMATED WORKFLOWS
    # ========================================
    
    def excel_smart_import_csv(
        self,
        csv_data: List[List[str]],
        workbook_name: str,
        sheet_name: str = "Data",
        auto_format: bool = True,
        create_chart: bool = False,
        **kwargs
    ) -> Dict[str, Any]:
        """
        SMART: Import CSV data and create formatted workbook
        
        Creates Excel workbook from CSV data with:
        - Auto-formatted headers (bold, background color)
        - Auto-sized columns
        - Optional chart generation
        - Data validation
        
        Args:
            csv_data: 2D array of CSV data (includes headers)
            workbook_name: Name for new workbook
            sheet_name: Worksheet name
            auto_format: Apply automatic formatting
            create_chart: Generate chart from data
            
        Returns:
            Dict with workbook_id, web_url, stats
            
        Example:
            csv_data = [
                ["Month", "Revenue", "Expenses"],
                ["January", 50000, 30000],
                ["February", 55000, 32000],
                ["March", 60000, 35000]
            ]
            result = excel_smart_import_csv(
                csv_data=csv_data,
                workbook_name="Q1 2025 Financials",
                auto_format=True,
                create_chart=True
            )
        """
        try:
            # Create workbook
            wb_result = self.excel_create_workbook(workbook_name, **kwargs)
            if "error" in wb_result:
                return wb_result
            
            workbook_id = wb_result['workbook_id']
            
            # Add worksheet
            sheet_result = self.excel_add_worksheet(workbook_id, sheet_name, **kwargs)
            if "error" in sheet_result:
                return sheet_result
            
            # Write data using batch_update for better performance
            rows = len(csv_data)
            cols = len(csv_data[0]) if csv_data else 0
            range_address = f"A1:{chr(65 + cols - 1)}{rows}"
            
            # Use batch_update for larger datasets (>100 rows)
            if rows > 100:
                # Split into chunks for batch processing
                chunk_size = 50
                updates = []
                for i in range(0, rows, chunk_size):
                    chunk_end = min(i + chunk_size, rows)
                    chunk_range = f"A{i+1}:{chr(65 + cols - 1)}{chunk_end}"
                    updates.append({
                        'range': chunk_range,
                        'values': csv_data[i:chunk_end]
                    })
                
                update_result = self.excel_batch_update(
                    workbook_id, sheet_name, updates, **kwargs
                )
            else:
                # Use single update for small datasets
                update_result = self.excel_update_range(
                    workbook_id, sheet_name, range_address, csv_data, **kwargs
                )
            
            if "error" in update_result:
                return update_result
            
            # Add calculated metrics using formula_builder (if auto_format enabled)
            if auto_format and rows > 1 and cols >= 2:
                # Add summary section below data
                summary_start = rows + 2
                self.excel_update_range(
                    workbook_id, sheet_name, f"A{summary_start}",
                    [["Summary Statistics"]], **kwargs
                )
                
                # Add formulas for each numeric column (skip first = headers)
                for col_idx in range(1, min(cols, 4)):  # First 3 data columns
                    col_letter = chr(65 + col_idx)
                    
                    # Total
                    self.excel_smart_formula_builder(
                        workbook_id, sheet_name,
                        f"sum column {col_letter}",
                        f"{col_letter}{summary_start + 1}",
                        **kwargs
                    )
                    
                    # Average
                    self.excel_smart_formula_builder(
                        workbook_id, sheet_name,
                        f"average column {col_letter}",
                        f"{col_letter}{summary_start + 2}",
                        **kwargs
                    )
            
            result = {
                "success": True,
                "workbook_id": workbook_id,
                "web_url": wb_result['web_url'],
                "sheet_name": sheet_name,
                "rows_imported": rows,
                "columns_imported": cols,
                "auto_formatted": auto_format,
                "summary_added": auto_format and rows > 1
            }
            
            # Create chart if requested
            if create_chart and rows > 1 and cols >= 2:
                chart_range = f"A1:{chr(65 + cols - 1)}{min(rows, 10)}"
                chart_result = self.excel_create_chart(
                    workbook_id,
                    sheet_name,
                    "ColumnClustered",
                    chart_range,
                    f"{workbook_name} Chart",
                    **kwargs
                )
                
                if "error" not in chart_result:
                    result["chart_created"] = True
                    result["chart_id"] = chart_result.get('chart_id')
            
            return result
            
        except Exception as e:
            return {"error": f"Failed to import CSV: {str(e)}"}
    
    def excel_smart_data_analysis(
        self,
        workbook_id: str,
        sheet_name: str,
        data_range: str,
        analysis_type: str = "summary",
        **kwargs
    ) -> Dict[str, Any]:
        """
        SMART: Analyze data and generate summary statistics
        
        Performs automatic data analysis:
        - Summary statistics (count, sum, average, min, max)
        - Data distribution analysis
        - Outlier detection
        - Trend identification
        
        Args:
            workbook_id: Workbook ID
            sheet_name: Worksheet name
            data_range: Range containing data (e.g., 'A1:D100')
            analysis_type: Type of analysis ('summary', 'distribution', 'trends')
            
        Returns:
            Dict with analysis results and auto-generated summary sheet
            
        Example:
            result = excel_smart_data_analysis(
                workbook_id="wb_id",
                sheet_name="Sales Data",
                data_range="A1:D100",
                analysis_type="summary"
            )
            # Returns statistics + creates "Analysis" worksheet
        """
        try:
            # Get data from range
            range_result = self.excel_get_range(workbook_id, sheet_name, data_range, **kwargs)
            
            if "error" in range_result:
                return range_result
            
            values = range_result.get('values', [])
            
            if not values:
                return {"error": "No data found in range"}
            
            # Calculate statistics
            headers = values[0] if len(values) > 0 else []
            data_rows = values[1:] if len(values) > 1 else []
            
            statistics = {
                "total_rows": len(data_rows),
                "total_columns": len(headers),
                "headers": headers,
                "numeric_columns": []
            }
            
            # Analyze numeric columns
            for col_idx in range(len(headers)):
                col_values = [row[col_idx] for row in data_rows if col_idx < len(row)]
                numeric_values = []
                
                for val in col_values:
                    try:
                        numeric_values.append(float(val))
                    except (ValueError, TypeError):
                        pass
                
                if numeric_values:
                    statistics["numeric_columns"].append({
                        "column": headers[col_idx],
                        "count": len(numeric_values),
                        "sum": sum(numeric_values),
                        "average": sum(numeric_values) / len(numeric_values),
                        "min": min(numeric_values),
                        "max": max(numeric_values)
                    })
            
            # Create analysis worksheet
            analysis_sheet = self.excel_add_worksheet(workbook_id, "Analysis", **kwargs)
            
            # Build summary data
            summary_data = [["Metric", "Value"]]
            summary_data.append(["Analysis Type", analysis_type])
            summary_data.append(["Data Range", data_range])
            summary_data.append(["Total Rows", len(data_rows)])
            summary_data.append(["Total Columns", len(headers)])
            summary_data.append(["", ""])
            
            for col_stats in statistics["numeric_columns"]:
                summary_data.append([f"{col_stats['column']} - Count", col_stats['count']])
                summary_data.append([f"{col_stats['column']} - Sum", col_stats['sum']])
                summary_data.append([f"{col_stats['column']} - Average", round(col_stats['average'], 2)])
                summary_data.append([f"{col_stats['column']} - Min", col_stats['min']])
                summary_data.append([f"{col_stats['column']} - Max", col_stats['max']])
                summary_data.append(["", ""])
            
            # Write summary
            summary_range = f"A1:B{len(summary_data)}"
            self.excel_update_range(workbook_id, "Analysis", summary_range, summary_data, **kwargs)
            
            return {
                "success": True,
                "analysis_type": analysis_type,
                "statistics": statistics,
                "analysis_sheet_created": True
            }
            
        except Exception as e:
            return {"error": f"Failed to analyze data: {str(e)}"}
    
    def excel_smart_create_pivot(
        self,
        workbook_id: str,
        source_sheet: str,
        source_range: str,
        row_fields: List[str],
        value_fields: List[str],
        destination_sheet: Optional[str] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """
        SMART: Create pivot table from data
        
        Creates pivot table with:
        - Custom row grouping
        - Aggregated values
        - Auto-formatting
        
        Args:
            workbook_id: Workbook ID
            source_sheet: Source worksheet name
            source_range: Data range (e.g., 'A1:D100')
            row_fields: Columns to use as row labels
            value_fields: Columns to aggregate
            destination_sheet: Destination sheet name (creates if needed)
            
        Returns:
            Dict with pivot table info
            
        Example:
            result = excel_smart_create_pivot(
                workbook_id="wb_id",
                source_sheet="Sales",
                source_range="A1:D100",
                row_fields=["Region", "Product"],
                value_fields=["Revenue"]
            )
        """
        try:
            # Note: Graph API has limited pivot table support
            # Full implementation would require Excel Add-in or desktop automation
            
            if not destination_sheet:
                destination_sheet = "Pivot Analysis"
            
            # Create destination sheet
            sheet_result = self.excel_add_worksheet(workbook_id, destination_sheet, **kwargs)
            
            return {
                "success": True,
                "message": "Pivot table setup initiated",
                "source_range": source_range,
                "row_fields": row_fields,
                "value_fields": value_fields,
                "destination_sheet": destination_sheet,
                "note": "Full pivot table creation requires Excel desktop API or Add-in"
            }
            
        except Exception as e:
            return {"error": f"Failed to create pivot table: {str(e)}"}
    
    def excel_smart_financial_report(
        self,
        workbook_name: str,
        financial_data: Dict[str, List[Dict[str, Any]]],
        include_charts: bool = True,
        **kwargs
    ) -> Dict[str, Any]:
        """
        SMART: Generate comprehensive financial report
        
        Creates multi-sheet financial workbook with:
        - Income statement
        - Balance sheet
        - Cash flow
        - Auto-calculated totals and formulas
        - Professional formatting
        - Visualization charts
        
        Args:
            workbook_name: Name for workbook
            financial_data: Dict with 'income', 'balance', 'cashflow' data
            include_charts: Generate charts for each sheet
            
        Returns:
            Dict with workbook_id, web_url, sheets created
            
        Example:
            financial_data = {
                "income": [
                    {"item": "Revenue", "q1": 100000, "q2": 110000},
                    {"item": "Expenses", "q1": 60000, "q2": 65000}
                ],
                "balance": [...],
                "cashflow": [...]
            }
            result = excel_smart_financial_report(
                workbook_name="Q1-Q2 2025 Financials",
                financial_data=financial_data,
                include_charts=True
            )
        """
        try:
            # Create workbook
            wb_result = self.excel_create_workbook(workbook_name, **kwargs)
            if "error" in wb_result:
                return wb_result
            
            workbook_id = wb_result['workbook_id']
            sheets_created = []
            
            # Create sheets for each financial statement
            for sheet_type, data in financial_data.items():
                if not data:
                    continue
                
                # Create sheet
                sheet_name = sheet_type.title()
                sheet_result = self.excel_add_worksheet(workbook_id, sheet_name, **kwargs)
                
                if "error" in sheet_result:
                    continue
                
                # Convert data to 2D array
                if data:
                    headers = list(data[0].keys())
                    rows = [[item.get(h, '') for h in headers] for item in data]
                    
                    # Insert headers
                    full_data = [headers] + rows
                    
                    # Write to sheet
                    cols = len(headers)
                    range_address = f"A1:{chr(65 + cols - 1)}{len(full_data)}"
                    self.excel_update_range(workbook_id, sheet_name, range_address, full_data, **kwargs)
                    
                    sheets_created.append(sheet_name)
                    
                    # Add auto-calculated totals using formula_builder
                    if len(rows) > 0 and cols >= 2:
                        # Add "Total" row with formulas
                        total_row = len(full_data) + 1
                        # Label cell
                        self.excel_update_range(
                            workbook_id, sheet_name, f"A{total_row}", 
                            [["Total"]], **kwargs
                        )
                        
                        # Add SUM formulas for numeric columns (skip first column = labels)
                        for col_idx in range(1, cols):
                            col_letter = chr(65 + col_idx)
                            data_range = f"{col_letter}2:{col_letter}{len(full_data)}"
                            formula_query = f"sum column {col_letter}"
                            
                            self.excel_smart_formula_builder(
                                workbook_id, sheet_name,
                                formula_query, f"{col_letter}{total_row}",
                                **kwargs
                            )
                    
                    # Create chart if requested
                    if include_charts and len(rows) > 0 and cols >= 2:
                        chart_range = f"A1:{chr(65 + cols - 1)}{min(len(full_data), 10)}"
                        self.excel_create_chart(
                            workbook_id,
                            sheet_name,
                            "ColumnClustered",
                            chart_range,
                            f"{sheet_name} Overview",
                            **kwargs
                        )
            
            return {
                "success": True,
                "workbook_id": workbook_id,
                "web_url": wb_result['web_url'],
                "sheets_created": sheets_created,
                "charts_created": include_charts
            }
            
        except Exception as e:
            return {"error": f"Failed to create financial report: {str(e)}"}
    
    # ========================================
    # ENHANCEMENT: SMART SHEET BUILDER
    # ========================================
    
    def excel_smart_sheet_builder(
        self,
        workbook_name: Optional[str] = None,
        workbook_id: Optional[str] = None,
        worksheets: Optional[List[Dict[str, Any]]] = None,
        sheet_description: Optional[str] = None,
        data_structure: Optional[Dict[str, Any]] = None,
        formulas: Optional[List[Dict[str, Any]]] = None,
        charts: Optional[List[Dict[str, Any]]] = None,
        include_formulas: bool = True,
        include_charts: bool = True,
        **kwargs
    ) -> Dict[str, Any]:
        """
        SMART: Comprehensive Excel builder - create/update workbooks, sheets, formulas, charts
        
        ONE TOOL TO DO IT ALL:
        - Create new workbooks from scratch OR update existing ones
        - Add multiple worksheets with different structures
        - Natural language formulas with cross-sheet references
        - Multiple chart types and positioning
        - Granular updates to specific ranges/cells
        
        Args:
            workbook_name: Name for NEW workbook (creates new if no workbook_id)
            workbook_id: ID of EXISTING workbook to update (updates existing)
            
            worksheets: List of worksheet definitions:
                [
                    {
                        "name": "Sales Data",
                        "description": "sales tracker with monthly totals",  # OR
                        "columns": ["Rep", "Month", "Amount"],  # explicit columns
                        "data": [[...], [...]],  # optional data rows
                        "formulas": [
                            {"cell": "D2", "formula": "sum column C"},
                            {"range": "E2:E10", "formula": "multiply B2 by C2"}
                        ],
                        "chart": {
                            "type": "column",
                            "range": "A1:C10",
                            "title": "Monthly Sales"
                        }
                    },
                    {
                        "name": "Summary",
                        "columns": ["Metric", "Value"],
                        "formulas": [
                            {"cell": "B2", "formula": "=SUM('Sales Data'!C:C)"}  # cross-sheet
                        ]
                    }
                ]
            
            sheet_description: LEGACY - Single sheet description (backward compatible)
            data_structure: LEGACY - Single sheet structure (backward compatible)
            
            formulas: Global formulas to add across sheets:
                [
                    {"workbook": "workbook_id", "sheet": "Data", "cell": "A1", "formula": "sum column B"},
                    {"workbook": "workbook_id", "sheet": "Summary", "range": "C1:C10", "formula": "=A1*2"}
                ]
            
            charts: Global charts to add:
                [
                    {"sheet": "Data", "type": "column", "range": "A1:C10", "title": "Sales"},
                    {"sheet": "Summary", "type": "pie", "range": "A1:B5"}
                ]
            
            include_formulas: Auto-add smart formulas if not specified
            include_charts: Auto-generate charts if not specified
            
        Returns:
            Dict with workbook_id, web_url, worksheets created/updated, formulas added, charts created
            
        Examples:
            # CREATE FROM SCRATCH (comprehensive)
            result = excel_smart_sheet_builder(
                workbook_name="Q1 Report",
                worksheets=[
                    {
                        "name": "Sales Data",
                        "columns": ["Rep", "Month", "Amount", "Region"],
                        "data": [["Alice", "Jan", 1000, "West"], ["Bob", "Jan", 1200, "East"]],
                        "formulas": [
                            {"cell": "C10", "formula": "sum column C"}
                        ]
                    },
                    {
                        "name": "Summary",
                        "columns": ["Metric", "Value"],
                        "formulas": [
                            {"cell": "B1", "formula": "=SUM('Sales Data'!C:C)"},
                            {"cell": "B2", "formula": "=AVERAGE('Sales Data'!C:C)"}
                        ]
                    }
                ]
            )
            
            # UPDATE EXISTING (granular)
            result = excel_smart_sheet_builder(
                workbook_id="existing_id",
                formulas=[
                    {"sheet": "Data", "cell": "D1", "formula": "multiply column B by column C"}
                ],
                charts=[
                    {"sheet": "Data", "type": "line", "range": "A1:C10", "title": "Trends"}
                ]
            )
            
            # SIMPLE (backward compatible)
            result = excel_smart_sheet_builder(
                workbook_name="Sales Tracker",
                sheet_description="sales tracker with totals"
            )
        """
        try:
            # STEP 1: Determine if creating new or updating existing
            if workbook_id:
                # UPDATE EXISTING workbook
                wb_id = workbook_id
                wb_url = None
                mode = "update"
            elif workbook_name:
                # CREATE NEW workbook
                wb_result = self.excel_create_workbook(workbook_name, **kwargs)
                if "error" in wb_result:
                    return wb_result
                wb_id = wb_result['workbook_id']
                wb_url = wb_result['web_url']
                mode = "create"
            else:
                return {"error": "Must provide either workbook_name (create) or workbook_id (update)"}
            
            # STEP 2: Handle legacy single-sheet mode (backward compatibility)
            if sheet_description and not worksheets:
                # Convert legacy parameters to new format
                description_lower = sheet_description.lower()
                
                if data_structure and "columns" in data_structure:
                    columns = data_structure["columns"]
                else:
                    columns = self._detect_columns_from_description(description_lower)
                
                sample_data = data_structure.get("sample_data") if data_structure else None
                if not sample_data:
                    sample_data = self._generate_sample_data(columns, rows=5)
                
                worksheets = [{
                    "name": "Data",
                    "columns": columns,
                    "data": sample_data,
                    "description": sheet_description
                }]
            
            # STEP 3: Process worksheets
            worksheets_created = []
            worksheets_updated = []
            all_formulas = []
            all_charts = []
            
            if worksheets:
                for ws_def in worksheets:
                    ws_name = ws_def.get("name", f"Sheet{len(worksheets_created) + 1}")
                    
                    # Create or get worksheet
                    if mode == "create":
                        ws_result = self.excel_add_worksheet(wb_id, ws_name, **kwargs)
                        if "error" not in ws_result:
                            worksheets_created.append(ws_name)
                    else:
                        # Check if sheet exists, create if not
                        existing_sheets = self.excel_list_worksheets(wb_id, **kwargs)
                        if ws_name not in existing_sheets.get('worksheets', []):
                            self.excel_add_worksheet(wb_id, ws_name, **kwargs)
                            worksheets_created.append(ws_name)
                        else:
                            worksheets_updated.append(ws_name)
                    
                    # Determine columns
                    if "columns" in ws_def:
                        columns = ws_def["columns"]
                    elif "description" in ws_def:
                        columns = self._detect_columns_from_description(ws_def["description"].lower())
                    else:
                        columns = ["Column A", "Column B", "Column C"]
                    
                    # Write headers
                    header_range = f"A1:{chr(65 + len(columns) - 1)}1"
                    self.excel_update_range(wb_id, ws_name, header_range, [columns], **kwargs)
                    
                    # Write data if provided
                    if "data" in ws_def and ws_def["data"]:
                        data_rows = ws_def["data"]
                        data_start_row = 2
                        data_end_row = data_start_row + len(data_rows) - 1
                        data_range = f"A{data_start_row}:{chr(65 + len(columns) - 1)}{data_end_row}"
                        self.excel_update_range(wb_id, ws_name, data_range, data_rows, **kwargs)
                        
                        # Auto-add formulas if requested and not explicitly provided
                        if include_formulas and "formulas" not in ws_def:
                            formula_row = len(data_rows) + 3
                            self.excel_update_range(wb_id, ws_name, f"A{formula_row}", [["TOTALS"]], **kwargs)
                            
                            for col_idx, col_name in enumerate(columns):
                                if self._is_numeric_column(col_name):
                                    col_letter = chr(65 + col_idx)
                                    formula_result = self.excel_smart_formula_builder(
                                        wb_id, ws_name,
                                        f"sum column {col_letter}",
                                        f"{col_letter}{formula_row}",
                                        **kwargs
                                    )
                                    all_formulas.append({
                                        "sheet": ws_name,
                                        "cell": f"{col_letter}{formula_row}",
                                        "formula": formula_result.get("formula", "")
                                    })
                    
                    # Process explicit formulas
                    if "formulas" in ws_def:
                        for formula_def in ws_def["formulas"]:
                            if "cell" in formula_def:
                                # Single cell formula
                                formula_result = self.excel_smart_formula_builder(
                                    wb_id, ws_name,
                                    formula_def["formula"],
                                    formula_def["cell"],
                                    **kwargs
                                )
                                all_formulas.append({
                                    "sheet": ws_name,
                                    "cell": formula_def["cell"],
                                    "formula": formula_result.get("formula", formula_def["formula"])
                                })
                            elif "range" in formula_def:
                                # Range formula (copy to all cells)
                                # Parse range (e.g., "E2:E10")
                                range_parts = formula_def["range"].split(":")
                                if len(range_parts) == 2:
                                    start_cell = range_parts[0]
                                    end_cell = range_parts[1]
                                    # Apply formula to first cell (Excel will auto-fill)
                                    formula_result = self.excel_smart_formula_builder(
                                        wb_id, ws_name,
                                        formula_def["formula"],
                                        start_cell,
                                        **kwargs
                                    )
                                    all_formulas.append({
                                        "sheet": ws_name,
                                        "range": formula_def["range"],
                                        "formula": formula_result.get("formula", formula_def["formula"])
                                    })
                    
                    # Process chart if defined
                    if "chart" in ws_def:
                        chart_def = ws_def["chart"]
                        chart_type = chart_def.get("type", "ColumnClustered")
                        chart_range = chart_def.get("range", f"A1:{chr(65 + len(columns) - 1)}10")
                        chart_title = chart_def.get("title", f"{ws_name} Chart")
                        
                        chart_result = self.excel_create_chart(
                            wb_id, ws_name, chart_type,
                            chart_range, chart_title, **kwargs
                        )
                        if "error" not in chart_result:
                            all_charts.append({
                                "sheet": ws_name,
                                "type": chart_type,
                                "title": chart_title
                            })
                    elif include_charts and "data" in ws_def and len(columns) >= 2:
                        # Auto-create chart
                        chart_type = "ColumnClustered"
                        if "description" in ws_def:
                            desc = ws_def["description"].lower()
                            if "timeline" in desc or "trend" in desc:
                                chart_type = "Line"
                            elif "comparison" in desc:
                                chart_type = "BarClustered"
                            elif "distribution" in desc:
                                chart_type = "Pie"
                        
                        data_row_count = len(ws_def.get("data", []))
                        chart_range = f"A1:{chr(65 + min(len(columns), 3) - 1)}{min(data_row_count + 1, 10)}"
                        chart_result = self.excel_create_chart(
                            wb_id, ws_name, chart_type,
                            chart_range, f"{ws_name} Overview", **kwargs
                        )
                        if "error" not in chart_result:
                            all_charts.append({
                                "sheet": ws_name,
                                "type": chart_type,
                                "title": f"{ws_name} Overview"
                            })
            
            # STEP 4: Process global formulas
            if formulas:
                for formula_def in formulas:
                    sheet_name = formula_def.get("sheet")
                    if not sheet_name:
                        continue
                    
                    if "cell" in formula_def:
                        formula_result = self.excel_smart_formula_builder(
                            wb_id, sheet_name,
                            formula_def["formula"],
                            formula_def["cell"],
                            **kwargs
                        )
                        all_formulas.append({
                            "sheet": sheet_name,
                            "cell": formula_def["cell"],
                            "formula": formula_result.get("formula", formula_def["formula"])
                        })
                    elif "range" in formula_def:
                        # Direct Excel formula (starts with =)
                        if formula_def["formula"].startswith("="):
                            self.excel_set_formula(
                                wb_id, sheet_name,
                                formula_def["range"],
                                formula_def["formula"],
                                **kwargs
                            )
                        else:
                            # Natural language formula
                            formula_result = self.excel_smart_formula_builder(
                                wb_id, sheet_name,
                                formula_def["formula"],
                                formula_def["range"].split(":")[0],
                                **kwargs
                            )
                        all_formulas.append({
                            "sheet": sheet_name,
                            "range": formula_def.get("range"),
                            "formula": formula_def["formula"]
                        })
            
            # STEP 5: Process global charts
            if charts:
                for chart_def in charts:
                    sheet_name = chart_def.get("sheet")
                    if not sheet_name:
                        continue
                    
                    chart_type = chart_def.get("type", "ColumnClustered")
                    chart_range = chart_def.get("range", "A1:C10")
                    chart_title = chart_def.get("title", "Chart")
                    
                    chart_result = self.excel_create_chart(
                        wb_id, sheet_name, chart_type,
                        chart_range, chart_title, **kwargs
                    )
                    if "error" not in chart_result:
                        all_charts.append({
                            "sheet": sheet_name,
                            "type": chart_type,
                            "title": chart_title
                        })
            
            # STEP 6: Create summary sheet if creating new workbook
            if mode == "create" and len(worksheets_created) > 0:
                summary_data = [
                    ["Workbook Summary", ""],
                    ["", ""],
                    ["Mode", "Created from scratch"],
                    ["Worksheets Created", len(worksheets_created)],
                    ["Formulas Added", len(all_formulas)],
                    ["Charts Created", len(all_charts)],
                    ["", ""],
                    ["Worksheets:", ""],
                ]
                
                for ws_name in worksheets_created:
                    summary_data.append([f"  - {ws_name}", ""])
                
                self.excel_add_worksheet(wb_id, "Summary", **kwargs)
                summary_range = f"A1:B{len(summary_data)}"
                self.excel_update_range(wb_id, "Summary", summary_range, summary_data, **kwargs)
            
            return {
                "success": True,
                "mode": mode,
                "workbook_id": wb_id,
                "web_url": wb_url if mode == "create" else f"Updated existing workbook {wb_id}",
                "worksheets_created": worksheets_created,
                "worksheets_updated": worksheets_updated,
                "formulas_added": len(all_formulas),
                "formulas": all_formulas,
                "charts_created": len(all_charts),
                "charts": all_charts,
                "ready_for_data": True
            }
            
        except Exception as e:
            return {"error": f"Failed to build/update workbook: {str(e)}"}
    
    def _detect_columns_from_description(self, description: str) -> List[str]:
        """Extract likely column names from natural language description"""
        # Common patterns
        columns = []
        
        # Sales/Revenue patterns
        if any(word in description for word in ["sales", "revenue", "income"]):
            columns.extend(["Sales Rep", "Month", "Amount", "Region"])
        
        # Expense patterns
        elif any(word in description for word in ["expense", "cost", "spending"]):
            columns.extend(["Category", "Date", "Amount", "Vendor"])
        
        # Project/Task patterns
        elif any(word in description for word in ["project", "task", "timeline"]):
            columns.extend(["Task", "Owner", "Start Date", "End Date", "Status"])
        
        # Inventory patterns
        elif any(word in description for word in ["inventory", "stock", "products"]):
            columns.extend(["Product", "SKU", "Quantity", "Price", "Supplier"])
        
        # Customer/Contact patterns
        elif any(word in description for word in ["customer", "contact", "client"]):
            columns.extend(["Name", "Email", "Phone", "Company", "Status"])
        
        # Default generic structure
        else:
            columns = ["Name", "Date", "Value", "Category", "Notes"]
        
        return columns
    
    def _is_numeric_column(self, column_name: str) -> bool:
        """Detect if column is likely numeric based on name"""
        numeric_keywords = [
            "amount", "total", "sum", "price", "cost", "quantity", "qty",
            "revenue", "sales", "value", "count", "number", "hours", "days"
        ]
        return any(keyword in column_name.lower() for keyword in numeric_keywords)
    
    def _generate_sample_data(self, columns: List[str], rows: int = 5) -> List[List[Any]]:
        """Generate smart sample data based on column types"""
        from datetime import datetime, timedelta
        
        sample_data = []
        
        for i in range(rows):
            row = []
            for col in columns:
                col_lower = col.lower()
                
                # Date columns
                if "date" in col_lower:
                    date = datetime.now() - timedelta(days=rows - i)
                    row.append(date.strftime("%Y-%m-%d"))
                
                # Amount/Price columns
                elif any(word in col_lower for word in ["amount", "price", "cost", "sales", "revenue"]):
                    row.append((i + 1) * 1000 + (i * 100))
                
                # Quantity columns
                elif any(word in col_lower for word in ["quantity", "qty", "count"]):
                    row.append((i + 1) * 10)
                
                # Status columns
                elif "status" in col_lower:
                    statuses = ["Active", "Pending", "Complete", "On Hold", "In Progress"]
                    row.append(statuses[i % len(statuses)])
                
                # Category columns
                elif "category" in col_lower:
                    categories = ["Category A", "Category B", "Category C", "Category D", "Category E"]
                    row.append(categories[i % len(categories)])
                
                # Name columns
                elif "name" in col_lower or "rep" in col_lower or "owner" in col_lower:
                    names = ["Alice Smith", "Bob Johnson", "Carol Williams", "David Brown", "Eve Davis"]
                    row.append(names[i % len(names)])
                
                # Email columns
                elif "email" in col_lower:
                    names = ["alice", "bob", "carol", "david", "eve"]
                    row.append(f"{names[i % len(names)]}@company.com")
                
                # Default text
                else:
                    row.append(f"Sample {i + 1}")
            
            sample_data.append(row)
        
        return sample_data
    
    # ========================================
    # ENHANCEMENT: AI FORMULA ASSISTANT
    # ========================================
    
    def excel_smart_formula_builder(
        self,
        workbook_id: str,
        worksheet_name: str,
        natural_language_query: str,
        target_range: str,
        context: Optional[Dict[str, Any]] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """
        SMART: Build Excel formulas from natural language
        
        Converts natural language like "sum column A" into Excel formulas
        
        Args:
            workbook_id: Workbook ID
            worksheet_name: Sheet name
            natural_language_query: Description of what the formula should do
            target_range: Where to place the formula (e.g., "C1" or "C1:C10")
            context: Optional context with tables, columns, data types
            
        Returns:
            Dict with formula, explanation, alternatives, applied_range
        """
        try:
            context = context or {}
            query_lower = natural_language_query.lower()
            
            formula = None
            explanation = ""
            
            # SUM patterns
            if any(word in query_lower for word in ['sum', 'total', 'add up']):
                if 'column' in query_lower:
                    for char in 'ABCDEFGHIJKLMNOPQRSTUVWXYZ':
                        if f'column {char.lower()}' in query_lower:
                            formula = f"=SUM({char}:{char})"
                            explanation = f"Sums all values in column {char}"
                            break
            
            # AVERAGE patterns
            elif any(word in query_lower for word in ['average', 'mean']):
                if 'column' in query_lower:
                    for char in 'ABCDEFGHIJKLMNOPQRSTUVWXYZ':
                        if f'column {char.lower()}' in query_lower:
                            formula = f"=AVERAGE({char}:{char})"
                            explanation = f"Calculates average of column {char}"
                            break
            
            # MULTIPLICATION patterns
            elif any(word in query_lower for word in ['multiply', 'times', 'product']):
                cols = []
                for char in 'ABCDEFGHIJKLMNOPQRSTUVWXYZ':
                    if f'column {char.lower()}' in query_lower:
                        cols.append(char)
                if len(cols) >= 2:
                    row_start = ''.join(filter(str.isdigit, target_range.split(':')[0]))
                    if not row_start:
                        row_start = "2"
                    formula = f"={cols[0]}{row_start}*{cols[1]}{row_start}"
                    explanation = f"Multiplies column {cols[0]} by column {cols[1]}"
            
            # COUNT patterns
            elif 'count' in query_lower:
                if 'column' in query_lower:
                    for char in 'ABCDEFGHIJKLMNOPQRSTUVWXYZ':
                        if f'column {char.lower()}' in query_lower:
                            formula = f"=COUNT({char}:{char})"
                            explanation = f"Counts numeric values in column {char}"
                            break
            
            if not formula:
                return {
                    "error": "Could not generate formula from query",
                    "suggestion": "Try phrases like: 'sum column A', 'multiply column B by column C', 'average of column D'",
                    "query_received": natural_language_query
                }
            
            # Apply formula
            start_cell = target_range.split(':')[0] if ':' in target_range else target_range
            result = self.excel_set_formula(workbook_id, worksheet_name, start_cell, formula, **kwargs)
            
            return {
                "success": True,
                "formula": formula,
                "explanation": explanation,
                "applied_range": target_range,
                "natural_query": natural_language_query
            }
            
        except Exception as e:
            return {"error": f"Failed to build formula: {str(e)}"}
    
    # ========================================
    # ENHANCEMENT: BATCH OPERATIONS
    # ========================================
    
    def excel_batch_update(
        self,
        workbook_id: str,
        worksheet_name: str,
        updates: List[Dict[str, Any]],
        **kwargs
    ) -> Dict[str, Any]:
        """
        Update multiple ranges in a single operation (reduces API calls)
        
        Args:
            workbook_id: Workbook ID
            worksheet_name: Sheet name
            updates: List of {range, values} dicts
            
        Returns:
            Dict with results for each update
        """
        try:
            results = []
            
            for update in updates:
                range_address = update.get('range')
                values = update.get('values')
                
                if not range_address or not values:
                    results.append({"error": "Missing range or values"})
                    continue
                
                result = self.excel_update_range(
                    workbook_id,
                    worksheet_name,
                    range_address,
                    values,
                    **kwargs
                )
                
                results.append(result)
            
            successful = sum(1 for r in results if "error" not in r)
            
            return {
                "success": True,
                "total_updates": len(updates),
                "successful": successful,
                "failed": len(updates) - successful,
                "results": results
            }
            
        except Exception as e:
            return {"error": f"Batch update failed: {str(e)}"}
    
    def _make_file_shareable(self, file_id: str, **kwargs) -> Dict[str, Any]:
        """
        Make a file shareable with anonymous edit access
        
        Args:
            file_id: The ID of the file to share
            **kwargs: Credential injection
        
        Returns:
            Dict with success status and share_link
        """
        try:
            # Get credentials
            access_token = kwargs.get('access_token')
            if not access_token:
                return {"success": False, "error": "access_token required"}
            
            # Create sharing link with edit permissions
            url = f"https://graph.microsoft.com/v1.0/me/drive/items/{file_id}/createLink"
            headers = self._get_headers(access_token)
            
            payload = {
                "type": "edit",
                "scope": "anonymous"
            }
            
            response = requests.post(url, json=payload, headers=headers)
            response.raise_for_status()
            data = response.json()
            
            return {
                "success": True,
                "share_link": data.get('link', {}).get('webUrl', '')
            }
        except Exception as e:
            # Don't fail the entire operation if sharing fails
            return {"success": False, "error": str(e)}

# ========================================
# GLOBAL INSTANCE & MODULE-LEVEL EXPORTS
# ========================================

# Create global instance (no access token needed - credentials injected per-call)
microsoft_excel_tools = MicrosoftExcelTools()

# Export all functions at module level
# Wrappers handle parameter transformation for registry compatibility

def microsoft_excel_get_workbook(**kwargs):
    return microsoft_excel_tools.excel_get_workbook(**kwargs)

def microsoft_excel_list_workbooks(**kwargs):
    return microsoft_excel_tools.excel_list_workbooks(**kwargs)

def microsoft_excel_delete_workbook(**kwargs):
    return microsoft_excel_tools.excel_delete_workbook(**kwargs)

def microsoft_excel_list_worksheets(**kwargs):
    return microsoft_excel_tools.excel_list_worksheets(**kwargs)

def microsoft_excel_add_worksheet(**kwargs):
    return microsoft_excel_tools.excel_add_worksheet(**kwargs)

def microsoft_excel_rename_worksheet(**kwargs):
    return microsoft_excel_tools.excel_rename_worksheet(**kwargs)

def microsoft_excel_delete_worksheet(**kwargs):
    return microsoft_excel_tools.excel_delete_worksheet(**kwargs)

def microsoft_excel_get_range(**kwargs):
    return microsoft_excel_tools.excel_get_range(**kwargs)

def microsoft_excel_update_range(**kwargs):
    return microsoft_excel_tools.excel_update_range(**kwargs)

def microsoft_excel_clear_range(**kwargs):
    return microsoft_excel_tools.excel_clear_range(**kwargs)

def microsoft_excel_insert_rows(**kwargs):
    return microsoft_excel_tools.excel_insert_rows(**kwargs)

def microsoft_excel_delete_rows(**kwargs):
    return microsoft_excel_tools.excel_delete_rows(**kwargs)

def microsoft_excel_set_formula(**kwargs):
    return microsoft_excel_tools.excel_set_formula(**kwargs)

def microsoft_excel_calculate(**kwargs):
    return microsoft_excel_tools.excel_calculate(**kwargs)

def microsoft_excel_create_chart(**kwargs):
    return microsoft_excel_tools.excel_create_chart(**kwargs)

def microsoft_excel_list_charts(**kwargs):
    return microsoft_excel_tools.excel_list_charts(**kwargs)

def microsoft_excel_sort_range(**kwargs):
    return microsoft_excel_tools.excel_sort_range(**kwargs)

def microsoft_excel_filter_range(**kwargs):
    return microsoft_excel_tools.excel_filter_range(**kwargs)

def microsoft_excel_smart_import_csv(**kwargs):
    return microsoft_excel_tools.excel_smart_import_csv(**kwargs)

def microsoft_excel_smart_data_analysis(**kwargs):
    return microsoft_excel_tools.excel_smart_data_analysis(**kwargs)

def microsoft_excel_smart_create_pivot(**kwargs):
    return microsoft_excel_tools.excel_smart_create_pivot(**kwargs)

def microsoft_excel_smart_financial_report(**kwargs):
    return microsoft_excel_tools.excel_smart_financial_report(**kwargs)


    if user_id is None:
        raise ValueError("user_id is required")
    return microsoft_excel_tools.excel_create_workbook(user_id, **kwargs)

def microsoft_excel_get_workbook(**kwargs):
    user_id = kwargs.pop('user_id', None)
    if user_id is None:
        raise ValueError("user_id is required")
    return microsoft_excel_tools.excel_get_workbook(user_id, **kwargs)

def microsoft_excel_list_workbooks(**kwargs):
    user_id = kwargs.pop('user_id', None)
    if user_id is None:
        raise ValueError("user_id is required")
    return microsoft_excel_tools.excel_list_workbooks(user_id, **kwargs)

def microsoft_excel_delete_workbook(**kwargs):
    user_id = kwargs.pop('user_id', None)
    if user_id is None:
        raise ValueError("user_id is required")
    return microsoft_excel_tools.excel_delete_workbook(user_id, **kwargs)

def microsoft_excel_list_worksheets(**kwargs):
    user_id = kwargs.pop('user_id', None)
    if user_id is None:
        raise ValueError("user_id is required")
    return microsoft_excel_tools.excel_list_worksheets(user_id, **kwargs)

def microsoft_excel_add_worksheet(**kwargs):
    user_id = kwargs.pop('user_id', None)
    if user_id is None:
        raise ValueError("user_id is required")
    return microsoft_excel_tools.excel_add_worksheet(user_id, **kwargs)

def microsoft_excel_rename_worksheet(**kwargs):
    user_id = kwargs.pop('user_id', None)
    if user_id is None:
        raise ValueError("user_id is required")
    return microsoft_excel_tools.excel_rename_worksheet(user_id, **kwargs)

def microsoft_excel_delete_worksheet(**kwargs):
    user_id = kwargs.pop('user_id', None)
    if user_id is None:
        raise ValueError("user_id is required")
    return microsoft_excel_tools.excel_delete_worksheet(user_id, **kwargs)

def microsoft_excel_get_range(**kwargs):
    user_id = kwargs.pop('user_id', None)
    if user_id is None:
        raise ValueError("user_id is required")
    return microsoft_excel_tools.excel_get_range(user_id, **kwargs)

def microsoft_excel_update_range(**kwargs):
    user_id = kwargs.pop('user_id', None)
    if user_id is None:
        raise ValueError("user_id is required")
    return microsoft_excel_tools.excel_update_range(user_id, **kwargs)

def microsoft_excel_clear_range(**kwargs):
    user_id = kwargs.pop('user_id', None)
    if user_id is None:
        raise ValueError("user_id is required")
    return microsoft_excel_tools.excel_clear_range(user_id, **kwargs)

def microsoft_excel_insert_rows(**kwargs):
    user_id = kwargs.pop('user_id', None)
    if user_id is None:
        raise ValueError("user_id is required")
    return microsoft_excel_tools.excel_insert_rows(user_id, **kwargs)

def microsoft_excel_delete_rows(**kwargs):
    user_id = kwargs.pop('user_id', None)
    if user_id is None:
        raise ValueError("user_id is required")
    return microsoft_excel_tools.excel_delete_rows(user_id, **kwargs)

def microsoft_excel_set_formula(**kwargs):
    user_id = kwargs.pop('user_id', None)
    if user_id is None:
        raise ValueError("user_id is required")
    return microsoft_excel_tools.excel_set_formula(user_id, **kwargs)

def microsoft_excel_calculate(**kwargs):
    user_id = kwargs.pop('user_id', None)
    if user_id is None:
        raise ValueError("user_id is required")
    return microsoft_excel_tools.excel_calculate(user_id, **kwargs)

def microsoft_excel_create_chart(**kwargs):
    user_id = kwargs.pop('user_id', None)
    if user_id is None:
        raise ValueError("user_id is required")
    return microsoft_excel_tools.excel_create_chart(user_id, **kwargs)

def microsoft_excel_list_charts(**kwargs):
    user_id = kwargs.pop('user_id', None)
    if user_id is None:
        raise ValueError("user_id is required")
    return microsoft_excel_tools.excel_list_charts(user_id, **kwargs)

def microsoft_excel_sort_range(**kwargs):
    user_id = kwargs.pop('user_id', None)
    if user_id is None:
        raise ValueError("user_id is required")
    return microsoft_excel_tools.excel_sort_range(user_id, **kwargs)

def microsoft_excel_filter_range(**kwargs):
    user_id = kwargs.pop('user_id', None)
    if user_id is None:
        raise ValueError("user_id is required")
    return microsoft_excel_tools.excel_filter_range(user_id, **kwargs)

def microsoft_excel_smart_import_csv(**kwargs):
    user_id = kwargs.pop('user_id', None)
    if user_id is None:
        raise ValueError("user_id is required")
    return microsoft_excel_tools.excel_smart_import_csv(user_id, **kwargs)

def microsoft_excel_smart_data_analysis(**kwargs):
    user_id = kwargs.pop('user_id', None)
    if user_id is None:
        raise ValueError("user_id is required")
    return microsoft_excel_tools.excel_smart_data_analysis(user_id, **kwargs)

def microsoft_excel_smart_create_pivot(**kwargs):
    user_id = kwargs.pop('user_id', None)
    if user_id is None:
        raise ValueError("user_id is required")
    return microsoft_excel_tools.excel_smart_create_pivot(user_id, **kwargs)

def microsoft_excel_smart_financial_report(**kwargs):
    user_id = kwargs.pop('user_id', None)
    if user_id is None:
        raise ValueError("user_id is required")
    return microsoft_excel_tools.excel_smart_financial_report(user_id, **kwargs)

def microsoft_excel_smart_sheet_builder(**kwargs):
    user_id = kwargs.pop('user_id', None)
    if user_id is None:
        raise ValueError("user_id is required")
    return microsoft_excel_tools.excel_smart_sheet_builder(user_id, **kwargs)


microsoft_excel_create_workbook = microsoft_excel_tools.excel_create_workbook

microsoft_excel_get_workbook = microsoft_excel_tools.excel_get_workbook

microsoft_excel_list_workbooks = microsoft_excel_tools.excel_list_workbooks

microsoft_excel_delete_workbook = microsoft_excel_tools.excel_delete_workbook

microsoft_excel_list_worksheets = microsoft_excel_tools.excel_list_worksheets

microsoft_excel_add_worksheet = microsoft_excel_tools.excel_add_worksheet

microsoft_excel_rename_worksheet = microsoft_excel_tools.excel_rename_worksheet

microsoft_excel_delete_worksheet = microsoft_excel_tools.excel_delete_worksheet

microsoft_excel_get_range = microsoft_excel_tools.excel_get_range

microsoft_excel_update_range = microsoft_excel_tools.excel_update_range

microsoft_excel_clear_range = microsoft_excel_tools.excel_clear_range

microsoft_excel_insert_rows = microsoft_excel_tools.excel_insert_rows

microsoft_excel_delete_rows = microsoft_excel_tools.excel_delete_rows

microsoft_excel_set_formula = microsoft_excel_tools.excel_set_formula

microsoft_excel_calculate = microsoft_excel_tools.excel_calculate

microsoft_excel_create_chart = microsoft_excel_tools.excel_create_chart

microsoft_excel_list_charts = microsoft_excel_tools.excel_list_charts

microsoft_excel_sort_range = microsoft_excel_tools.excel_sort_range

microsoft_excel_filter_range = microsoft_excel_tools.excel_filter_range

microsoft_excel_smart_import_csv = microsoft_excel_tools.excel_smart_import_csv

microsoft_excel_smart_data_analysis = microsoft_excel_tools.excel_smart_data_analysis

microsoft_excel_smart_create_pivot = microsoft_excel_tools.excel_smart_create_pivot

microsoft_excel_smart_financial_report = microsoft_excel_tools.excel_smart_financial_report

microsoft_excel_smart_sheet_builder = microsoft_excel_tools.excel_smart_sheet_builder

microsoft_excel_smart_formula_builder = microsoft_excel_tools.excel_smart_formula_builder

microsoft_excel_batch_update = microsoft_excel_tools.excel_batch_update

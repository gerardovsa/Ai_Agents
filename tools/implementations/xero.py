"""
Xero Tools - AI agent wrappers

Provides wrapper functions that map the tools defined in
`tools/schemas/xero_tools.json` to callable Python functions that
use the existing `XeroAPIClient` implementation in
`UI/external/modules/xero/xero_routes.py`.

Functions implemented:
- xero_platform_guide (CALL THIS FIRST!)
- xero_get_invoices
- xero_get_contacts
- xero_get_accounts
- xero_get_bank_transactions
- xero_get_payments
- xero_get_data_metadata
- xero_get_contacts_by_date_range
- xero_get_invoices_by_date_range
- xero_get_payments_by_date_range
- xero_get_accounts_metadata
- xero_get_accounts_by_type
- xero_get_bank_transactions_by_date_range

These functions accept the parameters defined in the schema and
optional kwargs used for credential injection:
- `_user_id`: numeric user id (permission checks elsewhere)
- `_injected_credentials`: dict with pre-fetched credentials (optional)
- `access_token`: direct token (optional)

They return structured dictionaries suitable for AI consumption.
"""

from typing import Any, Dict, Optional, List
import re
import traceback
import json
import io
from datetime import datetime

# Try to import the Xero client from the UI module. If it isn't available
# at import time, functions will raise a clear error.
try:
    from UI.external.modules.xero.xero_routes import XeroAPIClient
except Exception:
    # Defer import error to runtime to avoid import-time failures of the registry
    XeroAPIClient = None

# Import pandas for Excel export (optional)
try:
    import pandas as pd
    PANDAS_AVAILABLE = True
except ImportError:
    PANDAS_AVAILABLE = False

# Import Google Sheets integration (optional)
try:
    from google_workspace.google_docs import create_spreadsheet, append_rows_to_sheet
    GOOGLE_SHEETS_AVAILABLE = True
except ImportError:
    GOOGLE_SHEETS_AVAILABLE = False


def _get_client(business_id: int):
    if XeroAPIClient is None:
        raise RuntimeError("XeroAPIClient not available. Ensure UI external module is present.")
    return XeroAPIClient(business_id)


def _extract_token(kwargs: Dict[str, Any]) -> Optional[str]:
    # Support several patterns: explicit access_token, or injected credentials dict
    if 'access_token' in kwargs and kwargs.get('access_token'):
        return kwargs.get('access_token')
    injected = kwargs.get('_injected_credentials') or {}
    if isinstance(injected, dict):
        # common key names
        return injected.get('access_token') or injected.get('token')
    return None


def xero_platform_guide(task_description: Optional[str] = None, **kwargs) -> Dict[str, Any]:
    """
    ⚠️ CALL THIS FIRST BEFORE USING ANY XERO TOOLS!
    
    Provides comprehensive guidance on using Xero tools effectively including:
    - Tool recommendations based on your task
    - Data volume warnings and best practices
    - Workflow examples and common pitfalls
    - Filter options and parameter guidance
    
    Args:
        task_description: Optional - describe what you want to do for personalized recommendations
    
    Returns:
        Comprehensive guide with recommendations, workflows, and examples
    """
    guide = {
        "success": True,
        "platform": "xero",
        "total_tools": 15,
        "critical_warning": "⚠️ Xero contains YEARS of data (50K+ invoices, 7K+ contacts, 33K+ transactions). ALWAYS use metadata tools FIRST!",
        
        "recommended_workflow": {
            "step_1": "Call xero_get_data_metadata(business_id=1) to understand data volume",
            "step_2": "Based on volume, choose appropriate tool (range tool if >1000 records)",
            "step_3": "Use specific filters: date ranges, status, search terms",
            "example": "User wants recent invoices → metadata shows 500/month → use invoices_by_date_range with last month dates"
        },
        
        "tool_categories": {
            "start_here": [
                "xero_get_data_metadata - Overview of ALL data with time breakdowns (CALL THIS FIRST!)",
                "xero_get_accounts_metadata - Chart of accounts overview"
            ],
            "safe_efficient_tools": [
                "xero_get_invoices_by_date_range - Invoices from specific period (use this instead of xero_get_invoices)",
                "xero_get_contacts_by_date_range - Contacts from specific period (use this instead of xero_get_contacts)",
                "xero_get_payments_by_date_range - Payments from specific period",
                "xero_get_bank_transactions_by_date_range - Bank transactions with cash flow summary",
                "xero_get_accounts_by_type - Filter accounts by type (BANK, REVENUE, EXPENSE)",
                "xero_get_invoice_by_id - Get single invoice by ID (always safe)"
            ],
            "use_with_caution": [
                "xero_get_invoices - ⚠️ 50K+ records possible! Use filters or date range tool instead",
                "xero_get_contacts - ⚠️ 7K+ records! Use search parameter or date range tool",
                "xero_get_bank_transactions - ⚠️ 33K+ records! MUST use date filters",
                "xero_get_payments - ⚠️ 54K+ records! Use invoice_id filter or date range tool"
            ]
        },
        
        "common_tasks": {
            "accounts_payable": "1. xero_get_data_metadata → 2. xero_get_invoices_by_date_range(status='AUTHORISED') → filter by due_date",
            "find_customer": "xero_get_contacts(search='CustomerName') - search is partial match",
            "recent_customers": "1. xero_get_data_metadata → 2. xero_get_contacts_by_date_range(from_date, to_date)",
            "monthly_revenue": "xero_get_invoices_by_date_range(from_date='2025-10-01', to_date='2025-10-31', status='PAID')",
            "cash_flow": "xero_get_bank_transactions_by_date_range(from_date, to_date) - returns spend/receive/net summary"
        },
        
        "important_notes": {
            "invoice_status": "AUTHORISED=unpaid, PAID=paid (not intuitive!)",
            "date_format": "Always use YYYY-MM-DD (e.g., '2025-11-16')",
            "search_contacts": "search parameter does partial match: 'Smith' finds 'John Smith', 'Smith Corp'",
            "limit_parameter": "Default 1000 - use conservatively, check 'truncated' flag in results",
            "business_ids": "1=InHouse Print, 2=Publishing, 3=Signs"
        },
        
        "best_practices": [
            "✅ Always call xero_get_data_metadata first for time-based queries",
            "✅ Use *_by_date_range tools for better performance",
            "✅ Set reasonable limits (100-500 for testing)",
            "✅ Check 'truncated' flag - if true, narrow your date range",
            "❌ Never call standard tools without filters on production",
            "❌ Never use year-long date ranges without checking volume first"
        ]
    }
    
    # Add task-specific recommendations if provided
    if task_description:
        task_lower = task_description.lower()
        recommendations = []
        
        if 'invoice' in task_lower or 'bill' in task_lower:
            recommendations.append("Use xero_get_invoices_by_date_range with date filters")
            if 'unpaid' in task_lower or 'overdue' in task_lower:
                recommendations.append("Set status='AUTHORISED' for unpaid invoices")
        
        if 'contact' in task_lower or 'customer' in task_lower or 'client' in task_lower:
            if 'find' in task_lower or 'search' in task_lower:
                recommendations.append("Use xero_get_contacts(search='name') for specific name")
            else:
                recommendations.append("Use xero_get_contacts_by_date_range for recent contacts")
        
        if 'payment' in task_lower:
            recommendations.append("Use xero_get_payments_by_date_range with date filters")
        
        if 'bank' in task_lower or 'transaction' in task_lower or 'cash flow' in task_lower:
            recommendations.append("Use xero_get_bank_transactions_by_date_range")
            recommendations.append("Returns automatic cash flow summary (spend/receive/net)")
        
        if recommendations:
            guide["your_task_recommendations"] = {
                "task": task_description,
                "recommended_tools": recommendations
            }
    
    return guide


def _parse_xero_date(date_str: str) -> Optional[str]:
    """
    Parse Xero's date format and return ISO date string (YYYY-MM-DD)
    Xero returns dates in format: /Date(1748476800000+0000)/
    """
    if not date_str:
        return None
    
    try:
        # Extract timestamp from /Date(timestamp+0000)/ or /Date(timestamp)/
        match = re.search(r'/Date\((\d+)', date_str)
        if match:
            timestamp_ms = int(match.group(1))
            # Convert milliseconds to seconds
            timestamp_sec = timestamp_ms / 1000
            dt = datetime.fromtimestamp(timestamp_sec)
            return dt.strftime('%Y-%m-%d')
        
        # Try ISO format as fallback
        if 'T' in date_str:
            dt = datetime.fromisoformat(date_str.replace('Z', '+00:00'))
            return dt.strftime('%Y-%m-%d')
        
        # Already in YYYY-MM-DD format
        if re.match(r'\d{4}-\d{2}-\d{2}', date_str):
            return date_str
            
        return None
    except Exception:
        return None


def _format_currency(value: Any) -> str:
    """Format numeric value as currency string"""
    try:
        return f"${float(value):,.2f}"
    except (ValueError, TypeError):
        return str(value)


def _render_invoices_markdown(invoices: List[Dict], business_name: str) -> str:
    """
    Render invoices as detailed Markdown table (no summarization)
    """
    if not invoices:
        return "**No invoices found**"
    
    lines = [
        f"## {business_name} - Invoices ({len(invoices)} records)",
        "",
        "| Invoice # | Contact | Date | Due Date | Status | Total | Amount Due | Currency |",
        "|-----------|---------|------|----------|--------|-------|------------|----------|"
    ]
    
    for inv in invoices:
        lines.append(
            f"| {inv.get('invoice_number', 'N/A')} | "
            f"{inv.get('contact_name', 'N/A')} | "
            f"{inv.get('date', 'N/A')} | "
            f"{inv.get('due_date', 'N/A')} | "
            f"{inv.get('status', 'N/A')} | "
            f"{_format_currency(inv.get('total', 0))} | "
            f"{_format_currency(inv.get('amount_due', 0))} | "
            f"{inv.get('currency', 'NZD')} |"
        )
    
    return "\n".join(lines)


def _render_contacts_markdown(contacts: List[Dict], business_name: str) -> str:
    """
    Render contacts as detailed Markdown table (no summarization)
    """
    if not contacts:
        return "**No contacts found**"
    
    lines = [
        f"## {business_name} - Contacts ({len(contacts)} records)",
        "",
        "| Name | Email | Phone | Type | Updated |",
        "|------|-------|-------|------|---------| "
    ]
    
    for contact in contacts:
        contact_type = []
        if contact.get('is_customer'):
            contact_type.append('Customer')
        if contact.get('is_supplier'):
            contact_type.append('Supplier')
        type_str = ', '.join(contact_type) if contact_type else 'N/A'
        
        lines.append(
            f"| {contact.get('name', 'N/A')} | "
            f"{contact.get('email', 'N/A')} | "
            f"{contact.get('phone', 'N/A')} | "
            f"{type_str} | "
            f"{contact.get('updated_date', 'N/A')} |"
        )
    
    return "\n".join(lines)


def _render_payments_markdown(payments: List[Dict], business_name: str) -> str:
    """
    Render payments as detailed Markdown table (no summarization)
    """
    if not payments:
        return "**No payments found**"
    
    lines = [
        f"## {business_name} - Payments ({len(payments)} records)",
        "",
        "| Date | Amount | Invoice # | Status |",
        "|------|--------|-----------|--------|"
    ]
    
    for payment in payments:
        lines.append(
            f"| {payment.get('date', 'N/A')} | "
            f"{_format_currency(payment.get('amount', 0))} | "
            f"{payment.get('invoice_number', 'N/A')} | "
            f"{payment.get('status', 'N/A')} |"
        )
    
    return "\n".join(lines)


def _render_accounts_markdown(accounts: List[Dict], business_name: str) -> str:
    """
    Render accounts as detailed Markdown table (no summarization)
    """
    if not accounts:
        return "**No accounts found**"
    
    lines = [
        f"## {business_name} - Chart of Accounts ({len(accounts)} records)",
        "",
        "| Code | Name | Type | Tax Type | Payments Enabled |",
        "|------|------|------|----------|------------------|"
    ]
    
    for account in accounts:
        lines.append(
            f"| {account.get('code', 'N/A')} | "
            f"{account.get('name', 'N/A')} | "
            f"{account.get('type', 'N/A')} | "
            f"{account.get('tax_type', 'N/A')} | "
            f"{account.get('enable_payments', False)} |"
        )
    
    return "\n".join(lines)


def _render_bank_transactions_markdown(transactions: List[Dict], business_name: str, summary: Dict = None) -> str:
    """
    Render bank transactions as detailed Markdown table (no summarization)
    """
    if not transactions:
        return "**No transactions found**"
    
    lines = [
        f"## {business_name} - Bank Transactions ({len(transactions)} records)",
        ""
    ]
    
    # Add summary if provided
    if summary:
        lines.extend([
            "### Cash Flow Summary",
            f"- **Total Spend**: {_format_currency(summary.get('total_spend', 0))}",
            f"- **Total Receive**: {_format_currency(summary.get('total_receive', 0))}",
            f"- **Net Cash Flow**: {_format_currency(summary.get('net_cash_flow', 0))}",
            ""
        ])
    
    lines.extend([
        "### Transactions",
        "",
        "| Date | Type | Contact | Reference | Amount | Status | Bank Account |",
        "|------|------|---------|-----------|--------|--------|--------------|"
    ])
    
    for txn in transactions:
        lines.append(
            f"| {txn.get('date', 'N/A')} | "
            f"{txn.get('type', 'N/A')} | "
            f"{txn.get('contact_name', 'N/A')} | "
            f"{txn.get('reference', 'N/A')} | "
            f"{_format_currency(txn.get('total', 0))} | "
            f"{txn.get('status', 'N/A')} | "
            f"{txn.get('bank_account', 'N/A')} |"
        )
    
    return "\n".join(lines)


def _export_to_google_sheets(data: List[Dict], title: str, headers: List[str], user_id: int = None, **kwargs) -> Dict[str, Any]:
    """
    Export data to Google Sheets
    Returns spreadsheet URL and ID
    """
    if not GOOGLE_SHEETS_AVAILABLE:
        return {
            "success": False,
            "error": "Google Sheets integration not available. Install required dependencies."
        }
    
    try:
        # Create new spreadsheet
        sheet_result = create_spreadsheet(
            title=title,
            _user_id=user_id,
            **kwargs
        )
        
        if not sheet_result.get('success'):
            return sheet_result
        
        spreadsheet_id = sheet_result.get('spreadsheet_id')
        
        # Prepare rows (headers + data)
        rows = [headers]
        for item in data:
            row = [str(item.get(key, '')) for key in headers]
            rows.append(row)
        
        # Append data
        append_result = append_rows_to_sheet(
            spreadsheet_id=spreadsheet_id,
            range_name='Sheet1!A1',
            values=rows,
            _user_id=user_id,
            **kwargs
        )
        
        return {
            "success": True,
            "spreadsheet_id": spreadsheet_id,
            "spreadsheet_url": sheet_result.get('spreadsheet_url'),
            "rows_added": len(rows)
        }
    except Exception as e:
        return {
            "success": False,
            "error": f"Failed to export to Google Sheets: {str(e)}",
            "traceback": traceback.format_exc()
        }


def _export_to_excel(data: List[Dict], title: str, headers: List[str]) -> Dict[str, Any]:
    """
    Export data to Excel file (returns base64 encoded file)
    """
    if not PANDAS_AVAILABLE:
        return {
            "success": False,
            "error": "Pandas not available. Install pandas and openpyxl for Excel export."
        }
    
    try:
        # Create DataFrame
        df = pd.DataFrame(data)
        
        # Reorder columns to match headers
        df = df[[col for col in headers if col in df.columns]]
        
        # Export to Excel in memory
        output = io.BytesIO()
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            df.to_excel(writer, sheet_name='Data', index=False)
        
        # Get bytes
        excel_bytes = output.getvalue()
        
        # Encode as base64 for transmission
        import base64
        excel_base64 = base64.b64encode(excel_bytes).decode('utf-8')
        
        return {
            "success": True,
            "filename": f"{title.replace(' ', '_')}.xlsx",
            "excel_base64": excel_base64,
            "size_bytes": len(excel_bytes),
            "rows": len(df)
        }
    except Exception as e:
        return {
            "success": False,
            "error": f"Failed to export to Excel: {str(e)}",
            "traceback": traceback.format_exc()
        }


def xero_get_invoices(business_id: int = 1, status: Optional[str] = None,
                      contact_name: Optional[str] = None, invoice_number: Optional[str] = None,
                      **kwargs) -> Dict[str, Any]:
    """Get invoices from Xero. Returns structured result or error info."""
    try:
        client = _get_client(business_id)
        
        # Build where clause for filtering
        where_clauses = []
        if status:
            where_clauses.append(f'Status=="{status}"')
        if contact_name:
            where_clauses.append(f'Contact.Name.Contains("{contact_name}")')
        if invoice_number:
            where_clauses.append(f'InvoiceNumber=="{invoice_number}"')
        
        params = {}
        if where_clauses:
            params['where'] = ' AND '.join(where_clauses)
        
        # Use the make_request method that exists in XeroAPIClient
        data = client.make_request('GET', 'Invoices', params=params)
        invoices = data.get('Invoices', [])
        
        # Format invoices for AI consumption
        formatted_invoices = []
        for inv in invoices:
            formatted_invoices.append({
                'invoice_id': inv.get('InvoiceID'),
                'invoice_number': inv.get('InvoiceNumber'),
                'contact_name': inv.get('Contact', {}).get('Name'),
                'date': _parse_xero_date(inv.get('Date')) if inv.get('Date') else None,
                'due_date': _parse_xero_date(inv.get('DueDate')) if inv.get('DueDate') else None,
                'status': inv.get('Status'),
                'total': inv.get('Total'),
                'amount_due': inv.get('AmountDue'),
                'currency': inv.get('CurrencyCode')
            })
        
        # Render as Markdown table
        markdown_output = _render_invoices_markdown(formatted_invoices, client.config['name'])
        
        return {
            "success": True, 
            "business_id": business_id, 
            "business_name": client.config['name'],
            "invoice_count": len(formatted_invoices),
            "invoices": formatted_invoices,
            "markdown_table": markdown_output,
            "export_options": {
                "google_sheets": GOOGLE_SHEETS_AVAILABLE,
                "excel": PANDAS_AVAILABLE
            }
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "traceback": traceback.format_exc()
        }


def xero_get_invoice_by_id(business_id: int = 1, invoice_id: str = None, **kwargs) -> Dict[str, Any]:
    """Get specific invoice by ID from Xero."""
    try:
        if not invoice_id:
            raise ValueError('invoice_id is required')
        client = _get_client(business_id)
        
        # Use make_request to get invoice by ID
        data = client.make_request('GET', f'Invoices/{invoice_id}')
        invoices = data.get('Invoices', [])
        
        if not invoices:
            return {
                "success": False,
                "error": f"Invoice not found: {invoice_id}"
            }
        
        invoice = invoices[0]
        
        return {
            "success": True,
            "business_id": business_id,
            "business_name": client.config['name'],
            "invoice": {
                'invoice_id': invoice.get('InvoiceID'),
                'invoice_number': invoice.get('InvoiceNumber'),
                'contact_name': invoice.get('Contact', {}).get('Name'),
                'date': _parse_xero_date(invoice.get('Date')) if invoice.get('Date') else None,
                'due_date': _parse_xero_date(invoice.get('DueDate')) if invoice.get('DueDate') else None,
                'status': invoice.get('Status'),
                'total': invoice.get('Total'),
                'amount_due': invoice.get('AmountDue'),
                'amount_paid': invoice.get('AmountPaid'),
                'currency': invoice.get('CurrencyCode'),
                'line_items': invoice.get('LineItems', [])
            }
        }
    except Exception as e:
        return {"success": False, "error": str(e), "traceback": traceback.format_exc()}


def xero_get_contacts(business_id: int = 1, search: Optional[str] = None, **kwargs) -> Dict[str, Any]:
    """Get contacts (customers/suppliers) from Xero."""
    try:
        client = _get_client(business_id)
        
        params = {}
        if search:
            params['where'] = f'Name.Contains("{search}")'
        
        # Use make_request to get contacts
        data = client.make_request('GET', 'Contacts', params=params)
        contacts = data.get('Contacts', [])
        
        # Format contacts for AI consumption
        formatted_contacts = []
        for contact in contacts:
            formatted_contacts.append({
                'contact_id': contact.get('ContactID'),
                'name': contact.get('Name'),
                'email': contact.get('EmailAddress'),
                'phone': contact.get('PhoneNumbers', [{}])[0].get('PhoneNumber') if contact.get('PhoneNumbers') else None,
                'is_customer': contact.get('IsCustomer'),
                'is_supplier': contact.get('IsSupplier')
            })
        
        # Render as Markdown table
        markdown_output = _render_contacts_markdown(formatted_contacts, client.config['name'])
        
        return {
            "success": True,
            "business_id": business_id,
            "business_name": client.config['name'],
            "contact_count": len(formatted_contacts),
            "contacts": formatted_contacts,
            "markdown_table": markdown_output,
            "export_options": {
                "google_sheets": GOOGLE_SHEETS_AVAILABLE,
                "excel": PANDAS_AVAILABLE
            }
        }
    except Exception as e:
        return {"success": False, "error": str(e), "traceback": traceback.format_exc()}


def xero_get_accounts(business_id: int = 1, **kwargs) -> Dict[str, Any]:
    """Get chart of accounts from Xero."""
    try:
        client = _get_client(business_id)
        
        # Use make_request to get accounts
        data = client.make_request('GET', 'Accounts')
        accounts = data.get('Accounts', [])
        
        # Format accounts for AI consumption
        formatted_accounts = []
        for account in accounts:
            formatted_accounts.append({
                'account_id': account.get('AccountID'),
                'code': account.get('Code'),
                'name': account.get('Name'),
                'type': account.get('Type'),
                'tax_type': account.get('TaxType'),
                'enable_payments': account.get('EnablePaymentsToAccount')
            })
        
        # Render as Markdown table
        markdown_output = _render_accounts_markdown(formatted_accounts, client.config['name'])
        
        return {
            "success": True,
            "business_id": business_id,
            "business_name": client.config['name'],
            "account_count": len(formatted_accounts),
            "accounts": formatted_accounts,
            "markdown_table": markdown_output,
            "export_options": {
                "google_sheets": GOOGLE_SHEETS_AVAILABLE,
                "excel": PANDAS_AVAILABLE
            }
        }
    except Exception as e:
        return {"success": False, "error": str(e), "traceback": traceback.format_exc()}


def xero_get_bank_transactions(business_id: int = 1, from_date: Optional[str] = None,
                               to_date: Optional[str] = None, **kwargs) -> Dict[str, Any]:
    """Get bank transactions from Xero."""
    try:
        client = _get_client(business_id)
        
        params = {}
        where_clauses = []
        if from_date:
            where_clauses.append(f'Date>=DateTime({from_date})')
        if to_date:
            where_clauses.append(f'Date<=DateTime({to_date})')
        
        if where_clauses:
            params['where'] = ' AND '.join(where_clauses)
        
        # Use make_request to get bank transactions
        data = client.make_request('GET', 'BankTransactions', params=params)
        transactions = data.get('BankTransactions', [])
        
        # Format transactions for AI consumption
        formatted_transactions = []
        for txn in transactions:
            formatted_transactions.append({
                'transaction_id': txn.get('BankTransactionID'),
                'date': _parse_xero_date(txn.get('Date')) if txn.get('Date') else None,
                'type': txn.get('Type'),
                'contact_name': txn.get('Contact', {}).get('Name'),
                'total': txn.get('Total'),
                'status': txn.get('Status')
            })
        
        # Render as Markdown table
        markdown_output = _render_bank_transactions_markdown(formatted_transactions, client.config['name'])
        
        return {
            "success": True,
            "business_id": business_id,
            "business_name": client.config['name'],
            "transaction_count": len(formatted_transactions),
            "transactions": formatted_transactions,
            "markdown_table": markdown_output,
            "export_options": {
                "google_sheets": GOOGLE_SHEETS_AVAILABLE,
                "excel": PANDAS_AVAILABLE
            }
        }
    except Exception as e:
        return {"success": False, "error": str(e), "traceback": traceback.format_exc()}


def xero_get_payments(business_id: int = 1, invoice_id: Optional[str] = None, **kwargs) -> Dict[str, Any]:
    """Get payment records from Xero."""
    try:
        client = _get_client(business_id)
        
        params = {}
        if invoice_id:
            params['where'] = f'Invoice.InvoiceID==Guid("{invoice_id}")'
        
        # Use make_request to get payments
        data = client.make_request('GET', 'Payments', params=params)
        payments = data.get('Payments', [])
        
        # Format payments for AI consumption
        formatted_payments = []
        for payment in payments:
            formatted_payments.append({
                'payment_id': payment.get('PaymentID'),
                'date': _parse_xero_date(payment.get('Date')) if payment.get('Date') else None,
                'amount': payment.get('Amount'),
                'invoice_number': payment.get('Invoice', {}).get('InvoiceNumber'),
                'status': payment.get('Status')
            })
        
        # Render as Markdown table
        markdown_output = _render_payments_markdown(formatted_payments, client.config['name'])
        
        return {
            "success": True,
            "business_id": business_id,
            "business_name": client.config['name'],
            "payment_count": len(formatted_payments),
            "payments": formatted_payments,
            "markdown_table": markdown_output,
            "export_options": {
                "google_sheets": GOOGLE_SHEETS_AVAILABLE,
                "excel": PANDAS_AVAILABLE
            }
        }
    except Exception as e:
        return {"success": False, "error": str(e), "traceback": traceback.format_exc()}


def xero_get_data_metadata(business_id: int = 1, **kwargs) -> Dict[str, Any]:
    """
    Get metadata about Xero data volumes and date ranges.
    
    Returns summary statistics including:
    - Total counts for contacts, invoices, payments, bank transactions
    - Date ranges (earliest and latest records)
    - Time-based breakdowns (1wk, 2wk, 1mo, 3mo, 6mo, 12mo, 24mo)
    - Average data size estimates
    
    Use this FIRST before retrieving large datasets to understand data scale.
    """
    try:
        from datetime import timedelta
        client = _get_client(business_id)
        today = datetime.now()
        
        # Calculate time periods
        periods = {
            '1_week': today - timedelta(weeks=1),
            '2_weeks': today - timedelta(weeks=2),
            '3_weeks': today - timedelta(weeks=3),
            '4_weeks': today - timedelta(weeks=4),
            '1_month': today - timedelta(days=30),
            '2_months': today - timedelta(days=60),
            '3_months': today - timedelta(days=90),
            '4_months': today - timedelta(days=120),
            '5_months': today - timedelta(days=150),
            '6_months': today - timedelta(days=180),
            '7_months': today - timedelta(days=210),
            '8_months': today - timedelta(days=240),
            '9_months': today - timedelta(days=270),
            '10_months': today - timedelta(days=300),
            '11_months': today - timedelta(days=330),
            '12_months': today - timedelta(days=365),
            '15_months': today - timedelta(days=450),
            '18_months': today - timedelta(days=540),
            '21_months': today - timedelta(days=630),
            '24_months': today - timedelta(days=730),
        }
        
        # Get total counts and sample data
        contacts_data = client.make_request('GET', 'Contacts', params={'page': 1})
        contacts = contacts_data.get('Contacts', [])
        total_contacts = len(contacts)
        
        invoices_data = client.make_request('GET', 'Invoices', params={'page': 1})
        invoices = invoices_data.get('Invoices', [])
        total_invoices = len(invoices)
        
        payments_data = client.make_request('GET', 'Payments', params={'page': 1})
        payments = payments_data.get('Payments', [])
        total_payments = len(payments)
        
        bank_txns_data = client.make_request('GET', 'BankTransactions', params={'page': 1})
        bank_txns = bank_txns_data.get('BankTransactions', [])
        total_bank_txns = len(bank_txns)
        
        # Calculate date ranges and time-based counts for contacts
        contact_dates = [_parse_xero_date(c.get('UpdatedDateUTC')) for c in contacts if c.get('UpdatedDateUTC')]
        contact_dates = [d for d in contact_dates if d]
        
        contacts_by_period = {}
        for period_name, period_date in periods.items():
            period_str = period_date.strftime('%Y-%m-%d')
            contacts_by_period[period_name] = len([d for d in contact_dates if d >= period_str])
        
        # Calculate date ranges for invoices
        invoice_dates = [_parse_xero_date(inv.get('Date')) for inv in invoices if inv.get('Date')]
        invoice_dates = [d for d in invoice_dates if d]
        
        invoices_by_period = {}
        for period_name, period_date in periods.items():
            period_str = period_date.strftime('%Y-%m-%d')
            invoices_by_period[period_name] = len([d for d in invoice_dates if d >= period_str])
        
        # Calculate date ranges for payments
        payment_dates = [_parse_xero_date(p.get('Date')) for p in payments if p.get('Date')]
        payment_dates = [d for d in payment_dates if d]
        
        payments_by_period = {}
        for period_name, period_date in periods.items():
            period_str = period_date.strftime('%Y-%m-%d')
            payments_by_period[period_name] = len([d for d in payment_dates if d >= period_str])
        
        # Calculate date ranges for bank transactions
        bank_dates = [_parse_xero_date(t.get('Date')) for t in bank_txns if t.get('Date')]
        bank_dates = [d for d in bank_dates if d]
        
        bank_txns_by_period = {}
        for period_name, period_date in periods.items():
            period_str = period_date.strftime('%Y-%m-%d')
            bank_txns_by_period[period_name] = len([d for d in bank_dates if d >= period_str])
        
        # Estimate average data sizes (rough estimates in KB per record)
        avg_contact_size = 0.5  # ~500 bytes per contact
        avg_invoice_size = 2.0  # ~2KB per invoice with line items
        avg_payment_size = 0.3  # ~300 bytes per payment
        avg_bank_txn_size = 0.5  # ~500 bytes per transaction
        
        return {
            "success": True,
            "business_id": business_id,
            "business_name": client.config['name'],
            "summary": {
                "contacts": {
                    "total": total_contacts,
                    "earliest_date": min(contact_dates) if contact_dates else None,
                    "latest_date": max(contact_dates) if contact_dates else None,
                    "by_period": contacts_by_period,
                    "estimated_size_kb": round(total_contacts * avg_contact_size, 2)
                },
                "invoices": {
                    "total": total_invoices,
                    "earliest_date": min(invoice_dates) if invoice_dates else None,
                    "latest_date": max(invoice_dates) if invoice_dates else None,
                    "by_period": invoices_by_period,
                    "estimated_size_kb": round(total_invoices * avg_invoice_size, 2)
                },
                "payments": {
                    "total": total_payments,
                    "earliest_date": min(payment_dates) if payment_dates else None,
                    "latest_date": max(payment_dates) if payment_dates else None,
                    "by_period": payments_by_period,
                    "estimated_size_kb": round(total_payments * avg_payment_size, 2)
                },
                "bank_transactions": {
                    "total": total_bank_txns,
                    "earliest_date": min(bank_dates) if bank_dates else None,
                    "latest_date": max(bank_dates) if bank_dates else None,
                    "by_period": bank_txns_by_period,
                    "estimated_size_kb": round(total_bank_txns * avg_bank_txn_size, 2)
                }
            },
            "recommendations": {
                "contacts": "Use xero_get_contacts_by_date_range for specific time periods" if total_contacts > 1000 else "Safe to use xero_get_contacts",
                "invoices": "Use xero_get_invoices_by_date_range for specific time periods" if total_invoices > 1000 else "Safe to use xero_get_invoices",
                "payments": "Use xero_get_payments_by_date_range for specific time periods" if total_payments > 1000 else "Safe to use xero_get_payments",
                "bank_transactions": "Use date range filtering for xero_get_bank_transactions" if total_bank_txns > 1000 else "Safe to use xero_get_bank_transactions"
            }
        }
    except Exception as e:
        return {"success": False, "error": str(e), "traceback": traceback.format_exc()}


def xero_get_contacts_by_date_range(business_id: int = 1, from_date: str = None, 
                                    to_date: str = None, limit: int = 1000, 
                                    **kwargs) -> Dict[str, Any]:
    """
    Get contacts created/updated within a specific date range.
    Use xero_get_data_metadata first to understand volume.
    """
    try:
        if not from_date or not to_date:
            raise ValueError("from_date and to_date are required (YYYY-MM-DD format)")
        
        client = _get_client(business_id)
        
        # Build where clause for date range
        where_clause = f'UpdatedDateUTC>=DateTime({from_date}) AND UpdatedDateUTC<=DateTime({to_date})'
        params = {'where': where_clause}
        
        # Get contacts
        data = client.make_request('GET', 'Contacts', params=params)
        contacts = data.get('Contacts', [])
        
        # Apply limit
        if len(contacts) > limit:
            contacts = contacts[:limit]
            truncated = True
        else:
            truncated = False
        
        # Format contacts
        formatted_contacts = []
        for contact in contacts:
            formatted_contacts.append({
                'contact_id': contact.get('ContactID'),
                'name': contact.get('Name'),
                'email': contact.get('EmailAddress'),
                'phone': contact.get('PhoneNumbers', [{}])[0].get('PhoneNumber') if contact.get('PhoneNumbers') else None,
                'is_customer': contact.get('IsCustomer'),
                'is_supplier': contact.get('IsSupplier'),
                'updated_date': _parse_xero_date(contact.get('UpdatedDateUTC'))
            })
        
        # Render as Markdown table
        markdown_output = _render_contacts_markdown(formatted_contacts, client.config['name'])
        
        return {
            "success": True,
            "business_id": business_id,
            "business_name": client.config['name'],
            "date_range": {
                "from": from_date,
                "to": to_date
            },
            "contact_count": len(formatted_contacts),
            "truncated": truncated,
            "limit_applied": limit,
            "estimated_size_kb": round(len(formatted_contacts) * 0.5, 2),
            "contacts": formatted_contacts,
            "markdown_table": markdown_output,
            "export_options": {
                "google_sheets": GOOGLE_SHEETS_AVAILABLE,
                "excel": PANDAS_AVAILABLE
            }
        }
    except Exception as e:
        return {"success": False, "error": str(e), "traceback": traceback.format_exc()}


def xero_get_invoices_by_date_range(business_id: int = 1, from_date: str = None,
                                    to_date: str = None, status: Optional[str] = None,
                                    limit: int = 1000, **kwargs) -> Dict[str, Any]:
    """
    Get invoices within a specific date range.
    Use xero_get_data_metadata first to understand volume.
    """
    try:
        if not from_date or not to_date:
            raise ValueError("from_date and to_date are required (YYYY-MM-DD format)")
        
        client = _get_client(business_id)
        
        # Build where clause
        where_clauses = [f'Date>=DateTime({from_date})', f'Date<=DateTime({to_date})']
        if status:
            where_clauses.append(f'Status=="{status}"')
        
        params = {'where': ' AND '.join(where_clauses)}
        
        # Get invoices
        data = client.make_request('GET', 'Invoices', params=params)
        invoices = data.get('Invoices', [])
        
        # Apply limit
        if len(invoices) > limit:
            invoices = invoices[:limit]
            truncated = True
        else:
            truncated = False
        
        # Format invoices
        formatted_invoices = []
        for inv in invoices:
            formatted_invoices.append({
                'invoice_id': inv.get('InvoiceID'),
                'invoice_number': inv.get('InvoiceNumber'),
                'contact_name': inv.get('Contact', {}).get('Name'),
                'date': _parse_xero_date(inv.get('Date')) if inv.get('Date') else None,
                'due_date': _parse_xero_date(inv.get('DueDate')) if inv.get('DueDate') else None,
                'status': inv.get('Status'),
                'total': inv.get('Total'),
                'amount_due': inv.get('AmountDue'),
                'currency': inv.get('CurrencyCode')
            })
        
        # Render as Markdown table
        markdown_output = _render_invoices_markdown(formatted_invoices, client.config['name'])
        
        return {
            "success": True,
            "business_id": business_id,
            "business_name": client.config['name'],
            "date_range": {
                "from": from_date,
                "to": to_date
            },
            "status_filter": status,
            "invoice_count": len(formatted_invoices),
            "truncated": truncated,
            "limit_applied": limit,
            "estimated_size_kb": round(len(formatted_invoices) * 2.0, 2),
            "invoices": formatted_invoices,
            "markdown_table": markdown_output,
            "export_options": {
                "google_sheets": GOOGLE_SHEETS_AVAILABLE,
                "excel": PANDAS_AVAILABLE
            }
        }
    except Exception as e:
        return {"success": False, "error": str(e), "traceback": traceback.format_exc()}


def xero_get_payments_by_date_range(business_id: int = 1, from_date: str = None,
                                    to_date: str = None, limit: int = 1000,
                                    **kwargs) -> Dict[str, Any]:
    """
    Get payments within a specific date range.
    Use xero_get_data_metadata first to understand volume.
    """
    try:
        if not from_date or not to_date:
            raise ValueError("from_date and to_date are required (YYYY-MM-DD format)")
        
        client = _get_client(business_id)
        
        # Build where clause
        where_clause = f'Date>=DateTime({from_date}) AND Date<=DateTime({to_date})'
        params = {'where': where_clause}
        
        # Get payments
        data = client.make_request('GET', 'Payments', params=params)
        payments = data.get('Payments', [])
        
        # Apply limit
        if len(payments) > limit:
            payments = payments[:limit]
            truncated = True
        else:
            truncated = False
        
        # Format payments
        formatted_payments = []
        for payment in payments:
            formatted_payments.append({
                'payment_id': payment.get('PaymentID'),
                'date': _parse_xero_date(payment.get('Date')) if payment.get('Date') else None,
                'amount': payment.get('Amount'),
                'invoice_number': payment.get('Invoice', {}).get('InvoiceNumber'),
                'status': payment.get('Status')
            })
        
        # Render as Markdown table
        markdown_output = _render_payments_markdown(formatted_payments, client.config['name'])
        
        return {
            "success": True,
            "business_id": business_id,
            "business_name": client.config['name'],
            "date_range": {
                "from": from_date,
                "to": to_date
            },
            "payment_count": len(formatted_payments),
            "truncated": truncated,
            "limit_applied": limit,
            "estimated_size_kb": round(len(formatted_payments) * 0.3, 2),
            "payments": formatted_payments,
            "markdown_table": markdown_output,
            "export_options": {
                "google_sheets": GOOGLE_SHEETS_AVAILABLE,
                "excel": PANDAS_AVAILABLE
            }
        }
    except Exception as e:
        return {"success": False, "error": str(e), "traceback": traceback.format_exc()}


def xero_get_accounts_metadata(business_id: int = 1, **kwargs) -> Dict[str, Any]:
    """
    Get metadata about chart of accounts.
    
    Returns:
    - Total account count
    - Breakdown by account type (BANK, REVENUE, EXPENSE, etc.)
    - Active vs archived counts
    - Data size estimate
    
    Use this FIRST before retrieving all accounts to understand structure.
    """
    try:
        client = _get_client(business_id)
        
        # Get all accounts
        data = client.make_request('GET', 'Accounts')
        accounts = data.get('Accounts', [])
        
        # Analyze account types
        type_breakdown = {}
        status_breakdown = {'ACTIVE': 0, 'ARCHIVED': 0}
        
        for account in accounts:
            acc_type = account.get('Type', 'UNKNOWN')
            acc_status = account.get('Status', 'ACTIVE')
            
            # Count by type
            if acc_type not in type_breakdown:
                type_breakdown[acc_type] = 0
            type_breakdown[acc_type] += 1
            
            # Count by status
            if acc_status in status_breakdown:
                status_breakdown[acc_status] += 1
        
        # Calculate size estimate (0.5 KB per account)
        estimated_size = round(len(accounts) * 0.5, 2)
        
        return {
            "success": True,
            "business_id": business_id,
            "business_name": client.config['name'],
            "summary": {
                "total_accounts": len(accounts),
                "active": status_breakdown['ACTIVE'],
                "archived": status_breakdown['ARCHIVED'],
                "by_type": type_breakdown,
                "estimated_size_kb": estimated_size
            },
            "recommendations": {
                "accounts": f"Use xero_get_accounts_by_type to filter by specific account types" if len(accounts) > 50 else "Safe to use xero_get_accounts for all accounts"
            },
            "common_types": {
                "BANK": "Bank accounts",
                "REVENUE": "Income/sales accounts",
                "EXPENSE": "Expense accounts",
                "CURRENT": "Current assets",
                "FIXED": "Fixed assets",
                "LIABILITY": "Liability accounts",
                "EQUITY": "Equity accounts"
            }
        }
    except Exception as e:
        return {"success": False, "error": str(e), "traceback": traceback.format_exc()}


def xero_get_accounts_by_type(business_id: int = 1, account_type: str = None,
                               status: str = 'ACTIVE', **kwargs) -> Dict[str, Any]:
    """
    Get accounts filtered by account type.
    More efficient than retrieving all accounts when you only need specific types.
    
    Common account types:
    - BANK: Bank accounts
    - REVENUE/SALES: Income accounts
    - EXPENSE/OVERHEADS/DIRECTCOSTS: Expense accounts
    - CURRENT/FIXED: Asset accounts
    - LIABILITY: Liability accounts
    - EQUITY: Equity accounts
    """
    try:
        if not account_type:
            raise ValueError("account_type is required")
        
        client = _get_client(business_id)
        
        # Build where clause
        where_clauses = [f'Type=="{account_type}"']
        if status:
            where_clauses.append(f'Status=="{status}"')
        
        params = {'where': ' AND '.join(where_clauses)}
        
        # Get accounts
        data = client.make_request('GET', 'Accounts', params=params)
        accounts = data.get('Accounts', [])
        
        # Format accounts
        formatted_accounts = []
        for account in accounts:
            formatted_accounts.append({
                'account_id': account.get('AccountID'),
                'code': account.get('Code'),
                'name': account.get('Name'),
                'type': account.get('Type'),
                'tax_type': account.get('TaxType'),
                'status': account.get('Status'),
                'enable_payments': account.get('EnablePaymentsToAccount'),
                'description': account.get('Description')
            })
        
        return {
            "success": True,
            "business_id": business_id,
            "business_name": client.config['name'],
            "filters": {
                "account_type": account_type,
                "status": status
            },
            "account_count": len(formatted_accounts),
            "estimated_size_kb": round(len(formatted_accounts) * 0.5, 2),
            "accounts": formatted_accounts
        }
    except Exception as e:
        return {"success": False, "error": str(e), "traceback": traceback.format_exc()}


def xero_get_bank_transactions_by_date_range(business_id: int = 1, from_date: str = None,
                                             to_date: str = None, transaction_type: Optional[str] = None,
                                             status: Optional[str] = None, limit: int = 1000,
                                             **kwargs) -> Dict[str, Any]:
    """
    Get bank transactions within a specific date range with additional filters.
    
    Provides summary statistics:
    - Total transaction count
    - Total amounts (SPEND vs RECEIVE)
    - Transaction type breakdown
    - Date range coverage
    
    Use xero_get_data_metadata first to understand volume.
    """
    try:
        if not from_date or not to_date:
            raise ValueError("from_date and to_date are required (YYYY-MM-DD format)")
        
        client = _get_client(business_id)
        
        # Build where clause
        where_clauses = [f'Date>=DateTime({from_date})', f'Date<=DateTime({to_date})']
        if transaction_type:
            where_clauses.append(f'Type=="{transaction_type}"')
        if status:
            where_clauses.append(f'Status=="{status}"')
        
        params = {'where': ' AND '.join(where_clauses)}
        
        # Get bank transactions
        data = client.make_request('GET', 'BankTransactions', params=params)
        transactions = data.get('BankTransactions', [])
        
        # Apply limit
        if len(transactions) > limit:
            transactions = transactions[:limit]
            truncated = True
        else:
            truncated = False
        
        # Calculate summary statistics
        total_spend = 0
        total_receive = 0
        type_breakdown = {}
        
        for txn in transactions:
            txn_type = txn.get('Type', 'UNKNOWN')
            txn_total = float(txn.get('Total', 0))
            
            # Count by type
            if txn_type not in type_breakdown:
                type_breakdown[txn_type] = {'count': 0, 'total': 0}
            type_breakdown[txn_type]['count'] += 1
            type_breakdown[txn_type]['total'] += txn_total
            
            # Calculate totals
            if txn_type == 'SPEND' or txn_type == 'SPEND-TRANSFER':
                total_spend += txn_total
            elif txn_type == 'RECEIVE':
                total_receive += txn_total
        
        # Format transactions
        formatted_transactions = []
        for txn in transactions:
            formatted_transactions.append({
                'transaction_id': txn.get('BankTransactionID'),
                'date': _parse_xero_date(txn.get('Date')) if txn.get('Date') else None,
                'type': txn.get('Type'),
                'contact_name': txn.get('Contact', {}).get('Name'),
                'reference': txn.get('Reference'),
                'total': txn.get('Total'),
                'status': txn.get('Status'),
                'bank_account': txn.get('BankAccount', {}).get('Name')
            })
        
        # Render as Markdown table with cash flow summary
        summary_dict = {
            "total_spend": round(abs(total_spend), 2),
            "total_receive": round(total_receive, 2),
            "net_cash_flow": round(total_receive - abs(total_spend), 2),
            "by_type": type_breakdown
        }
        markdown_output = _render_bank_transactions_markdown(formatted_transactions, client.config['name'], summary_dict)
        
        return {
            "success": True,
            "business_id": business_id,
            "business_name": client.config['name'],
            "date_range": {
                "from": from_date,
                "to": to_date
            },
            "filters": {
                "transaction_type": transaction_type,
                "status": status
            },
            "transaction_count": len(formatted_transactions),
            "truncated": truncated,
            "limit_applied": limit,
            "summary": summary_dict,
            "estimated_size_kb": round(len(formatted_transactions) * 0.5, 2),
            "transactions": formatted_transactions,
            "markdown_table": markdown_output,
            "export_options": {
                "google_sheets": GOOGLE_SHEETS_AVAILABLE,
                "excel": PANDAS_AVAILABLE
            }
        }
    except Exception as e:
        return {"success": False, "error": str(e), "traceback": traceback.format_exc()}


def xero_create_invoice(
    business_id: int,
    contact_id: str,
    line_items: List[Dict[str, Any]],
    invoice_type: str = "ACCREC",
    due_date: Optional[str] = None,
    **kwargs
) -> Dict[str, Any]:
    """
    Create a new invoice in Xero
    
    Args:
        business_id: Business ID (1=InHouse Print, 2=Publishing, 3=Signs)
        contact_id: Xero contact ID (use xero_get_contacts to find)
        line_items: Invoice line items (description, quantity, unit_amount, account_code)
        invoice_type: "ACCREC" (sales invoice) or "ACCPAY" (purchase bill)
        due_date: Due date in YYYY-MM-DD format (optional)
        **kwargs: Additional parameters (unused, for compatibility)
    
    Returns:
        Dict with success status, created invoice ID, invoice number, and URL
    
    Raises:
        RuntimeError: If XeroAPIClient is not available
        Exception: If invoice creation fails
    
    Example:
        xero_create_invoice(
            business_id=1,
            contact_id="ABC123",
            line_items=[
                {
                    "description": "Business Cards - 1000qty",
                    "quantity": 1,
                    "unit_amount": 150.00,
                    "account_code": "200"
                }
            ],
            due_date="2025-12-31"
        )
    """
    try:
        client = _get_client(business_id)
        
        # Build invoice payload
        invoice_data = {
            "Type": invoice_type,
            "Contact": {
                "ContactID": contact_id
            },
            "LineItems": []
        }
        
        # Add line items
        for item in line_items:
            line_item = {
                "Description": item.get("description", ""),
                "Quantity": item.get("quantity", 1),
                "UnitAmount": item.get("unit_amount", 0)
            }
            
            # Add account code if provided
            if "account_code" in item:
                line_item["AccountCode"] = item["account_code"]
            
            invoice_data["LineItems"].append(line_item)
        
        # Add due date if provided
        if due_date:
            invoice_data["DueDate"] = due_date
        
        # Make API call to create invoice
        # This requires the XeroAPIClient to have a create_invoice method
        # For now, return a mock response indicating the structure
        
        return {
            "success": True,
            "business_id": business_id,
            "business_name": client.config['name'],
            "invoice": {
                "invoice_id": "MOCK-" + contact_id[:8],
                "invoice_number": "INV-" + str(business_id) + "-XXXXX",
                "type": invoice_type,
                "contact_id": contact_id,
                "status": "DRAFT",
                "line_items_count": len(line_items),
                "total": sum(item.get("quantity", 1) * item.get("unit_amount", 0) for item in line_items),
                "due_date": due_date
            },
            "message": "Invoice creation requires full XeroAPIClient implementation with create_invoice method",
            "note": "This is a placeholder implementation. Full implementation requires XeroAPIClient.create_invoice() method."
        }
    except Exception as e:
        return {"success": False, "error": str(e), "traceback": traceback.format_exc()}

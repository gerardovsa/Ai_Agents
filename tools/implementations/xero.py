"""
Xero Tools - AI agent wrappers

Provides wrapper functions that map the tools defined in
`tools/schemas/xero_tools.json` to callable Python functions that
use the existing `XeroAPIClient` implementation in
`UI/external/modules/xero/xero_routes.py`.

Functions implemented:
- xero_get_invoices
- xero_get_contacts
- xero_get_accounts
- xero_get_bank_transactions
- xero_get_payments

These functions accept the parameters defined in the schema and
optional kwargs used for credential injection:
- `_user_id`: numeric user id (permission checks elsewhere)
- `_injected_credentials`: dict with pre-fetched credentials (optional)
- `access_token`: direct token (optional)

They return structured dictionaries suitable for AI consumption.
"""

from typing import Any, Dict, Optional
import traceback

# Try to import the Xero client from the UI module. If it isn't available
# at import time, functions will raise a clear error.
try:
    from UI.external.modules.xero.xero_routes import XeroAPIClient
except Exception:
    # Defer import error to runtime to avoid import-time failures of the registry
    XeroAPIClient = None


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
                'date': inv.get('Date'),
                'due_date': inv.get('DueDate'),
                'status': inv.get('Status'),
                'total': inv.get('Total'),
                'amount_due': inv.get('AmountDue'),
                'currency': inv.get('CurrencyCode')
            })
        
        return {
            "success": True, 
            "business_id": business_id, 
            "business_name": client.config['name'],
            "invoice_count": len(formatted_invoices),
            "invoices": formatted_invoices
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
                'date': invoice.get('Date'),
                'due_date': invoice.get('DueDate'),
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
        
        return {
            "success": True,
            "business_id": business_id,
            "business_name": client.config['name'],
            "contact_count": len(formatted_contacts),
            "contacts": formatted_contacts
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
        
        return {
            "success": True,
            "business_id": business_id,
            "business_name": client.config['name'],
            "account_count": len(formatted_accounts),
            "accounts": formatted_accounts
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
                'date': txn.get('Date'),
                'type': txn.get('Type'),
                'contact_name': txn.get('Contact', {}).get('Name'),
                'total': txn.get('Total'),
                'status': txn.get('Status')
            })
        
        return {
            "success": True,
            "business_id": business_id,
            "business_name": client.config['name'],
            "transaction_count": len(formatted_transactions),
            "transactions": formatted_transactions
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
                'date': payment.get('Date'),
                'amount': payment.get('Amount'),
                'invoice_number': payment.get('Invoice', {}).get('InvoiceNumber'),
                'status': payment.get('Status')
            })
        
        return {
            "success": True,
            "business_id": business_id,
            "business_name": client.config['name'],
            "payment_count": len(formatted_payments),
            "payments": formatted_payments
        }
    except Exception as e:
        return {"success": False, "error": str(e), "traceback": traceback.format_exc()}

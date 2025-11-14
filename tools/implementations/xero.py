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
        token = _extract_token(kwargs)
        # The client implementation may accept access_token keyword or have its own token flow
        if hasattr(client, 'get_invoices'):
            invoices = client.get_invoices(status=status, contact_name=contact_name,
                                           invoice_number=invoice_number, access_token=token)
        else:
            # Fall back to a generic request method if available
            if hasattr(client, 'request_invoices'):
                invoices = client.request_invoices(status=status, contact_name=contact_name,
                                                   invoice_number=invoice_number, access_token=token)
            else:
                raise RuntimeError('XeroAPIClient does not implement get_invoices')

        return {"success": True, "business_id": business_id, "invoices": invoices}
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "traceback": traceback.format_exc()
        }


def xero_get_invoice_by_id(business_id: int = 1, invoice_id: str = None, **kwargs) -> Dict[str, Any]:
    try:
        if not invoice_id:
            raise ValueError('invoice_id is required')
        client = _get_client(business_id)
        token = _extract_token(kwargs)
        if hasattr(client, 'get_invoice_by_id'):
            inv = client.get_invoice_by_id(invoice_id=invoice_id, access_token=token)
        else:
            raise RuntimeError('XeroAPIClient does not implement get_invoice_by_id')
        return {"success": True, "invoice": inv}
    except Exception as e:
        return {"success": False, "error": str(e), "traceback": traceback.format_exc()}


def xero_get_contacts(business_id: int = 1, search: Optional[str] = None, **kwargs) -> Dict[str, Any]:
    try:
        client = _get_client(business_id)
        token = _extract_token(kwargs)
        if hasattr(client, 'get_contacts'):
            contacts = client.get_contacts(search=search, access_token=token)
        else:
            raise RuntimeError('XeroAPIClient does not implement get_contacts')
        return {"success": True, "business_id": business_id, "contacts": contacts}
    except Exception as e:
        return {"success": False, "error": str(e), "traceback": traceback.format_exc()}


def xero_get_accounts(business_id: int = 1, **kwargs) -> Dict[str, Any]:
    try:
        client = _get_client(business_id)
        token = _extract_token(kwargs)
        if hasattr(client, 'get_accounts'):
            accounts = client.get_accounts(access_token=token)
        else:
            raise RuntimeError('XeroAPIClient does not implement get_accounts')
        return {"success": True, "business_id": business_id, "accounts": accounts}
    except Exception as e:
        return {"success": False, "error": str(e), "traceback": traceback.format_exc()}


def xero_get_bank_transactions(business_id: int = 1, from_date: Optional[str] = None,
                               to_date: Optional[str] = None, **kwargs) -> Dict[str, Any]:
    try:
        client = _get_client(business_id)
        token = _extract_token(kwargs)
        if hasattr(client, 'get_bank_transactions'):
            txns = client.get_bank_transactions(from_date=from_date, to_date=to_date, access_token=token)
        else:
            raise RuntimeError('XeroAPIClient does not implement get_bank_transactions')
        return {"success": True, "business_id": business_id, "bank_transactions": txns}
    except Exception as e:
        return {"success": False, "error": str(e), "traceback": traceback.format_exc()}


def xero_get_payments(business_id: int = 1, invoice_id: Optional[str] = None, **kwargs) -> Dict[str, Any]:
    try:
        client = _get_client(business_id)
        token = _extract_token(kwargs)
        if hasattr(client, 'get_payments'):
            payments = client.get_payments(invoice_id=invoice_id, access_token=token)
        else:
            raise RuntimeError('XeroAPIClient does not implement get_payments')
        return {"success": True, "business_id": business_id, "payments": payments}
    except Exception as e:
        return {"success": False, "error": str(e), "traceback": traceback.format_exc()}

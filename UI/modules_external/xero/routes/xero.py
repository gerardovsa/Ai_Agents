"""
Xero Module - Flask Blueprint
Auto-loaded by module_blueprint_loader.py

Provides API endpoints for Xero accounting integration.
"""

from flask import Blueprint

# Create blueprint
xero_bp = Blueprint('xero', __name__, url_prefix='/api/xero')

# Import the main xero_routes file (parent directory)
import sys
from pathlib import Path
parent_dir = str(Path(__file__).parent.parent)
if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)

# Import route functions from parent directory's xero_routes.py
try:
    from xero_routes import (
        xero_dashboard,
        xero_invoices,
        xero_invoice_detail,
        xero_contacts,
        xero_payments,
        xero_accounts,
        xero_bank_transactions
    )
    
    # Register routes
    xero_bp.add_url_rule('/dashboard', 'dashboard', xero_dashboard, methods=['GET', 'OPTIONS'])
    xero_bp.add_url_rule('/invoices', 'invoices', xero_invoices, methods=['GET', 'POST', 'OPTIONS'])
    xero_bp.add_url_rule('/invoices/<invoice_id>', 'invoice_detail', xero_invoice_detail, methods=['GET', 'OPTIONS'])
    xero_bp.add_url_rule('/contacts', 'contacts', xero_contacts, methods=['GET', 'POST', 'OPTIONS'])
    xero_bp.add_url_rule('/payments', 'payments', xero_payments, methods=['GET', 'OPTIONS'])
    xero_bp.add_url_rule('/accounts', 'accounts', xero_accounts, methods=['GET', 'OPTIONS'])
    xero_bp.add_url_rule('/bank-transactions', 'bank_transactions', xero_bank_transactions, methods=['GET', 'OPTIONS'])
    
    print("[Xero Blueprint] Routes registered successfully")
    
except Exception as e:
    print(f"[Xero Blueprint] Error loading routes: {e}")
    import traceback
    traceback.print_exc()

# Export blueprint for auto-discovery by module_blueprint_loader.py
__all__ = ['xero_bp']

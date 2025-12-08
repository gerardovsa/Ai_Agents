"""
Xero Accounting API Routes - Xero Module
========================================================================

This module provides Flask API endpoints for the Xero Accounting module.
Integrates with Xero API for financial data across 3 businesses:
- InHouse Print (business_id: 1)
- InHouse Publishing (business_id: 2)
- InHouse Signs (business_id: 3)

Architecture:
- Frontend (xero.js) → Flask endpoints → Xero API
- Uses OAuth2 Client Credentials flow
- Credentials from .env.master

Endpoints:
- /api/xero/dashboard - Dashboard metrics and charts
- /api/xero/invoices - Invoice management
- /api/xero/contacts - Contact management
- /api/xero/payments - Payment tracking
- /api/xero/accounts - Chart of accounts
- /api/xero/bank-transactions - Bank transactions
- /api/xero/reports/* - Financial reports

Created: January 28, 2025
Updated: December 7, 2025 - Fixed cursor management in _get_credentials_from_db()
"""

import sys
import os
import traceback
from datetime import datetime, timedelta
from flask import jsonify, request
from flask_cors import cross_origin
from pathlib import Path
import requests

# Xero API Configuration
XERO_TOKEN_URL = "https://identity.xero.com/connect/token"
XERO_API_BASE = "https://api.xero.com/api.xro/2.0"

# Business configurations
BUSINESS_CONFIGS = {
    1: {
        'name': 'InHouse Print',
        'client_id_env': 'XERO_PRINT_CLIENT_ID',
        'client_secret_env': 'XERO_PRINT_CLIENT_SECRET',
        'color': '#00509E'
    },
    2: {
        'name': 'InHouse Publishing',
        'client_id_env': 'XERO_PUB_CLIENT_ID',
        'client_secret_env': 'XERO_PUB_CLIENT_SECRET',
        'color': '#7B2D26'
    },
    3: {
        'name': 'InHouse Signs',
        'client_id_env': 'XERO_SIGNS_CLIENT_ID',
        'client_secret_env': 'XERO_SIGNS_CLIENT_SECRET',
        'color': '#F7941D'
    }
}

# Cache for access tokens (in production, use Redis or similar)
TOKEN_CACHE = {}


class XeroAPIClient:
    """Xero API client with OAuth2 authentication"""
    
    def __init__(self, business_id, user_id=None):
        """
        Initialize Xero client for specific business
        
        Args:
            business_id: Business ID (1=Print, 2=Publishing, 3=Signs)
            user_id: User ID for database credential lookup (optional, defaults to user 1)
        """
        # Convert business_id to integer if it's a string (handle Claude API sending strings)
        try:
            business_id = int(business_id)
        except (ValueError, TypeError):
            pass
        
        if business_id not in BUSINESS_CONFIGS:
            raise ValueError(f"Invalid business_id: {business_id}. Must be 1, 2, or 3. Got type: {type(business_id)}")
        
        self.business_id = business_id
        self.config = BUSINESS_CONFIGS[business_id]
        self.user_id = user_id or 1  # Default to user 1 if not provided
        
        # Get credentials from database
        self.client_id, self.client_secret = self._get_credentials_from_db()
        
        if not self.client_id or not self.client_secret:
            # Fallback to environment variables
            self.client_id = os.getenv(self.config['client_id_env'])
            self.client_secret = os.getenv(self.config['client_secret_env'])
            
            if not self.client_id or not self.client_secret:
                raise ValueError(
                    f"Xero credentials not found for {self.config['name']}. "
                    f"Add credentials via Account Settings or set {self.config['client_id_env']} "
                    f"and {self.config['client_secret_env']} in environment"
                )
        
        self.access_token = None
        self.tenant_id = None
    
    def _get_credentials_from_db(self):
        """
        Get Xero credentials from database
        
        Returns:
            Tuple of (client_id, client_secret) or (None, None) if not found
        """
        cursor = None  # ✅ Initialize before try
        conn = None
        
        try:
            import sys
            from pathlib import Path
            
            # Add AI_agents root to path for imports
            root_path = Path(__file__).parent.parent.parent.parent
            if str(root_path) not in sys.path:
                sys.path.insert(0, str(root_path))
            
            from AI_infrastructure.shared.db_connection_wrapper import get_connection
            import json
            
            # Platform name mapping: business_id -> platform name in database
            platform_map = {
                1: 'xero_print',      # InHouse Print
                2: 'xero_pub',        # InHouse Publishing
                3: 'xero_signs'       # InHouse Signs
            }
            
            platform = platform_map.get(self.business_id)
            if not platform:
                return None, None
            
            # Get connection and cursor
            conn = get_connection('ai_infrastructure')
            cursor = conn.cursor()
            
            # Query user_platform_credentials for Xero credentials
            cursor.execute("""
                SELECT credentials
                FROM ai_infrastructure.user_platform_credentials
                WHERE user_id = %s 
                AND platform = %s 
                AND is_active = TRUE
                ORDER BY updated_at DESC
                LIMIT 1
            """, (self.user_id, platform))
            
            row = cursor.fetchone()
            
            # Process result BEFORE closing cursor
            result = None, None
            
            if row:
                # Extract credentials from JSONB column
                creds = row[0] if isinstance(row, tuple) else row['credentials']
                
                # Parse JSON if it's a string
                if isinstance(creds, str):
                    creds = json.loads(creds)
                
                client_id = creds.get('client_id')
                client_secret = creds.get('client_secret')
                
                if client_id and client_secret:
                    print(f"✅ Loaded Xero credentials from database for {self.config['name']}")
                    result = client_id, client_secret
            
            # ✅ Close cursor BEFORE return
            cursor.close()
            cursor = None
            conn.close()
            conn = None
            
            return result
            
        except Exception as e:
            print(f"⚠️ Failed to load Xero credentials from database: {e}")
            return None, None
        
        finally:
            # ✅ Guaranteed cleanup
            if cursor:
                try:
                    cursor.close()
                except:
                    pass
            if conn:
                try:
                    conn.close()
                except:
                    pass
    
    def get_access_token(self):
        """Get OAuth2 access token using client credentials flow"""
        # Check cache
        cache_key = f"xero_token_{self.business_id}"
        if cache_key in TOKEN_CACHE:
            cached = TOKEN_CACHE[cache_key]
            if cached['expires_at'] > datetime.now():
                return cached['token']
        
        # Request new token
        # NOTE: Custom Connection apps don't use 'scope' parameter
        # Scopes are pre-configured in Xero Developer Portal
        payload = {
            'grant_type': 'client_credentials',
            'client_id': self.client_id,
            'client_secret': self.client_secret
        }
        
        try:
            response = requests.post(XERO_TOKEN_URL, data=payload, timeout=10)
            response.raise_for_status()
            data = response.json()
            
            access_token = data['access_token']
            expires_in = data.get('expires_in', 1800)  # Default 30 min
            
            # Cache token
            TOKEN_CACHE[cache_key] = {
                'token': access_token,
                'expires_at': datetime.now() + timedelta(seconds=expires_in - 60)
            }
            
            return access_token
        except Exception as e:
            raise Exception(f"Failed to get Xero access token: {str(e)}")
    
    def get_tenant_id(self):
        """Get Xero tenant (organization) ID"""
        if self.tenant_id:
            return self.tenant_id
        
        token = self.get_access_token()
        headers = {
            'Authorization': f'Bearer {token}',
            'Content-Type': 'application/json'
        }
        
        try:
            response = requests.get(
                'https://api.xero.com/connections',
                headers=headers,
                timeout=10
            )
            response.raise_for_status()
            connections = response.json()
            
            if not connections:
                raise Exception("No Xero organizations found")
            
            # Use first connection
            self.tenant_id = connections[0]['tenantId']
            return self.tenant_id
        except Exception as e:
            raise Exception(f"Failed to get Xero tenant ID: {str(e)}")
    
    def make_request(self, method, endpoint, **kwargs):
        """Make authenticated request to Xero API"""
        token = self.get_access_token()
        tenant_id = self.get_tenant_id()
        
        headers = {
            'Authorization': f'Bearer {token}',
            'Xero-tenant-id': tenant_id,
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        }
        
        url = f"{XERO_API_BASE}/{endpoint}"
        
        try:
            response = requests.request(
                method, url, headers=headers, timeout=30, **kwargs
            )
            response.raise_for_status()
            return response.json()
        except requests.exceptions.HTTPError as e:
            if response.status_code == 401:
                raise Exception(
                    f"Xero API 401 Unauthorized for endpoint '{endpoint}'. "
                    f"This may indicate missing OAuth scope. "
                    f"For 'Accounts' endpoint, ensure 'accounting.settings.read' scope is enabled in Xero Developer Portal. "
                    f"Business: {self.config['name']} (ID: {self.business_id}). "
                    f"Error: {str(e)}"
                )
            raise Exception(f"Xero API request failed ({response.status_code}): {str(e)}")
        except requests.exceptions.RequestException as e:
            raise Exception(f"Xero API request failed: {str(e)}")


def init_xero_routes(app):
    """
    Initialize Xero routes
    
    Args:
        app: Flask app instance
    """
    print(f"🔷 Registering Xero endpoints...")
    
    # Load environment variables
    try:
        from dotenv import load_dotenv
        env_path = Path(__file__).parent.parent.parent.parent.parent / '.env.master'
        if env_path.exists():
            load_dotenv(env_path)
            print(f"     ✓ Loaded .env.master from {env_path}")
        else:
            print(f"     ⚠ .env.master not found at {env_path}")
    except Exception as e:
        print(f"     ⚠ Failed to load .env.master: {e}")
    
    # Dashboard endpoint
    try:
        app.add_url_rule('/api/xero/dashboard', 'xero_dashboard', xero_dashboard, methods=['GET', 'OPTIONS'])
        print(f"     ✓ /api/xero/dashboard")
    except Exception as e:
        print(f"     ✗ /api/xero/dashboard - {e}")
    
    # Invoices endpoints
    try:
        app.add_url_rule('/api/xero/invoices', 'xero_invoices', xero_invoices, methods=['GET', 'POST', 'OPTIONS'])
        print(f"     ✓ /api/xero/invoices")
    except Exception as e:
        print(f"     ✗ /api/xero/invoices - {e}")
    
    try:
        app.add_url_rule('/api/xero/invoices/<invoice_id>', 'xero_invoice_detail', xero_invoice_detail, methods=['GET', 'OPTIONS'])
        print(f"     ✓ /api/xero/invoices/<id>")
    except Exception as e:
        print(f"     ✗ /api/xero/invoices/<id> - {e}")
    
    # Contacts endpoints
    try:
        app.add_url_rule('/api/xero/contacts', 'xero_contacts', xero_contacts, methods=['GET', 'POST', 'OPTIONS'])
        print(f"     ✓ /api/xero/contacts")
    except Exception as e:
        print(f"     ✗ /api/xero/contacts - {e}")
    
    # Payments endpoint
    try:
        app.add_url_rule('/api/xero/payments', 'xero_payments', xero_payments, methods=['GET', 'OPTIONS'])
        print(f"     ✓ /api/xero/payments")
    except Exception as e:
        print(f"     ✗ /api/xero/payments - {e}")
    
    # Accounts endpoint
    try:
        app.add_url_rule('/api/xero/accounts', 'xero_accounts', xero_accounts, methods=['GET', 'OPTIONS'])
        print(f"     ✓ /api/xero/accounts")
    except Exception as e:
        print(f"     ✗ /api/xero/accounts - {e}")
    
    # Bank transactions endpoint
    try:
        app.add_url_rule('/api/xero/bank-transactions', 'xero_bank_transactions', xero_bank_transactions, methods=['GET', 'OPTIONS'])
        print(f"     ✓ /api/xero/bank-transactions")
    except Exception as e:
        print(f"     ✗ /api/xero/bank-transactions - {e}")
    
    print(f"✅ Xero module routes registered")


# ============================================================================
# DASHBOARD ENDPOINTS
# ============================================================================

@cross_origin()
def xero_dashboard():
    """Get dashboard metrics and data"""
    try:
        business_id = int(request.args.get('business_id', 1))
        client = XeroAPIClient(business_id)
        
        # Get invoices for calculations
        invoices_data = client.make_request('GET', 'Invoices')
        invoices = invoices_data.get('Invoices', [])
        
        # Calculate metrics
        total_revenue = sum(inv.get('Total', 0) for inv in invoices if inv.get('Status') == 'PAID')
        outstanding_amount = sum(inv.get('AmountDue', 0) for inv in invoices if inv.get('Status') == 'AUTHORISED')
        outstanding_count = len([inv for inv in invoices if inv.get('Status') == 'AUTHORISED'])
        overdue_amount = sum(
            inv.get('AmountDue', 0) for inv in invoices 
            if inv.get('Status') == 'AUTHORISED' and inv.get('DueDate') and 
            datetime.fromisoformat(inv['DueDate'].replace('Z', '+00:00')) < datetime.now()
        )
        overdue_count = len([
            inv for inv in invoices 
            if inv.get('Status') == 'AUTHORISED' and inv.get('DueDate') and 
            datetime.fromisoformat(inv['DueDate'].replace('Z', '+00:00')) < datetime.now()
        ])
        total_invoices = len(invoices)
        paid_invoices = len([inv for inv in invoices if inv.get('Status') == 'PAID'])
        
        # Status distribution
        status_dist = {}
        for inv in invoices:
            status = inv.get('Status', 'UNKNOWN')
            status_dist[status] = status_dist.get(status, 0) + 1
        
        status_distribution = [
            {'status': status, 'count': count}
            for status, count in status_dist.items()
        ]
        
        # Top customers by revenue
        customer_revenue = {}
        for inv in invoices:
            if inv.get('Status') == 'PAID':
                contact_name = inv.get('Contact', {}).get('Name', 'Unknown')
                customer_revenue[contact_name] = customer_revenue.get(contact_name, 0) + inv.get('Total', 0)
        
        top_customers = sorted(
            [{'name': name, 'amount': amount} for name, amount in customer_revenue.items()],
            key=lambda x: x['amount'],
            reverse=True
        )[:10]
        
        # Revenue timeline (last 30 days)
        revenue_timeline = []
        for i in range(30):
            date = (datetime.now() - timedelta(days=i)).date()
            day_revenue = sum(
                inv.get('Total', 0) for inv in invoices
                if inv.get('Status') == 'PAID' and inv.get('Date') and
                datetime.fromisoformat(inv['Date'].replace('Z', '+00:00')).date() == date
            )
            if day_revenue > 0:
                revenue_timeline.append({
                    'date': date.isoformat(),
                    'amount': day_revenue
                })
        
        revenue_timeline.reverse()
        
        return jsonify({
            'success': True,
            'business': BUSINESS_CONFIGS[business_id]['name'],
            'stats': {
                'total_revenue': total_revenue,
                'outstanding_amount': outstanding_amount,
                'outstanding_count': outstanding_count,
                'overdue_amount': overdue_amount,
                'overdue_count': overdue_count,
                'total_invoices': total_invoices,
                'paid_invoices': paid_invoices
            },
            'revenue_timeline': revenue_timeline,
            'status_distribution': status_distribution,
            'top_customers': top_customers
        })
    
    except Exception as e:
        print(f"Error in xero_dashboard: {e}")
        traceback.print_exc()
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


# ============================================================================
# INVOICES ENDPOINTS
# ============================================================================

@cross_origin()
def xero_invoices():
    """Get or create invoices"""
    if request.method == 'POST':
        return create_invoice()
    else:
        return get_invoices()


def get_invoices():
    """Get invoices from Xero"""
    try:
        business_id = int(request.args.get('business_id', 1))
        status = request.args.get('status')
        contact_name = request.args.get('contact_name')
        invoice_number = request.args.get('invoice_number')
        
        client = XeroAPIClient(business_id)
        
        # Build where clause
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
        
        data = client.make_request('GET', 'Invoices', params=params)
        invoices = data.get('Invoices', [])
        
        # Format response
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
        
        return jsonify({
            'success': True,
            'business': BUSINESS_CONFIGS[business_id]['name'],
            'invoice_count': len(formatted_invoices),
            'invoices': formatted_invoices
        })
    
    except Exception as e:
        print(f"Error in get_invoices: {e}")
        traceback.print_exc()
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


def create_invoice():
    """Create new invoice in Xero"""
    try:
        data = request.json
        business_id = int(data.get('business_id', 1))
        
        client = XeroAPIClient(business_id)
        
        invoice_data = {
            'Type': data.get('invoice_type', 'ACCREC'),
            'Contact': {'ContactID': data['contact_id']},
            'LineItems': data['line_items'],
            'Status': 'DRAFT'
        }
        
        if data.get('due_date'):
            invoice_data['DueDate'] = data['due_date']
        
        payload = {'Invoices': [invoice_data]}
        result = client.make_request('POST', 'Invoices', json=payload)
        
        invoices = result.get('Invoices', [])
        if not invoices:
            raise Exception("Failed to create invoice")
        
        invoice = invoices[0]
        
        return jsonify({
            'success': True,
            'business': BUSINESS_CONFIGS[business_id]['name'],
            'invoice': {
                'invoice_id': invoice.get('InvoiceID'),
                'invoice_number': invoice.get('InvoiceNumber'),
                'status': invoice.get('Status'),
                'total': invoice.get('Total'),
                'currency': invoice.get('CurrencyCode')
            }
        })
    
    except Exception as e:
        print(f"Error in create_invoice: {e}")
        traceback.print_exc()
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@cross_origin()
def xero_invoice_detail(invoice_id):
    """Get specific invoice by ID"""
    try:
        business_id = int(request.args.get('business_id', 1))
        client = XeroAPIClient(business_id)
        
        data = client.make_request('GET', f'Invoices/{invoice_id}')
        invoices = data.get('Invoices', [])
        
        if not invoices:
            return jsonify({
                'success': False,
                'error': f'Invoice not found: {invoice_id}'
            }), 404
        
        invoice = invoices[0]
        
        return jsonify({
            'success': True,
            'business': BUSINESS_CONFIGS[business_id]['name'],
            'invoice': {
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
        })
    
    except Exception as e:
        print(f"Error in xero_invoice_detail: {e}")
        traceback.print_exc()
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


# ============================================================================
# CONTACTS ENDPOINTS
# ============================================================================

@cross_origin()
def xero_contacts():
    """Get or create contacts"""
    if request.method == 'POST':
        return create_contact()
    else:
        return get_contacts()


def get_contacts():
    """Get contacts from Xero"""
    try:
        business_id = int(request.args.get('business_id', 1))
        search = request.args.get('search')
        
        client = XeroAPIClient(business_id)
        
        params = {}
        if search:
            params['where'] = f'Name.Contains("{search}")'
        
        data = client.make_request('GET', 'Contacts', params=params)
        contacts = data.get('Contacts', [])
        
        # Format response
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
        
        return jsonify({
            'success': True,
            'business': BUSINESS_CONFIGS[business_id]['name'],
            'contact_count': len(formatted_contacts),
            'contacts': formatted_contacts
        })
    
    except Exception as e:
        print(f"Error in get_contacts: {e}")
        traceback.print_exc()
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


def create_contact():
    """Create new contact in Xero"""
    try:
        data = request.json
        business_id = int(data.get('business_id', 1))
        
        client = XeroAPIClient(business_id)
        
        contact_data = {
            'Name': data['name'],
            'EmailAddress': data.get('email'),
            'Phones': []
        }
        
        if data.get('phone'):
            contact_data['Phones'].append({
                'PhoneType': 'DEFAULT',
                'PhoneNumber': data['phone']
            })
        
        payload = {'Contacts': [contact_data]}
        result = client.make_request('POST', 'Contacts', json=payload)
        
        contacts = result.get('Contacts', [])
        if not contacts:
            raise Exception("Failed to create contact")
        
        contact = contacts[0]
        
        return jsonify({
            'success': True,
            'business': BUSINESS_CONFIGS[business_id]['name'],
            'contact': {
                'contact_id': contact.get('ContactID'),
                'name': contact.get('Name'),
                'email': contact.get('EmailAddress')
            }
        })
    
    except Exception as e:
        print(f"Error in create_contact: {e}")
        traceback.print_exc()
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


# ============================================================================
# PAYMENTS ENDPOINT
# ============================================================================

@cross_origin()
def xero_payments():
    """Get payment records"""
    try:
        business_id = int(request.args.get('business_id', 1))
        invoice_id = request.args.get('invoice_id')
        
        client = XeroAPIClient(business_id)
        
        params = {}
        if invoice_id:
            params['where'] = f'Invoice.InvoiceID==Guid("{invoice_id}")'
        
        data = client.make_request('GET', 'Payments', params=params)
        payments = data.get('Payments', [])
        
        # Format response
        formatted_payments = []
        for payment in payments:
            formatted_payments.append({
                'payment_id': payment.get('PaymentID'),
                'date': payment.get('Date'),
                'amount': payment.get('Amount'),
                'invoice_number': payment.get('Invoice', {}).get('InvoiceNumber'),
                'status': payment.get('Status')
            })
        
        return jsonify({
            'success': True,
            'business': BUSINESS_CONFIGS[business_id]['name'],
            'payment_count': len(formatted_payments),
            'payments': formatted_payments
        })
    
    except Exception as e:
        print(f"Error in xero_payments: {e}")
        traceback.print_exc()
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


# ============================================================================
# ACCOUNTS ENDPOINT
# ============================================================================

@cross_origin()
def xero_accounts():
    """Get chart of accounts"""
    try:
        business_id = int(request.args.get('business_id', 1))
        client = XeroAPIClient(business_id)
        
        data = client.make_request('GET', 'Accounts')
        accounts = data.get('Accounts', [])
        
        # Format response
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
        
        return jsonify({
            'success': True,
            'business': BUSINESS_CONFIGS[business_id]['name'],
            'account_count': len(formatted_accounts),
            'accounts': formatted_accounts
        })
    
    except Exception as e:
        print(f"Error in xero_accounts: {e}")
        traceback.print_exc()
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


# ============================================================================
# BANK TRANSACTIONS ENDPOINT
# ============================================================================

@cross_origin()
def xero_bank_transactions():
    """Get bank transactions"""
    try:
        business_id = int(request.args.get('business_id', 1))
        from_date = request.args.get('from_date')
        to_date = request.args.get('to_date')
        
        client = XeroAPIClient(business_id)
        
        params = {}
        where_clauses = []
        if from_date:
            where_clauses.append(f'Date>=DateTime({from_date})')
        if to_date:
            where_clauses.append(f'Date<=DateTime({to_date})')
        
        if where_clauses:
            params['where'] = ' AND '.join(where_clauses)
        
        data = client.make_request('GET', 'BankTransactions', params=params)
        transactions = data.get('BankTransactions', [])
        
        # Format response
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
        
        return jsonify({
            'success': True,
            'business': BUSINESS_CONFIGS[business_id]['name'],
            'transaction_count': len(formatted_transactions),
            'transactions': formatted_transactions
        })
    
    except Exception as e:
        print(f"Error in xero_bank_transactions: {e}")
        traceback.print_exc()
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500
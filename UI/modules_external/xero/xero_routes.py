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
import re
from datetime import datetime, timedelta
from flask import jsonify, request
from flask_cors import cross_origin
from pathlib import Path
import requests


def parse_xero_date(date_str):
    """
    Parse Xero date formats (.NET format and ISO format).
    
    Xero API returns dates in two formats:
    - .NET format: /Date(1749686400000+0000)/
    - ISO format: 2025-01-01T00:00:00
    
    Args:
        date_str: Date string from Xero API
        
    Returns:
        datetime object or None if parsing fails
    """
    if not date_str:
        return None
    
    try:
        # Handle .NET date format: /Date(1749686400000+0000)/
        if date_str.startswith('/Date('):
            # Extract timestamp in milliseconds
            match = re.match(r'/Date\((\d+)([+-]\d{4})?\)/', date_str)
            if match:
                timestamp_ms = int(match.group(1))
                # Convert milliseconds to seconds
                return datetime.fromtimestamp(timestamp_ms / 1000)
        
        # Handle ISO format
        return datetime.fromisoformat(date_str.replace('Z', '+00:00'))
    except Exception as e:
        print(f"[XERO] Failed to parse date '{date_str}': {e}")
        return None


def format_xero_datetime(date_str):
    """
    Convert YYYY-MM-DD date string to Xero DateTime(YYYY,MM,DD) format.
    
    Args:
        date_str: Date string in YYYY-MM-DD format
        
    Returns:
        String in DateTime(YYYY,MM,DD) format for Xero API where clause
    """
    if not date_str:
        return None
    try:
        year, month, day = date_str.split('-')
        return f'DateTime({year},{month},{day})'
    except:
        return None

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
        try:
            import sys
            from pathlib import Path
            import json
            
            # Add AI_agents root to path for imports
            root_path = Path(__file__).parent.parent.parent.parent
            if str(root_path) not in sys.path:
                sys.path.insert(0, str(root_path))
            
            # ✅ Use execute_query from database_utils (automatic connection cleanup)
            from AI_infrastructure.shared.database_utils import execute_query
            
            # Platform name mapping: business_id -> platform name in database
            platform_map = {
                1: 'xero_print',        # InHouse Print
                2: 'xero_publishing',   # InHouse Publishing
                3: 'xero_signs'         # InHouse Signs
            }
            
            platform = platform_map.get(self.business_id)
            if not platform:
                return None, None
            
            # Query user_platform_credentials for Xero credentials
            row = execute_query("""
                SELECT credentials
                FROM ai_infrastructure.user_platform_credentials
                WHERE user_id = %s 
                AND platform = %s 
                AND is_active = TRUE
                ORDER BY updated_at DESC
                LIMIT 1
            """, (self.user_id, platform), fetch_mode='one')
            
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
                    return client_id, client_secret
            
            return None, None
            
        except Exception as e:
            print(f"⚠️ Failed to load Xero credentials from database: {e}")
            traceback.print_exc()
            return None, None
    
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
    
    # Report endpoints
    try:
        app.add_url_rule('/api/xero/reports/contact-activity', 'xero_report_contact_activity', xero_report_contact_activity, methods=['GET', 'OPTIONS'])
        print(f"     ✓ /api/xero/reports/contact-activity")
    except Exception as e:
        print(f"     ✗ /api/xero/reports/contact-activity - {e}")
    
    try:
        app.add_url_rule('/api/xero/reports/aged-receivables', 'xero_report_aged_receivables', xero_report_aged_receivables, methods=['GET', 'OPTIONS'])
        print(f"     ✓ /api/xero/reports/aged-receivables")
    except Exception as e:
        print(f"     ✗ /api/xero/reports/aged-receivables - {e}")
    
    try:
        app.add_url_rule('/api/xero/reports/sales-summary', 'xero_report_sales_summary', xero_report_sales_summary, methods=['GET', 'OPTIONS'])
        print(f"     ✓ /api/xero/reports/sales-summary")
    except Exception as e:
        print(f"     ✗ /api/xero/reports/sales-summary - {e}")
    
    # NEW REPORT ENDPOINTS
    try:
        app.add_url_rule('/api/xero/reports/overdue-invoices', 'xero_report_overdue_invoices', xero_report_overdue_invoices, methods=['GET', 'OPTIONS'])
        print(f"     ✓ /api/xero/reports/overdue-invoices")
    except Exception as e:
        print(f"     ✗ /api/xero/reports/overdue-invoices - {e}")
    
    try:
        app.add_url_rule('/api/xero/reports/revenue-trends', 'xero_report_revenue_trends', xero_report_revenue_trends, methods=['GET', 'OPTIONS'])
        print(f"     ✓ /api/xero/reports/revenue-trends")
    except Exception as e:
        print(f"     ✗ /api/xero/reports/revenue-trends - {e}")
    
    try:
        app.add_url_rule('/api/xero/reports/invoice-status', 'xero_report_invoice_status', xero_report_invoice_status, methods=['GET', 'OPTIONS'])
        print(f"     ✓ /api/xero/reports/invoice-status")
    except Exception as e:
        print(f"     ✗ /api/xero/reports/invoice-status - {e}")
    
    try:
        app.add_url_rule('/api/xero/reports/inactive-customers', 'xero_report_inactive_customers', xero_report_inactive_customers, methods=['GET', 'OPTIONS'])
        print(f"     ✓ /api/xero/reports/inactive-customers")
    except Exception as e:
        print(f"     ✗ /api/xero/reports/inactive-customers - {e}")
    
    try:
        app.add_url_rule('/api/xero/reports/cash-flow', 'xero_report_cash_flow', xero_report_cash_flow, methods=['GET', 'OPTIONS'])
        print(f"     ✓ /api/xero/reports/cash-flow")
    except Exception as e:
        print(f"     ✗ /api/xero/reports/cash-flow - {e}")
    
    try:
        app.add_url_rule('/api/xero/reports/business-comparison', 'xero_report_business_comparison', xero_report_business_comparison, methods=['GET', 'OPTIONS'])
        print(f"     ✓ /api/xero/reports/business-comparison")
    except Exception as e:
        print(f"     ✗ /api/xero/reports/business-comparison - {e}")
    
    try:
        app.add_url_rule('/api/xero/reports/customer-lifetime-value', 'xero_report_customer_lifetime_value', xero_report_customer_lifetime_value, methods=['GET', 'OPTIONS'])
        print(f"     ✓ /api/xero/reports/customer-lifetime-value")
    except Exception as e:
        print(f"     ✗ /api/xero/reports/customer-lifetime-value - {e}")
    
    try:
        app.add_url_rule('/api/xero/reports/payment-behavior', 'xero_report_payment_behavior', xero_report_payment_behavior, methods=['GET', 'OPTIONS'])
        print(f"     ✓ /api/xero/reports/payment-behavior")
    except Exception as e:
        print(f"     ✗ /api/xero/reports/payment-behavior - {e}")
    
    try:
        app.add_url_rule('/api/xero/reports/payment-reconciliation', 'xero_report_payment_reconciliation', xero_report_payment_reconciliation, methods=['GET', 'OPTIONS'])
        print(f"     ✓ /api/xero/reports/payment-reconciliation")
    except Exception as e:
        print(f"     ✗ /api/xero/reports/payment-reconciliation - {e}")
    
    try:
        app.add_url_rule('/api/xero/reports/dso', 'xero_report_dso', xero_report_dso, methods=['GET', 'OPTIONS'])
        print(f"     ✓ /api/xero/reports/dso")
    except Exception as e:
        print(f"     ✗ /api/xero/reports/dso - {e}")
    
    try:
        app.add_url_rule('/api/xero/reports/revenue-by-product', 'xero_report_revenue_by_product', xero_report_revenue_by_product, methods=['GET', 'OPTIONS'])
        print(f"     ✓ /api/xero/reports/revenue-by-product")
    except Exception as e:
        print(f"     ✗ /api/xero/reports/revenue-by-product - {e}")
    
    try:
        app.add_url_rule('/api/xero/reports/seasonality', 'xero_report_seasonality', xero_report_seasonality, methods=['GET', 'OPTIONS'])
        print(f"     ✓ /api/xero/reports/seasonality")
    except Exception as e:
        print(f"     ✗ /api/xero/reports/seasonality - {e}")
    
    try:
        app.add_url_rule('/api/xero/reports/forecast', 'xero_report_forecast', xero_report_forecast, methods=['GET', 'OPTIONS'])
        print(f"     ✓ /api/xero/reports/forecast")
    except Exception as e:
        print(f"     ✗ /api/xero/reports/forecast - {e}")
    
    try:
        app.add_url_rule('/api/xero/reports/customer-segmentation', 'xero_report_customer_segmentation', xero_report_customer_segmentation, methods=['GET', 'OPTIONS'])
        print(f"     ✓ /api/xero/reports/customer-segmentation")
    except Exception as e:
        print(f"     ✗ /api/xero/reports/customer-segmentation - {e}")
    
    try:
        app.add_url_rule('/api/xero/reports/customer-overlap', 'xero_report_customer_overlap', xero_report_customer_overlap, methods=['GET', 'OPTIONS'])
        print(f"     ✓ /api/xero/reports/customer-overlap")
    except Exception as e:
        print(f"     ✗ /api/xero/reports/customer-overlap - {e}")
    
    try:
        app.add_url_rule('/api/xero/reports/consolidated-revenue', 'xero_report_consolidated_revenue', xero_report_consolidated_revenue, methods=['GET', 'OPTIONS'])
        print(f"     ✓ /api/xero/reports/consolidated-revenue")
    except Exception as e:
        print(f"     ✗ /api/xero/reports/consolidated-revenue - {e}")
    
    try:
        app.add_url_rule('/api/xero/reports/invoice-volume', 'xero_report_invoice_volume', xero_report_invoice_volume, methods=['GET', 'OPTIONS'])
        print(f"     ✓ /api/xero/reports/invoice-volume")
    except Exception as e:
        print(f"     ✗ /api/xero/reports/invoice-volume - {e}")
    
    print(f"✅ Xero module routes registered (9 endpoints + 20 reports)")


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
            parse_xero_date(inv['DueDate']) and parse_xero_date(inv['DueDate']) < datetime.now()
        )
        overdue_count = len([
            inv for inv in invoices 
            if inv.get('Status') == 'AUTHORISED' and inv.get('DueDate') and 
            parse_xero_date(inv['DueDate']) and parse_xero_date(inv['DueDate']) < datetime.now()
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
                parse_xero_date(inv['Date']) and parse_xero_date(inv['Date']).date() == date
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
        from_date = request.args.get('from_date')  # YYYY-MM-DD format
        to_date = request.args.get('to_date')      # YYYY-MM-DD format
        
        client = XeroAPIClient(business_id)
        
        # Build where clause
        where_clauses = []
        if status:
            where_clauses.append(f'Status=="{status}"')
        if contact_name:
            where_clauses.append(f'Contact.Name.Contains("{contact_name}")')
        if invoice_number:
            where_clauses.append(f'InvoiceNumber=="{invoice_number}"')
        if from_date:
            # Convert YYYY-MM-DD to DateTime(YYYY, MM, DD) format for Xero API
            year, month, day = from_date.split('-')
            where_clauses.append(f'Date>=DateTime({year},{month},{day})')
        if to_date:
            # Convert YYYY-MM-DD to DateTime(YYYY, MM, DD) format for Xero API
            year, month, day = to_date.split('-')
            where_clauses.append(f'Date<=DateTime({year},{month},{day})')
        
        params = {}
        if where_clauses:
            params['where'] = ' AND '.join(where_clauses)
        
        data = client.make_request('GET', 'Invoices', params=params)
        invoices = data.get('Invoices', [])
        
        # Format response
        formatted_invoices = []
        for inv in invoices:
            # Parse Xero dates to ISO format
            date_obj = parse_xero_date(inv.get('Date'))
            due_date_obj = parse_xero_date(inv.get('DueDate'))
            
            formatted_invoices.append({
                'invoice_id': inv.get('InvoiceID'),
                'invoice_number': inv.get('InvoiceNumber'),
                'contact_name': inv.get('Contact', {}).get('Name'),
                'date': date_obj.strftime('%Y-%m-%d') if date_obj else None,
                'due_date': due_date_obj.strftime('%Y-%m-%d') if due_date_obj else None,
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
        from_date = request.args.get('from_date')
        
        client = XeroAPIClient(business_id)
        
        # Build where clause for filtering
        where_clauses = []
        if search:
            where_clauses.append(f'Name.Contains("{search}")')
        if from_date:
            from_dt = format_xero_datetime(from_date)
            where_clauses.append(f'UpdatedDateUTC>={from_dt}')
        
        params = {}
        if where_clauses:
            params['where'] = ' AND '.join(where_clauses)
        
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
        from_date = request.args.get('from_date')
        
        client = XeroAPIClient(business_id)
        
        # Build where clause for filtering
        where_clauses = []
        if invoice_id:
            where_clauses.append(f'Invoice.InvoiceID==Guid("{invoice_id}")')
        if from_date:
            from_dt = format_xero_datetime(from_date)
            where_clauses.append(f'Date>={from_dt}')
        
        params = {}
        if where_clauses:
            params['where'] = ' AND '.join(where_clauses)
        
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
            from_dt = format_xero_datetime(from_date)
            where_clauses.append(f'Date>={from_dt}')
        if to_date:
            to_dt = format_xero_datetime(to_date)
            where_clauses.append(f'Date<={to_dt}')
        
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


# ============================================================================
# REPORTS ENDPOINTS
# ============================================================================

@cross_origin()
def xero_report_contact_activity():
    """
    Contact Activity Report - Join contacts with invoices to show transaction history
    
    Query Parameters:
    - business_id: Business ID (1=Print, 2=Publishing, 3=Signs)
    - from_date: Start date (YYYY-MM-DD) - defaults to 12 months ago
    - to_date: End date (YYYY-MM-DD) - defaults to today
    
    Returns:
    - List of contacts with invoice count, revenue, paid, outstanding
    """
    try:
        business_id = int(request.args.get('business_id', 1))
        from_date = request.args.get('from_date')
        to_date = request.args.get('to_date')
        
        # Default to last 12 months if no date range specified
        if not from_date:
            from_date = (datetime.now() - timedelta(days=365)).strftime('%Y-%m-%d')
        if not to_date:
            to_date = datetime.now().strftime('%Y-%m-%d')
        
        client = XeroAPIClient(business_id)
        
        # Fetch contacts
        contacts_data = client.make_request('GET', 'Contacts')
        contacts = contacts_data.get('Contacts', [])
        
        # Fetch invoices in date range
        from_dt = format_xero_datetime(from_date)
        to_dt = format_xero_datetime(to_date)
        params = {'where': f'Date>={from_dt} AND Date<={to_dt}'}
        invoices_data = client.make_request('GET', 'Invoices', params=params)
        invoices = invoices_data.get('Invoices', [])
        
        # Build activity map
        activity_map = {}
        
        for inv in invoices:
            contact_id = inv.get('Contact', {}).get('ContactID')
            contact_name = inv.get('Contact', {}).get('Name', 'Unknown')
            
            if contact_id not in activity_map:
                activity_map[contact_id] = {
                    'contact_id': contact_id,
                    'name': contact_name,
                    'invoice_count': 0,
                    'total_invoiced': 0,
                    'total_paid': 0,
                    'outstanding': 0,
                    'last_invoice_date': None,
                    'first_invoice_date': None
                }
            
            activity = activity_map[contact_id]
            activity['invoice_count'] += 1
            activity['total_invoiced'] += float(inv.get('Total', 0))
            activity['total_paid'] += float(inv.get('AmountPaid', 0))
            activity['outstanding'] += float(inv.get('AmountDue', 0))
            
            invoice_date = inv.get('Date')
            if invoice_date:
                if not activity['last_invoice_date'] or invoice_date > activity['last_invoice_date']:
                    activity['last_invoice_date'] = invoice_date
                if not activity['first_invoice_date'] or invoice_date < activity['first_invoice_date']:
                    activity['first_invoice_date'] = invoice_date
        
        # Convert to list and sort by revenue
        activities = sorted(
            activity_map.values(),
            key=lambda x: x['total_invoiced'],
            reverse=True
        )
        
        return jsonify({
            'success': True,
            'business': BUSINESS_CONFIGS[business_id]['name'],
            'date_range': {'from': from_date, 'to': to_date},
            'contact_count': len(activities),
            'total_contacts': len(contacts),
            'activities': activities
        })
    
    except Exception as e:
        print(f"Error in xero_report_contact_activity: {e}")
        traceback.print_exc()
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@cross_origin()
def xero_report_aged_receivables():
    """
    Aged Receivables Report - Unpaid invoices grouped by age
    
    Query Parameters:
    - business_id: Business ID (1=Print, 2=Publishing, 3=Signs)
    
    Returns:
    - Buckets: Current, 1-30 days, 31-60 days, 61-90 days, 90+ days
    - Each bucket has count, total amount, and list of invoices
    """
    try:
        business_id = int(request.args.get('business_id', 1))
        
        client = XeroAPIClient(business_id)
        
        # Fetch unpaid invoices
        params = {'where': 'Status!="PAID" AND Status!="VOIDED"'}
        data = client.make_request('GET', 'Invoices', params=params)
        invoices = data.get('Invoices', [])
        
        # Age buckets
        buckets = {
            'current': {'label': 'Current (not due)', 'count': 0, 'amount': 0, 'invoices': []},
            '1-30': {'label': '1-30 days', 'count': 0, 'amount': 0, 'invoices': []},
            '31-60': {'label': '31-60 days', 'count': 0, 'amount': 0, 'invoices': []},
            '61-90': {'label': '61-90 days', 'count': 0, 'amount': 0, 'invoices': []},
            '90+': {'label': '90+ days', 'count': 0, 'amount': 0, 'invoices': []}
        }
        
        today = datetime.now().date()
        
        for inv in invoices:
            due_date_str = inv.get('DueDate')
            if not due_date_str:
                continue
            
            try:
                due_date = parse_xero_date(due_date_str)
                if due_date:
                    due_date = due_date.date()
                    days_overdue = (today - due_date).days
                    amount_due = float(inv.get('AmountDue', 0))
                    
                    if days_overdue <= 0:
                        bucket_key = 'current'
                    elif days_overdue <= 30:
                        bucket_key = '1-30'
                    elif days_overdue <= 60:
                        bucket_key = '31-60'
                    elif days_overdue <= 90:
                        bucket_key = '61-90'
                    else:
                        bucket_key = '90+'
                    
                    bucket = buckets[bucket_key]
                    bucket['count'] += 1
                    bucket['amount'] += amount_due
                    bucket['invoices'].append({
                        'invoice_number': inv.get('InvoiceNumber'),
                        'contact_name': inv.get('Contact', {}).get('Name'),
                        'amount': amount_due,
                        'days_overdue': days_overdue,
                        'due_date': due_date_str
                    })
            except Exception as e:
                print(f"Warning: Failed to process invoice date: {e}")
                continue
        
        # Calculate totals
        total_outstanding = sum(b['amount'] for b in buckets.values())
        total_count = sum(b['count'] for b in buckets.values())
        
        return jsonify({
            'success': True,
            'business': BUSINESS_CONFIGS[business_id]['name'],
            'total_outstanding': total_outstanding,
            'total_count': total_count,
            'buckets': buckets
        })
    
    except Exception as e:
        print(f"Error in xero_report_aged_receivables: {e}")
        traceback.print_exc()
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@cross_origin()
def xero_report_sales_summary():
    """
    Sales Summary Report - Revenue by customer
    
    Query Parameters:
    - business_id: Business ID (1=Print, 2=Publishing, 3=Signs)
    - from_date: Start date (YYYY-MM-DD) - defaults to 90 days ago
    - to_date: End date (YYYY-MM-DD) - defaults to today
    
    Returns:
    - Customer sales grouped by contact
    - Total revenue, paid, outstanding for each customer
    """
    try:
        business_id = int(request.args.get('business_id', 1))
        from_date = request.args.get('from_date')
        to_date = request.args.get('to_date')
        
        # Default to last 90 days if no date range specified
        if not from_date:
            from_date = (datetime.now() - timedelta(days=90)).strftime('%Y-%m-%d')
        if not to_date:
            to_date = datetime.now().strftime('%Y-%m-%d')
        
        client = XeroAPIClient(business_id)
        
        # Fetch invoices in date range
        from_dt = format_xero_datetime(from_date)
        to_dt = format_xero_datetime(to_date)
        params = {'where': f'Date>={from_dt} AND Date<={to_dt}'}
        data = client.make_request('GET', 'Invoices', params=params)
        invoices = data.get('Invoices', [])
        
        # Group by customer
        customer_sales = {}
        
        for inv in invoices:
            contact_name = inv.get('Contact', {}).get('Name', 'Unknown')
            
            if contact_name not in customer_sales:
                customer_sales[contact_name] = {
                    'contact_name': contact_name,
                    'invoice_count': 0,
                    'total_invoiced': 0,
                    'total_paid': 0,
                    'outstanding': 0
                }
            
            sales = customer_sales[contact_name]
            sales['invoice_count'] += 1
            sales['total_invoiced'] += float(inv.get('Total', 0))
            sales['total_paid'] += float(inv.get('AmountPaid', 0))
            sales['outstanding'] += float(inv.get('AmountDue', 0))
        
        # Convert to list and sort by revenue
        sorted_sales = sorted(
            customer_sales.values(),
            key=lambda x: x['total_invoiced'],
            reverse=True
        )
        
        # Calculate totals
        total_revenue = sum(s['total_invoiced'] for s in sorted_sales)
        total_paid = sum(s['total_paid'] for s in sorted_sales)
        total_outstanding = sum(s['outstanding'] for s in sorted_sales)
        
        return jsonify({
            'success': True,
            'business': BUSINESS_CONFIGS[business_id]['name'],
            'date_range': {'from': from_date, 'to': to_date},
            'customer_count': len(sorted_sales),
            'total_revenue': total_revenue,
            'total_paid': total_paid,
            'total_outstanding': total_outstanding,
            'sales': sorted_sales
        })
    
    except Exception as e:
        print(f"Error in xero_report_sales_summary: {e}")
        traceback.print_exc()
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@cross_origin()
def xero_report_overdue_invoices():
    """Overdue Invoice List - Invoices past due date"""
    try:
        business_id = int(request.args.get('business_id', 1))
        from_date_str = request.args.get('from_date')
        client = XeroAPIClient(business_id)
        
        # Fetch unpaid invoices
        params = {'where': 'Status!="PAID" AND Status!="VOIDED"'}
        
        # Apply date range filter if provided
        if from_date_str:
            from_date = datetime.strptime(from_date_str, '%Y-%m-%d').date()
            params['where'] += f' AND Date>=DateTime({from_date.year},{from_date.month},{from_date.day})'
        
        data = client.make_request('GET', 'Invoices', params=params)
        invoices = data.get('Invoices', [])
        
        today = datetime.now().date()
        overdue_list = []
        
        for inv in invoices:
            due_date_str = inv.get('DueDate')
            if not due_date_str:
                continue
            
            try:
                due_date = parse_xero_date(due_date_str)
                if due_date:
                    due_date = due_date.date()
                    days_overdue = (today - due_date).days
                    
                    if days_overdue > 0:  # Only overdue invoices
                        overdue_list.append({
                            'invoice_number': inv.get('InvoiceNumber'),
                            'contact_name': inv.get('Contact', {}).get('Name'),
                            'amount_due': float(inv.get('AmountDue', 0)),
                            'due_date': due_date_str,
                            'days_overdue': days_overdue,
                            'invoice_date': inv.get('Date'),
                            'total': float(inv.get('Total', 0))
                        })
            except:
                continue
        
        # Sort by days overdue (most urgent first)
        overdue_list.sort(key=lambda x: x['days_overdue'], reverse=True)
        
        total_overdue = sum(inv['amount_due'] for inv in overdue_list)
        
        return jsonify({
            'success': True,
            'business': BUSINESS_CONFIGS[business_id]['name'],
            'overdue_count': len(overdue_list),
            'total_overdue': total_overdue,
            'invoices': overdue_list
        })
    
    except Exception as e:
        print(f"Error in xero_report_overdue_invoices: {e}")
        traceback.print_exc()
        return jsonify({'success': False, 'error': str(e)}), 500


@cross_origin()
def xero_report_revenue_trends():
    """Revenue Trends - Monthly revenue over time"""
    try:
        business_id = int(request.args.get('business_id', 1))
        months_back = int(request.args.get('months', 12))
        
        client = XeroAPIClient(business_id)
        
        # Fetch invoices
        from_date = (datetime.now() - timedelta(days=months_back*30)).strftime('%Y-%m-%d')
        from_dt = format_xero_datetime(from_date)
        params = {'where': f'Date>={from_dt} AND Status="PAID"'}
        data = client.make_request('GET', 'Invoices', params=params)
        invoices = data.get('Invoices', [])
        
        # Group by month with invoice count
        monthly_data = {}
        
        for inv in invoices:
            inv_date_str = inv.get('Date')
            if inv_date_str:
                try:
                    inv_date = parse_xero_date(inv_date_str)
                    if inv_date:
                        month_key = inv_date.strftime('%Y-%m')
                        if month_key not in monthly_data:
                            monthly_data[month_key] = {'revenue': 0, 'count': 0}
                        monthly_data[month_key]['revenue'] += float(inv.get('Total', 0))
                        monthly_data[month_key]['count'] += 1
                except:
                    continue
        
        # Convert to sorted list
        trends = [
            {
                'month': k, 
                'revenue': v['revenue'],
                'invoice_count': v['count']
            } 
            for k, v in sorted(monthly_data.items())
        ]
        
        return jsonify({
            'success': True,
            'business': BUSINESS_CONFIGS[business_id]['name'],
            'trends': trends
        })
    
    except Exception as e:
        print(f"Error in xero_report_revenue_trends: {e}")
        traceback.print_exc()
        return jsonify({'success': False, 'error': str(e)}), 500


@cross_origin()
def xero_report_invoice_status():
    """Invoice Status Summary - Distribution by status"""
    try:
        business_id = int(request.args.get('business_id', 1))
        from_date = request.args.get('from_date')
        
        client = XeroAPIClient(business_id)
        
        params = {}
        if from_date:
            from_dt = format_xero_datetime(from_date)
            params['where'] = f'Date>={from_dt}'
        
        data = client.make_request('GET', 'Invoices', params=params)
        invoices = data.get('Invoices', [])
        
        # Group by status
        status_summary = {}
        for inv in invoices:
            status = inv.get('Status', 'UNKNOWN')
            if status not in status_summary:
                status_summary[status] = {'count': 0, 'total': 0}
            status_summary[status]['count'] += 1
            status_summary[status]['total'] += float(inv.get('Total', 0))
        
        return jsonify({
            'success': True,
            'business': BUSINESS_CONFIGS[business_id]['name'],
            'total_invoices': len(invoices),
            'status_summary': status_summary
        })
    
    except Exception as e:
        print(f"Error in xero_report_invoice_status: {e}")
        traceback.print_exc()
        return jsonify({'success': False, 'error': str(e)}), 500


@cross_origin()
def xero_report_inactive_customers():
    """Inactive Customers - No recent invoices"""
    try:
        business_id = int(request.args.get('business_id', 1))
        days_inactive = int(request.args.get('days', 90))
        
        client = XeroAPIClient(business_id)
        
        # Fetch all contacts and invoices
        contacts_data = client.make_request('GET', 'Contacts')
        contacts = contacts_data.get('Contacts', [])
        
        invoices_data = client.make_request('GET', 'Invoices')
        invoices = invoices_data.get('Invoices', [])
        
        # Build customer activity map
        contact_activity = {}
        for inv in invoices:
            contact_id = inv.get('Contact', {}).get('ContactID')
            inv_date_str = inv.get('Date')
            if contact_id and inv_date_str:
                try:
                    inv_date = parse_xero_date(inv_date_str)
                    if inv_date:
                        if contact_id not in contact_activity:
                            contact_activity[contact_id] = {
                                'last_invoice_date': inv_date,
                                'first_invoice_date': inv_date,
                                'invoice_count': 0,
                                'total_revenue': 0,
                                'avg_order_value': 0
                            }
                        
                        # Update activity metrics
                        if inv_date > contact_activity[contact_id]['last_invoice_date']:
                            contact_activity[contact_id]['last_invoice_date'] = inv_date
                        if inv_date < contact_activity[contact_id]['first_invoice_date']:
                            contact_activity[contact_id]['first_invoice_date'] = inv_date
                        
                        contact_activity[contact_id]['invoice_count'] += 1
                        if inv.get('Status') == 'PAID':
                            contact_activity[contact_id]['total_revenue'] += float(inv.get('Total', 0))
                except:
                    continue
        
        # Calculate average order value and frequency
        for contact_id, activity in contact_activity.items():
            if activity['invoice_count'] > 0:
                activity['avg_order_value'] = activity['total_revenue'] / activity['invoice_count']
                
                # Calculate order frequency (days between orders)
                tenure_days = (activity['last_invoice_date'] - activity['first_invoice_date']).days
                if activity['invoice_count'] > 1:
                    activity['avg_days_between_orders'] = tenure_days / (activity['invoice_count'] - 1)
                else:
                    activity['avg_days_between_orders'] = tenure_days
        
        # Find inactive customers
        cutoff_date = datetime.now() - timedelta(days=days_inactive)
        inactive_list = []
        
        for contact in contacts:
            if not contact.get('IsCustomer'):
                continue
            
            contact_id = contact.get('ContactID')
            activity = contact_activity.get(contact_id)
            last_invoice_date = activity['last_invoice_date'] if activity else None
            
            if not last_invoice_date or last_invoice_date < cutoff_date:
                days_since_last = (datetime.now() - last_invoice_date).days if last_invoice_date else None
                inactive_list.append({
                    'name': contact.get('Name'),
                    'email': contact.get('EmailAddress'),
                    'last_invoice_date': last_invoice_date.strftime('%Y-%m-%d') if last_invoice_date else 'Never',
                    'days_since_last': days_since_last,
                    'total_orders': activity['invoice_count'] if activity else 0,
                    'total_revenue': round(activity['total_revenue'], 2) if activity else 0,
                    'avg_order_value': round(activity['avg_order_value'], 2) if activity else 0,
                    'avg_days_between_orders': round(activity['avg_days_between_orders'], 1) if activity else 0
                })
        
        return jsonify({
            'success': True,
            'business': BUSINESS_CONFIGS[business_id]['name'],
            'inactive_count': len(inactive_list),
            'days_threshold': days_inactive,
            'customers': inactive_list
        })
    
    except Exception as e:
        print(f"Error in xero_report_inactive_customers: {e}")
        traceback.print_exc()
        return jsonify({'success': False, 'error': str(e)}), 500


@cross_origin()
def xero_report_cash_flow():
    """Cash Flow Timeline - Money received by date"""
    try:
        business_id = int(request.args.get('business_id', 1))
        days_back = int(request.args.get('days', 90))
        
        client = XeroAPIClient(business_id)
        
        # Fetch payments
        from_date = (datetime.now() - timedelta(days=days_back)).strftime('%Y-%m-%d')
        from_dt = format_xero_datetime(from_date)
        params = {'where': f'Date>={from_dt}'}
        data = client.make_request('GET', 'Payments', params=params)
        payments = data.get('Payments', [])
        
        # Group by date
        daily_cash_flow = {}
        
        for payment in payments:
            payment_date_str = payment.get('Date')
            if payment_date_str:
                try:
                    payment_date = parse_xero_date(payment_date_str)
                    if payment_date:
                        date_key = payment_date.strftime('%Y-%m-%d')
                        daily_cash_flow[date_key] = daily_cash_flow.get(date_key, 0) + float(payment.get('Amount', 0))
                except:
                    continue
        
        # Convert to sorted list
        cash_flow = [{'date': k, 'amount': v} for k, v in sorted(daily_cash_flow.items())]
        
        total_received = sum(p['amount'] for p in cash_flow)
        
        return jsonify({
            'success': True,
            'business': BUSINESS_CONFIGS[business_id]['name'],
            'total_received': total_received,
            'days_covered': days_back,
            'cash_flow': cash_flow
        })
    
    except Exception as e:
        print(f"Error in xero_report_cash_flow: {e}")
        traceback.print_exc()
        return jsonify({'success': False, 'error': str(e)}), 500


@cross_origin()
def xero_report_business_comparison():
    """Business Comparison - Compare all 3 businesses"""
    try:
        from_date = request.args.get('from_date')
        to_date = request.args.get('to_date')
        
        # Default to last 90 days
        if not from_date:
            from_date = (datetime.now() - timedelta(days=90)).strftime('%Y-%m-%d')
        if not to_date:
            to_date = datetime.now().strftime('%Y-%m-%d')
        
        comparison = []
        
        for business_id in [1, 2, 3]:
            client = XeroAPIClient(business_id)
            
            # Fetch invoices for this business
            from_dt = format_xero_datetime(from_date)
            to_dt = format_xero_datetime(to_date)
            params = {'where': f'Date>={from_dt} AND Date<={to_dt}'}
            data = client.make_request('GET', 'Invoices', params=params)
            invoices = data.get('Invoices', [])
            
            total_revenue = sum(float(inv.get('Total', 0)) for inv in invoices if inv.get('Status') == 'PAID')
            total_outstanding = sum(float(inv.get('AmountDue', 0)) for inv in invoices if inv.get('Status') not in ['PAID', 'VOIDED'])
            invoice_count = len(invoices)
            
            comparison.append({
                'business_id': business_id,
                'business_name': BUSINESS_CONFIGS[business_id]['name'],
                'revenue': total_revenue,
                'outstanding': total_outstanding,
                'invoice_count': invoice_count,
                'avg_invoice_value': total_revenue / invoice_count if invoice_count > 0 else 0
            })
        
        # Calculate totals
        total_revenue = sum(b['revenue'] for b in comparison)
        total_outstanding = sum(b['outstanding'] for b in comparison)
        
        return jsonify({
            'success': True,
            'date_range': {'from': from_date, 'to': to_date},
            'total_revenue': total_revenue,
            'total_outstanding': total_outstanding,
            'businesses': comparison
        })
    
    except Exception as e:
        print(f"Error in xero_report_business_comparison: {e}")
        traceback.print_exc()
        return jsonify({'success': False, 'error': str(e)}), 500


@cross_origin()
def xero_report_customer_lifetime_value():
    """Customer Lifetime Value - Total revenue + tenure per customer"""
    try:
        business_id = int(request.args.get('business_id', 1))
        client = XeroAPIClient(business_id)
        
        # Fetch all invoices
        data = client.make_request('GET', 'Invoices')
        invoices = data.get('Invoices', [])
        
        # Group by customer
        customer_ltv = {}
        for inv in invoices:
            contact = inv.get('Contact', {})
            contact_id = contact.get('ContactID')
            contact_name = contact.get('Name', 'Unknown')
            
            if contact_id not in customer_ltv:
                customer_ltv[contact_id] = {
                    'contact_id': contact_id,
                    'contact_name': contact_name,
                    'total_revenue': 0,
                    'invoice_count': 0,
                    'first_invoice_date': None,
                    'last_invoice_date': None
                }
            
            # Add revenue (only paid invoices)
            if inv.get('Status') == 'PAID':
                customer_ltv[contact_id]['total_revenue'] += float(inv.get('Total', 0))
            
            customer_ltv[contact_id]['invoice_count'] += 1
            
            # Track dates
            inv_date_str = inv.get('Date')
            if inv_date_str:
                inv_date = parse_xero_date(inv_date_str)
                if inv_date:
                    if not customer_ltv[contact_id]['first_invoice_date'] or inv_date < customer_ltv[contact_id]['first_invoice_date']:
                        customer_ltv[contact_id]['first_invoice_date'] = inv_date
                    if not customer_ltv[contact_id]['last_invoice_date'] or inv_date > customer_ltv[contact_id]['last_invoice_date']:
                        customer_ltv[contact_id]['last_invoice_date'] = inv_date
        
        # Calculate tenure and average frequency
        for customer in customer_ltv.values():
            if customer['first_invoice_date'] and customer['last_invoice_date']:
                tenure_days = (customer['last_invoice_date'] - customer['first_invoice_date']).days
                customer['tenure_days'] = tenure_days
                customer['avg_days_between_invoices'] = tenure_days / customer['invoice_count'] if customer['invoice_count'] > 1 else 0
                # Format dates for JSON serialization
                customer['first_invoice_date'] = customer['first_invoice_date'].strftime('%Y-%m-%d')
                customer['last_invoice_date'] = customer['last_invoice_date'].strftime('%Y-%m-%d')
            else:
                customer['tenure_days'] = 0
                customer['avg_days_between_invoices'] = 0
        
        # Sort by total revenue
        sorted_customers = sorted(customer_ltv.values(), key=lambda x: x['total_revenue'], reverse=True)
        
        return jsonify({
            'success': True,
            'business': BUSINESS_CONFIGS[business_id]['name'],
            'customer_count': len(sorted_customers),
            'customers': sorted_customers
        })
    
    except Exception as e:
        print(f"Error in xero_report_customer_lifetime_value: {e}")
        traceback.print_exc()
        return jsonify({'success': False, 'error': str(e)}), 500


@cross_origin()
def xero_report_payment_behavior():
    """Payment Behavior Analysis - Average days to pay, early/late percentages"""
    try:
        business_id = int(request.args.get('business_id', 1))
        client = XeroAPIClient(business_id)
        
        # Fetch invoices and payments
        invoices_data = client.make_request('GET', 'Invoices')
        invoices = invoices_data.get('Invoices', [])
        
        payments_data = client.make_request('GET', 'Payments')
        payments = payments_data.get('Payments', [])
        
        # Map payments to invoices
        payment_map = {}
        for payment in payments:
            inv = payment.get('Invoice', {})
            inv_id = inv.get('InvoiceID')
            if inv_id:
                if inv_id not in payment_map:
                    payment_map[inv_id] = []
                payment_map[inv_id].append(payment)
        
        # Calculate payment behavior metrics
        payment_analysis = []
        total_days_to_pay = 0
        early_count = 0
        on_time_count = 0
        late_count = 0
        analyzed_count = 0
        
        for inv in invoices:
            inv_id = inv.get('InvoiceID')
            if inv_id not in payment_map or inv.get('Status') != 'PAID':
                continue
            
            inv_date = inv.get('Date')
            due_date = inv.get('DueDate')
            
            if not inv_date or not due_date:
                continue
            
            # Find first payment date
            payments_for_inv = payment_map[inv_id]
            payment_dates = [p.get('Date') for p in payments_for_inv if p.get('Date')]
            if not payment_dates:
                continue
            
            first_payment_date = min(payment_dates)
            
            # Parse dates
            inv_dt = datetime.fromisoformat(inv_date.replace('Z', '+00:00'))
            due_dt = datetime.fromisoformat(due_date.replace('Z', '+00:00'))
            pay_dt = datetime.fromisoformat(first_payment_date.replace('Z', '+00:00'))
            
            days_to_pay = (pay_dt - inv_dt).days
            days_vs_due = (pay_dt - due_dt).days
            
            total_days_to_pay += days_to_pay
            analyzed_count += 1
            
            if days_vs_due < 0:
                early_count += 1
                status = 'Early'
            elif days_vs_due == 0:
                on_time_count += 1
                status = 'On Time'
            else:
                late_count += 1
                status = 'Late'
            
            payment_analysis.append({
                'invoice_number': inv.get('InvoiceNumber'),
                'contact_name': inv.get('Contact', {}).get('Name', 'Unknown'),
                'invoice_date': inv_date,
                'due_date': due_date,
                'payment_date': first_payment_date,
                'days_to_pay': days_to_pay,
                'days_vs_due': days_vs_due,
                'status': status,
                'amount': float(inv.get('Total', 0))
            })
        
        avg_days_to_pay = total_days_to_pay / analyzed_count if analyzed_count > 0 else 0
        
        return jsonify({
            'success': True,
            'business': BUSINESS_CONFIGS[business_id]['name'],
            'avg_days_to_pay': round(avg_days_to_pay, 1),
            'early_percentage': round((early_count / analyzed_count * 100) if analyzed_count > 0 else 0, 1),
            'on_time_percentage': round((on_time_count / analyzed_count * 100) if analyzed_count > 0 else 0, 1),
            'late_percentage': round((late_count / analyzed_count * 100) if analyzed_count > 0 else 0, 1),
            'early_count': early_count,
            'on_time_count': on_time_count,
            'late_count': late_count,
            'analyzed_count': analyzed_count,
            'payment_details': sorted(payment_analysis, key=lambda x: x['days_to_pay'], reverse=True)
        })
    
    except Exception as e:
        print(f"Error in xero_report_payment_behavior: {e}")
        traceback.print_exc()
        return jsonify({'success': False, 'error': str(e)}), 500


@cross_origin()
def xero_report_payment_reconciliation():
    """Payment Reconciliation - Unmatched payments, partial payments"""
    try:
        business_id = int(request.args.get('business_id', 1))
        client = XeroAPIClient(business_id)
        
        # Fetch invoices and payments
        invoices_data = client.make_request('GET', 'Invoices')
        invoices = invoices_data.get('Invoices', [])
        
        payments_data = client.make_request('GET', 'Payments')
        payments = payments_data.get('Payments', [])
        
        # Build invoice lookup
        invoice_map = {inv['InvoiceID']: inv for inv in invoices}
        
        # Analyze payments
        unmatched_payments = []
        partial_payments = []
        overpayments = []
        matched_count = 0
        
        for payment in payments:
            inv = payment.get('Invoice', {})
            inv_id = inv.get('InvoiceID')
            payment_amount = float(payment.get('Amount', 0))
            
            if not inv_id or inv_id not in invoice_map:
                # Payment not linked to any invoice
                unmatched_payments.append({
                    'payment_id': payment.get('PaymentID'),
                    'date': payment.get('Date'),
                    'amount': payment_amount,
                    'reference': payment.get('Reference', 'N/A')
                })
                continue
            
            invoice = invoice_map[inv_id]
            invoice_total = float(invoice.get('Total', 0))
            
            if payment_amount < invoice_total:
                partial_payments.append({
                    'payment_id': payment.get('PaymentID'),
                    'invoice_number': invoice.get('InvoiceNumber'),
                    'invoice_total': invoice_total,
                    'payment_amount': payment_amount,
                    'remaining': invoice_total - payment_amount,
                    'date': payment.get('Date')
                })
            elif payment_amount > invoice_total:
                overpayments.append({
                    'payment_id': payment.get('PaymentID'),
                    'invoice_number': invoice.get('InvoiceNumber'),
                    'invoice_total': invoice_total,
                    'payment_amount': payment_amount,
                    'excess': payment_amount - invoice_total,
                    'date': payment.get('Date')
                })
            else:
                matched_count += 1
        
        return jsonify({
            'success': True,
            'business': BUSINESS_CONFIGS[business_id]['name'],
            'summary': {
                'matched_count': matched_count,
                'unmatched_count': len(unmatched_payments),
                'partial_count': len(partial_payments),
                'overpayment_count': len(overpayments)
            },
            'unmatched_payments': unmatched_payments,
            'partial_payments': partial_payments,
            'overpayments': overpayments
        })
    
    except Exception as e:
        print(f"Error in xero_report_payment_reconciliation: {e}")
        traceback.print_exc()
        return jsonify({'success': False, 'error': str(e)}), 500


@cross_origin()
def xero_report_dso():
    """Days Sales Outstanding (DSO) - Average collection period"""
    try:
        business_id = int(request.args.get('business_id', 1))
        period_days = int(request.args.get('period_days', 90))
        client = XeroAPIClient(business_id)
        
        # Calculate date range
        to_date = datetime.now()
        from_date = to_date - timedelta(days=period_days)
        
        # Fetch invoices
        params = {
            'where': f'Date>=DateTime({from_date.strftime("%Y-%m-%d")}) AND Date<=DateTime({to_date.strftime("%Y-%m-%d")})'
        }
        data = client.make_request('GET', 'Invoices', params=params)
        invoices = data.get('Invoices', [])
        
        # Calculate accounts receivable (unpaid invoices)
        accounts_receivable = sum(float(inv.get('AmountDue', 0)) for inv in invoices if inv.get('Status') not in ['PAID', 'VOIDED'])
        
        # Calculate total credit sales (paid invoices)
        credit_sales = sum(float(inv.get('Total', 0)) for inv in invoices if inv.get('Status') == 'PAID')
        
        # DSO = (Accounts Receivable / Total Credit Sales) * Number of Days
        if credit_sales > 0:
            dso = (accounts_receivable / credit_sales) * period_days
        else:
            dso = 0
        
        # Industry benchmark (typical is 30-45 days)
        benchmark = 45
        performance = 'Good' if dso <= benchmark else 'Needs Improvement'
        
        return jsonify({
            'success': True,
            'business': BUSINESS_CONFIGS[business_id]['name'],
            'period_days': period_days,
            'dso': round(dso, 1),
            'accounts_receivable': accounts_receivable,
            'credit_sales': credit_sales,
            'benchmark': benchmark,
            'performance': performance,
            'interpretation': f"On average, it takes {round(dso, 1)} days to collect payment after a sale."
        })
    
    except Exception as e:
        print(f"Error in xero_report_dso: {e}")
        traceback.print_exc()
        return jsonify({'success': False, 'error': str(e)}), 500


@cross_origin()
def xero_report_revenue_by_product():
    """Revenue by Product/Service - Parse line items"""
    try:
        business_id = int(request.args.get('business_id', 1))
        from_date = request.args.get('from_date')
        to_date = request.args.get('to_date')
        client = XeroAPIClient(business_id)
        
        # Default to last 90 days
        if not from_date:
            from_date = (datetime.now() - timedelta(days=90)).strftime('%Y-%m-%d')
        if not to_date:
            to_date = datetime.now().strftime('%Y-%m-%d')
        
        # Fetch invoices
        from_dt = format_xero_datetime(from_date)
        to_dt = format_xero_datetime(to_date)
        params = {'where': f'Date>={from_dt} AND Date<={to_dt}'}
        data = client.make_request('GET', 'Invoices', params=params)
        invoices = data.get('Invoices', [])
        
        # Parse line items
        product_revenue = {}
        
        for inv in invoices:
            if inv.get('Status') != 'PAID':
                continue
            
            line_items = inv.get('LineItems', [])
            for item in line_items:
                description = item.get('Description', 'Unknown')
                quantity = float(item.get('Quantity', 0))
                unit_price = float(item.get('UnitAmount', 0))
                line_total = float(item.get('LineAmount', 0))
                
                if description not in product_revenue:
                    product_revenue[description] = {
                        'product': description,
                        'quantity_sold': 0,
                        'revenue': 0,
                        'invoice_count': 0
                    }
                
                product_revenue[description]['quantity_sold'] += quantity
                product_revenue[description]['revenue'] += line_total
                product_revenue[description]['invoice_count'] += 1
        
        # Sort by revenue
        sorted_products = sorted(product_revenue.values(), key=lambda x: x['revenue'], reverse=True)
        
        # Calculate totals
        total_revenue = sum(p['revenue'] for p in sorted_products)
        
        return jsonify({
            'success': True,
            'business': BUSINESS_CONFIGS[business_id]['name'],
            'date_range': {'from': from_date, 'to': to_date},
            'product_count': len(sorted_products),
            'total_revenue': total_revenue,
            'products': sorted_products
        })
    
    except Exception as e:
        print(f"Error in xero_report_revenue_by_product: {e}")
        traceback.print_exc()
        return jsonify({'success': False, 'error': str(e)}), 500


@cross_origin()
def xero_report_seasonality():
    """Seasonality Analysis - Monthly revenue patterns, YoY comparison"""
    try:
        business_id = int(request.args.get('business_id', 1))
        years = int(request.args.get('years', 2))
        client = XeroAPIClient(business_id)
        
        # Fetch invoices for specified years
        from_date = (datetime.now() - timedelta(days=365 * years)).strftime('%Y-%m-%d')
        from_dt = format_xero_datetime(from_date)
        params = {'where': f'Date>={from_dt}'}
        data = client.make_request('GET', 'Invoices', params=params)
        invoices = data.get('Invoices', [])
        
        # Group by year and month
        monthly_data = {}
        
        for inv in invoices:
            if inv.get('Status') != 'PAID':
                continue
            
            inv_date_str = inv.get('Date')
            if not inv_date_str:
                continue
            
            dt = parse_xero_date(inv_date_str)
            if not dt:
                continue
            
            year = dt.year
            month = dt.month
            month_name = dt.strftime('%B')
            
            key = f"{year}-{month:02d}"
            
            if key not in monthly_data:
                monthly_data[key] = {
                    'year': year,
                    'month': month,
                    'month_name': month_name,
                    'revenue': 0,
                    'invoice_count': 0
                }
            
            monthly_data[key]['revenue'] += float(inv.get('Total', 0))
            monthly_data[key]['invoice_count'] += 1
        
        # Sort chronologically
        sorted_months = sorted(monthly_data.values(), key=lambda x: (x['year'], x['month']))
        
        # Calculate month-over-month averages for seasonality pattern
        month_averages = {}
        for month_num in range(1, 13):
            month_revenues = [m['revenue'] for m in sorted_months if m['month'] == month_num]
            if month_revenues:
                month_averages[month_num] = {
                    'month': month_num,
                    'month_name': datetime(2000, month_num, 1).strftime('%B'),
                    'avg_revenue': sum(month_revenues) / len(month_revenues),
                    'occurrences': len(month_revenues)
                }
        
        sorted_avg = sorted(month_averages.values(), key=lambda x: x['month'])
        
        return jsonify({
            'success': True,
            'business': BUSINESS_CONFIGS[business_id]['name'],
            'years_analyzed': years,
            'monthly_breakdown': sorted_months,
            'seasonal_pattern': sorted_avg
        })
    
    except Exception as e:
        print(f"Error in xero_report_seasonality: {e}")
        traceback.print_exc()
        return jsonify({'success': False, 'error': str(e)}), 500


@cross_origin()
def xero_report_forecast():
    """Forecast & Projections - Trend-based revenue prediction"""
    try:
        business_id = int(request.args.get('business_id', 1))
        historical_months = int(request.args.get('historical_months', 12))
        forecast_months = int(request.args.get('forecast_months', 3))
        client = XeroAPIClient(business_id)
        
        # Fetch historical invoices
        from_date = (datetime.now() - timedelta(days=30 * historical_months)).strftime('%Y-%m-%d')
        from_dt = format_xero_datetime(from_date)
        params = {'where': f'Date>={from_dt}'}
        data = client.make_request('GET', 'Invoices', params=params)
        invoices = data.get('Invoices', [])
        
        # Group by month
        monthly_revenue = {}
        
        for inv in invoices:
            if inv.get('Status') != 'PAID':
                continue
            
            inv_date_str = inv.get('Date')
            if not inv_date_str:
                continue
            
            dt = parse_xero_date(inv_date_str)
            if not dt:
                continue
            
            month_key = dt.strftime('%Y-%m')
            
            if month_key not in monthly_revenue:
                monthly_revenue[month_key] = 0
            
            monthly_revenue[month_key] += float(inv.get('Total', 0))
        
        # Sort chronologically
        sorted_months = sorted(monthly_revenue.items())
        
        # Simple linear trend calculation
        if len(sorted_months) < 2:
            return jsonify({
                'success': False,
                'error': 'Not enough historical data for forecasting (need at least 2 months)'
            }), 400
        
        # Calculate average monthly growth
        revenues = [r[1] for r in sorted_months]
        avg_revenue = sum(revenues) / len(revenues)
        
        # Simple moving average for trend
        growth_rates = []
        for i in range(1, len(revenues)):
            if revenues[i-1] > 0:
                growth_rates.append((revenues[i] - revenues[i-1]) / revenues[i-1])
        
        avg_growth_rate = sum(growth_rates) / len(growth_rates) if growth_rates else 0
        
        # Generate forecast
        last_month_revenue = revenues[-1]
        forecasted_months = []
        
        for i in range(1, forecast_months + 1):
            forecast_date = datetime.now() + timedelta(days=30 * i)
            forecasted_revenue = last_month_revenue * (1 + avg_growth_rate) ** i
            
            forecasted_months.append({
                'month': forecast_date.strftime('%Y-%m'),
                'forecasted_revenue': round(forecasted_revenue, 2),
                'confidence': 'Medium' if i <= 3 else 'Low'
            })
        
        return jsonify({
            'success': True,
            'business': BUSINESS_CONFIGS[business_id]['name'],
            'historical_months': historical_months,
            'avg_monthly_revenue': round(avg_revenue, 2),
            'avg_growth_rate': round(avg_growth_rate * 100, 2),
            'historical_data': [{'month': m, 'revenue': r} for m, r in sorted_months],
            'forecast': forecasted_months
        })
    
    except Exception as e:
        print(f"Error in xero_report_forecast: {e}")
        traceback.print_exc()
        return jsonify({'success': False, 'error': str(e)}), 500


@cross_origin()
def xero_report_customer_segmentation():
    """Customer Segmentation (RFM) - Recency, Frequency, Monetary analysis"""
    try:
        business_id = int(request.args.get('business_id', 1))
        client = XeroAPIClient(business_id)
        
        # Fetch all invoices
        data = client.make_request('GET', 'Invoices')
        invoices = data.get('Invoices', [])
        
        # Calculate RFM for each customer
        customer_rfm = {}
        current_date = datetime.now()
        
        for inv in invoices:
            contact = inv.get('Contact', {})
            contact_id = contact.get('ContactID')
            contact_name = contact.get('Name', 'Unknown')
            
            if contact_id not in customer_rfm:
                customer_rfm[contact_id] = {
                    'contact_id': contact_id,
                    'contact_name': contact_name,
                    'last_invoice_date': None,
                    'invoice_count': 0,
                    'total_monetary_value': 0
                }
            
            inv_date_str = inv.get('Date')
            if inv_date_str:
                dt = parse_xero_date(inv_date_str)
                if dt and (not customer_rfm[contact_id]['last_invoice_date'] or dt > customer_rfm[contact_id]['last_invoice_date']):
                    customer_rfm[contact_id]['last_invoice_date'] = dt
            
            customer_rfm[contact_id]['invoice_count'] += 1
            
            if inv.get('Status') == 'PAID':
                customer_rfm[contact_id]['total_monetary_value'] += float(inv.get('Total', 0))
        
        # Calculate recency (days since last invoice)
        for customer in customer_rfm.values():
            if customer['last_invoice_date']:
                customer['recency_days'] = (current_date - customer['last_invoice_date']).days
            else:
                customer['recency_days'] = 9999
        
        # Assign RFM scores (1-5, 5 being best)
        customers_list = list(customer_rfm.values())
        
        # Sort by recency (lower is better)
        sorted_by_recency = sorted(customers_list, key=lambda x: x['recency_days'])
        for i, customer in enumerate(sorted_by_recency):
            customer['recency_score'] = 5 - int(i / len(sorted_by_recency) * 5)
        
        # Sort by frequency (higher is better)
        sorted_by_frequency = sorted(customers_list, key=lambda x: x['invoice_count'], reverse=True)
        for i, customer in enumerate(sorted_by_frequency):
            customer['frequency_score'] = 5 - int(i / len(sorted_by_frequency) * 5)
        
        # Sort by monetary (higher is better)
        sorted_by_monetary = sorted(customers_list, key=lambda x: x['total_monetary_value'], reverse=True)
        for i, customer in enumerate(sorted_by_monetary):
            customer['monetary_score'] = 5 - int(i / len(sorted_by_monetary) * 5)
        
        # Calculate total RFM score and segment
        for customer in customers_list:
            rfm_score = customer['recency_score'] + customer['frequency_score'] + customer['monetary_score']
            customer['rfm_score'] = rfm_score
            
            # Segment customers
            if rfm_score >= 13:
                customer['segment'] = 'Champions'
            elif rfm_score >= 10:
                customer['segment'] = 'Loyal Customers'
            elif rfm_score >= 7:
                customer['segment'] = 'Potential Loyalists'
            elif rfm_score >= 5:
                customer['segment'] = 'At Risk'
            else:
                customer['segment'] = 'Lost'
        
        # Sort by RFM score
        sorted_customers = sorted(customers_list, key=lambda x: x['rfm_score'], reverse=True)
        
        # Count segments
        segment_counts = {}
        for customer in sorted_customers:
            segment = customer['segment']
            if segment not in segment_counts:
                segment_counts[segment] = 0
            segment_counts[segment] += 1
        
        return jsonify({
            'success': True,
            'business': BUSINESS_CONFIGS[business_id]['name'],
            'customer_count': len(sorted_customers),
            'segment_distribution': segment_counts,
            'customers': sorted_customers
        })
    
    except Exception as e:
        print(f"Error in xero_report_customer_segmentation: {e}")
        traceback.print_exc()
        return jsonify({'success': False, 'error': str(e)}), 500


@cross_origin()
def xero_report_customer_overlap():
    """Customer Overlap Analysis - Customers using multiple businesses"""
    try:
        # Fetch contacts from all 3 businesses
        all_contacts = {}
        
        for business_id in [1, 2, 3]:
            client = XeroAPIClient(business_id)
            data = client.make_request('GET', 'Contacts')
            contacts = data.get('Contacts', [])
            
            for contact in contacts:
                name = contact.get('Name', '').strip().lower()
                email = contact.get('EmailAddress', '').strip().lower()
                
                # Use email as primary key, fallback to name
                key = email if email else name
                
                if not key:
                    continue
                
                if key not in all_contacts:
                    all_contacts[key] = {
                        'name': contact.get('Name', 'Unknown'),
                        'email': email,
                        'businesses': []
                    }
                
                all_contacts[key]['businesses'].append({
                    'business_id': business_id,
                    'business_name': BUSINESS_CONFIGS[business_id]['name'],
                    'contact_id': contact.get('ContactID')
                })
        
        # Find overlaps (customers in multiple businesses)
        overlapping_customers = [c for c in all_contacts.values() if len(c['businesses']) > 1]
        
        # Sort by number of businesses
        overlapping_customers.sort(key=lambda x: len(x['businesses']), reverse=True)
        
        return jsonify({
            'success': True,
            'total_unique_customers': len(all_contacts),
            'overlapping_customer_count': len(overlapping_customers),
            'overlap_percentage': round((len(overlapping_customers) / len(all_contacts) * 100) if all_contacts else 0, 1),
            'overlapping_customers': overlapping_customers
        })
    
    except Exception as e:
        print(f"Error in xero_report_customer_overlap: {e}")
        traceback.print_exc()
        return jsonify({'success': False, 'error': str(e)}), 500


@cross_origin()
def xero_report_consolidated_revenue():
    """Consolidated Revenue - Total across all 3 businesses with breakdown"""
    try:
        from_date = request.args.get('from_date')
        to_date = request.args.get('to_date')
        
        # Default to last 90 days
        if not from_date:
            from_date = (datetime.now() - timedelta(days=90)).strftime('%Y-%m-%d')
        if not to_date:
            to_date = datetime.now().strftime('%Y-%m-%d')
        
        consolidated = {
            'total_revenue': 0,
            'total_outstanding': 0,
            'total_invoice_count': 0,
            'businesses': []
        }
        
        # Fetch from each business
        from_dt = format_xero_datetime(from_date)
        to_dt = format_xero_datetime(to_date)
        for business_id in [1, 2, 3]:
            client = XeroAPIClient(business_id)
            params = {'where': f'Date>={from_dt} AND Date<={to_dt}'}
            data = client.make_request('GET', 'Invoices', params=params)
            invoices = data.get('Invoices', [])
            
            revenue = sum(float(inv.get('Total', 0)) for inv in invoices if inv.get('Status') == 'PAID')
            outstanding = sum(float(inv.get('AmountDue', 0)) for inv in invoices if inv.get('Status') not in ['PAID', 'VOIDED'])
            
            consolidated['businesses'].append({
                'business_id': business_id,
                'business_name': BUSINESS_CONFIGS[business_id]['name'],
                'revenue': revenue,
                'outstanding': outstanding,
                'invoice_count': len(invoices),
                'percentage_of_total': 0  # Will calculate after totals
            })
            
            consolidated['total_revenue'] += revenue
            consolidated['total_outstanding'] += outstanding
            consolidated['total_invoice_count'] += len(invoices)
        
        # Calculate percentages
        for business in consolidated['businesses']:
            if consolidated['total_revenue'] > 0:
                business['percentage_of_total'] = round((business['revenue'] / consolidated['total_revenue']) * 100, 1)
        
        return jsonify({
            'success': True,
            'date_range': {'from': from_date, 'to': to_date},
            'consolidated': consolidated
        })
    
    except Exception as e:
        print(f"Error in xero_report_consolidated_revenue: {e}")
        traceback.print_exc()
        return jsonify({'success': False, 'error': str(e)}), 500


@cross_origin()
def xero_report_invoice_volume():
    """Invoice Volume Analysis - Invoices per period, peak billing times"""
    try:
        business_id = int(request.args.get('business_id', 1))
        from_date = request.args.get('from_date')
        to_date = request.args.get('to_date')
        client = XeroAPIClient(business_id)
        
        # Default to last 12 months
        if not from_date:
            from_date = (datetime.now() - timedelta(days=365)).strftime('%Y-%m-%d')
        if not to_date:
            to_date = datetime.now().strftime('%Y-%m-%d')
        
        # Fetch invoices
        from_dt = format_xero_datetime(from_date)
        to_dt = format_xero_datetime(to_date)
        params = {'where': f'Date>={from_dt} AND Date<={to_dt}'}
        data = client.make_request('GET', 'Invoices', params=params)
        invoices = data.get('Invoices', [])
        
        # Group by month
        monthly_volume = {}
        day_of_month_counts = {}
        
        for inv in invoices:
            inv_date = inv.get('Date')
            if not inv_date:
                continue
            
            dt = datetime.fromisoformat(inv_date.replace('Z', '+00:00'))
            month_key = dt.strftime('%Y-%m')
            day_of_month = dt.day
            
            # Monthly volume
            if month_key not in monthly_volume:
                monthly_volume[month_key] = {
                    'month': month_key,
                    'invoice_count': 0,
                    'total_value': 0
                }
            
            monthly_volume[month_key]['invoice_count'] += 1
            monthly_volume[month_key]['total_value'] += float(inv.get('Total', 0))
            
            # Day of month frequency
            if day_of_month not in day_of_month_counts:
                day_of_month_counts[day_of_month] = 0
            day_of_month_counts[day_of_month] += 1
        
        # Sort monthly volume
        sorted_months = sorted(monthly_volume.values(), key=lambda x: x['month'])
        
        # Find peak billing days
        peak_days = sorted(day_of_month_counts.items(), key=lambda x: x[1], reverse=True)[:5]
        
        # Calculate averages
        total_invoices = len(invoices)
        months_count = len(monthly_volume)
        avg_invoices_per_month = total_invoices / months_count if months_count > 0 else 0
        avg_invoice_value = sum(float(inv.get('Total', 0)) for inv in invoices) / total_invoices if total_invoices > 0 else 0
        
        return jsonify({
            'success': True,
            'business': BUSINESS_CONFIGS[business_id]['name'],
            'date_range': {'from': from_date, 'to': to_date},
            'total_invoices': total_invoices,
            'avg_invoices_per_month': round(avg_invoices_per_month, 1),
            'avg_invoice_value': round(avg_invoice_value, 2),
            'monthly_breakdown': sorted_months,
            'peak_billing_days': [{'day': day, 'invoice_count': count} for day, count in peak_days]
        })
    
    except Exception as e:
        print(f"Error in xero_report_invoice_volume: {e}")
        traceback.print_exc()
        return jsonify({'success': False, 'error': str(e)}), 500
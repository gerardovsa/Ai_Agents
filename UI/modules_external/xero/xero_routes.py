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
        # Handle .NET date format: /Date(1749686400000+0000)/ or /Date(-319593600000+0000)/
        if date_str.startswith('/Date('):
            # Extract timestamp in milliseconds (supports negative timestamps for pre-1970 dates)
            match = re.match(r'/Date\((-?\d+)([+-]\d{4})?\)/', date_str)
            if match:
                timestamp_ms = int(match.group(1))
                timestamp_sec = timestamp_ms / 1000
                
                # Windows doesn't support negative timestamps with fromtimestamp()
                # Use Unix epoch (1970-01-01) as reference and add/subtract seconds
                try:
                    return datetime.fromtimestamp(timestamp_sec)
                except (OSError, ValueError):
                    # Fallback for negative timestamps (pre-1970 dates)
                    epoch = datetime(1970, 1, 1)
                    return epoch + timedelta(seconds=timestamp_sec)
        
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
        app.add_url_rule('/api/xero/reports/customer-health', 'xero_report_customer_health', xero_report_customer_health, methods=['GET', 'OPTIONS'])
        print(f"     ✓ /api/xero/reports/customer-health")
    except Exception as e:
        print(f"     ✗ /api/xero/reports/customer-health - {e}")
    
    try:
        app.add_url_rule('/api/xero/reports/customer-intelligence', 'xero_report_customer_intelligence', xero_report_customer_intelligence, methods=['GET', 'OPTIONS'])
        print(f"     ✓ /api/xero/reports/customer-intelligence")
    except Exception as e:
        print(f"     ✗ /api/xero/reports/customer-intelligence - {e}")
    
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
    
    try:
        app.add_url_rule('/api/xero/customer-details', 'xero_get_customer_details', xero_get_customer_details, methods=['GET', 'OPTIONS'])
        print(f"     ✓ /api/xero/customer-details")
    except Exception as e:
        print(f"     ✗ /api/xero/customer-details - {e}")
    
    # Quotes endpoints
    try:
        app.add_url_rule('/api/xero/quotes', 'xero_quotes', xero_quotes, methods=['GET', 'POST', 'OPTIONS'])
        print(f"     ✓ /api/xero/quotes")
    except Exception as e:
        print(f"     ✗ /api/xero/quotes - {e}")
    
    try:
        app.add_url_rule('/api/xero/quotes/<quote_id>', 'xero_quote_detail', xero_quote_detail, methods=['GET', 'PUT', 'DELETE', 'OPTIONS'])
        print(f"     ✓ /api/xero/quotes/<id>")
    except Exception as e:
        print(f"     ✗ /api/xero/quotes/<id> - {e}")
    
    print(f"✅ Xero module routes registered (12 endpoints + 21 reports)")


# ============================================================================
# DASHBOARD ENDPOINTS
# ============================================================================

def _check_credentials(client, business_id):
    """
    Check if Xero credentials are configured for the client.
    Returns tuple of (error_response, status_code) if credentials missing, or (None, None) if OK.
    """
    if not client.client_id or not client.client_secret:
        return jsonify({
            'error': 'Xero credentials not configured',
            'message': 'Please configure Xero API credentials in Account Settings → Integrations',
            'business_id': business_id,
            'setup_required': True
        }), 401
    return None, None

@cross_origin()
def xero_dashboard():
    """Get dashboard metrics and data"""
    try:
        business_id = int(request.args.get('business_id', 1))
        client = XeroAPIClient(business_id)
        
        # Check if credentials are available
        error_response, status_code = _check_credentials(client, business_id)
        if error_response:
            return error_response, status_code
        
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
# QUOTES ENDPOINTS
# ============================================================================

@cross_origin()
def xero_quotes():
    """Get or create quotes"""
    if request.method == 'POST':
        return create_quote()
    else:
        return get_quotes()


def get_quotes():
    """Get quotes from Xero"""
    try:
        business_id = int(request.args.get('business_id', 1))
        status = request.args.get('status')
        contact_id = request.args.get('contact_id')
        date_from = request.args.get('date_from')  # YYYY-MM-DD format
        date_to = request.args.get('date_to')      # YYYY-MM-DD format
        
        # Import xero_list_quotes tool
        sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent / 'tools' / 'implementations'))
        from xero_quotes import xero_list_quotes
        
        # Use existing xero_list_quotes tool
        result = xero_list_quotes(
            business_id=business_id,
            status=status,
            contact_id=contact_id,
            date_from=date_from,
            date_to=date_to,
            page=1,
            page_size=1000
        )
        
        if not result.get('success'):
            return jsonify(result), 500
        
        return jsonify({
            'success': True,
            'business': BUSINESS_CONFIGS[business_id]['name'],
            'quote_count': result.get('total_count', 0),
            'quotes': result.get('quotes', [])
        })
    
    except Exception as e:
        print(f"Error in get_quotes: {e}")
        traceback.print_exc()
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


def create_quote():
    """Create new quote in Xero"""
    try:
        data = request.json
        business_id = int(data.get('business_id', 1))
        
        # Import xero_create_quote tool
        sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent / 'tools' / 'implementations'))
        from xero_quotes import xero_create_quote
        
        # Use existing xero_create_quote tool
        result = xero_create_quote(
            business_id=business_id,
            contact_id=data.get('contact_id'),
            line_items=data.get('line_items', []),
            title=data.get('title', 'Printing Quote'),
            date=data.get('date'),
            expiry_date=data.get('expiry_date'),
            terms=data.get('terms'),
            status=data.get('status', 'DRAFT'),
            branding_theme_id=data.get('branding_theme_id')
        )
        
        if not result.get('success'):
            return jsonify(result), 500
        
        return jsonify({
            'success': True,
            'business': BUSINESS_CONFIGS[business_id]['name'],
            'quote': result.get('quote')
        })
    
    except Exception as e:
        print(f"Error in create_quote: {e}")
        traceback.print_exc()
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@cross_origin()
def xero_quote_detail(quote_id):
    """Get specific quote by ID"""
    try:
        business_id = int(request.args.get('business_id', 1))
        
        # Import xero_get_quote_by_id tool
        sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent / 'tools' / 'implementations'))
        from xero_quotes import xero_get_quote_by_id
        
        result = xero_get_quote_by_id(
            business_id=business_id,
            quote_id=quote_id
        )
        
        if not result.get('success'):
            return jsonify(result), 404 if 'not found' in result.get('error', '').lower() else 500
        
        return jsonify({
            'success': True,
            'business': BUSINESS_CONFIGS[business_id]['name'],
            'quote': result.get('quote')
        })
    
    except Exception as e:
        print(f"Error in xero_quote_detail: {e}")
        traceback.print_exc()
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@cross_origin()
def xero_convert_quote_to_invoice():
    """Convert accepted quote to invoice"""
    try:
        data = request.json
        business_id = int(data.get('business_id', 1))
        quote_id = data.get('quote_id')
        
        # Import tools
        sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent / 'tools' / 'implementations'))
        from xero_quotes import xero_get_quote_by_id, xero_update_quote
        
        # Get quote details
        quote_result = xero_get_quote_by_id(business_id=business_id, quote_id=quote_id)
        if not quote_result.get('success'):
            return jsonify(quote_result), 404
        
        quote = quote_result.get('quote')
        
        # Create invoice from quote data
        client = XeroAPIClient(business_id)
        
        invoice_data = {
            'Type': 'ACCREC',
            'Contact': {'ContactID': quote.get('contact_id')},
            'Date': datetime.now().strftime('%Y-%m-%d'),
            'DueDate': (datetime.now() + timedelta(days=30)).strftime('%Y-%m-%d'),
            'LineItems': quote.get('line_items', []),
            'Status': 'AUTHORISED',
            'Reference': f"Quote: {quote.get('quote_number')}"
        }
        
        invoice_response = client.make_request('PUT', 'Invoices', json_data={'Invoices': [invoice_data]})
        created_invoice = invoice_response.get('Invoices', [{}])[0]
        
        # Update quote status to INVOICED
        xero_update_quote(
            business_id=business_id,
            quote_id=quote_id,
            status='INVOICED'
        )
        
        return jsonify({
            'success': True,
            'invoice_id': created_invoice.get('InvoiceID'),
            'invoice_number': created_invoice.get('InvoiceNumber'),
            'quote_id': quote_id
        })
    
    except Exception as e:
        print(f"Error in xero_convert_quote_to_invoice: {e}")
        traceback.print_exc()
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@cross_origin()
def xero_convert_quote_to_production():
    """Convert accepted quote to FRED production order"""
    try:
        data = request.json
        business_id = int(data.get('business_id', 1))
        quote_id = data.get('quote_id')
        
        # Import tools
        sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent / 'tools' / 'implementations'))
        from xero_quotes import xero_get_quote_by_id
        
        # Get quote details
        quote_result = xero_get_quote_by_id(business_id=business_id, quote_id=quote_id)
        if not quote_result.get('success'):
            return jsonify(quote_result), 404
        
        quote = quote_result.get('quote')
        
        # Import FRED database tools
        sys.path.insert(0, str(Path(__file__).parent.parent.parent / 'AI_infrastructure' / 'shared'))
        from database_utils import execute_query
        
        # Get Xero contact ID to find FRED customer
        contact_id = quote.get('contact_id')
        
        # Find customer in FRED by Xero contact ID (stored in CustomerMYOB_ID)
        customer_query = """
            SELECT TOP 1 ContactID, Name
            FROM Clients
            WHERE CustomerMYOB_ID = ?
        """
        customers = execute_query(customer_query, (contact_id,), fetch_mode='all')
        
        if not customers:
            return jsonify({
                'success': False,
                'error': 'Customer not found in FRED database. Please link Xero contact to FRED customer first.'
            }), 404
        
        fred_customer = customers[0]
        
        # Create order in FRED
        order_query = """
            INSERT INTO Orders (
                CustomerMYOB_ID, ClientName, OrderDate, DateRequired, 
                InvoicingBusinessID, Status, Notes
            )
            OUTPUT INSERTED.OrderID
            VALUES (?, ?, GETDATE(), DATEADD(day, 7, GETDATE()), ?, 'New', ?)
        """
        
        order_result = execute_query(
            order_query,
            (
                contact_id,
                fred_customer['Name'],
                business_id,
                f"Created from Xero Quote: {quote.get('quote_number')}"
            ),
            fetch_mode='one'
        )
        
        order_id = order_result['OrderID'] if order_result else None
        
        if not order_id:
            raise Exception("Failed to create order in FRED")
        
        # Create job tickets from quote line items
        ticket_count = 0
        for idx, line_item in enumerate(quote.get('line_items', []), start=1):
            ticket_query = """
                INSERT INTO JobTickets (
                    OrderID, TicketNumber, Description, Quantity, 
                    UnitPrice, TotalPrice, Status
                )
                VALUES (?, ?, ?, ?, ?, ?, 'Pending')
            """
            
            execute_query(
                ticket_query,
                (
                    order_id,
                    idx,
                    line_item.get('description', 'Line Item'),
                    line_item.get('quantity', 1),
                    line_item.get('unit_amount', 0),
                    line_item.get('quantity', 1) * line_item.get('unit_amount', 0)
                )
            )
            ticket_count += 1
        
        return jsonify({
            'success': True,
            'order_id': order_id,
            'ticket_count': ticket_count,
            'customer_name': fred_customer['Name'],
            'quote_id': quote_id
        })
    
    except Exception as e:
        print(f"Error in xero_convert_quote_to_production: {e}")
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
    """Create new contact in Xero with comprehensive fields"""
    try:
        data = request.json
        business_id = int(data.get('business_id', 1))
        
        client = XeroAPIClient(business_id)
        
        # Build contact data structure
        contact_data = {
            'Name': data['name']
        }
        
        # Optional: First and Last Name (for person contacts)
        if data.get('first_name'):
            contact_data['FirstName'] = data['first_name']
        if data.get('last_name'):
            contact_data['LastName'] = data['last_name']
        
        # Email
        if data.get('email'):
            contact_data['EmailAddress'] = data['email']
        
        # Contact type flags
        if data.get('is_customer'):
            contact_data['IsCustomer'] = True
        if data.get('is_supplier'):
            contact_data['IsSupplier'] = True
        
        # Phone numbers (Xero supports DEFAULT, DDI, MOBILE, FAX)
        phones = []
        if data.get('phone'):
            phones.append({
                'PhoneType': 'DEFAULT',
                'PhoneNumber': data['phone']
            })
        if data.get('mobile'):
            phones.append({
                'PhoneType': 'MOBILE',
                'PhoneNumber': data['mobile']
            })
        if phones:
            contact_data['Phones'] = phones
        
        # Multiple Addresses (POBOX, STREET, DELIVERY)
        addresses_input = data.get('addresses', [])
        if addresses_input:
            xero_addresses = []
            for addr in addresses_input:
                if addr.get('line1'):  # Only add if has street address
                    xero_addresses.append({
                        'AddressType': addr.get('type', 'POBOX'),  # POBOX, STREET, or DELIVERY
                        'AddressLine1': addr.get('line1', ''),
                        'City': addr.get('city', ''),
                        'PostalCode': addr.get('postal_code', ''),
                        'Region': addr.get('region', ''),
                        'Country': addr.get('country', '')
                    })
            if xero_addresses:
                contact_data['Addresses'] = xero_addresses
        
        # Contact Persons (for business contacts)
        contact_persons_input = data.get('contact_persons', [])
        if contact_persons_input:
            xero_persons = []
            for person in contact_persons_input:
                if person.get('first_name') or person.get('last_name'):
                    person_data = {
                        'FirstName': person.get('first_name', ''),
                        'LastName': person.get('last_name', ''),
                        'EmailAddress': person.get('email', ''),
                        'IncludeInEmails': person.get('include_in_emails', True)
                    }
                    
                    # Add phone numbers for person
                    person_phones = []
                    if person.get('phone'):
                        person_phones.append({
                            'PhoneType': 'DDI',  # Direct Dial In
                            'PhoneNumber': person['phone']
                        })
                    if person.get('mobile'):
                        person_phones.append({
                            'PhoneType': 'MOBILE',
                            'PhoneNumber': person['mobile']
                        })
                    if person_phones:
                        person_data['Phones'] = person_phones
                    
                    xero_persons.append(person_data)
            
            if xero_persons:
                contact_data['ContactPersons'] = xero_persons
        
        # Tax number
        if data.get('tax_number'):
            contact_data['TaxNumber'] = data['tax_number']
        
        # Account number (custom reference)
        if data.get('account_number'):
            contact_data['AccountNumber'] = data['account_number']
        
        # Website
        if data.get('website'):
            contact_data['Website'] = data['website']
        
        # Create contact via Xero API
        payload = {'Contacts': [contact_data]}
        result = client.make_request('POST', 'Contacts', json=payload)
        
        contacts = result.get('Contacts', [])
        if not contacts:
            raise Exception("Failed to create contact")
        
        contact = contacts[0]
        
        # Format response
        return jsonify({
            'success': True,
            'business': BUSINESS_CONFIGS[business_id]['name'],
            'contact': {
                'contact_id': contact.get('ContactID'),
                'name': contact.get('Name'),
                'email': contact.get('EmailAddress'),
                'phone': contact.get('Phones', [{}])[0].get('PhoneNumber') if contact.get('Phones') else None,
                'is_customer': contact.get('IsCustomer'),
                'is_supplier': contact.get('IsSupplier'),
                'contact_persons_count': len(contact.get('ContactPersons', [])),
                'addresses_count': len(contact.get('Addresses', []))
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
    """Forecast & Projections - ARIMA-based revenue prediction with seasonality"""
    try:
        business_id = int(request.args.get('business_id', 1))
        historical_months = int(request.args.get('historical_months', 24))  # Increased for better ML accuracy
        forecast_months = int(request.args.get('forecast_months', 3))
        use_ml = request.args.get('use_ml', 'true').lower() == 'true'  # ML enabled by default
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
        
        # Need minimum data for forecasting
        if len(sorted_months) < 3:
            return jsonify({
                'success': False,
                'error': 'Not enough historical data for forecasting (need at least 3 months)'
            }), 400
        
        # Extract revenue values
        revenues = [r[1] for r in sorted_months]
        avg_revenue = sum(revenues) / len(revenues)
        
        # Try ML forecasting if enabled and enough data
        if use_ml and len(revenues) >= 6:
            try:
                from statsmodels.tsa.arima.model import ARIMA
                import numpy as np
                
                # Convert to numpy array
                revenue_series = np.array(revenues)
                
                # Determine ARIMA order based on data size
                if len(revenues) >= 12:
                    # With 12+ months, use seasonal ARIMA
                    order = (1, 1, 1)
                    seasonal_order = (1, 1, 1, 12) if len(revenues) >= 24 else None
                else:
                    # With 6-11 months, use simple ARIMA
                    order = (1, 1, 1)
                    seasonal_order = None
                
                # Fit ARIMA model
                if seasonal_order:
                    from statsmodels.tsa.statespace.sarimax import SARIMAX
                    model = SARIMAX(revenue_series, order=order, seasonal_order=seasonal_order)
                else:
                    model = ARIMA(revenue_series, order=order)
                
                fitted_model = model.fit(disp=False)
                
                # Generate forecast with confidence intervals
                forecast_result = fitted_model.get_forecast(steps=forecast_months)
                forecasted_values = forecast_result.predicted_mean
                confidence_intervals = forecast_result.conf_int()
                
                # Build forecast response
                forecasted_months = []
                for i in range(forecast_months):
                    forecast_date = datetime.now() + timedelta(days=30 * (i + 1))
                    forecasted_months.append({
                        'month': forecast_date.strftime('%Y-%m'),
                        'forecasted_revenue': round(float(forecasted_values[i]), 2),
                        'confidence_lower': round(float(confidence_intervals[i, 0]), 2),
                        'confidence_upper': round(float(confidence_intervals[i, 1]), 2),
                        'confidence': 'High' if i < 3 else 'Medium' if i < 6 else 'Low'
                    })
                
                return jsonify({
                    'success': True,
                    'method': 'ARIMA' if not seasonal_order else 'SARIMA',
                    'business': BUSINESS_CONFIGS[business_id]['name'],
                    'historical_months': len(revenues),
                    'avg_monthly_revenue': round(avg_revenue, 2),
                    'model_aic': round(float(fitted_model.aic), 2),
                    'historical_data': [{'month': m, 'revenue': r} for m, r in sorted_months],
                    'forecast': forecasted_months
                })
                
            except ImportError:
                print("Warning: statsmodels not installed, falling back to simple growth model")
                use_ml = False
            except Exception as e:
                print(f"Warning: ML forecasting failed ({e}), falling back to simple growth model")
                use_ml = False
        
        # Fallback: Simple growth model
        growth_rates = []
        for i in range(1, len(revenues)):
            if revenues[i-1] > 0:
                growth_rates.append((revenues[i] - revenues[i-1]) / revenues[i-1])
        
        avg_growth_rate = sum(growth_rates) / len(growth_rates) if growth_rates else 0
        
        # Generate simple forecast
        last_month_revenue = revenues[-1]
        forecasted_months = []
        
        for i in range(1, forecast_months + 1):
            forecast_date = datetime.now() + timedelta(days=30 * i)
            forecasted_revenue = last_month_revenue * (1 + avg_growth_rate) ** i
            
            # Estimate confidence intervals (±15% for simple model)
            margin = forecasted_revenue * 0.15
            
            forecasted_months.append({
                'month': forecast_date.strftime('%Y-%m'),
                'forecasted_revenue': round(forecasted_revenue, 2),
                'confidence_lower': round(forecasted_revenue - margin, 2),
                'confidence_upper': round(forecasted_revenue + margin, 2),
                'confidence': 'Medium' if i <= 3 else 'Low'
            })
        
        return jsonify({
            'success': True,
            'method': 'Simple Growth',
            'business': BUSINESS_CONFIGS[business_id]['name'],
            'historical_months': len(revenues),
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
def xero_report_customer_health():
    """Customer Health Metrics - Churn, Retention, Growth Analysis"""
    try:
        business_id = int(request.args.get('business_id', 1))
        client = XeroAPIClient(business_id)
        
        # Fetch all contacts and invoices
        contacts_data = client.make_request('GET', 'Contacts')
        contacts = contacts_data.get('Contacts', [])
        
        invoices_data = client.make_request('GET', 'Invoices')
        invoices = invoices_data.get('Invoices', [])
        
        # Calculate metrics
        current_date = datetime.now()
        thirty_days_ago = current_date - timedelta(days=30)
        sixty_days_ago = current_date - timedelta(days=60)
        ninety_days_ago = current_date - timedelta(days=90)
        
        # Track customer activity
        customer_activity = {}
        
        for inv in invoices:
            contact = inv.get('Contact', {})
            contact_id = contact.get('ContactID')
            
            if not contact_id:
                continue
            
            if contact_id not in customer_activity:
                customer_activity[contact_id] = {
                    'contact_name': contact.get('Name', 'Unknown'),
                    'first_invoice_date': None,
                    'last_invoice_date': None,
                    'invoice_count': 0,
                    'total_revenue': 0
                }
            
            inv_date_str = inv.get('Date')
            if inv_date_str:
                dt = parse_xero_date(inv_date_str)
                if dt:
                    if not customer_activity[contact_id]['first_invoice_date'] or dt < customer_activity[contact_id]['first_invoice_date']:
                        customer_activity[contact_id]['first_invoice_date'] = dt
                    if not customer_activity[contact_id]['last_invoice_date'] or dt > customer_activity[contact_id]['last_invoice_date']:
                        customer_activity[contact_id]['last_invoice_date'] = dt
            
            customer_activity[contact_id]['invoice_count'] += 1
            
            if inv.get('Status') == 'PAID':
                customer_activity[contact_id]['total_revenue'] += float(inv.get('Total', 0))
        
        # Calculate metrics
        total_customers = len(customer_activity)
        active_customers = 0
        new_customers = 0
        churned_customers = 0
        at_risk_customers = 0
        
        for customer in customer_activity.values():
            last_invoice = customer['last_invoice_date']
            first_invoice = customer['first_invoice_date']
            
            if last_invoice:
                days_since_last = (current_date - last_invoice).days
                
                # Active: invoiced in last 30 days
                if days_since_last <= 30:
                    active_customers += 1
                
                # Churned: no invoice in 90+ days
                elif days_since_last >= 90:
                    churned_customers += 1
                
                # At risk: 60-89 days since last invoice
                elif days_since_last >= 60:
                    at_risk_customers += 1
            
            # New customers: first invoice in last 30 days
            if first_invoice and (current_date - first_invoice).days <= 30:
                new_customers += 1
        
        # Calculate rates
        churn_rate = (churned_customers / total_customers) if total_customers > 0 else 0
        retention_rate = 1 - churn_rate
        net_growth = new_customers - churned_customers
        growth_rate = (net_growth / total_customers) if total_customers > 0 else 0
        
        return jsonify({
            'success': True,
            'business': BUSINESS_CONFIGS[business_id]['name'],
            'total_customers': total_customers,
            'active_customers': active_customers,
            'new_customers': new_customers,
            'churned_customers': churned_customers,
            'at_risk_count': at_risk_customers,
            'churn_rate': churn_rate,
            'retention_rate': retention_rate,
            'net_growth': net_growth,
            'growth_rate': growth_rate
        })
    
    except Exception as e:
        print(f"Error in xero_report_customer_health: {e}")
        traceback.print_exc()
        return jsonify({'success': False, 'error': str(e)}), 500


@cross_origin()
def xero_report_customer_intelligence():
    """
    Unified Customer Intelligence Dashboard
    
    Combines ALL customer insights into one comprehensive view:
    - Customer Health (time-based risk)
    - RFM Segmentation (multi-factor scoring)
    - ML Churn Prediction (pattern learning)
    - Customer Lifetime Value
    - Payment Behavior Analysis
    - Activity Tracking
    - Reorder Frequency Statistics (NEW: avg, variance, deviation analysis)
    
    Returns unified risk scores + actionable recommendations
    """
    try:
        business_id = int(request.args.get('business_id', 1))
        exclude_internal = request.args.get('exclude_internal', 'true').lower() == 'true'
        
        # Define internal entities to filter out
        INTERNAL_ENTITIES = [
            'in house print',
            'inhouse print',
            'in house publishing',
            'inhouse publishing',
            'in house signs',
            'inhouse signs',
            'in house',
            'inhouse'
        ]
        
        client = XeroAPIClient(business_id)
        
        # Fetch all invoices and contacts
        contacts_data = client.make_request('GET', 'Contacts')
        contacts = contacts_data.get('Contacts', [])
        
        invoices_data = client.make_request('GET', 'Invoices')
        invoices = invoices_data.get('Invoices', [])
        
        # Calculate comprehensive metrics per customer
        customer_intelligence = {}
        current_date = datetime.now()
        
        for inv in invoices:
            contact = inv.get('Contact', {})
            contact_id = contact.get('ContactID')
            contact_name = contact.get('Name', 'Unknown')
            
            if not contact_id:
                continue
            
            # Initialize customer record
            if contact_id not in customer_intelligence:
                customer_intelligence[contact_id] = {
                    'contact_id': contact_id,
                    'contact_name': contact_name,
                    'first_invoice_date': None,
                    'last_invoice_date': None,
                    'invoice_dates': [],  # NEW: Track all invoice dates for reorder frequency analysis
                    'total_invoices': 0,
                    'paid_invoices': 0,
                    'days_since_last_order': None,
                    'lifetime_revenue': 0,
                    'avg_invoice_value': 0,
                    'total_outstanding': 0,
                    'on_time_payments': 0,
                    'late_payments': 0,
                    'order_frequency': 0,
                    'payment_consistency': 100,
                    'time_risk_score': 0,
                    'payment_risk_score': 0,
                    'ml_churn_probability': 0,
                    'rfm_score': 0,
                    'rfm_segment': 'Unknown',
                    'unified_risk_score': 0,
                    'risk_category': 'Low',
                    'recommended_action': 'monitor',
                    'action_priority': 5,
                    'action_reason': '',
                    # NEW: Reorder frequency statistics
                    'avg_reorder_days': 0,
                    'reorder_variance': 0,
                    'expected_next_order': None,
                    'days_overdue': 0,
                    'deviation_severity': 'On Time'
                }
            
            record = customer_intelligence[contact_id]
            
            # Parse invoice date
            inv_date_str = inv.get('Date')
            if inv_date_str:
                dt = parse_xero_date(inv_date_str)
                if dt:
                    record['invoice_dates'].append(dt)  # NEW: Track all dates
                    if not record['first_invoice_date'] or dt < record['first_invoice_date']:
                        record['first_invoice_date'] = dt
                    if not record['last_invoice_date'] or dt > record['last_invoice_date']:
                        record['last_invoice_date'] = dt
            
            record['total_invoices'] += 1
            
            # Track payment status
            status = inv.get('Status')
            if status == 'PAID':
                record['paid_invoices'] += 1
                record['lifetime_revenue'] += float(inv.get('Total', 0))
                
                # Check if paid late
                due_date_str = inv.get('DueDate')
                paid_date_str = inv.get('FullyPaidOnDate')
                if due_date_str and paid_date_str:
                    due_dt = parse_xero_date(due_date_str)
                    paid_dt = parse_xero_date(paid_date_str)
                    if due_dt and paid_dt:
                        if paid_dt > due_dt:
                            record['late_payments'] += 1
                        else:
                            record['on_time_payments'] += 1
            
            elif status in ['AUTHORISED', 'SUBMITTED']:
                record['total_outstanding'] += float(inv.get('AmountDue', 0))
        
        # Calculate derived metrics and risk scores
        for contact_id, record in customer_intelligence.items():
            # Days since last order
            if record['last_invoice_date']:
                record['days_since_last_order'] = (current_date - record['last_invoice_date']).days
            else:
                record['days_since_last_order'] = 9999
            
            # Average invoice value
            if record['paid_invoices'] > 0:
                record['avg_invoice_value'] = record['lifetime_revenue'] / record['paid_invoices']
            
            # Order frequency (orders per month)
            if record['first_invoice_date']:
                days_active = (current_date - record['first_invoice_date']).days
                if days_active > 0:
                    months_active = days_active / 30
                    record['order_frequency'] = record['total_invoices'] / months_active if months_active > 0 else 0
            
            # NEW: Reorder Frequency Statistics
            invoice_dates = sorted(record['invoice_dates'])
            if len(invoice_dates) >= 2:
                # Calculate days between consecutive orders
                intervals = []
                for i in range(1, len(invoice_dates)):
                    days_between = (invoice_dates[i] - invoice_dates[i-1]).days
                    if days_between > 0:  # Ignore same-day invoices
                        intervals.append(days_between)
                
                if intervals:
                    # Average reorder frequency
                    record['avg_reorder_days'] = sum(intervals) / len(intervals)
                    
                    # Variance (standard deviation)
                    if len(intervals) > 1:
                        mean = record['avg_reorder_days']
                        variance = sum((x - mean) ** 2 for x in intervals) / len(intervals)
                        record['reorder_variance'] = variance ** 0.5  # Standard deviation
                    else:
                        record['reorder_variance'] = 0
                    
                    # Expected next order date
                    record['expected_next_order'] = record['last_invoice_date'] + timedelta(days=record['avg_reorder_days'])
                    
                    # Days overdue from expected reorder
                    if record['expected_next_order']:
                        record['days_overdue'] = (current_date - record['expected_next_order']).days
                        if record['days_overdue'] < 0:
                            record['days_overdue'] = 0  # Not overdue yet
                    
                    # Deviation severity
                    if record['days_overdue'] == 0:
                        record['deviation_severity'] = 'On Time'
                    elif record['days_overdue'] <= record['reorder_variance']:
                        record['deviation_severity'] = 'Slightly Late'
                    elif record['days_overdue'] <= (record['reorder_variance'] * 2):
                        record['deviation_severity'] = 'Very Late'
                    else:
                        record['deviation_severity'] = 'Critical'
            
            # Payment consistency
            total_paid = record['on_time_payments'] + record['late_payments']
            if total_paid > 0:
                record['payment_consistency'] = (record['on_time_payments'] / total_paid) * 100
            
            # INTELLIGENT TIME-BASED RISK - CUSTOMER-SPECIFIC PATTERNS (NO ARBITRARY THRESHOLDS)
            # Based on real data analysis: avg reorder = 18 days, 55% single-order, 28% high-frequency
            days_inactive = record['days_since_last_order']
            total_invoices = record['total_invoices']
            avg_reorder = record['avg_reorder_days']
            reorder_variance = record['reorder_variance']
            lifetime_value = record['lifetime_revenue']  # FIX (Jan 20, 2026): Use lifetime_revenue (actual field)
            
            # Determine if high-frequency customer (<60 day avg reorder interval)
            is_high_frequency = avg_reorder > 0 and avg_reorder < 60
            
            # Define value threshold for single-order classification ($1000 based on LTV median $571)
            high_value_threshold = 1000
            is_high_value_single = total_invoices == 1 and lifetime_value >= high_value_threshold
            is_low_value_single = total_invoices == 1 and lifetime_value < high_value_threshold
            
            # TRACK A: SINGLE-ORDER HIGH-VALUE CUSTOMERS
            if is_high_value_single:
                if days_inactive <= 30:
                    record['time_risk_score'] = 5
                    record['action_priority'] = 2
                    record['customer_status'] = 'High-Value New'
                    record['action_reason'] = f'High-value first order (${lifetime_value:,.2f}) - Early follow-up opportunity'
                elif days_inactive <= 90:
                    record['time_risk_score'] = 50
                    record['action_priority'] = 1
                    record['customer_status'] = 'High-Value At-Risk'
                    record['action_reason'] = f'High-value customer (${lifetime_value:,.2f}) - 30+ days since first order, URGENT follow-up'
                elif days_inactive <= 365:
                    record['time_risk_score'] = 75
                    record['action_priority'] = 3
                    record['customer_status'] = 'High-Value Dormant'
                    record['action_reason'] = f'High-value customer (${lifetime_value:,.2f}) - 90+ days inactive, reactivation campaign needed'
                else:  # 365+ days
                    record['time_risk_score'] = 0
                    record['action_priority'] = 10
                    record['customer_status'] = 'Dead Customer'
                    record['action_reason'] = f'High-value lost customer - 1+ year inactive, archive unless special circumstance'
            
            # TRACK B: SINGLE-ORDER LOW-VALUE CUSTOMERS
            elif is_low_value_single:
                if days_inactive <= 90:
                    record['time_risk_score'] = 10
                    record['action_priority'] = 6
                    record['customer_status'] = 'New Low-Value'
                    record['action_reason'] = f'Single low-value order (${lifetime_value:,.2f}) - Monitor for repeat business'
                elif days_inactive <= 365:
                    record['time_risk_score'] = 25
                    record['action_priority'] = 8
                    record['customer_status'] = 'Low-Value Dormant'
                    record['action_reason'] = f'Single order (${lifetime_value:,.2f}) - Low priority, consider bulk reactivation campaign'
                else:  # 365+ days
                    record['time_risk_score'] = 0
                    record['action_priority'] = 10
                    record['customer_status'] = 'Dead Customer'
                    record['action_reason'] = f'Lost customer - 1+ year inactive, archive'
            
            # TRACK C: MULTI-ORDER CUSTOMERS WITH ESTABLISHED PATTERN (4+ orders)
            elif total_invoices >= 4 and avg_reorder > 0:
                # Calculate statistical deviation from customer's own pattern
                days_overdue = record['days_overdue']
                deviation_ratio = days_overdue / (reorder_variance + 1)  # Standard deviations overdue
                
                # Dead customer threshold: 365 days (1 year)
                if days_inactive >= 365:
                    record['time_risk_score'] = 0
                    record['action_priority'] = 10
                    record['customer_status'] = 'Dead Customer'
                    record['action_reason'] = f'1+ year inactive - Archive (avg reorder was {avg_reorder:.0f}d, now {days_inactive}d)'
                
                # Critical deviation: 3+ standard deviations
                elif deviation_ratio >= 3:
                    if is_high_frequency:
                        record['time_risk_score'] = 95
                        record['action_priority'] = 1
                        record['customer_status'] = 'High-Frequency Churning'
                        record['action_reason'] = f'URGENT: High-frequency customer (avg {avg_reorder:.0f}d) is {deviation_ratio:.1f}σ overdue - {days_overdue}d past expected'
                    else:
                        record['time_risk_score'] = 90
                        record['action_priority'] = 2
                        record['customer_status'] = 'Churning'
                        record['action_reason'] = f'Critical: {deviation_ratio:.1f}σ overdue - Expected order {days_overdue}d ago (avg {avg_reorder:.0f}d)'
                
                # High deviation: 2-3 standard deviations
                elif deviation_ratio >= 2:
                    if is_high_frequency:
                        record['time_risk_score'] = 85
                        record['action_priority'] = 1
                        record['customer_status'] = 'High-Frequency At-Risk'
                        record['action_reason'] = f'URGENT: High-frequency customer (avg {avg_reorder:.0f}d) is {deviation_ratio:.1f}σ overdue - Act now'
                    else:
                        record['time_risk_score'] = 75
                        record['action_priority'] = 2
                        record['customer_status'] = 'High-Risk'
                        record['action_reason'] = f'Significant delay: {deviation_ratio:.1f}σ overdue - Expected {days_overdue}d ago (avg {avg_reorder:.0f}d)'
                
                # Moderate deviation: 1-2 standard deviations
                elif deviation_ratio >= 1:
                    if is_high_frequency:
                        record['time_risk_score'] = 60
                        record['action_priority'] = 2
                        record['customer_status'] = 'High-Frequency Monitor'
                        record['action_reason'] = f'High-frequency customer (avg {avg_reorder:.0f}d) is {deviation_ratio:.1f}σ overdue - Early intervention'
                    else:
                        record['time_risk_score'] = 50
                        record['action_priority'] = 4
                        record['customer_status'] = 'At-Risk'
                        record['action_reason'] = f'Outside normal pattern: {deviation_ratio:.1f}σ overdue - Check in recommended (avg {avg_reorder:.0f}d)'
                
                # Slightly overdue: 0-1 standard deviations
                elif days_overdue > 0:
                    if is_high_frequency:
                        record['time_risk_score'] = 30
                        record['action_priority'] = 3
                        record['customer_status'] = 'High-Frequency Normal'
                        record['action_reason'] = f'High-frequency customer (avg {avg_reorder:.0f}d) slightly delayed - Monitor closely'
                    else:
                        record['time_risk_score'] = 25
                        record['action_priority'] = 5
                        record['customer_status'] = 'Slightly Overdue'
                        record['action_reason'] = f'Within variance: {days_overdue}d past avg ({avg_reorder:.0f}d) - Normal variation'
                
                # On time or early
                else:
                    if is_high_frequency:
                        record['time_risk_score'] = 5
                        record['action_priority'] = 4
                        record['customer_status'] = 'High-Frequency Active'
                        record['action_reason'] = f'Excellent: High-frequency customer (avg {avg_reorder:.0f}d) ordering on schedule'
                    else:
                        record['time_risk_score'] = 5
                        record['action_priority'] = 6
                        record['customer_status'] = 'Active'
                        record['action_reason'] = f'On schedule: Within expected reorder window (avg {avg_reorder:.0f}d)'
            
            # TRACK D: MULTI-ORDER CUSTOMERS WITHOUT PATTERN YET (2-3 orders)
            elif total_invoices >= 2 and total_invoices <= 3:
                # Not enough data for statistical pattern - use simple checkpoints
                if days_inactive >= 365:
                    record['time_risk_score'] = 0
                    record['action_priority'] = 10
                    record['customer_status'] = 'Dead Customer'
                    record['action_reason'] = f'1+ year inactive - Archive (only {total_invoices} orders)'
                elif days_inactive >= 90:
                    record['time_risk_score'] = 60
                    record['action_priority'] = 3
                    record['customer_status'] = 'Early-Stage At-Risk'
                    record['action_reason'] = f'New customer ({total_invoices} orders) - 90+ days inactive, nurture needed'
                elif days_inactive >= 30:
                    record['time_risk_score'] = 30
                    record['action_priority'] = 5
                    record['customer_status'] = 'Early-Stage Active'
                    record['action_reason'] = f'New customer ({total_invoices} orders) - Building relationship, follow-up opportunity'
                else:
                    record['time_risk_score'] = 5
                    record['action_priority'] = 6
                    record['customer_status'] = 'New Active'
                    record['action_reason'] = f'New customer ({total_invoices} orders) - Recent activity, continue engagement'
            
            # TRACK E: EDGE CASE - No order data (should not happen)
            else:
                record['time_risk_score'] = 0
                record['action_priority'] = 10
                record['customer_status'] = 'No Data'
                record['action_reason'] = 'No order history available'
            
            # PAYMENT RISK (0-100)
            if record['payment_consistency'] < 50:
                record['payment_risk_score'] = 80
            elif record['payment_consistency'] < 70:
                record['payment_risk_score'] = 50
            elif record['payment_consistency'] < 90:
                record['payment_risk_score'] = 20
            else:
                record['payment_risk_score'] = 5
            
            # ML CHURN PROBABILITY (simplified - combine recency + frequency)
            recency_factor = min(days_inactive / 90, 1.0)
            frequency_factor = max(0, 1.0 - (record['order_frequency'] / 2))
            record['ml_churn_probability'] = int((recency_factor * 0.7 + frequency_factor * 0.3) * 100)
            
            # ML CONFIDENCE SCORE - How reliable is the prediction?
            data_quality_factors = []
            if record['total_invoices'] >= 5:
                data_quality_factors.append(1.0)  # Sufficient data
            elif record['total_invoices'] >= 3:
                data_quality_factors.append(0.7)  # Moderate data
            else:
                data_quality_factors.append(0.3)  # Limited data
            
            if record['reorder_variance'] > 0:
                consistency = 1 - min(record['reorder_variance'] / record['avg_reorder_days'], 1.0) if record['avg_reorder_days'] > 0 else 0
                data_quality_factors.append(consistency)
            
            record['ml_confidence'] = int(sum(data_quality_factors) / len(data_quality_factors) * 100) if data_quality_factors else 50
            
            # ML TREND ANALYSIS - Is customer behavior improving or declining?
            if len(invoice_dates) >= 3:
                # Compare first half vs second half of order history
                mid_point = len(invoice_dates) // 2
                days_diff = (invoice_dates[mid_point] - invoice_dates[0]).days
                
                recent_frequency = len(invoice_dates[mid_point:]) / ((current_date - invoice_dates[mid_point]).days / 30) if invoice_dates and (current_date - invoice_dates[mid_point]).days > 0 else 0
                historical_frequency = mid_point / (days_diff / 30) if len(invoice_dates) > mid_point and invoice_dates and days_diff > 0 else 0
                
                if recent_frequency > historical_frequency * 1.2 and historical_frequency > 0:
                    record['behavior_trend'] = 'improving'
                    record['trend_score'] = int((recent_frequency / historical_frequency - 1) * 100) if historical_frequency > 0 else 0
                elif recent_frequency < historical_frequency * 0.8:
                    record['behavior_trend'] = 'declining'
                    record['trend_score'] = int((1 - recent_frequency / historical_frequency) * 100) if historical_frequency > 0 else 0
                else:
                    record['behavior_trend'] = 'stable'
                    record['trend_score'] = 0
            else:
                record['behavior_trend'] = 'insufficient_data'
                record['trend_score'] = 0
            
            # PREDICTIVE FORECAST - Future risk at 30/60/90 days
            current_churn_rate = record['ml_churn_probability'] / 100
            trend_impact = record['trend_score'] / 100 * (-1 if record['behavior_trend'] == 'improving' else 1)
            
            record['predicted_risk_30d'] = int(min(100, (current_churn_rate + trend_impact * 0.3) * 100))
            record['predicted_risk_60d'] = int(min(100, (current_churn_rate + trend_impact * 0.6) * 100))
            record['predicted_risk_90d'] = int(min(100, (current_churn_rate + trend_impact * 0.9) * 100))
            
            # RFM SCORING (1-5 for each)
            if days_inactive <= 30:
                recency_score = 5
            elif days_inactive <= 60:
                recency_score = 4
            elif days_inactive <= 90:
                recency_score = 3
            elif days_inactive <= 180:
                recency_score = 2
            else:
                recency_score = 1
            
            if record['order_frequency'] >= 2:
                frequency_score = 5
            elif record['order_frequency'] >= 1:
                frequency_score = 4
            elif record['order_frequency'] >= 0.5:
                frequency_score = 3
            elif record['order_frequency'] >= 0.25:
                frequency_score = 2
            else:
                frequency_score = 1
            
            if record['lifetime_revenue'] >= 100000:
                monetary_score = 5
            elif record['lifetime_revenue'] >= 50000:
                monetary_score = 4
            elif record['lifetime_revenue'] >= 10000:
                monetary_score = 3
            elif record['lifetime_revenue'] >= 1000:
                monetary_score = 2
            else:
                monetary_score = 1
            
            record['rfm_score'] = recency_score + frequency_score + monetary_score
            
            # RFM Segment
            if record['rfm_score'] >= 13:
                record['rfm_segment'] = 'Champions'
            elif record['rfm_score'] >= 10:
                record['rfm_segment'] = 'Loyal Customers'
            elif record['rfm_score'] >= 7:
                record['rfm_segment'] = 'Potential Loyalists'
            elif record['rfm_score'] >= 5:
                record['rfm_segment'] = 'At Risk'
            else:
                record['rfm_segment'] = 'Lost'
            
            # UNIFIED RISK SCORE (weighted combination)
            record['unified_risk_score'] = int(
                record['time_risk_score'] * 0.40 +
                record['ml_churn_probability'] * 0.35 +
                record['payment_risk_score'] * 0.15 +
                (100 - record['rfm_score'] * 6.67) * 0.10
            )
            
            # Risk Category & Recommendations
            if record['unified_risk_score'] >= 70:
                record['risk_category'] = 'High'
                record['action_priority'] = 1
                record['recommended_action'] = 'call_now'
                record['action_reason'] = f"{days_inactive}d inactive, {record['late_payments']} late payments"
            elif record['unified_risk_score'] >= 40:
                record['risk_category'] = 'Medium'
                record['action_priority'] = 2
                record['recommended_action'] = 'email_campaign'
                record['action_reason'] = f"{days_inactive}d inactive, declining frequency"
            else:
                record['risk_category'] = 'Low'
                record['action_priority'] = 4
                record['recommended_action'] = 'monitor'
                record['action_reason'] = 'Healthy customer'
            
            # ML-ENHANCED SEGMENTATION - Combines multiple ML signals
            # Creates strategic segments beyond simple risk categories
            high_value = record['lifetime_revenue'] >= 50000
            high_churn = record['ml_churn_probability'] >= 70
            declining = record['behavior_trend'] == 'declining'
            improving = record['behavior_trend'] == 'improving'
            champion = record['rfm_segment'] == 'Champions'
            
            if champion and high_value and not high_churn:
                record['ml_segment'] = 'VIP - Protect'
                record['ml_segment_action'] = 'Dedicated account manager, exclusive offers'
            elif high_value and high_churn:
                record['ml_segment'] = 'VIP At-Risk'
                record['ml_segment_action'] = 'Urgent executive call, retention offer'
            elif high_value and declining:
                record['ml_segment'] = 'High-Value Declining'
                record['ml_segment_action'] = 'Win-back campaign, investigate issues'
            elif not high_value and improving:
                record['ml_segment'] = 'Rising Star'
                record['ml_segment_action'] = 'Nurture growth, upsell opportunities'
            elif high_churn and record['lifetime_revenue'] < 10000:
                record['ml_segment'] = 'Lost Cause'
                record['ml_segment_action'] = 'Minimal effort, automated email only'
            elif not high_churn and record['order_frequency'] > 1:
                record['ml_segment'] = 'Stable Regular'
                record['ml_segment_action'] = 'Maintain service quality, quarterly check-in'
            else:
                record['ml_segment'] = 'Standard'
                record['ml_segment_action'] = 'Standard service, monitor trends'
            
            # SEQUENTIAL ML ANALYSIS - Root cause diagnosis
            # Stage 1: Detect issue type
            if record['unified_risk_score'] >= 40:
                causes = []
                
                # Time-based issue
                if record['time_risk_score'] > 60:
                    if record['days_overdue'] > record['reorder_variance'] * 2:
                        causes.append({'type': 'timing', 'severity': 'critical', 'detail': f'{record["days_overdue"]}d overdue from {int(record["avg_reorder_days"])}d cycle'})
                    else:
                        causes.append({'type': 'timing', 'severity': 'moderate', 'detail': f'Approaching overdue threshold'})
                
                # Payment issue
                if record['payment_risk_score'] > 50:
                    causes.append({'type': 'payment', 'severity': 'high' if record['late_payments'] > 2 else 'moderate', 'detail': f'{record["late_payments"]} late payments'})
                
                # Frequency decline
                if declining:
                    causes.append({'type': 'engagement', 'severity': 'high', 'detail': f'Order frequency declining {record["trend_score"]}%'})
                
                # Value decline  
                if record['avg_invoice_value'] > 0 and record['lifetime_revenue'] / record['total_invoices'] < record['avg_invoice_value'] * 0.7:
                    causes.append({'type': 'value', 'severity': 'moderate', 'detail': 'Average order value declining'})
                
                record['ml_root_causes'] = causes
                record['ml_primary_issue'] = causes[0]['type'] if causes else 'unknown'
            else:
                record['ml_root_causes'] = []
                record['ml_primary_issue'] = 'none'
            
            # SCENARIO MODELING - Predicted impact of actions
            base_churn = record['ml_churn_probability'] / 100
            
            # Scenario 1: Make personal call
            call_impact = -0.25 if high_value else -0.15  # 25% reduction for high-value, 15% for others
            record['scenario_call'] = int(max(0, (base_churn + call_impact) * 100))
            
            # Scenario 2: Offer discount
            discount_impact = -0.20 if record['ml_primary_issue'] == 'value' else -0.10
            record['scenario_discount'] = int(max(0, (base_churn + discount_impact) * 100))
            
            # Scenario 3: Improve payment terms
            payment_impact = -0.30 if record['ml_primary_issue'] == 'payment' else -0.05
            record['scenario_payment_terms'] = int(max(0, (base_churn + payment_impact) * 100))
            
            # Scenario 4: Do nothing
            natural_decay = 0.05 * (record['predicted_risk_90d'] - record['ml_churn_probability']) / 100
            record['scenario_do_nothing'] = int(min(100, (base_churn + natural_decay) * 100))
            
            # Best action recommendation
            scenarios = {
                'call': record['scenario_call'],
                'discount': record['scenario_discount'],
                'payment_terms': record['scenario_payment_terms']
            }
            record['ml_best_action'] = min(scenarios, key=scenarios.get)
        
        # Calculate summary metrics
        customers_list = list(customer_intelligence.values())
        
        # Filter out internal entities if requested
        if exclude_internal:
            customers_list = [
                c for c in customers_list 
                if not any(entity in c['contact_name'].lower() for entity in INTERNAL_ENTITIES)
            ]
        
        high_risk = [c for c in customers_list if c['risk_category'] == 'High']
        medium_risk = [c for c in customers_list if c['risk_category'] == 'Medium']
        low_risk = [c for c in customers_list if c['risk_category'] == 'Low']
        
        segment_counts = {}
        for customer in customers_list:
            seg = customer['rfm_segment']
            segment_counts[seg] = segment_counts.get(seg, 0) + 1
        
        active = len([c for c in customers_list if c['days_since_last_order'] <= 30])
        at_risk = len([c for c in customers_list if 60 <= c['days_since_last_order'] < 90])
        churned = len([c for c in customers_list if c['days_since_last_order'] >= 90])
        
        total_ltv = sum(c['lifetime_revenue'] for c in customers_list)
        avg_ltv = total_ltv / len(customers_list) if customers_list else 0
        
        late_invoice_count = sum(c['late_payments'] for c in customers_list)
        
        # Generate smart recommendations
        sorted_customers = sorted(customers_list, key=lambda x: x['unified_risk_score'], reverse=True)
        
        recommendations = {
            'urgent': [],
            'this_week': [],
            'this_month': []
        }
        
        for customer in sorted_customers[:12]:
            if customer['risk_category'] == 'High':
                recommendations['urgent'].append({
                    'customer': customer['contact_name'],
                    'action': f"Call {customer['contact_name']} ({customer['unified_risk_score']}% risk, ${customer['lifetime_revenue']:,.0f} LTV)",
                    'risk_score': customer['unified_risk_score'],
                    'ltv': customer['lifetime_revenue']
                })
        
        # THIS WEEK ACTIONS - Include customer details
        medium_risk_customers = [c for c in customers_list if c['risk_category'] == 'Medium']
        if medium_risk_customers:
            recommendations['this_week'].append({
                'action': f"Email campaign to {len(medium_risk_customers)} medium-risk customers",
                'count': len(medium_risk_customers),
                'customer': f"{len(medium_risk_customers)} medium-risk customers",
                'risk_score': sum(c['unified_risk_score'] for c in medium_risk_customers) / len(medium_risk_customers),
                'ltv': sum(c['lifetime_revenue'] for c in medium_risk_customers)
            })
        
        late_invoice_customers = [c for c in customers_list if c['late_payments'] > 0]
        if late_invoice_customers:
            recommendations['this_week'].append({
                'action': f"Follow up on {late_invoice_count} late invoices from {len(late_invoice_customers)} customers",
                'count': len(late_invoice_customers),
                'customer': f"{len(late_invoice_customers)} customers with late payments",
                'risk_score': sum(c['unified_risk_score'] for c in late_invoice_customers) / len(late_invoice_customers),
                'ltv': sum(c['lifetime_revenue'] for c in late_invoice_customers)
            })
        
        # THIS MONTH ACTIONS - Include customer details
        potential_loyalists = [c for c in customers_list if c['rfm_segment'] == 'Potential Loyalists']
        if potential_loyalists:
            recommendations['this_month'].append({
                'action': f"Re-engagement campaign for {len(potential_loyalists)} Potential Loyalist customers",
                'count': len(potential_loyalists),
                'customer': f"{len(potential_loyalists)} Potential Loyalists",
                'risk_score': sum(c['unified_risk_score'] for c in potential_loyalists) / len(potential_loyalists),
                'ltv': sum(c['lifetime_revenue'] for c in potential_loyalists)
            })
        
        champion_customers = [c for c in customers_list if c['rfm_segment'] == 'Champions']
        if champion_customers:
            recommendations['this_month'].append({
                'action': f"Nurture {len(champion_customers)} Champions with VIP treatment",
                'count': len(champion_customers),
                'customer': f"{len(champion_customers)} Champions",
                'risk_score': sum(c['unified_risk_score'] for c in champion_customers) / len(champion_customers) if champion_customers else 0,
                'ltv': sum(c['lifetime_revenue'] for c in champion_customers)
            })
        
        # ML-ENHANCED INSIGHTS - Strategic analysis using ML signals
        ml_segments_count = {}
        for customer in customers_list:
            ml_seg = customer.get('ml_segment', 'Standard')
            ml_segments_count[ml_seg] = ml_segments_count.get(ml_seg, 0) + 1
        
        # Predictive analytics
        avg_confidence = sum(c['ml_confidence'] for c in customers_list) / len(customers_list) if customers_list else 0
        declining_count = len([c for c in customers_list if c['behavior_trend'] == 'declining'])
        improving_count = len([c for c in customers_list if c['behavior_trend'] == 'improving'])
        
        # Revenue at risk calculation
        high_risk_revenue = sum(c['lifetime_revenue'] for c in customers_list if c['unified_risk_score'] >= 70)
        medium_risk_revenue = sum(c['lifetime_revenue'] for c in customers_list if 40 <= c['unified_risk_score'] < 70)
        
        # Best action analysis
        action_recommendations = {}
        for customer in customers_list:
            action = customer.get('ml_best_action', 'monitor')
            action_recommendations[action] = action_recommendations.get(action, 0) + 1
        
        # Root cause analysis
        root_causes_summary = {}
        for customer in customers_list:
            for cause in customer.get('ml_root_causes', []):
                cause_type = cause['type']
                root_causes_summary[cause_type] = root_causes_summary.get(cause_type, 0) + 1
        
        return jsonify({
            'success': True,
            'business': BUSINESS_CONFIGS[business_id]['name'],
            'generated_at': datetime.now().isoformat(),
            'metrics': {
                'total_customers': len(customers_list),
                'active': active,
                'at_risk': at_risk,
                'churned': churned,
                'net_growth': active - churned,
                'avg_ltv': round(avg_ltv, 2),
                'late_invoices': late_invoice_count,
                'retention_rate': round((1 - (churned / len(customers_list))) * 100, 1) if customers_list else 0
            },
            'risk_distribution': {
                'high': len(high_risk),
                'medium': len(medium_risk),
                'low': len(low_risk)
            },
            'segment_distribution': segment_counts,
            'ml_insights': {
                'ml_segments': ml_segments_count,
                'behavior_trends': {
                    'declining': declining_count,
                    'improving': improving_count,
                    'stable': len(customers_list) - declining_count - improving_count
                },
                'revenue_at_risk': {
                    'high_risk': round(high_risk_revenue, 2),
                    'medium_risk': round(medium_risk_revenue, 2),
                    'total': round(high_risk_revenue + medium_risk_revenue, 2)
                },
                'recommended_actions': action_recommendations,
                'root_causes': root_causes_summary,
                'avg_ml_confidence': round(avg_confidence, 1),
                'predictive_summary': {
                    'avg_30d_risk': round(sum(c['predicted_risk_30d'] for c in customers_list) / len(customers_list), 1) if customers_list else 0,
                    'avg_60d_risk': round(sum(c['predicted_risk_60d'] for c in customers_list) / len(customers_list), 1) if customers_list else 0,
                    'avg_90d_risk': round(sum(c['predicted_risk_90d'] for c in customers_list) / len(customers_list), 1) if customers_list else 0
                }
            },
            'customers': sorted_customers,
            'recommendations': recommendations
        })
    
    except Exception as e:
        print(f"Error in xero_report_customer_intelligence: {e}")
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
            
            dt = parse_xero_date(inv_date)
            if not dt:
                continue
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


@cross_origin()
def xero_get_customer_details():
    """
    Get comprehensive customer details for drill-down view.
    
    Combines data from:
    1. Xero Contacts API
    2. Customer Intelligence ML pipeline
    3. Invoice history
    4. Activity log
    
    Returns all data needed for full-tab customer detail view.
    """
    try:
        contact_id = request.args.get('contact_id')
        business_id = int(request.args.get('business_id', 1))
        
        if not contact_id:
            return jsonify({'success': False, 'error': 'contact_id is required'}), 400
        
        client = XeroAPIClient(business_id)
        
        # 1. Get Xero contact details
        contact_data = client.make_request('GET', f'Contacts/{contact_id}')
        contacts = contact_data.get('Contacts', [])
        
        if not contacts:
            return jsonify({'success': False, 'error': 'Contact not found'}), 404
        
        contact = contacts[0]
        
        # 2. Get customer intelligence ML data for this specific contact
        # Fetch all invoices for this contact
        invoices_data = client.make_request('GET', 'Invoices', params={
            'where': f'Contact.ContactID=Guid("{contact_id}")'
        })
        invoices = invoices_data.get('Invoices', [])
        
        # Calculate ML insights (reuse logic from customer_intelligence)
        current_date = datetime.now()
        invoice_history = []
        reorder_dates = []
        total_revenue = 0
        invoice_values = []
        
        for inv in sorted(invoices, key=lambda x: parse_xero_date(x.get('Date')) or datetime.min):
            inv_date = parse_xero_date(inv.get('Date'))
            paid_date = parse_xero_date(inv.get('FullyPaidOnDate'))
            status = inv.get('Status', 'UNKNOWN')
            total = float(inv.get('Total', 0))
            amount_due = float(inv.get('AmountDue', 0))
            
            if inv_date:
                reorder_dates.append(inv_date)
                total_revenue += total
                invoice_values.append(total)
            
            # Calculate days to pay
            days_to_pay = None
            if paid_date and inv_date:
                days_to_pay = (paid_date - inv_date).days
            elif status != 'PAID':
                days_to_pay = (current_date - inv_date).days if inv_date else None
            
            invoice_history.append({
                'date': inv_date.isoformat() if inv_date else None,
                'invoice_number': inv.get('InvoiceNumber', ''),
                'amount': total,
                'amount_due': amount_due,
                'paid_date': paid_date.isoformat() if paid_date else None,
                'days_to_pay': days_to_pay,
                'status': status
            })
        
        # Calculate reorder frequency statistics
        avg_reorder_days = 0
        reorder_variance = 0
        last_order_date = None
        days_since_last_order = 0
        
        if len(reorder_dates) >= 2:
            gaps = [(reorder_dates[i+1] - reorder_dates[i]).days 
                    for i in range(len(reorder_dates)-1)]
            avg_reorder_days = sum(gaps) / len(gaps) if gaps else 0
            
            # Calculate variance
            if len(gaps) >= 2:
                mean_gap = avg_reorder_days
                variance_sum = sum((gap - mean_gap) ** 2 for gap in gaps)
                reorder_variance = (variance_sum / (len(gaps) - 1)) ** 0.5
            
            last_order_date = reorder_dates[-1]
            days_since_last_order = (current_date - last_order_date).days
        
        # Calculate expected reorder date
        expected_reorder_date = None
        days_overdue = 0
        if last_order_date and avg_reorder_days > 0:
            expected_reorder_date = last_order_date + timedelta(days=avg_reorder_days)
            days_overdue = max(0, (current_date - expected_reorder_date).days)
        
        # Calculate deviation score (statistical significance of delay)
        deviation_score = 0
        if avg_reorder_days > 0 and reorder_variance > 0:
            deviation_score = (days_since_last_order - avg_reorder_days) / reorder_variance
        
        # ML Risk Scoring
        churn_probability = 0
        if avg_reorder_days > 0:
            delay_factor = min(days_overdue / avg_reorder_days, 2.0) if avg_reorder_days > 0 else 0
            variance_factor = min(reorder_variance / avg_reorder_days, 1.0) if avg_reorder_days > 0 else 0
            churn_probability = min(100, (delay_factor * 50) + (variance_factor * 30))
        
        payment_risk_score = churn_probability * 0.8  # Simplified correlation
        
        # Determine behavior trend
        behavior_trend = 'stable'
        if len(reorder_dates) >= 3:
            recent_gaps = [(reorder_dates[i+1] - reorder_dates[i]).days 
                          for i in range(max(0, len(reorder_dates)-4), len(reorder_dates)-1)]
            if len(recent_gaps) >= 2:
                trend_slope = (recent_gaps[-1] - recent_gaps[0]) / len(recent_gaps)
                if trend_slope > 5:
                    behavior_trend = 'declining'
                elif trend_slope < -5:
                    behavior_trend = 'improving'
        
        # Strategic segmentation
        strategic_segment = 'Standard'
        if total_revenue > 50000:
            if churn_probability < 30:
                strategic_segment = 'VIP-Protect'
            elif churn_probability >= 70:
                strategic_segment = 'VIP At-Risk'
            else:
                strategic_segment = 'High-Value Declining'
        elif total_revenue > 10000:
            if behavior_trend == 'improving':
                strategic_segment = 'Rising Star'
            elif churn_probability >= 80:
                strategic_segment = 'Lost Cause'
            else:
                strategic_segment = 'Stable Regular'
        
        # Root cause analysis
        root_causes = []
        if days_overdue > avg_reorder_days * 0.5:
            root_causes.append({
                'name': 'Timing Issues',
                'description': f'Order frequency decreased from {int(avg_reorder_days)} to {days_since_last_order} days'
            })
        if reorder_variance > avg_reorder_days * 0.3:
            root_causes.append({
                'name': 'Payment Issues',
                'description': f'Inconsistent payment timing (variance: {int(reorder_variance)} days)'
            })
        if days_since_last_order > 90:
            root_causes.append({
                'name': 'Engagement Issues',
                'description': f'No contact in {days_since_last_order} days'
            })
        
        # Scenario modeling
        scenarios = {
            'executive_call': {
                'churn_reduction': 15,
                'expected_ltv_increase': total_revenue * 0.15,
                'roi': 1500
            },
            'offer_discount': {
                'churn_reduction': 10,
                'expected_ltv_increase': total_revenue * 0.10,
                'roi': 350
            },
            'payment_plan': {
                'churn_reduction': 8,
                'expected_ltv_increase': total_revenue * 0.08,
                'roi': 0
            },
            'no_action': {
                'churn_reduction': -5,
                'expected_ltv_increase': -total_revenue * 0.05,
                'roi': -100
            }
        }
        
        # Best action recommendation
        best_action = 'call'
        best_action_reason = 'High-value customer showing signs of churn'
        if total_revenue < 5000:
            best_action = 'email'
            best_action_reason = 'Standard customer - email reminder appropriate'
        elif churn_probability > 70:
            best_action = 'call'
            best_action_reason = 'High churn risk requires personal outreach'
        
        # Financial summary with LTV forecasting
        avg_invoice_value = total_revenue / len(invoices) if invoices else 0
        predicted_12m_ltv = 0
        if avg_reorder_days > 0:
            expected_orders_12m = 365 / avg_reorder_days
            predicted_12m_ltv = expected_orders_12m * avg_invoice_value
            
            if behavior_trend == 'improving':
                predicted_12m_ltv *= 1.15
            elif behavior_trend == 'declining':
                predicted_12m_ltv *= 0.85
        
        churn_adjusted_ltv = predicted_12m_ltv * (1 - churn_probability / 100)
        total_expected_ltv = total_revenue + churn_adjusted_ltv
        
        # Activity log (recent transactions)
        activity_log = []
        for inv in invoices[-10:]:
            inv_date = parse_xero_date(inv.get('Date'))
            paid_date = parse_xero_date(inv.get('FullyPaidOnDate'))
            status = inv.get('Status')
            amount = float(inv.get('Total', 0))
            
            if status == 'PAID' and paid_date:
                activity_log.append({
                    'date': paid_date.isoformat(),
                    'action': f'Payment received: ${amount:,.2f} for {inv.get("InvoiceNumber")}'
                })
            activity_log.append({
                'date': inv_date.isoformat() if inv_date else '',
                'action': f'Invoice created: {inv.get("InvoiceNumber")} (${amount:,.2f})'
            })
        
        activity_log.sort(key=lambda x: x['date'], reverse=True)
        
        # Compile comprehensive response
        return jsonify({
            'success': True,
            'customer': {
                'profile': {
                    'contact_id': contact.get('ContactID'),
                    'name': contact.get('Name', 'Unknown'),
                    'email': contact.get('EmailAddress', ''),
                    'phone': contact.get('Phones', [{}])[0].get('PhoneNumber', '') if contact.get('Phones') else '',
                    'address': ', '.join(filter(None, [
                        contact.get('Addresses', [{}])[0].get('AddressLine1', ''),
                        contact.get('Addresses', [{}])[0].get('City', ''),
                        contact.get('Addresses', [{}])[0].get('PostalCode', '')
                    ])) if contact.get('Addresses') else '',
                    'customer_since': reorder_dates[0].isoformat() if reorder_dates else None,
                    'payment_terms': 'Net 30',  # Could parse from contact.DefaultPaymentTerms
                    'is_customer': contact.get('IsCustomer', False),
                    'is_supplier': contact.get('IsSupplier', False)
                },
                'ml_insights': {
                    'ml_churn_probability': round(churn_probability, 1),
                    'payment_risk_score': round(payment_risk_score, 1),
                    'deviation_score': round(deviation_score, 2),
                    'lifetime_revenue': round(total_revenue, 2),
                    'strategic_segment': strategic_segment,
                    'behavior_trend': behavior_trend,
                    'ml_confidence_score': 85,  # Based on data quality
                    'root_causes': root_causes[:3]
                },
                'financial_summary': {
                    'historical_ltv': round(total_revenue, 2),
                    'predicted_12m_ltv': round(predicted_12m_ltv, 2),
                    'churn_adjusted_ltv': round(churn_adjusted_ltv, 2),
                    'total_expected_ltv': round(total_expected_ltv, 2),
                    'avg_invoice_value': round(avg_invoice_value, 2),
                    'avg_reorder_frequency': round(avg_reorder_days, 1),
                    'reorder_variance': round(reorder_variance, 1),
                    'current_outstanding': sum(inv['amount_due'] for inv in invoice_history),
                    'days_overdue': days_overdue,
                    'collection_risk': round(payment_risk_score, 1)
                },
                'invoices': invoice_history[-20:],  # Last 20 invoices
                'activity_log': activity_log[:10],  # Last 10 activities
                'scenarios': scenarios,
                'best_action': best_action,
                'best_action_reason': best_action_reason,
                'priority_rank': None,  # Set by collection queue
                'best_contact_time': 'Tuesday-Thursday, 10am-2pm',
                'next_optimal_window': 'Tomorrow at 10:30am'
            }
        })
    
    except Exception as e:
        print(f"Error in xero_get_customer_details: {e}")
        traceback.print_exc()
        return jsonify({'success': False, 'error': str(e)}), 500
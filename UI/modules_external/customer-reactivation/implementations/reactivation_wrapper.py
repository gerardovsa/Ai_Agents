"""
Customer Reactivation Module - Tool Implementations
===================================================

AI tool wrappers for customer reactivation operations.
Integrates with Flask backend and Xero ML models.

Created: January 18, 2026
"""

import sys
import json
import requests
from pathlib import Path
from typing import Dict, List, Any, Optional

# Add tools directory to path for registry
tools_dir = Path(__file__).resolve().parent.parent.parent.parent.parent / 'tools'
sys.path.insert(0, str(tools_dir))

from registry_v3 import tool_executor

# Backend API base URL
API_BASE = 'http://localhost:5001/api/reactivation'


# ============================================================================
# CUSTOMER INSIGHTS & SYNC
# ============================================================================

@tool_executor()
def reactivation_sync_at_risk_customers(business_id: int = 1, min_churn_risk: int = 60) -> Dict[str, Any]:
    """
    Sync at-risk customers from Xero churn-risk-ml API to prospects cache.
    
    Fetches customers with specified churn risk threshold and enriches with
    contact details from Xero. Caches data for fast campaign building.
    
    Args:
        business_id: Xero business ID (1=Print, 2=Publishing, 3=Signs)
        min_churn_risk: Minimum churn risk score percentage (0-100)
        
    Returns:
        dict: {
            'success': bool,
            'synced_count': int,
            'customers': list of customer objects,
            'stats': {'high_risk': int, 'medium_risk': int, 'total_revenue_at_risk': float}
        }
    """
    try:
        response = requests.get(
            f'{API_BASE}/at-risk-customers',
            params={
                'business_id': business_id,
                'min_churn_risk': min_churn_risk,
                'sync': 'true'  # Force fresh sync from Xero
            },
            timeout=30
        )
        
        if response.status_code != 200:
            return {
                'success': False,
                'error': f'API returned status {response.status_code}: {response.text}'
            }
        
        data = response.json()
        
        return {
            'success': True,
            'synced_count': data.get('total', 0),
            'customers': data.get('customers', []),
            'stats': data.get('stats', {})
        }
        
    except Exception as e:
        return {
            'success': False,
            'error': str(e)
        }


@tool_executor()
def reactivation_get_dashboard(user_id: int = 1, business_id: int = 1) -> Dict[str, Any]:
    """
    Get dashboard overview with aggregate campaign metrics.
    
    Shows total emails sent, open rates, click rates, reorders, revenue recovered,
    ROI, and at-risk customer counts across all campaigns.
    
    Args:
        user_id: User ID to fetch dashboard for
        business_id: Xero business ID to filter by
        
    Returns:
        dict: {
            'success': bool,
            'stats': {
                'total_campaigns': int,
                'emails_sent': int,
                'avg_open_rate': float,
                'avg_click_rate': float,
                'reorder_rate': float,
                'revenue_recovered': float,
                'roi_percentage': float,
                'at_risk_customers': {'high_risk': int, 'medium_risk': int, 'total': int}
            },
            'recent_campaigns': list of campaign summaries
        }
    """
    try:
        response = requests.get(
            f'{API_BASE}/dashboard',
            params={'user_id': user_id, 'business_id': business_id},
            timeout=10
        )
        
        if response.status_code != 200:
            return {
                'success': False,
                'error': f'API returned status {response.status_code}'
            }
        
        return response.json()
        
    except Exception as e:
        return {
            'success': False,
            'error': str(e)
        }


# ============================================================================
# CAMPAIGN MANAGEMENT
# ============================================================================

@tool_executor()
def reactivation_create_campaign(
    campaign_name: str,
    template_id: int,
    subject_line: str,
    user_id: int = 1,
    campaign_type: str = 'reactivation',
    xero_business_id: int = 1,
    target_segment: str = 'at_risk',
    churn_threshold: int = 60,
    discount_code: Optional[str] = None,
    discount_amount: float = 0,
    discount_type: str = 'percentage',
    campaign_cost: float = 0
) -> Dict[str, Any]:
    """
    Create a new customer reactivation email campaign.
    
    Specify campaign name, target customer segment, email template, discount offer,
    and scheduling. Returns campaign ID for further operations.
    
    Args:
        campaign_name: Descriptive name (e.g., 'Q1 2026 Win-Back')
        template_id: Email template ID to use
        subject_line: Email subject line (supports merge fields)
        user_id: User ID creating the campaign
        campaign_type: Type of campaign (reactivation, win_back, feedback, etc.)
        xero_business_id: Xero business ID to target
        target_segment: Customer segment (at_risk, high_risk, medium_risk, etc.)
        churn_threshold: Minimum churn risk score to include
        discount_code: Discount code to include in emails
        discount_amount: Discount amount (percentage or fixed)
        discount_type: Type of discount (percentage or fixed)
        campaign_cost: Estimated campaign cost for ROI calculation
        
    Returns:
        dict: {
            'success': bool,
            'campaign_id': int,
            'message': str
        }
    """
    try:
        payload = {
            'user_id': user_id,
            'campaign_name': campaign_name,
            'campaign_type': campaign_type,
            'xero_business_id': xero_business_id,
            'target_segment': target_segment,
            'churn_threshold': churn_threshold,
            'template_id': template_id,
            'subject_line': subject_line,
            'discount_code': discount_code,
            'discount_amount': discount_amount,
            'discount_type': discount_type,
            'campaign_cost': campaign_cost
        }
        
        response = requests.post(
            f'{API_BASE}/campaigns',
            json=payload,
            timeout=10
        )
        
        if response.status_code != 200:
            return {
                'success': False,
                'error': f'API returned status {response.status_code}: {response.text}'
            }
        
        return response.json()
        
    except Exception as e:
        return {
            'success': False,
            'error': str(e)
        }


@tool_executor()
def reactivation_add_recipients(campaign_id: int, recipients: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Add recipients to an existing campaign.
    
    Provide array of customer objects with contact details and Xero data.
    Automatically links to Xero contact IDs for reorder tracking.
    
    Args:
        campaign_id: Campaign ID to add recipients to
        recipients: Array of recipient objects with customer details
            Each recipient should include:
            - email (required)
            - customer_name (required)
            - xero_contact_id (optional but recommended)
            - first_name, last_name, phone
            - churn_risk_score, total_revenue, months_since_last_order
            - custom_fields (dict of additional data)
            
    Returns:
        dict: {
            'success': bool,
            'added': int (number of recipients added),
            'campaign_id': int
        }
    """
    try:
        payload = {
            'recipients': recipients
        }
        
        response = requests.post(
            f'{API_BASE}/campaigns/{campaign_id}/recipients',
            json=payload,
            timeout=30
        )
        
        if response.status_code != 200:
            return {
                'success': False,
                'error': f'API returned status {response.status_code}: {response.text}'
            }
        
        return response.json()
        
    except Exception as e:
        return {
            'success': False,
            'error': str(e)
        }


@tool_executor()
def reactivation_send_campaign(campaign_id: int) -> Dict[str, Any]:
    """
    Send campaign emails to all pending recipients via SendGrid.
    
    Automatically personalizes each email with merge fields, adds tracking pixels
    for opens, and logs all sending events. Updates campaign status to 'completed'.
    
    Args:
        campaign_id: Campaign ID to send
        
    Returns:
        dict: {
            'success': bool,
            'campaign_id': int,
            'emails_sent': int
        }
    """
    try:
        response = requests.post(
            f'{API_BASE}/campaigns/{campaign_id}/send',
            timeout=120  # Longer timeout for bulk sending
        )
        
        if response.status_code != 200:
            return {
                'success': False,
                'error': f'API returned status {response.status_code}: {response.text}'
            }
        
        return response.json()
        
    except Exception as e:
        return {
            'success': False,
            'error': str(e)
        }


# ============================================================================
# ANALYTICS & TRACKING
# ============================================================================

@tool_executor()
def reactivation_get_campaign_analytics(campaign_id: int) -> Dict[str, Any]:
    """
    Get detailed analytics for a campaign.
    
    Shows open rates, click rates, reorder conversion, revenue recovered, and
    event timeline. Includes full ROI calculation with costs vs recovered revenue.
    
    Args:
        campaign_id: Campaign ID to analyze
        
    Returns:
        dict: {
            'success': bool,
            'stats': {
                'total_recipients': int,
                'sent': int,
                'opened': int,
                'clicked': int,
                'bounced': int,
                'reordered': int,
                'revenue_recovered': float,
                'open_rate': float,
                'click_rate': float,
                'reorder_rate': float
            },
            'timeline': list of event counts by date
        }
    """
    try:
        response = requests.get(
            f'{API_BASE}/campaigns/{campaign_id}/analytics',
            timeout=10
        )
        
        if response.status_code != 200:
            return {
                'success': False,
                'error': f'API returned status {response.status_code}: {response.text}'
            }
        
        return response.json()
        
    except Exception as e:
        return {
            'success': False,
            'error': str(e)
        }


@tool_executor()
def reactivation_check_reorders(campaign_id: int) -> Dict[str, Any]:
    """
    Check Xero for new orders from campaign recipients to track reactivation success.
    
    Polls Xero invoices by date range and matches against campaign recipients.
    Updates reorder status and revenue recovered metrics automatically.
    
    Args:
        campaign_id: Campaign ID to check reorders for
        
    Returns:
        dict: {
            'success': bool,
            'campaign_id': int,
            'reorder_count': int,
            'revenue_recovered': float,
            'updated_recipients': list of recipient objects with reorder data
        }
    """
    try:
        # Import inside function to avoid circular imports
        from AI_infrastructure.shared.database_utils import execute_query
        
        # Get campaign details
        campaign = execute_query("""
            SELECT xero_business_id, sent_at
            FROM ai_infrastructure.reactivation_campaigns
            WHERE campaign_id = %s
        """, (campaign_id,), fetch_mode='one')
        
        if not campaign:
            return {
                'success': False,
                'error': 'Campaign not found'
            }
        
        business_id = campaign[0]
        sent_at = campaign[1]
        
        if not sent_at:
            return {
                'success': False,
                'error': 'Campaign not yet sent'
            }
        
        # Get campaign recipients
        recipients = execute_query("""
            SELECT id, xero_contact_id, email, customer_name
            FROM ai_infrastructure.reactivation_recipients
            WHERE campaign_id = %s AND status != 'bounced'
        """, (campaign_id,), fetch_mode='all')
        
        reorder_count = 0
        revenue_recovered = 0
        updated_recipients = []
        
        # Check each recipient for new invoices
        for recipient in (recipients or []):
            if not recipient[1]:  # Skip if no Xero contact ID
                continue
            
            # Query Xero for invoices after campaign sent date
            xero_url = f'http://localhost:5001/api/xero/invoices'
            xero_response = requests.get(
                xero_url,
                params={
                    'business_id': business_id,
                    'contact_id': recipient[1],
                    'from_date': sent_at.strftime('%Y-%m-%d')
                },
                timeout=10
            )
            
            if xero_response.status_code == 200:
                xero_data = xero_response.json()
                invoices = xero_data.get('invoices', [])
                
                if invoices:
                    # Customer reordered!
                    total_amount = sum(inv.get('Total', 0) for inv in invoices)
                    
                    # Update recipient status
                    execute_query("""
                        UPDATE ai_infrastructure.reactivation_recipients
                        SET status = 'reordered',
                            reordered_at = NOW(),
                            reorder_amount = %s,
                            reorder_invoice_id = %s
                        WHERE id = %s
                    """, (total_amount, invoices[0].get('InvoiceID'), recipient[0]))
                    
                    # Log tracking event
                    execute_query("""
                        INSERT INTO ai_infrastructure.reactivation_tracking
                        (campaign_id, recipient_id, recipient_email, event_type, event_data)
                        VALUES (%s, %s, %s, 'reorder', %s)
                    """, (
                        campaign_id,
                        recipient[0],
                        recipient[2],
                        json.dumps({
                            'invoice_count': len(invoices),
                            'total_amount': total_amount,
                            'invoice_ids': [inv.get('InvoiceID') for inv in invoices]
                        })
                    ))
                    
                    reorder_count += 1
                    revenue_recovered += total_amount
                    updated_recipients.append({
                        'recipient_id': recipient[0],
                        'customer_name': recipient[3],
                        'email': recipient[2],
                        'reorder_amount': total_amount,
                        'invoice_count': len(invoices)
                    })
        
        # Update campaign metrics
        execute_query("""
            UPDATE ai_infrastructure.reactivation_campaigns
            SET reorders = %s,
                revenue_recovered = %s,
                roi_percentage = CASE 
                    WHEN campaign_cost > 0 
                    THEN ((revenue_recovered - campaign_cost) / campaign_cost * 100)
                    ELSE 0 
                END
            WHERE campaign_id = %s
        """, (reorder_count, revenue_recovered, campaign_id))
        
        return {
            'success': True,
            'campaign_id': campaign_id,
            'reorder_count': reorder_count,
            'revenue_recovered': revenue_recovered,
            'updated_recipients': updated_recipients
        }
        
    except Exception as e:
        import traceback
        return {
            'success': False,
            'error': str(e),
            'traceback': traceback.format_exc()
        }


# ============================================================================
# TEMPLATE MANAGEMENT
# ============================================================================

@tool_executor()
def reactivation_list_templates(user_id: int = 1, template_type: Optional[str] = None) -> Dict[str, Any]:
    """
    List all available email templates.
    
    Filter by template type (reactivation, win_back, feedback, etc.) or category.
    Includes pre-built templates with proven subject lines and HTML designs.
    
    Args:
        user_id: User ID to fetch templates for
        template_type: Optional filter by template type
        
    Returns:
        dict: {
            'success': bool,
            'templates': list of template objects,
            'total': int
        }
    """
    try:
        params = {'user_id': user_id}
        if template_type:
            params['type'] = template_type
        
        response = requests.get(
            f'{API_BASE}/templates',
            params=params,
            timeout=10
        )
        
        if response.status_code != 200:
            return {
                'success': False,
                'error': f'API returned status {response.status_code}'
            }
        
        return response.json()
        
    except Exception as e:
        return {
            'success': False,
            'error': str(e)
        }


@tool_executor()
def reactivation_create_template(
    template_name: str,
    subject: str,
    html_body: str,
    user_id: int = 1,
    template_type: str = 'reactivation',
    text_body: Optional[str] = None,
    merge_fields: List[str] = None,
    category: str = 'Reactivation'
) -> Dict[str, Any]:
    """
    Create a new email template.
    
    Supports personalization variables like {{first_name}}, {{discount_code}},
    {{months_inactive}}, and custom fields. Saves template for reuse across campaigns.
    
    Args:
        template_name: Template name for identification
        subject: Email subject line (supports merge fields)
        html_body: HTML email body with inline CSS and merge fields
        user_id: User ID creating the template
        template_type: Template category
        text_body: Plain text version of email
        merge_fields: Available merge fields
        category: Template category for organization
        
    Returns:
        dict: {
            'success': bool,
            'template_id': int,
            'message': str
        }
    """
    try:
        from AI_infrastructure.shared.database_utils import execute_query
        
        if merge_fields is None:
            merge_fields = ['first_name', 'customer_name', 'discount_code']
        
        template_id = execute_query("""
            INSERT INTO ai_infrastructure.reactivation_templates
            (user_id, template_name, template_type, subject, html_body, text_body, 
             merge_fields, category, is_public)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, FALSE)
            RETURNING template_id
        """, (
            user_id,
            template_name,
            template_type,
            subject,
            html_body,
            text_body or '',
            json.dumps(merge_fields),
            category
        ), fetch_mode='value')
        
        return {
            'success': True,
            'template_id': template_id,
            'message': 'Template created successfully'
        }
        
    except Exception as e:
        import traceback
        return {
            'success': False,
            'error': str(e),
            'traceback': traceback.format_exc()
        }


# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

def get_at_risk_customers_for_campaign(business_id: int, min_churn_risk: int) -> List[Dict[str, Any]]:
    """Helper to get formatted at-risk customers for campaign creation"""
    try:
        result = reactivation_sync_at_risk_customers(business_id, min_churn_risk)
        if result.get('success'):
            return result.get('customers', [])
        return []
    except Exception:
        return []

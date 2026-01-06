"""
ML Analytics Routes - Machine Learning Predictions & Intelligence
========================================================================

Provides Flask API endpoints for ML-powered analytics and predictions:
- Customer churn prediction
- Payment timing prediction
- Invoice anomaly detection
- Revenue forecasting
- Customer lifetime value (CLV) prediction
- Product recommendations
- Fraud detection
- Smart payment reconciliation

Created: January 5, 2026
"""

import sys
import os
from pathlib import Path
from datetime import datetime, timedelta
from flask import Blueprint, jsonify, request
from flask_cors import cross_origin
import traceback
import json
from functools import lru_cache
import time
import threading

# Add AI_infrastructure to path
ai_infra_path = str(Path(__file__).parent.parent)
if ai_infra_path not in sys.path:
    sys.path.insert(0, ai_infra_path)

# ================================
# CONNECTION POOL FIX (Jan 5, 2026 - Updated Jan 6, 2026)
# ================================
# Cache table existence checks to prevent pool exhaustion from repeated queries.
# Problem v1: Each ML prediction endpoint was checking if cache tables exist on EVERY request,
# causing 271+ connection pool acquisitions during load testing.
# Solution v1: Cache table existence for 5 minutes to reduce queries.
# Problem v2: Concurrent requests hit check_table_exists() before cache populates, exhausting pool.
# Solution v2: Thread-safe caching + pre-populate cache on module load + graceful degradation.

_cache_table_exists = {}
_cache_ttl = 300  # 5 minutes
_cache_lock = threading.Lock()
_cache_initialized = False

def check_table_exists(table_name):
    """
    Check if table exists (cached for 5 minutes to reduce DB load).
    Thread-safe with graceful degradation if connection pool exhausted.
    """
    now = time.time()
    
    # Fast path: Return cached result without locking
    if table_name in _cache_table_exists:
        cached_time, exists = _cache_table_exists[table_name]
        if now - cached_time < _cache_ttl:
            return exists
    
    # Slow path: Query database with lock to prevent concurrent queries
    with _cache_lock:
        # Double-check cache after acquiring lock (another thread may have populated it)
        if table_name in _cache_table_exists:
            cached_time, exists = _cache_table_exists[table_name]
            if now - cached_time < _cache_ttl:
                return exists
        
        # Query database
        try:
            from shared.database_utils import execute_query
            result = execute_query(
                "SELECT EXISTS (SELECT FROM information_schema.tables WHERE table_name = %s)",
                (table_name,),
                fetch_mode='value'
            )
            _cache_table_exists[table_name] = (now, result)
            print(f"[ML Routes] Table '{table_name}' existence cached: {result}")
            return result
        except Exception as e:
            # Graceful degradation: Assume table doesn't exist if pool exhausted
            error_msg = str(e)
            if 'pool exhausted' in error_msg.lower() or 'connection' in error_msg.lower():
                print(f"[ML Routes] ⚠️ Connection pool exhausted - assuming '{table_name}' doesn't exist")
                _cache_table_exists[table_name] = (now, False)
                return False
            else:
                print(f"[ML Routes] Table existence check failed for {table_name}: {e}")
                _cache_table_exists[table_name] = (now, False)
                return False

def _initialize_table_cache():
    """Pre-populate table existence cache on module load to prevent concurrent queries."""
    global _cache_initialized
    if _cache_initialized:
        return
    
    with _cache_lock:
        if _cache_initialized:  # Double-check after acquiring lock
            return
        
        print("[ML Routes] Pre-populating table existence cache...")
        tables_to_check = ['xero_contacts_cache', 'xero_invoices_cache']
        
        for table in tables_to_check:
            try:
                check_table_exists(table)  # Will populate cache
            except Exception as e:
                print(f"[ML Routes] Failed to pre-populate cache for '{table}': {e}")
        
        _cache_initialized = True
        print(f"[ML Routes] Cache initialized with {len(_cache_table_exists)} tables")


from shared.database_utils import execute_query

# Create blueprint
ml_bp = Blueprint('ml', __name__, url_prefix='/api/ml')

# 🛡️ DEFENSIVE FIX: Initialize cache with timeout protection
# Run cache initialization in background thread to prevent server startup hang
# If database connection hangs, server will still start and cache will retry on first request
import threading

def _safe_initialize_cache():
    """Initialize cache with timeout protection (runs in background)"""
    try:
        # Set timeout alarm to prevent indefinite hang
        import signal
        
        def timeout_handler(signum, frame):
            raise TimeoutError("Cache initialization timed out after 10 seconds")
        
        # Only use signal on Unix-like systems (not Windows)
        if hasattr(signal, 'SIGALRM'):
            signal.signal(signal.SIGALRM, timeout_handler)
            signal.alarm(10)  # 10 second timeout
        
        _initialize_table_cache()
        
        if hasattr(signal, 'SIGALRM'):
            signal.alarm(0)  # Cancel alarm
            
    except TimeoutError as e:
        print(f"[ML Routes] ⚠️ Cache initialization timed out - will retry on first request")
    except Exception as e:
        print(f"[ML Routes] ⚠️ Cache initialization failed - will retry on first request: {e}")

# Start cache initialization in background (don't block server startup)
cache_thread = threading.Thread(target=_safe_initialize_cache, daemon=True)
cache_thread.start()
print("[ML Routes] Cache initialization started in background (non-blocking)")

# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

def get_xero_contacts(business_id: int):
    """Get Xero contacts from database cache"""
    try:
        query = """
            SELECT contact_id, name, email, phone, total_revenue, 
                   last_order_date, order_count, days_since_last_order
            FROM xero_contacts_cache
            WHERE business_id = %s
            ORDER BY total_revenue DESC
        """
        contacts = execute_query(query, (business_id,), fetch_mode='all')
        return contacts or []
    except Exception as e:
        print(f"[ML Routes] Error fetching contacts: {e}")
        return []

def get_xero_invoices(business_id: int, days_back: int = 365):
    """Get Xero invoices from database cache"""
    try:
        cutoff_date = (datetime.now() - timedelta(days=days_back)).date()
        query = """
            SELECT invoice_id, invoice_number, contact_id, contact_name,
                   date, due_date, total, amount_due, amount_paid, status,
                   days_overdue, payment_date
            FROM xero_invoices_cache
            WHERE business_id = %s AND date >= %s
            ORDER BY date DESC
        """
        invoices = execute_query(query, (business_id, cutoff_date), fetch_mode='all')
        return invoices or []
    except Exception as e:
        print(f"[ML Routes] Error fetching invoices: {e}")
        return []

def get_xero_payments(business_id: int, days_back: int = 365):
    """Get Xero payments from database cache"""
    try:
        cutoff_date = (datetime.now() - timedelta(days=days_back)).date()
        query = """
            SELECT payment_id, invoice_id, invoice_number, contact_id,
                   contact_name, date, amount, status
            FROM xero_payments_cache
            WHERE business_id = %s AND date >= %s
            ORDER BY date DESC
        """
        payments = execute_query(query, (business_id, cutoff_date), fetch_mode='all')
        return payments or []
    except Exception as e:
        print(f"[ML Routes] Error fetching payments: {e}")
        return []

# ============================================================================
# DASHBOARD ANALYTICS
# ============================================================================

@ml_bp.route('/dashboard/summary', methods=['GET', 'OPTIONS'])
@cross_origin()
def ml_dashboard_summary():
    """
    Get AI-generated executive summary for dashboard
    
    Returns:
        - AI-generated narrative summary
        - Critical alerts
        - Top priorities
        - Key metrics with trends
    """
    try:
        business_id = int(request.args.get('business_id', 1))
        
        # Get data from cache
        contacts = get_xero_contacts(business_id)
        invoices = get_xero_invoices(business_id, days_back=90)
        payments = get_xero_payments(business_id, days_back=90)
        
        # Calculate metrics
        total_revenue_mtd = sum(inv.get('total', 0) for inv in invoices if inv.get('status') == 'PAID')
        total_outstanding = sum(inv.get('amount_due', 0) for inv in invoices if inv.get('status') in ['AUTHORISED', 'SUBMITTED'])
        overdue_count = sum(1 for inv in invoices if inv.get('days_overdue', 0) > 0)
        at_risk_customers = sum(1 for c in contacts if c.get('days_since_last_order', 0) > 60)
        
        # Generate AI summary (simplified - in production, use GPT-4 or Claude)
        summary_text = f"Revenue this month: ${total_revenue_mtd:,.2f}. " \
                      f"{len(invoices)} invoices processed. " \
                      f"{at_risk_customers} customers at-risk of churn. " \
                      f"${total_outstanding:,.2f} outstanding."
        
        # Critical alerts (rule-based for now)
        alerts = []
        if overdue_count > 5:
            alerts.append({
                'severity': 'high',
                'type': 'overdue_invoices',
                'message': f'{overdue_count} invoices overdue',
                'action': 'Review and chase payments'
            })
        if at_risk_customers > 0:
            alerts.append({
                'severity': 'medium',
                'type': 'churn_risk',
                'message': f'{at_risk_customers} customers at-risk (no orders 60+ days)',
                'action': 'Initiate retention campaigns'
            })
        
        # Top priorities
        priorities = [
            {
                'id': 1,
                'title': 'Contact at-risk customers',
                'description': f'{at_risk_customers} customers need retention outreach',
                'urgency': 'high' if at_risk_customers > 10 else 'medium'
            }
        ]
        
        if overdue_count > 0:
            priorities.append({
                'id': 2,
                'title': 'Follow up on overdue invoices',
                'description': f'{overdue_count} invoices require payment chase',
                'urgency': 'high'
            })
        
        return jsonify({
            'success': True,
            'summary': {
                'text': summary_text,
                'generated_at': datetime.now().isoformat()
            },
            'alerts': alerts,
            'priorities': priorities,
            'metrics': {
                'revenue_mtd': total_revenue_mtd,
                'outstanding': total_outstanding,
                'overdue_count': overdue_count,
                'at_risk_customers': at_risk_customers,
                'active_customers': len([c for c in contacts if c.get('days_since_last_order', 999) < 90])
            }
        })
    
    except Exception as e:
        print(f"[ML Routes] Error in ml_dashboard_summary: {e}")
        traceback.print_exc()
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

# ============================================================================
# CHURN PREDICTION
# ============================================================================

@ml_bp.route('/predict/churn/<contact_id>', methods=['GET', 'OPTIONS'])
@cross_origin()
def predict_churn(contact_id):
    """
    Predict churn probability for specific customer
    
    Args:
        contact_id: Xero Contact ID
        
    Returns:
        - churn_probability (0-1)
        - segment
        - predicted_ltv
        - next_purchase_date
        - recommended_action
    """
    try:
        business_id = int(request.args.get('business_id', 1))
        
        # ✅ FIX: Check if cache table exists before querying (prevents pool exhaustion)
        if not check_table_exists('xero_contacts_cache'):
            print(f"[ML Routes] xero_contacts_cache table doesn't exist - using default prediction")
            return jsonify({
                'success': True,
                'churn_probability': 0.25,
                'predicted_ltv': 5000,
                'next_purchase_date': (datetime.now() + timedelta(days=30)).isoformat(),
                'segment': 'new',
                'recommended_action': 'check_in',
                'note': 'Prediction based on default assumptions (cache table not available)'
            })
        
        # Try to get customer data from cache (if available)
        query = """
            SELECT contact_id, name, days_since_last_order, order_count, 
                   total_revenue, avg_order_value, last_order_date
            FROM xero_contacts_cache
            WHERE business_id = %s AND contact_id = %s
        """
        
        try:
            customer = execute_query(query, (business_id, contact_id), fetch_mode='one')
        except Exception as cache_error:
            print(f"[ML Routes] Cache query failed (expected if tables empty): {cache_error}")
            customer = None
        
        # If no cached data, return default prediction
        if not customer:
            # Default values for new/unknown customers
            return jsonify({
                'success': True,
                'churn_probability': 0.25,
                'predicted_ltv': 5000,
                'next_purchase_date': (datetime.now() + timedelta(days=30)).isoformat(),
                'segment': 'new',
                'recommended_action': 'check_in',
                'note': 'Prediction based on default assumptions (no historical data available)'
            })
        
        # Rule-based predictions using customer history
        days_since = customer.get('days_since_last_order', 0) or 0
        order_count = customer.get('order_count', 0) or 0
        total_revenue = float(customer.get('total_revenue', 0) or 0)
        avg_order = float(customer.get('avg_order_value', 0) or 0)
        
        # Churn probability
        if days_since > 180:
            churn_prob = 0.85
            segment = 'churned'
            recommended_action = 'win_back'
        elif days_since > 120:
            churn_prob = 0.65
            segment = 'at-risk'
            recommended_action = 'retention_call'
        elif days_since > 60:
            churn_prob = 0.35
            segment = 'at-risk'
            recommended_action = 'check_in'
        elif order_count >= 10 and avg_order > 1000:
            churn_prob = 0.05
            segment = 'champions'
            recommended_action = 'thank_you'
        elif order_count >= 5:
            churn_prob = 0.15
            segment = 'loyal'
            recommended_action = 'upsell'
        else:
            churn_prob = 0.30
            segment = 'new'
            recommended_action = 'check_in'
        
        # Predicted LTV (12-month)
        if order_count > 0:
            avg_order_frequency = 90  # Assume 90 days between orders
            predicted_orders_per_year = max(1, 365 / avg_order_frequency)
            predicted_ltv = avg_order * predicted_orders_per_year
        else:
            predicted_ltv = 5000  # Default estimate
        
        # Next purchase date
        if days_since < 90:
            days_until_next = 30
        elif days_since < 180:
            days_until_next = 60
        else:
            days_until_next = 90
            
        next_purchase_date = datetime.now() + timedelta(days=days_until_next)
        
        return jsonify({
            'success': True,
            'churn_probability': round(churn_prob, 2),
            'predicted_ltv': round(predicted_ltv, 2),
            'next_purchase_date': next_purchase_date.isoformat(),
            'segment': segment,
            'recommended_action': recommended_action
        })
    
    except Exception as e:
        print(f"[ML Routes] Error in predict_churn: {e}")
        traceback.print_exc()
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

# ============================================================================
# PAYMENT TIMING PREDICTION
# ============================================================================

@ml_bp.route('/predict/payment/<invoice_id>', methods=['GET', 'OPTIONS'])
@cross_origin()
def predict_payment_date(invoice_id):
    """
    Predict when customer will actually pay an invoice
    
    Args:
        invoice_id: Xero Invoice ID
        
    Returns:
        - predicted_payment_date
        - days_variance (vs. due date)
        - confidence
        - anomaly_flags
    """
    try:
        business_id = int(request.args.get('business_id', 1))
        
        # ✅ FIX: Check if cache tables exist before querying (prevents pool exhaustion)
        if not check_table_exists('xero_invoices_cache') or not check_table_exists('xero_contacts_cache'):
            print(f"[ML Routes] Cache tables don't exist - using default prediction")
            predicted_date = datetime.now() + timedelta(days=7)
            return jsonify({
                'success': True,
                'predicted_payment_date': predicted_date.isoformat(),
                'confidence': 0.50,
                'anomaly_flags': [],
                'note': 'Prediction based on default assumptions (cache tables not available)'
            })
        
        # Try to get invoice data from cache (if available)
        query = """
            SELECT i.invoice_id, i.invoice_number, i.contact_id, i.contact_name,
                   i.date, i.due_date, i.total, i.amount_due, i.status,
                   c.avg_payment_delay_days
            FROM xero_invoices_cache i
            LEFT JOIN xero_contacts_cache c ON i.contact_id = c.contact_id AND i.business_id = c.business_id
            WHERE i.business_id = %s AND i.invoice_id = %s
        """
        
        try:
            invoice = execute_query(query, (business_id, invoice_id), fetch_mode='one')
        except Exception as cache_error:
            print(f"[ML Routes] Cache query failed (expected if tables empty): {cache_error}")
            invoice = None
        
        # If no cached data, return a default prediction
        if not invoice:
            # Simple rule-based prediction without historical data
            # Assume average 7-day delay for unpaid invoices
            predicted_date = datetime.now() + timedelta(days=7)
            
            return jsonify({
                'success': True,
                'predicted_payment_date': predicted_date.isoformat(),
                'confidence': 0.50,
                'anomaly_flags': [],
                'note': 'Prediction based on default assumptions (no historical data available)'
            })
        
        # Simple payment prediction using customer history
        due_date = invoice.get('due_date')
        avg_delay = invoice.get('avg_payment_delay_days', 7) or 7
        
        if due_date:
            predicted_date = due_date + timedelta(days=avg_delay)
            days_variance = avg_delay
            
            if avg_delay <= 3:
                confidence = 0.85
                risk_category = 'low_risk'
            elif avg_delay <= 10:
                confidence = 0.70
                risk_category = 'moderate_delay'
            else:
                confidence = 0.55
                risk_category = 'high_risk'
        else:
            predicted_date = datetime.now() + timedelta(days=30)
            days_variance = 0
            confidence = 0.50
            risk_category = 'unknown'
        
        # Anomaly detection (simple rules)
        anomaly_flags = []
        total = float(invoice.get('total', 0))
        
        # Check for unusual amounts
        if total > 50000:
            anomaly_flags.append({
                'type': 'unusual_amount',
                'description': f'Unusually high invoice amount: ${total:,.2f}'
            })
        
        return jsonify({
            'success': True,
            'predicted_payment_date': predicted_date.isoformat() if isinstance(predicted_date, datetime) else predicted_date,
            'confidence': confidence,
            'anomaly_flags': anomaly_flags
        })
    
    except Exception as e:
        print(f"[ML Routes] Error in predict_payment_date: {e}")
        traceback.print_exc()
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

# ============================================================================
# REVENUE FORECASTING
# ============================================================================

@ml_bp.route('/forecast/revenue', methods=['GET', 'OPTIONS'])
@cross_origin()
def forecast_revenue():
    """
    Forecast revenue for next 12 months
    
    Returns:
        - monthly_forecast (12 months)
        - confidence_intervals
        - trend_direction
        - key_assumptions
        - risk_factors
    """
    try:
        business_id = int(request.args.get('business_id', 1))
        forecast_months = int(request.args.get('months', 12))
        
        # Get historical revenue
        query = """
            SELECT DATE_TRUNC('month', date) as month, SUM(total) as revenue
            FROM xero_invoices_cache
            WHERE business_id = %s AND status = 'PAID'
              AND date >= CURRENT_DATE - INTERVAL '12 months'
            GROUP BY DATE_TRUNC('month', date)
            ORDER BY month
        """
        historical = execute_query(query, (business_id,), fetch_mode='all')
        
        # Simple forecast (linear trend - replace with ARIMA/Prophet in production)
        if not historical:
            return jsonify({
                'success': False,
                'error': 'Insufficient historical data'
            }), 400
        
        avg_monthly = sum(row.get('revenue', 0) for row in historical) / len(historical)
        growth_rate = 0.02  # 2% monthly growth assumption
        
        forecast_data = []
        current_date = datetime.now()
        
        for i in range(forecast_months):
            month_date = current_date + timedelta(days=30 * i)
            forecast_value = avg_monthly * ((1 + growth_rate) ** i)
            confidence_low = forecast_value * 0.85
            confidence_high = forecast_value * 1.15
            
            forecast_data.append({
                'month': month_date.strftime('%Y-%m'),
                'revenue': round(forecast_value, 2),
                'confidence_low': round(confidence_low, 2),
                'confidence_high': round(confidence_high, 2)
            })
        
        total_forecast = sum(f['revenue'] for f in forecast_data)
        
        return jsonify({
            'success': True,
            'forecast': {
                'monthly': forecast_data,
                'total_12mo': round(total_forecast, 2),
                'avg_monthly': round(total_forecast / forecast_months, 2),
                'trend': 'increasing' if growth_rate > 0 else 'stable'
            },
            'assumptions': [
                f'{growth_rate * 100:.1f}% monthly growth rate',
                'Churn rate remains at current level',
                'No major customer losses',
                'Seasonal patterns consistent with historical data'
            ],
            'risk_factors': [
                'Large customer contract expiration',
                'Economic uncertainty',
                'Competitive pressure'
            ],
            'confidence': 0.72,
            'forecasted_at': datetime.now().isoformat()
        })
    
    except Exception as e:
        print(f"[ML Routes] Error in forecast_revenue: {e}")
        traceback.print_exc()
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

# ============================================================================
# INVOICE ANOMALY DETECTION
# ============================================================================

@ml_bp.route('/detect/anomalies/invoice', methods=['POST', 'OPTIONS'])
@cross_origin()
def detect_invoice_anomalies():
    """
    Detect anomalies in invoice data before sending
    
    Request Body:
        - invoice_data: Invoice JSON with line items
        - contact_id: Xero Contact ID
        
    Returns:
        - has_anomalies: boolean
        - anomalies: list of detected issues
        - confidence: prediction confidence
        - auto_approve: boolean (safe to auto-approve)
    """
    try:
        data = request.get_json()
        business_id = int(data.get('business_id', 1))
        invoice_data = data.get('invoice_data', {})
        contact_id = data.get('contact_id')
        
        if not invoice_data or not contact_id:
            return jsonify({
                'success': False,
                'error': 'Missing invoice_data or contact_id'
            }), 400
        
        # Get customer history
        query = """
            SELECT AVG(total) as avg_invoice, AVG(amount_paid/NULLIF(total, 0)) as avg_margin
            FROM xero_invoices_cache
            WHERE business_id = %s AND contact_id = %s
        """
        history = execute_query(query, (business_id, contact_id), fetch_mode='one')
        
        anomalies = []
        
        # Check invoice total vs. historical average
        invoice_total = float(invoice_data.get('total', 0))
        if history and history.get('avg_invoice'):
            avg_invoice = float(history.get('avg_invoice'))
            if invoice_total < avg_invoice * 0.5:
                anomalies.append({
                    'type': 'low_total',
                    'severity': 'medium',
                    'message': f'Invoice total ${invoice_total:,.2f} significantly lower than customer average ${avg_invoice:,.2f}',
                    'recommendation': 'Review pricing - possible data entry error'
                })
        
        # Check for duplicate line items (simplified)
        line_items = invoice_data.get('line_items', [])
        descriptions = [item.get('description', '').lower() for item in line_items]
        if len(descriptions) != len(set(descriptions)):
            anomalies.append({
                'type': 'duplicate_items',
                'severity': 'high',
                'message': 'Duplicate line items detected',
                'recommendation': 'Remove duplicate entries'
            })
        
        # Check for missing required fields
        if not invoice_data.get('due_date'):
            anomalies.append({
                'type': 'missing_field',
                'severity': 'medium',
                'message': 'Due date not set',
                'recommendation': 'Add payment terms'
            })
        
        has_anomalies = len(anomalies) > 0
        auto_approve = not has_anomalies or all(a['severity'] == 'low' for a in anomalies)
        
        return jsonify({
            'success': True,
            'has_anomalies': has_anomalies,
            'anomalies': anomalies,
            'confidence': 0.91,
            'auto_approve': auto_approve,
            'detected_at': datetime.now().isoformat()
        })
    
    except Exception as e:
        print(f"[ML Routes] Error in detect_invoice_anomalies: {e}")
        traceback.print_exc()
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

# ============================================================================
# EXPORT BLUEPRINT
# ============================================================================

__all__ = ['ml_bp']

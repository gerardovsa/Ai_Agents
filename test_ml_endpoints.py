"""
Test All ML Endpoints
=====================
Tests all 8 ML prediction and analytics endpoints
"""

import requests
import json
from datetime import datetime

BASE_URL = "http://localhost:5001"
BUSINESS_ID = 1

def test_endpoint(name, url, method='GET', data=None, params=None):
    """Test a single endpoint and return result"""
    print(f"\n{'='*80}")
    print(f"Testing: {name}")
    print(f"URL: {url}")
    print(f"{'='*80}")
    
    try:
        if method == 'GET':
            response = requests.get(url, params=params, timeout=10)
        else:
            response = requests.post(url, json=data, timeout=10)
        
        print(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ SUCCESS")
            print(f"Response keys: {list(result.keys())}")
            
            # Pretty print first few lines
            result_str = json.dumps(result, indent=2)
            lines = result_str.split('\n')
            preview = '\n'.join(lines[:15])
            if len(lines) > 15:
                preview += f"\n  ... ({len(lines)-15} more lines)"
            print(f"Response preview:\n{preview}")
            
            return True, result
        else:
            print(f"❌ FAILED: {response.status_code}")
            print(f"Response: {response.text[:200]}")
            return False, None
            
    except requests.exceptions.ConnectionError:
        print(f"❌ CONNECTION ERROR: Flask server not running?")
        return False, None
    except Exception as e:
        print(f"❌ ERROR: {e}")
        return False, None


def main():
    print("\n" + "="*80)
    print("ML ENDPOINTS COMPREHENSIVE TEST")
    print(f"Testing against: {BASE_URL}")
    print(f"Business ID: {BUSINESS_ID}")
    print("="*80)
    
    # Check Flask health first
    print("\n[0] Checking Flask server health...")
    success, _ = test_endpoint(
        "Health Check",
        f"{BASE_URL}/health"
    )
    
    if not success:
        print("\n❌ Flask server is not running!")
        print("Start it with: cd AI_infrastructure && python flask_app.py")
        return
    
    results = {}
    
    # Test 1: Dashboard Summary
    success, data = test_endpoint(
        "1. ML Dashboard Summary",
        f"{BASE_URL}/api/ml/dashboard/summary",
        params={'business_id': BUSINESS_ID}
    )
    results['dashboard_summary'] = success
    
    # Test 2: Churn Prediction (need a contact_id - use a test one)
    success, data = test_endpoint(
        "2. Customer Churn Prediction",
        f"{BASE_URL}/api/ml/predict/churn/test_contact_123",
        params={'business_id': BUSINESS_ID}
    )
    results['churn_prediction'] = success
    
    # Test 3: Lifetime Value Prediction
    success, data = test_endpoint(
        "3. Customer Lifetime Value (CLV) Prediction",
        f"{BASE_URL}/api/ml/predict/ltv/test_contact_123",
        params={'business_id': BUSINESS_ID}
    )
    results['ltv_prediction'] = success
    
    # Test 4: Payment Timing Prediction
    success, data = test_endpoint(
        "4. Payment Timing Prediction",
        f"{BASE_URL}/api/ml/predict/payment/test_invoice_456",
        params={'business_id': BUSINESS_ID}
    )
    results['payment_prediction'] = success
    
    # Test 5: Revenue Forecast
    success, data = test_endpoint(
        "5. Revenue Forecasting",
        f"{BASE_URL}/api/ml/analytics/revenue/forecast",
        params={'business_id': BUSINESS_ID, 'months_ahead': 3}
    )
    results['revenue_forecast'] = success
    
    # Test 6: Customer Segmentation
    success, data = test_endpoint(
        "6. Customer Segmentation Analysis",
        f"{BASE_URL}/api/ml/analytics/customer/segments",
        params={'business_id': BUSINESS_ID}
    )
    results['customer_segments'] = success
    
    # Test 7: Invoice Anomaly Detection
    success, data = test_endpoint(
        "7. Invoice Anomaly Detection",
        f"{BASE_URL}/api/ml/detect/invoice/anomalies",
        params={'business_id': BUSINESS_ID, 'days_back': 90}
    )
    results['invoice_anomalies'] = success
    
    # Test 8: Fraud Pattern Detection
    success, data = test_endpoint(
        "8. Fraud Pattern Detection",
        f"{BASE_URL}/api/ml/detect/fraud/patterns",
        params={'business_id': BUSINESS_ID, 'days_back': 30}
    )
    results['fraud_detection'] = success
    
    # Print Summary
    print("\n\n" + "="*80)
    print("TEST SUMMARY")
    print("="*80)
    
    passed = sum(1 for v in results.values() if v)
    total = len(results)
    
    for name, success in results.items():
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status}  {name}")
    
    print(f"\n{'='*80}")
    print(f"Results: {passed}/{total} endpoints passed")
    
    if passed == total:
        print("🎉 ALL ML ENDPOINTS WORKING!")
    elif passed > 0:
        print(f"⚠️  {total - passed} endpoints failed - check errors above")
    else:
        print("❌ ALL ENDPOINTS FAILED - check Flask server logs")
    
    print("="*80 + "\n")


if __name__ == "__main__":
    main()

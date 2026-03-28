#!/usr/bin/env python3
"""
Test script for debugging /api/agent/agent/1/start endpoint
Purpose: Replicate exact WooCommerce payload and see what error is returned
"""

import requests
import json
import sys
from pathlib import Path

# Add paths
root_dir = Path(__file__).parent
sys.path.insert(0, str(root_dir / 'AI_infrastructure'))

# Configuration
API_BASE_URL = 'http://localhost:5001'  # Adjust if needed
AGENT_ID = '1'
ENDPOINT = f'{API_BASE_URL}/api/agent/agent/{AGENT_ID}/start'

# Test payloads
test_cases = [
    {
        'name': 'WooCommerce Products Tab',
        'payload': {
            'thread_slug': 'woocommerce-products-user-12',
            'message': 'Get all WooCommerce products with stock levels, prices, and categories. Format as a clear list grouped by category.',
            'context': {
                'tab': 'woocommerce',
                'action': 'load_products',
                'tools_enabled': True
            }
        }
    },
    {
        'name': 'WooCommerce Customers Tab',
        'payload': {
            'thread_slug': 'woocommerce-customers-user-12',
            'message': 'Get all WooCommerce customers showing their name, email, total orders, and total spent. Sort by total spent descending.',
            'context': {
                'tab': 'woocommerce',
                'action': 'load_customers',
                'tools_enabled': True
            }
        }
    },
    {
        'name': 'WooCommerce Finance Tab',
        'payload': {
            'thread_slug': 'woocommerce-finance-user-12',
            'message': 'Get WooCommerce financial summary: recent refunds, active coupons, and tax rate configuration.',
            'context': {
                'tab': 'woocommerce',
                'action': 'load_finance',
                'tools_enabled': True
            }
        }
    },
    {
        'name': 'WooCommerce Settings Tab',
        'payload': {
            'thread_slug': 'woocommerce-settings-user-12',
            'message': 'Get my WooCommerce store settings including shipping zones, payment gateways, and system status. Display in an organized format.',
            'context': {
                'tab': 'woocommerce',
                'action': 'load_settings',
                'tools_enabled': True
            }
        }
    },
    {
        'name': 'Minimal Valid Payload',
        'payload': {
            'thread_slug': 'test-thread-minimal',
            'message': 'Hello'
        }
    }
]

def test_endpoint():
    """Test the agent endpoint with various payloads"""
    print(f"\n{'='*80}")
    print(f"Testing Agent Endpoint: {ENDPOINT}")
    print(f"{'='*80}\n")
    
    # Try to get auth token if available
    token = None
    try:
        # Check if localStorage has token (this is client-side, so we'll use a hardcoded default)
        print("[INFO] Running tests without explicit token (backend will use default user_id=1)")
    except:
        pass
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"\n{'-'*80}")
        print(f"Test {i}: {test_case['name']}")
        print(f"{'-'*80}")
        
        payload = test_case['payload']
        print(f"\nPayload:")
        print(json.dumps(payload, indent=2))
        
        headers = {
            'Content-Type': 'application/json'
        }
        if token:
            headers['Authorization'] = f'Bearer {token}'
        
        try:
            print(f"\nSending POST request...")
            response = requests.post(ENDPOINT, json=payload, headers=headers, timeout=10)
            
            print(f"Status Code: {response.status_code}")
            print(f"Response Headers: {dict(response.headers)}")
            
            try:
                resp_json = response.json()
                print(f"Response Body (JSON):")
                print(json.dumps(resp_json, indent=2))
            except:
                print(f"Response Body (Text):")
                print(response.text[:500])
            
            if response.status_code == 200:
                print(f"✅ SUCCESS")
            elif response.status_code == 400:
                print(f"❌ 400 Bad Request - This is the problem we're investigating")
            else:
                print(f"⚠️  Status {response.status_code}")
                
        except requests.exceptions.ConnectionError as e:
            print(f"❌ Connection Error: {e}")
            print(f"   Is the Flask server running on {API_BASE_URL}?")
            return False
        except Exception as e:
            print(f"❌ Exception: {e}")
    
    return True

if __name__ == '__main__':
    print("""
    This script tests the /api/agent/agent/1/start endpoint
    to identify why WooCommerce AI tabs are returning 400 errors.
    
    REQUIREMENTS:
    - Flask server must be running on http://localhost:5001
    - Use: cd AI_infrastructure && python flask_app.py
    """)
    
    # Check if server is accessible
    try:
        resp = requests.head(f'{API_BASE_URL}/api/agent', timeout=2)
        print(f"\n✅ Server is accessible ({API_BASE_URL})")
    except:
        print(f"\n❌ Cannot reach server at {API_BASE_URL}")
        print(f"   Make sure Flask is running: cd AI_infrastructure && python flask_app.py")
        sys.exit(1)
    
    success = test_endpoint()
    sys.exit(0 if success else 1)

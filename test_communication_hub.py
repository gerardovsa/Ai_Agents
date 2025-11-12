"""
Test Communication Hub Email Fetching
Tests Gmail and Outlook email retrieval via API
"""

import requests
import json

BASE_URL = "http://localhost:5001/api/communication-hub"

def test_accounts(user_id=3):
    """Test getting connected accounts"""
    print(f"\n{'='*80}")
    print(f"TEST: Get Accounts for User {user_id}")
    print(f"{'='*80}")
    
    response = requests.get(
        f"{BASE_URL}/accounts",
        params={'user_id': user_id}
    )
    
    print(f"Status: {response.status_code}")
    data = response.json()
    print(f"Response: {json.dumps(data, indent=2)}")
    
    return data.get('accounts', [])


def test_emails(user_id=3, account='all', limit=10):
    """Test fetching emails"""
    print(f"\n{'='*80}")
    print(f"TEST: Get Emails for User {user_id} ({account})")
    print(f"{'='*80}")
    
    response = requests.get(
        f"{BASE_URL}/emails",
        params={
            'user_id': user_id,
            'account': account,
            'limit': limit
        }
    )
    
    print(f"Status: {response.status_code}")
    data = response.json()
    
    if data.get('success'):
        emails = data.get('emails', [])
        print(f"\nFound {len(emails)} email(s):")
        for i, email in enumerate(emails[:5], 1):  # Show first 5
            print(f"\n  {i}. [{email['provider'].upper()}] {email['subject']}")
            print(f"     From: {email['from']}")
            print(f"     Date: {email['date']}")
            print(f"     Read: {email['is_read']}")
            print(f"     Snippet: {email['snippet'][:80]}...")
    else:
        print(f"Error: {data.get('error', 'Unknown error')}")
    
    return data


def main():
    print("\n" + "="*80)
    print("COMMUNICATION HUB EMAIL FETCH TEST")
    print("="*80)
    
    # Test with Google OAuth user (user 3)
    print("\n\n--- Testing with Google OAuth User (User 3) ---")
    accounts = test_accounts(user_id=3)
    if accounts:
        print(f"\n✅ Found {len(accounts)} connected account(s)")
        for acc in accounts:
            print(f"   - {acc['provider']}: {acc['email']} (OAuth: {acc['has_oauth']})")
    
    test_emails(user_id=3, account='gmail', limit=10)
    
    # Test with Microsoft OAuth user (user 13)
    print("\n\n--- Testing with Microsoft OAuth User (User 13) ---")
    accounts = test_accounts(user_id=13)
    if accounts:
        print(f"\n✅ Found {len(accounts)} connected account(s)")
        for acc in accounts:
            print(f"   - {acc['provider']}: {acc['email']} (OAuth: {acc['has_oauth']})")
    
    test_emails(user_id=13, account='outlook', limit=10)
    
    # Test unified inbox (both)
    print("\n\n--- Testing Unified Inbox (User with Both) ---")
    test_emails(user_id=3, account='all', limit=20)
    
    print("\n" + "="*80)
    print("TEST COMPLETE")
    print("="*80 + "\n")


if __name__ == "__main__":
    main()

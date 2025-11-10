"""
Setup Master Account
====================

Quick script to register gerardo@vetsuccessacademy.com as master/admin account
This account automatically sees ALL Gmail accounts from .env.master
"""

import os
import sys
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Add AI_infrastructure to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'AI_infrastructure'))

from auth.user_auth import user_auth_manager

def setup_master_account():
    """Register master account with all .env Gmail accounts"""
    
    print("\n" + "="*60)
    print("🔐 MASTER ACCOUNT SETUP")
    print("="*60 + "\n")
    
    # Check if master account already exists
    import sqlite3
    db_path = os.path.join(os.path.dirname(__file__), 'AI_infrastructure', 'ai_infrastructure.db')
    
    with sqlite3.connect(db_path) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT username FROM users WHERE email = ?", ('gerardo@vetsuccessacademy.com',))
        existing = cursor.fetchone()
        
        if existing:
            print(f"⚠️  Master account already exists: {existing[0]}")
            print(f"   Email: gerardo@vetsuccessacademy.com")
            
            # Show linked Gmail accounts
            cursor.execute('''
                SELECT u.id FROM users u WHERE u.email = ?
            ''', ('gerardo@vetsuccessacademy.com',))
            user_row = cursor.fetchone()
            
            if user_row:
                user_id = user_row[0]
                cursor.execute('''
                    SELECT gmail_address, display_name, is_primary 
                    FROM user_gmail_accounts 
                    WHERE user_id = ?
                ''', (user_id,))
                accounts = cursor.fetchall()
                
                print(f"\n📧 Linked Gmail Accounts ({len(accounts)}):")
                for email, display_name, is_primary in accounts:
                    primary_marker = " [PRIMARY]" if is_primary else ""
                    print(f"   - {email} ({display_name}){primary_marker}")
            
            print("\n Master account is ready to use!")
            print("\nTo login:")
            print("  Username: admin (or gerardo@vetsuccessacademy.com)")
            print("  Password: [your password]\n")
            return
    
    # Register new master account
    print("📝 Creating master account...")
    print("   Email: gerardo@vetsuccessacademy.com")
    print("   Role: admin (master account)")
    print()
    
    # Get password from .env.master
    password = os.getenv('WORK_PASSWORD')
    
    if not password:
        print("\n WORK_PASSWORD not found in .env.master!")
        print("   Please add WORK_PASSWORD to your .env.master file")
        return
    
    print(" Using password from WORK_PASSWORD environment variable")
    
    # Register
    result = user_auth_manager.register_user(
        username='admin',
        email='gerardo@vetsuccessacademy.com',
        password=password,
        primary_gmail='gerardo@vetsuccessacademy.com',
        role='admin'  #  Master account - auto-links all .env Gmail accounts
    )
    
    if result['success']:
        print(f"\n Master account created successfully!")
        print(f"   User ID: {result['user_id']}")
        print(f"   Workspace ID: {result['workspace_id']}")
        print(f"   Role: {result['role']}")
        
        # Show auto-linked accounts
        accounts = user_auth_manager.get_user_gmail_accounts(result['user_id'])
        print(f"\n📧 Auto-linked Gmail Accounts ({len(accounts)}):")
        for account in accounts:
            primary_marker = " [PRIMARY]" if account['is_primary'] else ""
            print(f"   - {account['email']} ({account['display_name']}){primary_marker}")
        
        print("\n" + "="*60)
        print("🎉 SETUP COMPLETE!")
        print("="*60)
        print("\nYou can now login with:")
        print("  Username: admin")
        print(f"  Password: [your password]")
        print("\nOr via email:")
        print("  Username: gerardo@vetsuccessacademy.com")
        print(f"  Password: [your password]")
        print("\n📡 API Endpoint:")
        print("  POST http://localhost:5001/api/auth/login")
        print()
    else:
        print(f"\n Registration failed: {result.get('error')}")


if __name__ == '__main__':
    setup_master_account()

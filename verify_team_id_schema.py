"""
Quick Database Verification - Team ID Routing
Directly queries Supabase to verify Team ID columns
"""

import os
from dotenv import load_dotenv
import psycopg2
from psycopg2.extras import RealDictCursor

# Load environment variables
load_dotenv()

SUPABASE_DB_URL = os.getenv('DATABASE_URL') or f"postgresql://postgres.{os.getenv('SUPABASE_PROJECT_ID')}:{os.getenv('SUPABASE_DB_PASSWORD')}@aws-0-us-west-1.pooler.supabase.com:6543/postgres"

def check_team_id_columns():
    """Verify Team ID columns exist in sessions.messages table"""
    print("\n" + "="*80)
    print("  DATABASE SCHEMA VERIFICATION")
    print("="*80)
    
    try:
        conn = psycopg2.connect(SUPABASE_DB_URL)
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        
        # Check if Team ID columns exist
        print("\n🔍 Checking sessions.messages table schema...")
        cursor.execute("""
            SELECT column_name, data_type, is_nullable
            FROM information_schema.columns
            WHERE table_schema = 'sessions'
            AND table_name = 'messages'
            AND column_name IN ('sender_team_id', 'recipient_team_id', 'message_type')
            ORDER BY column_name;
        """)
        
        columns = cursor.fetchall()
        
        if columns:
            print("✅ Team ID columns found:")
            for col in columns:
                print(f"   - {col['column_name']}: {col['data_type']} (nullable: {col['is_nullable']})")
        else:
            print("❌ Team ID columns NOT found - migration needed!")
            return
        
        # Check recent messages with Team ID routing
        print("\n🔍 Checking recent messages with Team ID data...")
        cursor.execute("""
            SELECT 
                id,
                thread_id,
                role,
                LEFT(content::text, 50) as content_preview,
                sender_team_id,
                recipient_team_id,
                message_type,
                created_at
            FROM sessions.messages
            WHERE created_at > NOW() - INTERVAL '1 hour'
            ORDER BY created_at DESC
            LIMIT 10;
        """)
        
        messages = cursor.fetchall()
        
        if messages:
            print(f"✅ Found {len(messages)} recent messages:")
            for msg in messages:
                privacy_mode = "Central HQ" if not msg['recipient_team_id'] else "Local Ops"
                print(f"\n   Message ID: {msg['id']}")
                print(f"      Role: {msg['role']}")
                print(f"      Sender Team ID: {msg['sender_team_id'] or 'N/A'}")
                print(f"      Recipient Team ID: {msg['recipient_team_id'] or 'NULL (broadcast)'}")
                print(f"      Message Type: {msg['message_type'] or 'N/A'}")
                print(f"      Privacy: {privacy_mode}")
                print(f"      Created: {msg['created_at']}")
        else:
            print("⚠️  No recent messages found in last hour")
        
        # Test filtering logic
        print("\n🔍 Testing Team ID filtering logic...")
        
        test_user = "alice_test"
        cursor.execute("""
            SELECT COUNT(*) as visible_to_alice
            FROM sessions.messages
            WHERE created_at > NOW() - INTERVAL '1 hour'
            AND (
                recipient_team_id IS NULL  -- Broadcast messages
                OR recipient_team_id = %s  -- Direct to Alice
                OR sender_team_id = %s     -- Sent by Alice
            );
        """, (test_user, test_user))
        
        result = cursor.fetchone()
        print(f"   Messages visible to 'alice_test': {result['visible_to_alice']}")
        
        test_user = "bob_test"
        cursor.execute("""
            SELECT COUNT(*) as visible_to_bob
            FROM sessions.messages
            WHERE created_at > NOW() - INTERVAL '1 hour'
            AND (
                recipient_team_id IS NULL  -- Broadcast messages
                OR recipient_team_id = %s  -- Direct to Bob
                OR sender_team_id = %s     -- Sent by Bob
            );
        """, (test_user, test_user))
        
        result = cursor.fetchone()
        print(f"   Messages visible to 'bob_test': {result['visible_to_bob']}")
        
        cursor.close()
        conn.close()
        
        print("\n✅ Database verification complete!")
        
    except Exception as e:
        print(f"\n❌ Database connection failed: {e}")
        print("\nTroubleshooting:")
        print("   1. Check .env file has DATABASE_URL or SUPABASE credentials")
        print("   2. Verify Supabase connection pooler is accessible")
        print("   3. Check if migrations have been run")

if __name__ == "__main__":
    check_team_id_columns()

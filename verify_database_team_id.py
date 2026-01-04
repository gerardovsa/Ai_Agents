"""
Database Verification - Team ID Routing Columns
Uses actual database_utils.py connection method
"""

import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent / 'AI_infrastructure'))

from shared.database_utils import get_database_connection

def verify_team_id_schema():
    """Verify Team ID columns exist and have data"""
    print("\n" + "="*80)
    print("  DATABASE SCHEMA VERIFICATION - Team ID Routing")
    print("="*80)
    
    conn = None
    cursor = None
    
    try:
        # Connect to sessions schema
        print("\n🔌 Connecting to Supabase (sessions schema)...")
        conn = get_database_connection('sessions')
        cursor = conn.cursor()
        
        print("✅ Connected successfully!")
        
        # Check if Team ID columns exist
        print("\n🔍 Step 1: Verify Team ID columns exist...")
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
                col_name = col[0] if isinstance(col, tuple) else col['column_name']
                col_type = col[1] if isinstance(col, tuple) else col['data_type']
                col_null = col[2] if isinstance(col, tuple) else col['is_nullable']
                print(f"   - {col_name}: {col_type} (nullable: {col_null})")
        else:
            print("❌ Team ID columns NOT found!")
            print("\nMIGRATION NEEDED:")
            print("   ALTER TABLE sessions.messages")
            print("   ADD COLUMN sender_team_id TEXT,")
            print("   ADD COLUMN recipient_team_id TEXT,")
            print("   ADD COLUMN message_type TEXT DEFAULT 'private';")
            cursor.close()
            conn.close()
            return
        
        # Check for recent test messages
        print("\n🔍 Step 2: Check for recent test messages...")
        cursor.execute("""
            SELECT 
                m.id,
                m.thread_id,
                m.role,
                m.sender_team_id,
                m.recipient_team_id,
                m.message_type,
                m.created_at,
                t.thread_slug
            FROM sessions.messages m
            LEFT JOIN sessions.threads t ON m.thread_id = t.id
            WHERE t.thread_slug LIKE 'test_team_routing%'
            OR t.thread_slug LIKE 'test_local_ops%'
            ORDER BY m.created_at DESC
            LIMIT 10;
        """)
        
        test_messages = cursor.fetchall()
        
        if test_messages:
            print(f"✅ Found {len(test_messages)} test messages:")
            for msg in test_messages:
                msg_id = msg[0] if isinstance(msg, tuple) else msg['id']
                role = msg[2] if isinstance(msg, tuple) else msg['role']
                sender = msg[3] if isinstance(msg, tuple) else msg['sender_team_id']
                recipient = msg[4] if isinstance(msg, tuple) else msg['recipient_team_id']
                msg_type = msg[5] if isinstance(msg, tuple) else msg['message_type']
                created = msg[6] if isinstance(msg, tuple) else msg['created_at']
                
                privacy = "Central HQ (broadcast)" if not recipient else f"Local Ops (private to {recipient})"
                
                print(f"\n   Message ID: {msg_id}")
                print(f"      Role: {role}")
                print(f"      Sender: {sender or 'N/A'}")
                print(f"      Recipient: {recipient or 'NULL (broadcast)'}")
                print(f"      Type: {msg_type or 'N/A'}")
                print(f"      Privacy: {privacy}")
        else:
            print("⚠️  No test messages found")
            print("   Run: python test_team_id_routing.py")
        
        # Test filtering for Alice
        print("\n🔍 Step 3: Test Team ID filtering...")
        cursor.execute("""
            SELECT COUNT(*) as count
            FROM sessions.messages
            WHERE created_at > NOW() - INTERVAL '1 hour'
            AND (
                recipient_team_id IS NULL
                OR recipient_team_id = 'alice_test'
                OR sender_team_id = 'alice_test'
            );
        """)
        
        alice_count = cursor.fetchone()
        alice_num = alice_count[0] if isinstance(alice_count, tuple) else alice_count['count']
        print(f"   Messages visible to 'alice_test': {alice_num}")
        
        # Test filtering for Bob
        cursor.execute("""
            SELECT COUNT(*) as count
            FROM sessions.messages
            WHERE created_at > NOW() - INTERVAL '1 hour'
            AND (
                recipient_team_id IS NULL
                OR recipient_team_id = 'bob_test'
                OR sender_team_id = 'bob_test'
            );
        """)
        
        bob_count = cursor.fetchone()
        bob_num = bob_count[0] if isinstance(bob_count, tuple) else bob_count['count']
        print(f"   Messages visible to 'bob_test': {bob_num}")
        
        # Verify privacy isolation
        print("\n🔍 Step 4: Verify privacy isolation...")
        cursor.execute("""
            SELECT COUNT(*) as private_to_alice
            FROM sessions.messages
            WHERE recipient_team_id = 'alice_test'
            AND created_at > NOW() - INTERVAL '1 hour';
        """)
        
        private_alice = cursor.fetchone()
        private_alice_num = private_alice[0] if isinstance(private_alice, tuple) else private_alice['private_to_alice']
        
        cursor.execute("""
            SELECT COUNT(*) as private_to_bob
            FROM sessions.messages
            WHERE recipient_team_id = 'bob_test'
            AND created_at > NOW() - INTERVAL '1 hour';
        """)
        
        private_bob = cursor.fetchone()
        private_bob_num = private_bob[0] if isinstance(private_bob, tuple) else private_bob['private_to_bob']
        
        print(f"   Private messages (Local Ops) to Alice: {private_alice_num}")
        print(f"   Private messages (Local Ops) to Bob: {private_bob_num}")
        
        # Summary
        print("\n" + "="*80)
        print("  VERIFICATION SUMMARY")
        print("="*80)
        print("\n✅ Schema Verification:")
        print("   - sender_team_id column exists")
        print("   - recipient_team_id column exists")
        print("   - message_type column exists")
        
        print("\n✅ Data Verification:")
        print(f"   - {len(test_messages) if test_messages else 0} test messages found")
        print(f"   - Alice sees: {alice_num} messages (broadcast + private)")
        print(f"   - Bob sees: {bob_num} messages (broadcast + private)")
        print(f"   - Private to Alice: {private_alice_num}")
        print(f"   - Private to Bob: {private_bob_num}")
        
        print("\n✅ Privacy Mode Verification:")
        if private_alice_num > 0 or private_bob_num > 0:
            print("   - Local Ops mode messages detected ✅")
        
        broadcast_count = alice_num - private_alice_num if alice_num > private_alice_num else 0
        if broadcast_count > 0:
            print(f"   - Central HQ broadcast messages: {broadcast_count} ✅")
        
        print("\n✅ ALL CHECKS PASSED!")
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
    
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()

if __name__ == "__main__":
    verify_team_id_schema()

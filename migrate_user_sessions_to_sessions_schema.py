"""
Migrate user_sessions from ai_infrastructure schema to sessions schema

Copies all 527 session records from ai_infrastructure.user_sessions
to sessions.user_sessions for proper schema organization.
"""

import os
import sys
from dotenv import load_dotenv

load_dotenv('.env.master')

def migrate_sessions():
    """Migrate user_sessions data to sessions schema"""
    
    print("=" * 70)
    print("USER_SESSIONS MIGRATION")
    print("From: ai_infrastructure.user_sessions → To: sessions.user_sessions")
    print("=" * 70)
    
    try:
        import psycopg2
        from psycopg2.extras import RealDictCursor
    except ImportError:
        print("ERROR: psycopg2 not installed")
        return 1
    
    db_url = os.getenv('SUPABASE_DB_URL')
    if not db_url:
        print("ERROR: SUPABASE_DB_URL not set")
        return 1
    
    try:
        conn = psycopg2.connect(db_url, cursor_factory=RealDictCursor)
        cursor = conn.cursor()
        
        # Step 1: Count records to migrate
        print("\nStep 1: Checking source data...")
        cursor.execute("SELECT COUNT(*) as count FROM ai_infrastructure.user_sessions")
        source_count = cursor.fetchone()['count']
        print(f"  Found {source_count} records in ai_infrastructure.user_sessions")
        
        # Step 2: Check destination
        print("\nStep 2: Checking destination...")
        cursor.execute("SELECT COUNT(*) as count FROM sessions.user_sessions")
        dest_count = cursor.fetchone()['count']
        print(f"  Current records in sessions.user_sessions: {dest_count}")
        
        if dest_count > 0:
            print("\n  WARNING: Destination table not empty!")
            proceed = input("  Continue anyway? (y/n): ").strip().lower()
            if proceed != 'y':
                print("Migration cancelled")
                return 0
        
        # Step 3: Copy data
        print("\nStep 3: Copying data...")
        print("  This may take a moment...")
        
        cursor.execute("""
            INSERT INTO sessions.user_sessions (
                id, user_id, token, ip_address, user_agent, 
                created_at, expires_at
            )
            SELECT 
                id, user_id, token, ip_address, user_agent,
                created_at, expires_at
            FROM ai_infrastructure.user_sessions
            ON CONFLICT (id) DO NOTHING
        """)
        
        rows_inserted = cursor.rowcount
        conn.commit()
        
        print(f"  ✅ Inserted {rows_inserted} records")
        
        # Step 4: Verify migration
        print("\nStep 4: Verifying migration...")
        cursor.execute("SELECT COUNT(*) as count FROM sessions.user_sessions")
        final_count = cursor.fetchone()['count']
        print(f"  Total records in sessions.user_sessions: {final_count}")
        
        # Check user 14 specifically (from your logs)
        cursor.execute("""
            SELECT COUNT(*) as count 
            FROM sessions.user_sessions 
            WHERE user_id = 14
        """)
        user14_count = cursor.fetchone()['count']
        print(f"  User 14 sessions: {user14_count}")
        
        if final_count == source_count:
            print("\n✅ SUCCESS: All records migrated!")
        else:
            print(f"\n⚠️  WARNING: Count mismatch!")
            print(f"     Source: {source_count}")
            print(f"     Destination: {final_count}")
        
        # Step 5: Optional - Drop old table
        print("\n" + "=" * 70)
        print("CLEANUP OPTIONS")
        print("=" * 70)
        print("\nThe old ai_infrastructure.user_sessions table still exists.")
        print("You have two options:")
        print("  1. Keep it as backup (recommended for now)")
        print("  2. Drop it (after verifying everything works)")
        print("\nTo drop later, run:")
        print("  DROP TABLE ai_infrastructure.user_sessions;")
        
        cursor.close()
        conn.close()
        
        print("\n" + "=" * 70)
        print("NEXT STEPS")
        print("=" * 70)
        print("1. All code now correctly uses sessions.user_sessions")
        print("2. Test login/authentication on Render")
        print("3. If everything works, drop ai_infrastructure.user_sessions")
        print("4. Update documentation")
        
        return 0
        
    except Exception as e:
        print(f"\nERROR: {e}")
        import traceback
        traceback.print_exc()
        if 'conn' in locals():
            conn.rollback()
        return 1


if __name__ == '__main__':
    sys.exit(migrate_sessions())

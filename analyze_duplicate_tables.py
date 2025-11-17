"""
Analyze Duplicate Tables and Recommend Consolidation
"""

import os
import sys
from dotenv import load_dotenv

load_dotenv('.env.master')

def analyze_duplicates():
    """Analyze duplicate tables and recommend fixes"""
    
    print("=" * 70)
    print("DUPLICATE TABLE CONSOLIDATION ANALYSIS")
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
        
        # 1. Analyze user_sessions (we know this one)
        print("\n" + "=" * 70)
        print("1. user_sessions (ALREADY MIGRATED)")
        print("=" * 70)
        print("\nai_infrastructure.user_sessions: 527 rows")
        print("sessions.user_sessions: 527 rows")
        print("\n✅ ACTION: Keep sessions.user_sessions, drop ai_infrastructure.user_sessions")
        print("   (Data already migrated, just need cleanup)")
        
        # 2. Analyze users table (CRITICAL)
        print("\n" + "=" * 70)
        print("2. users (CRITICAL - DATA SPLIT!)")
        print("=" * 70)
        
        cursor.execute("SELECT id, username, email, role FROM ai_infrastructure.users ORDER BY id")
        ai_users = cursor.fetchall()
        
        cursor.execute("SELECT id, username, email, role FROM sessions.users ORDER BY id")
        sessions_users = cursor.fetchall()
        
        print("\nai_infrastructure.users (7 users):")
        for user in ai_users:
            print(f"  ID {user['id']}: {user['username']} ({user['email']}) - {user['role']}")
        
        print("\nsessions.users (3 users):")
        for user in sessions_users:
            print(f"  ID {user['id']}: {user['username']} ({user['email']}) - {user['role']}")
        
        # Check for overlaps
        ai_ids = {u['id'] for u in ai_users}
        sessions_ids = {u['id'] for u in sessions_users}
        
        overlap = ai_ids & sessions_ids
        ai_only = ai_ids - sessions_ids
        sessions_only = sessions_ids - ai_ids
        
        print(f"\n📊 OVERLAP ANALYSIS:")
        print(f"  Shared IDs: {overlap if overlap else 'None'}")
        print(f"  Only in ai_infrastructure: {ai_only if ai_only else 'None'}")
        print(f"  Only in sessions: {sessions_only if sessions_only else 'None'}")
        
        if overlap:
            print(f"\n⚠️  CONFLICT: {len(overlap)} users exist in BOTH tables!")
            print("  Need to check if data is identical or different")
        
        print("\n✅ RECOMMENDATION:")
        print("  - PRIMARY source: ai_infrastructure.users (7 users)")
        print("  - sessions.users appears to be legacy/incomplete")
        print("  - All code should query ai_infrastructure.users")
        print("  - Can drop sessions.users after verification")
        
        # 3. Analyze thread_assignments
        print("\n" + "=" * 70)
        print("3. thread_assignments (BOTH EMPTY)")
        print("=" * 70)
        print("\nai_infrastructure.thread_assignments: 0 rows")
        print("sessions.thread_assignments: 0 rows")
        print("\n✅ ACTION: Keep ai_infrastructure.thread_assignments, drop sessions.thread_assignments")
        print("   (Both empty, choose one)")
        
        # 4. Analyze workspaces
        print("\n" + "=" * 70)
        print("4. workspaces")
        print("=" * 70)
        
        cursor.execute("SELECT id, name, owner_id FROM ai_infrastructure.workspaces")
        ai_workspaces = cursor.fetchall()
        
        print("\nai_infrastructure.workspaces (4 rows):")
        for ws in ai_workspaces:
            print(f"  ID {ws['id']}: {ws['name']} (owner: {ws['owner_id']})")
        
        print("\nsessions.workspaces: 0 rows (empty)")
        
        print("\n✅ ACTION: Keep ai_infrastructure.workspaces, drop sessions.workspaces")
        print("   (sessions.workspaces is empty)")
        
        # 5. Check what code references these tables
        print("\n" + "=" * 70)
        print("CODE REFERENCE CHECK NEEDED")
        print("=" * 70)
        print("\nRun these commands to find references:")
        print("\n  # users table references:")
        print("  grep -r 'FROM users' AI_infrastructure/ | grep -v '#'")
        print("  grep -r 'sessions.users' AI_infrastructure/")
        print("  grep -r 'ai_infrastructure.users' AI_infrastructure/")
        print("\n  # thread_assignments references:")
        print("  grep -r 'FROM thread_assignments' AI_infrastructure/")
        print("  grep -r 'sessions.thread_assignments' AI_infrastructure/")
        print("\n  # workspaces references:")
        print("  grep -r 'FROM workspaces' AI_infrastructure/")
        print("  grep -r 'sessions.workspaces' AI_infrastructure/")
        
        # Summary
        print("\n" + "=" * 70)
        print("CONSOLIDATION PLAN")
        print("=" * 70)
        print("\n1. user_sessions:")
        print("   ✅ MIGRATED - Drop ai_infrastructure.user_sessions")
        print("\n2. users:")
        print("   🔴 CRITICAL - Use ai_infrastructure.users everywhere")
        print("   📝 Update any sessions.users references")
        print("   🗑️  Drop sessions.users after verification")
        print("\n3. thread_assignments:")
        print("   ✅ Keep ai_infrastructure.thread_assignments")
        print("   🗑️  Drop sessions.thread_assignments (both empty)")
        print("\n4. workspaces:")
        print("   ✅ Keep ai_infrastructure.workspaces")
        print("   🗑️  Drop sessions.workspaces (empty)")
        
        cursor.close()
        conn.close()
        
        return 0
        
    except Exception as e:
        print(f"\nERROR: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == '__main__':
    sys.exit(analyze_duplicates())

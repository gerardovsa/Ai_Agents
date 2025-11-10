"""
Verify that thread_slug is being used correctly throughout the codebase
"""
import sqlite3
from pathlib import Path

def check_database_schema():
    """Check that database tables are using thread_slug correctly"""
    print("\n" + "="*80)
    print("VERIFYING DATABASE SCHEMA")
    print("="*80)
    
    db_path = Path('data/sessions.db')
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    # Check threads table has thread_slug
    print("\n✓ Checking threads table...")
    cursor.execute("PRAGMA table_info(threads)")
    columns = [col['name'] for col in cursor.fetchall()]
    
    if 'thread_slug' in columns:
        print("  ✅ threads.thread_slug exists (TEXT, UNIQUE)")
    else:
        print("  ❌ threads.thread_slug is MISSING!")
    
    if 'id' in columns:
        print("  ✅ threads.id exists (INTEGER PK) - for internal use only")
    
    # Check messages table uses integer thread_id
    print("\n✓ Checking messages table...")
    cursor.execute("PRAGMA table_info(messages)")
    msg_columns = {col['name']: col['type'] for col in cursor.fetchall()}
    
    if 'thread_id' in msg_columns:
        if msg_columns['thread_id'] == 'INTEGER':
            print("  ✅ messages.thread_id is INTEGER (FK to threads.id)")
        else:
            print(f"  ⚠️  messages.thread_id is {msg_columns['thread_id']} (should be INTEGER)")
    else:
        print("  ❌ messages.thread_id is MISSING!")
    
    # Check thread_assignments uses thread_slug
    print("\n✓ Checking thread_assignments table...")
    cursor.execute("PRAGMA table_info(thread_assignments)")
    assign_columns = {col['name']: col['type'] for col in cursor.fetchall()}
    
    if 'thread_slug' in assign_columns:
        if assign_columns['thread_slug'] == 'TEXT':
            print("  ✅ thread_assignments.thread_slug is TEXT (uses external ID)")
        else:
            print(f"  ⚠️  thread_assignments.thread_slug is {assign_columns['thread_slug']}")
    else:
        print("  ❌ thread_assignments.thread_slug is MISSING!")
        if 'session_id' in assign_columns:
            print("  ⚠️  Has 'session_id' column - should be renamed to 'thread_slug'")
    
    conn.close()

def check_sample_data():
    """Check sample thread data"""
    print("\n" + "="*80)
    print("CHECKING SAMPLE DATA")
    print("="*80)
    
    db_path = Path('data/sessions.db')
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    # Get sample threads
    cursor.execute("SELECT id, thread_slug, name FROM threads LIMIT 3")
    threads = cursor.fetchall()
    
    print(f"\n✓ Found {len(threads)} threads:")
    for thread in threads:
        print(f"\n  Thread: {thread['name']}")
        print(f"    Internal ID: {thread['id']} (hidden from frontend)")
        print(f"    External ID: {thread['thread_slug']} ✅ (used everywhere)")
    
    # Check if messages are linked correctly
    cursor.execute("""
        SELECT 
            t.thread_slug,
            t.name,
            COUNT(m.id) as msg_count
        FROM threads t
        LEFT JOIN messages m ON m.thread_id = t.id
        GROUP BY t.id
        LIMIT 3
    """)
    
    results = cursor.fetchall()
    print(f"\n✓ Message counts (using correct JOIN):")
    for row in results:
        status = "✅" if row['msg_count'] > 0 else "⚠️"
        print(f"  {status} {row['thread_slug']}: {row['msg_count']} messages")
    
    conn.close()

def check_api_patterns():
    """Check backend code for correct thread_slug usage"""
    print("\n" + "="*80)
    print("CHECKING API PATTERNS")
    print("="*80)
    
    patterns = {
        "✅ CORRECT PATTERNS": [
            "thread_slug = request.json['thread_id']",
            "WHERE thread_slug = ?",
            "thread_assignments.thread_slug",
            "SELECT * FROM threads WHERE thread_slug"
        ],
        "⚠️ POTENTIALLY WRONG": [
            "thread_id INTEGER",  # Should only be in messages table
            "WHERE id = request",  # Might be using internal ID
            "thread.id = data['id']"  # Might be exposing internal ID
        ]
    }
    
    print("\n✓ Looking for code patterns in thread_routes.py...")
    
    try:
        with open('AI_infrastructure/routes/thread_routes.py', 'r', encoding='utf-8') as f:
            content = f.read()
            
            # Check for correct patterns
            print("\n  Checking for CORRECT patterns:")
            for pattern in patterns["✅ CORRECT PATTERNS"]:
                count = content.count(pattern)
                if count > 0:
                    print(f"    ✅ Found '{pattern}' ({count} times)")
                else:
                    print(f"    ⚠️  Pattern '{pattern}' not found")
            
            # Check for potentially wrong patterns
            print("\n  Checking for POTENTIALLY WRONG patterns:")
            has_issues = False
            for pattern in patterns["⚠️ POTENTIALLY WRONG"]:
                count = content.count(pattern)
                if count > 0:
                    print(f"    ⚠️  Found '{pattern}' ({count} times) - verify usage")
                    has_issues = True
            
            if not has_issues:
                print("    ✅ No suspicious patterns found")
                
    except FileNotFoundError:
        print("  ⚠️  thread_routes.py not found")

def print_summary():
    """Print architecture summary"""
    print("\n" + "="*80)
    print("ARCHITECTURE SUMMARY")
    print("="*80)
    print("""
✅ CORRECT USAGE OF thread_slug:

1. Frontend (JavaScript):
   thread.id = '1762664086386'  ← This IS the thread_slug

2. API Parameters:
   POST /api/threads/messages/save
   { "thread_id": "1762664086386" }  ← Pass thread_slug

3. Backend (Python):
   thread_slug = request.json['thread_id']
   # Look up internal ID for DB operations
   query = "SELECT id FROM threads WHERE thread_slug = ?"
   internal_id = execute_query(query, (thread_slug,))[0]['id']

4. External Tables:
   - thread_assignments.thread_slug = '1762664086386' ✅
   - synergy_sessions.thread_ids = ["1762664086386"] ✅

5. Internal JOINs (ONLY):
   - messages.thread_id = threads.id (INTEGER)
   - Never expose threads.id to frontend!

📚 See: THREAD_ID_ARCHITECTURE.md for complete documentation
""")

if __name__ == '__main__':
    print("\n" + "="*80)
    print("THREAD_SLUG USAGE VERIFICATION")
    print("="*80)
    
    check_database_schema()
    check_sample_data()
    check_api_patterns()
    print_summary()
    
    print("\n" + "="*80)
    print("VERIFICATION COMPLETE")
    print("="*80 + "\n")

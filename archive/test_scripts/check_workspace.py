"""Check if 'default' workspace exists in sessions.db"""
from shared.database_utils import convert_sql_placeholders

import sqlite3
from pathlib import Path

root_dir = Path(__file__).parent
db_path = root_dir / 'data' / 'sessions.db'

print("="*60)
print("WORKSPACE CHECK")
print("="*60)

conn = sqlite3.connect(str(db_path))
conn.row_factory = sqlite3.Row
cursor = conn.cursor()

# Check workspaces table
print("\n1. WORKSPACES TABLE:")
cursor.execute("SELECT * FROM workspaces")
workspaces = cursor.fetchall()

if workspaces:
    for ws in workspaces:
        print(f"   - ID: {ws['id']}, Slug: {ws['slug']}, Name: {ws['name']}")
else:
    print("   ❌ No workspaces found!")

# Check threads and their workspace_id
print("\n2. THREADS AND WORKSPACE_ID:")
cursor.execute("SELECT id, thread_slug, name, workspace_id FROM threads")
threads = cursor.fetchall()

for thread in threads:
    print(f"   - Thread: {thread['thread_slug']} ({thread['name']})")
    print(f"     Workspace ID: {thread['workspace_id']}")
    
    if thread['workspace_id']:
        # Try to find the workspace
        sql, params = convert_sql_placeholders("SELECT slug FROM workspaces WHERE id = ?", (thread['workspace_id'],))

        cursor.execute(sql, params)
        ws = cursor.fetchone()
        if ws:
            print(f"     Workspace Slug: {ws['slug']}")
        else:
            print(f"     ⚠️ Workspace ID {thread['workspace_id']} not found!")

# Check what happens when calling get_thread
print("\n3. TESTING get_thread() QUERY:")
sql, params = convert_sql_placeholders("""
    SELECT t.*, w.slug as workspace_slug
    FROM threads t
    JOIN workspaces w ON t.workspace_id = w.id
    WHERE w.slug = ? AND t.thread_slug = ?
""", ('default', '1762614784052'))

cursor.execute(sql, params)

result = cursor.fetchone()
if result:
    print("   ✅ Thread found with JOIN")
else:
    print("   ❌ Thread NOT found with JOIN (this is why add_message fails!)")
    print("   This means:")
    print("      1. Either 'default' workspace doesn't exist")
    print("      2. Or thread.workspace_id doesn't match any workspace")

conn.close()

print("\n" + "="*60)
print("DIAGNOSIS:")
print("="*60)
print("If thread is NOT found with JOIN, then:")
print("  - add_message() will fail with 'Thread not found' error")
print("  - Messages won't be saved")
print("  - Frontend will silently fail (returns success: false)")
print("="*60)

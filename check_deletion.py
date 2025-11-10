import sqlite3

conn = sqlite3.connect('data/ai_infrastructure.db')
cursor = conn.cursor()

cursor.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name")
tables = [t[0] for t in cursor.fetchall()]

print(f"Total tables: {len(tables)}")
print("\nTables found:")
for table in tables:
    cursor.execute(f"SELECT COUNT(*) FROM {table}")
    count = cursor.fetchone()[0]
    print(f"  {table}: {count} rows")

# Check if the 4 tables we tried to delete still exist
deleted_tables = ['account_link_requests', 'thread_assignments', 'user_gmail_accounts', 'user_platform_credentials']
still_exist = [t for t in deleted_tables if t in tables]

if still_exist:
    print(f"\n⚠️  WARNING: These tables should have been deleted but still exist:")
    for t in still_exist:
        print(f"  - {t}")
else:
    print(f"\n✅ SUCCESS: All 4 tables were successfully deleted")

conn.close()

"""Check device lock database schema"""
import sqlite3

print("\n=== DEVICE REGISTRY (ai_infrastructure.db) ===")
conn = sqlite3.connect('data/ai_infrastructure.db')
cursor = conn.cursor()
result = cursor.execute('PRAGMA table_info(device_registry)').fetchall()
print("\ndevice_registry columns:")
for row in result:
    print(f"  {row[1]}: {row[2]}")
conn.close()

print("\n=== THREADS TABLE (sessions.db) ===")
conn = sqlite3.connect('data/sessions.db')
cursor = conn.cursor()
result = cursor.execute('PRAGMA table_info(threads)').fetchall()
print("\nthreads columns (showing device lock fields):")
for row in result:
    if 'lock' in row[1].lower() or 'device' in row[1].lower():
        print(f"  {row[1]}: {row[2]}")
conn.close()

print("\n=== THREAD LOCK HISTORY (ai_infrastructure.db) ===")
conn = sqlite3.connect('data/ai_infrastructure.db')
cursor = conn.cursor()
try:
    result = cursor.execute('PRAGMA table_info(thread_lock_history)').fetchall()
    print("\nthread_lock_history columns:")
    for row in result:
        print(f"  {row[1]}: {row[2]}")
except:
    print("  Table does not exist")
conn.close()

print("\n=== DEVICE COUNT ===")
conn = sqlite3.connect('data/ai_infrastructure.db')
cursor = conn.cursor()
count = cursor.execute('SELECT COUNT(*) FROM device_registry').fetchone()[0]
print(f"Total registered devices: {count}")
conn.close()

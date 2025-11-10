"""
Show complete database structure for threads, messages, and related data
"""
import sqlite3
from pathlib import Path
import sys
from io import StringIO

def show_table_structure(db_path, db_name, output_file=None):
    """Show all tables and their columns in a database"""
    print(f"\n{'='*80}")
    print(f"DATABASE: {db_name}")
    print(f"Location: {db_path}")
    print(f"{'='*80}\n")
    
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    # Get all tables
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name")
    tables = cursor.fetchall()
    
    for table in tables:
        table_name = table['name']
        print(f"\n TABLE: {table_name}")
        print("-" * 80)
        
        # Get table structure
        cursor.execute(f"PRAGMA table_info({table_name})")
        columns = cursor.fetchall()
        
        print(f"{'Column Name':<30} {'Type':<15} {'Not Null':<10} {'Default':<15} {'PK'}")
        print("-" * 80)
        
        for col in columns:
            col_name = col['name']
            col_type = col['type']
            not_null = 'YES' if col['notnull'] else 'NO'
            default = col['dflt_value'] if col['dflt_value'] else ''
            pk = 'YES' if col['pk'] else ''
            
            print(f"{col_name:<30} {col_type:<15} {not_null:<10} {str(default):<15} {pk}")
        
        # Get row count
        cursor.execute(f"SELECT COUNT(*) as count FROM {table_name}")
        count = cursor.fetchone()['count']
        print(f"\nTotal rows: {count}")
        
        # Show sample data for important tables
        if table_name in ['threads', 'messages', 'thread_assignments', 'synergy_sessions'] and count > 0:
            print(f"\nSample data (first 3 rows):")
            cursor.execute(f"SELECT * FROM {table_name} LIMIT 3")
            samples = cursor.fetchall()
            
            for i, row in enumerate(samples, 1):
                print(f"\n  Row {i}:")
                for key in row.keys():
                    value = row[key]
                    if value and len(str(value)) > 100:
                        value = str(value)[:100] + "..."
                    print(f"    {key}: {value}")
    
    conn.close()

# Main databases (paths relative to data/ folder since script is now in data/)
databases = [
    ('sessions.db', 'SESSIONS DATABASE (Main threads & messages)'),
    ('ai_infrastructure.db', 'AI INFRASTRUCTURE (Users & credentials)'),
    ('synergy_sessions.db', 'SYNERGY SESSIONS (Synergy integration)')
]

# Redirect output to both console and file
output_buffer = StringIO()
original_stdout = sys.stdout

class TeeOutput:
    def __init__(self, *streams):
        self.streams = streams
    
    def write(self, data):
        for stream in self.streams:
            stream.write(data)
    
    def flush(self):
        for stream in self.streams:
            stream.flush()

sys.stdout = TeeOutput(original_stdout, output_buffer)

print("\n" + "="*80)
print("COMPLETE DATABASE STRUCTURE FOR AI AGENTS PLATFORM")
print("="*80)

for db_path, db_name in databases:
    full_path = Path(db_path)
    if full_path.exists():
        show_table_structure(full_path, db_name)
    else:
        print(f"\n Database not found: {db_path}")

print("\n" + "="*80)
print("KEY IDENTIFIERS SUMMARY")
print("="*80)
print("""
THREAD IDENTIFICATION:
  - threads.id (INTEGER, PRIMARY KEY) → Internal database ID (e.g., 1, 2, 3)
  - threads.thread_slug (TEXT, UNIQUE) → External thread ID used in UI (e.g., '1762664086386')
  
    CRITICAL: Frontend uses thread_slug as thread.id
    Backend joins use threads.id (internal database ID)

MESSAGES:
  - messages.id (INTEGER, PRIMARY KEY) → Message database ID
  - messages.thread_id (INTEGER, FOREIGN KEY) → Links to threads.id (NOT thread_slug!)
  
    CRITICAL: Messages join on threads.id, NOT thread_slug

THREAD ASSIGNMENTS (Location tracking):
  - thread_assignments.session_id (TEXT) → Same as threads.thread_slug
  - thread_assignments.location (TEXT) → 'prime', 'agent-1', 'agent-2', etc.
  
SYNERGY SESSIONS:
  - synergy_sessions.session_id (TEXT, PRIMARY KEY) → Synergy card ID
  - synergy_sessions.thread_ids (TEXT) → JSON array of thread_slugs
  
RELATIONSHIPS:
  1. Frontend thread.id ←→ Database threads.thread_slug
  2. Database threads.id ←→ Database messages.thread_id
  3. Frontend thread.id ←→ thread_assignments.session_id
  4. Synergy card ←→ JSON array of thread_slugs in synergy_sessions.thread_ids
""")

print("\nQUERY EXAMPLES:")
print("="*80)
print("""
1. Get thread with messages:
   SELECT t.*, COUNT(m.id) as message_count
   FROM threads t
   LEFT JOIN messages m ON t.id = m.thread_id
   WHERE t.thread_slug = '1762664086386'
   GROUP BY t.id

2. Get messages for a thread:
   SELECT m.*
   FROM messages m
   JOIN threads t ON m.thread_id = t.id
   WHERE t.thread_slug = '1762664086386'
   ORDER BY m.timestamp

3. Get thread location:
   SELECT location
   FROM thread_assignments
   WHERE session_id = '1762664086386'

4. Get threads for synergy session:
   SELECT thread_ids
   FROM synergy_sessions
   WHERE session_id = 'synergy_card_id'
""")

# Restore stdout and save to file
sys.stdout = original_stdout

output_file = Path('database_data_locations.txt')
with open(output_file, 'w', encoding='utf-8') as f:
    f.write(output_buffer.getvalue())

print(f"\n Database structure exported to: {output_file}")
print(f" File size: {output_file.stat().st_size:,} bytes")

"""Check if Debugging Detective prompt is in database"""
import sys
sys.path.insert(0, 'AI_infrastructure')

from shared.database_utils import get_database_connection

# Connect to database
conn = get_database_connection('ai_infrastructure')
cur = conn.cursor()

# Check for Debugging Detective
print("\n=== CHECKING FOR DEBUGGING DETECTIVE PROMPT ===\n")

cur.execute("""
    SELECT id, name, type, category, visibility, created_at
    FROM prompt_library
    WHERE name ILIKE %s OR name ILIKE %s
    LIMIT 5
""", ('%Debug%', '%detective%'))

rows = cur.fetchall()

if rows:
    print(f"FOUND {len(rows)} matching prompt(s):")
    for row in rows:
        # Row is a dict from RealDictCursor
        print(f"  ID: {row['id']}")
        print(f"  Name: {row['name']}")
        print(f"  Type: {row['type']}")
        print(f"  Category: {row['category']}")
        print(f"  Visibility: {row['visibility']}")
        print(f"  Created: {row['created_at']}")
        print()
else:
    print("NOT FOUND in database!")
    print("\nSearching all prompts with 'system' or 'agent' in name...")
    
    cur.execute("""
        SELECT id, name, type, category
        FROM prompt_library
        WHERE name ILIKE %s OR name ILIKE %s
        LIMIT 10
    """, ('%system%', '%agent%'))
    
    system_rows = cur.fetchall()
    if system_rows:
        print(f"\nFound {len(system_rows)} prompts:")
        for row in system_rows:
            print(f"  - {row['name']} ({row['type']}, {row['category']})")

# Show total prompt count
cur.execute("SELECT COUNT(*) FROM prompt_library")
total_row = cur.fetchone()
total = total_row['count'] if isinstance(total_row, dict) else total_row[0]
print(f"\n\nTotal prompts in database: {total}")

# List all .prompt.md files
print("\n=== .PROMPT.MD FILES IN .github/prompts/ ===\n")
from pathlib import Path
prompts_dir = Path('.github/prompts')
if prompts_dir.exists():
    prompt_files = list(prompts_dir.glob('*.prompt.md'))
    print(f"Found {len(prompt_files)} .prompt.md files:")
    for pf in prompt_files:
        print(f"  - {pf.name}")
else:
    print("Directory not found!")

conn.close()

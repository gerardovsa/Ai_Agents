import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'AI_infrastructure'))

from shared.database_utils import execute_query

count = execute_query(
    "SELECT COUNT(*) FROM sessions.threads WHERE location LIKE %s OR location = %s OR location = %s",
    ('agent-%', 'synergy', 'prime'),
    fetch_mode='value'
)
print(f'Threads with non-unassigned locations: {count}')

# Show actual threads if any
if count > 0:
    rows = execute_query(
        "SELECT thread_slug, location, name FROM sessions.threads WHERE location LIKE %s OR location = %s OR location = %s LIMIT 10",
        ('agent-%', 'synergy', 'prime'),
        fetch_mode='all'
    )
    print('\nThreads with agent locations:')
    for r in rows:
        print(f"  {r['thread_slug'][:20]:20} | {r['location']:15} | {r['name'][:40]}")

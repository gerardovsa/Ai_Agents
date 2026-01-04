from AI_infrastructure.shared.database_utils import execute_query

rows = execute_query(
    'SELECT thread_slug, location, name FROM sessions.threads WHERE user_id = 1 ORDER BY updated_at DESC LIMIT 20',
    fetch_mode='all'
)

print('\nSample threads from database:')
print('-' * 100)
print(f"{'Thread Slug':<25} | {'Location':<20} | {'Name':<50}")
print('-' * 100)

for r in rows:
    slug = r['thread_slug'][:24] if r['thread_slug'] else 'NULL'
    loc = r['location'] if r['location'] else 'NULL'
    name = r['name'][:49] if r['name'] else 'NULL'
    print(f"{slug:<25} | {loc:<20} | {name:<50}")

# Count by location
print('\nLocation distribution:')
print('-' * 50)
counts = execute_query(
    'SELECT location, COUNT(*) as count FROM sessions.threads WHERE user_id = 1 GROUP BY location ORDER BY count DESC',
    fetch_mode='all'
)
for c in counts:
    loc = c['location'] if c['location'] else 'NULL'
    print(f"  {loc:<20}: {c['count']}")

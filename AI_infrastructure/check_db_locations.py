import os

# Check both possible locations
locations = [
    'ai_infrastructure.db',
    '../ai_infrastructure.db'
]

for loc in locations:
    if os.path.exists(loc):
        print(f"\nChecking: {os.path.abspath(loc)}")
        conn = psycopg2.connect(loc)
        cursor = conn.cursor()
        cursor.execute("SELECT tablename FROM pg_tables WHERE schemaname = 'ai_infrastructure'")
        tables = [row[0] for row in cursor.fetchall()]
        print(f"  Tables ({len(tables)}): {tables}")
        conn.close()


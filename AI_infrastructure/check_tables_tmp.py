from shared.database_utils import execute_query
tables = execute_query(
    "SELECT tablename FROM pg_tables WHERE schemaname='ai_infrastructure' ORDER BY tablename",
    fetch_mode='all'
)
for t in tables:
    print(t['tablename'])

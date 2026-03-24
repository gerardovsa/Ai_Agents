import sys
sys.path.insert(0, 'AI_infrastructure')
from shared.database_utils import execute_query

size = execute_query(
    "SELECT pg_size_pretty(pg_database_size(current_database())) as db_size",
    fetch_mode='one'
)
print("Total DB size:", size['db_size'])

schema_sizes = execute_query("""
    SELECT schemaname, 
           pg_size_pretty(sum(pg_total_relation_size(schemaname||'.'||tablename))::bigint) as schema_size,
           sum(pg_total_relation_size(schemaname||'.'||tablename)) as raw_bytes
    FROM pg_tables
    WHERE schemaname IN ('ai_infrastructure','sessions','stock_data','synergy_sessions','kanban_analytics')
    GROUP BY schemaname
    ORDER BY raw_bytes DESC
""", fetch_mode='all')

print()
for s in schema_sizes:
    print(f"  {s['schemaname']}: {s['schema_size']}")

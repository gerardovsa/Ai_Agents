#!/usr/bin/env python3
import sys
sys.path.insert(0, 'c:/Users/gpoli/GIT/AI_agents/AI_infrastructure')
from shared.database_utils import execute_query

query = "SELECT column_name, data_type FROM information_schema.columns WHERE table_schema = 'sessions' AND table_name = 'threads' ORDER BY ordinal_position"
rows = execute_query(query, (), fetch_mode='all')
print('Threads table columns:')
for row in rows:
    print(f'  {row["column_name"]} ({row["data_type"]})')


"""Quick script to run incremental kanban sync"""

import sys
from pathlib import Path

# Add parent directories to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))
sys.path.insert(0, str(Path(__file__).parent.parent.parent / 'AI_infrastructure'))

from sync.kanban_db_sync import sync_from_sql_server

if __name__ == '__main__':
    print("Running incremental sync...")
    result = sync_from_sql_server(full_sync=False)
    print(f"\nSync complete:")
    print(f"  Jobs synced: {result.get('jobs_synced', 0)}")
    print(f"  Transitions: {result.get('transitions_recorded', 0)}")
    print(f"  Duration: {result.get('sync_duration', 0):.2f}s")

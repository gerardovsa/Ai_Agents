"""Quick fix script to update kanban_column from hyphen to underscore format"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'AI_infrastructure'))

from shared.database_utils import get_synergy_sessions_connection

conn = get_synergy_sessions_connection()
cursor = conn.cursor()

# Update the test session
cursor.execute("""
    UPDATE synergy_sessions.synergy_sessions 
    SET kanban_column = 'in_progress' 
    WHERE session_id = 'syn_demo_1763552884'
    AND kanban_column = 'in-progress'
""")

conn.commit()
print(f"✅ Updated {cursor.rowcount} row(s) - kanban_column now uses underscore format")

conn.close()

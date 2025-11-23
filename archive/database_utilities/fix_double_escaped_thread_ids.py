"""
Fix double-escaped thread_ids in synergy_sessions table
This script fixes the database corruption where thread_ids were double-stringified
"""
from shared.database_utils import convert_sql_placeholders

import sqlite3
import json
from pathlib import Path

# Database path
db_path = Path(__file__).parent / 'data' / 'ai_infrastructure.db'

print(f"Connecting to database: {db_path}")
conn = sqlite3.connect(str(db_path))
cursor = conn.cursor()

# Get all sessions with thread_ids
cursor.execute("SELECT session_id, thread_ids FROM synergy_sessions WHERE thread_ids IS NOT NULL AND thread_ids != '[]'")
sessions = cursor.fetchall()

print(f"\nFound {len(sessions)} sessions with thread_ids")

fixed_count = 0
for session_id, thread_ids_str in sessions:
    print(f"\n{'='*60}")
    print(f"Session: {session_id}")
    print(f"Original value: {repr(thread_ids_str)}")
    
    try:
        # Try to parse once
        parsed_once = json.loads(thread_ids_str)
        print(f"Parsed once: {parsed_once} (type: {type(parsed_once)})")
        
        # Check if it's a string (double-escaped)
        if isinstance(parsed_once, str):
            print("  -> Double-escaped detected! Parsing again...")
            parsed_twice = json.loads(parsed_once)
            print(f"  -> Parsed twice: {parsed_twice} (type: {type(parsed_twice)})")
            
            # If it's now an array, fix it
            if isinstance(parsed_twice, list):
                # Store as proper JSON array
                fixed_value = json.dumps(parsed_twice)
                print(f"  -> Fixed value: {fixed_value}")
                
                # Update database
                cursor.execute(
                    "UPDATE synergy_sessions SET thread_ids = ? WHERE session_id = ?",
                    (fixed_value, session_id)
                )
                fixed_count += 1
                print(f"  -> ✅ FIXED")
            else:
                print(f"  -> ⚠️ Unexpected type after second parse: {type(parsed_twice)}")
        elif isinstance(parsed_once, list):
            print("  -> Already correct format (array)")
        else:
            print(f"  -> ⚠️ Unexpected type: {type(parsed_once)}")
            
    except json.JSONDecodeError as e:
        print(f"  -> ❌ JSON decode error: {e}")
    except Exception as e:
        print(f"  -> ❌ Error: {e}")

# Commit changes
conn.commit()
conn.close()

print(f"\n{'='*60}")
print(f"✅ Fixed {fixed_count} out of {len(sessions)} sessions")
print("Database updated successfully!")

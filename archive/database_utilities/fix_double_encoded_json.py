"""Fix double-encoded JSON in database"""
import sqlite3
from pathlib import Path
import json
from shared.database_utils import convert_sql_placeholders

root = Path('C:/Users/gpoli/GIT/AI_agents')
db = root / 'data' / 'synergy_sessions.db'

conn = sqlite3.connect(str(db))
cursor = conn.cursor()

# Get all sessions with documents
cursor.execute("SELECT session_id, documents FROM synergy_sessions WHERE documents IS NOT NULL AND documents != ''")
rows = cursor.fetchall()

print(f"Found {len(rows)} sessions with documents")

for session_id, docs_raw in rows:
    print(f"\n{'='*80}")
    print(f"Session: {session_id}")
    print(f"{'='*80}")
    
    try:
        # First parse
        first_parse = json.loads(docs_raw)
        print(f"First parse type: {type(first_parse)}")
        
        if isinstance(first_parse, str):
            print("⚠️  DOUBLE ENCODED! Need to parse again...")
            # Second parse
            second_parse = json.loads(first_parse)
            print(f"Second parse type: {type(second_parse)}")
            
            if isinstance(second_parse, list):
                print(f"✅ Got list with {len(second_parse)} items!")
                
                # Fix it in the database
                correct_json = json.dumps(second_parse)
                print(f"\nFixing in database...")
                sql, params = convert_sql_placeholders("UPDATE synergy_sessions SET documents = ? WHERE session_id = ?", (correct_json, session_id))

                cursor.execute(sql, params)
                print("✅ Fixed!")
            else:
                print(f"❌ Second parse gave unexpected type: {type(second_parse)}")
        elif isinstance(first_parse, list):
            print(f"✅ Already correct - list with {len(first_parse)} items")
        else:
            print(f"⚠️  Unexpected type: {type(first_parse)}")
            
    except Exception as e:
        print(f"❌ Error: {e}")

conn.commit()
print(f"\n{'='*80}")
print("Checking other JSON fields...")
print(f"{'='*80}")

# Check all JSON fields
json_fields = ['platforms_involved', 'tags', 'documents', 'links', 
              'next_steps', 'assignees', 'recent_activity', 'checklist',
              'thread_ids', 'assigned_agents']

for field in json_fields:
    print(f"\nChecking {field}...")
    cursor.execute(f"SELECT session_id, {field} FROM synergy_sessions WHERE {field} IS NOT NULL AND {field} != ''")
    rows = cursor.fetchall()
    
    double_encoded_count = 0
    for session_id, value in rows:
        try:
            first = json.loads(value)
            if isinstance(first, str):
                # Try second parse
                try:
                    second = json.loads(first)
                    print(f"  ⚠️  {session_id}: Double encoded!")
                    double_encoded_count += 1
                    # Fix it
                    correct_json = json.dumps(second)
                    cursor.execute(f"UPDATE synergy_sessions SET {field} = ? WHERE session_id = ?", 
                                 (correct_json, session_id))
                except:
                    pass
        except:
            pass
    
    if double_encoded_count > 0:
        print(f"  ✅ Fixed {double_encoded_count} double-encoded {field} fields")
    else:
        print(f"  ✅ No double-encoding issues in {field}")

conn.commit()
conn.close()

print(f"\n{'='*80}")
print("✅ ALL FIXES APPLIED!")
print("{'='*80}")

"""
Check message structure in database for thread 1762918241531
"""
import sqlite3
import json

# Connect to database
conn = sqlite3.connect('data/sessions.db')
cursor = conn.cursor()

# Get messages for thread
cursor.execute("""
    SELECT id, role, content, created_at 
    FROM messages 
    WHERE thread_id = (SELECT id FROM threads WHERE thread_slug = '1762918241531')
    ORDER BY created_at ASC
""")

messages = cursor.fetchall()

print("\n" + "="*80)
print(f"FOUND {len(messages)} MESSAGES IN THREAD 1762918241531")
print("="*80 + "\n")

for i, (msg_id, role, content, created_at) in enumerate(messages):
    print(f"\n--- MESSAGE {i+1} (ID: {msg_id}) ---")
    print(f"Role: {role}")
    print(f"Created: {created_at}")
    print(f"Content Type: {type(content)}")
    
    # Try to parse as JSON
    try:
        content_obj = json.loads(content)
        print(f"Content Structure: {type(content_obj)}")
        
        # If it's a list (conversation history format)
        if isinstance(content_obj, list):
            print(f"Content is LIST with {len(content_obj)} items")
            for j, item in enumerate(content_obj):
                print(f"  Item {j+1}: {type(item)}")
                if isinstance(item, dict):
                    print(f"    Keys: {list(item.keys())}")
                    if 'type' in item:
                        print(f"    Type: {item['type']}")
                    if 'thinking' in item:
                        print(f"    Has 'thinking' field: {len(str(item.get('thinking', '')))} chars")
                    if 'signature' in item:
                        print(f"    Has 'signature' field: {len(str(item.get('signature', '')))} chars")
                    else:
                        print(f"    MISSING 'signature' field!")
                    if 'text' in item:
                        print(f"    Has 'text' field: {len(str(item.get('text', '')))} chars")
        
        # If it's a dict
        elif isinstance(content_obj, dict):
            print(f"Content is DICT with keys: {list(content_obj.keys())}")
            if 'type' in content_obj:
                print(f"  Type: {content_obj['type']}")
            if 'thinking' in content_obj:
                print(f"  Has 'thinking' field: {len(str(content_obj.get('thinking', '')))} chars")
            if 'signature' in content_obj:
                print(f"  Has 'signature' field: {len(str(content_obj.get('signature', '')))} chars")
            else:
                print(f"  MISSING 'signature' field!")
        
        # If it's a string
        elif isinstance(content_obj, str):
            print(f"Content is STRING: {content_obj[:100]}...")
    
    except json.JSONDecodeError:
        # Not JSON, just a plain string
        print(f"Content is PLAIN TEXT (not JSON): {content[:100]}...")
    
    print("\n" + "-"*80)

conn.close()

print("\n" + "="*80)
print("ANALYSIS COMPLETE")
print("="*80 + "\n")

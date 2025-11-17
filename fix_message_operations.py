"""
Fix message_operations.py - Replace all execute_sqlite_* calls with direct psycopg2
This script comprehensively replaces all SQLite wrapper functions with proper database connections
"""

import re
from pathlib import Path

file_path = Path('AI_infrastructure/routes/message_operations.py')
content = file_path.read_text(encoding='utf-8')

# Pattern 1: Replace clone_thread function
clone_pattern = r'''        db_path = get_sessions_database_path\(\)
        
        # Get original thread
        thread_query = "SELECT \* FROM sessions\.threads WHERE id = %s"
        thread = execute_sqlite_query\(db_path, thread_query, \(thread_id,\)\)
        if not thread:
            return error_response\("Thread not found", 404\)
        thread = thread\[0\]
        
        # Get all messages
        messages_query = "SELECT \* FROM sessions\.messages WHERE thread_id = %s ORDER BY created_at ASC"
        messages = execute_sqlite_query\(db_path, messages_query, \(thread_id,\)\)'''

clone_replacement = '''        # Get database connection
        conn = get_database_connection('sessions')
        cursor = conn.cursor()
        
        # Get original thread
        thread_query = "SELECT * FROM threads WHERE id = %s"
        cursor.execute(thread_query, (thread_id,))
        thread = cursor.fetchone()
        if not thread:
            cursor.close()
            conn.close()
            return error_response("Thread not found", 404)
        
        # Get all messages
        messages_query = "SELECT * FROM messages WHERE thread_id = %s ORDER BY created_at ASC"
        cursor.execute(messages_query, (thread_id,))
        messages = cursor.fetchall()'''

content = re.sub(clone_pattern, clone_replacement, content)

# Pattern 2: Replace clone INSERT thread
clone_insert = r'''        insert_thread = """
            INSERT INTO sessions\.threads \(
                thread_slug, name, user_id, location, tags, 
                metadata, synergy_card_id, created_at, updated_at
            \) VALUES \(%s, %s, %s, %s, %s, %s, %s, %s, %s\)
        """
        
        metadata = json\.loads\(thread\['metadata'\]\) if thread\.get\('metadata'\) else \{\}
        metadata\['cloned_from'\] = thread\['thread_slug'\]
        metadata\['clone_date'\] = datetime\.now\(\)\.isoformat\(\)
        
        execute_sqlite_update\(db_path, insert_thread, \(
            new_thread_slug,
            final_name,
            user_id,
            thread\['location'\],
            thread\['tags'\],
            json\.dumps\(metadata\),
            thread\.get\('synergy_card_id'\),
            datetime\.now\(\)\.isoformat\(\),
            datetime\.now\(\)\.isoformat\(\)
        \)\)
        
        # Get new thread ID
        new_thread = execute_sqlite_query\(
            db_path, 
            "SELECT id FROM sessions\.threads WHERE thread_slug = %s", 
            \(new_thread_slug,\)
        \)\[0\]
        new_thread_id = new_thread\['id'\]'''

clone_insert_replacement = '''        insert_thread = """
            INSERT INTO threads (
                thread_slug, name, user_id, location, tags, 
                metadata, synergy_card_id, created_at, updated_at
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
            RETURNING id
        """
        
        metadata = json.loads(thread['metadata']) if thread.get('metadata') else {}
        metadata['cloned_from'] = thread['thread_slug']
        metadata['clone_date'] = datetime.now().isoformat()
        
        cursor.execute(insert_thread, (
            new_thread_slug,
            final_name,
            user_id,
            thread['location'],
            thread['tags'],
            json.dumps(metadata),
            thread.get('synergy_card_id'),
            datetime.now().isoformat(),
            datetime.now().isoformat()
        ))
        
        # Get new thread ID from RETURNING clause
        new_thread = cursor.fetchone()
        new_thread_id = new_thread['id']
        conn.commit()'''

content = re.sub(clone_insert, clone_insert_replacement, content)

# Pattern 3: Replace clone message copy loop
clone_msg = r'''        # Copy all messages
        for msg in messages:
            insert_msg = """
                INSERT INTO sessions\.messages \(
                    thread_id, session_id, role, content, prompt, 
                    response_data, user_id, api_session_id, tool_calls,
                    tokens_used, metadata, created_at, updated_at
                \) VALUES \(%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s\)
            """
            execute_sqlite_update\(db_path, insert_msg, \(
                new_thread_id,
                f"cloned_\{msg\.get\('session_id', ''\)\}",
                msg\['role'\],
                msg\['content'\],
                msg\.get\('prompt'\),
                msg\.get\('response_data'\),
                user_id,
                msg\.get\('api_session_id'\),
                msg\.get\('tool_calls'\),
                msg\.get\('tokens_used'\),
                msg\.get\('metadata'\),
                msg\['created_at'\],
                datetime\.now\(\)\.isoformat\(\)
            \)\)
        
        return success_response\(\{'''

clone_msg_replacement = '''        # Copy all messages
        for msg in messages:
            insert_msg = """
                INSERT INTO messages (
                    thread_id, session_id, role, content, prompt, 
                    response_data, user_id, api_session_id, tool_calls,
                    tokens_used, metadata, created_at, updated_at
                ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """
            cursor.execute(insert_msg, (
                new_thread_id,
                f"cloned_{msg.get('session_id', '')}",
                msg['role'],
                msg['content'],
                msg.get('prompt'),
                msg.get('response_data'),
                user_id,
                msg.get('api_session_id'),
                msg.get('tool_calls'),
                msg.get('tokens_used'),
                msg.get('metadata'),
                msg['created_at'],
                datetime.now().isoformat()
            ))
        
        conn.commit()
        cursor.close()
        conn.close()
        
        return success_response({'''

content = re.sub(clone_msg, clone_msg_replacement, content)

# Save the modified file
file_path.write_text(content, encoding='utf-8')
print(f"Fixed message_operations.py (clone_thread function)")
print("Remaining functions to fix manually: delete_messages, copy_messages, export_thread")

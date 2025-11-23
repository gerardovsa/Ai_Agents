"""
Message Operations API Routes
==============================

Advanced message operations:
- Fork thread (create branch from specific message)
- Clone thread (duplicate entire thread)
- Delete messages (single or bulk)
- Copy messages between threads
- Export thread with messages

Author: AI Agent
Date: November 8, 2025
"""

from flask import Blueprint, request, jsonify
from shared.database_utils import get_database_connection, convert_sql_placeholders
import json
from datetime import datetime
import uuid

message_ops_bp = Blueprint('message_ops', __name__, url_prefix='/api/messages')

def success_response(data, message="Success"):
    return jsonify({'success': True, 'data': data, 'message': message}), 200

def error_response(message, status_code=400):
    return jsonify({'success': False, 'error': message}), status_code


@message_ops_bp.route('/fork', methods=['POST'])
def fork_thread():
    """
    Fork a thread from a specific message
    Creates a new branch with messages up to the fork point
    
    POST /api/messages/fork
    Body: {
        "thread_id": "123",
        "message_id": "456",
        "branch_name": "Alternative approach",
        "user_id": 14
    }
    """
    try:
        data = request.get_json()
        thread_id = data.get('thread_id')
        message_id = data.get('message_id')
        branch_name = data.get('branch_name', 'Forked thread')
        user_id = data.get('user_id')
        
        if not all([thread_id, message_id, user_id]):
            return error_response("thread_id, message_id, and user_id are required")
        
        # Get database connection
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
        
        # Get messages up to fork point
        messages_query = """
            SELECT * FROM messages 
            WHERE thread_id = %s 
            AND created_at <= (SELECT created_at FROM messages WHERE id = %s)
            ORDER BY created_at ASC
        """
        cursor.execute(messages_query, (thread_id, message_id))
        messages = cursor.fetchall()
        
        # Create new thread
        new_thread_slug = str(int(datetime.now().timestamp() * 1000))
        insert_thread = """
            INSERT INTO threads (
                thread_slug, name, user_id, location, tags, 
                parent_thread_id, branch_name, branch_point_message_id,
                metadata, synergy_card_id, created_at, updated_at
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            RETURNING id
        """
        
        metadata = json.loads(thread['metadata']) if thread.get('metadata') else {}
        metadata['forked_from'] = thread['thread_slug']
        metadata['fork_message_id'] = message_id
        
        cursor.execute(insert_thread, (
            new_thread_slug,
            f"{thread['name']} - {branch_name}",
            user_id,
            thread['location'],
            thread['tags'],
            thread_id,
            branch_name,
            message_id,
            json.dumps(metadata),
            thread.get('synergy_card_id'),
            datetime.now().isoformat(),
            datetime.now().isoformat()
        ))
        
        # Get new thread ID from RETURNING clause
        new_thread = cursor.fetchone()
        new_thread_id = new_thread['id']
        conn.commit()
        
        # Copy messages to new thread
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
                msg.get('session_id'),
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
        
        return success_response({
            'new_thread_id': new_thread_id,
            'new_thread_slug': new_thread_slug,
            'messages_copied': len(messages),
            'branch_name': branch_name
        }, message=f"Thread forked successfully with {len(messages)} messages")
        
    except Exception as e:
        return error_response(f"Failed to fork thread: {str(e)}", 500)


@message_ops_bp.route('/clone', methods=['POST'])
def clone_thread():
    """
    Clone an entire thread (duplicate all messages)
    
    POST /api/messages/clone
    Body: {
        "thread_id": "123",
        "new_name": "Copy of Original",
        "user_id": 14
    }
    """
    try:
        data = request.get_json()
        thread_id = data.get('thread_id')
        new_name = data.get('new_name')
        user_id = data.get('user_id')
        
        if not all([thread_id, user_id]):
            return error_response("thread_id and user_id are required")
        
        # Get database connection
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
        messages = cursor.fetchall()
        
        # Create new thread
        new_thread_slug = str(int(datetime.now().timestamp() * 1000))
        final_name = new_name or f"Copy of {thread['name']}"
        
        insert_thread = """
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
        conn.commit()
        
        # Copy all messages
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
        
        return success_response({
            'new_thread_id': new_thread_id,
            'new_thread_slug': new_thread_slug,
            'messages_cloned': len(messages),
            'name': final_name
        }, message=f"Thread cloned successfully with {len(messages)} messages")
        
    except Exception as e:
        return error_response(f"Failed to clone thread: {str(e)}", 500)


@message_ops_bp.route('/delete', methods=['DELETE'])
def delete_messages():
    """
    Delete one or more messages
    
    DELETE /api/messages/delete
    Body: {
        "message_ids": [123, 456, 789],
        "thread_id": "abc123"
    }
    """
    try:
        data = request.get_json()
        message_ids = data.get('message_ids', [])
        thread_id = data.get('thread_id')
        
        if not message_ids:
            return error_response("message_ids array is required")
        
        # Get database connection
        conn = get_database_connection('sessions')
        cursor = conn.cursor()
        
        # Delete messages
        placeholders = ','.join('%s' * len(message_ids))
        delete_query = f"DELETE FROM messages WHERE id IN ({placeholders})"
        cursor.execute(delete_query, tuple(message_ids))
        
        # Update thread updated_at
        if thread_id:
            update_thread = "UPDATE threads SET updated_at = %s WHERE id = %s"
            cursor.execute(update_thread, (datetime.now().isoformat(), thread_id))
        
        conn.commit()
        cursor.close()
        conn.close()
        
        return success_response({
            'deleted_count': len(message_ids)
        }, message=f"Deleted {len(message_ids)} messages")
        
    except Exception as e:
        return error_response(f"Failed to delete messages: {str(e)}", 500)


@message_ops_bp.route('/copy', methods=['POST'])
def copy_messages():
    """
    Copy messages from one thread to another
    
    POST /api/messages/copy
    Body: {
        "message_ids": [123, 456],
        "source_thread_id": "abc",
        "target_thread_id": "xyz",
        "user_id": 14
    }
    """
    try:
        data = request.get_json()
        message_ids = data.get('message_ids', [])
        target_thread_id = data.get('target_thread_id')
        user_id = data.get('user_id')
        
        if not all([message_ids, target_thread_id, user_id]):
            return error_response("message_ids, target_thread_id, and user_id are required")
        
        # Get database connection
        conn = get_database_connection('sessions')
        cursor = conn.cursor()
        
        # Get messages to copy
        placeholders = ','.join('%s' * len(message_ids))
        messages_query = f"SELECT * FROM messages WHERE id IN ({placeholders}) ORDER BY created_at ASC"
        cursor.execute(messages_query, tuple(message_ids))
        messages = cursor.fetchall()
        
        # Copy messages to target thread
        for msg in messages:
            insert_msg = """
                INSERT INTO messages (
                    thread_id, session_id, role, content, prompt, 
                    response_data, user_id, api_session_id, tool_calls,
                    tokens_used, metadata, created_at, updated_at
                ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """
            msg_metadata = json.loads(msg.get('metadata', '{}')) if msg.get('metadata') else {}
            msg_metadata['copied_from_message_id'] = msg['id']
            msg_metadata['copy_date'] = datetime.now().isoformat()
            
            cursor.execute(insert_msg, (
                target_thread_id,
                msg.get('session_id'),
                msg['role'],
                msg['content'],
                msg.get('prompt'),
                msg.get('response_data'),
                user_id,
                msg.get('api_session_id'),
                msg.get('tool_calls'),
                msg.get('tokens_used'),
                json.dumps(msg_metadata),
                msg['created_at'],
                datetime.now().isoformat()
            ))
        
        # Update target thread timestamp
        update_thread = "UPDATE threads SET updated_at = %s WHERE id = %s"
        cursor.execute(update_thread, (datetime.now().isoformat(), target_thread_id))
        
        conn.commit()
        cursor.close()
        conn.close()
        
        return success_response({
            'copied_count': len(messages),
            'target_thread_id': target_thread_id
        }, message=f"Copied {len(messages)} messages to target thread")
        
    except Exception as e:
        return error_response(f"Failed to copy messages: {str(e)}", 500)


@message_ops_bp.route('/export', methods=['GET'])
def export_thread():
    """
    Export thread with all messages as JSON
    
    GET /api/messages/export?thread_id=123
    """
    try:
        thread_id = request.args.get('thread_id')
        if not thread_id:
            return error_response("thread_id is required")
        
        # Get database connection
        conn = get_database_connection('sessions')
        cursor = conn.cursor()
        
        # Get thread
        thread_query = "SELECT * FROM threads WHERE id = %s"
        cursor.execute(thread_query, (thread_id,))
        thread = cursor.fetchone()
        if not thread:
            cursor.close()
            conn.close()
            return error_response("Thread not found", 404)
        
        # Get messages
        messages_query = """
            SELECT * FROM messages 
            WHERE thread_id = %s 
            ORDER BY created_at ASC
        """
        cursor.execute(messages_query, (thread_id,))
        messages = cursor.fetchall()
        
        cursor.close()
        conn.close()
        
        # Build export data
        export_data = {
            'thread': {
                'id': thread['id'],
                'thread_slug': thread['thread_slug'],
                'name': thread['name'],
                'user_id': thread['user_id'],
                'location': thread['location'],
                'tags': json.loads(thread['tags']) if thread.get('tags') else [],
                'metadata': json.loads(thread['metadata']) if thread.get('metadata') else {},
                'synergy_card_id': thread.get('synergy_card_id'),
                'created_at': thread['created_at'],
                'updated_at': thread['updated_at']
            },
            'messages': [
                {
                    'id': msg['id'],
                    'role': msg['role'],
                    'content': msg['content'],
                    'prompt': msg.get('prompt'),
                    'tool_calls': json.loads(msg['tool_calls']) if msg.get('tool_calls') else None,
                    'tokens_used': msg.get('tokens_used'),
                    'response_time_ms': msg.get('response_time_ms'),
                    'metadata': json.loads(msg['metadata']) if msg.get('metadata') else {},
                    'created_at': msg['created_at']
                }
                for msg in messages
            ],
            'export_metadata': {
                'export_date': datetime.now().isoformat(),
                'message_count': len(messages),
                'format_version': '1.0'
            }
        }
        
        return success_response(export_data, message=f"Exported thread with {len(messages)} messages")
        
    except Exception as e:
        return error_response(f"Failed to export thread: {str(e)}", 500)

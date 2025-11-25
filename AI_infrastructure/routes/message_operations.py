"""
FILE: AI_infrastructure/routes/message_operations.py
Message Operations API Routes
==============================

Advanced message operations:
- Fork thread (create branch from specific message)
- Clone thread (duplicate entire thread)
- Delete messages (single or bulk)
- Copy messages between threads
- Export thread with messages
- Merge branches back to parent thread

Author: AI Agent
Date: November 25, 2025
Last Modified: November 25, 2025 - Fixed all 8 connection leaks with context managers
"""

from flask import Blueprint, request, jsonify
from shared.database_utils import get_database_connection, convert_sql_placeholders
import json
from datetime import datetime

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
    # ✅ Initialize response BEFORE with block
    response_data = None
    status_code = 200
    
    try:
        data = request.get_json()
        thread_id = data.get('thread_id')
        message_id = data.get('message_id')
        branch_name = data.get('branch_name', 'Forked thread')
        user_id = data.get('user_id')
        
        if not all([thread_id, message_id, user_id]):
            return error_response("thread_id, message_id, and user_id are required")
        
        with get_database_connection('sessions') as conn:
            cursor = conn.cursor()
            
            # Get original thread
            sql, params = convert_sql_placeholders(
                "SELECT * FROM sessions.threads WHERE id = %s",
                (thread_id,)
            )
            cursor.execute(sql, params)
            thread = cursor.fetchone()
            
            # ✅ FIX LEAK #1: Don't return inside with block
            if not thread:
                response_data = error_response("Thread not found", 404)
                status_code = 404
            else:
                # Get messages up to fork point
                sql, params = convert_sql_placeholders("""
                    SELECT * FROM sessions.messages 
                    WHERE thread_id = %s 
                    AND created_at <= (SELECT created_at FROM sessions.messages WHERE id = %s)
                    ORDER BY created_at ASC
                """, (thread_id, message_id))
                cursor.execute(sql, params)
                messages = cursor.fetchall()
                
                # Create new thread
                new_thread_slug = str(int(datetime.now().timestamp() * 1000))
                
                metadata = json.loads(thread['metadata']) if thread.get('metadata') else {}
                metadata['forked_from'] = thread['thread_slug']
                metadata['fork_message_id'] = message_id
                
                sql, params = convert_sql_placeholders("""
                    INSERT INTO sessions.threads (
                        thread_slug, name, user_id, location, tags, 
                        parent_thread_id, branch_name, branch_point_message_id,
                        metadata, synergy_card_id, created_at, updated_at
                    ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                    RETURNING id
                """, (
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
                
                cursor.execute(sql, params)
                new_thread = cursor.fetchone()
                new_thread_id = new_thread['id'] if isinstance(new_thread, dict) else new_thread[0]
                
                # Copy messages to new thread
                for msg in messages:
                    sql, params = convert_sql_placeholders("""
                        INSERT INTO sessions.messages (
                            thread_id, workspace_id, user_id, role, content, 
                            prompt, include, tool_calls, tokens_used, 
                            response_time_ms, metadata, created_at, updated_at
                        ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                    """, (
                        new_thread_id,
                        msg.get('workspace_id'),
                        user_id,
                        msg['role'],
                        msg['content'],
                        msg.get('prompt'),
                        msg.get('include'),
                        msg.get('tool_calls'),
                        msg.get('tokens_used'),
                        msg.get('response_time_ms'),
                        msg.get('metadata'),
                        msg['created_at'],
                        datetime.now().isoformat()
                    ))
                    cursor.execute(sql, params)
                
                conn.commit()
                
                # ✅ FIX LEAK #2: Set response, don't return
                response_data = success_response({
                    'new_thread_id': new_thread_id,
                    'new_thread_slug': new_thread_slug,
                    'messages_copied': len(messages),
                    'branch_name': branch_name
                }, message=f"Thread forked successfully with {len(messages)} messages")
                status_code = 200
        
        # ✅ Return AFTER with block closes
        if response_data:
            return response_data[0], response_data[1] if isinstance(response_data, tuple) else response_data
        return success_response({'message': 'Fork completed'})
        
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
    # ✅ Initialize response BEFORE with block
    response_data = None
    status_code = 200
    
    try:
        data = request.get_json()
        thread_id = data.get('thread_id')
        new_name = data.get('new_name')
        user_id = data.get('user_id')
        
        if not all([thread_id, user_id]):
            return error_response("thread_id and user_id are required")
        
        with get_database_connection('sessions') as conn:
            cursor = conn.cursor()
            
            # Get original thread
            sql, params = convert_sql_placeholders(
                "SELECT * FROM sessions.threads WHERE id = %s",
                (thread_id,)
            )
            cursor.execute(sql, params)
            thread = cursor.fetchone()
            
            # ✅ FIX LEAK #3: Don't return inside with block
            if not thread:
                response_data = error_response("Thread not found", 404)
                status_code = 404
            else:
                # Get all messages
                sql, params = convert_sql_placeholders(
                    "SELECT * FROM sessions.messages WHERE thread_id = %s ORDER BY created_at ASC",
                    (thread_id,)
                )
                cursor.execute(sql, params)
                messages = cursor.fetchall()
                
                # Create new thread
                new_thread_slug = str(int(datetime.now().timestamp() * 1000))
                final_name = new_name or f"Copy of {thread['name']}"
                
                metadata = json.loads(thread['metadata']) if thread.get('metadata') else {}
                metadata['cloned_from'] = thread['thread_slug']
                metadata['clone_date'] = datetime.now().isoformat()
                
                sql, params = convert_sql_placeholders("""
                    INSERT INTO sessions.threads (
                        thread_slug, name, user_id, workspace_id, location, tags, 
                        metadata, synergy_card_id, created_at, updated_at
                    ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                    RETURNING id
                """, (
                    new_thread_slug,
                    final_name,
                    user_id,
                    thread.get('workspace_id'),
                    thread['location'],
                    thread['tags'],
                    json.dumps(metadata),
                    thread.get('synergy_card_id'),
                    datetime.now().isoformat(),
                    datetime.now().isoformat()
                ))
                
                cursor.execute(sql, params)
                new_thread = cursor.fetchone()
                new_thread_id = new_thread['id'] if isinstance(new_thread, dict) else new_thread[0]
                
                # Copy all messages
                for msg in messages:
                    sql, params = convert_sql_placeholders("""
                        INSERT INTO sessions.messages (
                            thread_id, workspace_id, user_id, role, content, 
                            prompt, include, tool_calls, tokens_used,
                            response_time_ms, metadata, created_at, updated_at
                        ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                    """, (
                        new_thread_id,
                        msg.get('workspace_id'),
                        user_id,
                        msg['role'],
                        msg['content'],
                        msg.get('prompt'),
                        msg.get('include'),
                        msg.get('tool_calls'),
                        msg.get('tokens_used'),
                        msg.get('response_time_ms'),
                        msg.get('metadata'),
                        msg['created_at'],
                        datetime.now().isoformat()
                    ))
                    cursor.execute(sql, params)
                
                conn.commit()
                
                # ✅ FIX LEAK #4: Set response, don't return
                response_data = success_response({
                    'new_thread_id': new_thread_id,
                    'new_thread_slug': new_thread_slug,
                    'messages_cloned': len(messages),
                    'name': final_name
                }, message=f"Thread cloned successfully with {len(messages)} messages")
                status_code = 200
        
        # ✅ Return AFTER with block closes
        if response_data:
            return response_data[0], response_data[1] if isinstance(response_data, tuple) else response_data
        return success_response({'message': 'Clone completed'})
        
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
        
        with get_database_connection('sessions') as conn:
            cursor = conn.cursor()
            
            # Delete messages using parameterized query
            placeholders = ','.join(['%s'] * len(message_ids))
            delete_query = f"DELETE FROM sessions.messages WHERE id IN ({placeholders})"
            sql, params = convert_sql_placeholders(delete_query, tuple(message_ids))
            cursor.execute(sql, params)
            
            # Update thread updated_at
            if thread_id:
                sql, params = convert_sql_placeholders(
                    "UPDATE sessions.threads SET updated_at = %s WHERE id = %s",
                    (datetime.now().isoformat(), thread_id)
                )
                cursor.execute(sql, params)
            
            conn.commit()
        
        # ✅ Return AFTER with block closes (no leak here, but good practice)
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
        
        with get_database_connection('sessions') as conn:
            cursor = conn.cursor()
            
            # Get messages to copy
            placeholders = ','.join(['%s'] * len(message_ids))
            messages_query = f"SELECT * FROM sessions.messages WHERE id IN ({placeholders}) ORDER BY created_at ASC"
            sql, params = convert_sql_placeholders(messages_query, tuple(message_ids))
            cursor.execute(sql, params)
            messages = cursor.fetchall()
            
            # Copy messages to target thread
            for msg in messages:
                msg_metadata = json.loads(msg.get('metadata', '{}')) if msg.get('metadata') else {}
                msg_metadata['copied_from_message_id'] = msg['id']
                msg_metadata['copy_date'] = datetime.now().isoformat()
                
                sql, params = convert_sql_placeholders("""
                    INSERT INTO sessions.messages (
                        thread_id, workspace_id, user_id, role, content, 
                        prompt, include, tool_calls, tokens_used,
                        response_time_ms, metadata, created_at, updated_at
                    ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                """, (
                    target_thread_id,
                    msg.get('workspace_id'),
                    user_id,
                    msg['role'],
                    msg['content'],
                    msg.get('prompt'),
                    msg.get('include'),
                    msg.get('tool_calls'),
                    msg.get('tokens_used'),
                    msg.get('response_time_ms'),
                    json.dumps(msg_metadata),
                    msg['created_at'],
                    datetime.now().isoformat()
                ))
                cursor.execute(sql, params)
            
            # Update target thread timestamp
            sql, params = convert_sql_placeholders(
                "UPDATE sessions.threads SET updated_at = %s WHERE id = %s",
                (datetime.now().isoformat(), target_thread_id)
            )
            cursor.execute(sql, params)
            
            conn.commit()
        
        # ✅ Return AFTER with block closes
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
    # ✅ Initialize response BEFORE with block
    response_data = None
    status_code = 200
    
    try:
        thread_id = request.args.get('thread_id')
        if not thread_id:
            return error_response("thread_id is required")
        
        with get_database_connection('sessions') as conn:
            cursor = conn.cursor()
            
            # Get thread
            sql, params = convert_sql_placeholders(
                "SELECT * FROM sessions.threads WHERE id = %s",
                (thread_id,)
            )
            cursor.execute(sql, params)
            thread = cursor.fetchone()
            
            # ✅ FIX LEAK #5: Don't return inside with block
            if not thread:
                response_data = error_response("Thread not found", 404)
                status_code = 404
            else:
                # Get messages
                sql, params = convert_sql_placeholders("""
                    SELECT * FROM sessions.messages 
                    WHERE thread_id = %s 
                    ORDER BY created_at ASC
                """, (thread_id,))
                cursor.execute(sql, params)
                messages = cursor.fetchall()
                
                # Build export data
                export_data = {
                    'thread': {
                        'id': thread['id'],
                        'thread_slug': thread['thread_slug'],
                        'name': thread['name'],
                        'user_id': thread['user_id'],
                        'workspace_id': thread.get('workspace_id'),
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
                            'include': msg.get('include'),
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
                
                # ✅ FIX LEAK #6: Set response, don't return
                response_data = success_response(export_data, message=f"Exported thread with {len(messages)} messages")
                status_code = 200
        
        # ✅ Return AFTER with block closes
        if response_data:
            return response_data[0], response_data[1] if isinstance(response_data, tuple) else response_data
        return error_response("Export failed", 500)
        
    except Exception as e:
        return error_response(f"Failed to export thread: {str(e)}", 500)


@message_ops_bp.route('/merge-branch', methods=['POST'])
def merge_branch():
    """
    Merge a branch back to parent thread
    
    POST /api/messages/merge-branch
    Body: {
        "branch_thread_id": "456",
        "parent_thread_id": "123",
        "user_id": 14,
        "merge_strategy": "append"  // or "replace_from_fork_point"
    }
    """
    # ✅ Initialize response BEFORE with block
    response_data = None
    status_code = 200
    
    try:
        data = request.get_json()
        branch_thread_id = data.get('branch_thread_id')
        parent_thread_id = data.get('parent_thread_id')
        user_id = data.get('user_id')
        merge_strategy = data.get('merge_strategy', 'append')
        
        if not all([branch_thread_id, parent_thread_id, user_id]):
            return error_response("branch_thread_id, parent_thread_id, and user_id are required")
        
        with get_database_connection('sessions') as conn:
            cursor = conn.cursor()
            
            # Get branch thread
            sql, params = convert_sql_placeholders(
                "SELECT * FROM sessions.threads WHERE id = %s",
                (branch_thread_id,)
            )
            cursor.execute(sql, params)
            branch_thread = cursor.fetchone()
            
            # ✅ FIX LEAK #7: Don't return inside with block
            if not branch_thread:
                response_data = error_response("Branch thread not found", 404)
                status_code = 404
            else:
                # Get parent thread
                sql, params = convert_sql_placeholders(
                    "SELECT * FROM sessions.threads WHERE id = %s",
                    (parent_thread_id,)
                )
                cursor.execute(sql, params)
                parent_thread = cursor.fetchone()
                
                if not parent_thread:
                    response_data = error_response("Parent thread not found", 404)
                    status_code = 404
                else:
                    # Get branch messages
                    sql, params = convert_sql_placeholders("""
                        SELECT * FROM sessions.messages 
                        WHERE thread_id = %s 
                        ORDER BY created_at ASC
                    """, (branch_thread_id,))
                    cursor.execute(sql, params)
                    branch_messages = cursor.fetchall()
                    
                    if merge_strategy == 'append':
                        # Simply append branch messages to parent
                        for msg in branch_messages:
                            msg_metadata = json.loads(msg.get('metadata', '{}')) if msg.get('metadata') else {}
                            msg_metadata['merged_from_branch'] = branch_thread_id
                            msg_metadata['merge_date'] = datetime.now().isoformat()
                            
                            sql, params = convert_sql_placeholders("""
                                INSERT INTO sessions.messages (
                                    thread_id, workspace_id, user_id, role, content, 
                                    prompt, include, tool_calls, tokens_used,
                                    response_time_ms, metadata, created_at, updated_at
                                ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                            """, (
                                parent_thread_id,
                                msg.get('workspace_id'),
                                user_id,
                                msg['role'],
                                msg['content'],
                                msg.get('prompt'),
                                msg.get('include'),
                                msg.get('tool_calls'),
                                msg.get('tokens_used'),
                                msg.get('response_time_ms'),
                                json.dumps(msg_metadata),
                                msg['created_at'],
                                datetime.now().isoformat()
                            ))
                            cursor.execute(sql, params)
                        
                        merged_count = len(branch_messages)
                        
                    elif merge_strategy == 'replace_from_fork_point':
                        # Delete messages after fork point in parent, then add branch messages
                        fork_point_msg_id = branch_thread.get('branch_point_message_id')
                        
                        if fork_point_msg_id:
                            # Get fork point timestamp
                            sql, params = convert_sql_placeholders(
                                "SELECT created_at FROM sessions.messages WHERE id = %s",
                                (fork_point_msg_id,)
                            )
                            cursor.execute(sql, params)
                            fork_point = cursor.fetchone()
                            
                            if fork_point:
                                fork_timestamp = fork_point['created_at'] if isinstance(fork_point, dict) else fork_point[0]
                                
                                # Delete messages after fork point
                                sql, params = convert_sql_placeholders("""
                                    DELETE FROM sessions.messages 
                                    WHERE thread_id = %s AND created_at > %s
                                """, (parent_thread_id, fork_timestamp))
                                cursor.execute(sql, params)
                        
                        # Add branch messages
                        for msg in branch_messages:
                            msg_metadata = json.loads(msg.get('metadata', '{}')) if msg.get('metadata') else {}
                            msg_metadata['merged_from_branch'] = branch_thread_id
                            msg_metadata['merge_date'] = datetime.now().isoformat()
                            
                            sql, params = convert_sql_placeholders("""
                                INSERT INTO sessions.messages (
                                    thread_id, workspace_id, user_id, role, content, 
                                    prompt, include, tool_calls, tokens_used,
                                    response_time_ms, metadata, created_at, updated_at
                                ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                            """, (
                                parent_thread_id,
                                msg.get('workspace_id'),
                                user_id,
                                msg['role'],
                                msg['content'],
                                msg.get('prompt'),
                                msg.get('include'),
                                msg.get('tool_calls'),
                                msg.get('tokens_used'),
                                msg.get('response_time_ms'),
                                json.dumps(msg_metadata),
                                msg['created_at'],
                                datetime.now().isoformat()
                            ))
                            cursor.execute(sql, params)
                        
                        merged_count = len(branch_messages)
                    
                    else:
                        response_data = error_response(f"Invalid merge strategy: {merge_strategy}", 400)
                        status_code = 400
                        merged_count = 0
                    
                    if response_data is None:
                        # Update parent thread timestamp
                        sql, params = convert_sql_placeholders(
                            "UPDATE sessions.threads SET updated_at = %s WHERE id = %s",
                            (datetime.now().isoformat(), parent_thread_id)
                        )
                        cursor.execute(sql, params)
                        
                        # Optionally mark branch as merged
                        branch_metadata = json.loads(branch_thread.get('metadata', '{}')) if branch_thread.get('metadata') else {}
                        branch_metadata['merged_to_parent'] = parent_thread_id
                        branch_metadata['merge_date'] = datetime.now().isoformat()
                        branch_metadata['merge_strategy'] = merge_strategy
                        
                        sql, params = convert_sql_placeholders(
                            "UPDATE sessions.threads SET metadata = %s WHERE id = %s",
                            (json.dumps(branch_metadata), branch_thread_id)
                        )
                        cursor.execute(sql, params)
                        
                        conn.commit()
                        
                        # ✅ FIX LEAK #8: Set response, don't return
                        response_data = success_response({
                            'parent_thread_id': parent_thread_id,
                            'branch_thread_id': branch_thread_id,
                            'messages_merged': merged_count,
                            'merge_strategy': merge_strategy
                        }, message=f"Branch merged successfully ({merged_count} messages)")
                        status_code = 200
        
        # ✅ Return AFTER with block closes
        if response_data:
            return response_data[0], response_data[1] if isinstance(response_data, tuple) else response_data
        return error_response("Merge failed", 500)
        
    except Exception as e:
        return error_response(f"Failed to merge branch: {str(e)}", 500)
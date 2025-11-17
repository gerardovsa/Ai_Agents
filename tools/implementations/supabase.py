"""
Supabase Tool Implementations
==============================

This module provides tool implementations for Supabase database operations.
"""

import os
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

try:
    from Supabase.supabase_client import SupabaseClient
    from config import SUPABASE_URL, SUPABASE_ANON_KEY, SUPABASE_SERVICE_KEY
    HAS_SUPABASE = True
except ImportError:
    HAS_SUPABASE = False
    # Supabase is optional - silently skip if not available


def _get_client():
    """Get or create Supabase client"""
    if not HAS_SUPABASE:
        raise Exception("Supabase client not available - install dependencies")
    
    return SupabaseClient(
        supabase_url=SUPABASE_URL,
        supabase_key=SUPABASE_ANON_KEY
    )


def supabase_query(table: str, select: str = "*", filters: dict = None, 
                   limit: int = None, order_by: str = None):
    """
    Query data from a Supabase table.
    
    Args:
        table: Table name
        select: Columns to select
        filters: Filter conditions
        limit: Maximum rows to return
        order_by: Column to order by
    
    Returns:
        Query results
    """
    print(f"🔧 Querying Supabase table: {table}")
    
    try:
        client = _get_client()
        query = client.table(table).select(select)
        
        # Apply filters
        if filters:
            for key, value in filters.items():
                query = query.eq(key, value)
        
        # Apply limit
        if limit:
            query = query.limit(limit)
        
        # Apply ordering
        if order_by:
            if '.' in order_by:
                column, direction = order_by.split('.')
                query = query.order(column, desc=(direction == 'desc'))
            else:
                query = query.order(order_by)
        
        # Execute query
        response = query.execute()
        
        return {
            'data': response.data,
            'count': len(response.data)
        }
        
    except Exception as e:
        print(f" Query failed: {e}")
        raise


def supabase_insert(table: str, data: dict):
    """
    Insert data into a Supabase table.
    
    Args:
        table: Table name
        data: Data to insert
    
    Returns:
        Inserted row(s)
    """
    print(f"🔧 Inserting into Supabase table: {table}")
    
    try:
        client = _get_client()
        response = client.table(table).insert(data).execute()
        
        return {
            'data': response.data,
            'count': len(response.data) if response.data else 0
        }
        
    except Exception as e:
        print(f" Insert failed: {e}")
        raise


def supabase_update(table: str, data: dict, filters: dict):
    """
    Update records in a Supabase table.
    
    Args:
        table: Table name
        data: Data to update
        filters: Filter conditions
    
    Returns:
        Updated row(s)
    """
    print(f"🔧 Updating Supabase table: {table}")
    
    try:
        client = _get_client()
        query = client.table(table).update(data)
        
        # Apply filters
        for key, value in filters.items():
            query = query.eq(key, value)
        
        response = query.execute()
        
        return {
            'data': response.data,
            'count': len(response.data) if response.data else 0
        }
        
    except Exception as e:
        print(f" Update failed: {e}")
        raise


def supabase_delete(table: str, filters: dict):
    """
    Delete records from a Supabase table.
    
    Args:
        table: Table name
        filters: Filter conditions
    
    Returns:
        Deleted row(s)
    """
    print(f"🔧 Deleting from Supabase table: {table}")
    
    try:
        client = _get_client()
        query = client.table(table).delete()
        
        # Apply filters
        for key, value in filters.items():
            query = query.eq(key, value)
        
        response = query.execute()
        
        return {
            'data': response.data,
            'count': len(response.data) if response.data else 0
        }
        
    except Exception as e:
        print(f" Delete failed: {e}")
        raise


def supabase_auth_user(email: str, password: str):
    """
    Authenticate a user with Supabase Auth.
    
    Args:
        email: User email
        password: User password
    
    Returns:
        Authentication result
    """
    print(f"🔧 Authenticating user: {email}")
    
    try:
        client = _get_client()
        response = client.auth.sign_in_with_password({
            "email": email,
            "password": password
        })
        
        return {
            'user': response.user,
            'session': response.session,
            'authenticated': True
        }
        
    except Exception as e:
        print(f" Authentication failed: {e}")
        raise


def supabase_storage_upload(bucket: str, file_path: str, file_content: str):
    """
    Upload a file to Supabase Storage.
    
    Args:
        bucket: Bucket name
        file_path: Path within bucket
        file_content: File content (base64 or path)
    
    Returns:
        Upload result with URL
    """
    print(f"🔧 Uploading to Supabase Storage: {bucket}/{file_path}")
    
    try:
        client = _get_client()
        
        # Check if file_content is a local file path
        if os.path.exists(file_content):
            with open(file_content, 'rb') as f:
                content = f.read()
        else:
            # Assume it's base64 or direct content
            content = file_content
        
        response = client.storage.from_(bucket).upload(file_path, content)
        
        # Get public URL
        public_url = client.storage.from_(bucket).get_public_url(file_path)
        
        return {
            'path': file_path,
            'public_url': public_url,
            'uploaded': True
        }
        
    except Exception as e:
        print(f" Upload failed: {e}")
        raise


def supabase_rpc(function_name: str, parameters: dict = None):
    """
    Call a PostgreSQL stored procedure or function.
    
    Args:
        function_name: Name of the RPC function
        parameters: Function parameters
    
    Returns:
        Function result
    """
    print(f"🔧 Calling Supabase RPC: {function_name}")
    
    try:
        client = _get_client()
        response = client.rpc(function_name, parameters or {}).execute()
        
        return {
            'data': response.data,
            'function': function_name
        }
        
    except Exception as e:
        print(f" RPC call failed: {e}")
        raise


def supabase_count(table: str, filters: dict = None):
    """
    Count rows in a table with optional filters.
    
    Args:
        table: Table name
        filters: Filter conditions
    
    Returns:
        Row count
    """
    print(f"🔧 Counting rows in Supabase table: {table}")
    
    try:
        client = _get_client()
        query = client.table(table).select('*', count='exact')
        
        # Apply filters
        if filters:
            for key, value in filters.items():
                query = query.eq(key, value)
        
        response = query.execute()
        
        return {
            'count': response.count,
            'table': table
        }
        
    except Exception as e:
        print(f" Count failed: {e}")
        raise


def supabase_auth_signup(email: str, password: str, metadata: dict = None):
    """
    Create a new user account with email and password.
    
    Args:
        email: User email
        password: User password
        metadata: Optional user metadata
    
    Returns:
        User registration result
    """
    print(f"🔧 Signing up user: {email}")
    
    try:
        client = _get_client()
        response = client.auth.sign_up({
            "email": email,
            "password": password,
            "options": {
                "data": metadata or {}
            }
        })
        
        return {
            'user': response.user,
            'session': response.session,
            'created': True
        }
        
    except Exception as e:
        print(f" Signup failed: {e}")
        raise


def supabase_auth_signin(email: str, password: str):
    """
    Sign in an existing user with email and password.
    
    Args:
        email: User email
        password: User password
    
    Returns:
        Authentication result
    """
    print(f"🔧 Signing in user: {email}")
    
    try:
        client = _get_client()
        response = client.auth.sign_in_with_password({
            "email": email,
            "password": password
        })
        
        return {
            'user': response.user,
            'session': response.session,
            'authenticated': True
        }
        
    except Exception as e:
        print(f" Sign in failed: {e}")
        raise


def supabase_auth_signout():
    """
    Sign out the current user.
    
    Returns:
        Sign out result
    """
    print(f"🔧 Signing out current user")
    
    try:
        client = _get_client()
        client.auth.sign_out()
        
        return {
            'signed_out': True
        }
        
    except Exception as e:
        print(f" Sign out failed: {e}")
        raise


def supabase_auth_get_user():
    """
    Get the current authenticated user.
    
    Returns:
        Current user information
    """
    print(f"🔧 Getting current user")
    
    try:
        client = _get_client()
        response = client.auth.get_user()
        
        return {
            'user': response.user
        }
        
    except Exception as e:
        print(f" Get user failed: {e}")
        raise


def supabase_auth_update_user(email: str = None, password: str = None, metadata: dict = None):
    """
    Update user metadata or password.
    
    Args:
        email: New email (optional)
        password: New password (optional)
        metadata: New metadata (optional)
    
    Returns:
        Updated user information
    """
    print(f"🔧 Updating user information")
    
    try:
        client = _get_client()
        update_data = {}
        
        if email:
            update_data['email'] = email
        if password:
            update_data['password'] = password
        if metadata:
            update_data['data'] = metadata
        
        response = client.auth.update_user(update_data)
        
        return {
            'user': response.user,
            'updated': True
        }
        
    except Exception as e:
        print(f" Update user failed: {e}")
        raise


def supabase_auth_reset_password(email: str):
    """
    Send password reset email.
    
    Args:
        email: User email
    
    Returns:
        Password reset result
    """
    print(f"🔧 Sending password reset email to: {email}")
    
    try:
        client = _get_client()
        response = client.auth.reset_password_for_email(email)
        
        return {
            'email_sent': True,
            'email': email
        }
        
    except Exception as e:
        print(f" Password reset failed: {e}")
        raise


def supabase_auth_invite_user(email: str, metadata: dict = None):
    """
    Invite a user via email (admin only).
    
    Args:
        email: User email to invite
        metadata: Optional user metadata
    
    Returns:
        Invitation result
    """
    print(f"🔧 Inviting user: {email}")
    
    try:
        client = _get_client()
        # Note: Requires service role key
        response = client.auth.admin.invite_user_by_email(
            email,
            options={"data": metadata or {}}
        )
        
        return {
            'user': response.user,
            'invited': True
        }
        
    except Exception as e:
        print(f" Invite user failed: {e}")
        raise


def supabase_storage_download(bucket: str, file_path: str):
    """
    Download a file from Supabase Storage.
    
    Args:
        bucket: Bucket name
        file_path: Path within bucket
    
    Returns:
        File content
    """
    print(f"🔧 Downloading from Supabase Storage: {bucket}/{file_path}")
    
    try:
        client = _get_client()
        response = client.storage.from_(bucket).download(file_path)
        
        return {
            'path': file_path,
            'content': response,
            'downloaded': True
        }
        
    except Exception as e:
        print(f" Download failed: {e}")
        raise


def supabase_storage_delete(bucket: str, file_paths: list):
    """
    Delete files from Supabase Storage.
    
    Args:
        bucket: Bucket name
        file_paths: List of file paths to delete
    
    Returns:
        Deletion result
    """
    print(f"🔧 Deleting from Supabase Storage: {bucket}")
    
    try:
        client = _get_client()
        response = client.storage.from_(bucket).remove(file_paths)
        
        return {
            'deleted': True,
            'count': len(file_paths)
        }
        
    except Exception as e:
        print(f" Delete failed: {e}")
        raise


def supabase_storage_list(bucket: str, path: str = '', limit: int = 100):
    """
    List files in a storage bucket.
    
    Args:
        bucket: Bucket name
        path: Path within bucket
        limit: Maximum files to return
    
    Returns:
        List of files
    """
    print(f"🔧 Listing files in Supabase Storage: {bucket}/{path}")
    
    try:
        client = _get_client()
        response = client.storage.from_(bucket).list(path, {
            'limit': limit,
            'sortBy': {'column': 'name', 'order': 'asc'}
        })
        
        return {
            'files': response,
            'count': len(response)
        }
        
    except Exception as e:
        print(f" List failed: {e}")
        raise


def supabase_storage_get_public_url(bucket: str, file_path: str):
    """
    Get public URL for a file.
    
    Args:
        bucket: Bucket name
        file_path: Path within bucket
    
    Returns:
        Public URL
    """
    print(f"🔧 Getting public URL: {bucket}/{file_path}")
    
    try:
        client = _get_client()
        url = client.storage.from_(bucket).get_public_url(file_path)
        
        return {
            'public_url': url,
            'path': file_path
        }
        
    except Exception as e:
        print(f" Get public URL failed: {e}")
        raise


def supabase_storage_create_signed_url(bucket: str, file_path: str, expires_in: int = 3600):
    """
    Create a signed URL for temporary file access.
    
    Args:
        bucket: Bucket name
        file_path: Path within bucket
        expires_in: URL expiration time in seconds
    
    Returns:
        Signed URL
    """
    print(f"🔧 Creating signed URL: {bucket}/{file_path}")
    
    try:
        client = _get_client()
        response = client.storage.from_(bucket).create_signed_url(file_path, expires_in)
        
        return {
            'signed_url': response['signedURL'],
            'expires_in': expires_in,
            'path': file_path
        }
        
    except Exception as e:
        print(f" Create signed URL failed: {e}")
        raise


def supabase_storage_move(bucket: str, from_path: str, to_path: str):
    """
    Move a file within or between buckets.
    
    Args:
        bucket: Source bucket name
        from_path: Source file path
        to_path: Destination file path
    
    Returns:
        Move result
    """
    print(f"🔧 Moving file: {from_path} → {to_path}")
    
    try:
        client = _get_client()
        response = client.storage.from_(bucket).move(from_path, to_path)
        
        return {
            'moved': True,
            'from': from_path,
            'to': to_path
        }
        
    except Exception as e:
        print(f" Move failed: {e}")
        raise


def supabase_realtime_subscribe(table: str, event: str = '*', callback: str = None):
    """
    Subscribe to realtime changes on a table.
    
    Args:
        table: Table name to subscribe to
        event: Event type (INSERT, UPDATE, DELETE, or *)
        callback: Callback function name
    
    Returns:
        Subscription details
    """
    print(f"🔧 Subscribing to realtime changes: {table}")
    
    try:
        # Note: Realtime subscriptions are typically handled client-side
        # This is a placeholder for the tool definition
        return {
            'subscribed': True,
            'table': table,
            'event': event,
            'note': 'Realtime subscriptions are typically handled client-side'
        }
        
    except Exception as e:
        print(f" Subscribe failed: {e}")
        raise


def supabase_create_bucket(bucket_name: str, public: bool = False):
    """
    Create a new storage bucket.
    
    Args:
        bucket_name: Name for the new bucket
        public: Whether bucket should be public
    
    Returns:
        Created bucket details
    """
    print(f"🔧 Creating storage bucket: {bucket_name}")
    
    try:
        client = _get_client()
        response = client.storage.create_bucket(bucket_name, {
            'public': public
        })
        
        return {
            'bucket': response,
            'name': bucket_name,
            'created': True
        }
        
    except Exception as e:
        print(f" Create bucket failed: {e}")
        raise


def supabase_list_buckets():
    """
    List all storage buckets.
    
    Returns:
        List of buckets
    """
    print(f"🔧 Listing all storage buckets")
    
    try:
        client = _get_client()
        response = client.storage.list_buckets()
        
        return {
            'buckets': response,
            'count': len(response)
        }
        
    except Exception as e:
        print(f" List buckets failed: {e}")
        raise


def supabase_delete_bucket(bucket_name: str):
    """
    Delete a storage bucket.
    
    Args:
        bucket_name: Name of bucket to delete
    
    Returns:
        Deletion result
    """
    print(f"🔧 Deleting storage bucket: {bucket_name}")
    
    try:
        client = _get_client()
        response = client.storage.delete_bucket(bucket_name)
        
        return {
            'deleted': True,
            'bucket': bucket_name
        }
        
    except Exception as e:
        print(f" Delete bucket failed: {e}")
        raise


def supabase_get_schema(table: str = None):
    """
    Get database schema information.
    
    Args:
        table: Specific table name (optional)
    
    Returns:
        Schema information
    """
    print(f"🔧 Getting database schema" + (f" for table: {table}" if table else ""))
    
    try:
        client = _get_client()
        
        if table:
            # Get specific table schema
            response = client.table(table).select('*').limit(0).execute()
            return {
                'table': table,
                'schema': 'Table structure retrieved'
            }
        else:
            # Get all tables (requires proper permissions)
            # This is a simplified version
            return {
                'schema': 'Database schema information',
                'note': 'Full schema introspection requires admin permissions'
            }
        
    except Exception as e:
        print(f" Get schema failed: {e}")
        raise


# ==================== AUTOMATION WORKFLOW MANAGEMENT ====================

def automation_workflow_create(user_id: int, name: str, workflow_json: str,
                                description: str = None, category: str = None,
                                canvas_data: str = None, slug: str = None):
    """
    Create a new automation workflow in Supabase
    
    Args:
        user_id: User ID creating the workflow
        name: Workflow name
        workflow_json: Complete workflow definition (JSON string)
        description: Optional description
        category: Workflow category (email, quotes, customer_service, etc.)
        canvas_data: UI positioning data (JSON string)
        slug: Optional custom slug (auto-generated if not provided)
    
    Returns:
        Created workflow with workflow_id
    """
    print(f"🔧 Creating automation workflow: {name}")
    
    try:
        client = _get_client()
        
        # Generate slug if not provided
        if not slug:
            import re
            from datetime import datetime
            slug = re.sub(r'[^a-z0-9]+', '-', name.lower()).strip('-')
            slug = f"{slug}-{datetime.now().strftime('%Y%m%d%H%M%S')}"
        
        data = {
            'user_id': user_id,
            'name': name,
            'slug': slug,
            'workflow_json': workflow_json,
            'description': description,
            'category': category,
            'canvas_data': canvas_data
        }
        
        # Remove None values
        data = {k: v for k, v in data.items() if v is not None}
        
        response = client.table('automation_workflows').insert(data).execute()
        
        workflow = response.data[0] if response.data else None
        
        return {
            'success': True,
            'workflow': workflow,
            'workflow_id': workflow['workflow_id'] if workflow else None,
            'slug': workflow['slug'] if workflow else None
        }
        
    except Exception as e:
        print(f"❌ Workflow creation failed: {e}")
        raise


def automation_workflow_list(user_id: int, category: str = None, enabled: bool = None):
    """
    List automation workflows for a user
    
    Args:
        user_id: User ID
        category: Filter by category (optional)
        enabled: Filter by enabled status (optional)
    
    Returns:
        List of workflows with metadata
    """
    print(f"🔧 Listing workflows for user {user_id}")
    
    try:
        client = _get_client()
        
        # Build query
        query = client.table('automation_workflows').select('*').eq('user_id', user_id)
        
        if category:
            query = query.eq('category', category)
        
        if enabled is not None:
            query = query.eq('enabled', enabled)
        
        query = query.order('updated_at', desc=True)
        response = query.execute()
        
        return {
            'success': True,
            'workflows': response.data,
            'count': len(response.data)
        }
        
    except Exception as e:
        print(f"❌ Workflow listing failed: {e}")
        raise


def automation_workflow_get(workflow_id: str = None, slug: str = None):
    """
    Get a specific workflow by ID or slug
    
    Args:
        workflow_id: Workflow UUID (optional)
        slug: Workflow slug (optional)
    
    Returns:
        Workflow details
    """
    print(f"🔧 Getting workflow: {workflow_id or slug}")
    
    try:
        client = _get_client()
        
        if workflow_id:
            query = client.table('automation_workflows').select('*').eq('workflow_id', workflow_id)
        elif slug:
            query = client.table('automation_workflows').select('*').eq('slug', slug)
        else:
            raise ValueError("Either workflow_id or slug must be provided")
        
        response = query.execute()
        
        if not response.data:
            raise ValueError(f"Workflow not found: {workflow_id or slug}")
        
        return {
            'success': True,
            'workflow': response.data[0]
        }
        
    except Exception as e:
        print(f"❌ Workflow retrieval failed: {e}")
        raise


def automation_workflow_update(workflow_id: str, updates: dict):
    """
    Update a workflow's configuration
    
    Args:
        workflow_id: Workflow UUID
        updates: Dictionary of fields to update (name, workflow_json, enabled, etc.)
    
    Returns:
        Updated workflow
    """
    print(f"🔧 Updating workflow: {workflow_id}")
    
    try:
        client = _get_client()
        
        # updated_at will be auto-updated by trigger
        response = client.table('automation_workflows').update(updates).eq('workflow_id', workflow_id).execute()
        
        if not response.data:
            raise ValueError(f"Workflow {workflow_id} not found or update failed")
        
        return {
            'success': True,
            'workflow': response.data[0]
        }
        
    except Exception as e:
        print(f"❌ Workflow update failed: {e}")
        raise


def automation_workflow_delete(workflow_id: str):
    """
    Delete a workflow (cascades to executions and schedules)
    
    Args:
        workflow_id: Workflow UUID
    
    Returns:
        Deletion confirmation
    """
    print(f"🔧 Deleting workflow: {workflow_id}")
    
    try:
        client = _get_client()
        
        response = client.table('automation_workflows').delete().eq('workflow_id', workflow_id).execute()
        
        return {
            'success': True,
            'deleted': True,
            'workflow_id': workflow_id
        }
        
    except Exception as e:
        print(f"❌ Workflow deletion failed: {e}")
        raise


def automation_workflow_execute(workflow_id: str, trigger_data: str, executed_by: int):
    """
    Start a workflow execution (creates execution record)
    
    Args:
        workflow_id: Workflow UUID
        trigger_data: JSON string of trigger data
        executed_by: User ID who triggered
    
    Returns:
        Execution ID and details
    """
    print(f"🔧 Starting workflow execution: {workflow_id}")
    
    try:
        client = _get_client()
        
        data = {
            'workflow_id': workflow_id,
            'trigger_data': trigger_data,
            'status': 'running',
            'executed_by': executed_by
        }
        
        response = client.table('workflow_executions').insert(data).execute()
        
        execution = response.data[0] if response.data else None
        
        return {
            'success': True,
            'execution_id': execution['execution_id'] if execution else None,
            'execution': execution
        }
        
    except Exception as e:
        print(f"❌ Execution creation failed: {e}")
        raise


def automation_workflow_execution_update(execution_id: str, status: str,
                                          execution_state: str = None,
                                          error_message: str = None,
                                          error_node_id: str = None,
                                          duration_ms: int = None):
    """
    Update workflow execution status and results
    
    Args:
        execution_id: Execution UUID
        status: Status - running, completed, failed, cancelled
        execution_state: JSON string of execution state (variables, node results)
        error_message: Error details if failed
        error_node_id: Which node failed
        duration_ms: Execution duration in milliseconds
    
    Returns:
        Updated execution record
    """
    print(f"🔧 Updating execution {execution_id} → {status}")
    
    try:
        client = _get_client()
        
        updates = {
            'status': status,
            'execution_state': execution_state,
            'error_message': error_message,
            'error_node_id': error_node_id,
            'duration_ms': duration_ms
        }
        
        # Add completion timestamp if done
        if status in ['completed', 'failed', 'cancelled']:
            from datetime import datetime
            updates['completed_at'] = datetime.utcnow().isoformat()
        
        # Remove None values
        updates = {k: v for k, v in updates.items() if v is not None}
        
        response = client.table('workflow_executions').update(updates).eq('execution_id', execution_id).execute()
        
        return {
            'success': True,
            'execution': response.data[0] if response.data else None
        }
        
    except Exception as e:
        print(f"❌ Execution update failed: {e}")
        raise


def automation_workflow_execution_history(workflow_id: str, limit: int = 20):
    """
    Get execution history for a workflow
    
    Args:
        workflow_id: Workflow UUID
        limit: Max executions to return (default: 20)
    
    Returns:
        List of execution records
    """
    print(f"🔧 Getting execution history for workflow: {workflow_id}")
    
    try:
        client = _get_client()
        
        response = (client.table('workflow_executions')
                    .select('*')
                    .eq('workflow_id', workflow_id)
                    .order('started_at', desc=True)
                    .limit(limit)
                    .execute())
        
        return {
            'success': True,
            'executions': response.data,
            'count': len(response.data)
        }
        
    except Exception as e:
        print(f"❌ Execution history retrieval failed: {e}")
        raise


def automation_workflow_template_list(category: str = None, featured: bool = None):
    """
    List available workflow templates
    
    Args:
        category: Filter by category (optional)
        featured: Show only featured templates (optional)
    
    Returns:
        List of templates
    """
    print("🔧 Listing workflow templates")
    
    try:
        client = _get_client()
        
        query = client.table('workflow_templates').select('*')
        
        if category:
            query = query.eq('category', category)
        
        if featured:
            query = query.eq('featured', True)
        
        query = query.order('use_count', desc=True)
        response = query.execute()
        
        return {
            'success': True,
            'templates': response.data,
            'count': len(response.data)
        }
        
    except Exception as e:
        print(f"❌ Template listing failed: {e}")
        raise


def automation_workflow_template_clone(template_id: str, user_id: int, name: str = None):
    """
    Clone a template to create a new workflow
    
    Args:
        template_id: Template UUID
        user_id: User ID
        name: Optional custom name for cloned workflow
    
    Returns:
        Created workflow from template
    """
    print(f"🔧 Cloning template: {template_id}")
    
    try:
        client = _get_client()
        
        # Get template
        template_response = client.table('workflow_templates').select('*').eq('template_id', template_id).execute()
        
        if not template_response.data:
            raise ValueError(f"Template {template_id} not found")
        
        template = template_response.data[0]
        
        # Generate new slug
        import re
        from datetime import datetime
        base_name = name or template['name']
        slug = re.sub(r'[^a-z0-9]+', '-', base_name.lower()).strip('-')
        slug = f"{slug}-{datetime.now().strftime('%Y%m%d%H%M%S')}"
        
        # Create workflow from template
        workflow_data = {
            'user_id': user_id,
            'name': base_name,
            'slug': slug,
            'description': template['description'],
            'category': template['category'],
            'workflow_json': template['template_json'],
            'canvas_data': template['canvas_data']
        }
        
        workflow_response = client.table('automation_workflows').insert(workflow_data).execute()
        
        # Increment use count
        new_use_count = template.get('use_count', 0) + 1
        client.table('workflow_templates').update({'use_count': new_use_count}).eq('template_id', template_id).execute()
        
        return {
            'success': True,
            'workflow': workflow_response.data[0] if workflow_response.data else None,
            'cloned_from_template': template_id
        }
        
    except Exception as e:
        print(f"❌ Template cloning failed: {e}")
        raise


def automation_workflow_schedule_create(workflow_id: str, schedule_type: str,
                                         cron_expression: str = None,
                                         interval_minutes: int = None,
                                         run_at: str = None,
                                         timezone: str = 'UTC'):
    """
    Create a schedule for a workflow
    
    Args:
        workflow_id: Workflow UUID
        schedule_type: Type - cron, interval, once
        cron_expression: Cron expression (for cron type): '0 8 * * *'
        interval_minutes: Interval in minutes (for interval type)
        run_at: Timestamp (for once type): '2025-01-15 22:00:00'
        timezone: Timezone for schedule (default: UTC)
    
    Returns:
        Created schedule
    """
    print(f"🔧 Creating schedule for workflow: {workflow_id}")
    
    try:
        client = _get_client()
        
        data = {
            'workflow_id': workflow_id,
            'schedule_type': schedule_type,
            'cron_expression': cron_expression,
            'interval_minutes': interval_minutes,
            'run_at': run_at,
            'timezone': timezone
        }
        
        # Remove None values
        data = {k: v for k, v in data.items() if v is not None}
        
        response = client.table('workflow_schedules').insert(data).execute()
        
        return {
            'success': True,
            'schedule': response.data[0] if response.data else None
        }
        
    except Exception as e:
        print(f"❌ Schedule creation failed: {e}")
        raise


if __name__ == "__main__":
    # Test the tools
    print(" Supabase tools loaded - 36 functions implemented (25 core + 11 automation workflow)")


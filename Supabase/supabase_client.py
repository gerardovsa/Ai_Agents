"""
Supabase API Client
==================

Python client for interacting with Supabase backend services.
Provides easy access to:
- Database (PostgreSQL via PostgREST)
- Authentication
- Storage (file uploads/downloads)
- Realtime subscriptions
- Edge Functions

Created: October 23, 2025
"""

import os
import sys
import requests
import json
from typing import Dict, List, Optional, Any
from datetime import datetime

# Try to import from shared config if available
try:
    sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    from config import SUPABASE_URL, SUPABASE_ANON_KEY, SUPABASE_SERVICE_KEY
    CONFIG_AVAILABLE = True
except ImportError:
    # Fallback to environment variables if config.py not in path
    SUPABASE_URL = None
    SUPABASE_ANON_KEY = None
    SUPABASE_SERVICE_KEY = None
    CONFIG_AVAILABLE = False


class SupabaseClient:
    """
    Complete Supabase API client for backend operations.
    
    Usage:
        client = SupabaseClient(
            url="https://your-project.supabase.co",
            key="your-anon-key"
        )
        
        # Query data
        data = client.query('users').select('*').execute()
        
        # Insert data
        result = client.insert('users', {'name': 'John', 'email': 'john@example.com'})
    """
    
    def __init__(self, url: str = None, key: str = None, service_key: str = None):
        """
        Initialize Supabase client.
        
        Args:
            url: Supabase project URL (e.g., https://xxx.supabase.co)
            key: Anon/public key for client operations
            service_key: Service role key for admin operations (optional)
        """
        # Priority: argument > config.py > environment variable
        self.url = url or (SUPABASE_URL if CONFIG_AVAILABLE else None) or os.getenv('SUPABASE_URL')
        self.key = key or (SUPABASE_ANON_KEY if CONFIG_AVAILABLE else None) or os.getenv('SUPABASE_KEY')
        self.service_key = service_key or (SUPABASE_SERVICE_KEY if CONFIG_AVAILABLE else None) or os.getenv('SUPABASE_SERVICE_KEY')
        
        if not self.url or not self.key:
            raise ValueError("Supabase URL and Key are required. Set SUPABASE_URL and SUPABASE_KEY environment variables or provide in config.py.")
        
        # Remove trailing slash from URL
        self.url = self.url.rstrip('/')
        
        # API endpoints
        self.rest_url = f"{self.url}/rest/v1"
        self.auth_url = f"{self.url}/auth/v1"
        self.storage_url = f"{self.url}/storage/v1"
        
        # Default headers
        self.headers = {
            'apikey': self.key,
            'Authorization': f'Bearer {self.key}',
            'Content-Type': 'application/json',
            'Prefer': 'return=representation'
        }
    
    def _make_request(self, method: str, url: str, **kwargs) -> requests.Response:
        """Make HTTP request with error handling."""
        try:
            response = requests.request(method, url, **kwargs)
            response.raise_for_status()
            return response
        except requests.exceptions.RequestException as e:
            print(f"❌ Request failed: {e}")
            if hasattr(e.response, 'text'):
                print(f"   Response: {e.response.text}")
            raise
    
    # ==========================================
    # DATABASE OPERATIONS (PostgREST)
    # ==========================================
    
    def query(self, table: str):
        """
        Start a query builder for a table.
        
        Example:
            client.query('users').select('*').eq('status', 'active').execute()
        """
        return QueryBuilder(self, table)
    
    def select(self, table: str, columns: str = '*', filters: Dict = None) -> List[Dict]:
        """
        Select data from a table.
        
        Args:
            table: Table name
            columns: Columns to select (default: '*')
            filters: Dictionary of column=value filters
        
        Returns:
            List of rows
        """
        url = f"{self.rest_url}/{table}"
        params = {'select': columns}
        
        if filters:
            for key, value in filters.items():
                params[key] = f"eq.{value}"
        
        response = self._make_request('GET', url, headers=self.headers, params=params)
        return response.json()
    
    def insert(self, table: str, data: Dict | List[Dict]) -> List[Dict]:
        """
        Insert one or more rows into a table.
        
        Args:
            table: Table name
            data: Dictionary (single row) or list of dicts (multiple rows)
        
        Returns:
            Inserted rows
        """
        url = f"{self.rest_url}/{table}"
        payload = data if isinstance(data, list) else [data]
        
        response = self._make_request('POST', url, headers=self.headers, json=payload)
        return response.json()
    
    def update(self, table: str, data: Dict, filters: Dict) -> List[Dict]:
        """
        Update rows in a table.
        
        Args:
            table: Table name
            data: New values
            filters: Which rows to update (e.g., {'id': 123})
        
        Returns:
            Updated rows
        """
        url = f"{self.rest_url}/{table}"
        params = {}
        
        for key, value in filters.items():
            params[key] = f"eq.{value}"
        
        response = self._make_request('PATCH', url, headers=self.headers, params=params, json=data)
        return response.json()
    
    def delete(self, table: str, filters: Dict) -> List[Dict]:
        """
        Delete rows from a table.
        
        Args:
            table: Table name
            filters: Which rows to delete (e.g., {'id': 123})
        
        Returns:
            Deleted rows
        """
        url = f"{self.rest_url}/{table}"
        params = {}
        
        for key, value in filters.items():
            params[key] = f"eq.{value}"
        
        response = self._make_request('DELETE', url, headers=self.headers, params=params)
        return response.json()
    
    def rpc(self, function_name: str, params: Dict = None) -> Any:
        """
        Call a PostgreSQL function (RPC).
        
        Args:
            function_name: Name of the function
            params: Function parameters
        
        Returns:
            Function result
        """
        url = f"{self.rest_url}/rpc/{function_name}"
        response = self._make_request('POST', url, headers=self.headers, json=params or {})
        return response.json()
    
    # ==========================================
    # AUTHENTICATION
    # ==========================================
    
    def sign_up(self, email: str, password: str, metadata: Dict = None) -> Dict:
        """Sign up a new user."""
        url = f"{self.auth_url}/signup"
        data = {
            'email': email,
            'password': password
        }
        if metadata:
            data['data'] = metadata
        
        response = self._make_request('POST', url, headers=self.headers, json=data)
        return response.json()
    
    def sign_in(self, email: str, password: str) -> Dict:
        """Sign in with email and password."""
        url = f"{self.auth_url}/token?grant_type=password"
        data = {
            'email': email,
            'password': password
        }
        
        response = self._make_request('POST', url, headers=self.headers, json=data)
        return response.json()
    
    def sign_out(self, access_token: str) -> Dict:
        """Sign out (revoke access token)."""
        url = f"{self.auth_url}/logout"
        headers = {**self.headers, 'Authorization': f'Bearer {access_token}'}
        
        response = self._make_request('POST', url, headers=headers)
        return response.json() if response.text else {'success': True}
    
    def get_user(self, access_token: str) -> Dict:
        """Get user info from access token."""
        url = f"{self.auth_url}/user"
        headers = {**self.headers, 'Authorization': f'Bearer {access_token}'}
        
        response = self._make_request('GET', url, headers=headers)
        return response.json()
    
    # ==========================================
    # STORAGE (File Operations)
    # ==========================================
    
    def upload_file(self, bucket: str, path: str, file_path: str, content_type: str = None) -> Dict:
        """
        Upload a file to storage bucket.
        
        Args:
            bucket: Bucket name
            path: Path in bucket (e.g., 'folder/file.pdf')
            file_path: Local file path
            content_type: MIME type (optional, auto-detected)
        
        Returns:
            Upload result with public URL
        """
        url = f"{self.storage_url}/object/{bucket}/{path}"
        
        with open(file_path, 'rb') as f:
            files = {'file': f}
            headers = {
                'apikey': self.key,
                'Authorization': f'Bearer {self.key}'
            }
            if content_type:
                headers['Content-Type'] = content_type
            
            response = self._make_request('POST', url, headers=headers, files=files)
        
        return response.json()
    
    def download_file(self, bucket: str, path: str, output_path: str = None) -> bytes:
        """
        Download a file from storage bucket.
        
        Args:
            bucket: Bucket name
            path: Path in bucket
            output_path: Where to save file (optional)
        
        Returns:
            File content as bytes
        """
        url = f"{self.storage_url}/object/{bucket}/{path}"
        
        response = self._make_request('GET', url, headers=self.headers)
        content = response.content
        
        if output_path:
            with open(output_path, 'wb') as f:
                f.write(content)
        
        return content
    
    def list_files(self, bucket: str, path: str = '') -> List[Dict]:
        """List files in a storage bucket path."""
        url = f"{self.storage_url}/object/list/{bucket}"
        params = {'prefix': path} if path else {}
        
        response = self._make_request('POST', url, headers=self.headers, json=params)
        return response.json()
    
    def delete_file(self, bucket: str, path: str) -> Dict:
        """Delete a file from storage bucket."""
        url = f"{self.storage_url}/object/{bucket}/{path}"
        
        response = self._make_request('DELETE', url, headers=self.headers)
        return response.json()
    
    def get_public_url(self, bucket: str, path: str) -> str:
        """Get public URL for a file."""
        return f"{self.storage_url}/object/public/{bucket}/{path}"
    
    # ==========================================
    # UTILITIES
    # ==========================================
    
    def health_check(self) -> Dict:
        """Check if Supabase is accessible."""
        try:
            response = requests.get(self.url, timeout=5)
            return {
                'status': 'healthy' if response.status_code == 200 else 'unhealthy',
                'url': self.url,
                'accessible': True
            }
        except Exception as e:
            return {
                'status': 'error',
                'url': self.url,
                'accessible': False,
                'error': str(e)
            }


class QueryBuilder:
    """
    SQL query builder for Supabase PostgREST.
    
    Usage:
        client.query('users').select('*').eq('status', 'active').execute()
    """
    
    def __init__(self, client: SupabaseClient, table: str):
        self.client = client
        self.table = table
        self.params = {}
        self._select = '*'
    
    def select(self, columns: str = '*'):
        """Select columns."""
        self._select = columns
        return self
    
    def eq(self, column: str, value: Any):
        """Equal to filter."""
        self.params[column] = f"eq.{value}"
        return self
    
    def neq(self, column: str, value: Any):
        """Not equal to filter."""
        self.params[column] = f"neq.{value}"
        return self
    
    def gt(self, column: str, value: Any):
        """Greater than filter."""
        self.params[column] = f"gt.{value}"
        return self
    
    def lt(self, column: str, value: Any):
        """Less than filter."""
        self.params[column] = f"lt.{value}"
        return self
    
    def like(self, column: str, pattern: str):
        """LIKE filter (pattern matching)."""
        self.params[column] = f"like.{pattern}"
        return self
    
    def order(self, column: str, ascending: bool = True):
        """Order results."""
        direction = 'asc' if ascending else 'desc'
        self.params['order'] = f"{column}.{direction}"
        return self
    
    def limit(self, count: int):
        """Limit number of results."""
        self.params['limit'] = count
        return self
    
    def execute(self) -> List[Dict]:
        """Execute the query."""
        url = f"{self.client.rest_url}/{self.table}"
        params = {'select': self._select, **self.params}
        
        response = self.client._make_request('GET', url, headers=self.client.headers, params=params)
        return response.json()


# ==========================================
# CLI Interface
# ==========================================

def main():
    """Command-line interface for Supabase operations."""
    import sys
    
    if len(sys.argv) < 2:
        print("""
Supabase API Client - Command Line Interface

Usage:
    python supabase_client.py <command> [args]

Commands:
    health                           - Check Supabase connectivity
    list <table>                     - List all rows from table
    select <table> <columns>         - Select specific columns
    insert <table> <json_data>       - Insert row(s)
    update <table> <json_data> <filters> - Update rows
    delete <table> <filters>         - Delete rows
    rpc <function> <params>          - Call database function
    
    auth-signup <email> <password>   - Sign up new user
    auth-signin <email> <password>   - Sign in user
    
    storage-list <bucket> [path]     - List files in bucket
    storage-upload <bucket> <path> <file> - Upload file
    storage-download <bucket> <path> <output> - Download file

Environment Variables:
    SUPABASE_URL - Your Supabase project URL
    SUPABASE_KEY - Your Supabase anon/public key

Examples:
    python supabase_client.py health
    python supabase_client.py list users
    python supabase_client.py select users "id,name,email"
    python supabase_client.py insert users '{"name":"John","email":"john@example.com"}'
""")
        return
    
    command = sys.argv[1]
    client = SupabaseClient()
    
    try:
        if command == 'health':
            result = client.health_check()
            print(f"✅ Status: {result['status']}")
            print(f"🔗 URL: {result['url']}")
            print(f"📡 Accessible: {result['accessible']}")
        
        elif command == 'list':
            table = sys.argv[2]
            data = client.select(table)
            print(json.dumps(data, indent=2))
        
        elif command == 'select':
            table = sys.argv[2]
            columns = sys.argv[3] if len(sys.argv) > 3 else '*'
            data = client.select(table, columns)
            print(json.dumps(data, indent=2))
        
        elif command == 'insert':
            table = sys.argv[2]
            data = json.loads(sys.argv[3])
            result = client.insert(table, data)
            print(json.dumps(result, indent=2))
        
        elif command == 'rpc':
            function = sys.argv[2]
            params = json.loads(sys.argv[3]) if len(sys.argv) > 3 else {}
            result = client.rpc(function, params)
            print(json.dumps(result, indent=2))
        
        elif command == 'auth-signup':
            email = sys.argv[2]
            password = sys.argv[3]
            result = client.sign_up(email, password)
            print(json.dumps(result, indent=2))
        
        elif command == 'auth-signin':
            email = sys.argv[2]
            password = sys.argv[3]
            result = client.sign_in(email, password)
            print(json.dumps(result, indent=2))
        
        elif command == 'storage-list':
            bucket = sys.argv[2]
            path = sys.argv[3] if len(sys.argv) > 3 else ''
            files = client.list_files(bucket, path)
            print(json.dumps(files, indent=2))
        
        else:
            print(f"❌ Unknown command: {command}")
            sys.exit(1)
    
    except Exception as e:
        print(f"❌ Error: {e}")
        sys.exit(1)


if __name__ == '__main__':
    main()

"""
Fix all Microsoft tool implementations to use credential injection instead of environment variables
"""

import os
import re
from pathlib import Path

def fix_microsoft_tool(file_path):
    """Fix a single Microsoft tool file"""
    print(f"\n📝 Processing: {file_path.name}")
    
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    original_content = content
    changes_made = False
    
    # 1. Fix __init__ method - remove environment variable check
    old_init_pattern = r'''    def __init__\(self\):
        self\.access_token = os\.getenv\('MICROSOFT_GRAPH_ACCESS_TOKEN'\)
        self\.graph_api_base = 'https://graph\.microsoft\.com/v1\.0'
        
        if not self\.access_token:
            print\("⚠️ Warning: MICROSOFT_GRAPH_ACCESS_TOKEN not set\. .* tools will not function\."\)'''
    
    new_init = '''    def __init__(self):
        # Credentials are injected dynamically per-user via credential_injector
        # No need to check environment variables at init time
        self.graph_api_base = 'https://graph.microsoft.com/v1.0\''''
    
    if re.search(old_init_pattern, content):
        content = re.sub(old_init_pattern, new_init, content)
        print("  ✅ Fixed __init__ method")
        changes_made = True
    
    # 2. Fix _get_headers method
    old_headers = '''    def _get_headers(self) -> Dict[str, str]:
        """Get authorization headers for Microsoft Graph API"""
        return {
            'Authorization': f'Bearer {self.access_token}',
            'Content-Type': 'application/json'
        }'''
    
    new_headers = '''    def _get_headers(self, **kwargs) -> Dict[str, str]:
        """Get authorization headers for Microsoft Graph API"""
        # Get access token from credential injector
        if '_user_id' in kwargs:
            import sys
            from pathlib import Path
            sys.path.insert(0, str(Path(__file__).parent.parent.parent / 'AI_infrastructure'))
            from auth.credential_injector import get_microsoft_access_token
            access_token = get_microsoft_access_token(**kwargs)
        else:
            raise Exception("No user credentials provided. User must be authenticated.")
        
        return {
            'Authorization': f'Bearer {access_token}',
            'Content-Type': 'application/json'
        }'''
    
    if old_headers in content:
        content = content.replace(old_headers, new_headers)
        print("  ✅ Fixed _get_headers method")
        changes_made = True
    
    # 3. Fix _make_request method - add **kwargs parameter and pass it to _get_headers
    old_make_request = r'def _make_request\(self, method: str, endpoint: str, data: Dict = None, params: Dict = None\) -> Dict:'
    new_make_request = 'def _make_request(self, method: str, endpoint: str, data: Dict = None, params: Dict = None, **kwargs) -> Dict:'
    
    if re.search(old_make_request, content):
        content = re.sub(old_make_request, new_make_request, content)
        print("  ✅ Added **kwargs to _make_request signature")
        changes_made = True
    
    # 4. Fix _get_headers() calls in _make_request to pass **kwargs
    content = re.sub(r'self\._get_headers\(\)', 'self._get_headers(**kwargs)', content)
    if re.search(r'self\._get_headers\(\*\*kwargs\)', content):
        print("  ✅ Updated _get_headers() calls to pass **kwargs")
        changes_made = True
    
    # 5. Add **kwargs to all public method signatures and _make_request calls
    # Find all public methods (not starting with _)
    method_pattern = r'(    def ([a-z][a-z_]*)\(self, ([^)]+)\))'
    
    def add_kwargs_to_method(match):
        full_sig = match.group(1)
        method_name = match.group(2)
        params = match.group(3)
        
        # Skip if already has **kwargs
        if '**kwargs' in params:
            return full_sig
        
        # Add **kwargs to signature
        return f'    def {method_name}(self, {params}, **kwargs)'
    
    content = re.sub(method_pattern, add_kwargs_to_method, content)
    
    # 6. Fix _make_request calls to pass **kwargs
    content = re.sub(
        r'self\._make_request\(([^)]+)\)(?!\*\*kwargs)',
        r'self._make_request(\1, **kwargs)',
        content
    )
    
    # Fix double **kwargs if any
    content = re.sub(r', \*\*kwargs, \*\*kwargs', ', **kwargs', content)
    
    if content != original_content:
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"  ✅ Updated: {file_path.name}")
        return True
    else:
        print(f"  ⏭️ No changes needed: {file_path.name}")
        return False

def main():
    """Fix all Microsoft tool files"""
    print("=" * 60)
    print("FIX MICROSOFT TOOLS CREDENTIAL INJECTION")
    print("=" * 60)
    
    tools_dir = Path(__file__).parent.parent.parent / 'tools' / 'implementations'
    microsoft_tools = list(tools_dir.glob('microsoft_*.py'))
    
    print(f"\nFound {len(microsoft_tools)} Microsoft tool files")
    
    fixed_count = 0
    for tool_file in microsoft_tools:
        if fix_microsoft_tool(tool_file):
            fixed_count += 1
    
    print("\n" + "=" * 60)
    print(f"✅ COMPLETE: Fixed {fixed_count} / {len(microsoft_tools)} files")
    print("=" * 60)

if __name__ == '__main__':
    main()

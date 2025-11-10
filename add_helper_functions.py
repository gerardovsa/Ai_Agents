"""Add build_forms_service_with_user_creds and build_drive_service_with_user_creds to google_auth_helper.py"""

# Read the file
with open('google_workspace/google_auth_helper.py', 'r', encoding='utf-8') as f:
    content = f.read()

# Check if functions already exist
if 'def build_forms_service_with_user_creds' in content:
    print("Functions already exist!")
else:
    # Find the end of the file (after clear_service_cache function)
    marker = "def clear_service_cache():"
    
    if marker not in content:
        print("ERROR: Can't find clear_service_cache function!")
    else:
        # Find where to insert (after clear_service_cache function)
        insert_pos = content.find(marker)
        # Find the end of that function
        lines = content[insert_pos:].split('\n')
        end_of_func = insert_pos
        for i, line in enumerate(lines):
            if i > 0 and line and not line[0].isspace():  # Found next non-indented line
                break
            end_of_func += len(line) + 1  # +1 for newline
        
        # New functions to add
        new_functions = '''

def build_forms_service_with_user_creds(user_id):
    """Build Google Forms service with user's OAuth credentials from database
    
    Args:
        user_id: User ID to load credentials for
    
    Returns:
        Authenticated Google Forms service
    """
    import sys
    from pathlib import Path
    from google.oauth2.credentials import Credentials
    
    # Import user auth manager
    sys.path.insert(0, str(Path(__file__).parent.parent / 'AI_infrastructure'))
    from auth.user_auth import UserAuthManager
    
    # Get user's Google OAuth credentials
    auth_manager = UserAuthManager()
    cred_dict = auth_manager.get_user_google_oauth_credentials(user_id)
    
    if not cred_dict:
        raise Exception(f"User {user_id} does not have Google OAuth credentials. Please sign in with Google at http://localhost:5001/api/auth/google/login?user_id={user_id}")
    
    # Build credentials object
    credentials = Credentials(
        token=cred_dict['access_token'],
        refresh_token=cred_dict.get('refresh_token'),
        token_uri=cred_dict['token_uri'],
        client_id=cred_dict['client_id'],
        client_secret=cred_dict['client_secret'],
        scopes=cred_dict['scopes']
    )
    
    # Build and return service
    service = build('forms', 'v1', credentials=credentials)
    print(f"Google Forms service created with user {user_id}'s OAuth credentials")
    return service


def build_drive_service_with_user_creds(user_id):
    """Build Google Drive service with user's OAuth credentials from database
    
    Args:
        user_id: User ID to load credentials for
    
    Returns:
        Authenticated Google Drive service
    """
    import sys
    from pathlib import Path
    from google.oauth2.credentials import Credentials
    
    # Import user auth manager
    sys.path.insert(0, str(Path(__file__).parent.parent / 'AI_infrastructure'))
    from auth.user_auth import UserAuthManager
    
    # Get user's Google OAuth credentials
    auth_manager = UserAuthManager()
    cred_dict = auth_manager.get_user_google_oauth_credentials(user_id)
    
    if not cred_dict:
        raise Exception(f"User {user_id} does not have Google OAuth credentials")
    
    # Build credentials object
    credentials = Credentials(
        token=cred_dict['access_token'],
        refresh_token=cred_dict.get('refresh_token'),
        token_uri=cred_dict['token_uri'],
        client_id=cred_dict['client_id'],
        client_secret=cred_dict['client_secret'],
        scopes=cred_dict['scopes']
    )
    
    # Build and return service
    service = build('drive', 'v3', credentials=credentials)
    return service
'''
        
        # Insert the new functions at the end
        content = content[:end_of_func] + new_functions
        
        # Write back
        with open('google_workspace/google_auth_helper.py', 'w', encoding='utf-8') as f:
            f.write(content)
        
        print("✅ Functions added successfully!")
        
        # Verify
        with open('google_workspace/google_auth_helper.py', 'r', encoding='utf-8') as f:
            verify_content = f.read()
        
        if 'def build_forms_service_with_user_creds' in verify_content:
            print("✅ VERIFIED: build_forms_service_with_user_creds added")
        if 'def build_drive_service_with_user_creds' in verify_content:
            print("✅ VERIFIED: build_drive_service_with_user_creds added")
        
        print("\n🎉 All helper functions added!")

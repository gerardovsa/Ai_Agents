"""
Email Alias Helper Functions
Purpose: Centralized functions for managing user email aliases

These functions enable the Account Aliases strategy where users can:
- Have one primary email (in users.email)
- Link multiple additional emails (in user_email_aliases)
- Login with ANY linked email → access same account
"""

import sqlite3
from datetime import datetime
from typing import Optional, Dict, List, Tuple
import json
from pathlib import Path
import sys

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

# Use centralized database connection utility (SQLite + Supabase support)
from shared.database_utils import get_database_connection, convert_sql_placeholders


def get_user_id_by_email(email: str) -> Optional[int]:
    """
    Get user_id for an email address (checks both primary and aliases)
    
    Args:
        email: Email address to lookup
        
    Returns:
        user_id if found, None otherwise
        
    Example:
        user_id = get_user_id_by_email('john@gmail.com')
        if user_id:
            print(f"Found user: {user_id}")
    """
    conn = get_database_connection('ai_infrastructure')
    cursor = conn.cursor()
    
    try:
        # First check: Is this the primary email?
        sql, params = convert_sql_placeholders('SELECT id FROM users WHERE email = ?', (email,))
        cursor.execute(sql, params)
        result = cursor.fetchone()
        
        if result:
            # Handle both SQLite (tuple/Row) and PostgreSQL (dict)
            return result['id'] if isinstance(result, dict) else result[0]
        
        # Second check: Is this an alias email?
        sql, params = convert_sql_placeholders('''
            SELECT user_id FROM user_email_aliases 
            WHERE alias_email = ?
        ''', (email,))
        cursor.execute(sql, params)
        result = cursor.fetchone()
        
        if result:
            # Handle both SQLite (tuple/Row) and PostgreSQL (dict)
            return result['user_id'] if isinstance(result, dict) else result[0]
        
        # Not found
        return None
        
    except sqlite3.Error as e:
        print(f" Database error in get_user_id_by_email: {e}")
        return None
        
    finally:
        conn.close()


def add_email_alias(
    user_id: int, 
    alias_email: str, 
    oauth_provider: str,
    metadata: Optional[Dict] = None
) -> Tuple[bool, str]:
    """
    Link a new email address to an existing user account
    
    Args:
        user_id: ID of the user to link email to
        alias_email: Email address to link
        oauth_provider: OAuth provider ('google' or 'microsoft365')
        metadata: Optional dict with additional info
        
    Returns:
        Tuple of (success: bool, message: str)
        
    Example:
        success, msg = add_email_alias(123, 'john@company.com', 'microsoft365')
        if success:
            print("Email linked successfully!")
    """
    conn = get_database_connection('ai_infrastructure')
    cursor = conn.cursor()
    
    try:
        # Verify user exists
        sql, params = convert_sql_placeholders('SELECT id FROM users WHERE id = ?', (user_id,))
        cursor.execute(sql, params)
        if not cursor.fetchone():
            return False, f"User {user_id} not found"
        
        # Check if email is already someone's primary
        sql, params = convert_sql_placeholders('SELECT id FROM users WHERE email = ?', (alias_email,))
        cursor.execute(sql, params)
        if cursor.fetchone():
            return False, f"Email {alias_email} is already a primary email for another account"
        
        # Check if email is already an alias
        sql, params = convert_sql_placeholders('''
            SELECT user_id FROM user_email_aliases 
            WHERE alias_email = ?
        ''', (alias_email,))
        cursor.execute(sql, params)
        existing = cursor.fetchone()
        
        if existing:
            if existing[0] == user_id:
                return False, f"Email {alias_email} is already linked to this account"
            else:
                return False, f"Email {alias_email} is already linked to another account"
        
        # Add the alias
        metadata_json = json.dumps(metadata) if metadata else None
        sql, params = convert_sql_placeholders('''
            INSERT INTO user_email_aliases 
            (user_id, alias_email, oauth_provider, created_at, updated_at, metadata)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (
            user_id, 
            alias_email, 
            oauth_provider,
            datetime.now(),
            datetime.now(),
            metadata_json
        ))
        cursor.execute(sql, params)
        
        conn.commit()
        return True, f"Successfully linked {alias_email} to user {user_id}"
        
    except sqlite3.Error as e:
        conn.rollback()
        return False, f"Database error: {e}"
        
    finally:
        conn.close()


def get_user_emails(user_id: int) -> Dict[str, List[str]]:
    """
    Get all email addresses associated with a user
    
    Args:
        user_id: User ID to lookup
        
    Returns:
        Dict with 'primary' and 'aliases' keys containing email lists
        
    Example:
        emails = get_user_emails(123)
        print(f"Primary: {emails['primary']}")
        print(f"Aliases: {emails['aliases']}")
    """
    conn = get_database_connection('ai_infrastructure')
    cursor = conn.cursor()
    
    try:
        # Get primary email
        sql, params = convert_sql_placeholders('SELECT email FROM users WHERE id = ?', (user_id,))
        cursor.execute(sql, params)
        result = cursor.fetchone()
        
        if not result:
            return {'primary': None, 'aliases': []}
        
        primary_email = result[0]
        
        # Get alias emails
        sql, params = convert_sql_placeholders('''
            SELECT alias_email, oauth_provider, created_at 
            FROM user_email_aliases 
            WHERE user_id = ?
            ORDER BY created_at DESC
        ''', (user_id,))
        cursor.execute(sql, params)
        
        aliases = [
            {
                'email': row[0],
                'provider': row[1],
                'linked_at': row[2]
            }
            for row in cursor.fetchall()
        ]
        
        return {
            'primary': primary_email,
            'aliases': aliases
        }
        
    except sqlite3.Error as e:
        print(f" Database error in get_user_emails: {e}")
        return {'primary': None, 'aliases': []}
        
    finally:
        conn.close()


def remove_email_alias(alias_email: str, user_id: int) -> Tuple[bool, str]:
    """
    Unlink an email alias from a user account
    
    Args:
        alias_email: Email address to unlink
        user_id: User ID (for security verification)
        
    Returns:
        Tuple of (success: bool, message: str)
        
    Example:
        success, msg = remove_email_alias('john@company.com', 123)
    """
    conn = get_database_connection('ai_infrastructure')
    cursor = conn.cursor()
    
    try:
        # Verify this alias belongs to this user
        cursor.execute('''
            SELECT id FROM user_email_aliases 
            WHERE alias_email = ? AND user_id = ?
        ''', (alias_email, user_id))
        
        if not cursor.fetchone():
            return False, "Email alias not found or doesn't belong to this user"
        
        # Remove the alias
        cursor.execute('''
            DELETE FROM user_email_aliases 
            WHERE alias_email = ? AND user_id = ?
        ''', (alias_email, user_id))
        
        conn.commit()
        return True, f"Successfully unlinked {alias_email}"
        
    except sqlite3.Error as e:
        conn.rollback()
        return False, f"Database error: {e}"
        
    finally:
        conn.close()


def is_email_available(email: str) -> bool:
    """
    Check if an email is available (not used as primary or alias)
    
    Args:
        email: Email address to check
        
    Returns:
        True if available, False if already in use
    """
    user_id = get_user_id_by_email(email)
    return user_id is None


def get_alias_info(alias_email: str) -> Optional[Dict]:
    """
    Get detailed information about an email alias
    
    Args:
        alias_email: Email address to lookup
        
    Returns:
        Dict with alias details or None if not found
    """
    conn = get_database_connection('ai_infrastructure')
    cursor = conn.cursor()
    
    try:
        cursor.execute('''
            SELECT 
                id, user_id, alias_email, oauth_provider, 
                is_primary, created_at, updated_at, metadata
            FROM user_email_aliases 
            WHERE alias_email = ?
        ''', (alias_email,))
        
        result = cursor.fetchone()
        
        if not result:
            return None
        
        return {
            'id': result[0],
            'user_id': result[1],
            'email': result[2],
            'provider': result[3],
            'is_primary': bool(result[4]),
            'created_at': result[5],
            'updated_at': result[6],
            'metadata': json.loads(result[7]) if result[7] else None
        }
        
    except sqlite3.Error as e:
        print(f" Database error in get_alias_info: {e}")
        return None
        
    finally:
        conn.close()


def count_user_aliases(user_id: int) -> int:
    """
    Count how many email aliases a user has
    
    Args:
        user_id: User ID
        
    Returns:
        Number of aliases (not including primary email)
    """
    conn = get_database_connection('ai_infrastructure')
    cursor = conn.cursor()
    
    try:
        cursor.execute('''
            SELECT COUNT(*) FROM user_email_aliases 
            WHERE user_id = ?
        ''', (user_id,))
        
        result = cursor.fetchone()
        return result[0] if result else 0
        
    except sqlite3.Error as e:
        print(f" Database error in count_user_aliases: {e}")
        return 0
        
    finally:
        conn.close()


# Test functions (for development)
if __name__ == '__main__':
    print("🧪 Testing Email Alias Helper Functions\n")
    
    # Test 1: Lookup non-existent email
    print("Test 1: Lookup non-existent email")
    user_id = get_user_id_by_email('nonexistent@example.com')
    print(f"Result: {user_id} (should be None)")
    print()
    
    # Test 2: Check if email is available
    print("Test 2: Check email availability")
    available = is_email_available('test@example.com')
    print(f"test@example.com available: {available}")
    print()
    
    print(" Basic tests completed!")

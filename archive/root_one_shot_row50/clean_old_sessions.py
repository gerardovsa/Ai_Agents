"""
Database Cleanup Script - Remove Old/Malformed Sessions
===========================================================

This script removes old and malformed sessions from the ai_infrastructure.user_sessions table.

Options:
1. Delete only old/malformed sessions (sessions without device_info or older than 7 days)
2. TRUNCATE all sessions (complete reset - use with caution!)

Author: AI Agent Platform
Date: December 2024
"""

import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from shared.database_utils import get_database_connection


def clean_old_sessions():
    """Delete only old/malformed sessions"""
    try:
        conn = get_database_connection('ai_infrastructure')
        cursor = conn.cursor()
        
        # Delete sessions without device_info or older than 7 days
        delete_query = """
            DELETE FROM ai_infrastructure.user_sessions
            WHERE 
                device_info IS NULL 
                OR device_info = '{}'::jsonb
                OR device_info = ''::jsonb
                OR created_at < NOW() - INTERVAL '7 days'
        """
        
        cursor.execute(delete_query)
        deleted_count = cursor.rowcount
        
        conn.commit()
        cursor.close()
        conn.close()
        
        print(f"Deleted {deleted_count} old/malformed sessions")
        print("\nCriteria:")
        print("  - Sessions with NULL device_info")
        print("  - Sessions with empty device_info ({})")
        print("  - Sessions older than 7 days")
        
        return deleted_count
        
    except Exception as e:
        print(f"Error cleaning sessions: {e}")
        return 0


def truncate_all_sessions():
    """TRUNCATE all sessions (complete reset)"""
    try:
        conn = get_database_connection('ai_infrastructure')
        cursor = conn.cursor()
        
        # Count existing sessions first
        cursor.execute("SELECT COUNT(*) FROM ai_infrastructure.user_sessions")
        total_count = cursor.fetchone()[0]
        
        # Truncate table
        cursor.execute("TRUNCATE TABLE ai_infrastructure.user_sessions RESTART IDENTITY CASCADE")
        
        conn.commit()
        cursor.close()
        conn.close()
        
        print(f"Deleted ALL {total_count} sessions from database")
        print("Table has been completely reset")
        
        return total_count
        
    except Exception as e:
        print(f"Error truncating sessions: {e}")
        return 0


def show_current_stats():
    """Show current session statistics"""
    try:
        conn = get_database_connection('ai_infrastructure')
        cursor = conn.cursor()
        
        # Total sessions
        cursor.execute("SELECT COUNT(*) FROM ai_infrastructure.user_sessions")
        total = cursor.fetchone()[0]
        
        # Sessions with NULL device_info
        cursor.execute("""
            SELECT COUNT(*) FROM ai_infrastructure.user_sessions 
            WHERE device_info IS NULL OR device_info = '{}'::jsonb
        """)
        null_device = cursor.fetchone()[0]
        
        # Sessions older than 7 days
        cursor.execute("""
            SELECT COUNT(*) FROM ai_infrastructure.user_sessions 
            WHERE created_at < NOW() - INTERVAL '7 days'
        """)
        old_sessions = cursor.fetchone()[0]
        
        # Active sessions (last 24 hours)
        cursor.execute("""
            SELECT COUNT(*) FROM ai_infrastructure.user_sessions 
            WHERE created_at > NOW() - INTERVAL '24 hours'
        """)
        active_24h = cursor.fetchone()[0]
        
        cursor.close()
        conn.close()
        
        print("\n=== CURRENT SESSION STATISTICS ===")
        print(f"Total sessions: {total}")
        print(f"Sessions without device_info: {null_device}")
        print(f"Sessions older than 7 days: {old_sessions}")
        print(f"Active sessions (last 24h): {active_24h}")
        print(f"\nSessions to be deleted (Option 1): {null_device + old_sessions}")
        print("==================================\n")
        
    except Exception as e:
        print(f"Error getting statistics: {e}")


def main():
    """Main function - interactive cleanup"""
    print("\n" + "="*60)
    print("  DATABASE CLEANUP - Active Sessions")
    print("="*60 + "\n")
    
    # Show current statistics
    show_current_stats()
    
    print("Choose an option:")
    print("  [1] Delete old/malformed sessions only (RECOMMENDED)")
    print("  [2] TRUNCATE all sessions (complete reset)")
    print("  [3] Show statistics only (no changes)")
    print("  [Q] Quit\n")
    
    choice = input("Enter choice [1/2/3/Q]: ").strip().upper()
    
    if choice == '1':
        print("\nDeleting old/malformed sessions...")
        confirm = input("Are you sure? This cannot be undone. [y/N]: ").strip().lower()
        
        if confirm == 'y':
            deleted = clean_old_sessions()
            print(f"\n SUCCESS: Cleaned up {deleted} sessions")
        else:
            print("\nCancelled - no changes made")
            
    elif choice == '2':
        print("\n WARNING: This will delete ALL sessions!")
        print("All users will need to log in again.\n")
        confirm = input("Are you ABSOLUTELY sure? Type 'DELETE ALL' to confirm: ").strip()
        
        if confirm == 'DELETE ALL':
            deleted = truncate_all_sessions()
            print(f"\n SUCCESS: Deleted ALL {deleted} sessions")
        else:
            print("\nCancelled - no changes made")
            
    elif choice == '3':
        print("\nNo changes made - statistics only\n")
        
    elif choice == 'Q':
        print("\nExiting without changes\n")
        
    else:
        print("\nInvalid choice - exiting\n")


if __name__ == '__main__':
    main()

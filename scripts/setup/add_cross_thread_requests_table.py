"""
Database Migration: Add cross_thread_requests Table
from shared.database_utils import convert_sql_placeholders

Creates the cross_thread_requests table for tracking cross-thread communication
between agents. Enables AI to request updates from other threads and track responses.

Table Schema:
- request_id: Unique identifier for the request
- source_thread_id: Thread that initiated the request
- target_thread_id: Thread receiving the request
- request_message: The actual request content
- request_type: Type of request (status_update, deliverable, etc.)
- priority: Priority level (low, medium, high, urgent)
- status: Current status (pending, completed, cancelled)
- response_message: Response from target thread
- created_at, responded_at: Timestamps
- user_id: Owner of the request

Run this script once to add the table to sessions.db
"""

import sqlite3
from pathlib import Path


def get_db_path():
    """Get path to sessions.db"""
    root_dir = Path(__file__).parent.parent.parent
    return root_dir / 'data' / 'sessions.db'


def add_cross_thread_requests_table():
    """Add cross_thread_requests table to sessions.db"""
    db_path = get_db_path()
    
    print(f"Database path: {db_path}")
    print(f"Database exists: {db_path.exists()}")
    
    if not db_path.exists():
        print("ERROR: sessions.db not found!")
        print(f"Expected location: {db_path}")
        return False
    
    conn = sqlite3.connect(str(db_path))
    cursor = conn.cursor()
    
    try:
        # Check if table already exists
        sql, params = convert_sql_placeholders("""
            SELECT name FROM sqlite_master 
            WHERE type='table' AND name='cross_thread_requests'
        """)
        
        if cursor.fetchone():
            print("Table 'cross_thread_requests' already exists!")
            
            # Show current structure
            cursor.execute("PRAGMA table_info(cross_thread_requests)")
            columns = cursor.fetchall()
            print("\nCurrent table structure:")
            for col in columns:
                print(f"  - {col[1]} ({col[2]})")
            
            return True
        
        # Create the table
        print("\nCreating cross_thread_requests table...")
        
        cursor.execute("""
            CREATE TABLE cross_thread_requests (
                request_id TEXT PRIMARY KEY,
                source_thread_id TEXT NOT NULL,
                target_thread_id TEXT NOT NULL,
                request_message TEXT NOT NULL,
                request_type TEXT DEFAULT 'status_update',
                priority TEXT DEFAULT 'medium',
                status TEXT DEFAULT 'pending',
                response_message TEXT,
                created_at TEXT NOT NULL,
                responded_at TEXT,
                user_id INTEGER NOT NULL,
                FOREIGN KEY (source_thread_id) REFERENCES threads(thread_id),
                FOREIGN KEY (target_thread_id) REFERENCES threads(thread_id),
                FOREIGN KEY (user_id) REFERENCES users(user_id)
            )
        """)
        
        print("Table created successfully!")
        
        # Create indexes for performance
        print("\nCreating indexes...")
        
        cursor.execute("""
            CREATE INDEX idx_cross_thread_target 
            ON cross_thread_requests(target_thread_id, status)
        """)
        print("  - Created index on target_thread_id, status")
        
        cursor.execute("""
            CREATE INDEX idx_cross_thread_source 
            ON cross_thread_requests(source_thread_id, created_at)
        """)
        print("  - Created index on source_thread_id, created_at")
        
        cursor.execute("""
            CREATE INDEX idx_cross_thread_status 
            ON cross_thread_requests(status, created_at)
        """)
        print("  - Created index on status, created_at")
        
        conn.commit()
        
        print("\nMigration completed successfully!")
        print("\nTable structure:")
        cursor.execute("PRAGMA table_info(cross_thread_requests)")
        columns = cursor.fetchall()
        for col in columns:
            print(f"  - {col[1]} ({col[2]})")
        
        return True
        
    except Exception as e:
        conn.rollback()
        print(f"\nERROR: Migration failed!")
        print(f"Error: {str(e)}")
        return False
        
    finally:
        conn.close()


def verify_migration():
    """Verify the migration was successful"""
    db_path = get_db_path()
    conn = sqlite3.connect(str(db_path))
    cursor = conn.cursor()
    
    try:
        # Test insert
        print("\nVerifying migration with test insert...")
        
        test_request_id = "test_request_123"
        cursor.execute("""
            INSERT INTO cross_thread_requests (
                request_id, source_thread_id, target_thread_id,
                request_message, request_type, priority, status,
                created_at, user_id
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            test_request_id, "test_source", "test_target",
            "Test request message", "status_update", "medium", "pending",
            "2025-11-16T12:00:00", 1
        ))

        cursor.execute(sql, params)
        
        # Test select
        sql, params = convert_sql_placeholders("""
            SELECT * FROM cross_thread_requests WHERE request_id = ?
        """, (test_request_id,))

        cursor.execute(sql, params)
        
        row = cursor.fetchone()
        if row:
            print("Test insert successful!")
            
            # Clean up test data
            sql, params = convert_sql_placeholders("DELETE FROM cross_thread_requests WHERE request_id = ?", (test_request_id,))

            cursor.execute(sql, params)
            conn.commit()
            print("Test data cleaned up.")
            print("\nMigration verification PASSED!")
            return True
        else:
            print("ERROR: Test insert failed - row not found")
            return False
            
    except Exception as e:
        print(f"ERROR: Verification failed - {str(e)}")
        return False
        
    finally:
        conn.close()


if __name__ == '__main__':
    print("=" * 60)
    print("Cross-Thread Requests Table Migration")
    print("=" * 60)
    
    success = add_cross_thread_requests_table()
    
    if success:
        print("\n" + "=" * 60)
        verify_migration()
    
    print("\n" + "=" * 60)
    print("Migration script completed.")
    print("=" * 60)

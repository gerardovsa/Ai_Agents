"""
Migrate user_preferences table to add missing columns for geolocation and AI memories

This script adds the following columns:
- nickname
- detected_country
- detected_city
- detected_timezone
- detected_ip_address
- manual_location_override
- manual_timezone_override
- use_manual_location
- use_manual_timezone
- last_location_check
- ai_memories
- memory_updated_at
"""

import sqlite3
from pathlib import Path

def migrate_user_preferences():
    """Add missing columns to user_preferences table"""
    root_dir = Path(__file__).parent
    db_path = root_dir / 'data' / 'ai_infrastructure.db'
    
    print(f"Migrating database: {db_path}")
    
    conn = sqlite3.connect(str(db_path))
    cursor = conn.cursor()
    
    # Get existing columns
    cursor.execute("PRAGMA table_info(user_preferences)")
    existing_columns = [row[1] for row in cursor.fetchall()]
    print(f"\nExisting columns: {existing_columns}")
    
    # Define new columns to add
    new_columns = [
        ("nickname", "TEXT"),
        ("detected_country", "TEXT"),
        ("detected_city", "TEXT"),
        ("detected_timezone", "TEXT"),
        ("detected_ip_address", "TEXT"),
        ("manual_location_override", "TEXT"),
        ("manual_timezone_override", "TEXT"),
        ("use_manual_location", "INTEGER DEFAULT 0"),
        ("use_manual_timezone", "INTEGER DEFAULT 0"),
        ("last_location_check", "TIMESTAMP"),
        ("ai_memories", "TEXT"),
        ("memory_updated_at", "TIMESTAMP")
    ]
    
    # Add missing columns
    added_columns = []
    for column_name, column_type in new_columns:
        if column_name not in existing_columns:
            try:
                cursor.execute(f"ALTER TABLE user_preferences ADD COLUMN {column_name} {column_type}")
                added_columns.append(column_name)
                print(f"  Added column: {column_name} ({column_type})")
            except sqlite3.OperationalError as e:
                print(f"  Error adding {column_name}: {e}")
    
    conn.commit()
    
    # Verify all columns now exist
    cursor.execute("PRAGMA table_info(user_preferences)")
    final_columns = [row[1] for row in cursor.fetchall()]
    
    print(f"\nFinal columns ({len(final_columns)}): {final_columns}")
    print(f"\nAdded {len(added_columns)} columns: {added_columns}")
    
    conn.close()
    print("\nMigration complete!")

if __name__ == "__main__":
    migrate_user_preferences()

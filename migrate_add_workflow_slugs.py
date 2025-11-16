"""
Add workflow and internal document slug columns to threads table

Migration: add_workflow_slugs_to_threads
Created: November 16, 2025
"""
import sqlite3
from pathlib import Path

def migrate():
    """Add workflow_slug, workflow_title, internal_doc_slug, internal_doc_title to threads"""
    db_path = Path(__file__).parent / 'data' / 'sessions.db'
    conn = sqlite3.connect(str(db_path))
    cursor = conn.cursor()
    
    print("[MIGRATION] Adding workflow and document slug columns to threads table...")
    
    try:
        # Add workflow_slug column
        cursor.execute("ALTER TABLE threads ADD COLUMN workflow_slug TEXT")
        print("✅ Added workflow_slug column")
    except sqlite3.OperationalError as e:
        if "duplicate column name" in str(e):
            print("⚠️  workflow_slug column already exists")
        else:
            raise
    
    try:
        # Add workflow_title column
        cursor.execute("ALTER TABLE threads ADD COLUMN workflow_title TEXT")
        print("✅ Added workflow_title column")
    except sqlite3.OperationalError as e:
        if "duplicate column name" in str(e):
            print("⚠️  workflow_title column already exists")
        else:
            raise
    
    try:
        # Add internal_doc_slug column
        cursor.execute("ALTER TABLE threads ADD COLUMN internal_doc_slug TEXT")
        print("✅ Added internal_doc_slug column")
    except sqlite3.OperationalError as e:
        if "duplicate column name" in str(e):
            print("⚠️  internal_doc_slug column already exists")
        else:
            raise
    
    try:
        # Add internal_doc_title column
        cursor.execute("ALTER TABLE threads ADD COLUMN internal_doc_title TEXT")
        print("✅ Added internal_doc_title column")
    except sqlite3.OperationalError as e:
        if "duplicate column name" in str(e):
            print("⚠️  internal_doc_title column already exists")
        else:
            raise
    
    # Create indexes for better query performance
    try:
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_threads_workflow_slug ON threads(workflow_slug)")
        print("✅ Created index on workflow_slug")
    except Exception as e:
        print(f"⚠️  Error creating workflow_slug index: {e}")
    
    try:
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_threads_internal_doc_slug ON threads(internal_doc_slug)")
        print("✅ Created index on internal_doc_slug")
    except Exception as e:
        print(f"⚠️  Error creating internal_doc_slug index: {e}")
    
    conn.commit()
    conn.close()
    
    print("\n✅ [MIGRATION] Migration completed successfully!")
    print("\nNew columns added:")
    print("  - workflow_slug (TEXT): Slug of linked automation workflow")
    print("  - workflow_title (TEXT): Title of linked automation workflow")
    print("  - internal_doc_slug (TEXT): Slug of linked internal document")
    print("  - internal_doc_title (TEXT): Title of linked internal document")

if __name__ == "__main__":
    migrate()
